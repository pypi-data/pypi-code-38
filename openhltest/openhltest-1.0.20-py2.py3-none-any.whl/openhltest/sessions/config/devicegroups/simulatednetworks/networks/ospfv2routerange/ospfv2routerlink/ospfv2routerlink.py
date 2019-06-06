from openhltest_client.base import Base


class Ospfv2RouterLink(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/simulated-networks/networks/ospfv2-route-range/ospfv2-router-link resource.
	"""
	YANG_NAME = 'ospfv2-router-link'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ospfv2RouterLink, self).__init__(parent)

	@property
	def RouterLinkType(self):
		"""Type of link
		VL             : Virtual Link
		POINT_TO_POINT : P2P (point-to-point) network
		STUB_NETWORK   : STUB Network

		Get an instance of the RouterLinkType class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.ospfv2routerlink.routerlinktype.routerlinktype.RouterLinkType)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.ospfv2routerlink.routerlinktype.routerlinktype import RouterLinkType
		return RouterLinkType(self)._read()

	@property
	def RouterLinkId(self):
		"""Link ID (IP address) to be used for the simulated link.

		Get an instance of the RouterLinkId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.ospfv2routerlink.routerlinkid.routerlinkid.RouterLinkId)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.ospfv2routerlink.routerlinkid.routerlinkid import RouterLinkId
		return RouterLinkId(self)._read()

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
		"""Get `ospfv2-router-link` resource(s). Returns all `ospfv2-router-link` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name):
		"""Create an instance of the `ospfv2-router-link` resource

		Args:
			Name (string): The unique name of the networks object.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `ospfv2-router-link` resource

		"""
		return self._delete()

