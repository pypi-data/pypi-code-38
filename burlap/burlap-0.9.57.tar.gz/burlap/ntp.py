"""
NTP component.

Merely a stub to document which packages should be installed
if a system uses this component.

It should be otherwise maintenance-free and have required settings to configure.
"""
from __future__ import print_function

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class NTPClientSatchel(ServiceSatchel):

    name = 'ntpclient'

    @property
    def packager_system_packages(self):
        return {
            FEDORA: ['ntpdate', 'ntp'],
            UBUNTU: ['ntpdate', 'ntp'],
            (UBUNTU, '12.04'): ['ntpdate', 'ntp'],
            (UBUNTU, '14.04'): ['ntpdate', 'ntp'],
            (UBUNTU, '16.04'): ['ntpdate', 'ntp'],
            DEBIAN: ['ntpdate', 'ntp'],
        }

    def set_defaults(self):
        self.env.enabled = True
        self.env.default_server = 'time.nist.gov'
        self.env.service_commands = {
            START:{
                UBUNTU: 'service ntp start',
                DEBIAN: 'service ntp start',
            },
            STOP:{
                UBUNTU: 'service ntp stop',
                DEBIAN: 'service ntp stop',
            },
            DISABLE:{
                UBUNTU: 'update-rc.d -f ntp remove',
                DEBIAN: 'update-rc.d ntp disable',
            },
            ENABLE:{
                UBUNTU: 'update-rc.d ntp defaults',
                DEBIAN: 'update-rc.d ntp enable',
            },
            RESTART:{
                UBUNTU: 'service ntp restart',
                DEBIAN: 'service ntp restart',
            },
            STATUS:{
                UBUNTU: 'service ntp status',
                DEBIAN: 'service ntp status',
            },
        }

    @task
    def force_update(self):
        r = self.local_renderer
        r.sudo('service ntp stop')
        r.sudo('ntpdate {default_server}')
        r.sudo('service ntp start')

    @task(precursors=['packager', 'user'])
    def configure(self):
        if self.env.enabled:
            self.install_packages()
            self.enable()
            self.restart()
        else:
            self.disable()
            self.stop()

ntpclient = NTPClientSatchel()
