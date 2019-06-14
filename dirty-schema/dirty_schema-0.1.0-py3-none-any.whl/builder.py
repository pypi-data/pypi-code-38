from typing import Type

from dirty_models import ArrayField, BaseModel, BooleanField, DateField, DateTimeField, EnumField, FloatField, \
    HashMapField, IntegerField, ModelField, MultiTypeField, StringField, StringIdField, TimeField, TimedeltaField
from dirty_models.fields import BaseField
from dirty_validators.complex import ModelValidateMixin, Required

from dirty_schema.models import JsonSchemaObject, SimpleTypes


class Context:

    def __init__(self):
        self._definitions = {}

    def get_reference_from_definition(self, definition: JsonSchemaObject):
        for ref, d in self._definitions.items():
            pass


class Builder:

    def __init__(self, context: Context = None, *, def_read_only: bool = True, to_update: bool = False):
        self._def_read_only = def_read_only
        self._to_update = to_update
        self._context = context or Context()

    def generate_from_model_validator(self, validator: Type[ModelValidateMixin], schema: JsonSchemaObject = None):
        schema = schema or JsonSchemaObject(type=SimpleTypes.OBJECT)

        self.generate_from_model(validator.__modelclass__, schema)

        required = []
        for name, field_validator in validator.spec.items():
            if isinstance(field_validator, Required):
                required.append(validator.__modelclass__.get_real_name(name))

        if len(required):
            schema.required = required

        return schema

    def generate_from_model(self, model_class: Type[BaseModel], schema: JsonSchemaObject = None):
        schema = schema or JsonSchemaObject(type=SimpleTypes.OBJECT)

        schema.properties = {name: self.map_field_type(field)
                             for name, field in model_class.get_structure().items()
                             if self._def_read_only or not field.read_only}

        return schema

    def map_field_type(self, field: BaseField, metadata=True) -> JsonSchemaObject:
        if metadata:
            schema = JsonSchemaObject(default=field.default if not callable(field.default) else field.default(),
                                      title=field.name,
                                      description=field.__doc__)
        else:
            schema = JsonSchemaObject()

        if isinstance(field, StringField):
            schema.type = SimpleTypes.STRING
            if isinstance(field, StringIdField):
                schema.minLength = 1
        elif isinstance(field, BooleanField):
            schema.type = SimpleTypes.BOOLEAN
        elif isinstance(field, IntegerField):
            schema.type = SimpleTypes.INTEGER
        elif isinstance(field, FloatField):
            schema.type = SimpleTypes.NUMBER
        elif isinstance(field, TimeField):
            schema.type = SimpleTypes.STRING
            schema.format = 'time'
        elif isinstance(field, DateField):
            schema.type = SimpleTypes.STRING
            schema.format = 'date'
        elif isinstance(field, DateTimeField):
            schema.type = SimpleTypes.STRING
            schema.format = 'date-time'
        elif isinstance(field, TimedeltaField):
            schema.type = SimpleTypes.NUMBER
        elif isinstance(field, EnumField):
            schema.type = [SimpleTypes.INTEGER, SimpleTypes.STRING]
            schema.enum = [v for v in field.enum_class.__members__.values()]
        elif isinstance(field, ArrayField):
            schema.type = SimpleTypes.ARRAY

            schema.items = self.map_field_type(field.field_type, metadata=False)
        elif isinstance(field, MultiTypeField):
            schema.anyOf = [self.map_field_type(f, metadata=False)
                            for f in field.field_types]
        elif isinstance(field, ModelField):
            schema.type = SimpleTypes.OBJECT

            self.generate_from_model(field.model_class, schema=schema)
        elif isinstance(field, HashMapField):
            schema.type = SimpleTypes.OBJECT

            schema.additionalItems = self.map_field_type(field.field_type, metadata=False)
            self.generate_from_model(field.model_class, schema=schema)

        return schema
