import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-directoryservice", "0.35.0", __name__, "aws-directoryservice@0.35.0.jsii.tgz")
class CfnMicrosoftAD(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-directoryservice.CfnMicrosoftAD"):
    """A CloudFormation ``AWS::DirectoryService::MicrosoftAD``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DirectoryService::MicrosoftAD
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, password: str, vpc_settings: typing.Union["VpcSettingsProperty", aws_cdk.cdk.IResolvable], create_alias: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, edition: typing.Optional[str]=None, enable_sso: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, short_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::DirectoryService::MicrosoftAD``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::DirectoryService::MicrosoftAD.Name``.
            password: ``AWS::DirectoryService::MicrosoftAD.Password``.
            vpcSettings: ``AWS::DirectoryService::MicrosoftAD.VpcSettings``.
            createAlias: ``AWS::DirectoryService::MicrosoftAD.CreateAlias``.
            edition: ``AWS::DirectoryService::MicrosoftAD.Edition``.
            enableSso: ``AWS::DirectoryService::MicrosoftAD.EnableSso``.
            shortName: ``AWS::DirectoryService::MicrosoftAD.ShortName``.

        Stability:
            experimental
        """
        props: CfnMicrosoftADProps = {"name": name, "password": password, "vpcSettings": vpc_settings}

        if create_alias is not None:
            props["createAlias"] = create_alias

        if edition is not None:
            props["edition"] = edition

        if enable_sso is not None:
            props["enableSso"] = enable_sso

        if short_name is not None:
            props["shortName"] = short_name

        jsii.create(CfnMicrosoftAD, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrAlias")
    def attr_alias(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Alias
        """
        return jsii.get(self, "attrAlias")

    @property
    @jsii.member(jsii_name="attrDnsIpAddresses")
    def attr_dns_ip_addresses(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DnsIpAddresses
        """
        return jsii.get(self, "attrDnsIpAddresses")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::DirectoryService::MicrosoftAD.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="password")
    def password(self) -> str:
        """``AWS::DirectoryService::MicrosoftAD.Password``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-password
        Stability:
            experimental
        """
        return jsii.get(self, "password")

    @password.setter
    def password(self, value: str):
        return jsii.set(self, "password", value)

    @property
    @jsii.member(jsii_name="vpcSettings")
    def vpc_settings(self) -> typing.Union["VpcSettingsProperty", aws_cdk.cdk.IResolvable]:
        """``AWS::DirectoryService::MicrosoftAD.VpcSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-vpcsettings
        Stability:
            experimental
        """
        return jsii.get(self, "vpcSettings")

    @vpc_settings.setter
    def vpc_settings(self, value: typing.Union["VpcSettingsProperty", aws_cdk.cdk.IResolvable]):
        return jsii.set(self, "vpcSettings", value)

    @property
    @jsii.member(jsii_name="createAlias")
    def create_alias(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::DirectoryService::MicrosoftAD.CreateAlias``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-createalias
        Stability:
            experimental
        """
        return jsii.get(self, "createAlias")

    @create_alias.setter
    def create_alias(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "createAlias", value)

    @property
    @jsii.member(jsii_name="edition")
    def edition(self) -> typing.Optional[str]:
        """``AWS::DirectoryService::MicrosoftAD.Edition``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-edition
        Stability:
            experimental
        """
        return jsii.get(self, "edition")

    @edition.setter
    def edition(self, value: typing.Optional[str]):
        return jsii.set(self, "edition", value)

    @property
    @jsii.member(jsii_name="enableSso")
    def enable_sso(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::DirectoryService::MicrosoftAD.EnableSso``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-enablesso
        Stability:
            experimental
        """
        return jsii.get(self, "enableSso")

    @enable_sso.setter
    def enable_sso(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "enableSso", value)

    @property
    @jsii.member(jsii_name="shortName")
    def short_name(self) -> typing.Optional[str]:
        """``AWS::DirectoryService::MicrosoftAD.ShortName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-shortname
        Stability:
            experimental
        """
        return jsii.get(self, "shortName")

    @short_name.setter
    def short_name(self, value: typing.Optional[str]):
        return jsii.set(self, "shortName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-directoryservice.CfnMicrosoftAD.VpcSettingsProperty", jsii_struct_bases=[])
    class VpcSettingsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-directoryservice-microsoftad-vpcsettings.html
        Stability:
            experimental
        """
        subnetIds: typing.List[str]
        """``CfnMicrosoftAD.VpcSettingsProperty.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-directoryservice-microsoftad-vpcsettings.html#cfn-directoryservice-microsoftad-vpcsettings-subnetids
        Stability:
            experimental
        """

        vpcId: str
        """``CfnMicrosoftAD.VpcSettingsProperty.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-directoryservice-microsoftad-vpcsettings.html#cfn-directoryservice-microsoftad-vpcsettings-vpcid
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnMicrosoftADProps(jsii.compat.TypedDict, total=False):
    createAlias: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::DirectoryService::MicrosoftAD.CreateAlias``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-createalias
    Stability:
        experimental
    """
    edition: str
    """``AWS::DirectoryService::MicrosoftAD.Edition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-edition
    Stability:
        experimental
    """
    enableSso: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::DirectoryService::MicrosoftAD.EnableSso``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-enablesso
    Stability:
        experimental
    """
    shortName: str
    """``AWS::DirectoryService::MicrosoftAD.ShortName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-shortname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-directoryservice.CfnMicrosoftADProps", jsii_struct_bases=[_CfnMicrosoftADProps])
class CfnMicrosoftADProps(_CfnMicrosoftADProps):
    """Properties for defining a ``AWS::DirectoryService::MicrosoftAD``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html
    Stability:
        experimental
    """
    name: str
    """``AWS::DirectoryService::MicrosoftAD.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-name
    Stability:
        experimental
    """

    password: str
    """``AWS::DirectoryService::MicrosoftAD.Password``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-password
    Stability:
        experimental
    """

    vpcSettings: typing.Union["CfnMicrosoftAD.VpcSettingsProperty", aws_cdk.cdk.IResolvable]
    """``AWS::DirectoryService::MicrosoftAD.VpcSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-vpcsettings
    Stability:
        experimental
    """

class CfnSimpleAD(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-directoryservice.CfnSimpleAD"):
    """A CloudFormation ``AWS::DirectoryService::SimpleAD``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DirectoryService::SimpleAD
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, password: str, size: str, vpc_settings: typing.Union[aws_cdk.cdk.IResolvable, "VpcSettingsProperty"], create_alias: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, description: typing.Optional[str]=None, enable_sso: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, short_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::DirectoryService::SimpleAD``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::DirectoryService::SimpleAD.Name``.
            password: ``AWS::DirectoryService::SimpleAD.Password``.
            size: ``AWS::DirectoryService::SimpleAD.Size``.
            vpcSettings: ``AWS::DirectoryService::SimpleAD.VpcSettings``.
            createAlias: ``AWS::DirectoryService::SimpleAD.CreateAlias``.
            description: ``AWS::DirectoryService::SimpleAD.Description``.
            enableSso: ``AWS::DirectoryService::SimpleAD.EnableSso``.
            shortName: ``AWS::DirectoryService::SimpleAD.ShortName``.

        Stability:
            experimental
        """
        props: CfnSimpleADProps = {"name": name, "password": password, "size": size, "vpcSettings": vpc_settings}

        if create_alias is not None:
            props["createAlias"] = create_alias

        if description is not None:
            props["description"] = description

        if enable_sso is not None:
            props["enableSso"] = enable_sso

        if short_name is not None:
            props["shortName"] = short_name

        jsii.create(CfnSimpleAD, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrAlias")
    def attr_alias(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Alias
        """
        return jsii.get(self, "attrAlias")

    @property
    @jsii.member(jsii_name="attrDnsIpAddresses")
    def attr_dns_ip_addresses(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DnsIpAddresses
        """
        return jsii.get(self, "attrDnsIpAddresses")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::DirectoryService::SimpleAD.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="password")
    def password(self) -> str:
        """``AWS::DirectoryService::SimpleAD.Password``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-password
        Stability:
            experimental
        """
        return jsii.get(self, "password")

    @password.setter
    def password(self, value: str):
        return jsii.set(self, "password", value)

    @property
    @jsii.member(jsii_name="size")
    def size(self) -> str:
        """``AWS::DirectoryService::SimpleAD.Size``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-size
        Stability:
            experimental
        """
        return jsii.get(self, "size")

    @size.setter
    def size(self, value: str):
        return jsii.set(self, "size", value)

    @property
    @jsii.member(jsii_name="vpcSettings")
    def vpc_settings(self) -> typing.Union[aws_cdk.cdk.IResolvable, "VpcSettingsProperty"]:
        """``AWS::DirectoryService::SimpleAD.VpcSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-vpcsettings
        Stability:
            experimental
        """
        return jsii.get(self, "vpcSettings")

    @vpc_settings.setter
    def vpc_settings(self, value: typing.Union[aws_cdk.cdk.IResolvable, "VpcSettingsProperty"]):
        return jsii.set(self, "vpcSettings", value)

    @property
    @jsii.member(jsii_name="createAlias")
    def create_alias(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::DirectoryService::SimpleAD.CreateAlias``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-createalias
        Stability:
            experimental
        """
        return jsii.get(self, "createAlias")

    @create_alias.setter
    def create_alias(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "createAlias", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::DirectoryService::SimpleAD.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="enableSso")
    def enable_sso(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::DirectoryService::SimpleAD.EnableSso``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-enablesso
        Stability:
            experimental
        """
        return jsii.get(self, "enableSso")

    @enable_sso.setter
    def enable_sso(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "enableSso", value)

    @property
    @jsii.member(jsii_name="shortName")
    def short_name(self) -> typing.Optional[str]:
        """``AWS::DirectoryService::SimpleAD.ShortName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-shortname
        Stability:
            experimental
        """
        return jsii.get(self, "shortName")

    @short_name.setter
    def short_name(self, value: typing.Optional[str]):
        return jsii.set(self, "shortName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-directoryservice.CfnSimpleAD.VpcSettingsProperty", jsii_struct_bases=[])
    class VpcSettingsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-directoryservice-simplead-vpcsettings.html
        Stability:
            experimental
        """
        subnetIds: typing.List[str]
        """``CfnSimpleAD.VpcSettingsProperty.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-directoryservice-simplead-vpcsettings.html#cfn-directoryservice-simplead-vpcsettings-subnetids
        Stability:
            experimental
        """

        vpcId: str
        """``CfnSimpleAD.VpcSettingsProperty.VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-directoryservice-simplead-vpcsettings.html#cfn-directoryservice-simplead-vpcsettings-vpcid
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSimpleADProps(jsii.compat.TypedDict, total=False):
    createAlias: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::DirectoryService::SimpleAD.CreateAlias``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-createalias
    Stability:
        experimental
    """
    description: str
    """``AWS::DirectoryService::SimpleAD.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-description
    Stability:
        experimental
    """
    enableSso: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::DirectoryService::SimpleAD.EnableSso``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-enablesso
    Stability:
        experimental
    """
    shortName: str
    """``AWS::DirectoryService::SimpleAD.ShortName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-shortname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-directoryservice.CfnSimpleADProps", jsii_struct_bases=[_CfnSimpleADProps])
class CfnSimpleADProps(_CfnSimpleADProps):
    """Properties for defining a ``AWS::DirectoryService::SimpleAD``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html
    Stability:
        experimental
    """
    name: str
    """``AWS::DirectoryService::SimpleAD.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-name
    Stability:
        experimental
    """

    password: str
    """``AWS::DirectoryService::SimpleAD.Password``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-password
    Stability:
        experimental
    """

    size: str
    """``AWS::DirectoryService::SimpleAD.Size``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-size
    Stability:
        experimental
    """

    vpcSettings: typing.Union[aws_cdk.cdk.IResolvable, "CfnSimpleAD.VpcSettingsProperty"]
    """``AWS::DirectoryService::SimpleAD.VpcSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-vpcsettings
    Stability:
        experimental
    """

__all__ = ["CfnMicrosoftAD", "CfnMicrosoftADProps", "CfnSimpleAD", "CfnSimpleADProps", "__jsii_assembly__"]

publication.publish()
