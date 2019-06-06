import marshmallow
import marshmallow.fields

from qsa.schema import Schema


class JenkinsConfigSchema(Schema):
    folder = marshmallow.fields.String(missing='/')


class ConfigSchema(Schema):
    jenkins = marshmallow.fields.Nested(JenkinsConfigSchema,
        missing=JenkinsConfigSchema.defaults,
        default=JenkinsConfigSchema.defaults)
