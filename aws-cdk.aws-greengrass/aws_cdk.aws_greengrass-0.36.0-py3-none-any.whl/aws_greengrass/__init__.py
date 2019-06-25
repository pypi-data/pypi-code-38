import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-greengrass", "0.36.0", __name__, "aws-greengrass@0.36.0.jsii.tgz")
class CfnConnectorDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinition"):
    """A CloudFormation ``AWS::Greengrass::ConnectorDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::ConnectorDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional["ConnectorDefinitionVersionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::Greengrass::ConnectorDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::ConnectorDefinition.Name``.
            initial_version: ``AWS::Greengrass::ConnectorDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnConnectorDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnConnectorDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::ConnectorDefinition.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional["ConnectorDefinitionVersionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Greengrass::ConnectorDefinition.InitialVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-initialversion
        Stability:
            stable
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional["ConnectorDefinitionVersionProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinition.ConnectorDefinitionVersionProperty", jsii_struct_bases=[])
    class ConnectorDefinitionVersionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connectordefinitionversion.html
        Stability:
            stable
        """
        connectors: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConnectorDefinition.ConnectorProperty"]]]
        """``CfnConnectorDefinition.ConnectorDefinitionVersionProperty.Connectors``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connectordefinitionversion.html#cfn-greengrass-connectordefinition-connectordefinitionversion-connectors
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ConnectorProperty(jsii.compat.TypedDict, total=False):
        parameters: typing.Any
        """``CfnConnectorDefinition.ConnectorProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html#cfn-greengrass-connectordefinition-connector-parameters
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinition.ConnectorProperty", jsii_struct_bases=[_ConnectorProperty])
    class ConnectorProperty(_ConnectorProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html
        Stability:
            stable
        """
        connectorArn: str
        """``CfnConnectorDefinition.ConnectorProperty.ConnectorArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html#cfn-greengrass-connectordefinition-connector-connectorarn
        Stability:
            stable
        """

        id: str
        """``CfnConnectorDefinition.ConnectorProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html#cfn-greengrass-connectordefinition-connector-id
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnConnectorDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union["CfnConnectorDefinition.ConnectorDefinitionVersionProperty", aws_cdk.core.IResolvable]
    """``AWS::Greengrass::ConnectorDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-initialversion
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinitionProps", jsii_struct_bases=[_CfnConnectorDefinitionProps])
class CfnConnectorDefinitionProps(_CfnConnectorDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::ConnectorDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html
    Stability:
        stable
    """
    name: str
    """``AWS::Greengrass::ConnectorDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-name
    Stability:
        stable
    """

class CfnConnectorDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::ConnectorDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::ConnectorDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, connector_definition_id: str, connectors: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ConnectorProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::ConnectorDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            connector_definition_id: ``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.
            connectors: ``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.

        Stability:
            experimental
        """
        props: CfnConnectorDefinitionVersionProps = {"connectorDefinitionId": connector_definition_id, "connectors": connectors}

        jsii.create(CfnConnectorDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="connectorDefinitionId")
    def connector_definition_id(self) -> str:
        """``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectordefinitionid
        Stability:
            stable
        """
        return jsii.get(self, "connectorDefinitionId")

    @connector_definition_id.setter
    def connector_definition_id(self, value: str):
        return jsii.set(self, "connectorDefinitionId", value)

    @property
    @jsii.member(jsii_name="connectors")
    def connectors(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ConnectorProperty"]]]:
        """``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectors
        Stability:
            stable
        """
        return jsii.get(self, "connectors")

    @connectors.setter
    def connectors(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ConnectorProperty"]]]):
        return jsii.set(self, "connectors", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ConnectorProperty(jsii.compat.TypedDict, total=False):
        parameters: typing.Any
        """``CfnConnectorDefinitionVersion.ConnectorProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html#cfn-greengrass-connectordefinitionversion-connector-parameters
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinitionVersion.ConnectorProperty", jsii_struct_bases=[_ConnectorProperty])
    class ConnectorProperty(_ConnectorProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html
        Stability:
            stable
        """
        connectorArn: str
        """``CfnConnectorDefinitionVersion.ConnectorProperty.ConnectorArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html#cfn-greengrass-connectordefinitionversion-connector-connectorarn
        Stability:
            stable
        """

        id: str
        """``CfnConnectorDefinitionVersion.ConnectorProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html#cfn-greengrass-connectordefinitionversion-connector-id
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnConnectorDefinitionVersionProps", jsii_struct_bases=[])
class CfnConnectorDefinitionVersionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Greengrass::ConnectorDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html
    Stability:
        stable
    """
    connectorDefinitionId: str
    """``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectordefinitionid
    Stability:
        stable
    """

    connectors: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConnectorDefinitionVersion.ConnectorProperty"]]]
    """``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectors
    Stability:
        stable
    """

class CfnCoreDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinition"):
    """A CloudFormation ``AWS::Greengrass::CoreDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::CoreDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CoreDefinitionVersionProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::CoreDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::CoreDefinition.Name``.
            initial_version: ``AWS::Greengrass::CoreDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnCoreDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnCoreDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::CoreDefinition.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CoreDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::CoreDefinition.InitialVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-initialversion
        Stability:
            stable
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CoreDefinitionVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinition.CoreDefinitionVersionProperty", jsii_struct_bases=[])
    class CoreDefinitionVersionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-coredefinitionversion.html
        Stability:
            stable
        """
        cores: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCoreDefinition.CoreProperty"]]]
        """``CfnCoreDefinition.CoreDefinitionVersionProperty.Cores``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-coredefinitionversion.html#cfn-greengrass-coredefinition-coredefinitionversion-cores
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CoreProperty(jsii.compat.TypedDict, total=False):
        syncShadow: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnCoreDefinition.CoreProperty.SyncShadow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-syncshadow
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinition.CoreProperty", jsii_struct_bases=[_CoreProperty])
    class CoreProperty(_CoreProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html
        Stability:
            stable
        """
        certificateArn: str
        """``CfnCoreDefinition.CoreProperty.CertificateArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-certificatearn
        Stability:
            stable
        """

        id: str
        """``CfnCoreDefinition.CoreProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-id
        Stability:
            stable
        """

        thingArn: str
        """``CfnCoreDefinition.CoreProperty.ThingArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-thingarn
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnCoreDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.core.IResolvable, "CfnCoreDefinition.CoreDefinitionVersionProperty"]
    """``AWS::Greengrass::CoreDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-initialversion
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinitionProps", jsii_struct_bases=[_CfnCoreDefinitionProps])
class CfnCoreDefinitionProps(_CfnCoreDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::CoreDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html
    Stability:
        stable
    """
    name: str
    """``AWS::Greengrass::CoreDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-name
    Stability:
        stable
    """

class CfnCoreDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::CoreDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::CoreDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, core_definition_id: str, cores: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CoreProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::CoreDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            core_definition_id: ``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.
            cores: ``AWS::Greengrass::CoreDefinitionVersion.Cores``.

        Stability:
            experimental
        """
        props: CfnCoreDefinitionVersionProps = {"coreDefinitionId": core_definition_id, "cores": cores}

        jsii.create(CfnCoreDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="coreDefinitionId")
    def core_definition_id(self) -> str:
        """``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-coredefinitionid
        Stability:
            stable
        """
        return jsii.get(self, "coreDefinitionId")

    @core_definition_id.setter
    def core_definition_id(self, value: str):
        return jsii.set(self, "coreDefinitionId", value)

    @property
    @jsii.member(jsii_name="cores")
    def cores(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CoreProperty"]]]:
        """``AWS::Greengrass::CoreDefinitionVersion.Cores``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-cores
        Stability:
            stable
        """
        return jsii.get(self, "cores")

    @cores.setter
    def cores(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CoreProperty"]]]):
        return jsii.set(self, "cores", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CoreProperty(jsii.compat.TypedDict, total=False):
        syncShadow: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnCoreDefinitionVersion.CoreProperty.SyncShadow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-syncshadow
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinitionVersion.CoreProperty", jsii_struct_bases=[_CoreProperty])
    class CoreProperty(_CoreProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html
        Stability:
            stable
        """
        certificateArn: str
        """``CfnCoreDefinitionVersion.CoreProperty.CertificateArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-certificatearn
        Stability:
            stable
        """

        id: str
        """``CfnCoreDefinitionVersion.CoreProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-id
        Stability:
            stable
        """

        thingArn: str
        """``CfnCoreDefinitionVersion.CoreProperty.ThingArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-thingarn
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnCoreDefinitionVersionProps", jsii_struct_bases=[])
class CfnCoreDefinitionVersionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Greengrass::CoreDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html
    Stability:
        stable
    """
    coreDefinitionId: str
    """``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-coredefinitionid
    Stability:
        stable
    """

    cores: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCoreDefinitionVersion.CoreProperty"]]]
    """``AWS::Greengrass::CoreDefinitionVersion.Cores``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-cores
    Stability:
        stable
    """

class CfnDeviceDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinition"):
    """A CloudFormation ``AWS::Greengrass::DeviceDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::DeviceDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DeviceDefinitionVersionProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::DeviceDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::DeviceDefinition.Name``.
            initial_version: ``AWS::Greengrass::DeviceDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnDeviceDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnDeviceDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::DeviceDefinition.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DeviceDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::DeviceDefinition.InitialVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-initialversion
        Stability:
            stable
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DeviceDefinitionVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinition.DeviceDefinitionVersionProperty", jsii_struct_bases=[])
    class DeviceDefinitionVersionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-devicedefinitionversion.html
        Stability:
            stable
        """
        devices: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDeviceDefinition.DeviceProperty"]]]
        """``CfnDeviceDefinition.DeviceDefinitionVersionProperty.Devices``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-devicedefinitionversion.html#cfn-greengrass-devicedefinition-devicedefinitionversion-devices
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DeviceProperty(jsii.compat.TypedDict, total=False):
        syncShadow: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDeviceDefinition.DeviceProperty.SyncShadow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-syncshadow
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinition.DeviceProperty", jsii_struct_bases=[_DeviceProperty])
    class DeviceProperty(_DeviceProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html
        Stability:
            stable
        """
        certificateArn: str
        """``CfnDeviceDefinition.DeviceProperty.CertificateArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-certificatearn
        Stability:
            stable
        """

        id: str
        """``CfnDeviceDefinition.DeviceProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-id
        Stability:
            stable
        """

        thingArn: str
        """``CfnDeviceDefinition.DeviceProperty.ThingArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-thingarn
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDeviceDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.core.IResolvable, "CfnDeviceDefinition.DeviceDefinitionVersionProperty"]
    """``AWS::Greengrass::DeviceDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-initialversion
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinitionProps", jsii_struct_bases=[_CfnDeviceDefinitionProps])
class CfnDeviceDefinitionProps(_CfnDeviceDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::DeviceDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html
    Stability:
        stable
    """
    name: str
    """``AWS::Greengrass::DeviceDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-name
    Stability:
        stable
    """

class CfnDeviceDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::DeviceDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::DeviceDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, device_definition_id: str, devices: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "DeviceProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::DeviceDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            device_definition_id: ``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.
            devices: ``AWS::Greengrass::DeviceDefinitionVersion.Devices``.

        Stability:
            experimental
        """
        props: CfnDeviceDefinitionVersionProps = {"deviceDefinitionId": device_definition_id, "devices": devices}

        jsii.create(CfnDeviceDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="deviceDefinitionId")
    def device_definition_id(self) -> str:
        """``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devicedefinitionid
        Stability:
            stable
        """
        return jsii.get(self, "deviceDefinitionId")

    @device_definition_id.setter
    def device_definition_id(self, value: str):
        return jsii.set(self, "deviceDefinitionId", value)

    @property
    @jsii.member(jsii_name="devices")
    def devices(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "DeviceProperty"]]]:
        """``AWS::Greengrass::DeviceDefinitionVersion.Devices``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devices
        Stability:
            stable
        """
        return jsii.get(self, "devices")

    @devices.setter
    def devices(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "DeviceProperty"]]]):
        return jsii.set(self, "devices", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DeviceProperty(jsii.compat.TypedDict, total=False):
        syncShadow: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDeviceDefinitionVersion.DeviceProperty.SyncShadow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-syncshadow
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinitionVersion.DeviceProperty", jsii_struct_bases=[_DeviceProperty])
    class DeviceProperty(_DeviceProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html
        Stability:
            stable
        """
        certificateArn: str
        """``CfnDeviceDefinitionVersion.DeviceProperty.CertificateArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-certificatearn
        Stability:
            stable
        """

        id: str
        """``CfnDeviceDefinitionVersion.DeviceProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-id
        Stability:
            stable
        """

        thingArn: str
        """``CfnDeviceDefinitionVersion.DeviceProperty.ThingArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-thingarn
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnDeviceDefinitionVersionProps", jsii_struct_bases=[])
class CfnDeviceDefinitionVersionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Greengrass::DeviceDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html
    Stability:
        stable
    """
    deviceDefinitionId: str
    """``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devicedefinitionid
    Stability:
        stable
    """

    devices: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDeviceDefinitionVersion.DeviceProperty"]]]
    """``AWS::Greengrass::DeviceDefinitionVersion.Devices``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devices
    Stability:
        stable
    """

class CfnFunctionDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition"):
    """A CloudFormation ``AWS::Greengrass::FunctionDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::FunctionDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["FunctionDefinitionVersionProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::FunctionDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::FunctionDefinition.Name``.
            initial_version: ``AWS::Greengrass::FunctionDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnFunctionDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnFunctionDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::FunctionDefinition.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["FunctionDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::FunctionDefinition.InitialVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-initialversion
        Stability:
            stable
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["FunctionDefinitionVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.DefaultConfigProperty", jsii_struct_bases=[])
    class DefaultConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-defaultconfig.html
        Stability:
            stable
        """
        execution: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.ExecutionProperty"]
        """``CfnFunctionDefinition.DefaultConfigProperty.Execution``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-defaultconfig.html#cfn-greengrass-functiondefinition-defaultconfig-execution
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.EnvironmentProperty", jsii_struct_bases=[])
    class EnvironmentProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html
        Stability:
            stable
        """
        accessSysfs: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnFunctionDefinition.EnvironmentProperty.AccessSysfs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-accesssysfs
        Stability:
            stable
        """

        execution: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.ExecutionProperty"]
        """``CfnFunctionDefinition.EnvironmentProperty.Execution``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-execution
        Stability:
            stable
        """

        resourceAccessPolicies: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.ResourceAccessPolicyProperty"]]]
        """``CfnFunctionDefinition.EnvironmentProperty.ResourceAccessPolicies``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-resourceaccesspolicies
        Stability:
            stable
        """

        variables: typing.Any
        """``CfnFunctionDefinition.EnvironmentProperty.Variables``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-variables
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.ExecutionProperty", jsii_struct_bases=[])
    class ExecutionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-execution.html
        Stability:
            stable
        """
        isolationMode: str
        """``CfnFunctionDefinition.ExecutionProperty.IsolationMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-execution.html#cfn-greengrass-functiondefinition-execution-isolationmode
        Stability:
            stable
        """

        runAs: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.RunAsProperty"]
        """``CfnFunctionDefinition.ExecutionProperty.RunAs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-execution.html#cfn-greengrass-functiondefinition-execution-runas
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.FunctionConfigurationProperty", jsii_struct_bases=[])
    class FunctionConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html
        Stability:
            stable
        """
        encodingType: str
        """``CfnFunctionDefinition.FunctionConfigurationProperty.EncodingType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-encodingtype
        Stability:
            stable
        """

        environment: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.EnvironmentProperty"]
        """``CfnFunctionDefinition.FunctionConfigurationProperty.Environment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-environment
        Stability:
            stable
        """

        execArgs: str
        """``CfnFunctionDefinition.FunctionConfigurationProperty.ExecArgs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-execargs
        Stability:
            stable
        """

        executable: str
        """``CfnFunctionDefinition.FunctionConfigurationProperty.Executable``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-executable
        Stability:
            stable
        """

        memorySize: jsii.Number
        """``CfnFunctionDefinition.FunctionConfigurationProperty.MemorySize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-memorysize
        Stability:
            stable
        """

        pinned: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnFunctionDefinition.FunctionConfigurationProperty.Pinned``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-pinned
        Stability:
            stable
        """

        timeout: jsii.Number
        """``CfnFunctionDefinition.FunctionConfigurationProperty.Timeout``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-timeout
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FunctionDefinitionVersionProperty(jsii.compat.TypedDict, total=False):
        defaultConfig: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.DefaultConfigProperty"]
        """``CfnFunctionDefinition.FunctionDefinitionVersionProperty.DefaultConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functiondefinitionversion.html#cfn-greengrass-functiondefinition-functiondefinitionversion-defaultconfig
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.FunctionDefinitionVersionProperty", jsii_struct_bases=[_FunctionDefinitionVersionProperty])
    class FunctionDefinitionVersionProperty(_FunctionDefinitionVersionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functiondefinitionversion.html
        Stability:
            stable
        """
        functions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.FunctionProperty"]]]
        """``CfnFunctionDefinition.FunctionDefinitionVersionProperty.Functions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functiondefinitionversion.html#cfn-greengrass-functiondefinition-functiondefinitionversion-functions
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.FunctionProperty", jsii_struct_bases=[])
    class FunctionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html
        Stability:
            stable
        """
        functionArn: str
        """``CfnFunctionDefinition.FunctionProperty.FunctionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html#cfn-greengrass-functiondefinition-function-functionarn
        Stability:
            stable
        """

        functionConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.FunctionConfigurationProperty"]
        """``CfnFunctionDefinition.FunctionProperty.FunctionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html#cfn-greengrass-functiondefinition-function-functionconfiguration
        Stability:
            stable
        """

        id: str
        """``CfnFunctionDefinition.FunctionProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html#cfn-greengrass-functiondefinition-function-id
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ResourceAccessPolicyProperty(jsii.compat.TypedDict, total=False):
        permission: str
        """``CfnFunctionDefinition.ResourceAccessPolicyProperty.Permission``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-resourceaccesspolicy.html#cfn-greengrass-functiondefinition-resourceaccesspolicy-permission
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.ResourceAccessPolicyProperty", jsii_struct_bases=[_ResourceAccessPolicyProperty])
    class ResourceAccessPolicyProperty(_ResourceAccessPolicyProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-resourceaccesspolicy.html
        Stability:
            stable
        """
        resourceId: str
        """``CfnFunctionDefinition.ResourceAccessPolicyProperty.ResourceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-resourceaccesspolicy.html#cfn-greengrass-functiondefinition-resourceaccesspolicy-resourceid
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinition.RunAsProperty", jsii_struct_bases=[])
    class RunAsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-runas.html
        Stability:
            stable
        """
        gid: jsii.Number
        """``CfnFunctionDefinition.RunAsProperty.Gid``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-runas.html#cfn-greengrass-functiondefinition-runas-gid
        Stability:
            stable
        """

        uid: jsii.Number
        """``CfnFunctionDefinition.RunAsProperty.Uid``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-runas.html#cfn-greengrass-functiondefinition-runas-uid
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnFunctionDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinition.FunctionDefinitionVersionProperty"]
    """``AWS::Greengrass::FunctionDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-initialversion
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionProps", jsii_struct_bases=[_CfnFunctionDefinitionProps])
class CfnFunctionDefinitionProps(_CfnFunctionDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::FunctionDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html
    Stability:
        stable
    """
    name: str
    """``AWS::Greengrass::FunctionDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-name
    Stability:
        stable
    """

class CfnFunctionDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::FunctionDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::FunctionDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, function_definition_id: str, functions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "FunctionProperty"]]], default_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DefaultConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::FunctionDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            function_definition_id: ``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.
            functions: ``AWS::Greengrass::FunctionDefinitionVersion.Functions``.
            default_config: ``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.

        Stability:
            experimental
        """
        props: CfnFunctionDefinitionVersionProps = {"functionDefinitionId": function_definition_id, "functions": functions}

        if default_config is not None:
            props["defaultConfig"] = default_config

        jsii.create(CfnFunctionDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="functionDefinitionId")
    def function_definition_id(self) -> str:
        """``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functiondefinitionid
        Stability:
            stable
        """
        return jsii.get(self, "functionDefinitionId")

    @function_definition_id.setter
    def function_definition_id(self, value: str):
        return jsii.set(self, "functionDefinitionId", value)

    @property
    @jsii.member(jsii_name="functions")
    def functions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "FunctionProperty"]]]:
        """``AWS::Greengrass::FunctionDefinitionVersion.Functions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functions
        Stability:
            stable
        """
        return jsii.get(self, "functions")

    @functions.setter
    def functions(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "FunctionProperty"]]]):
        return jsii.set(self, "functions", value)

    @property
    @jsii.member(jsii_name="defaultConfig")
    def default_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DefaultConfigProperty"]]]:
        """``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-defaultconfig
        Stability:
            stable
        """
        return jsii.get(self, "defaultConfig")

    @default_config.setter
    def default_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["DefaultConfigProperty"]]]):
        return jsii.set(self, "defaultConfig", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.DefaultConfigProperty", jsii_struct_bases=[])
    class DefaultConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-defaultconfig.html
        Stability:
            stable
        """
        execution: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.ExecutionProperty"]
        """``CfnFunctionDefinitionVersion.DefaultConfigProperty.Execution``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-defaultconfig.html#cfn-greengrass-functiondefinitionversion-defaultconfig-execution
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.EnvironmentProperty", jsii_struct_bases=[])
    class EnvironmentProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html
        Stability:
            stable
        """
        accessSysfs: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnFunctionDefinitionVersion.EnvironmentProperty.AccessSysfs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-accesssysfs
        Stability:
            stable
        """

        execution: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.ExecutionProperty"]
        """``CfnFunctionDefinitionVersion.EnvironmentProperty.Execution``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-execution
        Stability:
            stable
        """

        resourceAccessPolicies: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty"]]]
        """``CfnFunctionDefinitionVersion.EnvironmentProperty.ResourceAccessPolicies``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-resourceaccesspolicies
        Stability:
            stable
        """

        variables: typing.Any
        """``CfnFunctionDefinitionVersion.EnvironmentProperty.Variables``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-variables
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.ExecutionProperty", jsii_struct_bases=[])
    class ExecutionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-execution.html
        Stability:
            stable
        """
        isolationMode: str
        """``CfnFunctionDefinitionVersion.ExecutionProperty.IsolationMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-execution.html#cfn-greengrass-functiondefinitionversion-execution-isolationmode
        Stability:
            stable
        """

        runAs: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.RunAsProperty"]
        """``CfnFunctionDefinitionVersion.ExecutionProperty.RunAs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-execution.html#cfn-greengrass-functiondefinitionversion-execution-runas
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.FunctionConfigurationProperty", jsii_struct_bases=[])
    class FunctionConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html
        Stability:
            stable
        """
        encodingType: str
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.EncodingType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-encodingtype
        Stability:
            stable
        """

        environment: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.EnvironmentProperty"]
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Environment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-environment
        Stability:
            stable
        """

        execArgs: str
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.ExecArgs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-execargs
        Stability:
            stable
        """

        executable: str
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Executable``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-executable
        Stability:
            stable
        """

        memorySize: jsii.Number
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.MemorySize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-memorysize
        Stability:
            stable
        """

        pinned: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Pinned``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-pinned
        Stability:
            stable
        """

        timeout: jsii.Number
        """``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Timeout``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-timeout
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.FunctionProperty", jsii_struct_bases=[])
    class FunctionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html
        Stability:
            stable
        """
        functionArn: str
        """``CfnFunctionDefinitionVersion.FunctionProperty.FunctionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html#cfn-greengrass-functiondefinitionversion-function-functionarn
        Stability:
            stable
        """

        functionConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.FunctionConfigurationProperty"]
        """``CfnFunctionDefinitionVersion.FunctionProperty.FunctionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html#cfn-greengrass-functiondefinitionversion-function-functionconfiguration
        Stability:
            stable
        """

        id: str
        """``CfnFunctionDefinitionVersion.FunctionProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html#cfn-greengrass-functiondefinitionversion-function-id
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ResourceAccessPolicyProperty(jsii.compat.TypedDict, total=False):
        permission: str
        """``CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty.Permission``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-resourceaccesspolicy.html#cfn-greengrass-functiondefinitionversion-resourceaccesspolicy-permission
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty", jsii_struct_bases=[_ResourceAccessPolicyProperty])
    class ResourceAccessPolicyProperty(_ResourceAccessPolicyProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-resourceaccesspolicy.html
        Stability:
            stable
        """
        resourceId: str
        """``CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty.ResourceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-resourceaccesspolicy.html#cfn-greengrass-functiondefinitionversion-resourceaccesspolicy-resourceid
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersion.RunAsProperty", jsii_struct_bases=[])
    class RunAsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-runas.html
        Stability:
            stable
        """
        gid: jsii.Number
        """``CfnFunctionDefinitionVersion.RunAsProperty.Gid``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-runas.html#cfn-greengrass-functiondefinitionversion-runas-gid
        Stability:
            stable
        """

        uid: jsii.Number
        """``CfnFunctionDefinitionVersion.RunAsProperty.Uid``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-runas.html#cfn-greengrass-functiondefinitionversion-runas-uid
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnFunctionDefinitionVersionProps(jsii.compat.TypedDict, total=False):
    defaultConfig: typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.DefaultConfigProperty"]
    """``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-defaultconfig
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnFunctionDefinitionVersionProps", jsii_struct_bases=[_CfnFunctionDefinitionVersionProps])
class CfnFunctionDefinitionVersionProps(_CfnFunctionDefinitionVersionProps):
    """Properties for defining a ``AWS::Greengrass::FunctionDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html
    Stability:
        stable
    """
    functionDefinitionId: str
    """``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functiondefinitionid
    Stability:
        stable
    """

    functions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFunctionDefinitionVersion.FunctionProperty"]]]
    """``AWS::Greengrass::FunctionDefinitionVersion.Functions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functions
    Stability:
        stable
    """

class CfnGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnGroup"):
    """A CloudFormation ``AWS::Greengrass::Group``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::Group
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["GroupVersionProperty"]]]=None, role_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Greengrass::Group``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::Group.Name``.
            initial_version: ``AWS::Greengrass::Group.InitialVersion``.
            role_arn: ``AWS::Greengrass::Group.RoleArn``.

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="attrRoleArn")
    def attr_role_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            RoleArn
        """
        return jsii.get(self, "attrRoleArn")

    @property
    @jsii.member(jsii_name="attrRoleAttachedAt")
    def attr_role_attached_at(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            RoleAttachedAt
        """
        return jsii.get(self, "attrRoleAttachedAt")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::Group.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["GroupVersionProperty"]]]:
        """``AWS::Greengrass::Group.InitialVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-initialversion
        Stability:
            stable
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["GroupVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::Group.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-rolearn
        Stability:
            stable
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "roleArn", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnGroup.GroupVersionProperty", jsii_struct_bases=[])
    class GroupVersionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html
        Stability:
            stable
        """
        connectorDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.ConnectorDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-connectordefinitionversionarn
        Stability:
            stable
        """

        coreDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.CoreDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-coredefinitionversionarn
        Stability:
            stable
        """

        deviceDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.DeviceDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-devicedefinitionversionarn
        Stability:
            stable
        """

        functionDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.FunctionDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-functiondefinitionversionarn
        Stability:
            stable
        """

        loggerDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.LoggerDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-loggerdefinitionversionarn
        Stability:
            stable
        """

        resourceDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.ResourceDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-resourcedefinitionversionarn
        Stability:
            stable
        """

        subscriptionDefinitionVersionArn: str
        """``CfnGroup.GroupVersionProperty.SubscriptionDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-subscriptiondefinitionversionarn
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnGroupProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.core.IResolvable, "CfnGroup.GroupVersionProperty"]
    """``AWS::Greengrass::Group.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-initialversion
    Stability:
        stable
    """
    roleArn: str
    """``AWS::Greengrass::Group.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-rolearn
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnGroupProps", jsii_struct_bases=[_CfnGroupProps])
class CfnGroupProps(_CfnGroupProps):
    """Properties for defining a ``AWS::Greengrass::Group``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html
    Stability:
        stable
    """
    name: str
    """``AWS::Greengrass::Group.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-name
    Stability:
        stable
    """

class CfnGroupVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnGroupVersion"):
    """A CloudFormation ``AWS::Greengrass::GroupVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::GroupVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, group_id: str, connector_definition_version_arn: typing.Optional[str]=None, core_definition_version_arn: typing.Optional[str]=None, device_definition_version_arn: typing.Optional[str]=None, function_definition_version_arn: typing.Optional[str]=None, logger_definition_version_arn: typing.Optional[str]=None, resource_definition_version_arn: typing.Optional[str]=None, subscription_definition_version_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Greengrass::GroupVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            group_id: ``AWS::Greengrass::GroupVersion.GroupId``.
            connector_definition_version_arn: ``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.
            core_definition_version_arn: ``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.
            device_definition_version_arn: ``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.
            function_definition_version_arn: ``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.
            logger_definition_version_arn: ``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.
            resource_definition_version_arn: ``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.
            subscription_definition_version_arn: ``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.

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
        """``AWS::Greengrass::GroupVersion.GroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-groupid
        Stability:
            stable
        """
        return jsii.get(self, "groupId")

    @group_id.setter
    def group_id(self, value: str):
        return jsii.set(self, "groupId", value)

    @property
    @jsii.member(jsii_name="connectorDefinitionVersionArn")
    def connector_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-connectordefinitionversionarn
        Stability:
            stable
        """
        return jsii.get(self, "connectorDefinitionVersionArn")

    @connector_definition_version_arn.setter
    def connector_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "connectorDefinitionVersionArn", value)

    @property
    @jsii.member(jsii_name="coreDefinitionVersionArn")
    def core_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-coredefinitionversionarn
        Stability:
            stable
        """
        return jsii.get(self, "coreDefinitionVersionArn")

    @core_definition_version_arn.setter
    def core_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "coreDefinitionVersionArn", value)

    @property
    @jsii.member(jsii_name="deviceDefinitionVersionArn")
    def device_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-devicedefinitionversionarn
        Stability:
            stable
        """
        return jsii.get(self, "deviceDefinitionVersionArn")

    @device_definition_version_arn.setter
    def device_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "deviceDefinitionVersionArn", value)

    @property
    @jsii.member(jsii_name="functionDefinitionVersionArn")
    def function_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-functiondefinitionversionarn
        Stability:
            stable
        """
        return jsii.get(self, "functionDefinitionVersionArn")

    @function_definition_version_arn.setter
    def function_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "functionDefinitionVersionArn", value)

    @property
    @jsii.member(jsii_name="loggerDefinitionVersionArn")
    def logger_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-loggerdefinitionversionarn
        Stability:
            stable
        """
        return jsii.get(self, "loggerDefinitionVersionArn")

    @logger_definition_version_arn.setter
    def logger_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "loggerDefinitionVersionArn", value)

    @property
    @jsii.member(jsii_name="resourceDefinitionVersionArn")
    def resource_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-resourcedefinitionversionarn
        Stability:
            stable
        """
        return jsii.get(self, "resourceDefinitionVersionArn")

    @resource_definition_version_arn.setter
    def resource_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "resourceDefinitionVersionArn", value)

    @property
    @jsii.member(jsii_name="subscriptionDefinitionVersionArn")
    def subscription_definition_version_arn(self) -> typing.Optional[str]:
        """``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-subscriptiondefinitionversionarn
        Stability:
            stable
        """
        return jsii.get(self, "subscriptionDefinitionVersionArn")

    @subscription_definition_version_arn.setter
    def subscription_definition_version_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "subscriptionDefinitionVersionArn", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnGroupVersionProps(jsii.compat.TypedDict, total=False):
    connectorDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-connectordefinitionversionarn
    Stability:
        stable
    """
    coreDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-coredefinitionversionarn
    Stability:
        stable
    """
    deviceDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-devicedefinitionversionarn
    Stability:
        stable
    """
    functionDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-functiondefinitionversionarn
    Stability:
        stable
    """
    loggerDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-loggerdefinitionversionarn
    Stability:
        stable
    """
    resourceDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-resourcedefinitionversionarn
    Stability:
        stable
    """
    subscriptionDefinitionVersionArn: str
    """``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-subscriptiondefinitionversionarn
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnGroupVersionProps", jsii_struct_bases=[_CfnGroupVersionProps])
class CfnGroupVersionProps(_CfnGroupVersionProps):
    """Properties for defining a ``AWS::Greengrass::GroupVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html
    Stability:
        stable
    """
    groupId: str
    """``AWS::Greengrass::GroupVersion.GroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-groupid
    Stability:
        stable
    """

class CfnLoggerDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinition"):
    """A CloudFormation ``AWS::Greengrass::LoggerDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::LoggerDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LoggerDefinitionVersionProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::LoggerDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::LoggerDefinition.Name``.
            initial_version: ``AWS::Greengrass::LoggerDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnLoggerDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnLoggerDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::LoggerDefinition.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LoggerDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::LoggerDefinition.InitialVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-initialversion
        Stability:
            stable
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LoggerDefinitionVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinition.LoggerDefinitionVersionProperty", jsii_struct_bases=[])
    class LoggerDefinitionVersionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-loggerdefinitionversion.html
        Stability:
            stable
        """
        loggers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLoggerDefinition.LoggerProperty"]]]
        """``CfnLoggerDefinition.LoggerDefinitionVersionProperty.Loggers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-loggerdefinitionversion.html#cfn-greengrass-loggerdefinition-loggerdefinitionversion-loggers
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LoggerProperty(jsii.compat.TypedDict, total=False):
        space: jsii.Number
        """``CfnLoggerDefinition.LoggerProperty.Space``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-space
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinition.LoggerProperty", jsii_struct_bases=[_LoggerProperty])
    class LoggerProperty(_LoggerProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html
        Stability:
            stable
        """
        component: str
        """``CfnLoggerDefinition.LoggerProperty.Component``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-component
        Stability:
            stable
        """

        id: str
        """``CfnLoggerDefinition.LoggerProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-id
        Stability:
            stable
        """

        level: str
        """``CfnLoggerDefinition.LoggerProperty.Level``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-level
        Stability:
            stable
        """

        type: str
        """``CfnLoggerDefinition.LoggerProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-type
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnLoggerDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.core.IResolvable, "CfnLoggerDefinition.LoggerDefinitionVersionProperty"]
    """``AWS::Greengrass::LoggerDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-initialversion
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinitionProps", jsii_struct_bases=[_CfnLoggerDefinitionProps])
class CfnLoggerDefinitionProps(_CfnLoggerDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::LoggerDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html
    Stability:
        stable
    """
    name: str
    """``AWS::Greengrass::LoggerDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-name
    Stability:
        stable
    """

class CfnLoggerDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::LoggerDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::LoggerDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, logger_definition_id: str, loggers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "LoggerProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::LoggerDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            logger_definition_id: ``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.
            loggers: ``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.

        Stability:
            experimental
        """
        props: CfnLoggerDefinitionVersionProps = {"loggerDefinitionId": logger_definition_id, "loggers": loggers}

        jsii.create(CfnLoggerDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="loggerDefinitionId")
    def logger_definition_id(self) -> str:
        """``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggerdefinitionid
        Stability:
            stable
        """
        return jsii.get(self, "loggerDefinitionId")

    @logger_definition_id.setter
    def logger_definition_id(self, value: str):
        return jsii.set(self, "loggerDefinitionId", value)

    @property
    @jsii.member(jsii_name="loggers")
    def loggers(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "LoggerProperty"]]]:
        """``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggers
        Stability:
            stable
        """
        return jsii.get(self, "loggers")

    @loggers.setter
    def loggers(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "LoggerProperty"]]]):
        return jsii.set(self, "loggers", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LoggerProperty(jsii.compat.TypedDict, total=False):
        space: jsii.Number
        """``CfnLoggerDefinitionVersion.LoggerProperty.Space``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-space
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinitionVersion.LoggerProperty", jsii_struct_bases=[_LoggerProperty])
    class LoggerProperty(_LoggerProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html
        Stability:
            stable
        """
        component: str
        """``CfnLoggerDefinitionVersion.LoggerProperty.Component``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-component
        Stability:
            stable
        """

        id: str
        """``CfnLoggerDefinitionVersion.LoggerProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-id
        Stability:
            stable
        """

        level: str
        """``CfnLoggerDefinitionVersion.LoggerProperty.Level``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-level
        Stability:
            stable
        """

        type: str
        """``CfnLoggerDefinitionVersion.LoggerProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-type
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnLoggerDefinitionVersionProps", jsii_struct_bases=[])
class CfnLoggerDefinitionVersionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Greengrass::LoggerDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html
    Stability:
        stable
    """
    loggerDefinitionId: str
    """``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggerdefinitionid
    Stability:
        stable
    """

    loggers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLoggerDefinitionVersion.LoggerProperty"]]]
    """``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggers
    Stability:
        stable
    """

class CfnResourceDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition"):
    """A CloudFormation ``AWS::Greengrass::ResourceDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::ResourceDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ResourceDefinitionVersionProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::ResourceDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::ResourceDefinition.Name``.
            initial_version: ``AWS::Greengrass::ResourceDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnResourceDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnResourceDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::ResourceDefinition.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ResourceDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::ResourceDefinition.InitialVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-initialversion
        Stability:
            stable
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ResourceDefinitionVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _GroupOwnerSettingProperty(jsii.compat.TypedDict, total=False):
        groupOwner: str
        """``CfnResourceDefinition.GroupOwnerSettingProperty.GroupOwner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-groupownersetting.html#cfn-greengrass-resourcedefinition-groupownersetting-groupowner
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.GroupOwnerSettingProperty", jsii_struct_bases=[_GroupOwnerSettingProperty])
    class GroupOwnerSettingProperty(_GroupOwnerSettingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-groupownersetting.html
        Stability:
            stable
        """
        autoAddGroupOwner: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnResourceDefinition.GroupOwnerSettingProperty.AutoAddGroupOwner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-groupownersetting.html#cfn-greengrass-resourcedefinition-groupownersetting-autoaddgroupowner
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LocalDeviceResourceDataProperty(jsii.compat.TypedDict, total=False):
        groupOwnerSetting: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.GroupOwnerSettingProperty"]
        """``CfnResourceDefinition.LocalDeviceResourceDataProperty.GroupOwnerSetting``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localdeviceresourcedata.html#cfn-greengrass-resourcedefinition-localdeviceresourcedata-groupownersetting
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.LocalDeviceResourceDataProperty", jsii_struct_bases=[_LocalDeviceResourceDataProperty])
    class LocalDeviceResourceDataProperty(_LocalDeviceResourceDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localdeviceresourcedata.html
        Stability:
            stable
        """
        sourcePath: str
        """``CfnResourceDefinition.LocalDeviceResourceDataProperty.SourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localdeviceresourcedata.html#cfn-greengrass-resourcedefinition-localdeviceresourcedata-sourcepath
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LocalVolumeResourceDataProperty(jsii.compat.TypedDict, total=False):
        groupOwnerSetting: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.GroupOwnerSettingProperty"]
        """``CfnResourceDefinition.LocalVolumeResourceDataProperty.GroupOwnerSetting``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html#cfn-greengrass-resourcedefinition-localvolumeresourcedata-groupownersetting
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.LocalVolumeResourceDataProperty", jsii_struct_bases=[_LocalVolumeResourceDataProperty])
    class LocalVolumeResourceDataProperty(_LocalVolumeResourceDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html
        Stability:
            stable
        """
        destinationPath: str
        """``CfnResourceDefinition.LocalVolumeResourceDataProperty.DestinationPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html#cfn-greengrass-resourcedefinition-localvolumeresourcedata-destinationpath
        Stability:
            stable
        """

        sourcePath: str
        """``CfnResourceDefinition.LocalVolumeResourceDataProperty.SourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html#cfn-greengrass-resourcedefinition-localvolumeresourcedata-sourcepath
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.ResourceDataContainerProperty", jsii_struct_bases=[])
    class ResourceDataContainerProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html
        Stability:
            stable
        """
        localDeviceResourceData: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.LocalDeviceResourceDataProperty"]
        """``CfnResourceDefinition.ResourceDataContainerProperty.LocalDeviceResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-localdeviceresourcedata
        Stability:
            stable
        """

        localVolumeResourceData: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.LocalVolumeResourceDataProperty"]
        """``CfnResourceDefinition.ResourceDataContainerProperty.LocalVolumeResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-localvolumeresourcedata
        Stability:
            stable
        """

        s3MachineLearningModelResourceData: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.S3MachineLearningModelResourceDataProperty"]
        """``CfnResourceDefinition.ResourceDataContainerProperty.S3MachineLearningModelResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-s3machinelearningmodelresourcedata
        Stability:
            stable
        """

        sageMakerMachineLearningModelResourceData: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty"]
        """``CfnResourceDefinition.ResourceDataContainerProperty.SageMakerMachineLearningModelResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-sagemakermachinelearningmodelresourcedata
        Stability:
            stable
        """

        secretsManagerSecretResourceData: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.SecretsManagerSecretResourceDataProperty"]
        """``CfnResourceDefinition.ResourceDataContainerProperty.SecretsManagerSecretResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-secretsmanagersecretresourcedata
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.ResourceDefinitionVersionProperty", jsii_struct_bases=[])
    class ResourceDefinitionVersionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedefinitionversion.html
        Stability:
            stable
        """
        resources: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.ResourceInstanceProperty"]]]
        """``CfnResourceDefinition.ResourceDefinitionVersionProperty.Resources``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedefinitionversion.html#cfn-greengrass-resourcedefinition-resourcedefinitionversion-resources
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.ResourceInstanceProperty", jsii_struct_bases=[])
    class ResourceInstanceProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html
        Stability:
            stable
        """
        id: str
        """``CfnResourceDefinition.ResourceInstanceProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html#cfn-greengrass-resourcedefinition-resourceinstance-id
        Stability:
            stable
        """

        name: str
        """``CfnResourceDefinition.ResourceInstanceProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html#cfn-greengrass-resourcedefinition-resourceinstance-name
        Stability:
            stable
        """

        resourceDataContainer: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.ResourceDataContainerProperty"]
        """``CfnResourceDefinition.ResourceInstanceProperty.ResourceDataContainer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html#cfn-greengrass-resourcedefinition-resourceinstance-resourcedatacontainer
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.S3MachineLearningModelResourceDataProperty", jsii_struct_bases=[])
    class S3MachineLearningModelResourceDataProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html
        Stability:
            stable
        """
        destinationPath: str
        """``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.DestinationPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-s3machinelearningmodelresourcedata-destinationpath
        Stability:
            stable
        """

        s3Uri: str
        """``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.S3Uri``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-s3machinelearningmodelresourcedata-s3uri
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty", jsii_struct_bases=[])
    class SageMakerMachineLearningModelResourceDataProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html
        Stability:
            stable
        """
        destinationPath: str
        """``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.DestinationPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata-destinationpath
        Stability:
            stable
        """

        sageMakerJobArn: str
        """``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.SageMakerJobArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata-sagemakerjobarn
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SecretsManagerSecretResourceDataProperty(jsii.compat.TypedDict, total=False):
        additionalStagingLabelsToDownload: typing.List[str]
        """``CfnResourceDefinition.SecretsManagerSecretResourceDataProperty.AdditionalStagingLabelsToDownload``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinition-secretsmanagersecretresourcedata-additionalstaginglabelstodownload
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinition.SecretsManagerSecretResourceDataProperty", jsii_struct_bases=[_SecretsManagerSecretResourceDataProperty])
    class SecretsManagerSecretResourceDataProperty(_SecretsManagerSecretResourceDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-secretsmanagersecretresourcedata.html
        Stability:
            stable
        """
        arn: str
        """``CfnResourceDefinition.SecretsManagerSecretResourceDataProperty.ARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinition-secretsmanagersecretresourcedata-arn
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnResourceDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinition.ResourceDefinitionVersionProperty"]
    """``AWS::Greengrass::ResourceDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-initialversion
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionProps", jsii_struct_bases=[_CfnResourceDefinitionProps])
class CfnResourceDefinitionProps(_CfnResourceDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::ResourceDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html
    Stability:
        stable
    """
    name: str
    """``AWS::Greengrass::ResourceDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-name
    Stability:
        stable
    """

class CfnResourceDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::ResourceDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::ResourceDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, resource_definition_id: str, resources: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ResourceInstanceProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::ResourceDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            resource_definition_id: ``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.
            resources: ``AWS::Greengrass::ResourceDefinitionVersion.Resources``.

        Stability:
            experimental
        """
        props: CfnResourceDefinitionVersionProps = {"resourceDefinitionId": resource_definition_id, "resources": resources}

        jsii.create(CfnResourceDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="resourceDefinitionId")
    def resource_definition_id(self) -> str:
        """``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resourcedefinitionid
        Stability:
            stable
        """
        return jsii.get(self, "resourceDefinitionId")

    @resource_definition_id.setter
    def resource_definition_id(self, value: str):
        return jsii.set(self, "resourceDefinitionId", value)

    @property
    @jsii.member(jsii_name="resources")
    def resources(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ResourceInstanceProperty"]]]:
        """``AWS::Greengrass::ResourceDefinitionVersion.Resources``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resources
        Stability:
            stable
        """
        return jsii.get(self, "resources")

    @resources.setter
    def resources(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ResourceInstanceProperty"]]]):
        return jsii.set(self, "resources", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _GroupOwnerSettingProperty(jsii.compat.TypedDict, total=False):
        groupOwner: str
        """``CfnResourceDefinitionVersion.GroupOwnerSettingProperty.GroupOwner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-groupownersetting.html#cfn-greengrass-resourcedefinitionversion-groupownersetting-groupowner
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty", jsii_struct_bases=[_GroupOwnerSettingProperty])
    class GroupOwnerSettingProperty(_GroupOwnerSettingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-groupownersetting.html
        Stability:
            stable
        """
        autoAddGroupOwner: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnResourceDefinitionVersion.GroupOwnerSettingProperty.AutoAddGroupOwner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-groupownersetting.html#cfn-greengrass-resourcedefinitionversion-groupownersetting-autoaddgroupowner
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LocalDeviceResourceDataProperty(jsii.compat.TypedDict, total=False):
        groupOwnerSetting: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.GroupOwnerSettingProperty"]
        """``CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty.GroupOwnerSetting``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localdeviceresourcedata.html#cfn-greengrass-resourcedefinitionversion-localdeviceresourcedata-groupownersetting
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty", jsii_struct_bases=[_LocalDeviceResourceDataProperty])
    class LocalDeviceResourceDataProperty(_LocalDeviceResourceDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localdeviceresourcedata.html
        Stability:
            stable
        """
        sourcePath: str
        """``CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty.SourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localdeviceresourcedata.html#cfn-greengrass-resourcedefinitionversion-localdeviceresourcedata-sourcepath
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LocalVolumeResourceDataProperty(jsii.compat.TypedDict, total=False):
        groupOwnerSetting: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.GroupOwnerSettingProperty"]
        """``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.GroupOwnerSetting``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html#cfn-greengrass-resourcedefinitionversion-localvolumeresourcedata-groupownersetting
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty", jsii_struct_bases=[_LocalVolumeResourceDataProperty])
    class LocalVolumeResourceDataProperty(_LocalVolumeResourceDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html
        Stability:
            stable
        """
        destinationPath: str
        """``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.DestinationPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html#cfn-greengrass-resourcedefinitionversion-localvolumeresourcedata-destinationpath
        Stability:
            stable
        """

        sourcePath: str
        """``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.SourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html#cfn-greengrass-resourcedefinitionversion-localvolumeresourcedata-sourcepath
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.ResourceDataContainerProperty", jsii_struct_bases=[])
    class ResourceDataContainerProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html
        Stability:
            stable
        """
        localDeviceResourceData: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty"]
        """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.LocalDeviceResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-localdeviceresourcedata
        Stability:
            stable
        """

        localVolumeResourceData: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty"]
        """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.LocalVolumeResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-localvolumeresourcedata
        Stability:
            stable
        """

        s3MachineLearningModelResourceData: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty"]
        """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.S3MachineLearningModelResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-s3machinelearningmodelresourcedata
        Stability:
            stable
        """

        sageMakerMachineLearningModelResourceData: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty"]
        """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.SageMakerMachineLearningModelResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-sagemakermachinelearningmodelresourcedata
        Stability:
            stable
        """

        secretsManagerSecretResourceData: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty"]
        """``CfnResourceDefinitionVersion.ResourceDataContainerProperty.SecretsManagerSecretResourceData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-secretsmanagersecretresourcedata
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.ResourceInstanceProperty", jsii_struct_bases=[])
    class ResourceInstanceProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html
        Stability:
            stable
        """
        id: str
        """``CfnResourceDefinitionVersion.ResourceInstanceProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html#cfn-greengrass-resourcedefinitionversion-resourceinstance-id
        Stability:
            stable
        """

        name: str
        """``CfnResourceDefinitionVersion.ResourceInstanceProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html#cfn-greengrass-resourcedefinitionversion-resourceinstance-name
        Stability:
            stable
        """

        resourceDataContainer: typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.ResourceDataContainerProperty"]
        """``CfnResourceDefinitionVersion.ResourceInstanceProperty.ResourceDataContainer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html#cfn-greengrass-resourcedefinitionversion-resourceinstance-resourcedatacontainer
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty", jsii_struct_bases=[])
    class S3MachineLearningModelResourceDataProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html
        Stability:
            stable
        """
        destinationPath: str
        """``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.DestinationPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata-destinationpath
        Stability:
            stable
        """

        s3Uri: str
        """``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.S3Uri``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata-s3uri
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty", jsii_struct_bases=[])
    class SageMakerMachineLearningModelResourceDataProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html
        Stability:
            stable
        """
        destinationPath: str
        """``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.DestinationPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata-destinationpath
        Stability:
            stable
        """

        sageMakerJobArn: str
        """``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.SageMakerJobArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata-sagemakerjobarn
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SecretsManagerSecretResourceDataProperty(jsii.compat.TypedDict, total=False):
        additionalStagingLabelsToDownload: typing.List[str]
        """``CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty.AdditionalStagingLabelsToDownload``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata-additionalstaginglabelstodownload
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty", jsii_struct_bases=[_SecretsManagerSecretResourceDataProperty])
    class SecretsManagerSecretResourceDataProperty(_SecretsManagerSecretResourceDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata.html
        Stability:
            stable
        """
        arn: str
        """``CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty.ARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata-arn
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnResourceDefinitionVersionProps", jsii_struct_bases=[])
class CfnResourceDefinitionVersionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Greengrass::ResourceDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html
    Stability:
        stable
    """
    resourceDefinitionId: str
    """``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resourcedefinitionid
    Stability:
        stable
    """

    resources: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnResourceDefinitionVersion.ResourceInstanceProperty"]]]
    """``AWS::Greengrass::ResourceDefinitionVersion.Resources``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resources
    Stability:
        stable
    """

class CfnSubscriptionDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinition"):
    """A CloudFormation ``AWS::Greengrass::SubscriptionDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::SubscriptionDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, initial_version: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SubscriptionDefinitionVersionProperty"]]]=None) -> None:
        """Create a new ``AWS::Greengrass::SubscriptionDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::Greengrass::SubscriptionDefinition.Name``.
            initial_version: ``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.

        Stability:
            experimental
        """
        props: CfnSubscriptionDefinitionProps = {"name": name}

        if initial_version is not None:
            props["initialVersion"] = initial_version

        jsii.create(CfnSubscriptionDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Id
        """
        return jsii.get(self, "attrId")

    @property
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            LatestVersionArn
        """
        return jsii.get(self, "attrLatestVersionArn")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Greengrass::SubscriptionDefinition.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="initialVersion")
    def initial_version(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SubscriptionDefinitionVersionProperty"]]]:
        """``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-initialversion
        Stability:
            stable
        """
        return jsii.get(self, "initialVersion")

    @initial_version.setter
    def initial_version(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SubscriptionDefinitionVersionProperty"]]]):
        return jsii.set(self, "initialVersion", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty", jsii_struct_bases=[])
    class SubscriptionDefinitionVersionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscriptiondefinitionversion.html
        Stability:
            stable
        """
        subscriptions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSubscriptionDefinition.SubscriptionProperty"]]]
        """``CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty.Subscriptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinition-subscriptiondefinitionversion-subscriptions
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinition.SubscriptionProperty", jsii_struct_bases=[])
    class SubscriptionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html
        Stability:
            stable
        """
        id: str
        """``CfnSubscriptionDefinition.SubscriptionProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-id
        Stability:
            stable
        """

        source: str
        """``CfnSubscriptionDefinition.SubscriptionProperty.Source``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-source
        Stability:
            stable
        """

        subject: str
        """``CfnSubscriptionDefinition.SubscriptionProperty.Subject``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-subject
        Stability:
            stable
        """

        target: str
        """``CfnSubscriptionDefinition.SubscriptionProperty.Target``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-target
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSubscriptionDefinitionProps(jsii.compat.TypedDict, total=False):
    initialVersion: typing.Union[aws_cdk.core.IResolvable, "CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty"]
    """``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-initialversion
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinitionProps", jsii_struct_bases=[_CfnSubscriptionDefinitionProps])
class CfnSubscriptionDefinitionProps(_CfnSubscriptionDefinitionProps):
    """Properties for defining a ``AWS::Greengrass::SubscriptionDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html
    Stability:
        stable
    """
    name: str
    """``AWS::Greengrass::SubscriptionDefinition.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-name
    Stability:
        stable
    """

class CfnSubscriptionDefinitionVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinitionVersion"):
    """A CloudFormation ``AWS::Greengrass::SubscriptionDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html
    Stability:
        stable
    cloudformationResource:
        AWS::Greengrass::SubscriptionDefinitionVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, subscription_definition_id: str, subscriptions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "SubscriptionProperty"]]]) -> None:
        """Create a new ``AWS::Greengrass::SubscriptionDefinitionVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            subscription_definition_id: ``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.
            subscriptions: ``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.

        Stability:
            experimental
        """
        props: CfnSubscriptionDefinitionVersionProps = {"subscriptionDefinitionId": subscription_definition_id, "subscriptions": subscriptions}

        jsii.create(CfnSubscriptionDefinitionVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="subscriptionDefinitionId")
    def subscription_definition_id(self) -> str:
        """``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptiondefinitionid
        Stability:
            stable
        """
        return jsii.get(self, "subscriptionDefinitionId")

    @subscription_definition_id.setter
    def subscription_definition_id(self, value: str):
        return jsii.set(self, "subscriptionDefinitionId", value)

    @property
    @jsii.member(jsii_name="subscriptions")
    def subscriptions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "SubscriptionProperty"]]]:
        """``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptions
        Stability:
            stable
        """
        return jsii.get(self, "subscriptions")

    @subscriptions.setter
    def subscriptions(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "SubscriptionProperty"]]]):
        return jsii.set(self, "subscriptions", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinitionVersion.SubscriptionProperty", jsii_struct_bases=[])
    class SubscriptionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html
        Stability:
            stable
        """
        id: str
        """``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-id
        Stability:
            stable
        """

        source: str
        """``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Source``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-source
        Stability:
            stable
        """

        subject: str
        """``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Subject``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-subject
        Stability:
            stable
        """

        target: str
        """``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Target``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-target
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-greengrass.CfnSubscriptionDefinitionVersionProps", jsii_struct_bases=[])
class CfnSubscriptionDefinitionVersionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Greengrass::SubscriptionDefinitionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html
    Stability:
        stable
    """
    subscriptionDefinitionId: str
    """``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptiondefinitionid
    Stability:
        stable
    """

    subscriptions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSubscriptionDefinitionVersion.SubscriptionProperty"]]]
    """``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptions
    Stability:
        stable
    """

__all__ = ["CfnConnectorDefinition", "CfnConnectorDefinitionProps", "CfnConnectorDefinitionVersion", "CfnConnectorDefinitionVersionProps", "CfnCoreDefinition", "CfnCoreDefinitionProps", "CfnCoreDefinitionVersion", "CfnCoreDefinitionVersionProps", "CfnDeviceDefinition", "CfnDeviceDefinitionProps", "CfnDeviceDefinitionVersion", "CfnDeviceDefinitionVersionProps", "CfnFunctionDefinition", "CfnFunctionDefinitionProps", "CfnFunctionDefinitionVersion", "CfnFunctionDefinitionVersionProps", "CfnGroup", "CfnGroupProps", "CfnGroupVersion", "CfnGroupVersionProps", "CfnLoggerDefinition", "CfnLoggerDefinitionProps", "CfnLoggerDefinitionVersion", "CfnLoggerDefinitionVersionProps", "CfnResourceDefinition", "CfnResourceDefinitionProps", "CfnResourceDefinitionVersion", "CfnResourceDefinitionVersionProps", "CfnSubscriptionDefinition", "CfnSubscriptionDefinitionProps", "CfnSubscriptionDefinitionVersion", "CfnSubscriptionDefinitionVersionProps", "__jsii_assembly__"]

publication.publish()
