from openhltest_client.base import Base


class IcmpAddressMaskReply(Base):
	"""TBD
	"""
	YANG_NAME = 'icmp-address-mask-reply'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IcmpAddressMaskReply, self).__init__(parent)

	@property
	def Code(self):
		"""ICMP address mask reply code.

		Get an instance of the Code class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskreply.code.code.Code)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskreply.code.code import Code
		return Code(self)._read()

	@property
	def Identifier(self):
		"""Identifier value.

		Get an instance of the Identifier class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskreply.identifier.identifier.Identifier)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskreply.identifier.identifier import Identifier
		return Identifier(self)._read()

	@property
	def SequenceNumber(self):
		"""Sequence Number.

		Get an instance of the SequenceNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskreply.sequencenumber.sequencenumber.SequenceNumber)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskreply.sequencenumber.sequencenumber import SequenceNumber
		return SequenceNumber(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskreply.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskreply.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def AddressMask(self):
		"""Address Mask.

		Get an instance of the AddressMask class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskreply.addressmask.addressmask.AddressMask)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskreply.addressmask.addressmask import AddressMask
		return AddressMask(self)._read()

