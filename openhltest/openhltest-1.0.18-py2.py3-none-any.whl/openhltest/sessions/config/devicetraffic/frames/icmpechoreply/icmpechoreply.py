from openhltest_client.base import Base


class IcmpEchoReply(Base):
	"""TBD
	"""
	YANG_NAME = 'icmp-echo-reply'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IcmpEchoReply, self).__init__(parent)

	@property
	def Code(self):
		"""ICMP Echo reply code.

		Get an instance of the Code class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpechoreply.code.code.Code)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpechoreply.code.code import Code
		return Code(self)._read()

	@property
	def Identifier(self):
		"""Identifier value.

		Get an instance of the Identifier class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpechoreply.identifier.identifier.Identifier)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpechoreply.identifier.identifier import Identifier
		return Identifier(self)._read()

	@property
	def EchoData(self):
		"""Data value.

		Get an instance of the EchoData class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpechoreply.echodata.echodata.EchoData)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpechoreply.echodata.echodata import EchoData
		return EchoData(self)._read()

	@property
	def SequenceNumber(self):
		"""Sequence Number.

		Get an instance of the SequenceNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpechoreply.sequencenumber.sequencenumber.SequenceNumber)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpechoreply.sequencenumber.sequencenumber import SequenceNumber
		return SequenceNumber(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpechoreply.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpechoreply.checksum.checksum import Checksum
		return Checksum(self)._read()

