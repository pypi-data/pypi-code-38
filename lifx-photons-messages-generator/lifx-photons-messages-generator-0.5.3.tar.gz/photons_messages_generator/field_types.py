from photons_messages_generator.helpers import convert_type
from photons_messages_generator import errors

class SimpleType:
    def __init__(self, val, multiples):
        self.val = val
        self.multiples = multiples

    def __repr__(self):
        return f"<Simple: {self.multiples}: {self.val}>"

    def format(self, size_bytes, **kwargs):
        return f"{convert_type(self.val, size_bytes)}"

class StringType:
    def __repr__(self):
        return f"<String>"

    def format(self, size_bytes, **kwargs):
        return f"{convert_type('string', size_bytes)}"

class EnumType:
    def __init__(self, enum, multiples, allow_unknown=False):
        self.enum = enum
        self.allow_unknown = allow_unknown
        if multiples != 1:
            raise errors.NonsensicalMultiplier("Enums cannot be multiple"
                , wanted=multiples
                )

    def value(self, name):
        names = [v.name for v in self.enum.values]
        if name not in names:
            raise errors.NoSuchEnumValue(wanted=name, available=names, enum=self.enum.name)
        return name

    def __repr__(self):
        return f"<Enum: {self.enum.type}: {self.enum.name}>"

    def format(self, size_bytes, **kwargs):
        options = ""
        if self.allow_unknown:
            options = ", allow_unknown=True"
        return f"{convert_type(self.enum.type, size_bytes)}.enum(enums.{self.enum.name}{options})"

class StructOverrideType:
    def __init__(self, struct):
        self.struct = struct

    def __repr__(self):
        return f"<StructOverride: {self.struct}>"

    def format(self, size_bytes, **kwargs):
        raise errors.GeneratorError("Struct overrides should be resolved before format")

class SpecialType:
    def __init__(self, options):
        self.options = options

    def __repr__(self):
        return f"<SpecialType: {self.options.name}: {self.options.type}>"

    def format(self, size_bytes, in_fields=False, **kwargs):
        if size_bytes != self.options.size_bytes:
            raise errors.GeneratorError("Special type has different size_bytes than expected"
                , name=self.options.name
                , want=size_bytes
                , specified=self.options.size_bytes
                )

        prefix = "fields." if not in_fields else ""
        return f"{prefix}{self.options.name}"

class StructType:
    def __init__(self, struct, multiples, expanded=False, ignored=False):
        self.struct = struct
        self.multiples = multiples
        self.ignored = ignored
        self.expanded = expanded

    def __repr__(self):
        return f"<Struct: {self.multiples}: {self.struct.name}>"

    def format(self, size_bytes, in_fields=False, **kwargs):
        size_bytes = int(size_bytes / self.multiples * 8)
        prefix = "" if in_fields else "fields."
        typ = f"T.Bytes({size_bytes} * {self.multiples})"
        if self.ignored:
            return typ
        return f"{typ}.many(lambda pkt: {prefix}{self.struct.many_name})"

    def expand_fields(self, chain=None, prefix=None, expand_structs=False):
        if chain is None:
            chain = []

        if prefix is None:
            prefix = []

        if self.struct.full_name in chain:
            raise errors.CyclicPacketField(chain=chain)

        chain.append(self.struct.full_name)

        for field in self.struct.item_fields:
            if getattr(field.type, "expanded", False):
                yield from field.expand_fields(chain=chain, prefix=prefix, expand_structs=expand_structs)
            else:
                yield field.with_prefix(prefix)

class PacketType:
    def __init__(self, packet, multiples):
        self.packet = packet
        self.expanded = True
        if multiples != 1:
            raise errors.NonsensicalMultiplier("If you want multiples of a struct, make it not a packet type"
                , wanted=multiples
                )

    def __repr__(self):
        return f"<Packet: {self.packet.name}>"

    def format(self, size_bytes, **kwargs):
        raise errors.GeneratorError("Packet types are meant to be already resolved before formats are called", packet=self.packet)

    def expand_fields(self, chain=None, prefix=None, expand_structs=False):
        if chain is None:
            chain = []

        if prefix is None:
            prefix = []

        if self.packet.full_name in chain:
            raise errors.CyclicPacketField(chain=chain)

        chain.append(self.packet.full_name)

        for field in self.packet.item_fields:
            should_expand = getattr(field.type, "expanded", False)
            should_expand = should_expand or (expand_structs and isinstance(field.type, StructType))
            if should_expand:
                yield from field.expand_fields(chain=chain, prefix=prefix, expand_structs=True)
            else:
                yield field.with_prefix(prefix)

class OverrideType:
    def __init__(self, override):
        self.override = override

    def __repr__(self):
        return f"<Override {self.override}>"

    def format(self, size_bytes, **kwargs):
        return self.override
