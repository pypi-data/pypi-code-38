import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.assets
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_ec2
import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.aws_logs
import aws_cdk.aws_s3
import aws_cdk.aws_sqs
import aws_cdk.cdk
import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-lambda", "0.34.0", __name__, "aws-lambda@0.34.0.jsii.tgz")
@jsii.data_type_optionals(jsii_struct_bases=[])
class _AliasProps(jsii.compat.TypedDict, total=False):
    additionalVersions: typing.List["VersionWeight"]
    """Additional versions with individual weights this alias points to.

    Individual additional version weights specified here should add up to
    (less than) one. All remaining weight is routed to the default
    version.

    For example, the config is Example::

       version: "1"
       additionalVersions: [{ version: "2", weight: 0.05 }]

    Then 5% of traffic will be routed to function version 2, while
    the remaining 95% of traffic will be routed to function version 1.

    Default:
        No additional versions

    Stability:
        experimental
    """
    description: str
    """Description for the alias.

    Default:
        No description

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.AliasProps", jsii_struct_bases=[_AliasProps])
class AliasProps(_AliasProps):
    """Properties for a new Lambda alias.

    Stability:
        experimental
    """
    aliasName: str
    """Name of this alias.

    Stability:
        experimental
    """

    version: "IVersion"
    """Function version this alias refers to.

    Use lambda.addVersion() to obtain a new lambda version to refer to.

    Stability:
        experimental
    """

class CfnAlias(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.CfnAlias"):
    """A CloudFormation ``AWS::Lambda::Alias``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-alias.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Lambda::Alias
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, function_name: str, function_version: str, name: str, description: typing.Optional[str]=None, routing_config: typing.Optional[typing.Union[typing.Optional["AliasRoutingConfigurationProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::Lambda::Alias``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            functionName: ``AWS::Lambda::Alias.FunctionName``.
            functionVersion: ``AWS::Lambda::Alias.FunctionVersion``.
            name: ``AWS::Lambda::Alias.Name``.
            description: ``AWS::Lambda::Alias.Description``.
            routingConfig: ``AWS::Lambda::Alias.RoutingConfig``.

        Stability:
            experimental
        """
        props: CfnAliasProps = {"functionName": function_name, "functionVersion": function_version, "name": name}

        if description is not None:
            props["description"] = description

        if routing_config is not None:
            props["routingConfig"] = routing_config

        jsii.create(CfnAlias, self, [scope, id, props])

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
    @jsii.member(jsii_name="aliasArn")
    def alias_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "aliasArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnAliasProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnAlias.AliasRoutingConfigurationProperty", jsii_struct_bases=[])
    class AliasRoutingConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-alias-aliasroutingconfiguration.html
        Stability:
            experimental
        """
        additionalVersionWeights: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnAlias.VersionWeightProperty"]]]
        """``CfnAlias.AliasRoutingConfigurationProperty.AdditionalVersionWeights``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-alias-aliasroutingconfiguration.html#cfn-lambda-alias-aliasroutingconfiguration-additionalversionweights
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnAlias.VersionWeightProperty", jsii_struct_bases=[])
    class VersionWeightProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-alias-versionweight.html
        Stability:
            experimental
        """
        functionVersion: str
        """``CfnAlias.VersionWeightProperty.FunctionVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-alias-versionweight.html#cfn-lambda-alias-versionweight-functionversion
        Stability:
            experimental
        """

        functionWeight: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnAlias.VersionWeightProperty.FunctionWeight``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-alias-versionweight.html#cfn-lambda-alias-versionweight-functionweight
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAliasProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::Lambda::Alias.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-alias.html#cfn-lambda-alias-description
    Stability:
        experimental
    """
    routingConfig: typing.Union["CfnAlias.AliasRoutingConfigurationProperty", aws_cdk.cdk.Token]
    """``AWS::Lambda::Alias.RoutingConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-alias.html#cfn-lambda-alias-routingconfig
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnAliasProps", jsii_struct_bases=[_CfnAliasProps])
class CfnAliasProps(_CfnAliasProps):
    """Properties for defining a ``AWS::Lambda::Alias``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-alias.html
    Stability:
        experimental
    """
    functionName: str
    """``AWS::Lambda::Alias.FunctionName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-alias.html#cfn-lambda-alias-functionname
    Stability:
        experimental
    """

    functionVersion: str
    """``AWS::Lambda::Alias.FunctionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-alias.html#cfn-lambda-alias-functionversion
    Stability:
        experimental
    """

    name: str
    """``AWS::Lambda::Alias.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-alias.html#cfn-lambda-alias-name
    Stability:
        experimental
    """

class CfnEventSourceMapping(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.CfnEventSourceMapping"):
    """A CloudFormation ``AWS::Lambda::EventSourceMapping``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-eventsourcemapping.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Lambda::EventSourceMapping
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, event_source_arn: str, function_name: str, batch_size: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, starting_position: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Lambda::EventSourceMapping``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            eventSourceArn: ``AWS::Lambda::EventSourceMapping.EventSourceArn``.
            functionName: ``AWS::Lambda::EventSourceMapping.FunctionName``.
            batchSize: ``AWS::Lambda::EventSourceMapping.BatchSize``.
            enabled: ``AWS::Lambda::EventSourceMapping.Enabled``.
            startingPosition: ``AWS::Lambda::EventSourceMapping.StartingPosition``.

        Stability:
            experimental
        """
        props: CfnEventSourceMappingProps = {"eventSourceArn": event_source_arn, "functionName": function_name}

        if batch_size is not None:
            props["batchSize"] = batch_size

        if enabled is not None:
            props["enabled"] = enabled

        if starting_position is not None:
            props["startingPosition"] = starting_position

        jsii.create(CfnEventSourceMapping, self, [scope, id, props])

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
    @jsii.member(jsii_name="eventSourceMappingName")
    def event_source_mapping_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "eventSourceMappingName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnEventSourceMappingProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEventSourceMappingProps(jsii.compat.TypedDict, total=False):
    batchSize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Lambda::EventSourceMapping.BatchSize``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-eventsourcemapping.html#cfn-lambda-eventsourcemapping-batchsize
    Stability:
        experimental
    """
    enabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::Lambda::EventSourceMapping.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-eventsourcemapping.html#cfn-lambda-eventsourcemapping-enabled
    Stability:
        experimental
    """
    startingPosition: str
    """``AWS::Lambda::EventSourceMapping.StartingPosition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-eventsourcemapping.html#cfn-lambda-eventsourcemapping-startingposition
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnEventSourceMappingProps", jsii_struct_bases=[_CfnEventSourceMappingProps])
class CfnEventSourceMappingProps(_CfnEventSourceMappingProps):
    """Properties for defining a ``AWS::Lambda::EventSourceMapping``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-eventsourcemapping.html
    Stability:
        experimental
    """
    eventSourceArn: str
    """``AWS::Lambda::EventSourceMapping.EventSourceArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-eventsourcemapping.html#cfn-lambda-eventsourcemapping-eventsourcearn
    Stability:
        experimental
    """

    functionName: str
    """``AWS::Lambda::EventSourceMapping.FunctionName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-eventsourcemapping.html#cfn-lambda-eventsourcemapping-functionname
    Stability:
        experimental
    """

class CfnFunction(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.CfnFunction"):
    """A CloudFormation ``AWS::Lambda::Function``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Lambda::Function
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, code: typing.Union[aws_cdk.cdk.Token, "CodeProperty"], handler: str, role: str, runtime: str, dead_letter_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["DeadLetterConfigProperty"]]]=None, description: typing.Optional[str]=None, environment: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["EnvironmentProperty"]]]=None, function_name: typing.Optional[str]=None, kms_key_arn: typing.Optional[str]=None, layers: typing.Optional[typing.List[str]]=None, memory_size: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, reserved_concurrent_executions: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, timeout: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, tracing_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["TracingConfigProperty"]]]=None, vpc_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["VpcConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::Lambda::Function``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            code: ``AWS::Lambda::Function.Code``.
            handler: ``AWS::Lambda::Function.Handler``.
            role: ``AWS::Lambda::Function.Role``.
            runtime: ``AWS::Lambda::Function.Runtime``.
            deadLetterConfig: ``AWS::Lambda::Function.DeadLetterConfig``.
            description: ``AWS::Lambda::Function.Description``.
            environment: ``AWS::Lambda::Function.Environment``.
            functionName: ``AWS::Lambda::Function.FunctionName``.
            kmsKeyArn: ``AWS::Lambda::Function.KmsKeyArn``.
            layers: ``AWS::Lambda::Function.Layers``.
            memorySize: ``AWS::Lambda::Function.MemorySize``.
            reservedConcurrentExecutions: ``AWS::Lambda::Function.ReservedConcurrentExecutions``.
            tags: ``AWS::Lambda::Function.Tags``.
            timeout: ``AWS::Lambda::Function.Timeout``.
            tracingConfig: ``AWS::Lambda::Function.TracingConfig``.
            vpcConfig: ``AWS::Lambda::Function.VpcConfig``.

        Stability:
            experimental
        """
        props: CfnFunctionProps = {"code": code, "handler": handler, "role": role, "runtime": runtime}

        if dead_letter_config is not None:
            props["deadLetterConfig"] = dead_letter_config

        if description is not None:
            props["description"] = description

        if environment is not None:
            props["environment"] = environment

        if function_name is not None:
            props["functionName"] = function_name

        if kms_key_arn is not None:
            props["kmsKeyArn"] = kms_key_arn

        if layers is not None:
            props["layers"] = layers

        if memory_size is not None:
            props["memorySize"] = memory_size

        if reserved_concurrent_executions is not None:
            props["reservedConcurrentExecutions"] = reserved_concurrent_executions

        if tags is not None:
            props["tags"] = tags

        if timeout is not None:
            props["timeout"] = timeout

        if tracing_config is not None:
            props["tracingConfig"] = tracing_config

        if vpc_config is not None:
            props["vpcConfig"] = vpc_config

        jsii.create(CfnFunction, self, [scope, id, props])

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
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "functionArn")

    @property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "functionName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnFunctionProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnFunction.CodeProperty", jsii_struct_bases=[])
    class CodeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-code.html
        Stability:
            experimental
        """
        s3Bucket: str
        """``CfnFunction.CodeProperty.S3Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-code.html#cfn-lambda-function-code-s3bucket
        Stability:
            experimental
        """

        s3Key: str
        """``CfnFunction.CodeProperty.S3Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-code.html#cfn-lambda-function-code-s3key
        Stability:
            experimental
        """

        s3ObjectVersion: str
        """``CfnFunction.CodeProperty.S3ObjectVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-code.html#cfn-lambda-function-code-s3objectversion
        Stability:
            experimental
        """

        zipFile: str
        """``CfnFunction.CodeProperty.ZipFile``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-code.html#cfn-lambda-function-code-zipfile
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnFunction.DeadLetterConfigProperty", jsii_struct_bases=[])
    class DeadLetterConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-deadletterconfig.html
        Stability:
            experimental
        """
        targetArn: str
        """``CfnFunction.DeadLetterConfigProperty.TargetArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-deadletterconfig.html#cfn-lambda-function-deadletterconfig-targetarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnFunction.EnvironmentProperty", jsii_struct_bases=[])
    class EnvironmentProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-environment.html
        Stability:
            experimental
        """
        variables: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnFunction.EnvironmentProperty.Variables``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-environment.html#cfn-lambda-function-environment-variables
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnFunction.TracingConfigProperty", jsii_struct_bases=[])
    class TracingConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-tracingconfig.html
        Stability:
            experimental
        """
        mode: str
        """``CfnFunction.TracingConfigProperty.Mode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-tracingconfig.html#cfn-lambda-function-tracingconfig-mode
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnFunction.VpcConfigProperty", jsii_struct_bases=[])
    class VpcConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-vpcconfig.html
        Stability:
            experimental
        """
        securityGroupIds: typing.List[str]
        """``CfnFunction.VpcConfigProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-vpcconfig.html#cfn-lambda-function-vpcconfig-securitygroupids
        Stability:
            experimental
        """

        subnetIds: typing.List[str]
        """``CfnFunction.VpcConfigProperty.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-vpcconfig.html#cfn-lambda-function-vpcconfig-subnetids
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnFunctionProps(jsii.compat.TypedDict, total=False):
    deadLetterConfig: typing.Union[aws_cdk.cdk.Token, "CfnFunction.DeadLetterConfigProperty"]
    """``AWS::Lambda::Function.DeadLetterConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-deadletterconfig
    Stability:
        experimental
    """
    description: str
    """``AWS::Lambda::Function.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-description
    Stability:
        experimental
    """
    environment: typing.Union[aws_cdk.cdk.Token, "CfnFunction.EnvironmentProperty"]
    """``AWS::Lambda::Function.Environment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-environment
    Stability:
        experimental
    """
    functionName: str
    """``AWS::Lambda::Function.FunctionName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-functionname
    Stability:
        experimental
    """
    kmsKeyArn: str
    """``AWS::Lambda::Function.KmsKeyArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-kmskeyarn
    Stability:
        experimental
    """
    layers: typing.List[str]
    """``AWS::Lambda::Function.Layers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-layers
    Stability:
        experimental
    """
    memorySize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Lambda::Function.MemorySize``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-memorysize
    Stability:
        experimental
    """
    reservedConcurrentExecutions: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Lambda::Function.ReservedConcurrentExecutions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-reservedconcurrentexecutions
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Lambda::Function.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-tags
    Stability:
        experimental
    """
    timeout: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Lambda::Function.Timeout``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-timeout
    Stability:
        experimental
    """
    tracingConfig: typing.Union[aws_cdk.cdk.Token, "CfnFunction.TracingConfigProperty"]
    """``AWS::Lambda::Function.TracingConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-tracingconfig
    Stability:
        experimental
    """
    vpcConfig: typing.Union[aws_cdk.cdk.Token, "CfnFunction.VpcConfigProperty"]
    """``AWS::Lambda::Function.VpcConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-vpcconfig
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnFunctionProps", jsii_struct_bases=[_CfnFunctionProps])
class CfnFunctionProps(_CfnFunctionProps):
    """Properties for defining a ``AWS::Lambda::Function``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html
    Stability:
        experimental
    """
    code: typing.Union[aws_cdk.cdk.Token, "CfnFunction.CodeProperty"]
    """``AWS::Lambda::Function.Code``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-code
    Stability:
        experimental
    """

    handler: str
    """``AWS::Lambda::Function.Handler``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-handler
    Stability:
        experimental
    """

    role: str
    """``AWS::Lambda::Function.Role``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-role
    Stability:
        experimental
    """

    runtime: str
    """``AWS::Lambda::Function.Runtime``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-runtime
    Stability:
        experimental
    """

class CfnLayerVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.CfnLayerVersion"):
    """A CloudFormation ``AWS::Lambda::LayerVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversion.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Lambda::LayerVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, content: typing.Union[aws_cdk.cdk.Token, "ContentProperty"], compatible_runtimes: typing.Optional[typing.List[str]]=None, description: typing.Optional[str]=None, layer_name: typing.Optional[str]=None, license_info: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Lambda::LayerVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            content: ``AWS::Lambda::LayerVersion.Content``.
            compatibleRuntimes: ``AWS::Lambda::LayerVersion.CompatibleRuntimes``.
            description: ``AWS::Lambda::LayerVersion.Description``.
            layerName: ``AWS::Lambda::LayerVersion.LayerName``.
            licenseInfo: ``AWS::Lambda::LayerVersion.LicenseInfo``.

        Stability:
            experimental
        """
        props: CfnLayerVersionProps = {"content": content}

        if compatible_runtimes is not None:
            props["compatibleRuntimes"] = compatible_runtimes

        if description is not None:
            props["description"] = description

        if layer_name is not None:
            props["layerName"] = layer_name

        if license_info is not None:
            props["licenseInfo"] = license_info

        jsii.create(CfnLayerVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="layerVersionArn")
    def layer_version_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "layerVersionArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnLayerVersionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ContentProperty(jsii.compat.TypedDict, total=False):
        s3ObjectVersion: str
        """``CfnLayerVersion.ContentProperty.S3ObjectVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-layerversion-content.html#cfn-lambda-layerversion-content-s3objectversion
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnLayerVersion.ContentProperty", jsii_struct_bases=[_ContentProperty])
    class ContentProperty(_ContentProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-layerversion-content.html
        Stability:
            experimental
        """
        s3Bucket: str
        """``CfnLayerVersion.ContentProperty.S3Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-layerversion-content.html#cfn-lambda-layerversion-content-s3bucket
        Stability:
            experimental
        """

        s3Key: str
        """``CfnLayerVersion.ContentProperty.S3Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-layerversion-content.html#cfn-lambda-layerversion-content-s3key
        Stability:
            experimental
        """


class CfnLayerVersionPermission(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.CfnLayerVersionPermission"):
    """A CloudFormation ``AWS::Lambda::LayerVersionPermission``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversionpermission.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Lambda::LayerVersionPermission
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, action: str, layer_version_arn: str, principal: str, organization_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Lambda::LayerVersionPermission``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            action: ``AWS::Lambda::LayerVersionPermission.Action``.
            layerVersionArn: ``AWS::Lambda::LayerVersionPermission.LayerVersionArn``.
            principal: ``AWS::Lambda::LayerVersionPermission.Principal``.
            organizationId: ``AWS::Lambda::LayerVersionPermission.OrganizationId``.

        Stability:
            experimental
        """
        props: CfnLayerVersionPermissionProps = {"action": action, "layerVersionArn": layer_version_arn, "principal": principal}

        if organization_id is not None:
            props["organizationId"] = organization_id

        jsii.create(CfnLayerVersionPermission, self, [scope, id, props])

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
    @jsii.member(jsii_name="layerVersionPermissionArn")
    def layer_version_permission_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "layerVersionPermissionArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnLayerVersionPermissionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnLayerVersionPermissionProps(jsii.compat.TypedDict, total=False):
    organizationId: str
    """``AWS::Lambda::LayerVersionPermission.OrganizationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversionpermission.html#cfn-lambda-layerversionpermission-organizationid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnLayerVersionPermissionProps", jsii_struct_bases=[_CfnLayerVersionPermissionProps])
class CfnLayerVersionPermissionProps(_CfnLayerVersionPermissionProps):
    """Properties for defining a ``AWS::Lambda::LayerVersionPermission``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversionpermission.html
    Stability:
        experimental
    """
    action: str
    """``AWS::Lambda::LayerVersionPermission.Action``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversionpermission.html#cfn-lambda-layerversionpermission-action
    Stability:
        experimental
    """

    layerVersionArn: str
    """``AWS::Lambda::LayerVersionPermission.LayerVersionArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversionpermission.html#cfn-lambda-layerversionpermission-layerversionarn
    Stability:
        experimental
    """

    principal: str
    """``AWS::Lambda::LayerVersionPermission.Principal``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversionpermission.html#cfn-lambda-layerversionpermission-principal
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnLayerVersionProps(jsii.compat.TypedDict, total=False):
    compatibleRuntimes: typing.List[str]
    """``AWS::Lambda::LayerVersion.CompatibleRuntimes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversion.html#cfn-lambda-layerversion-compatibleruntimes
    Stability:
        experimental
    """
    description: str
    """``AWS::Lambda::LayerVersion.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversion.html#cfn-lambda-layerversion-description
    Stability:
        experimental
    """
    layerName: str
    """``AWS::Lambda::LayerVersion.LayerName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversion.html#cfn-lambda-layerversion-layername
    Stability:
        experimental
    """
    licenseInfo: str
    """``AWS::Lambda::LayerVersion.LicenseInfo``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversion.html#cfn-lambda-layerversion-licenseinfo
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnLayerVersionProps", jsii_struct_bases=[_CfnLayerVersionProps])
class CfnLayerVersionProps(_CfnLayerVersionProps):
    """Properties for defining a ``AWS::Lambda::LayerVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversion.html
    Stability:
        experimental
    """
    content: typing.Union[aws_cdk.cdk.Token, "CfnLayerVersion.ContentProperty"]
    """``AWS::Lambda::LayerVersion.Content``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-layerversion.html#cfn-lambda-layerversion-content
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnParametersCodeProps", jsii_struct_bases=[])
class CfnParametersCodeProps(jsii.compat.TypedDict, total=False):
    """Construction properties for {@link CfnParametersCode}.

    Stability:
        experimental
    """
    bucketNameParam: aws_cdk.cdk.CfnParameter
    """The CloudFormation parameter that represents the name of the S3 Bucket where the Lambda code will be located in. Must be of type 'String'.

    Default:
        a new parameter will be created

    Stability:
        experimental
    """

    objectKeyParam: aws_cdk.cdk.CfnParameter
    """The CloudFormation parameter that represents the path inside the S3 Bucket where the Lambda code will be located at. Must be of type 'String'.

    Default:
        a new parameter will be created

    Stability:
        experimental
    """

class CfnPermission(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.CfnPermission"):
    """A CloudFormation ``AWS::Lambda::Permission``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-permission.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Lambda::Permission
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, action: str, function_name: str, principal: str, event_source_token: typing.Optional[str]=None, source_account: typing.Optional[str]=None, source_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Lambda::Permission``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            action: ``AWS::Lambda::Permission.Action``.
            functionName: ``AWS::Lambda::Permission.FunctionName``.
            principal: ``AWS::Lambda::Permission.Principal``.
            eventSourceToken: ``AWS::Lambda::Permission.EventSourceToken``.
            sourceAccount: ``AWS::Lambda::Permission.SourceAccount``.
            sourceArn: ``AWS::Lambda::Permission.SourceArn``.

        Stability:
            experimental
        """
        props: CfnPermissionProps = {"action": action, "functionName": function_name, "principal": principal}

        if event_source_token is not None:
            props["eventSourceToken"] = event_source_token

        if source_account is not None:
            props["sourceAccount"] = source_account

        if source_arn is not None:
            props["sourceArn"] = source_arn

        jsii.create(CfnPermission, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnPermissionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPermissionProps(jsii.compat.TypedDict, total=False):
    eventSourceToken: str
    """``AWS::Lambda::Permission.EventSourceToken``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-permission.html#cfn-lambda-permission-eventsourcetoken
    Stability:
        experimental
    """
    sourceAccount: str
    """``AWS::Lambda::Permission.SourceAccount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-permission.html#cfn-lambda-permission-sourceaccount
    Stability:
        experimental
    """
    sourceArn: str
    """``AWS::Lambda::Permission.SourceArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-permission.html#cfn-lambda-permission-sourcearn
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnPermissionProps", jsii_struct_bases=[_CfnPermissionProps])
class CfnPermissionProps(_CfnPermissionProps):
    """Properties for defining a ``AWS::Lambda::Permission``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-permission.html
    Stability:
        experimental
    """
    action: str
    """``AWS::Lambda::Permission.Action``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-permission.html#cfn-lambda-permission-action
    Stability:
        experimental
    """

    functionName: str
    """``AWS::Lambda::Permission.FunctionName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-permission.html#cfn-lambda-permission-functionname
    Stability:
        experimental
    """

    principal: str
    """``AWS::Lambda::Permission.Principal``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-permission.html#cfn-lambda-permission-principal
    Stability:
        experimental
    """

class CfnVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.CfnVersion"):
    """A CloudFormation ``AWS::Lambda::Version``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-version.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Lambda::Version
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, function_name: str, code_sha256: typing.Optional[str]=None, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Lambda::Version``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            functionName: ``AWS::Lambda::Version.FunctionName``.
            codeSha256: ``AWS::Lambda::Version.CodeSha256``.
            description: ``AWS::Lambda::Version.Description``.

        Stability:
            experimental
        """
        props: CfnVersionProps = {"functionName": function_name}

        if code_sha256 is not None:
            props["codeSha256"] = code_sha256

        if description is not None:
            props["description"] = description

        jsii.create(CfnVersion, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnVersionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="version")
    def version(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Version
        """
        return jsii.get(self, "version")

    @property
    @jsii.member(jsii_name="versionArn")
    def version_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "versionArn")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVersionProps(jsii.compat.TypedDict, total=False):
    codeSha256: str
    """``AWS::Lambda::Version.CodeSha256``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-version.html#cfn-lambda-version-codesha256
    Stability:
        experimental
    """
    description: str
    """``AWS::Lambda::Version.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-version.html#cfn-lambda-version-description
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.CfnVersionProps", jsii_struct_bases=[_CfnVersionProps])
class CfnVersionProps(_CfnVersionProps):
    """Properties for defining a ``AWS::Lambda::Version``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-version.html
    Stability:
        experimental
    """
    functionName: str
    """``AWS::Lambda::Version.FunctionName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-version.html#cfn-lambda-version-functionname
    Stability:
        experimental
    """

class Code(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-lambda.Code"):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _CodeProxy

    def __init__(self) -> None:
        jsii.create(Code, self, [])

    @jsii.member(jsii_name="asset")
    @classmethod
    def asset(cls, path: str) -> "AssetCode":
        """Loads the function code from a local disk asset.

        Arguments:
            path: Either a directory with the Lambda code bundle or a .zip file.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "asset", [path])

    @jsii.member(jsii_name="bucket")
    @classmethod
    def bucket(cls, bucket: aws_cdk.aws_s3.IBucket, key: str, object_version: typing.Optional[str]=None) -> "S3Code":
        """
        Arguments:
            bucket: The S3 bucket.
            key: The object key.
            objectVersion: Optional S3 object version.

        Returns:
            ``LambdaS3Code`` associated with the specified S3 object.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "bucket", [bucket, key, object_version])

    @jsii.member(jsii_name="cfnParameters")
    @classmethod
    def cfn_parameters(cls, *, bucket_name_param: typing.Optional[aws_cdk.cdk.CfnParameter]=None, object_key_param: typing.Optional[aws_cdk.cdk.CfnParameter]=None) -> "CfnParametersCode":
        """Creates a new Lambda source defined using CloudFormation parameters.

        Arguments:
            props: optional construction properties of {@link CfnParametersCode}.
            bucketNameParam: The CloudFormation parameter that represents the name of the S3 Bucket where the Lambda code will be located in. Must be of type 'String'. Default: a new parameter will be created
            objectKeyParam: The CloudFormation parameter that represents the path inside the S3 Bucket where the Lambda code will be located at. Must be of type 'String'. Default: a new parameter will be created

        Returns:
            a new instance of ``CfnParametersCode``

        Stability:
            experimental
        """
        props: CfnParametersCodeProps = {}

        if bucket_name_param is not None:
            props["bucketNameParam"] = bucket_name_param

        if object_key_param is not None:
            props["objectKeyParam"] = object_key_param

        return jsii.sinvoke(cls, "cfnParameters", [props])

    @jsii.member(jsii_name="directory")
    @classmethod
    def directory(cls, directory_to_zip: str) -> "AssetCode":
        """
        Arguments:
            directoryToZip: The directory to zip.

        Returns:
            Zip archives the contents of a directory on disk and uses this
            as the lambda handler's code.

        Deprecated:
            use ``lambda.Code.asset(path)`` (no need to specify if it's a file or a directory)

        Stability:
            deprecated
        """
        return jsii.sinvoke(cls, "directory", [directory_to_zip])

    @jsii.member(jsii_name="file")
    @classmethod
    def file(cls, file_path: str) -> "AssetCode":
        """
        Arguments:
            filePath: The file path.

        Returns:
            Uses a file on disk as a lambda handler's code.

        Deprecated:
            use ``lambda.Code.asset(path)`` (no need to specify if it's a file or a directory)

        Stability:
            deprecated
        """
        return jsii.sinvoke(cls, "file", [file_path])

    @jsii.member(jsii_name="inline")
    @classmethod
    def inline(cls, code: str) -> "InlineCode":
        """
        Arguments:
            code: The actual handler code (limited to 4KiB).

        Returns:
            ``LambdaInlineCode`` with inline code.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "inline", [code])

    @jsii.member(jsii_name="bind")
    def bind(self, _construct: aws_cdk.cdk.Construct) -> None:
        """Called when the lambda or layer is initialized to allow this object to bind to the stack, add resources and have fun.

        Arguments:
            _construct: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_construct])

    @property
    @jsii.member(jsii_name="isInline")
    @abc.abstractmethod
    def is_inline(self) -> bool:
        """Determines whether this Code is inline code or not.

        Stability:
            experimental
        """
        ...


class _CodeProxy(Code):
    @property
    @jsii.member(jsii_name="isInline")
    def is_inline(self) -> bool:
        """Determines whether this Code is inline code or not.

        Stability:
            experimental
        """
        return jsii.get(self, "isInline")


class AssetCode(Code, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.AssetCode"):
    """Lambda code from a local directory.

    Stability:
        experimental
    """
    def __init__(self, path: str, packaging: typing.Optional[aws_cdk.assets.AssetPackaging]=None) -> None:
        """
        Arguments:
            path: The path to the asset file or directory.
            packaging: The asset packaging format (optional, determined automatically).

        Stability:
            experimental
        """
        jsii.create(AssetCode, self, [path, packaging])

    @jsii.member(jsii_name="bind")
    def bind(self, construct: aws_cdk.cdk.Construct) -> None:
        """Called when the lambda or layer is initialized to allow this object to bind to the stack, add resources and have fun.

        Arguments:
            construct: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [construct])

    @property
    @jsii.member(jsii_name="isInline")
    def is_inline(self) -> bool:
        """Determines whether this Code is inline code or not.

        Stability:
            experimental
        """
        return jsii.get(self, "isInline")

    @property
    @jsii.member(jsii_name="packaging")
    def packaging(self) -> aws_cdk.assets.AssetPackaging:
        """The asset packaging.

        Stability:
            experimental
        """
        return jsii.get(self, "packaging")

    @property
    @jsii.member(jsii_name="path")
    def path(self) -> str:
        """The path to the asset file or directory.

        Stability:
            experimental
        """
        return jsii.get(self, "path")


class CfnParametersCode(Code, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.CfnParametersCode"):
    """Lambda code defined using 2 CloudFormation parameters. Useful when you don't have access to the code of your Lambda from your CDK code, so you can't use Assets, and you want to deploy the Lambda in a CodePipeline, using CloudFormation Actions - you can fill the parameters using the {@link #assign} method.

    Stability:
        experimental
    """
    def __init__(self, *, bucket_name_param: typing.Optional[aws_cdk.cdk.CfnParameter]=None, object_key_param: typing.Optional[aws_cdk.cdk.CfnParameter]=None) -> None:
        """
        Arguments:
            props: -
            bucketNameParam: The CloudFormation parameter that represents the name of the S3 Bucket where the Lambda code will be located in. Must be of type 'String'. Default: a new parameter will be created
            objectKeyParam: The CloudFormation parameter that represents the path inside the S3 Bucket where the Lambda code will be located at. Must be of type 'String'. Default: a new parameter will be created

        Stability:
            experimental
        """
        props: CfnParametersCodeProps = {}

        if bucket_name_param is not None:
            props["bucketNameParam"] = bucket_name_param

        if object_key_param is not None:
            props["objectKeyParam"] = object_key_param

        jsii.create(CfnParametersCode, self, [props])

    @jsii.member(jsii_name="assign")
    def assign(self, *, bucket_name: str, object_key: str) -> typing.Mapping[str,typing.Any]:
        """Create a parameters map from this instance's CloudFormation parameters.

        It returns a map with 2 keys that correspond to the names of the parameters defined in this Lambda code,
        and as values it contains the appropriate expressions pointing at the provided S3 coordinates
        (most likely, obtained from a CodePipeline Artifact by calling the ``artifact.s3Coordinates`` method).
        The result should be provided to the CloudFormation Action
        that is deploying the Stack that the Lambda with this code is part of,
        in the ``parameterOverrides`` property.

        Arguments:
            coordinates: the coordinates of the object in S3 that represents the Lambda code.
            bucketName: The name of the S3 Bucket the object is in.
            objectKey: The path inside the Bucket where the object is located at.

        Stability:
            experimental
        """
        coordinates: aws_cdk.aws_s3.Coordinates = {"bucketName": bucket_name, "objectKey": object_key}

        return jsii.invoke(self, "assign", [coordinates])

    @jsii.member(jsii_name="bind")
    def bind(self, construct: aws_cdk.cdk.Construct) -> None:
        """Called when the lambda or layer is initialized to allow this object to bind to the stack, add resources and have fun.

        Arguments:
            construct: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [construct])

    @property
    @jsii.member(jsii_name="bucketNameParam")
    def bucket_name_param(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "bucketNameParam")

    @property
    @jsii.member(jsii_name="isInline")
    def is_inline(self) -> bool:
        """Determines whether this Code is inline code or not.

        Stability:
            experimental
        """
        return jsii.get(self, "isInline")

    @property
    @jsii.member(jsii_name="objectKeyParam")
    def object_key_param(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "objectKeyParam")


class EventSourceMapping(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.EventSourceMapping"):
    """Defines a Lambda EventSourceMapping resource.

    Usually, you won't need to define the mapping yourself. This will usually be done by
    event sources. For example, to add an SQS event source to a function::

       import { SqsEventSource } from '@aws-cdk/aws-lambda-event-sources';
       lambda.addEventSource(new SqsEventSource(sqs));

    The ``SqsEventSource`` class will automatically create the mapping, and will also
    modify the Lambda's execution role so it can consume messages from the queue.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, target: "IFunction", event_source_arn: str, batch_size: typing.Optional[jsii.Number]=None, enabled: typing.Optional[bool]=None, starting_position: typing.Optional["StartingPosition"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            target: The target AWS Lambda function.
            eventSourceArn: The Amazon Resource Name (ARN) of the event source. Any record added to this stream can invoke the Lambda function.
            batchSize: The largest number of records that AWS Lambda will retrieve from your event source at the time of invoking your function. Your function receives an event with all the retrieved records. Valid Range: Minimum value of 1. Maximum value of 10000. Default: - Amazon Kinesis and Amazon DynamoDB is 100 records. Both the default and maximum for Amazon SQS are 10 messages.
            enabled: Set to false to disable the event source upon creation. Default: true
            startingPosition: The position in the DynamoDB or Kinesis stream where AWS Lambda should start reading. Default: - Required for Amazon Kinesis and Amazon DynamoDB Streams sources.

        Stability:
            experimental
        """
        props: EventSourceMappingProps = {"target": target, "eventSourceArn": event_source_arn}

        if batch_size is not None:
            props["batchSize"] = batch_size

        if enabled is not None:
            props["enabled"] = enabled

        if starting_position is not None:
            props["startingPosition"] = starting_position

        jsii.create(EventSourceMapping, self, [scope, id, props])


@jsii.data_type_optionals(jsii_struct_bases=[])
class _EventSourceMappingOptions(jsii.compat.TypedDict, total=False):
    batchSize: jsii.Number
    """The largest number of records that AWS Lambda will retrieve from your event source at the time of invoking your function.

    Your function receives an
    event with all the retrieved records.

    Valid Range: Minimum value of 1. Maximum value of 10000.

    Default:
        - Amazon Kinesis and Amazon DynamoDB is 100 records.
          Both the default and maximum for Amazon SQS are 10 messages.

    Stability:
        experimental
    """
    enabled: bool
    """Set to false to disable the event source upon creation.

    Default:
        true

    Stability:
        experimental
    """
    startingPosition: "StartingPosition"
    """The position in the DynamoDB or Kinesis stream where AWS Lambda should start reading.

    Default:
        - Required for Amazon Kinesis and Amazon DynamoDB Streams sources.

    See:
        https://docs.aws.amazon.com/kinesis/latest/APIReference/API_GetShardIterator.html#Kinesis-GetShardIterator-request-ShardIteratorType
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.EventSourceMappingOptions", jsii_struct_bases=[_EventSourceMappingOptions])
class EventSourceMappingOptions(_EventSourceMappingOptions):
    """
    Stability:
        experimental
    """
    eventSourceArn: str
    """The Amazon Resource Name (ARN) of the event source.

    Any record added to
    this stream can invoke the Lambda function.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.EventSourceMappingProps", jsii_struct_bases=[EventSourceMappingOptions])
class EventSourceMappingProps(EventSourceMappingOptions, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    target: "IFunction"
    """The target AWS Lambda function.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _FunctionAttributes(jsii.compat.TypedDict, total=False):
    role: aws_cdk.aws_iam.IRole
    """The IAM execution role associated with this function.

    If the role is not specified, any role-related operations will no-op.

    Stability:
        experimental
    """
    securityGroupId: str
    """Id of the securityGroup for this Lambda, if in a VPC.

    This needs to be given in order to support allowing connections
    to this Lambda.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.FunctionAttributes", jsii_struct_bases=[_FunctionAttributes])
class FunctionAttributes(_FunctionAttributes):
    """Represents a Lambda function defined outside of this stack.

    Stability:
        experimental
    """
    functionArn: str
    """The ARN of the Lambda function.

    Format: arn::lambda:::function:

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _FunctionProps(jsii.compat.TypedDict, total=False):
    allowAllOutbound: bool
    """Whether to allow the Lambda to send all network traffic.

    If set to false, you must individually add traffic rules to allow the
    Lambda to connect to network targets.

    Default:
        true

    Stability:
        experimental
    """
    deadLetterQueue: aws_cdk.aws_sqs.IQueue
    """The SQS queue to use if DLQ is enabled.

    Default:
        - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``

    Stability:
        experimental
    """
    deadLetterQueueEnabled: bool
    """Enabled DLQ.

    If ``deadLetterQueue`` is undefined,
    an SQS queue with default options will be defined for your Function.

    Default:
        - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.

    Stability:
        experimental
    """
    description: str
    """A description of the function.

    Default:
        - No description.

    Stability:
        experimental
    """
    environment: typing.Mapping[str,typing.Any]
    """Key-value pairs that Lambda caches and makes available for your Lambda functions.

    Use environment variables to apply configuration changes, such
    as test and production environment configurations, without changing your
    Lambda function source code.

    Default:
        - No environment variables.

    Stability:
        experimental
    """
    events: typing.List["IEventSource"]
    """Event sources for this function.

    You can also add event sources using ``addEventSource``.

    Default:
        - No event sources.

    Stability:
        experimental
    """
    functionName: str
    """A name for the function.

    Default:
        - AWS CloudFormation generates a unique physical ID and uses that
          ID for the function's name. For more information, see Name Type.

    Stability:
        experimental
    """
    initialPolicy: typing.List[aws_cdk.aws_iam.PolicyStatement]
    """Initial policy statements to add to the created Lambda Role.

    You can call ``addToRolePolicy`` to the created lambda to add statements post creation.

    Default:
        - No policy statements are added to the created Lambda role.

    Stability:
        experimental
    """
    layers: typing.List["ILayerVersion"]
    """A list of layers to add to the function's execution environment.

    You can configure your Lambda function to pull in
    additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies
    that can be used by mulitple functions.

    Default:
        - No layers.

    Stability:
        experimental
    """
    logRetentionDays: aws_cdk.aws_logs.RetentionDays
    """The number of days log events are kept in CloudWatch Logs.

    When updating
    this property, unsetting it doesn't remove the log retention policy. To
    remove the retention policy, set the value to ``Infinity``.

    Default:
        - Logs never expire.

    Stability:
        experimental
    """
    memorySize: jsii.Number
    """The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide.

    Default:
        128

    Stability:
        experimental
    """
    reservedConcurrentExecutions: jsii.Number
    """The maximum of concurrent executions you want to reserve for the function.

    Default:
        - No specific limit - account limit.

    See:
        https://docs.aws.amazon.com/lambda/latest/dg/concurrent-executions.html
    Stability:
        experimental
    """
    role: aws_cdk.aws_iam.IRole
    """Lambda execution role.

    This is the role that will be assumed by the function upon execution.
    It controls the permissions that the function will have. The Role must
    be assumable by the 'lambda.amazonaws.com' service principal.

    Default:
        - A unique role will be generated for this lambda function.
          Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.

    Stability:
        experimental
    """
    securityGroup: aws_cdk.aws_ec2.ISecurityGroup
    """What security group to associate with the Lambda's network interfaces.

    Only used if 'vpc' is supplied.

    Default:
        - If the function is placed within a VPC and a security group is
          not specified, a dedicated security group will be created for this
          function.

    Stability:
        experimental
    """
    timeout: jsii.Number
    """The function execution time (in seconds) after which Lambda terminates the function.

    Because the execution time affects cost, set this value
    based on the function's expected execution time.

    Default:
        3

    Stability:
        experimental
    """
    tracing: "Tracing"
    """Enable AWS X-Ray Tracing for Lambda Function.

    Default:
        Tracing.Disabled

    Stability:
        experimental
    """
    vpc: aws_cdk.aws_ec2.IVpc
    """VPC network to place Lambda network interfaces.

    Specify this if the Lambda function needs to access resources in a VPC.

    Default:
        - Function is not placed within a VPC.

    Stability:
        experimental
    """
    vpcSubnets: aws_cdk.aws_ec2.SubnetSelection
    """Where to place the network interfaces within the VPC.

    Only used if 'vpc' is supplied. Note: internet access for Lambdas
    requires a NAT gateway, so picking Public subnets is not allowed.

    Default:
        - Private subnets.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.FunctionProps", jsii_struct_bases=[_FunctionProps])
class FunctionProps(_FunctionProps):
    """
    Stability:
        experimental
    """
    code: "Code"
    """The source code of your Lambda function.

    You can point to a file in an
    Amazon Simple Storage Service (Amazon S3) bucket or specify your source
    code as inline text.

    Stability:
        experimental
    """

    handler: str
    """The name of the function (within your source code) that Lambda calls to start running your code.

    For more information, see the Handler property
    in the AWS Lambda Developer Guide.

    NOTE: If you specify your source code as inline text by specifying the
    ZipFile property within the Code property, specify index.function_name as
    the handler.

    Stability:
        experimental
    """

    runtime: "Runtime"
    """The runtime environment for the Lambda function that you are uploading. For valid values, see the Runtime property in the AWS Lambda Developer Guide.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-lambda.IEventSource")
class IEventSource(jsii.compat.Protocol):
    """An abstract class which represents an AWS Lambda event source.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IEventSourceProxy

    @jsii.member(jsii_name="bind")
    def bind(self, target: "IFunction") -> None:
        """Called by ``lambda.addEventSource`` to allow the event source to bind to this function.

        Arguments:
            target: That lambda function to bind to.

        Stability:
            experimental
        """
        ...


class _IEventSourceProxy():
    """An abstract class which represents an AWS Lambda event source.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-lambda.IEventSource"
    @jsii.member(jsii_name="bind")
    def bind(self, target: "IFunction") -> None:
        """Called by ``lambda.addEventSource`` to allow the event source to bind to this function.

        Arguments:
            target: That lambda function to bind to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [target])


@jsii.interface(jsii_type="@aws-cdk/aws-lambda.IFunction")
class IFunction(aws_cdk.cdk.IResource, aws_cdk.aws_ec2.IConnectable, aws_cdk.aws_iam.IGrantable, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IFunctionProxy

    @property
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> str:
        """The ARN fo the function.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> str:
        """The name of the function.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="id")
    def id(self) -> str:
        """Logical ID of this Function.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="isBoundToVpc")
    def is_bound_to_vpc(self) -> bool:
        """Whether or not this Lambda function was bound to a VPC.

        If this is is ``false``, trying to access the ``connections`` object will fail.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """The IAM role associated with this function.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addEventSource")
    def add_event_source(self, source: "IEventSource") -> None:
        """
        Arguments:
            source: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addEventSourceMapping")
    def add_event_source_mapping(self, id: str, *, event_source_arn: str, batch_size: typing.Optional[jsii.Number]=None, enabled: typing.Optional[bool]=None, starting_position: typing.Optional["StartingPosition"]=None) -> "EventSourceMapping":
        """Adds an event source that maps to this AWS Lambda function.

        Arguments:
            id: construct ID.
            options: mapping options.
            eventSourceArn: The Amazon Resource Name (ARN) of the event source. Any record added to this stream can invoke the Lambda function.
            batchSize: The largest number of records that AWS Lambda will retrieve from your event source at the time of invoking your function. Your function receives an event with all the retrieved records. Valid Range: Minimum value of 1. Maximum value of 10000. Default: - Amazon Kinesis and Amazon DynamoDB is 100 records. Both the default and maximum for Amazon SQS are 10 messages.
            enabled: Set to false to disable the event source upon creation. Default: true
            startingPosition: The position in the DynamoDB or Kinesis stream where AWS Lambda should start reading. Default: - Required for Amazon Kinesis and Amazon DynamoDB Streams sources.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addPermission")
    def add_permission(self, id: str, *, principal: aws_cdk.aws_iam.IPrincipal, action: typing.Optional[str]=None, event_source_token: typing.Optional[str]=None, source_account: typing.Optional[str]=None, source_arn: typing.Optional[str]=None) -> None:
        """Adds a permission to the Lambda resource policy.

        Arguments:
            id: The id ƒor the permission construct.
            permission: -
            principal: The entity for which you are granting permission to invoke the Lambda function. This entity can be any valid AWS service principal, such as s3.amazonaws.com or sns.amazonaws.com, or, if you are granting cross-account permission, an AWS account ID. For example, you might want to allow a custom application in another AWS account to push events to Lambda by invoking your function. The principal can be either an AccountPrincipal or a ServicePrincipal.
            action: The Lambda actions that you want to allow in this statement. For example, you can specify lambda:CreateFunction to specify a certain action, or use a wildcard (``lambda:*``) to grant permission to all Lambda actions. For a list of actions, see Actions and Condition Context Keys for AWS Lambda in the IAM User Guide. Default: 'lambda:InvokeFunction'
            eventSourceToken: A unique token that must be supplied by the principal invoking the function. Default: The caller would not need to present a token.
            sourceAccount: The AWS account ID (without hyphens) of the source owner. For example, if you specify an S3 bucket in the SourceArn property, this value is the bucket owner's account ID. You can use this property to ensure that all source principals are owned by a specific account.
            sourceArn: The ARN of a resource that is invoking your function. When granting Amazon Simple Storage Service (Amazon S3) permission to invoke your function, specify this property with the bucket ARN as its value. This ensures that events generated only from the specified bucket, not just any bucket from any AWS account that creates a mapping to your function, can invoke the function.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """
        Arguments:
            statement: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(self, identity: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant the given identity permissions to invoke this Lambda.

        Arguments:
            identity: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Lambda Return the given named metric for this Function.

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

    @jsii.member(jsii_name="metricDuration")
    def metric_duration(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the Duration of this Lambda How long execution of this Lambda takes.

        Average over 5 minutes

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
        ...

    @jsii.member(jsii_name="metricErrors")
    def metric_errors(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """How many invocations of this Lambda fail.

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

    @jsii.member(jsii_name="metricInvocations")
    def metric_invocations(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of invocations of this Lambda How often this Lambda is invoked.

        Sum over 5 minutes

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
        ...

    @jsii.member(jsii_name="metricThrottles")
    def metric_throttles(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of throttled invocations of this Lambda How often this Lambda is throttled.

        Sum over 5 minutes

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
        ...


class _IFunctionProxy(jsii.proxy_for(aws_cdk.cdk.IResource), jsii.proxy_for(aws_cdk.aws_ec2.IConnectable), jsii.proxy_for(aws_cdk.aws_iam.IGrantable)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-lambda.IFunction"
    @property
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> str:
        """The ARN fo the function.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "functionArn")

    @property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> str:
        """The name of the function.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "functionName")

    @property
    @jsii.member(jsii_name="id")
    def id(self) -> str:
        """Logical ID of this Function.

        Stability:
            experimental
        """
        return jsii.get(self, "id")

    @property
    @jsii.member(jsii_name="isBoundToVpc")
    def is_bound_to_vpc(self) -> bool:
        """Whether or not this Lambda function was bound to a VPC.

        If this is is ``false``, trying to access the ``connections`` object will fail.

        Stability:
            experimental
        """
        return jsii.get(self, "isBoundToVpc")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """The IAM role associated with this function.

        Stability:
            experimental
        """
        return jsii.get(self, "role")

    @jsii.member(jsii_name="addEventSource")
    def add_event_source(self, source: "IEventSource") -> None:
        """
        Arguments:
            source: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addEventSource", [source])

    @jsii.member(jsii_name="addEventSourceMapping")
    def add_event_source_mapping(self, id: str, *, event_source_arn: str, batch_size: typing.Optional[jsii.Number]=None, enabled: typing.Optional[bool]=None, starting_position: typing.Optional["StartingPosition"]=None) -> "EventSourceMapping":
        """Adds an event source that maps to this AWS Lambda function.

        Arguments:
            id: construct ID.
            options: mapping options.
            eventSourceArn: The Amazon Resource Name (ARN) of the event source. Any record added to this stream can invoke the Lambda function.
            batchSize: The largest number of records that AWS Lambda will retrieve from your event source at the time of invoking your function. Your function receives an event with all the retrieved records. Valid Range: Minimum value of 1. Maximum value of 10000. Default: - Amazon Kinesis and Amazon DynamoDB is 100 records. Both the default and maximum for Amazon SQS are 10 messages.
            enabled: Set to false to disable the event source upon creation. Default: true
            startingPosition: The position in the DynamoDB or Kinesis stream where AWS Lambda should start reading. Default: - Required for Amazon Kinesis and Amazon DynamoDB Streams sources.

        Stability:
            experimental
        """
        options: EventSourceMappingOptions = {"eventSourceArn": event_source_arn}

        if batch_size is not None:
            options["batchSize"] = batch_size

        if enabled is not None:
            options["enabled"] = enabled

        if starting_position is not None:
            options["startingPosition"] = starting_position

        return jsii.invoke(self, "addEventSourceMapping", [id, options])

    @jsii.member(jsii_name="addPermission")
    def add_permission(self, id: str, *, principal: aws_cdk.aws_iam.IPrincipal, action: typing.Optional[str]=None, event_source_token: typing.Optional[str]=None, source_account: typing.Optional[str]=None, source_arn: typing.Optional[str]=None) -> None:
        """Adds a permission to the Lambda resource policy.

        Arguments:
            id: The id ƒor the permission construct.
            permission: -
            principal: The entity for which you are granting permission to invoke the Lambda function. This entity can be any valid AWS service principal, such as s3.amazonaws.com or sns.amazonaws.com, or, if you are granting cross-account permission, an AWS account ID. For example, you might want to allow a custom application in another AWS account to push events to Lambda by invoking your function. The principal can be either an AccountPrincipal or a ServicePrincipal.
            action: The Lambda actions that you want to allow in this statement. For example, you can specify lambda:CreateFunction to specify a certain action, or use a wildcard (``lambda:*``) to grant permission to all Lambda actions. For a list of actions, see Actions and Condition Context Keys for AWS Lambda in the IAM User Guide. Default: 'lambda:InvokeFunction'
            eventSourceToken: A unique token that must be supplied by the principal invoking the function. Default: The caller would not need to present a token.
            sourceAccount: The AWS account ID (without hyphens) of the source owner. For example, if you specify an S3 bucket in the SourceArn property, this value is the bucket owner's account ID. You can use this property to ensure that all source principals are owned by a specific account.
            sourceArn: The ARN of a resource that is invoking your function. When granting Amazon Simple Storage Service (Amazon S3) permission to invoke your function, specify this property with the bucket ARN as its value. This ensures that events generated only from the specified bucket, not just any bucket from any AWS account that creates a mapping to your function, can invoke the function.

        Stability:
            experimental
        """
        permission: Permission = {"principal": principal}

        if action is not None:
            permission["action"] = action

        if event_source_token is not None:
            permission["eventSourceToken"] = event_source_token

        if source_account is not None:
            permission["sourceAccount"] = source_account

        if source_arn is not None:
            permission["sourceArn"] = source_arn

        return jsii.invoke(self, "addPermission", [id, permission])

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """
        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToRolePolicy", [statement])

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(self, identity: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant the given identity permissions to invoke this Lambda.

        Arguments:
            identity: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantInvoke", [identity])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Lambda Return the given named metric for this Function.

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

    @jsii.member(jsii_name="metricDuration")
    def metric_duration(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the Duration of this Lambda How long execution of this Lambda takes.

        Average over 5 minutes

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

        return jsii.invoke(self, "metricDuration", [props])

    @jsii.member(jsii_name="metricErrors")
    def metric_errors(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """How many invocations of this Lambda fail.

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

        return jsii.invoke(self, "metricErrors", [props])

    @jsii.member(jsii_name="metricInvocations")
    def metric_invocations(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of invocations of this Lambda How often this Lambda is invoked.

        Sum over 5 minutes

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

        return jsii.invoke(self, "metricInvocations", [props])

    @jsii.member(jsii_name="metricThrottles")
    def metric_throttles(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of throttled invocations of this Lambda How often this Lambda is throttled.

        Sum over 5 minutes

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

        return jsii.invoke(self, "metricThrottles", [props])


@jsii.implements(IFunction)
class FunctionBase(aws_cdk.cdk.Resource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-lambda.FunctionBase"):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _FunctionBaseProxy

    def __init__(self, scope: aws_cdk.cdk.Construct, id: str) -> None:
        """Creates a new construct node.

        Arguments:
            scope: The scope in which to define this construct.
            id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.

        Stability:
            experimental
        """
        jsii.create(FunctionBase, self, [scope, id])

    @jsii.member(jsii_name="addEventSource")
    def add_event_source(self, source: "IEventSource") -> None:
        """Adds an event source to this function.

        Event sources are implemented in the @aws-cdk/aws-lambda-event-sources module.

        The following example adds an SQS Queue as an event source::

            import { SqsEventSource } from '@aws-cdk/aws-lambda-event-sources';
            myFunction.addEventSource(new SqsEventSource(myQueue));

        Arguments:
            source: The event source to bind to this function.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addEventSource", [source])

    @jsii.member(jsii_name="addEventSourceMapping")
    def add_event_source_mapping(self, id: str, *, event_source_arn: str, batch_size: typing.Optional[jsii.Number]=None, enabled: typing.Optional[bool]=None, starting_position: typing.Optional["StartingPosition"]=None) -> "EventSourceMapping":
        """Adds an event source that maps to this AWS Lambda function.

        Arguments:
            id: -
            options: -
            eventSourceArn: The Amazon Resource Name (ARN) of the event source. Any record added to this stream can invoke the Lambda function.
            batchSize: The largest number of records that AWS Lambda will retrieve from your event source at the time of invoking your function. Your function receives an event with all the retrieved records. Valid Range: Minimum value of 1. Maximum value of 10000. Default: - Amazon Kinesis and Amazon DynamoDB is 100 records. Both the default and maximum for Amazon SQS are 10 messages.
            enabled: Set to false to disable the event source upon creation. Default: true
            startingPosition: The position in the DynamoDB or Kinesis stream where AWS Lambda should start reading. Default: - Required for Amazon Kinesis and Amazon DynamoDB Streams sources.

        Stability:
            experimental
        """
        options: EventSourceMappingOptions = {"eventSourceArn": event_source_arn}

        if batch_size is not None:
            options["batchSize"] = batch_size

        if enabled is not None:
            options["enabled"] = enabled

        if starting_position is not None:
            options["startingPosition"] = starting_position

        return jsii.invoke(self, "addEventSourceMapping", [id, options])

    @jsii.member(jsii_name="addPermission")
    def add_permission(self, id: str, *, principal: aws_cdk.aws_iam.IPrincipal, action: typing.Optional[str]=None, event_source_token: typing.Optional[str]=None, source_account: typing.Optional[str]=None, source_arn: typing.Optional[str]=None) -> None:
        """Adds a permission to the Lambda resource policy.

        Arguments:
            id: The id ƒor the permission construct.
            permission: -
            principal: The entity for which you are granting permission to invoke the Lambda function. This entity can be any valid AWS service principal, such as s3.amazonaws.com or sns.amazonaws.com, or, if you are granting cross-account permission, an AWS account ID. For example, you might want to allow a custom application in another AWS account to push events to Lambda by invoking your function. The principal can be either an AccountPrincipal or a ServicePrincipal.
            action: The Lambda actions that you want to allow in this statement. For example, you can specify lambda:CreateFunction to specify a certain action, or use a wildcard (``lambda:*``) to grant permission to all Lambda actions. For a list of actions, see Actions and Condition Context Keys for AWS Lambda in the IAM User Guide. Default: 'lambda:InvokeFunction'
            eventSourceToken: A unique token that must be supplied by the principal invoking the function. Default: The caller would not need to present a token.
            sourceAccount: The AWS account ID (without hyphens) of the source owner. For example, if you specify an S3 bucket in the SourceArn property, this value is the bucket owner's account ID. You can use this property to ensure that all source principals are owned by a specific account.
            sourceArn: The ARN of a resource that is invoking your function. When granting Amazon Simple Storage Service (Amazon S3) permission to invoke your function, specify this property with the bucket ARN as its value. This ensures that events generated only from the specified bucket, not just any bucket from any AWS account that creates a mapping to your function, can invoke the function.

        Stability:
            experimental
        """
        permission: Permission = {"principal": principal}

        if action is not None:
            permission["action"] = action

        if event_source_token is not None:
            permission["eventSourceToken"] = event_source_token

        if source_account is not None:
            permission["sourceAccount"] = source_account

        if source_arn is not None:
            permission["sourceArn"] = source_arn

        return jsii.invoke(self, "addPermission", [id, permission])

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """
        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToRolePolicy", [statement])

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant the given identity permissions to invoke this Lambda.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantInvoke", [grantee])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Function.

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

    @jsii.member(jsii_name="metricDuration")
    def metric_duration(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """How long execution of this Lambda takes.

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

        return jsii.invoke(self, "metricDuration", [props])

    @jsii.member(jsii_name="metricErrors")
    def metric_errors(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """How many invocations of this Lambda fail.

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

        return jsii.invoke(self, "metricErrors", [props])

    @jsii.member(jsii_name="metricInvocations")
    def metric_invocations(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """How often this Lambda is invoked.

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

        return jsii.invoke(self, "metricInvocations", [props])

    @jsii.member(jsii_name="metricThrottles")
    def metric_throttles(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """How often this Lambda is throttled.

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

        return jsii.invoke(self, "metricThrottles", [props])

    @property
    @jsii.member(jsii_name="canCreatePermissions")
    @abc.abstractmethod
    def _can_create_permissions(self) -> bool:
        """Whether the addPermission() call adds any permissions.

        True for new Lambdas, false for imported Lambdas (they might live in different accounts).

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """Access the Connections object.

        Will fail if not a VPC-enabled Lambda Function

        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="functionArn")
    @abc.abstractmethod
    def function_arn(self) -> str:
        """The ARN fo the function.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="functionName")
    @abc.abstractmethod
    def function_name(self) -> str:
        """The name of the function.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="grantPrincipal")
    @abc.abstractmethod
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        """The principal this Lambda Function is running as.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="id")
    def id(self) -> str:
        """Logical ID of this Function.

        Stability:
            experimental
        """
        return jsii.get(self, "id")

    @property
    @jsii.member(jsii_name="isBoundToVpc")
    def is_bound_to_vpc(self) -> bool:
        """Whether or not this Lambda function was bound to a VPC.

        If this is is ``false``, trying to access the ``connections`` object will fail.

        Stability:
            experimental
        """
        return jsii.get(self, "isBoundToVpc")

    @property
    @jsii.member(jsii_name="role")
    @abc.abstractmethod
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """The IAM role associated with this function.

        Undefined if the function was imported without a role.

        Stability:
            experimental
        """
        ...


class _FunctionBaseProxy(FunctionBase, jsii.proxy_for(aws_cdk.cdk.Resource)):
    @property
    @jsii.member(jsii_name="canCreatePermissions")
    def _can_create_permissions(self) -> bool:
        """Whether the addPermission() call adds any permissions.

        True for new Lambdas, false for imported Lambdas (they might live in different accounts).

        Stability:
            experimental
        """
        return jsii.get(self, "canCreatePermissions")

    @property
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> str:
        """The ARN fo the function.

        Stability:
            experimental
        """
        return jsii.get(self, "functionArn")

    @property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> str:
        """The name of the function.

        Stability:
            experimental
        """
        return jsii.get(self, "functionName")

    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        """The principal this Lambda Function is running as.

        Stability:
            experimental
        """
        return jsii.get(self, "grantPrincipal")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """The IAM role associated with this function.

        Undefined if the function was imported without a role.

        Stability:
            experimental
        """
        return jsii.get(self, "role")


class Alias(FunctionBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.Alias"):
    """A new alias to a particular version of a Lambda function.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, alias_name: str, version: "IVersion", additional_versions: typing.Optional[typing.List["VersionWeight"]]=None, description: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            aliasName: Name of this alias.
            version: Function version this alias refers to. Use lambda.addVersion() to obtain a new lambda version to refer to.
            additionalVersions: Additional versions with individual weights this alias points to. Individual additional version weights specified here should add up to (less than) one. All remaining weight is routed to the default version. For example, the config is Example:: version: "1" additionalVersions: [{ version: "2", weight: 0.05 }] Then 5% of traffic will be routed to function version 2, while the remaining 95% of traffic will be routed to function version 1. Default: No additional versions
            description: Description for the alias. Default: No description

        Stability:
            experimental
        """
        props: AliasProps = {"aliasName": alias_name, "version": version}

        if additional_versions is not None:
            props["additionalVersions"] = additional_versions

        if description is not None:
            props["description"] = description

        jsii.create(Alias, self, [scope, id, props])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Function.

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

    @property
    @jsii.member(jsii_name="aliasName")
    def alias_name(self) -> str:
        """Name of this alias.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "aliasName")

    @property
    @jsii.member(jsii_name="canCreatePermissions")
    def _can_create_permissions(self) -> bool:
        """Whether the addPermission() call adds any permissions.

        True for new Lambdas, false for imported Lambdas (they might live in different accounts).

        Stability:
            experimental
        """
        return jsii.get(self, "canCreatePermissions")

    @property
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> str:
        """ARN of this alias.

        Used to be able to use Alias in place of a regular Lambda. Lambda accepts
        ARNs everywhere it accepts function names.

        Stability:
            experimental
        """
        return jsii.get(self, "functionArn")

    @property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> str:
        """ARN of this alias.

        Used to be able to use Alias in place of a regular Lambda. Lambda accepts
        ARNs everywhere it accepts function names.

        Stability:
            experimental
        """
        return jsii.get(self, "functionName")

    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        """The principal this Lambda Function is running as.

        Stability:
            experimental
        """
        return jsii.get(self, "grantPrincipal")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """Role associated with this alias.

        Stability:
            experimental
        """
        return jsii.get(self, "role")


class Function(FunctionBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.Function"):
    """Deploys a file from from inside the construct library as a function.

    The supplied file is subject to the 4096 bytes limit of being embedded in a
    CloudFormation template.

    The construct includes an associated role with the lambda.

    This construct does not yet reproduce all features from the underlying resource
    library.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, code: "Code", handler: str, runtime: "Runtime", allow_all_outbound: typing.Optional[bool]=None, dead_letter_queue: typing.Optional[aws_cdk.aws_sqs.IQueue]=None, dead_letter_queue_enabled: typing.Optional[bool]=None, description: typing.Optional[str]=None, environment: typing.Optional[typing.Mapping[str,typing.Any]]=None, events: typing.Optional[typing.List["IEventSource"]]=None, function_name: typing.Optional[str]=None, initial_policy: typing.Optional[typing.List[aws_cdk.aws_iam.PolicyStatement]]=None, layers: typing.Optional[typing.List["ILayerVersion"]]=None, log_retention_days: typing.Optional[aws_cdk.aws_logs.RetentionDays]=None, memory_size: typing.Optional[jsii.Number]=None, reserved_concurrent_executions: typing.Optional[jsii.Number]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]=None, timeout: typing.Optional[jsii.Number]=None, tracing: typing.Optional["Tracing"]=None, vpc: typing.Optional[aws_cdk.aws_ec2.IVpc]=None, vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            code: The source code of your Lambda function. You can point to a file in an Amazon Simple Storage Service (Amazon S3) bucket or specify your source code as inline text.
            handler: The name of the function (within your source code) that Lambda calls to start running your code. For more information, see the Handler property in the AWS Lambda Developer Guide. NOTE: If you specify your source code as inline text by specifying the ZipFile property within the Code property, specify index.function_name as the handler.
            runtime: The runtime environment for the Lambda function that you are uploading. For valid values, see the Runtime property in the AWS Lambda Developer Guide.
            allowAllOutbound: Whether to allow the Lambda to send all network traffic. If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets. Default: true
            deadLetterQueue: The SQS queue to use if DLQ is enabled. Default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
            deadLetterQueueEnabled: Enabled DLQ. If ``deadLetterQueue`` is undefined, an SQS queue with default options will be defined for your Function. Default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
            description: A description of the function. Default: - No description.
            environment: Key-value pairs that Lambda caches and makes available for your Lambda functions. Use environment variables to apply configuration changes, such as test and production environment configurations, without changing your Lambda function source code. Default: - No environment variables.
            events: Event sources for this function. You can also add event sources using ``addEventSource``. Default: - No event sources.
            functionName: A name for the function. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the function's name. For more information, see Name Type.
            initialPolicy: Initial policy statements to add to the created Lambda Role. You can call ``addToRolePolicy`` to the created lambda to add statements post creation. Default: - No policy statements are added to the created Lambda role.
            layers: A list of layers to add to the function's execution environment. You can configure your Lambda function to pull in additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies that can be used by mulitple functions. Default: - No layers.
            logRetentionDays: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: - Logs never expire.
            memorySize: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 128
            reservedConcurrentExecutions: The maximum of concurrent executions you want to reserve for the function. Default: - No specific limit - account limit.
            role: Lambda execution role. This is the role that will be assumed by the function upon execution. It controls the permissions that the function will have. The Role must be assumable by the 'lambda.amazonaws.com' service principal. Default: - A unique role will be generated for this lambda function. Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
            securityGroup: What security group to associate with the Lambda's network interfaces. Only used if 'vpc' is supplied. Default: - If the function is placed within a VPC and a security group is not specified, a dedicated security group will be created for this function.
            timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: 3
            tracing: Enable AWS X-Ray Tracing for Lambda Function. Default: Tracing.Disabled
            vpc: VPC network to place Lambda network interfaces. Specify this if the Lambda function needs to access resources in a VPC. Default: - Function is not placed within a VPC.
            vpcSubnets: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Note: internet access for Lambdas requires a NAT gateway, so picking Public subnets is not allowed. Default: - Private subnets.

        Stability:
            experimental
        """
        props: FunctionProps = {"code": code, "handler": handler, "runtime": runtime}

        if allow_all_outbound is not None:
            props["allowAllOutbound"] = allow_all_outbound

        if dead_letter_queue is not None:
            props["deadLetterQueue"] = dead_letter_queue

        if dead_letter_queue_enabled is not None:
            props["deadLetterQueueEnabled"] = dead_letter_queue_enabled

        if description is not None:
            props["description"] = description

        if environment is not None:
            props["environment"] = environment

        if events is not None:
            props["events"] = events

        if function_name is not None:
            props["functionName"] = function_name

        if initial_policy is not None:
            props["initialPolicy"] = initial_policy

        if layers is not None:
            props["layers"] = layers

        if log_retention_days is not None:
            props["logRetentionDays"] = log_retention_days

        if memory_size is not None:
            props["memorySize"] = memory_size

        if reserved_concurrent_executions is not None:
            props["reservedConcurrentExecutions"] = reserved_concurrent_executions

        if role is not None:
            props["role"] = role

        if security_group is not None:
            props["securityGroup"] = security_group

        if timeout is not None:
            props["timeout"] = timeout

        if tracing is not None:
            props["tracing"] = tracing

        if vpc is not None:
            props["vpc"] = vpc

        if vpc_subnets is not None:
            props["vpcSubnets"] = vpc_subnets

        jsii.create(Function, self, [scope, id, props])

    @jsii.member(jsii_name="fromFunctionArn")
    @classmethod
    def from_function_arn(cls, scope: aws_cdk.cdk.Construct, id: str, function_arn: str) -> "IFunction":
        """
        Arguments:
            scope: -
            id: -
            functionArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromFunctionArn", [scope, id, function_arn])

    @jsii.member(jsii_name="fromFunctionAttributes")
    @classmethod
    def from_function_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, function_arn: str, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, security_group_id: typing.Optional[str]=None) -> "IFunction":
        """Creates a Lambda function object which represents a function not defined within this stack.

        Lambda.import(this, 'MyImportedFunction', { lambdaArn: new LambdaArn('arn:aws:...') });

        Arguments:
            scope: The parent construct.
            id: The name of the lambda construct.
            attrs: the attributes of the function to import.
            functionArn: The ARN of the Lambda function. Format: arn::lambda:::function:
            role: The IAM execution role associated with this function. If the role is not specified, any role-related operations will no-op.
            securityGroupId: Id of the securityGroup for this Lambda, if in a VPC. This needs to be given in order to support allowing connections to this Lambda.

        Stability:
            experimental
        """
        attrs: FunctionAttributes = {"functionArn": function_arn}

        if role is not None:
            attrs["role"] = role

        if security_group_id is not None:
            attrs["securityGroupId"] = security_group_id

        return jsii.sinvoke(cls, "fromFunctionAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="metricAll")
    @classmethod
    def metric_all(cls, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Lambda.

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

    @jsii.member(jsii_name="metricAllConcurrentExecutions")
    @classmethod
    def metric_all_concurrent_executions(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of concurrent executions across all Lambdas.

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            max over 5 minutes

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

        return jsii.sinvoke(cls, "metricAllConcurrentExecutions", [props])

    @jsii.member(jsii_name="metricAllDuration")
    @classmethod
    def metric_all_duration(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the Duration executing all Lambdas.

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

        return jsii.sinvoke(cls, "metricAllDuration", [props])

    @jsii.member(jsii_name="metricAllErrors")
    @classmethod
    def metric_all_errors(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of Errors executing all Lambdas.

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

        return jsii.sinvoke(cls, "metricAllErrors", [props])

    @jsii.member(jsii_name="metricAllInvocations")
    @classmethod
    def metric_all_invocations(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of invocations of all Lambdas.

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

        return jsii.sinvoke(cls, "metricAllInvocations", [props])

    @jsii.member(jsii_name="metricAllThrottles")
    @classmethod
    def metric_all_throttles(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of throttled invocations of all Lambdas.

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

        return jsii.sinvoke(cls, "metricAllThrottles", [props])

    @jsii.member(jsii_name="metricAllUnreservedConcurrentExecutions")
    @classmethod
    def metric_all_unreserved_concurrent_executions(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of unreserved concurrent executions across all Lambdas.

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            max over 5 minutes

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

        return jsii.sinvoke(cls, "metricAllUnreservedConcurrentExecutions", [props])

    @jsii.member(jsii_name="addEnvironment")
    def add_environment(self, key: str, value: typing.Any) -> "Function":
        """Adds an environment variable to this Lambda function. If this is a ref to a Lambda function, this operation results in a no-op.

        Arguments:
            key: The environment variable key.
            value: The environment variable's value.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addEnvironment", [key, value])

    @jsii.member(jsii_name="addLayer")
    def add_layer(self, layer: "ILayerVersion") -> "Function":
        """Adds a Lambda Layer to this Lambda function.

        Arguments:
            layer: the layer to be added.

        Stability:
            experimental
        throws:
            if there are already 5 layers on this function, or the layer is incompatible with this function's runtime.
        """
        return jsii.invoke(self, "addLayer", [layer])

    @jsii.member(jsii_name="addVersion")
    def add_version(self, name: str, code_sha256: typing.Optional[str]=None, description: typing.Optional[str]=None) -> "Version":
        """Add a new version for this Lambda.

        If you want to deploy through CloudFormation and use aliases, you need to
        add a new version (with a new name) to your Lambda every time you want
        to deploy an update. An alias can then refer to the newly created Version.

        All versions should have distinct names, and you should not delete versions
        as long as your Alias needs to refer to them.

        Arguments:
            name: A unique name for this version.
            codeSha256: The SHA-256 hash of the most recently deployed Lambda source code, or omit to skip validation.
            description: A description for this version.

        Returns:
            A new Version object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addVersion", [name, code_sha256, description])

    @jsii.member(jsii_name="newVersion")
    def new_version(self) -> "Version":
        """Add a new version for this Lambda, always with a different name.

        This is similar to the {@link addVersion} method,
        but useful when deploying this Lambda through CodePipeline with blue/green deployments.
        When using {@link addVersion},
        your Alias will not be updated until you change the name passed to {@link addVersion} in your CDK code.
        When deploying through a Pipeline,
        that might lead to a situation where a change to your Lambda application code will never be activated,
        even though it traveled through the entire Pipeline,
        because the Alias is still pointing to an old Version.
        This method creates a new, unique Version every time the CDK code is executed,
        and so prevents that from happening.

        Stability:
            experimental
        """
        return jsii.invoke(self, "newVersion", [])

    @property
    @jsii.member(jsii_name="canCreatePermissions")
    def _can_create_permissions(self) -> bool:
        """Whether the addPermission() call adds any permissions.

        True for new Lambdas, false for imported Lambdas (they might live in different accounts).

        Stability:
            experimental
        """
        return jsii.get(self, "canCreatePermissions")

    @property
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> str:
        """ARN of this function.

        Stability:
            experimental
        """
        return jsii.get(self, "functionArn")

    @property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> str:
        """Name of this function.

        Stability:
            experimental
        """
        return jsii.get(self, "functionName")

    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        """The principal this Lambda Function is running as.

        Stability:
            experimental
        """
        return jsii.get(self, "grantPrincipal")

    @property
    @jsii.member(jsii_name="handler")
    def handler(self) -> str:
        """The name of the handler configured for this lambda.

        Stability:
            experimental
        """
        return jsii.get(self, "handler")

    @property
    @jsii.member(jsii_name="runtime")
    def runtime(self) -> "Runtime":
        """The runtime configured for this lambda.

        Stability:
            experimental
        """
        return jsii.get(self, "runtime")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """Execution role associated with this function.

        Stability:
            experimental
        """
        return jsii.get(self, "role")


@jsii.interface(jsii_type="@aws-cdk/aws-lambda.ILayerVersion")
class ILayerVersion(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ILayerVersionProxy

    @property
    @jsii.member(jsii_name="layerVersionArn")
    def layer_version_arn(self) -> str:
        """The ARN of the Lambda Layer version that this Layer defines.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="compatibleRuntimes")
    def compatible_runtimes(self) -> typing.Optional[typing.List["Runtime"]]:
        """The runtimes compatible with this Layer.

        Default:
            Runtime.All

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addPermission")
    def add_permission(self, id: str, *, account_id: str, organization_id: typing.Optional[str]=None) -> None:
        """Add permission for this layer version to specific entities.

        Usage within
        the same account where the layer is defined is always allowed and does not
        require calling this method. Note that the principal that creates the
        Lambda function using the layer (for example, a CloudFormation changeset
        execution role) also needs to have the ``lambda:GetLayerVersion``
        permission on the layer version.

        Arguments:
            id: the ID of the grant in the construct tree.
            permission: the identification of the grantee.
            accountId: The AWS Account id of the account that is authorized to use a Lambda Layer Version. The wild-card ``'*'`` can be used to grant access to "any" account (or any account in an organization when ``organizationId`` is specified).
            organizationId: The ID of the AWS Organization to hwich the grant is restricted. Can only be specified if ``accountId`` is ``'*'``

        Stability:
            experimental
        """
        ...


class _ILayerVersionProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-lambda.ILayerVersion"
    @property
    @jsii.member(jsii_name="layerVersionArn")
    def layer_version_arn(self) -> str:
        """The ARN of the Lambda Layer version that this Layer defines.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "layerVersionArn")

    @property
    @jsii.member(jsii_name="compatibleRuntimes")
    def compatible_runtimes(self) -> typing.Optional[typing.List["Runtime"]]:
        """The runtimes compatible with this Layer.

        Default:
            Runtime.All

        Stability:
            experimental
        """
        return jsii.get(self, "compatibleRuntimes")

    @jsii.member(jsii_name="addPermission")
    def add_permission(self, id: str, *, account_id: str, organization_id: typing.Optional[str]=None) -> None:
        """Add permission for this layer version to specific entities.

        Usage within
        the same account where the layer is defined is always allowed and does not
        require calling this method. Note that the principal that creates the
        Lambda function using the layer (for example, a CloudFormation changeset
        execution role) also needs to have the ``lambda:GetLayerVersion``
        permission on the layer version.

        Arguments:
            id: the ID of the grant in the construct tree.
            permission: the identification of the grantee.
            accountId: The AWS Account id of the account that is authorized to use a Lambda Layer Version. The wild-card ``'*'`` can be used to grant access to "any" account (or any account in an organization when ``organizationId`` is specified).
            organizationId: The ID of the AWS Organization to hwich the grant is restricted. Can only be specified if ``accountId`` is ``'*'``

        Stability:
            experimental
        """
        permission: LayerVersionPermission = {"accountId": account_id}

        if organization_id is not None:
            permission["organizationId"] = organization_id

        return jsii.invoke(self, "addPermission", [id, permission])


@jsii.interface(jsii_type="@aws-cdk/aws-lambda.IVersion")
class IVersion(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IVersionProxy

    @property
    @jsii.member(jsii_name="lambda")
    def lambda_(self) -> "IFunction":
        """The underlying AWS Lambda function.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="version")
    def version(self) -> str:
        """The most recently deployed version of this function.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IVersionProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-lambda.IVersion"
    @property
    @jsii.member(jsii_name="lambda")
    def lambda_(self) -> "IFunction":
        """The underlying AWS Lambda function.

        Stability:
            experimental
        """
        return jsii.get(self, "lambda")

    @property
    @jsii.member(jsii_name="version")
    def version(self) -> str:
        """The most recently deployed version of this function.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "version")


class InlineCode(Code, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.InlineCode"):
    """Lambda code from an inline string (limited to 4KiB).

    Stability:
        experimental
    """
    def __init__(self, code: str) -> None:
        """
        Arguments:
            code: -

        Stability:
            experimental
        """
        jsii.create(InlineCode, self, [code])

    @jsii.member(jsii_name="bind")
    def bind(self, construct: aws_cdk.cdk.Construct) -> None:
        """Called when the lambda or layer is initialized to allow this object to bind to the stack, add resources and have fun.

        Arguments:
            construct: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [construct])

    @property
    @jsii.member(jsii_name="isInline")
    def is_inline(self) -> bool:
        """Determines whether this Code is inline code or not.

        Stability:
            experimental
        """
        return jsii.get(self, "isInline")

    @property
    @jsii.member(jsii_name="code")
    def code(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "code")

    @code.setter
    def code(self, value: str):
        return jsii.set(self, "code", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.LambdaRuntimeProps", jsii_struct_bases=[])
class LambdaRuntimeProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    supportsInlineCode: bool
    """Whether the ``ZipFile`` (aka inline code) property can be used with this runtime.

    Default:
        false

    Stability:
        experimental
    """

@jsii.implements(ILayerVersion)
class LayerVersion(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.LayerVersion"):
    """Defines a new Lambda Layer version.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, code: "Code", compatible_runtimes: typing.Optional[typing.List["Runtime"]]=None, description: typing.Optional[str]=None, license: typing.Optional[str]=None, name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            code: The content of this Layer. Using *inline* (per ``code.isInline``) code is not permitted.
            compatibleRuntimes: The runtimes compatible with this Layer. Default: - All runtimes are supported.
            description: The description the this Lambda Layer. Default: - No description.
            license: The SPDX licence identifier or URL to the license file for this layer. Default: - No license information will be recorded.
            name: The name of the layer. Default: - A name will be generated.

        Stability:
            experimental
        """
        props: LayerVersionProps = {"code": code}

        if compatible_runtimes is not None:
            props["compatibleRuntimes"] = compatible_runtimes

        if description is not None:
            props["description"] = description

        if license is not None:
            props["license"] = license

        if name is not None:
            props["name"] = name

        jsii.create(LayerVersion, self, [scope, id, props])

    @jsii.member(jsii_name="fromLayerVersionArn")
    @classmethod
    def from_layer_version_arn(cls, scope: aws_cdk.cdk.Construct, id: str, layer_version_arn: str) -> "ILayerVersion":
        """Imports a layer version by ARN.

        Assumes it is compatible with all Lambda runtimes.

        Arguments:
            scope: -
            id: -
            layerVersionArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromLayerVersionArn", [scope, id, layer_version_arn])

    @jsii.member(jsii_name="fromLayerVersionAttributes")
    @classmethod
    def from_layer_version_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, layer_version_arn: str, compatible_runtimes: typing.Optional[typing.List["Runtime"]]=None) -> "ILayerVersion":
        """Imports a Layer that has been defined externally.

        Arguments:
            scope: the parent Construct that will use the imported layer.
            id: the id of the imported layer in the construct tree.
            attrs: the properties of the imported layer.
            layerVersionArn: The ARN of the LayerVersion.
            compatibleRuntimes: The list of compatible runtimes with this Layer.

        Stability:
            experimental
        """
        attrs: LayerVersionAttributes = {"layerVersionArn": layer_version_arn}

        if compatible_runtimes is not None:
            attrs["compatibleRuntimes"] = compatible_runtimes

        return jsii.sinvoke(cls, "fromLayerVersionAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="addPermission")
    def add_permission(self, id: str, *, account_id: str, organization_id: typing.Optional[str]=None) -> None:
        """Add permission for this layer version to specific entities.

        Usage within
        the same account where the layer is defined is always allowed and does not
        require calling this method. Note that the principal that creates the
        Lambda function using the layer (for example, a CloudFormation changeset
        execution role) also needs to have the ``lambda:GetLayerVersion``
        permission on the layer version.

        Arguments:
            id: -
            permission: -
            accountId: The AWS Account id of the account that is authorized to use a Lambda Layer Version. The wild-card ``'*'`` can be used to grant access to "any" account (or any account in an organization when ``organizationId`` is specified).
            organizationId: The ID of the AWS Organization to hwich the grant is restricted. Can only be specified if ``accountId`` is ``'*'``

        Stability:
            experimental
        """
        permission: LayerVersionPermission = {"accountId": account_id}

        if organization_id is not None:
            permission["organizationId"] = organization_id

        return jsii.invoke(self, "addPermission", [id, permission])

    @property
    @jsii.member(jsii_name="layerVersionArn")
    def layer_version_arn(self) -> str:
        """The ARN of the Lambda Layer version that this Layer defines.

        Stability:
            experimental
        """
        return jsii.get(self, "layerVersionArn")

    @property
    @jsii.member(jsii_name="compatibleRuntimes")
    def compatible_runtimes(self) -> typing.Optional[typing.List["Runtime"]]:
        """The runtimes compatible with this Layer.

        Stability:
            experimental
        """
        return jsii.get(self, "compatibleRuntimes")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _LayerVersionAttributes(jsii.compat.TypedDict, total=False):
    compatibleRuntimes: typing.List["Runtime"]
    """The list of compatible runtimes with this Layer.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.LayerVersionAttributes", jsii_struct_bases=[_LayerVersionAttributes])
class LayerVersionAttributes(_LayerVersionAttributes):
    """Properties necessary to import a LayerVersion.

    Stability:
        experimental
    """
    layerVersionArn: str
    """The ARN of the LayerVersion.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _LayerVersionPermission(jsii.compat.TypedDict, total=False):
    organizationId: str
    """The ID of the AWS Organization to hwich the grant is restricted.

    Can only be specified if ``accountId`` is ``'*'``

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.LayerVersionPermission", jsii_struct_bases=[_LayerVersionPermission])
class LayerVersionPermission(_LayerVersionPermission):
    """Identification of an account (or organization) that is allowed to access a Lambda Layer Version.

    Stability:
        experimental
    """
    accountId: str
    """The AWS Account id of the account that is authorized to use a Lambda Layer Version.

    The wild-card ``'*'`` can be
    used to grant access to "any" account (or any account in an organization when ``organizationId`` is specified).

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _LayerVersionProps(jsii.compat.TypedDict, total=False):
    compatibleRuntimes: typing.List["Runtime"]
    """The runtimes compatible with this Layer.

    Default:
        - All runtimes are supported.

    Stability:
        experimental
    """
    description: str
    """The description the this Lambda Layer.

    Default:
        - No description.

    Stability:
        experimental
    """
    license: str
    """The SPDX licence identifier or URL to the license file for this layer.

    Default:
        - No license information will be recorded.

    Stability:
        experimental
    """
    name: str
    """The name of the layer.

    Default:
        - A name will be generated.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.LayerVersionProps", jsii_struct_bases=[_LayerVersionProps])
class LayerVersionProps(_LayerVersionProps):
    """
    Stability:
        experimental
    """
    code: "Code"
    """The content of this Layer.

    Using *inline* (per ``code.isInline``) code is not permitted.

    Stability:
        experimental
    """

class LogRetention(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.LogRetention"):
    """Creates a custom resource to control the retention policy of a CloudWatch Logs log group.

    The log group is created if it doesn't already exist. The policy
    is removed when ``retentionDays`` is ``undefined`` or equal to ``Infinity``.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, log_group_name: str, retention_days: aws_cdk.aws_logs.RetentionDays) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            logGroupName: The log group name.
            retentionDays: The number of days log events are kept in CloudWatch Logs.

        Stability:
            experimental
        """
        props: LogRetentionProps = {"logGroupName": log_group_name, "retentionDays": retention_days}

        jsii.create(LogRetention, self, [scope, id, props])


@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.LogRetentionProps", jsii_struct_bases=[])
class LogRetentionProps(jsii.compat.TypedDict):
    """Construction properties for a LogRetention.

    Stability:
        experimental
    """
    logGroupName: str
    """The log group name.

    Stability:
        experimental
    """

    retentionDays: aws_cdk.aws_logs.RetentionDays
    """The number of days log events are kept in CloudWatch Logs.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _Permission(jsii.compat.TypedDict, total=False):
    action: str
    """The Lambda actions that you want to allow in this statement.

    For example,
    you can specify lambda:CreateFunction to specify a certain action, or use
    a wildcard (``lambda:*``) to grant permission to all Lambda actions. For a
    list of actions, see Actions and Condition Context Keys for AWS Lambda in
    the IAM User Guide.

    Default:
        'lambda:InvokeFunction'

    Stability:
        experimental
    """
    eventSourceToken: str
    """A unique token that must be supplied by the principal invoking the function.

    Default:
        The caller would not need to present a token.

    Stability:
        experimental
    """
    sourceAccount: str
    """The AWS account ID (without hyphens) of the source owner.

    For example, if
    you specify an S3 bucket in the SourceArn property, this value is the
    bucket owner's account ID. You can use this property to ensure that all
    source principals are owned by a specific account.

    Stability:
        experimental
    """
    sourceArn: str
    """The ARN of a resource that is invoking your function.

    When granting
    Amazon Simple Storage Service (Amazon S3) permission to invoke your
    function, specify this property with the bucket ARN as its value. This
    ensures that events generated only from the specified bucket, not just
    any bucket from any AWS account that creates a mapping to your function,
    can invoke the function.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.Permission", jsii_struct_bases=[_Permission])
class Permission(_Permission):
    """Represents a permission statement that can be added to a Lambda's resource policy via the ``addToResourcePolicy`` method.

    Stability:
        experimental
    """
    principal: aws_cdk.aws_iam.IPrincipal
    """The entity for which you are granting permission to invoke the Lambda function.

    This entity can be any valid AWS service principal, such as
    s3.amazonaws.com or sns.amazonaws.com, or, if you are granting
    cross-account permission, an AWS account ID. For example, you might want
    to allow a custom application in another AWS account to push events to
    Lambda by invoking your function.

    The principal can be either an AccountPrincipal or a ServicePrincipal.

    Stability:
        experimental
    """

class Runtime(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.Runtime"):
    """Lambda function runtime environment.

    If you need to use a runtime name that doesn't exist as a static member, you
    can instantiate a ``Runtime`` object, e.g: ``new Runtime('nodejs99.99')``.

    Stability:
        experimental
    """
    def __init__(self, name: str, family: typing.Optional["RuntimeFamily"]=None, *, supports_inline_code: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            name: -
            family: -
            props: -
            supportsInlineCode: Whether the ``ZipFile`` (aka inline code) property can be used with this runtime. Default: false

        Stability:
            experimental
        """
        props: LambdaRuntimeProps = {}

        if supports_inline_code is not None:
            props["supportsInlineCode"] = supports_inline_code

        jsii.create(Runtime, self, [name, family, props])

    @jsii.member(jsii_name="runtimeEquals")
    def runtime_equals(self, other: "Runtime") -> bool:
        """
        Arguments:
            other: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "runtimeEquals", [other])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @classproperty
    @jsii.member(jsii_name="All")
    def ALL(cls) -> typing.List["Runtime"]:
        """A list of all known ``Runtime``'s.

        Stability:
            experimental
        """
        return jsii.sget(cls, "All")

    @classproperty
    @jsii.member(jsii_name="DotNetCore1")
    def DOT_NET_CORE1(cls) -> "Runtime":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "DotNetCore1")

    @classproperty
    @jsii.member(jsii_name="DotNetCore2")
    def DOT_NET_CORE2(cls) -> "Runtime":
        """
        Deprecated:
            Use ``DotNetCore21``

        Stability:
            deprecated
        """
        return jsii.sget(cls, "DotNetCore2")

    @classproperty
    @jsii.member(jsii_name="DotNetCore21")
    def DOT_NET_CORE21(cls) -> "Runtime":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "DotNetCore21")

    @classproperty
    @jsii.member(jsii_name="Go1x")
    def GO1X(cls) -> "Runtime":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Go1x")

    @classproperty
    @jsii.member(jsii_name="Java8")
    def JAVA8(cls) -> "Runtime":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Java8")

    @classproperty
    @jsii.member(jsii_name="NodeJS")
    def NODE_JS(cls) -> "Runtime":
        """
        Deprecated:
            Use ``NodeJS810`` or ``NodeJS10x``

        Stability:
            deprecated
        """
        return jsii.sget(cls, "NodeJS")

    @classproperty
    @jsii.member(jsii_name="NodeJS10x")
    def NODE_J_S10X(cls) -> "Runtime":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "NodeJS10x")

    @classproperty
    @jsii.member(jsii_name="NodeJS43")
    def NODE_J_S43(cls) -> "Runtime":
        """
        Deprecated:
            Use ``NodeJS810`` or ``NodeJS10x``

        Stability:
            deprecated
        """
        return jsii.sget(cls, "NodeJS43")

    @classproperty
    @jsii.member(jsii_name="NodeJS610")
    def NODE_J_S610(cls) -> "Runtime":
        """
        Deprecated:
            Use ``NodeJS810`` or ``NodeJS10x``

        Stability:
            deprecated
        """
        return jsii.sget(cls, "NodeJS610")

    @classproperty
    @jsii.member(jsii_name="NodeJS810")
    def NODE_J_S810(cls) -> "Runtime":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "NodeJS810")

    @classproperty
    @jsii.member(jsii_name="Provided")
    def PROVIDED(cls) -> "Runtime":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Provided")

    @classproperty
    @jsii.member(jsii_name="Python27")
    def PYTHON27(cls) -> "Runtime":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Python27")

    @classproperty
    @jsii.member(jsii_name="Python36")
    def PYTHON36(cls) -> "Runtime":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Python36")

    @classproperty
    @jsii.member(jsii_name="Python37")
    def PYTHON37(cls) -> "Runtime":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Python37")

    @classproperty
    @jsii.member(jsii_name="Ruby25")
    def RUBY25(cls) -> "Runtime":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Ruby25")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """The name of this runtime, as expected by the Lambda resource.

        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @property
    @jsii.member(jsii_name="supportsInlineCode")
    def supports_inline_code(self) -> bool:
        """Whether the ``ZipFile`` (aka inline code) property can be used with this runtime.

        Stability:
            experimental
        """
        return jsii.get(self, "supportsInlineCode")

    @property
    @jsii.member(jsii_name="family")
    def family(self) -> typing.Optional["RuntimeFamily"]:
        """The runtime family.

        Stability:
            experimental
        """
        return jsii.get(self, "family")


@jsii.enum(jsii_type="@aws-cdk/aws-lambda.RuntimeFamily")
class RuntimeFamily(enum.Enum):
    """
    Stability:
        experimental
    """
    NodeJS = "NodeJS"
    """
    Stability:
        experimental
    """
    Java = "Java"
    """
    Stability:
        experimental
    """
    Python = "Python"
    """
    Stability:
        experimental
    """
    DotNetCore = "DotNetCore"
    """
    Stability:
        experimental
    """
    Go = "Go"
    """
    Stability:
        experimental
    """
    Ruby = "Ruby"
    """
    Stability:
        experimental
    """
    Other = "Other"
    """
    Stability:
        experimental
    """

class S3Code(Code, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.S3Code"):
    """Lambda code from an S3 archive.

    Stability:
        experimental
    """
    def __init__(self, bucket: aws_cdk.aws_s3.IBucket, key: str, object_version: typing.Optional[str]=None) -> None:
        """
        Arguments:
            bucket: -
            key: -
            objectVersion: -

        Stability:
            experimental
        """
        jsii.create(S3Code, self, [bucket, key, object_version])

    @property
    @jsii.member(jsii_name="isInline")
    def is_inline(self) -> bool:
        """Determines whether this Code is inline code or not.

        Stability:
            experimental
        """
        return jsii.get(self, "isInline")

    @property
    @jsii.member(jsii_name="key")
    def key(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "key")

    @key.setter
    def key(self, value: str):
        return jsii.set(self, "key", value)

    @property
    @jsii.member(jsii_name="objectVersion")
    def object_version(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "objectVersion")

    @object_version.setter
    def object_version(self, value: typing.Optional[str]):
        return jsii.set(self, "objectVersion", value)


class SingletonFunction(FunctionBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.SingletonFunction"):
    """A Lambda that will only ever be added to a stack once.

    The lambda is identified using the value of 'uuid'. Run 'uuidgen'
    for every SingletonLambda you create.

    Stability:
        experimental
    resource:
        AWS::Lambda::Function
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, uuid: str, lambda_purpose: typing.Optional[str]=None, code: "Code", handler: str, runtime: "Runtime", allow_all_outbound: typing.Optional[bool]=None, dead_letter_queue: typing.Optional[aws_cdk.aws_sqs.IQueue]=None, dead_letter_queue_enabled: typing.Optional[bool]=None, description: typing.Optional[str]=None, environment: typing.Optional[typing.Mapping[str,typing.Any]]=None, events: typing.Optional[typing.List["IEventSource"]]=None, function_name: typing.Optional[str]=None, initial_policy: typing.Optional[typing.List[aws_cdk.aws_iam.PolicyStatement]]=None, layers: typing.Optional[typing.List["ILayerVersion"]]=None, log_retention_days: typing.Optional[aws_cdk.aws_logs.RetentionDays]=None, memory_size: typing.Optional[jsii.Number]=None, reserved_concurrent_executions: typing.Optional[jsii.Number]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]=None, timeout: typing.Optional[jsii.Number]=None, tracing: typing.Optional["Tracing"]=None, vpc: typing.Optional[aws_cdk.aws_ec2.IVpc]=None, vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            uuid: A unique identifier to identify this lambda. The identifier should be unique across all custom resource providers. We recommend generating a UUID per provider.
            lambdaPurpose: A descriptive name for the purpose of this Lambda. If the Lambda does not have a physical name, this string will be reflected its generated name. The combination of lambdaPurpose and uuid must be unique. Default: SingletonLambda
            code: The source code of your Lambda function. You can point to a file in an Amazon Simple Storage Service (Amazon S3) bucket or specify your source code as inline text.
            handler: The name of the function (within your source code) that Lambda calls to start running your code. For more information, see the Handler property in the AWS Lambda Developer Guide. NOTE: If you specify your source code as inline text by specifying the ZipFile property within the Code property, specify index.function_name as the handler.
            runtime: The runtime environment for the Lambda function that you are uploading. For valid values, see the Runtime property in the AWS Lambda Developer Guide.
            allowAllOutbound: Whether to allow the Lambda to send all network traffic. If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets. Default: true
            deadLetterQueue: The SQS queue to use if DLQ is enabled. Default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
            deadLetterQueueEnabled: Enabled DLQ. If ``deadLetterQueue`` is undefined, an SQS queue with default options will be defined for your Function. Default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
            description: A description of the function. Default: - No description.
            environment: Key-value pairs that Lambda caches and makes available for your Lambda functions. Use environment variables to apply configuration changes, such as test and production environment configurations, without changing your Lambda function source code. Default: - No environment variables.
            events: Event sources for this function. You can also add event sources using ``addEventSource``. Default: - No event sources.
            functionName: A name for the function. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the function's name. For more information, see Name Type.
            initialPolicy: Initial policy statements to add to the created Lambda Role. You can call ``addToRolePolicy`` to the created lambda to add statements post creation. Default: - No policy statements are added to the created Lambda role.
            layers: A list of layers to add to the function's execution environment. You can configure your Lambda function to pull in additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies that can be used by mulitple functions. Default: - No layers.
            logRetentionDays: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: - Logs never expire.
            memorySize: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 128
            reservedConcurrentExecutions: The maximum of concurrent executions you want to reserve for the function. Default: - No specific limit - account limit.
            role: Lambda execution role. This is the role that will be assumed by the function upon execution. It controls the permissions that the function will have. The Role must be assumable by the 'lambda.amazonaws.com' service principal. Default: - A unique role will be generated for this lambda function. Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
            securityGroup: What security group to associate with the Lambda's network interfaces. Only used if 'vpc' is supplied. Default: - If the function is placed within a VPC and a security group is not specified, a dedicated security group will be created for this function.
            timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: 3
            tracing: Enable AWS X-Ray Tracing for Lambda Function. Default: Tracing.Disabled
            vpc: VPC network to place Lambda network interfaces. Specify this if the Lambda function needs to access resources in a VPC. Default: - Function is not placed within a VPC.
            vpcSubnets: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Note: internet access for Lambdas requires a NAT gateway, so picking Public subnets is not allowed. Default: - Private subnets.

        Stability:
            experimental
        """
        props: SingletonFunctionProps = {"uuid": uuid, "code": code, "handler": handler, "runtime": runtime}

        if lambda_purpose is not None:
            props["lambdaPurpose"] = lambda_purpose

        if allow_all_outbound is not None:
            props["allowAllOutbound"] = allow_all_outbound

        if dead_letter_queue is not None:
            props["deadLetterQueue"] = dead_letter_queue

        if dead_letter_queue_enabled is not None:
            props["deadLetterQueueEnabled"] = dead_letter_queue_enabled

        if description is not None:
            props["description"] = description

        if environment is not None:
            props["environment"] = environment

        if events is not None:
            props["events"] = events

        if function_name is not None:
            props["functionName"] = function_name

        if initial_policy is not None:
            props["initialPolicy"] = initial_policy

        if layers is not None:
            props["layers"] = layers

        if log_retention_days is not None:
            props["logRetentionDays"] = log_retention_days

        if memory_size is not None:
            props["memorySize"] = memory_size

        if reserved_concurrent_executions is not None:
            props["reservedConcurrentExecutions"] = reserved_concurrent_executions

        if role is not None:
            props["role"] = role

        if security_group is not None:
            props["securityGroup"] = security_group

        if timeout is not None:
            props["timeout"] = timeout

        if tracing is not None:
            props["tracing"] = tracing

        if vpc is not None:
            props["vpc"] = vpc

        if vpc_subnets is not None:
            props["vpcSubnets"] = vpc_subnets

        jsii.create(SingletonFunction, self, [scope, id, props])

    @jsii.member(jsii_name="addPermission")
    def add_permission(self, name: str, *, principal: aws_cdk.aws_iam.IPrincipal, action: typing.Optional[str]=None, event_source_token: typing.Optional[str]=None, source_account: typing.Optional[str]=None, source_arn: typing.Optional[str]=None) -> None:
        """Adds a permission to the Lambda resource policy.

        Arguments:
            name: -
            permission: -
            principal: The entity for which you are granting permission to invoke the Lambda function. This entity can be any valid AWS service principal, such as s3.amazonaws.com or sns.amazonaws.com, or, if you are granting cross-account permission, an AWS account ID. For example, you might want to allow a custom application in another AWS account to push events to Lambda by invoking your function. The principal can be either an AccountPrincipal or a ServicePrincipal.
            action: The Lambda actions that you want to allow in this statement. For example, you can specify lambda:CreateFunction to specify a certain action, or use a wildcard (``lambda:*``) to grant permission to all Lambda actions. For a list of actions, see Actions and Condition Context Keys for AWS Lambda in the IAM User Guide. Default: 'lambda:InvokeFunction'
            eventSourceToken: A unique token that must be supplied by the principal invoking the function. Default: The caller would not need to present a token.
            sourceAccount: The AWS account ID (without hyphens) of the source owner. For example, if you specify an S3 bucket in the SourceArn property, this value is the bucket owner's account ID. You can use this property to ensure that all source principals are owned by a specific account.
            sourceArn: The ARN of a resource that is invoking your function. When granting Amazon Simple Storage Service (Amazon S3) permission to invoke your function, specify this property with the bucket ARN as its value. This ensures that events generated only from the specified bucket, not just any bucket from any AWS account that creates a mapping to your function, can invoke the function.

        Stability:
            experimental
        """
        permission: Permission = {"principal": principal}

        if action is not None:
            permission["action"] = action

        if event_source_token is not None:
            permission["eventSourceToken"] = event_source_token

        if source_account is not None:
            permission["sourceAccount"] = source_account

        if source_arn is not None:
            permission["sourceArn"] = source_arn

        return jsii.invoke(self, "addPermission", [name, permission])

    @property
    @jsii.member(jsii_name="canCreatePermissions")
    def _can_create_permissions(self) -> bool:
        """Whether the addPermission() call adds any permissions.

        True for new Lambdas, false for imported Lambdas (they might live in different accounts).

        Stability:
            experimental
        """
        return jsii.get(self, "canCreatePermissions")

    @property
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> str:
        """The ARN fo the function.

        Stability:
            experimental
        """
        return jsii.get(self, "functionArn")

    @property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> str:
        """The name of the function.

        Stability:
            experimental
        """
        return jsii.get(self, "functionName")

    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        """The principal this Lambda Function is running as.

        Stability:
            experimental
        """
        return jsii.get(self, "grantPrincipal")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """The IAM role associated with this function.

        Undefined if the function was imported without a role.

        Stability:
            experimental
        """
        return jsii.get(self, "role")


@jsii.data_type_optionals(jsii_struct_bases=[FunctionProps])
class _SingletonFunctionProps(FunctionProps, jsii.compat.TypedDict, total=False):
    lambdaPurpose: str
    """A descriptive name for the purpose of this Lambda.

    If the Lambda does not have a physical name, this string will be
    reflected its generated name. The combination of lambdaPurpose
    and uuid must be unique.

    Default:
        SingletonLambda

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.SingletonFunctionProps", jsii_struct_bases=[_SingletonFunctionProps])
class SingletonFunctionProps(_SingletonFunctionProps):
    """Properties for a newly created singleton Lambda.

    Stability:
        experimental
    """
    uuid: str
    """A unique identifier to identify this lambda.

    The identifier should be unique across all custom resource providers.
    We recommend generating a UUID per provider.

    Stability:
        experimental
    """

@jsii.implements(ILayerVersion)
class SingletonLayerVersion(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.SingletonLayerVersion"):
    """A Singleton Lambda Layer Version.

    The construct gurantees exactly one LayerVersion will be created in a given Stack
    for the provided ``uuid``. It is recommended to use ``uuidgen`` to create a new ``uuid`` each time a new singleton
    layer is created.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, uuid: str, code: "Code", compatible_runtimes: typing.Optional[typing.List["Runtime"]]=None, description: typing.Optional[str]=None, license: typing.Optional[str]=None, name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            uuid: A unique identifier to identify this lambda layer version. The identifier should be unique across all layer providers. We recommend generating a UUID per provider.
            code: The content of this Layer. Using *inline* (per ``code.isInline``) code is not permitted.
            compatibleRuntimes: The runtimes compatible with this Layer. Default: - All runtimes are supported.
            description: The description the this Lambda Layer. Default: - No description.
            license: The SPDX licence identifier or URL to the license file for this layer. Default: - No license information will be recorded.
            name: The name of the layer. Default: - A name will be generated.

        Stability:
            experimental
        """
        props: SingletonLayerVersionProps = {"uuid": uuid, "code": code}

        if compatible_runtimes is not None:
            props["compatibleRuntimes"] = compatible_runtimes

        if description is not None:
            props["description"] = description

        if license is not None:
            props["license"] = license

        if name is not None:
            props["name"] = name

        jsii.create(SingletonLayerVersion, self, [scope, id, props])

    @jsii.member(jsii_name="addPermission")
    def add_permission(self, id: str, *, account_id: str, organization_id: typing.Optional[str]=None) -> None:
        """Add permission for this layer version to specific entities.

        Usage within
        the same account where the layer is defined is always allowed and does not
        require calling this method. Note that the principal that creates the
        Lambda function using the layer (for example, a CloudFormation changeset
        execution role) also needs to have the ``lambda:GetLayerVersion``
        permission on the layer version.

        Arguments:
            id: -
            grantee: -
            accountId: The AWS Account id of the account that is authorized to use a Lambda Layer Version. The wild-card ``'*'`` can be used to grant access to "any" account (or any account in an organization when ``organizationId`` is specified).
            organizationId: The ID of the AWS Organization to hwich the grant is restricted. Can only be specified if ``accountId`` is ``'*'``

        Stability:
            experimental
        """
        grantee: LayerVersionPermission = {"accountId": account_id}

        if organization_id is not None:
            grantee["organizationId"] = organization_id

        return jsii.invoke(self, "addPermission", [id, grantee])

    @property
    @jsii.member(jsii_name="layerVersionArn")
    def layer_version_arn(self) -> str:
        """The ARN of the Lambda Layer version that this Layer defines.

        Stability:
            experimental
        """
        return jsii.get(self, "layerVersionArn")

    @property
    @jsii.member(jsii_name="compatibleRuntimes")
    def compatible_runtimes(self) -> typing.Optional[typing.List["Runtime"]]:
        """The runtimes compatible with this Layer.

        Stability:
            experimental
        """
        return jsii.get(self, "compatibleRuntimes")


@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.SingletonLayerVersionProps", jsii_struct_bases=[LayerVersionProps])
class SingletonLayerVersionProps(LayerVersionProps, jsii.compat.TypedDict):
    """Properties of a Singleton Lambda Layer Version.

    Stability:
        experimental
    """
    uuid: str
    """A unique identifier to identify this lambda layer version.

    The identifier should be unique across all layer providers.
    We recommend generating a UUID per provider.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-lambda.StartingPosition")
class StartingPosition(enum.Enum):
    """The position in the DynamoDB or Kinesis stream where AWS Lambda should start reading.

    Stability:
        experimental
    """
    TrimHorizon = "TrimHorizon"
    """Start reading at the last untrimmed record in the shard in the system, which is the oldest data record in the shard.

    Stability:
        experimental
    """
    Latest = "Latest"
    """Start reading just after the most recent record in the shard, so that you always read the most recent data in the shard.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-lambda.Tracing")
class Tracing(enum.Enum):
    """X-Ray Tracing Modes (https://docs.aws.amazon.com/lambda/latest/dg/API_TracingConfig.html).

    Stability:
        experimental
    """
    Active = "Active"
    """Lambda will respect any tracing header it receives from an upstream service. If no tracing header is received, Lambda will call X-Ray for a tracing decision.

    Stability:
        experimental
    """
    PassThrough = "PassThrough"
    """Lambda will only trace the request from an upstream service if it contains a tracing header with "sampled=1".

    Stability:
        experimental
    """
    Disabled = "Disabled"
    """Lambda will not trace any request.

    Stability:
        experimental
    """

@jsii.implements(IVersion)
class Version(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-lambda.Version"):
    """A single newly-deployed version of a Lambda function.

    This object exists to--at deploy time--query the "then-current" version of
    the Lambda function that it refers to. This Version object can then be
    used in ``Alias`` to refer to a particular deployment of a Lambda.

    This means that for every new update you deploy to your Lambda (using the
    CDK and Aliases), you must always create a new Version object. In
    particular, it must have a different name, so that a new resource is
    created.

    If you want to ensure that you're associating the right version with
    the right deployment, specify the ``codeSha256`` property while
    creating the `Version.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, lambda_: "IFunction", code_sha256: typing.Optional[str]=None, description: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            lambda: Function to get the value of.
            codeSha256: SHA256 of the version of the Lambda source code. Specify to validate that you're deploying the right version. Default: No validation is performed
            description: Description of the version. Default: Description of the Lambda

        Stability:
            experimental
        """
        props: VersionProps = {"lambda": lambda_}

        if code_sha256 is not None:
            props["codeSha256"] = code_sha256

        if description is not None:
            props["description"] = description

        jsii.create(Version, self, [scope, id, props])

    @jsii.member(jsii_name="fromVersionAttributes")
    @classmethod
    def from_version_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, lambda_: "IFunction", version: str) -> "IVersion":
        """
        Arguments:
            scope: -
            id: -
            attrs: -
            lambda: The lambda function.
            version: The version.

        Stability:
            experimental
        """
        attrs: VersionAttributes = {"lambda": lambda_, "version": version}

        return jsii.sinvoke(cls, "fromVersionAttributes", [scope, id, attrs])

    @property
    @jsii.member(jsii_name="lambda")
    def lambda_(self) -> "IFunction":
        """The underlying AWS Lambda function.

        Stability:
            experimental
        """
        return jsii.get(self, "lambda")

    @property
    @jsii.member(jsii_name="version")
    def version(self) -> str:
        """The most recently deployed version of this function.

        Stability:
            experimental
        """
        return jsii.get(self, "version")


@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.VersionAttributes", jsii_struct_bases=[])
class VersionAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    lambda_: "IFunction"
    """The lambda function.

    Stability:
        experimental
    """

    version: str
    """The version.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _VersionProps(jsii.compat.TypedDict, total=False):
    codeSha256: str
    """SHA256 of the version of the Lambda source code.

    Specify to validate that you're deploying the right version.

    Default:
        No validation is performed

    Stability:
        experimental
    """
    description: str
    """Description of the version.

    Default:
        Description of the Lambda

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.VersionProps", jsii_struct_bases=[_VersionProps])
class VersionProps(_VersionProps):
    """Properties for a new Lambda version.

    Stability:
        experimental
    """
    lambda_: "IFunction"
    """Function to get the value of.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-lambda.VersionWeight", jsii_struct_bases=[])
class VersionWeight(jsii.compat.TypedDict):
    """A version/weight pair for routing traffic to Lambda functions.

    Stability:
        experimental
    """
    version: "IVersion"
    """The version to route traffic to.

    Stability:
        experimental
    """

    weight: jsii.Number
    """How much weight to assign to this version (0..1).

    Stability:
        experimental
    """

__all__ = ["Alias", "AliasProps", "AssetCode", "CfnAlias", "CfnAliasProps", "CfnEventSourceMapping", "CfnEventSourceMappingProps", "CfnFunction", "CfnFunctionProps", "CfnLayerVersion", "CfnLayerVersionPermission", "CfnLayerVersionPermissionProps", "CfnLayerVersionProps", "CfnParametersCode", "CfnParametersCodeProps", "CfnPermission", "CfnPermissionProps", "CfnVersion", "CfnVersionProps", "Code", "EventSourceMapping", "EventSourceMappingOptions", "EventSourceMappingProps", "Function", "FunctionAttributes", "FunctionBase", "FunctionProps", "IEventSource", "IFunction", "ILayerVersion", "IVersion", "InlineCode", "LambdaRuntimeProps", "LayerVersion", "LayerVersionAttributes", "LayerVersionPermission", "LayerVersionProps", "LogRetention", "LogRetentionProps", "Permission", "Runtime", "RuntimeFamily", "S3Code", "SingletonFunction", "SingletonFunctionProps", "SingletonLayerVersion", "SingletonLayerVersionProps", "StartingPosition", "Tracing", "Version", "VersionAttributes", "VersionProps", "VersionWeight", "__jsii_assembly__"]

publication.publish()
