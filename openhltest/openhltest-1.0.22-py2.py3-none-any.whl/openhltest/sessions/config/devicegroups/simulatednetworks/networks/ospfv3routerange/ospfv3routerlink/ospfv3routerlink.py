from openhltest_client.base import Base


class Ospfv3RouterLink(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/simulated-networks/networks/ospfv3-route-range/ospfv3-router-link resource.
	"""
	YANG_NAME = 'ospfv3-router-link'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ospfv3RouterLink, self).__init__(parent)

	@property
	def RouterLinkType(self):
		"""Type of link
		VIRTUAL_LINK   : Virtual Link
		POINT_TO_POINT : P2P (point-to-point) adjacency

		Get an instance of the RouterLinkType class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.ospfv3routerlink.routerlinktype.routerlinktype.RouterLinkType)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.ospfv3routerlink.routerlinktype.routerlinktype import RouterLinkType
		return RouterLinkType(self)._read()

	@property
	def InterfaceId(self):
		"""The Interface ID is an interface index number that a router uses to uniquely
		identify an interface. The Interface ID must be unique within the router.

		Get an instance of the InterfaceId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.ospfv3routerlink.interfaceid.interfaceid.InterfaceId)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.ospfv3routerlink.interfaceid.interfaceid import InterfaceId
		return InterfaceId(self)._read()

	@property
	def Name(self):
		"""The unique name of the networks object.

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
		"""Get `ospfv3-router-link` resource(s). Returns all `ospfv3-router-link` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name):
		"""Create an instance of the `ospfv3-router-link` resource

		Args:
			Name (string): The unique name of the networks object.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `ospfv3-router-link` resource

		"""
		return self._delete()

