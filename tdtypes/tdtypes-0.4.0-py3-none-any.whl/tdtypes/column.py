"Teradata column types"

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2016-2017, Paresh Adhia"

from .util import Ident

class SQLRegister(str):
	"Built-in SQL Register/function"
	pass

class IdentityDef:
	"""Definition for IDENTITY columns"""
	def __init__(self, attr):
		self.dflt = attr['valueGeneration'] == "ByDefault"
		self.by = attr['increment']
		self.start = attr['startValue']
		self.min = attr['minValue']
		self.max = attr['maxValue']
		self.cycle = attr['cycle'] == "true"

	def sqldef(self):
		"""Returns SQL DDL"""
		return 'GENERATED {} AS IDENTITY (START WITH {} INCREMENT BY {} MINVALUE {} MAXVALUE {}{})'.format(
			'BY DEFAULT' if self.dflt else 'ALWAYS',
			self.start,
			self.by,
			self.min,
			self.max,
			' CYCLE' if self.cycle else ''
		)

class Column:
	"Database Column"
	# When set to True, all attrubutes must match for two columns to be compared equally
	strict_compare = False

	def __init__(self, name, coltype=None, nullable=True, defval=None, fmtstr=None, cprs=None, idtype=None, sysgen=None):
		self.name, self.coltype, self.nullable, self.defval, self.fmtstr, self.cprs, self.idtype, self.sysgen = \
			Ident(name), coltype, nullable, defval, fmtstr, cprs, idtype, sysgen

	def sqltype(self):
		"SQL type"
		return self.coltype

	def sqldef(self, fmtstr="{:q} {} {}", incl_format=False):
		"""Returns SQL DDL"""

		attrs = ['        ' if self.nullable or isinstance(self, DerivedPeriod) else 'NOT NULL']
		if self.idtype:
			attrs.append(self.idtype.sqldef())
		if incl_format and self.fmtstr:
			attrs.append("FORMAT '{}'".format(self.fmtstr))
		if self.defval:
			attrs.append("DEFAULT {}".format(self.defval))
		if self.cprs:
			attrs.append("COMPRESS ({})".format(','.join(self.quote_val(v) for v in self.cprs)))
		if self.sysgen:
			attrs.append("GENERATED ALWAYS AS ROW " + self.sysgen.upper())

		return fmtstr.format(self.name, self.sqltype(), ' '.join(attrs)).rstrip()

	__repr__ = sqldef

	def __str__(self):
		return self.name

	def __eq__(self, other):
		if other is None:
			return False
		if isinstance(other, str):
			return self.name == other
		if isinstance(other, Column):
			if (self.name, self.coltype, self.nullable, self.idtype) == (other.name, other.coltype, other.nullable, other.idtype):
				return (self.cprs, self.defval, self.fmtstr) == (other.cprs, other.defval, other.fmtstr) if self.strict_compare else True

		return False

	@staticmethod
	def fromxml(cdef):
		"factory method to create object from XML"
		name = cdef.attrib['name']

		attr = {'nullable': cdef.attrib['nullable'] == 'true'}

		defval = cdef.find('Default')
		if defval is not None:
			attr['defval'] = SQLRegister(defval.attrib['type']) if 'type' in defval.attrib else defval.attrib['value']
		if 'format' in cdef.attrib:
			attr['fmtstr'] = cdef.attrib['format']
		if cdef.find('Compress'):
			attr['cprs'] = [v.attrib['value'] for v in cdef.find('Compress')]
		if cdef.find('Identity') is not None:
			attr['idtype'] = IdentityDef(cdef.find('Identity').attrib)
		if cdef.attrib.get('systemGeneratedRowStart'):
			attr['sysgen'] = 'start'
		if cdef.attrib.get('systemGeneratedRowEnd'):
			attr['sysgen'] = 'end'

		t = cdef.find('DataType')[0]

		attr['coltype'] = t.tag.upper()

		def int_attr(attr):
			"convert attribute to integer if present"
			return int(t.attrib[attr]) if attr in t.attrib else None

		# pylint: disable=locally-disabled, bad-whitespace, multiple-statements
		if   t.tag == 'Char':     return CharCol(name, int(t.attrib['length']), varchar=t.attrib['varying']=='true', charset=t.attrib['charset'], **attr)
		elif t.tag == 'Byte':     return ByteCol(name, int(t.attrib['length']), varying=t.attrib['varying']=='true', **attr)

		elif t.tag == 'Integer':  return IntegerCol(name, 4, **attr)
		elif t.tag == 'SmallInt': return IntegerCol(name, 2, **attr)
		elif t.tag == 'ByteInt':  return IntegerCol(name, 1, **attr)
		elif t.tag == 'BigInt':   return IntegerCol(name, 8, **attr)
		elif t.tag == 'Decimal':  return DecimalCol(name, int_attr('precision'), int_attr('scale'), **attr)
		elif t.tag == 'Number':   return NumberCol(name, int_attr('precision'), int_attr('scale'), **attr)
		elif t.tag == 'Float':    return FloatCol(name, **attr)

		elif t.tag == 'Date':     return DateCol(name, **attr)
		elif t.tag == 'Time':     return TimeCol(name, int(t.attrib['fractionalSecondsPrecision']), **attr)
		elif t.tag == 'TimeStamp':return TimestampCol(name, int(t.attrib['fractionalSecondsPrecision']), t.attrib.get("timezone", "false") == "true", **attr)
		elif t.tag == 'DerivedPeriod': return DerivedPeriod(name, t.attrib['startColumnName'], t.attrib['endColumnName'], **attr)
		elif t.tag.startswith('Interval'): return IntervalCol(name, t.tag[8:], int_attr('precision'), int_attr('fractionalSecondsPrecision'), **attr)

		elif t.tag == 'JSON':     return JSONCol(name, int_attr('size'), int_attr('inlinelength'), **attr)
		elif t.tag == 'XML':      return XMLCol(name, int_attr('size'), int_attr('inlinelength'), **attr)
		elif t.tag == 'UDT' and t.attrib['name'] == "SYSUDTLIB.XML": return XMLCol(name, None, None, **attr)

		return Column(name, **attr)

	@classmethod
	def quote_val(cls, v):
		"""Return quoted value suitable for SQL script"""
		return "'" + v + "'" if v is not None else None


class CharCol(Column):
	"Database CHAR or VARCHAR column"
	def __init__(self, name, size, varchar=False, cs=False, charset=None, **attr):
		super().__init__(name, **attr)
		self.size, self.varchar, self.cs, self.charset = size, varchar, cs, charset

	def sqltype(self):
		return '{}CHAR({})'.format('VAR' if self.varchar else '', self.size)

	@classmethod
	def quote_val(cls, v):
		"""Return quoted value suitable for SQL script"""
		return "'" + v.replace("'", "''") + "'" if v is not None else None

class ByteCol(Column):
	"Database BYTE or VARBYTE column"
	def __init__(self, name, size, varying=False, **attr):
		super().__init__(name, **attr)
		self.size, self.varying = size, varying

	def sqltype(self):
		return '{}BYTE({})'.format('VAR' if self.varying else '', self.size)

	@classmethod
	def quote_val(cls, v):
		"""Return quoted value suitable for SQL script"""
		return "'" + ''.join(format(ord(b), '02x') for b in v) + "'xb" if v is not None else None


class NumericCol(Column):
	"Base class for all numeric Database columns"
	@classmethod
	def quote_val(cls, v):
		"""Return quoted value suitable for SQL script"""
		return v

class IntegerCol(NumericCol):
	"Dataase INT, BIGINT, SMALLINT, BYTEINT column"
	def __init__(self, name, size, **attr):
		super().__init__(name, **attr)
		self.size = size

	def sqltype(self):
		return {4: 'INTEGER', 2: 'SMALLINT', 1: 'BYTEINT', 8: 'BIGINT'}[self.size]

class DecimalCol(NumericCol):
	"Database DECIMAL or NUMERIC column"
	def __init__(self, name, precision, scale, **attr):
		super().__init__(name, **attr)
		self.precision, self.scale = precision, scale

	def sqltype(self):
		return '{}({},{})'.format(self.coltype, self.precision, self.scale)

class FloatCol(NumericCol):
	"Database FLOAT column"
	def __init__(self, name, **attr):
		super().__init__(name, **attr)

class NumberCol(NumericCol):
	"Database DECIMAL or NUMERIC column"
	def __init__(self, name, precision, scale, **attr):
		super().__init__(name, **attr)
		self.precision, self.scale = precision, scale

	def sqltype(self):
		return self.coltype if self.precision is None else '{}({},{})'.format(self.coltype, self.precision, self.scale)


class DateCol(Column):
	"Database DATE column"
	def __init__(self, name, **attr):
		super().__init__(name, **attr)

class TimeCol(Column):
	"Database TIME column"
	def __init__(self, name, frac, **attr):
		super().__init__(name, **attr)
		self.frac = frac

	def sqltype(self):
		return '{}({})'.format(self.coltype, self.frac)

class TimestampCol(Column):
	"Database TIMESTAMP column"
	def __init__(self, name, frac, with_tz=False, **attr):
		super().__init__(name, **attr)
		self.frac, self.with_tz = frac, with_tz

	def sqltype(self):
		return 'TIMESTAMP({})'.format(self.frac) + (' WITH TIME ZONE' if self.with_tz else '')

class DerivedPeriod(Column):
	"Teradata Derived PERIOD column"
	def __init__(self, name, start, end, **attr):
		super().__init__(name, **attr)
		self.start, self.end = start, end

	def sqltype(self):
		return 'PERIOD FOR {} ({}, {})'.format(self.name, self.start, self.end)

class IntervalCol(Column):
	"Database INTERVAL column"
	def __init__(self, name, types, prec1, prec2, **attr):
		super().__init__(name, **attr)

		self.prec1, self.prec2 = prec1, prec2
		if 'To' in types:
			self.type1, self.type2 = types.split('To')
		else:
			self.type1, self.type2 = types, None

	def sqltype(self):
		prec1 = f"{self.prec1},{self.prec2}" if self.type2 is None and self.prec2 is not None else str(self.prec1)
		s = f'INTERVAL {self.type1.upper()}({prec1})'

		if self.type2:
			prec2 = '' if self.prec2 is None else f"({self.prec2})"
			s += f" TO {self.type2.upper()}{prec2}"

		return s

class SemiStructCol(Column):
	"Semi-structured data types"
	def __init__(self, name, size, size_in, **attr):
		super().__init__(name, **attr)
		self.size, self.size_in = size, size_in

class JSONCol(SemiStructCol):
	"Database JSON column"
	def sqltype(self):
		col_t = self.coltype
		if self.size != 16776192:
			col_t += f'({self.size})'
		if self.size_in != 4096:
			col_t += ' INLINE LENGTH {}'.format(self.size_in)
		return col_t

class XMLCol(SemiStructCol):
	"Database XML column"
	def sqltype(self):
		col_t = self.coltype
		if self.size != 2097088000:
			col_t += f'({self.size})'
		if self.size_in != 4046:
			col_t += ' INLINE LENGTH {}'.format(self.size_in)
		return col_t


class ColList:
	"""A mixin that represents column list"""
	@property
	def columns(self):
		"""return list of columns"""
		return self.col.values()

	def __iter__(self):
		for c in self.col.values():
			yield c

	def __getattr__(self, attr):
		attr = Ident(attr)
		if self._col and attr in self._col:
			return self._col[attr]
		raise AttributeError("No column named '{}' found".format(attr))

	def __getitem__(self, key):
		if not isinstance(key, Ident):
			key = Ident(key)
		return self.col[key]
