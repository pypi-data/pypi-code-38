"Common functions used by show*.py utilities"

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

from argparse import ArgumentParser
from typing import List, Iterable, Callable, Tuple, Optional

import tdtypes as td
from .. import vsch
from .. import util

dbc = vsch.load_schema('dbc')

def args_size(p: ArgumentParser) -> None:
	"add size args"
	x = p.add_mutually_exclusive_group()
	x.add_argument("-h", "--human-readable", dest='sizefmt', action="store_const", const='.1h', default='.1h',
		help="print human readable sizes (e.g., 1K 234M 2G)")
	x.add_argument("--si", dest='sizefmt', action="store_const", const='.1s', help="like -h but use powers of 1000 instead of 1024")
	x.add_argument("-b", "--bytes", dest='sizefmt', action="store_const", const=',d', help="print size in number of bytes")

def args_misc(p: ArgumentParser) -> None:
	"add misc args"
	g = p.add_argument_group("Miscellaneous")
	x = g.add_mutually_exclusive_group()
	x.add_argument('-v', '-l', '--verbose', default=1, action='count', help='print verbose output. Use -vv for more details')
	x.add_argument('-1', action='store_const', const=0, dest='verbose', help='print only names')
	g.add_argument('--help', action='help', help='show this help message and exit')
	util.dbconn_args(g)

def args_sort(p: ArgumentParser) -> None:
	"add ordering results args"
	x = p.add_mutually_exclusive_group()
	x.add_argument('--sort', metavar='WORD', default='name', choices=['none', 'size', 'name', 'time'],
		help="sort by WORD instead of name: none (-U), size (-S), time (-t)")
	x.add_argument("-t", dest='sort', action='store_const', const='mtime', help="sort by time, newest first")
	x.add_argument("-U", dest='sort', action='store_const', const='none', help="do not sort; list entries in database order")
	x.add_argument("-S", dest='sort', action='store_const', const='size', help="sort by size, largest first")
	p.add_argument("-r", "--reverse", action="store_true", help="reverse order while sorting")

class Listing:
	"Information listing"
	def __init__(self, name: str, doc: str):
		self.logger = util.getLogger(name)
		self.p = ArgumentParser(description=doc, fromfile_prefix_chars='@', add_help=False)

	def select(self, args) -> str:
		"columns for SELECT clause"
		return '\n\t, '.join(f'{expr} AS "{name}"' for (expr, name) in self.cols(args))

	def ls(self, args: Optional[List[str]] = None) -> int:
		"script entry-point"
		for fn in self.user_args():
			fn(self.p)
		args_misc(self.p)

		args = self.p.parse_args(args)

		with td.cursor(args) as csr:
			sql = self.build_sql(args.names, args)
			self.logger.debug('SQL =>\n%s;', sql.replace('\t', '    '))

			csr.execute(sql)
			if csr.rowcount == 0:
				return 3

			if len(csr.description) > 1:
				util.pprint_csr(csr, sizefmt=getattr(args, 'sizefmt', '.1h'))
			else:
				for c, in csr.fetchall():
					print(c)

		return 0

	def user_args(self) -> Iterable[Callable[[ArgumentParser], None]]:
		"returns a list of functions that will add arguments in to passed argparse Parser object"
		return []

	def build_sql(self, names: List[str], opts) -> str:
		"build SQL based on run-time options"
		raise NotImplementedError()

	def cols(self, opts) -> Iterable[Tuple[str, str]]:
		"columns that are to be part of the SELECT clause"
		return []
