from __future__ import print_function

import re
import getpass

from fabric.api import (
    settings,
    runs_once,
)

from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task, task_or_dryrun
from burlap.common import str_to_callable

def iter_hostnames():
    from burlap.common import get_hosts_retriever, get_verbose

    verbose = get_verbose()

    retriever = get_hosts_retriever()

    hosts = list(retriever(extended=1))
    for _hostname, _data in hosts:
        yield _hostname
#         if _data.ip == env.host_string:
#             yield _hostname
#         elif _data.public_dns_name == env.host_string:
#             yield _hostname


@task_or_dryrun
@runs_once
def list_hostnames():
    for hostname in iter_hostnames():
        print(hostname)


class HostSatchel(Satchel):
    """
    Used for initializing the host.

    Should only be called once, manually on a fresh install to initialize
    the primary user login.

    e.g. fab prod host.initrole host.configure
    """

    name = 'host'

    def set_defaults(self):

        self.env.default_hostname = None
        self.env.default_hosts = []
        self.env.default_user = None
        self.env.default_password = None
        self.env.default_key_filename = None

        self.env.do_initrole = True

        self.env.post_initrole_tasks = []

        self.env.original_user = None
        self.env.original_key_filename = None

        self.env.login_check = False

#         self.env.os_type = None # Linux/Windows/etc
#         self.env.os_distro = None # Ubuntu/Fedora/etc
#         self.env.os_release = None # 12.04/14.04/etc

    def hostname_to_ip(self, hostname):
        r = self.local_renderer
        r.env.hostname = hostname
        return r._local("getent hosts {hostname} | awk '{{ print $1 }}'", capture=True) or ''

    @task
    def is_present(self, host=None):
        """
        Returns true if the given host exists on the network.
        Returns false otherwise.
        """
        r = self.local_renderer
        r.env.host = host or self.genv.host_string
        ret = r._local("getent hosts {host} | awk '{{ print $1 }}'", capture=True) or ''
        if self.verbose:
            print('ret:', ret)
        ret = ret.strip()
        if self.verbose:
            print('Host %s %s present.' % (r.env.host, 'IS' if bool(ret) else 'IS NOT'))
        ip = ret
        ret = bool(ret)
        if not ret:
            return False

        r.env.ip = ip
        with settings(warn_only=True):
            ret = r._local('ping -c 1 {ip}', capture=True) or ''
        packet_loss = re.findall(r'([0-9]+)% packet loss', ret)
#         print('packet_loss:',packet_loss)
        ip_accessible = packet_loss and int(packet_loss[0]) < 100
        if self.verbose:
            print('IP %s accessible: %s' % (ip, ip_accessible))
        return bool(ip_accessible)

    @task
    def purge_keys(self):
        """
        Deletes all SSH keys on the localhost associated with the current remote host.
        """
        r = self.local_renderer
        r.env.default_ip = self.hostname_to_ip(self.env.default_hostname)
        r.env.home_dir = '/home/%s' % getpass.getuser()
        r.local('ssh-keygen -f "{home_dir}/.ssh/known_hosts" -R {host_string}')
        if self.env.default_hostname:
            r.local('ssh-keygen -f "{home_dir}/.ssh/known_hosts" -R {default_hostname}')
        if r.env.default_ip:
            r.local('ssh-keygen -f "{home_dir}/.ssh/known_hosts" -R {default_ip}')

    @task
    def find_working_password(self, usernames=None, host_strings=None):
        """
        Returns the first working combination of username and password for the current host.
        """
        r = self.local_renderer

        if host_strings is None:
            host_strings = []

        if not host_strings:
            host_strings.append(self.genv.host_string)

        if usernames is None:
            usernames = []

        if not usernames:
            usernames.append(self.genv.user)

        for host_string in host_strings:

            for username in usernames:

                passwords = []
                passwords.append(self.genv.user_default_passwords[username])
                passwords.append(self.genv.user_passwords[username])
                passwords.append(self.env.default_password)

                for password in passwords:

                    with settings(warn_only=True):
                        r.env.host_string = host_string
                        r.env.password = password
                        r.env.user = username
                        ret = r._local("sshpass -p '{password}' ssh -o StrictHostKeyChecking=no {user}@{host_string} echo hello", capture=True)
                        #print('ret.return_code:', ret.return_code)
            #             print('ret000:[%s]' % ret)
                        #code 1 = good password, but prompts needed
                        #code 5 = bad password
                        #code 6 = good password, but host public key is unknown

                    if ret.return_code in (1, 6) or 'hello' in ret:
                        # Login succeeded, so we haven't yet changed the password, so use the default password.
                        return host_string, username, password

        raise Exception('No working login found.')

    @task
    def needs_initrole(self, stop_on_error=False):
        """
        Returns true if the host does not exist at the expected location and may need
        to have its initial configuration set.
        Returns false if the host exists at the expected location.
        """

        ret = False

        target_host_present = self.is_present()

        if not target_host_present:
            default_host_present = self.is_present(self.env.default_hostname)
            if default_host_present:
                if self.verbose:
                    print('Target host missing and default host present so host init required.')
                ret = True
            else:
                if self.verbose:
                    print('Target host missing but default host also missing, '
                        'so no host init required.')
#                 if stop_on_error:
#                     raise Exception(
#                         'Both target and default hosts missing! '
#                         'Is the machine turned on and plugged into the network?')
        else:
            if self.verbose:
                print('Target host is present so no host init required.')

        return ret

    @task
    def initrole(self, check=True):
        """
        Called to set default password login for systems that do not yet have passwordless
        login setup.
        """

        if self.env.original_user is None:
            self.env.original_user = self.genv.user

        if self.env.original_key_filename is None:
            self.env.original_key_filename = self.genv.key_filename

        host_string = None
        user = None
        password = None
        if self.env.login_check:
            host_string, user, password = self.find_working_password(
                usernames=[self.genv.user, self.env.default_user],
                host_strings=[self.genv.host_string, self.env.default_hostname],
            )
            if self.verbose:
                print('host.initrole.host_string:', host_string)
                print('host.initrole.user:', user)
                print('host.initrole.password:', password)

#         needs = True
#         if check:
#             needs = self.needs_initrole(stop_on_error=True)
        needs = False

        if host_string is not None:
            self.genv.host_string = host_string
        if user is not None:
            self.genv.user = user
        if password is not None:
            self.genv.password = password

        if not needs:
            return

        assert self.env.default_hostname, 'No default hostname set.'
        assert self.env.default_user, 'No default user set.'

        self.genv.host_string = self.env.default_hostname
        if self.env.default_hosts:
            self.genv.hosts = self.env.default_hosts
        else:
            self.genv.hosts = [self.env.default_hostname]

        self.genv.user = self.env.default_user
        self.genv.password = self.env.default_password
        self.genv.key_filename = self.env.default_key_filename

        # If the host has been reformatted, the SSH keys will mismatch, throwing an error, so clear them.
        self.purge_keys()

        # Do a test login with the default password to determine which password we should use.
#         r.env.password = self.env.default_password
#         with settings(warn_only=True):
#             ret = r._local("sshpass -p '{password}' ssh -o StrictHostKeyChecking=no {user}@{host_string} echo hello", capture=True)
#             print('ret.return_code:', ret.return_code)
# #             print('ret000:[%s]' % ret)
#             #code 1 = good password, but prompts needed
#             #code 5 = bad password
#             #code 6 = good password, but host public key is unknown
#         if ret.return_code in (1, 6) or 'hello' in ret:
#             # Login succeeded, so we haven't yet changed the password, so use the default password.
#             self.genv.password = self.env.default_password
#         elif self.genv.user in self.genv.user_passwords:
#             # Otherwise, use the password or key set in the config.
#             self.genv.password = self.genv.user_passwords[self.genv.user]
#         else:
#             # Default password fails and there's no current password, so clear.
#             self.genv.password = None
#         self.genv.password = self.find_working_password()
#         print('host.initrole,using password:', self.genv.password)

        # Execute post-init callbacks.
        for task_name in self.env.post_initrole_tasks:
            if self.verbose:
                print('Calling post initrole task %s' % task_name)
            satchel_name, method_name = task_name.split('.')
            satchel = self.get_satchel(name=satchel_name)
            getattr(satchel, method_name)()

        print('^'*80)
        print('host.initrole.host_string:', self.genv.host_string)
        print('host.initrole.user:', self.genv.user)
        print('host.initrole.password:', self.genv.password)

    @task
    def reboot_test(self):
        r = self.local_renderer
        r.run('echo before reboot')
        r.reboot(wait=300)
        r.run('echo after reboot')

    def deploy_pre_run(self):

        # If the desired hostname is not present but the default hostname is present,
        # then we assume the host is new or has been reset and needs to be reconfigured.
        if self.env.do_initrole:
            self.initrole()

    def record_manifest(self, *args, **kargs):
        self.initrole()
        return super(HostSatchel, self).record_manifest(*args, **kargs)

    def configure(self):
        # Just a stub. All the magic happens in deploy_pre_run().
        pass

UNKNOWN = '?'

class HostnameSatchel(Satchel):

    name = 'hostname'

    def set_defaults(self):

        self.env.hostnames = {} # {ip: hostname}

        self.env.default_hostnames = {} # {target hostname: original hostname}

        self.env.use_retriever = False

        # The bash command to run to get our public IP as we appear on the WAN.
        self.env.get_public_ip_command = 'wget -qO- http://ipecho.net/plain ; echo'

        self.env.set_hostname_command = 'hostnamectl set-hostname {hostname}'

        self.env.auto_reboot = 1

    def record_manifest(self):
        """
        Returns a dictionary representing a serialized state of the service.
        """
        data = {}
        #data['hostnames'] = sorted(list(set(iter_hostnames())))
        data['hostnames'] = self.env.hostnames
        return data

    def hostname_to_ip(self, hostname):
        r = self.local_renderer
        r.env.hostname = hostname
#         print('self.genv.hosts:',self.genv.hosts)
#         print('self.genv.host_string:',self.genv.host_string)
        ret = r._local("getent hosts {hostname} | awk '{{ print $1 }}'", capture=True) or ''
#         print('ret:', ret)
        return ret

    def iter_hostnames(self):
        """
        Yields a list of tuples of the form (ip, hostname).
        """
        from burlap.common import get_hosts_retriever
        if self.env.use_retriever:
            self.vprint('using retriever')
            self.vprint('hosts:', self.genv.hosts)
            retriever = get_hosts_retriever()
            hosts = list(retriever(extended=1))
            for _hostname, _data in hosts:

                # Skip hosts that aren't selected for this run.
                if self.genv.hosts \
                and _data.ip not in self.genv.hosts \
                and _data.public_dns_name not in self.genv.hosts \
                and _hostname not in self.genv.hosts:
                    continue

                assert _data.ip, 'Missing IP.'
                yield _data.ip, _hostname#_data.public_dns_name
        else:
            self.vprint('using default')
            for ip, hostname in self.env.hostnames.items():
                self.vprint('ip lookup:', ip, hostname)
                if ip == UNKNOWN:
                    ip = self.hostname_to_ip(hostname)
                    if not ip and hostname in self.env.default_hostnames:
                        ip = self.hostname_to_ip(self.env.default_hostnames[hostname])
                elif not ip[0].isdigit():
                    ip = self.hostname_to_ip(ip)
                assert ip, 'Invalid IP.'
                yield ip, hostname

    @task
    def get_public_ip(self):
        """
        Gets the public IP for a host.
        """
        r = self.local_renderer
        ret = r.run(r.env.get_public_ip_command) or ''
        ret = ret.strip()
        print('ip:', ret)
        return ret

    @task
    @runs_once
    def configure(self, reboot=1):
        """
        Assigns a name to the server accessible from user space.

        Note, we add the name to /etc/hosts since not all programs use
        /etc/hostname to reliably identify the server hostname.
        """
        r = self.local_renderer
        for ip, hostname in self.iter_hostnames():
            self.vprint('ip/hostname:', ip, hostname)
            r.genv.host_string = ip
            r.env.hostname = hostname
            with settings(warn_only=True):
                r.sudo('echo "{hostname}" > /etc/hostname')
                r.sudo('echo "127.0.0.1 {hostname}" | cat - /etc/hosts > /tmp/out && mv /tmp/out /etc/hosts')
                r.sudo(r.env.set_hostname_command)
                if r.env.auto_reboot and int(reboot):
                    r.reboot()

class HostsFileSatchel(Satchel):
    """
    Manages customizations to /etc/hosts.
    """

    name = 'hostsfile'

    def set_defaults(self):
        self.env.ipdomains = [] # [[ip, domain]]
        self.env.ipdomain_retriever = None

    @task(precursors=['packager'])
    def configure(self, force=0):
        force = int(force)
        last_hosts = set(tuple(_) for _ in (self.last_manifest.ipdomains or []))
        ipdomains = list(self.env.ipdomains or [])

        current_hosts = set(tuple(_) for _ in ipdomains)
        if self.env.ipdomain_retriever:
            self.vprint('Looking up hosts with:', self.env.ipdomain_retriever)
            current_hosts.update(str_to_callable(self.env.ipdomain_retriever)(role=self.genv.ROLE) or [])
        self.vprint('current hosts:', sorted(current_hosts))

        if force:
            added_hosts = current_hosts
            removed_hosts = last_hosts.difference(current_hosts)
        else:
            added_hosts = current_hosts.difference(last_hosts)
            removed_hosts = last_hosts.difference(current_hosts)

        r = self.local_renderer
        if self.verbose:
            print('ipdomains:', sorted(ipdomains))
            print('added_hosts:', sorted(added_hosts))
            print('removed_hosts:', sorted(removed_hosts))

        for _ip, _domain in sorted(added_hosts):
            r.env.ip = _ip
            r.env.domain = _domain
            r.append(filename='/etc/hosts', text='%s %s' % (_ip, _domain), use_sudo=True)

        for _ip, _domain in sorted(removed_hosts):
            r.env.ip = _ip
            r.env.domain = _domain
            r.sed(filename='/etc/hosts', before='%s %s' % (_ip, _domain), after='', use_sudo=True)

class TimezoneSatchel(Satchel):
    """
    Manages setting the system-wide timezone.

    For a list of standard timezones see:

        https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    """

    name = 'timezone'

    def set_defaults(self):
        self.env.timezone = 'UTC'

    @task
    def get_current_timezone(self):
        ret = self.sudo('dpkg-reconfigure -f noninteractive tzdata') or ''
        matches = re.findall(r'Local time is now:.*?[0-9]+\s+([A-Z]+)\s+[0-9]+', ret)
        self.vprint('matches:', matches)
        if matches:
            return matches[0]
        return (self.run('date +%Z') or self.env.timezone).strip()

    @task(precursors=['packager'])
    def configure(self):
        r = self.local_renderer
        os_ver = self.os_version
        if os_ver.distro == UBUNTU and os_ver.release >= '16.04':
            r.sudo('timedatectl set-timezone {timezone}')
        else:
            # Old way in Ubuntu <= 14.04.
            r.sudo("sudo sh -c 'echo \"{timezone}\" > /etc/timezone'")
            r.sudo('dpkg-reconfigure -f noninteractive tzdata')

host = HostSatchel()
hostname = HostnameSatchel()
hostsfile = HostsFileSatchel()
timezone = TimezoneSatchel()
