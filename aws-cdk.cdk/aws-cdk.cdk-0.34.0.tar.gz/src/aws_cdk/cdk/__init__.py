import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/cdk", "0.34.0", __name__, "cdk@0.34.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/cdk.AppProps", jsii_struct_bases=[])
class AppProps(jsii.compat.TypedDict, total=False):
    """Initialization props for apps.

    Stability:
        experimental
    """
    autoRun: bool
    """Automatically call run before the application exits.

    If you set this, you don't have to call ``synth()`` anymore.

    Default:
        true if running via CDK toolkit (``CDK_OUTDIR`` is set), false otherwise

    Stability:
        experimental
    """

    context: typing.Mapping[str,str]
    """Additional context values for the application.

    Context can be read from any construct using ``node.getContext(key)``.

    Default:
        - no additional context

    Stability:
        experimental
    """

    outdir: str
    """The output directory into which to emit synthesized artifacts.

    Default:
        - If this value is *not* set, considers the environment variable ``CDK_OUTDIR``.
          If ``CDK_OUTDIR`` is not defined, uses a temp directory.

    Stability:
        experimental
    """

    runtimeInfo: bool
    """Include runtime versioning information in cloud assembly manifest.

    Default:
        true runtime info is included unless ``aws:cdk:disable-runtime-info`` is set in the context.

    Stability:
        experimental
    """

    stackTraces: bool
    """Include construct creation stack trace in the ``aws:cdk:trace`` metadata key of all constructs.

    Default:
        true stack traces are included unless ``aws:cdk:disable-stack-trace`` is set in the context.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _ArnComponents(jsii.compat.TypedDict, total=False):
    account: str
    """The ID of the AWS account that owns the resource, without the hyphens. For example, 123456789012. Note that the ARNs for some resources don't require an account number, so this component might be omitted.

    Default:
        The account the stack is deployed to.

    Stability:
        experimental
    """
    partition: str
    """The partition that the resource is in.

    For standard AWS regions, the
    partition is aws. If you have resources in other partitions, the
    partition is aws-partitionname. For example, the partition for resources
    in the China (Beijing) region is aws-cn.

    Default:
        The AWS partition the stack is deployed to.

    Stability:
        experimental
    """
    region: str
    """The region the resource resides in.

    Note that the ARNs for some resources
    do not require a region, so this component might be omitted.

    Default:
        The region the stack is deployed to.

    Stability:
        experimental
    """
    resourceName: str
    """Resource name or path within the resource (i.e. S3 bucket object key) or a wildcard such as ``"*"``. This is service-dependent.

    Stability:
        experimental
    """
    sep: str
    """Separator between resource type and the resource.

    Can be either '/', ':' or an empty string. Will only be used if resourceName is defined.

    Default:
        '/'

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.ArnComponents", jsii_struct_bases=[_ArnComponents])
class ArnComponents(_ArnComponents):
    """
    Stability:
        experimental
    """
    resource: str
    """Resource type (e.g. "table", "autoScalingGroup", "certificate"). For some resource types, e.g. S3 buckets, this field defines the bucket name.

    Stability:
        experimental
    """

    service: str
    """The service namespace that identifies the AWS product (for example, 's3', 'iam', 'codepipline').

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.AutoScalingCreationPolicy", jsii_struct_bases=[])
class AutoScalingCreationPolicy(jsii.compat.TypedDict, total=False):
    """For an Auto Scaling group replacement update, specifies how many instances must signal success for the update to succeed.

    Stability:
        experimental
    """
    minSuccessfulInstancesPercent: jsii.Number
    """Specifies the percentage of instances in an Auto Scaling replacement update that must signal success for the update to succeed.

    You can specify a value from 0 to 100. AWS CloudFormation rounds to the nearest tenth of a percent.
    For example, if you update five instances with a minimum successful percentage of 50, three instances must signal success.
    If an instance doesn't send a signal within the time specified by the Timeout property, AWS CloudFormation assumes that the
    instance wasn't created.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.AutoScalingReplacingUpdate", jsii_struct_bases=[])
class AutoScalingReplacingUpdate(jsii.compat.TypedDict, total=False):
    """Specifies whether an Auto Scaling group and the instances it contains are replaced during an update.

    During replacement,
    AWS CloudFormation retains the old group until it finishes creating the new one. If the update fails, AWS CloudFormation
    can roll back to the old Auto Scaling group and delete the new Auto Scaling group.

    While AWS CloudFormation creates the new group, it doesn't detach or attach any instances. After successfully creating
    the new Auto Scaling group, AWS CloudFormation deletes the old Auto Scaling group during the cleanup process.

    When you set the WillReplace parameter, remember to specify a matching CreationPolicy. If the minimum number of
    instances (specified by the MinSuccessfulInstancesPercent property) don't signal success within the Timeout period
    (specified in the CreationPolicy policy), the replacement update fails and AWS CloudFormation rolls back to the old
    Auto Scaling group.

    Stability:
        experimental
    """
    willReplace: bool
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.AutoScalingRollingUpdate", jsii_struct_bases=[])
class AutoScalingRollingUpdate(jsii.compat.TypedDict, total=False):
    """To specify how AWS CloudFormation handles rolling updates for an Auto Scaling group, use the AutoScalingRollingUpdate policy.

    Rolling updates enable you to specify whether AWS CloudFormation updates instances that are in an Auto Scaling
    group in batches or all at once.

    Stability:
        experimental
    """
    maxBatchSize: jsii.Number
    """Specifies the maximum number of instances that AWS CloudFormation updates.

    Stability:
        experimental
    """

    minInstancesInService: jsii.Number
    """Specifies the minimum number of instances that must be in service within the Auto Scaling group while AWS CloudFormation updates old instances.

    Stability:
        experimental
    """

    minSuccessfulInstancesPercent: jsii.Number
    """Specifies the percentage of instances in an Auto Scaling rolling update that must signal success for an update to succeed. You can specify a value from 0 to 100. AWS CloudFormation rounds to the nearest tenth of a percent. For example, if you update five instances with a minimum successful percentage of 50, three instances must signal success.

    If an instance doesn't send a signal within the time specified in the PauseTime property, AWS CloudFormation assumes
    that the instance wasn't updated.

    If you specify this property, you must also enable the WaitOnResourceSignals and PauseTime properties.

    Stability:
        experimental
    """

    pauseTime: str
    """The amount of time that AWS CloudFormation pauses after making a change to a batch of instances to give those instances time to start software applications.

    For example, you might need to specify PauseTime when scaling up the number of
    instances in an Auto Scaling group.

    If you enable the WaitOnResourceSignals property, PauseTime is the amount of time that AWS CloudFormation should wait
    for the Auto Scaling group to receive the required number of valid signals from added or replaced instances. If the
    PauseTime is exceeded before the Auto Scaling group receives the required number of signals, the update fails. For best
    results, specify a time period that gives your applications sufficient time to get started. If the update needs to be
    rolled back, a short PauseTime can cause the rollback to fail.

    Specify PauseTime in the ISO8601 duration format (in the format PT#H#M#S, where each # is the number of hours, minutes,
    and seconds, respectively). The maximum PauseTime is one hour (PT1H).

    Stability:
        experimental
    """

    suspendProcesses: typing.List[str]
    """Specifies the Auto Scaling processes to suspend during a stack update.

    Suspending processes prevents Auto Scaling from
    interfering with a stack update. For example, you can suspend alarming so that Auto Scaling doesn't execute scaling
    policies associated with an alarm. For valid values, see the ScalingProcesses.member.N parameter for the SuspendProcesses
    action in the Auto Scaling API Reference.

    Stability:
        experimental
    """

    waitOnResourceSignals: bool
    """Specifies whether the Auto Scaling group waits on signals from new instances during an update.

    Use this property to
    ensure that instances have completed installing and configuring applications before the Auto Scaling group update proceeds.
    AWS CloudFormation suspends the update of an Auto Scaling group after new EC2 instances are launched into the group.
    AWS CloudFormation must receive a signal from each new instance within the specified PauseTime before continuing the update.
    To signal the Auto Scaling group, use the cfn-signal helper script or SignalResource API.

    To have instances wait for an Elastic Load Balancing health check before they signal success, add a health-check
    verification by using the cfn-init helper script. For an example, see the verify_instance_health command in the Auto Scaling
    rolling updates sample template.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.AutoScalingScheduledAction", jsii_struct_bases=[])
class AutoScalingScheduledAction(jsii.compat.TypedDict, total=False):
    """With scheduled actions, the group size properties of an Auto Scaling group can change at any time.

    When you update a
    stack with an Auto Scaling group and scheduled action, AWS CloudFormation always sets the group size property values of
    your Auto Scaling group to the values that are defined in the AWS::AutoScaling::AutoScalingGroup resource of your template,
    even if a scheduled action is in effect.

    If you do not want AWS CloudFormation to change any of the group size property values when you have a scheduled action in
    effect, use the AutoScalingScheduledAction update policy to prevent AWS CloudFormation from changing the MinSize, MaxSize,
    or DesiredCapacity properties unless you have modified these values in your template.\

    Stability:
        experimental
    """
    ignoreUnmodifiedGroupSizeProperties: bool
    """
    Stability:
        experimental
    """

class AvailabilityZoneProvider(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.AvailabilityZoneProvider"):
    """Context provider that will return the availability zones for the current account and region.

    Stability:
        experimental
    """
    def __init__(self, context: "Construct") -> None:
        """
        Arguments:
            context: -

        Stability:
            experimental
        """
        jsii.create(AvailabilityZoneProvider, self, [context])

    @property
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[str]:
        """Return the list of AZs for the current account and region.

        Stability:
            experimental
        """
        return jsii.get(self, "availabilityZones")


class Aws(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.Aws"):
    """Accessor for pseudo parameters.

    Since pseudo parameters need to be anchored to a stack somewhere in the
    construct tree, this class takes an scope parameter; the pseudo parameter
    values can be obtained as properties from an scoped object.

    Stability:
        experimental
    """
    @classproperty
    @jsii.member(jsii_name="accountId")
    def account_id(cls) -> str:
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "accountId")

    @classproperty
    @jsii.member(jsii_name="notificationArns")
    def notification_arns(cls) -> typing.List[str]:
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "notificationArns")

    @classproperty
    @jsii.member(jsii_name="noValue")
    def no_value(cls) -> str:
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "noValue")

    @classproperty
    @jsii.member(jsii_name="partition")
    def partition(cls) -> str:
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "partition")

    @classproperty
    @jsii.member(jsii_name="region")
    def region(cls) -> str:
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "region")

    @classproperty
    @jsii.member(jsii_name="stackId")
    def stack_id(cls) -> str:
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "stackId")

    @classproperty
    @jsii.member(jsii_name="stackName")
    def stack_name(cls) -> str:
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "stackName")

    @classproperty
    @jsii.member(jsii_name="urlSuffix")
    def url_suffix(cls) -> str:
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "urlSuffix")


@jsii.data_type(jsii_type="@aws-cdk/cdk.CfnConditionProps", jsii_struct_bases=[])
class CfnConditionProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    expression: "ICfnConditionExpression"
    """The expression that the condition will evaluate.

    Default:
        - None.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/cdk.CfnDynamicReferenceService")
class CfnDynamicReferenceService(enum.Enum):
    """The service to retrieve the dynamic reference from.

    Stability:
        experimental
    """
    Ssm = "Ssm"
    """Plaintext value stored in AWS Systems Manager Parameter Store.

    Stability:
        experimental
    """
    SsmSecure = "SsmSecure"
    """Secure string stored in AWS Systems Manager Parameter Store.

    Stability:
        experimental
    """
    SecretsManager = "SecretsManager"
    """Secret stored in AWS Secrets Manager.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.CfnMappingProps", jsii_struct_bases=[])
class CfnMappingProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    mapping: typing.Mapping[str,typing.Mapping[str,typing.Any]]
    """Mapping of key to a set of corresponding set of named values. The key identifies a map of name-value pairs and must be unique within the mapping.

    For example, if you want to set values based on a region, you can create a mapping
    that uses the region name as a key and contains the values you want to specify for
    each specific region.

    Default:
        - No mapping.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnOutputProps(jsii.compat.TypedDict, total=False):
    condition: "CfnCondition"
    """A condition from the "Conditions" section to associate with this output value.

    If the condition evaluates to ``false``, this output value will not
    be included in the stack.

    Default:
        - No condition is associated with the output.

    Stability:
        experimental
    """
    description: str
    """A String type that describes the output value. The description can be a maximum of 4 K in length.

    Default:
        - No description.

    Stability:
        experimental
    """
    disableExport: bool
    """Disables the automatic allocation of an export name for this output.

    This prohibits exporting this value, either by specifying ``export`` or
    by calling ``makeImportValue()``.

    Default:
        false

    Stability:
        experimental
    """
    export: str
    """The name used to export the value of this output across stacks.

    To import the value from another stack, use ``FnImportValue(export)``. You
    can create an import value token by calling ``output.makeImportValue()``.

    Default:
        - Automatically allocate a name when ``makeImportValue()`` is
          called.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.CfnOutputProps", jsii_struct_bases=[_CfnOutputProps])
class CfnOutputProps(_CfnOutputProps):
    """
    Stability:
        experimental
    """
    value: typing.Any
    """The value of the property returned by the aws cloudformation describe-stacks command. The value of an output can include literals, parameter references, pseudo-parameters, a mapping value, or intrinsic functions.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnParameterProps(jsii.compat.TypedDict, total=False):
    allowedPattern: str
    """A regular expression that represents the patterns to allow for String types.

    Default:
        - No constraints on patterns allowed for parameter.

    Stability:
        experimental
    """
    allowedValues: typing.List[str]
    """An array containing the list of values allowed for the parameter.

    Default:
        - No constraints on values allowed for parameter.

    Stability:
        experimental
    """
    constraintDescription: str
    """A string that explains a constraint when the constraint is violated. For example, without a constraint description, a parameter that has an allowed pattern of [A-Za-z0-9]+ displays the following error message when the user specifies an invalid value:.

    Default:
        - No description with customized error message when user specifies invalid values.

    Stability:
        experimental
    """
    default: typing.Any
    """A value of the appropriate type for the template to use if no value is specified when a stack is created.

    If you define constraints for the parameter, you must specify
    a value that adheres to those constraints.

    Default:
        - No default value for parameter.

    Stability:
        experimental
    """
    description: str
    """A string of up to 4000 characters that describes the parameter.

    Default:
        - No description for the parameter.

    Stability:
        experimental
    """
    maxLength: jsii.Number
    """An integer value that determines the largest number of characters you want to allow for String types.

    Default:
        - None.

    Stability:
        experimental
    """
    maxValue: jsii.Number
    """A numeric value that determines the largest numeric value you want to allow for Number types.

    Default:
        - None.

    Stability:
        experimental
    """
    minLength: jsii.Number
    """An integer value that determines the smallest number of characters you want to allow for String types.

    Default:
        - None.

    Stability:
        experimental
    """
    minValue: jsii.Number
    """A numeric value that determines the smallest numeric value you want to allow for Number types.

    Default:
        - None.

    Stability:
        experimental
    """
    noEcho: bool
    """Whether to mask the parameter value when anyone makes a call that describes the stack. If you set the value to ``true``, the parameter value is masked with asterisks (``*****``).

    Default:
        - Parameter values are not masked.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.CfnParameterProps", jsii_struct_bases=[_CfnParameterProps])
class CfnParameterProps(_CfnParameterProps):
    """
    Stability:
        experimental
    """
    type: str
    """The data type for the parameter (DataType).

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnResourceProps(jsii.compat.TypedDict, total=False):
    properties: typing.Any
    """CloudFormation properties.

    Default:
        - No resource properties.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.CfnResourceProps", jsii_struct_bases=[_CfnResourceProps])
class CfnResourceProps(_CfnResourceProps):
    """
    Stability:
        experimental
    """
    type: str
    """CloudFormation resource type.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.CfnRuleProps", jsii_struct_bases=[])
class CfnRuleProps(jsii.compat.TypedDict, total=False):
    """A rule can include a RuleCondition property and must include an Assertions property. For each rule, you can define only one rule condition; you can define one or more asserts within the Assertions property. You define a rule condition and assertions by using rule-specific intrinsic functions.

    You can use the following rule-specific intrinsic functions to define rule conditions and assertions:

    Fn::And
    Fn::Contains
    Fn::EachMemberEquals
    Fn::EachMemberIn
    Fn::Equals
    Fn::If
    Fn::Not
    Fn::Or
    Fn::RefAll
    Fn::ValueOf
    Fn::ValueOfAll

    https://docs.aws.amazon.com/servicecatalog/latest/adminguide/reference-template_constraint_rules.html

    Stability:
        experimental
    """
    assertions: typing.List["RuleAssertion"]
    """Assertions which define the rule.

    Default:
        - No assertions for the rule.

    Stability:
        experimental
    """

    ruleCondition: "ICfnConditionExpression"
    """If the rule condition evaluates to false, the rule doesn't take effect. If the function in the rule condition evaluates to true, expressions in each assert are evaluated and applied.

    Default:
        - Rule's assertions will always take effect.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.CfnTag", jsii_struct_bases=[])
class CfnTag(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    link:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html
    """
    key: str
    """
    Stability:
        experimental
    link:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html#cfn-resource-tags-key
    """

    value: str
    """
    Stability:
        experimental
    link:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html#cfn-resource-tags-value
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CodeDeployLambdaAliasUpdate(jsii.compat.TypedDict, total=False):
    afterAllowTrafficHook: str
    """The name of the Lambda function to run after traffic routing completes.

    Stability:
        experimental
    """
    beforeAllowTrafficHook: str
    """The name of the Lambda function to run before traffic routing starts.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.CodeDeployLambdaAliasUpdate", jsii_struct_bases=[_CodeDeployLambdaAliasUpdate])
class CodeDeployLambdaAliasUpdate(_CodeDeployLambdaAliasUpdate):
    """To perform an AWS CodeDeploy deployment when the version changes on an AWS::Lambda::Alias resource, use the CodeDeployLambdaAliasUpdate update policy.

    Stability:
        experimental
    """
    applicationName: str
    """The name of the AWS CodeDeploy application.

    Stability:
        experimental
    """

    deploymentGroupName: str
    """The name of the AWS CodeDeploy deployment group.

    This is where the traffic-shifting policy is set.

    Stability:
        experimental
    """

class ConstructNode(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.ConstructNode"):
    """Represents the construct node in the scope tree.

    Stability:
        experimental
    """
    def __init__(self, host: "Construct", scope: "IConstruct", id: str) -> None:
        """
        Arguments:
            host: -
            scope: -
            id: -

        Stability:
            experimental
        """
        jsii.create(ConstructNode, self, [host, scope, id])

    @jsii.member(jsii_name="prepare")
    @classmethod
    def prepare(cls, node: "ConstructNode") -> None:
        """Invokes "prepare" on all constructs (depth-first, post-order) in the tree under ``node``.

        Arguments:
            node: The root node.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "prepare", [node])

    @jsii.member(jsii_name="synth")
    @classmethod
    def synth(cls, root: "ConstructNode", *, outdir: typing.Optional[str]=None, skip_validation: typing.Optional[bool]=None, runtime_info: typing.Optional[aws_cdk.cx_api.RuntimeInfo]=None) -> aws_cdk.cx_api.CloudAssembly:
        """Synthesizes a CloudAssembly from a construct tree.

        Arguments:
            root: The root of the construct tree.
            options: Synthesis options.
            outdir: The output directory into which to synthesize the cloud assembly. Default: - creates a temporary directory
            skipValidation: Whether synthesis should skip the validation phase. Default: false
            runtimeInfo: Include runtime information (module versions) in manifest. Default: true

        Stability:
            experimental
        """
        options: SynthesisOptions = {}

        if outdir is not None:
            options["outdir"] = outdir

        if skip_validation is not None:
            options["skipValidation"] = skip_validation

        if runtime_info is not None:
            options["runtimeInfo"] = runtime_info

        return jsii.sinvoke(cls, "synth", [root, options])

    @jsii.member(jsii_name="validate")
    @classmethod
    def validate(cls, node: "ConstructNode") -> typing.List["ValidationError"]:
        """Invokes "validate" on all constructs in the tree (depth-first, pre-order) and returns the list of all errors.

        An empty list indicates that there are no errors.

        Arguments:
            node: The root node.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "validate", [node])

    @jsii.member(jsii_name="addDependency")
    def add_dependency(self, *dependencies: "IDependable") -> None:
        """Add an ordering dependency on another Construct.

        All constructs in the dependency's scope will be deployed before any
        construct in this construct's scope.

        Arguments:
            dependencies: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addDependency", [*dependencies])

    @jsii.member(jsii_name="addError")
    def add_error(self, message: str) -> None:
        """Adds an { error:  } metadata entry to this construct. The toolkit will fail synthesis when errors are reported.

        Arguments:
            message: The error message.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addError", [message])

    @jsii.member(jsii_name="addInfo")
    def add_info(self, message: str) -> None:
        """Adds a { "aws:cdk:info":  } metadata entry to this construct. The toolkit will display the info message when apps are synthesized.

        Arguments:
            message: The info message.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addInfo", [message])

    @jsii.member(jsii_name="addMetadata")
    def add_metadata(self, type: str, data: typing.Any, from_: typing.Any=None) -> None:
        """Adds a metadata entry to this construct. Entries are arbitrary values and will also include a stack trace to allow tracing back to the code location for when the entry was added. It can be used, for example, to include source mapping in CloudFormation templates to improve diagnostics.

        Arguments:
            type: a string denoting the type of metadata.
            data: the value of the metadata (can be a Token). If null/undefined, metadata will not be added.
            from: a function under which to restrict the metadata entry's stack trace (defaults to this.addMetadata).

        Stability:
            experimental
        """
        return jsii.invoke(self, "addMetadata", [type, data, from_])

    @jsii.member(jsii_name="addReference")
    def add_reference(self, *refs: "Token") -> None:
        """Record a reference originating from this construct node.

        Arguments:
            refs: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addReference", [*refs])

    @jsii.member(jsii_name="addWarning")
    def add_warning(self, message: str) -> None:
        """Adds a { warning:  } metadata entry to this construct. The toolkit will display the warning when an app is synthesized, or fail if run in --strict mode.

        Arguments:
            message: The warning message.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addWarning", [message])

    @jsii.member(jsii_name="applyAspect")
    def apply_aspect(self, aspect: "IAspect") -> None:
        """Applies the aspect to this Constructs node.

        Arguments:
            aspect: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "applyAspect", [aspect])

    @jsii.member(jsii_name="findAll")
    def find_all(self, order: typing.Optional["ConstructOrder"]=None) -> typing.List["IConstruct"]:
        """Return this construct and all of its children in the given order.

        Arguments:
            order: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "findAll", [order])

    @jsii.member(jsii_name="findChild")
    def find_child(self, path: str) -> "IConstruct":
        """Return a descendant by path.

        Throws an exception if the descendant is not found.

        Note that if the original ID of the construct you are looking for contained
        a '/', then it would have been replaced by '--'.

        Arguments:
            path: Relative path of a direct or indirect child.

        Returns:
            Child with the given path.

        Stability:
            experimental
        """
        return jsii.invoke(self, "findChild", [path])

    @jsii.member(jsii_name="lock")
    def lock(self) -> None:
        """Locks this construct from allowing more children to be added.

        After this
        call, no more children can be added to this construct or to any children.

        Stability:
            experimental
        """
        return jsii.invoke(self, "lock", [])

    @jsii.member(jsii_name="setContext")
    def set_context(self, key: str, value: typing.Any) -> None:
        """This can be used to set contextual values. Context must be set before any children are added, since children may consult context info during construction. If the key already exists, it will be overridden.

        Arguments:
            key: The context key.
            value: The context value.

        Stability:
            experimental
        """
        return jsii.invoke(self, "setContext", [key, value])

    @jsii.member(jsii_name="tryFindChild")
    def try_find_child(self, path: str) -> typing.Optional["IConstruct"]:
        """Return a descendant by path, or undefined.

        Note that if the original ID of the construct you are looking for contained
        a '/', then it would have been replaced by '--'.

        Arguments:
            path: Relative path of a direct or indirect child.

        Returns:
            a child by path or undefined if not found.

        Stability:
            experimental
        """
        return jsii.invoke(self, "tryFindChild", [path])

    @jsii.member(jsii_name="tryGetContext")
    def try_get_context(self, key: str) -> typing.Any:
        """Retrieves a value from tree context.

        Context is usually initialized at the root, but can be overridden at any point in the tree.

        Arguments:
            key: The context key.

        Returns:
            The context value or ``undefined`` if there is no context value for thie key.

        Stability:
            experimental
        """
        return jsii.invoke(self, "tryGetContext", [key])

    @jsii.member(jsii_name="unlock")
    def unlock(self) -> None:
        """Unlocks this costruct and allows mutations (adding children).

        Stability:
            experimental
        """
        return jsii.invoke(self, "unlock", [])

    @classproperty
    @jsii.member(jsii_name="PATH_SEP")
    def PATH_SEP(cls) -> str:
        """Separator used to delimit construct path components.

        Stability:
            experimental
        """
        return jsii.sget(cls, "PATH_SEP")

    @property
    @jsii.member(jsii_name="children")
    def children(self) -> typing.List["IConstruct"]:
        """All direct children of this construct.

        Stability:
            experimental
        """
        return jsii.get(self, "children")

    @property
    @jsii.member(jsii_name="dependencies")
    def dependencies(self) -> typing.List["Dependency"]:
        """Return all dependencies registered on this node or any of its children.

        Stability:
            experimental
        """
        return jsii.get(self, "dependencies")

    @property
    @jsii.member(jsii_name="host")
    def host(self) -> "Construct":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "host")

    @property
    @jsii.member(jsii_name="id")
    def id(self) -> str:
        """The id of this construct within the current scope.

        This is a a scope-unique id. To obtain an app-unique id for this construct, use ``uniqueId``.

        Stability:
            experimental
        """
        return jsii.get(self, "id")

    @property
    @jsii.member(jsii_name="locked")
    def locked(self) -> bool:
        """Returns true if this construct or the scopes in which it is defined are locked.

        Stability:
            experimental
        """
        return jsii.get(self, "locked")

    @property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.List[aws_cdk.cx_api.MetadataEntry]:
        """An immutable array of metadata objects associated with this construct. This can be used, for example, to implement support for deprecation notices, source mapping, etc.

        Stability:
            experimental
        """
        return jsii.get(self, "metadata")

    @property
    @jsii.member(jsii_name="path")
    def path(self) -> str:
        """The full, absolute path of this construct in the tree.

        Components are separated by '/'.

        Stability:
            experimental
        """
        return jsii.get(self, "path")

    @property
    @jsii.member(jsii_name="references")
    def references(self) -> typing.List["OutgoingReference"]:
        """Return all references originating from this node or any of its children.

        Stability:
            experimental
        """
        return jsii.get(self, "references")

    @property
    @jsii.member(jsii_name="root")
    def root(self) -> "IConstruct":
        """
        Returns:
            The root of the construct tree.

        Stability:
            experimental
        """
        return jsii.get(self, "root")

    @property
    @jsii.member(jsii_name="scopes")
    def scopes(self) -> typing.List["IConstruct"]:
        """All parent scopes of this construct.

        Returns:
            a list of parent scopes. The last element in the list will always
            be the current construct and the first element will be the root of the
            tree.

        Stability:
            experimental
        """
        return jsii.get(self, "scopes")

    @property
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> str:
        """A tree-global unique alphanumeric identifier for this construct. Includes all components of the tree.

        Stability:
            experimental
        """
        return jsii.get(self, "uniqueId")

    @property
    @jsii.member(jsii_name="defaultChild")
    def default_child(self) -> typing.Optional["IConstruct"]:
        """Returns the child construct that has the id "Default" or "Resource".

        Returns:
            a construct or undefined if there is no default child

        Stability:
            experimental
        throws:
            if there is more than one child
        """
        return jsii.get(self, "defaultChild")

    @property
    @jsii.member(jsii_name="scope")
    def scope(self) -> typing.Optional["IConstruct"]:
        """Returns the scope in which this construct is defined.

        The value is ``undefined`` at the root of the construct scope tree.

        Stability:
            experimental
        """
        return jsii.get(self, "scope")


@jsii.enum(jsii_type="@aws-cdk/cdk.ConstructOrder")
class ConstructOrder(enum.Enum):
    """In what order to return constructs.

    Stability:
        experimental
    """
    PreOrder = "PreOrder"
    """Depth-first, pre-order.

    Stability:
        experimental
    """
    PostOrder = "PostOrder"
    """Depth-first, post-order (leaf nodes first).

    Stability:
        experimental
    """

class ContextProvider(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.ContextProvider"):
    """Base class for the model side of context providers.

    Instances of this class communicate with context provider plugins in the 'cdk
    toolkit' via context variables (input), outputting specialized queries for
    more context variables (output).

    ContextProvider needs access to a Construct to hook into the context mechanism.

    Stability:
        experimental
    """
    def __init__(self, context: "Construct", provider: str, props: typing.Optional[typing.Mapping[str,typing.Any]]=None) -> None:
        """
        Arguments:
            context: -
            provider: -
            props: -

        Stability:
            experimental
        """
        jsii.create(ContextProvider, self, [context, provider, props])

    @jsii.member(jsii_name="getStringListValue")
    def get_string_list_value(self, default_value: typing.List[str]) -> typing.List[str]:
        """Read a provider value, verifying it's a list.

        Arguments:
            defaultValue: The value to return if there is no value defined for this context key.

        Stability:
            experimental
        """
        return jsii.invoke(self, "getStringListValue", [default_value])

    @jsii.member(jsii_name="getStringValue")
    def get_string_value(self, default_value: str) -> str:
        """Read a provider value, verifying it's a string.

        Arguments:
            defaultValue: The value to return if there is no value defined for this context key.

        Stability:
            experimental
        """
        return jsii.invoke(self, "getStringValue", [default_value])

    @jsii.member(jsii_name="getValue")
    def get_value(self, default_value: typing.Any) -> typing.Any:
        """Read a provider value and verify it is not ``null``.

        Arguments:
            defaultValue: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getValue", [default_value])

    @jsii.member(jsii_name="reportMissingContext")
    def _report_missing_context(self, *, key: str, props: typing.Mapping[str,typing.Any], provider: str) -> None:
        """
        Arguments:
            report: -
            key: The missing context key.
            props: A set of provider-specific options.
            provider: The provider from which we expect this context key to be obtained.

        Stability:
            experimental
        """
        report: aws_cdk.cx_api.MissingContext = {"key": key, "props": props, "provider": provider}

        return jsii.invoke(self, "reportMissingContext", [report])

    @property
    @jsii.member(jsii_name="context")
    def context(self) -> "Construct":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "context")

    @property
    @jsii.member(jsii_name="key")
    def key(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "key")

    @property
    @jsii.member(jsii_name="provider")
    def provider(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "provider")


@jsii.data_type(jsii_type="@aws-cdk/cdk.CreationPolicy", jsii_struct_bases=[])
class CreationPolicy(jsii.compat.TypedDict, total=False):
    """Associate the CreationPolicy attribute with a resource to prevent its status from reaching create complete until AWS CloudFormation receives a specified number of success signals or the timeout period is exceeded.

    To signal a
    resource, you can use the cfn-signal helper script or SignalResource API. AWS CloudFormation publishes valid signals
    to the stack events so that you track the number of signals sent.

    The creation policy is invoked only when AWS CloudFormation creates the associated resource. Currently, the only
    AWS CloudFormation resources that support creation policies are AWS::AutoScaling::AutoScalingGroup, AWS::EC2::Instance,
    and AWS::CloudFormation::WaitCondition.

    Use the CreationPolicy attribute when you want to wait on resource configuration actions before stack creation proceeds.
    For example, if you install and configure software applications on an EC2 instance, you might want those applications to
    be running before proceeding. In such cases, you can add a CreationPolicy attribute to the instance, and then send a success
    signal to the instance after the applications are installed and configured. For a detailed example, see Deploying Applications
    on Amazon EC2 with AWS CloudFormation.

    Stability:
        experimental
    """
    autoScalingCreationPolicy: "AutoScalingCreationPolicy"
    """For an Auto Scaling group replacement update, specifies how many instances must signal success for the update to succeed.

    Stability:
        experimental
    """

    resourceSignal: "ResourceSignal"
    """When AWS CloudFormation creates the associated resource, configures the number of required success signals and the length of time that AWS CloudFormation waits for those signals.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/cdk.DeletionPolicy")
class DeletionPolicy(enum.Enum):
    """With the DeletionPolicy attribute you can preserve or (in some cases) backup a resource when its stack is deleted. You specify a DeletionPolicy attribute for each resource that you want to control. If a resource has no DeletionPolicy attribute, AWS CloudFormation deletes the resource by default. Note that this capability also applies to update operations that lead to resources being removed.

    Stability:
        experimental
    """
    Delete = "Delete"
    """AWS CloudFormation deletes the resource and all its content if applicable during stack deletion.

    You can add this
    deletion policy to any resource type. By default, if you don't specify a DeletionPolicy, AWS CloudFormation deletes
    your resources. However, be aware of the following considerations:

    Stability:
        experimental
    """
    Retain = "Retain"
    """AWS CloudFormation keeps the resource without deleting the resource or its contents when its stack is deleted. You can add this deletion policy to any resource type. Note that when AWS CloudFormation completes the stack deletion, the stack will be in Delete_Complete state; however, resources that are retained continue to exist and continue to incur applicable charges until you delete those resources.

    Stability:
        experimental
    """
    Snapshot = "Snapshot"
    """For resources that support snapshots (AWS::EC2::Volume, AWS::ElastiCache::CacheCluster, AWS::ElastiCache::ReplicationGroup, AWS::RDS::DBInstance, AWS::RDS::DBCluster, and AWS::Redshift::Cluster), AWS CloudFormation creates a snapshot for the resource before deleting it.

    Note that when AWS CloudFormation completes the stack deletion, the stack will be in the
    Delete_Complete state; however, the snapshots that are created with this policy continue to exist and continue to
    incur applicable charges until you delete those snapshots.

    Stability:
        experimental
    """

class DependableTrait(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/cdk.DependableTrait"):
    """Trait for IDependable.

    Traits are interfaces that are privately implemented by objects. Instead of
    showing up in the public interface of a class, they need to be queried
    explicitly. This is used to implement certain framework features that are
    not intended to be used by Construct consumers, and so should be hidden
    from accidental use.

    Stability:
        experimental

    Example::
        // Usage
        const roots = DependableTrait.get(construct).dependencyRoots;
        
        // Definition
        DependableTrait.implement(construct, {
          get dependencyRoots() { return []; }
        });
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _DependableTraitProxy

    def __init__(self) -> None:
        jsii.create(DependableTrait, self, [])

    @jsii.member(jsii_name="get")
    @classmethod
    def get(cls, instance: "IDependable") -> "DependableTrait":
        """Return the matching DependableTrait for the given class instance.

        Arguments:
            instance: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "get", [instance])

    @jsii.member(jsii_name="implement")
    @classmethod
    def implement(cls, instance: "IDependable", trait: "DependableTrait") -> None:
        """Register ``instance`` to have the given DependableTrait.

        Should be called in the class constructor.

        Arguments:
            instance: -
            trait: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "implement", [instance, trait])

    @property
    @jsii.member(jsii_name="dependencyRoots")
    @abc.abstractmethod
    def dependency_roots(self) -> typing.List["IConstruct"]:
        """The set of constructs that form the root of this dependable.

        All resources under all returned constructs are included in the ordering
        dependency.

        Stability:
            experimental
        """
        ...


class _DependableTraitProxy(DependableTrait):
    @property
    @jsii.member(jsii_name="dependencyRoots")
    def dependency_roots(self) -> typing.List["IConstruct"]:
        """The set of constructs that form the root of this dependable.

        All resources under all returned constructs are included in the ordering
        dependency.

        Stability:
            experimental
        """
        return jsii.get(self, "dependencyRoots")


@jsii.data_type(jsii_type="@aws-cdk/cdk.Dependency", jsii_struct_bases=[])
class Dependency(jsii.compat.TypedDict):
    """A single dependency.

    Stability:
        experimental
    """
    source: "IConstruct"
    """Source the dependency.

    Stability:
        experimental
    """

    target: "IConstruct"
    """Target of the dependency.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.DynamicReferenceProps", jsii_struct_bases=[])
class DynamicReferenceProps(jsii.compat.TypedDict):
    """Properties for a Dynamic Reference.

    Stability:
        experimental
    """
    referenceKey: str
    """The reference key of the dynamic reference.

    Stability:
        experimental
    """

    service: "CfnDynamicReferenceService"
    """The service to retrieve the dynamic reference from.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.Environment", jsii_struct_bases=[])
class Environment(jsii.compat.TypedDict, total=False):
    """The deployment environment for a stack.

    Stability:
        experimental
    """
    account: str
    """The AWS account ID for this environment. If not specified, the context parameter ``default-account`` is used.

    Stability:
        experimental
    """

    region: str
    """The AWS region for this environment. If not specified, the context parameter ``default-region`` is used.

    Stability:
        experimental
    """

class Fn(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.Fn"):
    """CloudFormation intrinsic functions. http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(Fn, self, [])

    @jsii.member(jsii_name="base64")
    @classmethod
    def base64(cls, data: str) -> str:
        """The intrinsic function ``Fn::Base64`` returns the Base64 representation of the input string.

        This function is typically used to pass encoded data to
        Amazon EC2 instances by way of the UserData property.

        Arguments:
            data: The string value you want to convert to Base64.

        Returns:
            a token represented as a string

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "base64", [data])

    @jsii.member(jsii_name="cidr")
    @classmethod
    def cidr(cls, ip_block: str, count: jsii.Number, size_mask: typing.Optional[str]=None) -> typing.List[str]:
        """The intrinsic function ``Fn::Cidr`` returns the specified Cidr address block.

        Arguments:
            ipBlock: The user-specified default Cidr address block.
            count: The number of subnets' Cidr block wanted. Count can be 1 to 256.
            sizeMask: The digit covered in the subnet.

        Returns:
            a token represented as a string

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "cidr", [ip_block, count, size_mask])

    @jsii.member(jsii_name="conditionAnd")
    @classmethod
    def condition_and(cls, *conditions: "ICfnConditionExpression") -> "ICfnConditionExpression":
        """Returns true if all the specified conditions evaluate to true, or returns false if any one of the conditions evaluates to false.

        ``Fn::And`` acts as
        an AND operator. The minimum number of conditions that you can include is
        2, and the maximum is 10.

        Arguments:
            conditions: conditions to AND.

        Returns:
            an FnCondition token

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "conditionAnd", [*conditions])

    @jsii.member(jsii_name="conditionContains")
    @classmethod
    def condition_contains(cls, list_of_strings: typing.List[str], value: str) -> "ICfnConditionExpression":
        """Returns true if a specified string matches at least one value in a list of strings.

        Arguments:
            listOfStrings: A list of strings, such as "A", "B", "C".
            value: A string, such as "A", that you want to compare against a list of strings.

        Returns:
            an FnCondition token

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "conditionContains", [list_of_strings, value])

    @jsii.member(jsii_name="conditionEquals")
    @classmethod
    def condition_equals(cls, lhs: typing.Any, rhs: typing.Any) -> "ICfnConditionExpression":
        """Compares if two values are equal.

        Returns true if the two values are equal
        or false if they aren't.

        Arguments:
            lhs: A value of any type that you want to compare.
            rhs: A value of any type that you want to compare.

        Returns:
            an FnCondition token

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "conditionEquals", [lhs, rhs])

    @jsii.member(jsii_name="conditionIf")
    @classmethod
    def condition_if(cls, condition_id: str, value_if_true: typing.Any, value_if_false: typing.Any) -> "ICfnConditionExpression":
        """Returns one value if the specified condition evaluates to true and another value if the specified condition evaluates to false.

        Currently, AWS
        CloudFormation supports the ``Fn::If`` intrinsic function in the metadata
        attribute, update policy attribute, and property values in the Resources
        section and Outputs sections of a template. You can use the AWS::NoValue
        pseudo parameter as a return value to remove the corresponding property.

        Arguments:
            conditionId: A reference to a condition in the Conditions section. Use the condition's name to reference it.
            valueIfTrue: A value to be returned if the specified condition evaluates to true.
            valueIfFalse: A value to be returned if the specified condition evaluates to false.

        Returns:
            an FnCondition token

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "conditionIf", [condition_id, value_if_true, value_if_false])

    @jsii.member(jsii_name="conditionNot")
    @classmethod
    def condition_not(cls, condition: "ICfnConditionExpression") -> "ICfnConditionExpression":
        """Returns true for a condition that evaluates to false or returns false for a condition that evaluates to true.

        ``Fn::Not`` acts as a NOT operator.

        Arguments:
            condition: A condition such as ``Fn::Equals`` that evaluates to true or false.

        Returns:
            an FnCondition token

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "conditionNot", [condition])

    @jsii.member(jsii_name="conditionOr")
    @classmethod
    def condition_or(cls, *conditions: "ICfnConditionExpression") -> "ICfnConditionExpression":
        """Returns true if any one of the specified conditions evaluate to true, or returns false if all of the conditions evaluates to false.

        ``Fn::Or`` acts
        as an OR operator. The minimum number of conditions that you can include is
        2, and the maximum is 10.

        Arguments:
            conditions: conditions that evaluates to true or false.

        Returns:
            an FnCondition token

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "conditionOr", [*conditions])

    @jsii.member(jsii_name="findInMap")
    @classmethod
    def find_in_map(cls, map_name: str, top_level_key: str, second_level_key: str) -> str:
        """The intrinsic function ``Fn::FindInMap`` returns the value corresponding to keys in a two-level map that is declared in the Mappings section.

        Arguments:
            mapName: -
            topLevelKey: -
            secondLevelKey: -

        Returns:
            a token represented as a string

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "findInMap", [map_name, top_level_key, second_level_key])

    @jsii.member(jsii_name="getAtt")
    @classmethod
    def get_att(cls, logical_name_of_resource: str, attribute_name: str) -> "Token":
        """The ``Fn::GetAtt`` intrinsic function returns the value of an attribute from a resource in the template.

        Arguments:
            logicalNameOfResource: The logical name (also called logical ID) of the resource that contains the attribute that you want.
            attributeName: The name of the resource-specific attribute whose value you want. See the resource's reference page for details about the attributes available for that resource type.

        Returns:
            a CloudFormationToken object

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "getAtt", [logical_name_of_resource, attribute_name])

    @jsii.member(jsii_name="getAZs")
    @classmethod
    def get_a_zs(cls, region: typing.Optional[str]=None) -> typing.List[str]:
        """The intrinsic function ``Fn::GetAZs`` returns an array that lists Availability Zones for a specified region.

        Because customers have access to
        different Availability Zones, the intrinsic function ``Fn::GetAZs`` enables
        template authors to write templates that adapt to the calling user's
        access. That way you don't have to hard-code a full list of Availability
        Zones for a specified region.

        Arguments:
            region: The name of the region for which you want to get the Availability Zones. You can use the AWS::Region pseudo parameter to specify the region in which the stack is created. Specifying an empty string is equivalent to specifying AWS::Region.

        Returns:
            a token represented as a string array

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "getAZs", [region])

    @jsii.member(jsii_name="importValue")
    @classmethod
    def import_value(cls, shared_value_to_import: str) -> str:
        """The intrinsic function ``Fn::ImportValue`` returns the value of an output exported by another stack.

        You typically use this function to create
        cross-stack references. In the following example template snippets, Stack A
        exports VPC security group values and Stack B imports them.

        Arguments:
            sharedValueToImport: The stack output value that you want to import.

        Returns:
            a token represented as a string

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "importValue", [shared_value_to_import])

    @jsii.member(jsii_name="join")
    @classmethod
    def join(cls, delimiter: str, list_of_values: typing.List[str]) -> str:
        """The intrinsic function ``Fn::Join`` appends a set of values into a single value, separated by the specified delimiter.

        If a delimiter is the empty
        string, the set of values are concatenated with no delimiter.

        Arguments:
            delimiter: The value you want to occur between fragments. The delimiter will occur between fragments only. It will not terminate the final value.
            listOfValues: The list of values you want combined.

        Returns:
            a token represented as a string

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "join", [delimiter, list_of_values])

    @jsii.member(jsii_name="select")
    @classmethod
    def select(cls, index: jsii.Number, array: typing.List[str]) -> str:
        """The intrinsic function ``Fn::Select`` returns a single object from a list of objects by index.

        Arguments:
            index: The index of the object to retrieve. This must be a value from zero to N-1, where N represents the number of elements in the array.
            array: The list of objects to select from. This list must not be null, nor can it have null entries.

        Returns:
            a token represented as a string

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "select", [index, array])

    @jsii.member(jsii_name="split")
    @classmethod
    def split(cls, delimiter: str, source: str) -> typing.List[str]:
        """To split a string into a list of string values so that you can select an element from the resulting string list, use the ``Fn::Split`` intrinsic function.

        Specify the location of splits
        with a delimiter, such as , (a comma). After you split a string, use the ``Fn::Select`` function
        to pick a specific element.

        Arguments:
            delimiter: A string value that determines where the source string is divided.
            source: The string value that you want to split.

        Returns:
            a token represented as a string array

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "split", [delimiter, source])

    @jsii.member(jsii_name="sub")
    @classmethod
    def sub(cls, body: str, variables: typing.Optional[typing.Mapping[str,str]]=None) -> str:
        """The intrinsic function ``Fn::Sub`` substitutes variables in an input string with values that you specify.

        In your templates, you can use this function
        to construct commands or outputs that include values that aren't available
        until you create or update a stack.

        Arguments:
            body: A string with variables that AWS CloudFormation substitutes with their associated values at runtime. Write variables as ${MyVarName}. Variables can be template parameter names, resource logical IDs, resource attributes, or a variable in a key-value map. If you specify only template parameter names, resource logical IDs, and resource attributes, don't specify a key-value map.
            variables: The name of a variable that you included in the String parameter. The value that AWS CloudFormation substitutes for the associated variable name at runtime.

        Returns:
            a token represented as a string

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "sub", [body, variables])

    @jsii.member(jsii_name="conditionEachMemberEquals")
    def condition_each_member_equals(self, list_of_strings: typing.List[str], value: str) -> "ICfnConditionExpression":
        """Returns true if a specified string matches all values in a list.

        Arguments:
            listOfStrings: A list of strings, such as "A", "B", "C".
            value: A string, such as "A", that you want to compare against a list of strings.

        Returns:
            an FnCondition token

        Stability:
            experimental
        """
        return jsii.invoke(self, "conditionEachMemberEquals", [list_of_strings, value])

    @jsii.member(jsii_name="conditionEachMemberIn")
    def condition_each_member_in(self, strings_to_check: typing.List[str], strings_to_match: str) -> "ICfnConditionExpression":
        """Returns true if each member in a list of strings matches at least one value in a second list of strings.

        Arguments:
            stringsToCheck: A list of strings, such as "A", "B", "C". AWS CloudFormation checks whether each member in the strings_to_check parameter is in the strings_to_match parameter.
            stringsToMatch: A list of strings, such as "A", "B", "C". Each member in the strings_to_match parameter is compared against the members of the strings_to_check parameter.

        Returns:
            an FnCondition token

        Stability:
            experimental
        """
        return jsii.invoke(self, "conditionEachMemberIn", [strings_to_check, strings_to_match])

    @jsii.member(jsii_name="refAll")
    def ref_all(self, parameter_type: str) -> typing.List[str]:
        """Returns all values for a specified parameter type.

        Arguments:
            parameterType: An AWS-specific parameter type, such as AWS::EC2::SecurityGroup::Id or AWS::EC2::VPC::Id. For more information, see Parameters in the AWS CloudFormation User Guide.

        Returns:
            a token represented as a string array

        Stability:
            experimental
        """
        return jsii.invoke(self, "refAll", [parameter_type])

    @jsii.member(jsii_name="valueOf")
    def value_of(self, parameter_or_logical_id: str, attribute: str) -> str:
        """Returns an attribute value or list of values for a specific parameter and attribute.

        Arguments:
            parameterOrLogicalId: The name of a parameter for which you want to retrieve attribute values. The parameter must be declared in the Parameters section of the template.
            attribute: The name of an attribute from which you want to retrieve a value.

        Returns:
            a token represented as a string

        Stability:
            experimental
        """
        return jsii.invoke(self, "valueOf", [parameter_or_logical_id, attribute])

    @jsii.member(jsii_name="valueOfAll")
    def value_of_all(self, parameter_type: str, attribute: str) -> typing.List[str]:
        """Returns a list of all attribute values for a given parameter type and attribute.

        Arguments:
            parameterType: An AWS-specific parameter type, such as AWS::EC2::SecurityGroup::Id or AWS::EC2::VPC::Id. For more information, see Parameters in the AWS CloudFormation User Guide.
            attribute: The name of an attribute from which you want to retrieve a value. For more information about attributes, see Supported Attributes.

        Returns:
            a token represented as a string array

        Stability:
            experimental
        """
        return jsii.invoke(self, "valueOfAll", [parameter_type, attribute])


@jsii.interface(jsii_type="@aws-cdk/cdk.IAddressingScheme")
class IAddressingScheme(jsii.compat.Protocol):
    """Interface for classes that implementation logical ID assignment strategies.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IAddressingSchemeProxy

    @jsii.member(jsii_name="allocateAddress")
    def allocate_address(self, address_components: typing.List[str]) -> str:
        """Return the logical ID for the given list of Construct names on the path.

        Arguments:
            addressComponents: -

        Stability:
            experimental
        """
        ...


class _IAddressingSchemeProxy():
    """Interface for classes that implementation logical ID assignment strategies.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.IAddressingScheme"
    @jsii.member(jsii_name="allocateAddress")
    def allocate_address(self, address_components: typing.List[str]) -> str:
        """Return the logical ID for the given list of Construct names on the path.

        Arguments:
            addressComponents: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allocateAddress", [address_components])


@jsii.implements(IAddressingScheme)
class HashedAddressingScheme(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.HashedAddressingScheme"):
    """Renders a hashed ID for a resource.

    In order to make sure logical IDs are unique and stable, we hash the resource
    construct tree path (i.e. toplevel/secondlevel/.../myresource) and add it as
    a suffix to the path components joined without a separator (CloudFormation
    IDs only allow alphanumeric characters).

    The result will be:

    <path.join('')><md5(path.join('/')>
    "human"      "hash"

    If the "human" part of the ID exceeds 240 characters, we simply trim it so
    the total ID doesn't exceed CloudFormation's 255 character limit.

    We only take 8 characters from the md5 hash (0.000005 chance of collision).

    Special cases:

    - If the path only contains a single component (i.e. it's a top-level
      resource), we won't add the hash to it. The hash is not needed for
      disamiguation and also, it allows for a more straightforward migration an
      existing CloudFormation template to a CDK stack without logical ID changes
      (or renames).
    - For aesthetic reasons, if the last components of the path are the same
      (i.e. ``L1/L2/Pipeline/Pipeline``), they will be de-duplicated to make the
      resulting human portion of the ID more pleasing: ``L1L2Pipeline<HASH>``
      instead of ``L1L2PipelinePipeline<HASH>``
    - If a component is named "Default" it will be omitted from the path. This
      allows refactoring higher level abstractions around constructs without affecting
      the IDs of already deployed resources.
    - If a component is named "Resource" it will be omitted from the user-visible
      path, but included in the hash. This reduces visual noise in the human readable
      part of the identifier.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(HashedAddressingScheme, self, [])

    @jsii.member(jsii_name="allocateAddress")
    def allocate_address(self, address_components: typing.List[str]) -> str:
        """Return the logical ID for the given list of Construct names on the path.

        Arguments:
            addressComponents: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "allocateAddress", [address_components])


@jsii.interface(jsii_type="@aws-cdk/cdk.IAspect")
class IAspect(jsii.compat.Protocol):
    """Represents an Aspect.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IAspectProxy

    @jsii.member(jsii_name="visit")
    def visit(self, node: "IConstruct") -> None:
        """All aspects can visit an IConstruct.

        Arguments:
            node: -

        Stability:
            experimental
        """
        ...


class _IAspectProxy():
    """Represents an Aspect.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.IAspect"
    @jsii.member(jsii_name="visit")
    def visit(self, node: "IConstruct") -> None:
        """All aspects can visit an IConstruct.

        Arguments:
            node: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "visit", [node])


@jsii.interface(jsii_type="@aws-cdk/cdk.ICfnConditionExpression")
class ICfnConditionExpression(jsii.compat.Protocol):
    """Represents a CloudFormation element that can be used within a Condition.

    You can use intrinsic functions, such as ``Fn.conditionIf``,
    ``Fn.conditionEquals``, and ``Fn.conditionNot``, to conditionally create
    stack resources. These conditions are evaluated based on input parameters
    that you declare when you create or update a stack. After you define all your
    conditions, you can associate them with resources or resource properties in
    the Resources and Outputs sections of a template.

    You define all conditions in the Conditions section of a template except for
    ``Fn.conditionIf`` conditions. You can use the ``Fn.conditionIf`` condition
    in the metadata attribute, update policy attribute, and property values in
    the Resources section and Outputs sections of a template.

    You might use conditions when you want to reuse a template that can create
    resources in different contexts, such as a test environment versus a
    production environment. In your template, you can add an EnvironmentType
    input parameter, which accepts either prod or test as inputs. For the
    production environment, you might include Amazon EC2 instances with certain
    capabilities; however, for the test environment, you want to use less
    capabilities to save costs. With conditions, you can define which resources
    are created and how they're configured for each environment type.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ICfnConditionExpressionProxy

    @jsii.member(jsii_name="resolve")
    def resolve(self, context: "IResolveContext") -> typing.Any:
        """Returns a JSON node that represents this condition expression.

        Arguments:
            context: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string token representation of this condition expression, which resolves to the CloudFormation condition JSON during synthesis.

        You can use ``toString`` when you wish to embed a condition expression
        in a property value that accepts a ``string``. For example::

           new sqs.Queue(this, 'MyQueue', {
              queueName: Fn.conditionIf('Condition', 'Hello', 'World').toString()
           });

        NOTE: we need this explicitly here despite the fact that in JavaScript this would
        "just work" since conditions are eventually tokens that implement ``toString``,
        in order for jsii languages like Java to proxy this to jsii.

        Stability:
            experimental
        """
        ...


class _ICfnConditionExpressionProxy():
    """Represents a CloudFormation element that can be used within a Condition.

    You can use intrinsic functions, such as ``Fn.conditionIf``,
    ``Fn.conditionEquals``, and ``Fn.conditionNot``, to conditionally create
    stack resources. These conditions are evaluated based on input parameters
    that you declare when you create or update a stack. After you define all your
    conditions, you can associate them with resources or resource properties in
    the Resources and Outputs sections of a template.

    You define all conditions in the Conditions section of a template except for
    ``Fn.conditionIf`` conditions. You can use the ``Fn.conditionIf`` condition
    in the metadata attribute, update policy attribute, and property values in
    the Resources section and Outputs sections of a template.

    You might use conditions when you want to reuse a template that can create
    resources in different contexts, such as a test environment versus a
    production environment. In your template, you can add an EnvironmentType
    input parameter, which accepts either prod or test as inputs. For the
    production environment, you might include Amazon EC2 instances with certain
    capabilities; however, for the test environment, you want to use less
    capabilities to save costs. With conditions, you can define which resources
    are created and how they're configured for each environment type.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.ICfnConditionExpression"
    @jsii.member(jsii_name="resolve")
    def resolve(self, context: "IResolveContext") -> typing.Any:
        """Returns a JSON node that represents this condition expression.

        Arguments:
            context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolve", [context])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string token representation of this condition expression, which resolves to the CloudFormation condition JSON during synthesis.

        You can use ``toString`` when you wish to embed a condition expression
        in a property value that accepts a ``string``. For example::

           new sqs.Queue(this, 'MyQueue', {
              queueName: Fn.conditionIf('Condition', 'Hello', 'World').toString()
           });

        NOTE: we need this explicitly here despite the fact that in JavaScript this would
        "just work" since conditions are eventually tokens that implement ``toString``,
        in order for jsii languages like Java to proxy this to jsii.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])


@jsii.interface(jsii_type="@aws-cdk/cdk.IDependable")
class IDependable(jsii.compat.Protocol):
    """Trait marker for classes that can be depended upon.

    The presence of this interface indicates that an object has
    an ``IDependableTrait`` implementation.

    This interface can be used to take an (ordering) dependency on a set of
    constructs. An ordering dependency implies that the resources represented by
    those constructs are deployed before the resources depending ON them are
    deployed.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IDependableProxy

    pass

class _IDependableProxy():
    """Trait marker for classes that can be depended upon.

    The presence of this interface indicates that an object has
    an ``IDependableTrait`` implementation.

    This interface can be used to take an (ordering) dependency on a set of
    constructs. An ordering dependency implies that the resources represented by
    those constructs are deployed before the resources depending ON them are
    deployed.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.IDependable"
    pass

@jsii.implements(IDependable)
class ConcreteDependable(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.ConcreteDependable"):
    """A set of constructs to be used as a dependable.

    This class can be used when a set of constructs which are disjoint in the
    construct tree needs to be combined to be used as a single dependable.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        """
        Stability:
            experimental
        """
        jsii.create(ConcreteDependable, self, [])

    @jsii.member(jsii_name="add")
    def add(self, construct: "IConstruct") -> None:
        """Add a construct to the dependency roots.

        Arguments:
            construct: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "add", [construct])


@jsii.interface(jsii_type="@aws-cdk/cdk.IConstruct")
class IConstruct(IDependable, jsii.compat.Protocol):
    """Represents a construct.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IConstructProxy

    @property
    @jsii.member(jsii_name="node")
    def node(self) -> "ConstructNode":
        """The construct node in the scope tree.

        Stability:
            experimental
        """
        ...


class _IConstructProxy(jsii.proxy_for(IDependable)):
    """Represents a construct.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.IConstruct"
    @property
    @jsii.member(jsii_name="node")
    def node(self) -> "ConstructNode":
        """The construct node in the scope tree.

        Stability:
            experimental
        """
        return jsii.get(self, "node")


@jsii.implements(IConstruct)
class Construct(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.Construct"):
    """Represents the building block of the construct graph.

    All constructs besides the root construct must be created within the scope of
    another construct.

    Stability:
        experimental
    """
    def __init__(self, scope: "Construct", id: str) -> None:
        """Creates a new construct node.

        Arguments:
            scope: The scope in which to define this construct.
            id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.

        Stability:
            experimental
        """
        jsii.create(Construct, self, [scope, id])

    @jsii.member(jsii_name="isConstruct")
    @classmethod
    def is_construct(cls, x: typing.Any) -> bool:
        """Return whether the given object is a Construct.

        Arguments:
            x: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "isConstruct", [x])

    @jsii.member(jsii_name="prepare")
    def _prepare(self) -> None:
        """Perform final modifications before synthesis.

        This method can be implemented by derived constructs in order to perform
        final changes before synthesis. prepare() will be called after child
        constructs have been prepared.

        This is an advanced framework feature. Only use this if you
        understand the implications.

        Stability:
            experimental
        """
        return jsii.invoke(self, "prepare", [])

    @jsii.member(jsii_name="synthesize")
    def _synthesize(self, session: "ISynthesisSession") -> None:
        """Allows this construct to emit artifacts into the cloud assembly during synthesis.

        This method is usually implemented by framework-level constructs such as ``Stack`` and ``Asset``
        as they participate in synthesizing the cloud assembly.

        Arguments:
            session: The synthesis session.

        Stability:
            experimental
        """
        return jsii.invoke(self, "synthesize", [session])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of this construct.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[str]:
        """Validate the current construct.

        This method can be implemented by derived constructs in order to perform
        validation logic. It is called on all constructs before synthesis.

        Returns:
            An array of validation error messages, or an empty array if there the construct is valid.

        Stability:
            experimental
        """
        return jsii.invoke(self, "validate", [])

    @property
    @jsii.member(jsii_name="node")
    def node(self) -> "ConstructNode":
        """Construct tree node which offers APIs for interacting with the construct tree.

        Stability:
            experimental
        """
        return jsii.get(self, "node")


class App(Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.App"):
    """A construct which represents an entire CDK app. This construct is normally the root of the construct tree.

    You would normally define an ``App`` instance in your program's entrypoint,
    then define constructs where the app is used as the parent scope.

    After all the child constructs are defined within the app, you should call
    ``app.synth()`` which will emit a "cloud assembly" from this app into the
    directory specified by ``outdir``. Cloud assemblies includes artifacts such as
    CloudFormation templates and assets that are needed to deploy this app into
    the AWS cloud.

    See:
        https://docs.aws.amazon.com/cdk/latest/guide/apps_and_stacks.html
    Stability:
        experimental
    """
    def __init__(self, *, auto_run: typing.Optional[bool]=None, context: typing.Optional[typing.Mapping[str,str]]=None, outdir: typing.Optional[str]=None, runtime_info: typing.Optional[bool]=None, stack_traces: typing.Optional[bool]=None) -> None:
        """Initializes a CDK application.

        Arguments:
            props: initialization properties.
            autoRun: Automatically call run before the application exits. If you set this, you don't have to call ``synth()`` anymore. Default: true if running via CDK toolkit (``CDK_OUTDIR`` is set), false otherwise
            context: Additional context values for the application. Context can be read from any construct using ``node.getContext(key)``. Default: - no additional context
            outdir: The output directory into which to emit synthesized artifacts. Default: - If this value is *not* set, considers the environment variable ``CDK_OUTDIR``. If ``CDK_OUTDIR`` is not defined, uses a temp directory.
            runtimeInfo: Include runtime versioning information in cloud assembly manifest. Default: true runtime info is included unless ``aws:cdk:disable-runtime-info`` is set in the context.
            stackTraces: Include construct creation stack trace in the ``aws:cdk:trace`` metadata key of all constructs. Default: true stack traces are included unless ``aws:cdk:disable-stack-trace`` is set in the context.

        Stability:
            experimental
        """
        props: AppProps = {}

        if auto_run is not None:
            props["autoRun"] = auto_run

        if context is not None:
            props["context"] = context

        if outdir is not None:
            props["outdir"] = outdir

        if runtime_info is not None:
            props["runtimeInfo"] = runtime_info

        if stack_traces is not None:
            props["stackTraces"] = stack_traces

        jsii.create(App, self, [props])

    @jsii.member(jsii_name="isApp")
    @classmethod
    def is_app(cls, obj: typing.Any) -> bool:
        """Checks if an object is an instance of the ``App`` class.

        Arguments:
            obj: The object to evaluate.

        Returns:
            ``true`` if ``obj`` is an ``App``.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "isApp", [obj])

    @jsii.member(jsii_name="run")
    def run(self) -> aws_cdk.cx_api.CloudAssembly:
        """
        Deprecated:
            use ``synth()``

        Stability:
            deprecated
        """
        return jsii.invoke(self, "run", [])

    @jsii.member(jsii_name="synth")
    def synth(self) -> aws_cdk.cx_api.CloudAssembly:
        """Synthesizes a cloud assembly for this app.

        Emits it to the directory
        specified by ``outdir``.

        Returns:
            a ``CloudAssembly`` which can be used to inspect synthesized
            artifacts such as CloudFormation templates and assets.

        Stability:
            experimental
        """
        return jsii.invoke(self, "synth", [])


class CfnElement(Construct, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/cdk.CfnElement"):
    """An element of a CloudFormation stack.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _CfnElementProxy

    def __init__(self, scope: "Construct", id: str) -> None:
        """Creates an entity and binds it to a tree. Note that the root of the tree must be a Stack object (not just any Root).

        Arguments:
            scope: The parent construct.
            id: -

        Stability:
            experimental
        """
        jsii.create(CfnElement, self, [scope, id])

    @jsii.member(jsii_name="isCfnElement")
    @classmethod
    def is_cfn_element(cls, x: typing.Any) -> bool:
        """Returns ``true`` if a construct is a stack element (i.e. part of the synthesized cloudformation template).

        Uses duck-typing instead of ``instanceof`` to allow stack elements from different
        versions of this library to be included in the same stack.

        Arguments:
            x: -

        Returns:
            The construct as a stack element or undefined if it is not a stack element.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "isCfnElement", [x])

    @jsii.member(jsii_name="overrideLogicalId")
    def override_logical_id(self, new_logical_id: str) -> None:
        """Overrides the auto-generated logical ID with a specific ID.

        Arguments:
            newLogicalId: The new logical ID to use for this stack element.

        Stability:
            experimental
        """
        return jsii.invoke(self, "overrideLogicalId", [new_logical_id])

    @jsii.member(jsii_name="prepare")
    def _prepare(self) -> None:
        """Automatically detect references in this CfnElement.

        Stability:
            experimental
        """
        return jsii.invoke(self, "prepare", [])

    @property
    @jsii.member(jsii_name="logicalId")
    def logical_id(self) -> str:
        """The logical ID for this CloudFormation stack element.

        The logical ID of the element
        is calculated from the path of the resource node in the construct tree.

        To override this value, use ``overrideLogicalId(newLogicalId)``.

        Returns:
            the logical ID as a stringified token. This value will only get
            resolved during synthesis.

        Stability:
            experimental
        """
        return jsii.get(self, "logicalId")

    @property
    @jsii.member(jsii_name="stack")
    def stack(self) -> "Stack":
        """The stack in which this element is defined.

        CfnElements must be defined within a stack scope (directly or indirectly).

        Stability:
            experimental
        """
        return jsii.get(self, "stack")

    @property
    @jsii.member(jsii_name="creationStackTrace")
    def creation_stack_trace(self) -> typing.Optional[typing.List[str]]:
        """
        Returns:
            the stack trace of the point where this Resource was created from, sourced
            from the +metadata+ entry typed +aws:cdk:logicalId+, and with the bottom-most
            node +internal+ entries filtered.

        Stability:
            experimental
        """
        return jsii.get(self, "creationStackTrace")


class _CfnElementProxy(CfnElement):
    pass

class CfnOutput(CfnElement, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.CfnOutput"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: "Construct", id: str, *, value: typing.Any, condition: typing.Optional["CfnCondition"]=None, description: typing.Optional[str]=None, disable_export: typing.Optional[bool]=None, export: typing.Optional[str]=None) -> None:
        """Creates an CfnOutput value for this stack.

        Arguments:
            scope: The parent construct.
            id: -
            props: CfnOutput properties.
            value: The value of the property returned by the aws cloudformation describe-stacks command. The value of an output can include literals, parameter references, pseudo-parameters, a mapping value, or intrinsic functions.
            condition: A condition from the "Conditions" section to associate with this output value. If the condition evaluates to ``false``, this output value will not be included in the stack. Default: - No condition is associated with the output.
            description: A String type that describes the output value. The description can be a maximum of 4 K in length. Default: - No description.
            disableExport: Disables the automatic allocation of an export name for this output. This prohibits exporting this value, either by specifying ``export`` or by calling ``makeImportValue()``. Default: false
            export: The name used to export the value of this output across stacks. To import the value from another stack, use ``FnImportValue(export)``. You can create an import value token by calling ``output.makeImportValue()``. Default: - Automatically allocate a name when ``makeImportValue()`` is called.

        Stability:
            experimental
        """
        props: CfnOutputProps = {"value": value}

        if condition is not None:
            props["condition"] = condition

        if description is not None:
            props["description"] = description

        if disable_export is not None:
            props["disableExport"] = disable_export

        if export is not None:
            props["export"] = export

        jsii.create(CfnOutput, self, [scope, id, props])

    @jsii.member(jsii_name="makeImportValue")
    def make_import_value(self) -> typing.Any:
        """Returns an FnImportValue bound to this export name.

        Stability:
            experimental
        """
        return jsii.invoke(self, "makeImportValue", [])

    @jsii.member(jsii_name="obtainExportName")
    def obtain_export_name(self) -> str:
        """Allocate an export name for this ``CfnOutput`` if not already done.

        Stability:
            experimental
        """
        return jsii.invoke(self, "obtainExportName", [])

    @property
    @jsii.member(jsii_name="ref")
    def ref(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "ref")

    @property
    @jsii.member(jsii_name="value")
    def value(self) -> typing.Any:
        """The value of the property returned by the aws cloudformation describe-stacks command. The value of an output can include literals, parameter references, pseudo-parameters, a mapping value, or intrinsic functions.

        Stability:
            experimental
        """
        return jsii.get(self, "value")

    @property
    @jsii.member(jsii_name="condition")
    def condition(self) -> typing.Optional["CfnCondition"]:
        """A condition from the "Conditions" section to associate with this output value.

        If the condition evaluates to ``false``, this output value will not
        be included in the stack.

        Stability:
            experimental
        """
        return jsii.get(self, "condition")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """A String type that describes the output value. The description can be a maximum of 4 K in length.

        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @property
    @jsii.member(jsii_name="export")
    def export(self) -> typing.Optional[str]:
        """The name of the resource output to be exported for a cross-stack reference. By default, the logical ID of the CfnOutput element is used as it's export name.

        May be undefined if the CfnOutput hasn't been exported yet.

        Stability:
            experimental
        """
        return jsii.get(self, "export")

    @export.setter
    def export(self, value: typing.Optional[str]):
        return jsii.set(self, "export", value)


class CfnRefElement(CfnElement, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/cdk.CfnRefElement"):
    """Base class for referenceable CloudFormation constructs which are not Resources.

    These constructs are things like Conditions and Parameters, can be
    referenced by taking the ``.ref`` attribute.

    Resource constructs do not inherit from CfnRefElement because they have their
    own, more specific types returned from the .ref attribute. Also, some
    resources aren't referenceable at all (such as BucketPolicies or GatewayAttachments).

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _CfnRefElementProxy

    def __init__(self, scope: "Construct", id: str) -> None:
        """Creates an entity and binds it to a tree. Note that the root of the tree must be a Stack object (not just any Root).

        Arguments:
            scope: The parent construct.
            id: -

        Stability:
            experimental
        """
        jsii.create(CfnRefElement, self, [scope, id])

    @property
    @jsii.member(jsii_name="ref")
    def ref(self) -> str:
        """Returns a token to a CloudFormation { Ref } that references this entity based on it's logical ID.

        Stability:
            experimental
        """
        return jsii.get(self, "ref")

    @property
    @jsii.member(jsii_name="referenceToken")
    def reference_token(self) -> "Token":
        """Return a token that will CloudFormation { Ref } this stack element.

        Stability:
            experimental
        """
        return jsii.get(self, "referenceToken")


class _CfnRefElementProxy(CfnRefElement, jsii.proxy_for(CfnElement)):
    pass

@jsii.implements(ICfnConditionExpression)
class CfnCondition(CfnRefElement, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.CfnCondition"):
    """Represents a CloudFormation condition, for resources which must be conditionally created and the determination must be made at deploy time.

    Stability:
        experimental
    """
    def __init__(self, scope: "Construct", id: str, *, expression: typing.Optional["ICfnConditionExpression"]=None) -> None:
        """Build a new condition.

        The condition must be constructed with a condition token,
        that the condition is based on.

        Arguments:
            scope: -
            id: -
            props: -
            expression: The expression that the condition will evaluate. Default: - None.

        Stability:
            experimental
        """
        props: CfnConditionProps = {}

        if expression is not None:
            props["expression"] = expression

        jsii.create(CfnCondition, self, [scope, id, props])

    @jsii.member(jsii_name="resolve")
    def resolve(self, _context: "IResolveContext") -> typing.Any:
        """Synthesizes the condition.

        Arguments:
            _context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolve", [_context])

    @property
    @jsii.member(jsii_name="expression")
    def expression(self) -> typing.Optional["ICfnConditionExpression"]:
        """The condition statement.

        Stability:
            experimental
        """
        return jsii.get(self, "expression")

    @expression.setter
    def expression(self, value: typing.Optional["ICfnConditionExpression"]):
        return jsii.set(self, "expression", value)


class CfnMapping(CfnRefElement, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.CfnMapping"):
    """Represents a CloudFormation mapping.

    Stability:
        experimental
    """
    def __init__(self, scope: "Construct", id: str, *, mapping: typing.Optional[typing.Mapping[str,typing.Mapping[str,typing.Any]]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            mapping: Mapping of key to a set of corresponding set of named values. The key identifies a map of name-value pairs and must be unique within the mapping. For example, if you want to set values based on a region, you can create a mapping that uses the region name as a key and contains the values you want to specify for each specific region. Default: - No mapping.

        Stability:
            experimental
        """
        props: CfnMappingProps = {}

        if mapping is not None:
            props["mapping"] = mapping

        jsii.create(CfnMapping, self, [scope, id, props])

    @jsii.member(jsii_name="findInMap")
    def find_in_map(self, key1: str, key2: str) -> str:
        """
        Arguments:
            key1: -
            key2: -

        Returns:
            A reference to a value in the map based on the two keys.

        Stability:
            experimental
        """
        return jsii.invoke(self, "findInMap", [key1, key2])

    @jsii.member(jsii_name="setValue")
    def set_value(self, key1: str, key2: str, value: typing.Any) -> None:
        """Sets a value in the map based on the two keys.

        Arguments:
            key1: -
            key2: -
            value: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "setValue", [key1, key2, value])


class CfnParameter(CfnRefElement, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.CfnParameter"):
    """Use the optional Parameters section to customize your templates. Parameters enable you to input custom values to your template each time you create or update a stack.

    Stability:
        experimental
    """
    def __init__(self, scope: "Construct", id: str, *, type: str, allowed_pattern: typing.Optional[str]=None, allowed_values: typing.Optional[typing.List[str]]=None, constraint_description: typing.Optional[str]=None, default: typing.Any=None, description: typing.Optional[str]=None, max_length: typing.Optional[jsii.Number]=None, max_value: typing.Optional[jsii.Number]=None, min_length: typing.Optional[jsii.Number]=None, min_value: typing.Optional[jsii.Number]=None, no_echo: typing.Optional[bool]=None) -> None:
        """Creates a parameter construct. Note that the name (logical ID) of the parameter will derive from it's ``coname`` and location within the stack. Therefore, it is recommended that parameters are defined at the stack level.

        Arguments:
            scope: The parent construct.
            id: -
            props: The parameter properties.
            type: The data type for the parameter (DataType).
            allowedPattern: A regular expression that represents the patterns to allow for String types. Default: - No constraints on patterns allowed for parameter.
            allowedValues: An array containing the list of values allowed for the parameter. Default: - No constraints on values allowed for parameter.
            constraintDescription: A string that explains a constraint when the constraint is violated. For example, without a constraint description, a parameter that has an allowed pattern of [A-Za-z0-9]+ displays the following error message when the user specifies an invalid value:. Default: - No description with customized error message when user specifies invalid values.
            default: A value of the appropriate type for the template to use if no value is specified when a stack is created. If you define constraints for the parameter, you must specify a value that adheres to those constraints. Default: - No default value for parameter.
            description: A string of up to 4000 characters that describes the parameter. Default: - No description for the parameter.
            maxLength: An integer value that determines the largest number of characters you want to allow for String types. Default: - None.
            maxValue: A numeric value that determines the largest numeric value you want to allow for Number types. Default: - None.
            minLength: An integer value that determines the smallest number of characters you want to allow for String types. Default: - None.
            minValue: A numeric value that determines the smallest numeric value you want to allow for Number types. Default: - None.
            noEcho: Whether to mask the parameter value when anyone makes a call that describes the stack. If you set the value to ``true``, the parameter value is masked with asterisks (``*****``). Default: - Parameter values are not masked.

        Stability:
            experimental
        """
        props: CfnParameterProps = {"type": type}

        if allowed_pattern is not None:
            props["allowedPattern"] = allowed_pattern

        if allowed_values is not None:
            props["allowedValues"] = allowed_values

        if constraint_description is not None:
            props["constraintDescription"] = constraint_description

        if default is not None:
            props["default"] = default

        if description is not None:
            props["description"] = description

        if max_length is not None:
            props["maxLength"] = max_length

        if max_value is not None:
            props["maxValue"] = max_value

        if min_length is not None:
            props["minLength"] = min_length

        if min_value is not None:
            props["minValue"] = min_value

        if no_echo is not None:
            props["noEcho"] = no_echo

        jsii.create(CfnParameter, self, [scope, id, props])

    @jsii.member(jsii_name="resolve")
    def resolve(self) -> typing.Any:
        """Allows using parameters as tokens without the need to dereference them. This implicitly implements Token, until we make it an interface.

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolve", [])

    @property
    @jsii.member(jsii_name="noEcho")
    def no_echo(self) -> bool:
        """Indicates if this parameter has "NoEcho" set.

        Stability:
            experimental
        """
        return jsii.get(self, "noEcho")

    @property
    @jsii.member(jsii_name="stringListValue")
    def string_list_value(self) -> typing.List[str]:
        """The parameter value token represented as a string array.

        Stability:
            experimental
        """
        return jsii.get(self, "stringListValue")

    @string_list_value.setter
    def string_list_value(self, value: typing.List[str]):
        return jsii.set(self, "stringListValue", value)

    @property
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> str:
        """The parameter value token represented as a string.

        Stability:
            experimental
        """
        return jsii.get(self, "stringValue")

    @string_value.setter
    def string_value(self, value: str):
        return jsii.set(self, "stringValue", value)

    @property
    @jsii.member(jsii_name="value")
    def value(self) -> "Token":
        """A token that represents the actual value of this parameter.

        Stability:
            experimental
        """
        return jsii.get(self, "value")

    @value.setter
    def value(self, value: "Token"):
        return jsii.set(self, "value", value)


class CfnResource(CfnRefElement, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.CfnResource"):
    """Represents a CloudFormation resource.

    Stability:
        experimental
    """
    def __init__(self, scope: "Construct", id: str, *, type: str, properties: typing.Any=None) -> None:
        """Creates a resource construct.

        Arguments:
            scope: -
            id: -
            props: -
            type: CloudFormation resource type.
            properties: CloudFormation properties. Default: - No resource properties.

        Stability:
            experimental
        """
        props: CfnResourceProps = {"type": type}

        if properties is not None:
            props["properties"] = properties

        jsii.create(CfnResource, self, [scope, id, props])

    @jsii.member(jsii_name="attribute")
    @classmethod
    def attribute(cls, custom_name: typing.Optional[str]=None) -> typing.Any:
        """A decoration used to create a CloudFormation attribute property.

        Arguments:
            customName: Custom name for the attribute (default is the name of the property) NOTE: we return "any" here to satistfy jsii, which doesn't support lambdas.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "attribute", [custom_name])

    @jsii.member(jsii_name="isCfnResource")
    @classmethod
    def is_cfn_resource(cls, construct: "IConstruct") -> bool:
        """Check whether the given construct is a CfnResource.

        Arguments:
            construct: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "isCfnResource", [construct])

    @jsii.member(jsii_name="addDeletionOverride")
    def add_deletion_override(self, path: str) -> None:
        """Syntactic sugar for ``addOverride(path, undefined)``.

        Arguments:
            path: The path of the value to delete.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addDeletionOverride", [path])

    @jsii.member(jsii_name="addDependsOn")
    def add_depends_on(self, resource: "CfnResource") -> None:
        """Indicates that this resource depends on another resource and cannot be provisioned unless the other resource has been successfully provisioned.

        Arguments:
            resource: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addDependsOn", [resource])

    @jsii.member(jsii_name="addOverride")
    def add_override(self, path: str, value: typing.Any) -> None:
        """Adds an override to the synthesized CloudFormation resource.

        To add a
        property override, either use ``addPropertyOverride`` or prefix ``path`` with
        "Properties." (i.e. ``Properties.TopicName``).

        Arguments:
            path: The path of the property, you can use dot notation to override values in complex types. Any intermdediate keys will be created as needed.
            value: The value. Could be primitive or complex.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addOverride", [path, value])

    @jsii.member(jsii_name="addPropertyDeletionOverride")
    def add_property_deletion_override(self, property_path: str) -> None:
        """Adds an override that deletes the value of a property from the resource definition.

        Arguments:
            propertyPath: The path to the property.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addPropertyDeletionOverride", [property_path])

    @jsii.member(jsii_name="addPropertyOverride")
    def add_property_override(self, property_path: str, value: typing.Any) -> None:
        """Adds an override to a resource property.

        Syntactic sugar for ``addOverride("Properties.<...>", value)``.

        Arguments:
            propertyPath: The path of the property.
            value: The value.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addPropertyOverride", [property_path, value])

    @jsii.member(jsii_name="getAtt")
    def get_att(self, attribute_name: str) -> "CfnReference":
        """Returns a token for an runtime attribute of this resource. Ideally, use generated attribute accessors (e.g. ``resource.arn``), but this can be used for future compatibility in case there is no generated attribute.

        Arguments:
            attributeName: The name of the attribute.

        Stability:
            experimental
        """
        return jsii.invoke(self, "getAtt", [attribute_name])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, properties: typing.Any) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            properties: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [properties])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of this construct.

        Returns:
            a string representation of this resource

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @jsii.member(jsii_name="validateProperties")
    def _validate_properties(self, _properties: typing.Any) -> None:
        """
        Arguments:
            _properties: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "validateProperties", [_properties])

    @property
    @jsii.member(jsii_name="options")
    def options(self) -> "IResourceOptions":
        """Options for this resource, such as condition, update policy etc.

        Stability:
            experimental
        """
        return jsii.get(self, "options")

    @property
    @jsii.member(jsii_name="properties")
    def _properties(self) -> typing.Any:
        """AWS resource properties.

        This object is rendered via a call to "renderProperties(this.properties)".

        Stability:
            experimental
        """
        return jsii.get(self, "properties")

    @property
    @jsii.member(jsii_name="resourceType")
    def resource_type(self) -> str:
        """AWS resource type.

        Stability:
            experimental
        """
        return jsii.get(self, "resourceType")

    @property
    @jsii.member(jsii_name="untypedPropertyOverrides")
    def _untyped_property_overrides(self) -> typing.Any:
        """AWS resource property overrides.

        During synthesis, the method "renderProperties(this.overrides)" is called
        with this object, and merged on top of the output of
        "renderProperties(this.properties)".

        Derived classes should expose a strongly-typed version of this object as
        a public property called ``propertyOverrides``.

        Stability:
            experimental
        """
        return jsii.get(self, "untypedPropertyOverrides")


class CfnRule(CfnRefElement, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.CfnRule"):
    """The Rules that define template constraints in an AWS Service Catalog portfolio describe when end users can use the template and which values they can specify for parameters that are declared in the AWS CloudFormation template used to create the product they are attempting to use.

    Rules
    are useful for preventing end users from inadvertently specifying an incorrect value.
    For example, you can add a rule to verify whether end users specified a valid subnet in a
    given VPC or used m1.small instance types for test environments. AWS CloudFormation uses
    rules to validate parameter values before it creates the resources for the product.

    A rule can include a RuleCondition property and must include an Assertions property.
    For each rule, you can define only one rule condition; you can define one or more asserts within the Assertions property.
    You define a rule condition and assertions by using rule-specific intrinsic functions.

    Stability:
        experimental
    link:
        https://docs.aws.amazon.com/servicecatalog/latest/adminguide/reference-template_constraint_rules.html
    """
    def __init__(self, scope: "Construct", id: str, *, assertions: typing.Optional[typing.List["RuleAssertion"]]=None, rule_condition: typing.Optional["ICfnConditionExpression"]=None) -> None:
        """Creates and adds a rule.

        Arguments:
            scope: The parent construct.
            id: -
            props: The rule props.
            assertions: Assertions which define the rule. Default: - No assertions for the rule.
            ruleCondition: If the rule condition evaluates to false, the rule doesn't take effect. If the function in the rule condition evaluates to true, expressions in each assert are evaluated and applied. Default: - Rule's assertions will always take effect.

        Stability:
            experimental
        """
        props: CfnRuleProps = {}

        if assertions is not None:
            props["assertions"] = assertions

        if rule_condition is not None:
            props["ruleCondition"] = rule_condition

        jsii.create(CfnRule, self, [scope, id, props])

    @jsii.member(jsii_name="addAssertion")
    def add_assertion(self, condition: "ICfnConditionExpression", description: str) -> None:
        """Adds an assertion to the rule.

        Arguments:
            condition: The expression to evaluation.
            description: The description of the assertion.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAssertion", [condition, description])

    @property
    @jsii.member(jsii_name="assertions")
    def assertions(self) -> typing.Optional[typing.List["RuleAssertion"]]:
        """Assertions which define the rule.

        Stability:
            experimental
        """
        return jsii.get(self, "assertions")

    @assertions.setter
    def assertions(self, value: typing.Optional[typing.List["RuleAssertion"]]):
        return jsii.set(self, "assertions", value)

    @property
    @jsii.member(jsii_name="ruleCondition")
    def rule_condition(self) -> typing.Optional["ICfnConditionExpression"]:
        """If the rule condition evaluates to false, the rule doesn't take effect. If the function in the rule condition evaluates to true, expressions in each assert are evaluated and applied.

        Stability:
            experimental
        """
        return jsii.get(self, "ruleCondition")

    @rule_condition.setter
    def rule_condition(self, value: typing.Optional["ICfnConditionExpression"]):
        return jsii.set(self, "ruleCondition", value)


@jsii.interface(jsii_type="@aws-cdk/cdk.IFragmentConcatenator")
class IFragmentConcatenator(jsii.compat.Protocol):
    """Function used to concatenate symbols in the target document language.

    Interface so it could potentially be exposed over jsii.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IFragmentConcatenatorProxy

    @jsii.member(jsii_name="join")
    def join(self, left: typing.Any, right: typing.Any) -> typing.Any:
        """Join the fragment on the left and on the right.

        Arguments:
            left: -
            right: -

        Stability:
            experimental
        """
        ...


class _IFragmentConcatenatorProxy():
    """Function used to concatenate symbols in the target document language.

    Interface so it could potentially be exposed over jsii.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.IFragmentConcatenator"
    @jsii.member(jsii_name="join")
    def join(self, left: typing.Any, right: typing.Any) -> typing.Any:
        """Join the fragment on the left and on the right.

        Arguments:
            left: -
            right: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "join", [left, right])


@jsii.interface(jsii_type="@aws-cdk/cdk.IResolveContext")
class IResolveContext(jsii.compat.Protocol):
    """Current resolution context for tokens.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IResolveContextProxy

    @property
    @jsii.member(jsii_name="scope")
    def scope(self) -> "IConstruct":
        """The scope from which resolution has been initiated.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="resolve")
    def resolve(self, x: typing.Any) -> typing.Any:
        """Resolve an inner object.

        Arguments:
            x: -

        Stability:
            experimental
        """
        ...


class _IResolveContextProxy():
    """Current resolution context for tokens.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.IResolveContext"
    @property
    @jsii.member(jsii_name="scope")
    def scope(self) -> "IConstruct":
        """The scope from which resolution has been initiated.

        Stability:
            experimental
        """
        return jsii.get(self, "scope")

    @jsii.member(jsii_name="resolve")
    def resolve(self, x: typing.Any) -> typing.Any:
        """Resolve an inner object.

        Arguments:
            x: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolve", [x])


@jsii.interface(jsii_type="@aws-cdk/cdk.IResolveOptions")
class IResolveOptions(jsii.compat.Protocol):
    """Options to the resolve() operation.

    NOT the same as the ResolveContext; ResolveContext is exposed to Token
    implementors and resolution hooks, whereas this struct is just to bundle
    a number of things that would otherwise be arguments to resolve() in a
    readable way.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IResolveOptionsProxy

    @property
    @jsii.member(jsii_name="resolver")
    def resolver(self) -> "ITokenResolver":
        """
        Stability:
            experimental
        """
        ...

    @resolver.setter
    def resolver(self, value: "ITokenResolver"):
        ...

    @property
    @jsii.member(jsii_name="scope")
    def scope(self) -> "IConstruct":
        """
        Stability:
            experimental
        """
        ...

    @scope.setter
    def scope(self, value: "IConstruct"):
        ...

    @property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> typing.Optional[typing.List[str]]:
        """
        Stability:
            experimental
        """
        ...

    @prefix.setter
    def prefix(self, value: typing.Optional[typing.List[str]]):
        ...


class _IResolveOptionsProxy():
    """Options to the resolve() operation.

    NOT the same as the ResolveContext; ResolveContext is exposed to Token
    implementors and resolution hooks, whereas this struct is just to bundle
    a number of things that would otherwise be arguments to resolve() in a
    readable way.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.IResolveOptions"
    @property
    @jsii.member(jsii_name="resolver")
    def resolver(self) -> "ITokenResolver":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "resolver")

    @resolver.setter
    def resolver(self, value: "ITokenResolver"):
        return jsii.set(self, "resolver", value)

    @property
    @jsii.member(jsii_name="scope")
    def scope(self) -> "IConstruct":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "scope")

    @scope.setter
    def scope(self, value: "IConstruct"):
        return jsii.set(self, "scope", value)

    @property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> typing.Optional[typing.List[str]]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "prefix")

    @prefix.setter
    def prefix(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "prefix", value)


@jsii.interface(jsii_type="@aws-cdk/cdk.IResolvedValuePostProcessor")
class IResolvedValuePostProcessor(jsii.compat.Protocol):
    """A Token that can post-process the complete resolved value, after resolve() has recursed over it.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IResolvedValuePostProcessorProxy

    @jsii.member(jsii_name="postProcess")
    def post_process(self, input: typing.Any, context: "IResolveContext") -> typing.Any:
        """Process the completely resolved value, after full recursion/resolution has happened.

        Arguments:
            input: -
            context: -

        Stability:
            experimental
        """
        ...


class _IResolvedValuePostProcessorProxy():
    """A Token that can post-process the complete resolved value, after resolve() has recursed over it.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.IResolvedValuePostProcessor"
    @jsii.member(jsii_name="postProcess")
    def post_process(self, input: typing.Any, context: "IResolveContext") -> typing.Any:
        """Process the completely resolved value, after full recursion/resolution has happened.

        Arguments:
            input: -
            context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "postProcess", [input, context])


@jsii.interface(jsii_type="@aws-cdk/cdk.IResource")
class IResource(IConstruct, jsii.compat.Protocol):
    """Interface for the Resource construct.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IResourceProxy

    pass

class _IResourceProxy(jsii.proxy_for(IConstruct)):
    """Interface for the Resource construct.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.IResource"
    pass

@jsii.interface(jsii_type="@aws-cdk/cdk.IResourceOptions")
class IResourceOptions(jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IResourceOptionsProxy

    @property
    @jsii.member(jsii_name="condition")
    def condition(self) -> typing.Optional["CfnCondition"]:
        """A condition to associate with this resource.

        This means that only if the condition evaluates to 'true' when the stack
        is deployed, the resource will be included. This is provided to allow CDK projects to produce legacy templates, but noramlly
        there is no need to use it in CDK projects.

        Stability:
            experimental
        """
        ...

    @condition.setter
    def condition(self, value: typing.Optional["CfnCondition"]):
        ...

    @property
    @jsii.member(jsii_name="creationPolicy")
    def creation_policy(self) -> typing.Optional["CreationPolicy"]:
        """Associate the CreationPolicy attribute with a resource to prevent its status from reaching create complete until AWS CloudFormation receives a specified number of success signals or the timeout period is exceeded.

        To signal a
        resource, you can use the cfn-signal helper script or SignalResource API. AWS CloudFormation publishes valid signals
        to the stack events so that you track the number of signals sent.

        Stability:
            experimental
        """
        ...

    @creation_policy.setter
    def creation_policy(self, value: typing.Optional["CreationPolicy"]):
        ...

    @property
    @jsii.member(jsii_name="deletionPolicy")
    def deletion_policy(self) -> typing.Optional["DeletionPolicy"]:
        """With the DeletionPolicy attribute you can preserve or (in some cases) backup a resource when its stack is deleted. You specify a DeletionPolicy attribute for each resource that you want to control. If a resource has no DeletionPolicy attribute, AWS CloudFormation deletes the resource by default. Note that this capability also applies to update operations that lead to resources being removed.

        Stability:
            experimental
        """
        ...

    @deletion_policy.setter
    def deletion_policy(self, value: typing.Optional["DeletionPolicy"]):
        ...

    @property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Optional[typing.Mapping[str,typing.Any]]:
        """Metadata associated with the CloudFormation resource.

        This is not the same as the construct metadata which can be added
        using construct.addMetadata(), but would not appear in the CloudFormation template automatically.

        Stability:
            experimental
        """
        ...

    @metadata.setter
    def metadata(self, value: typing.Optional[typing.Mapping[str,typing.Any]]):
        ...

    @property
    @jsii.member(jsii_name="updatePolicy")
    def update_policy(self) -> typing.Optional["UpdatePolicy"]:
        """Use the UpdatePolicy attribute to specify how AWS CloudFormation handles updates to the AWS::AutoScaling::AutoScalingGroup resource.

        AWS CloudFormation invokes one of three update policies depending on the type of change you make or whether a
        scheduled action is associated with the Auto Scaling group.

        Stability:
            experimental
        """
        ...

    @update_policy.setter
    def update_policy(self, value: typing.Optional["UpdatePolicy"]):
        ...

    @property
    @jsii.member(jsii_name="updateReplacePolicy")
    def update_replace_policy(self) -> typing.Optional["DeletionPolicy"]:
        """Use the UpdateReplacePolicy attribute to retain or (in some cases) backup the existing physical instance of a resource when it is replaced during a stack update operation.

        Stability:
            experimental
        """
        ...

    @update_replace_policy.setter
    def update_replace_policy(self, value: typing.Optional["DeletionPolicy"]):
        ...


class _IResourceOptionsProxy():
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.IResourceOptions"
    @property
    @jsii.member(jsii_name="condition")
    def condition(self) -> typing.Optional["CfnCondition"]:
        """A condition to associate with this resource.

        This means that only if the condition evaluates to 'true' when the stack
        is deployed, the resource will be included. This is provided to allow CDK projects to produce legacy templates, but noramlly
        there is no need to use it in CDK projects.

        Stability:
            experimental
        """
        return jsii.get(self, "condition")

    @condition.setter
    def condition(self, value: typing.Optional["CfnCondition"]):
        return jsii.set(self, "condition", value)

    @property
    @jsii.member(jsii_name="creationPolicy")
    def creation_policy(self) -> typing.Optional["CreationPolicy"]:
        """Associate the CreationPolicy attribute with a resource to prevent its status from reaching create complete until AWS CloudFormation receives a specified number of success signals or the timeout period is exceeded.

        To signal a
        resource, you can use the cfn-signal helper script or SignalResource API. AWS CloudFormation publishes valid signals
        to the stack events so that you track the number of signals sent.

        Stability:
            experimental
        """
        return jsii.get(self, "creationPolicy")

    @creation_policy.setter
    def creation_policy(self, value: typing.Optional["CreationPolicy"]):
        return jsii.set(self, "creationPolicy", value)

    @property
    @jsii.member(jsii_name="deletionPolicy")
    def deletion_policy(self) -> typing.Optional["DeletionPolicy"]:
        """With the DeletionPolicy attribute you can preserve or (in some cases) backup a resource when its stack is deleted. You specify a DeletionPolicy attribute for each resource that you want to control. If a resource has no DeletionPolicy attribute, AWS CloudFormation deletes the resource by default. Note that this capability also applies to update operations that lead to resources being removed.

        Stability:
            experimental
        """
        return jsii.get(self, "deletionPolicy")

    @deletion_policy.setter
    def deletion_policy(self, value: typing.Optional["DeletionPolicy"]):
        return jsii.set(self, "deletionPolicy", value)

    @property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Optional[typing.Mapping[str,typing.Any]]:
        """Metadata associated with the CloudFormation resource.

        This is not the same as the construct metadata which can be added
        using construct.addMetadata(), but would not appear in the CloudFormation template automatically.

        Stability:
            experimental
        """
        return jsii.get(self, "metadata")

    @metadata.setter
    def metadata(self, value: typing.Optional[typing.Mapping[str,typing.Any]]):
        return jsii.set(self, "metadata", value)

    @property
    @jsii.member(jsii_name="updatePolicy")
    def update_policy(self) -> typing.Optional["UpdatePolicy"]:
        """Use the UpdatePolicy attribute to specify how AWS CloudFormation handles updates to the AWS::AutoScaling::AutoScalingGroup resource.

        AWS CloudFormation invokes one of three update policies depending on the type of change you make or whether a
        scheduled action is associated with the Auto Scaling group.

        Stability:
            experimental
        """
        return jsii.get(self, "updatePolicy")

    @update_policy.setter
    def update_policy(self, value: typing.Optional["UpdatePolicy"]):
        return jsii.set(self, "updatePolicy", value)

    @property
    @jsii.member(jsii_name="updateReplacePolicy")
    def update_replace_policy(self) -> typing.Optional["DeletionPolicy"]:
        """Use the UpdateReplacePolicy attribute to retain or (in some cases) backup the existing physical instance of a resource when it is replaced during a stack update operation.

        Stability:
            experimental
        """
        return jsii.get(self, "updateReplacePolicy")

    @update_replace_policy.setter
    def update_replace_policy(self, value: typing.Optional["DeletionPolicy"]):
        return jsii.set(self, "updateReplacePolicy", value)


@jsii.interface(jsii_type="@aws-cdk/cdk.ISynthesisSession")
class ISynthesisSession(jsii.compat.Protocol):
    """Represents a single session of synthesis.

    Passed into ``Construct.synthesize()`` methods.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ISynthesisSessionProxy

    @property
    @jsii.member(jsii_name="assembly")
    def assembly(self) -> aws_cdk.cx_api.CloudAssemblyBuilder:
        """The cloud assembly being synthesized.

        Stability:
            experimental
        """
        ...

    @assembly.setter
    def assembly(self, value: aws_cdk.cx_api.CloudAssemblyBuilder):
        ...


class _ISynthesisSessionProxy():
    """Represents a single session of synthesis.

    Passed into ``Construct.synthesize()`` methods.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.ISynthesisSession"
    @property
    @jsii.member(jsii_name="assembly")
    def assembly(self) -> aws_cdk.cx_api.CloudAssemblyBuilder:
        """The cloud assembly being synthesized.

        Stability:
            experimental
        """
        return jsii.get(self, "assembly")

    @assembly.setter
    def assembly(self, value: aws_cdk.cx_api.CloudAssemblyBuilder):
        return jsii.set(self, "assembly", value)


@jsii.interface(jsii_type="@aws-cdk/cdk.ITaggable")
class ITaggable(jsii.compat.Protocol):
    """Interface to implement tags.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ITaggableProxy

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "TagManager":
        """TagManager to set, remove and format tags.

        Stability:
            experimental
        """
        ...


class _ITaggableProxy():
    """Interface to implement tags.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.ITaggable"
    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "TagManager":
        """TagManager to set, remove and format tags.

        Stability:
            experimental
        """
        return jsii.get(self, "tags")


@jsii.interface(jsii_type="@aws-cdk/cdk.ITemplateOptions")
class ITemplateOptions(jsii.compat.Protocol):
    """CloudFormation template options for a stack.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ITemplateOptionsProxy

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """Gets or sets the description of this stack. If provided, it will be included in the CloudFormation template's "Description" attribute.

        Stability:
            experimental
        """
        ...

    @description.setter
    def description(self, value: typing.Optional[str]):
        ...

    @property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Optional[typing.Mapping[str,typing.Any]]:
        """Metadata associated with the CloudFormation template.

        Stability:
            experimental
        """
        ...

    @metadata.setter
    def metadata(self, value: typing.Optional[typing.Mapping[str,typing.Any]]):
        ...

    @property
    @jsii.member(jsii_name="templateFormatVersion")
    def template_format_version(self) -> typing.Optional[str]:
        """Gets or sets the AWSTemplateFormatVersion field of the CloudFormation template.

        Stability:
            experimental
        """
        ...

    @template_format_version.setter
    def template_format_version(self, value: typing.Optional[str]):
        ...

    @property
    @jsii.member(jsii_name="transform")
    def transform(self) -> typing.Optional[str]:
        """Gets or sets the top-level template transform for this stack (e.g. "AWS::Serverless-2016-10-31").

        Stability:
            experimental
        """
        ...

    @transform.setter
    def transform(self, value: typing.Optional[str]):
        ...


class _ITemplateOptionsProxy():
    """CloudFormation template options for a stack.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.ITemplateOptions"
    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """Gets or sets the description of this stack. If provided, it will be included in the CloudFormation template's "Description" attribute.

        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Optional[typing.Mapping[str,typing.Any]]:
        """Metadata associated with the CloudFormation template.

        Stability:
            experimental
        """
        return jsii.get(self, "metadata")

    @metadata.setter
    def metadata(self, value: typing.Optional[typing.Mapping[str,typing.Any]]):
        return jsii.set(self, "metadata", value)

    @property
    @jsii.member(jsii_name="templateFormatVersion")
    def template_format_version(self) -> typing.Optional[str]:
        """Gets or sets the AWSTemplateFormatVersion field of the CloudFormation template.

        Stability:
            experimental
        """
        return jsii.get(self, "templateFormatVersion")

    @template_format_version.setter
    def template_format_version(self, value: typing.Optional[str]):
        return jsii.set(self, "templateFormatVersion", value)

    @property
    @jsii.member(jsii_name="transform")
    def transform(self) -> typing.Optional[str]:
        """Gets or sets the top-level template transform for this stack (e.g. "AWS::Serverless-2016-10-31").

        Stability:
            experimental
        """
        return jsii.get(self, "transform")

    @transform.setter
    def transform(self, value: typing.Optional[str]):
        return jsii.set(self, "transform", value)


@jsii.interface(jsii_type="@aws-cdk/cdk.ITokenMapper")
class ITokenMapper(jsii.compat.Protocol):
    """Interface to apply operation to tokens in a string.

    Interface so it can be exported via jsii.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ITokenMapperProxy

    @jsii.member(jsii_name="mapToken")
    def map_token(self, t: "Token") -> typing.Any:
        """Replace a single token.

        Arguments:
            t: -

        Stability:
            experimental
        """
        ...


class _ITokenMapperProxy():
    """Interface to apply operation to tokens in a string.

    Interface so it can be exported via jsii.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.ITokenMapper"
    @jsii.member(jsii_name="mapToken")
    def map_token(self, t: "Token") -> typing.Any:
        """Replace a single token.

        Arguments:
            t: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "mapToken", [t])


@jsii.interface(jsii_type="@aws-cdk/cdk.ITokenResolver")
class ITokenResolver(jsii.compat.Protocol):
    """How to resolve tokens.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ITokenResolverProxy

    @jsii.member(jsii_name="resolveList")
    def resolve_list(self, l: typing.List[str], context: "IResolveContext") -> typing.Any:
        """Resolve a tokenized list.

        Arguments:
            l: -
            context: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="resolveString")
    def resolve_string(self, s: "TokenizedStringFragments", context: "IResolveContext") -> typing.Any:
        """Resolve a string with at least one stringified token in it.

        (May use concatenation)

        Arguments:
            s: -
            context: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="resolveToken")
    def resolve_token(self, t: "Token", context: "IResolveContext") -> typing.Any:
        """Resolve a single token.

        Arguments:
            t: -
            context: -

        Stability:
            experimental
        """
        ...


class _ITokenResolverProxy():
    """How to resolve tokens.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/cdk.ITokenResolver"
    @jsii.member(jsii_name="resolveList")
    def resolve_list(self, l: typing.List[str], context: "IResolveContext") -> typing.Any:
        """Resolve a tokenized list.

        Arguments:
            l: -
            context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolveList", [l, context])

    @jsii.member(jsii_name="resolveString")
    def resolve_string(self, s: "TokenizedStringFragments", context: "IResolveContext") -> typing.Any:
        """Resolve a string with at least one stringified token in it.

        (May use concatenation)

        Arguments:
            s: -
            context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolveString", [s, context])

    @jsii.member(jsii_name="resolveToken")
    def resolve_token(self, t: "Token", context: "IResolveContext") -> typing.Any:
        """Resolve a single token.

        Arguments:
            t: -
            context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolveToken", [t, context])


@jsii.implements(ITokenResolver)
class DefaultTokenResolver(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.DefaultTokenResolver"):
    """Default resolver implementation.

    Stability:
        experimental
    """
    def __init__(self, concat: "IFragmentConcatenator") -> None:
        """
        Arguments:
            concat: -

        Stability:
            experimental
        """
        jsii.create(DefaultTokenResolver, self, [concat])

    @jsii.member(jsii_name="resolveList")
    def resolve_list(self, xs: typing.List[str], context: "IResolveContext") -> typing.Any:
        """Resolve a tokenized list.

        Arguments:
            xs: -
            context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolveList", [xs, context])

    @jsii.member(jsii_name="resolveString")
    def resolve_string(self, fragments: "TokenizedStringFragments", context: "IResolveContext") -> typing.Any:
        """Resolve string fragments to Tokens.

        Arguments:
            fragments: -
            context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolveString", [fragments, context])

    @jsii.member(jsii_name="resolveToken")
    def resolve_token(self, t: "Token", context: "IResolveContext") -> typing.Any:
        """Default Token resolution.

        Resolve the Token, recurse into whatever it returns,
        then finally post-process it.

        Arguments:
            t: -
            context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolveToken", [t, context])

    @property
    @jsii.member(jsii_name="concat")
    def concat(self) -> "IFragmentConcatenator":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "concat")


class Include(CfnElement, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.Include"):
    """Includes a CloudFormation template into a stack.

    All elements of the template will be merged into
    the current stack, together with any elements created programmatically.

    Stability:
        experimental
    """
    def __init__(self, scope: "Construct", id: str, *, template: typing.Mapping[typing.Any, typing.Any]) -> None:
        """Creates an adopted template construct.

        The template will be incorporated into the stack as-is with no changes at all.
        This means that logical IDs of entities within this template may conflict with logical IDs of entities that are part of the
        stack.

        Arguments:
            scope: The parent construct of this template.
            id: The ID of this construct.
            props: -
            template: The CloudFormation template to include in the stack (as is).

        Stability:
            experimental
        """
        props: IncludeProps = {"template": template}

        jsii.create(Include, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="template")
    def template(self) -> typing.Mapping[typing.Any, typing.Any]:
        """The included template.

        Stability:
            experimental
        """
        return jsii.get(self, "template")


@jsii.data_type(jsii_type="@aws-cdk/cdk.IncludeProps", jsii_struct_bases=[])
class IncludeProps(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    template: typing.Mapping[typing.Any, typing.Any]
    """The CloudFormation template to include in the stack (as is).

    Stability:
        experimental
    """

class LogicalIDs(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.LogicalIDs"):
    """Class that keeps track of the logical IDs that are assigned to resources.

    Supports renaming the generated IDs.

    Stability:
        experimental
    """
    def __init__(self, naming_scheme: "IAddressingScheme") -> None:
        """
        Arguments:
            namingScheme: -

        Stability:
            experimental
        """
        jsii.create(LogicalIDs, self, [naming_scheme])

    @jsii.member(jsii_name="assertAllRenamesApplied")
    def assert_all_renames_applied(self) -> None:
        """Throw an error if not all renames have been used.

        This is to assure that users didn't make typoes when registering renames.

        Stability:
            experimental
        """
        return jsii.invoke(self, "assertAllRenamesApplied", [])

    @jsii.member(jsii_name="getLogicalId")
    def get_logical_id(self, cfn_element: "CfnElement") -> str:
        """Return the logical ID for the given stack element.

        Arguments:
            cfnElement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getLogicalId", [cfn_element])

    @jsii.member(jsii_name="renameLogical")
    def rename_logical(self, old_id: str, new_id: str) -> None:
        """Rename a logical ID from an old ID to a new ID.

        Arguments:
            oldId: -
            newId: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renameLogical", [old_id, new_id])

    @property
    @jsii.member(jsii_name="namingScheme")
    def naming_scheme(self) -> "IAddressingScheme":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "namingScheme")


@jsii.data_type(jsii_type="@aws-cdk/cdk.OutgoingReference", jsii_struct_bases=[])
class OutgoingReference(jsii.compat.TypedDict):
    """Represents a reference that originates from a specific construct.

    Stability:
        experimental
    """
    reference: "Reference"
    """The reference.

    Stability:
        experimental
    """

    source: "IConstruct"
    """The originating construct.

    Stability:
        experimental
    """

class RememberingTokenResolver(DefaultTokenResolver, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.RememberingTokenResolver"):
    """Remember all Tokens encountered while resolving.

    Stability:
        experimental
    """
    def __init__(self, concat: "IFragmentConcatenator") -> None:
        """
        Arguments:
            concat: -

        Stability:
            experimental
        """
        jsii.create(RememberingTokenResolver, self, [concat])

    @jsii.member(jsii_name="resolveString")
    def resolve_string(self, s: "TokenizedStringFragments", context: "IResolveContext") -> typing.Any:
        """Resolve string fragments to Tokens.

        Arguments:
            s: -
            context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolveString", [s, context])

    @jsii.member(jsii_name="resolveToken")
    def resolve_token(self, t: "Token", context: "IResolveContext") -> typing.Any:
        """Default Token resolution.

        Resolve the Token, recurse into whatever it returns,
        then finally post-process it.

        Arguments:
            t: -
            context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolveToken", [t, context])

    @property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> typing.List["Token"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "tokens")


@jsii.enum(jsii_type="@aws-cdk/cdk.RemovalPolicy")
class RemovalPolicy(enum.Enum):
    """
    Stability:
        experimental
    """
    Destroy = "Destroy"
    """This is the default removal policy for most resources.

    It means that when the resource
    is removed from the app, it will be physically destroyed.

    Stability:
        experimental
    """
    Orphan = "Orphan"
    """This uses the 'Retain' DeletionPolicy, which will cause the resource to be retained in the account, but orphaned from the stack.

    Stability:
        experimental
    """
    Forbid = "Forbid"
    """This will apply the 'Retain' DeletionPolicy and also add metadata for the toolkit to apply a CloudFormation stack policy which forbids the deletion of resource.

    Stability:
        experimental
    """

@jsii.implements(IResource)
class Resource(Construct, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/cdk.Resource"):
    """A construct which represents an AWS resource.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ResourceProxy

    def __init__(self, scope: "Construct", id: str) -> None:
        """Creates a new construct node.

        Arguments:
            scope: The scope in which to define this construct.
            id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.

        Stability:
            experimental
        """
        jsii.create(Resource, self, [scope, id])


class _ResourceProxy(Resource):
    pass

@jsii.data_type(jsii_type="@aws-cdk/cdk.ResourceSignal", jsii_struct_bases=[])
class ResourceSignal(jsii.compat.TypedDict, total=False):
    """When AWS CloudFormation creates the associated resource, configures the number of required success signals and the length of time that AWS CloudFormation waits for those signals.

    Stability:
        experimental
    """
    count: jsii.Number
    """The number of success signals AWS CloudFormation must receive before it sets the resource status as CREATE_COMPLETE. If the resource receives a failure signal or doesn't receive the specified number of signals before the timeout period expires, the resource creation fails and AWS CloudFormation rolls the stack back.

    Stability:
        experimental
    """

    timeout: str
    """The length of time that AWS CloudFormation waits for the number of signals that was specified in the Count property. The timeout period starts after AWS CloudFormation starts creating the resource, and the timeout expires no sooner than the time you specify but can occur shortly thereafter. The maximum time that you can specify is 12 hours.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.RuleAssertion", jsii_struct_bases=[])
class RuleAssertion(jsii.compat.TypedDict):
    """A rule assertion.

    Stability:
        experimental
    """
    assert_: "ICfnConditionExpression"
    """The assertion.

    Stability:
        experimental
    """

    assertDescription: str
    """The assertion description.

    Stability:
        experimental
    """

class SSMParameterProvider(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.SSMParameterProvider"):
    """Context provider that will read values from the SSM parameter store in the indicated account and region.

    Stability:
        experimental
    """
    def __init__(self, context: "Construct", *, parameter_name: str) -> None:
        """
        Arguments:
            context: -
            props: -
            parameterName: The name of the parameter to lookup.

        Stability:
            experimental
        """
        props: SSMParameterProviderProps = {"parameterName": parameter_name}

        jsii.create(SSMParameterProvider, self, [context, props])

    @jsii.member(jsii_name="parameterValue")
    def parameter_value(self, default_value: typing.Optional[str]=None) -> typing.Any:
        """Return the SSM parameter string with the indicated key.

        Arguments:
            defaultValue: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "parameterValue", [default_value])


@jsii.data_type(jsii_type="@aws-cdk/cdk.SSMParameterProviderProps", jsii_struct_bases=[])
class SSMParameterProviderProps(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    parameterName: str
    """The name of the parameter to lookup.

    Stability:
        experimental
    """

class ScopedAws(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.ScopedAws"):
    """Accessor for scoped pseudo parameters.

    These pseudo parameters are anchored to a stack somewhere in the construct
    tree, and their values will be exported automatically.

    Stability:
        experimental
    """
    def __init__(self, scope: "Construct") -> None:
        """
        Arguments:
            scope: -

        Stability:
            experimental
        """
        jsii.create(ScopedAws, self, [scope])

    @property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "accountId")

    @property
    @jsii.member(jsii_name="notificationArns")
    def notification_arns(self) -> typing.List[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "notificationArns")

    @property
    @jsii.member(jsii_name="partition")
    def partition(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "partition")

    @property
    @jsii.member(jsii_name="region")
    def region(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "region")

    @property
    @jsii.member(jsii_name="scope")
    def scope(self) -> "Construct":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "scope")

    @property
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "stackId")

    @property
    @jsii.member(jsii_name="stackName")
    def stack_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "stackName")

    @property
    @jsii.member(jsii_name="urlSuffix")
    def url_suffix(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "urlSuffix")


@jsii.data_type(jsii_type="@aws-cdk/cdk.SecretsManagerSecretOptions", jsii_struct_bases=[])
class SecretsManagerSecretOptions(jsii.compat.TypedDict, total=False):
    """Options for referencing a secret value from Secrets Manager.

    Stability:
        experimental
    """
    jsonField: str
    """The key of a JSON field to retrieve.

    This can only be used if the secret
    stores a JSON object.

    Default:
        - returns all the content stored in the Secrets Manager secret.

    Stability:
        experimental
    """

    versionId: str
    """Specifies the unique identifier of the version of the secret you want to use.

    Can specify at most one of ``versionId`` and ``versionStage``.

    Default:
        AWSCURRENT

    Stability:
        experimental
    """

    versionStage: str
    """Specified the secret version that you want to retrieve by the staging label attached to the version.

    Can specify at most one of ``versionId`` and ``versionStage``.

    Default:
        AWSCURRENT

    Stability:
        experimental
    """

@jsii.implements(ITaggable)
class Stack(Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.Stack"):
    """A root construct which represents a single CloudFormation stack.

    Stability:
        experimental
    """
    def __init__(self, scope: typing.Optional["Construct"]=None, name: typing.Optional[str]=None, *, env: typing.Optional["Environment"]=None, naming_scheme: typing.Optional["IAddressingScheme"]=None, stack_name: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[str,str]]=None) -> None:
        """Creates a new stack.

        Arguments:
            scope: Parent of this stack, usually a Program instance.
            name: The name of the CloudFormation stack. Defaults to "Stack".
            props: Stack properties.
            env: The AWS environment (account/region) where this stack will be deployed. Default: - The ``default-account`` and ``default-region`` context parameters will be used. If they are undefined, it will not be possible to deploy the stack.
            namingScheme: Strategy for logical ID generation. Default: - The HashedNamingScheme will be used.
            stackName: Name to deploy the stack with. Default: - Derived from construct path.
            tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}

        Stability:
            experimental
        """
        props: StackProps = {}

        if env is not None:
            props["env"] = env

        if naming_scheme is not None:
            props["namingScheme"] = naming_scheme

        if stack_name is not None:
            props["stackName"] = stack_name

        if tags is not None:
            props["tags"] = tags

        jsii.create(Stack, self, [scope, name, props])

    @jsii.member(jsii_name="isStack")
    @classmethod
    def is_stack(cls, x: typing.Any) -> bool:
        """Return whether the given object is a Stack.

        We do attribute detection since we can't reliably use 'instanceof'.

        Arguments:
            x: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "isStack", [x])

    @jsii.member(jsii_name="of")
    @classmethod
    def of(cls, construct: "IConstruct") -> "Stack":
        """Looks up the first stack scope in which ``construct`` is defined.

        Fails if there is no stack up the tree.

        Arguments:
            construct: The construct to start the search from.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "of", [construct])

    @jsii.member(jsii_name="addDependency")
    def add_dependency(self, stack: "Stack", reason: typing.Optional[str]=None) -> None:
        """Add a dependency between this stack and another stack.

        Arguments:
            stack: -
            reason: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addDependency", [stack, reason])

    @jsii.member(jsii_name="findResource")
    def find_resource(self, construct_path: str) -> typing.Optional["CfnResource"]:
        """Looks up a resource by path.

        Arguments:
            constructPath: -

        Returns:
            The Resource or undefined if not found

        Stability:
            experimental
        """
        return jsii.invoke(self, "findResource", [construct_path])

    @jsii.member(jsii_name="formatArn")
    def format_arn(self, *, resource: str, service: str, account: typing.Optional[str]=None, partition: typing.Optional[str]=None, region: typing.Optional[str]=None, resource_name: typing.Optional[str]=None, sep: typing.Optional[str]=None) -> str:
        """Creates an ARN from components.

        If ``partition``, ``region`` or ``account`` are not specified, the stack's
        partition, region and account will be used.

        If any component is the empty string, an empty string will be inserted
        into the generated ARN at the location that component corresponds to.

        The ARN will be formatted as follows:

        arn:{partition}:{service}:{region}:{account}:{resource}{sep}}{resource-name}

        The required ARN pieces that are omitted will be taken from the stack that
        the 'scope' is attached to. If all ARN pieces are supplied, the supplied scope
        can be 'undefined'.

        Arguments:
            components: -
            resource: Resource type (e.g. "table", "autoScalingGroup", "certificate"). For some resource types, e.g. S3 buckets, this field defines the bucket name.
            service: The service namespace that identifies the AWS product (for example, 's3', 'iam', 'codepipline').
            account: The ID of the AWS account that owns the resource, without the hyphens. For example, 123456789012. Note that the ARNs for some resources don't require an account number, so this component might be omitted. Default: The account the stack is deployed to.
            partition: The partition that the resource is in. For standard AWS regions, the partition is aws. If you have resources in other partitions, the partition is aws-partitionname. For example, the partition for resources in the China (Beijing) region is aws-cn. Default: The AWS partition the stack is deployed to.
            region: The region the resource resides in. Note that the ARNs for some resources do not require a region, so this component might be omitted. Default: The region the stack is deployed to.
            resourceName: Resource name or path within the resource (i.e. S3 bucket object key) or a wildcard such as ``"*"``. This is service-dependent.
            sep: Separator between resource type and the resource. Can be either '/', ':' or an empty string. Will only be used if resourceName is defined. Default: '/'

        Stability:
            experimental
        """
        components: ArnComponents = {"resource": resource, "service": service}

        if account is not None:
            components["account"] = account

        if partition is not None:
            components["partition"] = partition

        if region is not None:
            components["region"] = region

        if resource_name is not None:
            components["resourceName"] = resource_name

        if sep is not None:
            components["sep"] = sep

        return jsii.invoke(self, "formatArn", [components])

    @jsii.member(jsii_name="parentApp")
    def parent_app(self) -> typing.Optional["App"]:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "parentApp", [])

    @jsii.member(jsii_name="parseArn")
    def parse_arn(self, arn: str, sep_if_token: typing.Optional[str]=None, has_name: typing.Optional[bool]=None) -> "ArnComponents":
        """Given an ARN, parses it and returns components.

        If the ARN is a concrete string, it will be parsed and validated. The
        separator (``sep``) will be set to '/' if the 6th component includes a '/',
        in which case, ``resource`` will be set to the value before the '/' and
        ``resourceName`` will be the rest. In case there is no '/', ``resource`` will
        be set to the 6th components and ``resourceName`` will be set to the rest
        of the string.

        If the ARN includes tokens (or is a token), the ARN cannot be validated,
        since we don't have the actual value yet at the time of this function
        call. You will have to know the separator and the type of ARN. The
        resulting ``ArnComponents`` object will contain tokens for the
        subexpressions of the ARN, not string literals. In this case this
        function cannot properly parse the complete final resourceName (path) out
        of ARNs that use '/' to both separate the 'resource' from the
        'resourceName' AND to subdivide the resourceName further. For example, in
        S3 ARNs::

           arn:aws:s3:::my_corporate_bucket/path/to/exampleobject.png

        After parsing the resourceName will not contain
        'path/to/exampleobject.png' but simply 'path'. This is a limitation
        because there is no slicing functionality in CloudFormation templates.

        Arguments:
            arn: The ARN string to parse.
            sepIfToken: The separator used to separate resource from resourceName.
            hasName: Whether there is a name component in the ARN at all. For example, SNS Topics ARNs have the 'resource' component contain the topic name, and no 'resourceName' component.

        Returns:
            an ArnComponents object which allows access to the various
            components of the ARN.

        Stability:
            experimental
        """
        return jsii.invoke(self, "parseArn", [arn, sep_if_token, has_name])

    @jsii.member(jsii_name="prepare")
    def _prepare(self) -> None:
        """Prepare stack.

        Find all CloudFormation references and tell them we're consuming them.

        Find all dependencies as well and add the appropriate DependsOn fields.

        Stability:
            experimental
        """
        return jsii.invoke(self, "prepare", [])

    @jsii.member(jsii_name="renameLogical")
    def rename_logical(self, old_id: str, new_id: str) -> None:
        """Rename a generated logical identities.

        Arguments:
            oldId: -
            newId: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renameLogical", [old_id, new_id])

    @jsii.member(jsii_name="reportMissingContext")
    def report_missing_context(self, *, key: str, props: typing.Mapping[str,typing.Any], provider: str) -> None:
        """Indicate that a context key was expected.

        Contains instructions which will be emitted into the cloud assembly on how
        the key should be supplied.

        Arguments:
            report: The set of parameters needed to obtain the context.
            key: The missing context key.
            props: A set of provider-specific options.
            provider: The provider from which we expect this context key to be obtained.

        Stability:
            experimental
        """
        report: aws_cdk.cx_api.MissingContext = {"key": key, "props": props, "provider": provider}

        return jsii.invoke(self, "reportMissingContext", [report])

    @jsii.member(jsii_name="requireAccountId")
    def require_account_id(self, why: typing.Optional[str]=None) -> str:
        """Returns the AWS account ID of this Stack, or throws an exception if the account ID is not set in the environment.

        Arguments:
            why: more information about why is the account ID required.

        Returns:
            the AWS account ID of this Stack

        Stability:
            experimental
        """
        return jsii.invoke(self, "requireAccountId", [why])

    @jsii.member(jsii_name="requireRegion")
    def require_region(self, why: typing.Optional[str]=None) -> str:
        """
        Arguments:
            why: more information about why region is required.

        Returns:
            The region in which this stack is deployed. Throws if region is not defined.

        Stability:
            experimental
        """
        return jsii.invoke(self, "requireRegion", [why])

    @jsii.member(jsii_name="resolve")
    def resolve(self, obj: typing.Any) -> typing.Any:
        """Resolve a tokenized value in the context of the current stack.

        Arguments:
            obj: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolve", [obj])

    @jsii.member(jsii_name="setParameterValue")
    def set_parameter_value(self, parameter: "CfnParameter", value: str) -> None:
        """Sets the value of a CloudFormation parameter.

        Arguments:
            parameter: The parameter to set the value for.
            value: The value, can use ``${}`` notation to reference other assembly block attributes.

        Stability:
            experimental
        """
        return jsii.invoke(self, "setParameterValue", [parameter, value])

    @jsii.member(jsii_name="synthesize")
    def _synthesize(self, session: "ISynthesisSession") -> None:
        """Allows this construct to emit artifacts into the cloud assembly during synthesis.

        This method is usually implemented by framework-level constructs such as ``Stack`` and ``Asset``
        as they participate in synthesizing the cloud assembly.

        Arguments:
            session: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "synthesize", [session])

    @jsii.member(jsii_name="toJsonString")
    def to_json_string(self, obj: typing.Any) -> str:
        """Convert an object, potentially containing tokens, to a JSON string.

        Arguments:
            obj: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJsonString", [obj])

    @property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> str:
        """The account in which this stack is defined.

        Either returns the literal account for this stack if it was specified
        literally upon Stack construction, or a symbolic value that will evaluate
        to the correct account at deployment time.

        Stability:
            experimental
        """
        return jsii.get(self, "accountId")

    @property
    @jsii.member(jsii_name="dependencies")
    def dependencies(self) -> typing.List["Stack"]:
        """Return the stacks this stack depends on.

        Stability:
            experimental
        """
        return jsii.get(self, "dependencies")

    @property
    @jsii.member(jsii_name="env")
    def env(self) -> "Environment":
        """The environment in which this stack is deployed.

        Stability:
            experimental
        """
        return jsii.get(self, "env")

    @property
    @jsii.member(jsii_name="environment")
    def environment(self) -> str:
        """Returns the environment specification for this stack (aws://account/region).

        Stability:
            experimental
        """
        return jsii.get(self, "environment")

    @property
    @jsii.member(jsii_name="logicalIds")
    def logical_ids(self) -> "LogicalIDs":
        """Logical ID generation strategy.

        Stability:
            experimental
        """
        return jsii.get(self, "logicalIds")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """The CloudFormation stack name.

        This is the stack name either configuration via the ``stackName`` property
        or automatically derived from the construct path.

        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @property
    @jsii.member(jsii_name="notificationArns")
    def notification_arns(self) -> typing.List[str]:
        """Returns the list of notification Amazon Resource Names (ARNs) for the current stack.

        Stability:
            experimental
        """
        return jsii.get(self, "notificationArns")

    @property
    @jsii.member(jsii_name="partition")
    def partition(self) -> str:
        """The partition in which this stack is defined.

        Stability:
            experimental
        """
        return jsii.get(self, "partition")

    @property
    @jsii.member(jsii_name="region")
    def region(self) -> str:
        """The region in which this stack is defined.

        Either returns the literal region for this stack if it was specified
        literally upon Stack construction, or a symbolic value that will evaluate
        to the correct region at deployment time.

        Stability:
            experimental
        """
        return jsii.get(self, "region")

    @property
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> str:
        """The ID of the stack.

        Stability:
            experimental

        Example::
            After resolving, looks like arn:aws:cloudformation:us-west-2:123456789012:stack/teststack/51af3dc0-da77-11e4-872e-1234567db123
        """
        return jsii.get(self, "stackId")

    @property
    @jsii.member(jsii_name="stackName")
    def stack_name(self) -> str:
        """The name of the stack currently being deployed.

        Only available at deployment time; this will always return an unresolved value.

        Stability:
            experimental
        """
        return jsii.get(self, "stackName")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "TagManager":
        """Tags to be applied to the stack.

        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="templateOptions")
    def template_options(self) -> "ITemplateOptions":
        """Options for CloudFormation template (like version, transform, description).

        Stability:
            experimental
        """
        return jsii.get(self, "templateOptions")

    @property
    @jsii.member(jsii_name="urlSuffix")
    def url_suffix(self) -> str:
        """The Amazon domain suffix for the region in which this stack is defined.

        Stability:
            experimental
        """
        return jsii.get(self, "urlSuffix")


@jsii.data_type(jsii_type="@aws-cdk/cdk.StackProps", jsii_struct_bases=[])
class StackProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    env: "Environment"
    """The AWS environment (account/region) where this stack will be deployed.

    Default:
        - The ``default-account`` and ``default-region`` context parameters will be
          used. If they are undefined, it will not be possible to deploy the stack.

    Stability:
        experimental
    """

    namingScheme: "IAddressingScheme"
    """Strategy for logical ID generation.

    Default:
        - The HashedNamingScheme will be used.

    Stability:
        experimental
    """

    stackName: str
    """Name to deploy the stack with.

    Default:
        - Derived from construct path.

    Stability:
        experimental
    """

    tags: typing.Mapping[str,str]
    """Stack tags that will be applied to all the taggable resources and the stack itself.

    Default:
        {}

    Stability:
        experimental
    """

@jsii.implements(IFragmentConcatenator)
class StringConcat(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.StringConcat"):
    """Converts all fragments to strings and concats those.

    Drops 'undefined's.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(StringConcat, self, [])

    @jsii.member(jsii_name="join")
    def join(self, left: typing.Any, right: typing.Any) -> typing.Any:
        """Join the fragment on the left and on the right.

        Arguments:
            left: -
            right: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "join", [left, right])


class StringListCfnOutput(Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.StringListCfnOutput"):
    """An output for a list of strings.

    Exports a list of Tokens via an CfnOutput variable, and return a list of Tokens
    that selects the imported values for them.

    Stability:
        experimental
    """
    def __init__(self, scope: "Construct", id: str, *, values: typing.List[typing.Any], condition: typing.Optional["CfnCondition"]=None, description: typing.Optional[str]=None, disable_export: typing.Optional[bool]=None, export: typing.Optional[str]=None, separator: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            values: The list of primitives to export.
            condition: A condition from the "Conditions" section to associate with this output value. If the condition evaluates to ``false``, this output value will not be included in the stack. Default: - None.
            description: A String type that describes the output value. The description can be a maximum of 4 K in length. Default: - No description.
            disableExport: Disables the automatic allocation of an export name for this output. Default: false, which means that an export name is either explicitly specified or allocated based on the output's logical ID and stack name.
            export: The name used to export the value of this output across stacks. To import the value from another stack, use ``FnImportValue(export)``. You can create an import value token by calling ``output.makeImportValue()``. Default: The default behavior is to automatically allocate an export name for outputs based on the stack name and the output's logical ID. To create an output without an export, set ``disableExport: true``.
            separator: The separator to use to separate stringified values. Default: ","

        Stability:
            experimental
        """
        props: StringListCfnOutputProps = {"values": values}

        if condition is not None:
            props["condition"] = condition

        if description is not None:
            props["description"] = description

        if disable_export is not None:
            props["disableExport"] = disable_export

        if export is not None:
            props["export"] = export

        if separator is not None:
            props["separator"] = separator

        jsii.create(StringListCfnOutput, self, [scope, id, props])

    @jsii.member(jsii_name="makeImportValues")
    def make_import_values(self) -> typing.List[str]:
        """Return an array of imported values for this CfnOutput.

        Stability:
            experimental
        """
        return jsii.invoke(self, "makeImportValues", [])

    @property
    @jsii.member(jsii_name="length")
    def length(self) -> jsii.Number:
        """Number of elements in the stringlist.

        Stability:
            experimental
        """
        return jsii.get(self, "length")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _StringListCfnOutputProps(jsii.compat.TypedDict, total=False):
    condition: "CfnCondition"
    """A condition from the "Conditions" section to associate with this output value.

    If the condition evaluates to ``false``, this output value will not
    be included in the stack.

    Default:
        - None.

    Stability:
        experimental
    """
    description: str
    """A String type that describes the output value. The description can be a maximum of 4 K in length.

    Default:
        - No description.

    Stability:
        experimental
    """
    disableExport: bool
    """Disables the automatic allocation of an export name for this output.

    Default:
        false, which means that an export name is either explicitly
        specified or allocated based on the output's logical ID and stack name.

    Stability:
        experimental
    """
    export: str
    """The name used to export the value of this output across stacks.

    To import
    the value from another stack, use ``FnImportValue(export)``. You can create
    an import value token by calling ``output.makeImportValue()``.

    Default:
        The default behavior is to automatically allocate an export name
        for outputs based on the stack name and the output's logical ID. To
        create an output without an export, set ``disableExport: true``.

    Stability:
        experimental
    """
    separator: str
    """The separator to use to separate stringified values.

    Default:
        ","

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.StringListCfnOutputProps", jsii_struct_bases=[_StringListCfnOutputProps])
class StringListCfnOutputProps(_StringListCfnOutputProps):
    """Properties for ListOutput.

    Stability:
        experimental
    """
    values: typing.List[typing.Any]
    """The list of primitives to export.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.SynthesisOptions", jsii_struct_bases=[aws_cdk.cx_api.AssemblyBuildOptions])
class SynthesisOptions(aws_cdk.cx_api.AssemblyBuildOptions, jsii.compat.TypedDict, total=False):
    """Options for synthesis.

    Stability:
        experimental
    """
    outdir: str
    """The output directory into which to synthesize the cloud assembly.

    Default:
        - creates a temporary directory

    Stability:
        experimental
    """

    skipValidation: bool
    """Whether synthesis should skip the validation phase.

    Default:
        false

    Stability:
        experimental
    """

@jsii.implements(IAspect)
class TagBase(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/cdk.TagBase"):
    """The common functionality for Tag and Remove Tag Aspects.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _TagBaseProxy

    def __init__(self, key: str, *, apply_to_launched_instances: typing.Optional[bool]=None, exclude_resource_types: typing.Optional[typing.List[str]]=None, include_resource_types: typing.Optional[typing.List[str]]=None, priority: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            key: -
            props: -
            applyToLaunchedInstances: Whether the tag should be applied to instances in an AutoScalingGroup. Default: true
            excludeResourceTypes: An array of Resource Types that will not receive this tag. An empty array will allow this tag to be applied to all resources. A non-empty array will apply this tag only if the Resource type is not in this array. Default: []
            includeResourceTypes: An array of Resource Types that will receive this tag. An empty array will match any Resource. A non-empty array will apply this tag only to Resource types that are included in this array. Default: []
            priority: Priority of the tag operation. Higher or equal priority tags will take precedence. Setting priority will enable the user to control tags when they need to not follow the default precedence pattern of last applied and closest to the construct in the tree. Default: Default priorities: - 100 for {@link SetTag} - 200 for {@link RemoveTag} - 50 for tags added directly to CloudFormation resources

        Stability:
            experimental
        """
        props: TagProps = {}

        if apply_to_launched_instances is not None:
            props["applyToLaunchedInstances"] = apply_to_launched_instances

        if exclude_resource_types is not None:
            props["excludeResourceTypes"] = exclude_resource_types

        if include_resource_types is not None:
            props["includeResourceTypes"] = include_resource_types

        if priority is not None:
            props["priority"] = priority

        jsii.create(TagBase, self, [key, props])

    @jsii.member(jsii_name="applyTag")
    @abc.abstractmethod
    def _apply_tag(self, resource: "ITaggable") -> None:
        """
        Arguments:
            resource: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="visit")
    def visit(self, construct: "IConstruct") -> None:
        """All aspects can visit an IConstruct.

        Arguments:
            construct: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "visit", [construct])

    @property
    @jsii.member(jsii_name="key")
    def key(self) -> str:
        """The string key for the tag.

        Stability:
            experimental
        """
        return jsii.get(self, "key")

    @property
    @jsii.member(jsii_name="props")
    def _props(self) -> "TagProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")


class _TagBaseProxy(TagBase):
    @jsii.member(jsii_name="applyTag")
    def _apply_tag(self, resource: "ITaggable") -> None:
        """
        Arguments:
            resource: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "applyTag", [resource])


class RemoveTag(TagBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.RemoveTag"):
    """The RemoveTag Aspect will handle removing tags from this node and children.

    Stability:
        experimental
    """
    def __init__(self, key: str, *, apply_to_launched_instances: typing.Optional[bool]=None, exclude_resource_types: typing.Optional[typing.List[str]]=None, include_resource_types: typing.Optional[typing.List[str]]=None, priority: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            key: -
            props: -
            applyToLaunchedInstances: Whether the tag should be applied to instances in an AutoScalingGroup. Default: true
            excludeResourceTypes: An array of Resource Types that will not receive this tag. An empty array will allow this tag to be applied to all resources. A non-empty array will apply this tag only if the Resource type is not in this array. Default: []
            includeResourceTypes: An array of Resource Types that will receive this tag. An empty array will match any Resource. A non-empty array will apply this tag only to Resource types that are included in this array. Default: []
            priority: Priority of the tag operation. Higher or equal priority tags will take precedence. Setting priority will enable the user to control tags when they need to not follow the default precedence pattern of last applied and closest to the construct in the tree. Default: Default priorities: - 100 for {@link SetTag} - 200 for {@link RemoveTag} - 50 for tags added directly to CloudFormation resources

        Stability:
            experimental
        """
        props: TagProps = {}

        if apply_to_launched_instances is not None:
            props["applyToLaunchedInstances"] = apply_to_launched_instances

        if exclude_resource_types is not None:
            props["excludeResourceTypes"] = exclude_resource_types

        if include_resource_types is not None:
            props["includeResourceTypes"] = include_resource_types

        if priority is not None:
            props["priority"] = priority

        jsii.create(RemoveTag, self, [key, props])

    @jsii.member(jsii_name="applyTag")
    def _apply_tag(self, resource: "ITaggable") -> None:
        """
        Arguments:
            resource: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "applyTag", [resource])


class Tag(TagBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.Tag"):
    """The Tag Aspect will handle adding a tag to this node and cascading tags to children.

    Stability:
        experimental
    """
    def __init__(self, key: str, value: str, *, apply_to_launched_instances: typing.Optional[bool]=None, exclude_resource_types: typing.Optional[typing.List[str]]=None, include_resource_types: typing.Optional[typing.List[str]]=None, priority: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            key: -
            value: -
            props: -
            applyToLaunchedInstances: Whether the tag should be applied to instances in an AutoScalingGroup. Default: true
            excludeResourceTypes: An array of Resource Types that will not receive this tag. An empty array will allow this tag to be applied to all resources. A non-empty array will apply this tag only if the Resource type is not in this array. Default: []
            includeResourceTypes: An array of Resource Types that will receive this tag. An empty array will match any Resource. A non-empty array will apply this tag only to Resource types that are included in this array. Default: []
            priority: Priority of the tag operation. Higher or equal priority tags will take precedence. Setting priority will enable the user to control tags when they need to not follow the default precedence pattern of last applied and closest to the construct in the tree. Default: Default priorities: - 100 for {@link SetTag} - 200 for {@link RemoveTag} - 50 for tags added directly to CloudFormation resources

        Stability:
            experimental
        """
        props: TagProps = {}

        if apply_to_launched_instances is not None:
            props["applyToLaunchedInstances"] = apply_to_launched_instances

        if exclude_resource_types is not None:
            props["excludeResourceTypes"] = exclude_resource_types

        if include_resource_types is not None:
            props["includeResourceTypes"] = include_resource_types

        if priority is not None:
            props["priority"] = priority

        jsii.create(Tag, self, [key, value, props])

    @jsii.member(jsii_name="applyTag")
    def _apply_tag(self, resource: "ITaggable") -> None:
        """
        Arguments:
            resource: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "applyTag", [resource])

    @property
    @jsii.member(jsii_name="value")
    def value(self) -> str:
        """The string value of the tag.

        Stability:
            experimental
        """
        return jsii.get(self, "value")


class TagManager(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.TagManager"):
    """TagManager facilitates a common implementation of tagging for Constructs.

    Stability:
        experimental
    """
    def __init__(self, tag_type: "TagType", resource_type_name: str, tag_structure: typing.Any=None) -> None:
        """
        Arguments:
            tagType: -
            resourceTypeName: -
            tagStructure: -

        Stability:
            experimental
        """
        jsii.create(TagManager, self, [tag_type, resource_type_name, tag_structure])

    @jsii.member(jsii_name="isTaggable")
    @classmethod
    def is_taggable(cls, construct: typing.Any) -> bool:
        """Check whether the given construct is Taggable.

        Arguments:
            construct: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "isTaggable", [construct])

    @jsii.member(jsii_name="applyTagAspectHere")
    def apply_tag_aspect_here(self, include: typing.Optional[typing.List[str]]=None, exclude: typing.Optional[typing.List[str]]=None) -> bool:
        """
        Arguments:
            include: -
            exclude: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "applyTagAspectHere", [include, exclude])

    @jsii.member(jsii_name="hasTags")
    def has_tags(self) -> bool:
        """Returns true if there are any tags defined.

        Stability:
            experimental
        """
        return jsii.invoke(self, "hasTags", [])

    @jsii.member(jsii_name="removeTag")
    def remove_tag(self, key: str, priority: jsii.Number) -> None:
        """Removes the specified tag from the array if it exists.

        Arguments:
            key: The tag to remove.
            priority: The priority of the remove operation.

        Stability:
            experimental
        """
        return jsii.invoke(self, "removeTag", [key, priority])

    @jsii.member(jsii_name="renderTags")
    def render_tags(self) -> typing.Any:
        """Renders tags into the proper format based on TagType.

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderTags", [])

    @jsii.member(jsii_name="setTag")
    def set_tag(self, key: str, value: str, priority: typing.Optional[jsii.Number]=None, apply_to_launched_instances: typing.Optional[bool]=None) -> None:
        """Adds the specified tag to the array of tags.

        Arguments:
            key: -
            value: -
            priority: -
            applyToLaunchedInstances: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "setTag", [key, value, priority, apply_to_launched_instances])


@jsii.data_type(jsii_type="@aws-cdk/cdk.TagProps", jsii_struct_bases=[])
class TagProps(jsii.compat.TypedDict, total=False):
    """Properties for a tag.

    Stability:
        experimental
    """
    applyToLaunchedInstances: bool
    """Whether the tag should be applied to instances in an AutoScalingGroup.

    Default:
        true

    Stability:
        experimental
    """

    excludeResourceTypes: typing.List[str]
    """An array of Resource Types that will not receive this tag.

    An empty array will allow this tag to be applied to all resources. A
    non-empty array will apply this tag only if the Resource type is not in
    this array.

    Default:
        []

    Stability:
        experimental
    """

    includeResourceTypes: typing.List[str]
    """An array of Resource Types that will receive this tag.

    An empty array will match any Resource. A non-empty array will apply this
    tag only to Resource types that are included in this array.

    Default:
        []

    Stability:
        experimental
    """

    priority: jsii.Number
    """Priority of the tag operation.

    Higher or equal priority tags will take precedence.

    Setting priority will enable the user to control tags when they need to not
    follow the default precedence pattern of last applied and closest to the
    construct in the tree.

    Default:
        Default priorities:
        
        - 100 for {@link SetTag}
        - 200 for {@link RemoveTag}
        - 50 for tags added directly to CloudFormation resources

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/cdk.TagType")
class TagType(enum.Enum):
    """
    Stability:
        experimental
    """
    Standard = "Standard"
    """
    Stability:
        experimental
    """
    AutoScalingGroup = "AutoScalingGroup"
    """
    Stability:
        experimental
    """
    Map = "Map"
    """
    Stability:
        experimental
    """
    KeyValue = "KeyValue"
    """
    Stability:
        experimental
    """
    NotTaggable = "NotTaggable"
    """
    Stability:
        experimental
    """

class Token(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.Token"):
    """Represents a special or lazily-evaluated value.

    Can be used to delay evaluation of a certain value in case, for example,
    that it requires some context or late-bound data. Can also be used to
    mark values that need special processing at document rendering time.

    Tokens can be embedded into strings while retaining their original
    semantics.

    Stability:
        experimental
    """
    def __init__(self, value_or_function: typing.Any=None, display_name: typing.Optional[str]=None) -> None:
        """Creates a token that resolves to ``value``.

        If value is a function, the function is evaluated upon resolution and
        the value it returns will be used as the token's value.

        displayName is used to represent the Token when it's embedded into a string; it
        will look something like this::

           "embedded in a larger string is ${Token[DISPLAY_NAME.123]}"

        This value is used as a hint to humans what the meaning of the Token is,
        and does not have any effect on the evaluation.

        Must contain only alphanumeric and simple separator characters (_.:-).

        Arguments:
            valueOrFunction: What this token will evaluate to, literal or function.
            displayName: A human-readable display hint for this Token.

        Stability:
            experimental
        """
        jsii.create(Token, self, [value_or_function, display_name])

    @jsii.member(jsii_name="isToken")
    @classmethod
    def is_token(cls, obj: typing.Any) -> bool:
        """Returns true if obj is a token (i.e. has the resolve() method or is a string or array which includes token markers).

        Arguments:
            obj: The object to test.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "isToken", [obj])

    @jsii.member(jsii_name="unresolved")
    @classmethod
    def unresolved(cls, obj: typing.Any) -> bool:
        """
        Arguments:
            obj: -

        Deprecated:
            use ``Token.isToken``

        Stability:
            deprecated
        """
        return jsii.sinvoke(cls, "unresolved", [obj])

    @jsii.member(jsii_name="newError")
    def _new_error(self, message: str) -> typing.Any:
        """Creates a throwable Error object that contains the token creation stack trace.

        Arguments:
            message: Error message.

        Stability:
            experimental
        """
        return jsii.invoke(self, "newError", [message])

    @jsii.member(jsii_name="resolve")
    def resolve(self, context: "IResolveContext") -> typing.Any:
        """
        Arguments:
            context: -

        Returns:
            The resolved value for this token.

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolve", [context])

    @jsii.member(jsii_name="toJSON")
    def to_json(self) -> typing.Any:
        """Turn this Token into JSON.

        This gets called by JSON.stringify(). We want to prohibit this, because
        it's not possible to do this properly, so we just throw an error here.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJSON", [])

    @jsii.member(jsii_name="toList")
    def to_list(self) -> typing.List[str]:
        """Return a string list representation of this token.

        Call this if the Token intrinsically evaluates to a list of strings.
        If so, you can represent the Token in a similar way in the type
        system.

        Note that even though the Token is represented as a list of strings, you
        still cannot do any operations on it such as concatenation, indexing,
        or taking its length. The only useful operations you can do to these lists
        is constructing a ``FnJoin`` or a ``FnSelect`` on it.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toList", [])

    @jsii.member(jsii_name="toNumber")
    def to_number(self) -> jsii.Number:
        """Return a floating point representation of this Token.

        Call this if the Token intrinsically resolves to something that represents
        a number, and you need to pass it into an API that expects a number.

        You may not do any operations on the returned value; any arithmetic or
        other operations can and probably will destroy the token-ness of the value.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toNumber", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Return a reversible string representation of this token.

        If the Token is initialized with a literal, the stringified value of the
        literal is returned. Otherwise, a special quoted string representation
        of the Token is returned that can be embedded into other strings.

        Strings with quoted Tokens in them can be restored back into
        complex values with the Tokens restored by calling ``resolve()``
        on the string.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="trace")
    def _trace(self) -> typing.List[str]:
        """The captured stack trace which represents the location in which this token was created.

        Stability:
            experimental
        """
        return jsii.get(self, "trace")

    @property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> typing.Optional[str]:
        """A human-readable display hint for this Token.

        Stability:
            experimental
        """
        return jsii.get(self, "displayName")

    @property
    @jsii.member(jsii_name="valueOrFunction")
    def value_or_function(self) -> typing.Any:
        """What this token will evaluate to, literal or function.

        Stability:
            experimental
        """
        return jsii.get(self, "valueOrFunction")


class CfnDynamicReference(Token, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.CfnDynamicReference"):
    """References a dynamically retrieved value.

    This is a Construct so that subclasses will (eventually) be able to attach
    metadata to themselves without having to change call signatures.

    See:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html
    Stability:
        experimental
    """
    def __init__(self, service: "CfnDynamicReferenceService", key: str) -> None:
        """
        Arguments:
            service: -
            key: -

        Stability:
            experimental
        """
        jsii.create(CfnDynamicReference, self, [service, key])


class Reference(Token, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.Reference"):
    """A Token that represents a reference between two constructs.

    References are recorded.

    Stability:
        experimental
    """
    def __init__(self, value: typing.Any, display_name: str, target: "Construct") -> None:
        """
        Arguments:
            value: -
            displayName: -
            target: -

        Stability:
            experimental
        """
        jsii.create(Reference, self, [value, display_name, target])

    @jsii.member(jsii_name="isReference")
    @classmethod
    def is_reference(cls, x: typing.Any) -> bool:
        """Check whether this is actually a Reference.

        Arguments:
            x: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "isReference", [x])

    @property
    @jsii.member(jsii_name="target")
    def target(self) -> "Construct":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "target")


class CfnReference(Reference, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.CfnReference"):
    """A Token that represents a CloudFormation reference to another resource.

    If these references are used in a different stack from where they are
    defined, appropriate CloudFormation ``Export``s and ``Fn::ImportValue``s will be
    synthesized automatically instead of the regular CloudFormation references.

    Additionally, the dependency between the stacks will be recorded, and the toolkit
    will make sure to deploy producing stack before the consuming stack.

    This magic happens in the prepare() phase, where consuming stacks will call
    ``consumeFromStack`` on these Tokens and if they happen to be exported by a different
    Stack, we'll register the dependency.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="for")
    @classmethod
    def for_(cls, target: "CfnRefElement", attribute: str) -> "CfnReference":
        """Return the CfnReference for the indicated target.

        Will make sure that multiple invocations for the same target and intrinsic
        return the same CfnReference. Because CfnReferences accumulate state in
        the prepare() phase (for the purpose of cross-stack references), it's
        important that the state isn't lost if it's lazily created, like so::

            new Token(() => new CfnReference(...))

        Arguments:
            target: -
            attribute: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "for", [target, attribute])

    @jsii.member(jsii_name="forPseudo")
    @classmethod
    def for_pseudo(cls, pseudo_name: str, scope: "Construct") -> "CfnReference":
        """Return a CfnReference that references a pseudo referencd.

        Arguments:
            pseudoName: -
            scope: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "forPseudo", [pseudo_name, scope])

    @jsii.member(jsii_name="isCfnReference")
    @classmethod
    def is_cfn_reference(cls, x: "Token") -> bool:
        """Check whether this is actually a Reference.

        Arguments:
            x: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "isCfnReference", [x])

    @jsii.member(jsii_name="consumeFromStack")
    def consume_from_stack(self, consuming_stack: "Stack", consuming_construct: "IConstruct") -> None:
        """Register a stack this references is being consumed from.

        Arguments:
            consumingStack: -
            consumingConstruct: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "consumeFromStack", [consuming_stack, consuming_construct])

    @jsii.member(jsii_name="resolve")
    def resolve(self, context: "IResolveContext") -> typing.Any:
        """
        Arguments:
            context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolve", [context])


class SecretValue(Token, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.SecretValue"):
    """Work with secret values in the CDK.

    Secret values in the CDK (such as those retrieved from SecretsManager) are
    represented as regular strings, just like other values that are only
    available at deployment time.

    To help you avoid accidental mistakes which would lead to you putting your
    secret values directly into a CloudFormation template, constructs that take
    secret values will not allow you to pass in a literal secret value. They do
    so by calling ``Secret.assertSafeSecret()``.

    You can escape the check by calling ``Secret.plainTex()``, but doing
    so is highly discouraged.

    Stability:
        experimental
    """
    def __init__(self, value_or_function: typing.Any=None, display_name: typing.Optional[str]=None) -> None:
        """Creates a token that resolves to ``value``.

        If value is a function, the function is evaluated upon resolution and
        the value it returns will be used as the token's value.

        displayName is used to represent the Token when it's embedded into a string; it
        will look something like this::

           "embedded in a larger string is ${Token[DISPLAY_NAME.123]}"

        This value is used as a hint to humans what the meaning of the Token is,
        and does not have any effect on the evaluation.

        Must contain only alphanumeric and simple separator characters (_.:-).

        Arguments:
            valueOrFunction: What this token will evaluate to, literal or function.
            displayName: A human-readable display hint for this Token.

        Stability:
            experimental
        """
        jsii.create(SecretValue, self, [value_or_function, display_name])

    @jsii.member(jsii_name="cfnDynamicReference")
    @classmethod
    def cfn_dynamic_reference(cls, ref: "CfnDynamicReference") -> "SecretValue":
        """Obtain the secret value through a CloudFormation dynamic reference.

        If possible, use ``SecretValue.ssmSecure`` or ``SecretValue.secretsManager`` directly.

        Arguments:
            ref: The dynamic reference to use.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "cfnDynamicReference", [ref])

    @jsii.member(jsii_name="cfnParameter")
    @classmethod
    def cfn_parameter(cls, param: "CfnParameter") -> "SecretValue":
        """Obtain the secret value through a CloudFormation parameter.

        Generally, this is not a recommended approach. AWS Secrets Manager is the
        recommended way to reference secrets.

        Arguments:
            param: The CloudFormation parameter to use.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "cfnParameter", [param])

    @jsii.member(jsii_name="plainText")
    @classmethod
    def plain_text(cls, secret: str) -> "SecretValue":
        """Construct a literal secret value for use with secret-aware constructs.

        *Do not use this method for any secrets that you care about.*

        The only reasonable use case for using this method is when you are testing.

        Arguments:
            secret: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "plainText", [secret])

    @jsii.member(jsii_name="secretsManager")
    @classmethod
    def secrets_manager(cls, secret_id: str, *, json_field: typing.Optional[str]=None, version_id: typing.Optional[str]=None, version_stage: typing.Optional[str]=None) -> "SecretValue":
        """Creates a ``SecretValue`` with a value which is dynamically loaded from AWS Secrets Manager.

        Arguments:
            secretId: The ID or ARN of the secret.
            options: Options.
            jsonField: The key of a JSON field to retrieve. This can only be used if the secret stores a JSON object. Default: - returns all the content stored in the Secrets Manager secret.
            versionId: Specifies the unique identifier of the version of the secret you want to use. Can specify at most one of ``versionId`` and ``versionStage``. Default: AWSCURRENT
            versionStage: Specified the secret version that you want to retrieve by the staging label attached to the version. Can specify at most one of ``versionId`` and ``versionStage``. Default: AWSCURRENT

        Stability:
            experimental
        """
        options: SecretsManagerSecretOptions = {}

        if json_field is not None:
            options["jsonField"] = json_field

        if version_id is not None:
            options["versionId"] = version_id

        if version_stage is not None:
            options["versionStage"] = version_stage

        return jsii.sinvoke(cls, "secretsManager", [secret_id, options])

    @jsii.member(jsii_name="ssmSecure")
    @classmethod
    def ssm_secure(cls, parameter_name: str, version: str) -> "SecretValue":
        """Use a secret value stored from a Systems Manager (SSM) parameter.

        Arguments:
            parameterName: The name of the parameter in the Systems Manager Parameter Store. The parameter name is case-sensitive.
            version: An integer that specifies the version of the parameter to use. You must specify the exact version. You cannot currently specify that AWS CloudFormation use the latest version of a parameter.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "ssmSecure", [parameter_name, version])


class TokenMap(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.TokenMap"):
    """Central place where we keep a mapping from Tokens to their String representation.

    The string representation is used to embed token into strings,
    and stored to be able to reverse that mapping.

    All instances of TokenStringMap share the same storage, so that this process
    works even when different copies of the library are loaded.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(TokenMap, self, [])

    @jsii.member(jsii_name="instance")
    @classmethod
    def instance(cls) -> "TokenMap":
        """Singleton instance of the token string map.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "instance", [])

    @jsii.member(jsii_name="lookupList")
    def lookup_list(self, xs: typing.List[str]) -> typing.Optional["Token"]:
        """Reverse a string representation into a Token object.

        Arguments:
            xs: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "lookupList", [xs])

    @jsii.member(jsii_name="lookupNumberToken")
    def lookup_number_token(self, x: jsii.Number) -> typing.Optional["Token"]:
        """Reverse a number encoding into a Token, or undefined if the number wasn't a Token.

        Arguments:
            x: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "lookupNumberToken", [x])

    @jsii.member(jsii_name="lookupString")
    def lookup_string(self, s: str) -> typing.Optional["Token"]:
        """Reverse a string representation into a Token object.

        Arguments:
            s: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "lookupString", [s])

    @jsii.member(jsii_name="lookupToken")
    def lookup_token(self, key: str) -> "Token":
        """Find a Token by key.

        This excludes the token markers.

        Arguments:
            key: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "lookupToken", [key])

    @jsii.member(jsii_name="registerList")
    def register_list(self, token: "Token", representation_hint: typing.Optional[str]=None) -> typing.List[str]:
        """Generate a unique string for this Token, returning a key.

        Arguments:
            token: -
            representationHint: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "registerList", [token, representation_hint])

    @jsii.member(jsii_name="registerNumber")
    def register_number(self, token: "Token") -> jsii.Number:
        """Create a unique number representation for this Token and return it.

        Arguments:
            token: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "registerNumber", [token])

    @jsii.member(jsii_name="registerString")
    def register_string(self, token: "Token", representation_hint: typing.Optional[str]=None) -> str:
        """Generate a unique string for this Token, returning a key.

        Every call for the same Token will produce a new unique string, no
        attempt is made to deduplicate. Token objects should cache the
        value themselves, if required.

        The token can choose (part of) its own representation string with a
        hint. This may be used to produce aesthetically pleasing and
        recognizable token representations for humans.

        Arguments:
            token: -
            representationHint: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "registerString", [token, representation_hint])

    @jsii.member(jsii_name="splitString")
    def split_string(self, s: str) -> "TokenizedStringFragments":
        """Split a string into literals and Tokens.

        Arguments:
            s: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "splitString", [s])

    @jsii.member(jsii_name="tokenFromEncoding")
    def token_from_encoding(self, x: typing.Any) -> typing.Optional["Token"]:
        """Lookup a token from an encoded value.

        Arguments:
            x: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "tokenFromEncoding", [x])


class TokenizedStringFragments(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.TokenizedStringFragments"):
    """Fragments of a concatenated string containing stringified Tokens.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(TokenizedStringFragments, self, [])

    @jsii.member(jsii_name="addIntrinsic")
    def add_intrinsic(self, value: typing.Any) -> None:
        """
        Arguments:
            value: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addIntrinsic", [value])

    @jsii.member(jsii_name="addLiteral")
    def add_literal(self, lit: typing.Any) -> None:
        """
        Arguments:
            lit: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addLiteral", [lit])

    @jsii.member(jsii_name="addToken")
    def add_token(self, token: "Token") -> None:
        """
        Arguments:
            token: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToken", [token])

    @jsii.member(jsii_name="join")
    def join(self, concat: "IFragmentConcatenator") -> typing.Any:
        """Combine the string fragments using the given joiner.

        If there are any

        Arguments:
            concat: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "join", [concat])

    @jsii.member(jsii_name="mapTokens")
    def map_tokens(self, mapper: "ITokenMapper") -> "TokenizedStringFragments":
        """Apply a transformation function to all tokens in the string.

        Arguments:
            mapper: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "mapTokens", [mapper])

    @property
    @jsii.member(jsii_name="firstValue")
    def first_value(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "firstValue")

    @property
    @jsii.member(jsii_name="length")
    def length(self) -> jsii.Number:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "length")

    @property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> typing.List["Token"]:
        """Return all Tokens from this string.

        Stability:
            experimental
        """
        return jsii.get(self, "tokens")

    @property
    @jsii.member(jsii_name="firstToken")
    def first_token(self) -> typing.Optional["Token"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "firstToken")


@jsii.data_type(jsii_type="@aws-cdk/cdk.UpdatePolicy", jsii_struct_bases=[])
class UpdatePolicy(jsii.compat.TypedDict, total=False):
    """Use the UpdatePolicy attribute to specify how AWS CloudFormation handles updates to the AWS::AutoScaling::AutoScalingGroup resource.

    AWS CloudFormation invokes one of three update policies depending on the type of change you make or whether a
    scheduled action is associated with the Auto Scaling group.

    Stability:
        experimental
    """
    autoScalingReplacingUpdate: "AutoScalingReplacingUpdate"
    """Specifies whether an Auto Scaling group and the instances it contains are replaced during an update.

    During replacement,
    AWS CloudFormation retains the old group until it finishes creating the new one. If the update fails, AWS CloudFormation
    can roll back to the old Auto Scaling group and delete the new Auto Scaling group.

    Stability:
        experimental
    """

    autoScalingRollingUpdate: "AutoScalingRollingUpdate"
    """To specify how AWS CloudFormation handles rolling updates for an Auto Scaling group, use the AutoScalingRollingUpdate policy.

    Rolling updates enable you to specify whether AWS CloudFormation updates instances that are in an Auto Scaling
    group in batches or all at once.

    Stability:
        experimental
    """

    autoScalingScheduledAction: "AutoScalingScheduledAction"
    """To specify how AWS CloudFormation handles updates for the MinSize, MaxSize, and DesiredCapacity properties when the AWS::AutoScaling::AutoScalingGroup resource has an associated scheduled action, use the AutoScalingScheduledAction policy.

    Stability:
        experimental
    """

    codeDeployLambdaAliasUpdate: "CodeDeployLambdaAliasUpdate"
    """To perform an AWS CodeDeploy deployment when the version changes on an AWS::Lambda::Alias resource, use the CodeDeployLambdaAliasUpdate update policy.

    Stability:
        experimental
    """

    useOnlineResharding: bool
    """To modify a replication group's shards by adding or removing shards, rather than replacing the entire AWS::ElastiCache::ReplicationGroup resource, use the UseOnlineResharding update policy.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/cdk.ValidationError", jsii_struct_bases=[])
class ValidationError(jsii.compat.TypedDict):
    """An error returned during the validation phase.

    Stability:
        experimental
    """
    message: str
    """The error message.

    Stability:
        experimental
    """

    source: "Construct"
    """The construct which emitted the error.

    Stability:
        experimental
    """

class ValidationResult(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.ValidationResult"):
    """Representation of validation results.

    Models a tree of validation errors so that we have as much information as possible
    about the failure that occurred.

    Stability:
        experimental
    """
    def __init__(self, error_message: typing.Optional[str]=None, results: typing.Optional["ValidationResults"]=None) -> None:
        """
        Arguments:
            errorMessage: -
            results: -

        Stability:
            experimental
        """
        jsii.create(ValidationResult, self, [error_message, results])

    @jsii.member(jsii_name="assertSuccess")
    def assert_success(self) -> None:
        """Turn a failed validation into an exception.

        Stability:
            experimental
        """
        return jsii.invoke(self, "assertSuccess", [])

    @jsii.member(jsii_name="errorTree")
    def error_tree(self) -> str:
        """Return a string rendering of the tree of validation failures.

        Stability:
            experimental
        """
        return jsii.invoke(self, "errorTree", [])

    @jsii.member(jsii_name="prefix")
    def prefix(self, message: str) -> "ValidationResult":
        """Wrap this result with an error message, if it concerns an error.

        Arguments:
            message: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "prefix", [message])

    @property
    @jsii.member(jsii_name="errorMessage")
    def error_message(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "errorMessage")

    @property
    @jsii.member(jsii_name="isSuccess")
    def is_success(self) -> bool:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "isSuccess")

    @property
    @jsii.member(jsii_name="results")
    def results(self) -> "ValidationResults":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "results")


class ValidationResults(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/cdk.ValidationResults"):
    """A collection of validation results.

    Stability:
        experimental
    """
    def __init__(self, results: typing.Optional[typing.List["ValidationResult"]]=None) -> None:
        """
        Arguments:
            results: -

        Stability:
            experimental
        """
        jsii.create(ValidationResults, self, [results])

    @jsii.member(jsii_name="collect")
    def collect(self, result: "ValidationResult") -> None:
        """
        Arguments:
            result: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "collect", [result])

    @jsii.member(jsii_name="errorTreeList")
    def error_tree_list(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "errorTreeList", [])

    @jsii.member(jsii_name="wrap")
    def wrap(self, message: str) -> "ValidationResult":
        """Wrap up all validation results into a single tree node.

        If there are failures in the collection, add a message, otherwise
        return a success.

        Arguments:
            message: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "wrap", [message])

    @property
    @jsii.member(jsii_name="isSuccess")
    def is_success(self) -> bool:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "isSuccess")

    @property
    @jsii.member(jsii_name="results")
    def results(self) -> typing.List["ValidationResult"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "results")

    @results.setter
    def results(self, value: typing.List["ValidationResult"]):
        return jsii.set(self, "results", value)


__all__ = ["App", "AppProps", "ArnComponents", "AutoScalingCreationPolicy", "AutoScalingReplacingUpdate", "AutoScalingRollingUpdate", "AutoScalingScheduledAction", "AvailabilityZoneProvider", "Aws", "CfnCondition", "CfnConditionProps", "CfnDynamicReference", "CfnDynamicReferenceService", "CfnElement", "CfnMapping", "CfnMappingProps", "CfnOutput", "CfnOutputProps", "CfnParameter", "CfnParameterProps", "CfnRefElement", "CfnReference", "CfnResource", "CfnResourceProps", "CfnRule", "CfnRuleProps", "CfnTag", "CodeDeployLambdaAliasUpdate", "ConcreteDependable", "Construct", "ConstructNode", "ConstructOrder", "ContextProvider", "CreationPolicy", "DefaultTokenResolver", "DeletionPolicy", "DependableTrait", "Dependency", "DynamicReferenceProps", "Environment", "Fn", "HashedAddressingScheme", "IAddressingScheme", "IAspect", "ICfnConditionExpression", "IConstruct", "IDependable", "IFragmentConcatenator", "IResolveContext", "IResolveOptions", "IResolvedValuePostProcessor", "IResource", "IResourceOptions", "ISynthesisSession", "ITaggable", "ITemplateOptions", "ITokenMapper", "ITokenResolver", "Include", "IncludeProps", "LogicalIDs", "OutgoingReference", "Reference", "RememberingTokenResolver", "RemovalPolicy", "RemoveTag", "Resource", "ResourceSignal", "RuleAssertion", "SSMParameterProvider", "SSMParameterProviderProps", "ScopedAws", "SecretValue", "SecretsManagerSecretOptions", "Stack", "StackProps", "StringConcat", "StringListCfnOutput", "StringListCfnOutputProps", "SynthesisOptions", "Tag", "TagBase", "TagManager", "TagProps", "TagType", "Token", "TokenMap", "TokenizedStringFragments", "UpdatePolicy", "ValidationError", "ValidationResult", "ValidationResults", "__jsii_assembly__"]

publication.publish()
