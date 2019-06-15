#! /usr/bin/env python
"List Teradata profiles"

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2016-2017, Paresh Adhia"
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
from .util import Listing, args_size, dbc

class Profile(Listing):
	"Profile Listing"

	def user_args(self):
		yield lambda p: p.add_argument("names", metavar='PROFILE', nargs='*', help="search for only specific names (wild-cards allowed)")
		yield args_size

	def cols(self, opts):
		yield ("ProfileName", "Prof")

		if opts.verbose >= 1:
			yield ("SpoolSpace", "Spool_")
			yield ("TempSpace", "Temp_")
			yield ("DefaultDB", "DB")
			yield ("DefaultAccount", "Acct")

		if opts.verbose >= 2:
			yield ("QueryBand", "QB")
			yield ("CommentString", "Note")

	def build_sql(self, names, opts):
		if names:
			where = "\nWHERE " + ' OR '.join([td.DBObjPat.search_predicate('ProfileName', f) for f in names])
		else:
			where = ''

		return f"""\
SELECT {self.select(opts)}
FROM {dbc.ProfileInfoV}{where}
ORDER BY 1"""

def main(args=None):
	"script entry-point"
	return Profile(__name__, __doc__).ls(args)

if __name__ == '__main__':
	import sys
	sys.exit(main())
