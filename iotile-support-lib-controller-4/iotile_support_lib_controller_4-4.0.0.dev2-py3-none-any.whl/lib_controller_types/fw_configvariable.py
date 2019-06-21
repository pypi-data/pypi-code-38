import struct
from iotile.core.exceptions import *
from . import fw_tileselector


class ConfigDescriptor:
    ConfigMagic = 0xCACA

    def __init__(self, arg):
        if isinstance(arg, bytearray):
            if len(arg) != size():
                raise ValidationError("Invalid size for buffer containing a TileDescriptor", expected=size(), actual=len(arg))

            self.raw_data = arg
            self._extract_info()
        else:
            raise ValidationError("You can only create a ConfigDescriptor from binary data")

    def _extract_info(self):
        magic, offset, length, match_info, valid, _ = struct.unpack("<HHH8sBB", self.raw_data)

        if magic != ConfigDescriptor.ConfigMagic:
            raise ValidationError("Invalid magic number in config variable", expected=ConfigDescriptor.ConfigMagic, actual=magic)

        self.data_offset = offset
        self.data_length = length
        self.target = fw_tileselector.convert_binary(bytearray(match_info))
        self.valid = bool(valid == 0xFF)

    def __str__(self):
        out = ""

        out += "Target: %s\n" % str(self.target)
        out += "Data Offset: %d\n" % self.data_offset
        out += "Data Length: %d\n" % self.data_length
        out += "Valid: %s" % str(self.valid)

        return out

def size():
    return 16

def convert(arg):
    if isinstance(arg, ConfigDescriptor):
        return arg

    return ConfigDescriptor(arg)

def convert_binary(arg, **kwargs):
    return ConfigDescriptor(arg)

#Formatting Functions
def default_formatter(arg, **kwargs):
    return str(arg)
