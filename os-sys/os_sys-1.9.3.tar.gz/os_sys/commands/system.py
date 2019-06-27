
import os
import sys
from subprocess import *
import socket
import socket as s
from time import *
import time as _time
import tkinter, time, subprocess as sub, wifi, subprocess

main_dir = os.path.split(os.path.abspath(__file__))[0]
working = True
def w():
    global working
    working = True
def ww():
    global working
    working = False
def cmd(command):
    return getstatusoutput(command)

def info(function):
    
    
    
    print(dir(function))
    print(help(function))
def info_o(function):
    
    import turtle as t
    import turtle
    
    print(dir(function))
    print(help(function))
def win_version():
    import sys
    is_windows = hasattr(sys, 'getwindowsversion')
    return is_windows
def cmd_filter_haak(op):
    net = cmd(op)
    
    net_bericht = str(net)
    if '[' in net_bericht:
        haak = '['
        haak2 = ']'
    elif '{' in net_bericht:
        haak = '{'
        haak2 = '}'
    elif '(' in net_bericht:
        haak = '('
        haak2 = ')'
    else:
        print('not a cmd output to filter')
        raise ValueError('geen haken gevonden om op te filteren')
    berijk = range(0, len(net_bericht))
    go = False
    now = False
    message = ''
    for i in berijk:
        
        if net_bericht[i] == haak or go == True or now == True:
            if go == True:
                if not net_bericht[i] == haak2:
                    message += net_bericht[i]
            go = True
            if net_bericht[i] == haak2:
                go = False
                if haak in net_bericht or not haak in net_bericht:
                    now = True
                    go = False
                    if '[' in net_bericht:
                        haak = '['
                        haak2 = ']'
                    elif '{' in net_bericht:
                        haak = '{'
                        haak2 = '}'
                    elif '(' in net_bericht:
                        haak = '('
                        haak2 = ')'
                    else:
                        go = False
                        break
                    continue
    return message
cmd_filter_haak('ping')
def filter_zin(zine):
    zin = ''
    into = ''
    f = 0
    lrn = str(zine)
    print(lrn)
    berijk = range(0, len(lrn))
    for i in berijk:
        if i < int(len(lrn) - 1):
            into = into + lrn[int(i)] + lrn[int(i + 1)]
        else: continue
        if '
' in into:
            zin = zin + into + '
'
            print(zin)
            into = ''
    return zin
def filter_regel(zinig):
    if not zinig == str:
        zinig = str(zinig)
    try:
        cmd(zinig)
    except Exception:
        pass
    OUTPUT = zinig
    if '0, ' in OUTPUT:
        OUTPUT = OUTPUT.replace('0, ', '')
    
    OUTPUT = OUTPUT.replace('(\'', '')
    OUTPUT = OUTPUT.replace('\')', '')
    formatted_output = OUTPUT.replace('\
', '
')
    return formatted_output
def data():
    return cmd('ping -n 10 -l 1000 8.8.8.8')    
def cmd_out_list(command_or_data):
    try:
        e = filter_regel(cmd(command_or_data))
        li = str(cmd(command_or_data)).split(sep='\
')
    except Exception:
        try:
            e = filter_regel(command_or_data)
            li = str(command_or_data).split(sep='\
')
        except Exception as ex:
            print('a error raised')
            raise ex('error')
    return [e, li]
def cmd_out(command_or_data):
    try:
        e = filter_regel(cmd(command_or_data))
        li = str(cmd(command_or_data)).split(sep='\
')
    except TypeError:
        try:
            e = filter_regel(command_or_data)
            li = str(command_or_data).split(sep='\
')
        except Exception as ex:
            print('a error raised')
            raise ex('error')
    return e
import sys

# Colored printing functions for strings that use universal ANSI escape sequences.
# fail: bold red, pass: bold green, warn: bold yellow, 
# info: bold blue, bold: bold white

class ColorPrint:

    @staticmethod
    def print_fail(message, end = '
'):
        sys.stderr.write(message.strip() + end)

    @staticmethod
    def print_pass(message, end = '
'):
        sys.stdout.write(message.strip() + end)

    @staticmethod
    def print_warn(message, end = '
'):
        sys.stderr.write(message.strip() + end)

    @staticmethod
    def print_info(message, end = '
'):
        sys.stdout.write(message.strip() + end)

    @staticmethod
    def print_bold(message, end = '
'):
        sys.stdout.write(message.strip() + end)
if __name__ == '__main__':
    import time
    start = time.time()
    try:
        cmd('arp -a')
    except Exception as ex:
        print_warn(ex)
        working = False
        pass
    stop = time.time()
    re = stop - start
    if working == True:
        print('func cmd(arp -a) state: working.
wifi: True
ping module importable: True
time to compleet func: ' + str(re))
    start = time.time()
    
    try:
        win_version()
    except Exception as ex:
        print_warn(ex)
        working = False
        pass
    stop = time.time()
    re = stop - start
    if working == True:
        print('func win_version state: working.
win_version module importable: True
time to compleet func: ' + str(re))
    start = time.time()
    w()
    try:
        cmd_filter_haak('arp -a')
    except Exception as ex:
        print_warn(ex)
        ww()
        pass
    stop = time.time()
    re = stop - start
    if working == True:
        print('func cmd_filter_haak(arp -a) state: working.
wifi: True
filter_haak module importable: True
time to compleet func: ' + str(re))
    w()
    try:
        filter_regel('arp -a')
    except Exception as ex:
        print_warn(ex)
        ww()
        pass
    stop = time.time()
    re = stop - start
    if working == True:
        print('func filter_regel(arp -a) state: working.
wifi: True
filter_regel module importable: True
time to compleet func: ' + str(re))
    w()
    try:
        cmd_out_list('arp -a')
    except Exception as ex:
        print_warn(ex)
        ww()
        pass
    stop = time.time()
    re = stop - start
    if working == True:
        print('func cmd_out_list(arp -a) state: working.
wifi: True
cmd_out_list module importable: True
time to compleet func: ' + str(re))
    w()
    try:
        cmd_out('arp -a')
    except Exception as ex:
        print_warn(ex)
        ww()
        pass
    stop = time.time()
    re = stop - start
    if working == True:
        print('func cmd_out(arp -a) state: working.
wifi: True
cmd_out module importable: True
time to compleet func: ' + str(re))
    w()
    import getpass
    print(getpass.getuser())


