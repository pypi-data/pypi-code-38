from openhltest_client.base import Base


class Protocols(Base):
	"""A list of emulated protocols.
	Each emulated protocols object is a container for one and only one of the emulated protocol types.
	The protocol-type is used to specify what type of protocol is contained in a protocols object.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/devices/protocols resource.
	"""
	YANG_NAME = 'protocols'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"FlowLink": "flow-link", "ProtocolType": "protocol-type", "ParentLink": "parent-link", "Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Protocols, self).__init__(parent)

	@property
	def Ethernet(self):
		"""TBD

		Get an instance of the Ethernet class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ethernet.ethernet.Ethernet)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ethernet.ethernet import Ethernet
		return Ethernet(self)._read()

	@property
	def Vlan(self):
		"""TBD

		Get an instance of the Vlan class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.vlan.vlan.Vlan)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.vlan.vlan import Vlan
		return Vlan(self)._read()

	@property
	def Ipv4(self):
		"""TBD

		Get an instance of the Ipv4 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv4.ipv4.Ipv4)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv4.ipv4 import Ipv4
		return Ipv4(self)._read()

	@property
	def Ipv6(self):
		"""TBD

		Get an instance of the Ipv6 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv6.ipv6.Ipv6)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ipv6.ipv6 import Ipv6
		return Ipv6(self)._read()

	@property
	def Bgpv4(self):
		"""TBD

		Get an instance of the Bgpv4 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.bgpv4.Bgpv4)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv4.bgpv4 import Bgpv4
		return Bgpv4(self)._read()

	@property
	def Bgpv6(self):
		"""TBD

		Get an instance of the Bgpv6 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv6.bgpv6.Bgpv6)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bgpv6.bgpv6 import Bgpv6
		return Bgpv6(self)._read()

	@property
	def Ospfv2(self):
		"""TBD

		Get an instance of the Ospfv2 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ospfv2.ospfv2.Ospfv2)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ospfv2.ospfv2 import Ospfv2
		return Ospfv2(self)._read()

	@property
	def Ospfv3(self):
		"""TBD

		Get an instance of the Ospfv3 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ospfv3.ospfv3.Ospfv3)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.ospfv3.ospfv3 import Ospfv3
		return Ospfv3(self)._read()

	@property
	def Isis(self):
		"""TBD

		Get an instance of the Isis class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.isis.Isis)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.isis.isis import Isis
		return Isis(self)._read()

	@property
	def Bfdv4(self):
		"""TBD

		Get an instance of the Bfdv4 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bfdv4.bfdv4.Bfdv4)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bfdv4.bfdv4 import Bfdv4
		return Bfdv4(self)._read()

	@property
	def Bfdv6(self):
		"""TBD

		Get an instance of the Bfdv6 class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bfdv6.bfdv6.Bfdv6)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devices.protocols.bfdv6.bfdv6 import Bfdv6
		return Bfdv6(self)._read()

	@property
	def Name(self):
		"""The unique name of a protocols object

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
		"""Identifies which protocols object is the parent of this protocol.
		This link only applies to protocol objects in one container.
		The link can be used to specify a vertical or horizontal relationship.
		To specify the first protocols object in a stack the value must be empty.

		Getter Returns:
			union[leafref]

		Setter Allows:
			union[leafref]

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('parent-link')

	@property
	def FlowLink(self):
		"""Identifies which object in another container is the next hop from this container.
		The name cannot be one of the names in this devices container.
		An empty link indicates no flow link

		Getter Returns:
			union[leafref]

		Setter Allows:
			union[leafref]

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('flow-link')

	@property
	def ProtocolType(self):
		"""Determines which detailed emulated protocol container is active.

		Getter Returns:
			ETHERNET | VLAN | IPV4 | IPV6 | BGPV4 | BGPV6 | OSPFV2 | OSPFV3 | ISIS | BFDV4 | BFDV6

		Setter Allows:
			ETHERNET | VLAN | IPV4 | IPV6 | BGPV4 | BGPV6 | OSPFV2 | OSPFV3 | ISIS | BFDV4 | BFDV6

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('protocol-type')

	def read(self, Name=None):
		"""Get `protocols` resource(s). Returns all `protocols` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, ParentLink=None, FlowLink=None, ProtocolType=None):
		"""Create an instance of the `protocols` resource

		Args:
			Name (string): The unique name of a protocols object
			ParentLink (union[leafref]): Identifies which protocols object is the parent of this protocol.This link only applies to protocol objects in one container.The link can be used to specify a vertical or horizontal relationship.To specify the first protocols object in a stack the value must be empty.
			FlowLink (union[leafref]): Identifies which object in another container is the next hop from this container.The name cannot be one of the names in this devices container.An empty link indicates no flow link
			ProtocolType (enumeration): Determines which detailed emulated protocol container is active.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `protocols` resource

		"""
		return self._delete()

	def update(self, ParentLink=None, FlowLink=None, ProtocolType=None):
		"""Update the current instance of the `protocols` resource

		Args:
			ParentLink (union[leafref]): Identifies which protocols object is the parent of this protocol.This link only applies to protocol objects in one container.The link can be used to specify a vertical or horizontal relationship.To specify the first protocols object in a stack the value must be empty.
			FlowLink (union[leafref]): Identifies which object in another container is the next hop from this container.The name cannot be one of the names in this devices container.An empty link indicates no flow link
			ProtocolType (enumeration): Determines which detailed emulated protocol container is active.
		"""
		return self._update(locals())

