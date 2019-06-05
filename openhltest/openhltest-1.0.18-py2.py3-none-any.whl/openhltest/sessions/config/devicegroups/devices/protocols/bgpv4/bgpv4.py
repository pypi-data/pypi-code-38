from openhltest_client.base import Base


class Bgpv4(Base):
	"""TBD
	"""
	YANG_NAME = 'bgpv4'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Bgpv4, self).__init__(parent)

	@property
	def AsNumber2Byte(self):
		"""2-Byte Autonomous system number for the emulated BGP router

		Get an instance of the AsNumber2Byte class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.asnumber2byte.asnumber2byte.AsNumber2Byte)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.asnumber2byte.asnumber2byte import AsNumber2Byte
		return AsNumber2Byte(self)._read()

	@property
	def DutAsNumber2Byte(self):
		"""2-Byte Autonomous system number configured for the DUT.

		Get an instance of the DutAsNumber2Byte class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.dutasnumber2byte.dutasnumber2byte.DutAsNumber2Byte)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.dutasnumber2byte.dutasnumber2byte import DutAsNumber2Byte
		return DutAsNumber2Byte(self)._read()

	@property
	def AsNumber4Byte(self):
		"""Enables the use of 4 Byte Autonomous system number

		Get an instance of the AsNumber4Byte class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.asnumber4byte.asnumber4byte.AsNumber4Byte)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.asnumber4byte.asnumber4byte import AsNumber4Byte
		return AsNumber4Byte(self)._read()

	@property
	def AsNumberSetMode(self):
		"""Option to exclude, include or prepend the local AS number.

		Get an instance of the AsNumberSetMode class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.asnumbersetmode.asnumbersetmode.AsNumberSetMode)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.asnumbersetmode.asnumbersetmode import AsNumberSetMode
		return AsNumberSetMode(self)._read()

	@property
	def BgpType(self):
		"""The type of BGP topology you create. Options include the following:
		   External BGP (EBGP)-used for BGP links between two or more Autonomous Systems (ASs)
		   Internal BGP (IBGP)-used within a single Autonomous System (AS)

		Get an instance of the BgpType class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.bgptype.bgptype.BgpType)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.bgptype.bgptype import BgpType
		return BgpType(self)._read()

	@property
	def HoldTimeInterval(self):
		"""BGP Hold Time in seconds to use when negotiating with peers. If the router
		does not receive KEEPALIVE or UPDATE or NOTIFICATION messages within the
		Hold Time field of the OPEN message, the BGP connection to the peer will be closed.

		Get an instance of the HoldTimeInterval class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.holdtimeinterval.holdtimeinterval.HoldTimeInterval)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.holdtimeinterval.holdtimeinterval import HoldTimeInterval
		return HoldTimeInterval(self)._read()

	@property
	def KeepAliveInterval(self):
		"""Number of seconds between transmissions of Keep Alive messages by the emulated router
		(in the absence of the sending of any other BGP packets) to the DUT. The standard
		keep-alive transmit time is every 30 seconds, or one-third of the Hold Time.

		Get an instance of the KeepAliveInterval class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.keepaliveinterval.keepaliveinterval.KeepAliveInterval)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.keepaliveinterval.keepaliveinterval import KeepAliveInterval
		return KeepAliveInterval(self)._read()

	@property
	def GracefulRestart(self):
		"""TBD

		Get an instance of the GracefulRestart class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.gracefulrestart.GracefulRestart)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.gracefulrestart import GracefulRestart
		return GracefulRestart(self)._read()

	@property
	def Authentication(self):
		"""TBD

		Get an instance of the Authentication class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.authentication.authentication.Authentication)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.authentication.authentication import Authentication
		return Authentication(self)._read()

	@property
	def Ttl(self):
		"""The limited number of iterations that a unit of data can experience before
		the data is discarded.

		Get an instance of the Ttl class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.ttl.ttl.Ttl)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.ttl.ttl import Ttl
		return Ttl(self)._read()

	@property
	def DutIpv4Address(self):
		"""IPv4 address of the BGP peer for the session.

		Get an instance of the DutIpv4Address class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.dutipv4address.dutipv4address.DutIpv4Address)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.dutipv4address.dutipv4address import DutIpv4Address
		return DutIpv4Address(self)._read()

