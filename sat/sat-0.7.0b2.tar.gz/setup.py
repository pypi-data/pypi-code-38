#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: an XMPP client
# Copyright (C) 2009-2016  Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import os

NAME = 'sat'

install_requires = [
    'babel',
    'dbus-python',
    'html2text',
    'jinja2>=2.10',
    'langid',
    'lxml >= 3.1.0',
    'markdown >= 3.0',
    'miniupnpc',
    'mutagen',
    'netifaces',
    'pillow',
    'progressbar',
    'pycrypto >= 2.6.1',
    'pygments',
    'pygobject',
    'PyOpenSSL',
    'python-dateutil',
    'python-potr',
    'pyxdg',
    'sat_tmp >= 0.7.0a4',
    'shortuuid',
    'twisted[tls] >= 15.2.0',
    'urwid >= 1.2.0',
    'urwid-satext >= 0.7.0a2',
    'wokkel >= 0.7.1',
    'omemo',
    'omemo_backend_signal',
]

DBUS_DIR = 'dbus-1/services'
DBUS_FILE = 'misc/org.salutatoi.SAT.service'
with open(os.path.join(NAME, 'VERSION')) as f:
    VERSION = f.read().strip()
is_dev_version = VERSION.endswith('D')


def sat_dev_version():
    """Use mercurial data to compute version"""
    def version_scheme(version):
        return VERSION.replace('D', '.dev0')

    def local_scheme(version):
        return "+{rev}.{distance}".format(
            rev=version.node[1:],
            distance=version.distance)

    return {'version_scheme': version_scheme,
            'local_scheme': local_scheme}


setup(name=NAME,
      version=VERSION,
      description=u'Salut à Toi multipurpose and multi frontend XMPP client',
      long_description=u'Salut à Toi (SàT) is a XMPP client based on a daemon/frontend '
                       u'architecture. Its multi frontend (desktop, web, console '
                       u'interface, CLI, etc) and multipurpose (instant messaging, '
                       u'microblogging, games, file sharing, etc).',
      author='Association « Salut à Toi »',
      author_email='contact@goffi.org',
      url='https://salut-a-toi.org',
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Framework :: Twisted',
                   'License :: OSI Approved :: GNU Affero General Public License v3 '
                   'or later (AGPLv3+)',
                   'Operating System :: POSIX :: Linux',
                   'Topic :: Communications :: Chat'],
      packages=find_packages() + ['twisted.plugins'],
      data_files=[('share/locale/fr/LC_MESSAGES',
                   ['i18n/fr/LC_MESSAGES/sat.mo']),
                  (os.path.join('share/doc', NAME),
                   ['CHANGELOG', 'COPYING', 'INSTALL', 'README', 'README4TRANSLATORS']),
                  (os.path.join('share', DBUS_DIR), [DBUS_FILE]),
                  ],
      scripts=['sat_frontends/jp/jp', 'sat_frontends/primitivus/primitivus', 'bin/sat'],
      zip_safe=False,
      setup_requires=['setuptools_scm'] if is_dev_version else [],
      use_scm_version=sat_dev_version if is_dev_version else False,
      install_requires=install_requires,
      package_data={'sat': ['VERSION']},
      python_requires='~=2.7',
      )
