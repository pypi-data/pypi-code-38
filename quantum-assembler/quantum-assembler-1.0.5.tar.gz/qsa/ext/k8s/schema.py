import marshmallow
import marshmallow.fields

from qsa.schema import Schema


class LoadBalancerConfigSchema(Schema):
    kind = marshmallow.fields.String(required=True,
        validate=[marshmallow.validate.OneOf(['ingress-nginx'])])
    impl = marshmallow.fields.String(required=True,
        validate=[marshmallow.validate.OneOf(['generic'])])
    ranges = marshmallow.fields.List(
        marshmallow.fields.String,
        missing=list, default=list
    )
    ip = marshmallow.fields.String(required=False)


class NamespaceConfigSchema(Schema):
    name = marshmallow.fields.String(required=True)
    environments = marshmallow.fields.List(
        marshmallow.fields.String,
        required=False,
        missing=list,
        default=list
    )
    annotations = marshmallow.fields.Dict(
        missing=dict, default=dict)
    labels = marshmallow.fields.Dict(
        missing=dict, default=dict)
    rules = marshmallow.fields.Dict(required=False,
        missing=dict, default=dict)


class DemilitarizedZoneConfigSchema(Schema):
    name = marshmallow.fields.String(required=True)
    environments = marshmallow.fields.List(
        marshmallow.fields.String,
        required=False,
        missing=list,
        default=list
    )
    loadbalancer = marshmallow.fields.Nested(
        LoadBalancerConfigSchema,
        default=None,
        missing=None
    )
    ingress = marshmallow.fields.Dict(
        missing=None, default=None)
    annotations = marshmallow.fields.Dict(
        missing=dict, default=dict)
    labels = marshmallow.fields.Dict(
        missing=dict, default=dict)
    rules = marshmallow.fields.Dict(required=False,
        missing=dict, default=dict)


class ClusterConfigSchema(Schema):
    name = marshmallow.fields.String(required=True)
    context = marshmallow.fields.String(required=False,
        allow_none=True)
    dmz = marshmallow.fields.Dict(
        keys=marshmallow.fields.String,
        values=marshmallow.fields.Nested(DemilitarizedZoneConfigSchema),
        missing=None,
        default=None
    )
    default_namespace = marshmallow.fields.String(
        missing='default', default='default')
    namespaces = marshmallow.fields.Dict(
        keys=marshmallow.fields.String,
        values=marshmallow.fields.Nested(NamespaceConfigSchema),
        missing=None,
        default=None
    )


class KubernetesConfigSchema(Schema):
    cluster = marshmallow.fields.Nested(ClusterConfigSchema,
        allow_none=True, missing=None, default=None)
    default_namespace = marshmallow.fields.String(
        missing='default', default='default')


class ConfigSchema(Schema):
    k8s = marshmallow.fields.Nested(KubernetesConfigSchema,
        missing=KubernetesConfigSchema.defaults,
        default=KubernetesConfigSchema.defaults)
