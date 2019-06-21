from __future__ import print_function

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

STATIC = 'static'
DYNAMIC = 'dynamic'

class IPSatchel(ServiceSatchel):

    name = 'ip'

    post_deploy_command = None

    def set_defaults(self):
        self.env.type = DYNAMIC # STATIC
        self.env.interface = 'eth0'
        self.env.address = None
        self.env.network = '192.168.0.0'
        self.env.netmask = '255.255.255.0'
        self.env.broadcast = '10.157.10.255'
        self.env.gateway = '10.157.10.1'
        self.env.dns_nameservers = None
        self.env.interfaces_fn = '/etc/network/interfaces'
        #env.network_restart_command = '/etc/init.d/networking restart'
        self.env.daemon_name = 'networking'
        self.env.service_commands = {
            START:{
                UBUNTU: 'service %s start' % self.env.daemon_name,
            },
            STOP:{
                UBUNTU: 'service %s stop' % self.env.daemon_name,
            },
            DISABLE:{
                UBUNTU: 'chkconfig %s off' % self.env.daemon_name,
            },
            ENABLE:{
                UBUNTU: 'chkconfig %s on' % self.env.daemon_name,
            },
            RESTART:{
                UBUNTU: 'service %s restart' % self.env.daemon_name,
            },
            STATUS:{
                UBUNTU: 'service %s status' % self.env.daemon_name,
            },
        }

    @task
    def static(self):
        """
        Configures the server to use a static IP.
        """
        fn = self.render_to_file('ip/ip_interfaces_static.template')
        r = self.local_renderer
        r.put(local_path=fn, remote_path=r.env.interfaces_fn, use_sudo=True)

    @task
    def dynamic(self):
        """
        Configures the server to use a static IP.
        """
        fn = self.render_to_file('ip/ip_interfaces_dynamic.template')
        r = self.local_renderer
        r.put(local_path=fn, remote_path=r.env.interfaces_fn, use_sudo=True)

    @task(precursors=['packager', 'user', 'hostname'])
    def configure(self):
        if self.env.type == STATIC:
            self.static()
        elif self.env.type == DYNAMIC:
            self.dynamic()
        else:
            raise NotImplementedError('Unknown type: %s' % self.env.type)
        self.restart()

ip = IPSatchel()
