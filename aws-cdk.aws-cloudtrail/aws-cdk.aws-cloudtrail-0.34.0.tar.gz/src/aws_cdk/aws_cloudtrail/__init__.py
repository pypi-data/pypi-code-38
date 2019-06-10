import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_logs
import aws_cdk.aws_s3
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-cloudtrail", "0.34.0", __name__, "aws-cloudtrail@0.34.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-cloudtrail.AddS3EventSelectorOptions", jsii_struct_bases=[])
class AddS3EventSelectorOptions(jsii.compat.TypedDict, total=False):
    """Options for adding an S3 event selector.

    Stability:
        experimental
    """
    includeManagementEvents: bool
    """Specifies whether the event selector includes management events for the trail.

    Default:
        true

    Stability:
        experimental
    """

    readWriteType: "ReadWriteType"
    """Specifies whether to log read-only events, write-only events, or all events.

    Default:
        ReadWriteType.All

    Stability:
        experimental
    """

class CfnTrail(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudtrail.CfnTrail"):
    """A CloudFormation ``AWS::CloudTrail::Trail``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CloudTrail::Trail
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, is_logging: typing.Union[bool, aws_cdk.cdk.Token], s3_bucket_name: str, cloud_watch_logs_log_group_arn: typing.Optional[str]=None, cloud_watch_logs_role_arn: typing.Optional[str]=None, enable_log_file_validation: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, event_selectors: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "EventSelectorProperty"]]]]]=None, include_global_service_events: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, is_multi_region_trail: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, kms_key_id: typing.Optional[str]=None, s3_key_prefix: typing.Optional[str]=None, sns_topic_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, trail_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::CloudTrail::Trail``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            isLogging: ``AWS::CloudTrail::Trail.IsLogging``.
            s3BucketName: ``AWS::CloudTrail::Trail.S3BucketName``.
            cloudWatchLogsLogGroupArn: ``AWS::CloudTrail::Trail.CloudWatchLogsLogGroupArn``.
            cloudWatchLogsRoleArn: ``AWS::CloudTrail::Trail.CloudWatchLogsRoleArn``.
            enableLogFileValidation: ``AWS::CloudTrail::Trail.EnableLogFileValidation``.
            eventSelectors: ``AWS::CloudTrail::Trail.EventSelectors``.
            includeGlobalServiceEvents: ``AWS::CloudTrail::Trail.IncludeGlobalServiceEvents``.
            isMultiRegionTrail: ``AWS::CloudTrail::Trail.IsMultiRegionTrail``.
            kmsKeyId: ``AWS::CloudTrail::Trail.KMSKeyId``.
            s3KeyPrefix: ``AWS::CloudTrail::Trail.S3KeyPrefix``.
            snsTopicName: ``AWS::CloudTrail::Trail.SnsTopicName``.
            tags: ``AWS::CloudTrail::Trail.Tags``.
            trailName: ``AWS::CloudTrail::Trail.TrailName``.

        Stability:
            experimental
        """
        props: CfnTrailProps = {"isLogging": is_logging, "s3BucketName": s3_bucket_name}

        if cloud_watch_logs_log_group_arn is not None:
            props["cloudWatchLogsLogGroupArn"] = cloud_watch_logs_log_group_arn

        if cloud_watch_logs_role_arn is not None:
            props["cloudWatchLogsRoleArn"] = cloud_watch_logs_role_arn

        if enable_log_file_validation is not None:
            props["enableLogFileValidation"] = enable_log_file_validation

        if event_selectors is not None:
            props["eventSelectors"] = event_selectors

        if include_global_service_events is not None:
            props["includeGlobalServiceEvents"] = include_global_service_events

        if is_multi_region_trail is not None:
            props["isMultiRegionTrail"] = is_multi_region_trail

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

        if s3_key_prefix is not None:
            props["s3KeyPrefix"] = s3_key_prefix

        if sns_topic_name is not None:
            props["snsTopicName"] = sns_topic_name

        if tags is not None:
            props["tags"] = tags

        if trail_name is not None:
            props["trailName"] = trail_name

        jsii.create(CfnTrail, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnTrailProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

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

    @property
    @jsii.member(jsii_name="trailArn")
    def trail_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "trailArn")

    @property
    @jsii.member(jsii_name="trailName")
    def trail_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "trailName")

    @property
    @jsii.member(jsii_name="trailSnsTopicArn")
    def trail_sns_topic_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            SnsTopicArn
        """
        return jsii.get(self, "trailSnsTopicArn")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DataResourceProperty(jsii.compat.TypedDict, total=False):
        values: typing.List[str]
        """``CfnTrail.DataResourceProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudtrail-trail-dataresource.html#cfn-cloudtrail-trail-dataresource-values
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cloudtrail.CfnTrail.DataResourceProperty", jsii_struct_bases=[_DataResourceProperty])
    class DataResourceProperty(_DataResourceProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudtrail-trail-dataresource.html
        Stability:
            experimental
        """
        type: str
        """``CfnTrail.DataResourceProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudtrail-trail-dataresource.html#cfn-cloudtrail-trail-dataresource-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cloudtrail.CfnTrail.EventSelectorProperty", jsii_struct_bases=[])
    class EventSelectorProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudtrail-trail-eventselector.html
        Stability:
            experimental
        """
        dataResources: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTrail.DataResourceProperty"]]]
        """``CfnTrail.EventSelectorProperty.DataResources``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudtrail-trail-eventselector.html#cfn-cloudtrail-trail-eventselector-dataresources
        Stability:
            experimental
        """

        includeManagementEvents: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTrail.EventSelectorProperty.IncludeManagementEvents``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudtrail-trail-eventselector.html#cfn-cloudtrail-trail-eventselector-includemanagementevents
        Stability:
            experimental
        """

        readWriteType: str
        """``CfnTrail.EventSelectorProperty.ReadWriteType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudtrail-trail-eventselector.html#cfn-cloudtrail-trail-eventselector-readwritetype
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnTrailProps(jsii.compat.TypedDict, total=False):
    cloudWatchLogsLogGroupArn: str
    """``AWS::CloudTrail::Trail.CloudWatchLogsLogGroupArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-cloudwatchlogsloggrouparn
    Stability:
        experimental
    """
    cloudWatchLogsRoleArn: str
    """``AWS::CloudTrail::Trail.CloudWatchLogsRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-cloudwatchlogsrolearn
    Stability:
        experimental
    """
    enableLogFileValidation: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::CloudTrail::Trail.EnableLogFileValidation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-enablelogfilevalidation
    Stability:
        experimental
    """
    eventSelectors: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTrail.EventSelectorProperty"]]]
    """``AWS::CloudTrail::Trail.EventSelectors``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-eventselectors
    Stability:
        experimental
    """
    includeGlobalServiceEvents: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::CloudTrail::Trail.IncludeGlobalServiceEvents``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-includeglobalserviceevents
    Stability:
        experimental
    """
    isMultiRegionTrail: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::CloudTrail::Trail.IsMultiRegionTrail``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-ismultiregiontrail
    Stability:
        experimental
    """
    kmsKeyId: str
    """``AWS::CloudTrail::Trail.KMSKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-kmskeyid
    Stability:
        experimental
    """
    s3KeyPrefix: str
    """``AWS::CloudTrail::Trail.S3KeyPrefix``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-s3keyprefix
    Stability:
        experimental
    """
    snsTopicName: str
    """``AWS::CloudTrail::Trail.SnsTopicName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-snstopicname
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::CloudTrail::Trail.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-tags
    Stability:
        experimental
    """
    trailName: str
    """``AWS::CloudTrail::Trail.TrailName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-trailname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudtrail.CfnTrailProps", jsii_struct_bases=[_CfnTrailProps])
class CfnTrailProps(_CfnTrailProps):
    """Properties for defining a ``AWS::CloudTrail::Trail``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html
    Stability:
        experimental
    """
    isLogging: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::CloudTrail::Trail.IsLogging``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-islogging
    Stability:
        experimental
    """

    s3BucketName: str
    """``AWS::CloudTrail::Trail.S3BucketName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#cfn-cloudtrail-trail-s3bucketname
    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-cloudtrail.ReadWriteType")
class ReadWriteType(enum.Enum):
    """
    Stability:
        experimental
    """
    ReadOnly = "ReadOnly"
    """
    Stability:
        experimental
    """
    WriteOnly = "WriteOnly"
    """
    Stability:
        experimental
    """
    All = "All"
    """
    Stability:
        experimental
    """

class Trail(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudtrail.Trail"):
    """Cloud trail allows you to log events that happen in your AWS account For example:.

    import { CloudTrail } from '@aws-cdk/aws-cloudtrail'

    const cloudTrail = new CloudTrail(this, 'MyTrail');

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cloud_watch_logs_retention_time_days: typing.Optional[aws_cdk.aws_logs.RetentionDays]=None, enable_file_validation: typing.Optional[bool]=None, include_global_service_events: typing.Optional[bool]=None, is_multi_region_trail: typing.Optional[bool]=None, kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, management_events: typing.Optional["ReadWriteType"]=None, s3_key_prefix: typing.Optional[str]=None, send_to_cloud_watch_logs: typing.Optional[bool]=None, sns_topic: typing.Optional[str]=None, trail_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            cloudWatchLogsRetentionTimeDays: How long to retain logs in CloudWatchLogs. Ignored if sendToCloudWatchLogs is false Default: logs.RetentionDays.OneYear
            enableFileValidation: To determine whether a log file was modified, deleted, or unchanged after CloudTrail delivered it, you can use CloudTrail log file integrity validation. This feature is built using industry standard algorithms: SHA-256 for hashing and SHA-256 with RSA for digital signing. This makes it computationally infeasible to modify, delete or forge CloudTrail log files without detection. You can use the AWS CLI to validate the files in the location where CloudTrail delivered them. Default: true
            includeGlobalServiceEvents: For most services, events are recorded in the region where the action occurred. For global services such as AWS Identity and Access Management (IAM), AWS STS, Amazon CloudFront, and Route 53, events are delivered to any trail that includes global services, and are logged as occurring in US East (N. Virginia) Region. Default: true
            isMultiRegionTrail: Whether or not this trail delivers log files from multiple regions to a single S3 bucket for a single account. Default: true
            kmsKey: The AWS Key Management Service (AWS KMS) key ID that you want to use to encrypt CloudTrail logs. Default: - No encryption.
            managementEvents: When an event occurs in your account, CloudTrail evaluates whether the event matches the settings for your trails. Only events that match your trail settings are delivered to your Amazon S3 bucket and Amazon CloudWatch Logs log group. This method sets the management configuration for this trail. Management events provide insight into management operations that are performed on resources in your AWS account. These are also known as control plane operations. Management events can also include non-API events that occur in your account. For example, when a user logs in to your account, CloudTrail logs the ConsoleLogin event. Default: - Management events will not be logged.
            s3KeyPrefix: An Amazon S3 object key prefix that precedes the name of all log files. Default: - No prefix.
            sendToCloudWatchLogs: If CloudTrail pushes logs to CloudWatch Logs in addition to S3. Disabled for cost out of the box. Default: false
            snsTopic: The name of an Amazon SNS topic that is notified when new log files are published. Default: - No notifications.
            trailName: The name of the trail. We recoomend customers do not set an explicit name. Default: - AWS CloudFormation generated name.

        Stability:
            experimental
        """
        props: TrailProps = {}

        if cloud_watch_logs_retention_time_days is not None:
            props["cloudWatchLogsRetentionTimeDays"] = cloud_watch_logs_retention_time_days

        if enable_file_validation is not None:
            props["enableFileValidation"] = enable_file_validation

        if include_global_service_events is not None:
            props["includeGlobalServiceEvents"] = include_global_service_events

        if is_multi_region_trail is not None:
            props["isMultiRegionTrail"] = is_multi_region_trail

        if kms_key is not None:
            props["kmsKey"] = kms_key

        if management_events is not None:
            props["managementEvents"] = management_events

        if s3_key_prefix is not None:
            props["s3KeyPrefix"] = s3_key_prefix

        if send_to_cloud_watch_logs is not None:
            props["sendToCloudWatchLogs"] = send_to_cloud_watch_logs

        if sns_topic is not None:
            props["snsTopic"] = sns_topic

        if trail_name is not None:
            props["trailName"] = trail_name

        jsii.create(Trail, self, [scope, id, props])

    @jsii.member(jsii_name="addS3EventSelector")
    def add_s3_event_selector(self, prefixes: typing.List[str], *, include_management_events: typing.Optional[bool]=None, read_write_type: typing.Optional["ReadWriteType"]=None) -> None:
        """When an event occurs in your account, CloudTrail evaluates whether the event matches the settings for your trails. Only events that match your trail settings are delivered to your Amazon S3 bucket and Amazon CloudWatch Logs log group.

        This method adds an S3 Data Event Selector for filtering events that match S3 operations.

        Data events: These events provide insight into the resource operations performed on or within a resource.
        These are also known as data plane operations.

        Arguments:
            prefixes: the list of object ARN prefixes to include in logging (maximum 250 entries).
            options: the options to configure logging of management and data events.
            includeManagementEvents: Specifies whether the event selector includes management events for the trail. Default: true
            readWriteType: Specifies whether to log read-only events, write-only events, or all events. Default: ReadWriteType.All

        Stability:
            experimental
        """
        options: AddS3EventSelectorOptions = {}

        if include_management_events is not None:
            options["includeManagementEvents"] = include_management_events

        if read_write_type is not None:
            options["readWriteType"] = read_write_type

        return jsii.invoke(self, "addS3EventSelector", [prefixes, options])

    @jsii.member(jsii_name="onCloudTrailEvent")
    def on_cloud_trail_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Create an event rule for when an event is recorded by any Trail in the account.

        Note that the event doesn't necessarily have to come from this Trail, it can
        be captured from any one.

        Be sure to filter the event further down using an event pattern.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onCloudTrailEvent", [id, options])

    @property
    @jsii.member(jsii_name="trailArn")
    def trail_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "trailArn")

    @property
    @jsii.member(jsii_name="trailSnsTopicArn")
    def trail_sns_topic_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "trailSnsTopicArn")


@jsii.data_type(jsii_type="@aws-cdk/aws-cloudtrail.TrailProps", jsii_struct_bases=[])
class TrailProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    cloudWatchLogsRetentionTimeDays: aws_cdk.aws_logs.RetentionDays
    """How long to retain logs in CloudWatchLogs.

    Ignored if sendToCloudWatchLogs is false

    Default:
        logs.RetentionDays.OneYear

    Stability:
        experimental
    """

    enableFileValidation: bool
    """To determine whether a log file was modified, deleted, or unchanged after CloudTrail delivered it, you can use CloudTrail log file integrity validation. This feature is built using industry standard algorithms: SHA-256 for hashing and SHA-256 with RSA for digital signing. This makes it computationally infeasible to modify, delete or forge CloudTrail log files without detection. You can use the AWS CLI to validate the files in the location where CloudTrail delivered them.

    Default:
        true

    Stability:
        experimental
    """

    includeGlobalServiceEvents: bool
    """For most services, events are recorded in the region where the action occurred. For global services such as AWS Identity and Access Management (IAM), AWS STS, Amazon CloudFront, and Route 53, events are delivered to any trail that includes global services, and are logged as occurring in US East (N. Virginia) Region.

    Default:
        true

    Stability:
        experimental
    """

    isMultiRegionTrail: bool
    """Whether or not this trail delivers log files from multiple regions to a single S3 bucket for a single account.

    Default:
        true

    Stability:
        experimental
    """

    kmsKey: aws_cdk.aws_kms.IKey
    """The AWS Key Management Service (AWS KMS) key ID that you want to use to encrypt CloudTrail logs.

    Default:
        - No encryption.

    Stability:
        experimental
    """

    managementEvents: "ReadWriteType"
    """When an event occurs in your account, CloudTrail evaluates whether the event matches the settings for your trails. Only events that match your trail settings are delivered to your Amazon S3 bucket and Amazon CloudWatch Logs log group.

    This method sets the management configuration for this trail.

    Management events provide insight into management operations that are performed on resources in your AWS account.
    These are also known as control plane operations.
    Management events can also include non-API events that occur in your account.
    For example, when a user logs in to your account, CloudTrail logs the ConsoleLogin event.

    Default:
        - Management events will not be logged.

    Stability:
        experimental
    """

    s3KeyPrefix: str
    """An Amazon S3 object key prefix that precedes the name of all log files.

    Default:
        - No prefix.

    Stability:
        experimental
    """

    sendToCloudWatchLogs: bool
    """If CloudTrail pushes logs to CloudWatch Logs in addition to S3. Disabled for cost out of the box.

    Default:
        false

    Stability:
        experimental
    """

    snsTopic: str
    """The name of an Amazon SNS topic that is notified when new log files are published.

    Default:
        - No notifications.

    Stability:
        experimental
    """

    trailName: str
    """The name of the trail.

    We recoomend customers do not set an explicit name.

    Default:
        - AWS CloudFormation generated name.

    Stability:
        experimental
    """

__all__ = ["AddS3EventSelectorOptions", "CfnTrail", "CfnTrailProps", "ReadWriteType", "Trail", "TrailProps", "__jsii_assembly__"]

publication.publish()
