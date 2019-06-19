# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import sys
import os

# MONKEY PATCH WARNING:
# Despicable check for anaconda, which has its own, unwelcome qt.conf.
# Relies on the fact that Pyside._utils.register_qt_conf will eventually
# look for qt.conf using os.path.exists in the directory of the python
# executable.
#
# Recent Anaconda does not provide PySide, so whatever Qt is included will
# likely be unusable.
if ' |Anaconda ' in sys.version or 'Continuum Analytics, Inc' in sys.version:
    _os_path_exists = os.path.exists
    _qtconf_path = os.path.join(os.path.dirname(sys.executable), 'qt.conf')

    try:
        os.path.exists = (
            lambda x: False if _qtconf_path == x else _os_path_exists(x))
        import PySide  # NOQA
    finally:
        os.path.exists = _os_path_exists
