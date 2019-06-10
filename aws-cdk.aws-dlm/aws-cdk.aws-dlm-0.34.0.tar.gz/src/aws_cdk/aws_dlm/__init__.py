import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-dlm", "0.34.0", __name__, "aws-dlm@0.34.0.jsii.tgz")
class CfnLifecyclePolicy(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy"):
    """A CloudFormation ``AWS::DLM::LifecyclePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DLM::LifecyclePolicy
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: typing.Optional[str]=None, execution_role_arn: typing.Optional[str]=None, policy_details: typing.Optional[typing.Union[typing.Optional["PolicyDetailsProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None, state: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::DLM::LifecyclePolicy``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::DLM::LifecyclePolicy.Description``.
            executionRoleArn: ``AWS::DLM::LifecyclePolicy.ExecutionRoleArn``.
            policyDetails: ``AWS::DLM::LifecyclePolicy.PolicyDetails``.
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
    @jsii.member(jsii_name="lifecyclePolicyArn")
    def lifecycle_policy_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "lifecyclePolicyArn")

    @property
    @jsii.member(jsii_name="lifecyclePolicyId")
    def lifecycle_policy_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "lifecyclePolicyId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnLifecyclePolicyProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CreateRuleProperty(jsii.compat.TypedDict, total=False):
        times: typing.List[str]
        """``CfnLifecyclePolicy.CreateRuleProperty.Times``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-createrule.html#cfn-dlm-lifecyclepolicy-createrule-times
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.CreateRuleProperty", jsii_struct_bases=[_CreateRuleProperty])
    class CreateRuleProperty(_CreateRuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-createrule.html
        Stability:
            experimental
        """
        interval: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLifecyclePolicy.CreateRuleProperty.Interval``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-createrule.html#cfn-dlm-lifecyclepolicy-createrule-interval
        Stability:
            experimental
        """

        intervalUnit: str
        """``CfnLifecyclePolicy.CreateRuleProperty.IntervalUnit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-createrule.html#cfn-dlm-lifecyclepolicy-createrule-intervalunit
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.PolicyDetailsProperty", jsii_struct_bases=[])
    class PolicyDetailsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html
        Stability:
            experimental
        """
        resourceTypes: typing.List[str]
        """``CfnLifecyclePolicy.PolicyDetailsProperty.ResourceTypes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-resourcetypes
        Stability:
            experimental
        """

        schedules: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnLifecyclePolicy.ScheduleProperty"]]]
        """``CfnLifecyclePolicy.PolicyDetailsProperty.Schedules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-schedules
        Stability:
            experimental
        """

        targetTags: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, aws_cdk.cdk.CfnTag]]]
        """``CfnLifecyclePolicy.PolicyDetailsProperty.TargetTags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-policydetails.html#cfn-dlm-lifecyclepolicy-policydetails-targettags
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.RetainRuleProperty", jsii_struct_bases=[])
    class RetainRuleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-retainrule.html
        Stability:
            experimental
        """
        count: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnLifecyclePolicy.RetainRuleProperty.Count``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-retainrule.html#cfn-dlm-lifecyclepolicy-retainrule-count
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicy.ScheduleProperty", jsii_struct_bases=[])
    class ScheduleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html
        Stability:
            experimental
        """
        copyTags: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnLifecyclePolicy.ScheduleProperty.CopyTags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-copytags
        Stability:
            experimental
        """

        createRule: typing.Union[aws_cdk.cdk.Token, "CfnLifecyclePolicy.CreateRuleProperty"]
        """``CfnLifecyclePolicy.ScheduleProperty.CreateRule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-createrule
        Stability:
            experimental
        """

        name: str
        """``CfnLifecyclePolicy.ScheduleProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-name
        Stability:
            experimental
        """

        retainRule: typing.Union[aws_cdk.cdk.Token, "CfnLifecyclePolicy.RetainRuleProperty"]
        """``CfnLifecyclePolicy.ScheduleProperty.RetainRule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-retainrule
        Stability:
            experimental
        """

        tagsToAdd: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, aws_cdk.cdk.CfnTag]]]
        """``CfnLifecyclePolicy.ScheduleProperty.TagsToAdd``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dlm-lifecyclepolicy-schedule.html#cfn-dlm-lifecyclepolicy-schedule-tagstoadd
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-dlm.CfnLifecyclePolicyProps", jsii_struct_bases=[])
class CfnLifecyclePolicyProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::DLM::LifecyclePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html
    Stability:
        experimental
    """
    description: str
    """``AWS::DLM::LifecyclePolicy.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-description
    Stability:
        experimental
    """

    executionRoleArn: str
    """``AWS::DLM::LifecyclePolicy.ExecutionRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-executionrolearn
    Stability:
        experimental
    """

    policyDetails: typing.Union["CfnLifecyclePolicy.PolicyDetailsProperty", aws_cdk.cdk.Token]
    """``AWS::DLM::LifecyclePolicy.PolicyDetails``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-policydetails
    Stability:
        experimental
    """

    state: str
    """``AWS::DLM::LifecyclePolicy.State``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dlm-lifecyclepolicy.html#cfn-dlm-lifecyclepolicy-state
    Stability:
        experimental
    """

__all__ = ["CfnLifecyclePolicy", "CfnLifecyclePolicyProps", "__jsii_assembly__"]

publication.publish()
