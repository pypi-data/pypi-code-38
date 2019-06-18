"""
RabbitMQ
============

https://www.rabbitmq.com/

"""
from __future__ import print_function

import sys

from fabric.api import settings

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

DJANGO = 'django'
LOCAL = 'local'

class RabbitMQSatchel(ServiceSatchel):

    name = 'rabbitmq'

    ## Service options.

    ignore_errors = True

    @property
    def packager_system_packages(self):
        return {
            FEDORA: ['rabbitmq-server'],
            (UBUNTU, '12.04'): ['rabbitmq-server'],
            (UBUNTU, '14.04'): ['rabbitmq-server'],
            (UBUNTU, '16.04'): ['rabbitmq-server'],
        }

    def set_defaults(self):
        self.env.rabbitmq_host = "localhost"
        self.env.vhost = "/"
        self.env.erlang_cookie = ''
        self.env.nodename = "rabbit"
        self.env.user = "guest" # DEPRECATED
        self.env.password = "guest" # DEPRECATED
        self.env.node_ip_address = ''
        self.env.port = 5672
        self.env.erl_args = ""
        self.env.cluster = "no"
        self.env.cluster_config = "/etc/rabbitmq/rabbitmq_cluster.config"
        self.env.logdir = "/var/log/rabbitmq"
        self.env.mnesiadir = "/var/lib/rabbitmq/mnesia"
        self.env.start_args = ""
        self.env.erlang_cookie_template = ''
        self.env.ignore_service_errors = 0
        self.env.management_enabled = False
        self.env.loopback_users = False
        self.env.admin_username = 'admin'
        self.env.user_lookup_method = None # LOCAL|DJANGO
        self.env.users_vhosts = [] # [(user, password, vhost)]

        self.env.auto_purge_mnesia_enabled = False
        self.env.auto_purge_mnesia_user = 'root'
        self.env.auto_purge_mnesia_command_template = 'rabbitmq/purge_mnesia.sh.template'
        self.env.auto_purge_mnesia_command_path = '/usr/local/bin/purge_mnesia.sh'
        self.env.auto_purge_mnesia_crontab_template = 'rabbitmq/etc_crond_purge_mnesia.template'
        self.env.auto_purge_mnesia_crontab_path = '/etc/cron.d/purge_mnesia'
        self.env.auto_purge_mnesia_cron_schedule = '0 0 * * SAT' # Every Saturday at midnight.
        self.env.auto_purge_mnesia_post_script = None

        # If true, enables a third-party reposistory to install the most recent version.
        self.env.bleeding = False

        self.env.service_commands = {
            START:{
                FEDORA: 'systemctl start rabbitmq-server.service',
                UBUNTU: 'service rabbitmq-server start',
            },
            STOP:{
                FEDORA: 'systemctl stop rabbitmq-server.service',
                UBUNTU: 'service rabbitmq-server stop',
            },
            DISABLE:{
                FEDORA: 'systemctl disable rabbitmq-server.service',
                UBUNTU: 'chkconfig rabbitmq-server off',
            },
            ENABLE:{
                FEDORA: 'systemctl enable rabbitmq-server.service',
                UBUNTU: 'chkconfig rabbitmq-server on',
            },
            RESTART:{
                FEDORA: 'systemctl restart rabbitmq-server.service',
                UBUNTU: 'service rabbitmq-server restart; sleep 5',
            },
            STATUS:{
                FEDORA: 'systemctl status rabbitmq-server.service',
                UBUNTU: 'service rabbitmq-server status | cat',
                (UBUNTU, '14.04'): 'service rabbitmq-server status',
                (UBUNTU, '16.04'): 'service rabbitmq-server status | cat',
            },
        }

    @task
    def configure_bleeding(self):
        """
        Enables the repository for a most current version on Debian systems.

            https://www.rabbitmq.com/install-debian.html
        """
        lm = self.last_manifest
        r = self.local_renderer
        if self.env.bleeding and not lm.bleeding:
            # Install.
            r.append(
                text='deb http://www.rabbitmq.com/debian/ testing main',
                filename='/etc/apt/sources.list.d/rabbitmq.list',
                use_sudo=True)
            r.sudo('cd /tmp; wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | sudo apt-key add -')
            r.sudo('apt-get update')

        elif not self.env.bleeding and lm.bleeding:
            # Uninstall.
            r.sudo('rm -f /etc/apt/sources.list.d/rabbitmq.list')
            r.sudo('apt-get update')

    def render_paths(self):
        r = self.local_renderer
        if self.env.erlang_cookie_template:
            r.env.erlang_cookie = r.format(self.env.erlang_cookie_template)

    @task
    def list_vhosts(self):
        """
        Displays a list of configured RabbitMQ vhosts.
        """
        self.sudo('rabbitmqctl list_vhosts')

    @task
    def list_users(self):
        """
        Displays a list of configured RabbitMQ users.
        """
        self.sudo('rabbitmqctl list_users')

    @task
    def list_queues(self):
        self.sudo('rabbitmqctl list_queues')

    @task
    def create_user(self, username, password):
        r = self.local_renderer
        r.env._user = username
        r.env._password = password
        with self.settings(warn_only=True):
            r.sudo('rabbitmqctl add_user {_user} {_password}')

    @task
    def force_stop_and_purge(self):
        """
        Forcibly kills Rabbit and purges all its queues.

        For emergency use when the server becomes unresponsive, even to service stop calls.

        If this also fails to correct the performance issues, the server may have to be completely
        reinstalled.
        """
        r = self.local_renderer
        self.stop()
        with settings(warn_only=True):
            r.sudo('killall rabbitmq-server')
        with settings(warn_only=True):
            r.sudo('killall beam.smp')
        #TODO:explicitly delete all subfolders, star-delete doesn't work
        r.sudo('rm -Rf /var/lib/rabbitmq/mnesia/*')

    @task
    def add_admin_user(self):
        r = self.local_renderer
        with self.settings(warn_only=True):
            r.sudo('rabbitmqctl add_user {admin_username} {admin_password}')
        r.sudo('rabbitmqctl set_user_tags {admin_username} administrator')
        r.sudo('rabbitmqctl set_permissions -p / {admin_username} ".*" ".*" ".*"')

    @task
    def enable_management_interface(self):
        r = self.local_renderer
        r.sudo('rabbitmq-plugins enable rabbitmq_management')
        r.sudo('service rabbitmq-server restart; sleep 3')
        self.add_admin_user()
        print('You should now be able to access the RabbitMQ web console from:')
        print('\n    http://%s:15672/' % self.genv.host_string)

    @task
    def set_loopback_users(self):
        # This allows guest to login through the management interface.
        self.sudo('touch /etc/rabbitmq/rabbitmq.config')
        #self.sudo("echo '[{rabbit, [{loopback_users, []}]}].' >> /etc/rabbitmq/rabbitmq.config")
        self.append(filename='/etc/rabbitmq/rabbitmq.config', text='[{rabbit, [{loopback_users, []}]}].', use_sudo=True)
        with self.settings(warn_only=True):
            self.sudo('service rabbitmq-server restart; sleep 3;')

    def get_user_vhosts(self, site=None):
        params = set() # [(user, password, vhost)]
        site = site or ALL
        if self.verbose:
            print('Using looking method:', self.env.user_lookup_method)
        if self.env.user_lookup_method == DJANGO:
            # Retrieve user settings from one or more assoicated Django sites.
            dj = self.get_satchel('dj')
            for _site, site_data in self.iter_sites(site=site, renderer=self.render_paths, no_secure=True):
                if self.verbose:
                    print('!'*80, file=sys.stderr)
                    print('site:', _site, file=sys.stderr)

                # Only load site configurations that are allowed for this host.
    #             if target_sites is not None:
    #                 assert isinstance(target_sites, (tuple, list))
    #                 if site not in target_sites:
    #                     continue

                _settings = dj.get_settings(site=_site)
                if not _settings:
                    continue

                if hasattr(_settings, 'BROKER_USER') and hasattr(_settings, 'BROKER_VHOST'):
                    if self.verbose:
                        print('RabbitMQ:', _settings.BROKER_USER, _settings.BROKER_VHOST)
                    params.add((_settings.BROKER_USER, _settings.BROKER_PASSWORD, _settings.BROKER_VHOST))

        elif self.env.user_lookup_method == LOCAL:
            # Retrieve user settings from our local settings.
            params.update(tuple(_) for _ in self.env.users_vhosts)

        elif self.env.user_lookup_method:
            raise NotImplementedError('Unknown user lookup method: %s' % self.env.user_lookup_method)

        return params

    @task
    def install_purge_script(self):
        r = self.local_renderer

        with self.capture_bash() as capture:
            self._configure_users()

        r.env.user_script = capture.stdout.getvalue()

        # Install script to perform the actual check.
        self.install_script(
            local_path=r.env.auto_purge_mnesia_command_template,
            remote_path=r.env.auto_purge_mnesia_command_path,
            render=True,
            extra=r.collect_genv())
        r.sudo('chown root:root {auto_purge_mnesia_command_path}')

        # Install crontab to schedule running the script.
        self.install_script(
            local_path=r.env.auto_purge_mnesia_crontab_template,
            remote_path=r.env.auto_purge_mnesia_crontab_path,
            render=True,
            extra=r.collect_genv())
        r.sudo('chown root:root {auto_purge_mnesia_crontab_path}')
        r.sudo('chmod 600 {auto_purge_mnesia_crontab_path}')
        r.sudo('service cron restart')

    @task
    def purge_mnesia(self):
        """
        Deletes all persistent data on the server.
        """
        self.install_purge_script()
        r = self.local_renderer
        r.sudo('{auto_purge_mnesia_command_path}')

    @task
    def uninstall_purge_script(self):
        r = self.local_renderer
        r.sudo('rm -f {auto_purge_mnesia_command_path}')
        r.sudo('rm -f {auto_purge_mnesia_crontab_path}')
        r.sudo('service cron restart')

    def _configure_users(self, site=None, full=0, only_data=0):
        """
        Installs and configures RabbitMQ.
        """

        site = site or ALL

        full = int(full)

        if full and not only_data:
            packager = self.get_satchel('packager')
            packager.install_required(type=SYSTEM, service=self.name)

        r = self.local_renderer

        params = self.get_user_vhosts(site=site) # [(user, password, vhost)]

        with settings(warn_only=True):
            self.add_admin_user()

        params = sorted(list(params))
        if not only_data:
            for user, password, vhost in params:
                r.env.broker_user = user
                r.env.broker_password = password
                r.env.broker_vhost = vhost
                with settings(warn_only=True):
                    r.sudo('rabbitmqctl add_user {broker_user} {broker_password}')
                    r.sudo('rabbitmqctl add_vhost {broker_vhost}')
                    r.sudo('rabbitmqctl set_permissions -p {broker_vhost} {broker_user} ".*" ".*" ".*"')
                    r.sudo('rabbitmqctl set_permissions -p {broker_vhost} {admin_username} ".*" ".*" ".*"')

        return params

    def record_manifest(self):
        """
        Returns a dictionary representing a serialized state of the service.
        """
        data = super(RabbitMQSatchel, self).record_manifest()
        params = sorted(list(self.get_user_vhosts())) # [(user, password, vhost)]
        data['rabbitmq_all_site_vhosts'] = params
        data['sites'] = list(self.genv.sites or [])
        return data

    @task(precursors=['packager', 'user'])
    def configure(self, site=None, **kwargs):
        lm = self.last_manifest

        self.configure_bleeding()

        if self.env.auto_purge_mnesia_enabled:
            self.install_purge_script()
        elif lm.auto_purge_mnesia_enabled:
            self.uninstall_purge_script()

        if self.env.management_enabled != lm.management_enabled:
            self.enable_management_interface()

        if self.env.loopback_users != lm.loopback_users:
            self.set_loopback_users()

        return self._configure_users(**kwargs)

rabbitmq = RabbitMQSatchel()
