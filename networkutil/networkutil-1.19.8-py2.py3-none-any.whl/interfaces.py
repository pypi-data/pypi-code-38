# encoding: utf-8

import sys
import netifaces
import subprocess

# TODO: move these into a separate module as they are generally useful!:
WINDOWS = True if sys.platform in [u'win32', u'cygwin'] else False
MACOS = True if sys.platform == u'darwin' else False
LINUX = True if sys.platform in [u'linux', u'linux2'] else False


def get_interface_names():

    interface_names = {}

    if MACOS:
        ifs_hardware = subprocess.check_output(['networksetup', '-listallhardwareports']).splitlines()

        # Check for VLAN configurations section
        idx = ifs_hardware.index(u'VLAN Configurations')

        # Split into hardware & VLAN interfaces
        interfaces = ifs_hardware[:idx]
        vlans = ifs_hardware[idx + 2:]

        # Handle hardware interfaces
        interface_names.update(
            {dev: name for dev, name in zip([name.split(':')[1].strip() for name in interfaces[2::4]],
                                            [name.split(':')[1].strip() for name in interfaces[1::4]])})

        # Update to include VLAN interfaces
        interface_names.update({dev: name
                                for dev, name in zip([name.split(':')[1].strip() for name in vlans[3::5]],
                                                     [name.split(':')[1].strip() for name in vlans[1::5]])})

    if WINDOWS:
        # Windows extraction adapted from example:
        # https://stackoverflow.com/questions/29913516/how-to-get-meaningful-network-interface-names-instead-of-guids-with-netifaces-un
        try:
            # Python 3.x
            import winreg
            winreg_exception = (winreg.PermissionError, winreg.FileNotFoundError)

        except (ImportError, AttributeError):
            # Python 2.x
            import _winreg as winreg
            winreg_exception = WindowsError

        ifs = netifaces.interfaces()

        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        reg_key = winreg.OpenKey(reg,
                                 r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')

        for i in range(len(ifs)):
            try:
                # Perform best effort update for each interface!
                reg_subkey = winreg.OpenKey(reg_key, ifs[i] + r'\Connection')
                ifs_name = winreg.QueryValueEx(reg_subkey, 'Name')[0]

            except winreg_exception:
                ifs_name = u'Unknown'

            interface_names[ifs[i]] = ifs_name

    return interface_names
