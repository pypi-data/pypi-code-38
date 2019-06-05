from openhltest_client.base import Base


class IcmpInformationRequest(Base):
	"""TBD
	"""
	YANG_NAME = 'icmp-information-request'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IcmpInformationRequest, self).__init__(parent)

	@property
	def Code(self):
		"""ICMP information request code.

		Get an instance of the Code class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationrequest.code.code.Code)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationrequest.code.code import Code
		return Code(self)._read()

	@property
	def Identifier(self):
		"""Identifier value.

		Get an instance of the Identifier class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationrequest.identifier.identifier.Identifier)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationrequest.identifier.identifier import Identifier
		return Identifier(self)._read()

	@property
	def SequenceNumber(self):
		"""Sequence Number.

		Get an instance of the SequenceNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationrequest.sequencenumber.sequencenumber.SequenceNumber)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationrequest.sequencenumber.sequencenumber import SequenceNumber
		return SequenceNumber(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationrequest.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationrequest.checksum.checksum import Checksum
		return Checksum(self)._read()

