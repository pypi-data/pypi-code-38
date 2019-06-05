import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_applicationautoscaling
import aws_cdk.aws_autoscaling
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_iam
import aws_cdk.aws_sns
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-cloudwatch-actions", "0.33.0", __name__, "aws-cloudwatch-actions@0.33.0.jsii.tgz")
@jsii.implements(aws_cdk.aws_cloudwatch.IAlarmAction)
class ApplicationScalingAction(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch-actions.ApplicationScalingAction"):
    """Use an ApplicationAutoScaling StepScalingAction as an Alarm Action."""
    def __init__(self, step_scaling_action: aws_cdk.aws_applicationautoscaling.StepScalingAction) -> None:
        """
        Arguments:
            stepScalingAction: -
        """
        jsii.create(ApplicationScalingAction, self, [step_scaling_action])

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: aws_cdk.cdk.Construct, _alarm: aws_cdk.aws_cloudwatch.IAlarm) -> aws_cdk.aws_cloudwatch.AlarmActionConfig:
        """
        Arguments:
            _scope: -
            _alarm: -
        """
        return jsii.invoke(self, "bind", [_scope, _alarm])

    @property
    @jsii.member(jsii_name="stepScalingAction")
    def step_scaling_action(self) -> aws_cdk.aws_applicationautoscaling.StepScalingAction:
        return jsii.get(self, "stepScalingAction")


@jsii.implements(aws_cdk.aws_cloudwatch.IAlarmAction)
class AutoScalingAction(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch-actions.AutoScalingAction"):
    """Use an AutoScaling StepScalingAction as an Alarm Action."""
    def __init__(self, step_scaling_action: aws_cdk.aws_autoscaling.StepScalingAction) -> None:
        """
        Arguments:
            stepScalingAction: -
        """
        jsii.create(AutoScalingAction, self, [step_scaling_action])

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: aws_cdk.cdk.Construct, _alarm: aws_cdk.aws_cloudwatch.IAlarm) -> aws_cdk.aws_cloudwatch.AlarmActionConfig:
        """
        Arguments:
            _scope: -
            _alarm: -
        """
        return jsii.invoke(self, "bind", [_scope, _alarm])

    @property
    @jsii.member(jsii_name="stepScalingAction")
    def step_scaling_action(self) -> aws_cdk.aws_autoscaling.StepScalingAction:
        return jsii.get(self, "stepScalingAction")


@jsii.implements(aws_cdk.aws_cloudwatch.IAlarmAction)
class SnsAction(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch-actions.SnsAction"):
    """Use an SNS topic as an alarm action."""
    def __init__(self, topic: aws_cdk.aws_sns.ITopic) -> None:
        """
        Arguments:
            topic: -
        """
        jsii.create(SnsAction, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: aws_cdk.cdk.Construct, _alarm: aws_cdk.aws_cloudwatch.IAlarm) -> aws_cdk.aws_cloudwatch.AlarmActionConfig:
        """
        Arguments:
            _scope: -
            _alarm: -
        """
        return jsii.invoke(self, "bind", [_scope, _alarm])

    @property
    @jsii.member(jsii_name="topic")
    def topic(self) -> aws_cdk.aws_sns.ITopic:
        return jsii.get(self, "topic")


__all__ = ["ApplicationScalingAction", "AutoScalingAction", "SnsAction", "__jsii_assembly__"]

publication.publish()
