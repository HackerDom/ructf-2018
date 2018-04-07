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


OVA_NAME = sys.argv[1]
VM_NAME = sys.argv[2]

CLOUD_IPS = ["93.158.156.113", "93.158.156.114", "93.158.156.115",
             "93.158.156.116", "93.158.156.117", "93.158.156.118",
             "93.158.156.119", "93.158.156.120", "93.158.156.121",
             "93.158.156.122"]

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


def log_stderr(*params):
    print(*params, file=sys.stderr)


def main():
    for cloud_ip in CLOUD_IPS:
        print("deploying %s:" % cloud_ip)

        file_from = OVA_NAME
        file_to_name = "/root/%s.ova" % VM_NAME
        file_to = "%s:%s" % (cloud_ip, file_to_name)
        ssh_arg = ["-e"] + [" ".join(map(shlex.quote, ["ssh"] + SSH_OPTS))]
        code = subprocess.call(["rsync", "--progress"] + ssh_arg +
                                   [file_from, file_to])
        if code != 0:
            log_stderr("scp to YA host %s failed" % cloud_ip)
            return 1

        code = subprocess.call(["ssh"] + SSH_OPTS + [cloud_ip] +
                               ["/cloud/scripts/reimport_vm.sh", VM_NAME])
        if code != 0:
            log_stderr("reimport vm failed on %s" % cloud_ip)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
