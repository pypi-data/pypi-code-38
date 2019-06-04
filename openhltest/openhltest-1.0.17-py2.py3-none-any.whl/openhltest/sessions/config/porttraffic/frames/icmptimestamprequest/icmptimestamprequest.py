from openhltest_client.base import Base


class IcmpTimestampRequest(Base):
	"""TBD
	"""
	YANG_NAME = 'icmp-timestamp-request'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IcmpTimestampRequest, self).__init__(parent)

	@property
	def Code(self):
		"""ICMP Timestamp request code.

		Get an instance of the Code class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.code.code.Code)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.code.code import Code
		return Code(self)._read()

	@property
	def Identifier(self):
		"""Identifier.

		Get an instance of the Identifier class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.identifier.identifier.Identifier)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.identifier.identifier import Identifier
		return Identifier(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def Sequence_number(self):
		"""Sequence Number.

		Get an instance of the Sequence_number class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.sequence_number.sequence_number.Sequence_number)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.sequence_number.sequence_number import Sequence_number
		return Sequence_number(self)._read()

	@property
	def OriginateTimestamp(self):
		"""Originate timestamp.

		Get an instance of the OriginateTimestamp class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.originatetimestamp.originatetimestamp.OriginateTimestamp)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.originatetimestamp.originatetimestamp import OriginateTimestamp
		return OriginateTimestamp(self)._read()

	@property
	def ReceiveTimestamp(self):
		"""Receive timestamp.

		Get an instance of the ReceiveTimestamp class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.receivetimestamp.receivetimestamp.ReceiveTimestamp)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.receivetimestamp.receivetimestamp import ReceiveTimestamp
		return ReceiveTimestamp(self)._read()

	@property
	def TransmitTimestamp(self):
		"""Transmit timestamp.

		Get an instance of the TransmitTimestamp class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.transmittimestamp.transmittimestamp.TransmitTimestamp)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.icmptimestamprequest.transmittimestamp.transmittimestamp import TransmitTimestamp
		return TransmitTimestamp(self)._read()

