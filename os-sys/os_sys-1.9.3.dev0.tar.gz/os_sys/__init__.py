from __future__ import print_function
try:
    from . import install as ins
except:
    import install as ins
from . import *
import os
import sys
import subprocess
import requests
import  zipfile,os,tarfile
import json, urllib.request as urllib
import os
import sys
import subprocess as sub
from os_sys import *
os_sys_work_path = os.path.join(os.path.expanduser('~'), 'os_sys')
if not os.path.isdir(os_sys_work_path):
    os.mkdir(os_sys_work_path)
os_sys_wp = os_sys_work_path
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
        print(end='')

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
        if '\n' in into:
            zin = zin + into + '\n'
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
    formatted_output = OUTPUT.replace('\\n', '\n')
    return formatted_output
def data():
    return cmd('ping -n 10 -l 1000 8.8.8.8')    
def cmd_out_list(command_or_data):
    try:
        e = filter_regel(cmd(command_or_data))
        li = str(cmd(command_or_data)).split(sep='\n')
    except TypeError:
        try:
            e = filter_regel(command_or_data)
            li = str(command_or_data).split(sep='\n')
        except Exception as ex:
            print('a error raised')
            raise ex('error')
    return [e, li]
def cmd_out(command_or_data):
    try:
        e = filter_regel(cmd(command_or_data))
        li = str(cmd(command_or_data)).split(sep='\n')
    except TypeError:
        try:
            e = filter_regel(command_or_data)
            li = str(command_or_data).split(sep='\n')
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
    def print_fail(message, end = '\n'):
        sys.stderr.write(message.strip())

    @staticmethod
    def print_pass(message, end = '\n'):
        sys.stdout.write(message.strip())

    @staticmethod
    def print_warn(message, end = '\n'):
        sys.stderr.write(message.strip())

    @staticmethod
    def print_info(message, end = '\n'):
        sys.stdout.write(message.strip())

    @staticmethod
    def print_bold(message, end = '\n'):
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
        print('func cmd(arp -a) state: working.  wifi: True  ping module importable: True time to compleet func: ' + str(re))
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
        print('func win_version state: working.win_version module importable: True  time to compleet func: ' + str(re))
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
        print('func cmd_filter_haak(arp -a) state: working. wifi: True filter_haak module importable: True time to compleet func: ' + str(re))
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
        print('func filter_regel(arp -a) state: working.wifi : True filter_regel module importable: True time to compleet func: ' + str(re))
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
        print('func cmd_out_list(arp -a) state: working.wifi: True cmd_out_list module importable: True time to compleet func: ' + str(re))
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
        print('func cmd_out(arp -a) state: working.  wifi: True  cmd_out module importable: True 5time to compleet func: ' + str(re))
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
    formatted_output = OUTPUT.replace('\\n', '\n')
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
import time
def show_progres():
    from tqdm import tqdm
    for i in tqdm(range(10)):
         time.sleep(1)
    import time, sys

# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 10 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r"
    if progress >= 1:
        progress = 1
        status = "Done...\r"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text + '\n')
    sys.stdout.flush()

def test():
    # update_progress test script
    print("progress : 'hello'")
    update_progress("hello")
    time.sleep(1)

    print("progress : 3")
    update_progress(3)
    time.sleep(1)

    print("progress : [23]")
    update_progress([23])
    time.sleep(1)

    print("")
    print("progress : -10")
    update_progress(-10)
    time.sleep(2)

    print("")
    print("progress : 10")
    update_progress(10)
    time.sleep(2)

    print("")
    print("progress : 0->1")
    for i in range(100):
        
        update_progress(i/100.0)

    print("")
    print("Test completed")
    time.sleep(1)
if __name__ == '__main__':
    test()

    try:
        from progressbar import *              # just a simple progress bar
        widgets = ['Test: ', Percentage(), ' ', Bar(marker='0',left='[',right=']'),
                   ' ', ETA(), ' ', FileTransferSpeed()] #see docs for other options

        pbar = ProgressBar(widgets=widgets, maxval=500)
        pbar.start()

        for i in range(100,500+1,50):
            # here do something long at each iteration
            pbar.update(i) #this adds a little symbol at each iteration
        pbar.finish()
        print
    except:
        pass

import sys
import re


class ProgressBar(object):
    DEFAULT = 'Progress: %(bar)s %(percent)3d%%'
    FULL = '%(bar)s %(current)d/%(total)d (%(percent)3d%%) %(remaining)d to go'

    def __init__(self, total, width=40, fmt=DEFAULT, symbol='=',
                 output=sys.stderr):
        assert len(symbol) == 1

        self.total = total
        self.width = width
        self.symbol = symbol
        self.output = output
        self.fmt = re.sub(r'(?P<name>%\(.+?\))d',
            r'\g<name>%dd' % len(str(total)), fmt)

        self.current = 0

    def __call__(self):
        percent = self.current / float(self.total)
        size = int(self.width * percent)
        remaining = self.total - self.current
        bar = '[' + self.symbol * size + ' ' * (self.width - size) + ']'

        args = {
            'total': self.total,
            'bar': bar,
            'current': self.current,
            'percent': percent * 100,
            'remaining': remaining
        }
        print('\r' + self.fmt % args, file=self.output, end='')

    def done(self):
        self.current = self.total
        self()
        print('', file=self.output)
from time import sleep
name = __name__ == '__main__'
if name:
    progress = ProgressBar(80)

    
    progress.current += 1
    progress()
    print('')
    sleep(0.1)
    progress.done()


def weather(url="https://data.buienradar.nl/2.0/feed/json"):
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    print(data)
    for key in data.keys():
        print('data:', key)
        try:
            loop = list(data[key]) if type(data) == type({}) else data[key]
        except:
            loop = [data[key]]
        print(loop)
        for part in loop:
            try:
                if type(data[key][part]) == type([]):
                    for p in len(data[key][part]):
                        print(data[key][part][p])
                elif type(data[key][part]) == type({}):
                    for p in list(data[key][part]):
                        print(data[key][part][p])
                else:
                    print(data[key], data[key][part])
            except:
                print(key, part)
def exec_return(code):
    import sys
    from io import StringIO
    import contextlib

    class Proxy(object):
        def __init__(self,stdout,stringio):
            self._stdout = stdout
            self._stringio = stringio
        def __getattr__(self,name):
            if name in ('_stdout','_stringio','write'):
                object.__getattribute__(self,name)
            else:
                return getattr(self._stringio,name)
        def write(self,data):
             self._stdout.write(data)
             self._stringio.write(data)

    @contextlib.contextmanager
    def stdoutIO(stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = Proxy(sys.stdout,stdout)
        yield sys.stdout
        sys.stdout = old


    with stdoutIO() as s:
        exec(code)
    return s.getvalue()


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
def re_install_pip():
    if input('shure to re_install pip(typ: y to re install pip)') == 'y':
        subprocess.getstatusoutput('python -m pip uninstall pip')
        ins.main_pip()
def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode() # uses 'utf-8' for encoding
    else:
        value = bytes_or_str
    return value # Instance of bytes
class com_data():
    def __init__(self):
        self.data = {}
def com(file):
    
    exec(open(file).read())
    try:
        return com_data.data
    except:
        print('no data to return found')
def nump(num, length):
	part = num/length
	ret = []
	for i in range(0, length+1):
		ret.append(part*i)
	return ret
def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode() # uses 'utf-8' for encoding
    else:
        value = bytes_or_str
    return value # Instance of str
class Extract:
    """ a app to extract .zip, .tar.gz and .tar zip files."""
    def __init__(self,path,remove_files_zip=True):
        self.path=path
        self.remove_source_zip=remove_files_zip
        print('Analysing Directory and extracting')
        self.count = 0
        self.extract(self.path)
        print('Extracted total '+str(self.count)+' files')

    def extract(self,path):
        for root, dirs, file in os.walk(path):
            for file_ in file:
                temp = os.path.join(root, file_)
                try:
                    if temp.endswith('zip'):
                        z = zipfile.ZipFile(temp)
                        z.extractall(temp.split('.')[0])
                        z.close()
                        self.count += 1
                    elif temp.endswith('tar.gz'):
                        z=tarfile.open(temp,'r:gz')
                        z.extractall(temp.split('.')[0])
                        self.count += 1
                        z.close()
                    elif temp.endswith('tar') :
                        z=tarfile.open(temp,'r:')
                        z.extractall(temp.split('.')[0])
                        self.count += 1
                        z.close()
                    self.extract(temp.split('.')[0])
                    if self.remove_source_zip:
                        os.remove(temp)
                except Exception as e:
                    print(temp.split('/')[-1]+' is not a supported file type')
extract = Extract
from distutils.sysconfig import get_python_lib as gpl
path = gpl()
osm = []
c_list = []

if __name__ == '__main__':
    nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    for i in os.listdir(path):
        if 'os_sys' in i:
            osm.append(i)
    import string
    for check in osm:
        
        c = string.digits
        for num in range(0, len(c)):
            c_list.append(c[num])
        
        var = int(len(nums))
        for cn in range(0, var):
            
            check_num = nums[cn]
            
            if check_num in check:
                global num1, num2, num3
                etc, etc2, etc3 = check.rsplit('-')
                nums = etc2.rsplit('.')
                
                num1 = int(nums[0])
                num2 = int(nums[1])
                num3 = int(nums[2])
                break


    def v():
        from bs4 import BeautifulSoup
        import requests
        url = "https://pypi.org/project/os-sys/"
        html = str(requests.get(url).content)
        soup = BeautifulSoup(html, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        text = text.replace('\\n', '\n')
        text = str(text)
        line = text.split('\n')
       
        s = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for li in line for phrase in li.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        text = text.replace('\\n', '\n')
        text = str(text)
        line = text.split('\n')
        for l in line:
            l = l.rstrip('\n')
            try:
                name, etc = l.split(' ')
            except:
                pass
            else:
                if 'os-sys' in name:
                    return etc.rsplit('.')
    num_list = []
    dat = v()
    for num in dat:
        num_list.append(int(num))
    num4 = num_list[0]
    num5 = num_list[1]
    num6 = num_list[2]
    if num1 < num4 or num2 < num5 or num3 < num6:
        print('version %(0)s.%(1)s.%(2)s is availble you have version %(3)s.%(4)s.%(5)s' % {'0': num4, '1': num5, '2': num6, '3': num1, '4': num2, '5': num3}, file=sys.stderr)
        raise Exception('you can still import programs but can not run it in main')
def _download(url, file, path=None):
    url = url  
    r = requests.get(url)
    
    
    import os
    if not path == None:
        filepath = os.path.join(path, file)
    else:
        filepath = file
    with open(str(filepath), 'wb') as f:  
        f.write(r.content)
def run_py(data):
    return exec(data)
def run_py_file(file):
    data = open(file).read()
    return exec(data)
class web_open():
    __all__ = ['docs', 'homepage']
    def __init__(self):
        import webbrowser as _w
        self.open = _w.open
        import os as _os
        self.path = _os.path.abspath('')
        self._docs = 'http://www.os-sys.tk/os_sys'
        self._homepage = 'http://www.os-sys.tk/os_sys/os_sys-homepage.html'
    def docs(self):
        self.open(self._docs)
    def homepage(self):
        self.open(self._homepage)
web = web_open()
import threading
class run_cmds_(threading.Thread):
    def __init__(self):
        self.none = None
    def run(self, commands):
        
        from subprocess import Popen, PIPE
        mystring = ''
        process = Popen( "cmd.exe", shell=False, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for st in commands:
            mystring = mystring + st + '\n'
        out, err = process.communicate(mystring)
        return [out, err]
run_cmds = run_cmds_()
def cmds(commands):
    def run(commands):
        
        from subprocess import Popen, PIPE
        mystring = ''
        process = Popen( "cmd.exe", shell=False, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for st in commands:
            mystring = mystring + st + '\n'
        out, err = process.communicate(mystring)
        return [out, err]
    return run(commands)
def docs():
    run_cmds.start(['cd %s' % os.path.join(path, 'mysite'), 'python manage.py runserver 8080'])
    import time
    time.sleep(2)
    import webbrowser as w
    w.open('http://127.0.0.1:8080/polls/')
def help_generator(module):
    for i in dir(module):
        help(i)
def _code(txt):
    b = txt
    d = {}
    for c in (65, 97):
        for i in range(26):
            d[chr(i+c)] = chr((i+13) % 26 + c)

    data = "".join([d.get(c, c) for c in b])
    
    return data
import requests
def download(url, file, path=None):
    url = url  
    r = requests.get(url)
    
    print('downloading:')
    import os
    filepath = os.path.join(path, file) if not file and path == None else os.path.join(os.path.abspath(''), file)
    with open(str(filepath), 'wb') as f:  
        f.write(r.content)
def os_sys_lib():
    from distutils.sysconfig import get_python_lib as gpl
    path = os.path.join(str(gpl()), 'os_sys')
    return path
def more_input():
    init = input()
    mystr = str()
    while not init == 'None':
        mystr = mystr + (str(init)) + '\n'
        init = input()
    
    return mystr

def print_all_dirs(start_dir, except_dir):
    for dirname, dirnames, filenames in os.walk(start_dir):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            print(os.path.join(dirname, subdirname))

        # print path to all filenames.
        for filename in filenames:
            print(os.path.join(dirname, filename))

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if except_dir in dirnames:
            # don't go into any .git directories.
            dirnames.remove(except_dir)
            
class cmd_parser:
    import argparse
    exeple = '''
    def main():
        ''\' Example of taking inputs for megazord bin''\'
        parser = argparse.ArgumentParser(prog='my_megazord_program')
        parser.add_argument('-i', nargs='?', help='help for -i blah')
        parser.add_argument('-d', nargs='?', help='help for -d blah')
        parser.add_argument('-v', nargs='?', help='help for -v blah')
        parser.add_argument('-w', nargs='?', help='help for -w blah')

        args = parser.parse_args()

        collected_inputs = {'i': args.i,
                        'd': args.d,
                        'v': args.v,
                        'w': args.w}
        print 'got input: ', collected_inputs
import argparse

def main():
    \''' Example of taking inputs for megazord bin''\'
    parser = argparse.ArgumentParser(prog='my_megazord_program')
    parser.add_argument('-i', nargs='?', help='help for -i blah')
    parser.add_argument('-d', nargs='?', help='help for -d blah')
    parser.add_argument('-v', nargs='?', help='help for -v blah')
    parser.add_argument('-w', nargs='?', help='help for -w blah')

    args = parser.parse_args()

    collected_inputs = {'i': args.i,
                    'd': args.d,
                    'v': args.v,
                    'w': args.w}
    print 'got input: ', collected_inputs



    '''
msg = 'installation succes'
import requests
def locate():
    import geocoder
    g = geocoder.ip('me')
    return g
if os.path.isfile(gpl() + r'\dont_remove.os_sys-file'):
    pass
else:
    pass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
def getLocation():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=%s" % "1,1")
    options.add_argument("--use-fake-ui-for-media-stream")
    timeout = 20
    driver = webdriver.Chrome(options=options)
    driver.get("https://mycurrentlocation.net/")
    wait = WebDriverWait(driver, timeout)
    longitude = driver.find_elements_by_xpath('//*[@id="longitude"]')
    longitude = [x.text for x in longitude]
    longitude = str(longitude[0])
    latitude = driver.find_elements_by_xpath('//*[@id="latitude"]')
    latitude = [x.text for x in latitude]
    latitude = str(latitude[0])
    alatitude = driver.find_elements_by_xpath('//*[@id="altitude"]')
    alatitude = [x.text for x in alatitude]
    alatitude = str(alatitude[0])
    driver.quit()
    return (latitude,longitude,alatitude)

def distance():
    import geocoder

    import requests
    geo_json = getLocation()

    address=input('enter an address: ')
    g= geocoder.google(address)
    lat_ad=g.latlng[0]
    lon_ad=g.latlng[1]

    user_postition = [geo_json[0], geo_json[1]]
    lat_ip=user_postition[0]
    lon_ip=user_postition[1]

    #Calculate the great circle distance between two points on the earth (specified in decimal degrees)

    from math import radians, cos, sin, asin, sqrt
    # convert decimal degrees to radians 
    lon_ad, lat_ad, lon_ip, lat_ip = map(radians, [lon_ad, lat_ad, lon_ip, lat_ip])

    # haversine formula 
    dlon = lon_ip - lon_ad 
    dlat = lat_ip - lat_ad 
    a = sin(dlat/2)**2 + cos(lat_ad) * cos(lat_ip) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    #end of calculation

    #limit decimals
    km = ('%.0f'%km)

    return str(address+' is about '+str(km)+' km away from you')
def make_text(file):
    try:
        fh = open(str(file) + '.lib', mode='r', encoding='utf-8')
    except Exception:
        data = ''
        pass
    else:
        data = _code(fh.read())
        fh.close()
        print(data)
    fh = open(str(file) + '.lib', mode='w', encoding='utf-8')
    fh.write(str(_code(str(data + more_input()))))
    fh.close()
def object_type(obj):
    m = type(obj)
    t = m
    m = str(t).replace('<class \'', '')
    t = m
    m = str(t).replace('\'>', '')
    return m
obj_type = object_type
from tqdm import tqdm_gui as gui_bar
from tqdm import tqdm_gui
ti = ''
def all_dict(dictory, exceptions=None, file_types=None, maps=True, files=False, print_data=False):
    import os
    global ti
    data = []
    string_data = ''
    e = exceptions
    if 'list' in str(type(e)) or e == None:
        pass
    else:
        raise TypeError('expected a list but got a %s' % type(e))
    e = file_types
    if 'list' in str(type(e)) or e == None:
        pass
    else:
        raise TypeError('expected a list but got a %s' % type(e))
    
    print_ = print_data
    
    for dirname, dirnames, filenames in os.walk(dictory):
        # print path to all subdirectories first.
        if maps:
            for subdirname in dirnames:
                dat = os.path.join(dirname, subdirname)
                data.append(dat)
                string_data = string_data + '\n' + dat
                if print_:
                    print(dat)

        # print path to all filenames.
        if files:
            for filename in filenames:
                s = False
                fname_path = filename
                file = fname_path.split('.', 1)
                no = int(len(file) - 1)
                file_type = '/*.' + str(file[no])
                ti += file_type
                if not e == None:
                    for b in range(0, len(e)):
                        if e[b] == file_type:
                            s = True
                            
                if e == None:
                    s = True
                if s:
                    s = False   
                            
                    dat = os.path.join(dirname, filename)
                    data.append(dat)
                    string_data = string_data + '\n' + dat
                    if print_:
                        
                        print(dat)
        

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if not exceptions == None:
            
            for ip in range(0, int(len(exceptions))):
                exception = exceptions[ip]
                
                if exception in dirnames:
                    # don't go into any .git directories.
                    dirnames.remove(exception)
    
    return [data, string_data]

def plat_info(print_data=False):
    import platform
    import sys

    def linux_distribution():
      try:
        return platform.linux_distribution()
      except:
        return "N/A"
    if print_data:
        print("""Python version: %s
        system: %s
        machine: %s
        platform: %s
        uname: %s
        version: %s
        mac_ver: %s
        """ % (
        sys.version.split('\n'),
        platform.system(),
        platform.machine(),
        platform.platform(),
        platform.uname(),
        platform.version(),
        platform.mac_ver(),
        ))
    return [sys.version.split(' ')[0],
        platform.system(),
        platform.machine(),
        platform.platform(),
        platform.uname(),
        platform.version(),
        platform.mac_ver(),]
import os
import time
def show_progres():
    import time, sys
    from tqdm import tqdm
    for i in tqdm(range(10)):
         time.sleep(1)
import time, sys
def list_out_str(m):
    """returns the list, dictory or tuple in a string"""
    return eval(m)
def dict_out_str(m):
    """returns the list, dictory or tuple in a string"""
    return eval(m)
def tuple_out_str(m):
    """returns the list, dictory or tuple in a string"""
    return eval(m)
# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 10 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text + '\n')
    sys.stdout.flush()
def test():
    # update_progress test script
    print("progress : 'hello'")
    update_progress("hello")
    

    print("progress : 3")
    update_progress(3)
    

    print("progress : [23]")
    update_progress([23])
    
    print("")
    print("progress : -10")
    update_progress(-10)
    

    print("")
    print("progress : 10")
    update_progress(10)
   

    print("")
    print("progress : 0->1")
    for i in range(100):
        
        update_progress(i/100.0)

    print("")
    print("Test completed")
import sys
import time
import threading
stop = False
kill = False
class progress_bar_loading(threading.Thread):
    __all__ = ['run', 'kill']
    def run(self):
            global stop
            global kill
            print('Loading....  ', file=sys.stderr)
            sys.stderr.flush()
            i = 0
            while stop != True:
                    if (i%4) == 0: 
                        sys.stderr.write('\b')
                    elif (i%4) == 1: 
                        sys.stdout.write('\b')
                    elif (i%4) == 2: 
                        sys.stderr.write('\b')
                    elif (i%4) == 3: 
                        sys.stdout.write('\b')

                    sys.stderr.flush()
                    time.sleep(0.2)
                    i+=1

            if kill:
                print('\b\b\b\b ABORT!')
            else: 
                print('\b\b done!')
    def kill(self):
        global kill
        global stop
        kill = True
        stop = True
lijst = nump(1, 1000)
import time
def print_style(item):
    item_ = list(str(item))
    for ik in item_:
        print(ik, end='')
        time.sleep(0.1)

kill = False
import threading
from threading import Thread
run_background = threading.Thread
run_apart = threading.Thread
from tqdm import tqdm as _t_q_d_m_
class tqdm_loop(Thread):
    global kill
    '''
tqdm help
  """
  Decorate an iterable object, returning an iterator which acts exactly
  like the original iterable, but prints a dynamically updating
  progressbar every time a value is requested.
  """

  def __init__(self, iterable=None, desc=None, total=None, leave=True,
               file=None, ncols=None, mininterval=0.1,
               maxinterval=10.0, miniters=None, ascii=None, disable=False,
               unit='it', unit_scale=False, dynamic_ncols=False,
               smoothing=0.3, bar_format=None, initial=0, position=None,
               postfix=None, unit_divisor=1000):
               '''
    __all__ = ['run']
    def __init__(self, _range, sleep):
        self.u = _range
        self.sleep_time = sleep
    def run(self):
        loop = True
        if loop:
            for i in _t_q_d_m_(self.u):
                from time import sleep
                sleep(self.sleep_time)
                if kill:
                    break
            return
    
        
class tqdm(Thread):
    
    '''
tqdm help
  """
  Decorate an iterable object, returning an iterator which acts exactly
  like the original iterable, but prints a dynamically updating
  progressbar every time a value is requested.
  """

  def __init__(self, iterable=None, desc=None, total=None, leave=True,
               file=None, ncols=None, mininterval=0.1,
               maxinterval=10.0, miniters=None, ascii=None, disable=False,
               unit='it', unit_scale=False, dynamic_ncols=False,
               smoothing=0.3, bar_format=None, initial=0, position=None,
               postfix=None, unit_divisor=1000 total=100):
               '''
    __all__ = ['run']
    def __init__(self, args):
        self.args = args
        self.args[total] = 100 if total not in args else args[total]
        self.sleep_time = args[sleep] if sleep in args else 0.1
        bar = tqdm(self.args)
    def update(self, n=1):
        bar.update(n)
    def run(self, between):
        for i in tqdm(range(self.args[total]), self.args):
            import time
            time.sleep(between)
    def close():
        bar.close()
bar = progress_bar_loading()



if __name__ == '__main__':
    test()

        

def bar(rn, fill='.'):
    import time



    loading = '\b' * rn  # for strings, * is the repeat operator
    rest = fill * int(100 - rn)

    # this loop replaces each dot with a hash!
    print('[\r%0s%1s] loading at %2d percent!' % (loading, rest, rn), end='\n')

if __name__ == '__main__':
     for rn in range(1, 101):
        bar(rn)
def get_commands(args):
    if len(args) < 3:
        return
    ret = {}
    begin = 2
    while begin < len(args):
        ret[str(str(str(args[start]).replace('-', '', 1)).replace('--', '', 1))] = args[int(start + 1)]
    return ret
from progress.bar import *
from progress.spinner import *
from progress.counter import *
class progress_types:
    __all__ = ['bar', 'charging_bar', 'filling_sqares_bar', 'filling_circles_bar', 'incremental_bar', 'pixel_bar',
               'shady_bar', 'spinner', 'pie_spinner', 'moon_spinner', 'line_spinner', 'pixel_spinner',
               'counter', 'countdown', 'stack', 'pie']
    bar = Bar
    charging_bar = ChargingBar
    filling_sqares_bar = FillingSquaresBar
    filling_circles_bar = FillingCirclesBar
    incremental_bar = IncrementalBar
    pixel_bar = PixelBar
    shady_bar = ShadyBar
    spinner = Spinner
    pie_spinner = PieSpinner
    moon_spinner = MoonSpinner
    line_spinner = LineSpinner
    pixel_spinner = PixelSpinner
    counter = Counter
    countdown = Countdown
    stack = Stack
    pie = Pie

progres_types = progress_types
progress_types = progress_types
if __name__ == '__main__':
    bar = Bar('Processing', max=20)
    for i in range(20):
        # Do some work
        bar.next()
        print('')
    bar.finish()

def get_newest_version():
    from bs4 import BeautifulSoup

    url = "https://pypi.org/project/os-sys/"
    html = str(requests.get(url).content)
    soup = BeautifulSoup(html)

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    print(text)
    text = text.replace('\\n', '\n')
    text = str(text)
    line = text.split('\n')
    for l in line:
        l = l.rstrip('\n')
        try:
            name, etc = l.split(' ')
        except:
            pass
        else:
            if 'os-sys' in name:
                return etc
'''import inspect as _ins
import __main__ as my_module
_g = [o[0] for o in _ins.getmembers(my_module) if _ins.isfunction(o[1])]
if __name__ == '__main__':
    print(_g)
from . import *'''
_m = ['main_dir', 'get_import_list', 'get_user', 'cmd', 'info', 'win_version', 'cmd_filter_haak', 'filter_regel', 'cmd_out_list',
           'cmd_out', 'ColorPrint', 'info', 'is_connected', 'ping', 'connect_time', 'internet',
           'chek_speed', 'internet_and_speed', 'cmd_ping', 'cmd',
           'ping_data', 'replace', 'open_site', 'explorer_dict', 'explorer',
           'is_even', 'is_oneven', 'fahr_to_celsius', 'celsius_to_kelvin', 'fahr_to_kelvin', 'convert_c_to_f','nump', 'maths', '_code', '_download', 'all_dict', 'docs', 'download', 'get_newest_version', 'gpl', 'make_text', 'more_input', 'obj_type', 'object_type', 'os_sys_lib', 'print_all_dirs', 'show_progres', 'test', 'update_progress',
      'os_sys', 'wifi',
           'commands', 'core', 'programs', 'discription', 'errors', 'fail', 'progress_bars',
           'system', 'upload', 'wifi', 'html_text', 'installers', 'py_install', 'Extract', 'extract', 'doc_maker', 'interpreter', 'frameworks', '_code', '_download', 'all_dict', 'cmds', 'com', 'dict_out_str', 'distance', 'docs', 'download', 'getLocation', 'get_commands', 'get_newest_version', 'gpl', 'help_generator', 'list_out_str', 'locate', 'make_tarfile', 'make_text', 'more_input', 'obj_type', 'object_type', 'os_sys_lib', 'print_all_dirs', 're_install_pip', 'run_py', 'run_py_file', 'show_progres', 'test', 'to_bytes', 'to_str', 'tuple_out_str', 'update_progress', 'v']

__all__ = _m

