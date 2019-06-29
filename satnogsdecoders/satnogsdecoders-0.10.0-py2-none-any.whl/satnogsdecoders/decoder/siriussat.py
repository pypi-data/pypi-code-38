# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Siriussat(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field beacon_type: ax25_frame.payload.ax25_info.beacon_type
    :field usb1: ax25_frame.payload.ax25_info.body.usb1
    :field usb2: ax25_frame.payload.ax25_info.body.usb2
    :field usb3: ax25_frame.payload.ax25_info.body.usb3
    :field isb1: ax25_frame.payload.ax25_info.body.isb1
    :field isb2: ax25_frame.payload.ax25_info.body.isb2
    :field isb3: ax25_frame.payload.ax25_info.body.isb3
    :field iab: ax25_frame.payload.ax25_info.body.iab
    :field ich1: ax25_frame.payload.ax25_info.body.ich1
    :field ich2: ax25_frame.payload.ax25_info.body.ich2
    :field ich3: ax25_frame.payload.ax25_info.body.ich3
    :field ich4: ax25_frame.payload.ax25_info.body.ich4
    :field t1_pw: ax25_frame.payload.ax25_info.body.t1_pw
    :field t2_pw: ax25_frame.payload.ax25_info.body.t2_pw
    :field t3_pw: ax25_frame.payload.ax25_info.body.t3_pw
    :field t4_pw: ax25_frame.payload.ax25_info.body.t4_pw
    :field uab_crit: ax25_frame.payload.ax25_info.body.uab_crit
    :field uab_min: ax25_frame.payload.ax25_info.body.uab_min
    :field heater2_manual: ax25_frame.payload.ax25_info.body.heater2_manual
    :field heater1_manual: ax25_frame.payload.ax25_info.body.heater1_manual
    :field heater2_on: ax25_frame.payload.ax25_info.body.heater2_on
    :field heater1_on: ax25_frame.payload.ax25_info.body.heater1_on
    :field tab_max: ax25_frame.payload.ax25_info.body.tab_max
    :field tab_min: ax25_frame.payload.ax25_info.body.tab_min
    :field channelon4: ax25_frame.payload.ax25_info.body.channelon4
    :field channelon3: ax25_frame.payload.ax25_info.body.channelon3
    :field channelon2: ax25_frame.payload.ax25_info.body.channelon2
    :field channelon1: ax25_frame.payload.ax25_info.body.channelon1
    :field ich_limit4: ax25_frame.payload.ax25_info.body.ich_limit4
    :field ich_limit3: ax25_frame.payload.ax25_info.body.ich_limit3
    :field ich_limit2: ax25_frame.payload.ax25_info.body.ich_limit2
    :field ich_limit1: ax25_frame.payload.ax25_info.body.ich_limit1
    :field reserved0: ax25_frame.payload.ax25_info.body.reserved0
    :field charger: ax25_frame.payload.ax25_info.body.charger
    :field reserved1: ax25_frame.payload.ax25_info.body.reserved1
    :field uab: ax25_frame.payload.ax25_info.body.uab
    :field reg_tel_id: ax25_frame.payload.ax25_info.body.reg_tel_id
    :field pss_time: ax25_frame.payload.ax25_info.body.pss_time
    :field pss_nres: ax25_frame.payload.ax25_info.body.pss_nres
    :field psdd_fl: ax25_frame.payload.ax25_info.body.psdd_fl
    :field t_amp: ax25_frame.payload.ax25_info.body.t_amp
    :field t_uhf: ax25_frame.payload.ax25_info.body.t_uhf
    :field rssirx: ax25_frame.payload.ax25_info.body.rssirx
    :field rssiidle: ax25_frame.payload.ax25_info.body.rssiidle
    :field pf: ax25_frame.payload.ax25_info.body.pf
    :field pb: ax25_frame.payload.ax25_info.body.pb
    :field uhf_nres: ax25_frame.payload.ax25_info.body.uhf_nres
    :field uhf_fl: ax25_frame.payload.ax25_info.body.uhf_fl
    :field uhf_time: ax25_frame.payload.ax25_info.body.uhf_time
    :field uptime: ax25_frame.payload.ax25_info.body.uptime
    :field current: ax25_frame.payload.ax25_info.body.current
    :field uuhf: ax25_frame.payload.ax25_info.body.uuhf
    :field t_mb: ax25_frame.payload.ax25_info.body.t_mb
    :field mx: ax25_frame.payload.ax25_info.body.mx
    :field my: ax25_frame.payload.ax25_info.body.my
    :field mz: ax25_frame.payload.ax25_info.body.mz
    :field vx: ax25_frame.payload.ax25_info.body.vx
    :field vy: ax25_frame.payload.ax25_info.body.vy
    :field vz: ax25_frame.payload.ax25_info.body.vz
    :field nres: ax25_frame.payload.ax25_info.body.nres
    :field rcon: ax25_frame.payload.ax25_info.body.rcon
    :field fl: ax25_frame.payload.ax25_info.body.fl
    :field time: ax25_frame.payload.ax25_info.body.time
    :field payload_flags: ax25_frame.payload.ax25_info.body.payload_flags
    :field timesend: ax25_frame.payload.ax25_info.body.timesend
    :field t_plate: ax25_frame.payload.ax25_info.body.t_plate
    :field t_cpu: ax25_frame.payload.ax25_info.body.t_cpu
    :field cursens1: ax25_frame.payload.ax25_info.body.cursens1
    :field cursens2: ax25_frame.payload.ax25_info.body.cursens2
    :field nrst: ax25_frame.payload.ax25_info.body.nrst
    :field timerst: ax25_frame.payload.ax25_info.body.timerst
    :field ch1rate: ax25_frame.payload.ax25_info.body.ch1rate
    :field ch2rate: ax25_frame.payload.ax25_info.body.ch2rate
    :field ch3rate: ax25_frame.payload.ax25_info.body.ch3rate
    :field ch4rate: ax25_frame.payload.ax25_info.body.ch4rate
    :field ch5rate: ax25_frame.payload.ax25_info.body.ch5rate
    :field ch6rate: ax25_frame.payload.ax25_info.body.ch6rate
    :field ptrend1: ax25_frame.payload.ax25_info.body.ptrend1
    :field ptrcrt1: ax25_frame.payload.ax25_info.body.ptrcrt1
    :field ptrend2: ax25_frame.payload.ax25_info.body.ptrend2
    :field ptrcrt2: ax25_frame.payload.ax25_info.body.ptrcrt2
    :field ptrend3: ax25_frame.payload.ax25_info.body.ptrend3
    :field ptrcrt3: ax25_frame.payload.ax25_info.body.ptrcrt3
    :field lastevent_ch1_1: ax25_frame.payload.ax25_info.body.lastevent_ch1_1
    :field lastevent_ch1_2: ax25_frame.payload.ax25_info.body.lastevent_ch1_2
    :field lastevent_ch1_3: ax25_frame.payload.ax25_info.body.lastevent_ch1_3
    :field lastevent_ch2_1: ax25_frame.payload.ax25_info.body.lastevent_ch2_1
    :field lastevent_ch2_2: ax25_frame.payload.ax25_info.body.lastevent_ch2_2
    :field lastevent_ch2_3: ax25_frame.payload.ax25_info.body.lastevent_ch2_3
    
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
            self.ax25_info = self._root.Tlm(io, self, self._root)


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
            self.ax25_info = self._root.Tlm(io, self, self._root)


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
            self.usb1 = self._io.read_u2le()
            self.usb2 = self._io.read_u2le()
            self.usb3 = self._io.read_u2le()
            self.isb1 = self._io.read_u2le()
            self.isb2 = self._io.read_u2le()
            self.isb3 = self._io.read_u2le()
            self.iab = self._io.read_s2le()
            self.ich1 = self._io.read_u2le()
            self.ich2 = self._io.read_u2le()
            self.ich3 = self._io.read_u2le()
            self.ich4 = self._io.read_u2le()
            self.t1_pw = self._io.read_s2le()
            self.t2_pw = self._io.read_s2le()
            self.t3_pw = self._io.read_s2le()
            self.t4_pw = self._io.read_s2le()
            self.uab_crit = self._io.read_bits_int(1) != 0
            self.uab_min = self._io.read_bits_int(1) != 0
            self.heater2_manual = self._io.read_bits_int(1) != 0
            self.heater1_manual = self._io.read_bits_int(1) != 0
            self.heater2_on = self._io.read_bits_int(1) != 0
            self.heater1_on = self._io.read_bits_int(1) != 0
            self.tab_max = self._io.read_bits_int(1) != 0
            self.tab_min = self._io.read_bits_int(1) != 0
            self.channelon4 = self._io.read_bits_int(1) != 0
            self.channelon3 = self._io.read_bits_int(1) != 0
            self.channelon2 = self._io.read_bits_int(1) != 0
            self.channelon1 = self._io.read_bits_int(1) != 0
            self.ich_limit4 = self._io.read_bits_int(1) != 0
            self.ich_limit3 = self._io.read_bits_int(1) != 0
            self.ich_limit2 = self._io.read_bits_int(1) != 0
            self.ich_limit1 = self._io.read_bits_int(1) != 0
            self.reserved0 = self._io.read_bits_int(7)
            self.charger = self._io.read_bits_int(1) != 0
            self._io.align_to_byte()
            self.reserved1 = self._io.read_u1()
            self.uab = self._io.read_s2le()
            self.reg_tel_id = self._io.read_u4le()
            self.pss_time = self._io.read_s4le()
            self.pss_nres = self._io.read_u1()
            self.psdd_fl = self._io.read_u1()
            self.t_amp = self._io.read_s1()
            self.t_uhf = self._io.read_s1()
            self.rssirx = self._io.read_s1()
            self.rssiidle = self._io.read_s1()
            self.pf = self._io.read_s1()
            self.pb = self._io.read_s1()
            self.uhf_nres = self._io.read_u1()
            self.uhf_fl = self._io.read_u1()
            self.uhf_time = self._io.read_s4le()
            self.uptime = self._io.read_u4le()
            self.current = self._io.read_u2le()
            self.uuhf = self._io.read_s2le()


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


    class Extendedbeacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.t_mb = self._io.read_s2le()
            self.mx = self._io.read_f4le()
            self.my = self._io.read_f4le()
            self.mz = self._io.read_f4le()
            self.vx = self._io.read_f4le()
            self.vy = self._io.read_f4le()
            self.vz = self._io.read_f4le()
            self.nres = self._io.read_u1()
            self.rcon = self._io.read_u1()
            self.fl = self._io.read_u1()
            self.time = self._io.read_s4le()
            self.payload_flags = self._io.read_u1()
            self.timesend = self._io.read_s4le()
            self.t_plate = self._io.read_s2le()
            self.t_cpu = self._io.read_s2le()
            self.cursens1 = self._io.read_u2le()
            self.cursens2 = self._io.read_u2le()
            self.nrst = self._io.read_u1()
            self.timerst = self._io.read_s4le()
            self.ch1rate = self._io.read_u2le()
            self.ch2rate = self._io.read_u2le()
            self.ch3rate = self._io.read_u2le()
            self.ch4rate = self._io.read_u2le()
            self.ch5rate = self._io.read_u2le()
            self.ch6rate = self._io.read_u2le()
            self.ptrend1 = self._io.read_u2le()
            self.ptrcrt1 = self._io.read_u2le()
            self.ptrend2 = self._io.read_u2le()
            self.ptrcrt2 = self._io.read_u2le()
            self.ptrend3 = self._io.read_u2le()
            self.ptrcrt3 = self._io.read_u2le()
            self.lastevent_ch1_1 = self._io.read_u1()
            self.lastevent_ch1_2 = self._io.read_u1()
            self.lastevent_ch1_3 = self._io.read_u1()
            self.lastevent_ch2_1 = self._io.read_u1()
            self.lastevent_ch2_2 = self._io.read_u1()
            self.lastevent_ch2_3 = self._io.read_u1()


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


    class Tlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_type = self._io.read_u1()
            self.unknown1 = self._io.read_bytes(7)
            _on = self.beacon_type
            if _on == 22:
                self.body = self._root.Beacon(self._io, self, self._root)
            elif _on == 23:
                self.body = self._root.Extendedbeacon(self._io, self, self._root)



