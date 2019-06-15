#! /usr/bin/env python
"List Teradata view dependecies"

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

from typing import List, Optional
import tdtypes as td
from . import util

logger = util.getLogger(__name__)

def main(args: Optional[List[str]] = None) -> None:
	"script entrypoint"
	import argparse

	p = argparse.ArgumentParser(description=__doc__)
	p.add_argument("names", metavar='VIEW', type=td.DBObjPat, nargs='+', help="View name or pattern (eg dbc.qry%% dbc.tablesv)")
	util.dbconn_args(p)

	args = p.parse_args(args)

	with td.cursor(args) as csr:
		if csr.version < "14.10":
			raise SystemExit('This script only works with Teradata versions 14.10 or later')

		vwlist: List[td.View] = td.DBObjPat.findall(args.names, objtypes='V', warn_notfound=False, csr=csr)
		if not vwlist:
			raise SystemExit(3)
		display(vwlist)

def display(vwlist: List[td.View]) -> None:
	"display view and dependencies as a tree"
	from yappt import treeiter

	for vw in vwlist:
		try:
			for pfx, node in treeiter(vw, getch=lambda v: v.refs if isinstance(v, td.View) else []):
				print(str(pfx) + str(node))
		except td.sqlcsr.DatabaseError as err:
			logger.error("Couldn't get referenced objects for %s: %s", vw, err)

if __name__ == '__main__':
	main()
