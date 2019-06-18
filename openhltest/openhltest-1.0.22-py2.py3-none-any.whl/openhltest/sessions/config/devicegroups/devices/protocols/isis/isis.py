from openhltest_client.base import Base


class Isis(Base):
	"""TBD
	"""
	YANG_NAME = 'isis'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Isis, self).__init__(parent)

	@property
	def SystemId(self):
		"""The System ID is used to identify an emulated router.

		Get an instance of the SystemId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.systemid.systemid.SystemId)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.systemid.systemid import SystemId
		return SystemId(self)._read()

	@property
	def IpVersion(self):
		"""IP Version
		           IPV4 : IPv4
		           IPV6 : IPv6
		           BOTH : IPv4 and IPv6

		Get an instance of the IpVersion class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.ipversion.ipversion.IpVersion)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.ipversion.ipversion import IpVersion
		return IpVersion(self)._read()

	@property
	def NetworkType(self):
		"""This setting to override the physical link type to emulate a broadcast
		           adjacency over POS, or a point-to-point adjacency over Ethernet
		           BROADCAST : Broadcast adjacency
		           P2P       : P2P (point-to-point) adjacency

		Get an instance of the NetworkType class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.networktype.networktype.NetworkType)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.networktype.networktype import NetworkType
		return NetworkType(self)._read()

	@property
	def RouterPriority(self):
		"""Router priority of the emulated router. Set the router priority to a higher
		           or lower value to influence the DR and BDR selection process.

		Get an instance of the RouterPriority class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.routerpriority.routerpriority.RouterPriority)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.routerpriority.routerpriority import RouterPriority
		return RouterPriority(self)._read()

	@property
	def Level(self):
		"""This is the circuit type of the emulated router. It defines the type of adjacency
		           Traffic Generator establishes with the DUT..

		Get an instance of the Level class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.level.level.Level)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.level.level import Level
		return Level(self)._read()

	@property
	def HelloInterval(self):
		"""Time interval (in seconds) used by the emulated routers to pace Hello packet
		           transmissions.

		Get an instance of the HelloInterval class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.hellointerval.hellointerval.HelloInterval)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.hellointerval.hellointerval import HelloInterval
		return HelloInterval(self)._read()

	@property
	def Authentication(self):
		"""Type of authentication to be used
		   NONE   : no authentication
		   SIMPLE : The packet is authenticated by the receiving router if the password
		            matches the authentication key that is included in the packet.
		            This method provides little security because the authentication
		            key can be learned by capturing packets.
		   MD5    : The packet contains a cryptographic checksum, but not the authentication
		           key itself. The receiving router performs a calculation based on the
		           MD5 algorithm and an authentication key ID. The packet is authenticated
		           if the calculated checksum matches. This method provides a stronger
		           assurance that routing data originated from a router with a valid
		           authentication key.

		Get an instance of the Authentication class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.authentication.authentication.Authentication)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.authentication.authentication import Authentication
		return Authentication(self)._read()

