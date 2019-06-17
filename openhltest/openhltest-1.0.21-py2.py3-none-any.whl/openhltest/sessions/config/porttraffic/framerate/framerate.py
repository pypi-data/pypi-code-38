from openhltest_client.base import Base


class FrameRate(Base):
	"""TBD
	"""
	YANG_NAME = 'frame-rate'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Mode": "mode"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(FrameRate, self).__init__(parent)

	@property
	def FixedRate(self):
		"""TBD

		Get an instance of the FixedRate class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.framerate.fixedrate.fixedrate.FixedRate)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.framerate.fixedrate.fixedrate import FixedRate
		return FixedRate(self)._read()

	@property
	def DecrementRate(self):
		"""TBD

		Get an instance of the DecrementRate class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.framerate.decrementrate.decrementrate.DecrementRate)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.framerate.decrementrate.decrementrate import DecrementRate
		return DecrementRate(self)._read()

	@property
	def IncrementRate(self):
		"""TBD

		Get an instance of the IncrementRate class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.framerate.incrementrate.incrementrate.IncrementRate)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.framerate.incrementrate.incrementrate import IncrementRate
		return IncrementRate(self)._read()

	@property
	def Mode(self):
		"""TBD

		Getter Returns:
			FIXED | INCREMENT | DECREMENT

		Setter Allows:
			FIXED | INCREMENT | DECREMENT

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('mode')

	def update(self, Mode=None):
		"""Update the current instance of the `frame-rate` resource

		Args:
			Mode (enumeration): TBD
		"""
		return self._update(locals())

