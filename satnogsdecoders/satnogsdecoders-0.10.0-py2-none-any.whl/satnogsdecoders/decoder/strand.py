# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Strand(KaitaiStruct):
    """:field seq_no: seq_no
    :field length: length
    :field packet_type: packet_type
    :field channel: body.channel
    :field time_since_last_obc_i2c_message: body.data.time_since_last_obc_i2c_message
    :field packets_up_count: body.data.packets_up_count
    :field packets_down_count: body.data.packets_down_count
    :field packets_up_dropped_count: body.data.packets_up_dropped_count
    :field packets_down_dropped_count: body.data.packets_down_dropped_count
    :field i2c_node_address: body.i2c_node_address
    :field i2c_node_address: body.node.i2c_node_address
    :field battery_0_current_direction: body.node.node.battery_0_current_direction
    :field battery_0_current_ma: body.node.node.battery_0_current_ma
    :field battery_0_voltage_v: body.node.node.battery_0_voltage_v
    :field battery_0_temperature_deg_c: body.node.node.battery_0_temperature_deg_c
    :field battery_1_current_direction: body.node.node.battery_1_current_direction
    :field battery_1_current_ma: body.node.node.battery_1_current_ma
    :field battery_1_voltage_v: body.node.node.battery_1_voltage_v
    :field battery_1_temperature_deg_c: body.node.node.battery_1_temperature_deg_c
    :field adc1_py_array_current: body.node.node.adc1_py_array_current
    :field adc2_py_array_temperature: body.node.node.adc2_py_array_temperature
    :field adc3_array_pair_y_voltage: body.node.node.adc3_array_pair_y_voltage
    :field adc4_my_array_current: body.node.node.adc4_my_array_current
    :field adc5_my_array_temperature: body.node.node.adc5_my_array_temperature
    :field adc6_array_pair_x_voltage: body.node.node.adc6_array_pair_x_voltage
    :field adc7_mx_array_current: body.node.node.adc7_mx_array_current
    :field adc8_mx_array_temperature: body.node.node.adc8_mx_array_temperature
    :field adc9_array_pair_z_voltage: body.node.node.adc9_array_pair_z_voltage
    :field adc10_pz_array_current: body.node.node.adc10_pz_array_current
    :field adc11_pz_array_temperature: body.node.node.adc11_pz_array_temperature
    :field adc13_px_array_current: body.node.node.adc13_px_array_current
    :field adc14_px_array_temperature: body.node.node.adc14_px_array_temperature
    :field adc17_battery_bus_current: body.node.node.adc17_battery_bus_current
    :field adc26_5v_bus_current: body.node.node.adc26_5v_bus_current
    :field adc27_33v_bus_current: body.node.node.adc27_33v_bus_current
    :field adc30_mz_array_temperature: body.node.node.adc30_mz_array_temperature
    :field adc31_mz_array_current: body.node.node.adc31_mz_array_current
    :field switch_0_ppt_power_supply_status: body.node.node.switch_0_ppt_power_supply_status
    :field switch_1_ppt_1_2_status: body.node.node.switch_1_ppt_1_2_status
    :field switch_2_phone_5v_webcam: body.node.node.switch_2_phone_5v_webcam
    :field switch_3_warp_valve_status: body.node.node.switch_3_warp_valve_status
    :field switch_4_warp_heater_status: body.node.node.switch_4_warp_heater_status
    :field switch_5_digi_wi9c_status: body.node.node.switch_5_digi_wi9c_status
    :field switch_6_sgr05_status: body.node.node.switch_6_sgr05_status
    :field switch_7_reaction_wheels: body.node.node.switch_7_reaction_wheels
    :field switch_8_solar_panel_deploy_arm: body.node.node.switch_8_solar_panel_deploy_arm
    :field switch_9_solar_panel_deploy_fire: body.node.node.switch_9_solar_panel_deploy_fire
    :field unix_time_little_endian: body.node.node.unix_time_little_endian
    :field magnetometer_set_1: body.node.node.magnetometer_set_1
    :field magnetometer_set_2: body.node.node.magnetometer_set_2
    
    .. seealso::
       Source - https://ukamsat.files.wordpress.com/2013/03/amsat-strand-1-20130327.xlsx
       https://amsat-uk.org/satellites/telemetry/strand-1/strand-1-telemetry/
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.hdlc_flag = self._io.ensure_fixed_contents(b"\xC0\x80")
        self.seq_no = self._io.read_u1()
        self.length = self._io.read_u1()
        self.packet_type = self._io.read_u1()
        _on = self.packet_type
        if _on == 1:
            self.body = self._root.ModemBeaconTlm(self._io, self, self._root)
        elif _on == 2:
            self.body = self._root.ObcBeaconTlm(self._io, self, self._root)
        self.crc_16_ccit = self._io.read_bytes(2)

    class ChAdc1PyArrayCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc1_py_array_current = self._io.read_u1()


    class ChSwitch1Ppt12Status(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_1_ppt_1_2_status = self._io.read_u1()


    class ChAdc9ArrayPairZVoltage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc9_array_pair_z_voltage = self._io.read_u1()


    class ChBattery1CurrentDirection(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_1_current_direction = self._io.read_u1()


    class ModemBeaconTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.channel = self._io.read_u1()
            _on = self.channel
            if _on == 224:
                self.data = self._root.ChTimeSinceLastObcI2cMessage(self._io, self, self._root)
            elif _on == 227:
                self.data = self._root.ChPacketsUpDroppedCount(self._io, self, self._root)
            elif _on == 226:
                self.data = self._root.ChPacketsDownCount(self._io, self, self._root)
            elif _on == 225:
                self.data = self._root.ChPacketsUpCount(self._io, self, self._root)
            elif _on == 228:
                self.data = self._root.ChPacketsDownDroppedCount(self._io, self, self._root)


    class ChMagnetometerSet1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magnetometer_set_1 = self._io.read_u1()


    class CsBattery(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_node_address = self._io.read_u1()
            _on = self.i2c_node_address
            if _on == 14:
                self.node = self._root.ChAdc14PxArrayTemperature(self._io, self, self._root)
            elif _on == 10:
                self.node = self._root.ChAdc10PzArrayCurrent(self._io, self, self._root)
            elif _on == 17:
                self.node = self._root.ChAdc17BatteryBusCurrent(self._io, self, self._root)
            elif _on == 4:
                self.node = self._root.ChAdc4MyArrayCurrent(self._io, self, self._root)
            elif _on == 6:
                self.node = self._root.ChAdc6ArrayPairXVoltage(self._io, self, self._root)
            elif _on == 7:
                self.node = self._root.ChAdc7MxArrayCurrent(self._io, self, self._root)
            elif _on == 1:
                self.node = self._root.ChAdc1PyArrayCurrent(self._io, self, self._root)
            elif _on == 27:
                self.node = self._root.ChAdc2733vBusCurrent(self._io, self, self._root)
            elif _on == 13:
                self.node = self._root.ChAdc13PxArrayCurrent(self._io, self, self._root)
            elif _on == 11:
                self.node = self._root.ChAdc11PzArrayTemperature(self._io, self, self._root)
            elif _on == 3:
                self.node = self._root.ChAdc3ArrayPairYVoltage(self._io, self, self._root)
            elif _on == 5:
                self.node = self._root.ChAdc5MyArrayTemperature(self._io, self, self._root)
            elif _on == 8:
                self.node = self._root.ChAdc8MxArrayTemperature(self._io, self, self._root)
            elif _on == 9:
                self.node = self._root.ChAdc9ArrayPairZVoltage(self._io, self, self._root)
            elif _on == 26:
                self.node = self._root.ChAdc265vBusCurrent(self._io, self, self._root)
            elif _on == 31:
                self.node = self._root.ChAdc31MzArrayCurrent(self._io, self, self._root)
            elif _on == 2:
                self.node = self._root.ChAdc2PyArrayTemperature(self._io, self, self._root)
            elif _on == 30:
                self.node = self._root.ChAdc30MzArrayTemperature(self._io, self, self._root)


    class ChAdc3ArrayPairYVoltage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc3_array_pair_y_voltage = self._io.read_u1()


    class ChSwitch9SolarPanelDeployFire(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_9_solar_panel_deploy_fire = self._io.read_u1()


    class ChBattery1VoltageV(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_1_voltage_v = self._io.read_u1()


    class ChAdc4MyArrayCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc4_my_array_current = self._io.read_u1()


    class ChAdc2PyArrayTemperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc2_py_array_temperature = self._io.read_u1()


    class ChUnixTimeLittleEndian(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unix_time_little_endian = self._io.read_u1()


    class ChTimeSinceLastObcI2cMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.time_since_last_obc_i2c_message = self._io.read_u1()


    class ChSwitch0PptPowerSupplyStatus(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_0_ppt_power_supply_status = self._io.read_u1()


    class ChBattery0CurrentDirection(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_0_current_direction = self._io.read_u1()


    class ObcData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_node_address = self._io.read_u1()
            _on = self.i2c_node_address
            if _on == 12:
                self.node = self._root.ChUnixTimeLittleEndian(self._io, self, self._root)


    class ChMagnetometerSet2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magnetometer_set_2 = self._io.read_u1()


    class ChAdc2733vBusCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc27_33v_bus_current = self._io.read_u1()


    class ChSwitch6Sgr05Status(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_6_sgr05_status = self._io.read_u1()


    class CsEps(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_node_address = self._io.read_u1()
            _on = self.i2c_node_address
            if _on == 0:
                self.node = self._root.ChBattery0CurrentDirection(self._io, self, self._root)
            elif _on == 4:
                self.node = self._root.ChBattery0TemperatureDegC(self._io, self, self._root)
            elif _on == 6:
                self.node = self._root.ChBattery1CurrentMa(self._io, self, self._root)
            elif _on == 1:
                self.node = self._root.ChBattery0CurrentMa(self._io, self, self._root)
            elif _on == 3:
                self.node = self._root.ChBattery0VoltageV(self._io, self, self._root)
            elif _on == 5:
                self.node = self._root.ChBattery1CurrentDirection(self._io, self, self._root)
            elif _on == 8:
                self.node = self._root.ChBattery1VoltageV(self._io, self, self._root)
            elif _on == 9:
                self.node = self._root.ChBattery1TemperatureDegC(self._io, self, self._root)


    class ChAdc7MxArrayCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc7_mx_array_current = self._io.read_u1()


    class ChAdc31MzArrayCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc31_mz_array_current = self._io.read_u1()


    class ChSwitch8SolarPanelDeployArm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_8_solar_panel_deploy_arm = self._io.read_u1()


    class ChAdc5MyArrayTemperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc5_my_array_temperature = self._io.read_u1()


    class ChPacketsDownDroppedCount(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packets_down_dropped_count = self._io.read_u1()


    class ObcBeaconTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_node_address = self._io.read_u1()
            _on = self.i2c_node_address
            if _on == 45:
                self.node = self._root.CsBattery(self._io, self, self._root)
            elif _on == 137:
                self.node = self._root.Magnetometers(self._io, self, self._root)
            elif _on == 44:
                self.node = self._root.CsEps(self._io, self, self._root)
            elif _on == 102:
                self.node = self._root.SwitchBoard(self._io, self, self._root)
            elif _on == 128:
                self.node = self._root.ObcData(self._io, self, self._root)


    class ChPacketsUpCount(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packets_up_count = self._io.read_u1()


    class ChSwitch3WarpValveStatus(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_3_warp_valve_status = self._io.read_u1()


    class ChBattery0VoltageV(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_0_voltage_v = self._io.read_u1()


    class ChAdc13PxArrayCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc13_px_array_current = self._io.read_u1()


    class ChAdc30MzArrayTemperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc30_mz_array_temperature = self._io.read_u1()


    class ChAdc8MxArrayTemperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc8_mx_array_temperature = self._io.read_u1()


    class ChAdc14PxArrayTemperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc14_px_array_temperature = self._io.read_u1()


    class ChBattery0CurrentMa(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_0_current_ma = self._io.read_u1()


    class ChAdc6ArrayPairXVoltage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc6_array_pair_x_voltage = self._io.read_u1()


    class ChSwitch2Phone5vWebcam(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_2_phone_5v_webcam = self._io.read_u1()


    class ChPacketsDownCount(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packets_down_count = self._io.read_u1()


    class ChAdc10PzArrayCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc10_pz_array_current = self._io.read_u1()


    class ChAdc17BatteryBusCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc17_battery_bus_current = self._io.read_u1()


    class ChAdc11PzArrayTemperature(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc11_pz_array_temperature = self._io.read_u1()


    class ChSwitch4WarpHeaterStatus(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_4_warp_heater_status = self._io.read_u1()


    class ChPacketsUpDroppedCount(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packets_up_dropped_count = self._io.read_u1()


    class ChSwitch7ReactionWheels(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_7_reaction_wheels = self._io.read_u1()


    class ChBattery1TemperatureDegC(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_1_temperature_deg_c = self._io.read_u1()


    class ChSwitch5DigiWi9cStatus(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.switch_5_digi_wi9c_status = self._io.read_u1()


    class SwitchBoard(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_node_address = self._io.read_u1()
            _on = self.i2c_node_address
            if _on == 159:
                self.node = self._root.ChSwitch6Sgr05Status(self._io, self, self._root)
            elif _on == 169:
                self.node = self._root.ChSwitch8SolarPanelDeployArm(self._io, self, self._root)
            elif _on == 144:
                self.node = self._root.ChSwitch3WarpValveStatus(self._io, self, self._root)
            elif _on == 149:
                self.node = self._root.ChSwitch4WarpHeaterStatus(self._io, self, self._root)
            elif _on == 172:
                self.node = self._root.ChSwitch9SolarPanelDeployFire(self._io, self, self._root)
            elif _on == 164:
                self.node = self._root.ChSwitch7ReactionWheels(self._io, self, self._root)
            elif _on == 129:
                self.node = self._root.ChSwitch0PptPowerSupplyStatus(self._io, self, self._root)
            elif _on == 134:
                self.node = self._root.ChSwitch1Ppt12Status(self._io, self, self._root)
            elif _on == 139:
                self.node = self._root.ChSwitch2Phone5vWebcam(self._io, self, self._root)
            elif _on == 154:
                self.node = self._root.ChSwitch5DigiWi9cStatus(self._io, self, self._root)


    class ChBattery0TemperatureDegC(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_0_temperature_deg_c = self._io.read_u1()


    class ChAdc265vBusCurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc26_5v_bus_current = self._io.read_u1()


    class Magnetometers(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.i2c_node_address = self._io.read_u1()
            _on = self.i2c_node_address
            if _on == 3:
                self.node = self._root.ChMagnetometerSet1(self._io, self, self._root)
            elif _on == 5:
                self.node = self._root.ChMagnetometerSet2(self._io, self, self._root)


    class ChBattery1CurrentMa(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_1_current_ma = self._io.read_u1()



