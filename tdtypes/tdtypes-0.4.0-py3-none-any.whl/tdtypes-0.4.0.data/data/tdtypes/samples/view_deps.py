#! /usr/bin/env python
"Sample script to list view dependencies"

from argparse import ArgumentParser
import tdtypes as td

p = ArgumentParser(description="Print view dependecies")
p.add_argument("view", type=td.DBObjPat, nargs='+', help="View name, e.g. DBC.DatabasesVX")
p.add_argument("--tdconn", help="Teradata connection JSON string")

args = p.parse_args()

def print_dep(v, indent=''):
	print(indent+str(v))
	if isinstance(v, td.View):
		for r in v.refs:
			print_dep(r, indent+'  ')

with td.cursor(args.tdconn) as csr:
	for v in td.DBObjPat.findall(args.view, objtypes='V', csr=csr):
		print_dep(v)
