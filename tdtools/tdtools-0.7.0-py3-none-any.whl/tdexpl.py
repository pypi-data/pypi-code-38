#! /usr/bin/env python
# -*- coding: utf8 -*-
"Print concise Teradata explain plan report"

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

from typing import Dict, Tuple, Iterator, Iterable, Optional
import xml.etree.ElementTree as ET

from yappt import tabulate, treeiter, PPCol
from . import util

logger = util.getLogger(__name__)

class TableLike:
	"A database object that stores data, optionally built using one or more children"
	def __init__(self):
		self.parent, self.children = None, []

class TV(TableLike):
	"Base class to represent user query-able, permanent database object"
	def __init__(self, sch: str, name: str, rows: Optional[str] = None):
		super().__init__()
		self.sch, self.name, self.rows, self.lock = sch, name, int(rows) if rows else None, None

	def __str__(self):
		return self.sch + "." + self.name

class Table(TV):
	"Tag class for a database table"

class View(TV):
	"Tag class for a database view"

class Spool(TableLike):
	"A temporary object that stores intermediate results of an intermediate database operation"
	maxdigits = 1

	def __init__(self, num: str, conf: Optional[str] = None, rows: Optional[str] = None):
		super().__init__()
		self.num, self.conf, self.rows, self.step = int(num), conf, int(rows) if rows is not None else None, None
		Spool.maxdigits = max(Spool.maxdigits, len(str(self.num)))

	def __str__(self):
		return f'Spool#{self.num:0{self.maxdigits}}'

class InList(TableLike):
	"A literal list of values represented as table"
	def __init__(self, numvals):
		super().__init__()
		self.numvals = numvals

	def __str__(self):
		return f'InList[{self.numvals}]'

class Index:
	"An Index"
	def __init__(self, xe):
		self.num = xe.attrib['IndexNum']
		self.uniq = xe.attrib.get('UniqueFlag', 'false') == 'true'
		self.type = {
			"Hash Ordered Secondary Covering": 'HI-Cover',
			"Primary Key": 'PKey',
			"Value Ordered Secondary": 'VOSI',
			"Nonpartitioned Primary": 'PI',
			"Partitioned Primary": 'PPI',
			"Secondary": 'SI',
			"Unique Constraint": 'Uniq',
			"Value Ordered Secondary Covering": 'VOSI-Cover',
			"Spatial": 'Spatial'}[xe.attrib['IndexType']]

	def __str__(self):
		return self.type

class Lock:
	"Lock attributes"
	def __init__(self, objx: ET.Element, severity: str, level: str):
		self.severity: str = severity
		self.level: str = level
		if objx.tag == 'RelationRef':
			self.obj: TableLike = objlist[objx.attrib['Ref']]
			self.obj.lock = severity
		else:
			raise RuntimeError(f'{objx.tag} is unknown tag for locking')

	def __str__(self):
		return f'{self.obj}:{self.level}:{self.severity}'

class Source:
	"Represents input to a database step"
	def __init__(self, xe: ET.Element):
		self.pos = int(xe.attrib['AccessPosition'])
		self.obj = self.parts = self.pred = self.IX = None

		# pylint: disable=locally-disabled, bad-whitespace, multiple-statements
		for c in xe:
			if   c.tag == 'SpoolRef':    self.obj   = objlist[c.attrib['Ref']]
			elif c.tag == 'RelationRef': self.obj   = objlist[c.attrib['Ref']]
			elif c.tag == 'IndexRef':    self.IX    = objlist[c.attrib['Ref']]
			elif c.tag == 'IN-List':     self.obj   = InList(c.attrib['NumValues'])
			elif c.tag == 'PPIAccess':   self.parts = int(c.attrib['TotalParts'])
			elif c.tag == 'Predicate':   self.pred  = c.attrib['PredicateKind']

	def __str__(self):
		s = str(self.obj)
		if self.IX:
			s += ':'+str(self.IX)
		if self.parts and self.parts < 1000000: # more than million partition isn't very useful info
			s += f'[{self.parts}]'
		if self.pred:
			s += ':' + self.pred
		return s

class Target:
	"Represents output of a database step"
	def __init__(self, xe):
		geo = xe.attrib.get('GeogInfo', '')
		self.geo = {'Duplicated': 'Dupl', 'Hash Distributed': 'Redist'}.get(geo, geo)
		self.sort = None
		for c in xe:
			# pylint: disable=locally-disabled, bad-whitespace, multiple-statements
			if   c.tag == 'SpoolRef':    self.obj = objlist[c.attrib['Ref']]
			elif c.tag == 'RelationRef': self.obj = objlist[c.attrib['Ref']]
			elif c.tag == 'SortKey':     self.sort = c.attrib['SortKind']

	def __str__(self):
		return self.geo

class StepNum:
	"Level 1 and Level 2 step numbers"
	dig_1 = 1
	dig_2 = 0

	def __init__(self, xe: ET.Element):
		def digits(num):
			return 3 if num > 99 else 2 if num > 9 else 1 if num > 0 else 0

		self._1 = int(xe.attrib['StepLev1Num'])
		self._2 = int(xe.attrib['StepLev2Num']) if xe.attrib['QCFParallelKind'] != 'Sequential' else 0
		StepNum.dig_1 = max(StepNum.dig_1, digits(self._1))
		StepNum.dig_2 = max(StepNum.dig_2, digits(self._2))

	def __str__(self):
		s = format(self._1, str(self.dig_1))
		if self.dig_2:
			s += f'.{self._2:0{self.dig_2}d}' if self._2 else ' '*(self.dig_2+1)
		return s

	@classmethod
	def ppfmt(cls):
		"return pretty print column information"
		return PPCol('Step', width=(StepNum.dig_1 + StepNum.dig_2 + (1 if StepNum.dig_2 else 0)), justify=str.rjust)

class Step:
	"An individual step in database query plan"
	def __init__(self, xe: ET.Element):
		self.num = StepNum(xe)
		self._op = xe.find('StepDetails')[0].tag if xe.find('StepDetails') is not None else xe.attrib['QCFStepKind']

		self.amps = self.rows = self.time = self.tgt = self.pred = None
		self.src = []

		for c in xe:
			# pylint: disable=locally-disabled, bad-whitespace, multiple-statements
			if   c.tag == 'AmpStepUsage': self.amps = c.attrib['QCFAmpUsage']
			elif c.tag == 'SourceAccess': self.src.append(Source(c))
			elif c.tag == 'TargetStore':  self.tgt = Target(c)
			elif c.tag == 'Predicate':    self.pred = c.attrib['PredicateKind']
			elif c.tag == 'OptStepEst':
				if c.attrib.get('EstRowCount'): self.rows = int(c.attrib['EstRowCount'])
				if c.attrib.get('EstProcTime'): self.time = float(c.attrib['EstProcTime'])

		self.src.sort(key=lambda s: s.pos)

		if self.tgt:
			self.tgt.obj.step = self
			self.tgt.obj.children.extend([s.obj for s in self.src])
			for s in self.src:
				s.obj.parent = self.tgt.obj

	@property
	def op(self) -> str:
		"operator name"
		return self._op + (', '+self.pred if self.pred else '')

	def operands(self) -> str:
		"operands on which the operator acts during the step"
		if self.src is None:
			return ''
		return '[{}] -> {}'.format(', '.join([str(s) for s in self.src]), self.tgt or 'Dispatcher')

	def __str__(self):
		return f'Step#{self.num} {self.op:6} {self.operands()}'

	@staticmethod
	def fromxml(xe: ET.Element) -> 'Step':
		"instantiate from XML element"
		detail = xe.find('StepDetails')
		kind = xe.attrib['QCFStepKind']

		if detail is None:
			StepType = {'SR': SpoolStep}.get(kind, Step)
		else:
			StepType = {'JIN':JoinStep, 'MLK':LockStep, 'SUM':SumStep}.get(detail[0].tag, Step)

		return StepType(xe)

class SpoolStep(Step):
	"A step that creates (or returns) spool"
	@property
	def op(self):
		if self.pred:
			return self.pred
		if self.tgt is None:
			return 'Return'
		return self.tgt.geo

class SumStep(Step):
	"An aggregation step"
	@property
	def op(self):
		return 'Sum'

class JoinStep(Step):
	"A join step"
	def __init__(self, xe: ET.Element):
		super().__init__(xe)

		detail = xe.find('StepDetails/JIN')
		self.jtyp, self.jkind = detail.attrib['JoinType'], JoinStep._abbreviate(detail.attrib['JoinKind'])

	@staticmethod
	def _abbreviate(phrase: str) -> str:
		"return words replaced with abbreviations"
		subs = [
			('Hash Join', 'HJ'),
			('Merge Join', 'MJ'),
			('Product Join', 'PJ'),
			(' Join', '-J'),
			('Product', 'Prod'),
			('Inclusion ', '+'),
			('Exclusion ', '-'),
			('Dynamic ', 'D-'),
			('Correlated', 'Corr')
		]
		for word, abbr in subs:
			if word in phrase:
				phrase = phrase.replace(word, abbr)

		return phrase

	@property
	def op(self) -> str:
		return self.jkind

class LockStep(Step):
	"A step that takes a database lock"
	def __init__(self, xe: ET.Element):
		super().__init__(xe)
		self.locks = []

		for l in xe.findall('StepDetails/MLK/LockOperation'):
			for t in l:
				self.locks.append(Lock(t, l.attrib['LockSeverity'], l.attrib['LockLevel']))

	@property
	def op(self) -> str:
		return 'Lock'

objlist: Dict[str, TableLike] = {}

def main():
	"script entry-point"
	args = getargs()

	xml = sql = None
	if args.query:
		sql = args.inp
	else:
		try:
			if args.xml:
				import re
				with open(args.inp, 'r') as f:
					xml = re.sub('xmlns=".*?"', '', re.sub('encoding="UTF-16"', 'encoding="utf-8"', f.read(), 1, flags=re.IGNORECASE), 1)
			else:
				with open(args.inp, 'r') as f:
					sql = '\n'.join(l for l in f.read().split('\n') if not l.startswith('-')).strip()
		except IOError:
			logger.error('Could not open [%s] for reading', args.inp)
			return 1

	if not xml:
		with util.cursor(args) as csr:
			try:
				logger.debug('EXPLAIN IN XML NODDLTEXT %s', sql)
				csr.execute('EXPLAIN IN XML NODDLTEXT ' + sql)
			except util.DatabaseError as msg:
				logger.error(msg)
				return 1
			xml = csr.fetchxml()

	root = ET.fromstring(xml)
	objlist.update((n, o) for db in root.findall('Query/ObjectDefs/*') for n, o in get_objs(db))
	steps = list(Step.fromxml(e) for e in root.findall('Query/Plan/*'))

	if args.steps:
		print_steps(steps)
		print()

	print_tree(filter(lambda tb: isinstance(tb, TableLike) and tb.parent is None, objlist.values()))

	if args.tables or args.spool:
		lines = []
		if args.tables:
			lines.extend(sorted([(tb.name, tb.sch, tb.rows, tb.lock) for tb in objlist.values() if isinstance(tb, Table)], key=lambda t: t[:2]))
		if args.spool:
			lines.extend(sorted([(str(s), None, s.rows, None) for s in objlist.values() if isinstance(s, Spool)]))
		print()
		print(tabulate(lines, columns=['Table', 'Database', 'Rows', 'Lock']))

def getargs():
	"get runtime parameters"
	from argparse import ArgumentParser

	p = ArgumentParser(description=__doc__)
	p.add_argument("inp", help="Input to the program. Defaul is name sql file")

	g = p.add_argument_group('Input type')
	g = g.add_mutually_exclusive_group()
	g.add_argument("-x", "--xml", action='store_true', help="Input is XML text instead of SQL query")
	g.add_argument("-q", "--query", action='store_true', help='Input is a query')

	g = p.add_argument_group('Output options')
	g.add_argument("-S", "--no-steps", dest='steps', action='store_false', help='Do not print steps')
	g.add_argument("-t", "--tables", action='store_true', help='Print table cardinality information')
	g.add_argument("-o", "--spool", action='store_true', help='Print spool cardinality information')

	util.dbconn_args(p)

	return p.parse_args()

_dblist = {}
def get_objs(db: ET.Element) -> Iterable[Tuple[str, TableLike]]:
	"generator yielding all database objects"
	_dblist[db.attrib['Id']] = db.attrib['DatabaseName']
	for tb in db:
		if tb.tag == 'Relation':
			yield (tb.attrib['Id'], Table(_dblist[tb.attrib['DatabaseId']], tb.attrib['TableName'], tb.attrib['Cardinality']))
		elif tb.tag == 'View':
			yield (tb.attrib['Id'], View(_dblist[tb.attrib['DatabaseId']], tb.attrib['ViewName']))
		elif tb.tag == 'Spool':
			yield (tb.attrib['Id'], Spool(tb.attrib['SpoolNumber'], tb.attrib.get('Confidence'), tb.attrib.get('Cardinality')))
		else:
			raise RuntimeError('Unknown Database Object (%s)' % tb.tag)
		for ix in tb:
			if ix.tag == 'Index':
				yield (ix.attrib['Id'], Index(ix))

def print_steps(steps: Iterator[Step]) -> None:
	"print explain steps in order"
	def step_details(s):
		op = s.op
		tgt = f'{s.tgt.obj}, {s.tgt}' if s.tgt else ''
		src1 = str(s.src[0]) if s.src else ''
		src2 = str(s.src[1]) if len(s.src) > 1 else ''

		return [s.num, op, tgt, src1, src2]

	print(tabulate(map(step_details, steps), columns=[StepNum.ppfmt(), 'Operation', 'Target', 'Source 1', 'Source 2']))

def print_tree(roots: Iterator[TableLike]) -> None:
	"Print object derivation hierarchy starting at each of the given objects"
	def obj_tree(tb):
		for pfx, ch in treeiter(tb):
			node = str(pfx) + str(ch)
			rows = time = op = geo = step = None
			if isinstance(ch, Spool) and ch.step:
				op, geo, step = ch.step.op, ch.step.tgt.geo, ch.step.num
				if ch.step.rows:
					rows, time = ch.step.rows, ch.step.time
			elif isinstance(ch, Table) and ch.rows:
				rows = ch.rows

			yield node, op, geo, step, rows, time

	lines = [n for tb in roots for n in obj_tree(tb)]
	c1_fmt = '.<' + str(max(len(r[0]) for r in lines))
	print(tabulate(([format(r[0], c1_fmt), *r[1:]] for r in lines), columns=['Table', 'Op', 'Acc', StepNum.ppfmt(), 'Rows', 'Time']))

if __name__ == '__main__':
	import sys
	sys.exit(main())
