import os
import sys
import subprocess as sub
try:
    import fail as f
except ModuleNotFoundError:
    try:
        import os_sys.fail as f
    except ModuleNotFoundError:
        import os_sys_.fail as f

import time as __time__
def chek(a):
        b = __time__.time()
        c = b - a
        return c
def loading(duur):
        a = __time__.time()
        while chek(a) < duur:
                print('|', end='')
                sleep(0.1)
        print(end='
')


__all_names__ = ['main_dir', 'get_import_list', 'get_user', 'cmd', 'info', 'win_version', 'cmd_filter_haak', 'filter_regel', 'cmd_out_list',
           'cmd_out', 'ColorPrint', 'info', 'is_connected', 'ping', 'connect_time', 'internet',
           'chek_speed', 'internet_and_speed', 'cmd_ping', 'cmd',
           'ping_data', 'replace', 'open_site', 'explorer_dict', 'explorer',
           'is_even', 'is_oneven', 'fahr_to_celsius', 'celsius_to_kelvin', 'fahr_to_kelvin', 'convert_c_to_f'
           ]
__all__ = __all_names__
main_dir = os.path.split(os.path.abspath(__file__))[0]

from tkinter import Tk
from tkinter.filedialog import askopenfilename
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing

def explorer_dict():
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    path_split = filename.split('\\')
    le = int(len(path_split) - 1)
    file = path_split[le]
    path_list = list()
    index = 0
    while index < le:
        index += 1
        path_list.append(path_split[index])
    path = ''.join(path_list)
    return {'filepath': filename, 'file': file, 'path': path,\
            'path_list': path_list, 'list': [file, filename, path, path_list]}
def explorer():
    filename = askopenfilename()
    return filename

    
def get_import_list(module):
    get_list = list(module.__all__)
    return get_list
def get_user():
    import getpass
    return getpass.getuser()

import os
import sys

from subprocess import *
import socket
import socket as s
from time import *
import time as _time
import tkinter, time, subprocess as sub, subprocess


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
    except TypeError:
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
        sys.stderr.write(message.strip())

    @staticmethod
    def print_pass(message, end = '
'):
        sys.stdout.write(message.strip())

    @staticmethod
    def print_warn(message, end = '
'):
        sys.stderr.write(message.strip())

    @staticmethod
    def print_info(message, end = '
'):
        sys.stdout.write(message.strip())

    @staticmethod
    def print_bold(message, end = '
'):
        sys.stdout.write(message.strip())
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

main_dir = os.path.split(os.path.abspath(__file__))[0]
def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        print(ex)
        return False
def chek_speed():
        '''voer de functie internet uit en vergelijk de tijd voor en na om te kijken welke vergelijking is'''
        start = time()
        internet()
        eind = time()
        tijd = eind - start
        
        
        return tijd
from subprocess import *
import socket
import socket as s
from time import *
import time as _time
def info():
    '''this is a lib where you can chek or test your wifi if you need commands:
    is_connected() = looks for you of your wifi is connected
    sub() = pings your wifi 8 times and returns the results
    ping() = pings your wifi one time to chek your connection
    connect_time() = looks how fast your wifi connects
    internet() = returns True if you have wifi and False if not
    chek_speed() = looks how vast the wifi reponse on a opening of google.com
    internet_and_speed() = chek of you have wifi and how fast
    cmd_ping() = pings your wifi one time
    cmd(command) = type a command that cmd need to do
    ping_data(times, task) = returns all ping data times for how many times and if task is print he prints all results and always he returns the data
    ping_data return list max_time, min_time, middel, totaal, procent, n_procent, aantal, int(aantal - faal), tt
    not all of this will work on a apple or linux pc
    all tings work only on windows'''
    help_data = '''this is a lib where you can chek or test your wifi if you need commands:
is_connected() = looks for you of your wifi is connected
sub() = pings your wifi 8 times and returns the results
ping() = pings your wifi one time to chek your connection
connect_time() = looks how fast your wifi connects
internet() = returns True if you have wifi and False if not
chek_speed() = looks how vast the wifi reponse on a opening of google.com
internet_and_speed() = chek of you have wifi and how fast
cmd_ping() = pings your wifi one time
cmd(command) = type a command that cmd need to do
ping_data(times, task) = returns all ping data times for how many times and if task is print he prints all results and always he returns the data
ping_data return list max_time, min_time, middel, totaal, procent, n_procent, aantal, int(aantal - faal), tt
not all of this will work on a apple or linux pc
all tings work only on windows'''
    return help_data
def is_connected(hostname = "www.google.com"):
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
     return False

import subprocess
def sub():
    al = subprocess.call('ping -n 8 -l 1000 8.8.8.8')
    
    return al
from platform   import system as system_name  # Returns the system/OS name
from subprocess import call   as system_call  # Execute a shell command

def ping(host='8.8.8.8'):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Ping command count option as function of OS
    param = '-n' if system_name().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    # Pinging
    return system_call(command) == 0

#import time
...
def connect_time():
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname('google.com')
    # connect to the host -- tells us if the host is actually
    # reachable
    before = _time.time()      # from Python 3.3 and above use before = time.perf_counter()
    s = socket.create_connection((host, 80), 2)
    after = _time.time()      # from Python 3.3 and above use after = time.perf_counter()
    return after - before
  except:
    return -1
def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        print(ex)
        return False
def chek_speed():
        '''voer de functie internet uit en vergelijk de tijd voor en na om te kijken welke vergelijking is'''
        start = time()
        internet()
        eind = time()
        tijd = eind - start
        start = time()
        ping()
        eind = time()
        tijd =  eind - start
        
        
        return tijd
def internet_and_speed():
    return str(internet()) + ' time to ping 32 bytes of data ' + str(chek_speed())

def cmd_ping():
    global get_it
    global get_in
    get_it = True
    if internet() == True:
        try:
            get_in = getstatusoutput('ping -n 1 -l 1000 8.8.8.8')
        except Exception as ex:
            print(ex)
            get_it = False
            get_in = None
    else:
        get_in = None
        get_it = False
    return get_in
def cmd(command):
    return getstatusoutput(command)
def ping_data(aantal, taak):
    global get_it
    global get_in
    tt = list()
    string = ''
    totaal = 0
    middel = 0
    faal = 0
    procent = 0
    n_procent = 0
    min_doen = 0
    for i in range(aantal):
        
        restart = time()
        cmd_ping()
        re_end = time()
        if get_it == False:
            faal = faal + 1
        if Exception:
            
            if not get_it == False:
                faal = faal - 1
        if not get_it == False:

            re = re_end - restart
            middel = middel + re
            totaal = totaal + re
            tt.append(re)
            min_doen += 1
    if middel > 0:
        middel = middel / min_doen
    
    per = 100 / aantal
    
    if faal > 0:
        min_p = faal * per
        
        
        procent = 100 - min_p
        n_procent = min_p
    else:
        procent += 100
        faal = 0
    try:
        max_time = max(tt)
        min_time = min(tt)
    except ValueError:
        max_time = None
        min_time = None
    if taak.lower() == 'print':
        if procent > 0:
            print('all the ping times: ' + str(tt))
            print('max time to ping with 1000 bytes of data: ' + str(max_time))
            print('and the min time: ' + str(min_time))
            print('and the average time: ' + str(middel))
            print('and the total time to ping ' + str(aantal) + ' times: ' + str(totaal))
        print('number of sent packages: ' + str(aantal))
        print('number of received packages: ' + str(aantal - faal))
        print('percentage that has not been lost: ' + str(procent) + '%')
        print('percentage that has been lost: ' + str(n_procent) + '%')
    return [max_time, min_time, middel, totaal, procent, n_procent, aantal, int(aantal - faal), tt]

def filter_regel(zinig):
    if not zinig == str:
        zinig = str(zinig)
    OUTPUT = zinig
    
    
    OUTPUT = OUTPUT.replace('(0, \'', '')
    OUTPUT = OUTPUT.replace('\')', '')
    formatted_output = OUTPUT.replace('\
', '
')
    return formatted_output
def data():
    return cmd('ping -n 10 -l 1000 8.8.8.8')


def replace(boodschap, een, twee):
    
    boodschap = boodschap.replace(een, twee)
    return boodschap
def open_site(url):
    import webbrowser as w
    w.open(url)

def is_even(getal):
    return getal % 2 == 0
def is_oneven(getal):
    if not getal % 2 == 0:
        return True
    else:
        return False

def plus(a, b):
    c = a + b
    return c

def min_(a, b):
    c = a - b
    return c

def keer(a, b):
    c = a * b
    return c

def deel(a, b):
    c = a / b
    return c
def maak_tegen(getal):
    if getal < 0:
        getal = abs(getal)
        return getal
    else:
        deel = getal
        deel = deel * 2
        getal = getal - deel
        return getal
    

def afstand(x1, y1, x2, y2):
    if x1 or x2 < 0 or x1 and x2 < 0:
        x = x1 - x2
    elif x1 and x2 == 0:
        x = 0
    else:
        x = x1 - x2
    if y1 or y2 < 0 or y1 and y2 < 0:
        y = y1 - y2
    elif y1 and y2 == 0:
        y = 0
    else:
        y = y1 - y2
    return x, y
def fahr_to_celsius(temp):
    return ((temp * (5/9)) + 32)

def celsius_to_kelvin(temp_c):
    return temp_c + 273.15

def fahr_to_kelvin(temp_f):
    temp_c = fahr_to_celsius(temp_f)
    temp_k = celsius_to_kelvin(temp_c)
    return temp_k

def convert_c_to_f(temp):
    
    c = (temp-32)*5/9
    return [c, str(c)]


import os
print(os.path.abspath(''))




