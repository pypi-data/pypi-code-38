import requests
import json
import sys
import paramiko
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3 import disable_warnings


session = None
entry_url = None


class InvalidVirtualMachine(Exception):
    pass


class InvalidVirtualDisk(Exception):
    pass


class SshException(Exception):
    pass


def stdout(host, username, password, command):
    """Execute a command on a remote host and return stdout as a list of lines.

    :param str host: IP address of server to connect to.
    :param str username: username of host to connect to.
    :param str password: password of host to connect to.
    :param str command: command to execute op remote host.
    :return list[str]: list of lines of stdout from command.
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(host, 22, username, password)
        sin, sout, serr = ssh.exec_command(command, timeout=3)
        if sys.version[0] == '2':
            return sout.read().split('\n')[:-1]
        return str(sout.read(), 'utf-8').split('\n')[:-1]

    except paramiko.AuthenticationException:
        print('Incorrect username or password for {}'.format(host))
    except paramiko.SSHException:
        print('Unable to connect to host {}'.format(host))
    finally:
        ssh.close()


def memoize(function):
    cache = dict()

    def memoized_function(*args):
        if args in cache:
            return cache[args]
        cache[args] = function(*args)
        return cache[args]

    return memoized_function


@memoize
def get_all_vms():
    vms = session.get(entry_url+'/vcenter/vm')
    return json.loads(vms.text)['value']


@memoize
def get_all_vmids():
    return [vm['vm'] for vm in get_all_vms()]


@memoize
def get_all_hosts():
    hosts = session.get(entry_url+'/vcenter/host')
    return json.loads(hosts.text)['value']


def get_all_host_ips():
    hosts = get_all_hosts()
    return [host['name'] for host in hosts]


def get_vm_by_hostname(vm_name):
    for vm in get_all_vms():
        if vm['name'] == vm_name:
            return vm
    return None


def get_host_by_ip(ip):
    for host in get_all_hosts():
        if host['name'] == ip:
            return host
    return None


class VCenterSession(object):
    def __init__(self, address, username, password):
        self.setup(address)
        self.username = username
        self.password = password
        self.address = address
        self.session = session.post(entry_url+'/com/vmware/cis/session', auth=(username, password))

    def setup(self, address):
        global session
        global entry_url
        entry_url = 'https://'+address+"/rest"
        disable_warnings(InsecureRequestWarning)
        session = requests.Session()
        session.verify = False


class EsxHost(object):
    def __init__(self, address, username, password):
        self.address = address
        self.username = username
        self.password = password
        self.url = entry_url + "/vcenter/host/{}".format(self.address)
        
    def _get_vmids(self):
        command = self.execute('vim-cmd vmsvc/getallvms')
        return [x.strip().split()[0] for x in command[1:]]

    def execute(self, command):
        return stdout(self.address, self.username, self.password, command)

    def list_vm_hostnames(self):
        command = self.execute('vim-cmd vmsvc/getallvms')
        return [x.strip().split()[1] for x in command[1:]]

    def list_vm_vmids(self):
        return [get_vm_by_hostname(x)['vm'] for x in self.list_vm_hostnames()]

    def list_vm_ips(self):
        rtn = list()
        for vmid in self._get_vmids():
            pre = "vim-cmd vmsvc/get.guest "
            suf = " | egrep -o '([0-9]{1,3}\\.){3}[0-9]{1,3}'"
            rtn.append(self.execute(pre+vmid+suf)[0])
        return rtn

    def enter_maint_mode(self):
        self.execute('esxcli system maintenanceMode set --enable true')

    def exit_maint_mode(self):
        self.execute('esxcli system maintenanceMode set --enable false')

    def reboot(self):
        self.execute('reboot')

    @memoize
    def get_vms(self):
        return [Vm(vmid) for vmid in self.list_vm_vmids()]


class Vm(object):
    def __init__(self, vmid):
        if vmid not in get_all_vmids():
            error = "{} is not a valid virtual machind."
            raise InvalidVirtualMachine(error.format(self.vmid))
        self.vmid = vmid
        self.url = entry_url + '/vcenter/vm/' + vmid

    def poweroff(self):
        print(self.url+'/power/stop')
        session.post(self.url+'/power/stop')

    def poweron(self):
        print(self.url+'/power/start')
        session.post(self.url+'/power/start')

    @memoize
    def get_disk_names(self):
        disks = session.get(self.url+'/hardware/disk')
        return [x['disk'] for x in json.loads(disks.text)['value']]

    def get_disks(self):
        rtn = list()
        for disk in self.get_disk_names():
            disk = json.loads(session.get(self.url+'/hardware/disk/'+disk).text)
            rtn.append(disk)
        return rtn

    def unmap_disk(self, disk):
        if disk not in self.get_disk_names():
            error = "{} is not a valid disk for this virtual machine."
            raise InvalidVirtualDisk(error.format(disk))
        session.delete(self.url+'/hardware/disk/'+disk)

    def unmap_all_disks(self):
        disks = self.get_disk_names()
        if len(disks) > 1:
            for disk in disks[1:]:
                self.unmap_disk(disk)
