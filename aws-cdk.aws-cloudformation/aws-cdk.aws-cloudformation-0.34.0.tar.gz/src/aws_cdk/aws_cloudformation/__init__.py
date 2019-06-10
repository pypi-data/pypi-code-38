import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_sns
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-cloudformation", "0.34.0", __name__, "aws-cloudformation@0.34.0.jsii.tgz")
class AwsCustomResource(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudformation.AwsCustomResource"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, on_create: typing.Optional["AwsSdkCall"]=None, on_delete: typing.Optional["AwsSdkCall"]=None, on_update: typing.Optional["AwsSdkCall"]=None, policy_statements: typing.Optional[typing.List[aws_cdk.aws_iam.PolicyStatement]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            onCreate: The AWS SDK call to make when the resource is created. At least onCreate, onUpdate or onDelete must be specified. Default: the call when the resource is updated
            onDelete: THe AWS SDK call to make when the resource is deleted. Default: no call
            onUpdate: The AWS SDK call to make when the resource is updated. Default: no call
            policyStatements: The IAM policy statements to allow the different calls. Use only if resource restriction is needed. Default: extract the permissions from the calls

        Stability:
            experimental
        """
        props: AwsCustomResourceProps = {}

        if on_create is not None:
            props["onCreate"] = on_create

        if on_delete is not None:
            props["onDelete"] = on_delete

        if on_update is not None:
            props["onUpdate"] = on_update

        if policy_statements is not None:
            props["policyStatements"] = policy_statements

        jsii.create(AwsCustomResource, self, [scope, id, props])

    @jsii.member(jsii_name="getData")
    def get_data(self, data_path: str) -> aws_cdk.cdk.CfnReference:
        """Returns response data for the AWS SDK call. Example for S3 / listBucket : 'Buckets.0.Name'.

        Arguments:
            dataPath: the path to the data.

        Stability:
            experimental
        """
        return jsii.invoke(self, "getData", [data_path])


@jsii.data_type(jsii_type="@aws-cdk/aws-cloudformation.AwsCustomResourceProps", jsii_struct_bases=[])
class AwsCustomResourceProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    onCreate: "AwsSdkCall"
    """The AWS SDK call to make when the resource is created. At least onCreate, onUpdate or onDelete must be specified.

    Default:
        the call when the resource is updated

    Stability:
        experimental
    """

    onDelete: "AwsSdkCall"
    """THe AWS SDK call to make when the resource is deleted.

    Default:
        no call

    Stability:
        experimental
    """

    onUpdate: "AwsSdkCall"
    """The AWS SDK call to make when the resource is updated.

    Default:
        no call

    Stability:
        experimental
    """

    policyStatements: typing.List[aws_cdk.aws_iam.PolicyStatement]
    """The IAM policy statements to allow the different calls.

    Use only if
    resource restriction is needed.

    Default:
        extract the permissions from the calls

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _AwsSdkCall(jsii.compat.TypedDict, total=False):
    apiVersion: str
    """API version to use for the service.

    Default:
        use latest available API version

    See:
        https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/locking-api-versions.html
    Stability:
        experimental
    """
    catchErrorPattern: str
    """The regex pattern to use to catch API errors.

    The ``code`` property of the
    ``Error`` object will be tested against this pattern. If there is a match an
    error will not be thrown.

    Default:
        do not catch errors

    Stability:
        experimental
    """
    parameters: typing.Any
    """The parameters for the service action.

    See:
        https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/index.html
    Stability:
        experimental
    """
    physicalResourceId: str
    """The physical resource id of the custom resource for this call.

    Either
    ``physicalResourceId`` or ``physicalResourceIdPath`` must be specified for
    onCreate or onUpdate calls.

    Default:
        no physical resource id

    Stability:
        experimental
    """
    physicalResourceIdPath: str
    """The path to the data in the API call response to use as the physical resource id.

    Either ``physicalResourceId`` or ``physicalResourceIdPath``
    must be specified for onCreate or onUpdate calls.

    Default:
        no path

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudformation.AwsSdkCall", jsii_struct_bases=[_AwsSdkCall])
class AwsSdkCall(_AwsSdkCall):
    """An AWS SDK call.

    Stability:
        experimental
    """
    action: str
    """The service action to call.

    See:
        https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/index.html
    Stability:
        experimental
    """

    service: str
    """The service to call.

    See:
        https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/index.html
    Stability:
        experimental
    """

class CfnCustomResource(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudformation.CfnCustomResource"):
    """A CloudFormation ``AWS::CloudFormation::CustomResource``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cfn-customresource.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CloudFormation::CustomResource
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, service_token: str) -> None:
        """Create a new ``AWS::CloudFormation::CustomResource``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            serviceToken: ``AWS::CloudFormation::CustomResource.ServiceToken``.

        Stability:
            experimental
        """
        props: CfnCustomResourceProps = {"serviceToken": service_token}

        jsii.create(CfnCustomResource, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnCustomResourceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-cloudformation.CfnCustomResourceProps", jsii_struct_bases=[])
class CfnCustomResourceProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::CloudFormation::CustomResource``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cfn-customresource.html
    Stability:
        experimental
    """
    serviceToken: str
    """``AWS::CloudFormation::CustomResource.ServiceToken``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cfn-customresource.html#cfn-customresource-servicetoken
    Stability:
        experimental
    """

class CfnMacro(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudformation.CfnMacro"):
    """A CloudFormation ``AWS::CloudFormation::Macro``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CloudFormation::Macro
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, function_name: str, name: str, description: typing.Optional[str]=None, log_group_name: typing.Optional[str]=None, log_role_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::CloudFormation::Macro``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            functionName: ``AWS::CloudFormation::Macro.FunctionName``.
            name: ``AWS::CloudFormation::Macro.Name``.
            description: ``AWS::CloudFormation::Macro.Description``.
            logGroupName: ``AWS::CloudFormation::Macro.LogGroupName``.
            logRoleArn: ``AWS::CloudFormation::Macro.LogRoleARN``.

        Stability:
            experimental
        """
        props: CfnMacroProps = {"functionName": function_name, "name": name}

        if description is not None:
            props["description"] = description

        if log_group_name is not None:
            props["logGroupName"] = log_group_name

        if log_role_arn is not None:
            props["logRoleArn"] = log_role_arn

        jsii.create(CfnMacro, self, [scope, id, props])

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
    @jsii.member(jsii_name="macroName")
    def macro_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "macroName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnMacroProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnMacroProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::CloudFormation::Macro.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html#cfn-cloudformation-macro-description
    Stability:
        experimental
    """
    logGroupName: str
    """``AWS::CloudFormation::Macro.LogGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html#cfn-cloudformation-macro-loggroupname
    Stability:
        experimental
    """
    logRoleArn: str
    """``AWS::CloudFormation::Macro.LogRoleARN``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html#cfn-cloudformation-macro-logrolearn
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudformation.CfnMacroProps", jsii_struct_bases=[_CfnMacroProps])
class CfnMacroProps(_CfnMacroProps):
    """Properties for defining a ``AWS::CloudFormation::Macro``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html
    Stability:
        experimental
    """
    functionName: str
    """``AWS::CloudFormation::Macro.FunctionName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html#cfn-cloudformation-macro-functionname
    Stability:
        experimental
    """

    name: str
    """``AWS::CloudFormation::Macro.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-macro.html#cfn-cloudformation-macro-name
    Stability:
        experimental
    """

class CfnStack(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudformation.CfnStack"):
    """A CloudFormation ``AWS::CloudFormation::Stack``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stack.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CloudFormation::Stack
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, template_url: str, notification_arns: typing.Optional[typing.List[str]]=None, parameters: typing.Optional[typing.Union[typing.Optional[typing.Mapping[str,str]], typing.Optional[aws_cdk.cdk.Token]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, timeout_in_minutes: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::CloudFormation::Stack``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            templateUrl: ``AWS::CloudFormation::Stack.TemplateURL``.
            notificationArns: ``AWS::CloudFormation::Stack.NotificationARNs``.
            parameters: ``AWS::CloudFormation::Stack.Parameters``.
            tags: ``AWS::CloudFormation::Stack.Tags``.
            timeoutInMinutes: ``AWS::CloudFormation::Stack.TimeoutInMinutes``.

        Stability:
            experimental
        """
        props: CfnStackProps = {"templateUrl": template_url}

        if notification_arns is not None:
            props["notificationArns"] = notification_arns

        if parameters is not None:
            props["parameters"] = parameters

        if tags is not None:
            props["tags"] = tags

        if timeout_in_minutes is not None:
            props["timeoutInMinutes"] = timeout_in_minutes

        jsii.create(CfnStack, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnStackProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "stackId")

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
class _CfnStackProps(jsii.compat.TypedDict, total=False):
    notificationArns: typing.List[str]
    """``AWS::CloudFormation::Stack.NotificationARNs``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stack.html#cfn-cloudformation-stack-notificationarns
    Stability:
        experimental
    """
    parameters: typing.Union[typing.Mapping[str,str], aws_cdk.cdk.Token]
    """``AWS::CloudFormation::Stack.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stack.html#cfn-cloudformation-stack-parameters
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::CloudFormation::Stack.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stack.html#cfn-cloudformation-stack-tags
    Stability:
        experimental
    """
    timeoutInMinutes: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::CloudFormation::Stack.TimeoutInMinutes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stack.html#cfn-cloudformation-stack-timeoutinminutes
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudformation.CfnStackProps", jsii_struct_bases=[_CfnStackProps])
class CfnStackProps(_CfnStackProps):
    """Properties for defining a ``AWS::CloudFormation::Stack``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stack.html
    Stability:
        experimental
    """
    templateUrl: str
    """``AWS::CloudFormation::Stack.TemplateURL``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stack.html#cfn-cloudformation-stack-templateurl
    Stability:
        experimental
    """

class CfnWaitCondition(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudformation.CfnWaitCondition"):
    """A CloudFormation ``AWS::CloudFormation::WaitCondition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-waitcondition.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CloudFormation::WaitCondition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, count: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, handle: typing.Optional[str]=None, timeout: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::CloudFormation::WaitCondition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            count: ``AWS::CloudFormation::WaitCondition.Count``.
            handle: ``AWS::CloudFormation::WaitCondition.Handle``.
            timeout: ``AWS::CloudFormation::WaitCondition.Timeout``.

        Stability:
            experimental
        """
        props: CfnWaitConditionProps = {}

        if count is not None:
            props["count"] = count

        if handle is not None:
            props["handle"] = handle

        if timeout is not None:
            props["timeout"] = timeout

        jsii.create(CfnWaitCondition, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnWaitConditionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="waitConditionData")
    def wait_condition_data(self) -> aws_cdk.cdk.Token:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Data
        """
        return jsii.get(self, "waitConditionData")

    @property
    @jsii.member(jsii_name="waitConditionName")
    def wait_condition_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "waitConditionName")


class CfnWaitConditionHandle(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudformation.CfnWaitConditionHandle"):
    """A CloudFormation ``AWS::CloudFormation::WaitConditionHandle``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-waitconditionhandle.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CloudFormation::WaitConditionHandle
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str) -> None:
        """Create a new ``AWS::CloudFormation::WaitConditionHandle``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.

        Stability:
            experimental
        """
        jsii.create(CfnWaitConditionHandle, self, [scope, id])

    @classproperty
    @jsii.member(jsii_name="resourceTypeName")
    def RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "resourceTypeName")

    @property
    @jsii.member(jsii_name="waitConditionHandleUrl")
    def wait_condition_handle_url(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "waitConditionHandleUrl")


@jsii.data_type(jsii_type="@aws-cdk/aws-cloudformation.CfnWaitConditionProps", jsii_struct_bases=[])
class CfnWaitConditionProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::CloudFormation::WaitCondition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-waitcondition.html
    Stability:
        experimental
    """
    count: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::CloudFormation::WaitCondition.Count``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-waitcondition.html#cfn-waitcondition-count
    Stability:
        experimental
    """

    handle: str
    """``AWS::CloudFormation::WaitCondition.Handle``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-waitcondition.html#cfn-waitcondition-handle
    Stability:
        experimental
    """

    timeout: str
    """``AWS::CloudFormation::WaitCondition.Timeout``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-waitcondition.html#cfn-waitcondition-timeout
    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-cloudformation.CloudFormationCapabilities")
class CloudFormationCapabilities(enum.Enum):
    """Capabilities that affect whether CloudFormation is allowed to change IAM resources.

    Stability:
        experimental
    """
    None_ = "None"
    """No IAM Capabilities.

    Pass this capability if you wish to block the creation IAM resources.

    Stability:
        experimental
    link:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#using-iam-capabilities
    """
    AnonymousIAM = "AnonymousIAM"
    """Capability to create anonymous IAM resources.

    Pass this capability if you're only creating anonymous resources.

    Stability:
        experimental
    link:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#using-iam-capabilities
    """
    NamedIAM = "NamedIAM"
    """Capability to create named IAM resources.

    Pass this capability if you're creating IAM resources that have physical
    names.

    ``CloudFormationCapabilities.NamedIAM`` implies ``CloudFormationCapabilities.IAM``; you don't have to pass both.

    Stability:
        experimental
    link:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#using-iam-capabilities
    """

class CustomResource(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudformation.CustomResource"):
    """Custom resource that is implemented using a Lambda.

    As a custom resource author, you should be publishing a subclass of this class
    that hides the choice of provider, and accepts a strongly-typed properties
    object with the properties your provider accepts.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, provider: "CustomResourceProvider", properties: typing.Optional[typing.Mapping[str,typing.Any]]=None, resource_type: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            provider: The provider which implements the custom resource.
            properties: Properties to pass to the Lambda. Default: - No properties.
            resourceType: For custom resources, you can specify AWS::CloudFormation::CustomResource (the default) as the resource type, or you can specify your own resource type name. For example, you can use "Custom::MyCustomResourceTypeName". Custom resource type names must begin with "Custom::" and can include alphanumeric characters and the following characters: _@-. You can specify a custom resource type name up to a maximum length of 60 characters. You cannot change the type during an update. Using your own resource type names helps you quickly differentiate the types of custom resources in your stack. For example, if you had two custom resources that conduct two different ping tests, you could name their type as Custom::PingTester to make them easily identifiable as ping testers (instead of using AWS::CloudFormation::CustomResource). Default: - AWS::CloudFormation::CustomResource

        Stability:
            experimental
        """
        props: CustomResourceProps = {"provider": provider}

        if properties is not None:
            props["properties"] = properties

        if resource_type is not None:
            props["resourceType"] = resource_type

        jsii.create(CustomResource, self, [scope, id, props])

    @jsii.member(jsii_name="getAtt")
    def get_att(self, attribute_name: str) -> aws_cdk.cdk.CfnReference:
        """
        Arguments:
            attributeName: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getAtt", [attribute_name])


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CustomResourceProps(jsii.compat.TypedDict, total=False):
    properties: typing.Mapping[str,typing.Any]
    """Properties to pass to the Lambda.

    Default:
        - No properties.

    Stability:
        experimental
    """
    resourceType: str
    """For custom resources, you can specify AWS::CloudFormation::CustomResource (the default) as the resource type, or you can specify your own resource type name.

    For example, you can use "Custom::MyCustomResourceTypeName".

    Custom resource type names must begin with "Custom::" and can include
    alphanumeric characters and the following characters: _@-. You can specify
    a custom resource type name up to a maximum length of 60 characters. You
    cannot change the type during an update.

    Using your own resource type names helps you quickly differentiate the
    types of custom resources in your stack. For example, if you had two custom
    resources that conduct two different ping tests, you could name their type
    as Custom::PingTester to make them easily identifiable as ping testers
    (instead of using AWS::CloudFormation::CustomResource).

    Default:
        - AWS::CloudFormation::CustomResource

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cfn-customresource.html#aws-cfn-resource-type-name
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudformation.CustomResourceProps", jsii_struct_bases=[_CustomResourceProps])
class CustomResourceProps(_CustomResourceProps):
    """Properties to provide a Lambda-backed custom resource.

    Stability:
        experimental
    """
    provider: "CustomResourceProvider"
    """The provider which implements the custom resource.

    Stability:
        experimental

    Example::
        CustomResourceProvider.topic(myTopic)
    """

class CustomResourceProvider(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudformation.CustomResourceProvider"):
    """
    Stability:
        experimental
    """
    @jsii.member(jsii_name="lambda")
    @classmethod
    def lambda_(cls, handler: aws_cdk.aws_lambda.IFunction) -> "CustomResourceProvider":
        """The Lambda provider that implements this custom resource.

        We recommend using a lambda.SingletonFunction for this.

        Arguments:
            handler: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "lambda", [handler])

    @jsii.member(jsii_name="topic")
    @classmethod
    def topic(cls, topic: aws_cdk.aws_sns.ITopic) -> "CustomResourceProvider":
        """The SNS Topic for the provider that implements this custom resource.

        Arguments:
            topic: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "topic", [topic])

    @property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "serviceToken")


__all__ = ["AwsCustomResource", "AwsCustomResourceProps", "AwsSdkCall", "CfnCustomResource", "CfnCustomResourceProps", "CfnMacro", "CfnMacroProps", "CfnStack", "CfnStackProps", "CfnWaitCondition", "CfnWaitConditionHandle", "CfnWaitConditionProps", "CloudFormationCapabilities", "CustomResource", "CustomResourceProps", "CustomResourceProvider", "__jsii_assembly__"]

publication.publish()
