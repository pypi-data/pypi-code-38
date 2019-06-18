from openhltest_client.base import Base


class IcmpRouterSolicitation(Base):
	"""TBD
	"""
	YANG_NAME = 'icmp-router-solicitation'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IcmpRouterSolicitation, self).__init__(parent)

	@property
	def Code(self):
		"""ICMP Router Solicitation code.

		Get an instance of the Code class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmproutersolicitation.code.code.Code)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmproutersolicitation.code.code import Code
		return Code(self)._read()

	@property
	def Reserved(self):
		"""Reserved.

		Get an instance of the Reserved class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmproutersolicitation.reserved.reserved.Reserved)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmproutersolicitation.reserved.reserved import Reserved
		return Reserved(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmproutersolicitation.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmproutersolicitation.checksum.checksum import Checksum
		return Checksum(self)._read()

