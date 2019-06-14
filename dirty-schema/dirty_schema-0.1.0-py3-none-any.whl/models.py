from enum import Enum
from functools import partial

from dirty_models import EnumField
from dirty_models.fields import ArrayField, BooleanField, FloatField, HashMapField, IntegerField, ModelField, \
    MultiTypeField, StringField, StringIdField
from dirty_models.models import BaseModel, DirtyModelMeta, FastDynamicModel

NumberField = partial(MultiTypeField, field_types=[IntegerField(), FloatField()])


class SimpleTypes(Enum):
    ARRAY = 'array'
    BOOLEAN = 'boolean'
    INTEGER = 'integer'
    NULL = 'null'
    NUMBER = 'number'
    OBJECT = 'object'
    STRING = 'string'


class JsonSchemaObjectMetaclass(DirtyModelMeta):

    def __call__(cls, data=None, *args, **kwargs):
        if cls == BaseJsonSchemaObject:
            if '$ref' in data or 'd_ref' in data or '$ref' in kwargs or 'd_ref' in kwargs:
                return JsonSchemaRefObject(data=data, *args, **kwargs)
            else:
                return JsonSchemaObject(data=data, *args, **kwargs)

        return super(JsonSchemaObjectMetaclass, cls).__call__(data=data, *args, **kwargs)


class BaseJsonSchemaObject(BaseModel, metaclass=JsonSchemaObjectMetaclass):
    pass


JsonSchemaObjectField = partial(ModelField, model_class=BaseJsonSchemaObject)


class JsonSchemaObject(BaseJsonSchemaObject):
    """
    {
        "id": "http://json-schema.org/draft-04/schema#",
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Core schema meta-schema",
        "definitions": {
            "schemaArray": {
                "type": "array",
                "minItems": 1,
                "items": { "$ref": "#" }
            },
            "positiveInteger": {
                "type": "integer",
                "minimum": 0
            },
            "positiveIntegerDefault0": {
                "allOf": [ { "$ref": "#/definitions/positiveInteger" }, { "default": 0 } ]
            },
            "simpleTypes": {
                "enum": [ "array", "boolean", "integer", "null", "number", "object", "string" ]
            },
            "stringArray": {
                "type": "array",
                "items": { "type": "string" },
                "minItems": 1,
                "uniqueItems": true
            }
        },
        "type": "object",
        "properties": {

            "enum": {
                "type": "array",
                "minItems": 1,
                "uniqueItems": true
            },
            "type": {
                "anyOf": [
                    { "$ref": "#/definitions/simpleTypes" },
                    {
                        "type": "array",
                        "items": { "$ref": "#/definitions/simpleTypes" },
                        "minItems": 1,
                        "uniqueItems": true
                    }
                ]
            },
            "format": { "type": "string" },
            "allOf": { "$ref": "#/definitions/schemaArray" },
            "anyOf": { "$ref": "#/definitions/schemaArray" },
            "oneOf": { "$ref": "#/definitions/schemaArray" },
            "not": { "$ref": "#" }
        },
        "dependencies": {
            "exclusiveMaximum": [ "maximum" ],
            "exclusiveMinimum": [ "minimum" ]
        },
        "default": {}
    }
    """

    id = StringIdField()
    d_schema = StringIdField(name="$schema")
    title = StringField()
    description = StringField()
    multipleOf = NumberField()
    maximum = NumberField()
    exclusiveMaximum = BooleanField()
    minimum = NumberField()
    exclusiveMinimum = BooleanField()
    maxLength = IntegerField()
    minLength = IntegerField()
    pattern = StringIdField()
    additionalItems = MultiTypeField(field_types=[BooleanField(),
                                                  JsonSchemaObjectField()])
    items = MultiTypeField(field_types=[ArrayField(field_type=JsonSchemaObjectField()),
                                        JsonSchemaObjectField()])
    maxItems = IntegerField()
    minItems = IntegerField()
    uniqueItems = BooleanField()

    maxProperties = IntegerField()
    minProperties = IntegerField()

    required = ArrayField(field_type=StringIdField())
    additionalProperties = MultiTypeField(field_types=[BooleanField(),
                                                       JsonSchemaObjectField()])
    definitions = HashMapField(field_type=JsonSchemaObjectField())
    properties = HashMapField(field_type=JsonSchemaObjectField())
    patternProperties = HashMapField(field_type=JsonSchemaObjectField())
    dependencies = HashMapField(field_type=MultiTypeField(field_types=[JsonSchemaObjectField(),
                                                                       ArrayField(field_type=StringIdField())]))

    enum = ArrayField(field_type=MultiTypeField(field_types=[StringIdField(),
                                                             IntegerField()]))
    type_ = MultiTypeField(name='type',
                           field_types=[ArrayField(field_type=EnumField(enum_class=SimpleTypes)),
                                        EnumField(enum_class=SimpleTypes)])
    format = StringIdField()
    allOf = ArrayField(field_type=JsonSchemaObjectField())
    anyOf = ArrayField(field_type=JsonSchemaObjectField())
    oneOf = ArrayField(field_type=JsonSchemaObjectField())
    p_not = JsonSchemaObjectField(name='not')

    default = MultiTypeField(field_types=[IntegerField(),
                                          StringField(),
                                          FloatField(),
                                          BooleanField(),
                                          ModelField(model_class=FastDynamicModel)])


class JsonSchemaRefObject(BaseJsonSchemaObject):
    d_ref = StringIdField(name="$ref")
