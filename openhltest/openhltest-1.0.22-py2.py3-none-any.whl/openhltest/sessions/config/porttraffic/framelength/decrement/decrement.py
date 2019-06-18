from openhltest_client.base import Base


class Decrement(Base):
	"""TBD
	"""
	YANG_NAME = 'decrement'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Start": "start", "Step": "step", "End": "end"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Decrement, self).__init__(parent)

	@property
	def Start(self):
		"""The minimum value for the decrementing frame length

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('start')

	@property
	def End(self):
		"""The maximum value for the decrementing frame length

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('end')

	@property
	def Step(self):
		"""The step value for the decrementing frame length. This must be a power of two.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('step')

	def update(self, Start=None, End=None, Step=None):
		"""Update the current instance of the `decrement` resource

		Args:
			Start (int32): The minimum value for the decrementing frame length
			End (int32): The maximum value for the decrementing frame length
			Step (int32): The step value for the decrementing frame length. This must be a power of two.
		"""
		return self._update(locals())

