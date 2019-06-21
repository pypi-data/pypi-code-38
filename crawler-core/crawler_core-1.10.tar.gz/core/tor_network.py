import re
import gc
import io
import os
import sys
import stem
import time
import socket
import psutil
import shutil
import zipfile
import datetime as dt
import pandas as pd
from core import torrc
from time import sleep
from sqlalchemy import *
from itertools import chain
from datetime import datetime
from core.database import Database
from core.request import Request
from subprocess import Popen, PIPE
from stem.control import Controller
from core.thread_pool import ThreadPool
from multiprocessing import Process

# _database is prepared instance of core>database>Database
_database = None
_table_name = 'tor_list'
_view_name = 'v_tor_list'
_base_url = 'https://www.torproject.org'
_tor_url = '{}/download/download.html'.format(_base_url)
_dip = r'C:\Users\{}\Tor'.format(os.getlogin())  # default install path
_user_path = r'C:\Users\{}'.format(os.getlogin())
_ip_check = 'https://check.torproject.org/'


def install(install_path=_dip):
    """
    :param str install_path:
    Description:
        install_path = is place where you want Tor to be instaled
            default is in Users\yourusername\Tor
    """
    if os.path.isdir(_dip):
        shutil.rmtree(_dip)

    r = Request()
    r.go(_tor_url)
    html = r.response.content
    if type(html) is dict:
        print('Unable to download tor zip package. Try again later.')
        return

    links = html.find_all('a', {'href': True, 'class': 'button'})
    expert_url = [link for link in links if re.search('Expert Bundle', link.decode()) is not None]
    if not expert_url:
        print("Unable to find Expert Bundle.")
        return
    expert_url = expert_url[0].get('href').replace('..', _base_url)

    file = r.go(expert_url, download=True)
    z = zipfile.ZipFile(io.BytesIO(file))
    z.extractall(install_path)

    with open(r'{}\tor_path.txt'.format(_user_path), 'w') as f:
        f.write(install_path)
        f.close()

    # Deploying additional directories needed for tor_network to work
    for folder in ['TorData', 'TorData\data', 'TorData\config']:
        os.mkdir(r'{}\{}'.format(_dip, folder))


def get_ipv4():
    ipv4 = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect(("8.8.8.8", 80))
        ipv4 = s.getsockname()[0]
        s.close()
        return ipv4
    except:
        return ipv4


def tor_table():
    table_cols = [{'name': 'pid', 'type_': Integer},
                  {'name': 'ipv4', 'type_': String(50)},
                  {'name': 'ip', 'type_': String(50)},
                  {'name': 'port', 'type_': Integer},
                  {'name': 'control_port', 'type_': Integer},
                  {'name': 'torrc_path', 'type_': String(3000)},
                  {'name': 'pid_file', 'type_': String(3000)},
                  {'name': 'data_dir', 'type_': String(3000)}]
    _database.create_table(_table_name, table_cols)


def get_free_ports():
    ports = []
    for i in range(2):
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind(('', 0))
        ports.append(tcp.getsockname()[1])
        tcp.close()
    return ports


def clean_tor():
    db_data = _database.select(_table_name)
    df = pd.DataFrame.from_dict(db_data)
    if df.empty is False:
        df = df[df.dat_pro.notnull()]
        for_delete = df.to_dict('records')

        ipv4 = get_ipv4()
        for row in for_delete:
            data_dir = row.get('data_dir')
            torrc_path = row.get('torrc_path')
            ipv4_db = row.get('ipv4')
            if ipv4 == ipv4_db:
                try:
                    if os.path.isdir(data_dir):
                        shutil.rmtree(data_dir)
                    if os.path.exists(torrc_path):
                        os.remove(torrc_path)
                    _database.delete('tor_list')
                except Exception as e:
                    # print("err03", str(e))
                    pass


def check_tor_ip(socket_port):
    r = Request()
    r.request_type = 2
    r.port = socket_port
    r.ip = get_ipv4()
    r.go(_ip_check)
    html = r.response.content
    if type(html) is dict:
        return 403
    tor_ip = None
    tor_node = re.search('''Your IP address appears to be:\s*<strong>(.*?)</strong>''', html.decode(), re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if tor_node is not None:
        tor_ip = tor_node.group(1).strip()

    return tor_ip


def create_controller(address, control_port):
    tc = TorControl()
    tc.create_controller(address=address, control_port=control_port)
    tc.tor_connect()
    tc.tor_authenticate()
    return tc


def new_id(control_port, address=get_ipv4()):
    tc = create_controller(address=address, control_port=control_port)
    tc.controller.signal('NEWNYM')


class Base:
    _database = None
    _maxtor = 5

    def __init__(self):
        print(self._database, self._maxtor)
        self._database = self._database
        self._maxtor = self._maxtor


class TorControl:
    """
        Description:
        Class task is to control tor expert programs.
        - Connect python program on it so it can send requests.
        - Change identity(exit node ip) of tor expert if it is needed.
        - Close, Kill or Delete everything for connected tor instance
    """
    socket_port = None
    control_port = None

    def __init__(self):
        self.SocketOriginal = socket.socket
        self.socket_port = self.socket_port
        self.control_port = self.control_port
        self.controller = None

    def create_controller(self, address='127.0.0.1', control_port=None):
        """Creates control instance for a caller"""
        if control_port is None:
            control_port = self.control_port
        self.controller = Controller.from_port(address=address, port=control_port)

    def tor_connect(self):
        """Connects to control instance"""
        self.controller.connect()

    def tor_authenticate(self):
        """Authenticates controller"""
        self.controller.authenticate()

    def tor_reconnect(self):
        """Connects, cleans cache and authenticates"""
        self.controller.reconnect()

    @staticmethod
    def is_tor_up(pid):
        """Checks is the tor expert pid running in processes"""
        if os.path.exists(pid):
            for process in psutil.process_iter():
                if process.pid == int(pid) and process.name() == 'tor.exe':
                    return True
        return False

    def kill_tor(self, pid, data_dir, torrc_path):
        """
            Kills tor expert pid in running processes.
            Deletes data from data_dir and torrc_path
        """
        for process in psutil.process_iter():
            if process.pid == int(pid) and process.name() == 'tor.exe':
                process.terminate()
        self.clear_data(data_dir, torrc_path)

    def new_id(self, control_port):
        controller = create_controller(address=get_ipv4(), control_port=control_port)
        controller.signal('NEWNYM')

    def new_identity(self, socket_port=None, control_port=9150):
        """Creates new identity(exit node ip) for current tor instance"""
        controller = self.controller
        new_id_status = controller.is_newnym_available()
        new_id_wait_time = controller.get_newnym_wait()
        if new_id_status:
            controller.clear_cache()
            start = time.time()
            process_timeout = 60
            p = Process(target=new_id, args=(control_port,))
            p.start()
            while time.time() - start <= process_timeout:
                if p.is_alive():
                    time.sleep(1)  # Just to avoid hogging the CPU
                else:
                    # All the processes are done, break now.
                    break
            else:
                p.terminate()
                p.join()
            tor_ip = check_tor_ip(socket_port)
            _database.callproc([('update_tor_ip', [tor_ip, socket_port])])
        else:
            print("sleeping", new_id_wait_time)
            sleep(new_id_wait_time)

    def clear_socket(self):
        if socket.socket != self.SocketOriginal:
            socket.socket = self.SocketOriginal

    def shutdown_tor(self, data_dir, torrc_path):
        """Shutdowns tor expert and cleans data behind
        Deletes data from data_dir and torrc_path"""
        self.clear_socket()
        self.controller.signal('SHUTDOWN')
        sleep(30)
        self.clear_data(data_dir, torrc_path)

    @staticmethod
    def clear_data(data_dir, torrc_path):
        """Deletes data from data_dir and torrc_path"""
        if os.path.exists(torrc_path):
            os.remove(torrc_path)
        if os.path.isdir(data_dir):
            shutil.rmtree(data_dir)

    def get_pid(self, data_dir):
        pid = None
        pid_file = '{}\pid'.format(data_dir)
        if os.path.exists(pid_file):
            with open(pid_file) as f:
                pid = f.read().strip()
        return pid


class TorBuild:
    """
    Description:
    Class task is to create new instances of tor
    and save that info to the table.
    """

    def __init__(self, tormax=1, db_type=None, database_config=None, db_con_type=None):
        """database must provide an instance of core>database>Database"""
        if db_type is not None:
            global _database
            Database.db_type = db_type
            _database = Database(database_config, db_con_type)

        self.tc = TorControl()
        self.tors = {}
        while True:
            tor = _database.select(_view_name,filters={'ipv4': get_ipv4()}, view=True)
            if len(tor) >= tormax:
                break
            ports = get_free_ports()
            self.create_tor(*ports)

    def tor_remove(self, pid, data_dir, torrc_path):
        if pid is not None:
            self.tc.kill_tor(pid, data_dir, torrc_path)
        if pid is None:
            self.tc.clear_data(data_dir, torrc_path)

    def create_tor(self, socket_port, control_port, timeout=60):
        start_time = datetime.now()

        # getting tor path
        tor_file_path = r'{}\tor_path.txt'.format(_user_path)
        with open(tor_file_path, 'r') as f:
            tor_path = f.read()

        # preparing variables
        tor_exe = r'{0}\Tor\tor.exe'.format(tor_path)
        data_dir = '{0}\TorData\data\{1}'.format(tor_path, socket_port)
        torrc_path = r'{0}\TorData\config\torrc{1}.config'.format(tor_path, socket_port)

        # create tor expert directory named by socket_port if doesn't exists
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)

        # create torrc file
        torrc_data = torrc.make_torrc(tor_path, socket_port, control_port, get_ipv4())
        with open(torrc_path, "w") as f:
            f.write(torrc_data)

        # start instance of tor
        cmd = [tor_exe, '-f', torrc_path]
        self.p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)

        while True:
            event = self.p.stdout.readline().strip()
            diff = datetime.now() - start_time
            pid = self.tc.get_pid(data_dir)
            if diff.total_seconds() > timeout:
                self.tor_remove(pid, data_dir, torrc_path)
                err = 'Too long to establish tor circuit over {0} seconds'.format(diff.seconds)
                return 401
            if re.search('Bootstrapped 100%', str(event)):
                tor_ip = check_tor_ip(socket_port)
                pid_file = '{0}\TorData\data\{1}\pid'.format(tor_path, socket_port)
                new_tor = {'pid': pid, 'ipv4': get_ipv4(),
                           'ip': tor_ip, 'port': socket_port,
                           'control_port': control_port, 'torrc_path': torrc_path,
                           'pid_file': pid_file, 'data_dir': data_dir}

                # create controller instance
                # tc = create_controller(get_ipv4(),control_port)

                _database.insert(_table_name, [new_tor])

                # new_tor.update({'controller': tc})
                self.tors.update({control_port: new_tor})
                return 200
            if re.search('No route to host', str(event)):
                self.tor_remove(pid, data_dir, torrc_path)
                return 402


class TorScanner:
    """
        Description:
        This class task is to find all torrc files that you have created
        until now on your local drives. It will read data for tor expert
        and you have currently running processes of tor instances but
        don't have info what are their connection ports.
        It will delete all torrc data including files and directories
        for that tor instance data is stored. It will free your disc space.
        It will also insert data in table you specified with following columns:
    """

    def __init__(self, db_type, database_config, db_con_type, drives=None):
        """drives- specifiy letters of drive to check"""
        Database.db_type = db_type
        _database = Database(database_config, db_con_type)

        self.torrcs = []
        self.pool = ThreadPool(50)
        self.drives = drives
        self.tor = TorControl()
        self.opened_tors = {}
        self.torrc_scanner()
        if self.opened_tors:
            _database.merge(_table_name, self.opened_tors, filters={'dat_pro': None, 'ipv4': get_ipv4()}, on=['ipv4', 'pid', 'control_port'])
        else:
            _database.callproc([('tor_list_updall', [get_ipv4()])])
        del self.tor

    def torrc_scanner(self):
        datas = []
        dps = psutil.disk_partitions()
        if self.drives is not None:
            drives = [drive.upper() + ":\\" for drive in self.drives]
        else:
            drives = [dp.device for dp in dps if dp.fstype == 'NTFS']
        pool = self.pool
        for drive in drives:
            print(" + scaning drive", drive)
            data = os.walk(drive)
            datas.append(data)
            del data
            gc.collect()

        datas = chain(*datas)
        pool.map(self.scan_torrc, datas)
        pool.wait_completion()
        del datas, self.pool, pool
        gc.collect()

        print(" + scanning done. {} torrc files found".format(len(self.torrcs)))
        self.read_torrc()

    def scan_torrc(self, data, **kwargs):
        """Method thats goes trough all folders and files in search for torrc files"""
        root, dirs, files = data
        for f in files:
            result = re.search('torrc\d+.config', f)
            if result:
                torrc_path = os.path.join(root, f)
                if torrc_path not in self.torrcs:
                    self.torrcs.append(torrc_path)

    def read_torrc(self):
        for torrc_path in self.torrcs:
            sys.stdout.write("\r + read torrc files {}".format(torrc_path))
            torrc_data = {'torrc_path': torrc_path, 'ipv4': get_ipv4()}
            # ones found read the file and get details about connection
            path_existance = os.path.exists(torrc_path)
            if path_existance:
                with open(torrc_path) as f:
                    rexs = ['SocksPort\s+(?:\d+\.\d+\.\d+\.\d+:)?(?P<port>\d+)',
                            'ControlPort\s+(?:\d+\.\d+\.\d+\.\d+:)?(?P<control_port>\d+)',
                            'PidFile\s+(?P<pid_file>.*?pid)',
                            'DataDirectory\s+(?P<data_dir>.*?data.\d+)',
                            'SocksListenAddress\s+(?P<ip>\d+\.\d+\.\d+\.\d+)'
                            ]
                    text = f.read()
                    for rex in rexs:
                        x = re.search(rex, text, re.IGNORECASE | re.DOTALL)
                        if x is not None:
                            torrc_data.update(x.groupdict())
                    f.close()

                check_host = torrc_data.get('ip')
                if check_host is None:
                    torrc_data.update({'ip': '127.0.0.1'})

                if torrc_data.get('pid_file') is None or torrc_data.get('data_dir') is None:
                    os.remove(torrc_path)
                    continue

            if len(torrc_data.keys()) > 2:
                try:
                    self.tor.create_controller(address=torrc_data.get('ip'), control_port=int(torrc_data.get('control_port')))
                    self.tor.tor_connect()
                    with open(torrc_data.get('pid_file')) as f:
                        pid = int(f.read().strip())
                        torrc_data.update({'pid': pid})
                    self.opened_tors.update({len(self.opened_tors): torrc_data})
                except Exception as e:
                    # if stem is not possible to establish controller delete
                    del_dir = torrc_data.get('data_dir')
                    try:
                        if os.path.isdir(del_dir):
                            shutil.rmtree(del_dir)

                        if os.path.exists(torrc_path):
                            os.remove(torrc_path)
                    except:
                        err = "file cand be accessed it's used by different process"
        del self.torrcs


class TorService:
    """
        Description:
        This class task is to run at all times and secure that
        - there is always enough tors running
        - cleaning up tor data that is not longer in use
        - change identity from time to time
    """

    def __init__(self, _maxtor=5, _db_type='ms', _db_con_type=1, _database_config=None):
        self.running_tors = {}
        self._maxtor = _maxtor
        self._db_type = _db_type
        self._db_con_type = _db_con_type
        self._database_config = _database_config
        self.main()

    def main(self, id_change=30):
        global _database
        Database.db_type = self._db_type
        _database = Database(self._database_config, self._db_con_type)

        # create table if does not exists in db
        tor_table()
        Database.db_type = self._db_type
        _database = Database(self._database_config, self._db_con_type)

        # find torrc data
        print("+ TorScanner")
        p = Process(target=TorScanner, args=(self._db_type, self._database_config, self._db_con_type,))
        p.start()
        p.join()

        # clean memory garbage
        gc.collect()

        # clean unusable tor's
        print("\n+ Clean unusable tor data")
        clean_tor()

        print("+ Check to change identity")
        # get curent tor_list from database
        tor_list = _database.select(_table_name, filters={'ipv4': get_ipv4()})
        db_df = pd.DataFrame.from_records(tor_list)
        # filter only with defined public ip
        tor_change = {}
        if db_df.empty is False:
            db_df = db_df[~db_df['ip'].isin(['127.0.0.1'])]

            # get all that dont have changed public ip in last 30 min
            db_df['identity_time'] = pd.DatetimeIndex(db_df['identity_time']) + dt.timedelta(minutes=id_change)
            change_id = db_df[(db_df.identity_time.isnull()) | (db_df['identity_time'] < datetime.now())]

            # change tor identity
            tor_change = {records.get('control_port'): records for records in change_id.to_dict('records')}
        print(" + changing ip addres for {} tors".format(len(tor_change)))
        for k, v in tor_change.items():
            try:
                tc = TorControl
                tc.control_port = k
                tc.socket_port = v.get('port')
                tc = tc()
                tc.control_port = None
                tc.create_controller(v.get('ipv4'), control_port=k)
                tc.new_identity(v.get('port'), control_port=k)
            except Exception as e:
                print(str(e))
                err = "Can't create since there is no control_auth_cookie"
                _database.callproc([('close_tor_ip', [get_ipv4(), k])])

        # add new tors if rquired
        print("+ Creating new tors if needed")
        start = time.time()
        process_timeout = 180
        p = Process(target=TorBuild, args=(self._maxtor, self._db_type, self._database_config, self._db_con_type,))
        p.start()
        while time.time() - start <= process_timeout:
            if p.is_alive():
                time.sleep(1)  # Just to avoid hogging the CPU
            else:
                # All the processes are done, break now.
                break
        else:
            # We only enter this if we didn't 'break' above.
            print("timed out on creating tor, killing Process")
            p.terminate()
            p.join()





