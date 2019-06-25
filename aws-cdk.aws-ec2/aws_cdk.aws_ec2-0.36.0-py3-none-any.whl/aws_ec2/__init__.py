import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_cloudwatch
import aws_cdk.aws_iam
import aws_cdk.aws_ssm
import aws_cdk.core
import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-ec2", "0.36.0", __name__, "aws-ec2@0.36.0.jsii.tgz")
@jsii.enum(jsii_type="@aws-cdk/aws-ec2.AmazonLinuxEdition")
class AmazonLinuxEdition(enum.Enum):
    """Amazon Linux edition.

    Stability:
        experimental
    """
    STANDARD = "STANDARD"
    """Standard edition.

    Stability:
        experimental
    """
    MINIMAL = "MINIMAL"
    """Minimal edition.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ec2.AmazonLinuxGeneration")
class AmazonLinuxGeneration(enum.Enum):
    """What generation of Amazon Linux to use.

    Stability:
        experimental
    """
    AMAZON_LINUX = "AMAZON_LINUX"
    """Amazon Linux.

    Stability:
        experimental
    """
    AMAZON_LINUX_2 = "AMAZON_LINUX_2"
    """Amazon Linux 2.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.AmazonLinuxImageProps", jsii_struct_bases=[])
class AmazonLinuxImageProps(jsii.compat.TypedDict, total=False):
    """Amazon Linux image properties.

    Stability:
        experimental
    """
    edition: "AmazonLinuxEdition"
    """What edition of Amazon Linux to use.

    Default:
        Standard

    Stability:
        experimental
    """

    generation: "AmazonLinuxGeneration"
    """What generation of Amazon Linux to use.

    Default:
        AmazonLinux

    Stability:
        experimental
    """

    storage: "AmazonLinuxStorage"
    """What storage backed image to use.

    Default:
        GeneralPurpose

    Stability:
        experimental
    """

    userData: "UserData"
    """Initial user data.

    Default:
        - Empty UserData for Linux machines

    Stability:
        experimental
    """

    virtualization: "AmazonLinuxVirt"
    """Virtualization type.

    Default:
        HVM

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ec2.AmazonLinuxStorage")
class AmazonLinuxStorage(enum.Enum):
    """
    Stability:
        experimental
    """
    EBS = "EBS"
    """EBS-backed storage.

    Stability:
        experimental
    """
    GENERAL_PURPOSE = "GENERAL_PURPOSE"
    """General Purpose-based storage (recommended).

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ec2.AmazonLinuxVirt")
class AmazonLinuxVirt(enum.Enum):
    """Virtualization type for Amazon Linux.

    Stability:
        experimental
    """
    HVM = "HVM"
    """HVM virtualization (recommended).

    Stability:
        experimental
    """
    PV = "PV"
    """PV virtualization.

    Stability:
        experimental
    """

class CfnCapacityReservation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnCapacityReservation"):
    """A CloudFormation ``AWS::EC2::CapacityReservation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::CapacityReservation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, availability_zone: str, instance_count: jsii.Number, instance_platform: str, instance_type: str, ebs_optimized: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, end_date: typing.Optional[str]=None, end_date_type: typing.Optional[str]=None, ephemeral_storage: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, instance_match_criteria: typing.Optional[str]=None, tag_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TagSpecificationProperty"]]]]]=None, tenancy: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::CapacityReservation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            availability_zone: ``AWS::EC2::CapacityReservation.AvailabilityZone``.
            instance_count: ``AWS::EC2::CapacityReservation.InstanceCount``.
            instance_platform: ``AWS::EC2::CapacityReservation.InstancePlatform``.
            instance_type: ``AWS::EC2::CapacityReservation.InstanceType``.
            ebs_optimized: ``AWS::EC2::CapacityReservation.EbsOptimized``.
            end_date: ``AWS::EC2::CapacityReservation.EndDate``.
            end_date_type: ``AWS::EC2::CapacityReservation.EndDateType``.
            ephemeral_storage: ``AWS::EC2::CapacityReservation.EphemeralStorage``.
            instance_match_criteria: ``AWS::EC2::CapacityReservation.InstanceMatchCriteria``.
            tag_specifications: ``AWS::EC2::CapacityReservation.TagSpecifications``.
            tenancy: ``AWS::EC2::CapacityReservation.Tenancy``.

        Stability:
            experimental
        """
        props: CfnCapacityReservationProps = {"availabilityZone": availability_zone, "instanceCount": instance_count, "instancePlatform": instance_platform, "instanceType": instance_type}

        if ebs_optimized is not None:
            props["ebsOptimized"] = ebs_optimized

        if end_date is not None:
            props["endDate"] = end_date

        if end_date_type is not None:
            props["endDateType"] = end_date_type

        if ephemeral_storage is not None:
            props["ephemeralStorage"] = ephemeral_storage

        if instance_match_criteria is not None:
            props["instanceMatchCriteria"] = instance_match_criteria

        if tag_specifications is not None:
            props["tagSpecifications"] = tag_specifications

        if tenancy is not None:
            props["tenancy"] = tenancy

        jsii.create(CfnCapacityReservation, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrAvailabilityZone")
    def attr_availability_zone(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            AvailabilityZone
        """
        return jsii.get(self, "attrAvailabilityZone")

    @property
    @jsii.member(jsii_name="attrAvailableInstanceCount")
    def attr_available_instance_count(self) -> jsii.Number:
        """
        Stability:
            stable
        cloudformationAttribute:
            AvailableInstanceCount
        """
        return jsii.get(self, "attrAvailableInstanceCount")

    @property
    @jsii.member(jsii_name="attrInstanceType")
    def attr_instance_type(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            InstanceType
        """
        return jsii.get(self, "attrInstanceType")

    @property
    @jsii.member(jsii_name="attrTenancy")
    def attr_tenancy(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Tenancy
        """
        return jsii.get(self, "attrTenancy")

    @property
    @jsii.member(jsii_name="attrTotalInstanceCount")
    def attr_total_instance_count(self) -> jsii.Number:
        """
        Stability:
            stable
        cloudformationAttribute:
            TotalInstanceCount
        """
        return jsii.get(self, "attrTotalInstanceCount")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> str:
        """``AWS::EC2::CapacityReservation.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-availabilityzone
        Stability:
            stable
        """
        return jsii.get(self, "availabilityZone")

    @availability_zone.setter
    def availability_zone(self, value: str):
        return jsii.set(self, "availabilityZone", value)

    @property
    @jsii.member(jsii_name="instanceCount")
    def instance_count(self) -> jsii.Number:
        """``AWS::EC2::CapacityReservation.InstanceCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-instancecount
        Stability:
            stable
        """
        return jsii.get(self, "instanceCount")

    @instance_count.setter
    def instance_count(self, value: jsii.Number):
        return jsii.set(self, "instanceCount", value)

    @property
    @jsii.member(jsii_name="instancePlatform")
    def instance_platform(self) -> str:
        """``AWS::EC2::CapacityReservation.InstancePlatform``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-instanceplatform
        Stability:
            stable
        """
        return jsii.get(self, "instancePlatform")

    @instance_platform.setter
    def instance_platform(self, value: str):
        return jsii.set(self, "instancePlatform", value)

    @property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> str:
        """``AWS::EC2::CapacityReservation.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-instancetype
        Stability:
            stable
        """
        return jsii.get(self, "instanceType")

    @instance_type.setter
    def instance_type(self, value: str):
        return jsii.set(self, "instanceType", value)

    @property
    @jsii.member(jsii_name="ebsOptimized")
    def ebs_optimized(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::CapacityReservation.EbsOptimized``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-ebsoptimized
        Stability:
            stable
        """
        return jsii.get(self, "ebsOptimized")

    @ebs_optimized.setter
    def ebs_optimized(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "ebsOptimized", value)

    @property
    @jsii.member(jsii_name="endDate")
    def end_date(self) -> typing.Optional[str]:
        """``AWS::EC2::CapacityReservation.EndDate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-enddate
        Stability:
            stable
        """
        return jsii.get(self, "endDate")

    @end_date.setter
    def end_date(self, value: typing.Optional[str]):
        return jsii.set(self, "endDate", value)

    @property
    @jsii.member(jsii_name="endDateType")
    def end_date_type(self) -> typing.Optional[str]:
        """``AWS::EC2::CapacityReservation.EndDateType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-enddatetype
        Stability:
            stable
        """
        return jsii.get(self, "endDateType")

    @end_date_type.setter
    def end_date_type(self, value: typing.Optional[str]):
        return jsii.set(self, "endDateType", value)

    @property
    @jsii.member(jsii_name="ephemeralStorage")
    def ephemeral_storage(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::CapacityReservation.EphemeralStorage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-ephemeralstorage
        Stability:
            stable
        """
        return jsii.get(self, "ephemeralStorage")

    @ephemeral_storage.setter
    def ephemeral_storage(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "ephemeralStorage", value)

    @property
    @jsii.member(jsii_name="instanceMatchCriteria")
    def instance_match_criteria(self) -> typing.Optional[str]:
        """``AWS::EC2::CapacityReservation.InstanceMatchCriteria``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-instancematchcriteria
        Stability:
            stable
        """
        return jsii.get(self, "instanceMatchCriteria")

    @instance_match_criteria.setter
    def instance_match_criteria(self, value: typing.Optional[str]):
        return jsii.set(self, "instanceMatchCriteria", value)

    @property
    @jsii.member(jsii_name="tagSpecifications")
    def tag_specifications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TagSpecificationProperty"]]]]]:
        """``AWS::EC2::CapacityReservation.TagSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-tagspecifications
        Stability:
            stable
        """
        return jsii.get(self, "tagSpecifications")

    @tag_specifications.setter
    def tag_specifications(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TagSpecificationProperty"]]]]]):
        return jsii.set(self, "tagSpecifications", value)

    @property
    @jsii.member(jsii_name="tenancy")
    def tenancy(self) -> typing.Optional[str]:
        """``AWS::EC2::CapacityReservation.Tenancy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-tenancy
        Stability:
            stable
        """
        return jsii.get(self, "tenancy")

    @tenancy.setter
    def tenancy(self, value: typing.Optional[str]):
        return jsii.set(self, "tenancy", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnCapacityReservation.TagSpecificationProperty", jsii_struct_bases=[])
    class TagSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-capacityreservation-tagspecification.html
        Stability:
            stable
        """
        resourceType: str
        """``CfnCapacityReservation.TagSpecificationProperty.ResourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-capacityreservation-tagspecification.html#cfn-ec2-capacityreservation-tagspecification-resourcetype
        Stability:
            stable
        """

        tags: typing.List[aws_cdk.core.CfnTag]
        """``CfnCapacityReservation.TagSpecificationProperty.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-capacityreservation-tagspecification.html#cfn-ec2-capacityreservation-tagspecification-tags
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnCapacityReservationProps(jsii.compat.TypedDict, total=False):
    ebsOptimized: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::CapacityReservation.EbsOptimized``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-ebsoptimized
    Stability:
        stable
    """
    endDate: str
    """``AWS::EC2::CapacityReservation.EndDate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-enddate
    Stability:
        stable
    """
    endDateType: str
    """``AWS::EC2::CapacityReservation.EndDateType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-enddatetype
    Stability:
        stable
    """
    ephemeralStorage: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::CapacityReservation.EphemeralStorage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-ephemeralstorage
    Stability:
        stable
    """
    instanceMatchCriteria: str
    """``AWS::EC2::CapacityReservation.InstanceMatchCriteria``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-instancematchcriteria
    Stability:
        stable
    """
    tagSpecifications: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCapacityReservation.TagSpecificationProperty"]]]
    """``AWS::EC2::CapacityReservation.TagSpecifications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-tagspecifications
    Stability:
        stable
    """
    tenancy: str
    """``AWS::EC2::CapacityReservation.Tenancy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-tenancy
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnCapacityReservationProps", jsii_struct_bases=[_CfnCapacityReservationProps])
class CfnCapacityReservationProps(_CfnCapacityReservationProps):
    """Properties for defining a ``AWS::EC2::CapacityReservation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html
    Stability:
        stable
    """
    availabilityZone: str
    """``AWS::EC2::CapacityReservation.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-availabilityzone
    Stability:
        stable
    """

    instanceCount: jsii.Number
    """``AWS::EC2::CapacityReservation.InstanceCount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-instancecount
    Stability:
        stable
    """

    instancePlatform: str
    """``AWS::EC2::CapacityReservation.InstancePlatform``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-instanceplatform
    Stability:
        stable
    """

    instanceType: str
    """``AWS::EC2::CapacityReservation.InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-instancetype
    Stability:
        stable
    """

class CfnClientVpnAuthorizationRule(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnClientVpnAuthorizationRule"):
    """A CloudFormation ``AWS::EC2::ClientVpnAuthorizationRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnauthorizationrule.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::ClientVpnAuthorizationRule
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, client_vpn_endpoint_id: str, target_network_cidr: str, access_group_id: typing.Optional[str]=None, authorize_all_groups: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::ClientVpnAuthorizationRule``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            client_vpn_endpoint_id: ``AWS::EC2::ClientVpnAuthorizationRule.ClientVpnEndpointId``.
            target_network_cidr: ``AWS::EC2::ClientVpnAuthorizationRule.TargetNetworkCidr``.
            access_group_id: ``AWS::EC2::ClientVpnAuthorizationRule.AccessGroupId``.
            authorize_all_groups: ``AWS::EC2::ClientVpnAuthorizationRule.AuthorizeAllGroups``.
            description: ``AWS::EC2::ClientVpnAuthorizationRule.Description``.

        Stability:
            experimental
        """
        props: CfnClientVpnAuthorizationRuleProps = {"clientVpnEndpointId": client_vpn_endpoint_id, "targetNetworkCidr": target_network_cidr}

        if access_group_id is not None:
            props["accessGroupId"] = access_group_id

        if authorize_all_groups is not None:
            props["authorizeAllGroups"] = authorize_all_groups

        if description is not None:
            props["description"] = description

        jsii.create(CfnClientVpnAuthorizationRule, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="clientVpnEndpointId")
    def client_vpn_endpoint_id(self) -> str:
        """``AWS::EC2::ClientVpnAuthorizationRule.ClientVpnEndpointId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnauthorizationrule.html#cfn-ec2-clientvpnauthorizationrule-clientvpnendpointid
        Stability:
            stable
        """
        return jsii.get(self, "clientVpnEndpointId")

    @client_vpn_endpoint_id.setter
    def client_vpn_endpoint_id(self, value: str):
        return jsii.set(self, "clientVpnEndpointId", value)

    @property
    @jsii.member(jsii_name="targetNetworkCidr")
    def target_network_cidr(self) -> str:
        """``AWS::EC2::ClientVpnAuthorizationRule.TargetNetworkCidr``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnauthorizationrule.html#cfn-ec2-clientvpnauthorizationrule-targetnetworkcidr
        Stability:
            stable
        """
        return jsii.get(self, "targetNetworkCidr")

    @target_network_cidr.setter
    def target_network_cidr(self, value: str):
        return jsii.set(self, "targetNetworkCidr", value)

    @property
    @jsii.member(jsii_name="accessGroupId")
    def access_group_id(self) -> typing.Optional[str]:
        """``AWS::EC2::ClientVpnAuthorizationRule.AccessGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnauthorizationrule.html#cfn-ec2-clientvpnauthorizationrule-accessgroupid
        Stability:
            stable
        """
        return jsii.get(self, "accessGroupId")

    @access_group_id.setter
    def access_group_id(self, value: typing.Optional[str]):
        return jsii.set(self, "accessGroupId", value)

    @property
    @jsii.member(jsii_name="authorizeAllGroups")
    def authorize_all_groups(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::ClientVpnAuthorizationRule.AuthorizeAllGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnauthorizationrule.html#cfn-ec2-clientvpnauthorizationrule-authorizeallgroups
        Stability:
            stable
        """
        return jsii.get(self, "authorizeAllGroups")

    @authorize_all_groups.setter
    def authorize_all_groups(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "authorizeAllGroups", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::EC2::ClientVpnAuthorizationRule.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnauthorizationrule.html#cfn-ec2-clientvpnauthorizationrule-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnClientVpnAuthorizationRuleProps(jsii.compat.TypedDict, total=False):
    accessGroupId: str
    """``AWS::EC2::ClientVpnAuthorizationRule.AccessGroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnauthorizationrule.html#cfn-ec2-clientvpnauthorizationrule-accessgroupid
    Stability:
        stable
    """
    authorizeAllGroups: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::ClientVpnAuthorizationRule.AuthorizeAllGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnauthorizationrule.html#cfn-ec2-clientvpnauthorizationrule-authorizeallgroups
    Stability:
        stable
    """
    description: str
    """``AWS::EC2::ClientVpnAuthorizationRule.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnauthorizationrule.html#cfn-ec2-clientvpnauthorizationrule-description
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnClientVpnAuthorizationRuleProps", jsii_struct_bases=[_CfnClientVpnAuthorizationRuleProps])
class CfnClientVpnAuthorizationRuleProps(_CfnClientVpnAuthorizationRuleProps):
    """Properties for defining a ``AWS::EC2::ClientVpnAuthorizationRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnauthorizationrule.html
    Stability:
        stable
    """
    clientVpnEndpointId: str
    """``AWS::EC2::ClientVpnAuthorizationRule.ClientVpnEndpointId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnauthorizationrule.html#cfn-ec2-clientvpnauthorizationrule-clientvpnendpointid
    Stability:
        stable
    """

    targetNetworkCidr: str
    """``AWS::EC2::ClientVpnAuthorizationRule.TargetNetworkCidr``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnauthorizationrule.html#cfn-ec2-clientvpnauthorizationrule-targetnetworkcidr
    Stability:
        stable
    """

class CfnClientVpnEndpoint(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnClientVpnEndpoint"):
    """A CloudFormation ``AWS::EC2::ClientVpnEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::ClientVpnEndpoint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, authentication_options: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ClientAuthenticationRequestProperty"]]], client_cidr_block: str, connection_log_options: typing.Union[aws_cdk.core.IResolvable, "ConnectionLogOptionsProperty"], server_certificate_arn: str, description: typing.Optional[str]=None, dns_servers: typing.Optional[typing.List[str]]=None, tag_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TagSpecificationProperty"]]]]]=None, transport_protocol: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::ClientVpnEndpoint``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            authentication_options: ``AWS::EC2::ClientVpnEndpoint.AuthenticationOptions``.
            client_cidr_block: ``AWS::EC2::ClientVpnEndpoint.ClientCidrBlock``.
            connection_log_options: ``AWS::EC2::ClientVpnEndpoint.ConnectionLogOptions``.
            server_certificate_arn: ``AWS::EC2::ClientVpnEndpoint.ServerCertificateArn``.
            description: ``AWS::EC2::ClientVpnEndpoint.Description``.
            dns_servers: ``AWS::EC2::ClientVpnEndpoint.DnsServers``.
            tag_specifications: ``AWS::EC2::ClientVpnEndpoint.TagSpecifications``.
            transport_protocol: ``AWS::EC2::ClientVpnEndpoint.TransportProtocol``.

        Stability:
            experimental
        """
        props: CfnClientVpnEndpointProps = {"authenticationOptions": authentication_options, "clientCidrBlock": client_cidr_block, "connectionLogOptions": connection_log_options, "serverCertificateArn": server_certificate_arn}

        if description is not None:
            props["description"] = description

        if dns_servers is not None:
            props["dnsServers"] = dns_servers

        if tag_specifications is not None:
            props["tagSpecifications"] = tag_specifications

        if transport_protocol is not None:
            props["transportProtocol"] = transport_protocol

        jsii.create(CfnClientVpnEndpoint, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="authenticationOptions")
    def authentication_options(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ClientAuthenticationRequestProperty"]]]:
        """``AWS::EC2::ClientVpnEndpoint.AuthenticationOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-authenticationoptions
        Stability:
            stable
        """
        return jsii.get(self, "authenticationOptions")

    @authentication_options.setter
    def authentication_options(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ClientAuthenticationRequestProperty"]]]):
        return jsii.set(self, "authenticationOptions", value)

    @property
    @jsii.member(jsii_name="clientCidrBlock")
    def client_cidr_block(self) -> str:
        """``AWS::EC2::ClientVpnEndpoint.ClientCidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-clientcidrblock
        Stability:
            stable
        """
        return jsii.get(self, "clientCidrBlock")

    @client_cidr_block.setter
    def client_cidr_block(self, value: str):
        return jsii.set(self, "clientCidrBlock", value)

    @property
    @jsii.member(jsii_name="connectionLogOptions")
    def connection_log_options(self) -> typing.Union[aws_cdk.core.IResolvable, "ConnectionLogOptionsProperty"]:
        """``AWS::EC2::ClientVpnEndpoint.ConnectionLogOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-connectionlogoptions
        Stability:
            stable
        """
        return jsii.get(self, "connectionLogOptions")

    @connection_log_options.setter
    def connection_log_options(self, value: typing.Union[aws_cdk.core.IResolvable, "ConnectionLogOptionsProperty"]):
        return jsii.set(self, "connectionLogOptions", value)

    @property
    @jsii.member(jsii_name="serverCertificateArn")
    def server_certificate_arn(self) -> str:
        """``AWS::EC2::ClientVpnEndpoint.ServerCertificateArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-servercertificatearn
        Stability:
            stable
        """
        return jsii.get(self, "serverCertificateArn")

    @server_certificate_arn.setter
    def server_certificate_arn(self, value: str):
        return jsii.set(self, "serverCertificateArn", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::EC2::ClientVpnEndpoint.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="dnsServers")
    def dns_servers(self) -> typing.Optional[typing.List[str]]:
        """``AWS::EC2::ClientVpnEndpoint.DnsServers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-dnsservers
        Stability:
            stable
        """
        return jsii.get(self, "dnsServers")

    @dns_servers.setter
    def dns_servers(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "dnsServers", value)

    @property
    @jsii.member(jsii_name="tagSpecifications")
    def tag_specifications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TagSpecificationProperty"]]]]]:
        """``AWS::EC2::ClientVpnEndpoint.TagSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-tagspecifications
        Stability:
            stable
        """
        return jsii.get(self, "tagSpecifications")

    @tag_specifications.setter
    def tag_specifications(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TagSpecificationProperty"]]]]]):
        return jsii.set(self, "tagSpecifications", value)

    @property
    @jsii.member(jsii_name="transportProtocol")
    def transport_protocol(self) -> typing.Optional[str]:
        """``AWS::EC2::ClientVpnEndpoint.TransportProtocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-transportprotocol
        Stability:
            stable
        """
        return jsii.get(self, "transportProtocol")

    @transport_protocol.setter
    def transport_protocol(self, value: typing.Optional[str]):
        return jsii.set(self, "transportProtocol", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnClientVpnEndpoint.CertificateAuthenticationRequestProperty", jsii_struct_bases=[])
    class CertificateAuthenticationRequestProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-certificateauthenticationrequest.html
        Stability:
            stable
        """
        clientRootCertificateChainArn: str
        """``CfnClientVpnEndpoint.CertificateAuthenticationRequestProperty.ClientRootCertificateChainArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-certificateauthenticationrequest.html#cfn-ec2-clientvpnendpoint-certificateauthenticationrequest-clientrootcertificatechainarn
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ClientAuthenticationRequestProperty(jsii.compat.TypedDict, total=False):
        activeDirectory: typing.Union[aws_cdk.core.IResolvable, "CfnClientVpnEndpoint.DirectoryServiceAuthenticationRequestProperty"]
        """``CfnClientVpnEndpoint.ClientAuthenticationRequestProperty.ActiveDirectory``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-clientauthenticationrequest.html#cfn-ec2-clientvpnendpoint-clientauthenticationrequest-activedirectory
        Stability:
            stable
        """
        mutualAuthentication: typing.Union[aws_cdk.core.IResolvable, "CfnClientVpnEndpoint.CertificateAuthenticationRequestProperty"]
        """``CfnClientVpnEndpoint.ClientAuthenticationRequestProperty.MutualAuthentication``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-clientauthenticationrequest.html#cfn-ec2-clientvpnendpoint-clientauthenticationrequest-mutualauthentication
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnClientVpnEndpoint.ClientAuthenticationRequestProperty", jsii_struct_bases=[_ClientAuthenticationRequestProperty])
    class ClientAuthenticationRequestProperty(_ClientAuthenticationRequestProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-clientauthenticationrequest.html
        Stability:
            stable
        """
        type: str
        """``CfnClientVpnEndpoint.ClientAuthenticationRequestProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-clientauthenticationrequest.html#cfn-ec2-clientvpnendpoint-clientauthenticationrequest-type
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ConnectionLogOptionsProperty(jsii.compat.TypedDict, total=False):
        cloudwatchLogGroup: str
        """``CfnClientVpnEndpoint.ConnectionLogOptionsProperty.CloudwatchLogGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-connectionlogoptions.html#cfn-ec2-clientvpnendpoint-connectionlogoptions-cloudwatchloggroup
        Stability:
            stable
        """
        cloudwatchLogStream: str
        """``CfnClientVpnEndpoint.ConnectionLogOptionsProperty.CloudwatchLogStream``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-connectionlogoptions.html#cfn-ec2-clientvpnendpoint-connectionlogoptions-cloudwatchlogstream
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnClientVpnEndpoint.ConnectionLogOptionsProperty", jsii_struct_bases=[_ConnectionLogOptionsProperty])
    class ConnectionLogOptionsProperty(_ConnectionLogOptionsProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-connectionlogoptions.html
        Stability:
            stable
        """
        enabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnClientVpnEndpoint.ConnectionLogOptionsProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-connectionlogoptions.html#cfn-ec2-clientvpnendpoint-connectionlogoptions-enabled
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnClientVpnEndpoint.DirectoryServiceAuthenticationRequestProperty", jsii_struct_bases=[])
    class DirectoryServiceAuthenticationRequestProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-directoryserviceauthenticationrequest.html
        Stability:
            stable
        """
        directoryId: str
        """``CfnClientVpnEndpoint.DirectoryServiceAuthenticationRequestProperty.DirectoryId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-directoryserviceauthenticationrequest.html#cfn-ec2-clientvpnendpoint-directoryserviceauthenticationrequest-directoryid
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnClientVpnEndpoint.TagSpecificationProperty", jsii_struct_bases=[])
    class TagSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-tagspecification.html
        Stability:
            stable
        """
        resourceType: str
        """``CfnClientVpnEndpoint.TagSpecificationProperty.ResourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-tagspecification.html#cfn-ec2-clientvpnendpoint-tagspecification-resourcetype
        Stability:
            stable
        """

        tags: typing.List[aws_cdk.core.CfnTag]
        """``CfnClientVpnEndpoint.TagSpecificationProperty.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-clientvpnendpoint-tagspecification.html#cfn-ec2-clientvpnendpoint-tagspecification-tags
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnClientVpnEndpointProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::EC2::ClientVpnEndpoint.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-description
    Stability:
        stable
    """
    dnsServers: typing.List[str]
    """``AWS::EC2::ClientVpnEndpoint.DnsServers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-dnsservers
    Stability:
        stable
    """
    tagSpecifications: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnClientVpnEndpoint.TagSpecificationProperty"]]]
    """``AWS::EC2::ClientVpnEndpoint.TagSpecifications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-tagspecifications
    Stability:
        stable
    """
    transportProtocol: str
    """``AWS::EC2::ClientVpnEndpoint.TransportProtocol``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-transportprotocol
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnClientVpnEndpointProps", jsii_struct_bases=[_CfnClientVpnEndpointProps])
class CfnClientVpnEndpointProps(_CfnClientVpnEndpointProps):
    """Properties for defining a ``AWS::EC2::ClientVpnEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html
    Stability:
        stable
    """
    authenticationOptions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnClientVpnEndpoint.ClientAuthenticationRequestProperty"]]]
    """``AWS::EC2::ClientVpnEndpoint.AuthenticationOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-authenticationoptions
    Stability:
        stable
    """

    clientCidrBlock: str
    """``AWS::EC2::ClientVpnEndpoint.ClientCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-clientcidrblock
    Stability:
        stable
    """

    connectionLogOptions: typing.Union[aws_cdk.core.IResolvable, "CfnClientVpnEndpoint.ConnectionLogOptionsProperty"]
    """``AWS::EC2::ClientVpnEndpoint.ConnectionLogOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-connectionlogoptions
    Stability:
        stable
    """

    serverCertificateArn: str
    """``AWS::EC2::ClientVpnEndpoint.ServerCertificateArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnendpoint.html#cfn-ec2-clientvpnendpoint-servercertificatearn
    Stability:
        stable
    """

class CfnClientVpnRoute(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnClientVpnRoute"):
    """A CloudFormation ``AWS::EC2::ClientVpnRoute``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnroute.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::ClientVpnRoute
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, client_vpn_endpoint_id: str, destination_cidr_block: str, target_vpc_subnet_id: str, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::ClientVpnRoute``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            client_vpn_endpoint_id: ``AWS::EC2::ClientVpnRoute.ClientVpnEndpointId``.
            destination_cidr_block: ``AWS::EC2::ClientVpnRoute.DestinationCidrBlock``.
            target_vpc_subnet_id: ``AWS::EC2::ClientVpnRoute.TargetVpcSubnetId``.
            description: ``AWS::EC2::ClientVpnRoute.Description``.

        Stability:
            experimental
        """
        props: CfnClientVpnRouteProps = {"clientVpnEndpointId": client_vpn_endpoint_id, "destinationCidrBlock": destination_cidr_block, "targetVpcSubnetId": target_vpc_subnet_id}

        if description is not None:
            props["description"] = description

        jsii.create(CfnClientVpnRoute, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="clientVpnEndpointId")
    def client_vpn_endpoint_id(self) -> str:
        """``AWS::EC2::ClientVpnRoute.ClientVpnEndpointId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnroute.html#cfn-ec2-clientvpnroute-clientvpnendpointid
        Stability:
            stable
        """
        return jsii.get(self, "clientVpnEndpointId")

    @client_vpn_endpoint_id.setter
    def client_vpn_endpoint_id(self, value: str):
        return jsii.set(self, "clientVpnEndpointId", value)

    @property
    @jsii.member(jsii_name="destinationCidrBlock")
    def destination_cidr_block(self) -> str:
        """``AWS::EC2::ClientVpnRoute.DestinationCidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnroute.html#cfn-ec2-clientvpnroute-destinationcidrblock
        Stability:
            stable
        """
        return jsii.get(self, "destinationCidrBlock")

    @destination_cidr_block.setter
    def destination_cidr_block(self, value: str):
        return jsii.set(self, "destinationCidrBlock", value)

    @property
    @jsii.member(jsii_name="targetVpcSubnetId")
    def target_vpc_subnet_id(self) -> str:
        """``AWS::EC2::ClientVpnRoute.TargetVpcSubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnroute.html#cfn-ec2-clientvpnroute-targetvpcsubnetid
        Stability:
            stable
        """
        return jsii.get(self, "targetVpcSubnetId")

    @target_vpc_subnet_id.setter
    def target_vpc_subnet_id(self, value: str):
        return jsii.set(self, "targetVpcSubnetId", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::EC2::ClientVpnRoute.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnroute.html#cfn-ec2-clientvpnroute-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnClientVpnRouteProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::EC2::ClientVpnRoute.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnroute.html#cfn-ec2-clientvpnroute-description
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnClientVpnRouteProps", jsii_struct_bases=[_CfnClientVpnRouteProps])
class CfnClientVpnRouteProps(_CfnClientVpnRouteProps):
    """Properties for defining a ``AWS::EC2::ClientVpnRoute``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnroute.html
    Stability:
        stable
    """
    clientVpnEndpointId: str
    """``AWS::EC2::ClientVpnRoute.ClientVpnEndpointId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnroute.html#cfn-ec2-clientvpnroute-clientvpnendpointid
    Stability:
        stable
    """

    destinationCidrBlock: str
    """``AWS::EC2::ClientVpnRoute.DestinationCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnroute.html#cfn-ec2-clientvpnroute-destinationcidrblock
    Stability:
        stable
    """

    targetVpcSubnetId: str
    """``AWS::EC2::ClientVpnRoute.TargetVpcSubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpnroute.html#cfn-ec2-clientvpnroute-targetvpcsubnetid
    Stability:
        stable
    """

class CfnClientVpnTargetNetworkAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnClientVpnTargetNetworkAssociation"):
    """A CloudFormation ``AWS::EC2::ClientVpnTargetNetworkAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpntargetnetworkassociation.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::ClientVpnTargetNetworkAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, client_vpn_endpoint_id: str, subnet_id: str) -> None:
        """Create a new ``AWS::EC2::ClientVpnTargetNetworkAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            client_vpn_endpoint_id: ``AWS::EC2::ClientVpnTargetNetworkAssociation.ClientVpnEndpointId``.
            subnet_id: ``AWS::EC2::ClientVpnTargetNetworkAssociation.SubnetId``.

        Stability:
            experimental
        """
        props: CfnClientVpnTargetNetworkAssociationProps = {"clientVpnEndpointId": client_vpn_endpoint_id, "subnetId": subnet_id}

        jsii.create(CfnClientVpnTargetNetworkAssociation, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="clientVpnEndpointId")
    def client_vpn_endpoint_id(self) -> str:
        """``AWS::EC2::ClientVpnTargetNetworkAssociation.ClientVpnEndpointId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpntargetnetworkassociation.html#cfn-ec2-clientvpntargetnetworkassociation-clientvpnendpointid
        Stability:
            stable
        """
        return jsii.get(self, "clientVpnEndpointId")

    @client_vpn_endpoint_id.setter
    def client_vpn_endpoint_id(self, value: str):
        return jsii.set(self, "clientVpnEndpointId", value)

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        """``AWS::EC2::ClientVpnTargetNetworkAssociation.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpntargetnetworkassociation.html#cfn-ec2-clientvpntargetnetworkassociation-subnetid
        Stability:
            stable
        """
        return jsii.get(self, "subnetId")

    @subnet_id.setter
    def subnet_id(self, value: str):
        return jsii.set(self, "subnetId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnClientVpnTargetNetworkAssociationProps", jsii_struct_bases=[])
class CfnClientVpnTargetNetworkAssociationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::ClientVpnTargetNetworkAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpntargetnetworkassociation.html
    Stability:
        stable
    """
    clientVpnEndpointId: str
    """``AWS::EC2::ClientVpnTargetNetworkAssociation.ClientVpnEndpointId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpntargetnetworkassociation.html#cfn-ec2-clientvpntargetnetworkassociation-clientvpnendpointid
    Stability:
        stable
    """

    subnetId: str
    """``AWS::EC2::ClientVpnTargetNetworkAssociation.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-clientvpntargetnetworkassociation.html#cfn-ec2-clientvpntargetnetworkassociation-subnetid
    Stability:
        stable
    """

class CfnCustomerGateway(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnCustomerGateway"):
    """A CloudFormation ``AWS::EC2::CustomerGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::CustomerGateway
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, bgp_asn: jsii.Number, ip_address: str, type: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::CustomerGateway``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            bgp_asn: ``AWS::EC2::CustomerGateway.BgpAsn``.
            ip_address: ``AWS::EC2::CustomerGateway.IpAddress``.
            type: ``AWS::EC2::CustomerGateway.Type``.
            tags: ``AWS::EC2::CustomerGateway.Tags``.

        Stability:
            experimental
        """
        props: CfnCustomerGatewayProps = {"bgpAsn": bgp_asn, "ipAddress": ip_address, "type": type}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnCustomerGateway, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::CustomerGateway.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html#cfn-ec2-customergateway-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="bgpAsn")
    def bgp_asn(self) -> jsii.Number:
        """``AWS::EC2::CustomerGateway.BgpAsn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html#cfn-ec2-customergateway-bgpasn
        Stability:
            stable
        """
        return jsii.get(self, "bgpAsn")

    @bgp_asn.setter
    def bgp_asn(self, value: jsii.Number):
        return jsii.set(self, "bgpAsn", value)

    @property
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> str:
        """``AWS::EC2::CustomerGateway.IpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html#cfn-ec2-customergateway-ipaddress
        Stability:
            stable
        """
        return jsii.get(self, "ipAddress")

    @ip_address.setter
    def ip_address(self, value: str):
        return jsii.set(self, "ipAddress", value)

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """``AWS::EC2::CustomerGateway.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html#cfn-ec2-customergateway-type
        Stability:
            stable
        """
        return jsii.get(self, "type")

    @type.setter
    def type(self, value: str):
        return jsii.set(self, "type", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnCustomerGatewayProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::CustomerGateway.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html#cfn-ec2-customergateway-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnCustomerGatewayProps", jsii_struct_bases=[_CfnCustomerGatewayProps])
class CfnCustomerGatewayProps(_CfnCustomerGatewayProps):
    """Properties for defining a ``AWS::EC2::CustomerGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html
    Stability:
        stable
    """
    bgpAsn: jsii.Number
    """``AWS::EC2::CustomerGateway.BgpAsn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html#cfn-ec2-customergateway-bgpasn
    Stability:
        stable
    """

    ipAddress: str
    """``AWS::EC2::CustomerGateway.IpAddress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html#cfn-ec2-customergateway-ipaddress
    Stability:
        stable
    """

    type: str
    """``AWS::EC2::CustomerGateway.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html#cfn-ec2-customergateway-type
    Stability:
        stable
    """

class CfnDHCPOptions(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnDHCPOptions"):
    """A CloudFormation ``AWS::EC2::DHCPOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::DHCPOptions
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, domain_name: typing.Optional[str]=None, domain_name_servers: typing.Optional[typing.List[str]]=None, netbios_name_servers: typing.Optional[typing.List[str]]=None, netbios_node_type: typing.Optional[jsii.Number]=None, ntp_servers: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::DHCPOptions``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            domain_name: ``AWS::EC2::DHCPOptions.DomainName``.
            domain_name_servers: ``AWS::EC2::DHCPOptions.DomainNameServers``.
            netbios_name_servers: ``AWS::EC2::DHCPOptions.NetbiosNameServers``.
            netbios_node_type: ``AWS::EC2::DHCPOptions.NetbiosNodeType``.
            ntp_servers: ``AWS::EC2::DHCPOptions.NtpServers``.
            tags: ``AWS::EC2::DHCPOptions.Tags``.

        Stability:
            experimental
        """
        props: CfnDHCPOptionsProps = {}

        if domain_name is not None:
            props["domainName"] = domain_name

        if domain_name_servers is not None:
            props["domainNameServers"] = domain_name_servers

        if netbios_name_servers is not None:
            props["netbiosNameServers"] = netbios_name_servers

        if netbios_node_type is not None:
            props["netbiosNodeType"] = netbios_node_type

        if ntp_servers is not None:
            props["ntpServers"] = ntp_servers

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnDHCPOptions, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::DHCPOptions.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> typing.Optional[str]:
        """``AWS::EC2::DHCPOptions.DomainName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-domainname
        Stability:
            stable
        """
        return jsii.get(self, "domainName")

    @domain_name.setter
    def domain_name(self, value: typing.Optional[str]):
        return jsii.set(self, "domainName", value)

    @property
    @jsii.member(jsii_name="domainNameServers")
    def domain_name_servers(self) -> typing.Optional[typing.List[str]]:
        """``AWS::EC2::DHCPOptions.DomainNameServers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-domainnameservers
        Stability:
            stable
        """
        return jsii.get(self, "domainNameServers")

    @domain_name_servers.setter
    def domain_name_servers(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "domainNameServers", value)

    @property
    @jsii.member(jsii_name="netbiosNameServers")
    def netbios_name_servers(self) -> typing.Optional[typing.List[str]]:
        """``AWS::EC2::DHCPOptions.NetbiosNameServers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-netbiosnameservers
        Stability:
            stable
        """
        return jsii.get(self, "netbiosNameServers")

    @netbios_name_servers.setter
    def netbios_name_servers(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "netbiosNameServers", value)

    @property
    @jsii.member(jsii_name="netbiosNodeType")
    def netbios_node_type(self) -> typing.Optional[jsii.Number]:
        """``AWS::EC2::DHCPOptions.NetbiosNodeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-netbiosnodetype
        Stability:
            stable
        """
        return jsii.get(self, "netbiosNodeType")

    @netbios_node_type.setter
    def netbios_node_type(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "netbiosNodeType", value)

    @property
    @jsii.member(jsii_name="ntpServers")
    def ntp_servers(self) -> typing.Optional[typing.List[str]]:
        """``AWS::EC2::DHCPOptions.NtpServers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-ntpservers
        Stability:
            stable
        """
        return jsii.get(self, "ntpServers")

    @ntp_servers.setter
    def ntp_servers(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "ntpServers", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnDHCPOptionsProps", jsii_struct_bases=[])
class CfnDHCPOptionsProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::DHCPOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html
    Stability:
        stable
    """
    domainName: str
    """``AWS::EC2::DHCPOptions.DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-domainname
    Stability:
        stable
    """

    domainNameServers: typing.List[str]
    """``AWS::EC2::DHCPOptions.DomainNameServers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-domainnameservers
    Stability:
        stable
    """

    netbiosNameServers: typing.List[str]
    """``AWS::EC2::DHCPOptions.NetbiosNameServers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-netbiosnameservers
    Stability:
        stable
    """

    netbiosNodeType: jsii.Number
    """``AWS::EC2::DHCPOptions.NetbiosNodeType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-netbiosnodetype
    Stability:
        stable
    """

    ntpServers: typing.List[str]
    """``AWS::EC2::DHCPOptions.NtpServers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-ntpservers
    Stability:
        stable
    """

    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::DHCPOptions.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-tags
    Stability:
        stable
    """

class CfnEC2Fleet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet"):
    """A CloudFormation ``AWS::EC2::EC2Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::EC2Fleet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, launch_template_configs: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "FleetLaunchTemplateConfigRequestProperty"]]], target_capacity_specification: typing.Union[aws_cdk.core.IResolvable, "TargetCapacitySpecificationRequestProperty"], excess_capacity_termination_policy: typing.Optional[str]=None, on_demand_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["OnDemandOptionsRequestProperty"]]]=None, replace_unhealthy_instances: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, spot_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SpotOptionsRequestProperty"]]]=None, tag_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TagSpecificationProperty"]]]]]=None, terminate_instances_with_expiration: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, type: typing.Optional[str]=None, valid_from: typing.Optional[str]=None, valid_until: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::EC2Fleet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            launch_template_configs: ``AWS::EC2::EC2Fleet.LaunchTemplateConfigs``.
            target_capacity_specification: ``AWS::EC2::EC2Fleet.TargetCapacitySpecification``.
            excess_capacity_termination_policy: ``AWS::EC2::EC2Fleet.ExcessCapacityTerminationPolicy``.
            on_demand_options: ``AWS::EC2::EC2Fleet.OnDemandOptions``.
            replace_unhealthy_instances: ``AWS::EC2::EC2Fleet.ReplaceUnhealthyInstances``.
            spot_options: ``AWS::EC2::EC2Fleet.SpotOptions``.
            tag_specifications: ``AWS::EC2::EC2Fleet.TagSpecifications``.
            terminate_instances_with_expiration: ``AWS::EC2::EC2Fleet.TerminateInstancesWithExpiration``.
            type: ``AWS::EC2::EC2Fleet.Type``.
            valid_from: ``AWS::EC2::EC2Fleet.ValidFrom``.
            valid_until: ``AWS::EC2::EC2Fleet.ValidUntil``.

        Stability:
            experimental
        """
        props: CfnEC2FleetProps = {"launchTemplateConfigs": launch_template_configs, "targetCapacitySpecification": target_capacity_specification}

        if excess_capacity_termination_policy is not None:
            props["excessCapacityTerminationPolicy"] = excess_capacity_termination_policy

        if on_demand_options is not None:
            props["onDemandOptions"] = on_demand_options

        if replace_unhealthy_instances is not None:
            props["replaceUnhealthyInstances"] = replace_unhealthy_instances

        if spot_options is not None:
            props["spotOptions"] = spot_options

        if tag_specifications is not None:
            props["tagSpecifications"] = tag_specifications

        if terminate_instances_with_expiration is not None:
            props["terminateInstancesWithExpiration"] = terminate_instances_with_expiration

        if type is not None:
            props["type"] = type

        if valid_from is not None:
            props["validFrom"] = valid_from

        if valid_until is not None:
            props["validUntil"] = valid_until

        jsii.create(CfnEC2Fleet, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="launchTemplateConfigs")
    def launch_template_configs(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "FleetLaunchTemplateConfigRequestProperty"]]]:
        """``AWS::EC2::EC2Fleet.LaunchTemplateConfigs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-launchtemplateconfigs
        Stability:
            stable
        """
        return jsii.get(self, "launchTemplateConfigs")

    @launch_template_configs.setter
    def launch_template_configs(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "FleetLaunchTemplateConfigRequestProperty"]]]):
        return jsii.set(self, "launchTemplateConfigs", value)

    @property
    @jsii.member(jsii_name="targetCapacitySpecification")
    def target_capacity_specification(self) -> typing.Union[aws_cdk.core.IResolvable, "TargetCapacitySpecificationRequestProperty"]:
        """``AWS::EC2::EC2Fleet.TargetCapacitySpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-targetcapacityspecification
        Stability:
            stable
        """
        return jsii.get(self, "targetCapacitySpecification")

    @target_capacity_specification.setter
    def target_capacity_specification(self, value: typing.Union[aws_cdk.core.IResolvable, "TargetCapacitySpecificationRequestProperty"]):
        return jsii.set(self, "targetCapacitySpecification", value)

    @property
    @jsii.member(jsii_name="excessCapacityTerminationPolicy")
    def excess_capacity_termination_policy(self) -> typing.Optional[str]:
        """``AWS::EC2::EC2Fleet.ExcessCapacityTerminationPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-excesscapacityterminationpolicy
        Stability:
            stable
        """
        return jsii.get(self, "excessCapacityTerminationPolicy")

    @excess_capacity_termination_policy.setter
    def excess_capacity_termination_policy(self, value: typing.Optional[str]):
        return jsii.set(self, "excessCapacityTerminationPolicy", value)

    @property
    @jsii.member(jsii_name="onDemandOptions")
    def on_demand_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["OnDemandOptionsRequestProperty"]]]:
        """``AWS::EC2::EC2Fleet.OnDemandOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-ondemandoptions
        Stability:
            stable
        """
        return jsii.get(self, "onDemandOptions")

    @on_demand_options.setter
    def on_demand_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["OnDemandOptionsRequestProperty"]]]):
        return jsii.set(self, "onDemandOptions", value)

    @property
    @jsii.member(jsii_name="replaceUnhealthyInstances")
    def replace_unhealthy_instances(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::EC2Fleet.ReplaceUnhealthyInstances``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-replaceunhealthyinstances
        Stability:
            stable
        """
        return jsii.get(self, "replaceUnhealthyInstances")

    @replace_unhealthy_instances.setter
    def replace_unhealthy_instances(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "replaceUnhealthyInstances", value)

    @property
    @jsii.member(jsii_name="spotOptions")
    def spot_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SpotOptionsRequestProperty"]]]:
        """``AWS::EC2::EC2Fleet.SpotOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-spotoptions
        Stability:
            stable
        """
        return jsii.get(self, "spotOptions")

    @spot_options.setter
    def spot_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SpotOptionsRequestProperty"]]]):
        return jsii.set(self, "spotOptions", value)

    @property
    @jsii.member(jsii_name="tagSpecifications")
    def tag_specifications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TagSpecificationProperty"]]]]]:
        """``AWS::EC2::EC2Fleet.TagSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-tagspecifications
        Stability:
            stable
        """
        return jsii.get(self, "tagSpecifications")

    @tag_specifications.setter
    def tag_specifications(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TagSpecificationProperty"]]]]]):
        return jsii.set(self, "tagSpecifications", value)

    @property
    @jsii.member(jsii_name="terminateInstancesWithExpiration")
    def terminate_instances_with_expiration(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::EC2Fleet.TerminateInstancesWithExpiration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-terminateinstanceswithexpiration
        Stability:
            stable
        """
        return jsii.get(self, "terminateInstancesWithExpiration")

    @terminate_instances_with_expiration.setter
    def terminate_instances_with_expiration(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "terminateInstancesWithExpiration", value)

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> typing.Optional[str]:
        """``AWS::EC2::EC2Fleet.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-type
        Stability:
            stable
        """
        return jsii.get(self, "type")

    @type.setter
    def type(self, value: typing.Optional[str]):
        return jsii.set(self, "type", value)

    @property
    @jsii.member(jsii_name="validFrom")
    def valid_from(self) -> typing.Optional[str]:
        """``AWS::EC2::EC2Fleet.ValidFrom``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-validfrom
        Stability:
            stable
        """
        return jsii.get(self, "validFrom")

    @valid_from.setter
    def valid_from(self, value: typing.Optional[str]):
        return jsii.set(self, "validFrom", value)

    @property
    @jsii.member(jsii_name="validUntil")
    def valid_until(self) -> typing.Optional[str]:
        """``AWS::EC2::EC2Fleet.ValidUntil``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-validuntil
        Stability:
            stable
        """
        return jsii.get(self, "validUntil")

    @valid_until.setter
    def valid_until(self, value: typing.Optional[str]):
        return jsii.set(self, "validUntil", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.FleetLaunchTemplateConfigRequestProperty", jsii_struct_bases=[])
    class FleetLaunchTemplateConfigRequestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateconfigrequest.html
        Stability:
            stable
        """
        launchTemplateSpecification: typing.Union[aws_cdk.core.IResolvable, "CfnEC2Fleet.FleetLaunchTemplateSpecificationRequestProperty"]
        """``CfnEC2Fleet.FleetLaunchTemplateConfigRequestProperty.LaunchTemplateSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateconfigrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateconfigrequest-launchtemplatespecification
        Stability:
            stable
        """

        overrides: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty"]]]
        """``CfnEC2Fleet.FleetLaunchTemplateConfigRequestProperty.Overrides``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateconfigrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateconfigrequest-overrides
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty", jsii_struct_bases=[])
    class FleetLaunchTemplateOverridesRequestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html
        Stability:
            stable
        """
        availabilityZone: str
        """``CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest-availabilityzone
        Stability:
            stable
        """

        instanceType: str
        """``CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest-instancetype
        Stability:
            stable
        """

        maxPrice: str
        """``CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty.MaxPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest-maxprice
        Stability:
            stable
        """

        priority: jsii.Number
        """``CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty.Priority``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest-priority
        Stability:
            stable
        """

        subnetId: str
        """``CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest-subnetid
        Stability:
            stable
        """

        weightedCapacity: jsii.Number
        """``CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty.WeightedCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest-weightedcapacity
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.FleetLaunchTemplateSpecificationRequestProperty", jsii_struct_bases=[])
    class FleetLaunchTemplateSpecificationRequestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest.html
        Stability:
            stable
        """
        launchTemplateId: str
        """``CfnEC2Fleet.FleetLaunchTemplateSpecificationRequestProperty.LaunchTemplateId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest-launchtemplateid
        Stability:
            stable
        """

        launchTemplateName: str
        """``CfnEC2Fleet.FleetLaunchTemplateSpecificationRequestProperty.LaunchTemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest-launchtemplatename
        Stability:
            stable
        """

        version: str
        """``CfnEC2Fleet.FleetLaunchTemplateSpecificationRequestProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest-version
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.OnDemandOptionsRequestProperty", jsii_struct_bases=[])
    class OnDemandOptionsRequestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-ondemandoptionsrequest.html
        Stability:
            stable
        """
        allocationStrategy: str
        """``CfnEC2Fleet.OnDemandOptionsRequestProperty.AllocationStrategy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-ondemandoptionsrequest.html#cfn-ec2-ec2fleet-ondemandoptionsrequest-allocationstrategy
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.SpotOptionsRequestProperty", jsii_struct_bases=[])
    class SpotOptionsRequestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-spotoptionsrequest.html
        Stability:
            stable
        """
        allocationStrategy: str
        """``CfnEC2Fleet.SpotOptionsRequestProperty.AllocationStrategy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-spotoptionsrequest.html#cfn-ec2-ec2fleet-spotoptionsrequest-allocationstrategy
        Stability:
            stable
        """

        instanceInterruptionBehavior: str
        """``CfnEC2Fleet.SpotOptionsRequestProperty.InstanceInterruptionBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-spotoptionsrequest.html#cfn-ec2-ec2fleet-spotoptionsrequest-instanceinterruptionbehavior
        Stability:
            stable
        """

        instancePoolsToUseCount: jsii.Number
        """``CfnEC2Fleet.SpotOptionsRequestProperty.InstancePoolsToUseCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-spotoptionsrequest.html#cfn-ec2-ec2fleet-spotoptionsrequest-instancepoolstousecount
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.TagRequestProperty", jsii_struct_bases=[])
    class TagRequestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-tagrequest.html
        Stability:
            stable
        """
        key: str
        """``CfnEC2Fleet.TagRequestProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-tagrequest.html#cfn-ec2-ec2fleet-tagrequest-key
        Stability:
            stable
        """

        value: str
        """``CfnEC2Fleet.TagRequestProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-tagrequest.html#cfn-ec2-ec2fleet-tagrequest-value
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.TagSpecificationProperty", jsii_struct_bases=[])
    class TagSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-tagspecification.html
        Stability:
            stable
        """
        resourceType: str
        """``CfnEC2Fleet.TagSpecificationProperty.ResourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-tagspecification.html#cfn-ec2-ec2fleet-tagspecification-resourcetype
        Stability:
            stable
        """

        tags: typing.List["CfnEC2Fleet.TagRequestProperty"]
        """``CfnEC2Fleet.TagSpecificationProperty.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-tagspecification.html#cfn-ec2-ec2fleet-tagspecification-tags
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _TargetCapacitySpecificationRequestProperty(jsii.compat.TypedDict, total=False):
        defaultTargetCapacityType: str
        """``CfnEC2Fleet.TargetCapacitySpecificationRequestProperty.DefaultTargetCapacityType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-targetcapacityspecificationrequest.html#cfn-ec2-ec2fleet-targetcapacityspecificationrequest-defaulttargetcapacitytype
        Stability:
            stable
        """
        onDemandTargetCapacity: jsii.Number
        """``CfnEC2Fleet.TargetCapacitySpecificationRequestProperty.OnDemandTargetCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-targetcapacityspecificationrequest.html#cfn-ec2-ec2fleet-targetcapacityspecificationrequest-ondemandtargetcapacity
        Stability:
            stable
        """
        spotTargetCapacity: jsii.Number
        """``CfnEC2Fleet.TargetCapacitySpecificationRequestProperty.SpotTargetCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-targetcapacityspecificationrequest.html#cfn-ec2-ec2fleet-targetcapacityspecificationrequest-spottargetcapacity
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.TargetCapacitySpecificationRequestProperty", jsii_struct_bases=[_TargetCapacitySpecificationRequestProperty])
    class TargetCapacitySpecificationRequestProperty(_TargetCapacitySpecificationRequestProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-targetcapacityspecificationrequest.html
        Stability:
            stable
        """
        totalTargetCapacity: jsii.Number
        """``CfnEC2Fleet.TargetCapacitySpecificationRequestProperty.TotalTargetCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-targetcapacityspecificationrequest.html#cfn-ec2-ec2fleet-targetcapacityspecificationrequest-totaltargetcapacity
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEC2FleetProps(jsii.compat.TypedDict, total=False):
    excessCapacityTerminationPolicy: str
    """``AWS::EC2::EC2Fleet.ExcessCapacityTerminationPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-excesscapacityterminationpolicy
    Stability:
        stable
    """
    onDemandOptions: typing.Union[aws_cdk.core.IResolvable, "CfnEC2Fleet.OnDemandOptionsRequestProperty"]
    """``AWS::EC2::EC2Fleet.OnDemandOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-ondemandoptions
    Stability:
        stable
    """
    replaceUnhealthyInstances: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::EC2Fleet.ReplaceUnhealthyInstances``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-replaceunhealthyinstances
    Stability:
        stable
    """
    spotOptions: typing.Union[aws_cdk.core.IResolvable, "CfnEC2Fleet.SpotOptionsRequestProperty"]
    """``AWS::EC2::EC2Fleet.SpotOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-spotoptions
    Stability:
        stable
    """
    tagSpecifications: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnEC2Fleet.TagSpecificationProperty"]]]
    """``AWS::EC2::EC2Fleet.TagSpecifications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-tagspecifications
    Stability:
        stable
    """
    terminateInstancesWithExpiration: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::EC2Fleet.TerminateInstancesWithExpiration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-terminateinstanceswithexpiration
    Stability:
        stable
    """
    type: str
    """``AWS::EC2::EC2Fleet.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-type
    Stability:
        stable
    """
    validFrom: str
    """``AWS::EC2::EC2Fleet.ValidFrom``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-validfrom
    Stability:
        stable
    """
    validUntil: str
    """``AWS::EC2::EC2Fleet.ValidUntil``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-validuntil
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2FleetProps", jsii_struct_bases=[_CfnEC2FleetProps])
class CfnEC2FleetProps(_CfnEC2FleetProps):
    """Properties for defining a ``AWS::EC2::EC2Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html
    Stability:
        stable
    """
    launchTemplateConfigs: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnEC2Fleet.FleetLaunchTemplateConfigRequestProperty"]]]
    """``AWS::EC2::EC2Fleet.LaunchTemplateConfigs``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-launchtemplateconfigs
    Stability:
        stable
    """

    targetCapacitySpecification: typing.Union[aws_cdk.core.IResolvable, "CfnEC2Fleet.TargetCapacitySpecificationRequestProperty"]
    """``AWS::EC2::EC2Fleet.TargetCapacitySpecification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-targetcapacityspecification
    Stability:
        stable
    """

class CfnEIP(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnEIP"):
    """A CloudFormation ``AWS::EC2::EIP``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::EIP
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, domain: typing.Optional[str]=None, instance_id: typing.Optional[str]=None, public_ipv4_pool: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::EIP``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            domain: ``AWS::EC2::EIP.Domain``.
            instance_id: ``AWS::EC2::EIP.InstanceId``.
            public_ipv4_pool: ``AWS::EC2::EIP.PublicIpv4Pool``.

        Stability:
            experimental
        """
        props: CfnEIPProps = {}

        if domain is not None:
            props["domain"] = domain

        if instance_id is not None:
            props["instanceId"] = instance_id

        if public_ipv4_pool is not None:
            props["publicIpv4Pool"] = public_ipv4_pool

        jsii.create(CfnEIP, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrAllocationId")
    def attr_allocation_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            AllocationId
        """
        return jsii.get(self, "attrAllocationId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="domain")
    def domain(self) -> typing.Optional[str]:
        """``AWS::EC2::EIP.Domain``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html#cfn-ec2-eip-domain
        Stability:
            stable
        """
        return jsii.get(self, "domain")

    @domain.setter
    def domain(self, value: typing.Optional[str]):
        return jsii.set(self, "domain", value)

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> typing.Optional[str]:
        """``AWS::EC2::EIP.InstanceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html#cfn-ec2-eip-instanceid
        Stability:
            stable
        """
        return jsii.get(self, "instanceId")

    @instance_id.setter
    def instance_id(self, value: typing.Optional[str]):
        return jsii.set(self, "instanceId", value)

    @property
    @jsii.member(jsii_name="publicIpv4Pool")
    def public_ipv4_pool(self) -> typing.Optional[str]:
        """``AWS::EC2::EIP.PublicIpv4Pool``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html#cfn-ec2-eip-publicipv4pool
        Stability:
            stable
        """
        return jsii.get(self, "publicIpv4Pool")

    @public_ipv4_pool.setter
    def public_ipv4_pool(self, value: typing.Optional[str]):
        return jsii.set(self, "publicIpv4Pool", value)


class CfnEIPAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnEIPAssociation"):
    """A CloudFormation ``AWS::EC2::EIPAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::EIPAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, allocation_id: typing.Optional[str]=None, eip: typing.Optional[str]=None, instance_id: typing.Optional[str]=None, network_interface_id: typing.Optional[str]=None, private_ip_address: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::EIPAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            allocation_id: ``AWS::EC2::EIPAssociation.AllocationId``.
            eip: ``AWS::EC2::EIPAssociation.EIP``.
            instance_id: ``AWS::EC2::EIPAssociation.InstanceId``.
            network_interface_id: ``AWS::EC2::EIPAssociation.NetworkInterfaceId``.
            private_ip_address: ``AWS::EC2::EIPAssociation.PrivateIpAddress``.

        Stability:
            experimental
        """
        props: CfnEIPAssociationProps = {}

        if allocation_id is not None:
            props["allocationId"] = allocation_id

        if eip is not None:
            props["eip"] = eip

        if instance_id is not None:
            props["instanceId"] = instance_id

        if network_interface_id is not None:
            props["networkInterfaceId"] = network_interface_id

        if private_ip_address is not None:
            props["privateIpAddress"] = private_ip_address

        jsii.create(CfnEIPAssociation, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="allocationId")
    def allocation_id(self) -> typing.Optional[str]:
        """``AWS::EC2::EIPAssociation.AllocationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-allocationid
        Stability:
            stable
        """
        return jsii.get(self, "allocationId")

    @allocation_id.setter
    def allocation_id(self, value: typing.Optional[str]):
        return jsii.set(self, "allocationId", value)

    @property
    @jsii.member(jsii_name="eip")
    def eip(self) -> typing.Optional[str]:
        """``AWS::EC2::EIPAssociation.EIP``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-eip
        Stability:
            stable
        """
        return jsii.get(self, "eip")

    @eip.setter
    def eip(self, value: typing.Optional[str]):
        return jsii.set(self, "eip", value)

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> typing.Optional[str]:
        """``AWS::EC2::EIPAssociation.InstanceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-instanceid
        Stability:
            stable
        """
        return jsii.get(self, "instanceId")

    @instance_id.setter
    def instance_id(self, value: typing.Optional[str]):
        return jsii.set(self, "instanceId", value)

    @property
    @jsii.member(jsii_name="networkInterfaceId")
    def network_interface_id(self) -> typing.Optional[str]:
        """``AWS::EC2::EIPAssociation.NetworkInterfaceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-networkinterfaceid
        Stability:
            stable
        """
        return jsii.get(self, "networkInterfaceId")

    @network_interface_id.setter
    def network_interface_id(self, value: typing.Optional[str]):
        return jsii.set(self, "networkInterfaceId", value)

    @property
    @jsii.member(jsii_name="privateIpAddress")
    def private_ip_address(self) -> typing.Optional[str]:
        """``AWS::EC2::EIPAssociation.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-PrivateIpAddress
        Stability:
            stable
        """
        return jsii.get(self, "privateIpAddress")

    @private_ip_address.setter
    def private_ip_address(self, value: typing.Optional[str]):
        return jsii.set(self, "privateIpAddress", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEIPAssociationProps", jsii_struct_bases=[])
class CfnEIPAssociationProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::EIPAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html
    Stability:
        stable
    """
    allocationId: str
    """``AWS::EC2::EIPAssociation.AllocationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-allocationid
    Stability:
        stable
    """

    eip: str
    """``AWS::EC2::EIPAssociation.EIP``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-eip
    Stability:
        stable
    """

    instanceId: str
    """``AWS::EC2::EIPAssociation.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-instanceid
    Stability:
        stable
    """

    networkInterfaceId: str
    """``AWS::EC2::EIPAssociation.NetworkInterfaceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-networkinterfaceid
    Stability:
        stable
    """

    privateIpAddress: str
    """``AWS::EC2::EIPAssociation.PrivateIpAddress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-PrivateIpAddress
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEIPProps", jsii_struct_bases=[])
class CfnEIPProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::EIP``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html
    Stability:
        stable
    """
    domain: str
    """``AWS::EC2::EIP.Domain``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html#cfn-ec2-eip-domain
    Stability:
        stable
    """

    instanceId: str
    """``AWS::EC2::EIP.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html#cfn-ec2-eip-instanceid
    Stability:
        stable
    """

    publicIpv4Pool: str
    """``AWS::EC2::EIP.PublicIpv4Pool``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html#cfn-ec2-eip-publicipv4pool
    Stability:
        stable
    """

class CfnEgressOnlyInternetGateway(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnEgressOnlyInternetGateway"):
    """A CloudFormation ``AWS::EC2::EgressOnlyInternetGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-egressonlyinternetgateway.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::EgressOnlyInternetGateway
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, vpc_id: str) -> None:
        """Create a new ``AWS::EC2::EgressOnlyInternetGateway``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            vpc_id: ``AWS::EC2::EgressOnlyInternetGateway.VpcId``.

        Stability:
            experimental
        """
        props: CfnEgressOnlyInternetGatewayProps = {"vpcId": vpc_id}

        jsii.create(CfnEgressOnlyInternetGateway, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """``AWS::EC2::EgressOnlyInternetGateway.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-egressonlyinternetgateway.html#cfn-ec2-egressonlyinternetgateway-vpcid
        Stability:
            stable
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: str):
        return jsii.set(self, "vpcId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEgressOnlyInternetGatewayProps", jsii_struct_bases=[])
class CfnEgressOnlyInternetGatewayProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::EgressOnlyInternetGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-egressonlyinternetgateway.html
    Stability:
        stable
    """
    vpcId: str
    """``AWS::EC2::EgressOnlyInternetGateway.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-egressonlyinternetgateway.html#cfn-ec2-egressonlyinternetgateway-vpcid
    Stability:
        stable
    """

class CfnFlowLog(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnFlowLog"):
    """A CloudFormation ``AWS::EC2::FlowLog``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::FlowLog
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, resource_id: str, resource_type: str, traffic_type: str, deliver_logs_permission_arn: typing.Optional[str]=None, log_destination: typing.Optional[str]=None, log_destination_type: typing.Optional[str]=None, log_group_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::FlowLog``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            resource_id: ``AWS::EC2::FlowLog.ResourceId``.
            resource_type: ``AWS::EC2::FlowLog.ResourceType``.
            traffic_type: ``AWS::EC2::FlowLog.TrafficType``.
            deliver_logs_permission_arn: ``AWS::EC2::FlowLog.DeliverLogsPermissionArn``.
            log_destination: ``AWS::EC2::FlowLog.LogDestination``.
            log_destination_type: ``AWS::EC2::FlowLog.LogDestinationType``.
            log_group_name: ``AWS::EC2::FlowLog.LogGroupName``.

        Stability:
            experimental
        """
        props: CfnFlowLogProps = {"resourceId": resource_id, "resourceType": resource_type, "trafficType": traffic_type}

        if deliver_logs_permission_arn is not None:
            props["deliverLogsPermissionArn"] = deliver_logs_permission_arn

        if log_destination is not None:
            props["logDestination"] = log_destination

        if log_destination_type is not None:
            props["logDestinationType"] = log_destination_type

        if log_group_name is not None:
            props["logGroupName"] = log_group_name

        jsii.create(CfnFlowLog, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> str:
        """``AWS::EC2::FlowLog.ResourceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-resourceid
        Stability:
            stable
        """
        return jsii.get(self, "resourceId")

    @resource_id.setter
    def resource_id(self, value: str):
        return jsii.set(self, "resourceId", value)

    @property
    @jsii.member(jsii_name="resourceType")
    def resource_type(self) -> str:
        """``AWS::EC2::FlowLog.ResourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-resourcetype
        Stability:
            stable
        """
        return jsii.get(self, "resourceType")

    @resource_type.setter
    def resource_type(self, value: str):
        return jsii.set(self, "resourceType", value)

    @property
    @jsii.member(jsii_name="trafficType")
    def traffic_type(self) -> str:
        """``AWS::EC2::FlowLog.TrafficType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-traffictype
        Stability:
            stable
        """
        return jsii.get(self, "trafficType")

    @traffic_type.setter
    def traffic_type(self, value: str):
        return jsii.set(self, "trafficType", value)

    @property
    @jsii.member(jsii_name="deliverLogsPermissionArn")
    def deliver_logs_permission_arn(self) -> typing.Optional[str]:
        """``AWS::EC2::FlowLog.DeliverLogsPermissionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-deliverlogspermissionarn
        Stability:
            stable
        """
        return jsii.get(self, "deliverLogsPermissionArn")

    @deliver_logs_permission_arn.setter
    def deliver_logs_permission_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "deliverLogsPermissionArn", value)

    @property
    @jsii.member(jsii_name="logDestination")
    def log_destination(self) -> typing.Optional[str]:
        """``AWS::EC2::FlowLog.LogDestination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-logdestination
        Stability:
            stable
        """
        return jsii.get(self, "logDestination")

    @log_destination.setter
    def log_destination(self, value: typing.Optional[str]):
        return jsii.set(self, "logDestination", value)

    @property
    @jsii.member(jsii_name="logDestinationType")
    def log_destination_type(self) -> typing.Optional[str]:
        """``AWS::EC2::FlowLog.LogDestinationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-logdestinationtype
        Stability:
            stable
        """
        return jsii.get(self, "logDestinationType")

    @log_destination_type.setter
    def log_destination_type(self, value: typing.Optional[str]):
        return jsii.set(self, "logDestinationType", value)

    @property
    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self) -> typing.Optional[str]:
        """``AWS::EC2::FlowLog.LogGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-loggroupname
        Stability:
            stable
        """
        return jsii.get(self, "logGroupName")

    @log_group_name.setter
    def log_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "logGroupName", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnFlowLogProps(jsii.compat.TypedDict, total=False):
    deliverLogsPermissionArn: str
    """``AWS::EC2::FlowLog.DeliverLogsPermissionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-deliverlogspermissionarn
    Stability:
        stable
    """
    logDestination: str
    """``AWS::EC2::FlowLog.LogDestination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-logdestination
    Stability:
        stable
    """
    logDestinationType: str
    """``AWS::EC2::FlowLog.LogDestinationType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-logdestinationtype
    Stability:
        stable
    """
    logGroupName: str
    """``AWS::EC2::FlowLog.LogGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-loggroupname
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnFlowLogProps", jsii_struct_bases=[_CfnFlowLogProps])
class CfnFlowLogProps(_CfnFlowLogProps):
    """Properties for defining a ``AWS::EC2::FlowLog``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html
    Stability:
        stable
    """
    resourceId: str
    """``AWS::EC2::FlowLog.ResourceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-resourceid
    Stability:
        stable
    """

    resourceType: str
    """``AWS::EC2::FlowLog.ResourceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-resourcetype
    Stability:
        stable
    """

    trafficType: str
    """``AWS::EC2::FlowLog.TrafficType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-traffictype
    Stability:
        stable
    """

class CfnHost(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnHost"):
    """A CloudFormation ``AWS::EC2::Host``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::Host
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, availability_zone: str, instance_type: str, auto_placement: typing.Optional[str]=None, host_recovery: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::Host``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            availability_zone: ``AWS::EC2::Host.AvailabilityZone``.
            instance_type: ``AWS::EC2::Host.InstanceType``.
            auto_placement: ``AWS::EC2::Host.AutoPlacement``.
            host_recovery: ``AWS::EC2::Host.HostRecovery``.

        Stability:
            experimental
        """
        props: CfnHostProps = {"availabilityZone": availability_zone, "instanceType": instance_type}

        if auto_placement is not None:
            props["autoPlacement"] = auto_placement

        if host_recovery is not None:
            props["hostRecovery"] = host_recovery

        jsii.create(CfnHost, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> str:
        """``AWS::EC2::Host.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html#cfn-ec2-host-availabilityzone
        Stability:
            stable
        """
        return jsii.get(self, "availabilityZone")

    @availability_zone.setter
    def availability_zone(self, value: str):
        return jsii.set(self, "availabilityZone", value)

    @property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> str:
        """``AWS::EC2::Host.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html#cfn-ec2-host-instancetype
        Stability:
            stable
        """
        return jsii.get(self, "instanceType")

    @instance_type.setter
    def instance_type(self, value: str):
        return jsii.set(self, "instanceType", value)

    @property
    @jsii.member(jsii_name="autoPlacement")
    def auto_placement(self) -> typing.Optional[str]:
        """``AWS::EC2::Host.AutoPlacement``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html#cfn-ec2-host-autoplacement
        Stability:
            stable
        """
        return jsii.get(self, "autoPlacement")

    @auto_placement.setter
    def auto_placement(self, value: typing.Optional[str]):
        return jsii.set(self, "autoPlacement", value)

    @property
    @jsii.member(jsii_name="hostRecovery")
    def host_recovery(self) -> typing.Optional[str]:
        """``AWS::EC2::Host.HostRecovery``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html#cfn-ec2-host-hostrecovery
        Stability:
            stable
        """
        return jsii.get(self, "hostRecovery")

    @host_recovery.setter
    def host_recovery(self, value: typing.Optional[str]):
        return jsii.set(self, "hostRecovery", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnHostProps(jsii.compat.TypedDict, total=False):
    autoPlacement: str
    """``AWS::EC2::Host.AutoPlacement``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html#cfn-ec2-host-autoplacement
    Stability:
        stable
    """
    hostRecovery: str
    """``AWS::EC2::Host.HostRecovery``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html#cfn-ec2-host-hostrecovery
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnHostProps", jsii_struct_bases=[_CfnHostProps])
class CfnHostProps(_CfnHostProps):
    """Properties for defining a ``AWS::EC2::Host``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html
    Stability:
        stable
    """
    availabilityZone: str
    """``AWS::EC2::Host.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html#cfn-ec2-host-availabilityzone
    Stability:
        stable
    """

    instanceType: str
    """``AWS::EC2::Host.InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html#cfn-ec2-host-instancetype
    Stability:
        stable
    """

class CfnInstance(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnInstance"):
    """A CloudFormation ``AWS::EC2::Instance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::Instance
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, additional_info: typing.Optional[str]=None, affinity: typing.Optional[str]=None, availability_zone: typing.Optional[str]=None, block_device_mappings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "BlockDeviceMappingProperty"]]]]]=None, credit_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CreditSpecificationProperty"]]]=None, disable_api_termination: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, ebs_optimized: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, elastic_gpu_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ElasticGpuSpecificationProperty"]]]]]=None, elastic_inference_accelerators: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ElasticInferenceAcceleratorProperty"]]]]]=None, host_id: typing.Optional[str]=None, iam_instance_profile: typing.Optional[str]=None, image_id: typing.Optional[str]=None, instance_initiated_shutdown_behavior: typing.Optional[str]=None, instance_type: typing.Optional[str]=None, ipv6_address_count: typing.Optional[jsii.Number]=None, ipv6_addresses: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "InstanceIpv6AddressProperty"]]]]]=None, kernel_id: typing.Optional[str]=None, key_name: typing.Optional[str]=None, launch_template: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LaunchTemplateSpecificationProperty"]]]=None, license_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "LicenseSpecificationProperty"]]]]]=None, monitoring: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, network_interfaces: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NetworkInterfaceProperty"]]]]]=None, placement_group_name: typing.Optional[str]=None, private_ip_address: typing.Optional[str]=None, ramdisk_id: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, security_groups: typing.Optional[typing.List[str]]=None, source_dest_check: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, ssm_associations: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SsmAssociationProperty"]]]]]=None, subnet_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, tenancy: typing.Optional[str]=None, user_data: typing.Optional[str]=None, volumes: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "VolumeProperty"]]]]]=None) -> None:
        """Create a new ``AWS::EC2::Instance``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            additional_info: ``AWS::EC2::Instance.AdditionalInfo``.
            affinity: ``AWS::EC2::Instance.Affinity``.
            availability_zone: ``AWS::EC2::Instance.AvailabilityZone``.
            block_device_mappings: ``AWS::EC2::Instance.BlockDeviceMappings``.
            credit_specification: ``AWS::EC2::Instance.CreditSpecification``.
            disable_api_termination: ``AWS::EC2::Instance.DisableApiTermination``.
            ebs_optimized: ``AWS::EC2::Instance.EbsOptimized``.
            elastic_gpu_specifications: ``AWS::EC2::Instance.ElasticGpuSpecifications``.
            elastic_inference_accelerators: ``AWS::EC2::Instance.ElasticInferenceAccelerators``.
            host_id: ``AWS::EC2::Instance.HostId``.
            iam_instance_profile: ``AWS::EC2::Instance.IamInstanceProfile``.
            image_id: ``AWS::EC2::Instance.ImageId``.
            instance_initiated_shutdown_behavior: ``AWS::EC2::Instance.InstanceInitiatedShutdownBehavior``.
            instance_type: ``AWS::EC2::Instance.InstanceType``.
            ipv6_address_count: ``AWS::EC2::Instance.Ipv6AddressCount``.
            ipv6_addresses: ``AWS::EC2::Instance.Ipv6Addresses``.
            kernel_id: ``AWS::EC2::Instance.KernelId``.
            key_name: ``AWS::EC2::Instance.KeyName``.
            launch_template: ``AWS::EC2::Instance.LaunchTemplate``.
            license_specifications: ``AWS::EC2::Instance.LicenseSpecifications``.
            monitoring: ``AWS::EC2::Instance.Monitoring``.
            network_interfaces: ``AWS::EC2::Instance.NetworkInterfaces``.
            placement_group_name: ``AWS::EC2::Instance.PlacementGroupName``.
            private_ip_address: ``AWS::EC2::Instance.PrivateIpAddress``.
            ramdisk_id: ``AWS::EC2::Instance.RamdiskId``.
            security_group_ids: ``AWS::EC2::Instance.SecurityGroupIds``.
            security_groups: ``AWS::EC2::Instance.SecurityGroups``.
            source_dest_check: ``AWS::EC2::Instance.SourceDestCheck``.
            ssm_associations: ``AWS::EC2::Instance.SsmAssociations``.
            subnet_id: ``AWS::EC2::Instance.SubnetId``.
            tags: ``AWS::EC2::Instance.Tags``.
            tenancy: ``AWS::EC2::Instance.Tenancy``.
            user_data: ``AWS::EC2::Instance.UserData``.
            volumes: ``AWS::EC2::Instance.Volumes``.

        Stability:
            experimental
        """
        props: CfnInstanceProps = {}

        if additional_info is not None:
            props["additionalInfo"] = additional_info

        if affinity is not None:
            props["affinity"] = affinity

        if availability_zone is not None:
            props["availabilityZone"] = availability_zone

        if block_device_mappings is not None:
            props["blockDeviceMappings"] = block_device_mappings

        if credit_specification is not None:
            props["creditSpecification"] = credit_specification

        if disable_api_termination is not None:
            props["disableApiTermination"] = disable_api_termination

        if ebs_optimized is not None:
            props["ebsOptimized"] = ebs_optimized

        if elastic_gpu_specifications is not None:
            props["elasticGpuSpecifications"] = elastic_gpu_specifications

        if elastic_inference_accelerators is not None:
            props["elasticInferenceAccelerators"] = elastic_inference_accelerators

        if host_id is not None:
            props["hostId"] = host_id

        if iam_instance_profile is not None:
            props["iamInstanceProfile"] = iam_instance_profile

        if image_id is not None:
            props["imageId"] = image_id

        if instance_initiated_shutdown_behavior is not None:
            props["instanceInitiatedShutdownBehavior"] = instance_initiated_shutdown_behavior

        if instance_type is not None:
            props["instanceType"] = instance_type

        if ipv6_address_count is not None:
            props["ipv6AddressCount"] = ipv6_address_count

        if ipv6_addresses is not None:
            props["ipv6Addresses"] = ipv6_addresses

        if kernel_id is not None:
            props["kernelId"] = kernel_id

        if key_name is not None:
            props["keyName"] = key_name

        if launch_template is not None:
            props["launchTemplate"] = launch_template

        if license_specifications is not None:
            props["licenseSpecifications"] = license_specifications

        if monitoring is not None:
            props["monitoring"] = monitoring

        if network_interfaces is not None:
            props["networkInterfaces"] = network_interfaces

        if placement_group_name is not None:
            props["placementGroupName"] = placement_group_name

        if private_ip_address is not None:
            props["privateIpAddress"] = private_ip_address

        if ramdisk_id is not None:
            props["ramdiskId"] = ramdisk_id

        if security_group_ids is not None:
            props["securityGroupIds"] = security_group_ids

        if security_groups is not None:
            props["securityGroups"] = security_groups

        if source_dest_check is not None:
            props["sourceDestCheck"] = source_dest_check

        if ssm_associations is not None:
            props["ssmAssociations"] = ssm_associations

        if subnet_id is not None:
            props["subnetId"] = subnet_id

        if tags is not None:
            props["tags"] = tags

        if tenancy is not None:
            props["tenancy"] = tenancy

        if user_data is not None:
            props["userData"] = user_data

        if volumes is not None:
            props["volumes"] = volumes

        jsii.create(CfnInstance, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrAvailabilityZone")
    def attr_availability_zone(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            AvailabilityZone
        """
        return jsii.get(self, "attrAvailabilityZone")

    @property
    @jsii.member(jsii_name="attrPrivateDnsName")
    def attr_private_dns_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            PrivateDnsName
        """
        return jsii.get(self, "attrPrivateDnsName")

    @property
    @jsii.member(jsii_name="attrPrivateIp")
    def attr_private_ip(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            PrivateIp
        """
        return jsii.get(self, "attrPrivateIp")

    @property
    @jsii.member(jsii_name="attrPublicDnsName")
    def attr_public_dns_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            PublicDnsName
        """
        return jsii.get(self, "attrPublicDnsName")

    @property
    @jsii.member(jsii_name="attrPublicIp")
    def attr_public_ip(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            PublicIp
        """
        return jsii.get(self, "attrPublicIp")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::Instance.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="additionalInfo")
    def additional_info(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.AdditionalInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-additionalinfo
        Stability:
            stable
        """
        return jsii.get(self, "additionalInfo")

    @additional_info.setter
    def additional_info(self, value: typing.Optional[str]):
        return jsii.set(self, "additionalInfo", value)

    @property
    @jsii.member(jsii_name="affinity")
    def affinity(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.Affinity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-affinity
        Stability:
            stable
        """
        return jsii.get(self, "affinity")

    @affinity.setter
    def affinity(self, value: typing.Optional[str]):
        return jsii.set(self, "affinity", value)

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-availabilityzone
        Stability:
            stable
        """
        return jsii.get(self, "availabilityZone")

    @availability_zone.setter
    def availability_zone(self, value: typing.Optional[str]):
        return jsii.set(self, "availabilityZone", value)

    @property
    @jsii.member(jsii_name="blockDeviceMappings")
    def block_device_mappings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "BlockDeviceMappingProperty"]]]]]:
        """``AWS::EC2::Instance.BlockDeviceMappings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-blockdevicemappings
        Stability:
            stable
        """
        return jsii.get(self, "blockDeviceMappings")

    @block_device_mappings.setter
    def block_device_mappings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "BlockDeviceMappingProperty"]]]]]):
        return jsii.set(self, "blockDeviceMappings", value)

    @property
    @jsii.member(jsii_name="creditSpecification")
    def credit_specification(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CreditSpecificationProperty"]]]:
        """``AWS::EC2::Instance.CreditSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-creditspecification
        Stability:
            stable
        """
        return jsii.get(self, "creditSpecification")

    @credit_specification.setter
    def credit_specification(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CreditSpecificationProperty"]]]):
        return jsii.set(self, "creditSpecification", value)

    @property
    @jsii.member(jsii_name="disableApiTermination")
    def disable_api_termination(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::Instance.DisableApiTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-disableapitermination
        Stability:
            stable
        """
        return jsii.get(self, "disableApiTermination")

    @disable_api_termination.setter
    def disable_api_termination(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "disableApiTermination", value)

    @property
    @jsii.member(jsii_name="ebsOptimized")
    def ebs_optimized(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::Instance.EbsOptimized``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ebsoptimized
        Stability:
            stable
        """
        return jsii.get(self, "ebsOptimized")

    @ebs_optimized.setter
    def ebs_optimized(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "ebsOptimized", value)

    @property
    @jsii.member(jsii_name="elasticGpuSpecifications")
    def elastic_gpu_specifications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ElasticGpuSpecificationProperty"]]]]]:
        """``AWS::EC2::Instance.ElasticGpuSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-elasticgpuspecifications
        Stability:
            stable
        """
        return jsii.get(self, "elasticGpuSpecifications")

    @elastic_gpu_specifications.setter
    def elastic_gpu_specifications(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ElasticGpuSpecificationProperty"]]]]]):
        return jsii.set(self, "elasticGpuSpecifications", value)

    @property
    @jsii.member(jsii_name="elasticInferenceAccelerators")
    def elastic_inference_accelerators(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ElasticInferenceAcceleratorProperty"]]]]]:
        """``AWS::EC2::Instance.ElasticInferenceAccelerators``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-elasticinferenceaccelerators
        Stability:
            stable
        """
        return jsii.get(self, "elasticInferenceAccelerators")

    @elastic_inference_accelerators.setter
    def elastic_inference_accelerators(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ElasticInferenceAcceleratorProperty"]]]]]):
        return jsii.set(self, "elasticInferenceAccelerators", value)

    @property
    @jsii.member(jsii_name="hostId")
    def host_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.HostId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-hostid
        Stability:
            stable
        """
        return jsii.get(self, "hostId")

    @host_id.setter
    def host_id(self, value: typing.Optional[str]):
        return jsii.set(self, "hostId", value)

    @property
    @jsii.member(jsii_name="iamInstanceProfile")
    def iam_instance_profile(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.IamInstanceProfile``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-iaminstanceprofile
        Stability:
            stable
        """
        return jsii.get(self, "iamInstanceProfile")

    @iam_instance_profile.setter
    def iam_instance_profile(self, value: typing.Optional[str]):
        return jsii.set(self, "iamInstanceProfile", value)

    @property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.ImageId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-imageid
        Stability:
            stable
        """
        return jsii.get(self, "imageId")

    @image_id.setter
    def image_id(self, value: typing.Optional[str]):
        return jsii.set(self, "imageId", value)

    @property
    @jsii.member(jsii_name="instanceInitiatedShutdownBehavior")
    def instance_initiated_shutdown_behavior(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.InstanceInitiatedShutdownBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-instanceinitiatedshutdownbehavior
        Stability:
            stable
        """
        return jsii.get(self, "instanceInitiatedShutdownBehavior")

    @instance_initiated_shutdown_behavior.setter
    def instance_initiated_shutdown_behavior(self, value: typing.Optional[str]):
        return jsii.set(self, "instanceInitiatedShutdownBehavior", value)

    @property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-instancetype
        Stability:
            stable
        """
        return jsii.get(self, "instanceType")

    @instance_type.setter
    def instance_type(self, value: typing.Optional[str]):
        return jsii.set(self, "instanceType", value)

    @property
    @jsii.member(jsii_name="ipv6AddressCount")
    def ipv6_address_count(self) -> typing.Optional[jsii.Number]:
        """``AWS::EC2::Instance.Ipv6AddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ipv6addresscount
        Stability:
            stable
        """
        return jsii.get(self, "ipv6AddressCount")

    @ipv6_address_count.setter
    def ipv6_address_count(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "ipv6AddressCount", value)

    @property
    @jsii.member(jsii_name="ipv6Addresses")
    def ipv6_addresses(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "InstanceIpv6AddressProperty"]]]]]:
        """``AWS::EC2::Instance.Ipv6Addresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ipv6addresses
        Stability:
            stable
        """
        return jsii.get(self, "ipv6Addresses")

    @ipv6_addresses.setter
    def ipv6_addresses(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "InstanceIpv6AddressProperty"]]]]]):
        return jsii.set(self, "ipv6Addresses", value)

    @property
    @jsii.member(jsii_name="kernelId")
    def kernel_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.KernelId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-kernelid
        Stability:
            stable
        """
        return jsii.get(self, "kernelId")

    @kernel_id.setter
    def kernel_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kernelId", value)

    @property
    @jsii.member(jsii_name="keyName")
    def key_name(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.KeyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-keyname
        Stability:
            stable
        """
        return jsii.get(self, "keyName")

    @key_name.setter
    def key_name(self, value: typing.Optional[str]):
        return jsii.set(self, "keyName", value)

    @property
    @jsii.member(jsii_name="launchTemplate")
    def launch_template(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LaunchTemplateSpecificationProperty"]]]:
        """``AWS::EC2::Instance.LaunchTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-launchtemplate
        Stability:
            stable
        """
        return jsii.get(self, "launchTemplate")

    @launch_template.setter
    def launch_template(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LaunchTemplateSpecificationProperty"]]]):
        return jsii.set(self, "launchTemplate", value)

    @property
    @jsii.member(jsii_name="licenseSpecifications")
    def license_specifications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "LicenseSpecificationProperty"]]]]]:
        """``AWS::EC2::Instance.LicenseSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-licensespecifications
        Stability:
            stable
        """
        return jsii.get(self, "licenseSpecifications")

    @license_specifications.setter
    def license_specifications(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "LicenseSpecificationProperty"]]]]]):
        return jsii.set(self, "licenseSpecifications", value)

    @property
    @jsii.member(jsii_name="monitoring")
    def monitoring(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::Instance.Monitoring``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-monitoring
        Stability:
            stable
        """
        return jsii.get(self, "monitoring")

    @monitoring.setter
    def monitoring(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "monitoring", value)

    @property
    @jsii.member(jsii_name="networkInterfaces")
    def network_interfaces(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NetworkInterfaceProperty"]]]]]:
        """``AWS::EC2::Instance.NetworkInterfaces``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-networkinterfaces
        Stability:
            stable
        """
        return jsii.get(self, "networkInterfaces")

    @network_interfaces.setter
    def network_interfaces(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NetworkInterfaceProperty"]]]]]):
        return jsii.set(self, "networkInterfaces", value)

    @property
    @jsii.member(jsii_name="placementGroupName")
    def placement_group_name(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.PlacementGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-placementgroupname
        Stability:
            stable
        """
        return jsii.get(self, "placementGroupName")

    @placement_group_name.setter
    def placement_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "placementGroupName", value)

    @property
    @jsii.member(jsii_name="privateIpAddress")
    def private_ip_address(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-privateipaddress
        Stability:
            stable
        """
        return jsii.get(self, "privateIpAddress")

    @private_ip_address.setter
    def private_ip_address(self, value: typing.Optional[str]):
        return jsii.set(self, "privateIpAddress", value)

    @property
    @jsii.member(jsii_name="ramdiskId")
    def ramdisk_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.RamdiskId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ramdiskid
        Stability:
            stable
        """
        return jsii.get(self, "ramdiskId")

    @ramdisk_id.setter
    def ramdisk_id(self, value: typing.Optional[str]):
        return jsii.set(self, "ramdiskId", value)

    @property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::EC2::Instance.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-securitygroupids
        Stability:
            stable
        """
        return jsii.get(self, "securityGroupIds")

    @security_group_ids.setter
    def security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "securityGroupIds", value)

    @property
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.Optional[typing.List[str]]:
        """``AWS::EC2::Instance.SecurityGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-securitygroups
        Stability:
            stable
        """
        return jsii.get(self, "securityGroups")

    @security_groups.setter
    def security_groups(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "securityGroups", value)

    @property
    @jsii.member(jsii_name="sourceDestCheck")
    def source_dest_check(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::Instance.SourceDestCheck``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-sourcedestcheck
        Stability:
            stable
        """
        return jsii.get(self, "sourceDestCheck")

    @source_dest_check.setter
    def source_dest_check(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "sourceDestCheck", value)

    @property
    @jsii.member(jsii_name="ssmAssociations")
    def ssm_associations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SsmAssociationProperty"]]]]]:
        """``AWS::EC2::Instance.SsmAssociations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ssmassociations
        Stability:
            stable
        """
        return jsii.get(self, "ssmAssociations")

    @ssm_associations.setter
    def ssm_associations(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SsmAssociationProperty"]]]]]):
        return jsii.set(self, "ssmAssociations", value)

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-subnetid
        Stability:
            stable
        """
        return jsii.get(self, "subnetId")

    @subnet_id.setter
    def subnet_id(self, value: typing.Optional[str]):
        return jsii.set(self, "subnetId", value)

    @property
    @jsii.member(jsii_name="tenancy")
    def tenancy(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.Tenancy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-tenancy
        Stability:
            stable
        """
        return jsii.get(self, "tenancy")

    @tenancy.setter
    def tenancy(self, value: typing.Optional[str]):
        return jsii.set(self, "tenancy", value)

    @property
    @jsii.member(jsii_name="userData")
    def user_data(self) -> typing.Optional[str]:
        """``AWS::EC2::Instance.UserData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-userdata
        Stability:
            stable
        """
        return jsii.get(self, "userData")

    @user_data.setter
    def user_data(self, value: typing.Optional[str]):
        return jsii.set(self, "userData", value)

    @property
    @jsii.member(jsii_name="volumes")
    def volumes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "VolumeProperty"]]]]]:
        """``AWS::EC2::Instance.Volumes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-volumes
        Stability:
            stable
        """
        return jsii.get(self, "volumes")

    @volumes.setter
    def volumes(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "VolumeProperty"]]]]]):
        return jsii.set(self, "volumes", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.AssociationParameterProperty", jsii_struct_bases=[])
    class AssociationParameterProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-ssmassociations-associationparameters.html
        Stability:
            stable
        """
        key: str
        """``CfnInstance.AssociationParameterProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-ssmassociations-associationparameters.html#cfn-ec2-instance-ssmassociations-associationparameters-key
        Stability:
            stable
        """

        value: typing.List[str]
        """``CfnInstance.AssociationParameterProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-ssmassociations-associationparameters.html#cfn-ec2-instance-ssmassociations-associationparameters-value
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _BlockDeviceMappingProperty(jsii.compat.TypedDict, total=False):
        ebs: typing.Union[aws_cdk.core.IResolvable, "CfnInstance.EbsProperty"]
        """``CfnInstance.BlockDeviceMappingProperty.Ebs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-mapping.html#cfn-ec2-blockdev-mapping-ebs
        Stability:
            stable
        """
        noDevice: typing.Union[aws_cdk.core.IResolvable, "CfnInstance.NoDeviceProperty"]
        """``CfnInstance.BlockDeviceMappingProperty.NoDevice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-mapping.html#cfn-ec2-blockdev-mapping-nodevice
        Stability:
            stable
        """
        virtualName: str
        """``CfnInstance.BlockDeviceMappingProperty.VirtualName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-mapping.html#cfn-ec2-blockdev-mapping-virtualname
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.BlockDeviceMappingProperty", jsii_struct_bases=[_BlockDeviceMappingProperty])
    class BlockDeviceMappingProperty(_BlockDeviceMappingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-mapping.html
        Stability:
            stable
        """
        deviceName: str
        """``CfnInstance.BlockDeviceMappingProperty.DeviceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-mapping.html#cfn-ec2-blockdev-mapping-devicename
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.CreditSpecificationProperty", jsii_struct_bases=[])
    class CreditSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-creditspecification.html
        Stability:
            stable
        """
        cpuCredits: str
        """``CfnInstance.CreditSpecificationProperty.CPUCredits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-creditspecification.html#cfn-ec2-instance-creditspecification-cpucredits
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.EbsProperty", jsii_struct_bases=[])
    class EbsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html
        Stability:
            stable
        """
        deleteOnTermination: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnInstance.EbsProperty.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html#cfn-ec2-blockdev-template-deleteontermination
        Stability:
            stable
        """

        encrypted: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnInstance.EbsProperty.Encrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html#cfn-ec2-blockdev-template-encrypted
        Stability:
            stable
        """

        iops: jsii.Number
        """``CfnInstance.EbsProperty.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html#cfn-ec2-blockdev-template-iops
        Stability:
            stable
        """

        snapshotId: str
        """``CfnInstance.EbsProperty.SnapshotId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html#cfn-ec2-blockdev-template-snapshotid
        Stability:
            stable
        """

        volumeSize: jsii.Number
        """``CfnInstance.EbsProperty.VolumeSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html#cfn-ec2-blockdev-template-volumesize
        Stability:
            stable
        """

        volumeType: str
        """``CfnInstance.EbsProperty.VolumeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html#cfn-ec2-blockdev-template-volumetype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.ElasticGpuSpecificationProperty", jsii_struct_bases=[])
    class ElasticGpuSpecificationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-elasticgpuspecification.html
        Stability:
            stable
        """
        type: str
        """``CfnInstance.ElasticGpuSpecificationProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-elasticgpuspecification.html#cfn-ec2-instance-elasticgpuspecification-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.ElasticInferenceAcceleratorProperty", jsii_struct_bases=[])
    class ElasticInferenceAcceleratorProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-elasticinferenceaccelerator.html
        Stability:
            stable
        """
        type: str
        """``CfnInstance.ElasticInferenceAcceleratorProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-elasticinferenceaccelerator.html#cfn-ec2-instance-elasticinferenceaccelerator-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.InstanceIpv6AddressProperty", jsii_struct_bases=[])
    class InstanceIpv6AddressProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-instanceipv6address.html
        Stability:
            stable
        """
        ipv6Address: str
        """``CfnInstance.InstanceIpv6AddressProperty.Ipv6Address``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-instanceipv6address.html#cfn-ec2-instance-instanceipv6address-ipv6address
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LaunchTemplateSpecificationProperty(jsii.compat.TypedDict, total=False):
        launchTemplateId: str
        """``CfnInstance.LaunchTemplateSpecificationProperty.LaunchTemplateId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-launchtemplatespecification.html#cfn-ec2-instance-launchtemplatespecification-launchtemplateid
        Stability:
            stable
        """
        launchTemplateName: str
        """``CfnInstance.LaunchTemplateSpecificationProperty.LaunchTemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-launchtemplatespecification.html#cfn-ec2-instance-launchtemplatespecification-launchtemplatename
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.LaunchTemplateSpecificationProperty", jsii_struct_bases=[_LaunchTemplateSpecificationProperty])
    class LaunchTemplateSpecificationProperty(_LaunchTemplateSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-launchtemplatespecification.html
        Stability:
            stable
        """
        version: str
        """``CfnInstance.LaunchTemplateSpecificationProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-launchtemplatespecification.html#cfn-ec2-instance-launchtemplatespecification-version
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.LicenseSpecificationProperty", jsii_struct_bases=[])
    class LicenseSpecificationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-licensespecification.html
        Stability:
            stable
        """
        licenseConfigurationArn: str
        """``CfnInstance.LicenseSpecificationProperty.LicenseConfigurationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-licensespecification.html#cfn-ec2-instance-licensespecification-licenseconfigurationarn
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _NetworkInterfaceProperty(jsii.compat.TypedDict, total=False):
        associatePublicIpAddress: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnInstance.NetworkInterfaceProperty.AssociatePublicIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-associatepubip
        Stability:
            stable
        """
        deleteOnTermination: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnInstance.NetworkInterfaceProperty.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-delete
        Stability:
            stable
        """
        description: str
        """``CfnInstance.NetworkInterfaceProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-description
        Stability:
            stable
        """
        groupSet: typing.List[str]
        """``CfnInstance.NetworkInterfaceProperty.GroupSet``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-groupset
        Stability:
            stable
        """
        ipv6AddressCount: jsii.Number
        """``CfnInstance.NetworkInterfaceProperty.Ipv6AddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#cfn-ec2-instance-networkinterface-ipv6addresscount
        Stability:
            stable
        """
        ipv6Addresses: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstance.InstanceIpv6AddressProperty"]]]
        """``CfnInstance.NetworkInterfaceProperty.Ipv6Addresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#cfn-ec2-instance-networkinterface-ipv6addresses
        Stability:
            stable
        """
        networkInterfaceId: str
        """``CfnInstance.NetworkInterfaceProperty.NetworkInterfaceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-network-iface
        Stability:
            stable
        """
        privateIpAddress: str
        """``CfnInstance.NetworkInterfaceProperty.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-privateipaddress
        Stability:
            stable
        """
        privateIpAddresses: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstance.PrivateIpAddressSpecificationProperty"]]]
        """``CfnInstance.NetworkInterfaceProperty.PrivateIpAddresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-privateipaddresses
        Stability:
            stable
        """
        secondaryPrivateIpAddressCount: jsii.Number
        """``CfnInstance.NetworkInterfaceProperty.SecondaryPrivateIpAddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-secondprivateip
        Stability:
            stable
        """
        subnetId: str
        """``CfnInstance.NetworkInterfaceProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-subnetid
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.NetworkInterfaceProperty", jsii_struct_bases=[_NetworkInterfaceProperty])
    class NetworkInterfaceProperty(_NetworkInterfaceProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html
        Stability:
            stable
        """
        deviceIndex: str
        """``CfnInstance.NetworkInterfaceProperty.DeviceIndex``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-deviceindex
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.NoDeviceProperty", jsii_struct_bases=[])
    class NoDeviceProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-nodevice.html
        Stability:
            stable
        """
        pass

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.PrivateIpAddressSpecificationProperty", jsii_struct_bases=[])
    class PrivateIpAddressSpecificationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-interface-privateipspec.html
        Stability:
            stable
        """
        primary: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnInstance.PrivateIpAddressSpecificationProperty.Primary``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-interface-privateipspec.html#cfn-ec2-networkinterface-privateipspecification-primary
        Stability:
            stable
        """

        privateIpAddress: str
        """``CfnInstance.PrivateIpAddressSpecificationProperty.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-interface-privateipspec.html#cfn-ec2-networkinterface-privateipspecification-privateipaddress
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SsmAssociationProperty(jsii.compat.TypedDict, total=False):
        associationParameters: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstance.AssociationParameterProperty"]]]
        """``CfnInstance.SsmAssociationProperty.AssociationParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-ssmassociations.html#cfn-ec2-instance-ssmassociations-associationparameters
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.SsmAssociationProperty", jsii_struct_bases=[_SsmAssociationProperty])
    class SsmAssociationProperty(_SsmAssociationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-ssmassociations.html
        Stability:
            stable
        """
        documentName: str
        """``CfnInstance.SsmAssociationProperty.DocumentName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-ssmassociations.html#cfn-ec2-instance-ssmassociations-documentname
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.VolumeProperty", jsii_struct_bases=[])
    class VolumeProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-mount-point.html
        Stability:
            stable
        """
        device: str
        """``CfnInstance.VolumeProperty.Device``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-mount-point.html#cfn-ec2-mountpoint-device
        Stability:
            stable
        """

        volumeId: str
        """``CfnInstance.VolumeProperty.VolumeId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-mount-point.html#cfn-ec2-mountpoint-volumeid
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstanceProps", jsii_struct_bases=[])
class CfnInstanceProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::Instance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html
    Stability:
        stable
    """
    additionalInfo: str
    """``AWS::EC2::Instance.AdditionalInfo``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-additionalinfo
    Stability:
        stable
    """

    affinity: str
    """``AWS::EC2::Instance.Affinity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-affinity
    Stability:
        stable
    """

    availabilityZone: str
    """``AWS::EC2::Instance.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-availabilityzone
    Stability:
        stable
    """

    blockDeviceMappings: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstance.BlockDeviceMappingProperty"]]]
    """``AWS::EC2::Instance.BlockDeviceMappings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-blockdevicemappings
    Stability:
        stable
    """

    creditSpecification: typing.Union[aws_cdk.core.IResolvable, "CfnInstance.CreditSpecificationProperty"]
    """``AWS::EC2::Instance.CreditSpecification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-creditspecification
    Stability:
        stable
    """

    disableApiTermination: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::Instance.DisableApiTermination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-disableapitermination
    Stability:
        stable
    """

    ebsOptimized: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::Instance.EbsOptimized``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ebsoptimized
    Stability:
        stable
    """

    elasticGpuSpecifications: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstance.ElasticGpuSpecificationProperty"]]]
    """``AWS::EC2::Instance.ElasticGpuSpecifications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-elasticgpuspecifications
    Stability:
        stable
    """

    elasticInferenceAccelerators: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstance.ElasticInferenceAcceleratorProperty"]]]
    """``AWS::EC2::Instance.ElasticInferenceAccelerators``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-elasticinferenceaccelerators
    Stability:
        stable
    """

    hostId: str
    """``AWS::EC2::Instance.HostId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-hostid
    Stability:
        stable
    """

    iamInstanceProfile: str
    """``AWS::EC2::Instance.IamInstanceProfile``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-iaminstanceprofile
    Stability:
        stable
    """

    imageId: str
    """``AWS::EC2::Instance.ImageId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-imageid
    Stability:
        stable
    """

    instanceInitiatedShutdownBehavior: str
    """``AWS::EC2::Instance.InstanceInitiatedShutdownBehavior``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-instanceinitiatedshutdownbehavior
    Stability:
        stable
    """

    instanceType: str
    """``AWS::EC2::Instance.InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-instancetype
    Stability:
        stable
    """

    ipv6AddressCount: jsii.Number
    """``AWS::EC2::Instance.Ipv6AddressCount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ipv6addresscount
    Stability:
        stable
    """

    ipv6Addresses: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstance.InstanceIpv6AddressProperty"]]]
    """``AWS::EC2::Instance.Ipv6Addresses``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ipv6addresses
    Stability:
        stable
    """

    kernelId: str
    """``AWS::EC2::Instance.KernelId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-kernelid
    Stability:
        stable
    """

    keyName: str
    """``AWS::EC2::Instance.KeyName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-keyname
    Stability:
        stable
    """

    launchTemplate: typing.Union[aws_cdk.core.IResolvable, "CfnInstance.LaunchTemplateSpecificationProperty"]
    """``AWS::EC2::Instance.LaunchTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-launchtemplate
    Stability:
        stable
    """

    licenseSpecifications: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstance.LicenseSpecificationProperty"]]]
    """``AWS::EC2::Instance.LicenseSpecifications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-licensespecifications
    Stability:
        stable
    """

    monitoring: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::Instance.Monitoring``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-monitoring
    Stability:
        stable
    """

    networkInterfaces: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstance.NetworkInterfaceProperty"]]]
    """``AWS::EC2::Instance.NetworkInterfaces``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-networkinterfaces
    Stability:
        stable
    """

    placementGroupName: str
    """``AWS::EC2::Instance.PlacementGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-placementgroupname
    Stability:
        stable
    """

    privateIpAddress: str
    """``AWS::EC2::Instance.PrivateIpAddress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-privateipaddress
    Stability:
        stable
    """

    ramdiskId: str
    """``AWS::EC2::Instance.RamdiskId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ramdiskid
    Stability:
        stable
    """

    securityGroupIds: typing.List[str]
    """``AWS::EC2::Instance.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-securitygroupids
    Stability:
        stable
    """

    securityGroups: typing.List[str]
    """``AWS::EC2::Instance.SecurityGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-securitygroups
    Stability:
        stable
    """

    sourceDestCheck: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::Instance.SourceDestCheck``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-sourcedestcheck
    Stability:
        stable
    """

    ssmAssociations: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstance.SsmAssociationProperty"]]]
    """``AWS::EC2::Instance.SsmAssociations``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ssmassociations
    Stability:
        stable
    """

    subnetId: str
    """``AWS::EC2::Instance.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-subnetid
    Stability:
        stable
    """

    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::Instance.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-tags
    Stability:
        stable
    """

    tenancy: str
    """``AWS::EC2::Instance.Tenancy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-tenancy
    Stability:
        stable
    """

    userData: str
    """``AWS::EC2::Instance.UserData``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-userdata
    Stability:
        stable
    """

    volumes: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnInstance.VolumeProperty"]]]
    """``AWS::EC2::Instance.Volumes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-volumes
    Stability:
        stable
    """

class CfnInternetGateway(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnInternetGateway"):
    """A CloudFormation ``AWS::EC2::InternetGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-internetgateway.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::InternetGateway
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::InternetGateway``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            tags: ``AWS::EC2::InternetGateway.Tags``.

        Stability:
            experimental
        """
        props: CfnInternetGatewayProps = {}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnInternetGateway, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::InternetGateway.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-internetgateway.html#cfn-ec2-internetgateway-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInternetGatewayProps", jsii_struct_bases=[])
class CfnInternetGatewayProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::InternetGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-internetgateway.html
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::InternetGateway.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-internetgateway.html#cfn-ec2-internetgateway-tags
    Stability:
        stable
    """

class CfnLaunchTemplate(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate"):
    """A CloudFormation ``AWS::EC2::LaunchTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-launchtemplate.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::LaunchTemplate
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, launch_template_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LaunchTemplateDataProperty"]]]=None, launch_template_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::LaunchTemplate``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            launch_template_data: ``AWS::EC2::LaunchTemplate.LaunchTemplateData``.
            launch_template_name: ``AWS::EC2::LaunchTemplate.LaunchTemplateName``.

        Stability:
            experimental
        """
        props: CfnLaunchTemplateProps = {}

        if launch_template_data is not None:
            props["launchTemplateData"] = launch_template_data

        if launch_template_name is not None:
            props["launchTemplateName"] = launch_template_name

        jsii.create(CfnLaunchTemplate, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrDefaultVersionNumber")
    def attr_default_version_number(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            DefaultVersionNumber
        """
        return jsii.get(self, "attrDefaultVersionNumber")

    @property
    @jsii.member(jsii_name="attrLatestVersionNumber")
    def attr_latest_version_number(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            LatestVersionNumber
        """
        return jsii.get(self, "attrLatestVersionNumber")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="launchTemplateData")
    def launch_template_data(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LaunchTemplateDataProperty"]]]:
        """``AWS::EC2::LaunchTemplate.LaunchTemplateData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-launchtemplate.html#cfn-ec2-launchtemplate-launchtemplatedata
        Stability:
            stable
        """
        return jsii.get(self, "launchTemplateData")

    @launch_template_data.setter
    def launch_template_data(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LaunchTemplateDataProperty"]]]):
        return jsii.set(self, "launchTemplateData", value)

    @property
    @jsii.member(jsii_name="launchTemplateName")
    def launch_template_name(self) -> typing.Optional[str]:
        """``AWS::EC2::LaunchTemplate.LaunchTemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-launchtemplate.html#cfn-ec2-launchtemplate-launchtemplatename
        Stability:
            stable
        """
        return jsii.get(self, "launchTemplateName")

    @launch_template_name.setter
    def launch_template_name(self, value: typing.Optional[str]):
        return jsii.set(self, "launchTemplateName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.BlockDeviceMappingProperty", jsii_struct_bases=[])
    class BlockDeviceMappingProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping.html
        Stability:
            stable
        """
        deviceName: str
        """``CfnLaunchTemplate.BlockDeviceMappingProperty.DeviceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping.html#cfn-ec2-launchtemplate-blockdevicemapping-devicename
        Stability:
            stable
        """

        ebs: typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.EbsProperty"]
        """``CfnLaunchTemplate.BlockDeviceMappingProperty.Ebs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs
        Stability:
            stable
        """

        noDevice: str
        """``CfnLaunchTemplate.BlockDeviceMappingProperty.NoDevice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping.html#cfn-ec2-launchtemplate-blockdevicemapping-nodevice
        Stability:
            stable
        """

        virtualName: str
        """``CfnLaunchTemplate.BlockDeviceMappingProperty.VirtualName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping.html#cfn-ec2-launchtemplate-blockdevicemapping-virtualname
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.CapacityReservationSpecificationProperty", jsii_struct_bases=[])
    class CapacityReservationSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-capacityreservationspecification.html
        Stability:
            stable
        """
        capacityReservationPreference: str
        """``CfnLaunchTemplate.CapacityReservationSpecificationProperty.CapacityReservationPreference``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-capacityreservationspecification.html#cfn-ec2-launchtemplate-launchtemplatedata-capacityreservationspecification-capacityreservationpreference
        Stability:
            stable
        """

        capacityReservationTarget: typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.CapacityReservationTargetProperty"]
        """``CfnLaunchTemplate.CapacityReservationSpecificationProperty.CapacityReservationTarget``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-capacityreservationspecification.html#cfn-ec2-launchtemplate-launchtemplatedata-capacityreservationspecification-capacityreservationtarget
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.CapacityReservationTargetProperty", jsii_struct_bases=[])
    class CapacityReservationTargetProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-capacityreservationtarget.html
        Stability:
            stable
        """
        capacityReservationId: str
        """``CfnLaunchTemplate.CapacityReservationTargetProperty.CapacityReservationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-capacityreservationtarget.html#cfn-ec2-launchtemplate-capacityreservationtarget-capacityreservationid
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.CpuOptionsProperty", jsii_struct_bases=[])
    class CpuOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-cpuoptions.html
        Stability:
            stable
        """
        coreCount: jsii.Number
        """``CfnLaunchTemplate.CpuOptionsProperty.CoreCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-cpuoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-cpuoptions-corecount
        Stability:
            stable
        """

        threadsPerCore: jsii.Number
        """``CfnLaunchTemplate.CpuOptionsProperty.ThreadsPerCore``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-cpuoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-cpuoptions-threadspercore
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.CreditSpecificationProperty", jsii_struct_bases=[])
    class CreditSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-creditspecification.html
        Stability:
            stable
        """
        cpuCredits: str
        """``CfnLaunchTemplate.CreditSpecificationProperty.CpuCredits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-creditspecification.html#cfn-ec2-launchtemplate-launchtemplatedata-creditspecification-cpucredits
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.EbsProperty", jsii_struct_bases=[])
    class EbsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html
        Stability:
            stable
        """
        deleteOnTermination: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnLaunchTemplate.EbsProperty.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-deleteontermination
        Stability:
            stable
        """

        encrypted: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnLaunchTemplate.EbsProperty.Encrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-encrypted
        Stability:
            stable
        """

        iops: jsii.Number
        """``CfnLaunchTemplate.EbsProperty.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-iops
        Stability:
            stable
        """

        kmsKeyId: str
        """``CfnLaunchTemplate.EbsProperty.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-kmskeyid
        Stability:
            stable
        """

        snapshotId: str
        """``CfnLaunchTemplate.EbsProperty.SnapshotId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-snapshotid
        Stability:
            stable
        """

        volumeSize: jsii.Number
        """``CfnLaunchTemplate.EbsProperty.VolumeSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-volumesize
        Stability:
            stable
        """

        volumeType: str
        """``CfnLaunchTemplate.EbsProperty.VolumeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-volumetype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.ElasticGpuSpecificationProperty", jsii_struct_bases=[])
    class ElasticGpuSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-elasticgpuspecification.html
        Stability:
            stable
        """
        type: str
        """``CfnLaunchTemplate.ElasticGpuSpecificationProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-elasticgpuspecification.html#cfn-ec2-launchtemplate-elasticgpuspecification-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.HibernationOptionsProperty", jsii_struct_bases=[])
    class HibernationOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-hibernationoptions.html
        Stability:
            stable
        """
        configured: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnLaunchTemplate.HibernationOptionsProperty.Configured``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-hibernationoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-hibernationoptions-configured
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.IamInstanceProfileProperty", jsii_struct_bases=[])
    class IamInstanceProfileProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-iaminstanceprofile.html
        Stability:
            stable
        """
        arn: str
        """``CfnLaunchTemplate.IamInstanceProfileProperty.Arn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-iaminstanceprofile.html#cfn-ec2-launchtemplate-launchtemplatedata-iaminstanceprofile-arn
        Stability:
            stable
        """

        name: str
        """``CfnLaunchTemplate.IamInstanceProfileProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-iaminstanceprofile.html#cfn-ec2-launchtemplate-launchtemplatedata-iaminstanceprofile-name
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.InstanceMarketOptionsProperty", jsii_struct_bases=[])
    class InstanceMarketOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions.html
        Stability:
            stable
        """
        marketType: str
        """``CfnLaunchTemplate.InstanceMarketOptionsProperty.MarketType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-markettype
        Stability:
            stable
        """

        spotOptions: typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.SpotOptionsProperty"]
        """``CfnLaunchTemplate.InstanceMarketOptionsProperty.SpotOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.Ipv6AddProperty", jsii_struct_bases=[])
    class Ipv6AddProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-ipv6add.html
        Stability:
            stable
        """
        ipv6Address: str
        """``CfnLaunchTemplate.Ipv6AddProperty.Ipv6Address``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-ipv6add.html#cfn-ec2-launchtemplate-ipv6add-ipv6address
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.LaunchTemplateDataProperty", jsii_struct_bases=[])
    class LaunchTemplateDataProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html
        Stability:
            stable
        """
        blockDeviceMappings: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.BlockDeviceMappingProperty"]]]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.BlockDeviceMappings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-blockdevicemappings
        Stability:
            stable
        """

        capacityReservationSpecification: typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.CapacityReservationSpecificationProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.CapacityReservationSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-capacityreservationspecification
        Stability:
            stable
        """

        cpuOptions: typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.CpuOptionsProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.CpuOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-cpuoptions
        Stability:
            stable
        """

        creditSpecification: typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.CreditSpecificationProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.CreditSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-creditspecification
        Stability:
            stable
        """

        disableApiTermination: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.DisableApiTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-disableapitermination
        Stability:
            stable
        """

        ebsOptimized: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.EbsOptimized``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-ebsoptimized
        Stability:
            stable
        """

        elasticGpuSpecifications: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.ElasticGpuSpecificationProperty"]]]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.ElasticGpuSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-elasticgpuspecifications
        Stability:
            stable
        """

        elasticInferenceAccelerators: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.LaunchTemplateElasticInferenceAcceleratorProperty"]]]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.ElasticInferenceAccelerators``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-elasticinferenceaccelerators
        Stability:
            stable
        """

        hibernationOptions: typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.HibernationOptionsProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.HibernationOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-hibernationoptions
        Stability:
            stable
        """

        iamInstanceProfile: typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.IamInstanceProfileProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.IamInstanceProfile``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-iaminstanceprofile
        Stability:
            stable
        """

        imageId: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.ImageId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-imageid
        Stability:
            stable
        """

        instanceInitiatedShutdownBehavior: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.InstanceInitiatedShutdownBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-instanceinitiatedshutdownbehavior
        Stability:
            stable
        """

        instanceMarketOptions: typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.InstanceMarketOptionsProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.InstanceMarketOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-instancemarketoptions
        Stability:
            stable
        """

        instanceType: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-instancetype
        Stability:
            stable
        """

        kernelId: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.KernelId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-kernelid
        Stability:
            stable
        """

        keyName: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.KeyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-keyname
        Stability:
            stable
        """

        licenseSpecifications: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.LicenseSpecificationProperty"]]]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.LicenseSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-licensespecifications
        Stability:
            stable
        """

        monitoring: typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.MonitoringProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.Monitoring``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-monitoring
        Stability:
            stable
        """

        networkInterfaces: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.NetworkInterfaceProperty"]]]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.NetworkInterfaces``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-networkinterfaces
        Stability:
            stable
        """

        placement: typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.PlacementProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.Placement``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-placement
        Stability:
            stable
        """

        ramDiskId: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.RamDiskId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-ramdiskid
        Stability:
            stable
        """

        securityGroupIds: typing.List[str]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-securitygroupids
        Stability:
            stable
        """

        securityGroups: typing.List[str]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.SecurityGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-securitygroups
        Stability:
            stable
        """

        tagSpecifications: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.TagSpecificationProperty"]]]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.TagSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-tagspecifications
        Stability:
            stable
        """

        userData: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.UserData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-userdata
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.LaunchTemplateElasticInferenceAcceleratorProperty", jsii_struct_bases=[])
    class LaunchTemplateElasticInferenceAcceleratorProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplateelasticinferenceaccelerator.html
        Stability:
            stable
        """
        type: str
        """``CfnLaunchTemplate.LaunchTemplateElasticInferenceAcceleratorProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplateelasticinferenceaccelerator.html#cfn-ec2-launchtemplate-launchtemplateelasticinferenceaccelerator-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.LicenseSpecificationProperty", jsii_struct_bases=[])
    class LicenseSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-licensespecification.html
        Stability:
            stable
        """
        licenseConfigurationArn: str
        """``CfnLaunchTemplate.LicenseSpecificationProperty.LicenseConfigurationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-licensespecification.html#cfn-ec2-launchtemplate-licensespecification-licenseconfigurationarn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.MonitoringProperty", jsii_struct_bases=[])
    class MonitoringProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-monitoring.html
        Stability:
            stable
        """
        enabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnLaunchTemplate.MonitoringProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-monitoring.html#cfn-ec2-launchtemplate-launchtemplatedata-monitoring-enabled
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.NetworkInterfaceProperty", jsii_struct_bases=[])
    class NetworkInterfaceProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html
        Stability:
            stable
        """
        associatePublicIpAddress: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.AssociatePublicIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-associatepublicipaddress
        Stability:
            stable
        """

        deleteOnTermination: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-deleteontermination
        Stability:
            stable
        """

        description: str
        """``CfnLaunchTemplate.NetworkInterfaceProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-description
        Stability:
            stable
        """

        deviceIndex: jsii.Number
        """``CfnLaunchTemplate.NetworkInterfaceProperty.DeviceIndex``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-deviceindex
        Stability:
            stable
        """

        groups: typing.List[str]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.Groups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-groups
        Stability:
            stable
        """

        interfaceType: str
        """``CfnLaunchTemplate.NetworkInterfaceProperty.InterfaceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-interfacetype
        Stability:
            stable
        """

        ipv6AddressCount: jsii.Number
        """``CfnLaunchTemplate.NetworkInterfaceProperty.Ipv6AddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-ipv6addresscount
        Stability:
            stable
        """

        ipv6Addresses: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.Ipv6AddProperty"]]]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.Ipv6Addresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-ipv6addresses
        Stability:
            stable
        """

        networkInterfaceId: str
        """``CfnLaunchTemplate.NetworkInterfaceProperty.NetworkInterfaceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-networkinterfaceid
        Stability:
            stable
        """

        privateIpAddress: str
        """``CfnLaunchTemplate.NetworkInterfaceProperty.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-privateipaddress
        Stability:
            stable
        """

        privateIpAddresses: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.PrivateIpAddProperty"]]]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.PrivateIpAddresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-privateipaddresses
        Stability:
            stable
        """

        secondaryPrivateIpAddressCount: jsii.Number
        """``CfnLaunchTemplate.NetworkInterfaceProperty.SecondaryPrivateIpAddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-secondaryprivateipaddresscount
        Stability:
            stable
        """

        subnetId: str
        """``CfnLaunchTemplate.NetworkInterfaceProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-subnetid
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.PlacementProperty", jsii_struct_bases=[])
    class PlacementProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-placement.html
        Stability:
            stable
        """
        affinity: str
        """``CfnLaunchTemplate.PlacementProperty.Affinity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-placement.html#cfn-ec2-launchtemplate-launchtemplatedata-placement-affinity
        Stability:
            stable
        """

        availabilityZone: str
        """``CfnLaunchTemplate.PlacementProperty.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-placement.html#cfn-ec2-launchtemplate-launchtemplatedata-placement-availabilityzone
        Stability:
            stable
        """

        groupName: str
        """``CfnLaunchTemplate.PlacementProperty.GroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-placement.html#cfn-ec2-launchtemplate-launchtemplatedata-placement-groupname
        Stability:
            stable
        """

        hostId: str
        """``CfnLaunchTemplate.PlacementProperty.HostId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-placement.html#cfn-ec2-launchtemplate-launchtemplatedata-placement-hostid
        Stability:
            stable
        """

        tenancy: str
        """``CfnLaunchTemplate.PlacementProperty.Tenancy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-placement.html#cfn-ec2-launchtemplate-launchtemplatedata-placement-tenancy
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.PrivateIpAddProperty", jsii_struct_bases=[])
    class PrivateIpAddProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-privateipadd.html
        Stability:
            stable
        """
        primary: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnLaunchTemplate.PrivateIpAddProperty.Primary``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-privateipadd.html#cfn-ec2-launchtemplate-privateipadd-primary
        Stability:
            stable
        """

        privateIpAddress: str
        """``CfnLaunchTemplate.PrivateIpAddProperty.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-privateipadd.html#cfn-ec2-launchtemplate-privateipadd-privateipaddress
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.SpotOptionsProperty", jsii_struct_bases=[])
    class SpotOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions.html
        Stability:
            stable
        """
        instanceInterruptionBehavior: str
        """``CfnLaunchTemplate.SpotOptionsProperty.InstanceInterruptionBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions-instanceinterruptionbehavior
        Stability:
            stable
        """

        maxPrice: str
        """``CfnLaunchTemplate.SpotOptionsProperty.MaxPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions-maxprice
        Stability:
            stable
        """

        spotInstanceType: str
        """``CfnLaunchTemplate.SpotOptionsProperty.SpotInstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions-spotinstancetype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.TagSpecificationProperty", jsii_struct_bases=[])
    class TagSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-tagspecification.html
        Stability:
            stable
        """
        resourceType: str
        """``CfnLaunchTemplate.TagSpecificationProperty.ResourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-tagspecification.html#cfn-ec2-launchtemplate-tagspecification-resourcetype
        Stability:
            stable
        """

        tags: typing.List[aws_cdk.core.CfnTag]
        """``CfnLaunchTemplate.TagSpecificationProperty.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-tagspecification.html#cfn-ec2-launchtemplate-tagspecification-tags
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplateProps", jsii_struct_bases=[])
class CfnLaunchTemplateProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::LaunchTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-launchtemplate.html
    Stability:
        stable
    """
    launchTemplateData: typing.Union[aws_cdk.core.IResolvable, "CfnLaunchTemplate.LaunchTemplateDataProperty"]
    """``AWS::EC2::LaunchTemplate.LaunchTemplateData``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-launchtemplate.html#cfn-ec2-launchtemplate-launchtemplatedata
    Stability:
        stable
    """

    launchTemplateName: str
    """``AWS::EC2::LaunchTemplate.LaunchTemplateName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-launchtemplate.html#cfn-ec2-launchtemplate-launchtemplatename
    Stability:
        stable
    """

class CfnNatGateway(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnNatGateway"):
    """A CloudFormation ``AWS::EC2::NatGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::NatGateway
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, allocation_id: str, subnet_id: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::NatGateway``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            allocation_id: ``AWS::EC2::NatGateway.AllocationId``.
            subnet_id: ``AWS::EC2::NatGateway.SubnetId``.
            tags: ``AWS::EC2::NatGateway.Tags``.

        Stability:
            experimental
        """
        props: CfnNatGatewayProps = {"allocationId": allocation_id, "subnetId": subnet_id}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnNatGateway, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::NatGateway.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html#cfn-ec2-natgateway-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="allocationId")
    def allocation_id(self) -> str:
        """``AWS::EC2::NatGateway.AllocationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html#cfn-ec2-natgateway-allocationid
        Stability:
            stable
        """
        return jsii.get(self, "allocationId")

    @allocation_id.setter
    def allocation_id(self, value: str):
        return jsii.set(self, "allocationId", value)

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        """``AWS::EC2::NatGateway.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html#cfn-ec2-natgateway-subnetid
        Stability:
            stable
        """
        return jsii.get(self, "subnetId")

    @subnet_id.setter
    def subnet_id(self, value: str):
        return jsii.set(self, "subnetId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnNatGatewayProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::NatGateway.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html#cfn-ec2-natgateway-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNatGatewayProps", jsii_struct_bases=[_CfnNatGatewayProps])
class CfnNatGatewayProps(_CfnNatGatewayProps):
    """Properties for defining a ``AWS::EC2::NatGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html
    Stability:
        stable
    """
    allocationId: str
    """``AWS::EC2::NatGateway.AllocationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html#cfn-ec2-natgateway-allocationid
    Stability:
        stable
    """

    subnetId: str
    """``AWS::EC2::NatGateway.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html#cfn-ec2-natgateway-subnetid
    Stability:
        stable
    """

class CfnNetworkAcl(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnNetworkAcl"):
    """A CloudFormation ``AWS::EC2::NetworkAcl``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::NetworkAcl
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, vpc_id: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::NetworkAcl``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            vpc_id: ``AWS::EC2::NetworkAcl.VpcId``.
            tags: ``AWS::EC2::NetworkAcl.Tags``.

        Stability:
            experimental
        """
        props: CfnNetworkAclProps = {"vpcId": vpc_id}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnNetworkAcl, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::NetworkAcl.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl.html#cfn-ec2-networkacl-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """``AWS::EC2::NetworkAcl.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl.html#cfn-ec2-networkacl-vpcid
        Stability:
            stable
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: str):
        return jsii.set(self, "vpcId", value)


class CfnNetworkAclEntry(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnNetworkAclEntry"):
    """A CloudFormation ``AWS::EC2::NetworkAclEntry``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::NetworkAclEntry
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, network_acl_id: str, protocol: jsii.Number, rule_action: str, rule_number: jsii.Number, cidr_block: typing.Optional[str]=None, egress: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, icmp: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["IcmpProperty"]]]=None, ipv6_cidr_block: typing.Optional[str]=None, port_range: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PortRangeProperty"]]]=None) -> None:
        """Create a new ``AWS::EC2::NetworkAclEntry``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            network_acl_id: ``AWS::EC2::NetworkAclEntry.NetworkAclId``.
            protocol: ``AWS::EC2::NetworkAclEntry.Protocol``.
            rule_action: ``AWS::EC2::NetworkAclEntry.RuleAction``.
            rule_number: ``AWS::EC2::NetworkAclEntry.RuleNumber``.
            cidr_block: ``AWS::EC2::NetworkAclEntry.CidrBlock``.
            egress: ``AWS::EC2::NetworkAclEntry.Egress``.
            icmp: ``AWS::EC2::NetworkAclEntry.Icmp``.
            ipv6_cidr_block: ``AWS::EC2::NetworkAclEntry.Ipv6CidrBlock``.
            port_range: ``AWS::EC2::NetworkAclEntry.PortRange``.

        Stability:
            experimental
        """
        props: CfnNetworkAclEntryProps = {"networkAclId": network_acl_id, "protocol": protocol, "ruleAction": rule_action, "ruleNumber": rule_number}

        if cidr_block is not None:
            props["cidrBlock"] = cidr_block

        if egress is not None:
            props["egress"] = egress

        if icmp is not None:
            props["icmp"] = icmp

        if ipv6_cidr_block is not None:
            props["ipv6CidrBlock"] = ipv6_cidr_block

        if port_range is not None:
            props["portRange"] = port_range

        jsii.create(CfnNetworkAclEntry, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="networkAclId")
    def network_acl_id(self) -> str:
        """``AWS::EC2::NetworkAclEntry.NetworkAclId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-networkaclid
        Stability:
            stable
        """
        return jsii.get(self, "networkAclId")

    @network_acl_id.setter
    def network_acl_id(self, value: str):
        return jsii.set(self, "networkAclId", value)

    @property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> jsii.Number:
        """``AWS::EC2::NetworkAclEntry.Protocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-protocol
        Stability:
            stable
        """
        return jsii.get(self, "protocol")

    @protocol.setter
    def protocol(self, value: jsii.Number):
        return jsii.set(self, "protocol", value)

    @property
    @jsii.member(jsii_name="ruleAction")
    def rule_action(self) -> str:
        """``AWS::EC2::NetworkAclEntry.RuleAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-ruleaction
        Stability:
            stable
        """
        return jsii.get(self, "ruleAction")

    @rule_action.setter
    def rule_action(self, value: str):
        return jsii.set(self, "ruleAction", value)

    @property
    @jsii.member(jsii_name="ruleNumber")
    def rule_number(self) -> jsii.Number:
        """``AWS::EC2::NetworkAclEntry.RuleNumber``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-rulenumber
        Stability:
            stable
        """
        return jsii.get(self, "ruleNumber")

    @rule_number.setter
    def rule_number(self, value: jsii.Number):
        return jsii.set(self, "ruleNumber", value)

    @property
    @jsii.member(jsii_name="cidrBlock")
    def cidr_block(self) -> typing.Optional[str]:
        """``AWS::EC2::NetworkAclEntry.CidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-cidrblock
        Stability:
            stable
        """
        return jsii.get(self, "cidrBlock")

    @cidr_block.setter
    def cidr_block(self, value: typing.Optional[str]):
        return jsii.set(self, "cidrBlock", value)

    @property
    @jsii.member(jsii_name="egress")
    def egress(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::NetworkAclEntry.Egress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-egress
        Stability:
            stable
        """
        return jsii.get(self, "egress")

    @egress.setter
    def egress(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "egress", value)

    @property
    @jsii.member(jsii_name="icmp")
    def icmp(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["IcmpProperty"]]]:
        """``AWS::EC2::NetworkAclEntry.Icmp``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-icmp
        Stability:
            stable
        """
        return jsii.get(self, "icmp")

    @icmp.setter
    def icmp(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["IcmpProperty"]]]):
        return jsii.set(self, "icmp", value)

    @property
    @jsii.member(jsii_name="ipv6CidrBlock")
    def ipv6_cidr_block(self) -> typing.Optional[str]:
        """``AWS::EC2::NetworkAclEntry.Ipv6CidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-ipv6cidrblock
        Stability:
            stable
        """
        return jsii.get(self, "ipv6CidrBlock")

    @ipv6_cidr_block.setter
    def ipv6_cidr_block(self, value: typing.Optional[str]):
        return jsii.set(self, "ipv6CidrBlock", value)

    @property
    @jsii.member(jsii_name="portRange")
    def port_range(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PortRangeProperty"]]]:
        """``AWS::EC2::NetworkAclEntry.PortRange``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-portrange
        Stability:
            stable
        """
        return jsii.get(self, "portRange")

    @port_range.setter
    def port_range(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PortRangeProperty"]]]):
        return jsii.set(self, "portRange", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkAclEntry.IcmpProperty", jsii_struct_bases=[])
    class IcmpProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkaclentry-icmp.html
        Stability:
            stable
        """
        code: jsii.Number
        """``CfnNetworkAclEntry.IcmpProperty.Code``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkaclentry-icmp.html#cfn-ec2-networkaclentry-icmp-code
        Stability:
            stable
        """

        type: jsii.Number
        """``CfnNetworkAclEntry.IcmpProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkaclentry-icmp.html#cfn-ec2-networkaclentry-icmp-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkAclEntry.PortRangeProperty", jsii_struct_bases=[])
    class PortRangeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkaclentry-portrange.html
        Stability:
            stable
        """
        from_: jsii.Number
        """``CfnNetworkAclEntry.PortRangeProperty.From``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkaclentry-portrange.html#cfn-ec2-networkaclentry-portrange-from
        Stability:
            stable
        """

        to: jsii.Number
        """``CfnNetworkAclEntry.PortRangeProperty.To``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkaclentry-portrange.html#cfn-ec2-networkaclentry-portrange-to
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnNetworkAclEntryProps(jsii.compat.TypedDict, total=False):
    cidrBlock: str
    """``AWS::EC2::NetworkAclEntry.CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-cidrblock
    Stability:
        stable
    """
    egress: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::NetworkAclEntry.Egress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-egress
    Stability:
        stable
    """
    icmp: typing.Union[aws_cdk.core.IResolvable, "CfnNetworkAclEntry.IcmpProperty"]
    """``AWS::EC2::NetworkAclEntry.Icmp``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-icmp
    Stability:
        stable
    """
    ipv6CidrBlock: str
    """``AWS::EC2::NetworkAclEntry.Ipv6CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-ipv6cidrblock
    Stability:
        stable
    """
    portRange: typing.Union[aws_cdk.core.IResolvable, "CfnNetworkAclEntry.PortRangeProperty"]
    """``AWS::EC2::NetworkAclEntry.PortRange``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-portrange
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkAclEntryProps", jsii_struct_bases=[_CfnNetworkAclEntryProps])
class CfnNetworkAclEntryProps(_CfnNetworkAclEntryProps):
    """Properties for defining a ``AWS::EC2::NetworkAclEntry``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html
    Stability:
        stable
    """
    networkAclId: str
    """``AWS::EC2::NetworkAclEntry.NetworkAclId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-networkaclid
    Stability:
        stable
    """

    protocol: jsii.Number
    """``AWS::EC2::NetworkAclEntry.Protocol``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-protocol
    Stability:
        stable
    """

    ruleAction: str
    """``AWS::EC2::NetworkAclEntry.RuleAction``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-ruleaction
    Stability:
        stable
    """

    ruleNumber: jsii.Number
    """``AWS::EC2::NetworkAclEntry.RuleNumber``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-rulenumber
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnNetworkAclProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::NetworkAcl.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl.html#cfn-ec2-networkacl-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkAclProps", jsii_struct_bases=[_CfnNetworkAclProps])
class CfnNetworkAclProps(_CfnNetworkAclProps):
    """Properties for defining a ``AWS::EC2::NetworkAcl``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl.html
    Stability:
        stable
    """
    vpcId: str
    """``AWS::EC2::NetworkAcl.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl.html#cfn-ec2-networkacl-vpcid
    Stability:
        stable
    """

class CfnNetworkInterface(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterface"):
    """A CloudFormation ``AWS::EC2::NetworkInterface``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::NetworkInterface
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, subnet_id: str, description: typing.Optional[str]=None, group_set: typing.Optional[typing.List[str]]=None, interface_type: typing.Optional[str]=None, ipv6_address_count: typing.Optional[jsii.Number]=None, ipv6_addresses: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["InstanceIpv6AddressProperty"]]]=None, private_ip_address: typing.Optional[str]=None, private_ip_addresses: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PrivateIpAddressSpecificationProperty"]]]]]=None, secondary_private_ip_address_count: typing.Optional[jsii.Number]=None, source_dest_check: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::NetworkInterface``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            subnet_id: ``AWS::EC2::NetworkInterface.SubnetId``.
            description: ``AWS::EC2::NetworkInterface.Description``.
            group_set: ``AWS::EC2::NetworkInterface.GroupSet``.
            interface_type: ``AWS::EC2::NetworkInterface.InterfaceType``.
            ipv6_address_count: ``AWS::EC2::NetworkInterface.Ipv6AddressCount``.
            ipv6_addresses: ``AWS::EC2::NetworkInterface.Ipv6Addresses``.
            private_ip_address: ``AWS::EC2::NetworkInterface.PrivateIpAddress``.
            private_ip_addresses: ``AWS::EC2::NetworkInterface.PrivateIpAddresses``.
            secondary_private_ip_address_count: ``AWS::EC2::NetworkInterface.SecondaryPrivateIpAddressCount``.
            source_dest_check: ``AWS::EC2::NetworkInterface.SourceDestCheck``.
            tags: ``AWS::EC2::NetworkInterface.Tags``.

        Stability:
            experimental
        """
        props: CfnNetworkInterfaceProps = {"subnetId": subnet_id}

        if description is not None:
            props["description"] = description

        if group_set is not None:
            props["groupSet"] = group_set

        if interface_type is not None:
            props["interfaceType"] = interface_type

        if ipv6_address_count is not None:
            props["ipv6AddressCount"] = ipv6_address_count

        if ipv6_addresses is not None:
            props["ipv6Addresses"] = ipv6_addresses

        if private_ip_address is not None:
            props["privateIpAddress"] = private_ip_address

        if private_ip_addresses is not None:
            props["privateIpAddresses"] = private_ip_addresses

        if secondary_private_ip_address_count is not None:
            props["secondaryPrivateIpAddressCount"] = secondary_private_ip_address_count

        if source_dest_check is not None:
            props["sourceDestCheck"] = source_dest_check

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnNetworkInterface, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrPrimaryPrivateIpAddress")
    def attr_primary_private_ip_address(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            PrimaryPrivateIpAddress
        """
        return jsii.get(self, "attrPrimaryPrivateIpAddress")

    @property
    @jsii.member(jsii_name="attrSecondaryPrivateIpAddresses")
    def attr_secondary_private_ip_addresses(self) -> typing.List[str]:
        """
        Stability:
            stable
        cloudformationAttribute:
            SecondaryPrivateIpAddresses
        """
        return jsii.get(self, "attrSecondaryPrivateIpAddresses")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::NetworkInterface.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        """``AWS::EC2::NetworkInterface.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-subnetid
        Stability:
            stable
        """
        return jsii.get(self, "subnetId")

    @subnet_id.setter
    def subnet_id(self, value: str):
        return jsii.set(self, "subnetId", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::EC2::NetworkInterface.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="groupSet")
    def group_set(self) -> typing.Optional[typing.List[str]]:
        """``AWS::EC2::NetworkInterface.GroupSet``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-groupset
        Stability:
            stable
        """
        return jsii.get(self, "groupSet")

    @group_set.setter
    def group_set(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "groupSet", value)

    @property
    @jsii.member(jsii_name="interfaceType")
    def interface_type(self) -> typing.Optional[str]:
        """``AWS::EC2::NetworkInterface.InterfaceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-ec2-networkinterface-interfacetype
        Stability:
            stable
        """
        return jsii.get(self, "interfaceType")

    @interface_type.setter
    def interface_type(self, value: typing.Optional[str]):
        return jsii.set(self, "interfaceType", value)

    @property
    @jsii.member(jsii_name="ipv6AddressCount")
    def ipv6_address_count(self) -> typing.Optional[jsii.Number]:
        """``AWS::EC2::NetworkInterface.Ipv6AddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-ec2-networkinterface-ipv6addresscount
        Stability:
            stable
        """
        return jsii.get(self, "ipv6AddressCount")

    @ipv6_address_count.setter
    def ipv6_address_count(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "ipv6AddressCount", value)

    @property
    @jsii.member(jsii_name="ipv6Addresses")
    def ipv6_addresses(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["InstanceIpv6AddressProperty"]]]:
        """``AWS::EC2::NetworkInterface.Ipv6Addresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-ec2-networkinterface-ipv6addresses
        Stability:
            stable
        """
        return jsii.get(self, "ipv6Addresses")

    @ipv6_addresses.setter
    def ipv6_addresses(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["InstanceIpv6AddressProperty"]]]):
        return jsii.set(self, "ipv6Addresses", value)

    @property
    @jsii.member(jsii_name="privateIpAddress")
    def private_ip_address(self) -> typing.Optional[str]:
        """``AWS::EC2::NetworkInterface.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-privateipaddress
        Stability:
            stable
        """
        return jsii.get(self, "privateIpAddress")

    @private_ip_address.setter
    def private_ip_address(self, value: typing.Optional[str]):
        return jsii.set(self, "privateIpAddress", value)

    @property
    @jsii.member(jsii_name="privateIpAddresses")
    def private_ip_addresses(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PrivateIpAddressSpecificationProperty"]]]]]:
        """``AWS::EC2::NetworkInterface.PrivateIpAddresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-privateipaddresses
        Stability:
            stable
        """
        return jsii.get(self, "privateIpAddresses")

    @private_ip_addresses.setter
    def private_ip_addresses(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PrivateIpAddressSpecificationProperty"]]]]]):
        return jsii.set(self, "privateIpAddresses", value)

    @property
    @jsii.member(jsii_name="secondaryPrivateIpAddressCount")
    def secondary_private_ip_address_count(self) -> typing.Optional[jsii.Number]:
        """``AWS::EC2::NetworkInterface.SecondaryPrivateIpAddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-secondaryprivateipcount
        Stability:
            stable
        """
        return jsii.get(self, "secondaryPrivateIpAddressCount")

    @secondary_private_ip_address_count.setter
    def secondary_private_ip_address_count(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "secondaryPrivateIpAddressCount", value)

    @property
    @jsii.member(jsii_name="sourceDestCheck")
    def source_dest_check(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::NetworkInterface.SourceDestCheck``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-sourcedestcheck
        Stability:
            stable
        """
        return jsii.get(self, "sourceDestCheck")

    @source_dest_check.setter
    def source_dest_check(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "sourceDestCheck", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterface.InstanceIpv6AddressProperty", jsii_struct_bases=[])
    class InstanceIpv6AddressProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkinterface-instanceipv6address.html
        Stability:
            stable
        """
        ipv6Address: str
        """``CfnNetworkInterface.InstanceIpv6AddressProperty.Ipv6Address``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkinterface-instanceipv6address.html#cfn-ec2-networkinterface-instanceipv6address-ipv6address
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterface.PrivateIpAddressSpecificationProperty", jsii_struct_bases=[])
    class PrivateIpAddressSpecificationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-interface-privateipspec.html
        Stability:
            stable
        """
        primary: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnNetworkInterface.PrivateIpAddressSpecificationProperty.Primary``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-interface-privateipspec.html#cfn-ec2-networkinterface-privateipspecification-primary
        Stability:
            stable
        """

        privateIpAddress: str
        """``CfnNetworkInterface.PrivateIpAddressSpecificationProperty.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-interface-privateipspec.html#cfn-ec2-networkinterface-privateipspecification-privateipaddress
        Stability:
            stable
        """


class CfnNetworkInterfaceAttachment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterfaceAttachment"):
    """A CloudFormation ``AWS::EC2::NetworkInterfaceAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::NetworkInterfaceAttachment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, device_index: str, instance_id: str, network_interface_id: str, delete_on_termination: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::EC2::NetworkInterfaceAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            device_index: ``AWS::EC2::NetworkInterfaceAttachment.DeviceIndex``.
            instance_id: ``AWS::EC2::NetworkInterfaceAttachment.InstanceId``.
            network_interface_id: ``AWS::EC2::NetworkInterfaceAttachment.NetworkInterfaceId``.
            delete_on_termination: ``AWS::EC2::NetworkInterfaceAttachment.DeleteOnTermination``.

        Stability:
            experimental
        """
        props: CfnNetworkInterfaceAttachmentProps = {"deviceIndex": device_index, "instanceId": instance_id, "networkInterfaceId": network_interface_id}

        if delete_on_termination is not None:
            props["deleteOnTermination"] = delete_on_termination

        jsii.create(CfnNetworkInterfaceAttachment, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="deviceIndex")
    def device_index(self) -> str:
        """``AWS::EC2::NetworkInterfaceAttachment.DeviceIndex``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html#cfn-ec2-network-interface-attachment-deviceindex
        Stability:
            stable
        """
        return jsii.get(self, "deviceIndex")

    @device_index.setter
    def device_index(self, value: str):
        return jsii.set(self, "deviceIndex", value)

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> str:
        """``AWS::EC2::NetworkInterfaceAttachment.InstanceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html#cfn-ec2-network-interface-attachment-instanceid
        Stability:
            stable
        """
        return jsii.get(self, "instanceId")

    @instance_id.setter
    def instance_id(self, value: str):
        return jsii.set(self, "instanceId", value)

    @property
    @jsii.member(jsii_name="networkInterfaceId")
    def network_interface_id(self) -> str:
        """``AWS::EC2::NetworkInterfaceAttachment.NetworkInterfaceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html#cfn-ec2-network-interface-attachment-networkinterfaceid
        Stability:
            stable
        """
        return jsii.get(self, "networkInterfaceId")

    @network_interface_id.setter
    def network_interface_id(self, value: str):
        return jsii.set(self, "networkInterfaceId", value)

    @property
    @jsii.member(jsii_name="deleteOnTermination")
    def delete_on_termination(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::NetworkInterfaceAttachment.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html#cfn-ec2-network-interface-attachment-deleteonterm
        Stability:
            stable
        """
        return jsii.get(self, "deleteOnTermination")

    @delete_on_termination.setter
    def delete_on_termination(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "deleteOnTermination", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnNetworkInterfaceAttachmentProps(jsii.compat.TypedDict, total=False):
    deleteOnTermination: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::NetworkInterfaceAttachment.DeleteOnTermination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html#cfn-ec2-network-interface-attachment-deleteonterm
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterfaceAttachmentProps", jsii_struct_bases=[_CfnNetworkInterfaceAttachmentProps])
class CfnNetworkInterfaceAttachmentProps(_CfnNetworkInterfaceAttachmentProps):
    """Properties for defining a ``AWS::EC2::NetworkInterfaceAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html
    Stability:
        stable
    """
    deviceIndex: str
    """``AWS::EC2::NetworkInterfaceAttachment.DeviceIndex``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html#cfn-ec2-network-interface-attachment-deviceindex
    Stability:
        stable
    """

    instanceId: str
    """``AWS::EC2::NetworkInterfaceAttachment.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html#cfn-ec2-network-interface-attachment-instanceid
    Stability:
        stable
    """

    networkInterfaceId: str
    """``AWS::EC2::NetworkInterfaceAttachment.NetworkInterfaceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html#cfn-ec2-network-interface-attachment-networkinterfaceid
    Stability:
        stable
    """

class CfnNetworkInterfacePermission(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterfacePermission"):
    """A CloudFormation ``AWS::EC2::NetworkInterfacePermission``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::NetworkInterfacePermission
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, aws_account_id: str, network_interface_id: str, permission: str) -> None:
        """Create a new ``AWS::EC2::NetworkInterfacePermission``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            aws_account_id: ``AWS::EC2::NetworkInterfacePermission.AwsAccountId``.
            network_interface_id: ``AWS::EC2::NetworkInterfacePermission.NetworkInterfaceId``.
            permission: ``AWS::EC2::NetworkInterfacePermission.Permission``.

        Stability:
            experimental
        """
        props: CfnNetworkInterfacePermissionProps = {"awsAccountId": aws_account_id, "networkInterfaceId": network_interface_id, "permission": permission}

        jsii.create(CfnNetworkInterfacePermission, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="awsAccountId")
    def aws_account_id(self) -> str:
        """``AWS::EC2::NetworkInterfacePermission.AwsAccountId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html#cfn-ec2-networkinterfacepermission-awsaccountid
        Stability:
            stable
        """
        return jsii.get(self, "awsAccountId")

    @aws_account_id.setter
    def aws_account_id(self, value: str):
        return jsii.set(self, "awsAccountId", value)

    @property
    @jsii.member(jsii_name="networkInterfaceId")
    def network_interface_id(self) -> str:
        """``AWS::EC2::NetworkInterfacePermission.NetworkInterfaceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html#cfn-ec2-networkinterfacepermission-networkinterfaceid
        Stability:
            stable
        """
        return jsii.get(self, "networkInterfaceId")

    @network_interface_id.setter
    def network_interface_id(self, value: str):
        return jsii.set(self, "networkInterfaceId", value)

    @property
    @jsii.member(jsii_name="permission")
    def permission(self) -> str:
        """``AWS::EC2::NetworkInterfacePermission.Permission``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html#cfn-ec2-networkinterfacepermission-permission
        Stability:
            stable
        """
        return jsii.get(self, "permission")

    @permission.setter
    def permission(self, value: str):
        return jsii.set(self, "permission", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterfacePermissionProps", jsii_struct_bases=[])
class CfnNetworkInterfacePermissionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::NetworkInterfacePermission``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html
    Stability:
        stable
    """
    awsAccountId: str
    """``AWS::EC2::NetworkInterfacePermission.AwsAccountId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html#cfn-ec2-networkinterfacepermission-awsaccountid
    Stability:
        stable
    """

    networkInterfaceId: str
    """``AWS::EC2::NetworkInterfacePermission.NetworkInterfaceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html#cfn-ec2-networkinterfacepermission-networkinterfaceid
    Stability:
        stable
    """

    permission: str
    """``AWS::EC2::NetworkInterfacePermission.Permission``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html#cfn-ec2-networkinterfacepermission-permission
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnNetworkInterfaceProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::EC2::NetworkInterface.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-description
    Stability:
        stable
    """
    groupSet: typing.List[str]
    """``AWS::EC2::NetworkInterface.GroupSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-groupset
    Stability:
        stable
    """
    interfaceType: str
    """``AWS::EC2::NetworkInterface.InterfaceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-ec2-networkinterface-interfacetype
    Stability:
        stable
    """
    ipv6AddressCount: jsii.Number
    """``AWS::EC2::NetworkInterface.Ipv6AddressCount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-ec2-networkinterface-ipv6addresscount
    Stability:
        stable
    """
    ipv6Addresses: typing.Union[aws_cdk.core.IResolvable, "CfnNetworkInterface.InstanceIpv6AddressProperty"]
    """``AWS::EC2::NetworkInterface.Ipv6Addresses``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-ec2-networkinterface-ipv6addresses
    Stability:
        stable
    """
    privateIpAddress: str
    """``AWS::EC2::NetworkInterface.PrivateIpAddress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-privateipaddress
    Stability:
        stable
    """
    privateIpAddresses: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnNetworkInterface.PrivateIpAddressSpecificationProperty"]]]
    """``AWS::EC2::NetworkInterface.PrivateIpAddresses``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-privateipaddresses
    Stability:
        stable
    """
    secondaryPrivateIpAddressCount: jsii.Number
    """``AWS::EC2::NetworkInterface.SecondaryPrivateIpAddressCount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-secondaryprivateipcount
    Stability:
        stable
    """
    sourceDestCheck: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::NetworkInterface.SourceDestCheck``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-sourcedestcheck
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::NetworkInterface.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterfaceProps", jsii_struct_bases=[_CfnNetworkInterfaceProps])
class CfnNetworkInterfaceProps(_CfnNetworkInterfaceProps):
    """Properties for defining a ``AWS::EC2::NetworkInterface``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html
    Stability:
        stable
    """
    subnetId: str
    """``AWS::EC2::NetworkInterface.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-subnetid
    Stability:
        stable
    """

class CfnPlacementGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnPlacementGroup"):
    """A CloudFormation ``AWS::EC2::PlacementGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-placementgroup.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::PlacementGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, strategy: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::PlacementGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            strategy: ``AWS::EC2::PlacementGroup.Strategy``.

        Stability:
            experimental
        """
        props: CfnPlacementGroupProps = {}

        if strategy is not None:
            props["strategy"] = strategy

        jsii.create(CfnPlacementGroup, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="strategy")
    def strategy(self) -> typing.Optional[str]:
        """``AWS::EC2::PlacementGroup.Strategy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-placementgroup.html#cfn-ec2-placementgroup-strategy
        Stability:
            stable
        """
        return jsii.get(self, "strategy")

    @strategy.setter
    def strategy(self, value: typing.Optional[str]):
        return jsii.set(self, "strategy", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnPlacementGroupProps", jsii_struct_bases=[])
class CfnPlacementGroupProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::PlacementGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-placementgroup.html
    Stability:
        stable
    """
    strategy: str
    """``AWS::EC2::PlacementGroup.Strategy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-placementgroup.html#cfn-ec2-placementgroup-strategy
    Stability:
        stable
    """

class CfnRoute(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnRoute"):
    """A CloudFormation ``AWS::EC2::Route``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::Route
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, route_table_id: str, destination_cidr_block: typing.Optional[str]=None, destination_ipv6_cidr_block: typing.Optional[str]=None, egress_only_internet_gateway_id: typing.Optional[str]=None, gateway_id: typing.Optional[str]=None, instance_id: typing.Optional[str]=None, nat_gateway_id: typing.Optional[str]=None, network_interface_id: typing.Optional[str]=None, transit_gateway_id: typing.Optional[str]=None, vpc_peering_connection_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::Route``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            route_table_id: ``AWS::EC2::Route.RouteTableId``.
            destination_cidr_block: ``AWS::EC2::Route.DestinationCidrBlock``.
            destination_ipv6_cidr_block: ``AWS::EC2::Route.DestinationIpv6CidrBlock``.
            egress_only_internet_gateway_id: ``AWS::EC2::Route.EgressOnlyInternetGatewayId``.
            gateway_id: ``AWS::EC2::Route.GatewayId``.
            instance_id: ``AWS::EC2::Route.InstanceId``.
            nat_gateway_id: ``AWS::EC2::Route.NatGatewayId``.
            network_interface_id: ``AWS::EC2::Route.NetworkInterfaceId``.
            transit_gateway_id: ``AWS::EC2::Route.TransitGatewayId``.
            vpc_peering_connection_id: ``AWS::EC2::Route.VpcPeeringConnectionId``.

        Stability:
            experimental
        """
        props: CfnRouteProps = {"routeTableId": route_table_id}

        if destination_cidr_block is not None:
            props["destinationCidrBlock"] = destination_cidr_block

        if destination_ipv6_cidr_block is not None:
            props["destinationIpv6CidrBlock"] = destination_ipv6_cidr_block

        if egress_only_internet_gateway_id is not None:
            props["egressOnlyInternetGatewayId"] = egress_only_internet_gateway_id

        if gateway_id is not None:
            props["gatewayId"] = gateway_id

        if instance_id is not None:
            props["instanceId"] = instance_id

        if nat_gateway_id is not None:
            props["natGatewayId"] = nat_gateway_id

        if network_interface_id is not None:
            props["networkInterfaceId"] = network_interface_id

        if transit_gateway_id is not None:
            props["transitGatewayId"] = transit_gateway_id

        if vpc_peering_connection_id is not None:
            props["vpcPeeringConnectionId"] = vpc_peering_connection_id

        jsii.create(CfnRoute, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="routeTableId")
    def route_table_id(self) -> str:
        """``AWS::EC2::Route.RouteTableId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-routetableid
        Stability:
            stable
        """
        return jsii.get(self, "routeTableId")

    @route_table_id.setter
    def route_table_id(self, value: str):
        return jsii.set(self, "routeTableId", value)

    @property
    @jsii.member(jsii_name="destinationCidrBlock")
    def destination_cidr_block(self) -> typing.Optional[str]:
        """``AWS::EC2::Route.DestinationCidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-destinationcidrblock
        Stability:
            stable
        """
        return jsii.get(self, "destinationCidrBlock")

    @destination_cidr_block.setter
    def destination_cidr_block(self, value: typing.Optional[str]):
        return jsii.set(self, "destinationCidrBlock", value)

    @property
    @jsii.member(jsii_name="destinationIpv6CidrBlock")
    def destination_ipv6_cidr_block(self) -> typing.Optional[str]:
        """``AWS::EC2::Route.DestinationIpv6CidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-destinationipv6cidrblock
        Stability:
            stable
        """
        return jsii.get(self, "destinationIpv6CidrBlock")

    @destination_ipv6_cidr_block.setter
    def destination_ipv6_cidr_block(self, value: typing.Optional[str]):
        return jsii.set(self, "destinationIpv6CidrBlock", value)

    @property
    @jsii.member(jsii_name="egressOnlyInternetGatewayId")
    def egress_only_internet_gateway_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Route.EgressOnlyInternetGatewayId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-egressonlyinternetgatewayid
        Stability:
            stable
        """
        return jsii.get(self, "egressOnlyInternetGatewayId")

    @egress_only_internet_gateway_id.setter
    def egress_only_internet_gateway_id(self, value: typing.Optional[str]):
        return jsii.set(self, "egressOnlyInternetGatewayId", value)

    @property
    @jsii.member(jsii_name="gatewayId")
    def gateway_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Route.GatewayId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-gatewayid
        Stability:
            stable
        """
        return jsii.get(self, "gatewayId")

    @gateway_id.setter
    def gateway_id(self, value: typing.Optional[str]):
        return jsii.set(self, "gatewayId", value)

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Route.InstanceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-instanceid
        Stability:
            stable
        """
        return jsii.get(self, "instanceId")

    @instance_id.setter
    def instance_id(self, value: typing.Optional[str]):
        return jsii.set(self, "instanceId", value)

    @property
    @jsii.member(jsii_name="natGatewayId")
    def nat_gateway_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Route.NatGatewayId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-natgatewayid
        Stability:
            stable
        """
        return jsii.get(self, "natGatewayId")

    @nat_gateway_id.setter
    def nat_gateway_id(self, value: typing.Optional[str]):
        return jsii.set(self, "natGatewayId", value)

    @property
    @jsii.member(jsii_name="networkInterfaceId")
    def network_interface_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Route.NetworkInterfaceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-networkinterfaceid
        Stability:
            stable
        """
        return jsii.get(self, "networkInterfaceId")

    @network_interface_id.setter
    def network_interface_id(self, value: typing.Optional[str]):
        return jsii.set(self, "networkInterfaceId", value)

    @property
    @jsii.member(jsii_name="transitGatewayId")
    def transit_gateway_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Route.TransitGatewayId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-transitgatewayid
        Stability:
            stable
        """
        return jsii.get(self, "transitGatewayId")

    @transit_gateway_id.setter
    def transit_gateway_id(self, value: typing.Optional[str]):
        return jsii.set(self, "transitGatewayId", value)

    @property
    @jsii.member(jsii_name="vpcPeeringConnectionId")
    def vpc_peering_connection_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Route.VpcPeeringConnectionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-vpcpeeringconnectionid
        Stability:
            stable
        """
        return jsii.get(self, "vpcPeeringConnectionId")

    @vpc_peering_connection_id.setter
    def vpc_peering_connection_id(self, value: typing.Optional[str]):
        return jsii.set(self, "vpcPeeringConnectionId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRouteProps(jsii.compat.TypedDict, total=False):
    destinationCidrBlock: str
    """``AWS::EC2::Route.DestinationCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-destinationcidrblock
    Stability:
        stable
    """
    destinationIpv6CidrBlock: str
    """``AWS::EC2::Route.DestinationIpv6CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-destinationipv6cidrblock
    Stability:
        stable
    """
    egressOnlyInternetGatewayId: str
    """``AWS::EC2::Route.EgressOnlyInternetGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-egressonlyinternetgatewayid
    Stability:
        stable
    """
    gatewayId: str
    """``AWS::EC2::Route.GatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-gatewayid
    Stability:
        stable
    """
    instanceId: str
    """``AWS::EC2::Route.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-instanceid
    Stability:
        stable
    """
    natGatewayId: str
    """``AWS::EC2::Route.NatGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-natgatewayid
    Stability:
        stable
    """
    networkInterfaceId: str
    """``AWS::EC2::Route.NetworkInterfaceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-networkinterfaceid
    Stability:
        stable
    """
    transitGatewayId: str
    """``AWS::EC2::Route.TransitGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-transitgatewayid
    Stability:
        stable
    """
    vpcPeeringConnectionId: str
    """``AWS::EC2::Route.VpcPeeringConnectionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-vpcpeeringconnectionid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnRouteProps", jsii_struct_bases=[_CfnRouteProps])
class CfnRouteProps(_CfnRouteProps):
    """Properties for defining a ``AWS::EC2::Route``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html
    Stability:
        stable
    """
    routeTableId: str
    """``AWS::EC2::Route.RouteTableId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-routetableid
    Stability:
        stable
    """

class CfnRouteTable(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnRouteTable"):
    """A CloudFormation ``AWS::EC2::RouteTable``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route-table.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::RouteTable
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, vpc_id: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::RouteTable``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            vpc_id: ``AWS::EC2::RouteTable.VpcId``.
            tags: ``AWS::EC2::RouteTable.Tags``.

        Stability:
            experimental
        """
        props: CfnRouteTableProps = {"vpcId": vpc_id}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnRouteTable, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::RouteTable.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route-table.html#cfn-ec2-routetable-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """``AWS::EC2::RouteTable.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route-table.html#cfn-ec2-routetable-vpcid
        Stability:
            stable
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: str):
        return jsii.set(self, "vpcId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRouteTableProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::RouteTable.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route-table.html#cfn-ec2-routetable-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnRouteTableProps", jsii_struct_bases=[_CfnRouteTableProps])
class CfnRouteTableProps(_CfnRouteTableProps):
    """Properties for defining a ``AWS::EC2::RouteTable``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route-table.html
    Stability:
        stable
    """
    vpcId: str
    """``AWS::EC2::RouteTable.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route-table.html#cfn-ec2-routetable-vpcid
    Stability:
        stable
    """

class CfnSecurityGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroup"):
    """A CloudFormation ``AWS::EC2::SecurityGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::SecurityGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, group_description: str, group_name: typing.Optional[str]=None, security_group_egress: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "EgressProperty"]]]]]=None, security_group_ingress: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "IngressProperty"]]]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, vpc_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::SecurityGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            group_description: ``AWS::EC2::SecurityGroup.GroupDescription``.
            group_name: ``AWS::EC2::SecurityGroup.GroupName``.
            security_group_egress: ``AWS::EC2::SecurityGroup.SecurityGroupEgress``.
            security_group_ingress: ``AWS::EC2::SecurityGroup.SecurityGroupIngress``.
            tags: ``AWS::EC2::SecurityGroup.Tags``.
            vpc_id: ``AWS::EC2::SecurityGroup.VpcId``.

        Stability:
            experimental
        """
        props: CfnSecurityGroupProps = {"groupDescription": group_description}

        if group_name is not None:
            props["groupName"] = group_name

        if security_group_egress is not None:
            props["securityGroupEgress"] = security_group_egress

        if security_group_ingress is not None:
            props["securityGroupIngress"] = security_group_ingress

        if tags is not None:
            props["tags"] = tags

        if vpc_id is not None:
            props["vpcId"] = vpc_id

        jsii.create(CfnSecurityGroup, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrGroupId")
    def attr_group_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            GroupId
        """
        return jsii.get(self, "attrGroupId")

    @property
    @jsii.member(jsii_name="attrVpcId")
    def attr_vpc_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            VpcId
        """
        return jsii.get(self, "attrVpcId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::SecurityGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="groupDescription")
    def group_description(self) -> str:
        """``AWS::EC2::SecurityGroup.GroupDescription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-groupdescription
        Stability:
            stable
        """
        return jsii.get(self, "groupDescription")

    @group_description.setter
    def group_description(self, value: str):
        return jsii.set(self, "groupDescription", value)

    @property
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroup.GroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-groupname
        Stability:
            stable
        """
        return jsii.get(self, "groupName")

    @group_name.setter
    def group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "groupName", value)

    @property
    @jsii.member(jsii_name="securityGroupEgress")
    def security_group_egress(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "EgressProperty"]]]]]:
        """``AWS::EC2::SecurityGroup.SecurityGroupEgress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-securitygroupegress
        Stability:
            stable
        """
        return jsii.get(self, "securityGroupEgress")

    @security_group_egress.setter
    def security_group_egress(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "EgressProperty"]]]]]):
        return jsii.set(self, "securityGroupEgress", value)

    @property
    @jsii.member(jsii_name="securityGroupIngress")
    def security_group_ingress(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "IngressProperty"]]]]]:
        """``AWS::EC2::SecurityGroup.SecurityGroupIngress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-securitygroupingress
        Stability:
            stable
        """
        return jsii.get(self, "securityGroupIngress")

    @security_group_ingress.setter
    def security_group_ingress(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "IngressProperty"]]]]]):
        return jsii.set(self, "securityGroupIngress", value)

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroup.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-vpcid
        Stability:
            stable
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: typing.Optional[str]):
        return jsii.set(self, "vpcId", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _EgressProperty(jsii.compat.TypedDict, total=False):
        cidrIp: str
        """``CfnSecurityGroup.EgressProperty.CidrIp``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-cidrip
        Stability:
            stable
        """
        cidrIpv6: str
        """``CfnSecurityGroup.EgressProperty.CidrIpv6``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-cidripv6
        Stability:
            stable
        """
        description: str
        """``CfnSecurityGroup.EgressProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-description
        Stability:
            stable
        """
        destinationPrefixListId: str
        """``CfnSecurityGroup.EgressProperty.DestinationPrefixListId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-destinationprefixlistid
        Stability:
            stable
        """
        destinationSecurityGroupId: str
        """``CfnSecurityGroup.EgressProperty.DestinationSecurityGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-destsecgroupid
        Stability:
            stable
        """
        fromPort: jsii.Number
        """``CfnSecurityGroup.EgressProperty.FromPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-fromport
        Stability:
            stable
        """
        toPort: jsii.Number
        """``CfnSecurityGroup.EgressProperty.ToPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-toport
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroup.EgressProperty", jsii_struct_bases=[_EgressProperty])
    class EgressProperty(_EgressProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html
        Stability:
            stable
        """
        ipProtocol: str
        """``CfnSecurityGroup.EgressProperty.IpProtocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-ipprotocol
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _IngressProperty(jsii.compat.TypedDict, total=False):
        cidrIp: str
        """``CfnSecurityGroup.IngressProperty.CidrIp``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-cidrip
        Stability:
            stable
        """
        cidrIpv6: str
        """``CfnSecurityGroup.IngressProperty.CidrIpv6``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-cidripv6
        Stability:
            stable
        """
        description: str
        """``CfnSecurityGroup.IngressProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-description
        Stability:
            stable
        """
        fromPort: jsii.Number
        """``CfnSecurityGroup.IngressProperty.FromPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-fromport
        Stability:
            stable
        """
        sourcePrefixListId: str
        """``CfnSecurityGroup.IngressProperty.SourcePrefixListId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-securitygroup-ingress-sourceprefixlistid
        Stability:
            stable
        """
        sourceSecurityGroupId: str
        """``CfnSecurityGroup.IngressProperty.SourceSecurityGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-sourcesecuritygroupid
        Stability:
            stable
        """
        sourceSecurityGroupName: str
        """``CfnSecurityGroup.IngressProperty.SourceSecurityGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-sourcesecuritygroupname
        Stability:
            stable
        """
        sourceSecurityGroupOwnerId: str
        """``CfnSecurityGroup.IngressProperty.SourceSecurityGroupOwnerId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-sourcesecuritygroupownerid
        Stability:
            stable
        """
        toPort: jsii.Number
        """``CfnSecurityGroup.IngressProperty.ToPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-toport
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroup.IngressProperty", jsii_struct_bases=[_IngressProperty])
    class IngressProperty(_IngressProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html
        Stability:
            stable
        """
        ipProtocol: str
        """``CfnSecurityGroup.IngressProperty.IpProtocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-ipprotocol
        Stability:
            stable
        """


class CfnSecurityGroupEgress(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroupEgress"):
    """A CloudFormation ``AWS::EC2::SecurityGroupEgress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::SecurityGroupEgress
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, group_id: str, ip_protocol: str, cidr_ip: typing.Optional[str]=None, cidr_ipv6: typing.Optional[str]=None, description: typing.Optional[str]=None, destination_prefix_list_id: typing.Optional[str]=None, destination_security_group_id: typing.Optional[str]=None, from_port: typing.Optional[jsii.Number]=None, to_port: typing.Optional[jsii.Number]=None) -> None:
        """Create a new ``AWS::EC2::SecurityGroupEgress``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            group_id: ``AWS::EC2::SecurityGroupEgress.GroupId``.
            ip_protocol: ``AWS::EC2::SecurityGroupEgress.IpProtocol``.
            cidr_ip: ``AWS::EC2::SecurityGroupEgress.CidrIp``.
            cidr_ipv6: ``AWS::EC2::SecurityGroupEgress.CidrIpv6``.
            description: ``AWS::EC2::SecurityGroupEgress.Description``.
            destination_prefix_list_id: ``AWS::EC2::SecurityGroupEgress.DestinationPrefixListId``.
            destination_security_group_id: ``AWS::EC2::SecurityGroupEgress.DestinationSecurityGroupId``.
            from_port: ``AWS::EC2::SecurityGroupEgress.FromPort``.
            to_port: ``AWS::EC2::SecurityGroupEgress.ToPort``.

        Stability:
            experimental
        """
        props: CfnSecurityGroupEgressProps = {"groupId": group_id, "ipProtocol": ip_protocol}

        if cidr_ip is not None:
            props["cidrIp"] = cidr_ip

        if cidr_ipv6 is not None:
            props["cidrIpv6"] = cidr_ipv6

        if description is not None:
            props["description"] = description

        if destination_prefix_list_id is not None:
            props["destinationPrefixListId"] = destination_prefix_list_id

        if destination_security_group_id is not None:
            props["destinationSecurityGroupId"] = destination_security_group_id

        if from_port is not None:
            props["fromPort"] = from_port

        if to_port is not None:
            props["toPort"] = to_port

        jsii.create(CfnSecurityGroupEgress, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> str:
        """``AWS::EC2::SecurityGroupEgress.GroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-groupid
        Stability:
            stable
        """
        return jsii.get(self, "groupId")

    @group_id.setter
    def group_id(self, value: str):
        return jsii.set(self, "groupId", value)

    @property
    @jsii.member(jsii_name="ipProtocol")
    def ip_protocol(self) -> str:
        """``AWS::EC2::SecurityGroupEgress.IpProtocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-ipprotocol
        Stability:
            stable
        """
        return jsii.get(self, "ipProtocol")

    @ip_protocol.setter
    def ip_protocol(self, value: str):
        return jsii.set(self, "ipProtocol", value)

    @property
    @jsii.member(jsii_name="cidrIp")
    def cidr_ip(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupEgress.CidrIp``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-cidrip
        Stability:
            stable
        """
        return jsii.get(self, "cidrIp")

    @cidr_ip.setter
    def cidr_ip(self, value: typing.Optional[str]):
        return jsii.set(self, "cidrIp", value)

    @property
    @jsii.member(jsii_name="cidrIpv6")
    def cidr_ipv6(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupEgress.CidrIpv6``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-cidripv6
        Stability:
            stable
        """
        return jsii.get(self, "cidrIpv6")

    @cidr_ipv6.setter
    def cidr_ipv6(self, value: typing.Optional[str]):
        return jsii.set(self, "cidrIpv6", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupEgress.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="destinationPrefixListId")
    def destination_prefix_list_id(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupEgress.DestinationPrefixListId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-destinationprefixlistid
        Stability:
            stable
        """
        return jsii.get(self, "destinationPrefixListId")

    @destination_prefix_list_id.setter
    def destination_prefix_list_id(self, value: typing.Optional[str]):
        return jsii.set(self, "destinationPrefixListId", value)

    @property
    @jsii.member(jsii_name="destinationSecurityGroupId")
    def destination_security_group_id(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupEgress.DestinationSecurityGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-destinationsecuritygroupid
        Stability:
            stable
        """
        return jsii.get(self, "destinationSecurityGroupId")

    @destination_security_group_id.setter
    def destination_security_group_id(self, value: typing.Optional[str]):
        return jsii.set(self, "destinationSecurityGroupId", value)

    @property
    @jsii.member(jsii_name="fromPort")
    def from_port(self) -> typing.Optional[jsii.Number]:
        """``AWS::EC2::SecurityGroupEgress.FromPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-fromport
        Stability:
            stable
        """
        return jsii.get(self, "fromPort")

    @from_port.setter
    def from_port(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "fromPort", value)

    @property
    @jsii.member(jsii_name="toPort")
    def to_port(self) -> typing.Optional[jsii.Number]:
        """``AWS::EC2::SecurityGroupEgress.ToPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-toport
        Stability:
            stable
        """
        return jsii.get(self, "toPort")

    @to_port.setter
    def to_port(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "toPort", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSecurityGroupEgressProps(jsii.compat.TypedDict, total=False):
    cidrIp: str
    """``AWS::EC2::SecurityGroupEgress.CidrIp``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-cidrip
    Stability:
        stable
    """
    cidrIpv6: str
    """``AWS::EC2::SecurityGroupEgress.CidrIpv6``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-cidripv6
    Stability:
        stable
    """
    description: str
    """``AWS::EC2::SecurityGroupEgress.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-description
    Stability:
        stable
    """
    destinationPrefixListId: str
    """``AWS::EC2::SecurityGroupEgress.DestinationPrefixListId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-destinationprefixlistid
    Stability:
        stable
    """
    destinationSecurityGroupId: str
    """``AWS::EC2::SecurityGroupEgress.DestinationSecurityGroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-destinationsecuritygroupid
    Stability:
        stable
    """
    fromPort: jsii.Number
    """``AWS::EC2::SecurityGroupEgress.FromPort``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-fromport
    Stability:
        stable
    """
    toPort: jsii.Number
    """``AWS::EC2::SecurityGroupEgress.ToPort``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-toport
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroupEgressProps", jsii_struct_bases=[_CfnSecurityGroupEgressProps])
class CfnSecurityGroupEgressProps(_CfnSecurityGroupEgressProps):
    """Properties for defining a ``AWS::EC2::SecurityGroupEgress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html
    Stability:
        stable
    """
    groupId: str
    """``AWS::EC2::SecurityGroupEgress.GroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-groupid
    Stability:
        stable
    """

    ipProtocol: str
    """``AWS::EC2::SecurityGroupEgress.IpProtocol``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-ipprotocol
    Stability:
        stable
    """

class CfnSecurityGroupIngress(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroupIngress"):
    """A CloudFormation ``AWS::EC2::SecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::SecurityGroupIngress
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, ip_protocol: str, cidr_ip: typing.Optional[str]=None, cidr_ipv6: typing.Optional[str]=None, description: typing.Optional[str]=None, from_port: typing.Optional[jsii.Number]=None, group_id: typing.Optional[str]=None, group_name: typing.Optional[str]=None, source_prefix_list_id: typing.Optional[str]=None, source_security_group_id: typing.Optional[str]=None, source_security_group_name: typing.Optional[str]=None, source_security_group_owner_id: typing.Optional[str]=None, to_port: typing.Optional[jsii.Number]=None) -> None:
        """Create a new ``AWS::EC2::SecurityGroupIngress``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            ip_protocol: ``AWS::EC2::SecurityGroupIngress.IpProtocol``.
            cidr_ip: ``AWS::EC2::SecurityGroupIngress.CidrIp``.
            cidr_ipv6: ``AWS::EC2::SecurityGroupIngress.CidrIpv6``.
            description: ``AWS::EC2::SecurityGroupIngress.Description``.
            from_port: ``AWS::EC2::SecurityGroupIngress.FromPort``.
            group_id: ``AWS::EC2::SecurityGroupIngress.GroupId``.
            group_name: ``AWS::EC2::SecurityGroupIngress.GroupName``.
            source_prefix_list_id: ``AWS::EC2::SecurityGroupIngress.SourcePrefixListId``.
            source_security_group_id: ``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupId``.
            source_security_group_name: ``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupName``.
            source_security_group_owner_id: ``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupOwnerId``.
            to_port: ``AWS::EC2::SecurityGroupIngress.ToPort``.

        Stability:
            experimental
        """
        props: CfnSecurityGroupIngressProps = {"ipProtocol": ip_protocol}

        if cidr_ip is not None:
            props["cidrIp"] = cidr_ip

        if cidr_ipv6 is not None:
            props["cidrIpv6"] = cidr_ipv6

        if description is not None:
            props["description"] = description

        if from_port is not None:
            props["fromPort"] = from_port

        if group_id is not None:
            props["groupId"] = group_id

        if group_name is not None:
            props["groupName"] = group_name

        if source_prefix_list_id is not None:
            props["sourcePrefixListId"] = source_prefix_list_id

        if source_security_group_id is not None:
            props["sourceSecurityGroupId"] = source_security_group_id

        if source_security_group_name is not None:
            props["sourceSecurityGroupName"] = source_security_group_name

        if source_security_group_owner_id is not None:
            props["sourceSecurityGroupOwnerId"] = source_security_group_owner_id

        if to_port is not None:
            props["toPort"] = to_port

        jsii.create(CfnSecurityGroupIngress, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="ipProtocol")
    def ip_protocol(self) -> str:
        """``AWS::EC2::SecurityGroupIngress.IpProtocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-ipprotocol
        Stability:
            stable
        """
        return jsii.get(self, "ipProtocol")

    @ip_protocol.setter
    def ip_protocol(self, value: str):
        return jsii.set(self, "ipProtocol", value)

    @property
    @jsii.member(jsii_name="cidrIp")
    def cidr_ip(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupIngress.CidrIp``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-cidrip
        Stability:
            stable
        """
        return jsii.get(self, "cidrIp")

    @cidr_ip.setter
    def cidr_ip(self, value: typing.Optional[str]):
        return jsii.set(self, "cidrIp", value)

    @property
    @jsii.member(jsii_name="cidrIpv6")
    def cidr_ipv6(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupIngress.CidrIpv6``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-cidripv6
        Stability:
            stable
        """
        return jsii.get(self, "cidrIpv6")

    @cidr_ipv6.setter
    def cidr_ipv6(self, value: typing.Optional[str]):
        return jsii.set(self, "cidrIpv6", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupIngress.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="fromPort")
    def from_port(self) -> typing.Optional[jsii.Number]:
        """``AWS::EC2::SecurityGroupIngress.FromPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-fromport
        Stability:
            stable
        """
        return jsii.get(self, "fromPort")

    @from_port.setter
    def from_port(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "fromPort", value)

    @property
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupIngress.GroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-groupid
        Stability:
            stable
        """
        return jsii.get(self, "groupId")

    @group_id.setter
    def group_id(self, value: typing.Optional[str]):
        return jsii.set(self, "groupId", value)

    @property
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupIngress.GroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-groupname
        Stability:
            stable
        """
        return jsii.get(self, "groupName")

    @group_name.setter
    def group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "groupName", value)

    @property
    @jsii.member(jsii_name="sourcePrefixListId")
    def source_prefix_list_id(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupIngress.SourcePrefixListId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-securitygroupingress-sourceprefixlistid
        Stability:
            stable
        """
        return jsii.get(self, "sourcePrefixListId")

    @source_prefix_list_id.setter
    def source_prefix_list_id(self, value: typing.Optional[str]):
        return jsii.set(self, "sourcePrefixListId", value)

    @property
    @jsii.member(jsii_name="sourceSecurityGroupId")
    def source_security_group_id(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-sourcesecuritygroupid
        Stability:
            stable
        """
        return jsii.get(self, "sourceSecurityGroupId")

    @source_security_group_id.setter
    def source_security_group_id(self, value: typing.Optional[str]):
        return jsii.set(self, "sourceSecurityGroupId", value)

    @property
    @jsii.member(jsii_name="sourceSecurityGroupName")
    def source_security_group_name(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-sourcesecuritygroupname
        Stability:
            stable
        """
        return jsii.get(self, "sourceSecurityGroupName")

    @source_security_group_name.setter
    def source_security_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "sourceSecurityGroupName", value)

    @property
    @jsii.member(jsii_name="sourceSecurityGroupOwnerId")
    def source_security_group_owner_id(self) -> typing.Optional[str]:
        """``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupOwnerId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-sourcesecuritygroupownerid
        Stability:
            stable
        """
        return jsii.get(self, "sourceSecurityGroupOwnerId")

    @source_security_group_owner_id.setter
    def source_security_group_owner_id(self, value: typing.Optional[str]):
        return jsii.set(self, "sourceSecurityGroupOwnerId", value)

    @property
    @jsii.member(jsii_name="toPort")
    def to_port(self) -> typing.Optional[jsii.Number]:
        """``AWS::EC2::SecurityGroupIngress.ToPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-toport
        Stability:
            stable
        """
        return jsii.get(self, "toPort")

    @to_port.setter
    def to_port(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "toPort", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSecurityGroupIngressProps(jsii.compat.TypedDict, total=False):
    cidrIp: str
    """``AWS::EC2::SecurityGroupIngress.CidrIp``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-cidrip
    Stability:
        stable
    """
    cidrIpv6: str
    """``AWS::EC2::SecurityGroupIngress.CidrIpv6``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-cidripv6
    Stability:
        stable
    """
    description: str
    """``AWS::EC2::SecurityGroupIngress.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-description
    Stability:
        stable
    """
    fromPort: jsii.Number
    """``AWS::EC2::SecurityGroupIngress.FromPort``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-fromport
    Stability:
        stable
    """
    groupId: str
    """``AWS::EC2::SecurityGroupIngress.GroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-groupid
    Stability:
        stable
    """
    groupName: str
    """``AWS::EC2::SecurityGroupIngress.GroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-groupname
    Stability:
        stable
    """
    sourcePrefixListId: str
    """``AWS::EC2::SecurityGroupIngress.SourcePrefixListId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-securitygroupingress-sourceprefixlistid
    Stability:
        stable
    """
    sourceSecurityGroupId: str
    """``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-sourcesecuritygroupid
    Stability:
        stable
    """
    sourceSecurityGroupName: str
    """``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-sourcesecuritygroupname
    Stability:
        stable
    """
    sourceSecurityGroupOwnerId: str
    """``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupOwnerId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-sourcesecuritygroupownerid
    Stability:
        stable
    """
    toPort: jsii.Number
    """``AWS::EC2::SecurityGroupIngress.ToPort``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-toport
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroupIngressProps", jsii_struct_bases=[_CfnSecurityGroupIngressProps])
class CfnSecurityGroupIngressProps(_CfnSecurityGroupIngressProps):
    """Properties for defining a ``AWS::EC2::SecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html
    Stability:
        stable
    """
    ipProtocol: str
    """``AWS::EC2::SecurityGroupIngress.IpProtocol``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-ipprotocol
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSecurityGroupProps(jsii.compat.TypedDict, total=False):
    groupName: str
    """``AWS::EC2::SecurityGroup.GroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-groupname
    Stability:
        stable
    """
    securityGroupEgress: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSecurityGroup.EgressProperty"]]]
    """``AWS::EC2::SecurityGroup.SecurityGroupEgress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-securitygroupegress
    Stability:
        stable
    """
    securityGroupIngress: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSecurityGroup.IngressProperty"]]]
    """``AWS::EC2::SecurityGroup.SecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-securitygroupingress
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::SecurityGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-tags
    Stability:
        stable
    """
    vpcId: str
    """``AWS::EC2::SecurityGroup.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-vpcid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroupProps", jsii_struct_bases=[_CfnSecurityGroupProps])
class CfnSecurityGroupProps(_CfnSecurityGroupProps):
    """Properties for defining a ``AWS::EC2::SecurityGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
    Stability:
        stable
    """
    groupDescription: str
    """``AWS::EC2::SecurityGroup.GroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-groupdescription
    Stability:
        stable
    """

class CfnSpotFleet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet"):
    """A CloudFormation ``AWS::EC2::SpotFleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-spotfleet.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::SpotFleet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, spot_fleet_request_config_data: typing.Union[aws_cdk.core.IResolvable, "SpotFleetRequestConfigDataProperty"]) -> None:
        """Create a new ``AWS::EC2::SpotFleet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            spot_fleet_request_config_data: ``AWS::EC2::SpotFleet.SpotFleetRequestConfigData``.

        Stability:
            experimental
        """
        props: CfnSpotFleetProps = {"spotFleetRequestConfigData": spot_fleet_request_config_data}

        jsii.create(CfnSpotFleet, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="spotFleetRequestConfigData")
    def spot_fleet_request_config_data(self) -> typing.Union[aws_cdk.core.IResolvable, "SpotFleetRequestConfigDataProperty"]:
        """``AWS::EC2::SpotFleet.SpotFleetRequestConfigData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-spotfleet.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata
        Stability:
            stable
        """
        return jsii.get(self, "spotFleetRequestConfigData")

    @spot_fleet_request_config_data.setter
    def spot_fleet_request_config_data(self, value: typing.Union[aws_cdk.core.IResolvable, "SpotFleetRequestConfigDataProperty"]):
        return jsii.set(self, "spotFleetRequestConfigData", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _BlockDeviceMappingProperty(jsii.compat.TypedDict, total=False):
        ebs: typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.EbsBlockDeviceProperty"]
        """``CfnSpotFleet.BlockDeviceMappingProperty.Ebs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings.html#cfn-ec2-spotfleet-blockdevicemapping-ebs
        Stability:
            stable
        """
        noDevice: str
        """``CfnSpotFleet.BlockDeviceMappingProperty.NoDevice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings.html#cfn-ec2-spotfleet-blockdevicemapping-nodevice
        Stability:
            stable
        """
        virtualName: str
        """``CfnSpotFleet.BlockDeviceMappingProperty.VirtualName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings.html#cfn-ec2-spotfleet-blockdevicemapping-virtualname
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.BlockDeviceMappingProperty", jsii_struct_bases=[_BlockDeviceMappingProperty])
    class BlockDeviceMappingProperty(_BlockDeviceMappingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings.html
        Stability:
            stable
        """
        deviceName: str
        """``CfnSpotFleet.BlockDeviceMappingProperty.DeviceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings.html#cfn-ec2-spotfleet-blockdevicemapping-devicename
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.ClassicLoadBalancerProperty", jsii_struct_bases=[])
    class ClassicLoadBalancerProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-classicloadbalancer.html
        Stability:
            stable
        """
        name: str
        """``CfnSpotFleet.ClassicLoadBalancerProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-classicloadbalancer.html#cfn-ec2-spotfleet-classicloadbalancer-name
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.ClassicLoadBalancersConfigProperty", jsii_struct_bases=[])
    class ClassicLoadBalancersConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-classicloadbalancersconfig.html
        Stability:
            stable
        """
        classicLoadBalancers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.ClassicLoadBalancerProperty"]]]
        """``CfnSpotFleet.ClassicLoadBalancersConfigProperty.ClassicLoadBalancers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-classicloadbalancersconfig.html#cfn-ec2-spotfleet-classicloadbalancersconfig-classicloadbalancers
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.EbsBlockDeviceProperty", jsii_struct_bases=[])
    class EbsBlockDeviceProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html
        Stability:
            stable
        """
        deleteOnTermination: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSpotFleet.EbsBlockDeviceProperty.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html#cfn-ec2-spotfleet-ebsblockdevice-deleteontermination
        Stability:
            stable
        """

        encrypted: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSpotFleet.EbsBlockDeviceProperty.Encrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html#cfn-ec2-spotfleet-ebsblockdevice-encrypted
        Stability:
            stable
        """

        iops: jsii.Number
        """``CfnSpotFleet.EbsBlockDeviceProperty.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html#cfn-ec2-spotfleet-ebsblockdevice-iops
        Stability:
            stable
        """

        snapshotId: str
        """``CfnSpotFleet.EbsBlockDeviceProperty.SnapshotId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html#cfn-ec2-spotfleet-ebsblockdevice-snapshotid
        Stability:
            stable
        """

        volumeSize: jsii.Number
        """``CfnSpotFleet.EbsBlockDeviceProperty.VolumeSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html#cfn-ec2-spotfleet-ebsblockdevice-volumesize
        Stability:
            stable
        """

        volumeType: str
        """``CfnSpotFleet.EbsBlockDeviceProperty.VolumeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html#cfn-ec2-spotfleet-ebsblockdevice-volumetype
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FleetLaunchTemplateSpecificationProperty(jsii.compat.TypedDict, total=False):
        launchTemplateId: str
        """``CfnSpotFleet.FleetLaunchTemplateSpecificationProperty.LaunchTemplateId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-fleetlaunchtemplatespecification.html#cfn-ec2-spotfleet-fleetlaunchtemplatespecification-launchtemplateid
        Stability:
            stable
        """
        launchTemplateName: str
        """``CfnSpotFleet.FleetLaunchTemplateSpecificationProperty.LaunchTemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-fleetlaunchtemplatespecification.html#cfn-ec2-spotfleet-fleetlaunchtemplatespecification-launchtemplatename
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.FleetLaunchTemplateSpecificationProperty", jsii_struct_bases=[_FleetLaunchTemplateSpecificationProperty])
    class FleetLaunchTemplateSpecificationProperty(_FleetLaunchTemplateSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-fleetlaunchtemplatespecification.html
        Stability:
            stable
        """
        version: str
        """``CfnSpotFleet.FleetLaunchTemplateSpecificationProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-fleetlaunchtemplatespecification.html#cfn-ec2-spotfleet-fleetlaunchtemplatespecification-version
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.GroupIdentifierProperty", jsii_struct_bases=[])
    class GroupIdentifierProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-securitygroups.html
        Stability:
            stable
        """
        groupId: str
        """``CfnSpotFleet.GroupIdentifierProperty.GroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-securitygroups.html#cfn-ec2-spotfleet-groupidentifier-groupid
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.IamInstanceProfileSpecificationProperty", jsii_struct_bases=[])
    class IamInstanceProfileSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-iaminstanceprofile.html
        Stability:
            stable
        """
        arn: str
        """``CfnSpotFleet.IamInstanceProfileSpecificationProperty.Arn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-iaminstanceprofile.html#cfn-ec2-spotfleet-iaminstanceprofilespecification-arn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.InstanceIpv6AddressProperty", jsii_struct_bases=[])
    class InstanceIpv6AddressProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-instanceipv6address.html
        Stability:
            stable
        """
        ipv6Address: str
        """``CfnSpotFleet.InstanceIpv6AddressProperty.Ipv6Address``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-instanceipv6address.html#cfn-ec2-spotfleet-instanceipv6address-ipv6address
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty", jsii_struct_bases=[])
    class InstanceNetworkInterfaceSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html
        Stability:
            stable
        """
        associatePublicIpAddress: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.AssociatePublicIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-associatepublicipaddress
        Stability:
            stable
        """

        deleteOnTermination: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-deleteontermination
        Stability:
            stable
        """

        description: str
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-description
        Stability:
            stable
        """

        deviceIndex: jsii.Number
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.DeviceIndex``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-deviceindex
        Stability:
            stable
        """

        groups: typing.List[str]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.Groups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-groups
        Stability:
            stable
        """

        ipv6AddressCount: jsii.Number
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.Ipv6AddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-ipv6addresscount
        Stability:
            stable
        """

        ipv6Addresses: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.InstanceIpv6AddressProperty"]]]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.Ipv6Addresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-ipv6addresses
        Stability:
            stable
        """

        networkInterfaceId: str
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.NetworkInterfaceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-networkinterfaceid
        Stability:
            stable
        """

        privateIpAddresses: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.PrivateIpAddressSpecificationProperty"]]]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.PrivateIpAddresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-privateipaddresses
        Stability:
            stable
        """

        secondaryPrivateIpAddressCount: jsii.Number
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.SecondaryPrivateIpAddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-secondaryprivateipaddresscount
        Stability:
            stable
        """

        subnetId: str
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-subnetid
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.LaunchTemplateConfigProperty", jsii_struct_bases=[])
    class LaunchTemplateConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateconfig.html
        Stability:
            stable
        """
        launchTemplateSpecification: typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.FleetLaunchTemplateSpecificationProperty"]
        """``CfnSpotFleet.LaunchTemplateConfigProperty.LaunchTemplateSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateconfig.html#cfn-ec2-spotfleet-launchtemplateconfig-launchtemplatespecification
        Stability:
            stable
        """

        overrides: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.LaunchTemplateOverridesProperty"]]]
        """``CfnSpotFleet.LaunchTemplateConfigProperty.Overrides``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateconfig.html#cfn-ec2-spotfleet-launchtemplateconfig-overrides
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.LaunchTemplateOverridesProperty", jsii_struct_bases=[])
    class LaunchTemplateOverridesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateoverrides.html
        Stability:
            stable
        """
        availabilityZone: str
        """``CfnSpotFleet.LaunchTemplateOverridesProperty.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateoverrides.html#cfn-ec2-spotfleet-launchtemplateoverrides-availabilityzone
        Stability:
            stable
        """

        instanceType: str
        """``CfnSpotFleet.LaunchTemplateOverridesProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateoverrides.html#cfn-ec2-spotfleet-launchtemplateoverrides-instancetype
        Stability:
            stable
        """

        spotPrice: str
        """``CfnSpotFleet.LaunchTemplateOverridesProperty.SpotPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateoverrides.html#cfn-ec2-spotfleet-launchtemplateoverrides-spotprice
        Stability:
            stable
        """

        subnetId: str
        """``CfnSpotFleet.LaunchTemplateOverridesProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateoverrides.html#cfn-ec2-spotfleet-launchtemplateoverrides-subnetid
        Stability:
            stable
        """

        weightedCapacity: jsii.Number
        """``CfnSpotFleet.LaunchTemplateOverridesProperty.WeightedCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateoverrides.html#cfn-ec2-spotfleet-launchtemplateoverrides-weightedcapacity
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.LoadBalancersConfigProperty", jsii_struct_bases=[])
    class LoadBalancersConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-loadbalancersconfig.html
        Stability:
            stable
        """
        classicLoadBalancersConfig: typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.ClassicLoadBalancersConfigProperty"]
        """``CfnSpotFleet.LoadBalancersConfigProperty.ClassicLoadBalancersConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-loadbalancersconfig.html#cfn-ec2-spotfleet-loadbalancersconfig-classicloadbalancersconfig
        Stability:
            stable
        """

        targetGroupsConfig: typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.TargetGroupsConfigProperty"]
        """``CfnSpotFleet.LoadBalancersConfigProperty.TargetGroupsConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-loadbalancersconfig.html#cfn-ec2-spotfleet-loadbalancersconfig-targetgroupsconfig
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _PrivateIpAddressSpecificationProperty(jsii.compat.TypedDict, total=False):
        primary: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSpotFleet.PrivateIpAddressSpecificationProperty.Primary``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces-privateipaddresses.html#cfn-ec2-spotfleet-privateipaddressspecification-primary
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.PrivateIpAddressSpecificationProperty", jsii_struct_bases=[_PrivateIpAddressSpecificationProperty])
    class PrivateIpAddressSpecificationProperty(_PrivateIpAddressSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces-privateipaddresses.html
        Stability:
            stable
        """
        privateIpAddress: str
        """``CfnSpotFleet.PrivateIpAddressSpecificationProperty.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces-privateipaddresses.html#cfn-ec2-spotfleet-privateipaddressspecification-privateipaddress
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SpotFleetLaunchSpecificationProperty(jsii.compat.TypedDict, total=False):
        blockDeviceMappings: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.BlockDeviceMappingProperty"]]]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.BlockDeviceMappings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-blockdevicemappings
        Stability:
            stable
        """
        ebsOptimized: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.EbsOptimized``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-ebsoptimized
        Stability:
            stable
        """
        iamInstanceProfile: typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.IamInstanceProfileSpecificationProperty"]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.IamInstanceProfile``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-iaminstanceprofile
        Stability:
            stable
        """
        kernelId: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.KernelId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-kernelid
        Stability:
            stable
        """
        keyName: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.KeyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-keyname
        Stability:
            stable
        """
        monitoring: typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.SpotFleetMonitoringProperty"]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.Monitoring``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-monitoring
        Stability:
            stable
        """
        networkInterfaces: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty"]]]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.NetworkInterfaces``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-networkinterfaces
        Stability:
            stable
        """
        placement: typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.SpotPlacementProperty"]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.Placement``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-placement
        Stability:
            stable
        """
        ramdiskId: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.RamdiskId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-ramdiskid
        Stability:
            stable
        """
        securityGroups: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.GroupIdentifierProperty"]]]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.SecurityGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-securitygroups
        Stability:
            stable
        """
        spotPrice: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.SpotPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-spotprice
        Stability:
            stable
        """
        subnetId: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-subnetid
        Stability:
            stable
        """
        tagSpecifications: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.SpotFleetTagSpecificationProperty"]]]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.TagSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-tagspecifications
        Stability:
            stable
        """
        userData: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.UserData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-userdata
        Stability:
            stable
        """
        weightedCapacity: jsii.Number
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.WeightedCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-weightedcapacity
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.SpotFleetLaunchSpecificationProperty", jsii_struct_bases=[_SpotFleetLaunchSpecificationProperty])
    class SpotFleetLaunchSpecificationProperty(_SpotFleetLaunchSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html
        Stability:
            stable
        """
        imageId: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.ImageId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-imageid
        Stability:
            stable
        """

        instanceType: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-instancetype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.SpotFleetMonitoringProperty", jsii_struct_bases=[])
    class SpotFleetMonitoringProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-monitoring.html
        Stability:
            stable
        """
        enabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSpotFleet.SpotFleetMonitoringProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-monitoring.html#cfn-ec2-spotfleet-spotfleetmonitoring-enabled
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SpotFleetRequestConfigDataProperty(jsii.compat.TypedDict, total=False):
        allocationStrategy: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.AllocationStrategy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-allocationstrategy
        Stability:
            stable
        """
        excessCapacityTerminationPolicy: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.ExcessCapacityTerminationPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-excesscapacityterminationpolicy
        Stability:
            stable
        """
        instanceInterruptionBehavior: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.InstanceInterruptionBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-instanceinterruptionbehavior
        Stability:
            stable
        """
        launchSpecifications: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.SpotFleetLaunchSpecificationProperty"]]]
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.LaunchSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications
        Stability:
            stable
        """
        launchTemplateConfigs: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.LaunchTemplateConfigProperty"]]]
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.LaunchTemplateConfigs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-launchtemplateconfigs
        Stability:
            stable
        """
        loadBalancersConfig: typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.LoadBalancersConfigProperty"]
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.LoadBalancersConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-loadbalancersconfig
        Stability:
            stable
        """
        replaceUnhealthyInstances: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.ReplaceUnhealthyInstances``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-replaceunhealthyinstances
        Stability:
            stable
        """
        spotPrice: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.SpotPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-spotprice
        Stability:
            stable
        """
        terminateInstancesWithExpiration: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.TerminateInstancesWithExpiration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-terminateinstanceswithexpiration
        Stability:
            stable
        """
        type: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-type
        Stability:
            stable
        """
        validFrom: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.ValidFrom``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-validfrom
        Stability:
            stable
        """
        validUntil: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.ValidUntil``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-validuntil
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.SpotFleetRequestConfigDataProperty", jsii_struct_bases=[_SpotFleetRequestConfigDataProperty])
    class SpotFleetRequestConfigDataProperty(_SpotFleetRequestConfigDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html
        Stability:
            stable
        """
        iamFleetRole: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.IamFleetRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-iamfleetrole
        Stability:
            stable
        """

        targetCapacity: jsii.Number
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.TargetCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-targetcapacity
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.SpotFleetTagSpecificationProperty", jsii_struct_bases=[])
    class SpotFleetTagSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-tagspecifications.html
        Stability:
            stable
        """
        resourceType: str
        """``CfnSpotFleet.SpotFleetTagSpecificationProperty.ResourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-tagspecifications.html#cfn-ec2-spotfleet-spotfleettagspecification-resourcetype
        Stability:
            stable
        """

        tags: typing.List[aws_cdk.core.CfnTag]
        """``CfnSpotFleet.SpotFleetTagSpecificationProperty.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-tagspecifications.html#cfn-ec2-spotfleet-tags
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.SpotPlacementProperty", jsii_struct_bases=[])
    class SpotPlacementProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-placement.html
        Stability:
            stable
        """
        availabilityZone: str
        """``CfnSpotFleet.SpotPlacementProperty.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-placement.html#cfn-ec2-spotfleet-spotplacement-availabilityzone
        Stability:
            stable
        """

        groupName: str
        """``CfnSpotFleet.SpotPlacementProperty.GroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-placement.html#cfn-ec2-spotfleet-spotplacement-groupname
        Stability:
            stable
        """

        tenancy: str
        """``CfnSpotFleet.SpotPlacementProperty.Tenancy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-placement.html#cfn-ec2-spotfleet-spotplacement-tenancy
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.TargetGroupProperty", jsii_struct_bases=[])
    class TargetGroupProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-targetgroup.html
        Stability:
            stable
        """
        arn: str
        """``CfnSpotFleet.TargetGroupProperty.Arn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-targetgroup.html#cfn-ec2-spotfleet-targetgroup-arn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.TargetGroupsConfigProperty", jsii_struct_bases=[])
    class TargetGroupsConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-targetgroupsconfig.html
        Stability:
            stable
        """
        targetGroups: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.TargetGroupProperty"]]]
        """``CfnSpotFleet.TargetGroupsConfigProperty.TargetGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-targetgroupsconfig.html#cfn-ec2-spotfleet-targetgroupsconfig-targetgroups
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleetProps", jsii_struct_bases=[])
class CfnSpotFleetProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::SpotFleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-spotfleet.html
    Stability:
        stable
    """
    spotFleetRequestConfigData: typing.Union[aws_cdk.core.IResolvable, "CfnSpotFleet.SpotFleetRequestConfigDataProperty"]
    """``AWS::EC2::SpotFleet.SpotFleetRequestConfigData``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-spotfleet.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata
    Stability:
        stable
    """

class CfnSubnet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSubnet"):
    """A CloudFormation ``AWS::EC2::Subnet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::Subnet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, cidr_block: str, vpc_id: str, assign_ipv6_address_on_creation: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, availability_zone: typing.Optional[str]=None, ipv6_cidr_block: typing.Optional[str]=None, map_public_ip_on_launch: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::Subnet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            cidr_block: ``AWS::EC2::Subnet.CidrBlock``.
            vpc_id: ``AWS::EC2::Subnet.VpcId``.
            assign_ipv6_address_on_creation: ``AWS::EC2::Subnet.AssignIpv6AddressOnCreation``.
            availability_zone: ``AWS::EC2::Subnet.AvailabilityZone``.
            ipv6_cidr_block: ``AWS::EC2::Subnet.Ipv6CidrBlock``.
            map_public_ip_on_launch: ``AWS::EC2::Subnet.MapPublicIpOnLaunch``.
            tags: ``AWS::EC2::Subnet.Tags``.

        Stability:
            experimental
        """
        props: CfnSubnetProps = {"cidrBlock": cidr_block, "vpcId": vpc_id}

        if assign_ipv6_address_on_creation is not None:
            props["assignIpv6AddressOnCreation"] = assign_ipv6_address_on_creation

        if availability_zone is not None:
            props["availabilityZone"] = availability_zone

        if ipv6_cidr_block is not None:
            props["ipv6CidrBlock"] = ipv6_cidr_block

        if map_public_ip_on_launch is not None:
            props["mapPublicIpOnLaunch"] = map_public_ip_on_launch

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnSubnet, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrAvailabilityZone")
    def attr_availability_zone(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            AvailabilityZone
        """
        return jsii.get(self, "attrAvailabilityZone")

    @property
    @jsii.member(jsii_name="attrIpv6CidrBlocks")
    def attr_ipv6_cidr_blocks(self) -> typing.List[str]:
        """
        Stability:
            stable
        cloudformationAttribute:
            Ipv6CidrBlocks
        """
        return jsii.get(self, "attrIpv6CidrBlocks")

    @property
    @jsii.member(jsii_name="attrNetworkAclAssociationId")
    def attr_network_acl_association_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            NetworkAclAssociationId
        """
        return jsii.get(self, "attrNetworkAclAssociationId")

    @property
    @jsii.member(jsii_name="attrVpcId")
    def attr_vpc_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            VpcId
        """
        return jsii.get(self, "attrVpcId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::Subnet.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="cidrBlock")
    def cidr_block(self) -> str:
        """``AWS::EC2::Subnet.CidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-cidrblock
        Stability:
            stable
        """
        return jsii.get(self, "cidrBlock")

    @cidr_block.setter
    def cidr_block(self, value: str):
        return jsii.set(self, "cidrBlock", value)

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """``AWS::EC2::Subnet.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-awsec2subnet-prop-vpcid
        Stability:
            stable
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: str):
        return jsii.set(self, "vpcId", value)

    @property
    @jsii.member(jsii_name="assignIpv6AddressOnCreation")
    def assign_ipv6_address_on_creation(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::Subnet.AssignIpv6AddressOnCreation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-assignipv6addressoncreation
        Stability:
            stable
        """
        return jsii.get(self, "assignIpv6AddressOnCreation")

    @assign_ipv6_address_on_creation.setter
    def assign_ipv6_address_on_creation(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "assignIpv6AddressOnCreation", value)

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> typing.Optional[str]:
        """``AWS::EC2::Subnet.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-availabilityzone
        Stability:
            stable
        """
        return jsii.get(self, "availabilityZone")

    @availability_zone.setter
    def availability_zone(self, value: typing.Optional[str]):
        return jsii.set(self, "availabilityZone", value)

    @property
    @jsii.member(jsii_name="ipv6CidrBlock")
    def ipv6_cidr_block(self) -> typing.Optional[str]:
        """``AWS::EC2::Subnet.Ipv6CidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-ipv6cidrblock
        Stability:
            stable
        """
        return jsii.get(self, "ipv6CidrBlock")

    @ipv6_cidr_block.setter
    def ipv6_cidr_block(self, value: typing.Optional[str]):
        return jsii.set(self, "ipv6CidrBlock", value)

    @property
    @jsii.member(jsii_name="mapPublicIpOnLaunch")
    def map_public_ip_on_launch(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::Subnet.MapPublicIpOnLaunch``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-mappubliciponlaunch
        Stability:
            stable
        """
        return jsii.get(self, "mapPublicIpOnLaunch")

    @map_public_ip_on_launch.setter
    def map_public_ip_on_launch(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "mapPublicIpOnLaunch", value)


class CfnSubnetCidrBlock(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSubnetCidrBlock"):
    """A CloudFormation ``AWS::EC2::SubnetCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnetcidrblock.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::SubnetCidrBlock
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, ipv6_cidr_block: str, subnet_id: str) -> None:
        """Create a new ``AWS::EC2::SubnetCidrBlock``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            ipv6_cidr_block: ``AWS::EC2::SubnetCidrBlock.Ipv6CidrBlock``.
            subnet_id: ``AWS::EC2::SubnetCidrBlock.SubnetId``.

        Stability:
            experimental
        """
        props: CfnSubnetCidrBlockProps = {"ipv6CidrBlock": ipv6_cidr_block, "subnetId": subnet_id}

        jsii.create(CfnSubnetCidrBlock, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="ipv6CidrBlock")
    def ipv6_cidr_block(self) -> str:
        """``AWS::EC2::SubnetCidrBlock.Ipv6CidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnetcidrblock.html#cfn-ec2-subnetcidrblock-ipv6cidrblock
        Stability:
            stable
        """
        return jsii.get(self, "ipv6CidrBlock")

    @ipv6_cidr_block.setter
    def ipv6_cidr_block(self, value: str):
        return jsii.set(self, "ipv6CidrBlock", value)

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        """``AWS::EC2::SubnetCidrBlock.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnetcidrblock.html#cfn-ec2-subnetcidrblock-subnetid
        Stability:
            stable
        """
        return jsii.get(self, "subnetId")

    @subnet_id.setter
    def subnet_id(self, value: str):
        return jsii.set(self, "subnetId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSubnetCidrBlockProps", jsii_struct_bases=[])
class CfnSubnetCidrBlockProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::SubnetCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnetcidrblock.html
    Stability:
        stable
    """
    ipv6CidrBlock: str
    """``AWS::EC2::SubnetCidrBlock.Ipv6CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnetcidrblock.html#cfn-ec2-subnetcidrblock-ipv6cidrblock
    Stability:
        stable
    """

    subnetId: str
    """``AWS::EC2::SubnetCidrBlock.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnetcidrblock.html#cfn-ec2-subnetcidrblock-subnetid
    Stability:
        stable
    """

class CfnSubnetNetworkAclAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSubnetNetworkAclAssociation"):
    """A CloudFormation ``AWS::EC2::SubnetNetworkAclAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-network-acl-assoc.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::SubnetNetworkAclAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, network_acl_id: str, subnet_id: str) -> None:
        """Create a new ``AWS::EC2::SubnetNetworkAclAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            network_acl_id: ``AWS::EC2::SubnetNetworkAclAssociation.NetworkAclId``.
            subnet_id: ``AWS::EC2::SubnetNetworkAclAssociation.SubnetId``.

        Stability:
            experimental
        """
        props: CfnSubnetNetworkAclAssociationProps = {"networkAclId": network_acl_id, "subnetId": subnet_id}

        jsii.create(CfnSubnetNetworkAclAssociation, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrAssociationId")
    def attr_association_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            AssociationId
        """
        return jsii.get(self, "attrAssociationId")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="networkAclId")
    def network_acl_id(self) -> str:
        """``AWS::EC2::SubnetNetworkAclAssociation.NetworkAclId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-network-acl-assoc.html#cfn-ec2-subnetnetworkaclassociation-networkaclid
        Stability:
            stable
        """
        return jsii.get(self, "networkAclId")

    @network_acl_id.setter
    def network_acl_id(self, value: str):
        return jsii.set(self, "networkAclId", value)

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        """``AWS::EC2::SubnetNetworkAclAssociation.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-network-acl-assoc.html#cfn-ec2-subnetnetworkaclassociation-associationid
        Stability:
            stable
        """
        return jsii.get(self, "subnetId")

    @subnet_id.setter
    def subnet_id(self, value: str):
        return jsii.set(self, "subnetId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSubnetNetworkAclAssociationProps", jsii_struct_bases=[])
class CfnSubnetNetworkAclAssociationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::SubnetNetworkAclAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-network-acl-assoc.html
    Stability:
        stable
    """
    networkAclId: str
    """``AWS::EC2::SubnetNetworkAclAssociation.NetworkAclId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-network-acl-assoc.html#cfn-ec2-subnetnetworkaclassociation-networkaclid
    Stability:
        stable
    """

    subnetId: str
    """``AWS::EC2::SubnetNetworkAclAssociation.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-network-acl-assoc.html#cfn-ec2-subnetnetworkaclassociation-associationid
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSubnetProps(jsii.compat.TypedDict, total=False):
    assignIpv6AddressOnCreation: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::Subnet.AssignIpv6AddressOnCreation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-assignipv6addressoncreation
    Stability:
        stable
    """
    availabilityZone: str
    """``AWS::EC2::Subnet.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-availabilityzone
    Stability:
        stable
    """
    ipv6CidrBlock: str
    """``AWS::EC2::Subnet.Ipv6CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-ipv6cidrblock
    Stability:
        stable
    """
    mapPublicIpOnLaunch: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::Subnet.MapPublicIpOnLaunch``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-mappubliciponlaunch
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::Subnet.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSubnetProps", jsii_struct_bases=[_CfnSubnetProps])
class CfnSubnetProps(_CfnSubnetProps):
    """Properties for defining a ``AWS::EC2::Subnet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html
    Stability:
        stable
    """
    cidrBlock: str
    """``AWS::EC2::Subnet.CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-cidrblock
    Stability:
        stable
    """

    vpcId: str
    """``AWS::EC2::Subnet.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-awsec2subnet-prop-vpcid
    Stability:
        stable
    """

class CfnSubnetRouteTableAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSubnetRouteTableAssociation"):
    """A CloudFormation ``AWS::EC2::SubnetRouteTableAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::SubnetRouteTableAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, route_table_id: str, subnet_id: str) -> None:
        """Create a new ``AWS::EC2::SubnetRouteTableAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            route_table_id: ``AWS::EC2::SubnetRouteTableAssociation.RouteTableId``.
            subnet_id: ``AWS::EC2::SubnetRouteTableAssociation.SubnetId``.

        Stability:
            experimental
        """
        props: CfnSubnetRouteTableAssociationProps = {"routeTableId": route_table_id, "subnetId": subnet_id}

        jsii.create(CfnSubnetRouteTableAssociation, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="routeTableId")
    def route_table_id(self) -> str:
        """``AWS::EC2::SubnetRouteTableAssociation.RouteTableId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html#cfn-ec2-subnetroutetableassociation-routetableid
        Stability:
            stable
        """
        return jsii.get(self, "routeTableId")

    @route_table_id.setter
    def route_table_id(self, value: str):
        return jsii.set(self, "routeTableId", value)

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        """``AWS::EC2::SubnetRouteTableAssociation.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html#cfn-ec2-subnetroutetableassociation-subnetid
        Stability:
            stable
        """
        return jsii.get(self, "subnetId")

    @subnet_id.setter
    def subnet_id(self, value: str):
        return jsii.set(self, "subnetId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSubnetRouteTableAssociationProps", jsii_struct_bases=[])
class CfnSubnetRouteTableAssociationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::SubnetRouteTableAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html
    Stability:
        stable
    """
    routeTableId: str
    """``AWS::EC2::SubnetRouteTableAssociation.RouteTableId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html#cfn-ec2-subnetroutetableassociation-routetableid
    Stability:
        stable
    """

    subnetId: str
    """``AWS::EC2::SubnetRouteTableAssociation.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html#cfn-ec2-subnetroutetableassociation-subnetid
    Stability:
        stable
    """

class CfnTransitGateway(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnTransitGateway"):
    """A CloudFormation ``AWS::EC2::TransitGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::TransitGateway
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, amazon_side_asn: typing.Optional[jsii.Number]=None, auto_accept_shared_attachments: typing.Optional[str]=None, default_route_table_association: typing.Optional[str]=None, default_route_table_propagation: typing.Optional[str]=None, description: typing.Optional[str]=None, dns_support: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, vpn_ecmp_support: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::TransitGateway``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            amazon_side_asn: ``AWS::EC2::TransitGateway.AmazonSideAsn``.
            auto_accept_shared_attachments: ``AWS::EC2::TransitGateway.AutoAcceptSharedAttachments``.
            default_route_table_association: ``AWS::EC2::TransitGateway.DefaultRouteTableAssociation``.
            default_route_table_propagation: ``AWS::EC2::TransitGateway.DefaultRouteTablePropagation``.
            description: ``AWS::EC2::TransitGateway.Description``.
            dns_support: ``AWS::EC2::TransitGateway.DnsSupport``.
            tags: ``AWS::EC2::TransitGateway.Tags``.
            vpn_ecmp_support: ``AWS::EC2::TransitGateway.VpnEcmpSupport``.

        Stability:
            experimental
        """
        props: CfnTransitGatewayProps = {}

        if amazon_side_asn is not None:
            props["amazonSideAsn"] = amazon_side_asn

        if auto_accept_shared_attachments is not None:
            props["autoAcceptSharedAttachments"] = auto_accept_shared_attachments

        if default_route_table_association is not None:
            props["defaultRouteTableAssociation"] = default_route_table_association

        if default_route_table_propagation is not None:
            props["defaultRouteTablePropagation"] = default_route_table_propagation

        if description is not None:
            props["description"] = description

        if dns_support is not None:
            props["dnsSupport"] = dns_support

        if tags is not None:
            props["tags"] = tags

        if vpn_ecmp_support is not None:
            props["vpnEcmpSupport"] = vpn_ecmp_support

        jsii.create(CfnTransitGateway, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::TransitGateway.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="amazonSideAsn")
    def amazon_side_asn(self) -> typing.Optional[jsii.Number]:
        """``AWS::EC2::TransitGateway.AmazonSideAsn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-amazonsideasn
        Stability:
            stable
        """
        return jsii.get(self, "amazonSideAsn")

    @amazon_side_asn.setter
    def amazon_side_asn(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "amazonSideAsn", value)

    @property
    @jsii.member(jsii_name="autoAcceptSharedAttachments")
    def auto_accept_shared_attachments(self) -> typing.Optional[str]:
        """``AWS::EC2::TransitGateway.AutoAcceptSharedAttachments``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-autoacceptsharedattachments
        Stability:
            stable
        """
        return jsii.get(self, "autoAcceptSharedAttachments")

    @auto_accept_shared_attachments.setter
    def auto_accept_shared_attachments(self, value: typing.Optional[str]):
        return jsii.set(self, "autoAcceptSharedAttachments", value)

    @property
    @jsii.member(jsii_name="defaultRouteTableAssociation")
    def default_route_table_association(self) -> typing.Optional[str]:
        """``AWS::EC2::TransitGateway.DefaultRouteTableAssociation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-defaultroutetableassociation
        Stability:
            stable
        """
        return jsii.get(self, "defaultRouteTableAssociation")

    @default_route_table_association.setter
    def default_route_table_association(self, value: typing.Optional[str]):
        return jsii.set(self, "defaultRouteTableAssociation", value)

    @property
    @jsii.member(jsii_name="defaultRouteTablePropagation")
    def default_route_table_propagation(self) -> typing.Optional[str]:
        """``AWS::EC2::TransitGateway.DefaultRouteTablePropagation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-defaultroutetablepropagation
        Stability:
            stable
        """
        return jsii.get(self, "defaultRouteTablePropagation")

    @default_route_table_propagation.setter
    def default_route_table_propagation(self, value: typing.Optional[str]):
        return jsii.set(self, "defaultRouteTablePropagation", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::EC2::TransitGateway.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="dnsSupport")
    def dns_support(self) -> typing.Optional[str]:
        """``AWS::EC2::TransitGateway.DnsSupport``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-dnssupport
        Stability:
            stable
        """
        return jsii.get(self, "dnsSupport")

    @dns_support.setter
    def dns_support(self, value: typing.Optional[str]):
        return jsii.set(self, "dnsSupport", value)

    @property
    @jsii.member(jsii_name="vpnEcmpSupport")
    def vpn_ecmp_support(self) -> typing.Optional[str]:
        """``AWS::EC2::TransitGateway.VpnEcmpSupport``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-vpnecmpsupport
        Stability:
            stable
        """
        return jsii.get(self, "vpnEcmpSupport")

    @vpn_ecmp_support.setter
    def vpn_ecmp_support(self, value: typing.Optional[str]):
        return jsii.set(self, "vpnEcmpSupport", value)


class CfnTransitGatewayAttachment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayAttachment"):
    """A CloudFormation ``AWS::EC2::TransitGatewayAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::TransitGatewayAttachment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, subnet_ids: typing.List[str], transit_gateway_id: str, vpc_id: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::TransitGatewayAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            subnet_ids: ``AWS::EC2::TransitGatewayAttachment.SubnetIds``.
            transit_gateway_id: ``AWS::EC2::TransitGatewayAttachment.TransitGatewayId``.
            vpc_id: ``AWS::EC2::TransitGatewayAttachment.VpcId``.
            tags: ``AWS::EC2::TransitGatewayAttachment.Tags``.

        Stability:
            experimental
        """
        props: CfnTransitGatewayAttachmentProps = {"subnetIds": subnet_ids, "transitGatewayId": transit_gateway_id, "vpcId": vpc_id}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnTransitGatewayAttachment, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::TransitGatewayAttachment.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html#cfn-ec2-transitgatewayattachment-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::EC2::TransitGatewayAttachment.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html#cfn-ec2-transitgatewayattachment-subnetids
        Stability:
            stable
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[str]):
        return jsii.set(self, "subnetIds", value)

    @property
    @jsii.member(jsii_name="transitGatewayId")
    def transit_gateway_id(self) -> str:
        """``AWS::EC2::TransitGatewayAttachment.TransitGatewayId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html#cfn-ec2-transitgatewayattachment-transitgatewayid
        Stability:
            stable
        """
        return jsii.get(self, "transitGatewayId")

    @transit_gateway_id.setter
    def transit_gateway_id(self, value: str):
        return jsii.set(self, "transitGatewayId", value)

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """``AWS::EC2::TransitGatewayAttachment.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html#cfn-ec2-transitgatewayattachment-vpcid
        Stability:
            stable
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: str):
        return jsii.set(self, "vpcId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnTransitGatewayAttachmentProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::TransitGatewayAttachment.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html#cfn-ec2-transitgatewayattachment-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayAttachmentProps", jsii_struct_bases=[_CfnTransitGatewayAttachmentProps])
class CfnTransitGatewayAttachmentProps(_CfnTransitGatewayAttachmentProps):
    """Properties for defining a ``AWS::EC2::TransitGatewayAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html
    Stability:
        stable
    """
    subnetIds: typing.List[str]
    """``AWS::EC2::TransitGatewayAttachment.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html#cfn-ec2-transitgatewayattachment-subnetids
    Stability:
        stable
    """

    transitGatewayId: str
    """``AWS::EC2::TransitGatewayAttachment.TransitGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html#cfn-ec2-transitgatewayattachment-transitgatewayid
    Stability:
        stable
    """

    vpcId: str
    """``AWS::EC2::TransitGatewayAttachment.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html#cfn-ec2-transitgatewayattachment-vpcid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayProps", jsii_struct_bases=[])
class CfnTransitGatewayProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::TransitGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html
    Stability:
        stable
    """
    amazonSideAsn: jsii.Number
    """``AWS::EC2::TransitGateway.AmazonSideAsn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-amazonsideasn
    Stability:
        stable
    """

    autoAcceptSharedAttachments: str
    """``AWS::EC2::TransitGateway.AutoAcceptSharedAttachments``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-autoacceptsharedattachments
    Stability:
        stable
    """

    defaultRouteTableAssociation: str
    """``AWS::EC2::TransitGateway.DefaultRouteTableAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-defaultroutetableassociation
    Stability:
        stable
    """

    defaultRouteTablePropagation: str
    """``AWS::EC2::TransitGateway.DefaultRouteTablePropagation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-defaultroutetablepropagation
    Stability:
        stable
    """

    description: str
    """``AWS::EC2::TransitGateway.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-description
    Stability:
        stable
    """

    dnsSupport: str
    """``AWS::EC2::TransitGateway.DnsSupport``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-dnssupport
    Stability:
        stable
    """

    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::TransitGateway.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-tags
    Stability:
        stable
    """

    vpnEcmpSupport: str
    """``AWS::EC2::TransitGateway.VpnEcmpSupport``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-vpnecmpsupport
    Stability:
        stable
    """

class CfnTransitGatewayRoute(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRoute"):
    """A CloudFormation ``AWS::EC2::TransitGatewayRoute``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::TransitGatewayRoute
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, transit_gateway_route_table_id: str, blackhole: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, destination_cidr_block: typing.Optional[str]=None, transit_gateway_attachment_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::TransitGatewayRoute``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            transit_gateway_route_table_id: ``AWS::EC2::TransitGatewayRoute.TransitGatewayRouteTableId``.
            blackhole: ``AWS::EC2::TransitGatewayRoute.Blackhole``.
            destination_cidr_block: ``AWS::EC2::TransitGatewayRoute.DestinationCidrBlock``.
            transit_gateway_attachment_id: ``AWS::EC2::TransitGatewayRoute.TransitGatewayAttachmentId``.

        Stability:
            experimental
        """
        props: CfnTransitGatewayRouteProps = {"transitGatewayRouteTableId": transit_gateway_route_table_id}

        if blackhole is not None:
            props["blackhole"] = blackhole

        if destination_cidr_block is not None:
            props["destinationCidrBlock"] = destination_cidr_block

        if transit_gateway_attachment_id is not None:
            props["transitGatewayAttachmentId"] = transit_gateway_attachment_id

        jsii.create(CfnTransitGatewayRoute, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="transitGatewayRouteTableId")
    def transit_gateway_route_table_id(self) -> str:
        """``AWS::EC2::TransitGatewayRoute.TransitGatewayRouteTableId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html#cfn-ec2-transitgatewayroute-transitgatewayroutetableid
        Stability:
            stable
        """
        return jsii.get(self, "transitGatewayRouteTableId")

    @transit_gateway_route_table_id.setter
    def transit_gateway_route_table_id(self, value: str):
        return jsii.set(self, "transitGatewayRouteTableId", value)

    @property
    @jsii.member(jsii_name="blackhole")
    def blackhole(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::TransitGatewayRoute.Blackhole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html#cfn-ec2-transitgatewayroute-blackhole
        Stability:
            stable
        """
        return jsii.get(self, "blackhole")

    @blackhole.setter
    def blackhole(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "blackhole", value)

    @property
    @jsii.member(jsii_name="destinationCidrBlock")
    def destination_cidr_block(self) -> typing.Optional[str]:
        """``AWS::EC2::TransitGatewayRoute.DestinationCidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html#cfn-ec2-transitgatewayroute-destinationcidrblock
        Stability:
            stable
        """
        return jsii.get(self, "destinationCidrBlock")

    @destination_cidr_block.setter
    def destination_cidr_block(self, value: typing.Optional[str]):
        return jsii.set(self, "destinationCidrBlock", value)

    @property
    @jsii.member(jsii_name="transitGatewayAttachmentId")
    def transit_gateway_attachment_id(self) -> typing.Optional[str]:
        """``AWS::EC2::TransitGatewayRoute.TransitGatewayAttachmentId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html#cfn-ec2-transitgatewayroute-transitgatewayattachmentid
        Stability:
            stable
        """
        return jsii.get(self, "transitGatewayAttachmentId")

    @transit_gateway_attachment_id.setter
    def transit_gateway_attachment_id(self, value: typing.Optional[str]):
        return jsii.set(self, "transitGatewayAttachmentId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnTransitGatewayRouteProps(jsii.compat.TypedDict, total=False):
    blackhole: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::TransitGatewayRoute.Blackhole``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html#cfn-ec2-transitgatewayroute-blackhole
    Stability:
        stable
    """
    destinationCidrBlock: str
    """``AWS::EC2::TransitGatewayRoute.DestinationCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html#cfn-ec2-transitgatewayroute-destinationcidrblock
    Stability:
        stable
    """
    transitGatewayAttachmentId: str
    """``AWS::EC2::TransitGatewayRoute.TransitGatewayAttachmentId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html#cfn-ec2-transitgatewayroute-transitgatewayattachmentid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteProps", jsii_struct_bases=[_CfnTransitGatewayRouteProps])
class CfnTransitGatewayRouteProps(_CfnTransitGatewayRouteProps):
    """Properties for defining a ``AWS::EC2::TransitGatewayRoute``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html
    Stability:
        stable
    """
    transitGatewayRouteTableId: str
    """``AWS::EC2::TransitGatewayRoute.TransitGatewayRouteTableId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html#cfn-ec2-transitgatewayroute-transitgatewayroutetableid
    Stability:
        stable
    """

class CfnTransitGatewayRouteTable(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteTable"):
    """A CloudFormation ``AWS::EC2::TransitGatewayRouteTable``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetable.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::TransitGatewayRouteTable
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, transit_gateway_id: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::TransitGatewayRouteTable``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            transit_gateway_id: ``AWS::EC2::TransitGatewayRouteTable.TransitGatewayId``.
            tags: ``AWS::EC2::TransitGatewayRouteTable.Tags``.

        Stability:
            experimental
        """
        props: CfnTransitGatewayRouteTableProps = {"transitGatewayId": transit_gateway_id}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnTransitGatewayRouteTable, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::TransitGatewayRouteTable.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetable.html#cfn-ec2-transitgatewayroutetable-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="transitGatewayId")
    def transit_gateway_id(self) -> str:
        """``AWS::EC2::TransitGatewayRouteTable.TransitGatewayId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetable.html#cfn-ec2-transitgatewayroutetable-transitgatewayid
        Stability:
            stable
        """
        return jsii.get(self, "transitGatewayId")

    @transit_gateway_id.setter
    def transit_gateway_id(self, value: str):
        return jsii.set(self, "transitGatewayId", value)


class CfnTransitGatewayRouteTableAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteTableAssociation"):
    """A CloudFormation ``AWS::EC2::TransitGatewayRouteTableAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetableassociation.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::TransitGatewayRouteTableAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, transit_gateway_attachment_id: str, transit_gateway_route_table_id: str) -> None:
        """Create a new ``AWS::EC2::TransitGatewayRouteTableAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            transit_gateway_attachment_id: ``AWS::EC2::TransitGatewayRouteTableAssociation.TransitGatewayAttachmentId``.
            transit_gateway_route_table_id: ``AWS::EC2::TransitGatewayRouteTableAssociation.TransitGatewayRouteTableId``.

        Stability:
            experimental
        """
        props: CfnTransitGatewayRouteTableAssociationProps = {"transitGatewayAttachmentId": transit_gateway_attachment_id, "transitGatewayRouteTableId": transit_gateway_route_table_id}

        jsii.create(CfnTransitGatewayRouteTableAssociation, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="transitGatewayAttachmentId")
    def transit_gateway_attachment_id(self) -> str:
        """``AWS::EC2::TransitGatewayRouteTableAssociation.TransitGatewayAttachmentId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetableassociation.html#cfn-ec2-transitgatewayroutetableassociation-transitgatewayattachmentid
        Stability:
            stable
        """
        return jsii.get(self, "transitGatewayAttachmentId")

    @transit_gateway_attachment_id.setter
    def transit_gateway_attachment_id(self, value: str):
        return jsii.set(self, "transitGatewayAttachmentId", value)

    @property
    @jsii.member(jsii_name="transitGatewayRouteTableId")
    def transit_gateway_route_table_id(self) -> str:
        """``AWS::EC2::TransitGatewayRouteTableAssociation.TransitGatewayRouteTableId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetableassociation.html#cfn-ec2-transitgatewayroutetableassociation-transitgatewayroutetableid
        Stability:
            stable
        """
        return jsii.get(self, "transitGatewayRouteTableId")

    @transit_gateway_route_table_id.setter
    def transit_gateway_route_table_id(self, value: str):
        return jsii.set(self, "transitGatewayRouteTableId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteTableAssociationProps", jsii_struct_bases=[])
class CfnTransitGatewayRouteTableAssociationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::TransitGatewayRouteTableAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetableassociation.html
    Stability:
        stable
    """
    transitGatewayAttachmentId: str
    """``AWS::EC2::TransitGatewayRouteTableAssociation.TransitGatewayAttachmentId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetableassociation.html#cfn-ec2-transitgatewayroutetableassociation-transitgatewayattachmentid
    Stability:
        stable
    """

    transitGatewayRouteTableId: str
    """``AWS::EC2::TransitGatewayRouteTableAssociation.TransitGatewayRouteTableId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetableassociation.html#cfn-ec2-transitgatewayroutetableassociation-transitgatewayroutetableid
    Stability:
        stable
    """

class CfnTransitGatewayRouteTablePropagation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteTablePropagation"):
    """A CloudFormation ``AWS::EC2::TransitGatewayRouteTablePropagation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetablepropagation.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::TransitGatewayRouteTablePropagation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, transit_gateway_attachment_id: str, transit_gateway_route_table_id: str) -> None:
        """Create a new ``AWS::EC2::TransitGatewayRouteTablePropagation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            transit_gateway_attachment_id: ``AWS::EC2::TransitGatewayRouteTablePropagation.TransitGatewayAttachmentId``.
            transit_gateway_route_table_id: ``AWS::EC2::TransitGatewayRouteTablePropagation.TransitGatewayRouteTableId``.

        Stability:
            experimental
        """
        props: CfnTransitGatewayRouteTablePropagationProps = {"transitGatewayAttachmentId": transit_gateway_attachment_id, "transitGatewayRouteTableId": transit_gateway_route_table_id}

        jsii.create(CfnTransitGatewayRouteTablePropagation, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="transitGatewayAttachmentId")
    def transit_gateway_attachment_id(self) -> str:
        """``AWS::EC2::TransitGatewayRouteTablePropagation.TransitGatewayAttachmentId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetablepropagation.html#cfn-ec2-transitgatewayroutetablepropagation-transitgatewayattachmentid
        Stability:
            stable
        """
        return jsii.get(self, "transitGatewayAttachmentId")

    @transit_gateway_attachment_id.setter
    def transit_gateway_attachment_id(self, value: str):
        return jsii.set(self, "transitGatewayAttachmentId", value)

    @property
    @jsii.member(jsii_name="transitGatewayRouteTableId")
    def transit_gateway_route_table_id(self) -> str:
        """``AWS::EC2::TransitGatewayRouteTablePropagation.TransitGatewayRouteTableId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetablepropagation.html#cfn-ec2-transitgatewayroutetablepropagation-transitgatewayroutetableid
        Stability:
            stable
        """
        return jsii.get(self, "transitGatewayRouteTableId")

    @transit_gateway_route_table_id.setter
    def transit_gateway_route_table_id(self, value: str):
        return jsii.set(self, "transitGatewayRouteTableId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteTablePropagationProps", jsii_struct_bases=[])
class CfnTransitGatewayRouteTablePropagationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::TransitGatewayRouteTablePropagation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetablepropagation.html
    Stability:
        stable
    """
    transitGatewayAttachmentId: str
    """``AWS::EC2::TransitGatewayRouteTablePropagation.TransitGatewayAttachmentId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetablepropagation.html#cfn-ec2-transitgatewayroutetablepropagation-transitgatewayattachmentid
    Stability:
        stable
    """

    transitGatewayRouteTableId: str
    """``AWS::EC2::TransitGatewayRouteTablePropagation.TransitGatewayRouteTableId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetablepropagation.html#cfn-ec2-transitgatewayroutetablepropagation-transitgatewayroutetableid
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnTransitGatewayRouteTableProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::TransitGatewayRouteTable.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetable.html#cfn-ec2-transitgatewayroutetable-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteTableProps", jsii_struct_bases=[_CfnTransitGatewayRouteTableProps])
class CfnTransitGatewayRouteTableProps(_CfnTransitGatewayRouteTableProps):
    """Properties for defining a ``AWS::EC2::TransitGatewayRouteTable``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetable.html
    Stability:
        stable
    """
    transitGatewayId: str
    """``AWS::EC2::TransitGatewayRouteTable.TransitGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetable.html#cfn-ec2-transitgatewayroutetable-transitgatewayid
    Stability:
        stable
    """

class CfnVPC(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPC"):
    """A CloudFormation ``AWS::EC2::VPC``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPC
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, cidr_block: str, enable_dns_hostnames: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, enable_dns_support: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, instance_tenancy: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::VPC``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            cidr_block: ``AWS::EC2::VPC.CidrBlock``.
            enable_dns_hostnames: ``AWS::EC2::VPC.EnableDnsHostnames``.
            enable_dns_support: ``AWS::EC2::VPC.EnableDnsSupport``.
            instance_tenancy: ``AWS::EC2::VPC.InstanceTenancy``.
            tags: ``AWS::EC2::VPC.Tags``.

        Stability:
            experimental
        """
        props: CfnVPCProps = {"cidrBlock": cidr_block}

        if enable_dns_hostnames is not None:
            props["enableDnsHostnames"] = enable_dns_hostnames

        if enable_dns_support is not None:
            props["enableDnsSupport"] = enable_dns_support

        if instance_tenancy is not None:
            props["instanceTenancy"] = instance_tenancy

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnVPC, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrCidrBlock")
    def attr_cidr_block(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            CidrBlock
        """
        return jsii.get(self, "attrCidrBlock")

    @property
    @jsii.member(jsii_name="attrCidrBlockAssociations")
    def attr_cidr_block_associations(self) -> typing.List[str]:
        """
        Stability:
            stable
        cloudformationAttribute:
            CidrBlockAssociations
        """
        return jsii.get(self, "attrCidrBlockAssociations")

    @property
    @jsii.member(jsii_name="attrDefaultNetworkAcl")
    def attr_default_network_acl(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            DefaultNetworkAcl
        """
        return jsii.get(self, "attrDefaultNetworkAcl")

    @property
    @jsii.member(jsii_name="attrDefaultSecurityGroup")
    def attr_default_security_group(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            DefaultSecurityGroup
        """
        return jsii.get(self, "attrDefaultSecurityGroup")

    @property
    @jsii.member(jsii_name="attrIpv6CidrBlocks")
    def attr_ipv6_cidr_blocks(self) -> typing.List[str]:
        """
        Stability:
            stable
        cloudformationAttribute:
            Ipv6CidrBlocks
        """
        return jsii.get(self, "attrIpv6CidrBlocks")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::VPC.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="cidrBlock")
    def cidr_block(self) -> str:
        """``AWS::EC2::VPC.CidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-cidrblock
        Stability:
            stable
        """
        return jsii.get(self, "cidrBlock")

    @cidr_block.setter
    def cidr_block(self, value: str):
        return jsii.set(self, "cidrBlock", value)

    @property
    @jsii.member(jsii_name="enableDnsHostnames")
    def enable_dns_hostnames(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::VPC.EnableDnsHostnames``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-EnableDnsHostnames
        Stability:
            stable
        """
        return jsii.get(self, "enableDnsHostnames")

    @enable_dns_hostnames.setter
    def enable_dns_hostnames(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enableDnsHostnames", value)

    @property
    @jsii.member(jsii_name="enableDnsSupport")
    def enable_dns_support(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::VPC.EnableDnsSupport``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-EnableDnsSupport
        Stability:
            stable
        """
        return jsii.get(self, "enableDnsSupport")

    @enable_dns_support.setter
    def enable_dns_support(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enableDnsSupport", value)

    @property
    @jsii.member(jsii_name="instanceTenancy")
    def instance_tenancy(self) -> typing.Optional[str]:
        """``AWS::EC2::VPC.InstanceTenancy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-instancetenancy
        Stability:
            stable
        """
        return jsii.get(self, "instanceTenancy")

    @instance_tenancy.setter
    def instance_tenancy(self, value: typing.Optional[str]):
        return jsii.set(self, "instanceTenancy", value)


class CfnVPCCidrBlock(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCCidrBlock"):
    """A CloudFormation ``AWS::EC2::VPCCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPCCidrBlock
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, vpc_id: str, amazon_provided_ipv6_cidr_block: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, cidr_block: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::VPCCidrBlock``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            vpc_id: ``AWS::EC2::VPCCidrBlock.VpcId``.
            amazon_provided_ipv6_cidr_block: ``AWS::EC2::VPCCidrBlock.AmazonProvidedIpv6CidrBlock``.
            cidr_block: ``AWS::EC2::VPCCidrBlock.CidrBlock``.

        Stability:
            experimental
        """
        props: CfnVPCCidrBlockProps = {"vpcId": vpc_id}

        if amazon_provided_ipv6_cidr_block is not None:
            props["amazonProvidedIpv6CidrBlock"] = amazon_provided_ipv6_cidr_block

        if cidr_block is not None:
            props["cidrBlock"] = cidr_block

        jsii.create(CfnVPCCidrBlock, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """``AWS::EC2::VPCCidrBlock.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html#cfn-ec2-vpccidrblock-vpcid
        Stability:
            stable
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: str):
        return jsii.set(self, "vpcId", value)

    @property
    @jsii.member(jsii_name="amazonProvidedIpv6CidrBlock")
    def amazon_provided_ipv6_cidr_block(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::VPCCidrBlock.AmazonProvidedIpv6CidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html#cfn-ec2-vpccidrblock-amazonprovidedipv6cidrblock
        Stability:
            stable
        """
        return jsii.get(self, "amazonProvidedIpv6CidrBlock")

    @amazon_provided_ipv6_cidr_block.setter
    def amazon_provided_ipv6_cidr_block(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "amazonProvidedIpv6CidrBlock", value)

    @property
    @jsii.member(jsii_name="cidrBlock")
    def cidr_block(self) -> typing.Optional[str]:
        """``AWS::EC2::VPCCidrBlock.CidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html#cfn-ec2-vpccidrblock-cidrblock
        Stability:
            stable
        """
        return jsii.get(self, "cidrBlock")

    @cidr_block.setter
    def cidr_block(self, value: typing.Optional[str]):
        return jsii.set(self, "cidrBlock", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCCidrBlockProps(jsii.compat.TypedDict, total=False):
    amazonProvidedIpv6CidrBlock: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::VPCCidrBlock.AmazonProvidedIpv6CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html#cfn-ec2-vpccidrblock-amazonprovidedipv6cidrblock
    Stability:
        stable
    """
    cidrBlock: str
    """``AWS::EC2::VPCCidrBlock.CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html#cfn-ec2-vpccidrblock-cidrblock
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCCidrBlockProps", jsii_struct_bases=[_CfnVPCCidrBlockProps])
class CfnVPCCidrBlockProps(_CfnVPCCidrBlockProps):
    """Properties for defining a ``AWS::EC2::VPCCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html
    Stability:
        stable
    """
    vpcId: str
    """``AWS::EC2::VPCCidrBlock.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html#cfn-ec2-vpccidrblock-vpcid
    Stability:
        stable
    """

class CfnVPCDHCPOptionsAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCDHCPOptionsAssociation"):
    """A CloudFormation ``AWS::EC2::VPCDHCPOptionsAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-dhcp-options-assoc.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPCDHCPOptionsAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, dhcp_options_id: str, vpc_id: str) -> None:
        """Create a new ``AWS::EC2::VPCDHCPOptionsAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            dhcp_options_id: ``AWS::EC2::VPCDHCPOptionsAssociation.DhcpOptionsId``.
            vpc_id: ``AWS::EC2::VPCDHCPOptionsAssociation.VpcId``.

        Stability:
            experimental
        """
        props: CfnVPCDHCPOptionsAssociationProps = {"dhcpOptionsId": dhcp_options_id, "vpcId": vpc_id}

        jsii.create(CfnVPCDHCPOptionsAssociation, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="dhcpOptionsId")
    def dhcp_options_id(self) -> str:
        """``AWS::EC2::VPCDHCPOptionsAssociation.DhcpOptionsId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-dhcp-options-assoc.html#cfn-ec2-vpcdhcpoptionsassociation-dhcpoptionsid
        Stability:
            stable
        """
        return jsii.get(self, "dhcpOptionsId")

    @dhcp_options_id.setter
    def dhcp_options_id(self, value: str):
        return jsii.set(self, "dhcpOptionsId", value)

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """``AWS::EC2::VPCDHCPOptionsAssociation.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-dhcp-options-assoc.html#cfn-ec2-vpcdhcpoptionsassociation-vpcid
        Stability:
            stable
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: str):
        return jsii.set(self, "vpcId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCDHCPOptionsAssociationProps", jsii_struct_bases=[])
class CfnVPCDHCPOptionsAssociationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::VPCDHCPOptionsAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-dhcp-options-assoc.html
    Stability:
        stable
    """
    dhcpOptionsId: str
    """``AWS::EC2::VPCDHCPOptionsAssociation.DhcpOptionsId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-dhcp-options-assoc.html#cfn-ec2-vpcdhcpoptionsassociation-dhcpoptionsid
    Stability:
        stable
    """

    vpcId: str
    """``AWS::EC2::VPCDHCPOptionsAssociation.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-dhcp-options-assoc.html#cfn-ec2-vpcdhcpoptionsassociation-vpcid
    Stability:
        stable
    """

class CfnVPCEndpoint(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpoint"):
    """A CloudFormation ``AWS::EC2::VPCEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPCEndpoint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, service_name: str, vpc_id: str, policy_document: typing.Any=None, private_dns_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, route_table_ids: typing.Optional[typing.List[str]]=None, security_group_ids: typing.Optional[typing.List[str]]=None, subnet_ids: typing.Optional[typing.List[str]]=None, vpc_endpoint_type: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::VPCEndpoint``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            service_name: ``AWS::EC2::VPCEndpoint.ServiceName``.
            vpc_id: ``AWS::EC2::VPCEndpoint.VpcId``.
            policy_document: ``AWS::EC2::VPCEndpoint.PolicyDocument``.
            private_dns_enabled: ``AWS::EC2::VPCEndpoint.PrivateDnsEnabled``.
            route_table_ids: ``AWS::EC2::VPCEndpoint.RouteTableIds``.
            security_group_ids: ``AWS::EC2::VPCEndpoint.SecurityGroupIds``.
            subnet_ids: ``AWS::EC2::VPCEndpoint.SubnetIds``.
            vpc_endpoint_type: ``AWS::EC2::VPCEndpoint.VpcEndpointType``.

        Stability:
            experimental
        """
        props: CfnVPCEndpointProps = {"serviceName": service_name, "vpcId": vpc_id}

        if policy_document is not None:
            props["policyDocument"] = policy_document

        if private_dns_enabled is not None:
            props["privateDnsEnabled"] = private_dns_enabled

        if route_table_ids is not None:
            props["routeTableIds"] = route_table_ids

        if security_group_ids is not None:
            props["securityGroupIds"] = security_group_ids

        if subnet_ids is not None:
            props["subnetIds"] = subnet_ids

        if vpc_endpoint_type is not None:
            props["vpcEndpointType"] = vpc_endpoint_type

        jsii.create(CfnVPCEndpoint, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrCreationTimestamp")
    def attr_creation_timestamp(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            CreationTimestamp
        """
        return jsii.get(self, "attrCreationTimestamp")

    @property
    @jsii.member(jsii_name="attrDnsEntries")
    def attr_dns_entries(self) -> typing.List[str]:
        """
        Stability:
            stable
        cloudformationAttribute:
            DnsEntries
        """
        return jsii.get(self, "attrDnsEntries")

    @property
    @jsii.member(jsii_name="attrNetworkInterfaceIds")
    def attr_network_interface_ids(self) -> typing.List[str]:
        """
        Stability:
            stable
        cloudformationAttribute:
            NetworkInterfaceIds
        """
        return jsii.get(self, "attrNetworkInterfaceIds")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="policyDocument")
    def policy_document(self) -> typing.Any:
        """``AWS::EC2::VPCEndpoint.PolicyDocument``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-policydocument
        Stability:
            stable
        """
        return jsii.get(self, "policyDocument")

    @policy_document.setter
    def policy_document(self, value: typing.Any):
        return jsii.set(self, "policyDocument", value)

    @property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> str:
        """``AWS::EC2::VPCEndpoint.ServiceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-servicename
        Stability:
            stable
        """
        return jsii.get(self, "serviceName")

    @service_name.setter
    def service_name(self, value: str):
        return jsii.set(self, "serviceName", value)

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """``AWS::EC2::VPCEndpoint.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-vpcid
        Stability:
            stable
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: str):
        return jsii.set(self, "vpcId", value)

    @property
    @jsii.member(jsii_name="privateDnsEnabled")
    def private_dns_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::VPCEndpoint.PrivateDnsEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-privatednsenabled
        Stability:
            stable
        """
        return jsii.get(self, "privateDnsEnabled")

    @private_dns_enabled.setter
    def private_dns_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "privateDnsEnabled", value)

    @property
    @jsii.member(jsii_name="routeTableIds")
    def route_table_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::EC2::VPCEndpoint.RouteTableIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-routetableids
        Stability:
            stable
        """
        return jsii.get(self, "routeTableIds")

    @route_table_ids.setter
    def route_table_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "routeTableIds", value)

    @property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::EC2::VPCEndpoint.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-securitygroupids
        Stability:
            stable
        """
        return jsii.get(self, "securityGroupIds")

    @security_group_ids.setter
    def security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "securityGroupIds", value)

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::EC2::VPCEndpoint.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-subnetids
        Stability:
            stable
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "subnetIds", value)

    @property
    @jsii.member(jsii_name="vpcEndpointType")
    def vpc_endpoint_type(self) -> typing.Optional[str]:
        """``AWS::EC2::VPCEndpoint.VpcEndpointType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-vpcendpointtype
        Stability:
            stable
        """
        return jsii.get(self, "vpcEndpointType")

    @vpc_endpoint_type.setter
    def vpc_endpoint_type(self, value: typing.Optional[str]):
        return jsii.set(self, "vpcEndpointType", value)


class CfnVPCEndpointConnectionNotification(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointConnectionNotification"):
    """A CloudFormation ``AWS::EC2::VPCEndpointConnectionNotification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPCEndpointConnectionNotification
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, connection_events: typing.List[str], connection_notification_arn: str, service_id: typing.Optional[str]=None, vpc_endpoint_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::VPCEndpointConnectionNotification``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            connection_events: ``AWS::EC2::VPCEndpointConnectionNotification.ConnectionEvents``.
            connection_notification_arn: ``AWS::EC2::VPCEndpointConnectionNotification.ConnectionNotificationArn``.
            service_id: ``AWS::EC2::VPCEndpointConnectionNotification.ServiceId``.
            vpc_endpoint_id: ``AWS::EC2::VPCEndpointConnectionNotification.VPCEndpointId``.

        Stability:
            experimental
        """
        props: CfnVPCEndpointConnectionNotificationProps = {"connectionEvents": connection_events, "connectionNotificationArn": connection_notification_arn}

        if service_id is not None:
            props["serviceId"] = service_id

        if vpc_endpoint_id is not None:
            props["vpcEndpointId"] = vpc_endpoint_id

        jsii.create(CfnVPCEndpointConnectionNotification, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="connectionEvents")
    def connection_events(self) -> typing.List[str]:
        """``AWS::EC2::VPCEndpointConnectionNotification.ConnectionEvents``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html#cfn-ec2-vpcendpointconnectionnotification-connectionevents
        Stability:
            stable
        """
        return jsii.get(self, "connectionEvents")

    @connection_events.setter
    def connection_events(self, value: typing.List[str]):
        return jsii.set(self, "connectionEvents", value)

    @property
    @jsii.member(jsii_name="connectionNotificationArn")
    def connection_notification_arn(self) -> str:
        """``AWS::EC2::VPCEndpointConnectionNotification.ConnectionNotificationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html#cfn-ec2-vpcendpointconnectionnotification-connectionnotificationarn
        Stability:
            stable
        """
        return jsii.get(self, "connectionNotificationArn")

    @connection_notification_arn.setter
    def connection_notification_arn(self, value: str):
        return jsii.set(self, "connectionNotificationArn", value)

    @property
    @jsii.member(jsii_name="serviceId")
    def service_id(self) -> typing.Optional[str]:
        """``AWS::EC2::VPCEndpointConnectionNotification.ServiceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html#cfn-ec2-vpcendpointconnectionnotification-serviceid
        Stability:
            stable
        """
        return jsii.get(self, "serviceId")

    @service_id.setter
    def service_id(self, value: typing.Optional[str]):
        return jsii.set(self, "serviceId", value)

    @property
    @jsii.member(jsii_name="vpcEndpointId")
    def vpc_endpoint_id(self) -> typing.Optional[str]:
        """``AWS::EC2::VPCEndpointConnectionNotification.VPCEndpointId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html#cfn-ec2-vpcendpointconnectionnotification-vpcendpointid
        Stability:
            stable
        """
        return jsii.get(self, "vpcEndpointId")

    @vpc_endpoint_id.setter
    def vpc_endpoint_id(self, value: typing.Optional[str]):
        return jsii.set(self, "vpcEndpointId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCEndpointConnectionNotificationProps(jsii.compat.TypedDict, total=False):
    serviceId: str
    """``AWS::EC2::VPCEndpointConnectionNotification.ServiceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html#cfn-ec2-vpcendpointconnectionnotification-serviceid
    Stability:
        stable
    """
    vpcEndpointId: str
    """``AWS::EC2::VPCEndpointConnectionNotification.VPCEndpointId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html#cfn-ec2-vpcendpointconnectionnotification-vpcendpointid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointConnectionNotificationProps", jsii_struct_bases=[_CfnVPCEndpointConnectionNotificationProps])
class CfnVPCEndpointConnectionNotificationProps(_CfnVPCEndpointConnectionNotificationProps):
    """Properties for defining a ``AWS::EC2::VPCEndpointConnectionNotification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html
    Stability:
        stable
    """
    connectionEvents: typing.List[str]
    """``AWS::EC2::VPCEndpointConnectionNotification.ConnectionEvents``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html#cfn-ec2-vpcendpointconnectionnotification-connectionevents
    Stability:
        stable
    """

    connectionNotificationArn: str
    """``AWS::EC2::VPCEndpointConnectionNotification.ConnectionNotificationArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html#cfn-ec2-vpcendpointconnectionnotification-connectionnotificationarn
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCEndpointProps(jsii.compat.TypedDict, total=False):
    policyDocument: typing.Any
    """``AWS::EC2::VPCEndpoint.PolicyDocument``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-policydocument
    Stability:
        stable
    """
    privateDnsEnabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::VPCEndpoint.PrivateDnsEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-privatednsenabled
    Stability:
        stable
    """
    routeTableIds: typing.List[str]
    """``AWS::EC2::VPCEndpoint.RouteTableIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-routetableids
    Stability:
        stable
    """
    securityGroupIds: typing.List[str]
    """``AWS::EC2::VPCEndpoint.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-securitygroupids
    Stability:
        stable
    """
    subnetIds: typing.List[str]
    """``AWS::EC2::VPCEndpoint.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-subnetids
    Stability:
        stable
    """
    vpcEndpointType: str
    """``AWS::EC2::VPCEndpoint.VpcEndpointType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-vpcendpointtype
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointProps", jsii_struct_bases=[_CfnVPCEndpointProps])
class CfnVPCEndpointProps(_CfnVPCEndpointProps):
    """Properties for defining a ``AWS::EC2::VPCEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html
    Stability:
        stable
    """
    serviceName: str
    """``AWS::EC2::VPCEndpoint.ServiceName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-servicename
    Stability:
        stable
    """

    vpcId: str
    """``AWS::EC2::VPCEndpoint.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-vpcid
    Stability:
        stable
    """

class CfnVPCEndpointService(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointService"):
    """A CloudFormation ``AWS::EC2::VPCEndpointService``.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservice.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPCEndpointService
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, network_load_balancer_arns: typing.List[str], acceptance_required: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::EC2::VPCEndpointService``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            network_load_balancer_arns: ``AWS::EC2::VPCEndpointService.NetworkLoadBalancerArns``.
            acceptance_required: ``AWS::EC2::VPCEndpointService.AcceptanceRequired``.

        Stability:
            experimental
        """
        props: CfnVPCEndpointServiceProps = {"networkLoadBalancerArns": network_load_balancer_arns}

        if acceptance_required is not None:
            props["acceptanceRequired"] = acceptance_required

        jsii.create(CfnVPCEndpointService, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="networkLoadBalancerArns")
    def network_load_balancer_arns(self) -> typing.List[str]:
        """``AWS::EC2::VPCEndpointService.NetworkLoadBalancerArns``.

        See:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservice.html#cfn-ec2-vpcendpointservice-networkloadbalancerarns
        Stability:
            stable
        """
        return jsii.get(self, "networkLoadBalancerArns")

    @network_load_balancer_arns.setter
    def network_load_balancer_arns(self, value: typing.List[str]):
        return jsii.set(self, "networkLoadBalancerArns", value)

    @property
    @jsii.member(jsii_name="acceptanceRequired")
    def acceptance_required(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::VPCEndpointService.AcceptanceRequired``.

        See:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservice.html#cfn-ec2-vpcendpointservice-acceptancerequired
        Stability:
            stable
        """
        return jsii.get(self, "acceptanceRequired")

    @acceptance_required.setter
    def acceptance_required(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "acceptanceRequired", value)


class CfnVPCEndpointServicePermissions(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointServicePermissions"):
    """A CloudFormation ``AWS::EC2::VPCEndpointServicePermissions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservicepermissions.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPCEndpointServicePermissions
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, service_id: str, allowed_principals: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::EC2::VPCEndpointServicePermissions``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            service_id: ``AWS::EC2::VPCEndpointServicePermissions.ServiceId``.
            allowed_principals: ``AWS::EC2::VPCEndpointServicePermissions.AllowedPrincipals``.

        Stability:
            experimental
        """
        props: CfnVPCEndpointServicePermissionsProps = {"serviceId": service_id}

        if allowed_principals is not None:
            props["allowedPrincipals"] = allowed_principals

        jsii.create(CfnVPCEndpointServicePermissions, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="serviceId")
    def service_id(self) -> str:
        """``AWS::EC2::VPCEndpointServicePermissions.ServiceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservicepermissions.html#cfn-ec2-vpcendpointservicepermissions-serviceid
        Stability:
            stable
        """
        return jsii.get(self, "serviceId")

    @service_id.setter
    def service_id(self, value: str):
        return jsii.set(self, "serviceId", value)

    @property
    @jsii.member(jsii_name="allowedPrincipals")
    def allowed_principals(self) -> typing.Optional[typing.List[str]]:
        """``AWS::EC2::VPCEndpointServicePermissions.AllowedPrincipals``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservicepermissions.html#cfn-ec2-vpcendpointservicepermissions-allowedprincipals
        Stability:
            stable
        """
        return jsii.get(self, "allowedPrincipals")

    @allowed_principals.setter
    def allowed_principals(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "allowedPrincipals", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCEndpointServicePermissionsProps(jsii.compat.TypedDict, total=False):
    allowedPrincipals: typing.List[str]
    """``AWS::EC2::VPCEndpointServicePermissions.AllowedPrincipals``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservicepermissions.html#cfn-ec2-vpcendpointservicepermissions-allowedprincipals
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointServicePermissionsProps", jsii_struct_bases=[_CfnVPCEndpointServicePermissionsProps])
class CfnVPCEndpointServicePermissionsProps(_CfnVPCEndpointServicePermissionsProps):
    """Properties for defining a ``AWS::EC2::VPCEndpointServicePermissions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservicepermissions.html
    Stability:
        stable
    """
    serviceId: str
    """``AWS::EC2::VPCEndpointServicePermissions.ServiceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservicepermissions.html#cfn-ec2-vpcendpointservicepermissions-serviceid
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCEndpointServiceProps(jsii.compat.TypedDict, total=False):
    acceptanceRequired: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::VPCEndpointService.AcceptanceRequired``.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservice.html#cfn-ec2-vpcendpointservice-acceptancerequired
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointServiceProps", jsii_struct_bases=[_CfnVPCEndpointServiceProps])
class CfnVPCEndpointServiceProps(_CfnVPCEndpointServiceProps):
    """Properties for defining a ``AWS::EC2::VPCEndpointService``.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservice.html
    Stability:
        stable
    """
    networkLoadBalancerArns: typing.List[str]
    """``AWS::EC2::VPCEndpointService.NetworkLoadBalancerArns``.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservice.html#cfn-ec2-vpcendpointservice-networkloadbalancerarns
    Stability:
        stable
    """

class CfnVPCGatewayAttachment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCGatewayAttachment"):
    """A CloudFormation ``AWS::EC2::VPCGatewayAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPCGatewayAttachment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, vpc_id: str, internet_gateway_id: typing.Optional[str]=None, vpn_gateway_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::VPCGatewayAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            vpc_id: ``AWS::EC2::VPCGatewayAttachment.VpcId``.
            internet_gateway_id: ``AWS::EC2::VPCGatewayAttachment.InternetGatewayId``.
            vpn_gateway_id: ``AWS::EC2::VPCGatewayAttachment.VpnGatewayId``.

        Stability:
            experimental
        """
        props: CfnVPCGatewayAttachmentProps = {"vpcId": vpc_id}

        if internet_gateway_id is not None:
            props["internetGatewayId"] = internet_gateway_id

        if vpn_gateway_id is not None:
            props["vpnGatewayId"] = vpn_gateway_id

        jsii.create(CfnVPCGatewayAttachment, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """``AWS::EC2::VPCGatewayAttachment.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html#cfn-ec2-vpcgatewayattachment-vpcid
        Stability:
            stable
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: str):
        return jsii.set(self, "vpcId", value)

    @property
    @jsii.member(jsii_name="internetGatewayId")
    def internet_gateway_id(self) -> typing.Optional[str]:
        """``AWS::EC2::VPCGatewayAttachment.InternetGatewayId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html#cfn-ec2-vpcgatewayattachment-internetgatewayid
        Stability:
            stable
        """
        return jsii.get(self, "internetGatewayId")

    @internet_gateway_id.setter
    def internet_gateway_id(self, value: typing.Optional[str]):
        return jsii.set(self, "internetGatewayId", value)

    @property
    @jsii.member(jsii_name="vpnGatewayId")
    def vpn_gateway_id(self) -> typing.Optional[str]:
        """``AWS::EC2::VPCGatewayAttachment.VpnGatewayId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html#cfn-ec2-vpcgatewayattachment-vpngatewayid
        Stability:
            stable
        """
        return jsii.get(self, "vpnGatewayId")

    @vpn_gateway_id.setter
    def vpn_gateway_id(self, value: typing.Optional[str]):
        return jsii.set(self, "vpnGatewayId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCGatewayAttachmentProps(jsii.compat.TypedDict, total=False):
    internetGatewayId: str
    """``AWS::EC2::VPCGatewayAttachment.InternetGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html#cfn-ec2-vpcgatewayattachment-internetgatewayid
    Stability:
        stable
    """
    vpnGatewayId: str
    """``AWS::EC2::VPCGatewayAttachment.VpnGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html#cfn-ec2-vpcgatewayattachment-vpngatewayid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCGatewayAttachmentProps", jsii_struct_bases=[_CfnVPCGatewayAttachmentProps])
class CfnVPCGatewayAttachmentProps(_CfnVPCGatewayAttachmentProps):
    """Properties for defining a ``AWS::EC2::VPCGatewayAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html
    Stability:
        stable
    """
    vpcId: str
    """``AWS::EC2::VPCGatewayAttachment.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html#cfn-ec2-vpcgatewayattachment-vpcid
    Stability:
        stable
    """

class CfnVPCPeeringConnection(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCPeeringConnection"):
    """A CloudFormation ``AWS::EC2::VPCPeeringConnection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPCPeeringConnection
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, peer_vpc_id: str, vpc_id: str, peer_owner_id: typing.Optional[str]=None, peer_region: typing.Optional[str]=None, peer_role_arn: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::VPCPeeringConnection``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            peer_vpc_id: ``AWS::EC2::VPCPeeringConnection.PeerVpcId``.
            vpc_id: ``AWS::EC2::VPCPeeringConnection.VpcId``.
            peer_owner_id: ``AWS::EC2::VPCPeeringConnection.PeerOwnerId``.
            peer_region: ``AWS::EC2::VPCPeeringConnection.PeerRegion``.
            peer_role_arn: ``AWS::EC2::VPCPeeringConnection.PeerRoleArn``.
            tags: ``AWS::EC2::VPCPeeringConnection.Tags``.

        Stability:
            experimental
        """
        props: CfnVPCPeeringConnectionProps = {"peerVpcId": peer_vpc_id, "vpcId": vpc_id}

        if peer_owner_id is not None:
            props["peerOwnerId"] = peer_owner_id

        if peer_region is not None:
            props["peerRegion"] = peer_region

        if peer_role_arn is not None:
            props["peerRoleArn"] = peer_role_arn

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnVPCPeeringConnection, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::VPCPeeringConnection.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="peerVpcId")
    def peer_vpc_id(self) -> str:
        """``AWS::EC2::VPCPeeringConnection.PeerVpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-peervpcid
        Stability:
            stable
        """
        return jsii.get(self, "peerVpcId")

    @peer_vpc_id.setter
    def peer_vpc_id(self, value: str):
        return jsii.set(self, "peerVpcId", value)

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """``AWS::EC2::VPCPeeringConnection.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-vpcid
        Stability:
            stable
        """
        return jsii.get(self, "vpcId")

    @vpc_id.setter
    def vpc_id(self, value: str):
        return jsii.set(self, "vpcId", value)

    @property
    @jsii.member(jsii_name="peerOwnerId")
    def peer_owner_id(self) -> typing.Optional[str]:
        """``AWS::EC2::VPCPeeringConnection.PeerOwnerId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-peerownerid
        Stability:
            stable
        """
        return jsii.get(self, "peerOwnerId")

    @peer_owner_id.setter
    def peer_owner_id(self, value: typing.Optional[str]):
        return jsii.set(self, "peerOwnerId", value)

    @property
    @jsii.member(jsii_name="peerRegion")
    def peer_region(self) -> typing.Optional[str]:
        """``AWS::EC2::VPCPeeringConnection.PeerRegion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-peerregion
        Stability:
            stable
        """
        return jsii.get(self, "peerRegion")

    @peer_region.setter
    def peer_region(self, value: typing.Optional[str]):
        return jsii.set(self, "peerRegion", value)

    @property
    @jsii.member(jsii_name="peerRoleArn")
    def peer_role_arn(self) -> typing.Optional[str]:
        """``AWS::EC2::VPCPeeringConnection.PeerRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-peerrolearn
        Stability:
            stable
        """
        return jsii.get(self, "peerRoleArn")

    @peer_role_arn.setter
    def peer_role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "peerRoleArn", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCPeeringConnectionProps(jsii.compat.TypedDict, total=False):
    peerOwnerId: str
    """``AWS::EC2::VPCPeeringConnection.PeerOwnerId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-peerownerid
    Stability:
        stable
    """
    peerRegion: str
    """``AWS::EC2::VPCPeeringConnection.PeerRegion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-peerregion
    Stability:
        stable
    """
    peerRoleArn: str
    """``AWS::EC2::VPCPeeringConnection.PeerRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-peerrolearn
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::VPCPeeringConnection.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCPeeringConnectionProps", jsii_struct_bases=[_CfnVPCPeeringConnectionProps])
class CfnVPCPeeringConnectionProps(_CfnVPCPeeringConnectionProps):
    """Properties for defining a ``AWS::EC2::VPCPeeringConnection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html
    Stability:
        stable
    """
    peerVpcId: str
    """``AWS::EC2::VPCPeeringConnection.PeerVpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-peervpcid
    Stability:
        stable
    """

    vpcId: str
    """``AWS::EC2::VPCPeeringConnection.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-vpcid
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCProps(jsii.compat.TypedDict, total=False):
    enableDnsHostnames: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::VPC.EnableDnsHostnames``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-EnableDnsHostnames
    Stability:
        stable
    """
    enableDnsSupport: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::VPC.EnableDnsSupport``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-EnableDnsSupport
    Stability:
        stable
    """
    instanceTenancy: str
    """``AWS::EC2::VPC.InstanceTenancy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-instancetenancy
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::VPC.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCProps", jsii_struct_bases=[_CfnVPCProps])
class CfnVPCProps(_CfnVPCProps):
    """Properties for defining a ``AWS::EC2::VPC``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html
    Stability:
        stable
    """
    cidrBlock: str
    """``AWS::EC2::VPC.CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-cidrblock
    Stability:
        stable
    """

class CfnVPNConnection(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPNConnection"):
    """A CloudFormation ``AWS::EC2::VPNConnection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPNConnection
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, customer_gateway_id: str, type: str, static_routes_only: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, transit_gateway_id: typing.Optional[str]=None, vpn_gateway_id: typing.Optional[str]=None, vpn_tunnel_options_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "VpnTunnelOptionsSpecificationProperty"]]]]]=None) -> None:
        """Create a new ``AWS::EC2::VPNConnection``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            customer_gateway_id: ``AWS::EC2::VPNConnection.CustomerGatewayId``.
            type: ``AWS::EC2::VPNConnection.Type``.
            static_routes_only: ``AWS::EC2::VPNConnection.StaticRoutesOnly``.
            tags: ``AWS::EC2::VPNConnection.Tags``.
            transit_gateway_id: ``AWS::EC2::VPNConnection.TransitGatewayId``.
            vpn_gateway_id: ``AWS::EC2::VPNConnection.VpnGatewayId``.
            vpn_tunnel_options_specifications: ``AWS::EC2::VPNConnection.VpnTunnelOptionsSpecifications``.

        Stability:
            experimental
        """
        props: CfnVPNConnectionProps = {"customerGatewayId": customer_gateway_id, "type": type}

        if static_routes_only is not None:
            props["staticRoutesOnly"] = static_routes_only

        if tags is not None:
            props["tags"] = tags

        if transit_gateway_id is not None:
            props["transitGatewayId"] = transit_gateway_id

        if vpn_gateway_id is not None:
            props["vpnGatewayId"] = vpn_gateway_id

        if vpn_tunnel_options_specifications is not None:
            props["vpnTunnelOptionsSpecifications"] = vpn_tunnel_options_specifications

        jsii.create(CfnVPNConnection, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::VPNConnection.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="customerGatewayId")
    def customer_gateway_id(self) -> str:
        """``AWS::EC2::VPNConnection.CustomerGatewayId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-customergatewayid
        Stability:
            stable
        """
        return jsii.get(self, "customerGatewayId")

    @customer_gateway_id.setter
    def customer_gateway_id(self, value: str):
        return jsii.set(self, "customerGatewayId", value)

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """``AWS::EC2::VPNConnection.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-type
        Stability:
            stable
        """
        return jsii.get(self, "type")

    @type.setter
    def type(self, value: str):
        return jsii.set(self, "type", value)

    @property
    @jsii.member(jsii_name="staticRoutesOnly")
    def static_routes_only(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::VPNConnection.StaticRoutesOnly``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-StaticRoutesOnly
        Stability:
            stable
        """
        return jsii.get(self, "staticRoutesOnly")

    @static_routes_only.setter
    def static_routes_only(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "staticRoutesOnly", value)

    @property
    @jsii.member(jsii_name="transitGatewayId")
    def transit_gateway_id(self) -> typing.Optional[str]:
        """``AWS::EC2::VPNConnection.TransitGatewayId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-transitgatewayid
        Stability:
            stable
        """
        return jsii.get(self, "transitGatewayId")

    @transit_gateway_id.setter
    def transit_gateway_id(self, value: typing.Optional[str]):
        return jsii.set(self, "transitGatewayId", value)

    @property
    @jsii.member(jsii_name="vpnGatewayId")
    def vpn_gateway_id(self) -> typing.Optional[str]:
        """``AWS::EC2::VPNConnection.VpnGatewayId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-vpngatewayid
        Stability:
            stable
        """
        return jsii.get(self, "vpnGatewayId")

    @vpn_gateway_id.setter
    def vpn_gateway_id(self, value: typing.Optional[str]):
        return jsii.set(self, "vpnGatewayId", value)

    @property
    @jsii.member(jsii_name="vpnTunnelOptionsSpecifications")
    def vpn_tunnel_options_specifications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "VpnTunnelOptionsSpecificationProperty"]]]]]:
        """``AWS::EC2::VPNConnection.VpnTunnelOptionsSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-vpntunneloptionsspecifications
        Stability:
            stable
        """
        return jsii.get(self, "vpnTunnelOptionsSpecifications")

    @vpn_tunnel_options_specifications.setter
    def vpn_tunnel_options_specifications(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "VpnTunnelOptionsSpecificationProperty"]]]]]):
        return jsii.set(self, "vpnTunnelOptionsSpecifications", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPNConnection.VpnTunnelOptionsSpecificationProperty", jsii_struct_bases=[])
    class VpnTunnelOptionsSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-vpnconnection-vpntunneloptionsspecification.html
        Stability:
            stable
        """
        preSharedKey: str
        """``CfnVPNConnection.VpnTunnelOptionsSpecificationProperty.PreSharedKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-vpnconnection-vpntunneloptionsspecification.html#cfn-ec2-vpnconnection-vpntunneloptionsspecification-presharedkey
        Stability:
            stable
        """

        tunnelInsideCidr: str
        """``CfnVPNConnection.VpnTunnelOptionsSpecificationProperty.TunnelInsideCidr``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-vpnconnection-vpntunneloptionsspecification.html#cfn-ec2-vpnconnection-vpntunneloptionsspecification-tunnelinsidecidr
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPNConnectionProps(jsii.compat.TypedDict, total=False):
    staticRoutesOnly: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::VPNConnection.StaticRoutesOnly``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-StaticRoutesOnly
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::VPNConnection.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-tags
    Stability:
        stable
    """
    transitGatewayId: str
    """``AWS::EC2::VPNConnection.TransitGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-transitgatewayid
    Stability:
        stable
    """
    vpnGatewayId: str
    """``AWS::EC2::VPNConnection.VpnGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-vpngatewayid
    Stability:
        stable
    """
    vpnTunnelOptionsSpecifications: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVPNConnection.VpnTunnelOptionsSpecificationProperty"]]]
    """``AWS::EC2::VPNConnection.VpnTunnelOptionsSpecifications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-vpntunneloptionsspecifications
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPNConnectionProps", jsii_struct_bases=[_CfnVPNConnectionProps])
class CfnVPNConnectionProps(_CfnVPNConnectionProps):
    """Properties for defining a ``AWS::EC2::VPNConnection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html
    Stability:
        stable
    """
    customerGatewayId: str
    """``AWS::EC2::VPNConnection.CustomerGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-customergatewayid
    Stability:
        stable
    """

    type: str
    """``AWS::EC2::VPNConnection.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-type
    Stability:
        stable
    """

class CfnVPNConnectionRoute(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPNConnectionRoute"):
    """A CloudFormation ``AWS::EC2::VPNConnectionRoute``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection-route.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPNConnectionRoute
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, destination_cidr_block: str, vpn_connection_id: str) -> None:
        """Create a new ``AWS::EC2::VPNConnectionRoute``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            destination_cidr_block: ``AWS::EC2::VPNConnectionRoute.DestinationCidrBlock``.
            vpn_connection_id: ``AWS::EC2::VPNConnectionRoute.VpnConnectionId``.

        Stability:
            experimental
        """
        props: CfnVPNConnectionRouteProps = {"destinationCidrBlock": destination_cidr_block, "vpnConnectionId": vpn_connection_id}

        jsii.create(CfnVPNConnectionRoute, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="destinationCidrBlock")
    def destination_cidr_block(self) -> str:
        """``AWS::EC2::VPNConnectionRoute.DestinationCidrBlock``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection-route.html#cfn-ec2-vpnconnectionroute-cidrblock
        Stability:
            stable
        """
        return jsii.get(self, "destinationCidrBlock")

    @destination_cidr_block.setter
    def destination_cidr_block(self, value: str):
        return jsii.set(self, "destinationCidrBlock", value)

    @property
    @jsii.member(jsii_name="vpnConnectionId")
    def vpn_connection_id(self) -> str:
        """``AWS::EC2::VPNConnectionRoute.VpnConnectionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection-route.html#cfn-ec2-vpnconnectionroute-connectionid
        Stability:
            stable
        """
        return jsii.get(self, "vpnConnectionId")

    @vpn_connection_id.setter
    def vpn_connection_id(self, value: str):
        return jsii.set(self, "vpnConnectionId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPNConnectionRouteProps", jsii_struct_bases=[])
class CfnVPNConnectionRouteProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::VPNConnectionRoute``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection-route.html
    Stability:
        stable
    """
    destinationCidrBlock: str
    """``AWS::EC2::VPNConnectionRoute.DestinationCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection-route.html#cfn-ec2-vpnconnectionroute-cidrblock
    Stability:
        stable
    """

    vpnConnectionId: str
    """``AWS::EC2::VPNConnectionRoute.VpnConnectionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection-route.html#cfn-ec2-vpnconnectionroute-connectionid
    Stability:
        stable
    """

class CfnVPNGateway(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPNGateway"):
    """A CloudFormation ``AWS::EC2::VPNGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPNGateway
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, type: str, amazon_side_asn: typing.Optional[jsii.Number]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::VPNGateway``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            type: ``AWS::EC2::VPNGateway.Type``.
            amazon_side_asn: ``AWS::EC2::VPNGateway.AmazonSideAsn``.
            tags: ``AWS::EC2::VPNGateway.Tags``.

        Stability:
            experimental
        """
        props: CfnVPNGatewayProps = {"type": type}

        if amazon_side_asn is not None:
            props["amazonSideAsn"] = amazon_side_asn

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnVPNGateway, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::VPNGateway.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html#cfn-ec2-vpngateway-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """``AWS::EC2::VPNGateway.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html#cfn-ec2-vpngateway-type
        Stability:
            stable
        """
        return jsii.get(self, "type")

    @type.setter
    def type(self, value: str):
        return jsii.set(self, "type", value)

    @property
    @jsii.member(jsii_name="amazonSideAsn")
    def amazon_side_asn(self) -> typing.Optional[jsii.Number]:
        """``AWS::EC2::VPNGateway.AmazonSideAsn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html#cfn-ec2-vpngateway-amazonsideasn
        Stability:
            stable
        """
        return jsii.get(self, "amazonSideAsn")

    @amazon_side_asn.setter
    def amazon_side_asn(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "amazonSideAsn", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPNGatewayProps(jsii.compat.TypedDict, total=False):
    amazonSideAsn: jsii.Number
    """``AWS::EC2::VPNGateway.AmazonSideAsn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html#cfn-ec2-vpngateway-amazonsideasn
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::VPNGateway.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html#cfn-ec2-vpngateway-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPNGatewayProps", jsii_struct_bases=[_CfnVPNGatewayProps])
class CfnVPNGatewayProps(_CfnVPNGatewayProps):
    """Properties for defining a ``AWS::EC2::VPNGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html
    Stability:
        stable
    """
    type: str
    """``AWS::EC2::VPNGateway.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html#cfn-ec2-vpngateway-type
    Stability:
        stable
    """

class CfnVPNGatewayRoutePropagation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPNGatewayRoutePropagation"):
    """A CloudFormation ``AWS::EC2::VPNGatewayRoutePropagation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gatewayrouteprop.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VPNGatewayRoutePropagation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, route_table_ids: typing.List[str], vpn_gateway_id: str) -> None:
        """Create a new ``AWS::EC2::VPNGatewayRoutePropagation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            route_table_ids: ``AWS::EC2::VPNGatewayRoutePropagation.RouteTableIds``.
            vpn_gateway_id: ``AWS::EC2::VPNGatewayRoutePropagation.VpnGatewayId``.

        Stability:
            experimental
        """
        props: CfnVPNGatewayRoutePropagationProps = {"routeTableIds": route_table_ids, "vpnGatewayId": vpn_gateway_id}

        jsii.create(CfnVPNGatewayRoutePropagation, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="routeTableIds")
    def route_table_ids(self) -> typing.List[str]:
        """``AWS::EC2::VPNGatewayRoutePropagation.RouteTableIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gatewayrouteprop.html#cfn-ec2-vpngatewayrouteprop-routetableids
        Stability:
            stable
        """
        return jsii.get(self, "routeTableIds")

    @route_table_ids.setter
    def route_table_ids(self, value: typing.List[str]):
        return jsii.set(self, "routeTableIds", value)

    @property
    @jsii.member(jsii_name="vpnGatewayId")
    def vpn_gateway_id(self) -> str:
        """``AWS::EC2::VPNGatewayRoutePropagation.VpnGatewayId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gatewayrouteprop.html#cfn-ec2-vpngatewayrouteprop-vpngatewayid
        Stability:
            stable
        """
        return jsii.get(self, "vpnGatewayId")

    @vpn_gateway_id.setter
    def vpn_gateway_id(self, value: str):
        return jsii.set(self, "vpnGatewayId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPNGatewayRoutePropagationProps", jsii_struct_bases=[])
class CfnVPNGatewayRoutePropagationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::VPNGatewayRoutePropagation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gatewayrouteprop.html
    Stability:
        stable
    """
    routeTableIds: typing.List[str]
    """``AWS::EC2::VPNGatewayRoutePropagation.RouteTableIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gatewayrouteprop.html#cfn-ec2-vpngatewayrouteprop-routetableids
    Stability:
        stable
    """

    vpnGatewayId: str
    """``AWS::EC2::VPNGatewayRoutePropagation.VpnGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gatewayrouteprop.html#cfn-ec2-vpngatewayrouteprop-vpngatewayid
    Stability:
        stable
    """

class CfnVolume(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVolume"):
    """A CloudFormation ``AWS::EC2::Volume``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::Volume
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, availability_zone: str, auto_enable_io: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, iops: typing.Optional[jsii.Number]=None, kms_key_id: typing.Optional[str]=None, size: typing.Optional[jsii.Number]=None, snapshot_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, volume_type: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::Volume``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            availability_zone: ``AWS::EC2::Volume.AvailabilityZone``.
            auto_enable_io: ``AWS::EC2::Volume.AutoEnableIO``.
            encrypted: ``AWS::EC2::Volume.Encrypted``.
            iops: ``AWS::EC2::Volume.Iops``.
            kms_key_id: ``AWS::EC2::Volume.KmsKeyId``.
            size: ``AWS::EC2::Volume.Size``.
            snapshot_id: ``AWS::EC2::Volume.SnapshotId``.
            tags: ``AWS::EC2::Volume.Tags``.
            volume_type: ``AWS::EC2::Volume.VolumeType``.

        Stability:
            experimental
        """
        props: CfnVolumeProps = {"availabilityZone": availability_zone}

        if auto_enable_io is not None:
            props["autoEnableIo"] = auto_enable_io

        if encrypted is not None:
            props["encrypted"] = encrypted

        if iops is not None:
            props["iops"] = iops

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

        if size is not None:
            props["size"] = size

        if snapshot_id is not None:
            props["snapshotId"] = snapshot_id

        if tags is not None:
            props["tags"] = tags

        if volume_type is not None:
            props["volumeType"] = volume_type

        jsii.create(CfnVolume, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::EC2::Volume.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> str:
        """``AWS::EC2::Volume.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-availabilityzone
        Stability:
            stable
        """
        return jsii.get(self, "availabilityZone")

    @availability_zone.setter
    def availability_zone(self, value: str):
        return jsii.set(self, "availabilityZone", value)

    @property
    @jsii.member(jsii_name="autoEnableIo")
    def auto_enable_io(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::Volume.AutoEnableIO``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-autoenableio
        Stability:
            stable
        """
        return jsii.get(self, "autoEnableIo")

    @auto_enable_io.setter
    def auto_enable_io(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "autoEnableIo", value)

    @property
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EC2::Volume.Encrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-encrypted
        Stability:
            stable
        """
        return jsii.get(self, "encrypted")

    @encrypted.setter
    def encrypted(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "encrypted", value)

    @property
    @jsii.member(jsii_name="iops")
    def iops(self) -> typing.Optional[jsii.Number]:
        """``AWS::EC2::Volume.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-iops
        Stability:
            stable
        """
        return jsii.get(self, "iops")

    @iops.setter
    def iops(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "iops", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Volume.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-kmskeyid
        Stability:
            stable
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="size")
    def size(self) -> typing.Optional[jsii.Number]:
        """``AWS::EC2::Volume.Size``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-size
        Stability:
            stable
        """
        return jsii.get(self, "size")

    @size.setter
    def size(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "size", value)

    @property
    @jsii.member(jsii_name="snapshotId")
    def snapshot_id(self) -> typing.Optional[str]:
        """``AWS::EC2::Volume.SnapshotId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-snapshotid
        Stability:
            stable
        """
        return jsii.get(self, "snapshotId")

    @snapshot_id.setter
    def snapshot_id(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotId", value)

    @property
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> typing.Optional[str]:
        """``AWS::EC2::Volume.VolumeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-volumetype
        Stability:
            stable
        """
        return jsii.get(self, "volumeType")

    @volume_type.setter
    def volume_type(self, value: typing.Optional[str]):
        return jsii.set(self, "volumeType", value)


class CfnVolumeAttachment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVolumeAttachment"):
    """A CloudFormation ``AWS::EC2::VolumeAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html
    Stability:
        stable
    cloudformationResource:
        AWS::EC2::VolumeAttachment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, device: str, instance_id: str, volume_id: str) -> None:
        """Create a new ``AWS::EC2::VolumeAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            device: ``AWS::EC2::VolumeAttachment.Device``.
            instance_id: ``AWS::EC2::VolumeAttachment.InstanceId``.
            volume_id: ``AWS::EC2::VolumeAttachment.VolumeId``.

        Stability:
            experimental
        """
        props: CfnVolumeAttachmentProps = {"device": device, "instanceId": instance_id, "volumeId": volume_id}

        jsii.create(CfnVolumeAttachment, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="device")
    def device(self) -> str:
        """``AWS::EC2::VolumeAttachment.Device``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html#cfn-ec2-ebs-volumeattachment-device
        Stability:
            stable
        """
        return jsii.get(self, "device")

    @device.setter
    def device(self, value: str):
        return jsii.set(self, "device", value)

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> str:
        """``AWS::EC2::VolumeAttachment.InstanceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html#cfn-ec2-ebs-volumeattachment-instanceid
        Stability:
            stable
        """
        return jsii.get(self, "instanceId")

    @instance_id.setter
    def instance_id(self, value: str):
        return jsii.set(self, "instanceId", value)

    @property
    @jsii.member(jsii_name="volumeId")
    def volume_id(self) -> str:
        """``AWS::EC2::VolumeAttachment.VolumeId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html#cfn-ec2-ebs-volumeattachment-volumeid
        Stability:
            stable
        """
        return jsii.get(self, "volumeId")

    @volume_id.setter
    def volume_id(self, value: str):
        return jsii.set(self, "volumeId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVolumeAttachmentProps", jsii_struct_bases=[])
class CfnVolumeAttachmentProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::VolumeAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html
    Stability:
        stable
    """
    device: str
    """``AWS::EC2::VolumeAttachment.Device``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html#cfn-ec2-ebs-volumeattachment-device
    Stability:
        stable
    """

    instanceId: str
    """``AWS::EC2::VolumeAttachment.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html#cfn-ec2-ebs-volumeattachment-instanceid
    Stability:
        stable
    """

    volumeId: str
    """``AWS::EC2::VolumeAttachment.VolumeId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html#cfn-ec2-ebs-volumeattachment-volumeid
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVolumeProps(jsii.compat.TypedDict, total=False):
    autoEnableIo: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::Volume.AutoEnableIO``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-autoenableio
    Stability:
        stable
    """
    encrypted: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EC2::Volume.Encrypted``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-encrypted
    Stability:
        stable
    """
    iops: jsii.Number
    """``AWS::EC2::Volume.Iops``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-iops
    Stability:
        stable
    """
    kmsKeyId: str
    """``AWS::EC2::Volume.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-kmskeyid
    Stability:
        stable
    """
    size: jsii.Number
    """``AWS::EC2::Volume.Size``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-size
    Stability:
        stable
    """
    snapshotId: str
    """``AWS::EC2::Volume.SnapshotId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-snapshotid
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::EC2::Volume.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-tags
    Stability:
        stable
    """
    volumeType: str
    """``AWS::EC2::Volume.VolumeType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-volumetype
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVolumeProps", jsii_struct_bases=[_CfnVolumeProps])
class CfnVolumeProps(_CfnVolumeProps):
    """Properties for defining a ``AWS::EC2::Volume``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html
    Stability:
        stable
    """
    availabilityZone: str
    """``AWS::EC2::Volume.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-availabilityzone
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _ConnectionRule(jsii.compat.TypedDict, total=False):
    description: str
    """Description of this connection.

    It is applied to both the ingress rule
    and the egress rule.

    Default:
        No description

    Stability:
        experimental
    """
    protocol: str
    """The IP protocol name (tcp, udp, icmp) or number (see Protocol Numbers). Use -1 to specify all protocols. If you specify -1, or a protocol number other than tcp, udp, icmp, or 58 (ICMPv6), traffic on all ports is allowed, regardless of any ports you specify. For tcp, udp, and icmp, you must specify a port range. For protocol 58 (ICMPv6), you can optionally specify a port range; if you don't, traffic for all types and codes is allowed.

    Default:
        tcp

    Stability:
        experimental
    """
    toPort: jsii.Number
    """End of port range for the TCP and UDP protocols, or an ICMP code.

    If you specify icmp for the IpProtocol property, you can specify -1 as a
    wildcard (i.e., any ICMP code).

    Default:
        If toPort is not specified, it will be the same as fromPort.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.ConnectionRule", jsii_struct_bases=[_ConnectionRule])
class ConnectionRule(_ConnectionRule):
    """
    Stability:
        experimental
    """
    fromPort: jsii.Number
    """Start of port range for the TCP and UDP protocols, or an ICMP type number.

    If you specify icmp for the IpProtocol property, you can specify
    -1 as a wildcard (i.e., any ICMP type number).

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.ConnectionsProps", jsii_struct_bases=[])
class ConnectionsProps(jsii.compat.TypedDict, total=False):
    """Properties to intialize a new Connections object.

    Stability:
        experimental
    """
    defaultPort: "Port"
    """Default port range for initiating connections to and from this object.

    Default:
        - No default port

    Stability:
        experimental
    """

    peer: "IPeer"
    """Class that represents the rule by which others can connect to this connectable.

    This object is required, but will be derived from securityGroup if that is passed.

    Default:
        Derived from securityGroup if set.

    Stability:
        experimental
    """

    securityGroups: typing.List["ISecurityGroup"]
    """What securityGroup(s) this object is managing connections for.

    Default:
        No security groups

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ec2.DefaultInstanceTenancy")
class DefaultInstanceTenancy(enum.Enum):
    """The default tenancy of instances launched into the VPC.

    Stability:
        experimental
    """
    DEFAULT = "DEFAULT"
    """Instances can be launched with any tenancy.

    Stability:
        experimental
    """
    DEDICATED = "DEDICATED"
    """Any instance launched into the VPC automatically has dedicated tenancy, unless you launch it with the default tenancy.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _GatewayVpcEndpointOptions(jsii.compat.TypedDict, total=False):
    subnets: typing.List["SubnetSelection"]
    """Where to add endpoint routing.

    Default:
        private subnets

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.GatewayVpcEndpointOptions", jsii_struct_bases=[_GatewayVpcEndpointOptions])
class GatewayVpcEndpointOptions(_GatewayVpcEndpointOptions):
    """Options to add a gateway endpoint to a VPC.

    Stability:
        experimental
    """
    service: "IGatewayVpcEndpointService"
    """The service to use for this gateway VPC endpoint.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.GatewayVpcEndpointProps", jsii_struct_bases=[GatewayVpcEndpointOptions])
class GatewayVpcEndpointProps(GatewayVpcEndpointOptions, jsii.compat.TypedDict):
    """Construction properties for a GatewayVpcEndpoint.

    Stability:
        experimental
    """
    vpc: "IVpc"
    """The VPC network in which the gateway endpoint will be used.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.GenericLinuxImageProps", jsii_struct_bases=[])
class GenericLinuxImageProps(jsii.compat.TypedDict, total=False):
    """Configuration options for GenericLinuxImage.

    Stability:
        experimental
    """
    userData: "UserData"
    """Initial user data.

    Default:
        - Empty UserData for Windows machines

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IConnectable")
class IConnectable(jsii.compat.Protocol):
    """The goal of this module is to make possible to write statements like this:.

    Example::

         database.connections.allowFrom(fleet);
         fleet.connections.allowTo(database);
         rdgw.connections.allowFromCidrIp('0.3.1.5/86');
         rgdw.connections.allowTrafficTo(fleet, new AllPorts());

    The insight here is that some connecting peers have information on what ports should
    be involved in the connection, and some don't.
    An object that has a Connections object

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IConnectableProxy

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> "Connections":
        """
        Stability:
            experimental
        """
        ...


class _IConnectableProxy():
    """The goal of this module is to make possible to write statements like this:.

    Example::

         database.connections.allowFrom(fleet);
         fleet.connections.allowTo(database);
         rdgw.connections.allowFromCidrIp('0.3.1.5/86');
         rgdw.connections.allowTrafficTo(fleet, new AllPorts());

    The insight here is that some connecting peers have information on what ports should
    be involved in the connection, and some don't.
    An object that has a Connections object

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IConnectable"
    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> "Connections":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "connections")


@jsii.implements(IConnectable)
class Connections(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.Connections"):
    """Manage the allowed network connections for constructs with Security Groups.

    Security Groups can be thought of as a firewall for network-connected
    devices. This class makes it easy to allow network connections to and
    from security groups, and between security groups individually. When
    establishing connectivity between security groups, it will automatically
    add rules in both security groups

    This object can manage one or more security groups.

    Stability:
        experimental
    """
    def __init__(self, *, default_port: typing.Optional["Port"]=None, peer: typing.Optional["IPeer"]=None, security_groups: typing.Optional[typing.List["ISecurityGroup"]]=None) -> None:
        """
        Arguments:
            props: -
            default_port: Default port range for initiating connections to and from this object. Default: - No default port
            peer: Class that represents the rule by which others can connect to this connectable. This object is required, but will be derived from securityGroup if that is passed. Default: Derived from securityGroup if set.
            security_groups: What securityGroup(s) this object is managing connections for. Default: No security groups

        Stability:
            experimental
        """
        props: ConnectionsProps = {}

        if default_port is not None:
            props["defaultPort"] = default_port

        if peer is not None:
            props["peer"] = peer

        if security_groups is not None:
            props["securityGroups"] = security_groups

        jsii.create(Connections, self, [props])

    @jsii.member(jsii_name="addSecurityGroup")
    def add_security_group(self, *security_groups: "ISecurityGroup") -> None:
        """Add a security group to the list of security groups managed by this object.

        Arguments:
            security_groups: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addSecurityGroup", [*security_groups])

    @jsii.member(jsii_name="allowDefaultPortFrom")
    def allow_default_port_from(self, other: "IConnectable", description: typing.Optional[str]=None) -> None:
        """Allow connections from the peer on our default port.

        Even if the peer has a default port, we will always use our default port.

        Arguments:
            other: -
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowDefaultPortFrom", [other, description])

    @jsii.member(jsii_name="allowDefaultPortFromAnyIpv4")
    def allow_default_port_from_any_ipv4(self, description: typing.Optional[str]=None) -> None:
        """Allow default connections from all IPv4 ranges.

        Arguments:
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowDefaultPortFromAnyIpv4", [description])

    @jsii.member(jsii_name="allowDefaultPortInternally")
    def allow_default_port_internally(self, description: typing.Optional[str]=None) -> None:
        """Allow hosts inside the security group to connect to each other.

        Arguments:
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowDefaultPortInternally", [description])

    @jsii.member(jsii_name="allowDefaultPortTo")
    def allow_default_port_to(self, other: "IConnectable", description: typing.Optional[str]=None) -> None:
        """Allow connections from the peer on our default port.

        Even if the peer has a default port, we will always use our default port.

        Arguments:
            other: -
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowDefaultPortTo", [other, description])

    @jsii.member(jsii_name="allowFrom")
    def allow_from(self, other: "IConnectable", port_range: "Port", description: typing.Optional[str]=None) -> None:
        """Allow connections from the peer on the given port.

        Arguments:
            other: -
            port_range: -
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowFrom", [other, port_range, description])

    @jsii.member(jsii_name="allowFromAnyIPv4")
    def allow_from_any_i_pv4(self, port_range: "Port", description: typing.Optional[str]=None) -> None:
        """Allow from any IPv4 ranges.

        Arguments:
            port_range: -
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowFromAnyIPv4", [port_range, description])

    @jsii.member(jsii_name="allowInternally")
    def allow_internally(self, port_range: "Port", description: typing.Optional[str]=None) -> None:
        """Allow hosts inside the security group to connect to each other on the given port.

        Arguments:
            port_range: -
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowInternally", [port_range, description])

    @jsii.member(jsii_name="allowTo")
    def allow_to(self, other: "IConnectable", port_range: "Port", description: typing.Optional[str]=None) -> None:
        """Allow connections to the peer on the given port.

        Arguments:
            other: -
            port_range: -
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowTo", [other, port_range, description])

    @jsii.member(jsii_name="allowToAnyIPv4")
    def allow_to_any_i_pv4(self, port_range: "Port", description: typing.Optional[str]=None) -> None:
        """Allow to all IPv4 ranges.

        Arguments:
            port_range: -
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowToAnyIPv4", [port_range, description])

    @jsii.member(jsii_name="allowToDefaultPort")
    def allow_to_default_port(self, other: "IConnectable", description: typing.Optional[str]=None) -> None:
        """Allow connections to the security group on their default port.

        Arguments:
            other: -
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowToDefaultPort", [other, description])

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> "Connections":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List["ISecurityGroup"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroups")

    @property
    @jsii.member(jsii_name="defaultPort")
    def default_port(self) -> typing.Optional["Port"]:
        """The default port configured for this connection peer, if available.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultPort")


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IGatewayVpcEndpointService")
class IGatewayVpcEndpointService(jsii.compat.Protocol):
    """A service for a gateway VPC endpoint.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IGatewayVpcEndpointServiceProxy

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """The name of the service.

        Stability:
            experimental
        """
        ...


class _IGatewayVpcEndpointServiceProxy():
    """A service for a gateway VPC endpoint.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IGatewayVpcEndpointService"
    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """The name of the service.

        Stability:
            experimental
        """
        return jsii.get(self, "name")


@jsii.implements(IGatewayVpcEndpointService)
class GatewayVpcEndpointAwsService(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.GatewayVpcEndpointAwsService"):
    """An AWS service for a gateway VPC endpoint.

    Stability:
        experimental
    """
    def __init__(self, name: str, prefix: typing.Optional[str]=None) -> None:
        """
        Arguments:
            name: -
            prefix: -

        Stability:
            experimental
        """
        jsii.create(GatewayVpcEndpointAwsService, self, [name, prefix])

    @classproperty
    @jsii.member(jsii_name="DYNAMODB")
    def DYNAMODB(cls) -> "GatewayVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "DYNAMODB")

    @classproperty
    @jsii.member(jsii_name="S3")
    def S3(cls) -> "GatewayVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "S3")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """The name of the service.

        Stability:
            experimental
        """
        return jsii.get(self, "name")


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IInterfaceVpcEndpointService")
class IInterfaceVpcEndpointService(jsii.compat.Protocol):
    """A service for an interface VPC endpoint.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IInterfaceVpcEndpointServiceProxy

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """The name of the service.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        """The port of the service.

        Stability:
            experimental
        """
        ...


class _IInterfaceVpcEndpointServiceProxy():
    """A service for an interface VPC endpoint.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IInterfaceVpcEndpointService"
    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """The name of the service.

        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        """The port of the service.

        Stability:
            experimental
        """
        return jsii.get(self, "port")


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IMachineImage")
class IMachineImage(jsii.compat.Protocol):
    """Interface for classes that can select an appropriate machine image to use.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IMachineImageProxy

    @jsii.member(jsii_name="getImage")
    def get_image(self, scope: aws_cdk.core.Construct) -> "MachineImageConfig":
        """Return the image to use in the given context.

        Arguments:
            scope: -

        Stability:
            experimental
        """
        ...


class _IMachineImageProxy():
    """Interface for classes that can select an appropriate machine image to use.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IMachineImage"
    @jsii.member(jsii_name="getImage")
    def get_image(self, scope: aws_cdk.core.Construct) -> "MachineImageConfig":
        """Return the image to use in the given context.

        Arguments:
            scope: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getImage", [scope])


@jsii.implements(IMachineImage)
class AmazonLinuxImage(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.AmazonLinuxImage"):
    """Selects the latest version of Amazon Linux.

    The AMI ID is selected using the values published to the SSM parameter store.

    Stability:
        experimental
    """
    def __init__(self, *, edition: typing.Optional["AmazonLinuxEdition"]=None, generation: typing.Optional["AmazonLinuxGeneration"]=None, storage: typing.Optional["AmazonLinuxStorage"]=None, user_data: typing.Optional["UserData"]=None, virtualization: typing.Optional["AmazonLinuxVirt"]=None) -> None:
        """
        Arguments:
            props: -
            edition: What edition of Amazon Linux to use. Default: Standard
            generation: What generation of Amazon Linux to use. Default: AmazonLinux
            storage: What storage backed image to use. Default: GeneralPurpose
            user_data: Initial user data. Default: - Empty UserData for Linux machines
            virtualization: Virtualization type. Default: HVM

        Stability:
            experimental
        """
        props: AmazonLinuxImageProps = {}

        if edition is not None:
            props["edition"] = edition

        if generation is not None:
            props["generation"] = generation

        if storage is not None:
            props["storage"] = storage

        if user_data is not None:
            props["userData"] = user_data

        if virtualization is not None:
            props["virtualization"] = virtualization

        jsii.create(AmazonLinuxImage, self, [props])

    @jsii.member(jsii_name="getImage")
    def get_image(self, scope: aws_cdk.core.Construct) -> "MachineImageConfig":
        """Return the image to use in the given context.

        Arguments:
            scope: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getImage", [scope])


@jsii.implements(IMachineImage)
class GenericLinuxImage(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.GenericLinuxImage"):
    """Construct a Linux machine image from an AMI map.

    Linux images IDs are not published to SSM parameter store yet, so you'll have to
    manually specify an AMI map.

    Stability:
        experimental
    """
    def __init__(self, ami_map: typing.Mapping[str,str], *, user_data: typing.Optional["UserData"]=None) -> None:
        """
        Arguments:
            ami_map: -
            props: -
            user_data: Initial user data. Default: - Empty UserData for Windows machines

        Stability:
            experimental
        """
        props: GenericLinuxImageProps = {}

        if user_data is not None:
            props["userData"] = user_data

        jsii.create(GenericLinuxImage, self, [ami_map, props])

    @jsii.member(jsii_name="getImage")
    def get_image(self, scope: aws_cdk.core.Construct) -> "MachineImageConfig":
        """Return the image to use in the given context.

        Arguments:
            scope: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getImage", [scope])


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IPeer")
class IPeer(IConnectable, jsii.compat.Protocol):
    """Interface for classes that provide the peer-specification parts of a security group rule.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IPeerProxy

    @property
    @jsii.member(jsii_name="canInlineRule")
    def can_inline_rule(self) -> bool:
        """Whether the rule can be inlined into a SecurityGroup or not.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> str:
        """A unique identifier for this connection peer.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="toEgressRuleConfig")
    def to_egress_rule_config(self) -> typing.Any:
        """Produce the egress rule JSON for the given connection.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="toIngressRuleConfig")
    def to_ingress_rule_config(self) -> typing.Any:
        """Produce the ingress rule JSON for the given connection.

        Stability:
            experimental
        """
        ...


class _IPeerProxy(jsii.proxy_for(IConnectable)):
    """Interface for classes that provide the peer-specification parts of a security group rule.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IPeer"
    @property
    @jsii.member(jsii_name="canInlineRule")
    def can_inline_rule(self) -> bool:
        """Whether the rule can be inlined into a SecurityGroup or not.

        Stability:
            experimental
        """
        return jsii.get(self, "canInlineRule")

    @property
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> str:
        """A unique identifier for this connection peer.

        Stability:
            experimental
        """
        return jsii.get(self, "uniqueId")

    @jsii.member(jsii_name="toEgressRuleConfig")
    def to_egress_rule_config(self) -> typing.Any:
        """Produce the egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toEgressRuleConfig", [])

    @jsii.member(jsii_name="toIngressRuleConfig")
    def to_ingress_rule_config(self) -> typing.Any:
        """Produce the ingress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toIngressRuleConfig", [])


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IRouteTable")
class IRouteTable(jsii.compat.Protocol):
    """An absract route table.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IRouteTableProxy

    @property
    @jsii.member(jsii_name="routeTableId")
    def route_table_id(self) -> str:
        """Route table ID.

        Stability:
            experimental
        """
        ...


class _IRouteTableProxy():
    """An absract route table.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IRouteTable"
    @property
    @jsii.member(jsii_name="routeTableId")
    def route_table_id(self) -> str:
        """Route table ID.

        Stability:
            experimental
        """
        return jsii.get(self, "routeTableId")


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.ISecurityGroup")
class ISecurityGroup(aws_cdk.core.IResource, IPeer, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ISecurityGroupProxy

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """ID for the current security group.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @jsii.member(jsii_name="addEgressRule")
    def add_egress_rule(self, peer: "IPeer", connection: "Port", description: typing.Optional[str]=None, remote_rule: typing.Optional[bool]=None) -> None:
        """Add an egress rule for the current security group.

        ``remoteRule`` controls where the Rule object is created if the peer is also a
        securityGroup and they are in different stack. If false (default) the
        rule object is created under the current SecurityGroup object. If true and the
        peer is also a SecurityGroup, the rule object is created under the remote
        SecurityGroup object.

        Arguments:
            peer: -
            connection: -
            description: -
            remote_rule: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addIngressRule")
    def add_ingress_rule(self, peer: "IPeer", connection: "Port", description: typing.Optional[str]=None, remote_rule: typing.Optional[bool]=None) -> None:
        """Add an ingress rule for the current security group.

        ``remoteRule`` controls where the Rule object is created if the peer is also a
        securityGroup and they are in different stack. If false (default) the
        rule object is created under the current SecurityGroup object. If true and the
        peer is also a SecurityGroup, the rule object is created under the remote
        SecurityGroup object.

        Arguments:
            peer: -
            connection: -
            description: -
            remote_rule: -

        Stability:
            experimental
        """
        ...


class _ISecurityGroupProxy(jsii.proxy_for(aws_cdk.core.IResource), jsii.proxy_for(IPeer)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.ISecurityGroup"
    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """ID for the current security group.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "securityGroupId")

    @jsii.member(jsii_name="addEgressRule")
    def add_egress_rule(self, peer: "IPeer", connection: "Port", description: typing.Optional[str]=None, remote_rule: typing.Optional[bool]=None) -> None:
        """Add an egress rule for the current security group.

        ``remoteRule`` controls where the Rule object is created if the peer is also a
        securityGroup and they are in different stack. If false (default) the
        rule object is created under the current SecurityGroup object. If true and the
        peer is also a SecurityGroup, the rule object is created under the remote
        SecurityGroup object.

        Arguments:
            peer: -
            connection: -
            description: -
            remote_rule: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addEgressRule", [peer, connection, description, remote_rule])

    @jsii.member(jsii_name="addIngressRule")
    def add_ingress_rule(self, peer: "IPeer", connection: "Port", description: typing.Optional[str]=None, remote_rule: typing.Optional[bool]=None) -> None:
        """Add an ingress rule for the current security group.

        ``remoteRule`` controls where the Rule object is created if the peer is also a
        securityGroup and they are in different stack. If false (default) the
        rule object is created under the current SecurityGroup object. If true and the
        peer is also a SecurityGroup, the rule object is created under the remote
        SecurityGroup object.

        Arguments:
            peer: -
            connection: -
            description: -
            remote_rule: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addIngressRule", [peer, connection, description, remote_rule])


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.ISubnet")
class ISubnet(aws_cdk.core.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ISubnetProxy

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> str:
        """The Availability Zone the subnet is located in.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="internetConnectivityEstablished")
    def internet_connectivity_established(self) -> aws_cdk.core.IDependable:
        """Dependable that can be depended upon to force internet connectivity established on the VPC.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="routeTable")
    def route_table(self) -> "IRouteTable":
        """The route table for this subnet.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        """The subnetId for this particular subnet.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _ISubnetProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.ISubnet"
    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> str:
        """The Availability Zone the subnet is located in.

        Stability:
            experimental
        """
        return jsii.get(self, "availabilityZone")

    @property
    @jsii.member(jsii_name="internetConnectivityEstablished")
    def internet_connectivity_established(self) -> aws_cdk.core.IDependable:
        """Dependable that can be depended upon to force internet connectivity established on the VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "internetConnectivityEstablished")

    @property
    @jsii.member(jsii_name="routeTable")
    def route_table(self) -> "IRouteTable":
        """The route table for this subnet.

        Stability:
            experimental
        """
        return jsii.get(self, "routeTable")

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        """The subnetId for this particular subnet.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "subnetId")


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IPrivateSubnet")
class IPrivateSubnet(ISubnet, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IPrivateSubnetProxy

    pass

class _IPrivateSubnetProxy(jsii.proxy_for(ISubnet)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IPrivateSubnet"
    pass

@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IPublicSubnet")
class IPublicSubnet(ISubnet, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IPublicSubnetProxy

    pass

class _IPublicSubnetProxy(jsii.proxy_for(ISubnet)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IPublicSubnet"
    pass

@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IVpc")
class IVpc(aws_cdk.core.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IVpcProxy

    @property
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[str]:
        """AZs for this VPC.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="internetConnectivityEstablished")
    def internet_connectivity_established(self) -> aws_cdk.core.IDependable:
        """Dependable that can be depended upon to force internet connectivity established on the VPC.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="isolatedSubnets")
    def isolated_subnets(self) -> typing.List["ISubnet"]:
        """List of isolated subnets in this VPC.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="privateSubnets")
    def private_subnets(self) -> typing.List["ISubnet"]:
        """List of private subnets in this VPC.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="publicSubnets")
    def public_subnets(self) -> typing.List["ISubnet"]:
        """List of public subnets in this VPC.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """Identifier for this VPC.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="vpnGatewayId")
    def vpn_gateway_id(self) -> typing.Optional[str]:
        """Identifier for the VPN gateway.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addInterfaceEndpoint")
    def add_interface_endpoint(self, id: str, *, service: "IInterfaceVpcEndpointService", private_dns_enabled: typing.Optional[bool]=None, subnets: typing.Optional["SubnetSelection"]=None) -> "InterfaceVpcEndpoint":
        """Adds a new interface endpoint to this VPC.

        Arguments:
            id: -
            options: -
            service: The service to use for this interface VPC endpoint.
            private_dns_enabled: Whether to associate a private hosted zone with the specified VPC. This allows you to make requests to the service using its default DNS hostname. Default: true
            subnets: The subnets in which to create an endpoint network interface. At most one per availability zone. Default: private subnets

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addVpnConnection")
    def add_vpn_connection(self, id: str, *, ip: str, asn: typing.Optional[jsii.Number]=None, static_routes: typing.Optional[typing.List[str]]=None, tunnel_options: typing.Optional[typing.List["VpnTunnelOption"]]=None) -> "VpnConnection":
        """Adds a new VPN connection to this VPC.

        Arguments:
            id: -
            options: -
            ip: The ip address of the customer gateway.
            asn: The ASN of the customer gateway. Default: 65000
            static_routes: The static routes to be routed from the VPN gateway to the customer gateway. Default: Dynamic routing (BGP)
            tunnel_options: The tunnel options for the VPN connection. At most two elements (one per tunnel). Duplicates not allowed. Default: Amazon generated tunnel options

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="selectSubnets")
    def select_subnets(self, *, one_per_az: typing.Optional[bool]=None, subnet_name: typing.Optional[str]=None, subnet_type: typing.Optional["SubnetType"]=None) -> "SelectedSubnets":
        """Return information on the subnets appropriate for the given selection strategy.

        Requires that at least one subnet is matched, throws a descriptive
        error message otherwise.

        Arguments:
            selection: -
            one_per_az: If true, return at most one subnet per AZ.
            subnet_name: Place the instances in the subnets with the given name. (This is the name supplied in subnetConfiguration). At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: name
            subnet_type: Place the instances in the subnets of the given type. At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: SubnetType.Private

        Stability:
            experimental
        """
        ...


class _IVpcProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IVpc"
    @property
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[str]:
        """AZs for this VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "availabilityZones")

    @property
    @jsii.member(jsii_name="internetConnectivityEstablished")
    def internet_connectivity_established(self) -> aws_cdk.core.IDependable:
        """Dependable that can be depended upon to force internet connectivity established on the VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "internetConnectivityEstablished")

    @property
    @jsii.member(jsii_name="isolatedSubnets")
    def isolated_subnets(self) -> typing.List["ISubnet"]:
        """List of isolated subnets in this VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "isolatedSubnets")

    @property
    @jsii.member(jsii_name="privateSubnets")
    def private_subnets(self) -> typing.List["ISubnet"]:
        """List of private subnets in this VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "privateSubnets")

    @property
    @jsii.member(jsii_name="publicSubnets")
    def public_subnets(self) -> typing.List["ISubnet"]:
        """List of public subnets in this VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "publicSubnets")

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """Identifier for this VPC.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcId")

    @property
    @jsii.member(jsii_name="vpnGatewayId")
    def vpn_gateway_id(self) -> typing.Optional[str]:
        """Identifier for the VPN gateway.

        Stability:
            experimental
        """
        return jsii.get(self, "vpnGatewayId")

    @jsii.member(jsii_name="addInterfaceEndpoint")
    def add_interface_endpoint(self, id: str, *, service: "IInterfaceVpcEndpointService", private_dns_enabled: typing.Optional[bool]=None, subnets: typing.Optional["SubnetSelection"]=None) -> "InterfaceVpcEndpoint":
        """Adds a new interface endpoint to this VPC.

        Arguments:
            id: -
            options: -
            service: The service to use for this interface VPC endpoint.
            private_dns_enabled: Whether to associate a private hosted zone with the specified VPC. This allows you to make requests to the service using its default DNS hostname. Default: true
            subnets: The subnets in which to create an endpoint network interface. At most one per availability zone. Default: private subnets

        Stability:
            experimental
        """
        options: InterfaceVpcEndpointOptions = {"service": service}

        if private_dns_enabled is not None:
            options["privateDnsEnabled"] = private_dns_enabled

        if subnets is not None:
            options["subnets"] = subnets

        return jsii.invoke(self, "addInterfaceEndpoint", [id, options])

    @jsii.member(jsii_name="addVpnConnection")
    def add_vpn_connection(self, id: str, *, ip: str, asn: typing.Optional[jsii.Number]=None, static_routes: typing.Optional[typing.List[str]]=None, tunnel_options: typing.Optional[typing.List["VpnTunnelOption"]]=None) -> "VpnConnection":
        """Adds a new VPN connection to this VPC.

        Arguments:
            id: -
            options: -
            ip: The ip address of the customer gateway.
            asn: The ASN of the customer gateway. Default: 65000
            static_routes: The static routes to be routed from the VPN gateway to the customer gateway. Default: Dynamic routing (BGP)
            tunnel_options: The tunnel options for the VPN connection. At most two elements (one per tunnel). Duplicates not allowed. Default: Amazon generated tunnel options

        Stability:
            experimental
        """
        options: VpnConnectionOptions = {"ip": ip}

        if asn is not None:
            options["asn"] = asn

        if static_routes is not None:
            options["staticRoutes"] = static_routes

        if tunnel_options is not None:
            options["tunnelOptions"] = tunnel_options

        return jsii.invoke(self, "addVpnConnection", [id, options])

    @jsii.member(jsii_name="selectSubnets")
    def select_subnets(self, *, one_per_az: typing.Optional[bool]=None, subnet_name: typing.Optional[str]=None, subnet_type: typing.Optional["SubnetType"]=None) -> "SelectedSubnets":
        """Return information on the subnets appropriate for the given selection strategy.

        Requires that at least one subnet is matched, throws a descriptive
        error message otherwise.

        Arguments:
            selection: -
            one_per_az: If true, return at most one subnet per AZ.
            subnet_name: Place the instances in the subnets with the given name. (This is the name supplied in subnetConfiguration). At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: name
            subnet_type: Place the instances in the subnets of the given type. At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: SubnetType.Private

        Stability:
            experimental
        """
        selection: SubnetSelection = {}

        if one_per_az is not None:
            selection["onePerAz"] = one_per_az

        if subnet_name is not None:
            selection["subnetName"] = subnet_name

        if subnet_type is not None:
            selection["subnetType"] = subnet_type

        return jsii.invoke(self, "selectSubnets", [selection])


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IVpcEndpoint")
class IVpcEndpoint(aws_cdk.core.IResource, jsii.compat.Protocol):
    """A VPC endpoint.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IVpcEndpointProxy

    @property
    @jsii.member(jsii_name="vpcEndpointId")
    def vpc_endpoint_id(self) -> str:
        """The VPC endpoint identifier.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IVpcEndpointProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """A VPC endpoint.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IVpcEndpoint"
    @property
    @jsii.member(jsii_name="vpcEndpointId")
    def vpc_endpoint_id(self) -> str:
        """The VPC endpoint identifier.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcEndpointId")


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IGatewayVpcEndpoint")
class IGatewayVpcEndpoint(IVpcEndpoint, jsii.compat.Protocol):
    """A gateway VPC endpoint.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IGatewayVpcEndpointProxy

    pass

class _IGatewayVpcEndpointProxy(jsii.proxy_for(IVpcEndpoint)):
    """A gateway VPC endpoint.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IGatewayVpcEndpoint"
    pass

@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IInterfaceVpcEndpoint")
class IInterfaceVpcEndpoint(IVpcEndpoint, IConnectable, jsii.compat.Protocol):
    """An interface VPC endpoint.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IInterfaceVpcEndpointProxy

    pass

class _IInterfaceVpcEndpointProxy(jsii.proxy_for(IVpcEndpoint), jsii.proxy_for(IConnectable)):
    """An interface VPC endpoint.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IInterfaceVpcEndpoint"
    pass

@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IVpnConnection")
class IVpnConnection(aws_cdk.core.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IVpnConnectionProxy

    @property
    @jsii.member(jsii_name="customerGatewayAsn")
    def customer_gateway_asn(self) -> jsii.Number:
        """The ASN of the customer gateway.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="customerGatewayId")
    def customer_gateway_id(self) -> str:
        """The id of the customer gateway.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="customerGatewayIp")
    def customer_gateway_ip(self) -> str:
        """The ip address of the customer gateway.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="vpnId")
    def vpn_id(self) -> str:
        """The id of the VPN connection.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this VPNConnection.

        Arguments:
            metric_name: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricTunnelDataIn")
    def metric_tunnel_data_in(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The bytes received through the VPN tunnel.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricTunnelDataOut")
    def metric_tunnel_data_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The bytes sent through the VPN tunnel.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricTunnelState")
    def metric_tunnel_state(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The state of the tunnel. 0 indicates DOWN and 1 indicates UP.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...


class _IVpnConnectionProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IVpnConnection"
    @property
    @jsii.member(jsii_name="customerGatewayAsn")
    def customer_gateway_asn(self) -> jsii.Number:
        """The ASN of the customer gateway.

        Stability:
            experimental
        """
        return jsii.get(self, "customerGatewayAsn")

    @property
    @jsii.member(jsii_name="customerGatewayId")
    def customer_gateway_id(self) -> str:
        """The id of the customer gateway.

        Stability:
            experimental
        """
        return jsii.get(self, "customerGatewayId")

    @property
    @jsii.member(jsii_name="customerGatewayIp")
    def customer_gateway_ip(self) -> str:
        """The ip address of the customer gateway.

        Stability:
            experimental
        """
        return jsii.get(self, "customerGatewayIp")

    @property
    @jsii.member(jsii_name="vpnId")
    def vpn_id(self) -> str:
        """The id of the VPN connection.

        Stability:
            experimental
        """
        return jsii.get(self, "vpnId")

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this VPNConnection.

        Arguments:
            metric_name: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricTunnelDataIn")
    def metric_tunnel_data_in(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The bytes received through the VPN tunnel.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricTunnelDataIn", [props])

    @jsii.member(jsii_name="metricTunnelDataOut")
    def metric_tunnel_data_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The bytes sent through the VPN tunnel.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricTunnelDataOut", [props])

    @jsii.member(jsii_name="metricTunnelState")
    def metric_tunnel_state(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The state of the tunnel. 0 indicates DOWN and 1 indicates UP.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricTunnelState", [props])


@jsii.enum(jsii_type="@aws-cdk/aws-ec2.InstanceClass")
class InstanceClass(enum.Enum):
    """What class and generation of instance to use.

    We have both symbolic and concrete enums for every type.

    The first are for people that want to specify by purpose,
    the second one are for people who already know exactly what
    'R4' means.

    Stability:
        experimental
    """
    STANDARD3 = "STANDARD3"
    """Standard instances, 3rd generation.

    Stability:
        experimental
    """
    STANDARD4 = "STANDARD4"
    """Standard instances, 4th generation.

    Stability:
        experimental
    """
    STANDARD5 = "STANDARD5"
    """Standard instances, 5th generation.

    Stability:
        experimental
    """
    MEMORY3 = "MEMORY3"
    """Memory optimized instances, 3rd generation.

    Stability:
        experimental
    """
    MEMORY4 = "MEMORY4"
    """Memory optimized instances, 3rd generation.

    Stability:
        experimental
    """
    COMPUTE3 = "COMPUTE3"
    """Compute optimized instances, 3rd generation.

    Stability:
        experimental
    """
    COMPUTE4 = "COMPUTE4"
    """Compute optimized instances, 4th generation.

    Stability:
        experimental
    """
    COMPUTE5 = "COMPUTE5"
    """Compute optimized instances, 5th generation.

    Stability:
        experimental
    """
    STORAGE2 = "STORAGE2"
    """Storage-optimized instances, 2nd generation.

    Stability:
        experimental
    """
    STORAGE_COMPUTE_1 = "STORAGE_COMPUTE_1"
    """Storage/compute balanced instances, 1st generation.

    Stability:
        experimental
    """
    IO3 = "IO3"
    """I/O-optimized instances, 3rd generation.

    Stability:
        experimental
    """
    BURSTABLE2 = "BURSTABLE2"
    """Burstable instances, 2nd generation.

    Stability:
        experimental
    """
    BURSTABLE3 = "BURSTABLE3"
    """Burstable instances, 3rd generation.

    Stability:
        experimental
    """
    MEMORY_INTENSIVE_1 = "MEMORY_INTENSIVE_1"
    """Memory-intensive instances, 1st generation.

    Stability:
        experimental
    """
    MEMORY_INTENSIVE_1_EXTENDED = "MEMORY_INTENSIVE_1_EXTENDED"
    """Memory-intensive instances, extended, 1st generation.

    Stability:
        experimental
    """
    FPGA1 = "FPGA1"
    """Instances with customizable hardware acceleration, 1st generation.

    Stability:
        experimental
    """
    GRAPHICS3 = "GRAPHICS3"
    """Graphics-optimized instances, 3rd generation.

    Stability:
        experimental
    """
    PARALLEL2 = "PARALLEL2"
    """Parallel-processing optimized instances, 2nd generation.

    Stability:
        experimental
    """
    PARALLEL3 = "PARALLEL3"
    """Parallel-processing optimized instances, 3nd generation.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ec2.InstanceSize")
class InstanceSize(enum.Enum):
    """What size of instance to use.

    Stability:
        experimental
    """
    NANO = "NANO"
    """
    Stability:
        experimental
    """
    MICRO = "MICRO"
    """
    Stability:
        experimental
    """
    SMALL = "SMALL"
    """
    Stability:
        experimental
    """
    MEDIUM = "MEDIUM"
    """
    Stability:
        experimental
    """
    LARGE = "LARGE"
    """
    Stability:
        experimental
    """
    XLARGE = "XLARGE"
    """
    Stability:
        experimental
    """
    XLARGE2 = "XLARGE2"
    """
    Stability:
        experimental
    """
    XLARGE4 = "XLARGE4"
    """
    Stability:
        experimental
    """
    XLARGE8 = "XLARGE8"
    """
    Stability:
        experimental
    """
    XLARGE9 = "XLARGE9"
    """
    Stability:
        experimental
    """
    XLARGE10 = "XLARGE10"
    """
    Stability:
        experimental
    """
    XLARGE12 = "XLARGE12"
    """
    Stability:
        experimental
    """
    XLARGE16 = "XLARGE16"
    """
    Stability:
        experimental
    """
    XLARGE18 = "XLARGE18"
    """
    Stability:
        experimental
    """
    XLARGE24 = "XLARGE24"
    """
    Stability:
        experimental
    """
    XLARGE32 = "XLARGE32"
    """
    Stability:
        experimental
    """

class InstanceType(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.InstanceType"):
    """Instance type for EC2 instances.

    This class takes a literal string, good if you already
    know the identifier of the type you want.

    Stability:
        experimental
    """
    def __init__(self, instance_type_identifier: str) -> None:
        """
        Arguments:
            instance_type_identifier: -

        Stability:
            experimental
        """
        jsii.create(InstanceType, self, [instance_type_identifier])

    @jsii.member(jsii_name="of")
    @classmethod
    def of(cls, instance_class: "InstanceClass", instance_size: "InstanceSize") -> "InstanceType":
        """Instance type for EC2 instances.

        This class takes a combination of a class and size.

        Be aware that not all combinations of class and size are available, and not all
        classes are available in all regions.

        Arguments:
            instance_class: -
            instance_size: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "of", [instance_class, instance_size])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Return the instance type as a dotted string.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.InterfaceVpcEndpointAttributes", jsii_struct_bases=[])
class InterfaceVpcEndpointAttributes(jsii.compat.TypedDict):
    """Construction properties for an ImportedInterfaceVpcEndpoint.

    Stability:
        experimental
    """
    port: jsii.Number
    """The port of the service of the interface VPC endpoint.

    Stability:
        experimental
    """

    securityGroupId: str
    """The identifier of the security group associated with the interface VPC endpoint.

    Stability:
        experimental
    """

    vpcEndpointId: str
    """The interface VPC endpoint identifier.

    Stability:
        experimental
    """

@jsii.implements(IInterfaceVpcEndpointService)
class InterfaceVpcEndpointAwsService(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.InterfaceVpcEndpointAwsService"):
    """An AWS service for an interface VPC endpoint.

    Stability:
        experimental
    """
    def __init__(self, name: str, prefix: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            name: -
            prefix: -
            port: -

        Stability:
            experimental
        """
        jsii.create(InterfaceVpcEndpointAwsService, self, [name, prefix, port])

    @classproperty
    @jsii.member(jsii_name="APIGATEWAY")
    def APIGATEWAY(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "APIGATEWAY")

    @classproperty
    @jsii.member(jsii_name="CLOUDFORMATION")
    def CLOUDFORMATION(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CLOUDFORMATION")

    @classproperty
    @jsii.member(jsii_name="CLOUDTRAIL")
    def CLOUDTRAIL(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CLOUDTRAIL")

    @classproperty
    @jsii.member(jsii_name="CLOUDWATCH")
    def CLOUDWATCH(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CLOUDWATCH")

    @classproperty
    @jsii.member(jsii_name="CLOUDWATCH_EVENTS")
    def CLOUDWATCH_EVENTS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CLOUDWATCH_EVENTS")

    @classproperty
    @jsii.member(jsii_name="CLOUDWATCH_LOGS")
    def CLOUDWATCH_LOGS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CLOUDWATCH_LOGS")

    @classproperty
    @jsii.member(jsii_name="CODEBUILD")
    def CODEBUILD(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CODEBUILD")

    @classproperty
    @jsii.member(jsii_name="CODEBUILD_FIPS")
    def CODEBUILD_FIPS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CODEBUILD_FIPS")

    @classproperty
    @jsii.member(jsii_name="CODECOMMIT")
    def CODECOMMIT(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CODECOMMIT")

    @classproperty
    @jsii.member(jsii_name="CODECOMMIT_FIPS")
    def CODECOMMIT_FIPS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CODECOMMIT_FIPS")

    @classproperty
    @jsii.member(jsii_name="CODECOMMIT_GIT")
    def CODECOMMIT_GIT(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CODECOMMIT_GIT")

    @classproperty
    @jsii.member(jsii_name="CODECOMMIT_GIT_FIPS")
    def CODECOMMIT_GIT_FIPS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CODECOMMIT_GIT_FIPS")

    @classproperty
    @jsii.member(jsii_name="CODEPIPELINE")
    def CODEPIPELINE(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CODEPIPELINE")

    @classproperty
    @jsii.member(jsii_name="CONFIG")
    def CONFIG(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CONFIG")

    @classproperty
    @jsii.member(jsii_name="EC2")
    def E_C2(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "EC2")

    @classproperty
    @jsii.member(jsii_name="EC2_MESSAGES")
    def E_C2_MESSAGES(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "EC2_MESSAGES")

    @classproperty
    @jsii.member(jsii_name="ECR")
    def ECR(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ECR")

    @classproperty
    @jsii.member(jsii_name="ECR_DOCKER")
    def ECR_DOCKER(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ECR_DOCKER")

    @classproperty
    @jsii.member(jsii_name="ECS")
    def ECS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ECS")

    @classproperty
    @jsii.member(jsii_name="ECS_AGENT")
    def ECS_AGENT(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ECS_AGENT")

    @classproperty
    @jsii.member(jsii_name="ECS_TELEMETRY")
    def ECS_TELEMETRY(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ECS_TELEMETRY")

    @classproperty
    @jsii.member(jsii_name="ELASTIC_INFERENCE_RUNTIME")
    def ELASTIC_INFERENCE_RUNTIME(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ELASTIC_INFERENCE_RUNTIME")

    @classproperty
    @jsii.member(jsii_name="ELASTIC_LOAD_BALANCING")
    def ELASTIC_LOAD_BALANCING(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ELASTIC_LOAD_BALANCING")

    @classproperty
    @jsii.member(jsii_name="KINESIS_STREAMS")
    def KINESIS_STREAMS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "KINESIS_STREAMS")

    @classproperty
    @jsii.member(jsii_name="KMS")
    def KMS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "KMS")

    @classproperty
    @jsii.member(jsii_name="SAGEMAKER_API")
    def SAGEMAKER_API(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SAGEMAKER_API")

    @classproperty
    @jsii.member(jsii_name="SAGEMAKER_NOTEBOOK")
    def SAGEMAKER_NOTEBOOK(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SAGEMAKER_NOTEBOOK")

    @classproperty
    @jsii.member(jsii_name="SAGEMAKER_RUNTIME")
    def SAGEMAKER_RUNTIME(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SAGEMAKER_RUNTIME")

    @classproperty
    @jsii.member(jsii_name="SAGEMAKER_RUNTIME_FIPS")
    def SAGEMAKER_RUNTIME_FIPS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SAGEMAKER_RUNTIME_FIPS")

    @classproperty
    @jsii.member(jsii_name="SECRETS_MANAGER")
    def SECRETS_MANAGER(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SECRETS_MANAGER")

    @classproperty
    @jsii.member(jsii_name="SERVICE_CATALOG")
    def SERVICE_CATALOG(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SERVICE_CATALOG")

    @classproperty
    @jsii.member(jsii_name="SNS")
    def SNS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SNS")

    @classproperty
    @jsii.member(jsii_name="SQS")
    def SQS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SQS")

    @classproperty
    @jsii.member(jsii_name="SSM")
    def SSM(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SSM")

    @classproperty
    @jsii.member(jsii_name="SSM_MESSAGES")
    def SSM_MESSAGES(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SSM_MESSAGES")

    @classproperty
    @jsii.member(jsii_name="STS")
    def STS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "STS")

    @classproperty
    @jsii.member(jsii_name="TRANSFER")
    def TRANSFER(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "TRANSFER")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """The name of the service.

        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        """The port of the service.

        Stability:
            experimental
        """
        return jsii.get(self, "port")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _InterfaceVpcEndpointOptions(jsii.compat.TypedDict, total=False):
    privateDnsEnabled: bool
    """Whether to associate a private hosted zone with the specified VPC.

    This
    allows you to make requests to the service using its default DNS hostname.

    Default:
        true

    Stability:
        experimental
    """
    subnets: "SubnetSelection"
    """The subnets in which to create an endpoint network interface.

    At most one
    per availability zone.

    Default:
        private subnets

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.InterfaceVpcEndpointOptions", jsii_struct_bases=[_InterfaceVpcEndpointOptions])
class InterfaceVpcEndpointOptions(_InterfaceVpcEndpointOptions):
    """Options to add an interface endpoint to a VPC.

    Stability:
        experimental
    """
    service: "IInterfaceVpcEndpointService"
    """The service to use for this interface VPC endpoint.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.InterfaceVpcEndpointProps", jsii_struct_bases=[InterfaceVpcEndpointOptions])
class InterfaceVpcEndpointProps(InterfaceVpcEndpointOptions, jsii.compat.TypedDict):
    """Construction properties for an InterfaceVpcEndpoint.

    Stability:
        experimental
    """
    vpc: "IVpc"
    """The VPC network in which the interface endpoint will be used.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.LinuxUserDataOptions", jsii_struct_bases=[])
class LinuxUserDataOptions(jsii.compat.TypedDict, total=False):
    """Options when constructing UserData for Linux.

    Stability:
        experimental
    """
    shebang: str
    """Shebang for the UserData script.

    Default:
        "#!/bin/bash"

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _MachineImageConfig(jsii.compat.TypedDict, total=False):
    userData: "UserData"
    """Initial UserData for this image.

    Default:
        - Default UserData appropriate for the osType is created

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.MachineImageConfig", jsii_struct_bases=[_MachineImageConfig])
class MachineImageConfig(_MachineImageConfig):
    """Configuration for a machine image.

    Stability:
        experimental
    """
    imageId: str
    """The AMI ID of the image to use.

    Stability:
        experimental
    """

    osType: "OperatingSystemType"
    """Operating system type for this image.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ec2.OperatingSystemType")
class OperatingSystemType(enum.Enum):
    """The OS type of a particular image.

    Stability:
        experimental
    """
    LINUX = "LINUX"
    """
    Stability:
        experimental
    """
    WINDOWS = "WINDOWS"
    """
    Stability:
        experimental
    """

class Peer(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.Peer"):
    """Factories for static connection peer.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        """
        Stability:
            experimental
        """
        jsii.create(Peer, self, [])

    @jsii.member(jsii_name="anyIpv4")
    @classmethod
    def any_ipv4(cls) -> "IPeer":
        """Any IPv4 address.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "anyIpv4", [])

    @jsii.member(jsii_name="anyIpv6")
    @classmethod
    def any_ipv6(cls) -> "IPeer":
        """Any IPv6 address.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "anyIpv6", [])

    @jsii.member(jsii_name="ipv4")
    @classmethod
    def ipv4(cls, cidr_ip: str) -> "IPeer":
        """Create an IPv4 peer from a CIDR.

        Arguments:
            cidr_ip: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "ipv4", [cidr_ip])

    @jsii.member(jsii_name="ipv6")
    @classmethod
    def ipv6(cls, cidr_ip: str) -> "IPeer":
        """Create an IPv6 peer from a CIDR.

        Arguments:
            cidr_ip: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "ipv6", [cidr_ip])

    @jsii.member(jsii_name="prefixList")
    @classmethod
    def prefix_list(cls, prefix_list_id: str) -> "IPeer":
        """A prefix list.

        Arguments:
            prefix_list_id: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "prefixList", [prefix_list_id])


class Port(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.Port"):
    """Interface for classes that provide the connection-specification parts of a security group rule.

    Stability:
        experimental
    """
    def __init__(self, *, protocol: "Protocol", string_representation: str, from_port: typing.Optional[jsii.Number]=None, to_port: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            props: -
            protocol: The protocol for the range.
            string_representation: String representation for this object.
            from_port: The starting port for the range. Default: - Not included in the rule
            to_port: The ending port for the range. Default: - Not included in the rule

        Stability:
            experimental
        """
        props: PortProps = {"protocol": protocol, "stringRepresentation": string_representation}

        if from_port is not None:
            props["fromPort"] = from_port

        if to_port is not None:
            props["toPort"] = to_port

        jsii.create(Port, self, [props])

    @jsii.member(jsii_name="allIcmp")
    @classmethod
    def all_icmp(cls) -> "Port":
        """All ICMP traffic.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "allIcmp", [])

    @jsii.member(jsii_name="allTcp")
    @classmethod
    def all_tcp(cls) -> "Port":
        """Any TCP traffic.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "allTcp", [])

    @jsii.member(jsii_name="allTraffic")
    @classmethod
    def all_traffic(cls) -> "Port":
        """All traffic.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "allTraffic", [])

    @jsii.member(jsii_name="allUdp")
    @classmethod
    def all_udp(cls) -> "Port":
        """Any UDP traffic.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "allUdp", [])

    @jsii.member(jsii_name="icmpPing")
    @classmethod
    def icmp_ping(cls) -> "Port":
        """ICMP ping (echo) traffic.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "icmpPing", [])

    @jsii.member(jsii_name="icmpType")
    @classmethod
    def icmp_type(cls, type: jsii.Number) -> "Port":
        """All codes for a single ICMP type.

        Arguments:
            type: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "icmpType", [type])

    @jsii.member(jsii_name="icmpTypeAndCode")
    @classmethod
    def icmp_type_and_code(cls, type: jsii.Number, code: jsii.Number) -> "Port":
        """A specific combination of ICMP type and code.

        Arguments:
            type: -
            code: -

        See:
            https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml
        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "icmpTypeAndCode", [type, code])

    @jsii.member(jsii_name="tcp")
    @classmethod
    def tcp(cls, port: jsii.Number) -> "Port":
        """A single TCP port.

        Arguments:
            port: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "tcp", [port])

    @jsii.member(jsii_name="tcpRange")
    @classmethod
    def tcp_range(cls, start_port: jsii.Number, end_port: jsii.Number) -> "Port":
        """A TCP port range.

        Arguments:
            start_port: -
            end_port: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "tcpRange", [start_port, end_port])

    @jsii.member(jsii_name="udp")
    @classmethod
    def udp(cls, port: jsii.Number) -> "Port":
        """A single UDP port.

        Arguments:
            port: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "udp", [port])

    @jsii.member(jsii_name="udpRange")
    @classmethod
    def udp_range(cls, start_port: jsii.Number, end_port: jsii.Number) -> "Port":
        """A UDP port range.

        Arguments:
            start_port: -
            end_port: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "udpRange", [start_port, end_port])

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="canInlineRule")
    def can_inline_rule(self) -> bool:
        """Whether the rule containing this port range can be inlined into a securitygroup or not.

        Stability:
            experimental
        """
        return jsii.get(self, "canInlineRule")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _PortProps(jsii.compat.TypedDict, total=False):
    fromPort: jsii.Number
    """The starting port for the range.

    Default:
        - Not included in the rule

    Stability:
        experimental
    """
    toPort: jsii.Number
    """The ending port for the range.

    Default:
        - Not included in the rule

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.PortProps", jsii_struct_bases=[_PortProps])
class PortProps(_PortProps):
    """Properties to create a port range.

    Stability:
        experimental
    """
    protocol: "Protocol"
    """The protocol for the range.

    Stability:
        experimental
    """

    stringRepresentation: str
    """String representation for this object.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ec2.Protocol")
class Protocol(enum.Enum):
    """Protocol for use in Connection Rules.

    Stability:
        experimental
    """
    ALL = "ALL"
    """
    Stability:
        experimental
    """
    TCP = "TCP"
    """
    Stability:
        experimental
    """
    UDP = "UDP"
    """
    Stability:
        experimental
    """
    ICMP = "ICMP"
    """
    Stability:
        experimental
    """
    ICMPV6 = "ICMPV6"
    """
    Stability:
        experimental
    """

@jsii.implements(ISecurityGroup)
class SecurityGroup(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.SecurityGroup"):
    """Creates an Amazon EC2 security group within a VPC.

    This class has an additional optimization over imported security groups that it can also create
    inline ingress and egress rule (which saves on the total number of resources inside
    the template).

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, vpc: "IVpc", allow_all_outbound: typing.Optional[bool]=None, description: typing.Optional[str]=None, security_group_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            vpc: The VPC in which to create the security group.
            allow_all_outbound: Whether to allow all outbound traffic by default. If this is set to true, there will only be a single egress rule which allows all outbound traffic. If this is set to false, no outbound traffic will be allowed by default and all egress traffic must be explicitly authorized. Default: true
            description: A description of the security group. Default: The default name will be the construct's CDK path.
            security_group_name: The name of the security group. For valid values, see the GroupName parameter of the CreateSecurityGroup action in the Amazon EC2 API Reference. It is not recommended to use an explicit group name. Default: If you don't specify a GroupName, AWS CloudFormation generates a unique physical ID and uses that ID for the group name.

        Stability:
            experimental
        """
        props: SecurityGroupProps = {"vpc": vpc}

        if allow_all_outbound is not None:
            props["allowAllOutbound"] = allow_all_outbound

        if description is not None:
            props["description"] = description

        if security_group_name is not None:
            props["securityGroupName"] = security_group_name

        jsii.create(SecurityGroup, self, [scope, id, props])

    @jsii.member(jsii_name="fromSecurityGroupId")
    @classmethod
    def from_security_group_id(cls, scope: aws_cdk.core.Construct, id: str, security_group_id: str) -> "ISecurityGroup":
        """Import an existing security group into this app.

        Arguments:
            scope: -
            id: -
            security_group_id: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromSecurityGroupId", [scope, id, security_group_id])

    @jsii.member(jsii_name="isSecurityGroup")
    @classmethod
    def is_security_group(cls, x: typing.Any) -> bool:
        """Return whether the indicated object is a security group.

        Arguments:
            x: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "isSecurityGroup", [x])

    @jsii.member(jsii_name="addEgressRule")
    def add_egress_rule(self, peer: "IPeer", connection: "Port", description: typing.Optional[str]=None, remote_rule: typing.Optional[bool]=None) -> None:
        """Add an egress rule for the current security group.

        ``remoteRule`` controls where the Rule object is created if the peer is also a
        securityGroup and they are in different stack. If false (default) the
        rule object is created under the current SecurityGroup object. If true and the
        peer is also a SecurityGroup, the rule object is created under the remote
        SecurityGroup object.

        Arguments:
            peer: -
            connection: -
            description: -
            remote_rule: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addEgressRule", [peer, connection, description, remote_rule])

    @jsii.member(jsii_name="addIngressRule")
    def add_ingress_rule(self, peer: "IPeer", connection: "Port", description: typing.Optional[str]=None, remote_rule: typing.Optional[bool]=None) -> None:
        """Add an ingress rule for the current security group.

        ``remoteRule`` controls where the Rule object is created if the peer is also a
        securityGroup and they are in different stack. If false (default) the
        rule object is created under the current SecurityGroup object. If true and the
        peer is also a SecurityGroup, the rule object is created under the remote
        SecurityGroup object.

        Arguments:
            peer: -
            connection: -
            description: -
            remote_rule: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addIngressRule", [peer, connection, description, remote_rule])

    @jsii.member(jsii_name="toEgressRuleConfig")
    def to_egress_rule_config(self) -> typing.Any:
        """Produce the egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toEgressRuleConfig", [])

    @jsii.member(jsii_name="toIngressRuleConfig")
    def to_ingress_rule_config(self) -> typing.Any:
        """Produce the ingress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toIngressRuleConfig", [])

    @property
    @jsii.member(jsii_name="canInlineRule")
    def can_inline_rule(self) -> bool:
        """Whether the rule can be inlined into a SecurityGroup or not.

        Stability:
            experimental
        """
        return jsii.get(self, "canInlineRule")

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> "Connections":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """The ID of the security group.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "securityGroupId")

    @property
    @jsii.member(jsii_name="securityGroupName")
    def security_group_name(self) -> str:
        """An attribute that represents the security group name.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "securityGroupName")

    @property
    @jsii.member(jsii_name="securityGroupVpcId")
    def security_group_vpc_id(self) -> str:
        """The VPC ID this security group is part of.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "securityGroupVpcId")

    @property
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> str:
        """A unique identifier for this connection peer.

        Stability:
            experimental
        """
        return jsii.get(self, "uniqueId")

    @property
    @jsii.member(jsii_name="defaultPort")
    def default_port(self) -> typing.Optional["Port"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "defaultPort")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _SecurityGroupProps(jsii.compat.TypedDict, total=False):
    allowAllOutbound: bool
    """Whether to allow all outbound traffic by default.

    If this is set to true, there will only be a single egress rule which allows all
    outbound traffic. If this is set to false, no outbound traffic will be allowed by
    default and all egress traffic must be explicitly authorized.

    Default:
        true

    Stability:
        experimental
    """
    description: str
    """A description of the security group.

    Default:
        The default name will be the construct's CDK path.

    Stability:
        experimental
    """
    securityGroupName: str
    """The name of the security group.

    For valid values, see the GroupName
    parameter of the CreateSecurityGroup action in the Amazon EC2 API
    Reference.

    It is not recommended to use an explicit group name.

    Default:
        If you don't specify a GroupName, AWS CloudFormation generates a
        unique physical ID and uses that ID for the group name.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.SecurityGroupProps", jsii_struct_bases=[_SecurityGroupProps])
class SecurityGroupProps(_SecurityGroupProps):
    """
    Stability:
        experimental
    """
    vpc: "IVpc"
    """The VPC in which to create the security group.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.SelectedSubnets", jsii_struct_bases=[])
class SelectedSubnets(jsii.compat.TypedDict):
    """Result of selecting a subset of subnets from a VPC.

    Stability:
        experimental
    """
    availabilityZones: typing.List[str]
    """The respective AZs of each subnet.

    Stability:
        experimental
    """

    hasPublic: bool
    """Whether any of the given subnets are from the VPC's public subnets.

    Stability:
        experimental
    """

    internetConnectivityEstablished: aws_cdk.core.IDependable
    """Dependency representing internet connectivity for these subnets.

    Stability:
        experimental
    """

    subnetIds: typing.List[str]
    """The subnet IDs.

    Stability:
        experimental
    """

    subnets: typing.List["ISubnet"]
    """Selected subnet objects.

    Stability:
        experimental
    """

@jsii.implements(ISubnet)
class Subnet(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.Subnet"):
    """Represents a new VPC subnet resource.

    Stability:
        experimental
    resource:
        AWS::EC2::Subnet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, availability_zone: str, cidr_block: str, vpc_id: str, map_public_ip_on_launch: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            availability_zone: The availability zone for the subnet.
            cidr_block: The CIDR notation for this subnet.
            vpc_id: The VPC which this subnet is part of.
            map_public_ip_on_launch: Controls if a public IP is associated to an instance at launch. Default: true in Subnet.Public, false in Subnet.Private or Subnet.Isolated.

        Stability:
            experimental
        """
        props: SubnetProps = {"availabilityZone": availability_zone, "cidrBlock": cidr_block, "vpcId": vpc_id}

        if map_public_ip_on_launch is not None:
            props["mapPublicIpOnLaunch"] = map_public_ip_on_launch

        jsii.create(Subnet, self, [scope, id, props])

    @jsii.member(jsii_name="fromSubnetAttributes")
    @classmethod
    def from_subnet_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, availability_zone: str, subnet_id: str) -> "ISubnet":
        """
        Arguments:
            scope: -
            id: -
            attrs: -
            availability_zone: The Availability Zone the subnet is located in.
            subnet_id: The subnetId for this particular subnet.

        Stability:
            experimental
        """
        attrs: SubnetAttributes = {"availabilityZone": availability_zone, "subnetId": subnet_id}

        return jsii.sinvoke(cls, "fromSubnetAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="isVpcSubnet")
    @classmethod
    def is_vpc_subnet(cls, x: typing.Any) -> bool:
        """
        Arguments:
            x: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "isVpcSubnet", [x])

    @jsii.member(jsii_name="addDefaultInternetRoute")
    def add_default_internet_route(self, gateway_id: str, gateway_attachment: aws_cdk.core.IDependable) -> None:
        """Create a default route that points to a passed IGW, with a dependency on the IGW's attachment to the VPC.

        Arguments:
            gateway_id: the logical ID (ref) of the gateway attached to your VPC.
            gateway_attachment: the gateway attachment construct to be added as a dependency.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addDefaultInternetRoute", [gateway_id, gateway_attachment])

    @jsii.member(jsii_name="addDefaultNatRoute")
    def add_default_nat_route(self, nat_gateway_id: str) -> None:
        """Adds an entry to this subnets route table that points to the passed NATGatwayId.

        Arguments:
            nat_gateway_id: The ID of the NAT gateway.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addDefaultNatRoute", [nat_gateway_id])

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> str:
        """The Availability Zone the subnet is located in.

        Stability:
            experimental
        """
        return jsii.get(self, "availabilityZone")

    @property
    @jsii.member(jsii_name="dependencyElements")
    def dependency_elements(self) -> typing.List[aws_cdk.core.IDependable]:
        """Parts of this VPC subnet.

        Stability:
            experimental
        """
        return jsii.get(self, "dependencyElements")

    @property
    @jsii.member(jsii_name="internetConnectivityEstablished")
    def internet_connectivity_established(self) -> aws_cdk.core.IDependable:
        """Dependable that can be depended upon to force internet connectivity established on the VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "internetConnectivityEstablished")

    @property
    @jsii.member(jsii_name="routeTable")
    def route_table(self) -> "IRouteTable":
        """The routeTableId attached to this subnet.

        Stability:
            experimental
        """
        return jsii.get(self, "routeTable")

    @property
    @jsii.member(jsii_name="subnetAvailabilityZone")
    def subnet_availability_zone(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "subnetAvailabilityZone")

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        """The subnetId for this particular subnet.

        Stability:
            experimental
        """
        return jsii.get(self, "subnetId")

    @property
    @jsii.member(jsii_name="subnetIpv6CidrBlocks")
    def subnet_ipv6_cidr_blocks(self) -> typing.List[str]:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "subnetIpv6CidrBlocks")

    @property
    @jsii.member(jsii_name="subnetNetworkAclAssociationId")
    def subnet_network_acl_association_id(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "subnetNetworkAclAssociationId")

    @property
    @jsii.member(jsii_name="subnetVpcId")
    def subnet_vpc_id(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "subnetVpcId")


@jsii.implements(IPrivateSubnet)
class PrivateSubnet(Subnet, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.PrivateSubnet"):
    """Represents a private VPC subnet resource.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, availability_zone: str, cidr_block: str, vpc_id: str, map_public_ip_on_launch: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            availability_zone: The availability zone for the subnet.
            cidr_block: The CIDR notation for this subnet.
            vpc_id: The VPC which this subnet is part of.
            map_public_ip_on_launch: Controls if a public IP is associated to an instance at launch. Default: true in Subnet.Public, false in Subnet.Private or Subnet.Isolated.

        Stability:
            experimental
        """
        props: PrivateSubnetProps = {"availabilityZone": availability_zone, "cidrBlock": cidr_block, "vpcId": vpc_id}

        if map_public_ip_on_launch is not None:
            props["mapPublicIpOnLaunch"] = map_public_ip_on_launch

        jsii.create(PrivateSubnet, self, [scope, id, props])

    @jsii.member(jsii_name="fromPrivateSubnetAttributes")
    @classmethod
    def from_private_subnet_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, availability_zone: str, subnet_id: str) -> "IPrivateSubnet":
        """
        Arguments:
            scope: -
            id: -
            attrs: -
            availability_zone: The Availability Zone the subnet is located in.
            subnet_id: The subnetId for this particular subnet.

        Stability:
            experimental
        """
        attrs: PrivateSubnetAttributes = {"availabilityZone": availability_zone, "subnetId": subnet_id}

        return jsii.sinvoke(cls, "fromPrivateSubnetAttributes", [scope, id, attrs])


@jsii.implements(IPublicSubnet)
class PublicSubnet(Subnet, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.PublicSubnet"):
    """Represents a public VPC subnet resource.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, availability_zone: str, cidr_block: str, vpc_id: str, map_public_ip_on_launch: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            availability_zone: The availability zone for the subnet.
            cidr_block: The CIDR notation for this subnet.
            vpc_id: The VPC which this subnet is part of.
            map_public_ip_on_launch: Controls if a public IP is associated to an instance at launch. Default: true in Subnet.Public, false in Subnet.Private or Subnet.Isolated.

        Stability:
            experimental
        """
        props: PublicSubnetProps = {"availabilityZone": availability_zone, "cidrBlock": cidr_block, "vpcId": vpc_id}

        if map_public_ip_on_launch is not None:
            props["mapPublicIpOnLaunch"] = map_public_ip_on_launch

        jsii.create(PublicSubnet, self, [scope, id, props])

    @jsii.member(jsii_name="fromPublicSubnetAttributes")
    @classmethod
    def from_public_subnet_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, availability_zone: str, subnet_id: str) -> "IPublicSubnet":
        """
        Arguments:
            scope: -
            id: -
            attrs: -
            availability_zone: The Availability Zone the subnet is located in.
            subnet_id: The subnetId for this particular subnet.

        Stability:
            experimental
        """
        attrs: PublicSubnetAttributes = {"availabilityZone": availability_zone, "subnetId": subnet_id}

        return jsii.sinvoke(cls, "fromPublicSubnetAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="addNatGateway")
    def add_nat_gateway(self) -> "CfnNatGateway":
        """Creates a new managed NAT gateway attached to this public subnet. Also adds the EIP for the managed NAT.

        Returns:
            A ref to the the NAT Gateway ID

        Stability:
            experimental
        """
        return jsii.invoke(self, "addNatGateway", [])


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.SubnetAttributes", jsii_struct_bases=[])
class SubnetAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    availabilityZone: str
    """The Availability Zone the subnet is located in.

    Stability:
        experimental
    """

    subnetId: str
    """The subnetId for this particular subnet.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.PrivateSubnetAttributes", jsii_struct_bases=[SubnetAttributes])
class PrivateSubnetAttributes(SubnetAttributes, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    pass

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.PublicSubnetAttributes", jsii_struct_bases=[SubnetAttributes])
class PublicSubnetAttributes(SubnetAttributes, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    pass

@jsii.data_type_optionals(jsii_struct_bases=[])
class _SubnetConfiguration(jsii.compat.TypedDict, total=False):
    cidrMask: jsii.Number
    """The CIDR Mask or the number of leading 1 bits in the routing mask.

    Valid values are 16 - 28

    Stability:
        experimental
    """
    reserved: bool
    """Controls if subnet IP space needs to be reserved.

    When true, the IP space for the subnet is reserved but no actual
    resources are provisioned. This space is only dependent on the
    number of availibility zones and on ``cidrMask`` - all other subnet
    properties are ignored.

    Default:
        false

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.SubnetConfiguration", jsii_struct_bases=[_SubnetConfiguration])
class SubnetConfiguration(_SubnetConfiguration):
    """Specify configuration parameters for a VPC to be built.

    Stability:
        experimental
    """
    name: str
    """The common Logical Name for the ``VpcSubnet``.

    This name will be suffixed with an integer correlating to a specific
    availability zone.

    Stability:
        experimental
    """

    subnetType: "SubnetType"
    """The type of Subnet to configure.

    The Subnet type will control the ability to route and connect to the
    Internet.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _SubnetProps(jsii.compat.TypedDict, total=False):
    mapPublicIpOnLaunch: bool
    """Controls if a public IP is associated to an instance at launch.

    Default:
        true in Subnet.Public, false in Subnet.Private or Subnet.Isolated.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.SubnetProps", jsii_struct_bases=[_SubnetProps])
class SubnetProps(_SubnetProps):
    """Specify configuration parameters for a VPC subnet.

    Stability:
        experimental
    """
    availabilityZone: str
    """The availability zone for the subnet.

    Stability:
        experimental
    """

    cidrBlock: str
    """The CIDR notation for this subnet.

    Stability:
        experimental
    """

    vpcId: str
    """The VPC which this subnet is part of.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.PrivateSubnetProps", jsii_struct_bases=[SubnetProps])
class PrivateSubnetProps(SubnetProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    pass

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.PublicSubnetProps", jsii_struct_bases=[SubnetProps])
class PublicSubnetProps(SubnetProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    pass

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.SubnetSelection", jsii_struct_bases=[])
class SubnetSelection(jsii.compat.TypedDict, total=False):
    """Customize subnets that are selected for placement of ENIs.

    Constructs that allow customization of VPC placement use parameters of this
    type to provide placement settings.

    By default, the instances are placed in the private subnets.

    Stability:
        experimental
    """
    onePerAz: bool
    """If true, return at most one subnet per AZ.

    Stability:
        experimental
    defautl:
        false
    """

    subnetName: str
    """Place the instances in the subnets with the given name.

    (This is the name supplied in subnetConfiguration).

    At most one of ``subnetType`` and ``subnetName`` can be supplied.

    Default:
        name

    Stability:
        experimental
    """

    subnetType: "SubnetType"
    """Place the instances in the subnets of the given type.

    At most one of ``subnetType`` and ``subnetName`` can be supplied.

    Default:
        SubnetType.Private

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ec2.SubnetType")
class SubnetType(enum.Enum):
    """The type of Subnet.

    Stability:
        experimental
    """
    ISOLATED = "ISOLATED"
    """Isolated Subnets do not route Outbound traffic.

    This can be good for subnets with RDS or
    Elasticache endpoints

    Stability:
        experimental
    """
    PRIVATE = "PRIVATE"
    """Subnet that routes to the internet, but not vice versa.

    Instances in a private subnet can connect to the Internet, but will not
    allow connections to be initiated from the Internet.

    Outbound traffic will be routed via a NAT Gateway. Preference being in
    the same AZ, but if not available will use another AZ (control by
    specifing ``maxGateways`` on VpcNetwork). This might be used for
    experimental cost conscious accounts or accounts where HA outbound
    traffic is not needed.

    Stability:
        experimental
    """
    PUBLIC = "PUBLIC"
    """Subnet connected to the Internet.

    Instances in a Public subnet can connect to the Internet and can be
    connected to from the Internet as long as they are launched with public
    IPs (controlled on the AutoScalingGroup or other constructs that launch
    instances).

    Public subnets route outbound traffic via an Internet Gateway.

    Stability:
        experimental
    """

class UserData(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-ec2.UserData"):
    """Instance User Data.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _UserDataProxy

    def __init__(self) -> None:
        jsii.create(UserData, self, [])

    @jsii.member(jsii_name="forLinux")
    @classmethod
    def for_linux(cls, *, shebang: typing.Optional[str]=None) -> "UserData":
        """Create a userdata object for Linux hosts.

        Arguments:
            options: -
            shebang: Shebang for the UserData script. Default: "#!/bin/bash"

        Stability:
            experimental
        """
        options: LinuxUserDataOptions = {}

        if shebang is not None:
            options["shebang"] = shebang

        return jsii.sinvoke(cls, "forLinux", [options])

    @jsii.member(jsii_name="forOperatingSystem")
    @classmethod
    def for_operating_system(cls, os: "OperatingSystemType") -> "UserData":
        """
        Arguments:
            os: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "forOperatingSystem", [os])

    @jsii.member(jsii_name="forWindows")
    @classmethod
    def for_windows(cls) -> "UserData":
        """Create a userdata object for Windows hosts.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "forWindows", [])

    @jsii.member(jsii_name="addCommands")
    @abc.abstractmethod
    def add_commands(self, *commands: str) -> None:
        """Add one or more commands to the user data.

        Arguments:
            commands: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="render")
    @abc.abstractmethod
    def render(self) -> str:
        """Render the UserData for use in a construct.

        Stability:
            experimental
        """
        ...


class _UserDataProxy(UserData):
    @jsii.member(jsii_name="addCommands")
    def add_commands(self, *commands: str) -> None:
        """Add one or more commands to the user data.

        Arguments:
            commands: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addCommands", [*commands])

    @jsii.member(jsii_name="render")
    def render(self) -> str:
        """Render the UserData for use in a construct.

        Stability:
            experimental
        """
        return jsii.invoke(self, "render", [])


@jsii.implements(IVpc)
class Vpc(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.Vpc"):
    """VpcNetwork deploys an AWS VPC, with public and private subnets per Availability Zone. For example:.

    Example::

       import { Vpc } from '@aws-cdk/aws-ec2'

       const vpc = new Vpc(this, {
          cidr: "10.0.0.0/16"
       })

       // Iterate the public subnets
       for (let subnet of vpc.publicSubnets) {

       }

       // Iterate the private subnets
       for (let subnet of vpc.privateSubnets) {

       }

    Stability:
        experimental
    resource:
        AWS::EC2::VPC
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, cidr: typing.Optional[str]=None, default_instance_tenancy: typing.Optional["DefaultInstanceTenancy"]=None, enable_dns_hostnames: typing.Optional[bool]=None, enable_dns_support: typing.Optional[bool]=None, gateway_endpoints: typing.Optional[typing.Mapping[str,"GatewayVpcEndpointOptions"]]=None, max_a_zs: typing.Optional[jsii.Number]=None, nat_gateways: typing.Optional[jsii.Number]=None, nat_gateway_subnets: typing.Optional["SubnetSelection"]=None, subnet_configuration: typing.Optional[typing.List["SubnetConfiguration"]]=None, vpn_connections: typing.Optional[typing.Mapping[str,"VpnConnectionOptions"]]=None, vpn_gateway: typing.Optional[bool]=None, vpn_gateway_asn: typing.Optional[jsii.Number]=None, vpn_route_propagation: typing.Optional[typing.List["SubnetSelection"]]=None) -> None:
        """VpcNetwork creates a VPC that spans a whole region. It will automatically divide the provided VPC CIDR range, and create public and private subnets per Availability Zone. Network routing for the public subnets will be configured to allow outbound access directly via an Internet Gateway. Network routing for the private subnets will be configured to allow outbound access via a set of resilient NAT Gateways (one per AZ).

        Arguments:
            scope: -
            id: -
            props: -
            cidr: The CIDR range to use for the VPC (e.g. '10.0.0.0/16'). Should be a minimum of /28 and maximum size of /16. The range will be split evenly into two subnets per Availability Zone (one public, one private). Default: Vpc.DEFAULT_CIDR_RANGE
            default_instance_tenancy: The default tenancy of instances launched into the VPC. By setting this to dedicated tenancy, instances will be launched on hardware dedicated to a single AWS customer, unless specifically specified at instance launch time. Please note, not all instance types are usable with Dedicated tenancy. Default: DefaultInstanceTenancy.Default (shared) tenancy
            enable_dns_hostnames: Indicates whether the instances launched in the VPC get public DNS hostnames. If this attribute is true, instances in the VPC get public DNS hostnames, but only if the enableDnsSupport attribute is also set to true. Default: true
            enable_dns_support: Indicates whether the DNS resolution is supported for the VPC. If this attribute is false, the Amazon-provided DNS server in the VPC that resolves public DNS hostnames to IP addresses is not enabled. If this attribute is true, queries to the Amazon provided DNS server at the 169.254.169.253 IP address, or the reserved IP address at the base of the VPC IPv4 network range plus two will succeed. Default: true
            gateway_endpoints: Gateway endpoints to add to this VPC. Default: - None.
            max_a_zs: Define the maximum number of AZs to use in this region. If the region has more AZs than you want to use (for example, because of EIP limits), pick a lower number here. The AZs will be sorted and picked from the start of the list. If you pick a higher number than the number of AZs in the region, all AZs in the region will be selected. To use "all AZs" available to your account, use a high number (such as 99). Default: 3
            nat_gateways: The number of NAT Gateways to create. For example, if set this to 1 and your subnet configuration is for 3 Public subnets then only one of the Public subnets will have a gateway and all Private subnets will route to this NAT Gateway. Default: maxAZs
            nat_gateway_subnets: Configures the subnets which will have NAT Gateways. You can pick a specific group of subnets by specifying the group name; the picked subnets must be public subnets. Default: - All public subnets.
            subnet_configuration: Configure the subnets to build for each AZ. The subnets are constructed in the context of the VPC so you only need specify the configuration. The VPC details (VPC ID, specific CIDR, specific AZ will be calculated during creation) For example if you want 1 public subnet, 1 private subnet, and 1 isolated subnet in each AZ provide the following: subnetConfiguration: [ { cidrMask: 24, name: 'ingress', subnetType: SubnetType.Public, }, { cidrMask: 24, name: 'application', subnetType: SubnetType.Private, }, { cidrMask: 28, name: 'rds', subnetType: SubnetType.Isolated, } ] ``cidrMask`` is optional and if not provided the IP space in the VPC will be evenly divided between the requested subnets. Default: - The VPC CIDR will be evenly divided between 1 public and 1 private subnet per AZ.
            vpn_connections: VPN connections to this VPC. Default: - No connections.
            vpn_gateway: Indicates whether a VPN gateway should be created and attached to this VPC. Default: - true when vpnGatewayAsn or vpnConnections is specified.
            vpn_gateway_asn: The private Autonomous System Number (ASN) for the VPN gateway. Default: - Amazon default ASN.
            vpn_route_propagation: Where to propagate VPN routes. Default: - On the route tables associated with private subnets.

        Stability:
            experimental
        """
        props: VpcProps = {}

        if cidr is not None:
            props["cidr"] = cidr

        if default_instance_tenancy is not None:
            props["defaultInstanceTenancy"] = default_instance_tenancy

        if enable_dns_hostnames is not None:
            props["enableDnsHostnames"] = enable_dns_hostnames

        if enable_dns_support is not None:
            props["enableDnsSupport"] = enable_dns_support

        if gateway_endpoints is not None:
            props["gatewayEndpoints"] = gateway_endpoints

        if max_a_zs is not None:
            props["maxAZs"] = max_a_zs

        if nat_gateways is not None:
            props["natGateways"] = nat_gateways

        if nat_gateway_subnets is not None:
            props["natGatewaySubnets"] = nat_gateway_subnets

        if subnet_configuration is not None:
            props["subnetConfiguration"] = subnet_configuration

        if vpn_connections is not None:
            props["vpnConnections"] = vpn_connections

        if vpn_gateway is not None:
            props["vpnGateway"] = vpn_gateway

        if vpn_gateway_asn is not None:
            props["vpnGatewayAsn"] = vpn_gateway_asn

        if vpn_route_propagation is not None:
            props["vpnRoutePropagation"] = vpn_route_propagation

        jsii.create(Vpc, self, [scope, id, props])

    @jsii.member(jsii_name="fromLookup")
    @classmethod
    def from_lookup(cls, scope: aws_cdk.core.Construct, id: str, *, is_default: typing.Optional[bool]=None, tags: typing.Optional[typing.Mapping[str,str]]=None, vpc_id: typing.Optional[str]=None, vpc_name: typing.Optional[str]=None) -> "IVpc":
        """Import an existing VPC from by querying the AWS environment this stack is deployed to.

        Arguments:
            scope: -
            id: -
            options: -
            is_default: Whether to match the default VPC. Default: Don't care whether we return the default VPC
            tags: Tags on the VPC. The VPC must have all of these tags Default: Don't filter on tags
            vpc_id: The ID of the VPC. If given, will import exactly this VPC. Default: Don't filter on vpcId
            vpc_name: The name of the VPC. If given, will import the VPC with this name. Default: Don't filter on vpcName

        Stability:
            experimental
        """
        options: VpcLookupOptions = {}

        if is_default is not None:
            options["isDefault"] = is_default

        if tags is not None:
            options["tags"] = tags

        if vpc_id is not None:
            options["vpcId"] = vpc_id

        if vpc_name is not None:
            options["vpcName"] = vpc_name

        return jsii.sinvoke(cls, "fromLookup", [scope, id, options])

    @jsii.member(jsii_name="fromVpcAttributes")
    @classmethod
    def from_vpc_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, availability_zones: typing.List[str], vpc_id: str, isolated_subnet_ids: typing.Optional[typing.List[str]]=None, isolated_subnet_names: typing.Optional[typing.List[str]]=None, private_subnet_ids: typing.Optional[typing.List[str]]=None, private_subnet_names: typing.Optional[typing.List[str]]=None, public_subnet_ids: typing.Optional[typing.List[str]]=None, public_subnet_names: typing.Optional[typing.List[str]]=None, vpn_gateway_id: typing.Optional[str]=None) -> "IVpc":
        """Import an exported VPC.

        Arguments:
            scope: -
            id: -
            attrs: -
            availability_zones: List of availability zones for the subnets in this VPC.
            vpc_id: VPC's identifier.
            isolated_subnet_ids: List of isolated subnet IDs. Must be undefined or match the availability zones in length and order.
            isolated_subnet_names: List of names for the isolated subnets. Must be undefined or have a name for every isolated subnet group.
            private_subnet_ids: List of private subnet IDs. Must be undefined or match the availability zones in length and order.
            private_subnet_names: List of names for the private subnets. Must be undefined or have a name for every private subnet group.
            public_subnet_ids: List of public subnet IDs. Must be undefined or match the availability zones in length and order.
            public_subnet_names: List of names for the public subnets. Must be undefined or have a name for every public subnet group.
            vpn_gateway_id: VPN gateway's identifier.

        Stability:
            experimental
        """
        attrs: VpcAttributes = {"availabilityZones": availability_zones, "vpcId": vpc_id}

        if isolated_subnet_ids is not None:
            attrs["isolatedSubnetIds"] = isolated_subnet_ids

        if isolated_subnet_names is not None:
            attrs["isolatedSubnetNames"] = isolated_subnet_names

        if private_subnet_ids is not None:
            attrs["privateSubnetIds"] = private_subnet_ids

        if private_subnet_names is not None:
            attrs["privateSubnetNames"] = private_subnet_names

        if public_subnet_ids is not None:
            attrs["publicSubnetIds"] = public_subnet_ids

        if public_subnet_names is not None:
            attrs["publicSubnetNames"] = public_subnet_names

        if vpn_gateway_id is not None:
            attrs["vpnGatewayId"] = vpn_gateway_id

        return jsii.sinvoke(cls, "fromVpcAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="addDynamoDbEndpoint")
    def add_dynamo_db_endpoint(self, id: str, subnets: typing.Optional[typing.List["SubnetSelection"]]=None) -> "GatewayVpcEndpoint":
        """Adds a new DynamoDB gateway endpoint to this VPC.

        Arguments:
            id: -
            subnets: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addDynamoDbEndpoint", [id, subnets])

    @jsii.member(jsii_name="addGatewayEndpoint")
    def add_gateway_endpoint(self, id: str, *, service: "IGatewayVpcEndpointService", subnets: typing.Optional[typing.List["SubnetSelection"]]=None) -> "GatewayVpcEndpoint":
        """Adds a new gateway endpoint to this VPC.

        Arguments:
            id: -
            options: -
            service: The service to use for this gateway VPC endpoint.
            subnets: Where to add endpoint routing. Default: private subnets

        Stability:
            experimental
        """
        options: GatewayVpcEndpointOptions = {"service": service}

        if subnets is not None:
            options["subnets"] = subnets

        return jsii.invoke(self, "addGatewayEndpoint", [id, options])

    @jsii.member(jsii_name="addInterfaceEndpoint")
    def add_interface_endpoint(self, id: str, *, service: "IInterfaceVpcEndpointService", private_dns_enabled: typing.Optional[bool]=None, subnets: typing.Optional["SubnetSelection"]=None) -> "InterfaceVpcEndpoint":
        """Adds a new interface endpoint to this VPC.

        Arguments:
            id: -
            options: -
            service: The service to use for this interface VPC endpoint.
            private_dns_enabled: Whether to associate a private hosted zone with the specified VPC. This allows you to make requests to the service using its default DNS hostname. Default: true
            subnets: The subnets in which to create an endpoint network interface. At most one per availability zone. Default: private subnets

        Stability:
            experimental
        """
        options: InterfaceVpcEndpointOptions = {"service": service}

        if private_dns_enabled is not None:
            options["privateDnsEnabled"] = private_dns_enabled

        if subnets is not None:
            options["subnets"] = subnets

        return jsii.invoke(self, "addInterfaceEndpoint", [id, options])

    @jsii.member(jsii_name="addS3Endpoint")
    def add_s3_endpoint(self, id: str, subnets: typing.Optional[typing.List["SubnetSelection"]]=None) -> "GatewayVpcEndpoint":
        """Adds a new S3 gateway endpoint to this VPC.

        Arguments:
            id: -
            subnets: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addS3Endpoint", [id, subnets])

    @jsii.member(jsii_name="addVpnConnection")
    def add_vpn_connection(self, id: str, *, ip: str, asn: typing.Optional[jsii.Number]=None, static_routes: typing.Optional[typing.List[str]]=None, tunnel_options: typing.Optional[typing.List["VpnTunnelOption"]]=None) -> "VpnConnection":
        """Adds a new VPN connection to this VPC.

        Arguments:
            id: -
            options: -
            ip: The ip address of the customer gateway.
            asn: The ASN of the customer gateway. Default: 65000
            static_routes: The static routes to be routed from the VPN gateway to the customer gateway. Default: Dynamic routing (BGP)
            tunnel_options: The tunnel options for the VPN connection. At most two elements (one per tunnel). Duplicates not allowed. Default: Amazon generated tunnel options

        Stability:
            experimental
        """
        options: VpnConnectionOptions = {"ip": ip}

        if asn is not None:
            options["asn"] = asn

        if static_routes is not None:
            options["staticRoutes"] = static_routes

        if tunnel_options is not None:
            options["tunnelOptions"] = tunnel_options

        return jsii.invoke(self, "addVpnConnection", [id, options])

    @jsii.member(jsii_name="selectSubnetObjects")
    def _select_subnet_objects(self, *, one_per_az: typing.Optional[bool]=None, subnet_name: typing.Optional[str]=None, subnet_type: typing.Optional["SubnetType"]=None) -> typing.List["ISubnet"]:
        """Return the subnets appropriate for the placement strategy.

        Arguments:
            selection: -
            one_per_az: If true, return at most one subnet per AZ.
            subnet_name: Place the instances in the subnets with the given name. (This is the name supplied in subnetConfiguration). At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: name
            subnet_type: Place the instances in the subnets of the given type. At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: SubnetType.Private

        Stability:
            experimental
        """
        selection: SubnetSelection = {}

        if one_per_az is not None:
            selection["onePerAz"] = one_per_az

        if subnet_name is not None:
            selection["subnetName"] = subnet_name

        if subnet_type is not None:
            selection["subnetType"] = subnet_type

        return jsii.invoke(self, "selectSubnetObjects", [selection])

    @jsii.member(jsii_name="selectSubnets")
    def select_subnets(self, *, one_per_az: typing.Optional[bool]=None, subnet_name: typing.Optional[str]=None, subnet_type: typing.Optional["SubnetType"]=None) -> "SelectedSubnets":
        """Returns IDs of selected subnets.

        Arguments:
            selection: -
            one_per_az: If true, return at most one subnet per AZ.
            subnet_name: Place the instances in the subnets with the given name. (This is the name supplied in subnetConfiguration). At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: name
            subnet_type: Place the instances in the subnets of the given type. At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: SubnetType.Private

        Stability:
            experimental
        """
        selection: SubnetSelection = {}

        if one_per_az is not None:
            selection["onePerAz"] = one_per_az

        if subnet_name is not None:
            selection["subnetName"] = subnet_name

        if subnet_type is not None:
            selection["subnetType"] = subnet_type

        return jsii.invoke(self, "selectSubnets", [selection])

    @classproperty
    @jsii.member(jsii_name="DEFAULT_CIDR_RANGE")
    def DEFAULT_CIDR_RANGE(cls) -> str:
        """The default CIDR range used when creating VPCs. This can be overridden using VpcNetworkProps when creating a VPCNetwork resource. e.g. new VpcResource(this, { cidr: '192.168.0.0./16' }).

        Stability:
            experimental
        """
        return jsii.sget(cls, "DEFAULT_CIDR_RANGE")

    @classproperty
    @jsii.member(jsii_name="DEFAULT_SUBNETS")
    def DEFAULT_SUBNETS(cls) -> typing.List["SubnetConfiguration"]:
        """The default subnet configuration.

        1 Public and 1 Private subnet per AZ evenly split

        Stability:
            experimental
        """
        return jsii.sget(cls, "DEFAULT_SUBNETS")

    @property
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[str]:
        """AZs for this VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "availabilityZones")

    @property
    @jsii.member(jsii_name="internetConnectivityEstablished")
    def internet_connectivity_established(self) -> aws_cdk.core.IDependable:
        """Dependencies for internet connectivity.

        Stability:
            experimental
        """
        return jsii.get(self, "internetConnectivityEstablished")

    @property
    @jsii.member(jsii_name="isolatedSubnets")
    def isolated_subnets(self) -> typing.List["ISubnet"]:
        """List of isolated subnets in this VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "isolatedSubnets")

    @property
    @jsii.member(jsii_name="natDependencies")
    def _nat_dependencies(self) -> typing.List[aws_cdk.core.IConstruct]:
        """Dependencies for NAT connectivity.

        Stability:
            experimental
        """
        return jsii.get(self, "natDependencies")

    @property
    @jsii.member(jsii_name="privateSubnets")
    def private_subnets(self) -> typing.List["ISubnet"]:
        """List of private subnets in this VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "privateSubnets")

    @property
    @jsii.member(jsii_name="publicSubnets")
    def public_subnets(self) -> typing.List["ISubnet"]:
        """List of public subnets in this VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "publicSubnets")

    @property
    @jsii.member(jsii_name="vpcCidrBlock")
    def vpc_cidr_block(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcCidrBlock")

    @property
    @jsii.member(jsii_name="vpcCidrBlockAssociations")
    def vpc_cidr_block_associations(self) -> typing.List[str]:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcCidrBlockAssociations")

    @property
    @jsii.member(jsii_name="vpcDefaultNetworkAcl")
    def vpc_default_network_acl(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcDefaultNetworkAcl")

    @property
    @jsii.member(jsii_name="vpcDefaultSecurityGroup")
    def vpc_default_security_group(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcDefaultSecurityGroup")

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """Identifier for this VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "vpcId")

    @property
    @jsii.member(jsii_name="vpcIpv6CidrBlocks")
    def vpc_ipv6_cidr_blocks(self) -> typing.List[str]:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcIpv6CidrBlocks")

    @property
    @jsii.member(jsii_name="vpnGatewayId")
    def vpn_gateway_id(self) -> typing.Optional[str]:
        """Identifier for the VPN gateway.

        Stability:
            experimental
        """
        return jsii.get(self, "vpnGatewayId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _VpcAttributes(jsii.compat.TypedDict, total=False):
    isolatedSubnetIds: typing.List[str]
    """List of isolated subnet IDs.

    Must be undefined or match the availability zones in length and order.

    Stability:
        experimental
    """
    isolatedSubnetNames: typing.List[str]
    """List of names for the isolated subnets.

    Must be undefined or have a name for every isolated subnet group.

    Stability:
        experimental
    """
    privateSubnetIds: typing.List[str]
    """List of private subnet IDs.

    Must be undefined or match the availability zones in length and order.

    Stability:
        experimental
    """
    privateSubnetNames: typing.List[str]
    """List of names for the private subnets.

    Must be undefined or have a name for every private subnet group.

    Stability:
        experimental
    """
    publicSubnetIds: typing.List[str]
    """List of public subnet IDs.

    Must be undefined or match the availability zones in length and order.

    Stability:
        experimental
    """
    publicSubnetNames: typing.List[str]
    """List of names for the public subnets.

    Must be undefined or have a name for every public subnet group.

    Stability:
        experimental
    """
    vpnGatewayId: str
    """VPN gateway's identifier.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.VpcAttributes", jsii_struct_bases=[_VpcAttributes])
class VpcAttributes(_VpcAttributes):
    """Properties that reference an external VpcNetwork.

    Stability:
        experimental
    """
    availabilityZones: typing.List[str]
    """List of availability zones for the subnets in this VPC.

    Stability:
        experimental
    """

    vpcId: str
    """VPC's identifier.

    Stability:
        experimental
    """

@jsii.implements(IVpcEndpoint)
class VpcEndpoint(aws_cdk.core.Resource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-ec2.VpcEndpoint"):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _VpcEndpointProxy

    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, physical_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time

        Stability:
            experimental
        """
        props: aws_cdk.core.ResourceProps = {}

        if physical_name is not None:
            props["physicalName"] = physical_name

        jsii.create(VpcEndpoint, self, [scope, id, props])

    @jsii.member(jsii_name="addToPolicy")
    def add_to_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Adds a statement to the policy document of the VPC endpoint. The statement must have a Principal.

        Not all interface VPC endpoints support policy. For more information
        see https://docs.aws.amazon.com/vpc/latest/userguide/vpce-interface.html

        Arguments:
            statement: the IAM statement to add.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToPolicy", [statement])

    @property
    @jsii.member(jsii_name="vpcEndpointId")
    @abc.abstractmethod
    def vpc_endpoint_id(self) -> str:
        """The VPC endpoint identifier.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="policyDocument")
    def _policy_document(self) -> typing.Optional[aws_cdk.aws_iam.PolicyDocument]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "policyDocument")

    @_policy_document.setter
    def _policy_document(self, value: typing.Optional[aws_cdk.aws_iam.PolicyDocument]):
        return jsii.set(self, "policyDocument", value)


class _VpcEndpointProxy(VpcEndpoint, jsii.proxy_for(aws_cdk.core.Resource)):
    @property
    @jsii.member(jsii_name="vpcEndpointId")
    def vpc_endpoint_id(self) -> str:
        """The VPC endpoint identifier.

        Stability:
            experimental
        """
        return jsii.get(self, "vpcEndpointId")


@jsii.implements(IGatewayVpcEndpoint)
class GatewayVpcEndpoint(VpcEndpoint, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.GatewayVpcEndpoint"):
    """A gateway VPC endpoint.

    Stability:
        experimental
    resource:
        AWS::EC2::VPCEndpoint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, vpc: "IVpc", service: "IGatewayVpcEndpointService", subnets: typing.Optional[typing.List["SubnetSelection"]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            vpc: The VPC network in which the gateway endpoint will be used.
            service: The service to use for this gateway VPC endpoint.
            subnets: Where to add endpoint routing. Default: private subnets

        Stability:
            experimental
        """
        props: GatewayVpcEndpointProps = {"vpc": vpc, "service": service}

        if subnets is not None:
            props["subnets"] = subnets

        jsii.create(GatewayVpcEndpoint, self, [scope, id, props])

    @jsii.member(jsii_name="fromGatewayVpcEndpointId")
    @classmethod
    def from_gateway_vpc_endpoint_id(cls, scope: aws_cdk.core.Construct, id: str, gateway_vpc_endpoint_id: str) -> "IGatewayVpcEndpoint":
        """
        Arguments:
            scope: -
            id: -
            gateway_vpc_endpoint_id: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromGatewayVpcEndpointId", [scope, id, gateway_vpc_endpoint_id])

    @property
    @jsii.member(jsii_name="vpcEndpointCreationTimestamp")
    def vpc_endpoint_creation_timestamp(self) -> str:
        """The date and time the gateway VPC endpoint was created.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcEndpointCreationTimestamp")

    @property
    @jsii.member(jsii_name="vpcEndpointDnsEntries")
    def vpc_endpoint_dns_entries(self) -> typing.List[str]:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcEndpointDnsEntries")

    @property
    @jsii.member(jsii_name="vpcEndpointId")
    def vpc_endpoint_id(self) -> str:
        """The gateway VPC endpoint identifier.

        Stability:
            experimental
        """
        return jsii.get(self, "vpcEndpointId")

    @property
    @jsii.member(jsii_name="vpcEndpointNetworkInterfaceIds")
    def vpc_endpoint_network_interface_ids(self) -> typing.List[str]:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcEndpointNetworkInterfaceIds")


@jsii.implements(IInterfaceVpcEndpoint)
class InterfaceVpcEndpoint(VpcEndpoint, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.InterfaceVpcEndpoint"):
    """A interface VPC endpoint.

    Stability:
        experimental
    resource:
        AWS::EC2::VPCEndpoint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, vpc: "IVpc", service: "IInterfaceVpcEndpointService", private_dns_enabled: typing.Optional[bool]=None, subnets: typing.Optional["SubnetSelection"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            vpc: The VPC network in which the interface endpoint will be used.
            service: The service to use for this interface VPC endpoint.
            private_dns_enabled: Whether to associate a private hosted zone with the specified VPC. This allows you to make requests to the service using its default DNS hostname. Default: true
            subnets: The subnets in which to create an endpoint network interface. At most one per availability zone. Default: private subnets

        Stability:
            experimental
        """
        props: InterfaceVpcEndpointProps = {"vpc": vpc, "service": service}

        if private_dns_enabled is not None:
            props["privateDnsEnabled"] = private_dns_enabled

        if subnets is not None:
            props["subnets"] = subnets

        jsii.create(InterfaceVpcEndpoint, self, [scope, id, props])

    @jsii.member(jsii_name="fromInterfaceVpcEndpointAttributes")
    @classmethod
    def from_interface_vpc_endpoint_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, port: jsii.Number, security_group_id: str, vpc_endpoint_id: str) -> "IInterfaceVpcEndpoint":
        """Imports an existing interface VPC endpoint.

        Arguments:
            scope: -
            id: -
            attrs: -
            port: The port of the service of the interface VPC endpoint.
            security_group_id: The identifier of the security group associated with the interface VPC endpoint.
            vpc_endpoint_id: The interface VPC endpoint identifier.

        Stability:
            experimental
        """
        attrs: InterfaceVpcEndpointAttributes = {"port": port, "securityGroupId": security_group_id, "vpcEndpointId": vpc_endpoint_id}

        return jsii.sinvoke(cls, "fromInterfaceVpcEndpointAttributes", [scope, id, attrs])

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> "Connections":
        """Access to network connections.

        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """The identifier of the security group associated with this interface VPC endpoint.

        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupId")

    @property
    @jsii.member(jsii_name="vpcEndpointCreationTimestamp")
    def vpc_endpoint_creation_timestamp(self) -> str:
        """The date and time the interface VPC endpoint was created.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcEndpointCreationTimestamp")

    @property
    @jsii.member(jsii_name="vpcEndpointDnsEntries")
    def vpc_endpoint_dns_entries(self) -> typing.List[str]:
        """The DNS entries for the interface VPC endpoint.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcEndpointDnsEntries")

    @property
    @jsii.member(jsii_name="vpcEndpointId")
    def vpc_endpoint_id(self) -> str:
        """The interface VPC endpoint identifier.

        Stability:
            experimental
        """
        return jsii.get(self, "vpcEndpointId")

    @property
    @jsii.member(jsii_name="vpcEndpointNetworkInterfaceIds")
    def vpc_endpoint_network_interface_ids(self) -> typing.List[str]:
        """One or more network interfaces for the interface VPC endpoint.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcEndpointNetworkInterfaceIds")


@jsii.enum(jsii_type="@aws-cdk/aws-ec2.VpcEndpointType")
class VpcEndpointType(enum.Enum):
    """The type of VPC endpoint.

    Stability:
        experimental
    """
    INTERFACE = "INTERFACE"
    """Interface.

    An interface endpoint is an elastic network interface with a private IP
    address that serves as an entry point for traffic destined to a supported
    service.

    Stability:
        experimental
    """
    GATEWAY = "GATEWAY"
    """Gateway.

    A gateway endpoint is a gateway that is a target for a specified route in
    your route table, used for traffic destined to a supported AWS service.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.VpcLookupOptions", jsii_struct_bases=[])
class VpcLookupOptions(jsii.compat.TypedDict, total=False):
    """Properties for looking up an existing VPC.

    The combination of properties must specify filter down to exactly one
    non-default VPC, otherwise an error is raised.

    Stability:
        experimental
    """
    isDefault: bool
    """Whether to match the default VPC.

    Default:
        Don't care whether we return the default VPC

    Stability:
        experimental
    """

    tags: typing.Mapping[str,str]
    """Tags on the VPC.

    The VPC must have all of these tags

    Default:
        Don't filter on tags

    Stability:
        experimental
    """

    vpcId: str
    """The ID of the VPC.

    If given, will import exactly this VPC.

    Default:
        Don't filter on vpcId

    Stability:
        experimental
    """

    vpcName: str
    """The name of the VPC.

    If given, will import the VPC with this name.

    Default:
        Don't filter on vpcName

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.VpcProps", jsii_struct_bases=[])
class VpcProps(jsii.compat.TypedDict, total=False):
    """Configuration for Vpc.

    Stability:
        experimental
    """
    cidr: str
    """The CIDR range to use for the VPC (e.g. '10.0.0.0/16'). Should be a minimum of /28 and maximum size of /16. The range will be split evenly into two subnets per Availability Zone (one public, one private).

    Default:
        Vpc.DEFAULT_CIDR_RANGE

    Stability:
        experimental
    """

    defaultInstanceTenancy: "DefaultInstanceTenancy"
    """The default tenancy of instances launched into the VPC. By setting this to dedicated tenancy, instances will be launched on hardware dedicated to a single AWS customer, unless specifically specified at instance launch time. Please note, not all instance types are usable with Dedicated tenancy.

    Default:
        DefaultInstanceTenancy.Default (shared) tenancy

    Stability:
        experimental
    """

    enableDnsHostnames: bool
    """Indicates whether the instances launched in the VPC get public DNS hostnames. If this attribute is true, instances in the VPC get public DNS hostnames, but only if the enableDnsSupport attribute is also set to true.

    Default:
        true

    Stability:
        experimental
    """

    enableDnsSupport: bool
    """Indicates whether the DNS resolution is supported for the VPC.

    If this attribute
    is false, the Amazon-provided DNS server in the VPC that resolves public DNS hostnames
    to IP addresses is not enabled. If this attribute is true, queries to the Amazon
    provided DNS server at the 169.254.169.253 IP address, or the reserved IP address
    at the base of the VPC IPv4 network range plus two will succeed.

    Default:
        true

    Stability:
        experimental
    """

    gatewayEndpoints: typing.Mapping[str,"GatewayVpcEndpointOptions"]
    """Gateway endpoints to add to this VPC.

    Default:
        - None.

    Stability:
        experimental
    """

    maxAZs: jsii.Number
    """Define the maximum number of AZs to use in this region.

    If the region has more AZs than you want to use (for example, because of EIP limits),
    pick a lower number here. The AZs will be sorted and picked from the start of the list.

    If you pick a higher number than the number of AZs in the region, all AZs in
    the region will be selected. To use "all AZs" available to your account, use a
    high number (such as 99).

    Default:
        3

    Stability:
        experimental
    """

    natGateways: jsii.Number
    """The number of NAT Gateways to create.

    For example, if set this to 1 and your subnet configuration is for 3 Public subnets then only
    one of the Public subnets will have a gateway and all Private subnets will route to this NAT Gateway.

    Default:
        maxAZs

    Stability:
        experimental
    """

    natGatewaySubnets: "SubnetSelection"
    """Configures the subnets which will have NAT Gateways.

    You can pick a specific group of subnets by specifying the group name;
    the picked subnets must be public subnets.

    Default:
        - All public subnets.

    Stability:
        experimental
    """

    subnetConfiguration: typing.List["SubnetConfiguration"]
    """Configure the subnets to build for each AZ.

    The subnets are constructed in the context of the VPC so you only need
    specify the configuration. The VPC details (VPC ID, specific CIDR,
    specific AZ will be calculated during creation)

    For example if you want 1 public subnet, 1 private subnet, and 1 isolated
    subnet in each AZ provide the following:
    subnetConfiguration: [
    {
    cidrMask: 24,
    name: 'ingress',
    subnetType: SubnetType.Public,
    },
    {
    cidrMask: 24,
    name: 'application',
    subnetType: SubnetType.Private,
    },
    {
    cidrMask: 28,
    name: 'rds',
    subnetType: SubnetType.Isolated,
    }
    ]

    ``cidrMask`` is optional and if not provided the IP space in the VPC will be
    evenly divided between the requested subnets.

    Default:
        - The VPC CIDR will be evenly divided between 1 public and 1
          private subnet per AZ.

    Stability:
        experimental
    """

    vpnConnections: typing.Mapping[str,"VpnConnectionOptions"]
    """VPN connections to this VPC.

    Default:
        - No connections.

    Stability:
        experimental
    """

    vpnGateway: bool
    """Indicates whether a VPN gateway should be created and attached to this VPC.

    Default:
        - true when vpnGatewayAsn or vpnConnections is specified.

    Stability:
        experimental
    """

    vpnGatewayAsn: jsii.Number
    """The private Autonomous System Number (ASN) for the VPN gateway.

    Default:
        - Amazon default ASN.

    Stability:
        experimental
    """

    vpnRoutePropagation: typing.List["SubnetSelection"]
    """Where to propagate VPN routes.

    Default:
        - On the route tables associated with private subnets.

    Stability:
        experimental
    """

@jsii.implements(IVpnConnection)
class VpnConnection(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.VpnConnection"):
    """Define a VPN Connection.

    Stability:
        experimental
    resource:
        AWS::EC2::VPNConnection
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, vpc: "IVpc", ip: str, asn: typing.Optional[jsii.Number]=None, static_routes: typing.Optional[typing.List[str]]=None, tunnel_options: typing.Optional[typing.List["VpnTunnelOption"]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            vpc: The VPC to connect to.
            ip: The ip address of the customer gateway.
            asn: The ASN of the customer gateway. Default: 65000
            static_routes: The static routes to be routed from the VPN gateway to the customer gateway. Default: Dynamic routing (BGP)
            tunnel_options: The tunnel options for the VPN connection. At most two elements (one per tunnel). Duplicates not allowed. Default: Amazon generated tunnel options

        Stability:
            experimental
        """
        props: VpnConnectionProps = {"vpc": vpc, "ip": ip}

        if asn is not None:
            props["asn"] = asn

        if static_routes is not None:
            props["staticRoutes"] = static_routes

        if tunnel_options is not None:
            props["tunnelOptions"] = tunnel_options

        jsii.create(VpnConnection, self, [scope, id, props])

    @jsii.member(jsii_name="metricAll")
    @classmethod
    def metric_all(cls, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for all VPN connections in the account/region.

        Arguments:
            metric_name: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.sinvoke(cls, "metricAll", [metric_name, props])

    @jsii.member(jsii_name="metricAllTunnelDataIn")
    @classmethod
    def metric_all_tunnel_data_in(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the tunnel data in of all VPN connections in the account/region.

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            sum over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.sinvoke(cls, "metricAllTunnelDataIn", [props])

    @jsii.member(jsii_name="metricAllTunnelDataOut")
    @classmethod
    def metric_all_tunnel_data_out(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the tunnel data out of all VPN connections.

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            sum over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.sinvoke(cls, "metricAllTunnelDataOut", [props])

    @jsii.member(jsii_name="metricAllTunnelState")
    @classmethod
    def metric_all_tunnel_state(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the tunnel state of all VPN connections in the account/region.

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            average over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.sinvoke(cls, "metricAllTunnelState", [props])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this VPNConnection.

        Arguments:
            metric_name: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricTunnelDataIn")
    def metric_tunnel_data_in(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The bytes received through the VPN tunnel.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricTunnelDataIn", [props])

    @jsii.member(jsii_name="metricTunnelDataOut")
    def metric_tunnel_data_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The bytes sent through the VPN tunnel.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricTunnelDataOut", [props])

    @jsii.member(jsii_name="metricTunnelState")
    def metric_tunnel_state(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The state of the tunnel. 0 indicates DOWN and 1 indicates UP.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricTunnelState", [props])

    @property
    @jsii.member(jsii_name="customerGatewayAsn")
    def customer_gateway_asn(self) -> jsii.Number:
        """The ASN of the customer gateway.

        Stability:
            experimental
        """
        return jsii.get(self, "customerGatewayAsn")

    @property
    @jsii.member(jsii_name="customerGatewayId")
    def customer_gateway_id(self) -> str:
        """The id of the customer gateway.

        Stability:
            experimental
        """
        return jsii.get(self, "customerGatewayId")

    @property
    @jsii.member(jsii_name="customerGatewayIp")
    def customer_gateway_ip(self) -> str:
        """The ip address of the customer gateway.

        Stability:
            experimental
        """
        return jsii.get(self, "customerGatewayIp")

    @property
    @jsii.member(jsii_name="vpnId")
    def vpn_id(self) -> str:
        """The id of the VPN connection.

        Stability:
            experimental
        """
        return jsii.get(self, "vpnId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _VpnConnectionOptions(jsii.compat.TypedDict, total=False):
    asn: jsii.Number
    """The ASN of the customer gateway.

    Default:
        65000

    Stability:
        experimental
    """
    staticRoutes: typing.List[str]
    """The static routes to be routed from the VPN gateway to the customer gateway.

    Default:
        Dynamic routing (BGP)

    Stability:
        experimental
    """
    tunnelOptions: typing.List["VpnTunnelOption"]
    """The tunnel options for the VPN connection.

    At most two elements (one per tunnel).
    Duplicates not allowed.

    Default:
        Amazon generated tunnel options

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.VpnConnectionOptions", jsii_struct_bases=[_VpnConnectionOptions])
class VpnConnectionOptions(_VpnConnectionOptions):
    """
    Stability:
        experimental
    """
    ip: str
    """The ip address of the customer gateway.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.VpnConnectionProps", jsii_struct_bases=[VpnConnectionOptions])
class VpnConnectionProps(VpnConnectionOptions, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    vpc: "IVpc"
    """The VPC to connect to.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ec2.VpnConnectionType")
class VpnConnectionType(enum.Enum):
    """The VPN connection type.

    Stability:
        experimental
    """
    IPSEC_1 = "IPSEC_1"
    """The IPsec 1 VPN connection type.

    Stability:
        experimental
    """
    DUMMY = "DUMMY"
    """Dummy member TODO: remove once https://github.com/awslabs/jsii/issues/231 is fixed.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.VpnTunnelOption", jsii_struct_bases=[])
class VpnTunnelOption(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    preSharedKey: str
    """The pre-shared key (PSK) to establish initial authentication between the virtual private gateway and customer gateway.

    Allowed characters are alphanumeric characters
    and ._. Must be between 8 and 64 characters in length and cannot start with zero (0).

    Default:
        an Amazon generated pre-shared key

    Stability:
        experimental
    """

    tunnelInsideCidr: str
    """The range of inside IP addresses for the tunnel.

    Any specified CIDR blocks must be
    unique across all VPN connections that use the same virtual private gateway.
    A size /30 CIDR block from the 169.254.0.0/16 range.

    Default:
        an Amazon generated inside IP CIDR

    Stability:
        experimental
    """

@jsii.implements(IMachineImage)
class WindowsImage(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.WindowsImage"):
    """Select the latest version of the indicated Windows version.

    The AMI ID is selected using the values published to the SSM parameter store.

    https://aws.amazon.com/blogs/mt/query-for-the-latest-windows-ami-using-systems-manager-parameter-store/

    Stability:
        experimental
    """
    def __init__(self, version: "WindowsVersion", *, user_data: typing.Optional["UserData"]=None) -> None:
        """
        Arguments:
            version: -
            props: -
            user_data: Initial user data. Default: - Empty UserData for Windows machines

        Stability:
            experimental
        """
        props: WindowsImageProps = {}

        if user_data is not None:
            props["userData"] = user_data

        jsii.create(WindowsImage, self, [version, props])

    @jsii.member(jsii_name="getImage")
    def get_image(self, scope: aws_cdk.core.Construct) -> "MachineImageConfig":
        """Return the image to use in the given context.

        Arguments:
            scope: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getImage", [scope])


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.WindowsImageProps", jsii_struct_bases=[])
class WindowsImageProps(jsii.compat.TypedDict, total=False):
    """Configuration options for WindowsImage.

    Stability:
        experimental
    """
    userData: "UserData"
    """Initial user data.

    Default:
        - Empty UserData for Windows machines

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ec2.WindowsVersion")
class WindowsVersion(enum.Enum):
    """The Windows version to use for the WindowsImage.

    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_SP2_ENGLISH_64BIT_SQL_2008_SP4_EXPRESS = "WINDOWS_SERVER_2008_SP2_ENGLISH_64BIT_SQL_2008_SP4_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_CHINESE_SIMPLIFIED_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_CHINESE_SIMPLIFIED_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_CHINESE_TRADITIONAL_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_CHINESE_TRADITIONAL_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_DUTCH_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_DUTCH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP2_ENTERPRISE = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP2_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_HUNGARIAN_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_HUNGARIAN_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_CORE_CONTAINERS = "WINDOWS_SERVER_2016_ENGLISH_CORE_CONTAINERS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP1_WEB = "WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP1_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_GERMAL_FULL_BASE = "WINDOWS_SERVER_2016_GERMAL_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2003_R2_SP2_LANGUAGE_PACKS_32BIT_BASE = "WINDOWS_SERVER_2003_R2_SP2_LANGUAGE_PACKS_32BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2008_R2_SP3_WEB = "WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2008_R2_SP3_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2012_SP4_EXPRESS = "WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2012_SP4_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_SP1_PORTUGESE_BRAZIL_64BIT_CORE = "WINDOWS_SERVER_2012_R2_SP1_PORTUGESE_BRAZIL_64BIT_CORE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP2_STANDARD = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP2_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2014_SP2_EXPRESS = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2014_SP2_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ITALIAN_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_ITALIAN_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP1_EXPRESS = "WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP1_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_DEEP_LEARNING = "WINDOWS_SERVER_2016_ENGLISH_DEEP_LEARNING"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ITALIAN_FULL_BASE = "WINDOWS_SERVER_2019_ITALIAN_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_KOREAN_64BIT_BASE = "WINDOWS_SERVER_2008_R2_SP1_KOREAN_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP1_EXPRESS = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP1_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP2_WEB = "WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP2_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_JAPANESE_FULL_FQL_2016_SP2_WEB = "WINDOWS_SERVER_2016_JAPANESE_FULL_FQL_2016_SP2_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_KOREAN_FULL_BASE = "WINDOWS_SERVER_2016_KOREAN_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_KOREAN_FULL_SQL_2016_SP2_STANDARD = "WINDOWS_SERVER_2016_KOREAN_FULL_SQL_2016_SP2_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_PORTUGESE_PORTUGAL_FULL_BASE = "WINDOWS_SERVER_2016_PORTUGESE_PORTUGAL_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2017_WEB = "WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2017_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_FRENCH_FULL_BASE = "WINDOWS_SERVER_2019_FRENCH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_KOREAN_FULL_BASE = "WINDOWS_SERVER_2019_KOREAN_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_CHINESE_HONG_KONG_SAR_64BIT_BASE = "WINDOWS_SERVER_2008_R2_SP1_CHINESE_HONG_KONG_SAR_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_CHINESE_PRC_64BIT_BASE = "WINDOWS_SERVER_2008_R2_SP1_CHINESE_PRC_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_FRENCH_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_FRENCH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_CONTAINERS = "WINDOWS_SERVER_2016_ENGLISH_FULL_CONTAINERS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP1_STANDARD = "WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP1_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_RUSSIAN_FULL_BASE = "WINDOWS_SERVER_2016_RUSSIAN_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_CHINESE_SIMPLIFIED_FULL_BASE = "WINDOWS_SERVER_2019_CHINESE_SIMPLIFIED_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2016_SP2_STANDARD = "WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2016_SP2_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_HUNGARIAN_FULL_BASE = "WINDOWS_SERVER_2019_HUNGARIAN_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2008_R2_SP3_EXPRESS = "WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2008_R2_SP3_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2007_R2_SP1_LANGUAGE_PACKS_64BIT_BASE = "WINDOWS_SERVER_2007_R2_SP1_LANGUAGE_PACKS_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_SP2_ENGLISH_32BIT_BASE = "WINDOWS_SERVER_2008_SP2_ENGLISH_32BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2012_SP4_ENTERPRISE = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2012_SP4_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_CHINESE_TRADITIONAL_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_CHINESE_TRADITIONAL_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2008_R2_SP3_EXPRESS = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2008_R2_SP3_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2014_SP2_STANDARD = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2014_SP2_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2014_SP2_EXPRESS = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2014_SP2_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_POLISH_FULL_BASE = "WINDOWS_SERVER_2016_POLISH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2016_SP2_WEB = "WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2016_SP2_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP3_STANDARD = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP3_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP2_EXPRESS = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP2_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_DEEP_LEARNING = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_DEEP_LEARNING"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_GERMAN_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_GERMAN_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP1_EXPRESS = "WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP1_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_RUSSIAN_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_RUSSIAN_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_CHINESE_TRADITIONAL_HONG_KONG_SAR_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_CHINESE_TRADITIONAL_HONG_KONG_SAR_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_HUNGARIAN_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_HUNGARIAN_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2014_SP3_STANDARD = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2014_SP3_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_FULL_HYPERV = "WINDOWS_SERVER_2019_ENGLISH_FULL_HYPERV"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2003_R2_SP2_ENGLISH_64BIT_SQL_2005_SP4_EXPRESS = "WINDOWS_SERVER_2003_R2_SP2_ENGLISH_64BIT_SQL_2005_SP4_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_JAPANESE_64BIT_SQL_2012_SP4_EXPRESS = "WINDOWS_SERVER_2008_R2_SP1_JAPANESE_64BIT_SQL_2012_SP4_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_GERMAN_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_GERMAN_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2008_R2_SP3_STANDARD = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2008_R2_SP3_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP2_STANDARD = "WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP2_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2017_EXPRESS = "WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2017_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_JAPANESE_FULL_BASE = "WINDOWS_SERVER_2019_JAPANESE_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_RUSSIAN_FULL_BASE = "WINDOWS_SERVER_2019_RUSSIAN_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP2_STANDARD = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP2_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ITALIAN_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_ITALIAN_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2008_R2_SP3_STANDARD = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2008_R2_SP3_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_HYPERV = "WINDOWS_SERVER_2016_ENGLISH_FULL_HYPERV"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP2_ENTERPRISE = "WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP2_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_CHINESE_TRADITIONAL_FULL_BASE = "WINDOWS_SERVER_2019_CHINESE_TRADITIONAL_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_CORE_BASE = "WINDOWS_SERVER_2019_ENGLISH_CORE_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_CORE_CONTAINERSLATEST = "WINDOWS_SERVER_2019_ENGLISH_CORE_CONTAINERSLATEST"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_SP2_ENGLISH_64BIT_BASE = "WINDOWS_SERVER_2008_SP2_ENGLISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_FRENCH_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_FRENCH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_POLISH_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_POLISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2012_SP4_EXPRESS = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2012_SP4_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2014_SP3_STANDARD = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2014_SP3_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_2012_SP4_STANDARD = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_2012_SP4_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_CORE_CONTAINERSLATEST = "WINDOWS_SERVER_2016_ENGLISH_CORE_CONTAINERSLATEST"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2016_SP2_EXPRESS = "WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2016_SP2_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_TURKISH_FULL_BASE = "WINDOWS_SERVER_2019_TURKISH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP2_EXPRESS = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP2_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP3_WEB = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP3_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP1_WEB = "WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP1_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_PORTUGESE_BRAZIL_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_PORTUGESE_BRAZIL_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_PORTUGESE_PORTUGAL_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_PORTUGESE_PORTUGAL_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_SWEDISH_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_SWEDISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP1_EXPRESS = "WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP1_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ITALIAN_FULL_BASE = "WINDOWS_SERVER_2016_ITALIAN_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_SPANISH_FULL_BASE = "WINDOWS_SERVER_2016_SPANISH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2017_STANDARD = "WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2017_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2003_R2_SP2_LANGUAGE_PACKS_64BIT_SQL_2005_SP4_STANDARD = "WINDOWS_SERVER_2003_R2_SP2_LANGUAGE_PACKS_64BIT_SQL_2005_SP4_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_JAPANESE_64BIT_SQL_2008_R2_SP3_STANDARD = "WINDOWS_SERVER_2008_R2_SP1_JAPANESE_64BIT_SQL_2008_R2_SP3_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP1_STANDARD = "WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP1_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2007_R2_SP3_WEB = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2007_R2_SP3_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2014_SP2_WEB = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2014_SP2_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP2_ENTERPRISE = "WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP2_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_PORTUGESE_BRAZIL_FULL_BASE = "WINDOWS_SERVER_2016_PORTUGESE_BRAZIL_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_FULL_BASE = "WINDOWS_SERVER_2019_ENGLISH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2003_R2_SP2_ENGLISH_32BIT_BASE = "WINDOWS_SERVER_2003_R2_SP2_ENGLISH_32BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_CZECH_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_CZECH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP1_STANDARD = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP1_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2014_SP2_EXPRESS = "WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2014_SP2_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2012_SP4_STANDARD = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2012_SP4_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP1_ENTERPRISE = "WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP1_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP1_WEB = "WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP1_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_SWEDISH_FULL_BASE = "WINDOWS_SERVER_2016_SWEDISH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_TURKISH_FULL_BASE = "WINDOWS_SERVER_2016_TURKISH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_CORE_SQL_2012_SP4_STANDARD = "WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_CORE_SQL_2012_SP4_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_LANGUAGE_PACKS_64BIT_SQL_2008_R2_SP3_STANDARD = "WINDOWS_SERVER_2008_R2_SP1_LANGUAGE_PACKS_64BIT_SQL_2008_R2_SP3_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_CZECH_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_CZECH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_TURKISH_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_TURKISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_DUTCH_FULL_BASE = "WINDOWS_SERVER_2016_DUTCH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP2_EXPRESS = "WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP2_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2017_ENTERPRISE = "WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2017_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_HUNGARIAN_FULL_BASE = "WINDOWS_SERVER_2016_HUNGARIAN_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_KOREAN_FULL_SQL_2016_SP1_STANDARD = "WINDOWS_SERVER_2016_KOREAN_FULL_SQL_2016_SP1_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_SPANISH_FULL_BASE = "WINDOWS_SERVER_2019_SPANISH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2003_R2_SP2_ENGLISH_64BIT_BASE = "WINDOWS_SERVER_2003_R2_SP2_ENGLISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_BASE = "WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_LANGUAGE_PACKS_64BIT_SQL_2008_R2_SP3_EXPRESS = "WINDOWS_SERVER_2008_R2_SP1_LANGUAGE_PACKS_64BIT_SQL_2008_R2_SP3_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_SP2_PORTUGESE_BRAZIL_64BIT_BASE = "WINDOWS_SERVER_2012_SP2_PORTUGESE_BRAZIL_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP1_WEB = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP1_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2014_SP3_EXPRESS = "WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2014_SP3_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP2_ENTERPRISE = "WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP2_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_FULL_CONTAINERSLATEST = "WINDOWS_SERVER_2019_ENGLISH_FULL_CONTAINERSLATEST"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2017_ENTERPRISE = "WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2017_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_1709_ENGLISH_CORE_CONTAINERSLATEST = "WINDOWS_SERVER_1709_ENGLISH_CORE_CONTAINERSLATEST"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_1803_ENGLISH_CORE_BASE = "WINDOWS_SERVER_1803_ENGLISH_CORE_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2012_SP4_WEB = "WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2012_SP4_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_JAPANESE_64BIT_BASE = "WINDOWS_SERVER_2008_R2_SP1_JAPANESE_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_SP2_ENGLISH_64BIT_SQL_2008_SP4_STANDARD = "WINDOWS_SERVER_2008_SP2_ENGLISH_64BIT_SQL_2008_SP4_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_PORTUGESE_BRAZIL_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_PORTUGESE_BRAZIL_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP1_WEB = "WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP1_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_P3 = "WINDOWS_SERVER_2016_ENGLISH_P3"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP1_ENTERPRISE = "WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP1_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2003_R2_SP2_LANGUAGE_PACKS_64BIT_BASE = "WINDOWS_SERVER_2003_R2_SP2_LANGUAGE_PACKS_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_CHINESE_TRADITIONAL_HONG_KONG_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_CHINESE_TRADITIONAL_HONG_KONG_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP3_EXPRESS = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP3_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP2_ENTERPRISE = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP2_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_CHINESE_SIMPLIFIED_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_CHINESE_SIMPLIFIED_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2012_SP4_WEB = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2012_SP4_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2014_SP3_WEB = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2014_SP3_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_JAPANESE_FULL_BASE = "WINDOWS_SERVER_2016_JAPANESE_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP1_EXPRESS = "WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP1_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_1803_ENGLISH_CORE_CONTAINERSLATEST = "WINDOWS_SERVER_1803_ENGLISH_CORE_CONTAINERSLATEST"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_JAPANESE_64BIT_SQL_2012_SP4_STANDARD = "WINDOWS_SERVER_2008_R2_SP1_JAPANESE_64BIT_SQL_2012_SP4_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_CORE = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_CORE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP2_WEB = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP2_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP3_ENTERPRISE = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2014_SP3_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP2_STANDARD = "WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP2_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_2014_SP3_WEB = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_2014_SP3_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_SWEDISH_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_SWEDISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_CHINESE_SIMPLIFIED_FULL_BASE = "WINDOWS_SERVER_2016_CHINESE_SIMPLIFIED_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_POLISH_FULL_BASE = "WINDOWS_SERVER_2019_POLISH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_JAPANESE_64BIT_SQL_2008_R2_SP3_WEB = "WINDOWS_SERVER_2008_R2_SP1_JAPANESE_64BIT_SQL_2008_R2_SP3_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_PORTUGESE_BRAZIL_64BIT_BASE = "WINDOWS_SERVER_2008_R2_SP1_PORTUGESE_BRAZIL_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP1_ENTERPRISE = "WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2016_SP1_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2016_SP2_EXPRESS = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2016_SP2_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2014_SP3_EXPRESS = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2014_SP3_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2014_SP2_STANDARD = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2014_SP2_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_CORE_BASE = "WINDOWS_SERVER_2016_ENGLISH_CORE_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_BASE = "WINDOWS_SERVER_2016_ENGLISH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2017_WEB = "WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2017_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_GERMAN_FULL_BASE = "WINDOWS_SERVER_2019_GERMAN_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2003_R2_SP2_ENGLISH_64BIT_SQL_2005_SP4_STANDARD = "WINDOWS_SERVER_2003_R2_SP2_ENGLISH_64BIT_SQL_2005_SP4_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2012_SP4_ENTERPRISE = "WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2012_SP4_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_JAPANESE_64BIT_SQL_2008_R2_SP3_EXPRESS = "WINDOWS_SERVER_2008_R2_SP1_JAPANESE_64BIT_SQL_2008_R2_SP3_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP1_ENTERPRISE = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP1_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2014_SP2_WEB = "WINDOWS_SERVER_2012_RTM_ENGLISH_64BIT_SQL_2014_SP2_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2008_R2_SP3_EXPRESS = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2008_R2_SP3_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_FRENCH_FULL_BASE = "WINDOWS_SERVER_2016_FRENCH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP2_ENTERPRISE = "WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP2_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_CZECH_FULL_BASE = "WINDOWS_SERVER_2019_CZECH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_1809_ENGLISH_CORE_BASE = "WINDOWS_SERVER_1809_ENGLISH_CORE_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_1809_ENGLISH_CORE_CONTAINERSLATEST = "WINDOWS_SERVER_1809_ENGLISH_CORE_CONTAINERSLATEST"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2003_R2_SP2_LANGUAGE_PACKS_64BIT_SQL_2005_SP4_EXPRESS = "WINDOWS_SERVER_2003_R2_SP2_LANGUAGE_PACKS_64BIT_SQL_2005_SP4_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_TURKISH_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_TURKISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2012_SP4_WEB = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2012_SP4_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_POLISH_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_POLISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_SPANISH_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_SPANISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP1_ENTERPRISE = "WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP1_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP2_EXPRESS = "WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP2_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2016_SP2_ENTERPRISE = "WINDOWS_SERVER_2019_ENGLISH_FULL_SQL_2016_SP2_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_1709_ENGLISH_CORE_BASE = "WINDOWS_SERVER_1709_ENGLISH_CORE_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_ENGLISH_61BIT_SQL_2012_RTM_SP2_ENTERPRISE = "WINDOWS_SERVER_2008_R2_SP1_ENGLISH_61BIT_SQL_2012_RTM_SP2_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2012_SP4_STANDARD = "WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2012_SP4_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_SP2_PORTUGESE_BRAZIL_32BIT_BASE = "WINDOWS_SERVER_2008_SP2_PORTUGESE_BRAZIL_32BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2014_SP2_STANDARD = "WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2014_SP2_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2012_SP4_EXPRESS = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2012_SP4_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_PORTUGESE_PORTUGAL_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_PORTUGESE_PORTUGAL_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_CZECH_FULL_BASE = "WINDOWS_SERVER_2016_CZECH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP1_STANDARD = "WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP1_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_DUTCH_FULL_BASE = "WINDOWS_SERVER_2019_DUTCH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_CORE = "WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_CORE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP2_WEB = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_SQL_2016_SP2_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_KOREAN_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_KOREAN_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_DUTCH_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_DUTCH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_64BIT_SQL_2012_SP4_ENTERPRISE = "WINDOWS_SERVER_2016_ENGLISH_64BIT_SQL_2012_SP4_ENTERPRISE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP1_STANDARD = "WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP1_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP2_EXPRESS = "WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP2_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP2_WEB = "WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP2_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2017_STANDARD = "WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2017_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_PORTUGESE_BRAZIL_FULL_BASE = "WINDOWS_SERVER_2019_PORTUGESE_BRAZIL_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2008_R2_SP3_STANDARD = "WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SQL_2008_R2_SP3_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SHAREPOINT_2010_SP2_FOUNDATION = "WINDOWS_SERVER_2008_R2_SP1_ENGLISH_64BIT_SHAREPOINT_2010_SP2_FOUNDATION"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_P3 = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_P3"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2014_SP3_STANDARD = "WINDOWS_SERVER_2012_R2_RTM_JAPANESE_64BIT_SQL_2014_SP3_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_SPANISH_64BIT_BASE = "WINDOWS_SERVER_2012_R2_RTM_SPANISH_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2014_SP3_EXPRESS = "WINDOWS_SERVER_2012_RTM_JAPANESE_64BIT_SQL_2014_SP3_EXPRESS"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP2_STANDARD = "WINDOWS_SERVER_2016_ENGLISH_CORE_SQL_2016_SP2_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP2_STANDARD = "WINDOWS_SERVER_2016_JAPANESE_FULL_SQL_2016_SP2_STANDARD"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_PORTUGESE_PORTUGAL_FULL_BASE = "WINDOWS_SERVER_2019_PORTUGESE_PORTUGAL_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2019_SWEDISH_FULL_BASE = "WINDOWS_SERVER_2019_SWEDISH_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_HYPERV = "WINDOWS_SERVER_2012_R2_RTM_ENGLISH_64BIT_HYPERV"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_KOREAN_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_KOREAN_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2012_RTM_RUSSIAN_64BIT_BASE = "WINDOWS_SERVER_2012_RTM_RUSSIAN_64BIT_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_CHINESE_TRADITIONAL_FULL_BASE = "WINDOWS_SERVER_2016_CHINESE_TRADITIONAL_FULL_BASE"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP2_WEB = "WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2016_SP2_WEB"
    """
    Stability:
        experimental
    """
    WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2017_EXPRESS = "WINDOWS_SERVER_2016_ENGLISH_FULL_SQL_2017_EXPRESS"
    """
    Stability:
        experimental
    """

__all__ = ["AmazonLinuxEdition", "AmazonLinuxGeneration", "AmazonLinuxImage", "AmazonLinuxImageProps", "AmazonLinuxStorage", "AmazonLinuxVirt", "CfnCapacityReservation", "CfnCapacityReservationProps", "CfnClientVpnAuthorizationRule", "CfnClientVpnAuthorizationRuleProps", "CfnClientVpnEndpoint", "CfnClientVpnEndpointProps", "CfnClientVpnRoute", "CfnClientVpnRouteProps", "CfnClientVpnTargetNetworkAssociation", "CfnClientVpnTargetNetworkAssociationProps", "CfnCustomerGateway", "CfnCustomerGatewayProps", "CfnDHCPOptions", "CfnDHCPOptionsProps", "CfnEC2Fleet", "CfnEC2FleetProps", "CfnEIP", "CfnEIPAssociation", "CfnEIPAssociationProps", "CfnEIPProps", "CfnEgressOnlyInternetGateway", "CfnEgressOnlyInternetGatewayProps", "CfnFlowLog", "CfnFlowLogProps", "CfnHost", "CfnHostProps", "CfnInstance", "CfnInstanceProps", "CfnInternetGateway", "CfnInternetGatewayProps", "CfnLaunchTemplate", "CfnLaunchTemplateProps", "CfnNatGateway", "CfnNatGatewayProps", "CfnNetworkAcl", "CfnNetworkAclEntry", "CfnNetworkAclEntryProps", "CfnNetworkAclProps", "CfnNetworkInterface", "CfnNetworkInterfaceAttachment", "CfnNetworkInterfaceAttachmentProps", "CfnNetworkInterfacePermission", "CfnNetworkInterfacePermissionProps", "CfnNetworkInterfaceProps", "CfnPlacementGroup", "CfnPlacementGroupProps", "CfnRoute", "CfnRouteProps", "CfnRouteTable", "CfnRouteTableProps", "CfnSecurityGroup", "CfnSecurityGroupEgress", "CfnSecurityGroupEgressProps", "CfnSecurityGroupIngress", "CfnSecurityGroupIngressProps", "CfnSecurityGroupProps", "CfnSpotFleet", "CfnSpotFleetProps", "CfnSubnet", "CfnSubnetCidrBlock", "CfnSubnetCidrBlockProps", "CfnSubnetNetworkAclAssociation", "CfnSubnetNetworkAclAssociationProps", "CfnSubnetProps", "CfnSubnetRouteTableAssociation", "CfnSubnetRouteTableAssociationProps", "CfnTransitGateway", "CfnTransitGatewayAttachment", "CfnTransitGatewayAttachmentProps", "CfnTransitGatewayProps", "CfnTransitGatewayRoute", "CfnTransitGatewayRouteProps", "CfnTransitGatewayRouteTable", "CfnTransitGatewayRouteTableAssociation", "CfnTransitGatewayRouteTableAssociationProps", "CfnTransitGatewayRouteTablePropagation", "CfnTransitGatewayRouteTablePropagationProps", "CfnTransitGatewayRouteTableProps", "CfnVPC", "CfnVPCCidrBlock", "CfnVPCCidrBlockProps", "CfnVPCDHCPOptionsAssociation", "CfnVPCDHCPOptionsAssociationProps", "CfnVPCEndpoint", "CfnVPCEndpointConnectionNotification", "CfnVPCEndpointConnectionNotificationProps", "CfnVPCEndpointProps", "CfnVPCEndpointService", "CfnVPCEndpointServicePermissions", "CfnVPCEndpointServicePermissionsProps", "CfnVPCEndpointServiceProps", "CfnVPCGatewayAttachment", "CfnVPCGatewayAttachmentProps", "CfnVPCPeeringConnection", "CfnVPCPeeringConnectionProps", "CfnVPCProps", "CfnVPNConnection", "CfnVPNConnectionProps", "CfnVPNConnectionRoute", "CfnVPNConnectionRouteProps", "CfnVPNGateway", "CfnVPNGatewayProps", "CfnVPNGatewayRoutePropagation", "CfnVPNGatewayRoutePropagationProps", "CfnVolume", "CfnVolumeAttachment", "CfnVolumeAttachmentProps", "CfnVolumeProps", "ConnectionRule", "Connections", "ConnectionsProps", "DefaultInstanceTenancy", "GatewayVpcEndpoint", "GatewayVpcEndpointAwsService", "GatewayVpcEndpointOptions", "GatewayVpcEndpointProps", "GenericLinuxImage", "GenericLinuxImageProps", "IConnectable", "IGatewayVpcEndpoint", "IGatewayVpcEndpointService", "IInterfaceVpcEndpoint", "IInterfaceVpcEndpointService", "IMachineImage", "IPeer", "IPrivateSubnet", "IPublicSubnet", "IRouteTable", "ISecurityGroup", "ISubnet", "IVpc", "IVpcEndpoint", "IVpnConnection", "InstanceClass", "InstanceSize", "InstanceType", "InterfaceVpcEndpoint", "InterfaceVpcEndpointAttributes", "InterfaceVpcEndpointAwsService", "InterfaceVpcEndpointOptions", "InterfaceVpcEndpointProps", "LinuxUserDataOptions", "MachineImageConfig", "OperatingSystemType", "Peer", "Port", "PortProps", "PrivateSubnet", "PrivateSubnetAttributes", "PrivateSubnetProps", "Protocol", "PublicSubnet", "PublicSubnetAttributes", "PublicSubnetProps", "SecurityGroup", "SecurityGroupProps", "SelectedSubnets", "Subnet", "SubnetAttributes", "SubnetConfiguration", "SubnetProps", "SubnetSelection", "SubnetType", "UserData", "Vpc", "VpcAttributes", "VpcEndpoint", "VpcEndpointType", "VpcLookupOptions", "VpcProps", "VpnConnection", "VpnConnectionOptions", "VpnConnectionProps", "VpnConnectionType", "VpnTunnelOption", "WindowsImage", "WindowsImageProps", "WindowsVersion", "__jsii_assembly__"]

publication.publish()
