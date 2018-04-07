#!/usr/bin/python3
# Developed by Alexander Bersenev from Hackerdom team, bay@hackerdom.ru

"""Connects vm network to the game network"""

import sys
import time
import os
import traceback

from cloud_common import (get_cloud_ip, log_progress, call_unitl_zero_exit,
                          SSH_OPTS, SSH_CLOUD_OPTS, ROUTER_HOST)

TEAM = int(sys.argv[1])


def log_stderr(*params):
    print("Team %d:" % TEAM, *params, file=sys.stderr)


def main():
    team_state = open("db/team%d/team_state" % TEAM).read().strip()

    if team_state == "NOT_CLOUD":
        cmd = ["sudo", "/root/cloud/open_network.sh", str(TEAM)]
        ret = call_unitl_zero_exit(["ssh"] + SSH_CLOUD_OPTS + [ROUTER_HOST] + cmd)
        if not ret:
            log_stderr("open_network")
            return 1
        team_state = "CLOUD"
        open("db/team%d/team_state" % TEAM, "w").write(team_state)
    
    if team_state == "CLOUD":
        print("msg: OK")
        return 0

    return 1

if __name__ == "__main__":
    sys.stdout = os.fdopen(1, 'w', 1)
    print("started: %d" % time.time())
    exitcode = 1
    try:
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        exitcode = main()
    except:
        traceback.print_exc()
    print("exit_code: %d" % exitcode)
    print("finished: %d" % time.time())
