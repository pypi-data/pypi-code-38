from openhltest_client.base import Base


class Igmpv3Report(Base):
	"""IGMPv3 Report message
	"""
	YANG_NAME = 'igmpv3-report'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Igmpv3Report, self).__init__(parent)

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv3report.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv3report.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def NumberOfGroupRecords(self):
		"""Number of group records.

		Get an instance of the NumberOfGroupRecords class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv3report.numberofgrouprecords.numberofgrouprecords.NumberOfGroupRecords)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv3report.numberofgrouprecords.numberofgrouprecords import NumberOfGroupRecords
		return NumberOfGroupRecords(self)._read()

	@property
	def Reserved(self):
		"""Reserved

		Get an instance of the Reserved class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv3report.reserved.reserved.Reserved)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv3report.reserved.reserved import Reserved
		return Reserved(self)._read()

	@property
	def Reserved2(self):
		"""Reserved2

		Get an instance of the Reserved2 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv3report.reserved2.reserved2.Reserved2)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv3report.reserved2.reserved2 import Reserved2
		return Reserved2(self)._read()

