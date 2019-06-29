# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Cas4(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field pwr_volt: ax25_frame.payload.ax25_info.telemetry.pwr_volt
    :field pwr_cur: ax25_frame.payload.ax25_info.telemetry.pwr_cur
    :field convert_volt: ax25_frame.payload.ax25_info.telemetry.convert_volt
    :field convert_cur: ax25_frame.payload.ax25_info.telemetry.convert_cur
    :field obc_temp: ax25_frame.payload.ax25_info.telemetry.obc_temp
    :field rf_amp_temp: ax25_frame.payload.ax25_info.telemetry.rf_amp_temp
    :field rcv_agc_volt: ax25_frame.payload.ax25_info.telemetry.rcv_agc_volt
    :field rf_fwd: ax25_frame.payload.ax25_info.telemetry.rf_fwd
    :field rf_ref: ax25_frame.payload.ax25_info.telemetry.rf_ref
    :field obc_volt: ax25_frame.payload.ax25_info.telemetry.obc_volt
    :field obc_reset: ax25_frame.payload.ax25_info.telemetry.obc_reset
    :field pkt_cnt: ax25_frame.payload.ax25_info.telemetry.pkt_cnt
    :field sat_num: ax25_frame.payload.ax25_info.telemetry.sat_num
    :field op_mode: ax25_frame.payload.ax25_info.telemetry.op_mode
    :field pwr_on_op_mode: ax25_frame.payload.ax25_info.telemetry.pwr_on_op_mode
    :field i2c_watchdog: ax25_frame.payload.ax25_info.telemetry.i2c_watchdog
    :field i2c_recon_cnt: ax25_frame.payload.ax25_info.telemetry.i2c_recon_cnt
    :field tc_watchdog: ax25_frame.payload.ax25_info.telemetry.tc_watchdog
    :field tc_reset_cnt: ax25_frame.payload.ax25_info.telemetry.tc_reset_cnt
    :field adc_watchdog: ax25_frame.payload.ax25_info.telemetry.adc_watchdog
    :field adc_reset_cnt: ax25_frame.payload.ax25_info.telemetry.adc_reset_cnt
    :field spi_watchdog: ax25_frame.payload.ax25_info.telemetry.spi_watchdog
    :field spi_init_cnt: ax25_frame.payload.ax25_info.telemetry.spi_init_cnt
    :field cpu_watchdog: ax25_frame.payload.ax25_info.telemetry.cpu_watchdog
    :field cpu_reset_cnt: ax25_frame.payload.ax25_info.telemetry.cpu_reset_cnt
    :field framecounter: ax25_frame.payload.ax25_info.framecounter
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
                self.ax25_info = self._root.Cas4Frame(io, self, self._root)
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


    class Cas4Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.syncpacket = self._io.ensure_fixed_contents(b"\xEB\x90")
            _on = (self.framecounter % 4)
            if _on == 0:
                self._raw_telemetry = self._io.read_bytes(4)
                io = KaitaiStream(BytesIO(self._raw_telemetry))
                self.telemetry = self._root.Cas4Frame.Frame1(io, self, self._root)
            elif _on == 1:
                self._raw_telemetry = self._io.read_bytes(4)
                io = KaitaiStream(BytesIO(self._raw_telemetry))
                self.telemetry = self._root.Cas4Frame.Frame2(io, self, self._root)
            elif _on == 3:
                self._raw_telemetry = self._io.read_bytes(4)
                io = KaitaiStream(BytesIO(self._raw_telemetry))
                self.telemetry = self._root.Cas4Frame.Frame4(io, self, self._root)
            elif _on == 2:
                self._raw_telemetry = self._io.read_bytes(4)
                io = KaitaiStream(BytesIO(self._raw_telemetry))
                self.telemetry = self._root.Cas4Frame.Frame3(io, self, self._root)
            else:
                self.telemetry = self._io.read_bytes(4)
            self.reserved1 = self._io.read_bytes(9)
            self.framecounterplaceholder = self._io.read_u1()
            self.reserved2 = self._io.read_bytes(112)

        class Frame1(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.pwr_volt = self._io.read_u1()
                self.pwr_cur = self._io.read_u1()
                self.convert_volt = self._io.read_u1()
                self.convert_cur = self._io.read_u1()


        class Frame2(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.obc_temp = self._io.read_u1()
                self.rf_amp_temp = self._io.read_u1()
                self.rcv_agc_volt = self._io.read_u1()
                self.rf_fwd = self._io.read_u1()


        class Frame3(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.rf_ref = self._io.read_u1()
                self.obc_volt = self._io.read_u1()
                self.obc_reset = self._io.read_u1()
                self.pkt_cnt = self._io.read_bits_int(4)
                self.sat_num = self._io.read_bits_int(4)


        class Frame4(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.op_mode = self._io.read_bits_int(4)
                self.pwr_on_op_mode = self._io.read_bits_int(4)
                self.i2c_watchdog = self._io.read_bits_int(1) != 0
                self.i2c_recon_cnt = self._io.read_bits_int(3)
                self.tc_watchdog = self._io.read_bits_int(1) != 0
                self.tc_reset_cnt = self._io.read_bits_int(3)
                self.adc_watchdog = self._io.read_bits_int(1) != 0
                self.adc_reset_cnt = self._io.read_bits_int(3)
                self.spi_watchdog = self._io.read_bits_int(1) != 0
                self.spi_init_cnt = self._io.read_bits_int(3)
                self.cpu_watchdog = self._io.read_bits_int(1) != 0
                self.cpu_reset_cnt = self._io.read_bits_int(3)


        @property
        def framecounter(self):
            if hasattr(self, '_m_framecounter'):
                return self._m_framecounter if hasattr(self, '_m_framecounter') else None

            _pos = self._io.pos()
            self._io.seek(15)
            self._m_framecounter = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_framecounter if hasattr(self, '_m_framecounter') else None


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



