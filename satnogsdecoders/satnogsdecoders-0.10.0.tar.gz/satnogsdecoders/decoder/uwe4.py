# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Uwe4(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field beacon_header_flags1: ax25_frame.payload.ax25_info.beacon_header.beacon_header_flags1
    :field beacon_header_flags2: ax25_frame.payload.ax25_info.beacon_header.beacon_header_flags2
    :field beacon_header_packet_id: ax25_frame.payload.ax25_info.beacon_header.beacon_header_packet_id
    :field beacon_header_fm_system_id: ax25_frame.payload.ax25_info.beacon_header.beacon_header_fm_system_id
    :field beacon_header_fm_subsystem_id: ax25_frame.payload.ax25_info.beacon_header.beacon_header_fm_subsystem_id
    :field beacon_header_to_system_id: ax25_frame.payload.ax25_info.beacon_header.beacon_header_to_system_id
    :field beacon_header_to_subsystem_id: ax25_frame.payload.ax25_info.beacon_header.beacon_header_to_subsystem_id
    :field beacon_header_api: ax25_frame.payload.ax25_info.beacon_header.beacon_header_api
    :field beacon_header_payload_size: ax25_frame.payload.ax25_info.beacon_header.beacon_header_payload_size
    :field beacon_payload_command: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_command
    :field beacon_payload_var_id: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_var_id
    :field beacon_payload_typeandlength: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_typeandlength
    :field beacon_payload_timestamp: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_timestamp
    :field beacon_payload_beacon_rate: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_beacon_rate
    :field beacon_payload_vals_out_of_range: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_vals_out_of_range
    :field beacon_payload_uptime: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_uptime
    :field beacon_payload_subsystem_status_bitmap: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_subsystem_status.beacon_payload_subsystem_status_bitmap
    :field beacon_payload_batt_a_temp: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_batt_a_temp
    :field beacon_payload_batt_a_state_of_charge: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_batt_a_state_of_charge
    :field beacon_payload_batt_b_temp: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_batt_b_temp
    :field beacon_payload_batt_b_state_of_charge: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_batt_b_state_of_charge
    :field beacon_payload_batt_a_current: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_batt_a_current
    :field beacon_payload_batt_a_voltage: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_batt_a_voltage
    :field beacon_payload_batt_b_current: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_batt_b_current
    :field beacon_payload_batt_b_voltage: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_batt_b_voltage
    :field beacon_payload_power_consumption: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_power_consumption
    :field beacon_payload_obc_temp: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_obc_temp
    :field beacon_payload_panel_pos_x_temp: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_panel_pos_x_temp
    :field beacon_payload_panel_neg_x_temp: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_panel_neg_x_temp
    :field beacon_payload_panel_pos_y_temp: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_panel_pos_y_temp
    :field beacon_payload_panel_neg_y_temp: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_panel_neg_y_temp
    :field beacon_payload_panel_pos_z_temp: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_panel_pos_z_temp
    :field beacon_payload_panel_neg_z_temp: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_panel_neg_z_temp
    :field beacon_payload_freq: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_freq
    :field beacon_payload_crc: ax25_frame.payload.ax25_info.beacon_payload.beacon_payload_crc
    :field rf_message: ax25_frame.payload.ax25_info.beacon_payload.message
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


    class HskpPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_payload_command = self._io.read_u1()
            self.beacon_payload_var_id = self._io.read_u2le()
            self.beacon_payload_typeandlength = self._io.read_u2le()
            self.beacon_payload_timestamp_raw = [None] * (6)
            for i in range(6):
                self.beacon_payload_timestamp_raw[i] = self._io.read_u1()

            self.beacon_payload_beacon_rate = self._io.read_u4le()
            self.beacon_payload_vals_out_of_range = self._io.read_u2le()
            self.beacon_payload_uptime = self._io.read_u4le()
            self.beacon_payload_subsystem_status = self._root.Bitmap16SubsystemStatus(self._io, self, self._root)
            self.beacon_payload_batt_a_temp = self._io.read_s1()
            self.beacon_payload_batt_a_state_of_charge = self._io.read_s1()
            self.beacon_payload_batt_b_temp = self._io.read_s1()
            self.beacon_payload_batt_b_state_of_charge = self._io.read_s1()
            self.beacon_payload_batt_a_current = self._io.read_s2le()
            self.beacon_payload_batt_a_voltage = self._io.read_s2le()
            self.beacon_payload_batt_b_current = self._io.read_s2le()
            self.beacon_payload_batt_b_voltage = self._io.read_s2le()
            self.beacon_payload_power_consumption = self._io.read_s2le()
            self.beacon_payload_obc_temp = self._io.read_s1()
            self.beacon_payload_panel_pos_x_temp = self._io.read_s1()
            self.beacon_payload_panel_neg_x_temp = self._io.read_s1()
            self.beacon_payload_panel_pos_y_temp = self._io.read_s1()
            self.beacon_payload_panel_neg_y_temp = self._io.read_s1()
            self.beacon_payload_panel_pos_z_temp = self._io.read_s1()
            self.beacon_payload_panel_neg_z_temp = self._io.read_s1()
            self.beacon_payload_freq = self._io.read_u2le()
            self.beacon_payload_crc = self._io.read_u2le()

        @property
        def beacon_payload_timestamp(self):
            if hasattr(self, '_m_beacon_payload_timestamp'):
                return self._m_beacon_payload_timestamp if hasattr(self, '_m_beacon_payload_timestamp') else None

            self._m_beacon_payload_timestamp = (((((self.beacon_payload_timestamp_raw[0] + (self.beacon_payload_timestamp_raw[1] << 8)) + (self.beacon_payload_timestamp_raw[2] << 16)) + (self.beacon_payload_timestamp_raw[3] << 24)) + (self.beacon_payload_timestamp_raw[4] << 32)) + (self.beacon_payload_timestamp_raw[5] << 48))
            return self._m_beacon_payload_timestamp if hasattr(self, '_m_beacon_payload_timestamp') else None


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
            self.ax25_info = self._root.Beacon(io, self, self._root)


    class Bitmap16SubsystemStatus(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_payload_subsystem_status_bitmap = self._io.read_u2le()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"utf-8")


    class RfMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset_0 = [None] * (6)
            for i in range(6):
                self.offset_0[i] = self._io.read_u1()

            self.message = (self._io.read_bytes((self._parent.beacon_header.beacon_header_payload_size - 6))).decode(u"utf-8")
            self.rf_message_crc = self._io.read_u2le()


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


    class Beacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.is_valid_source
            if _on == True:
                self.beacon_header = self._root.BeaconHeader(self._io, self, self._root)
            if self.is_valid_payload:
                _on = self.beacon_header.beacon_header_api
                if _on == 14:
                    self.beacon_payload = self._root.HskpPayload(self._io, self, self._root)
                elif _on == 103:
                    self.beacon_payload = self._root.RfMessage(self._io, self, self._root)


        @property
        def is_valid_source(self):
            """This is work in progress as it never returns `true` without the
            `(1 == 1)` statement. It DOES NOT check the source for now!
            """
            if hasattr(self, '_m_is_valid_source'):
                return self._m_is_valid_source if hasattr(self, '_m_is_valid_source') else None

            self._m_is_valid_source =  ((1 == 1) or (self._root.ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign == u"DP0UWH")) 
            return self._m_is_valid_source if hasattr(self, '_m_is_valid_source') else None

        @property
        def is_valid_payload(self):
            if hasattr(self, '_m_is_valid_payload'):
                return self._m_is_valid_payload if hasattr(self, '_m_is_valid_payload') else None

            self._m_is_valid_payload =  (( ((self.beacon_header.beacon_header_fm_system_id == 2) and (self.beacon_header.beacon_header_fm_subsystem_id == 1) and (self.beacon_header.beacon_header_to_system_id == 1) and (self.beacon_header.beacon_header_to_subsystem_id == 0) and (self.beacon_header.beacon_header_payload_size == 46) and (self.beacon_header.beacon_header_api == 14)) ) or ( ((self.beacon_header.beacon_header_fm_system_id == 2) and (self.beacon_header.beacon_header_fm_subsystem_id == 1) and (self.beacon_header.beacon_header_to_system_id == 1) and (self.beacon_header.beacon_header_to_subsystem_id == 0) and (self.beacon_header.beacon_header_api == 103)) )) 
            return self._m_is_valid_payload if hasattr(self, '_m_is_valid_payload') else None


    class BeaconHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_header_flags1 = self._io.read_u1()
            self.beacon_header_flags2 = self._io.read_u1()
            self.beacon_header_packet_id = self._io.read_u2le()
            self.beacon_header_fm_system_id = self._io.read_u1()
            self.beacon_header_fm_subsystem_id = self._io.read_u1()
            self.beacon_header_to_system_id = self._io.read_u1()
            self.beacon_header_to_subsystem_id = self._io.read_u1()
            self.beacon_header_api = self._io.read_u1()
            self.beacon_header_payload_size = self._io.read_u1()


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



