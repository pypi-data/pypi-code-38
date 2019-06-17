from openhltest_client.base import Base


class IcmpAddressMaskRequest(Base):
	"""TBD
	"""
	YANG_NAME = 'icmp-address-mask-request'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IcmpAddressMaskRequest, self).__init__(parent)

	@property
	def Code(self):
		"""ICMP address mask request code.

		Get an instance of the Code class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskrequest.code.code.Code)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskrequest.code.code import Code
		return Code(self)._read()

	@property
	def Identifier(self):
		"""Identifier value.

		Get an instance of the Identifier class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskrequest.identifier.identifier.Identifier)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskrequest.identifier.identifier import Identifier
		return Identifier(self)._read()

	@property
	def SequenceNumber(self):
		"""Sequence Number.

		Get an instance of the SequenceNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskrequest.sequencenumber.sequencenumber.SequenceNumber)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskrequest.sequencenumber.sequencenumber import SequenceNumber
		return SequenceNumber(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskrequest.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskrequest.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def AddressMask(self):
		"""Address Mask.

		Get an instance of the AddressMask class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskrequest.addressmask.addressmask.AddressMask)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpaddressmaskrequest.addressmask.addressmask import AddressMask
		return AddressMask(self)._read()

