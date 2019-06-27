from __future__ import print_function

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class MemcachedSatchel(ServiceSatchel):

    name = 'memcached'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['memcached'],
        }

    def set_defaults(self):
        super(MemcachedSatchel, self).set_defaults()
        self.env.service_commands = {
            START:{
                FEDORA: 'systemctl start memcached',
                UBUNTU: 'service memcached start',
            },
            STOP:{
                FEDORA: 'systemctl stop memcached',
                UBUNTU: 'service memcached stop',
            },
            STATUS:{
                FEDORA: 'systemctl status memcached',
                UBUNTU: 'service memcached status',
            },
            DISABLE:{
                FEDORA: 'systemctl disable memcached',
                UBUNTU: 'chkconfig memcached off',
            },
            ENABLE:{
                FEDORA: 'systemctl enable memcached',
                UBUNTU: 'chkconfig memcached on',
            },
            RELOAD:{
                FEDORA: 'systemctl reload memcached',
                UBUNTU: 'service memcached reload',
            },
            RESTART:{
                FEDORA: 'systemctl restart memcached',
                #UBUNTU: 'service memcached restart',
                # Note, the sleep 5 is necessary because the stop/start appears to
                # happen in the background but gets aborted if Fabric exits before
                # it completes.
                UBUNTU: 'service memcached restart; sleep 3',
            },
        }

    @task(precursors=['packager'])
    def configure(self):
        pass
