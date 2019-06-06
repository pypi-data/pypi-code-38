from openhltest_client.base import Base


class DataCenterBridgingExchange(Base):
	"""Data Center Bridging Exchange protocol is a discovery and capability exchange protocol that is used for conveying capabilities and configuration between neighbors to ensure consistent configuration across the network. This protocol leverages functionality provided by LLDP
	"""
	YANG_NAME = 'data-center-bridging-exchange'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(DataCenterBridgingExchange, self).__init__(parent)

