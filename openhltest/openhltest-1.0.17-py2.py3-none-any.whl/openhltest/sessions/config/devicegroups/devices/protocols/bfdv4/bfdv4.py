from openhltest_client.base import Base


class Bfdv4(Base):
	"""TBD
	"""
	YANG_NAME = 'bfdv4'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Bfdv4, self).__init__(parent)

	@property
	def TransmitInterval(self):
		"""Minimum interval, in milliseconds, that the emulated router desires between
		transmitted BFD Control packets.

		Get an instance of the TransmitInterval class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bfdv4.transmitinterval.transmitinterval.TransmitInterval)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bfdv4.transmitinterval.transmitinterval import TransmitInterval
		return TransmitInterval(self)._read()

	@property
	def ReceiveInterval(self):
		"""Minimum interval, in milliseconds, that the emulated router desires between
		received BFD Control packets.

		Get an instance of the ReceiveInterval class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bfdv4.receiveinterval.receiveinterval.ReceiveInterval)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bfdv4.receiveinterval.receiveinterval import ReceiveInterval
		return ReceiveInterval(self)._read()

	@property
	def EchoReceiveInterval(self):
		"""Minimum interval, in milliseconds, that the emulated router desires between
		received BFD Echo packets.

		Get an instance of the EchoReceiveInterval class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bfdv4.echoreceiveinterval.echoreceiveinterval.EchoReceiveInterval)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bfdv4.echoreceiveinterval.echoreceiveinterval import EchoReceiveInterval
		return EchoReceiveInterval(self)._read()

	@property
	def Authentication(self):
		"""Type of authentication to be used
		NONE   : no authentication
		SIMPLE : The packet is authenticated by the receiving router if the password
		matches the authentication key that is included in the packet.
		This method provides little security because the authentication
		key can be learned by capturing packets.
		MD5    : The packet contains a cryptographic checksum, but not the authentication
		key itself. The receiving router performs a calculation based on the
		MD5 algorithm and an authentication key ID. The packet is authenticated
		if the calculated checksum matches. This method provides a stronger
		assurance that routing data originated from a router with a valid
		authentication key.

		Get an instance of the Authentication class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bfdv4.authentication.authentication.Authentication)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bfdv4.authentication.authentication import Authentication
		return Authentication(self)._read()

