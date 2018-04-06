#!/usr/bin/python3

import sys
import os
import shutil
import crypt

N = 32

if __name__ != "__main__":
    print("I am not a module")
    sys.exit(0)

os.chdir(os.path.dirname(os.path.realpath(__file__)))

try:
    os.mkdir("db")
except FileExistsError:
    print("Remove ./db dir first")
    sys.exit(1)

for i in range(1, N+1):
    os.mkdir("db/team%d" % i)

    open("db/team%d/image_deploy_state" % i, "w").write("NOT_STARTED")
    open("db/team%d/team_state" % i, "w").write("CLOUD")

    shutil.copyfile("root_passwds/passwds/team%d_root_passwd.txt" % i,
                    "db/team%d/root_passwd.txt" % i)

    shutil.copyfile("tokens_hashed/%d.txt" % i, "db/team%d/token_hash.txt" % i)

    open("db/team%d/cloud_ip" % i, "w").write("10.60.%d.253\n" % i)

    root_passwd_filename = "root_passwds/passwds/team%d_root_passwd.txt" % i
    root_passwd = open(root_passwd_filename).read().strip()
    root_passwd_hash = crypt.crypt(root_passwd, crypt.METHOD_SHA512)
    root_passwd_hash_filename = "db/team%d/root_passwd_hash.txt" % i
    open(root_passwd_hash_filename, "w").write(root_passwd_hash + "\n")
