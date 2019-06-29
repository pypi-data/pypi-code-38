# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Us6(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field packetindex: ax25_frame.payload.ax25_info.packetindex
    :field groundindexack: ax25_frame.payload.ax25_info.groundindexack
    :field payloadsize: ax25_frame.payload.ax25_info.payloadsize
    :field rebootcounter: ax25_frame.payload.ax25_info.rebootcounter
    :field uptime: ax25_frame.payload.ax25_info.uptime
    :field unixtime: ax25_frame.payload.ax25_info.unixtime
    :field tempmcu: ax25_frame.payload.ax25_info.tempmcu
    :field tempfpga: ax25_frame.payload.ax25_info.tempfpga
    :field magnetometerx: ax25_frame.payload.ax25_info.magnetometerx
    :field magnetometery: ax25_frame.payload.ax25_info.magnetometery
    :field magnetometerz: ax25_frame.payload.ax25_info.magnetometerz
    :field gyroscopex: ax25_frame.payload.ax25_info.gyroscopex
    :field gyroscopey: ax25_frame.payload.ax25_info.gyroscopey
    :field gyroscopez: ax25_frame.payload.ax25_info.gyroscopez
    :field cpucurrent: ax25_frame.payload.ax25_info.cpucurrent
    :field tempradio: ax25_frame.payload.ax25_info.tempradio
    :field payloadreserved1: ax25_frame.payload.ax25_info.payloadreserved1
    :field payloadreserved2: ax25_frame.payload.ax25_info.payloadreserved2
    :field tempbottom: ax25_frame.payload.ax25_info.tempbottom
    :field tempupper: ax25_frame.payload.ax25_info.tempupper
    :field payloadreserved3: ax25_frame.payload.ax25_info.payloadreserved3
    :field epsvbat: ax25_frame.payload.ax25_info.epsvbat
    :field epscurrent_sun: ax25_frame.payload.ax25_info.epscurrent_sun
    :field epscurrent_out: ax25_frame.payload.ax25_info.epscurrent_out
    :field epsvpanel01: ax25_frame.payload.ax25_info.epsvpanel01
    :field epsvpanel02: ax25_frame.payload.ax25_info.epsvpanel02
    :field epsvpanel03: ax25_frame.payload.ax25_info.epsvpanel03
    :field epscurrent01: ax25_frame.payload.ax25_info.epscurrent01
    :field epscurrent02: ax25_frame.payload.ax25_info.epscurrent02
    :field epscurrent03: ax25_frame.payload.ax25_info.epscurrent03
    :field epsbatttemp: ax25_frame.payload.ax25_info.epsbatttemp
    :field payloadreserved4: ax25_frame.payload.ax25_info.payloadreserved4
    :field saterrorflags: ax25_frame.payload.ax25_info.saterrorflags
    :field satoperationstatus: ax25_frame.payload.ax25_info.satoperationstatus
    :field crc: ax25_frame.payload.ax25_info.crc
    
    .. seealso::
       Source - https://www.gaussteam.com/radio-amateur-information-for-unisat-6/
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
            self.payload = self._root.Us6Frame(self._io, self, self._root)


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


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class Us6Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._root.Frame(self._io, self, self._root)


    class Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.syncpacket = self._io.ensure_fixed_contents(b"\x55\x53\x36")
            self.packetindex = self._io.read_u2le()
            self.groundindexack = self._io.read_u2le()
            self.packettype = self._io.ensure_fixed_contents(b"\x01")
            self.payloadsize = self._io.read_u1()
            self.rebootcounter = self._io.read_u2le()
            self.uptime = self._io.read_u4le()
            self.unixtime = self._io.read_u4le()
            self.tempmcu = self._io.read_s1()
            self.tempfpga = self._io.read_s1()
            self.magnetometerx = self._io.read_s2le()
            self.magnetometery = self._io.read_s2le()
            self.magnetometerz = self._io.read_s2le()
            self.gyroscopex = self._io.read_s2le()
            self.gyroscopey = self._io.read_s2le()
            self.gyroscopez = self._io.read_s2le()
            self.cpucurrent = self._io.read_u2le()
            self.tempradio = self._io.read_s1()
            self.payloadreserved1 = self._io.read_u1()
            self.payloadreserved2 = self._io.read_u1()
            self.tempbottom = self._io.read_u1()
            self.tempupper = self._io.read_u1()
            self.payloadreserved3 = self._io.read_u1()
            self.epsvbat = self._io.read_u2le()
            self.epscurrent_sun = self._io.read_u2le()
            self.epscurrent_out = self._io.read_u2le()
            self.epsvpanel01 = self._io.read_u2le()
            self.epsvpanel02 = self._io.read_u2le()
            self.epsvpanel03 = self._io.read_u2le()
            self.epscurrent01 = self._io.read_u2le()
            self.epscurrent02 = self._io.read_u2le()
            self.epscurrent03 = self._io.read_u2le()
            self.epsbatttemp = self._io.read_u2le()
            self.payloadreserved4 = self._io.read_u1()
            self.saterrorflags = self._io.read_u2le()
            self.satoperationstatus = self._io.read_u1()
            self.crc = self._io.read_u1()


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



