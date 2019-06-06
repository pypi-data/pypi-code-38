from openhltest_client.base import Base


class GracefulRestart(Base):
	"""TBD
	"""
	YANG_NAME = 'graceful-restart'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(GracefulRestart, self).__init__(parent)

	@property
	def LongLivedGracefulRestart(self):
		"""BGP long lived graceful restart allows a network operator to choose to maintain stale routing information
		from a failed BGP peer much longer than the existing BGP graceful restart facility.
		   TRUE  : Enable long lived graceful restart
		   FALSE : Disable long lived graceful restart

		Get an instance of the LongLivedGracefulRestart class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv6.gracefulrestart.longlivedgracefulrestart.longlivedgracefulrestart.LongLivedGracefulRestart)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv6.gracefulrestart.longlivedgracefulrestart.longlivedgracefulrestart import LongLivedGracefulRestart
		return LongLivedGracefulRestart(self)._read()

	@property
	def RestartTime(self):
		"""BGP graceful restart time. The amount of time (in seconds) that the emulated
		router will wait for its peer to re-establish the session. If the session is
		not re-established within this time frame, the stale routes will be removed
		from the route database.

		Get an instance of the RestartTime class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv6.gracefulrestart.restarttime.restarttime.RestartTime)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv6.gracefulrestart.restarttime.restarttime import RestartTime
		return RestartTime(self)._read()

	@property
	def RestartDelay(self):
		"""The amount of time to wait before initiating a new BGP session. Traffic generator
		will not initiate a new session until this timer expires. If the DUT initiates a
		new session, Spirent TestCenter will process it and establish the session.

		Get an instance of the RestartDelay class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv6.gracefulrestart.restartdelay.restartdelay.RestartDelay)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv6.gracefulrestart.restartdelay.restartdelay import RestartDelay
		return RestartDelay(self)._read()

	@property
	def AdvertiseEor(self):
		"""Advertise End-of-RIB
		   TRUE  : Send end-of-RIB marker in the update packet
		   FALSE : Do not send end-of-RIB marker in the update packet

		Get an instance of the AdvertiseEor class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv6.gracefulrestart.advertiseeor.advertiseeor.AdvertiseEor)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv6.gracefulrestart.advertiseeor.advertiseeor import AdvertiseEor
		return AdvertiseEor(self)._read()

