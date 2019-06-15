"tdtools utility functions"

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

from typing import Optional
from logging import Logger
from tdtypes.sqlcsr import *

def load_json(resource):
	import json
	from pkg_resources import resource_filename

	with open(resource_filename(__name__, resource), 'r') as jsonf:
		return json.load(jsonf)

def getLogger(name: Optional[str]) -> Logger:
	import tdtypes as td

	td.getLogger('tdtools')
	return td.getLogger(name)

def pprint_csr(csr: EnhancedCursor, limit: int = 0, sizefmt: str = '.1h', pctfmt: str = '.1%', sql: Optional[str] = None) -> None:
	"""
	pretty print cursor resultset in formatted tabular form.
	Values are fomatted appropriately for their types, except when column names end with
	- _ (underscore) are formatted as human-readable sizes (_ is removed for column heading)
	- % are formatted as percentage
	Column names are turned into column headers, after removing a trailing _ if any
	"""
	import yappt

	if limit:
		def data():
			"generate rows up to limit specified"
			def rows():
				"return row at a time until exhausted"
				r = csr.fetchone()
				while r is not None:
					yield r
					r = csr.fetchone()
			yield from (r for e, r in enumerate(rows()) if e < limit)
	else:
		data = csr.fetchall

	if sql:
		csr.execute(sql)

	def Col(d):
		return yappt.PPCol.create((d[0], d[1]), title_encoded=True, sizefmt=sizefmt, pctfmt=pctfmt)

	return yappt.pprint(data(), columns=[Col(d) for d in csr.description], sep='  ')

try:
	dbconn_args # test if a custom function is defined
except NameError:
	from argparse import ArgumentParser
	def dbconn_args(parser: ArgumentParser) -> None:
		"""
		Placeholder function, when overriden allows database connection information to be supplied via command-line.
		database connection information via command line option.
		- tdconn_site.py must include dbconn_args() function that accepts
		argparse.ArgumentParser object and adds required argument(s).
		- And, dbconnect() function that will be passed output of ArgumentParser.parse_args()
		"""
