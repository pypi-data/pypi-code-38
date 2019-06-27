from __future__ import print_function

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class InadynSatchel(ServiceSatchel):

    name = 'inadyn'

    def set_defaults(self):

        self.env.daemon_name = 'inadyn'
        self.env.config_user = 'root'
        self.env.config_group = 'debian-inadyn'
        self.env.config_chmod = 640
        self.env.config_path = '/etc/inadyn.conf'
        self.env.system = None
        self.env.dyndns_system = None
        self.env.update_period_sec = 600
        self.env.username = None
        self.env.password = None
        self.env.aliases_by_hostname = {}
        self.env.check_command_template = 'inadyn ' \
            '--username {username} --password "{password}" ' \
            '--update_period_sec {update_period_sec} --dyndns_system {dyndns_system} --alias {alias} --test'

        self.env.service_commands = {
            START:{
                UBUNTU: 'service %s start' % self.env.daemon_name,
            },
            STOP:{
                UBUNTU: 'service %s stop' % self.env.daemon_name,
            },
            DISABLE:{
                UBUNTU: 'systemctl disable %s.service' % self.env.daemon_name,
            },
            ENABLE:{
                UBUNTU: 'systemctl enable %s.service' % self.env.daemon_name,
            },
            RESTART:{
                UBUNTU: 'service %s restart' % self.env.daemon_name,
            },
            STATUS:{
                UBUNTU: 'service %s status' % self.env.daemon_name,
            },
        }

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['inadyn'],
        }

    def _validate_settings(self):
        print('_validate_settings.1')
        r = self.local_renderer
        assert r.env.username, 'No username.'
        print('_validate_settings.1:', r.env.username)
        assert r.env.password, 'No password.'
        assert r.env.dyndns_system, 'No dyndns_system.'
        hn = self.current_hostname
        r.env.aliases = r.env.aliases_by_hostname.get(hn)
        print('_validate_settings.2:', r.env.aliases)
        assert r.env.aliases, 'No aliases for hostname %s.' % hn
        assert isinstance(r.env.aliases, (list, tuple)), 'Aliases must be list.'
        return True

    @task
    def check(self):
        """
        Run inadyn from the commandline to test the configuration.

        To be run like:

            fab role inadyn.check

        """
        self._validate_settings()
        r = self.local_renderer
        r.env.alias = r.env.aliases[0]
        r.sudo(r.env.check_command_template)

    @task
    def write_config(self):
        self._validate_settings()
        r = self.local_renderer
        r.env.remote_path = r.env.config_path
        self.genv.inadyn_aliases = r.env.aliases
        r.install_config(local_path='inadyn/etc_inadyn_conf.template', remote_path=r.env.config_path)
        r.sudo('chown {config_user}:{config_group} {config_path}')
        r.sudo('chmod {config_chmod} {config_path}')
        del self.genv['inadyn_aliases']
        r.install_config(local_path='inadyn/etc_default_inadyn.template', remote_path='/etc/default/inadyn')

    @task(precursors=['packager', 'user'])
    def configure(self):
        if self.env.enabled:
            self.enable()
            self.write_config()
            self.restart()
        else:
            self.disable()
            self.stop()

inadyn = InadynSatchel()
