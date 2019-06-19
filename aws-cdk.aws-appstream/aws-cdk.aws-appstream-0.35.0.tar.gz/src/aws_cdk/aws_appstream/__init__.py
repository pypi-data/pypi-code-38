import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-appstream", "0.35.0", __name__, "aws-appstream@0.35.0.jsii.tgz")
class CfnDirectoryConfig(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appstream.CfnDirectoryConfig"):
    """A CloudFormation ``AWS::AppStream::DirectoryConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-directoryconfig.html
    Stability:
        experimental
    cloudformationResource:
        AWS::AppStream::DirectoryConfig
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, directory_name: str, organizational_unit_distinguished_names: typing.List[str], service_account_credentials: typing.Union["ServiceAccountCredentialsProperty", aws_cdk.cdk.IResolvable]) -> None:
        """Create a new ``AWS::AppStream::DirectoryConfig``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            directoryName: ``AWS::AppStream::DirectoryConfig.DirectoryName``.
            organizationalUnitDistinguishedNames: ``AWS::AppStream::DirectoryConfig.OrganizationalUnitDistinguishedNames``.
            serviceAccountCredentials: ``AWS::AppStream::DirectoryConfig.ServiceAccountCredentials``.

        Stability:
            experimental
        """
        props: CfnDirectoryConfigProps = {"directoryName": directory_name, "organizationalUnitDistinguishedNames": organizational_unit_distinguished_names, "serviceAccountCredentials": service_account_credentials}

        jsii.create(CfnDirectoryConfig, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="directoryName")
    def directory_name(self) -> str:
        """``AWS::AppStream::DirectoryConfig.DirectoryName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-directoryconfig.html#cfn-appstream-directoryconfig-directoryname
        Stability:
            experimental
        """
        return jsii.get(self, "directoryName")

    @directory_name.setter
    def directory_name(self, value: str):
        return jsii.set(self, "directoryName", value)

    @property
    @jsii.member(jsii_name="organizationalUnitDistinguishedNames")
    def organizational_unit_distinguished_names(self) -> typing.List[str]:
        """``AWS::AppStream::DirectoryConfig.OrganizationalUnitDistinguishedNames``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-directoryconfig.html#cfn-appstream-directoryconfig-organizationalunitdistinguishednames
        Stability:
            experimental
        """
        return jsii.get(self, "organizationalUnitDistinguishedNames")

    @organizational_unit_distinguished_names.setter
    def organizational_unit_distinguished_names(self, value: typing.List[str]):
        return jsii.set(self, "organizationalUnitDistinguishedNames", value)

    @property
    @jsii.member(jsii_name="serviceAccountCredentials")
    def service_account_credentials(self) -> typing.Union["ServiceAccountCredentialsProperty", aws_cdk.cdk.IResolvable]:
        """``AWS::AppStream::DirectoryConfig.ServiceAccountCredentials``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-directoryconfig.html#cfn-appstream-directoryconfig-serviceaccountcredentials
        Stability:
            experimental
        """
        return jsii.get(self, "serviceAccountCredentials")

    @service_account_credentials.setter
    def service_account_credentials(self, value: typing.Union["ServiceAccountCredentialsProperty", aws_cdk.cdk.IResolvable]):
        return jsii.set(self, "serviceAccountCredentials", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnDirectoryConfig.ServiceAccountCredentialsProperty", jsii_struct_bases=[])
    class ServiceAccountCredentialsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-directoryconfig-serviceaccountcredentials.html
        Stability:
            experimental
        """
        accountName: str
        """``CfnDirectoryConfig.ServiceAccountCredentialsProperty.AccountName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-directoryconfig-serviceaccountcredentials.html#cfn-appstream-directoryconfig-serviceaccountcredentials-accountname
        Stability:
            experimental
        """

        accountPassword: str
        """``CfnDirectoryConfig.ServiceAccountCredentialsProperty.AccountPassword``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-directoryconfig-serviceaccountcredentials.html#cfn-appstream-directoryconfig-serviceaccountcredentials-accountpassword
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnDirectoryConfigProps", jsii_struct_bases=[])
class CfnDirectoryConfigProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::AppStream::DirectoryConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-directoryconfig.html
    Stability:
        experimental
    """
    directoryName: str
    """``AWS::AppStream::DirectoryConfig.DirectoryName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-directoryconfig.html#cfn-appstream-directoryconfig-directoryname
    Stability:
        experimental
    """

    organizationalUnitDistinguishedNames: typing.List[str]
    """``AWS::AppStream::DirectoryConfig.OrganizationalUnitDistinguishedNames``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-directoryconfig.html#cfn-appstream-directoryconfig-organizationalunitdistinguishednames
    Stability:
        experimental
    """

    serviceAccountCredentials: typing.Union["CfnDirectoryConfig.ServiceAccountCredentialsProperty", aws_cdk.cdk.IResolvable]
    """``AWS::AppStream::DirectoryConfig.ServiceAccountCredentials``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-directoryconfig.html#cfn-appstream-directoryconfig-serviceaccountcredentials
    Stability:
        experimental
    """

class CfnFleet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appstream.CfnFleet"):
    """A CloudFormation ``AWS::AppStream::Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html
    Stability:
        experimental
    cloudformationResource:
        AWS::AppStream::Fleet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, compute_capacity: typing.Union[aws_cdk.cdk.IResolvable, "ComputeCapacityProperty"], instance_type: str, description: typing.Optional[str]=None, disconnect_timeout_in_seconds: typing.Optional[jsii.Number]=None, display_name: typing.Optional[str]=None, domain_join_info: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["DomainJoinInfoProperty"]]]=None, enable_default_internet_access: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, fleet_type: typing.Optional[str]=None, image_arn: typing.Optional[str]=None, image_name: typing.Optional[str]=None, max_user_duration_in_seconds: typing.Optional[jsii.Number]=None, name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VpcConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::AppStream::Fleet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            computeCapacity: ``AWS::AppStream::Fleet.ComputeCapacity``.
            instanceType: ``AWS::AppStream::Fleet.InstanceType``.
            description: ``AWS::AppStream::Fleet.Description``.
            disconnectTimeoutInSeconds: ``AWS::AppStream::Fleet.DisconnectTimeoutInSeconds``.
            displayName: ``AWS::AppStream::Fleet.DisplayName``.
            domainJoinInfo: ``AWS::AppStream::Fleet.DomainJoinInfo``.
            enableDefaultInternetAccess: ``AWS::AppStream::Fleet.EnableDefaultInternetAccess``.
            fleetType: ``AWS::AppStream::Fleet.FleetType``.
            imageArn: ``AWS::AppStream::Fleet.ImageArn``.
            imageName: ``AWS::AppStream::Fleet.ImageName``.
            maxUserDurationInSeconds: ``AWS::AppStream::Fleet.MaxUserDurationInSeconds``.
            name: ``AWS::AppStream::Fleet.Name``.
            tags: ``AWS::AppStream::Fleet.Tags``.
            vpcConfig: ``AWS::AppStream::Fleet.VpcConfig``.

        Stability:
            experimental
        """
        props: CfnFleetProps = {"computeCapacity": compute_capacity, "instanceType": instance_type}

        if description is not None:
            props["description"] = description

        if disconnect_timeout_in_seconds is not None:
            props["disconnectTimeoutInSeconds"] = disconnect_timeout_in_seconds

        if display_name is not None:
            props["displayName"] = display_name

        if domain_join_info is not None:
            props["domainJoinInfo"] = domain_join_info

        if enable_default_internet_access is not None:
            props["enableDefaultInternetAccess"] = enable_default_internet_access

        if fleet_type is not None:
            props["fleetType"] = fleet_type

        if image_arn is not None:
            props["imageArn"] = image_arn

        if image_name is not None:
            props["imageName"] = image_name

        if max_user_duration_in_seconds is not None:
            props["maxUserDurationInSeconds"] = max_user_duration_in_seconds

        if name is not None:
            props["name"] = name

        if tags is not None:
            props["tags"] = tags

        if vpc_config is not None:
            props["vpcConfig"] = vpc_config

        jsii.create(CfnFleet, self, [scope, id, props])

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
        """``AWS::AppStream::Fleet.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="computeCapacity")
    def compute_capacity(self) -> typing.Union[aws_cdk.cdk.IResolvable, "ComputeCapacityProperty"]:
        """``AWS::AppStream::Fleet.ComputeCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-computecapacity
        Stability:
            experimental
        """
        return jsii.get(self, "computeCapacity")

    @compute_capacity.setter
    def compute_capacity(self, value: typing.Union[aws_cdk.cdk.IResolvable, "ComputeCapacityProperty"]):
        return jsii.set(self, "computeCapacity", value)

    @property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> str:
        """``AWS::AppStream::Fleet.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-instancetype
        Stability:
            experimental
        """
        return jsii.get(self, "instanceType")

    @instance_type.setter
    def instance_type(self, value: str):
        return jsii.set(self, "instanceType", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::AppStream::Fleet.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="disconnectTimeoutInSeconds")
    def disconnect_timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
        """``AWS::AppStream::Fleet.DisconnectTimeoutInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-disconnecttimeoutinseconds
        Stability:
            experimental
        """
        return jsii.get(self, "disconnectTimeoutInSeconds")

    @disconnect_timeout_in_seconds.setter
    def disconnect_timeout_in_seconds(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "disconnectTimeoutInSeconds", value)

    @property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> typing.Optional[str]:
        """``AWS::AppStream::Fleet.DisplayName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-displayname
        Stability:
            experimental
        """
        return jsii.get(self, "displayName")

    @display_name.setter
    def display_name(self, value: typing.Optional[str]):
        return jsii.set(self, "displayName", value)

    @property
    @jsii.member(jsii_name="domainJoinInfo")
    def domain_join_info(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["DomainJoinInfoProperty"]]]:
        """``AWS::AppStream::Fleet.DomainJoinInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-domainjoininfo
        Stability:
            experimental
        """
        return jsii.get(self, "domainJoinInfo")

    @domain_join_info.setter
    def domain_join_info(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["DomainJoinInfoProperty"]]]):
        return jsii.set(self, "domainJoinInfo", value)

    @property
    @jsii.member(jsii_name="enableDefaultInternetAccess")
    def enable_default_internet_access(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::AppStream::Fleet.EnableDefaultInternetAccess``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-enabledefaultinternetaccess
        Stability:
            experimental
        """
        return jsii.get(self, "enableDefaultInternetAccess")

    @enable_default_internet_access.setter
    def enable_default_internet_access(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "enableDefaultInternetAccess", value)

    @property
    @jsii.member(jsii_name="fleetType")
    def fleet_type(self) -> typing.Optional[str]:
        """``AWS::AppStream::Fleet.FleetType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-fleettype
        Stability:
            experimental
        """
        return jsii.get(self, "fleetType")

    @fleet_type.setter
    def fleet_type(self, value: typing.Optional[str]):
        return jsii.set(self, "fleetType", value)

    @property
    @jsii.member(jsii_name="imageArn")
    def image_arn(self) -> typing.Optional[str]:
        """``AWS::AppStream::Fleet.ImageArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-imagearn
        Stability:
            experimental
        """
        return jsii.get(self, "imageArn")

    @image_arn.setter
    def image_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "imageArn", value)

    @property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> typing.Optional[str]:
        """``AWS::AppStream::Fleet.ImageName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-imagename
        Stability:
            experimental
        """
        return jsii.get(self, "imageName")

    @image_name.setter
    def image_name(self, value: typing.Optional[str]):
        return jsii.set(self, "imageName", value)

    @property
    @jsii.member(jsii_name="maxUserDurationInSeconds")
    def max_user_duration_in_seconds(self) -> typing.Optional[jsii.Number]:
        """``AWS::AppStream::Fleet.MaxUserDurationInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-maxuserdurationinseconds
        Stability:
            experimental
        """
        return jsii.get(self, "maxUserDurationInSeconds")

    @max_user_duration_in_seconds.setter
    def max_user_duration_in_seconds(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "maxUserDurationInSeconds", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::AppStream::Fleet.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="vpcConfig")
    def vpc_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VpcConfigProperty"]]]:
        """``AWS::AppStream::Fleet.VpcConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-vpcconfig
        Stability:
            experimental
        """
        return jsii.get(self, "vpcConfig")

    @vpc_config.setter
    def vpc_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VpcConfigProperty"]]]):
        return jsii.set(self, "vpcConfig", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnFleet.ComputeCapacityProperty", jsii_struct_bases=[])
    class ComputeCapacityProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-fleet-computecapacity.html
        Stability:
            experimental
        """
        desiredInstances: jsii.Number
        """``CfnFleet.ComputeCapacityProperty.DesiredInstances``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-fleet-computecapacity.html#cfn-appstream-fleet-computecapacity-desiredinstances
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnFleet.DomainJoinInfoProperty", jsii_struct_bases=[])
    class DomainJoinInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-fleet-domainjoininfo.html
        Stability:
            experimental
        """
        directoryName: str
        """``CfnFleet.DomainJoinInfoProperty.DirectoryName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-fleet-domainjoininfo.html#cfn-appstream-fleet-domainjoininfo-directoryname
        Stability:
            experimental
        """

        organizationalUnitDistinguishedName: str
        """``CfnFleet.DomainJoinInfoProperty.OrganizationalUnitDistinguishedName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-fleet-domainjoininfo.html#cfn-appstream-fleet-domainjoininfo-organizationalunitdistinguishedname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnFleet.VpcConfigProperty", jsii_struct_bases=[])
    class VpcConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-fleet-vpcconfig.html
        Stability:
            experimental
        """
        securityGroupIds: typing.List[str]
        """``CfnFleet.VpcConfigProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-fleet-vpcconfig.html#cfn-appstream-fleet-vpcconfig-securitygroupids
        Stability:
            experimental
        """

        subnetIds: typing.List[str]
        """``CfnFleet.VpcConfigProperty.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-fleet-vpcconfig.html#cfn-appstream-fleet-vpcconfig-subnetids
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnFleetProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::AppStream::Fleet.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-description
    Stability:
        experimental
    """
    disconnectTimeoutInSeconds: jsii.Number
    """``AWS::AppStream::Fleet.DisconnectTimeoutInSeconds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-disconnecttimeoutinseconds
    Stability:
        experimental
    """
    displayName: str
    """``AWS::AppStream::Fleet.DisplayName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-displayname
    Stability:
        experimental
    """
    domainJoinInfo: typing.Union[aws_cdk.cdk.IResolvable, "CfnFleet.DomainJoinInfoProperty"]
    """``AWS::AppStream::Fleet.DomainJoinInfo``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-domainjoininfo
    Stability:
        experimental
    """
    enableDefaultInternetAccess: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::AppStream::Fleet.EnableDefaultInternetAccess``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-enabledefaultinternetaccess
    Stability:
        experimental
    """
    fleetType: str
    """``AWS::AppStream::Fleet.FleetType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-fleettype
    Stability:
        experimental
    """
    imageArn: str
    """``AWS::AppStream::Fleet.ImageArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-imagearn
    Stability:
        experimental
    """
    imageName: str
    """``AWS::AppStream::Fleet.ImageName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-imagename
    Stability:
        experimental
    """
    maxUserDurationInSeconds: jsii.Number
    """``AWS::AppStream::Fleet.MaxUserDurationInSeconds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-maxuserdurationinseconds
    Stability:
        experimental
    """
    name: str
    """``AWS::AppStream::Fleet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-name
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::AppStream::Fleet.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-tags
    Stability:
        experimental
    """
    vpcConfig: typing.Union[aws_cdk.cdk.IResolvable, "CfnFleet.VpcConfigProperty"]
    """``AWS::AppStream::Fleet.VpcConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-vpcconfig
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnFleetProps", jsii_struct_bases=[_CfnFleetProps])
class CfnFleetProps(_CfnFleetProps):
    """Properties for defining a ``AWS::AppStream::Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html
    Stability:
        experimental
    """
    computeCapacity: typing.Union[aws_cdk.cdk.IResolvable, "CfnFleet.ComputeCapacityProperty"]
    """``AWS::AppStream::Fleet.ComputeCapacity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-computecapacity
    Stability:
        experimental
    """

    instanceType: str
    """``AWS::AppStream::Fleet.InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-fleet.html#cfn-appstream-fleet-instancetype
    Stability:
        experimental
    """

class CfnImageBuilder(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appstream.CfnImageBuilder"):
    """A CloudFormation ``AWS::AppStream::ImageBuilder``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html
    Stability:
        experimental
    cloudformationResource:
        AWS::AppStream::ImageBuilder
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, instance_type: str, appstream_agent_version: typing.Optional[str]=None, description: typing.Optional[str]=None, display_name: typing.Optional[str]=None, domain_join_info: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["DomainJoinInfoProperty"]]]=None, enable_default_internet_access: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, image_arn: typing.Optional[str]=None, image_name: typing.Optional[str]=None, name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VpcConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::AppStream::ImageBuilder``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            instanceType: ``AWS::AppStream::ImageBuilder.InstanceType``.
            appstreamAgentVersion: ``AWS::AppStream::ImageBuilder.AppstreamAgentVersion``.
            description: ``AWS::AppStream::ImageBuilder.Description``.
            displayName: ``AWS::AppStream::ImageBuilder.DisplayName``.
            domainJoinInfo: ``AWS::AppStream::ImageBuilder.DomainJoinInfo``.
            enableDefaultInternetAccess: ``AWS::AppStream::ImageBuilder.EnableDefaultInternetAccess``.
            imageArn: ``AWS::AppStream::ImageBuilder.ImageArn``.
            imageName: ``AWS::AppStream::ImageBuilder.ImageName``.
            name: ``AWS::AppStream::ImageBuilder.Name``.
            tags: ``AWS::AppStream::ImageBuilder.Tags``.
            vpcConfig: ``AWS::AppStream::ImageBuilder.VpcConfig``.

        Stability:
            experimental
        """
        props: CfnImageBuilderProps = {"instanceType": instance_type}

        if appstream_agent_version is not None:
            props["appstreamAgentVersion"] = appstream_agent_version

        if description is not None:
            props["description"] = description

        if display_name is not None:
            props["displayName"] = display_name

        if domain_join_info is not None:
            props["domainJoinInfo"] = domain_join_info

        if enable_default_internet_access is not None:
            props["enableDefaultInternetAccess"] = enable_default_internet_access

        if image_arn is not None:
            props["imageArn"] = image_arn

        if image_name is not None:
            props["imageName"] = image_name

        if name is not None:
            props["name"] = name

        if tags is not None:
            props["tags"] = tags

        if vpc_config is not None:
            props["vpcConfig"] = vpc_config

        jsii.create(CfnImageBuilder, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrStreamingUrl")
    def attr_streaming_url(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            StreamingUrl
        """
        return jsii.get(self, "attrStreamingUrl")

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
        """``AWS::AppStream::ImageBuilder.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> str:
        """``AWS::AppStream::ImageBuilder.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-instancetype
        Stability:
            experimental
        """
        return jsii.get(self, "instanceType")

    @instance_type.setter
    def instance_type(self, value: str):
        return jsii.set(self, "instanceType", value)

    @property
    @jsii.member(jsii_name="appstreamAgentVersion")
    def appstream_agent_version(self) -> typing.Optional[str]:
        """``AWS::AppStream::ImageBuilder.AppstreamAgentVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-appstreamagentversion
        Stability:
            experimental
        """
        return jsii.get(self, "appstreamAgentVersion")

    @appstream_agent_version.setter
    def appstream_agent_version(self, value: typing.Optional[str]):
        return jsii.set(self, "appstreamAgentVersion", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::AppStream::ImageBuilder.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> typing.Optional[str]:
        """``AWS::AppStream::ImageBuilder.DisplayName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-displayname
        Stability:
            experimental
        """
        return jsii.get(self, "displayName")

    @display_name.setter
    def display_name(self, value: typing.Optional[str]):
        return jsii.set(self, "displayName", value)

    @property
    @jsii.member(jsii_name="domainJoinInfo")
    def domain_join_info(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["DomainJoinInfoProperty"]]]:
        """``AWS::AppStream::ImageBuilder.DomainJoinInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-domainjoininfo
        Stability:
            experimental
        """
        return jsii.get(self, "domainJoinInfo")

    @domain_join_info.setter
    def domain_join_info(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["DomainJoinInfoProperty"]]]):
        return jsii.set(self, "domainJoinInfo", value)

    @property
    @jsii.member(jsii_name="enableDefaultInternetAccess")
    def enable_default_internet_access(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::AppStream::ImageBuilder.EnableDefaultInternetAccess``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-enabledefaultinternetaccess
        Stability:
            experimental
        """
        return jsii.get(self, "enableDefaultInternetAccess")

    @enable_default_internet_access.setter
    def enable_default_internet_access(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "enableDefaultInternetAccess", value)

    @property
    @jsii.member(jsii_name="imageArn")
    def image_arn(self) -> typing.Optional[str]:
        """``AWS::AppStream::ImageBuilder.ImageArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-imagearn
        Stability:
            experimental
        """
        return jsii.get(self, "imageArn")

    @image_arn.setter
    def image_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "imageArn", value)

    @property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> typing.Optional[str]:
        """``AWS::AppStream::ImageBuilder.ImageName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-imagename
        Stability:
            experimental
        """
        return jsii.get(self, "imageName")

    @image_name.setter
    def image_name(self, value: typing.Optional[str]):
        return jsii.set(self, "imageName", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::AppStream::ImageBuilder.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="vpcConfig")
    def vpc_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VpcConfigProperty"]]]:
        """``AWS::AppStream::ImageBuilder.VpcConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-vpcconfig
        Stability:
            experimental
        """
        return jsii.get(self, "vpcConfig")

    @vpc_config.setter
    def vpc_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VpcConfigProperty"]]]):
        return jsii.set(self, "vpcConfig", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnImageBuilder.DomainJoinInfoProperty", jsii_struct_bases=[])
    class DomainJoinInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-imagebuilder-domainjoininfo.html
        Stability:
            experimental
        """
        directoryName: str
        """``CfnImageBuilder.DomainJoinInfoProperty.DirectoryName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-imagebuilder-domainjoininfo.html#cfn-appstream-imagebuilder-domainjoininfo-directoryname
        Stability:
            experimental
        """

        organizationalUnitDistinguishedName: str
        """``CfnImageBuilder.DomainJoinInfoProperty.OrganizationalUnitDistinguishedName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-imagebuilder-domainjoininfo.html#cfn-appstream-imagebuilder-domainjoininfo-organizationalunitdistinguishedname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnImageBuilder.VpcConfigProperty", jsii_struct_bases=[])
    class VpcConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-imagebuilder-vpcconfig.html
        Stability:
            experimental
        """
        securityGroupIds: typing.List[str]
        """``CfnImageBuilder.VpcConfigProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-imagebuilder-vpcconfig.html#cfn-appstream-imagebuilder-vpcconfig-securitygroupids
        Stability:
            experimental
        """

        subnetIds: typing.List[str]
        """``CfnImageBuilder.VpcConfigProperty.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-imagebuilder-vpcconfig.html#cfn-appstream-imagebuilder-vpcconfig-subnetids
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnImageBuilderProps(jsii.compat.TypedDict, total=False):
    appstreamAgentVersion: str
    """``AWS::AppStream::ImageBuilder.AppstreamAgentVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-appstreamagentversion
    Stability:
        experimental
    """
    description: str
    """``AWS::AppStream::ImageBuilder.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-description
    Stability:
        experimental
    """
    displayName: str
    """``AWS::AppStream::ImageBuilder.DisplayName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-displayname
    Stability:
        experimental
    """
    domainJoinInfo: typing.Union[aws_cdk.cdk.IResolvable, "CfnImageBuilder.DomainJoinInfoProperty"]
    """``AWS::AppStream::ImageBuilder.DomainJoinInfo``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-domainjoininfo
    Stability:
        experimental
    """
    enableDefaultInternetAccess: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::AppStream::ImageBuilder.EnableDefaultInternetAccess``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-enabledefaultinternetaccess
    Stability:
        experimental
    """
    imageArn: str
    """``AWS::AppStream::ImageBuilder.ImageArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-imagearn
    Stability:
        experimental
    """
    imageName: str
    """``AWS::AppStream::ImageBuilder.ImageName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-imagename
    Stability:
        experimental
    """
    name: str
    """``AWS::AppStream::ImageBuilder.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-name
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::AppStream::ImageBuilder.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-tags
    Stability:
        experimental
    """
    vpcConfig: typing.Union[aws_cdk.cdk.IResolvable, "CfnImageBuilder.VpcConfigProperty"]
    """``AWS::AppStream::ImageBuilder.VpcConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-vpcconfig
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnImageBuilderProps", jsii_struct_bases=[_CfnImageBuilderProps])
class CfnImageBuilderProps(_CfnImageBuilderProps):
    """Properties for defining a ``AWS::AppStream::ImageBuilder``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html
    Stability:
        experimental
    """
    instanceType: str
    """``AWS::AppStream::ImageBuilder.InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-imagebuilder.html#cfn-appstream-imagebuilder-instancetype
    Stability:
        experimental
    """

class CfnStack(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appstream.CfnStack"):
    """A CloudFormation ``AWS::AppStream::Stack``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html
    Stability:
        experimental
    cloudformationResource:
        AWS::AppStream::Stack
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, application_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ApplicationSettingsProperty"]]]=None, attributes_to_delete: typing.Optional[typing.List[str]]=None, delete_storage_connectors: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, description: typing.Optional[str]=None, display_name: typing.Optional[str]=None, feedback_url: typing.Optional[str]=None, name: typing.Optional[str]=None, redirect_url: typing.Optional[str]=None, storage_connectors: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "StorageConnectorProperty"]]]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, user_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "UserSettingProperty"]]]]]=None) -> None:
        """Create a new ``AWS::AppStream::Stack``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            applicationSettings: ``AWS::AppStream::Stack.ApplicationSettings``.
            attributesToDelete: ``AWS::AppStream::Stack.AttributesToDelete``.
            deleteStorageConnectors: ``AWS::AppStream::Stack.DeleteStorageConnectors``.
            description: ``AWS::AppStream::Stack.Description``.
            displayName: ``AWS::AppStream::Stack.DisplayName``.
            feedbackUrl: ``AWS::AppStream::Stack.FeedbackURL``.
            name: ``AWS::AppStream::Stack.Name``.
            redirectUrl: ``AWS::AppStream::Stack.RedirectURL``.
            storageConnectors: ``AWS::AppStream::Stack.StorageConnectors``.
            tags: ``AWS::AppStream::Stack.Tags``.
            userSettings: ``AWS::AppStream::Stack.UserSettings``.

        Stability:
            experimental
        """
        props: CfnStackProps = {}

        if application_settings is not None:
            props["applicationSettings"] = application_settings

        if attributes_to_delete is not None:
            props["attributesToDelete"] = attributes_to_delete

        if delete_storage_connectors is not None:
            props["deleteStorageConnectors"] = delete_storage_connectors

        if description is not None:
            props["description"] = description

        if display_name is not None:
            props["displayName"] = display_name

        if feedback_url is not None:
            props["feedbackUrl"] = feedback_url

        if name is not None:
            props["name"] = name

        if redirect_url is not None:
            props["redirectUrl"] = redirect_url

        if storage_connectors is not None:
            props["storageConnectors"] = storage_connectors

        if tags is not None:
            props["tags"] = tags

        if user_settings is not None:
            props["userSettings"] = user_settings

        jsii.create(CfnStack, self, [scope, id, props])

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
        """``AWS::AppStream::Stack.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="applicationSettings")
    def application_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ApplicationSettingsProperty"]]]:
        """``AWS::AppStream::Stack.ApplicationSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-applicationsettings
        Stability:
            experimental
        """
        return jsii.get(self, "applicationSettings")

    @application_settings.setter
    def application_settings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ApplicationSettingsProperty"]]]):
        return jsii.set(self, "applicationSettings", value)

    @property
    @jsii.member(jsii_name="attributesToDelete")
    def attributes_to_delete(self) -> typing.Optional[typing.List[str]]:
        """``AWS::AppStream::Stack.AttributesToDelete``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-attributestodelete
        Stability:
            experimental
        """
        return jsii.get(self, "attributesToDelete")

    @attributes_to_delete.setter
    def attributes_to_delete(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "attributesToDelete", value)

    @property
    @jsii.member(jsii_name="deleteStorageConnectors")
    def delete_storage_connectors(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::AppStream::Stack.DeleteStorageConnectors``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-deletestorageconnectors
        Stability:
            experimental
        """
        return jsii.get(self, "deleteStorageConnectors")

    @delete_storage_connectors.setter
    def delete_storage_connectors(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "deleteStorageConnectors", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::AppStream::Stack.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> typing.Optional[str]:
        """``AWS::AppStream::Stack.DisplayName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-displayname
        Stability:
            experimental
        """
        return jsii.get(self, "displayName")

    @display_name.setter
    def display_name(self, value: typing.Optional[str]):
        return jsii.set(self, "displayName", value)

    @property
    @jsii.member(jsii_name="feedbackUrl")
    def feedback_url(self) -> typing.Optional[str]:
        """``AWS::AppStream::Stack.FeedbackURL``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-feedbackurl
        Stability:
            experimental
        """
        return jsii.get(self, "feedbackUrl")

    @feedback_url.setter
    def feedback_url(self, value: typing.Optional[str]):
        return jsii.set(self, "feedbackUrl", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::AppStream::Stack.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="redirectUrl")
    def redirect_url(self) -> typing.Optional[str]:
        """``AWS::AppStream::Stack.RedirectURL``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-redirecturl
        Stability:
            experimental
        """
        return jsii.get(self, "redirectUrl")

    @redirect_url.setter
    def redirect_url(self, value: typing.Optional[str]):
        return jsii.set(self, "redirectUrl", value)

    @property
    @jsii.member(jsii_name="storageConnectors")
    def storage_connectors(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "StorageConnectorProperty"]]]]]:
        """``AWS::AppStream::Stack.StorageConnectors``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-storageconnectors
        Stability:
            experimental
        """
        return jsii.get(self, "storageConnectors")

    @storage_connectors.setter
    def storage_connectors(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "StorageConnectorProperty"]]]]]):
        return jsii.set(self, "storageConnectors", value)

    @property
    @jsii.member(jsii_name="userSettings")
    def user_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "UserSettingProperty"]]]]]:
        """``AWS::AppStream::Stack.UserSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-usersettings
        Stability:
            experimental
        """
        return jsii.get(self, "userSettings")

    @user_settings.setter
    def user_settings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "UserSettingProperty"]]]]]):
        return jsii.set(self, "userSettings", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ApplicationSettingsProperty(jsii.compat.TypedDict, total=False):
        settingsGroup: str
        """``CfnStack.ApplicationSettingsProperty.SettingsGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-stack-applicationsettings.html#cfn-appstream-stack-applicationsettings-settingsgroup
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnStack.ApplicationSettingsProperty", jsii_struct_bases=[_ApplicationSettingsProperty])
    class ApplicationSettingsProperty(_ApplicationSettingsProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-stack-applicationsettings.html
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnStack.ApplicationSettingsProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-stack-applicationsettings.html#cfn-appstream-stack-applicationsettings-enabled
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _StorageConnectorProperty(jsii.compat.TypedDict, total=False):
        domains: typing.List[str]
        """``CfnStack.StorageConnectorProperty.Domains``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-stack-storageconnector.html#cfn-appstream-stack-storageconnector-domains
        Stability:
            experimental
        """
        resourceIdentifier: str
        """``CfnStack.StorageConnectorProperty.ResourceIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-stack-storageconnector.html#cfn-appstream-stack-storageconnector-resourceidentifier
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnStack.StorageConnectorProperty", jsii_struct_bases=[_StorageConnectorProperty])
    class StorageConnectorProperty(_StorageConnectorProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-stack-storageconnector.html
        Stability:
            experimental
        """
        connectorType: str
        """``CfnStack.StorageConnectorProperty.ConnectorType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-stack-storageconnector.html#cfn-appstream-stack-storageconnector-connectortype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnStack.UserSettingProperty", jsii_struct_bases=[])
    class UserSettingProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-stack-usersetting.html
        Stability:
            experimental
        """
        action: str
        """``CfnStack.UserSettingProperty.Action``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-stack-usersetting.html#cfn-appstream-stack-usersetting-action
        Stability:
            experimental
        """

        permission: str
        """``CfnStack.UserSettingProperty.Permission``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appstream-stack-usersetting.html#cfn-appstream-stack-usersetting-permission
        Stability:
            experimental
        """


class CfnStackFleetAssociation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appstream.CfnStackFleetAssociation"):
    """A CloudFormation ``AWS::AppStream::StackFleetAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackfleetassociation.html
    Stability:
        experimental
    cloudformationResource:
        AWS::AppStream::StackFleetAssociation
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, fleet_name: str, stack_name: str) -> None:
        """Create a new ``AWS::AppStream::StackFleetAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            fleetName: ``AWS::AppStream::StackFleetAssociation.FleetName``.
            stackName: ``AWS::AppStream::StackFleetAssociation.StackName``.

        Stability:
            experimental
        """
        props: CfnStackFleetAssociationProps = {"fleetName": fleet_name, "stackName": stack_name}

        jsii.create(CfnStackFleetAssociation, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="fleetName")
    def fleet_name(self) -> str:
        """``AWS::AppStream::StackFleetAssociation.FleetName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackfleetassociation.html#cfn-appstream-stackfleetassociation-fleetname
        Stability:
            experimental
        """
        return jsii.get(self, "fleetName")

    @fleet_name.setter
    def fleet_name(self, value: str):
        return jsii.set(self, "fleetName", value)

    @property
    @jsii.member(jsii_name="stackName")
    def stack_name(self) -> str:
        """``AWS::AppStream::StackFleetAssociation.StackName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackfleetassociation.html#cfn-appstream-stackfleetassociation-stackname
        Stability:
            experimental
        """
        return jsii.get(self, "stackName")

    @stack_name.setter
    def stack_name(self, value: str):
        return jsii.set(self, "stackName", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnStackFleetAssociationProps", jsii_struct_bases=[])
class CfnStackFleetAssociationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::AppStream::StackFleetAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackfleetassociation.html
    Stability:
        experimental
    """
    fleetName: str
    """``AWS::AppStream::StackFleetAssociation.FleetName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackfleetassociation.html#cfn-appstream-stackfleetassociation-fleetname
    Stability:
        experimental
    """

    stackName: str
    """``AWS::AppStream::StackFleetAssociation.StackName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackfleetassociation.html#cfn-appstream-stackfleetassociation-stackname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnStackProps", jsii_struct_bases=[])
class CfnStackProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::AppStream::Stack``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html
    Stability:
        experimental
    """
    applicationSettings: typing.Union[aws_cdk.cdk.IResolvable, "CfnStack.ApplicationSettingsProperty"]
    """``AWS::AppStream::Stack.ApplicationSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-applicationsettings
    Stability:
        experimental
    """

    attributesToDelete: typing.List[str]
    """``AWS::AppStream::Stack.AttributesToDelete``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-attributestodelete
    Stability:
        experimental
    """

    deleteStorageConnectors: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::AppStream::Stack.DeleteStorageConnectors``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-deletestorageconnectors
    Stability:
        experimental
    """

    description: str
    """``AWS::AppStream::Stack.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-description
    Stability:
        experimental
    """

    displayName: str
    """``AWS::AppStream::Stack.DisplayName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-displayname
    Stability:
        experimental
    """

    feedbackUrl: str
    """``AWS::AppStream::Stack.FeedbackURL``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-feedbackurl
    Stability:
        experimental
    """

    name: str
    """``AWS::AppStream::Stack.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-name
    Stability:
        experimental
    """

    redirectUrl: str
    """``AWS::AppStream::Stack.RedirectURL``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-redirecturl
    Stability:
        experimental
    """

    storageConnectors: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnStack.StorageConnectorProperty"]]]
    """``AWS::AppStream::Stack.StorageConnectors``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-storageconnectors
    Stability:
        experimental
    """

    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::AppStream::Stack.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-tags
    Stability:
        experimental
    """

    userSettings: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnStack.UserSettingProperty"]]]
    """``AWS::AppStream::Stack.UserSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stack.html#cfn-appstream-stack-usersettings
    Stability:
        experimental
    """

class CfnStackUserAssociation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appstream.CfnStackUserAssociation"):
    """A CloudFormation ``AWS::AppStream::StackUserAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackuserassociation.html
    Stability:
        experimental
    cloudformationResource:
        AWS::AppStream::StackUserAssociation
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, authentication_type: str, stack_name: str, user_name: str, send_email_notification: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None) -> None:
        """Create a new ``AWS::AppStream::StackUserAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            authenticationType: ``AWS::AppStream::StackUserAssociation.AuthenticationType``.
            stackName: ``AWS::AppStream::StackUserAssociation.StackName``.
            userName: ``AWS::AppStream::StackUserAssociation.UserName``.
            sendEmailNotification: ``AWS::AppStream::StackUserAssociation.SendEmailNotification``.

        Stability:
            experimental
        """
        props: CfnStackUserAssociationProps = {"authenticationType": authentication_type, "stackName": stack_name, "userName": user_name}

        if send_email_notification is not None:
            props["sendEmailNotification"] = send_email_notification

        jsii.create(CfnStackUserAssociation, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="authenticationType")
    def authentication_type(self) -> str:
        """``AWS::AppStream::StackUserAssociation.AuthenticationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackuserassociation.html#cfn-appstream-stackuserassociation-authenticationtype
        Stability:
            experimental
        """
        return jsii.get(self, "authenticationType")

    @authentication_type.setter
    def authentication_type(self, value: str):
        return jsii.set(self, "authenticationType", value)

    @property
    @jsii.member(jsii_name="stackName")
    def stack_name(self) -> str:
        """``AWS::AppStream::StackUserAssociation.StackName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackuserassociation.html#cfn-appstream-stackuserassociation-stackname
        Stability:
            experimental
        """
        return jsii.get(self, "stackName")

    @stack_name.setter
    def stack_name(self, value: str):
        return jsii.set(self, "stackName", value)

    @property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> str:
        """``AWS::AppStream::StackUserAssociation.UserName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackuserassociation.html#cfn-appstream-stackuserassociation-username
        Stability:
            experimental
        """
        return jsii.get(self, "userName")

    @user_name.setter
    def user_name(self, value: str):
        return jsii.set(self, "userName", value)

    @property
    @jsii.member(jsii_name="sendEmailNotification")
    def send_email_notification(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::AppStream::StackUserAssociation.SendEmailNotification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackuserassociation.html#cfn-appstream-stackuserassociation-sendemailnotification
        Stability:
            experimental
        """
        return jsii.get(self, "sendEmailNotification")

    @send_email_notification.setter
    def send_email_notification(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "sendEmailNotification", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnStackUserAssociationProps(jsii.compat.TypedDict, total=False):
    sendEmailNotification: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::AppStream::StackUserAssociation.SendEmailNotification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackuserassociation.html#cfn-appstream-stackuserassociation-sendemailnotification
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnStackUserAssociationProps", jsii_struct_bases=[_CfnStackUserAssociationProps])
class CfnStackUserAssociationProps(_CfnStackUserAssociationProps):
    """Properties for defining a ``AWS::AppStream::StackUserAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackuserassociation.html
    Stability:
        experimental
    """
    authenticationType: str
    """``AWS::AppStream::StackUserAssociation.AuthenticationType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackuserassociation.html#cfn-appstream-stackuserassociation-authenticationtype
    Stability:
        experimental
    """

    stackName: str
    """``AWS::AppStream::StackUserAssociation.StackName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackuserassociation.html#cfn-appstream-stackuserassociation-stackname
    Stability:
        experimental
    """

    userName: str
    """``AWS::AppStream::StackUserAssociation.UserName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-stackuserassociation.html#cfn-appstream-stackuserassociation-username
    Stability:
        experimental
    """

class CfnUser(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appstream.CfnUser"):
    """A CloudFormation ``AWS::AppStream::User``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-user.html
    Stability:
        experimental
    cloudformationResource:
        AWS::AppStream::User
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, authentication_type: str, user_name: str, first_name: typing.Optional[str]=None, last_name: typing.Optional[str]=None, message_action: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::AppStream::User``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            authenticationType: ``AWS::AppStream::User.AuthenticationType``.
            userName: ``AWS::AppStream::User.UserName``.
            firstName: ``AWS::AppStream::User.FirstName``.
            lastName: ``AWS::AppStream::User.LastName``.
            messageAction: ``AWS::AppStream::User.MessageAction``.

        Stability:
            experimental
        """
        props: CfnUserProps = {"authenticationType": authentication_type, "userName": user_name}

        if first_name is not None:
            props["firstName"] = first_name

        if last_name is not None:
            props["lastName"] = last_name

        if message_action is not None:
            props["messageAction"] = message_action

        jsii.create(CfnUser, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="authenticationType")
    def authentication_type(self) -> str:
        """``AWS::AppStream::User.AuthenticationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-user.html#cfn-appstream-user-authenticationtype
        Stability:
            experimental
        """
        return jsii.get(self, "authenticationType")

    @authentication_type.setter
    def authentication_type(self, value: str):
        return jsii.set(self, "authenticationType", value)

    @property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> str:
        """``AWS::AppStream::User.UserName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-user.html#cfn-appstream-user-username
        Stability:
            experimental
        """
        return jsii.get(self, "userName")

    @user_name.setter
    def user_name(self, value: str):
        return jsii.set(self, "userName", value)

    @property
    @jsii.member(jsii_name="firstName")
    def first_name(self) -> typing.Optional[str]:
        """``AWS::AppStream::User.FirstName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-user.html#cfn-appstream-user-firstname
        Stability:
            experimental
        """
        return jsii.get(self, "firstName")

    @first_name.setter
    def first_name(self, value: typing.Optional[str]):
        return jsii.set(self, "firstName", value)

    @property
    @jsii.member(jsii_name="lastName")
    def last_name(self) -> typing.Optional[str]:
        """``AWS::AppStream::User.LastName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-user.html#cfn-appstream-user-lastname
        Stability:
            experimental
        """
        return jsii.get(self, "lastName")

    @last_name.setter
    def last_name(self, value: typing.Optional[str]):
        return jsii.set(self, "lastName", value)

    @property
    @jsii.member(jsii_name="messageAction")
    def message_action(self) -> typing.Optional[str]:
        """``AWS::AppStream::User.MessageAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-user.html#cfn-appstream-user-messageaction
        Stability:
            experimental
        """
        return jsii.get(self, "messageAction")

    @message_action.setter
    def message_action(self, value: typing.Optional[str]):
        return jsii.set(self, "messageAction", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnUserProps(jsii.compat.TypedDict, total=False):
    firstName: str
    """``AWS::AppStream::User.FirstName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-user.html#cfn-appstream-user-firstname
    Stability:
        experimental
    """
    lastName: str
    """``AWS::AppStream::User.LastName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-user.html#cfn-appstream-user-lastname
    Stability:
        experimental
    """
    messageAction: str
    """``AWS::AppStream::User.MessageAction``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-user.html#cfn-appstream-user-messageaction
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-appstream.CfnUserProps", jsii_struct_bases=[_CfnUserProps])
class CfnUserProps(_CfnUserProps):
    """Properties for defining a ``AWS::AppStream::User``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-user.html
    Stability:
        experimental
    """
    authenticationType: str
    """``AWS::AppStream::User.AuthenticationType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-user.html#cfn-appstream-user-authenticationtype
    Stability:
        experimental
    """

    userName: str
    """``AWS::AppStream::User.UserName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appstream-user.html#cfn-appstream-user-username
    Stability:
        experimental
    """

__all__ = ["CfnDirectoryConfig", "CfnDirectoryConfigProps", "CfnFleet", "CfnFleetProps", "CfnImageBuilder", "CfnImageBuilderProps", "CfnStack", "CfnStackFleetAssociation", "CfnStackFleetAssociationProps", "CfnStackProps", "CfnStackUserAssociation", "CfnStackUserAssociationProps", "CfnUser", "CfnUserProps", "__jsii_assembly__"]

publication.publish()
