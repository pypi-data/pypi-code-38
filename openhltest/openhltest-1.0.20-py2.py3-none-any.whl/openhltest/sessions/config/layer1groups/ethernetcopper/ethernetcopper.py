from openhltest_client.base import Base


class EthernetCopper(Base):
	"""TBD
	"""
	YANG_NAME = 'ethernet-copper'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"InternalPpmAdjust": "internal-ppm-adjust", "TransmitClockSource": "transmit-clock-source", "SpeedDuplexType": "speed-duplex-type", "AutoMdix": "auto-mdix", "AutoNegotiationEnabled": "auto-negotiation-enabled", "TxGapControl": "tx-gap-control", "IgnoreLinkStatus": "ignore-link-status", "Mtu": "mtu", "MasterSlaveType": "master-slave-type", "TxMode": "tx-mode", "DataPathMode": "data-path-mode", "OptimizedXon": "optimized-xon", "ForwardErrorCorrection": "forward-error-correction", "PortSetupMode": "port-setup-mode", "CollisionExponent": "collision-exponent", "AutoInstrumentation": "auto-instrumentation", "FlowControlDirectedAddress": "flow-control-directed-address", "RxMode": "rx-mode", "FlowControl": "flow-control", "CustomFecMode": "custom-fec-mode"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(EthernetCopper, self).__init__(parent)

	@property
	def PriorityBasedFlowControl(self):
		"""Priority-based Flow Control provides a link level flow control mechanism that can be controlled independently for each frame priority. The goal of this mechanism is to ensure zero loss under congestion in DCB networks

		Get an instance of the PriorityBasedFlowControl class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.layer1groups.ethernetcopper.prioritybasedflowcontrol.prioritybasedflowcontrol.PriorityBasedFlowControl)
		"""
		from openhltest_client.openhltest.sessions.config.layer1groups.ethernetcopper.prioritybasedflowcontrol.prioritybasedflowcontrol import PriorityBasedFlowControl
		return PriorityBasedFlowControl(self)._read()

	@property
	def DataCenterBridgingExchange(self):
		"""Data Center Bridging Exchange protocol is a discovery and capability exchange protocol that is used for conveying capabilities and configuration between neighbors to ensure consistent configuration across the network. This protocol leverages functionality provided by LLDP

		Get an instance of the DataCenterBridgingExchange class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.layer1groups.ethernetcopper.datacenterbridgingexchange.datacenterbridgingexchange.DataCenterBridgingExchange)
		"""
		from openhltest_client.openhltest.sessions.config.layer1groups.ethernetcopper.datacenterbridgingexchange.datacenterbridgingexchange import DataCenterBridgingExchange
		return DataCenterBridgingExchange(self)._read()

	@property
	def AutoNegotiationCapabilities(self):
		"""When auto negotiation is enabled the following speeds and duplex can be advertised

		Get an instance of the AutoNegotiationCapabilities class.

		Returns:
			obj(openhltest_client.openhltest.sessions.config.layer1groups.ethernetcopper.autonegotiationcapabilities.autonegotiationcapabilities.AutoNegotiationCapabilities)
		"""
		from openhltest_client.openhltest.sessions.config.layer1groups.ethernetcopper.autonegotiationcapabilities.autonegotiationcapabilities import AutoNegotiationCapabilities
		return AutoNegotiationCapabilities(self)._read()

	@property
	def AutoMdix(self):
		"""TBD

		Getter Returns:
			boolean

		Setter Allows:
			boolean

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('auto-mdix')

	@property
	def AutoInstrumentation(self):
		"""TBD

		Getter Returns:
			END_OF_FRAME | FLOATING

		Setter Allows:
			END_OF_FRAME | FLOATING

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('auto-instrumentation')

	@property
	def CollisionExponent(self):
		"""TBD

		Getter Returns:
			uint8

		Setter Allows:
			uint8

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('collision-exponent')

	@property
	def CustomFecMode(self):
		"""TBD

		Getter Returns:
			NONE | KR_FEC | RS_FEC

		Setter Allows:
			NONE | KR_FEC | RS_FEC

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('custom-fec-mode')

	@property
	def DataPathMode(self):
		"""TBD

		Getter Returns:
			NORMAL | LOOPBACK | LINE_MONITOR

		Setter Allows:
			NORMAL | LOOPBACK | LINE_MONITOR

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('data-path-mode')

	@property
	def FlowControl(self):
		"""Enables the port's MAC flow control mechanisms to listen for a directed address pause message

		Getter Returns:
			boolean

		Setter Allows:
			boolean

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('flow-control')

	@property
	def FlowControlDirectedAddress(self):
		"""The 48-bit MAC address that the port listens on for a directed pause.

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('flow-control-directed-address')

	@property
	def ForwardErrorCorrection(self):
		"""TBD

		Getter Returns:
			boolean

		Setter Allows:
			boolean

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('forward-error-correction')

	@property
	def IgnoreLinkStatus(self):
		"""TBD

		Getter Returns:
			boolean

		Setter Allows:
			boolean

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('ignore-link-status')

	@property
	def InternalPpmAdjust(self):
		"""TBD

		Getter Returns:
			int8

		Setter Allows:
			int8

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('internal-ppm-adjust')

	@property
	def Mtu(self):
		"""TBD

		Getter Returns:
			uint16

		Setter Allows:
			uint16

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('mtu')

	@property
	def OptimizedXon(self):
		"""TBD

		Getter Returns:
			DISABLE | ENABLE

		Setter Allows:
			DISABLE | ENABLE

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('optimized-xon')

	@property
	def PortSetupMode(self):
		"""TBD

		Getter Returns:
			PORTCONFIG_ONLY | REGISTERS_ONLY

		Setter Allows:
			PORTCONFIG_ONLY | REGISTERS_ONLY

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('port-setup-mode')

	@property
	def RxMode(self):
		"""TBD

		Getter Returns:
			CAPTURE | CAPTURE_AND_MEASURE | MEASURE | PACKET_IMPAIRMENT

		Setter Allows:
			CAPTURE | CAPTURE_AND_MEASURE | MEASURE | PACKET_IMPAIRMENT

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('rx-mode')

	@property
	def TransmitClockSource(self):
		"""TBD

		Getter Returns:
			INTERNAL | INTERNAL_PPM_ADJ | BITS | LOOP | EXTERNAL

		Setter Allows:
			INTERNAL | INTERNAL_PPM_ADJ | BITS | LOOP | EXTERNAL

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('transmit-clock-source')

	@property
	def TxGapControl(self):
		"""TBD

		Getter Returns:
			AVERAGE_MODE | FIXED_MODE

		Setter Allows:
			AVERAGE_MODE | FIXED_MODE

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('tx-gap-control')

	@property
	def TxMode(self):
		"""TBD

		Getter Returns:
			INTERLEAVED | INTERLEAVED_COARSE | PACKET_IMPAIRMENT | SEQUENTIAL | SEQUENTIAL_COARSE

		Setter Allows:
			INTERLEAVED | INTERLEAVED_COARSE | PACKET_IMPAIRMENT | SEQUENTIAL | SEQUENTIAL_COARSE

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('tx-mode')

	@property
	def AutoNegotiationEnabled(self):
		"""If enabled allows for auto negotiation between ports for speed and duplex operation.

		Getter Returns:
			boolean

		Setter Allows:
			boolean

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('auto-negotiation-enabled')

	@property
	def SpeedDuplexType(self):
		"""When auto negotiation is disabled a single speed and duplex type can be selected

		Getter Returns:
			1000G | 100M_FD | 100M_HD | 10M_FD | 10M_HD

		Setter Allows:
			1000G | 100M_FD | 100M_HD | 10M_FD | 10M_HD

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('speed-duplex-type')

	@property
	def MasterSlaveType(self):
		"""When auto negotiation is enabled one of the master slave types can be specified

		Getter Returns:
			MASTER | SLAVE | FAULT

		Setter Allows:
			MASTER | SLAVE | FAULT

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('master-slave-type')

	def update(self, AutoMdix=None, AutoInstrumentation=None, CollisionExponent=None, CustomFecMode=None, DataPathMode=None, FlowControl=None, FlowControlDirectedAddress=None, ForwardErrorCorrection=None, IgnoreLinkStatus=None, InternalPpmAdjust=None, Mtu=None, OptimizedXon=None, PortSetupMode=None, RxMode=None, TransmitClockSource=None, TxGapControl=None, TxMode=None, AutoNegotiationEnabled=None, SpeedDuplexType=None, MasterSlaveType=None):
		"""Update the current instance of the `ethernet-copper` resource

		Args:
			AutoMdix (boolean): TBD
			AutoInstrumentation (enumeration): TBD
			CollisionExponent (uint8): TBD
			CustomFecMode (enumeration): TBD
			DataPathMode (enumeration): TBD
			FlowControl (boolean): Enables the port's MAC flow control mechanisms to listen for a directed address pause message
			FlowControlDirectedAddress (string): The 48-bit MAC address that the port listens on for a directed pause.
			ForwardErrorCorrection (boolean): TBD
			IgnoreLinkStatus (boolean): TBD
			InternalPpmAdjust (int8): TBD
			Mtu (uint16): TBD
			OptimizedXon (enumeration): TBD
			PortSetupMode (enumeration): TBD
			RxMode (enumeration): TBD
			TransmitClockSource (enumeration): TBD
			TxGapControl (enumeration): TBD
			TxMode (enumeration): TBD
			AutoNegotiationEnabled (boolean): If enabled allows for auto negotiation between ports for speed and duplex operation.
			SpeedDuplexType (enumeration): When auto negotiation is disabled a single speed and duplex type can be selected
			MasterSlaveType (enumeration): When auto negotiation is enabled one of the master slave types can be specified
		"""
		return self._update(locals())

