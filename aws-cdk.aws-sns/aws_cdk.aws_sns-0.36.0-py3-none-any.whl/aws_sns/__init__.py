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
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-sns", "0.36.0", __name__, "aws-sns@0.36.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-sns.BetweenCondition", jsii_struct_bases=[])
class BetweenCondition(jsii.compat.TypedDict):
    """Between condition for a numeric attribute.

    Stability:
        experimental
    """
    start: jsii.Number
    """The start value.

    Stability:
        experimental
    """

    stop: jsii.Number
    """The stop value.

    Stability:
        experimental
    """

class CfnSubscription(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns.CfnSubscription"):
    """A CloudFormation ``AWS::SNS::Subscription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html
    Stability:
        stable
    cloudformationResource:
        AWS::SNS::Subscription
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, protocol: str, topic_arn: str, delivery_policy: typing.Any=None, endpoint: typing.Optional[str]=None, filter_policy: typing.Any=None, raw_message_delivery: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, region: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SNS::Subscription``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            protocol: ``AWS::SNS::Subscription.Protocol``.
            topic_arn: ``AWS::SNS::Subscription.TopicArn``.
            delivery_policy: ``AWS::SNS::Subscription.DeliveryPolicy``.
            endpoint: ``AWS::SNS::Subscription.Endpoint``.
            filter_policy: ``AWS::SNS::Subscription.FilterPolicy``.
            raw_message_delivery: ``AWS::SNS::Subscription.RawMessageDelivery``.
            region: ``AWS::SNS::Subscription.Region``.

        Stability:
            experimental
        """
        props: CfnSubscriptionProps = {"protocol": protocol, "topicArn": topic_arn}

        if delivery_policy is not None:
            props["deliveryPolicy"] = delivery_policy

        if endpoint is not None:
            props["endpoint"] = endpoint

        if filter_policy is not None:
            props["filterPolicy"] = filter_policy

        if raw_message_delivery is not None:
            props["rawMessageDelivery"] = raw_message_delivery

        if region is not None:
            props["region"] = region

        jsii.create(CfnSubscription, self, [scope, id, props])

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
    @jsii.member(jsii_name="deliveryPolicy")
    def delivery_policy(self) -> typing.Any:
        """``AWS::SNS::Subscription.DeliveryPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-subscription-deliverypolicy
        Stability:
            stable
        """
        return jsii.get(self, "deliveryPolicy")

    @delivery_policy.setter
    def delivery_policy(self, value: typing.Any):
        return jsii.set(self, "deliveryPolicy", value)

    @property
    @jsii.member(jsii_name="filterPolicy")
    def filter_policy(self) -> typing.Any:
        """``AWS::SNS::Subscription.FilterPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-subscription-filterpolicy
        Stability:
            stable
        """
        return jsii.get(self, "filterPolicy")

    @filter_policy.setter
    def filter_policy(self, value: typing.Any):
        return jsii.set(self, "filterPolicy", value)

    @property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> str:
        """``AWS::SNS::Subscription.Protocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-protocol
        Stability:
            stable
        """
        return jsii.get(self, "protocol")

    @protocol.setter
    def protocol(self, value: str):
        return jsii.set(self, "protocol", value)

    @property
    @jsii.member(jsii_name="topicArn")
    def topic_arn(self) -> str:
        """``AWS::SNS::Subscription.TopicArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#topicarn
        Stability:
            stable
        """
        return jsii.get(self, "topicArn")

    @topic_arn.setter
    def topic_arn(self, value: str):
        return jsii.set(self, "topicArn", value)

    @property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> typing.Optional[str]:
        """``AWS::SNS::Subscription.Endpoint``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-endpoint
        Stability:
            stable
        """
        return jsii.get(self, "endpoint")

    @endpoint.setter
    def endpoint(self, value: typing.Optional[str]):
        return jsii.set(self, "endpoint", value)

    @property
    @jsii.member(jsii_name="rawMessageDelivery")
    def raw_message_delivery(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::SNS::Subscription.RawMessageDelivery``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-subscription-rawmessagedelivery
        Stability:
            stable
        """
        return jsii.get(self, "rawMessageDelivery")

    @raw_message_delivery.setter
    def raw_message_delivery(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "rawMessageDelivery", value)

    @property
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[str]:
        """``AWS::SNS::Subscription.Region``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-subscription-region
        Stability:
            stable
        """
        return jsii.get(self, "region")

    @region.setter
    def region(self, value: typing.Optional[str]):
        return jsii.set(self, "region", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSubscriptionProps(jsii.compat.TypedDict, total=False):
    deliveryPolicy: typing.Any
    """``AWS::SNS::Subscription.DeliveryPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-subscription-deliverypolicy
    Stability:
        stable
    """
    endpoint: str
    """``AWS::SNS::Subscription.Endpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-endpoint
    Stability:
        stable
    """
    filterPolicy: typing.Any
    """``AWS::SNS::Subscription.FilterPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-subscription-filterpolicy
    Stability:
        stable
    """
    rawMessageDelivery: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::SNS::Subscription.RawMessageDelivery``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-subscription-rawmessagedelivery
    Stability:
        stable
    """
    region: str
    """``AWS::SNS::Subscription.Region``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-subscription-region
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sns.CfnSubscriptionProps", jsii_struct_bases=[_CfnSubscriptionProps])
class CfnSubscriptionProps(_CfnSubscriptionProps):
    """Properties for defining a ``AWS::SNS::Subscription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html
    Stability:
        stable
    """
    protocol: str
    """``AWS::SNS::Subscription.Protocol``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-protocol
    Stability:
        stable
    """

    topicArn: str
    """``AWS::SNS::Subscription.TopicArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#topicarn
    Stability:
        stable
    """

class CfnTopic(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns.CfnTopic"):
    """A CloudFormation ``AWS::SNS::Topic``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html
    Stability:
        stable
    cloudformationResource:
        AWS::SNS::Topic
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, display_name: typing.Optional[str]=None, kms_master_key_id: typing.Optional[str]=None, subscription: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SubscriptionProperty"]]]]]=None, topic_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SNS::Topic``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            display_name: ``AWS::SNS::Topic.DisplayName``.
            kms_master_key_id: ``AWS::SNS::Topic.KmsMasterKeyId``.
            subscription: ``AWS::SNS::Topic.Subscription``.
            topic_name: ``AWS::SNS::Topic.TopicName``.

        Stability:
            experimental
        """
        props: CfnTopicProps = {}

        if display_name is not None:
            props["displayName"] = display_name

        if kms_master_key_id is not None:
            props["kmsMasterKeyId"] = kms_master_key_id

        if subscription is not None:
            props["subscription"] = subscription

        if topic_name is not None:
            props["topicName"] = topic_name

        jsii.create(CfnTopic, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrTopicName")
    def attr_topic_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            TopicName
        """
        return jsii.get(self, "attrTopicName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> typing.Optional[str]:
        """``AWS::SNS::Topic.DisplayName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html#cfn-sns-topic-displayname
        Stability:
            stable
        """
        return jsii.get(self, "displayName")

    @display_name.setter
    def display_name(self, value: typing.Optional[str]):
        return jsii.set(self, "displayName", value)

    @property
    @jsii.member(jsii_name="kmsMasterKeyId")
    def kms_master_key_id(self) -> typing.Optional[str]:
        """``AWS::SNS::Topic.KmsMasterKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html#cfn-sns-topic-kmsmasterkeyid
        Stability:
            stable
        """
        return jsii.get(self, "kmsMasterKeyId")

    @kms_master_key_id.setter
    def kms_master_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsMasterKeyId", value)

    @property
    @jsii.member(jsii_name="subscription")
    def subscription(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SubscriptionProperty"]]]]]:
        """``AWS::SNS::Topic.Subscription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html#cfn-sns-topic-subscription
        Stability:
            stable
        """
        return jsii.get(self, "subscription")

    @subscription.setter
    def subscription(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SubscriptionProperty"]]]]]):
        return jsii.set(self, "subscription", value)

    @property
    @jsii.member(jsii_name="topicName")
    def topic_name(self) -> typing.Optional[str]:
        """``AWS::SNS::Topic.TopicName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html#cfn-sns-topic-topicname
        Stability:
            stable
        """
        return jsii.get(self, "topicName")

    @topic_name.setter
    def topic_name(self, value: typing.Optional[str]):
        return jsii.set(self, "topicName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-sns.CfnTopic.SubscriptionProperty", jsii_struct_bases=[])
    class SubscriptionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-subscription.html
        Stability:
            stable
        """
        endpoint: str
        """``CfnTopic.SubscriptionProperty.Endpoint``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-subscription.html#cfn-sns-topic-subscription-endpoint
        Stability:
            stable
        """

        protocol: str
        """``CfnTopic.SubscriptionProperty.Protocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-subscription.html#cfn-sns-topic-subscription-protocol
        Stability:
            stable
        """


class CfnTopicPolicy(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns.CfnTopicPolicy"):
    """A CloudFormation ``AWS::SNS::TopicPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-policy.html
    Stability:
        stable
    cloudformationResource:
        AWS::SNS::TopicPolicy
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, policy_document: typing.Any, topics: typing.List[str]) -> None:
        """Create a new ``AWS::SNS::TopicPolicy``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            policy_document: ``AWS::SNS::TopicPolicy.PolicyDocument``.
            topics: ``AWS::SNS::TopicPolicy.Topics``.

        Stability:
            experimental
        """
        props: CfnTopicPolicyProps = {"policyDocument": policy_document, "topics": topics}

        jsii.create(CfnTopicPolicy, self, [scope, id, props])

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
    @jsii.member(jsii_name="policyDocument")
    def policy_document(self) -> typing.Any:
        """``AWS::SNS::TopicPolicy.PolicyDocument``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-policy.html#cfn-sns-topicpolicy-policydocument
        Stability:
            stable
        """
        return jsii.get(self, "policyDocument")

    @policy_document.setter
    def policy_document(self, value: typing.Any):
        return jsii.set(self, "policyDocument", value)

    @property
    @jsii.member(jsii_name="topics")
    def topics(self) -> typing.List[str]:
        """``AWS::SNS::TopicPolicy.Topics``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-policy.html#cfn-sns-topicpolicy-topics
        Stability:
            stable
        """
        return jsii.get(self, "topics")

    @topics.setter
    def topics(self, value: typing.List[str]):
        return jsii.set(self, "topics", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-sns.CfnTopicPolicyProps", jsii_struct_bases=[])
class CfnTopicPolicyProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::SNS::TopicPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-policy.html
    Stability:
        stable
    """
    policyDocument: typing.Any
    """``AWS::SNS::TopicPolicy.PolicyDocument``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-policy.html#cfn-sns-topicpolicy-policydocument
    Stability:
        stable
    """

    topics: typing.List[str]
    """``AWS::SNS::TopicPolicy.Topics``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-policy.html#cfn-sns-topicpolicy-topics
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sns.CfnTopicProps", jsii_struct_bases=[])
class CfnTopicProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::SNS::Topic``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html
    Stability:
        stable
    """
    displayName: str
    """``AWS::SNS::Topic.DisplayName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html#cfn-sns-topic-displayname
    Stability:
        stable
    """

    kmsMasterKeyId: str
    """``AWS::SNS::Topic.KmsMasterKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html#cfn-sns-topic-kmsmasterkeyid
    Stability:
        stable
    """

    subscription: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnTopic.SubscriptionProperty"]]]
    """``AWS::SNS::Topic.Subscription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html#cfn-sns-topic-subscription
    Stability:
        stable
    """

    topicName: str
    """``AWS::SNS::Topic.TopicName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html#cfn-sns-topic-topicname
    Stability:
        stable
    """

@jsii.interface(jsii_type="@aws-cdk/aws-sns.ITopic")
class ITopic(aws_cdk.core.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ITopicProxy

    @property
    @jsii.member(jsii_name="topicArn")
    def topic_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="topicName")
    def topic_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...

    @jsii.member(jsii_name="addSubscription")
    def add_subscription(self, subscription: "ITopicSubscription") -> None:
        """Subscribe some endpoint to this topic.

        Arguments:
            subscription: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Adds a statement to the IAM resource policy associated with this topic.

        If this topic was created in this stack (``new Topic``), a topic policy
        will be automatically created upon the first call to ``addToPolicy``. If
        the topic is improted (``Topic.import``), then this is a no-op.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantPublish")
    def grant_publish(self, identity: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant topic publishing permissions to the given identity.

        Arguments:
            identity: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Topic.

        Arguments:
            metric_name: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricNumberOfMessagesPublished")
    def metric_number_of_messages_published(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages published to your Amazon SNS topics.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricNumberOfNotificationsDelivered")
    def metric_number_of_notifications_delivered(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages successfully delivered from your Amazon SNS topics to subscribing endpoints.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricNumberOfNotificationsFailed")
    def metric_number_of_notifications_failed(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that Amazon SNS failed to deliver.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricNumberOfNotificationsFilteredOut")
    def metric_number_of_notifications_filtered_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that were rejected by subscription filter policies.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricNumberOfNotificationsFilteredOutInvalidAttributes")
    def metric_number_of_notifications_filtered_out_invalid_attributes(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that were rejected by subscription filter policies because the messages' attributes are invalid.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricNumberOfNotificationsFilteredOutNoMessageAttributes")
    def metric_number_of_notifications_filtered_out_no_message_attributes(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that were rejected by subscription filter policies because the messages have no attributes.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricPublishSize")
    def metric_publish_size(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the size of messages published through this topic.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricSMSMonthToDateSpentUSD")
    def metric_sms_month_to_date_spent_usd(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The charges you have accrued since the start of the current calendar month for sending SMS messages.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricSMSSuccessRate")
    def metric_sms_success_rate(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The rate of successful SMS message deliveries.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...


class _ITopicProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-sns.ITopic"
    @property
    @jsii.member(jsii_name="topicArn")
    def topic_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "topicArn")

    @property
    @jsii.member(jsii_name="topicName")
    def topic_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "topicName")

    @jsii.member(jsii_name="addSubscription")
    def add_subscription(self, subscription: "ITopicSubscription") -> None:
        """Subscribe some endpoint to this topic.

        Arguments:
            subscription: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addSubscription", [subscription])

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Adds a statement to the IAM resource policy associated with this topic.

        If this topic was created in this stack (``new Topic``), a topic policy
        will be automatically created upon the first call to ``addToPolicy``. If
        the topic is improted (``Topic.import``), then this is a no-op.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToResourcePolicy", [statement])

    @jsii.member(jsii_name="grantPublish")
    def grant_publish(self, identity: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant topic publishing permissions to the given identity.

        Arguments:
            identity: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPublish", [identity])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Topic.

        Arguments:
            metric_name: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricNumberOfMessagesPublished")
    def metric_number_of_messages_published(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages published to your Amazon SNS topics.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfMessagesPublished", [props])

    @jsii.member(jsii_name="metricNumberOfNotificationsDelivered")
    def metric_number_of_notifications_delivered(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages successfully delivered from your Amazon SNS topics to subscribing endpoints.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfNotificationsDelivered", [props])

    @jsii.member(jsii_name="metricNumberOfNotificationsFailed")
    def metric_number_of_notifications_failed(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that Amazon SNS failed to deliver.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfNotificationsFailed", [props])

    @jsii.member(jsii_name="metricNumberOfNotificationsFilteredOut")
    def metric_number_of_notifications_filtered_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that were rejected by subscription filter policies.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfNotificationsFilteredOut", [props])

    @jsii.member(jsii_name="metricNumberOfNotificationsFilteredOutInvalidAttributes")
    def metric_number_of_notifications_filtered_out_invalid_attributes(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that were rejected by subscription filter policies because the messages' attributes are invalid.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfNotificationsFilteredOutInvalidAttributes", [props])

    @jsii.member(jsii_name="metricNumberOfNotificationsFilteredOutNoMessageAttributes")
    def metric_number_of_notifications_filtered_out_no_message_attributes(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that were rejected by subscription filter policies because the messages have no attributes.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfNotificationsFilteredOutNoMessageAttributes", [props])

    @jsii.member(jsii_name="metricPublishSize")
    def metric_publish_size(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the size of messages published through this topic.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricPublishSize", [props])

    @jsii.member(jsii_name="metricSMSMonthToDateSpentUSD")
    def metric_sms_month_to_date_spent_usd(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The charges you have accrued since the start of the current calendar month for sending SMS messages.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricSMSMonthToDateSpentUSD", [props])

    @jsii.member(jsii_name="metricSMSSuccessRate")
    def metric_sms_success_rate(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The rate of successful SMS message deliveries.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricSMSSuccessRate", [props])


@jsii.interface(jsii_type="@aws-cdk/aws-sns.ITopicSubscription")
class ITopicSubscription(jsii.compat.Protocol):
    """Topic subscription.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ITopicSubscriptionProxy

    @jsii.member(jsii_name="bind")
    def bind(self, topic: "ITopic") -> "TopicSubscriptionConfig":
        """
        Arguments:
            topic: -

        Stability:
            experimental
        """
        ...


class _ITopicSubscriptionProxy():
    """Topic subscription.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-sns.ITopicSubscription"
    @jsii.member(jsii_name="bind")
    def bind(self, topic: "ITopic") -> "TopicSubscriptionConfig":
        """
        Arguments:
            topic: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [topic])


@jsii.data_type(jsii_type="@aws-cdk/aws-sns.NumericConditions", jsii_struct_bases=[])
class NumericConditions(jsii.compat.TypedDict, total=False):
    """Conditions that can be applied to numeric attributes.

    Stability:
        experimental
    """
    between: "BetweenCondition"
    """Match values that are between the specified values.

    Stability:
        experimental
    """

    betweenStrict: "BetweenCondition"
    """Match values that are strictly between the specified values.

    Stability:
        experimental
    """

    greaterThan: jsii.Number
    """Match values that are greater than the specified value.

    Stability:
        experimental
    """

    greaterThanOrEqualTo: jsii.Number
    """Match values that are greater than or equal to the specified value.

    Stability:
        experimental
    """

    lessThan: jsii.Number
    """Match values that are less than the specified value.

    Stability:
        experimental
    """

    lessThanOrEqualTo: jsii.Number
    """Match values that are less than or equal to the specified value.

    Stability:
        experimental
    """

    whitelist: typing.List[jsii.Number]
    """Match one or more values.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sns.StringConditions", jsii_struct_bases=[])
class StringConditions(jsii.compat.TypedDict, total=False):
    """Conditions that can be applied to string attributes.

    Stability:
        experimental
    """
    blacklist: typing.List[str]
    """Match any value that doesn't include any of the specified values.

    Stability:
        experimental
    """

    matchPrefixes: typing.List[str]
    """Matches values that begins with the specified prefixes.

    Stability:
        experimental
    """

    whitelist: typing.List[str]
    """Match one or more values.

    Stability:
        experimental
    """

class Subscription(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns.Subscription"):
    """A new subscription.

    Prefer to use the ``ITopic.addSubscription()`` methods to create instances of
    this class.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, topic: "ITopic", endpoint: str, protocol: "SubscriptionProtocol", filter_policy: typing.Optional[typing.Mapping[str,"SubscriptionFilter"]]=None, raw_message_delivery: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            topic: The topic to subscribe to.
            endpoint: The subscription endpoint. The meaning of this value depends on the value for 'protocol'.
            protocol: What type of subscription to add.
            filter_policy: The filter policy. Default: - all messages are delivered
            raw_message_delivery: true if raw message delivery is enabled for the subscription. Raw messages are free of JSON formatting and can be sent to HTTP/S and Amazon SQS endpoints. For more information, see GetSubscriptionAttributes in the Amazon Simple Notification Service API Reference. Default: false

        Stability:
            experimental
        """
        props: SubscriptionProps = {"topic": topic, "endpoint": endpoint, "protocol": protocol}

        if filter_policy is not None:
            props["filterPolicy"] = filter_policy

        if raw_message_delivery is not None:
            props["rawMessageDelivery"] = raw_message_delivery

        jsii.create(Subscription, self, [scope, id, props])


class SubscriptionFilter(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns.SubscriptionFilter"):
    """A subscription filter for an attribute.

    Stability:
        experimental
    """
    def __init__(self, conditions: typing.Optional[typing.List[typing.Any]]=None) -> None:
        """
        Arguments:
            conditions: -

        Stability:
            experimental
        """
        jsii.create(SubscriptionFilter, self, [conditions])

    @jsii.member(jsii_name="numericFilter")
    @classmethod
    def numeric_filter(cls, *, between: typing.Optional["BetweenCondition"]=None, between_strict: typing.Optional["BetweenCondition"]=None, greater_than: typing.Optional[jsii.Number]=None, greater_than_or_equal_to: typing.Optional[jsii.Number]=None, less_than: typing.Optional[jsii.Number]=None, less_than_or_equal_to: typing.Optional[jsii.Number]=None, whitelist: typing.Optional[typing.List[jsii.Number]]=None) -> "SubscriptionFilter":
        """Returns a subscription filter for a numeric attribute.

        Arguments:
            numeric_conditions: -
            between: Match values that are between the specified values.
            between_strict: Match values that are strictly between the specified values.
            greater_than: Match values that are greater than the specified value.
            greater_than_or_equal_to: Match values that are greater than or equal to the specified value.
            less_than: Match values that are less than the specified value.
            less_than_or_equal_to: Match values that are less than or equal to the specified value.
            whitelist: Match one or more values.

        Stability:
            experimental
        """
        numeric_conditions: NumericConditions = {}

        if between is not None:
            numeric_conditions["between"] = between

        if between_strict is not None:
            numeric_conditions["betweenStrict"] = between_strict

        if greater_than is not None:
            numeric_conditions["greaterThan"] = greater_than

        if greater_than_or_equal_to is not None:
            numeric_conditions["greaterThanOrEqualTo"] = greater_than_or_equal_to

        if less_than is not None:
            numeric_conditions["lessThan"] = less_than

        if less_than_or_equal_to is not None:
            numeric_conditions["lessThanOrEqualTo"] = less_than_or_equal_to

        if whitelist is not None:
            numeric_conditions["whitelist"] = whitelist

        return jsii.sinvoke(cls, "numericFilter", [numeric_conditions])

    @jsii.member(jsii_name="stringFilter")
    @classmethod
    def string_filter(cls, *, blacklist: typing.Optional[typing.List[str]]=None, match_prefixes: typing.Optional[typing.List[str]]=None, whitelist: typing.Optional[typing.List[str]]=None) -> "SubscriptionFilter":
        """Returns a subscription filter for a string attribute.

        Arguments:
            string_conditions: -
            blacklist: Match any value that doesn't include any of the specified values.
            match_prefixes: Matches values that begins with the specified prefixes.
            whitelist: Match one or more values.

        Stability:
            experimental
        """
        string_conditions: StringConditions = {}

        if blacklist is not None:
            string_conditions["blacklist"] = blacklist

        if match_prefixes is not None:
            string_conditions["matchPrefixes"] = match_prefixes

        if whitelist is not None:
            string_conditions["whitelist"] = whitelist

        return jsii.sinvoke(cls, "stringFilter", [string_conditions])

    @property
    @jsii.member(jsii_name="conditions")
    def conditions(self) -> typing.List[typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "conditions")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _SubscriptionOptions(jsii.compat.TypedDict, total=False):
    filterPolicy: typing.Mapping[str,"SubscriptionFilter"]
    """The filter policy.

    Default:
        - all messages are delivered

    Stability:
        experimental
    """
    rawMessageDelivery: bool
    """true if raw message delivery is enabled for the subscription.

    Raw messages are free of JSON formatting and can be
    sent to HTTP/S and Amazon SQS endpoints. For more information, see GetSubscriptionAttributes in the Amazon Simple
    Notification Service API Reference.

    Default:
        false

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sns.SubscriptionOptions", jsii_struct_bases=[_SubscriptionOptions])
class SubscriptionOptions(_SubscriptionOptions):
    """Options for creating a new subscription.

    Stability:
        experimental
    """
    endpoint: str
    """The subscription endpoint.

    The meaning of this value depends on the value for 'protocol'.

    Stability:
        experimental
    """

    protocol: "SubscriptionProtocol"
    """What type of subscription to add.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sns.SubscriptionProps", jsii_struct_bases=[SubscriptionOptions])
class SubscriptionProps(SubscriptionOptions, jsii.compat.TypedDict):
    """Properties for creating a new subscription.

    Stability:
        experimental
    """
    topic: "ITopic"
    """The topic to subscribe to.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-sns.SubscriptionProtocol")
class SubscriptionProtocol(enum.Enum):
    """The type of subscription, controlling the type of the endpoint parameter.

    Stability:
        experimental
    """
    HTTP = "HTTP"
    """JSON-encoded message is POSTED to an HTTP url.

    Stability:
        experimental
    """
    HTTPS = "HTTPS"
    """JSON-encoded message is POSTed to an HTTPS url.

    Stability:
        experimental
    """
    EMAIL = "EMAIL"
    """Notifications are sent via email.

    Stability:
        experimental
    """
    EMAIL_JSON = "EMAIL_JSON"
    """Notifications are JSON-encoded and sent via mail.

    Stability:
        experimental
    """
    SMS = "SMS"
    """Notification is delivered by SMS.

    Stability:
        experimental
    """
    SQS = "SQS"
    """Notifications are enqueued into an SQS queue.

    Stability:
        experimental
    """
    APPLICATION = "APPLICATION"
    """JSON-encoded notifications are sent to a mobile app endpoint.

    Stability:
        experimental
    """
    LAMBDA = "LAMBDA"
    """Notifications trigger a Lambda function.

    Stability:
        experimental
    """

@jsii.implements(ITopic)
class TopicBase(aws_cdk.core.Resource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-sns.TopicBase"):
    """Either a new or imported Topic.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _TopicBaseProxy

    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, physical_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time

        Stability:
            experimental
        """
        props: aws_cdk.core.ResourceProps = {}

        if physical_name is not None:
            props["physicalName"] = physical_name

        jsii.create(TopicBase, self, [scope, id, props])

    @jsii.member(jsii_name="addSubscription")
    def add_subscription(self, subscription: "ITopicSubscription") -> None:
        """Subscribe some endpoint to this topic.

        Arguments:
            subscription: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addSubscription", [subscription])

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Adds a statement to the IAM resource policy associated with this topic.

        If this topic was created in this stack (``new Topic``), a topic policy
        will be automatically created upon the first call to ``addToPolicy``. If
        the topic is improted (``Topic.import``), then this is a no-op.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToResourcePolicy", [statement])

    @jsii.member(jsii_name="grantPublish")
    def grant_publish(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant topic publishing permissions to the given identity.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPublish", [grantee])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Topic.

        Arguments:
            metric_name: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricNumberOfMessagesPublished")
    def metric_number_of_messages_published(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages published to your Amazon SNS topics.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfMessagesPublished", [props])

    @jsii.member(jsii_name="metricNumberOfNotificationsDelivered")
    def metric_number_of_notifications_delivered(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages successfully delivered from your Amazon SNS topics to subscribing endpoints.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfNotificationsDelivered", [props])

    @jsii.member(jsii_name="metricNumberOfNotificationsFailed")
    def metric_number_of_notifications_failed(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that Amazon SNS failed to deliver.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfNotificationsFailed", [props])

    @jsii.member(jsii_name="metricNumberOfNotificationsFilteredOut")
    def metric_number_of_notifications_filtered_out(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that were rejected by subscription filter policies.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfNotificationsFilteredOut", [props])

    @jsii.member(jsii_name="metricNumberOfNotificationsFilteredOutInvalidAttributes")
    def metric_number_of_notifications_filtered_out_invalid_attributes(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that were rejected by subscription filter policies because the messages' attributes are invalid.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfNotificationsFilteredOutInvalidAttributes", [props])

    @jsii.member(jsii_name="metricNumberOfNotificationsFilteredOutNoMessageAttributes")
    def metric_number_of_notifications_filtered_out_no_message_attributes(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that were rejected by subscription filter policies because the messages have no attributes.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfNotificationsFilteredOutNoMessageAttributes", [props])

    @jsii.member(jsii_name="metricPublishSize")
    def metric_publish_size(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for the size of messages published through this topic.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricPublishSize", [props])

    @jsii.member(jsii_name="metricSMSMonthToDateSpentUSD")
    def metric_sms_month_to_date_spent_usd(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The charges you have accrued since the start of the current calendar month for sending SMS messages.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricSMSMonthToDateSpentUSD", [props])

    @jsii.member(jsii_name="metricSMSSuccessRate")
    def metric_sms_success_rate(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The rate of successful SMS message deliveries.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

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

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricSMSSuccessRate", [props])

    @property
    @jsii.member(jsii_name="autoCreatePolicy")
    @abc.abstractmethod
    def _auto_create_policy(self) -> bool:
        """Controls automatic creation of policy objects.

        Set by subclasses.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="topicArn")
    @abc.abstractmethod
    def topic_arn(self) -> str:
        """
        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="topicName")
    @abc.abstractmethod
    def topic_name(self) -> str:
        """
        Stability:
            experimental
        """
        ...


class _TopicBaseProxy(TopicBase, jsii.proxy_for(aws_cdk.core.Resource)):
    @property
    @jsii.member(jsii_name="autoCreatePolicy")
    def _auto_create_policy(self) -> bool:
        """Controls automatic creation of policy objects.

        Set by subclasses.

        Stability:
            experimental
        """
        return jsii.get(self, "autoCreatePolicy")

    @property
    @jsii.member(jsii_name="topicArn")
    def topic_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "topicArn")

    @property
    @jsii.member(jsii_name="topicName")
    def topic_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "topicName")


class Topic(TopicBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns.Topic"):
    """A new SNS topic.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, display_name: typing.Optional[str]=None, topic_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            display_name: A developer-defined string that can be used to identify this SNS topic. Default: None
            topic_name: A name for the topic. If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the topic name. For more information, see Name Type. Default: Generated name

        Stability:
            experimental
        """
        props: TopicProps = {}

        if display_name is not None:
            props["displayName"] = display_name

        if topic_name is not None:
            props["topicName"] = topic_name

        jsii.create(Topic, self, [scope, id, props])

    @jsii.member(jsii_name="fromTopicArn")
    @classmethod
    def from_topic_arn(cls, scope: aws_cdk.core.Construct, id: str, topic_arn: str) -> "ITopic":
        """
        Arguments:
            scope: -
            id: -
            topic_arn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromTopicArn", [scope, id, topic_arn])

    @property
    @jsii.member(jsii_name="autoCreatePolicy")
    def _auto_create_policy(self) -> bool:
        """Controls automatic creation of policy objects.

        Set by subclasses.

        Stability:
            experimental
        """
        return jsii.get(self, "autoCreatePolicy")

    @property
    @jsii.member(jsii_name="topicArn")
    def topic_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "topicArn")

    @property
    @jsii.member(jsii_name="topicName")
    def topic_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "topicName")


class TopicPolicy(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sns.TopicPolicy"):
    """Applies a policy to SNS topics.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, topics: typing.List["ITopic"]) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            topics: The set of topics this policy applies to.

        Stability:
            experimental
        """
        props: TopicPolicyProps = {"topics": topics}

        jsii.create(TopicPolicy, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="document")
    def document(self) -> aws_cdk.aws_iam.PolicyDocument:
        """The IAM policy document for this policy.

        Stability:
            experimental
        """
        return jsii.get(self, "document")


@jsii.data_type(jsii_type="@aws-cdk/aws-sns.TopicPolicyProps", jsii_struct_bases=[])
class TopicPolicyProps(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    topics: typing.List["ITopic"]
    """The set of topics this policy applies to.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sns.TopicProps", jsii_struct_bases=[])
class TopicProps(jsii.compat.TypedDict, total=False):
    """Properties for a new SNS topic.

    Stability:
        experimental
    """
    displayName: str
    """A developer-defined string that can be used to identify this SNS topic.

    Default:
        None

    Stability:
        experimental
    """

    topicName: str
    """A name for the topic.

    If you don't specify a name, AWS CloudFormation generates a unique
    physical ID and uses that ID for the topic name. For more information,
    see Name Type.

    Default:
        Generated name

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sns.TopicSubscriptionConfig", jsii_struct_bases=[SubscriptionOptions])
class TopicSubscriptionConfig(SubscriptionOptions, jsii.compat.TypedDict):
    """Subscription configuration.

    Stability:
        experimental
    """
    subscriberId: str
    """The id of the subscriber.

    Will be used as the id for the subscription in
    the topic's scope.

    Stability:
        experimental
    """

__all__ = ["BetweenCondition", "CfnSubscription", "CfnSubscriptionProps", "CfnTopic", "CfnTopicPolicy", "CfnTopicPolicyProps", "CfnTopicProps", "ITopic", "ITopicSubscription", "NumericConditions", "StringConditions", "Subscription", "SubscriptionFilter", "SubscriptionOptions", "SubscriptionProps", "SubscriptionProtocol", "Topic", "TopicBase", "TopicPolicy", "TopicPolicyProps", "TopicProps", "TopicSubscriptionConfig", "__jsii_assembly__"]

publication.publish()
