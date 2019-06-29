# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Irazu(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field beacon_verf_code: ax25_frame.payload.ax25_info.data.beacon_verf_code
    :field time_sync: ax25_frame.payload.ax25_info.data.time_sync_int
    :field timestamp: ax25_frame.payload.ax25_info.data.timestamp
    :field mission_files: ax25_frame.payload.ax25_info.data.mission_files_int
    :field buffers_free: ax25_frame.payload.ax25_info.data.buffers_free_int
    :field last_rssi: ax25_frame.payload.ax25_info.data.last_rssi_int
    :field obc_temp1: ax25_frame.payload.ax25_info.data.obc_temp1_flt
    :field obc_temp2: ax25_frame.payload.ax25_info.data.obc_temp2_flt
    :field com_temp_pa: ax25_frame.payload.ax25_info.data.com_temp_pa_int
    :field com_temp_mcu: ax25_frame.payload.ax25_info.data.com_temp_mcu_int
    :field eps_temp_t4: ax25_frame.payload.ax25_info.data.eps_temp_t4_int
    :field bat_voltage: ax25_frame.payload.ax25_info.data.bat_voltage_int
    :field cur_sun: ax25_frame.payload.ax25_info.data.cur_sun_int
    :field cur_sys: ax25_frame.payload.ax25_info.data.cur_sys_int
    :field batt_mode: ax25_frame.payload.ax25_info.data.batt_mode_int
    :field panel1_voltage: ax25_frame.payload.ax25_info.data.panel1_voltage_int
    :field panel2_voltage: ax25_frame.payload.ax25_info.data.panel2_voltage_int
    :field panel3_voltage: ax25_frame.payload.ax25_info.data.panel3_voltage_int
    :field panel1_current: ax25_frame.payload.ax25_info.data.panel1_current_int
    :field panel2_current: ax25_frame.payload.ax25_info.data.panel2_current_int
    :field panel3_current: ax25_frame.payload.ax25_info.data.panel3_current_int
    :field bat_bootcount: ax25_frame.payload.ax25_info.data.bat_bootcount_int
    :field gyro_x: ax25_frame.payload.ax25_info.data.gyro_x_flt
    :field gyro_y: ax25_frame.payload.ax25_info.data.gyro_y_flt
    :field gyro_z: ax25_frame.payload.ax25_info.data.gyro_z_flt
    :field magneto_x: ax25_frame.payload.ax25_info.data.magneto_x_flt
    :field magneto_y: ax25_frame.payload.ax25_info.data.magneto_y_flt
    :field magneto_z: ax25_frame.payload.ax25_info.data.magneto_z_flt
    
    Attention: `rpt_callsign` cannot be accessed because `rpt_instance` is an
    array of unknown size at the beginning of the parsing process! Left an
    example in here.
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
            self.ax25_info = self._root.Ax25InfoData(io, self, self._root)


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
            self._raw_ax25_info = self._io.read_bytes_full()
            io = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = self._root.Ax25InfoData(io, self, self._root)


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


    class Beacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.prefix = self._io.read_bytes(4)
            self.beacon_verf_code = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.time_sync_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.time_sync = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.timestamp_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.timestamp = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.mission_files_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.mission_files = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.buffers_free_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.buffers_free = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.last_rssi_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.last_rssi = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.obc_temperature_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.obc_temp1_int = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.obc_temp1_frac = (self._io.read_bytes_term(47, False, True, True)).decode(u"utf-8")
            self.obc_temp2_int = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.obc_temp2_frac = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.com_temperature_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.com_temp_pa = (self._io.read_bytes_term(47, False, True, True)).decode(u"utf-8")
            self.com_temp_mcu = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.eps_temp_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.eps_temp_t4 = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.bat_voltage_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.bat_voltage = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.cur_sun_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.cur_sun = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.cur_sys_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.cur_sys = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.batt_mode_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.batt_mode = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.panels_voltage_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.panel1_voltage = (self._io.read_bytes_term(47, False, True, True)).decode(u"utf-8")
            self.panel2_voltage = (self._io.read_bytes_term(47, False, True, True)).decode(u"utf-8")
            self.panel3_voltage = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.panels_current_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.panel1_current = (self._io.read_bytes_term(47, False, True, True)).decode(u"utf-8")
            self.panel2_current = (self._io.read_bytes_term(47, False, True, True)).decode(u"utf-8")
            self.panel3_current = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.bat_bootcount_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.bat_bootcount = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.gyro_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.gyro_x_int = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.gyro_x_frac = (self._io.read_bytes_term(47, False, True, True)).decode(u"utf-8")
            self.gyro_y_int = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.gyro_y_frac = (self._io.read_bytes_term(47, False, True, True)).decode(u"utf-8")
            self.gyro_z_int = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.gyro_z_frac = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf-8")
            self.magneto_label = (self._io.read_bytes(1)).decode(u"utf-8")
            self.magneto_x_int = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.magneto_x_frac = (self._io.read_bytes_term(47, False, True, True)).decode(u"utf-8")
            self.magneto_y_int = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.magneto_y_frac = (self._io.read_bytes_term(47, False, True, True)).decode(u"utf-8")
            self.magneto_z_int = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf-8")
            self.magneto_z_frac = (self._io.read_bytes_term(0, False, True, True)).decode(u"utf-8")
            self.suffix = self._io.read_bytes(5)

        @property
        def magneto_y_flt(self):
            """R[1]."""
            if hasattr(self, '_m_magneto_y_flt'):
                return self._m_magneto_y_flt if hasattr(self, '_m_magneto_y_flt') else None

            self._m_magneto_y_flt = (int(self.magneto_y_int) + ((((int(int(self.magneto_y_int) < 0) * -2) + 1) * int(self.magneto_y_frac)) / 1000.0))
            return self._m_magneto_y_flt if hasattr(self, '_m_magneto_y_flt') else None

        @property
        def batt_mode_int(self):
            """M."""
            if hasattr(self, '_m_batt_mode_int'):
                return self._m_batt_mode_int if hasattr(self, '_m_batt_mode_int') else None

            self._m_batt_mode_int = int(self.batt_mode)
            return self._m_batt_mode_int if hasattr(self, '_m_batt_mode_int') else None

        @property
        def time_sync_int(self):
            """A."""
            if hasattr(self, '_m_time_sync_int'):
                return self._m_time_sync_int if hasattr(self, '_m_time_sync_int') else None

            self._m_time_sync_int = int(self.time_sync)
            return self._m_time_sync_int if hasattr(self, '_m_time_sync_int') else None

        @property
        def panel2_voltage_int(self):
            """N[1]."""
            if hasattr(self, '_m_panel2_voltage_int'):
                return self._m_panel2_voltage_int if hasattr(self, '_m_panel2_voltage_int') else None

            self._m_panel2_voltage_int = int(self.panel2_voltage)
            return self._m_panel2_voltage_int if hasattr(self, '_m_panel2_voltage_int') else None

        @property
        def panel1_current_int(self):
            """O[0]."""
            if hasattr(self, '_m_panel1_current_int'):
                return self._m_panel1_current_int if hasattr(self, '_m_panel1_current_int') else None

            self._m_panel1_current_int = int(self.panel1_current)
            return self._m_panel1_current_int if hasattr(self, '_m_panel1_current_int') else None

        @property
        def obc_temp2_flt(self):
            """G[1]."""
            if hasattr(self, '_m_obc_temp2_flt'):
                return self._m_obc_temp2_flt if hasattr(self, '_m_obc_temp2_flt') else None

            self._m_obc_temp2_flt = (int(self.obc_temp2_int) + ((((int(int(self.obc_temp2_int) < 0) * -2) + 1) * int(self.obc_temp2_frac)) / 100.0))
            return self._m_obc_temp2_flt if hasattr(self, '_m_obc_temp2_flt') else None

        @property
        def gyro_y_flt(self):
            """Q[1]."""
            if hasattr(self, '_m_gyro_y_flt'):
                return self._m_gyro_y_flt if hasattr(self, '_m_gyro_y_flt') else None

            self._m_gyro_y_flt = (int(self.gyro_y_int) + ((((int(int(self.gyro_y_int) < 0) * -2) + 1) * int(self.gyro_y_frac)) / 1000000.0))
            return self._m_gyro_y_flt if hasattr(self, '_m_gyro_y_flt') else None

        @property
        def magneto_z_flt(self):
            """R[2]."""
            if hasattr(self, '_m_magneto_z_flt'):
                return self._m_magneto_z_flt if hasattr(self, '_m_magneto_z_flt') else None

            self._m_magneto_z_flt = (int(self.magneto_z_int) + ((((int(int(self.magneto_z_int) < 0) * -2) + 1) * int(self.magneto_z_frac)) / 1000.0))
            return self._m_magneto_z_flt if hasattr(self, '_m_magneto_z_flt') else None

        @property
        def gyro_x_flt(self):
            """Q[0]."""
            if hasattr(self, '_m_gyro_x_flt'):
                return self._m_gyro_x_flt if hasattr(self, '_m_gyro_x_flt') else None

            self._m_gyro_x_flt = (int(self.gyro_x_int) + ((((int(int(self.gyro_x_int) < 0) * -2) + 1) * int(self.gyro_x_frac)) / 1000000.0))
            return self._m_gyro_x_flt if hasattr(self, '_m_gyro_x_flt') else None

        @property
        def magneto_x_flt(self):
            """R[0]."""
            if hasattr(self, '_m_magneto_x_flt'):
                return self._m_magneto_x_flt if hasattr(self, '_m_magneto_x_flt') else None

            self._m_magneto_x_flt = (int(self.magneto_x_int) + ((((int(int(self.magneto_x_int) < 0) * -2) + 1) * int(self.magneto_x_frac)) / 1000.0))
            return self._m_magneto_x_flt if hasattr(self, '_m_magneto_x_flt') else None

        @property
        def panel2_current_int(self):
            """O[1]."""
            if hasattr(self, '_m_panel2_current_int'):
                return self._m_panel2_current_int if hasattr(self, '_m_panel2_current_int') else None

            self._m_panel2_current_int = int(self.panel2_current)
            return self._m_panel2_current_int if hasattr(self, '_m_panel2_current_int') else None

        @property
        def com_temp_mcu_int(self):
            """H[1]."""
            if hasattr(self, '_m_com_temp_mcu_int'):
                return self._m_com_temp_mcu_int if hasattr(self, '_m_com_temp_mcu_int') else None

            self._m_com_temp_mcu_int = int(self.com_temp_mcu)
            return self._m_com_temp_mcu_int if hasattr(self, '_m_com_temp_mcu_int') else None

        @property
        def obc_temp1_flt(self):
            """G[0]."""
            if hasattr(self, '_m_obc_temp1_flt'):
                return self._m_obc_temp1_flt if hasattr(self, '_m_obc_temp1_flt') else None

            self._m_obc_temp1_flt = (int(self.obc_temp1_int) + ((((int(int(self.obc_temp1_int) < 0) * -2) + 1) * int(self.obc_temp1_frac)) / 100.0))
            return self._m_obc_temp1_flt if hasattr(self, '_m_obc_temp1_flt') else None

        @property
        def panel3_voltage_int(self):
            """N[2]."""
            if hasattr(self, '_m_panel3_voltage_int'):
                return self._m_panel3_voltage_int if hasattr(self, '_m_panel3_voltage_int') else None

            self._m_panel3_voltage_int = int(self.panel3_voltage)
            return self._m_panel3_voltage_int if hasattr(self, '_m_panel3_voltage_int') else None

        @property
        def buffers_free_int(self):
            """E."""
            if hasattr(self, '_m_buffers_free_int'):
                return self._m_buffers_free_int if hasattr(self, '_m_buffers_free_int') else None

            self._m_buffers_free_int = int(self.buffers_free)
            return self._m_buffers_free_int if hasattr(self, '_m_buffers_free_int') else None

        @property
        def bat_voltage_int(self):
            """J."""
            if hasattr(self, '_m_bat_voltage_int'):
                return self._m_bat_voltage_int if hasattr(self, '_m_bat_voltage_int') else None

            self._m_bat_voltage_int = int(self.bat_voltage)
            return self._m_bat_voltage_int if hasattr(self, '_m_bat_voltage_int') else None

        @property
        def panel3_current_int(self):
            """O[2]."""
            if hasattr(self, '_m_panel3_current_int'):
                return self._m_panel3_current_int if hasattr(self, '_m_panel3_current_int') else None

            self._m_panel3_current_int = int(self.panel3_current)
            return self._m_panel3_current_int if hasattr(self, '_m_panel3_current_int') else None

        @property
        def cur_sun_int(self):
            """K."""
            if hasattr(self, '_m_cur_sun_int'):
                return self._m_cur_sun_int if hasattr(self, '_m_cur_sun_int') else None

            self._m_cur_sun_int = int(self.cur_sun)
            return self._m_cur_sun_int if hasattr(self, '_m_cur_sun_int') else None

        @property
        def mission_files_int(self):
            """D."""
            if hasattr(self, '_m_mission_files_int'):
                return self._m_mission_files_int if hasattr(self, '_m_mission_files_int') else None

            self._m_mission_files_int = int(self.mission_files)
            return self._m_mission_files_int if hasattr(self, '_m_mission_files_int') else None

        @property
        def com_temp_pa_int(self):
            """H[0]."""
            if hasattr(self, '_m_com_temp_pa_int'):
                return self._m_com_temp_pa_int if hasattr(self, '_m_com_temp_pa_int') else None

            self._m_com_temp_pa_int = int(self.com_temp_pa)
            return self._m_com_temp_pa_int if hasattr(self, '_m_com_temp_pa_int') else None

        @property
        def bat_bootcount_int(self):
            """P."""
            if hasattr(self, '_m_bat_bootcount_int'):
                return self._m_bat_bootcount_int if hasattr(self, '_m_bat_bootcount_int') else None

            self._m_bat_bootcount_int = int(self.bat_bootcount)
            return self._m_bat_bootcount_int if hasattr(self, '_m_bat_bootcount_int') else None

        @property
        def gyro_z_flt(self):
            """Q[2]."""
            if hasattr(self, '_m_gyro_z_flt'):
                return self._m_gyro_z_flt if hasattr(self, '_m_gyro_z_flt') else None

            self._m_gyro_z_flt = (int(self.gyro_z_int) + ((((int(int(self.gyro_z_int) < 0) * -2) + 1) * int(self.gyro_z_frac)) / 1000000.0))
            return self._m_gyro_z_flt if hasattr(self, '_m_gyro_z_flt') else None

        @property
        def panel1_voltage_int(self):
            """N[0]."""
            if hasattr(self, '_m_panel1_voltage_int'):
                return self._m_panel1_voltage_int if hasattr(self, '_m_panel1_voltage_int') else None

            self._m_panel1_voltage_int = int(self.panel1_voltage)
            return self._m_panel1_voltage_int if hasattr(self, '_m_panel1_voltage_int') else None

        @property
        def last_rssi_int(self):
            """F."""
            if hasattr(self, '_m_last_rssi_int'):
                return self._m_last_rssi_int if hasattr(self, '_m_last_rssi_int') else None

            self._m_last_rssi_int = int(self.last_rssi)
            return self._m_last_rssi_int if hasattr(self, '_m_last_rssi_int') else None

        @property
        def cur_sys_int(self):
            """L."""
            if hasattr(self, '_m_cur_sys_int'):
                return self._m_cur_sys_int if hasattr(self, '_m_cur_sys_int') else None

            self._m_cur_sys_int = int(self.cur_sys)
            return self._m_cur_sys_int if hasattr(self, '_m_cur_sys_int') else None

        @property
        def eps_temp_t4_int(self):
            """I."""
            if hasattr(self, '_m_eps_temp_t4_int'):
                return self._m_eps_temp_t4_int if hasattr(self, '_m_eps_temp_t4_int') else None

            self._m_eps_temp_t4_int = int(self.eps_temp_t4)
            return self._m_eps_temp_t4_int if hasattr(self, '_m_eps_temp_t4_int') else None


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


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.tlm_type
            if _on == 66:
                self.data = self._root.Beacon(self._io, self, self._root)

        @property
        def tlm_type(self):
            if hasattr(self, '_m_tlm_type'):
                return self._m_tlm_type if hasattr(self, '_m_tlm_type') else None

            _pos = self._io.pos()
            self._io.seek(4)
            self._m_tlm_type = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_tlm_type if hasattr(self, '_m_tlm_type') else None



