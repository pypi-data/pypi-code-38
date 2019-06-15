"""Python Class that represents an "evolutionary schema". Class attributes
return either table with the same name or a table expressions"""

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

from lazy import lazy

class VSchema:
	"Virtual schema that contains table or table expressions adjusted for specific version"
	def __init__(self, sch, sch_hist, version=None):
		self.sch, self.sch_hist, self._version = sch, sch_hist, version

	@lazy
	def version(self):
		"base version to which future columns are derived"
		from tdtypes.sqlcsr import csr
		return self._version or csr.version

	def __getattr__(self, table):
		"Return either table, or derived table expression"
		if table not in self.sch_hist:    # table doesn't have any derived columns
			return f"{self.sch}.{table}"

		# pick up derived column expression that relatively in future to the specified version
		vcols = [cols for hist in self.sch_hist[table] for ver, cols in hist.items() if ver > self.versioin]

		if vcols:
			colexpr = ', '.join(['{} AS {}'.format(v, k) for cmap in vcols for k, v in cmap.items()])
			return '(SELECT _T.*, {} FROM {}.{} AS _T)'.format(colexpr, self.sch, table)

		return f"{self.sch}.{table}"

def load_schema(schema):
	from .util import load_json
	return VSchema(schema, load_json(schema+'.json'))
