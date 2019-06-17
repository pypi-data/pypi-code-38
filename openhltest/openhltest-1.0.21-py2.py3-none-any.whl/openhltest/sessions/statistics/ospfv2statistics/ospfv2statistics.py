from openhltest_client.base import Base


class Ospfv2Statistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/ospfv2-statistics resource.
	"""
	YANG_NAME = 'ospfv2-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'device-name'
	YANG_PROPERTY_MAP = {"TxTeLsa": "tx-te-lsa", "TxHelloCount": "tx-hello-count", "RxRouterInfoLsa": "rx-router-info-lsa", "RxExtendedLinkLsa": "rx-extended-link-lsa", "RxNssaLsa": "rx-nssa-lsa", "RxSummaryLsa": "rx-summary-lsa", "TxSummaryLsa": "tx-summary-lsa", "DeviceName": "device-name", "TxAck": "tx-ack", "TxAsbrSummaryLsa": "tx-asbr-summary-lsa", "RxTeLsa": "rx-te-lsa", "RxDd": "rx-dd", "TxRequest": "tx-request", "RxNetworkLsa": "rx-network-lsa", "TxExtendedPrefixLsa": "tx-extended-prefix-lsa", "RxRouterLsa": "rx-router-lsa", "TxNetworkLsa": "tx-network-lsa", "RxAck": "rx-ack", "TxAsExternalLsa": "tx-as-external-lsa", "RxExtendedPrefixLsa": "rx-extended-prefix-lsa", "TxDd": "tx-dd", "TxRouterLsa": "tx-router-lsa", "RouterState": "router-state", "RxRequest": "rx-request", "TxNssaLsa": "tx-nssa-lsa", "RxAsbrSummaryLsa": "rx-asbr-summary-lsa", "AdjacencyStatus": "adjacency-status", "TxRouterInfoLsa": "tx-router-info-lsa", "TxExtendedLinkLsa": "tx-extended-link-lsa", "RxAsExternalLsa": "rx-as-external-lsa", "PortName": "port-name", "RxHelloCount": "rx-hello-count"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ospfv2Statistics, self).__init__(parent)

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
		"""Received Acks - Number of Link State Acknowledgment packets
		received by theemulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-ack')

	@property
	def RxAsbrSummaryLsa(self):
		"""Received ASBR-Summary-LSAs - Number of ASBR-Summary-LSAs received
		by theemulated router. 

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-asbr-summary-lsa')

	@property
	def RxAsExternalLsa(self):
		"""Number of Extended Prefix LSAs received by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-as-external-lsa')

	@property
	def RxDd(self):
		"""Received DD - Number of Database Description packets (containing LSAheaders)
		received by the emulated router. 

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-dd')

	@property
	def RxExtendedLinkLsa(self):
		"""Number of Extended Link LSAs received by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-extended-link-lsa')

	@property
	def RxExtendedPrefixLsa(self):
		"""Number of Extended Prefix LSAs received by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-extended-prefix-lsa')

	@property
	def RxNetworkLsa(self):
		"""Received Network-LSAs - Number of Network LSAs received by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-network-lsa')

	@property
	def RxNssaLsa(self):
		"""Received NSSA-LSAs - Number of NSSA LSAs received by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-nssa-lsa')

	@property
	def RxRequest(self):
		"""Received Requests - Number of LS Request packets received by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-request')

	@property
	def RxRouterInfoLsa(self):
		"""Number of Router Info LSAs received by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-router-info-lsa')

	@property
	def RxRouterLsa(self):
		"""Received Router-LSAs - Number of Router LSAs received by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-router-lsa')

	@property
	def RxSummaryLsa(self):
		"""Received Summary-LSAs - Number of Summary LSAs received by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-summary-lsa')

	@property
	def RxTeLsa(self):
		"""Received TE-LSAs - Number of TE-LSAs received by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-te-lsa')

	@property
	def TxAck(self):
		"""Sent Acks - Number of Link State Acknowledgment packets sent by the
		emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-ack')

	@property
	def TxAsbrSummaryLsa(self):
		"""Sent ASBR-Summary-LSAs - Number of ASBR-Summary LSAs sent by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-asbr-summary-lsa')

	@property
	def TxAsExternalLsa(self):
		"""Sent External-LSAs - Number of External LSAs sent by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-as-external-lsa')

	@property
	def TxDd(self):
		"""Sent DD - Number of Database Description packets sent by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-dd')

	@property
	def TxExtendedLinkLsa(self):
		"""Number of Extended Link LSAs sent by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-extended-link-lsa')

	@property
	def TxExtendedPrefixLsa(self):
		"""Number of Extended Prefix LSAs sent by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-extended-prefix-lsa')

	@property
	def TxNetworkLsa(self):
		"""Sent Network-LSAs - Number of Network LSAs sent by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-network-lsa')

	@property
	def TxNssaLsa(self):
		"""Sent NSSA-LSAs - Number of NSSA LSAs sent by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-nssa-lsa')

	@property
	def TxRequest(self):
		"""Sent Requests - Number of LS Request packets sent by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-request')

	@property
	def TxRouterInfoLsa(self):
		"""Number of Router Info LSAs sent by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-router-info-lsa')

	@property
	def TxRouterLsa(self):
		"""Sent Router-LSAs - Number of Router LSAs sent by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-router-lsa')

	@property
	def TxSummaryLsa(self):
		"""Sent Summary-LSAs - Number of Summary LSAs sent by the emulatedrouter.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-summary-lsa')

	@property
	def TxTeLsa(self):
		"""Sent TE-LSAs - Number of TE-LSAs sent by the emulated router.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-te-lsa')

	def read(self, DeviceName=None):
		"""Get `ospfv2-statistics` resource(s). Returns all `ospfv2-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(DeviceName)

