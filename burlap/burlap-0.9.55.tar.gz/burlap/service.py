from __future__ import print_function

import sys
import traceback

from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task

# from fabric.api import (
#     env,
#     settings,
#     hide,
# )


# from burlap import systemd
# from burlap.system import using_systemd, distrib_family
# from burlap.utils import run_as_root

from burlap import common
# from burlap.common import (
#     get_dryrun,
# )
# from burlap.decorators import task_or_dryrun

#run_as_root = sudo_or_dryrun

# @task
# def is_running(service):
#     """
#     Check if a service is running.
#
#     ::
#
#         import burlap
#
#         if burlap.service.is_running('foo'):
#             print("Service foo is running!")
#     """
#
#     #DEPRECATED?
#     service = service.strip().lower()
#     _ran = False
#     for _service in self.genv.services:
#         _service = _service.strip().upper()
#         if service and _service.lower() != service:
#             continue
#         srv = common.services.get(_service)
#         if srv:
#             _ran = True
#             #print('%s.is_running: %s' % (service, srv.is_running()))
#             return srv.is_running()
#
#     with settings(hide('running', 'stdout', 'stderr', 'warnings'),
#                   warn_only=True):
#         if using_systemd():
#             return systemd.is_running(service)
#         else:
#             if distrib_family() != "gentoo":
#                 test_upstart = run_as_root('test -f /etc/init/%s.conf' %
#                                            service)
#                 status = _run_service(service, 'status')
#                 if test_upstart.succeeded:
#                     return 'running' in status
#                 else:
#                     return status.succeeded
#             else:
#                 # gentoo
#                 status = _run_service(service, 'status')
#                 return ' started' in status
#
#
# def start(service):
#     """
#     Start a service.
#
#     ::
#
#         import burlap
#
#         # Start service if it is not running
#         if not burlap.service.is_running('foo'):
#             burlap.service.start('foo')
#     """
#
#     with settings(warn_only=True):
#         _run_service(service, 'start')
#
#     # Sometimes race conditions result in us trying to start a service that wasn't running
#     # when we checked, but started running by the time we tried to start.
#     # So ignore the error that the service we're trying to start has started
#     # and then do a separate check to confirm the service has started.
#     assert is_running(service), 'Service %s failed to start.' % service
#
#
# @task
# def stop(service=''):
#     """
#     Stop a service.
#
#     ::
#
#         import burlap
#
#         # Stop service if it is running
#         if burlap.service.is_running('foo'):
#             burlap.service.stop('foo')
#     """
#
#     ran = False
#     service = service.strip().lower()
#     for _service in self.genv.services:
#         _service = _service.strip().upper()
#         if service and _service.lower() != service:
#             continue
#         funcs = common.service_stoppers.get(_service)
#         if funcs:
#             print('Restarting service %s...' % (_service,))
#             for func in funcs:
#                 func()
#                 ran = True
#
#     if not ran and not get_dryrun() and service:
#         _run_service(service, 'stop')
#
#
# @task
# def restart(service=''):
#     """
#     Restart a service.
#
#     ::
#
#         import burlap
#
#         # Start service, or restart it if it is already running
#         if burlap.service.is_running('foo'):
#             burlap.service.restart('foo')
#         else:
#             burlap.service.start('foo')
#     """
#
#     service = service.strip().lower()
#     _ran = False
#
#     for _service in self.genv.services:
#         _service = _service.strip().upper()
#
#         if service and _service.lower() != service:
#             continue
#
#         srv = common.services.get(_service)
#         if srv:
#             srv.restart()
#             _ran = True
#             continue
#
#         funcs = common.service_restarters.get(_service)
#         if funcs:
#             print('Restarting service %s...' % (_service,))
#             for func in funcs:
#                 if not self.dryrun:
#                     func()
#                     _ran = True
#
#     if not get_dryrun() and not _ran and service:
#         _run_service(service, 'restart')
#
#
# def reload(service): # pylint: disable=redefined-builtin
#     """
#     Reload a service.
#
#     ::
#
#         import burlap
#
#         # Reload service
#         burlap.service.reload('foo')
#
#     .. warning::
#
#         The service needs to support the ``reload`` operation.
#     """
#     _run_service(service, 'reload')
#
#
# def force_reload(service):
#     """
#     Force reload a service.
#
#     ::
#
#         import burlap
#
#         # Force reload service
#         burlap.service.force_reload('foo')
#
#     .. warning::
#
#         The service needs to support the ``force-reload`` operation.
#     """
#     _run_service(service, 'force-reload')
#
#
# def _run_service(service, action):
#     """
#     Compatibility layer for distros that use ``service`` and those that don't.
#     """
#     if distrib_family() != "gentoo":
#         status = run_as_root('service %(service)s %(action)s' % locals(),
#                              pty=False)
#     else:
#         # gentoo
#         status = run_as_root('/etc/init.d/%(service)s %(action)s' % locals(),
#                              pty=False)
#     return status

class ServiceManagementSatchel(Satchel):

    name = 'service'

    @task
    def pre_deploy(self):
        """
        Runs methods services have requested be run before each deployment.
        """
        for service in self.genv.services:
            service = service.strip().upper()
            funcs = common.service_pre_deployers.get(service)
            if funcs:
                print('Running pre-deployments for service %s...' % (service,))
                for func in funcs:
                    func()

    @task
    def deploy(self):
        """
        Applies routine, typically application-level changes to the service.
        """
        for service in self.genv.services:
            service = service.strip().upper()
            funcs = common.service_deployers.get(service)
            if funcs:
                print('Deploying service %s...' % (service,))
                for func in funcs:
                    if not self.dryrun:
                        func()

    @task
    def post_deploy(self):
        """
        Runs methods services have requested be run before after deployment.
        """
        for service in self.genv.services:
            service = service.strip().upper()
            self.vprint('post_deploy:', service)
            funcs = common.service_post_deployers.get(service)
            if funcs:
                self.vprint('Running post-deployments for service %s...' % (service,))
                for func in funcs:
                    try:
                        func()
                    except Exception as e:
                        print('Post deployment error: %s' % e, file=sys.stderr)
                        print(traceback.format_exc(), file=sys.stderr)

    def is_selected(self, name):
        name = name.strip().upper()
        for service in self.genv.services:
            if service.strip().upper() == name:
                return True
        return False

    @task
    def pre_db_dump(self):
        """
        Runs methods services that have requested to be run before each
        database dump.
        """
        for service in self.genv.services:
            service = service.strip().upper()
            funcs = common.service_pre_db_dumpers.get(service)
            if funcs:
                print('Running pre-database dump for service %s...' % (service,))
                for func in funcs:
                    func()

    @task
    def post_db_dump(self):
        """
        Runs methods services that have requested to be run before each
        database dump.
        """
        for service in self.genv.services:
            service = service.strip().upper()
            funcs = common.service_post_db_dumpers.get(service)
            if funcs:
                print('Running post-database dump for service %s...' % (service,))
                for func in funcs:
                    func()


    @task
    def refresh(self):
        self.configure()
        self.deploy()
        self.post_deploy()

    @task
    def configure(self):
        """
        Applies one-time settings changes to the host, usually to initialize the service.
        """
        print('env.services:', self.genv.services)
        for service in list(self.genv.services):
            service = service.strip().upper()
            funcs = common.service_configurators.get(service, [])
            if funcs:
                print('!'*80)
                print('Configuring service %s...' % (service,))
                for func in funcs:
                    print('Function:', func)
                    if not self.dryrun:
                        func()

service = ServiceManagementSatchel()
