from openhltest_client.base import Base


class IsisStatistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/isis-statistics resource.
	"""
	YANG_NAME = 'isis-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'device-name'
	YANG_PROPERTY_MAP = {"NeighborExtendedCircuitId": "neighbor-extended-circuit-id", "TxL1LanHelloCount": "tx-l1-lan-hello-count", "TxL1CsnpCount": "tx-l1-csnp-count", "TxL2LspCount": "tx-l2-lsp-count", "TxL1PsnpCount": "tx-l1-psnp-count", "RxL2CsnpCount": "rx-l2-csnp-count", "RxL2LspCount": "rx-l2-lsp-count", "DeviceName": "device-name", "TxL1LspCount": "tx-l1-lsp-count", "RxPtpHelloCount": "rx-ptp-hello-count", "ThreeWayP2pAdjacencyState": "three-way-p2p-adjacency-state", "TxPtpHelloCount": "tx-ptp-hello-count", "L2BroadcastAdjacencyState": "l2-broadcast-adjacency-state", "L1BroadcastAdjacencyState": "l1-broadcast-adjacency-state", "TxL2PsnpCount": "tx-l2-psnp-count", "TxL2CsnpCount": "tx-l2-csnp-count", "NeighborSystemId": "neighbor-system-id", "TxL2LanHelloCount": "tx-l2-lan-hello-count", "RxL1CsnpCount": "rx-l1-csnp-count", "RxL2PsnpCount": "rx-l2-psnp-count", "RxL1LspCount": "rx-l1-lsp-count", "RouterState": "router-state", "RxL2LanHelloCount": "rx-l2-lan-hello-count", "RxL1PsnpCount": "rx-l1-psnp-count", "RxL1LanHelloCount": "rx-l1-lan-hello-count", "PortName": "port-name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IsisStatistics, self).__init__(parent)

	@property
	def DeviceName(self):
		"""Device Name

		Getter Returns:
			string
		"""
		return self._get_value('device-name')

	@property
	def PortName(self):
		"""An abstract test port name

		Getter Returns:
			string
		"""
		return self._get_value('port-name')

	@property
	def RxL1LanHelloCount(self):
		"""Number of LAN Hello packets received by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-l1-lan-hello-count')

	@property
	def TxL1LanHelloCount(self):
		"""Number of LAN Hello packets transmitted by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-l1-lan-hello-count')

	@property
	def RxL2LanHelloCount(self):
		"""Number of LAN Hello packets received by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-l2-lan-hello-count')

	@property
	def TxL2LanHelloCount(self):
		"""Number of LAN Hello packets transmitted by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-l2-lan-hello-count')

	@property
	def TxL1CsnpCount(self):
		"""Number of Tx CSNPs sent to the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-l1-csnp-count')

	@property
	def TxL1LspCount(self):
		"""Number of Tx LSPs sent to the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-l1-lsp-count')

	@property
	def TxL1PsnpCount(self):
		"""Number of Tx PSNPs sent to the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-l1-psnp-count')

	@property
	def RxL1CsnpCount(self):
		"""Number of Rx CSNPs received from the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-l1-csnp-count')

	@property
	def RxL1LspCount(self):
		"""Number of Rx LSPs received from the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-l1-lsp-count')

	@property
	def RxL1PsnpCount(self):
		"""Number of Rx PSNPs received from the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-l1-psnp-count')

	@property
	def TxL2CsnpCount(self):
		"""Number of Tx CSNPs sent to the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-l2-csnp-count')

	@property
	def TxL2LspCount(self):
		"""Number of Tx LSPs sent to the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-l2-lsp-count')

	@property
	def TxL2PsnpCount(self):
		"""Number of Tx PSNPs sent to the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-l2-psnp-count')

	@property
	def RxL2CsnpCount(self):
		"""Number of Rx CSNPs received from the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-l2-csnp-count')

	@property
	def RxL2LspCount(self):
		"""Number of Rx LSPs received from the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-l2-lsp-count')

	@property
	def RxL2PsnpCount(self):
		"""Number of Rx PSNPs received from the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-l2-psnp-count')

	@property
	def RouterState(self):
		"""State of adjacency with the SUT

		Getter Returns:
			IDLE | INIT | UP | GR | GRHELPER
		"""
		return self._get_value('router-state')

	@property
	def NeighborExtendedCircuitId(self):
		"""Learned the extended circuit ID of the adjacent neighbor after a three-way Hello exchange.

		Getter Returns:
			string
		"""
		return self._get_value('neighbor-extended-circuit-id')

	@property
	def RxPtpHelloCount(self):
		"""Number of Rx point-to-point hellos received from the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-ptp-hello-count')

	@property
	def TxPtpHelloCount(self):
		"""Number of Tx point-to-point hellos sent to the SUT.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-ptp-hello-count')

	@property
	def NeighborSystemId(self):
		"""Learned System ID of the adjacent neighbor after three-way Helloexchange.

		Getter Returns:
			string
		"""
		return self._get_value('neighbor-system-id')

	@property
	def ThreeWayP2pAdjacencyState(self):
		"""Adjacency state of three-way Hello in point-to-pointnetwork.

		Getter Returns:
			UP | INIT | DOWN | NOT_STARTED | NA
		"""
		return self._get_value('three-way-p2p-adjacency-state')

	@property
	def L1BroadcastAdjacencyState(self):
		"""Adjacency state of broadcast router.

		Getter Returns:
			NOT_STARTED | IDLE | INIT | DIS_OTHER | DIS | GR | GRHELPER | NA
		"""
		return self._get_value('l1-broadcast-adjacency-state')

	@property
	def L2BroadcastAdjacencyState(self):
		"""Adjacency state of broadcast router.

		Getter Returns:
			NOT_STARTED | IDLE | INIT | DIS_OTHER | DIS | GR | GRHELPER | NA
		"""
		return self._get_value('l2-broadcast-adjacency-state')

	def read(self, DeviceName=None):
		"""Get `isis-statistics` resource(s). Returns all `isis-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(DeviceName)

