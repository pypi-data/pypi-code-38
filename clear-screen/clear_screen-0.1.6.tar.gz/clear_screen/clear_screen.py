from sys import platform
from subprocess import call


def clear():
    if 'win' in platform:
        cmd = 'cls'
    else:
        cmd = 'clear'
    try:
        call(cmd, shell=True)
    except Exception as e:
        print(type(e).__name__, e)
