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
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-applicationautoscaling", "0.36.0", __name__, "aws-applicationautoscaling@0.36.0.jsii.tgz")
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
    CHANGE_IN_CAPACITY = "CHANGE_IN_CAPACITY"
    """Add the adjustment number to the current capacity.

    A positive number increases capacity, a negative number decreases capacity.

    Stability:
        experimental
    """
    PERCENT_CHANGE_IN_CAPACITY = "PERCENT_CHANGE_IN_CAPACITY"
    """Add this percentage of the current capacity to itself.

    The number must be between -100 and 100; a positive number increases
    capacity and a negative number decreases it.

    Stability:
        experimental
    """
    EXACT_CAPACITY = "EXACT_CAPACITY"
    """Make the capacity equal to the exact number given.

    Stability:
        experimental
    """

class BaseScalableAttribute(aws_cdk.core.Construct, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-applicationautoscaling.BaseScalableAttribute"):
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

    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, dimension: str, resource_id: str, role: aws_cdk.aws_iam.IRole, service_namespace: "ServiceNamespace", max_capacity: jsii.Number, min_capacity: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            dimension: Scalable dimension of the attribute.
            resource_id: Resource ID of the attribute.
            role: Role to use for scaling.
            service_namespace: Service namespace of the scalable attribute.
            max_capacity: Maximum capacity to scale to.
            min_capacity: Minimum capacity to scale to. Default: 1

        Stability:
            experimental
        """
        props: BaseScalableAttributeProps = {"dimension": dimension, "resourceId": resource_id, "role": role, "serviceNamespace": service_namespace, "maxCapacity": max_capacity}

        if min_capacity is not None:
            props["minCapacity"] = min_capacity

        jsii.create(BaseScalableAttribute, self, [scope, id, props])

    @jsii.member(jsii_name="doScaleOnMetric")
    def _do_scale_on_metric(self, id: str, *, metric: aws_cdk.aws_cloudwatch.IMetric, scaling_steps: typing.List["ScalingInterval"], adjustment_type: typing.Optional["AdjustmentType"]=None, cooldown: typing.Optional[aws_cdk.core.Duration]=None, min_adjustment_magnitude: typing.Optional[jsii.Number]=None) -> None:
        """Scale out or in based on a metric value.

        Arguments:
            id: -
            props: -
            metric: Metric to scale on.
            scaling_steps: The intervals for scaling. Maps a range of metric values to a particular scaling behavior.
            adjustment_type: How the adjustment numbers inside 'intervals' are interpreted. Default: ChangeInCapacity
            cooldown: Grace period after scaling activity. Subsequent scale outs during the cooldown period are squashed so that only the biggest scale out happens. Subsequent scale ins during the cooldown period are ignored. Default: No cooldown period
            min_adjustment_magnitude: Minimum absolute number to adjust capacity with as result of percentage scaling. Only when using AdjustmentType = PercentChangeInCapacity, this number controls the minimum absolute effect size. Default: No minimum scaling effect

        Stability:
            experimental
        """
        props: BasicStepScalingPolicyProps = {"metric": metric, "scalingSteps": scaling_steps}

        if adjustment_type is not None:
            props["adjustmentType"] = adjustment_type

        if cooldown is not None:
            props["cooldown"] = cooldown

        if min_adjustment_magnitude is not None:
            props["minAdjustmentMagnitude"] = min_adjustment_magnitude

        return jsii.invoke(self, "doScaleOnMetric", [id, props])

    @jsii.member(jsii_name="doScaleOnSchedule")
    def _do_scale_on_schedule(self, id: str, *, schedule: "Schedule", end_time: typing.Optional[datetime.datetime]=None, max_capacity: typing.Optional[jsii.Number]=None, min_capacity: typing.Optional[jsii.Number]=None, start_time: typing.Optional[datetime.datetime]=None) -> None:
        """Scale out or in based on time.

        Arguments:
            id: -
            props: -
            schedule: When to perform this action.
            end_time: When this scheduled action expires. Default: The rule never expires.
            max_capacity: The new maximum capacity. During the scheduled time, the current capacity is above the maximum capacity, Application Auto Scaling scales in to the maximum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new maximum capacity
            min_capacity: The new minimum capacity. During the scheduled time, if the current capacity is below the minimum capacity, Application Auto Scaling scales out to the minimum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new minimum capacity
            start_time: When this scheduled action becomes active. Default: The rule is activate immediately

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
    def _do_scale_to_track_metric(self, id: str, *, target_value: jsii.Number, custom_metric: typing.Optional[aws_cdk.aws_cloudwatch.IMetric]=None, predefined_metric: typing.Optional["PredefinedMetric"]=None, resource_label: typing.Optional[str]=None, disable_scale_in: typing.Optional[bool]=None, policy_name: typing.Optional[str]=None, scale_in_cooldown: typing.Optional[aws_cdk.core.Duration]=None, scale_out_cooldown: typing.Optional[aws_cdk.core.Duration]=None) -> None:
        """Scale out or in in order to keep a metric around a target value.

        Arguments:
            id: -
            props: -
            target_value: The target value for the metric.
            custom_metric: A custom metric for application autoscaling. The metric must track utilization. Scaling out will happen if the metric is higher than the target value, scaling in will happen in the metric is lower than the target value. Exactly one of customMetric or predefinedMetric must be specified. Default: - No custom metric.
            predefined_metric: A predefined metric for application autoscaling. The metric must track utilization. Scaling out will happen if the metric is higher than the target value, scaling in will happen in the metric is lower than the target value. Exactly one of customMetric or predefinedMetric must be specified. Default: - No predefined metrics.
            resource_label: Identify the resource associated with the metric type. Only used for predefined metric ALBRequestCountPerTarget. Default: - No resource label.
            disable_scale_in: Indicates whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. Default: false
            policy_name: A name for the scaling policy. Default: - Automatically generated name.
            scale_in_cooldown: Period after a scale in activity completes before another scale in activity can start. Default: - No scale in cooldown.
            scale_out_cooldown: Period after a scale out activity completes before another scale out activity can start. Default: - No scale out cooldown.

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

        if scale_in_cooldown is not None:
            props["scaleInCooldown"] = scale_in_cooldown

        if scale_out_cooldown is not None:
            props["scaleOutCooldown"] = scale_out_cooldown

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

    scaleInCooldown: aws_cdk.core.Duration
    """Period after a scale in activity completes before another scale in activity can start.

    Default:
        - No scale in cooldown.

    Stability:
        experimental
    """

    scaleOutCooldown: aws_cdk.core.Duration
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
    cooldown: aws_cdk.core.Duration
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
    metric: aws_cdk.aws_cloudwatch.IMetric
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
    customMetric: aws_cdk.aws_cloudwatch.IMetric
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

class CfnScalableTarget(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalableTarget"):
    """A CloudFormation ``AWS::ApplicationAutoScaling::ScalableTarget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html
    Stability:
        stable
    cloudformationResource:
        AWS::ApplicationAutoScaling::ScalableTarget
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, max_capacity: jsii.Number, min_capacity: jsii.Number, resource_id: str, role_arn: str, scalable_dimension: str, service_namespace: str, scheduled_actions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["ScheduledActionProperty", aws_cdk.core.IResolvable]]]]]=None) -> None:
        """Create a new ``AWS::ApplicationAutoScaling::ScalableTarget``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            max_capacity: ``AWS::ApplicationAutoScaling::ScalableTarget.MaxCapacity``.
            min_capacity: ``AWS::ApplicationAutoScaling::ScalableTarget.MinCapacity``.
            resource_id: ``AWS::ApplicationAutoScaling::ScalableTarget.ResourceId``.
            role_arn: ``AWS::ApplicationAutoScaling::ScalableTarget.RoleARN``.
            scalable_dimension: ``AWS::ApplicationAutoScaling::ScalableTarget.ScalableDimension``.
            service_namespace: ``AWS::ApplicationAutoScaling::ScalableTarget.ServiceNamespace``.
            scheduled_actions: ``AWS::ApplicationAutoScaling::ScalableTarget.ScheduledActions``.

        Stability:
            experimental
        """
        props: CfnScalableTargetProps = {"maxCapacity": max_capacity, "minCapacity": min_capacity, "resourceId": resource_id, "roleArn": role_arn, "scalableDimension": scalable_dimension, "serviceNamespace": service_namespace}

        if scheduled_actions is not None:
            props["scheduledActions"] = scheduled_actions

        jsii.create(CfnScalableTarget, self, [scope, id, props])

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
    @jsii.member(jsii_name="maxCapacity")
    def max_capacity(self) -> jsii.Number:
        """``AWS::ApplicationAutoScaling::ScalableTarget.MaxCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-maxcapacity
        Stability:
            stable
        """
        return jsii.get(self, "maxCapacity")

    @max_capacity.setter
    def max_capacity(self, value: jsii.Number):
        return jsii.set(self, "maxCapacity", value)

    @property
    @jsii.member(jsii_name="minCapacity")
    def min_capacity(self) -> jsii.Number:
        """``AWS::ApplicationAutoScaling::ScalableTarget.MinCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-mincapacity
        Stability:
            stable
        """
        return jsii.get(self, "minCapacity")

    @min_capacity.setter
    def min_capacity(self, value: jsii.Number):
        return jsii.set(self, "minCapacity", value)

    @property
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> str:
        """``AWS::ApplicationAutoScaling::ScalableTarget.ResourceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-resourceid
        Stability:
            stable
        """
        return jsii.get(self, "resourceId")

    @resource_id.setter
    def resource_id(self, value: str):
        return jsii.set(self, "resourceId", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """``AWS::ApplicationAutoScaling::ScalableTarget.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-rolearn
        Stability:
            stable
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: str):
        return jsii.set(self, "roleArn", value)

    @property
    @jsii.member(jsii_name="scalableDimension")
    def scalable_dimension(self) -> str:
        """``AWS::ApplicationAutoScaling::ScalableTarget.ScalableDimension``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-scalabledimension
        Stability:
            stable
        """
        return jsii.get(self, "scalableDimension")

    @scalable_dimension.setter
    def scalable_dimension(self, value: str):
        return jsii.set(self, "scalableDimension", value)

    @property
    @jsii.member(jsii_name="serviceNamespace")
    def service_namespace(self) -> str:
        """``AWS::ApplicationAutoScaling::ScalableTarget.ServiceNamespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-servicenamespace
        Stability:
            stable
        """
        return jsii.get(self, "serviceNamespace")

    @service_namespace.setter
    def service_namespace(self, value: str):
        return jsii.set(self, "serviceNamespace", value)

    @property
    @jsii.member(jsii_name="scheduledActions")
    def scheduled_actions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["ScheduledActionProperty", aws_cdk.core.IResolvable]]]]]:
        """``AWS::ApplicationAutoScaling::ScalableTarget.ScheduledActions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-scheduledactions
        Stability:
            stable
        """
        return jsii.get(self, "scheduledActions")

    @scheduled_actions.setter
    def scheduled_actions(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["ScheduledActionProperty", aws_cdk.core.IResolvable]]]]]):
        return jsii.set(self, "scheduledActions", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalableTarget.ScalableTargetActionProperty", jsii_struct_bases=[])
    class ScalableTargetActionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scalabletargetaction.html
        Stability:
            stable
        """
        maxCapacity: jsii.Number
        """``CfnScalableTarget.ScalableTargetActionProperty.MaxCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scalabletargetaction.html#cfn-applicationautoscaling-scalabletarget-scalabletargetaction-maxcapacity
        Stability:
            stable
        """

        minCapacity: jsii.Number
        """``CfnScalableTarget.ScalableTargetActionProperty.MinCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scalabletargetaction.html#cfn-applicationautoscaling-scalabletarget-scalabletargetaction-mincapacity
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ScheduledActionProperty(jsii.compat.TypedDict, total=False):
        endTime: typing.Union[aws_cdk.core.IResolvable, datetime.datetime]
        """``CfnScalableTarget.ScheduledActionProperty.EndTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scheduledaction.html#cfn-applicationautoscaling-scalabletarget-scheduledaction-endtime
        Stability:
            stable
        """
        scalableTargetAction: typing.Union[aws_cdk.core.IResolvable, "CfnScalableTarget.ScalableTargetActionProperty"]
        """``CfnScalableTarget.ScheduledActionProperty.ScalableTargetAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scheduledaction.html#cfn-applicationautoscaling-scalabletarget-scheduledaction-scalabletargetaction
        Stability:
            stable
        """
        startTime: typing.Union[aws_cdk.core.IResolvable, datetime.datetime]
        """``CfnScalableTarget.ScheduledActionProperty.StartTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scheduledaction.html#cfn-applicationautoscaling-scalabletarget-scheduledaction-starttime
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalableTarget.ScheduledActionProperty", jsii_struct_bases=[_ScheduledActionProperty])
    class ScheduledActionProperty(_ScheduledActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scheduledaction.html
        Stability:
            stable
        """
        schedule: str
        """``CfnScalableTarget.ScheduledActionProperty.Schedule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scheduledaction.html#cfn-applicationautoscaling-scalabletarget-scheduledaction-schedule
        Stability:
            stable
        """

        scheduledActionName: str
        """``CfnScalableTarget.ScheduledActionProperty.ScheduledActionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalabletarget-scheduledaction.html#cfn-applicationautoscaling-scalabletarget-scheduledaction-scheduledactionname
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnScalableTargetProps(jsii.compat.TypedDict, total=False):
    scheduledActions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnScalableTarget.ScheduledActionProperty", aws_cdk.core.IResolvable]]]
    """``AWS::ApplicationAutoScaling::ScalableTarget.ScheduledActions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-scheduledactions
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalableTargetProps", jsii_struct_bases=[_CfnScalableTargetProps])
class CfnScalableTargetProps(_CfnScalableTargetProps):
    """Properties for defining a ``AWS::ApplicationAutoScaling::ScalableTarget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html
    Stability:
        stable
    """
    maxCapacity: jsii.Number
    """``AWS::ApplicationAutoScaling::ScalableTarget.MaxCapacity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-maxcapacity
    Stability:
        stable
    """

    minCapacity: jsii.Number
    """``AWS::ApplicationAutoScaling::ScalableTarget.MinCapacity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-mincapacity
    Stability:
        stable
    """

    resourceId: str
    """``AWS::ApplicationAutoScaling::ScalableTarget.ResourceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-resourceid
    Stability:
        stable
    """

    roleArn: str
    """``AWS::ApplicationAutoScaling::ScalableTarget.RoleARN``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-rolearn
    Stability:
        stable
    """

    scalableDimension: str
    """``AWS::ApplicationAutoScaling::ScalableTarget.ScalableDimension``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-scalabledimension
    Stability:
        stable
    """

    serviceNamespace: str
    """``AWS::ApplicationAutoScaling::ScalableTarget.ServiceNamespace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalabletarget.html#cfn-applicationautoscaling-scalabletarget-servicenamespace
    Stability:
        stable
    """

class CfnScalingPolicy(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy"):
    """A CloudFormation ``AWS::ApplicationAutoScaling::ScalingPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html
    Stability:
        stable
    cloudformationResource:
        AWS::ApplicationAutoScaling::ScalingPolicy
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, policy_name: str, policy_type: str, resource_id: typing.Optional[str]=None, scalable_dimension: typing.Optional[str]=None, scaling_target_id: typing.Optional[str]=None, service_namespace: typing.Optional[str]=None, step_scaling_policy_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["StepScalingPolicyConfigurationProperty"]]]=None, target_tracking_scaling_policy_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TargetTrackingScalingPolicyConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::ApplicationAutoScaling::ScalingPolicy``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            policy_name: ``AWS::ApplicationAutoScaling::ScalingPolicy.PolicyName``.
            policy_type: ``AWS::ApplicationAutoScaling::ScalingPolicy.PolicyType``.
            resource_id: ``AWS::ApplicationAutoScaling::ScalingPolicy.ResourceId``.
            scalable_dimension: ``AWS::ApplicationAutoScaling::ScalingPolicy.ScalableDimension``.
            scaling_target_id: ``AWS::ApplicationAutoScaling::ScalingPolicy.ScalingTargetId``.
            service_namespace: ``AWS::ApplicationAutoScaling::ScalingPolicy.ServiceNamespace``.
            step_scaling_policy_configuration: ``AWS::ApplicationAutoScaling::ScalingPolicy.StepScalingPolicyConfiguration``.
            target_tracking_scaling_policy_configuration: ``AWS::ApplicationAutoScaling::ScalingPolicy.TargetTrackingScalingPolicyConfiguration``.

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
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> str:
        """``AWS::ApplicationAutoScaling::ScalingPolicy.PolicyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-policyname
        Stability:
            stable
        """
        return jsii.get(self, "policyName")

    @policy_name.setter
    def policy_name(self, value: str):
        return jsii.set(self, "policyName", value)

    @property
    @jsii.member(jsii_name="policyType")
    def policy_type(self) -> str:
        """``AWS::ApplicationAutoScaling::ScalingPolicy.PolicyType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-policytype
        Stability:
            stable
        """
        return jsii.get(self, "policyType")

    @policy_type.setter
    def policy_type(self, value: str):
        return jsii.set(self, "policyType", value)

    @property
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> typing.Optional[str]:
        """``AWS::ApplicationAutoScaling::ScalingPolicy.ResourceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-resourceid
        Stability:
            stable
        """
        return jsii.get(self, "resourceId")

    @resource_id.setter
    def resource_id(self, value: typing.Optional[str]):
        return jsii.set(self, "resourceId", value)

    @property
    @jsii.member(jsii_name="scalableDimension")
    def scalable_dimension(self) -> typing.Optional[str]:
        """``AWS::ApplicationAutoScaling::ScalingPolicy.ScalableDimension``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-scalabledimension
        Stability:
            stable
        """
        return jsii.get(self, "scalableDimension")

    @scalable_dimension.setter
    def scalable_dimension(self, value: typing.Optional[str]):
        return jsii.set(self, "scalableDimension", value)

    @property
    @jsii.member(jsii_name="scalingTargetId")
    def scaling_target_id(self) -> typing.Optional[str]:
        """``AWS::ApplicationAutoScaling::ScalingPolicy.ScalingTargetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-scalingtargetid
        Stability:
            stable
        """
        return jsii.get(self, "scalingTargetId")

    @scaling_target_id.setter
    def scaling_target_id(self, value: typing.Optional[str]):
        return jsii.set(self, "scalingTargetId", value)

    @property
    @jsii.member(jsii_name="serviceNamespace")
    def service_namespace(self) -> typing.Optional[str]:
        """``AWS::ApplicationAutoScaling::ScalingPolicy.ServiceNamespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-servicenamespace
        Stability:
            stable
        """
        return jsii.get(self, "serviceNamespace")

    @service_namespace.setter
    def service_namespace(self, value: typing.Optional[str]):
        return jsii.set(self, "serviceNamespace", value)

    @property
    @jsii.member(jsii_name="stepScalingPolicyConfiguration")
    def step_scaling_policy_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["StepScalingPolicyConfigurationProperty"]]]:
        """``AWS::ApplicationAutoScaling::ScalingPolicy.StepScalingPolicyConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "stepScalingPolicyConfiguration")

    @step_scaling_policy_configuration.setter
    def step_scaling_policy_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["StepScalingPolicyConfigurationProperty"]]]):
        return jsii.set(self, "stepScalingPolicyConfiguration", value)

    @property
    @jsii.member(jsii_name="targetTrackingScalingPolicyConfiguration")
    def target_tracking_scaling_policy_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TargetTrackingScalingPolicyConfigurationProperty"]]]:
        """``AWS::ApplicationAutoScaling::ScalingPolicy.TargetTrackingScalingPolicyConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "targetTrackingScalingPolicyConfiguration")

    @target_tracking_scaling_policy_configuration.setter
    def target_tracking_scaling_policy_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TargetTrackingScalingPolicyConfigurationProperty"]]]):
        return jsii.set(self, "targetTrackingScalingPolicyConfiguration", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CustomizedMetricSpecificationProperty(jsii.compat.TypedDict, total=False):
        dimensions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnScalingPolicy.MetricDimensionProperty"]]]
        """``CfnScalingPolicy.CustomizedMetricSpecificationProperty.Dimensions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-customizedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-customizedmetricspecification-dimensions
        Stability:
            stable
        """
        unit: str
        """``CfnScalingPolicy.CustomizedMetricSpecificationProperty.Unit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-customizedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-customizedmetricspecification-unit
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy.CustomizedMetricSpecificationProperty", jsii_struct_bases=[_CustomizedMetricSpecificationProperty])
    class CustomizedMetricSpecificationProperty(_CustomizedMetricSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-customizedmetricspecification.html
        Stability:
            stable
        """
        metricName: str
        """``CfnScalingPolicy.CustomizedMetricSpecificationProperty.MetricName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-customizedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-customizedmetricspecification-metricname
        Stability:
            stable
        """

        namespace: str
        """``CfnScalingPolicy.CustomizedMetricSpecificationProperty.Namespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-customizedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-customizedmetricspecification-namespace
        Stability:
            stable
        """

        statistic: str
        """``CfnScalingPolicy.CustomizedMetricSpecificationProperty.Statistic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-customizedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-customizedmetricspecification-statistic
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy.MetricDimensionProperty", jsii_struct_bases=[])
    class MetricDimensionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-metricdimension.html
        Stability:
            stable
        """
        name: str
        """``CfnScalingPolicy.MetricDimensionProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-metricdimension.html#cfn-applicationautoscaling-scalingpolicy-metricdimension-name
        Stability:
            stable
        """

        value: str
        """``CfnScalingPolicy.MetricDimensionProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-metricdimension.html#cfn-applicationautoscaling-scalingpolicy-metricdimension-value
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _PredefinedMetricSpecificationProperty(jsii.compat.TypedDict, total=False):
        resourceLabel: str
        """``CfnScalingPolicy.PredefinedMetricSpecificationProperty.ResourceLabel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-predefinedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-predefinedmetricspecification-resourcelabel
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy.PredefinedMetricSpecificationProperty", jsii_struct_bases=[_PredefinedMetricSpecificationProperty])
    class PredefinedMetricSpecificationProperty(_PredefinedMetricSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-predefinedmetricspecification.html
        Stability:
            stable
        """
        predefinedMetricType: str
        """``CfnScalingPolicy.PredefinedMetricSpecificationProperty.PredefinedMetricType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-predefinedmetricspecification.html#cfn-applicationautoscaling-scalingpolicy-predefinedmetricspecification-predefinedmetrictype
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _StepAdjustmentProperty(jsii.compat.TypedDict, total=False):
        metricIntervalLowerBound: jsii.Number
        """``CfnScalingPolicy.StepAdjustmentProperty.MetricIntervalLowerBound``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment-metricintervallowerbound
        Stability:
            stable
        """
        metricIntervalUpperBound: jsii.Number
        """``CfnScalingPolicy.StepAdjustmentProperty.MetricIntervalUpperBound``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment-metricintervalupperbound
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy.StepAdjustmentProperty", jsii_struct_bases=[_StepAdjustmentProperty])
    class StepAdjustmentProperty(_StepAdjustmentProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment.html
        Stability:
            stable
        """
        scalingAdjustment: jsii.Number
        """``CfnScalingPolicy.StepAdjustmentProperty.ScalingAdjustment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustment-scalingadjustment
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy.StepScalingPolicyConfigurationProperty", jsii_struct_bases=[])
    class StepScalingPolicyConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration.html
        Stability:
            stable
        """
        adjustmentType: str
        """``CfnScalingPolicy.StepScalingPolicyConfigurationProperty.AdjustmentType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-adjustmenttype
        Stability:
            stable
        """

        cooldown: jsii.Number
        """``CfnScalingPolicy.StepScalingPolicyConfigurationProperty.Cooldown``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-cooldown
        Stability:
            stable
        """

        metricAggregationType: str
        """``CfnScalingPolicy.StepScalingPolicyConfigurationProperty.MetricAggregationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-metricaggregationtype
        Stability:
            stable
        """

        minAdjustmentMagnitude: jsii.Number
        """``CfnScalingPolicy.StepScalingPolicyConfigurationProperty.MinAdjustmentMagnitude``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-minadjustmentmagnitude
        Stability:
            stable
        """

        stepAdjustments: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnScalingPolicy.StepAdjustmentProperty"]]]
        """``CfnScalingPolicy.StepScalingPolicyConfigurationProperty.StepAdjustments``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration-stepadjustments
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _TargetTrackingScalingPolicyConfigurationProperty(jsii.compat.TypedDict, total=False):
        customizedMetricSpecification: typing.Union[aws_cdk.core.IResolvable, "CfnScalingPolicy.CustomizedMetricSpecificationProperty"]
        """``CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty.CustomizedMetricSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration-customizedmetricspecification
        Stability:
            stable
        """
        disableScaleIn: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty.DisableScaleIn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration-disablescalein
        Stability:
            stable
        """
        predefinedMetricSpecification: typing.Union[aws_cdk.core.IResolvable, "CfnScalingPolicy.PredefinedMetricSpecificationProperty"]
        """``CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty.PredefinedMetricSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration-predefinedmetricspecification
        Stability:
            stable
        """
        scaleInCooldown: jsii.Number
        """``CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty.ScaleInCooldown``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration-scaleincooldown
        Stability:
            stable
        """
        scaleOutCooldown: jsii.Number
        """``CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty.ScaleOutCooldown``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration-scaleoutcooldown
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty", jsii_struct_bases=[_TargetTrackingScalingPolicyConfigurationProperty])
    class TargetTrackingScalingPolicyConfigurationProperty(_TargetTrackingScalingPolicyConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html
        Stability:
            stable
        """
        targetValue: jsii.Number
        """``CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty.TargetValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration-targetvalue
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnScalingPolicyProps(jsii.compat.TypedDict, total=False):
    resourceId: str
    """``AWS::ApplicationAutoScaling::ScalingPolicy.ResourceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-resourceid
    Stability:
        stable
    """
    scalableDimension: str
    """``AWS::ApplicationAutoScaling::ScalingPolicy.ScalableDimension``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-scalabledimension
    Stability:
        stable
    """
    scalingTargetId: str
    """``AWS::ApplicationAutoScaling::ScalingPolicy.ScalingTargetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-scalingtargetid
    Stability:
        stable
    """
    serviceNamespace: str
    """``AWS::ApplicationAutoScaling::ScalingPolicy.ServiceNamespace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-servicenamespace
    Stability:
        stable
    """
    stepScalingPolicyConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnScalingPolicy.StepScalingPolicyConfigurationProperty"]
    """``AWS::ApplicationAutoScaling::ScalingPolicy.StepScalingPolicyConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-stepscalingpolicyconfiguration
    Stability:
        stable
    """
    targetTrackingScalingPolicyConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnScalingPolicy.TargetTrackingScalingPolicyConfigurationProperty"]
    """``AWS::ApplicationAutoScaling::ScalingPolicy.TargetTrackingScalingPolicyConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-targettrackingscalingpolicyconfiguration
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CfnScalingPolicyProps", jsii_struct_bases=[_CfnScalingPolicyProps])
class CfnScalingPolicyProps(_CfnScalingPolicyProps):
    """Properties for defining a ``AWS::ApplicationAutoScaling::ScalingPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html
    Stability:
        stable
    """
    policyName: str
    """``AWS::ApplicationAutoScaling::ScalingPolicy.PolicyName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-policyname
    Stability:
        stable
    """

    policyType: str
    """``AWS::ApplicationAutoScaling::ScalingPolicy.PolicyType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-applicationautoscaling-scalingpolicy.html#cfn-applicationautoscaling-scalingpolicy-policytype
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-applicationautoscaling.CronOptions", jsii_struct_bases=[])
class CronOptions(jsii.compat.TypedDict, total=False):
    """Options to configure a cron expression.

    All fields are strings so you can use complex expresions. Absence of
    a field implies '*' or '?', whichever one is appropriate.

    See:
        https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html#CronExpressions
    Stability:
        experimental
    """
    day: str
    """The day of the month to run this rule at.

    Default:
        - Every day of the month

    Stability:
        experimental
    """

    hour: str
    """The hour to run this rule at.

    Default:
        - Every hour

    Stability:
        experimental
    """

    minute: str
    """The minute to run this rule at.

    Default:
        - Every minute

    Stability:
        experimental
    """

    month: str
    """The month to run this rule at.

    Default:
        - Every month

    Stability:
        experimental
    """

    weekDay: str
    """The day of the week to run this rule at.

    Default:
        - Any day of the week

    Stability:
        experimental
    """

    year: str
    """The year to run this rule at.

    Default:
        - Every year

    Stability:
        experimental
    """

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
class IScalableTarget(aws_cdk.core.IResource, jsii.compat.Protocol):
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


class _IScalableTargetProxy(jsii.proxy_for(aws_cdk.core.IResource)):
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
    AVERAGE = "AVERAGE"
    """Average.

    Stability:
        experimental
    """
    MINIMUM = "MINIMUM"
    """Minimum.

    Stability:
        experimental
    """
    MAXIMUM = "MAXIMUM"
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
    DYNAMODB_READ_CAPACITY_UTILIZATION = "DYNAMODB_READ_CAPACITY_UTILIZATION"
    """
    Stability:
        experimental
    """
    DYANMODB_WRITE_CAPACITY_UTILIZATION = "DYANMODB_WRITE_CAPACITY_UTILIZATION"
    """
    Stability:
        experimental
    """
    ALB_REQUEST_COUNT_PER_TARGET = "ALB_REQUEST_COUNT_PER_TARGET"
    """
    Stability:
        experimental
    """
    RDS_READER_AVERAGE_CPU_UTILIZATION = "RDS_READER_AVERAGE_CPU_UTILIZATION"
    """
    Stability:
        experimental
    """
    RDS_READER_AVERAGE_DATABASE_CONNECTIONS = "RDS_READER_AVERAGE_DATABASE_CONNECTIONS"
    """
    Stability:
        experimental
    """
    EC2_SPOT_FLEET_REQUEST_AVERAGE_CPU_UTILIZATION = "EC2_SPOT_FLEET_REQUEST_AVERAGE_CPU_UTILIZATION"
    """
    Stability:
        experimental
    """
    EC2_SPOT_FLEET_REQUEST_AVERAGE_NETWORK_IN = "EC2_SPOT_FLEET_REQUEST_AVERAGE_NETWORK_IN"
    """
    Stability:
        experimental
    """
    EC2_SPOT_FLEET_REQUEST_AVERAGE_NETWORK_OUT = "EC2_SPOT_FLEET_REQUEST_AVERAGE_NETWORK_OUT"
    """
    Stability:
        experimental
    """
    SAGEMAKER_VARIANT_INVOCATIONS_PER_INSTANCE = "SAGEMAKER_VARIANT_INVOCATIONS_PER_INSTANCE"
    """
    Stability:
        experimental
    """
    ECS_SERVICE_AVERAGE_CPU_UTILIZATION = "ECS_SERVICE_AVERAGE_CPU_UTILIZATION"
    """
    Stability:
        experimental
    """
    ECS_SERVICE_AVERAGE_MEMORY_UTILIZATION = "ECS_SERVICE_AVERAGE_MEMORY_UTILIZATION"
    """
    Stability:
        experimental
    """

@jsii.implements(IScalableTarget)
class ScalableTarget(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.ScalableTarget"):
    """Define a scalable target.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, max_capacity: jsii.Number, min_capacity: jsii.Number, resource_id: str, scalable_dimension: str, service_namespace: "ServiceNamespace", role: typing.Optional[aws_cdk.aws_iam.IRole]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            max_capacity: The maximum value that Application Auto Scaling can use to scale a target during a scaling activity.
            min_capacity: The minimum value that Application Auto Scaling can use to scale a target during a scaling activity.
            resource_id: The resource identifier to associate with this scalable target. This string consists of the resource type and unique identifier.
            scalable_dimension: The scalable dimension that's associated with the scalable target. Specify the service namespace, resource type, and scaling property.
            service_namespace: The namespace of the AWS service that provides the resource or custom-resource for a resource provided by your own application or service. For valid AWS service namespace values, see the RegisterScalableTarget action in the Application Auto Scaling API Reference.
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
    def from_scalable_target_id(cls, scope: aws_cdk.core.Construct, id: str, scalable_target_id: str) -> "IScalableTarget":
        """
        Arguments:
            scope: -
            id: -
            scalable_target_id: -

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
    def scale_on_metric(self, id: str, *, metric: aws_cdk.aws_cloudwatch.IMetric, scaling_steps: typing.List["ScalingInterval"], adjustment_type: typing.Optional["AdjustmentType"]=None, cooldown: typing.Optional[aws_cdk.core.Duration]=None, min_adjustment_magnitude: typing.Optional[jsii.Number]=None) -> "StepScalingPolicy":
        """Scale out or in, in response to a metric.

        Arguments:
            id: -
            props: -
            metric: Metric to scale on.
            scaling_steps: The intervals for scaling. Maps a range of metric values to a particular scaling behavior.
            adjustment_type: How the adjustment numbers inside 'intervals' are interpreted. Default: ChangeInCapacity
            cooldown: Grace period after scaling activity. Subsequent scale outs during the cooldown period are squashed so that only the biggest scale out happens. Subsequent scale ins during the cooldown period are ignored. Default: No cooldown period
            min_adjustment_magnitude: Minimum absolute number to adjust capacity with as result of percentage scaling. Only when using AdjustmentType = PercentChangeInCapacity, this number controls the minimum absolute effect size. Default: No minimum scaling effect

        Stability:
            experimental
        """
        props: BasicStepScalingPolicyProps = {"metric": metric, "scalingSteps": scaling_steps}

        if adjustment_type is not None:
            props["adjustmentType"] = adjustment_type

        if cooldown is not None:
            props["cooldown"] = cooldown

        if min_adjustment_magnitude is not None:
            props["minAdjustmentMagnitude"] = min_adjustment_magnitude

        return jsii.invoke(self, "scaleOnMetric", [id, props])

    @jsii.member(jsii_name="scaleOnSchedule")
    def scale_on_schedule(self, id: str, *, schedule: "Schedule", end_time: typing.Optional[datetime.datetime]=None, max_capacity: typing.Optional[jsii.Number]=None, min_capacity: typing.Optional[jsii.Number]=None, start_time: typing.Optional[datetime.datetime]=None) -> None:
        """Scale out or in based on time.

        Arguments:
            id: -
            action: -
            schedule: When to perform this action.
            end_time: When this scheduled action expires. Default: The rule never expires.
            max_capacity: The new maximum capacity. During the scheduled time, the current capacity is above the maximum capacity, Application Auto Scaling scales in to the maximum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new maximum capacity
            min_capacity: The new minimum capacity. During the scheduled time, if the current capacity is below the minimum capacity, Application Auto Scaling scales out to the minimum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new minimum capacity
            start_time: When this scheduled action becomes active. Default: The rule is activate immediately

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
    def scale_to_track_metric(self, id: str, *, target_value: jsii.Number, custom_metric: typing.Optional[aws_cdk.aws_cloudwatch.IMetric]=None, predefined_metric: typing.Optional["PredefinedMetric"]=None, resource_label: typing.Optional[str]=None, disable_scale_in: typing.Optional[bool]=None, policy_name: typing.Optional[str]=None, scale_in_cooldown: typing.Optional[aws_cdk.core.Duration]=None, scale_out_cooldown: typing.Optional[aws_cdk.core.Duration]=None) -> "TargetTrackingScalingPolicy":
        """Scale out or in in order to keep a metric around a target value.

        Arguments:
            id: -
            props: -
            target_value: The target value for the metric.
            custom_metric: A custom metric for application autoscaling. The metric must track utilization. Scaling out will happen if the metric is higher than the target value, scaling in will happen in the metric is lower than the target value. Exactly one of customMetric or predefinedMetric must be specified. Default: - No custom metric.
            predefined_metric: A predefined metric for application autoscaling. The metric must track utilization. Scaling out will happen if the metric is higher than the target value, scaling in will happen in the metric is lower than the target value. Exactly one of customMetric or predefinedMetric must be specified. Default: - No predefined metrics.
            resource_label: Identify the resource associated with the metric type. Only used for predefined metric ALBRequestCountPerTarget. Default: - No resource label.
            disable_scale_in: Indicates whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. Default: false
            policy_name: A name for the scaling policy. Default: - Automatically generated name.
            scale_in_cooldown: Period after a scale in activity completes before another scale in activity can start. Default: - No scale in cooldown.
            scale_out_cooldown: Period after a scale out activity completes before another scale out activity can start. Default: - No scale out cooldown.

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

        if scale_in_cooldown is not None:
            props["scaleInCooldown"] = scale_in_cooldown

        if scale_out_cooldown is not None:
            props["scaleOutCooldown"] = scale_out_cooldown

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
    schedule: "Schedule"
    """When to perform this action.

    Stability:
        experimental
    """

class Schedule(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-applicationautoscaling.Schedule"):
    """Schedule for scheduled scaling actions.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ScheduleProxy

    def __init__(self) -> None:
        """
        Stability:
            experimental
        """
        jsii.create(Schedule, self, [])

    @jsii.member(jsii_name="at")
    @classmethod
    def at(cls, moment: datetime.datetime) -> "Schedule":
        """Construct a Schedule from a moment in time.

        Arguments:
            moment: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "at", [moment])

    @jsii.member(jsii_name="cron")
    @classmethod
    def cron(cls, *, day: typing.Optional[str]=None, hour: typing.Optional[str]=None, minute: typing.Optional[str]=None, month: typing.Optional[str]=None, week_day: typing.Optional[str]=None, year: typing.Optional[str]=None) -> "Schedule":
        """Create a schedule from a set of cron fields.

        Arguments:
            options: -
            day: The day of the month to run this rule at. Default: - Every day of the month
            hour: The hour to run this rule at. Default: - Every hour
            minute: The minute to run this rule at. Default: - Every minute
            month: The month to run this rule at. Default: - Every month
            week_day: The day of the week to run this rule at. Default: - Any day of the week
            year: The year to run this rule at. Default: - Every year

        Stability:
            experimental
        """
        options: CronOptions = {}

        if day is not None:
            options["day"] = day

        if hour is not None:
            options["hour"] = hour

        if minute is not None:
            options["minute"] = minute

        if month is not None:
            options["month"] = month

        if week_day is not None:
            options["weekDay"] = week_day

        if year is not None:
            options["year"] = year

        return jsii.sinvoke(cls, "cron", [options])

    @jsii.member(jsii_name="expression")
    @classmethod
    def expression(cls, expression: str) -> "Schedule":
        """Construct a schedule from a literal schedule expression.

        Arguments:
            expression: The expression to use. Must be in a format that Application AutoScaling will recognize

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "expression", [expression])

    @jsii.member(jsii_name="rate")
    @classmethod
    def rate(cls, duration: aws_cdk.core.Duration) -> "Schedule":
        """Construct a schedule from an interval and a time unit.

        Arguments:
            duration: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "rate", [duration])

    @property
    @jsii.member(jsii_name="expressionString")
    @abc.abstractmethod
    def expression_string(self) -> str:
        """Retrieve the expression for this schedule.

        Stability:
            experimental
        """
        ...


class _ScheduleProxy(Schedule):
    @property
    @jsii.member(jsii_name="expressionString")
    def expression_string(self) -> str:
        """Retrieve the expression for this schedule.

        Stability:
            experimental
        """
        return jsii.get(self, "expressionString")


@jsii.enum(jsii_type="@aws-cdk/aws-applicationautoscaling.ServiceNamespace")
class ServiceNamespace(enum.Enum):
    """The service that supports Application AutoScaling.

    Stability:
        experimental
    """
    ECS = "ECS"
    """Elastic Container Service.

    Stability:
        experimental
    """
    ELASTIC_MAP_REDUCE = "ELASTIC_MAP_REDUCE"
    """Elastic Map Reduce.

    Stability:
        experimental
    """
    EC2 = "EC2"
    """Elastic Compute Cloud.

    Stability:
        experimental
    """
    APPSTREAM = "APPSTREAM"
    """App Stream.

    Stability:
        experimental
    """
    DYNAMODB = "DYNAMODB"
    """Dynamo DB.

    Stability:
        experimental
    """
    RDS = "RDS"
    """Relational Database Service.

    Stability:
        experimental
    """
    SAGEMAKER = "SAGEMAKER"
    """SageMaker.

    Stability:
        experimental
    """
    CUSTOM_RESOURCE = "CUSTOM_RESOURCE"
    """Custom Resource.

    Stability:
        experimental
    """

class StepScalingAction(aws_cdk.core.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.StepScalingAction"):
    """Define a step scaling action.

    This kind of scaling policy adjusts the target capacity in configurable
    steps. The size of the step is configurable based on the metric's distance
    to its alarm threshold.

    This Action must be used as the target of a CloudWatch alarm to take effect.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, scaling_target: "IScalableTarget", adjustment_type: typing.Optional["AdjustmentType"]=None, cooldown: typing.Optional[aws_cdk.core.Duration]=None, metric_aggregation_type: typing.Optional["MetricAggregationType"]=None, min_adjustment_magnitude: typing.Optional[jsii.Number]=None, policy_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            scaling_target: The scalable target.
            adjustment_type: How the adjustment numbers are interpreted. Default: ChangeInCapacity
            cooldown: Grace period after scaling activity. For scale out policies, multiple scale outs during the cooldown period are squashed so that only the biggest scale out happens. For scale in policies, subsequent scale ins during the cooldown period are ignored. Default: No cooldown period
            metric_aggregation_type: The aggregation type for the CloudWatch metrics. Default: Average
            min_adjustment_magnitude: Minimum absolute number to adjust capacity with as result of percentage scaling. Only when using AdjustmentType = PercentChangeInCapacity, this number controls the minimum absolute effect size. Default: No minimum scaling effect
            policy_name: A name for the scaling policy. Default: Automatically generated name

        Stability:
            experimental
        """
        props: StepScalingActionProps = {"scalingTarget": scaling_target}

        if adjustment_type is not None:
            props["adjustmentType"] = adjustment_type

        if cooldown is not None:
            props["cooldown"] = cooldown

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
            lower_bound: Lower bound where this scaling tier applies. The scaling tier applies if the difference between the metric value and its alarm threshold is higher than this value. Default: -Infinity if this is the first tier, otherwise the upperBound of the previous tier
            upper_bound: Upper bound where this scaling tier applies. The scaling tier applies if the difference between the metric value and its alarm threshold is lower than this value. Default: +Infinity

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
    cooldown: aws_cdk.core.Duration
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

class StepScalingPolicy(aws_cdk.core.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.StepScalingPolicy"):
    """Define a acaling strategy which scales depending on absolute values of some metric.

    You can specify the scaling behavior for various values of the metric.

    Implemented using one or more CloudWatch alarms and Step Scaling Policies.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, scaling_target: "IScalableTarget", metric: aws_cdk.aws_cloudwatch.IMetric, scaling_steps: typing.List["ScalingInterval"], adjustment_type: typing.Optional["AdjustmentType"]=None, cooldown: typing.Optional[aws_cdk.core.Duration]=None, min_adjustment_magnitude: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            scaling_target: The scaling target.
            metric: Metric to scale on.
            scaling_steps: The intervals for scaling. Maps a range of metric values to a particular scaling behavior.
            adjustment_type: How the adjustment numbers inside 'intervals' are interpreted. Default: ChangeInCapacity
            cooldown: Grace period after scaling activity. Subsequent scale outs during the cooldown period are squashed so that only the biggest scale out happens. Subsequent scale ins during the cooldown period are ignored. Default: No cooldown period
            min_adjustment_magnitude: Minimum absolute number to adjust capacity with as result of percentage scaling. Only when using AdjustmentType = PercentChangeInCapacity, this number controls the minimum absolute effect size. Default: No minimum scaling effect

        Stability:
            experimental
        """
        props: StepScalingPolicyProps = {"scalingTarget": scaling_target, "metric": metric, "scalingSteps": scaling_steps}

        if adjustment_type is not None:
            props["adjustmentType"] = adjustment_type

        if cooldown is not None:
            props["cooldown"] = cooldown

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

class TargetTrackingScalingPolicy(aws_cdk.core.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-applicationautoscaling.TargetTrackingScalingPolicy"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, scaling_target: "IScalableTarget", target_value: jsii.Number, custom_metric: typing.Optional[aws_cdk.aws_cloudwatch.IMetric]=None, predefined_metric: typing.Optional["PredefinedMetric"]=None, resource_label: typing.Optional[str]=None, disable_scale_in: typing.Optional[bool]=None, policy_name: typing.Optional[str]=None, scale_in_cooldown: typing.Optional[aws_cdk.core.Duration]=None, scale_out_cooldown: typing.Optional[aws_cdk.core.Duration]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            scaling_target: 
            target_value: The target value for the metric.
            custom_metric: A custom metric for application autoscaling. The metric must track utilization. Scaling out will happen if the metric is higher than the target value, scaling in will happen in the metric is lower than the target value. Exactly one of customMetric or predefinedMetric must be specified. Default: - No custom metric.
            predefined_metric: A predefined metric for application autoscaling. The metric must track utilization. Scaling out will happen if the metric is higher than the target value, scaling in will happen in the metric is lower than the target value. Exactly one of customMetric or predefinedMetric must be specified. Default: - No predefined metrics.
            resource_label: Identify the resource associated with the metric type. Only used for predefined metric ALBRequestCountPerTarget. Default: - No resource label.
            disable_scale_in: Indicates whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. Default: false
            policy_name: A name for the scaling policy. Default: - Automatically generated name.
            scale_in_cooldown: Period after a scale in activity completes before another scale in activity can start. Default: - No scale in cooldown.
            scale_out_cooldown: Period after a scale out activity completes before another scale out activity can start. Default: - No scale out cooldown.

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

        if scale_in_cooldown is not None:
            props["scaleInCooldown"] = scale_in_cooldown

        if scale_out_cooldown is not None:
            props["scaleOutCooldown"] = scale_out_cooldown

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

__all__ = ["AdjustmentTier", "AdjustmentType", "BaseScalableAttribute", "BaseScalableAttributeProps", "BaseTargetTrackingProps", "BasicStepScalingPolicyProps", "BasicTargetTrackingScalingPolicyProps", "CfnScalableTarget", "CfnScalableTargetProps", "CfnScalingPolicy", "CfnScalingPolicyProps", "CronOptions", "EnableScalingProps", "IScalableTarget", "MetricAggregationType", "PredefinedMetric", "ScalableTarget", "ScalableTargetProps", "ScalingInterval", "ScalingSchedule", "Schedule", "ServiceNamespace", "StepScalingAction", "StepScalingActionProps", "StepScalingPolicy", "StepScalingPolicyProps", "TargetTrackingScalingPolicy", "TargetTrackingScalingPolicyProps", "__jsii_assembly__"]

publication.publish()
