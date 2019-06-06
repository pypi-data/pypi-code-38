from openhltest_client.base import Base


class IcmpInformationReply(Base):
	"""TBD
	"""
	YANG_NAME = 'icmp-information-reply'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IcmpInformationReply, self).__init__(parent)

	@property
	def Code(self):
		"""ICMP information reply code.

		Get an instance of the Code class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationreply.code.code.Code)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationreply.code.code import Code
		return Code(self)._read()

	@property
	def Identifier(self):
		"""Identifier value.

		Get an instance of the Identifier class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationreply.identifier.identifier.Identifier)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationreply.identifier.identifier import Identifier
		return Identifier(self)._read()

	@property
	def SequenceNumber(self):
		"""Sequence Number.

		Get an instance of the SequenceNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationreply.sequencenumber.sequencenumber.SequenceNumber)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationreply.sequencenumber.sequencenumber import SequenceNumber
		return SequenceNumber(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationreply.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationreply.checksum.checksum import Checksum
		return Checksum(self)._read()

