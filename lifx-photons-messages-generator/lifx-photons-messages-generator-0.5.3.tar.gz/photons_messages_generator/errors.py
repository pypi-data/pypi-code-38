from delfick_error import DelfickError

class GeneratorError(DelfickError):
    pass

class UnexpectedEnumName(GeneratorError):
    desc = "enum name was unexpected"

class ExpectedManyName(GeneratorError):
    desc = "struct needs to be specified with a many name"

class CannotExpand(GeneratorError):
    desc = "Cannot expand fields that aren't packets"

class NotAClone(GeneratorError):
    pass

class UnknownClone(GeneratorError):
    desc = "Tried to access a struct clone that doesn't exist"

class UnknownStruct(GeneratorError):
    desc = "Tried to access a struct that doesn't exist"

class OverridingStructWithClone(GeneratorError):
    desc = "Trying to override existing struct with a clone"

class NotSameType(GeneratorError):
    pass

class NoSuchType(GeneratorError):
    desc = "No such type"

class NonsensicalMultiplier(GeneratorError):
    pass

class CyclicPacketField(GeneratorError):
    desc = "packet types form a cycle"

class NoSuchEnumValue(GeneratorError):
    desc = "No such enum value"

class UnknownSpecialType(GeneratorError):
    desc = "Unknown special type specified"

class UnknownPacket(GeneratorError):
    desc = "Unknown packet"

class NeedMoreInformation(GeneratorError):
    desc = "Need more information"

class BadUsingInstruction(GeneratorError):
    desc = "Invalid using option provided"

class InvalidBits(GeneratorError):
    desc = "bits instruction is wrong"

class InvalidOutput(GeneratorError):
    desc = "invalid output settings"

class InvalidName(GeneratorError):
    desc = "invalid name"

class CantBeString(GeneratorError):
    desc = "Cannot replace this type with a string"
