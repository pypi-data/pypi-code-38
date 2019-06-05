from openhltest_client.base import Base


class Vlan(Base):
	"""TBD
	"""
	YANG_NAME = 'vlan'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Vlan, self).__init__(parent)

	@property
	def Priority(self):
		"""TBD

		Get an instance of the Priority class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.vlan.priority.priority.Priority)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.vlan.priority.priority import Priority
		return Priority(self)._read()

	@property
	def Id(self):
		"""A single-tagged VLAN id

		Get an instance of the Id class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.vlan.id.id.Id)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.vlan.id.id import Id
		return Id(self)._read()

