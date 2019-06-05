from openhltest_client.base import Base


class Bgpv4RouteRange(Base):
	"""TBD
	"""
	YANG_NAME = 'bgpv4-route-range'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Active": "active"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Bgpv4RouteRange, self).__init__(parent)

	@property
	def Address(self):
		"""TBD

		Get an instance of the Address class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.address.address.Address)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.address.address import Address
		return Address(self)._read()

	@property
	def PrefixLength(self):
		"""TBD

		Get an instance of the PrefixLength class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.prefixlength.prefixlength.PrefixLength)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.prefixlength.prefixlength import PrefixLength
		return PrefixLength(self)._read()

	@property
	def AsPath(self):
		"""Used in the AS_PATH attribute in BGP UPDATE messages.

		Get an instance of the AsPath class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.aspath.aspath.AsPath)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.aspath.aspath import AsPath
		return AsPath(self)._read()

	@property
	def NextHopAddress(self):
		"""The next hop is the node to which packets should be sent to get them closer
		           to the destination. Specify the IP address of the border router that should be
		           used as the next hop to the destinations listed in the UPDATE message.
		           This is the mandatory NEXT_HOP path attribute in UPDATE messages.

		Get an instance of the NextHopAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.nexthopaddress.nexthopaddress.NextHopAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.nexthopaddress.nexthopaddress import NextHopAddress
		return NextHopAddress(self)._read()

	@property
	def AigpMetric(self):
		"""Value of the first accumulated interior gateway protocol(AIGP) metric

		Get an instance of the AigpMetric class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.aigpmetric.aigpmetric.AigpMetric)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.aigpmetric.aigpmetric import AigpMetric
		return AigpMetric(self)._read()

	@property
	def AtomicAggregate(self):
		"""TBD

		Get an instance of the AtomicAggregate class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.atomicaggregate.atomicaggregate.AtomicAggregate)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.atomicaggregate.atomicaggregate import AtomicAggregate
		return AtomicAggregate(self)._read()

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
		"""Update the current instance of the `bgpv4-route-range` resource

		Args:
			Active (boolean): TBD
		"""
		return self._update(locals())

