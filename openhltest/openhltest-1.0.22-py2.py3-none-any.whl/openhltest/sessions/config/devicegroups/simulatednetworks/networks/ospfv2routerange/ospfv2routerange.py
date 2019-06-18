from openhltest_client.base import Base


class Ospfv2RouteRange(Base):
	"""OSPFV2 Router LSA
	"""
	YANG_NAME = 'ospfv2-route-range'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Active": "active"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ospfv2RouteRange, self).__init__(parent)

	@property
	def AdvertiseRouterId(self):
		"""Advertising Router ID.  Specifies the 32-bit router ID of the router that
		advertises a given LSA 

		Get an instance of the AdvertiseRouterId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.advertiserouterid.advertiserouterid.AdvertiseRouterId)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.advertiserouterid.advertiserouterid import AdvertiseRouterId
		return AdvertiseRouterId(self)._read()

	@property
	def RouterType(self):
		"""Router Type
		ASBR    : AS Boundary Router (E-bit set)
		ABR     : Border Router (B-bit set)

		Get an instance of the RouterType class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.routertype.routertype.RouterType)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.routertype.routertype import RouterType
		return RouterType(self)._read()

	@property
	def Options(self):
		"""Summary LSA Options.
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
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.options.options.Options)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.options.options import Options
		return Options(self)._read()

	@property
	def SequenceNumber(self):
		"""Sequence Number. Used to detect old and duplicate LSAs.

		Get an instance of the SequenceNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.sequencenumber.sequencenumber.SequenceNumber)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.sequencenumber.sequencenumber import SequenceNumber
		return SequenceNumber(self)._read()

	@property
	def Age(self):
		"""Age of the LSA, in seconds.

		Get an instance of the Age class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.age.age.Age)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.age.age import Age
		return Age(self)._read()

	@property
	def Ospfv2RouterLink(self):
		"""TBD

		Get an instance of the Ospfv2RouterLink class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.ospfv2routerlink.ospfv2routerlink.Ospfv2RouterLink)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2routerange.ospfv2routerlink.ospfv2routerlink import Ospfv2RouterLink
		return Ospfv2RouterLink(self)

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
		"""Update the current instance of the `ospfv2-route-range` resource

		Args:
			Active (boolean): TBD
		"""
		return self._update(locals())

