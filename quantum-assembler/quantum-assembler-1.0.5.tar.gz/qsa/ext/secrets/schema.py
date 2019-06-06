import marshmallow
import marshmallow.fields

from qsa.schema import Schema


class VaultConfigSchema(Schema):
    """Specifies a vault and its various options."""
    #: The GPG keys used to encrypt the password.
    allowed_keys = marshmallow.fields.List(marshmallow.fields.String,
        required=False, missing=list, default=list)


class SecretConfigSchema(Schema):
    default_ownership = marshmallow.fields.String(
        missing='repo', default='repo')
    vaults = marshmallow.fields.Dict(
        keys=marshmallow.fields.String(),
        values=marshmallow.fields.Nested(VaultConfigSchema),
        missing=dict,
        default=dict
    )
    allowed_keys = marshmallow.fields.List(
        marshmallow.fields.String,
        missing=list, default=list
    )


class ConfigSchema(Schema):
    secrets = marshmallow.fields.Nested(SecretConfigSchema,
        missing=SecretConfigSchema.defaults,
        default=SecretConfigSchema.defaults)
