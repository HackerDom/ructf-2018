#!/usr/bin/python3
import paramiko
import sys

HOST = "10.10.10.101"
PORT = 22


p = """t1 9555927887
t2 1108210189
t3 9197244457
t4 1892762356
t5 0451775639
t6 3393858379
t7 5931258887
t8 0250036452
t9 2793909637
t10 2333111087
t11 8700907488
t12 1591854481
t13 2545930155
t14 4625047383
t15 8873411276
t16 9237302601
t17 8714345800
t18 5069072629
t19 0583341529
t20 9164791796
t21 4748005792
t22 6820862775
t23 2547599042
t24 3808213234
t25 9616701247
t26 1902317814
t27 1365696752
t28 8558037625""".split('\n')


def main():
    psws = {}
    for k in p:
        num, psw = k.split()
        psws[num] = psw
    print(psws)
    if sys.argv[1] == 'info':
        print("vulns 1")
        exit(101)
    root_dir = '/home/ructf-2018/checkers/eloquent'
    checker_name = 'checker-server.py'
    if sys.argv[1] in ('put', 'get', 'check'):
        index = sys.argv[2].split('.')[2]
        login = 't' + index
        password = psws[login]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOST, username=login, password=password, port=PORT)
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
