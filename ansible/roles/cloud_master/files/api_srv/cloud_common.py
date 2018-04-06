# Developed by Alexander Bersenev from Hackerdom team, bay@hackerdom.ru

"""Common functions and consts that are often used by other scripts in 
this directory"""

import subprocess
import sys
import time
import os
import shutil

# change me before the game
ROUTER_HOST = "127.0.0.1"

SSH_OPTS = [
    "-o", "StrictHostKeyChecking=no",
    "-o", "CheckHostIP=no",
    "-o", "NoHostAuthenticationForLocalhost=yes",
    "-o", "BatchMode=yes",
    "-o", "LogLevel=ERROR",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "ConnectTimeout=10"
]


SSH_CLOUD_OPTS = SSH_OPTS + [
    "-o", "User=cloud",
    "-o", "IdentityFile=ructf2018_cloud_deploy"
]


def get_cloud_ip(team):
    try:
        return open("db/team%d/cloud_ip" % team).read().strip()
    except FileNotFoundError as e:
        return None


def log_progress(*params):
    print("progress:", *params, flush=True)


def call_unitl_zero_exit(params, redirect_out_to_err=True, attempts=30, timeout=10):
    if redirect_out_to_err:
        stdout = sys.stderr
    else:
        stdout = sys.stdout

    for i in range(attempts-1):
        if subprocess.call(params, stdout=stdout) == 0:
            return True
        time.sleep(timeout)
    if subprocess.call(params, stdout=stdout) == 0:
        return True

    return None
