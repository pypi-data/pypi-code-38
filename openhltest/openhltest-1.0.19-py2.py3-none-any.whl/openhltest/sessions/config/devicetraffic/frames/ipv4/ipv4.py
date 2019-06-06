from openhltest_client.base import Base


class Ipv4(Base):
	"""TBD
	"""
	YANG_NAME = 'ipv4'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ipv4, self).__init__(parent)

	@property
	def SourceAddress(self):
		"""Source IPv4 Address

		Get an instance of the SourceAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.sourceaddress.sourceaddress.SourceAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.sourceaddress.sourceaddress import SourceAddress
		return SourceAddress(self)._read()

	@property
	def DestinationAddress(self):
		"""Destination IPv4 Address

		Get an instance of the DestinationAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.destinationaddress.destinationaddress.DestinationAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.destinationaddress.destinationaddress import DestinationAddress
		return DestinationAddress(self)._read()

	@property
	def Ttl(self):
		"""The limited number of iterations that a unit of data can experience before
		           the data is discarded.

		Get an instance of the Ttl class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.ttl.ttl.Ttl)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.ttl.ttl import Ttl
		return Ttl(self)._read()

	@property
	def HeaderLength(self):
		"""The length of the IP header field in number of bytes.

		Get an instance of the HeaderLength class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.headerlength.headerlength.HeaderLength)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.headerlength.headerlength import HeaderLength
		return HeaderLength(self)._read()

	@property
	def Identification(self):
		"""Specifies the identifying value used to help assemble the fragments of a datagram.

		Get an instance of the Identification class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.identification.identification.Identification)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.identification.identification import Identification
		return Identification(self)._read()

	@property
	def FragmentOffset(self):
		"""The byte count from the start of the original sent packet.

		Get an instance of the FragmentOffset class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.fragmentoffset.fragmentoffset.FragmentOffset)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.fragmentoffset.fragmentoffset import FragmentOffset
		return FragmentOffset(self)._read()

	@property
	def Protocol(self):
		"""Indicates the type of L4 protocol in the IP header.

		Get an instance of the Protocol class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.protocol.protocol.Protocol)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.protocol.protocol import Protocol
		return Protocol(self)._read()

	@property
	def Checksum(self):
		"""Verifies that packets are not corrupted.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def ReservedBit(self):
		"""Specifies the reserved bit in the Flags field of the internet header.

		Get an instance of the ReservedBit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.reservedbit.reservedbit.ReservedBit)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.reservedbit.reservedbit import ReservedBit
		return ReservedBit(self)._read()

	@property
	def MfBit(self):
		"""Specifies the More Fragment (MF) bit in the Flags field of the internet header.

		Get an instance of the MfBit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.mfbit.mfbit.MfBit)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.mfbit.mfbit import MfBit
		return MfBit(self)._read()

	@property
	def DfBit(self):
		"""Specifies whether the datagram is fragmented.

		Get an instance of the DfBit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.dfbit.dfbit.DfBit)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv4.dfbit.dfbit import DfBit
		return DfBit(self)._read()

