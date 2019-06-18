from openhltest_client.base import Base


class Ipv4(Base):
	"""TBD
	"""
	YANG_NAME = 'ipv4'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ipv4, self).__init__(parent)

	@property
	def SourceAddress(self):
		"""TBD

		Get an instance of the SourceAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv4.sourceaddress.sourceaddress.SourceAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv4.sourceaddress.sourceaddress import SourceAddress
		return SourceAddress(self)._read()

	@property
	def GatewayAddress(self):
		"""TBD

		Get an instance of the GatewayAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv4.gatewayaddress.gatewayaddress.GatewayAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv4.gatewayaddress.gatewayaddress import GatewayAddress
		return GatewayAddress(self)._read()

	@property
	def Prefix(self):
		"""TBD

		Get an instance of the Prefix class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv4.prefix.prefix.Prefix)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv4.prefix.prefix import Prefix
		return Prefix(self)._read()

