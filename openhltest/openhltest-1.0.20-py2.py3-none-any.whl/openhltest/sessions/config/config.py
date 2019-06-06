from openhltest_client.base import Base


class Config(Base):
	"""This container aggregates all other top level configuration submodules.
	"""
	YANG_NAME = 'config'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = ["commit", "port-control", "clear", "load", "save", "arp-control", "traffic-control", "device-groups-control", "bgpv4-control", "bgpv6-control", "ospfv2-control", "ospfv3-control", "isis-control", "bfdv4-control", "bfdv6-control"]

	def __init__(self, parent):
		super(Config, self).__init__(parent)

	@property
	def Ports(self):
		"""A list of abstract test ports

		Get an instance of the Ports class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.ports.ports.Ports)
		"""
		from openhltest_client.openhltest.sessions.config.ports.ports import Ports
		return Ports(self)

	@property
	def Layer1Groups(self):
		"""A group of layer1 settings that will be applied to each port's location.
		The vendor implementation should apply layer 1 settings when starting protocols.
		If the port's location is empty then nothing will be applied to that port.

		Get an instance of the Layer1Groups class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.layer1groups.layer1groups.Layer1Groups)
		"""
		from openhltest_client.openhltest.sessions.config.layer1groups.layer1groups import Layer1Groups
		return Layer1Groups(self)

	@property
	def GlobalProtocols(self):
		"""This list allows for configuring global protocols options.

		Get an instance of the GlobalProtocols class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.globalprotocols.globalprotocols.GlobalProtocols)
		"""
		from openhltest_client.openhltest.sessions.config.globalprotocols.globalprotocols import GlobalProtocols
		return GlobalProtocols(self)._read()

	@property
	def DeviceGroups(self):
		"""A list of device-groups.
		Each device-groups object can contain 0..n devices.

		Get an instance of the DeviceGroups class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicegroups.devicegroups.DeviceGroups)
		"""
		from openhltest_client.openhltest.sessions.config.devicegroups.devicegroups import DeviceGroups
		return DeviceGroups(self)

	@property
	def PortTraffic(self):
		"""A list of traffic streams where each traffic stream
		has a single transmit port as its source and a list of user defined frames.

		Get an instance of the PortTraffic class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.porttraffic.porttraffic.PortTraffic)
		"""
		from openhltest_client.openhltest.sessions.config.porttraffic.porttraffic import PortTraffic
		return PortTraffic(self)

	@property
	def DeviceTraffic(self):
		"""This is a collection of nodes that the server uses to generate 1..n traffic-streams.
		The source and destinations of the device traffic group can only come from the device-groups list or its children.

		Get an instance of the DeviceTraffic class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.devicetraffic.devicetraffic.DeviceTraffic)
		"""
		from openhltest_client.openhltest.sessions.config.devicetraffic.devicetraffic import DeviceTraffic
		return DeviceTraffic(self)

	def Commit(self):
		"""Notify the server to push all uncommitted config changes to vendor hardware

		"""
		return self._execute('commit')

	def PortControl(self, input):
		"""Control one or more physical hardware test ports and/or
		virtual machine test ports.
		An empty targets list signifies that all ports will be subject to the mode specified.

		Args:
			input ({"targets": "leafref", "mode": "enumeration"})

		"""
		return self._execute('port-control', input)

	def Clear(self):
		"""Clear the current configuration

		"""
		return self._execute('clear')

	def Load(self, input):
		"""Load a configuration

		Args:
			input ({"mode": "enumeration", "file-name": "string"})

		"""
		with open(input['file-name'], 'rb') as fid:
			import base64
			input['file-name'] = base64.b64encode(fid.read())
		return self._execute('load', input)

	def Save(self, input):
		"""Save the current configuration

		Args:
			input ({"mode": "enumeration", "file-name": "string"})

		Returns:
			({"content": "string"})

		"""
		output = self._execute('save', input)
		with open(input['file-name'], 'wb') as fid:
			import base64
			fid.write(base64.b64decode(output['content']))
		return output

	def ArpControl(self, input):
		"""ARP control command.
		An empty targets list signifies that ARP will be performed globally

		Args:
			input ({"targets": "union[leafref]"})

		"""
		return self._execute('arp-control', input)

	def TrafficControl(self, input):
		"""Control one or more traffic groups.
		An empty list signifies that all traffic will be subject to the mode specified.

		Args:
			input ({"targets": "union[leafref]", "mode": "enumeration"})

		"""
		return self._execute('traffic-control', input)

	def DeviceGroupsControl(self, input):
		"""Control one or more device-groups.
		An empty list signifies that all device-groups will be subject to the mode specified.

		Args:
			input ({"targets": "leafref", "mode": "enumeration"})

		"""
		return self._execute('device-groups-control', input)

	def Bgpv4Control(self, input):
		"""Start one or more emulated BGPV4 protocol groups.
		An empty targets list signifies that all BGPV4 protocol groups will be subject to the mode specified.

		Args:
			input ({"targets": "leafref", "mode": "enumeration"})

		"""
		return self._execute('bgpv4-control', input)

	def Bgpv6Control(self, input):
		"""Start one or more emulated BGPV6 protocol groups.
		An empty targets list signifies that all BGPV6 protocol groups will be subject to the mode specified.

		Args:
			input ({"targets": "leafref", "mode": "enumeration"})

		"""
		return self._execute('bgpv6-control', input)

	def Ospfv2Control(self, input):
		"""Start one or more emulated OSPFV2 protocol groups.
		An empty targets list signifies that all OSPFV2 protocol groups will be subject to the mode specified.

		Args:
			input ({"targets": "leafref", "mode": "enumeration"})

		"""
		return self._execute('ospfv2-control', input)

	def Ospfv3Control(self, input):
		"""Start one or more emulated OSPFV3 protocol groups.
		An empty targets list signifies that all OSPFV3 protocol groups will be subject to the mode specified.

		Args:
			input ({"targets": "leafref", "mode": "enumeration"})

		"""
		return self._execute('ospfv3-control', input)

	def IsisControl(self, input):
		"""Start one or more emulated ISIS protocol groups.
		An empty targets list signifies that all ISIS protocol groups will be subject to the mode specified.

		Args:
			input ({"targets": "leafref", "mode": "enumeration"})

		"""
		return self._execute('isis-control', input)

	def Bfdv4Control(self, input):
		"""Start one or more emulated BFD v4 protocol groups.
		An empty targets list signifies that all BFD v4 protocol groups will be subject to the mode specified.

		Args:
			input ({"targets": "leafref", "mode": "enumeration"})

		"""
		return self._execute('bfdv4-control', input)

	def Bfdv6Control(self, input):
		"""Start one or more emulated BFD v6 protocol groups.
		An empty targets list signifies that all BFD v6 protocol groups will be subject to the mode specified.

		Args:
			input ({"targets": "leafref", "mode": "enumeration"})

		"""
		return self._execute('bfdv6-control', input)

