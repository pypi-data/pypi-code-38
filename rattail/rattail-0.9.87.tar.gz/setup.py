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

from __future__ import unicode_literals, absolute_import

import sys
import os.path
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
exec(open(os.path.join(here, 'rattail', '_version.py')).read())
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

    'bcrypt',                           # 3.1.4
    'humanize',                         # 0.5.1
    'lockfile',                         # 0.9.1
    'openpyxl',                         # 2.5.0
    'packaging',                        # 19.0
    'progress',                         # 1.3
    'six',                              # 1.10.0
    'texttable',                        # 1.2.1
    'xlrd',                             # 1.1.0

    # TODO: Remove this / make it optional / etc.
    'Mako',                             # 1.0.0

    # Hardcode ``pytz`` minimum since apparently it isn't (any longer?) enough
    # to simply require the library.
    'pytz>=2013b',                      #                       2013b 
]


if sys.platform != 'win32':
    requires += [
        #
        # package                       # low                   high
            
        'pyinotify',                    # 0.9.3
    ]


extras = {

    'bouncer': [
        #
        # package                       # low                   high

        # until we support PY3K we must stick with older flufl.bounce
        'flufl.bounce<3.0',             # 2.3
    ],

    'db': [
        #
        # package                       # low                   high

        # Support for multiple migration bases was added in Alembic 0.7.
        'alembic>=0.7.0',               #                       0.7.4

        'SQLAlchemy',                   # 0.7.6
        'SQLAlchemy-Continuum',         # 1.1.5
    ],

    'docs': [
        #
        # package                       # low                   high

        'Sphinx',                       # 1.1.3
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


# TODO: pretty sure some/all of this should be merged with above
if sys.platform == 'win32':
    extras['auth'] = [
        #
        # package                       # low                   high

        'py-bcrypt-w32',                # 0.2.2
        ]
else:
    extras['auth'] = [
        #
        # package                       # low                   high

        'passlib',                      # 1.7.1
    ]


setup(
    name = "rattail",
    version = __version__,
    author = "Lance Edgar",
    author_email = "lance@edbob.org",
    url = "https://rattailproject.org/",
    license = "GNU GPL v3",
    description = "Retail Software Framework",
    long_description = README,

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    install_requires = requires,
    extras_require = extras,
    tests_require = ['rattail[db,tests]'],
    test_suite = 'nose.collector',

    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,

    entry_points = """

[console_scripts]
rattail = rattail.commands:main
rattail-dev = rattail.commands.dev:main
trainwreck = rattail.trainwreck.commands:main

[gui_scripts]
rattailw = rattail.commands:main

[rattail.commands]
backup = rattail.commands.backup:Backup
bouncer = rattail.commands.core:EmailBouncer
clonedb = rattail.commands.core:CloneDatabase
datasync = rattail.commands.core:DataSync
date-organize = rattail.commands.core:DateOrganize
execute-batch = rattail.commands.batch:ExecuteBatch
export-rattail = rattail.commands.importing:ExportRattail
filemon = rattail.commands.core:FileMonitorCommand
import-rattail = rattail.commands.importing:ImportRattail
import-sample = rattail.commands.importing:ImportSampleData
import-versions = rattail.commands.importing:ImportVersions
make-appdir = rattail.commands.core:MakeAppDir
make-config = rattail.commands.core:MakeConfig
make-user = rattail.commands.core:MakeUser
make-uuid = rattail.commands.core:MakeUUID
populate-batch = rattail.commands.batch:PopulateBatch
purge-batches = rattail.commands.batch:PurgeBatches
refresh-batch = rattail.commands.batch:RefreshBatch
run-n-mail = rattail.commands.core:RunAndMail
runsql = rattail.commands.core:RunSQL
update-costs = rattail.commands.products:UpdateCosts
upgrade = rattail.commands.core:Upgrade

[rattail_dev.commands]
new-batch = rattail.commands.dev:NewBatch

[rattail.config.extensions]
rattail.db = rattail.db:ConfigExtension
rattail.trainwreck = rattail.trainwreck.config:TrainwreckConfig

[rattail.sil.column_providers]
rattail = rattail.sil.columns:provide_columns

[rattail.vendors.catalogs.parsers]
rattail.contrib.dutchvalley = rattail.contrib.vendors.catalogs.dutchvalley:DutchValleyCatalogParser
rattail.contrib.kehe = rattail.contrib.vendors.catalogs.kehe:KeheCatalogParser
rattail.contrib.lotuslight = rattail.contrib.vendors.catalogs.lotuslight:LotusLightCatalogParser
rattail.contrib.unfi = rattail.contrib.vendors.catalogs.unfi:UNFICatalogParser
rattail.contrib.unfi.2 = rattail.contrib.vendors.catalogs.unfi:UNFICatalogParser2

[rattail.vendors.invoices.parsers]
rattail.contrib.alberts = rattail.contrib.vendors.invoices.alberts:AlbertsInvoiceParser
rattail.contrib.kehe = rattail.contrib.vendors.invoices.kehe:KeheInvoiceParser
rattail.contrib.unfi = rattail.contrib.vendors.invoices.unfi:UnfiInvoiceParser

""",
)
