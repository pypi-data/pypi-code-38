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
    return str('ineternet connection: ' + internet()) + ' time to ping 32 bytes of data ' + str(chek_speed())

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




