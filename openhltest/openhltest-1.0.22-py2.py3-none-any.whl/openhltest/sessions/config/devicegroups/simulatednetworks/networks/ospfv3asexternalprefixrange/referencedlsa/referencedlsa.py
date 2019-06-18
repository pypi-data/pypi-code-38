from openhltest_client.base import Base


class ReferencedLsa(Base):
	"""TBD
	"""
	YANG_NAME = 'referenced-lsa'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(ReferencedLsa, self).__init__(parent)

	@property
	def Type(self):
		"""Type of the referenced LSA.

		Get an instance of the Type class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.referencedlsa.type.type.Type)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.referencedlsa.type.type import Type
		return Type(self)._read()

	@property
	def LinkStateId(self):
		"""Referenced Link State ID.

		Get an instance of the LinkStateId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.referencedlsa.linkstateid.linkstateid.LinkStateId)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.ospfv3asexternalprefixrange.referencedlsa.linkstateid.linkstateid import LinkStateId
		return LinkStateId(self)._read()

