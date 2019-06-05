from openhltest_client.base import Base


class ExtendedLsa(Base):
	"""TBD
	"""
	YANG_NAME = 'extended-lsa'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(ExtendedLsa, self).__init__(parent)

	@property
	def ExtendedLsaTlvs(self):
		"""Include extended LSA tlvs.
		   IPV6_FORWARDING_ADDR IPv6  IPv6 Forwarding Address sub-TLV.
		   IPV4_FORWARDING_ADDR IPv4  IPv4 Forwarding Address sub-TLV.
		   ROUTE_TAG                  Route-Tag sub-TLV.

		Get an instance of the ExtendedLsaTlvs class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.extendedlsa.extendedlsatlvs.extendedlsatlvs.ExtendedLsaTlvs)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.extendedlsa.extendedlsatlvs.extendedlsatlvs import ExtendedLsaTlvs
		return ExtendedLsaTlvs(self)._read()

	@property
	def Ipv6ForwardingAddress(self):
		"""IPv6 Forwarding address

		Get an instance of the Ipv6ForwardingAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.extendedlsa.ipv6forwardingaddress.ipv6forwardingaddress.Ipv6ForwardingAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.extendedlsa.ipv6forwardingaddress.ipv6forwardingaddress import Ipv6ForwardingAddress
		return Ipv6ForwardingAddress(self)._read()

	@property
	def Ipv4ForwardingAddress(self):
		"""IPv4 Forwarding address

		Get an instance of the Ipv4ForwardingAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.extendedlsa.ipv4forwardingaddress.ipv4forwardingaddress.Ipv4ForwardingAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.extendedlsa.ipv4forwardingaddress.ipv4forwardingaddress import Ipv4ForwardingAddress
		return Ipv4ForwardingAddress(self)._read()

	@property
	def RouteTag(self):
		"""Route tag

		Get an instance of the RouteTag class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.extendedlsa.routetag.routetag.RouteTag)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.extendedlsa.routetag.routetag import RouteTag
		return RouteTag(self)._read()

