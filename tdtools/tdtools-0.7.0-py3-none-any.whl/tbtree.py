#! /usr/bin/env python
"List all views that reference the given tables"

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2017, Paresh Adhia"

from typing import Iterable, Optional, List
import tdtypes as td

logger = td.getLogger(__name__)

class View:
	"View with reference to parent and list of children"
	def __init__(self, parent: Optional['View'], db: Optional[str], vw: Optional[str]):
		self.parent: 'View' = parent
		self.db: str = db
		self.vw: str = vw
		self.children = []

	def __str__(self):
		return self.db+'.'+self.vw

def main(args: Optional[List[str]] = None) -> None:
	"script entry-point"
	import argparse
	from .updviewrefs import DFLT_REFTB

	def depth(v: str) -> int:
		"assert: depth must be a +ve integer"
		if int(v) <= 0:
			raise argparse.ArgumentTypeError("Must be a positive integer value")
		return int(v)

	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('table', metavar='TBL', type=td.DBObjPat, nargs='+', help=td.DBObjPat.__doc__)
	parser.add_argument('--reftb', metavar='TBL', default=DFLT_REFTB, help=f'table containing static view reference data (default: {DFLT_REFTB})')
	parser.add_argument('--max-depth', metavar='INT', type=depth, default=0, help='Limit maximum depth of traversals for dependency search')
	args = parser.parse_args(args)

	with td.cursor(args) as csr:
		print_tree(csr, args.table, args.reftb, args.max_depth)

def print_tree(csr, tables: Iterable[td.DBObjPat], reftb: str = 'SysDBA.ViewRefs', max_depth: int = 0) -> int:
	"print table dependecy tree using pre-populated reftb table"
	from yappt import treeiter

	err = None
	try:
		csr.execute(build_sql(tables, reftb=reftb, max_depth=max_depth))
	except td.sqlcsr.Error as e:
		err = str(e)
	if err:
		raise SystemExit(f'Table {reftb} does not exist (SQLCODE=3807)' if '3807' in err else err)

	for tree in build_trees(csr.fetchall()):
		for pfx, node in treeiter(tree):
			print(str(pfx)+str(node))

def build_sql(tab_p: Iterable[td.DBObjPat], reftb: str = 'SysDBA.ViewRefs', max_depth: int = 0) -> str:
	"SQL query to obtain descendants of all matching objects"

	pred = '\n\t\t  OR '.join(p.search_cond() for p in tab_p)
	pred_depth = f"\n\t\tAND p.Depth <= {max_depth}" if max_depth else ""

	sql = f"""\
WITH RECURSIVE descendants AS (
	SELECT DatabaseName c_db, TableName c_name
		, c_db || '.' || c_name  VwPath
		, 1 as Depth
	FROM dbc.TablesV
	WHERE TableKind in ('T', 'O', 'V')
		AND ({pred})

	UNION ALL

	SELECT c.ViewDB, c.ViewName
		, VwPath || '>' || c.ViewDB || '.' || c.ViewName
		, Depth+1 AS Depth
	FROM {reftb} c
		, descendants p
	WHERE p.c_db = c.RefDB
		AND p.c_name = c.RefName{pred_depth}
)

SELECT c_db, c_name
	, Depth
FROM descendants
ORDER BY VwPath"""

	logger.debug('SQL =>\n%s', sql.replace('\t', '    '))
	return sql

def build_trees(rows) -> List[View]:
	"build hierarchical tree using the depth information"

	forest = View(None, None, None)
	prev_level = 0
	parent = None

	for db, vw, level in rows:
		if level > prev_level:
			parent = parent.children[-1] if parent else forest
		else:
			while prev_level > level:
				parent = parent.parent
				prev_level -= 1

		node = View(parent, db, vw)

		if parent:
			parent.children.append(node)
		else:
			forest = node

		prev_level = level

	return forest.children

if __name__ == '__main__':
	main()
