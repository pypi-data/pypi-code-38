from openhltest_client.base import Base


class Decrement(Base):
	"""TBD
	"""
	YANG_NAME = 'decrement'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Start": "start", "Step": "step"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Decrement, self).__init__(parent)

	@property
	def Start(self):
		"""The start value of the decrement pattern

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('start')

	@property
	def Step(self):
		"""The step value of the decrement pattern

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('step')

	def update(self, Start=None, Step=None):
		"""Update the current instance of the `decrement` resource

		Args:
			Start (string): The start value of the decrement pattern
			Step (string): The step value of the decrement pattern
		"""
		return self._update(locals())

