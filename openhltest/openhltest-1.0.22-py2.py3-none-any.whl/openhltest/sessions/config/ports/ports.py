from openhltest_client.base import Base


class Ports(Base):
	"""A list of abstract test ports

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/ports resource.
	"""
	YANG_NAME = 'ports'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name", "Location": "location"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ports, self).__init__(parent)

	@property
	def Name(self):
		"""The unique name of an abstract test port

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('name')

	@property
	def Location(self):
		"""The location of the physical or virtual port that will be connected to this abstract port.
		The value pattern must be chassis/card/port where chassis is an ipv4/ipv6 address and card/port are unsigned byte 1-255.
		The separator between the chassis/card/port values must be a forward slash.

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('location')

	def read(self, Name=None):
		"""Get `ports` resource(s). Returns all `ports` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, Location=None):
		"""Create an instance of the `ports` resource

		Args:
			Name (string): The unique name of an abstract test port
			Location (string): The location of the physical or virtual port that will be connected to this abstract port.The value pattern must be chassis/card/port where chassis is an ipv4/ipv6 address and card/port are unsigned byte 1-255.The separator between the chassis/card/port values must be a forward slash.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `ports` resource

		"""
		return self._delete()

	def update(self, Location=None):
		"""Update the current instance of the `ports` resource

		Args:
			Location (string): The location of the physical or virtual port that will be connected to this abstract port.The value pattern must be chassis/card/port where chassis is an ipv4/ipv6 address and card/port are unsigned byte 1-255.The separator between the chassis/card/port values must be a forward slash.
		"""
		return self._update(locals())

