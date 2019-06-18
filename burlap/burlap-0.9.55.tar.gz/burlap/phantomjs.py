from __future__ import print_function

from fabric.api import cd

from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task


class PhantomJSSatchel(Satchel):
    """
    Installs PhantomJS from upstream, since the Ubuntu package is incorrectly built.

    Extrapolated from this Gist:

        https://gist.github.com/telbiyski/ec56a92d7114b8631c906c18064ce620

    """

    name = 'phantomjs'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: [
                'build-essential',
                'chrpath',
                'libssl-dev',
                'libxft-dev',
                'libfreetype6',
                'libfreetype6-dev',
                'libfontconfig1',
                'libfontconfig1-dev',
            ],
        }

    def set_defaults(self):
        self.env.version = '2.1.1'
        self.env.target = 'phantomjs-{version}-linux-x86_64'
        self.env.wget_url = 'https://github.com/Medium/phantomjs/releases/download/v{version}/{target}.tar.bz2'
        self.env.installed = True

    @task
    def install(self):
        r = self.local_renderer

        # Ensure the buggy system package is removed.
        r.sudo('DEBIAN_FRONTEND=noninteractive apt-get -yq purge phantomjs')

        with cd('/tmp'):
            r.run('wget {wget_url}')
            r.run('tar xvjf {target}.tar.bz2')
            r.sudo('[ -d /usr/local/share/{target} ] && rm -Rf /usr/local/share/{target} || true')
            r.sudo('mv {target} /usr/local/share')
            r.sudo('[ -f /usr/local/bin/phantomjs ] && rm -f /usr/local/bin/phantomjs || true')
            r.sudo('ln -sf /usr/local/share/{target}/bin/phantomjs /usr/local/bin')
            r.run('phantomjs --version')

    @task
    def uninstall(self):
        r = self.local_renderer
        r.sudo('rm -Rf /usr/local/share/{target}')
        r.sudo('rm -f /usr/local/bin/phantomjs')

    @task(precursors=['packager', 'user'])
    def configure(self, *args, **kwargs):
        r = self.local_renderer
        if r.env.installed:
            self.install()
        else:
            self.uninstall()

phantomjs = PhantomJSSatchel()
