from photons_messages_generator.helpers import camel_to_snake, snake_to_camel
from photons_messages_generator.src import CloneStruct, struct_field_spec
from photons_messages_generator import field_types as ft
from photons_messages_generator import errors

from input_algorithms.meta import Meta
from collections import defaultdict
from delfick_logging import lc
import keyword
import logging

log = logging.getLogger("generator.resolver")

class Resolver:
    def __init__(self, src, adjustments):
        self.src = src
        self.adjustments = adjustments

    def resolve(self):
        for struct in self.src.groups:
            struct.many_options = self.adjustments.many_options(struct.full_name)

        by_fields = defaultdict(list)
        for packet in self.src.packets:
            if packet.item_fields:
                fields = tuple((field.full_name, field.type) for field in packet.item_fields)
                by_fields[fields].append(packet)

        self.resolve_using()
        self.validate_bits()
        self.fix_packet_names()

        self.register_clones()
        self.resolve_namespaces()
        self.resolve_field_extras()
        self.resolve_types()
        self.resolve_renames()
        self.resolve_packet_fields()
        self.generate_clones()

        self.fix_field_names()
        self.validate_field_names()
        self.rename_namespaces()

        for packets in by_fields.values():
            if len(packets) > 1:
                diff = False
                for packet in packets:
                    if not diff:
                        for compare in [p for p in packets if p is not packet]:
                            diff = self.compare_fields(packet, compare)

    def compare_fields(self, one, two):
        names_one = [f.name for f in one.item_fields]
        names_two = [f.name for f in two.item_fields]
        if set(names_one) != set(names_two):
            log.warning(lc("Two packets with same full names has different resolved names"
                , **{one.name: names_one, two.name: names_two}
                ))
            return True

        diff = False
        for f1, f2 in zip(one.item_fields, two.item_fields):
            info = lambda f: f"\n<<\n\tname: {f.name}\n\ttype: {f.type}\n\tdefault: {f.default}\n\textras: {f.extras}\n>>\n"
            f1_info = info(f1)
            f2_info = info(f2)
            if f1_info != f2_info:
                log.warning(lc("Two packets with same field types has differences in fields\n"
                    , **{one.name: f1_info, two.name: f2_info}
                    ))
                diff = True

        return diff

    def ensure_using_instruction_is_correct(self, one, two):
        names_one = [f.full_name for f in one.item_fields]
        names_two = [f.full_name for f in two.item_fields]
        if set(names_one) != set(names_two):
            raise errors.BadUsingInstruction("The two packets have different field names"
                , **{one.name: names_one, two.name: names_two}
                )

        for f1, f2 in zip(one.item_fields, two.item_fields):
            info = lambda f: f"\n<<\n\tname: {f.name}\n\ttype: {f.type}\n>>\n"
            f1_info = info(f1)
            f2_info = info(f2)
            if f1_info != f2_info:
                raise errors.BadUsingInstruction("The two packets have different field types"
                    , **{one.name: f1_info, two.name: f2_info}
                    )

    def validate_bits(self):
        for parent_full_name, field in self.all_fields:
            bits = self.adjustments.field_attr(parent_full_name, field.full_name, "bits")
            if bits:
                if len(bits) != field.size_bytes * 8:
                    raise errors.InvalidBits(f"Need {field.size_bytes * 8} options but only have {len(bits)}"
                        , packet = parent_full_name
                        , field = field.full_name
                        )

    def register_clones(self):
        names = [s.full_name for s in self.src.groups]
        for name, clone in self.adjustments.clones.items():
            if name in names:
                raise errors.OverridingStructWithClone(existing=name)
            self.src.groups.append(CloneStruct(name=name, many_options=clone.many_options))

    def generate_clones(self):
        for name, clone in self.adjustments.clones.items():
            struct = clone.clone_struct(self.get_struct(clone.cloning))
            struct.name = name
            struct.full_name = name
            self.src.groups.insert(0, struct)
        self.src.groups = [s for s in self.src.groups if not isinstance(s, CloneStruct)]

    def resolve_using(self):
        for parent, _ in self.all_parents:
            using = self.adjustments.using_for(parent.full_name)
            if using:
                using = self.find_packet(using)
                if using.pkt_type > parent.pkt_type:
                    raise errors.BadUsingInstruction("The pkt_type of the used message must be less than the packet"
                        , packet = parent.full_name
                        , using = parent.full_name
                        , packet_pkt_type = parent.pkt_type
                        , using_pkt_type = using.pkt_type
                        )
                self.ensure_using_instruction_is_correct(parent, using)
                self.adjustments.change_using(parent.full_name, using)

    def rename_namespaces(self):
        for packet in self.src.packets:
            rename = self.adjustments.rename_namespaces.get(packet.namespace)
            if rename:
                packet.namespace = rename

    def resolve_namespaces(self):
        for packet in self.src.packets:
            namespace = self.adjustments.packet_namespace(packet.full_name)
            if namespace is not None:
                packet.namespace = namespace

    def resolve_field_extras(self):
        for parent_full_name, field in self.all_fields:
            field.default = self.adjustments.field_attr(
                  parent_full_name, field.full_name, "default"
                )

            field.extras = self.adjustments.field_attr(
                  parent_full_name, field.full_name, "extras", []
                )

    def resolve_types(self):
        for parent_full_name, field in self.all_fields:
            if field.full_name and field.full_name.startswith("Reserved"):
                field.name = self.adjustments.field_attr(parent_full_name, field.full_name, "rename")
                field.full_name = None
                field.type = "reserved"

            field_type = self.adjustments.field_type(
                  parent_full_name, field.full_name
                ) or field.type

            field.type = self.resolve_type(field.full_name, parent_full_name, field_type
                , original = self.resolve_type(field.full_name, parent_full_name, field.type, original=None)
                )

    def resolve_packet_fields(self):
        for parent, _ in self.all_parents:
            fields = []
            for field in parent.item_fields:
                bits = self.adjustments.field_attr(parent.full_name, field.full_name, "bits")
                if bits:
                    for name in bits:
                        meta = Meta({}, []).at(parent.full_name).at(field.full_name).at(name)
                        f = struct_field_spec().normalise(meta
                            , { "name": name
                              , "type": "bit"
                              , "size_bytes": 0
                              }
                            )
                        f.type = ft.SimpleType("bit", 1)
                        fields.append(f)
                    continue

                if getattr(field.type, "expanded", False):
                    expand_structs = isinstance(field.type, ft.PacketType)
                    fields.extend(field.expand_fields(expand_structs=expand_structs))
                else:
                    fields.append(field)
            parent.item_fields = fields

    def resolve_renames(self):
        for enum in self.src.enums:
            rename = self.adjustments.rename(enum.full_name)
            if rename:
                enum.name = rename

        for parent, is_packet in self.all_parents:
            rename = self.adjustments.rename(parent.full_name, is_struct=not is_packet)
            if rename:
                parent.name = rename

            for field in parent.item_fields:
                rename = self.adjustments.field_attr(parent.full_name, field.full_name, "rename")
                if rename:
                    field.name = rename

    def fix_packet_names(self):
        for packet in self.src.packets:
            namespace_camel = snake_to_camel(packet.namespace)
            if not packet.full_name.startswith(namespace_camel):
                log.warning(lc("Packet with weird name, expected it to start with the namesapce"
                    , expected_prefix = namespace_camel
                    , packet_name = packet.full_name
                    ))
                continue

            short = packet.full_name[len(namespace_camel):]

            if short.startswith("Get"):
                name = f"Get{short[3:]}"
                if name == "Get":
                    name = f"{name}{namespace_camel}"
            elif short.startswith("Set"):
                name = f"Set{short[3:]}"
                if name == "Set":
                    name = f"{name}{namespace_camel}"
            elif short.startswith("State"):
                name = f"State{short[5:]}"
                if name == "State":
                    name = f"{namespace_camel}{name}"
            else:
                name = short

            packet.name = name

    def fix_field_names(self):
        for enum in self.src.enums:
            reserved_num = 1
            for value in enum.values:
                if value.name == "reserved":
                    value.name = f"reserved{reserved_num}".upper()
                    reserved_num += 1
                else:
                    prefix = f"{camel_to_snake(enum.full_name).upper()}_"
                    if value.name.startswith(prefix):
                        value.name = value.name[len(prefix):]
                    else:
                        raise errors.UnexpectedEnumName("Expected enum name to have the enum name as a prefix", got=value.name, enum=enum.name)

        for parent, is_packet in self.all_parents:
            reserved_num = self.adjustments.reserved_start(parent.full_name)
            for field in parent.item_fields:
                if field.name is None:
                    field.name = f"reserved{reserved_num}"
                    reserved_num += 1
                else:
                    field.name = camel_to_snake(field.name)

    def validate_field_names(self):
        for parent_full_name, field in self.all_fields:
            name = field.name

            invalid = self.adjustments.invalid_field_names
            if name and name in invalid:
                raise errors.InvalidName("Fields cannot be one of the invalid field names"
                    , field = name
                    , parent = parent_full_name
                    , invalid_names = invalid
                    )

            if name and name in keyword.kwlist:
                raise errors.InvalidName("Field names cannot be reserved python keywords"
                    , field = name
                    , parent = parent_full_name
                    , invalid_names = keyword.kwlist
                    )

    @property
    def all_fields(self):
        for struct in self.src.groups:
            if not isinstance(struct, CloneStruct):
                for field in struct.item_fields:
                    yield struct.full_name, field

        for packet in self.src.packets:
            for field in packet.item_fields:
                yield packet.full_name, field

    @property
    def all_parents(self):
        for struct in self.src.groups:
            if not isinstance(struct, CloneStruct):
                yield struct, False

        for packet in self.src.packets:
            yield packet, True

    def find_packet(self, name):
        for packet in self.src.packets:
            if packet.full_name == name:
                return packet
        raise errors.UnknownPacket(wanted=name)

    def ensure_is_same_type(self, typ, original, full_name):
        if not isinstance(original, ft.SimpleType):
            raise errors.GeneratorError("Cannot override non simple type with a special type"
                , overriding = original
                , name = full_name
                )

        if original.val != typ.options.type:
            raise errors.NotSameType("Tried to set type to something that is wrong"
                , want = typ
                , should_be = original
                , name = full_name
                )

        if original.multiples != typ.options.multiples:
            raise errors.NotSameType("Expect the same number of multiples for special type as original"
                , want = typ.options.multiples
                , need = original.multiples
                , special_type = typ.options.name
                , name = full_name
                )

    def resolve_type(self, field, parent, typ, original):
        if isinstance(typ, ft.OverrideType):
            return typ

        elif isinstance(typ, ft.StructOverrideType):
            if not self.is_clone(typ.struct, original):
                raise errors.NotAClone("Can only override structs with clones of them"
                    , wanted=typ
                    , need_clone_of=original
                    , name=parent
                    )
            return ft.StructType(self.get_struct(typ.struct), original.multiples)

        elif isinstance(typ, ft.StringType):
            if not isinstance(original, ft.SimpleType) or original.val != "byte":
                raise errors.CantBeString("Only bytes can be turned into string"
                    , name=parent
                    )
            return typ

        elif isinstance(typ, ft.SpecialType):
            self.ensure_is_same_type(typ, original, parent)
            return typ

        elif not isinstance(typ, str):
            raise Exception("Expected a string", got=typ, type=type(typ))

        multiples = 1
        if typ.startswith('['):
            multiples = int(typ[1:typ.find("]")])
            typ = typ[typ.find("]") + 1:]

        if typ.startswith("<") and typ.endswith(">"):
            return self.find_type(field, parent, typ[1:-1], multiples)
        else:
            return ft.SimpleType(typ, multiples)

    def find_type(self, field, parent, typ, multiples):
        ignored = self.adjustments.ignore.get(typ)
        if ignored and not ignored.expanded:
            return ft.SimpleType("byte", 1)

        for enum in self.src.enums:
            if enum.full_name == typ:
                allow_unknown_enums = self.adjustments.field_attr(parent, field, "allow_unknown_enums", False)
                return ft.EnumType(enum, multiples, allow_unknown=allow_unknown_enums)

        for struct in self.src.groups:
            if struct.full_name == typ:
                expanded = (ignored and ignored.expanded) and multiples == 1
                return ft.StructType(struct, multiples, expanded=expanded, ignored=ignored)

        for packet in self.src.packets:
            if packet.full_name == typ:
                return ft.PacketType(packet, multiples)

        raise errors.NoSuchType(wanted=typ)

    def is_clone(self, typ, original):
        if not isinstance(original, ft.StructType):
            raise errors.GeneratorError("Can only override structs with clones", got=original)

        clone = self.get_clone(typ)
        if clone.cloning != original.struct.name:
            raise errors.GeneratorError("Overriding a type with a clone of a different type", want=typ, overriding=original)

        return True

    def get_clone(self, typ):
        if typ not in self.adjustments.clones:
            raise errors.UnknownClone(want=typ, available=list(self.adjustments.clones))
        return self.adjustments.clones[typ]

    def get_struct(self, typ):
        for struct in self.src.groups:
            if struct.full_name == typ:
                return struct
        raise errors.UnknownStruct(wanted=typ)
