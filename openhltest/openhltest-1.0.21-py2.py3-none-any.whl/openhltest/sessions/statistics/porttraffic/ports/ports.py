from openhltest_client.base import Base


class Ports(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/port-traffic/ports resource.
	"""
	YANG_NAME = 'ports'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"RxFrames": "rx-frames", "RxFrameRate": "rx-frame-rate", "TxFrameRate": "tx-frame-rate", "Name": "name", "TxByteRate": "tx-byte-rate", "TxBitRate": "tx-bit-rate", "TxByteCount": "tx-byte-count", "RxByteCount": "rx-byte-count", "TxFrames": "tx-frames", "RxBitRate": "rx-bit-rate", "RxBitCount": "rx-bit-count", "DroppedFrames": "dropped-frames", "TxBitCount": "tx-bit-count", "RxByteRate": "rx-byte-rate"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ports, self).__init__(parent)

	@property
	def Name(self):
		"""The name of the transmit port of this port traffic stream

		Getter Returns:
			leafref
		"""
		return self._get_value('name')

	@property
	def TxFrames(self):
		"""The total number of frames transmitted on the port.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-frames')

	@property
	def RxFrames(self):
		"""The total number of frames received on the the port.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-frames')

	@property
	def TxFrameRate(self):
		"""Total number of frames transmitted over the last 1-second interval.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-frame-rate')

	@property
	def RxFrameRate(self):
		"""Total number of frames received over the last 1-second interval.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-frame-rate')

	@property
	def DroppedFrames(self):
		"""Total Number of dropped frames during transit.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('dropped-frames')

	@property
	def TxBitCount(self):
		"""The total number of bits transmitted on the port.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-bit-count')

	@property
	def RxBitCount(self):
		"""The total number of bits received on the the port.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-bit-count')

	@property
	def TxBitRate(self):
		"""Total number of bits transmitted over the last 1-second interval.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-bit-rate')

	@property
	def RxBitRate(self):
		"""Total number of bits received over the last 1-second interval.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-bit-rate')

	@property
	def TxByteCount(self):
		"""The total number of bytes transmitted on the port.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-byte-count')

	@property
	def RxByteCount(self):
		"""The total number of bytes received on the the port.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-byte-count')

	@property
	def TxByteRate(self):
		"""Total number of bytes transmitted over the last 1-second interval.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-byte-rate')

	@property
	def RxByteRate(self):
		"""Total number of bytes received over the last 1-second interval.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-byte-rate')

	def read(self, Name=None):
		"""Get `ports` resource(s). Returns all `ports` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

