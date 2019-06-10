import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_ec2
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_route53
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-servicediscovery", "0.34.0", __name__, "aws-servicediscovery@0.34.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.BaseInstanceProps", jsii_struct_bases=[])
class BaseInstanceProps(jsii.compat.TypedDict, total=False):
    """Used when the resource that's associated with the service instance is accessible using values other than an IP address or a domain name (CNAME), i.e. for non-ip-instances.

    Stability:
        experimental
    """
    customAttributes: typing.Mapping[str,str]
    """Custom attributes of the instance.

    Default:
        none

    Stability:
        experimental
    """

    instanceId: str
    """The id of the instance resource.

    Default:
        Automatically generated name

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.AliasTargetInstanceProps", jsii_struct_bases=[BaseInstanceProps])
class AliasTargetInstanceProps(BaseInstanceProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    dnsName: str
    """DNS name of the target.

    Stability:
        experimental
    """

    service: "IService"
    """The Cloudmap service this resource is registered to.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _BaseNamespaceProps(jsii.compat.TypedDict, total=False):
    description: str
    """A description of the Namespace.

    Default:
        none

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.BaseNamespaceProps", jsii_struct_bases=[_BaseNamespaceProps])
class BaseNamespaceProps(_BaseNamespaceProps):
    """
    Stability:
        experimental
    """
    name: str
    """A name for the Namespace.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.BaseServiceProps", jsii_struct_bases=[])
class BaseServiceProps(jsii.compat.TypedDict, total=False):
    """Basic props needed to create a service in a given namespace.

    Used by HttpNamespace.createService

    Stability:
        experimental
    """
    customHealthCheck: "HealthCheckCustomConfig"
    """Structure containing failure threshold for a custom health checker. Only one of healthCheckConfig or healthCheckCustomConfig can be specified. See: https://docs.aws.amazon.com/cloud-map/latest/api/API_HealthCheckCustomConfig.html.

    Default:
        none

    Stability:
        experimental
    """

    description: str
    """A description of the service.

    Default:
        none

    Stability:
        experimental
    """

    healthCheck: "HealthCheckConfig"
    """Settings for an optional health check.

    If you specify health check settings, AWS Cloud Map associates the health
    check with the records that you specify in DnsConfig. Only one of healthCheckConfig or healthCheckCustomConfig can
    be specified. Not valid for PrivateDnsNamespaces. If you use healthCheck, you can only register IP instances to
    this service.

    Default:
        none

    Stability:
        experimental
    """

    name: str
    """A name for the Service.

    Default:
        CloudFormation-generated name

    Stability:
        experimental
    """

class CfnHttpNamespace(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.CfnHttpNamespace"):
    """A CloudFormation ``AWS::ServiceDiscovery::HttpNamespace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-httpnamespace.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ServiceDiscovery::HttpNamespace
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceDiscovery::HttpNamespace``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::ServiceDiscovery::HttpNamespace.Name``.
            description: ``AWS::ServiceDiscovery::HttpNamespace.Description``.

        Stability:
            experimental
        """
        props: CfnHttpNamespaceProps = {"name": name}

        if description is not None:
            props["description"] = description

        jsii.create(CfnHttpNamespace, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, properties: typing.Any) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            properties: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [properties])

    @classproperty
    @jsii.member(jsii_name="resourceTypeName")
    def RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "resourceTypeName")

    @property
    @jsii.member(jsii_name="httpNamespaceArn")
    def http_namespace_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "httpNamespaceArn")

    @property
    @jsii.member(jsii_name="httpNamespaceId")
    def http_namespace_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "httpNamespaceId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnHttpNamespaceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnHttpNamespaceProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::ServiceDiscovery::HttpNamespace.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-httpnamespace.html#cfn-servicediscovery-httpnamespace-description
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.CfnHttpNamespaceProps", jsii_struct_bases=[_CfnHttpNamespaceProps])
class CfnHttpNamespaceProps(_CfnHttpNamespaceProps):
    """Properties for defining a ``AWS::ServiceDiscovery::HttpNamespace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-httpnamespace.html
    Stability:
        experimental
    """
    name: str
    """``AWS::ServiceDiscovery::HttpNamespace.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-httpnamespace.html#cfn-servicediscovery-httpnamespace-name
    Stability:
        experimental
    """

class CfnInstance(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.CfnInstance"):
    """A CloudFormation ``AWS::ServiceDiscovery::Instance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-instance.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ServiceDiscovery::Instance
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, instance_attributes: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token], service_id: str, instance_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceDiscovery::Instance``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            instanceAttributes: ``AWS::ServiceDiscovery::Instance.InstanceAttributes``.
            serviceId: ``AWS::ServiceDiscovery::Instance.ServiceId``.
            instanceId: ``AWS::ServiceDiscovery::Instance.InstanceId``.

        Stability:
            experimental
        """
        props: CfnInstanceProps = {"instanceAttributes": instance_attributes, "serviceId": service_id}

        if instance_id is not None:
            props["instanceId"] = instance_id

        jsii.create(CfnInstance, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, properties: typing.Any) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            properties: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [properties])

    @classproperty
    @jsii.member(jsii_name="resourceTypeName")
    def RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "resourceTypeName")

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "instanceId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnInstanceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnInstanceProps(jsii.compat.TypedDict, total=False):
    instanceId: str
    """``AWS::ServiceDiscovery::Instance.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-instance.html#cfn-servicediscovery-instance-instanceid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.CfnInstanceProps", jsii_struct_bases=[_CfnInstanceProps])
class CfnInstanceProps(_CfnInstanceProps):
    """Properties for defining a ``AWS::ServiceDiscovery::Instance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-instance.html
    Stability:
        experimental
    """
    instanceAttributes: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ServiceDiscovery::Instance.InstanceAttributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-instance.html#cfn-servicediscovery-instance-instanceattributes
    Stability:
        experimental
    """

    serviceId: str
    """``AWS::ServiceDiscovery::Instance.ServiceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-instance.html#cfn-servicediscovery-instance-serviceid
    Stability:
        experimental
    """

class CfnPrivateDnsNamespace(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.CfnPrivateDnsNamespace"):
    """A CloudFormation ``AWS::ServiceDiscovery::PrivateDnsNamespace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-privatednsnamespace.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ServiceDiscovery::PrivateDnsNamespace
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, vpc: str, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceDiscovery::PrivateDnsNamespace``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::ServiceDiscovery::PrivateDnsNamespace.Name``.
            vpc: ``AWS::ServiceDiscovery::PrivateDnsNamespace.Vpc``.
            description: ``AWS::ServiceDiscovery::PrivateDnsNamespace.Description``.

        Stability:
            experimental
        """
        props: CfnPrivateDnsNamespaceProps = {"name": name, "vpc": vpc}

        if description is not None:
            props["description"] = description

        jsii.create(CfnPrivateDnsNamespace, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, properties: typing.Any) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            properties: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [properties])

    @classproperty
    @jsii.member(jsii_name="resourceTypeName")
    def RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "resourceTypeName")

    @property
    @jsii.member(jsii_name="privateDnsNamespaceArn")
    def private_dns_namespace_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "privateDnsNamespaceArn")

    @property
    @jsii.member(jsii_name="privateDnsNamespaceId")
    def private_dns_namespace_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "privateDnsNamespaceId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnPrivateDnsNamespaceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPrivateDnsNamespaceProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::ServiceDiscovery::PrivateDnsNamespace.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-privatednsnamespace.html#cfn-servicediscovery-privatednsnamespace-description
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.CfnPrivateDnsNamespaceProps", jsii_struct_bases=[_CfnPrivateDnsNamespaceProps])
class CfnPrivateDnsNamespaceProps(_CfnPrivateDnsNamespaceProps):
    """Properties for defining a ``AWS::ServiceDiscovery::PrivateDnsNamespace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-privatednsnamespace.html
    Stability:
        experimental
    """
    name: str
    """``AWS::ServiceDiscovery::PrivateDnsNamespace.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-privatednsnamespace.html#cfn-servicediscovery-privatednsnamespace-name
    Stability:
        experimental
    """

    vpc: str
    """``AWS::ServiceDiscovery::PrivateDnsNamespace.Vpc``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-privatednsnamespace.html#cfn-servicediscovery-privatednsnamespace-vpc
    Stability:
        experimental
    """

class CfnPublicDnsNamespace(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.CfnPublicDnsNamespace"):
    """A CloudFormation ``AWS::ServiceDiscovery::PublicDnsNamespace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-publicdnsnamespace.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ServiceDiscovery::PublicDnsNamespace
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceDiscovery::PublicDnsNamespace``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::ServiceDiscovery::PublicDnsNamespace.Name``.
            description: ``AWS::ServiceDiscovery::PublicDnsNamespace.Description``.

        Stability:
            experimental
        """
        props: CfnPublicDnsNamespaceProps = {"name": name}

        if description is not None:
            props["description"] = description

        jsii.create(CfnPublicDnsNamespace, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, properties: typing.Any) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            properties: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [properties])

    @classproperty
    @jsii.member(jsii_name="resourceTypeName")
    def RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "resourceTypeName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnPublicDnsNamespaceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="publicDnsNamespaceArn")
    def public_dns_namespace_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "publicDnsNamespaceArn")

    @property
    @jsii.member(jsii_name="publicDnsNamespaceId")
    def public_dns_namespace_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "publicDnsNamespaceId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPublicDnsNamespaceProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::ServiceDiscovery::PublicDnsNamespace.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-publicdnsnamespace.html#cfn-servicediscovery-publicdnsnamespace-description
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.CfnPublicDnsNamespaceProps", jsii_struct_bases=[_CfnPublicDnsNamespaceProps])
class CfnPublicDnsNamespaceProps(_CfnPublicDnsNamespaceProps):
    """Properties for defining a ``AWS::ServiceDiscovery::PublicDnsNamespace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-publicdnsnamespace.html
    Stability:
        experimental
    """
    name: str
    """``AWS::ServiceDiscovery::PublicDnsNamespace.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-publicdnsnamespace.html#cfn-servicediscovery-publicdnsnamespace-name
    Stability:
        experimental
    """

class CfnService(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.CfnService"):
    """A CloudFormation ``AWS::ServiceDiscovery::Service``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-service.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ServiceDiscovery::Service
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: typing.Optional[str]=None, dns_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["DnsConfigProperty"]]]=None, health_check_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["HealthCheckConfigProperty"]]]=None, health_check_custom_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["HealthCheckCustomConfigProperty"]]]=None, name: typing.Optional[str]=None, namespace_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ServiceDiscovery::Service``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::ServiceDiscovery::Service.Description``.
            dnsConfig: ``AWS::ServiceDiscovery::Service.DnsConfig``.
            healthCheckConfig: ``AWS::ServiceDiscovery::Service.HealthCheckConfig``.
            healthCheckCustomConfig: ``AWS::ServiceDiscovery::Service.HealthCheckCustomConfig``.
            name: ``AWS::ServiceDiscovery::Service.Name``.
            namespaceId: ``AWS::ServiceDiscovery::Service.NamespaceId``.

        Stability:
            experimental
        """
        props: CfnServiceProps = {}

        if description is not None:
            props["description"] = description

        if dns_config is not None:
            props["dnsConfig"] = dns_config

        if health_check_config is not None:
            props["healthCheckConfig"] = health_check_config

        if health_check_custom_config is not None:
            props["healthCheckCustomConfig"] = health_check_custom_config

        if name is not None:
            props["name"] = name

        if namespace_id is not None:
            props["namespaceId"] = namespace_id

        jsii.create(CfnService, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, properties: typing.Any) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            properties: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [properties])

    @classproperty
    @jsii.member(jsii_name="resourceTypeName")
    def RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "resourceTypeName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnServiceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="serviceArn")
    def service_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "serviceArn")

    @property
    @jsii.member(jsii_name="serviceId")
    def service_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "serviceId")

    @property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "serviceName")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DnsConfigProperty(jsii.compat.TypedDict, total=False):
        namespaceId: str
        """``CfnService.DnsConfigProperty.NamespaceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-dnsconfig.html#cfn-servicediscovery-service-dnsconfig-namespaceid
        Stability:
            experimental
        """
        routingPolicy: str
        """``CfnService.DnsConfigProperty.RoutingPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-dnsconfig.html#cfn-servicediscovery-service-dnsconfig-routingpolicy
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.CfnService.DnsConfigProperty", jsii_struct_bases=[_DnsConfigProperty])
    class DnsConfigProperty(_DnsConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-dnsconfig.html
        Stability:
            experimental
        """
        dnsRecords: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnService.DnsRecordProperty"]]]
        """``CfnService.DnsConfigProperty.DnsRecords``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-dnsconfig.html#cfn-servicediscovery-service-dnsconfig-dnsrecords
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.CfnService.DnsRecordProperty", jsii_struct_bases=[])
    class DnsRecordProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-dnsrecord.html
        Stability:
            experimental
        """
        ttl: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnService.DnsRecordProperty.TTL``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-dnsrecord.html#cfn-servicediscovery-service-dnsrecord-ttl
        Stability:
            experimental
        """

        type: str
        """``CfnService.DnsRecordProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-dnsrecord.html#cfn-servicediscovery-service-dnsrecord-type
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _HealthCheckConfigProperty(jsii.compat.TypedDict, total=False):
        failureThreshold: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnService.HealthCheckConfigProperty.FailureThreshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-healthcheckconfig.html#cfn-servicediscovery-service-healthcheckconfig-failurethreshold
        Stability:
            experimental
        """
        resourcePath: str
        """``CfnService.HealthCheckConfigProperty.ResourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-healthcheckconfig.html#cfn-servicediscovery-service-healthcheckconfig-resourcepath
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.CfnService.HealthCheckConfigProperty", jsii_struct_bases=[_HealthCheckConfigProperty])
    class HealthCheckConfigProperty(_HealthCheckConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-healthcheckconfig.html
        Stability:
            experimental
        """
        type: str
        """``CfnService.HealthCheckConfigProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-healthcheckconfig.html#cfn-servicediscovery-service-healthcheckconfig-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.CfnService.HealthCheckCustomConfigProperty", jsii_struct_bases=[])
    class HealthCheckCustomConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-healthcheckcustomconfig.html
        Stability:
            experimental
        """
        failureThreshold: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnService.HealthCheckCustomConfigProperty.FailureThreshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-servicediscovery-service-healthcheckcustomconfig.html#cfn-servicediscovery-service-healthcheckcustomconfig-failurethreshold
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.CfnServiceProps", jsii_struct_bases=[])
class CfnServiceProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::ServiceDiscovery::Service``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-service.html
    Stability:
        experimental
    """
    description: str
    """``AWS::ServiceDiscovery::Service.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-service.html#cfn-servicediscovery-service-description
    Stability:
        experimental
    """

    dnsConfig: typing.Union[aws_cdk.cdk.Token, "CfnService.DnsConfigProperty"]
    """``AWS::ServiceDiscovery::Service.DnsConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-service.html#cfn-servicediscovery-service-dnsconfig
    Stability:
        experimental
    """

    healthCheckConfig: typing.Union[aws_cdk.cdk.Token, "CfnService.HealthCheckConfigProperty"]
    """``AWS::ServiceDiscovery::Service.HealthCheckConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-service.html#cfn-servicediscovery-service-healthcheckconfig
    Stability:
        experimental
    """

    healthCheckCustomConfig: typing.Union[aws_cdk.cdk.Token, "CfnService.HealthCheckCustomConfigProperty"]
    """``AWS::ServiceDiscovery::Service.HealthCheckCustomConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-service.html#cfn-servicediscovery-service-healthcheckcustomconfig
    Stability:
        experimental
    """

    name: str
    """``AWS::ServiceDiscovery::Service.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-service.html#cfn-servicediscovery-service-name
    Stability:
        experimental
    """

    namespaceId: str
    """``AWS::ServiceDiscovery::Service.NamespaceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicediscovery-service.html#cfn-servicediscovery-service-namespaceid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.CnameInstanceBaseProps", jsii_struct_bases=[BaseInstanceProps])
class CnameInstanceBaseProps(BaseInstanceProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    instanceCname: str
    """If the service configuration includes a CNAME record, the domain name that you want Route 53 to return in response to DNS queries, for example, example.com. This value is required if the service specified by ServiceId includes settings for an CNAME record.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.CnameInstanceProps", jsii_struct_bases=[CnameInstanceBaseProps])
class CnameInstanceProps(CnameInstanceBaseProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    service: "IService"
    """The Cloudmap service this resource is registered to.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-servicediscovery.DnsRecordType")
class DnsRecordType(enum.Enum):
    """
    Stability:
        experimental
    """
    A = "A"
    """An A record.

    Stability:
        experimental
    """
    AAAA = "AAAA"
    """An AAAA record.

    Stability:
        experimental
    """
    A_AAAA = "A_AAAA"
    """Both an A and AAAA record.

    Stability:
        experimental
    """
    SRV = "SRV"
    """A Srv record.

    Stability:
        experimental
    """
    CNAME = "CNAME"
    """A CNAME record.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.DnsServiceProps", jsii_struct_bases=[BaseServiceProps])
class DnsServiceProps(BaseServiceProps, jsii.compat.TypedDict, total=False):
    """Service props needed to create a service in a given namespace.

    Used by createService() for PrivateDnsNamespace and
    PublicDnsNamespace

    Stability:
        experimental
    """
    dnsRecordType: "DnsRecordType"
    """The DNS type of the record that you want AWS Cloud Map to create.

    Supported record types
    include A, AAAA, A and AAAA (A_AAAA), CNAME, and SRV.

    Default:
        A

    Stability:
        experimental
    """

    dnsTtlSec: jsii.Number
    """The amount of time, in seconds, that you want DNS resolvers to cache the settings for this record.

    Default:
        60

    Stability:
        experimental
    """

    loadBalancer: bool
    """Whether or not this service will have an Elastic LoadBalancer registered to it as an AliasTargetInstance.

    Setting this to ``true`` correctly configures the ``routingPolicy``
    and performs some additional validation.

    Default:
        false

    Stability:
        experimental
    """

    routingPolicy: "RoutingPolicy"
    """The routing policy that you want to apply to all DNS records that AWS Cloud Map creates when you register an instance and specify this service.

    Default:
        WEIGHTED for CNAME records and when loadBalancer is true, MULTIVALUE otherwise

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.HealthCheckConfig", jsii_struct_bases=[])
class HealthCheckConfig(jsii.compat.TypedDict, total=False):
    """Settings for an optional Amazon Route 53 health check.

    If you specify settings for a health check, AWS Cloud Map
    associates the health check with all the records that you specify in DnsConfig. Only valid with a PublicDnsNamespace.

    Stability:
        experimental
    """
    failureThreshold: jsii.Number
    """The number of consecutive health checks that an endpoint must pass or fail for Route 53 to change the current status of the endpoint from unhealthy to healthy or vice versa.

    Default:
        1

    Stability:
        experimental
    """

    resourcePath: str
    """The path that you want Route 53 to request when performing health checks.

    Do not use when health check type is TCP.

    Default:
        '/'

    Stability:
        experimental
    """

    type: "HealthCheckType"
    """The type of health check that you want to create, which indicates how Route 53 determines whether an endpoint is healthy.

    Cannot be modified once created. Supported values are HTTP, HTTPS, and TCP.

    Default:
        HTTP

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.HealthCheckCustomConfig", jsii_struct_bases=[])
class HealthCheckCustomConfig(jsii.compat.TypedDict, total=False):
    """Specifies information about an optional custom health check.

    Stability:
        experimental
    """
    failureThreshold: jsii.Number
    """The number of 30-second intervals that you want Cloud Map to wait after receiving an UpdateInstanceCustomHealthStatus request before it changes the health status of a service instance.

    Default:
        1

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-servicediscovery.HealthCheckType")
class HealthCheckType(enum.Enum):
    """
    Stability:
        experimental
    """
    Http = "Http"
    """Route 53 tries to establish a TCP connection.

    If successful, Route 53 submits an HTTP request and waits for an HTTP
    status code of 200 or greater and less than 400.

    Stability:
        experimental
    """
    Https = "Https"
    """Route 53 tries to establish a TCP connection.

    If successful, Route 53 submits an HTTPS request and waits for an
    HTTP status code of 200 or greater and less than 400.  If you specify HTTPS for the value of Type, the endpoint
    must support TLS v1.0 or later.

    Stability:
        experimental
    """
    Tcp = "Tcp"
    """Route 53 tries to establish a TCP connection. If you specify TCP for Type, don't specify a value for ResourcePath.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.HttpNamespaceAttributes", jsii_struct_bases=[])
class HttpNamespaceAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    namespaceArn: str
    """Namespace ARN for the Namespace.

    Stability:
        experimental
    """

    namespaceId: str
    """Namespace Id for the Namespace.

    Stability:
        experimental
    """

    namespaceName: str
    """A name for the Namespace.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.HttpNamespaceProps", jsii_struct_bases=[BaseNamespaceProps])
class HttpNamespaceProps(BaseNamespaceProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    pass

@jsii.interface(jsii_type="@aws-cdk/aws-servicediscovery.IInstance")
class IInstance(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IInstanceProxy

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> str:
        """The id of the instance resource.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="service")
    def service(self) -> "IService":
        """The Cloudmap service this resource is registered to.

        Stability:
            experimental
        """
        ...


class _IInstanceProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-servicediscovery.IInstance"
    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> str:
        """The id of the instance resource.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "instanceId")

    @property
    @jsii.member(jsii_name="service")
    def service(self) -> "IService":
        """The Cloudmap service this resource is registered to.

        Stability:
            experimental
        """
        return jsii.get(self, "service")


@jsii.interface(jsii_type="@aws-cdk/aws-servicediscovery.INamespace")
class INamespace(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _INamespaceProxy

    @property
    @jsii.member(jsii_name="namespaceArn")
    def namespace_arn(self) -> str:
        """Namespace ARN for the Namespace.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> str:
        """Namespace Id for the Namespace.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="namespaceName")
    def namespace_name(self) -> str:
        """A name for the Namespace.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "NamespaceType":
        """Type of Namespace.

        Stability:
            experimental
        """
        ...


class _INamespaceProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-servicediscovery.INamespace"
    @property
    @jsii.member(jsii_name="namespaceArn")
    def namespace_arn(self) -> str:
        """Namespace ARN for the Namespace.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "namespaceArn")

    @property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> str:
        """Namespace Id for the Namespace.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "namespaceId")

    @property
    @jsii.member(jsii_name="namespaceName")
    def namespace_name(self) -> str:
        """A name for the Namespace.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "namespaceName")

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "NamespaceType":
        """Type of Namespace.

        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.interface(jsii_type="@aws-cdk/aws-servicediscovery.IHttpNamespace")
class IHttpNamespace(INamespace, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IHttpNamespaceProxy

    pass

class _IHttpNamespaceProxy(jsii.proxy_for(INamespace)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-servicediscovery.IHttpNamespace"
    pass

@jsii.implements(IHttpNamespace)
class HttpNamespace(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.HttpNamespace"):
    """Define an HTTP Namespace.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, description: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            name: A name for the Namespace.
            description: A description of the Namespace. Default: none

        Stability:
            experimental
        """
        props: HttpNamespaceProps = {"name": name}

        if description is not None:
            props["description"] = description

        jsii.create(HttpNamespace, self, [scope, id, props])

    @jsii.member(jsii_name="fromHttpNamespaceAttributes")
    @classmethod
    def from_http_namespace_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, namespace_arn: str, namespace_id: str, namespace_name: str) -> "IHttpNamespace":
        """
        Arguments:
            scope: -
            id: -
            attrs: -
            namespaceArn: Namespace ARN for the Namespace.
            namespaceId: Namespace Id for the Namespace.
            namespaceName: A name for the Namespace.

        Stability:
            experimental
        """
        attrs: HttpNamespaceAttributes = {"namespaceArn": namespace_arn, "namespaceId": namespace_id, "namespaceName": namespace_name}

        return jsii.sinvoke(cls, "fromHttpNamespaceAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="createService")
    def create_service(self, id: str, *, custom_health_check: typing.Optional["HealthCheckCustomConfig"]=None, description: typing.Optional[str]=None, health_check: typing.Optional["HealthCheckConfig"]=None, name: typing.Optional[str]=None) -> "Service":
        """Creates a service within the namespace.

        Arguments:
            id: -
            props: -
            customHealthCheck: Structure containing failure threshold for a custom health checker. Only one of healthCheckConfig or healthCheckCustomConfig can be specified. See: https://docs.aws.amazon.com/cloud-map/latest/api/API_HealthCheckCustomConfig.html. Default: none
            description: A description of the service. Default: none
            healthCheck: Settings for an optional health check. If you specify health check settings, AWS Cloud Map associates the health check with the records that you specify in DnsConfig. Only one of healthCheckConfig or healthCheckCustomConfig can be specified. Not valid for PrivateDnsNamespaces. If you use healthCheck, you can only register IP instances to this service. Default: none
            name: A name for the Service. Default: CloudFormation-generated name

        Stability:
            experimental
        """
        props: BaseServiceProps = {}

        if custom_health_check is not None:
            props["customHealthCheck"] = custom_health_check

        if description is not None:
            props["description"] = description

        if health_check is not None:
            props["healthCheck"] = health_check

        if name is not None:
            props["name"] = name

        return jsii.invoke(self, "createService", [id, props])

    @property
    @jsii.member(jsii_name="httpNamespaceArn")
    def http_namespace_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "httpNamespaceArn")

    @property
    @jsii.member(jsii_name="httpNamespaceId")
    def http_namespace_id(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "httpNamespaceId")

    @property
    @jsii.member(jsii_name="httpNamespaceName")
    def http_namespace_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "httpNamespaceName")

    @property
    @jsii.member(jsii_name="namespaceArn")
    def namespace_arn(self) -> str:
        """Namespace Arn for the namespace.

        Stability:
            experimental
        """
        return jsii.get(self, "namespaceArn")

    @property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> str:
        """Namespace Id for the namespace.

        Stability:
            experimental
        """
        return jsii.get(self, "namespaceId")

    @property
    @jsii.member(jsii_name="namespaceName")
    def namespace_name(self) -> str:
        """A name for the namespace.

        Stability:
            experimental
        """
        return jsii.get(self, "namespaceName")

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "NamespaceType":
        """Type of the namespace.

        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.interface(jsii_type="@aws-cdk/aws-servicediscovery.IPrivateDnsNamespace")
class IPrivateDnsNamespace(INamespace, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IPrivateDnsNamespaceProxy

    pass

class _IPrivateDnsNamespaceProxy(jsii.proxy_for(INamespace)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-servicediscovery.IPrivateDnsNamespace"
    pass

@jsii.interface(jsii_type="@aws-cdk/aws-servicediscovery.IPublicDnsNamespace")
class IPublicDnsNamespace(INamespace, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IPublicDnsNamespaceProxy

    pass

class _IPublicDnsNamespaceProxy(jsii.proxy_for(INamespace)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-servicediscovery.IPublicDnsNamespace"
    pass

@jsii.interface(jsii_type="@aws-cdk/aws-servicediscovery.IService")
class IService(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IServiceProxy

    @property
    @jsii.member(jsii_name="dnsRecordType")
    def dns_record_type(self) -> "DnsRecordType":
        """The DnsRecordType used by the service.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> "INamespace":
        """The namespace for the Cloudmap Service.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="routingPolicy")
    def routing_policy(self) -> "RoutingPolicy":
        """The Routing Policy used by the service.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="serviceArn")
    def service_arn(self) -> str:
        """The Arn of the namespace that you want to use for DNS configuration.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="serviceId")
    def service_id(self) -> str:
        """The ID of the namespace that you want to use for DNS configuration.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> str:
        """A name for the Cloudmap Service.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IServiceProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-servicediscovery.IService"
    @property
    @jsii.member(jsii_name="dnsRecordType")
    def dns_record_type(self) -> "DnsRecordType":
        """The DnsRecordType used by the service.

        Stability:
            experimental
        """
        return jsii.get(self, "dnsRecordType")

    @property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> "INamespace":
        """The namespace for the Cloudmap Service.

        Stability:
            experimental
        """
        return jsii.get(self, "namespace")

    @property
    @jsii.member(jsii_name="routingPolicy")
    def routing_policy(self) -> "RoutingPolicy":
        """The Routing Policy used by the service.

        Stability:
            experimental
        """
        return jsii.get(self, "routingPolicy")

    @property
    @jsii.member(jsii_name="serviceArn")
    def service_arn(self) -> str:
        """The Arn of the namespace that you want to use for DNS configuration.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "serviceArn")

    @property
    @jsii.member(jsii_name="serviceId")
    def service_id(self) -> str:
        """The ID of the namespace that you want to use for DNS configuration.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "serviceId")

    @property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> str:
        """A name for the Cloudmap Service.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "serviceName")


@jsii.implements(IInstance)
class InstanceBase(aws_cdk.cdk.Resource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-servicediscovery.InstanceBase"):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _InstanceBaseProxy

    def __init__(self, scope: aws_cdk.cdk.Construct, id: str) -> None:
        """Creates a new construct node.

        Arguments:
            scope: The scope in which to define this construct.
            id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.

        Stability:
            experimental
        """
        jsii.create(InstanceBase, self, [scope, id])

    @jsii.member(jsii_name="uniqueInstanceId")
    def _unique_instance_id(self) -> str:
        """Generate a unique instance Id that is safe to pass to CloudMap.

        Stability:
            experimental
        """
        return jsii.invoke(self, "uniqueInstanceId", [])

    @property
    @jsii.member(jsii_name="instanceId")
    @abc.abstractmethod
    def instance_id(self) -> str:
        """The Id of the instance.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="service")
    @abc.abstractmethod
    def service(self) -> "IService":
        """The Cloudmap service to which the instance is registered.

        Stability:
            experimental
        """
        ...


class _InstanceBaseProxy(InstanceBase, jsii.proxy_for(aws_cdk.cdk.Resource)):
    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> str:
        """The Id of the instance.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceId")

    @property
    @jsii.member(jsii_name="service")
    def service(self) -> "IService":
        """The Cloudmap service to which the instance is registered.

        Stability:
            experimental
        """
        return jsii.get(self, "service")


class AliasTargetInstance(InstanceBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.AliasTargetInstance"):
    """Instance that uses Route 53 Alias record type.

    Currently, the only resource types supported are Elastic Load
    Balancers.

    Stability:
        experimental
    resource:
        AWS::ServiceDiscovery::Instance
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, dns_name: str, service: "IService", custom_attributes: typing.Optional[typing.Mapping[str,str]]=None, instance_id: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            dnsName: DNS name of the target.
            service: The Cloudmap service this resource is registered to.
            customAttributes: Custom attributes of the instance. Default: none
            instanceId: The id of the instance resource. Default: Automatically generated name

        Stability:
            experimental
        """
        props: AliasTargetInstanceProps = {"dnsName": dns_name, "service": service}

        if custom_attributes is not None:
            props["customAttributes"] = custom_attributes

        if instance_id is not None:
            props["instanceId"] = instance_id

        jsii.create(AliasTargetInstance, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> str:
        """The Route53 DNS name of the alias target.

        Stability:
            experimental
        """
        return jsii.get(self, "dnsName")

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> str:
        """The Id of the instance.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceId")

    @property
    @jsii.member(jsii_name="service")
    def service(self) -> "IService":
        """The Cloudmap service to which the instance is registered.

        Stability:
            experimental
        """
        return jsii.get(self, "service")


class CnameInstance(InstanceBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.CnameInstance"):
    """Instance that is accessible using a domain name (CNAME).

    Stability:
        experimental
    resource:
        AWS::ServiceDiscovery::Instance
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, service: "IService", instance_cname: str, custom_attributes: typing.Optional[typing.Mapping[str,str]]=None, instance_id: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            service: The Cloudmap service this resource is registered to.
            instanceCname: If the service configuration includes a CNAME record, the domain name that you want Route 53 to return in response to DNS queries, for example, example.com. This value is required if the service specified by ServiceId includes settings for an CNAME record.
            customAttributes: Custom attributes of the instance. Default: none
            instanceId: The id of the instance resource. Default: Automatically generated name

        Stability:
            experimental
        """
        props: CnameInstanceProps = {"service": service, "instanceCname": instance_cname}

        if custom_attributes is not None:
            props["customAttributes"] = custom_attributes

        if instance_id is not None:
            props["instanceId"] = instance_id

        jsii.create(CnameInstance, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="cname")
    def cname(self) -> str:
        """The domain name returned by DNS queries for the instance.

        Stability:
            experimental
        """
        return jsii.get(self, "cname")

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> str:
        """The Id of the instance.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceId")

    @property
    @jsii.member(jsii_name="service")
    def service(self) -> "IService":
        """The Cloudmap service to which the instance is registered.

        Stability:
            experimental
        """
        return jsii.get(self, "service")


class IpInstance(InstanceBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.IpInstance"):
    """Instance that is accessible using an IP address.

    Stability:
        experimental
    resource:
        AWS::ServiceDiscovery::Instance
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, service: "IService", ipv4: typing.Optional[str]=None, ipv6: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, custom_attributes: typing.Optional[typing.Mapping[str,str]]=None, instance_id: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            service: The Cloudmap service this resource is registered to.
            ipv4: If the service that you specify contains a template for an A record, the IPv4 address that you want AWS Cloud Map to use for the value of the A record. Default: none
            ipv6: If the service that you specify contains a template for an AAAA record, the IPv6 address that you want AWS Cloud Map to use for the value of the AAAA record. Default: none
            port: The port on the endpoint that you want AWS Cloud Map to perform health checks on. This value is also used for the port value in an SRV record if the service that you specify includes an SRV record. You can also specify a default port that is applied to all instances in the Service configuration. Default: 80
            customAttributes: Custom attributes of the instance. Default: none
            instanceId: The id of the instance resource. Default: Automatically generated name

        Stability:
            experimental
        """
        props: IpInstanceProps = {"service": service}

        if ipv4 is not None:
            props["ipv4"] = ipv4

        if ipv6 is not None:
            props["ipv6"] = ipv6

        if port is not None:
            props["port"] = port

        if custom_attributes is not None:
            props["customAttributes"] = custom_attributes

        if instance_id is not None:
            props["instanceId"] = instance_id

        jsii.create(IpInstance, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> str:
        """The Id of the instance.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceId")

    @property
    @jsii.member(jsii_name="ipv4")
    def ipv4(self) -> str:
        """The Ipv4 address of the instance, or blank string if none available.

        Stability:
            experimental
        """
        return jsii.get(self, "ipv4")

    @property
    @jsii.member(jsii_name="ipv6")
    def ipv6(self) -> str:
        """The Ipv6 address of the instance, or blank string if none available.

        Stability:
            experimental
        """
        return jsii.get(self, "ipv6")

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        """The exposed port of the instance.

        Stability:
            experimental
        """
        return jsii.get(self, "port")

    @property
    @jsii.member(jsii_name="service")
    def service(self) -> "IService":
        """The Cloudmap service to which the instance is registered.

        Stability:
            experimental
        """
        return jsii.get(self, "service")


@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.IpInstanceBaseProps", jsii_struct_bases=[BaseInstanceProps])
class IpInstanceBaseProps(BaseInstanceProps, jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    ipv4: str
    """If the service that you specify contains a template for an A record, the IPv4 address that you want AWS Cloud Map to use for the value of the A record.

    Default:
        none

    Stability:
        experimental
    """

    ipv6: str
    """If the service that you specify contains a template for an AAAA record, the IPv6 address that you want AWS Cloud Map to use for the value of the AAAA record.

    Default:
        none

    Stability:
        experimental
    """

    port: jsii.Number
    """The port on the endpoint that you want AWS Cloud Map to perform health checks on.

    This value is also used for
    the port value in an SRV record if the service that you specify includes an SRV record. You can also specify a
    default port that is applied to all instances in the Service configuration.

    Default:
        80

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.IpInstanceProps", jsii_struct_bases=[IpInstanceBaseProps])
class IpInstanceProps(IpInstanceBaseProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    service: "IService"
    """The Cloudmap service this resource is registered to.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.NamespaceAttributes", jsii_struct_bases=[])
class NamespaceAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    namespaceArn: str
    """Namespace ARN for the Namespace.

    Stability:
        experimental
    """

    namespaceId: str
    """Namespace Id for the Namespace.

    Stability:
        experimental
    """

    namespaceName: str
    """A name for the Namespace.

    Stability:
        experimental
    """

    type: "NamespaceType"
    """Type of Namespace.

    Valid values: HTTP, DNS_PUBLIC, or DNS_PRIVATE

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-servicediscovery.NamespaceType")
class NamespaceType(enum.Enum):
    """
    Stability:
        experimental
    """
    Http = "Http"
    """Choose this option if you want your application to use only API calls to discover registered instances.

    Stability:
        experimental
    """
    DnsPrivate = "DnsPrivate"
    """Choose this option if you want your application to be able to discover instances using either API calls or using DNS queries in a VPC.

    Stability:
        experimental
    """
    DnsPublic = "DnsPublic"
    """Choose this option if you want your application to be able to discover instances using either API calls or using public DNS queries.

    You aren't required to use both methods.

    Stability:
        experimental
    """

class NonIpInstance(InstanceBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.NonIpInstance"):
    """Instance accessible using values other than an IP address or a domain name (CNAME). Specify the other values in Custom attributes.

    Stability:
        experimental
    resource:
        AWS::ServiceDiscovery::Instance
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, service: "IService", custom_attributes: typing.Optional[typing.Mapping[str,str]]=None, instance_id: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            service: The Cloudmap service this resource is registered to.
            customAttributes: Custom attributes of the instance. Default: none
            instanceId: The id of the instance resource. Default: Automatically generated name

        Stability:
            experimental
        """
        props: NonIpInstanceProps = {"service": service}

        if custom_attributes is not None:
            props["customAttributes"] = custom_attributes

        if instance_id is not None:
            props["instanceId"] = instance_id

        jsii.create(NonIpInstance, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> str:
        """The Id of the instance.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceId")

    @property
    @jsii.member(jsii_name="service")
    def service(self) -> "IService":
        """The Cloudmap service to which the instance is registered.

        Stability:
            experimental
        """
        return jsii.get(self, "service")


@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.NonIpInstanceBaseProps", jsii_struct_bases=[BaseInstanceProps])
class NonIpInstanceBaseProps(BaseInstanceProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    pass

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.NonIpInstanceProps", jsii_struct_bases=[NonIpInstanceBaseProps])
class NonIpInstanceProps(NonIpInstanceBaseProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    service: "IService"
    """The Cloudmap service this resource is registered to.

    Stability:
        experimental
    """

@jsii.implements(IPrivateDnsNamespace)
class PrivateDnsNamespace(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.PrivateDnsNamespace"):
    """Define a Service Discovery HTTP Namespace.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc: aws_cdk.aws_ec2.IVpc, name: str, description: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            vpc: The Amazon VPC that you want to associate the namespace with.
            name: A name for the Namespace.
            description: A description of the Namespace. Default: none

        Stability:
            experimental
        """
        props: PrivateDnsNamespaceProps = {"vpc": vpc, "name": name}

        if description is not None:
            props["description"] = description

        jsii.create(PrivateDnsNamespace, self, [scope, id, props])

    @jsii.member(jsii_name="fromPrivateDnsNamespaceAttributes")
    @classmethod
    def from_private_dns_namespace_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, namespace_arn: str, namespace_id: str, namespace_name: str) -> "IPrivateDnsNamespace":
        """
        Arguments:
            scope: -
            id: -
            attrs: -
            namespaceArn: Namespace ARN for the Namespace.
            namespaceId: Namespace Id for the Namespace.
            namespaceName: A name for the Namespace.

        Stability:
            experimental
        """
        attrs: PrivateDnsNamespaceAttributes = {"namespaceArn": namespace_arn, "namespaceId": namespace_id, "namespaceName": namespace_name}

        return jsii.sinvoke(cls, "fromPrivateDnsNamespaceAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="createService")
    def create_service(self, id: str, *, dns_record_type: typing.Optional["DnsRecordType"]=None, dns_ttl_sec: typing.Optional[jsii.Number]=None, load_balancer: typing.Optional[bool]=None, routing_policy: typing.Optional["RoutingPolicy"]=None, custom_health_check: typing.Optional["HealthCheckCustomConfig"]=None, description: typing.Optional[str]=None, health_check: typing.Optional["HealthCheckConfig"]=None, name: typing.Optional[str]=None) -> "Service":
        """Creates a service within the namespace.

        Arguments:
            id: -
            props: -
            dnsRecordType: The DNS type of the record that you want AWS Cloud Map to create. Supported record types include A, AAAA, A and AAAA (A_AAAA), CNAME, and SRV. Default: A
            dnsTtlSec: The amount of time, in seconds, that you want DNS resolvers to cache the settings for this record. Default: 60
            loadBalancer: Whether or not this service will have an Elastic LoadBalancer registered to it as an AliasTargetInstance. Setting this to ``true`` correctly configures the ``routingPolicy`` and performs some additional validation. Default: false
            routingPolicy: The routing policy that you want to apply to all DNS records that AWS Cloud Map creates when you register an instance and specify this service. Default: WEIGHTED for CNAME records and when loadBalancer is true, MULTIVALUE otherwise
            customHealthCheck: Structure containing failure threshold for a custom health checker. Only one of healthCheckConfig or healthCheckCustomConfig can be specified. See: https://docs.aws.amazon.com/cloud-map/latest/api/API_HealthCheckCustomConfig.html. Default: none
            description: A description of the service. Default: none
            healthCheck: Settings for an optional health check. If you specify health check settings, AWS Cloud Map associates the health check with the records that you specify in DnsConfig. Only one of healthCheckConfig or healthCheckCustomConfig can be specified. Not valid for PrivateDnsNamespaces. If you use healthCheck, you can only register IP instances to this service. Default: none
            name: A name for the Service. Default: CloudFormation-generated name

        Stability:
            experimental
        """
        props: DnsServiceProps = {}

        if dns_record_type is not None:
            props["dnsRecordType"] = dns_record_type

        if dns_ttl_sec is not None:
            props["dnsTtlSec"] = dns_ttl_sec

        if load_balancer is not None:
            props["loadBalancer"] = load_balancer

        if routing_policy is not None:
            props["routingPolicy"] = routing_policy

        if custom_health_check is not None:
            props["customHealthCheck"] = custom_health_check

        if description is not None:
            props["description"] = description

        if health_check is not None:
            props["healthCheck"] = health_check

        if name is not None:
            props["name"] = name

        return jsii.invoke(self, "createService", [id, props])

    @property
    @jsii.member(jsii_name="namespaceArn")
    def namespace_arn(self) -> str:
        """Namespace Arn of the namespace.

        Stability:
            experimental
        """
        return jsii.get(self, "namespaceArn")

    @property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> str:
        """Namespace Id of the PrivateDnsNamespace.

        Stability:
            experimental
        """
        return jsii.get(self, "namespaceId")

    @property
    @jsii.member(jsii_name="namespaceName")
    def namespace_name(self) -> str:
        """The name of the PrivateDnsNamespace.

        Stability:
            experimental
        """
        return jsii.get(self, "namespaceName")

    @property
    @jsii.member(jsii_name="privateDnsNamespaceArn")
    def private_dns_namespace_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "privateDnsNamespaceArn")

    @property
    @jsii.member(jsii_name="privateDnsNamespaceId")
    def private_dns_namespace_id(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "privateDnsNamespaceId")

    @property
    @jsii.member(jsii_name="privateDnsNamespaceName")
    def private_dns_namespace_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "privateDnsNamespaceName")

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "NamespaceType":
        """Type of the namespace.

        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.PrivateDnsNamespaceAttributes", jsii_struct_bases=[])
class PrivateDnsNamespaceAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    namespaceArn: str
    """Namespace ARN for the Namespace.

    Stability:
        experimental
    """

    namespaceId: str
    """Namespace Id for the Namespace.

    Stability:
        experimental
    """

    namespaceName: str
    """A name for the Namespace.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.PrivateDnsNamespaceProps", jsii_struct_bases=[BaseNamespaceProps])
class PrivateDnsNamespaceProps(BaseNamespaceProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    vpc: aws_cdk.aws_ec2.IVpc
    """The Amazon VPC that you want to associate the namespace with.

    Stability:
        experimental
    """

@jsii.implements(IPublicDnsNamespace)
class PublicDnsNamespace(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.PublicDnsNamespace"):
    """Define a Public DNS Namespace.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, description: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            name: A name for the Namespace.
            description: A description of the Namespace. Default: none

        Stability:
            experimental
        """
        props: PublicDnsNamespaceProps = {"name": name}

        if description is not None:
            props["description"] = description

        jsii.create(PublicDnsNamespace, self, [scope, id, props])

    @jsii.member(jsii_name="fromPublicDnsNamespaceAttributes")
    @classmethod
    def from_public_dns_namespace_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, namespace_arn: str, namespace_id: str, namespace_name: str) -> "IPublicDnsNamespace":
        """
        Arguments:
            scope: -
            id: -
            attrs: -
            namespaceArn: Namespace ARN for the Namespace.
            namespaceId: Namespace Id for the Namespace.
            namespaceName: A name for the Namespace.

        Stability:
            experimental
        """
        attrs: PublicDnsNamespaceAttributes = {"namespaceArn": namespace_arn, "namespaceId": namespace_id, "namespaceName": namespace_name}

        return jsii.sinvoke(cls, "fromPublicDnsNamespaceAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="createService")
    def create_service(self, id: str, *, dns_record_type: typing.Optional["DnsRecordType"]=None, dns_ttl_sec: typing.Optional[jsii.Number]=None, load_balancer: typing.Optional[bool]=None, routing_policy: typing.Optional["RoutingPolicy"]=None, custom_health_check: typing.Optional["HealthCheckCustomConfig"]=None, description: typing.Optional[str]=None, health_check: typing.Optional["HealthCheckConfig"]=None, name: typing.Optional[str]=None) -> "Service":
        """Creates a service within the namespace.

        Arguments:
            id: -
            props: -
            dnsRecordType: The DNS type of the record that you want AWS Cloud Map to create. Supported record types include A, AAAA, A and AAAA (A_AAAA), CNAME, and SRV. Default: A
            dnsTtlSec: The amount of time, in seconds, that you want DNS resolvers to cache the settings for this record. Default: 60
            loadBalancer: Whether or not this service will have an Elastic LoadBalancer registered to it as an AliasTargetInstance. Setting this to ``true`` correctly configures the ``routingPolicy`` and performs some additional validation. Default: false
            routingPolicy: The routing policy that you want to apply to all DNS records that AWS Cloud Map creates when you register an instance and specify this service. Default: WEIGHTED for CNAME records and when loadBalancer is true, MULTIVALUE otherwise
            customHealthCheck: Structure containing failure threshold for a custom health checker. Only one of healthCheckConfig or healthCheckCustomConfig can be specified. See: https://docs.aws.amazon.com/cloud-map/latest/api/API_HealthCheckCustomConfig.html. Default: none
            description: A description of the service. Default: none
            healthCheck: Settings for an optional health check. If you specify health check settings, AWS Cloud Map associates the health check with the records that you specify in DnsConfig. Only one of healthCheckConfig or healthCheckCustomConfig can be specified. Not valid for PrivateDnsNamespaces. If you use healthCheck, you can only register IP instances to this service. Default: none
            name: A name for the Service. Default: CloudFormation-generated name

        Stability:
            experimental
        """
        props: DnsServiceProps = {}

        if dns_record_type is not None:
            props["dnsRecordType"] = dns_record_type

        if dns_ttl_sec is not None:
            props["dnsTtlSec"] = dns_ttl_sec

        if load_balancer is not None:
            props["loadBalancer"] = load_balancer

        if routing_policy is not None:
            props["routingPolicy"] = routing_policy

        if custom_health_check is not None:
            props["customHealthCheck"] = custom_health_check

        if description is not None:
            props["description"] = description

        if health_check is not None:
            props["healthCheck"] = health_check

        if name is not None:
            props["name"] = name

        return jsii.invoke(self, "createService", [id, props])

    @property
    @jsii.member(jsii_name="namespaceArn")
    def namespace_arn(self) -> str:
        """Namespace Arn for the namespace.

        Stability:
            experimental
        """
        return jsii.get(self, "namespaceArn")

    @property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> str:
        """Namespace Id for the namespace.

        Stability:
            experimental
        """
        return jsii.get(self, "namespaceId")

    @property
    @jsii.member(jsii_name="namespaceName")
    def namespace_name(self) -> str:
        """A name for the namespace.

        Stability:
            experimental
        """
        return jsii.get(self, "namespaceName")

    @property
    @jsii.member(jsii_name="publicDnsNamespaceArn")
    def public_dns_namespace_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "publicDnsNamespaceArn")

    @property
    @jsii.member(jsii_name="publicDnsNamespaceId")
    def public_dns_namespace_id(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "publicDnsNamespaceId")

    @property
    @jsii.member(jsii_name="publicDnsNamespaceName")
    def public_dns_namespace_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "publicDnsNamespaceName")

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "NamespaceType":
        """Type of the namespace.

        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.PublicDnsNamespaceAttributes", jsii_struct_bases=[])
class PublicDnsNamespaceAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    namespaceArn: str
    """Namespace ARN for the Namespace.

    Stability:
        experimental
    """

    namespaceId: str
    """Namespace Id for the Namespace.

    Stability:
        experimental
    """

    namespaceName: str
    """A name for the Namespace.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.PublicDnsNamespaceProps", jsii_struct_bases=[BaseNamespaceProps])
class PublicDnsNamespaceProps(BaseNamespaceProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    pass

@jsii.enum(jsii_type="@aws-cdk/aws-servicediscovery.RoutingPolicy")
class RoutingPolicy(enum.Enum):
    """
    Stability:
        experimental
    """
    Weighted = "Weighted"
    """Route 53 returns the applicable value from one randomly selected instance from among the instances that you registered using the same service.

    Stability:
        experimental
    """
    Multivalue = "Multivalue"
    """If you define a health check for the service and the health check is healthy, Route 53 returns the applicable value for up to eight instances.

    Stability:
        experimental
    """

@jsii.implements(IService)
class Service(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-servicediscovery.Service"):
    """Define a CloudMap Service.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, namespace: "INamespace", dns_record_type: typing.Optional["DnsRecordType"]=None, dns_ttl_sec: typing.Optional[jsii.Number]=None, load_balancer: typing.Optional[bool]=None, routing_policy: typing.Optional["RoutingPolicy"]=None, custom_health_check: typing.Optional["HealthCheckCustomConfig"]=None, description: typing.Optional[str]=None, health_check: typing.Optional["HealthCheckConfig"]=None, name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            namespace: The ID of the namespace that you want to use for DNS configuration.
            dnsRecordType: The DNS type of the record that you want AWS Cloud Map to create. Supported record types include A, AAAA, A and AAAA (A_AAAA), CNAME, and SRV. Default: A
            dnsTtlSec: The amount of time, in seconds, that you want DNS resolvers to cache the settings for this record. Default: 60
            loadBalancer: Whether or not this service will have an Elastic LoadBalancer registered to it as an AliasTargetInstance. Setting this to ``true`` correctly configures the ``routingPolicy`` and performs some additional validation. Default: false
            routingPolicy: The routing policy that you want to apply to all DNS records that AWS Cloud Map creates when you register an instance and specify this service. Default: WEIGHTED for CNAME records and when loadBalancer is true, MULTIVALUE otherwise
            customHealthCheck: Structure containing failure threshold for a custom health checker. Only one of healthCheckConfig or healthCheckCustomConfig can be specified. See: https://docs.aws.amazon.com/cloud-map/latest/api/API_HealthCheckCustomConfig.html. Default: none
            description: A description of the service. Default: none
            healthCheck: Settings for an optional health check. If you specify health check settings, AWS Cloud Map associates the health check with the records that you specify in DnsConfig. Only one of healthCheckConfig or healthCheckCustomConfig can be specified. Not valid for PrivateDnsNamespaces. If you use healthCheck, you can only register IP instances to this service. Default: none
            name: A name for the Service. Default: CloudFormation-generated name

        Stability:
            experimental
        """
        props: ServiceProps = {"namespace": namespace}

        if dns_record_type is not None:
            props["dnsRecordType"] = dns_record_type

        if dns_ttl_sec is not None:
            props["dnsTtlSec"] = dns_ttl_sec

        if load_balancer is not None:
            props["loadBalancer"] = load_balancer

        if routing_policy is not None:
            props["routingPolicy"] = routing_policy

        if custom_health_check is not None:
            props["customHealthCheck"] = custom_health_check

        if description is not None:
            props["description"] = description

        if health_check is not None:
            props["healthCheck"] = health_check

        if name is not None:
            props["name"] = name

        jsii.create(Service, self, [scope, id, props])

    @jsii.member(jsii_name="fromServiceAttributes")
    @classmethod
    def from_service_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, dns_record_type: "DnsRecordType", routing_policy: "RoutingPolicy", service_arn: str, service_id: str, service_name: str) -> "IService":
        """
        Arguments:
            scope: -
            id: -
            attrs: -
            dnsRecordType: 
            routingPolicy: 
            serviceArn: 
            serviceId: 
            serviceName: 

        Stability:
            experimental
        """
        attrs: ServiceAttributes = {"dnsRecordType": dns_record_type, "routingPolicy": routing_policy, "serviceArn": service_arn, "serviceId": service_id, "serviceName": service_name}

        return jsii.sinvoke(cls, "fromServiceAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="registerCnameInstance")
    def register_cname_instance(self, id: str, *, instance_cname: str, custom_attributes: typing.Optional[typing.Mapping[str,str]]=None, instance_id: typing.Optional[str]=None) -> "IInstance":
        """Registers a resource that is accessible using a CNAME.

        Arguments:
            id: -
            props: -
            instanceCname: If the service configuration includes a CNAME record, the domain name that you want Route 53 to return in response to DNS queries, for example, example.com. This value is required if the service specified by ServiceId includes settings for an CNAME record.
            customAttributes: Custom attributes of the instance. Default: none
            instanceId: The id of the instance resource. Default: Automatically generated name

        Stability:
            experimental
        """
        props: CnameInstanceBaseProps = {"instanceCname": instance_cname}

        if custom_attributes is not None:
            props["customAttributes"] = custom_attributes

        if instance_id is not None:
            props["instanceId"] = instance_id

        return jsii.invoke(self, "registerCnameInstance", [id, props])

    @jsii.member(jsii_name="registerIpInstance")
    def register_ip_instance(self, id: str, *, ipv4: typing.Optional[str]=None, ipv6: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, custom_attributes: typing.Optional[typing.Mapping[str,str]]=None, instance_id: typing.Optional[str]=None) -> "IInstance":
        """Registers a resource that is accessible using an IP address.

        Arguments:
            id: -
            props: -
            ipv4: If the service that you specify contains a template for an A record, the IPv4 address that you want AWS Cloud Map to use for the value of the A record. Default: none
            ipv6: If the service that you specify contains a template for an AAAA record, the IPv6 address that you want AWS Cloud Map to use for the value of the AAAA record. Default: none
            port: The port on the endpoint that you want AWS Cloud Map to perform health checks on. This value is also used for the port value in an SRV record if the service that you specify includes an SRV record. You can also specify a default port that is applied to all instances in the Service configuration. Default: 80
            customAttributes: Custom attributes of the instance. Default: none
            instanceId: The id of the instance resource. Default: Automatically generated name

        Stability:
            experimental
        """
        props: IpInstanceBaseProps = {}

        if ipv4 is not None:
            props["ipv4"] = ipv4

        if ipv6 is not None:
            props["ipv6"] = ipv6

        if port is not None:
            props["port"] = port

        if custom_attributes is not None:
            props["customAttributes"] = custom_attributes

        if instance_id is not None:
            props["instanceId"] = instance_id

        return jsii.invoke(self, "registerIpInstance", [id, props])

    @jsii.member(jsii_name="registerLoadBalancer")
    def register_load_balancer(self, id: str, load_balancer: aws_cdk.aws_elasticloadbalancingv2.ILoadBalancerV2, custom_attributes: typing.Optional[typing.Mapping[str,str]]=None) -> "IInstance":
        """Registers an ELB as a new instance with unique name instanceId in this service.

        Arguments:
            id: -
            loadBalancer: -
            customAttributes: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "registerLoadBalancer", [id, load_balancer, custom_attributes])

    @jsii.member(jsii_name="registerNonIpInstance")
    def register_non_ip_instance(self, id: str, *, custom_attributes: typing.Optional[typing.Mapping[str,str]]=None, instance_id: typing.Optional[str]=None) -> "IInstance":
        """Registers a resource that is accessible using values other than an IP address or a domain name (CNAME).

        Arguments:
            id: -
            props: -
            customAttributes: Custom attributes of the instance. Default: none
            instanceId: The id of the instance resource. Default: Automatically generated name

        Stability:
            experimental
        """
        props: NonIpInstanceBaseProps = {}

        if custom_attributes is not None:
            props["customAttributes"] = custom_attributes

        if instance_id is not None:
            props["instanceId"] = instance_id

        return jsii.invoke(self, "registerNonIpInstance", [id, props])

    @property
    @jsii.member(jsii_name="dnsRecordType")
    def dns_record_type(self) -> "DnsRecordType":
        """The DnsRecordType used by the service.

        Stability:
            experimental
        """
        return jsii.get(self, "dnsRecordType")

    @property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> "INamespace":
        """The namespace for the Cloudmap Service.

        Stability:
            experimental
        """
        return jsii.get(self, "namespace")

    @property
    @jsii.member(jsii_name="routingPolicy")
    def routing_policy(self) -> "RoutingPolicy":
        """The Routing Policy used by the service.

        Stability:
            experimental
        """
        return jsii.get(self, "routingPolicy")

    @property
    @jsii.member(jsii_name="serviceArn")
    def service_arn(self) -> str:
        """The Arn of the namespace that you want to use for DNS configuration.

        Stability:
            experimental
        """
        return jsii.get(self, "serviceArn")

    @property
    @jsii.member(jsii_name="serviceId")
    def service_id(self) -> str:
        """The ID of the namespace that you want to use for DNS configuration.

        Stability:
            experimental
        """
        return jsii.get(self, "serviceId")

    @property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> str:
        """A name for the Cloudmap Service.

        Stability:
            experimental
        """
        return jsii.get(self, "serviceName")


@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.ServiceAttributes", jsii_struct_bases=[])
class ServiceAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    dnsRecordType: "DnsRecordType"
    """
    Stability:
        experimental
    """

    routingPolicy: "RoutingPolicy"
    """
    Stability:
        experimental
    """

    serviceArn: str
    """
    Stability:
        experimental
    """

    serviceId: str
    """
    Stability:
        experimental
    """

    serviceName: str
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-servicediscovery.ServiceProps", jsii_struct_bases=[DnsServiceProps])
class ServiceProps(DnsServiceProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    namespace: "INamespace"
    """The ID of the namespace that you want to use for DNS configuration.

    Stability:
        experimental
    """

__all__ = ["AliasTargetInstance", "AliasTargetInstanceProps", "BaseInstanceProps", "BaseNamespaceProps", "BaseServiceProps", "CfnHttpNamespace", "CfnHttpNamespaceProps", "CfnInstance", "CfnInstanceProps", "CfnPrivateDnsNamespace", "CfnPrivateDnsNamespaceProps", "CfnPublicDnsNamespace", "CfnPublicDnsNamespaceProps", "CfnService", "CfnServiceProps", "CnameInstance", "CnameInstanceBaseProps", "CnameInstanceProps", "DnsRecordType", "DnsServiceProps", "HealthCheckConfig", "HealthCheckCustomConfig", "HealthCheckType", "HttpNamespace", "HttpNamespaceAttributes", "HttpNamespaceProps", "IHttpNamespace", "IInstance", "INamespace", "IPrivateDnsNamespace", "IPublicDnsNamespace", "IService", "InstanceBase", "IpInstance", "IpInstanceBaseProps", "IpInstanceProps", "NamespaceAttributes", "NamespaceType", "NonIpInstance", "NonIpInstanceBaseProps", "NonIpInstanceProps", "PrivateDnsNamespace", "PrivateDnsNamespaceAttributes", "PrivateDnsNamespaceProps", "PublicDnsNamespace", "PublicDnsNamespaceAttributes", "PublicDnsNamespaceProps", "RoutingPolicy", "Service", "ServiceAttributes", "ServiceProps", "__jsii_assembly__"]

publication.publish()
