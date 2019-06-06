from openhltest_client.base import Base


class Tcp(Base):
	"""TBD
	"""
	YANG_NAME = 'tcp'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Tcp, self).__init__(parent)

	@property
	def SourcePort(self):
		"""Specifies the port on the sending TCP module.

		Get an instance of the SourcePort class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.sourceport.sourceport.SourcePort)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.sourceport.sourceport import SourcePort
		return SourcePort(self)._read()

	@property
	def DestinationPort(self):
		"""Specifies the port on the receiving TCP module.

		Get an instance of the DestinationPort class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.destinationport.destinationport.DestinationPort)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.destinationport.destinationport import DestinationPort
		return DestinationPort(self)._read()

	@property
	def AcknowledgementNumber(self):
		"""Identifies the next expected TCP octet.

		Get an instance of the AcknowledgementNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.acknowledgementnumber.acknowledgementnumber.AcknowledgementNumber)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.acknowledgementnumber.acknowledgementnumber import AcknowledgementNumber
		return AcknowledgementNumber(self)._read()

	@property
	def HeaderLength(self):
		"""Specifies the data offset field in the TCP header.

		Get an instance of the HeaderLength class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.headerlength.headerlength.HeaderLength)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.headerlength.headerlength import HeaderLength
		return HeaderLength(self)._read()

	@property
	def Reserved(self):
		"""Reserves TCP bits.

		Get an instance of the Reserved class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.reserved.reserved.Reserved)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.reserved.reserved import Reserved
		return Reserved(self)._read()

	@property
	def SequenceNumber(self):
		"""Identifies the position of the data within the data stream.

		Get an instance of the SequenceNumber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.sequencenumber.sequencenumber.SequenceNumber)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.sequencenumber.sequencenumber import SequenceNumber
		return SequenceNumber(self)._read()

	@property
	def UrgentPointer(self):
		"""Specifies the position in the segment where urgent data ends.

		Get an instance of the UrgentPointer class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.urgentpointer.urgentpointer.UrgentPointer)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.urgentpointer.urgentpointer import UrgentPointer
		return UrgentPointer(self)._read()

	@property
	def WindowSize(self):
		"""This field is used by the receiver to indicate to the sender the amount of data that it is able to accept.

		Get an instance of the WindowSize class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.windowsize.windowsize.WindowSize)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.windowsize.windowsize import WindowSize
		return WindowSize(self)._read()

	@property
	def AcknowledgementFlag(self):
		"""Indicates whether the data identified by the sequence number has been received.

		Get an instance of the AcknowledgementFlag class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.acknowledgementflag.acknowledgementflag.AcknowledgementFlag)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.acknowledgementflag.acknowledgementflag import AcknowledgementFlag
		return AcknowledgementFlag(self)._read()

	@property
	def FinFlag(self):
		"""Indicates whether a connection is terminated.

		Get an instance of the FinFlag class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.finflag.finflag.FinFlag)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.finflag.finflag import FinFlag
		return FinFlag(self)._read()

	@property
	def PushFlag(self):
		"""Indicates whether to ensure that the data is given the appropriate priority and is processed at the sending or receiving end.

		Get an instance of the PushFlag class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.pushflag.pushflag.PushFlag)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.pushflag.pushflag import PushFlag
		return PushFlag(self)._read()

	@property
	def ResetFlag(self):
		"""Resets the connection when a segment arrives that is not intended for the current connection.

		Get an instance of the ResetFlag class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.resetflag.resetflag.ResetFlag)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.resetflag.resetflag import ResetFlag
		return ResetFlag(self)._read()

	@property
	def SyncFlag(self):
		"""Indicates whether the port is open for connection.

		Get an instance of the SyncFlag class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.syncflag.syncflag.SyncFlag)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.syncflag.syncflag import SyncFlag
		return SyncFlag(self)._read()

	@property
	def UrgentFlag(self):
		"""Identifies the incoming data as urgent, giving it priority over the other segments.

		Get an instance of the UrgentFlag class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.urgentflag.urgentflag.UrgentFlag)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.urgentflag.urgentflag import UrgentFlag
		return UrgentFlag(self)._read()

	@property
	def Checksum(self):
		"""Specifies the TCP checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.tcp.checksum.checksum import Checksum
		return Checksum(self)._read()

