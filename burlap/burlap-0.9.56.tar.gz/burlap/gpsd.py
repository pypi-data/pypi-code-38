
from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class GPSDSatchel(ServiceSatchel):

    name = 'gpsd'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['gpsd', 'gpsd-clients', 'python-gps', 'ntp'],
            DEBIAN: ['gpsd', 'gpsd-clients', 'python-gps', 'ntp'],
        }

    def set_defaults(self):
        self.env.service_commands = {
            START:{
                UBUNTU: 'service gpsd start',
                DEBIAN: 'service gpsd start',
            },
            STOP:{
                UBUNTU: 'service gpsd stop',
                DEBIAN: 'service gpsd stop',
            },
            DISABLE:{
                UBUNTU: 'chkconfig gpsd off',
                (UBUNTU, '14.04'): 'update-rc.d -f gpsd remove',
                DEBIAN: 'update-rc.d gpsd disable',
            },
            ENABLE:{
                UBUNTU: 'chkconfig gpsd on',
                (UBUNTU, '14.04'): 'update-rc.d gpsd defaults',
                DEBIAN: 'update-rc.d gpsd enable',
            },
            RELOAD:{
                UBUNTU: 'service gpsd reload',
                DEBIAN: 'service gpsd reload',
            },
            RESTART:{
                UBUNTU: 'service gpsd restart; sleep 3',
                DEBIAN: 'service gpsd restart; sleep 3',
            },
        }

    @task
    def launch(self):
        self.run('gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock')

    @task(precursors=['packager', 'user'])
    def configure(self):
        self.install_packages()
    configure.is_deployer = True

gpsd = GPSDSatchel()
