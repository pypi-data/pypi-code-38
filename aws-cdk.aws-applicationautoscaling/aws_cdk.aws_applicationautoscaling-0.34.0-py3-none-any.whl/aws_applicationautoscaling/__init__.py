import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_autoscaling_common
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_iam
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-applicationautoscaling", "0.34.0", __name__, "aws-applicationautoscaling@0.34.0.jsii.tgz")
@jsii.data_type_optionals(jsii_struct_bases=[])
class _AdjustmentTier(jsii.compat.TypedDict, total=False):
    lowerBound: jsii.Number
    """Lower bound where this scaling tier applies.

    The scaling tier applies if the difference between the metric
    value and its alarm threshold is higher than this value.

    Default:
        -Infinity if this is the first tier, otherwise the upperBound of the previous tier

    Stability:
        experimental
    """
    upperBound: jsii.Number
    """Upper bound where this scaling tier applies.

    The scaling tier applies if the difference between the metric
    value and its alarm threshold is lower than this value.

    Default:
        +Infinity

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.AdjustmentTier", jsii_struct_bases=[_AdjustmentTier])
class AdjustmentTier(_AdjustmentTier):
    """An adjustment.

    Stability:
        experimental
    """
    adjustment: jsii.Number
    """What number to adjust the capacity with.

    The number is interpeted as an added capacity, a new fixed capacity or an
    added percentage depending on the AdjustmentType value of the
    StepScalingPolicy.

    Can be positive or negative.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-applicationautoscaling.AdjustmentType")
class AdjustmentType(enum.Enum):
    """How adjustment numbers are interpreted.

    Stability:
        experimental
    """
    ChangeInCapacity = "ChangeInCapacity"
    """Add the adjustment number to the current capacity.

    A positive number increases capacity, a negative number decreases capacity.

    Stability:
        experimental
    """
    PercentChangeInCapacity = "PercentChangeInCapacity"
    """Add this percentage of the current capacity to itself.

    The number must be between -100 and 100; a positive number increases
    capacity and a negative number decreases it.

    Stability:
        experimental
    """
    ExactCapacity = "ExactCapacity"
    """Make the capacity equal to the exact number given.

    Stability:
        experimental
    """

class BaseScalableAttribute(aws_cdk.cdk.Construct, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-applicationautoscaling.BaseScalableAttribute"):
    """Represent an attribute for which autoscaling can be configured.

    This class is basically a light wrapper around ScalableTarget, but with
    all methods protected instead of public so they can be selectively
    exposed and/or more specific versions of them can be exposed by derived
    classes for individual services support autoscaling.

    Typical use cases:

    - Hide away the PredefinedMetric enum for target tracking policies.
    - Don't expose all scaling methods (for example Dynamo tables don't support
      Step Scaling, so the Dynamo subclass won't expose this method).

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _BaseScalableAttributeProxy

    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, dimension: str, resource_id: str, role: aws_cdk.aws_iam.IRole, service_namespace: "ServiceNamespace", max_capacity: jsii.Number, min_capacity: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            dimension: Scalable dimension of the attribute.
            resourceId: Resource ID of the attribute.
            role: Role to use for scaling.
            serviceNamespace: Service namespace of the scalable attribute.
            maxCapacity: Maximum capacity to scale to.
            minCapacity: Minimum capacity to scale to. Default: 1

        Stability:
            experimental
        """
        props: BaseScalableAttributeProps = {"dimension": dimension, "resourceId": resource_id, "role": role, "serviceNamespace": service_namespace, "maxCapacity": max_capacity}

        if min_capacity is not None:
            props["minCapacity"] = min_capacity

        jsii.create(BaseScalableAttribute, self, [scope, id, props])

    @jsii.member(jsii_name="doScaleOnMetric")
    def _do_scale_on_metric(self, id: str, *, metric: aws_cdk.aws_cloudwatch.Metric, scaling_steps: typing.List["ScalingInterval"], adjustment_type: typing.Optional["AdjustmentType"]=None, cooldown_sec: typing.Optional[jsii.Number]=None, min_adjustment_magnitude: typing.Optional[jsii.Number]=None) -> None:
        """Scale out or in based on a metric value.

        Arguments:
            id: -
            props: -
            metric: Metric to scale on.
            scalingSteps: The intervals for scaling. Maps a range of metric values to a particular scaling behavior.
            adjustmentType: How the adjustment numbers inside 'intervals' are interpreted. Default: ChangeInCapacity
            cooldownSec: Grace period after scaling activity. Subsequent scale outs during the cooldown period are squashed so that only the biggest scale out happens. Subsequent scale ins during the cooldown period are ignored. Default: No cooldown period
            minAdjustmentMagnitude: Minimum absolute number to adjust capacity with as result of percentage scaling. Only when using AdjustmentType = PercentChangeInCapacity, this number controls the minimum absolute effect size. Default: No minimum scaling effect

        Stability:
            experimental
        """
        props: BasicStepScalingPolicyProps = {"metric": metric, "scalingSteps": scaling_steps}

        if adjustment_type is not None:
            props["adjustmentType"] = adjustment_type

        if cooldown_sec is not None:
            props["cooldownSec"] = cooldown_sec

        if min_adjustment_magnitude is not None:
            props["minAdjustmentMagnitude"] = min_adjustment_magnitude

        return jsii.invoke(self, "doScaleOnMetric", [id, props])

    @jsii.member(jsii_name="doScaleOnSchedule")
    def _do_scale_on_schedule(self, id: str, *, schedule: str, end_time: typing.Optional[datetime.datetime]=None, max_capacity: typing.Optional[jsii.Number]=None, min_capacity: typing.Optional[jsii.Number]=None, start_time: typing.Optional[datetime.datetime]=None) -> None:
        """Scale out or in based on time.

        Arguments:
            id: -
            props: -
            schedule: When to perform this action. Support formats: - at(yyyy-mm-ddThh:mm:ss) - rate(value unit) - cron(fields) "At" expressions are useful for one-time schedules. Specify the time in UTC. For "rate" expressions, value is a positive integer, and unit is minute, minutes, hour, hours, day, or days. For more information about cron expressions, see https://en.wikipedia.org/wiki/Cron.
            endTime: When this scheduled action expires. Default: The rule never expires.
            maxCapacity: The new maximum capacity. During the scheduled time, the current capacity is above the maximum capacity, Application Auto Scaling scales in to the maximum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new maximum capacity
            minCapacity: The new minimum capacity. During the scheduled time, if the current capacity is below the minimum capacity, Application Auto Scaling scales out to the minimum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new minimum capacity
            startTime: When this scheduled action becomes active. Default: The rule is activate immediately

        Stability:
            experimental
        """
        props: ScalingSchedule = {"schedule": schedule}

        if end_time is not None:
            props["endTime"] = end_time

        if max_capacity is not None:
            props["maxCapacity"] = max_capacity

        if min_capacity is not None:
            props["minCapacity"] = min_capacity

        if start_time is not None:
            props["startTime"] = start_time

        return jsii.invoke(self, "doScaleOnSchedule", [id, props])

    @jsii.member(jsii_name="doScaleToTrackMetric")
    def _do_scale_to_track_metric(self, id: str, *, target_value: jsii.Number, custom_metric: typing.Optional[aws_cdk.aws_cloudwatch.Metric]=None, predefined_metric: typing.Optional["PredefinedMetric"]=None, resource_label: typing.Optional[str]=None, disable_scale_in: typing.Optional[bool]=None, policy_name: typing.Optional[str]=None, scale_in_cooldown_sec: typing.Optional[jsii.Number]=None, scale_out_cooldown_sec: typing.Optional[jsii.Number]=None) -> None:
        """Scale out or in in order to keep a metric around a target value.

        Arguments:
            id: -
            props: -
            targetValue: The target value for the metric.
            customMetric: A custom metric for application autoscaling. The metric must track utilization. Scaling out will happen if the metric is higher than the target value, scaling in will happen in the metric is lower than the target value. Exactly one of customMetric or predefinedMetric must be specified. Default: - No custom metric.
            predefinedMetric: A predefined metric for application autoscaling. The metric must track utilization. Scaling out will happen if the metric is higher than the target value, scaling in will happen in the metric is lower than the target value. Exactly one of customMetric or predefinedMetric must be specified. Default: - No predefined metrics.
            resourceLabel: Identify the resource associated with the metric type. Only used for predefined metric ALBRequestCountPerTarget. Default: - No resource label.
            disableScaleIn: Indicates whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. Default: false
            policyName: A name for the scaling policy. Default: - Automatically generated name.
            scaleInCooldownSec: Period after a scale in activity completes before another scale in activity can start. Default: - No scale in cooldown.
            scaleOutCooldownSec: Period after a scale out activity completes before another scale out activity can start. Default: - No scale out cooldown.

        Stability:
            experimental
        """
        props: BasicTargetTrackingScalingPolicyProps = {"targetValue": target_value}

        if custom_metric is not None:
            props["customMetric"] = custom_metric

        if predefined_metric is not None:
            props["predefinedMetric"] = predefined_metric

        if resource_label is not None:
            props["resourceLabel"] = resource_label

        if disable_scale_in is not None:
            props["disableScaleIn"] = disable_scale_in

        if policy_name is not None:
            props["policyName"] = policy_name

        if scale_in_cooldown_sec is not None:
            props["scaleInCooldownSec"] = scale_in_cooldown_sec

        if scale_out_cooldown_sec is not None:
            props["scaleOutCooldownSec"] = scale_out_cooldown_sec

        return jsii.invoke(self, "doScaleToTrackMetric", [id, props])

    @property
    @jsii.member(jsii_name="props")
    def _props(self) -> "BaseScalableAttributeProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")


class _BaseScalableAttributeProxy(BaseScalableAttribute):
    pass

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.BaseTargetTrackingProps", jsii_struct_bases=[])
class BaseTargetTrackingProps(jsii.compat.TypedDict, total=False):
    """Base interface for target tracking props.

    Contains the attributes that are common to target tracking policies,
    except the ones relating to the metric and to the scalable target.

    This interface is reused by more specific target tracking props objects
    in other services.

    Stability:
        experimental
    """
    disableScaleIn: bool
    """Indicates whether scale in by the target tracking policy is disabled.

    If the value is true, scale in is disabled and the target tracking policy
    won't remove capacity from the scalable resource. Otherwise, scale in is
    enabled and the target tracking policy can remove capacity from the
    scalable resource.

    Default:
        false

    Stability:
        experimental
    """

    policyName: str
    """A name for the scaling policy.

    Default:
        - Automatically generated name.

    Stability:
        experimental
    """

    scaleInCooldownSec: jsii.Number
    """Period after a scale in activity completes before another scale in activity can start.

    Default:
        - No scale in cooldown.

    Stability:
        experimental
    """

    scaleOutCooldownSec: jsii.Number
    """Period after a scale out activity completes before another scale out activity can start.

    Default:
        - No scale out cooldown.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _BasicStepScalingPolicyProps(jsii.compat.TypedDict, total=False):
    adjustmentType: "AdjustmentType"
    """How the adjustment numbers inside 'intervals' are interpreted.

    Default:
        ChangeInCapacity

    Stability:
        experimental
    """
    cooldownSec: jsii.Number
    """Grace period after scaling activity.

    Subsequent scale outs during the cooldown period are squashed so that only
    the biggest scale out happens.

    Subsequent scale ins during the cooldown period are ignored.

    Default:
        No cooldown period

    See:
        https://docs.aws.amazon.com/autoscaling/application/APIReference/API_StepScalingPolicyConfiguration.html
    Stability:
        experimental
    """
    minAdjustmentMagnitude: jsii.Number
    """Minimum absolute number to adjust capacity with as result of percentage scaling.

    Only when using AdjustmentType = PercentChangeInCapacity, this number controls
    the minimum absolute effect size.

    Default:
        No minimum scaling effect

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.BasicStepScalingPolicyProps", jsii_struct_bases=[_BasicStepScalingPolicyProps])
class BasicStepScalingPolicyProps(_BasicStepScalingPolicyProps):
    """
    Stability:
        experimental
    """
    metric: aws_cdk.aws_cloudwatch.Metric
    """Metric to scale on.

    Stability:
        experimental
    """

    scalingSteps: typing.List["ScalingInterval"]
    """The intervals for scaling.

    Maps a range of metric values to a particular scaling behavior.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[BaseTargetTrackingProps])
class _BasicTargetTrackingScalingPolicyProps(BaseTargetTrackingProps, jsii.compat.TypedDict, total=False):
    customMetric: aws_cdk.aws_cloudwatch.Metric
    """A custom metric for application autoscaling.

    The metric must track utilization. Scaling out will happen if the metric is higher than
    the target value, scaling in will happen in the metric is lower than the target value.

    Exactly one of customMetric or predefinedMetric must be specified.

    Default:
        - No custom metric.

    Stability:
        experimental
    """
    predefinedMetric: "PredefinedMetric"
    """A predefined metric for application autoscaling.

    The metric must track utilization. Scaling out will happen if the metric is higher than
    the target value, scaling in will happen in the metric is lower than the target value.

    Exactly one of customMetric or predefinedMetric must be specified.

    Default:
        - No predefined metrics.

    Stability:
        experimental
    """
    resourceLabel: str
    """Identify the resource associated with the metric type.

    Only used for predefined metric ALBRequestCountPerTarget.

    Default:
        - No resource label.

    Stability:
        experimental

    Example::
        app/<load-balancer-name>/<load-balancer-id>/targetgroup/<target-group-name>/<target-group-id>
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.BasicTargetTrackingScalingPolicyProps", jsii_struct_bases=[_BasicTargetTrackingScalingPolicyProps])
class BasicTargetTrackingScalingPolicyProps(_BasicTargetTrackingScalingPolicyProps):
    """Properties for a Target Tracking policy that include the metric but exclude the target.

    Stability:
        experimental
    """
    targetValue: jsii.Number
    """The target value for the metric.

    Stability:
        experimental
    """

class CfnScalableTarget(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalableTarget"):
    """A CloudFormation ``AWS::ApplicationAutoScaling::ScalableTarget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApplicationAutoScaling::ScalableTarget
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, max_capacity: typing.Union[jsii.Number, aws_cdk.cdk.Token], min_capacity: typing.Union[jsii.Number, aws_cdk.cdk.Token], resource_id: str, role_arn: str, scalable_dimension: str, service_namespace: str, scheduled_actions: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "ScheduledActionProperty"]]]]]=None) -> None:
        """Create a new ``AWS::ApplicationAutoScaling::ScalableTarget``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            maxCapacity: ``AWS::ApplicationAutoScaling::ScalableTarget.MaxCapacity``.
            minCapacity: ``AWS::ApplicationAutoScaling::ScalableTarget.MinCapacity``.
            resourceId: ``AWS::ApplicationAutoScaling::ScalableTarget.ResourceId``.
            roleArn: ``AWS::ApplicationAutoScaling::ScalableTarget.RoleARN``.
            scalableDimension: ``AWS::ApplicationAutoScaling::ScalableTarget.ScalableDimension``.
            serviceNamespace: ``AWS::ApplicationAutoScaling::ScalableTarget.ServiceNamespace``.
            scheduledActions: ``AWS::ApplicationAutoScaling::ScalableTarget.ScheduledActions``.

        Stability:
            experimental
        """
        props: CfnScalableTargetProps = {"maxCapacity": max_capacity, "minCapacity": min_capacity, "resourceId": resource_id, "roleArn": role_arn, "scalableDimension": scalable_dimension, "serviceNamespace": service_namespace}

        if scheduled_actions is not None:
            props["scheduledActions"] = scheduled_actions

        jsii.create(CfnScalableTarget, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnScalableTargetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="scalableTargetId")
    def scalable_target_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "scalableTargetId")

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalableTarget.ScalableTargetActionProperty", jsii_struct_bases=[])
    class ScalableTargetActionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scalabletargetaction.html
        Stability:
            experimental
        """
        maxCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnScalableTarget.ScalableTargetActionProperty.MaxCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scalabletargetaction.html#cfn-applicationautoscaling-scalabletarget-scalabletargetaction-maxcapacity
        Stability:
            experimental
        """

        minCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnScalableTarget.ScalableTargetActionProperty.MinCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scalabletargetaction.html#cfn-applicationautoscaling-scalabletarget-scalabletargetaction-mincapacity
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ScheduledActionProperty(jsii.compat.TypedDict, total=False):
        endTime: typing.Union[aws_cdk.cdk.Token, datetime.datetime]
        """``CfnScalableTarget.ScheduledActionProperty.EndTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scheduledaction.html#cfn-applicationautoscaling-scalabletarget-scheduledaction-endtime
        Stability:
            experimental
        """
        scalableTargetAction: typing.Union[aws_cdk.cdk.Token, "CfnScalableTarget.ScalableTargetActionProperty"]
        """``CfnScalableTarget.ScheduledActionProperty.ScalableTargetAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scheduledaction.html#cfn-applicationautoscaling-scalabletarget-scheduledaction-scalabletargetaction
        Stability:
            experimental
        """
        startTime: typing.Union[aws_cdk.cdk.Token, datetime.datetime]
        """``CfnScalableTarget.ScheduledActionProperty.StartTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scheduledaction.html#cfn-applicationautoscaling-scalabletarget-scheduledaction-starttime
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalableTarget.ScheduledActionProperty", jsii_struct_bases=[_ScheduledActionProperty])
    class ScheduledActionProperty(_ScheduledActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scheduledaction.html
        Stability:
            experimental
        """
        schedule: str
        """``CfnScalableTarget.ScheduledActionProperty.Schedule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scheduledaction.html#cfn-applicationautoscaling-scalabletarget-scheduledaction-schedule
        Stability:
            experimental
        """

        scheduledActionName: str
        """``CfnScalableTarget.ScheduledActionProperty.ScheduledActionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scheduledaction.html#cfn-applicationautoscaling-scalabletarget-scheduledaction-scheduledactionname
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnScalableTargetProps(jsii.compat.TypedDict, total=False):
    scheduledActions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnScalableTarget.ScheduledActionProperty"]]]
    """``AWS::ApplicationAutoScaling::ScalableTarget.ScheduledActions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-scheduledactions
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalableTargetProps", jsii_struct_bases=[_CfnScalableTargetProps])
class CfnScalableTargetProps(_CfnScalableTargetProps):
    """Properties for defining a ``AWS::ApplicationAutoScaling::ScalableTarget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html
    Stability:
        experimental
    """
    maxCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ApplicationAutoScaling::ScalableTarget.MaxCapacity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-maxcapacity
    Stability:
        experimental
    """

    minCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ApplicationAutoScaling::ScalableTarget.MinCapacity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-mincapacity
    Stability:
        experimental
    """

    resourceId: str
    """``AWS::ApplicationAutoScaling::ScalableTarget.ResourceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-resourceid
    Stability:
        experimental
    """

    roleArn: str
    """``AWS::ApplicationAutoScaling::ScalableTarget.RoleARN``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-rolearn
    Stability:
        experimental
    """

    scalableDimension: str
    """``AWS::ApplicationAutoScaling::ScalableTarget.ScalableDimension``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-scalabledimension
    Stability:
        experimental
    """

    serviceNamespace: str
    """``AWS::ApplicationAutoScaling::ScalableTarget.ServiceNamespace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-servicenamespace
    Stability:
        experimental
    """

class CfnScalingPolicy(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy"):
    """A CloudFormation ``AWS::ApplicationAutoScaling::ScalingPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApplicationAutoScaling::ScalingPolicy
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, policy_name: str, policy_type: str, resource_id: typing.Optional[str]=None, scalable_dimension: typing.Optional[str]=None, scaling_target_id: typing.Optional[str]=None, service_namespace: typing.Optional[str]=None, step_scaling_policy_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["StepScalingPolicyConfigurationProperty"]]]=None, target_tracking_scaling_policy_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["TargetTrackingScalingPolicyConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::ApplicationAutoScaling::ScalingPolicy``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            policyName: ``AWS::ApplicationAutoScaling::ScalingPolicy.PolicyName``.
            policyType: ``AWS::ApplicationAutoScaling::ScalingPolicy.PolicyType``.
            resourceId: ``AWS::ApplicationAutoScaling::ScalingPolicy.ResourceId``.
            scalableDimension: ``AWS::ApplicationAutoScaling::ScalingPolicy.ScalableDimension``.
            scalingTargetId: ``AWS::ApplicationAutoScaling::ScalingPolicy.ScalingTargetId``.
            serviceNamespace: ``AWS::ApplicationAutoScaling::ScalingPolicy.ServiceNamespace``.
            stepScalingPolicyConfiguration: ``AWS::ApplicationAutoScaling::ScalingPolicy.StepScalingPolicyConfiguration``.
            targetTrackingScalingPolicyConfiguration: ``AWS::ApplicationAutoScaling::ScalingPolicy.TargetTrackingScalingPolicyConfiguration``.

        Stability:
            experimental
        """
        props: CfnScalingPolicyProps = {"policyName": policy_name, "policyType": policy_type}

        if resource_id is not None:
            props["resourceId"] = resource_id

        if scalable_dimension is not None:
            props["scalableDimension"] = scalable_dimension

        if scaling_target_id is not None:
            props["scalingTargetId"] = scaling_target_id

        if service_namespace is not None:
            props["serviceNamespace"] = service_namespace

        if step_scaling_policy_configuration is not None:
            props["stepScalingPolicyConfiguration"] = step_scaling_policy_configuration

        if target_tracking_scaling_policy_configuration is not None:
            props["targetTrackingScalingPolicyConfiguration"] = target_tracking_scaling_policy_configuration

        jsii.create(CfnScalingPolicy, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnScalingPolicyProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="scalingPolicyArn")
    def scaling_policy_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "scalingPolicyArn")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CustomizedMetricSpecificationProperty(jsii.compat.TypedDict, total=False):
        dimensions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnScalingPolicy.MetricDimensionProperty"]]]
        """``CfnScalingPolicy.CustomizedMetricSpecificationProperty.Dimensions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-customizedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-customizedmetricspecification-dimensions
        Stability:
            experimental
        """
        unit: str
        """``CfnScalingPolicy.CustomizedMetricSpecificationProperty.Unit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-customizedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-customizedmetricspecification-unit
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy.CustomizedMetricSpecificationProperty", jsii_struct_bases=[_CustomizedMetricSpecificationProperty])
    class CustomizedMetricSpecificationProperty(_CustomizedMetricSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-customizedmetricspecification.html
        Stability:
            experimental
        """
        metricName: str
        """``CfnScalingPolicy.CustomizedMetricSpecificationProperty.MetricName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-customizedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-customizedmetricspecification-metricname
        Stability:
            experimental
        """

        namespace: str
        """``CfnScalingPolicy.CustomizedMetricSpecificationProperty.Namespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-customizedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-customizedmetricspecification-namespace
        Stability:
            experimental
        """

        statistic: str
        """``CfnScalingPolicy.CustomizedMetricSpecificationProperty.Statistic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-customizedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-customizedmetricspecification-statistic
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy.MetricDimensionProperty", jsii_struct_bases=[])
    class MetricDimensionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-metricdimension.html
        Stability:
            experimental
        """
        name: str
        """``CfnScalingPolicy.MetricDimensionProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-metricdimension.html#cfn-applicationautoscaling-scalingpolicy-metricdimension-name
        Stability:
            experimental
        """

        value: str
        """``CfnScalingPolicy.MetricDimensionProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-metricdimension.html#cfn-applicationautoscaling-scalingpolicy-metricdimension-value
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _PredefinedMetricSpecificationProperty(jsii.compat.TypedDict, total=False):
        resourceLabel: str
        """``CfnScalingPolicy.PredefinedMetricSpecificationProperty.ResourceLabel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-predefinedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-predefinedmetricspecification-resourcelabel
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy.PredefinedMetricSpecificationProperty", jsii_struct_bases=[_PredefinedMetricSpecificationProperty])
    class PredefinedMetricSpecificationProperty(_PredefinedMetricSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-predefinedmetricspecification.html
        Stability:
            experimental
        """
        predefinedMetricType: str
        """``CfnScalingPolicy.PredefinedMetricSpecificationProperty.PredefinedMetricType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-predefinedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-predefinedmetricspecification-predefinedmetrictype
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _StepAdjustmentProperty(jsii.compat.TypedDict, total=False):
        metricIntervalLowerBound: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnScalingPolicy.StepAdjustmentProperty.MetricIntervalLowerBound``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment-metricintervallowerbound
        Stability:
            experimental
        """
        metricIntervalUpperBound: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnScalingPolicy.StepAdjustmentProperty.MetricIntervalUpperBound``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment-metricintervalupperbound
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy.StepAdjustmentProperty", jsii_struct_bases=[_StepAdjustmentProperty])
    class StepAdjustmentProperty(_StepAdjustmentProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment.html
        Stability:
            experimental
        """
        scalingAdjustment: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnScalingPolicy.StepAdjustmentProperty.ScalingAdjustment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment-scalingadjustment
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy.StepScalingPolicyConfigurationProperty", jsii_struct_bases=[])
    class StepScalingPolicyConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration.html
        Stability:
            experimental
        """
        adjustmentType: str
        """``CfnScalingPolicy.StepScalingPolicyConfigurationProperty.AdjustmentType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-adjustmenttype
        Stability:
            experimental
        """

        cooldown: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnScalingPolicy.StepScalingPolicyConfigurationProperty.Cooldown``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-cooldown
        Stability:
            experimental
        """

        metricAggregationType: str
        """``CfnScalingPolicy.StepScalingPolicyConfigurationProperty.MetricAggregationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-metricaggregationtype
        Stability:
            experimental
        """

        minAdjustmentMagnitude: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnScalingPolicy.StepScalingPolicyConfigurationProperty.MinAdjustmentMagnitude``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-minadjustmentmagnitude
        Stability:
            experimental
        """

        stepAdjustments: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnScalingPolicy.StepAdjustmentProperty"]]]
        """``CfnScalingPolicy.StepScalingPolicyConfigurationProperty.StepAdjustments``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustments
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _TargetTrackingScalingPolicyConfigurationProperty(jsii.compat.TypedDict, total=False):
        customizedMetricSpecification: typing.Union[aws_cdk.cdk.Token, "CfnScalingPolicy.CustomizedMetricSpecificationProperty"]
        """``CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty.CustomizedMetricSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration-customizedmetricspecification
        Stability:
            experimental
        """
        disableScaleIn: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty.DisableScaleIn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration-disablescalein
        Stability:
            experimental
        """
        predefinedMetricSpecification: typing.Union[aws_cdk.cdk.Token, "CfnScalingPolicy.PredefinedMetricSpecificationProperty"]
        """``CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty.PredefinedMetricSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration-predefinedmetricspecification
        Stability:
            experimental
        """
        scaleInCooldown: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty.ScaleInCooldown``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration-scaleincooldown
        Stability:
            experimental
        """
        scaleOutCooldown: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty.ScaleOutCooldown``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration-scaleoutcooldown
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty", jsii_struct_bases=[_TargetTrackingScalingPolicyConfigurationProperty])
    class TargetTrackingScalingPolicyConfigurationProperty(_TargetTrackingScalingPolicyConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html
        Stability:
            experimental
        """
        targetValue: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty.TargetValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration-targetvalue
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnScalingPolicyProps(jsii.compat.TypedDict, total=False):
    resourceId: str
    """``AWS::ApplicationAutoScaling::ScalingPolicy.ResourceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-resourceid
    Stability:
        experimental
    """
    scalableDimension: str
    """``AWS::ApplicationAutoScaling::ScalingPolicy.ScalableDimension``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-scalabledimension
    Stability:
        experimental
    """
    scalingTargetId: str
    """``AWS::ApplicationAutoScaling::ScalingPolicy.ScalingTargetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-scalingtargetid
    Stability:
        experimental
    """
    serviceNamespace: str
    """``AWS::ApplicationAutoScaling::ScalingPolicy.ServiceNamespace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-servicenamespace
    Stability:
        experimental
    """
    stepScalingPolicyConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnScalingPolicy.StepScalingPolicyConfigurationProperty"]
    """``AWS::ApplicationAutoScaling::ScalingPolicy.StepScalingPolicyConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration
    Stability:
        experimental
    """
    targetTrackingScalingPolicyConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty"]
    """``AWS::ApplicationAutoScaling::ScalingPolicy.TargetTrackingScalingPolicyConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicyProps", jsii_struct_bases=[_CfnScalingPolicyProps])
class CfnScalingPolicyProps(_CfnScalingPolicyProps):
    """Properties for defining a ``AWS::ApplicationAutoScaling::ScalingPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html
    Stability:
        experimental
    """
    policyName: str
    """``AWS::ApplicationAutoScaling::ScalingPolicy.PolicyName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-policyname
    Stability:
        experimental
    """

    policyType: str
    """``AWS::ApplicationAutoScaling::ScalingPolicy.PolicyType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-policytype
    Stability:
        experimental
    """

class Cron(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.Cron"):
    """Helper class to generate Cron expressions.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(Cron, self, [])

    @jsii.member(jsii_name="dailyUtc")
    @classmethod
    def daily_utc(cls, hour: jsii.Number, minute: typing.Optional[jsii.Number]=None) -> str:
        """Return a cron expression to run every day at a particular time.

        The time is specified in UTC.

        Arguments:
            hour: The hour in UTC to schedule this action.
            minute: The minute in the our to schedule this action (defaults to 0).

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "dailyUtc", [hour, minute])


@jsii.data_type_optionals(jsii_struct_bases=[])
class _EnableScalingProps(jsii.compat.TypedDict, total=False):
    minCapacity: jsii.Number
    """Minimum capacity to scale to.

    Default:
        1

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.EnableScalingProps", jsii_struct_bases=[_EnableScalingProps])
class EnableScalingProps(_EnableScalingProps):
    """Properties for enabling DynamoDB capacity scaling.

    Stability:
        experimental
    """
    maxCapacity: jsii.Number
    """Maximum capacity to scale to.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.BaseScalableAttributeProps", jsii_struct_bases=[EnableScalingProps])
class BaseScalableAttributeProps(EnableScalingProps, jsii.compat.TypedDict):
    """Properties for a ScalableTableAttribute.

    Stability:
        experimental
    """
    dimension: str
    """Scalable dimension of the attribute.

    Stability:
        experimental
    """

    resourceId: str
    """Resource ID of the attribute.

    Stability:
        experimental
    """

    role: aws_cdk.aws_iam.IRole
    """Role to use for scaling.

    Stability:
        experimental
    """

    serviceNamespace: "ServiceNamespace"
    """Service namespace of the scalable attribute.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-applicationautoscaling.IScalableTarget")
class IScalableTarget(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IScalableTargetProxy

    @property
    @jsii.member(jsii_name="scalableTargetId")
    def scalable_target_id(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IScalableTargetProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-applicationautoscaling.IScalableTarget"
    @property
    @jsii.member(jsii_name="scalableTargetId")
    def scalable_target_id(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "scalableTargetId")


@jsii.enum(jsii_type="@aws-cdk/aws-applicationautoscaling.MetricAggregationType")
class MetricAggregationType(enum.Enum):
    """How the scaling metric is going to be aggregated.

    Stability:
        experimental
    """
    Average = "Average"
    """Average.

    Stability:
        experimental
    """
    Minimum = "Minimum"
    """Minimum.

    Stability:
        experimental
    """
    Maximum = "Maximum"
    """Maximum.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-applicationautoscaling.PredefinedMetric")
class PredefinedMetric(enum.Enum):
    """One of the predefined autoscaling metrics.

    Stability:
        experimental
    """
    DynamoDBReadCapacityUtilization = "DynamoDBReadCapacityUtilization"
    """
    Stability:
        experimental
    """
    DynamoDBWriteCapacityUtilization = "DynamoDBWriteCapacityUtilization"
    """
    Stability:
        experimental
    """
    ALBRequestCountPerTarget = "ALBRequestCountPerTarget"
    """
    Stability:
        experimental
    """
    RDSReaderAverageCPUUtilization = "RDSReaderAverageCPUUtilization"
    """
    Stability:
        experimental
    """
    RDSReaderAverageDatabaseConnections = "RDSReaderAverageDatabaseConnections"
    """
    Stability:
        experimental
    """
    EC2SpotFleetRequestAverageCPUUtilization = "EC2SpotFleetRequestAverageCPUUtilization"
    """
    Stability:
        experimental
    """
    EC2SpotFleetRequestAverageNetworkIn = "EC2SpotFleetRequestAverageNetworkIn"
    """
    Stability:
        experimental
    """
    EC2SpotFleetRequestAverageNetworkOut = "EC2SpotFleetRequestAverageNetworkOut"
    """
    Stability:
        experimental
    """
    SageMakerVariantInvocationsPerInstance = "SageMakerVariantInvocationsPerInstance"
    """
    Stability:
        experimental
    """
    ECSServiceAverageCPUUtilization = "ECSServiceAverageCPUUtilization"
    """
    Stability:
        experimental
    """
    ECSServiceAverageMemoryUtilization = "ECSServiceAverageMemoryUtilization"
    """
    Stability:
        experimental
    """

@jsii.implements(IScalableTarget)
class ScalableTarget(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.ScalableTarget"):
    """Define a scalable target.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, max_capacity: jsii.Number, min_capacity: jsii.Number, resource_id: str, scalable_dimension: str, service_namespace: "ServiceNamespace", role: typing.Optional[aws_cdk.aws_iam.IRole]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            maxCapacity: The maximum value that Application Auto Scaling can use to scale a target during a scaling activity.
            minCapacity: The minimum value that Application Auto Scaling can use to scale a target during a scaling activity.
            resourceId: The resource identifier to associate with this scalable target. This string consists of the resource type and unique identifier.
            scalableDimension: The scalable dimension that's associated with the scalable target. Specify the service namespace, resource type, and scaling property.
            serviceNamespace: The namespace of the AWS service that provides the resource or custom-resource for a resource provided by your own application or service. For valid AWS service namespace values, see the RegisterScalableTarget action in the Application Auto Scaling API Reference.
            role: Role that allows Application Auto Scaling to modify your scalable target. Default: A role is automatically created

        Stability:
            experimental
        """
        props: ScalableTargetProps = {"maxCapacity": max_capacity, "minCapacity": min_capacity, "resourceId": resource_id, "scalableDimension": scalable_dimension, "serviceNamespace": service_namespace}

        if role is not None:
            props["role"] = role

        jsii.create(ScalableTarget, self, [scope, id, props])

    @jsii.member(jsii_name="fromScalableTargetId")
    @classmethod
    def from_scalable_target_id(cls, scope: aws_cdk.cdk.Construct, id: str, scalable_target_id: str) -> "IScalableTarget":
        """
        Arguments:
            scope: -
            id: -
            scalableTargetId: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromScalableTargetId", [scope, id, scalable_target_id])

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add a policy statement to the role's policy.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToRolePolicy", [statement])

    @jsii.member(jsii_name="scaleOnMetric")
    def scale_on_metric(self, id: str, *, metric: aws_cdk.aws_cloudwatch.Metric, scaling_steps: typing.List["ScalingInterval"], adjustment_type: typing.Optional["AdjustmentType"]=None, cooldown_sec: typing.Optional[jsii.Number]=None, min_adjustment_magnitude: typing.Optional[jsii.Number]=None) -> "StepScalingPolicy":
        """Scale out or in, in response to a metric.

        Arguments:
            id: -
            props: -
            metric: Metric to scale on.
            scalingSteps: The intervals for scaling. Maps a range of metric values to a particular scaling behavior.
            adjustmentType: How the adjustment numbers inside 'intervals' are interpreted. Default: ChangeInCapacity
            cooldownSec: Grace period after scaling activity. Subsequent scale outs during the cooldown period are squashed so that only the biggest scale out happens. Subsequent scale ins during the cooldown period are ignored. Default: No cooldown period
            minAdjustmentMagnitude: Minimum absolute number to adjust capacity with as result of percentage scaling. Only when using AdjustmentType = PercentChangeInCapacity, this number controls the minimum absolute effect size. Default: No minimum scaling effect

        Stability:
            experimental
        """
        props: BasicStepScalingPolicyProps = {"metric": metric, "scalingSteps": scaling_steps}

        if adjustment_type is not None:
            props["adjustmentType"] = adjustment_type

        if cooldown_sec is not None:
            props["cooldownSec"] = cooldown_sec

        if min_adjustment_magnitude is not None:
            props["minAdjustmentMagnitude"] = min_adjustment_magnitude

        return jsii.invoke(self, "scaleOnMetric", [id, props])

    @jsii.member(jsii_name="scaleOnSchedule")
    def scale_on_schedule(self, id: str, *, schedule: str, end_time: typing.Optional[datetime.datetime]=None, max_capacity: typing.Optional[jsii.Number]=None, min_capacity: typing.Optional[jsii.Number]=None, start_time: typing.Optional[datetime.datetime]=None) -> None:
        """Scale out or in based on time.

        Arguments:
            id: -
            action: -
            schedule: When to perform this action. Support formats: - at(yyyy-mm-ddThh:mm:ss) - rate(value unit) - cron(fields) "At" expressions are useful for one-time schedules. Specify the time in UTC. For "rate" expressions, value is a positive integer, and unit is minute, minutes, hour, hours, day, or days. For more information about cron expressions, see https://en.wikipedia.org/wiki/Cron.
            endTime: When this scheduled action expires. Default: The rule never expires.
            maxCapacity: The new maximum capacity. During the scheduled time, the current capacity is above the maximum capacity, Application Auto Scaling scales in to the maximum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new maximum capacity
            minCapacity: The new minimum capacity. During the scheduled time, if the current capacity is below the minimum capacity, Application Auto Scaling scales out to the minimum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new minimum capacity
            startTime: When this scheduled action becomes active. Default: The rule is activate immediately

        Stability:
            experimental
        """
        action: ScalingSchedule = {"schedule": schedule}

        if end_time is not None:
            action["endTime"] = end_time

        if max_capacity is not None:
            action["maxCapacity"] = max_capacity

        if min_capacity is not None:
            action["minCapacity"] = min_capacity

        if start_time is not None:
            action["startTime"] = start_time

        return jsii.invoke(self, "scaleOnSchedule", [id, action])

    @jsii.member(jsii_name="scaleToTrackMetric")
    def scale_to_track_metric(self, id: str, *, target_value: jsii.Number, custom_metric: typing.Optional[aws_cdk.aws_cloudwatch.Metric]=None, predefined_metric: typing.Optional["PredefinedMetric"]=None, resource_label: typing.Optional[str]=None, disable_scale_in: typing.Optional[bool]=None, policy_name: typing.Optional[str]=None, scale_in_cooldown_sec: typing.Optional[jsii.Number]=None, scale_out_cooldown_sec: typing.Optional[jsii.Number]=None) -> "TargetTrackingScalingPolicy":
        """Scale out or in in order to keep a metric around a target value.

        Arguments:
            id: -
            props: -
            targetValue: The target value for the metric.
            customMetric: A custom metric for application autoscaling. The metric must track utilization. Scaling out will happen if the metric is higher than the target value, scaling in will happen in the metric is lower than the target value. Exactly one of customMetric or predefinedMetric must be specified. Default: - No custom metric.
            predefinedMetric: A predefined metric for application autoscaling. The metric must track utilization. Scaling out will happen if the metric is higher than the target value, scaling in will happen in the metric is lower than the target value. Exactly one of customMetric or predefinedMetric must be specified. Default: - No predefined metrics.
            resourceLabel: Identify the resource associated with the metric type. Only used for predefined metric ALBRequestCountPerTarget. Default: - No resource label.
            disableScaleIn: Indicates whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. Default: false
            policyName: A name for the scaling policy. Default: - Automatically generated name.
            scaleInCooldownSec: Period after a scale in activity completes before another scale in activity can start. Default: - No scale in cooldown.
            scaleOutCooldownSec: Period after a scale out activity completes before another scale out activity can start. Default: - No scale out cooldown.

        Stability:
            experimental
        """
        props: BasicTargetTrackingScalingPolicyProps = {"targetValue": target_value}

        if custom_metric is not None:
            props["customMetric"] = custom_metric

        if predefined_metric is not None:
            props["predefinedMetric"] = predefined_metric

        if resource_label is not None:
            props["resourceLabel"] = resource_label

        if disable_scale_in is not None:
            props["disableScaleIn"] = disable_scale_in

        if policy_name is not None:
            props["policyName"] = policy_name

        if scale_in_cooldown_sec is not None:
            props["scaleInCooldownSec"] = scale_in_cooldown_sec

        if scale_out_cooldown_sec is not None:
            props["scaleOutCooldownSec"] = scale_out_cooldown_sec

        return jsii.invoke(self, "scaleToTrackMetric", [id, props])

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        """The role used to give AutoScaling permissions to your resource.

        Stability:
            experimental
        """
        return jsii.get(self, "role")

    @property
    @jsii.member(jsii_name="scalableTargetId")
    def scalable_target_id(self) -> str:
        """ID of the Scalable Target.

        Stability:
            experimental
        attribute:
            true

        Example::
            service/ecsStack-MyECSCluster-AB12CDE3F4GH/ecsStack-MyECSService-AB12CDE3F4GH|ecs:service:DesiredCount|ecs
        """
        return jsii.get(self, "scalableTargetId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ScalableTargetProps(jsii.compat.TypedDict, total=False):
    role: aws_cdk.aws_iam.IRole
    """Role that allows Application Auto Scaling to modify your scalable target.

    Default:
        A role is automatically created

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.ScalableTargetProps", jsii_struct_bases=[_ScalableTargetProps])
class ScalableTargetProps(_ScalableTargetProps):
    """Properties for a scalable target.

    Stability:
        experimental
    """
    maxCapacity: jsii.Number
    """The maximum value that Application Auto Scaling can use to scale a target during a scaling activity.

    Stability:
        experimental
    """

    minCapacity: jsii.Number
    """The minimum value that Application Auto Scaling can use to scale a target during a scaling activity.

    Stability:
        experimental
    """

    resourceId: str
    """The resource identifier to associate with this scalable target.

    This string consists of the resource type and unique identifier.

    See:
        https://docs.aws.amazon.com/autoscaling/application/APIReference/API_RegisterScalableTarget.html
    Stability:
        experimental

    Example::
        service/ecsStack-MyECSCluster-AB12CDE3F4GH/ecsStack-MyECSService-AB12CDE3F4GH
    """

    scalableDimension: str
    """The scalable dimension that's associated with the scalable target.

    Specify the service namespace, resource type, and scaling property.

    See:
        https://docs.aws.amazon.com/autoscaling/application/APIReference/API_ScalingPolicy.html
    Stability:
        experimental

    Example::
        ecs:service:DesiredCount
    """

    serviceNamespace: "ServiceNamespace"
    """The namespace of the AWS service that provides the resource or custom-resource for a resource provided by your own application or service.

    For valid AWS service namespace values, see the RegisterScalableTarget
    action in the Application Auto Scaling API Reference.

    See:
        https://docs.aws.amazon.com/autoscaling/application/APIReference/API_RegisterScalableTarget.html
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _ScalingInterval(jsii.compat.TypedDict, total=False):
    lower: jsii.Number
    """The lower bound of the interval.

    The scaling adjustment will be applied if the metric is higher than this value.

    Default:
        Threshold automatically derived from neighbouring intervals

    Stability:
        experimental
    """
    upper: jsii.Number
    """The upper bound of the interval.

    The scaling adjustment will be applied if the metric is lower than this value.

    Default:
        Threshold automatically derived from neighbouring intervals

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.ScalingInterval", jsii_struct_bases=[_ScalingInterval])
class ScalingInterval(_ScalingInterval):
    """A range of metric values in which to apply a certain scaling operation.

    Stability:
        experimental
    """
    change: jsii.Number
    """The capacity adjustment to apply in this interval.

    The number is interpreted differently based on AdjustmentType:

    - ChangeInCapacity: add the adjustment to the current capacity.
      The number can be positive or negative.
    - PercentChangeInCapacity: add or remove the given percentage of the current
      capacity to itself. The number can be in the range [-100..100].
    - ExactCapacity: set the capacity to this number. The number must
      be positive.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _ScalingSchedule(jsii.compat.TypedDict, total=False):
    endTime: datetime.datetime
    """When this scheduled action expires.

    Default:
        The rule never expires.

    Stability:
        experimental
    """
    maxCapacity: jsii.Number
    """The new maximum capacity.

    During the scheduled time, the current capacity is above the maximum
    capacity, Application Auto Scaling scales in to the maximum capacity.

    At least one of maxCapacity and minCapacity must be supplied.

    Default:
        No new maximum capacity

    Stability:
        experimental
    """
    minCapacity: jsii.Number
    """The new minimum capacity.

    During the scheduled time, if the current capacity is below the minimum
    capacity, Application Auto Scaling scales out to the minimum capacity.

    At least one of maxCapacity and minCapacity must be supplied.

    Default:
        No new minimum capacity

    Stability:
        experimental
    """
    startTime: datetime.datetime
    """When this scheduled action becomes active.

    Default:
        The rule is activate immediately

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.ScalingSchedule", jsii_struct_bases=[_ScalingSchedule])
class ScalingSchedule(_ScalingSchedule):
    """A scheduled scaling action.

    Stability:
        experimental
    """
    schedule: str
    """When to perform this action.

    Support formats:

    - at(yyyy-mm-ddThh:mm:ss)
    - rate(value unit)
    - cron(fields)

    "At" expressions are useful for one-time schedules. Specify the time in
    UTC.

    For "rate" expressions, value is a positive integer, and unit is minute,
    minutes, hour, hours, day, or days.

    For more information about cron expressions, see https://en.wikipedia.org/wiki/Cron.

    Stability:
        experimental

    Example::
        rate(12 hours)
    """

@jsii.enum(jsii_type="@aws-cdk/aws-applicationautoscaling.ServiceNamespace")
class ServiceNamespace(enum.Enum):
    """The service that supports Application AutoScaling.

    Stability:
        experimental
    """
    Ecs = "Ecs"
    """Elastic Container Service.

    Stability:
        experimental
    """
    ElasticMapReduce = "ElasticMapReduce"
    """Elastic Map Reduce.

    Stability:
        experimental
    """
    Ec2 = "Ec2"
    """Elastic Compute Cloud.

    Stability:
        experimental
    """
    AppStream = "AppStream"
    """App Stream.

    Stability:
        experimental
    """
    DynamoDb = "DynamoDb"
    """Dynamo DB.

    Stability:
        experimental
    """
    Rds = "Rds"
    """Relational Database Service.

    Stability:
        experimental
    """
    SageMaker = "SageMaker"
    """SageMaker.

    Stability:
        experimental
    """
    CustomResource = "CustomResource"
    """Custom Resource.

    Stability:
        experimental
    """

class StepScalingAction(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.StepScalingAction"):
    """Define a step scaling action.

    This kind of scaling policy adjusts the target capacity in configurable
    steps. The size of the step is configurable based on the metric's distance
    to its alarm threshold.

    This Action must be used as the target of a CloudWatch alarm to take effect.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, scaling_target: "IScalableTarget", adjustment_type: typing.Optional["AdjustmentType"]=None, cooldown_sec: typing.Optional[jsii.Number]=None, metric_aggregation_type: typing.Optional["MetricAggregationType"]=None, min_adjustment_magnitude: typing.Optional[jsii.Number]=None, policy_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            scalingTarget: The scalable target.
            adjustmentType: How the adjustment numbers are interpreted. Default: ChangeInCapacity
            cooldownSec: Grace period after scaling activity. For scale out policies, multiple scale outs during the cooldown period are squashed so that only the biggest scale out happens. For scale in policies, subsequent scale ins during the cooldown period are ignored. Default: No cooldown period
            metricAggregationType: The aggregation type for the CloudWatch metrics. Default: Average
            minAdjustmentMagnitude: Minimum absolute number to adjust capacity with as result of percentage scaling. Only when using AdjustmentType = PercentChangeInCapacity, this number controls the minimum absolute effect size. Default: No minimum scaling effect
            policyName: A name for the scaling policy. Default: Automatically generated name

        Stability:
            experimental
        """
        props: StepScalingActionProps = {"scalingTarget": scaling_target}

        if adjustment_type is not None:
            props["adjustmentType"] = adjustment_type

        if cooldown_sec is not None:
            props["cooldownSec"] = cooldown_sec

        if metric_aggregation_type is not None:
            props["metricAggregationType"] = metric_aggregation_type

        if min_adjustment_magnitude is not None:
            props["minAdjustmentMagnitude"] = min_adjustment_magnitude

        if policy_name is not None:
            props["policyName"] = policy_name

        jsii.create(StepScalingAction, self, [scope, id, props])

    @jsii.member(jsii_name="addAdjustment")
    def add_adjustment(self, *, adjustment: jsii.Number, lower_bound: typing.Optional[jsii.Number]=None, upper_bound: typing.Optional[jsii.Number]=None) -> None:
        """Add an adjusment interval to the ScalingAction.

        Arguments:
            adjustment: -
            adjustment: What number to adjust the capacity with. The number is interpeted as an added capacity, a new fixed capacity or an added percentage depending on the AdjustmentType value of the StepScalingPolicy. Can be positive or negative.
            lowerBound: Lower bound where this scaling tier applies. The scaling tier applies if the difference between the metric value and its alarm threshold is higher than this value. Default: -Infinity if this is the first tier, otherwise the upperBound of the previous tier
            upperBound: Upper bound where this scaling tier applies. The scaling tier applies if the difference between the metric value and its alarm threshold is lower than this value. Default: +Infinity

        Stability:
            experimental
        """
        adjustment: AdjustmentTier = {"adjustment": adjustment}

        if lower_bound is not None:
            adjustment["lowerBound"] = lower_bound

        if upper_bound is not None:
            adjustment["upperBound"] = upper_bound

        return jsii.invoke(self, "addAdjustment", [adjustment])

    @property
    @jsii.member(jsii_name="scalingPolicyArn")
    def scaling_policy_arn(self) -> str:
        """ARN of the scaling policy.

        Stability:
            experimental
        """
        return jsii.get(self, "scalingPolicyArn")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _StepScalingActionProps(jsii.compat.TypedDict, total=False):
    adjustmentType: "AdjustmentType"
    """How the adjustment numbers are interpreted.

    Default:
        ChangeInCapacity

    Stability:
        experimental
    """
    cooldownSec: jsii.Number
    """Grace period after scaling activity.

    For scale out policies, multiple scale outs during the cooldown period are
    squashed so that only the biggest scale out happens.

    For scale in policies, subsequent scale ins during the cooldown period are
    ignored.

    Default:
        No cooldown period

    See:
        https://docs.aws.amazon.com/autoscaling/application/APIReference/API_StepScalingPolicyConfiguration.html
    Stability:
        experimental
    """
    metricAggregationType: "MetricAggregationType"
    """The aggregation type for the CloudWatch metrics.

    Default:
        Average

    Stability:
        experimental
    """
    minAdjustmentMagnitude: jsii.Number
    """Minimum absolute number to adjust capacity with as result of percentage scaling.

    Only when using AdjustmentType = PercentChangeInCapacity, this number controls
    the minimum absolute effect size.

    Default:
        No minimum scaling effect

    Stability:
        experimental
    """
    policyName: str
    """A name for the scaling policy.

    Default:
        Automatically generated name

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.StepScalingActionProps", jsii_struct_bases=[_StepScalingActionProps])
class StepScalingActionProps(_StepScalingActionProps):
    """Properties for a scaling policy.

    Stability:
        experimental
    """
    scalingTarget: "IScalableTarget"
    """The scalable target.

    Stability:
        experimental
    """

class StepScalingPolicy(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.StepScalingPolicy"):
    """Define a acaling strategy which scales depending on absolute values of some metric.

    You can specify the scaling behavior for various values of the metric.

    Implemented using one or more CloudWatch alarms and Step Scaling Policies.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, scaling_target: "IScalableTarget", metric: aws_cdk.aws_cloudwatch.Metric, scaling_steps: typing.List["ScalingInterval"], adjustment_type: typing.Optional["AdjustmentType"]=None, cooldown_sec: typing.Optional[jsii.Number]=None, min_adjustment_magnitude: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            scalingTarget: The scaling target.
            metric: Metric to scale on.
            scalingSteps: The intervals for scaling. Maps a range of metric values to a particular scaling behavior.
            adjustmentType: How the adjustment numbers inside 'intervals' are interpreted. Default: ChangeInCapacity
            cooldownSec: Grace period after scaling activity. Subsequent scale outs during the cooldown period are squashed so that only the biggest scale out happens. Subsequent scale ins during the cooldown period are ignored. Default: No cooldown period
            minAdjustmentMagnitude: Minimum absolute number to adjust capacity with as result of percentage scaling. Only when using AdjustmentType = PercentChangeInCapacity, this number controls the minimum absolute effect size. Default: No minimum scaling effect

        Stability:
            experimental
        """
        props: StepScalingPolicyProps = {"scalingTarget": scaling_target, "metric": metric, "scalingSteps": scaling_steps}

        if adjustment_type is not None:
            props["adjustmentType"] = adjustment_type

        if cooldown_sec is not None:
            props["cooldownSec"] = cooldown_sec

        if min_adjustment_magnitude is not None:
            props["minAdjustmentMagnitude"] = min_adjustment_magnitude

        jsii.create(StepScalingPolicy, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="lowerAction")
    def lower_action(self) -> typing.Optional["StepScalingAction"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "lowerAction")

    @property
    @jsii.member(jsii_name="lowerAlarm")
    def lower_alarm(self) -> typing.Optional[aws_cdk.aws_cloudwatch.Alarm]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "lowerAlarm")

    @property
    @jsii.member(jsii_name="upperAction")
    def upper_action(self) -> typing.Optional["StepScalingAction"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "upperAction")

    @property
    @jsii.member(jsii_name="upperAlarm")
    def upper_alarm(self) -> typing.Optional[aws_cdk.aws_cloudwatch.Alarm]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "upperAlarm")


@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.StepScalingPolicyProps", jsii_struct_bases=[BasicStepScalingPolicyProps])
class StepScalingPolicyProps(BasicStepScalingPolicyProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    scalingTarget: "IScalableTarget"
    """The scaling target.

    Stability:
        experimental
    """

class TargetTrackingScalingPolicy(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.TargetTrackingScalingPolicy"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, scaling_target: "IScalableTarget", target_value: jsii.Number, custom_metric: typing.Optional[aws_cdk.aws_cloudwatch.Metric]=None, predefined_metric: typing.Optional["PredefinedMetric"]=None, resource_label: typing.Optional[str]=None, disable_scale_in: typing.Optional[bool]=None, policy_name: typing.Optional[str]=None, scale_in_cooldown_sec: typing.Optional[jsii.Number]=None, scale_out_cooldown_sec: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            scalingTarget: 
            targetValue: The target value for the metric.
            customMetric: A custom metric for application autoscaling. The metric must track utilization. Scaling out will happen if the metric is higher than the target value, scaling in will happen in the metric is lower than the target value. Exactly one of customMetric or predefinedMetric must be specified. Default: - No custom metric.
            predefinedMetric: A predefined metric for application autoscaling. The metric must track utilization. Scaling out will happen if the metric is higher than the target value, scaling in will happen in the metric is lower than the target value. Exactly one of customMetric or predefinedMetric must be specified. Default: - No predefined metrics.
            resourceLabel: Identify the resource associated with the metric type. Only used for predefined metric ALBRequestCountPerTarget. Default: - No resource label.
            disableScaleIn: Indicates whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. Default: false
            policyName: A name for the scaling policy. Default: - Automatically generated name.
            scaleInCooldownSec: Period after a scale in activity completes before another scale in activity can start. Default: - No scale in cooldown.
            scaleOutCooldownSec: Period after a scale out activity completes before another scale out activity can start. Default: - No scale out cooldown.

        Stability:
            experimental
        """
        props: TargetTrackingScalingPolicyProps = {"scalingTarget": scaling_target, "targetValue": target_value}

        if custom_metric is not None:
            props["customMetric"] = custom_metric

        if predefined_metric is not None:
            props["predefinedMetric"] = predefined_metric

        if resource_label is not None:
            props["resourceLabel"] = resource_label

        if disable_scale_in is not None:
            props["disableScaleIn"] = disable_scale_in

        if policy_name is not None:
            props["policyName"] = policy_name

        if scale_in_cooldown_sec is not None:
            props["scaleInCooldownSec"] = scale_in_cooldown_sec

        if scale_out_cooldown_sec is not None:
            props["scaleOutCooldownSec"] = scale_out_cooldown_sec

        jsii.create(TargetTrackingScalingPolicy, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="scalingPolicyArn")
    def scaling_policy_arn(self) -> str:
        """ARN of the scaling policy.

        Stability:
            experimental
        """
        return jsii.get(self, "scalingPolicyArn")


@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.TargetTrackingScalingPolicyProps", jsii_struct_bases=[BasicTargetTrackingScalingPolicyProps])
class TargetTrackingScalingPolicyProps(BasicTargetTrackingScalingPolicyProps, jsii.compat.TypedDict):
    """Properties for a concrete TargetTrackingPolicy.

    Adds the scalingTarget.

    Stability:
        experimental
    """
    scalingTarget: "IScalableTarget"
    """
    Stability:
        experimental
    """

__all__ = ["AdjustmentTier", "AdjustmentType", "BaseScalableAttribute", "BaseScalableAttributeProps", "BaseTargetTrackingProps", "BasicStepScalingPolicyProps", "BasicTargetTrackingScalingPolicyProps", "CfnScalableTarget", "CfnScalableTargetProps", "CfnScalingPolicy", "CfnScalingPolicyProps", "Cron", "EnableScalingProps", "IScalableTarget", "MetricAggregationType", "PredefinedMetric", "ScalableTarget", "ScalableTargetProps", "ScalingInterval", "ScalingSchedule", "ServiceNamespace", "StepScalingAction", "StepScalingActionProps", "StepScalingPolicy", "StepScalingPolicyProps", "TargetTrackingScalingPolicy", "TargetTrackingScalingPolicyProps", "__jsii_assembly__"]

publication.publish()
