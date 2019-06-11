import os
import random

"""
To obtain available ports
"""

def clean_port(port):
    result=int(port)
    return result

def used_ports():
    command="lsof -i TCP|awk '{print $9}'|awk -F'->' '{split($1,a,\":\");print a[2]}'|sed '/^\s*$/d'| grep -Eo \"[0-9]{0,6}\" "
    retvalue = os.popen(command).readlines()
    result= set(map(clean_port, retvalue))
    return result

def get_port(used_ports):
    p0=1025
    pf=65535
    port=0
    while True:
        port=random.randint(p0,pf)
        if not port in used_ports:
            break
    used_ports.add(port)
    return [port, used_ports]

