# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Setup script for Tailbone
"""

from __future__ import unicode_literals, absolute_import

import os.path
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
exec(open(os.path.join(here, 'tailbone', '_version.py')).read())
README = open(os.path.join(here, 'README.rst')).read()


requires = [
    #
    # Version numbers within comments below have specific meanings.
    # Basically the 'low' value is a "soft low," and 'high' a "soft high."
    # In other words:
    #
    # If either a 'low' or 'high' value exists, the primary point to be
    # made about the value is that it represents the most current (stable)
    # version available for the package (assuming typical public access
    # methods) whenever this project was started and/or documented.
    # Therefore:
    #
    # If a 'low' version is present, you should know that attempts to use
    # versions of the package significantly older than the 'low' version
    # may not yield happy results.  (A "hard" high limit may or may not be
    # indicated by a true version requirement.)
    #
    # Similarly, if a 'high' version is present, and especially if this
    # project has laid dormant for a while, you may need to refactor a bit
    # when attempting to support a more recent version of the package.  (A
    # "hard" low limit should be indicated by a true version requirement
    # when a 'high' version is present.)
    #
    # In any case, developers and other users are encouraged to play
    # outside the lines with regard to these soft limits.  If bugs are
    # encountered then they should be filed as such.
    #
    # package                           # low                   high

    # TODO: why do we need to cap this?  breaks tailbone.db zope stuff somehow
    'zope.sqlalchemy<1.0',              # 0.7                   0.7.7

    # TODO: apparently they jumped from 0.1 to 0.9 and that broke us...
    # (0.1 was released on 2014-09-14 and then 0.9 came out on 2018-09-27)
    # (i've cached 0.1 at pypi.rattailproject.org just in case it disappears)
    # (still, probably a better idea is to refactor so we can use 0.9)
    'webhelpers2_grid==0.1',            # 0.1

    'colander',                         # 1.7.0
    'ColanderAlchemy',                  # 0.3.3
    'cornice',                          # 3.4.2
    'deform',                           # 2.0.4
    'humanize',                         # 0.5.1
    'Mako',                             # 0.6.2
    'openpyxl',                         # 2.4.7
    'paginate',                         # 0.5.6
    'paginate_sqlalchemy',              # 0.2.0
    'passlib',                          # 1.7.1
    'Pillow',                           # 5.3.0
    'pyramid',                          # 1.3b2
    'pyramid_beaker>=0.6',              #                       0.6.1
    'pyramid_deform',                   # 0.2
    'pyramid_exclog',                   # 0.6
    'pyramid_mako',                     # 1.0.2
    'pyramid_tm',                       # 0.3
    'rattail[db,bouncer]',              # 0.5.0
    'six',                              # 1.10.0
    'sqlalchemy-filters',               # 0.8.0
    'transaction',                      # 1.2.0
    'waitress',                         # 0.8.1
    'WebHelpers2',                      # 2.0
    'WTForms',                          # 2.1
]


extras = {

    'docs': [
        #
        # package                       # low                   high

        'Sphinx',                       # 1.2
        'sphinx-rtd-theme',             # 0.2.4
    ],

    'tests': [
        #
        # package                       # low                   high

        'coverage',                     # 3.6
        'fixture',                      # 1.5
        'mock',                         # 1.0.1
        'nose',                         # 1.3.0
    ],
}


setup(
    name = "Tailbone",
    version = __version__,
    author = "Lance Edgar",
    author_email = "lance@edbob.org",
    url = "http://rattailproject.org/",
    license = "GNU GPL v3",
    description = "Backoffice Web Application for Rattail",
    long_description = README,

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    install_requires = requires,
    extras_require = extras,
    tests_require = ['Tailbone[tests]'],
    test_suite = 'nose.collector',

    packages = find_packages(exclude=['tests.*', 'tests']),
    include_package_data = True,
    zip_safe = False,

    entry_points = {

        'paste.app_factory': [
            'main = tailbone.app:main',
        ],

        'rattail.config.extensions': [
            'tailbone = tailbone.config:ConfigExtension',
        ],

        'pyramid.scaffold': [
            'rattail = tailbone.scaffolds:RattailTemplate',
        ],
    },
)
