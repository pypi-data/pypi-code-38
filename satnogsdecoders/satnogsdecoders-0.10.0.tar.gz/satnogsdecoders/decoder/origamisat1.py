# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Origamisat1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field last_exec_obc_id: ax25_frame.payload.ax25_info.hk_data.chunk.last_exec_obc_id
    :field obc_cmd_status: ax25_frame.payload.ax25_info.hk_data.chunk.obc_cmd_status
    :field data_obtained_time_year: ax25_frame.payload.ax25_info.hk_data.chunk.data_obtained_time_year
    :field data_obtained_time_month: ax25_frame.payload.ax25_info.hk_data.chunk.data_obtained_time_month
    :field data_obtained_time_day: ax25_frame.payload.ax25_info.hk_data.chunk.data_obtained_time_day
    :field data_obtained_time_hour: ax25_frame.payload.ax25_info.hk_data.chunk.data_obtained_time_hour
    :field data_obtained_time_minute: ax25_frame.payload.ax25_info.hk_data.chunk.data_obtained_time_minute
    :field data_obtained_time_second: ax25_frame.payload.ax25_info.hk_data.chunk.data_obtained_time_second
    :field battery_voltage: ax25_frame.payload.ax25_info.hk_data.chunk.battery_voltage
    :field battery_current: ax25_frame.payload.ax25_info.hk_data.chunk.battery_current
    :field bat_status: ax25_frame.payload.ax25_info.hk_data.chunk.bat_status
    :field eps_sw_status: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_status
    :field eps_bus_status: ax25_frame.payload.ax25_info.hk_data.chunk.eps_bus_status
    :field satellite_mode: ax25_frame.payload.ax25_info.hk_data.chunk.satellite_mode
    :field sap_voltage: ax25_frame.payload.ax25_info.hk_data.chunk.sap_voltage
    :field sap_current: ax25_frame.payload.ax25_info.hk_data.chunk.sap_current
    :field sap_1_gen_pwr: ax25_frame.payload.ax25_info.hk_data.chunk.sap_1_gen_pwr
    :field sap_2_gen_pwr: ax25_frame.payload.ax25_info.hk_data.chunk.sap_2_gen_pwr
    :field sap_3_gen_pwr: ax25_frame.payload.ax25_info.hk_data.chunk.sap_3_gen_pwr
    :field sap_4_gen_pwr: ax25_frame.payload.ax25_info.hk_data.chunk.sap_4_gen_pwr
    :field sap_5_gen_pwr: ax25_frame.payload.ax25_info.hk_data.chunk.sap_5_gen_pwr
    :field sap_2_current: ax25_frame.payload.ax25_info.hk_data.chunk.sap_2_current
    :field sap_3_current: ax25_frame.payload.ax25_info.hk_data.chunk.sap_3_current
    :field sap_4_current: ax25_frame.payload.ax25_info.hk_data.chunk.sap_4_current
    :field sap_5_current: ax25_frame.payload.ax25_info.hk_data.chunk.sap_5_current
    :field eps_temp: ax25_frame.payload.ax25_info.hk_data.chunk.eps_temp
    :field obc_cmd_status: ax25_frame.payload.ax25_info.hk_data.chunk.
    :field obc_temp_0: ax25_frame.payload.ax25_info.hk_data.chunk.obc_temp_0
    :field obc_temp_1: ax25_frame.payload.ax25_info.hk_data.chunk.obc_temp_1
    :field amp_5g8hz_temp: ax25_frame.payload.ax25_info.hk_data.chunk.amp_5g8hz_temp
    :field rad_plate_5g8hz_temp: ax25_frame.payload.ax25_info.hk_data.chunk.rad_plate_5g8hz_temp
    :field tx_temp: ax25_frame.payload.ax25_info.hk_data.chunk.tx_temp
    :field rx_temp: ax25_frame.payload.ax25_info.hk_data.chunk.rx_temp
    :field bat_mbrd_temp: ax25_frame.payload.ax25_info.hk_data.chunk.bat_mbrd_temp
    :field ci_brd_temp: ax25_frame.payload.ax25_info.hk_data.chunk.ci_brd_temp
    :field panel_pos_y: ax25_frame.payload.ax25_info.hk_data.chunk.panel_pos_y
    :field panel_pos_x: ax25_frame.payload.ax25_info.hk_data.chunk.panel_pos_x
    :field panel_neg_x: ax25_frame.payload.ax25_info.hk_data.chunk.panel_neg_x
    :field obc_gpu_temp: ax25_frame.payload.ax25_info.hk_data.chunk.obc_gpu_temp
    :field panel_neg_y: ax25_frame.payload.ax25_info.hk_data.chunk.panel_neg_y
    :field accel_x: ax25_frame.payload.ax25_info.hk_data.chunk.accel_x
    :field accel_y: ax25_frame.payload.ax25_info.hk_data.chunk.accel_y
    :field accel_z: ax25_frame.payload.ax25_info.hk_data.chunk.accel_z
    :field ang_vcty_x: ax25_frame.payload.ax25_info.hk_data.chunk.ang_vcty_x
    :field ang_vcty_z: ax25_frame.payload.ax25_info.hk_data.chunk.ang_vcty_z
    :field raspi_last_exec: ax25_frame.payload.ax25_info.hk_data.chunk.raspi_last_exec
    :field raspi_mode: ax25_frame.payload.ax25_info.hk_data.chunk.raspi_mode
    :field eps_sw_1_volt: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_1_volt
    :field eps_sw_1_curr: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_1_curr
    :field eps_sw_2_volt: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_2_volt
    :field eps_sw_2_curr: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_2_curr
    :field eps_sw_5_volt: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_5_volt
    :field eps_sw_5_curr: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_5_curr
    :field eps_sw_6_volt: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_6_volt
    :field eps_sw_6_curr: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_6_curr
    :field eps_sw_7_volt: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_7_volt
    :field eps_sw_7_curr: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_7_curr
    :field eps_sw_8_volt: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_8_volt
    :field eps_sw_8_curr: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_8_curr
    :field eps_sw_9_volt: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_9_volt
    :field eps_sw_10_volt: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_10_volt
    :field eps_sw_10_curr: ax25_frame.payload.ax25_info.hk_data.chunk.eps_sw_10_curr
    :field eps_3v3_voltage: ax25_frame.payload.ax25_info.hk_data.chunk.eps_3v3_voltage
    :field eps_3v3_current: ax25_frame.payload.ax25_info.hk_data.chunk.eps_3v3_current
    :field eps_5v_voltage: ax25_frame.payload.ax25_info.hk_data.chunk.eps_5v_voltage
    :field eps_5v_current: ax25_frame.payload.ax25_info.hk_data.chunk.eps_5v_current
    :field eps_12v_voltage: ax25_frame.payload.ax25_info.hk_data.chunk.eps_12v_voltage
    :field eps_12v_current: ax25_frame.payload.ax25_info.hk_data.chunk.eps_12v_current
    :field bcr_1_voltage: ax25_frame.payload.ax25_info.hk_data.chunk.bcr_1_voltage
    :field bcr_2_voltage: ax25_frame.payload.ax25_info.hk_data.chunk.bcr_2_voltage
    :field bcr_3_voltage: ax25_frame.payload.ax25_info.hk_data.chunk.bcr_3_voltage
    :field pwr5g8hz_12v_voltage: ax25_frame.payload.ax25_info.hk_data.chunk.pwr5g8hz_12v_voltage
    
    Attention: `rpt_callsign` cannot be accessed because `rpt_instance` is an
    array of unknown size at the beginning of the parsing process! Left an
    example in here.
    
    .. seealso::
       'http://www.origami.titech.ac.jp/wp/wp-content/uploads/2019/01/OP-S1-0115_FMDownLinkDataFormat_20190118.pdf'
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = self._root.Ax25Frame(self._io, self, self._root)

    class HkDataChunk3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ang_vcty_y_b1 = self._io.read_u1()
            self.ang_vcty_z = self._io.read_u2be()
            self.raspi_last_exec = self._io.read_u1()
            self.raspi_mode = self._io.read_u1()
            self.eps_sw_1_volt = self._io.read_u2be()
            self.eps_sw_1_curr = self._io.read_u2be()
            self.eps_sw_2_volt = self._io.read_u2be()
            self.eps_sw_2_curr = self._io.read_u2be()
            self.eps_sw_5_volt = self._io.read_u2be()
            self.eps_sw_5_curr = self._io.read_u2be()
            self.eps_sw_6_volt = self._io.read_u2be()
            self.eps_sw_6_curr = self._io.read_u2be()
            self.eps_sw_7_volt = self._io.read_u2be()
            self.eps_sw_7_curr = self._io.read_u2be()
            self.eps_sw_8_volt = self._io.read_u2be()
            self.eps_sw_8_curr = self._io.read_u2be()
            self.eps_sw_9_volt = self._io.read_u2be()
            self.eps_sw_9_curr_b0 = self._io.read_u1()


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


    class HkDataChunk1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.last_exec_obc_id = self._io.read_u1()
            self.obc_cmd_status = self._io.read_u1()
            self.data_obtained_time_year = self._io.read_u1()
            self.data_obtained_time_month = self._io.read_u1()
            self.data_obtained_time_day = self._io.read_u1()
            self.data_obtained_time_hour = self._io.read_u1()
            self.data_obtained_time_minute = self._io.read_u1()
            self.data_obtained_time_second = self._io.read_u1()
            self.battery_voltage = self._io.read_u2be()
            self.battery_current = self._io.read_u2be()
            self.bat_status = self._io.read_u1()
            self.eps_sw_status = self._io.read_u2be()
            self.eps_bus_status = self._io.read_u1()
            self.satellite_mode = self._io.read_u1()
            self.sap_voltage = self._io.read_u2be()
            self.sap_current = self._io.read_u2be()
            self.sap_1_gen_pwr = self._io.read_u2be()
            self.sap_2_gen_pwr = self._io.read_u2be()
            self.sap_3_gen_pwr = self._io.read_u2be()
            self.sap_4_gen_pwr = self._io.read_u2be()
            self.sap_5_gen_pwr = self._io.read_u2be()
            self.sap_1_current_b0 = self._io.read_u1()


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
            _on = self._io.size()
            if _on == 48:
                self.ax25_info = self._root.EchoBack(self._io, self, self._root)
            elif _on == 51:
                self.ax25_info = self._root.HkOrMissionData(self._io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class HkDataChunk4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eps_sw_9_curr_b1 = self._io.read_u1()
            self.eps_sw_10_volt = self._io.read_u2be()
            self.eps_sw_10_curr = self._io.read_u2be()
            self.eps_3v3_voltage = self._io.read_u2be()
            self.eps_3v3_current = self._io.read_u2be()
            self.eps_5v_voltage = self._io.read_u2be()
            self.eps_5v_current = self._io.read_u2be()
            self.eps_12v_voltage = self._io.read_u2be()
            self.eps_12v_current = self._io.read_u2be()
            self.bcr_1_voltage = self._io.read_u2be()
            self.bcr_2_voltage = self._io.read_u2be()
            self.bcr_3_voltage = self._io.read_u2be()
            self.sap_5_current = self._io.read_u2be()
            self.pwr5g8hz_12v_voltage = self._io.read_u1()


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


    class HkOrMissionData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pkt_num = [None] * (3)
            for i in range(3):
                self.pkt_num[i] = self._io.read_u1()

            if  ((self.pkt_num[0] == self.pkt_num[1]) and (self.pkt_num[1] == self.pkt_num[2])) :
                self.hk_data = self._root.HkData(self._io, self, self._root)

            if self.pkt_num[0] != self.pkt_num[1]:
                self._raw_mission_data = self._io.read_bytes(32)
                io = KaitaiStream(BytesIO(self._raw_mission_data))
                self.mission_data = self._root.MissionData(io, self, self._root)


        @property
        def packet_number(self):
            if hasattr(self, '_m_packet_number'):
                return self._m_packet_number if hasattr(self, '_m_packet_number') else None

            self._m_packet_number = ((self.pkt_num[0] | self.pkt_num[1]) | self.pkt_num[2])
            return self._m_packet_number if hasattr(self, '_m_packet_number') else None


    class HkData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = (self._parent.packet_number % 4)
            if _on == 0:
                self._raw_chunk = self._io.read_bytes_full()
                io = KaitaiStream(BytesIO(self._raw_chunk))
                self.chunk = self._root.HkDataChunk4(io, self, self._root)
            elif _on == 1:
                self._raw_chunk = self._io.read_bytes_full()
                io = KaitaiStream(BytesIO(self._raw_chunk))
                self.chunk = self._root.HkDataChunk1(io, self, self._root)
            elif _on == 3:
                self._raw_chunk = self._io.read_bytes_full()
                io = KaitaiStream(BytesIO(self._raw_chunk))
                self.chunk = self._root.HkDataChunk3(io, self, self._root)
            elif _on == 2:
                self._raw_chunk = self._io.read_bytes_full()
                io = KaitaiStream(BytesIO(self._raw_chunk))
                self.chunk = self._root.HkDataChunk2(io, self, self._root)
            else:
                self.chunk = self._io.read_bytes_full()


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


    class HkDataChunk2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sap_1_current_b1 = self._io.read_u1()
            self.sap_2_current = self._io.read_u2be()
            self.sap_3_current = self._io.read_u2be()
            self.sap_4_current = self._io.read_u2be()
            self.eps_temp = self._io.read_u2be()
            self.obc_temp_0 = self._io.read_u1()
            self.obc_temp_1 = self._io.read_u1()
            self.amp_5g8hz_temp = self._io.read_u1()
            self.rad_plate_5g8hz_temp = self._io.read_u1()
            self.tx_temp = self._io.read_u1()
            self.rx_temp = self._io.read_u1()
            self.bat_mbrd_temp = self._io.read_u2be()
            self.ci_brd_temp = self._io.read_u1()
            self.panel_pos_y = self._io.read_u1()
            self.panel_pos_x = self._io.read_u1()
            self.panel_neg_x = self._io.read_u1()
            self.obc_gpu_temp = self._io.read_u1()
            self.panel_neg_y = self._io.read_u1()
            self.accel_x = self._io.read_u2be()
            self.accel_y = self._io.read_u2be()
            self.accel_z = self._io.read_u2be()
            self.ang_vcty_x = self._io.read_u2be()
            self.ang_vcty_y_b0 = self._io.read_u1()


    class EchoBack(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.response_data = self._io.read_bytes(32)


    class MissionData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes_full()



