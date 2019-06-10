import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_cloudwatch
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-sqs", "0.34.0", __name__, "aws-sqs@0.34.0.jsii.tgz")
class CfnQueue(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sqs.CfnQueue"):
    """A CloudFormation ``AWS::SQS::Queue``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SQS::Queue
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, content_based_deduplication: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, delay_seconds: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, fifo_queue: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, kms_data_key_reuse_period_seconds: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, kms_master_key_id: typing.Optional[str]=None, maximum_message_size: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, message_retention_period: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, queue_name: typing.Optional[str]=None, receive_message_wait_time_seconds: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, redrive_policy: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, visibility_timeout: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::SQS::Queue``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            contentBasedDeduplication: ``AWS::SQS::Queue.ContentBasedDeduplication``.
            delaySeconds: ``AWS::SQS::Queue.DelaySeconds``.
            fifoQueue: ``AWS::SQS::Queue.FifoQueue``.
            kmsDataKeyReusePeriodSeconds: ``AWS::SQS::Queue.KmsDataKeyReusePeriodSeconds``.
            kmsMasterKeyId: ``AWS::SQS::Queue.KmsMasterKeyId``.
            maximumMessageSize: ``AWS::SQS::Queue.MaximumMessageSize``.
            messageRetentionPeriod: ``AWS::SQS::Queue.MessageRetentionPeriod``.
            queueName: ``AWS::SQS::Queue.QueueName``.
            receiveMessageWaitTimeSeconds: ``AWS::SQS::Queue.ReceiveMessageWaitTimeSeconds``.
            redrivePolicy: ``AWS::SQS::Queue.RedrivePolicy``.
            tags: ``AWS::SQS::Queue.Tags``.
            visibilityTimeout: ``AWS::SQS::Queue.VisibilityTimeout``.

        Stability:
            experimental
        """
        props: CfnQueueProps = {}

        if content_based_deduplication is not None:
            props["contentBasedDeduplication"] = content_based_deduplication

        if delay_seconds is not None:
            props["delaySeconds"] = delay_seconds

        if fifo_queue is not None:
            props["fifoQueue"] = fifo_queue

        if kms_data_key_reuse_period_seconds is not None:
            props["kmsDataKeyReusePeriodSeconds"] = kms_data_key_reuse_period_seconds

        if kms_master_key_id is not None:
            props["kmsMasterKeyId"] = kms_master_key_id

        if maximum_message_size is not None:
            props["maximumMessageSize"] = maximum_message_size

        if message_retention_period is not None:
            props["messageRetentionPeriod"] = message_retention_period

        if queue_name is not None:
            props["queueName"] = queue_name

        if receive_message_wait_time_seconds is not None:
            props["receiveMessageWaitTimeSeconds"] = receive_message_wait_time_seconds

        if redrive_policy is not None:
            props["redrivePolicy"] = redrive_policy

        if tags is not None:
            props["tags"] = tags

        if visibility_timeout is not None:
            props["visibilityTimeout"] = visibility_timeout

        jsii.create(CfnQueue, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnQueueProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="queueArn")
    def queue_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "queueArn")

    @property
    @jsii.member(jsii_name="queueName")
    def queue_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            QueueName
        """
        return jsii.get(self, "queueName")

    @property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "queueUrl")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """The ``TagManager`` handles setting, removing and formatting tags.

        Tags should be managed either passing them as properties during
        initiation or by calling methods on this object. If both techniques are
        used only the tags from the TagManager will be used. ``Tag`` (aspect)
        will use the manager.

        Stability:
            experimental
        """
        return jsii.get(self, "tags")


class CfnQueuePolicy(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sqs.CfnQueuePolicy"):
    """A CloudFormation ``AWS::SQS::QueuePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-policy.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SQS::QueuePolicy
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, policy_document: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token], queues: typing.List[str]) -> None:
        """Create a new ``AWS::SQS::QueuePolicy``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            policyDocument: ``AWS::SQS::QueuePolicy.PolicyDocument``.
            queues: ``AWS::SQS::QueuePolicy.Queues``.

        Stability:
            experimental
        """
        props: CfnQueuePolicyProps = {"policyDocument": policy_document, "queues": queues}

        jsii.create(CfnQueuePolicy, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnQueuePolicyProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-sqs.CfnQueuePolicyProps", jsii_struct_bases=[])
class CfnQueuePolicyProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::SQS::QueuePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-policy.html
    Stability:
        experimental
    """
    policyDocument: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::SQS::QueuePolicy.PolicyDocument``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-policy.html#cfn-sqs-queuepolicy-policydoc
    Stability:
        experimental
    """

    queues: typing.List[str]
    """``AWS::SQS::QueuePolicy.Queues``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-policy.html#cfn-sqs-queuepolicy-queues
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sqs.CfnQueueProps", jsii_struct_bases=[])
class CfnQueueProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::SQS::Queue``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html
    Stability:
        experimental
    """
    contentBasedDeduplication: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::SQS::Queue.ContentBasedDeduplication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-contentbaseddeduplication
    Stability:
        experimental
    """

    delaySeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::SQS::Queue.DelaySeconds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-delayseconds
    Stability:
        experimental
    """

    fifoQueue: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::SQS::Queue.FifoQueue``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-fifoqueue
    Stability:
        experimental
    """

    kmsDataKeyReusePeriodSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::SQS::Queue.KmsDataKeyReusePeriodSeconds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-kmsdatakeyreuseperiodseconds
    Stability:
        experimental
    """

    kmsMasterKeyId: str
    """``AWS::SQS::Queue.KmsMasterKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-kmsmasterkeyid
    Stability:
        experimental
    """

    maximumMessageSize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::SQS::Queue.MaximumMessageSize``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-maxmesgsize
    Stability:
        experimental
    """

    messageRetentionPeriod: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::SQS::Queue.MessageRetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-msgretentionperiod
    Stability:
        experimental
    """

    queueName: str
    """``AWS::SQS::Queue.QueueName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-name
    Stability:
        experimental
    """

    receiveMessageWaitTimeSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::SQS::Queue.ReceiveMessageWaitTimeSeconds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-receivemsgwaittime
    Stability:
        experimental
    """

    redrivePolicy: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::SQS::Queue.RedrivePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-redrive
    Stability:
        experimental
    """

    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::SQS::Queue.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#cfn-sqs-queue-tags
    Stability:
        experimental
    """

    visibilityTimeout: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::SQS::Queue.VisibilityTimeout``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-visiblitytimeout
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sqs.DeadLetterQueue", jsii_struct_bases=[])
class DeadLetterQueue(jsii.compat.TypedDict):
    """Dead letter queue settings.

    Stability:
        experimental
    """
    maxReceiveCount: jsii.Number
    """The number of times a message can be unsuccesfully dequeued before being moved to the dead-letter queue.

    Stability:
        experimental
    """

    queue: "IQueue"
    """The dead-letter queue to which Amazon SQS moves messages after the value of maxReceiveCount is exceeded.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-sqs.IQueue")
class IQueue(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IQueueProxy

    @property
    @jsii.member(jsii_name="queueArn")
    def queue_arn(self) -> str:
        """The ARN of this queue.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="queueName")
    def queue_name(self) -> str:
        """The name of this queue.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> str:
        """The URL of this queue.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="encryptionMasterKey")
    def encryption_master_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """If this queue is server-side encrypted, this is the KMS encryption key.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Adds a statement to the IAM resource policy associated with this queue.

        If this queue was created in this stack (``new Queue``), a queue policy
        will be automatically created upon the first call to ``addToPolicy``. If
        the queue is improted (``Queue.import``), then this is a no-op.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *queue_actions: str) -> aws_cdk.aws_iam.Grant:
        """Grant the actions defined in queueActions to the identity Principal given on this SQS queue resource.

        Arguments:
            grantee: Principal to grant right to.
            queueActions: The actions to grant.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantConsumeMessages")
    def grant_consume_messages(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant permissions to consume messages from a queue.

        This will grant the following permissions:

        - sqs:ChangeMessageVisibility
        - sqs:ChangeMessageVisibilityBatch
        - sqs:DeleteMessage
        - sqs:ReceiveMessage
        - sqs:DeleteMessageBatch
        - sqs:GetQueueAttributes
        - sqs:GetQueueUrl

        Arguments:
            grantee: Principal to grant consume rights to.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantPurge")
    def grant_purge(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant an IAM principal permissions to purge all messages from the queue.

        This will grant the following permissions:

        - sqs:PurgeQueue
        - sqs:GetQueueAttributes
        - sqs:GetQueueUrl

        Arguments:
            grantee: Principal to grant send rights to.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantSendMessages")
    def grant_send_messages(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant access to send messages to a queue to the given identity.

        This will grant the following permissions:

        - sqs:SendMessage
        - sqs:SendMessageBatch
        - sqs:GetQueueAttributes
        - sqs:GetQueueUrl

        Arguments:
            grantee: Principal to grant send rights to.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Queue.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricApproximateAgeOfOldestMessage")
    def metric_approximate_age_of_oldest_message(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The approximate age of the oldest non-deleted message in the queue.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricApproximateNumberOfMessagesDelayed")
    def metric_approximate_number_of_messages_delayed(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages in the queue that are delayed and not available for reading immediately.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricApproximateNumberOfMessagesNotVisible")
    def metric_approximate_number_of_messages_not_visible(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that are in flight.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricApproximateNumberOfMessagesVisible")
    def metric_approximate_number_of_messages_visible(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages available for retrieval from the queue.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricNumberOfEmptyReceives")
    def metric_number_of_empty_receives(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of ReceiveMessage API calls that did not return a message.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricNumberOfMessagesDeleted")
    def metric_number_of_messages_deleted(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages deleted from the queue.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricNumberOfMessagesReceived")
    def metric_number_of_messages_received(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages returned by calls to the ReceiveMessage action.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricNumberOfMessagesSent")
    def metric_number_of_messages_sent(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages added to a queue.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricSentMessageSize")
    def metric_sent_message_size(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The size of messages added to a queue.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...


class _IQueueProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-sqs.IQueue"
    @property
    @jsii.member(jsii_name="queueArn")
    def queue_arn(self) -> str:
        """The ARN of this queue.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "queueArn")

    @property
    @jsii.member(jsii_name="queueName")
    def queue_name(self) -> str:
        """The name of this queue.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "queueName")

    @property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> str:
        """The URL of this queue.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "queueUrl")

    @property
    @jsii.member(jsii_name="encryptionMasterKey")
    def encryption_master_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """If this queue is server-side encrypted, this is the KMS encryption key.

        Stability:
            experimental
        """
        return jsii.get(self, "encryptionMasterKey")

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Adds a statement to the IAM resource policy associated with this queue.

        If this queue was created in this stack (``new Queue``), a queue policy
        will be automatically created upon the first call to ``addToPolicy``. If
        the queue is improted (``Queue.import``), then this is a no-op.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToResourcePolicy", [statement])

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *queue_actions: str) -> aws_cdk.aws_iam.Grant:
        """Grant the actions defined in queueActions to the identity Principal given on this SQS queue resource.

        Arguments:
            grantee: Principal to grant right to.
            queueActions: The actions to grant.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grant", [grantee, *queue_actions])

    @jsii.member(jsii_name="grantConsumeMessages")
    def grant_consume_messages(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant permissions to consume messages from a queue.

        This will grant the following permissions:

        - sqs:ChangeMessageVisibility
        - sqs:ChangeMessageVisibilityBatch
        - sqs:DeleteMessage
        - sqs:ReceiveMessage
        - sqs:DeleteMessageBatch
        - sqs:GetQueueAttributes
        - sqs:GetQueueUrl

        Arguments:
            grantee: Principal to grant consume rights to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantConsumeMessages", [grantee])

    @jsii.member(jsii_name="grantPurge")
    def grant_purge(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant an IAM principal permissions to purge all messages from the queue.

        This will grant the following permissions:

        - sqs:PurgeQueue
        - sqs:GetQueueAttributes
        - sqs:GetQueueUrl

        Arguments:
            grantee: Principal to grant send rights to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPurge", [grantee])

    @jsii.member(jsii_name="grantSendMessages")
    def grant_send_messages(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant access to send messages to a queue to the given identity.

        This will grant the following permissions:

        - sqs:SendMessage
        - sqs:SendMessageBatch
        - sqs:GetQueueAttributes
        - sqs:GetQueueUrl

        Arguments:
            grantee: Principal to grant send rights to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantSendMessages", [grantee])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Queue.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricApproximateAgeOfOldestMessage")
    def metric_approximate_age_of_oldest_message(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The approximate age of the oldest non-deleted message in the queue.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricApproximateAgeOfOldestMessage", [props])

    @jsii.member(jsii_name="metricApproximateNumberOfMessagesDelayed")
    def metric_approximate_number_of_messages_delayed(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages in the queue that are delayed and not available for reading immediately.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricApproximateNumberOfMessagesDelayed", [props])

    @jsii.member(jsii_name="metricApproximateNumberOfMessagesNotVisible")
    def metric_approximate_number_of_messages_not_visible(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that are in flight.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricApproximateNumberOfMessagesNotVisible", [props])

    @jsii.member(jsii_name="metricApproximateNumberOfMessagesVisible")
    def metric_approximate_number_of_messages_visible(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages available for retrieval from the queue.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricApproximateNumberOfMessagesVisible", [props])

    @jsii.member(jsii_name="metricNumberOfEmptyReceives")
    def metric_number_of_empty_receives(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of ReceiveMessage API calls that did not return a message.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfEmptyReceives", [props])

    @jsii.member(jsii_name="metricNumberOfMessagesDeleted")
    def metric_number_of_messages_deleted(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages deleted from the queue.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfMessagesDeleted", [props])

    @jsii.member(jsii_name="metricNumberOfMessagesReceived")
    def metric_number_of_messages_received(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages returned by calls to the ReceiveMessage action.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfMessagesReceived", [props])

    @jsii.member(jsii_name="metricNumberOfMessagesSent")
    def metric_number_of_messages_sent(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages added to a queue.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfMessagesSent", [props])

    @jsii.member(jsii_name="metricSentMessageSize")
    def metric_sent_message_size(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The size of messages added to a queue.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricSentMessageSize", [props])


@jsii.data_type_optionals(jsii_struct_bases=[])
class _QueueAttributes(jsii.compat.TypedDict, total=False):
    keyArn: str
    """KMS encryption key, if this queue is server-side encrypted by a KMS key.

    Stability:
        experimental
    """
    queueName: str
    """The name of the queue.

    Default:
        if queue name is not specified, the name will be derived from the queue ARN

    Stability:
        experimental
    """
    queueUrl: str
    """The URL of the queue.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sqs.QueueAttributes", jsii_struct_bases=[_QueueAttributes])
class QueueAttributes(_QueueAttributes):
    """Reference to a queue.

    Stability:
        experimental
    """
    queueArn: str
    """The ARN of the queue.

    Stability:
        experimental
    """

@jsii.implements(IQueue)
class QueueBase(aws_cdk.cdk.Resource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-sqs.QueueBase"):
    """Reference to a new or existing Amazon SQS queue.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _QueueBaseProxy

    def __init__(self, scope: aws_cdk.cdk.Construct, id: str) -> None:
        """Creates a new construct node.

        Arguments:
            scope: The scope in which to define this construct.
            id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.

        Stability:
            experimental
        """
        jsii.create(QueueBase, self, [scope, id])

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Adds a statement to the IAM resource policy associated with this queue.

        If this queue was created in this stack (``new Queue``), a queue policy
        will be automatically created upon the first call to ``addToPolicy``. If
        the queue is improted (``Queue.import``), then this is a no-op.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToResourcePolicy", [statement])

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *actions: str) -> aws_cdk.aws_iam.Grant:
        """Grant the actions defined in queueActions to the identity Principal given on this SQS queue resource.

        Arguments:
            grantee: Principal to grant right to.
            actions: The actions to grant.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grant", [grantee, *actions])

    @jsii.member(jsii_name="grantConsumeMessages")
    def grant_consume_messages(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant permissions to consume messages from a queue.

        This will grant the following permissions:

        - sqs:ChangeMessageVisibility
        - sqs:ChangeMessageVisibilityBatch
        - sqs:DeleteMessage
        - sqs:ReceiveMessage
        - sqs:DeleteMessageBatch
        - sqs:GetQueueAttributes
        - sqs:GetQueueUrl

        Arguments:
            grantee: Principal to grant consume rights to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantConsumeMessages", [grantee])

    @jsii.member(jsii_name="grantPurge")
    def grant_purge(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant an IAM principal permissions to purge all messages from the queue.

        This will grant the following permissions:

        - sqs:PurgeQueue
        - sqs:GetQueueAttributes
        - sqs:GetQueueUrl

        Arguments:
            grantee: Principal to grant send rights to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPurge", [grantee])

    @jsii.member(jsii_name="grantSendMessages")
    def grant_send_messages(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant access to send messages to a queue to the given identity.

        This will grant the following permissions:

        - sqs:SendMessage
        - sqs:SendMessageBatch
        - sqs:GetQueueAttributes
        - sqs:GetQueueUrl

        Arguments:
            grantee: Principal to grant send rights to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantSendMessages", [grantee])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Queue.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricApproximateAgeOfOldestMessage")
    def metric_approximate_age_of_oldest_message(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The approximate age of the oldest non-deleted message in the queue.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricApproximateAgeOfOldestMessage", [props])

    @jsii.member(jsii_name="metricApproximateNumberOfMessagesDelayed")
    def metric_approximate_number_of_messages_delayed(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages in the queue that are delayed and not available for reading immediately.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricApproximateNumberOfMessagesDelayed", [props])

    @jsii.member(jsii_name="metricApproximateNumberOfMessagesNotVisible")
    def metric_approximate_number_of_messages_not_visible(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages that are in flight.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricApproximateNumberOfMessagesNotVisible", [props])

    @jsii.member(jsii_name="metricApproximateNumberOfMessagesVisible")
    def metric_approximate_number_of_messages_visible(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages available for retrieval from the queue.

        Maximum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricApproximateNumberOfMessagesVisible", [props])

    @jsii.member(jsii_name="metricNumberOfEmptyReceives")
    def metric_number_of_empty_receives(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of ReceiveMessage API calls that did not return a message.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfEmptyReceives", [props])

    @jsii.member(jsii_name="metricNumberOfMessagesDeleted")
    def metric_number_of_messages_deleted(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages deleted from the queue.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfMessagesDeleted", [props])

    @jsii.member(jsii_name="metricNumberOfMessagesReceived")
    def metric_number_of_messages_received(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages returned by calls to the ReceiveMessage action.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfMessagesReceived", [props])

    @jsii.member(jsii_name="metricNumberOfMessagesSent")
    def metric_number_of_messages_sent(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of messages added to a queue.

        Sum over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricNumberOfMessagesSent", [props])

    @jsii.member(jsii_name="metricSentMessageSize")
    def metric_sent_message_size(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The size of messages added to a queue.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricSentMessageSize", [props])

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
    @jsii.member(jsii_name="queueArn")
    @abc.abstractmethod
    def queue_arn(self) -> str:
        """The ARN of this queue.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="queueName")
    @abc.abstractmethod
    def queue_name(self) -> str:
        """The name of this queue.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="queueUrl")
    @abc.abstractmethod
    def queue_url(self) -> str:
        """The URL of this queue.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="encryptionMasterKey")
    @abc.abstractmethod
    def encryption_master_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """If this queue is server-side encrypted, this is the KMS encryption key.

        Stability:
            experimental
        """
        ...


class _QueueBaseProxy(QueueBase, jsii.proxy_for(aws_cdk.cdk.Resource)):
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
    @jsii.member(jsii_name="queueArn")
    def queue_arn(self) -> str:
        """The ARN of this queue.

        Stability:
            experimental
        """
        return jsii.get(self, "queueArn")

    @property
    @jsii.member(jsii_name="queueName")
    def queue_name(self) -> str:
        """The name of this queue.

        Stability:
            experimental
        """
        return jsii.get(self, "queueName")

    @property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> str:
        """The URL of this queue.

        Stability:
            experimental
        """
        return jsii.get(self, "queueUrl")

    @property
    @jsii.member(jsii_name="encryptionMasterKey")
    def encryption_master_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """If this queue is server-side encrypted, this is the KMS encryption key.

        Stability:
            experimental
        """
        return jsii.get(self, "encryptionMasterKey")


class Queue(QueueBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sqs.Queue"):
    """A new Amazon SQS queue.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, content_based_deduplication: typing.Optional[bool]=None, data_key_reuse_sec: typing.Optional[jsii.Number]=None, dead_letter_queue: typing.Optional["DeadLetterQueue"]=None, delivery_delay_sec: typing.Optional[jsii.Number]=None, encryption: typing.Optional["QueueEncryption"]=None, encryption_master_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, fifo: typing.Optional[bool]=None, max_message_size_bytes: typing.Optional[jsii.Number]=None, queue_name: typing.Optional[str]=None, receive_message_wait_time_sec: typing.Optional[jsii.Number]=None, retention_period_sec: typing.Optional[jsii.Number]=None, visibility_timeout_sec: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            contentBasedDeduplication: Specifies whether to enable content-based deduplication. During the deduplication interval (5 minutes), Amazon SQS treats messages that are sent with identical content (excluding attributes) as duplicates and delivers only one copy of the message. If you don't enable content-based deduplication and you want to deduplicate messages, provide an explicit deduplication ID in your SendMessage() call. (Only applies to FIFO queues.) Default: false
            dataKeyReuseSec: The length of time that Amazon SQS reuses a data key before calling KMS again. The value must be an integer between 60 (1 minute) and 86,400 (24 hours). The default is 300 (5 minutes). Default: 300 (5 minutes)
            deadLetterQueue: Send messages to this queue if they were unsuccessfully dequeued a number of times. Default: no dead-letter queue
            deliveryDelaySec: The time in seconds that the delivery of all messages in the queue is delayed. You can specify an integer value of 0 to 900 (15 minutes). The default value is 0. Default: 0
            encryption: Whether the contents of the queue are encrypted, and by what type of key. Be aware that encryption is not available in all regions, please see the docs for current availability details. Default: Unencrypted
            encryptionMasterKey: External KMS master key to use for queue encryption. Individual messages will be encrypted using data keys. The data keys in turn will be encrypted using this key, and reused for a maximum of ``dataKeyReuseSecs`` seconds. The 'encryption' property must be either not specified or set to "Kms". An error will be emitted if encryption is set to "Unencrypted" or "KmsManaged". Default: If encryption is set to KMS and not specified, a key will be created.
            fifo: Whether this a first-in-first-out (FIFO) queue. Default: false, unless queueName ends in '.fifo' or 'contentBasedDeduplication' is true.
            maxMessageSizeBytes: The limit of how many bytes that a message can contain before Amazon SQS rejects it. You can specify an integer value from 1024 bytes (1 KiB) to 262144 bytes (256 KiB). The default value is 262144 (256 KiB). Default: 256KiB
            queueName: A name for the queue. If specified and this is a FIFO queue, must end in the string '.fifo'. Default: CloudFormation-generated name
            receiveMessageWaitTimeSec: Default wait time for ReceiveMessage calls. Does not wait if set to 0, otherwise waits this amount of seconds by default for messages to arrive. For more information, see Amazon SQS Long Poll. Default: 0
            retentionPeriodSec: The number of seconds that Amazon SQS retains a message. You can specify an integer value from 60 seconds (1 minute) to 1209600 seconds (14 days). The default value is 345600 seconds (4 days). Default: 345600 seconds (4 days)
            visibilityTimeoutSec: Timeout of processing a single message. After dequeuing, the processor has this much time to handle the message and delete it from the queue before it becomes visible again for dequeueing by another processor. Values must be from 0 to 43200 seconds (12 hours). If you don't specify a value, AWS CloudFormation uses the default value of 30 seconds. Default: 30

        Stability:
            experimental
        """
        props: QueueProps = {}

        if content_based_deduplication is not None:
            props["contentBasedDeduplication"] = content_based_deduplication

        if data_key_reuse_sec is not None:
            props["dataKeyReuseSec"] = data_key_reuse_sec

        if dead_letter_queue is not None:
            props["deadLetterQueue"] = dead_letter_queue

        if delivery_delay_sec is not None:
            props["deliveryDelaySec"] = delivery_delay_sec

        if encryption is not None:
            props["encryption"] = encryption

        if encryption_master_key is not None:
            props["encryptionMasterKey"] = encryption_master_key

        if fifo is not None:
            props["fifo"] = fifo

        if max_message_size_bytes is not None:
            props["maxMessageSizeBytes"] = max_message_size_bytes

        if queue_name is not None:
            props["queueName"] = queue_name

        if receive_message_wait_time_sec is not None:
            props["receiveMessageWaitTimeSec"] = receive_message_wait_time_sec

        if retention_period_sec is not None:
            props["retentionPeriodSec"] = retention_period_sec

        if visibility_timeout_sec is not None:
            props["visibilityTimeoutSec"] = visibility_timeout_sec

        jsii.create(Queue, self, [scope, id, props])

    @jsii.member(jsii_name="fromQueueArn")
    @classmethod
    def from_queue_arn(cls, scope: aws_cdk.cdk.Construct, id: str, queue_arn: str) -> "IQueue":
        """
        Arguments:
            scope: -
            id: -
            queueArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromQueueArn", [scope, id, queue_arn])

    @jsii.member(jsii_name="fromQueueAttributes")
    @classmethod
    def from_queue_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, queue_arn: str, key_arn: typing.Optional[str]=None, queue_name: typing.Optional[str]=None, queue_url: typing.Optional[str]=None) -> "IQueue":
        """Import an existing queue.

        Arguments:
            scope: -
            id: -
            attrs: -
            queueArn: The ARN of the queue.
            keyArn: KMS encryption key, if this queue is server-side encrypted by a KMS key.
            queueName: The name of the queue. Default: if queue name is not specified, the name will be derived from the queue ARN
            queueUrl: The URL of the queue.

        Stability:
            experimental
        """
        attrs: QueueAttributes = {"queueArn": queue_arn}

        if key_arn is not None:
            attrs["keyArn"] = key_arn

        if queue_name is not None:
            attrs["queueName"] = queue_name

        if queue_url is not None:
            attrs["queueUrl"] = queue_url

        return jsii.sinvoke(cls, "fromQueueAttributes", [scope, id, attrs])

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
    @jsii.member(jsii_name="queueArn")
    def queue_arn(self) -> str:
        """The ARN of this queue.

        Stability:
            experimental
        """
        return jsii.get(self, "queueArn")

    @property
    @jsii.member(jsii_name="queueName")
    def queue_name(self) -> str:
        """The name of this queue.

        Stability:
            experimental
        """
        return jsii.get(self, "queueName")

    @property
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> str:
        """The URL of this queue.

        Stability:
            experimental
        """
        return jsii.get(self, "queueUrl")

    @property
    @jsii.member(jsii_name="encryptionMasterKey")
    def encryption_master_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """If this queue is encrypted, this is the KMS key.

        Stability:
            experimental
        """
        return jsii.get(self, "encryptionMasterKey")


@jsii.enum(jsii_type="@aws-cdk/aws-sqs.QueueEncryption")
class QueueEncryption(enum.Enum):
    """What kind of encryption to apply to this queue.

    Stability:
        experimental
    """
    Unencrypted = "Unencrypted"
    """Messages in the queue are not encrypted.

    Stability:
        experimental
    """
    KmsManaged = "KmsManaged"
    """Server-side KMS encryption with a master key managed by SQS.

    Stability:
        experimental
    """
    Kms = "Kms"
    """Server-side encryption with a KMS key managed by the user.

    If ``encryptionKey`` is specified, this key will be used, otherwise, one will be defined.

    Stability:
        experimental
    """

class QueuePolicy(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-sqs.QueuePolicy"):
    """Applies a policy to SQS queues.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, queues: typing.List["IQueue"]) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            queues: The set of queues this policy applies to.

        Stability:
            experimental
        """
        props: QueuePolicyProps = {"queues": queues}

        jsii.create(QueuePolicy, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="document")
    def document(self) -> aws_cdk.aws_iam.PolicyDocument:
        """The IAM policy document for this policy.

        Stability:
            experimental
        """
        return jsii.get(self, "document")


@jsii.data_type(jsii_type="@aws-cdk/aws-sqs.QueuePolicyProps", jsii_struct_bases=[])
class QueuePolicyProps(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    queues: typing.List["IQueue"]
    """The set of queues this policy applies to.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-sqs.QueueProps", jsii_struct_bases=[])
class QueueProps(jsii.compat.TypedDict, total=False):
    """Properties for creating a new Queue.

    Stability:
        experimental
    """
    contentBasedDeduplication: bool
    """Specifies whether to enable content-based deduplication.

    During the deduplication interval (5 minutes), Amazon SQS treats
    messages that are sent with identical content (excluding attributes) as
    duplicates and delivers only one copy of the message.

    If you don't enable content-based deduplication and you want to deduplicate
    messages, provide an explicit deduplication ID in your SendMessage() call.

    (Only applies to FIFO queues.)

    Default:
        false

    Stability:
        experimental
    """

    dataKeyReuseSec: jsii.Number
    """The length of time that Amazon SQS reuses a data key before calling KMS again.

    The value must be an integer between 60 (1 minute) and 86,400 (24
    hours). The default is 300 (5 minutes).

    Default:
        300 (5 minutes)

    Stability:
        experimental
    """

    deadLetterQueue: "DeadLetterQueue"
    """Send messages to this queue if they were unsuccessfully dequeued a number of times.

    Default:
        no dead-letter queue

    Stability:
        experimental
    """

    deliveryDelaySec: jsii.Number
    """The time in seconds that the delivery of all messages in the queue is delayed.

    You can specify an integer value of 0 to 900 (15 minutes). The default
    value is 0.

    Default:
        0

    Stability:
        experimental
    """

    encryption: "QueueEncryption"
    """Whether the contents of the queue are encrypted, and by what type of key.

    Be aware that encryption is not available in all regions, please see the docs
    for current availability details.

    Default:
        Unencrypted

    Stability:
        experimental
    """

    encryptionMasterKey: aws_cdk.aws_kms.IKey
    """External KMS master key to use for queue encryption.

    Individual messages will be encrypted using data keys. The data keys in
    turn will be encrypted using this key, and reused for a maximum of
    ``dataKeyReuseSecs`` seconds.

    The 'encryption' property must be either not specified or set to "Kms".
    An error will be emitted if encryption is set to "Unencrypted" or
    "KmsManaged".

    Default:
        If encryption is set to KMS and not specified, a key will be created.

    Stability:
        experimental
    """

    fifo: bool
    """Whether this a first-in-first-out (FIFO) queue.

    Default:
        false, unless queueName ends in '.fifo' or 'contentBasedDeduplication' is true.

    Stability:
        experimental
    """

    maxMessageSizeBytes: jsii.Number
    """The limit of how many bytes that a message can contain before Amazon SQS rejects it.

    You can specify an integer value from 1024 bytes (1 KiB) to 262144 bytes
    (256 KiB). The default value is 262144 (256 KiB).

    Default:
        256KiB

    Stability:
        experimental
    """

    queueName: str
    """A name for the queue.

    If specified and this is a FIFO queue, must end in the string '.fifo'.

    Default:
        CloudFormation-generated name

    Stability:
        experimental
    """

    receiveMessageWaitTimeSec: jsii.Number
    """Default wait time for ReceiveMessage calls.

    Does not wait if set to 0, otherwise waits this amount of seconds
    by default for messages to arrive.

    For more information, see Amazon SQS Long Poll.

    Default:
        0

    Stability:
        experimental
    """

    retentionPeriodSec: jsii.Number
    """The number of seconds that Amazon SQS retains a message.

    You can specify an integer value from 60 seconds (1 minute) to 1209600
    seconds (14 days). The default value is 345600 seconds (4 days).

    Default:
        345600 seconds (4 days)

    Stability:
        experimental
    """

    visibilityTimeoutSec: jsii.Number
    """Timeout of processing a single message.

    After dequeuing, the processor has this much time to handle the message
    and delete it from the queue before it becomes visible again for dequeueing
    by another processor.

    Values must be from 0 to 43200 seconds (12 hours). If you don't specify
    a value, AWS CloudFormation uses the default value of 30 seconds.

    Default:
        30

    Stability:
        experimental
    """

__all__ = ["CfnQueue", "CfnQueuePolicy", "CfnQueuePolicyProps", "CfnQueueProps", "DeadLetterQueue", "IQueue", "Queue", "QueueAttributes", "QueueBase", "QueueEncryption", "QueuePolicy", "QueuePolicyProps", "QueueProps", "__jsii_assembly__"]

publication.publish()
