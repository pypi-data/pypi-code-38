import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-kinesisfirehose", "0.34.0", __name__, "aws-kinesisfirehose@0.34.0.jsii.tgz")
class CfnDeliveryStream(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream"):
    """A CloudFormation ``AWS::KinesisFirehose::DeliveryStream``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html
    Stability:
        experimental
    cloudformationResource:
        AWS::KinesisFirehose::DeliveryStream
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, delivery_stream_name: typing.Optional[str]=None, delivery_stream_type: typing.Optional[str]=None, elasticsearch_destination_configuration: typing.Optional[typing.Union[typing.Optional["ElasticsearchDestinationConfigurationProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None, extended_s3_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ExtendedS3DestinationConfigurationProperty"]]]=None, kinesis_stream_source_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["KinesisStreamSourceConfigurationProperty"]]]=None, redshift_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["RedshiftDestinationConfigurationProperty"]]]=None, s3_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["S3DestinationConfigurationProperty"]]]=None, splunk_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["SplunkDestinationConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::KinesisFirehose::DeliveryStream``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            deliveryStreamName: ``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamName``.
            deliveryStreamType: ``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamType``.
            elasticsearchDestinationConfiguration: ``AWS::KinesisFirehose::DeliveryStream.ElasticsearchDestinationConfiguration``.
            extendedS3DestinationConfiguration: ``AWS::KinesisFirehose::DeliveryStream.ExtendedS3DestinationConfiguration``.
            kinesisStreamSourceConfiguration: ``AWS::KinesisFirehose::DeliveryStream.KinesisStreamSourceConfiguration``.
            redshiftDestinationConfiguration: ``AWS::KinesisFirehose::DeliveryStream.RedshiftDestinationConfiguration``.
            s3DestinationConfiguration: ``AWS::KinesisFirehose::DeliveryStream.S3DestinationConfiguration``.
            splunkDestinationConfiguration: ``AWS::KinesisFirehose::DeliveryStream.SplunkDestinationConfiguration``.

        Stability:
            experimental
        """
        props: CfnDeliveryStreamProps = {}

        if delivery_stream_name is not None:
            props["deliveryStreamName"] = delivery_stream_name

        if delivery_stream_type is not None:
            props["deliveryStreamType"] = delivery_stream_type

        if elasticsearch_destination_configuration is not None:
            props["elasticsearchDestinationConfiguration"] = elasticsearch_destination_configuration

        if extended_s3_destination_configuration is not None:
            props["extendedS3DestinationConfiguration"] = extended_s3_destination_configuration

        if kinesis_stream_source_configuration is not None:
            props["kinesisStreamSourceConfiguration"] = kinesis_stream_source_configuration

        if redshift_destination_configuration is not None:
            props["redshiftDestinationConfiguration"] = redshift_destination_configuration

        if s3_destination_configuration is not None:
            props["s3DestinationConfiguration"] = s3_destination_configuration

        if splunk_destination_configuration is not None:
            props["splunkDestinationConfiguration"] = splunk_destination_configuration

        jsii.create(CfnDeliveryStream, self, [scope, id, props])

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
    @jsii.member(jsii_name="deliveryStreamArn")
    def delivery_stream_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "deliveryStreamArn")

    @property
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deliveryStreamName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDeliveryStreamProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty", jsii_struct_bases=[])
    class BufferingHintsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html
        Stability:
            experimental
        """
        intervalInSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeliveryStream.BufferingHintsProperty.IntervalInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html#cfn-kinesisfirehose-deliverystream-bufferinghints-intervalinseconds
        Stability:
            experimental
        """

        sizeInMBs: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeliveryStream.BufferingHintsProperty.SizeInMBs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html#cfn-kinesisfirehose-deliverystream-bufferinghints-sizeinmbs
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty", jsii_struct_bases=[])
    class CloudWatchLoggingOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeliveryStream.CloudWatchLoggingOptionsProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html#cfn-kinesisfirehose-deliverystream-cloudwatchloggingoptions-enabled
        Stability:
            experimental
        """

        logGroupName: str
        """``CfnDeliveryStream.CloudWatchLoggingOptionsProperty.LogGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html#cfn-kinesisfirehose-deliverystream-cloudwatchloggingoptions-loggroupname
        Stability:
            experimental
        """

        logStreamName: str
        """``CfnDeliveryStream.CloudWatchLoggingOptionsProperty.LogStreamName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html#cfn-kinesisfirehose-deliverystream-cloudwatchloggingoptions-logstreamname
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CopyCommandProperty(jsii.compat.TypedDict, total=False):
        copyOptions: str
        """``CfnDeliveryStream.CopyCommandProperty.CopyOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html#cfn-kinesisfirehose-deliverystream-copycommand-copyoptions
        Stability:
            experimental
        """
        dataTableColumns: str
        """``CfnDeliveryStream.CopyCommandProperty.DataTableColumns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html#cfn-kinesisfirehose-deliverystream-copycommand-datatablecolumns
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.CopyCommandProperty", jsii_struct_bases=[_CopyCommandProperty])
    class CopyCommandProperty(_CopyCommandProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html
        Stability:
            experimental
        """
        dataTableName: str
        """``CfnDeliveryStream.CopyCommandProperty.DataTableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html#cfn-kinesisfirehose-deliverystream-copycommand-datatablename
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ElasticsearchBufferingHintsProperty", jsii_struct_bases=[])
    class ElasticsearchBufferingHintsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html
        Stability:
            experimental
        """
        intervalInSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeliveryStream.ElasticsearchBufferingHintsProperty.IntervalInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html#cfn-kinesisfirehose-deliverystream-elasticsearchbufferinghints-intervalinseconds
        Stability:
            experimental
        """

        sizeInMBs: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeliveryStream.ElasticsearchBufferingHintsProperty.SizeInMBs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html#cfn-kinesisfirehose-deliverystream-elasticsearchbufferinghints-sizeinmbs
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ElasticsearchDestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchLoggingOptions: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-cloudwatchloggingoptions
        Stability:
            experimental
        """
        processingConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.ProcessingConfigurationProperty"]
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.ProcessingConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-processingconfiguration
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty", jsii_struct_bases=[_ElasticsearchDestinationConfigurationProperty])
    class ElasticsearchDestinationConfigurationProperty(_ElasticsearchDestinationConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html
        Stability:
            experimental
        """
        bufferingHints: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.ElasticsearchBufferingHintsProperty"]
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.BufferingHints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-bufferinghints
        Stability:
            experimental
        """

        domainArn: str
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.DomainARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-domainarn
        Stability:
            experimental
        """

        indexName: str
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.IndexName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-indexname
        Stability:
            experimental
        """

        indexRotationPeriod: str
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.IndexRotationPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-indexrotationperiod
        Stability:
            experimental
        """

        retryOptions: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.ElasticsearchRetryOptionsProperty"]
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.RetryOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-retryoptions
        Stability:
            experimental
        """

        roleArn: str
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-rolearn
        Stability:
            experimental
        """

        s3BackupMode: str
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.S3BackupMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-s3backupmode
        Stability:
            experimental
        """

        s3Configuration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.S3Configuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-s3configuration
        Stability:
            experimental
        """

        typeName: str
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.TypeName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-typename
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ElasticsearchRetryOptionsProperty", jsii_struct_bases=[])
    class ElasticsearchRetryOptionsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchretryoptions.html
        Stability:
            experimental
        """
        durationInSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeliveryStream.ElasticsearchRetryOptionsProperty.DurationInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchretryoptions.html#cfn-kinesisfirehose-deliverystream-elasticsearchretryoptions-durationinseconds
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty", jsii_struct_bases=[])
    class EncryptionConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-encryptionconfiguration.html
        Stability:
            experimental
        """
        kmsEncryptionConfig: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.KMSEncryptionConfigProperty"]
        """``CfnDeliveryStream.EncryptionConfigurationProperty.KMSEncryptionConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-encryptionconfiguration.html#cfn-kinesisfirehose-deliverystream-encryptionconfiguration-kmsencryptionconfig
        Stability:
            experimental
        """

        noEncryptionConfig: str
        """``CfnDeliveryStream.EncryptionConfigurationProperty.NoEncryptionConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-encryptionconfiguration.html#cfn-kinesisfirehose-deliverystream-encryptionconfiguration-noencryptionconfig
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ExtendedS3DestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchLoggingOptions: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-cloudwatchloggingoptions
        Stability:
            experimental
        """
        encryptionConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.EncryptionConfigurationProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.EncryptionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-encryptionconfiguration
        Stability:
            experimental
        """
        processingConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.ProcessingConfigurationProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.ProcessingConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-processingconfiguration
        Stability:
            experimental
        """
        s3BackupConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.S3BackupConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-s3backupconfiguration
        Stability:
            experimental
        """
        s3BackupMode: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.S3BackupMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-s3backupmode
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty", jsii_struct_bases=[_ExtendedS3DestinationConfigurationProperty])
    class ExtendedS3DestinationConfigurationProperty(_ExtendedS3DestinationConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html
        Stability:
            experimental
        """
        bucketArn: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.BucketARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-bucketarn
        Stability:
            experimental
        """

        bufferingHints: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.BufferingHintsProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.BufferingHints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-bufferinghints
        Stability:
            experimental
        """

        compressionFormat: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.CompressionFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-compressionformat
        Stability:
            experimental
        """

        prefix: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-prefix
        Stability:
            experimental
        """

        roleArn: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-rolearn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty", jsii_struct_bases=[])
    class KMSEncryptionConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kmsencryptionconfig.html
        Stability:
            experimental
        """
        awskmsKeyArn: str
        """``CfnDeliveryStream.KMSEncryptionConfigProperty.AWSKMSKeyARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kmsencryptionconfig.html#cfn-kinesisfirehose-deliverystream-kmsencryptionconfig-awskmskeyarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.KinesisStreamSourceConfigurationProperty", jsii_struct_bases=[])
    class KinesisStreamSourceConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html
        Stability:
            experimental
        """
        kinesisStreamArn: str
        """``CfnDeliveryStream.KinesisStreamSourceConfigurationProperty.KinesisStreamARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration-kinesisstreamarn
        Stability:
            experimental
        """

        roleArn: str
        """``CfnDeliveryStream.KinesisStreamSourceConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration-rolearn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty", jsii_struct_bases=[])
    class ProcessingConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeliveryStream.ProcessingConfigurationProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html#cfn-kinesisfirehose-deliverystream-processingconfiguration-enabled
        Stability:
            experimental
        """

        processors: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.ProcessorProperty"]]]
        """``CfnDeliveryStream.ProcessingConfigurationProperty.Processors``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html#cfn-kinesisfirehose-deliverystream-processingconfiguration-processors
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty", jsii_struct_bases=[])
    class ProcessorParameterProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html
        Stability:
            experimental
        """
        parameterName: str
        """``CfnDeliveryStream.ProcessorParameterProperty.ParameterName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html#cfn-kinesisfirehose-deliverystream-processorparameter-parametername
        Stability:
            experimental
        """

        parameterValue: str
        """``CfnDeliveryStream.ProcessorParameterProperty.ParameterValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html#cfn-kinesisfirehose-deliverystream-processorparameter-parametervalue
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ProcessorProperty", jsii_struct_bases=[])
    class ProcessorProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html
        Stability:
            experimental
        """
        parameters: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.ProcessorParameterProperty"]]]
        """``CfnDeliveryStream.ProcessorProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html#cfn-kinesisfirehose-deliverystream-processor-parameters
        Stability:
            experimental
        """

        type: str
        """``CfnDeliveryStream.ProcessorProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html#cfn-kinesisfirehose-deliverystream-processor-type
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _RedshiftDestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchLoggingOptions: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-cloudwatchloggingoptions
        Stability:
            experimental
        """
        processingConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.ProcessingConfigurationProperty"]
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.ProcessingConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-processingconfiguration
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.RedshiftDestinationConfigurationProperty", jsii_struct_bases=[_RedshiftDestinationConfigurationProperty])
    class RedshiftDestinationConfigurationProperty(_RedshiftDestinationConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html
        Stability:
            experimental
        """
        clusterJdbcurl: str
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.ClusterJDBCURL``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-clusterjdbcurl
        Stability:
            experimental
        """

        copyCommand: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.CopyCommandProperty"]
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.CopyCommand``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-copycommand
        Stability:
            experimental
        """

        password: str
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.Password``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-password
        Stability:
            experimental
        """

        roleArn: str
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-rolearn
        Stability:
            experimental
        """

        s3Configuration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.S3Configuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-s3configuration
        Stability:
            experimental
        """

        username: str
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.Username``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-username
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _S3DestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchLoggingOptions: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-cloudwatchloggingoptions
        Stability:
            experimental
        """
        encryptionConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.EncryptionConfigurationProperty"]
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.EncryptionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-encryptionconfiguration
        Stability:
            experimental
        """
        prefix: str
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-prefix
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty", jsii_struct_bases=[_S3DestinationConfigurationProperty])
    class S3DestinationConfigurationProperty(_S3DestinationConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html
        Stability:
            experimental
        """
        bucketArn: str
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.BucketARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-bucketarn
        Stability:
            experimental
        """

        bufferingHints: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.BufferingHintsProperty"]
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.BufferingHints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-bufferinghints
        Stability:
            experimental
        """

        compressionFormat: str
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.CompressionFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-compressionformat
        Stability:
            experimental
        """

        roleArn: str
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-rolearn
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SplunkDestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchLoggingOptions: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-cloudwatchloggingoptions
        Stability:
            experimental
        """
        hecAcknowledgmentTimeoutInSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECAcknowledgmentTimeoutInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecacknowledgmenttimeoutinseconds
        Stability:
            experimental
        """
        processingConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.ProcessingConfigurationProperty"]
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.ProcessingConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-processingconfiguration
        Stability:
            experimental
        """
        retryOptions: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.SplunkRetryOptionsProperty"]
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.RetryOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-retryoptions
        Stability:
            experimental
        """
        s3BackupMode: str
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.S3BackupMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-s3backupmode
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SplunkDestinationConfigurationProperty", jsii_struct_bases=[_SplunkDestinationConfigurationProperty])
    class SplunkDestinationConfigurationProperty(_SplunkDestinationConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html
        Stability:
            experimental
        """
        hecEndpoint: str
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECEndpoint``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecendpoint
        Stability:
            experimental
        """

        hecEndpointType: str
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECEndpointType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecendpointtype
        Stability:
            experimental
        """

        hecToken: str
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECToken``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hectoken
        Stability:
            experimental
        """

        s3Configuration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.S3Configuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-s3configuration
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SplunkRetryOptionsProperty", jsii_struct_bases=[])
    class SplunkRetryOptionsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkretryoptions.html
        Stability:
            experimental
        """
        durationInSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeliveryStream.SplunkRetryOptionsProperty.DurationInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkretryoptions.html#cfn-kinesisfirehose-deliverystream-splunkretryoptions-durationinseconds
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStreamProps", jsii_struct_bases=[])
class CfnDeliveryStreamProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::KinesisFirehose::DeliveryStream``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html
    Stability:
        experimental
    """
    deliveryStreamName: str
    """``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamname
    Stability:
        experimental
    """

    deliveryStreamType: str
    """``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamtype
    Stability:
        experimental
    """

    elasticsearchDestinationConfiguration: typing.Union["CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty", aws_cdk.cdk.Token]
    """``AWS::KinesisFirehose::DeliveryStream.ElasticsearchDestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration
    Stability:
        experimental
    """

    extendedS3DestinationConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.ExtendedS3DestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration
    Stability:
        experimental
    """

    kinesisStreamSourceConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.KinesisStreamSourceConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.KinesisStreamSourceConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration
    Stability:
        experimental
    """

    redshiftDestinationConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.RedshiftDestinationConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.RedshiftDestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration
    Stability:
        experimental
    """

    s3DestinationConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.S3DestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration
    Stability:
        experimental
    """

    splunkDestinationConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryStream.SplunkDestinationConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.SplunkDestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration
    Stability:
        experimental
    """

__all__ = ["CfnDeliveryStream", "CfnDeliveryStreamProps", "__jsii_assembly__"]

publication.publish()
