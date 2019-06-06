from openhltest_client.base import Base


class DeviceGroups(Base):
	"""A list of device-groups.
	Each device-groups object can contain 0..n devices.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups resource.
	"""
	YANG_NAME = 'device-groups'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name", "Ports": "ports"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(DeviceGroups, self).__init__(parent)

	@property
	def Devices(self):
		"""A list of devices.
		Each devices object can contain 0..n protocols objects

		Get an instance of the Devices class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.devices.Devices)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.devices import Devices
		return Devices(self)

	@property
	def SimulatedNetworks(self):
		"""A list of network groups.
		Each network group object can contain 0..n networks objects

		Get an instance of the SimulatedNetworks class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.simulatednetworks.SimulatedNetworks)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.simulatednetworks import SimulatedNetworks
		return SimulatedNetworks(self)

	@property
	def Name(self):
		"""The unique name of a device-groups object.

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
	def Ports(self):
		"""A list of abstract test port names.
		Every object in the devices and protocols lists will share the ports assigned to a device-groups object.
		An abstract test port name cannot be assigned to more than one device-groups object.

		Getter Returns:
			list(OpenHLTest.Sessions.Config.Ports.Name)

		Setter Allows:
			obj(OpenHLTest.Sessions.Config.Ports) | list(OpenHLTest.Sessions.Config.Ports.Name)

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('ports')

	def read(self, Name=None):
		"""Get `device-groups` resource(s). Returns all `device-groups` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, Ports=None):
		"""Create an instance of the `device-groups` resource

		Args:
			Name (string): The unique name of a device-groups object.
			Ports (leafref): A list of abstract test port names.Every object in the devices and protocols lists will share the ports assigned to a device-groups object.An abstract test port name cannot be assigned to more than one device-groups object.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `device-groups` resource

		"""
		return self._delete()

	def update(self, Ports=None):
		"""Update the current instance of the `device-groups` resource

		Args:
			Ports (leafref): A list of abstract test port names.Every object in the devices and protocols lists will share the ports assigned to a device-groups object.An abstract test port name cannot be assigned to more than one device-groups object.
		"""
		return self._update(locals())

