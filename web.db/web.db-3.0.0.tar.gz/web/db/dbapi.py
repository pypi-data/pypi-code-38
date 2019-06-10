from marrow.package.loader import load

from .util import redact_uri


log = __import__('logging').getLogger(__name__)


class DBAPIConnection:
	"""WebCore DBExtension interface for projects utilizing PEP 249 DB API database engines."""
	
	uri_safety = True  # Go to some effort to hide connection passwords from logs.
	thread_safe = True  # When False, create a connection for the duration of the request only.
	
	def __init__(self, engine, uri, safe=True, protect=True, alias=None, **kw):
		"""Prepare configuration options."""
		
		self.engine = engine
		self.uri = uri
		self.safe = safe  # Thread safe? When False, create a connection for the duration of a request only.
		self.protect = protect
		self.alias = alias
		self.config = kw
		
		self._connector = load(engine, 'db_api_connect')
		
		if self.safe:  # pragma: no cover
			self.start = self._connect
			self.stop = self._disconnect
		else:
			self.prepare = self._connect
			self.done = self._disconnect
	
	def __repr__(self):
		return '{self.__class__.__name__}({self.alias}, "{self.engine}", "{uri}")'.format(
				self = self,
				uri = redact_uri(self.uri, self.protect),
			)
	
	def _connect(self, context):
		"""Initialize the database connection."""
		
		if __debug__:
			log.info("Connecting " + self.engine.partition(':')[0] + " database layer.", extra=dict(
					uri = redact_uri(self.uri, self.protect),
					config = self.config,
					alias = self.alias,
				))
		
		self.connection = context.db[self.alias] = self._connector(self.uri, **self.config)
	
	def _disconnect(self, context):
		"""Close the connection and clean up references."""
		
		self.connection.close()
		del self.connection


class SQLite3Connection(DBAPIConnection):
	def __init__(self, path, alias=None, **kw):
		super().__init__('sqlite3:connect', path, False, False, alias, **kw)
