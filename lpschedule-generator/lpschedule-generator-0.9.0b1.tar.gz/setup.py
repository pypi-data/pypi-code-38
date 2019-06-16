#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    SPDX-License-Identifier: CC0-1.0
#
#    This file is part of lpschedule-generator.
#

from lpschedule_generator import _version

from setuptools import setup, find_packages

def readf(filename):
    content = ''
    try:
        with open(filename, 'r') as f:
            for line in f:
                content = content + line
    except IOError:
        print('Error: unable to open {}'.format(filename))
    return content

config = {
    'name': 'lpschedule-generator',
    'description': 'LibrePlanet schedule generator',
    'long_description': readf('README.rst'),
    'version': _version.__version__,
    'platforms': 'GNU/Linux',
    'license': 'Public Domain',
    'url': 'https://notabug.org/rsd/lpschedule-generator/',
    'author': 'rsiddharth',
    'author_email': 'rsd@gnu.org',
    'install_requires': ['mistune', 'Jinja2', 'beautifulsoup4',
                         'unidecode', 'icalendar', 'pytz'],
    'tests_require': ['nose', 'mock'],
    'test_suite': 'nose.collector',
    'py_modules': ['lps_gen', 'lpschedule_generator._version'],
    'data_files': [('share/lpschedule-generator/libreplanet-templates/2016',
                        [
                            'libreplanet-templates/2016/lp-schedule.jinja2',
                            'libreplanet-templates/2016/lp-speakers.jinja2'
                        ]
                    ),
                    ('share/lpschedule-generator/libreplanet-templates/2017',
                        [
                            'libreplanet-templates/2017/lp-schedule.jinja2'
                        ]
                    ),
                    ('share/lpschedule-generator/libreplanet-templates/2018',
                        [
                            'libreplanet-templates/2018/lp-schedule.jinja2'
                        ]
                    ),
                    ('share/lpschedule-generator/libreplanet-templates/2019',
                        [
                            'libreplanet-templates/2019/lp-schedule.jinja2'
                        ]
                    )
     ],
    'entry_points': {
        'console_scripts': ['lps_gen = lps_gen:main']
    },
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: Public Domain',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Text Processing',
        'Topic :: Utilities',
        ]
}

setup(**config)
