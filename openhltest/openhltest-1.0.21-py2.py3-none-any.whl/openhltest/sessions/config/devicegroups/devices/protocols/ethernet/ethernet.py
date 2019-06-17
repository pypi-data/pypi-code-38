from openhltest_client.base import Base


class Ethernet(Base):
	"""TBD
	"""
	YANG_NAME = 'ethernet'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ethernet, self).__init__(parent)

	@property
	def Mac(self):
		"""The mac address

		Get an instance of the Mac class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ethernet.mac.mac.Mac)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ethernet.mac.mac import Mac
		return Mac(self)._read()

