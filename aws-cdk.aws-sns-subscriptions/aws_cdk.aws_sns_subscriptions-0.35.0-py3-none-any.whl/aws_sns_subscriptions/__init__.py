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
import aws_cdk.aws_sqs
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-sns-subscriptions", "0.35.0", __name__, "aws-sns-subscriptions@0.35.0.jsii.tgz")
@jsii.implements(aws_cdk.aws_sns.ITopicSubscription)
class EmailSubscription(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns-subscriptions.EmailSubscription"):
    """Use an email address as a subscription target.

    Email subscriptions require confirmation.

    Stability:
        experimental
    """
    def __init__(self, email_address: str, *, json: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            emailAddress: -
            props: -
            json: Indicates if the full notification JSON should be sent to the email address or just the message text. Default: false (Message text)

        Stability:
            experimental
        """
        props: EmailSubscriptionProps = {}

        if json is not None:
            props["json"] = json

        jsii.create(EmailSubscription, self, [email_address, props])

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.cdk.Construct, topic: aws_cdk.aws_sns.ITopic) -> None:
        """
        Arguments:
            scope: -
            topic: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [scope, topic])


@jsii.data_type(jsii_type="@aws-cdk/aws-sns-subscriptions.EmailSubscriptionProps", jsii_struct_bases=[])
class EmailSubscriptionProps(jsii.compat.TypedDict, total=False):
    """Options for email subscriptions.

    Stability:
        experimental
    """
    json: bool
    """Indicates if the full notification JSON should be sent to the email address or just the message text.

    Default:
        false (Message text)

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_sns.ITopicSubscription)
class LambdaSubscription(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns-subscriptions.LambdaSubscription"):
    """Use a Lambda function as a subscription target.

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
        jsii.create(LambdaSubscription, self, [fn])

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: aws_cdk.cdk.Construct, topic: aws_cdk.aws_sns.ITopic) -> None:
        """
        Arguments:
            _scope: -
            topic: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_scope, topic])


@jsii.implements(aws_cdk.aws_sns.ITopicSubscription)
class SqsSubscription(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns-subscriptions.SqsSubscription"):
    """Use an SQS queue as a subscription target.

    Stability:
        experimental
    """
    def __init__(self, queue: aws_cdk.aws_sqs.IQueue, *, raw_message_delivery: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            queue: -
            props: -
            rawMessageDelivery: The message to the queue is the same as it was sent to the topic. If false, the message will be wrapped in an SNS envelope. Default: false

        Stability:
            experimental
        """
        props: SqsSubscriptionProps = {}

        if raw_message_delivery is not None:
            props["rawMessageDelivery"] = raw_message_delivery

        jsii.create(SqsSubscription, self, [queue, props])

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: aws_cdk.cdk.Construct, topic: aws_cdk.aws_sns.ITopic) -> None:
        """
        Arguments:
            _scope: -
            topic: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_scope, topic])


@jsii.data_type(jsii_type="@aws-cdk/aws-sns-subscriptions.SqsSubscriptionProps", jsii_struct_bases=[])
class SqsSubscriptionProps(jsii.compat.TypedDict, total=False):
    """Properties for an SQS subscription.

    Stability:
        experimental
    """
    rawMessageDelivery: bool
    """The message to the queue is the same as it was sent to the topic.

    If false, the message will be wrapped in an SNS envelope.

    Default:
        false

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_sns.ITopicSubscription)
class UrlSubscription(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns-subscriptions.UrlSubscription"):
    """Use a URL as a subscription target.

    The message will be POSTed to the given URL.

    See:
        https://docs.aws.amazon.com/sns/latest/dg/sns-http-https-endpoint-as-subscriber.html
    Stability:
        experimental
    """
    def __init__(self, url: str, *, raw_message_delivery: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            url: -
            props: -
            rawMessageDelivery: The message to the queue is the same as it was sent to the topic. If false, the message will be wrapped in an SNS envelope. Default: false

        Stability:
            experimental
        """
        props: UrlSubscriptionProps = {}

        if raw_message_delivery is not None:
            props["rawMessageDelivery"] = raw_message_delivery

        jsii.create(UrlSubscription, self, [url, props])

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.cdk.Construct, topic: aws_cdk.aws_sns.ITopic) -> None:
        """
        Arguments:
            scope: -
            topic: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [scope, topic])


@jsii.data_type(jsii_type="@aws-cdk/aws-sns-subscriptions.UrlSubscriptionProps", jsii_struct_bases=[])
class UrlSubscriptionProps(jsii.compat.TypedDict, total=False):
    """Options for URL subscriptions.

    Stability:
        experimental
    """
    rawMessageDelivery: bool
    """The message to the queue is the same as it was sent to the topic.

    If false, the message will be wrapped in an SNS envelope.

    Default:
        false

    Stability:
        experimental
    """

__all__ = ["EmailSubscription", "EmailSubscriptionProps", "LambdaSubscription", "SqsSubscription", "SqsSubscriptionProps", "UrlSubscription", "UrlSubscriptionProps", "__jsii_assembly__"]

publication.publish()
