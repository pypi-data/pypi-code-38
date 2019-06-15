#! /usr/bin/env python
"Generate DDL for Teradata Zones using DBC information"

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2016, Paresh Adhia"
__license__ = "GPL"

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from .util import * # pylint: disable=locally-disabled, wildcard-import, unused-wildcard-import

def add_args(p):
	p.add_argument("zone", default=['%'], nargs='*', help="Teradata zone name")

def genddl(args):
	if dbc.version < '15.10':
		raise Err('Zones are not supported in this Teradata release')

	sql = f"""\
SELECT ZoneName
     , RootName
FROM {dbc.ZonesV} Z
WHERE ZoneName {mk_pred(args.zone)}"""

	yield from (f"Create Zone {z}{mk_opt('Root {}', r)};" for z, r in execsql(sql, 'ZoneV SQL'))

def main(args=None):
	import sys
	return enter(sys.modules[__name__], args)
