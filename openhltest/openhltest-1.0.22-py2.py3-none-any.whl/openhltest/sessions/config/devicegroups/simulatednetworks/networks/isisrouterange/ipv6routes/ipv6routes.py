from openhltest_client.base import Base


class Ipv6Routes(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/simulated-networks/networks/isis-route-range/ipv6-routes resource.
	"""
	YANG_NAME = 'ipv6-routes'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ipv6Routes, self).__init__(parent)

	@property
	def Address(self):
		"""TBD

		Get an instance of the Address class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.ipv6routes.address.address.Address)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.ipv6routes.address.address import Address
		return Address(self)._read()

	@property
	def PrefixLength(self):
		"""TBD

		Get an instance of the PrefixLength class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.ipv6routes.prefixlength.prefixlength.PrefixLength)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.ipv6routes.prefixlength.prefixlength import PrefixLength
		return PrefixLength(self)._read()

	@property
	def Name(self):
		"""The unique name of the IPv4 route object.

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('name')

	def read(self, Name=None):
		"""Get `ipv6-routes` resource(s). Returns all `ipv6-routes` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name):
		"""Create an instance of the `ipv6-routes` resource

		Args:
			Name (string): The unique name of the IPv4 route object.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `ipv6-routes` resource

		"""
		return self._delete()

