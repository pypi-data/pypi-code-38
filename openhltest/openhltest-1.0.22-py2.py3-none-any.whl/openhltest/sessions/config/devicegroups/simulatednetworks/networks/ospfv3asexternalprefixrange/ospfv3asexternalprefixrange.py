from openhltest_client.base import Base


class Ospfv3AsExternalPrefixRange(Base):
	"""TBD
	"""
	YANG_NAME = 'ospfv3-as-external-prefix-range'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ospfv3AsExternalPrefixRange, self).__init__(parent)

	@property
	def Address(self):
		"""IPv6 address

		Get an instance of the Address class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.address.address.Address)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.address.address import Address
		return Address(self)._read()

	@property
	def PrefixLength(self):
		"""Prefix Length

		Get an instance of the PrefixLength class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.prefixlength.prefixlength.PrefixLength)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.prefixlength.prefixlength import PrefixLength
		return PrefixLength(self)._read()

	@property
	def AdvertiseRouterId(self):
		"""Advertising Router ID.  Specifies the 32-bit router ID of the router that
		advertises a given LSA 

		Get an instance of the AdvertiseRouterId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.advertiserouterid.advertiserouterid.AdvertiseRouterId)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.advertiserouterid.advertiserouterid import AdvertiseRouterId
		return AdvertiseRouterId(self)._read()

	@property
	def SequenceNumber(self):
		"""Sequence Number. Used to detect old and duplicate LSAs.

		Get an instance of the SequenceNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.sequencenumber.sequencenumber.SequenceNumber)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.sequencenumber.sequencenumber import SequenceNumber
		return SequenceNumber(self)._read()

	@property
	def Age(self):
		"""Age of the LSA, in seconds.

		Get an instance of the Age class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.age.age.Age)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.age.age import Age
		return Age(self)._read()

	@property
	def Checksum(self):
		"""Specifies the LSA will be advertised with a good or a bad checksum.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.checksum.checksum import Checksum
		return Checksum(self)._read()

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
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.routecategory.routecategory.RouteCategory)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.routecategory.routecategory import RouteCategory
		return RouteCategory(self)._read()

	@property
	def MetricType(self):
		"""Metric type.
		   TRUE  Metric is considered larger than any intra-AS path.(External Metric)
		   FALSE Metric is expressed in the same units as interface cost.

		Get an instance of the MetricType class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.metrictype.metrictype.MetricType)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.metrictype.metrictype import MetricType
		return MetricType(self)._read()

	@property
	def Metric(self):
		"""Cost of the advertised network prefix.

		Get an instance of the Metric class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.metric.metric.Metric)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.metric.metric import Metric
		return Metric(self)._read()

	@property
	def PrefixOptions(self):
		"""8- bit field of capabilities advertised with each prefix.
		   NUBIT    No Unicast capability bit. If set, the prefix is excluded from IPv6 unicast calculations.
		   LABIT    Local Address capability bit. If set, the prefix becomes an IPv6 interface address of the advertising router.
		   MCBIT    Multicast capability bit. If set, the prefix is included in the IPv6 multicast calculations.
		   PBIT     Propagate bit. Set this on the NSSA area prefixes that should be readvertised at the NSSA border.
		   DNBIT    Downward bit. Controls an inter-area-prefix-LSAs or AS-external-LSAs re-advertisement in a VPN environment
		   NBIT     Set in PrefixOptions for a host address (PrefixLength=128) that identifies the advertising router
		   UNUSED6  Bit not defined.
		   UNUSED7  Bit not defined. 

		Get an instance of the PrefixOptions class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.prefixoptions.prefixoptions.PrefixOptions)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.prefixoptions.prefixoptions import PrefixOptions
		return PrefixOptions(self)._read()

	@property
	def LinkStateId(self):
		"""Link State ID. ID of the interface connected to the transit network

		Get an instance of the LinkStateId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.linkstateid.linkstateid.LinkStateId)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.linkstateid.linkstateid import LinkStateId
		return LinkStateId(self)._read()

	@property
	def ExtendedLsa(self):
		"""TBD

		Get an instance of the ExtendedLsa class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.extendedlsa.extendedlsa.ExtendedLsa)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.extendedlsa.extendedlsa import ExtendedLsa
		return ExtendedLsa(self)._read()

	@property
	def ReferencedLsa(self):
		"""TBD

		Get an instance of the ReferencedLsa class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.referencedlsa.referencedlsa.ReferencedLsa)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.referencedlsa.referencedlsa import ReferencedLsa
		return ReferencedLsa(self)._read()

