"""
Wrapper around the Motion service.

http://www.lavrsen.dk/foswiki/bin/view/Motion/WebHome
"""
from __future__ import print_function

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class MotionSatchel(ServiceSatchel):

    name = 'motion'

    @property
    def packager_system_packages(self):
        return {
            FEDORA: ['motion'],
            UBUNTU: ['motion'],
        }

    def set_defaults(self):
        self.env.notify_enabled = False
        self.env.service_commands = {
            START:{
                FEDORA: 'systemctl start motion.service',
                UBUNTU: 'service motion start',
            },
            STOP:{
                FEDORA: 'systemctl stop motion.service',
                UBUNTU: 'service motion stop',
            },
            DISABLE:{
                FEDORA: 'systemctl disable motion.service',
                UBUNTU: 'chkconfig motion off',
            },
            ENABLE:{
                FEDORA: 'systemctl enable motion.service',
                UBUNTU: 'chkconfig motion on',
            },
            RESTART:{
                FEDORA: 'systemctl restart motion.service',
                UBUNTU: 'service motion restart; sleep 5',
            },
            STATUS:{
                FEDORA: 'systemctl status motion.service',
                UBUNTU: 'service motion status',
            },
        }

    @task(precursors=['packager', 'user'])
    def configure(self):
        pass

motion = MotionSatchel()
