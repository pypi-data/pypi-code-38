from openhltest_client.base import Base


class Layer1Groups(Base):
	"""A group of layer1 settings that will be applied to each port's location.
	The vendor implementation should apply layer 1 settings when starting protocols.
	If the port's location is empty then nothing will be applied to that port.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/layer1-groups resource.
	"""
	YANG_NAME = 'layer1-groups'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name", "Layer1Type": "layer1-type", "Ports": "ports"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Layer1Groups, self).__init__(parent)

	@property
	def EthernetCopper(self):
		"""TBD

		Get an instance of the EthernetCopper class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.layer1groups.ethernetcopper.ethernetcopper.EthernetCopper)
		"""
		from openhltest_client.openhltest.sessions.config.layer1groups.ethernetcopper.ethernetcopper import EthernetCopper
		return EthernetCopper(self)._read()

	@property
	def EthernetFiber(self):
		"""TBD

		Get an instance of the EthernetFiber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.layer1groups.ethernetfiber.ethernetfiber.EthernetFiber)
		"""
		from openhltest_client.openhltest.sessions.config.layer1groups.ethernetfiber.ethernetfiber import EthernetFiber
		return EthernetFiber(self)._read()

	@property
	def TenGigCopper(self):
		"""TBD

		Get an instance of the TenGigCopper class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.layer1groups.tengigcopper.tengigcopper.TenGigCopper)
		"""
		from openhltest_client.openhltest.sessions.config.layer1groups.tengigcopper.tengigcopper import TenGigCopper
		return TenGigCopper(self)._read()

	@property
	def TenGigFiber(self):
		"""TBD

		Get an instance of the TenGigFiber class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.layer1groups.tengigfiber.tengigfiber.TenGigFiber)
		"""
		from openhltest_client.openhltest.sessions.config.layer1groups.tengigfiber.tengigfiber import TenGigFiber
		return TenGigFiber(self)._read()

	@property
	def TwentyFiveGig(self):
		"""TBD

		Get an instance of the TwentyFiveGig class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.layer1groups.twentyfivegig.twentyfivegig.TwentyFiveGig)
		"""
		from openhltest_client.openhltest.sessions.config.layer1groups.twentyfivegig.twentyfivegig import TwentyFiveGig
		return TwentyFiveGig(self)._read()

	@property
	def Name(self):
		"""The unique name of a layer1 group

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

	@property
	def Layer1Type(self):
		"""TBD

		Getter Returns:
			ETHERNET_COPPER | ETHERNET_FIBER | TEN_GIG_COPPER | TEN_GIG_FIBER | TWENTY_FIVE_GIG | FORTY_GIG | FIFTY_GIG | ONE_HUNDRED_GIG | TWO_HUNDRED_GIG | FOUR_HUNDRED_GIG

		Setter Allows:
			ETHERNET_COPPER | ETHERNET_FIBER | TEN_GIG_COPPER | TEN_GIG_FIBER | TWENTY_FIVE_GIG | FORTY_GIG | FIFTY_GIG | ONE_HUNDRED_GIG | TWO_HUNDRED_GIG | FOUR_HUNDRED_GIG

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('layer1-type')

	def read(self, Name=None):
		"""Get `layer1-groups` resource(s). Returns all `layer1-groups` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, Ports=None, Layer1Type=None):
		"""Create an instance of the `layer1-groups` resource

		Args:
			Name (string): The unique name of a layer1 group
			Ports (leafref): A list of abstract test port names.Every object in the devices and protocols lists will share the ports assigned to a device-groups object.An abstract test port name cannot be assigned to more than one device-groups object.
			Layer1Type (enumeration): TBD
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `layer1-groups` resource

		"""
		return self._delete()

	def update(self, Ports=None, Layer1Type=None):
		"""Update the current instance of the `layer1-groups` resource

		Args:
			Ports (leafref): A list of abstract test port names.Every object in the devices and protocols lists will share the ports assigned to a device-groups object.An abstract test port name cannot be assigned to more than one device-groups object.
			Layer1Type (enumeration): TBD
		"""
		return self._update(locals())

