from openhltest_client.base import Base


class FixedRate(Base):
	"""TBD
	"""
	YANG_NAME = 'fixed-rate'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"PercentValue": "percent-value", "Mbps": "mbps", "RateType": "rate-type", "Bps": "bps", "InterPacketGap": "inter-packet-gap", "Fps": "fps", "Kbps": "kbps"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(FixedRate, self).__init__(parent)

	@property
	def RateType(self):
		"""Load unit applied to the stream block.

		Getter Returns:
			BPS | KBPS | MPBS | FRAMES_PER_SECOND | INTER_PACKET_GAP | PERCENT_LINE_RATE

		Setter Allows:
			BPS | KBPS | MPBS | FRAMES_PER_SECOND | INTER_PACKET_GAP | PERCENT_LINE_RATE

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('rate-type')

	@property
	def Bps(self):
		"""Load value set on the streamblock/traffic-item in bits per second.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('bps')

	@property
	def Kbps(self):
		"""Load value set on the streamblock/traffic-item in kilo bits per second.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('kbps')

	@property
	def Mbps(self):
		"""Load value set on the streamblock/traffic-item in mega bits per second.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('mbps')

	@property
	def Fps(self):
		"""Load value set on the streamblock/traffic-item in frames per second.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('fps')

	@property
	def InterPacketGap(self):
		"""Load value set on the streamblock/traffic-item inter packet gap.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('inter-packet-gap')

	@property
	def PercentValue(self):
		"""Load value set on the streamblock/traffic-item in percent.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('percent-value')

	def update(self, RateType=None, Bps=None, Kbps=None, Mbps=None, Fps=None, InterPacketGap=None, PercentValue=None):
		"""Update the current instance of the `fixed-rate` resource

		Args:
			RateType (enumeration): Load unit applied to the stream block.
			Bps (int32): Load value set on the streamblock/traffic-item in bits per second.
			Kbps (int32): Load value set on the streamblock/traffic-item in kilo bits per second.
			Mbps (int32): Load value set on the streamblock/traffic-item in mega bits per second.
			Fps (int32): Load value set on the streamblock/traffic-item in frames per second.
			InterPacketGap (int32): Load value set on the streamblock/traffic-item inter packet gap.
			PercentValue (int32): Load value set on the streamblock/traffic-item in percent.
		"""
		return self._update(locals())

