from openhltest_client.base import Base


class Ospfv2NssaRange(Base):
	"""OSPFV2 NSSA LSA (Type-7), NNot So Stubby Area (NSSA) LSAs (OSPF Type 7), are originated by ASBRs within NSSAs,
	but are flooded only within the NSSAs, by default..
	"""
	YANG_NAME = 'ospfv2-nssa-range'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ospfv2NssaRange, self).__init__(parent)

	@property
	def Address(self):
		"""IP address

		Get an instance of the Address class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.address.address.Address)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.address.address import Address
		return Address(self)._read()

	@property
	def PrefixLength(self):
		"""Prefix Length

		Get an instance of the PrefixLength class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.prefixlength.prefixlength.PrefixLength)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.prefixlength.prefixlength import PrefixLength
		return PrefixLength(self)._read()

	@property
	def AdvertiseRouterId(self):
		"""Router ID of the simulated router that will advertise NSSA LSAs

		Get an instance of the AdvertiseRouterId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.advertiserouterid.advertiserouterid.AdvertiseRouterId)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.advertiserouterid.advertiserouterid import AdvertiseRouterId
		return AdvertiseRouterId(self)._read()

	@property
	def RouteCategory(self):
		"""Route Category can be used to filter routes by type.
		   UNDEFINED The default category assigned to a manually created block.
		   PRIMARY   A preferred route that has duplicates (secondary routes) advertised by other ports.
		   SECONDARY Secondary route.
		   UNIQUE    A less preferred backup route.
		   ANY       Indicates that a single port in the test configuration advertises this route.

		Get an instance of the RouteCategory class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.routecategory.routecategory.RouteCategory)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.routecategory.routecategory import RouteCategory
		return RouteCategory(self)._read()

	@property
	def ForwardingAddress(self):
		"""IPv4 forwarding address to use in the forwarding address field of the LSA.

		Get an instance of the ForwardingAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.forwardingaddress.forwardingaddress.ForwardingAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.forwardingaddress.forwardingaddress import ForwardingAddress
		return ForwardingAddress(self)._read()

	@property
	def SequenceNumber(self):
		"""Initial value of the LS sequence number field in the LSA header.
		Used to detect old and duplicate LSAs. The larger the sequence number,
		the more recent the LSA.

		Get an instance of the SequenceNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.sequencenumber.sequencenumber.SequenceNumber)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.sequencenumber.sequencenumber import SequenceNumber
		return SequenceNumber(self)._read()

	@property
	def Age(self):
		"""Age of the LSA, in seconds.

		Get an instance of the Age class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.age.age.Age)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.age.age import Age
		return Age(self)._read()

	@property
	def Checksum(self):
		"""Specifies the LSA will be advertised with a good or a bad checksum.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def MetricType(self):
		"""Metric type.
		   TYPE1  When calculating the cost of the path to an NSSA route, the costs of internal links are included.
		   TYPE2  Costs of internal links are not included in total cost calculation. Type 2 routes have a lower priority and are considered in path selection after Type 1 costs have been evaluated.

		Get an instance of the MetricType class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.metrictype.metrictype.MetricType)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.metrictype.metrictype import MetricType
		return MetricType(self)._read()

	@property
	def Metric(self):
		"""Route-cost metric to be used when advertising the specified NSSA LSAs.

		Get an instance of the Metric class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.metric.metric.Metric)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.metric.metric import Metric
		return Metric(self)._read()

	@property
	def Options(self):
		"""NSSA LSA Options.
		   TBIT     TOS: Type of Service (T,0).
		   EBIT     External Routing: Specifies the way AS-external-LSAs are flooded (E,1).
		   MCBIT    Multicast: Specifies whether IP multicast datagrams are forwarded (MC,2).
		   NPBIT    NSSA: Specifies the handling of Type-7 LSAs (N/P,3).
		   EABIT    External Attribute: Specifies the router's willingness to receive and forward External-Attributes-LSAs (EA,4).
		   DCBIT    Demand Circuit: Specifies the router's handling of demand circuits (DC,5).
		   OBIT     Opaque: Specifies the router's willingness to receive and forward Opaque LSAs as specified in RFC 2370 (O,6).
		   UNUSED7  Unused: This bit is not used

		Get an instance of the Options class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.options.options.Options)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.options.options import Options
		return Options(self)._read()

	@property
	def SegmentRouting(self):
		"""TBD

		Get an instance of the SegmentRouting class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.segmentrouting.segmentrouting.SegmentRouting)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2nssarange.segmentrouting.segmentrouting import SegmentRouting
		return SegmentRouting(self)._read()

