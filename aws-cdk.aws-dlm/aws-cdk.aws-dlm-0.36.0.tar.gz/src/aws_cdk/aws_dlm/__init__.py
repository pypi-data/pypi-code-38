import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-dlm", "0.36.0", __name__, "aws-dlm@0.36.0.jsii.tgz")
class CfnLifecyclePolicy(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy"):
    """A CloudFormation ``AWS::DLM::LifecyclePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html
    Stability:
        stable
    cloudformationResource:
        AWS::DLM::LifecyclePolicy
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, description: typing.Optional[str]=None, execution_role_arn: typing.Optional[str]=None, policy_details: typing.Optional[typing.Union[typing.Optional["PolicyDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, state: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::DLM::LifecyclePolicy``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::DLM::LifecyclePolicy.Description``.
            execution_role_arn: ``AWS::DLM::LifecyclePolicy.ExecutionRoleArn``.
            policy_details: ``AWS::DLM::LifecyclePolicy.PolicyDetails``.
            state: ``AWS::DLM::LifecyclePolicy.State``.

        Stability:
            experimental
        """
        props: CfnLifecyclePolicyProps = {}

        if description is not None:
            props["description"] = description

        if execution_role_arn is not None:
            props["executionRoleArn"] = execution_role_arn

        if policy_details is not None:
            props["policyDetails"] = policy_details

        if state is not None:
            props["state"] = state

        jsii.create(CfnLifecyclePolicy, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::DLM::LifecyclePolicy.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="executionRoleArn")
    def execution_role_arn(self) -> typing.Optional[str]:
        """``AWS::DLM::LifecyclePolicy.ExecutionRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-executionrolearn
        Stability:
            stable
        """
        return jsii.get(self, "executionRoleArn")

    @execution_role_arn.setter
    def execution_role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "executionRoleArn", value)

    @property
    @jsii.member(jsii_name="policyDetails")
    def policy_details(self) -> typing.Optional[typing.Union[typing.Optional["PolicyDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DLM::LifecyclePolicy.PolicyDetails``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-policydetails
        Stability:
            stable
        """
        return jsii.get(self, "policyDetails")

    @policy_details.setter
    def policy_details(self, value: typing.Optional[typing.Union[typing.Optional["PolicyDetailsProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "policyDetails", value)

    @property
    @jsii.member(jsii_name="state")
    def state(self) -> typing.Optional[str]:
        """``AWS::DLM::LifecyclePolicy.State``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-state
        Stability:
            stable
        """
        return jsii.get(self, "state")

    @state.setter
    def state(self, value: typing.Optional[str]):
        return jsii.set(self, "state", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CreateRuleProperty(jsii.compat.TypedDict, total=False):
        times: typing.List[str]
        """``CfnLifecyclePolicy.CreateRuleProperty.Times``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-createrule.html#cfn-dlm-lifecyclepolicy-createrule-times
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.CreateRuleProperty", jsii_struct_bases=[_CreateRuleProperty])
    class CreateRuleProperty(_CreateRuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-createrule.html
        Stability:
            stable
        """
        interval: jsii.Number
        """``CfnLifecyclePolicy.CreateRuleProperty.Interval``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-createrule.html#cfn-dlm-lifecyclepolicy-createrule-interval
        Stability:
            stable
        """

        intervalUnit: str
        """``CfnLifecyclePolicy.CreateRuleProperty.IntervalUnit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-createrule.html#cfn-dlm-lifecyclepolicy-createrule-intervalunit
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.ParametersProperty", jsii_struct_bases=[])
    class ParametersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-parameters.html
        Stability:
            stable
        """
        excludeBootVolume: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnLifecyclePolicy.ParametersProperty.ExcludeBootVolume``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-parameters.html#cfn-dlm-lifecyclepolicy-parameters-excludebootvolume
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.PolicyDetailsProperty", jsii_struct_bases=[])
    class PolicyDetailsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html
        Stability:
            stable
        """
        parameters: typing.Union[aws_cdk.core.IResolvable, "CfnLifecyclePolicy.ParametersProperty"]
        """``CfnLifecyclePolicy.PolicyDetailsProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-parameters
        Stability:
            stable
        """

        policyType: str
        """``CfnLifecyclePolicy.PolicyDetailsProperty.PolicyType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-policytype
        Stability:
            stable
        """

        resourceTypes: typing.List[str]
        """``CfnLifecyclePolicy.PolicyDetailsProperty.ResourceTypes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-resourcetypes
        Stability:
            stable
        """

        schedules: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnLifecyclePolicy.ScheduleProperty"]]]
        """``CfnLifecyclePolicy.PolicyDetailsProperty.Schedules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-schedules
        Stability:
            stable
        """

        targetTags: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]
        """``CfnLifecyclePolicy.PolicyDetailsProperty.TargetTags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-targettags
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.RetainRuleProperty", jsii_struct_bases=[])
    class RetainRuleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-retainrule.html
        Stability:
            stable
        """
        count: jsii.Number
        """``CfnLifecyclePolicy.RetainRuleProperty.Count``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-retainrule.html#cfn-dlm-lifecyclepolicy-retainrule-count
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.ScheduleProperty", jsii_struct_bases=[])
    class ScheduleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html
        Stability:
            stable
        """
        copyTags: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnLifecyclePolicy.ScheduleProperty.CopyTags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-copytags
        Stability:
            stable
        """

        createRule: typing.Union[aws_cdk.core.IResolvable, "CfnLifecyclePolicy.CreateRuleProperty"]
        """``CfnLifecyclePolicy.ScheduleProperty.CreateRule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-createrule
        Stability:
            stable
        """

        name: str
        """``CfnLifecyclePolicy.ScheduleProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-name
        Stability:
            stable
        """

        retainRule: typing.Union[aws_cdk.core.IResolvable, "CfnLifecyclePolicy.RetainRuleProperty"]
        """``CfnLifecyclePolicy.ScheduleProperty.RetainRule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-retainrule
        Stability:
            stable
        """

        tagsToAdd: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]
        """``CfnLifecyclePolicy.ScheduleProperty.TagsToAdd``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-tagstoadd
        Stability:
            stable
        """

        variableTags: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]
        """``CfnLifecyclePolicy.ScheduleProperty.VariableTags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-variabletags
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicyProps", jsii_struct_bases=[])
class CfnLifecyclePolicyProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::DLM::LifecyclePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html
    Stability:
        stable
    """
    description: str
    """``AWS::DLM::LifecyclePolicy.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-description
    Stability:
        stable
    """

    executionRoleArn: str
    """``AWS::DLM::LifecyclePolicy.ExecutionRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-executionrolearn
    Stability:
        stable
    """

    policyDetails: typing.Union["CfnLifecyclePolicy.PolicyDetailsProperty", aws_cdk.core.IResolvable]
    """``AWS::DLM::LifecyclePolicy.PolicyDetails``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-policydetails
    Stability:
        stable
    """

    state: str
    """``AWS::DLM::LifecyclePolicy.State``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-state
    Stability:
        stable
    """

__all__ = ["CfnLifecyclePolicy", "CfnLifecyclePolicyProps", "__jsii_assembly__"]

publication.publish()
