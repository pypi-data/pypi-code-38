import struct


class TileDescriptor:
    """
    TileDescriptor

    A data structure that lists information about a tile attached to an IOTile controller.
    """

    def __init__(self, binvalue):
        hwtype, api_major, api_minor, name, major, minor, patch, exec_maj, exec_min, exec_patch, slot, uid = struct.unpack("<BBB6sBBBBBBBL", binvalue)

        self.hwtype = hwtype
        self.api_version = (api_major, api_minor)
        self.module_version = (major, minor, patch)
        self.exec_version = (exec_maj, exec_min, exec_patch)
        self.slot = slot
        self.unique_id = uid
        self.name = name

    def __str__(self):
        return "%s, version %d.%d.%d at slot %d" % (self.name, self.module_version[0], self.module_version[1], self.module_version[2], self.slot)


def size():
    return 20

def convert(arg):
    if isinstance(arg, TileDescriptor):
        return arg

    raise ValueError("fw_tiledescriptor can only be created from binary data inside a bytearray")

def convert_binary(arg, **kwargs):
    return TileDescriptor(arg)

#Formatting Functions
def default_formatter(arg, **kwargs):
    return str(arg)
