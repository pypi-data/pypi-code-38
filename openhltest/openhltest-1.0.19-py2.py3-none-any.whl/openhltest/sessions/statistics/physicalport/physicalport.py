from openhltest_client.base import Base


class PhysicalPort(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/physical-port resource.
	"""
	YANG_NAME = 'physical-port'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'port-name'
	YANG_PROPERTY_MAP = {"ConnectedTestPortId": "connected-test-port-id", "ConnectionStateDetails": "connection-state-details", "ConnectedTestPortDescription": "connected-test-port-description", "ConnectionState": "connection-state", "PortName": "port-name", "Speed": "speed"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(PhysicalPort, self).__init__(parent)

	@property
	def PortName(self):
		"""An abstract test port name

		Getter Returns:
			string
		"""
		return self._get_value('port-name')

	@property
	def ConnectedTestPortId(self):
		"""The id of the connected test port.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			string
		"""
		return self._get_value('connected-test-port-id')

	@property
	def ConnectedTestPortDescription(self):
		"""Free form vendor specific description of the connected test port.
		Can include details such as make/model/productId of the underlying hardware.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			string
		"""
		return self._get_value('connected-test-port-description')

	@property
	def ConnectionState(self):
		"""The state of the connection to the physical hardware
		test port or virtual machine test port

		Getter Returns:
			CONNECTING | CONNECTED_LINK_UP | CONNECTED_LINK_DOWN | DISCONNECTING | DISCONNECTED
		"""
		return self._get_value('connection-state')

	@property
	def ConnectionStateDetails(self):
		"""Free form vendor specific information about the state of the connection to
		the physical hardware test port or virtual machine test port.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			string
		"""
		return self._get_value('connection-state-details')

	@property
	def Speed(self):
		"""The actual speed of the test port.
		Empty if the abstract port is not connected to a test port.

		Getter Returns:
			string
		"""
		return self._get_value('speed')

	def read(self, PortName=None):
		"""Get `physical-port` resource(s). Returns all `physical-port` resources from the server if no input parameters are specified.

		"""
		return self._read(PortName)

