# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Cubesatsim(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field data_type: ax25_frame.payload.ax25_info.data_type
    :field channel_1a_val: ax25_frame.payload.ax25_info.payload.channel_1a_val
    :field channel_1b_val: ax25_frame.payload.ax25_info.payload.channel_1b_val
    :field channel_1c_val: ax25_frame.payload.ax25_info.payload.channel_1c_val
    :field channel_1d_val: ax25_frame.payload.ax25_info.payload.channel_1d_val
    :field channel_2a_val: ax25_frame.payload.ax25_info.payload.channel_2a_val
    :field channel_2b_val: ax25_frame.payload.ax25_info.payload.channel_2b_val
    :field channel_2c_val: ax25_frame.payload.ax25_info.payload.channel_2c_val
    :field channel_2d_val: ax25_frame.payload.ax25_info.payload.channel_2d_val
    :field channel_3a_val: ax25_frame.payload.ax25_info.payload.channel_3a_val
    :field channel_3b_val: ax25_frame.payload.ax25_info.payload.channel_3b_val
    :field channel_3c_val: ax25_frame.payload.ax25_info.payload.channel_3c_val
    :field channel_3d_val: ax25_frame.payload.ax25_info.payload.channel_3d_val
    :field channel_4a_val: ax25_frame.payload.ax25_info.payload.channel_4a_val
    :field channel_4b_val: ax25_frame.payload.ax25_info.payload.channel_4b_val
    :field channel_4c_val: ax25_frame.payload.ax25_info.payload.channel_4c_val
    :field channel_4d_val: ax25_frame.payload.ax25_info.payload.channel_4d_val
    :field channel_5a_val: ax25_frame.payload.ax25_info.payload.channel_5a_val
    :field channel_5b_val: ax25_frame.payload.ax25_info.payload.channel_5b_val
    :field channel_5c_val: ax25_frame.payload.ax25_info.payload.channel_5c_val
    :field channel_5d_val: ax25_frame.payload.ax25_info.payload.channel_5d_val
    :field channel_6a_val: ax25_frame.payload.ax25_info.payload.channel_6a_val
    :field channel_6b_val: ax25_frame.payload.ax25_info.payload.channel_6b_val
    :field channel_6c_val: ax25_frame.payload.ax25_info.payload.channel_6c_val
    :field channel_6d_val: ax25_frame.payload.ax25_info.payload.channel_6d_val
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
            self.ax25_info = self._root.Data(io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class Data(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data_type = self._io.read_u2be()
            _on = self.data_type
            if _on == 26729:
                self.payload = self._root.Ao7(self._io, self, self._root)
            else:
                self.payload = self._root.Ao7(self._io, self, self._root)


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


    class Ao7(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao_7_magic = self._io.ensure_fixed_contents(b"\x20\x68\x69\x20")
            self.channel_1a_id = self._io.ensure_fixed_contents(b"\x31")
            self.channel_1a_val_raw = [None] * (2)
            for i in range(2):
                self.channel_1a_val_raw[i] = self._io.read_u1()

            self.delim_1a = self._io.read_bytes(1)
            self.channel_1b_id = self._io.ensure_fixed_contents(b"\x31")
            self.channel_1b_val_raw = [None] * (2)
            for i in range(2):
                self.channel_1b_val_raw[i] = self._io.read_u1()

            self.delim_1b = self._io.read_bytes(1)
            self.channel_1c_id = self._io.ensure_fixed_contents(b"\x31")
            self.channel_1c_val_raw = [None] * (2)
            for i in range(2):
                self.channel_1c_val_raw[i] = self._io.read_u1()

            self.delim_1c = self._io.read_bytes(1)
            self.channel_1d_id = self._io.ensure_fixed_contents(b"\x31")
            self.channel_1d_val_raw = [None] * (2)
            for i in range(2):
                self.channel_1d_val_raw[i] = self._io.read_u1()

            self.delim_1d = self._io.read_bytes(1)
            self.channel_2a_id = self._io.ensure_fixed_contents(b"\x32")
            self.channel_2a_val_raw = [None] * (2)
            for i in range(2):
                self.channel_2a_val_raw[i] = self._io.read_u1()

            self.delim_2a = self._io.read_bytes(1)
            self.channel_2b_id = self._io.ensure_fixed_contents(b"\x32")
            self.channel_2b_val_raw = [None] * (2)
            for i in range(2):
                self.channel_2b_val_raw[i] = self._io.read_u1()

            self.delim_2b = self._io.read_bytes(1)
            self.channel_2c_id = self._io.ensure_fixed_contents(b"\x32")
            self.channel_2c_val_raw = [None] * (2)
            for i in range(2):
                self.channel_2c_val_raw[i] = self._io.read_u1()

            self.delim_2c = self._io.read_bytes(1)
            self.channel_2d_id = self._io.ensure_fixed_contents(b"\x32")
            self.channel_2d_val_raw = [None] * (2)
            for i in range(2):
                self.channel_2d_val_raw[i] = self._io.read_u1()

            self.delim_2d = self._io.read_bytes(1)
            self.channel_3a_id = self._io.ensure_fixed_contents(b"\x33")
            self.channel_3a_val_raw = [None] * (2)
            for i in range(2):
                self.channel_3a_val_raw[i] = self._io.read_u1()

            self.delim_3a = self._io.read_bytes(1)
            self.channel_3b_id = self._io.ensure_fixed_contents(b"\x33")
            self.channel_3b_val_raw = [None] * (2)
            for i in range(2):
                self.channel_3b_val_raw[i] = self._io.read_u1()

            self.delim_3b = self._io.read_bytes(1)
            self.channel_3c_id = self._io.ensure_fixed_contents(b"\x33")
            self.channel_3c_val_raw = [None] * (2)
            for i in range(2):
                self.channel_3c_val_raw[i] = self._io.read_u1()

            self.delim_3c = self._io.read_bytes(1)
            self.channel_3d_id = self._io.ensure_fixed_contents(b"\x33")
            self.channel_3d_val_raw = [None] * (2)
            for i in range(2):
                self.channel_3d_val_raw[i] = self._io.read_u1()

            self.delim_3d = self._io.read_bytes(1)
            self.channel_4a_id = self._io.ensure_fixed_contents(b"\x34")
            self.channel_4a_val_raw = [None] * (2)
            for i in range(2):
                self.channel_4a_val_raw[i] = self._io.read_u1()

            self.delim_4a = self._io.read_bytes(1)
            self.channel_4b_id = self._io.ensure_fixed_contents(b"\x34")
            self.channel_4b_val_raw = [None] * (2)
            for i in range(2):
                self.channel_4b_val_raw[i] = self._io.read_u1()

            self.delim_4b = self._io.read_bytes(1)
            self.channel_4c_id = self._io.ensure_fixed_contents(b"\x34")
            self.channel_4c_val_raw = [None] * (2)
            for i in range(2):
                self.channel_4c_val_raw[i] = self._io.read_u1()

            self.delim_4c = self._io.read_bytes(1)
            self.channel_4d_id = self._io.ensure_fixed_contents(b"\x34")
            self.channel_4d_val_raw = [None] * (2)
            for i in range(2):
                self.channel_4d_val_raw[i] = self._io.read_u1()

            self.delim_4d = self._io.read_bytes(1)
            self.channel_5a_id = self._io.ensure_fixed_contents(b"\x35")
            self.channel_5a_val_raw = [None] * (2)
            for i in range(2):
                self.channel_5a_val_raw[i] = self._io.read_u1()

            self.delim_5a = self._io.read_bytes(1)
            self.channel_5b_id = self._io.ensure_fixed_contents(b"\x35")
            self.channel_5b_val_raw = [None] * (2)
            for i in range(2):
                self.channel_5b_val_raw[i] = self._io.read_u1()

            self.delim_5b = self._io.read_bytes(1)
            self.channel_5c_id = self._io.ensure_fixed_contents(b"\x35")
            self.channel_5c_val_raw = [None] * (2)
            for i in range(2):
                self.channel_5c_val_raw[i] = self._io.read_u1()

            self.delim_5c = self._io.read_bytes(1)
            self.channel_5d_id = self._io.ensure_fixed_contents(b"\x35")
            self.channel_5d_val_raw = [None] * (2)
            for i in range(2):
                self.channel_5d_val_raw[i] = self._io.read_u1()

            self.delim_5d = self._io.read_bytes(1)
            self.channel_6a_id = self._io.ensure_fixed_contents(b"\x36")
            self.channel_6a_val_raw = [None] * (2)
            for i in range(2):
                self.channel_6a_val_raw[i] = self._io.read_u1()

            self.delim_6a = self._io.read_bytes(1)
            self.channel_6b_id = self._io.ensure_fixed_contents(b"\x36")
            self.channel_6b_val_raw = [None] * (2)
            for i in range(2):
                self.channel_6b_val_raw[i] = self._io.read_u1()

            self.delim_6b = self._io.read_bytes(1)
            self.channel_6c_id = self._io.ensure_fixed_contents(b"\x36")
            self.channel_6c_val_raw = [None] * (2)
            for i in range(2):
                self.channel_6c_val_raw[i] = self._io.read_u1()

            self.delim_6c = self._io.read_bytes(1)
            self.channel_6d_id = self._io.ensure_fixed_contents(b"\x36")
            self.channel_6d_val_raw = [None] * (2)
            for i in range(2):
                self.channel_6d_val_raw[i] = self._io.read_u1()

            self.delim_6d = self._io.read_bytes(1)

        @property
        def channel_1d_val(self):
            """1970 - (20 * value) [mA]."""
            if hasattr(self, '_m_channel_1d_val'):
                return self._m_channel_1d_val if hasattr(self, '_m_channel_1d_val') else None

            self._m_channel_1d_val = (((self.channel_1d_val_raw[0] - 48) * 10) + (self.channel_1d_val_raw[1] - 48))
            return self._m_channel_1d_val if hasattr(self, '_m_channel_1d_val') else None

        @property
        def channel_1a_val(self):
            """value * 29.5 [mA]."""
            if hasattr(self, '_m_channel_1a_val'):
                return self._m_channel_1a_val if hasattr(self, '_m_channel_1a_val') else None

            self._m_channel_1a_val = (((self.channel_1a_val_raw[0] - 48) * 10) + (self.channel_1a_val_raw[1] - 48))
            return self._m_channel_1a_val if hasattr(self, '_m_channel_1a_val') else None

        @property
        def channel_6a_val(self):
            """value^2 / 1.56 [mA]."""
            if hasattr(self, '_m_channel_6a_val'):
                return self._m_channel_6a_val if hasattr(self, '_m_channel_6a_val') else None

            self._m_channel_6a_val = (((self.channel_6a_val_raw[0] - 48) * 10) + (self.channel_6a_val_raw[1] - 48))
            return self._m_channel_6a_val if hasattr(self, '_m_channel_6a_val') else None

        @property
        def channel_1c_val(self):
            """1970 - (20 * value) [mA]."""
            if hasattr(self, '_m_channel_1c_val'):
                return self._m_channel_1c_val if hasattr(self, '_m_channel_1c_val') else None

            self._m_channel_1c_val = (((self.channel_1c_val_raw[0] - 48) * 10) + (self.channel_1c_val_raw[1] - 48))
            return self._m_channel_1c_val if hasattr(self, '_m_channel_1c_val') else None

        @property
        def channel_4a_val(self):
            """95.8 - 1.48 * value [C]."""
            if hasattr(self, '_m_channel_4a_val'):
                return self._m_channel_4a_val if hasattr(self, '_m_channel_4a_val') else None

            self._m_channel_4a_val = (((self.channel_4a_val_raw[0] - 48) * 10) + (self.channel_4a_val_raw[1] - 48))
            return self._m_channel_4a_val if hasattr(self, '_m_channel_4a_val') else None

        @property
        def channel_5a_val(self):
            """95.8 - 1.48 * value [C]."""
            if hasattr(self, '_m_channel_5a_val'):
                return self._m_channel_5a_val if hasattr(self, '_m_channel_5a_val') else None

            self._m_channel_5a_val = (((self.channel_5a_val_raw[0] - 48) * 10) + (self.channel_5a_val_raw[1] - 48))
            return self._m_channel_5a_val if hasattr(self, '_m_channel_5a_val') else None

        @property
        def channel_2b_val(self):
            """8 * (1 - 0.01 * value)^2 [W]."""
            if hasattr(self, '_m_channel_2b_val'):
                return self._m_channel_2b_val if hasattr(self, '_m_channel_2b_val') else None

            self._m_channel_2b_val = (((self.channel_2b_val_raw[0] - 48) * 10) + (self.channel_2b_val_raw[1] - 48))
            return self._m_channel_2b_val if hasattr(self, '_m_channel_2b_val') else None

        @property
        def channel_6b_val(self):
            """0.1 * value^2 + 35 [mA]."""
            if hasattr(self, '_m_channel_6b_val'):
                return self._m_channel_6b_val if hasattr(self, '_m_channel_6b_val') else None

            self._m_channel_6b_val = (((self.channel_6b_val_raw[0] - 48) * 10) + (self.channel_6b_val_raw[1] - 48))
            return self._m_channel_6b_val if hasattr(self, '_m_channel_6b_val') else None

        @property
        def channel_6c_val(self):
            """0.041 * value^2 [mA]."""
            if hasattr(self, '_m_channel_6c_val'):
                return self._m_channel_6c_val if hasattr(self, '_m_channel_6c_val') else None

            self._m_channel_6c_val = (((self.channel_6c_val_raw[0] - 48) * 10) + (self.channel_6c_val_raw[1] - 48))
            return self._m_channel_6c_val if hasattr(self, '_m_channel_6c_val') else None

        @property
        def channel_3a_val(self):
            """0.1 * value + 6.4 [V]."""
            if hasattr(self, '_m_channel_3a_val'):
                return self._m_channel_3a_val if hasattr(self, '_m_channel_3a_val') else None

            self._m_channel_3a_val = (((self.channel_3a_val_raw[0] - 48) * 10) + (self.channel_3a_val_raw[1] - 48))
            return self._m_channel_3a_val if hasattr(self, '_m_channel_3a_val') else None

        @property
        def channel_2d_val(self):
            """40 * (value - 50) [mA]."""
            if hasattr(self, '_m_channel_2d_val'):
                return self._m_channel_2d_val if hasattr(self, '_m_channel_2d_val') else None

            self._m_channel_2d_val = (((self.channel_2d_val_raw[0] - 48) * 10) + (self.channel_2d_val_raw[1] - 48))
            return self._m_channel_2d_val if hasattr(self, '_m_channel_2d_val') else None

        @property
        def channel_5d_val(self):
            """11 + 0.82 * value [mA]."""
            if hasattr(self, '_m_channel_5d_val'):
                return self._m_channel_5d_val if hasattr(self, '_m_channel_5d_val') else None

            self._m_channel_5d_val = (((self.channel_5d_val_raw[0] - 48) * 10) + (self.channel_5d_val_raw[1] - 48))
            return self._m_channel_5d_val if hasattr(self, '_m_channel_5d_val') else None

        @property
        def channel_2c_val(self):
            """15.16 * value [h]."""
            if hasattr(self, '_m_channel_2c_val'):
                return self._m_channel_2c_val if hasattr(self, '_m_channel_2c_val') else None

            self._m_channel_2c_val = (((self.channel_2c_val_raw[0] - 48) * 10) + (self.channel_2c_val_raw[1] - 48))
            return self._m_channel_2c_val if hasattr(self, '_m_channel_2c_val') else None

        @property
        def channel_6d_val(self):
            """0.01 * value."""
            if hasattr(self, '_m_channel_6d_val'):
                return self._m_channel_6d_val if hasattr(self, '_m_channel_6d_val') else None

            self._m_channel_6d_val = (((self.channel_6d_val_raw[0] - 48) * 10) + (self.channel_6d_val_raw[1] - 48))
            return self._m_channel_6d_val if hasattr(self, '_m_channel_6d_val') else None

        @property
        def channel_1b_val(self):
            """1970 - (20 * value) [mA]."""
            if hasattr(self, '_m_channel_1b_val'):
                return self._m_channel_1b_val if hasattr(self, '_m_channel_1b_val') else None

            self._m_channel_1b_val = (((self.channel_1b_val_raw[0] - 48) * 10) + (self.channel_1b_val_raw[1] - 48))
            return self._m_channel_1b_val if hasattr(self, '_m_channel_1b_val') else None

        @property
        def channel_3b_val(self):
            """0.1 * value [V]."""
            if hasattr(self, '_m_channel_3b_val'):
                return self._m_channel_3b_val if hasattr(self, '_m_channel_3b_val') else None

            self._m_channel_3b_val = (((self.channel_3b_val_raw[0] - 48) * 10) + (self.channel_3b_val_raw[1] - 48))
            return self._m_channel_3b_val if hasattr(self, '_m_channel_3b_val') else None

        @property
        def channel_4c_val(self):
            """95.8 - 1.48 * value [C]."""
            if hasattr(self, '_m_channel_4c_val'):
                return self._m_channel_4c_val if hasattr(self, '_m_channel_4c_val') else None

            self._m_channel_4c_val = (((self.channel_4c_val_raw[0] - 48) * 10) + (self.channel_4c_val_raw[1] - 48))
            return self._m_channel_4c_val if hasattr(self, '_m_channel_4c_val') else None

        @property
        def channel_5c_val(self):
            """95.8 - 1.48 * value [C]."""
            if hasattr(self, '_m_channel_5c_val'):
                return self._m_channel_5c_val if hasattr(self, '_m_channel_5c_val') else None

            self._m_channel_5c_val = (((self.channel_5c_val_raw[0] - 48) * 10) + (self.channel_5c_val_raw[1] - 48))
            return self._m_channel_5c_val if hasattr(self, '_m_channel_5c_val') else None

        @property
        def channel_4b_val(self):
            """95.8 - 1.48 * value [C]."""
            if hasattr(self, '_m_channel_4b_val'):
                return self._m_channel_4b_val if hasattr(self, '_m_channel_4b_val') else None

            self._m_channel_4b_val = (((self.channel_4b_val_raw[0] - 48) * 10) + (self.channel_4b_val_raw[1] - 48))
            return self._m_channel_4b_val if hasattr(self, '_m_channel_4b_val') else None

        @property
        def channel_3d_val(self):
            """95.8 - 1.48 * value [C]."""
            if hasattr(self, '_m_channel_3d_val'):
                return self._m_channel_3d_val if hasattr(self, '_m_channel_3d_val') else None

            self._m_channel_3d_val = (((self.channel_3d_val_raw[0] - 48) * 10) + (self.channel_3d_val_raw[1] - 48))
            return self._m_channel_3d_val if hasattr(self, '_m_channel_3d_val') else None

        @property
        def channel_2a_val(self):
            """1970 - (20 * value) [mA]."""
            if hasattr(self, '_m_channel_2a_val'):
                return self._m_channel_2a_val if hasattr(self, '_m_channel_2a_val') else None

            self._m_channel_2a_val = (((self.channel_2a_val_raw[0] - 48) * 10) + (self.channel_2a_val_raw[1] - 48))
            return self._m_channel_2a_val if hasattr(self, '_m_channel_2a_val') else None

        @property
        def channel_4d_val(self):
            """95.8 - 1.48 * value [C]."""
            if hasattr(self, '_m_channel_4d_val'):
                return self._m_channel_4d_val if hasattr(self, '_m_channel_4d_val') else None

            self._m_channel_4d_val = (((self.channel_4d_val_raw[0] - 48) * 10) + (self.channel_4d_val_raw[1] - 48))
            return self._m_channel_4d_val if hasattr(self, '_m_channel_4d_val') else None

        @property
        def channel_3c_val(self):
            """0.15 * value [V]."""
            if hasattr(self, '_m_channel_3c_val'):
                return self._m_channel_3c_val if hasattr(self, '_m_channel_3c_val') else None

            self._m_channel_3c_val = (((self.channel_3c_val_raw[0] - 48) * 10) + (self.channel_3c_val_raw[1] - 48))
            return self._m_channel_3c_val if hasattr(self, '_m_channel_3c_val') else None

        @property
        def channel_5b_val(self):
            """11.67 * value [mA]."""
            if hasattr(self, '_m_channel_5b_val'):
                return self._m_channel_5b_val if hasattr(self, '_m_channel_5b_val') else None

            self._m_channel_5b_val = (((self.channel_5b_val_raw[0] - 48) * 10) + (self.channel_5b_val_raw[1] - 48))
            return self._m_channel_5b_val if hasattr(self, '_m_channel_5b_val') else None


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



