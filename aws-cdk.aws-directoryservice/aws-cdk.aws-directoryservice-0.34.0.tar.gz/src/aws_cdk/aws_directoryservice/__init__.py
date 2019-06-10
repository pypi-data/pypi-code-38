import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-directoryservice", "0.34.0", __name__, "aws-directoryservice@0.34.0.jsii.tgz")
class CfnMicrosoftAD(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-directoryservice.CfnMicrosoftAD"):
    """A CloudFormation ``AWS::DirectoryService::MicrosoftAD``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DirectoryService::MicrosoftAD
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, password: str, vpc_settings: typing.Union["VpcSettingsProperty", aws_cdk.cdk.Token], create_alias: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, edition: typing.Optional[str]=None, enable_sso: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, short_name: typing.Optional[str]=None) -> None:
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
    @jsii.member(jsii_name="microsoftAdAlias")
    def microsoft_ad_alias(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Alias
        """
        return jsii.get(self, "microsoftAdAlias")

    @property
    @jsii.member(jsii_name="microsoftAdDnsIpAddresses")
    def microsoft_ad_dns_ip_addresses(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DnsIpAddresses
        """
        return jsii.get(self, "microsoftAdDnsIpAddresses")

    @property
    @jsii.member(jsii_name="microsoftAdId")
    def microsoft_ad_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "microsoftAdId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnMicrosoftADProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

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
    createAlias: typing.Union[bool, aws_cdk.cdk.Token]
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
    enableSso: typing.Union[bool, aws_cdk.cdk.Token]
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

    vpcSettings: typing.Union["CfnMicrosoftAD.VpcSettingsProperty", aws_cdk.cdk.Token]
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, password: str, size: str, vpc_settings: typing.Union[aws_cdk.cdk.Token, "VpcSettingsProperty"], create_alias: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, description: typing.Optional[str]=None, enable_sso: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, short_name: typing.Optional[str]=None) -> None:
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
    def property_overrides(self) -> "CfnSimpleADProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="simpleAdAlias")
    def simple_ad_alias(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Alias
        """
        return jsii.get(self, "simpleAdAlias")

    @property
    @jsii.member(jsii_name="simpleAdDnsIpAddresses")
    def simple_ad_dns_ip_addresses(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DnsIpAddresses
        """
        return jsii.get(self, "simpleAdDnsIpAddresses")

    @property
    @jsii.member(jsii_name="simpleAdId")
    def simple_ad_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "simpleAdId")

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
    createAlias: typing.Union[bool, aws_cdk.cdk.Token]
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
    enableSso: typing.Union[bool, aws_cdk.cdk.Token]
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

    vpcSettings: typing.Union[aws_cdk.cdk.Token, "CfnSimpleAD.VpcSettingsProperty"]
    """``AWS::DirectoryService::SimpleAD.VpcSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-simplead.html#cfn-directoryservice-simplead-vpcsettings
    Stability:
        experimental
    """

__all__ = ["CfnMicrosoftAD", "CfnMicrosoftADProps", "CfnSimpleAD", "CfnSimpleADProps", "__jsii_assembly__"]

publication.publish()
