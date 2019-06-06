import marshmallow.fields

from qsa.schema import Schema


class ConfigSchema(Schema):
    version = marshmallow.fields.String(required=True)
