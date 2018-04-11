#!/usr/bin/python3
# Developed by Alexander Bersenev from Hackerdom team, bay@hackerdom.ru

"""Copies ova to all cloud servers and imports it, deleting the old vm"""

import sys
import json
import time
import os
import re
import shlex
import subprocess
from multiprocessing import Pool

OVA_NAME = sys.argv[1]
VM_NAME = sys.argv[2]

CLOUD_IPS = ["10.60.%d.253" % i for i in range(1, 32+1)]

SSH_OPTS = [
    "-o", "StrictHostKeyChecking=no",
    "-o", "CheckHostIP=no",
    "-o", "NoHostAuthenticationForLocalhost=yes",
    "-o", "BatchMode=yes",
    "-o", "LogLevel=ERROR",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "ConnectTimeout=10",
    "-o", "User=root"
]

THREAD_POOL_SIZE = 16

def log_stderr(*params):
    print(*params, file=sys.stderr)


def deploy(cloud_ip):
    print("deploying %s:" % cloud_ip)

    file_from = OVA_NAME
    file_to_name = "/root/%s.ova" % VM_NAME
    file_to = "%s:%s" % (cloud_ip, file_to_name)
    ssh_arg = ["-e"] + [" ".join(map(shlex.quote, ["ssh"] + SSH_OPTS))]
    code = subprocess.call(["rsync", "--progress"] + ssh_arg +
                               [file_from, file_to])
    if code != 0:
        log_stderr("scp to CLOUD host %s failed" % cloud_ip)
        return False

    code = subprocess.call(["ssh"] + SSH_OPTS + [cloud_ip] +
                           ["/cloud/scripts/reimport_vm.sh", VM_NAME])
    if code != 0:
        log_stderr("reimport vm failed on %s" % cloud_ip)
        return False
    return True



def main():
    p = Pool(THREAD_POOL_SIZE)

    result = dict(zip(CLOUD_IPS, p.map(deploy, CLOUD_IPS)))
    for ip in sorted(result.keys()):
        print("%s: %s" % (ip, result[ip]))

    return 0


if __name__ == "__main__":
    sys.exit(main())
