from openhltest_client.base import Base


class Ospfv3RouteRange(Base):
	"""TBD
	"""
	YANG_NAME = 'ospfv3-route-range'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Active": "active"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ospfv3RouteRange, self).__init__(parent)

	@property
	def AdvertiseRouterId(self):
		"""Advertising Router ID.  Specifies the 32-bit router ID of the router that
		advertises a given LSA 

		Get an instance of the AdvertiseRouterId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.advertiserouterid.advertiserouterid.AdvertiseRouterId)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.advertiserouterid.advertiserouterid import AdvertiseRouterId
		return AdvertiseRouterId(self)._read()

	@property
	def RouterType(self):
		"""Router Type
		ASBR    : AS Boundary Router (E-bit set)
		ABR     : Border Router (B-bit set)

		Get an instance of the RouterType class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.routertype.routertype.RouterType)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.routertype.routertype import RouterType
		return RouterType(self)._read()

	@property
	def SequenceNumber(self):
		"""Sequence Number. Used to detect old and duplicate LSAs.

		Get an instance of the SequenceNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.sequencenumber.sequencenumber.SequenceNumber)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.sequencenumber.sequencenumber import SequenceNumber
		return SequenceNumber(self)._read()

	@property
	def Age(self):
		"""Age of the LSA, in seconds.

		Get an instance of the Age class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.age.age.Age)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.age.age import Age
		return Age(self)._read()

	@property
	def Ospfv3RouterLink(self):
		"""TBD

		Get an instance of the Ospfv3RouterLink class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.ospfv3routerlink.ospfv3routerlink.Ospfv3RouterLink)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3routerange.ospfv3routerlink.ospfv3routerlink import Ospfv3RouterLink
		return Ospfv3RouterLink(self)

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
		"""Update the current instance of the `ospfv3-route-range` resource

		Args:
			Active (boolean): TBD
		"""
		return self._update(locals())

