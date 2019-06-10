import marshmallow
import marshmallow.fields

from qsa.schema import Schema


class ProjectConfigSchema(Schema):
    name = marshmallow.fields.String(missing=None, allow_none=True)
    display_name = marshmallow.fields.String(missing=None)
    type = marshmallow.fields.String(required=True)
    language = marshmallow.fields.String(required=False, allow_none=True,
        missing=None)


class ConfigSchema(Schema):
    project = marshmallow.fields.Nested(ProjectConfigSchema,
        missing=ProjectConfigSchema.defaults)
