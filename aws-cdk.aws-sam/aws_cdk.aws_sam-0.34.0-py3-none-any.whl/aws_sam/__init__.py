import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-sam", "0.34.0", __name__, "aws-sam@0.34.0.jsii.tgz")
class CfnApi(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sam.CfnApi"):
    """A CloudFormation ``AWS::Serverless::Api``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    cloudformationResource:
        AWS::Serverless::Api
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, stage_name: str, auth: typing.Optional[typing.Union[typing.Optional["AuthProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None, binary_media_types: typing.Optional[typing.List[str]]=None, cache_cluster_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, cache_cluster_size: typing.Optional[str]=None, cors: typing.Optional[str]=None, definition_body: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, definition_uri: typing.Optional[typing.Union[typing.Optional[str], typing.Optional[aws_cdk.cdk.Token], typing.Optional["S3LocationProperty"]]]=None, endpoint_configuration: typing.Optional[str]=None, method_settings: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, name: typing.Optional[str]=None, tracing_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, variables: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.Mapping[str,str]]]]=None) -> None:
        """Create a new ``AWS::Serverless::Api``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            stageName: ``AWS::Serverless::Api.StageName``.
            auth: ``AWS::Serverless::Api.Auth``.
            binaryMediaTypes: ``AWS::Serverless::Api.BinaryMediaTypes``.
            cacheClusterEnabled: ``AWS::Serverless::Api.CacheClusterEnabled``.
            cacheClusterSize: ``AWS::Serverless::Api.CacheClusterSize``.
            cors: ``AWS::Serverless::Api.Cors``.
            definitionBody: ``AWS::Serverless::Api.DefinitionBody``.
            definitionUri: ``AWS::Serverless::Api.DefinitionUri``.
            endpointConfiguration: ``AWS::Serverless::Api.EndpointConfiguration``.
            methodSettings: ``AWS::Serverless::Api.MethodSettings``.
            name: ``AWS::Serverless::Api.Name``.
            tracingEnabled: ``AWS::Serverless::Api.TracingEnabled``.
            variables: ``AWS::Serverless::Api.Variables``.

        Stability:
            experimental
        """
        props: CfnApiProps = {"stageName": stage_name}

        if auth is not None:
            props["auth"] = auth

        if binary_media_types is not None:
            props["binaryMediaTypes"] = binary_media_types

        if cache_cluster_enabled is not None:
            props["cacheClusterEnabled"] = cache_cluster_enabled

        if cache_cluster_size is not None:
            props["cacheClusterSize"] = cache_cluster_size

        if cors is not None:
            props["cors"] = cors

        if definition_body is not None:
            props["definitionBody"] = definition_body

        if definition_uri is not None:
            props["definitionUri"] = definition_uri

        if endpoint_configuration is not None:
            props["endpointConfiguration"] = endpoint_configuration

        if method_settings is not None:
            props["methodSettings"] = method_settings

        if name is not None:
            props["name"] = name

        if tracing_enabled is not None:
            props["tracingEnabled"] = tracing_enabled

        if variables is not None:
            props["variables"] = variables

        jsii.create(CfnApi, self, [scope, id, props])

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
    @jsii.member(jsii_name="requiredTransform")
    def REQUIRED_TRANSFORM(cls) -> str:
        """The ``Transform`` a template must use in order to use this resource.

        Stability:
            experimental
        """
        return jsii.sget(cls, "requiredTransform")

    @classproperty
    @jsii.member(jsii_name="resourceTypeName")
    def RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "resourceTypeName")

    @property
    @jsii.member(jsii_name="apiName")
    def api_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "apiName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnApiProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnApi.AuthProperty", jsii_struct_bases=[])
    class AuthProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api-auth-object
        Stability:
            experimental
        """
        authorizers: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnApi.AuthProperty.Authorizers``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api-auth-object
        Stability:
            experimental
        """

        defaultAuthorizer: str
        """``CfnApi.AuthProperty.DefaultAuthorizer``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api-auth-object
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnApi.S3LocationProperty", jsii_struct_bases=[])
    class S3LocationProperty(jsii.compat.TypedDict):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#s3-location-object
        Stability:
            experimental
        """
        bucket: str
        """``CfnApi.S3LocationProperty.Bucket``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        Stability:
            experimental
        """

        key: str
        """``CfnApi.S3LocationProperty.Key``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        Stability:
            experimental
        """

        version: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnApi.S3LocationProperty.Version``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnApiProps(jsii.compat.TypedDict, total=False):
    auth: typing.Union["CfnApi.AuthProperty", aws_cdk.cdk.Token]
    """``AWS::Serverless::Api.Auth``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """
    binaryMediaTypes: typing.List[str]
    """``AWS::Serverless::Api.BinaryMediaTypes``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """
    cacheClusterEnabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::Serverless::Api.CacheClusterEnabled``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """
    cacheClusterSize: str
    """``AWS::Serverless::Api.CacheClusterSize``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """
    cors: str
    """``AWS::Serverless::Api.Cors``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """
    definitionBody: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::Serverless::Api.DefinitionBody``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """
    definitionUri: typing.Union[str, aws_cdk.cdk.Token, "CfnApi.S3LocationProperty"]
    """``AWS::Serverless::Api.DefinitionUri``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """
    endpointConfiguration: str
    """``AWS::Serverless::Api.EndpointConfiguration``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """
    methodSettings: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::Serverless::Api.MethodSettings``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """
    name: str
    """``AWS::Serverless::Api.Name``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """
    tracingEnabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::Serverless::Api.TracingEnabled``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """
    variables: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
    """``AWS::Serverless::Api.Variables``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnApiProps", jsii_struct_bases=[_CfnApiProps])
class CfnApiProps(_CfnApiProps):
    """Properties for defining a ``AWS::Serverless::Api``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """
    stageName: str
    """``AWS::Serverless::Api.StageName``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapi
    Stability:
        experimental
    """

class CfnApplication(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sam.CfnApplication"):
    """A CloudFormation ``AWS::Serverless::Application``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
    Stability:
        experimental
    cloudformationResource:
        AWS::Serverless::Application
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, location: typing.Union[str, aws_cdk.cdk.Token, "ApplicationLocationProperty"], notification_arns: typing.Optional[typing.List[str]]=None, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.Mapping[str,str]]]]=None, tags: typing.Optional[typing.Mapping[str,str]]=None, timeout_in_minutes: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::Serverless::Application``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            location: ``AWS::Serverless::Application.Location``.
            notificationArns: ``AWS::Serverless::Application.NotificationArns``.
            parameters: ``AWS::Serverless::Application.Parameters``.
            tags: ``AWS::Serverless::Application.Tags``.
            timeoutInMinutes: ``AWS::Serverless::Application.TimeoutInMinutes``.

        Stability:
            experimental
        """
        props: CfnApplicationProps = {"location": location}

        if notification_arns is not None:
            props["notificationArns"] = notification_arns

        if parameters is not None:
            props["parameters"] = parameters

        if tags is not None:
            props["tags"] = tags

        if timeout_in_minutes is not None:
            props["timeoutInMinutes"] = timeout_in_minutes

        jsii.create(CfnApplication, self, [scope, id, props])

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
    @jsii.member(jsii_name="requiredTransform")
    def REQUIRED_TRANSFORM(cls) -> str:
        """The ``Transform`` a template must use in order to use this resource.

        Stability:
            experimental
        """
        return jsii.sget(cls, "requiredTransform")

    @classproperty
    @jsii.member(jsii_name="resourceTypeName")
    def RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "resourceTypeName")

    @property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "applicationName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnApplicationProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnApplication.ApplicationLocationProperty", jsii_struct_bases=[])
    class ApplicationLocationProperty(jsii.compat.TypedDict):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        Stability:
            experimental
        """
        applicationId: str
        """``CfnApplication.ApplicationLocationProperty.ApplicationId``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        Stability:
            experimental
        """

        semanticVersion: str
        """``CfnApplication.ApplicationLocationProperty.SemanticVersion``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnApplicationProps(jsii.compat.TypedDict, total=False):
    notificationArns: typing.List[str]
    """``AWS::Serverless::Application.NotificationArns``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
    Stability:
        experimental
    """
    parameters: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
    """``AWS::Serverless::Application.Parameters``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
    Stability:
        experimental
    """
    tags: typing.Mapping[str,str]
    """``AWS::Serverless::Application.Tags``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
    Stability:
        experimental
    """
    timeoutInMinutes: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Serverless::Application.TimeoutInMinutes``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnApplicationProps", jsii_struct_bases=[_CfnApplicationProps])
class CfnApplicationProps(_CfnApplicationProps):
    """Properties for defining a ``AWS::Serverless::Application``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
    Stability:
        experimental
    """
    location: typing.Union[str, aws_cdk.cdk.Token, "CfnApplication.ApplicationLocationProperty"]
    """``AWS::Serverless::Application.Location``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessapplication
    Stability:
        experimental
    """

class CfnFunction(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sam.CfnFunction"):
    """A CloudFormation ``AWS::Serverless::Function``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    cloudformationResource:
        AWS::Serverless::Function
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, code_uri: typing.Union[str, aws_cdk.cdk.Token, "S3LocationProperty"], handler: str, runtime: str, auto_publish_alias: typing.Optional[str]=None, dead_letter_queue: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["DeadLetterQueueProperty"]]]=None, deployment_preference: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["DeploymentPreferenceProperty"]]]=None, description: typing.Optional[str]=None, environment: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["FunctionEnvironmentProperty"]]]=None, events: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.Mapping[str,typing.Union[aws_cdk.cdk.Token, "EventSourceProperty"]]]]]=None, function_name: typing.Optional[str]=None, kms_key_arn: typing.Optional[str]=None, layers: typing.Optional[typing.List[str]]=None, memory_size: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, permissions_boundary: typing.Optional[str]=None, policies: typing.Optional[typing.Union[typing.Optional[str], typing.Optional[aws_cdk.cdk.Token], typing.Optional["IAMPolicyDocumentProperty"], typing.Optional[typing.List[typing.Union[str, aws_cdk.cdk.Token, "IAMPolicyDocumentProperty"]]]]]=None, reserved_concurrent_executions: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, role: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[str,str]]=None, timeout: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, tracing: typing.Optional[str]=None, vpc_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["VpcConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::Serverless::Function``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            codeUri: ``AWS::Serverless::Function.CodeUri``.
            handler: ``AWS::Serverless::Function.Handler``.
            runtime: ``AWS::Serverless::Function.Runtime``.
            autoPublishAlias: ``AWS::Serverless::Function.AutoPublishAlias``.
            deadLetterQueue: ``AWS::Serverless::Function.DeadLetterQueue``.
            deploymentPreference: ``AWS::Serverless::Function.DeploymentPreference``.
            description: ``AWS::Serverless::Function.Description``.
            environment: ``AWS::Serverless::Function.Environment``.
            events: ``AWS::Serverless::Function.Events``.
            functionName: ``AWS::Serverless::Function.FunctionName``.
            kmsKeyArn: ``AWS::Serverless::Function.KmsKeyArn``.
            layers: ``AWS::Serverless::Function.Layers``.
            memorySize: ``AWS::Serverless::Function.MemorySize``.
            permissionsBoundary: ``AWS::Serverless::Function.PermissionsBoundary``.
            policies: ``AWS::Serverless::Function.Policies``.
            reservedConcurrentExecutions: ``AWS::Serverless::Function.ReservedConcurrentExecutions``.
            role: ``AWS::Serverless::Function.Role``.
            tags: ``AWS::Serverless::Function.Tags``.
            timeout: ``AWS::Serverless::Function.Timeout``.
            tracing: ``AWS::Serverless::Function.Tracing``.
            vpcConfig: ``AWS::Serverless::Function.VpcConfig``.

        Stability:
            experimental
        """
        props: CfnFunctionProps = {"codeUri": code_uri, "handler": handler, "runtime": runtime}

        if auto_publish_alias is not None:
            props["autoPublishAlias"] = auto_publish_alias

        if dead_letter_queue is not None:
            props["deadLetterQueue"] = dead_letter_queue

        if deployment_preference is not None:
            props["deploymentPreference"] = deployment_preference

        if description is not None:
            props["description"] = description

        if environment is not None:
            props["environment"] = environment

        if events is not None:
            props["events"] = events

        if function_name is not None:
            props["functionName"] = function_name

        if kms_key_arn is not None:
            props["kmsKeyArn"] = kms_key_arn

        if layers is not None:
            props["layers"] = layers

        if memory_size is not None:
            props["memorySize"] = memory_size

        if permissions_boundary is not None:
            props["permissionsBoundary"] = permissions_boundary

        if policies is not None:
            props["policies"] = policies

        if reserved_concurrent_executions is not None:
            props["reservedConcurrentExecutions"] = reserved_concurrent_executions

        if role is not None:
            props["role"] = role

        if tags is not None:
            props["tags"] = tags

        if timeout is not None:
            props["timeout"] = timeout

        if tracing is not None:
            props["tracing"] = tracing

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
    @jsii.member(jsii_name="requiredTransform")
    def REQUIRED_TRANSFORM(cls) -> str:
        """The ``Transform`` a template must use in order to use this resource.

        Stability:
            experimental
        """
        return jsii.sget(cls, "requiredTransform")

    @classproperty
    @jsii.member(jsii_name="resourceTypeName")
    def RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "resourceTypeName")

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

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.AlexaSkillEventProperty", jsii_struct_bases=[])
    class AlexaSkillEventProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#alexaskill
        Stability:
            experimental
        """
        variables: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnFunction.AlexaSkillEventProperty.Variables``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#alexaskill
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ApiEventProperty(jsii.compat.TypedDict, total=False):
        restApiId: str
        """``CfnFunction.ApiEventProperty.RestApiId``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.ApiEventProperty", jsii_struct_bases=[_ApiEventProperty])
    class ApiEventProperty(_ApiEventProperty):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api
        Stability:
            experimental
        """
        method: str
        """``CfnFunction.ApiEventProperty.Method``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api
        Stability:
            experimental
        """

        path: str
        """``CfnFunction.ApiEventProperty.Path``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CloudWatchEventEventProperty(jsii.compat.TypedDict, total=False):
        input: str
        """``CfnFunction.CloudWatchEventEventProperty.Input``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#cloudwatchevent
        Stability:
            experimental
        """
        inputPath: str
        """``CfnFunction.CloudWatchEventEventProperty.InputPath``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#cloudwatchevent
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.CloudWatchEventEventProperty", jsii_struct_bases=[_CloudWatchEventEventProperty])
    class CloudWatchEventEventProperty(_CloudWatchEventEventProperty):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#cloudwatchevent
        Stability:
            experimental
        """
        pattern: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnFunction.CloudWatchEventEventProperty.Pattern``.

        See:
            http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/CloudWatchEventsandEventPatterns.html
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.DeadLetterQueueProperty", jsii_struct_bases=[])
    class DeadLetterQueueProperty(jsii.compat.TypedDict):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deadletterqueue-object
        Stability:
            experimental
        """
        targetArn: str
        """``CfnFunction.DeadLetterQueueProperty.TargetArn``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        Stability:
            experimental
        """

        type: str
        """``CfnFunction.DeadLetterQueueProperty.Type``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DeploymentPreferenceProperty(jsii.compat.TypedDict, total=False):
        alarms: typing.List[str]
        """``CfnFunction.DeploymentPreferenceProperty.Alarms``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deploymentpreference-object
        Stability:
            experimental
        """
        hooks: typing.List[str]
        """``CfnFunction.DeploymentPreferenceProperty.Hooks``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deploymentpreference-object
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.DeploymentPreferenceProperty", jsii_struct_bases=[_DeploymentPreferenceProperty])
    class DeploymentPreferenceProperty(_DeploymentPreferenceProperty):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/docs/safe_lambda_deployments.rst
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnFunction.DeploymentPreferenceProperty.Enabled``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deploymentpreference-object
        Stability:
            experimental
        """

        type: str
        """``CfnFunction.DeploymentPreferenceProperty.Type``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deploymentpreference-object
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DynamoDBEventProperty(jsii.compat.TypedDict, total=False):
        batchSize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFunction.DynamoDBEventProperty.BatchSize``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#dynamodb
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnFunction.DynamoDBEventProperty.Enabled``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#dynamodb
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.DynamoDBEventProperty", jsii_struct_bases=[_DynamoDBEventProperty])
    class DynamoDBEventProperty(_DynamoDBEventProperty):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#dynamodb
        Stability:
            experimental
        """
        startingPosition: str
        """``CfnFunction.DynamoDBEventProperty.StartingPosition``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#dynamodb
        Stability:
            experimental
        """

        stream: str
        """``CfnFunction.DynamoDBEventProperty.Stream``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#dynamodb
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.EventSourceProperty", jsii_struct_bases=[])
    class EventSourceProperty(jsii.compat.TypedDict):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#event-source-object
        Stability:
            experimental
        """
        properties: typing.Union[aws_cdk.cdk.Token, "CfnFunction.AlexaSkillEventProperty", "CfnFunction.ApiEventProperty", "CfnFunction.CloudWatchEventEventProperty", "CfnFunction.DynamoDBEventProperty", "CfnFunction.S3EventProperty", "CfnFunction.SNSEventProperty", "CfnFunction.SQSEventProperty", "CfnFunction.KinesisEventProperty", "CfnFunction.ScheduleEventProperty", "CfnFunction.IoTRuleEventProperty"]
        """``CfnFunction.EventSourceProperty.Properties``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#event-source-types
        Stability:
            experimental
        """

        type: str
        """``CfnFunction.EventSourceProperty.Type``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#event-source-object
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.FunctionEnvironmentProperty", jsii_struct_bases=[])
    class FunctionEnvironmentProperty(jsii.compat.TypedDict):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#environment-object
        Stability:
            experimental
        """
        variables: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnFunction.FunctionEnvironmentProperty.Variables``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#environment-object
        Stability:
            experimental
        """

    @jsii.interface(jsii_type="@aws-cdk/aws-sam.CfnFunction.IAMPolicyDocumentProperty")
    class IAMPolicyDocumentProperty(jsii.compat.Protocol):
        """
        See:
            http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html
        Stability:
            experimental
        """
        @staticmethod
        def __jsii_proxy_class__():
            return _IAMPolicyDocumentPropertyProxy

        @property
        @jsii.member(jsii_name="statement")
        def statement(self) -> typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]:
            """``CfnFunction.IAMPolicyDocumentProperty.Statement``.

            See:
                http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html
            Stability:
                experimental
            """
            ...


    class _IAMPolicyDocumentPropertyProxy():
        """
        See:
            http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html
        Stability:
            experimental
        """
        __jsii_type__ = "@aws-cdk/aws-sam.CfnFunction.IAMPolicyDocumentProperty"
        @property
        @jsii.member(jsii_name="statement")
        def statement(self) -> typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]:
            """``CfnFunction.IAMPolicyDocumentProperty.Statement``.

            See:
                http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html
            Stability:
                experimental
            """
            return jsii.get(self, "statement")


    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _IoTRuleEventProperty(jsii.compat.TypedDict, total=False):
        awsIotSqlVersion: str
        """``CfnFunction.IoTRuleEventProperty.AwsIotSqlVersion``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#iotrule
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.IoTRuleEventProperty", jsii_struct_bases=[_IoTRuleEventProperty])
    class IoTRuleEventProperty(_IoTRuleEventProperty):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#iotrule
        Stability:
            experimental
        """
        sql: str
        """``CfnFunction.IoTRuleEventProperty.Sql``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#iotrule
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _KinesisEventProperty(jsii.compat.TypedDict, total=False):
        batchSize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFunction.KinesisEventProperty.BatchSize``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#kinesis
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnFunction.KinesisEventProperty.Enabled``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#kinesis
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.KinesisEventProperty", jsii_struct_bases=[_KinesisEventProperty])
    class KinesisEventProperty(_KinesisEventProperty):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#kinesis
        Stability:
            experimental
        """
        startingPosition: str
        """``CfnFunction.KinesisEventProperty.StartingPosition``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#kinesis
        Stability:
            experimental
        """

        stream: str
        """``CfnFunction.KinesisEventProperty.Stream``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#kinesis
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _S3EventProperty(jsii.compat.TypedDict, total=False):
        filter: typing.Union[aws_cdk.cdk.Token, "CfnFunction.S3NotificationFilterProperty"]
        """``CfnFunction.S3EventProperty.Filter``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#s3
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.S3EventProperty", jsii_struct_bases=[_S3EventProperty])
    class S3EventProperty(_S3EventProperty):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#s3
        Stability:
            experimental
        """
        bucket: str
        """``CfnFunction.S3EventProperty.Bucket``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#s3
        Stability:
            experimental
        """

        events: typing.Union[str, aws_cdk.cdk.Token, typing.List[str]]
        """``CfnFunction.S3EventProperty.Events``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#s3
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _S3LocationProperty(jsii.compat.TypedDict, total=False):
        version: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFunction.S3LocationProperty.Version``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.S3LocationProperty", jsii_struct_bases=[_S3LocationProperty])
    class S3LocationProperty(_S3LocationProperty):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#s3-location-object
        Stability:
            experimental
        """
        bucket: str
        """``CfnFunction.S3LocationProperty.Bucket``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        Stability:
            experimental
        """

        key: str
        """``CfnFunction.S3LocationProperty.Key``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.S3NotificationFilterProperty", jsii_struct_bases=[])
    class S3NotificationFilterProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfiguration-config-filter.html
        Stability:
            experimental
        """
        s3Key: str
        """``CfnFunction.S3NotificationFilterProperty.S3Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-notificationconfiguration-config-filter.html
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.SNSEventProperty", jsii_struct_bases=[])
    class SNSEventProperty(jsii.compat.TypedDict):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#sns
        Stability:
            experimental
        """
        topic: str
        """``CfnFunction.SNSEventProperty.Topic``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#sns
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SQSEventProperty(jsii.compat.TypedDict, total=False):
        batchSize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFunction.SQSEventProperty.BatchSize``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#sqs
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnFunction.SQSEventProperty.Enabled``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#sqs
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.SQSEventProperty", jsii_struct_bases=[_SQSEventProperty])
    class SQSEventProperty(_SQSEventProperty):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#sqs
        Stability:
            experimental
        """
        queue: str
        """``CfnFunction.SQSEventProperty.Queue``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#sqs
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ScheduleEventProperty(jsii.compat.TypedDict, total=False):
        input: str
        """``CfnFunction.ScheduleEventProperty.Input``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#schedule
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.ScheduleEventProperty", jsii_struct_bases=[_ScheduleEventProperty])
    class ScheduleEventProperty(_ScheduleEventProperty):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#schedule
        Stability:
            experimental
        """
        schedule: str
        """``CfnFunction.ScheduleEventProperty.Schedule``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#schedule
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunction.VpcConfigProperty", jsii_struct_bases=[])
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
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-vpcconfig.html
        Stability:
            experimental
        """

        subnetIds: typing.List[str]
        """``CfnFunction.VpcConfigProperty.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-vpcconfig.html
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnFunctionProps(jsii.compat.TypedDict, total=False):
    autoPublishAlias: str
    """``AWS::Serverless::Function.AutoPublishAlias``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    deadLetterQueue: typing.Union[aws_cdk.cdk.Token, "CfnFunction.DeadLetterQueueProperty"]
    """``AWS::Serverless::Function.DeadLetterQueue``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    deploymentPreference: typing.Union[aws_cdk.cdk.Token, "CfnFunction.DeploymentPreferenceProperty"]
    """``AWS::Serverless::Function.DeploymentPreference``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#deploymentpreference-object
    Stability:
        experimental
    """
    description: str
    """``AWS::Serverless::Function.Description``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    environment: typing.Union[aws_cdk.cdk.Token, "CfnFunction.FunctionEnvironmentProperty"]
    """``AWS::Serverless::Function.Environment``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    events: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,typing.Union[aws_cdk.cdk.Token, "CfnFunction.EventSourceProperty"]]]
    """``AWS::Serverless::Function.Events``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    functionName: str
    """``AWS::Serverless::Function.FunctionName``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    kmsKeyArn: str
    """``AWS::Serverless::Function.KmsKeyArn``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    layers: typing.List[str]
    """``AWS::Serverless::Function.Layers``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    memorySize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Serverless::Function.MemorySize``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    permissionsBoundary: str
    """``AWS::Serverless::Function.PermissionsBoundary``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    policies: typing.Union[str, aws_cdk.cdk.Token, "CfnFunction.IAMPolicyDocumentProperty", typing.List[typing.Union[str, aws_cdk.cdk.Token, "CfnFunction.IAMPolicyDocumentProperty"]]]
    """``AWS::Serverless::Function.Policies``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    reservedConcurrentExecutions: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Serverless::Function.ReservedConcurrentExecutions``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    role: str
    """``AWS::Serverless::Function.Role``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    tags: typing.Mapping[str,str]
    """``AWS::Serverless::Function.Tags``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    timeout: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Serverless::Function.Timeout``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    tracing: str
    """``AWS::Serverless::Function.Tracing``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    vpcConfig: typing.Union[aws_cdk.cdk.Token, "CfnFunction.VpcConfigProperty"]
    """``AWS::Serverless::Function.VpcConfig``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnFunctionProps", jsii_struct_bases=[_CfnFunctionProps])
class CfnFunctionProps(_CfnFunctionProps):
    """Properties for defining a ``AWS::Serverless::Function``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """
    codeUri: typing.Union[str, aws_cdk.cdk.Token, "CfnFunction.S3LocationProperty"]
    """``AWS::Serverless::Function.CodeUri``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """

    handler: str
    """``AWS::Serverless::Function.Handler``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """

    runtime: str
    """``AWS::Serverless::Function.Runtime``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    Stability:
        experimental
    """

class CfnLayerVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sam.CfnLayerVersion"):
    """A CloudFormation ``AWS::Serverless::LayerVersion``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
    Stability:
        experimental
    cloudformationResource:
        AWS::Serverless::LayerVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, compatible_runtimes: typing.Optional[typing.List[str]]=None, content_uri: typing.Optional[str]=None, description: typing.Optional[str]=None, layer_name: typing.Optional[str]=None, license_info: typing.Optional[str]=None, retention_policy: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Serverless::LayerVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            compatibleRuntimes: ``AWS::Serverless::LayerVersion.CompatibleRuntimes``.
            contentUri: ``AWS::Serverless::LayerVersion.ContentUri``.
            description: ``AWS::Serverless::LayerVersion.Description``.
            layerName: ``AWS::Serverless::LayerVersion.LayerName``.
            licenseInfo: ``AWS::Serverless::LayerVersion.LicenseInfo``.
            retentionPolicy: ``AWS::Serverless::LayerVersion.RetentionPolicy``.

        Stability:
            experimental
        """
        props: CfnLayerVersionProps = {}

        if compatible_runtimes is not None:
            props["compatibleRuntimes"] = compatible_runtimes

        if content_uri is not None:
            props["contentUri"] = content_uri

        if description is not None:
            props["description"] = description

        if layer_name is not None:
            props["layerName"] = layer_name

        if license_info is not None:
            props["licenseInfo"] = license_info

        if retention_policy is not None:
            props["retentionPolicy"] = retention_policy

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
    @jsii.member(jsii_name="requiredTransform")
    def REQUIRED_TRANSFORM(cls) -> str:
        """The ``Transform`` a template must use in order to use this resource.

        Stability:
            experimental
        """
        return jsii.sget(cls, "requiredTransform")

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


@jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnLayerVersionProps", jsii_struct_bases=[])
class CfnLayerVersionProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::Serverless::LayerVersion``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
    Stability:
        experimental
    """
    compatibleRuntimes: typing.List[str]
    """``AWS::Serverless::LayerVersion.CompatibleRuntimes``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
    Stability:
        experimental
    """

    contentUri: str
    """``AWS::Serverless::LayerVersion.ContentUri``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
    Stability:
        experimental
    """

    description: str
    """``AWS::Serverless::LayerVersion.Description``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
    Stability:
        experimental
    """

    layerName: str
    """``AWS::Serverless::LayerVersion.LayerName``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
    Stability:
        experimental
    """

    licenseInfo: str
    """``AWS::Serverless::LayerVersion.LicenseInfo``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
    Stability:
        experimental
    """

    retentionPolicy: str
    """``AWS::Serverless::LayerVersion.RetentionPolicy``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesslayerversion
    Stability:
        experimental
    """

class CfnSimpleTable(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sam.CfnSimpleTable"):
    """A CloudFormation ``AWS::Serverless::SimpleTable``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
    Stability:
        experimental
    cloudformationResource:
        AWS::Serverless::SimpleTable
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, primary_key: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["PrimaryKeyProperty"]]]=None, provisioned_throughput: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ProvisionedThroughputProperty"]]]=None, sse_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["SSESpecificationProperty"]]]=None, table_name: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[str,str]]=None) -> None:
        """Create a new ``AWS::Serverless::SimpleTable``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            primaryKey: ``AWS::Serverless::SimpleTable.PrimaryKey``.
            provisionedThroughput: ``AWS::Serverless::SimpleTable.ProvisionedThroughput``.
            sseSpecification: ``AWS::Serverless::SimpleTable.SSESpecification``.
            tableName: ``AWS::Serverless::SimpleTable.TableName``.
            tags: ``AWS::Serverless::SimpleTable.Tags``.

        Stability:
            experimental
        """
        props: CfnSimpleTableProps = {}

        if primary_key is not None:
            props["primaryKey"] = primary_key

        if provisioned_throughput is not None:
            props["provisionedThroughput"] = provisioned_throughput

        if sse_specification is not None:
            props["sseSpecification"] = sse_specification

        if table_name is not None:
            props["tableName"] = table_name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnSimpleTable, self, [scope, id, props])

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
    @jsii.member(jsii_name="requiredTransform")
    def REQUIRED_TRANSFORM(cls) -> str:
        """The ``Transform`` a template must use in order to use this resource.

        Stability:
            experimental
        """
        return jsii.sget(cls, "requiredTransform")

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
    def property_overrides(self) -> "CfnSimpleTableProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="simpleTableName")
    def simple_table_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "simpleTableName")

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
    class _PrimaryKeyProperty(jsii.compat.TypedDict, total=False):
        name: str
        """``CfnSimpleTable.PrimaryKeyProperty.Name``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#primary-key-object
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnSimpleTable.PrimaryKeyProperty", jsii_struct_bases=[_PrimaryKeyProperty])
    class PrimaryKeyProperty(_PrimaryKeyProperty):
        """
        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#primary-key-object
        Stability:
            experimental
        """
        type: str
        """``CfnSimpleTable.PrimaryKeyProperty.Type``.

        See:
            https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#primary-key-object
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ProvisionedThroughputProperty(jsii.compat.TypedDict, total=False):
        readCapacityUnits: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSimpleTable.ProvisionedThroughputProperty.ReadCapacityUnits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-provisionedthroughput.html
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnSimpleTable.ProvisionedThroughputProperty", jsii_struct_bases=[_ProvisionedThroughputProperty])
    class ProvisionedThroughputProperty(_ProvisionedThroughputProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-provisionedthroughput.html
        Stability:
            experimental
        """
        writeCapacityUnits: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSimpleTable.ProvisionedThroughputProperty.WriteCapacityUnits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-provisionedthroughput.html
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnSimpleTable.SSESpecificationProperty", jsii_struct_bases=[])
    class SSESpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-table-ssespecification.html
        Stability:
            experimental
        """
        sseEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnSimpleTable.SSESpecificationProperty.SSEEnabled``.

        See:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-table-ssespecification.html
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-sam.CfnSimpleTableProps", jsii_struct_bases=[])
class CfnSimpleTableProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::Serverless::SimpleTable``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
    Stability:
        experimental
    """
    primaryKey: typing.Union[aws_cdk.cdk.Token, "CfnSimpleTable.PrimaryKeyProperty"]
    """``AWS::Serverless::SimpleTable.PrimaryKey``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#primary-key-object
    Stability:
        experimental
    """

    provisionedThroughput: typing.Union[aws_cdk.cdk.Token, "CfnSimpleTable.ProvisionedThroughputProperty"]
    """``AWS::Serverless::SimpleTable.ProvisionedThroughput``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-provisionedthroughput.html
    Stability:
        experimental
    """

    sseSpecification: typing.Union[aws_cdk.cdk.Token, "CfnSimpleTable.SSESpecificationProperty"]
    """``AWS::Serverless::SimpleTable.SSESpecification``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
    Stability:
        experimental
    """

    tableName: str
    """``AWS::Serverless::SimpleTable.TableName``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
    Stability:
        experimental
    """

    tags: typing.Mapping[str,str]
    """``AWS::Serverless::SimpleTable.Tags``.

    See:
        https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlesssimpletable
    Stability:
        experimental
    """

__all__ = ["CfnApi", "CfnApiProps", "CfnApplication", "CfnApplicationProps", "CfnFunction", "CfnFunctionProps", "CfnLayerVersion", "CfnLayerVersionProps", "CfnSimpleTable", "CfnSimpleTableProps", "__jsii_assembly__"]

publication.publish()
