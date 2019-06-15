"Common functions used by show*.py utilities"

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

from typing import List, Any, Optional, Union

from .. import vsch
from .. import util

logger = util.getLogger(__name__)

dbc = vsch.load_schema('dbc')

class Err(Exception):
	"A throwable Error"

class Opt:
	"An option and associated value pair"
	def __init__(self, opt, val=''):
		self.opt, self.val = opt, val

	def __str__(self):
		if isinstance(self.val, int):
			v = next((f'{self.val//10**n}e{n}' for n in [15, 12, 9, 6, 3] if self.val % 10**n == 0), str(self.val)) if self.val else 0
		elif isinstance(self.val, list):
			v = '({})'.format(','.join(str(self.val))) if len(self.val) > 1 else str(self.val[0])
		else:
			v = str(self.val)

		return f'{self.opt}={v}' if v != '' else str(self.opt)

def optstr(ol: List[Opt]) -> str:
	"return non-null options as concated string values that are comma separated"
	return ', '.join(str(o) for o in ol if o.val is not None)

def quote(ident: Union[str, List[str], None]) -> Optional[str]:
	"Return quoted string value, or comma separated list of string value"
	if ident is None:
		return None

	if isinstance(ident, list):
		return "(" + ', '.join([quote(i) for i in ident]) + ")"

	return "'{}'".format(ident.replace("'", "''"))

def execsql(sql: str, msg='SQL') -> List[List[Any]]:
	"log, run SQL and return the resultset as list"
	logger.debug(msg + ':\n' + sql.replace('\t', '  '))
	csr.execute(sql)

	return [[c.rstrip() if isinstance(c, str) else c for c in r] for r in csr.fetchall()]

def mk_pred(names: List[str]) -> str:
	"make SQL predicate clause including operator"
	op = 'Like ' if [o for o in names if '%' in o] else '= '
	if len(names) > 1:
		op += 'Any '
	return op + quote(names)

def mk_opt(tmpl: str, v: Optional[str]):
	"make optional parameter if present"
	return ' ' + tmpl.format(v) if v else ''

def enter(mod, args=None):
	"common entry-point"
	global csr

	try:
		from argparse import ArgumentParser

		p = ArgumentParser(description=mod.__doc__)

		mod.add_args(p)
		util.dbconn_args(p)

		args = p.parse_args(args)

		found = False
		with util.cursor(args) as csr:
			for ddl in mod.genddl(args):
				found = True
				print(ddl)

		return 0 if found else 3

	except Err as msg:
		logger.error(msg)
		return 1
