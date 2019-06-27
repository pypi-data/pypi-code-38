from __future__ import print_function

import sys

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class CronSatchel(ServiceSatchel):

    name = 'cron'

    ## Service options.

    #ignore_errors = True

    post_deploy_command = None

    @property
    def packager_system_packages(self):
        return {
            FEDORA: ['crontabs'],
            (UBUNTU, '12.04'): ['cron'],
        }

    def set_defaults(self):
        self.env.enabled = True
        self.env.crontabs_available = type(self.genv)() # {name:[cron lines]}
        self.env.command = 'cron'
        self.env.user = 'www-data'
        self.env.python = None
        self.env.crontab_headers = ['PATH=/usr/sbin:/usr/bin:/sbin:/bin\nSHELL=/bin/bash']
        #self.env.stdout_log_template = r'/tmp/chroniker-{SITE}-stdout.$(date +\%%d).log'
        #self.env.stderr_log_template = r'/tmp/chroniker-{SITE}-stderr.$(date +\%%d).log'
        self.env.stdout_log_template = r'/var/log/cron-{SITE}-stdout.log'
        self.env.stderr_log_template = r'/var/log/cron-{SITE}-stderr.log'
        self.env.crontabs_selected = [] # [name]
        self.env.logrotate_templates = [] # [(template_fn, remote_path)]

        self.env.service_commands = {
            START:{
                FEDORA: 'systemctl start crond.service',
                UBUNTU: 'service cron start',
            },
            STOP:{
                FEDORA: 'systemctl stop crond.service',
                UBUNTU: 'service cron stop',
            },
            DISABLE:{
                FEDORA: 'systemctl disable crond.service',
                UBUNTU: 'systemctl disable cron',
                (UBUNTU, '14.04'): 'update-rc.d -f cron remove',
            },
            ENABLE:{
                FEDORA: 'systemctl enable crond.service',
                UBUNTU: 'systemctl enable cron',
                (UBUNTU, '14.04'): 'update-rc.d cron defaults',
                (UBUNTU, '16.04'): 'systemctl enable cron',
            },
            RESTART:{
                FEDORA: 'systemctl restart crond.service',
                UBUNTU: 'service cron restart; sleep 3',
            },
            STATUS:{
                FEDORA: 'systemctl status crond.service',
                UBUNTU: 'service cron status',
            },
        }

    def render_paths(self):
        r = self.local_renderer
        r.env.cron_stdout_log = r.format(r.env.stdout_log_template)
        r.env.cron_stderr_log = r.format(r.env.stderr_log_template)

    @task
    def deploy_logrotate(self):
        r = self.local_renderer
        with self.settings(warn_only=True):
            for template_fn, remote_path in r.env.logrotate_templates:
                r.env.remote_path = remote_path
                r.install_config(local_path=template_fn, remote_path=remote_path)
                r.sudo('chown root:root {remote_path}')
                r.sudo('chmod 600 {remote_path}')
                r.sudo('logrotate {remote_path} --verbose')

    def deploy(self, site=None):
        """
        Writes entire crontab to the host.
        """
        r = self.local_renderer

        self.deploy_logrotate()

        cron_crontabs = []
#         if self.verbose:
#             print('hostname: "%s"' % (hostname,), file=sys.stderr)
        for _site, site_data in self.iter_sites(site=site):
            r.env.cron_stdout_log = r.format(r.env.stdout_log_template)
            r.env.cron_stderr_log = r.format(r.env.stderr_log_template)
            r.sudo('touch {cron_stdout_log}')
            r.sudo('touch {cron_stderr_log}')
            r.sudo('sudo chown {user}:{user} {cron_stdout_log}')
            r.sudo('sudo chown {user}:{user} {cron_stderr_log}')

            if self.verbose:
                print('site:', site, file=sys.stderr)
                print('env.crontabs_selected:', self.env.crontabs_selected, file=sys.stderr)

            for selected_crontab in self.env.crontabs_selected:
                lines = self.env.crontabs_available.get(selected_crontab, [])
                if self.verbose:
                    print('lines:', lines, file=sys.stderr)
                for line in lines:
                    cron_crontabs.append(r.format(line))

        if not cron_crontabs:
            return

        cron_crontabs = self.env.crontab_headers + cron_crontabs
        cron_crontabs.append('\n')
        r.env.crontabs_rendered = '\n'.join(cron_crontabs)
        fn = self.write_to_file(content=r.env.crontabs_rendered)
        print('fn:', fn)
        r.env.put_remote_path = r.put(local_path=fn)
        if isinstance(r.env.put_remote_path, (tuple, list)):
            r.env.put_remote_path = r.env.put_remote_path[0]
        r.sudo('crontab -u {cron_user} {put_remote_path}')

    @task(precursors=['packager', 'user', 'tarball'])
    def configure(self, **kwargs):
        if self.env.enabled:
            kwargs['site'] = ALL
            self.deploy(**kwargs)
            self.enable()
            self.restart()
        else:
            self.disable()
            self.stop()

cron = CronSatchel()
