# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Qbee(KaitaiStruct):
    """:field wod_time: beacon_data.wod.wod_time
    :field wod_mode: beacon_data.wod.wod_mode
    :field wod_voltage_battery: beacon_data.wod.wod_voltage_battery
    :field wod_current_battery: beacon_data.wod.wod_current_battery
    :field wod_current_3v3: beacon_data.wod.wod_current_3v3
    :field wod_current_5v: beacon_data.wod.wod_current_5v
    :field wod_temperature_comms: beacon_data.wod.wod_temperature_comms
    :field wod_temperature_eps: beacon_data.wod.wod_temperature_eps
    :field wod_temperature_battery: beacon_data.wod.wod_temperature_battery
    :field pwr_info_adcs: beacon_data.power_info.pwr_info_adcs
    :field pwr_info_fipex: beacon_data.power_info.pwr_info_fipex
    :field pwr_info_gps: beacon_data.power_info.pwr_info_gps
    :field pwr_info_ocobc: beacon_data.power_info.pwr_info_ocobc
    :field service_enabled_adcs: beacon_data.service_enabled.service_enabled_adcs
    :field service_enabled_fipex: beacon_data.service_enabled.service_enabled_fipex
    :field service_enabled_ocobc: beacon_data.service_enabled.service_enabled_ocobc
    :field service_running_adcs: beacon_data.service_running.service_running_adcs
    :field service_running_fipex: beacon_data.service_running.service_running_fipex
    :field service_running_ocobc: beacon_data.service_running.service_running_ocobc
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax_header = self._root.AxHeader(self._io, self, self._root)
        self.csp_header = self._io.read_bytes(4)
        self.beacon_data = self._root.BeaconData(self._io, self, self._root)
        self.rs_parity = self._io.read_bytes(32)

    class ServiceEnabled(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.service_enabled_adcs = self._io.read_bits_int(1) != 0
            self.service_enabled_fipex = self._io.read_bits_int(1) != 0
            self.service_enabled_ocobc = self._io.read_bits_int(1) != 0
            self.service_enabled_reserved = self._io.read_bits_int(5)


    class AxHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.destination = (self._io.read_bytes(6)).decode(u"ASCII")
            self.destination_ssid = self._io.read_u1()
            self.source = (self._io.read_bytes(6)).decode(u"ASCII")
            self.source_ssid = self._io.read_u1()
            self.control = self._io.read_u1()
            self.pid = self._io.read_u1()


    class BeaconData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.wod = self._root.Wod(self._io, self, self._root)
            self.power_info = self._root.PowerInfo(self._io, self, self._root)
            self.service_enabled = self._root.ServiceEnabled(self._io, self, self._root)
            self.service_running = self._root.ServiceRunning(self._io, self, self._root)
            self.reserved = self._io.read_bytes(14)


    class ServiceRunning(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.service_running_adcs = self._io.read_bits_int(1) != 0
            self.service_running_fipex = self._io.read_bits_int(1) != 0
            self.service_running_ocobc = self._io.read_bits_int(1) != 0
            self.service_running_reserved = self._io.read_bits_int(5)


    class PowerInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pwr_info_adcs = self._io.read_bits_int(1) != 0
            self.pwr_info_fipex = self._io.read_bits_int(1) != 0
            self.pwr_info_gps = self._io.read_bits_int(1) != 0
            self.pwr_info_ocobc = self._io.read_bits_int(1) != 0
            self.pwr_info_reserved = self._io.read_bits_int(4)


    class Wod(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.wod_time = self._io.read_u4le()
            self.wod_mode = self._io.read_u1()
            self.wod_voltage_battery = self._io.read_u1()
            self.wod_current_battery = self._io.read_u1()
            self.wod_current_3v3 = self._io.read_u1()
            self.wod_current_5v = self._io.read_u1()
            self.wod_temperature_comms = self._io.read_u1()
            self.wod_temperature_eps = self._io.read_u1()
            self.wod_temperature_battery = self._io.read_u1()



