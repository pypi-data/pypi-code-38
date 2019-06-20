from marshmallow import Schema, fields, post_load, validates_schema, ValidationError

from sidecar.const import ServiceType
from sidecar.messaging_service import MessagingConnectionProperties
from sidecar.model.objects import AwsSidecarConfiguration, AzureSidecarConfiguration, \
    KubernetesSidecarConfiguration, SidecarApplication, SidecarTerraformService, Script, \
    TerraformServiceModule, InputParameter


class MessagingConnectionPropertiesSchema(Schema):
    queue = fields.Str()
    usessl = fields.Boolean()
    expires = fields.Integer()
    queuetype = fields.Str()
    port = fields.Integer()
    virtualhost = fields.Str()
    routingkey = fields.Str()
    exchange = fields.Str()
    password = fields.Str()
    user = fields.Str()
    host = fields.Str()

    @post_load
    def make(self, data):
        return MessagingConnectionProperties(**data)

    @validates_schema
    def validate_numbers(self, data):
        if not data:
            raise ValidationError("Missing MessagingConnectionProperties")

    class Meta:
        strict = True


class ScriptSchema(Schema):
    path = fields.Str(required=True)
    name = fields.Str(required=True)
    headers = fields.Dict(required=True)

    @post_load
    def make(self, data):
        return Script(**data)

    class Meta:
        strict = True


class TerraformServiceModuleSchema(Schema):
    source = fields.Str(required=False, allow_none=True)
    version = fields.Str(required=False, allow_none=True)

    @post_load
    def make(self, data):
        return TerraformServiceModule(**data)

    class Meta:
        strict = True


class InputParameterSchema(Schema):
    name = fields.Str(required=True)
    value = fields.Str(required=True)

    @post_load
    def make(self, data):
        return InputParameter(**data)

    class Meta:
        strict = True


class SidecarServiceSchema(Schema):
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    dependencies = fields.List(fields.Str)
    inputs = fields.List(fields.Nested(InputParameterSchema()), allow_none=True)
    outputs = fields.List(fields.Str, allow_none=True, required=False)

    # TODO: find a better way to deal with it in the future ...
    terraform_module = fields.Nested(TerraformServiceModuleSchema(), required=False, allow_none=True)
    terraform_version = fields.Str(required=False, allow_none=True)
    tfvars_file = fields.Nested(ScriptSchema(), required=False, allow_none=True)

    @post_load
    def make(self, data):
        if data["type"] == ServiceType.TerraForm:
            return SidecarTerraformService(**data)

    @validates_schema
    def validate_numbers(self, data):
        if data['type'] != ServiceType.TerraForm:
            raise ValidationError("service '{}' must be of type '{}' only".format(data['name'], ServiceType.TerraForm))

    class Meta:
        strict = True


class SidecarApplicationSchema(Schema):
    default_health_check_ports_to_test = fields.List(fields.Integer())
    healthcheck_timeout = fields.Integer()
    env = fields.Dict(values=fields.Str(), keys=fields.Str())
    dependencies = fields.List(fields.Str())
    instances_count = fields.Integer()
    healthcheck_script = fields.Str()
    has_public_access = fields.Bool()
    outputs = fields.List(fields.Str(), allow_none=True, required=False)

    @post_load
    def make(self, data):
        data["name"] = "yet-to-be-filled"  # remove when json will become json and not dynamic field named
        return SidecarApplication(**data)

    class Meta:
        strict = True


class SidecarConfigurationSchema(Schema):
    environment = fields.Str()
    provider = fields.Str()
    sandbox_id = fields.Str()
    production_id = fields.Str(allow_none=True)
    space_id = fields.Str()
    cloud_external_key = fields.Str()
    apps = fields.Dict(keys=fields.Str(), values=fields.Nested(SidecarApplicationSchema()))
    services = fields.List(fields.Nested(SidecarServiceSchema()))
    messaging = fields.Nested(MessagingConnectionPropertiesSchema(), required=True)
    env_type = fields.Str()

    @post_load
    def make(self, data):
        for k, v in data["apps"].items():
            v.name = k
        data["apps"] = [v for k, v in data["apps"].items()]

    @validates_schema
    def validate_numbers(self, data):
        if data['apps'] is None or len(data['apps']) == 0:
            raise ValidationError("Cannot have 0 applications")

    class Meta:
        strict = True


class KubernetesSidecarConfigurationSchema(SidecarConfigurationSchema):
    kub_api_address = fields.Str()

    @post_load
    def make(self, data):
        super().make(data)
        data.pop('provider', None)
        return KubernetesSidecarConfiguration(**data)

    class Meta:
        strict = True


class AwsSidecarConfigurationSchema(SidecarConfigurationSchema):
    region_name = fields.Str()
    onboarding_region = fields.Str(allow_none=True)
    data_table_name = fields.Str()

    @post_load
    def make(self, data):
        super().make(data)
        data.pop('provider', None)
        return AwsSidecarConfiguration(**data)

    class Meta:
        strict = True


class AzureSidecarConfigurationSchema(SidecarConfigurationSchema):
    tenant_id = fields.Str()
    application_secret = fields.Str()
    application_id = fields.Str()
    subscription_id = fields.Str()
    management_resource_group = fields.Str()

    @post_load
    def make(self, data):
        super().make(data)
        data.pop('provider', None)
        return AzureSidecarConfiguration(**data)

    class Meta:
        strict = True
