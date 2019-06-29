# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Entrysat(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field monitor: ax25_frame.payload.ax25_info.data_monitor
    :field packet_id: ax25_frame.payload.ax25_info.pus_packet.tm_packet.packet_id
    :field packet_seq_ctl: ax25_frame.payload.ax25_info.pus_packet.tm_packet.packet_seq_ctl
    :field packet_length: ax25_frame.payload.ax25_info.pus_packet.tm_packet.packet_length
    :field service: ax25_frame.payload.ax25_info.pus_packet.tm_packet.service
    :field subservice: ax25_frame.payload.ax25_info.pus_packet.tm_packet.subservice
    :field sid: ax25_frame.payload.ax25_info.pus_packet.tm_packet.sid
    :field mode: ax25_frame.payload.ax25_info.pus_packet.tm_packet.mode
    :field eps_vbatt: ax25_frame.payload.ax25_info.pus_packet.tm_packet.eps_vbatt
    :field eps_batt_vcurrent: ax25_frame.payload.ax25_info.pus_packet.tm_packet.eps_batt_vcurrent
    :field eps_3v3_current: ax25_frame.payload.ax25_info.pus_packet.tm_packet.eps_3v3_current
    :field eps_5v_current: ax25_frame.payload.ax25_info.pus_packet.tm_packet.eps_5v_current
    :field trx_temp: ax25_frame.payload.ax25_info.pus_packet.tm_packet.trx_temp
    :field eps_temp: ax25_frame.payload.ax25_info.pus_packet.tm_packet.eps_temp
    :field batt_temp: ax25_frame.payload.ax25_info.pus_packet.tm_packet.batt_temp
    :field frame_status: ax25_frame.payload.ax25_info.pus_packet.tm_packet.frame_status
    :field timestamp: ax25_frame.payload.ax25_info.pus_packet.tm_packet.timestamp
    :field clock: ax25_frame.payload.ax25_info.pus_packet.tm_packet.clock
    
    
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


    class PusPacketT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp_unused = self._io.read_u4be()
            self.tm_packet = self._root.TmPacketT(self._io, self, self._root)


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


    class TmPacketT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packet_id = self._io.read_u2be()
            self.packet_seq_ctl = self._io.read_u2be()
            self.packet_length = self._io.read_u2be()
            self.spare_tm = self._io.read_u1()
            self.service = self._io.read_u1()
            self.subservice = self._io.read_u1()
            self.clock_array = [None] * (5)
            for i in range(5):
                self.clock_array[i] = self._io.read_u1()

            self.sid = self._io.read_u1()
            self.mode = self._io.read_u1()
            self.eps_vbatt = self._io.read_u1()
            self.eps_batt_vcurrent = self._io.read_u1()
            self.eps_3v3_current = self._io.read_u1()
            self.eps_5v_current = self._io.read_u1()
            self.trx_temp = self._io.read_u1()
            self.eps_temp = self._io.read_u1()
            self.batt_temp = self._io.read_u1()
            self.crc = self._io.read_u2be()
            self.frame_status = self._io.read_u1()
            self.timestamp = self._io.read_u4le()

        @property
        def clock(self):
            if hasattr(self, '_m_clock'):
                return self._m_clock if hasattr(self, '_m_clock') else None

            self._m_clock = (((((((self.clock_array[0] * 256) * 256) * 256) + ((self.clock_array[1] * 256) * 256)) + (self.clock_array[2] * 256)) + self.clock_array[3]) + (self.clock_array[4] / 256.0))
            return self._m_clock if hasattr(self, '_m_clock') else None


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
            self.pus_packet = self._root.PusPacketT(self._io, self, self._root)



