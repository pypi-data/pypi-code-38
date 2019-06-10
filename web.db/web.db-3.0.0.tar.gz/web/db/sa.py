try:
	from sqlalchemy import create_engine
	from sqlalchemy.orm import scoped_session, sessionmaker
except ImportError:  # pragma: no cover
	raise ImportError('Unable to import sqlalchemy; pip install sqlalchemy to fix this.')

from .util import redact_uri


log = __import__('logging').getLogger(__name__)


class SQLAlchemyConnection:
	"""SQLAlchemy database engine support for WebCore's DatabaseExtension."""
	
	def __init__(self, uri, alias=None, **config):
		"""Prepare SQLAlchemy configuration."""
		# def __init__(self, uri, session=None, metadata=None, session_opts=None, alias=None, **kw):
		
		config.setdefault('pool_recycle', 3600)
		
		self.uri = uri
		self.alias = alias
		self.config = config
		self.engine = None
		self.Session = None
	
	def __repr__(self):
		return '{self.__class__.__name__}({self.alias}, "{uri}")'.format(
				self = self,
				uri = redact_uri(self.uri),
			)
	
	def start(self, context):
		"""Construct the SQLAlchemy engine and session factory."""
		
		if __debug__:
			log.info("Connecting SQLAlchemy database layer.", extra=dict(
					uri = redact_uri(self.uri),
					config = self.config,
					alias = self.alias,
				))
		
		# Construct the engine.
		engine = self.engine = create_engine(self.uri, **self.config)
		
		# Construct the session factory.
		self.Session = scoped_session(sessionmaker(bind=engine))
		
		# Test the connection.
		engine.connect().close()
		
		# Assign the engine to our database alias.
		context.db[self.alias] = engine
	
	def prepare(self, context):
		"""Prepare a sqlalchemy session on the WebCore context"""
		
		# Assign the session factory to our database alias.
		context.db[self.alias] = self.Session
	
	def done(self, context):
		"""Close and clean up the request local session, if any."""
		
		context.db[self.alias].remove()
	
	def stop(self, context):
		"""Disconnect any hanging connections in the pool."""
		
		self.engine.dispose()
