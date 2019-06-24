#!/usr/bin/env python3
#
# setup.py - Vocabulary Football (VocBall)
# Copyright (C) 2017-2019 - Thomas Dähnrich <develop@tdaehnrich.de>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess

from glob import glob
from setuptools import setup
from vocball.settings import VERSION


# create locale files

languages = ('de', 'en_GB', 'va')

for lang in languages:
    locale_dir = os.path.join('locale', lang, 'LC_MESSAGES')
    locale_file = os.path.join(locale_dir, 'vocball.mo')
    po_file = os.path.join('po', lang + '.po')
    if not os.path.exists(locale_dir):
        os.makedirs(locale_dir)
        subprocess.call(['msgfmt', '-o', locale_file, po_file])
    if lang == 'va':
        locale_c_dir = os.path.join('locale', 'C', 'LC_MESSAGES')
        if not os.path.exists(locale_c_dir):
            os.makedirs(locale_c_dir)
            subprocess.call(['cp', '-u', locale_file, locale_c_dir])


# create desktop file

template_file = os.path.join('data', 'com.gitlab.RomaAeterna.VocBall.desktop.in')
desktop_file = os.path.join('data', 'com.gitlab.RomaAeterna.VocBall.desktop')

if not os.path.exists(desktop_file):
    subprocess.call(['msgfmt', '--desktop', '--template={}'.format(template_file),
        '--output-file={}'.format(desktop_file), '-d', 'po'])


# get README description

with open('README.rst', 'r') as f:
    long_description = f.read()


# install application

setup(
    name = 'vocball',
    version = VERSION,
    license = 'GPL-3+',
    packages = [
        'vocball',
        'vocball.simpleaudio',
    ],
    package_data = {
        'vocball.simpleaudio': ['LICENSE.txt', 'README.rst', '_simpleaudio.so'],
    },
    scripts = ['bin/vocball'],
    data_files = [
        ('share/applications', [desktop_file]),
        ('share/icons/hicolor/16x16/apps', glob('data/icons/hicolor/16x16/apps/*')),
        ('share/icons/hicolor/22x22/apps', glob('data/icons/hicolor/22x22/apps/*')),
        ('share/icons/hicolor/24x24/apps', glob('data/icons/hicolor/24x24/apps/*')),
        ('share/icons/hicolor/32x32/apps', glob('data/icons/hicolor/32x32/apps/*')),
        ('share/icons/hicolor/48x48/apps', glob('data/icons/hicolor/48x48/apps/*')),
        ('share/icons/hicolor/256x256/apps', glob('data/icons/hicolor/256x256/apps/*')),
        ('share/icons/hicolor/512x512/apps', glob('data/icons/hicolor/512x512/apps/*')),
        ('share/locale/C/LC_MESSAGES', ['locale/C/LC_MESSAGES/vocball.mo']),
        ('share/locale/de/LC_MESSAGES', ['locale/de/LC_MESSAGES/vocball.mo']),
        ('share/locale/en_GB/LC_MESSAGES', ['locale/en_GB/LC_MESSAGES/vocball.mo']),
        ('share/locale/va/LC_MESSAGES', ['locale/va/LC_MESSAGES/vocball.mo']),
        ('share/vocball/pixmaps', glob('data/pixmaps/*')),
        ('share/vocball/sounds', glob('data/sounds/*')),
        ('share/vocball/ui', glob('data/ui/*')),
    ],
    python_requires = '>=3.3',
    author = 'Thomas Dähnrich',
    description = 'Play vocabulary football in class',
    long_description = long_description,
    keywords = ['education', 'game'],
    url = 'https://gitlab.com/romaaeterna/vocball',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: GTK',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Desktop Environment :: Gnome',
        'Topic :: Education',
        'Topic :: Games/Entertainment',
    ],
)
