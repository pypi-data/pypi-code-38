from openhltest_client.base import Base


class Ipv6(Base):
	"""TBD
	"""
	YANG_NAME = 'ipv6'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ipv6, self).__init__(parent)

	@property
	def SourceAddress(self):
		"""TBD

		Get an instance of the SourceAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv6.sourceaddress.sourceaddress.SourceAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv6.sourceaddress.sourceaddress import SourceAddress
		return SourceAddress(self)._read()

	@property
	def GatewayAddress(self):
		"""TBD

		Get an instance of the GatewayAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv6.gatewayaddress.gatewayaddress.GatewayAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv6.gatewayaddress.gatewayaddress import GatewayAddress
		return GatewayAddress(self)._read()

	@property
	def LinkLocalAddress(self):
		"""TBD

		Get an instance of the LinkLocalAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv6.linklocaladdress.linklocaladdress.LinkLocalAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv6.linklocaladdress.linklocaladdress import LinkLocalAddress
		return LinkLocalAddress(self)._read()

