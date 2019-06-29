# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Acrux1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field tx_count: ax25_frame.payload.msp_payload.tx_count
    :field rx_count: ax25_frame.payload.msp_payload.rx_count
    :field rx_valid: ax25_frame.payload.msp_payload.rx_valid
    :field payload_type: ax25_frame.payload.msp_payload.payload_type
    :field comouti1: ax25_frame.payload.msp_payload.comouti1
    :field comoutv1: ax25_frame.payload.msp_payload.comoutv1
    :field comouti2: ax25_frame.payload.msp_payload.comouti2
    :field comoutv2: ax25_frame.payload.msp_payload.comoutv2
    :field comt2: ax25_frame.payload.msp_payload.comt2
    :field epsadcbatv1: ax25_frame.payload.msp_payload.epsadcbatv1
    :field epsloadi1: ax25_frame.payload.msp_payload.epsloadi1
    :field epsadcbatv2: ax25_frame.payload.msp_payload.epsadcbatv2
    :field epsboostini2: ax25_frame.payload.msp_payload.epsboostini2
    :field epsrail1: ax25_frame.payload.msp_payload.epsrail1
    :field epsrail2: ax25_frame.payload.msp_payload.epsrail2
    :field epstoppanelv: ax25_frame.payload.msp_payload.epstoppanelv
    :field epstoppaneli: ax25_frame.payload.msp_payload.epstoppaneli
    :field epst1: ax25_frame.payload.msp_payload.epst1
    :field epst2: ax25_frame.payload.msp_payload.epst2
    :field xposv: ax25_frame.payload.msp_payload.xposv
    :field xposi: ax25_frame.payload.msp_payload.xposi
    :field xpost1: ax25_frame.payload.msp_payload.xpost1
    :field yposv: ax25_frame.payload.msp_payload.yposv
    :field yposi: ax25_frame.payload.msp_payload.yposi
    :field ypost1: ax25_frame.payload.msp_payload.ypost1
    :field xnegv: ax25_frame.payload.msp_payload.xnegv
    :field xnegi: ax25_frame.payload.msp_payload.xnegi
    :field xnegt1: ax25_frame.payload.msp_payload.xnegt1
    :field ynegv: ax25_frame.payload.msp_payload.ynegv
    :field ynegi: ax25_frame.payload.msp_payload.ynegi
    :field ynegt1: ax25_frame.payload.msp_payload.ynegt1
    :field znegv: ax25_frame.payload.msp_payload.znegv
    :field znegi: ax25_frame.payload.msp_payload.znegi
    :field znegt1: ax25_frame.payload.msp_payload.znegt1
    :field zpost: ax25_frame.payload.msp_payload.zpost
    :field cdhtime: ax25_frame.payload.msp_payload.cdhtime
    :field swcdhlastreboot: ax25_frame.payload.msp_payload.swcdhlastreboot
    :field swsequence: ax25_frame.payload.msp_payload.swsequence
    :field outreachmessage: ax25_frame.payload.msp_payload.outreachmessage
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
            self.msp_payload = self._root.MspPayloadT(self._io, self, self._root)
            self.zero_padding = self._io.read_bytes(91)
            self.fec8_rs_checksum = self._io.read_bytes(32)


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


    class MspPayloadT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tx_count = self._io.read_u1()
            self.rx_count = self._io.read_u1()
            self.rx_valid = self._io.read_u1()
            self.payload_type = self._io.read_u1()
            self.comouti1 = self._io.read_s2le()
            self.comoutv1 = self._io.read_s2le()
            self.comouti2 = self._io.read_s2le()
            self.comoutv2 = self._io.read_s2le()
            self.comt2 = self._io.read_s2le()
            self.epsadcbatv1 = self._io.read_s2le()
            self.epsloadi1 = self._io.read_s2le()
            self.epsadcbatv2 = self._io.read_s2le()
            self.epsboostini2 = self._io.read_s2le()
            self.epsrail1 = self._io.read_s2le()
            self.epsrail2 = self._io.read_s2le()
            self.epstoppanelv = self._io.read_s2le()
            self.epstoppaneli = self._io.read_s2le()
            self.epst1 = self._io.read_s2le()
            self.epst2 = self._io.read_s2le()
            self.xposv = self._io.read_s2le()
            self.xposi = self._io.read_s2le()
            self.xpost1 = self._io.read_s2le()
            self.yposv = self._io.read_s2le()
            self.yposi = self._io.read_s2le()
            self.ypost1 = self._io.read_s2le()
            self.xnegv = self._io.read_s2le()
            self.xnegi = self._io.read_s2le()
            self.xnegt1 = self._io.read_s2le()
            self.ynegv = self._io.read_s2le()
            self.ynegi = self._io.read_s2le()
            self.ynegt1 = self._io.read_s2le()
            self.znegv = self._io.read_s2le()
            self.znegi = self._io.read_s2le()
            self.znegt1 = self._io.read_s2le()
            self.zpost = self._io.read_s2le()
            self.cdhtime = self._io.read_u8le()
            self.swcdhlastreboot = self._io.read_u8le()
            self.swsequence = self._io.read_u2le()
            self.outreachmessage = (self._io.read_bytes(48)).decode(u"ASCII")


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



