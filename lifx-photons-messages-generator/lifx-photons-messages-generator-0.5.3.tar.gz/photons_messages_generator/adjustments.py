from photons_messages_generator.helpers import camel_to_snake, valid_struct_types
from photons_messages_generator.src import struct_field_spec
from photons_messages_generator import field_types as ft
from photons_messages_generator import errors

from input_algorithms.validators import Validator
from input_algorithms.errors import BadSpecValue
from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from input_algorithms.meta import Meta
from contextlib import contextmanager
import os

class override_type_spec(sb.Spec):
    def normalise_filled(self, meta, val):
        val = sb.string_spec().normalise(meta, val)
        return ft.OverrideType(val)

class SpecialType(dictobj.Spec):
    name = dictobj.Field(sb.string_spec, wrapper=sb.required)
    type = dictobj.Field(sb.string_choice_spec(valid_struct_types), wrapper=sb.required)
    size_bytes = dictobj.Field(sb.integer_spec, wrapper=sb.required)
    multiples = dictobj.Field(sb.integer_spec, default=1)
    default = dictobj.NullableField(sb.string_spec)
    extras = dictobj.Field(sb.listof(sb.string_spec()))

    def format(self, in_fields=False):
        meta = Meta({}, []).at("special_types").at(self.name)
        field = struct_field_spec().normalise(meta
            , dict(
                  name = self.name
                , full_name = self.name
                , type = self.type
                , size_bytes = self.size_bytes
                , default = self.default
                , extras = self.extras
                )
            )
        field.type = ft.SimpleType(self.type, self.multiples)
        return field.format(type_only=True, in_fields=in_fields)

class special_types_spec(sb.Spec):
    def normalise_empty(self, meta):
        return {}

    def normalise_filled(self, meta, val):
        val = sb.dictof(sb.string_spec(), sb.dictionary_spec()).normalise(meta, val)
        for name, options in list(val.items()):
            options["name"] = name
            val[name] = SpecialType.FieldSpec().normalise(meta.at(name), options)

        return val

class no_more_than_one(Validator):
    def setup(self, choices):
        self.choices = choices

    def validate(self, meta, val):
        found = [key for key in self.choices if key in val]
        if len(found) > 1:
            raise BadSpecValue("Can only specify at most one of the type overrides"
                , avaialable=self.choices
                , found=found
                , meta=meta
                )
        return val

class adjust_field_spec(sb.Spec):
    def normalise_filled(self, meta, val):
        val = sb.dictionary_spec().normalise(meta, val)
        choices = ["bits", "string_type", "override_type", "override_struct", "special_type"]
        no_more_than_one(choices).normalise(meta, val)
        return AdjustField.FieldSpec().normalise(meta, val)

class must_be_true_spec(sb.Spec):
    def setup(self, name):
        self.name = name

    def normalise_filled(self, meta, val):
        if val != True:
            raise BadSpecValue(f"{self.name} can only be True or not present")
        return val

class AdjustField(dictobj.Spec):
    rename = dictobj.NullableField(sb.string_spec)
    default = dictobj.NullableField(sb.string_spec)
    extras = dictobj.Field(sb.listof(sb.string_spec()))
    allow_unknown_enums = dictobj.Field(sb.boolean, default=False)

    bits = dictobj.NullableField(sb.listof(sb.string_spec()))
    string_type = dictobj.NullableField(must_be_true_spec("string_type"))
    override_type = dictobj.NullableField(override_type_spec)
    override_struct = dictobj.NullableField(sb.string_spec)
    special_type = dictobj.NullableField(sb.string_spec)

class Many(dictobj.Spec):
    name = dictobj.Field(sb.string_spec, wrapper=sb.required)
    cache_amount = dictobj.NullableField(sb.integer_spec)

class struct_adjustment_spec(sb.Spec):
    def normalise_filled(self, meta, val):
        val = sb.dictionary_spec().normalise(meta, val)
        choices = ["fields", "using"]
        no_more_than_one(choices).normalise(meta, val)
        return StructAdjustment.FieldSpec().normalise(meta, val)

class StructAdjustment(dictobj.Spec):
    rename = dictobj.NullableField(sb.string_spec)
    fields = dictobj.Field(sb.dictof(sb.string_spec(), adjust_field_spec()))
    using = dictobj.NullableField(sb.string_spec)
    many_options = dictobj.NullableField(Many.FieldSpec())
    reserved_start = dictobj.NullableField(sb.integer_spec)
    namespace = dictobj.NullableField(sb.string_spec)
    multi = dictobj.NullableField(sb.string_spec)

class CloneField(dictobj.Spec):
    more_extras = dictobj.Field(sb.listof(sb.string_spec()))
    remove_default = dictobj.Field(sb.boolean, default=False)

class Clone(dictobj.Spec):
    cloning = dictobj.Field(sb.string_spec, wrapper=sb.required)
    fields = dictobj.Field(sb.dictof(sb.string_spec(), CloneField.FieldSpec()))
    many_options = dictobj.NullableField(Many.FieldSpec())

    def clone_struct(self, struct):
        clone = struct.clone()
        clone.many_options = self.many_options

        fields = []
        for field in struct.item_fields:
            field = field.clone()
            options = self.fields.get(field.name)
            if options:
                field.extras = field.extras + options.more_extras
                if options.remove_default:
                    field.default = None
            fields.append(field)
        clone.item_fields = fields

        return clone

class IgnoreOptions(dictobj.Spec):
    expanded = dictobj.NullableField(must_be_true_spec("expanded"))

class PacketOutputOptions(dictobj.Spec):
    include = dictobj.Field(sb.listof(sb.string_spec()))
    exclude = dictobj.Field(sb.listof(sb.string_spec()))

class output_spec(sb.Spec):
    def normalise_filled(self, meta, val):
        val = Output.FieldSpec().normalise(meta, val)
        if val.create == "packets":
            val.options = PacketOutputOptions.FieldSpec().normalise(meta.at("options"), val.options)
        return val

class non_empty_list(sb.Spec):
    def normalise_filled(self, meta, val):
        val = sb.listof(sb.string_spec()).normalise(meta, val)
        if len(val) == 0:
            raise BadSpecValue("List must not be empty", meta=meta)
        return val

class Output(dictobj.Spec):
    create = dictobj.Field(sb.string_choice_spec(["enums", "fields", "packets"]))
    options = dictobj.Field(sb.dictionary_spec)
    dest = dictobj.Field(non_empty_list(), wrapper=sb.required)
    static = dictobj.Field(sb.string_spec)

    @contextmanager
    def file(self, output_folder):
        dest = os.path.join(output_folder, *self.dest)
        directory = os.path.dirname(dest)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(dest, "w") as fle:
            def write_line(s):
                print(s, file=fle)
            yield write_line

class Adjustments(dictobj.Spec):
    changes = dictobj.Field(sb.dictof(sb.string_spec(), struct_adjustment_spec()))
    extra_imports = dictobj.Field(sb.listof(sb.string_spec()))
    namespace_order = dictobj.Field(sb.listof(sb.string_spec()))
    clones = dictobj.Field(sb.dictof(sb.string_spec(), Clone.FieldSpec()))
    types = dictobj.Field(special_types_spec())
    output = dictobj.Field(sb.listof(output_spec()))
    num_reserved_fields_in_frame = dictobj.Field(sb.integer_spec, wrapper=sb.required)
    ignore = dictobj.Field(sb.dictof(sb.string_spec(), IgnoreOptions.FieldSpec()))
    rename_namespaces = dictobj.Field(sb.dictof(sb.string_spec(), sb.string_spec()))
    invalid_field_names = dictobj.Field(sb.listof(sb.string_spec()))

    def field(self, parent, field):
        parent = self.changes.get(parent)
        if parent:
            return parent.fields.get(field)

    def packet_namespace(self, parent):
        parent = self.changes.get(parent)
        if parent:
            return parent.namespace

    def using_for(self, parent):
        parent = self.changes.get(parent)
        if parent:
            return parent.using

    def change_using(self, parent, using):
        parent = self.changes.get(parent)
        parent.using = using
        if using.full_name in self.changes:
            u = self.changes.get(using.full_name)
            parent.fields = u.fields
            parent.namespace = u.namespace

    def field_attr(self, parent, field, attr, when_missing=None):
        field = self.field(parent, field)
        if field:
            return field[attr]
        return when_missing

    def many_options(self, parent):
        parent = self.changes.get(parent)
        if parent:
            return parent.many_options

    def rename(self, name, is_struct=False):
        parent = self.changes.get(name)
        if parent:
            rename = parent.rename
            if rename is not None:
                return rename

        if is_struct:
            return camel_to_snake(name)

    def reserved_start(self, parent):
        parent = self.changes.get(parent)
        if parent and parent.reserved_start is not None:
            return parent.reserved_start
        return self.num_reserved_fields_in_frame + 1

    def field_type(self, parent, field):
        f = self.field(parent, field)
        if f:
            override = f.override_type
            if override is not None:
                return override

            override_struct = f.override_struct
            if override_struct is not None:
                return ft.StructOverrideType(override_struct)

            special_type = f.special_type
            if special_type is not None:
                if special_type not in self.types:
                    raise errors.UnknownSpecialType(wanted=special_type, available=list(self.types))
                return ft.SpecialType(self.types[special_type])

            string_type = f.string_type
            if string_type is not None:
                return ft.StringType()
