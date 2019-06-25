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
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-sns-subscriptions", "0.36.0", __name__, "aws-sns-subscriptions@0.36.0.jsii.tgz")
@jsii.implements(aws_cdk.aws_sns.ITopicSubscription)
class EmailSubscription(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns-subscriptions.EmailSubscription"):
    """Use an email address as a subscription target.

    Email subscriptions require confirmation.

    Stability:
        experimental
    """
    def __init__(self, email_address: str, *, json: typing.Optional[bool]=None, filter_policy: typing.Optional[typing.Mapping[str,aws_cdk.aws_sns.SubscriptionFilter]]=None) -> None:
        """
        Arguments:
            email_address: -
            props: -
            json: Indicates if the full notification JSON should be sent to the email address or just the message text. Default: false (Message text)
            filter_policy: The filter policy. Default: - all messages are delivered

        Stability:
            experimental
        """
        props: EmailSubscriptionProps = {}

        if json is not None:
            props["json"] = json

        if filter_policy is not None:
            props["filterPolicy"] = filter_policy

        jsii.create(EmailSubscription, self, [email_address, props])

    @jsii.member(jsii_name="bind")
    def bind(self, _topic: aws_cdk.aws_sns.ITopic) -> aws_cdk.aws_sns.TopicSubscriptionConfig:
        """
        Arguments:
            _topic: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_topic])


@jsii.implements(aws_cdk.aws_sns.ITopicSubscription)
class LambdaSubscription(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns-subscriptions.LambdaSubscription"):
    """Use a Lambda function as a subscription target.

    Stability:
        experimental
    """
    def __init__(self, fn: aws_cdk.aws_lambda.IFunction, *, filter_policy: typing.Optional[typing.Mapping[str,aws_cdk.aws_sns.SubscriptionFilter]]=None) -> None:
        """
        Arguments:
            fn: -
            props: -
            filter_policy: The filter policy. Default: - all messages are delivered

        Stability:
            experimental
        """
        props: LambdaSubscriptionProps = {}

        if filter_policy is not None:
            props["filterPolicy"] = filter_policy

        jsii.create(LambdaSubscription, self, [fn, props])

    @jsii.member(jsii_name="bind")
    def bind(self, topic: aws_cdk.aws_sns.ITopic) -> aws_cdk.aws_sns.TopicSubscriptionConfig:
        """
        Arguments:
            topic: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [topic])


@jsii.implements(aws_cdk.aws_sns.ITopicSubscription)
class SqsSubscription(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns-subscriptions.SqsSubscription"):
    """Use an SQS queue as a subscription target.

    Stability:
        experimental
    """
    def __init__(self, queue: aws_cdk.aws_sqs.IQueue, *, raw_message_delivery: typing.Optional[bool]=None, filter_policy: typing.Optional[typing.Mapping[str,aws_cdk.aws_sns.SubscriptionFilter]]=None) -> None:
        """
        Arguments:
            queue: -
            props: -
            raw_message_delivery: The message to the queue is the same as it was sent to the topic. If false, the message will be wrapped in an SNS envelope. Default: false
            filter_policy: The filter policy. Default: - all messages are delivered

        Stability:
            experimental
        """
        props: SqsSubscriptionProps = {}

        if raw_message_delivery is not None:
            props["rawMessageDelivery"] = raw_message_delivery

        if filter_policy is not None:
            props["filterPolicy"] = filter_policy

        jsii.create(SqsSubscription, self, [queue, props])

    @jsii.member(jsii_name="bind")
    def bind(self, topic: aws_cdk.aws_sns.ITopic) -> aws_cdk.aws_sns.TopicSubscriptionConfig:
        """
        Arguments:
            topic: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [topic])


@jsii.data_type(jsii_type="@aws-cdk/aws-sns-subscriptions.SubscriptionProps", jsii_struct_bases=[])
class SubscriptionProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    filterPolicy: typing.Mapping[str,aws_cdk.aws_sns.SubscriptionFilter]
    """The filter policy.

    Default:
        - all messages are delivered

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sns-subscriptions.EmailSubscriptionProps", jsii_struct_bases=[SubscriptionProps])
class EmailSubscriptionProps(SubscriptionProps, jsii.compat.TypedDict, total=False):
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

@jsii.data_type(jsii_type="@aws-cdk/aws-sns-subscriptions.LambdaSubscriptionProps", jsii_struct_bases=[SubscriptionProps])
class LambdaSubscriptionProps(SubscriptionProps, jsii.compat.TypedDict):
    """Properties for a Lambda subscription.

    Stability:
        experimental
    """
    pass

@jsii.data_type(jsii_type="@aws-cdk/aws-sns-subscriptions.SqsSubscriptionProps", jsii_struct_bases=[SubscriptionProps])
class SqsSubscriptionProps(SubscriptionProps, jsii.compat.TypedDict, total=False):
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
    def __init__(self, url: str, *, raw_message_delivery: typing.Optional[bool]=None, filter_policy: typing.Optional[typing.Mapping[str,aws_cdk.aws_sns.SubscriptionFilter]]=None) -> None:
        """
        Arguments:
            url: -
            props: -
            raw_message_delivery: The message to the queue is the same as it was sent to the topic. If false, the message will be wrapped in an SNS envelope. Default: false
            filter_policy: The filter policy. Default: - all messages are delivered

        Stability:
            experimental
        """
        props: UrlSubscriptionProps = {}

        if raw_message_delivery is not None:
            props["rawMessageDelivery"] = raw_message_delivery

        if filter_policy is not None:
            props["filterPolicy"] = filter_policy

        jsii.create(UrlSubscription, self, [url, props])

    @jsii.member(jsii_name="bind")
    def bind(self, _topic: aws_cdk.aws_sns.ITopic) -> aws_cdk.aws_sns.TopicSubscriptionConfig:
        """
        Arguments:
            _topic: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_topic])


@jsii.data_type(jsii_type="@aws-cdk/aws-sns-subscriptions.UrlSubscriptionProps", jsii_struct_bases=[SubscriptionProps])
class UrlSubscriptionProps(SubscriptionProps, jsii.compat.TypedDict, total=False):
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

__all__ = ["EmailSubscription", "EmailSubscriptionProps", "LambdaSubscription", "LambdaSubscriptionProps", "SqsSubscription", "SqsSubscriptionProps", "SubscriptionProps", "UrlSubscription", "UrlSubscriptionProps", "__jsii_assembly__"]

publication.publish()
