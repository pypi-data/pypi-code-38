import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_autoscaling
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_sns
import aws_cdk.aws_sqs
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-autoscaling-hooktargets", "0.34.0", __name__, "aws-autoscaling-hooktargets@0.34.0.jsii.tgz")
@jsii.implements(aws_cdk.aws_autoscaling.ILifecycleHookTarget)
class FunctionHook(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-autoscaling-hooktargets.FunctionHook"):
    """Use a Lambda Function as a hook target.

    Internally creates a Topic to make the connection.

    Stability:
        experimental
    """
    def __init__(self, fn: aws_cdk.aws_lambda.IFunction) -> None:
        """
        Arguments:
            fn: -

        Stability:
            experimental
        """
        jsii.create(FunctionHook, self, [fn])

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.cdk.Construct, lifecycle_hook: aws_cdk.aws_autoscaling.ILifecycleHook) -> aws_cdk.aws_autoscaling.LifecycleHookTargetConfig:
        """Called when this object is used as the target of a lifecycle hook.

        Arguments:
            scope: -
            lifecycleHook: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [scope, lifecycle_hook])

    @property
    @jsii.member(jsii_name="fn")
    def fn(self) -> aws_cdk.aws_lambda.IFunction:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "fn")


@jsii.implements(aws_cdk.aws_autoscaling.ILifecycleHookTarget)
class QueueHook(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-autoscaling-hooktargets.QueueHook"):
    """Use an SQS queue as a hook target.

    Stability:
        experimental
    """
    def __init__(self, queue: aws_cdk.aws_sqs.IQueue) -> None:
        """
        Arguments:
            queue: -

        Stability:
            experimental
        """
        jsii.create(QueueHook, self, [queue])

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: aws_cdk.cdk.Construct, lifecycle_hook: aws_cdk.aws_autoscaling.ILifecycleHook) -> aws_cdk.aws_autoscaling.LifecycleHookTargetConfig:
        """Called when this object is used as the target of a lifecycle hook.

        Arguments:
            _scope: -
            lifecycleHook: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_scope, lifecycle_hook])

    @property
    @jsii.member(jsii_name="queue")
    def queue(self) -> aws_cdk.aws_sqs.IQueue:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "queue")


@jsii.implements(aws_cdk.aws_autoscaling.ILifecycleHookTarget)
class TopicHook(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-autoscaling-hooktargets.TopicHook"):
    """Use an SNS topic as a hook target.

    Stability:
        experimental
    """
    def __init__(self, topic: aws_cdk.aws_sns.ITopic) -> None:
        """
        Arguments:
            topic: -

        Stability:
            experimental
        """
        jsii.create(TopicHook, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: aws_cdk.cdk.Construct, lifecycle_hook: aws_cdk.aws_autoscaling.ILifecycleHook) -> aws_cdk.aws_autoscaling.LifecycleHookTargetConfig:
        """Called when this object is used as the target of a lifecycle hook.

        Arguments:
            _scope: -
            lifecycleHook: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_scope, lifecycle_hook])

    @property
    @jsii.member(jsii_name="topic")
    def topic(self) -> aws_cdk.aws_sns.ITopic:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "topic")


__all__ = ["FunctionHook", "QueueHook", "TopicHook", "__jsii_assembly__"]

publication.publish()
