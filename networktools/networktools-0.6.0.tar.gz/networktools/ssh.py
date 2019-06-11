import os
import shlex
import subprocess
import time

"""
To create a bridge on ssh

"""


def bridge(client_port, host_port, host, user, ipv="4"):
    command = "ssh -f -N -%s -L %s:localhost:%s %s@%s" % (
        ipv, client_port, host_port, user, host)
    args = shlex.split(command)
    result = subprocess.Popen(args)
    time.sleep(1)
    return result


def kill(bridge):
    print("Se cierra puenta ssh %s" % bridge)
    command = "kill %s" % bridge.pid
    args = shlex.split(command)
    result = subprocess.Popen(args)
    return result


def clean_port(number):
    command = "lsof -n -i4TCP:%s | grep LISTEN|awk '{ print $2 }' | xargs kill" % number
    ps = subprocess.Popen(command,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    result = ps.communicate()[0]
    return result
