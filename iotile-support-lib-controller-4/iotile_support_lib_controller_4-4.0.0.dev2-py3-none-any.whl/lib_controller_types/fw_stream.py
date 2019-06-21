from iotile.core.exceptions import ValidationError


class SensorStream:
    TypeOffset = 12
    TypeMask = (0b1111 << TypeOffset)
    MaxID = (1 << (TypeOffset - 1)) - 1
    CodeMask = (1 << (TypeOffset - 1)) - 1

    BufferedNodeType = 0
    UnbufferedNodeType = 1
    ConstantType = 2
    InputType = 3
    CountType = 4
    OutputType = 5
    SystemCode = 1 << 11
    BreaksCode = 1 << 15
    AllStreamsCode = (SystemCode - 1)
    SpecialType = 0b1111

    namemap = {InputType: 'input', OutputType: 'output', BufferedNodeType: 'buffered node',
               UnbufferedNodeType: 'unbuffered node', ConstantType: 'constant',
               CountType: 'counter node'}

    def __init__(self, desc):
        """
        Create a sensor stream from either a string descriptor or a numeric ID

        sensor stream names are 16 bit unsigned integers with 8 bits of ID number
        and other flag bits that specify how and where the stream is stored.
        """

        if isinstance(desc, str):
            self.id = self._process_descriptor(desc)
        elif isinstance(desc, int):
            self.id = desc
        else:
            raise ValidationError("Could not convert sensor stream descriptor to integer", descriptor=desc)

        self.buffered = False
        self.output = False
        self.type = (self.id & SensorStream.TypeMask) >> SensorStream.TypeOffset
        self.system = bool(self.id & SensorStream.SystemCode)
        self.code = self.id & SensorStream.CodeMask

        #Set some useful flags so we know where to look for this stream
        if self.type == SensorStream.BufferedNodeType:
            self.buffered = True
        elif self.type == SensorStream.OutputType:
            self.buffered = True
            self.output = True

    def _process_descriptor(self, desc):
        """
        Process a string descriptor into a numeric sensor stream id

        String format is:
        [input|output|buffered node|unbuffered node|constant|counter] (number)
        """

        typemap = {'input': SensorStream.InputType, 'output': SensorStream.OutputType, 'buffered node': SensorStream.BufferedNodeType,
                   'buffered': SensorStream.BufferedNodeType, 'unbuffered': SensorStream.UnbufferedNodeType, 'unbuffered node': SensorStream.UnbufferedNodeType, 'constant': SensorStream.ConstantType,
                   'counter node': SensorStream.CountType, 'counter': SensorStream.CountType}

        system_id = 0
        if desc.startswith('system '):
            desc = desc[len('system '):]
            system_id = SensorStream.SystemCode

        # Check for special stream names here that indicate metastreams
        if desc == 'all outputs':
            return (SensorStream.OutputType << SensorStream.TypeOffset) | SensorStream.AllStreamsCode | SensorStream.BreaksCode
        elif desc == 'all system outputs':
            return (SensorStream.OutputType << SensorStream.TypeOffset) | SensorStream.AllStreamsCode | SensorStream.SystemCode
        elif desc == 'all user outputs':
            return (SensorStream.OutputType << SensorStream.TypeOffset) | SensorStream.AllStreamsCode
        elif desc == 'all combined outputs':
            return (SensorStream.OutputType << SensorStream.TypeOffset) | SensorStream.AllStreamsCode | SensorStream.BreaksCode | SensorStream.SystemCode
        elif desc == 'all storage' or desc == 'all buffered':
            return (SensorStream.BufferedNodeType << SensorStream.TypeOffset) | SensorStream.AllStreamsCode | SensorStream.BreaksCode
        elif desc == 'all system storage' or desc == 'all system buffered':
            return (SensorStream.BufferedNodeType << SensorStream.TypeOffset) | SensorStream.AllStreamsCode | SensorStream.SystemCode
        elif desc == 'all user storage'  or desc == 'all user buffered':
            return (SensorStream.BufferedNodeType << SensorStream.TypeOffset) | SensorStream.AllStreamsCode
        elif desc == 'all combined storage' or desc == 'all combined buffered':
            return (SensorStream.BufferedNodeType << SensorStream.TypeOffset) | SensorStream.AllStreamsCode | SensorStream.BreaksCode | SensorStream.SystemCode

        typename, _sep, idnumber = desc.rpartition(' ')

        if typename not in typemap:
            raise ValidationError("Unknown stream type", typename=typename, known_types=typemap.keys(), descriptor=desc)

        try:
            idnumber = int(idnumber, 0)
        except ValueError:
            raise ValidationError("Could not convert stream id to a number", id_number=idnumber, descriptor=desc)

        if idnumber < 0 or idnumber > SensorStream.MaxID:
            raise ValidationError("Stream id numbers must be in the range of [0, 4095]", id_number=idnumber)

        return idnumber | (typemap[typename] << SensorStream.TypeOffset) | system_id

    def __str__(self):
        name = ""
        if self.system:
            name = "system "

        name += self.namemap[self.type]
        name += " 0x%X" % self.code

        return name

    def is_constant(self):
        return self.type == SensorStream.ConstantType

def size():
    return 2

def convert(arg):
    if isinstance(arg, SensorStream):
        return arg

    return SensorStream(arg)

#Formatting Functions
def default_formatter(arg, **kwargs):
    return str(arg.id)

#Validator Function
def validate_buffered(arg, **kwargs):
    if not arg.buffered:
        raise ValueError("Stream is not buffered")
