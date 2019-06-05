from openhltest_client.base import Base


class IcmpRouterAdvertisement(Base):
	"""TBD
	"""
	YANG_NAME = 'icmp-router-advertisement'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IcmpRouterAdvertisement, self).__init__(parent)

	@property
	def Code(self):
		"""ICMP Router Advertisement code.

		Get an instance of the Code class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.code.code.Code)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.code.code import Code
		return Code(self)._read()

	@property
	def AdvertiseCount(self):
		"""Advertise Count.

		Get an instance of the AdvertiseCount class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.advertisecount.advertisecount.AdvertiseCount)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.advertisecount.advertisecount import AdvertiseCount
		return AdvertiseCount(self)._read()

	@property
	def LifeTime(self):
		"""Life Time.

		Get an instance of the LifeTime class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.lifetime.lifetime.LifeTime)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.lifetime.lifetime import LifeTime
		return LifeTime(self)._read()

	@property
	def AddressEntrySize(self):
		"""Address Entry Size.

		Get an instance of the AddressEntrySize class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.addressentrysize.addressentrysize.AddressEntrySize)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.addressentrysize.addressentrysize import AddressEntrySize
		return AddressEntrySize(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def IcmpRouterAddress(self):
		"""TBD

		Get an instance of the IcmpRouterAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.icmprouteraddress.icmprouteraddress.IcmpRouterAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.icmprouteraddress.icmprouteraddress import IcmpRouterAddress
		return IcmpRouterAddress(self)

