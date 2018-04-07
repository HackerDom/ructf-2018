import time
import json
import re
import hashlib
import sys
import os
import signal
import fcntl

DB_PATH="/cloud/backend/db"
SCRIPTS_PATH="/cloud/backend"

RESP_HEADERS = [
    ("Content-Type", "application/json"), 
    ("Cache-Control", "no-cache, no-store, max-age=0, must-revalidate"),
    ("Expires", "0"),
    ("Pragma", "no-cache"),
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Access-Control-Max-Age", "300"),
    ("Access-Control-Allow-Headers", "content-type, accept, x-authorization"),
    ("Access-Control-Allow-Methods", "POST")
]

RATE_LIMITS = {
    "create_vm": 20,
    "take_snapshot": 30,
    "open_network": 10,
    "isolate_network": 10,
    "list_snapshots": 10,
    "restore_vm_from_snapshot": 30,
    "remove_snapshot": 10,
    "reboot_vm": 10
}


def authenticate_request_by_token(token):
    "Returns team number or None"

    m = re.fullmatch(r"([0-9]+)_[0-9a-f]{32}", token)
    if not m:
        return None

    team_num = int(m.group(1))

    right_token_hash = open("%s/team%d/token_hash.txt" % (DB_PATH, team_num)).read().strip()
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    if right_token_hash == token_hash:
        return team_num
    return None

def parse_task_file(team, task_name):
    "returns start_time, end_time and data"
    
    if not re.fullmatch(r"[a-z_]+", task_name):
        return None

    try:
        data = open("%s/team%d/task_%s.out" % (DB_PATH, team, task_name)).read().strip()
    except OSError:
        return None

    start_time = 0
    end_time = 0

    exit_code = None

    lines = data.split("\n")
    m = re.fullmatch(r"started: ([0-9]+)", lines[0])
    if m:
        start_time = int(m.group(1))
        lines = lines[1:]
    
    if len(lines) > 0:
        m = re.fullmatch(r"finished: ([0-9]+)", lines[-1])
        if m:
            end_time = int(m.group(1))
            lines = lines[:-1]

    if len(lines) > 0:
        m = re.fullmatch(r"exit_code: ([0-9]+)", lines[-1])
        if m:
            exit_code = int(m.group(1))
            lines = lines[:-1]

    progress = None
    status_lines = []
    for line in lines:
        m = re.fullmatch(r"msg: (.+)", line)
        if m:
            status_lines.append(m.group(1))
        m = re.fullmatch(r"progress: ([0-9]+)%?", line)
        if m:
            progress = int(m.group(1))

    msg = "\n".join(status_lines)
    if not msg:
        if exit_code == 0:
            msg = "OK"
        elif exit_code is not None:
            msg = "ERR"
    return start_time, end_time, msg, progress, exit_code


def get_rate_limit_remaining(team, task_name):
    if task_name not in RATE_LIMITS:
        return 0
    rate_limit = RATE_LIMITS[task_name]

    result = parse_task_file(team, task_name)
    if not result:
        return 0
    start_time, end_time, msg, progress, exit_code = result    
    if not end_time or exit_code != 0:
        return 0

    print(time.time()-end_time, file=sys.stderr)
    return max(0, int(rate_limit - (time.time() - end_time)))


def create_task(team, task_name, script_name, args, timeout=300):
    if not re.fullmatch(r"[a-z_]+", task_name):
        return "422 Failed to create a task", {"result": "bad task name"}
    if not re.fullmatch(r"[a-z_]+\.?[a-z]*", script_name):
        return "422 Failed to create a task", {"result": "bad script name"}
    
    task_lock_file = open("%s/team%d/lock" % (DB_PATH, team), "a+", 1)
    task_lock_file.seek(0)

    try:
        fcntl.flock(task_lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)

        task_lock_file.truncate()
        task_lock_file.write(task_name + "\n")

    except BlockingIOError:
        lock_trgt = task_lock_file.read().strip()
        if lock_trgt == task_name:
            return "202 Attaching to task", {"result": "ok", "task": task_name}
        else:
            return "409 Conflict", {"result": "another task (%s) is running" % lock_trgt}

    retry_after = get_rate_limit_remaining(team, task_name)
    if retry_after > 0:
        return "429 Too fast", {"result": "too fast", "msg": "too fast, try again after %d secs" % retry_after}

    print("starting task", task_name, args, file=sys.stderr)
    task_result_file = open("%s/team%d/task_%s.out" % (DB_PATH, team, task_name), "w", 1)

    sys.stdout.flush()
    sys.stderr.flush()

    pid1 = os.fork()
    if pid1 == 0:
        try:
            new_stdin = open("/dev/null")
            os.dup2(new_stdin.fileno(), 0)
            
            os.dup2(task_result_file.fileno(), 1)
            os.close(task_result_file.fileno())
    
            new_stderr = open("%s/team%d/tasks.log" % (DB_PATH, team), "a+", 1)
            os.dup2(new_stderr.fileno(), 2)

            # pass fd to child process as aliveness indicator
            os.dup2(task_lock_file.fileno(), 3)
            os.close(task_lock_file.fileno())           
    
            os.chdir("/")
            os.setsid()
            os.umask(0)
    
            pid2 = os.fork()
            if pid2 > 0:
                os._exit(0)
    
            # child survives, now init handles him
            signal.alarm(timeout)
    
            new_args = [str(arg) for arg in args]
            exec_name = "%s/%s" % (SCRIPTS_PATH, script_name)

            print("starting task", task_name, args, file=new_stderr)
            # Make sure that webserver is not running with MemoryDenyWriteExecute=true
            os.execv(exec_name, [exec_name] + new_args)
            os._exit(1)
        except BaseException as e:
            print("error while preparing task", e, file=sys.stderr)
        finally:
            os._exit(1)  # we must die

    status = os.waitpid(pid1, 0)[1]
    # print("waitpid", status, file=sys.stderr)
    if status != 0:
        return "500 Failed to Create Task", {"result": "prepare general fault"}
        
    return "202 Accepted", {"result": "ok", "task": task_name}


def cmd_create_vm(team, args):
    return create_task(team, "create_vm", "create_team_instance.py", [str(team)], timeout=1200)


def cmd_get_vm_info(team, args):
    image_state = open("%s/team%d/image_deploy_state" % (DB_PATH, team)).read().strip()
    team_state = open("%s/team%d/team_state" % (DB_PATH, team)).read().strip()

    info = {"state": "not started", "ip": "none", 
            "root passwd": "none", "net": "isolated"}

    img_ready = image_state == "RUNNING"
    if img_ready:
        root_passwd = open("%s/team%d/root_passwd.txt" % (DB_PATH, team)).read().strip()

        info["state"] = "running"
        info["ip"] = "10.%d.%d.1" % (60 + team//256, team%256)
        info["root passwd"] = root_passwd
        
    if team_state == "CLOUD":
        info["net"] = "opened"
        
    msglines = []
    for field in ["state", "ip", "root passwd", "net"]:
        msglines.append("  %-11s : %s" % (field, info[field]))
    
    config = open("%s/team%d/root_passwd.txt" % (DB_PATH, team)).read().strip()
    return "200 Ok", {"result": "ok", "msg": "\n".join(msglines)}

def cmd_login(team, args):
    AUTOCOMPLETE = ["create_vm", "get_vm_info",
                    "open_network", "isolate_network",
                    "take_snapshot", "list_snapshots", "restore_vm_from_snapshot", "remove_snapshot",
                    "reboot_vm", "help", "man", "oblaka"]
    return "200 Ok", {"result": "ok", "msg": "access granted\n", "team": team, 
                      "autocomplete": AUTOCOMPLETE}

def cmd_open_network(team, args):
    return create_task(team, "open_network", "open_network.py", [str(team)])

def cmd_isolate_network(team, args):
    return create_task(team, "isolate_network", "isolate_network.py", [str(team)])

def cmd_take_snapshot(team, args):
    name = str(args[0])
    if not re.fullmatch(r"[0-9a-zA-Z_]+", name):
        return "422 Failed to take snapshot", {"result": "bad snapshot name"}
    if len(args) < 2 or not args[1].startswith("coins_stopped"):
        return "422 Failed to take snapshot", {"result": "please do 'systemctl stop PirateCoin' before making a snapshot\nor it never finishes. After that exec:\ntake_snapshot <snapshot_name> coins_stopped"}
    return create_task(team, "take_snapshot", "take_snapshot.py", [str(team), name])

def cmd_list_snapshots(team, args):
    return create_task(team, "list_snapshots", "list_snapshots.py", [str(team)])    

def cmd_restore_vm_from_snapshot(team, args):
    name = str(args[0])
    if not re.fullmatch(r"[0-9a-zA-Z_]+", name):
        return "422 Failed to take snapshot", {"result": "bad snapshot name"}    
    return create_task(team, "restore_vm_from_snapshot", "restore_vm_from_snapshot.py", [str(team), name])

def cmd_remove_snapshot(team, args):
    name = str(args[0])
    if not re.fullmatch(r"[0-9a-zA-Z_]+", name):
        return "422 Failed to remove snapshot", {"result": "bad snapshot name"}    
    return create_task(team, "remove_snapshot", "remove_snapshot.py", [str(team), name])

def cmd_reboot_vm(team, args):
    return create_task(team, "reboot_vm", "reboot_vm.py", [str(team)])

def cmd_help(team, args):
    help_msg = """
  create_vm                        - create vm
  get_vm_info                      - get info about vm
  take_snapshot <name>             - take a snapshot
  list_snapshots                   - list snapshots
  restore_vm_from_snapshot <name>  - restore vm from the snapshot
  remove_snapshot <name>           - remove a snapshot
  reboot_vm                        - reboot vm
  isolate_network                  - isolate network from other teams and checksystem
  open_network                     - open network
  help                             - help
  man                              - instructions
""".strip("\n")

    return "200 Ok", {"result": "ok", "msg": help_msg, "team": team}

def cmd_man(team, args):
    man_msg = """
  Step 1: 
    Create the vulnerable vm
      # create_vm
  Step 2:
    Connect to vulnerable vm using ssh client: 
      # get_vm_info
  Step 3:
    After initial setup, make your first vm snapshot, so you can recover to
    that saved state later:
    # take_snapshot <name>
  Step 4:
    Have a nice game!

  If something goes wrong, use these commands:
    # reboot_vm
    # list_snapshots -> restore_vm_from_snapshot <name>
  If you are being hacked too hard use this command:
    # isolate_network
  To reopen the network for the checksystem and other teams use:
    # open_network""".lstrip("\n")

    return "200 Ok", {"result": "ok", "msg": man_msg, "team": team}

def cmd_poll(team, args):
    task_name = args[0]

    if not re.fullmatch(r"[a-z_]+", task_name):
        return "422 Bad request", {"result": "bad task name"}

    is_running = False
    with open("%s/team%d/lock" % (DB_PATH, team), "a+", 1) as task_lock_file:
        task_lock_file.seek(0)
        try:
            fcntl.flock(task_lock_file, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError:
            lock_trgt = task_lock_file.read().strip()
            if lock_trgt == task_name:
                is_running = True

    result = parse_task_file(team, task_name)
    if not result:
        return "422 Bad request", {"result": "bad task name"}

    start_time, end_time, msg, progress, exit_code = result
    ans = {"result": "ok", "task": task_name}
    if progress is not None:
        ans["progress"] = progress
    if msg:
        ans["msg"] = msg
        
    if not is_running:
        status = "200 Ok"
        if "msg" not in ans and not start_time and not end_time and not progress and not exit_code:
            ans["msg"] = "ERR, task silently died"
        elif exit_code != 0 and "msg" not in ans:
            ans["msg"] = "ERR"
    else:
        status = "202 Wait more"

    return status, ans

def cmd_oblaka(team, args):
    msg = """                _                                  
              (`  ).                   _           
             (     ).              .:(`  )`.       
)           _(       '`.          :(   .    )      
        .=(`(      .   )     .--  `.  (    ) )      
       ((    (..__.:'-'   .+(   )   ` _`  ) )                 
`.     `(       ) )       (   .  )     (   )  ._   
  )      ` __.:'   )     (   (   ))     `-'.-(`  ) 
)  )  ( )       --'       `- __.'         :(      )) 
.-'  (_.'          .')                    `(    )  ))
                  (_  )                     ` __.:'          
                                        
--..,___.--,--'`,---..-.--+--.,,-,,..._.--..-._.-a:f--."""
    return "200 Ok", {"result": "ok", "msg": msg}

def application(environ, start_response):
    response_body = b'Request method: %s' % environ['REQUEST_METHOD'].encode()

    if environ["REQUEST_METHOD"] != "POST":
        start_response("405 Method Not Allowed", RESP_HEADERS)
        return [json.dumps({"result": "bad method"}).encode()]

    if "HTTP_X_AUTHORIZATION" not in environ or not environ["HTTP_X_AUTHORIZATION"].startswith("Bearier "):
        start_response("403 Bad Token", RESP_HEADERS)
        return [json.dumps({"result": "no token", "msg": "access denied\n"}).encode()]

    token = environ["HTTP_X_AUTHORIZATION"].replace("Bearier ", "", 1)

    team = authenticate_request_by_token(token)
    if team is None:
        start_response("403 Bad Token", RESP_HEADERS)
        return [json.dumps({"result": "bad token", "msg": "access denied\n"}).encode()]

    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)

    try:
        req = json.loads(request_body.decode("utf-8"))
        cmd = req["cmd"]
        args = req["args"]
    except (json.decoder.JSONDecodeError, KeyError):
        start_response("400 Bad Request", RESP_HEADERS)
        return [json.dumps({"result": "bad request",}).encode()]

    CMDS = {
        "create_vm": (cmd_create_vm, 0, False),
        "get_vm_info": (cmd_get_vm_info, 0, False),
        "take_snapshot": (cmd_take_snapshot, 1, True),
        "list_snapshots": (cmd_list_snapshots, 0, True),
        "restore_vm_from_snapshot": (cmd_restore_vm_from_snapshot, 1, True),
        "remove_snapshot": (cmd_remove_snapshot, 1, True),
        "reboot_vm": (cmd_reboot_vm, 0, True),
        "isolate_network": (cmd_isolate_network, 0, False),
        "open_network": (cmd_open_network, 0, False),
        "help": (cmd_help, 0, False),
        "?": (cmd_help, 0, False),
        "man": (cmd_man, 0, False),
        "oblaka": (cmd_oblaka, 0, False),
        "login": (cmd_login, 0, False),
        "poll": (cmd_poll, 1, False),
    }

    if cmd not in CMDS:
        start_response("422 Bad Request", RESP_HEADERS)
        return [json.dumps({"result": "error", "msg": "bad command, type 'help' for help"}).encode()]

    handler, min_args_num, check_vm_created = CMDS[cmd]

    if check_vm_created:
        image_deploy_state = open("%s/team%d/image_deploy_state" % (DB_PATH, team)).read().strip()
        if image_deploy_state != "RUNNING":
            start_response("422 Not yet", RESP_HEADERS)
            return [json.dumps({"result": "not yet", "msg": "ERROR: create vm first"}).encode()]

    if len(args) < min_args_num:
        start_response("422 Bad Request", RESP_HEADERS)
        return [json.dumps({"result": "error", "msg": "insufficient arguments, type 'help' for help"}).encode()]

    status, ans = handler(team, args)
    print("cmd: team %d, %s -> %s" % (team, " ".join(map(str,[cmd] +  args)), status), file=sys.stderr)

    # print(cmd, args, file=sys.stderr)
    start_response(status, RESP_HEADERS)
    return [json.dumps(ans).encode()]
