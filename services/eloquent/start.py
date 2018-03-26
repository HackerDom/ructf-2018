import sys

from webserver.service import start_web_server


def main():
    start_web_server(*sys.argv[1:])

if __name__ == '__main__':
    main()
