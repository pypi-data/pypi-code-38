"""
Supervisor processes
====================

This module provides high-level tools for managing long-running
processes using `supervisord`_.

.. _supervisord: http://supervisord.org/

"""
from __future__ import print_function

import os
import time

import six

from burlap.constants import *
from burlap import ServiceSatchel
from burlap.decorators import task

# def reload_config():
#     """
#     Reload supervisor configuration.
#     """
#     run_as_root("supervisorctl reload")
#
#
# def update_config():
#     """
#     Reread and update supervisor job configurations.
#
#     Less heavy-handed than a full reload, as it doesn't restart the
#     backend supervisor process and all managed processes.
#     """
#     run_as_root("supervisorctl update")
#
#
# def process_status(name):
#     """
#     Get the status of a supervisor process.
#     """
#     with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
#         res = run_as_root("supervisorctl status {name}" % locals())
#         if res.startswith("No such process"):
#             return None
#         else:
#             return res.split()[1]
#
#
# def start_process(name):
#     """
#     Start a supervisor process
#     """
#     run_as_root("supervisorctl start {name}" % locals())
#
#
# def stop_process(name):
#     """
#     Stop a supervisor process
#     """
#     run_as_root("supervisorctl stop {name}" % locals())
#
#
# def restart_process(name):
#     """
#     Restart a supervisor process
#     """
#     run_as_root("supervisorctl restart {name}" % locals())


class SupervisorSatchel(ServiceSatchel):

    name = 'supervisor'

    ## Service options.

    #ignore_errors = True

    post_deploy_command = 'restart'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['supervisor'],
        }

    def set_defaults(self):

        self.env.manage_configs = True
        self.env.config_template = 'supervisor/supervisor_daemon.template2.config'
        self.env.config_path = '/etc/supervisor/supervisord.conf'
        #/etc/supervisor/conf.d/celery_
        self.env.conf_dir = '/etc/supervisor/conf.d'
        self.env.daemon_bin_path_template = '{pip_virtualenv_dir}/bin/supervisord'
        self.env.daemon_path = '/etc/init.d/supervisord'
        self.env.bin_path_template = '{pip_virtualenv_dir}/bin'
        self.env.daemon_pid = '/var/run/supervisord.pid'
        self.env.log_path = "/var/log/supervisord.log"
        self.env.supervisorctl_path_template = '{pip_virtualenv_dir}/bin/supervisorctl'
        self.env.kill_pattern = ''
        self.env.max_restart_wait_minutes = 5
        self.env.services_rendered = ''

        # If true, then all configuration files not explicitly managed by use will be deleted.
        self.env.purge_all_confs = True

        self.env.services = []

        # Functions that, when called, should return a supervisor service text
        # ready to be appended to supervisord.conf.
        # It will be called once for each site.
        self.genv._supervisor_create_service_callbacks = []

        self.env.service_commands = {
            START:{
                FEDORA: 'systemctl start supervisord.service',
                UBUNTU: 'service supervisor start',
            },
            STOP:{
                FEDORA: 'systemctl stop supervisor.service',
                UBUNTU: 'service supervisor stop',
            },
            DISABLE:{
                FEDORA: 'systemctl disable httpd.service',
                UBUNTU: 'chkconfig supervisor off',
            },
            ENABLE:{
                FEDORA: 'systemctl enable httpd.service',
                UBUNTU: 'chkconfig supervisor on',
            },
            RESTART:{
                FEDORA: 'systemctl restart supervisord.service',
                UBUNTU: 'service supervisor restart; sleep 5',
            },
            STATUS:{
                FEDORA: 'systemctl --no-pager status supervisord.service',
                (UBUNTU, '14.04'): 'service supervisor status',
                (UBUNTU, '16.04'): 'systemctl --no-pager status supervisor',
                UBUNTU: 'systemctl --no-pager status supervisor',
            },
        }

    def render_paths(self):
        r = self.local_renderer
        r.env.daemon_bin_path = r.format(r.env.daemon_bin_path_template)
        r.env.bin_path = r.format(r.env.bin_path_template)
        r.env.supervisorctl_path = r.format(r.env.supervisorctl_path_template)

    def register_callback(self, f):
        self.genv._supervisor_create_service_callbacks.append(f)

    @task
    def restart(self):
        """
        Supervisor can take a very long time to start and stop,
        so wait for it.
        """
        n = 60
        sleep_n = int(self.env.max_restart_wait_minutes/10.*60)
        for _ in six.moves.range(n):
            self.stop()
            if self.dryrun or not self.is_running():
                break
            print('Waiting for supervisor to stop (%i of %i)...' % (_, n))
            time.sleep(sleep_n)
        self.start()
        for _ in six.moves.range(n):
            if self.dryrun or self.is_running():
                return
            print('Waiting for supervisor to start (%i of %i)...' % (_, n))
            time.sleep(sleep_n)
        raise Exception('Failed to restart service %s!' % self.name)

    @task
    def reload(self):
        r = self.local_renderer
        r.sudo('supervisorctl reread')
        r.sudo('supervisorctl reload all')

    def record_manifest(self):
        """
        Called after a deployment to record any data necessary to detect changes
        for a future deployment.
        """
        data = super(SupervisorSatchel, self).record_manifest()

        # Celery deploys itself through supervisor, so monitor its changes too in Apache site configs.
        for site_name, site_data in self.genv.sites.items():
            if self.verbose:
                print(site_name, site_data)
            data['celery_has_worker_%s' % site_name] = site_data.get('celery_has_worker', False)

        data['configured'] = True

        # Generate services list.
        self.write_configs(upload=0)
        #data['services_rendered'] = ''

        return data

    @task
    def write_configs(self, site=None, upload=1):

        site = site or ALL

        verbose = self.verbose

        self.render_paths()

        supervisor_services = []
        process_groups = []

        #TODO:check available_sites_by_host and remove dead?
        for _site, site_data in self.iter_sites(site=site, renderer=self.render_paths):
            if verbose:
                print('write_configs.site:', _site)
            for cb in self.genv._supervisor_create_service_callbacks:
                ret = cb(site=_site)
                if isinstance(ret, six.string_types):
                    supervisor_services.append(ret)
                elif isinstance(ret, tuple):
                    assert len(ret) == 2
                    conf_name, conf_content = ret
                    if verbose:
                        print('conf_name:', conf_name)
                        print('conf_content:', conf_content)
                    remote_fn = os.path.join(self.env.conf_dir, conf_name)
                    if int(upload):
                        local_fn = self.write_to_file(conf_content)
                        self.put_or_dryrun(local_path=local_fn, remote_path=remote_fn, use_sudo=True)

        self.env.services_rendered = '\n'.join(supervisor_services)

        if int(upload):
            fn = self.render_to_file(self.env.config_template)
            self.put_or_dryrun(local_path=fn, remote_path=self.env.config_path, use_sudo=True)

    def deploy_services(self, site=None):
        """
        Collects the configurations for all registered services and writes
        the appropriate supervisord.conf file.
        """

        verbose = self.verbose

        r = self.local_renderer
        if not r.env.manage_configs:
            return
#
#         target_sites = self.genv.available_sites_by_host.get(hostname, None)

        self.render_paths()

        supervisor_services = []

        if r.env.purge_all_confs:
            r.sudo('rm -Rf /etc/supervisor/conf.d/*')

        #TODO:check available_sites_by_host and remove dead?
        self.write_configs(site=site)
        for _site, site_data in self.iter_sites(site=site, renderer=self.render_paths):
            if verbose:
                print('deploy_services.site:', _site)

            # Only load site configurations that are allowed for this host.
#             if target_sites is not None:
#                 assert isinstance(target_sites, (tuple, list))
#                 if site not in target_sites:
#                     continue

            for cb in self.genv._supervisor_create_service_callbacks:
                if self.verbose:
                    print('cb:', cb)
                ret = cb(site=_site)
                if self.verbose:
                    print('ret:', ret)
                if isinstance(ret, six.string_types):
                    supervisor_services.append(ret)
                elif isinstance(ret, tuple):
                    assert len(ret) == 2
                    conf_name, conf_content = ret
                    if self.dryrun:
                        print('supervisor conf filename:', conf_name)
                        print(conf_content)
                    self.write_to_file(conf_content)

        self.env.services_rendered = '\n'.join(supervisor_services)

        fn = self.render_to_file(self.env.config_template)
        r.put(local_path=fn, remote_path=self.env.config_path, use_sudo=True)

        # We use supervisorctl to configure supervisor, but this will throw a uselessly vague
        # error message is supervisor isn't running.
        if not self.is_running():
            self.start()

        # Reload config and then add and remove as necessary (restarts programs)
        r.sudo('supervisorctl update')

    @task(precursors=['packager', 'user', 'rabbitmq'])
    def configure(self, **kwargs):
        kwargs.setdefault('site', ALL)

        self.deploy_services(**kwargs)

supervisor = SupervisorSatchel()
