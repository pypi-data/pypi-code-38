from openhltest_client.base import Base


class Ipv4Ttl(Base):
	"""The limited number of iterations that a unit of data can experience before
	the data is discarded.
	"""
	YANG_NAME = 'ipv4-ttl'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Single": "single", "PatternType": "pattern-type", "PatternFormat": "pattern-format", "ValueList": "value-list"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ipv4Ttl, self).__init__(parent)

	@property
	def Increment(self):
		"""The values that make up the increment pattern

		Get an instance of the Increment class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpsourcequench.ipv4ttl.increment.increment.Increment)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpsourcequench.ipv4ttl.increment.increment import Increment
		return Increment(self)._read()

	@property
	def Decrement(self):
		"""TBD

		Get an instance of the Decrement class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpsourcequench.ipv4ttl.decrement.decrement.Decrement)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpsourcequench.ipv4ttl.decrement.decrement import Decrement
		return Decrement(self)._read()

	@property
	def Random(self):
		"""The repeatable random pattern.

		Get an instance of the Random class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpsourcequench.ipv4ttl.random.random.Random)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpsourcequench.ipv4ttl.random.random import Random
		return Random(self)._read()

	@property
	def PatternType(self):
		"""The selected pattern from the possible pattern types.

		Getter Returns:
			SINGLE | INCREMENT | DECREMENT | RANDOM | VALUE_LIST

		Setter Allows:
			SINGLE | INCREMENT | DECREMENT | RANDOM | VALUE_LIST

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('pattern-type')

	@property
	def PatternFormat(self):
		"""The format of the pattern.
		This will almost always be a regular expression.
		It is used to determine the validity of the values being set in the child leaf nodes of the pattern.

		Getter Returns:
			string
		"""
		return self._get_value('pattern-format')

	@property
	def Single(self):
		"""The value of the single pattern

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('single')

	@property
	def ValueList(self):
		"""The value list pattern takes a list of values that will be repeated if they do not meet or exceed the count

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('value-list')

	def update(self, PatternType=None, PatternFormat=None, Single=None, ValueList=None):
		"""Update the current instance of the `ipv4-ttl` resource

		Args:
			PatternType (enumeration): The selected pattern from the possible pattern types.
			PatternFormat (string): The format of the pattern.This will almost always be a regular expression.It is used to determine the validity of the values being set in the child leaf nodes of the pattern.
			Single (string): The value of the single pattern
			ValueList (string): The value list pattern takes a list of values that will be repeated if they do not meet or exceed the count
		"""
		return self._update(locals())

