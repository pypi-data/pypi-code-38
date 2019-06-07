# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['whost', 'whost.ui']

package_data = \
{'': ['*']}

install_requires = \
['PyYaml>=3.13,<4.0',
 'colorama>=0.4.1,<0.5.0',
 'humanfriendly>=4.17,<5.0',
 'ipython>=7.2,<8.0',
 'netifaces>=0.10.7,<0.11.0',
 'requests>=2.21,<3.0',
 'tabulate>=0.8.2,<0.9.0',
 'unidecode>=1.0,<2.0']

setup_kwargs = {
    'name': 'whost',
    'version': '0.1.22',
    'description': 'Cardshop Writer Host Tools',
    'long_description': "# Cardshop Writer Host\n\nCardshop use writer hosts to download, write and ship SD-cards to recipient.\nA WriterHost is an always-running, always-connected computer connected to one or more USB SD-card readers (physical device).\n\nWriter Hosts authenticate with the cardshop to fetch tasks. The WriterHost operator is contacted (email) when an SD-card must be inserted, retrieved and shipped.\n\n## Requirements\n\n* always-on-capable computer\n* 500GB storage or more.\n* high-speed, direct, permanent connection to internet via ethernet.\n* one or more good-quality USB SD-card readers ([Kingston MobileLite G4](https://www.ldlc.com/fiche/PB00171186.html))\n* A `writer` account on the cardshop.\n* An assigned port on the demo server (see [maintenance](http://wiki.kiwix.org/wiki/Cardshop-maintenance)).\n\n## Ubuntu Install\n\nJust a regular, fresh Ubuntu-server install. Bellow are the __defaults used for tests__ (you can customize them).\n\n* Boot off the install media & select *Install Ubuntu Server* at grub prompt.\n* Select language (*English*)\n* Select Keyboard layout (*English (US)*, *English (US)*)\n* Select *Install Ubuntu* (not cloud instance)\n* Configure the network (*eth via dhcp*)\n* Proxy Address: none\n* Mirror Address: http://archive.ubuntu.com/ubuntu (pre-filled default)\n* *Use an entire Disk*\n* Choose disk to install to: *selected disk*\n* Summary: confirm and continue\n* Profile\n  * name: whatever (ex: `maint`)\n  * server name: whatever (ex: `bkored`)\n  * username: whatever (ex: `maint_user`)\n  * password: whatever (ex: `maint_pwd`)\n* *Reboot now*\n* Remove install media then `ENTER`\n\n## Setup software\n\n* log-in and elevate as `root` (`sudo su -`)\n* set a password for `root` (`passwd`)\n* Make sure internet is working\n* Configure SSH tunneling for remote access\n  * Generate SSH key pair for `root` using `ssh-keygen` (no passphrase)\n  * Copy `/root/.ssh/id_rsa` to `/root/.ssh/tunnel`\n  * Share (via email for example) public key with cardshop admin (it's located at `/root/.ssh/id_rsa.pub`).\n  * This file will be appened to `/home/tunnel/.ssh/authorized_keys` on the the tunneling server gateway by the cardshop admin, so the writer can connect.\n* Download setup script `curl -L -o /tmp/whost-setup https://raw.githubusercontent.com/kiwix/cardshop/master/whost/whost-setup`\n* Go to https://wiki.kiwix.org/wiki/Cardshop/maintenance, pick a port for your host and update the writers table\n* run the setup script `chmod +x /tmp/whost-setup && REVERSE_SSH_PORT=XXX /tmp/whost-setup`. \n\n## Configure the writer\n\nThe writer is configured through a command-line tool that is launched automatically when logging-in as `root` (not via `su`).\n\n``` sh\nHotsport Cardshop writer-host configurator\n-------------------------------------------\n\n:: Internet Connectivity: CONNECTED\n:: Authentication: AUTHENTICATED\n:: Host Status: ENABLED\n:: Configured Writers: 2\n:: Choose:\n   1 Configure Network\n   2 Configure Credentials\n   3 Configure USB Writers\n   4 Update code and restart\n   5 Disable this Host\n   6 Exit to a shell\n   7 Exit (logout)\n>\n```\n\nYou can launch it on any console via `whost-config`.\n\n__Initially__, use the *Update code and Restart* option to make sure you get all the fixes.\n\n__First__, make sure *Internet Connectivity* shows *CONNECTED*. If not, you should configure it externally or using the *Configure Network* helper (only Ethernet).\n\n__Second__, configure *Authentication* using *Configure Credentials*. Enter your Scheduler's username and password (should be of the `writer` role) and press enter when asked for the API URL (default should be OK).\n\n__Then__, *Configure USB Writers*. For this, you'll need your _Kingston mobilite G4_ USB readers. Kingston readers are seen as block devices (in `/dev/sd_`) when plugged, even when no card are inserted.\n\n**WARNING**: the *USB Writers* configuration does not accept devices being removed or reinserted while the computer is running. If you accidentaly disconnect one of the reader, reconnect it and restart.\n\nFor the initial configuration, shutdown the computer, plug the USB devices and then start the computer to proceed to the Configuration.\n\n``` sh\n> 3\n:: Already configured writer devices\n * A:/dev/sdc (Generic- USB3.0 CRW   -SD at 2:0:0:1)\n * B:/dev/sde (Generic- USB3.0 CRW   -SD at 3:0:0:1)\n\n:: Choose:\n   1 Reset writers config (remove ALL)\n   2 Add one device\n   3 CANCEL\n>\n```\n\nTo configure devices, follow on-screen's instructions: remove SD-cards from all ports then, when asked, enter any card into the desired device. The configurator will detect the card, its reader and assign a *Slot Name* to it (a letter). You can now remove the SD-card and proceed to configure another device or exit.\n\nWhen your host picks up writing jobs, it will (once download is complete) ask you to insert a certain capacity SD-card into *Slot X* where slot is the assigned Slot Name. Make sure you label your physical slots on your readers with their assigned names. If you don't unplug the readers, those names won't change.\n\n_Note_: The recommended Kingston readers are actually 2 independent readers with different slots (1 x microSD and 1 x SD). You can choose to configure both of just the one you prefer but keep in mind that those are not interchangeable.\n\n__Finally__, you can *Enable this host*. This will trigger the launch (and automatic launch upon startup) of your downloader container and one writer container per configured USB reader.\n\n--\n\nYou can check that your host is properly configured by:\n\n* Exiting to shell and running `docker ps` and `docker logs`.\n* Check the *Scheduler* page on the Manager UI.\n* Ask the cardshop admin to connect using the reverse SSH bridge (`ssh -i /root/whost-maint.priv root@localhost -p 2111`)\n",
    'author': 'renaud gaudin',
    'author_email': 'reg@kiwix.org',
    'url': 'https://www.kiwix.org/kiwix-hotspot/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
