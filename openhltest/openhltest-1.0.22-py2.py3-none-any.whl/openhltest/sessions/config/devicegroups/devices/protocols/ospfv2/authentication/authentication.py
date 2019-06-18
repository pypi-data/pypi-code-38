from openhltest_client.base import Base


class Authentication(Base):
	"""TBD
	"""
	YANG_NAME = 'authentication'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Authentication, self).__init__(parent)

	@property
	def AuthenticationType(self):
		"""Type of authentication to be used

		Get an instance of the AuthenticationType class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ospfv2.authentication.authenticationtype.authenticationtype.AuthenticationType)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ospfv2.authentication.authenticationtype.authenticationtype import AuthenticationType
		return AuthenticationType(self)._read()

	@property
	def Password(self):
		"""Authentication password.

		Get an instance of the Password class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ospfv2.authentication.password.password.Password)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ospfv2.authentication.password.password import Password
		return Password(self)._read()

