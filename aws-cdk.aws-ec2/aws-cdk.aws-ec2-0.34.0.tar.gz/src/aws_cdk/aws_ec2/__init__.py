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
import aws_cdk.cdk
import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-ec2", "0.34.0", __name__, "aws-ec2@0.34.0.jsii.tgz")
@jsii.enum(jsii_type="@aws-cdk/aws-ec2.AmazonLinuxEdition")
class AmazonLinuxEdition(enum.Enum):
    """Amazon Linux edition.

    Stability:
        experimental
    """
    Standard = "Standard"
    """Standard edition.

    Stability:
        experimental
    """
    Minimal = "Minimal"
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
    AmazonLinux = "AmazonLinux"
    """Amazon Linux.

    Stability:
        experimental
    """
    AmazonLinux2 = "AmazonLinux2"
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
    GeneralPurpose = "GeneralPurpose"
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

class CfnCapacityReservation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnCapacityReservation"):
    """A CloudFormation ``AWS::EC2::CapacityReservation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::CapacityReservation
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, availability_zone: str, instance_count: typing.Union[jsii.Number, aws_cdk.cdk.Token], instance_platform: str, instance_type: str, ebs_optimized: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, end_date: typing.Optional[str]=None, end_date_type: typing.Optional[str]=None, ephemeral_storage: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, instance_match_criteria: typing.Optional[str]=None, tag_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "TagSpecificationProperty"]]]]]=None, tenancy: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::CapacityReservation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            availabilityZone: ``AWS::EC2::CapacityReservation.AvailabilityZone``.
            instanceCount: ``AWS::EC2::CapacityReservation.InstanceCount``.
            instancePlatform: ``AWS::EC2::CapacityReservation.InstancePlatform``.
            instanceType: ``AWS::EC2::CapacityReservation.InstanceType``.
            ebsOptimized: ``AWS::EC2::CapacityReservation.EbsOptimized``.
            endDate: ``AWS::EC2::CapacityReservation.EndDate``.
            endDateType: ``AWS::EC2::CapacityReservation.EndDateType``.
            ephemeralStorage: ``AWS::EC2::CapacityReservation.EphemeralStorage``.
            instanceMatchCriteria: ``AWS::EC2::CapacityReservation.InstanceMatchCriteria``.
            tagSpecifications: ``AWS::EC2::CapacityReservation.TagSpecifications``.
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
    @jsii.member(jsii_name="capacityReservationAvailabilityZone")
    def capacity_reservation_availability_zone(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            AvailabilityZone
        """
        return jsii.get(self, "capacityReservationAvailabilityZone")

    @property
    @jsii.member(jsii_name="capacityReservationAvailableInstanceCount")
    def capacity_reservation_available_instance_count(self) -> aws_cdk.cdk.Token:
        """
        Stability:
            experimental
        cloudformationAttribute:
            AvailableInstanceCount
        """
        return jsii.get(self, "capacityReservationAvailableInstanceCount")

    @property
    @jsii.member(jsii_name="capacityReservationId")
    def capacity_reservation_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "capacityReservationId")

    @property
    @jsii.member(jsii_name="capacityReservationInstanceType")
    def capacity_reservation_instance_type(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            InstanceType
        """
        return jsii.get(self, "capacityReservationInstanceType")

    @property
    @jsii.member(jsii_name="capacityReservationTenancy")
    def capacity_reservation_tenancy(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Tenancy
        """
        return jsii.get(self, "capacityReservationTenancy")

    @property
    @jsii.member(jsii_name="capacityReservationTotalInstanceCount")
    def capacity_reservation_total_instance_count(self) -> aws_cdk.cdk.Token:
        """
        Stability:
            experimental
        cloudformationAttribute:
            TotalInstanceCount
        """
        return jsii.get(self, "capacityReservationTotalInstanceCount")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnCapacityReservationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnCapacityReservation.TagSpecificationProperty", jsii_struct_bases=[])
    class TagSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-capacityreservation-tagspecification.html
        Stability:
            experimental
        """
        resourceType: str
        """``CfnCapacityReservation.TagSpecificationProperty.ResourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-capacityreservation-tagspecification.html#cfn-ec2-capacityreservation-tagspecification-resourcetype
        Stability:
            experimental
        """

        tags: typing.List[aws_cdk.cdk.CfnTag]
        """``CfnCapacityReservation.TagSpecificationProperty.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-capacityreservation-tagspecification.html#cfn-ec2-capacityreservation-tagspecification-tags
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnCapacityReservationProps(jsii.compat.TypedDict, total=False):
    ebsOptimized: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::CapacityReservation.EbsOptimized``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-ebsoptimized
    Stability:
        experimental
    """
    endDate: str
    """``AWS::EC2::CapacityReservation.EndDate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-enddate
    Stability:
        experimental
    """
    endDateType: str
    """``AWS::EC2::CapacityReservation.EndDateType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-enddatetype
    Stability:
        experimental
    """
    ephemeralStorage: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::CapacityReservation.EphemeralStorage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-ephemeralstorage
    Stability:
        experimental
    """
    instanceMatchCriteria: str
    """``AWS::EC2::CapacityReservation.InstanceMatchCriteria``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-instancematchcriteria
    Stability:
        experimental
    """
    tagSpecifications: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnCapacityReservation.TagSpecificationProperty"]]]
    """``AWS::EC2::CapacityReservation.TagSpecifications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-tagspecifications
    Stability:
        experimental
    """
    tenancy: str
    """``AWS::EC2::CapacityReservation.Tenancy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-tenancy
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnCapacityReservationProps", jsii_struct_bases=[_CfnCapacityReservationProps])
class CfnCapacityReservationProps(_CfnCapacityReservationProps):
    """Properties for defining a ``AWS::EC2::CapacityReservation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html
    Stability:
        experimental
    """
    availabilityZone: str
    """``AWS::EC2::CapacityReservation.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-availabilityzone
    Stability:
        experimental
    """

    instanceCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::CapacityReservation.InstanceCount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-instancecount
    Stability:
        experimental
    """

    instancePlatform: str
    """``AWS::EC2::CapacityReservation.InstancePlatform``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-instanceplatform
    Stability:
        experimental
    """

    instanceType: str
    """``AWS::EC2::CapacityReservation.InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-capacityreservation.html#cfn-ec2-capacityreservation-instancetype
    Stability:
        experimental
    """

class CfnCustomerGateway(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnCustomerGateway"):
    """A CloudFormation ``AWS::EC2::CustomerGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::CustomerGateway
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, bgp_asn: typing.Union[jsii.Number, aws_cdk.cdk.Token], ip_address: str, type: str, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::CustomerGateway``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            bgpAsn: ``AWS::EC2::CustomerGateway.BgpAsn``.
            ipAddress: ``AWS::EC2::CustomerGateway.IpAddress``.
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
    @jsii.member(jsii_name="customerGatewayName")
    def customer_gateway_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "customerGatewayName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnCustomerGatewayProps":
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
class _CfnCustomerGatewayProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::CustomerGateway.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html#cfn-ec2-customergateway-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnCustomerGatewayProps", jsii_struct_bases=[_CfnCustomerGatewayProps])
class CfnCustomerGatewayProps(_CfnCustomerGatewayProps):
    """Properties for defining a ``AWS::EC2::CustomerGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html
    Stability:
        experimental
    """
    bgpAsn: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::CustomerGateway.BgpAsn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html#cfn-ec2-customergateway-bgpasn
    Stability:
        experimental
    """

    ipAddress: str
    """``AWS::EC2::CustomerGateway.IpAddress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html#cfn-ec2-customergateway-ipaddress
    Stability:
        experimental
    """

    type: str
    """``AWS::EC2::CustomerGateway.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-customer-gateway.html#cfn-ec2-customergateway-type
    Stability:
        experimental
    """

class CfnDHCPOptions(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnDHCPOptions"):
    """A CloudFormation ``AWS::EC2::DHCPOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::DHCPOptions
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, domain_name: typing.Optional[str]=None, domain_name_servers: typing.Optional[typing.List[str]]=None, netbios_name_servers: typing.Optional[typing.List[str]]=None, netbios_node_type: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, ntp_servers: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::DHCPOptions``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            domainName: ``AWS::EC2::DHCPOptions.DomainName``.
            domainNameServers: ``AWS::EC2::DHCPOptions.DomainNameServers``.
            netbiosNameServers: ``AWS::EC2::DHCPOptions.NetbiosNameServers``.
            netbiosNodeType: ``AWS::EC2::DHCPOptions.NetbiosNodeType``.
            ntpServers: ``AWS::EC2::DHCPOptions.NtpServers``.
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
    @jsii.member(jsii_name="dhcpOptionsName")
    def dhcp_options_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "dhcpOptionsName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDHCPOptionsProps":
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


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnDHCPOptionsProps", jsii_struct_bases=[])
class CfnDHCPOptionsProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::DHCPOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html
    Stability:
        experimental
    """
    domainName: str
    """``AWS::EC2::DHCPOptions.DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-domainname
    Stability:
        experimental
    """

    domainNameServers: typing.List[str]
    """``AWS::EC2::DHCPOptions.DomainNameServers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-domainnameservers
    Stability:
        experimental
    """

    netbiosNameServers: typing.List[str]
    """``AWS::EC2::DHCPOptions.NetbiosNameServers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-netbiosnameservers
    Stability:
        experimental
    """

    netbiosNodeType: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::DHCPOptions.NetbiosNodeType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-netbiosnodetype
    Stability:
        experimental
    """

    ntpServers: typing.List[str]
    """``AWS::EC2::DHCPOptions.NtpServers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-ntpservers
    Stability:
        experimental
    """

    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::DHCPOptions.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-dhcp-options.html#cfn-ec2-dhcpoptions-tags
    Stability:
        experimental
    """

class CfnEC2Fleet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet"):
    """A CloudFormation ``AWS::EC2::EC2Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::EC2Fleet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, launch_template_configs: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "FleetLaunchTemplateConfigRequestProperty"]]], target_capacity_specification: typing.Union[aws_cdk.cdk.Token, "TargetCapacitySpecificationRequestProperty"], excess_capacity_termination_policy: typing.Optional[str]=None, on_demand_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["OnDemandOptionsRequestProperty"]]]=None, replace_unhealthy_instances: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, spot_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["SpotOptionsRequestProperty"]]]=None, tag_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "TagSpecificationProperty"]]]]]=None, terminate_instances_with_expiration: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, type: typing.Optional[str]=None, valid_from: typing.Optional[str]=None, valid_until: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::EC2Fleet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            launchTemplateConfigs: ``AWS::EC2::EC2Fleet.LaunchTemplateConfigs``.
            targetCapacitySpecification: ``AWS::EC2::EC2Fleet.TargetCapacitySpecification``.
            excessCapacityTerminationPolicy: ``AWS::EC2::EC2Fleet.ExcessCapacityTerminationPolicy``.
            onDemandOptions: ``AWS::EC2::EC2Fleet.OnDemandOptions``.
            replaceUnhealthyInstances: ``AWS::EC2::EC2Fleet.ReplaceUnhealthyInstances``.
            spotOptions: ``AWS::EC2::EC2Fleet.SpotOptions``.
            tagSpecifications: ``AWS::EC2::EC2Fleet.TagSpecifications``.
            terminateInstancesWithExpiration: ``AWS::EC2::EC2Fleet.TerminateInstancesWithExpiration``.
            type: ``AWS::EC2::EC2Fleet.Type``.
            validFrom: ``AWS::EC2::EC2Fleet.ValidFrom``.
            validUntil: ``AWS::EC2::EC2Fleet.ValidUntil``.

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
    @jsii.member(jsii_name="ec2FleetId")
    def ec2_fleet_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "ec2FleetId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnEC2FleetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.FleetLaunchTemplateConfigRequestProperty", jsii_struct_bases=[])
    class FleetLaunchTemplateConfigRequestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateconfigrequest.html
        Stability:
            experimental
        """
        launchTemplateSpecification: typing.Union[aws_cdk.cdk.Token, "CfnEC2Fleet.FleetLaunchTemplateSpecificationRequestProperty"]
        """``CfnEC2Fleet.FleetLaunchTemplateConfigRequestProperty.LaunchTemplateSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateconfigrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateconfigrequest-launchtemplatespecification
        Stability:
            experimental
        """

        overrides: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty"]]]
        """``CfnEC2Fleet.FleetLaunchTemplateConfigRequestProperty.Overrides``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateconfigrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateconfigrequest-overrides
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty", jsii_struct_bases=[])
    class FleetLaunchTemplateOverridesRequestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html
        Stability:
            experimental
        """
        availabilityZone: str
        """``CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest-availabilityzone
        Stability:
            experimental
        """

        instanceType: str
        """``CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest-instancetype
        Stability:
            experimental
        """

        maxPrice: str
        """``CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty.MaxPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest-maxprice
        Stability:
            experimental
        """

        priority: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty.Priority``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest-priority
        Stability:
            experimental
        """

        subnetId: str
        """``CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest-subnetid
        Stability:
            experimental
        """

        weightedCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnEC2Fleet.FleetLaunchTemplateOverridesRequestProperty.WeightedCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplateoverridesrequest-weightedcapacity
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.FleetLaunchTemplateSpecificationRequestProperty", jsii_struct_bases=[])
    class FleetLaunchTemplateSpecificationRequestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest.html
        Stability:
            experimental
        """
        launchTemplateId: str
        """``CfnEC2Fleet.FleetLaunchTemplateSpecificationRequestProperty.LaunchTemplateId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest-launchtemplateid
        Stability:
            experimental
        """

        launchTemplateName: str
        """``CfnEC2Fleet.FleetLaunchTemplateSpecificationRequestProperty.LaunchTemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest-launchtemplatename
        Stability:
            experimental
        """

        version: str
        """``CfnEC2Fleet.FleetLaunchTemplateSpecificationRequestProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest.html#cfn-ec2-ec2fleet-fleetlaunchtemplatespecificationrequest-version
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.OnDemandOptionsRequestProperty", jsii_struct_bases=[])
    class OnDemandOptionsRequestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-ondemandoptionsrequest.html
        Stability:
            experimental
        """
        allocationStrategy: str
        """``CfnEC2Fleet.OnDemandOptionsRequestProperty.AllocationStrategy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-ondemandoptionsrequest.html#cfn-ec2-ec2fleet-ondemandoptionsrequest-allocationstrategy
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.SpotOptionsRequestProperty", jsii_struct_bases=[])
    class SpotOptionsRequestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-spotoptionsrequest.html
        Stability:
            experimental
        """
        allocationStrategy: str
        """``CfnEC2Fleet.SpotOptionsRequestProperty.AllocationStrategy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-spotoptionsrequest.html#cfn-ec2-ec2fleet-spotoptionsrequest-allocationstrategy
        Stability:
            experimental
        """

        instanceInterruptionBehavior: str
        """``CfnEC2Fleet.SpotOptionsRequestProperty.InstanceInterruptionBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-spotoptionsrequest.html#cfn-ec2-ec2fleet-spotoptionsrequest-instanceinterruptionbehavior
        Stability:
            experimental
        """

        instancePoolsToUseCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnEC2Fleet.SpotOptionsRequestProperty.InstancePoolsToUseCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-spotoptionsrequest.html#cfn-ec2-ec2fleet-spotoptionsrequest-instancepoolstousecount
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.TagRequestProperty", jsii_struct_bases=[])
    class TagRequestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-tagrequest.html
        Stability:
            experimental
        """
        key: str
        """``CfnEC2Fleet.TagRequestProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-tagrequest.html#cfn-ec2-ec2fleet-tagrequest-key
        Stability:
            experimental
        """

        value: str
        """``CfnEC2Fleet.TagRequestProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-tagrequest.html#cfn-ec2-ec2fleet-tagrequest-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.TagSpecificationProperty", jsii_struct_bases=[])
    class TagSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-tagspecification.html
        Stability:
            experimental
        """
        resourceType: str
        """``CfnEC2Fleet.TagSpecificationProperty.ResourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-tagspecification.html#cfn-ec2-ec2fleet-tagspecification-resourcetype
        Stability:
            experimental
        """

        tags: typing.List["CfnEC2Fleet.TagRequestProperty"]
        """``CfnEC2Fleet.TagSpecificationProperty.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-tagspecification.html#cfn-ec2-ec2fleet-tagspecification-tags
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _TargetCapacitySpecificationRequestProperty(jsii.compat.TypedDict, total=False):
        defaultTargetCapacityType: str
        """``CfnEC2Fleet.TargetCapacitySpecificationRequestProperty.DefaultTargetCapacityType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-targetcapacityspecificationrequest.html#cfn-ec2-ec2fleet-targetcapacityspecificationrequest-defaulttargetcapacitytype
        Stability:
            experimental
        """
        onDemandTargetCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnEC2Fleet.TargetCapacitySpecificationRequestProperty.OnDemandTargetCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-targetcapacityspecificationrequest.html#cfn-ec2-ec2fleet-targetcapacityspecificationrequest-ondemandtargetcapacity
        Stability:
            experimental
        """
        spotTargetCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnEC2Fleet.TargetCapacitySpecificationRequestProperty.SpotTargetCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-targetcapacityspecificationrequest.html#cfn-ec2-ec2fleet-targetcapacityspecificationrequest-spottargetcapacity
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2Fleet.TargetCapacitySpecificationRequestProperty", jsii_struct_bases=[_TargetCapacitySpecificationRequestProperty])
    class TargetCapacitySpecificationRequestProperty(_TargetCapacitySpecificationRequestProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-targetcapacityspecificationrequest.html
        Stability:
            experimental
        """
        totalTargetCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnEC2Fleet.TargetCapacitySpecificationRequestProperty.TotalTargetCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ec2fleet-targetcapacityspecificationrequest.html#cfn-ec2-ec2fleet-targetcapacityspecificationrequest-totaltargetcapacity
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEC2FleetProps(jsii.compat.TypedDict, total=False):
    excessCapacityTerminationPolicy: str
    """``AWS::EC2::EC2Fleet.ExcessCapacityTerminationPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-excesscapacityterminationpolicy
    Stability:
        experimental
    """
    onDemandOptions: typing.Union[aws_cdk.cdk.Token, "CfnEC2Fleet.OnDemandOptionsRequestProperty"]
    """``AWS::EC2::EC2Fleet.OnDemandOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-ondemandoptions
    Stability:
        experimental
    """
    replaceUnhealthyInstances: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::EC2Fleet.ReplaceUnhealthyInstances``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-replaceunhealthyinstances
    Stability:
        experimental
    """
    spotOptions: typing.Union[aws_cdk.cdk.Token, "CfnEC2Fleet.SpotOptionsRequestProperty"]
    """``AWS::EC2::EC2Fleet.SpotOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-spotoptions
    Stability:
        experimental
    """
    tagSpecifications: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnEC2Fleet.TagSpecificationProperty"]]]
    """``AWS::EC2::EC2Fleet.TagSpecifications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-tagspecifications
    Stability:
        experimental
    """
    terminateInstancesWithExpiration: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::EC2Fleet.TerminateInstancesWithExpiration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-terminateinstanceswithexpiration
    Stability:
        experimental
    """
    type: str
    """``AWS::EC2::EC2Fleet.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-type
    Stability:
        experimental
    """
    validFrom: str
    """``AWS::EC2::EC2Fleet.ValidFrom``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-validfrom
    Stability:
        experimental
    """
    validUntil: str
    """``AWS::EC2::EC2Fleet.ValidUntil``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-validuntil
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEC2FleetProps", jsii_struct_bases=[_CfnEC2FleetProps])
class CfnEC2FleetProps(_CfnEC2FleetProps):
    """Properties for defining a ``AWS::EC2::EC2Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html
    Stability:
        experimental
    """
    launchTemplateConfigs: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnEC2Fleet.FleetLaunchTemplateConfigRequestProperty"]]]
    """``AWS::EC2::EC2Fleet.LaunchTemplateConfigs``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-launchtemplateconfigs
    Stability:
        experimental
    """

    targetCapacitySpecification: typing.Union[aws_cdk.cdk.Token, "CfnEC2Fleet.TargetCapacitySpecificationRequestProperty"]
    """``AWS::EC2::EC2Fleet.TargetCapacitySpecification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html#cfn-ec2-ec2fleet-targetcapacityspecification
    Stability:
        experimental
    """

class CfnEIP(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnEIP"):
    """A CloudFormation ``AWS::EC2::EIP``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::EIP
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, domain: typing.Optional[str]=None, instance_id: typing.Optional[str]=None, public_ipv4_pool: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::EIP``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            domain: ``AWS::EC2::EIP.Domain``.
            instanceId: ``AWS::EC2::EIP.InstanceId``.
            publicIpv4Pool: ``AWS::EC2::EIP.PublicIpv4Pool``.

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
    @jsii.member(jsii_name="eipAllocationId")
    def eip_allocation_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            AllocationId
        """
        return jsii.get(self, "eipAllocationId")

    @property
    @jsii.member(jsii_name="eipIp")
    def eip_ip(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "eipIp")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnEIPProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


class CfnEIPAssociation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnEIPAssociation"):
    """A CloudFormation ``AWS::EC2::EIPAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::EIPAssociation
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, allocation_id: typing.Optional[str]=None, eip: typing.Optional[str]=None, instance_id: typing.Optional[str]=None, network_interface_id: typing.Optional[str]=None, private_ip_address: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::EIPAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            allocationId: ``AWS::EC2::EIPAssociation.AllocationId``.
            eip: ``AWS::EC2::EIPAssociation.EIP``.
            instanceId: ``AWS::EC2::EIPAssociation.InstanceId``.
            networkInterfaceId: ``AWS::EC2::EIPAssociation.NetworkInterfaceId``.
            privateIpAddress: ``AWS::EC2::EIPAssociation.PrivateIpAddress``.

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
    @jsii.member(jsii_name="eipAssociationName")
    def eip_association_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "eipAssociationName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnEIPAssociationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEIPAssociationProps", jsii_struct_bases=[])
class CfnEIPAssociationProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::EIPAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html
    Stability:
        experimental
    """
    allocationId: str
    """``AWS::EC2::EIPAssociation.AllocationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-allocationid
    Stability:
        experimental
    """

    eip: str
    """``AWS::EC2::EIPAssociation.EIP``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-eip
    Stability:
        experimental
    """

    instanceId: str
    """``AWS::EC2::EIPAssociation.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-instanceid
    Stability:
        experimental
    """

    networkInterfaceId: str
    """``AWS::EC2::EIPAssociation.NetworkInterfaceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-networkinterfaceid
    Stability:
        experimental
    """

    privateIpAddress: str
    """``AWS::EC2::EIPAssociation.PrivateIpAddress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip-association.html#cfn-ec2-eipassociation-PrivateIpAddress
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEIPProps", jsii_struct_bases=[])
class CfnEIPProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::EIP``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html
    Stability:
        experimental
    """
    domain: str
    """``AWS::EC2::EIP.Domain``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html#cfn-ec2-eip-domain
    Stability:
        experimental
    """

    instanceId: str
    """``AWS::EC2::EIP.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html#cfn-ec2-eip-instanceid
    Stability:
        experimental
    """

    publicIpv4Pool: str
    """``AWS::EC2::EIP.PublicIpv4Pool``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-eip.html#cfn-ec2-eip-publicipv4pool
    Stability:
        experimental
    """

class CfnEgressOnlyInternetGateway(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnEgressOnlyInternetGateway"):
    """A CloudFormation ``AWS::EC2::EgressOnlyInternetGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-egressonlyinternetgateway.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::EgressOnlyInternetGateway
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc_id: str) -> None:
        """Create a new ``AWS::EC2::EgressOnlyInternetGateway``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            vpcId: ``AWS::EC2::EgressOnlyInternetGateway.VpcId``.

        Stability:
            experimental
        """
        props: CfnEgressOnlyInternetGatewayProps = {"vpcId": vpc_id}

        jsii.create(CfnEgressOnlyInternetGateway, self, [scope, id, props])

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
    @jsii.member(jsii_name="egressOnlyInternetGatewayId")
    def egress_only_internet_gateway_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "egressOnlyInternetGatewayId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnEgressOnlyInternetGatewayProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnEgressOnlyInternetGatewayProps", jsii_struct_bases=[])
class CfnEgressOnlyInternetGatewayProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::EgressOnlyInternetGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-egressonlyinternetgateway.html
    Stability:
        experimental
    """
    vpcId: str
    """``AWS::EC2::EgressOnlyInternetGateway.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-egressonlyinternetgateway.html#cfn-ec2-egressonlyinternetgateway-vpcid
    Stability:
        experimental
    """

class CfnFlowLog(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnFlowLog"):
    """A CloudFormation ``AWS::EC2::FlowLog``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::FlowLog
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, resource_id: str, resource_type: str, traffic_type: str, deliver_logs_permission_arn: typing.Optional[str]=None, log_destination: typing.Optional[str]=None, log_destination_type: typing.Optional[str]=None, log_group_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::FlowLog``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            resourceId: ``AWS::EC2::FlowLog.ResourceId``.
            resourceType: ``AWS::EC2::FlowLog.ResourceType``.
            trafficType: ``AWS::EC2::FlowLog.TrafficType``.
            deliverLogsPermissionArn: ``AWS::EC2::FlowLog.DeliverLogsPermissionArn``.
            logDestination: ``AWS::EC2::FlowLog.LogDestination``.
            logDestinationType: ``AWS::EC2::FlowLog.LogDestinationType``.
            logGroupName: ``AWS::EC2::FlowLog.LogGroupName``.

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
    @jsii.member(jsii_name="flowLogId")
    def flow_log_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "flowLogId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnFlowLogProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnFlowLogProps(jsii.compat.TypedDict, total=False):
    deliverLogsPermissionArn: str
    """``AWS::EC2::FlowLog.DeliverLogsPermissionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-deliverlogspermissionarn
    Stability:
        experimental
    """
    logDestination: str
    """``AWS::EC2::FlowLog.LogDestination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-logdestination
    Stability:
        experimental
    """
    logDestinationType: str
    """``AWS::EC2::FlowLog.LogDestinationType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-logdestinationtype
    Stability:
        experimental
    """
    logGroupName: str
    """``AWS::EC2::FlowLog.LogGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-loggroupname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnFlowLogProps", jsii_struct_bases=[_CfnFlowLogProps])
class CfnFlowLogProps(_CfnFlowLogProps):
    """Properties for defining a ``AWS::EC2::FlowLog``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html
    Stability:
        experimental
    """
    resourceId: str
    """``AWS::EC2::FlowLog.ResourceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-resourceid
    Stability:
        experimental
    """

    resourceType: str
    """``AWS::EC2::FlowLog.ResourceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-resourcetype
    Stability:
        experimental
    """

    trafficType: str
    """``AWS::EC2::FlowLog.TrafficType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-flowlog.html#cfn-ec2-flowlog-traffictype
    Stability:
        experimental
    """

class CfnHost(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnHost"):
    """A CloudFormation ``AWS::EC2::Host``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::Host
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, availability_zone: str, instance_type: str, auto_placement: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::Host``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            availabilityZone: ``AWS::EC2::Host.AvailabilityZone``.
            instanceType: ``AWS::EC2::Host.InstanceType``.
            autoPlacement: ``AWS::EC2::Host.AutoPlacement``.

        Stability:
            experimental
        """
        props: CfnHostProps = {"availabilityZone": availability_zone, "instanceType": instance_type}

        if auto_placement is not None:
            props["autoPlacement"] = auto_placement

        jsii.create(CfnHost, self, [scope, id, props])

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
    @jsii.member(jsii_name="hostId")
    def host_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "hostId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnHostProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnHostProps(jsii.compat.TypedDict, total=False):
    autoPlacement: str
    """``AWS::EC2::Host.AutoPlacement``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html#cfn-ec2-host-autoplacement
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnHostProps", jsii_struct_bases=[_CfnHostProps])
class CfnHostProps(_CfnHostProps):
    """Properties for defining a ``AWS::EC2::Host``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html
    Stability:
        experimental
    """
    availabilityZone: str
    """``AWS::EC2::Host.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html#cfn-ec2-host-availabilityzone
    Stability:
        experimental
    """

    instanceType: str
    """``AWS::EC2::Host.InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-host.html#cfn-ec2-host-instancetype
    Stability:
        experimental
    """

class CfnInstance(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnInstance"):
    """A CloudFormation ``AWS::EC2::Instance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::Instance
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, additional_info: typing.Optional[str]=None, affinity: typing.Optional[str]=None, availability_zone: typing.Optional[str]=None, block_device_mappings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "BlockDeviceMappingProperty"]]]]]=None, credit_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["CreditSpecificationProperty"]]]=None, disable_api_termination: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, ebs_optimized: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, elastic_gpu_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "ElasticGpuSpecificationProperty"]]]]]=None, elastic_inference_accelerators: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "ElasticInferenceAcceleratorProperty"]]]]]=None, host_id: typing.Optional[str]=None, iam_instance_profile: typing.Optional[str]=None, image_id: typing.Optional[str]=None, instance_initiated_shutdown_behavior: typing.Optional[str]=None, instance_type: typing.Optional[str]=None, ipv6_address_count: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, ipv6_addresses: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "InstanceIpv6AddressProperty"]]]]]=None, kernel_id: typing.Optional[str]=None, key_name: typing.Optional[str]=None, launch_template: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["LaunchTemplateSpecificationProperty"]]]=None, license_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "LicenseSpecificationProperty"]]]]]=None, monitoring: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, network_interfaces: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "NetworkInterfaceProperty"]]]]]=None, placement_group_name: typing.Optional[str]=None, private_ip_address: typing.Optional[str]=None, ramdisk_id: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, security_groups: typing.Optional[typing.List[str]]=None, source_dest_check: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, ssm_associations: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "SsmAssociationProperty"]]]]]=None, subnet_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, tenancy: typing.Optional[str]=None, user_data: typing.Optional[str]=None, volumes: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "VolumeProperty"]]]]]=None) -> None:
        """Create a new ``AWS::EC2::Instance``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            additionalInfo: ``AWS::EC2::Instance.AdditionalInfo``.
            affinity: ``AWS::EC2::Instance.Affinity``.
            availabilityZone: ``AWS::EC2::Instance.AvailabilityZone``.
            blockDeviceMappings: ``AWS::EC2::Instance.BlockDeviceMappings``.
            creditSpecification: ``AWS::EC2::Instance.CreditSpecification``.
            disableApiTermination: ``AWS::EC2::Instance.DisableApiTermination``.
            ebsOptimized: ``AWS::EC2::Instance.EbsOptimized``.
            elasticGpuSpecifications: ``AWS::EC2::Instance.ElasticGpuSpecifications``.
            elasticInferenceAccelerators: ``AWS::EC2::Instance.ElasticInferenceAccelerators``.
            hostId: ``AWS::EC2::Instance.HostId``.
            iamInstanceProfile: ``AWS::EC2::Instance.IamInstanceProfile``.
            imageId: ``AWS::EC2::Instance.ImageId``.
            instanceInitiatedShutdownBehavior: ``AWS::EC2::Instance.InstanceInitiatedShutdownBehavior``.
            instanceType: ``AWS::EC2::Instance.InstanceType``.
            ipv6AddressCount: ``AWS::EC2::Instance.Ipv6AddressCount``.
            ipv6Addresses: ``AWS::EC2::Instance.Ipv6Addresses``.
            kernelId: ``AWS::EC2::Instance.KernelId``.
            keyName: ``AWS::EC2::Instance.KeyName``.
            launchTemplate: ``AWS::EC2::Instance.LaunchTemplate``.
            licenseSpecifications: ``AWS::EC2::Instance.LicenseSpecifications``.
            monitoring: ``AWS::EC2::Instance.Monitoring``.
            networkInterfaces: ``AWS::EC2::Instance.NetworkInterfaces``.
            placementGroupName: ``AWS::EC2::Instance.PlacementGroupName``.
            privateIpAddress: ``AWS::EC2::Instance.PrivateIpAddress``.
            ramdiskId: ``AWS::EC2::Instance.RamdiskId``.
            securityGroupIds: ``AWS::EC2::Instance.SecurityGroupIds``.
            securityGroups: ``AWS::EC2::Instance.SecurityGroups``.
            sourceDestCheck: ``AWS::EC2::Instance.SourceDestCheck``.
            ssmAssociations: ``AWS::EC2::Instance.SsmAssociations``.
            subnetId: ``AWS::EC2::Instance.SubnetId``.
            tags: ``AWS::EC2::Instance.Tags``.
            tenancy: ``AWS::EC2::Instance.Tenancy``.
            userData: ``AWS::EC2::Instance.UserData``.
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
    @jsii.member(jsii_name="instanceAvailabilityZone")
    def instance_availability_zone(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            AvailabilityZone
        """
        return jsii.get(self, "instanceAvailabilityZone")

    @property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "instanceId")

    @property
    @jsii.member(jsii_name="instancePrivateDnsName")
    def instance_private_dns_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            PrivateDnsName
        """
        return jsii.get(self, "instancePrivateDnsName")

    @property
    @jsii.member(jsii_name="instancePrivateIp")
    def instance_private_ip(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            PrivateIp
        """
        return jsii.get(self, "instancePrivateIp")

    @property
    @jsii.member(jsii_name="instancePublicDnsName")
    def instance_public_dns_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            PublicDnsName
        """
        return jsii.get(self, "instancePublicDnsName")

    @property
    @jsii.member(jsii_name="instancePublicIp")
    def instance_public_ip(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            PublicIp
        """
        return jsii.get(self, "instancePublicIp")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnInstanceProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.AssociationParameterProperty", jsii_struct_bases=[])
    class AssociationParameterProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-ssmassociations-associationparameters.html
        Stability:
            experimental
        """
        key: str
        """``CfnInstance.AssociationParameterProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-ssmassociations-associationparameters.html#cfn-ec2-instance-ssmassociations-associationparameters-key
        Stability:
            experimental
        """

        value: typing.List[str]
        """``CfnInstance.AssociationParameterProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-ssmassociations-associationparameters.html#cfn-ec2-instance-ssmassociations-associationparameters-value
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _BlockDeviceMappingProperty(jsii.compat.TypedDict, total=False):
        ebs: typing.Union[aws_cdk.cdk.Token, "CfnInstance.EbsProperty"]
        """``CfnInstance.BlockDeviceMappingProperty.Ebs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-mapping.html#cfn-ec2-blockdev-mapping-ebs
        Stability:
            experimental
        """
        noDevice: typing.Union[aws_cdk.cdk.Token, "CfnInstance.NoDeviceProperty"]
        """``CfnInstance.BlockDeviceMappingProperty.NoDevice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-mapping.html#cfn-ec2-blockdev-mapping-nodevice
        Stability:
            experimental
        """
        virtualName: str
        """``CfnInstance.BlockDeviceMappingProperty.VirtualName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-mapping.html#cfn-ec2-blockdev-mapping-virtualname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.BlockDeviceMappingProperty", jsii_struct_bases=[_BlockDeviceMappingProperty])
    class BlockDeviceMappingProperty(_BlockDeviceMappingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-mapping.html
        Stability:
            experimental
        """
        deviceName: str
        """``CfnInstance.BlockDeviceMappingProperty.DeviceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-mapping.html#cfn-ec2-blockdev-mapping-devicename
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.CreditSpecificationProperty", jsii_struct_bases=[])
    class CreditSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-creditspecification.html
        Stability:
            experimental
        """
        cpuCredits: str
        """``CfnInstance.CreditSpecificationProperty.CPUCredits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-creditspecification.html#cfn-ec2-instance-creditspecification-cpucredits
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.EbsProperty", jsii_struct_bases=[])
    class EbsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html
        Stability:
            experimental
        """
        deleteOnTermination: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnInstance.EbsProperty.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html#cfn-ec2-blockdev-template-deleteontermination
        Stability:
            experimental
        """

        encrypted: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnInstance.EbsProperty.Encrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html#cfn-ec2-blockdev-template-encrypted
        Stability:
            experimental
        """

        iops: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnInstance.EbsProperty.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html#cfn-ec2-blockdev-template-iops
        Stability:
            experimental
        """

        snapshotId: str
        """``CfnInstance.EbsProperty.SnapshotId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html#cfn-ec2-blockdev-template-snapshotid
        Stability:
            experimental
        """

        volumeSize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnInstance.EbsProperty.VolumeSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html#cfn-ec2-blockdev-template-volumesize
        Stability:
            experimental
        """

        volumeType: str
        """``CfnInstance.EbsProperty.VolumeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html#cfn-ec2-blockdev-template-volumetype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.ElasticGpuSpecificationProperty", jsii_struct_bases=[])
    class ElasticGpuSpecificationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-elasticgpuspecification.html
        Stability:
            experimental
        """
        type: str
        """``CfnInstance.ElasticGpuSpecificationProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-elasticgpuspecification.html#cfn-ec2-instance-elasticgpuspecification-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.ElasticInferenceAcceleratorProperty", jsii_struct_bases=[])
    class ElasticInferenceAcceleratorProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-elasticinferenceaccelerator.html
        Stability:
            experimental
        """
        type: str
        """``CfnInstance.ElasticInferenceAcceleratorProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-elasticinferenceaccelerator.html#cfn-ec2-instance-elasticinferenceaccelerator-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.InstanceIpv6AddressProperty", jsii_struct_bases=[])
    class InstanceIpv6AddressProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-instanceipv6address.html
        Stability:
            experimental
        """
        ipv6Address: str
        """``CfnInstance.InstanceIpv6AddressProperty.Ipv6Address``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-instanceipv6address.html#cfn-ec2-instance-instanceipv6address-ipv6address
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LaunchTemplateSpecificationProperty(jsii.compat.TypedDict, total=False):
        launchTemplateId: str
        """``CfnInstance.LaunchTemplateSpecificationProperty.LaunchTemplateId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-launchtemplatespecification.html#cfn-ec2-instance-launchtemplatespecification-launchtemplateid
        Stability:
            experimental
        """
        launchTemplateName: str
        """``CfnInstance.LaunchTemplateSpecificationProperty.LaunchTemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-launchtemplatespecification.html#cfn-ec2-instance-launchtemplatespecification-launchtemplatename
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.LaunchTemplateSpecificationProperty", jsii_struct_bases=[_LaunchTemplateSpecificationProperty])
    class LaunchTemplateSpecificationProperty(_LaunchTemplateSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-launchtemplatespecification.html
        Stability:
            experimental
        """
        version: str
        """``CfnInstance.LaunchTemplateSpecificationProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-launchtemplatespecification.html#cfn-ec2-instance-launchtemplatespecification-version
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.LicenseSpecificationProperty", jsii_struct_bases=[])
    class LicenseSpecificationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-licensespecification.html
        Stability:
            experimental
        """
        licenseConfigurationArn: str
        """``CfnInstance.LicenseSpecificationProperty.LicenseConfigurationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-licensespecification.html#cfn-ec2-instance-licensespecification-licenseconfigurationarn
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _NetworkInterfaceProperty(jsii.compat.TypedDict, total=False):
        associatePublicIpAddress: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnInstance.NetworkInterfaceProperty.AssociatePublicIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-associatepubip
        Stability:
            experimental
        """
        deleteOnTermination: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnInstance.NetworkInterfaceProperty.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-delete
        Stability:
            experimental
        """
        description: str
        """``CfnInstance.NetworkInterfaceProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-description
        Stability:
            experimental
        """
        groupSet: typing.List[str]
        """``CfnInstance.NetworkInterfaceProperty.GroupSet``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-groupset
        Stability:
            experimental
        """
        ipv6AddressCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnInstance.NetworkInterfaceProperty.Ipv6AddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#cfn-ec2-instance-networkinterface-ipv6addresscount
        Stability:
            experimental
        """
        ipv6Addresses: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnInstance.InstanceIpv6AddressProperty"]]]
        """``CfnInstance.NetworkInterfaceProperty.Ipv6Addresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#cfn-ec2-instance-networkinterface-ipv6addresses
        Stability:
            experimental
        """
        networkInterfaceId: str
        """``CfnInstance.NetworkInterfaceProperty.NetworkInterfaceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-network-iface
        Stability:
            experimental
        """
        privateIpAddress: str
        """``CfnInstance.NetworkInterfaceProperty.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-privateipaddress
        Stability:
            experimental
        """
        privateIpAddresses: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnInstance.PrivateIpAddressSpecificationProperty"]]]
        """``CfnInstance.NetworkInterfaceProperty.PrivateIpAddresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-privateipaddresses
        Stability:
            experimental
        """
        secondaryPrivateIpAddressCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnInstance.NetworkInterfaceProperty.SecondaryPrivateIpAddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-secondprivateip
        Stability:
            experimental
        """
        subnetId: str
        """``CfnInstance.NetworkInterfaceProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-subnetid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.NetworkInterfaceProperty", jsii_struct_bases=[_NetworkInterfaceProperty])
    class NetworkInterfaceProperty(_NetworkInterfaceProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html
        Stability:
            experimental
        """
        deviceIndex: str
        """``CfnInstance.NetworkInterfaceProperty.DeviceIndex``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-iface-embedded.html#aws-properties-ec2-network-iface-embedded-deviceindex
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.NoDeviceProperty", jsii_struct_bases=[])
    class NoDeviceProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-nodevice.html
        Stability:
            experimental
        """
        pass

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.PrivateIpAddressSpecificationProperty", jsii_struct_bases=[])
    class PrivateIpAddressSpecificationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-interface-privateipspec.html
        Stability:
            experimental
        """
        primary: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnInstance.PrivateIpAddressSpecificationProperty.Primary``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-interface-privateipspec.html#cfn-ec2-networkinterface-privateipspecification-primary
        Stability:
            experimental
        """

        privateIpAddress: str
        """``CfnInstance.PrivateIpAddressSpecificationProperty.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-interface-privateipspec.html#cfn-ec2-networkinterface-privateipspecification-privateipaddress
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SsmAssociationProperty(jsii.compat.TypedDict, total=False):
        associationParameters: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnInstance.AssociationParameterProperty"]]]
        """``CfnInstance.SsmAssociationProperty.AssociationParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-ssmassociations.html#cfn-ec2-instance-ssmassociations-associationparameters
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.SsmAssociationProperty", jsii_struct_bases=[_SsmAssociationProperty])
    class SsmAssociationProperty(_SsmAssociationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-ssmassociations.html
        Stability:
            experimental
        """
        documentName: str
        """``CfnInstance.SsmAssociationProperty.DocumentName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance-ssmassociations.html#cfn-ec2-instance-ssmassociations-documentname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstance.VolumeProperty", jsii_struct_bases=[])
    class VolumeProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-mount-point.html
        Stability:
            experimental
        """
        device: str
        """``CfnInstance.VolumeProperty.Device``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-mount-point.html#cfn-ec2-mountpoint-device
        Stability:
            experimental
        """

        volumeId: str
        """``CfnInstance.VolumeProperty.VolumeId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-mount-point.html#cfn-ec2-mountpoint-volumeid
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInstanceProps", jsii_struct_bases=[])
class CfnInstanceProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::Instance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html
    Stability:
        experimental
    """
    additionalInfo: str
    """``AWS::EC2::Instance.AdditionalInfo``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-additionalinfo
    Stability:
        experimental
    """

    affinity: str
    """``AWS::EC2::Instance.Affinity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-affinity
    Stability:
        experimental
    """

    availabilityZone: str
    """``AWS::EC2::Instance.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-availabilityzone
    Stability:
        experimental
    """

    blockDeviceMappings: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnInstance.BlockDeviceMappingProperty"]]]
    """``AWS::EC2::Instance.BlockDeviceMappings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-blockdevicemappings
    Stability:
        experimental
    """

    creditSpecification: typing.Union[aws_cdk.cdk.Token, "CfnInstance.CreditSpecificationProperty"]
    """``AWS::EC2::Instance.CreditSpecification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-creditspecification
    Stability:
        experimental
    """

    disableApiTermination: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::Instance.DisableApiTermination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-disableapitermination
    Stability:
        experimental
    """

    ebsOptimized: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::Instance.EbsOptimized``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ebsoptimized
    Stability:
        experimental
    """

    elasticGpuSpecifications: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnInstance.ElasticGpuSpecificationProperty"]]]
    """``AWS::EC2::Instance.ElasticGpuSpecifications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-elasticgpuspecifications
    Stability:
        experimental
    """

    elasticInferenceAccelerators: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnInstance.ElasticInferenceAcceleratorProperty"]]]
    """``AWS::EC2::Instance.ElasticInferenceAccelerators``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-elasticinferenceaccelerators
    Stability:
        experimental
    """

    hostId: str
    """``AWS::EC2::Instance.HostId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-hostid
    Stability:
        experimental
    """

    iamInstanceProfile: str
    """``AWS::EC2::Instance.IamInstanceProfile``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-iaminstanceprofile
    Stability:
        experimental
    """

    imageId: str
    """``AWS::EC2::Instance.ImageId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-imageid
    Stability:
        experimental
    """

    instanceInitiatedShutdownBehavior: str
    """``AWS::EC2::Instance.InstanceInitiatedShutdownBehavior``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-instanceinitiatedshutdownbehavior
    Stability:
        experimental
    """

    instanceType: str
    """``AWS::EC2::Instance.InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-instancetype
    Stability:
        experimental
    """

    ipv6AddressCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::Instance.Ipv6AddressCount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ipv6addresscount
    Stability:
        experimental
    """

    ipv6Addresses: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnInstance.InstanceIpv6AddressProperty"]]]
    """``AWS::EC2::Instance.Ipv6Addresses``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ipv6addresses
    Stability:
        experimental
    """

    kernelId: str
    """``AWS::EC2::Instance.KernelId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-kernelid
    Stability:
        experimental
    """

    keyName: str
    """``AWS::EC2::Instance.KeyName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-keyname
    Stability:
        experimental
    """

    launchTemplate: typing.Union[aws_cdk.cdk.Token, "CfnInstance.LaunchTemplateSpecificationProperty"]
    """``AWS::EC2::Instance.LaunchTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-launchtemplate
    Stability:
        experimental
    """

    licenseSpecifications: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnInstance.LicenseSpecificationProperty"]]]
    """``AWS::EC2::Instance.LicenseSpecifications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-licensespecifications
    Stability:
        experimental
    """

    monitoring: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::Instance.Monitoring``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-monitoring
    Stability:
        experimental
    """

    networkInterfaces: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnInstance.NetworkInterfaceProperty"]]]
    """``AWS::EC2::Instance.NetworkInterfaces``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-networkinterfaces
    Stability:
        experimental
    """

    placementGroupName: str
    """``AWS::EC2::Instance.PlacementGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-placementgroupname
    Stability:
        experimental
    """

    privateIpAddress: str
    """``AWS::EC2::Instance.PrivateIpAddress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-privateipaddress
    Stability:
        experimental
    """

    ramdiskId: str
    """``AWS::EC2::Instance.RamdiskId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ramdiskid
    Stability:
        experimental
    """

    securityGroupIds: typing.List[str]
    """``AWS::EC2::Instance.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-securitygroupids
    Stability:
        experimental
    """

    securityGroups: typing.List[str]
    """``AWS::EC2::Instance.SecurityGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-securitygroups
    Stability:
        experimental
    """

    sourceDestCheck: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::Instance.SourceDestCheck``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-sourcedestcheck
    Stability:
        experimental
    """

    ssmAssociations: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnInstance.SsmAssociationProperty"]]]
    """``AWS::EC2::Instance.SsmAssociations``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-ssmassociations
    Stability:
        experimental
    """

    subnetId: str
    """``AWS::EC2::Instance.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-subnetid
    Stability:
        experimental
    """

    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::Instance.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-tags
    Stability:
        experimental
    """

    tenancy: str
    """``AWS::EC2::Instance.Tenancy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-tenancy
    Stability:
        experimental
    """

    userData: str
    """``AWS::EC2::Instance.UserData``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-userdata
    Stability:
        experimental
    """

    volumes: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnInstance.VolumeProperty"]]]
    """``AWS::EC2::Instance.Volumes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-volumes
    Stability:
        experimental
    """

class CfnInternetGateway(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnInternetGateway"):
    """A CloudFormation ``AWS::EC2::InternetGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-internetgateway.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::InternetGateway
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
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
    @jsii.member(jsii_name="internetGatewayName")
    def internet_gateway_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "internetGatewayName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnInternetGatewayProps":
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


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnInternetGatewayProps", jsii_struct_bases=[])
class CfnInternetGatewayProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::InternetGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-internetgateway.html
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::InternetGateway.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-internetgateway.html#cfn-ec2-internetgateway-tags
    Stability:
        experimental
    """

class CfnLaunchTemplate(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate"):
    """A CloudFormation ``AWS::EC2::LaunchTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-launchtemplate.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::LaunchTemplate
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, launch_template_data: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["LaunchTemplateDataProperty"]]]=None, launch_template_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::LaunchTemplate``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            launchTemplateData: ``AWS::EC2::LaunchTemplate.LaunchTemplateData``.
            launchTemplateName: ``AWS::EC2::LaunchTemplate.LaunchTemplateName``.

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
    @jsii.member(jsii_name="launchTemplateDefaultVersionNumber")
    def launch_template_default_version_number(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DefaultVersionNumber
        """
        return jsii.get(self, "launchTemplateDefaultVersionNumber")

    @property
    @jsii.member(jsii_name="launchTemplateId")
    def launch_template_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "launchTemplateId")

    @property
    @jsii.member(jsii_name="launchTemplateLatestVersionNumber")
    def launch_template_latest_version_number(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            LatestVersionNumber
        """
        return jsii.get(self, "launchTemplateLatestVersionNumber")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnLaunchTemplateProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.BlockDeviceMappingProperty", jsii_struct_bases=[])
    class BlockDeviceMappingProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping.html
        Stability:
            experimental
        """
        deviceName: str
        """``CfnLaunchTemplate.BlockDeviceMappingProperty.DeviceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping.html#cfn-ec2-launchtemplate-blockdevicemapping-devicename
        Stability:
            experimental
        """

        ebs: typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.EbsProperty"]
        """``CfnLaunchTemplate.BlockDeviceMappingProperty.Ebs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs
        Stability:
            experimental
        """

        noDevice: str
        """``CfnLaunchTemplate.BlockDeviceMappingProperty.NoDevice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping.html#cfn-ec2-launchtemplate-blockdevicemapping-nodevice
        Stability:
            experimental
        """

        virtualName: str
        """``CfnLaunchTemplate.BlockDeviceMappingProperty.VirtualName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping.html#cfn-ec2-launchtemplate-blockdevicemapping-virtualname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.CapacityReservationSpecificationProperty", jsii_struct_bases=[])
    class CapacityReservationSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-capacityreservationspecification.html
        Stability:
            experimental
        """
        capacityReservationPreference: str
        """``CfnLaunchTemplate.CapacityReservationSpecificationProperty.CapacityReservationPreference``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-capacityreservationspecification.html#cfn-ec2-launchtemplate-launchtemplatedata-capacityreservationspecification-capacityreservationpreference
        Stability:
            experimental
        """

        capacityReservationTarget: typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.CapacityReservationTargetProperty"]
        """``CfnLaunchTemplate.CapacityReservationSpecificationProperty.CapacityReservationTarget``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-capacityreservationspecification.html#cfn-ec2-launchtemplate-launchtemplatedata-capacityreservationspecification-capacityreservationtarget
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.CapacityReservationTargetProperty", jsii_struct_bases=[])
    class CapacityReservationTargetProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-capacityreservationtarget.html
        Stability:
            experimental
        """
        capacityReservationId: str
        """``CfnLaunchTemplate.CapacityReservationTargetProperty.CapacityReservationId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-capacityreservationtarget.html#cfn-ec2-launchtemplate-capacityreservationtarget-capacityreservationid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.CpuOptionsProperty", jsii_struct_bases=[])
    class CpuOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-cpuoptions.html
        Stability:
            experimental
        """
        coreCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.CpuOptionsProperty.CoreCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-cpuoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-cpuoptions-corecount
        Stability:
            experimental
        """

        threadsPerCore: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.CpuOptionsProperty.ThreadsPerCore``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-cpuoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-cpuoptions-threadspercore
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.CreditSpecificationProperty", jsii_struct_bases=[])
    class CreditSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-creditspecification.html
        Stability:
            experimental
        """
        cpuCredits: str
        """``CfnLaunchTemplate.CreditSpecificationProperty.CpuCredits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-creditspecification.html#cfn-ec2-launchtemplate-launchtemplatedata-creditspecification-cpucredits
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.EbsProperty", jsii_struct_bases=[])
    class EbsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html
        Stability:
            experimental
        """
        deleteOnTermination: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.EbsProperty.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-deleteontermination
        Stability:
            experimental
        """

        encrypted: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.EbsProperty.Encrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-encrypted
        Stability:
            experimental
        """

        iops: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.EbsProperty.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-iops
        Stability:
            experimental
        """

        kmsKeyId: str
        """``CfnLaunchTemplate.EbsProperty.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-kmskeyid
        Stability:
            experimental
        """

        snapshotId: str
        """``CfnLaunchTemplate.EbsProperty.SnapshotId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-snapshotid
        Stability:
            experimental
        """

        volumeSize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.EbsProperty.VolumeSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-volumesize
        Stability:
            experimental
        """

        volumeType: str
        """``CfnLaunchTemplate.EbsProperty.VolumeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-blockdevicemapping-ebs.html#cfn-ec2-launchtemplate-blockdevicemapping-ebs-volumetype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.ElasticGpuSpecificationProperty", jsii_struct_bases=[])
    class ElasticGpuSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-elasticgpuspecification.html
        Stability:
            experimental
        """
        type: str
        """``CfnLaunchTemplate.ElasticGpuSpecificationProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-elasticgpuspecification.html#cfn-ec2-launchtemplate-elasticgpuspecification-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.HibernationOptionsProperty", jsii_struct_bases=[])
    class HibernationOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-hibernationoptions.html
        Stability:
            experimental
        """
        configured: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.HibernationOptionsProperty.Configured``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-hibernationoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-hibernationoptions-configured
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.IamInstanceProfileProperty", jsii_struct_bases=[])
    class IamInstanceProfileProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-iaminstanceprofile.html
        Stability:
            experimental
        """
        arn: str
        """``CfnLaunchTemplate.IamInstanceProfileProperty.Arn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-iaminstanceprofile.html#cfn-ec2-launchtemplate-launchtemplatedata-iaminstanceprofile-arn
        Stability:
            experimental
        """

        name: str
        """``CfnLaunchTemplate.IamInstanceProfileProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-iaminstanceprofile.html#cfn-ec2-launchtemplate-launchtemplatedata-iaminstanceprofile-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.InstanceMarketOptionsProperty", jsii_struct_bases=[])
    class InstanceMarketOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions.html
        Stability:
            experimental
        """
        marketType: str
        """``CfnLaunchTemplate.InstanceMarketOptionsProperty.MarketType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-markettype
        Stability:
            experimental
        """

        spotOptions: typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.SpotOptionsProperty"]
        """``CfnLaunchTemplate.InstanceMarketOptionsProperty.SpotOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.Ipv6AddProperty", jsii_struct_bases=[])
    class Ipv6AddProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-ipv6add.html
        Stability:
            experimental
        """
        ipv6Address: str
        """``CfnLaunchTemplate.Ipv6AddProperty.Ipv6Address``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-ipv6add.html#cfn-ec2-launchtemplate-ipv6add-ipv6address
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.LaunchTemplateDataProperty", jsii_struct_bases=[])
    class LaunchTemplateDataProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html
        Stability:
            experimental
        """
        blockDeviceMappings: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.BlockDeviceMappingProperty"]]]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.BlockDeviceMappings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-blockdevicemappings
        Stability:
            experimental
        """

        capacityReservationSpecification: typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.CapacityReservationSpecificationProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.CapacityReservationSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-capacityreservationspecification
        Stability:
            experimental
        """

        cpuOptions: typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.CpuOptionsProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.CpuOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-cpuoptions
        Stability:
            experimental
        """

        creditSpecification: typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.CreditSpecificationProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.CreditSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-creditspecification
        Stability:
            experimental
        """

        disableApiTermination: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.DisableApiTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-disableapitermination
        Stability:
            experimental
        """

        ebsOptimized: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.EbsOptimized``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-ebsoptimized
        Stability:
            experimental
        """

        elasticGpuSpecifications: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.ElasticGpuSpecificationProperty"]]]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.ElasticGpuSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-elasticgpuspecifications
        Stability:
            experimental
        """

        elasticInferenceAccelerators: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.LaunchTemplateElasticInferenceAcceleratorProperty"]]]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.ElasticInferenceAccelerators``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-elasticinferenceaccelerators
        Stability:
            experimental
        """

        hibernationOptions: typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.HibernationOptionsProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.HibernationOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-hibernationoptions
        Stability:
            experimental
        """

        iamInstanceProfile: typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.IamInstanceProfileProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.IamInstanceProfile``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-iaminstanceprofile
        Stability:
            experimental
        """

        imageId: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.ImageId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-imageid
        Stability:
            experimental
        """

        instanceInitiatedShutdownBehavior: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.InstanceInitiatedShutdownBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-instanceinitiatedshutdownbehavior
        Stability:
            experimental
        """

        instanceMarketOptions: typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.InstanceMarketOptionsProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.InstanceMarketOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-instancemarketoptions
        Stability:
            experimental
        """

        instanceType: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-instancetype
        Stability:
            experimental
        """

        kernelId: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.KernelId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-kernelid
        Stability:
            experimental
        """

        keyName: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.KeyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-keyname
        Stability:
            experimental
        """

        licenseSpecifications: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.LicenseSpecificationProperty"]]]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.LicenseSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-licensespecifications
        Stability:
            experimental
        """

        monitoring: typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.MonitoringProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.Monitoring``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-monitoring
        Stability:
            experimental
        """

        networkInterfaces: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.NetworkInterfaceProperty"]]]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.NetworkInterfaces``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-networkinterfaces
        Stability:
            experimental
        """

        placement: typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.PlacementProperty"]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.Placement``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-placement
        Stability:
            experimental
        """

        ramDiskId: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.RamDiskId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-ramdiskid
        Stability:
            experimental
        """

        securityGroupIds: typing.List[str]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-securitygroupids
        Stability:
            experimental
        """

        securityGroups: typing.List[str]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.SecurityGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-securitygroups
        Stability:
            experimental
        """

        tagSpecifications: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.TagSpecificationProperty"]]]
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.TagSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-tagspecifications
        Stability:
            experimental
        """

        userData: str
        """``CfnLaunchTemplate.LaunchTemplateDataProperty.UserData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata.html#cfn-ec2-launchtemplate-launchtemplatedata-userdata
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.LaunchTemplateElasticInferenceAcceleratorProperty", jsii_struct_bases=[])
    class LaunchTemplateElasticInferenceAcceleratorProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplateelasticinferenceaccelerator.html
        Stability:
            experimental
        """
        type: str
        """``CfnLaunchTemplate.LaunchTemplateElasticInferenceAcceleratorProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplateelasticinferenceaccelerator.html#cfn-ec2-launchtemplate-launchtemplateelasticinferenceaccelerator-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.LicenseSpecificationProperty", jsii_struct_bases=[])
    class LicenseSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-licensespecification.html
        Stability:
            experimental
        """
        licenseConfigurationArn: str
        """``CfnLaunchTemplate.LicenseSpecificationProperty.LicenseConfigurationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-licensespecification.html#cfn-ec2-launchtemplate-licensespecification-licenseconfigurationarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.MonitoringProperty", jsii_struct_bases=[])
    class MonitoringProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-monitoring.html
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.MonitoringProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-monitoring.html#cfn-ec2-launchtemplate-launchtemplatedata-monitoring-enabled
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.NetworkInterfaceProperty", jsii_struct_bases=[])
    class NetworkInterfaceProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html
        Stability:
            experimental
        """
        associatePublicIpAddress: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.AssociatePublicIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-associatepublicipaddress
        Stability:
            experimental
        """

        deleteOnTermination: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-deleteontermination
        Stability:
            experimental
        """

        description: str
        """``CfnLaunchTemplate.NetworkInterfaceProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-description
        Stability:
            experimental
        """

        deviceIndex: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.DeviceIndex``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-deviceindex
        Stability:
            experimental
        """

        groups: typing.List[str]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.Groups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-groups
        Stability:
            experimental
        """

        interfaceType: str
        """``CfnLaunchTemplate.NetworkInterfaceProperty.InterfaceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-interfacetype
        Stability:
            experimental
        """

        ipv6AddressCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.Ipv6AddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-ipv6addresscount
        Stability:
            experimental
        """

        ipv6Addresses: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.Ipv6AddProperty"]]]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.Ipv6Addresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-ipv6addresses
        Stability:
            experimental
        """

        networkInterfaceId: str
        """``CfnLaunchTemplate.NetworkInterfaceProperty.NetworkInterfaceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-networkinterfaceid
        Stability:
            experimental
        """

        privateIpAddress: str
        """``CfnLaunchTemplate.NetworkInterfaceProperty.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-privateipaddress
        Stability:
            experimental
        """

        privateIpAddresses: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.PrivateIpAddProperty"]]]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.PrivateIpAddresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-privateipaddresses
        Stability:
            experimental
        """

        secondaryPrivateIpAddressCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.NetworkInterfaceProperty.SecondaryPrivateIpAddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-secondaryprivateipaddresscount
        Stability:
            experimental
        """

        subnetId: str
        """``CfnLaunchTemplate.NetworkInterfaceProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-networkinterface.html#cfn-ec2-launchtemplate-networkinterface-subnetid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.PlacementProperty", jsii_struct_bases=[])
    class PlacementProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-placement.html
        Stability:
            experimental
        """
        affinity: str
        """``CfnLaunchTemplate.PlacementProperty.Affinity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-placement.html#cfn-ec2-launchtemplate-launchtemplatedata-placement-affinity
        Stability:
            experimental
        """

        availabilityZone: str
        """``CfnLaunchTemplate.PlacementProperty.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-placement.html#cfn-ec2-launchtemplate-launchtemplatedata-placement-availabilityzone
        Stability:
            experimental
        """

        groupName: str
        """``CfnLaunchTemplate.PlacementProperty.GroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-placement.html#cfn-ec2-launchtemplate-launchtemplatedata-placement-groupname
        Stability:
            experimental
        """

        hostId: str
        """``CfnLaunchTemplate.PlacementProperty.HostId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-placement.html#cfn-ec2-launchtemplate-launchtemplatedata-placement-hostid
        Stability:
            experimental
        """

        tenancy: str
        """``CfnLaunchTemplate.PlacementProperty.Tenancy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-placement.html#cfn-ec2-launchtemplate-launchtemplatedata-placement-tenancy
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.PrivateIpAddProperty", jsii_struct_bases=[])
    class PrivateIpAddProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-privateipadd.html
        Stability:
            experimental
        """
        primary: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnLaunchTemplate.PrivateIpAddProperty.Primary``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-privateipadd.html#cfn-ec2-launchtemplate-privateipadd-primary
        Stability:
            experimental
        """

        privateIpAddress: str
        """``CfnLaunchTemplate.PrivateIpAddProperty.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-privateipadd.html#cfn-ec2-launchtemplate-privateipadd-privateipaddress
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.SpotOptionsProperty", jsii_struct_bases=[])
    class SpotOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions.html
        Stability:
            experimental
        """
        instanceInterruptionBehavior: str
        """``CfnLaunchTemplate.SpotOptionsProperty.InstanceInterruptionBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions-instanceinterruptionbehavior
        Stability:
            experimental
        """

        maxPrice: str
        """``CfnLaunchTemplate.SpotOptionsProperty.MaxPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions-maxprice
        Stability:
            experimental
        """

        spotInstanceType: str
        """``CfnLaunchTemplate.SpotOptionsProperty.SpotInstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions.html#cfn-ec2-launchtemplate-launchtemplatedata-instancemarketoptions-spotoptions-spotinstancetype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplate.TagSpecificationProperty", jsii_struct_bases=[])
    class TagSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-tagspecification.html
        Stability:
            experimental
        """
        resourceType: str
        """``CfnLaunchTemplate.TagSpecificationProperty.ResourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-tagspecification.html#cfn-ec2-launchtemplate-tagspecification-resourcetype
        Stability:
            experimental
        """

        tags: typing.List[aws_cdk.cdk.CfnTag]
        """``CfnLaunchTemplate.TagSpecificationProperty.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-launchtemplate-tagspecification.html#cfn-ec2-launchtemplate-tagspecification-tags
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnLaunchTemplateProps", jsii_struct_bases=[])
class CfnLaunchTemplateProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::LaunchTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-launchtemplate.html
    Stability:
        experimental
    """
    launchTemplateData: typing.Union[aws_cdk.cdk.Token, "CfnLaunchTemplate.LaunchTemplateDataProperty"]
    """``AWS::EC2::LaunchTemplate.LaunchTemplateData``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-launchtemplate.html#cfn-ec2-launchtemplate-launchtemplatedata
    Stability:
        experimental
    """

    launchTemplateName: str
    """``AWS::EC2::LaunchTemplate.LaunchTemplateName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-launchtemplate.html#cfn-ec2-launchtemplate-launchtemplatename
    Stability:
        experimental
    """

class CfnNatGateway(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnNatGateway"):
    """A CloudFormation ``AWS::EC2::NatGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::NatGateway
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, allocation_id: str, subnet_id: str, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::NatGateway``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            allocationId: ``AWS::EC2::NatGateway.AllocationId``.
            subnetId: ``AWS::EC2::NatGateway.SubnetId``.
            tags: ``AWS::EC2::NatGateway.Tags``.

        Stability:
            experimental
        """
        props: CfnNatGatewayProps = {"allocationId": allocation_id, "subnetId": subnet_id}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnNatGateway, self, [scope, id, props])

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
    @jsii.member(jsii_name="natGatewayId")
    def nat_gateway_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "natGatewayId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnNatGatewayProps":
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
class _CfnNatGatewayProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::NatGateway.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html#cfn-ec2-natgateway-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNatGatewayProps", jsii_struct_bases=[_CfnNatGatewayProps])
class CfnNatGatewayProps(_CfnNatGatewayProps):
    """Properties for defining a ``AWS::EC2::NatGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html
    Stability:
        experimental
    """
    allocationId: str
    """``AWS::EC2::NatGateway.AllocationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html#cfn-ec2-natgateway-allocationid
    Stability:
        experimental
    """

    subnetId: str
    """``AWS::EC2::NatGateway.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html#cfn-ec2-natgateway-subnetid
    Stability:
        experimental
    """

class CfnNetworkAcl(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnNetworkAcl"):
    """A CloudFormation ``AWS::EC2::NetworkAcl``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::NetworkAcl
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc_id: str, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::NetworkAcl``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            vpcId: ``AWS::EC2::NetworkAcl.VpcId``.
            tags: ``AWS::EC2::NetworkAcl.Tags``.

        Stability:
            experimental
        """
        props: CfnNetworkAclProps = {"vpcId": vpc_id}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnNetworkAcl, self, [scope, id, props])

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
    @jsii.member(jsii_name="networkAclName")
    def network_acl_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "networkAclName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnNetworkAclProps":
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


class CfnNetworkAclEntry(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnNetworkAclEntry"):
    """A CloudFormation ``AWS::EC2::NetworkAclEntry``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::NetworkAclEntry
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, network_acl_id: str, protocol: typing.Union[jsii.Number, aws_cdk.cdk.Token], rule_action: str, rule_number: typing.Union[jsii.Number, aws_cdk.cdk.Token], cidr_block: typing.Optional[str]=None, egress: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, icmp: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["IcmpProperty"]]]=None, ipv6_cidr_block: typing.Optional[str]=None, port_range: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["PortRangeProperty"]]]=None) -> None:
        """Create a new ``AWS::EC2::NetworkAclEntry``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            networkAclId: ``AWS::EC2::NetworkAclEntry.NetworkAclId``.
            protocol: ``AWS::EC2::NetworkAclEntry.Protocol``.
            ruleAction: ``AWS::EC2::NetworkAclEntry.RuleAction``.
            ruleNumber: ``AWS::EC2::NetworkAclEntry.RuleNumber``.
            cidrBlock: ``AWS::EC2::NetworkAclEntry.CidrBlock``.
            egress: ``AWS::EC2::NetworkAclEntry.Egress``.
            icmp: ``AWS::EC2::NetworkAclEntry.Icmp``.
            ipv6CidrBlock: ``AWS::EC2::NetworkAclEntry.Ipv6CidrBlock``.
            portRange: ``AWS::EC2::NetworkAclEntry.PortRange``.

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
    @jsii.member(jsii_name="networkAclEntryName")
    def network_acl_entry_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "networkAclEntryName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnNetworkAclEntryProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkAclEntry.IcmpProperty", jsii_struct_bases=[])
    class IcmpProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkaclentry-icmp.html
        Stability:
            experimental
        """
        code: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnNetworkAclEntry.IcmpProperty.Code``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkaclentry-icmp.html#cfn-ec2-networkaclentry-icmp-code
        Stability:
            experimental
        """

        type: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnNetworkAclEntry.IcmpProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkaclentry-icmp.html#cfn-ec2-networkaclentry-icmp-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkAclEntry.PortRangeProperty", jsii_struct_bases=[])
    class PortRangeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkaclentry-portrange.html
        Stability:
            experimental
        """
        from_: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnNetworkAclEntry.PortRangeProperty.From``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkaclentry-portrange.html#cfn-ec2-networkaclentry-portrange-from
        Stability:
            experimental
        """

        to: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnNetworkAclEntry.PortRangeProperty.To``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkaclentry-portrange.html#cfn-ec2-networkaclentry-portrange-to
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnNetworkAclEntryProps(jsii.compat.TypedDict, total=False):
    cidrBlock: str
    """``AWS::EC2::NetworkAclEntry.CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-cidrblock
    Stability:
        experimental
    """
    egress: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::NetworkAclEntry.Egress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-egress
    Stability:
        experimental
    """
    icmp: typing.Union[aws_cdk.cdk.Token, "CfnNetworkAclEntry.IcmpProperty"]
    """``AWS::EC2::NetworkAclEntry.Icmp``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-icmp
    Stability:
        experimental
    """
    ipv6CidrBlock: str
    """``AWS::EC2::NetworkAclEntry.Ipv6CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-ipv6cidrblock
    Stability:
        experimental
    """
    portRange: typing.Union[aws_cdk.cdk.Token, "CfnNetworkAclEntry.PortRangeProperty"]
    """``AWS::EC2::NetworkAclEntry.PortRange``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-portrange
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkAclEntryProps", jsii_struct_bases=[_CfnNetworkAclEntryProps])
class CfnNetworkAclEntryProps(_CfnNetworkAclEntryProps):
    """Properties for defining a ``AWS::EC2::NetworkAclEntry``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html
    Stability:
        experimental
    """
    networkAclId: str
    """``AWS::EC2::NetworkAclEntry.NetworkAclId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-networkaclid
    Stability:
        experimental
    """

    protocol: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::NetworkAclEntry.Protocol``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-protocol
    Stability:
        experimental
    """

    ruleAction: str
    """``AWS::EC2::NetworkAclEntry.RuleAction``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-ruleaction
    Stability:
        experimental
    """

    ruleNumber: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::NetworkAclEntry.RuleNumber``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl-entry.html#cfn-ec2-networkaclentry-rulenumber
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnNetworkAclProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::NetworkAcl.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl.html#cfn-ec2-networkacl-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkAclProps", jsii_struct_bases=[_CfnNetworkAclProps])
class CfnNetworkAclProps(_CfnNetworkAclProps):
    """Properties for defining a ``AWS::EC2::NetworkAcl``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl.html
    Stability:
        experimental
    """
    vpcId: str
    """``AWS::EC2::NetworkAcl.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-acl.html#cfn-ec2-networkacl-vpcid
    Stability:
        experimental
    """

class CfnNetworkInterface(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterface"):
    """A CloudFormation ``AWS::EC2::NetworkInterface``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::NetworkInterface
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, subnet_id: str, description: typing.Optional[str]=None, group_set: typing.Optional[typing.List[str]]=None, interface_type: typing.Optional[str]=None, ipv6_address_count: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, ipv6_addresses: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["InstanceIpv6AddressProperty"]]]=None, private_ip_address: typing.Optional[str]=None, private_ip_addresses: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "PrivateIpAddressSpecificationProperty"]]]]]=None, secondary_private_ip_address_count: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, source_dest_check: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::NetworkInterface``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            subnetId: ``AWS::EC2::NetworkInterface.SubnetId``.
            description: ``AWS::EC2::NetworkInterface.Description``.
            groupSet: ``AWS::EC2::NetworkInterface.GroupSet``.
            interfaceType: ``AWS::EC2::NetworkInterface.InterfaceType``.
            ipv6AddressCount: ``AWS::EC2::NetworkInterface.Ipv6AddressCount``.
            ipv6Addresses: ``AWS::EC2::NetworkInterface.Ipv6Addresses``.
            privateIpAddress: ``AWS::EC2::NetworkInterface.PrivateIpAddress``.
            privateIpAddresses: ``AWS::EC2::NetworkInterface.PrivateIpAddresses``.
            secondaryPrivateIpAddressCount: ``AWS::EC2::NetworkInterface.SecondaryPrivateIpAddressCount``.
            sourceDestCheck: ``AWS::EC2::NetworkInterface.SourceDestCheck``.
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
    @jsii.member(jsii_name="networkInterfaceName")
    def network_interface_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "networkInterfaceName")

    @property
    @jsii.member(jsii_name="networkInterfacePrimaryPrivateIpAddress")
    def network_interface_primary_private_ip_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            PrimaryPrivateIpAddress
        """
        return jsii.get(self, "networkInterfacePrimaryPrivateIpAddress")

    @property
    @jsii.member(jsii_name="networkInterfaceSecondaryPrivateIpAddresses")
    def network_interface_secondary_private_ip_addresses(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            SecondaryPrivateIpAddresses
        """
        return jsii.get(self, "networkInterfaceSecondaryPrivateIpAddresses")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnNetworkInterfaceProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterface.InstanceIpv6AddressProperty", jsii_struct_bases=[])
    class InstanceIpv6AddressProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkinterface-instanceipv6address.html
        Stability:
            experimental
        """
        ipv6Address: str
        """``CfnNetworkInterface.InstanceIpv6AddressProperty.Ipv6Address``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-networkinterface-instanceipv6address.html#cfn-ec2-networkinterface-instanceipv6address-ipv6address
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterface.PrivateIpAddressSpecificationProperty", jsii_struct_bases=[])
    class PrivateIpAddressSpecificationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-interface-privateipspec.html
        Stability:
            experimental
        """
        primary: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnNetworkInterface.PrivateIpAddressSpecificationProperty.Primary``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-interface-privateipspec.html#cfn-ec2-networkinterface-privateipspecification-primary
        Stability:
            experimental
        """

        privateIpAddress: str
        """``CfnNetworkInterface.PrivateIpAddressSpecificationProperty.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-network-interface-privateipspec.html#cfn-ec2-networkinterface-privateipspecification-privateipaddress
        Stability:
            experimental
        """


class CfnNetworkInterfaceAttachment(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterfaceAttachment"):
    """A CloudFormation ``AWS::EC2::NetworkInterfaceAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::NetworkInterfaceAttachment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, device_index: str, instance_id: str, network_interface_id: str, delete_on_termination: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::EC2::NetworkInterfaceAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            deviceIndex: ``AWS::EC2::NetworkInterfaceAttachment.DeviceIndex``.
            instanceId: ``AWS::EC2::NetworkInterfaceAttachment.InstanceId``.
            networkInterfaceId: ``AWS::EC2::NetworkInterfaceAttachment.NetworkInterfaceId``.
            deleteOnTermination: ``AWS::EC2::NetworkInterfaceAttachment.DeleteOnTermination``.

        Stability:
            experimental
        """
        props: CfnNetworkInterfaceAttachmentProps = {"deviceIndex": device_index, "instanceId": instance_id, "networkInterfaceId": network_interface_id}

        if delete_on_termination is not None:
            props["deleteOnTermination"] = delete_on_termination

        jsii.create(CfnNetworkInterfaceAttachment, self, [scope, id, props])

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
    @jsii.member(jsii_name="networkInterfaceAttachmentName")
    def network_interface_attachment_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "networkInterfaceAttachmentName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnNetworkInterfaceAttachmentProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnNetworkInterfaceAttachmentProps(jsii.compat.TypedDict, total=False):
    deleteOnTermination: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::NetworkInterfaceAttachment.DeleteOnTermination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html#cfn-ec2-network-interface-attachment-deleteonterm
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterfaceAttachmentProps", jsii_struct_bases=[_CfnNetworkInterfaceAttachmentProps])
class CfnNetworkInterfaceAttachmentProps(_CfnNetworkInterfaceAttachmentProps):
    """Properties for defining a ``AWS::EC2::NetworkInterfaceAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html
    Stability:
        experimental
    """
    deviceIndex: str
    """``AWS::EC2::NetworkInterfaceAttachment.DeviceIndex``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html#cfn-ec2-network-interface-attachment-deviceindex
    Stability:
        experimental
    """

    instanceId: str
    """``AWS::EC2::NetworkInterfaceAttachment.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html#cfn-ec2-network-interface-attachment-instanceid
    Stability:
        experimental
    """

    networkInterfaceId: str
    """``AWS::EC2::NetworkInterfaceAttachment.NetworkInterfaceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface-attachment.html#cfn-ec2-network-interface-attachment-networkinterfaceid
    Stability:
        experimental
    """

class CfnNetworkInterfacePermission(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterfacePermission"):
    """A CloudFormation ``AWS::EC2::NetworkInterfacePermission``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::NetworkInterfacePermission
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, aws_account_id: str, network_interface_id: str, permission: str) -> None:
        """Create a new ``AWS::EC2::NetworkInterfacePermission``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            awsAccountId: ``AWS::EC2::NetworkInterfacePermission.AwsAccountId``.
            networkInterfaceId: ``AWS::EC2::NetworkInterfacePermission.NetworkInterfaceId``.
            permission: ``AWS::EC2::NetworkInterfacePermission.Permission``.

        Stability:
            experimental
        """
        props: CfnNetworkInterfacePermissionProps = {"awsAccountId": aws_account_id, "networkInterfaceId": network_interface_id, "permission": permission}

        jsii.create(CfnNetworkInterfacePermission, self, [scope, id, props])

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
    @jsii.member(jsii_name="networkInterfacePermissionId")
    def network_interface_permission_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "networkInterfacePermissionId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnNetworkInterfacePermissionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterfacePermissionProps", jsii_struct_bases=[])
class CfnNetworkInterfacePermissionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::NetworkInterfacePermission``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html
    Stability:
        experimental
    """
    awsAccountId: str
    """``AWS::EC2::NetworkInterfacePermission.AwsAccountId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html#cfn-ec2-networkinterfacepermission-awsaccountid
    Stability:
        experimental
    """

    networkInterfaceId: str
    """``AWS::EC2::NetworkInterfacePermission.NetworkInterfaceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html#cfn-ec2-networkinterfacepermission-networkinterfaceid
    Stability:
        experimental
    """

    permission: str
    """``AWS::EC2::NetworkInterfacePermission.Permission``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-networkinterfacepermission.html#cfn-ec2-networkinterfacepermission-permission
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnNetworkInterfaceProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::EC2::NetworkInterface.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-description
    Stability:
        experimental
    """
    groupSet: typing.List[str]
    """``AWS::EC2::NetworkInterface.GroupSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-groupset
    Stability:
        experimental
    """
    interfaceType: str
    """``AWS::EC2::NetworkInterface.InterfaceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-ec2-networkinterface-interfacetype
    Stability:
        experimental
    """
    ipv6AddressCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::NetworkInterface.Ipv6AddressCount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-ec2-networkinterface-ipv6addresscount
    Stability:
        experimental
    """
    ipv6Addresses: typing.Union[aws_cdk.cdk.Token, "CfnNetworkInterface.InstanceIpv6AddressProperty"]
    """``AWS::EC2::NetworkInterface.Ipv6Addresses``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-ec2-networkinterface-ipv6addresses
    Stability:
        experimental
    """
    privateIpAddress: str
    """``AWS::EC2::NetworkInterface.PrivateIpAddress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-privateipaddress
    Stability:
        experimental
    """
    privateIpAddresses: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnNetworkInterface.PrivateIpAddressSpecificationProperty"]]]
    """``AWS::EC2::NetworkInterface.PrivateIpAddresses``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-privateipaddresses
    Stability:
        experimental
    """
    secondaryPrivateIpAddressCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::NetworkInterface.SecondaryPrivateIpAddressCount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-secondaryprivateipcount
    Stability:
        experimental
    """
    sourceDestCheck: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::NetworkInterface.SourceDestCheck``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-sourcedestcheck
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::NetworkInterface.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnNetworkInterfaceProps", jsii_struct_bases=[_CfnNetworkInterfaceProps])
class CfnNetworkInterfaceProps(_CfnNetworkInterfaceProps):
    """Properties for defining a ``AWS::EC2::NetworkInterface``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html
    Stability:
        experimental
    """
    subnetId: str
    """``AWS::EC2::NetworkInterface.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-network-interface.html#cfn-awsec2networkinterface-subnetid
    Stability:
        experimental
    """

class CfnPlacementGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnPlacementGroup"):
    """A CloudFormation ``AWS::EC2::PlacementGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-placementgroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::PlacementGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, strategy: typing.Optional[str]=None) -> None:
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
    @jsii.member(jsii_name="placementGroupName")
    def placement_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "placementGroupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnPlacementGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnPlacementGroupProps", jsii_struct_bases=[])
class CfnPlacementGroupProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::PlacementGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-placementgroup.html
    Stability:
        experimental
    """
    strategy: str
    """``AWS::EC2::PlacementGroup.Strategy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-placementgroup.html#cfn-ec2-placementgroup-strategy
    Stability:
        experimental
    """

class CfnRoute(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnRoute"):
    """A CloudFormation ``AWS::EC2::Route``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::Route
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, route_table_id: str, destination_cidr_block: typing.Optional[str]=None, destination_ipv6_cidr_block: typing.Optional[str]=None, egress_only_internet_gateway_id: typing.Optional[str]=None, gateway_id: typing.Optional[str]=None, instance_id: typing.Optional[str]=None, nat_gateway_id: typing.Optional[str]=None, network_interface_id: typing.Optional[str]=None, vpc_peering_connection_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::Route``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            routeTableId: ``AWS::EC2::Route.RouteTableId``.
            destinationCidrBlock: ``AWS::EC2::Route.DestinationCidrBlock``.
            destinationIpv6CidrBlock: ``AWS::EC2::Route.DestinationIpv6CidrBlock``.
            egressOnlyInternetGatewayId: ``AWS::EC2::Route.EgressOnlyInternetGatewayId``.
            gatewayId: ``AWS::EC2::Route.GatewayId``.
            instanceId: ``AWS::EC2::Route.InstanceId``.
            natGatewayId: ``AWS::EC2::Route.NatGatewayId``.
            networkInterfaceId: ``AWS::EC2::Route.NetworkInterfaceId``.
            vpcPeeringConnectionId: ``AWS::EC2::Route.VpcPeeringConnectionId``.

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

        if vpc_peering_connection_id is not None:
            props["vpcPeeringConnectionId"] = vpc_peering_connection_id

        jsii.create(CfnRoute, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnRouteProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="routeName")
    def route_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "routeName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRouteProps(jsii.compat.TypedDict, total=False):
    destinationCidrBlock: str
    """``AWS::EC2::Route.DestinationCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-destinationcidrblock
    Stability:
        experimental
    """
    destinationIpv6CidrBlock: str
    """``AWS::EC2::Route.DestinationIpv6CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-destinationipv6cidrblock
    Stability:
        experimental
    """
    egressOnlyInternetGatewayId: str
    """``AWS::EC2::Route.EgressOnlyInternetGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-egressonlyinternetgatewayid
    Stability:
        experimental
    """
    gatewayId: str
    """``AWS::EC2::Route.GatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-gatewayid
    Stability:
        experimental
    """
    instanceId: str
    """``AWS::EC2::Route.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-instanceid
    Stability:
        experimental
    """
    natGatewayId: str
    """``AWS::EC2::Route.NatGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-natgatewayid
    Stability:
        experimental
    """
    networkInterfaceId: str
    """``AWS::EC2::Route.NetworkInterfaceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-networkinterfaceid
    Stability:
        experimental
    """
    vpcPeeringConnectionId: str
    """``AWS::EC2::Route.VpcPeeringConnectionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-vpcpeeringconnectionid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnRouteProps", jsii_struct_bases=[_CfnRouteProps])
class CfnRouteProps(_CfnRouteProps):
    """Properties for defining a ``AWS::EC2::Route``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html
    Stability:
        experimental
    """
    routeTableId: str
    """``AWS::EC2::Route.RouteTableId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html#cfn-ec2-route-routetableid
    Stability:
        experimental
    """

class CfnRouteTable(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnRouteTable"):
    """A CloudFormation ``AWS::EC2::RouteTable``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route-table.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::RouteTable
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc_id: str, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::RouteTable``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            vpcId: ``AWS::EC2::RouteTable.VpcId``.
            tags: ``AWS::EC2::RouteTable.Tags``.

        Stability:
            experimental
        """
        props: CfnRouteTableProps = {"vpcId": vpc_id}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnRouteTable, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnRouteTableProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="routeTableId")
    def route_table_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "routeTableId")

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
class _CfnRouteTableProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::RouteTable.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route-table.html#cfn-ec2-routetable-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnRouteTableProps", jsii_struct_bases=[_CfnRouteTableProps])
class CfnRouteTableProps(_CfnRouteTableProps):
    """Properties for defining a ``AWS::EC2::RouteTable``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route-table.html
    Stability:
        experimental
    """
    vpcId: str
    """``AWS::EC2::RouteTable.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route-table.html#cfn-ec2-routetable-vpcid
    Stability:
        experimental
    """

class CfnSecurityGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroup"):
    """A CloudFormation ``AWS::EC2::SecurityGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::SecurityGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, group_description: str, group_name: typing.Optional[str]=None, security_group_egress: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "EgressProperty"]]]]]=None, security_group_ingress: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "IngressProperty"]]]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::SecurityGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            groupDescription: ``AWS::EC2::SecurityGroup.GroupDescription``.
            groupName: ``AWS::EC2::SecurityGroup.GroupName``.
            securityGroupEgress: ``AWS::EC2::SecurityGroup.SecurityGroupEgress``.
            securityGroupIngress: ``AWS::EC2::SecurityGroup.SecurityGroupIngress``.
            tags: ``AWS::EC2::SecurityGroup.Tags``.
            vpcId: ``AWS::EC2::SecurityGroup.VpcId``.

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
    def property_overrides(self) -> "CfnSecurityGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            GroupId
        """
        return jsii.get(self, "securityGroupId")

    @property
    @jsii.member(jsii_name="securityGroupName")
    def security_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupName")

    @property
    @jsii.member(jsii_name="securityGroupVpcId")
    def security_group_vpc_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            VpcId
        """
        return jsii.get(self, "securityGroupVpcId")

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
    class _EgressProperty(jsii.compat.TypedDict, total=False):
        cidrIp: str
        """``CfnSecurityGroup.EgressProperty.CidrIp``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-cidrip
        Stability:
            experimental
        """
        cidrIpv6: str
        """``CfnSecurityGroup.EgressProperty.CidrIpv6``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-cidripv6
        Stability:
            experimental
        """
        description: str
        """``CfnSecurityGroup.EgressProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-description
        Stability:
            experimental
        """
        destinationPrefixListId: str
        """``CfnSecurityGroup.EgressProperty.DestinationPrefixListId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-destinationprefixlistid
        Stability:
            experimental
        """
        destinationSecurityGroupId: str
        """``CfnSecurityGroup.EgressProperty.DestinationSecurityGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-destsecgroupid
        Stability:
            experimental
        """
        fromPort: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSecurityGroup.EgressProperty.FromPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-fromport
        Stability:
            experimental
        """
        toPort: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSecurityGroup.EgressProperty.ToPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-toport
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroup.EgressProperty", jsii_struct_bases=[_EgressProperty])
    class EgressProperty(_EgressProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html
        Stability:
            experimental
        """
        ipProtocol: str
        """``CfnSecurityGroup.EgressProperty.IpProtocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-ipprotocol
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _IngressProperty(jsii.compat.TypedDict, total=False):
        cidrIp: str
        """``CfnSecurityGroup.IngressProperty.CidrIp``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-cidrip
        Stability:
            experimental
        """
        cidrIpv6: str
        """``CfnSecurityGroup.IngressProperty.CidrIpv6``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-cidripv6
        Stability:
            experimental
        """
        description: str
        """``CfnSecurityGroup.IngressProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-description
        Stability:
            experimental
        """
        fromPort: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSecurityGroup.IngressProperty.FromPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-fromport
        Stability:
            experimental
        """
        sourcePrefixListId: str
        """``CfnSecurityGroup.IngressProperty.SourcePrefixListId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-securitygroup-ingress-sourceprefixlistid
        Stability:
            experimental
        """
        sourceSecurityGroupId: str
        """``CfnSecurityGroup.IngressProperty.SourceSecurityGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-sourcesecuritygroupid
        Stability:
            experimental
        """
        sourceSecurityGroupName: str
        """``CfnSecurityGroup.IngressProperty.SourceSecurityGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-sourcesecuritygroupname
        Stability:
            experimental
        """
        sourceSecurityGroupOwnerId: str
        """``CfnSecurityGroup.IngressProperty.SourceSecurityGroupOwnerId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-sourcesecuritygroupownerid
        Stability:
            experimental
        """
        toPort: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSecurityGroup.IngressProperty.ToPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-toport
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroup.IngressProperty", jsii_struct_bases=[_IngressProperty])
    class IngressProperty(_IngressProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html
        Stability:
            experimental
        """
        ipProtocol: str
        """``CfnSecurityGroup.IngressProperty.IpProtocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html#cfn-ec2-security-group-rule-ipprotocol
        Stability:
            experimental
        """


class CfnSecurityGroupEgress(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroupEgress"):
    """A CloudFormation ``AWS::EC2::SecurityGroupEgress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::SecurityGroupEgress
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, group_id: str, ip_protocol: str, cidr_ip: typing.Optional[str]=None, cidr_ipv6: typing.Optional[str]=None, description: typing.Optional[str]=None, destination_prefix_list_id: typing.Optional[str]=None, destination_security_group_id: typing.Optional[str]=None, from_port: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, to_port: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::EC2::SecurityGroupEgress``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            groupId: ``AWS::EC2::SecurityGroupEgress.GroupId``.
            ipProtocol: ``AWS::EC2::SecurityGroupEgress.IpProtocol``.
            cidrIp: ``AWS::EC2::SecurityGroupEgress.CidrIp``.
            cidrIpv6: ``AWS::EC2::SecurityGroupEgress.CidrIpv6``.
            description: ``AWS::EC2::SecurityGroupEgress.Description``.
            destinationPrefixListId: ``AWS::EC2::SecurityGroupEgress.DestinationPrefixListId``.
            destinationSecurityGroupId: ``AWS::EC2::SecurityGroupEgress.DestinationSecurityGroupId``.
            fromPort: ``AWS::EC2::SecurityGroupEgress.FromPort``.
            toPort: ``AWS::EC2::SecurityGroupEgress.ToPort``.

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
    def property_overrides(self) -> "CfnSecurityGroupEgressProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="securityGroupEgressId")
    def security_group_egress_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupEgressId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSecurityGroupEgressProps(jsii.compat.TypedDict, total=False):
    cidrIp: str
    """``AWS::EC2::SecurityGroupEgress.CidrIp``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-cidrip
    Stability:
        experimental
    """
    cidrIpv6: str
    """``AWS::EC2::SecurityGroupEgress.CidrIpv6``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-cidripv6
    Stability:
        experimental
    """
    description: str
    """``AWS::EC2::SecurityGroupEgress.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-description
    Stability:
        experimental
    """
    destinationPrefixListId: str
    """``AWS::EC2::SecurityGroupEgress.DestinationPrefixListId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-destinationprefixlistid
    Stability:
        experimental
    """
    destinationSecurityGroupId: str
    """``AWS::EC2::SecurityGroupEgress.DestinationSecurityGroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-destinationsecuritygroupid
    Stability:
        experimental
    """
    fromPort: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::SecurityGroupEgress.FromPort``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-fromport
    Stability:
        experimental
    """
    toPort: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::SecurityGroupEgress.ToPort``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-toport
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroupEgressProps", jsii_struct_bases=[_CfnSecurityGroupEgressProps])
class CfnSecurityGroupEgressProps(_CfnSecurityGroupEgressProps):
    """Properties for defining a ``AWS::EC2::SecurityGroupEgress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html
    Stability:
        experimental
    """
    groupId: str
    """``AWS::EC2::SecurityGroupEgress.GroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-groupid
    Stability:
        experimental
    """

    ipProtocol: str
    """``AWS::EC2::SecurityGroupEgress.IpProtocol``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html#cfn-ec2-securitygroupegress-ipprotocol
    Stability:
        experimental
    """

class CfnSecurityGroupIngress(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroupIngress"):
    """A CloudFormation ``AWS::EC2::SecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::SecurityGroupIngress
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, ip_protocol: str, cidr_ip: typing.Optional[str]=None, cidr_ipv6: typing.Optional[str]=None, description: typing.Optional[str]=None, from_port: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, group_id: typing.Optional[str]=None, group_name: typing.Optional[str]=None, source_prefix_list_id: typing.Optional[str]=None, source_security_group_id: typing.Optional[str]=None, source_security_group_name: typing.Optional[str]=None, source_security_group_owner_id: typing.Optional[str]=None, to_port: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::EC2::SecurityGroupIngress``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            ipProtocol: ``AWS::EC2::SecurityGroupIngress.IpProtocol``.
            cidrIp: ``AWS::EC2::SecurityGroupIngress.CidrIp``.
            cidrIpv6: ``AWS::EC2::SecurityGroupIngress.CidrIpv6``.
            description: ``AWS::EC2::SecurityGroupIngress.Description``.
            fromPort: ``AWS::EC2::SecurityGroupIngress.FromPort``.
            groupId: ``AWS::EC2::SecurityGroupIngress.GroupId``.
            groupName: ``AWS::EC2::SecurityGroupIngress.GroupName``.
            sourcePrefixListId: ``AWS::EC2::SecurityGroupIngress.SourcePrefixListId``.
            sourceSecurityGroupId: ``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupId``.
            sourceSecurityGroupName: ``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupName``.
            sourceSecurityGroupOwnerId: ``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupOwnerId``.
            toPort: ``AWS::EC2::SecurityGroupIngress.ToPort``.

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
    def property_overrides(self) -> "CfnSecurityGroupIngressProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="securityGroupIngressId")
    def security_group_ingress_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupIngressId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSecurityGroupIngressProps(jsii.compat.TypedDict, total=False):
    cidrIp: str
    """``AWS::EC2::SecurityGroupIngress.CidrIp``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-cidrip
    Stability:
        experimental
    """
    cidrIpv6: str
    """``AWS::EC2::SecurityGroupIngress.CidrIpv6``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-cidripv6
    Stability:
        experimental
    """
    description: str
    """``AWS::EC2::SecurityGroupIngress.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-description
    Stability:
        experimental
    """
    fromPort: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::SecurityGroupIngress.FromPort``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-fromport
    Stability:
        experimental
    """
    groupId: str
    """``AWS::EC2::SecurityGroupIngress.GroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-groupid
    Stability:
        experimental
    """
    groupName: str
    """``AWS::EC2::SecurityGroupIngress.GroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-groupname
    Stability:
        experimental
    """
    sourcePrefixListId: str
    """``AWS::EC2::SecurityGroupIngress.SourcePrefixListId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-securitygroupingress-sourceprefixlistid
    Stability:
        experimental
    """
    sourceSecurityGroupId: str
    """``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-sourcesecuritygroupid
    Stability:
        experimental
    """
    sourceSecurityGroupName: str
    """``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-sourcesecuritygroupname
    Stability:
        experimental
    """
    sourceSecurityGroupOwnerId: str
    """``AWS::EC2::SecurityGroupIngress.SourceSecurityGroupOwnerId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-sourcesecuritygroupownerid
    Stability:
        experimental
    """
    toPort: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::SecurityGroupIngress.ToPort``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-toport
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroupIngressProps", jsii_struct_bases=[_CfnSecurityGroupIngressProps])
class CfnSecurityGroupIngressProps(_CfnSecurityGroupIngressProps):
    """Properties for defining a ``AWS::EC2::SecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html
    Stability:
        experimental
    """
    ipProtocol: str
    """``AWS::EC2::SecurityGroupIngress.IpProtocol``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html#cfn-ec2-security-group-ingress-ipprotocol
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSecurityGroupProps(jsii.compat.TypedDict, total=False):
    groupName: str
    """``AWS::EC2::SecurityGroup.GroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-groupname
    Stability:
        experimental
    """
    securityGroupEgress: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSecurityGroup.EgressProperty"]]]
    """``AWS::EC2::SecurityGroup.SecurityGroupEgress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-securitygroupegress
    Stability:
        experimental
    """
    securityGroupIngress: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSecurityGroup.IngressProperty"]]]
    """``AWS::EC2::SecurityGroup.SecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-securitygroupingress
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::SecurityGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-tags
    Stability:
        experimental
    """
    vpcId: str
    """``AWS::EC2::SecurityGroup.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-vpcid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSecurityGroupProps", jsii_struct_bases=[_CfnSecurityGroupProps])
class CfnSecurityGroupProps(_CfnSecurityGroupProps):
    """Properties for defining a ``AWS::EC2::SecurityGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
    Stability:
        experimental
    """
    groupDescription: str
    """``AWS::EC2::SecurityGroup.GroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html#cfn-ec2-securitygroup-groupdescription
    Stability:
        experimental
    """

class CfnSpotFleet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet"):
    """A CloudFormation ``AWS::EC2::SpotFleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-spotfleet.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::SpotFleet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, spot_fleet_request_config_data: typing.Union[aws_cdk.cdk.Token, "SpotFleetRequestConfigDataProperty"]) -> None:
        """Create a new ``AWS::EC2::SpotFleet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            spotFleetRequestConfigData: ``AWS::EC2::SpotFleet.SpotFleetRequestConfigData``.

        Stability:
            experimental
        """
        props: CfnSpotFleetProps = {"spotFleetRequestConfigData": spot_fleet_request_config_data}

        jsii.create(CfnSpotFleet, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSpotFleetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="spotFleetName")
    def spot_fleet_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "spotFleetName")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _BlockDeviceMappingProperty(jsii.compat.TypedDict, total=False):
        ebs: typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.EbsBlockDeviceProperty"]
        """``CfnSpotFleet.BlockDeviceMappingProperty.Ebs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings.html#cfn-ec2-spotfleet-blockdevicemapping-ebs
        Stability:
            experimental
        """
        noDevice: str
        """``CfnSpotFleet.BlockDeviceMappingProperty.NoDevice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings.html#cfn-ec2-spotfleet-blockdevicemapping-nodevice
        Stability:
            experimental
        """
        virtualName: str
        """``CfnSpotFleet.BlockDeviceMappingProperty.VirtualName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings.html#cfn-ec2-spotfleet-blockdevicemapping-virtualname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.BlockDeviceMappingProperty", jsii_struct_bases=[_BlockDeviceMappingProperty])
    class BlockDeviceMappingProperty(_BlockDeviceMappingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings.html
        Stability:
            experimental
        """
        deviceName: str
        """``CfnSpotFleet.BlockDeviceMappingProperty.DeviceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings.html#cfn-ec2-spotfleet-blockdevicemapping-devicename
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.ClassicLoadBalancerProperty", jsii_struct_bases=[])
    class ClassicLoadBalancerProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-classicloadbalancer.html
        Stability:
            experimental
        """
        name: str
        """``CfnSpotFleet.ClassicLoadBalancerProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-classicloadbalancer.html#cfn-ec2-spotfleet-classicloadbalancer-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.ClassicLoadBalancersConfigProperty", jsii_struct_bases=[])
    class ClassicLoadBalancersConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-classicloadbalancersconfig.html
        Stability:
            experimental
        """
        classicLoadBalancers: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.ClassicLoadBalancerProperty"]]]
        """``CfnSpotFleet.ClassicLoadBalancersConfigProperty.ClassicLoadBalancers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-classicloadbalancersconfig.html#cfn-ec2-spotfleet-classicloadbalancersconfig-classicloadbalancers
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.EbsBlockDeviceProperty", jsii_struct_bases=[])
    class EbsBlockDeviceProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html
        Stability:
            experimental
        """
        deleteOnTermination: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnSpotFleet.EbsBlockDeviceProperty.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html#cfn-ec2-spotfleet-ebsblockdevice-deleteontermination
        Stability:
            experimental
        """

        encrypted: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnSpotFleet.EbsBlockDeviceProperty.Encrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html#cfn-ec2-spotfleet-ebsblockdevice-encrypted
        Stability:
            experimental
        """

        iops: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSpotFleet.EbsBlockDeviceProperty.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html#cfn-ec2-spotfleet-ebsblockdevice-iops
        Stability:
            experimental
        """

        snapshotId: str
        """``CfnSpotFleet.EbsBlockDeviceProperty.SnapshotId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html#cfn-ec2-spotfleet-ebsblockdevice-snapshotid
        Stability:
            experimental
        """

        volumeSize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSpotFleet.EbsBlockDeviceProperty.VolumeSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html#cfn-ec2-spotfleet-ebsblockdevice-volumesize
        Stability:
            experimental
        """

        volumeType: str
        """``CfnSpotFleet.EbsBlockDeviceProperty.VolumeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-blockdevicemappings-ebs.html#cfn-ec2-spotfleet-ebsblockdevice-volumetype
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FleetLaunchTemplateSpecificationProperty(jsii.compat.TypedDict, total=False):
        launchTemplateId: str
        """``CfnSpotFleet.FleetLaunchTemplateSpecificationProperty.LaunchTemplateId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-fleetlaunchtemplatespecification.html#cfn-ec2-spotfleet-fleetlaunchtemplatespecification-launchtemplateid
        Stability:
            experimental
        """
        launchTemplateName: str
        """``CfnSpotFleet.FleetLaunchTemplateSpecificationProperty.LaunchTemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-fleetlaunchtemplatespecification.html#cfn-ec2-spotfleet-fleetlaunchtemplatespecification-launchtemplatename
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.FleetLaunchTemplateSpecificationProperty", jsii_struct_bases=[_FleetLaunchTemplateSpecificationProperty])
    class FleetLaunchTemplateSpecificationProperty(_FleetLaunchTemplateSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-fleetlaunchtemplatespecification.html
        Stability:
            experimental
        """
        version: str
        """``CfnSpotFleet.FleetLaunchTemplateSpecificationProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-fleetlaunchtemplatespecification.html#cfn-ec2-spotfleet-fleetlaunchtemplatespecification-version
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.GroupIdentifierProperty", jsii_struct_bases=[])
    class GroupIdentifierProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-securitygroups.html
        Stability:
            experimental
        """
        groupId: str
        """``CfnSpotFleet.GroupIdentifierProperty.GroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-securitygroups.html#cfn-ec2-spotfleet-groupidentifier-groupid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.IamInstanceProfileSpecificationProperty", jsii_struct_bases=[])
    class IamInstanceProfileSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-iaminstanceprofile.html
        Stability:
            experimental
        """
        arn: str
        """``CfnSpotFleet.IamInstanceProfileSpecificationProperty.Arn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-iaminstanceprofile.html#cfn-ec2-spotfleet-iaminstanceprofilespecification-arn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.InstanceIpv6AddressProperty", jsii_struct_bases=[])
    class InstanceIpv6AddressProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-instanceipv6address.html
        Stability:
            experimental
        """
        ipv6Address: str
        """``CfnSpotFleet.InstanceIpv6AddressProperty.Ipv6Address``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-instanceipv6address.html#cfn-ec2-spotfleet-instanceipv6address-ipv6address
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty", jsii_struct_bases=[])
    class InstanceNetworkInterfaceSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html
        Stability:
            experimental
        """
        associatePublicIpAddress: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.AssociatePublicIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-associatepublicipaddress
        Stability:
            experimental
        """

        deleteOnTermination: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.DeleteOnTermination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-deleteontermination
        Stability:
            experimental
        """

        description: str
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-description
        Stability:
            experimental
        """

        deviceIndex: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.DeviceIndex``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-deviceindex
        Stability:
            experimental
        """

        groups: typing.List[str]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.Groups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-groups
        Stability:
            experimental
        """

        ipv6AddressCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.Ipv6AddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-ipv6addresscount
        Stability:
            experimental
        """

        ipv6Addresses: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.InstanceIpv6AddressProperty"]]]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.Ipv6Addresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-ipv6addresses
        Stability:
            experimental
        """

        networkInterfaceId: str
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.NetworkInterfaceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-networkinterfaceid
        Stability:
            experimental
        """

        privateIpAddresses: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.PrivateIpAddressSpecificationProperty"]]]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.PrivateIpAddresses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-privateipaddresses
        Stability:
            experimental
        """

        secondaryPrivateIpAddressCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.SecondaryPrivateIpAddressCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-secondaryprivateipaddresscount
        Stability:
            experimental
        """

        subnetId: str
        """``CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces.html#cfn-ec2-spotfleet-instancenetworkinterfacespecification-subnetid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.LaunchTemplateConfigProperty", jsii_struct_bases=[])
    class LaunchTemplateConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateconfig.html
        Stability:
            experimental
        """
        launchTemplateSpecification: typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.FleetLaunchTemplateSpecificationProperty"]
        """``CfnSpotFleet.LaunchTemplateConfigProperty.LaunchTemplateSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateconfig.html#cfn-ec2-spotfleet-launchtemplateconfig-launchtemplatespecification
        Stability:
            experimental
        """

        overrides: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.LaunchTemplateOverridesProperty"]]]
        """``CfnSpotFleet.LaunchTemplateConfigProperty.Overrides``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateconfig.html#cfn-ec2-spotfleet-launchtemplateconfig-overrides
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.LaunchTemplateOverridesProperty", jsii_struct_bases=[])
    class LaunchTemplateOverridesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateoverrides.html
        Stability:
            experimental
        """
        availabilityZone: str
        """``CfnSpotFleet.LaunchTemplateOverridesProperty.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateoverrides.html#cfn-ec2-spotfleet-launchtemplateoverrides-availabilityzone
        Stability:
            experimental
        """

        instanceType: str
        """``CfnSpotFleet.LaunchTemplateOverridesProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateoverrides.html#cfn-ec2-spotfleet-launchtemplateoverrides-instancetype
        Stability:
            experimental
        """

        spotPrice: str
        """``CfnSpotFleet.LaunchTemplateOverridesProperty.SpotPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateoverrides.html#cfn-ec2-spotfleet-launchtemplateoverrides-spotprice
        Stability:
            experimental
        """

        subnetId: str
        """``CfnSpotFleet.LaunchTemplateOverridesProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateoverrides.html#cfn-ec2-spotfleet-launchtemplateoverrides-subnetid
        Stability:
            experimental
        """

        weightedCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSpotFleet.LaunchTemplateOverridesProperty.WeightedCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-launchtemplateoverrides.html#cfn-ec2-spotfleet-launchtemplateoverrides-weightedcapacity
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.LoadBalancersConfigProperty", jsii_struct_bases=[])
    class LoadBalancersConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-loadbalancersconfig.html
        Stability:
            experimental
        """
        classicLoadBalancersConfig: typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.ClassicLoadBalancersConfigProperty"]
        """``CfnSpotFleet.LoadBalancersConfigProperty.ClassicLoadBalancersConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-loadbalancersconfig.html#cfn-ec2-spotfleet-loadbalancersconfig-classicloadbalancersconfig
        Stability:
            experimental
        """

        targetGroupsConfig: typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.TargetGroupsConfigProperty"]
        """``CfnSpotFleet.LoadBalancersConfigProperty.TargetGroupsConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-loadbalancersconfig.html#cfn-ec2-spotfleet-loadbalancersconfig-targetgroupsconfig
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _PrivateIpAddressSpecificationProperty(jsii.compat.TypedDict, total=False):
        primary: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnSpotFleet.PrivateIpAddressSpecificationProperty.Primary``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces-privateipaddresses.html#cfn-ec2-spotfleet-privateipaddressspecification-primary
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.PrivateIpAddressSpecificationProperty", jsii_struct_bases=[_PrivateIpAddressSpecificationProperty])
    class PrivateIpAddressSpecificationProperty(_PrivateIpAddressSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces-privateipaddresses.html
        Stability:
            experimental
        """
        privateIpAddress: str
        """``CfnSpotFleet.PrivateIpAddressSpecificationProperty.PrivateIpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-networkinterfaces-privateipaddresses.html#cfn-ec2-spotfleet-privateipaddressspecification-privateipaddress
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SpotFleetLaunchSpecificationProperty(jsii.compat.TypedDict, total=False):
        blockDeviceMappings: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.BlockDeviceMappingProperty"]]]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.BlockDeviceMappings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-blockdevicemappings
        Stability:
            experimental
        """
        ebsOptimized: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.EbsOptimized``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-ebsoptimized
        Stability:
            experimental
        """
        iamInstanceProfile: typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.IamInstanceProfileSpecificationProperty"]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.IamInstanceProfile``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-iaminstanceprofile
        Stability:
            experimental
        """
        kernelId: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.KernelId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-kernelid
        Stability:
            experimental
        """
        keyName: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.KeyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-keyname
        Stability:
            experimental
        """
        monitoring: typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.SpotFleetMonitoringProperty"]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.Monitoring``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-monitoring
        Stability:
            experimental
        """
        networkInterfaces: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.InstanceNetworkInterfaceSpecificationProperty"]]]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.NetworkInterfaces``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-networkinterfaces
        Stability:
            experimental
        """
        placement: typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.SpotPlacementProperty"]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.Placement``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-placement
        Stability:
            experimental
        """
        ramdiskId: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.RamdiskId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-ramdiskid
        Stability:
            experimental
        """
        securityGroups: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.GroupIdentifierProperty"]]]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.SecurityGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-securitygroups
        Stability:
            experimental
        """
        spotPrice: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.SpotPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-spotprice
        Stability:
            experimental
        """
        subnetId: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-subnetid
        Stability:
            experimental
        """
        tagSpecifications: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.SpotFleetTagSpecificationProperty"]]]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.TagSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-tagspecifications
        Stability:
            experimental
        """
        userData: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.UserData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-userdata
        Stability:
            experimental
        """
        weightedCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.WeightedCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-weightedcapacity
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.SpotFleetLaunchSpecificationProperty", jsii_struct_bases=[_SpotFleetLaunchSpecificationProperty])
    class SpotFleetLaunchSpecificationProperty(_SpotFleetLaunchSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html
        Stability:
            experimental
        """
        imageId: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.ImageId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-imageid
        Stability:
            experimental
        """

        instanceType: str
        """``CfnSpotFleet.SpotFleetLaunchSpecificationProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications.html#cfn-ec2-spotfleet-spotfleetlaunchspecification-instancetype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.SpotFleetMonitoringProperty", jsii_struct_bases=[])
    class SpotFleetMonitoringProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-monitoring.html
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnSpotFleet.SpotFleetMonitoringProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-monitoring.html#cfn-ec2-spotfleet-spotfleetmonitoring-enabled
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SpotFleetRequestConfigDataProperty(jsii.compat.TypedDict, total=False):
        allocationStrategy: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.AllocationStrategy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-allocationstrategy
        Stability:
            experimental
        """
        excessCapacityTerminationPolicy: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.ExcessCapacityTerminationPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-excesscapacityterminationpolicy
        Stability:
            experimental
        """
        instanceInterruptionBehavior: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.InstanceInterruptionBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-instanceinterruptionbehavior
        Stability:
            experimental
        """
        launchSpecifications: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.SpotFleetLaunchSpecificationProperty"]]]
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.LaunchSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications
        Stability:
            experimental
        """
        launchTemplateConfigs: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.LaunchTemplateConfigProperty"]]]
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.LaunchTemplateConfigs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-launchtemplateconfigs
        Stability:
            experimental
        """
        loadBalancersConfig: typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.LoadBalancersConfigProperty"]
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.LoadBalancersConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-loadbalancersconfig
        Stability:
            experimental
        """
        replaceUnhealthyInstances: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.ReplaceUnhealthyInstances``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-replaceunhealthyinstances
        Stability:
            experimental
        """
        spotPrice: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.SpotPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-spotprice
        Stability:
            experimental
        """
        terminateInstancesWithExpiration: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.TerminateInstancesWithExpiration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-terminateinstanceswithexpiration
        Stability:
            experimental
        """
        type: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-type
        Stability:
            experimental
        """
        validFrom: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.ValidFrom``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-validfrom
        Stability:
            experimental
        """
        validUntil: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.ValidUntil``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-validuntil
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.SpotFleetRequestConfigDataProperty", jsii_struct_bases=[_SpotFleetRequestConfigDataProperty])
    class SpotFleetRequestConfigDataProperty(_SpotFleetRequestConfigDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html
        Stability:
            experimental
        """
        iamFleetRole: str
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.IamFleetRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-iamfleetrole
        Stability:
            experimental
        """

        targetCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSpotFleet.SpotFleetRequestConfigDataProperty.TargetCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata-targetcapacity
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.SpotFleetTagSpecificationProperty", jsii_struct_bases=[])
    class SpotFleetTagSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-tagspecifications.html
        Stability:
            experimental
        """
        resourceType: str
        """``CfnSpotFleet.SpotFleetTagSpecificationProperty.ResourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-tagspecifications.html#cfn-ec2-spotfleet-spotfleettagspecification-resourcetype
        Stability:
            experimental
        """

        tags: typing.List[aws_cdk.cdk.CfnTag]
        """``CfnSpotFleet.SpotFleetTagSpecificationProperty.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-tagspecifications.html#cfn-ec2-spotfleet-tags
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.SpotPlacementProperty", jsii_struct_bases=[])
    class SpotPlacementProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-placement.html
        Stability:
            experimental
        """
        availabilityZone: str
        """``CfnSpotFleet.SpotPlacementProperty.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-placement.html#cfn-ec2-spotfleet-spotplacement-availabilityzone
        Stability:
            experimental
        """

        groupName: str
        """``CfnSpotFleet.SpotPlacementProperty.GroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-placement.html#cfn-ec2-spotfleet-spotplacement-groupname
        Stability:
            experimental
        """

        tenancy: str
        """``CfnSpotFleet.SpotPlacementProperty.Tenancy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-placement.html#cfn-ec2-spotfleet-spotplacement-tenancy
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.TargetGroupProperty", jsii_struct_bases=[])
    class TargetGroupProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-targetgroup.html
        Stability:
            experimental
        """
        arn: str
        """``CfnSpotFleet.TargetGroupProperty.Arn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-targetgroup.html#cfn-ec2-spotfleet-targetgroup-arn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleet.TargetGroupsConfigProperty", jsii_struct_bases=[])
    class TargetGroupsConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-targetgroupsconfig.html
        Stability:
            experimental
        """
        targetGroups: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.TargetGroupProperty"]]]
        """``CfnSpotFleet.TargetGroupsConfigProperty.TargetGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-targetgroupsconfig.html#cfn-ec2-spotfleet-targetgroupsconfig-targetgroups
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSpotFleetProps", jsii_struct_bases=[])
class CfnSpotFleetProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::SpotFleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-spotfleet.html
    Stability:
        experimental
    """
    spotFleetRequestConfigData: typing.Union[aws_cdk.cdk.Token, "CfnSpotFleet.SpotFleetRequestConfigDataProperty"]
    """``AWS::EC2::SpotFleet.SpotFleetRequestConfigData``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-spotfleet.html#cfn-ec2-spotfleet-spotfleetrequestconfigdata
    Stability:
        experimental
    """

class CfnSubnet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSubnet"):
    """A CloudFormation ``AWS::EC2::Subnet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::Subnet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cidr_block: str, vpc_id: str, assign_ipv6_address_on_creation: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, availability_zone: typing.Optional[str]=None, ipv6_cidr_block: typing.Optional[str]=None, map_public_ip_on_launch: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::Subnet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            cidrBlock: ``AWS::EC2::Subnet.CidrBlock``.
            vpcId: ``AWS::EC2::Subnet.VpcId``.
            assignIpv6AddressOnCreation: ``AWS::EC2::Subnet.AssignIpv6AddressOnCreation``.
            availabilityZone: ``AWS::EC2::Subnet.AvailabilityZone``.
            ipv6CidrBlock: ``AWS::EC2::Subnet.Ipv6CidrBlock``.
            mapPublicIpOnLaunch: ``AWS::EC2::Subnet.MapPublicIpOnLaunch``.
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
    def property_overrides(self) -> "CfnSubnetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="subnetAvailabilityZone")
    def subnet_availability_zone(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            AvailabilityZone
        """
        return jsii.get(self, "subnetAvailabilityZone")

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        """
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
        cloudformationAttribute:
            Ipv6CidrBlocks
        """
        return jsii.get(self, "subnetIpv6CidrBlocks")

    @property
    @jsii.member(jsii_name="subnetNetworkAclAssociationId")
    def subnet_network_acl_association_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            NetworkAclAssociationId
        """
        return jsii.get(self, "subnetNetworkAclAssociationId")

    @property
    @jsii.member(jsii_name="subnetVpcId")
    def subnet_vpc_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            VpcId
        """
        return jsii.get(self, "subnetVpcId")

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


class CfnSubnetCidrBlock(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSubnetCidrBlock"):
    """A CloudFormation ``AWS::EC2::SubnetCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnetcidrblock.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::SubnetCidrBlock
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, ipv6_cidr_block: str, subnet_id: str) -> None:
        """Create a new ``AWS::EC2::SubnetCidrBlock``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            ipv6CidrBlock: ``AWS::EC2::SubnetCidrBlock.Ipv6CidrBlock``.
            subnetId: ``AWS::EC2::SubnetCidrBlock.SubnetId``.

        Stability:
            experimental
        """
        props: CfnSubnetCidrBlockProps = {"ipv6CidrBlock": ipv6_cidr_block, "subnetId": subnet_id}

        jsii.create(CfnSubnetCidrBlock, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSubnetCidrBlockProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="subnetCidrBlockId")
    def subnet_cidr_block_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "subnetCidrBlockId")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSubnetCidrBlockProps", jsii_struct_bases=[])
class CfnSubnetCidrBlockProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::SubnetCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnetcidrblock.html
    Stability:
        experimental
    """
    ipv6CidrBlock: str
    """``AWS::EC2::SubnetCidrBlock.Ipv6CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnetcidrblock.html#cfn-ec2-subnetcidrblock-ipv6cidrblock
    Stability:
        experimental
    """

    subnetId: str
    """``AWS::EC2::SubnetCidrBlock.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnetcidrblock.html#cfn-ec2-subnetcidrblock-subnetid
    Stability:
        experimental
    """

class CfnSubnetNetworkAclAssociation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSubnetNetworkAclAssociation"):
    """A CloudFormation ``AWS::EC2::SubnetNetworkAclAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-network-acl-assoc.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::SubnetNetworkAclAssociation
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, network_acl_id: str, subnet_id: str) -> None:
        """Create a new ``AWS::EC2::SubnetNetworkAclAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            networkAclId: ``AWS::EC2::SubnetNetworkAclAssociation.NetworkAclId``.
            subnetId: ``AWS::EC2::SubnetNetworkAclAssociation.SubnetId``.

        Stability:
            experimental
        """
        props: CfnSubnetNetworkAclAssociationProps = {"networkAclId": network_acl_id, "subnetId": subnet_id}

        jsii.create(CfnSubnetNetworkAclAssociation, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSubnetNetworkAclAssociationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="subnetNetworkAclAssociationAssociationId")
    def subnet_network_acl_association_association_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            AssociationId
        """
        return jsii.get(self, "subnetNetworkAclAssociationAssociationId")

    @property
    @jsii.member(jsii_name="subnetNetworkAclAssociationName")
    def subnet_network_acl_association_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "subnetNetworkAclAssociationName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSubnetNetworkAclAssociationProps", jsii_struct_bases=[])
class CfnSubnetNetworkAclAssociationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::SubnetNetworkAclAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-network-acl-assoc.html
    Stability:
        experimental
    """
    networkAclId: str
    """``AWS::EC2::SubnetNetworkAclAssociation.NetworkAclId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-network-acl-assoc.html#cfn-ec2-subnetnetworkaclassociation-networkaclid
    Stability:
        experimental
    """

    subnetId: str
    """``AWS::EC2::SubnetNetworkAclAssociation.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-network-acl-assoc.html#cfn-ec2-subnetnetworkaclassociation-associationid
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSubnetProps(jsii.compat.TypedDict, total=False):
    assignIpv6AddressOnCreation: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::Subnet.AssignIpv6AddressOnCreation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-assignipv6addressoncreation
    Stability:
        experimental
    """
    availabilityZone: str
    """``AWS::EC2::Subnet.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-availabilityzone
    Stability:
        experimental
    """
    ipv6CidrBlock: str
    """``AWS::EC2::Subnet.Ipv6CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-ipv6cidrblock
    Stability:
        experimental
    """
    mapPublicIpOnLaunch: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::Subnet.MapPublicIpOnLaunch``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-mappubliciponlaunch
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::Subnet.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSubnetProps", jsii_struct_bases=[_CfnSubnetProps])
class CfnSubnetProps(_CfnSubnetProps):
    """Properties for defining a ``AWS::EC2::Subnet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html
    Stability:
        experimental
    """
    cidrBlock: str
    """``AWS::EC2::Subnet.CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-ec2-subnet-cidrblock
    Stability:
        experimental
    """

    vpcId: str
    """``AWS::EC2::Subnet.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html#cfn-awsec2subnet-prop-vpcid
    Stability:
        experimental
    """

class CfnSubnetRouteTableAssociation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnSubnetRouteTableAssociation"):
    """A CloudFormation ``AWS::EC2::SubnetRouteTableAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::SubnetRouteTableAssociation
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, route_table_id: str, subnet_id: str) -> None:
        """Create a new ``AWS::EC2::SubnetRouteTableAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            routeTableId: ``AWS::EC2::SubnetRouteTableAssociation.RouteTableId``.
            subnetId: ``AWS::EC2::SubnetRouteTableAssociation.SubnetId``.

        Stability:
            experimental
        """
        props: CfnSubnetRouteTableAssociationProps = {"routeTableId": route_table_id, "subnetId": subnet_id}

        jsii.create(CfnSubnetRouteTableAssociation, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSubnetRouteTableAssociationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="subnetRouteTableAssociationName")
    def subnet_route_table_association_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "subnetRouteTableAssociationName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnSubnetRouteTableAssociationProps", jsii_struct_bases=[])
class CfnSubnetRouteTableAssociationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::SubnetRouteTableAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html
    Stability:
        experimental
    """
    routeTableId: str
    """``AWS::EC2::SubnetRouteTableAssociation.RouteTableId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html#cfn-ec2-subnetroutetableassociation-routetableid
    Stability:
        experimental
    """

    subnetId: str
    """``AWS::EC2::SubnetRouteTableAssociation.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html#cfn-ec2-subnetroutetableassociation-subnetid
    Stability:
        experimental
    """

class CfnTransitGateway(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnTransitGateway"):
    """A CloudFormation ``AWS::EC2::TransitGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::TransitGateway
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, amazon_side_asn: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, auto_accept_shared_attachments: typing.Optional[str]=None, default_route_table_association: typing.Optional[str]=None, default_route_table_propagation: typing.Optional[str]=None, description: typing.Optional[str]=None, dns_support: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpn_ecmp_support: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::TransitGateway``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            amazonSideAsn: ``AWS::EC2::TransitGateway.AmazonSideAsn``.
            autoAcceptSharedAttachments: ``AWS::EC2::TransitGateway.AutoAcceptSharedAttachments``.
            defaultRouteTableAssociation: ``AWS::EC2::TransitGateway.DefaultRouteTableAssociation``.
            defaultRouteTablePropagation: ``AWS::EC2::TransitGateway.DefaultRouteTablePropagation``.
            description: ``AWS::EC2::TransitGateway.Description``.
            dnsSupport: ``AWS::EC2::TransitGateway.DnsSupport``.
            tags: ``AWS::EC2::TransitGateway.Tags``.
            vpnEcmpSupport: ``AWS::EC2::TransitGateway.VpnEcmpSupport``.

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
    def property_overrides(self) -> "CfnTransitGatewayProps":
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

    @property
    @jsii.member(jsii_name="transitGatewayId")
    def transit_gateway_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "transitGatewayId")


class CfnTransitGatewayAttachment(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayAttachment"):
    """A CloudFormation ``AWS::EC2::TransitGatewayAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::TransitGatewayAttachment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, subnet_ids: typing.List[str], transit_gateway_id: str, vpc_id: str, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::TransitGatewayAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            subnetIds: ``AWS::EC2::TransitGatewayAttachment.SubnetIds``.
            transitGatewayId: ``AWS::EC2::TransitGatewayAttachment.TransitGatewayId``.
            vpcId: ``AWS::EC2::TransitGatewayAttachment.VpcId``.
            tags: ``AWS::EC2::TransitGatewayAttachment.Tags``.

        Stability:
            experimental
        """
        props: CfnTransitGatewayAttachmentProps = {"subnetIds": subnet_ids, "transitGatewayId": transit_gateway_id, "vpcId": vpc_id}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnTransitGatewayAttachment, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnTransitGatewayAttachmentProps":
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

    @property
    @jsii.member(jsii_name="transitGatewayAttachmentId")
    def transit_gateway_attachment_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "transitGatewayAttachmentId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnTransitGatewayAttachmentProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::TransitGatewayAttachment.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html#cfn-ec2-transitgatewayattachment-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayAttachmentProps", jsii_struct_bases=[_CfnTransitGatewayAttachmentProps])
class CfnTransitGatewayAttachmentProps(_CfnTransitGatewayAttachmentProps):
    """Properties for defining a ``AWS::EC2::TransitGatewayAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html
    Stability:
        experimental
    """
    subnetIds: typing.List[str]
    """``AWS::EC2::TransitGatewayAttachment.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html#cfn-ec2-transitgatewayattachment-subnetids
    Stability:
        experimental
    """

    transitGatewayId: str
    """``AWS::EC2::TransitGatewayAttachment.TransitGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html#cfn-ec2-transitgatewayattachment-transitgatewayid
    Stability:
        experimental
    """

    vpcId: str
    """``AWS::EC2::TransitGatewayAttachment.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayattachment.html#cfn-ec2-transitgatewayattachment-vpcid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayProps", jsii_struct_bases=[])
class CfnTransitGatewayProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EC2::TransitGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html
    Stability:
        experimental
    """
    amazonSideAsn: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::TransitGateway.AmazonSideAsn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-amazonsideasn
    Stability:
        experimental
    """

    autoAcceptSharedAttachments: str
    """``AWS::EC2::TransitGateway.AutoAcceptSharedAttachments``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-autoacceptsharedattachments
    Stability:
        experimental
    """

    defaultRouteTableAssociation: str
    """``AWS::EC2::TransitGateway.DefaultRouteTableAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-defaultroutetableassociation
    Stability:
        experimental
    """

    defaultRouteTablePropagation: str
    """``AWS::EC2::TransitGateway.DefaultRouteTablePropagation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-defaultroutetablepropagation
    Stability:
        experimental
    """

    description: str
    """``AWS::EC2::TransitGateway.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-description
    Stability:
        experimental
    """

    dnsSupport: str
    """``AWS::EC2::TransitGateway.DnsSupport``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-dnssupport
    Stability:
        experimental
    """

    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::TransitGateway.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-tags
    Stability:
        experimental
    """

    vpnEcmpSupport: str
    """``AWS::EC2::TransitGateway.VpnEcmpSupport``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgateway.html#cfn-ec2-transitgateway-vpnecmpsupport
    Stability:
        experimental
    """

class CfnTransitGatewayRoute(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRoute"):
    """A CloudFormation ``AWS::EC2::TransitGatewayRoute``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::TransitGatewayRoute
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, transit_gateway_route_table_id: str, blackhole: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, destination_cidr_block: typing.Optional[str]=None, transit_gateway_attachment_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::TransitGatewayRoute``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            transitGatewayRouteTableId: ``AWS::EC2::TransitGatewayRoute.TransitGatewayRouteTableId``.
            blackhole: ``AWS::EC2::TransitGatewayRoute.Blackhole``.
            destinationCidrBlock: ``AWS::EC2::TransitGatewayRoute.DestinationCidrBlock``.
            transitGatewayAttachmentId: ``AWS::EC2::TransitGatewayRoute.TransitGatewayAttachmentId``.

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
    def property_overrides(self) -> "CfnTransitGatewayRouteProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="transitGatewayRouteId")
    def transit_gateway_route_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "transitGatewayRouteId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnTransitGatewayRouteProps(jsii.compat.TypedDict, total=False):
    blackhole: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::TransitGatewayRoute.Blackhole``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html#cfn-ec2-transitgatewayroute-blackhole
    Stability:
        experimental
    """
    destinationCidrBlock: str
    """``AWS::EC2::TransitGatewayRoute.DestinationCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html#cfn-ec2-transitgatewayroute-destinationcidrblock
    Stability:
        experimental
    """
    transitGatewayAttachmentId: str
    """``AWS::EC2::TransitGatewayRoute.TransitGatewayAttachmentId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html#cfn-ec2-transitgatewayroute-transitgatewayattachmentid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteProps", jsii_struct_bases=[_CfnTransitGatewayRouteProps])
class CfnTransitGatewayRouteProps(_CfnTransitGatewayRouteProps):
    """Properties for defining a ``AWS::EC2::TransitGatewayRoute``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html
    Stability:
        experimental
    """
    transitGatewayRouteTableId: str
    """``AWS::EC2::TransitGatewayRoute.TransitGatewayRouteTableId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroute.html#cfn-ec2-transitgatewayroute-transitgatewayroutetableid
    Stability:
        experimental
    """

class CfnTransitGatewayRouteTable(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteTable"):
    """A CloudFormation ``AWS::EC2::TransitGatewayRouteTable``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetable.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::TransitGatewayRouteTable
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, transit_gateway_id: str, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::TransitGatewayRouteTable``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            transitGatewayId: ``AWS::EC2::TransitGatewayRouteTable.TransitGatewayId``.
            tags: ``AWS::EC2::TransitGatewayRouteTable.Tags``.

        Stability:
            experimental
        """
        props: CfnTransitGatewayRouteTableProps = {"transitGatewayId": transit_gateway_id}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnTransitGatewayRouteTable, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnTransitGatewayRouteTableProps":
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

    @property
    @jsii.member(jsii_name="transitGatewayRouteTableId")
    def transit_gateway_route_table_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "transitGatewayRouteTableId")


class CfnTransitGatewayRouteTableAssociation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteTableAssociation"):
    """A CloudFormation ``AWS::EC2::TransitGatewayRouteTableAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetableassociation.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::TransitGatewayRouteTableAssociation
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, transit_gateway_attachment_id: str, transit_gateway_route_table_id: str) -> None:
        """Create a new ``AWS::EC2::TransitGatewayRouteTableAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            transitGatewayAttachmentId: ``AWS::EC2::TransitGatewayRouteTableAssociation.TransitGatewayAttachmentId``.
            transitGatewayRouteTableId: ``AWS::EC2::TransitGatewayRouteTableAssociation.TransitGatewayRouteTableId``.

        Stability:
            experimental
        """
        props: CfnTransitGatewayRouteTableAssociationProps = {"transitGatewayAttachmentId": transit_gateway_attachment_id, "transitGatewayRouteTableId": transit_gateway_route_table_id}

        jsii.create(CfnTransitGatewayRouteTableAssociation, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnTransitGatewayRouteTableAssociationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="transitGatewayRouteTableAssociationId")
    def transit_gateway_route_table_association_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "transitGatewayRouteTableAssociationId")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteTableAssociationProps", jsii_struct_bases=[])
class CfnTransitGatewayRouteTableAssociationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::TransitGatewayRouteTableAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetableassociation.html
    Stability:
        experimental
    """
    transitGatewayAttachmentId: str
    """``AWS::EC2::TransitGatewayRouteTableAssociation.TransitGatewayAttachmentId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetableassociation.html#cfn-ec2-transitgatewayroutetableassociation-transitgatewayattachmentid
    Stability:
        experimental
    """

    transitGatewayRouteTableId: str
    """``AWS::EC2::TransitGatewayRouteTableAssociation.TransitGatewayRouteTableId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetableassociation.html#cfn-ec2-transitgatewayroutetableassociation-transitgatewayroutetableid
    Stability:
        experimental
    """

class CfnTransitGatewayRouteTablePropagation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteTablePropagation"):
    """A CloudFormation ``AWS::EC2::TransitGatewayRouteTablePropagation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetablepropagation.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::TransitGatewayRouteTablePropagation
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, transit_gateway_attachment_id: str, transit_gateway_route_table_id: str) -> None:
        """Create a new ``AWS::EC2::TransitGatewayRouteTablePropagation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            transitGatewayAttachmentId: ``AWS::EC2::TransitGatewayRouteTablePropagation.TransitGatewayAttachmentId``.
            transitGatewayRouteTableId: ``AWS::EC2::TransitGatewayRouteTablePropagation.TransitGatewayRouteTableId``.

        Stability:
            experimental
        """
        props: CfnTransitGatewayRouteTablePropagationProps = {"transitGatewayAttachmentId": transit_gateway_attachment_id, "transitGatewayRouteTableId": transit_gateway_route_table_id}

        jsii.create(CfnTransitGatewayRouteTablePropagation, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnTransitGatewayRouteTablePropagationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="transitGatewayRouteTablePropagationId")
    def transit_gateway_route_table_propagation_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "transitGatewayRouteTablePropagationId")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteTablePropagationProps", jsii_struct_bases=[])
class CfnTransitGatewayRouteTablePropagationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::TransitGatewayRouteTablePropagation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetablepropagation.html
    Stability:
        experimental
    """
    transitGatewayAttachmentId: str
    """``AWS::EC2::TransitGatewayRouteTablePropagation.TransitGatewayAttachmentId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetablepropagation.html#cfn-ec2-transitgatewayroutetablepropagation-transitgatewayattachmentid
    Stability:
        experimental
    """

    transitGatewayRouteTableId: str
    """``AWS::EC2::TransitGatewayRouteTablePropagation.TransitGatewayRouteTableId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetablepropagation.html#cfn-ec2-transitgatewayroutetablepropagation-transitgatewayroutetableid
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnTransitGatewayRouteTableProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::TransitGatewayRouteTable.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetable.html#cfn-ec2-transitgatewayroutetable-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnTransitGatewayRouteTableProps", jsii_struct_bases=[_CfnTransitGatewayRouteTableProps])
class CfnTransitGatewayRouteTableProps(_CfnTransitGatewayRouteTableProps):
    """Properties for defining a ``AWS::EC2::TransitGatewayRouteTable``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetable.html
    Stability:
        experimental
    """
    transitGatewayId: str
    """``AWS::EC2::TransitGatewayRouteTable.TransitGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-transitgatewayroutetable.html#cfn-ec2-transitgatewayroutetable-transitgatewayid
    Stability:
        experimental
    """

class CfnVPC(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPC"):
    """A CloudFormation ``AWS::EC2::VPC``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPC
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cidr_block: str, enable_dns_hostnames: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, enable_dns_support: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, instance_tenancy: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::VPC``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            cidrBlock: ``AWS::EC2::VPC.CidrBlock``.
            enableDnsHostnames: ``AWS::EC2::VPC.EnableDnsHostnames``.
            enableDnsSupport: ``AWS::EC2::VPC.EnableDnsSupport``.
            instanceTenancy: ``AWS::EC2::VPC.InstanceTenancy``.
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
    def property_overrides(self) -> "CfnVPCProps":
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

    @property
    @jsii.member(jsii_name="vpcCidrBlock")
    def vpc_cidr_block(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            CidrBlock
        """
        return jsii.get(self, "vpcCidrBlock")

    @property
    @jsii.member(jsii_name="vpcCidrBlockAssociations")
    def vpc_cidr_block_associations(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            CidrBlockAssociations
        """
        return jsii.get(self, "vpcCidrBlockAssociations")

    @property
    @jsii.member(jsii_name="vpcDefaultNetworkAcl")
    def vpc_default_network_acl(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DefaultNetworkAcl
        """
        return jsii.get(self, "vpcDefaultNetworkAcl")

    @property
    @jsii.member(jsii_name="vpcDefaultSecurityGroup")
    def vpc_default_security_group(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DefaultSecurityGroup
        """
        return jsii.get(self, "vpcDefaultSecurityGroup")

    @property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        """
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
        cloudformationAttribute:
            Ipv6CidrBlocks
        """
        return jsii.get(self, "vpcIpv6CidrBlocks")


class CfnVPCCidrBlock(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCCidrBlock"):
    """A CloudFormation ``AWS::EC2::VPCCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPCCidrBlock
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc_id: str, amazon_provided_ipv6_cidr_block: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, cidr_block: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::VPCCidrBlock``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            vpcId: ``AWS::EC2::VPCCidrBlock.VpcId``.
            amazonProvidedIpv6CidrBlock: ``AWS::EC2::VPCCidrBlock.AmazonProvidedIpv6CidrBlock``.
            cidrBlock: ``AWS::EC2::VPCCidrBlock.CidrBlock``.

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
    def property_overrides(self) -> "CfnVPCCidrBlockProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="vpcCidrBlockId")
    def vpc_cidr_block_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpcCidrBlockId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCCidrBlockProps(jsii.compat.TypedDict, total=False):
    amazonProvidedIpv6CidrBlock: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::VPCCidrBlock.AmazonProvidedIpv6CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html#cfn-ec2-vpccidrblock-amazonprovidedipv6cidrblock
    Stability:
        experimental
    """
    cidrBlock: str
    """``AWS::EC2::VPCCidrBlock.CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html#cfn-ec2-vpccidrblock-cidrblock
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCCidrBlockProps", jsii_struct_bases=[_CfnVPCCidrBlockProps])
class CfnVPCCidrBlockProps(_CfnVPCCidrBlockProps):
    """Properties for defining a ``AWS::EC2::VPCCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html
    Stability:
        experimental
    """
    vpcId: str
    """``AWS::EC2::VPCCidrBlock.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpccidrblock.html#cfn-ec2-vpccidrblock-vpcid
    Stability:
        experimental
    """

class CfnVPCDHCPOptionsAssociation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCDHCPOptionsAssociation"):
    """A CloudFormation ``AWS::EC2::VPCDHCPOptionsAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-dhcp-options-assoc.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPCDHCPOptionsAssociation
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, dhcp_options_id: str, vpc_id: str) -> None:
        """Create a new ``AWS::EC2::VPCDHCPOptionsAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            dhcpOptionsId: ``AWS::EC2::VPCDHCPOptionsAssociation.DhcpOptionsId``.
            vpcId: ``AWS::EC2::VPCDHCPOptionsAssociation.VpcId``.

        Stability:
            experimental
        """
        props: CfnVPCDHCPOptionsAssociationProps = {"dhcpOptionsId": dhcp_options_id, "vpcId": vpc_id}

        jsii.create(CfnVPCDHCPOptionsAssociation, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnVPCDHCPOptionsAssociationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="vpcdhcpOptionsAssociationName")
    def vpcdhcp_options_association_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpcdhcpOptionsAssociationName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCDHCPOptionsAssociationProps", jsii_struct_bases=[])
class CfnVPCDHCPOptionsAssociationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::VPCDHCPOptionsAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-dhcp-options-assoc.html
    Stability:
        experimental
    """
    dhcpOptionsId: str
    """``AWS::EC2::VPCDHCPOptionsAssociation.DhcpOptionsId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-dhcp-options-assoc.html#cfn-ec2-vpcdhcpoptionsassociation-dhcpoptionsid
    Stability:
        experimental
    """

    vpcId: str
    """``AWS::EC2::VPCDHCPOptionsAssociation.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-dhcp-options-assoc.html#cfn-ec2-vpcdhcpoptionsassociation-vpcid
    Stability:
        experimental
    """

class CfnVPCEndpoint(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpoint"):
    """A CloudFormation ``AWS::EC2::VPCEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPCEndpoint
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, service_name: str, vpc_id: str, policy_document: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, private_dns_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, route_table_ids: typing.Optional[typing.List[str]]=None, security_group_ids: typing.Optional[typing.List[str]]=None, subnet_ids: typing.Optional[typing.List[str]]=None, vpc_endpoint_type: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::VPCEndpoint``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            serviceName: ``AWS::EC2::VPCEndpoint.ServiceName``.
            vpcId: ``AWS::EC2::VPCEndpoint.VpcId``.
            policyDocument: ``AWS::EC2::VPCEndpoint.PolicyDocument``.
            privateDnsEnabled: ``AWS::EC2::VPCEndpoint.PrivateDnsEnabled``.
            routeTableIds: ``AWS::EC2::VPCEndpoint.RouteTableIds``.
            securityGroupIds: ``AWS::EC2::VPCEndpoint.SecurityGroupIds``.
            subnetIds: ``AWS::EC2::VPCEndpoint.SubnetIds``.
            vpcEndpointType: ``AWS::EC2::VPCEndpoint.VpcEndpointType``.

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
    def property_overrides(self) -> "CfnVPCEndpointProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="vpcEndpointCreationTimestamp")
    def vpc_endpoint_creation_timestamp(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            CreationTimestamp
        """
        return jsii.get(self, "vpcEndpointCreationTimestamp")

    @property
    @jsii.member(jsii_name="vpcEndpointDnsEntries")
    def vpc_endpoint_dns_entries(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DnsEntries
        """
        return jsii.get(self, "vpcEndpointDnsEntries")

    @property
    @jsii.member(jsii_name="vpcEndpointId")
    def vpc_endpoint_id(self) -> str:
        """
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
        cloudformationAttribute:
            NetworkInterfaceIds
        """
        return jsii.get(self, "vpcEndpointNetworkInterfaceIds")


class CfnVPCEndpointConnectionNotification(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointConnectionNotification"):
    """A CloudFormation ``AWS::EC2::VPCEndpointConnectionNotification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPCEndpointConnectionNotification
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, connection_events: typing.List[str], connection_notification_arn: str, service_id: typing.Optional[str]=None, vpc_endpoint_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::VPCEndpointConnectionNotification``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            connectionEvents: ``AWS::EC2::VPCEndpointConnectionNotification.ConnectionEvents``.
            connectionNotificationArn: ``AWS::EC2::VPCEndpointConnectionNotification.ConnectionNotificationArn``.
            serviceId: ``AWS::EC2::VPCEndpointConnectionNotification.ServiceId``.
            vpcEndpointId: ``AWS::EC2::VPCEndpointConnectionNotification.VPCEndpointId``.

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
    def property_overrides(self) -> "CfnVPCEndpointConnectionNotificationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCEndpointConnectionNotificationProps(jsii.compat.TypedDict, total=False):
    serviceId: str
    """``AWS::EC2::VPCEndpointConnectionNotification.ServiceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html#cfn-ec2-vpcendpointconnectionnotification-serviceid
    Stability:
        experimental
    """
    vpcEndpointId: str
    """``AWS::EC2::VPCEndpointConnectionNotification.VPCEndpointId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html#cfn-ec2-vpcendpointconnectionnotification-vpcendpointid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointConnectionNotificationProps", jsii_struct_bases=[_CfnVPCEndpointConnectionNotificationProps])
class CfnVPCEndpointConnectionNotificationProps(_CfnVPCEndpointConnectionNotificationProps):
    """Properties for defining a ``AWS::EC2::VPCEndpointConnectionNotification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html
    Stability:
        experimental
    """
    connectionEvents: typing.List[str]
    """``AWS::EC2::VPCEndpointConnectionNotification.ConnectionEvents``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html#cfn-ec2-vpcendpointconnectionnotification-connectionevents
    Stability:
        experimental
    """

    connectionNotificationArn: str
    """``AWS::EC2::VPCEndpointConnectionNotification.ConnectionNotificationArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointconnectionnotification.html#cfn-ec2-vpcendpointconnectionnotification-connectionnotificationarn
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCEndpointProps(jsii.compat.TypedDict, total=False):
    policyDocument: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::EC2::VPCEndpoint.PolicyDocument``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-policydocument
    Stability:
        experimental
    """
    privateDnsEnabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::VPCEndpoint.PrivateDnsEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-privatednsenabled
    Stability:
        experimental
    """
    routeTableIds: typing.List[str]
    """``AWS::EC2::VPCEndpoint.RouteTableIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-routetableids
    Stability:
        experimental
    """
    securityGroupIds: typing.List[str]
    """``AWS::EC2::VPCEndpoint.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-securitygroupids
    Stability:
        experimental
    """
    subnetIds: typing.List[str]
    """``AWS::EC2::VPCEndpoint.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-subnetids
    Stability:
        experimental
    """
    vpcEndpointType: str
    """``AWS::EC2::VPCEndpoint.VpcEndpointType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-vpcendpointtype
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointProps", jsii_struct_bases=[_CfnVPCEndpointProps])
class CfnVPCEndpointProps(_CfnVPCEndpointProps):
    """Properties for defining a ``AWS::EC2::VPCEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html
    Stability:
        experimental
    """
    serviceName: str
    """``AWS::EC2::VPCEndpoint.ServiceName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-servicename
    Stability:
        experimental
    """

    vpcId: str
    """``AWS::EC2::VPCEndpoint.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#cfn-ec2-vpcendpoint-vpcid
    Stability:
        experimental
    """

class CfnVPCEndpointService(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointService"):
    """A CloudFormation ``AWS::EC2::VPCEndpointService``.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservice.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPCEndpointService
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, network_load_balancer_arns: typing.List[str], acceptance_required: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::EC2::VPCEndpointService``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            networkLoadBalancerArns: ``AWS::EC2::VPCEndpointService.NetworkLoadBalancerArns``.
            acceptanceRequired: ``AWS::EC2::VPCEndpointService.AcceptanceRequired``.

        Stability:
            experimental
        """
        props: CfnVPCEndpointServiceProps = {"networkLoadBalancerArns": network_load_balancer_arns}

        if acceptance_required is not None:
            props["acceptanceRequired"] = acceptance_required

        jsii.create(CfnVPCEndpointService, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnVPCEndpointServiceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="vpcEndpointServiceId")
    def vpc_endpoint_service_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpcEndpointServiceId")


class CfnVPCEndpointServicePermissions(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointServicePermissions"):
    """A CloudFormation ``AWS::EC2::VPCEndpointServicePermissions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservicepermissions.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPCEndpointServicePermissions
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, service_id: str, allowed_principals: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::EC2::VPCEndpointServicePermissions``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            serviceId: ``AWS::EC2::VPCEndpointServicePermissions.ServiceId``.
            allowedPrincipals: ``AWS::EC2::VPCEndpointServicePermissions.AllowedPrincipals``.

        Stability:
            experimental
        """
        props: CfnVPCEndpointServicePermissionsProps = {"serviceId": service_id}

        if allowed_principals is not None:
            props["allowedPrincipals"] = allowed_principals

        jsii.create(CfnVPCEndpointServicePermissions, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnVPCEndpointServicePermissionsProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCEndpointServicePermissionsProps(jsii.compat.TypedDict, total=False):
    allowedPrincipals: typing.List[str]
    """``AWS::EC2::VPCEndpointServicePermissions.AllowedPrincipals``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservicepermissions.html#cfn-ec2-vpcendpointservicepermissions-allowedprincipals
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointServicePermissionsProps", jsii_struct_bases=[_CfnVPCEndpointServicePermissionsProps])
class CfnVPCEndpointServicePermissionsProps(_CfnVPCEndpointServicePermissionsProps):
    """Properties for defining a ``AWS::EC2::VPCEndpointServicePermissions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservicepermissions.html
    Stability:
        experimental
    """
    serviceId: str
    """``AWS::EC2::VPCEndpointServicePermissions.ServiceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservicepermissions.html#cfn-ec2-vpcendpointservicepermissions-serviceid
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCEndpointServiceProps(jsii.compat.TypedDict, total=False):
    acceptanceRequired: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::VPCEndpointService.AcceptanceRequired``.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservice.html#cfn-ec2-vpcendpointservice-acceptancerequired
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCEndpointServiceProps", jsii_struct_bases=[_CfnVPCEndpointServiceProps])
class CfnVPCEndpointServiceProps(_CfnVPCEndpointServiceProps):
    """Properties for defining a ``AWS::EC2::VPCEndpointService``.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservice.html
    Stability:
        experimental
    """
    networkLoadBalancerArns: typing.List[str]
    """``AWS::EC2::VPCEndpointService.NetworkLoadBalancerArns``.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpointservice.html#cfn-ec2-vpcendpointservice-networkloadbalancerarns
    Stability:
        experimental
    """

class CfnVPCGatewayAttachment(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCGatewayAttachment"):
    """A CloudFormation ``AWS::EC2::VPCGatewayAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPCGatewayAttachment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc_id: str, internet_gateway_id: typing.Optional[str]=None, vpn_gateway_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::VPCGatewayAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            vpcId: ``AWS::EC2::VPCGatewayAttachment.VpcId``.
            internetGatewayId: ``AWS::EC2::VPCGatewayAttachment.InternetGatewayId``.
            vpnGatewayId: ``AWS::EC2::VPCGatewayAttachment.VpnGatewayId``.

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
    def property_overrides(self) -> "CfnVPCGatewayAttachmentProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="vpcGatewayAttachmentName")
    def vpc_gateway_attachment_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpcGatewayAttachmentName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCGatewayAttachmentProps(jsii.compat.TypedDict, total=False):
    internetGatewayId: str
    """``AWS::EC2::VPCGatewayAttachment.InternetGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html#cfn-ec2-vpcgatewayattachment-internetgatewayid
    Stability:
        experimental
    """
    vpnGatewayId: str
    """``AWS::EC2::VPCGatewayAttachment.VpnGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html#cfn-ec2-vpcgatewayattachment-vpngatewayid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCGatewayAttachmentProps", jsii_struct_bases=[_CfnVPCGatewayAttachmentProps])
class CfnVPCGatewayAttachmentProps(_CfnVPCGatewayAttachmentProps):
    """Properties for defining a ``AWS::EC2::VPCGatewayAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html
    Stability:
        experimental
    """
    vpcId: str
    """``AWS::EC2::VPCGatewayAttachment.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html#cfn-ec2-vpcgatewayattachment-vpcid
    Stability:
        experimental
    """

class CfnVPCPeeringConnection(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPCPeeringConnection"):
    """A CloudFormation ``AWS::EC2::VPCPeeringConnection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPCPeeringConnection
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, peer_vpc_id: str, vpc_id: str, peer_owner_id: typing.Optional[str]=None, peer_region: typing.Optional[str]=None, peer_role_arn: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::VPCPeeringConnection``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            peerVpcId: ``AWS::EC2::VPCPeeringConnection.PeerVpcId``.
            vpcId: ``AWS::EC2::VPCPeeringConnection.VpcId``.
            peerOwnerId: ``AWS::EC2::VPCPeeringConnection.PeerOwnerId``.
            peerRegion: ``AWS::EC2::VPCPeeringConnection.PeerRegion``.
            peerRoleArn: ``AWS::EC2::VPCPeeringConnection.PeerRoleArn``.
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
    def property_overrides(self) -> "CfnVPCPeeringConnectionProps":
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

    @property
    @jsii.member(jsii_name="vpcPeeringConnectionName")
    def vpc_peering_connection_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpcPeeringConnectionName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCPeeringConnectionProps(jsii.compat.TypedDict, total=False):
    peerOwnerId: str
    """``AWS::EC2::VPCPeeringConnection.PeerOwnerId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-peerownerid
    Stability:
        experimental
    """
    peerRegion: str
    """``AWS::EC2::VPCPeeringConnection.PeerRegion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-peerregion
    Stability:
        experimental
    """
    peerRoleArn: str
    """``AWS::EC2::VPCPeeringConnection.PeerRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-peerrolearn
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::VPCPeeringConnection.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCPeeringConnectionProps", jsii_struct_bases=[_CfnVPCPeeringConnectionProps])
class CfnVPCPeeringConnectionProps(_CfnVPCPeeringConnectionProps):
    """Properties for defining a ``AWS::EC2::VPCPeeringConnection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html
    Stability:
        experimental
    """
    peerVpcId: str
    """``AWS::EC2::VPCPeeringConnection.PeerVpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-peervpcid
    Stability:
        experimental
    """

    vpcId: str
    """``AWS::EC2::VPCPeeringConnection.VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcpeeringconnection.html#cfn-ec2-vpcpeeringconnection-vpcid
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPCProps(jsii.compat.TypedDict, total=False):
    enableDnsHostnames: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::VPC.EnableDnsHostnames``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-EnableDnsHostnames
    Stability:
        experimental
    """
    enableDnsSupport: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::VPC.EnableDnsSupport``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-EnableDnsSupport
    Stability:
        experimental
    """
    instanceTenancy: str
    """``AWS::EC2::VPC.InstanceTenancy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-instancetenancy
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::VPC.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPCProps", jsii_struct_bases=[_CfnVPCProps])
class CfnVPCProps(_CfnVPCProps):
    """Properties for defining a ``AWS::EC2::VPC``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html
    Stability:
        experimental
    """
    cidrBlock: str
    """``AWS::EC2::VPC.CidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html#cfn-aws-ec2-vpc-cidrblock
    Stability:
        experimental
    """

class CfnVPNConnection(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPNConnection"):
    """A CloudFormation ``AWS::EC2::VPNConnection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPNConnection
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, customer_gateway_id: str, type: str, vpn_gateway_id: str, static_routes_only: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpn_tunnel_options_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "VpnTunnelOptionsSpecificationProperty"]]]]]=None) -> None:
        """Create a new ``AWS::EC2::VPNConnection``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            customerGatewayId: ``AWS::EC2::VPNConnection.CustomerGatewayId``.
            type: ``AWS::EC2::VPNConnection.Type``.
            vpnGatewayId: ``AWS::EC2::VPNConnection.VpnGatewayId``.
            staticRoutesOnly: ``AWS::EC2::VPNConnection.StaticRoutesOnly``.
            tags: ``AWS::EC2::VPNConnection.Tags``.
            vpnTunnelOptionsSpecifications: ``AWS::EC2::VPNConnection.VpnTunnelOptionsSpecifications``.

        Stability:
            experimental
        """
        props: CfnVPNConnectionProps = {"customerGatewayId": customer_gateway_id, "type": type, "vpnGatewayId": vpn_gateway_id}

        if static_routes_only is not None:
            props["staticRoutesOnly"] = static_routes_only

        if tags is not None:
            props["tags"] = tags

        if vpn_tunnel_options_specifications is not None:
            props["vpnTunnelOptionsSpecifications"] = vpn_tunnel_options_specifications

        jsii.create(CfnVPNConnection, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnVPNConnectionProps":
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

    @property
    @jsii.member(jsii_name="vpnConnectionName")
    def vpn_connection_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpnConnectionName")

    @jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPNConnection.VpnTunnelOptionsSpecificationProperty", jsii_struct_bases=[])
    class VpnTunnelOptionsSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-vpnconnection-vpntunneloptionsspecification.html
        Stability:
            experimental
        """
        preSharedKey: str
        """``CfnVPNConnection.VpnTunnelOptionsSpecificationProperty.PreSharedKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-vpnconnection-vpntunneloptionsspecification.html#cfn-ec2-vpnconnection-vpntunneloptionsspecification-presharedkey
        Stability:
            experimental
        """

        tunnelInsideCidr: str
        """``CfnVPNConnection.VpnTunnelOptionsSpecificationProperty.TunnelInsideCidr``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-vpnconnection-vpntunneloptionsspecification.html#cfn-ec2-vpnconnection-vpntunneloptionsspecification-tunnelinsidecidr
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPNConnectionProps(jsii.compat.TypedDict, total=False):
    staticRoutesOnly: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::VPNConnection.StaticRoutesOnly``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-StaticRoutesOnly
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::VPNConnection.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-tags
    Stability:
        experimental
    """
    vpnTunnelOptionsSpecifications: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnVPNConnection.VpnTunnelOptionsSpecificationProperty"]]]
    """``AWS::EC2::VPNConnection.VpnTunnelOptionsSpecifications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-vpntunneloptionsspecifications
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPNConnectionProps", jsii_struct_bases=[_CfnVPNConnectionProps])
class CfnVPNConnectionProps(_CfnVPNConnectionProps):
    """Properties for defining a ``AWS::EC2::VPNConnection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html
    Stability:
        experimental
    """
    customerGatewayId: str
    """``AWS::EC2::VPNConnection.CustomerGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-customergatewayid
    Stability:
        experimental
    """

    type: str
    """``AWS::EC2::VPNConnection.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-type
    Stability:
        experimental
    """

    vpnGatewayId: str
    """``AWS::EC2::VPNConnection.VpnGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection.html#cfn-ec2-vpnconnection-vpngatewayid
    Stability:
        experimental
    """

class CfnVPNConnectionRoute(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPNConnectionRoute"):
    """A CloudFormation ``AWS::EC2::VPNConnectionRoute``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection-route.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPNConnectionRoute
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, destination_cidr_block: str, vpn_connection_id: str) -> None:
        """Create a new ``AWS::EC2::VPNConnectionRoute``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            destinationCidrBlock: ``AWS::EC2::VPNConnectionRoute.DestinationCidrBlock``.
            vpnConnectionId: ``AWS::EC2::VPNConnectionRoute.VpnConnectionId``.

        Stability:
            experimental
        """
        props: CfnVPNConnectionRouteProps = {"destinationCidrBlock": destination_cidr_block, "vpnConnectionId": vpn_connection_id}

        jsii.create(CfnVPNConnectionRoute, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnVPNConnectionRouteProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="vpnConnectionRouteName")
    def vpn_connection_route_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpnConnectionRouteName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPNConnectionRouteProps", jsii_struct_bases=[])
class CfnVPNConnectionRouteProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::VPNConnectionRoute``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection-route.html
    Stability:
        experimental
    """
    destinationCidrBlock: str
    """``AWS::EC2::VPNConnectionRoute.DestinationCidrBlock``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection-route.html#cfn-ec2-vpnconnectionroute-cidrblock
    Stability:
        experimental
    """

    vpnConnectionId: str
    """``AWS::EC2::VPNConnectionRoute.VpnConnectionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-connection-route.html#cfn-ec2-vpnconnectionroute-connectionid
    Stability:
        experimental
    """

class CfnVPNGateway(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPNGateway"):
    """A CloudFormation ``AWS::EC2::VPNGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPNGateway
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, type: str, amazon_side_asn: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::EC2::VPNGateway``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            type: ``AWS::EC2::VPNGateway.Type``.
            amazonSideAsn: ``AWS::EC2::VPNGateway.AmazonSideAsn``.
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
    def property_overrides(self) -> "CfnVPNGatewayProps":
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

    @property
    @jsii.member(jsii_name="vpnGatewayName")
    def vpn_gateway_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpnGatewayName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVPNGatewayProps(jsii.compat.TypedDict, total=False):
    amazonSideAsn: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::VPNGateway.AmazonSideAsn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html#cfn-ec2-vpngateway-amazonsideasn
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::VPNGateway.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html#cfn-ec2-vpngateway-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPNGatewayProps", jsii_struct_bases=[_CfnVPNGatewayProps])
class CfnVPNGatewayProps(_CfnVPNGatewayProps):
    """Properties for defining a ``AWS::EC2::VPNGateway``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html
    Stability:
        experimental
    """
    type: str
    """``AWS::EC2::VPNGateway.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gateway.html#cfn-ec2-vpngateway-type
    Stability:
        experimental
    """

class CfnVPNGatewayRoutePropagation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVPNGatewayRoutePropagation"):
    """A CloudFormation ``AWS::EC2::VPNGatewayRoutePropagation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gatewayrouteprop.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VPNGatewayRoutePropagation
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, route_table_ids: typing.List[str], vpn_gateway_id: str) -> None:
        """Create a new ``AWS::EC2::VPNGatewayRoutePropagation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            routeTableIds: ``AWS::EC2::VPNGatewayRoutePropagation.RouteTableIds``.
            vpnGatewayId: ``AWS::EC2::VPNGatewayRoutePropagation.VpnGatewayId``.

        Stability:
            experimental
        """
        props: CfnVPNGatewayRoutePropagationProps = {"routeTableIds": route_table_ids, "vpnGatewayId": vpn_gateway_id}

        jsii.create(CfnVPNGatewayRoutePropagation, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnVPNGatewayRoutePropagationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="vpnGatewayRoutePropagationName")
    def vpn_gateway_route_propagation_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpnGatewayRoutePropagationName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVPNGatewayRoutePropagationProps", jsii_struct_bases=[])
class CfnVPNGatewayRoutePropagationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::VPNGatewayRoutePropagation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gatewayrouteprop.html
    Stability:
        experimental
    """
    routeTableIds: typing.List[str]
    """``AWS::EC2::VPNGatewayRoutePropagation.RouteTableIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gatewayrouteprop.html#cfn-ec2-vpngatewayrouteprop-routetableids
    Stability:
        experimental
    """

    vpnGatewayId: str
    """``AWS::EC2::VPNGatewayRoutePropagation.VpnGatewayId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpn-gatewayrouteprop.html#cfn-ec2-vpngatewayrouteprop-vpngatewayid
    Stability:
        experimental
    """

class CfnVolume(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVolume"):
    """A CloudFormation ``AWS::EC2::Volume``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::Volume
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, availability_zone: str, auto_enable_io: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, iops: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, kms_key_id: typing.Optional[str]=None, size: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, snapshot_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, volume_type: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EC2::Volume``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            availabilityZone: ``AWS::EC2::Volume.AvailabilityZone``.
            autoEnableIo: ``AWS::EC2::Volume.AutoEnableIO``.
            encrypted: ``AWS::EC2::Volume.Encrypted``.
            iops: ``AWS::EC2::Volume.Iops``.
            kmsKeyId: ``AWS::EC2::Volume.KmsKeyId``.
            size: ``AWS::EC2::Volume.Size``.
            snapshotId: ``AWS::EC2::Volume.SnapshotId``.
            tags: ``AWS::EC2::Volume.Tags``.
            volumeType: ``AWS::EC2::Volume.VolumeType``.

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
    def property_overrides(self) -> "CfnVolumeProps":
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

    @property
    @jsii.member(jsii_name="volumeId")
    def volume_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "volumeId")


class CfnVolumeAttachment(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CfnVolumeAttachment"):
    """A CloudFormation ``AWS::EC2::VolumeAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EC2::VolumeAttachment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, device: str, instance_id: str, volume_id: str) -> None:
        """Create a new ``AWS::EC2::VolumeAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            device: ``AWS::EC2::VolumeAttachment.Device``.
            instanceId: ``AWS::EC2::VolumeAttachment.InstanceId``.
            volumeId: ``AWS::EC2::VolumeAttachment.VolumeId``.

        Stability:
            experimental
        """
        props: CfnVolumeAttachmentProps = {"device": device, "instanceId": instance_id, "volumeId": volume_id}

        jsii.create(CfnVolumeAttachment, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnVolumeAttachmentProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="volumeAttachmentId")
    def volume_attachment_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "volumeAttachmentId")


@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVolumeAttachmentProps", jsii_struct_bases=[])
class CfnVolumeAttachmentProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EC2::VolumeAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html
    Stability:
        experimental
    """
    device: str
    """``AWS::EC2::VolumeAttachment.Device``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html#cfn-ec2-ebs-volumeattachment-device
    Stability:
        experimental
    """

    instanceId: str
    """``AWS::EC2::VolumeAttachment.InstanceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html#cfn-ec2-ebs-volumeattachment-instanceid
    Stability:
        experimental
    """

    volumeId: str
    """``AWS::EC2::VolumeAttachment.VolumeId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volumeattachment.html#cfn-ec2-ebs-volumeattachment-volumeid
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVolumeProps(jsii.compat.TypedDict, total=False):
    autoEnableIo: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::Volume.AutoEnableIO``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-autoenableio
    Stability:
        experimental
    """
    encrypted: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::EC2::Volume.Encrypted``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-encrypted
    Stability:
        experimental
    """
    iops: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::Volume.Iops``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-iops
    Stability:
        experimental
    """
    kmsKeyId: str
    """``AWS::EC2::Volume.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-kmskeyid
    Stability:
        experimental
    """
    size: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::EC2::Volume.Size``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-size
    Stability:
        experimental
    """
    snapshotId: str
    """``AWS::EC2::Volume.SnapshotId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-snapshotid
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EC2::Volume.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-tags
    Stability:
        experimental
    """
    volumeType: str
    """``AWS::EC2::Volume.VolumeType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-volumetype
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ec2.CfnVolumeProps", jsii_struct_bases=[_CfnVolumeProps])
class CfnVolumeProps(_CfnVolumeProps):
    """Properties for defining a ``AWS::EC2::Volume``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html
    Stability:
        experimental
    """
    availabilityZone: str
    """``AWS::EC2::Volume.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-ebs-volume.html#cfn-ec2-ebs-volume-availabilityzone
    Stability:
        experimental
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
    defaultPortRange: "IPortRange"
    """Default port range for initiating connections to and from this object.

    Default:
        No default port range

    Stability:
        experimental
    """

    securityGroupRule: "ISecurityGroupRule"
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
    Default = "Default"
    """Instances can be launched with any tenancy.

    Stability:
        experimental
    """
    Dedicated = "Dedicated"
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
    def __init__(self, *, default_port_range: typing.Optional["IPortRange"]=None, security_group_rule: typing.Optional["ISecurityGroupRule"]=None, security_groups: typing.Optional[typing.List["ISecurityGroup"]]=None) -> None:
        """
        Arguments:
            props: -
            defaultPortRange: Default port range for initiating connections to and from this object. Default: No default port range
            securityGroupRule: Class that represents the rule by which others can connect to this connectable. This object is required, but will be derived from securityGroup if that is passed. Default: Derived from securityGroup if set.
            securityGroups: What securityGroup(s) this object is managing connections for. Default: No security groups

        Stability:
            experimental
        """
        props: ConnectionsProps = {}

        if default_port_range is not None:
            props["defaultPortRange"] = default_port_range

        if security_group_rule is not None:
            props["securityGroupRule"] = security_group_rule

        if security_groups is not None:
            props["securityGroups"] = security_groups

        jsii.create(Connections, self, [props])

    @jsii.member(jsii_name="addSecurityGroup")
    def add_security_group(self, *security_groups: "ISecurityGroup") -> None:
        """Add a security group to the list of security groups managed by this object.

        Arguments:
            securityGroups: -

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
    def allow_from(self, other: "IConnectable", port_range: "IPortRange", description: typing.Optional[str]=None) -> None:
        """Allow connections from the peer on the given port.

        Arguments:
            other: -
            portRange: -
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowFrom", [other, port_range, description])

    @jsii.member(jsii_name="allowFromAnyIPv4")
    def allow_from_any_i_pv4(self, port_range: "IPortRange", description: typing.Optional[str]=None) -> None:
        """Allow from any IPv4 ranges.

        Arguments:
            portRange: -
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowFromAnyIPv4", [port_range, description])

    @jsii.member(jsii_name="allowInternally")
    def allow_internally(self, port_range: "IPortRange", description: typing.Optional[str]=None) -> None:
        """Allow hosts inside the security group to connect to each other on the given port.

        Arguments:
            portRange: -
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowInternally", [port_range, description])

    @jsii.member(jsii_name="allowTo")
    def allow_to(self, other: "IConnectable", port_range: "IPortRange", description: typing.Optional[str]=None) -> None:
        """Allow connections to the peer on the given port.

        Arguments:
            other: -
            portRange: -
            description: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allowTo", [other, port_range, description])

    @jsii.member(jsii_name="allowToAnyIPv4")
    def allow_to_any_i_pv4(self, port_range: "IPortRange", description: typing.Optional[str]=None) -> None:
        """Allow to all IPv4 ranges.

        Arguments:
            portRange: -
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
    @jsii.member(jsii_name="defaultPortRange")
    def default_port_range(self) -> typing.Optional["IPortRange"]:
        """The default port configured for this connection peer, if available.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultPortRange")


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
    @jsii.member(jsii_name="DynamoDb")
    def DYNAMO_DB(cls) -> "GatewayVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "DynamoDb")

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


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IMachineImageSource")
class IMachineImageSource(jsii.compat.Protocol):
    """Interface for classes that can select an appropriate machine image to use.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IMachineImageSourceProxy

    @jsii.member(jsii_name="getImage")
    def get_image(self, scope: aws_cdk.cdk.Construct) -> "MachineImage":
        """Return the image to use in the given context.

        Arguments:
            scope: -

        Stability:
            experimental
        """
        ...


class _IMachineImageSourceProxy():
    """Interface for classes that can select an appropriate machine image to use.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IMachineImageSource"
    @jsii.member(jsii_name="getImage")
    def get_image(self, scope: aws_cdk.cdk.Construct) -> "MachineImage":
        """Return the image to use in the given context.

        Arguments:
            scope: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getImage", [scope])


@jsii.implements(IMachineImageSource)
class AmazonLinuxImage(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.AmazonLinuxImage"):
    """Selects the latest version of Amazon Linux.

    The AMI ID is selected using the values published to the SSM parameter store.

    Stability:
        experimental
    """
    def __init__(self, *, edition: typing.Optional["AmazonLinuxEdition"]=None, generation: typing.Optional["AmazonLinuxGeneration"]=None, storage: typing.Optional["AmazonLinuxStorage"]=None, virtualization: typing.Optional["AmazonLinuxVirt"]=None) -> None:
        """
        Arguments:
            props: -
            edition: What edition of Amazon Linux to use. Default: Standard
            generation: What generation of Amazon Linux to use. Default: AmazonLinux
            storage: What storage backed image to use. Default: GeneralPurpose
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

        if virtualization is not None:
            props["virtualization"] = virtualization

        jsii.create(AmazonLinuxImage, self, [props])

    @jsii.member(jsii_name="getImage")
    def get_image(self, scope: aws_cdk.cdk.Construct) -> "MachineImage":
        """Return the image to use in the given context.

        Arguments:
            scope: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getImage", [scope])


@jsii.implements(IMachineImageSource)
class GenericLinuxImage(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.GenericLinuxImage"):
    """Construct a Linux machine image from an AMI map.

    Linux images IDs are not published to SSM parameter store yet, so you'll have to
    manually specify an AMI map.

    Stability:
        experimental
    """
    def __init__(self, ami_map: typing.Mapping[str,str]) -> None:
        """
        Arguments:
            amiMap: -

        Stability:
            experimental
        """
        jsii.create(GenericLinuxImage, self, [ami_map])

    @jsii.member(jsii_name="getImage")
    def get_image(self, scope: aws_cdk.cdk.Construct) -> "MachineImage":
        """Return the image to use in the given context.

        Arguments:
            scope: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getImage", [scope])

    @property
    @jsii.member(jsii_name="amiMap")
    def ami_map(self) -> typing.Mapping[str,str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "amiMap")


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.IPortRange")
class IPortRange(jsii.compat.Protocol):
    """Interface for classes that provide the connection-specification parts of a security group rule.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IPortRangeProxy

    @property
    @jsii.member(jsii_name="canInlineRule")
    def can_inline_rule(self) -> bool:
        """Whether the rule containing this port range can be inlined into a securitygroup or not.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        ...


class _IPortRangeProxy():
    """Interface for classes that provide the connection-specification parts of a security group rule.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.IPortRange"
    @property
    @jsii.member(jsii_name="canInlineRule")
    def can_inline_rule(self) -> bool:
        """Whether the rule containing this port range can be inlined into a securitygroup or not.

        Stability:
            experimental
        """
        return jsii.get(self, "canInlineRule")

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])


@jsii.implements(IPortRange)
class AllTraffic(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.AllTraffic"):
    """All Traffic.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(AllTraffic, self, [])

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

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


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.ISecurityGroupRule")
class ISecurityGroupRule(jsii.compat.Protocol):
    """Interface for classes that provide the peer-specification parts of a security group rule.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ISecurityGroupRuleProxy

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

    @jsii.member(jsii_name="toEgressRuleJSON")
    def to_egress_rule_json(self) -> typing.Any:
        """Produce the egress rule JSON for the given connection.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="toIngressRuleJSON")
    def to_ingress_rule_json(self) -> typing.Any:
        """Produce the ingress rule JSON for the given connection.

        Stability:
            experimental
        """
        ...


class _ISecurityGroupRuleProxy():
    """Interface for classes that provide the peer-specification parts of a security group rule.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ec2.ISecurityGroupRule"
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

    @jsii.member(jsii_name="toEgressRuleJSON")
    def to_egress_rule_json(self) -> typing.Any:
        """Produce the egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toEgressRuleJSON", [])

    @jsii.member(jsii_name="toIngressRuleJSON")
    def to_ingress_rule_json(self) -> typing.Any:
        """Produce the ingress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toIngressRuleJSON", [])


@jsii.implements(ISecurityGroupRule, IConnectable)
class CidrIPv4(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CidrIPv4"):
    """A connection to and from a given IP range.

    Stability:
        experimental
    """
    def __init__(self, cidr_ip: str) -> None:
        """
        Arguments:
            cidrIp: -

        Stability:
            experimental
        """
        jsii.create(CidrIPv4, self, [cidr_ip])

    @jsii.member(jsii_name="toEgressRuleJSON")
    def to_egress_rule_json(self) -> typing.Any:
        """Produce the egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toEgressRuleJSON", [])

    @jsii.member(jsii_name="toIngressRuleJSON")
    def to_ingress_rule_json(self) -> typing.Any:
        """Produce the ingress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toIngressRuleJSON", [])

    @property
    @jsii.member(jsii_name="canInlineRule")
    def can_inline_rule(self) -> bool:
        """Whether the rule can be inlined into a SecurityGroup or not.

        Stability:
            experimental
        """
        return jsii.get(self, "canInlineRule")

    @property
    @jsii.member(jsii_name="cidrIp")
    def cidr_ip(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cidrIp")

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> "Connections":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> str:
        """A unique identifier for this connection peer.

        Stability:
            experimental
        """
        return jsii.get(self, "uniqueId")


class AnyIPv4(CidrIPv4, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.AnyIPv4"):
    """Any IPv4 address.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        """
        Stability:
            experimental
        """
        jsii.create(AnyIPv4, self, [])


@jsii.implements(ISecurityGroupRule, IConnectable)
class CidrIPv6(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.CidrIPv6"):
    """A connection to a from a given IPv6 range.

    Stability:
        experimental
    """
    def __init__(self, cidr_ipv6: str) -> None:
        """
        Arguments:
            cidrIpv6: -

        Stability:
            experimental
        """
        jsii.create(CidrIPv6, self, [cidr_ipv6])

    @jsii.member(jsii_name="toEgressRuleJSON")
    def to_egress_rule_json(self) -> typing.Any:
        """Produce the egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toEgressRuleJSON", [])

    @jsii.member(jsii_name="toIngressRuleJSON")
    def to_ingress_rule_json(self) -> typing.Any:
        """Produce the ingress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toIngressRuleJSON", [])

    @property
    @jsii.member(jsii_name="canInlineRule")
    def can_inline_rule(self) -> bool:
        """Whether the rule can be inlined into a SecurityGroup or not.

        Stability:
            experimental
        """
        return jsii.get(self, "canInlineRule")

    @property
    @jsii.member(jsii_name="cidrIpv6")
    def cidr_ipv6(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cidrIpv6")

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> "Connections":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> str:
        """A unique identifier for this connection peer.

        Stability:
            experimental
        """
        return jsii.get(self, "uniqueId")


class AnyIPv6(CidrIPv6, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.AnyIPv6"):
    """Any IPv6 address.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        """
        Stability:
            experimental
        """
        jsii.create(AnyIPv6, self, [])


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.ISecurityGroup")
class ISecurityGroup(aws_cdk.cdk.IResource, ISecurityGroupRule, IConnectable, jsii.compat.Protocol):
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
    def add_egress_rule(self, peer: "ISecurityGroupRule", connection: "IPortRange", description: typing.Optional[str]=None, remote_rule: typing.Optional[bool]=None) -> None:
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
            remoteRule: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addIngressRule")
    def add_ingress_rule(self, peer: "ISecurityGroupRule", connection: "IPortRange", description: typing.Optional[str]=None, remote_rule: typing.Optional[bool]=None) -> None:
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
            remoteRule: -

        Stability:
            experimental
        """
        ...


class _ISecurityGroupProxy(jsii.proxy_for(aws_cdk.cdk.IResource), jsii.proxy_for(ISecurityGroupRule), jsii.proxy_for(IConnectable)):
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
    def add_egress_rule(self, peer: "ISecurityGroupRule", connection: "IPortRange", description: typing.Optional[str]=None, remote_rule: typing.Optional[bool]=None) -> None:
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
            remoteRule: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addEgressRule", [peer, connection, description, remote_rule])

    @jsii.member(jsii_name="addIngressRule")
    def add_ingress_rule(self, peer: "ISecurityGroupRule", connection: "IPortRange", description: typing.Optional[str]=None, remote_rule: typing.Optional[bool]=None) -> None:
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
            remoteRule: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addIngressRule", [peer, connection, description, remote_rule])


@jsii.interface(jsii_type="@aws-cdk/aws-ec2.ISubnet")
class ISubnet(aws_cdk.cdk.IResource, jsii.compat.Protocol):
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
    def internet_connectivity_established(self) -> aws_cdk.cdk.IDependable:
        """Dependable that can be depended upon to force internet connectivity established on the VPC.

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

    @property
    @jsii.member(jsii_name="routeTableId")
    def route_table_id(self) -> typing.Optional[str]:
        """Route table ID.

        Stability:
            experimental
        """
        ...


class _ISubnetProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
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
    def internet_connectivity_established(self) -> aws_cdk.cdk.IDependable:
        """Dependable that can be depended upon to force internet connectivity established on the VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "internetConnectivityEstablished")

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

    @property
    @jsii.member(jsii_name="routeTableId")
    def route_table_id(self) -> typing.Optional[str]:
        """Route table ID.

        Stability:
            experimental
        """
        return jsii.get(self, "routeTableId")


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
class IVpc(aws_cdk.cdk.IResource, jsii.compat.Protocol):
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
    @jsii.member(jsii_name="region")
    def region(self) -> str:
        """Region where this VPC is located.

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
            privateDnsEnabled: Whether to associate a private hosted zone with the specified VPC. This allows you to make requests to the service using its default DNS hostname. Default: true
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
            staticRoutes: The static routes to be routed from the VPN gateway to the customer gateway. Default: Dynamic routing (BGP)
            tunnelOptions: The tunnel options for the VPN connection. At most two elements (one per tunnel). Duplicates not allowed. Default: Amazon generated tunnel options

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="isPublicSubnets")
    def is_public_subnets(self, subnet_ids: typing.List[str]) -> bool:
        """Return whether all of the given subnets are from the VPC's public subnets.

        Arguments:
            subnetIds: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="selectSubnetIds")
    def select_subnet_ids(self, *, one_per_az: typing.Optional[bool]=None, subnet_name: typing.Optional[str]=None, subnet_type: typing.Optional["SubnetType"]=None) -> typing.List[str]:
        """Return IDs of the subnets appropriate for the given selection strategy.

        Requires that at least one subnet is matched, throws a descriptive
        error message otherwise.

        Arguments:
            selection: -
            onePerAz: If true, return at most one subnet per AZ.
            subnetName: Place the instances in the subnets with the given name. (This is the name supplied in subnetConfiguration). At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: name
            subnetType: Place the instances in the subnets of the given type. At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: SubnetType.Private

        Deprecated:
            Use selectSubnets() instead.

        Stability:
            deprecated
        """
        ...

    @jsii.member(jsii_name="selectSubnets")
    def select_subnets(self, *, one_per_az: typing.Optional[bool]=None, subnet_name: typing.Optional[str]=None, subnet_type: typing.Optional["SubnetType"]=None) -> "SelectedSubnets":
        """Return information on the subnets appropriate for the given selection strategy.

        Requires that at least one subnet is matched, throws a descriptive
        error message otherwise.

        Arguments:
            selection: -
            onePerAz: If true, return at most one subnet per AZ.
            subnetName: Place the instances in the subnets with the given name. (This is the name supplied in subnetConfiguration). At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: name
            subnetType: Place the instances in the subnets of the given type. At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: SubnetType.Private

        Stability:
            experimental
        """
        ...


class _IVpcProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
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
    @jsii.member(jsii_name="region")
    def region(self) -> str:
        """Region where this VPC is located.

        Stability:
            experimental
        """
        return jsii.get(self, "region")

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
            privateDnsEnabled: Whether to associate a private hosted zone with the specified VPC. This allows you to make requests to the service using its default DNS hostname. Default: true
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
            staticRoutes: The static routes to be routed from the VPN gateway to the customer gateway. Default: Dynamic routing (BGP)
            tunnelOptions: The tunnel options for the VPN connection. At most two elements (one per tunnel). Duplicates not allowed. Default: Amazon generated tunnel options

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

    @jsii.member(jsii_name="isPublicSubnets")
    def is_public_subnets(self, subnet_ids: typing.List[str]) -> bool:
        """Return whether all of the given subnets are from the VPC's public subnets.

        Arguments:
            subnetIds: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "isPublicSubnets", [subnet_ids])

    @jsii.member(jsii_name="selectSubnetIds")
    def select_subnet_ids(self, *, one_per_az: typing.Optional[bool]=None, subnet_name: typing.Optional[str]=None, subnet_type: typing.Optional["SubnetType"]=None) -> typing.List[str]:
        """Return IDs of the subnets appropriate for the given selection strategy.

        Requires that at least one subnet is matched, throws a descriptive
        error message otherwise.

        Arguments:
            selection: -
            onePerAz: If true, return at most one subnet per AZ.
            subnetName: Place the instances in the subnets with the given name. (This is the name supplied in subnetConfiguration). At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: name
            subnetType: Place the instances in the subnets of the given type. At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: SubnetType.Private

        Deprecated:
            Use selectSubnets() instead.

        Stability:
            deprecated
        """
        selection: SubnetSelection = {}

        if one_per_az is not None:
            selection["onePerAz"] = one_per_az

        if subnet_name is not None:
            selection["subnetName"] = subnet_name

        if subnet_type is not None:
            selection["subnetType"] = subnet_type

        return jsii.invoke(self, "selectSubnetIds", [selection])

    @jsii.member(jsii_name="selectSubnets")
    def select_subnets(self, *, one_per_az: typing.Optional[bool]=None, subnet_name: typing.Optional[str]=None, subnet_type: typing.Optional["SubnetType"]=None) -> "SelectedSubnets":
        """Return information on the subnets appropriate for the given selection strategy.

        Requires that at least one subnet is matched, throws a descriptive
        error message otherwise.

        Arguments:
            selection: -
            onePerAz: If true, return at most one subnet per AZ.
            subnetName: Place the instances in the subnets with the given name. (This is the name supplied in subnetConfiguration). At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: name
            subnetType: Place the instances in the subnets of the given type. At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: SubnetType.Private

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
class IVpcEndpoint(aws_cdk.cdk.IResource, jsii.compat.Protocol):
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


class _IVpcEndpointProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
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
class IVpnConnection(aws_cdk.cdk.IConstruct, jsii.compat.Protocol):
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
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this VPNConnection.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricTunnelDataIn")
    def metric_tunnel_data_in(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The bytes received through the VPN tunnel.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricTunnelDataOut")
    def metric_tunnel_data_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The bytes sent through the VPN tunnel.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricTunnelState")
    def metric_tunnel_state(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The state of the tunnel. 0 indicates DOWN and 1 indicates UP.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...


class _IVpnConnectionProxy(jsii.proxy_for(aws_cdk.cdk.IConstruct)):
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
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this VPNConnection.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricTunnelDataIn")
    def metric_tunnel_data_in(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The bytes received through the VPN tunnel.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricTunnelDataIn", [props])

    @jsii.member(jsii_name="metricTunnelDataOut")
    def metric_tunnel_data_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The bytes sent through the VPN tunnel.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricTunnelDataOut", [props])

    @jsii.member(jsii_name="metricTunnelState")
    def metric_tunnel_state(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The state of the tunnel. 0 indicates DOWN and 1 indicates UP.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricTunnelState", [props])


@jsii.implements(IPortRange)
class IcmpAllTypeCodes(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.IcmpAllTypeCodes"):
    """All ICMP Codes for a given ICMP Type.

    Stability:
        experimental
    """
    def __init__(self, type: jsii.Number) -> None:
        """
        Arguments:
            type: -

        Stability:
            experimental
        """
        jsii.create(IcmpAllTypeCodes, self, [type])

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

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

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> jsii.Number:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.implements(IPortRange)
class IcmpAllTypesAndCodes(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.IcmpAllTypesAndCodes"):
    """All ICMP Types & Codes.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(IcmpAllTypesAndCodes, self, [])

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

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


@jsii.implements(IPortRange)
class IcmpPing(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.IcmpPing"):
    """ICMP Ping traffic.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(IcmpPing, self, [])

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

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


@jsii.implements(IPortRange)
class IcmpTypeAndCode(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.IcmpTypeAndCode"):
    """A set of matching ICMP Type & Code.

    Stability:
        experimental
    """
    def __init__(self, type: jsii.Number, code: jsii.Number) -> None:
        """
        Arguments:
            type: -
            code: -

        Stability:
            experimental
        """
        jsii.create(IcmpTypeAndCode, self, [type, code])

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

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

    @property
    @jsii.member(jsii_name="code")
    def code(self) -> jsii.Number:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "code")

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> jsii.Number:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


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
    Standard3 = "Standard3"
    """Standard instances, 3rd generation.

    Stability:
        experimental
    """
    Standard4 = "Standard4"
    """Standard instances, 4th generation.

    Stability:
        experimental
    """
    Standard5 = "Standard5"
    """Standard instances, 5th generation.

    Stability:
        experimental
    """
    Memory3 = "Memory3"
    """Memory optimized instances, 3rd generation.

    Stability:
        experimental
    """
    Memory4 = "Memory4"
    """Memory optimized instances, 3rd generation.

    Stability:
        experimental
    """
    Compute3 = "Compute3"
    """Compute optimized instances, 3rd generation.

    Stability:
        experimental
    """
    Compute4 = "Compute4"
    """Compute optimized instances, 4th generation.

    Stability:
        experimental
    """
    Compute5 = "Compute5"
    """Compute optimized instances, 5th generation.

    Stability:
        experimental
    """
    Storage2 = "Storage2"
    """Storage-optimized instances, 2nd generation.

    Stability:
        experimental
    """
    StorageCompute1 = "StorageCompute1"
    """Storage/compute balanced instances, 1st generation.

    Stability:
        experimental
    """
    Io3 = "Io3"
    """I/O-optimized instances, 3rd generation.

    Stability:
        experimental
    """
    Burstable2 = "Burstable2"
    """Burstable instances, 2nd generation.

    Stability:
        experimental
    """
    Burstable3 = "Burstable3"
    """Burstable instances, 3rd generation.

    Stability:
        experimental
    """
    MemoryIntensive1 = "MemoryIntensive1"
    """Memory-intensive instances, 1st generation.

    Stability:
        experimental
    """
    MemoryIntensive1Extended = "MemoryIntensive1Extended"
    """Memory-intensive instances, extended, 1st generation.

    Stability:
        experimental
    """
    Fpga1 = "Fpga1"
    """Instances with customizable hardware acceleration, 1st generation.

    Stability:
        experimental
    """
    Graphics3 = "Graphics3"
    """Graphics-optimized instances, 3rd generation.

    Stability:
        experimental
    """
    Parallel2 = "Parallel2"
    """Parallel-processing optimized instances, 2nd generation.

    Stability:
        experimental
    """
    Parallel3 = "Parallel3"
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
    Nano = "Nano"
    """
    Stability:
        experimental
    """
    Micro = "Micro"
    """
    Stability:
        experimental
    """
    Small = "Small"
    """
    Stability:
        experimental
    """
    Medium = "Medium"
    """
    Stability:
        experimental
    """
    Large = "Large"
    """
    Stability:
        experimental
    """
    XLarge = "XLarge"
    """
    Stability:
        experimental
    """
    XLarge2 = "XLarge2"
    """
    Stability:
        experimental
    """
    XLarge4 = "XLarge4"
    """
    Stability:
        experimental
    """
    XLarge8 = "XLarge8"
    """
    Stability:
        experimental
    """
    XLarge9 = "XLarge9"
    """
    Stability:
        experimental
    """
    XLarge10 = "XLarge10"
    """
    Stability:
        experimental
    """
    XLarge12 = "XLarge12"
    """
    Stability:
        experimental
    """
    XLarge16 = "XLarge16"
    """
    Stability:
        experimental
    """
    XLarge18 = "XLarge18"
    """
    Stability:
        experimental
    """
    XLarge24 = "XLarge24"
    """
    Stability:
        experimental
    """
    XLarge32 = "XLarge32"
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
            instanceTypeIdentifier: -

        Stability:
            experimental
        """
        jsii.create(InstanceType, self, [instance_type_identifier])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Return the instance type as a dotted string.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="instanceTypeIdentifier")
    def instance_type_identifier(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "instanceTypeIdentifier")


class InstanceTypePair(InstanceType, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.InstanceTypePair"):
    """Instance type for EC2 instances.

    This class takes a combination of a class and size.

    Be aware that not all combinations of class and size are available, and not all
    classes are available in all regions.

    Stability:
        experimental
    """
    def __init__(self, instance_class: "InstanceClass", instance_size: "InstanceSize") -> None:
        """
        Arguments:
            instanceClass: -
            instanceSize: -

        Stability:
            experimental
        """
        jsii.create(InstanceTypePair, self, [instance_class, instance_size])

    @property
    @jsii.member(jsii_name="instanceClass")
    def instance_class(self) -> "InstanceClass":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "instanceClass")

    @property
    @jsii.member(jsii_name="instanceSize")
    def instance_size(self) -> "InstanceSize":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "instanceSize")


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
    @jsii.member(jsii_name="ApiGateway")
    def API_GATEWAY(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ApiGateway")

    @classproperty
    @jsii.member(jsii_name="CloudFormation")
    def CLOUD_FORMATION(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CloudFormation")

    @classproperty
    @jsii.member(jsii_name="CloudTrail")
    def CLOUD_TRAIL(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CloudTrail")

    @classproperty
    @jsii.member(jsii_name="CloudWatch")
    def CLOUD_WATCH(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CloudWatch")

    @classproperty
    @jsii.member(jsii_name="CloudWatchEvents")
    def CLOUD_WATCH_EVENTS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CloudWatchEvents")

    @classproperty
    @jsii.member(jsii_name="CloudWatchLogs")
    def CLOUD_WATCH_LOGS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CloudWatchLogs")

    @classproperty
    @jsii.member(jsii_name="CodeBuild")
    def CODE_BUILD(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CodeBuild")

    @classproperty
    @jsii.member(jsii_name="CodeBuildFips")
    def CODE_BUILD_FIPS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CodeBuildFips")

    @classproperty
    @jsii.member(jsii_name="CodeCommit")
    def CODE_COMMIT(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CodeCommit")

    @classproperty
    @jsii.member(jsii_name="CodeCommitFips")
    def CODE_COMMIT_FIPS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CodeCommitFips")

    @classproperty
    @jsii.member(jsii_name="CodeCommitGit")
    def CODE_COMMIT_GIT(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CodeCommitGit")

    @classproperty
    @jsii.member(jsii_name="CodeCommitGitFips")
    def CODE_COMMIT_GIT_FIPS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CodeCommitGitFips")

    @classproperty
    @jsii.member(jsii_name="CodePipeline")
    def CODE_PIPELINE(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "CodePipeline")

    @classproperty
    @jsii.member(jsii_name="Config")
    def CONFIG(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Config")

    @classproperty
    @jsii.member(jsii_name="Ec2")
    def EC2(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Ec2")

    @classproperty
    @jsii.member(jsii_name="Ec2Messages")
    def EC2_MESSAGES(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Ec2Messages")

    @classproperty
    @jsii.member(jsii_name="Ecr")
    def ECR(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Ecr")

    @classproperty
    @jsii.member(jsii_name="EcrDocker")
    def ECR_DOCKER(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "EcrDocker")

    @classproperty
    @jsii.member(jsii_name="Ecs")
    def ECS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Ecs")

    @classproperty
    @jsii.member(jsii_name="EcsAgent")
    def ECS_AGENT(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "EcsAgent")

    @classproperty
    @jsii.member(jsii_name="EcsTelemetry")
    def ECS_TELEMETRY(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "EcsTelemetry")

    @classproperty
    @jsii.member(jsii_name="ElasticInferenceRuntime")
    def ELASTIC_INFERENCE_RUNTIME(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ElasticInferenceRuntime")

    @classproperty
    @jsii.member(jsii_name="ElasticLoadBalancing")
    def ELASTIC_LOAD_BALANCING(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ElasticLoadBalancing")

    @classproperty
    @jsii.member(jsii_name="KinesisStreams")
    def KINESIS_STREAMS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "KinesisStreams")

    @classproperty
    @jsii.member(jsii_name="Kms")
    def KMS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Kms")

    @classproperty
    @jsii.member(jsii_name="SageMakerApi")
    def SAGE_MAKER_API(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SageMakerApi")

    @classproperty
    @jsii.member(jsii_name="SageMakerNotebook")
    def SAGE_MAKER_NOTEBOOK(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SageMakerNotebook")

    @classproperty
    @jsii.member(jsii_name="SageMakerRuntime")
    def SAGE_MAKER_RUNTIME(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SageMakerRuntime")

    @classproperty
    @jsii.member(jsii_name="SageMakerRuntimeFips")
    def SAGE_MAKER_RUNTIME_FIPS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SageMakerRuntimeFips")

    @classproperty
    @jsii.member(jsii_name="SecretsManager")
    def SECRETS_MANAGER(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SecretsManager")

    @classproperty
    @jsii.member(jsii_name="ServiceCatalog")
    def SERVICE_CATALOG(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ServiceCatalog")

    @classproperty
    @jsii.member(jsii_name="Sns")
    def SNS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Sns")

    @classproperty
    @jsii.member(jsii_name="Sqs")
    def SQS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Sqs")

    @classproperty
    @jsii.member(jsii_name="Ssm")
    def SSM(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Ssm")

    @classproperty
    @jsii.member(jsii_name="SsmMessages")
    def SSM_MESSAGES(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SsmMessages")

    @classproperty
    @jsii.member(jsii_name="Sts")
    def STS(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Sts")

    @classproperty
    @jsii.member(jsii_name="Transfer")
    def TRANSFER(cls) -> "InterfaceVpcEndpointAwsService":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Transfer")

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

class MachineImage(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.MachineImage"):
    """Representation of a machine to be launched.

    Combines an AMI ID with an OS.

    Stability:
        experimental
    """
    def __init__(self, image_id: str, os: "OperatingSystem") -> None:
        """
        Arguments:
            imageId: -
            os: -

        Stability:
            experimental
        """
        jsii.create(MachineImage, self, [image_id, os])

    @property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "imageId")

    @property
    @jsii.member(jsii_name="os")
    def os(self) -> "OperatingSystem":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "os")


class OperatingSystem(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-ec2.OperatingSystem"):
    """Abstraction of OS features we need to be aware of.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _OperatingSystemProxy

    def __init__(self) -> None:
        jsii.create(OperatingSystem, self, [])

    @jsii.member(jsii_name="createUserData")
    @abc.abstractmethod
    def create_user_data(self, scripts: typing.List[str]) -> str:
        """
        Arguments:
            scripts: -

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="type")
    @abc.abstractmethod
    def type(self) -> "OperatingSystemType":
        """
        Stability:
            experimental
        """
        ...


class _OperatingSystemProxy(OperatingSystem):
    @jsii.member(jsii_name="createUserData")
    def create_user_data(self, scripts: typing.List[str]) -> str:
        """
        Arguments:
            scripts: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "createUserData", [scripts])

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "OperatingSystemType":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


class LinuxOS(OperatingSystem, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.LinuxOS"):
    """OS features specialized for Linux.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(LinuxOS, self, [])

    @jsii.member(jsii_name="createUserData")
    def create_user_data(self, scripts: typing.List[str]) -> str:
        """
        Arguments:
            scripts: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "createUserData", [scripts])

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "OperatingSystemType":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.enum(jsii_type="@aws-cdk/aws-ec2.OperatingSystemType")
class OperatingSystemType(enum.Enum):
    """The OS type of a particular image.

    Stability:
        experimental
    """
    Linux = "Linux"
    """
    Stability:
        experimental
    """
    Windows = "Windows"
    """
    Stability:
        experimental
    """

@jsii.implements(ISecurityGroupRule, IConnectable)
class PrefixList(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.PrefixList"):
    """A prefix list.

    Prefix lists are used to allow traffic to VPC-local service endpoints.

    For more information, see this page:

    https://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/vpc-endpoints.html

    Stability:
        experimental
    """
    def __init__(self, prefix_list_id: str) -> None:
        """
        Arguments:
            prefixListId: -

        Stability:
            experimental
        """
        jsii.create(PrefixList, self, [prefix_list_id])

    @jsii.member(jsii_name="toEgressRuleJSON")
    def to_egress_rule_json(self) -> typing.Any:
        """Produce the egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toEgressRuleJSON", [])

    @jsii.member(jsii_name="toIngressRuleJSON")
    def to_ingress_rule_json(self) -> typing.Any:
        """Produce the ingress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toIngressRuleJSON", [])

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
    @jsii.member(jsii_name="prefixListId")
    def prefix_list_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "prefixListId")

    @property
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> str:
        """A unique identifier for this connection peer.

        Stability:
            experimental
        """
        return jsii.get(self, "uniqueId")


@jsii.enum(jsii_type="@aws-cdk/aws-ec2.Protocol")
class Protocol(enum.Enum):
    """Protocol for use in Connection Rules.

    Stability:
        experimental
    """
    All = "All"
    """
    Stability:
        experimental
    """
    Tcp = "Tcp"
    """
    Stability:
        experimental
    """
    Udp = "Udp"
    """
    Stability:
        experimental
    """
    Icmp = "Icmp"
    """
    Stability:
        experimental
    """
    Icmpv6 = "Icmpv6"
    """
    Stability:
        experimental
    """

@jsii.implements(ISecurityGroup)
class SecurityGroup(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.SecurityGroup"):
    """Creates an Amazon EC2 security group within a VPC.

    This class has an additional optimization over imported security groups that it can also create
    inline ingress and egress rule (which saves on the total number of resources inside
    the template).

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc: "IVpc", allow_all_outbound: typing.Optional[bool]=None, description: typing.Optional[str]=None, group_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            vpc: The VPC in which to create the security group.
            allowAllOutbound: Whether to allow all outbound traffic by default. If this is set to true, there will only be a single egress rule which allows all outbound traffic. If this is set to false, no outbound traffic will be allowed by default and all egress traffic must be explicitly authorized. Default: true
            description: A description of the security group. Default: The default name will be the construct's CDK path.
            groupName: The name of the security group. For valid values, see the GroupName parameter of the CreateSecurityGroup action in the Amazon EC2 API Reference. It is not recommended to use an explicit group name. Default: If you don't specify a GroupName, AWS CloudFormation generates a unique physical ID and uses that ID for the group name.

        Stability:
            experimental
        """
        props: SecurityGroupProps = {"vpc": vpc}

        if allow_all_outbound is not None:
            props["allowAllOutbound"] = allow_all_outbound

        if description is not None:
            props["description"] = description

        if group_name is not None:
            props["groupName"] = group_name

        jsii.create(SecurityGroup, self, [scope, id, props])

    @jsii.member(jsii_name="fromSecurityGroupId")
    @classmethod
    def from_security_group_id(cls, scope: aws_cdk.cdk.Construct, id: str, security_group_id: str) -> "ISecurityGroup":
        """Import an existing security group into this app.

        Arguments:
            scope: -
            id: -
            securityGroupId: -

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
    def add_egress_rule(self, peer: "ISecurityGroupRule", connection: "IPortRange", description: typing.Optional[str]=None, remote_rule: typing.Optional[bool]=None) -> None:
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
            remoteRule: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addEgressRule", [peer, connection, description, remote_rule])

    @jsii.member(jsii_name="addIngressRule")
    def add_ingress_rule(self, peer: "ISecurityGroupRule", connection: "IPortRange", description: typing.Optional[str]=None, remote_rule: typing.Optional[bool]=None) -> None:
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
            remoteRule: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addIngressRule", [peer, connection, description, remote_rule])

    @jsii.member(jsii_name="toEgressRuleJSON")
    def to_egress_rule_json(self) -> typing.Any:
        """Produce the egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toEgressRuleJSON", [])

    @jsii.member(jsii_name="toIngressRuleJSON")
    def to_ingress_rule_json(self) -> typing.Any:
        """Produce the ingress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toIngressRuleJSON", [])

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
    @jsii.member(jsii_name="defaultPortRange")
    def default_port_range(self) -> typing.Optional["IPortRange"]:
        """FIXME: Where to place this??

        Stability:
            experimental
        """
        return jsii.get(self, "defaultPortRange")


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
    groupName: str
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

    internetConnectedDependency: aws_cdk.cdk.IDependable
    """Dependency representing internet connectivity for these subnets.

    Stability:
        experimental
    """

    routeTableIds: typing.List[str]
    """Route table IDs of each respective subnet.

    Stability:
        experimental
    """

    subnetIds: typing.List[str]
    """The subnet IDs.

    Stability:
        experimental
    """

@jsii.implements(ISubnet)
class Subnet(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.Subnet"):
    """Represents a new VPC subnet resource.

    Stability:
        experimental
    resource:
        AWS::EC2::Subnet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, availability_zone: str, cidr_block: str, vpc_id: str, map_public_ip_on_launch: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            availabilityZone: The availability zone for the subnet.
            cidrBlock: The CIDR notation for this subnet.
            vpcId: The VPC which this subnet is part of.
            mapPublicIpOnLaunch: Controls if a public IP is associated to an instance at launch. Default: true in Subnet.Public, false in Subnet.Private or Subnet.Isolated.

        Stability:
            experimental
        """
        props: SubnetProps = {"availabilityZone": availability_zone, "cidrBlock": cidr_block, "vpcId": vpc_id}

        if map_public_ip_on_launch is not None:
            props["mapPublicIpOnLaunch"] = map_public_ip_on_launch

        jsii.create(Subnet, self, [scope, id, props])

    @jsii.member(jsii_name="fromSubnetAttributes")
    @classmethod
    def from_subnet_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, availability_zone: str, subnet_id: str) -> "ISubnet":
        """
        Arguments:
            scope: -
            id: -
            attrs: -
            availabilityZone: The Availability Zone the subnet is located in.
            subnetId: The subnetId for this particular subnet.

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
    def add_default_internet_route(self, gateway_id: str, gateway_attachment: aws_cdk.cdk.IDependable) -> None:
        """Create a default route that points to a passed IGW, with a dependency on the IGW's attachment to the VPC.

        Arguments:
            gatewayId: the logical ID (ref) of the gateway attached to your VPC.
            gatewayAttachment: the gateway attachment construct to be added as a dependency.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addDefaultInternetRoute", [gateway_id, gateway_attachment])

    @jsii.member(jsii_name="addDefaultNatRoute")
    def add_default_nat_route(self, nat_gateway_id: str) -> None:
        """Adds an entry to this subnets route table that points to the passed NATGatwayId.

        Arguments:
            natGatewayId: The ID of the NAT gateway.

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
    def dependency_elements(self) -> typing.List[aws_cdk.cdk.IDependable]:
        """Parts of this VPC subnet.

        Stability:
            experimental
        """
        return jsii.get(self, "dependencyElements")

    @property
    @jsii.member(jsii_name="internetConnectivityEstablished")
    def internet_connectivity_established(self) -> aws_cdk.cdk.IDependable:
        """Dependable that can be depended upon to force internet connectivity established on the VPC.

        Stability:
            experimental
        """
        return jsii.get(self, "internetConnectivityEstablished")

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

    @property
    @jsii.member(jsii_name="routeTableId")
    def route_table_id(self) -> typing.Optional[str]:
        """The routeTableId attached to this subnet.

        Stability:
            experimental
        """
        return jsii.get(self, "routeTableId")


@jsii.implements(IPrivateSubnet)
class PrivateSubnet(Subnet, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.PrivateSubnet"):
    """Represents a private VPC subnet resource.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, availability_zone: str, cidr_block: str, vpc_id: str, map_public_ip_on_launch: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            availabilityZone: The availability zone for the subnet.
            cidrBlock: The CIDR notation for this subnet.
            vpcId: The VPC which this subnet is part of.
            mapPublicIpOnLaunch: Controls if a public IP is associated to an instance at launch. Default: true in Subnet.Public, false in Subnet.Private or Subnet.Isolated.

        Stability:
            experimental
        """
        props: PrivateSubnetProps = {"availabilityZone": availability_zone, "cidrBlock": cidr_block, "vpcId": vpc_id}

        if map_public_ip_on_launch is not None:
            props["mapPublicIpOnLaunch"] = map_public_ip_on_launch

        jsii.create(PrivateSubnet, self, [scope, id, props])

    @jsii.member(jsii_name="fromPrivateSubnetAttributes")
    @classmethod
    def from_private_subnet_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, availability_zone: str, subnet_id: str) -> "IPrivateSubnet":
        """
        Arguments:
            scope: -
            id: -
            attrs: -
            availabilityZone: The Availability Zone the subnet is located in.
            subnetId: The subnetId for this particular subnet.

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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, availability_zone: str, cidr_block: str, vpc_id: str, map_public_ip_on_launch: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            availabilityZone: The availability zone for the subnet.
            cidrBlock: The CIDR notation for this subnet.
            vpcId: The VPC which this subnet is part of.
            mapPublicIpOnLaunch: Controls if a public IP is associated to an instance at launch. Default: true in Subnet.Public, false in Subnet.Private or Subnet.Isolated.

        Stability:
            experimental
        """
        props: PublicSubnetProps = {"availabilityZone": availability_zone, "cidrBlock": cidr_block, "vpcId": vpc_id}

        if map_public_ip_on_launch is not None:
            props["mapPublicIpOnLaunch"] = map_public_ip_on_launch

        jsii.create(PublicSubnet, self, [scope, id, props])

    @jsii.member(jsii_name="fromPublicSubnetAttributes")
    @classmethod
    def from_public_subnet_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, availability_zone: str, subnet_id: str) -> "IPublicSubnet":
        """
        Arguments:
            scope: -
            id: -
            attrs: -
            availabilityZone: The Availability Zone the subnet is located in.
            subnetId: The subnetId for this particular subnet.

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
    Isolated = "Isolated"
    """Isolated Subnets do not route Outbound traffic.

    This can be good for subnets with RDS or
    Elasticache endpoints

    Stability:
        experimental
    """
    Private = "Private"
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
    Public = "Public"
    """Subnet connected to the Internet.

    Instances in a Public subnet can connect to the Internet and can be
    connected to from the Internet as long as they are launched with public
    IPs (controlled on the AutoScalingGroup or other constructs that launch
    instances).

    Public subnets route outbound traffic via an Internet Gateway.

    Stability:
        experimental
    """

@jsii.implements(IPortRange)
class TcpAllPorts(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.TcpAllPorts"):
    """All TCP Ports.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(TcpAllPorts, self, [])

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

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


@jsii.implements(IPortRange)
class TcpPort(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.TcpPort"):
    """A single TCP port.

    Stability:
        experimental
    """
    def __init__(self, port: jsii.Number) -> None:
        """
        Arguments:
            port: -

        Stability:
            experimental
        """
        jsii.create(TcpPort, self, [port])

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

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

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "port")


@jsii.implements(IPortRange)
class TcpPortRange(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.TcpPortRange"):
    """A TCP port range.

    Stability:
        experimental
    """
    def __init__(self, start_port: jsii.Number, end_port: jsii.Number) -> None:
        """
        Arguments:
            startPort: -
            endPort: -

        Stability:
            experimental
        """
        jsii.create(TcpPortRange, self, [start_port, end_port])

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

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

    @property
    @jsii.member(jsii_name="endPort")
    def end_port(self) -> jsii.Number:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "endPort")

    @property
    @jsii.member(jsii_name="startPort")
    def start_port(self) -> jsii.Number:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "startPort")


@jsii.implements(IPortRange)
class UdpAllPorts(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.UdpAllPorts"):
    """All UDP Ports.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(UdpAllPorts, self, [])

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

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


@jsii.implements(IPortRange)
class UdpPort(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.UdpPort"):
    """A single UDP port.

    Stability:
        experimental
    """
    def __init__(self, port: jsii.Number) -> None:
        """
        Arguments:
            port: -

        Stability:
            experimental
        """
        jsii.create(UdpPort, self, [port])

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

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

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "port")


@jsii.implements(IPortRange)
class UdpPortRange(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.UdpPortRange"):
    """A UDP port range.

    Stability:
        experimental
    """
    def __init__(self, start_port: jsii.Number, end_port: jsii.Number) -> None:
        """
        Arguments:
            startPort: -
            endPort: -

        Stability:
            experimental
        """
        jsii.create(UdpPortRange, self, [start_port, end_port])

    @jsii.member(jsii_name="toRuleJSON")
    def to_rule_json(self) -> typing.Any:
        """Produce the ingress/egress rule JSON for the given connection.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRuleJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

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

    @property
    @jsii.member(jsii_name="endPort")
    def end_port(self) -> jsii.Number:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "endPort")

    @property
    @jsii.member(jsii_name="startPort")
    def start_port(self) -> jsii.Number:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "startPort")


@jsii.implements(IVpc)
class Vpc(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.Vpc"):
    """VpcNetwork deploys an AWS VPC, with public and private subnets per Availability Zone. For example:.

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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cidr: typing.Optional[str]=None, default_instance_tenancy: typing.Optional["DefaultInstanceTenancy"]=None, enable_dns_hostnames: typing.Optional[bool]=None, enable_dns_support: typing.Optional[bool]=None, gateway_endpoints: typing.Optional[typing.Mapping[str,"GatewayVpcEndpointOptions"]]=None, max_a_zs: typing.Optional[jsii.Number]=None, nat_gateways: typing.Optional[jsii.Number]=None, nat_gateway_subnets: typing.Optional["SubnetSelection"]=None, subnet_configuration: typing.Optional[typing.List["SubnetConfiguration"]]=None, vpn_connections: typing.Optional[typing.Mapping[str,"VpnConnectionOptions"]]=None, vpn_gateway: typing.Optional[bool]=None, vpn_gateway_asn: typing.Optional[jsii.Number]=None, vpn_route_propagation: typing.Optional[typing.List["SubnetSelection"]]=None) -> None:
        """VpcNetwork creates a VPC that spans a whole region. It will automatically divide the provided VPC CIDR range, and create public and private subnets per Availability Zone. Network routing for the public subnets will be configured to allow outbound access directly via an Internet Gateway. Network routing for the private subnets will be configured to allow outbound access via a set of resilient NAT Gateways (one per AZ).

        Arguments:
            scope: -
            id: -
            props: -
            cidr: The CIDR range to use for the VPC (e.g. '10.0.0.0/16'). Should be a minimum of /28 and maximum size of /16. The range will be split evenly into two subnets per Availability Zone (one public, one private). Default: Vpc.DEFAULT_CIDR_RANGE
            defaultInstanceTenancy: The default tenancy of instances launched into the VPC. By setting this to dedicated tenancy, instances will be launched on hardware dedicated to a single AWS customer, unless specifically specified at instance launch time. Please note, not all instance types are usable with Dedicated tenancy. Default: DefaultInstanceTenancy.Default (shared) tenancy
            enableDnsHostnames: Indicates whether the instances launched in the VPC get public DNS hostnames. If this attribute is true, instances in the VPC get public DNS hostnames, but only if the enableDnsSupport attribute is also set to true. Default: true
            enableDnsSupport: Indicates whether the DNS resolution is supported for the VPC. If this attribute is false, the Amazon-provided DNS server in the VPC that resolves public DNS hostnames to IP addresses is not enabled. If this attribute is true, queries to the Amazon provided DNS server at the 169.254.169.253 IP address, or the reserved IP address at the base of the VPC IPv4 network range plus two will succeed. Default: true
            gatewayEndpoints: Gateway endpoints to add to this VPC. Default: - None.
            maxAZs: Define the maximum number of AZs to use in this region. If the region has more AZs than you want to use (for example, because of EIP limits), pick a lower number here. The AZs will be sorted and picked from the start of the list. If you pick a higher number than the number of AZs in the region, all AZs in the region will be selected. To use "all AZs" available to your account, use a high number (such as 99). Default: 3
            natGateways: The number of NAT Gateways to create. For example, if set this to 1 and your subnet configuration is for 3 Public subnets then only one of the Public subnets will have a gateway and all Private subnets will route to this NAT Gateway. Default: maxAZs
            natGatewaySubnets: Configures the subnets which will have NAT Gateways. You can pick a specific group of subnets by specifying the group name; the picked subnets must be public subnets. Default: - All public subnets.
            subnetConfiguration: Configure the subnets to build for each AZ. The subnets are constructed in the context of the VPC so you only need specify the configuration. The VPC details (VPC ID, specific CIDR, specific AZ will be calculated during creation) For example if you want 1 public subnet, 1 private subnet, and 1 isolated subnet in each AZ provide the following: subnetConfiguration: [ { cidrMask: 24, name: 'ingress', subnetType: SubnetType.Public, }, { cidrMask: 24, name: 'application', subnetType: SubnetType.Private, }, { cidrMask: 28, name: 'rds', subnetType: SubnetType.Isolated, } ] ``cidrMask`` is optional and if not provided the IP space in the VPC will be evenly divided between the requested subnets. Default: - The VPC CIDR will be evenly divided between 1 public and 1 private subnet per AZ.
            vpnConnections: VPN connections to this VPC. Default: - No connections.
            vpnGateway: Indicates whether a VPN gateway should be created and attached to this VPC. Default: - true when vpnGatewayAsn or vpnConnections is specified.
            vpnGatewayAsn: The private Autonomous System Number (ASN) for the VPN gateway. Default: - Amazon default ASN.
            vpnRoutePropagation: Where to propagate VPN routes. Default: - On the route tables associated with private subnets.

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
    def from_lookup(cls, scope: aws_cdk.cdk.Construct, id: str, *, is_default: typing.Optional[bool]=None, tags: typing.Optional[typing.Mapping[str,str]]=None, vpc_id: typing.Optional[str]=None, vpc_name: typing.Optional[str]=None) -> "IVpc":
        """Import an existing VPC from by querying the AWS environment this stack is deployed to.

        Arguments:
            scope: -
            id: -
            options: -
            isDefault: Whether to match the default VPC. Default: Don't care whether we return the default VPC
            tags: Tags on the VPC. The VPC must have all of these tags Default: Don't filter on tags
            vpcId: The ID of the VPC. If given, will import exactly this VPC. Default: Don't filter on vpcId
            vpcName: The name of the VPC. If given, will import the VPC with this name. Default: Don't filter on vpcName

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
    def from_vpc_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, availability_zones: typing.List[str], vpc_id: str, isolated_subnet_ids: typing.Optional[typing.List[str]]=None, isolated_subnet_names: typing.Optional[typing.List[str]]=None, private_subnet_ids: typing.Optional[typing.List[str]]=None, private_subnet_names: typing.Optional[typing.List[str]]=None, public_subnet_ids: typing.Optional[typing.List[str]]=None, public_subnet_names: typing.Optional[typing.List[str]]=None, vpn_gateway_id: typing.Optional[str]=None) -> "IVpc":
        """Import an exported VPC.

        Arguments:
            scope: -
            id: -
            attrs: -
            availabilityZones: List of availability zones for the subnets in this VPC.
            vpcId: VPC's identifier.
            isolatedSubnetIds: List of isolated subnet IDs. Must be undefined or match the availability zones in length and order.
            isolatedSubnetNames: List of names for the isolated subnets. Must be undefined or have a name for every isolated subnet group.
            privateSubnetIds: List of private subnet IDs. Must be undefined or match the availability zones in length and order.
            privateSubnetNames: List of names for the private subnets. Must be undefined or have a name for every private subnet group.
            publicSubnetIds: List of public subnet IDs. Must be undefined or match the availability zones in length and order.
            publicSubnetNames: List of names for the public subnets. Must be undefined or have a name for every public subnet group.
            vpnGatewayId: VPN gateway's identifier.

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
            privateDnsEnabled: Whether to associate a private hosted zone with the specified VPC. This allows you to make requests to the service using its default DNS hostname. Default: true
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
            staticRoutes: The static routes to be routed from the VPN gateway to the customer gateway. Default: Dynamic routing (BGP)
            tunnelOptions: The tunnel options for the VPN connection. At most two elements (one per tunnel). Duplicates not allowed. Default: Amazon generated tunnel options

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

    @jsii.member(jsii_name="isPublicSubnets")
    def is_public_subnets(self, subnet_ids: typing.List[str]) -> bool:
        """Return whether all of the given subnets are from the VPC's public subnets.

        Arguments:
            subnetIds: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "isPublicSubnets", [subnet_ids])

    @jsii.member(jsii_name="selectSubnetIds")
    def select_subnet_ids(self, *, one_per_az: typing.Optional[bool]=None, subnet_name: typing.Optional[str]=None, subnet_type: typing.Optional["SubnetType"]=None) -> typing.List[str]:
        """Return IDs of the subnets appropriate for the given selection strategy.

        Requires that at least one subnet is matched, throws a descriptive
        error message otherwise.

        Arguments:
            selection: -
            onePerAz: If true, return at most one subnet per AZ.
            subnetName: Place the instances in the subnets with the given name. (This is the name supplied in subnetConfiguration). At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: name
            subnetType: Place the instances in the subnets of the given type. At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: SubnetType.Private

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

        return jsii.invoke(self, "selectSubnetIds", [selection])

    @jsii.member(jsii_name="selectSubnetObjects")
    def _select_subnet_objects(self, *, one_per_az: typing.Optional[bool]=None, subnet_name: typing.Optional[str]=None, subnet_type: typing.Optional["SubnetType"]=None) -> typing.List["ISubnet"]:
        """Return the subnets appropriate for the placement strategy.

        Arguments:
            selection: -
            onePerAz: If true, return at most one subnet per AZ.
            subnetName: Place the instances in the subnets with the given name. (This is the name supplied in subnetConfiguration). At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: name
            subnetType: Place the instances in the subnets of the given type. At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: SubnetType.Private

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
            onePerAz: If true, return at most one subnet per AZ.
            subnetName: Place the instances in the subnets with the given name. (This is the name supplied in subnetConfiguration). At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: name
            subnetType: Place the instances in the subnets of the given type. At most one of ``subnetType`` and ``subnetName`` can be supplied. Default: SubnetType.Private

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
    @jsii.member(jsii_name="internetDependencies")
    def internet_dependencies(self) -> typing.List[aws_cdk.cdk.IConstruct]:
        """Dependencies for internet connectivity.

        Stability:
            experimental
        """
        return jsii.get(self, "internetDependencies")

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
    def nat_dependencies(self) -> typing.List[aws_cdk.cdk.IConstruct]:
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
    @jsii.member(jsii_name="region")
    def region(self) -> str:
        """The region where this VPC is defined.

        Stability:
            experimental
        """
        return jsii.get(self, "region")

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
class VpcEndpoint(aws_cdk.cdk.Resource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-ec2.VpcEndpoint"):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _VpcEndpointProxy

    def __init__(self, scope: aws_cdk.cdk.Construct, id: str) -> None:
        """Creates a new construct node.

        Arguments:
            scope: The scope in which to define this construct.
            id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.

        Stability:
            experimental
        """
        jsii.create(VpcEndpoint, self, [scope, id])

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


class _VpcEndpointProxy(VpcEndpoint, jsii.proxy_for(aws_cdk.cdk.Resource)):
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc: "IVpc", service: "IGatewayVpcEndpointService", subnets: typing.Optional[typing.List["SubnetSelection"]]=None) -> None:
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
    def from_gateway_vpc_endpoint_id(cls, scope: aws_cdk.cdk.Construct, id: str, gateway_vpc_endpoint_id: str) -> "IGatewayVpcEndpoint":
        """
        Arguments:
            scope: -
            id: -
            gatewayVpcEndpointId: -

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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc: "IVpc", service: "IInterfaceVpcEndpointService", private_dns_enabled: typing.Optional[bool]=None, subnets: typing.Optional["SubnetSelection"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            vpc: The VPC network in which the interface endpoint will be used.
            service: The service to use for this interface VPC endpoint.
            privateDnsEnabled: Whether to associate a private hosted zone with the specified VPC. This allows you to make requests to the service using its default DNS hostname. Default: true
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
    def from_interface_vpc_endpoint_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, port: jsii.Number, security_group_id: str, vpc_endpoint_id: str) -> "IInterfaceVpcEndpoint":
        """Imports an existing interface VPC endpoint.

        Arguments:
            scope: -
            id: -
            attrs: -
            port: The port of the service of the interface VPC endpoint.
            securityGroupId: The identifier of the security group associated with the interface VPC endpoint.
            vpcEndpointId: The interface VPC endpoint identifier.

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
    Interface = "Interface"
    """Interface.

    An interface endpoint is an elastic network interface with a private IP
    address that serves as an entry point for traffic destined to a supported
    service.

    Stability:
        experimental
    """
    Gateway = "Gateway"
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

class VpcNetworkProvider(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.VpcNetworkProvider"):
    """Context provider to discover and import existing VPCs.

    Stability:
        experimental
    """
    def __init__(self, context: aws_cdk.cdk.Construct, *, is_default: typing.Optional[bool]=None, tags: typing.Optional[typing.Mapping[str,str]]=None, vpc_id: typing.Optional[str]=None, vpc_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            context: -
            options: -
            isDefault: Whether to match the default VPC. Default: Don't care whether we return the default VPC
            tags: Tags on the VPC. The VPC must have all of these tags Default: Don't filter on tags
            vpcId: The ID of the VPC. If given, will import exactly this VPC. Default: Don't filter on vpcId
            vpcName: The name of the VPC. If given, will import the VPC with this name. Default: Don't filter on vpcName

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

        jsii.create(VpcNetworkProvider, self, [context, options])

    @property
    @jsii.member(jsii_name="vpcProps")
    def vpc_props(self) -> "VpcAttributes":
        """Return the VPC import props matching the filter.

        Stability:
            experimental
        """
        return jsii.get(self, "vpcProps")


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
class VpnConnection(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.VpnConnection"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc: "IVpc", ip: str, asn: typing.Optional[jsii.Number]=None, static_routes: typing.Optional[typing.List[str]]=None, tunnel_options: typing.Optional[typing.List["VpnTunnelOption"]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            vpc: The VPC to connect to.
            ip: The ip address of the customer gateway.
            asn: The ASN of the customer gateway. Default: 65000
            staticRoutes: The static routes to be routed from the VPN gateway to the customer gateway. Default: Dynamic routing (BGP)
            tunnelOptions: The tunnel options for the VPN connection. At most two elements (one per tunnel). Duplicates not allowed. Default: Amazon generated tunnel options

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
    def metric_all(cls, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for all VPN connections in the account/region.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.sinvoke(cls, "metricAll", [metric_name, props])

    @jsii.member(jsii_name="metricAllTunnelDataIn")
    @classmethod
    def metric_all_tunnel_data_in(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the tunnel data in of all VPN connections in the account/region.

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.sinvoke(cls, "metricAllTunnelDataIn", [props])

    @jsii.member(jsii_name="metricAllTunnelDataOut")
    @classmethod
    def metric_all_tunnel_data_out(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the tunnel data out of all VPN connections.

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.sinvoke(cls, "metricAllTunnelDataOut", [props])

    @jsii.member(jsii_name="metricAllTunnelState")
    @classmethod
    def metric_all_tunnel_state(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the tunnel state of all VPN connections in the account/region.

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.sinvoke(cls, "metricAllTunnelState", [props])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this VPNConnection.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricTunnelDataIn")
    def metric_tunnel_data_in(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The bytes received through the VPN tunnel.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricTunnelDataIn", [props])

    @jsii.member(jsii_name="metricTunnelDataOut")
    def metric_tunnel_data_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The bytes sent through the VPN tunnel.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricTunnelDataOut", [props])

    @jsii.member(jsii_name="metricTunnelState")
    def metric_tunnel_state(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The state of the tunnel. 0 indicates DOWN and 1 indicates UP.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

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
    IPsec1 = "IPsec1"
    """The IPsec 1 VPN connection type.

    Stability:
        experimental
    """
    Dummy = "Dummy"
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

@jsii.implements(IMachineImageSource)
class WindowsImage(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.WindowsImage"):
    """Select the latest version of the indicated Windows version.

    The AMI ID is selected using the values published to the SSM parameter store.

    https://aws.amazon.com/blogs/mt/query-for-the-latest-windows-ami-using-systems-manager-parameter-store/

    Stability:
        experimental
    """
    def __init__(self, version: "WindowsVersion") -> None:
        """
        Arguments:
            version: -

        Stability:
            experimental
        """
        jsii.create(WindowsImage, self, [version])

    @jsii.member(jsii_name="getImage")
    def get_image(self, scope: aws_cdk.cdk.Construct) -> "MachineImage":
        """Return the image to use in the given context.

        Arguments:
            scope: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getImage", [scope])

    @property
    @jsii.member(jsii_name="version")
    def version(self) -> "WindowsVersion":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "version")


class WindowsOS(OperatingSystem, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ec2.WindowsOS"):
    """OS features specialized for Windows.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(WindowsOS, self, [])

    @jsii.member(jsii_name="createUserData")
    def create_user_data(self, scripts: typing.List[str]) -> str:
        """
        Arguments:
            scripts: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "createUserData", [scripts])

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "OperatingSystemType":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")


@jsii.enum(jsii_type="@aws-cdk/aws-ec2.WindowsVersion")
class WindowsVersion(enum.Enum):
    """The Windows version to use for the WindowsImage.

    Stability:
        experimental
    """
    WindowsServer2008SP2English64BitSQL2008SP4Express = "WindowsServer2008SP2English64BitSQL2008SP4Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMChineseSimplified64BitBase = "WindowsServer2012R2RTMChineseSimplified64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMChineseTraditional64BitBase = "WindowsServer2012R2RTMChineseTraditional64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMDutch64BitBase = "WindowsServer2012R2RTMDutch64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2014SP2Enterprise = "WindowsServer2012R2RTMEnglish64BitSQL2014SP2Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMHungarian64BitBase = "WindowsServer2012R2RTMHungarian64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitBase = "WindowsServer2012R2RTMJapanese64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishCoreContainers = "WindowsServer2016EnglishCoreContainers"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishCoreSQL2016SP1Web = "WindowsServer2016EnglishCoreSQL2016SP1Web"
    """
    Stability:
        experimental
    """
    WindowsServer2016GermanFullBase = "WindowsServer2016GermanFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2003R2SP2LanguagePacks32BitBase = "WindowsServer2003R2SP2LanguagePacks32BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1English64BitSQL2008R2SP3Web = "WindowsServer2008R2SP1English64BitSQL2008R2SP3Web"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1English64BitSQL2012SP4Express = "WindowsServer2008R2SP1English64BitSQL2012SP4Express"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1PortugueseBrazil64BitCore = "WindowsServer2008R2SP1PortugueseBrazil64BitCore"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2016SP2Standard = "WindowsServer2012R2RTMEnglish64BitSQL2016SP2Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitSQL2014SP2Express = "WindowsServer2012RTMEnglish64BitSQL2014SP2Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMItalian64BitBase = "WindowsServer2012RTMItalian64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishCoreSQL2016SP1Express = "WindowsServer2016EnglishCoreSQL2016SP1Express"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishDeepLearning = "WindowsServer2016EnglishDeepLearning"
    """
    Stability:
        experimental
    """
    WindowsServer2019ItalianFullBase = "WindowsServer2019ItalianFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1Korean64BitBase = "WindowsServer2008R2SP1Korean64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2016SP1Express = "WindowsServer2012R2RTMEnglish64BitSQL2016SP1Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitSQL2016SP2Web = "WindowsServer2012R2RTMJapanese64BitSQL2016SP2Web"
    """
    Stability:
        experimental
    """
    WindowsServer2016JapaneseFullSQL2016SP2Web = "WindowsServer2016JapaneseFullSQL2016SP2Web"
    """
    Stability:
        experimental
    """
    WindowsServer2016KoreanFullBase = "WindowsServer2016KoreanFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016KoreanFullSQL2016SP2Standard = "WindowsServer2016KoreanFullSQL2016SP2Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2016PortuguesePortugalFullBase = "WindowsServer2016PortuguesePortugalFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishFullSQL2017Web = "WindowsServer2019EnglishFullSQL2017Web"
    """
    Stability:
        experimental
    """
    WindowsServer2019FrenchFullBase = "WindowsServer2019FrenchFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019KoreanFullBase = "WindowsServer2019KoreanFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1ChineseHongKongSAR64BitBase = "WindowsServer2008R2SP1ChineseHongKongSAR64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1ChinesePRC64BitBase = "WindowsServer2008R2SP1ChinesePRC64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMFrench64BitBase = "WindowsServer2012RTMFrench64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullContainers = "WindowsServer2016EnglishFullContainers"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullSQL2016SP1Standard = "WindowsServer2016EnglishFullSQL2016SP1Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2016RussianFullBase = "WindowsServer2016RussianFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019ChineseSimplifiedFullBase = "WindowsServer2019ChineseSimplifiedFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishFullSQL2016SP2Standard = "WindowsServer2019EnglishFullSQL2016SP2Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2019HungarianFullBase = "WindowsServer2019HungarianFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1English64BitSQL2008R2SP3Express = "WindowsServer2008R2SP1English64BitSQL2008R2SP3Express"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1LanguagePacks64BitBase = "WindowsServer2008R2SP1LanguagePacks64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008SP2English32BitBase = "WindowsServer2008SP2English32BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2012SP4Enterprise = "WindowsServer2012R2RTMEnglish64BitSQL2012SP4Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMChineseTraditional64BitBase = "WindowsServer2012RTMChineseTraditional64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitSQL2008R2SP3Express = "WindowsServer2012RTMEnglish64BitSQL2008R2SP3Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitSQL2014SP2Standard = "WindowsServer2012RTMEnglish64BitSQL2014SP2Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMJapanese64BitSQL2014SP2Express = "WindowsServer2012RTMJapanese64BitSQL2014SP2Express"
    """
    Stability:
        experimental
    """
    WindowsServer2016PolishFullBase = "WindowsServer2016PolishFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishFullSQL2016SP2Web = "WindowsServer2019EnglishFullSQL2016SP2Web"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2014SP3Standard = "WindowsServer2012R2RTMEnglish64BitSQL2014SP3Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2016SP2Express = "WindowsServer2012R2RTMEnglish64BitSQL2016SP2Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglishDeepLearning = "WindowsServer2012R2RTMEnglishDeepLearning"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMGerman64BitBase = "WindowsServer2012R2RTMGerman64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitSQL2016SP1Express = "WindowsServer2012R2RTMJapanese64BitSQL2016SP1Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMRussian64BitBase = "WindowsServer2012R2RTMRussian64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMChineseTraditionalHongKongSAR64BitBase = "WindowsServer2012RTMChineseTraditionalHongKongSAR64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMHungarian64BitBase = "WindowsServer2012RTMHungarian64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMJapanese64BitSQL2014SP3Standard = "WindowsServer2012RTMJapanese64BitSQL2014SP3Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishFullHyperV = "WindowsServer2019EnglishFullHyperV"
    """
    Stability:
        experimental
    """
    WindowsServer2003R2SP2English64BitSQL2005SP4Express = "WindowsServer2003R2SP2English64BitSQL2005SP4Express"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1Japanese64BitSQL2012SP4Express = "WindowsServer2008R2SP1Japanese64BitSQL2012SP4Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMGerman64BitBase = "WindowsServer2012RTMGerman64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMJapanese64BitSQL2008R2SP3Standard = "WindowsServer2012RTMJapanese64BitSQL2008R2SP3Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullSQL2016SP2Standard = "WindowsServer2016EnglishFullSQL2016SP2Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishFullSQL2017Express = "WindowsServer2019EnglishFullSQL2017Express"
    """
    Stability:
        experimental
    """
    WindowsServer2019JapaneseFullBase = "WindowsServer2019JapaneseFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019RussianFullBase = "WindowsServer2019RussianFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2014SP2Standard = "WindowsServer2012R2RTMEnglish64BitSQL2014SP2Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMItalian64BitBase = "WindowsServer2012R2RTMItalian64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitBase = "WindowsServer2012RTMEnglish64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitSQL2008R2SP3Standard = "WindowsServer2012RTMEnglish64BitSQL2008R2SP3Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullHyperV = "WindowsServer2016EnglishFullHyperV"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullSQL2016SP2Enterprise = "WindowsServer2016EnglishFullSQL2016SP2Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2019ChineseTraditionalFullBase = "WindowsServer2019ChineseTraditionalFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishCoreBase = "WindowsServer2019EnglishCoreBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishCoreContainersLatest = "WindowsServer2019EnglishCoreContainersLatest"
    """
    Stability:
        experimental
    """
    WindowsServer2008SP2English64BitBase = "WindowsServer2008SP2English64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMFrench64BitBase = "WindowsServer2012R2RTMFrench64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMPolish64BitBase = "WindowsServer2012R2RTMPolish64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitSQL2012SP4Express = "WindowsServer2012RTMEnglish64BitSQL2012SP4Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitSQL2014SP3Standard = "WindowsServer2012RTMEnglish64BitSQL2014SP3Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMJapanese64BitSQL2012SP4Standard = "WindowsServer2012RTMJapanese64BitSQL2012SP4Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishCoreContainersLatest = "WindowsServer2016EnglishCoreContainersLatest"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishFullSQL2016SP2Express = "WindowsServer2019EnglishFullSQL2016SP2Express"
    """
    Stability:
        experimental
    """
    WindowsServer2019TurkishFullBase = "WindowsServer2019TurkishFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2014SP2Express = "WindowsServer2012R2RTMEnglish64BitSQL2014SP2Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2014SP3Web = "WindowsServer2012R2RTMEnglish64BitSQL2014SP3Web"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitSQL2016SP1Web = "WindowsServer2012R2RTMJapanese64BitSQL2016SP1Web"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMPortugueseBrazil64BitBase = "WindowsServer2012R2RTMPortugueseBrazil64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMPortuguesePortugal64BitBase = "WindowsServer2012R2RTMPortuguesePortugal64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMSwedish64BitBase = "WindowsServer2012R2RTMSwedish64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullSQL2016SP1Express = "WindowsServer2016EnglishFullSQL2016SP1Express"
    """
    Stability:
        experimental
    """
    WindowsServer2016ItalianFullBase = "WindowsServer2016ItalianFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016SpanishFullBase = "WindowsServer2016SpanishFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishFullSQL2017Standard = "WindowsServer2019EnglishFullSQL2017Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2003R2SP2LanguagePacks64BitSQL2005SP4Standard = "WindowsServer2003R2SP2LanguagePacks64BitSQL2005SP4Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1Japanese64BitSQL2008R2SP3Standard = "WindowsServer2008R2SP1Japanese64BitSQL2008R2SP3Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitSQL2016SP1Standard = "WindowsServer2012R2RTMJapanese64BitSQL2016SP1Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitSQL2008R2SP3Web = "WindowsServer2012RTMEnglish64BitSQL2008R2SP3Web"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMJapanese64BitSQL2014SP2Web = "WindowsServer2012RTMJapanese64BitSQL2014SP2Web"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishCoreSQL2016SP2Enterprise = "WindowsServer2016EnglishCoreSQL2016SP2Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2016PortugueseBrazilFullBase = "WindowsServer2016PortugueseBrazilFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishFullBase = "WindowsServer2019EnglishFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2003R2SP2English32BitBase = "WindowsServer2003R2SP2English32BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMCzech64BitBase = "WindowsServer2012R2RTMCzech64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2016SP1Standard = "WindowsServer2012R2RTMEnglish64BitSQL2016SP1Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitSQL2014SP2Express = "WindowsServer2012R2RTMJapanese64BitSQL2014SP2Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitSQL2012SP4Standard = "WindowsServer2012RTMEnglish64BitSQL2012SP4Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishCoreSQL2016SP1Enterprise = "WindowsServer2016EnglishCoreSQL2016SP1Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2016JapaneseFullSQL2016SP1Web = "WindowsServer2016JapaneseFullSQL2016SP1Web"
    """
    Stability:
        experimental
    """
    WindowsServer2016SwedishFullBase = "WindowsServer2016SwedishFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016TurkishFullBase = "WindowsServer2016TurkishFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1English64BitCoreSQL2012SP4Standard = "WindowsServer2008R2SP1English64BitCoreSQL2012SP4Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1LanguagePacks64BitSQL2008R2SP3Standard = "WindowsServer2008R2SP1LanguagePacks64BitSQL2008R2SP3Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMCzech64BitBase = "WindowsServer2012RTMCzech64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMTurkish64BitBase = "WindowsServer2012RTMTurkish64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016DutchFullBase = "WindowsServer2016DutchFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullSQL2016SP2Express = "WindowsServer2016EnglishFullSQL2016SP2Express"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullSQL2017Enterprise = "WindowsServer2016EnglishFullSQL2017Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2016HungarianFullBase = "WindowsServer2016HungarianFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016KoreanFullSQL2016SP1Standard = "WindowsServer2016KoreanFullSQL2016SP1Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2019SpanishFullBase = "WindowsServer2019SpanishFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2003R2SP2English64BitBase = "WindowsServer2003R2SP2English64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1English64BitBase = "WindowsServer2008R2SP1English64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1LanguagePacks64BitSQL2008R2SP3Express = "WindowsServer2008R2SP1LanguagePacks64BitSQL2008R2SP3Express"
    """
    Stability:
        experimental
    """
    WindowsServer2008SP2PortugueseBrazil64BitBase = "WindowsServer2008SP2PortugueseBrazil64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2016SP1Web = "WindowsServer2012R2RTMEnglish64BitSQL2016SP1Web"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitSQL2014SP3Express = "WindowsServer2012R2RTMJapanese64BitSQL2014SP3Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitSQL2016SP2Enterprise = "WindowsServer2012R2RTMJapanese64BitSQL2016SP2Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMJapanese64BitBase = "WindowsServer2012RTMJapanese64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishFullContainersLatest = "WindowsServer2019EnglishFullContainersLatest"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishFullSQL2017Enterprise = "WindowsServer2019EnglishFullSQL2017Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer1709EnglishCoreContainersLatest = "WindowsServer1709EnglishCoreContainersLatest"
    """
    Stability:
        experimental
    """
    WindowsServer1803EnglishCoreBase = "WindowsServer1803EnglishCoreBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1English64BitSQL2012SP4Web = "WindowsServer2008R2SP1English64BitSQL2012SP4Web"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1Japanese64BitBase = "WindowsServer2008R2SP1Japanese64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008SP2English64BitSQL2008SP4Standard = "WindowsServer2008SP2English64BitSQL2008SP4Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitBase = "WindowsServer2012R2RTMEnglish64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMPortugueseBrazil64BitBase = "WindowsServer2012RTMPortugueseBrazil64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullSQL2016SP1Web = "WindowsServer2016EnglishFullSQL2016SP1Web"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishP3 = "WindowsServer2016EnglishP3"
    """
    Stability:
        experimental
    """
    WindowsServer2016JapaneseFullSQL2016SP1Enterprise = "WindowsServer2016JapaneseFullSQL2016SP1Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2003R2SP2LanguagePacks64BitBase = "WindowsServer2003R2SP2LanguagePacks64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMChineseTraditionalHongKong64BitBase = "WindowsServer2012R2RTMChineseTraditionalHongKong64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2014SP3Express = "WindowsServer2012R2RTMEnglish64BitSQL2014SP3Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2016SP2Enterprise = "WindowsServer2012R2RTMEnglish64BitSQL2016SP2Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMChineseSimplified64BitBase = "WindowsServer2012RTMChineseSimplified64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitSQL2012SP4Web = "WindowsServer2012RTMEnglish64BitSQL2012SP4Web"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMJapanese64BitSQL2014SP3Web = "WindowsServer2012RTMJapanese64BitSQL2014SP3Web"
    """
    Stability:
        experimental
    """
    WindowsServer2016JapaneseFullBase = "WindowsServer2016JapaneseFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016JapaneseFullSQL2016SP1Express = "WindowsServer2016JapaneseFullSQL2016SP1Express"
    """
    Stability:
        experimental
    """
    WindowsServer1803EnglishCoreContainersLatest = "WindowsServer1803EnglishCoreContainersLatest"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1Japanese64BitSQL2012SP4Standard = "WindowsServer2008R2SP1Japanese64BitSQL2012SP4Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitCore = "WindowsServer2012R2RTMEnglish64BitCore"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2014SP2Web = "WindowsServer2012R2RTMEnglish64BitSQL2014SP2Web"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2014SP3Enterprise = "WindowsServer2012R2RTMEnglish64BitSQL2014SP3Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitSQL2016SP2Standard = "WindowsServer2012R2RTMJapanese64BitSQL2016SP2Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitSQL2014SP3Web = "WindowsServer2012RTMEnglish64BitSQL2014SP3Web"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMSwedish64BitBase = "WindowsServer2012RTMSwedish64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016ChineseSimplifiedFullBase = "WindowsServer2016ChineseSimplifiedFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019PolishFullBase = "WindowsServer2019PolishFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1Japanese64BitSQL2008R2SP3Web = "WindowsServer2008R2SP1Japanese64BitSQL2008R2SP3Web"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1PortugueseBrazil64BitBase = "WindowsServer2008R2SP1PortugueseBrazil64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitSQL2016SP1Enterprise = "WindowsServer2012R2RTMJapanese64BitSQL2016SP1Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitSQL2016SP2Express = "WindowsServer2012R2RTMJapanese64BitSQL2016SP2Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitSQL2014SP3Express = "WindowsServer2012RTMEnglish64BitSQL2014SP3Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMJapanese64BitSQL2014SP2Standard = "WindowsServer2012RTMJapanese64BitSQL2014SP2Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishCoreBase = "WindowsServer2016EnglishCoreBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullBase = "WindowsServer2016EnglishFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullSQL2017Web = "WindowsServer2016EnglishFullSQL2017Web"
    """
    Stability:
        experimental
    """
    WindowsServer2019GermanFullBase = "WindowsServer2019GermanFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2003R2SP2English64BitSQL2005SP4Standard = "WindowsServer2003R2SP2English64BitSQL2005SP4Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1English64BitSQL2012SP4Enterprise = "WindowsServer2008R2SP1English64BitSQL2012SP4Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1Japanese64BitSQL2008R2SP3Express = "WindowsServer2008R2SP1Japanese64BitSQL2008R2SP3Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2016SP1Enterprise = "WindowsServer2012R2RTMEnglish64BitSQL2016SP1Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMEnglish64BitSQL2014SP2Web = "WindowsServer2012RTMEnglish64BitSQL2014SP2Web"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMJapanese64BitSQL2008R2SP3Express = "WindowsServer2012RTMJapanese64BitSQL2008R2SP3Express"
    """
    Stability:
        experimental
    """
    WindowsServer2016FrenchFullBase = "WindowsServer2016FrenchFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016JapaneseFullSQL2016SP2Enterprise = "WindowsServer2016JapaneseFullSQL2016SP2Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2019CzechFullBase = "WindowsServer2019CzechFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer1809EnglishCoreBase = "WindowsServer1809EnglishCoreBase"
    """
    Stability:
        experimental
    """
    WindowsServer1809EnglishCoreContainersLatest = "WindowsServer1809EnglishCoreContainersLatest"
    """
    Stability:
        experimental
    """
    WindowsServer2003R2SP2LanguagePacks64BitSQL2005SP4Express = "WindowsServer2003R2SP2LanguagePacks64BitSQL2005SP4Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMTurkish64BitBase = "WindowsServer2012R2RTMTurkish64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMJapanese64BitSQL2012SP4Web = "WindowsServer2012RTMJapanese64BitSQL2012SP4Web"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMPolish64BitBase = "WindowsServer2012RTMPolish64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMSpanish64BitBase = "WindowsServer2012RTMSpanish64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullSQL2016SP1Enterprise = "WindowsServer2016EnglishFullSQL2016SP1Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2016JapaneseFullSQL2016SP2Express = "WindowsServer2016JapaneseFullSQL2016SP2Express"
    """
    Stability:
        experimental
    """
    WindowsServer2019EnglishFullSQL2016SP2Enterprise = "WindowsServer2019EnglishFullSQL2016SP2Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer1709EnglishCoreBase = "WindowsServer1709EnglishCoreBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1English64BitSQL2012RTMSP2Enterprise = "WindowsServer2008R2SP1English64BitSQL2012RTMSP2Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1English64BitSQL2012SP4Standard = "WindowsServer2008R2SP1English64BitSQL2012SP4Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2008SP2PortugueseBrazil32BitBase = "WindowsServer2008SP2PortugueseBrazil32BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitSQL2014SP2Standard = "WindowsServer2012R2RTMJapanese64BitSQL2014SP2Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMJapanese64BitSQL2012SP4Express = "WindowsServer2012RTMJapanese64BitSQL2012SP4Express"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMPortuguesePortugal64BitBase = "WindowsServer2012RTMPortuguesePortugal64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016CzechFullBase = "WindowsServer2016CzechFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016JapaneseFullSQL2016SP1Standard = "WindowsServer2016JapaneseFullSQL2016SP1Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2019DutchFullBase = "WindowsServer2019DutchFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1English64BitCore = "WindowsServer2008R2SP1English64BitCore"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitSQL2016SP2Web = "WindowsServer2012R2RTMEnglish64BitSQL2016SP2Web"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMKorean64BitBase = "WindowsServer2012R2RTMKorean64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMDutch64BitBase = "WindowsServer2012RTMDutch64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016English64BitSQL2012SP4Enterprise = "WindowsServer2016English64BitSQL2012SP4Enterprise"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishCoreSQL2016SP1Standard = "WindowsServer2016EnglishCoreSQL2016SP1Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishCoreSQL2016SP2Express = "WindowsServer2016EnglishCoreSQL2016SP2Express"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishCoreSQL2016SP2Web = "WindowsServer2016EnglishCoreSQL2016SP2Web"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullSQL2017Standard = "WindowsServer2016EnglishFullSQL2017Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2019PortugueseBrazilFullBase = "WindowsServer2019PortugueseBrazilFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1English64BitSQL2008R2SP3Standard = "WindowsServer2008R2SP1English64BitSQL2008R2SP3Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2008R2SP1English64BitSharePoint2010SP2Foundation = "WindowsServer2008R2SP1English64BitSharePoint2010SP2Foundation"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglishP3 = "WindowsServer2012R2RTMEnglishP3"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMJapanese64BitSQL2014SP3Standard = "WindowsServer2012R2RTMJapanese64BitSQL2014SP3Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMSpanish64BitBase = "WindowsServer2012R2RTMSpanish64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMJapanese64BitSQL2014SP3Express = "WindowsServer2012RTMJapanese64BitSQL2014SP3Express"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishCoreSQL2016SP2Standard = "WindowsServer2016EnglishCoreSQL2016SP2Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2016JapaneseFullSQL2016SP2Standard = "WindowsServer2016JapaneseFullSQL2016SP2Standard"
    """
    Stability:
        experimental
    """
    WindowsServer2019PortuguesePortugalFullBase = "WindowsServer2019PortuguesePortugalFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2019SwedishFullBase = "WindowsServer2019SwedishFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012R2RTMEnglish64BitHyperV = "WindowsServer2012R2RTMEnglish64BitHyperV"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMKorean64BitBase = "WindowsServer2012RTMKorean64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2012RTMRussian64BitBase = "WindowsServer2012RTMRussian64BitBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016ChineseTraditionalFullBase = "WindowsServer2016ChineseTraditionalFullBase"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullSQL2016SP2Web = "WindowsServer2016EnglishFullSQL2016SP2Web"
    """
    Stability:
        experimental
    """
    WindowsServer2016EnglishFullSQL2017Express = "WindowsServer2016EnglishFullSQL2017Express"
    """
    Stability:
        experimental
    """

__all__ = ["AllTraffic", "AmazonLinuxEdition", "AmazonLinuxGeneration", "AmazonLinuxImage", "AmazonLinuxImageProps", "AmazonLinuxStorage", "AmazonLinuxVirt", "AnyIPv4", "AnyIPv6", "CfnCapacityReservation", "CfnCapacityReservationProps", "CfnCustomerGateway", "CfnCustomerGatewayProps", "CfnDHCPOptions", "CfnDHCPOptionsProps", "CfnEC2Fleet", "CfnEC2FleetProps", "CfnEIP", "CfnEIPAssociation", "CfnEIPAssociationProps", "CfnEIPProps", "CfnEgressOnlyInternetGateway", "CfnEgressOnlyInternetGatewayProps", "CfnFlowLog", "CfnFlowLogProps", "CfnHost", "CfnHostProps", "CfnInstance", "CfnInstanceProps", "CfnInternetGateway", "CfnInternetGatewayProps", "CfnLaunchTemplate", "CfnLaunchTemplateProps", "CfnNatGateway", "CfnNatGatewayProps", "CfnNetworkAcl", "CfnNetworkAclEntry", "CfnNetworkAclEntryProps", "CfnNetworkAclProps", "CfnNetworkInterface", "CfnNetworkInterfaceAttachment", "CfnNetworkInterfaceAttachmentProps", "CfnNetworkInterfacePermission", "CfnNetworkInterfacePermissionProps", "CfnNetworkInterfaceProps", "CfnPlacementGroup", "CfnPlacementGroupProps", "CfnRoute", "CfnRouteProps", "CfnRouteTable", "CfnRouteTableProps", "CfnSecurityGroup", "CfnSecurityGroupEgress", "CfnSecurityGroupEgressProps", "CfnSecurityGroupIngress", "CfnSecurityGroupIngressProps", "CfnSecurityGroupProps", "CfnSpotFleet", "CfnSpotFleetProps", "CfnSubnet", "CfnSubnetCidrBlock", "CfnSubnetCidrBlockProps", "CfnSubnetNetworkAclAssociation", "CfnSubnetNetworkAclAssociationProps", "CfnSubnetProps", "CfnSubnetRouteTableAssociation", "CfnSubnetRouteTableAssociationProps", "CfnTransitGateway", "CfnTransitGatewayAttachment", "CfnTransitGatewayAttachmentProps", "CfnTransitGatewayProps", "CfnTransitGatewayRoute", "CfnTransitGatewayRouteProps", "CfnTransitGatewayRouteTable", "CfnTransitGatewayRouteTableAssociation", "CfnTransitGatewayRouteTableAssociationProps", "CfnTransitGatewayRouteTablePropagation", "CfnTransitGatewayRouteTablePropagationProps", "CfnTransitGatewayRouteTableProps", "CfnVPC", "CfnVPCCidrBlock", "CfnVPCCidrBlockProps", "CfnVPCDHCPOptionsAssociation", "CfnVPCDHCPOptionsAssociationProps", "CfnVPCEndpoint", "CfnVPCEndpointConnectionNotification", "CfnVPCEndpointConnectionNotificationProps", "CfnVPCEndpointProps", "CfnVPCEndpointService", "CfnVPCEndpointServicePermissions", "CfnVPCEndpointServicePermissionsProps", "CfnVPCEndpointServiceProps", "CfnVPCGatewayAttachment", "CfnVPCGatewayAttachmentProps", "CfnVPCPeeringConnection", "CfnVPCPeeringConnectionProps", "CfnVPCProps", "CfnVPNConnection", "CfnVPNConnectionProps", "CfnVPNConnectionRoute", "CfnVPNConnectionRouteProps", "CfnVPNGateway", "CfnVPNGatewayProps", "CfnVPNGatewayRoutePropagation", "CfnVPNGatewayRoutePropagationProps", "CfnVolume", "CfnVolumeAttachment", "CfnVolumeAttachmentProps", "CfnVolumeProps", "CidrIPv4", "CidrIPv6", "ConnectionRule", "Connections", "ConnectionsProps", "DefaultInstanceTenancy", "GatewayVpcEndpoint", "GatewayVpcEndpointAwsService", "GatewayVpcEndpointOptions", "GatewayVpcEndpointProps", "GenericLinuxImage", "IConnectable", "IGatewayVpcEndpoint", "IGatewayVpcEndpointService", "IInterfaceVpcEndpoint", "IInterfaceVpcEndpointService", "IMachineImageSource", "IPortRange", "IPrivateSubnet", "IPublicSubnet", "ISecurityGroup", "ISecurityGroupRule", "ISubnet", "IVpc", "IVpcEndpoint", "IVpnConnection", "IcmpAllTypeCodes", "IcmpAllTypesAndCodes", "IcmpPing", "IcmpTypeAndCode", "InstanceClass", "InstanceSize", "InstanceType", "InstanceTypePair", "InterfaceVpcEndpoint", "InterfaceVpcEndpointAttributes", "InterfaceVpcEndpointAwsService", "InterfaceVpcEndpointOptions", "InterfaceVpcEndpointProps", "LinuxOS", "MachineImage", "OperatingSystem", "OperatingSystemType", "PrefixList", "PrivateSubnet", "PrivateSubnetAttributes", "PrivateSubnetProps", "Protocol", "PublicSubnet", "PublicSubnetAttributes", "PublicSubnetProps", "SecurityGroup", "SecurityGroupProps", "SelectedSubnets", "Subnet", "SubnetAttributes", "SubnetConfiguration", "SubnetProps", "SubnetSelection", "SubnetType", "TcpAllPorts", "TcpPort", "TcpPortRange", "UdpAllPorts", "UdpPort", "UdpPortRange", "Vpc", "VpcAttributes", "VpcEndpoint", "VpcEndpointType", "VpcLookupOptions", "VpcNetworkProvider", "VpcProps", "VpnConnection", "VpnConnectionOptions", "VpnConnectionProps", "VpnConnectionType", "VpnTunnelOption", "WindowsImage", "WindowsOS", "WindowsVersion", "__jsii_assembly__"]

publication.publish()
