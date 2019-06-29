# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Skcube(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field packet_type: ax25_frame.payload.ax25_info.packet_type
    :field adcs_mode: ax25_frame.payload.ax25_info.telemetry.adcs_mode
    :field bd_k: ax25_frame.payload.ax25_info.telemetry.bd_k
    :field max_pwm_coil_x: ax25_frame.payload.ax25_info.telemetry.max_pwm_coil_x
    :field max_pwm_coil_y: ax25_frame.payload.ax25_info.telemetry.max_pwm_coil_y
    :field max_pwm_coil_z: ax25_frame.payload.ax25_info.telemetry.max_pwm_coil_z
    :field sun_x_p_x: ax25_frame.payload.ax25_info.telemetry.sun_x_p_x
    :field sun_x_p_y: ax25_frame.payload.ax25_info.telemetry.sun_x_p_y
    :field sun_x_p_irradiation: ax25_frame.payload.ax25_info.telemetry.sun_x_p_irradiation
    :field sun_x_m_x: ax25_frame.payload.ax25_info.telemetry.sun_x_m_x
    :field sun_x_m_y: ax25_frame.payload.ax25_info.telemetry.sun_x_m_y
    :field sun_x_m_irradiation: ax25_frame.payload.ax25_info.telemetry.sun_x_m_irradiation
    :field sun_y_p_x: ax25_frame.payload.ax25_info.telemetry.sun_y_p_x
    :field sun_y_p_y: ax25_frame.payload.ax25_info.telemetry.sun_y_p_y
    :field sun_y_p_irradiation: ax25_frame.payload.ax25_info.telemetry.sun_y_p_irradiation
    :field sun_y_m_x: ax25_frame.payload.ax25_info.telemetry.sun_y_m_x
    :field sun_y_m_y: ax25_frame.payload.ax25_info.telemetry.sun_y_m_y
    :field sun_y_m_irradiation: ax25_frame.payload.ax25_info.telemetry.sun_y_m_irradiation
    :field sun_z_p_x: ax25_frame.payload.ax25_info.telemetry.sun_z_p_x
    :field sun_z_p_y: ax25_frame.payload.ax25_info.telemetry.sun_z_p_y
    :field sun_z_p_irradiation: ax25_frame.payload.ax25_info.telemetry.sun_z_p_irradiation
    :field sun_z_m_x: ax25_frame.payload.ax25_info.telemetry.sun_z_m_x
    :field sun_z_m_y: ax25_frame.payload.ax25_info.telemetry.sun_z_m_y
    :field sun_z_m_irradiation: ax25_frame.payload.ax25_info.telemetry.sun_z_m_irradiation
    :field gyroscopex: ax25_frame.payload.ax25_info.telemetry.gyroscopex
    :field gyroscopey: ax25_frame.payload.ax25_info.telemetry.gyroscopey
    :field gyroscopez: ax25_frame.payload.ax25_info.telemetry.gyroscopez
    :field gyroscope_temp: ax25_frame.payload.ax25_info.telemetry.gyroscope_temp
    :field magnetometer_1_x: ax25_frame.payload.ax25_info.telemetry.magnetometer_1_x
    :field magnetometer_1_y: ax25_frame.payload.ax25_info.telemetry.magnetometer_1_y
    :field magnetometer_1_z: ax25_frame.payload.ax25_info.telemetry.magnetometer_1_z
    :field magnetometer_1_temp: ax25_frame.payload.ax25_info.telemetry.magnetometer_1_temp
    :field magnetometer_2_x: ax25_frame.payload.ax25_info.telemetry.magnetometer_2_x
    :field magnetometer_2_y: ax25_frame.payload.ax25_info.telemetry.magnetometer_2_y
    :field magnetometer_2_z: ax25_frame.payload.ax25_info.telemetry.magnetometer_2_z
    :field magnetometer_2_temp: ax25_frame.payload.ax25_info.telemetry.magnetometer_2_temp
    :field accelerometer_x: ax25_frame.payload.ax25_info.telemetry.accelerometer_x
    :field accelerometer_y: ax25_frame.payload.ax25_info.telemetry.accelerometer_y
    :field accelerometer_z: ax25_frame.payload.ax25_info.telemetry.accelerometer_z
    :field accel_temp: ax25_frame.payload.ax25_info.telemetry.accel_temp
    :field earth_sensor_x_m: ax25_frame.payload.ax25_info.telemetry.earth_sensor_x_m
    :field earth_sensor_x_p: ax25_frame.payload.ax25_info.telemetry.earth_sensor_x_p
    :field earth_sensor_y_m: ax25_frame.payload.ax25_info.telemetry.earth_sensor_y_m
    :field earth_sensor_y_p: ax25_frame.payload.ax25_info.telemetry.earth_sensor_y_p
    :field timestamp: ax25_frame.payload.ax25_info.telemetry.timestamp
    :field fwversion: ax25_frame.payload.ax25_info.telemetry.fwversion
    :field activecom: ax25_frame.payload.ax25_info.telemetry.activecom
    :field digipeatermode: ax25_frame.payload.ax25_info.telemetry.digipeatermode
    :field noofreboots: ax25_frame.payload.ax25_info.telemetry.noofreboots
    :field outputreflpower: ax25_frame.payload.ax25_info.telemetry.outputreflpower
    :field outputforwardpower: ax25_frame.payload.ax25_info.telemetry.outputforwardpower
    :field outputreflpowercw: ax25_frame.payload.ax25_info.telemetry.outputreflpowercw
    :field outputforwardpowercw: ax25_frame.payload.ax25_info.telemetry.outputforwardpowercw
    :field rssi: ax25_frame.payload.ax25_info.telemetry.rssi
    :field rssinoise: ax25_frame.payload.ax25_info.telemetry.rssinoise
    :field mcutemperature: ax25_frame.payload.ax25_info.telemetry.mcutemperature
    :field patemperature: ax25_frame.payload.ax25_info.telemetry.patemperature
    :field cwbeaconsent: ax25_frame.payload.ax25_info.telemetry.cwbeaconsent
    :field packetsent: ax25_frame.payload.ax25_info.telemetry.packetsent
    :field correctpacketsreceived: ax25_frame.payload.ax25_info.telemetry.correctpacketsreceived
    :field brokenpacketsreceived: ax25_frame.payload.ax25_info.telemetry.brokenpacketsreceived
    :field comprotocolerror: ax25_frame.payload.ax25_info.telemetry.comprotocolerror
    :field gsprotocolerror: ax25_frame.payload.ax25_info.telemetry.gsprotocolerror
    :field txdisablestatus: ax25_frame.payload.ax25_info.telemetry.txdisablestatus
    :field orbittime: ax25_frame.payload.ax25_info.telemetry.orbittime
    :field timeslotstart: ax25_frame.payload.ax25_info.telemetry.timeslotstart
    :field timeslotend: ax25_frame.payload.ax25_info.telemetry.timeslotend
    :field fw_version: ax25_frame.payload.ax25_info.telemetry.fw_version
    :field number_of_reboots: ax25_frame.payload.ax25_info.telemetry.number_of_reboots
    :field jpeg_compression: ax25_frame.payload.ax25_info.telemetry.jpeg_compression
    :field jpeg_scale: ax25_frame.payload.ax25_info.telemetry.jpeg_scale
    :field mcu_temperature: ax25_frame.payload.ax25_info.telemetry.mcu_temperature
    :field vref_internal: ax25_frame.payload.ax25_info.telemetry.vref_internal
    :field packets_sent: ax25_frame.payload.ax25_info.telemetry.packets_sent
    :field cw_sent: ax25_frame.payload.ax25_info.telemetry.cw_sent
    :field flash_image_position: ax25_frame.payload.ax25_info.telemetry.flash_image_position
    :field tx_datarate: ax25_frame.payload.ax25_info.telemetry.tx_datarate
    :field fulluptime: ax25_frame.payload.ax25_info.telemetry.fulluptime
    :field uptime: ax25_frame.payload.ax25_info.telemetry.uptime
    :field active_procesor: ax25_frame.payload.ax25_info.telemetry.active_procesor
    :field countcomerrors: ax25_frame.payload.ax25_info.telemetry.countcomerrors
    :field countpsuerrors: ax25_frame.payload.ax25_info.telemetry.countpsuerrors
    :field solar_j_current: ax25_frame.payload.ax25_info.telemetry.solar_j_current
    :field solar_k_current: ax25_frame.payload.ax25_info.telemetry.solar_k_current
    :field solar_l_current: ax25_frame.payload.ax25_info.telemetry.solar_l_current
    :field solar_m_current: ax25_frame.payload.ax25_info.telemetry.solar_m_current
    :field solar_u_current: ax25_frame.payload.ax25_info.telemetry.solar_u_current
    :field solar_d_current: ax25_frame.payload.ax25_info.telemetry.solar_d_current
    :field solar_j_temp: ax25_frame.payload.ax25_info.telemetry.solar_j_temp
    :field solar_k_temp: ax25_frame.payload.ax25_info.telemetry.solar_k_temp
    :field solar_l_temp: ax25_frame.payload.ax25_info.telemetry.solar_l_temp
    :field solar_m_temp: ax25_frame.payload.ax25_info.telemetry.solar_m_temp
    :field solar_u_temp: ax25_frame.payload.ax25_info.telemetry.solar_u_temp
    :field solar_d_temp: ax25_frame.payload.ax25_info.telemetry.solar_d_temp
    :field battery_a_voltage: ax25_frame.payload.ax25_info.telemetry.battery_a_voltage
    :field battery_b_voltage: ax25_frame.payload.ax25_info.telemetry.battery_b_voltage
    :field battery_temp: ax25_frame.payload.ax25_info.telemetry.battery_temp
    :field battery_a_capacity: ax25_frame.payload.ax25_info.telemetry.battery_b_capacity
    :field bat_capacity: ax25_frame.payload.ax25_info.telemetry.bat_capacity
    :field battery_a_current: ax25_frame.payload.ax25_info.telemetry.battery_a_current
    :field battery_b_current: ax25_frame.payload.ax25_info.telemetry.battery_b_current
    :field battery_a_min_current: ax25_frame.payload.ax25_info.telemetry.battery_a_min_current
    :field battery_b_min_current: ax25_frame.payload.ax25_info.telemetry.battery_b_min_current
    :field battery_a_max_current: ax25_frame.payload.ax25_info.telemetry.battery_a_max_current
    :field battery_b_max_current: ax25_frame.payload.ax25_info.telemetry.battery_b_max_current
    :field battery_a_avg_current: ax25_frame.payload.ax25_info.telemetry.battery_a_avg_current
    :field battery_b_avg_current: ax25_frame.payload.ax25_info.telemetry.battery_b_avg_current
    :field chds_min_current: ax25_frame.payload.ax25_info.telemetry.chds_min_current
    :field chds_max_current: ax25_frame.payload.ax25_info.telemetry.chds_max_current
    :field chds_avg_current: ax25_frame.payload.ax25_info.telemetry.chds_avg_current
    :field chds_actual_current: ax25_frame.payload.ax25_info.telemetry.chds_actual_current
    :field cam_min_current: ax25_frame.payload.ax25_info.telemetry.cam_min_current
    :field cam_max_current: ax25_frame.payload.ax25_info.telemetry.cam_max_current
    :field cam_avg_current: ax25_frame.payload.ax25_info.telemetry.cam_avg_current
    :field cam_actual_current: ax25_frame.payload.ax25_info.telemetry.cam_actual_current
    :field exp_min_current: ax25_frame.payload.ax25_info.telemetry.exp_min_current
    :field exp_max_current: ax25_frame.payload.ax25_info.telemetry.exp_max_current
    :field exp_avg_current: ax25_frame.payload.ax25_info.telemetry.exp_avg_current
    :field exp_actual_current: ax25_frame.payload.ax25_info.telemetry.exp_actual_current
    :field adcs_min_current: ax25_frame.payload.ax25_info.telemetry.adcs_min_current
    :field adcs_max_current: ax25_frame.payload.ax25_info.telemetry.adcs_max_current
    :field adcs_avg_current: ax25_frame.payload.ax25_info.telemetry.adcs_avg_current
    :field adcs_actual_current: ax25_frame.payload.ax25_info.telemetry.adcs_actual_current
    :field sys_voltage_min: ax25_frame.payload.ax25_info.telemetry.sys_voltage_min
    :field sys_voltage_max: ax25_frame.payload.ax25_info.telemetry.sys_voltage_max
    :field sys_voltage_actual: ax25_frame.payload.ax25_info.telemetry.sys_voltage_actual
    :field nadprudy: ax25_frame.payload.ax25_info.telemetry.nadprudy
    :field stav_pripojenia: ax25_frame.payload.ax25_info.telemetry.stav_pripojenia
    :field ts_temp: ax25_frame.payload.ax25_info.telemetry.ts_temp
    :field countpacket: ax25_frame.payload.ax25_info.telemetry.countpacket
    :field psu_error: ax25_frame.payload.ax25_info.telemetry.psu_error
    :field psu_lasterror: ax25_frame.payload.ax25_info.telemetry.psu_lasterror
    :field com_error: ax25_frame.payload.ax25_info.telemetry.com_error
    :field com_lasterror: ax25_frame.payload.ax25_info.telemetry.com_lasterror
    :field cdhs_i_limit: ax25_frame.payload.ax25_info.telemetry.cdhs_i_limit
    :field com_i_limit: ax25_frame.payload.ax25_info.telemetry.com_i_limit
    :field cam_i_limit: ax25_frame.payload.ax25_info.telemetry.cam_i_limit
    :field adcs_i_limit: ax25_frame.payload.ax25_info.telemetry.adcs_i_limit
    :field exp_i_limit: ax25_frame.payload.ax25_info.telemetry.exp_i_limit
    :field cam_uv_limit: ax25_frame.payload.ax25_info.telemetry.cam_uv_limit
    :field adcs_uv_limit: ax25_frame.payload.ax25_info.telemetry.adcs_uv_limit
    :field bat1_vmax: ax25_frame.payload.ax25_info.telemetry.bat1_vmax
    :field bat1_vmin: ax25_frame.payload.ax25_info.telemetry.bat1_vmin
    :field bat2_vmax: ax25_frame.payload.ax25_info.telemetry.bat2_vmax
    :field bat2_vmin: ax25_frame.payload.ax25_info.telemetry.bat2_vmin
    :field endofdata: ax25_frame.payload.ax25_info.telemetry.endofdata
    :field active_adc_channel: ax25_frame.payload.ax25_info.telemetry.active_adc_channel
    :field fft_gain: ax25_frame.payload.ax25_info.telemetry.fft_gain
    :field low_frequency: ax25_frame.payload.ax25_info.telemetry.low_frequency
    :field high_frequency: ax25_frame.payload.ax25_info.telemetry.high_frequency
    :field max_hold_sec: ax25_frame.payload.ax25_info.telemetry.max_hold_sec
    :field slow_position: ax25_frame.payload.ax25_info.telemetry.slow_position
    :field postring_samples: ax25_frame.payload.ax25_info.telemetry.postring_samples
    :field psd: ax25_frame.payload.ax25_info.telemetry.psd
    :field psd_max: ax25_frame.payload.ax25_info.telemetry.psd_max
    :field psd_selected: ax25_frame.payload.ax25_info.telemetry.psd_selected
    :field psd_selected_max: ax25_frame.payload.ax25_info.telemetry.psd_selected_max
    :field peak_freq: ax25_frame.payload.ax25_info.telemetry.peak_freq
    :field peak_amp: ax25_frame.payload.ax25_info.telemetry.peak_amp
    :field psd_threshold: ax25_frame.payload.ax25_info.telemetry.psd_threshold
    :field psd_selected_events: ax25_frame.payload.ax25_info.telemetry.psd_selected_events
    :field events_position: ax25_frame.payload.ax25_info.telemetry.events_position
    :field event_time_1: ax25_frame.payload.ax25_info.telemetry.event_time_1
    :field event_time_2: ax25_frame.payload.ax25_info.telemetry.event_time_2
    :field event_time_3: ax25_frame.payload.ax25_info.telemetry.event_time_3
    :field event_time_4: ax25_frame.payload.ax25_info.telemetry.event_time_4
    :field event_time_5: ax25_frame.payload.ax25_info.telemetry.event_time_5
    :field event_time_6: ax25_frame.payload.ax25_info.telemetry.event_time_6
    :field event_time_7: ax25_frame.payload.ax25_info.telemetry.event_time_7
    :field event_time_8: ax25_frame.payload.ax25_info.telemetry.event_time_8
    :field event_time_9: ax25_frame.payload.ax25_info.telemetry.event_time_9
    :field event_time_10: ax25_frame.payload.ax25_info.telemetry.event_time_10
    :field message: ax25_frame.payload.ax25_info.telemetry.message
    
    .. seealso::
       Source - http://www.skcube.sk/wp-content/uploads/2016/06/skcube_data_structures.xlsx
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
            _on = self.pid
            if _on == 240:
                self._raw_ax25_info = self._io.read_bytes_full()
                io = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = self._root.SkcubeFrame(io, self, self._root)
            else:
                self.ax25_info = self._io.read_bytes_full()


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


    class SkcubeFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.packet_type
            if _on == 4:
                self.telemetry = self._root.SkcubeFrame.Block4Cam(self._io, self, self._root)
            elif _on == 6:
                self.telemetry = self._root.SkcubeFrame.Block6Exp(self._io, self, self._root)
            elif _on == 3:
                self.telemetry = self._root.SkcubeFrame.Block3Com(self._io, self, self._root)
            elif _on == 5:
                self.telemetry = self._root.SkcubeFrame.Block5Pwr(self._io, self, self._root)
            elif _on == 2:
                self.telemetry = self._root.SkcubeFrame.Block2Adcs(self._io, self, self._root)
            else:
                self.telemetry = self._root.SkcubeFrame.BlockMessage(self._io, self, self._root)

        class Block5Pwr(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.packet_type_holder = self._io.read_u1()
                self.timestamp = self._io.read_u4le()
                self.fulluptime = self._io.read_u4le()
                self.uptime = self._io.read_u4le()
                self.active_procesor = self._io.read_u2le()
                self.fw_version = self._io.read_u2le()
                self.number_of_reboots = self._io.read_u2le()
                self.countcomerrors = self._io.read_u2le()
                self.countpsuerrors = self._io.read_u2le()
                self.solar_j_current = self._io.read_s2le()
                self.solar_k_current = self._io.read_s2le()
                self.solar_l_current = self._io.read_s2le()
                self.solar_m_current = self._io.read_s2le()
                self.solar_u_current = self._io.read_s2le()
                self.solar_d_current = self._io.read_s2le()
                self.solar_j_temp = self._io.read_s2le()
                self.solar_k_temp = self._io.read_s2le()
                self.solar_l_temp = self._io.read_s2le()
                self.solar_m_temp = self._io.read_s2le()
                self.solar_u_temp = self._io.read_s2le()
                self.solar_d_temp = self._io.read_s2le()
                self.battery_a_voltage = self._io.read_s2le()
                self.battery_b_voltage = self._io.read_s2le()
                self.battery_temp = self._io.read_s2le()
                self.battery_a_capacity = self._io.read_u2le()
                self.battery_b_capacity = self._io.read_u2le()
                self.bat_capacity = self._io.read_u2le()
                self.battery_a_current = self._io.read_s2le()
                self.battery_b_current = self._io.read_s2le()
                self.battery_a_min_current = self._io.read_s2le()
                self.battery_b_min_current = self._io.read_s2le()
                self.battery_a_max_current = self._io.read_s2le()
                self.battery_b_max_current = self._io.read_s2le()
                self.battery_a_avg_current = self._io.read_s2le()
                self.battery_b_avg_current = self._io.read_s2le()
                self.chds_min_current = self._io.read_s2le()
                self.chds_max_current = self._io.read_s2le()
                self.chds_avg_current = self._io.read_s2le()
                self.chds_actual_current = self._io.read_s2le()
                self.com_min_current = self._io.read_s2le()
                self.com_max_current = self._io.read_s2le()
                self.com_avg_current = self._io.read_s2le()
                self.com_actual_current = self._io.read_s2le()
                self.cam_min_current = self._io.read_s2le()
                self.cam_max_current = self._io.read_s2le()
                self.cam_avg_current = self._io.read_s2le()
                self.cam_actual_current = self._io.read_s2le()
                self.exp_min_current = self._io.read_s2le()
                self.exp_max_current = self._io.read_s2le()
                self.exp_avg_current = self._io.read_s2le()
                self.exp_actual_current = self._io.read_s2le()
                self.adcs_min_current = self._io.read_s2le()
                self.adcs_max_current = self._io.read_s2le()
                self.adcs_avg_current = self._io.read_s2le()
                self.adcs_actual_current = self._io.read_s2le()
                self.sys_voltage_min = self._io.read_u2le()
                self.sys_voltage_max = self._io.read_u2le()
                self.sys_voltage_actual = self._io.read_u2le()
                self.nadprudy = self._io.read_u2le()
                self.stav_pripojenia = self._io.read_u2le()
                self.ts_temp = self._io.read_s2le()
                self.countpacket = self._io.read_u4le()
                self.psu_error = self._io.read_u2le()
                self.psu_lasterror = self._io.read_u2le()
                self.com_error = self._io.read_u2le()
                self.com_lasterror = self._io.read_u2le()
                self.cdhs_i_limit = self._io.read_u1()
                self.com_i_limit = self._io.read_u1()
                self.cam_i_limit = self._io.read_u1()
                self.adcs_i_limit = self._io.read_u1()
                self.exp_i_limit = self._io.read_u1()
                self.cam_uv_limit = self._io.read_u1()
                self.exp_uv_limit = self._io.read_u1()
                self.adcs_uv_limit = self._io.read_u1()
                self.bat1_vmax = self._io.read_s2le()
                self.bat1_vmin = self._io.read_s2le()
                self.bat2_vmax = self._io.read_s2le()
                self.bat2_vmin = self._io.read_s2le()
                self.endofdata = self._io.read_u2le()


        class Block2Adcs(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.packet_type_holder = self._io.read_u1()
                self.adcs_mode = self._io.read_u1()
                self.bd_k = self._io.read_u1()
                self.max_pwm_coil_x = self._io.read_u1()
                self.max_pwm_coil_y = self._io.read_u1()
                self.max_pwm_coil_z = self._io.read_u1()
                self.sun_x_p_x = self._io.read_s2le()
                self.sun_x_p_y = self._io.read_s2le()
                self.sun_x_p_irradiation = self._io.read_u1()
                self.sun_x_m_x = self._io.read_s2le()
                self.sun_x_m_y = self._io.read_s2le()
                self.sun_x_m_irradiation = self._io.read_u1()
                self.sun_y_p_x = self._io.read_s2le()
                self.sun_y_p_y = self._io.read_s2le()
                self.sun_y_p_irradiation = self._io.read_u1()
                self.sun_y_m_x = self._io.read_s2le()
                self.sun_y_m_y = self._io.read_s2le()
                self.sun_y_m_irradiation = self._io.read_u1()
                self.sun_z_p_x = self._io.read_s2le()
                self.sun_z_p_y = self._io.read_s2le()
                self.sun_z_p_irradiation = self._io.read_u1()
                self.sun_z_m_x = self._io.read_s2le()
                self.sun_z_m_y = self._io.read_s2le()
                self.sun_z_m_irradiation = self._io.read_u1()
                self.gyroscope_x = self._io.read_u2le()
                self.gyroscope_y = self._io.read_u2le()
                self.gyroscope_z = self._io.read_u2le()
                self.gyroscope_temp = self._io.read_u2le()
                self.magnetometer_1_x = self._io.read_u2le()
                self.magnetometer_1_y = self._io.read_u2le()
                self.magnetometer_1_z = self._io.read_u2le()
                self.magnetometer_1_temp = self._io.read_u2le()
                self.magnetometer_2_x = self._io.read_u2le()
                self.magnetometer_2_y = self._io.read_u2le()
                self.magnetometer_2_z = self._io.read_u2le()
                self.magnetometer_2_temp = self._io.read_u2le()
                self.accelerometer_x = self._io.read_u2le()
                self.accelerometer_y = self._io.read_u2le()
                self.accelerometer_z = self._io.read_u2le()
                self.accel_temp = self._io.read_u2le()
                self.earth_sensor_x_p = self._io.read_u2le()
                self.earth_sensor_x_m = self._io.read_u2le()
                self.earth_sensor_y_p = self._io.read_u2le()
                self.earth_sensor_y_m = self._io.read_u2le()


        class Block3Com(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.packet_type_holder = self._io.read_u1()
                self.timestamp = self._io.read_u4le()
                self.fwversion = self._io.read_u2le()
                self.activecom = self._io.read_u1()
                self.digipeatermode = self._io.read_u1()
                self.noofreboots = self._io.read_u2le()
                self.outputreflpower = self._io.read_u2le()
                self.outputforwardpower = self._io.read_u2le()
                self.outputreflpowercw = self._io.read_u2le()
                self.outputforwardpowercw = self._io.read_u2le()
                self.rssi = self._io.read_u2le()
                self.rssinoise = self._io.read_u2le()
                self.mcutemperature = self._io.read_s1()
                self.patemperature = self._io.read_s1()
                self.cwbeaconsent = self._io.read_u2le()
                self.packetsent = self._io.read_u2le()
                self.correctpacketsreceived = self._io.read_u2le()
                self.brokenpacketsreceived = self._io.read_u2le()
                self.comprotocolerror = self._io.read_u2le()
                self.gsprotocolerror = self._io.read_u2le()
                self.txdisablestatus = self._io.read_u1()
                self.orbittime = self._io.read_u1()
                self.timeslotstart = self._io.read_u1()
                self.timeslotend = self._io.read_u1()


        class Block6Exp(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.packet_type_holder = self._io.read_u1()
                self.timestamp = self._io.read_u4le()
                self.fw_version = self._io.read_u2le()
                self.number_of_reboots = self._io.read_u2le()
                self.active_adc_channel = self._io.read_u1()
                self.fft_gain = self._io.read_u1()
                self.low_frequency = self._io.read_u1()
                self.high_frequency = self._io.read_u1()
                self.max_hold_sec = self._io.read_u2le()
                self.slow_position = self._io.read_u2le()
                self.postring_samples = self._io.read_u2le()
                self.psd = self._io.read_u2le()
                self.psd_max = self._io.read_u2le()
                self.psd_selected = self._io.read_u2le()
                self.psd_selected_max = self._io.read_u2le()
                self.peak_freq = self._io.read_u2le()
                self.peak_amp = self._io.read_u2le()
                self.psd_threshold = self._io.read_u2le()
                self.psd_selected_events = self._io.read_u2le()
                self.events_position = self._io.read_u1()
                self.event_time_1 = self._io.read_u4le()
                self.event_time_2 = self._io.read_u4le()
                self.event_time_3 = self._io.read_u4le()
                self.event_time_4 = self._io.read_u4le()
                self.event_time_5 = self._io.read_u4le()
                self.event_time_6 = self._io.read_u4le()
                self.event_time_7 = self._io.read_u4le()
                self.event_time_8 = self._io.read_u4le()
                self.event_time_9 = self._io.read_u4le()
                self.event_time_10 = self._io.read_u4le()


        class BlockMessage(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.message = (self._io.read_bytes_full()).decode(u"utf-8")


        class Block4Cam(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.packet_type_holder = self._io.read_u1()
                self.timestamp = self._io.read_u4le()
                self.fw_version = self._io.read_u2le()
                self.number_of_reboots = self._io.read_u2le()
                self.jpeg_compression = self._io.read_u1()
                self.jpeg_scale = self._io.read_u1()
                self.mcu_temperature = self._io.read_s1()
                self.vref_internal = self._io.read_u2le()
                self.packets_sent = self._io.read_u2le()
                self.cw_sent = self._io.read_u2le()
                self.flash_image_position = self._io.read_u1()
                self.tx_datarate = self._io.read_u1()


        @property
        def packet_type(self):
            if hasattr(self, '_m_packet_type'):
                return self._m_packet_type if hasattr(self, '_m_packet_type') else None

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_packet_type = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_packet_type if hasattr(self, '_m_packet_type') else None


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



