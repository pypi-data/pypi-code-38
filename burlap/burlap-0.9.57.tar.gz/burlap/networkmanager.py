from __future__ import print_function

from fabric.api import settings

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class NetworkManagerSatchel(ServiceSatchel):
    """
    Configures Network Manager for automatically controlling network interfaces.

    https://fedoraproject.org/wiki/Networking/CLI#Wifi
    """

    name = 'nm'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['network-manager', 'cron'],
            DEBIAN: ['network-manager', 'cron'],
        }

    templates = (
        'check_networkmanager.sh',
        'etc_crond_check_networkmanager',
    )

    def set_defaults(self):
        self.env.check_enabled = False

        self.env.service_commands = {
            START:{
                UBUNTU: 'service network-manager start',
                DEBIAN: 'service network-manager start',
            },
            STOP:{
                UBUNTU: 'service network-manager stop',
                DEBIAN: 'service network-manager stop',
            },
            DISABLE:{
                DEBIAN: 'update-rc.d network-manager disable',
                #UBUNTU: 'chkconfig network-manager off',
                UBUNTU: 'systemctl disable network-manager.service',
                (UBUNTU, '14.04'): 'echo "manual" | sudo tee /etc/init/network-manager.override',
            },
            ENABLE:{
                DEBIAN: 'update-rc.d network-manager enable',
                #UBUNTU: 'chkconfig network-manager on',
                UBUNTU: 'systemctl enable network-manager.service',
                (UBUNTU, '14.04'): 'rm /etc/init/network-manager.override || true',
            },
            RESTART:{
                UBUNTU: 'service network-manager restart',
                DEBIAN: 'service network-manager restart',
            },
            STATUS:{
                UBUNTU: 'service network-manager status',
                DEBIAN: 'service network-manager status',
            },
        }

        self.env.check_script_path = '/usr/local/bin/check_networkmanager.sh'
        self.env.cron_script_path = '/etc/cron.d/check_networkmanager'
        self.env.check_script_template = '%s/check_networkmanager.sh' % self.name
        self.env.cron_perms = '600'

        self.env.connections = {} # {ssid: passphrase}

    @task
    def add_wifi_connection(self, ssid, passphrase=None):
        r = self.local_renderer
        r.env.ssid = ssid = ssid
        r.env.passphrase = passphrase
        r.sudo('nmcli device wifi connect "{ssid}" password "{passphrase}"')

    @task
    def remove_connection(self, ssid):
        r = self.local_renderer
        r.env.ssid = ssid = ssid
        #r.sudo("nmcli connection delete `nmcli --fields NAME,UUID con list | grep -i {ssid} | awk '{print $2}'`")
        r.sudo("nmcli connection delete id {ssid}")

    @task
    def dev_status(self):
        r = self.local_renderer
        r.sudo('nmcli device status')

    @task
    def dev_wifi_list(self):
        r = self.local_renderer
        r.sudo('nmcli device wifi list')

    @task
    def configure_checker(self):
        r = self.local_renderer
        if r.env.check_enabled:
            # Installs a crontab to check Network-Manager every ten minutes
            # and restart it if theres' no Internet connection.
            self.install_script(
                local_path=r.env.check_script_template,
                remote_path=self.lenv.check_script_path)
            remote_path = r.put(
                local_path=self.find_template('%s/etc_crond_check_networkmanager' % self.name),
                remote_path=self.env.cron_script_path, use_sudo=True)[0]
            r.sudo('chown root:root %s' % remote_path)#env.put_remote_path)
            # Must be 600, otherwise gives INSECURE MODE error.
            # http://unix.stackexchange.com/questions/91202/cron-does-not-print-to-syslog
            r.sudo('chmod %s %s' % (self.env.cron_perms, remote_path))#env.put_remote_path)
            r.sudo('service cron restart')
        else:
            r.sudo('rm -f {cron_script_path}'.format(**self.lenv))
            r.sudo('service cron restart')

    @task(precursors=['packager', 'user', 'cron'])
    def configure(self):

        r = self.local_renderer

        lm = self.last_manifest
        lm_connections = lm.connections or {}

        if r.env.enabled:

            # Clear the /etc/network/interfaces so NM will control all interfaces.
            if not self.files.exists('/etc/network/interfaces'):
                r.sudo('mv /etc/network/interfaces /etc/network/interfaces.bak')
            r.sudo('rm -f /etc/network/interfaces')
            r.sudo('touch /etc/network/interfaces')
            r.sudo('echo -e "auto lo\\niface lo inet loopback" > /etc/network/interfaces')

            self.enable()
            self.restart()
        else:
            self.disable()
            self.stop()

        self.configure_checker()

        # When enabling wifi for the first time, a reboot is required.
        if not lm_connections and r.env.connections and r.env.enabled:
            r.reboot(wait=300, timeout=60)

        # Remove deleted connections.
        # Note, this will fail if the host's connection is currently using the connection.
        for old_ssid in lm_connections:
            if old_ssid not in r.env.connections:
                self.remove_connection(old_ssid)

        # Add or update connections.
        for ssid, passphrase in r.env.connections.items():

            # Remove old connection.
            if ssid in lm_connections and lm_connections[ssid] != passphrase:
                self.remove_connection(ssid)

            # Add new connection.
            with settings(warn_only=True):
                # This may through an error code, but on reboot, the connection will appear and be connected.
                self.add_wifi_connection(ssid, passphrase)

nm = NetworkManagerSatchel()
