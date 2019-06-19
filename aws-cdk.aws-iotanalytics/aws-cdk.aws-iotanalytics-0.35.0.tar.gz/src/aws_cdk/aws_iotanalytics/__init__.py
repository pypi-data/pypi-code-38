import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-iotanalytics", "0.35.0", __name__, "aws-iotanalytics@0.35.0.jsii.tgz")
class CfnChannel(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotanalytics.CfnChannel"):
    """A CloudFormation ``AWS::IoTAnalytics::Channel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoTAnalytics::Channel
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, channel_name: typing.Optional[str]=None, retention_period: typing.Optional[typing.Union[typing.Optional["RetentionPeriodProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::IoTAnalytics::Channel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            channelName: ``AWS::IoTAnalytics::Channel.ChannelName``.
            retentionPeriod: ``AWS::IoTAnalytics::Channel.RetentionPeriod``.
            tags: ``AWS::IoTAnalytics::Channel.Tags``.

        Stability:
            experimental
        """
        props: CfnChannelProps = {}

        if channel_name is not None:
            props["channelName"] = channel_name

        if retention_period is not None:
            props["retentionPeriod"] = retention_period

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::IoTAnalytics::Channel.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html#cfn-iotanalytics-channel-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="channelName")
    def channel_name(self) -> typing.Optional[str]:
        """``AWS::IoTAnalytics::Channel.ChannelName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html#cfn-iotanalytics-channel-channelname
        Stability:
            experimental
        """
        return jsii.get(self, "channelName")

    @channel_name.setter
    def channel_name(self, value: typing.Optional[str]):
        return jsii.set(self, "channelName", value)

    @property
    @jsii.member(jsii_name="retentionPeriod")
    def retention_period(self) -> typing.Optional[typing.Union[typing.Optional["RetentionPeriodProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::IoTAnalytics::Channel.RetentionPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html#cfn-iotanalytics-channel-retentionperiod
        Stability:
            experimental
        """
        return jsii.get(self, "retentionPeriod")

    @retention_period.setter
    def retention_period(self, value: typing.Optional[typing.Union[typing.Optional["RetentionPeriodProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "retentionPeriod", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnChannel.RetentionPeriodProperty", jsii_struct_bases=[])
    class RetentionPeriodProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-channel-retentionperiod.html
        Stability:
            experimental
        """
        numberOfDays: jsii.Number
        """``CfnChannel.RetentionPeriodProperty.NumberOfDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-channel-retentionperiod.html#cfn-iotanalytics-channel-retentionperiod-numberofdays
        Stability:
            experimental
        """

        unlimited: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnChannel.RetentionPeriodProperty.Unlimited``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-channel-retentionperiod.html#cfn-iotanalytics-channel-retentionperiod-unlimited
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnChannelProps", jsii_struct_bases=[])
class CfnChannelProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::IoTAnalytics::Channel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html
    Stability:
        experimental
    """
    channelName: str
    """``AWS::IoTAnalytics::Channel.ChannelName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html#cfn-iotanalytics-channel-channelname
    Stability:
        experimental
    """

    retentionPeriod: typing.Union["CfnChannel.RetentionPeriodProperty", aws_cdk.cdk.IResolvable]
    """``AWS::IoTAnalytics::Channel.RetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html#cfn-iotanalytics-channel-retentionperiod
    Stability:
        experimental
    """

    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::IoTAnalytics::Channel.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html#cfn-iotanalytics-channel-tags
    Stability:
        experimental
    """

class CfnDataset(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset"):
    """A CloudFormation ``AWS::IoTAnalytics::Dataset``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoTAnalytics::Dataset
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, actions: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ActionProperty"]]], content_delivery_rules: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "DatasetContentDeliveryRuleProperty"]]]]]=None, dataset_name: typing.Optional[str]=None, retention_period: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["RetentionPeriodProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, triggers: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "TriggerProperty"]]]]]=None, versioning_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VersioningConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::IoTAnalytics::Dataset``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            actions: ``AWS::IoTAnalytics::Dataset.Actions``.
            contentDeliveryRules: ``AWS::IoTAnalytics::Dataset.ContentDeliveryRules``.
            datasetName: ``AWS::IoTAnalytics::Dataset.DatasetName``.
            retentionPeriod: ``AWS::IoTAnalytics::Dataset.RetentionPeriod``.
            tags: ``AWS::IoTAnalytics::Dataset.Tags``.
            triggers: ``AWS::IoTAnalytics::Dataset.Triggers``.
            versioningConfiguration: ``AWS::IoTAnalytics::Dataset.VersioningConfiguration``.

        Stability:
            experimental
        """
        props: CfnDatasetProps = {"actions": actions}

        if content_delivery_rules is not None:
            props["contentDeliveryRules"] = content_delivery_rules

        if dataset_name is not None:
            props["datasetName"] = dataset_name

        if retention_period is not None:
            props["retentionPeriod"] = retention_period

        if tags is not None:
            props["tags"] = tags

        if triggers is not None:
            props["triggers"] = triggers

        if versioning_configuration is not None:
            props["versioningConfiguration"] = versioning_configuration

        jsii.create(CfnDataset, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::IoTAnalytics::Dataset.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ActionProperty"]]]:
        """``AWS::IoTAnalytics::Dataset.Actions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-actions
        Stability:
            experimental
        """
        return jsii.get(self, "actions")

    @actions.setter
    def actions(self, value: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ActionProperty"]]]):
        return jsii.set(self, "actions", value)

    @property
    @jsii.member(jsii_name="contentDeliveryRules")
    def content_delivery_rules(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "DatasetContentDeliveryRuleProperty"]]]]]:
        """``AWS::IoTAnalytics::Dataset.ContentDeliveryRules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-contentdeliveryrules
        Stability:
            experimental
        """
        return jsii.get(self, "contentDeliveryRules")

    @content_delivery_rules.setter
    def content_delivery_rules(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "DatasetContentDeliveryRuleProperty"]]]]]):
        return jsii.set(self, "contentDeliveryRules", value)

    @property
    @jsii.member(jsii_name="datasetName")
    def dataset_name(self) -> typing.Optional[str]:
        """``AWS::IoTAnalytics::Dataset.DatasetName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-datasetname
        Stability:
            experimental
        """
        return jsii.get(self, "datasetName")

    @dataset_name.setter
    def dataset_name(self, value: typing.Optional[str]):
        return jsii.set(self, "datasetName", value)

    @property
    @jsii.member(jsii_name="retentionPeriod")
    def retention_period(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["RetentionPeriodProperty"]]]:
        """``AWS::IoTAnalytics::Dataset.RetentionPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-retentionperiod
        Stability:
            experimental
        """
        return jsii.get(self, "retentionPeriod")

    @retention_period.setter
    def retention_period(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["RetentionPeriodProperty"]]]):
        return jsii.set(self, "retentionPeriod", value)

    @property
    @jsii.member(jsii_name="triggers")
    def triggers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "TriggerProperty"]]]]]:
        """``AWS::IoTAnalytics::Dataset.Triggers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-triggers
        Stability:
            experimental
        """
        return jsii.get(self, "triggers")

    @triggers.setter
    def triggers(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "TriggerProperty"]]]]]):
        return jsii.set(self, "triggers", value)

    @property
    @jsii.member(jsii_name="versioningConfiguration")
    def versioning_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VersioningConfigurationProperty"]]]:
        """``AWS::IoTAnalytics::Dataset.VersioningConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-versioningconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "versioningConfiguration")

    @versioning_configuration.setter
    def versioning_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["VersioningConfigurationProperty"]]]):
        return jsii.set(self, "versioningConfiguration", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ActionProperty(jsii.compat.TypedDict, total=False):
        containerAction: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.ContainerActionProperty"]
        """``CfnDataset.ActionProperty.ContainerAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-action.html#cfn-iotanalytics-dataset-action-containeraction
        Stability:
            experimental
        """
        queryAction: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.QueryActionProperty"]
        """``CfnDataset.ActionProperty.QueryAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-action.html#cfn-iotanalytics-dataset-action-queryaction
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.ActionProperty", jsii_struct_bases=[_ActionProperty])
    class ActionProperty(_ActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-action.html
        Stability:
            experimental
        """
        actionName: str
        """``CfnDataset.ActionProperty.ActionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-action.html#cfn-iotanalytics-dataset-action-actionname
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ContainerActionProperty(jsii.compat.TypedDict, total=False):
        variables: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.VariableProperty"]]]
        """``CfnDataset.ContainerActionProperty.Variables``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-containeraction.html#cfn-iotanalytics-dataset-containeraction-variables
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.ContainerActionProperty", jsii_struct_bases=[_ContainerActionProperty])
    class ContainerActionProperty(_ContainerActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-containeraction.html
        Stability:
            experimental
        """
        executionRoleArn: str
        """``CfnDataset.ContainerActionProperty.ExecutionRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-containeraction.html#cfn-iotanalytics-dataset-containeraction-executionrolearn
        Stability:
            experimental
        """

        image: str
        """``CfnDataset.ContainerActionProperty.Image``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-containeraction.html#cfn-iotanalytics-dataset-containeraction-image
        Stability:
            experimental
        """

        resourceConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.ResourceConfigurationProperty"]
        """``CfnDataset.ContainerActionProperty.ResourceConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-containeraction.html#cfn-iotanalytics-dataset-containeraction-resourceconfiguration
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.DatasetContentDeliveryRuleDestinationProperty", jsii_struct_bases=[])
    class DatasetContentDeliveryRuleDestinationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-datasetcontentdeliveryruledestination.html
        Stability:
            experimental
        """
        iotEventsDestinationConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.IotEventsDestinationConfigurationProperty"]
        """``CfnDataset.DatasetContentDeliveryRuleDestinationProperty.IotEventsDestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-datasetcontentdeliveryruledestination.html#cfn-iotanalytics-dataset-datasetcontentdeliveryruledestination-ioteventsdestinationconfiguration
        Stability:
            experimental
        """

        s3DestinationConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.S3DestinationConfigurationProperty"]
        """``CfnDataset.DatasetContentDeliveryRuleDestinationProperty.S3DestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-datasetcontentdeliveryruledestination.html#cfn-iotanalytics-dataset-datasetcontentdeliveryruledestination-s3destinationconfiguration
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DatasetContentDeliveryRuleProperty(jsii.compat.TypedDict, total=False):
        entryName: str
        """``CfnDataset.DatasetContentDeliveryRuleProperty.EntryName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-datasetcontentdeliveryrule.html#cfn-iotanalytics-dataset-datasetcontentdeliveryrule-entryname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.DatasetContentDeliveryRuleProperty", jsii_struct_bases=[_DatasetContentDeliveryRuleProperty])
    class DatasetContentDeliveryRuleProperty(_DatasetContentDeliveryRuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-datasetcontentdeliveryrule.html
        Stability:
            experimental
        """
        destination: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.DatasetContentDeliveryRuleDestinationProperty"]
        """``CfnDataset.DatasetContentDeliveryRuleProperty.Destination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-datasetcontentdeliveryrule.html#cfn-iotanalytics-dataset-datasetcontentdeliveryrule-destination
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.DatasetContentVersionValueProperty", jsii_struct_bases=[])
    class DatasetContentVersionValueProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable-datasetcontentversionvalue.html
        Stability:
            experimental
        """
        datasetName: str
        """``CfnDataset.DatasetContentVersionValueProperty.DatasetName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable-datasetcontentversionvalue.html#cfn-iotanalytics-dataset-variable-datasetcontentversionvalue-datasetname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.DeltaTimeProperty", jsii_struct_bases=[])
    class DeltaTimeProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-deltatime.html
        Stability:
            experimental
        """
        offsetSeconds: jsii.Number
        """``CfnDataset.DeltaTimeProperty.OffsetSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-deltatime.html#cfn-iotanalytics-dataset-deltatime-offsetseconds
        Stability:
            experimental
        """

        timeExpression: str
        """``CfnDataset.DeltaTimeProperty.TimeExpression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-deltatime.html#cfn-iotanalytics-dataset-deltatime-timeexpression
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.FilterProperty", jsii_struct_bases=[])
    class FilterProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-filter.html
        Stability:
            experimental
        """
        deltaTime: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.DeltaTimeProperty"]
        """``CfnDataset.FilterProperty.DeltaTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-filter.html#cfn-iotanalytics-dataset-filter-deltatime
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.GlueConfigurationProperty", jsii_struct_bases=[])
    class GlueConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-glueconfiguration.html
        Stability:
            experimental
        """
        databaseName: str
        """``CfnDataset.GlueConfigurationProperty.DatabaseName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-glueconfiguration.html#cfn-iotanalytics-dataset-glueconfiguration-databasename
        Stability:
            experimental
        """

        tableName: str
        """``CfnDataset.GlueConfigurationProperty.TableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-glueconfiguration.html#cfn-iotanalytics-dataset-glueconfiguration-tablename
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.IotEventsDestinationConfigurationProperty", jsii_struct_bases=[])
    class IotEventsDestinationConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-ioteventsdestinationconfiguration.html
        Stability:
            experimental
        """
        inputName: str
        """``CfnDataset.IotEventsDestinationConfigurationProperty.InputName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-ioteventsdestinationconfiguration.html#cfn-iotanalytics-dataset-ioteventsdestinationconfiguration-inputname
        Stability:
            experimental
        """

        roleArn: str
        """``CfnDataset.IotEventsDestinationConfigurationProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-ioteventsdestinationconfiguration.html#cfn-iotanalytics-dataset-ioteventsdestinationconfiguration-rolearn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.OutputFileUriValueProperty", jsii_struct_bases=[])
    class OutputFileUriValueProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable-outputfileurivalue.html
        Stability:
            experimental
        """
        fileName: str
        """``CfnDataset.OutputFileUriValueProperty.FileName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable-outputfileurivalue.html#cfn-iotanalytics-dataset-variable-outputfileurivalue-filename
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _QueryActionProperty(jsii.compat.TypedDict, total=False):
        filters: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.FilterProperty"]]]
        """``CfnDataset.QueryActionProperty.Filters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-queryaction.html#cfn-iotanalytics-dataset-queryaction-filters
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.QueryActionProperty", jsii_struct_bases=[_QueryActionProperty])
    class QueryActionProperty(_QueryActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-queryaction.html
        Stability:
            experimental
        """
        sqlQuery: str
        """``CfnDataset.QueryActionProperty.SqlQuery``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-queryaction.html#cfn-iotanalytics-dataset-queryaction-sqlquery
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.ResourceConfigurationProperty", jsii_struct_bases=[])
    class ResourceConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-resourceconfiguration.html
        Stability:
            experimental
        """
        computeType: str
        """``CfnDataset.ResourceConfigurationProperty.ComputeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-resourceconfiguration.html#cfn-iotanalytics-dataset-resourceconfiguration-computetype
        Stability:
            experimental
        """

        volumeSizeInGb: jsii.Number
        """``CfnDataset.ResourceConfigurationProperty.VolumeSizeInGB``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-resourceconfiguration.html#cfn-iotanalytics-dataset-resourceconfiguration-volumesizeingb
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.RetentionPeriodProperty", jsii_struct_bases=[])
    class RetentionPeriodProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-retentionperiod.html
        Stability:
            experimental
        """
        numberOfDays: jsii.Number
        """``CfnDataset.RetentionPeriodProperty.NumberOfDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-retentionperiod.html#cfn-iotanalytics-dataset-retentionperiod-numberofdays
        Stability:
            experimental
        """

        unlimited: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDataset.RetentionPeriodProperty.Unlimited``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-retentionperiod.html#cfn-iotanalytics-dataset-retentionperiod-unlimited
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _S3DestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        glueConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.GlueConfigurationProperty"]
        """``CfnDataset.S3DestinationConfigurationProperty.GlueConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-s3destinationconfiguration.html#cfn-iotanalytics-dataset-s3destinationconfiguration-glueconfiguration
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.S3DestinationConfigurationProperty", jsii_struct_bases=[_S3DestinationConfigurationProperty])
    class S3DestinationConfigurationProperty(_S3DestinationConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-s3destinationconfiguration.html
        Stability:
            experimental
        """
        bucket: str
        """``CfnDataset.S3DestinationConfigurationProperty.Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-s3destinationconfiguration.html#cfn-iotanalytics-dataset-s3destinationconfiguration-bucket
        Stability:
            experimental
        """

        key: str
        """``CfnDataset.S3DestinationConfigurationProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-s3destinationconfiguration.html#cfn-iotanalytics-dataset-s3destinationconfiguration-key
        Stability:
            experimental
        """

        roleArn: str
        """``CfnDataset.S3DestinationConfigurationProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-s3destinationconfiguration.html#cfn-iotanalytics-dataset-s3destinationconfiguration-rolearn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.ScheduleProperty", jsii_struct_bases=[])
    class ScheduleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-trigger-schedule.html
        Stability:
            experimental
        """
        scheduleExpression: str
        """``CfnDataset.ScheduleProperty.ScheduleExpression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-trigger-schedule.html#cfn-iotanalytics-dataset-trigger-schedule-scheduleexpression
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.TriggerProperty", jsii_struct_bases=[])
    class TriggerProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-trigger.html
        Stability:
            experimental
        """
        schedule: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.ScheduleProperty"]
        """``CfnDataset.TriggerProperty.Schedule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-trigger.html#cfn-iotanalytics-dataset-trigger-schedule
        Stability:
            experimental
        """

        triggeringDataset: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.TriggeringDatasetProperty"]
        """``CfnDataset.TriggerProperty.TriggeringDataset``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-trigger.html#cfn-iotanalytics-dataset-trigger-triggeringdataset
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.TriggeringDatasetProperty", jsii_struct_bases=[])
    class TriggeringDatasetProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-triggeringdataset.html
        Stability:
            experimental
        """
        datasetName: str
        """``CfnDataset.TriggeringDatasetProperty.DatasetName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-triggeringdataset.html#cfn-iotanalytics-dataset-triggeringdataset-datasetname
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _VariableProperty(jsii.compat.TypedDict, total=False):
        datasetContentVersionValue: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.DatasetContentVersionValueProperty"]
        """``CfnDataset.VariableProperty.DatasetContentVersionValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html#cfn-iotanalytics-dataset-variable-datasetcontentversionvalue
        Stability:
            experimental
        """
        doubleValue: jsii.Number
        """``CfnDataset.VariableProperty.DoubleValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html#cfn-iotanalytics-dataset-variable-doublevalue
        Stability:
            experimental
        """
        outputFileUriValue: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.OutputFileUriValueProperty"]
        """``CfnDataset.VariableProperty.OutputFileUriValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html#cfn-iotanalytics-dataset-variable-outputfileurivalue
        Stability:
            experimental
        """
        stringValue: str
        """``CfnDataset.VariableProperty.StringValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html#cfn-iotanalytics-dataset-variable-stringvalue
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.VariableProperty", jsii_struct_bases=[_VariableProperty])
    class VariableProperty(_VariableProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html
        Stability:
            experimental
        """
        variableName: str
        """``CfnDataset.VariableProperty.VariableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html#cfn-iotanalytics-dataset-variable-variablename
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.VersioningConfigurationProperty", jsii_struct_bases=[])
    class VersioningConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-versioningconfiguration.html
        Stability:
            experimental
        """
        maxVersions: jsii.Number
        """``CfnDataset.VersioningConfigurationProperty.MaxVersions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-versioningconfiguration.html#cfn-iotanalytics-dataset-versioningconfiguration-maxversions
        Stability:
            experimental
        """

        unlimited: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDataset.VersioningConfigurationProperty.Unlimited``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-versioningconfiguration.html#cfn-iotanalytics-dataset-versioningconfiguration-unlimited
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDatasetProps(jsii.compat.TypedDict, total=False):
    contentDeliveryRules: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.DatasetContentDeliveryRuleProperty"]]]
    """``AWS::IoTAnalytics::Dataset.ContentDeliveryRules``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-contentdeliveryrules
    Stability:
        experimental
    """
    datasetName: str
    """``AWS::IoTAnalytics::Dataset.DatasetName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-datasetname
    Stability:
        experimental
    """
    retentionPeriod: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.RetentionPeriodProperty"]
    """``AWS::IoTAnalytics::Dataset.RetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-retentionperiod
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::IoTAnalytics::Dataset.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-tags
    Stability:
        experimental
    """
    triggers: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.TriggerProperty"]]]
    """``AWS::IoTAnalytics::Dataset.Triggers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-triggers
    Stability:
        experimental
    """
    versioningConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.VersioningConfigurationProperty"]
    """``AWS::IoTAnalytics::Dataset.VersioningConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-versioningconfiguration
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDatasetProps", jsii_struct_bases=[_CfnDatasetProps])
class CfnDatasetProps(_CfnDatasetProps):
    """Properties for defining a ``AWS::IoTAnalytics::Dataset``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html
    Stability:
        experimental
    """
    actions: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnDataset.ActionProperty"]]]
    """``AWS::IoTAnalytics::Dataset.Actions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-actions
    Stability:
        experimental
    """

class CfnDatastore(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotanalytics.CfnDatastore"):
    """A CloudFormation ``AWS::IoTAnalytics::Datastore``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoTAnalytics::Datastore
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, datastore_name: typing.Optional[str]=None, retention_period: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["RetentionPeriodProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::IoTAnalytics::Datastore``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            datastoreName: ``AWS::IoTAnalytics::Datastore.DatastoreName``.
            retentionPeriod: ``AWS::IoTAnalytics::Datastore.RetentionPeriod``.
            tags: ``AWS::IoTAnalytics::Datastore.Tags``.

        Stability:
            experimental
        """
        props: CfnDatastoreProps = {}

        if datastore_name is not None:
            props["datastoreName"] = datastore_name

        if retention_period is not None:
            props["retentionPeriod"] = retention_period

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnDatastore, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::IoTAnalytics::Datastore.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html#cfn-iotanalytics-datastore-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="datastoreName")
    def datastore_name(self) -> typing.Optional[str]:
        """``AWS::IoTAnalytics::Datastore.DatastoreName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html#cfn-iotanalytics-datastore-datastorename
        Stability:
            experimental
        """
        return jsii.get(self, "datastoreName")

    @datastore_name.setter
    def datastore_name(self, value: typing.Optional[str]):
        return jsii.set(self, "datastoreName", value)

    @property
    @jsii.member(jsii_name="retentionPeriod")
    def retention_period(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["RetentionPeriodProperty"]]]:
        """``AWS::IoTAnalytics::Datastore.RetentionPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html#cfn-iotanalytics-datastore-retentionperiod
        Stability:
            experimental
        """
        return jsii.get(self, "retentionPeriod")

    @retention_period.setter
    def retention_period(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["RetentionPeriodProperty"]]]):
        return jsii.set(self, "retentionPeriod", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDatastore.RetentionPeriodProperty", jsii_struct_bases=[])
    class RetentionPeriodProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-datastore-retentionperiod.html
        Stability:
            experimental
        """
        numberOfDays: jsii.Number
        """``CfnDatastore.RetentionPeriodProperty.NumberOfDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-datastore-retentionperiod.html#cfn-iotanalytics-datastore-retentionperiod-numberofdays
        Stability:
            experimental
        """

        unlimited: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnDatastore.RetentionPeriodProperty.Unlimited``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-datastore-retentionperiod.html#cfn-iotanalytics-datastore-retentionperiod-unlimited
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDatastoreProps", jsii_struct_bases=[])
class CfnDatastoreProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::IoTAnalytics::Datastore``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html
    Stability:
        experimental
    """
    datastoreName: str
    """``AWS::IoTAnalytics::Datastore.DatastoreName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html#cfn-iotanalytics-datastore-datastorename
    Stability:
        experimental
    """

    retentionPeriod: typing.Union[aws_cdk.cdk.IResolvable, "CfnDatastore.RetentionPeriodProperty"]
    """``AWS::IoTAnalytics::Datastore.RetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html#cfn-iotanalytics-datastore-retentionperiod
    Stability:
        experimental
    """

    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::IoTAnalytics::Datastore.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html#cfn-iotanalytics-datastore-tags
    Stability:
        experimental
    """

class CfnPipeline(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline"):
    """A CloudFormation ``AWS::IoTAnalytics::Pipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoTAnalytics::Pipeline
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, pipeline_activities: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ActivityProperty"]]], pipeline_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::IoTAnalytics::Pipeline``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            pipelineActivities: ``AWS::IoTAnalytics::Pipeline.PipelineActivities``.
            pipelineName: ``AWS::IoTAnalytics::Pipeline.PipelineName``.
            tags: ``AWS::IoTAnalytics::Pipeline.Tags``.

        Stability:
            experimental
        """
        props: CfnPipelineProps = {"pipelineActivities": pipeline_activities}

        if pipeline_name is not None:
            props["pipelineName"] = pipeline_name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnPipeline, self, [scope, id, props])

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
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::IoTAnalytics::Pipeline.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="pipelineActivities")
    def pipeline_activities(self) -> typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ActivityProperty"]]]:
        """``AWS::IoTAnalytics::Pipeline.PipelineActivities``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-pipelineactivities
        Stability:
            experimental
        """
        return jsii.get(self, "pipelineActivities")

    @pipeline_activities.setter
    def pipeline_activities(self, value: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ActivityProperty"]]]):
        return jsii.set(self, "pipelineActivities", value)

    @property
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> typing.Optional[str]:
        """``AWS::IoTAnalytics::Pipeline.PipelineName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-pipelinename
        Stability:
            experimental
        """
        return jsii.get(self, "pipelineName")

    @pipeline_name.setter
    def pipeline_name(self, value: typing.Optional[str]):
        return jsii.set(self, "pipelineName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.ActivityProperty", jsii_struct_bases=[])
    class ActivityProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html
        Stability:
            experimental
        """
        addAttributes: typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.AddAttributesProperty"]
        """``CfnPipeline.ActivityProperty.AddAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-addattributes
        Stability:
            experimental
        """

        channel: typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.ChannelProperty"]
        """``CfnPipeline.ActivityProperty.Channel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-channel
        Stability:
            experimental
        """

        datastore: typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.DatastoreProperty"]
        """``CfnPipeline.ActivityProperty.Datastore``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-datastore
        Stability:
            experimental
        """

        deviceRegistryEnrich: typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.DeviceRegistryEnrichProperty"]
        """``CfnPipeline.ActivityProperty.DeviceRegistryEnrich``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-deviceregistryenrich
        Stability:
            experimental
        """

        deviceShadowEnrich: typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.DeviceShadowEnrichProperty"]
        """``CfnPipeline.ActivityProperty.DeviceShadowEnrich``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-deviceshadowenrich
        Stability:
            experimental
        """

        filter: typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.FilterProperty"]
        """``CfnPipeline.ActivityProperty.Filter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-filter
        Stability:
            experimental
        """

        lambda_: typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.LambdaProperty"]
        """``CfnPipeline.ActivityProperty.Lambda``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-lambda
        Stability:
            experimental
        """

        math: typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.MathProperty"]
        """``CfnPipeline.ActivityProperty.Math``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-math
        Stability:
            experimental
        """

        removeAttributes: typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.RemoveAttributesProperty"]
        """``CfnPipeline.ActivityProperty.RemoveAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-removeattributes
        Stability:
            experimental
        """

        selectAttributes: typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.SelectAttributesProperty"]
        """``CfnPipeline.ActivityProperty.SelectAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-selectattributes
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.AddAttributesProperty", jsii_struct_bases=[])
    class AddAttributesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-addattributes.html
        Stability:
            experimental
        """
        attributes: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
        """``CfnPipeline.AddAttributesProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-addattributes.html#cfn-iotanalytics-pipeline-addattributes-attributes
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.AddAttributesProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-addattributes.html#cfn-iotanalytics-pipeline-addattributes-name
        Stability:
            experimental
        """

        next: str
        """``CfnPipeline.AddAttributesProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-addattributes.html#cfn-iotanalytics-pipeline-addattributes-next
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.ChannelProperty", jsii_struct_bases=[])
    class ChannelProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-channel.html
        Stability:
            experimental
        """
        channelName: str
        """``CfnPipeline.ChannelProperty.ChannelName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-channel.html#cfn-iotanalytics-pipeline-channel-channelname
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.ChannelProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-channel.html#cfn-iotanalytics-pipeline-channel-name
        Stability:
            experimental
        """

        next: str
        """``CfnPipeline.ChannelProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-channel.html#cfn-iotanalytics-pipeline-channel-next
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.DatastoreProperty", jsii_struct_bases=[])
    class DatastoreProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-datastore.html
        Stability:
            experimental
        """
        datastoreName: str
        """``CfnPipeline.DatastoreProperty.DatastoreName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-datastore.html#cfn-iotanalytics-pipeline-datastore-datastorename
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.DatastoreProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-datastore.html#cfn-iotanalytics-pipeline-datastore-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.DeviceRegistryEnrichProperty", jsii_struct_bases=[])
    class DeviceRegistryEnrichProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceregistryenrich.html
        Stability:
            experimental
        """
        attribute: str
        """``CfnPipeline.DeviceRegistryEnrichProperty.Attribute``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceregistryenrich.html#cfn-iotanalytics-pipeline-deviceregistryenrich-attribute
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.DeviceRegistryEnrichProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceregistryenrich.html#cfn-iotanalytics-pipeline-deviceregistryenrich-name
        Stability:
            experimental
        """

        next: str
        """``CfnPipeline.DeviceRegistryEnrichProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceregistryenrich.html#cfn-iotanalytics-pipeline-deviceregistryenrich-next
        Stability:
            experimental
        """

        roleArn: str
        """``CfnPipeline.DeviceRegistryEnrichProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceregistryenrich.html#cfn-iotanalytics-pipeline-deviceregistryenrich-rolearn
        Stability:
            experimental
        """

        thingName: str
        """``CfnPipeline.DeviceRegistryEnrichProperty.ThingName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceregistryenrich.html#cfn-iotanalytics-pipeline-deviceregistryenrich-thingname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.DeviceShadowEnrichProperty", jsii_struct_bases=[])
    class DeviceShadowEnrichProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceshadowenrich.html
        Stability:
            experimental
        """
        attribute: str
        """``CfnPipeline.DeviceShadowEnrichProperty.Attribute``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceshadowenrich.html#cfn-iotanalytics-pipeline-deviceshadowenrich-attribute
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.DeviceShadowEnrichProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceshadowenrich.html#cfn-iotanalytics-pipeline-deviceshadowenrich-name
        Stability:
            experimental
        """

        next: str
        """``CfnPipeline.DeviceShadowEnrichProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceshadowenrich.html#cfn-iotanalytics-pipeline-deviceshadowenrich-next
        Stability:
            experimental
        """

        roleArn: str
        """``CfnPipeline.DeviceShadowEnrichProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceshadowenrich.html#cfn-iotanalytics-pipeline-deviceshadowenrich-rolearn
        Stability:
            experimental
        """

        thingName: str
        """``CfnPipeline.DeviceShadowEnrichProperty.ThingName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceshadowenrich.html#cfn-iotanalytics-pipeline-deviceshadowenrich-thingname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.FilterProperty", jsii_struct_bases=[])
    class FilterProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-filter.html
        Stability:
            experimental
        """
        filter: str
        """``CfnPipeline.FilterProperty.Filter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-filter.html#cfn-iotanalytics-pipeline-filter-filter
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.FilterProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-filter.html#cfn-iotanalytics-pipeline-filter-name
        Stability:
            experimental
        """

        next: str
        """``CfnPipeline.FilterProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-filter.html#cfn-iotanalytics-pipeline-filter-next
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.LambdaProperty", jsii_struct_bases=[])
    class LambdaProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-lambda.html
        Stability:
            experimental
        """
        batchSize: jsii.Number
        """``CfnPipeline.LambdaProperty.BatchSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-lambda.html#cfn-iotanalytics-pipeline-lambda-batchsize
        Stability:
            experimental
        """

        lambdaName: str
        """``CfnPipeline.LambdaProperty.LambdaName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-lambda.html#cfn-iotanalytics-pipeline-lambda-lambdaname
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.LambdaProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-lambda.html#cfn-iotanalytics-pipeline-lambda-name
        Stability:
            experimental
        """

        next: str
        """``CfnPipeline.LambdaProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-lambda.html#cfn-iotanalytics-pipeline-lambda-next
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.MathProperty", jsii_struct_bases=[])
    class MathProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-math.html
        Stability:
            experimental
        """
        attribute: str
        """``CfnPipeline.MathProperty.Attribute``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-math.html#cfn-iotanalytics-pipeline-math-attribute
        Stability:
            experimental
        """

        math: str
        """``CfnPipeline.MathProperty.Math``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-math.html#cfn-iotanalytics-pipeline-math-math
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.MathProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-math.html#cfn-iotanalytics-pipeline-math-name
        Stability:
            experimental
        """

        next: str
        """``CfnPipeline.MathProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-math.html#cfn-iotanalytics-pipeline-math-next
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.RemoveAttributesProperty", jsii_struct_bases=[])
    class RemoveAttributesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-removeattributes.html
        Stability:
            experimental
        """
        attributes: typing.List[str]
        """``CfnPipeline.RemoveAttributesProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-removeattributes.html#cfn-iotanalytics-pipeline-removeattributes-attributes
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.RemoveAttributesProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-removeattributes.html#cfn-iotanalytics-pipeline-removeattributes-name
        Stability:
            experimental
        """

        next: str
        """``CfnPipeline.RemoveAttributesProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-removeattributes.html#cfn-iotanalytics-pipeline-removeattributes-next
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.SelectAttributesProperty", jsii_struct_bases=[])
    class SelectAttributesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-selectattributes.html
        Stability:
            experimental
        """
        attributes: typing.List[str]
        """``CfnPipeline.SelectAttributesProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-selectattributes.html#cfn-iotanalytics-pipeline-selectattributes-attributes
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.SelectAttributesProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-selectattributes.html#cfn-iotanalytics-pipeline-selectattributes-name
        Stability:
            experimental
        """

        next: str
        """``CfnPipeline.SelectAttributesProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-selectattributes.html#cfn-iotanalytics-pipeline-selectattributes-next
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPipelineProps(jsii.compat.TypedDict, total=False):
    pipelineName: str
    """``AWS::IoTAnalytics::Pipeline.PipelineName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-pipelinename
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::IoTAnalytics::Pipeline.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipelineProps", jsii_struct_bases=[_CfnPipelineProps])
class CfnPipelineProps(_CfnPipelineProps):
    """Properties for defining a ``AWS::IoTAnalytics::Pipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html
    Stability:
        experimental
    """
    pipelineActivities: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.ActivityProperty"]]]
    """``AWS::IoTAnalytics::Pipeline.PipelineActivities``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-pipelineactivities
    Stability:
        experimental
    """

__all__ = ["CfnChannel", "CfnChannelProps", "CfnDataset", "CfnDatasetProps", "CfnDatastore", "CfnDatastoreProps", "CfnPipeline", "CfnPipelineProps", "__jsii_assembly__"]

publication.publish()
