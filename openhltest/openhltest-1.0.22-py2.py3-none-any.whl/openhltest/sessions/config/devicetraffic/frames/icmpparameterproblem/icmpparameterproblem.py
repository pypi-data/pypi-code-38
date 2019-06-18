from openhltest_client.base import Base


class IcmpParameterProblem(Base):
	"""TBD
	"""
	YANG_NAME = 'icmp-parameter-problem'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IcmpParameterProblem, self).__init__(parent)

	@property
	def Code(self):
		"""ICMP Destination Parameter problem code.

		Get an instance of the Code class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.code.code.Code)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.code.code import Code
		return Code(self)._read()

	@property
	def Pointer(self):
		"""Pointer value.

		Get an instance of the Pointer class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.pointer.pointer.Pointer)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.pointer.pointer import Pointer
		return Pointer(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def Unused(self):
		"""Unused field.

		Get an instance of the Unused class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.unused.unused.Unused)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.unused.unused import Unused
		return Unused(self)._read()

	@property
	def Ipv4SourceAddress(self):
		"""Source IPv4 Address

		Get an instance of the Ipv4SourceAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4sourceaddress.ipv4sourceaddress.Ipv4SourceAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4sourceaddress.ipv4sourceaddress import Ipv4SourceAddress
		return Ipv4SourceAddress(self)._read()

	@property
	def Ipv4DestinationAddress(self):
		"""Destination IPv4 Address

		Get an instance of the Ipv4DestinationAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4destinationaddress.ipv4destinationaddress.Ipv4DestinationAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4destinationaddress.ipv4destinationaddress import Ipv4DestinationAddress
		return Ipv4DestinationAddress(self)._read()

	@property
	def Ipv4GatewayAddress(self):
		"""Gateway IPv4 Address

		Get an instance of the Ipv4GatewayAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4gatewayaddress.ipv4gatewayaddress.Ipv4GatewayAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4gatewayaddress.ipv4gatewayaddress import Ipv4GatewayAddress
		return Ipv4GatewayAddress(self)._read()

	@property
	def Ipv4Ttl(self):
		"""The limited number of iterations that a unit of data can experience before
		the data is discarded.

		Get an instance of the Ipv4Ttl class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4ttl.ipv4ttl.Ipv4Ttl)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4ttl.ipv4ttl import Ipv4Ttl
		return Ipv4Ttl(self)._read()

	@property
	def Ipv4Protocol(self):
		"""Indicates the type of L4 protocol in the IP header.

		Get an instance of the Ipv4Protocol class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4protocol.ipv4protocol.Ipv4Protocol)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4protocol.ipv4protocol import Ipv4Protocol
		return Ipv4Protocol(self)._read()

	@property
	def Ipv4FragmentOffset(self):
		"""The byte count from the start of the original sent packet.

		Get an instance of the Ipv4FragmentOffset class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4fragmentoffset.ipv4fragmentoffset.Ipv4FragmentOffset)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4fragmentoffset.ipv4fragmentoffset import Ipv4FragmentOffset
		return Ipv4FragmentOffset(self)._read()

	@property
	def Ipv4Identification(self):
		"""Specifies the identifying value used to help assemble the fragments of a datagram.

		Get an instance of the Ipv4Identification class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4identification.ipv4identification.Ipv4Identification)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4identification.ipv4identification import Ipv4Identification
		return Ipv4Identification(self)._read()

	@property
	def Ipv4ReservedBit(self):
		"""Specifies the reserved bit in the Flags field of the internet header.

		Get an instance of the Ipv4ReservedBit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4reservedbit.ipv4reservedbit.Ipv4ReservedBit)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4reservedbit.ipv4reservedbit import Ipv4ReservedBit
		return Ipv4ReservedBit(self)._read()

	@property
	def Ipv4MfBit(self):
		"""Specifies the More Fragment (MF) bit in the Flags field of the internet header.

		Get an instance of the Ipv4MfBit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4mfbit.ipv4mfbit.Ipv4MfBit)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4mfbit.ipv4mfbit import Ipv4MfBit
		return Ipv4MfBit(self)._read()

	@property
	def Ipv4DfBit(self):
		"""Specifies whether the datagram is fragmented.

		Get an instance of the Ipv4DfBit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4dfbit.ipv4dfbit.Ipv4DfBit)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4dfbit.ipv4dfbit import Ipv4DfBit
		return Ipv4DfBit(self)._read()

	@property
	def Ipv4HeaderLength(self):
		"""The length of the IP header field in number of bytes.

		Get an instance of the Ipv4HeaderLength class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4headerlength.ipv4headerlength.Ipv4HeaderLength)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4headerlength.ipv4headerlength import Ipv4HeaderLength
		return Ipv4HeaderLength(self)._read()

	@property
	def Ipv4TotalLength(self):
		"""The total length of the IP header.

		Get an instance of the Ipv4TotalLength class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4totallength.ipv4totallength.Ipv4TotalLength)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4totallength.ipv4totallength import Ipv4TotalLength
		return Ipv4TotalLength(self)._read()

	@property
	def Ipv4Checksum(self):
		"""The header checksum is calculated over the IP header only.
		It does not cover any data that follows the header.

		Get an instance of the Ipv4Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4checksum.ipv4checksum.Ipv4Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4checksum.ipv4checksum import Ipv4Checksum
		return Ipv4Checksum(self)._read()

	@property
	def Ipv4Data(self):
		"""Dataplane of IP header.

		Get an instance of the Ipv4Data class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4data.ipv4data.Ipv4Data)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpparameterproblem.ipv4data.ipv4data import Ipv4Data
		return Ipv4Data(self)._read()

