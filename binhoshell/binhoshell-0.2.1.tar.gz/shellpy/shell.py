# shell.py
import os

from subprocess import Popen, PIPE, TimeoutExpired
from collections import namedtuple

WORKDIR = os.getcwd()

User = namedtuple('User', ['name', 'password'])

def cd(dir):
    global WORKDIR

    if not os.path.isdir(dir):
        os.makedirs(dir)

    WORKDIR = dir

def cmd(cmd):
    if 'sudo' in cmd:
        raise Exception("sudo is not to you, nigga!")
    
    global WORKDIR
    with Popen(cmd, cwd=WORKDIR ,stdout=PIPE, shell=True, env=os.environ) as proc:
        try: 
            proc.communicate(timeout=500)
        except TimeoutExpired:
            proc.kill()

def sudo(cmd, user: User):
    global WORKDIR
    with Popen(cmd, cwd=WORKDIR ,stdout=PIPE, shell=True, env=os.environ) as proc:
        try: 
            proc.communicate(user.password + '\n', timeout=500)
        except TimeoutExpired:
            proc.kill()