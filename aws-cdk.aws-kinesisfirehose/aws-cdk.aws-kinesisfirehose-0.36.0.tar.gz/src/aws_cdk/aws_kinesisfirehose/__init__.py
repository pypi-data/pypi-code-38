import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-kinesisfirehose", "0.36.0", __name__, "aws-kinesisfirehose@0.36.0.jsii.tgz")
class CfnDeliveryStream(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream"):
    """A CloudFormation ``AWS::KinesisFirehose::DeliveryStream``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html
    Stability:
        stable
    cloudformationResource:
        AWS::KinesisFirehose::DeliveryStream
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, delivery_stream_name: typing.Optional[str]=None, delivery_stream_type: typing.Optional[str]=None, elasticsearch_destination_configuration: typing.Optional[typing.Union[typing.Optional["ElasticsearchDestinationConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, extended_s3_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ExtendedS3DestinationConfigurationProperty"]]]=None, kinesis_stream_source_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["KinesisStreamSourceConfigurationProperty"]]]=None, redshift_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RedshiftDestinationConfigurationProperty"]]]=None, s3_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3DestinationConfigurationProperty"]]]=None, splunk_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SplunkDestinationConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::KinesisFirehose::DeliveryStream``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            delivery_stream_name: ``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamName``.
            delivery_stream_type: ``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamType``.
            elasticsearch_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.ElasticsearchDestinationConfiguration``.
            extended_s3_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.ExtendedS3DestinationConfiguration``.
            kinesis_stream_source_configuration: ``AWS::KinesisFirehose::DeliveryStream.KinesisStreamSourceConfiguration``.
            redshift_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.RedshiftDestinationConfiguration``.
            s3_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.S3DestinationConfiguration``.
            splunk_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.SplunkDestinationConfiguration``.

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> typing.Optional[str]:
        """``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamname
        Stability:
            stable
        """
        return jsii.get(self, "deliveryStreamName")

    @delivery_stream_name.setter
    def delivery_stream_name(self, value: typing.Optional[str]):
        return jsii.set(self, "deliveryStreamName", value)

    @property
    @jsii.member(jsii_name="deliveryStreamType")
    def delivery_stream_type(self) -> typing.Optional[str]:
        """``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamtype
        Stability:
            stable
        """
        return jsii.get(self, "deliveryStreamType")

    @delivery_stream_type.setter
    def delivery_stream_type(self, value: typing.Optional[str]):
        return jsii.set(self, "deliveryStreamType", value)

    @property
    @jsii.member(jsii_name="elasticsearchDestinationConfiguration")
    def elasticsearch_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional["ElasticsearchDestinationConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::KinesisFirehose::DeliveryStream.ElasticsearchDestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "elasticsearchDestinationConfiguration")

    @elasticsearch_destination_configuration.setter
    def elasticsearch_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional["ElasticsearchDestinationConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "elasticsearchDestinationConfiguration", value)

    @property
    @jsii.member(jsii_name="extendedS3DestinationConfiguration")
    def extended_s3_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ExtendedS3DestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.ExtendedS3DestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "extendedS3DestinationConfiguration")

    @extended_s3_destination_configuration.setter
    def extended_s3_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ExtendedS3DestinationConfigurationProperty"]]]):
        return jsii.set(self, "extendedS3DestinationConfiguration", value)

    @property
    @jsii.member(jsii_name="kinesisStreamSourceConfiguration")
    def kinesis_stream_source_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["KinesisStreamSourceConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.KinesisStreamSourceConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "kinesisStreamSourceConfiguration")

    @kinesis_stream_source_configuration.setter
    def kinesis_stream_source_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["KinesisStreamSourceConfigurationProperty"]]]):
        return jsii.set(self, "kinesisStreamSourceConfiguration", value)

    @property
    @jsii.member(jsii_name="redshiftDestinationConfiguration")
    def redshift_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RedshiftDestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.RedshiftDestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "redshiftDestinationConfiguration")

    @redshift_destination_configuration.setter
    def redshift_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RedshiftDestinationConfigurationProperty"]]]):
        return jsii.set(self, "redshiftDestinationConfiguration", value)

    @property
    @jsii.member(jsii_name="s3DestinationConfiguration")
    def s3_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3DestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.S3DestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "s3DestinationConfiguration")

    @s3_destination_configuration.setter
    def s3_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["S3DestinationConfigurationProperty"]]]):
        return jsii.set(self, "s3DestinationConfiguration", value)

    @property
    @jsii.member(jsii_name="splunkDestinationConfiguration")
    def splunk_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SplunkDestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.SplunkDestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "splunkDestinationConfiguration")

    @splunk_destination_configuration.setter
    def splunk_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SplunkDestinationConfigurationProperty"]]]):
        return jsii.set(self, "splunkDestinationConfiguration", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty", jsii_struct_bases=[])
    class BufferingHintsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html
        Stability:
            stable
        """
        intervalInSeconds: jsii.Number
        """``CfnDeliveryStream.BufferingHintsProperty.IntervalInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html#cfn-kinesisfirehose-deliverystream-bufferinghints-intervalinseconds
        Stability:
            stable
        """

        sizeInMBs: jsii.Number
        """``CfnDeliveryStream.BufferingHintsProperty.SizeInMBs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html#cfn-kinesisfirehose-deliverystream-bufferinghints-sizeinmbs
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty", jsii_struct_bases=[])
    class CloudWatchLoggingOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html
        Stability:
            stable
        """
        enabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDeliveryStream.CloudWatchLoggingOptionsProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html#cfn-kinesisfirehose-deliverystream-cloudwatchloggingoptions-enabled
        Stability:
            stable
        """

        logGroupName: str
        """``CfnDeliveryStream.CloudWatchLoggingOptionsProperty.LogGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html#cfn-kinesisfirehose-deliverystream-cloudwatchloggingoptions-loggroupname
        Stability:
            stable
        """

        logStreamName: str
        """``CfnDeliveryStream.CloudWatchLoggingOptionsProperty.LogStreamName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html#cfn-kinesisfirehose-deliverystream-cloudwatchloggingoptions-logstreamname
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CopyCommandProperty(jsii.compat.TypedDict, total=False):
        copyOptions: str
        """``CfnDeliveryStream.CopyCommandProperty.CopyOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html#cfn-kinesisfirehose-deliverystream-copycommand-copyoptions
        Stability:
            stable
        """
        dataTableColumns: str
        """``CfnDeliveryStream.CopyCommandProperty.DataTableColumns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html#cfn-kinesisfirehose-deliverystream-copycommand-datatablecolumns
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.CopyCommandProperty", jsii_struct_bases=[_CopyCommandProperty])
    class CopyCommandProperty(_CopyCommandProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html
        Stability:
            stable
        """
        dataTableName: str
        """``CfnDeliveryStream.CopyCommandProperty.DataTableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html#cfn-kinesisfirehose-deliverystream-copycommand-datatablename
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.DataFormatConversionConfigurationProperty", jsii_struct_bases=[])
    class DataFormatConversionConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html
        Stability:
            stable
        """
        enabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDeliveryStream.DataFormatConversionConfigurationProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-enabled
        Stability:
            stable
        """

        inputFormatConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.InputFormatConfigurationProperty"]
        """``CfnDeliveryStream.DataFormatConversionConfigurationProperty.InputFormatConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-inputformatconfiguration
        Stability:
            stable
        """

        outputFormatConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.OutputFormatConfigurationProperty"]
        """``CfnDeliveryStream.DataFormatConversionConfigurationProperty.OutputFormatConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-outputformatconfiguration
        Stability:
            stable
        """

        schemaConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.SchemaConfigurationProperty"]
        """``CfnDeliveryStream.DataFormatConversionConfigurationProperty.SchemaConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-schemaconfiguration
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.DeserializerProperty", jsii_struct_bases=[])
    class DeserializerProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deserializer.html
        Stability:
            stable
        """
        hiveJsonSerDe: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.HiveJsonSerDeProperty"]
        """``CfnDeliveryStream.DeserializerProperty.HiveJsonSerDe``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deserializer.html#cfn-kinesisfirehose-deliverystream-deserializer-hivejsonserde
        Stability:
            stable
        """

        openXJsonSerDe: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.OpenXJsonSerDeProperty"]
        """``CfnDeliveryStream.DeserializerProperty.OpenXJsonSerDe``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deserializer.html#cfn-kinesisfirehose-deliverystream-deserializer-openxjsonserde
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ElasticsearchBufferingHintsProperty", jsii_struct_bases=[])
    class ElasticsearchBufferingHintsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html
        Stability:
            stable
        """
        intervalInSeconds: jsii.Number
        """``CfnDeliveryStream.ElasticsearchBufferingHintsProperty.IntervalInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html#cfn-kinesisfirehose-deliverystream-elasticsearchbufferinghints-intervalinseconds
        Stability:
            stable
        """

        sizeInMBs: jsii.Number
        """``CfnDeliveryStream.ElasticsearchBufferingHintsProperty.SizeInMBs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html#cfn-kinesisfirehose-deliverystream-elasticsearchbufferinghints-sizeinmbs
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ElasticsearchDestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchLoggingOptions: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-cloudwatchloggingoptions
        Stability:
            stable
        """
        processingConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.ProcessingConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-processingconfiguration
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty", jsii_struct_bases=[_ElasticsearchDestinationConfigurationProperty])
    class ElasticsearchDestinationConfigurationProperty(_ElasticsearchDestinationConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html
        Stability:
            stable
        """
        bufferingHints: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ElasticsearchBufferingHintsProperty"]
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.BufferingHints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-bufferinghints
        Stability:
            stable
        """

        domainArn: str
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.DomainARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-domainarn
        Stability:
            stable
        """

        indexName: str
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.IndexName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-indexname
        Stability:
            stable
        """

        indexRotationPeriod: str
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.IndexRotationPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-indexrotationperiod
        Stability:
            stable
        """

        retryOptions: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ElasticsearchRetryOptionsProperty"]
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.RetryOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-retryoptions
        Stability:
            stable
        """

        roleArn: str
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-rolearn
        Stability:
            stable
        """

        s3BackupMode: str
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.S3BackupMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-s3backupmode
        Stability:
            stable
        """

        s3Configuration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.S3Configuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-s3configuration
        Stability:
            stable
        """

        typeName: str
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.TypeName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-typename
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ElasticsearchRetryOptionsProperty", jsii_struct_bases=[])
    class ElasticsearchRetryOptionsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchretryoptions.html
        Stability:
            stable
        """
        durationInSeconds: jsii.Number
        """``CfnDeliveryStream.ElasticsearchRetryOptionsProperty.DurationInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchretryoptions.html#cfn-kinesisfirehose-deliverystream-elasticsearchretryoptions-durationinseconds
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty", jsii_struct_bases=[])
    class EncryptionConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-encryptionconfiguration.html
        Stability:
            stable
        """
        kmsEncryptionConfig: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.KMSEncryptionConfigProperty"]
        """``CfnDeliveryStream.EncryptionConfigurationProperty.KMSEncryptionConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-encryptionconfiguration.html#cfn-kinesisfirehose-deliverystream-encryptionconfiguration-kmsencryptionconfig
        Stability:
            stable
        """

        noEncryptionConfig: str
        """``CfnDeliveryStream.EncryptionConfigurationProperty.NoEncryptionConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-encryptionconfiguration.html#cfn-kinesisfirehose-deliverystream-encryptionconfiguration-noencryptionconfig
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ExtendedS3DestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchLoggingOptions: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-cloudwatchloggingoptions
        Stability:
            stable
        """
        dataFormatConversionConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.DataFormatConversionConfigurationProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.DataFormatConversionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-dataformatconversionconfiguration
        Stability:
            stable
        """
        encryptionConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.EncryptionConfigurationProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.EncryptionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-encryptionconfiguration
        Stability:
            stable
        """
        errorOutputPrefix: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.ErrorOutputPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-erroroutputprefix
        Stability:
            stable
        """
        prefix: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-prefix
        Stability:
            stable
        """
        processingConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.ProcessingConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-processingconfiguration
        Stability:
            stable
        """
        s3BackupConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.S3BackupConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-s3backupconfiguration
        Stability:
            stable
        """
        s3BackupMode: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.S3BackupMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-s3backupmode
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty", jsii_struct_bases=[_ExtendedS3DestinationConfigurationProperty])
    class ExtendedS3DestinationConfigurationProperty(_ExtendedS3DestinationConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html
        Stability:
            stable
        """
        bucketArn: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.BucketARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-bucketarn
        Stability:
            stable
        """

        bufferingHints: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.BufferingHints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-bufferinghints
        Stability:
            stable
        """

        compressionFormat: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.CompressionFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-compressionformat
        Stability:
            stable
        """

        roleArn: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-rolearn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.HiveJsonSerDeProperty", jsii_struct_bases=[])
    class HiveJsonSerDeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-hivejsonserde.html
        Stability:
            stable
        """
        timestampFormats: typing.List[str]
        """``CfnDeliveryStream.HiveJsonSerDeProperty.TimestampFormats``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-hivejsonserde.html#cfn-kinesisfirehose-deliverystream-hivejsonserde-timestampformats
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.InputFormatConfigurationProperty", jsii_struct_bases=[])
    class InputFormatConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-inputformatconfiguration.html
        Stability:
            stable
        """
        deserializer: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.DeserializerProperty"]
        """``CfnDeliveryStream.InputFormatConfigurationProperty.Deserializer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-inputformatconfiguration.html#cfn-kinesisfirehose-deliverystream-inputformatconfiguration-deserializer
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty", jsii_struct_bases=[])
    class KMSEncryptionConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kmsencryptionconfig.html
        Stability:
            stable
        """
        awskmsKeyArn: str
        """``CfnDeliveryStream.KMSEncryptionConfigProperty.AWSKMSKeyARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kmsencryptionconfig.html#cfn-kinesisfirehose-deliverystream-kmsencryptionconfig-awskmskeyarn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.KinesisStreamSourceConfigurationProperty", jsii_struct_bases=[])
    class KinesisStreamSourceConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html
        Stability:
            stable
        """
        kinesisStreamArn: str
        """``CfnDeliveryStream.KinesisStreamSourceConfigurationProperty.KinesisStreamARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration-kinesisstreamarn
        Stability:
            stable
        """

        roleArn: str
        """``CfnDeliveryStream.KinesisStreamSourceConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration-rolearn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.OpenXJsonSerDeProperty", jsii_struct_bases=[])
    class OpenXJsonSerDeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html
        Stability:
            stable
        """
        caseInsensitive: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDeliveryStream.OpenXJsonSerDeProperty.CaseInsensitive``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html#cfn-kinesisfirehose-deliverystream-openxjsonserde-caseinsensitive
        Stability:
            stable
        """

        columnToJsonKeyMappings: typing.Union[aws_cdk.core.IResolvable, typing.Mapping[str,str]]
        """``CfnDeliveryStream.OpenXJsonSerDeProperty.ColumnToJsonKeyMappings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html#cfn-kinesisfirehose-deliverystream-openxjsonserde-columntojsonkeymappings
        Stability:
            stable
        """

        convertDotsInJsonKeysToUnderscores: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDeliveryStream.OpenXJsonSerDeProperty.ConvertDotsInJsonKeysToUnderscores``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html#cfn-kinesisfirehose-deliverystream-openxjsonserde-convertdotsinjsonkeystounderscores
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.OrcSerDeProperty", jsii_struct_bases=[])
    class OrcSerDeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html
        Stability:
            stable
        """
        blockSizeBytes: jsii.Number
        """``CfnDeliveryStream.OrcSerDeProperty.BlockSizeBytes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-blocksizebytes
        Stability:
            stable
        """

        bloomFilterColumns: typing.List[str]
        """``CfnDeliveryStream.OrcSerDeProperty.BloomFilterColumns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-bloomfiltercolumns
        Stability:
            stable
        """

        bloomFilterFalsePositiveProbability: jsii.Number
        """``CfnDeliveryStream.OrcSerDeProperty.BloomFilterFalsePositiveProbability``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-bloomfilterfalsepositiveprobability
        Stability:
            stable
        """

        compression: str
        """``CfnDeliveryStream.OrcSerDeProperty.Compression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-compression
        Stability:
            stable
        """

        dictionaryKeyThreshold: jsii.Number
        """``CfnDeliveryStream.OrcSerDeProperty.DictionaryKeyThreshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-dictionarykeythreshold
        Stability:
            stable
        """

        enablePadding: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDeliveryStream.OrcSerDeProperty.EnablePadding``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-enablepadding
        Stability:
            stable
        """

        formatVersion: str
        """``CfnDeliveryStream.OrcSerDeProperty.FormatVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-formatversion
        Stability:
            stable
        """

        paddingTolerance: jsii.Number
        """``CfnDeliveryStream.OrcSerDeProperty.PaddingTolerance``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-paddingtolerance
        Stability:
            stable
        """

        rowIndexStride: jsii.Number
        """``CfnDeliveryStream.OrcSerDeProperty.RowIndexStride``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-rowindexstride
        Stability:
            stable
        """

        stripeSizeBytes: jsii.Number
        """``CfnDeliveryStream.OrcSerDeProperty.StripeSizeBytes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-stripesizebytes
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.OutputFormatConfigurationProperty", jsii_struct_bases=[])
    class OutputFormatConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-outputformatconfiguration.html
        Stability:
            stable
        """
        serializer: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.SerializerProperty"]
        """``CfnDeliveryStream.OutputFormatConfigurationProperty.Serializer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-outputformatconfiguration.html#cfn-kinesisfirehose-deliverystream-outputformatconfiguration-serializer
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ParquetSerDeProperty", jsii_struct_bases=[])
    class ParquetSerDeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html
        Stability:
            stable
        """
        blockSizeBytes: jsii.Number
        """``CfnDeliveryStream.ParquetSerDeProperty.BlockSizeBytes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-blocksizebytes
        Stability:
            stable
        """

        compression: str
        """``CfnDeliveryStream.ParquetSerDeProperty.Compression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-compression
        Stability:
            stable
        """

        enableDictionaryCompression: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDeliveryStream.ParquetSerDeProperty.EnableDictionaryCompression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-enabledictionarycompression
        Stability:
            stable
        """

        maxPaddingBytes: jsii.Number
        """``CfnDeliveryStream.ParquetSerDeProperty.MaxPaddingBytes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-maxpaddingbytes
        Stability:
            stable
        """

        pageSizeBytes: jsii.Number
        """``CfnDeliveryStream.ParquetSerDeProperty.PageSizeBytes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-pagesizebytes
        Stability:
            stable
        """

        writerVersion: str
        """``CfnDeliveryStream.ParquetSerDeProperty.WriterVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-writerversion
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty", jsii_struct_bases=[])
    class ProcessingConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html
        Stability:
            stable
        """
        enabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDeliveryStream.ProcessingConfigurationProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html#cfn-kinesisfirehose-deliverystream-processingconfiguration-enabled
        Stability:
            stable
        """

        processors: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ProcessorProperty"]]]
        """``CfnDeliveryStream.ProcessingConfigurationProperty.Processors``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html#cfn-kinesisfirehose-deliverystream-processingconfiguration-processors
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty", jsii_struct_bases=[])
    class ProcessorParameterProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html
        Stability:
            stable
        """
        parameterName: str
        """``CfnDeliveryStream.ProcessorParameterProperty.ParameterName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html#cfn-kinesisfirehose-deliverystream-processorparameter-parametername
        Stability:
            stable
        """

        parameterValue: str
        """``CfnDeliveryStream.ProcessorParameterProperty.ParameterValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html#cfn-kinesisfirehose-deliverystream-processorparameter-parametervalue
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ProcessorProperty", jsii_struct_bases=[])
    class ProcessorProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html
        Stability:
            stable
        """
        parameters: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ProcessorParameterProperty"]]]
        """``CfnDeliveryStream.ProcessorProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html#cfn-kinesisfirehose-deliverystream-processor-parameters
        Stability:
            stable
        """

        type: str
        """``CfnDeliveryStream.ProcessorProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html#cfn-kinesisfirehose-deliverystream-processor-type
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _RedshiftDestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchLoggingOptions: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-cloudwatchloggingoptions
        Stability:
            stable
        """
        processingConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.ProcessingConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-processingconfiguration
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.RedshiftDestinationConfigurationProperty", jsii_struct_bases=[_RedshiftDestinationConfigurationProperty])
    class RedshiftDestinationConfigurationProperty(_RedshiftDestinationConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html
        Stability:
            stable
        """
        clusterJdbcurl: str
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.ClusterJDBCURL``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-clusterjdbcurl
        Stability:
            stable
        """

        copyCommand: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.CopyCommandProperty"]
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.CopyCommand``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-copycommand
        Stability:
            stable
        """

        password: str
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.Password``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-password
        Stability:
            stable
        """

        roleArn: str
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-rolearn
        Stability:
            stable
        """

        s3Configuration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.S3Configuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-s3configuration
        Stability:
            stable
        """

        username: str
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.Username``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-username
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _S3DestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchLoggingOptions: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-cloudwatchloggingoptions
        Stability:
            stable
        """
        encryptionConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.EncryptionConfigurationProperty"]
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.EncryptionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-encryptionconfiguration
        Stability:
            stable
        """
        errorOutputPrefix: str
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.ErrorOutputPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-erroroutputprefix
        Stability:
            stable
        """
        prefix: str
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.Prefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-prefix
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty", jsii_struct_bases=[_S3DestinationConfigurationProperty])
    class S3DestinationConfigurationProperty(_S3DestinationConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html
        Stability:
            stable
        """
        bucketArn: str
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.BucketARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-bucketarn
        Stability:
            stable
        """

        bufferingHints: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"]
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.BufferingHints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-bufferinghints
        Stability:
            stable
        """

        compressionFormat: str
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.CompressionFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-compressionformat
        Stability:
            stable
        """

        roleArn: str
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-rolearn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SchemaConfigurationProperty", jsii_struct_bases=[])
    class SchemaConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html
        Stability:
            stable
        """
        catalogId: str
        """``CfnDeliveryStream.SchemaConfigurationProperty.CatalogId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-catalogid
        Stability:
            stable
        """

        databaseName: str
        """``CfnDeliveryStream.SchemaConfigurationProperty.DatabaseName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-databasename
        Stability:
            stable
        """

        region: str
        """``CfnDeliveryStream.SchemaConfigurationProperty.Region``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-region
        Stability:
            stable
        """

        roleArn: str
        """``CfnDeliveryStream.SchemaConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-rolearn
        Stability:
            stable
        """

        tableName: str
        """``CfnDeliveryStream.SchemaConfigurationProperty.TableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-tablename
        Stability:
            stable
        """

        versionId: str
        """``CfnDeliveryStream.SchemaConfigurationProperty.VersionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-versionid
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SerializerProperty", jsii_struct_bases=[])
    class SerializerProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-serializer.html
        Stability:
            stable
        """
        orcSerDe: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.OrcSerDeProperty"]
        """``CfnDeliveryStream.SerializerProperty.OrcSerDe``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-serializer.html#cfn-kinesisfirehose-deliverystream-serializer-orcserde
        Stability:
            stable
        """

        parquetSerDe: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ParquetSerDeProperty"]
        """``CfnDeliveryStream.SerializerProperty.ParquetSerDe``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-serializer.html#cfn-kinesisfirehose-deliverystream-serializer-parquetserde
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SplunkDestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchLoggingOptions: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-cloudwatchloggingoptions
        Stability:
            stable
        """
        hecAcknowledgmentTimeoutInSeconds: jsii.Number
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECAcknowledgmentTimeoutInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecacknowledgmenttimeoutinseconds
        Stability:
            stable
        """
        processingConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.ProcessingConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-processingconfiguration
        Stability:
            stable
        """
        retryOptions: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.SplunkRetryOptionsProperty"]
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.RetryOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-retryoptions
        Stability:
            stable
        """
        s3BackupMode: str
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.S3BackupMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-s3backupmode
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SplunkDestinationConfigurationProperty", jsii_struct_bases=[_SplunkDestinationConfigurationProperty])
    class SplunkDestinationConfigurationProperty(_SplunkDestinationConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html
        Stability:
            stable
        """
        hecEndpoint: str
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECEndpoint``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecendpoint
        Stability:
            stable
        """

        hecEndpointType: str
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECEndpointType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecendpointtype
        Stability:
            stable
        """

        hecToken: str
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECToken``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hectoken
        Stability:
            stable
        """

        s3Configuration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.S3Configuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-s3configuration
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SplunkRetryOptionsProperty", jsii_struct_bases=[])
    class SplunkRetryOptionsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkretryoptions.html
        Stability:
            stable
        """
        durationInSeconds: jsii.Number
        """``CfnDeliveryStream.SplunkRetryOptionsProperty.DurationInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkretryoptions.html#cfn-kinesisfirehose-deliverystream-splunkretryoptions-durationinseconds
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStreamProps", jsii_struct_bases=[])
class CfnDeliveryStreamProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::KinesisFirehose::DeliveryStream``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html
    Stability:
        stable
    """
    deliveryStreamName: str
    """``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamname
    Stability:
        stable
    """

    deliveryStreamType: str
    """``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamtype
    Stability:
        stable
    """

    elasticsearchDestinationConfiguration: typing.Union["CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty", aws_cdk.core.IResolvable]
    """``AWS::KinesisFirehose::DeliveryStream.ElasticsearchDestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration
    Stability:
        stable
    """

    extendedS3DestinationConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.ExtendedS3DestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration
    Stability:
        stable
    """

    kinesisStreamSourceConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.KinesisStreamSourceConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.KinesisStreamSourceConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration
    Stability:
        stable
    """

    redshiftDestinationConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.RedshiftDestinationConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.RedshiftDestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration
    Stability:
        stable
    """

    s3DestinationConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.S3DestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration
    Stability:
        stable
    """

    splunkDestinationConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryStream.SplunkDestinationConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.SplunkDestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration
    Stability:
        stable
    """

__all__ = ["CfnDeliveryStream", "CfnDeliveryStreamProps", "__jsii_assembly__"]

publication.publish()
