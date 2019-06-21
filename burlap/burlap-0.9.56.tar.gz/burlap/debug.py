"""
Various debug tasks.

Note, this is a special module, in that all tasks defined here are auto-imported
into the top-level namespace. That means you access them by calling them directly,
not through "debug."
"""
from __future__ import print_function

import re
from pprint import pprint

from burlap import ContainerSatchel
from burlap.decorators import task, runs_once

def list_to_str_or_unknown(lst):
    if lst:
        return ', '.join(map(str, lst))
    return 'unknown'

class DebugSatchel(ContainerSatchel):

    name = 'debug'

    def set_defaults(self):
        self.env.shell_default_dir = '~'
        self.env.shell_interactive_cmd = '/bin/bash -i'
        #self.env.shell_interactive_cmd = 'cd {start_dir}; /bin/bash -i'
        self.env.shell_default_options = ['-o StrictHostKeyChecking=no']

    @task
    def ping_servers(self):
        self.local('nmap -p 80 -sT {host_string}')

    @task
    def list_settings(self, name):
        from burlap import load_yaml_settings
        load_yaml_settings(name=name, verbose=1)

    @task
    def test_dryrun1(self):
        print('test1.get_dryrun:', self.dryrun)#should show false
        self.local('echo "hello 1"')
        self.test_dryrun2(dryrun=1)
        self.local('echo "hello 3"')

    @task
    def test_dryrun2(self):
        print('test2.get_dryrun:', self.dryrun)#should show true
        self.local('echo "hello 2"')

    @task
    def list_env(self, key=None):
        """
        Displays a list of environment key/value pairs.
        """
        for k, v in sorted(self.genv.items(), key=lambda o: o[0]):
            if key and k != key:
                continue
            print('%s ' % (k,))
            pprint(v, indent=4)

    @task
    def list_sites(self, site='all', *args, **kwargs):
        kwargs['site'] = site
        for _site, data in self.iter_sites(*args, **kwargs):
            print(_site)

    @task
    def list_server_specs(self, cpu=1, memory=1, hdd=1):
        """
        Displays a list of common servers characteristics, like number
        of CPU cores, amount of memory and hard drive capacity.
        """
        r = self.local_renderer

        cpu = int(cpu)
        memory = int(memory)
        hdd = int(hdd)

        # CPU
        if cpu:
            cmd = 'cat /proc/cpuinfo | grep -i "model name"'
            ret = r.run(cmd)
            matches = map(str.strip, re.findall(r'model name\s+:\s*([^\n]+)', ret, re.DOTALL|re.I))
            cores = {}
            for match in matches:
                cores.setdefault(match, 0)
                cores[match] += 1

        # Memory
        if memory:
            cmd = 'dmidecode --type 17'
            ret = r.sudo(cmd)
            matches = re.findall(r'Memory\s+Device\r\n(.*?)(?:\r\n\r\n|$)', ret, flags=re.DOTALL|re.I)
            memory_slot_dicts = []
            for match in matches:
                attrs = dict((_a.strip(), _b.strip()) for _a, _b in re.findall(r'^([^:]+):\s+(.*)$', match, flags=re.MULTILINE))
                memory_slot_dicts.append(attrs)
            total_memory_gb = 0
            total_slots_filled = 0
            total_slots = len(memory_slot_dicts)
            memory_types = set()
            memory_forms = set()
            memory_speeds = set()
            for memory_dict in memory_slot_dicts:
                try:
                    size = int(round(float(re.findall(r'([0-9]+)\s+MB', memory_dict['Size'])[0])/1024.))
                    total_memory_gb += size
                    total_slots_filled += 1
                except IndexError:
                    pass
                _v = memory_dict['Type']
                if _v != 'Unknown':
                    memory_types.add(_v)
                _v = memory_dict['Form Factor']
                if _v != 'Unknown':
                    memory_forms.add(_v)

        # Storage
        if hdd:
            #cmd = 'ls /dev/*d* | grep "/dev/[a-z]+d[a-z]$"'
            cmd = 'find /dev -maxdepth 1 | grep -E "/dev/[a-z]+d[a-z]$"'
            devices = map(str.strip, r.run(cmd).split('\n'))
            total_drives = len(devices)
            total_physical_storage_gb = 0
            total_logical_storage_gb = 0
            drive_transports = set()
            for device in devices:
                #cmd = 'udisks --show-info %s |grep -i "  size:"' % (device)
                cmd = 'udisksctl info -b %s |grep -i "  size:"' % (device)
                ret = r.run(cmd)
                size_bytes = float(re.findall(r'size:\s*([0-9]+)', ret, flags=re.I)[0].strip())
                size_gb = int(round(size_bytes/1024/1024/1024))
                #print device, size_gb
                total_physical_storage_gb += size_gb

                with self.settings(warn_only=True):
                    cmd = 'hdparm -I %s|grep -i "Transport:"' % device
                    ret = self.sudo(cmd)
                    if ret and not ret.return_code:
                        drive_transports.add(ret.split('Transport:')[-1].strip())

            cmd = "df | grep '^/dev/[mhs]d*' | awk '{{s+=$2}} END {{print s/1048576}}'"
            ret = r.run(cmd)
            total_logical_storage_gb = float(ret)

        if cpu:
            print('-'*80)
            print('CPU')
            print('-'*80)
            type_str = ', '.join(['%s x %i' % (_type, _count) for _type, _count in cores.items()])
            print('Cores: %i' % sum(cores.values()))
            print('Types: %s' % type_str)

        if memory:
            print('-'*80)
            print('MEMORY')
            print('-'*80)
            print('Total: %s GB' % total_memory_gb)
            print('Type: %s' % list_to_str_or_unknown(memory_types))
            print('Form: %s' % list_to_str_or_unknown(memory_forms))
            print('Speed: %s' % list_to_str_or_unknown(memory_speeds))
            print('Slots: %i (%i filled, %i empty)' % (total_slots, total_slots_filled, total_slots - total_slots_filled))

        if hdd:
            print('-'*80)
            print('STORAGE')
            print('-'*80)
            print('Total physical drives: %i' % total_drives)
            print('Total physical storage: %s GB' % total_physical_storage_gb)
            print('Total logical storage: %s GB' % total_logical_storage_gb)
            print('Types: %s' % list_to_str_or_unknown(drive_transports))

    @task
    def list_hosts(self):
        print('hosts:', self.genv.hosts)

    @task
    def info(self):
        print('Info')
        print('\tROLE:', self.genv.ROLE)
        print('\tSITE:', self.genv.SITE)
        print('\tdefault_site:', self.genv.default_site)

    @task
    @runs_once
    def shell(self, gui=0, command='', dryrun=None, shell_interactive_cmd_str=None):
        """
        Opens an SSH connection.
        """
        from burlap.common import get_hosts_for_site

        if dryrun is not None:
            self.dryrun = dryrun

        r = self.local_renderer

        if r.genv.SITE != r.genv.default_site:
            shell_hosts = get_hosts_for_site()
            if shell_hosts:
                r.genv.host_string = shell_hosts[0]

        r.env.SITE = r.genv.SITE or r.genv.default_site

        if int(gui):
            r.env.shell_default_options.append('-X')

        if 'host_string' not in self.genv or not self.genv.host_string:
            if 'available_sites' in self.genv and r.env.SITE not in r.genv.available_sites:
                raise Exception('No host_string set. Unknown site %s.' % r.env.SITE)
            raise Exception('No host_string set.')

        if '@' in r.genv.host_string:
            r.env.shell_host_string = r.genv.host_string
        else:
            r.env.shell_host_string = '{user}@{host_string}'

        if command:
            r.env.shell_interactive_cmd_str = command
        else:
            r.env.shell_interactive_cmd_str = r.format(shell_interactive_cmd_str or r.env.shell_interactive_cmd)

        r.env.shell_default_options_str = ' '.join(r.env.shell_default_options)
        if self.is_local:
            self.vprint('Using direct local.')
            cmd = '{shell_interactive_cmd_str}'
        elif r.genv.key_filename:
            self.vprint('Using key filename.')
            # If host_string contains the port, then strip it off and pass separately.
            port = r.env.shell_host_string.split(':')[-1]
            if port.isdigit():
                r.env.shell_host_string = r.env.shell_host_string.split(':')[0] + (' -p %s' % port)
            cmd = 'ssh -t {shell_default_options_str} -i {key_filename} {shell_host_string} "{shell_interactive_cmd_str}"'
        elif r.genv.password:
            self.vprint('Using password.')
            cmd = 'ssh -t {shell_default_options_str} {shell_host_string} "{shell_interactive_cmd_str}"'
        else:
            # No explicit password or key file needed?
            self.vprint('Using nothing.')
            cmd = 'ssh -t {shell_default_options_str} {shell_host_string} "{shell_interactive_cmd_str}"'
        r.local(cmd)

    @task
    def disk(self):
        """
        Display percent of disk usage.
        """
        r = self.local_renderer
        r.run(r.env.disk_usage_command)

    @task
    def tunnel(self, local_port, remote_port):
        """
        Creates an SSH tunnel.
        """
        r = self.local_renderer
        r.env.tunnel_local_port = local_port
        r.env.tunnel_remote_port = remote_port
        r.local(' ssh -i {key_filename} -L {tunnel_local_port}:localhost:{tunnel_remote_port} {user}@{host_string} -N')

    @task
    def test_local(self):
        self.local("echo hello")

    @task
    def test_run(self):
        self.run("echo hello")

    @task
    def test_sudo(self):
        self.sudo("echo hello")

    @task
    def set_satchel_value(self, satchel, key, value):
        """
        Sets a key/value pair in a satchel's local renderer.
        """
        satchel = self.get_satchel(satchel)
        r = satchel.local_renderer
        setattr(r.env, key, value)
        print('Set %s=%s in satchel %s.' % (key, value, satchel.name))

    @task
    def show_satchel_items(self, satchel):
        satchel = self.get_satchel(satchel)
        r = satchel.local_renderer
        for k, v in sorted(r.env.items()):
            print('%s = %s' % (k, v))

debug = DebugSatchel()
