import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_cloudwatch
import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-stepfunctions", "0.34.0", __name__, "aws-stepfunctions@0.34.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.ActivityProps", jsii_struct_bases=[])
class ActivityProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    activityName: str
    """The name for this activity.

    Default:
        If not supplied, a name is generated

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.AfterwardsOptions", jsii_struct_bases=[])
class AfterwardsOptions(jsii.compat.TypedDict, total=False):
    """Options for selecting the choice paths.

    Stability:
        experimental
    """
    includeErrorHandlers: bool
    """Whether to include error handling states.

    If this is true, all states which are error handlers (added through 'onError')
    and states reachable via error handlers will be included as well.

    Default:
        false

    Stability:
        experimental
    """

    includeOtherwise: bool
    """Whether to include the default/otherwise transition for the current Choice state.

    If this is true and the current Choice does not have a default outgoing
    transition, one will be added included when .next() is called on the chain.

    Default:
        false

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.CatchProps", jsii_struct_bases=[])
class CatchProps(jsii.compat.TypedDict, total=False):
    """Error handler details.

    Stability:
        experimental
    """
    errors: typing.List[str]
    """Errors to recover from by going to the given state.

    A list of error strings to retry, which can be either predefined errors
    (for example Errors.NoChoiceMatched) or a self-defined error.

    Default:
        All errors

    Stability:
        experimental
    """

    resultPath: str
    """JSONPath expression to indicate where to inject the error data.

    May also be the special value DISCARD, which will cause the error
    data to be discarded.

    Default:
        $

    Stability:
        experimental
    """

class CfnActivity(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.CfnActivity"):
    """A CloudFormation ``AWS::StepFunctions::Activity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-activity.html
    Stability:
        experimental
    cloudformationResource:
        AWS::StepFunctions::Activity
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, tags: typing.Optional[typing.List["TagsEntryProperty"]]=None) -> None:
        """Create a new ``AWS::StepFunctions::Activity``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::StepFunctions::Activity.Name``.
            tags: ``AWS::StepFunctions::Activity.Tags``.

        Stability:
            experimental
        """
        props: CfnActivityProps = {"name": name}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnActivity, self, [scope, id, props])

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
    @jsii.member(jsii_name="activityArn")
    def activity_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "activityArn")

    @property
    @jsii.member(jsii_name="activityName")
    def activity_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "activityName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnActivityProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.CfnActivity.TagsEntryProperty", jsii_struct_bases=[])
    class TagsEntryProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-activity-tagsentry.html
        Stability:
            experimental
        """
        key: str
        """``CfnActivity.TagsEntryProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-activity-tagsentry.html#cfn-stepfunctions-activity-tagsentry-key
        Stability:
            experimental
        """

        value: str
        """``CfnActivity.TagsEntryProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-activity-tagsentry.html#cfn-stepfunctions-activity-tagsentry-value
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnActivityProps(jsii.compat.TypedDict, total=False):
    tags: typing.List["CfnActivity.TagsEntryProperty"]
    """``AWS::StepFunctions::Activity.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-activity.html#cfn-stepfunctions-activity-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.CfnActivityProps", jsii_struct_bases=[_CfnActivityProps])
class CfnActivityProps(_CfnActivityProps):
    """Properties for defining a ``AWS::StepFunctions::Activity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-activity.html
    Stability:
        experimental
    """
    name: str
    """``AWS::StepFunctions::Activity.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-activity.html#cfn-stepfunctions-activity-name
    Stability:
        experimental
    """

class CfnStateMachine(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.CfnStateMachine"):
    """A CloudFormation ``AWS::StepFunctions::StateMachine``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html
    Stability:
        experimental
    cloudformationResource:
        AWS::StepFunctions::StateMachine
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, definition_string: str, role_arn: str, state_machine_name: typing.Optional[str]=None, tags: typing.Optional[typing.List["TagsEntryProperty"]]=None) -> None:
        """Create a new ``AWS::StepFunctions::StateMachine``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            definitionString: ``AWS::StepFunctions::StateMachine.DefinitionString``.
            roleArn: ``AWS::StepFunctions::StateMachine.RoleArn``.
            stateMachineName: ``AWS::StepFunctions::StateMachine.StateMachineName``.
            tags: ``AWS::StepFunctions::StateMachine.Tags``.

        Stability:
            experimental
        """
        props: CfnStateMachineProps = {"definitionString": definition_string, "roleArn": role_arn}

        if state_machine_name is not None:
            props["stateMachineName"] = state_machine_name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnStateMachine, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnStateMachineProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="stateMachineArn")
    def state_machine_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "stateMachineArn")

    @property
    @jsii.member(jsii_name="stateMachineName")
    def state_machine_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "stateMachineName")

    @jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.CfnStateMachine.TagsEntryProperty", jsii_struct_bases=[])
    class TagsEntryProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-tagsentry.html
        Stability:
            experimental
        """
        key: str
        """``CfnStateMachine.TagsEntryProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-tagsentry.html#cfn-stepfunctions-statemachine-tagsentry-key
        Stability:
            experimental
        """

        value: str
        """``CfnStateMachine.TagsEntryProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-tagsentry.html#cfn-stepfunctions-statemachine-tagsentry-value
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnStateMachineProps(jsii.compat.TypedDict, total=False):
    stateMachineName: str
    """``AWS::StepFunctions::StateMachine.StateMachineName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-statemachinename
    Stability:
        experimental
    """
    tags: typing.List["CfnStateMachine.TagsEntryProperty"]
    """``AWS::StepFunctions::StateMachine.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.CfnStateMachineProps", jsii_struct_bases=[_CfnStateMachineProps])
class CfnStateMachineProps(_CfnStateMachineProps):
    """Properties for defining a ``AWS::StepFunctions::StateMachine``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html
    Stability:
        experimental
    """
    definitionString: str
    """``AWS::StepFunctions::StateMachine.DefinitionString``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-definitionstring
    Stability:
        experimental
    """

    roleArn: str
    """``AWS::StepFunctions::StateMachine.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-rolearn
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.ChoiceProps", jsii_struct_bases=[])
class ChoiceProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a Choice state.

    Stability:
        experimental
    """
    comment: str
    """An optional description for this state.

    Default:
        No comment

    Stability:
        experimental
    """

    inputPath: str
    """JSONPath expression to select part of the state to be the input to this state.

    May also be the special value DISCARD, which will cause the effective
    input to be the empty object {}.

    Default:
        $

    Stability:
        experimental
    """

    outputPath: str
    """JSONPath expression to select part of the state to be the output to this state.

    May also be the special value DISCARD, which will cause the effective
    output to be the empty object {}.

    Default:
        $

    Stability:
        experimental
    """

class Condition(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-stepfunctions.Condition"):
    """A Condition for use in a Choice state branch.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ConditionProxy

    def __init__(self) -> None:
        jsii.create(Condition, self, [])

    @jsii.member(jsii_name="and")
    @classmethod
    def and_(cls, *conditions: "Condition") -> "Condition":
        """Combine two or more conditions with a logical AND.

        Arguments:
            conditions: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "and", [*conditions])

    @jsii.member(jsii_name="booleanEquals")
    @classmethod
    def boolean_equals(cls, variable: str, value: bool) -> "Condition":
        """Matches if a boolean field has the given value.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "booleanEquals", [variable, value])

    @jsii.member(jsii_name="not")
    @classmethod
    def not_(cls, condition: "Condition") -> "Condition":
        """Negate a condition.

        Arguments:
            condition: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "not", [condition])

    @jsii.member(jsii_name="numberEquals")
    @classmethod
    def number_equals(cls, variable: str, value: jsii.Number) -> "Condition":
        """Matches if a numeric field has the given value.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "numberEquals", [variable, value])

    @jsii.member(jsii_name="numberGreaterThan")
    @classmethod
    def number_greater_than(cls, variable: str, value: jsii.Number) -> "Condition":
        """Matches if a numeric field is greater than the given value.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "numberGreaterThan", [variable, value])

    @jsii.member(jsii_name="numberGreaterThanEquals")
    @classmethod
    def number_greater_than_equals(cls, variable: str, value: jsii.Number) -> "Condition":
        """Matches if a numeric field is greater than or equal to the given value.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "numberGreaterThanEquals", [variable, value])

    @jsii.member(jsii_name="numberLessThan")
    @classmethod
    def number_less_than(cls, variable: str, value: jsii.Number) -> "Condition":
        """Matches if a numeric field is less than the given value.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "numberLessThan", [variable, value])

    @jsii.member(jsii_name="numberLessThanEquals")
    @classmethod
    def number_less_than_equals(cls, variable: str, value: jsii.Number) -> "Condition":
        """Matches if a numeric field is less than or equal to the given value.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "numberLessThanEquals", [variable, value])

    @jsii.member(jsii_name="or")
    @classmethod
    def or_(cls, *conditions: "Condition") -> "Condition":
        """Combine two or more conditions with a logical OR.

        Arguments:
            conditions: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "or", [*conditions])

    @jsii.member(jsii_name="stringEquals")
    @classmethod
    def string_equals(cls, variable: str, value: str) -> "Condition":
        """Matches if a string field has the given value.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "stringEquals", [variable, value])

    @jsii.member(jsii_name="stringGreaterThan")
    @classmethod
    def string_greater_than(cls, variable: str, value: str) -> "Condition":
        """Matches if a string field sorts after a given value.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "stringGreaterThan", [variable, value])

    @jsii.member(jsii_name="stringGreaterThanEquals")
    @classmethod
    def string_greater_than_equals(cls, variable: str, value: str) -> "Condition":
        """Matches if a string field sorts after or equal to a given value.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "stringGreaterThanEquals", [variable, value])

    @jsii.member(jsii_name="stringLessThan")
    @classmethod
    def string_less_than(cls, variable: str, value: str) -> "Condition":
        """Matches if a string field sorts before a given value.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "stringLessThan", [variable, value])

    @jsii.member(jsii_name="stringLessThanEquals")
    @classmethod
    def string_less_than_equals(cls, variable: str, value: str) -> "Condition":
        """Matches if a string field sorts equal to or before a given value.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "stringLessThanEquals", [variable, value])

    @jsii.member(jsii_name="timestampEquals")
    @classmethod
    def timestamp_equals(cls, variable: str, value: str) -> "Condition":
        """Matches if a timestamp field is the same time as the given timestamp.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "timestampEquals", [variable, value])

    @jsii.member(jsii_name="timestampGreaterThan")
    @classmethod
    def timestamp_greater_than(cls, variable: str, value: str) -> "Condition":
        """Matches if a timestamp field is after the given timestamp.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "timestampGreaterThan", [variable, value])

    @jsii.member(jsii_name="timestampGreaterThanEquals")
    @classmethod
    def timestamp_greater_than_equals(cls, variable: str, value: str) -> "Condition":
        """Matches if a timestamp field is after or equal to the given timestamp.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "timestampGreaterThanEquals", [variable, value])

    @jsii.member(jsii_name="timestampLessThan")
    @classmethod
    def timestamp_less_than(cls, variable: str, value: str) -> "Condition":
        """Matches if a timestamp field is before the given timestamp.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "timestampLessThan", [variable, value])

    @jsii.member(jsii_name="timestampLessThanEquals")
    @classmethod
    def timestamp_less_than_equals(cls, variable: str, value: str) -> "Condition":
        """Matches if a timestamp field is before or equal to the given timestamp.

        Arguments:
            variable: -
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "timestampLessThanEquals", [variable, value])

    @jsii.member(jsii_name="renderCondition")
    @abc.abstractmethod
    def render_condition(self) -> typing.Any:
        """Render Amazon States Language JSON for the condition.

        Stability:
            experimental
        """
        ...


class _ConditionProxy(Condition):
    @jsii.member(jsii_name="renderCondition")
    def render_condition(self) -> typing.Any:
        """Render Amazon States Language JSON for the condition.

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderCondition", [])


class Context(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Context"):
    """Extract a field from the State Machine Context data.

    See:
        https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html#wait-token-contextobject
    Stability:
        experimental
    """
    @jsii.member(jsii_name="numberAt")
    @classmethod
    def number_at(cls, path: str) -> jsii.Number:
        """Instead of using a literal number, get the value from a JSON path.

        Arguments:
            path: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "numberAt", [path])

    @jsii.member(jsii_name="stringAt")
    @classmethod
    def string_at(cls, path: str) -> str:
        """Instead of using a literal string, get the value from a JSON path.

        Arguments:
            path: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "stringAt", [path])

    @classproperty
    @jsii.member(jsii_name="entireContext")
    def entire_context(cls) -> str:
        """Use the entire context data structure.

        Will be an object at invocation time, but is represented in the CDK
        application as a string.

        Stability:
            experimental
        """
        return jsii.sget(cls, "entireContext")

    @classproperty
    @jsii.member(jsii_name="taskToken")
    def task_token(cls) -> str:
        """Return the Task Token field.

        External actions will need this token to report step completion
        back to StepFunctions using the ``SendTaskSuccess`` or ``SendTaskFailure``
        calls.

        Stability:
            experimental
        """
        return jsii.sget(cls, "taskToken")


class Data(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Data"):
    """Extract a field from the State Machine data that gets passed around between states.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="listAt")
    @classmethod
    def list_at(cls, path: str) -> typing.List[str]:
        """Instead of using a literal string list, get the value from a JSON path.

        Arguments:
            path: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "listAt", [path])

    @jsii.member(jsii_name="numberAt")
    @classmethod
    def number_at(cls, path: str) -> jsii.Number:
        """Instead of using a literal number, get the value from a JSON path.

        Arguments:
            path: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "numberAt", [path])

    @jsii.member(jsii_name="stringAt")
    @classmethod
    def string_at(cls, path: str) -> str:
        """Instead of using a literal string, get the value from a JSON path.

        Arguments:
            path: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "stringAt", [path])

    @classproperty
    @jsii.member(jsii_name="entirePayload")
    def entire_payload(cls) -> str:
        """Use the entire data structure.

        Will be an object at invocation time, but is represented in the CDK
        application as a string.

        Stability:
            experimental
        """
        return jsii.sget(cls, "entirePayload")


class Errors(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Errors"):
    """Predefined error strings.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(Errors, self, [])

    @classproperty
    @jsii.member(jsii_name="All")
    def ALL(cls) -> str:
        """Matches any Error.

        Stability:
            experimental
        """
        return jsii.sget(cls, "All")

    @classproperty
    @jsii.member(jsii_name="BranchFailed")
    def BRANCH_FAILED(cls) -> str:
        """A branch of a Parallel state failed.

        Stability:
            experimental
        """
        return jsii.sget(cls, "BranchFailed")

    @classproperty
    @jsii.member(jsii_name="NoChoiceMatched")
    def NO_CHOICE_MATCHED(cls) -> str:
        """A Choice state failed to find a match for the condition field extracted from its input.

        Stability:
            experimental
        """
        return jsii.sget(cls, "NoChoiceMatched")

    @classproperty
    @jsii.member(jsii_name="Permissions")
    def PERMISSIONS(cls) -> str:
        """A Task State failed because it had insufficient privileges to execute the specified code.

        Stability:
            experimental
        """
        return jsii.sget(cls, "Permissions")

    @classproperty
    @jsii.member(jsii_name="ResultPathMatchFailure")
    def RESULT_PATH_MATCH_FAILURE(cls) -> str:
        """A Task State’s “ResultPath” field cannot be applied to the input the state received.

        Stability:
            experimental
        """
        return jsii.sget(cls, "ResultPathMatchFailure")

    @classproperty
    @jsii.member(jsii_name="TaskFailed")
    def TASK_FAILED(cls) -> str:
        """A Task State failed during the execution.

        Stability:
            experimental
        """
        return jsii.sget(cls, "TaskFailed")

    @classproperty
    @jsii.member(jsii_name="Timeout")
    def TIMEOUT(cls) -> str:
        """A Task State either ran longer than the “TimeoutSeconds” value, or failed to heartbeat for a time longer than the “HeartbeatSeconds” value.

        Stability:
            experimental
        """
        return jsii.sget(cls, "Timeout")


@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.FailProps", jsii_struct_bases=[])
class FailProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a Fail state.

    Stability:
        experimental
    """
    cause: str
    """A description for the cause of the failure.

    Default:
        No description

    Stability:
        experimental
    """

    comment: str
    """An optional description for this state.

    Default:
        No comment

    Stability:
        experimental
    """

    error: str
    """Error code used to represent this failure.

    Default:
        No error code

    Stability:
        experimental
    """

class FieldUtils(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.FieldUtils"):
    """Helper functions to work with structures containing fields.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="containsTaskToken")
    @classmethod
    def contains_task_token(cls, obj: typing.Optional[typing.Mapping[str,typing.Any]]=None) -> bool:
        """Returns whether the given task structure contains the TaskToken field anywhere.

        The field is considered included if the field itself or one of its containing
        fields occurs anywhere in the payload.

        Arguments:
            obj: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "containsTaskToken", [obj])

    @jsii.member(jsii_name="findReferencedPaths")
    @classmethod
    def find_referenced_paths(cls, obj: typing.Optional[typing.Mapping[str,typing.Any]]=None) -> typing.List[str]:
        """Return all JSON paths used in the given structure.

        Arguments:
            obj: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "findReferencedPaths", [obj])

    @jsii.member(jsii_name="renderObject")
    @classmethod
    def render_object(cls, obj: typing.Optional[typing.Mapping[str,typing.Any]]=None) -> typing.Optional[typing.Mapping[str,typing.Any]]:
        """Render a JSON structure containing fields to the right StepFunctions structure.

        Arguments:
            obj: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "renderObject", [obj])


@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.FindStateOptions", jsii_struct_bases=[])
class FindStateOptions(jsii.compat.TypedDict, total=False):
    """Options for finding reachable states.

    Stability:
        experimental
    """
    includeErrorHandlers: bool
    """Whether or not to follow error-handling transitions.

    Default:
        false

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-stepfunctions.IActivity")
class IActivity(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IActivityProxy

    @property
    @jsii.member(jsii_name="activityArn")
    def activity_arn(self) -> str:
        """The ARN of the activity.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="activityName")
    def activity_name(self) -> str:
        """The name of the activity.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IActivityProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-stepfunctions.IActivity"
    @property
    @jsii.member(jsii_name="activityArn")
    def activity_arn(self) -> str:
        """The ARN of the activity.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "activityArn")

    @property
    @jsii.member(jsii_name="activityName")
    def activity_name(self) -> str:
        """The name of the activity.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "activityName")


@jsii.implements(IActivity)
class Activity(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Activity"):
    """Define a new StepFunctions activity.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, activity_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            activityName: The name for this activity. Default: If not supplied, a name is generated

        Stability:
            experimental
        """
        props: ActivityProps = {}

        if activity_name is not None:
            props["activityName"] = activity_name

        jsii.create(Activity, self, [scope, id, props])

    @jsii.member(jsii_name="fromActivityArn")
    @classmethod
    def from_activity_arn(cls, scope: aws_cdk.cdk.Construct, id: str, activity_arn: str) -> "IActivity":
        """Construct an Activity from an existing Activity ARN.

        Arguments:
            scope: -
            id: -
            activityArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromActivityArn", [scope, id, activity_arn])

    @jsii.member(jsii_name="fromActivityName")
    @classmethod
    def from_activity_name(cls, scope: aws_cdk.cdk.Construct, id: str, activity_name: str) -> "IActivity":
        """Construct an Activity from an existing Activity Name.

        Arguments:
            scope: -
            id: -
            activityName: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromActivityName", [scope, id, activity_name])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Activity.

        Arguments:
            metricName: -
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

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricFailed")
    def metric_failed(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of times this activity fails.

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

        return jsii.invoke(self, "metricFailed", [props])

    @jsii.member(jsii_name="metricHeartbeatTimedOut")
    def metric_heartbeat_timed_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of times the heartbeat times out for this activity.

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

        return jsii.invoke(self, "metricHeartbeatTimedOut", [props])

    @jsii.member(jsii_name="metricRunTime")
    def metric_run_time(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The interval, in milliseconds, between the time the activity starts and the time it closes.

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

        return jsii.invoke(self, "metricRunTime", [props])

    @jsii.member(jsii_name="metricScheduled")
    def metric_scheduled(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of times this activity is scheduled.

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

        return jsii.invoke(self, "metricScheduled", [props])

    @jsii.member(jsii_name="metricScheduleTime")
    def metric_schedule_time(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The interval, in milliseconds, for which the activity stays in the schedule state.

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

        return jsii.invoke(self, "metricScheduleTime", [props])

    @jsii.member(jsii_name="metricStarted")
    def metric_started(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of times this activity is started.

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

        return jsii.invoke(self, "metricStarted", [props])

    @jsii.member(jsii_name="metricSucceeded")
    def metric_succeeded(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of times this activity succeeds.

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

        return jsii.invoke(self, "metricSucceeded", [props])

    @jsii.member(jsii_name="metricTime")
    def metric_time(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The interval, in milliseconds, between the time the activity is scheduled and the time it closes.

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

        return jsii.invoke(self, "metricTime", [props])

    @jsii.member(jsii_name="metricTimedOut")
    def metric_timed_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of times this activity times out.

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

        return jsii.invoke(self, "metricTimedOut", [props])

    @property
    @jsii.member(jsii_name="activityArn")
    def activity_arn(self) -> str:
        """The ARN of the activity.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "activityArn")

    @property
    @jsii.member(jsii_name="activityName")
    def activity_name(self) -> str:
        """The name of the activity.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "activityName")


@jsii.interface(jsii_type="@aws-cdk/aws-stepfunctions.IChainable")
class IChainable(jsii.compat.Protocol):
    """Interface for objects that can be used in a Chain.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IChainableProxy

    @property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        """The chainable end state(s) of this chainable.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="id")
    def id(self) -> str:
        """Descriptive identifier for this chainable.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> "State":
        """The start state of this chainable.

        Stability:
            experimental
        """
        ...


class _IChainableProxy():
    """Interface for objects that can be used in a Chain.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-stepfunctions.IChainable"
    @property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        """The chainable end state(s) of this chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "endStates")

    @property
    @jsii.member(jsii_name="id")
    def id(self) -> str:
        """Descriptive identifier for this chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "id")

    @property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> "State":
        """The start state of this chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "startState")


@jsii.implements(IChainable)
class Chain(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Chain"):
    """A collection of states to chain onto.

    A Chain has a start and zero or more chainable ends. If there are
    zero ends, calling next() on the Chain will fail.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="custom")
    @classmethod
    def custom(cls, start_state: "State", end_states: typing.List["INextable"], last_added: "IChainable") -> "Chain":
        """Make a Chain with specific start and end states, and a last-added Chainable.

        Arguments:
            startState: -
            endStates: -
            lastAdded: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "custom", [start_state, end_states, last_added])

    @jsii.member(jsii_name="sequence")
    @classmethod
    def sequence(cls, start: "IChainable", next: "IChainable") -> "Chain":
        """Make a Chain with the start from one chain and the ends from another.

        Arguments:
            start: -
            next: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "sequence", [start, next])

    @jsii.member(jsii_name="start")
    @classmethod
    def start(cls, state: "IChainable") -> "Chain":
        """Begin a new Chain from one chainable.

        Arguments:
            state: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "start", [state])

    @jsii.member(jsii_name="next")
    def next(self, next: "IChainable") -> "Chain":
        """Continue normal execution with the given state.

        Arguments:
            next: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "next", [next])

    @jsii.member(jsii_name="toSingleState")
    def to_single_state(self, id: str, *, comment: typing.Optional[str]=None, input_path: typing.Optional[str]=None, output_path: typing.Optional[str]=None, result_path: typing.Optional[str]=None) -> "Parallel":
        """Return a single state that encompasses all states in the chain.

        This can be used to add error handling to a sequence of states.

        Be aware that this changes the result of the inner state machine
        to be an array with the result of the state machine in it. Adjust
        your paths accordingly. For example, change 'outputPath' to
        '$[0]'.

        Arguments:
            id: -
            props: -
            comment: An optional description for this state. Default: No comment
            inputPath: JSONPath expression to select part of the state to be the input to this state. May also be the special value DISCARD, which will cause the effective input to be the empty object {}. Default: $
            outputPath: JSONPath expression to select part of the state to be the output to this state. May also be the special value DISCARD, which will cause the effective output to be the empty object {}. Default: $
            resultPath: JSONPath expression to indicate where to inject the state's output. May also be the special value DISCARD, which will cause the state's input to become its output. Default: $

        Stability:
            experimental
        """
        props: ParallelProps = {}

        if comment is not None:
            props["comment"] = comment

        if input_path is not None:
            props["inputPath"] = input_path

        if output_path is not None:
            props["outputPath"] = output_path

        if result_path is not None:
            props["resultPath"] = result_path

        return jsii.invoke(self, "toSingleState", [id, props])

    @property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        """The chainable end state(s) of this chain.

        Stability:
            experimental
        """
        return jsii.get(self, "endStates")

    @property
    @jsii.member(jsii_name="id")
    def id(self) -> str:
        """Identify this Chain.

        Stability:
            experimental
        """
        return jsii.get(self, "id")

    @property
    @jsii.member(jsii_name="lastAdded")
    def last_added(self) -> "IChainable":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "lastAdded")

    @property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> "State":
        """The start state of this chain.

        Stability:
            experimental
        """
        return jsii.get(self, "startState")


@jsii.interface(jsii_type="@aws-cdk/aws-stepfunctions.INextable")
class INextable(jsii.compat.Protocol):
    """Interface for states that can have 'next' states.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _INextableProxy

    @jsii.member(jsii_name="next")
    def next(self, state: "IChainable") -> "Chain":
        """Go to the indicated state after this state.

        Arguments:
            state: -

        Returns:
            The chain of states built up

        Stability:
            experimental
        """
        ...


class _INextableProxy():
    """Interface for states that can have 'next' states.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-stepfunctions.INextable"
    @jsii.member(jsii_name="next")
    def next(self, state: "IChainable") -> "Chain":
        """Go to the indicated state after this state.

        Arguments:
            state: -

        Returns:
            The chain of states built up

        Stability:
            experimental
        """
        return jsii.invoke(self, "next", [state])


@jsii.interface(jsii_type="@aws-cdk/aws-stepfunctions.IStateMachine")
class IStateMachine(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """A State Machine.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IStateMachineProxy

    @property
    @jsii.member(jsii_name="stateMachineArn")
    def state_machine_arn(self) -> str:
        """The ARN of the state machine.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IStateMachineProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """A State Machine.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-stepfunctions.IStateMachine"
    @property
    @jsii.member(jsii_name="stateMachineArn")
    def state_machine_arn(self) -> str:
        """The ARN of the state machine.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "stateMachineArn")


@jsii.interface(jsii_type="@aws-cdk/aws-stepfunctions.IStepFunctionsTask")
class IStepFunctionsTask(jsii.compat.Protocol):
    """Interface for resources that can be used as tasks.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IStepFunctionsTaskProxy

    @jsii.member(jsii_name="bind")
    def bind(self, task: "Task") -> "StepFunctionsTaskConfig":
        """Called when the task object is used in a workflow.

        Arguments:
            task: -

        Stability:
            experimental
        """
        ...


class _IStepFunctionsTaskProxy():
    """Interface for resources that can be used as tasks.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-stepfunctions.IStepFunctionsTask"
    @jsii.member(jsii_name="bind")
    def bind(self, task: "Task") -> "StepFunctionsTaskConfig":
        """Called when the task object is used in a workflow.

        Arguments:
            task: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [task])


@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions.InputType")
class InputType(enum.Enum):
    """The type of task input.

    Stability:
        experimental
    """
    Text = "Text"
    """
    Stability:
        experimental
    """
    Object = "Object"
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.ParallelProps", jsii_struct_bases=[])
class ParallelProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a Parallel state.

    Stability:
        experimental
    """
    comment: str
    """An optional description for this state.

    Default:
        No comment

    Stability:
        experimental
    """

    inputPath: str
    """JSONPath expression to select part of the state to be the input to this state.

    May also be the special value DISCARD, which will cause the effective
    input to be the empty object {}.

    Default:
        $

    Stability:
        experimental
    """

    outputPath: str
    """JSONPath expression to select part of the state to be the output to this state.

    May also be the special value DISCARD, which will cause the effective
    output to be the empty object {}.

    Default:
        $

    Stability:
        experimental
    """

    resultPath: str
    """JSONPath expression to indicate where to inject the state's output.

    May also be the special value DISCARD, which will cause the state's
    input to become its output.

    Default:
        $

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.PassProps", jsii_struct_bases=[])
class PassProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a Pass state.

    Stability:
        experimental
    """
    comment: str
    """An optional description for this state.

    Default:
        No comment

    Stability:
        experimental
    """

    inputPath: str
    """JSONPath expression to select part of the state to be the input to this state.

    May also be the special value DISCARD, which will cause the effective
    input to be the empty object {}.

    Default:
        $

    Stability:
        experimental
    """

    outputPath: str
    """JSONPath expression to select part of the state to be the output to this state.

    May also be the special value DISCARD, which will cause the effective
    output to be the empty object {}.

    Default:
        $

    Stability:
        experimental
    """

    result: typing.Mapping[str,typing.Any]
    """If given, treat as the result of this operation.

    Can be used to inject or replace the current execution state.

    Default:
        No injected result

    Stability:
        experimental
    """

    resultPath: str
    """JSONPath expression to indicate where to inject the state's output.

    May also be the special value DISCARD, which will cause the state's
    input to become its output.

    Default:
        $

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.RetryProps", jsii_struct_bases=[])
class RetryProps(jsii.compat.TypedDict, total=False):
    """Retry details.

    Stability:
        experimental
    """
    backoffRate: jsii.Number
    """Multiplication for how much longer the wait interval gets on every retry.

    Default:
        2

    Stability:
        experimental
    """

    errors: typing.List[str]
    """Errors to retry.

    A list of error strings to retry, which can be either predefined errors
    (for example Errors.NoChoiceMatched) or a self-defined error.

    Default:
        All errors

    Stability:
        experimental
    """

    intervalSeconds: jsii.Number
    """How many seconds to wait initially before retrying.

    Default:
        1

    Stability:
        experimental
    """

    maxAttempts: jsii.Number
    """How many times to retry this particular error.

    May be 0 to disable retry for specific errors (in case you have
    a catch-all retry policy).

    Default:
        3

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.SingleStateOptions", jsii_struct_bases=[ParallelProps])
class SingleStateOptions(ParallelProps, jsii.compat.TypedDict, total=False):
    """Options for creating a single state.

    Stability:
        experimental
    """
    prefixStates: str
    """String to prefix all stateIds in the state machine with.

    Default:
        stateId

    Stability:
        experimental
    """

    stateId: str
    """ID of newly created containing state.

    Default:
        Construct ID of the StateMachineFragment

    Stability:
        experimental
    """

@jsii.implements(IChainable)
class State(aws_cdk.cdk.Construct, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-stepfunctions.State"):
    """Base class for all other state classes.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _StateProxy

    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, comment: typing.Optional[str]=None, input_path: typing.Optional[str]=None, output_path: typing.Optional[str]=None, parameters: typing.Optional[typing.Mapping[str,typing.Any]]=None, result_path: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            comment: A comment describing this state. Default: No comment
            inputPath: JSONPath expression to select part of the state to be the input to this state. May also be the special value DISCARD, which will cause the effective input to be the empty object {}. Default: $
            outputPath: JSONPath expression to select part of the state to be the output to this state. May also be the special value DISCARD, which will cause the effective output to be the empty object {}. Default: $
            parameters: Parameters pass a collection of key-value pairs, either static values or JSONPath expressions that select from the input. Default: No parameters
            resultPath: JSONPath expression to indicate where to inject the state's output. May also be the special value DISCARD, which will cause the state's input to become its output. Default: $

        Stability:
            experimental
        """
        props: StateProps = {}

        if comment is not None:
            props["comment"] = comment

        if input_path is not None:
            props["inputPath"] = input_path

        if output_path is not None:
            props["outputPath"] = output_path

        if parameters is not None:
            props["parameters"] = parameters

        if result_path is not None:
            props["resultPath"] = result_path

        jsii.create(State, self, [scope, id, props])

    @jsii.member(jsii_name="filterNextables")
    @classmethod
    def filter_nextables(cls, states: typing.List["State"]) -> typing.List["INextable"]:
        """Return only the states that allow chaining from an array of states.

        Arguments:
            states: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "filterNextables", [states])

    @jsii.member(jsii_name="findReachableEndStates")
    @classmethod
    def find_reachable_end_states(cls, start: "State", *, include_error_handlers: typing.Optional[bool]=None) -> typing.List["State"]:
        """Find the set of end states states reachable through transitions from the given start state.

        Arguments:
            start: -
            options: -
            includeErrorHandlers: Whether or not to follow error-handling transitions. Default: false

        Stability:
            experimental
        """
        options: FindStateOptions = {}

        if include_error_handlers is not None:
            options["includeErrorHandlers"] = include_error_handlers

        return jsii.sinvoke(cls, "findReachableEndStates", [start, options])

    @jsii.member(jsii_name="prefixStates")
    @classmethod
    def prefix_states(cls, root: aws_cdk.cdk.IConstruct, prefix: str) -> None:
        """Add a prefix to the stateId of all States found in a construct tree.

        Arguments:
            root: -
            prefix: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "prefixStates", [root, prefix])

    @jsii.member(jsii_name="addBranch")
    def _add_branch(self, branch: "StateGraph") -> None:
        """Add a paralle branch to this state.

        Arguments:
            branch: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addBranch", [branch])

    @jsii.member(jsii_name="addChoice")
    def _add_choice(self, condition: "Condition", next: "State") -> None:
        """Add a choice branch to this state.

        Arguments:
            condition: -
            next: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addChoice", [condition, next])

    @jsii.member(jsii_name="addPrefix")
    def add_prefix(self, x: str) -> None:
        """Add a prefix to the stateId of this state.

        Arguments:
            x: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addPrefix", [x])

    @jsii.member(jsii_name="bindToGraph")
    def bind_to_graph(self, graph: "StateGraph") -> None:
        """Register this state as part of the given graph.

        Don't call this. It will be called automatically when you work
        with states normally.

        Arguments:
            graph: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bindToGraph", [graph])

    @jsii.member(jsii_name="makeDefault")
    def _make_default(self, def_: "State") -> None:
        """Make the indicated state the default choice transition of this state.

        Arguments:
            def: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "makeDefault", [def_])

    @jsii.member(jsii_name="makeNext")
    def _make_next(self, next: "State") -> None:
        """Make the indicated state the default transition of this state.

        Arguments:
            next: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "makeNext", [next])

    @jsii.member(jsii_name="renderBranches")
    def _render_branches(self) -> typing.Any:
        """Render parallel branches in ASL JSON format.

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderBranches", [])

    @jsii.member(jsii_name="renderChoices")
    def _render_choices(self) -> typing.Any:
        """Render the choices in ASL JSON format.

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderChoices", [])

    @jsii.member(jsii_name="renderInputOutput")
    def _render_input_output(self) -> typing.Any:
        """Render InputPath/Parameters/OutputPath in ASL JSON format.

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderInputOutput", [])

    @jsii.member(jsii_name="renderNextEnd")
    def _render_next_end(self) -> typing.Any:
        """Render the default next state in ASL JSON format.

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderNextEnd", [])

    @jsii.member(jsii_name="renderRetryCatch")
    def _render_retry_catch(self) -> typing.Any:
        """Render error recovery options in ASL JSON format.

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderRetryCatch", [])

    @jsii.member(jsii_name="toStateJson")
    @abc.abstractmethod
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        """Render the state as JSON.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="whenBoundToGraph")
    def _when_bound_to_graph(self, graph: "StateGraph") -> None:
        """Called whenever this state is bound to a graph.

        Can be overridden by subclasses.

        Arguments:
            graph: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "whenBoundToGraph", [graph])

    @property
    @jsii.member(jsii_name="branches")
    def _branches(self) -> typing.List["StateGraph"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "branches")

    @property
    @jsii.member(jsii_name="endStates")
    @abc.abstractmethod
    def end_states(self) -> typing.List["INextable"]:
        """Continuable states of this Chainable.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="id")
    def id(self) -> str:
        """Descriptive identifier for this chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "id")

    @property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> "State":
        """First state of this Chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "startState")

    @property
    @jsii.member(jsii_name="stateId")
    def state_id(self) -> str:
        """Tokenized string that evaluates to the state's ID.

        Stability:
            experimental
        """
        return jsii.get(self, "stateId")

    @property
    @jsii.member(jsii_name="comment")
    def _comment(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "comment")

    @property
    @jsii.member(jsii_name="inputPath")
    def _input_path(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "inputPath")

    @property
    @jsii.member(jsii_name="outputPath")
    def _output_path(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "outputPath")

    @property
    @jsii.member(jsii_name="parameters")
    def _parameters(self) -> typing.Optional[typing.Mapping[typing.Any, typing.Any]]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "parameters")

    @property
    @jsii.member(jsii_name="resultPath")
    def _result_path(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "resultPath")

    @property
    @jsii.member(jsii_name="defaultChoice")
    def _default_choice(self) -> typing.Optional["State"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "defaultChoice")

    @_default_choice.setter
    def _default_choice(self, value: typing.Optional["State"]):
        return jsii.set(self, "defaultChoice", value)


class _StateProxy(State):
    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        """Render the state as JSON.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toStateJson", [])

    @property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        """Continuable states of this Chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "endStates")


class Choice(State, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Choice"):
    """Define a Choice in the state machine.

    A choice state can be used to make decisions based on the execution
    state.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, comment: typing.Optional[str]=None, input_path: typing.Optional[str]=None, output_path: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            comment: An optional description for this state. Default: No comment
            inputPath: JSONPath expression to select part of the state to be the input to this state. May also be the special value DISCARD, which will cause the effective input to be the empty object {}. Default: $
            outputPath: JSONPath expression to select part of the state to be the output to this state. May also be the special value DISCARD, which will cause the effective output to be the empty object {}. Default: $

        Stability:
            experimental
        """
        props: ChoiceProps = {}

        if comment is not None:
            props["comment"] = comment

        if input_path is not None:
            props["inputPath"] = input_path

        if output_path is not None:
            props["outputPath"] = output_path

        jsii.create(Choice, self, [scope, id, props])

    @jsii.member(jsii_name="afterwards")
    def afterwards(self, *, include_error_handlers: typing.Optional[bool]=None, include_otherwise: typing.Optional[bool]=None) -> "Chain":
        """Return a Chain that contains all reachable end states from this Choice.

        Use this to combine all possible choice paths back.

        Arguments:
            options: -
            includeErrorHandlers: Whether to include error handling states. If this is true, all states which are error handlers (added through 'onError') and states reachable via error handlers will be included as well. Default: false
            includeOtherwise: Whether to include the default/otherwise transition for the current Choice state. If this is true and the current Choice does not have a default outgoing transition, one will be added included when .next() is called on the chain. Default: false

        Stability:
            experimental
        """
        options: AfterwardsOptions = {}

        if include_error_handlers is not None:
            options["includeErrorHandlers"] = include_error_handlers

        if include_otherwise is not None:
            options["includeOtherwise"] = include_otherwise

        return jsii.invoke(self, "afterwards", [options])

    @jsii.member(jsii_name="otherwise")
    def otherwise(self, def_: "IChainable") -> "Choice":
        """If none of the given conditions match, continue execution with the given state.

        If no conditions match and no otherwise() has been given, an execution
        error will be raised.

        Arguments:
            def: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "otherwise", [def_])

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        """Return the Amazon States Language object for this state.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toStateJson", [])

    @jsii.member(jsii_name="when")
    def when(self, condition: "Condition", next: "IChainable") -> "Choice":
        """If the given condition matches, continue execution with the given state.

        Arguments:
            condition: -
            next: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "when", [condition, next])

    @property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        """Continuable states of this Chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "endStates")


class Fail(State, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Fail"):
    """Define a Fail state in the state machine.

    Reaching a Fail state terminates the state execution in failure.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cause: typing.Optional[str]=None, comment: typing.Optional[str]=None, error: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            cause: A description for the cause of the failure. Default: No description
            comment: An optional description for this state. Default: No comment
            error: Error code used to represent this failure. Default: No error code

        Stability:
            experimental
        """
        props: FailProps = {}

        if cause is not None:
            props["cause"] = cause

        if comment is not None:
            props["comment"] = comment

        if error is not None:
            props["error"] = error

        jsii.create(Fail, self, [scope, id, props])

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        """Return the Amazon States Language object for this state.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toStateJson", [])

    @property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        """Continuable states of this Chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "endStates")


@jsii.implements(INextable)
class Parallel(State, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Parallel"):
    """Define a Parallel state in the state machine.

    A Parallel state can be used to run one or more state machines at the same
    time.

    The Result of a Parallel state is an array of the results of its substatemachines.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, comment: typing.Optional[str]=None, input_path: typing.Optional[str]=None, output_path: typing.Optional[str]=None, result_path: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            comment: An optional description for this state. Default: No comment
            inputPath: JSONPath expression to select part of the state to be the input to this state. May also be the special value DISCARD, which will cause the effective input to be the empty object {}. Default: $
            outputPath: JSONPath expression to select part of the state to be the output to this state. May also be the special value DISCARD, which will cause the effective output to be the empty object {}. Default: $
            resultPath: JSONPath expression to indicate where to inject the state's output. May also be the special value DISCARD, which will cause the state's input to become its output. Default: $

        Stability:
            experimental
        """
        props: ParallelProps = {}

        if comment is not None:
            props["comment"] = comment

        if input_path is not None:
            props["inputPath"] = input_path

        if output_path is not None:
            props["outputPath"] = output_path

        if result_path is not None:
            props["resultPath"] = result_path

        jsii.create(Parallel, self, [scope, id, props])

    @jsii.member(jsii_name="addCatch")
    def add_catch(self, handler: "IChainable", *, errors: typing.Optional[typing.List[str]]=None, result_path: typing.Optional[str]=None) -> "Parallel":
        """Add a recovery handler for this state.

        When a particular error occurs, execution will continue at the error
        handler instead of failing the state machine execution.

        Arguments:
            handler: -
            props: -
            errors: Errors to recover from by going to the given state. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
            resultPath: JSONPath expression to indicate where to inject the error data. May also be the special value DISCARD, which will cause the error data to be discarded. Default: $

        Stability:
            experimental
        """
        props: CatchProps = {}

        if errors is not None:
            props["errors"] = errors

        if result_path is not None:
            props["resultPath"] = result_path

        return jsii.invoke(self, "addCatch", [handler, props])

    @jsii.member(jsii_name="addRetry")
    def add_retry(self, *, backoff_rate: typing.Optional[jsii.Number]=None, errors: typing.Optional[typing.List[str]]=None, interval_seconds: typing.Optional[jsii.Number]=None, max_attempts: typing.Optional[jsii.Number]=None) -> "Parallel":
        """Add retry configuration for this state.

        This controls if and how the execution will be retried if a particular
        error occurs.

        Arguments:
            props: -
            backoffRate: Multiplication for how much longer the wait interval gets on every retry. Default: 2
            errors: Errors to retry. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
            intervalSeconds: How many seconds to wait initially before retrying. Default: 1
            maxAttempts: How many times to retry this particular error. May be 0 to disable retry for specific errors (in case you have a catch-all retry policy). Default: 3

        Stability:
            experimental
        """
        props: RetryProps = {}

        if backoff_rate is not None:
            props["backoffRate"] = backoff_rate

        if errors is not None:
            props["errors"] = errors

        if interval_seconds is not None:
            props["intervalSeconds"] = interval_seconds

        if max_attempts is not None:
            props["maxAttempts"] = max_attempts

        return jsii.invoke(self, "addRetry", [props])

    @jsii.member(jsii_name="branch")
    def branch(self, *branches: "IChainable") -> "Parallel":
        """Define one or more branches to run in parallel.

        Arguments:
            branches: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "branch", [*branches])

    @jsii.member(jsii_name="next")
    def next(self, next: "IChainable") -> "Chain":
        """Continue normal execution with the given state.

        Arguments:
            next: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "next", [next])

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        """Return the Amazon States Language object for this state.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toStateJson", [])

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[str]:
        """Validate this state.

        Stability:
            experimental
        """
        return jsii.invoke(self, "validate", [])

    @property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        """Continuable states of this Chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "endStates")


@jsii.implements(INextable)
class Pass(State, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Pass"):
    """Define a Pass in the state machine.

    A Pass state can be used to transform the current exeuction's state.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, comment: typing.Optional[str]=None, input_path: typing.Optional[str]=None, output_path: typing.Optional[str]=None, result: typing.Optional[typing.Mapping[str,typing.Any]]=None, result_path: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            comment: An optional description for this state. Default: No comment
            inputPath: JSONPath expression to select part of the state to be the input to this state. May also be the special value DISCARD, which will cause the effective input to be the empty object {}. Default: $
            outputPath: JSONPath expression to select part of the state to be the output to this state. May also be the special value DISCARD, which will cause the effective output to be the empty object {}. Default: $
            result: If given, treat as the result of this operation. Can be used to inject or replace the current execution state. Default: No injected result
            resultPath: JSONPath expression to indicate where to inject the state's output. May also be the special value DISCARD, which will cause the state's input to become its output. Default: $

        Stability:
            experimental
        """
        props: PassProps = {}

        if comment is not None:
            props["comment"] = comment

        if input_path is not None:
            props["inputPath"] = input_path

        if output_path is not None:
            props["outputPath"] = output_path

        if result is not None:
            props["result"] = result

        if result_path is not None:
            props["resultPath"] = result_path

        jsii.create(Pass, self, [scope, id, props])

    @jsii.member(jsii_name="next")
    def next(self, next: "IChainable") -> "Chain":
        """Continue normal execution with the given state.

        Arguments:
            next: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "next", [next])

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        """Return the Amazon States Language object for this state.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toStateJson", [])

    @property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        """Continuable states of this Chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "endStates")


class StateGraph(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.StateGraph"):
    """A collection of connected states.

    A StateGraph is used to keep track of all states that are connected (have
    transitions between them). It does not include the substatemachines in
    a Parallel's branches: those are their own StateGraphs, but the graphs
    themselves have a hierarchical relationship as well.

    By assigning states to a definintive StateGraph, we verify that no state
    machines are constructed. In particular:

    - Every state object can only ever be in 1 StateGraph, and not inadvertently
      be used in two graphs.
    - Every stateId must be unique across all states in the entire state
      machine.

    All policy statements in all states in all substatemachines are bubbled so
    that the top-level StateMachine instantiation can read them all and add
    them to the IAM Role.

    You do not need to instantiate this class; it is used internally.

    Stability:
        experimental
    """
    def __init__(self, start_state: "State", graph_description: str) -> None:
        """
        Arguments:
            startState: -
            graphDescription: -

        Stability:
            experimental
        """
        jsii.create(StateGraph, self, [start_state, graph_description])

    @jsii.member(jsii_name="registerPolicyStatement")
    def register_policy_statement(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Register a Policy Statement used by states in this graph.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "registerPolicyStatement", [statement])

    @jsii.member(jsii_name="registerState")
    def register_state(self, state: "State") -> None:
        """Register a state as part of this graph.

        Called by State.bindToGraph().

        Arguments:
            state: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "registerState", [state])

    @jsii.member(jsii_name="registerSuperGraph")
    def register_super_graph(self, graph: "StateGraph") -> None:
        """Register this graph as a child of the given graph.

        Resource changes will be bubbled up to the given graph.

        Arguments:
            graph: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "registerSuperGraph", [graph])

    @jsii.member(jsii_name="toGraphJson")
    def to_graph_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        """Return the Amazon States Language JSON for this graph.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toGraphJson", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Return a string description of this graph.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="graphDescription")
    def graph_description(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "graphDescription")

    @property
    @jsii.member(jsii_name="policyStatements")
    def policy_statements(self) -> typing.List[aws_cdk.aws_iam.PolicyStatement]:
        """The accumulated policy statements.

        Stability:
            experimental
        """
        return jsii.get(self, "policyStatements")

    @property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> "State":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "startState")

    @property
    @jsii.member(jsii_name="timeoutSeconds")
    def timeout_seconds(self) -> typing.Optional[jsii.Number]:
        """Set a timeout to render into the graph JSON.

        Read/write. Only makes sense on the top-level graph, subgraphs
        do not support this feature.

        Default:
            No timeout

        Stability:
            experimental
        """
        return jsii.get(self, "timeoutSeconds")

    @timeout_seconds.setter
    def timeout_seconds(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "timeoutSeconds", value)


@jsii.implements(IStateMachine)
class StateMachine(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.StateMachine"):
    """Define a StepFunctions State Machine.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, definition: "IChainable", role: typing.Optional[aws_cdk.aws_iam.IRole]=None, state_machine_name: typing.Optional[str]=None, timeout_sec: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            definition: Definition for this state machine.
            role: The execution role for the state machine service. Default: A role is automatically created
            stateMachineName: A name for the state machine. Default: A name is automatically generated
            timeoutSec: Maximum run time for this state machine. Default: No timeout

        Stability:
            experimental
        """
        props: StateMachineProps = {"definition": definition}

        if role is not None:
            props["role"] = role

        if state_machine_name is not None:
            props["stateMachineName"] = state_machine_name

        if timeout_sec is not None:
            props["timeoutSec"] = timeout_sec

        jsii.create(StateMachine, self, [scope, id, props])

    @jsii.member(jsii_name="fromStateMachineArn")
    @classmethod
    def from_state_machine_arn(cls, scope: aws_cdk.cdk.Construct, id: str, state_machine_arn: str) -> "IStateMachine":
        """Import a state machine.

        Arguments:
            scope: -
            id: -
            stateMachineArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromStateMachineArn", [scope, id, state_machine_arn])

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add the given statement to the role's policy.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToRolePolicy", [statement])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this State Machine's executions.

        Arguments:
            metricName: -
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

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricAborted")
    def metric_aborted(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of executions that were aborted.

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

        return jsii.invoke(self, "metricAborted", [props])

    @jsii.member(jsii_name="metricFailed")
    def metric_failed(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of executions that failed.

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

        return jsii.invoke(self, "metricFailed", [props])

    @jsii.member(jsii_name="metricStarted")
    def metric_started(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of executions that were started.

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

        return jsii.invoke(self, "metricStarted", [props])

    @jsii.member(jsii_name="metricSucceeded")
    def metric_succeeded(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of executions that succeeded.

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

        return jsii.invoke(self, "metricSucceeded", [props])

    @jsii.member(jsii_name="metricThrottled")
    def metric_throttled(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of executions that were throttled.

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

        return jsii.invoke(self, "metricThrottled", [props])

    @jsii.member(jsii_name="metricTime")
    def metric_time(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the interval, in milliseconds, between the time the execution starts and the time it closes.

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

        return jsii.invoke(self, "metricTime", [props])

    @jsii.member(jsii_name="metricTimedOut")
    def metric_timed_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of executions that succeeded.

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

        return jsii.invoke(self, "metricTimedOut", [props])

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        """Execution role of this state machine.

        Stability:
            experimental
        """
        return jsii.get(self, "role")

    @property
    @jsii.member(jsii_name="stateMachineArn")
    def state_machine_arn(self) -> str:
        """The ARN of the state machine.

        Stability:
            experimental
        """
        return jsii.get(self, "stateMachineArn")

    @property
    @jsii.member(jsii_name="stateMachineName")
    def state_machine_name(self) -> str:
        """The name of the state machine.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "stateMachineName")


@jsii.implements(IChainable)
class StateMachineFragment(aws_cdk.cdk.Construct, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-stepfunctions.StateMachineFragment"):
    """Base class for reusable state machine fragments.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _StateMachineFragmentProxy

    def __init__(self, scope: aws_cdk.cdk.Construct, id: str) -> None:
        """Creates a new construct node.

        Arguments:
            scope: The scope in which to define this construct.
            id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.

        Stability:
            experimental
        """
        jsii.create(StateMachineFragment, self, [scope, id])

    @jsii.member(jsii_name="next")
    def next(self, next: "IChainable") -> "Chain":
        """Continue normal execution with the given state.

        Arguments:
            next: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "next", [next])

    @jsii.member(jsii_name="prefixStates")
    def prefix_states(self, prefix: typing.Optional[str]=None) -> "StateMachineFragment":
        """Prefix the IDs of all states in this state machine fragment.

        Use this to avoid multiple copies of the state machine all having the
        same state IDs.

        Arguments:
            prefix: The prefix to add. Will use construct ID by default.

        Stability:
            experimental
        """
        return jsii.invoke(self, "prefixStates", [prefix])

    @jsii.member(jsii_name="toSingleState")
    def to_single_state(self, *, prefix_states: typing.Optional[str]=None, state_id: typing.Optional[str]=None, comment: typing.Optional[str]=None, input_path: typing.Optional[str]=None, output_path: typing.Optional[str]=None, result_path: typing.Optional[str]=None) -> "Parallel":
        """Wrap all states in this state machine fragment up into a single state.

        This can be used to add retry or error handling onto this state
        machine fragment.

        Be aware that this changes the result of the inner state machine
        to be an array with the result of the state machine in it. Adjust
        your paths accordingly. For example, change 'outputPath' to
        '$[0]'.

        Arguments:
            options: -
            prefixStates: String to prefix all stateIds in the state machine with. Default: stateId
            stateId: ID of newly created containing state. Default: Construct ID of the StateMachineFragment
            comment: An optional description for this state. Default: No comment
            inputPath: JSONPath expression to select part of the state to be the input to this state. May also be the special value DISCARD, which will cause the effective input to be the empty object {}. Default: $
            outputPath: JSONPath expression to select part of the state to be the output to this state. May also be the special value DISCARD, which will cause the effective output to be the empty object {}. Default: $
            resultPath: JSONPath expression to indicate where to inject the state's output. May also be the special value DISCARD, which will cause the state's input to become its output. Default: $

        Stability:
            experimental
        """
        options: SingleStateOptions = {}

        if prefix_states is not None:
            options["prefixStates"] = prefix_states

        if state_id is not None:
            options["stateId"] = state_id

        if comment is not None:
            options["comment"] = comment

        if input_path is not None:
            options["inputPath"] = input_path

        if output_path is not None:
            options["outputPath"] = output_path

        if result_path is not None:
            options["resultPath"] = result_path

        return jsii.invoke(self, "toSingleState", [options])

    @property
    @jsii.member(jsii_name="endStates")
    @abc.abstractmethod
    def end_states(self) -> typing.List["INextable"]:
        """The states to chain onto if this fragment is used.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="id")
    def id(self) -> str:
        """Descriptive identifier for this chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "id")

    @property
    @jsii.member(jsii_name="startState")
    @abc.abstractmethod
    def start_state(self) -> "State":
        """The start state of this state machine fragment.

        Stability:
            experimental
        """
        ...


class _StateMachineFragmentProxy(StateMachineFragment):
    @property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        """The states to chain onto if this fragment is used.

        Stability:
            experimental
        """
        return jsii.get(self, "endStates")

    @property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> "State":
        """The start state of this state machine fragment.

        Stability:
            experimental
        """
        return jsii.get(self, "startState")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _StateMachineProps(jsii.compat.TypedDict, total=False):
    role: aws_cdk.aws_iam.IRole
    """The execution role for the state machine service.

    Default:
        A role is automatically created

    Stability:
        experimental
    """
    stateMachineName: str
    """A name for the state machine.

    Default:
        A name is automatically generated

    Stability:
        experimental
    """
    timeoutSec: jsii.Number
    """Maximum run time for this state machine.

    Default:
        No timeout

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.StateMachineProps", jsii_struct_bases=[_StateMachineProps])
class StateMachineProps(_StateMachineProps):
    """Properties for defining a State Machine.

    Stability:
        experimental
    """
    definition: "IChainable"
    """Definition for this state machine.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.StateProps", jsii_struct_bases=[])
class StateProps(jsii.compat.TypedDict, total=False):
    """Properties shared by all states.

    Stability:
        experimental
    """
    comment: str
    """A comment describing this state.

    Default:
        No comment

    Stability:
        experimental
    """

    inputPath: str
    """JSONPath expression to select part of the state to be the input to this state.

    May also be the special value DISCARD, which will cause the effective
    input to be the empty object {}.

    Default:
        $

    Stability:
        experimental
    """

    outputPath: str
    """JSONPath expression to select part of the state to be the output to this state.

    May also be the special value DISCARD, which will cause the effective
    output to be the empty object {}.

    Default:
        $

    Stability:
        experimental
    """

    parameters: typing.Mapping[str,typing.Any]
    """Parameters pass a collection of key-value pairs, either static values or JSONPath expressions that select from the input.

    Default:
        No parameters

    See:
        https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-parameters
    Stability:
        experimental
    """

    resultPath: str
    """JSONPath expression to indicate where to inject the state's output.

    May also be the special value DISCARD, which will cause the state's
    input to become its output.

    Default:
        $

    Stability:
        experimental
    """

class StateTransitionMetric(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.StateTransitionMetric"):
    """Metrics on the rate limiting performed on state machine execution.

    These rate limits are shared across all state machines.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(StateTransitionMetric, self, [])

    @jsii.member(jsii_name="metric")
    @classmethod
    def metric(cls, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for the service's state transition metrics.

        Arguments:
            metricName: -
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

        return jsii.sinvoke(cls, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricConsumedCapacity")
    @classmethod
    def metric_consumed_capacity(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of available state transitions per second.

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

        return jsii.sinvoke(cls, "metricConsumedCapacity", [props])

    @jsii.member(jsii_name="metricProvisionedBucketSize")
    @classmethod
    def metric_provisioned_bucket_size(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of available state transitions.

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

        return jsii.sinvoke(cls, "metricProvisionedBucketSize", [props])

    @jsii.member(jsii_name="metricProvisionedRefillRate")
    @classmethod
    def metric_provisioned_refill_rate(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the provisioned steady-state execution rate.

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

        return jsii.sinvoke(cls, "metricProvisionedRefillRate", [props])

    @jsii.member(jsii_name="metricThrottledEvents")
    @classmethod
    def metric_throttled_events(cls, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of throttled state transitions.

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

        return jsii.sinvoke(cls, "metricThrottledEvents", [props])


@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions.StateType")
class StateType(enum.Enum):
    """State types.

    Stability:
        experimental
    """
    Pass = "Pass"
    """
    Stability:
        experimental
    """
    Task = "Task"
    """
    Stability:
        experimental
    """
    Choice = "Choice"
    """
    Stability:
        experimental
    """
    Wait = "Wait"
    """
    Stability:
        experimental
    """
    Succeed = "Succeed"
    """
    Stability:
        experimental
    """
    Fail = "Fail"
    """
    Stability:
        experimental
    """
    Parallel = "Parallel"
    """
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _StepFunctionsTaskConfig(jsii.compat.TypedDict, total=False):
    heartbeatSeconds: jsii.Number
    """Maximum time between heart beats.

    If the time between heart beats takes longer than this, a 'Timeout' error is raised.

    This is only relevant when using an Activity type as resource.

    Default:
        No heart beat timeout

    Stability:
        experimental
    """
    metricDimensions: typing.Mapping[str,typing.Any]
    """The dimensions to attach to metrics.

    Default:
        No metrics

    Stability:
        experimental
    """
    metricPrefixPlural: str
    """Prefix for plural metric names of activity actions.

    Default:
        No such metrics

    Stability:
        experimental
    """
    metricPrefixSingular: str
    """Prefix for singular metric names of activity actions.

    Default:
        No such metrics

    Stability:
        experimental
    """
    parameters: typing.Mapping[str,typing.Any]
    """Parameters pass a collection of key-value pairs, either static values or JSONPath expressions that select from the input.

    What is passed here will be merged with any default parameters
    configured by the ``resource``. For example, a DynamoDB table target
    will

    Default:
        No parameters

    See:
        https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-parameters
    Stability:
        experimental
    """
    policyStatements: typing.List[aws_cdk.aws_iam.PolicyStatement]
    """Additional policy statements to add to the execution role.

    Default:
        No policy roles

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.StepFunctionsTaskConfig", jsii_struct_bases=[_StepFunctionsTaskConfig])
class StepFunctionsTaskConfig(_StepFunctionsTaskConfig):
    """Properties that define what kind of task should be created.

    Stability:
        experimental
    """
    resourceArn: str
    """The resource that represents the work to be executed.

    Either the ARN of a Lambda Function or Activity, or a special
    ARN.

    Stability:
        experimental
    """

class Succeed(State, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Succeed"):
    """Define a Succeed state in the state machine.

    Reaching a Succeed state terminates the state execution in success.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, comment: typing.Optional[str]=None, input_path: typing.Optional[str]=None, output_path: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            comment: An optional description for this state. Default: No comment
            inputPath: JSONPath expression to select part of the state to be the input to this state. May also be the special value DISCARD, which will cause the effective input to be the empty object {}. Default: $
            outputPath: JSONPath expression to select part of the state to be the output to this state. May also be the special value DISCARD, which will cause the effective output to be the empty object {}. Default: $

        Stability:
            experimental
        """
        props: SucceedProps = {}

        if comment is not None:
            props["comment"] = comment

        if input_path is not None:
            props["inputPath"] = input_path

        if output_path is not None:
            props["outputPath"] = output_path

        jsii.create(Succeed, self, [scope, id, props])

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        """Return the Amazon States Language object for this state.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toStateJson", [])

    @property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        """Continuable states of this Chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "endStates")


@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.SucceedProps", jsii_struct_bases=[])
class SucceedProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a Succeed state.

    Stability:
        experimental
    """
    comment: str
    """An optional description for this state.

    Default:
        No comment

    Stability:
        experimental
    """

    inputPath: str
    """JSONPath expression to select part of the state to be the input to this state.

    May also be the special value DISCARD, which will cause the effective
    input to be the empty object {}.

    Default:
        $

    Stability:
        experimental
    """

    outputPath: str
    """JSONPath expression to select part of the state to be the output to this state.

    May also be the special value DISCARD, which will cause the effective
    output to be the empty object {}.

    Default:
        $

    Stability:
        experimental
    """

@jsii.implements(INextable)
class Task(State, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Task"):
    """Define a Task state in the state machine.

    Reaching a Task state causes some work to be executed, represented by the
    Task's resource property. Task constructs represent a generic Amazon
    States Language Task.

    For some resource types, more specific subclasses of Task may be available
    which are more convenient to use.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, task: "IStepFunctionsTask", comment: typing.Optional[str]=None, input_path: typing.Optional[str]=None, output_path: typing.Optional[str]=None, result_path: typing.Optional[str]=None, timeout_seconds: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            task: Actual task to be invoked in this workflow.
            comment: An optional description for this state. Default: No comment
            inputPath: JSONPath expression to select part of the state to be the input to this state. May also be the special value DISCARD, which will cause the effective input to be the empty object {}. Default: $
            outputPath: JSONPath expression to select part of the state to be the output to this state. May also be the special value DISCARD, which will cause the effective output to be the empty object {}. Default: $
            resultPath: JSONPath expression to indicate where to inject the state's output. May also be the special value DISCARD, which will cause the state's input to become its output. Default: $
            timeoutSeconds: Maximum run time of this state. If the state takes longer than this amount of time to complete, a 'Timeout' error is raised. Default: 60

        Stability:
            experimental
        """
        props: TaskProps = {"task": task}

        if comment is not None:
            props["comment"] = comment

        if input_path is not None:
            props["inputPath"] = input_path

        if output_path is not None:
            props["outputPath"] = output_path

        if result_path is not None:
            props["resultPath"] = result_path

        if timeout_seconds is not None:
            props["timeoutSeconds"] = timeout_seconds

        jsii.create(Task, self, [scope, id, props])

    @jsii.member(jsii_name="addCatch")
    def add_catch(self, handler: "IChainable", *, errors: typing.Optional[typing.List[str]]=None, result_path: typing.Optional[str]=None) -> "Task":
        """Add a recovery handler for this state.

        When a particular error occurs, execution will continue at the error
        handler instead of failing the state machine execution.

        Arguments:
            handler: -
            props: -
            errors: Errors to recover from by going to the given state. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
            resultPath: JSONPath expression to indicate where to inject the error data. May also be the special value DISCARD, which will cause the error data to be discarded. Default: $

        Stability:
            experimental
        """
        props: CatchProps = {}

        if errors is not None:
            props["errors"] = errors

        if result_path is not None:
            props["resultPath"] = result_path

        return jsii.invoke(self, "addCatch", [handler, props])

    @jsii.member(jsii_name="addRetry")
    def add_retry(self, *, backoff_rate: typing.Optional[jsii.Number]=None, errors: typing.Optional[typing.List[str]]=None, interval_seconds: typing.Optional[jsii.Number]=None, max_attempts: typing.Optional[jsii.Number]=None) -> "Task":
        """Add retry configuration for this state.

        This controls if and how the execution will be retried if a particular
        error occurs.

        Arguments:
            props: -
            backoffRate: Multiplication for how much longer the wait interval gets on every retry. Default: 2
            errors: Errors to retry. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
            intervalSeconds: How many seconds to wait initially before retrying. Default: 1
            maxAttempts: How many times to retry this particular error. May be 0 to disable retry for specific errors (in case you have a catch-all retry policy). Default: 3

        Stability:
            experimental
        """
        props: RetryProps = {}

        if backoff_rate is not None:
            props["backoffRate"] = backoff_rate

        if errors is not None:
            props["errors"] = errors

        if interval_seconds is not None:
            props["intervalSeconds"] = interval_seconds

        if max_attempts is not None:
            props["maxAttempts"] = max_attempts

        return jsii.invoke(self, "addRetry", [props])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Task.

        Arguments:
            metricName: -
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

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricFailed")
    def metric_failed(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of times this activity fails.

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

        return jsii.invoke(self, "metricFailed", [props])

    @jsii.member(jsii_name="metricHeartbeatTimedOut")
    def metric_heartbeat_timed_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of times the heartbeat times out for this activity.

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

        return jsii.invoke(self, "metricHeartbeatTimedOut", [props])

    @jsii.member(jsii_name="metricRunTime")
    def metric_run_time(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The interval, in milliseconds, between the time the Task starts and the time it closes.

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

        return jsii.invoke(self, "metricRunTime", [props])

    @jsii.member(jsii_name="metricScheduled")
    def metric_scheduled(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of times this activity is scheduled.

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

        return jsii.invoke(self, "metricScheduled", [props])

    @jsii.member(jsii_name="metricScheduleTime")
    def metric_schedule_time(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The interval, in milliseconds, for which the activity stays in the schedule state.

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

        return jsii.invoke(self, "metricScheduleTime", [props])

    @jsii.member(jsii_name="metricStarted")
    def metric_started(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of times this activity is started.

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

        return jsii.invoke(self, "metricStarted", [props])

    @jsii.member(jsii_name="metricSucceeded")
    def metric_succeeded(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of times this activity succeeds.

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

        return jsii.invoke(self, "metricSucceeded", [props])

    @jsii.member(jsii_name="metricTime")
    def metric_time(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The interval, in milliseconds, between the time the activity is scheduled and the time it closes.

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

        return jsii.invoke(self, "metricTime", [props])

    @jsii.member(jsii_name="metricTimedOut")
    def metric_timed_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the number of times this activity times out.

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

        return jsii.invoke(self, "metricTimedOut", [props])

    @jsii.member(jsii_name="next")
    def next(self, next: "IChainable") -> "Chain":
        """Continue normal execution with the given state.

        Arguments:
            next: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "next", [next])

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        """Return the Amazon States Language object for this state.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toStateJson", [])

    @jsii.member(jsii_name="whenBoundToGraph")
    def _when_bound_to_graph(self, graph: "StateGraph") -> None:
        """Called whenever this state is bound to a graph.

        Can be overridden by subclasses.

        Arguments:
            graph: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "whenBoundToGraph", [graph])

    @property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        """Continuable states of this Chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "endStates")


class TaskInput(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.TaskInput"):
    """Type union for task classes that accept multiple types of payload.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="fromContextAt")
    @classmethod
    def from_context_at(cls, path: str) -> "TaskInput":
        """Use a part of the task context as task input.

        Use this when you want to use a subobject or string from
        the current task context as complete payload
        to a task.

        Arguments:
            path: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromContextAt", [path])

    @jsii.member(jsii_name="fromDataAt")
    @classmethod
    def from_data_at(cls, path: str) -> "TaskInput":
        """Use a part of the execution data as task input.

        Use this when you want to use a subobject or string from
        the current state machine execution as complete payload
        to a task.

        Arguments:
            path: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromDataAt", [path])

    @jsii.member(jsii_name="fromObject")
    @classmethod
    def from_object(cls, obj: typing.Mapping[str,typing.Any]) -> "TaskInput":
        """Use an object as task input.

        This object may contain Data and Context fields
        as object values, if desired.

        Arguments:
            obj: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromObject", [obj])

    @jsii.member(jsii_name="fromText")
    @classmethod
    def from_text(cls, text: str) -> "TaskInput":
        """Use a literal string as task input.

        This might be a JSON-encoded object, or just a text.

        Arguments:
            text: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromText", [text])

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> "InputType":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "type")

    @property
    @jsii.member(jsii_name="value")
    def value(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "value")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _TaskProps(jsii.compat.TypedDict, total=False):
    comment: str
    """An optional description for this state.

    Default:
        No comment

    Stability:
        experimental
    """
    inputPath: str
    """JSONPath expression to select part of the state to be the input to this state.

    May also be the special value DISCARD, which will cause the effective
    input to be the empty object {}.

    Default:
        $

    Stability:
        experimental
    """
    outputPath: str
    """JSONPath expression to select part of the state to be the output to this state.

    May also be the special value DISCARD, which will cause the effective
    output to be the empty object {}.

    Default:
        $

    Stability:
        experimental
    """
    resultPath: str
    """JSONPath expression to indicate where to inject the state's output.

    May also be the special value DISCARD, which will cause the state's
    input to become its output.

    Default:
        $

    Stability:
        experimental
    """
    timeoutSeconds: jsii.Number
    """Maximum run time of this state.

    If the state takes longer than this amount of time to complete, a 'Timeout' error is raised.

    Default:
        60

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.TaskProps", jsii_struct_bases=[_TaskProps])
class TaskProps(_TaskProps):
    """Props that are common to all tasks.

    Stability:
        experimental
    """
    task: "IStepFunctionsTask"
    """Actual task to be invoked in this workflow.

    Stability:
        experimental
    """

@jsii.implements(INextable)
class Wait(State, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Wait"):
    """Define a Wait state in the state machine.

    A Wait state can be used to delay execution of the state machine for a while.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, duration: "WaitDuration", comment: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            duration: Wait duration.
            comment: An optional description for this state. Default: No comment

        Stability:
            experimental
        """
        props: WaitProps = {"duration": duration}

        if comment is not None:
            props["comment"] = comment

        jsii.create(Wait, self, [scope, id, props])

    @jsii.member(jsii_name="next")
    def next(self, next: "IChainable") -> "Chain":
        """Continue normal execution with the given state.

        Arguments:
            next: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "next", [next])

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        """Return the Amazon States Language object for this state.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toStateJson", [])

    @property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        """Continuable states of this Chainable.

        Stability:
            experimental
        """
        return jsii.get(self, "endStates")


class WaitDuration(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.WaitDuration"):
    """
    Stability:
        experimental
    """
    @jsii.member(jsii_name="seconds")
    @classmethod
    def seconds(cls, duration: jsii.Number) -> "WaitDuration":
        """Wait a fixed number of seconds.

        Arguments:
            duration: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "seconds", [duration])

    @jsii.member(jsii_name="secondsPath")
    @classmethod
    def seconds_path(cls, path: str) -> "WaitDuration":
        """Wait for a number of seconds stored in the state object.

        Arguments:
            path: -

        Stability:
            experimental

        Example::
            $.waitSeconds
        """
        return jsii.sinvoke(cls, "secondsPath", [path])

    @jsii.member(jsii_name="timestamp")
    @classmethod
    def timestamp(cls, timestamp: str) -> "WaitDuration":
        """Wait until the given ISO8601 timestamp.

        Arguments:
            timestamp: -

        Stability:
            experimental

        Example::
            2016-03-14T01:59:00Z
        """
        return jsii.sinvoke(cls, "timestamp", [timestamp])

    @jsii.member(jsii_name="timestampPath")
    @classmethod
    def timestamp_path(cls, path: str) -> "WaitDuration":
        """Wait until a timestamp found in the state object.

        Arguments:
            path: -

        Stability:
            experimental

        Example::
            $.waitTimestamp
        """
        return jsii.sinvoke(cls, "timestampPath", [path])

    @property
    @jsii.member(jsii_name="json")
    def json(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "json")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _WaitProps(jsii.compat.TypedDict, total=False):
    comment: str
    """An optional description for this state.

    Default:
        No comment

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions.WaitProps", jsii_struct_bases=[_WaitProps])
class WaitProps(_WaitProps):
    """Properties for defining a Wait state.

    Stability:
        experimental
    """
    duration: "WaitDuration"
    """Wait duration.

    Stability:
        experimental
    """

__all__ = ["Activity", "ActivityProps", "AfterwardsOptions", "CatchProps", "CfnActivity", "CfnActivityProps", "CfnStateMachine", "CfnStateMachineProps", "Chain", "Choice", "ChoiceProps", "Condition", "Context", "Data", "Errors", "Fail", "FailProps", "FieldUtils", "FindStateOptions", "IActivity", "IChainable", "INextable", "IStateMachine", "IStepFunctionsTask", "InputType", "Parallel", "ParallelProps", "Pass", "PassProps", "RetryProps", "SingleStateOptions", "State", "StateGraph", "StateMachine", "StateMachineFragment", "StateMachineProps", "StateProps", "StateTransitionMetric", "StateType", "StepFunctionsTaskConfig", "Succeed", "SucceedProps", "Task", "TaskInput", "TaskProps", "Wait", "WaitDuration", "WaitProps", "__jsii_assembly__"]

publication.publish()
