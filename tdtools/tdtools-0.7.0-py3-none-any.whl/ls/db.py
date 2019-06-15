#! /usr/bin/env python

"List Teradata Databases"

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
from .util import Listing, dbc

class Database(Listing):
	"Database listing"

	def user_args(self):
		yield lambda p: p.add_argument("names", metavar='DB', nargs='*', help="search for only specific names (wild-cards allowed)")
		yield args_filter
		yield args_display
		yield args_order

	def cols(self, opts):
		if opts.verbose >= 1:
			yield ("d.DBKind", "T")
			yield ("PermSpace", "Alloc_")

		if opts.verbose >= 2:
			yield ("CurrPerm", "Used_")
			yield ("ImpactPerm", "Impact_")
			yield ("PermSpace - ImpactPerm", "Free_")

		if opts.verbose >= 1:
			yield ("UsedPct", "Used%")

		if opts.verbose >= 2:
			yield ("DBSkew", "Skew%")

		yield ("d.DatabaseName", "DB")

		if opts.verbose >= 2:
			yield ("OwnerName", "Owner")
			yield ("CreateTimestamp", "Created")
			yield ("CreatorName", "Creator")

	def build_sql(self, names, opts):
		sql = f"""\
SELECT {self.select(opts)}
FROM {dbc.DatabasesV} d
LEFT JOIN (
	SELECT DatabaseName
		, Sum(CurrentPerm) as CurrPerm
		, CAST(Sum(CurrentPerm) as FLOAT) / NullIFZero(Sum(MaxPerm)) as UsedPct
		, CAST((1.0 - AVG(CurrentPerm) / NULLIFZERO(MAX(CurrentPerm))) AS DECIMAL(4,3)) AS DBSkew
		, Max(CurrentPerm) * count(*) as ImpactPerm
	FROM {dbc.Diskspacev}
	GROUP BY 1
) k ON k.DatabaseName = d.DatabaseName"""

		cond = []
		if names:
			pred = ' OR '.join([td.DBObjPat.search_predicate('OwnerName' if opts.owner else 'd.DatabaseName', f) for f in names])
			cond.append("({})".format(pred) if len(names) > 1 else pred)
		if opts.hide:
			pred = ' OR '.join(f"d.DatabaseName LIKE ")
			cond.append('d.DatabaseName NOT LIKE ALL ({})'.format(",".join(f"'{d}'" for d in opts.hide)))
		if opts.dbkind:
			cond.append("DBKind = '{}'".format(opts.dbkind))
		if opts.non_zero:
			cond.append("PermSpace > 0")

		if cond:
			sql += "\n WHERE " + "\n   AND ".join(cond)

		if opts.sort != 'none':
			sql += "\n ORDER BY " + {'name': 'd.DatabaseName', 'size': 'PermSpace', 'time': 'CreateTimestamp'}[opts.sort]
			if opts.reverse:
				sql += " DESC"

		return sql

def args_filter(p):
	"options to filter listing"
	g = p.add_argument_group("Filters")
	g.add_argument('-o', '--owner', action='store_true', help='names to seach are owner names')
	g.add_argument("-Z", "--non-zero", action='store_true', help="only show databases with non-zero PERM space")
	g.add_argument("-I", "--hide", action='append', metavar='PATTERN',  help="exclude database names that match PATTERN")
	x = g.add_mutually_exclusive_group()
	x.add_argument('-d', '--only-db', dest='dbkind', action='store_const', const='D', help='list only databases')
	x.add_argument('-u', '--only-users', dest='dbkind', action='store_const', const='U', help='list only users')

def args_display(p):
	"options to format the display"
	from .util import args_size
	g = p.add_argument_group("Display")
	args_size(g)

def args_order(p):
	"options to order the listing"
	from .util import args_sort
	g = p.add_argument_group("Ordering")
	args_sort(g)

def main(args=None):
	"script entry-point"
	return Database(__name__, __doc__).ls(args)

if __name__ == '__main__':
	import sys
	sys.exit(main())
