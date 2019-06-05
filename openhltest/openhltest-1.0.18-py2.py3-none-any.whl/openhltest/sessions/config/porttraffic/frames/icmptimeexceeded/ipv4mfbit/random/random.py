from openhltest_client.base import Base


class Random(Base):
	"""The repeatable random pattern.
	"""
	YANG_NAME = 'random'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Max": "max", "Step": "step", "Seed": "seed", "Min": "min"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Random, self).__init__(parent)

	@property
	def Min(self):
		"""The minimum random value of the random pattern

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('min')

	@property
	def Max(self):
		"""The maximum random value of the random pattern

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('max')

	@property
	def Step(self):
		"""The step value of the random pattern

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('step')

	@property
	def Seed(self):
		"""The seed value of the random pattern

		Getter Returns:
			uint32

		Setter Allows:
			uint32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('seed')

	def update(self, Min=None, Max=None, Step=None, Seed=None):
		"""Update the current instance of the `random` resource

		Args:
			Min (string): The minimum random value of the random pattern
			Max (string): The maximum random value of the random pattern
			Step (string): The step value of the random pattern
			Seed (uint32): The seed value of the random pattern
		"""
		return self._update(locals())

