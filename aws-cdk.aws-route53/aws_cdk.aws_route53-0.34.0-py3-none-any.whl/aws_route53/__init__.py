import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_ec2
import aws_cdk.aws_logs
import aws_cdk.cdk
import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-route53", "0.34.0", __name__, "aws-route53@0.34.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-route53.AliasRecordTargetConfig", jsii_struct_bases=[])
class AliasRecordTargetConfig(jsii.compat.TypedDict):
    """Represents the properties of an alias target destination.

    Stability:
        experimental
    """
    dnsName: str
    """DNS name of the target.

    Stability:
        experimental
    """

    hostedZoneId: str
    """Hosted zone ID of the target.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.CaaRecordValue", jsii_struct_bases=[])
class CaaRecordValue(jsii.compat.TypedDict):
    """Properties for a CAA record value.

    Stability:
        experimental
    """
    flag: jsii.Number
    """The flag.

    Stability:
        experimental
    """

    tag: "CaaTag"
    """The tag.

    Stability:
        experimental
    """

    value: str
    """The value associated with the tag.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-route53.CaaTag")
class CaaTag(enum.Enum):
    """The CAA tag.

    Stability:
        experimental
    """
    ISSUE = "ISSUE"
    """Explicity authorizes a single certificate authority to issue a certificate (any type) for the hostname.

    Stability:
        experimental
    """
    ISSUEWILD = "ISSUEWILD"
    """Explicity authorizes a single certificate authority to issue a wildcard certificate (and only wildcard) for the hostname.

    Stability:
        experimental
    """
    IODEF = "IODEF"
    """Specifies a URL to which a certificate authority may report policy violations.

    Stability:
        experimental
    """

class CfnHealthCheck(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.CfnHealthCheck"):
    """A CloudFormation ``AWS::Route53::HealthCheck``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-healthcheck.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Route53::HealthCheck
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, health_check_config: typing.Union["HealthCheckConfigProperty", aws_cdk.cdk.Token], health_check_tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "HealthCheckTagProperty"]]]]]=None) -> None:
        """Create a new ``AWS::Route53::HealthCheck``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            healthCheckConfig: ``AWS::Route53::HealthCheck.HealthCheckConfig``.
            healthCheckTags: ``AWS::Route53::HealthCheck.HealthCheckTags``.

        Stability:
            experimental
        """
        props: CfnHealthCheckProps = {"healthCheckConfig": health_check_config}

        if health_check_tags is not None:
            props["healthCheckTags"] = health_check_tags

        jsii.create(CfnHealthCheck, self, [scope, id, props])

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
    @jsii.member(jsii_name="healthCheckId")
    def health_check_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "healthCheckId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnHealthCheckProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnHealthCheck.AlarmIdentifierProperty", jsii_struct_bases=[])
    class AlarmIdentifierProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-alarmidentifier.html
        Stability:
            experimental
        """
        name: str
        """``CfnHealthCheck.AlarmIdentifierProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-alarmidentifier.html#cfn-route53-healthcheck-alarmidentifier-name
        Stability:
            experimental
        """

        region: str
        """``CfnHealthCheck.AlarmIdentifierProperty.Region``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-alarmidentifier.html#cfn-route53-healthcheck-alarmidentifier-region
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _HealthCheckConfigProperty(jsii.compat.TypedDict, total=False):
        alarmIdentifier: typing.Union[aws_cdk.cdk.Token, "CfnHealthCheck.AlarmIdentifierProperty"]
        """``CfnHealthCheck.HealthCheckConfigProperty.AlarmIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-alarmidentifier
        Stability:
            experimental
        """
        childHealthChecks: typing.List[str]
        """``CfnHealthCheck.HealthCheckConfigProperty.ChildHealthChecks``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-childhealthchecks
        Stability:
            experimental
        """
        enableSni: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnHealthCheck.HealthCheckConfigProperty.EnableSNI``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-enablesni
        Stability:
            experimental
        """
        failureThreshold: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnHealthCheck.HealthCheckConfigProperty.FailureThreshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-failurethreshold
        Stability:
            experimental
        """
        fullyQualifiedDomainName: str
        """``CfnHealthCheck.HealthCheckConfigProperty.FullyQualifiedDomainName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-fullyqualifieddomainname
        Stability:
            experimental
        """
        healthThreshold: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnHealthCheck.HealthCheckConfigProperty.HealthThreshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-healththreshold
        Stability:
            experimental
        """
        insufficientDataHealthStatus: str
        """``CfnHealthCheck.HealthCheckConfigProperty.InsufficientDataHealthStatus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-insufficientdatahealthstatus
        Stability:
            experimental
        """
        inverted: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnHealthCheck.HealthCheckConfigProperty.Inverted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-inverted
        Stability:
            experimental
        """
        ipAddress: str
        """``CfnHealthCheck.HealthCheckConfigProperty.IPAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-ipaddress
        Stability:
            experimental
        """
        measureLatency: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnHealthCheck.HealthCheckConfigProperty.MeasureLatency``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-measurelatency
        Stability:
            experimental
        """
        port: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnHealthCheck.HealthCheckConfigProperty.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-port
        Stability:
            experimental
        """
        regions: typing.List[str]
        """``CfnHealthCheck.HealthCheckConfigProperty.Regions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-regions
        Stability:
            experimental
        """
        requestInterval: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnHealthCheck.HealthCheckConfigProperty.RequestInterval``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-requestinterval
        Stability:
            experimental
        """
        resourcePath: str
        """``CfnHealthCheck.HealthCheckConfigProperty.ResourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-resourcepath
        Stability:
            experimental
        """
        searchString: str
        """``CfnHealthCheck.HealthCheckConfigProperty.SearchString``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-searchstring
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnHealthCheck.HealthCheckConfigProperty", jsii_struct_bases=[_HealthCheckConfigProperty])
    class HealthCheckConfigProperty(_HealthCheckConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html
        Stability:
            experimental
        """
        type: str
        """``CfnHealthCheck.HealthCheckConfigProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnHealthCheck.HealthCheckTagProperty", jsii_struct_bases=[])
    class HealthCheckTagProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthchecktag.html
        Stability:
            experimental
        """
        key: str
        """``CfnHealthCheck.HealthCheckTagProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthchecktag.html#cfn-route53-healthchecktags-key
        Stability:
            experimental
        """

        value: str
        """``CfnHealthCheck.HealthCheckTagProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthchecktag.html#cfn-route53-healthchecktags-value
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnHealthCheckProps(jsii.compat.TypedDict, total=False):
    healthCheckTags: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnHealthCheck.HealthCheckTagProperty"]]]
    """``AWS::Route53::HealthCheck.HealthCheckTags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-healthcheck.html#cfn-route53-healthcheck-healthchecktags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnHealthCheckProps", jsii_struct_bases=[_CfnHealthCheckProps])
class CfnHealthCheckProps(_CfnHealthCheckProps):
    """Properties for defining a ``AWS::Route53::HealthCheck``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-healthcheck.html
    Stability:
        experimental
    """
    healthCheckConfig: typing.Union["CfnHealthCheck.HealthCheckConfigProperty", aws_cdk.cdk.Token]
    """``AWS::Route53::HealthCheck.HealthCheckConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-healthcheck.html#cfn-route53-healthcheck-healthcheckconfig
    Stability:
        experimental
    """

class CfnHostedZone(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.CfnHostedZone"):
    """A CloudFormation ``AWS::Route53::HostedZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Route53::HostedZone
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, hosted_zone_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["HostedZoneConfigProperty"]]]=None, hosted_zone_tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "HostedZoneTagProperty"]]]]]=None, query_logging_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["QueryLoggingConfigProperty"]]]=None, vpcs: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union["VPCProperty", aws_cdk.cdk.Token]]]]]=None) -> None:
        """Create a new ``AWS::Route53::HostedZone``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Route53::HostedZone.Name``.
            hostedZoneConfig: ``AWS::Route53::HostedZone.HostedZoneConfig``.
            hostedZoneTags: ``AWS::Route53::HostedZone.HostedZoneTags``.
            queryLoggingConfig: ``AWS::Route53::HostedZone.QueryLoggingConfig``.
            vpcs: ``AWS::Route53::HostedZone.VPCs``.

        Stability:
            experimental
        """
        props: CfnHostedZoneProps = {"name": name}

        if hosted_zone_config is not None:
            props["hostedZoneConfig"] = hosted_zone_config

        if hosted_zone_tags is not None:
            props["hostedZoneTags"] = hosted_zone_tags

        if query_logging_config is not None:
            props["queryLoggingConfig"] = query_logging_config

        if vpcs is not None:
            props["vpcs"] = vpcs

        jsii.create(CfnHostedZone, self, [scope, id, props])

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
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "hostedZoneId")

    @property
    @jsii.member(jsii_name="hostedZoneNameServers")
    def hosted_zone_name_servers(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            NameServers
        """
        return jsii.get(self, "hostedZoneNameServers")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnHostedZoneProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnHostedZone.HostedZoneConfigProperty", jsii_struct_bases=[])
    class HostedZoneConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-hostedzone-hostedzoneconfig.html
        Stability:
            experimental
        """
        comment: str
        """``CfnHostedZone.HostedZoneConfigProperty.Comment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-hostedzone-hostedzoneconfig.html#cfn-route53-hostedzone-hostedzoneconfig-comment
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnHostedZone.HostedZoneTagProperty", jsii_struct_bases=[])
    class HostedZoneTagProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-hostedzone-hostedzonetags.html
        Stability:
            experimental
        """
        key: str
        """``CfnHostedZone.HostedZoneTagProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-hostedzone-hostedzonetags.html#cfn-route53-hostedzonetags-key
        Stability:
            experimental
        """

        value: str
        """``CfnHostedZone.HostedZoneTagProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-hostedzone-hostedzonetags.html#cfn-route53-hostedzonetags-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnHostedZone.QueryLoggingConfigProperty", jsii_struct_bases=[])
    class QueryLoggingConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-hostedzone-queryloggingconfig.html
        Stability:
            experimental
        """
        cloudWatchLogsLogGroupArn: str
        """``CfnHostedZone.QueryLoggingConfigProperty.CloudWatchLogsLogGroupArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-hostedzone-queryloggingconfig.html#cfn-route53-hostedzone-queryloggingconfig-cloudwatchlogsloggrouparn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnHostedZone.VPCProperty", jsii_struct_bases=[])
    class VPCProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone-hostedzonevpcs.html
        Stability:
            experimental
        """
        vpcId: str
        """``CfnHostedZone.VPCProperty.VPCId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone-hostedzonevpcs.html#cfn-route53-hostedzone-hostedzonevpcs-vpcid
        Stability:
            experimental
        """

        vpcRegion: str
        """``CfnHostedZone.VPCProperty.VPCRegion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone-hostedzonevpcs.html#cfn-route53-hostedzone-hostedzonevpcs-vpcregion
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnHostedZoneProps(jsii.compat.TypedDict, total=False):
    hostedZoneConfig: typing.Union[aws_cdk.cdk.Token, "CfnHostedZone.HostedZoneConfigProperty"]
    """``AWS::Route53::HostedZone.HostedZoneConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone.html#cfn-route53-hostedzone-hostedzoneconfig
    Stability:
        experimental
    """
    hostedZoneTags: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnHostedZone.HostedZoneTagProperty"]]]
    """``AWS::Route53::HostedZone.HostedZoneTags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone.html#cfn-route53-hostedzone-hostedzonetags
    Stability:
        experimental
    """
    queryLoggingConfig: typing.Union[aws_cdk.cdk.Token, "CfnHostedZone.QueryLoggingConfigProperty"]
    """``AWS::Route53::HostedZone.QueryLoggingConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone.html#cfn-route53-hostedzone-queryloggingconfig
    Stability:
        experimental
    """
    vpcs: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnHostedZone.VPCProperty", aws_cdk.cdk.Token]]]
    """``AWS::Route53::HostedZone.VPCs``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone.html#cfn-route53-hostedzone-vpcs
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnHostedZoneProps", jsii_struct_bases=[_CfnHostedZoneProps])
class CfnHostedZoneProps(_CfnHostedZoneProps):
    """Properties for defining a ``AWS::Route53::HostedZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone.html
    Stability:
        experimental
    """
    name: str
    """``AWS::Route53::HostedZone.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone.html#cfn-route53-hostedzone-name
    Stability:
        experimental
    """

class CfnRecordSet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.CfnRecordSet"):
    """A CloudFormation ``AWS::Route53::RecordSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Route53::RecordSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, type: str, alias_target: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["AliasTargetProperty"]]]=None, comment: typing.Optional[str]=None, failover: typing.Optional[str]=None, geo_location: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["GeoLocationProperty"]]]=None, health_check_id: typing.Optional[str]=None, hosted_zone_id: typing.Optional[str]=None, hosted_zone_name: typing.Optional[str]=None, multi_value_answer: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, region: typing.Optional[str]=None, resource_records: typing.Optional[typing.List[str]]=None, set_identifier: typing.Optional[str]=None, ttl: typing.Optional[str]=None, weight: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::Route53::RecordSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Route53::RecordSet.Name``.
            type: ``AWS::Route53::RecordSet.Type``.
            aliasTarget: ``AWS::Route53::RecordSet.AliasTarget``.
            comment: ``AWS::Route53::RecordSet.Comment``.
            failover: ``AWS::Route53::RecordSet.Failover``.
            geoLocation: ``AWS::Route53::RecordSet.GeoLocation``.
            healthCheckId: ``AWS::Route53::RecordSet.HealthCheckId``.
            hostedZoneId: ``AWS::Route53::RecordSet.HostedZoneId``.
            hostedZoneName: ``AWS::Route53::RecordSet.HostedZoneName``.
            multiValueAnswer: ``AWS::Route53::RecordSet.MultiValueAnswer``.
            region: ``AWS::Route53::RecordSet.Region``.
            resourceRecords: ``AWS::Route53::RecordSet.ResourceRecords``.
            setIdentifier: ``AWS::Route53::RecordSet.SetIdentifier``.
            ttl: ``AWS::Route53::RecordSet.TTL``.
            weight: ``AWS::Route53::RecordSet.Weight``.

        Stability:
            experimental
        """
        props: CfnRecordSetProps = {"name": name, "type": type}

        if alias_target is not None:
            props["aliasTarget"] = alias_target

        if comment is not None:
            props["comment"] = comment

        if failover is not None:
            props["failover"] = failover

        if geo_location is not None:
            props["geoLocation"] = geo_location

        if health_check_id is not None:
            props["healthCheckId"] = health_check_id

        if hosted_zone_id is not None:
            props["hostedZoneId"] = hosted_zone_id

        if hosted_zone_name is not None:
            props["hostedZoneName"] = hosted_zone_name

        if multi_value_answer is not None:
            props["multiValueAnswer"] = multi_value_answer

        if region is not None:
            props["region"] = region

        if resource_records is not None:
            props["resourceRecords"] = resource_records

        if set_identifier is not None:
            props["setIdentifier"] = set_identifier

        if ttl is not None:
            props["ttl"] = ttl

        if weight is not None:
            props["weight"] = weight

        jsii.create(CfnRecordSet, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnRecordSetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="recordSetDomainName")
    def record_set_domain_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "recordSetDomainName")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _AliasTargetProperty(jsii.compat.TypedDict, total=False):
        evaluateTargetHealth: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnRecordSet.AliasTargetProperty.EvaluateTargetHealth``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-aliastarget.html#cfn-route53-aliastarget-evaluatetargethealth
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnRecordSet.AliasTargetProperty", jsii_struct_bases=[_AliasTargetProperty])
    class AliasTargetProperty(_AliasTargetProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-aliastarget.html
        Stability:
            experimental
        """
        dnsName: str
        """``CfnRecordSet.AliasTargetProperty.DNSName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-aliastarget.html#cfn-route53-aliastarget-dnshostname
        Stability:
            experimental
        """

        hostedZoneId: str
        """``CfnRecordSet.AliasTargetProperty.HostedZoneId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-aliastarget.html#cfn-route53-aliastarget-hostedzoneid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnRecordSet.GeoLocationProperty", jsii_struct_bases=[])
    class GeoLocationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset-geolocation.html
        Stability:
            experimental
        """
        continentCode: str
        """``CfnRecordSet.GeoLocationProperty.ContinentCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset-geolocation.html#cfn-route53-recordset-geolocation-continentcode
        Stability:
            experimental
        """

        countryCode: str
        """``CfnRecordSet.GeoLocationProperty.CountryCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset-geolocation.html#cfn-route53-recordset-geolocation-countrycode
        Stability:
            experimental
        """

        subdivisionCode: str
        """``CfnRecordSet.GeoLocationProperty.SubdivisionCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset-geolocation.html#cfn-route53-recordset-geolocation-subdivisioncode
        Stability:
            experimental
        """


class CfnRecordSetGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.CfnRecordSetGroup"):
    """A CloudFormation ``AWS::Route53::RecordSetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-recordsetgroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Route53::RecordSetGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, comment: typing.Optional[str]=None, hosted_zone_id: typing.Optional[str]=None, hosted_zone_name: typing.Optional[str]=None, record_sets: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "RecordSetProperty"]]]]]=None) -> None:
        """Create a new ``AWS::Route53::RecordSetGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            comment: ``AWS::Route53::RecordSetGroup.Comment``.
            hostedZoneId: ``AWS::Route53::RecordSetGroup.HostedZoneId``.
            hostedZoneName: ``AWS::Route53::RecordSetGroup.HostedZoneName``.
            recordSets: ``AWS::Route53::RecordSetGroup.RecordSets``.

        Stability:
            experimental
        """
        props: CfnRecordSetGroupProps = {}

        if comment is not None:
            props["comment"] = comment

        if hosted_zone_id is not None:
            props["hostedZoneId"] = hosted_zone_id

        if hosted_zone_name is not None:
            props["hostedZoneName"] = hosted_zone_name

        if record_sets is not None:
            props["recordSets"] = record_sets

        jsii.create(CfnRecordSetGroup, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnRecordSetGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="recordSetGroupName")
    def record_set_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "recordSetGroupName")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _AliasTargetProperty(jsii.compat.TypedDict, total=False):
        evaluateTargetHealth: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnRecordSetGroup.AliasTargetProperty.EvaluateTargetHealth``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-aliastarget.html#cfn-route53-aliastarget-evaluatetargethealth
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnRecordSetGroup.AliasTargetProperty", jsii_struct_bases=[_AliasTargetProperty])
    class AliasTargetProperty(_AliasTargetProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-aliastarget.html
        Stability:
            experimental
        """
        dnsName: str
        """``CfnRecordSetGroup.AliasTargetProperty.DNSName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-aliastarget.html#cfn-route53-aliastarget-dnshostname
        Stability:
            experimental
        """

        hostedZoneId: str
        """``CfnRecordSetGroup.AliasTargetProperty.HostedZoneId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-aliastarget.html#cfn-route53-aliastarget-hostedzoneid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnRecordSetGroup.GeoLocationProperty", jsii_struct_bases=[])
    class GeoLocationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset-geolocation.html
        Stability:
            experimental
        """
        continentCode: str
        """``CfnRecordSetGroup.GeoLocationProperty.ContinentCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset-geolocation.html#cfn-route53-recordsetgroup-geolocation-continentcode
        Stability:
            experimental
        """

        countryCode: str
        """``CfnRecordSetGroup.GeoLocationProperty.CountryCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset-geolocation.html#cfn-route53-recordset-geolocation-countrycode
        Stability:
            experimental
        """

        subdivisionCode: str
        """``CfnRecordSetGroup.GeoLocationProperty.SubdivisionCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset-geolocation.html#cfn-route53-recordset-geolocation-subdivisioncode
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _RecordSetProperty(jsii.compat.TypedDict, total=False):
        aliasTarget: typing.Union[aws_cdk.cdk.Token, "CfnRecordSetGroup.AliasTargetProperty"]
        """``CfnRecordSetGroup.RecordSetProperty.AliasTarget``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-aliastarget
        Stability:
            experimental
        """
        comment: str
        """``CfnRecordSetGroup.RecordSetProperty.Comment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-comment
        Stability:
            experimental
        """
        failover: str
        """``CfnRecordSetGroup.RecordSetProperty.Failover``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-failover
        Stability:
            experimental
        """
        geoLocation: typing.Union[aws_cdk.cdk.Token, "CfnRecordSetGroup.GeoLocationProperty"]
        """``CfnRecordSetGroup.RecordSetProperty.GeoLocation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-geolocation
        Stability:
            experimental
        """
        healthCheckId: str
        """``CfnRecordSetGroup.RecordSetProperty.HealthCheckId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-healthcheckid
        Stability:
            experimental
        """
        hostedZoneId: str
        """``CfnRecordSetGroup.RecordSetProperty.HostedZoneId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-hostedzoneid
        Stability:
            experimental
        """
        hostedZoneName: str
        """``CfnRecordSetGroup.RecordSetProperty.HostedZoneName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-hostedzonename
        Stability:
            experimental
        """
        multiValueAnswer: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnRecordSetGroup.RecordSetProperty.MultiValueAnswer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-multivalueanswer
        Stability:
            experimental
        """
        region: str
        """``CfnRecordSetGroup.RecordSetProperty.Region``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-region
        Stability:
            experimental
        """
        resourceRecords: typing.List[str]
        """``CfnRecordSetGroup.RecordSetProperty.ResourceRecords``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-resourcerecords
        Stability:
            experimental
        """
        setIdentifier: str
        """``CfnRecordSetGroup.RecordSetProperty.SetIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-setidentifier
        Stability:
            experimental
        """
        ttl: str
        """``CfnRecordSetGroup.RecordSetProperty.TTL``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-ttl
        Stability:
            experimental
        """
        weight: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnRecordSetGroup.RecordSetProperty.Weight``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-weight
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnRecordSetGroup.RecordSetProperty", jsii_struct_bases=[_RecordSetProperty])
    class RecordSetProperty(_RecordSetProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html
        Stability:
            experimental
        """
        name: str
        """``CfnRecordSetGroup.RecordSetProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-name
        Stability:
            experimental
        """

        type: str
        """``CfnRecordSetGroup.RecordSetProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-type
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnRecordSetGroupProps", jsii_struct_bases=[])
class CfnRecordSetGroupProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::Route53::RecordSetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-recordsetgroup.html
    Stability:
        experimental
    """
    comment: str
    """``AWS::Route53::RecordSetGroup.Comment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-recordsetgroup.html#cfn-route53-recordsetgroup-comment
    Stability:
        experimental
    """

    hostedZoneId: str
    """``AWS::Route53::RecordSetGroup.HostedZoneId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-recordsetgroup.html#cfn-route53-recordsetgroup-hostedzoneid
    Stability:
        experimental
    """

    hostedZoneName: str
    """``AWS::Route53::RecordSetGroup.HostedZoneName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-recordsetgroup.html#cfn-route53-recordsetgroup-hostedzonename
    Stability:
        experimental
    """

    recordSets: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnRecordSetGroup.RecordSetProperty"]]]
    """``AWS::Route53::RecordSetGroup.RecordSets``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-recordsetgroup.html#cfn-route53-recordsetgroup-recordsets
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRecordSetProps(jsii.compat.TypedDict, total=False):
    aliasTarget: typing.Union[aws_cdk.cdk.Token, "CfnRecordSet.AliasTargetProperty"]
    """``AWS::Route53::RecordSet.AliasTarget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-aliastarget
    Stability:
        experimental
    """
    comment: str
    """``AWS::Route53::RecordSet.Comment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-comment
    Stability:
        experimental
    """
    failover: str
    """``AWS::Route53::RecordSet.Failover``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-failover
    Stability:
        experimental
    """
    geoLocation: typing.Union[aws_cdk.cdk.Token, "CfnRecordSet.GeoLocationProperty"]
    """``AWS::Route53::RecordSet.GeoLocation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-geolocation
    Stability:
        experimental
    """
    healthCheckId: str
    """``AWS::Route53::RecordSet.HealthCheckId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-healthcheckid
    Stability:
        experimental
    """
    hostedZoneId: str
    """``AWS::Route53::RecordSet.HostedZoneId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-hostedzoneid
    Stability:
        experimental
    """
    hostedZoneName: str
    """``AWS::Route53::RecordSet.HostedZoneName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-hostedzonename
    Stability:
        experimental
    """
    multiValueAnswer: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::Route53::RecordSet.MultiValueAnswer``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-multivalueanswer
    Stability:
        experimental
    """
    region: str
    """``AWS::Route53::RecordSet.Region``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-region
    Stability:
        experimental
    """
    resourceRecords: typing.List[str]
    """``AWS::Route53::RecordSet.ResourceRecords``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-resourcerecords
    Stability:
        experimental
    """
    setIdentifier: str
    """``AWS::Route53::RecordSet.SetIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-setidentifier
    Stability:
        experimental
    """
    ttl: str
    """``AWS::Route53::RecordSet.TTL``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-ttl
    Stability:
        experimental
    """
    weight: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Route53::RecordSet.Weight``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-weight
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.CfnRecordSetProps", jsii_struct_bases=[_CfnRecordSetProps])
class CfnRecordSetProps(_CfnRecordSetProps):
    """Properties for defining a ``AWS::Route53::RecordSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html
    Stability:
        experimental
    """
    name: str
    """``AWS::Route53::RecordSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-name
    Stability:
        experimental
    """

    type: str
    """``AWS::Route53::RecordSet.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html#cfn-route53-recordset-type
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CommonHostedZoneProps(jsii.compat.TypedDict, total=False):
    comment: str
    """Any comments that you want to include about the hosted zone.

    Default:
        none

    Stability:
        experimental
    """
    queryLogsLogGroupArn: str
    """The Amazon Resource Name (ARN) for the log group that you want Amazon Route 53 to send query logs to.

    Default:
        disabled

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.CommonHostedZoneProps", jsii_struct_bases=[_CommonHostedZoneProps])
class CommonHostedZoneProps(_CommonHostedZoneProps):
    """
    Stability:
        experimental
    """
    zoneName: str
    """The name of the domain.

    For resource record types that include a domain
    name, specify a fully qualified domain name.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.HostedZoneAttributes", jsii_struct_bases=[])
class HostedZoneAttributes(jsii.compat.TypedDict):
    """Reference to a hosted zone.

    Stability:
        experimental
    """
    hostedZoneId: str
    """Identifier of the hosted zone.

    Stability:
        experimental
    """

    zoneName: str
    """Name of the hosted zone.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.HostedZoneProps", jsii_struct_bases=[CommonHostedZoneProps])
class HostedZoneProps(CommonHostedZoneProps, jsii.compat.TypedDict, total=False):
    """Properties of a new hosted zone.

    Stability:
        experimental
    """
    vpcs: typing.List[aws_cdk.aws_ec2.IVpc]
    """A VPC that you want to associate with this hosted zone.

    When you specify
    this property, a private hosted zone will be created.

    You can associate additional VPCs to this private zone using ``addVpc(vpc)``.

    Default:
        public (no VPCs associated)

    Stability:
        experimental
    """

class HostedZoneProvider(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.HostedZoneProvider"):
    """Context provider that will lookup the Hosted Zone ID for the given arguments.

    Stability:
        experimental
    """
    def __init__(self, context: aws_cdk.cdk.Construct, *, domain_name: str, private_zone: typing.Optional[bool]=None, vpc_id: typing.Optional[str]=None) -> None:
        """
        Arguments:
            context: -
            props: -
            domainName: The zone domain e.g. example.com.
            privateZone: Is this a private zone.
            vpcId: If this is a private zone which VPC is assocaitated.

        Stability:
            experimental
        """
        props: HostedZoneProviderProps = {"domainName": domain_name}

        if private_zone is not None:
            props["privateZone"] = private_zone

        if vpc_id is not None:
            props["vpcId"] = vpc_id

        jsii.create(HostedZoneProvider, self, [context, props])

    @jsii.member(jsii_name="findAndImport")
    def find_and_import(self, scope: aws_cdk.cdk.Construct, id: str) -> "IHostedZone":
        """This method calls ``findHostedZone`` and returns the imported hosted zone.

        Arguments:
            scope: -
            id: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "findAndImport", [scope, id])

    @jsii.member(jsii_name="findHostedZone")
    def find_hosted_zone(self) -> "HostedZoneAttributes":
        """Return the hosted zone meeting the filter.

        Stability:
            experimental
        """
        return jsii.invoke(self, "findHostedZone", [])


@jsii.data_type_optionals(jsii_struct_bases=[])
class _HostedZoneProviderProps(jsii.compat.TypedDict, total=False):
    privateZone: bool
    """Is this a private zone.

    Stability:
        experimental
    """
    vpcId: str
    """If this is a private zone which VPC is assocaitated.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.HostedZoneProviderProps", jsii_struct_bases=[_HostedZoneProviderProps])
class HostedZoneProviderProps(_HostedZoneProviderProps):
    """Zone properties for looking up the Hosted Zone.

    Stability:
        experimental
    """
    domainName: str
    """The zone domain e.g. example.com.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-route53.IAliasRecordTarget")
class IAliasRecordTarget(jsii.compat.Protocol):
    """Classes that are valid alias record targets, like CloudFront distributions and load balancers, should implement this interface.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IAliasRecordTargetProxy

    @jsii.member(jsii_name="bind")
    def bind(self, record: "IRecordSet") -> "AliasRecordTargetConfig":
        """Return hosted zone ID and DNS name, usable for Route53 alias targets.

        Arguments:
            record: -

        Stability:
            experimental
        """
        ...


class _IAliasRecordTargetProxy():
    """Classes that are valid alias record targets, like CloudFront distributions and load balancers, should implement this interface.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-route53.IAliasRecordTarget"
    @jsii.member(jsii_name="bind")
    def bind(self, record: "IRecordSet") -> "AliasRecordTargetConfig":
        """Return hosted zone ID and DNS name, usable for Route53 alias targets.

        Arguments:
            record: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [record])


@jsii.interface(jsii_type="@aws-cdk/aws-route53.IHostedZone")
class IHostedZone(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """Imported or created hosted zone.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IHostedZoneProxy

    @property
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> str:
        """ID of this hosted zone, such as "Z23ABC4XYZL05B".

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> str:
        """FQDN of this hosted zone.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="hostedZoneNameServers")
    def hosted_zone_name_servers(self) -> typing.Optional[typing.List[str]]:
        """Returns the set of name servers for the specific hosted zone. For example: ns1.example.com.

        This attribute will be undefined for private hosted zones or hosted zones imported from another stack.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IHostedZoneProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """Imported or created hosted zone.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-route53.IHostedZone"
    @property
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> str:
        """ID of this hosted zone, such as "Z23ABC4XYZL05B".

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "hostedZoneId")

    @property
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> str:
        """FQDN of this hosted zone.

        Stability:
            experimental
        """
        return jsii.get(self, "zoneName")

    @property
    @jsii.member(jsii_name="hostedZoneNameServers")
    def hosted_zone_name_servers(self) -> typing.Optional[typing.List[str]]:
        """Returns the set of name servers for the specific hosted zone. For example: ns1.example.com.

        This attribute will be undefined for private hosted zones or hosted zones imported from another stack.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "hostedZoneNameServers")


@jsii.implements(IHostedZone)
class HostedZone(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.HostedZone"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpcs: typing.Optional[typing.List[aws_cdk.aws_ec2.IVpc]]=None, zone_name: str, comment: typing.Optional[str]=None, query_logs_log_group_arn: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            vpcs: A VPC that you want to associate with this hosted zone. When you specify this property, a private hosted zone will be created. You can associate additional VPCs to this private zone using ``addVpc(vpc)``. Default: public (no VPCs associated)
            zoneName: The name of the domain. For resource record types that include a domain name, specify a fully qualified domain name.
            comment: Any comments that you want to include about the hosted zone. Default: none
            queryLogsLogGroupArn: The Amazon Resource Name (ARN) for the log group that you want Amazon Route 53 to send query logs to. Default: disabled

        Stability:
            experimental
        """
        props: HostedZoneProps = {"zoneName": zone_name}

        if vpcs is not None:
            props["vpcs"] = vpcs

        if comment is not None:
            props["comment"] = comment

        if query_logs_log_group_arn is not None:
            props["queryLogsLogGroupArn"] = query_logs_log_group_arn

        jsii.create(HostedZone, self, [scope, id, props])

    @jsii.member(jsii_name="fromHostedZoneAttributes")
    @classmethod
    def from_hosted_zone_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, hosted_zone_id: str, zone_name: str) -> "IHostedZone":
        """Imports a hosted zone from another stack.

        Arguments:
            scope: -
            id: -
            attrs: -
            hostedZoneId: Identifier of the hosted zone.
            zoneName: Name of the hosted zone.

        Stability:
            experimental
        """
        attrs: HostedZoneAttributes = {"hostedZoneId": hosted_zone_id, "zoneName": zone_name}

        return jsii.sinvoke(cls, "fromHostedZoneAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="fromHostedZoneId")
    @classmethod
    def from_hosted_zone_id(cls, scope: aws_cdk.cdk.Construct, id: str, hosted_zone_id: str) -> "IHostedZone":
        """
        Arguments:
            scope: -
            id: -
            hostedZoneId: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromHostedZoneId", [scope, id, hosted_zone_id])

    @jsii.member(jsii_name="addVpc")
    def add_vpc(self, vpc: aws_cdk.aws_ec2.IVpc) -> None:
        """Add another VPC to this private hosted zone.

        Arguments:
            vpc: the other VPC to add.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addVpc", [vpc])

    @property
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> str:
        """ID of this hosted zone, such as "Z23ABC4XYZL05B".

        Stability:
            experimental
        """
        return jsii.get(self, "hostedZoneId")

    @property
    @jsii.member(jsii_name="vpcs")
    def _vpcs(self) -> typing.List["CfnHostedZone.VPCProperty"]:
        """VPCs to which this hosted zone will be added.

        Stability:
            experimental
        """
        return jsii.get(self, "vpcs")

    @property
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> str:
        """FQDN of this hosted zone.

        Stability:
            experimental
        """
        return jsii.get(self, "zoneName")

    @property
    @jsii.member(jsii_name="hostedZoneNameServers")
    def hosted_zone_name_servers(self) -> typing.Optional[typing.List[str]]:
        """Returns the set of name servers for the specific hosted zone. For example: ns1.example.com.

        This attribute will be undefined for private hosted zones or hosted zones imported from another stack.

        Stability:
            experimental
        """
        return jsii.get(self, "hostedZoneNameServers")


@jsii.interface(jsii_type="@aws-cdk/aws-route53.IPrivateHostedZone")
class IPrivateHostedZone(IHostedZone, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IPrivateHostedZoneProxy

    pass

class _IPrivateHostedZoneProxy(jsii.proxy_for(IHostedZone)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-route53.IPrivateHostedZone"
    pass

@jsii.interface(jsii_type="@aws-cdk/aws-route53.IPublicHostedZone")
class IPublicHostedZone(IHostedZone, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IPublicHostedZoneProxy

    pass

class _IPublicHostedZoneProxy(jsii.proxy_for(IHostedZone)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-route53.IPublicHostedZone"
    pass

@jsii.interface(jsii_type="@aws-cdk/aws-route53.IRecordSet")
class IRecordSet(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """A record set.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IRecordSetProxy

    @property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> str:
        """The domain name of the record.

        Stability:
            experimental
        """
        ...


class _IRecordSetProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """A record set.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-route53.IRecordSet"
    @property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> str:
        """The domain name of the record.

        Stability:
            experimental
        """
        return jsii.get(self, "domainName")


@jsii.data_type(jsii_type="@aws-cdk/aws-route53.MxRecordValue", jsii_struct_bases=[])
class MxRecordValue(jsii.compat.TypedDict):
    """Properties for a MX record value.

    Stability:
        experimental
    """
    hostName: str
    """The mail server host name.

    Stability:
        experimental
    """

    priority: jsii.Number
    """The priority.

    Stability:
        experimental
    """

@jsii.implements(IPrivateHostedZone)
class PrivateHostedZone(HostedZone, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.PrivateHostedZone"):
    """Create a Route53 private hosted zone for use in one or more VPCs.

    Note that ``enableDnsHostnames`` and ``enableDnsSupport`` must have been enabled
    for the VPC you're configuring for private hosted zones.

    Stability:
        experimental
    resource:
        AWS::Route53::HostedZone
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc: aws_cdk.aws_ec2.IVpc, zone_name: str, comment: typing.Optional[str]=None, query_logs_log_group_arn: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            vpc: A VPC that you want to associate with this hosted zone. Private hosted zones must be associated with at least one VPC. You can associated additional VPCs using ``addVpc(vpc)``.
            zoneName: The name of the domain. For resource record types that include a domain name, specify a fully qualified domain name.
            comment: Any comments that you want to include about the hosted zone. Default: none
            queryLogsLogGroupArn: The Amazon Resource Name (ARN) for the log group that you want Amazon Route 53 to send query logs to. Default: disabled

        Stability:
            experimental
        """
        props: PrivateHostedZoneProps = {"vpc": vpc, "zoneName": zone_name}

        if comment is not None:
            props["comment"] = comment

        if query_logs_log_group_arn is not None:
            props["queryLogsLogGroupArn"] = query_logs_log_group_arn

        jsii.create(PrivateHostedZone, self, [scope, id, props])

    @jsii.member(jsii_name="fromPrivateHostedZoneId")
    @classmethod
    def from_private_hosted_zone_id(cls, scope: aws_cdk.cdk.Construct, id: str, private_hosted_zone_id: str) -> "IPrivateHostedZone":
        """
        Arguments:
            scope: -
            id: -
            privateHostedZoneId: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromPrivateHostedZoneId", [scope, id, private_hosted_zone_id])


@jsii.data_type(jsii_type="@aws-cdk/aws-route53.PrivateHostedZoneProps", jsii_struct_bases=[CommonHostedZoneProps])
class PrivateHostedZoneProps(CommonHostedZoneProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    vpc: aws_cdk.aws_ec2.IVpc
    """A VPC that you want to associate with this hosted zone.

    Private hosted zones must be associated with at least one VPC. You can
    associated additional VPCs using ``addVpc(vpc)``.

    Stability:
        experimental
    """

@jsii.implements(IPublicHostedZone)
class PublicHostedZone(HostedZone, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.PublicHostedZone"):
    """Create a Route53 public hosted zone.

    Stability:
        experimental
    resource:
        AWS::Route53::HostedZone
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, caa_amazon: typing.Optional[bool]=None, zone_name: str, comment: typing.Optional[str]=None, query_logs_log_group_arn: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            caaAmazon: Whether to create a CAA record to restrict certificate authorities allowed to issue certificates for this domain to Amazon only. Default: false
            zoneName: The name of the domain. For resource record types that include a domain name, specify a fully qualified domain name.
            comment: Any comments that you want to include about the hosted zone. Default: none
            queryLogsLogGroupArn: The Amazon Resource Name (ARN) for the log group that you want Amazon Route 53 to send query logs to. Default: disabled

        Stability:
            experimental
        """
        props: PublicHostedZoneProps = {"zoneName": zone_name}

        if caa_amazon is not None:
            props["caaAmazon"] = caa_amazon

        if comment is not None:
            props["comment"] = comment

        if query_logs_log_group_arn is not None:
            props["queryLogsLogGroupArn"] = query_logs_log_group_arn

        jsii.create(PublicHostedZone, self, [scope, id, props])

    @jsii.member(jsii_name="fromPublicHostedZoneId")
    @classmethod
    def from_public_hosted_zone_id(cls, scope: aws_cdk.cdk.Construct, id: str, public_hosted_zone_id: str) -> "IPublicHostedZone":
        """
        Arguments:
            scope: -
            id: -
            publicHostedZoneId: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromPublicHostedZoneId", [scope, id, public_hosted_zone_id])

    @jsii.member(jsii_name="addDelegation")
    def add_delegation(self, delegate: "IPublicHostedZone", *, comment: typing.Optional[str]=None, ttl: typing.Optional[jsii.Number]=None) -> None:
        """Adds a delegation from this zone to a designated zone.

        Arguments:
            delegate: the zone being delegated to.
            opts: options for creating the DNS record, if any.
            comment: A comment to add on the DNS record created to incorporate the delegation. Default: none
            ttl: The TTL (Time To Live) of the DNS delegation record in DNS caches. Default: 172800

        Stability:
            experimental
        """
        opts: ZoneDelegationOptions = {}

        if comment is not None:
            opts["comment"] = comment

        if ttl is not None:
            opts["ttl"] = ttl

        return jsii.invoke(self, "addDelegation", [delegate, opts])

    @jsii.member(jsii_name="addVpc")
    def add_vpc(self, _vpc: aws_cdk.aws_ec2.IVpc) -> None:
        """Add another VPC to this private hosted zone.

        Arguments:
            _vpc: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addVpc", [_vpc])


@jsii.data_type(jsii_type="@aws-cdk/aws-route53.PublicHostedZoneProps", jsii_struct_bases=[CommonHostedZoneProps])
class PublicHostedZoneProps(CommonHostedZoneProps, jsii.compat.TypedDict, total=False):
    """Construction properties for a PublicHostedZone.

    Stability:
        experimental
    """
    caaAmazon: bool
    """Whether to create a CAA record to restrict certificate authorities allowed to issue certificates for this domain to Amazon only.

    Default:
        false

    Stability:
        experimental
    """

@jsii.implements(IRecordSet)
class RecordSet(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.RecordSet"):
    """A record set.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, record_type: "RecordType", target: "RecordTarget", zone: "IHostedZone", comment: typing.Optional[str]=None, record_name: typing.Optional[str]=None, ttl: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            recordType: The record type.
            target: The target for this record, either ``RecordTarget.fromValues()`` or ``RecordTarget.fromAlias()``.
            zone: The hosted zone in which to define the new record.
            comment: A comment to add on the record. Default: no comment
            recordName: The domain name for this record. Default: zone root
            ttl: The resource record cache time to live (TTL) in seconds. Default: 1800 seconds

        Stability:
            experimental
        """
        props: RecordSetProps = {"recordType": record_type, "target": target, "zone": zone}

        if comment is not None:
            props["comment"] = comment

        if record_name is not None:
            props["recordName"] = record_name

        if ttl is not None:
            props["ttl"] = ttl

        jsii.create(RecordSet, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> str:
        """The domain name of the record.

        Stability:
            experimental
        """
        return jsii.get(self, "domainName")


class ARecord(RecordSet, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.ARecord"):
    """A DNS A record.

    Stability:
        experimental
    resource:
        AWS::Route53::RecordSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, target: "AddressRecordTarget", zone: "IHostedZone", comment: typing.Optional[str]=None, record_name: typing.Optional[str]=None, ttl: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            target: The target.
            zone: The hosted zone in which to define the new record.
            comment: A comment to add on the record. Default: no comment
            recordName: The domain name for this record. Default: zone root
            ttl: The resource record cache time to live (TTL) in seconds. Default: 1800 seconds

        Stability:
            experimental
        """
        props: ARecordProps = {"target": target, "zone": zone}

        if comment is not None:
            props["comment"] = comment

        if record_name is not None:
            props["recordName"] = record_name

        if ttl is not None:
            props["ttl"] = ttl

        jsii.create(ARecord, self, [scope, id, props])


class AaaaRecord(RecordSet, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.AaaaRecord"):
    """A DNS AAAA record.

    Stability:
        experimental
    resource:
        AWS::Route53::RecordSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, target: "AddressRecordTarget", zone: "IHostedZone", comment: typing.Optional[str]=None, record_name: typing.Optional[str]=None, ttl: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            target: The target.
            zone: The hosted zone in which to define the new record.
            comment: A comment to add on the record. Default: no comment
            recordName: The domain name for this record. Default: zone root
            ttl: The resource record cache time to live (TTL) in seconds. Default: 1800 seconds

        Stability:
            experimental
        """
        props: AaaaRecordProps = {"target": target, "zone": zone}

        if comment is not None:
            props["comment"] = comment

        if record_name is not None:
            props["recordName"] = record_name

        if ttl is not None:
            props["ttl"] = ttl

        jsii.create(AaaaRecord, self, [scope, id, props])


class CaaRecord(RecordSet, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.CaaRecord"):
    """A DNS CAA record.

    Stability:
        experimental
    resource:
        AWS::Route53::RecordSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, values: typing.List["CaaRecordValue"], zone: "IHostedZone", comment: typing.Optional[str]=None, record_name: typing.Optional[str]=None, ttl: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            values: The values.
            zone: The hosted zone in which to define the new record.
            comment: A comment to add on the record. Default: no comment
            recordName: The domain name for this record. Default: zone root
            ttl: The resource record cache time to live (TTL) in seconds. Default: 1800 seconds

        Stability:
            experimental
        """
        props: CaaRecordProps = {"values": values, "zone": zone}

        if comment is not None:
            props["comment"] = comment

        if record_name is not None:
            props["recordName"] = record_name

        if ttl is not None:
            props["ttl"] = ttl

        jsii.create(CaaRecord, self, [scope, id, props])


class CaaAmazonRecord(CaaRecord, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.CaaAmazonRecord"):
    """A DNS Amazon CAA record.

    A CAA record to restrict certificate authorities allowed
    to issue certificates for a domain to Amazon only.

    Stability:
        experimental
    resource:
        AWS::Route53::RecordSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, zone: "IHostedZone", comment: typing.Optional[str]=None, record_name: typing.Optional[str]=None, ttl: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            zone: The hosted zone in which to define the new record.
            comment: A comment to add on the record. Default: no comment
            recordName: The domain name for this record. Default: zone root
            ttl: The resource record cache time to live (TTL) in seconds. Default: 1800 seconds

        Stability:
            experimental
        """
        props: CaaAmazonRecordProps = {"zone": zone}

        if comment is not None:
            props["comment"] = comment

        if record_name is not None:
            props["recordName"] = record_name

        if ttl is not None:
            props["ttl"] = ttl

        jsii.create(CaaAmazonRecord, self, [scope, id, props])


class CnameRecord(RecordSet, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.CnameRecord"):
    """A DNS CNAME record.

    Stability:
        experimental
    resource:
        AWS::Route53::RecordSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, domain_name: str, zone: "IHostedZone", comment: typing.Optional[str]=None, record_name: typing.Optional[str]=None, ttl: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            domainName: The domain name.
            zone: The hosted zone in which to define the new record.
            comment: A comment to add on the record. Default: no comment
            recordName: The domain name for this record. Default: zone root
            ttl: The resource record cache time to live (TTL) in seconds. Default: 1800 seconds

        Stability:
            experimental
        """
        props: CnameRecordProps = {"domainName": domain_name, "zone": zone}

        if comment is not None:
            props["comment"] = comment

        if record_name is not None:
            props["recordName"] = record_name

        if ttl is not None:
            props["ttl"] = ttl

        jsii.create(CnameRecord, self, [scope, id, props])


class MxRecord(RecordSet, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.MxRecord"):
    """A DNS MX record.

    Stability:
        experimental
    resource:
        AWS::Route53::RecordSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, values: typing.List["MxRecordValue"], zone: "IHostedZone", comment: typing.Optional[str]=None, record_name: typing.Optional[str]=None, ttl: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            values: The values.
            zone: The hosted zone in which to define the new record.
            comment: A comment to add on the record. Default: no comment
            recordName: The domain name for this record. Default: zone root
            ttl: The resource record cache time to live (TTL) in seconds. Default: 1800 seconds

        Stability:
            experimental
        """
        props: MxRecordProps = {"values": values, "zone": zone}

        if comment is not None:
            props["comment"] = comment

        if record_name is not None:
            props["recordName"] = record_name

        if ttl is not None:
            props["ttl"] = ttl

        jsii.create(MxRecord, self, [scope, id, props])


@jsii.data_type_optionals(jsii_struct_bases=[])
class _RecordSetOptions(jsii.compat.TypedDict, total=False):
    comment: str
    """A comment to add on the record.

    Default:
        no comment

    Stability:
        experimental
    """
    recordName: str
    """The domain name for this record.

    Default:
        zone root

    Stability:
        experimental
    """
    ttl: jsii.Number
    """The resource record cache time to live (TTL) in seconds.

    Default:
        1800 seconds

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.RecordSetOptions", jsii_struct_bases=[_RecordSetOptions])
class RecordSetOptions(_RecordSetOptions):
    """Options for a RecordSet.

    Stability:
        experimental
    """
    zone: "IHostedZone"
    """The hosted zone in which to define the new record.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.ARecordProps", jsii_struct_bases=[RecordSetOptions])
class ARecordProps(RecordSetOptions, jsii.compat.TypedDict):
    """Construction properties for a ARecord.

    Stability:
        experimental
    """
    target: "AddressRecordTarget"
    """The target.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.AaaaRecordProps", jsii_struct_bases=[RecordSetOptions])
class AaaaRecordProps(RecordSetOptions, jsii.compat.TypedDict):
    """Construction properties for a AaaaRecord.

    Stability:
        experimental
    """
    target: "AddressRecordTarget"
    """The target.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.CaaAmazonRecordProps", jsii_struct_bases=[RecordSetOptions])
class CaaAmazonRecordProps(RecordSetOptions, jsii.compat.TypedDict):
    """Construction properties for a CaaAmazonRecord.

    Stability:
        experimental
    """
    pass

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.CaaRecordProps", jsii_struct_bases=[RecordSetOptions])
class CaaRecordProps(RecordSetOptions, jsii.compat.TypedDict):
    """Construction properties for a CaaRecord.

    Stability:
        experimental
    """
    values: typing.List["CaaRecordValue"]
    """The values.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.CnameRecordProps", jsii_struct_bases=[RecordSetOptions])
class CnameRecordProps(RecordSetOptions, jsii.compat.TypedDict):
    """Construction properties for a CnameRecord.

    Stability:
        experimental
    """
    domainName: str
    """The domain name.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.MxRecordProps", jsii_struct_bases=[RecordSetOptions])
class MxRecordProps(RecordSetOptions, jsii.compat.TypedDict):
    """Construction properties for a MxRecord.

    Stability:
        experimental
    """
    values: typing.List["MxRecordValue"]
    """The values.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.RecordSetProps", jsii_struct_bases=[RecordSetOptions])
class RecordSetProps(RecordSetOptions, jsii.compat.TypedDict):
    """Construction properties for a RecordSet.

    Stability:
        experimental
    """
    recordType: "RecordType"
    """The record type.

    Stability:
        experimental
    """

    target: "RecordTarget"
    """The target for this record, either ``RecordTarget.fromValues()`` or ``RecordTarget.fromAlias()``.

    Stability:
        experimental
    """

class RecordTarget(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.RecordTarget"):
    """Type union for a record that accepts multiple types of target.

    Stability:
        experimental
    """
    def __init__(self, values: typing.Optional[typing.List[str]]=None, alias_target: typing.Optional["IAliasRecordTarget"]=None) -> None:
        """
        Arguments:
            values: -
            aliasTarget: -

        Stability:
            experimental
        """
        jsii.create(RecordTarget, self, [values, alias_target])

    @jsii.member(jsii_name="fromAlias")
    @classmethod
    def from_alias(cls, alias_target: "IAliasRecordTarget") -> "RecordTarget":
        """Use an alias as target.

        Arguments:
            aliasTarget: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromAlias", [alias_target])

    @jsii.member(jsii_name="fromValues")
    @classmethod
    def from_values(cls, *values: str) -> "RecordTarget":
        """Use string values as target.

        Arguments:
            values: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromValues", [*values])

    @property
    @jsii.member(jsii_name="aliasTarget")
    def alias_target(self) -> typing.Optional["IAliasRecordTarget"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "aliasTarget")

    @property
    @jsii.member(jsii_name="values")
    def values(self) -> typing.Optional[typing.List[str]]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "values")


class AddressRecordTarget(RecordTarget, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.AddressRecordTarget"):
    """
    Stability:
        experimental
    """
    def __init__(self, values: typing.Optional[typing.List[str]]=None, alias_target: typing.Optional["IAliasRecordTarget"]=None) -> None:
        """
        Arguments:
            values: -
            aliasTarget: -

        Stability:
            experimental
        """
        jsii.create(AddressRecordTarget, self, [values, alias_target])

    @jsii.member(jsii_name="fromIpAddresses")
    @classmethod
    def from_ip_addresses(cls, *ip_addresses: str) -> "RecordTarget":
        """Use ip adresses as target.

        Arguments:
            ipAddresses: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromIpAddresses", [*ip_addresses])


@jsii.enum(jsii_type="@aws-cdk/aws-route53.RecordType")
class RecordType(enum.Enum):
    """The record type.

    Stability:
        experimental
    """
    A = "A"
    """
    Stability:
        experimental
    """
    AAAA = "AAAA"
    """
    Stability:
        experimental
    """
    CAA = "CAA"
    """
    Stability:
        experimental
    """
    CNAME = "CNAME"
    """
    Stability:
        experimental
    """
    MX = "MX"
    """
    Stability:
        experimental
    """
    NAPTR = "NAPTR"
    """
    Stability:
        experimental
    """
    NS = "NS"
    """
    Stability:
        experimental
    """
    PTR = "PTR"
    """
    Stability:
        experimental
    """
    SOA = "SOA"
    """
    Stability:
        experimental
    """
    SPF = "SPF"
    """
    Stability:
        experimental
    """
    SRV = "SRV"
    """
    Stability:
        experimental
    """
    TXT = "TXT"
    """
    Stability:
        experimental
    """

class SrvRecord(RecordSet, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.SrvRecord"):
    """A DNS SRV record.

    Stability:
        experimental
    resource:
        AWS::Route53::RecordSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, values: typing.List["SrvRecordValue"], zone: "IHostedZone", comment: typing.Optional[str]=None, record_name: typing.Optional[str]=None, ttl: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            values: The values.
            zone: The hosted zone in which to define the new record.
            comment: A comment to add on the record. Default: no comment
            recordName: The domain name for this record. Default: zone root
            ttl: The resource record cache time to live (TTL) in seconds. Default: 1800 seconds

        Stability:
            experimental
        """
        props: SrvRecordProps = {"values": values, "zone": zone}

        if comment is not None:
            props["comment"] = comment

        if record_name is not None:
            props["recordName"] = record_name

        if ttl is not None:
            props["ttl"] = ttl

        jsii.create(SrvRecord, self, [scope, id, props])


@jsii.data_type(jsii_type="@aws-cdk/aws-route53.SrvRecordProps", jsii_struct_bases=[RecordSetOptions])
class SrvRecordProps(RecordSetOptions, jsii.compat.TypedDict):
    """Construction properties for a SrvRecord.

    Stability:
        experimental
    """
    values: typing.List["SrvRecordValue"]
    """The values.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.SrvRecordValue", jsii_struct_bases=[])
class SrvRecordValue(jsii.compat.TypedDict):
    """Properties for a SRV record value.

    Stability:
        experimental
    """
    hostName: str
    """The server host name.

    Stability:
        experimental
    """

    port: jsii.Number
    """The port.

    Stability:
        experimental
    """

    priority: jsii.Number
    """The priority.

    Stability:
        experimental
    """

    weight: jsii.Number
    """The weight.

    Stability:
        experimental
    """

class TxtRecord(RecordSet, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.TxtRecord"):
    """A DNS TXT record.

    Stability:
        experimental
    resource:
        AWS::Route53::RecordSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, values: typing.List[str], zone: "IHostedZone", comment: typing.Optional[str]=None, record_name: typing.Optional[str]=None, ttl: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            values: The text values.
            zone: The hosted zone in which to define the new record.
            comment: A comment to add on the record. Default: no comment
            recordName: The domain name for this record. Default: zone root
            ttl: The resource record cache time to live (TTL) in seconds. Default: 1800 seconds

        Stability:
            experimental
        """
        props: TxtRecordProps = {"values": values, "zone": zone}

        if comment is not None:
            props["comment"] = comment

        if record_name is not None:
            props["recordName"] = record_name

        if ttl is not None:
            props["ttl"] = ttl

        jsii.create(TxtRecord, self, [scope, id, props])


@jsii.data_type(jsii_type="@aws-cdk/aws-route53.TxtRecordProps", jsii_struct_bases=[RecordSetOptions])
class TxtRecordProps(RecordSetOptions, jsii.compat.TypedDict):
    """Construction properties for a TxtRecord.

    Stability:
        experimental
    """
    values: typing.List[str]
    """The text values.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53.ZoneDelegationOptions", jsii_struct_bases=[])
class ZoneDelegationOptions(jsii.compat.TypedDict, total=False):
    """Options available when creating a delegation relationship from one PublicHostedZone to another.

    Stability:
        experimental
    """
    comment: str
    """A comment to add on the DNS record created to incorporate the delegation.

    Default:
        none

    Stability:
        experimental
    """

    ttl: jsii.Number
    """The TTL (Time To Live) of the DNS delegation record in DNS caches.

    Default:
        172800

    Stability:
        experimental
    """

class ZoneDelegationRecord(RecordSet, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53.ZoneDelegationRecord"):
    """A record to delegate further lookups to a different set of name servers.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name_servers: typing.List[str], zone: "IHostedZone", comment: typing.Optional[str]=None, record_name: typing.Optional[str]=None, ttl: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            nameServers: The name servers to report in the delegation records.
            zone: The hosted zone in which to define the new record.
            comment: A comment to add on the record. Default: no comment
            recordName: The domain name for this record. Default: zone root
            ttl: The resource record cache time to live (TTL) in seconds. Default: 1800 seconds

        Stability:
            experimental
        """
        props: ZoneDelegationRecordProps = {"nameServers": name_servers, "zone": zone}

        if comment is not None:
            props["comment"] = comment

        if record_name is not None:
            props["recordName"] = record_name

        if ttl is not None:
            props["ttl"] = ttl

        jsii.create(ZoneDelegationRecord, self, [scope, id, props])


@jsii.data_type(jsii_type="@aws-cdk/aws-route53.ZoneDelegationRecordProps", jsii_struct_bases=[RecordSetOptions])
class ZoneDelegationRecordProps(RecordSetOptions, jsii.compat.TypedDict):
    """Construction properties for a ZoneDelegationRecord.

    Stability:
        experimental
    """
    nameServers: typing.List[str]
    """The name servers to report in the delegation records.

    Stability:
        experimental
    """

__all__ = ["ARecord", "ARecordProps", "AaaaRecord", "AaaaRecordProps", "AddressRecordTarget", "AliasRecordTargetConfig", "CaaAmazonRecord", "CaaAmazonRecordProps", "CaaRecord", "CaaRecordProps", "CaaRecordValue", "CaaTag", "CfnHealthCheck", "CfnHealthCheckProps", "CfnHostedZone", "CfnHostedZoneProps", "CfnRecordSet", "CfnRecordSetGroup", "CfnRecordSetGroupProps", "CfnRecordSetProps", "CnameRecord", "CnameRecordProps", "CommonHostedZoneProps", "HostedZone", "HostedZoneAttributes", "HostedZoneProps", "HostedZoneProvider", "HostedZoneProviderProps", "IAliasRecordTarget", "IHostedZone", "IPrivateHostedZone", "IPublicHostedZone", "IRecordSet", "MxRecord", "MxRecordProps", "MxRecordValue", "PrivateHostedZone", "PrivateHostedZoneProps", "PublicHostedZone", "PublicHostedZoneProps", "RecordSet", "RecordSetOptions", "RecordSetProps", "RecordTarget", "RecordType", "SrvRecord", "SrvRecordProps", "SrvRecordValue", "TxtRecord", "TxtRecordProps", "ZoneDelegationOptions", "ZoneDelegationRecord", "ZoneDelegationRecordProps", "__jsii_assembly__"]

publication.publish()
