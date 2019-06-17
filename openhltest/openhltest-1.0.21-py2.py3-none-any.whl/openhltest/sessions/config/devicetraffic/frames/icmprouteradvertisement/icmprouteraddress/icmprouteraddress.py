from openhltest_client.base import Base


class IcmpRouterAddress(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-traffic/frames/icmp-router-advertisement/icmp-router-address resource.
	"""
	YANG_NAME = 'icmp-router-address'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IcmpRouterAddress, self).__init__(parent)

	@property
	def RouterAddress(self):
		"""Router Address

		Get an instance of the RouterAddress class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.icmprouteraddress.routeraddress.routeraddress.RouterAddress)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.icmprouteraddress.routeraddress.routeraddress import RouterAddress
		return RouterAddress(self)._read()

	@property
	def PreferenceLevel(self):
		"""Preference Level

		Get an instance of the PreferenceLevel class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.icmprouteraddress.preferencelevel.preferencelevel.PreferenceLevel)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.frames.icmprouteradvertisement.icmprouteraddress.preferencelevel.preferencelevel import PreferenceLevel
		return PreferenceLevel(self)._read()

	@property
	def Name(self):
		"""Name

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('name')

	def read(self, Name=None):
		"""Get `icmp-router-address` resource(s). Returns all `icmp-router-address` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name):
		"""Create an instance of the `icmp-router-address` resource

		Args:
			Name (string): Name
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `icmp-router-address` resource

		"""
		return self._delete()

