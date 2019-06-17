from openhltest_client.base import Base


class Frames(Base):
	"""List of user defined frames.
	The order of frames in the list will be the order of frames on the wire

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/port-traffic/frames resource.
	"""
	YANG_NAME = 'frames'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name", "FrameType": "frame-type"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Frames, self).__init__(parent)

	@property
	def Ethernet(self):
		"""TBD

		Get an instance of the Ethernet class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ethernet.ethernet.Ethernet)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ethernet.ethernet import Ethernet
		return Ethernet(self)._read()

	@property
	def Vlan(self):
		"""TBD

		Get an instance of the Vlan class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.vlan.vlan.Vlan)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.vlan.vlan import Vlan
		return Vlan(self)._read()

	@property
	def Ipv4(self):
		"""TBD

		Get an instance of the Ipv4 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ipv4.ipv4.Ipv4)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ipv4.ipv4 import Ipv4
		return Ipv4(self)._read()

	@property
	def Ipv6(self):
		"""TBD

		Get an instance of the Ipv6 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ipv6.ipv6.Ipv6)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ipv6.ipv6 import Ipv6
		return Ipv6(self)._read()

	@property
	def Tcp(self):
		"""TBD

		Get an instance of the Tcp class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.tcp.Tcp)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.tcp import Tcp
		return Tcp(self)._read()

	@property
	def Udp(self):
		"""TBD

		Get an instance of the Udp class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.udp.udp.Udp)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.udp.udp import Udp
		return Udp(self)._read()

	@property
	def Gre(self):
		"""TBD

		Get an instance of the Gre class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.gre.gre.Gre)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.gre.gre import Gre
		return Gre(self)._read()

	@property
	def IcmpDestinationUnreachable(self):
		"""TBD

		Get an instance of the IcmpDestinationUnreachable class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpdestinationunreachable.icmpdestinationunreachable.IcmpDestinationUnreachable)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpdestinationunreachable.icmpdestinationunreachable import IcmpDestinationUnreachable
		return IcmpDestinationUnreachable(self)._read()

	@property
	def IcmpEchoReply(self):
		"""TBD

		Get an instance of the IcmpEchoReply class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpechoreply.icmpechoreply.IcmpEchoReply)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpechoreply.icmpechoreply import IcmpEchoReply
		return IcmpEchoReply(self)._read()

	@property
	def IcmpEchoRequest(self):
		"""TBD

		Get an instance of the IcmpEchoRequest class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpechorequest.icmpechorequest.IcmpEchoRequest)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpechorequest.icmpechorequest import IcmpEchoRequest
		return IcmpEchoRequest(self)._read()

	@property
	def IcmpInformationReply(self):
		"""TBD

		Get an instance of the IcmpInformationReply class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationreply.icmpinformationreply.IcmpInformationReply)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationreply.icmpinformationreply import IcmpInformationReply
		return IcmpInformationReply(self)._read()

	@property
	def IcmpInformationRequest(self):
		"""TBD

		Get an instance of the IcmpInformationRequest class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationrequest.icmpinformationrequest.IcmpInformationRequest)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpinformationrequest.icmpinformationrequest import IcmpInformationRequest
		return IcmpInformationRequest(self)._read()

	@property
	def IcmpAddressMaskReply(self):
		"""TBD

		Get an instance of the IcmpAddressMaskReply class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpaddressmaskreply.icmpaddressmaskreply.IcmpAddressMaskReply)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpaddressmaskreply.icmpaddressmaskreply import IcmpAddressMaskReply
		return IcmpAddressMaskReply(self)._read()

	@property
	def IcmpAddressMaskRequest(self):
		"""TBD

		Get an instance of the IcmpAddressMaskRequest class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpaddressmaskrequest.icmpaddressmaskrequest.IcmpAddressMaskRequest)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpaddressmaskrequest.icmpaddressmaskrequest import IcmpAddressMaskRequest
		return IcmpAddressMaskRequest(self)._read()

	@property
	def IcmpParameterProblem(self):
		"""TBD

		Get an instance of the IcmpParameterProblem class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpparameterproblem.icmpparameterproblem.IcmpParameterProblem)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpparameterproblem.icmpparameterproblem import IcmpParameterProblem
		return IcmpParameterProblem(self)._read()

	@property
	def IcmpRedirect(self):
		"""TBD

		Get an instance of the IcmpRedirect class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpredirect.icmpredirect.IcmpRedirect)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpredirect.icmpredirect import IcmpRedirect
		return IcmpRedirect(self)._read()

	@property
	def IcmpRouterAdvertisement(self):
		"""TBD

		Get an instance of the IcmpRouterAdvertisement class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmprouteradvertisement.icmprouteradvertisement.IcmpRouterAdvertisement)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmprouteradvertisement.icmprouteradvertisement import IcmpRouterAdvertisement
		return IcmpRouterAdvertisement(self)._read()

	@property
	def IcmpRouterSolicitation(self):
		"""TBD

		Get an instance of the IcmpRouterSolicitation class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmproutersolicitation.icmproutersolicitation.IcmpRouterSolicitation)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmproutersolicitation.icmproutersolicitation import IcmpRouterSolicitation
		return IcmpRouterSolicitation(self)._read()

	@property
	def IcmpSourceQuench(self):
		"""TBD

		Get an instance of the IcmpSourceQuench class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpsourcequench.icmpsourcequench.IcmpSourceQuench)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpsourcequench.icmpsourcequench import IcmpSourceQuench
		return IcmpSourceQuench(self)._read()

	@property
	def IcmpTimeExceeded(self):
		"""TBD

		Get an instance of the IcmpTimeExceeded class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimeexceeded.icmptimeexceeded.IcmpTimeExceeded)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimeexceeded.icmptimeexceeded import IcmpTimeExceeded
		return IcmpTimeExceeded(self)._read()

	@property
	def IcmpTimestampReply(self):
		"""TBD

		Get an instance of the IcmpTimestampReply class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestampreply.icmptimestampreply.IcmpTimestampReply)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestampreply.icmptimestampreply import IcmpTimestampReply
		return IcmpTimestampReply(self)._read()

	@property
	def IcmpTimestampRequest(self):
		"""TBD

		Get an instance of the IcmpTimestampRequest class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.icmptimestamprequest.IcmpTimestampRequest)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.icmptimestamprequest import IcmpTimestampRequest
		return IcmpTimestampRequest(self)._read()

	@property
	def Icmpv6DestinationUnreachable(self):
		"""TBD

		Get an instance of the Icmpv6DestinationUnreachable class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpv6destinationunreachable.icmpv6destinationunreachable.Icmpv6DestinationUnreachable)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpv6destinationunreachable.icmpv6destinationunreachable import Icmpv6DestinationUnreachable
		return Icmpv6DestinationUnreachable(self)._read()

	@property
	def Icmpv6EchoReply(self):
		"""TBD

		Get an instance of the Icmpv6EchoReply class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpv6echoreply.icmpv6echoreply.Icmpv6EchoReply)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpv6echoreply.icmpv6echoreply import Icmpv6EchoReply
		return Icmpv6EchoReply(self)._read()

	@property
	def Icmpv6EchoRequest(self):
		"""TBD

		Get an instance of the Icmpv6EchoRequest class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpv6echorequest.icmpv6echorequest.Icmpv6EchoRequest)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpv6echorequest.icmpv6echorequest import Icmpv6EchoRequest
		return Icmpv6EchoRequest(self)._read()

	@property
	def Icmpv6ParameterProblem(self):
		"""TBD

		Get an instance of the Icmpv6ParameterProblem class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpv6parameterproblem.icmpv6parameterproblem.Icmpv6ParameterProblem)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpv6parameterproblem.icmpv6parameterproblem import Icmpv6ParameterProblem
		return Icmpv6ParameterProblem(self)._read()

	@property
	def Icmpv6TimeExceeded(self):
		"""TBD

		Get an instance of the Icmpv6TimeExceeded class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpv6timeexceeded.icmpv6timeexceeded.Icmpv6TimeExceeded)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpv6timeexceeded.icmpv6timeexceeded import Icmpv6TimeExceeded
		return Icmpv6TimeExceeded(self)._read()

	@property
	def Icmpv6PacketTooBig(self):
		"""TBD

		Get an instance of the Icmpv6PacketTooBig class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpv6packettoobig.icmpv6packettoobig.Icmpv6PacketTooBig)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmpv6packettoobig.icmpv6packettoobig import Icmpv6PacketTooBig
		return Icmpv6PacketTooBig(self)._read()

	@property
	def Igmpv1Query(self):
		"""IGMPv1 Query message

		Get an instance of the Igmpv1Query class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1query.igmpv1query.Igmpv1Query)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1query.igmpv1query import Igmpv1Query
		return Igmpv1Query(self)._read()

	@property
	def Igmpv1Report(self):
		"""IGMPv1 Report message

		Get an instance of the Igmpv1Report class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1report.igmpv1report.Igmpv1Report)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1report.igmpv1report import Igmpv1Report
		return Igmpv1Report(self)._read()

	@property
	def Igmpv2Query(self):
		"""IGMPv2 Query message

		Get an instance of the Igmpv2Query class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv2query.igmpv2query.Igmpv2Query)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv2query.igmpv2query import Igmpv2Query
		return Igmpv2Query(self)._read()

	@property
	def Igmpv2Report(self):
		"""IGMPv2 Report message

		Get an instance of the Igmpv2Report class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv2report.igmpv2report.Igmpv2Report)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv2report.igmpv2report import Igmpv2Report
		return Igmpv2Report(self)._read()

	@property
	def Igmpv3Query(self):
		"""IGMPv3 Query message

		Get an instance of the Igmpv3Query class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv3query.igmpv3query.Igmpv3Query)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv3query.igmpv3query import Igmpv3Query
		return Igmpv3Query(self)._read()

	@property
	def Igmpv3Report(self):
		"""IGMPv3 Report message

		Get an instance of the Igmpv3Report class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv3report.igmpv3report.Igmpv3Report)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv3report.igmpv3report import Igmpv3Report
		return Igmpv3Report(self)._read()

	@property
	def Ospfv2Hello(self):
		"""TBD

		Get an instance of the Ospfv2Hello class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.ospfv2hello.Ospfv2Hello)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.ospfv2hello import Ospfv2Hello
		return Ospfv2Hello(self)._read()

	@property
	def Custom(self):
		"""TBD

		Get an instance of the Custom class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.custom.custom.Custom)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.custom.custom import Custom
		return Custom(self)._read()

	@property
	def Name(self):
		"""TBD

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('name')

	@property
	def FrameType(self):
		"""TBD

		Getter Returns:
			CUSTOM | ETHERNET | VLAN | IPV4 | IPV6 | TCP | UDP | GRE | ICMP_DESTINATION_UNREACHABLE | ICMP_ECHO_REPLY | ICMP_ECHO_REQUEST | ICMP_INFORMATION_REPLY | ICMP_INFORMATION_REQUEST | ICMP_ADDRESS_MASK_REPLY | ICMP_ADDRESS_MASK_REQUEST | ICMP_PARAMETER_PROBLEM | ICMP_REDIRECT | ICMP_ROUTER_ADVERTISEMENT | ICMP_ROUTER_SOLICITATION | ICMP_SOURCE_QUENCH | ICMP_TIME_EXCEEDED | ICMP_TIMESTAMP_REPLY | ICMP_TIMESTAMP_REQUEST | ICMPV6_DESTINATION_UNREACHABLE | ICMPV6_ECHO_REPLY | ICMPV6_ECHO_REQUEST | ICMPV6_PARAMETER_PROBLEM | ICMPV6_TIME_EXCEEDED | ICMPV6_PACKET_TOO_BIG | IGMPV1_QUERY | IGMPV1_REPORT | IGMPV2_QUERY | IGMPV2_REPORT | IGMPV3_QUERY | IGMPV3_REPORT | OSPFV2_HELLO

		Setter Allows:
			CUSTOM | ETHERNET | VLAN | IPV4 | IPV6 | TCP | UDP | GRE | ICMP_DESTINATION_UNREACHABLE | ICMP_ECHO_REPLY | ICMP_ECHO_REQUEST | ICMP_INFORMATION_REPLY | ICMP_INFORMATION_REQUEST | ICMP_ADDRESS_MASK_REPLY | ICMP_ADDRESS_MASK_REQUEST | ICMP_PARAMETER_PROBLEM | ICMP_REDIRECT | ICMP_ROUTER_ADVERTISEMENT | ICMP_ROUTER_SOLICITATION | ICMP_SOURCE_QUENCH | ICMP_TIME_EXCEEDED | ICMP_TIMESTAMP_REPLY | ICMP_TIMESTAMP_REQUEST | ICMPV6_DESTINATION_UNREACHABLE | ICMPV6_ECHO_REPLY | ICMPV6_ECHO_REQUEST | ICMPV6_PARAMETER_PROBLEM | ICMPV6_TIME_EXCEEDED | ICMPV6_PACKET_TOO_BIG | IGMPV1_QUERY | IGMPV1_REPORT | IGMPV2_QUERY | IGMPV2_REPORT | IGMPV3_QUERY | IGMPV3_REPORT | OSPFV2_HELLO

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('frame-type')

	def read(self, Name=None):
		"""Get `frames` resource(s). Returns all `frames` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, FrameType=None):
		"""Create an instance of the `frames` resource

		Args:
			Name (string): TBD
			FrameType (enumeration): TBD
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `frames` resource

		"""
		return self._delete()

	def update(self, FrameType=None):
		"""Update the current instance of the `frames` resource

		Args:
			FrameType (enumeration): TBD
		"""
		return self._update(locals())

