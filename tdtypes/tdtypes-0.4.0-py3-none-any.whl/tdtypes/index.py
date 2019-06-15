"Teradata Index and Partition types"

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2016-2017, Paresh Adhia"

from lazy import lazy
from .util import Ident
from .column import ColList

class Index(ColList):
	"""Database INDEX"""
	def __init__(self, xml, cdefs):
		from collections import OrderedDict

		self._xml, self._tbcols = xml, cdefs
		self.name = xml.get('name')
		self.col = OrderedDict()

		xcols = self._xml.find('./ColumnList')
		if xcols is not None:
			for xcol in xcols:
				c = cdefs[Ident(xcol.attrib['name'])]
				self.col[c.name] = c

	def sqldef(self):
		"""Return SQL definition of the index"""

		if self.columns:
			if self.is_pk:
				ddl = 'PRIMARY KEY'
			else:
				ddl = '{}{}INDEX'.format('UNIQUE ' if self.is_uniq else '', 'PRIMARY ' if self.is_pi else '')
			if self.name: ddl += ' '+self.name
			if self.allness: ddl += ' ALL'
			ddl += ' ({})'.format(','.join(c.name for c in self.columns))
		else:
			ddl = 'NO PRIMARY INDEX'

		if self._ix_attr:
			ddl += '\n' + self._ix_attr

		return ddl

	def __repr__(self):
		return "Index('"+self.sqldef()+"')"

	@lazy
	def _ix_attr(self):
		return ''

	@lazy
	def is_pi(self):
		"True if this is PI"
		return self._xml.tag == 'PrimaryIndex'

	@lazy
	def is_uniq(self):
		"True if index is unique"
		return self._xml.attrib['unique'] == 'true'

	@lazy
	def is_pk(self):
		"True if index supports primary key constraint"
		return self._xml.get('implicitIndexFor', 'None') == "PrimaryKeyConstraint"

	@lazy
	def allness(self):
		"true if ALL option is set"
		return self._xml.get('allOption', "false") == 'true'

	@staticmethod
	def fromxml(xml, cdefs):
		"factory method to create object from XML"

		o_xml = xml.find('./OrderBy')
		if o_xml is not None:
			return VOSI(xml, cdefs, o_xml)

		pt_xml = xml.find('PartitioningList')
		if pt_xml is not None:
			return PPI(xml, cdefs, pt_xml)

		return Index(xml, cdefs)

class VOSI(Index):
	"Value Ordered Secondary Index"
	def __init__(self, xml, cdefs, o_xml):
		super().__init__(xml, cdefs)
		self.order_col = self._tbcols[Ident(o_xml.attrib['column'])]
		self.order_byval = o_xml.attrib['type'] == 'Values'

	@lazy
	def _ix_attr(self):
		ddl = 'ORDER BY ' + ('VALUES' if self.order_byval else 'HASH')
		if self.order_col:
			ddl += '('+self.order_col.name+')'
		return ddl

class PPI(Index):
	"Partitioned Primary Index"
	def __init__(self, xml, cdefs, pt_xml):
		super().__init__(xml, cdefs)
		self._pt_xml = pt_xml

	@lazy
	def _ix_attr(self):
		return "PARTITION BY ({})".format('\n, '.join(p.sqldef() for p in self.parts))

	@lazy
	def parts(self):
		"column partition list"
		return [Partition.fromxml(pt, self._tbcols) for pt in self._pt_xml]


class Partition:
	"Base class for ROW or COLUMN partition"
	def __init__(self, level, extra=0):
		self.level, self.extra = level, extra

	def sqldef(self):
		"""Return SQL definition"""
		pass

	@staticmethod
	def fromxml(xml, cdefs):
		"factory method to create object from XML"
		level, extra = xml.attrib['level'], xml.get('extraPartitions', 0)

		if xml.tag == 'RowPartitioning':
			return RowPartition(level, xml.attrib['expression'], extra=extra)

		if xml.tag == 'ColumnPartitioning':
			return ColPartition(level, [ColGroup.fromxml(cg, cdefs) for cg in xml], extra=extra)

class RowPartition(Partition):
	"Row Partition"
	def __init__(self, level, expr, extra=0):
		super().__init__(level, extra)
		self.expr = expr.replace('\r', '\n')

	def sqldef(self):
		return self.expr

	def __repr__(self):
		return 'RowPartition("{}", levl={}, extra={})'.format(self.expr, self.level, self.extra)

class ColPartition(Partition):
	"Column Partition"
	def __init__(self, level, col_groups, extra=0):
		super().__init__(level, extra)
		self.col_groups = col_groups

	def sqldef(self):
		ddl = "COLUMN"
		groups = [g for g in self.col_groups if len(g) > 1 or not g.compressed or g.row]
		if groups:
			if len(groups) == 1 and groups[0].row:
				ddl += ' ALL BUT '
			ddl += "(" + ', '.join(g.sqldef() for g in groups) + ')'
		if self.extra:
			ddl += " ADD {}".format(self.extra)

		return ddl

	def __repr__(self):
		return 'ColPartition({}, levl={}, extra={})'.format(self.col_groups, self.level, self.extra)


class ColGroup(list):
	"A Column group of column partition"
	def __init__(self, copy=None, compressed=False, row=False):
		super().__init__()
		if copy:
			self.extend(copy)
		self.compressed, self.row = compressed, row

	def sqldef(self):
		"""SQL DDL"""
		ddl = 'ROW ' if self.row else ''
		ddl += ','.join(c.name for c in self)
		if len(self) > 1:
			ddl += '(' + ddl + ')'
		if not self.compressed:
			ddl += ' NO AUTO COMPRESS'
		return ddl

	def __repr__(self):
		return 'ColGroup({}, Compressed={}, Row={})'.format([c.name for c in self], self.compressed, self.row)

	@staticmethod
	def fromxml(xml, cdefs):
		"factory method to create object from XML"
		cg = ColGroup(compressed=xml.get('autoCompress', "false") == "true", row=xml.get('storage', "column") == "Row")
		cg.extend(cdefs[Ident(xcol.attrib['name'])] for xcol in xml.find('./ColumnList'))

		return cg
