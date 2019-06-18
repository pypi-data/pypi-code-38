from openhltest_client.base import Base


class Igmpv1Query(Base):
	"""IGMPv1 Query message
	"""
	YANG_NAME = 'igmpv1-query'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Igmpv1Query, self).__init__(parent)

	@property
	def GroupAddress(self):
		"""Group IPv4 Address

		Get an instance of the GroupAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1query.groupaddress.groupaddress.GroupAddress)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1query.groupaddress.groupaddress import GroupAddress
		return GroupAddress(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1query.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1query.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def Unused(self):
		"""Unused.

		Get an instance of the Unused class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1query.unused.unused.Unused)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.igmpv1query.unused.unused import Unused
		return Unused(self)._read()

