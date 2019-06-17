from openhltest_client.base import Base


class Increment(Base):
	"""TBD
	"""
	YANG_NAME = 'increment'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"To": "to", "Step": "step", "From": "from"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Increment, self).__init__(parent)

	@property
	def From(self):
		"""Starting increment value for frame length

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('from')

	@property
	def To(self):
		"""Maximum increment value for frame length

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('to')

	@property
	def Step(self):
		"""Step increment value for frame length

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('step')

	def update(self, From=None, To=None, Step=None):
		"""Update the current instance of the `increment` resource

		Args:
			From (int32): Starting increment value for frame length
			To (int32): Maximum increment value for frame length
			Step (int32): Step increment value for frame length
		"""
		return self._update(locals())

