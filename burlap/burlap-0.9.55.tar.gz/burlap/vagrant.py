from __future__ import print_function

import re

from fabric.api import hide

from six.moves.urllib.request import urlopen

from burlap.constants import *
from burlap import ContainerSatchel
from burlap.decorators import task

def _to_int(val):
    try:
        return int(val)
    except ValueError:
        return val

DOWNLOAD_LINK_PATTERN = re.compile(r'http[s]{0,1}://[^/]+/vagrant/[0-9\.]+/vagrant[^"]+')

class VagrantSatchel(ContainerSatchel):

    name = 'vagrant'

    def set_defaults(self):
        self.env.box = '?'
        self.env.provider = '?'
        self.env.shell_command = 'vagrant ssh'
        self.env.download_url = 'https://www.vagrantup.com/downloads.html'

    def ssh_config(self, name=''):
        """
        Get the SSH parameters for connecting to a vagrant VM.
        """
        r = self.local_renderer
        with self.settings(hide('running')):
            output = r.local('vagrant ssh-config %s' % name, capture=True)

        config = {}
        for line in output.splitlines()[1:]:
            key, value = line.strip().split(' ', 2)
            config[key] = value
        return config

    def _get_settings(self, config):
        settings = {}

        user = config['User']
        hostname = config['HostName']
        port = config['Port']

        # Build host string
        host_string = "%s@%s:%s" % (user, hostname, port)

        settings['user'] = user
        settings['hosts'] = [host_string]
        settings['host_string'] = host_string

        # Strip leading and trailing double quotes introduced by vagrant 1.1
        settings['key_filename'] = config['IdentityFile'].strip('"')

        settings['forward_agent'] = (config.get('ForwardAgent', 'no') == 'yes')
        settings['disable_known_hosts'] = True

        return settings


    @task
    def version(self):
        """
        Get the Vagrant version.
        """
        r = self.local_renderer
        with self.settings(hide('running', 'warnings'), warn_only=True):
            res = r.local('vagrant --version', capture=True)
        if res.failed:
            return None
        line = res.splitlines()[-1]
        version = re.match(r'Vagrant (?:v(?:ersion )?)?(.*)', line).group(1)
        return tuple(_to_int(part) for part in version.split('.'))


    @task
    def setup(self, name=''):
        r = self.local_renderer
        _settings = self._get_settings(self.ssh_config(name=name))
        if self.verbose:
            print(_settings)
        r.genv.update(_settings)


    @task
    def init(self):
        r = self.local_renderer
        r.local('vagrant init {box}')


    @task
    def up(self):
        r = self.local_renderer
        r.local('vagrant up --provider={provider}')


    @task
    def shell(self):
        r = self.local_renderer
        self.setup()
        r.local(r.env.shell_command)


    @task
    def destroy(self):
        r = self.local_renderer
        r.local('vagrant destroy')


    @task
    def upload(self, src, dst=None):
        r = self.local_renderer
        r.put(local_path=src, remote_path=dst)


    #http://serverfault.com/a/758017/41252
    @task
    def ssh(self):
        r = self.local_renderer
        self.setup()
        hostname, port = r.genv.host_string.split('@')[-1].split(':')
        r.local((
            'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '
            '-i %s %s@%s -p %s') % (r.genv.key_filename, r.genv.user, hostname, port))


    def _settings_dict(self, config):
        settings = {}

        user = config['User']
        hostname = config['HostName']
        port = config['Port']

        # Build host string
        host_string = "%s@%s:%s" % (user, hostname, port)

        settings['user'] = user
        settings['hosts'] = [host_string]
        settings['host_string'] = host_string

        # Strip leading and trailing double quotes introduced by vagrant 1.1
        settings['key_filename'] = config['IdentityFile'].strip('"')

        settings['forward_agent'] = (config.get('ForwardAgent', 'no') == 'yes')
        settings['disable_known_hosts'] = True

        return settings


    @task
    def vagrant(self, name=''):
        """
        Run the following tasks on a vagrant box.

        First, you need to import this task in your ``fabfile.py``::

            from fabric.api import *
            from burlap.vagrant import vagrant

            @task
            def some_task():
                run('echo hello')

        Then you can easily run tasks on your current Vagrant box::

            $ fab vagrant some_task

        """
        r = self.local_renderer
        config = self.ssh_config(name)

        extra_args = self._settings_dict(config)
        r.genv.update(extra_args)

    def vagrant_settings(self, name='', *args, **kwargs):
        """
        Context manager that sets a vagrant VM
        as the remote host.

        Use this context manager inside a task to run commands
        on your current Vagrant box::

            from burlap.vagrant import vagrant_settings

            with vagrant_settings():
                run('hostname')
        """
        config = self.ssh_config(name)

        extra_args = self._settings_dict(config)
        kwargs.update(extra_args)

        return self.settings(*args, **kwargs)

    def status(self, name='default'):
        """
        Get the status of a vagrant machine
        """
        machine_states = dict(self._status())
        return machine_states[name]

    def _status(self):
        if self.version() >= (1, 4):
            return self._status_machine_readable()
        return self._status_human_readable()

    def _status_machine_readable(self):
        with self.settings(hide('running')):
            output = self.local('vagrant status --machine-readable', capture=True)
        tuples = [tuple(line.split(',')) for line in output.splitlines() if line.strip() != '']
        return [(target, data) for timestamp, target, type_, data in tuples if type_ == 'state-human-short']

    def _status_human_readable(self):
        with self.settings(hide('running')):
            output = self.local('vagrant status', capture=True)
        lines = output.splitlines()[2:]
        states = []
        for line in lines:
            if line == '':
                break
            target = line[:25].strip()
            state = re.match(r'(.{25}) ([^\(]+)( \(.+\))?$', line).group(2)
            states.append((target, state))
        return states

    def machines(self):
        """
        Get the list of vagrant machines
        """
        return [name for name, state in self._status()]

    def base_boxes(self):
        """
        Get the list of vagrant base boxes
        """
        return sorted(list(set(name for name, provider in self._box_list())))

    def _box_list(self):
        if self.version() >= (1, 4):
            return self._box_list_machine_readable()
        return self._box_list_human_readable()

    def _box_list_machine_readable(self):
        r = self.local_renderer
        with self.settings(hide('running')):
            output = r.local('vagrant box list --machine-readable', capture=True)
        tuples = [tuple(line.split(',')) for line in output.splitlines() if line.strip() != '']
        res = []
        for timestamp, target, type_, data in tuples:
            if type_ == 'box-name':
                box_name = data
            elif type_ == 'box-provider':
                box_provider = data
                res.append((box_name, box_provider))
            else:
                raise ValueError('Unknown item type')
        return res

    def _box_list_human_readable(self):
        r = self.local_renderer
        with self.settings(hide('running')):
            output = r.local('vagrant box list', capture=True)
        lines = output.splitlines()
        res = []
        for line in lines:
            box_name = line[:25].strip()
            mo = re.match(r'.{25} \((.+)\)$', line)
            box_provider = mo.group(1) if mo is not None else 'virtualbox'
            res.append((box_name, box_provider))
        return res

    @task
    def install_from_upstream(self):
        """
        Installs Vagrant from the most recent package available from their homepage.
        """
        from burlap.system import get_arch, distrib_family
        r = self.local_renderer
        content = urlopen(r.env.download_url).read()
        print(len(content))
        matches = DOWNLOAD_LINK_PATTERN.findall(content)
        print(matches)
        arch = get_arch() # e.g. 'x86_64'
        family = distrib_family()
        if family == DEBIAN:
            ext = '.deb'
            matches = [match for match in matches if match.endswith(ext) and arch in match]
            print('matches:', matches)
            assert matches, "No matches found."
            assert len(matches) == 1, "Too many matches found: %s" % (', '.join(matches))
            r.env.final_download_url = matches[0]
            r.env.local_filename = '/tmp/vagrant%s' % ext
            r.run('wget -O {local_filename} {final_download_url}')
            r.sudo('dpkg -i {local_filename}')
        else:
            raise NotImplementedError('Unsupported family: %s' % family)

    @task(precursors=['packager', 'user'])
    def configure(self, *args, **kwargs):
        self.install_from_upstream()

vagrant = VagrantSatchel()
