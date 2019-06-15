"Teradata Table and View types"

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2016-2017, Paresh Adhia"

from lazy import lazy

from . import sqlcsr
from .util import getLogger
from .util import Ident
from .column import ColList

logger = getLogger(__name__)

class DBObj:
	"A Database object that has schema and a name"
	_xml_type = None

	def __init__(self, sch, name, objtype=None):
		self.sch, self.name, self.objtype = Ident(sch), Ident(name), objtype
		self.get_xmldef = None

	def __str__(self):
		return format(self.sch, 'q') + '.' + format(self.name, 'q')

	def __format__(self, spec):
		return format(str(self), spec)

	def __repr__(self):
		if self.__class__.__name__ == DBObj.__name__:
			return "{}({}, {}, {})".format(self.__class__.__name__, repr(self.sch), repr(self.name), repr(self.objtype))
		return "{}({}, {})".format(self.__class__.__name__, repr(self.sch), repr(self.name))

	# pylint: disable=locally-disabled, bad-whitespace, multiple-statements
	def __eq__(self, other): return other is not None and isinstance(other, DBObj) and (self.sch, self.name) == (other.sch, other.name)
	def __lt__(self, other): return other is not None and isinstance(other, DBObj) and (self.sch, self.name) < (other.sch, other.name)
	def __le__(self, other): return self.__eq__(other) or self.__lt__(other)
	def __ge__(self, other): return not self.__lt__(other)
	def __ne__(self, other): return not self.__eq__(other)
	def __gt__(self, other): return not self.__le__(other)

	def __hash__(self):
		return (self.sch.lower() + self.name.lower()).__hash__()

	@staticmethod
	def create(sch, name, objtype, get_xmldef=None):
		"instantiate object based on type"
		if objtype == 'V':
			return View(sch, name, get_xmldef)
		if objtype == 'v': # hack for Volatile table
			return VolatileTable(sch, name, 'T', get_xmldef)
		if objtype == 't': # hack for GTT
			return GTTable(sch, name, 'T', get_xmldef)
		if objtype == 'O':
			return NoPITable(sch, name, get_xmldef)
		if objtype == 'T':
			return Table(sch, name, objtype, get_xmldef)

		return DBObj(sch, name, objtype)

	@lazy
	def _xmldef(self):
		"""get XML definition for an object, either using registered function or default cursor"""
		import xml.etree.ElementTree as ET

		if self.get_xmldef:
			fn = self.get_xmldef
		elif sqlcsr.csr:
			fn = sqlcsr.csr.get_xmldef
		else:
			raise RuntimeError('No get_xmldef() function has been registered')

		return ET.fromstring(fn(self)).find('./' + self._xml_type)


class Table(DBObj, ColList):
	"Teradata table. Except for schema and name, all attributes are lazily evaluated"
	_xml_type = 'Table'

	def __init__(self, sch, name, objtype='T', get_xmldef=None):
		super().__init__(sch, name, objtype=objtype)
		self.get_xmldef = get_xmldef
		self._col = None

	@property
	def col(self):
		"""ordered dictionary of table columns"""
		if self._col is None:
			from collections import OrderedDict
			from .column import Column
			self._col = OrderedDict(((c.name, c) for c in (Column.fromxml(c) for c in self._xmldef.find('./ColumnList'))))

		return self._col

	@lazy
	def indexes(self):
		"list of indexes"
		from .index import Index
		return [Index.fromxml(i, self.col) for i in self._xmldef.find('./Indexes')]

	@lazy
	def pi_cols(self):
		"list of Primary Index columns"
		try:
			return next(ix for ix in self.indexes if ix.is_pi).columns
		except StopIteration:
			return []

	@lazy
	def pk_cols(self):
		"list of primary key columns"
		try:
			return next(ix for ix in self.indexes if ix.is_pk).columns
		except StopIteration:
			return []

	@lazy
	def is_multiset(self):
		"returns True if table is MULTISET"
		return self._xmldef.attrib['kind'] == 'Multiset'

	@lazy
	def has_fallback(self):
		"returns True if table has FALLBACK"
		return self._xmldef.attrib['fallback'] == 'true'

	@lazy
	def is_sysver(self):
		"returns True if table is system versioned TEMPORAL"
		return self._xmldef.attrib.get("systemVersioned", "false") == "true"

	@lazy
	def pt_cols(self):
		"list of columns that participate in table partitioning"
		import re
		from .index import PPI
		from .index import RowPartition

		return [c for i in self.indexes if isinstance(i, PPI)
				for pt in i.parts if isinstance(pt, RowPartition)
				for c in self.columns if re.search(r'\b'+c.name+r'\b', pt.expr)]

	def cstr_defs(self):
		"""retuns a list of table constraints"""
		return []

	def sqldef(self, col_format=False):
		"""Returns SQL DDL"""

		from .column import DerivedPeriod

		colfmt = "{{:{}}}  {{:{}}}  {{}}".format(
				max(len(c.name) for c in self.columns),
				max(len(c.sqltype()) for c in self.columns if not isinstance(c, DerivedPeriod))
			)

		def post_opts():
			"returns a generator to table post-def options"
			yield from (i.sqldef() for i in self.indexes)
			yield from self.cstr_defs()
			if self.is_sysver:
				yield "WITH SYSTEM VERSIONING"

		return """\
CREATE {} {}TABLE {}
(
    {}
) {};""".format(
			'MULTISET' if self.is_multiset else 'SET',
			{GTTable: 'GLOBAL TEMPORARY ', VolatileTable: 'VOLATILE '}.get(type(self), ''),
			str(self),
			',\n    '.join(c.sqldef(colfmt, incl_format=col_format) for c in self.columns),
			"\n  ".join(post_opts())
		)

class NoPITable(Table):
	"NOPI Table"
	def __init__(self, sch, name, *args, **kwargs):
		super().__init__(sch, name, 'O', *args, **kwargs)

	@lazy
	def pi_cols(self):
		return []

class TemporaryTable(Table):
	"""Temporary Table"""
	@lazy
	def preserve_on_commit(self):
		"""Returns True if on commit behavior is to perserve rows"""
		return self._xmldef.find('./TableConstraint/TablePreserveMode').attrib['onCommit'] == 'Preserve'

	def cstr_defs(self):
		return super().cstr_defs() + ['ON COMMIT {} ROWS'.format('PRESERVE' if self.preserve_on_commit else 'DELETE')]

class VolatileTable(TemporaryTable):
	"""Volatile Table"""
	_xml_type = 'VolatileTable'

class GTTable(TemporaryTable):
	"""Global Temporary Table"""
	_xml_type = 'GlobalTemporaryTable'


class View(DBObj, ColList):
	"Database View"
	_xml_type = 'View'

	def __init__(self, sch, name, get_xmldef=None):
		super().__init__(sch, name, 'V')
		self.get_xmldef = get_xmldef

	@lazy
	def col(self):
		"""ordered dictionary of table columns"""
		from collections import OrderedDict
		from .column import Column

		return OrderedDict(((c.name, c) for c in (Column.fromxml(c) for c in self._xmldef.find('./ColumnList'))))

	@lazy
	def refs(self):
		"list of objects referred by this view"

		if not self._xmldef.find('./RefList'):
			logger.info("XML definition for '%s' did not contain referenced objects list", str(self))
			return []

		def xml2ob(x):
			"convert reference in xml to Table/View"
			sch, name, tv = x.attrib['dbName'], x.attrib['name'], x.attrib['type']
			return View(sch, name, get_xmldef=self.get_xmldef) if tv == 'View' else Table(sch, name, tv, get_xmldef=self.get_xmldef)

		return [xml2ob(r) for r in self._xmldef.find('./RefList')]

	def sqldef(self):
		"Return SQL definition"
		return self._xmldef.find('SQLText').text

class DBObjPat:
	"[<DB-PAT>.]<TB-PAT>. Pattern can include: %%,*,?. E.g. DB%%.TB%%, DB1.TB1*, tb2?last"

	def __init__(self, pat):
		self.sch, self.name = pat.split('.') if '.' in pat else (None, pat)

	def search_cond(self, db='DatabaseName', tb='TableName'):
		"build SQL search condition using search predicates formed by schema and name"
		cond = []
		if self.sch is None or self.sch != '%':
			cond.append(self.search_predicate(db, self.sch, defval='DATABASE'))
		if self.name != "%":
			cond.append(self.search_predicate(tb, self.name))
		return " AND ".join(cond) if cond else f"{db} LIKE '%' AND {tb} LIKE '%'"

	__str__ = search_cond

	@staticmethod
	def search_predicate(col, val, defval=None):
		"build SQL search predicate based on if value contains any wild-card characters"
		if val is None:
			return col + ' = ' + defval if defval is not None else None
		if '%' in val or '?' in val or '*' in val:
			return col + " LIKE '{}'{}".format(val.replace('_', '+_').replace('?', '_').replace('*', '%'), " ESCAPE '+'" if '_' in val else '')
		return col + " = '{}'".format(val)

	@staticmethod
	def findall(patterns, objtypes='', flatten=True, warn_notfound=True, csr=None):
		"factory method that returns list of objects matching list of wild-cards"
		return DBObjFinder(patterns, objtypes).findall(csr or sqlcsr.csr, flatten=flatten, warn_notfound=warn_notfound)


class DBObjFinder:
	"Class to find all DBObj that match a list of DBOBjPat"

	def __init__(self, patterns, objtypes=''):
		self.patterns, self.objtypes = patterns, objtypes

	def match_col(self, indent="\t"):
		"returns SQL CASE expression that evaluates to the index of of matched pattern"
		when = ''.join('{}WHEN {} THEN {}'.format('\t', pat, e) for e, pat in enumerate(self.patterns))
		return "CASE\n{}\n\tELSE NULL\nEND".format(when).replace('\n', '\n'+indent)

	def make_sql(self):
		"Build SQL to find objects matching patterns"

		obj_pred = ' AND TableKind IN ({})'.format(', '.join("'{}'".format(t) for t in self.objtypes)) if self.objtypes else ''

		return """\
SELECT DatabaseName
	, TableName
	, CASE WHEN CommitOpt <> 'N' THEN 't' ELSE TableKind END AS TableKind
	, {} AS MATCHED_PAT
FROM dbc.TablesV T
WHERE MATCHED_PAT IS NOT NULL{}""".format(self.match_col(), obj_pred)

	def names2objs(self, names, flatten=True, warn_notfound=True, csr=None):
		"group names by pattern index that they belong to"

		matches = [[] for p in self.patterns]
		for db, tb, tp, m in names:
			matches[m].append(DBObj.create(db, tb, tp, csr.get_xmldef if csr else None))

		if warn_notfound:
			all_notfound = ', '.join('{}.{}'.format(p.sch, p.name) for p, m in zip(self.patterns, matches) if not m)
			if all_notfound:
				logger.warning('No objects were found for search pattern(s): %s', all_notfound)

		return [o for m in matches for o in m] if flatten else matches

	def findall(self, csr, flatten=True, warn_notfound=True):
		"returns list of matching objects"

		sql = self.make_sql() + '\nORDER BY MATCHED_PAT, 1, 2'
		logger.debug('Search patterns: {}, SQL:{}\n'.format(', '.join(str(p) for p in self.patterns), sql))
		csr.execute(sql)

		return self.names2objs([r[:4] for r in csr.fetchall()], flatten=flatten, warn_notfound=warn_notfound, csr=csr)
