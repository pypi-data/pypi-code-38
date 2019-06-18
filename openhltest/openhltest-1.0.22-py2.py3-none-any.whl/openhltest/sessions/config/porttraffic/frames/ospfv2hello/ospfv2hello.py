from openhltest_client.base import Base


class Ospfv2Hello(Base):
	"""TBD
	"""
	YANG_NAME = 'ospfv2-hello'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ospfv2Hello, self).__init__(parent)

	@property
	def DesignatedRouterAddress(self):
		"""Designated Router Address

		Get an instance of the DesignatedRouterAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.designatedrouteraddress.designatedrouteraddress.DesignatedRouterAddress)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.designatedrouteraddress.designatedrouteraddress import DesignatedRouterAddress
		return DesignatedRouterAddress(self)._read()

	@property
	def BackupDesignatedRouterAddress(self):
		"""Backup Designated Router Address

		Get an instance of the BackupDesignatedRouterAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.backupdesignatedrouteraddress.backupdesignatedrouteraddress.BackupDesignatedRouterAddress)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.backupdesignatedrouteraddress.backupdesignatedrouteraddress import BackupDesignatedRouterAddress
		return BackupDesignatedRouterAddress(self)._read()

	@property
	def HelloInterval(self):
		"""Hello Interval.

		Get an instance of the HelloInterval class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.hellointerval.hellointerval.HelloInterval)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.hellointerval.hellointerval import HelloInterval
		return HelloInterval(self)._read()

	@property
	def RouterDeadInterval(self):
		"""Router Dead Interval.

		Get an instance of the RouterDeadInterval class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.routerdeadinterval.routerdeadinterval.RouterDeadInterval)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.routerdeadinterval.routerdeadinterval import RouterDeadInterval
		return RouterDeadInterval(self)._read()

	@property
	def RouterPriority(self):
		"""Router Priority.

		Get an instance of the RouterPriority class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.routerpriority.routerpriority.RouterPriority)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.routerpriority.routerpriority import RouterPriority
		return RouterPriority(self)._read()

	@property
	def NetworkMask(self):
		"""Network mask

		Get an instance of the NetworkMask class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.networkmask.networkmask.NetworkMask)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.networkmask.networkmask import NetworkMask
		return NetworkMask(self)._read()

	@property
	def AreaId(self):
		"""Area Id

		Get an instance of the AreaId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.areaid.areaid.AreaId)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.areaid.areaid import AreaId
		return AreaId(self)._read()

	@property
	def RouterId(self):
		"""Router Id

		Get an instance of the RouterId class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.routerid.routerid.RouterId)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.routerid.routerid import RouterId
		return RouterId(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.checksum.checksum.Checksum)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def PacketLength(self):
		"""Packet Length.

		Get an instance of the PacketLength class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.packetlength.packetlength.PacketLength)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.packetlength.packetlength import PacketLength
		return PacketLength(self)._read()

	@property
	def AuthType(self):
		"""Authentication Type.
		   NO_AUTH : No Authentication.
		   SIMPLE_PASSWORD : Simple Password.
		   MD5 : MD5 Authentication.
		   USER_DEFINED : User Defined.

		Get an instance of the AuthType class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.authtype.authtype.AuthType)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.authtype.authtype import AuthType
		return AuthType(self)._read()

	@property
	def AuthValue1(self):
		"""Authentication Value 1.

		Get an instance of the AuthValue1 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.authvalue1.authvalue1.AuthValue1)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.authvalue1.authvalue1 import AuthValue1
		return AuthValue1(self)._read()

	@property
	def AuthValue2(self):
		"""Authentication Value 2.

		Get an instance of the AuthValue2 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.authvalue2.authvalue2.AuthValue2)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.authvalue2.authvalue2 import AuthValue2
		return AuthValue2(self)._read()

	@property
	def OptionsReservedBit7(self):
		"""Reserved Bit 7

		Get an instance of the OptionsReservedBit7 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsreservedbit7.optionsreservedbit7.OptionsReservedBit7)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsreservedbit7.optionsreservedbit7 import OptionsReservedBit7
		return OptionsReservedBit7(self)._read()

	@property
	def OptionsReservedBit6(self):
		"""Reserved Bit 6

		Get an instance of the OptionsReservedBit6 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsreservedbit6.optionsreservedbit6.OptionsReservedBit6)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsreservedbit6.optionsreservedbit6 import OptionsReservedBit6
		return OptionsReservedBit6(self)._read()

	@property
	def OptionsDcBit(self):
		"""Demand Circuits Bit

		Get an instance of the OptionsDcBit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsdcbit.optionsdcbit.OptionsDcBit)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsdcbit.optionsdcbit import OptionsDcBit
		return OptionsDcBit(self)._read()

	@property
	def OptionsEaBit(self):
		"""EA Bit

		Get an instance of the OptionsEaBit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionseabit.optionseabit.OptionsEaBit)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionseabit.optionseabit import OptionsEaBit
		return OptionsEaBit(self)._read()

	@property
	def OptionsNpBit(self):
		"""NSSA Support

		Get an instance of the OptionsNpBit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsnpbit.optionsnpbit.OptionsNpBit)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsnpbit.optionsnpbit import OptionsNpBit
		return OptionsNpBit(self)._read()

	@property
	def OptionsMcBit(self):
		"""Multicast Capable

		Get an instance of the OptionsMcBit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsmcbit.optionsmcbit.OptionsMcBit)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsmcbit.optionsmcbit import OptionsMcBit
		return OptionsMcBit(self)._read()

	@property
	def OptionsEBit(self):
		"""E Bit, External Routing Capability.

		Get an instance of the OptionsEBit class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsebit.optionsebit.OptionsEBit)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsebit.optionsebit import OptionsEBit
		return OptionsEBit(self)._read()

	@property
	def OptionsReservedBit0(self):
		"""Reserved Bit 0

		Get an instance of the OptionsReservedBit0 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsreservedbit0.optionsreservedbit0.OptionsReservedBit0)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.optionsreservedbit0.optionsreservedbit0 import OptionsReservedBit0
		return OptionsReservedBit0(self)._read()

	@property
	def Neighbors(self):
		"""TBD

		Get an instance of the Neighbors class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.neighbors.neighbors.Neighbors)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.frames.ospfv2hello.neighbors.neighbors import Neighbors
		return Neighbors(self)

