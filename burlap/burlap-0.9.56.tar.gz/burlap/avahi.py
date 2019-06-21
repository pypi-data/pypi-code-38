from __future__ import print_function

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class AvahiSatchel(ServiceSatchel):

    name = 'avahi'

    def set_defaults(self):

        self.env.daemon_name = 'avahi-daemon'

        self.env.service_commands = {
            START:{
                UBUNTU: 'service %s start' % self.env.daemon_name,
                DEBIAN: 'service %s start' % self.env.daemon_name,
            },
            STOP:{
                UBUNTU: 'service %s stop' % self.env.daemon_name,
                DEBIAN: 'service %s stop' % self.env.daemon_name,
            },
            DISABLE:{
                #UBUNTU: 'chkconfig %s off' % self.env.daemon_name,
                UBUNTU: 'systemctl disable %s.service' % self.env.daemon_name,
                DEBIAN: 'update-rc.d %s disable' % self.env.daemon_name,
            },
            ENABLE:{
                #UBUNTU: 'chkconfig %s on' % self.env.daemon_name,
                UBUNTU: 'systemctl enable %s.service' % self.env.daemon_name,
                DEBIAN: 'update-rc.d %s enable' % self.env.daemon_name,
            },
            RESTART:{
                UBUNTU: 'service %s restart' % self.env.daemon_name,
                DEBIAN: 'service %s restart' % self.env.daemon_name,
            },
            STATUS:{
                UBUNTU: 'service %s status' % self.env.daemon_name,
                DEBIAN: 'service %s status' % self.env.daemon_name,
            },
        }

    @property
    def packager_system_packages(self):
        return {
            DEBIAN: ['avahi-daemon'],
            UBUNTU: ['avahi-daemon'],
        }

    @task(precursors=['packager', 'user'])
    def configure(self):
        if self.env.enabled:
            self.enable()
            self.restart()
        else:
            self.disable()
            self.stop()

AvahiSatchel()
