#!/usr/bin/python3
import paramiko
import sys

from paramiko import SSHException

HOST = "10.10.10.101"
USER = 'root'
PASSWORD = 'gbhfncrjgbhfncrbqgbhfn'
PORT = 22


def main():
    root_dir = '/home/ructf-2018/checkers/eloquent'
    checker_name = 'checker-server.py'
    client = paramiko.SSHClient()
    try:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT, timeout=10)
        c = client.get_transport().open_session()
        c.exec_command("cd {}; ./{} {}".format(root_dir, checker_name, ' '.join(sys.argv[1:])))
        stderr_data = c.recv_stderr(10240).decode()
        stdout_data = c.recv(10240).decode()
        print(stdout_data.strip())
        print('stdout: ' + repr(stdout_data), file=sys.stderr)
        print('stderr: ' + repr(stderr_data), file=sys.stderr)
        exit(int(c.recv_exit_status()))
    except SSHException as e:
        exit(104)
    finally:
        client.close()

if __name__ == '__main__':
    main()

