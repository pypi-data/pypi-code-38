from openhltest_client.base import Base


class Ipv6(Base):
	"""TBD
	"""
	YANG_NAME = 'ipv6'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ipv6, self).__init__(parent)

	@property
	def SourceAddress(self):
		"""Specifies the source IPv6 address of the first generated packet.

		Get an instance of the SourceAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.sourceaddress.sourceaddress.SourceAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.sourceaddress.sourceaddress import SourceAddress
		return SourceAddress(self)._read()

	@property
	def DestinationAddress(self):
		"""Specifies the destination IPv6 address of the first generated packet.

		Get an instance of the DestinationAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.destinationaddress.destinationaddress.DestinationAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.destinationaddress.destinationaddress import DestinationAddress
		return DestinationAddress(self)._read()

	@property
	def TrafficClass(self):
		"""Specifies the IPv6 traffic class setting to use for application layer traffic.

		Get an instance of the TrafficClass class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.trafficclass.trafficclass.TrafficClass)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.trafficclass.trafficclass import TrafficClass
		return TrafficClass(self)._read()

	@property
	def FlowLabel(self):
		"""The flow label value of the IPv6 stream, which is a twenty- bit field is used for QoS management.

		Get an instance of the FlowLabel class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.flowlabel.flowlabel.FlowLabel)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.flowlabel.flowlabel import FlowLabel
		return FlowLabel(self)._read()

	@property
	def PayloadLength(self):
		"""The two-byte payload length field in the IPv6 header.

		Get an instance of the PayloadLength class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.payloadlength.payloadlength.PayloadLength)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.payloadlength.payloadlength import PayloadLength
		return PayloadLength(self)._read()

	@property
	def NextHeader(self):
		"""The next header field in the IPv6 header.

		Get an instance of the NextHeader class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.nextheader.nextheader.NextHeader)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.nextheader.nextheader import NextHeader
		return NextHeader(self)._read()

	@property
	def HopLimit(self):
		"""The hop limit field in the IPv6 header, which is an eight- bit field similar to TTL in IPv4.

		Get an instance of the HopLimit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.hoplimit.hoplimit.HopLimit)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.ipv6.hoplimit.hoplimit import HopLimit
		return HopLimit(self)._read()

