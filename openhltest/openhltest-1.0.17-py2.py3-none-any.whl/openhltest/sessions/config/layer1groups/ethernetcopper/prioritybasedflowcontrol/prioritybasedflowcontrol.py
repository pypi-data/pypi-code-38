from openhltest_client.base import Base


class PriorityBasedFlowControl(Base):
	"""Priority-based Flow Control provides a link level flow control mechanism that can be controlled independently for each frame priority. The goal of this mechanism is to ensure zero loss under congestion in DCB networks
	"""
	YANG_NAME = 'priority-based-flow-control'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(PriorityBasedFlowControl, self).__init__(parent)

