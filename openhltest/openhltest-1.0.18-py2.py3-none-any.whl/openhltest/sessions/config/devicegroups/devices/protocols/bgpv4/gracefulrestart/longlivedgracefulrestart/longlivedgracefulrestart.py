from openhltest_client.base import Base


class LongLivedGracefulRestart(Base):
	"""BGP long lived graceful restart allows a network operator to choose to maintain stale routing information
	from a failed BGP peer much longer than the existing BGP graceful restart facility.
	   TRUE  : Enable long lived graceful restart
	   FALSE : Disable long lived graceful restart
	"""
	YANG_NAME = 'long-lived-graceful-restart'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Single": "single", "PatternType": "pattern-type", "PatternFormat": "pattern-format", "ValueList": "value-list"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(LongLivedGracefulRestart, self).__init__(parent)

	@property
	def Increment(self):
		"""The values that make up the increment pattern

		Get an instance of the Increment class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.longlivedgracefulrestart.increment.increment.Increment)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.longlivedgracefulrestart.increment.increment import Increment
		return Increment(self)._read()

	@property
	def Decrement(self):
		"""TBD

		Get an instance of the Decrement class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.longlivedgracefulrestart.decrement.decrement.Decrement)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.longlivedgracefulrestart.decrement.decrement import Decrement
		return Decrement(self)._read()

	@property
	def Random(self):
		"""The repeatable random pattern.

		Get an instance of the Random class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.longlivedgracefulrestart.random.random.Random)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.longlivedgracefulrestart.random.random import Random
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
		"""Update the current instance of the `long-lived-graceful-restart` resource

		Args:
			PatternType (enumeration): The selected pattern from the possible pattern types.
			PatternFormat (string): The format of the pattern.This will almost always be a regular expression.It is used to determine the validity of the values being set in the child leaf nodes of the pattern.
			Single (string): The value of the single pattern
			ValueList (string): The value list pattern takes a list of values that will be repeated if they do not meet or exceed the count
		"""
		return self._update(locals())

