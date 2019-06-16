# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
**Package Root**

The only things present in the ``rattail`` root namespace are:

.. attribute:: __version__

   A string indicating the version of the Rattail core package.

.. attribute:: enum
   :noindex:

   The :mod:`rattail.enum` module, imported at load time for convenience.
"""

from ._version import __version__
from . import enum

# TODO: Remove this at some point, when callers are ready.  Maybe would be nice
# to deprecate somehow in the meantime?
from rattail.enum import *
