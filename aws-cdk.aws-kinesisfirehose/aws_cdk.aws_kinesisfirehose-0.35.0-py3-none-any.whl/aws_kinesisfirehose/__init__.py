import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-kinesisfirehose", "0.35.0", __name__, "aws-kinesisfirehose@0.35.0.jsii.tgz")
class CfnDeliveryStream(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream"):
    """A CloudFormation ``AWS::KinesisFirehose::DeliveryStream``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html
    Stability:
        experimental
    cloudformationResource:
        AWS::KinesisFirehose::DeliveryStream
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, delivery_stream_name: typing.Optional[str]=None, delivery_stream_type: typing.Optional[str]=None, elasticsearch_destination_configuration: typing.Optional[typing.Union[typing.Optional["ElasticsearchDestinationConfigurationProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, extended_s3_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ExtendedS3DestinationConfigurationProperty"]]]=None, kinesis_stream_source_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["KinesisStreamSourceConfigurationProperty"]]]=None, redshift_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["RedshiftDestinationConfigurationProperty"]]]=None, s3_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["S3DestinationConfigurationProperty"]]]=None, splunk_destination_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SplunkDestinationConfigurationProperty"]]]=None) -> None:
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
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> typing.Optional[str]:
        """``AWS::KinesisFirehose::DeliveryStream.DeliveryStreamName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamname
        Stability:
            experimental
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
            experimental
        """
        return jsii.get(self, "deliveryStreamType")

    @delivery_stream_type.setter
    def delivery_stream_type(self, value: typing.Optional[str]):
        return jsii.set(self, "deliveryStreamType", value)

    @property
    @jsii.member(jsii_name="elasticsearchDestinationConfiguration")
    def elasticsearch_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional["ElasticsearchDestinationConfigurationProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::KinesisFirehose::DeliveryStream.ElasticsearchDestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "elasticsearchDestinationConfiguration")

    @elasticsearch_destination_configuration.setter
    def elasticsearch_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional["ElasticsearchDestinationConfigurationProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "elasticsearchDestinationConfiguration", value)

    @property
    @jsii.member(jsii_name="extendedS3DestinationConfiguration")
    def extended_s3_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ExtendedS3DestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.ExtendedS3DestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "extendedS3DestinationConfiguration")

    @extended_s3_destination_configuration.setter
    def extended_s3_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ExtendedS3DestinationConfigurationProperty"]]]):
        return jsii.set(self, "extendedS3DestinationConfiguration", value)

    @property
    @jsii.member(jsii_name="kinesisStreamSourceConfiguration")
    def kinesis_stream_source_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["KinesisStreamSourceConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.KinesisStreamSourceConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "kinesisStreamSourceConfiguration")

    @kinesis_stream_source_configuration.setter
    def kinesis_stream_source_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["KinesisStreamSourceConfigurationProperty"]]]):
        return jsii.set(self, "kinesisStreamSourceConfiguration", value)

    @property
    @jsii.member(jsii_name="redshiftDestinationConfiguration")
    def redshift_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["RedshiftDestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.RedshiftDestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "redshiftDestinationConfiguration")

    @redshift_destination_configuration.setter
    def redshift_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["RedshiftDestinationConfigurationProperty"]]]):
        return jsii.set(self, "redshiftDestinationConfiguration", value)

    @property
    @jsii.member(jsii_name="s3DestinationConfiguration")
    def s3_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["S3DestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.S3DestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "s3DestinationConfiguration")

    @s3_destination_configuration.setter
    def s3_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["S3DestinationConfigurationProperty"]]]):
        return jsii.set(self, "s3DestinationConfiguration", value)

    @property
    @jsii.member(jsii_name="splunkDestinationConfiguration")
    def splunk_destination_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SplunkDestinationConfigurationProperty"]]]:
        """``AWS::KinesisFirehose::DeliveryStream.SplunkDestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "splunkDestinationConfiguration")

    @splunk_destination_configuration.setter
    def splunk_destination_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SplunkDestinationConfigurationProperty"]]]):
        return jsii.set(self, "splunkDestinationConfiguration", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty", jsii_struct_bases=[])
    class BufferingHintsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html
        Stability:
            experimental
        """
        intervalInSeconds: jsii.Number
        """``CfnDeliveryStream.BufferingHintsProperty.IntervalInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html#cfn-kinesisfirehose-deliverystream-bufferinghints-intervalinseconds
        Stability:
            experimental
        """

        sizeInMBs: jsii.Number
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
        enabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.DataFormatConversionConfigurationProperty", jsii_struct_bases=[])
    class DataFormatConversionConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDeliveryStream.DataFormatConversionConfigurationProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-enabled
        Stability:
            experimental
        """

        inputFormatConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.InputFormatConfigurationProperty"]
        """``CfnDeliveryStream.DataFormatConversionConfigurationProperty.InputFormatConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-inputformatconfiguration
        Stability:
            experimental
        """

        outputFormatConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.OutputFormatConfigurationProperty"]
        """``CfnDeliveryStream.DataFormatConversionConfigurationProperty.OutputFormatConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-outputformatconfiguration
        Stability:
            experimental
        """

        schemaConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.SchemaConfigurationProperty"]
        """``CfnDeliveryStream.DataFormatConversionConfigurationProperty.SchemaConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-schemaconfiguration
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.DeserializerProperty", jsii_struct_bases=[])
    class DeserializerProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deserializer.html
        Stability:
            experimental
        """
        hiveJsonSerDe: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.HiveJsonSerDeProperty"]
        """``CfnDeliveryStream.DeserializerProperty.HiveJsonSerDe``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deserializer.html#cfn-kinesisfirehose-deliverystream-deserializer-hivejsonserde
        Stability:
            experimental
        """

        openXJsonSerDe: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.OpenXJsonSerDeProperty"]
        """``CfnDeliveryStream.DeserializerProperty.OpenXJsonSerDe``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deserializer.html#cfn-kinesisfirehose-deliverystream-deserializer-openxjsonserde
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
        intervalInSeconds: jsii.Number
        """``CfnDeliveryStream.ElasticsearchBufferingHintsProperty.IntervalInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html#cfn-kinesisfirehose-deliverystream-elasticsearchbufferinghints-intervalinseconds
        Stability:
            experimental
        """

        sizeInMBs: jsii.Number
        """``CfnDeliveryStream.ElasticsearchBufferingHintsProperty.SizeInMBs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html#cfn-kinesisfirehose-deliverystream-elasticsearchbufferinghints-sizeinmbs
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ElasticsearchDestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchLoggingOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-cloudwatchloggingoptions
        Stability:
            experimental
        """
        processingConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]
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
        bufferingHints: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.ElasticsearchBufferingHintsProperty"]
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

        retryOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.ElasticsearchRetryOptionsProperty"]
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

        s3Configuration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
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
        durationInSeconds: jsii.Number
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
        kmsEncryptionConfig: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.KMSEncryptionConfigProperty"]
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
        cloudWatchLoggingOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-cloudwatchloggingoptions
        Stability:
            experimental
        """
        dataFormatConversionConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.DataFormatConversionConfigurationProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.DataFormatConversionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-dataformatconversionconfiguration
        Stability:
            experimental
        """
        encryptionConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.EncryptionConfigurationProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.EncryptionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-encryptionconfiguration
        Stability:
            experimental
        """
        errorOutputPrefix: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.ErrorOutputPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-erroroutputprefix
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
        processingConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.ProcessingConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-processingconfiguration
        Stability:
            experimental
        """
        s3BackupConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
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

        bufferingHints: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"]
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

        roleArn: str
        """``CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-rolearn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.HiveJsonSerDeProperty", jsii_struct_bases=[])
    class HiveJsonSerDeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-hivejsonserde.html
        Stability:
            experimental
        """
        timestampFormats: typing.List[str]
        """``CfnDeliveryStream.HiveJsonSerDeProperty.TimestampFormats``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-hivejsonserde.html#cfn-kinesisfirehose-deliverystream-hivejsonserde-timestampformats
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.InputFormatConfigurationProperty", jsii_struct_bases=[])
    class InputFormatConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-inputformatconfiguration.html
        Stability:
            experimental
        """
        deserializer: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.DeserializerProperty"]
        """``CfnDeliveryStream.InputFormatConfigurationProperty.Deserializer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-inputformatconfiguration.html#cfn-kinesisfirehose-deliverystream-inputformatconfiguration-deserializer
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.OpenXJsonSerDeProperty", jsii_struct_bases=[])
    class OpenXJsonSerDeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html
        Stability:
            experimental
        """
        caseInsensitive: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDeliveryStream.OpenXJsonSerDeProperty.CaseInsensitive``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html#cfn-kinesisfirehose-deliverystream-openxjsonserde-caseinsensitive
        Stability:
            experimental
        """

        columnToJsonKeyMappings: typing.Union[aws_cdk.cdk.IResolvable, typing.Mapping[str,str]]
        """``CfnDeliveryStream.OpenXJsonSerDeProperty.ColumnToJsonKeyMappings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html#cfn-kinesisfirehose-deliverystream-openxjsonserde-columntojsonkeymappings
        Stability:
            experimental
        """

        convertDotsInJsonKeysToUnderscores: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDeliveryStream.OpenXJsonSerDeProperty.ConvertDotsInJsonKeysToUnderscores``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html#cfn-kinesisfirehose-deliverystream-openxjsonserde-convertdotsinjsonkeystounderscores
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.OrcSerDeProperty", jsii_struct_bases=[])
    class OrcSerDeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html
        Stability:
            experimental
        """
        blockSizeBytes: jsii.Number
        """``CfnDeliveryStream.OrcSerDeProperty.BlockSizeBytes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-blocksizebytes
        Stability:
            experimental
        """

        bloomFilterColumns: typing.List[str]
        """``CfnDeliveryStream.OrcSerDeProperty.BloomFilterColumns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-bloomfiltercolumns
        Stability:
            experimental
        """

        bloomFilterFalsePositiveProbability: jsii.Number
        """``CfnDeliveryStream.OrcSerDeProperty.BloomFilterFalsePositiveProbability``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-bloomfilterfalsepositiveprobability
        Stability:
            experimental
        """

        compression: str
        """``CfnDeliveryStream.OrcSerDeProperty.Compression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-compression
        Stability:
            experimental
        """

        dictionaryKeyThreshold: jsii.Number
        """``CfnDeliveryStream.OrcSerDeProperty.DictionaryKeyThreshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-dictionarykeythreshold
        Stability:
            experimental
        """

        enablePadding: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDeliveryStream.OrcSerDeProperty.EnablePadding``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-enablepadding
        Stability:
            experimental
        """

        formatVersion: str
        """``CfnDeliveryStream.OrcSerDeProperty.FormatVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-formatversion
        Stability:
            experimental
        """

        paddingTolerance: jsii.Number
        """``CfnDeliveryStream.OrcSerDeProperty.PaddingTolerance``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-paddingtolerance
        Stability:
            experimental
        """

        rowIndexStride: jsii.Number
        """``CfnDeliveryStream.OrcSerDeProperty.RowIndexStride``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-rowindexstride
        Stability:
            experimental
        """

        stripeSizeBytes: jsii.Number
        """``CfnDeliveryStream.OrcSerDeProperty.StripeSizeBytes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-stripesizebytes
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.OutputFormatConfigurationProperty", jsii_struct_bases=[])
    class OutputFormatConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-outputformatconfiguration.html
        Stability:
            experimental
        """
        serializer: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.SerializerProperty"]
        """``CfnDeliveryStream.OutputFormatConfigurationProperty.Serializer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-outputformatconfiguration.html#cfn-kinesisfirehose-deliverystream-outputformatconfiguration-serializer
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ParquetSerDeProperty", jsii_struct_bases=[])
    class ParquetSerDeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html
        Stability:
            experimental
        """
        blockSizeBytes: jsii.Number
        """``CfnDeliveryStream.ParquetSerDeProperty.BlockSizeBytes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-blocksizebytes
        Stability:
            experimental
        """

        compression: str
        """``CfnDeliveryStream.ParquetSerDeProperty.Compression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-compression
        Stability:
            experimental
        """

        enableDictionaryCompression: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDeliveryStream.ParquetSerDeProperty.EnableDictionaryCompression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-enabledictionarycompression
        Stability:
            experimental
        """

        maxPaddingBytes: jsii.Number
        """``CfnDeliveryStream.ParquetSerDeProperty.MaxPaddingBytes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-maxpaddingbytes
        Stability:
            experimental
        """

        pageSizeBytes: jsii.Number
        """``CfnDeliveryStream.ParquetSerDeProperty.PageSizeBytes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-pagesizebytes
        Stability:
            experimental
        """

        writerVersion: str
        """``CfnDeliveryStream.ParquetSerDeProperty.WriterVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-writerversion
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
        enabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDeliveryStream.ProcessingConfigurationProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html#cfn-kinesisfirehose-deliverystream-processingconfiguration-enabled
        Stability:
            experimental
        """

        processors: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.ProcessorProperty"]]]
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
        parameters: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.ProcessorParameterProperty"]]]
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
        cloudWatchLoggingOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.RedshiftDestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-cloudwatchloggingoptions
        Stability:
            experimental
        """
        processingConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]
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

        copyCommand: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.CopyCommandProperty"]
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

        s3Configuration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
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
        cloudWatchLoggingOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-cloudwatchloggingoptions
        Stability:
            experimental
        """
        encryptionConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.EncryptionConfigurationProperty"]
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.EncryptionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-encryptionconfiguration
        Stability:
            experimental
        """
        errorOutputPrefix: str
        """``CfnDeliveryStream.S3DestinationConfigurationProperty.ErrorOutputPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-erroroutputprefix
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

        bufferingHints: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"]
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SchemaConfigurationProperty", jsii_struct_bases=[])
    class SchemaConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html
        Stability:
            experimental
        """
        catalogId: str
        """``CfnDeliveryStream.SchemaConfigurationProperty.CatalogId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-catalogid
        Stability:
            experimental
        """

        databaseName: str
        """``CfnDeliveryStream.SchemaConfigurationProperty.DatabaseName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-databasename
        Stability:
            experimental
        """

        region: str
        """``CfnDeliveryStream.SchemaConfigurationProperty.Region``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-region
        Stability:
            experimental
        """

        roleArn: str
        """``CfnDeliveryStream.SchemaConfigurationProperty.RoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-rolearn
        Stability:
            experimental
        """

        tableName: str
        """``CfnDeliveryStream.SchemaConfigurationProperty.TableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-tablename
        Stability:
            experimental
        """

        versionId: str
        """``CfnDeliveryStream.SchemaConfigurationProperty.VersionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-versionid
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SerializerProperty", jsii_struct_bases=[])
    class SerializerProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-serializer.html
        Stability:
            experimental
        """
        orcSerDe: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.OrcSerDeProperty"]
        """``CfnDeliveryStream.SerializerProperty.OrcSerDe``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-serializer.html#cfn-kinesisfirehose-deliverystream-serializer-orcserde
        Stability:
            experimental
        """

        parquetSerDe: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.ParquetSerDeProperty"]
        """``CfnDeliveryStream.SerializerProperty.ParquetSerDe``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-serializer.html#cfn-kinesisfirehose-deliverystream-serializer-parquetserde
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SplunkDestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchLoggingOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.CloudWatchLoggingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-cloudwatchloggingoptions
        Stability:
            experimental
        """
        hecAcknowledgmentTimeoutInSeconds: jsii.Number
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.HECAcknowledgmentTimeoutInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecacknowledgmenttimeoutinseconds
        Stability:
            experimental
        """
        processingConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]
        """``CfnDeliveryStream.SplunkDestinationConfigurationProperty.ProcessingConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-processingconfiguration
        Stability:
            experimental
        """
        retryOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.SplunkRetryOptionsProperty"]
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

        s3Configuration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
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
        durationInSeconds: jsii.Number
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

    elasticsearchDestinationConfiguration: typing.Union["CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty", aws_cdk.cdk.IResolvable]
    """``AWS::KinesisFirehose::DeliveryStream.ElasticsearchDestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration
    Stability:
        experimental
    """

    extendedS3DestinationConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.ExtendedS3DestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration
    Stability:
        experimental
    """

    kinesisStreamSourceConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.KinesisStreamSourceConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.KinesisStreamSourceConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration
    Stability:
        experimental
    """

    redshiftDestinationConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.RedshiftDestinationConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.RedshiftDestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration
    Stability:
        experimental
    """

    s3DestinationConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.S3DestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration
    Stability:
        experimental
    """

    splunkDestinationConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDeliveryStream.SplunkDestinationConfigurationProperty"]
    """``AWS::KinesisFirehose::DeliveryStream.SplunkDestinationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration
    Stability:
        experimental
    """

__all__ = ["CfnDeliveryStream", "CfnDeliveryStreamProps", "__jsii_assembly__"]

publication.publish()
