from openhltest_client.base import Base


class SegmentRouting(Base):
	"""TBD
	"""
	YANG_NAME = 'segment-routing'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(SegmentRouting, self).__init__(parent)

	@property
	def SegmentId(self):
		"""Value of the Segment identifier(SID).

		Get an instance of the SegmentId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2summaryrange.segmentrouting.segmentid.segmentid.SegmentId)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2summaryrange.segmentrouting.segmentid.segmentid import SegmentId
		return SegmentId(self)._read()

	@property
	def PrefixSegmentId(self):
		"""Value of the Prefix Segment identifier(SID).
		NBIT    Node SID Flag
		NPBIT   No-PHP Flag
		MBIT    Mapping Server Flag
		EBIT    Explicit-Null Flag
		VBIT    Value/Index Flag
		LBIT    Local/Global Flag

		Get an instance of the PrefixSegmentId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2summaryrange.segmentrouting.prefixsegmentid.prefixsegmentid.PrefixSegmentId)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv2summaryrange.segmentrouting.prefixsegmentid.prefixsegmentid import PrefixSegmentId
		return PrefixSegmentId(self)._read()

