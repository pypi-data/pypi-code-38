from openhltest_client.base import Base


class Statistics(Base):
	"""The statistics pull model
	"""
	YANG_NAME = 'statistics'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"LastActivityTimestamp": "last-activity-timestamp", "FirstActivityTimestamp": "first-activity-timestamp"}
	YANG_ACTIONS = ["clear"]

	def __init__(self, parent):
		super(Statistics, self).__init__(parent)

	@property
	def PhysicalPort(self):
		"""TBD

		Get an instance of the PhysicalPort class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.physicalport.physicalport.PhysicalPort)
		"""
		from openhltest_client.openhltest.sessions.statistics.physicalport.physicalport import PhysicalPort
		return PhysicalPort(self)

	@property
	def Port(self):
		"""TBD

		Get an instance of the Port class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.port.port.Port)
		"""
		from openhltest_client.openhltest.sessions.statistics.port.port import Port
		return Port(self)

	@property
	def PortTraffic(self):
		"""TBD

		Get an instance of the PortTraffic class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.porttraffic.porttraffic.PortTraffic)
		"""
		from openhltest_client.openhltest.sessions.statistics.porttraffic.porttraffic import PortTraffic
		return PortTraffic(self)

	@property
	def DeviceTraffic(self):
		"""TBD

		Get an instance of the DeviceTraffic class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.devicetraffic.devicetraffic.DeviceTraffic)
		"""
		from openhltest_client.openhltest.sessions.statistics.devicetraffic.devicetraffic import DeviceTraffic
		return DeviceTraffic(self)

	@property
	def Bgpv4Statistics(self):
		"""TBD

		Get an instance of the Bgpv4Statistics class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.bgpv4statistics.bgpv4statistics.Bgpv4Statistics)
		"""
		from openhltest_client.openhltest.sessions.statistics.bgpv4statistics.bgpv4statistics import Bgpv4Statistics
		return Bgpv4Statistics(self)

	@property
	def Bgpv6Statistics(self):
		"""TBD

		Get an instance of the Bgpv6Statistics class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.bgpv6statistics.bgpv6statistics.Bgpv6Statistics)
		"""
		from openhltest_client.openhltest.sessions.statistics.bgpv6statistics.bgpv6statistics import Bgpv6Statistics
		return Bgpv6Statistics(self)

	@property
	def Ospfv2Statistics(self):
		"""TBD

		Get an instance of the Ospfv2Statistics class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.ospfv2statistics.ospfv2statistics.Ospfv2Statistics)
		"""
		from openhltest_client.openhltest.sessions.statistics.ospfv2statistics.ospfv2statistics import Ospfv2Statistics
		return Ospfv2Statistics(self)

	@property
	def Ospfv3Statistics(self):
		"""TBD

		Get an instance of the Ospfv3Statistics class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.ospfv3statistics.ospfv3statistics.Ospfv3Statistics)
		"""
		from openhltest_client.openhltest.sessions.statistics.ospfv3statistics.ospfv3statistics import Ospfv3Statistics
		return Ospfv3Statistics(self)

	@property
	def IsisStatistics(self):
		"""TBD

		Get an instance of the IsisStatistics class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.isisstatistics.isisstatistics.IsisStatistics)
		"""
		from openhltest_client.openhltest.sessions.statistics.isisstatistics.isisstatistics import IsisStatistics
		return IsisStatistics(self)

	@property
	def Bfdv4Statistics(self):
		"""TBD

		Get an instance of the Bfdv4Statistics class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.bfdv4statistics.bfdv4statistics.Bfdv4Statistics)
		"""
		from openhltest_client.openhltest.sessions.statistics.bfdv4statistics.bfdv4statistics import Bfdv4Statistics
		return Bfdv4Statistics(self)

	@property
	def Bfdv6Statistics(self):
		"""TBD

		Get an instance of the Bfdv6Statistics class.

		Returns:
			obj(openhltest_client.openhltest.sessions.statistics.bfdv6statistics.bfdv6statistics.Bfdv6Statistics)
		"""
		from openhltest_client.openhltest.sessions.statistics.bfdv6statistics.bfdv6statistics import Bfdv6Statistics
		return Bfdv6Statistics(self)

	@property
	def FirstActivityTimestamp(self):
		"""Timestamp of the first request to this session.

		Getter Returns:
			string
		"""
		return self._get_value('first-activity-timestamp')

	@property
	def LastActivityTimestamp(self):
		"""Timestamp of the last request to this session

		Getter Returns:
			string
		"""
		return self._get_value('last-activity-timestamp')

	def Clear(self):
		"""Clear all statistic counters.

		"""
		return self._execute('clear')

