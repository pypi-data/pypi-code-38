import marshmallow
import marshmallow.fields

from qsa.schema import Schema


class MountedSecretSchema(Schema):
    name = marshmallow.fields.String(required=True)
    path = marshmallow.fields.String(required=True)
    kind = marshmallow.fields.String(required=True)


class RegistryCredentialSchema(Schema):
    url = marshmallow.fields.String()
    secret = marshmallow.fields.String(default=None, allow_none=True)


class RegistryConfigSchema(Schema):
    default = marshmallow.fields.Nested(RegistryCredentialSchema,
        default=lambda: {'url': 'docker.io'})
    base = marshmallow.fields.Nested(RegistryCredentialSchema,
        default=lambda: {'url': 'docker.io'})
    build = marshmallow.fields.Nested(RegistryCredentialSchema,
        default=lambda: {'url': 'docker.io'})
    publish = marshmallow.fields.Nested(RegistryCredentialSchema,
        default=lambda: {'url': 'docker.io'})


class OriginConfigSchema(Schema):
    remote = marshmallow.fields.String(missing=None,
        allow_none=True)
    credentials = marshmallow.fields.String(missing=None,
        allow_none=True)
    poll = marshmallow.fields.String(missing='noop', default='noop')
    webhook = marshmallow.fields.String(missing='noop', default='noop')


class ContinuousIntegrationConfigSchema(Schema):
    using = marshmallow.fields.String(required=True, default='noop',
        validate=[marshmallow.validate.OneOf(['noop', 'jenkins', 'gitlab', 'gitlab+jenkins'])])
    container_registries = marshmallow.fields.Nested(
        RegistryConfigSchema,
        default=RegistryConfigSchema.defaults
    )
    strategy = marshmallow.fields.String(
        validate=marshmallow.validate.OneOf(
            ['noop','trunk','trunk+tagged','gitflow','gitflow+tagged']),
        required=False,
        missing='noop'
    )
    origin = marshmallow.fields.Nested(OriginConfigSchema,
        missing=OriginConfigSchema.defaults,
        default=OriginConfigSchema.defaults)
    mounted_secrets = marshmallow.fields.Nested(MountedSecretSchema,
        missing=list, default=list, many=True)
    notifications = marshmallow.fields.Dict(
        missing=dict,
        default=dict,
        keys=marshmallow.fields.String,
        values=marshmallow.fields.Dict
    )

class ConfigSchema(Schema):
    ci = marshmallow.fields.Nested(ContinuousIntegrationConfigSchema,
        required=True, default=ContinuousIntegrationConfigSchema.defaults)
