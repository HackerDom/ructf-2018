#!/usr/bin/python3
import os

import paramiko
import sys

HOST = "10.10.10.101"
USER = 'root'
PASSWORD = 'gbhfncrjgbhfncrbqgbhfn'
PORT = 22


def main():
    root_dir = '/root/ructf-2018/checkers/eloquent'
    checker_name = 'eloquent.checker.py'
    full_path = os.path.join(root_dir, checker_name)
    command = full_path + ' ' + ' '.join(sys.argv[1:])
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    c = client.get_transport().open_session()
    c.exec_command("cd {}; ./{} {}".format(root_dir, checker_name, ' '.join(sys.argv[1:])))
    stderr_data = c.recv_stderr(10240).decode()
    stdout_data = c.recv(10240).decode()
    print(stdout_data)
    print(stderr_data, file=sys.stderr)

    exit(int(c.recv_exit_status()))
    client.close()

if __name__ == '__main__':
    main()

