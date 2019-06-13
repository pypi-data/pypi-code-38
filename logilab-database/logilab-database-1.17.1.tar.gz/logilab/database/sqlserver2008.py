# copyright 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of logilab-database.
#
# logilab-database is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# logilab-database is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with logilab-database. If not, see <http://www.gnu.org/licenses/>.
"""Sqlserver 2008 RDBMS support

Mostly untested, use at your own risks. 

Supported drivers, in order of preference:
- pyodbc (recommended, others are not well tested)
- adodbapi

"""

from logilab import database as db
from logilab.database.sqlserver import _PyodbcAdapter, _AdodbapiAdapter

class _PyodbcSqlServer2008Adapter(_PyodbcAdapter):
    driver = "SQL Server Native Client 10.0"


class _AdodbapiSqlServer2008Adapter(_AdodbapiAdapter):
    driver = "SQL Server Native Client 10.0"

db._PREFERED_DRIVERS.update({
    'sqlserver2008' : ['pyodbc', 'adodbapi', ],
    })

db._ADAPTER_DIRECTORY.update({
    'sqlserver2008' : {'adodbapi': _AdodbapiSqlServer2008Adapter,
                       'pyodbc': _PyodbcSqlServer2008Adapter},
    })
