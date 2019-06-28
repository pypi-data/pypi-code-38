from photons_messages_generator.helpers import valid_enum_types
from photons_messages_generator import field_types as ft
from photons_messages_generator import errors

from input_algorithms.errors import BadSpecValue
from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb

class EnumValue(dictobj.Spec):
    name = dictobj.Field(sb.string_spec, wrapper=sb.required)
    value = dictobj.Field(sb.integer_spec, wrapper=sb.required)

class Enum(dictobj.Spec):
    name = dictobj.Field(sb.string_spec, wrapper=sb.required)
    full_name = dictobj.Field(sb.string_spec, wrapper=sb.required)
    type = dictobj.Field(sb.string_choice_spec(valid_enum_types), wrapper=sb.required)
    values = dictobj.Field(sb.listof(EnumValue.FieldSpec()))

class struct_field_spec(sb.Spec):
    def normalise_filled(self, meta, val):
        val = sb.dictionary_spec().normalise(meta, val)
        if val.get("type") == "reserved":
            if "name" in val:
                raise BadSpecValue("Expected reserved field to not have a name", meta=meta.at("name"))
        else:
            if "name" not in val:
                raise BadSpecValue("Expected field to have a name", meta=meta.at("name"))
            val["full_name"] = val["name"]

        if "type" in val:
            val["original_type"] = val["type"]

        return StructField.FieldSpec().normalise(meta, val)

class StructField(dictobj.Spec):
    name = dictobj.NullableField(sb.string_spec)
    full_name = dictobj.NullableField(sb.string_spec)
    type = dictobj.Field(sb.string_spec, wrapper=sb.required)
    original_type = dictobj.Field(sb.string_spec, wrapper=sb.required)
    size_bytes = dictobj.Field(sb.integer_spec, wrapper=sb.required)
    default = dictobj.NullableField(sb.string_spec)
    extras = dictobj.Field(sb.listof(sb.string_spec()))

    def format(self, in_fields=False, type_only=False):
        extras = ".".join(self.format_extras())
        if extras:
            extras = f".{extras}"

        if isinstance(self.type, ft.StructType):
            if self.type.multiples == 1 and not self.original_type.startswith("["):
                prefix = "" if in_fields else "fields."
                return f"*{prefix}{self.type.struct.name}"

        type_info = f"{self.type.format(self.size_bytes, in_fields=in_fields)}{extras}"
        if type_only:
            return type_info

        if isinstance(self.type, ft.StructType):
            return f"(\"{self.name}\", {type_info})"
        else:
            return f"(\"{self.name}\", {type_info})"

    def format_extras(self):
        if self.default is not None:
            if isinstance(self.type, ft.EnumType):
                yield f"default(enums.{self.type.enum.name}.{self.type.value(self.default)})"
            else:
                yield f"default({self.default})"

        for extra in self.extras:
            yield extra.strip()

    def expand_fields(self, chain=None, prefix=None, expand_structs=False):
        if not getattr(self.type, "expanded", False):
            if isinstance(self.type, ft.StructType):
                if self.type.multiples > 1:
                    return self
            else:
                raise errors.CannotExpand(cant_expand=self.type)

        if prefix is None:
            prefix = []

        if not isinstance(self.type, ft.StructType) or getattr(self.type, "expanded", False):
            prefix.append(self.name)

        yield from self.type.expand_fields(chain=chain, prefix=prefix, expand_structs=expand_structs)

    def with_prefix(self, prefix):
        clone = self.clone()

        if self.name is None:
            return clone

        clone.name = "".join(prefix + [self.name])
        return clone

class CloneStruct(dictobj.Spec):
    name = dictobj.Field(sb.string_spec, wrapper=sb.required)
    many_options = dictobj.NullableField(sb.any_spec)

    @property
    def full_name(self):
        return self.name

    @property
    def many_name(self):
        if self.many_options is None:
            raise errors.ExpectedManyName(f"Struct {self.name} is used in a .many block but has no many_name specified")
        return self.many_options.name

class struct_spec(sb.Spec):
    def normalise_filled(self, meta, val):
        val = sb.dictionary_spec().normalise(meta, val)
        if "fields" in val:
            val["item_fields"] = val["fields"]
        return Struct.FieldSpec().normalise(meta, val)

class Struct(dictobj.Spec):
    name = dictobj.Field(sb.string_spec, wrapper=sb.required)
    full_name = dictobj.Field(sb.string_spec, wrapper=sb.required)
    size_bytes = dictobj.Field(sb.integer_spec, wrapper=sb.required)
    item_fields = dictobj.Field(sb.listof(struct_field_spec()))
    many_options = dictobj.NullableField(sb.any_spec)

    @property
    def many_name(self):
        if self.many_options is None:
            raise errors.ExpectedManyName(f"Struct {self.name} is used in a .many block but has no many_name specified")
        return self.many_options.name

class packet_spec(sb.Spec):
    def normalise_filled(self, meta, val):
        val = sb.dictionary_spec().normalise(meta, val)
        if "fields" in val:
            val["item_fields"] = val["fields"]
        return Packet.FieldSpec().normalise(meta, val)

class Packet(dictobj.Spec):
    name = dictobj.Field(sb.string_spec, wrapper=sb.required)
    full_name = dictobj.Field(sb.string_spec, wrapper=sb.required)
    namespace = dictobj.Field(sb.string_spec, wrapper=sb.required)
    pkt_type = dictobj.Field(sb.integer_spec, wrapper=sb.required)
    size_bytes = dictobj.Field(sb.integer_spec, wrapper=sb.required)
    item_fields = dictobj.Field(sb.listof(struct_field_spec()), wrapper=sb.required)

class Type(dictobj.Spec):
    multiples = dictobj.Field(sb.integer_spec, wrapper=sb.required)
    type = dictobj.Field(sb.any_spec, wrapper=sb.required)

class named_spec(sb.Spec):
    def __init__(self, spec):
        self.spec = spec

    def normalise_empty(self, meta):
        return []

    def normalise_filled(self, meta, val):
        val = sb.dictof(sb.string_spec(), sb.dictionary_spec()).normalise(meta, val)

        final = []
        for name, v in val.items():
            v["name"] = name
            v["full_name"] = name
            final.append(self.spec.normalise(meta.at(name), v))

        return final

class packets_spec(sb.Spec):
    def normalise_empty(self, meta):
        return []

    def normalise_filled(self, meta, val):
        val = sb.dictionary_spec().normalise(meta, val)

        final = []
        for namespace, packets in val.items():
            for name, v in packets.items():
                if type(v) is dict:
                    v = dict(v)
                    v["namespace"] = namespace
                    v["full_name"] = name
                    v["name"] = name
                final.append(packet_spec().normalise(meta.at(name), v))

        return final

class Src(dictobj.Spec):
    enums = dictobj.Field(named_spec(Enum.FieldSpec()))
    groups = dictobj.Field(named_spec(struct_spec()))
    packets = dictobj.Field(packets_spec())
