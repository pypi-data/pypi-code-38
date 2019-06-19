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
    """Memoization decorator.
    """
    cache = dict()

    def memoized_function(*args):
        if args in cache:
            return cache[args]
        cache[args] = function(*args)
        return cache[args]

    return memoized_function


@memoize
def get_all_vms():
    """Get a list of all virtual machine dictionaries that are managed by
    the current vCenter session. This function is memoized.
    
    :return list[dict[str, str]]: list of json dictionaries of virtual
                                  machines.
    """
    vms = session.get(entry_url+'/vcenter/vm')
    return json.loads(vms.text)['value']


@memoize
def get_all_vmids():
    """Get the vCenter REST api vmid name for each virtual machine. This
    function is memoized.
    
    :return list[str]: each virtual machine's vmid.
    """
    return [vm['vm'] for vm in get_all_vms()]


@memoize
def get_all_hosts():
    """Get a list of all esx servers managed by the current vCenter session.
    This function is memoized.
    
    :return list[dict[str, str]]: list of host json dictionaries.
    """
    hosts = session.get(entry_url+'/vcenter/host')
    return json.loads(hosts.text)['value']


def get_all_host_ips():
    """Get the IP address of each esx server managed by the current vCenter
    session.
    
    :return list[str]: list of host IP addresses.
    """
    hosts = get_all_hosts()
    return [host['name'] for host in hosts]


def get_vm_by_hostname(vm_name):
    """Get a virtual machine's json dictionary by its hostname.
    
    :param str vm_name: hostname of virtual machine to return.
    :return dict[str, str]: json dictionary of virtual machine.
    """
    for vm in get_all_vms():
        if vm['name'] == vm_name:
            return vm
    return None


def get_host_by_ip(ip):
    """Get an esx host's json dictionary by its IP address.
    
    :param str ip: IP address of host to return.
    :return dict[str, str]: json dictionary of esx host.
    """
    for host in get_all_hosts():
        if host['name'] == ip:
            return host
    return None


class VCenterSession(object):
    """Create a vCenter session and authenticate to the vCenter server. This
    class must be instantiated for all other methods and functions to make
    REST api calls.
    """
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
    """Representation of an esx server.
    """
    def __init__(self, address, username, password):
        self.address = address
        self.username = username
        self.password = password
        self.url = entry_url + "/vcenter/host/{}".format(self.address)
        
    def _get_vmids(self):
        """Get a list of vmids that are specific to the local esx operating
        system.
        
        :return list[str]: list of vmids for all virtual machines.
        """
        command = self.execute('vim-cmd vmsvc/getallvms')
        return [x.strip().split()[0] for x in command[1:]]

    def execute(self, command):
        """Execute a command over ssh on the esx server and return stdout.
        
        :return list[str]: lines of stdout from command execution.
        """
        return stdout(self.address, self.username, self.password, command)

    def list_vm_hostnames(self):
        """Get the hostname for each virtual machine that resides on
        the esx server.
        
        :return list[str]: list of virtual machine hostnames.
        """
        command = self.execute('vim-cmd vmsvc/getallvms')
        return [x.strip().split()[1] for x in command[1:]]

    def list_vm_api_names(self):
        """Get a list of virtual machine REST api names for making api calls.
        
        :return list[str]: virtual machine REST api names.
        """
        return [get_vm_by_hostname(x)['vm'] for x in self.list_vm_hostnames()]

    def list_vm_ips(self):
        """Get a list of virtual machine IP addresses. Virtual machines will
        only return an IP address if their power state is on.
        """
        rtn = list()
        for vmid in self._get_vmids():
            pre = "vim-cmd vmsvc/get.guest "
            suf = " | egrep -o '([0-9]{1,3}\\.){3}[0-9]{1,3}'"
            rtn.append(self.execute(pre+vmid+suf)[0])
        return rtn

    def enter_maint_mode(self):
        """Put this esx server into maintenance mode.
        """
        self.execute('esxcli system maintenanceMode set --enable true')

    def exit_maint_mode(self):
        """Exit this esx server from maintenance mode.
        """
        self.execute('esxcli system maintenanceMode set --enable false')

    def reboot(self):
        """Reboot this esx server.
        """
        self.execute('reboot')

    @memoize
    def get_vms(self):
        """Get a list of instantiated Vm objects for each virtual machine on
        this esx server. This method is memoized.
        
        :return list[serverdev.model.Vm]: list of instantiated virtual
                                          machines.
        """
        return [Vm(vmid) for vmid in self.list_vm_api_names()]


class Vm(object):
    """Representation of virtual machine.
    """
    def __init__(self, vmid):
        """
        :param str vmid: REST api name for this virtual machine.
        """
        if vmid not in get_all_vmids():
            error = "{} is not a valid virtual machind."
            raise InvalidVirtualMachine(error.format(self.vmid))
        self.vmid = vmid
        self.url = entry_url + '/vcenter/vm/' + vmid

    def poweroff(self):
        """Turn off a virtual machine.
        """
        print(self.url+'/power/stop')
        session.post(self.url+'/power/stop')

    def poweron(self):
        """Turn on a virtual machine.
        """
        print(self.url+'/power/start')
        session.post(self.url+'/power/start')

    @memoize
    def get_disk_names(self):
        """Get the REST api disk names for all drives on a virtual machine.
        This function is memoized.
        
        :return list[str]: list of virtual disk names.
        """
        disks = session.get(self.url+'/hardware/disk')
        return [x['disk'] for x in json.loads(disks.text)['value']]

    def get_disks(self):
        """Get a list of a virtual machine disk's json dictionaries.
        
        :return list[dict[str, str]]: list of disk json dictionaries.
        """
        rtn = list()
        for disk in self.get_disk_names():
            disk = json.loads(session.get(self.url+'/hardware/disk/'+disk).text)
            rtn.append(disk)
        return rtn

    def unmap_disk(self, disk):
        """Unmap a disk from a virtual machine by its REST api disk name. Disk
        files are note deleted, just removed from virtual machine configuration.
        
        :param str disk: disk to unmap from virtual machine.
        """
        if disk not in self.get_disk_names():
            error = "{} is not a valid disk for this virtual machine."
            raise InvalidVirtualDisk(error.format(disk))
        session.delete(self.url+'/hardware/disk/'+disk)

    def unmap_all_disks(self):
        """Unmap all virtual disks from a virtual machine except for the boot
        disk. Disk files are not deleted, just removed from virtual machine
        configuration.
        """
        disks = self.get_disk_names()
        if len(disks) > 1:
            for disk in disks[1:]:
                self.unmap_disk(disk)
