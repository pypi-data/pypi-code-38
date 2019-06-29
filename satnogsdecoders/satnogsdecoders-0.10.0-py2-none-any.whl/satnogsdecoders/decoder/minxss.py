# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Minxss(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field spacecraft_flags: ax25_frame.payload.ax25_info.beacon.spacecraft_flags
    :field pointing_mode: ax25_frame.payload.ax25_info.beacon.pointing_mode
    :field cmd_accept_cnt: ax25_frame.payload.ax25_info.beacon.cmd_accept_cnt
    :field flight_model: ax25_frame.payload.ax25_info.beacon.flight_model
    :field cdh_board_temp: ax25_frame.payload.ax25_info.beacon.cdh_board_temp
    :field enable_flags: ax25_frame.payload.ax25_info.beacon.enable_flags
    :field comm_brd_temp: ax25_frame.payload.ax25_info.beacon.comm_brd_temp
    :field mbrd_temp: ax25_frame.payload.ax25_info.beacon.mbrd_temp
    :field eps_brd_temp: ax25_frame.payload.ax25_info.beacon.eps_brd_temp
    :field battery_voltage: ax25_frame.payload.ax25_info.beacon.battery_voltage
    :field solar_panel_minus_y_curr: ax25_frame.payload.ax25_info.beacon.solar_panel_minus_y_curr
    :field solar_panel_minus_y_volt: ax25_frame.payload.ax25_info.beacon.solar_panel_minus_y_volt
    :field solar_panel_plus_x_curr: ax25_frame.payload.ax25_info.beacon.solar_panel_plus_x_curr
    :field solar_panel_plus_x_volt: ax25_frame.payload.ax25_info.beacon.solar_panel_plus_x_volt
    :field solar_panel_plus_y_curr: ax25_frame.payload.ax25_info.beacon.solar_panel_plus_y_curr
    :field solar_panel_plus_y_volt: ax25_frame.payload.ax25_info.beacon.solar_panel_plus_y_volt
    :field solar_panel_minus_y_temp: ax25_frame.payload.ax25_info.beacon.solar_panel_minus_y_temp
    :field solar_panel_plus_x_temp: ax25_frame.payload.ax25_info.beacon.solar_panel_plus_x_temp
    :field solar_panel_plus_y_temp: ax25_frame.payload.ax25_info.beacon.solar_panel_plus_y_temp
    :field battery_chrg_curr: ax25_frame.payload.ax25_info.beacon.battery_chrg_curr
    :field battery_dchrg_curr: ax25_frame.payload.ax25_info.beacon.battery_dchrg_curr
    :field battery_temp: ax25_frame.payload.ax25_info.beacon.battery_temp
    :field xp: ax25_frame.payload.ax25_info.beacon.xp
    :field sps_x: ax25_frame.payload.ax25_info.beacon.sps_x
    :field sps_y: ax25_frame.payload.ax25_info.beacon.sps_y
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
            self.ax25_info = self._root.Telemetry(io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class HskpData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.res_1 = [None] * (10)
            for i in range(10):
                self.res_1[i] = self._io.read_u1()

            self.spacecraft_flags = self._io.read_u1()
            self.pointing_mode = self._io.read_u1()
            self.res_2 = self._io.read_u2be()
            self.cmd_accept_cnt = self._io.read_u2le()
            self.res_3 = [None] * (33)
            for i in range(33):
                self.res_3[i] = self._io.read_u1()

            self.flight_model = self._io.read_u1()
            self.res_4 = [None] * (34)
            for i in range(34):
                self.res_4[i] = self._io.read_u1()

            self.cdh_board_temp = self._io.read_s2le()
            self.enable_flags = self._io.read_u2be()
            self.res_5 = [None] * (32)
            for i in range(32):
                self.res_5[i] = self._io.read_u1()

            self.comm_brd_temp = self._io.read_s2le()
            self.mbrd_temp = self._io.read_s2le()
            self.res_6 = self._io.read_u2be()
            self.eps_brd_temp = self._io.read_s2le()
            self.res_7 = self._io.read_u2be()
            self.battery_voltage = self._io.read_u2le()
            self.res_8 = self._io.read_u2be()
            self.solar_panel_minus_y_curr = self._io.read_u2le()
            self.solar_panel_minus_y_volt = self._io.read_u2le()
            self.solar_panel_plus_x_curr = self._io.read_u2le()
            self.solar_panel_plus_x_volt = self._io.read_u2le()
            self.solar_panel_plus_y_curr = self._io.read_u2le()
            self.solar_panel_plus_y_volt = self._io.read_u2le()
            self.res_9 = [None] * (12)
            for i in range(12):
                self.res_9[i] = self._io.read_u1()

            self.solar_panel_minus_y_temp = self._io.read_u2le()
            self.solar_panel_plus_x_temp = self._io.read_u2le()
            self.solar_panel_plus_y_temp = self._io.read_u2le()
            self.res_0 = self._io.read_u2be()
            self.battery_chrg_curr = self._io.read_u2le()
            self.res_a = self._io.read_u2be()
            self.battery_dchrg_curr = self._io.read_u2le()
            self.battery_temp = self._io.read_u2le()
            self.res_b = [None] * (16)
            for i in range(16):
                self.res_b[i] = self._io.read_u1()

            self.xp = self._io.read_u4le()
            self.res_c = [None] * (10)
            for i in range(10):
                self.res_c[i] = self._io.read_u1()

            self.sps_x = self._io.read_u2le()
            self.sps_y = self._io.read_u2le()


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


    class RtData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rt_data_raw = self._io.read_bytes((self._io.size() - 4))


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


    class Telemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.start_sync_flag = self._io.read_u2be()
            _on = self.start_sync_flag
            if _on == 2073:
                self._raw_beacon = self._io.read_bytes((self._io.size() - 4))
                io = KaitaiStream(BytesIO(self._raw_beacon))
                self.beacon = self._root.HskpData(io, self, self._root)
            elif _on == 2077:
                self._raw_beacon = self._io.read_bytes((self._io.size() - 4))
                io = KaitaiStream(BytesIO(self._raw_beacon))
                self.beacon = self._root.RtData(io, self, self._root)
            else:
                self.beacon = self._io.read_bytes((self._io.size() - 4))
            self.stop_sync_flag = self._io.ensure_fixed_contents(b"\xA5\xA5")



