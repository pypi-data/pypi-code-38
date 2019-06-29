# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Eshail2(KaitaiStruct):
    """:field ao40_beacon_type: ao40_frame.ao40_coding.ao40_beacon_type
    :field ao40_message_line1: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line1
    :field ao40_message_line2: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line2
    :field ao40_message_line3: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line3
    :field ao40_message_line4: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line4
    :field ao40_message_line5: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line5
    :field ao40_message_line6: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line6
    :field ao40_message_line7: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line7
    :field ao40_message_line8: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line8
    :field uptime: ao40_frame.ao40_coding.ao40_beacon_data.uptime
    :field commands: ao40_frame.ao40_coding.ao40_beacon_data.commands
    :field leila_req: ao40_frame.ao40_coding.ao40_beacon_data.leila_req
    :field leila_act: ao40_frame.ao40_coding.ao40_beacon_data.leila_act
    :field temperature: ao40_frame.ao40_coding.ao40_beacon_data.temperature
    :field volt_1: ao40_frame.ao40_coding.ao40_beacon_data.volt_1
    :field volt_2: ao40_frame.ao40_coding.ao40_beacon_data.volt_2
    :field volt_3: ao40_frame.ao40_coding.ao40_beacon_data.volt_3
    :field volt_4: ao40_frame.ao40_coding.ao40_beacon_data.volt_4
    :field volt_5: ao40_frame.ao40_coding.ao40_beacon_data.volt_5
    :field volt_6: ao40_frame.ao40_coding.ao40_beacon_data.volt_6
    :field volt_7: ao40_frame.ao40_coding.ao40_beacon_data.volt_7
    :field volt_8: ao40_frame.ao40_coding.ao40_beacon_data.volt_8
    :field volt_9: ao40_frame.ao40_coding.ao40_beacon_data.volt_9
    
    .. seealso::
       Source - https://amsat-dl.org/wp-content/uploads/2019/01/tlmspec.pdf
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ao40_frame = self._root.Ao40Frame(self._io, self, self._root)

    class Ao40FecMessageSpare(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.frame_length
            if _on == 256:
                self.ao40_coding = self._root.Ao40FrameFec(self._io, self, self._root)
            elif _on == 514:
                self.ao40_coding = self._root.Ao40FrameUncoded(self._io, self, self._root)


    class Ao40CommandResponse(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line5 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line6 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line7 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line8 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40FrameUncoded(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.ao40_beacon_type
            if _on == 77:
                self.ao40_beacon_data = self._root.Ao40MessageSpare(self._io, self, self._root)
            elif _on == 69:
                self.ao40_beacon_data = self._root.Ao40MessageSpare(self._io, self, self._root)
            elif _on == 88:
                self.ao40_beacon_data = self._root.Ao40MessageSpare(self._io, self, self._root)
            elif _on == 78:
                self.ao40_beacon_data = self._root.Ao40MessageSpare(self._io, self, self._root)
            elif _on == 65:
                self.ao40_beacon_data = self._root.Ao40MessageSpare(self._io, self, self._root)
            elif _on == 76:
                self.ao40_beacon_data = self._root.Ao40MessageL(self._io, self, self._root)
            elif _on == 68:
                self.ao40_beacon_data = self._root.Ao40MessageSpare(self._io, self, self._root)
            elif _on == 75:
                self.ao40_beacon_data = self._root.Ao40MessageK(self._io, self, self._root)
            else:
                self.ao40_beacon_data = self._root.Ao40CommandResponse(self._io, self, self._root)
            self.crc = self._io.read_u2be()

        @property
        def ao40_beacon_type(self):
            if hasattr(self, '_m_ao40_beacon_type'):
                return self._m_ao40_beacon_type if hasattr(self, '_m_ao40_beacon_type') else None

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_ao40_beacon_type = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_ao40_beacon_type if hasattr(self, '_m_ao40_beacon_type') else None


    class Ao40FecMessageL(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40FrameFec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.ao40_beacon_type
            if _on == 77:
                self.ao40_beacon_data = self._root.Ao40FecMessageSpare(self._io, self, self._root)
            elif _on == 69:
                self.ao40_beacon_data = self._root.Ao40FecMessageSpare(self._io, self, self._root)
            elif _on == 88:
                self.ao40_beacon_data = self._root.Ao40FecMessageSpare(self._io, self, self._root)
            elif _on == 78:
                self.ao40_beacon_data = self._root.Ao40FecMessageSpare(self._io, self, self._root)
            elif _on == 65:
                self.ao40_beacon_data = self._root.Ao40FecMessageSpare(self._io, self, self._root)
            elif _on == 76:
                self.ao40_beacon_data = self._root.Ao40FecMessageL(self._io, self, self._root)
            elif _on == 68:
                self.ao40_beacon_data = self._root.Ao40FecMessageSpare(self._io, self, self._root)
            elif _on == 75:
                self.ao40_beacon_data = self._root.Ao40FecMessageK(self._io, self, self._root)
            else:
                self.ao40_beacon_data = self._root.Ao40FecCommandResponse(self._io, self, self._root)

        @property
        def ao40_beacon_type(self):
            if hasattr(self, '_m_ao40_beacon_type'):
                return self._m_ao40_beacon_type if hasattr(self, '_m_ao40_beacon_type') else None

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_ao40_beacon_type = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_ao40_beacon_type if hasattr(self, '_m_ao40_beacon_type') else None


    class Ao40MessageSpare(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line5 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line6 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line7 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line8 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40MessageL(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line5 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line6 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line7 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line8 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40FecMessageK(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")

        @property
        def tfl_str(self):
            if hasattr(self, '_m_tfl_str'):
                return self._m_tfl_str if hasattr(self, '_m_tfl_str') else None

            _pos = self._io.pos()
            self._io.seek(201)
            self._m_tfl_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_tfl_str if hasattr(self, '_m_tfl_str') else None

        @property
        def volts_str_9(self):
            if hasattr(self, '_m_volts_str_9'):
                return self._m_volts_str_9 if hasattr(self, '_m_volts_str_9') else None

            _pos = self._io.pos()
            self._io.seek(182)
            self._m_volts_str_9 = [None] * (3)
            for i in range(3):
                self._m_volts_str_9[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_9 if hasattr(self, '_m_volts_str_9') else None

        @property
        def leila_act(self):
            if hasattr(self, '_m_leila_act'):
                return self._m_leila_act if hasattr(self, '_m_leila_act') else None

            self._m_leila_act = self.leila_active_str > 48
            return self._m_leila_act if hasattr(self, '_m_leila_act') else None

        @property
        def volt_3(self):
            if hasattr(self, '_m_volt_3'):
                return self._m_volt_3 if hasattr(self, '_m_volt_3') else None

            self._m_volt_3 = (((self.volts_str_3[0] - 48) * 1.0) + ((self.volts_str_3[2] - 48) / 10.0))
            return self._m_volt_3 if hasattr(self, '_m_volt_3') else None

        @property
        def uptime_dd_str(self):
            if hasattr(self, '_m_uptime_dd_str'):
                return self._m_uptime_dd_str if hasattr(self, '_m_uptime_dd_str') else None

            _pos = self._io.pos()
            self._io.seek(71)
            self._m_uptime_dd_str = [None] * (2)
            for i in range(2):
                self._m_uptime_dd_str[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_uptime_dd_str if hasattr(self, '_m_uptime_dd_str') else None

        @property
        def volts_str_2(self):
            if hasattr(self, '_m_volts_str_2'):
                return self._m_volts_str_2 if hasattr(self, '_m_volts_str_2') else None

            _pos = self._io.pos()
            self._io.seek(154)
            self._m_volts_str_2 = [None] * (3)
            for i in range(3):
                self._m_volts_str_2[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_2 if hasattr(self, '_m_volts_str_2') else None

        @property
        def commands(self):
            if hasattr(self, '_m_commands'):
                return self._m_commands if hasattr(self, '_m_commands') else None

            self._m_commands = ((((((1 if self.commands_str[0] > 47 else 0) * (self.commands_str[0] - 48)) * 1000) + (((1 if self.commands_str[1] > 47 else 0) * (self.commands_str[1] - 48)) * 100)) + (((1 if self.commands_str[2] > 47 else 0) * (self.commands_str[2] - 48)) * 10)) + (self.commands_str[3] - 48))
            return self._m_commands if hasattr(self, '_m_commands') else None

        @property
        def volt_8(self):
            if hasattr(self, '_m_volt_8'):
                return self._m_volt_8 if hasattr(self, '_m_volt_8') else None

            self._m_volt_8 = (((self.volts_str_8[0] - 48) * 1.0) + ((self.volts_str_8[2] - 48) / 10.0))
            return self._m_volt_8 if hasattr(self, '_m_volt_8') else None

        @property
        def volts_str_8(self):
            if hasattr(self, '_m_volts_str_8'):
                return self._m_volts_str_8 if hasattr(self, '_m_volts_str_8') else None

            _pos = self._io.pos()
            self._io.seek(178)
            self._m_volts_str_8 = [None] * (3)
            for i in range(3):
                self._m_volts_str_8[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_8 if hasattr(self, '_m_volts_str_8') else None

        @property
        def volts_str_6(self):
            if hasattr(self, '_m_volts_str_6'):
                return self._m_volts_str_6 if hasattr(self, '_m_volts_str_6') else None

            _pos = self._io.pos()
            self._io.seek(170)
            self._m_volts_str_6 = [None] * (3)
            for i in range(3):
                self._m_volts_str_6[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_6 if hasattr(self, '_m_volts_str_6') else None

        @property
        def tfh_str(self):
            if hasattr(self, '_m_tfh_str'):
                return self._m_tfh_str if hasattr(self, '_m_tfh_str') else None

            _pos = self._io.pos()
            self._io.seek(222)
            self._m_tfh_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_tfh_str if hasattr(self, '_m_tfh_str') else None

        @property
        def volt_7(self):
            if hasattr(self, '_m_volt_7'):
                return self._m_volt_7 if hasattr(self, '_m_volt_7') else None

            self._m_volt_7 = (((self.volts_str_7[0] - 48) * 1.0) + ((self.volts_str_7[2] - 48) / 10.0))
            return self._m_volt_7 if hasattr(self, '_m_volt_7') else None

        @property
        def commands_str(self):
            if hasattr(self, '_m_commands_str'):
                return self._m_commands_str if hasattr(self, '_m_commands_str') else None

            _pos = self._io.pos()
            self._io.seek(90)
            self._m_commands_str = [None] * (4)
            for i in range(4):
                self._m_commands_str[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_commands_str if hasattr(self, '_m_commands_str') else None

        @property
        def volts_str_7(self):
            if hasattr(self, '_m_volts_str_7'):
                return self._m_volts_str_7 if hasattr(self, '_m_volts_str_7') else None

            _pos = self._io.pos()
            self._io.seek(174)
            self._m_volts_str_7 = [None] * (3)
            for i in range(3):
                self._m_volts_str_7[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_7 if hasattr(self, '_m_volts_str_7') else None

        @property
        def hth_str(self):
            if hasattr(self, '_m_hth_str'):
                return self._m_hth_str if hasattr(self, '_m_hth_str') else None

            _pos = self._io.pos()
            self._io.seek(245)
            self._m_hth_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_hth_str if hasattr(self, '_m_hth_str') else None

        @property
        def temperature(self):
            if hasattr(self, '_m_temperature'):
                return self._m_temperature if hasattr(self, '_m_temperature') else None

            self._m_temperature = ((((1 if self.temp_str[0] > 47 else 0) * (self.temp_str[0] - 48)) * 10) + (self.temp_str[1] - 48))
            return self._m_temperature if hasattr(self, '_m_temperature') else None

        @property
        def uptime_hh_str(self):
            if hasattr(self, '_m_uptime_hh_str'):
                return self._m_uptime_hh_str if hasattr(self, '_m_uptime_hh_str') else None

            _pos = self._io.pos()
            self._io.seek(75)
            self._m_uptime_hh_str = [None] * (2)
            for i in range(2):
                self._m_uptime_hh_str[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_uptime_hh_str if hasattr(self, '_m_uptime_hh_str') else None

        @property
        def volt_9(self):
            if hasattr(self, '_m_volt_9'):
                return self._m_volt_9 if hasattr(self, '_m_volt_9') else None

            self._m_volt_9 = (((self.volts_str_9[0] - 48) * 1.0) + ((self.volts_str_9[2] - 48) / 10.0))
            return self._m_volt_9 if hasattr(self, '_m_volt_9') else None

        @property
        def volts_str_4(self):
            if hasattr(self, '_m_volts_str_4'):
                return self._m_volts_str_4 if hasattr(self, '_m_volts_str_4') else None

            _pos = self._io.pos()
            self._io.seek(162)
            self._m_volts_str_4 = [None] * (3)
            for i in range(3):
                self._m_volts_str_4[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_4 if hasattr(self, '_m_volts_str_4') else None

        @property
        def volt_2(self):
            if hasattr(self, '_m_volt_2'):
                return self._m_volt_2 if hasattr(self, '_m_volt_2') else None

            self._m_volt_2 = (((self.volts_str_2[0] - 48) * 1.0) + ((self.volts_str_2[2] - 48) / 10.0))
            return self._m_volt_2 if hasattr(self, '_m_volt_2') else None

        @property
        def leila_request_str(self):
            if hasattr(self, '_m_leila_request_str'):
                return self._m_leila_request_str if hasattr(self, '_m_leila_request_str') else None

            _pos = self._io.pos()
            self._io.seek(110)
            self._m_leila_request_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_leila_request_str if hasattr(self, '_m_leila_request_str') else None

        @property
        def leila_req(self):
            if hasattr(self, '_m_leila_req'):
                return self._m_leila_req if hasattr(self, '_m_leila_req') else None

            self._m_leila_req = self.leila_request_str > 48
            return self._m_leila_req if hasattr(self, '_m_leila_req') else None

        @property
        def volt_4(self):
            if hasattr(self, '_m_volt_4'):
                return self._m_volt_4 if hasattr(self, '_m_volt_4') else None

            self._m_volt_4 = (((self.volts_str_4[0] - 48) * 1.0) + ((self.volts_str_4[2] - 48) / 10.0))
            return self._m_volt_4 if hasattr(self, '_m_volt_4') else None

        @property
        def leila_active_str(self):
            if hasattr(self, '_m_leila_active_str'):
                return self._m_leila_active_str if hasattr(self, '_m_leila_active_str') else None

            _pos = self._io.pos()
            self._io.seek(127)
            self._m_leila_active_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_leila_active_str if hasattr(self, '_m_leila_active_str') else None

        @property
        def volts_str_5(self):
            if hasattr(self, '_m_volts_str_5'):
                return self._m_volts_str_5 if hasattr(self, '_m_volts_str_5') else None

            _pos = self._io.pos()
            self._io.seek(166)
            self._m_volts_str_5 = [None] * (3)
            for i in range(3):
                self._m_volts_str_5[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_5 if hasattr(self, '_m_volts_str_5') else None

        @property
        def volt_1(self):
            if hasattr(self, '_m_volt_1'):
                return self._m_volt_1 if hasattr(self, '_m_volt_1') else None

            self._m_volt_1 = (((self.volts_str_1[0] - 48) * 1.0) + ((self.volts_str_1[2] - 48) / 10.0))
            return self._m_volt_1 if hasattr(self, '_m_volt_1') else None

        @property
        def uptime_mm_str(self):
            if hasattr(self, '_m_uptime_mm_str'):
                return self._m_uptime_mm_str if hasattr(self, '_m_uptime_mm_str') else None

            _pos = self._io.pos()
            self._io.seek(79)
            self._m_uptime_mm_str = [None] * (2)
            for i in range(2):
                self._m_uptime_mm_str[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_uptime_mm_str if hasattr(self, '_m_uptime_mm_str') else None

        @property
        def tfe_str(self):
            if hasattr(self, '_m_tfe_str'):
                return self._m_tfe_str if hasattr(self, '_m_tfe_str') else None

            _pos = self._io.pos()
            self._io.seek(212)
            self._m_tfe_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_tfe_str if hasattr(self, '_m_tfe_str') else None

        @property
        def temp_str(self):
            if hasattr(self, '_m_temp_str'):
                return self._m_temp_str if hasattr(self, '_m_temp_str') else None

            _pos = self._io.pos()
            self._io.seek(134)
            self._m_temp_str = [None] * (2)
            for i in range(2):
                self._m_temp_str[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_temp_str if hasattr(self, '_m_temp_str') else None

        @property
        def volts_str_3(self):
            if hasattr(self, '_m_volts_str_3'):
                return self._m_volts_str_3 if hasattr(self, '_m_volts_str_3') else None

            _pos = self._io.pos()
            self._io.seek(158)
            self._m_volts_str_3 = [None] * (3)
            for i in range(3):
                self._m_volts_str_3[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_3 if hasattr(self, '_m_volts_str_3') else None

        @property
        def volt_6(self):
            if hasattr(self, '_m_volt_6'):
                return self._m_volt_6 if hasattr(self, '_m_volt_6') else None

            self._m_volt_6 = (((self.volts_str_6[0] - 48) * 1.0) + ((self.volts_str_6[2] - 48) / 10.0))
            return self._m_volt_6 if hasattr(self, '_m_volt_6') else None

        @property
        def volt_5(self):
            if hasattr(self, '_m_volt_5'):
                return self._m_volt_5 if hasattr(self, '_m_volt_5') else None

            self._m_volt_5 = (((self.volts_str_5[0] - 48) * 1.0) + ((self.volts_str_5[2] - 48) / 10.0))
            return self._m_volt_5 if hasattr(self, '_m_volt_5') else None

        @property
        def uptime(self):
            if hasattr(self, '_m_uptime'):
                return self._m_uptime if hasattr(self, '_m_uptime') else None

            self._m_uptime = (((((((((1 if self.uptime_dd_str[0] > 47 else 0) * (self.uptime_dd_str[0] - 48)) * 10) + (self.uptime_dd_str[1] - 48)) * 24) * 60) * 60) + ((((((1 if self.uptime_hh_str[0] > 47 else 0) * (self.uptime_hh_str[0] - 48)) * 10) + (self.uptime_hh_str[1] - 48)) * 60) * 60)) + (((((1 if self.uptime_mm_str[0] > 47 else 0) * (self.uptime_mm_str[0] - 48)) * 10) + (self.uptime_mm_str[1] - 48)) * 60))
            return self._m_uptime if hasattr(self, '_m_uptime') else None

        @property
        def volts_str_1(self):
            if hasattr(self, '_m_volts_str_1'):
                return self._m_volts_str_1 if hasattr(self, '_m_volts_str_1') else None

            _pos = self._io.pos()
            self._io.seek(150)
            self._m_volts_str_1 = [None] * (3)
            for i in range(3):
                self._m_volts_str_1[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_1 if hasattr(self, '_m_volts_str_1') else None

        @property
        def hff_str(self):
            if hasattr(self, '_m_hff_str'):
                return self._m_hff_str if hasattr(self, '_m_hff_str') else None

            _pos = self._io.pos()
            self._io.seek(234)
            self._m_hff_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_hff_str if hasattr(self, '_m_hff_str') else None

        @property
        def hr_str(self):
            if hasattr(self, '_m_hr_str'):
                return self._m_hr_str if hasattr(self, '_m_hr_str') else None

            _pos = self._io.pos()
            self._io.seek(255)
            self._m_hr_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_hr_str if hasattr(self, '_m_hr_str') else None


    class Ao40FecCommandResponse(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40MessageK(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line5 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line6 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line7 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line8 = (self._io.read_bytes(64)).decode(u"ASCII")

        @property
        def tfl_str(self):
            if hasattr(self, '_m_tfl_str'):
                return self._m_tfl_str if hasattr(self, '_m_tfl_str') else None

            _pos = self._io.pos()
            self._io.seek(201)
            self._m_tfl_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_tfl_str if hasattr(self, '_m_tfl_str') else None

        @property
        def volts_str_9(self):
            if hasattr(self, '_m_volts_str_9'):
                return self._m_volts_str_9 if hasattr(self, '_m_volts_str_9') else None

            _pos = self._io.pos()
            self._io.seek(182)
            self._m_volts_str_9 = [None] * (3)
            for i in range(3):
                self._m_volts_str_9[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_9 if hasattr(self, '_m_volts_str_9') else None

        @property
        def leila_act(self):
            if hasattr(self, '_m_leila_act'):
                return self._m_leila_act if hasattr(self, '_m_leila_act') else None

            self._m_leila_act = self.leila_active_str > 48
            return self._m_leila_act if hasattr(self, '_m_leila_act') else None

        @property
        def volt_3(self):
            if hasattr(self, '_m_volt_3'):
                return self._m_volt_3 if hasattr(self, '_m_volt_3') else None

            self._m_volt_3 = (((self.volts_str_3[0] - 48) * 1.0) + ((self.volts_str_3[2] - 48) / 10.0))
            return self._m_volt_3 if hasattr(self, '_m_volt_3') else None

        @property
        def uptime_dd_str(self):
            if hasattr(self, '_m_uptime_dd_str'):
                return self._m_uptime_dd_str if hasattr(self, '_m_uptime_dd_str') else None

            _pos = self._io.pos()
            self._io.seek(71)
            self._m_uptime_dd_str = [None] * (2)
            for i in range(2):
                self._m_uptime_dd_str[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_uptime_dd_str if hasattr(self, '_m_uptime_dd_str') else None

        @property
        def volts_str_2(self):
            if hasattr(self, '_m_volts_str_2'):
                return self._m_volts_str_2 if hasattr(self, '_m_volts_str_2') else None

            _pos = self._io.pos()
            self._io.seek(154)
            self._m_volts_str_2 = [None] * (3)
            for i in range(3):
                self._m_volts_str_2[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_2 if hasattr(self, '_m_volts_str_2') else None

        @property
        def commands(self):
            if hasattr(self, '_m_commands'):
                return self._m_commands if hasattr(self, '_m_commands') else None

            self._m_commands = ((((((1 if self.commands_str[0] > 47 else 0) * (self.commands_str[0] - 48)) * 1000) + (((1 if self.commands_str[1] > 47 else 0) * (self.commands_str[1] - 48)) * 100)) + (((1 if self.commands_str[2] > 47 else 0) * (self.commands_str[2] - 48)) * 10)) + (self.commands_str[3] - 48))
            return self._m_commands if hasattr(self, '_m_commands') else None

        @property
        def volt_8(self):
            if hasattr(self, '_m_volt_8'):
                return self._m_volt_8 if hasattr(self, '_m_volt_8') else None

            self._m_volt_8 = (((self.volts_str_8[0] - 48) * 1.0) + ((self.volts_str_8[2] - 48) / 10.0))
            return self._m_volt_8 if hasattr(self, '_m_volt_8') else None

        @property
        def volts_str_8(self):
            if hasattr(self, '_m_volts_str_8'):
                return self._m_volts_str_8 if hasattr(self, '_m_volts_str_8') else None

            _pos = self._io.pos()
            self._io.seek(178)
            self._m_volts_str_8 = [None] * (3)
            for i in range(3):
                self._m_volts_str_8[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_8 if hasattr(self, '_m_volts_str_8') else None

        @property
        def volts_str_6(self):
            if hasattr(self, '_m_volts_str_6'):
                return self._m_volts_str_6 if hasattr(self, '_m_volts_str_6') else None

            _pos = self._io.pos()
            self._io.seek(170)
            self._m_volts_str_6 = [None] * (3)
            for i in range(3):
                self._m_volts_str_6[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_6 if hasattr(self, '_m_volts_str_6') else None

        @property
        def tfh_str(self):
            if hasattr(self, '_m_tfh_str'):
                return self._m_tfh_str if hasattr(self, '_m_tfh_str') else None

            _pos = self._io.pos()
            self._io.seek(222)
            self._m_tfh_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_tfh_str if hasattr(self, '_m_tfh_str') else None

        @property
        def volt_7(self):
            if hasattr(self, '_m_volt_7'):
                return self._m_volt_7 if hasattr(self, '_m_volt_7') else None

            self._m_volt_7 = (((self.volts_str_7[0] - 48) * 1.0) + ((self.volts_str_7[2] - 48) / 10.0))
            return self._m_volt_7 if hasattr(self, '_m_volt_7') else None

        @property
        def commands_str(self):
            if hasattr(self, '_m_commands_str'):
                return self._m_commands_str if hasattr(self, '_m_commands_str') else None

            _pos = self._io.pos()
            self._io.seek(90)
            self._m_commands_str = [None] * (4)
            for i in range(4):
                self._m_commands_str[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_commands_str if hasattr(self, '_m_commands_str') else None

        @property
        def volts_str_7(self):
            if hasattr(self, '_m_volts_str_7'):
                return self._m_volts_str_7 if hasattr(self, '_m_volts_str_7') else None

            _pos = self._io.pos()
            self._io.seek(174)
            self._m_volts_str_7 = [None] * (3)
            for i in range(3):
                self._m_volts_str_7[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_7 if hasattr(self, '_m_volts_str_7') else None

        @property
        def hth_str(self):
            if hasattr(self, '_m_hth_str'):
                return self._m_hth_str if hasattr(self, '_m_hth_str') else None

            _pos = self._io.pos()
            self._io.seek(245)
            self._m_hth_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_hth_str if hasattr(self, '_m_hth_str') else None

        @property
        def temperature(self):
            if hasattr(self, '_m_temperature'):
                return self._m_temperature if hasattr(self, '_m_temperature') else None

            self._m_temperature = ((((1 if self.temp_str[0] > 47 else 0) * (self.temp_str[0] - 48)) * 10) + (self.temp_str[1] - 48))
            return self._m_temperature if hasattr(self, '_m_temperature') else None

        @property
        def uptime_hh_str(self):
            if hasattr(self, '_m_uptime_hh_str'):
                return self._m_uptime_hh_str if hasattr(self, '_m_uptime_hh_str') else None

            _pos = self._io.pos()
            self._io.seek(75)
            self._m_uptime_hh_str = [None] * (2)
            for i in range(2):
                self._m_uptime_hh_str[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_uptime_hh_str if hasattr(self, '_m_uptime_hh_str') else None

        @property
        def volt_9(self):
            if hasattr(self, '_m_volt_9'):
                return self._m_volt_9 if hasattr(self, '_m_volt_9') else None

            self._m_volt_9 = (((self.volts_str_9[0] - 48) * 1.0) + ((self.volts_str_9[2] - 48) / 10.0))
            return self._m_volt_9 if hasattr(self, '_m_volt_9') else None

        @property
        def volts_str_4(self):
            if hasattr(self, '_m_volts_str_4'):
                return self._m_volts_str_4 if hasattr(self, '_m_volts_str_4') else None

            _pos = self._io.pos()
            self._io.seek(162)
            self._m_volts_str_4 = [None] * (3)
            for i in range(3):
                self._m_volts_str_4[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_4 if hasattr(self, '_m_volts_str_4') else None

        @property
        def volt_2(self):
            if hasattr(self, '_m_volt_2'):
                return self._m_volt_2 if hasattr(self, '_m_volt_2') else None

            self._m_volt_2 = (((self.volts_str_2[0] - 48) * 1.0) + ((self.volts_str_2[2] - 48) / 10.0))
            return self._m_volt_2 if hasattr(self, '_m_volt_2') else None

        @property
        def leila_request_str(self):
            if hasattr(self, '_m_leila_request_str'):
                return self._m_leila_request_str if hasattr(self, '_m_leila_request_str') else None

            _pos = self._io.pos()
            self._io.seek(110)
            self._m_leila_request_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_leila_request_str if hasattr(self, '_m_leila_request_str') else None

        @property
        def leila_req(self):
            if hasattr(self, '_m_leila_req'):
                return self._m_leila_req if hasattr(self, '_m_leila_req') else None

            self._m_leila_req = self.leila_request_str > 48
            return self._m_leila_req if hasattr(self, '_m_leila_req') else None

        @property
        def volt_4(self):
            if hasattr(self, '_m_volt_4'):
                return self._m_volt_4 if hasattr(self, '_m_volt_4') else None

            self._m_volt_4 = (((self.volts_str_4[0] - 48) * 1.0) + ((self.volts_str_4[2] - 48) / 10.0))
            return self._m_volt_4 if hasattr(self, '_m_volt_4') else None

        @property
        def leila_active_str(self):
            if hasattr(self, '_m_leila_active_str'):
                return self._m_leila_active_str if hasattr(self, '_m_leila_active_str') else None

            _pos = self._io.pos()
            self._io.seek(127)
            self._m_leila_active_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_leila_active_str if hasattr(self, '_m_leila_active_str') else None

        @property
        def volts_str_5(self):
            if hasattr(self, '_m_volts_str_5'):
                return self._m_volts_str_5 if hasattr(self, '_m_volts_str_5') else None

            _pos = self._io.pos()
            self._io.seek(166)
            self._m_volts_str_5 = [None] * (3)
            for i in range(3):
                self._m_volts_str_5[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_5 if hasattr(self, '_m_volts_str_5') else None

        @property
        def volt_1(self):
            if hasattr(self, '_m_volt_1'):
                return self._m_volt_1 if hasattr(self, '_m_volt_1') else None

            self._m_volt_1 = (((self.volts_str_1[0] - 48) * 1.0) + ((self.volts_str_1[2] - 48) / 10.0))
            return self._m_volt_1 if hasattr(self, '_m_volt_1') else None

        @property
        def uptime_mm_str(self):
            if hasattr(self, '_m_uptime_mm_str'):
                return self._m_uptime_mm_str if hasattr(self, '_m_uptime_mm_str') else None

            _pos = self._io.pos()
            self._io.seek(79)
            self._m_uptime_mm_str = [None] * (2)
            for i in range(2):
                self._m_uptime_mm_str[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_uptime_mm_str if hasattr(self, '_m_uptime_mm_str') else None

        @property
        def tfe_str(self):
            if hasattr(self, '_m_tfe_str'):
                return self._m_tfe_str if hasattr(self, '_m_tfe_str') else None

            _pos = self._io.pos()
            self._io.seek(212)
            self._m_tfe_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_tfe_str if hasattr(self, '_m_tfe_str') else None

        @property
        def temp_str(self):
            if hasattr(self, '_m_temp_str'):
                return self._m_temp_str if hasattr(self, '_m_temp_str') else None

            _pos = self._io.pos()
            self._io.seek(134)
            self._m_temp_str = [None] * (2)
            for i in range(2):
                self._m_temp_str[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_temp_str if hasattr(self, '_m_temp_str') else None

        @property
        def volts_str_3(self):
            if hasattr(self, '_m_volts_str_3'):
                return self._m_volts_str_3 if hasattr(self, '_m_volts_str_3') else None

            _pos = self._io.pos()
            self._io.seek(158)
            self._m_volts_str_3 = [None] * (3)
            for i in range(3):
                self._m_volts_str_3[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_3 if hasattr(self, '_m_volts_str_3') else None

        @property
        def volt_6(self):
            if hasattr(self, '_m_volt_6'):
                return self._m_volt_6 if hasattr(self, '_m_volt_6') else None

            self._m_volt_6 = (((self.volts_str_6[0] - 48) * 1.0) + ((self.volts_str_6[2] - 48) / 10.0))
            return self._m_volt_6 if hasattr(self, '_m_volt_6') else None

        @property
        def volt_5(self):
            if hasattr(self, '_m_volt_5'):
                return self._m_volt_5 if hasattr(self, '_m_volt_5') else None

            self._m_volt_5 = (((self.volts_str_5[0] - 48) * 1.0) + ((self.volts_str_5[2] - 48) / 10.0))
            return self._m_volt_5 if hasattr(self, '_m_volt_5') else None

        @property
        def uptime(self):
            if hasattr(self, '_m_uptime'):
                return self._m_uptime if hasattr(self, '_m_uptime') else None

            self._m_uptime = (((((((((1 if self.uptime_dd_str[0] > 47 else 0) * (self.uptime_dd_str[0] - 48)) * 10) + (self.uptime_dd_str[1] - 48)) * 24) * 60) * 60) + ((((((1 if self.uptime_hh_str[0] > 47 else 0) * (self.uptime_hh_str[0] - 48)) * 10) + (self.uptime_hh_str[1] - 48)) * 60) * 60)) + (((((1 if self.uptime_mm_str[0] > 47 else 0) * (self.uptime_mm_str[0] - 48)) * 10) + (self.uptime_mm_str[1] - 48)) * 60))
            return self._m_uptime if hasattr(self, '_m_uptime') else None

        @property
        def volts_str_1(self):
            if hasattr(self, '_m_volts_str_1'):
                return self._m_volts_str_1 if hasattr(self, '_m_volts_str_1') else None

            _pos = self._io.pos()
            self._io.seek(150)
            self._m_volts_str_1 = [None] * (3)
            for i in range(3):
                self._m_volts_str_1[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_volts_str_1 if hasattr(self, '_m_volts_str_1') else None

        @property
        def hff_str(self):
            if hasattr(self, '_m_hff_str'):
                return self._m_hff_str if hasattr(self, '_m_hff_str') else None

            _pos = self._io.pos()
            self._io.seek(234)
            self._m_hff_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_hff_str if hasattr(self, '_m_hff_str') else None

        @property
        def hr_str(self):
            if hasattr(self, '_m_hr_str'):
                return self._m_hr_str if hasattr(self, '_m_hr_str') else None

            _pos = self._io.pos()
            self._io.seek(255)
            self._m_hr_str = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_hr_str if hasattr(self, '_m_hr_str') else None


    @property
    def frame_length(self):
        if hasattr(self, '_m_frame_length'):
            return self._m_frame_length if hasattr(self, '_m_frame_length') else None

        self._m_frame_length = self._io.size()
        return self._m_frame_length if hasattr(self, '_m_frame_length') else None


