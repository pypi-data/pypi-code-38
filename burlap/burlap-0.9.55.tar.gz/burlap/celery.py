"""
Celery component.

Note, we manage Celery through Supervisor, since it's extremely difficult to
run several instances of Celery for multiple Apache sites.

"""
from __future__ import print_function

from pprint import pprint

from burlap.constants import *
from burlap import ServiceSatchel
from burlap.decorators import task

class CelerySatchel(ServiceSatchel):

    name = 'celery'

    @property
    def packager_system_packages(self):
        d = {}
        if self.env.use_system_packages:
            d.update({
                FEDORA: ['celery', 'django-celery'],
                UBUNTU: ['celery', 'django-celery'],
            })
        return d

    def set_defaults(self):

        # Better versions are available in PyPI, so don't use system packages by default.
        self.env.use_system_packages = False

        self.env.config_path = '/etc/sysconfig/celeryd'
        self.env.daemon_opts = '--concurrency=1 --loglevel=DEBUG'
        self.env.daemon_path = '/etc/init.d/celeryd'
        self.env.log_path_template = '/var/log/celeryd-{SITE}.log'
        self.env.celerybeat_log_path_template = '/var/log/celerybeat-{SITE}.log'
        self.env.celeryd_command = 'celeryd'
        self.env.has_worker = False
        self.env.daemon_user = 'www-data'
        self.env.numprocs = 1
        self.env.force_stop_command = 'pkill -9 -f celery'
        self.env.celeryd_command_template = None
        self.env.supervisor_directory_template = None#'/usr/local/myproject'

        #DEPRECATED
        self.env.has_celerybeat = False
        self.env.celerybeat_command = 'celerybeat'
        self.env.paths_owned = ['/tmp/celerybeat-schedule*', '/var/log/celery*']
        self.env.celerybeat_opts_template = ('--schedule=/tmp/celerybeat-schedule-{SITE} --pidfile=/tmp/celerybeat-{SITE}.pid '
            '--logfile={celery_celerybeat_log_path} --loglevel=DEBUG')
        self.env.celerybeat_command_template = ('{celery_supervisor_python} {celery_supervisor_django_manage} '
            '{celery_celerybeat_command} {celery_celerybeat_opts}')

        self.env.service_commands = {
            START:{
                FEDORA: 'systemctl start celeryd.service',
                UBUNTU: 'service celeryd start',
            },
            STOP:{
                FEDORA: 'systemctl stop celery.service',
                UBUNTU: 'service celeryd stop',
            },
            DISABLE:{
                FEDORA: 'systemctl disable httpd.service',
                UBUNTU: 'chkconfig celeryd off',
            },
            ENABLE:{
                FEDORA: 'systemctl enable httpd.service',
                UBUNTU: 'chkconfig celeryd on',
            },
            RESTART:{
                FEDORA: 'systemctl stop celeryd.service; pkill -9 -f celery; systemctl start celeryd.service',
                UBUNTU: 'service celeryd stop; pkill -9 -f celery; service celeryd start',
            },
            STATUS:{
                FEDORA: 'systemctl status celeryd.service',
                UBUNTU: 'service celeryd status',
            },
        }

    @task
    def purge(self):
        """
        Clears all pending tasks in the Celery queue.
        """
        self.render_paths()
        r = self.local_renderer
        r.sudo('export SITE={SITE}; export ROLE={ROLE}; {celery_supervisor_django_manage} celeryctl purge')

    @task
    def force_stop(self):
        """
        Forcibly terminates all Celery processes.
        """
        r = self.local_renderer
        with self.settings(warn_only=True):
            r.sudo('pkill -9 -f celery')
        r.sudo('rm -f /tmp/celery*.pid')

    @task
    def set_permissions(self):
        """
        Sets ownership and permissions for Celery-related files.
        """
        r = self.local_renderer
        for path in r.env.paths_owned:
            r.env.path_owned = path
            r.sudo('chown {celery_daemon_user}:{celery_daemon_user} {celery_path_owned}')

    @task
    def render_paths(self):
        r = self.local_renderer
        r.env.supervisor_directory = r.format(r.env.supervisor_directory_template)
        r.env.celeryd_command = r.format(r.env.celeryd_command_template or r.env.celeryd_command)
        r.env.log_path = r.format(r.env.log_path_template)

    @task
    def create_supervisor_services(self, site):
        """
        This is called for each site to render a Celery config file.
        """

        self.vprint('create_supervisor_services:', site)

        self.set_site_specifics(site=site)

        r = self.local_renderer
        if self.verbose:
            print('r.env:')
            pprint(r.env, indent=4)

        self.vprint('r.env.has_worker:', r.env.has_worker)
        if not r.env.has_worker:
            self.vprint('skipping: no celery worker')
            return

        if self.name.lower() not in self.genv.services:
            self.vprint('skipping: celery not enabled')
            return

        hostname = self.current_hostname
        target_sites = self.genv.available_sites_by_host.get(hostname, None)
        if target_sites and site not in target_sites:
            self.vprint('skipping: site not supported on this server')
            return

        self.render_paths()

        conf_name = 'celery_%s.conf' % site
        ret = r.render_to_string('celery/celery_supervisor.template.conf')
        return conf_name, ret

    @task(post_callback=True)
    def register_callbacks(self):
        from burlap.supervisor import supervisor
        supervisor.register_callback(self.create_supervisor_services)

    @task(precursors=['packager'])
    def configure(self):
        pass

celery = CelerySatchel()
