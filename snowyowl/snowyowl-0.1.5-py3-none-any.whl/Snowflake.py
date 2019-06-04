from .get_data import get_data
import snowflake.connector
from snowflake.connector import SnowflakeConnection
import atexit

class Snowflake:
	def __init__(self, user, password, account, warehouse=None):
		self._connection = None
		self._warehouse = None
		self.connect(user=user, password=password, account=account, warehouse=warehouse)
		atexit.register(self.connection.close)

	@property
	def connection(self):
		"""
		:rtype: SnowflakeConnection
		"""
		return self._connection

	def connect(self, user, password, account, warehouse=None):
		if self._connection is not None:
			self.connection.close()
		self._connection = snowflake.connector.connect(user=user, password=password, account=account)
		self._warehouse = warehouse or self._warehouse

	def close_connection(self):
		self.connection.close()

	def __del__(self):
		self.connection.close()

	def get_data(self, query, warehouse=None):
		warehouse = warehouse or self._warehouse
		return get_data(query=query, warehouse=warehouse, connection=self._connection)
