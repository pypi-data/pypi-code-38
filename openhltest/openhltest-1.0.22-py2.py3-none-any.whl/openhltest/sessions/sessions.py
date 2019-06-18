from openhltest_client.base import Base


class Sessions(Base):
	"""A list of test tool sessions.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions resource.
	"""
	YANG_NAME = 'sessions'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Sessions, self).__init__(parent)

	@property
	def Config(self):
		"""This container aggregates all other top level configuration submodules.

		Get an instance of the Config class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.config.Config)
		"""
		from openhltest_client.openhltest.sessions.config.config import Config
		return Config(self)._read()

	@property
	def Statistics(self):
		"""The statistics pull model

		Get an instance of the Statistics class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.statistics.Statistics)
		"""
		from openhltest_client.openhltest.sessions.statistics.statistics import Statistics
		return Statistics(self)._read()

	@property
	def Name(self):
		"""The unique name of a test tool session.

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('name')

	def read(self, Name=None):
		"""Get `sessions` resource(s). Returns all `sessions` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name):
		"""Create an instance of the `sessions` resource

		Args:
			Name (string): The unique name of a test tool session.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `sessions` resource

		"""
		return self._delete()

