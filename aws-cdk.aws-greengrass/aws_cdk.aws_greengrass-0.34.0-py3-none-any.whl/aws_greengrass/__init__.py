import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-greengrass", "0.34.0", __name__, "aws-greengrass@0.34.0.jsii.tgz")
class CfnConnectorDefinition(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinition"):
    """A CloudFormation ``AWS::Greengrass::ConnectorDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::ConnectorDefinition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional["ConnectorDefinitionVersionProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::Greengrass::ConnectorDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::ConnectorDefinition.Name``.
            initialVersion: ``AWS::Greengrass::ConnectorDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnConnectorDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnConnectorDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="connectorDefinitionArn")
    def connector_definition_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "connectorDefinitionArn")

    @property
    @jsii.member(jsii_name="connectorDefinitionId")
    def connector_definition_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "connectorDefinitionId")

    @property
    @jsii.member(jsii_name="connectorDefinitionLatestVersionArn")
    def connector_definition_latest_version_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "connectorDefinitionLatestVersionArn")

    @property
    @jsii.member(jsii_name="connectorDefinitionName")
    def connector_definition_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "connectorDefinitionName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnConnectorDefinitionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinition.ConnectorDefinitionVersionProperty", jsii_struct_bases=[])
    class ConnectorDefinitionVersionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connectordefinitionversion.html
        Stability:
            experimental
        """
        connectors: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnConnectorDefinition.ConnectorProperty"]]]
        """``CfnConnectorDefinition.ConnectorDefinitionVersionProperty.Connectors``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connectordefinitionversion.html#cfn-greengrass-connectordefinition-connectordefinitionversion-connectors
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ConnectorProperty(jsii.compat.TypedDict, total=False):
        parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnConnectorDefinition.ConnectorProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html#cfn-greengrass-connectordefinition-connector-parameters
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinition.ConnectorProperty", jsii_struct_bases=[_ConnectorProperty])
    class ConnectorProperty(_ConnectorProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html
        Stability:
            experimental
        """
        connectorArn: str
        """``CfnConnectorDefinition.ConnectorProperty.ConnectorArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html#cfn-greengrass-connectordefinition-connector-connectorarn
        Stability:
            experimental
        """

        id: str
        """``CfnConnectorDefinition.ConnectorProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html#cfn-greengrass-connectordefinition-connector-id
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnConnectorDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union["CfnConnectorDefinition.ConnectorDefinitionVersionProperty", aws_cdk.cdk.Token]
    """``AWS::Greengrass::ConnectorDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-initialversion
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinitionProps", jsii_struct_bases=[_CfnConnectorDefinitionProps])
class CfnConnectorDefinitionProps(_CfnConnectorDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::ConnectorDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html
    Stability:
        experimental
    """
    name: str
    """``AWS::Greengrass::ConnectorDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-name
    Stability:
        experimental
    """

class CfnConnectorDefinitionVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::ConnectorDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::ConnectorDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, connector_definition_id: str, connectors: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "ConnectorProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::ConnectorDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            connectorDefinitionId: ``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.
            connectors: ``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.

        Stability:
            experimental
        """
        props: CfnConnectorDefinitionVersionProps = {"connectorDefinitionId": connector_definition_id, "connectors": connectors}

        jsii.create(CfnConnectorDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="connectorDefinitionVersionArn")
    def connector_definition_version_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "connectorDefinitionVersionArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnConnectorDefinitionVersionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ConnectorProperty(jsii.compat.TypedDict, total=False):
        parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnConnectorDefinitionVersion.ConnectorProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html#cfn-greengrass-connectordefinitionversion-connector-parameters
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinitionVersion.ConnectorProperty", jsii_struct_bases=[_ConnectorProperty])
    class ConnectorProperty(_ConnectorProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html
        Stability:
            experimental
        """
        connectorArn: str
        """``CfnConnectorDefinitionVersion.ConnectorProperty.ConnectorArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html#cfn-greengrass-connectordefinitionversion-connector-connectorarn
        Stability:
            experimental
        """

        id: str
        """``CfnConnectorDefinitionVersion.ConnectorProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html#cfn-greengrass-connectordefinitionversion-connector-id
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinitionVersionProps", jsii_struct_bases=[])
class CfnConnectorDefinitionVersionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Greengrass::ConnectorDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html
    Stability:
        experimental
    """
    connectorDefinitionId: str
    """``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectordefinitionid
    Stability:
        experimental
    """

    connectors: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnConnectorDefinitionVersion.ConnectorProperty"]]]
    """``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectors
    Stability:
        experimental
    """

class CfnCoreDefinition(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinition"):
    """A CloudFormation ``AWS::Greengrass::CoreDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::CoreDefinition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["CoreDefinitionVersionProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::CoreDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::CoreDefinition.Name``.
            initialVersion: ``AWS::Greengrass::CoreDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnCoreDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnCoreDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="coreDefinitionArn")
    def core_definition_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "coreDefinitionArn")

    @property
    @jsii.member(jsii_name="coreDefinitionId")
    def core_definition_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "coreDefinitionId")

    @property
    @jsii.member(jsii_name="coreDefinitionLatestVersionArn")
    def core_definition_latest_version_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "coreDefinitionLatestVersionArn")

    @property
    @jsii.member(jsii_name="coreDefinitionName")
    def core_definition_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "coreDefinitionName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnCoreDefinitionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinition.CoreDefinitionVersionProperty", jsii_struct_bases=[])
    class CoreDefinitionVersionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-coredefinitionversion.html
        Stability:
            experimental
        """
        cores: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnCoreDefinition.CoreProperty"]]]
        """``CfnCoreDefinition.CoreDefinitionVersionProperty.Cores``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-coredefinitionversion.html#cfn-greengrass-coredefinition-coredefinitionversion-cores
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CoreProperty(jsii.compat.TypedDict, total=False):
        syncShadow: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnCoreDefinition.CoreProperty.SyncShadow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-syncshadow
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinition.CoreProperty", jsii_struct_bases=[_CoreProperty])
    class CoreProperty(_CoreProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html
        Stability:
            experimental
        """
        certificateArn: str
        """``CfnCoreDefinition.CoreProperty.CertificateArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-certificatearn
        Stability:
            experimental
        """

        id: str
        """``CfnCoreDefinition.CoreProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-id
        Stability:
            experimental
        """

        thingArn: str
        """``CfnCoreDefinition.CoreProperty.ThingArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-thingarn
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnCoreDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.cdk.Token, "CfnCoreDefinition.CoreDefinitionVersionProperty"]
    """``AWS::Greengrass::CoreDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-initialversion
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinitionProps", jsii_struct_bases=[_CfnCoreDefinitionProps])
class CfnCoreDefinitionProps(_CfnCoreDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::CoreDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html
    Stability:
        experimental
    """
    name: str
    """``AWS::Greengrass::CoreDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-name
    Stability:
        experimental
    """

class CfnCoreDefinitionVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::CoreDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::CoreDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, core_definition_id: str, cores: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CoreProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::CoreDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            coreDefinitionId: ``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.
            cores: ``AWS::Greengrass::CoreDefinitionVersion.Cores``.

        Stability:
            experimental
        """
        props: CfnCoreDefinitionVersionProps = {"coreDefinitionId": core_definition_id, "cores": cores}

        jsii.create(CfnCoreDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="coreDefinitionVersionArn")
    def core_definition_version_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "coreDefinitionVersionArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnCoreDefinitionVersionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CoreProperty(jsii.compat.TypedDict, total=False):
        syncShadow: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnCoreDefinitionVersion.CoreProperty.SyncShadow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-syncshadow
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinitionVersion.CoreProperty", jsii_struct_bases=[_CoreProperty])
    class CoreProperty(_CoreProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html
        Stability:
            experimental
        """
        certificateArn: str
        """``CfnCoreDefinitionVersion.CoreProperty.CertificateArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-certificatearn
        Stability:
            experimental
        """

        id: str
        """``CfnCoreDefinitionVersion.CoreProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-id
        Stability:
            experimental
        """

        thingArn: str
        """``CfnCoreDefinitionVersion.CoreProperty.ThingArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-thingarn
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinitionVersionProps", jsii_struct_bases=[])
class CfnCoreDefinitionVersionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Greengrass::CoreDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html
    Stability:
        experimental
    """
    coreDefinitionId: str
    """``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-coredefinitionid
    Stability:
        experimental
    """

    cores: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnCoreDefinitionVersion.CoreProperty"]]]
    """``AWS::Greengrass::CoreDefinitionVersion.Cores``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-cores
    Stability:
        experimental
    """

class CfnDeviceDefinition(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinition"):
    """A CloudFormation ``AWS::Greengrass::DeviceDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::DeviceDefinition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["DeviceDefinitionVersionProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::DeviceDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::DeviceDefinition.Name``.
            initialVersion: ``AWS::Greengrass::DeviceDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnDeviceDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnDeviceDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="deviceDefinitionArn")
    def device_definition_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "deviceDefinitionArn")

    @property
    @jsii.member(jsii_name="deviceDefinitionId")
    def device_definition_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "deviceDefinitionId")

    @property
    @jsii.member(jsii_name="deviceDefinitionLatestVersionArn")
    def device_definition_latest_version_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "deviceDefinitionLatestVersionArn")

    @property
    @jsii.member(jsii_name="deviceDefinitionName")
    def device_definition_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "deviceDefinitionName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDeviceDefinitionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinition.DeviceDefinitionVersionProperty", jsii_struct_bases=[])
    class DeviceDefinitionVersionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-devicedefinitionversion.html
        Stability:
            experimental
        """
        devices: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeviceDefinition.DeviceProperty"]]]
        """``CfnDeviceDefinition.DeviceDefinitionVersionProperty.Devices``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-devicedefinitionversion.html#cfn-greengrass-devicedefinition-devicedefinitionversion-devices
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DeviceProperty(jsii.compat.TypedDict, total=False):
        syncShadow: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeviceDefinition.DeviceProperty.SyncShadow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-syncshadow
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinition.DeviceProperty", jsii_struct_bases=[_DeviceProperty])
    class DeviceProperty(_DeviceProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html
        Stability:
            experimental
        """
        certificateArn: str
        """``CfnDeviceDefinition.DeviceProperty.CertificateArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-certificatearn
        Stability:
            experimental
        """

        id: str
        """``CfnDeviceDefinition.DeviceProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-id
        Stability:
            experimental
        """

        thingArn: str
        """``CfnDeviceDefinition.DeviceProperty.ThingArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-thingarn
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDeviceDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.cdk.Token, "CfnDeviceDefinition.DeviceDefinitionVersionProperty"]
    """``AWS::Greengrass::DeviceDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-initialversion
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinitionProps", jsii_struct_bases=[_CfnDeviceDefinitionProps])
class CfnDeviceDefinitionProps(_CfnDeviceDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::DeviceDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html
    Stability:
        experimental
    """
    name: str
    """``AWS::Greengrass::DeviceDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-name
    Stability:
        experimental
    """

class CfnDeviceDefinitionVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::DeviceDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::DeviceDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, device_definition_id: str, devices: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "DeviceProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::DeviceDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            deviceDefinitionId: ``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.
            devices: ``AWS::Greengrass::DeviceDefinitionVersion.Devices``.

        Stability:
            experimental
        """
        props: CfnDeviceDefinitionVersionProps = {"deviceDefinitionId": device_definition_id, "devices": devices}

        jsii.create(CfnDeviceDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="deviceDefinitionVersionArn")
    def device_definition_version_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deviceDefinitionVersionArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDeviceDefinitionVersionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DeviceProperty(jsii.compat.TypedDict, total=False):
        syncShadow: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeviceDefinitionVersion.DeviceProperty.SyncShadow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-syncshadow
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinitionVersion.DeviceProperty", jsii_struct_bases=[_DeviceProperty])
    class DeviceProperty(_DeviceProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html
        Stability:
            experimental
        """
        certificateArn: str
        """``CfnDeviceDefinitionVersion.DeviceProperty.CertificateArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-certificatearn
        Stability:
            experimental
        """

        id: str
        """``CfnDeviceDefinitionVersion.DeviceProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-id
        Stability:
            experimental
        """

        thingArn: str
        """``CfnDeviceDefinitionVersion.DeviceProperty.ThingArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-thingarn
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinitionVersionProps", jsii_struct_bases=[])
class CfnDeviceDefinitionVersionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Greengrass::DeviceDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html
    Stability:
        experimental
    """
    deviceDefinitionId: str
    """``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devicedefinitionid
    Stability:
        experimental
    """

    devices: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeviceDefinitionVersion.DeviceProperty"]]]
    """``AWS::Greengrass::DeviceDefinitionVersion.Devices``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devices
    Stability:
        experimental
    """

class CfnFunctionDefinition(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition"):
    """A CloudFormation ``AWS::Greengrass::FunctionDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::FunctionDefinition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["FunctionDefinitionVersionProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::FunctionDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::FunctionDefinition.Name``.
            initialVersion: ``AWS::Greengrass::FunctionDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnFunctionDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnFunctionDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="functionDefinitionArn")
    def function_definition_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "functionDefinitionArn")

    @property
    @jsii.member(jsii_name="functionDefinitionId")
    def function_definition_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "functionDefinitionId")

    @property
    @jsii.member(jsii_name="functionDefinitionLatestVersionArn")
    def function_definition_latest_version_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "functionDefinitionLatestVersionArn")

    @property
    @jsii.member(jsii_name="functionDefinitionName")
    def function_definition_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "functionDefinitionName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnFunctionDefinitionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.DefaultConfigProperty", jsii_struct_bases=[])
    class DefaultConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-defaultconfig.html
        Stability:
            experimental
        """
        execution: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinition.ExecutionProperty"]
        """``CfnFunctionDefinition.DefaultConfigProperty.Execution``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-defaultconfig.html#cfn-greengrass-functiondefinition-defaultconfig-execution
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.EnvironmentProperty", jsii_struct_bases=[])
    class EnvironmentProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html
        Stability:
            experimental
        """
        accessSysfs: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnFunctionDefinition.EnvironmentProperty.AccessSysfs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-accesssysfs
        Stability:
            experimental
        """

        execution: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinition.ExecutionProperty"]
        """``CfnFunctionDefinition.EnvironmentProperty.Execution``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-execution
        Stability:
            experimental
        """

        resourceAccessPolicies: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinition.ResourceAccessPolicyProperty"]]]
        """``CfnFunctionDefinition.EnvironmentProperty.ResourceAccessPolicies``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-resourceaccesspolicies
        Stability:
            experimental
        """

        variables: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnFunctionDefinition.EnvironmentProperty.Variables``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-variables
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.ExecutionProperty", jsii_struct_bases=[])
    class ExecutionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-execution.html
        Stability:
            experimental
        """
        isolationMode: str
        """``CfnFunctionDefinition.ExecutionProperty.IsolationMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-execution.html#cfn-greengrass-functiondefinition-execution-isolationmode
        Stability:
            experimental
        """

        runAs: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinition.RunAsProperty"]
        """``CfnFunctionDefinition.ExecutionProperty.RunAs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-execution.html#cfn-greengrass-functiondefinition-execution-runas
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.FunctionConfigurationProperty", jsii_struct_bases=[])
    class FunctionConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html
        Stability:
            experimental
        """
        encodingType: str
        """``CfnFunctionDefinition.FunctionConfigurationProperty.EncodingType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-encodingtype
        Stability:
            experimental
        """

        environment: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinition.EnvironmentProperty"]
        """``CfnFunctionDefinition.FunctionConfigurationProperty.Environment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-environment
        Stability:
            experimental
        """

        execArgs: str
        """``CfnFunctionDefinition.FunctionConfigurationProperty.ExecArgs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-execargs
        Stability:
            experimental
        """

        executable: str
        """``CfnFunctionDefinition.FunctionConfigurationProperty.Executable``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-executable
        Stability:
            experimental
        """

        memorySize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFunctionDefinition.FunctionConfigurationProperty.MemorySize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-memorysize
        Stability:
            experimental
        """

        pinned: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnFunctionDefinition.FunctionConfigurationProperty.Pinned``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-pinned
        Stability:
            experimental
        """

        timeout: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFunctionDefinition.FunctionConfigurationProperty.Timeout``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-timeout
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FunctionDefinitionVersionProperty(jsii.compat.TypedDict, total=False):
        defaultConfig: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinition.DefaultConfigProperty"]
        """``CfnFunctionDefinition.FunctionDefinitionVersionProperty.DefaultConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functiondefinitionversion.html#cfn-greengrass-functiondefinition-functiondefinitionversion-defaultconfig
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.FunctionDefinitionVersionProperty", jsii_struct_bases=[_FunctionDefinitionVersionProperty])
    class FunctionDefinitionVersionProperty(_FunctionDefinitionVersionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functiondefinitionversion.html
        Stability:
            experimental
        """
        functions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinition.FunctionProperty"]]]
        """``CfnFunctionDefinition.FunctionDefinitionVersionProperty.Functions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functiondefinitionversion.html#cfn-greengrass-functiondefinition-functiondefinitionversion-functions
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.FunctionProperty", jsii_struct_bases=[])
    class FunctionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html
        Stability:
            experimental
        """
        functionArn: str
        """``CfnFunctionDefinition.FunctionProperty.FunctionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html#cfn-greengrass-functiondefinition-function-functionarn
        Stability:
            experimental
        """

        functionConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinition.FunctionConfigurationProperty"]
        """``CfnFunctionDefinition.FunctionProperty.FunctionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html#cfn-greengrass-functiondefinition-function-functionconfiguration
        Stability:
            experimental
        """

        id: str
        """``CfnFunctionDefinition.FunctionProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html#cfn-greengrass-functiondefinition-function-id
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ResourceAccessPolicyProperty(jsii.compat.TypedDict, total=False):
        permission: str
        """``CfnFunctionDefinition.ResourceAccessPolicyProperty.Permission``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-resourceaccesspolicy.html#cfn-greengrass-functiondefinition-resourceaccesspolicy-permission
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.ResourceAccessPolicyProperty", jsii_struct_bases=[_ResourceAccessPolicyProperty])
    class ResourceAccessPolicyProperty(_ResourceAccessPolicyProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-resourceaccesspolicy.html
        Stability:
            experimental
        """
        resourceId: str
        """``CfnFunctionDefinition.ResourceAccessPolicyProperty.ResourceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-resourceaccesspolicy.html#cfn-greengrass-functiondefinition-resourceaccesspolicy-resourceid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.RunAsProperty", jsii_struct_bases=[])
    class RunAsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-runas.html
        Stability:
            experimental
        """
        gid: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFunctionDefinition.RunAsProperty.Gid``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-runas.html#cfn-greengrass-functiondefinition-runas-gid
        Stability:
            experimental
        """

        uid: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFunctionDefinition.RunAsProperty.Uid``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-runas.html#cfn-greengrass-functiondefinition-runas-uid
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnFunctionDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinition.FunctionDefinitionVersionProperty"]
    """``AWS::Greengrass::FunctionDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-initialversion
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionProps", jsii_struct_bases=[_CfnFunctionDefinitionProps])
class CfnFunctionDefinitionProps(_CfnFunctionDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::FunctionDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html
    Stability:
        experimental
    """
    name: str
    """``AWS::Greengrass::FunctionDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-name
    Stability:
        experimental
    """

class CfnFunctionDefinitionVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::FunctionDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::FunctionDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, function_definition_id: str, functions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "FunctionProperty"]]], default_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["DefaultConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::FunctionDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            functionDefinitionId: ``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.
            functions: ``AWS::Greengrass::FunctionDefinitionVersion.Functions``.
            defaultConfig: ``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.

        Stability:
            experimental
        """
        props: CfnFunctionDefinitionVersionProps = {"functionDefinitionId": function_definition_id, "functions": functions}

        if default_config is not None:
            props["defaultConfig"] = default_config

        jsii.create(CfnFunctionDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="functionDefinitionVersionArn")
    def function_definition_version_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "functionDefinitionVersionArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnFunctionDefinitionVersionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.DefaultConfigProperty", jsii_struct_bases=[])
    class DefaultConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-defaultconfig.html
        Stability:
            experimental
        """
        execution: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinitionVersion.ExecutionProperty"]
        """``CfnFunctionDefinitionVersion.DefaultConfigProperty.Execution``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-defaultconfig.html#cfn-greengrass-functiondefinitionversion-defaultconfig-execution
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.EnvironmentProperty", jsii_struct_bases=[])
    class EnvironmentProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html
        Stability:
            experimental
        """
        accessSysfs: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnFunctionDefinitionVersion.EnvironmentProperty.AccessSysfs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-accesssysfs
        Stability:
            experimental
        """

        execution: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinitionVersion.ExecutionProperty"]
        """``CfnFunctionDefinitionVersion.EnvironmentProperty.Execution``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-execution
        Stability:
            experimental
        """

        resourceAccessPolicies: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty"]]]
        """``CfnFunctionDefinitionVersion.EnvironmentProperty.ResourceAccessPolicies``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-resourceaccesspolicies
        Stability:
            experimental
        """

        variables: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnFunctionDefinitionVersion.EnvironmentProperty.Variables``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-variables
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.ExecutionProperty", jsii_struct_bases=[])
    class ExecutionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-execution.html
        Stability:
            experimental
        """
        isolationMode: str
        """``CfnFunctionDefinitionVersion.ExecutionProperty.IsolationMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-execution.html#cfn-greengrass-functiondefinitionversion-execution-isolationmode
        Stability:
            experimental
        """

        runAs: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinitionVersion.RunAsProperty"]
        """``CfnFunctionDefinitionVersion.ExecutionProperty.RunAs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-execution.html#cfn-greengrass-functiondefinitionversion-execution-runas
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.FunctionConfigurationProperty", jsii_struct_bases=[])
    class FunctionConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html
        Stability:
            experimental
        """
        encodingType: str
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.EncodingType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-encodingtype
        Stability:
            experimental
        """

        environment: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinitionVersion.EnvironmentProperty"]
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Environment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-environment
        Stability:
            experimental
        """

        execArgs: str
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.ExecArgs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-execargs
        Stability:
            experimental
        """

        executable: str
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Executable``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-executable
        Stability:
            experimental
        """

        memorySize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.MemorySize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-memorysize
        Stability:
            experimental
        """

        pinned: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Pinned``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-pinned
        Stability:
            experimental
        """

        timeout: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Timeout``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-timeout
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.FunctionProperty", jsii_struct_bases=[])
    class FunctionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html
        Stability:
            experimental
        """
        functionArn: str
        """``CfnFunctionDefinitionVersion.FunctionProperty.FunctionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html#cfn-greengrass-functiondefinitionversion-function-functionarn
        Stability:
            experimental
        """

        functionConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinitionVersion.FunctionConfigurationProperty"]
        """``CfnFunctionDefinitionVersion.FunctionProperty.FunctionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html#cfn-greengrass-functiondefinitionversion-function-functionconfiguration
        Stability:
            experimental
        """

        id: str
        """``CfnFunctionDefinitionVersion.FunctionProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html#cfn-greengrass-functiondefinitionversion-function-id
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ResourceAccessPolicyProperty(jsii.compat.TypedDict, total=False):
        permission: str
        """``CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty.Permission``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-resourceaccesspolicy.html#cfn-greengrass-functiondefinitionversion-resourceaccesspolicy-permission
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty", jsii_struct_bases=[_ResourceAccessPolicyProperty])
    class ResourceAccessPolicyProperty(_ResourceAccessPolicyProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-resourceaccesspolicy.html
        Stability:
            experimental
        """
        resourceId: str
        """``CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty.ResourceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-resourceaccesspolicy.html#cfn-greengrass-functiondefinitionversion-resourceaccesspolicy-resourceid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.RunAsProperty", jsii_struct_bases=[])
    class RunAsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-runas.html
        Stability:
            experimental
        """
        gid: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFunctionDefinitionVersion.RunAsProperty.Gid``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-runas.html#cfn-greengrass-functiondefinitionversion-runas-gid
        Stability:
            experimental
        """

        uid: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFunctionDefinitionVersion.RunAsProperty.Uid``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-runas.html#cfn-greengrass-functiondefinitionversion-runas-uid
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnFunctionDefinitionVersionProps(jsii.compat.TypedDict, total=False):
    defaultConfig: typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinitionVersion.DefaultConfigProperty"]
    """``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-defaultconfig
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersionProps", jsii_struct_bases=[_CfnFunctionDefinitionVersionProps])
class CfnFunctionDefinitionVersionProps(_CfnFunctionDefinitionVersionProps):
    """Properties for defining a ``AWS::Greengrass::FunctionDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html
    Stability:
        experimental
    """
    functionDefinitionId: str
    """``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functiondefinitionid
    Stability:
        experimental
    """

    functions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnFunctionDefinitionVersion.FunctionProperty"]]]
    """``AWS::Greengrass::FunctionDefinitionVersion.Functions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functions
    Stability:
        experimental
    """

class CfnGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnGroup"):
    """A CloudFormation ``AWS::Greengrass::Group``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::Group
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["GroupVersionProperty"]]]=None, role_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Greengrass::Group``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::Group.Name``.
            initialVersion: ``AWS::Greengrass::Group.InitialVersion``.
            roleArn: ``AWS::Greengrass::Group.RoleArn``.

        Stability:
            experimental
        """
        props: CfnGroupProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        if role_arn is not None:
            props["roleArn"] = role_arn

        jsii.create(CfnGroup, self, [scope, id, props])

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
    @jsii.member(jsii_name="groupArn")
    def group_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "groupArn")

    @property
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "groupId")

    @property
    @jsii.member(jsii_name="groupLatestVersionArn")
    def group_latest_version_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "groupLatestVersionArn")

    @property
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "groupName")

    @property
    @jsii.member(jsii_name="groupRoleArn")
    def group_role_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RoleArn
        """
        return jsii.get(self, "groupRoleArn")

    @property
    @jsii.member(jsii_name="groupRoleAttachedAt")
    def group_role_attached_at(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RoleAttachedAt
        """
        return jsii.get(self, "groupRoleAttachedAt")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnGroup.GroupVersionProperty", jsii_struct_bases=[])
    class GroupVersionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html
        Stability:
            experimental
        """
        connectorDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.ConnectorDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-connectordefinitionversionarn
        Stability:
            experimental
        """

        coreDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.CoreDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-coredefinitionversionarn
        Stability:
            experimental
        """

        deviceDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.DeviceDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-devicedefinitionversionarn
        Stability:
            experimental
        """

        functionDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.FunctionDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-functiondefinitionversionarn
        Stability:
            experimental
        """

        loggerDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.LoggerDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-loggerdefinitionversionarn
        Stability:
            experimental
        """

        resourceDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.ResourceDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-resourcedefinitionversionarn
        Stability:
            experimental
        """

        subscriptionDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.SubscriptionDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-subscriptiondefinitionversionarn
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnGroupProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.cdk.Token, "CfnGroup.GroupVersionProperty"]
    """``AWS::Greengrass::Group.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-initialversion
    Stability:
        experimental
    """
    roleArn: str
    """``AWS::Greengrass::Group.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-rolearn
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnGroupProps", jsii_struct_bases=[_CfnGroupProps])
class CfnGroupProps(_CfnGroupProps):
    """Properties for defining a ``AWS::Greengrass::Group``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html
    Stability:
        experimental
    """
    name: str
    """``AWS::Greengrass::Group.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-name
    Stability:
        experimental
    """

class CfnGroupVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnGroupVersion"):
    """A CloudFormation ``AWS::Greengrass::GroupVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::GroupVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, group_id: str, connector_definition_version_arn: typing.Optional[str]=None, core_definition_version_arn: typing.Optional[str]=None, device_definition_version_arn: typing.Optional[str]=None, function_definition_version_arn: typing.Optional[str]=None, logger_definition_version_arn: typing.Optional[str]=None, resource_definition_version_arn: typing.Optional[str]=None, subscription_definition_version_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Greengrass::GroupVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            groupId: ``AWS::Greengrass::GroupVersion.GroupId``.
            connectorDefinitionVersionArn: ``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.
            coreDefinitionVersionArn: ``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.
            deviceDefinitionVersionArn: ``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.
            functionDefinitionVersionArn: ``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.
            loggerDefinitionVersionArn: ``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.
            resourceDefinitionVersionArn: ``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.
            subscriptionDefinitionVersionArn: ``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.

        Stability:
            experimental
        """
        props: CfnGroupVersionProps = {"groupId": group_id}

        if connector_definition_version_arn is not None:
            props["connectorDefinitionVersionArn"] = connector_definition_version_arn

        if core_definition_version_arn is not None:
            props["coreDefinitionVersionArn"] = core_definition_version_arn

        if device_definition_version_arn is not None:
            props["deviceDefinitionVersionArn"] = device_definition_version_arn

        if function_definition_version_arn is not None:
            props["functionDefinitionVersionArn"] = function_definition_version_arn

        if logger_definition_version_arn is not None:
            props["loggerDefinitionVersionArn"] = logger_definition_version_arn

        if resource_definition_version_arn is not None:
            props["resourceDefinitionVersionArn"] = resource_definition_version_arn

        if subscription_definition_version_arn is not None:
            props["subscriptionDefinitionVersionArn"] = subscription_definition_version_arn

        jsii.create(CfnGroupVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="groupVersionArn")
    def group_version_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "groupVersionArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnGroupVersionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnGroupVersionProps(jsii.compat.TypedDict, total=False):
    connectorDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-connectordefinitionversionarn
    Stability:
        experimental
    """
    coreDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-coredefinitionversionarn
    Stability:
        experimental
    """
    deviceDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-devicedefinitionversionarn
    Stability:
        experimental
    """
    functionDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-functiondefinitionversionarn
    Stability:
        experimental
    """
    loggerDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-loggerdefinitionversionarn
    Stability:
        experimental
    """
    resourceDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-resourcedefinitionversionarn
    Stability:
        experimental
    """
    subscriptionDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-subscriptiondefinitionversionarn
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnGroupVersionProps", jsii_struct_bases=[_CfnGroupVersionProps])
class CfnGroupVersionProps(_CfnGroupVersionProps):
    """Properties for defining a ``AWS::Greengrass::GroupVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html
    Stability:
        experimental
    """
    groupId: str
    """``AWS::Greengrass::GroupVersion.GroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-groupid
    Stability:
        experimental
    """

class CfnLoggerDefinition(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinition"):
    """A CloudFormation ``AWS::Greengrass::LoggerDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::LoggerDefinition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["LoggerDefinitionVersionProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::LoggerDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::LoggerDefinition.Name``.
            initialVersion: ``AWS::Greengrass::LoggerDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnLoggerDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnLoggerDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="loggerDefinitionArn")
    def logger_definition_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "loggerDefinitionArn")

    @property
    @jsii.member(jsii_name="loggerDefinitionId")
    def logger_definition_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "loggerDefinitionId")

    @property
    @jsii.member(jsii_name="loggerDefinitionLatestVersionArn")
    def logger_definition_latest_version_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "loggerDefinitionLatestVersionArn")

    @property
    @jsii.member(jsii_name="loggerDefinitionName")
    def logger_definition_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "loggerDefinitionName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnLoggerDefinitionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinition.LoggerDefinitionVersionProperty", jsii_struct_bases=[])
    class LoggerDefinitionVersionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-loggerdefinitionversion.html
        Stability:
            experimental
        """
        loggers: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLoggerDefinition.LoggerProperty"]]]
        """``CfnLoggerDefinition.LoggerDefinitionVersionProperty.Loggers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-loggerdefinitionversion.html#cfn-greengrass-loggerdefinition-loggerdefinitionversion-loggers
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LoggerProperty(jsii.compat.TypedDict, total=False):
        space: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLoggerDefinition.LoggerProperty.Space``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-space
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinition.LoggerProperty", jsii_struct_bases=[_LoggerProperty])
    class LoggerProperty(_LoggerProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html
        Stability:
            experimental
        """
        component: str
        """``CfnLoggerDefinition.LoggerProperty.Component``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-component
        Stability:
            experimental
        """

        id: str
        """``CfnLoggerDefinition.LoggerProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-id
        Stability:
            experimental
        """

        level: str
        """``CfnLoggerDefinition.LoggerProperty.Level``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-level
        Stability:
            experimental
        """

        type: str
        """``CfnLoggerDefinition.LoggerProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-type
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnLoggerDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.cdk.Token, "CfnLoggerDefinition.LoggerDefinitionVersionProperty"]
    """``AWS::Greengrass::LoggerDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-initialversion
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinitionProps", jsii_struct_bases=[_CfnLoggerDefinitionProps])
class CfnLoggerDefinitionProps(_CfnLoggerDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::LoggerDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html
    Stability:
        experimental
    """
    name: str
    """``AWS::Greengrass::LoggerDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-name
    Stability:
        experimental
    """

class CfnLoggerDefinitionVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::LoggerDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::LoggerDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, logger_definition_id: str, loggers: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "LoggerProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::LoggerDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            loggerDefinitionId: ``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.
            loggers: ``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.

        Stability:
            experimental
        """
        props: CfnLoggerDefinitionVersionProps = {"loggerDefinitionId": logger_definition_id, "loggers": loggers}

        jsii.create(CfnLoggerDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="loggerDefinitionVersionArn")
    def logger_definition_version_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "loggerDefinitionVersionArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnLoggerDefinitionVersionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LoggerProperty(jsii.compat.TypedDict, total=False):
        space: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLoggerDefinitionVersion.LoggerProperty.Space``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-space
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinitionVersion.LoggerProperty", jsii_struct_bases=[_LoggerProperty])
    class LoggerProperty(_LoggerProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html
        Stability:
            experimental
        """
        component: str
        """``CfnLoggerDefinitionVersion.LoggerProperty.Component``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-component
        Stability:
            experimental
        """

        id: str
        """``CfnLoggerDefinitionVersion.LoggerProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-id
        Stability:
            experimental
        """

        level: str
        """``CfnLoggerDefinitionVersion.LoggerProperty.Level``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-level
        Stability:
            experimental
        """

        type: str
        """``CfnLoggerDefinitionVersion.LoggerProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-type
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinitionVersionProps", jsii_struct_bases=[])
class CfnLoggerDefinitionVersionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Greengrass::LoggerDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html
    Stability:
        experimental
    """
    loggerDefinitionId: str
    """``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggerdefinitionid
    Stability:
        experimental
    """

    loggers: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLoggerDefinitionVersion.LoggerProperty"]]]
    """``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggers
    Stability:
        experimental
    """

class CfnResourceDefinition(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition"):
    """A CloudFormation ``AWS::Greengrass::ResourceDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::ResourceDefinition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ResourceDefinitionVersionProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::ResourceDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::ResourceDefinition.Name``.
            initialVersion: ``AWS::Greengrass::ResourceDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnResourceDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnResourceDefinition, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnResourceDefinitionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="resourceDefinitionArn")
    def resource_definition_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "resourceDefinitionArn")

    @property
    @jsii.member(jsii_name="resourceDefinitionId")
    def resource_definition_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "resourceDefinitionId")

    @property
    @jsii.member(jsii_name="resourceDefinitionLatestVersionArn")
    def resource_definition_latest_version_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "resourceDefinitionLatestVersionArn")

    @property
    @jsii.member(jsii_name="resourceDefinitionName")
    def resource_definition_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "resourceDefinitionName")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _GroupOwnerSettingProperty(jsii.compat.TypedDict, total=False):
        groupOwner: str
        """``CfnResourceDefinition.GroupOwnerSettingProperty.GroupOwner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-groupownersetting.html#cfn-greengrass-resourcedefinition-groupownersetting-groupowner
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.GroupOwnerSettingProperty", jsii_struct_bases=[_GroupOwnerSettingProperty])
    class GroupOwnerSettingProperty(_GroupOwnerSettingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-groupownersetting.html
        Stability:
            experimental
        """
        autoAddGroupOwner: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnResourceDefinition.GroupOwnerSettingProperty.AutoAddGroupOwner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-groupownersetting.html#cfn-greengrass-resourcedefinition-groupownersetting-autoaddgroupowner
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LocalDeviceResourceDataProperty(jsii.compat.TypedDict, total=False):
        groupOwnerSetting: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinition.GroupOwnerSettingProperty"]
        """``CfnResourceDefinition.LocalDeviceResourceDataProperty.GroupOwnerSetting``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localdeviceresourcedata.html#cfn-greengrass-resourcedefinition-localdeviceresourcedata-groupownersetting
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.LocalDeviceResourceDataProperty", jsii_struct_bases=[_LocalDeviceResourceDataProperty])
    class LocalDeviceResourceDataProperty(_LocalDeviceResourceDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localdeviceresourcedata.html
        Stability:
            experimental
        """
        sourcePath: str
        """``CfnResourceDefinition.LocalDeviceResourceDataProperty.SourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localdeviceresourcedata.html#cfn-greengrass-resourcedefinition-localdeviceresourcedata-sourcepath
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LocalVolumeResourceDataProperty(jsii.compat.TypedDict, total=False):
        groupOwnerSetting: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinition.GroupOwnerSettingProperty"]
        """``CfnResourceDefinition.LocalVolumeResourceDataProperty.GroupOwnerSetting``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html#cfn-greengrass-resourcedefinition-localvolumeresourcedata-groupownersetting
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.LocalVolumeResourceDataProperty", jsii_struct_bases=[_LocalVolumeResourceDataProperty])
    class LocalVolumeResourceDataProperty(_LocalVolumeResourceDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html
        Stability:
            experimental
        """
        destinationPath: str
        """``CfnResourceDefinition.LocalVolumeResourceDataProperty.DestinationPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html#cfn-greengrass-resourcedefinition-localvolumeresourcedata-destinationpath
        Stability:
            experimental
        """

        sourcePath: str
        """``CfnResourceDefinition.LocalVolumeResourceDataProperty.SourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html#cfn-greengrass-resourcedefinition-localvolumeresourcedata-sourcepath
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.ResourceDataContainerProperty", jsii_struct_bases=[])
    class ResourceDataContainerProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html
        Stability:
            experimental
        """
        localDeviceResourceData: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinition.LocalDeviceResourceDataProperty"]
        """``CfnResourceDefinition.ResourceDataContainerProperty.LocalDeviceResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-localdeviceresourcedata
        Stability:
            experimental
        """

        localVolumeResourceData: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinition.LocalVolumeResourceDataProperty"]
        """``CfnResourceDefinition.ResourceDataContainerProperty.LocalVolumeResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-localvolumeresourcedata
        Stability:
            experimental
        """

        s3MachineLearningModelResourceData: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinition.S3MachineLearningModelResourceDataProperty"]
        """``CfnResourceDefinition.ResourceDataContainerProperty.S3MachineLearningModelResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-s3machinelearningmodelresourcedata
        Stability:
            experimental
        """

        sageMakerMachineLearningModelResourceData: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty"]
        """``CfnResourceDefinition.ResourceDataContainerProperty.SageMakerMachineLearningModelResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-sagemakermachinelearningmodelresourcedata
        Stability:
            experimental
        """

        secretsManagerSecretResourceData: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinition.SecretsManagerSecretResourceDataProperty"]
        """``CfnResourceDefinition.ResourceDataContainerProperty.SecretsManagerSecretResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-secretsmanagersecretresourcedata
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.ResourceDefinitionVersionProperty", jsii_struct_bases=[])
    class ResourceDefinitionVersionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedefinitionversion.html
        Stability:
            experimental
        """
        resources: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinition.ResourceInstanceProperty"]]]
        """``CfnResourceDefinition.ResourceDefinitionVersionProperty.Resources``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedefinitionversion.html#cfn-greengrass-resourcedefinition-resourcedefinitionversion-resources
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.ResourceInstanceProperty", jsii_struct_bases=[])
    class ResourceInstanceProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html
        Stability:
            experimental
        """
        id: str
        """``CfnResourceDefinition.ResourceInstanceProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html#cfn-greengrass-resourcedefinition-resourceinstance-id
        Stability:
            experimental
        """

        name: str
        """``CfnResourceDefinition.ResourceInstanceProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html#cfn-greengrass-resourcedefinition-resourceinstance-name
        Stability:
            experimental
        """

        resourceDataContainer: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinition.ResourceDataContainerProperty"]
        """``CfnResourceDefinition.ResourceInstanceProperty.ResourceDataContainer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html#cfn-greengrass-resourcedefinition-resourceinstance-resourcedatacontainer
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.S3MachineLearningModelResourceDataProperty", jsii_struct_bases=[])
    class S3MachineLearningModelResourceDataProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html
        Stability:
            experimental
        """
        destinationPath: str
        """``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.DestinationPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-s3machinelearningmodelresourcedata-destinationpath
        Stability:
            experimental
        """

        s3Uri: str
        """``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.S3Uri``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-s3machinelearningmodelresourcedata-s3uri
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty", jsii_struct_bases=[])
    class SageMakerMachineLearningModelResourceDataProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html
        Stability:
            experimental
        """
        destinationPath: str
        """``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.DestinationPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata-destinationpath
        Stability:
            experimental
        """

        sageMakerJobArn: str
        """``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.SageMakerJobArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata-sagemakerjobarn
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SecretsManagerSecretResourceDataProperty(jsii.compat.TypedDict, total=False):
        additionalStagingLabelsToDownload: typing.List[str]
        """``CfnResourceDefinition.SecretsManagerSecretResourceDataProperty.AdditionalStagingLabelsToDownload``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinition-secretsmanagersecretresourcedata-additionalstaginglabelstodownload
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.SecretsManagerSecretResourceDataProperty", jsii_struct_bases=[_SecretsManagerSecretResourceDataProperty])
    class SecretsManagerSecretResourceDataProperty(_SecretsManagerSecretResourceDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-secretsmanagersecretresourcedata.html
        Stability:
            experimental
        """
        arn: str
        """``CfnResourceDefinition.SecretsManagerSecretResourceDataProperty.ARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinition-secretsmanagersecretresourcedata-arn
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnResourceDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinition.ResourceDefinitionVersionProperty"]
    """``AWS::Greengrass::ResourceDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-initialversion
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionProps", jsii_struct_bases=[_CfnResourceDefinitionProps])
class CfnResourceDefinitionProps(_CfnResourceDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::ResourceDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html
    Stability:
        experimental
    """
    name: str
    """``AWS::Greengrass::ResourceDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-name
    Stability:
        experimental
    """

class CfnResourceDefinitionVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::ResourceDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::ResourceDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, resource_definition_id: str, resources: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "ResourceInstanceProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::ResourceDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            resourceDefinitionId: ``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.
            resources: ``AWS::Greengrass::ResourceDefinitionVersion.Resources``.

        Stability:
            experimental
        """
        props: CfnResourceDefinitionVersionProps = {"resourceDefinitionId": resource_definition_id, "resources": resources}

        jsii.create(CfnResourceDefinitionVersion, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnResourceDefinitionVersionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="resourceDefinitionVersionArn")
    def resource_definition_version_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "resourceDefinitionVersionArn")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _GroupOwnerSettingProperty(jsii.compat.TypedDict, total=False):
        groupOwner: str
        """``CfnResourceDefinitionVersion.GroupOwnerSettingProperty.GroupOwner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-groupownersetting.html#cfn-greengrass-resourcedefinitionversion-groupownersetting-groupowner
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty", jsii_struct_bases=[_GroupOwnerSettingProperty])
    class GroupOwnerSettingProperty(_GroupOwnerSettingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-groupownersetting.html
        Stability:
            experimental
        """
        autoAddGroupOwner: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnResourceDefinitionVersion.GroupOwnerSettingProperty.AutoAddGroupOwner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-groupownersetting.html#cfn-greengrass-resourcedefinitionversion-groupownersetting-autoaddgroupowner
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LocalDeviceResourceDataProperty(jsii.compat.TypedDict, total=False):
        groupOwnerSetting: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinitionVersion.GroupOwnerSettingProperty"]
        """``CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty.GroupOwnerSetting``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localdeviceresourcedata.html#cfn-greengrass-resourcedefinitionversion-localdeviceresourcedata-groupownersetting
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty", jsii_struct_bases=[_LocalDeviceResourceDataProperty])
    class LocalDeviceResourceDataProperty(_LocalDeviceResourceDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localdeviceresourcedata.html
        Stability:
            experimental
        """
        sourcePath: str
        """``CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty.SourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localdeviceresourcedata.html#cfn-greengrass-resourcedefinitionversion-localdeviceresourcedata-sourcepath
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LocalVolumeResourceDataProperty(jsii.compat.TypedDict, total=False):
        groupOwnerSetting: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinitionVersion.GroupOwnerSettingProperty"]
        """``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.GroupOwnerSetting``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html#cfn-greengrass-resourcedefinitionversion-localvolumeresourcedata-groupownersetting
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty", jsii_struct_bases=[_LocalVolumeResourceDataProperty])
    class LocalVolumeResourceDataProperty(_LocalVolumeResourceDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html
        Stability:
            experimental
        """
        destinationPath: str
        """``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.DestinationPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html#cfn-greengrass-resourcedefinitionversion-localvolumeresourcedata-destinationpath
        Stability:
            experimental
        """

        sourcePath: str
        """``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.SourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html#cfn-greengrass-resourcedefinitionversion-localvolumeresourcedata-sourcepath
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.ResourceDataContainerProperty", jsii_struct_bases=[])
    class ResourceDataContainerProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html
        Stability:
            experimental
        """
        localDeviceResourceData: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty"]
        """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.LocalDeviceResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-localdeviceresourcedata
        Stability:
            experimental
        """

        localVolumeResourceData: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty"]
        """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.LocalVolumeResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-localvolumeresourcedata
        Stability:
            experimental
        """

        s3MachineLearningModelResourceData: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty"]
        """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.S3MachineLearningModelResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-s3machinelearningmodelresourcedata
        Stability:
            experimental
        """

        sageMakerMachineLearningModelResourceData: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty"]
        """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.SageMakerMachineLearningModelResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-sagemakermachinelearningmodelresourcedata
        Stability:
            experimental
        """

        secretsManagerSecretResourceData: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty"]
        """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.SecretsManagerSecretResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-secretsmanagersecretresourcedata
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.ResourceInstanceProperty", jsii_struct_bases=[])
    class ResourceInstanceProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html
        Stability:
            experimental
        """
        id: str
        """``CfnResourceDefinitionVersion.ResourceInstanceProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html#cfn-greengrass-resourcedefinitionversion-resourceinstance-id
        Stability:
            experimental
        """

        name: str
        """``CfnResourceDefinitionVersion.ResourceInstanceProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html#cfn-greengrass-resourcedefinitionversion-resourceinstance-name
        Stability:
            experimental
        """

        resourceDataContainer: typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinitionVersion.ResourceDataContainerProperty"]
        """``CfnResourceDefinitionVersion.ResourceInstanceProperty.ResourceDataContainer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html#cfn-greengrass-resourcedefinitionversion-resourceinstance-resourcedatacontainer
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty", jsii_struct_bases=[])
    class S3MachineLearningModelResourceDataProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html
        Stability:
            experimental
        """
        destinationPath: str
        """``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.DestinationPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata-destinationpath
        Stability:
            experimental
        """

        s3Uri: str
        """``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.S3Uri``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata-s3uri
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty", jsii_struct_bases=[])
    class SageMakerMachineLearningModelResourceDataProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html
        Stability:
            experimental
        """
        destinationPath: str
        """``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.DestinationPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata-destinationpath
        Stability:
            experimental
        """

        sageMakerJobArn: str
        """``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.SageMakerJobArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata-sagemakerjobarn
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SecretsManagerSecretResourceDataProperty(jsii.compat.TypedDict, total=False):
        additionalStagingLabelsToDownload: typing.List[str]
        """``CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty.AdditionalStagingLabelsToDownload``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata-additionalstaginglabelstodownload
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty", jsii_struct_bases=[_SecretsManagerSecretResourceDataProperty])
    class SecretsManagerSecretResourceDataProperty(_SecretsManagerSecretResourceDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata.html
        Stability:
            experimental
        """
        arn: str
        """``CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty.ARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata-arn
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersionProps", jsii_struct_bases=[])
class CfnResourceDefinitionVersionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Greengrass::ResourceDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html
    Stability:
        experimental
    """
    resourceDefinitionId: str
    """``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resourcedefinitionid
    Stability:
        experimental
    """

    resources: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnResourceDefinitionVersion.ResourceInstanceProperty"]]]
    """``AWS::Greengrass::ResourceDefinitionVersion.Resources``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resources
    Stability:
        experimental
    """

class CfnSubscriptionDefinition(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinition"):
    """A CloudFormation ``AWS::Greengrass::SubscriptionDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::SubscriptionDefinition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["SubscriptionDefinitionVersionProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::SubscriptionDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::SubscriptionDefinition.Name``.
            initialVersion: ``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnSubscriptionDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnSubscriptionDefinition, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSubscriptionDefinitionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="subscriptionDefinitionArn")
    def subscription_definition_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "subscriptionDefinitionArn")

    @property
    @jsii.member(jsii_name="subscriptionDefinitionId")
    def subscription_definition_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "subscriptionDefinitionId")

    @property
    @jsii.member(jsii_name="subscriptionDefinitionLatestVersionArn")
    def subscription_definition_latest_version_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "subscriptionDefinitionLatestVersionArn")

    @property
    @jsii.member(jsii_name="subscriptionDefinitionName")
    def subscription_definition_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "subscriptionDefinitionName")

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty", jsii_struct_bases=[])
    class SubscriptionDefinitionVersionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscriptiondefinitionversion.html
        Stability:
            experimental
        """
        subscriptions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSubscriptionDefinition.SubscriptionProperty"]]]
        """``CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty.Subscriptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinition-subscriptiondefinitionversion-subscriptions
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinition.SubscriptionProperty", jsii_struct_bases=[])
    class SubscriptionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html
        Stability:
            experimental
        """
        id: str
        """``CfnSubscriptionDefinition.SubscriptionProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-id
        Stability:
            experimental
        """

        source: str
        """``CfnSubscriptionDefinition.SubscriptionProperty.Source``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-source
        Stability:
            experimental
        """

        subject: str
        """``CfnSubscriptionDefinition.SubscriptionProperty.Subject``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-subject
        Stability:
            experimental
        """

        target: str
        """``CfnSubscriptionDefinition.SubscriptionProperty.Target``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-target
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSubscriptionDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.cdk.Token, "CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty"]
    """``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-initialversion
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinitionProps", jsii_struct_bases=[_CfnSubscriptionDefinitionProps])
class CfnSubscriptionDefinitionProps(_CfnSubscriptionDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::SubscriptionDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html
    Stability:
        experimental
    """
    name: str
    """``AWS::Greengrass::SubscriptionDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-name
    Stability:
        experimental
    """

class CfnSubscriptionDefinitionVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::SubscriptionDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Greengrass::SubscriptionDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, subscription_definition_id: str, subscriptions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "SubscriptionProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::SubscriptionDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            subscriptionDefinitionId: ``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.
            subscriptions: ``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.

        Stability:
            experimental
        """
        props: CfnSubscriptionDefinitionVersionProps = {"subscriptionDefinitionId": subscription_definition_id, "subscriptions": subscriptions}

        jsii.create(CfnSubscriptionDefinitionVersion, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSubscriptionDefinitionVersionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="subscriptionDefinitionVersionArn")
    def subscription_definition_version_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "subscriptionDefinitionVersionArn")

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinitionVersion.SubscriptionProperty", jsii_struct_bases=[])
    class SubscriptionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html
        Stability:
            experimental
        """
        id: str
        """``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-id
        Stability:
            experimental
        """

        source: str
        """``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Source``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-source
        Stability:
            experimental
        """

        subject: str
        """``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Subject``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-subject
        Stability:
            experimental
        """

        target: str
        """``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Target``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-target
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinitionVersionProps", jsii_struct_bases=[])
class CfnSubscriptionDefinitionVersionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Greengrass::SubscriptionDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html
    Stability:
        experimental
    """
    subscriptionDefinitionId: str
    """``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptiondefinitionid
    Stability:
        experimental
    """

    subscriptions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSubscriptionDefinitionVersion.SubscriptionProperty"]]]
    """``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptions
    Stability:
        experimental
    """

__all__ = ["CfnConnectorDefinition", "CfnConnectorDefinitionProps", "CfnConnectorDefinitionVersion", "CfnConnectorDefinitionVersionProps", "CfnCoreDefinition", "CfnCoreDefinitionProps", "CfnCoreDefinitionVersion", "CfnCoreDefinitionVersionProps", "CfnDeviceDefinition", "CfnDeviceDefinitionProps", "CfnDeviceDefinitionVersion", "CfnDeviceDefinitionVersionProps", "CfnFunctionDefinition", "CfnFunctionDefinitionProps", "CfnFunctionDefinitionVersion", "CfnFunctionDefinitionVersionProps", "CfnGroup", "CfnGroupProps", "CfnGroupVersion", "CfnGroupVersionProps", "CfnLoggerDefinition", "CfnLoggerDefinitionProps", "CfnLoggerDefinitionVersion", "CfnLoggerDefinitionVersionProps", "CfnResourceDefinition", "CfnResourceDefinitionProps", "CfnResourceDefinitionVersion", "CfnResourceDefinitionVersionProps", "CfnSubscriptionDefinition", "CfnSubscriptionDefinitionProps", "CfnSubscriptionDefinitionVersion", "CfnSubscriptionDefinitionVersionProps", "__jsii_assembly__"]

publication.publish()
