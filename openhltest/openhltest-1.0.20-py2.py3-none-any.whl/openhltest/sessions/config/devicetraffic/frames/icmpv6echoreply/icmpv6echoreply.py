from openhltest_client.base import Base


class Icmpv6EchoReply(Base):
	"""TBD
	"""
	YANG_NAME = 'icmpv6-echo-reply'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Icmpv6EchoReply, self).__init__(parent)

	@property
	def Code(self):
		"""ICMPv6 Echo reply code.

		Get an instance of the Code class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6echoreply.code.code.Code)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6echoreply.code.code import Code
		return Code(self)._read()

	@property
	def Identifier(self):
		"""Identifier value.

		Get an instance of the Identifier class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6echoreply.identifier.identifier.Identifier)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6echoreply.identifier.identifier import Identifier
		return Identifier(self)._read()

	@property
	def EchoData(self):
		"""Data value.

		Get an instance of the EchoData class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6echoreply.echodata.echodata.EchoData)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6echoreply.echodata.echodata import EchoData
		return EchoData(self)._read()

	@property
	def SequenceNumber(self):
		"""Sequence Number.

		Get an instance of the SequenceNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6echoreply.sequencenumber.sequencenumber.SequenceNumber)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6echoreply.sequencenumber.sequencenumber import SequenceNumber
		return SequenceNumber(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.
		Default: Automatically calculated for each packet.
		(If you set this to 0, the checksum will not be calculated and will be the same for each packet.)

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6echoreply.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6echoreply.checksum.checksum import Checksum
		return Checksum(self)._read()

