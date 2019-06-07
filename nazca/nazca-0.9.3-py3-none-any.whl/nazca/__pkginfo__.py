# pylint: disable-msg=W0622
# copyright 2004-2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of nazca.
#
# nazca is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# nazca is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with nazca. If not, see <http://www.gnu.org/licenses/>.
"""Nazca packaging information."""
__docformat__ = "restructuredtext en"
from os.path import join
import sys

distname = 'nazca'
modname = 'nazca'

numversion = (0, 9, 3)
version = '.'.join([str(num) for num in numversion])

license = 'LGPL'  # 2.1 or later
description = "Python library for data alignment"
web = "https://www.logilab.org/project/nazca"
author = "Logilab"
author_email = "contact@logilab.fr"

classifiers = [
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Text Processing',
]

__depends__ = {
    'python-dateutil': None,
    'lxml': None,
    'six': None,
    'numpy': None,
    'scipy': None,
    'scikit-learn': None,
}

__recommends__ = {
    'sparqlwrapper': None,
    'nltk': None,
}

include_dirs = [join('test', 'data'), 'data', 'examples', 'ner', 'rl', 'utils']

if sys.version_info < (2, 7):
    __depends__['unittest2'] = '>= 0.5.1'
