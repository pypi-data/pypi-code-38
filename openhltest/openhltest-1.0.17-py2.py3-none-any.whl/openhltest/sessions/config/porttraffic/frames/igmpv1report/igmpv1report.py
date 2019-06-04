from openhltest_client.base import Base


class Igmpv1Report(Base):
	"""IGMPv1 Report message
	"""
	YANG_NAME = 'igmpv1-report'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Igmpv1Report, self).__init__(parent)

	@property
	def GroupAddress(self):
		"""Group IPv4 Address

		Get an instance of the GroupAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1report.groupaddress.groupaddress.GroupAddress)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1report.groupaddress.groupaddress import GroupAddress
		return GroupAddress(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1report.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1report.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def Unused(self):
		"""Unused.

		Get an instance of the Unused class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1report.unused.unused.Unused)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1report.unused.unused import Unused
		return Unused(self)._read()

