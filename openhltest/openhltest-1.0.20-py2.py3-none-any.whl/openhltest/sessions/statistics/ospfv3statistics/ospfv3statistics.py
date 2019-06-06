from openhltest_client.base import Base


class Ospfv3Statistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/ospfv3-statistics resource.
	"""
	YANG_NAME = 'ospfv3-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'device-name'
	YANG_PROPERTY_MAP = {"TxLinkLsa": "tx-link-lsa", "RxInterAreaRouterLsa": "rx-inter-area-router-lsa", "RxUpdate": "rx-update", "TxHelloCount": "tx-hello-count", "RxRouterInfoLsa": "rx-router-info-lsa", "TxRouterInfoLsa": "tx-router-info-lsa", "RxNssaLsa": "rx-nssa-lsa", "TxInterAreaPrefixLsa": "tx-inter-area-prefix-lsa", "DeviceName": "device-name", "TxAck": "tx-ack", "RxLinkLsa": "rx-link-lsa", "RxDd": "rx-dd", "TxRequest": "tx-request", "RxNetworkLsa": "rx-network-lsa", "RxIntraAreaPrefixLsa": "rx-intra-area-prefix-lsa", "TxDd": "tx-dd", "TxNetworkLsa": "tx-network-lsa", "RxAck": "rx-ack", "TxAsExternalLsa": "tx-as-external-lsa", "TxInterAreaRouterLsa": "tx-inter-area-router-lsa", "RxRouterLsa": "rx-router-lsa", "RxInterAreaPrefixLsa": "rx-inter-area-prefix-lsa", "TxRouterLsa": "tx-router-lsa", "RouterState": "router-state", "RxRequest": "rx-request", "TxNssaLsa": "tx-nssa-lsa", "AdjacencyStatus": "adjacency-status", "TxUpdate": "tx-update", "RxAsExternalLsa": "rx-as-external-lsa", "PortName": "port-name", "TxIntraAreaPrefixLsa": "tx-intra-area-prefix-lsa", "RxHelloCount": "rx-hello-count"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ospfv3Statistics, self).__init__(parent)

	@property
	def ExtendedLsaCounters(self):
		"""Extended LSA counters.

		Get an instance of the ExtendedLsaCounters class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.ospfv3statistics.extendedlsacounters.extendedlsacounters.ExtendedLsaCounters)
		"""
		from openhltest_client.openhltest.sessions.statistics.ospfv3statistics.extendedlsacounters.extendedlsacounters import ExtendedLsaCounters
		return ExtendedLsaCounters(self)._read()

	@property
	def DeviceName(self):
		"""An abstract test port name

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
	def RouterState(self):
		"""Reports the state of adjacency on the current port.

		Getter Returns:
			DOWN | WAITING | DR | DR_OTHER | BACKUP
		"""
		return self._get_value('router-state')

	@property
	def AdjacencyStatus(self):
		"""OSPFv2 Adjacency State.
		 DOWN    Initial state of a neighbor conversation. It indicates that therehas been no
		         recent information received from the neighbor.
		 ATTEMPT This state is only valid for neighbors attached to non-broadcastnetworks. It
		         indicates that no recent information has been received from theneighbor, but that
		         a more concerted effort should be made to contact the neighbor. This is done by
		         sending the neighbor Hello packets at intervals ofHelloInterval.
		
		 INIT    An Hello packet has recently been seen from the neighbor. However,bidirectional
		         communication has not yet been established with the neighbor(the router itself
		         did not appear in the neighbor's Hello packet). Allneighbors in this state (or higher)
		         are listed in the Hello packets sentfrom the associated interface.
		
		 TWOWAYS Communication between the two routers is bidirectional. This has been assured by the
		         operation of the Hello Protocol. This is the mostadvanced state short of beginning
		         adjacency establishment. The BackupDesignated Router (BDR) is selected from the set
		         of neighbors in the TWOWAYSstate or greater.
		
		 EXSTART This is the first step in creating an adjacency between the twoneighboring routers.
		         The goal of this step is to decide which router is the master, and to decide upon
		         the initial database description (DD) sequencenumber. Neighbor conversations in this
		         state or greater are calledadjacencies.
		
		 EXCHANGE In this state the router is describing its entire link statedatabase by sending
		         Database Description packets to the neighbor. EachDatabase Description Packet has
		         a DD sequence number, and is explicitlyacknowledged. Only one Database Description
		         Packet is allowed outstanding atany one time. In this state, Link State Request Packets
		         may also be sentasking for the neighbor's more recent advertisements. All adjacencies in
		         Exchange state or greater are used by the flooding procedure. In fact, these adjacencies
		         are fully capable of transmitting and receiving all types of OSPF routing protocol packets.
		         Loading Link State Request packets are sent to the neighbor asking for themore recent
		         advertisements that have been discovered (but not yet received)in the Exchange state.
		
		 FULL    Neighboring routers are fully adjacent. These adjacencies will nowappear in router
		         links and network links advertisements. 

		Getter Returns:
			DOWN | ATTEMPT | INIT | TWOWAYS | EXSTART | EXCHANGE | LOADING | FULL
		"""
		return self._get_value('adjacency-status')

	@property
	def TxHelloCount(self):
		"""Number of Hello packets transmitted by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-hello-count')

	@property
	def RxHelloCount(self):
		"""Number of Hello packets received by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-hello-count')

	@property
	def RxAck(self):
		"""Received acks. The number of Link State Acknowledgment packets received by the emulated router. 

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-ack')

	@property
	def RxDd(self):
		"""Received DD - The number of Database Description packets (containing LSAheaders) received by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-dd')

	@property
	def RxRequest(self):
		"""Received requests. The number of LS requests received by the emulatedrouter. 

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-request')

	@property
	def RxUpdate(self):
		"""Rx update.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-update')

	@property
	def RxRouterInfoLsa(self):
		"""The number of Router Information LSAs received by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-router-info-lsa')

	@property
	def TxAck(self):
		"""Sent acks. The number of Link State Acknowledgment packets sent by theemulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-ack')

	@property
	def TxDd(self):
		"""Sent DD - Number of Database Description packets sent by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-dd')

	@property
	def TxRequest(self):
		"""Sent requests. The number of LS request packets sent by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-request')

	@property
	def TxUpdate(self):
		"""Tx update.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-update')

	@property
	def TxRouterInfoLsa(self):
		"""The number of Router Information LSAs sent by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-router-info-lsa')

	@property
	def RxAsExternalLsa(self):
		"""Received external-LSAs. The number of external LSAs received by theemulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-as-external-lsa')

	@property
	def RxInterAreaPrefixLsa(self):
		"""Received inter-area-prefix LSAs. The number of inter-area-prefix LSAsreceived by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-inter-area-prefix-lsa')

	@property
	def RxInterAreaRouterLsa(self):
		"""Received inter-area-router LSAs. The number of inter-area-router LSAsreceived by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-inter-area-router-lsa')

	@property
	def RxIntraAreaPrefixLsa(self):
		"""Received Intra-Area-Prefix-LSAs - Number of Intra-Area-Prefix LSAs receivedby the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-intra-area-prefix-lsa')

	@property
	def RxLinkLsa(self):
		"""Received link-LSAs. The number of link LSAs received by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-link-lsa')

	@property
	def RxNetworkLsa(self):
		"""Received Network-LSAs - Number of Network LSAs received by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-network-lsa')

	@property
	def RxNssaLsa(self):
		"""Received Link-LSAs. The number of Link LSAs received by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-nssa-lsa')

	@property
	def RxRouterLsa(self):
		"""Received Router-LSAs - Number of Router LSAs received by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-router-lsa')

	@property
	def TxAsExternalLsa(self):
		"""Sent external-LSAs. The number of external LSAs sent by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-as-external-lsa')

	@property
	def TxInterAreaPrefixLsa(self):
		"""Sent inter-area-prefix LSAs. The number of inter-area-prefix LSAs sent bythe emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-inter-area-prefix-lsa')

	@property
	def TxInterAreaRouterLsa(self):
		"""Sent inter-area-router LSAs. The number of inter-area-router LSAs sent bythe emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-inter-area-router-lsa')

	@property
	def TxIntraAreaPrefixLsa(self):
		"""Sent Intra-Area-Prefix-LSAs - Number of Intra-Area-Prefix LSAs sent by theemulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-intra-area-prefix-lsa')

	@property
	def TxLinkLsa(self):
		"""Sent link-LSAs. The number of link LSAs sent by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-link-lsa')

	@property
	def TxNetworkLsa(self):
		"""Sent Network-LSAs - Number of Network LSAs sent by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-network-lsa')

	@property
	def TxNssaLsa(self):
		"""Sent NSSA-LSAs. The number of NSSA LSAs sent by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-nssa-lsa')

	@property
	def TxRouterLsa(self):
		"""Sent Router-LSAs - Number of Router LSAs sent by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-router-lsa')

	def read(self, DeviceName=None):
		"""Get `ospfv3-statistics` resource(s). Returns all `ospfv3-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(DeviceName)

