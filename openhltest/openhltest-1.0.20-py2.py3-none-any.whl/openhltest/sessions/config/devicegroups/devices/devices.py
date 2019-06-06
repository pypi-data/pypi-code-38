from openhltest_client.base import Base


class Devices(Base):
	"""A list of devices.
	Each devices object can contain 0..n protocols objects

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/devices resource.
	"""
	YANG_NAME = 'devices'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"ParentLink": "parent-link", "DeviceCountPerPort": "device-count-per-port", "Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Devices, self).__init__(parent)

	@property
	def Protocols(self):
		"""A list of emulated protocols.
		Each emulated protocols object is a container for one and only one of the emulated protocol types.
		The protocol-type is used to specify what type of protocol is contained in a protocols object.

		Get an instance of the Protocols class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.protocols.Protocols)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.protocols import Protocols
		return Protocols(self)

	@property
	def Name(self):
		"""The unique name of a devices object.

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
	def DeviceCountPerPort(self):
		"""The number of devices that will be created on each
		abstract test port specified in the port-names list.

		Getter Returns:
			uint32

		Setter Allows:
			uint32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('device-count-per-port')

	@property
	def ParentLink(self):
		"""Identifies which devices object or simulated-networks object is connected to this object.
		This is used to create a devices container behind a devices or simulated networks container.
		An empty link indicates that the object is at the top of the stack.

		Getter Returns:
			union[leafref]

		Setter Allows:
			union[leafref]

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('parent-link')

	def read(self, Name=None):
		"""Get `devices` resource(s). Returns all `devices` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, DeviceCountPerPort=None, ParentLink=None):
		"""Create an instance of the `devices` resource

		Args:
			Name (string): The unique name of a devices object.
			DeviceCountPerPort (uint32): The number of devices that will be created on eachabstract test port specified in the port-names list.
			ParentLink (union[leafref]): Identifies which devices object or simulated-networks object is connected to this object.This is used to create a devices container behind a devices or simulated networks container.An empty link indicates that the object is at the top of the stack.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `devices` resource

		"""
		return self._delete()

	def update(self, DeviceCountPerPort=None, ParentLink=None):
		"""Update the current instance of the `devices` resource

		Args:
			DeviceCountPerPort (uint32): The number of devices that will be created on eachabstract test port specified in the port-names list.
			ParentLink (union[leafref]): Identifies which devices object or simulated-networks object is connected to this object.This is used to create a devices container behind a devices or simulated networks container.An empty link indicates that the object is at the top of the stack.
		"""
		return self._update(locals())

