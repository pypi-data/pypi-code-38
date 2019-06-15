#! /usr/bin/env python
"Sample script to print PI columns"

from argparse import ArgumentParser
import tdtypes as td

p = ArgumentParser(description="Print Primary Index columns")
p.add_argument("table", type=td.DBObjPat, nargs='+', help="Table name, e.g. DBC.TVM")
p.add_argument("--tdconn", help="Teradata connection JSON string")

args = p.parse_args()

with td.cursor(args.tdconn) as csr:
	for tb in td.DBObjPat.findall(args.table, objtypes='T', csr=csr):
		print(tb, '->', ','.join(c.name for c in tb.pi_cols))
