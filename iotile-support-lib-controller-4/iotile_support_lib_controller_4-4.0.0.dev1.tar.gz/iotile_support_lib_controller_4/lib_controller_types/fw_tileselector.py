import struct
from pyparsing import Regex, Literal, QuotedString, ParseException
from iotile.core.exceptions import ValidationError

number = Regex('((0x[a-fA-F0-9]+)|[0-9]+)').setParseAction(lambda s,l,t: [int(t[0], 0)])
slot_statement = Literal("slot").suppress() + number('slot_id')
con_statement = Literal("controller")
name_statement = Literal("name") + QuotedString('"')('tile_name')

selector = slot_statement | con_statement | name_statement


class TileSelector(object):
    MatchBySlot = 1
    MatchController = 2
    MatchByName = 3

    def __init__(self, desc):
        """
        Create a TileSelector from a string description of what tile should be matched
        """

        if isinstance(desc, str):
            self._process_descriptor(desc)
        elif isinstance(desc, bytearray):
            if len(desc) != size():
                raise ValidationError("Invalid size for buffer containing a TileDescriptor", expected=size(), actual=len(desc))

            self.raw_data = desc
        else:
            raise ValidationError("You must create a TileSelector from a string or binary description", descriptor=desc)

        self._extract_info()

    def _process_descriptor(self, desc):
        try:
            data = selector.parseString(desc)
        except ParseException as e:
            raise ValidationError("Invalid tile selector descriptor that could not be processed", location=e.loc, reason=e.msg)

        if 'slot_id' in data:
            slot = data['slot_id']

            if slot <= 0 or slot > 255:
                raise ValidationError("Invalid slot specified in TileSelector", slot=slot, expected_range=[1, 255])

            self.raw_data = struct.pack("<B5xxB", slot, self.MatchBySlot)
        elif 'tile_name' in data:
            name = data['tile_name']

            if len(name) < 6:
                name += ' '*(6 - len(name))
            elif len(name) > 6:
                raise ValidationError("Name is too long in TileSelector", expected_length=6, actual_length=len(name))

            self.raw_data = struct.pack("<6sxB", name, self.MatchByName)
        else:
            self.raw_data = struct.pack("<6xxB", self.MatchController)

    def _extract_info(self):
        data, op = struct.unpack("<6sxB", bytes(self.raw_data))

        self.slot = None
        self.name = None

        if op == self.MatchBySlot:
            self.slot, = struct.unpack_from("<B", bytes(self.raw_data))
        elif op == self.MatchByName:
            self.name = data
        
        self.op = op

    def matches_descriptor(self, desc):
        """Test if selector matches a TileDescriptor

        Args:
            desc (TileDescriptor): The descriptor to check

        Returns:
            bool: whether this selector matches the passed descriptor
        """
        if self.op == self.MatchBySlot and self.slot == desc.slot:
            return True
        elif self.op == self.MatchController and desc.slot == 0:
            return True
        elif self.op == self.MatchByName and desc.name == self.name:
            return True

        return False

    def __str__(self):
        if self.op == TileSelector.MatchBySlot:
            return "slot %d" % self.slot
        elif self.op == TileSelector.MatchByName:
            return "name \"%s\"" % self.name
        else:
            return "controller"

def size():
    return 8

def convert(arg):
    if isinstance(arg, TileSelector):
        return arg

    return TileSelector(arg)

def convert_binary(arg, **kwargs):
    return TileSelector(arg)

#Formatting Functions
def default_formatter(arg, **kwargs):
    return str(arg)
