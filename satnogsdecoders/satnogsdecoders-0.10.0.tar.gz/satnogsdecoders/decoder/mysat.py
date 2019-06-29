# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Mysat(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field callsign: ax25_frame.payload.ax25_info.beacon_type.callsign
    :field obc_mode: ax25_frame.payload.ax25_info.beacon_type.obc_mode
    :field obc_reset_counter: ax25_frame.payload.ax25_info.beacon_type.obc_reset_counter
    :field obc_uptime: ax25_frame.payload.ax25_info.beacon_type.obc_uptime
    :field gyro_norm: ax25_frame.payload.ax25_info.beacon_type.gyro_norm
    :field eps_reset_counter: ax25_frame.payload.ax25_info.beacon_type.eps_reset_counter
    :field eps_last_boot_cause: ax25_frame.payload.ax25_info.beacon_type.eps_last_boot_cause
    :field eps_battery_mode: ax25_frame.payload.ax25_info.beacon_type.eps_battery_mode
    :field timestamp: ax25_frame.payload.ax25_info.beacon_type.timestamp
    :field obc_temperature: ax25_frame.payload.ax25_info.beacon_type.obc_temperature
    :field obc_daughterboard_temperature: ax25_frame.payload.ax25_info.beacon_type.obc_daughterboard_temperature
    :field eps_battery_temperature: ax25_frame.payload.ax25_info.beacon_type.eps_battery_temperature
    :field eps_board_temperature: ax25_frame.payload.ax25_info.beacon_type.eps_board_temperature
    :field ants_temperature: ax25_frame.payload.ax25_info.beacon_type.ants_temperature
    :field trxvu_temperature: ax25_frame.payload.ax25_info.beacon_type.trxvu_temperature
    :field adcs_temperature: ax25_frame.payload.ax25_info.beacon_type.adcs_temperature
    :field obc_3v3_voltage: ax25_frame.payload.ax25_info.beacon_type.obc_3v3_voltage
    :field camera_voltage: ax25_frame.payload.ax25_info.beacon_type.camera_voltage
    :field trxvu_voltage: ax25_frame.payload.ax25_info.beacon_type.trxvu_voltage
    :field eps_battery_voltage: ax25_frame.payload.ax25_info.beacon_type.eps_battery_voltage
    :field obc_5v_current: ax25_frame.payload.ax25_info.beacon_type.obc_5v_current
    :field eps_total_pv_current: ax25_frame.payload.ax25_info.beacon_type.eps_total_pv_current
    :field eps_total_system_current: ax25_frame.payload.ax25_info.beacon_type.eps_total_system_current
    :field message: ax25_frame.payload.ax25_info.beacon_type.message
    
    Attention: `rpt_callsign` cannot be accessed because `rpt_instance` is an
    array of unknown size at the beginning of the parsing process! Left an
    example in here.
    
    .. seealso::
       
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = self._root.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = self._root.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = self._root.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = self._root.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = self._root.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = self._root.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = self._root.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = self._root.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = self._root.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = self._root.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = self._root.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = self._root.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = self._root.Repeater(self._io, self, self._root)

            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_info = self._io.read_bytes_full()
            io = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = self._root.MysatPayload(io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


    class SsidMask(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ssid_mask = self._io.read_u1()

        @property
        def ssid(self):
            if hasattr(self, '_m_ssid'):
                return self._m_ssid if hasattr(self, '_m_ssid') else None

            self._m_ssid = ((self.ssid_mask & 15) >> 1)
            return self._m_ssid if hasattr(self, '_m_ssid') else None


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = self._root.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = self._root.SsidMask(self._io, self, self._root)


    class Repeater(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_instance = []
            i = 0
            while True:
                _ = self._root.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class MysatMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.message = (self._io.read_bytes_full()).decode(u"utf-8")


    class MysatPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._io.size()
            if _on == 42:
                self.beacon_type = self._root.MysatTlm(self._io, self, self._root)
            else:
                self.beacon_type = self._root.MysatMessage(self._io, self, self._root)


    class CallsignRaw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_callsign_ror = self._io.read_bytes(6)
            self._raw_callsign_ror = KaitaiStream.process_rotate_left(self._raw__raw_callsign_ror, 8 - (1), 1)
            io = KaitaiStream(BytesIO(self._raw_callsign_ror))
            self.callsign_ror = self._root.Callsign(io, self, self._root)


    class MysatTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(5)).decode(u"utf-8")
            self.obc_mode = self._io.read_u1()
            self.obc_reset_counter = self._io.read_u4le()
            self.obc_uptime = self._io.read_u4le()
            self.gyro_norm = self._io.read_u1()
            self.eps_reset_counter = self._io.read_u4le()
            self.eps_last_boot_cause = self._io.read_u1()
            self.eps_battery_mode = self._io.read_u1()
            self.timestamp = self._io.read_u4le()
            self.obc_temperature = self._io.read_u1()
            self.obc_daughterboard_temperature = self._io.read_u1()
            self.eps_battery_temperature = self._io.read_u1()
            self.eps_board_temperature = self._io.read_u1()
            self.ants_temperature = self._io.read_u1()
            self.trxvu_temperature = self._io.read_u1()
            self.adcs_temperature = self._io.read_u1()
            self.obc_3v3_voltage = self._io.read_u1()
            self.camera_voltage = self._io.read_u1()
            self.trxvu_voltage = self._io.read_u1()
            self.eps_battery_voltage = self._io.read_u1()
            self.obc_5v_current = self._io.read_u2le()
            self.eps_total_pv_current = self._io.read_u2le()
            self.eps_total_system_current = self._io.read_u2le()


    @property
    def frame_length(self):
        if hasattr(self, '_m_frame_length'):
            return self._m_frame_length if hasattr(self, '_m_frame_length') else None

        self._m_frame_length = self._io.size()
        return self._m_frame_length if hasattr(self, '_m_frame_length') else None


