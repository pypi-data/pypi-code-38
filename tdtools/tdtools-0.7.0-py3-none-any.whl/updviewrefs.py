#! /usr/bin/env python
"View Reference Table maintenance"

from typing import List, Tuple, Optional
import tdtypes as td
from tdtools.util import getLogger

DFLT_REFTB = "SysDBA.ViewRefs"

logger = getLogger(__name__)

def main(args: Optional[List[str]] = None) -> None:
	"script entry-point"
	import argparse
	from . import util

	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('-t', '--reftb', metavar='TBL', default=DFLT_REFTB, help=f'table for storing view reference data (default: {DFLT_REFTB})')
	parser.add_argument('--ddl', action='store_true', help='Show DDL for creating a new table to store static references')
	parser.add_argument('views', type=td.DBObjPat, nargs='*', help="Optional list of views (wildcard allowed) to refresh (default all)")
	util.dbconn_args(parser)

	args = parser.parse_args(args)

	if args.ddl:
		print(get_ddl(args.reftb) + ';')
	else:
		with td.cursor(args) as csr:
			try:
				print("{:,d} rows added, {:,d} rows removed, {:,d} rows orphaned".format(*refresh(args.views, csr=csr, reftb=args.reftb)))
			except td.sqlcsr.DatabaseError as err:
				raise SystemExit(str(err))

def get_ddl(reftb: str) -> None:
	"print DDL for storing static view reference info needed for reverse lookup"
	return f"""\
CREATE TABLE {reftb}
( ViewDB    varchar(128) character set unicode not null
, ViewName  varchar(128) character set unicode not null
, ViewUpdTS Timestamp(0) not null
, RefDB     varchar(128) character set unicode
, RefName   varchar(128) character set unicode
) PRIMARY INDEX(ViewDB,ViewName)"""

def refresh(view_filters: List[td.DBObjPat], csr: td.sqlcsr.EnhancedCursor, reftb: str = DFLT_REFTB) -> Tuple[int, int, int]:
	"refresh static reftb with views that were altered since last they were evaluated"
	if view_filters:
		ref_filter = "\n\tAND (" + '\n\t\t  OR '.join(p.search_cond(db='ViewDB', tb='ViewName') for p in view_filters) + ")"
		dbc_filter = "\n\tAND (" + '\n\t\t  OR '.join(p.search_cond() for p in view_filters) + ")"
	else:
		ref_filter = dbc_filter = ""

	def runsql(sql, parms=None):
		if parms is None:
			csr.execute(sql)
		else:
			csr.executemany(sql, parms)
		rowc = csr.rowcount
		logger.debug("%d rows affected\n> %s\n", rowc, sql.replace('\t', '    ').replace('\n', '\n> '))
		return rowc

	# remove views that no longer exists or were altered past last time
	removed = runsql(f"""\
DELETE
FROM {reftb} R
WHERE NOT EXISTS (
			SELECT 1
			FROM dbc.TablesV V
			WHERE V.DatabaseName = R.ViewDB
				AND V.TableName = R.ViewName
				AND V.TableKind = 'V'
				AND V.LastAlterTimestamp <= R.ViewUpdTS
		){ref_filter}""")

	# set parent dependencies to NULL for child views whose parent objects were removed
	orphaned = runsql(f"""\
UPDATE {reftb} R
SET RefDB = NULL, RefName = NULL
WHERE RefDB IS NOT NULL
	AND NOT EXISTS (
			SELECT 1
			FROM dbc.TablesV V
			WHERE V.DatabaseName = R.RefDB
				AND V.TableName = R.RefName
		){ref_filter}""")

	# find new views for inclusion
	runsql(f"""\
SELECT DatabaseName
	, TableName
	, LastAlterTimestamp
FROM dbc.TablesV V
WHERE TableKind = 'V'{dbc_filter}
	AND NOT EXISTS (
			SELECT 1
			FROM {reftb} R
			WHERE V.DatabaseName = R.ViewDB
				AND V.TableName = R.ViewName
		)""")

	def vdeps(db, vw) -> List[Tuple[str, str]]:
		try:
			return [(r.sch, r.name) for r in td.View(db, vw, csr.get_xmldef).refs] or [(None, None)]
		except td.sqlcsr.DatabaseError:
			logger.error("Unable to obtain referenced objects for '%s.%s'", db, vw)
			return [(None, None)]

	refs = [(db, vw, ts, rdb, rob) for db, vw, ts in csr.fetchall() for (rdb, rob) in vdeps(db, vw)]
	if refs:
		runsql(f"INSERT INTO {reftb} (ViewDB,ViewName,ViewUpdTS,RefDB,RefName) VALUES(?,?,?,?,?)", refs)

	return (len(refs), removed, orphaned)

if __name__ == '__main__':
	main()
