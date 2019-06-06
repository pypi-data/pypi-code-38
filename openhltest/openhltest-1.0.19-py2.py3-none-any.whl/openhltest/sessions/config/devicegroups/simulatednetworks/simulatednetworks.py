from openhltest_client.base import Base


class SimulatedNetworks(Base):
	"""A list of network groups.
	Each network group object can contain 0..n networks objects

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/simulated-networks resource.
	"""
	YANG_NAME = 'simulated-networks'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"ParentLink": "parent-link", "Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(SimulatedNetworks, self).__init__(parent)

	@property
	def Networks(self):
		"""A list of networks.
		Each networks object is a container for one and only one of the network types.

		Get an instance of the Networks class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.networks.Networks)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.simulatednetworks.networks.networks import Networks
		return Networks(self)

	@property
	def Name(self):
		"""The unique name of the network groups object.

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
	def ParentLink(self):
		"""Identifies which devices object or networks object is connected to this object.
		This is used to create a netwwork groups container behind a devices or networks container.

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
		"""Get `simulated-networks` resource(s). Returns all `simulated-networks` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, ParentLink=None):
		"""Create an instance of the `simulated-networks` resource

		Args:
			Name (string): The unique name of the network groups object.
			ParentLink (union[leafref]): Identifies which devices object or networks object is connected to this object.This is used to create a netwwork groups container behind a devices or networks container.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `simulated-networks` resource

		"""
		return self._delete()

	def update(self, ParentLink=None):
		"""Update the current instance of the `simulated-networks` resource

		Args:
			ParentLink (union[leafref]): Identifies which devices object or networks object is connected to this object.This is used to create a netwwork groups container behind a devices or networks container.
		"""
		return self._update(locals())

