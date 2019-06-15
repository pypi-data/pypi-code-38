#! /usr/bin/env python
"List Teradata Roles"

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2016-2019, Paresh Adhia"
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

import tdtypes as td
from .util import Listing, dbc

class Role(Listing):
	"Role Listing"

	def user_args(self):
		yield lambda p: p.add_argument("names", metavar='ROLE', nargs='*', help="search for only specific names (wild-cards allowed)")

	def cols(self, opts):
		yield ("RoleName", "Role")
		if opts.verbose >= 1:
			yield ("CommentString", "Note")

	def build_sql(self, names, opts):
		if names:
			where = "\nWHERE " + ' OR '.join([td.DBObjPat.search_predicate('RoleName', f) for f in names])
		else:
			where = ''

		return f"""\
SELECT {self.select(opts)}
FROM {dbc.RoleInfoV}{where}
ORDER BY 1"""

def main(args=None):
	"script entry-point"
	return Role(__name__, __doc__).ls(args)

if __name__ == '__main__':
	import sys
	sys.exit(main())
