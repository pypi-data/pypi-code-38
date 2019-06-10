import marshmallow
import marshmallow.fields

from qsa.schema import Schema


class DemilitarizedZoneConfigSchema(Schema):
    name = marshmallow.fields.String(required=True)


class EnvironmentConfigSchema(Schema):
    name = marshmallow.fields.String(required=True)
    alias = marshmallow.fields.String(required=False,
        missing=None, default=None, allow_none=True)
    production = marshmallow.fields.Boolean(
        missing=False, default=False
    )
    purgeable = marshmallow.fields.Boolean(
        missing=False, default=False
    )
    annotations = marshmallow.fields.Dict(
        default=dict, missing=dict, required=False)


class DeploymentConfigSchema(Schema):
    environments = marshmallow.fields.Dict(
        keys=marshmallow.fields.String,
        values=marshmallow.fields.Nested(EnvironmentConfigSchema),
        missing=dict,
        default=dict
    )


class ConfigSchema(Schema):
    deployment = marshmallow.fields.Nested(DeploymentConfigSchema,
        missing=DeploymentConfigSchema.defaults,
        default=DeploymentConfigSchema.defaults)
