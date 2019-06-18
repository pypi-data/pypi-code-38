from openhltest_client.base import Base


class Random(Base):
	"""Random frame size options
	"""
	YANG_NAME = 'random'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Start": "start", "End": "end"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Random, self).__init__(parent)

	@property
	def Start(self):
		"""The mimumum value of the random frame length

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
		"""The maximum value of the random frame length

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('end')

	def update(self, Start=None, End=None):
		"""Update the current instance of the `random` resource

		Args:
			Start (int32): The mimumum value of the random frame length
			End (int32): The maximum value of the random frame length
		"""
		return self._update(locals())

