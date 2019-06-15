#! /usr/bin/env python
"Wrapper around Teradata's SHOW command"

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

import sys
import os
import os.path as p

from itertools import groupby
import tdtypes as td

from .util import * # pylint: disable=locally-disabled, wildcard-import, unused-wildcard-import

obj_t = {
	'T': 'Table',
	'O': 'Table',
	'V': 'View',
	'C': 'Temporary Table',
	'I': 'Join Index',
	'G': 'Trigger',
	'M': 'Macro',
	'F': 'Specific Function',
	'S': 'Function',
	'R': 'Function',
	'P': 'Procedure',
	'E': 'Procedure'
}

def add_args(argp):
	"Add arguments to the passed parser"
	from datetime import datetime

	ArgDate = lambda d: datetime.strptime(d, '%Y-%m-%d')
	kinds = ','.join(sorted(obj_t))

	argp.add_argument("filter", metavar='TVM', type=td.DBObjPat, nargs='+', help="a database object")

	argp.add_argument("-t", '--type', metavar='KIND', choices=obj_t, dest="types", action='append', help=f"limit objects to selected types ({kinds})")
	argp.add_argument("-I", "--hide", type=td.DBObjPat, action='append', metavar='PATTERN',  help="exclude tables that match PATTERN")
	argp.add_argument('--show-db', action='store_true', help="generate DDL to set default database")
	argp.add_argument('--no-stats', dest='stats', action='store_false', help="do not generate stats defintions for table and JI")
	argp.add_argument('--since', metavar='YYYY-MM-DD', type=ArgDate, help="only consider objects ALTERed since the given date")
	argp.add_argument('--before', metavar='YYYY-MM-DD', type=ArgDate, help="only consider objects ALTERed before the given date")
	argp.add_argument('-w', '--write', action='store_true', help='create a file for each database object')

def genddl(args):
	"DDL generator"
	for _, grp1 in groupby(getobjs(args.filter, args.types, args.since, args.before, args.hide), key=lambda o: o.objtype):
		for db, grp2 in groupby(grp1, key=lambda o: o.sch):
			if args.show_db:
				yield '\nDatabase {0};\n'.format(db)
			for o in grp2:
				try:
					yield obj_ddl(o, args.write, args.stats)
				except td.sqlcsr.Error as msg:
					logger.warning("Skipped {}, error:{}'".format(o, msg))

def getobjs(objects, types, since=None, before=None, hide=None):
	"return object lists based on passed criteria"
	def preds():
		"generate predicates based on the parameters"
		def obj_pred(objects):
			objs = '\n    OR  '.join(o.search_cond(db='T.DatabaseName', tb='T.TableName') for o in objects)
			return "(" + objs + ")" if len(objects) > 1 else objs

		yield obj_pred(objects)
		if hide:
			yield f"NOT ({obj_pred(hide)})"
		if types:
			yield f"TableKind IN {quote(types)}"
		if since:
			yield f"LastAlterTimestamp >= CAST('{since.isoformat()}' AS TIMESTAMP(0))"
		if before:
			yield f"LastAlterTimestamp <  CAST('{before.isoformat()}' AS TIMESTAMP(0))"

	where = "\n   AND ".join(preds())

	sql = f"""\
SELECT T.DatabaseName,
    COALESCE(F.SpecificName, T.TableName),
    T.TableKind
FROM {dbc.TablesV} T
LEFT JOIN {dbc.FunctionsV} F ON F.DatabaseName = T.DatabaseName AND F.FunctionName = T.TableName
WHERE {where}
ORDER BY
	CASE TableKind
		WHEN 'T' THEN 0
		WHEN 'O' THEN 0
		WHEN 'C' THEN 0
		WHEN 'G' THEN 1
		WHEN 'I' THEN 2
		WHEN 'V' THEN 3
		ELSE 4
	END,
	CreateTimestamp"""

	return [td.DBObj.create(db, ob, k.rstrip()) for db, ob, k in execsql(sql, 'Object list SQL')]

def obj_ddl(obj, write, stats):
	"Object DDL generator"
	def show(sql):
		"return cleansed DDL"
		return ''.join([l[0].replace('\r', '\n') for l in execsql('SHOW ' + sql)]).rstrip().rstrip(';') + ';'

	if obj.objtype in obj_t:
		ddl = show('{} "{}"."{}"'.format(obj_t[obj.objtype], obj.sch, obj.name))
	else:
		logger.error('SHOW command is not supported for {}'.format(obj))
		return ''

	if stats and obj.objtype in ['T', 'O', 'N', 'I']:
		try:
			ddl += '\n\n' + show('STATS ON "{}"."{}"'.format(obj.sch, obj.name))
		except td.sqlcsr.Warning:
			logger.info('SHOW STATS ON {} failed.'.format(str(obj)))

	if write:
		mk_dbfolder(obj.sch)
		fname = p.join(obj.sch, obj.name + '.' + {'P':'sp'}.get(obj.objtype, 'sql'))
		logger.debug('Writing DDL of "{}" to "{}"'.format(obj, fname))
		with open(fname, 'w') as out:
			print(ddl, file=out)
		return '.{} file={}'.format('compile' if obj.objtype == 'P' else 'run', fname)

	else:
		return ddl + '\n'

folders = set()
def mk_dbfolder(db):
	"Create a folder with same name as DATABASE"
	if db in folders:
		return

	if not p.exists(db):
		os.mkdir(db)
	elif not p.isdir(db):
		raise Err('[{}] exists and is not a directory'.format(db))

	folders.add(db)

def main(args=None):
	"script entry-point"
	return enter(sys.modules[__name__], args)

if __name__ == '__main__':
	sys.exit(main())
