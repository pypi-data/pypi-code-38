import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_ec2
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-elasticloadbalancing", "0.34.0", __name__, "aws-elasticloadbalancing@0.34.0.jsii.tgz")
class CfnLoadBalancer(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticloadbalancing.CfnLoadBalancer"):
    """A CloudFormation ``AWS::ElasticLoadBalancing::LoadBalancer``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ElasticLoadBalancing::LoadBalancer
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, listeners: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["ListenersProperty", aws_cdk.cdk.Token]]], access_logging_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["AccessLoggingPolicyProperty"]]]=None, app_cookie_stickiness_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "AppCookieStickinessPolicyProperty"]]]]]=None, availability_zones: typing.Optional[typing.List[str]]=None, connection_draining_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ConnectionDrainingPolicyProperty"]]]=None, connection_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ConnectionSettingsProperty"]]]=None, cross_zone: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, health_check: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["HealthCheckProperty"]]]=None, instances: typing.Optional[typing.List[str]]=None, lb_cookie_stickiness_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "LBCookieStickinessPolicyProperty"]]]]]=None, load_balancer_name: typing.Optional[str]=None, policies: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "PoliciesProperty"]]]]]=None, scheme: typing.Optional[str]=None, security_groups: typing.Optional[typing.List[str]]=None, subnets: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::ElasticLoadBalancing::LoadBalancer``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            listeners: ``AWS::ElasticLoadBalancing::LoadBalancer.Listeners``.
            accessLoggingPolicy: ``AWS::ElasticLoadBalancing::LoadBalancer.AccessLoggingPolicy``.
            appCookieStickinessPolicy: ``AWS::ElasticLoadBalancing::LoadBalancer.AppCookieStickinessPolicy``.
            availabilityZones: ``AWS::ElasticLoadBalancing::LoadBalancer.AvailabilityZones``.
            connectionDrainingPolicy: ``AWS::ElasticLoadBalancing::LoadBalancer.ConnectionDrainingPolicy``.
            connectionSettings: ``AWS::ElasticLoadBalancing::LoadBalancer.ConnectionSettings``.
            crossZone: ``AWS::ElasticLoadBalancing::LoadBalancer.CrossZone``.
            healthCheck: ``AWS::ElasticLoadBalancing::LoadBalancer.HealthCheck``.
            instances: ``AWS::ElasticLoadBalancing::LoadBalancer.Instances``.
            lbCookieStickinessPolicy: ``AWS::ElasticLoadBalancing::LoadBalancer.LBCookieStickinessPolicy``.
            loadBalancerName: ``AWS::ElasticLoadBalancing::LoadBalancer.LoadBalancerName``.
            policies: ``AWS::ElasticLoadBalancing::LoadBalancer.Policies``.
            scheme: ``AWS::ElasticLoadBalancing::LoadBalancer.Scheme``.
            securityGroups: ``AWS::ElasticLoadBalancing::LoadBalancer.SecurityGroups``.
            subnets: ``AWS::ElasticLoadBalancing::LoadBalancer.Subnets``.
            tags: ``AWS::ElasticLoadBalancing::LoadBalancer.Tags``.

        Stability:
            experimental
        """
        props: CfnLoadBalancerProps = {"listeners": listeners}

        if access_logging_policy is not None:
            props["accessLoggingPolicy"] = access_logging_policy

        if app_cookie_stickiness_policy is not None:
            props["appCookieStickinessPolicy"] = app_cookie_stickiness_policy

        if availability_zones is not None:
            props["availabilityZones"] = availability_zones

        if connection_draining_policy is not None:
            props["connectionDrainingPolicy"] = connection_draining_policy

        if connection_settings is not None:
            props["connectionSettings"] = connection_settings

        if cross_zone is not None:
            props["crossZone"] = cross_zone

        if health_check is not None:
            props["healthCheck"] = health_check

        if instances is not None:
            props["instances"] = instances

        if lb_cookie_stickiness_policy is not None:
            props["lbCookieStickinessPolicy"] = lb_cookie_stickiness_policy

        if load_balancer_name is not None:
            props["loadBalancerName"] = load_balancer_name

        if policies is not None:
            props["policies"] = policies

        if scheme is not None:
            props["scheme"] = scheme

        if security_groups is not None:
            props["securityGroups"] = security_groups

        if subnets is not None:
            props["subnets"] = subnets

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnLoadBalancer, self, [scope, id, props])

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
    @jsii.member(jsii_name="loadBalancerCanonicalHostedZoneName")
    def load_balancer_canonical_hosted_zone_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            CanonicalHostedZoneName
        """
        return jsii.get(self, "loadBalancerCanonicalHostedZoneName")

    @property
    @jsii.member(jsii_name="loadBalancerCanonicalHostedZoneNameId")
    def load_balancer_canonical_hosted_zone_name_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            CanonicalHostedZoneNameID
        """
        return jsii.get(self, "loadBalancerCanonicalHostedZoneNameId")

    @property
    @jsii.member(jsii_name="loadBalancerDnsName")
    def load_balancer_dns_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DNSName
        """
        return jsii.get(self, "loadBalancerDnsName")

    @property
    @jsii.member(jsii_name="loadBalancerName")
    def load_balancer_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "loadBalancerName")

    @property
    @jsii.member(jsii_name="loadBalancerSourceSecurityGroupGroupName")
    def load_balancer_source_security_group_group_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            SourceSecurityGroup.GroupName
        """
        return jsii.get(self, "loadBalancerSourceSecurityGroupGroupName")

    @property
    @jsii.member(jsii_name="loadBalancerSourceSecurityGroupOwnerAlias")
    def load_balancer_source_security_group_owner_alias(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            SourceSecurityGroup.OwnerAlias
        """
        return jsii.get(self, "loadBalancerSourceSecurityGroupOwnerAlias")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnLoadBalancerProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """The ``TagManager`` handles setting, removing and formatting tags.

        Tags should be managed either passing them as properties during
        initiation or by calling methods on this object. If both techniques are
        used only the tags from the TagManager will be used. ``Tag`` (aspect)
        will use the manager.

        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _AccessLoggingPolicyProperty(jsii.compat.TypedDict, total=False):
        emitInterval: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLoadBalancer.AccessLoggingPolicyProperty.EmitInterval``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-accessloggingpolicy.html#cfn-elb-accessloggingpolicy-emitinterval
        Stability:
            experimental
        """
        s3BucketPrefix: str
        """``CfnLoadBalancer.AccessLoggingPolicyProperty.S3BucketPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-accessloggingpolicy.html#cfn-elb-accessloggingpolicy-s3bucketprefix
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticloadbalancing.CfnLoadBalancer.AccessLoggingPolicyProperty", jsii_struct_bases=[_AccessLoggingPolicyProperty])
    class AccessLoggingPolicyProperty(_AccessLoggingPolicyProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-accessloggingpolicy.html
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnLoadBalancer.AccessLoggingPolicyProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-accessloggingpolicy.html#cfn-elb-accessloggingpolicy-enabled
        Stability:
            experimental
        """

        s3BucketName: str
        """``CfnLoadBalancer.AccessLoggingPolicyProperty.S3BucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-accessloggingpolicy.html#cfn-elb-accessloggingpolicy-s3bucketname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticloadbalancing.CfnLoadBalancer.AppCookieStickinessPolicyProperty", jsii_struct_bases=[])
    class AppCookieStickinessPolicyProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-AppCookieStickinessPolicy.html
        Stability:
            experimental
        """
        cookieName: str
        """``CfnLoadBalancer.AppCookieStickinessPolicyProperty.CookieName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-AppCookieStickinessPolicy.html#cfn-elb-appcookiestickinesspolicy-cookiename
        Stability:
            experimental
        """

        policyName: str
        """``CfnLoadBalancer.AppCookieStickinessPolicyProperty.PolicyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-AppCookieStickinessPolicy.html#cfn-elb-appcookiestickinesspolicy-policyname
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ConnectionDrainingPolicyProperty(jsii.compat.TypedDict, total=False):
        timeout: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLoadBalancer.ConnectionDrainingPolicyProperty.Timeout``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-connectiondrainingpolicy.html#cfn-elb-connectiondrainingpolicy-timeout
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticloadbalancing.CfnLoadBalancer.ConnectionDrainingPolicyProperty", jsii_struct_bases=[_ConnectionDrainingPolicyProperty])
    class ConnectionDrainingPolicyProperty(_ConnectionDrainingPolicyProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-connectiondrainingpolicy.html
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnLoadBalancer.ConnectionDrainingPolicyProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-connectiondrainingpolicy.html#cfn-elb-connectiondrainingpolicy-enabled
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticloadbalancing.CfnLoadBalancer.ConnectionSettingsProperty", jsii_struct_bases=[])
    class ConnectionSettingsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-connectionsettings.html
        Stability:
            experimental
        """
        idleTimeout: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLoadBalancer.ConnectionSettingsProperty.IdleTimeout``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-connectionsettings.html#cfn-elb-connectionsettings-idletimeout
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticloadbalancing.CfnLoadBalancer.HealthCheckProperty", jsii_struct_bases=[])
    class HealthCheckProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-health-check.html
        Stability:
            experimental
        """
        healthyThreshold: str
        """``CfnLoadBalancer.HealthCheckProperty.HealthyThreshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-health-check.html#cfn-elb-healthcheck-healthythreshold
        Stability:
            experimental
        """

        interval: str
        """``CfnLoadBalancer.HealthCheckProperty.Interval``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-health-check.html#cfn-elb-healthcheck-interval
        Stability:
            experimental
        """

        target: str
        """``CfnLoadBalancer.HealthCheckProperty.Target``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-health-check.html#cfn-elb-healthcheck-target
        Stability:
            experimental
        """

        timeout: str
        """``CfnLoadBalancer.HealthCheckProperty.Timeout``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-health-check.html#cfn-elb-healthcheck-timeout
        Stability:
            experimental
        """

        unhealthyThreshold: str
        """``CfnLoadBalancer.HealthCheckProperty.UnhealthyThreshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-health-check.html#cfn-elb-healthcheck-unhealthythreshold
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticloadbalancing.CfnLoadBalancer.LBCookieStickinessPolicyProperty", jsii_struct_bases=[])
    class LBCookieStickinessPolicyProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-LBCookieStickinessPolicy.html
        Stability:
            experimental
        """
        cookieExpirationPeriod: str
        """``CfnLoadBalancer.LBCookieStickinessPolicyProperty.CookieExpirationPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-LBCookieStickinessPolicy.html#cfn-elb-lbcookiestickinesspolicy-cookieexpirationperiod
        Stability:
            experimental
        """

        policyName: str
        """``CfnLoadBalancer.LBCookieStickinessPolicyProperty.PolicyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-LBCookieStickinessPolicy.html#cfn-elb-lbcookiestickinesspolicy-policyname
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ListenersProperty(jsii.compat.TypedDict, total=False):
        instanceProtocol: str
        """``CfnLoadBalancer.ListenersProperty.InstanceProtocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-listener.html#cfn-ec2-elb-listener-instanceprotocol
        Stability:
            experimental
        """
        policyNames: typing.List[str]
        """``CfnLoadBalancer.ListenersProperty.PolicyNames``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-listener.html#cfn-ec2-elb-listener-policynames
        Stability:
            experimental
        """
        sslCertificateId: str
        """``CfnLoadBalancer.ListenersProperty.SSLCertificateId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-listener.html#cfn-ec2-elb-listener-sslcertificateid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticloadbalancing.CfnLoadBalancer.ListenersProperty", jsii_struct_bases=[_ListenersProperty])
    class ListenersProperty(_ListenersProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-listener.html
        Stability:
            experimental
        """
        instancePort: str
        """``CfnLoadBalancer.ListenersProperty.InstancePort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-listener.html#cfn-ec2-elb-listener-instanceport
        Stability:
            experimental
        """

        loadBalancerPort: str
        """``CfnLoadBalancer.ListenersProperty.LoadBalancerPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-listener.html#cfn-ec2-elb-listener-loadbalancerport
        Stability:
            experimental
        """

        protocol: str
        """``CfnLoadBalancer.ListenersProperty.Protocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-listener.html#cfn-ec2-elb-listener-protocol
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _PoliciesProperty(jsii.compat.TypedDict, total=False):
        instancePorts: typing.List[str]
        """``CfnLoadBalancer.PoliciesProperty.InstancePorts``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-policy.html#cfn-ec2-elb-policy-instanceports
        Stability:
            experimental
        """
        loadBalancerPorts: typing.List[str]
        """``CfnLoadBalancer.PoliciesProperty.LoadBalancerPorts``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-policy.html#cfn-ec2-elb-policy-loadbalancerports
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticloadbalancing.CfnLoadBalancer.PoliciesProperty", jsii_struct_bases=[_PoliciesProperty])
    class PoliciesProperty(_PoliciesProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-policy.html
        Stability:
            experimental
        """
        attributes: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]]]
        """``CfnLoadBalancer.PoliciesProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-policy.html#cfn-ec2-elb-policy-attributes
        Stability:
            experimental
        """

        policyName: str
        """``CfnLoadBalancer.PoliciesProperty.PolicyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-policy.html#cfn-ec2-elb-policy-policyname
        Stability:
            experimental
        """

        policyType: str
        """``CfnLoadBalancer.PoliciesProperty.PolicyType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb-policy.html#cfn-ec2-elb-policy-policytype
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnLoadBalancerProps(jsii.compat.TypedDict, total=False):
    accessLoggingPolicy: typing.Union[aws_cdk.cdk.Token, "CfnLoadBalancer.AccessLoggingPolicyProperty"]
    """``AWS::ElasticLoadBalancing::LoadBalancer.AccessLoggingPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-accessloggingpolicy
    Stability:
        experimental
    """
    appCookieStickinessPolicy: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLoadBalancer.AppCookieStickinessPolicyProperty"]]]
    """``AWS::ElasticLoadBalancing::LoadBalancer.AppCookieStickinessPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-appcookiestickinesspolicy
    Stability:
        experimental
    """
    availabilityZones: typing.List[str]
    """``AWS::ElasticLoadBalancing::LoadBalancer.AvailabilityZones``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-availabilityzones
    Stability:
        experimental
    """
    connectionDrainingPolicy: typing.Union[aws_cdk.cdk.Token, "CfnLoadBalancer.ConnectionDrainingPolicyProperty"]
    """``AWS::ElasticLoadBalancing::LoadBalancer.ConnectionDrainingPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-connectiondrainingpolicy
    Stability:
        experimental
    """
    connectionSettings: typing.Union[aws_cdk.cdk.Token, "CfnLoadBalancer.ConnectionSettingsProperty"]
    """``AWS::ElasticLoadBalancing::LoadBalancer.ConnectionSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-connectionsettings
    Stability:
        experimental
    """
    crossZone: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ElasticLoadBalancing::LoadBalancer.CrossZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-crosszone
    Stability:
        experimental
    """
    healthCheck: typing.Union[aws_cdk.cdk.Token, "CfnLoadBalancer.HealthCheckProperty"]
    """``AWS::ElasticLoadBalancing::LoadBalancer.HealthCheck``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-healthcheck
    Stability:
        experimental
    """
    instances: typing.List[str]
    """``AWS::ElasticLoadBalancing::LoadBalancer.Instances``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-instances
    Stability:
        experimental
    """
    lbCookieStickinessPolicy: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLoadBalancer.LBCookieStickinessPolicyProperty"]]]
    """``AWS::ElasticLoadBalancing::LoadBalancer.LBCookieStickinessPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-lbcookiestickinesspolicy
    Stability:
        experimental
    """
    loadBalancerName: str
    """``AWS::ElasticLoadBalancing::LoadBalancer.LoadBalancerName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-elbname
    Stability:
        experimental
    """
    policies: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLoadBalancer.PoliciesProperty"]]]
    """``AWS::ElasticLoadBalancing::LoadBalancer.Policies``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-policies
    Stability:
        experimental
    """
    scheme: str
    """``AWS::ElasticLoadBalancing::LoadBalancer.Scheme``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-scheme
    Stability:
        experimental
    """
    securityGroups: typing.List[str]
    """``AWS::ElasticLoadBalancing::LoadBalancer.SecurityGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-securitygroups
    Stability:
        experimental
    """
    subnets: typing.List[str]
    """``AWS::ElasticLoadBalancing::LoadBalancer.Subnets``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-subnets
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::ElasticLoadBalancing::LoadBalancer.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-elasticloadbalancing-loadbalancer-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticloadbalancing.CfnLoadBalancerProps", jsii_struct_bases=[_CfnLoadBalancerProps])
class CfnLoadBalancerProps(_CfnLoadBalancerProps):
    """Properties for defining a ``AWS::ElasticLoadBalancing::LoadBalancer``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html
    Stability:
        experimental
    """
    listeners: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnLoadBalancer.ListenersProperty", aws_cdk.cdk.Token]]]
    """``AWS::ElasticLoadBalancing::LoadBalancer.Listeners``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html#cfn-ec2-elb-listeners
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _HealthCheck(jsii.compat.TypedDict, total=False):
    healthyThreshold: jsii.Number
    """After how many successful checks is an instance considered healthy.

    Default:
        2

    Stability:
        experimental
    """
    interval: jsii.Number
    """Number of seconds between health checks.

    Default:
        30

    Stability:
        experimental
    """
    path: str
    """What path to use for HTTP or HTTPS health check (must return 200).

    For SSL and TCP health checks, accepting connections is enough to be considered
    healthy.

    Default:
        "/"

    Stability:
        experimental
    """
    protocol: "LoadBalancingProtocol"
    """What protocol to use for health checking.

    The protocol is automatically determined from the port if it's not supplied.

    Default:
        Automatic

    Stability:
        experimental
    """
    timeout: jsii.Number
    """Health check timeout.

    Default:
        5

    Stability:
        experimental
    """
    unhealthyThreshold: jsii.Number
    """After how many unsuccessful checks is an instance considered unhealthy.

    Default:
        5

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticloadbalancing.HealthCheck", jsii_struct_bases=[_HealthCheck])
class HealthCheck(_HealthCheck):
    """Describe the health check to a load balancer.

    Stability:
        experimental
    """
    port: jsii.Number
    """What port number to health check on.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-elasticloadbalancing.ILoadBalancerTarget")
class ILoadBalancerTarget(aws_cdk.aws_ec2.IConnectable, jsii.compat.Protocol):
    """Interface that is going to be implemented by constructs that you can load balance to.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ILoadBalancerTargetProxy

    @jsii.member(jsii_name="attachToClassicLB")
    def attach_to_classic_lb(self, load_balancer: "LoadBalancer") -> None:
        """Attach load-balanced target to a classic ELB.

        Arguments:
            loadBalancer: [disable-awslint:ref-via-interface] The load balancer to attach the target to.

        Stability:
            experimental
        """
        ...


class _ILoadBalancerTargetProxy(jsii.proxy_for(aws_cdk.aws_ec2.IConnectable)):
    """Interface that is going to be implemented by constructs that you can load balance to.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-elasticloadbalancing.ILoadBalancerTarget"
    @jsii.member(jsii_name="attachToClassicLB")
    def attach_to_classic_lb(self, load_balancer: "LoadBalancer") -> None:
        """Attach load-balanced target to a classic ELB.

        Arguments:
            loadBalancer: [disable-awslint:ref-via-interface] The load balancer to attach the target to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachToClassicLB", [load_balancer])


@jsii.implements(aws_cdk.aws_ec2.IConnectable)
class ListenerPort(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticloadbalancing.ListenerPort"):
    """Reference to a listener's port just created.

    This implements IConnectable with a default port (the port that an ELB
    listener was just created on) for a given security group so that it can be
    conveniently used just like any Connectable. E.g::

       const listener = elb.addListener(...);

       listener.connections.allowDefaultPortFromAnyIPv4();
       // or
       instance.connections.allowToDefaultPort(listener);

    Stability:
        experimental
    """
    def __init__(self, security_group: aws_cdk.aws_ec2.ISecurityGroup, default_port_range: aws_cdk.aws_ec2.IPortRange) -> None:
        """
        Arguments:
            securityGroup: -
            defaultPortRange: -

        Stability:
            experimental
        """
        jsii.create(ListenerPort, self, [security_group, default_port_range])

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "connections")


@jsii.implements(aws_cdk.aws_ec2.IConnectable)
class LoadBalancer(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticloadbalancing.LoadBalancer"):
    """A load balancer with a single listener.

    Routes to a fleet of of instances in a VPC.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc: aws_cdk.aws_ec2.IVpc, health_check: typing.Optional["HealthCheck"]=None, internet_facing: typing.Optional[bool]=None, listeners: typing.Optional[typing.List["LoadBalancerListener"]]=None, targets: typing.Optional[typing.List["ILoadBalancerTarget"]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            vpc: VPC network of the fleet instances.
            healthCheck: Health check settings for the load balancing targets. Not required but recommended. Default: - None.
            internetFacing: Whether this is an internet-facing Load Balancer. This controls whether the LB has a public IP address assigned. It does not open up the Load Balancer's security groups to public internet access. Default: false
            listeners: What listeners to set up for the load balancer. Can also be added by .addListener() Default: -
            targets: What targets to load balance to. Can also be added by .addTarget() Default: - None.

        Stability:
            experimental
        """
        props: LoadBalancerProps = {"vpc": vpc}

        if health_check is not None:
            props["healthCheck"] = health_check

        if internet_facing is not None:
            props["internetFacing"] = internet_facing

        if listeners is not None:
            props["listeners"] = listeners

        if targets is not None:
            props["targets"] = targets

        jsii.create(LoadBalancer, self, [scope, id, props])

    @jsii.member(jsii_name="addListener")
    def add_listener(self, *, external_port: jsii.Number, allow_connections_from: typing.Optional[typing.List[aws_cdk.aws_ec2.IConnectable]]=None, external_protocol: typing.Optional["LoadBalancingProtocol"]=None, internal_port: typing.Optional[jsii.Number]=None, internal_protocol: typing.Optional["LoadBalancingProtocol"]=None, policy_names: typing.Optional[typing.List[str]]=None, ssl_certificate_id: typing.Optional[str]=None) -> "ListenerPort":
        """Add a backend to the load balancer.

        Arguments:
            listener: -
            externalPort: External listening port.
            allowConnectionsFrom: Allow connections to the load balancer from the given set of connection peers. By default, connections will be allowed from anywhere. Set this to an empty list to deny connections, or supply a custom list of peers to allow connections from (IP ranges or security groups). Default: Anywhere
            externalProtocol: What public protocol to use for load balancing. Either 'tcp', 'ssl', 'http' or 'https'. May be omitted if the external port is either 80 or 443.
            internalPort: Instance listening port. Same as the externalPort if not specified. Default: externalPort
            internalProtocol: What public protocol to use for load balancing. Either 'tcp', 'ssl', 'http' or 'https'. May be omitted if the internal port is either 80 or 443. The instance protocol is 'tcp' if the front-end protocol is 'tcp' or 'ssl', the instance protocol is 'http' if the front-end protocol is 'https'.
            policyNames: SSL policy names.
            sslCertificateId: ID of SSL certificate.

        Returns:
            A ListenerPort object that controls connections to the listener port

        Stability:
            experimental
        """
        listener: LoadBalancerListener = {"externalPort": external_port}

        if allow_connections_from is not None:
            listener["allowConnectionsFrom"] = allow_connections_from

        if external_protocol is not None:
            listener["externalProtocol"] = external_protocol

        if internal_port is not None:
            listener["internalPort"] = internal_port

        if internal_protocol is not None:
            listener["internalProtocol"] = internal_protocol

        if policy_names is not None:
            listener["policyNames"] = policy_names

        if ssl_certificate_id is not None:
            listener["sslCertificateId"] = ssl_certificate_id

        return jsii.invoke(self, "addListener", [listener])

    @jsii.member(jsii_name="addTarget")
    def add_target(self, target: "ILoadBalancerTarget") -> None:
        """
        Arguments:
            target: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addTarget", [target])

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """Control all connections from and to this load balancer.

        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="listenerPorts")
    def listener_ports(self) -> typing.List["ListenerPort"]:
        """An object controlling specifically the connections for each listener added to this load balancer.

        Stability:
            experimental
        """
        return jsii.get(self, "listenerPorts")

    @property
    @jsii.member(jsii_name="loadBalancerCanonicalHostedZoneName")
    def load_balancer_canonical_hosted_zone_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "loadBalancerCanonicalHostedZoneName")

    @property
    @jsii.member(jsii_name="loadBalancerCanonicalHostedZoneNameId")
    def load_balancer_canonical_hosted_zone_name_id(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "loadBalancerCanonicalHostedZoneNameId")

    @property
    @jsii.member(jsii_name="loadBalancerDnsName")
    def load_balancer_dns_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "loadBalancerDnsName")

    @property
    @jsii.member(jsii_name="loadBalancerName")
    def load_balancer_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "loadBalancerName")

    @property
    @jsii.member(jsii_name="loadBalancerSourceSecurityGroupGroupName")
    def load_balancer_source_security_group_group_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "loadBalancerSourceSecurityGroupGroupName")

    @property
    @jsii.member(jsii_name="loadBalancerSourceSecurityGroupOwnerAlias")
    def load_balancer_source_security_group_owner_alias(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "loadBalancerSourceSecurityGroupOwnerAlias")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _LoadBalancerListener(jsii.compat.TypedDict, total=False):
    allowConnectionsFrom: typing.List[aws_cdk.aws_ec2.IConnectable]
    """Allow connections to the load balancer from the given set of connection peers.

    By default, connections will be allowed from anywhere. Set this to an empty list
    to deny connections, or supply a custom list of peers to allow connections from
    (IP ranges or security groups).

    Default:
        Anywhere

    Stability:
        experimental
    """
    externalProtocol: "LoadBalancingProtocol"
    """What public protocol to use for load balancing.

    Either 'tcp', 'ssl', 'http' or 'https'.

    May be omitted if the external port is either 80 or 443.

    Stability:
        experimental
    """
    internalPort: jsii.Number
    """Instance listening port.

    Same as the externalPort if not specified.

    Default:
        externalPort

    Stability:
        experimental
    """
    internalProtocol: "LoadBalancingProtocol"
    """What public protocol to use for load balancing.

    Either 'tcp', 'ssl', 'http' or 'https'.

    May be omitted if the internal port is either 80 or 443.

    The instance protocol is 'tcp' if the front-end protocol
    is 'tcp' or 'ssl', the instance protocol is 'http' if the
    front-end protocol is 'https'.

    Stability:
        experimental
    """
    policyNames: typing.List[str]
    """SSL policy names.

    Stability:
        experimental
    """
    sslCertificateId: str
    """ID of SSL certificate.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticloadbalancing.LoadBalancerListener", jsii_struct_bases=[_LoadBalancerListener])
class LoadBalancerListener(_LoadBalancerListener):
    """Add a backend to the load balancer.

    Stability:
        experimental
    """
    externalPort: jsii.Number
    """External listening port.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _LoadBalancerProps(jsii.compat.TypedDict, total=False):
    healthCheck: "HealthCheck"
    """Health check settings for the load balancing targets.

    Not required but recommended.

    Default:
        - None.

    Stability:
        experimental
    """
    internetFacing: bool
    """Whether this is an internet-facing Load Balancer.

    This controls whether the LB has a public IP address assigned. It does
    not open up the Load Balancer's security groups to public internet access.

    Default:
        false

    Stability:
        experimental
    """
    listeners: typing.List["LoadBalancerListener"]
    """What listeners to set up for the load balancer.

    Can also be added by .addListener()

    Default:
        -

    Stability:
        experimental
    """
    targets: typing.List["ILoadBalancerTarget"]
    """What targets to load balance to.

    Can also be added by .addTarget()

    Default:
        - None.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticloadbalancing.LoadBalancerProps", jsii_struct_bases=[_LoadBalancerProps])
class LoadBalancerProps(_LoadBalancerProps):
    """Construction properties for a LoadBalancer.

    Stability:
        experimental
    """
    vpc: aws_cdk.aws_ec2.IVpc
    """VPC network of the fleet instances.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-elasticloadbalancing.LoadBalancingProtocol")
class LoadBalancingProtocol(enum.Enum):
    """
    Stability:
        experimental
    """
    Tcp = "Tcp"
    """
    Stability:
        experimental
    """
    Ssl = "Ssl"
    """
    Stability:
        experimental
    """
    Http = "Http"
    """
    Stability:
        experimental
    """
    Https = "Https"
    """
    Stability:
        experimental
    """

__all__ = ["CfnLoadBalancer", "CfnLoadBalancerProps", "HealthCheck", "ILoadBalancerTarget", "ListenerPort", "LoadBalancer", "LoadBalancerListener", "LoadBalancerProps", "LoadBalancingProtocol", "__jsii_assembly__"]

publication.publish()
