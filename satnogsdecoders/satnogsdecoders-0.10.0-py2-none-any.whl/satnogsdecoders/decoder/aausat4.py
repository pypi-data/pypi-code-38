# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Aausat4(KaitaiStruct):
    """:field csp_hdr_crc: csp_header.crc
    :field csp_hdr_rdp: csp_header.rdp
    :field csp_hdr_xtea: csp_header.xtea
    :field csp_hdr_hmac: csp_header.hmac
    :field csp_hdr_src_port: csp_header.src_port
    :field csp_hdr_dst_port: csp_header.dst_port
    :field csp_hdr_destination: csp_header.destination
    :field csp_hdr_source: csp_header.source
    :field csp_hdr_priority: csp_header.priority
    :field subsystems_valid: csp_data.csp_payload.valid
    :field eps_boot_count: csp_data.csp_payload.eps.boot_count
    :field eps_boot_cause: csp_data.csp_payload.eps.boot_cause
    :field eps_uptime: csp_data.csp_payload.eps.uptime
    :field eps_rt_clock: csp_data.csp_payload.eps.rt_clock
    :field eps_ping_status: csp_data.csp_payload.eps.ping_status
    :field eps_subsystem_selfstatus: csp_data.csp_payload.eps.subsystem_selfstatus
    :field eps_battery_voltage: csp_data.csp_payload.eps.battery_voltage
    :field eps_cell_diff: csp_data.csp_payload.eps.cell_diff
    :field eps_battery_current: csp_data.csp_payload.eps.battery_current
    :field eps_solar_power: csp_data.csp_payload.eps.solar_power
    :field eps_temp: csp_data.csp_payload.eps.temp
    :field eps_pa_temp: csp_data.csp_payload.eps.pa_temp
    :field eps_main_voltage: csp_data.csp_payload.eps.main_voltage
    :field com_boot_count: csp_data.csp_payload.com.boot_count
    :field com_boot_cause: csp_data.csp_payload.com.boot_cause
    
    .. seealso::
       Source - https://github.com/aausat/aausat4_beacon_parser/blob/master/beacon.py
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.csp_header = self._root.CspHeaderT(self._io, self, self._root)
        self.csp_data = self._root.CspDataT(self._io, self, self._root)

    class ComT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.boot_count_raw = self._io.read_u2be()

        @property
        def boot_count(self):
            if hasattr(self, '_m_boot_count'):
                return self._m_boot_count if hasattr(self, '_m_boot_count') else None

            self._m_boot_count = (self.boot_count_raw & 8191)
            return self._m_boot_count if hasattr(self, '_m_boot_count') else None

        @property
        def boot_cause(self):
            if hasattr(self, '_m_boot_cause'):
                return self._m_boot_cause if hasattr(self, '_m_boot_cause') else None

            self._m_boot_cause = ((self.boot_count_raw & 57344) >> 13)
            return self._m_boot_cause if hasattr(self, '_m_boot_cause') else None


    class EpsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.boot_count_raw = self._io.read_u2be()
            self.uptime = self._io.read_u4be()
            self.rt_clock = self._io.read_u4be()
            self.ping_status = self._io.read_u1()
            self.subsystem_selfstatus = self._io.read_u2be()
            self.battery_voltage = self._io.read_u1()
            self.cell_diff = self._io.read_s1()
            self.battery_current = self._io.read_s1()
            self.solar_power = self._io.read_u1()
            self.temp = self._io.read_s1()
            self.pa_temp = self._io.read_s1()
            self.main_voltage = self._io.read_s1()

        @property
        def boot_count(self):
            if hasattr(self, '_m_boot_count'):
                return self._m_boot_count if hasattr(self, '_m_boot_count') else None

            self._m_boot_count = (self.boot_count_raw & 8191)
            return self._m_boot_count if hasattr(self, '_m_boot_count') else None

        @property
        def boot_cause(self):
            if hasattr(self, '_m_boot_cause'):
                return self._m_boot_cause if hasattr(self, '_m_boot_cause') else None

            self._m_boot_cause = ((self.boot_count_raw & 57344) >> 13)
            return self._m_boot_cause if hasattr(self, '_m_boot_cause') else None


    class Adcs1T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes(7)


    class CspDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.frame_length
            if _on == 88:
                self.csp_payload = self._root.Aausat4BeaconT(self._io, self, self._root)

        @property
        def frame_length(self):
            if hasattr(self, '_m_frame_length'):
                return self._m_frame_length if hasattr(self, '_m_frame_length') else None

            self._m_frame_length = self._io.size()
            return self._m_frame_length if hasattr(self, '_m_frame_length') else None


    class Ais2T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes(20)


    class Aausat4BeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.valid = self._io.read_u1()
            self._raw_eps = self._io.read_bytes(20)
            io = KaitaiStream(BytesIO(self._raw_eps))
            self.eps = self._root.EpsT(io, self, self._root)
            self._raw_com = self._io.read_bytes(10)
            io = KaitaiStream(BytesIO(self._raw_com))
            self.com = self._root.ComT(io, self, self._root)
            self.adcs1 = self._root.Adcs1T(self._io, self, self._root)
            self.adcs2 = self._root.Adcs2T(self._io, self, self._root)
            self.ais1 = self._root.Ais1T(self._io, self, self._root)
            self.ais2 = self._root.Ais2T(self._io, self, self._root)
            self.unparsed = self._io.read_bytes_full()


    class CspHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_flags = [None] * (4)
            for i in range(4):
                self.csp_flags[i] = self._io.read_u1()


        @property
        def source(self):
            if hasattr(self, '_m_source'):
                return self._m_source if hasattr(self, '_m_source') else None

            self._m_source = ((self.csp_flags[3] >> 1) & 31)
            return self._m_source if hasattr(self, '_m_source') else None

        @property
        def rdp(self):
            if hasattr(self, '_m_rdp'):
                return self._m_rdp if hasattr(self, '_m_rdp') else None

            self._m_rdp = ((self.csp_flags[0] >> 1) & 1)
            return self._m_rdp if hasattr(self, '_m_rdp') else None

        @property
        def src_port(self):
            if hasattr(self, '_m_src_port'):
                return self._m_src_port if hasattr(self, '_m_src_port') else None

            self._m_src_port = (self.csp_flags[1] & 63)
            return self._m_src_port if hasattr(self, '_m_src_port') else None

        @property
        def destination(self):
            if hasattr(self, '_m_destination'):
                return self._m_destination if hasattr(self, '_m_destination') else None

            self._m_destination = (((self.csp_flags[2] | (self.csp_flags[3] << 8)) >> 4) & 31)
            return self._m_destination if hasattr(self, '_m_destination') else None

        @property
        def dst_port(self):
            if hasattr(self, '_m_dst_port'):
                return self._m_dst_port if hasattr(self, '_m_dst_port') else None

            self._m_dst_port = (((self.csp_flags[1] | (self.csp_flags[2] << 8)) >> 6) & 63)
            return self._m_dst_port if hasattr(self, '_m_dst_port') else None

        @property
        def priority(self):
            if hasattr(self, '_m_priority'):
                return self._m_priority if hasattr(self, '_m_priority') else None

            self._m_priority = (self.csp_flags[3] >> 6)
            return self._m_priority if hasattr(self, '_m_priority') else None

        @property
        def reserved(self):
            if hasattr(self, '_m_reserved'):
                return self._m_reserved if hasattr(self, '_m_reserved') else None

            self._m_reserved = (self.csp_flags[0] >> 4)
            return self._m_reserved if hasattr(self, '_m_reserved') else None

        @property
        def xtea(self):
            if hasattr(self, '_m_xtea'):
                return self._m_xtea if hasattr(self, '_m_xtea') else None

            self._m_xtea = ((self.csp_flags[0] >> 2) & 1)
            return self._m_xtea if hasattr(self, '_m_xtea') else None

        @property
        def hmac(self):
            if hasattr(self, '_m_hmac'):
                return self._m_hmac if hasattr(self, '_m_hmac') else None

            self._m_hmac = ((self.csp_flags[0] >> 3) & 1)
            return self._m_hmac if hasattr(self, '_m_hmac') else None

        @property
        def crc(self):
            if hasattr(self, '_m_crc'):
                return self._m_crc if hasattr(self, '_m_crc') else None

            self._m_crc = (self.csp_flags[0] & 1)
            return self._m_crc if hasattr(self, '_m_crc') else None


    class Adcs2T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes(6)


    class Ais1T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unparsed = self._io.read_bytes(20)



