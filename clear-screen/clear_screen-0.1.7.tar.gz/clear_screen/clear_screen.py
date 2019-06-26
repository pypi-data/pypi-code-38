from sys import platform
from subprocess import call


def clear():
    if 'win' not in platform and platform != 'msys':
        cmd = 'clear'
    else:
        cmd = 'cls'
    try:
        call(cmd, shell=True)
    except Exception as e:
        print(type(e).__name__, e)

