#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Copyright (C) 2019 K.I.A.Derouiche

#If not, see <https://www.mozilla.org/en-US/MPL/2.0/>.

import pathlib
import json

from setuptools import setup, find_packages


f = pathlib.Path("sumtool", "common", "version.json")
contents = f.read_text()
__version__ = '.'.join(str(part) for part in json.loads(contents))

path = pathlib.Path.cwd() / 'README.md'
__ldescr__ = path.read_text()   

__appinfo__ = {}
f = pathlib.Path("sumtool", "common", "__appinfo__.py")
exec(f.read_text(), __appinfo__)

modname = __appinfo__['__nameapp__']
distname = __appinfo__.get('distname', modname)
data_files = __appinfo__.get('data_files', None)
include_dirs = __appinfo__.get('include_dirs', [])
install_requires = __appinfo__.get('install_requires', None)

#data_files = []
#if sys.platform.startswith('linux'):
#    data_files.append(('/usr/share/applications', ['data/checksum-tool.desktop']))
#    data_files.append(('/usr/share/pixmaps/', ['data/checksum-tool.png']))
#elif sys.platform[:6] == 'netbsd':
 #   data_files.append(('/usr/pkg/share/applications', ['data/checksum-tool.desktop']))
#    data_files.append(('/usr/pkg/share/pixmaps/', ['data/checksum-tool.png']))
#elif sys.platform.startswith('openbsd') or sys.platform.startswith('freebsd'):
 #   data_files.append(('/usr/local/share/applications', ['data/checksum-tool.desktop']))
#    data_files.append(('/usr/local/share/pixmaps/', ['data/checksum-tool.png']))

setup(
    name = distname,
    license=__appinfo__['__license__'],
    version=__version__,
    description= __appinfo__['__descr__'],
    long_description=__ldescr__,
    long_description_content_type='text/markdown',
    author=__appinfo__['__author__'],
    author_email= __appinfo__['__email__'],
    url=__appinfo__['__url__'],
    platforms = __appinfo__['__platform__'],
    packages= find_packages(),
    classifiers=__appinfo__['__classifiers__'],
    data_files=data_files,
    install_requires= __appinfo__['__install_requires__'],
    entry_points = {
        'gui_scripts': [
            'checksum-gui = sumtool.__main__:main',
        ],
    },
)
