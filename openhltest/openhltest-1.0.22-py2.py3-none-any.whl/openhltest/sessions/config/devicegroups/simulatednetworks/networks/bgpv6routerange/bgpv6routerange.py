from openhltest_client.base import Base


class Bgpv6RouteRange(Base):
	"""TBD
	"""
	YANG_NAME = 'bgpv6-route-range'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Active": "active"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Bgpv6RouteRange, self).__init__(parent)

	@property
	def Address(self):
		"""TBD

		Get an instance of the Address class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv6routerange.address.address.Address)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv6routerange.address.address import Address
		return Address(self)._read()

	@property
	def PrefixLength(self):
		"""TBD

		Get an instance of the PrefixLength class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv6routerange.prefixlength.prefixlength.PrefixLength)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv6routerange.prefixlength.prefixlength import PrefixLength
		return PrefixLength(self)._read()

	@property
	def AsPath(self):
		"""Used in the AS_PATH attribute in BGP UPDATE messages.

		Get an instance of the AsPath class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv6routerange.aspath.aspath.AsPath)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv6routerange.aspath.aspath import AsPath
		return AsPath(self)._read()

	@property
	def NextHopAddress(self):
		"""The next hop is the node to which packets should be sent to get them closer
		to the destination. Specify the IP address of the border router that should be
		used as the next hop to the destinations listed in the UPDATE message.
		This is the mandatory NEXT_HOP path attribute in UPDATE messages.

		Get an instance of the NextHopAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv6routerange.nexthopaddress.nexthopaddress.NextHopAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv6routerange.nexthopaddress.nexthopaddress import NextHopAddress
		return NextHopAddress(self)._read()

	@property
	def Active(self):
		"""TBD

		Getter Returns:
			boolean

		Setter Allows:
			boolean

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('active')

	def update(self, Active=None):
		"""Update the current instance of the `bgpv6-route-range` resource

		Args:
			Active (boolean): TBD
		"""
		return self._update(locals())

