#! /usr/bin/env python
"List Teradata objects with Linux commands ls/find like options"

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

import sys

from tdtypes import DBObjPat
from .util import Listing, dbc

class TVM(Listing):
	"TVM listing"

	def user_args(self):
		yield lambda p: p.add_argument("names", metavar='PATTERN', nargs='*', type=DBObjPat, help=DBObjPat.__doc__)
		yield args_filter
		yield args_display
		yield args_order

	def cols(self, opts):
		def tscol(ts):
			return ts if opts.verbose >= 3 else f"CAST({ts} AS DATE)"

		if opts.verbose >= 1:
			yield ('TableKind', "T")
			yield ("CreatorName", "Creator")

			yield (opts.sizecol, "Size_")
			if opts.verbose >= 2 and opts.sizecol != 'TableSize':
				yield ('TableSize', 'TSize_')
			yield ('RowCount', "Rows_")
			yield ("TableSkew", "Skew%")

			if opts.verbose < 2:
				expr, label = ("T.CreateTimestamp", "Created") if opts.create else ("T.LastAlterTimestamp", "Altered")
				yield (tscol(expr), label)

		if opts.verbose >= 2:
			yield (tscol("T.CreateTimestamp"), "Created")
			yield (tscol("T.LastAlterTimestamp"), "Altered")
			yield (tscol("R.LastCollectTimeStamp"), "StatsColl")
			yield (tscol("R.LastAlterTimeStamp"), "StatsSub")

		yield ("T.DatabaseName || '.' || T.TableName" if opts.showdb else 'T.TableName', "Table")

	def build_sql(self, names, opts):
		def preds():
			if names:
				pred = '\n    OR  '.join(n.search_cond('T.DatabaseName', 'T.TableName') for n in names)
				yield pred if len(names) == 1 else '('+pred+')'
			else:
				yield 'T.DatabaseName = Database'

			if opts.type:
				yield "Position(TableKind In '{}') > 0".format(opts.type)
			if opts.hide:
				yield from ("NOT ({})".format(p.search_cond(db='T.DatabaseName', tb='T.TableName')) for p in opts.hide)
			if opts.ctime:
				yield 'CAST(T.CreateTimestamp AS DATE) {}'.format(opts.ctime)
			if opts.mtime:
				yield 'CAST(T.LastAlterTimestamp AS DATE) {}'.format(opts.mtime)
			if opts.user:
				yield "T.CreatorName = '{}'".format(opts.user)
			if opts.size:
				yield "Size_ {}".format(opts.size)
			if opts.skew:
				yield "TableSkew {}".format(opts.skew)

		where = '\n\tAND '.join(preds())

		timecol = "T.CreateTimestamp" if opts.create else "T.LastAlterTimestamp"

		sql = f"""\
SELECT {self.select(opts)}

FROM {dbc.TablesV} T
LEFT JOIN {dbc.StatsV} R on R.DatabaseName = T.DatabaseName AND R.TableName = T.TableName AND R.ColumnName IS NULL
LEFT JOIN (
	SELECT DatabaseName
		, TableName
		, SUM(CurrentPerm) AS TableSize
		, MAX(CurrentPerm) * COUNT(*) AS ImpactSize
		, ImpactSize - TableSize AS WastedSize
		, CAST((1.0 - AVG(CurrentPerm) / NULLIFZERO(MAX(CurrentPerm))) AS DECIMAL(4,3)) AS TableSkew
	FROM {dbc.TableSizeV} Z
	GROUP BY 1,2
) Z ON Z.DatabaseName = T.DatabaseName AND Z.TableName = T.TableName

WHERE {where}"""

		order = []
		if opts.group:
			order.append('TableKind')
		if opts.sort:
			if opts.sort == 'name':
				if opts.showdb:
					order.append('T.DatabaseName')
				order.append('T.TableName')
			else:
				order.append({'size': 'Size_', 'time': timecol, 'mtime': 'T.LastAlterTimestamp'}[opts.sort])

		if order:
			def collate(c):
				"generate correct SQL ORDER BY clause"
				desc = c in ['Size_', "T.CreateTimestamp", "T.LastAlterTimestamp"]
				if opts.reverse and c != 'TableKind':
					desc = not desc
				return ' DESC' if desc else ''

			sql += "\nORDER BY " + ', '.join(["{}{}".format(c, collate(c)) for c in order])

		return sql

def args_filter(p):
	"options to filter listing"
	import os.path

	def rel_time(val: str) -> str:
		"relative time like in find linux command"
		import datetime as dt
		val = int(val.lstrip())
		return "{} '{}'".format('>=' if val < 0 else '<', (dt.date.today() - dt.timedelta(days=abs(val))).isoformat())

	def rel_size(val: str):
		"relative size like in find linux command"
		import re

		val = val.lstrip().lower()
		m = re.search(r"(.*)(p|t|g|m|k)b?$", val)
		if m:
			val, sfx = m.groups()
			val = int(val) * 10 ** {'p': 15, 't': 12, 'g': 9, 'm': 6, 'k': 3}[sfx]
		else:
			val = int(float(val))

		def compact(v: int):
			return next((f'{v//10**n}e{n}' for n in [15, 12, 9, 6, 3] if v % 10**n == 0), str(v))

		return "{} {}".format('<' if val < 0 else '>=', compact(abs(val)))

	def rel_pct(val: str):
		"relative skew type"
		val = float(val.lstrip())
		if -1.0 <= val <= 1.0:
			return "{} {}".format('<=' if val <= 0 else '>=', abs(val))
		raise ValueError("Skew must be a fraction between -1.0..+1.0")

	cmd = os.path.split(sys.argv[0])[1]
	kind = {'lstb':'TO', 'lsvw':'V', 'lspr':'PE', 'lsji':'I', 'lsmc':'M', 'lsfn':'ABCFRSL'}.get(cmd)

	# pylint: disable=locally-disabled, bad-whitespace
	g = p.add_argument_group("Filters")
	g.add_argument(      "--type",    type=str.upper,    default=kind,     help="only include TVM entries with specified TableKind")
	g.add_argument("-I", "--hide",    type=DBObjPat,     action='append', metavar='PATTERN',  help="exclude tables that match PATTERN")
	g.add_argument(      "--mtime",   metavar='+N,-N,N', type=rel_time,    help="modify time n*24 hours ago")
	g.add_argument(      "--ctime",   metavar='+N,-N,N', type=rel_time,    help="create time n*24 hours ago")
	g.add_argument(      "--size",    metavar='+N,-N,N', type=rel_size,    help="size more/less than specified")
	g.add_argument(      "--skew",    metavar='+N,-N,N', type=rel_pct,     help="skew more/less than specified")
	g.add_argument(      "--user",                                         help="only display tables created by this user")

def args_display(p):
	"options to format the display"
	g = p.add_argument_group("Display")

	g.add_argument("-D", dest="showdb", action="store_false", help="show just the object name without database prefix")
	x = g.add_mutually_exclusive_group()
	x.add_argument("-i", "--impact", dest="sizecol", action='store_const', const='ImpactSize', default='TableSize', help="use impact size")
	x.add_argument("-w", "--waste", dest="sizecol", action='store_const', const='WastedSize', help="use wasted size")
	g.add_argument("-c", dest='create', action="store_true", help="use create instead of modified time for display/sort")

	from .util import args_size
	args_size(g)

def args_order(p):
	"options to order the listing"
	from .util import args_sort
	g = p.add_argument_group("Ordering")
	g.add_argument("--group", action="store_true", help="group by object type")
	args_sort(g)

def main(args=None):
	"script entry-point"
	return TVM(__name__, __doc__).ls(args)

if __name__ == '__main__':
	sys.exit(main())
