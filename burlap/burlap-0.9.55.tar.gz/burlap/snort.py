from __future__ import print_function

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class SnortSatchel(ServiceSatchel):

    name = 'snort'

    #def set_defaults(self):
        #super(SnortSatchel, self).set_defaults()

    @property
    def packager_system_packages(self):
        return {
            DEBIAN: [
                'snort',
            ],
            UBUNTU: [
                'snort',
            ],
        }

    @task(precursors=['packager'])
    def configure(self):
        pass

snort = SnortSatchel()
