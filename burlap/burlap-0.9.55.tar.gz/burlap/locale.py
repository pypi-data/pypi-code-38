from __future__ import print_function

import re

from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task

# Note, using the name "locale" doesn't allow the satchel to be imported due to a conflict with an existing variable/module.

class LocalesSatchel(Satchel):

    name = 'locales'

    def set_defaults(self):
        self.env.language = 'en_US:en' # 'en_US.UTF-8'
        self.env.lang = 'C' # 'en_US.UTF-8'
        self.env.lc_all = None # 'C' # 'en_US.UTF-8'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['locales'],
            DEBIAN: ['locales'],
        }

    @task
    def cat_locale(self):
        return self.run('cat /etc/default/locale')

    def get_locale_dict(self, text=None):
        """
        Reads /etc/default/locale and returns a dictionary representing its key pairs.
        """
        text = text or self.cat_locale()
        # Format NAME="value".
        return dict(re.findall(r'^([a-zA-Z_]+)\s*=\s*[\'\"]*([0-8a-zA-Z_\.\:\-]+)[\'\"]*', text, re.MULTILINE))

    @task(precursors=['user'])
    def configure(self):
        r = self.local_renderer

        # Locales is an odd case, because it needs to be run before most packages are installed
        # but it still needs to ensure it's own package is installed.
        self.install_packages()

        args = []
        if r.env.language:
            args.append('LANGUAGE={language}')
        if r.env.lang:
            args.append('LANG={lang}')
        if r.env.lc_all:
            args.append('LC_ALL={lc_all}')

        r.env.exports = ' '.join('export %s;' % _ for _ in args)
        r.env.lang = r.env.lang or r.env.language
        if r.env.lang:
            r.sudo('{exports} locale-gen {lang}')

        r.sudo('{exports} dpkg-reconfigure --frontend=noninteractive locales')

        r.env.update_args = ' '.join(args)
        r.sudo('{exports} update-locale {update_args}')

locales = LocalesSatchel()
