from openhltest_client.base import Base


class GlobalProtocols(Base):
	"""This list allows for configuring global protocols options.
	"""
	YANG_NAME = 'global-protocols'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(GlobalProtocols, self).__init__(parent)

	@property
	def Dhcpv4(self):
		"""This list allows for configuring global DHCPv4 options.

		Get an instance of the Dhcpv4 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.dhcpv4.Dhcpv4)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.dhcpv4 import Dhcpv4
		return Dhcpv4(self)

