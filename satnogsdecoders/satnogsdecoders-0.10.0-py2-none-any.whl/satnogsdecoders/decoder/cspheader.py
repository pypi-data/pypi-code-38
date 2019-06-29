# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Cspheader(KaitaiStruct):
    """
    .. seealso::
       Source - https://en.wikipedia.org/wiki/Cubesat_Space_Protocol
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.csp_header = self._root.CspHeaderT(self._io, self, self._root)
        self.csp_data = self._root.CspDataT(self._io, self, self._root)

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


    class CspDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_payload = self._io.read_bytes_full()



