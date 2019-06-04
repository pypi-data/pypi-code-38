from openhltest_client.base import Base


class IsisRouteRange(Base):
	"""TBD
	"""
	YANG_NAME = 'isis-route-range'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IsisRouteRange, self).__init__(parent)

	@property
	def SystemId(self):
		"""System ID.

		Get an instance of the SystemId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.systemid.systemid.SystemId)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.systemid.systemid import SystemId
		return SystemId(self)._read()

	@property
	def SequenceNumber(self):
		"""Sequence Number. Used to detect old and duplicate LSAs.

		Get an instance of the SequenceNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.sequencenumber.sequencenumber.SequenceNumber)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.sequencenumber.sequencenumber import SequenceNumber
		return SequenceNumber(self)._read()

	@property
	def Level(self):
		"""This is the circuit type of the emulated router. It defines the type of adjacency
		           Traffic Generator establishes with the DUT..

		Get an instance of the Level class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.level.level.Level)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.level.level import Level
		return Level(self)._read()

	@property
	def Ipv4Routes(self):
		"""TBD

		Get an instance of the Ipv4Routes class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.ipv4routes.ipv4routes.Ipv4Routes)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.ipv4routes.ipv4routes import Ipv4Routes
		return Ipv4Routes(self)

	@property
	def Ipv6Routes(self):
		"""TBD

		Get an instance of the Ipv6Routes class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.ipv6routes.ipv6routes.Ipv6Routes)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.isisrouterange.ipv6routes.ipv6routes import Ipv6Routes
		return Ipv6Routes(self)

