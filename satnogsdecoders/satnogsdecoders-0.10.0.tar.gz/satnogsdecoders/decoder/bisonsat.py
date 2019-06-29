# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Bisonsat(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field rtc_time_year: ax25_frame.payload.ax25_info.rtc_time_year
    :field rtc_time_month: ax25_frame.payload.ax25_info.rtc_time_month
    :field rtc_time_day: ax25_frame.payload.ax25_info.rtc_time_day
    :field rtc_time_hour: ax25_frame.payload.ax25_info.rtc_time_hour
    :field rtc_time_minutes: ax25_frame.payload.ax25_info.rtc_time_minutes
    :field rtc_time_seconds: ax25_frame.payload.ax25_info.rtc_time_seconds
    :field rtc_time_th: ax25_frame.payload.ax25_info.rtc_time_th
    :field os_ticks: ax25_frame.payload.ax25_info.os_ticks
    :field last_cmd_1: ax25_frame.payload.ax25_info.last_cmd_1
    :field last_cmd_2: ax25_frame.payload.ax25_info.last_cmd_2
    :field cmd_queue_length: ax25_frame.payload.ax25_info.cmd_queue_length
    :field filename_jpeg: ax25_frame.payload.ax25_info.filename_jpeg
    :field filename_raw: ax25_frame.payload.ax25_info.filename_raw
    :field cdh_reset_events: ax25_frame.payload.ax25_info.cdh_reset_events
    :field y_plus_current: ax25_frame.payload.ax25_info.y_plus_current
    :field y_plus_temperature: ax25_frame.payload.ax25_info.y_plus_temperature
    :field y_pair_voltage: ax25_frame.payload.ax25_info.y_pair_voltage
    :field x_minus_current: ax25_frame.payload.ax25_info.x_minus_current
    :field x_minus_temperature: ax25_frame.payload.ax25_info.x_minus_temperature
    :field x_pair_voltage: ax25_frame.payload.ax25_info.x_pair_voltage
    :field x_plus_current: ax25_frame.payload.ax25_info.x_plus_current
    :field x_plus_temperature: ax25_frame.payload.ax25_info.x_plus_temperature
    :field z_pair_voltage: ax25_frame.payload.ax25_info.z_pair_voltage
    :field z_plus__current: ax25_frame.payload.ax25_info.z_plus__current
    :field z_plus_temperature: ax25_frame.payload.ax25_info.z_plus_temperature
    :field y_minus_current: ax25_frame.payload.ax25_info.y_minus_current
    :field y_minus_temperature: ax25_frame.payload.ax25_info.y_minus_temperature
    :field battery_current: ax25_frame.payload.ax25_info.battery_current
    :field battery1_temperature: ax25_frame.payload.ax25_info.battery1_temperature
    :field battery1_full_voltage: ax25_frame.payload.ax25_info.battery1_full_voltage
    :field battery1_current_direction: ax25_frame.payload.ax25_info.battery1_current_direction
    :field battery1_current: ax25_frame.payload.ax25_info.battery1_current
    :field battery0_temperature: ax25_frame.payload.ax25_info.battery0_temperature
    :field battery0_full_voltage: ax25_frame.payload.ax25_info.battery0_full_voltage
    :field bus_current_5v: ax25_frame.payload.ax25_info.bus_current_5v
    :field bus_current_3v3: ax25_frame.payload.ax25_info.bus_current_3v3
    :field battery0_current_direction: ax25_frame.payload.ax25_info.battery0_current_direction
    :field battery0_current: ax25_frame.payload.ax25_info.battery0_current
    :field z_minus_temperature: ax25_frame.payload.ax25_info.z_minus_temperature
    :field z_minus_current: ax25_frame.payload.ax25_info.z_minus_current
    :field hmb_accelx: ax25_frame.payload.ax25_info.hmb_accelx
    :field hmb_accely: ax25_frame.payload.ax25_info.hmb_accely
    :field hmb_accelz: ax25_frame.payload.ax25_info.hmb_accelz
    :field hmb_temperature: ax25_frame.payload.ax25_info.hmb_temperature
    :field hmb_gyrox: ax25_frame.payload.ax25_info.hmb_gyrox
    :field hmb_gyroy: ax25_frame.payload.ax25_info.hmb_gyroy
    :field hmb_gyroz: ax25_frame.payload.ax25_info.hmb_gyroz
    :field hmb_magx: ax25_frame.payload.ax25_info.hmb_magx
    :field hmb_magy: ax25_frame.payload.ax25_info.hmb_magy
    :field hmb_magz: ax25_frame.payload.ax25_info.hmb_magz
    :field task_rst_status: ax25_frame.payload.ax25_info.task_rst_status
    :field task_antenna_deploy_status: ax25_frame.payload.ax25_info.task_antenna_deploy_status
    :field task_telemetry_gather_status: ax25_frame.payload.ax25_info.task_telemetry_gather_status
    :field task_image_capture_status: ax25_frame.payload.ax25_info.task_image_capture_status
    :field task_jpeg_status: ax25_frame.payload.ax25_info.task_jpeg_status
    :field task_com_receive_status: ax25_frame.payload.ax25_info.task_com_receive_status
    :field task_cmd_decoder_status: ax25_frame.payload.ax25_info.task_cmd_decoder_status
    :field task_bisonsat_cmd_decoder_status: ax25_frame.payload.ax25_info.task_bisonsat_cmd_decoder_status
    :field task_tranmit_image_status: ax25_frame.payload.ax25_info.task_tranmit_image_status
    :field cdh_wdt_events: ax25_frame.payload.ax25_info.cdh_wdt_events
    :field eps_status: ax25_frame.payload.ax25_info.eps_status
    
    .. seealso::
       Source - http://cubesat.skc.edu/beacon-decoding-information/
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
            self.offset = (self._io.read_bytes(7)).decode(u"ASCII")
            self.preamble = (self._io.read_bytes(3)).decode(u"ASCII")
            self.call_sign = (self._io.read_bytes(6)).decode(u"ASCII")
            self.rtc_time_year = self._io.read_u1()
            self.rtc_time_month = self._io.read_u1()
            self.rtc_time_day = self._io.read_u1()
            self.rtc_time_hour = self._io.read_u1()
            self.rtc_time_minutes = self._io.read_u1()
            self.rtc_time_seconds = self._io.read_u1()
            self.rtc_time_th = self._io.read_u1()
            self.os_ticks = self._io.read_u4le()
            self.last_cmd_1 = self._io.read_u1()
            self.last_cmd_2 = self._io.read_u1()
            self.cmd_queue_length = self._io.read_u1()
            self.filename_jpeg = (self._io.read_bytes(8)).decode(u"ASCII")
            self.filename_raw = (self._io.read_bytes(8)).decode(u"ASCII")
            self.cdh_reset_events = self._io.read_u1()
            self.y_plus_current = self._io.read_u2le()
            self.y_plus_temperature = self._io.read_u2le()
            self.y_pair_voltage = self._io.read_u2le()
            self.x_minus_current = self._io.read_u2le()
            self.x_minus_temperature = self._io.read_u2le()
            self.x_pair_voltage = self._io.read_u2le()
            self.x_plus_current = self._io.read_u2le()
            self.x_plus_temperature = self._io.read_u2le()
            self.z_pair_voltage = self._io.read_u2le()
            self.z_plus__current = self._io.read_u2le()
            self.z_plus_temperature = self._io.read_u2le()
            self.y_minus_current = self._io.read_u2le()
            self.y_minus_temperature = self._io.read_u2le()
            self.battery_current = self._io.read_u2le()
            self.battery1_temperature = self._io.read_u2le()
            self.battery1_full_voltage = self._io.read_u2le()
            self.battery1_current_direction = self._io.read_u2le()
            self.battery1_current = self._io.read_u2le()
            self.battery0_temperature = self._io.read_u2le()
            self.battery0_full_voltage = self._io.read_u2le()
            self.bus_current_5v = self._io.read_u2le()
            self.bus_current_3v3 = self._io.read_u2le()
            self.battery0_current_direction = self._io.read_u2le()
            self.battery0_current = self._io.read_u2le()
            self.z_minus_temperature = self._io.read_u2le()
            self.z_minus_current = self._io.read_u2le()
            self.hmb_accelx = self._io.read_u2le()
            self.hmb_accely = self._io.read_u2le()
            self.hmb_accelz = self._io.read_u2le()
            self.hmb_temperature = self._io.read_u2le()
            self.hmb_gyrox = self._io.read_u2le()
            self.hmb_gyroy = self._io.read_u2le()
            self.hmb_gyroz = self._io.read_u2le()
            self.hmb_magx = self._io.read_u2le()
            self.hmb_magy = self._io.read_u2le()
            self.hmb_magz = self._io.read_u2le()
            self.task_rst_status = self._io.read_u1()
            self.task_antenna_deploy_status = self._io.read_u1()
            self.task_telemetry_gather_status = self._io.read_u1()
            self.task_image_capture_status = self._io.read_u1()
            self.task_jpeg_status = self._io.read_u1()
            self.task_com_receive_status = self._io.read_u1()
            self.task_cmd_decoder_status = self._io.read_u1()
            self.task_bisonsat_cmd_decoder_status = self._io.read_u1()
            self.task_tranmit_image_status = self._io.read_u1()
            self.cdh_wdt_events = self._io.read_u1()
            self.eps_status = self._io.read_u2le()



