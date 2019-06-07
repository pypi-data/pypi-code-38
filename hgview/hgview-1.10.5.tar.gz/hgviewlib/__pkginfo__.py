# pylint: disable=W0622
# coding: iso-8859-1
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
"""Copyright (c) 2000-2012 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

import glob
from os.path import join as joinpath
distname = modname = 'hgview'
numversion = (1, 10, 5)
version = '.'.join([str(num) for num in numversion])


license = 'GPL'
copyright = '''Copyright © 2007-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''


classifiers =  ['Development Status :: 4 - Beta',
                'Environment :: X11 Applications :: Qt',
                'Environment :: Win32 (MS Windows)',
                'Environment :: MacOS X',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: GNU General Public License (GPL)',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Version Control',
                ]


description = "a Mercurial interactive history viewer"


author = "Logilab"
author_email = 'python-projects@lists.logilab.org'

# TODO - publish
web = "http://www.logilab.org/projects/%s" % modname
ftp = "ftp://ftp.logilab.org/pub/%s" % modname
mailinglist = "mailto://python-projects@lists.logilab.org"


scripts = ['bin/hgview']
debian_name = 'hgview'
debian_maintainer = 'Alexandre Fayolle'
debian_maintainer_email = 'afayolle@debian.org'
pyversions = ["2.5"]

debian_handler = 'python-dep-standalone'

include_dirs = []
data_files = [
    [joinpath('share', 'doc', 'hgview', 'examples'),
     [joinpath('hgviewlib', 'qt4', 'resources', 'description.css')]]
]
