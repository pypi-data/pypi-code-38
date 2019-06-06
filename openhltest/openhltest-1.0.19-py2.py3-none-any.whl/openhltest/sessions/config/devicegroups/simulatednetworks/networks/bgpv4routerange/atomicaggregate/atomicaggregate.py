from openhltest_client.base import Base


class AtomicAggregate(Base):
	"""TBD
	"""
	YANG_NAME = 'atomic-aggregate'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(AtomicAggregate, self).__init__(parent)

	@property
	def AggregateAs(self):
		"""The AS number to use for the AGGREGATOR attribute

		Get an instance of the AggregateAs class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.atomicaggregate.aggregateas.aggregateas.AggregateAs)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.atomicaggregate.aggregateas.aggregateas import AggregateAs
		return AggregateAs(self)._read()

	@property
	def AggregateIp(self):
		"""The IP address to use for the AGGREGATOR attribute.

		Get an instance of the AggregateIp class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.atomicaggregate.aggregateip.aggregateip.AggregateIp)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.bgpv4routerange.atomicaggregate.aggregateip.aggregateip import AggregateIp
		return AggregateIp(self)._read()

