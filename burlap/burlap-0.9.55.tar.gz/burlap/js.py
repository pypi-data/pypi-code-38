from __future__ import print_function

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task

class JSHintSatchel(ServiceSatchel):

    name = 'jshint'

    def set_defaults(self):
        pass

#     @property
#     def packager_system_packages(self):
#         return {
#             DEBIAN: ['npm'],
#             UBUNTU: ['npm'],
#         }

    @task
    def install_packages(self):
        packager = self.packager
        if packager == APT:
            self.sudo('apt-get update --fix-missing')
            # Necessary because Ubuntu 14 has malformed npm/nodejs packages.
            self.sudo('DEBIAN_FRONTEND=noninteractive apt-get -f -o Dpkg::Options::="--force-overwrite" install --yes npm')
        else:
            raise NotImplementedError('Unsupported packager: %s' % (packager,))

    @task(precursors=['packager', 'user'])
    def configure(self):
        r = self.local_renderer
        if r.env.enabled:
            self.install_packages()
            r.sudo('npm install -g jshint')
            # The Ubuntu 14 package is malformed and refers to "node" instead of "nodejs".
            r.sudo('[ ! -f /usr/bin/node ] && ln -s /usr/bin/nodejs /usr/bin/node || true')
        else:
            r.sudo('npm uninstall -g jshint')

jshint = JSHintSatchel()
