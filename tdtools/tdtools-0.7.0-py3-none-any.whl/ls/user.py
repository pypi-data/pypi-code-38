#! /usr/bin/env python

"List Teradata Users"

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

from .util import Listing, args_size, dbc

class User(Listing):
	"User listing"
	def user_args(self):
		yield lambda p: p.add_argument("names", metavar='USER', nargs='*', help="search for only specific names (wild-cards allowed)")
		yield lambda p: p.add_argument("-p", "--profile", action="store_true", help="names to search are profile names (default usernames)")
		yield args_size

	def cols(self, opts):
		yield ("D.DatabaseName", "User")

		if opts.verbose >= 1:
			yield ("D.ProfileName", "Prof")
			yield ("COALESCE(P.DefaultDB,D.DefaultDatabase)", "DB")
			yield ("D.PermSpace", "Perm_")
			yield ("COALESCE(P.SpoolSpace,D.SpoolSpace)", "Spool_")
			yield ("COALESCE(P.TempSpace,D.TempSpace)", "Temp_")

		if opts.verbose >= 2:
			yield ("COALESCE(P.DefaultAccount,AccountName)", "Acct")
			yield ("D.PasswordChangeDate", "PasswdChg")

			if opts.verbose >= 3:
				yield ("D.LockedTimestamp", "Locked")
				yield ("D.CreateTimeStamp", "Created")
			else:
				yield ("CAST(D.LockedTimestamp AS DATE)", "Locked")
				yield ("CAST(D.CreateTimeStamp AS DATE)", "Created")

			yield ("D.CommentString", "Note")

		if opts.verbose >= 3:
			yield ("D.OwnerName", "Owner")
			yield ("D.CreatorName", "Creator")
			yield ("D.LastAlterTimeStamp", "Altered")

	def build_sql(self, names, opts):
		def preds():
			yield "RowType = 'U'"
			if names:
				import tdtypes as td
				search_col = 'D.ProfileName' if opts.profile else 'DatabaseName'
				pred = ' OR '.join([td.DBObjPat.search_predicate(search_col, n) for n in names])
				yield pred if len(names) == 1 else '('+pred+')'

		where = "\n\tAND ".join(preds())

		return f"""\
SELECT {self.select(opts)}
FROM (
	SELECT D.*
		, case when PasswordChgDate < 0
			then null
			else cast(((100 * ((4 * nullifzero(PasswordChgDate) - 1) / 146097)
				+ (4 * (((4 * PasswordChgDate - 1) MOD 146097) / 4)
				+ 3) / 1461 - 1900) + ((5 * (((4 * (((4 * PasswordChgDate
				- 1) MOD 146097) / 4) + 3) MOD 1461 + 4) / 4) - 3) / 153 + 2)
				/ 12) * 10000 + (((5 * (((4 * (((4 * PasswordChgDate - 1)
				MOD 146097) / 4) + 3) MOD 1461 + 4) / 4) - 3) / 153 + 2) MOD 12
				+ 1) * 100 + ((5 * (((4 * (((4 * PasswordChgDate - 1) MOD
				146097) / 4) + 3) MOD 1461 + 4) / 4) - 3) MOD 153 +5) / 5
			 as date format 'yyyy-mm-dd')
			end as PasswordChangeDate
		, cast(((100 * ((4 * LockedDate - 1) / 146097)
				+ (4 * (((4 * LockedDate - 1) MOD 146097) / 4)
				+ 3) / 1461 - 1900) + ((5 * (((4 * (((4 * LockedDate
				- 1) MOD 146097) / 4) + 3) MOD 1461 + 4) / 4) - 3) / 153 + 2)
				/ 12) * 10000 + (((5 * (((4 * (((4 * LockedDate - 1)
				MOD 146097) / 4) + 3) MOD 1461 + 4) / 4) - 3) / 153 + 2) MOD 12
				+ 1) * 100 + ((5 * (((4 * (((4 * LockedDate - 1) MOD
				146097) / 4) + 3) MOD 1461 + 4) / 4) - 3) MOD 153 +5) / 5
			as date format 'yyyy-mm-dd') AS LockedDate2
		, cast((LockedTime / 60) * 10000 + (LockedTime MOD 60) * 100 as integer format '99:99:99') as LockedTime2
		, cast(cast(LockedDate2 as char(10)) || 'T' || cast(LockedTime2 as char(8)) as timestamp) as LockedTimestamp
	FROM {dbc.dbase} D
) D
LEFT JOIN {dbc.ProfileInfoV} P ON P.ProfileName = D.ProfileName
WHERE {where}
ORDER BY 1"""

def main(args=None):
	"script entry-point"
	return User(__name__, __doc__).ls(args)

if __name__ == '__main__':
	import sys
	sys.exit(main())
