import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-route53resolver", "0.35.0", __name__, "aws-route53resolver@0.35.0.jsii.tgz")
class CfnResolverEndpoint(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-route53resolver.CfnResolverEndpoint"):
    """A CloudFormation ``AWS::Route53Resolver::ResolverEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Route53Resolver::ResolverEndpoint
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, direction: str, ip_addresses: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union["IpAddressRequestProperty", aws_cdk.cdk.IResolvable]]], security_group_ids: typing.List[str], name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
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
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrDirection")
    def attr_direction(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Direction
        """
        return jsii.get(self, "attrDirection")

    @property
    @jsii.member(jsii_name="attrHostVpcId")
    def attr_host_vpc_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            HostVPCId
        """
        return jsii.get(self, "attrHostVpcId")

    @property
    @jsii.member(jsii_name="attrIpAddressCount")
    def attr_ip_address_count(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            IpAddressCount
        """
        return jsii.get(self, "attrIpAddressCount")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="attrResolverEndpointId")
    def attr_resolver_endpoint_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ResolverEndpointId
        """
        return jsii.get(self, "attrResolverEndpointId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::Route53Resolver::ResolverEndpoint.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="direction")
    def direction(self) -> str:
        """``AWS::Route53Resolver::ResolverEndpoint.Direction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-direction
        Stability:
            experimental
        """
        return jsii.get(self, "direction")

    @direction.setter
    def direction(self, value: str):
        return jsii.set(self, "direction", value)

    @property
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union["IpAddressRequestProperty", aws_cdk.cdk.IResolvable]]]:
        """``AWS::Route53Resolver::ResolverEndpoint.IpAddresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-ipaddresses
        Stability:
            experimental
        """
        return jsii.get(self, "ipAddresses")

    @ip_addresses.setter
    def ip_addresses(self, value: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union["IpAddressRequestProperty", aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "ipAddresses", value)

    @property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[str]:
        """``AWS::Route53Resolver::ResolverEndpoint.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-securitygroupids
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupIds")

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[str]):
        return jsii.set(self, "securityGroupIds", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Route53Resolver::ResolverEndpoint.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverendpoint.html#cfn-route53resolver-resolverendpoint-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

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

    ipAddresses: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union["CfnResolverEndpoint.IpAddressRequestProperty", aws_cdk.cdk.IResolvable]]]
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, domain_name: str, rule_type: str, name: typing.Optional[str]=None, resolver_endpoint_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, target_ips: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "TargetAddressProperty"]]]]]=None) -> None:
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
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrDomainName")
    def attr_domain_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DomainName
        """
        return jsii.get(self, "attrDomainName")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="attrResolverEndpointId")
    def attr_resolver_endpoint_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ResolverEndpointId
        """
        return jsii.get(self, "attrResolverEndpointId")

    @property
    @jsii.member(jsii_name="attrResolverRuleId")
    def attr_resolver_rule_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ResolverRuleId
        """
        return jsii.get(self, "attrResolverRuleId")

    @property
    @jsii.member(jsii_name="attrTargetIps")
    def attr_target_ips(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            TargetIps
        """
        return jsii.get(self, "attrTargetIps")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::Route53Resolver::ResolverRule.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> str:
        """``AWS::Route53Resolver::ResolverRule.DomainName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-domainname
        Stability:
            experimental
        """
        return jsii.get(self, "domainName")

    @domain_name.setter
    def domain_name(self, value: str):
        return jsii.set(self, "domainName", value)

    @property
    @jsii.member(jsii_name="ruleType")
    def rule_type(self) -> str:
        """``AWS::Route53Resolver::ResolverRule.RuleType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-ruletype
        Stability:
            experimental
        """
        return jsii.get(self, "ruleType")

    @rule_type.setter
    def rule_type(self, value: str):
        return jsii.set(self, "ruleType", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Route53Resolver::ResolverRule.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="resolverEndpointId")
    def resolver_endpoint_id(self) -> typing.Optional[str]:
        """``AWS::Route53Resolver::ResolverRule.ResolverEndpointId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-resolverendpointid
        Stability:
            experimental
        """
        return jsii.get(self, "resolverEndpointId")

    @resolver_endpoint_id.setter
    def resolver_endpoint_id(self, value: typing.Optional[str]):
        return jsii.set(self, "resolverEndpointId", value)

    @property
    @jsii.member(jsii_name="targetIps")
    def target_ips(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "TargetAddressProperty"]]]]]:
        """``AWS::Route53Resolver::ResolverRule.TargetIps``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverrule.html#cfn-route53resolver-resolverrule-targetips
        Stability:
            experimental
        """
        return jsii.get(self, "targetIps")

    @target_ips.setter
    def target_ips(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "TargetAddressProperty"]]]]]):
        return jsii.set(self, "targetIps", value)

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
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="attrResolverRuleAssociationId")
    def attr_resolver_rule_association_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ResolverRuleAssociationId
        """
        return jsii.get(self, "attrResolverRuleAssociationId")

    @property
    @jsii.member(jsii_name="attrResolverRuleId")
    def attr_resolver_rule_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ResolverRuleId
        """
        return jsii.get(self, "attrResolverRuleId")

    @property
    @jsii.member(jsii_name="attrVpcId")
    def attr_vpc_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            VPCId
        """
        return jsii.get(self, "attrVpcId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="resolverRuleId")
    def resolver_rule_id(self) -> str:
        """``AWS::Route53Resolver::ResolverRuleAssociation.ResolverRuleId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-resolverruleid
        Stability:
            experimental
        """
        return jsii.get(self, "resolverRuleId")

    @resolver_rule_id.setter
    def resolver_rule_id(self, value: str):
        return jsii.set(self, "resolverRuleId", value)

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """``AWS::Route53Resolver::ResolverRuleAssociation.VPCId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-vpcid
        Stability:
            experimental
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: str):
        return jsii.set(self, "vpcId", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Route53Resolver::ResolverRuleAssociation.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53resolver-resolverruleassociation.html#cfn-route53resolver-resolverruleassociation-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


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
    targetIps: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnResolverRule.TargetAddressProperty"]]]
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
