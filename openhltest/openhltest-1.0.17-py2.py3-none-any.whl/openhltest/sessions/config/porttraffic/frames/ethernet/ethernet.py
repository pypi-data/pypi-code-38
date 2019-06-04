from openhltest_client.base import Base


class Ethernet(Base):
	"""TBD
	"""
	YANG_NAME = 'ethernet'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ethernet, self).__init__(parent)

	@property
	def Destination(self):
		"""Destination mac address

		Get an instance of the Destination class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ethernet.destination.destination.Destination)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ethernet.destination.destination import Destination
		return Destination(self)._read()

	@property
	def Source(self):
		"""Source mac address

		Get an instance of the Source class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ethernet.source.source.Source)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ethernet.source.source import Source
		return Source(self)._read()

	@property
	def EthernetType(self):
		"""Ethernet type.
		Common values are 88B5 86DD 0800

		Get an instance of the EthernetType class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ethernet.ethernettype.ethernettype.EthernetType)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ethernet.ethernettype.ethernettype import EthernetType
		return EthernetType(self)._read()

