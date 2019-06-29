# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Cubebel1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field hdr_rf_id: ax25_frame.payload.ax25_info.header.rf_id
    :field hdr_opr_time: ax25_frame.payload.ax25_info.header.opr_time
    :field hdr_reboot_cnt: ax25_frame.payload.ax25_info.header.reboot_cnt
    :field hdr_mcusr: ax25_frame.payload.ax25_info.header.mcusr
    :field hdr_pamp_temp: ax25_frame.payload.ax25_info.header.pamp_temp
    :field hdr_pamp_voltage: ax25_frame.payload.ax25_info.header.pamp_voltage
    :field hdr_tx_attenuator: ax25_frame.payload.ax25_info.header.tx_attenuator
    :field hdr_battery_voltage: ax25_frame.payload.ax25_info.header.battery_voltage
    :field hdr_system_voltage: ax25_frame.payload.ax25_info.header.system_voltage
    :field hdr_seq_number: ax25_frame.payload.ax25_info.header.seq_number
    :field hdr_pwr_save_state: ax25_frame.payload.ax25_info.header.pwr_save_state
    :field hdr_modem_on_period: ax25_frame.payload.ax25_info.header.modem_on_period
    :field hdr_obc_can_status: ax25_frame.payload.ax25_info.header.obc_can_status
    :field hdr_eps_can_status: ax25_frame.payload.ax25_info.header.eps_can_status
    :field hdr_info_size: ax25_frame.payload.ax25_info.header.info_size
    :field hdr_data_type: ax25_frame.payload.ax25_info.header.data_type
    :field fec_crc_status: ax25_frame.payload.ax25_info.data.fec_crc_status
    :field rx_msg_state: ax25_frame.payload.ax25_info.data.rx_msg_state
    :field rssi: ax25_frame.payload.ax25_info.data.rssi
    :field rf_msg: ax25_frame.payload.ax25_info.data.rf_msg
    :field current_to_gamma: ax25_frame.payload.ax25_info.data.current_to_gamma
    :field current_to_irsensor: ax25_frame.payload.ax25_info.data.current_to_irsensor
    :field current_to_extflash: ax25_frame.payload.ax25_info.data.current_to_extflash
    :field current_to_solarsens: ax25_frame.payload.ax25_info.data.current_to_solarsens
    :field current_to_magnetcoils: ax25_frame.payload.ax25_info.data.current_to_magnetcoils
    :field current_to_coil_x: ax25_frame.payload.ax25_info.data.current_to_coil_x
    :field current_to_coil_y: ax25_frame.payload.ax25_info.data.current_to_coil_y
    :field current_to_coil_pz: ax25_frame.payload.ax25_info.data.current_to_coil_pz
    :field current_to_coil_nz: ax25_frame.payload.ax25_info.data.current_to_coil_nz
    :field battery1_temp: ax25_frame.payload.ax25_info.data.battery1_temp
    :field battery2_temp: ax25_frame.payload.ax25_info.data.battery2_temp
    :field numb_oc_obc: ax25_frame.payload.ax25_info.data.numb_oc_obc
    :field numb_oc_out_gamma: ax25_frame.payload.ax25_info.data.numb_oc_out_gamma
    :field numb_oc_out_rf1: ax25_frame.payload.ax25_info.data.numb_oc_out_rf1
    :field numb_oc_out_rf2: ax25_frame.payload.ax25_info.data.numb_oc_out_rf2
    :field numb_oc_out_flash: ax25_frame.payload.ax25_info.data.numb_oc_out_flash
    :field numb_oc_out_irsens: ax25_frame.payload.ax25_info.data.numb_oc_out_irsens
    :field numb_oc_coil_x: ax25_frame.payload.ax25_info.data.numb_oc_coil_x
    :field numb_oc_coil_y: ax25_frame.payload.ax25_info.data.numb_oc_coil_y
    :field numb_oc_coil_pz: ax25_frame.payload.ax25_info.data.numb_oc_coil_pz
    :field numb_oc_coil_nz: ax25_frame.payload.ax25_info.data.numb_oc_coil_nz
    :field numb_oc_magnetcoils: ax25_frame.payload.ax25_info.data.numb_oc_magnetcoils
    :field numb_oc_solarsens: ax25_frame.payload.ax25_info.data.numb_oc_solarsens
    :field reset_num: ax25_frame.payload.ax25_info.data.reset_num
    :field reset_reason: ax25_frame.payload.ax25_info.data.reset_reason
    :field pwr_sat: ax25_frame.payload.ax25_info.data.pwr_sat
    :field pwr_rf1: ax25_frame.payload.ax25_info.data.pwr_rf1
    :field pwr_rf2: ax25_frame.payload.ax25_info.data.pwr_rf2
    :field pwr_sunsensor: ax25_frame.payload.ax25_info.data.pwr_sunsensor
    :field pwr_gamma: ax25_frame.payload.ax25_info.data.pwr_gamma
    :field pwr_irsensor: ax25_frame.payload.ax25_info.data.pwr_irsensor
    :field pwr_flash: ax25_frame.payload.ax25_info.data.pwr_flash
    :field pwr_magnet_x: ax25_frame.payload.ax25_info.data.pwr_magnet_x
    :field pwr_magnet_y: ax25_frame.payload.ax25_info.data.pwr_magnet_y
    :field pwr_magnet_z: ax25_frame.payload.ax25_info.data.pwr_magnet_z
    :field sys_time: ax25_frame.payload.ax25_info.data.sys_time
    :field adc_correctness: ax25_frame.payload.ax25_info.data.adc_correctness
    :field t_adc1: ax25_frame.payload.ax25_info.data.t_adc1
    :field t_adc2: ax25_frame.payload.ax25_info.data.t_adc2
    :field stepup_current: ax25_frame.payload.ax25_info.data.stepup_current
    :field stepup_voltage: ax25_frame.payload.ax25_info.data.stepup_voltage
    :field afterbq_current: ax25_frame.payload.ax25_info.data.afterbq_current
    :field battery_voltage: ax25_frame.payload.ax25_info.data.battery_voltage
    :field sys_voltage_50: ax25_frame.payload.ax25_info.data.sys_voltage_50
    :field sys_voltage_33: ax25_frame.payload.ax25_info.data.sys_voltage_33
    :field eps_uc_current: ax25_frame.payload.ax25_info.data.eps_uc_current
    :field obc_uc_current: ax25_frame.payload.ax25_info.data.obc_uc_current
    :field rf1_uc_current: ax25_frame.payload.ax25_info.data.rf1_uc_current
    :field rf2_uc_current: ax25_frame.payload.ax25_info.data.rf2_uc_current
    :field solar_voltage: ax25_frame.payload.ax25_info.data.solar_voltage
    :field side_x_current: ax25_frame.payload.ax25_info.data.side_x_current
    :field side_py_current: ax25_frame.payload.ax25_info.data.side_py_current
    :field side_ny_current: ax25_frame.payload.ax25_info.data.side_ny_current
    :field side_pz_current: ax25_frame.payload.ax25_info.data.side_pz_current
    :field side_nz_current: ax25_frame.payload.ax25_info.data.side_nz_current
    
    .. seealso::
       Source - https://bsusat.com/media/docs/2018/bsusat-1_data_struct.xlsx
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
            self.ax25_info = self._root.Frame(io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class RfMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rf_msg = (self._io.read_bytes((self._parent.header.info_size - 2))).decode(u"utf-8")


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


    class Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = self._root.Header(self._io, self, self._root)
            if self.header.info_size > 0:
                _on = self.header.data_type
                if _on == 1:
                    self.data = self._root.RfResponse(self._io, self, self._root)
                elif _on == 3:
                    self.data = self._root.RfMessage(self._io, self, self._root)
                elif _on == 254:
                    self.data = self._root.EpsFullTel(self._io, self, self._root)
                elif _on == 255:
                    self.data = self._root.EpsShortTel(self._io, self, self._root)



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


    class EpsShortTel(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bytes = []
            i = 0
            while not self._io.is_eof():
                self.bytes.append(self._io.read_u1())
                i += 1


        @property
        def eps_uc_current(self):
            """12 bits."""
            if hasattr(self, '_m_eps_uc_current'):
                return self._m_eps_uc_current if hasattr(self, '_m_eps_uc_current') else None

            self._m_eps_uc_current = (((self.bytes[14] | (self.bytes[15] << 8)) >> 2) & 4095)
            return self._m_eps_uc_current if hasattr(self, '_m_eps_uc_current') else None

        @property
        def side_py_current(self):
            """12 bits."""
            if hasattr(self, '_m_side_py_current'):
                return self._m_side_py_current if hasattr(self, '_m_side_py_current') else None

            self._m_side_py_current = ((((self.bytes[22] | (self.bytes[23] << 8)) | (self.bytes[24] << 16)) >> 6) & 4095)
            return self._m_side_py_current if hasattr(self, '_m_side_py_current') else None

        @property
        def t_adc1(self):
            """12 bits."""
            if hasattr(self, '_m_t_adc1'):
                return self._m_t_adc1 if hasattr(self, '_m_t_adc1') else None

            self._m_t_adc1 = (((self.bytes[2] | (self.bytes[3] << 8)) >> 2) & 4095)
            return self._m_t_adc1 if hasattr(self, '_m_t_adc1') else None

        @property
        def afterbq_current(self):
            """12 bits."""
            if hasattr(self, '_m_afterbq_current'):
                return self._m_afterbq_current if hasattr(self, '_m_afterbq_current') else None

            self._m_afterbq_current = (((self.bytes[8] | (self.bytes[9] << 8)) >> 2) & 4095)
            return self._m_afterbq_current if hasattr(self, '_m_afterbq_current') else None

        @property
        def battery_voltage(self):
            """12 bits."""
            if hasattr(self, '_m_battery_voltage'):
                return self._m_battery_voltage if hasattr(self, '_m_battery_voltage') else None

            self._m_battery_voltage = ((((self.bytes[9] | (self.bytes[10] << 8)) | (self.bytes[11] << 16)) >> 6) & 4095)
            return self._m_battery_voltage if hasattr(self, '_m_battery_voltage') else None

        @property
        def sys_voltage_50(self):
            """12 bits."""
            if hasattr(self, '_m_sys_voltage_50'):
                return self._m_sys_voltage_50 if hasattr(self, '_m_sys_voltage_50') else None

            self._m_sys_voltage_50 = (((self.bytes[11] | (self.bytes[12] << 8)) >> 2) & 4095)
            return self._m_sys_voltage_50 if hasattr(self, '_m_sys_voltage_50') else None

        @property
        def stepup_current(self):
            """12 bits."""
            if hasattr(self, '_m_stepup_current'):
                return self._m_stepup_current if hasattr(self, '_m_stepup_current') else None

            self._m_stepup_current = (((self.bytes[5] | (self.bytes[6] << 8)) >> 2) & 4095)
            return self._m_stepup_current if hasattr(self, '_m_stepup_current') else None

        @property
        def side_pz_current(self):
            """12 bits."""
            if hasattr(self, '_m_side_pz_current'):
                return self._m_side_pz_current if hasattr(self, '_m_side_pz_current') else None

            self._m_side_pz_current = ((((self.bytes[25] | (self.bytes[26] << 8)) | (self.bytes[27] << 16)) >> 6) & 4095)
            return self._m_side_pz_current if hasattr(self, '_m_side_pz_current') else None

        @property
        def sys_voltage_33(self):
            """12 bits."""
            if hasattr(self, '_m_sys_voltage_33'):
                return self._m_sys_voltage_33 if hasattr(self, '_m_sys_voltage_33') else None

            self._m_sys_voltage_33 = ((((self.bytes[12] | (self.bytes[13] << 8)) | (self.bytes[14] << 16)) >> 6) & 4095)
            return self._m_sys_voltage_33 if hasattr(self, '_m_sys_voltage_33') else None

        @property
        def rf2_uc_current(self):
            """12 bits."""
            if hasattr(self, '_m_rf2_uc_current'):
                return self._m_rf2_uc_current if hasattr(self, '_m_rf2_uc_current') else None

            self._m_rf2_uc_current = (((self.bytes[18] | (self.bytes[19] << 8)) >> 2) & 4095)
            return self._m_rf2_uc_current if hasattr(self, '_m_rf2_uc_current') else None

        @property
        def solar_voltage(self):
            """12 bits."""
            if hasattr(self, '_m_solar_voltage'):
                return self._m_solar_voltage if hasattr(self, '_m_solar_voltage') else None

            self._m_solar_voltage = ((((self.bytes[19] | (self.bytes[20] << 8)) | (self.bytes[21] << 16)) >> 6) & 4095)
            return self._m_solar_voltage if hasattr(self, '_m_solar_voltage') else None

        @property
        def side_x_current(self):
            """12 bits."""
            if hasattr(self, '_m_side_x_current'):
                return self._m_side_x_current if hasattr(self, '_m_side_x_current') else None

            self._m_side_x_current = (((self.bytes[21] | (self.bytes[22] << 8)) >> 2) & 4095)
            return self._m_side_x_current if hasattr(self, '_m_side_x_current') else None

        @property
        def obc_uc_current(self):
            """10 bits."""
            if hasattr(self, '_m_obc_uc_current'):
                return self._m_obc_uc_current if hasattr(self, '_m_obc_uc_current') else None

            self._m_obc_uc_current = ((self.bytes[15] | (self.bytes[16] << 8)) >> 6)
            return self._m_obc_uc_current if hasattr(self, '_m_obc_uc_current') else None

        @property
        def side_nz_current(self):
            """12 bits."""
            if hasattr(self, '_m_side_nz_current'):
                return self._m_side_nz_current if hasattr(self, '_m_side_nz_current') else None

            self._m_side_nz_current = (((self.bytes[27] | (self.bytes[28] << 8)) >> 2) & 4095)
            return self._m_side_nz_current if hasattr(self, '_m_side_nz_current') else None

        @property
        def adc_correctness(self):
            """2 bits."""
            if hasattr(self, '_m_adc_correctness'):
                return self._m_adc_correctness if hasattr(self, '_m_adc_correctness') else None

            self._m_adc_correctness = (self.bytes[2] & 3)
            return self._m_adc_correctness if hasattr(self, '_m_adc_correctness') else None

        @property
        def sys_time(self):
            """16 bits."""
            if hasattr(self, '_m_sys_time'):
                return self._m_sys_time if hasattr(self, '_m_sys_time') else None

            self._m_sys_time = (self.bytes[0] | (self.bytes[1] << 8))
            return self._m_sys_time if hasattr(self, '_m_sys_time') else None

        @property
        def stepup_voltage(self):
            """12 bits."""
            if hasattr(self, '_m_stepup_voltage'):
                return self._m_stepup_voltage if hasattr(self, '_m_stepup_voltage') else None

            self._m_stepup_voltage = ((((self.bytes[6] | (self.bytes[7] << 8)) | (self.bytes[8] << 16)) >> 6) & 4095)
            return self._m_stepup_voltage if hasattr(self, '_m_stepup_voltage') else None

        @property
        def side_ny_current(self):
            """12 bits."""
            if hasattr(self, '_m_side_ny_current'):
                return self._m_side_ny_current if hasattr(self, '_m_side_ny_current') else None

            self._m_side_ny_current = (((self.bytes[24] | (self.bytes[25] << 8)) >> 2) & 4095)
            return self._m_side_ny_current if hasattr(self, '_m_side_ny_current') else None

        @property
        def t_adc2(self):
            """12 bits."""
            if hasattr(self, '_m_t_adc2'):
                return self._m_t_adc2 if hasattr(self, '_m_t_adc2') else None

            self._m_t_adc2 = ((((self.bytes[3] | (self.bytes[4] << 8)) | (self.bytes[5] << 16)) >> 6) & 4095)
            return self._m_t_adc2 if hasattr(self, '_m_t_adc2') else None

        @property
        def rf1_uc_current(self):
            """10 bits."""
            if hasattr(self, '_m_rf1_uc_current'):
                return self._m_rf1_uc_current if hasattr(self, '_m_rf1_uc_current') else None

            self._m_rf1_uc_current = ((self.bytes[17] | (self.bytes[18] << 8)) & 1023)
            return self._m_rf1_uc_current if hasattr(self, '_m_rf1_uc_current') else None


    class RfResponse(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.status_bits = self._io.read_u1()
            self.rssi = self._io.read_u1()

        @property
        def fec_crc_status(self):
            if hasattr(self, '_m_fec_crc_status'):
                return self._m_fec_crc_status if hasattr(self, '_m_fec_crc_status') else None

            self._m_fec_crc_status = (self.status_bits & 1)
            return self._m_fec_crc_status if hasattr(self, '_m_fec_crc_status') else None

        @property
        def rx_msg_state(self):
            if hasattr(self, '_m_rx_msg_state'):
                return self._m_rx_msg_state if hasattr(self, '_m_rx_msg_state') else None

            self._m_rx_msg_state = (self.status_bits >> 1)
            return self._m_rx_msg_state if hasattr(self, '_m_rx_msg_state') else None


    class EpsFullTel(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bytes = []
            i = 0
            while not self._io.is_eof():
                self.bytes.append(self._io.read_u1())
                i += 1


        @property
        def eps_uc_current(self):
            """12 bits."""
            if hasattr(self, '_m_eps_uc_current'):
                return self._m_eps_uc_current if hasattr(self, '_m_eps_uc_current') else None

            self._m_eps_uc_current = (((self.bytes[14] | (self.bytes[15] << 8)) >> 2) & 4095)
            return self._m_eps_uc_current if hasattr(self, '_m_eps_uc_current') else None

        @property
        def pwr_sat(self):
            """1 bits."""
            if hasattr(self, '_m_pwr_sat'):
                return self._m_pwr_sat if hasattr(self, '_m_pwr_sat') else None

            self._m_pwr_sat = (self.bytes[61] & 1)
            return self._m_pwr_sat if hasattr(self, '_m_pwr_sat') else None

        @property
        def pwr_irsensor(self):
            """1 bits."""
            if hasattr(self, '_m_pwr_irsensor'):
                return self._m_pwr_irsensor if hasattr(self, '_m_pwr_irsensor') else None

            self._m_pwr_irsensor = ((self.bytes[61] >> 5) & 1)
            return self._m_pwr_irsensor if hasattr(self, '_m_pwr_irsensor') else None

        @property
        def numb_oc_coil_y(self):
            """8 bits."""
            if hasattr(self, '_m_numb_oc_coil_y'):
                return self._m_numb_oc_coil_y if hasattr(self, '_m_numb_oc_coil_y') else None

            self._m_numb_oc_coil_y = self.bytes[53]
            return self._m_numb_oc_coil_y if hasattr(self, '_m_numb_oc_coil_y') else None

        @property
        def side_py_current(self):
            """12 bits."""
            if hasattr(self, '_m_side_py_current'):
                return self._m_side_py_current if hasattr(self, '_m_side_py_current') else None

            self._m_side_py_current = ((((self.bytes[22] | (self.bytes[23] << 8)) | (self.bytes[24] << 16)) >> 6) & 4095)
            return self._m_side_py_current if hasattr(self, '_m_side_py_current') else None

        @property
        def current_to_solarsens(self):
            """12 bits."""
            if hasattr(self, '_m_current_to_solarsens'):
                return self._m_current_to_solarsens if hasattr(self, '_m_current_to_solarsens') else None

            self._m_current_to_solarsens = (((self.bytes[33] | (self.bytes[34] << 8)) >> 2) & 4095)
            return self._m_current_to_solarsens if hasattr(self, '_m_current_to_solarsens') else None

        @property
        def current_to_extflash(self):
            """12 bits."""
            if hasattr(self, '_m_current_to_extflash'):
                return self._m_current_to_extflash if hasattr(self, '_m_current_to_extflash') else None

            self._m_current_to_extflash = ((((self.bytes[31] | (self.bytes[32] << 8)) | (self.bytes[33] << 16)) >> 6) & 4095)
            return self._m_current_to_extflash if hasattr(self, '_m_current_to_extflash') else None

        @property
        def pwr_magnet_x(self):
            """1 bits."""
            if hasattr(self, '_m_pwr_magnet_x'):
                return self._m_pwr_magnet_x if hasattr(self, '_m_pwr_magnet_x') else None

            self._m_pwr_magnet_x = (self.bytes[61] >> 7)
            return self._m_pwr_magnet_x if hasattr(self, '_m_pwr_magnet_x') else None

        @property
        def numb_oc_solarsens(self):
            """8 bits."""
            if hasattr(self, '_m_numb_oc_solarsens'):
                return self._m_numb_oc_solarsens if hasattr(self, '_m_numb_oc_solarsens') else None

            self._m_numb_oc_solarsens = self.bytes[57]
            return self._m_numb_oc_solarsens if hasattr(self, '_m_numb_oc_solarsens') else None

        @property
        def t_adc1(self):
            """12 bits."""
            if hasattr(self, '_m_t_adc1'):
                return self._m_t_adc1 if hasattr(self, '_m_t_adc1') else None

            self._m_t_adc1 = (((self.bytes[2] | (self.bytes[3] << 8)) >> 2) & 4095)
            return self._m_t_adc1 if hasattr(self, '_m_t_adc1') else None

        @property
        def afterbq_current(self):
            """12 bits."""
            if hasattr(self, '_m_afterbq_current'):
                return self._m_afterbq_current if hasattr(self, '_m_afterbq_current') else None

            self._m_afterbq_current = (((self.bytes[8] | (self.bytes[9] << 8)) >> 2) & 4095)
            return self._m_afterbq_current if hasattr(self, '_m_afterbq_current') else None

        @property
        def pwr_sunsensor(self):
            """1 bits."""
            if hasattr(self, '_m_pwr_sunsensor'):
                return self._m_pwr_sunsensor if hasattr(self, '_m_pwr_sunsensor') else None

            self._m_pwr_sunsensor = ((self.bytes[61] >> 3) & 1)
            return self._m_pwr_sunsensor if hasattr(self, '_m_pwr_sunsensor') else None

        @property
        def numb_oc_obc(self):
            """8 bits."""
            if hasattr(self, '_m_numb_oc_obc'):
                return self._m_numb_oc_obc if hasattr(self, '_m_numb_oc_obc') else None

            self._m_numb_oc_obc = self.bytes[46]
            return self._m_numb_oc_obc if hasattr(self, '_m_numb_oc_obc') else None

        @property
        def current_to_coil_pz(self):
            """12 bits."""
            if hasattr(self, '_m_current_to_coil_pz'):
                return self._m_current_to_coil_pz if hasattr(self, '_m_current_to_coil_pz') else None

            self._m_current_to_coil_pz = (((self.bytes[39] | (self.bytes[40] << 8)) >> 2) & 4095)
            return self._m_current_to_coil_pz if hasattr(self, '_m_current_to_coil_pz') else None

        @property
        def battery_voltage(self):
            """12 bits."""
            if hasattr(self, '_m_battery_voltage'):
                return self._m_battery_voltage if hasattr(self, '_m_battery_voltage') else None

            self._m_battery_voltage = ((((self.bytes[9] | (self.bytes[10] << 8)) | (self.bytes[11] << 16)) >> 6) & 4095)
            return self._m_battery_voltage if hasattr(self, '_m_battery_voltage') else None

        @property
        def pwr_rf1(self):
            """1 bits."""
            if hasattr(self, '_m_pwr_rf1'):
                return self._m_pwr_rf1 if hasattr(self, '_m_pwr_rf1') else None

            self._m_pwr_rf1 = ((self.bytes[61] >> 1) & 1)
            return self._m_pwr_rf1 if hasattr(self, '_m_pwr_rf1') else None

        @property
        def sys_voltage_50(self):
            """12 bits."""
            if hasattr(self, '_m_sys_voltage_50'):
                return self._m_sys_voltage_50 if hasattr(self, '_m_sys_voltage_50') else None

            self._m_sys_voltage_50 = (((self.bytes[11] | (self.bytes[12] << 8)) >> 2) & 4095)
            return self._m_sys_voltage_50 if hasattr(self, '_m_sys_voltage_50') else None

        @property
        def numb_oc_magnetcoils(self):
            """8 bits."""
            if hasattr(self, '_m_numb_oc_magnetcoils'):
                return self._m_numb_oc_magnetcoils if hasattr(self, '_m_numb_oc_magnetcoils') else None

            self._m_numb_oc_magnetcoils = self.bytes[56]
            return self._m_numb_oc_magnetcoils if hasattr(self, '_m_numb_oc_magnetcoils') else None

        @property
        def pwr_magnet_z(self):
            """1 bits."""
            if hasattr(self, '_m_pwr_magnet_z'):
                return self._m_pwr_magnet_z if hasattr(self, '_m_pwr_magnet_z') else None

            self._m_pwr_magnet_z = ((self.bytes[62] >> 1) & 1)
            return self._m_pwr_magnet_z if hasattr(self, '_m_pwr_magnet_z') else None

        @property
        def stepup_current(self):
            """12 bits."""
            if hasattr(self, '_m_stepup_current'):
                return self._m_stepup_current if hasattr(self, '_m_stepup_current') else None

            self._m_stepup_current = (((self.bytes[5] | (self.bytes[6] << 8)) >> 2) & 4095)
            return self._m_stepup_current if hasattr(self, '_m_stepup_current') else None

        @property
        def side_pz_current(self):
            """12 bits."""
            if hasattr(self, '_m_side_pz_current'):
                return self._m_side_pz_current if hasattr(self, '_m_side_pz_current') else None

            self._m_side_pz_current = ((((self.bytes[25] | (self.bytes[26] << 8)) | (self.bytes[27] << 16)) >> 6) & 4095)
            return self._m_side_pz_current if hasattr(self, '_m_side_pz_current') else None

        @property
        def current_to_coil_y(self):
            """12 bits."""
            if hasattr(self, '_m_current_to_coil_y'):
                return self._m_current_to_coil_y if hasattr(self, '_m_current_to_coil_y') else None

            self._m_current_to_coil_y = ((((self.bytes[37] | (self.bytes[38] << 8)) | (self.bytes[39] << 16)) >> 6) & 4095)
            return self._m_current_to_coil_y if hasattr(self, '_m_current_to_coil_y') else None

        @property
        def numb_oc_out_irsens(self):
            """8 bits."""
            if hasattr(self, '_m_numb_oc_out_irsens'):
                return self._m_numb_oc_out_irsens if hasattr(self, '_m_numb_oc_out_irsens') else None

            self._m_numb_oc_out_irsens = self.bytes[51]
            return self._m_numb_oc_out_irsens if hasattr(self, '_m_numb_oc_out_irsens') else None

        @property
        def sys_voltage_33(self):
            """12 bits."""
            if hasattr(self, '_m_sys_voltage_33'):
                return self._m_sys_voltage_33 if hasattr(self, '_m_sys_voltage_33') else None

            self._m_sys_voltage_33 = ((((self.bytes[12] | (self.bytes[13] << 8)) | (self.bytes[14] << 16)) >> 6) & 4095)
            return self._m_sys_voltage_33 if hasattr(self, '_m_sys_voltage_33') else None

        @property
        def rf2_uc_current(self):
            """12 bits."""
            if hasattr(self, '_m_rf2_uc_current'):
                return self._m_rf2_uc_current if hasattr(self, '_m_rf2_uc_current') else None

            self._m_rf2_uc_current = (((self.bytes[18] | (self.bytes[19] << 8)) >> 2) & 4095)
            return self._m_rf2_uc_current if hasattr(self, '_m_rf2_uc_current') else None

        @property
        def battery2_temp(self):
            """12 bits."""
            if hasattr(self, '_m_battery2_temp'):
                return self._m_battery2_temp if hasattr(self, '_m_battery2_temp') else None

            self._m_battery2_temp = ((((self.bytes[43] | (self.bytes[44] << 8)) | (self.bytes[45] << 16)) >> 6) & 4095)
            return self._m_battery2_temp if hasattr(self, '_m_battery2_temp') else None

        @property
        def current_to_magnetcoils(self):
            """12 bits."""
            if hasattr(self, '_m_current_to_magnetcoils'):
                return self._m_current_to_magnetcoils if hasattr(self, '_m_current_to_magnetcoils') else None

            self._m_current_to_magnetcoils = ((((self.bytes[34] | (self.bytes[35] << 8)) | (self.bytes[36] << 16)) >> 6) & 4095)
            return self._m_current_to_magnetcoils if hasattr(self, '_m_current_to_magnetcoils') else None

        @property
        def current_to_coil_x(self):
            """12 bits."""
            if hasattr(self, '_m_current_to_coil_x'):
                return self._m_current_to_coil_x if hasattr(self, '_m_current_to_coil_x') else None

            self._m_current_to_coil_x = (((self.bytes[36] | (self.bytes[37] << 8)) >> 2) & 4095)
            return self._m_current_to_coil_x if hasattr(self, '_m_current_to_coil_x') else None

        @property
        def numb_oc_out_rf2(self):
            """8 bits."""
            if hasattr(self, '_m_numb_oc_out_rf2'):
                return self._m_numb_oc_out_rf2 if hasattr(self, '_m_numb_oc_out_rf2') else None

            self._m_numb_oc_out_rf2 = self.bytes[49]
            return self._m_numb_oc_out_rf2 if hasattr(self, '_m_numb_oc_out_rf2') else None

        @property
        def solar_voltage(self):
            """12 bits."""
            if hasattr(self, '_m_solar_voltage'):
                return self._m_solar_voltage if hasattr(self, '_m_solar_voltage') else None

            self._m_solar_voltage = ((((self.bytes[19] | (self.bytes[20] << 8)) | (self.bytes[21] << 16)) >> 6) & 4095)
            return self._m_solar_voltage if hasattr(self, '_m_solar_voltage') else None

        @property
        def numb_oc_out_flash(self):
            """8 bits."""
            if hasattr(self, '_m_numb_oc_out_flash'):
                return self._m_numb_oc_out_flash if hasattr(self, '_m_numb_oc_out_flash') else None

            self._m_numb_oc_out_flash = self.bytes[50]
            return self._m_numb_oc_out_flash if hasattr(self, '_m_numb_oc_out_flash') else None

        @property
        def numb_oc_coil_nz(self):
            """8 bits."""
            if hasattr(self, '_m_numb_oc_coil_nz'):
                return self._m_numb_oc_coil_nz if hasattr(self, '_m_numb_oc_coil_nz') else None

            self._m_numb_oc_coil_nz = self.bytes[55]
            return self._m_numb_oc_coil_nz if hasattr(self, '_m_numb_oc_coil_nz') else None

        @property
        def numb_oc_out_gamma(self):
            """8 bits."""
            if hasattr(self, '_m_numb_oc_out_gamma'):
                return self._m_numb_oc_out_gamma if hasattr(self, '_m_numb_oc_out_gamma') else None

            self._m_numb_oc_out_gamma = self.bytes[47]
            return self._m_numb_oc_out_gamma if hasattr(self, '_m_numb_oc_out_gamma') else None

        @property
        def side_x_current(self):
            """12 bits."""
            if hasattr(self, '_m_side_x_current'):
                return self._m_side_x_current if hasattr(self, '_m_side_x_current') else None

            self._m_side_x_current = (((self.bytes[21] | (self.bytes[22] << 8)) >> 2) & 4095)
            return self._m_side_x_current if hasattr(self, '_m_side_x_current') else None

        @property
        def obc_uc_current(self):
            """10 bits."""
            if hasattr(self, '_m_obc_uc_current'):
                return self._m_obc_uc_current if hasattr(self, '_m_obc_uc_current') else None

            self._m_obc_uc_current = ((self.bytes[15] | (self.bytes[16] << 8)) >> 6)
            return self._m_obc_uc_current if hasattr(self, '_m_obc_uc_current') else None

        @property
        def current_to_coil_nz(self):
            """12 bits."""
            if hasattr(self, '_m_current_to_coil_nz'):
                return self._m_current_to_coil_nz if hasattr(self, '_m_current_to_coil_nz') else None

            self._m_current_to_coil_nz = ((((self.bytes[40] | (self.bytes[41] << 8)) | (self.bytes[42] << 16)) >> 6) & 4095)
            return self._m_current_to_coil_nz if hasattr(self, '_m_current_to_coil_nz') else None

        @property
        def pwr_flash(self):
            """1 bits."""
            if hasattr(self, '_m_pwr_flash'):
                return self._m_pwr_flash if hasattr(self, '_m_pwr_flash') else None

            self._m_pwr_flash = ((self.bytes[61] >> 6) & 1)
            return self._m_pwr_flash if hasattr(self, '_m_pwr_flash') else None

        @property
        def battery1_temp(self):
            """12 bits."""
            if hasattr(self, '_m_battery1_temp'):
                return self._m_battery1_temp if hasattr(self, '_m_battery1_temp') else None

            self._m_battery1_temp = (((self.bytes[42] | (self.bytes[43] << 8)) >> 2) & 4095)
            return self._m_battery1_temp if hasattr(self, '_m_battery1_temp') else None

        @property
        def current_to_gamma(self):
            """12 bits."""
            if hasattr(self, '_m_current_to_gamma'):
                return self._m_current_to_gamma if hasattr(self, '_m_current_to_gamma') else None

            self._m_current_to_gamma = ((((self.bytes[28] | (self.bytes[29] << 8)) | (self.bytes[30] << 16)) >> 6) & 4095)
            return self._m_current_to_gamma if hasattr(self, '_m_current_to_gamma') else None

        @property
        def current_to_irsensor(self):
            """12 bits."""
            if hasattr(self, '_m_current_to_irsensor'):
                return self._m_current_to_irsensor if hasattr(self, '_m_current_to_irsensor') else None

            self._m_current_to_irsensor = (((self.bytes[30] | (self.bytes[31] << 8)) >> 2) & 4095)
            return self._m_current_to_irsensor if hasattr(self, '_m_current_to_irsensor') else None

        @property
        def side_nz_current(self):
            """12 bits."""
            if hasattr(self, '_m_side_nz_current'):
                return self._m_side_nz_current if hasattr(self, '_m_side_nz_current') else None

            self._m_side_nz_current = (((self.bytes[27] | (self.bytes[28] << 8)) >> 2) & 4095)
            return self._m_side_nz_current if hasattr(self, '_m_side_nz_current') else None

        @property
        def adc_correctness(self):
            """2 bits."""
            if hasattr(self, '_m_adc_correctness'):
                return self._m_adc_correctness if hasattr(self, '_m_adc_correctness') else None

            self._m_adc_correctness = (self.bytes[2] & 3)
            return self._m_adc_correctness if hasattr(self, '_m_adc_correctness') else None

        @property
        def reset_reason(self):
            """8 bits."""
            if hasattr(self, '_m_reset_reason'):
                return self._m_reset_reason if hasattr(self, '_m_reset_reason') else None

            self._m_reset_reason = self.bytes[60]
            return self._m_reset_reason if hasattr(self, '_m_reset_reason') else None

        @property
        def sys_time(self):
            """16 bits."""
            if hasattr(self, '_m_sys_time'):
                return self._m_sys_time if hasattr(self, '_m_sys_time') else None

            self._m_sys_time = (self.bytes[0] | (self.bytes[1] << 8))
            return self._m_sys_time if hasattr(self, '_m_sys_time') else None

        @property
        def pwr_rf2(self):
            """1 bits."""
            if hasattr(self, '_m_pwr_rf2'):
                return self._m_pwr_rf2 if hasattr(self, '_m_pwr_rf2') else None

            self._m_pwr_rf2 = ((self.bytes[61] >> 2) & 1)
            return self._m_pwr_rf2 if hasattr(self, '_m_pwr_rf2') else None

        @property
        def numb_oc_coil_pz(self):
            """8 bits."""
            if hasattr(self, '_m_numb_oc_coil_pz'):
                return self._m_numb_oc_coil_pz if hasattr(self, '_m_numb_oc_coil_pz') else None

            self._m_numb_oc_coil_pz = self.bytes[54]
            return self._m_numb_oc_coil_pz if hasattr(self, '_m_numb_oc_coil_pz') else None

        @property
        def stepup_voltage(self):
            """12 bits."""
            if hasattr(self, '_m_stepup_voltage'):
                return self._m_stepup_voltage if hasattr(self, '_m_stepup_voltage') else None

            self._m_stepup_voltage = ((((self.bytes[6] | (self.bytes[7] << 8)) | (self.bytes[8] << 16)) >> 6) & 4095)
            return self._m_stepup_voltage if hasattr(self, '_m_stepup_voltage') else None

        @property
        def side_ny_current(self):
            """12 bits."""
            if hasattr(self, '_m_side_ny_current'):
                return self._m_side_ny_current if hasattr(self, '_m_side_ny_current') else None

            self._m_side_ny_current = (((self.bytes[24] | (self.bytes[25] << 8)) >> 2) & 4095)
            return self._m_side_ny_current if hasattr(self, '_m_side_ny_current') else None

        @property
        def numb_oc_out_rf1(self):
            """8 bits."""
            if hasattr(self, '_m_numb_oc_out_rf1'):
                return self._m_numb_oc_out_rf1 if hasattr(self, '_m_numb_oc_out_rf1') else None

            self._m_numb_oc_out_rf1 = self.bytes[48]
            return self._m_numb_oc_out_rf1 if hasattr(self, '_m_numb_oc_out_rf1') else None

        @property
        def t_adc2(self):
            """12 bits."""
            if hasattr(self, '_m_t_adc2'):
                return self._m_t_adc2 if hasattr(self, '_m_t_adc2') else None

            self._m_t_adc2 = ((((self.bytes[3] | (self.bytes[4] << 8)) | (self.bytes[5] << 16)) >> 6) & 4095)
            return self._m_t_adc2 if hasattr(self, '_m_t_adc2') else None

        @property
        def rf1_uc_current(self):
            """10 bits."""
            if hasattr(self, '_m_rf1_uc_current'):
                return self._m_rf1_uc_current if hasattr(self, '_m_rf1_uc_current') else None

            self._m_rf1_uc_current = ((self.bytes[17] | (self.bytes[18] << 8)) & 1023)
            return self._m_rf1_uc_current if hasattr(self, '_m_rf1_uc_current') else None

        @property
        def pwr_gamma(self):
            """1 bits."""
            if hasattr(self, '_m_pwr_gamma'):
                return self._m_pwr_gamma if hasattr(self, '_m_pwr_gamma') else None

            self._m_pwr_gamma = ((self.bytes[61] >> 4) & 1)
            return self._m_pwr_gamma if hasattr(self, '_m_pwr_gamma') else None

        @property
        def numb_oc_coil_x(self):
            """8 bits."""
            if hasattr(self, '_m_numb_oc_coil_x'):
                return self._m_numb_oc_coil_x if hasattr(self, '_m_numb_oc_coil_x') else None

            self._m_numb_oc_coil_x = self.bytes[52]
            return self._m_numb_oc_coil_x if hasattr(self, '_m_numb_oc_coil_x') else None

        @property
        def reset_num(self):
            """16 bits."""
            if hasattr(self, '_m_reset_num'):
                return self._m_reset_num if hasattr(self, '_m_reset_num') else None

            self._m_reset_num = (self.bytes[58] | (self.bytes[59] << 8))
            return self._m_reset_num if hasattr(self, '_m_reset_num') else None

        @property
        def pwr_magnet_y(self):
            """1 bits."""
            if hasattr(self, '_m_pwr_magnet_y'):
                return self._m_pwr_magnet_y if hasattr(self, '_m_pwr_magnet_y') else None

            self._m_pwr_magnet_y = (self.bytes[62] & 1)
            return self._m_pwr_magnet_y if hasattr(self, '_m_pwr_magnet_y') else None


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rf_id = self._io.read_u1()
            self.opr_time = self._io.read_u2le()
            self.reboot_cnt = self._io.read_u1()
            self.mcusr = self._io.read_u1()
            self.pamp_temp = self._io.read_u2le()
            self.pamp_voltage = self._io.read_u1()
            self.tx_attenuator = self._io.read_u1()
            self.battery_voltage = self._io.read_u2le()
            self.system_voltage = self._io.read_u2le()
            self.seq_number = self._io.read_u2le()
            self.pwr_save_state = self._io.read_u1()
            self.modem_on_period = self._io.read_u2le()
            self.obc_can_status = self._io.read_u1()
            self.eps_can_status = self._io.read_u1()
            self.info_size = self._io.read_u1()
            self.data_type = self._io.read_u1()


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



