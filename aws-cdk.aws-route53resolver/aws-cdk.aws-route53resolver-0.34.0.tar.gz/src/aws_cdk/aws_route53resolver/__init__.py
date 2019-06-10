import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-route53resolver", "0.34.0", __name__, "aws-route53resolver@0.34.0.jsii.tgz")
class CfnResolverEndpoint(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53resolver.CfnResolverEndpoint"):
    """A CloudFormation ``AWS::Route53Resolver::ResolverEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Route53Resolver::ResolverEndpoint
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, direction: str, ip_addresses: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["IpAddressRequestProperty", aws_cdk.cdk.Token]]], security_group_ids: typing.List[str], name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::Route53Resolver::ResolverEndpoint``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            direction: ``AWS::Route53Resolver::ResolverEndpoint.Direction``.
            ipAddresses: ``AWS::Route53Resolver::ResolverEndpoint.IpAddresses``.
            securityGroupIds: ``AWS::Route53Resolver::ResolverEndpoint.SecurityGroupIds``.
            name: ``AWS::Route53Resolver::ResolverEndpoint.Name``.
            tags: ``AWS::Route53Resolver::ResolverEndpoint.Tags``.

        Stability:
            experimental
        """
        props: CfnResolverEndpointProps = {"direction": direction, "ipAddresses": ip_addresses, "securityGroupIds": security_group_ids}

        if name is not None:
            props["name"] = name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnResolverEndpoint, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnResolverEndpointProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="resolverEndpointArn")
    def resolver_endpoint_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "resolverEndpointArn")

    @property
    @jsii.member(jsii_name="resolverEndpointDirection")
    def resolver_endpoint_direction(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Direction
        """
        return jsii.get(self, "resolverEndpointDirection")

    @property
    @jsii.member(jsii_name="resolverEndpointHostVpcId")
    def resolver_endpoint_host_vpc_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            HostVPCId
        """
        return jsii.get(self, "resolverEndpointHostVpcId")

    @property
    @jsii.member(jsii_name="resolverEndpointId")
    def resolver_endpoint_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ResolverEndpointId
        """
        return jsii.get(self, "resolverEndpointId")

    @property
    @jsii.member(jsii_name="resolverEndpointIpAddressCount")
    def resolver_endpoint_ip_address_count(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            IpAddressCount
        """
        return jsii.get(self, "resolverEndpointIpAddressCount")

    @property
    @jsii.member(jsii_name="resolverEndpointName")
    def resolver_endpoint_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "resolverEndpointName")

    @property
    @jsii.member(jsii_name="resolverEndpointObject")
    def resolver_endpoint_object(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "resolverEndpointObject")

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
    class _IpAddressRequestProperty(jsii.compat.TypedDict, total=False):
        ip: str
        """``CfnResolverEndpoint.IpAddressRequestProperty.Ip``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverendpoint-ipaddressrequest.html#cfn-route53resolver-resolverendpoint-ipaddressrequest-ip
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53resolver.CfnResolverEndpoint.IpAddressRequestProperty", jsii_struct_bases=[_IpAddressRequestProperty])
    class IpAddressRequestProperty(_IpAddressRequestProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverendpoint-ipaddressrequest.html
        Stability:
            experimental
        """
        subnetId: str
        """``CfnResolverEndpoint.IpAddressRequestProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverendpoint-ipaddressrequest.html#cfn-route53resolver-resolverendpoint-ipaddressrequest-subnetid
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnResolverEndpointProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::Route53Resolver::ResolverEndpoint.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-name
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Route53Resolver::ResolverEndpoint.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53resolver.CfnResolverEndpointProps", jsii_struct_bases=[_CfnResolverEndpointProps])
class CfnResolverEndpointProps(_CfnResolverEndpointProps):
    """Properties for defining a ``AWS::Route53Resolver::ResolverEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html
    Stability:
        experimental
    """
    direction: str
    """``AWS::Route53Resolver::ResolverEndpoint.Direction``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-direction
    Stability:
        experimental
    """

    ipAddresses: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnResolverEndpoint.IpAddressRequestProperty", aws_cdk.cdk.Token]]]
    """``AWS::Route53Resolver::ResolverEndpoint.IpAddresses``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-ipaddresses
    Stability:
        experimental
    """

    securityGroupIds: typing.List[str]
    """``AWS::Route53Resolver::ResolverEndpoint.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-securitygroupids
    Stability:
        experimental
    """

class CfnResolverRule(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRule"):
    """A CloudFormation ``AWS::Route53Resolver::ResolverRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Route53Resolver::ResolverRule
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, domain_name: str, rule_type: str, name: typing.Optional[str]=None, resolver_endpoint_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, target_ips: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "TargetAddressProperty"]]]]]=None) -> None:
        """Create a new ``AWS::Route53Resolver::ResolverRule``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            domainName: ``AWS::Route53Resolver::ResolverRule.DomainName``.
            ruleType: ``AWS::Route53Resolver::ResolverRule.RuleType``.
            name: ``AWS::Route53Resolver::ResolverRule.Name``.
            resolverEndpointId: ``AWS::Route53Resolver::ResolverRule.ResolverEndpointId``.
            tags: ``AWS::Route53Resolver::ResolverRule.Tags``.
            targetIps: ``AWS::Route53Resolver::ResolverRule.TargetIps``.

        Stability:
            experimental
        """
        props: CfnResolverRuleProps = {"domainName": domain_name, "ruleType": rule_type}

        if name is not None:
            props["name"] = name

        if resolver_endpoint_id is not None:
            props["resolverEndpointId"] = resolver_endpoint_id

        if tags is not None:
            props["tags"] = tags

        if target_ips is not None:
            props["targetIps"] = target_ips

        jsii.create(CfnResolverRule, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnResolverRuleProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="resolverRuleArn")
    def resolver_rule_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "resolverRuleArn")

    @property
    @jsii.member(jsii_name="resolverRuleDomainName")
    def resolver_rule_domain_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DomainName
        """
        return jsii.get(self, "resolverRuleDomainName")

    @property
    @jsii.member(jsii_name="resolverRuleId")
    def resolver_rule_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ResolverRuleId
        """
        return jsii.get(self, "resolverRuleId")

    @property
    @jsii.member(jsii_name="resolverRuleName")
    def resolver_rule_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "resolverRuleName")

    @property
    @jsii.member(jsii_name="resolverRuleObject")
    def resolver_rule_object(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "resolverRuleObject")

    @property
    @jsii.member(jsii_name="resolverRuleResolverEndpointId")
    def resolver_rule_resolver_endpoint_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ResolverEndpointId
        """
        return jsii.get(self, "resolverRuleResolverEndpointId")

    @property
    @jsii.member(jsii_name="resolverRuleTargetIps")
    def resolver_rule_target_ips(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            TargetIps
        """
        return jsii.get(self, "resolverRuleTargetIps")

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

    @jsii.data_type(jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRule.TargetAddressProperty", jsii_struct_bases=[])
    class TargetAddressProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverrule-targetaddress.html
        Stability:
            experimental
        """
        ip: str
        """``CfnResolverRule.TargetAddressProperty.Ip``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverrule-targetaddress.html#cfn-route53resolver-resolverrule-targetaddress-ip
        Stability:
            experimental
        """

        port: str
        """``CfnResolverRule.TargetAddressProperty.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53resolver-resolverrule-targetaddress.html#cfn-route53resolver-resolverrule-targetaddress-port
        Stability:
            experimental
        """


class CfnResolverRuleAssociation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRuleAssociation"):
    """A CloudFormation ``AWS::Route53Resolver::ResolverRuleAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Route53Resolver::ResolverRuleAssociation
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, resolver_rule_id: str, vpc_id: str, name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Route53Resolver::ResolverRuleAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            resolverRuleId: ``AWS::Route53Resolver::ResolverRuleAssociation.ResolverRuleId``.
            vpcId: ``AWS::Route53Resolver::ResolverRuleAssociation.VPCId``.
            name: ``AWS::Route53Resolver::ResolverRuleAssociation.Name``.

        Stability:
            experimental
        """
        props: CfnResolverRuleAssociationProps = {"resolverRuleId": resolver_rule_id, "vpcId": vpc_id}

        if name is not None:
            props["name"] = name

        jsii.create(CfnResolverRuleAssociation, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnResolverRuleAssociationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="resolverRuleAssociationId")
    def resolver_rule_association_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ResolverRuleAssociationId
        """
        return jsii.get(self, "resolverRuleAssociationId")

    @property
    @jsii.member(jsii_name="resolverRuleAssociationName")
    def resolver_rule_association_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "resolverRuleAssociationName")

    @property
    @jsii.member(jsii_name="resolverRuleAssociationResolverRuleId")
    def resolver_rule_association_resolver_rule_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ResolverRuleId
        """
        return jsii.get(self, "resolverRuleAssociationResolverRuleId")

    @property
    @jsii.member(jsii_name="resolverRuleAssociationVpcId")
    def resolver_rule_association_vpc_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            VPCId
        """
        return jsii.get(self, "resolverRuleAssociationVpcId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnResolverRuleAssociationProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::Route53Resolver::ResolverRuleAssociation.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-name
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRuleAssociationProps", jsii_struct_bases=[_CfnResolverRuleAssociationProps])
class CfnResolverRuleAssociationProps(_CfnResolverRuleAssociationProps):
    """Properties for defining a ``AWS::Route53Resolver::ResolverRuleAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html
    Stability:
        experimental
    """
    resolverRuleId: str
    """``AWS::Route53Resolver::ResolverRuleAssociation.ResolverRuleId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-resolverruleid
    Stability:
        experimental
    """

    vpcId: str
    """``AWS::Route53Resolver::ResolverRuleAssociation.VPCId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-vpcid
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnResolverRuleProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::Route53Resolver::ResolverRule.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-name
    Stability:
        experimental
    """
    resolverEndpointId: str
    """``AWS::Route53Resolver::ResolverRule.ResolverEndpointId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-resolverendpointid
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Route53Resolver::ResolverRule.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-tags
    Stability:
        experimental
    """
    targetIps: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnResolverRule.TargetAddressProperty"]]]
    """``AWS::Route53Resolver::ResolverRule.TargetIps``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-targetips
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-route53resolver.CfnResolverRuleProps", jsii_struct_bases=[_CfnResolverRuleProps])
class CfnResolverRuleProps(_CfnResolverRuleProps):
    """Properties for defining a ``AWS::Route53Resolver::ResolverRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html
    Stability:
        experimental
    """
    domainName: str
    """``AWS::Route53Resolver::ResolverRule.DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-domainname
    Stability:
        experimental
    """

    ruleType: str
    """``AWS::Route53Resolver::ResolverRule.RuleType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-ruletype
    Stability:
        experimental
    """

__all__ = ["CfnResolverEndpoint", "CfnResolverEndpointProps", "CfnResolverRule", "CfnResolverRuleAssociation", "CfnResolverRuleAssociationProps", "CfnResolverRuleProps", "__jsii_assembly__"]

publication.publish()
