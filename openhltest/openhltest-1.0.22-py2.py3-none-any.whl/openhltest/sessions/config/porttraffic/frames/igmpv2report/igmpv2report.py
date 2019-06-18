from openhltest_client.base import Base


class Igmpv2Report(Base):
	"""IGMPv2 Report message
	"""
	YANG_NAME = 'igmpv2-report'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Igmpv2Report, self).__init__(parent)

	@property
	def GroupAddress(self):
		"""Group IPv4 Address

		Get an instance of the GroupAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv2report.groupaddress.groupaddress.GroupAddress)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv2report.groupaddress.groupaddress import GroupAddress
		return GroupAddress(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv2report.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv2report.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def MaxResponseTime(self):
		"""Maximum response Time.

		Get an instance of the MaxResponseTime class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv2report.maxresponsetime.maxresponsetime.MaxResponseTime)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv2report.maxresponsetime.maxresponsetime import MaxResponseTime
		return MaxResponseTime(self)._read()

