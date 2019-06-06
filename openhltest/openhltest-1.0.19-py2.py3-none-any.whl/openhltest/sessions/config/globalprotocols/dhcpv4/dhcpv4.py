from openhltest_client.base import Base


class Dhcpv4(Base):
	"""This list allows for configuring global DHCPv4 options.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/global-protocols/dhcpv4 resource.
	"""
	YANG_NAME = 'dhcpv4'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name", "Ports": "ports"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Dhcpv4, self).__init__(parent)

	@property
	def RequestRate(self):
		"""Requests per second for DHCP client leases or lease renewals.

		Get an instance of the RequestRate class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.requestrate.requestrate.RequestRate)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.requestrate.requestrate import RequestRate
		return RequestRate(self)._read()

	@property
	def LeaseTime(self):
		"""Suggested lease time in seconds at the DHCP port level.

		Get an instance of the LeaseTime class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.leasetime.leasetime.LeaseTime)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.leasetime.leasetime import LeaseTime
		return LeaseTime(self)._read()

	@property
	def MaxMsgSize(self):
		"""Used to negotiate the maximum DHCP message size, in bytes.
		This is option 57 for the options field of the DHCP message, as described in RFC 2132.

		Get an instance of the MaxMsgSize class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.maxmsgsize.maxmsgsize.MaxMsgSize)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.maxmsgsize.maxmsgsize import MaxMsgSize
		return MaxMsgSize(self)._read()

	@property
	def MsgTimeout(self):
		"""Message timeout in seconds.

		Get an instance of the MsgTimeout class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.msgtimeout.msgtimeout.MsgTimeout)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.msgtimeout.msgtimeout import MsgTimeout
		return MsgTimeout(self)._read()

	@property
	def OutstandingSessionCount(self):
		"""Number of DHCP sessions to resolve at a time.

		Get an instance of the OutstandingSessionCount class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.outstandingsessioncount.outstandingsessioncount.OutstandingSessionCount)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.outstandingsessioncount.outstandingsessioncount import OutstandingSessionCount
		return OutstandingSessionCount(self)._read()

	@property
	def ReleaseRate(self):
		"""Number of DHCP sessions that are released per second.

		Get an instance of the ReleaseRate class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.releaserate.releaserate.ReleaseRate)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.releaserate.releaserate import ReleaseRate
		return ReleaseRate(self)._read()

	@property
	def RetryCount(self):
		"""Number of retries allowed.

		Get an instance of the RetryCount class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.retrycount.retrycount.RetryCount)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.retrycount.retrycount import RetryCount
		return RetryCount(self)._read()

	@property
	def SequenceType(self):
		"""Port-level sequence type that determines in what order sessions are attempted.
		SEQUENTIAL	: Sessions are attempted sequentially across host blocks under the port.
		PARALLEL	  : Sessions are attempted in parallel across host blocks under the port

		Get an instance of the SequenceType class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.sequencetype.sequencetype.SequenceType)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.sequencetype.sequencetype import SequenceType
		return SequenceType(self)._read()

	@property
	def StartTransactionId(self):
		"""Starting transaction ID for sessions on this port.

		Get an instance of the StartTransactionId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.starttransactionid.starttransactionid.StartTransactionId)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.starttransactionid.starttransactionid import StartTransactionId
		return StartTransactionId(self)._read()

	@property
	def MaxDnaV4RetryCount(self):
		"""Max DNAv4 retry count.

		Get an instance of the MaxDnaV4RetryCount class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.maxdnav4retrycount.maxdnav4retrycount.MaxDnaV4RetryCount)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.maxdnav4retrycount.maxdnav4retrycount import MaxDnaV4RetryCount
		return MaxDnaV4RetryCount(self)._read()

	@property
	def DnaV4Timeout(self):
		"""DNAv4 timeout.

		Get an instance of the DnaV4Timeout class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.dnav4timeout.dnav4timeout.DnaV4Timeout)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.dnav4timeout.dnav4timeout import DnaV4Timeout
		return DnaV4Timeout(self)._read()

	@property
	def EnableCustomOptionAssignForRelayAgents(self):
		"""Enable custom option assignments on relay agent mode.

		Get an instance of the EnableCustomOptionAssignForRelayAgents class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.enablecustomoptionassignforrelayagents.enablecustomoptionassignforrelayagents.EnableCustomOptionAssignForRelayAgents)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.dhcpv4.enablecustomoptionassignforrelayagents.enablecustomoptionassignforrelayagents import EnableCustomOptionAssignForRelayAgents
		return EnableCustomOptionAssignForRelayAgents(self)._read()

	@property
	def Name(self):
		"""The unique name for a global protocols list item

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
	def Ports(self):
		"""A list of abstract port references

		Getter Returns:
			list(OpenHLTest.Sessions.Config.Ports.Name)

		Setter Allows:
			obj(OpenHLTest.Sessions.Config.Ports) | list(OpenHLTest.Sessions.Config.Ports.Name)

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('ports')

	def read(self, Name=None):
		"""Get `dhcpv4` resource(s). Returns all `dhcpv4` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, Ports=None):
		"""Create an instance of the `dhcpv4` resource

		Args:
			Name (string): The unique name for a global protocols list item
			Ports (leafref): A list of abstract port references
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `dhcpv4` resource

		"""
		return self._delete()

	def update(self, Ports=None):
		"""Update the current instance of the `dhcpv4` resource

		Args:
			Ports (leafref): A list of abstract port references
		"""
		return self._update(locals())

