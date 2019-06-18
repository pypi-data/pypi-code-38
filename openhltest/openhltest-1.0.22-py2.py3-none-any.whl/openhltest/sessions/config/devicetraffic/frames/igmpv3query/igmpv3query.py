from openhltest_client.base import Base


class Igmpv3Query(Base):
	"""IGMPv3 Query message
	"""
	YANG_NAME = 'igmpv3-query'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Igmpv3Query, self).__init__(parent)

	@property
	def GroupAddress(self):
		"""Group IPv4 Address

		Get an instance of the GroupAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.groupaddress.groupaddress.GroupAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.groupaddress.groupaddress import GroupAddress
		return GroupAddress(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def MaxResponseTime(self):
		"""Maximum response Time.

		Get an instance of the MaxResponseTime class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.maxresponsetime.maxresponsetime.MaxResponseTime)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.maxresponsetime.maxresponsetime import MaxResponseTime
		return MaxResponseTime(self)._read()

	@property
	def NumberOfSources(self):
		"""Number of Sources.

		Get an instance of the NumberOfSources class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.numberofsources.numberofsources.NumberOfSources)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.numberofsources.numberofsources import NumberOfSources
		return NumberOfSources(self)._read()

	@property
	def SuppressFlag(self):
		"""Suppress Flag.

		Get an instance of the SuppressFlag class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.suppressflag.suppressflag.SuppressFlag)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.suppressflag.suppressflag import SuppressFlag
		return SuppressFlag(self)._read()

	@property
	def Reserved(self):
		"""Reserved.

		Get an instance of the Reserved class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.reserved.reserved.Reserved)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.reserved.reserved import Reserved
		return Reserved(self)._read()

	@property
	def Qqic(self):
		"""QQIC(Querier's Query Interval Code).

		Get an instance of the Qqic class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.qqic.qqic.Qqic)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.qqic.qqic import Qqic
		return Qqic(self)._read()

	@property
	def Qrv(self):
		"""QRV bits(Querier's Robustness Variable).

		Get an instance of the Qrv class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.qrv.qrv.Qrv)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.qrv.qrv import Qrv
		return Qrv(self)._read()

	@property
	def SourceAddressList(self):
		"""TBD

		Get an instance of the SourceAddressList class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.sourceaddresslist.sourceaddresslist.SourceAddressList)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.igmpv3query.sourceaddresslist.sourceaddresslist import SourceAddressList
		return SourceAddressList(self)

