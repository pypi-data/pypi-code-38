import socket
import urllib.request
from getpass import getuser
import subprocess
import ipaddress

import threading
import time

# IP address
def localhost():
    '''     Localhost ip address
    '''
    return '127.0.0.1'

def hostname():
    return socket.gethostname()

def username():
    return getuser()

def lan_ip(debug=False):
    '''     Use AF_INET in order to connect to server 8.8.8.8 at port 80
                in order to identify my address on the internet.
                This is called LAN IP ADDRESS
    '''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
        if debug:
            print('found lan ip:',lan_ip)
        return lan_ip
    except:
        return ''


def wan_ip(debug=False):
    try:
        wan_ip = urllib.request.urlopen('http://myip.dnsomatic.com/ ').read()
        if debug:
            print('getting wan ip:',wan_ip)
        return wan_ip.decode()
    except:
        return ''


def statistics():
    return {'hostname': hostname(),
            'username': username(),
            'localhost': localhost(),
            'lan': lan_ip(),
            'wan': wan_ip()
            }


class Network_manager:
    __version__ = 'alpha'
    _tasks = []
    _parallel_limit = 50

    def __init__(self):
        print(' Network Manager')
        print('   Lan IP: {}'.format(lan_ip()))
        print('   Wan IP: {}'.format(wan_ip()))

    # Screen
    def animated_bar(self, task):

        marked = int(task['percent'])
        needed = 100 - marked

        line = ''
        for m in range(marked):
            line += '>'
        # ♪
        for n in range(needed):
            line += '-'

        print('\r  {}   {}% |{}| '.format(task['msg'],task['percent'], line), end='')

    # Process
    def scan_network(self, ip=lan_ip(), mask='24'):
        '''

            get the host ip and replace the last xxx digits with 0

            192.168.1.xxx ->  192.168.1.0

        :param ip:
        :param mask:
        :return:
        '''
        net_ip = ''.join(str(i + '.') for i in ip.split(".")[:-1]) + '0'
        self.net_addr = '{}/{}'.format(net_ip, mask)
        net_ip_obj = ipaddress.ip_network(self.net_addr)
        self.all_hosts = list(net_ip_obj.hosts())
        self.info = subprocess.STARTUPINFO()
        self.info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.info.wShowWindow = subprocess.SW_HIDE

        tasks = 0
        for i, host in enumerate(self.all_hosts):
            if tasks < self._parallel_limit:
                self.insert(host,mask,i)
                tasks += 1
            else:
                for t in self._tasks:
                    # print(t)
                    if t['thread'] is None:
                        t['thread'] = threading.Thread(target=self.ping, args=(t,))
                self.start()
                self.wait()
                tasks = 0
        t = {'msg': 'Scaning {}/{}'.format(self._tasks.__len__(), self.all_hosts.__len__(), self.net_addr),
             'msg': 'Scaning {}/{}'.format(self._tasks.__len__(), self.all_hosts.__len__(), self.net_addr),
             'percent': 100}
        t['msg'] = 'Scaning {}/{}'.format(self.all_hosts.__len__(), self.all_hosts.__len__(), self.net_addr)
        self.animated_bar(task=t)
        print()

    # Tasks
    def insert(self, host,mask, i):
        host = str(host)
        percent = round(float(i / self.all_hosts.__len__()) * 100, 2)
        msg = 'Scaning {}/{}'.format(self._tasks.__len__(), self.all_hosts.__len__(), self.net_addr)
        task = {'thread': None,
                'msg': msg,
                'index': i,
                'host': host,
                'mask': mask,
                'percent': percent,
                'status': None,
                'ping': None}
        # print('\r adding {}'.format(task))
        self.animated_bar(task=task)
        self._tasks.append(task)
        # task['msg'] = 'Scaning {}/{}'.format(self._tasks.__len__(),self.all_hosts.__len__(),self.net_addr)
    def start(self):
        for t in self._tasks:
            if t['status'] == None:
                # print('starting  {}'.format(t))
                t['thread'].start()
        # print('started {}'.format(self._tasks.__len__()))
        time.sleep(1)

        # last one
        # t = dict(self._tasks[-1])
        # t['percent'] = 100
        # self.animated_bar(task=t)
    def wait(self):
        for t in self._tasks:
            if t['thread'].is_alive():
                t['thread'].join()
                # print('stopped thread {}'.format(t['thread']))
        while self.is_full():
            time.sleep(1)

    def is_full(self):
        for t in self._tasks:
            if not t['thread'].is_alive():
                # print('found available')
                return False
        # print('is full')
        return True

    # Function
    def ping(self, task):
        output = subprocess.Popen(['ping', '-n', '1', '-w', '500', str(task['host'])],
                                  stdout=subprocess.PIPE,
                                  startupinfo=self.info).communicate()[0]
        if "Destination host unreachable" in output.decode("utf-8"):
            task['status'] = 'offline'
            task['ping'] = None
            # print('\r {} is unreachable'.format(host))

        elif "Request timed out" in output.decode("utf-8"):
            task['status'] = 'offline'
            task['ping'] = None
            # print('\r {} is offline'.format(host))

        else:
            ping_time = output.decode('utf-8').split('time')[1].split('TTL')[0]
            task['ping'] = ping_time
            task['status'] = 'online'
            # print('\r {}/{} is online  {}'.format(task['host'],task['mask'], ping_time))

        # self.animated_bar(task=task)

    # Show
    def online(self):
        print('\n Online Hosts')
        for t in self._tasks:
            if t['status'] == 'online':
                print(' host {} ping {}'.format(t['host'], t['ping']))

    def offline(self):
        print('\n Offline Hosts')
        for t in self._tasks:
            if t['status'] == 'offline':
                print(' host {} ping {}'.format(t['host'], t['ping']))
