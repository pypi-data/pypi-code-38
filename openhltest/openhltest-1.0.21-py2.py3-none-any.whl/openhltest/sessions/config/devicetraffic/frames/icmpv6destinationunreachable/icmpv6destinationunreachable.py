from openhltest_client.base import Base


class Icmpv6DestinationUnreachable(Base):
	"""TBD
	"""
	YANG_NAME = 'icmpv6-destination-unreachable'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Icmpv6DestinationUnreachable, self).__init__(parent)

	@property
	def Code(self):
		"""ICMPv6 Destination Unreachable code.
		   NO_ROUTE            : No Route To Destination
		   PROHIBITED          : Communication with Destination Prohibited
		   ADDRESS_UNREACHABLE : Address Unreachable
		   PORT_UNREACHABLE    : Port Unreachable

		Get an instance of the Code class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.code.code.Code)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.code.code import Code
		return Code(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.
		Default: Automatically calculated for each packet.
		(If you set this to 0, the checksum will not be calculated and will be the same for each packet.)

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def Unused(self):
		"""Unused field.

		Get an instance of the Unused class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.unused.unused.Unused)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.unused.unused import Unused
		return Unused(self)._read()

	@property
	def Ipv6SourceAddress(self):
		"""Source IPv6 Address

		Get an instance of the Ipv6SourceAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6sourceaddress.ipv6sourceaddress.Ipv6SourceAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6sourceaddress.ipv6sourceaddress import Ipv6SourceAddress
		return Ipv6SourceAddress(self)._read()

	@property
	def Ipv6DestinationAddress(self):
		"""Destination IPv6 Address

		Get an instance of the Ipv6DestinationAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6destinationaddress.ipv6destinationaddress.Ipv6DestinationAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6destinationaddress.ipv6destinationaddress import Ipv6DestinationAddress
		return Ipv6DestinationAddress(self)._read()

	@property
	def Ipv6GatewayAddress(self):
		"""Gateway IPv6 Address

		Get an instance of the Ipv6GatewayAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6gatewayaddress.ipv6gatewayaddress.Ipv6GatewayAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6gatewayaddress.ipv6gatewayaddress import Ipv6GatewayAddress
		return Ipv6GatewayAddress(self)._read()

	@property
	def Ipv6HopLimit(self):
		"""The hop limit field in the IPv6 header, which is an eight- bit field similar to TTL in IPv4.

		Get an instance of the Ipv6HopLimit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6hoplimit.ipv6hoplimit.Ipv6HopLimit)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6hoplimit.ipv6hoplimit import Ipv6HopLimit
		return Ipv6HopLimit(self)._read()

	@property
	def Ipv6TrafficClass(self):
		"""Specifies the IPv6 traffic class setting to use for application layer traffic.

		Get an instance of the Ipv6TrafficClass class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6trafficclass.ipv6trafficclass.Ipv6TrafficClass)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6trafficclass.ipv6trafficclass import Ipv6TrafficClass
		return Ipv6TrafficClass(self)._read()

	@property
	def Ipv6NextHeader(self):
		"""Indicates the type of L4 protocol in the IP header.

		Get an instance of the Ipv6NextHeader class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6nextheader.ipv6nextheader.Ipv6NextHeader)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6nextheader.ipv6nextheader import Ipv6NextHeader
		return Ipv6NextHeader(self)._read()

	@property
	def Ipv6PayloadLength(self):
		"""Payload Length.

		Get an instance of the Ipv6PayloadLength class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6payloadlength.ipv6payloadlength.Ipv6PayloadLength)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6payloadlength.ipv6payloadlength import Ipv6PayloadLength
		return Ipv6PayloadLength(self)._read()

	@property
	def Ipv6FlowLabel(self):
		"""The flow label value of the IPv6 stream, which is a twenty- bit field is used for QoS management.

		Get an instance of the Ipv6FlowLabel class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6flowlabel.ipv6flowlabel.Ipv6FlowLabel)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6flowlabel.ipv6flowlabel import Ipv6FlowLabel
		return Ipv6FlowLabel(self)._read()

	@property
	def Ipv6Data(self):
		"""Dataplane of IP header.

		Get an instance of the Ipv6Data class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6data.ipv6data.Ipv6Data)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmpv6destinationunreachable.ipv6data.ipv6data import Ipv6Data
		return Ipv6Data(self)._read()

