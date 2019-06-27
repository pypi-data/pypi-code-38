from __future__ import print_function

from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task

#http://askubuntu.com/a/555366/13217
class VirtualboxSatchel(Satchel):

    name = 'virtualbox'

    @task(precursors=['packager'])
    def configure(self):
        """
        Enables the repository for a most current version on Debian systems.

            https://www.rabbitmq.com/install-debian.html
        """

        os_version = self.os_version
        if not self.dryrun and os_version.distro != UBUNTU:
            raise NotImplementedError("OS %s is not supported." % os_version)

        r = self.local_renderer

        r.env.codename = (r.run('lsb_release -c -s') or "`lsb_release -c -s`").strip()
        r.sudo('apt-add-repository "deb http://download.virtualbox.org/virtualbox/debian {codename} contrib"')
        r.sudo('cd /tmp; wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -')
        r.sudo('apt-get update')

virtualbox = VirtualboxSatchel()
