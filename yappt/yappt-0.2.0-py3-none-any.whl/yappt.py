"Yet another pretty print table"

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2016-2019, Paresh Adhia"

from typing import Type, Optional, Callable, Iterable, Any, List, TextIO, Union, Tuple, TypeVar
from decimal import Decimal
import datetime as dt

T = TypeVar('T')
TableRow = List[Optional[Any]]
TableColumn = Iterable[T]

class HumanInt(int):
	"An int subclass that formats values for human readability (similar to --human-readable option of the ls command)"
	def __format__(self, spec):
		if spec == '':
			width, prec, typ = None, '.1', 'h'
		else:
			import re
			m = re.match(r'(\d*)(.\d+)?(h|s|e)$', spec)
			if not m:
				return int.__format__(self, spec)
			width, prec, typ = m.groups()

		sign, val = ('-', abs(self)) if self < 0 else ('', self)

		if typ == 'e':
			if prec:
				raise ValueError('Precision not allowed in integer format specifier')

			if val == 0:
				s = '0'
			else:
				for e in [12, 9, 6, 3, 0]:
					if val % 10**e == 0:
						break
				s = (str(val // 10**e) + 'e' + str(e)) if e else str(val)

		else:
			num = float(val)
			base = 1000.0 if typ == 's' else 1024.0

			for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']:
				if num < base:
					break
				num /= base

			fmt = ',' + (prec or '.0') + 'f'
			s = format(num, fmt)
			if '.' in s:
				s = s.rstrip('0').rstrip('.')
			s += unit

		s = sign + s

		return s.rjust(int(width)) if width else s

class PPCol:
	"Pretty printer for a column within a table"
	@staticmethod
	def make_fmtval(ctype: type) -> Callable[[Any], str]:
		"make format function based on type"
		if issubclass(ctype, HumanInt):
			return lambda v: HumanInt.__format__(v, '.1h')
		if issubclass(ctype, int):
			return lambda v: format(v, ',d')
		if issubclass(ctype, (float, Decimal)):
			return lambda v: format(v, ',.2f')

		return str

	@staticmethod
	def make_justify(ctype: type) -> Callable[[str], str]:
		"make justify function based on type"
		return str.rjust if issubclass(ctype, (int, float, Decimal, dt.date, dt.datetime, dt.time, dt.timedelta)) else str.ljust

	@staticmethod
	def create(
			col: Union['PPCol', Tuple[str, type], str, Any],
			infer_from: Optional[TableColumn] = None,
			title_encoded: bool = False,
			sizefmt: str = '.1h',
			pctfmt: str = '.1%') -> 'PPCol':
		"""
		create PPCol instance from parameter type.
		Arguments:
		col: can be (col-name, coltype) tuple, or col-name
		infer_from: an optional list of column value to derive column type from
		title_encoded: True if column title contains format characters (see below)
		sizefmt: default format for displaying "size types"
		pctfmt: default format for displaying "% types"

		column title "n" can be encoded with following formatting characters:
		n_ -> HumanInt
		n% -> Fraction displayed as percentage. None: trailing % is not removed from the title
		:n -> Left justified
		n: -> right justified
		:n: -> center aligned

		Note: Except for "%", the encoding symbols are removed from the title name
		"""

		if isinstance(col, PPCol):
			return col

		n, t = col if isinstance(col, tuple) else (col, None)
		if not t and infer_from:
			t = next((type(v) for v in infer_from if v is not None), None)

		f = j = None
		if title_encoded:
			if n.endswith('_'):
				n, f = n[:-1], lambda v: format(HumanInt(v), sizefmt)
			elif n.endswith('%'):
				f = lambda v: format(v, pctfmt)
			elif n.startswith(":") and n.endswith(":"):
				n, j = n[1:-1], str.center
			elif n.startswith(":"):
				n, j = n[1:], str.ljust
			elif n.endswith(":"):
				n, j = n[:-1], str.rjust

		return PPCol(n, ctype=t, fmtval=f, justify=j)

	def __init__(self,
			title: str,
			ctype: Optional[type] = None,
			fmtval: Optional[Callable[[Any], str]] = None,
			justify: Optional[Callable[[str], str]] = None,
			width: int = 1):

		self.title: str = title or ''
		self.width: int = max(width, len(self.title))
		self.fmtval: Callable[[Any], str] = fmtval or (self.make_fmtval(ctype) if ctype else str)
		self._justify: Callable[[str, int], str] = justify or (self.make_justify(ctype) if ctype else str.ljust)

	def justify(self, val: str) -> str:
		"justify value"
		return self._justify(val, self.width)

	def __str__(self):
		return f"{self.title}:{self.width}"

branch_styles = {
	'fancy': {'T': "├─ ", 'L': "└─ ", 'I': "│  ", ' ': "   "}, # uses Unicode codepoints
	'ascii': {'T': "|- ", 'L': "L_ ", 'I': "|  ", ' ': "   "}, # uses only ASCII characters
}
def treeiter(root: T, getch: Callable[[T], Iterable[T]] = lambda n: n.children, style: str = 'fancy') -> Iterable[Tuple[str, T]]:
	"""
	generates a pair (trunk, node) using supplied function to iterate over starting node (root)
	where elem is element of any type that can be iterated over using getch function and,
	getch is a function that returns an iterable of elements that are children or descendents of given node
	trunk is tree's current trunk at that element
	style can be either 'fancy' (default) or 'ascii' used for building "trunk"
	"""
	def extend(trunk, by):
		"extend the trunk by a new brach"
		return trunk.replace('L', ' ').replace('T', 'I') + by

	def lpos_iter(in_iter):
		"an iterator which returns tuple (lpos, item) where lpos is True if this is the last item from the original iterator"
		has_prev, prev = False, None
		for child in in_iter:
			if has_prev:
				yield False, prev
			has_prev, prev = True, child
		if has_prev:
			yield True, prev

	def walk(node, trunk):
		"Visits node and its children in order"
		yield (trunk, node)
		for is_last, child in lpos_iter(getch(node)):
			yield from walk(child, extend(trunk, 'L' if is_last else 'T'))

	def stylize(trunk):
		"stylize the trunk if style is not None"
		return trunk if style is None else ''.join(branch_styles[style][c] for c in trunk)

	for trunk, node in walk(root, ''):
		yield (stylize(trunk), node)

def formatted(
		rows: Iterable[TableRow],
		columns: Optional[List[str]] = None,
		none_value: str = '',
		dash: str = '-',
		title_encoded: bool = False) -> Iterable[List[str]]:
	"return formatted rows. Inspired by https://bitbucket.org/astanin/python-formatted"

	table = [list(r) for r in zip(*rows)]  # transpose
	if not table and not columns:
		return
	if columns:
		if table:
			if len(columns) != len(table):
				raise ValueError('Number of columns in data must match column definitions')
			columns = [PPCol.create(c, v, title_encoded=title_encoded) for c, v in zip(columns, table)]
		else:
			columns = [PPCol.create(c, title_encoded=title_encoded) for c in columns]
	else:
		columns = [PPCol.create('', v) for v in table]

	# stage 1: transform table values to formatted string
	table = [[c.fmtval(v) if v != None else none_value for v in vals] for c, vals in zip(columns, table)]

	# adjust max width, if needed, before the second stage
	for col, w in zip(columns, [max(len(v) for v in vals) for vals in table]):
		if w > col.width:
			col.width = w

	# stage 2: justify table values
	table = [[c.justify(v) for v in vals] for c, vals in zip(columns, table)]

	if [c.title for c in columns if c.title]: # print column titles if at least one is non-blank
		yield [c.justify(c.title) for c in columns]
		if dash:
			yield [''.ljust(c.width, dash) for c in columns]

	yield from zip(*table) # transform table to rows

def tabulate(
		rows: Iterable[TableRow],
		columns: Optional[List[str]] = None,
		sep: str = ' ',
		end: str = '\n',
		none_value: str = '',
		dash: str = '-',
		title_encoded: bool = False) -> str:
	"format and return table as a string"
	return end.join(sep.join(row) for row in formatted(rows, columns, none_value=none_value, dash=dash, title_encoded=title_encoded))

def pprint(
		rows: Iterable[TableRow],
		columns: Optional[List[str]] = None,
		sep: str = ' ',
		end: str = '\n',
		none_value: str = '',
		dash: str = '-',
		title_encoded: bool = False,
		file: Optional[TextIO] = None,
		flush: bool = False) -> None:
	"print formatted tabular data"
	print(tabulate(rows, columns, sep=sep, end=end, none_value=none_value, dash=dash, title_encoded=title_encoded), file=file, flush=flush)
