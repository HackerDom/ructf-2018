#!/usr/bin/python3
from subprocess import check_output
from os import system


def ru(name):
    system("useradd -m -d /home/{}".format(name))


def main():
    for i in range(30):
        ru("team{}".format(i))
    system("sudo chmod o= /home/*")


if __name__ == '__main__':
    main()
