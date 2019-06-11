import os
import sys
import json


def read_config():
    print "pathhhh", os.getcwd() # current execution path
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config_dict = json.load(f)
            return config_dict
    else:
        print "config file doesn't exist!"


# transform application to a daemon
def start_daemon():
    pid = os.fork()
    print pid
    if pid > 0:
        sys.exit(0)
    print pid
    os.chdir('/')  # change the current working directory
    print os.getcwd()
    os.setsid()  # creates a new session if the calling process is not a process group leader.
    os.umask(0)

    # do a second fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.exit(1)
    print "here1"
    sys.stdout.flush()
    sys.stderr.flush()
    si = open(os.devnull, 'r')
    so = open(os.devnull, 'w')
    se = open(os.devnull, 'w')

    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    print "here"


def run():
    pass


def main():
    start_daemon()
    run()


if __name__ == '__main__':
    main()
