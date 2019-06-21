from __future__ import print_function

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class BluetoothSatchel(ServiceSatchel):

    name = 'bluetooth'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['bluetooth', 'bluez', 'python-bluez', 'bluez-firmware', 'blueman', 'pi-bluetooth'],
            DEBIAN: ['bluetooth', 'bluez', 'python-bluez', 'bluez-firmware', 'blueman', 'pi-bluetooth'],
        }

    def set_defaults(self):
        pass

    def scan(self):
        r = self.local_renderer
        #r.sudo('hciconfig hci0 piscan')
        r.run('hcitool scan')

    def add(self, name):
        r = self.local_renderer
        r.sudo('hciconfig hci0 name "%s"' % name)

    @task(precursors=['packager', 'user'])
    def configure(self):
        if self.env.enabled:
            self.install_packages()
            r = self.local_renderer
            #http://blog.davidvassallo.me/2014/05/11/android-linux-raspberry-pi-bluetooth-communication/
            r.sudo('echo "DisablePlugins = pnat" >> /etc/bluetooth/main.conf')

            #TODO:fix bluetooth.btcommon.BluetoothError: (2, 'No such file or directory')
            #https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=133263
            #sudo nano /lib/systemd/system/bluetooth.service
            #-ExecStart=/usr/lib/bluetooth/bluetoothd
            #+ExecStart=/usr/lib/bluetooth/bluetoothd -C
            #sudo sdptool add SP

            self.reboot()

BluetoothSatchel()
