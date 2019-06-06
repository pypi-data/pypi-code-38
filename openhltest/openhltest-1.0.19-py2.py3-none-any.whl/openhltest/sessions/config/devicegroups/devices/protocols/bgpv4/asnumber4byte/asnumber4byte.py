from openhltest_client.base import Base


class AsNumber4Byte(Base):
	"""Enables the use of 4 Byte Autonomous system number
	"""
	YANG_NAME = 'as-number-4-byte'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(AsNumber4Byte, self).__init__(parent)

	@property
	def AsNumber(self):
		"""4-Byte Autonomous system number

		Get an instance of the AsNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.asnumber4byte.asnumber.asnumber.AsNumber)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.asnumber4byte.asnumber.asnumber import AsNumber
		return AsNumber(self)._read()

	@property
	def DutAsNumber(self):
		"""4-Byte Autonomous system number configured for the DUT.

		Get an instance of the DutAsNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.asnumber4byte.dutasnumber.dutasnumber.DutAsNumber)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.asnumber4byte.dutasnumber.dutasnumber import DutAsNumber
		return DutAsNumber(self)._read()

