"Module containing functions to obtain Teradata cursor"

__author__ = "Paresh Adhia"
__copyright__ = "Copyright 2016-2017 Paresh Adhia"

try:
	from tdconn_site import *
except ImportError:
	from .tdconn_default import *

conn = None # The first (and usually the only) connection object
csr = None  # The latest (and usually the only) cursor object

class EnhancedCursor:
	"Cursor wrapper class with some useful attributes"

	_version = None

	def __init__(self, base_csr):
		self.csr = base_csr

	@property
	def version(self):
		"Teradata database version"
		if not EnhancedCursor._version:
			self.csr.execute("Select InfoData From DBC.DBCInfoV Where InfoKey = 'VERSION'")
			EnhancedCursor._version = self.csr.fetchone()[0]
		return EnhancedCursor._version

	def _builtin(self, fn):
		"built-in function"
		self.execute('select ' + fn)
		return self.fetchone()[0]

	@property
	def schema(self):
		"Current DATABASE"
		self.execute('select database')
		return self.fetchone()[0]

	@schema.setter
	def schema(self, new_schema):
		self.execute('database ' + new_schema)
		self.csr.connection.commit()

	def fetchxml(self):
		"returns cleansed XML value from the first column of the result-set"
		import re

		val, more = '', True
		while more:
			val += ''.join(r[0] for r in self.fetchall())
			more = self.nextset()

		return re.sub('xmlns=".*?"', '', re.sub('encoding="UTF-16"', 'encoding="utf-8"', val, 1, flags=re.IGNORECASE), 1)

	def get_xmldef(self, o):
		"returns XML definition for a table or a view"
		from .table import Table, View

		if isinstance(o, Table):
			self.execute('SHOW IN XML TABLE ' + str(o))
		elif isinstance(o, View):
			self.execute('SHOW IN XML VIEW ' + str(o))
		else:
			raise TypeError('get_xmldef() supports only Table or View types')

		return self.fetchxml()

	def __iter__(self):
		return self.csr.__iter__()

	def __enter__(self, *args, **kwargs):
		return self

	def __exit__(self, *args, **kwargs):
		return self.csr.__exit__(*args, **kwargs)

	def __getattr__(self, attr):
		if attr in ['current_user', 'current_date', 'current_role', 'current_time', 'current_timestamp', 'session', 'user']:
			return self._builtin(attr)
		return getattr(self.csr, attr)

class EnhancedConnection:
	"Connection wrapper that provisions EnhancedCursor and commits before connection closes"
	cursor_class = EnhancedCursor

	def __init__(self, base_conn):
		self._conn = base_conn

	def cursor(self):
		"returns an EnhancedCursor instance"
		return EnhancedConnection.cursor_class(self._conn.cursor())

	def close(self):
		"returns an EnhancedCursor instance"
		self._conn.commit()
		self._conn.close()

	def __enter__(self, *args, **kwargs):
		return self

	def __exit__(self, *args, **kwargs):
		self.close()

	def __getattr__(self, attr):
		return getattr(self._conn, attr)

def connect(*args, **kargs):
	"returns Enhanced connection"
	return EnhancedConnection(dbconnect(*args, **kargs))

def cursor(*args, **kargs):
	"return cursor object"
	global conn, csr

	if not conn:
		import atexit
		conn = connect(*args, **kargs)
		atexit.register(conn.close)

	csr = conn.cursor()

	return csr

def commit():
	"commit using the global connection object"
	conn.commit()
