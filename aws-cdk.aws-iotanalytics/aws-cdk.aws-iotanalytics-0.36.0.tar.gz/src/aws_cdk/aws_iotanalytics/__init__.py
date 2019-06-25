import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-iotanalytics", "0.36.0", __name__, "aws-iotanalytics@0.36.0.jsii.tgz")
class CfnChannel(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotanalytics.CfnChannel"):
    """A CloudFormation ``AWS::IoTAnalytics::Channel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoTAnalytics::Channel
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, channel_name: typing.Optional[str]=None, retention_period: typing.Optional[typing.Union[typing.Optional["RetentionPeriodProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::IoTAnalytics::Channel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            channel_name: ``AWS::IoTAnalytics::Channel.ChannelName``.
            retention_period: ``AWS::IoTAnalytics::Channel.RetentionPeriod``.
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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::IoTAnalytics::Channel.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html#cfn-iotanalytics-channel-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="channelName")
    def channel_name(self) -> typing.Optional[str]:
        """``AWS::IoTAnalytics::Channel.ChannelName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html#cfn-iotanalytics-channel-channelname
        Stability:
            stable
        """
        return jsii.get(self, "channelName")

    @channel_name.setter
    def channel_name(self, value: typing.Optional[str]):
        return jsii.set(self, "channelName", value)

    @property
    @jsii.member(jsii_name="retentionPeriod")
    def retention_period(self) -> typing.Optional[typing.Union[typing.Optional["RetentionPeriodProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::IoTAnalytics::Channel.RetentionPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html#cfn-iotanalytics-channel-retentionperiod
        Stability:
            stable
        """
        return jsii.get(self, "retentionPeriod")

    @retention_period.setter
    def retention_period(self, value: typing.Optional[typing.Union[typing.Optional["RetentionPeriodProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "retentionPeriod", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnChannel.RetentionPeriodProperty", jsii_struct_bases=[])
    class RetentionPeriodProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-channel-retentionperiod.html
        Stability:
            stable
        """
        numberOfDays: jsii.Number
        """``CfnChannel.RetentionPeriodProperty.NumberOfDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-channel-retentionperiod.html#cfn-iotanalytics-channel-retentionperiod-numberofdays
        Stability:
            stable
        """

        unlimited: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnChannel.RetentionPeriodProperty.Unlimited``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-channel-retentionperiod.html#cfn-iotanalytics-channel-retentionperiod-unlimited
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnChannelProps", jsii_struct_bases=[])
class CfnChannelProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::IoTAnalytics::Channel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html
    Stability:
        stable
    """
    channelName: str
    """``AWS::IoTAnalytics::Channel.ChannelName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html#cfn-iotanalytics-channel-channelname
    Stability:
        stable
    """

    retentionPeriod: typing.Union["CfnChannel.RetentionPeriodProperty", aws_cdk.core.IResolvable]
    """``AWS::IoTAnalytics::Channel.RetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html#cfn-iotanalytics-channel-retentionperiod
    Stability:
        stable
    """

    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::IoTAnalytics::Channel.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html#cfn-iotanalytics-channel-tags
    Stability:
        stable
    """

class CfnDataset(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset"):
    """A CloudFormation ``AWS::IoTAnalytics::Dataset``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoTAnalytics::Dataset
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, actions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ActionProperty"]]], content_delivery_rules: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "DatasetContentDeliveryRuleProperty"]]]]]=None, dataset_name: typing.Optional[str]=None, retention_period: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RetentionPeriodProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, triggers: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TriggerProperty"]]]]]=None, versioning_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["VersioningConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::IoTAnalytics::Dataset``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            actions: ``AWS::IoTAnalytics::Dataset.Actions``.
            content_delivery_rules: ``AWS::IoTAnalytics::Dataset.ContentDeliveryRules``.
            dataset_name: ``AWS::IoTAnalytics::Dataset.DatasetName``.
            retention_period: ``AWS::IoTAnalytics::Dataset.RetentionPeriod``.
            tags: ``AWS::IoTAnalytics::Dataset.Tags``.
            triggers: ``AWS::IoTAnalytics::Dataset.Triggers``.
            versioning_configuration: ``AWS::IoTAnalytics::Dataset.VersioningConfiguration``.

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::IoTAnalytics::Dataset.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ActionProperty"]]]:
        """``AWS::IoTAnalytics::Dataset.Actions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-actions
        Stability:
            stable
        """
        return jsii.get(self, "actions")

    @actions.setter
    def actions(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ActionProperty"]]]):
        return jsii.set(self, "actions", value)

    @property
    @jsii.member(jsii_name="contentDeliveryRules")
    def content_delivery_rules(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "DatasetContentDeliveryRuleProperty"]]]]]:
        """``AWS::IoTAnalytics::Dataset.ContentDeliveryRules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-contentdeliveryrules
        Stability:
            stable
        """
        return jsii.get(self, "contentDeliveryRules")

    @content_delivery_rules.setter
    def content_delivery_rules(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "DatasetContentDeliveryRuleProperty"]]]]]):
        return jsii.set(self, "contentDeliveryRules", value)

    @property
    @jsii.member(jsii_name="datasetName")
    def dataset_name(self) -> typing.Optional[str]:
        """``AWS::IoTAnalytics::Dataset.DatasetName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-datasetname
        Stability:
            stable
        """
        return jsii.get(self, "datasetName")

    @dataset_name.setter
    def dataset_name(self, value: typing.Optional[str]):
        return jsii.set(self, "datasetName", value)

    @property
    @jsii.member(jsii_name="retentionPeriod")
    def retention_period(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RetentionPeriodProperty"]]]:
        """``AWS::IoTAnalytics::Dataset.RetentionPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-retentionperiod
        Stability:
            stable
        """
        return jsii.get(self, "retentionPeriod")

    @retention_period.setter
    def retention_period(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RetentionPeriodProperty"]]]):
        return jsii.set(self, "retentionPeriod", value)

    @property
    @jsii.member(jsii_name="triggers")
    def triggers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TriggerProperty"]]]]]:
        """``AWS::IoTAnalytics::Dataset.Triggers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-triggers
        Stability:
            stable
        """
        return jsii.get(self, "triggers")

    @triggers.setter
    def triggers(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "TriggerProperty"]]]]]):
        return jsii.set(self, "triggers", value)

    @property
    @jsii.member(jsii_name="versioningConfiguration")
    def versioning_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["VersioningConfigurationProperty"]]]:
        """``AWS::IoTAnalytics::Dataset.VersioningConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-versioningconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "versioningConfiguration")

    @versioning_configuration.setter
    def versioning_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["VersioningConfigurationProperty"]]]):
        return jsii.set(self, "versioningConfiguration", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ActionProperty(jsii.compat.TypedDict, total=False):
        containerAction: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.ContainerActionProperty"]
        """``CfnDataset.ActionProperty.ContainerAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-action.html#cfn-iotanalytics-dataset-action-containeraction
        Stability:
            stable
        """
        queryAction: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.QueryActionProperty"]
        """``CfnDataset.ActionProperty.QueryAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-action.html#cfn-iotanalytics-dataset-action-queryaction
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.ActionProperty", jsii_struct_bases=[_ActionProperty])
    class ActionProperty(_ActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-action.html
        Stability:
            stable
        """
        actionName: str
        """``CfnDataset.ActionProperty.ActionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-action.html#cfn-iotanalytics-dataset-action-actionname
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ContainerActionProperty(jsii.compat.TypedDict, total=False):
        variables: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDataset.VariableProperty"]]]
        """``CfnDataset.ContainerActionProperty.Variables``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-containeraction.html#cfn-iotanalytics-dataset-containeraction-variables
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.ContainerActionProperty", jsii_struct_bases=[_ContainerActionProperty])
    class ContainerActionProperty(_ContainerActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-containeraction.html
        Stability:
            stable
        """
        executionRoleArn: str
        """``CfnDataset.ContainerActionProperty.ExecutionRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-containeraction.html#cfn-iotanalytics-dataset-containeraction-executionrolearn
        Stability:
            stable
        """

        image: str
        """``CfnDataset.ContainerActionProperty.Image``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-containeraction.html#cfn-iotanalytics-dataset-containeraction-image
        Stability:
            stable
        """

        resourceConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.ResourceConfigurationProperty"]
        """``CfnDataset.ContainerActionProperty.ResourceConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-containeraction.html#cfn-iotanalytics-dataset-containeraction-resourceconfiguration
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.DatasetContentDeliveryRuleDestinationProperty", jsii_struct_bases=[])
    class DatasetContentDeliveryRuleDestinationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-datasetcontentdeliveryruledestination.html
        Stability:
            stable
        """
        iotEventsDestinationConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.IotEventsDestinationConfigurationProperty"]
        """``CfnDataset.DatasetContentDeliveryRuleDestinationProperty.IotEventsDestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-datasetcontentdeliveryruledestination.html#cfn-iotanalytics-dataset-datasetcontentdeliveryruledestination-ioteventsdestinationconfiguration
        Stability:
            stable
        """

        s3DestinationConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.S3DestinationConfigurationProperty"]
        """``CfnDataset.DatasetContentDeliveryRuleDestinationProperty.S3DestinationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-datasetcontentdeliveryruledestination.html#cfn-iotanalytics-dataset-datasetcontentdeliveryruledestination-s3destinationconfiguration
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DatasetContentDeliveryRuleProperty(jsii.compat.TypedDict, total=False):
        entryName: str
        """``CfnDataset.DatasetContentDeliveryRuleProperty.EntryName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-datasetcontentdeliveryrule.html#cfn-iotanalytics-dataset-datasetcontentdeliveryrule-entryname
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.DatasetContentDeliveryRuleProperty", jsii_struct_bases=[_DatasetContentDeliveryRuleProperty])
    class DatasetContentDeliveryRuleProperty(_DatasetContentDeliveryRuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-datasetcontentdeliveryrule.html
        Stability:
            stable
        """
        destination: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.DatasetContentDeliveryRuleDestinationProperty"]
        """``CfnDataset.DatasetContentDeliveryRuleProperty.Destination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-datasetcontentdeliveryrule.html#cfn-iotanalytics-dataset-datasetcontentdeliveryrule-destination
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.DatasetContentVersionValueProperty", jsii_struct_bases=[])
    class DatasetContentVersionValueProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable-datasetcontentversionvalue.html
        Stability:
            stable
        """
        datasetName: str
        """``CfnDataset.DatasetContentVersionValueProperty.DatasetName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable-datasetcontentversionvalue.html#cfn-iotanalytics-dataset-variable-datasetcontentversionvalue-datasetname
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.DeltaTimeProperty", jsii_struct_bases=[])
    class DeltaTimeProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-deltatime.html
        Stability:
            stable
        """
        offsetSeconds: jsii.Number
        """``CfnDataset.DeltaTimeProperty.OffsetSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-deltatime.html#cfn-iotanalytics-dataset-deltatime-offsetseconds
        Stability:
            stable
        """

        timeExpression: str
        """``CfnDataset.DeltaTimeProperty.TimeExpression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-deltatime.html#cfn-iotanalytics-dataset-deltatime-timeexpression
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.FilterProperty", jsii_struct_bases=[])
    class FilterProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-filter.html
        Stability:
            stable
        """
        deltaTime: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.DeltaTimeProperty"]
        """``CfnDataset.FilterProperty.DeltaTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-filter.html#cfn-iotanalytics-dataset-filter-deltatime
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.GlueConfigurationProperty", jsii_struct_bases=[])
    class GlueConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-glueconfiguration.html
        Stability:
            stable
        """
        databaseName: str
        """``CfnDataset.GlueConfigurationProperty.DatabaseName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-glueconfiguration.html#cfn-iotanalytics-dataset-glueconfiguration-databasename
        Stability:
            stable
        """

        tableName: str
        """``CfnDataset.GlueConfigurationProperty.TableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-glueconfiguration.html#cfn-iotanalytics-dataset-glueconfiguration-tablename
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.IotEventsDestinationConfigurationProperty", jsii_struct_bases=[])
    class IotEventsDestinationConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-ioteventsdestinationconfiguration.html
        Stability:
            stable
        """
        inputName: str
        """``CfnDataset.IotEventsDestinationConfigurationProperty.InputName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-ioteventsdestinationconfiguration.html#cfn-iotanalytics-dataset-ioteventsdestinationconfiguration-inputname
        Stability:
            stable
        """

        roleArn: str
        """``CfnDataset.IotEventsDestinationConfigurationProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-ioteventsdestinationconfiguration.html#cfn-iotanalytics-dataset-ioteventsdestinationconfiguration-rolearn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.OutputFileUriValueProperty", jsii_struct_bases=[])
    class OutputFileUriValueProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable-outputfileurivalue.html
        Stability:
            stable
        """
        fileName: str
        """``CfnDataset.OutputFileUriValueProperty.FileName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable-outputfileurivalue.html#cfn-iotanalytics-dataset-variable-outputfileurivalue-filename
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _QueryActionProperty(jsii.compat.TypedDict, total=False):
        filters: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDataset.FilterProperty"]]]
        """``CfnDataset.QueryActionProperty.Filters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-queryaction.html#cfn-iotanalytics-dataset-queryaction-filters
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.QueryActionProperty", jsii_struct_bases=[_QueryActionProperty])
    class QueryActionProperty(_QueryActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-queryaction.html
        Stability:
            stable
        """
        sqlQuery: str
        """``CfnDataset.QueryActionProperty.SqlQuery``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-queryaction.html#cfn-iotanalytics-dataset-queryaction-sqlquery
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.ResourceConfigurationProperty", jsii_struct_bases=[])
    class ResourceConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-resourceconfiguration.html
        Stability:
            stable
        """
        computeType: str
        """``CfnDataset.ResourceConfigurationProperty.ComputeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-resourceconfiguration.html#cfn-iotanalytics-dataset-resourceconfiguration-computetype
        Stability:
            stable
        """

        volumeSizeInGb: jsii.Number
        """``CfnDataset.ResourceConfigurationProperty.VolumeSizeInGB``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-resourceconfiguration.html#cfn-iotanalytics-dataset-resourceconfiguration-volumesizeingb
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.RetentionPeriodProperty", jsii_struct_bases=[])
    class RetentionPeriodProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-retentionperiod.html
        Stability:
            stable
        """
        numberOfDays: jsii.Number
        """``CfnDataset.RetentionPeriodProperty.NumberOfDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-retentionperiod.html#cfn-iotanalytics-dataset-retentionperiod-numberofdays
        Stability:
            stable
        """

        unlimited: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDataset.RetentionPeriodProperty.Unlimited``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-retentionperiod.html#cfn-iotanalytics-dataset-retentionperiod-unlimited
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _S3DestinationConfigurationProperty(jsii.compat.TypedDict, total=False):
        glueConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.GlueConfigurationProperty"]
        """``CfnDataset.S3DestinationConfigurationProperty.GlueConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-s3destinationconfiguration.html#cfn-iotanalytics-dataset-s3destinationconfiguration-glueconfiguration
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.S3DestinationConfigurationProperty", jsii_struct_bases=[_S3DestinationConfigurationProperty])
    class S3DestinationConfigurationProperty(_S3DestinationConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-s3destinationconfiguration.html
        Stability:
            stable
        """
        bucket: str
        """``CfnDataset.S3DestinationConfigurationProperty.Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-s3destinationconfiguration.html#cfn-iotanalytics-dataset-s3destinationconfiguration-bucket
        Stability:
            stable
        """

        key: str
        """``CfnDataset.S3DestinationConfigurationProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-s3destinationconfiguration.html#cfn-iotanalytics-dataset-s3destinationconfiguration-key
        Stability:
            stable
        """

        roleArn: str
        """``CfnDataset.S3DestinationConfigurationProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-s3destinationconfiguration.html#cfn-iotanalytics-dataset-s3destinationconfiguration-rolearn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.ScheduleProperty", jsii_struct_bases=[])
    class ScheduleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-trigger-schedule.html
        Stability:
            stable
        """
        scheduleExpression: str
        """``CfnDataset.ScheduleProperty.ScheduleExpression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-trigger-schedule.html#cfn-iotanalytics-dataset-trigger-schedule-scheduleexpression
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.TriggerProperty", jsii_struct_bases=[])
    class TriggerProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-trigger.html
        Stability:
            stable
        """
        schedule: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.ScheduleProperty"]
        """``CfnDataset.TriggerProperty.Schedule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-trigger.html#cfn-iotanalytics-dataset-trigger-schedule
        Stability:
            stable
        """

        triggeringDataset: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.TriggeringDatasetProperty"]
        """``CfnDataset.TriggerProperty.TriggeringDataset``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-trigger.html#cfn-iotanalytics-dataset-trigger-triggeringdataset
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.TriggeringDatasetProperty", jsii_struct_bases=[])
    class TriggeringDatasetProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-triggeringdataset.html
        Stability:
            stable
        """
        datasetName: str
        """``CfnDataset.TriggeringDatasetProperty.DatasetName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-triggeringdataset.html#cfn-iotanalytics-dataset-triggeringdataset-datasetname
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _VariableProperty(jsii.compat.TypedDict, total=False):
        datasetContentVersionValue: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.DatasetContentVersionValueProperty"]
        """``CfnDataset.VariableProperty.DatasetContentVersionValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html#cfn-iotanalytics-dataset-variable-datasetcontentversionvalue
        Stability:
            stable
        """
        doubleValue: jsii.Number
        """``CfnDataset.VariableProperty.DoubleValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html#cfn-iotanalytics-dataset-variable-doublevalue
        Stability:
            stable
        """
        outputFileUriValue: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.OutputFileUriValueProperty"]
        """``CfnDataset.VariableProperty.OutputFileUriValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html#cfn-iotanalytics-dataset-variable-outputfileurivalue
        Stability:
            stable
        """
        stringValue: str
        """``CfnDataset.VariableProperty.StringValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html#cfn-iotanalytics-dataset-variable-stringvalue
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.VariableProperty", jsii_struct_bases=[_VariableProperty])
    class VariableProperty(_VariableProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html
        Stability:
            stable
        """
        variableName: str
        """``CfnDataset.VariableProperty.VariableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html#cfn-iotanalytics-dataset-variable-variablename
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDataset.VersioningConfigurationProperty", jsii_struct_bases=[])
    class VersioningConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-versioningconfiguration.html
        Stability:
            stable
        """
        maxVersions: jsii.Number
        """``CfnDataset.VersioningConfigurationProperty.MaxVersions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-versioningconfiguration.html#cfn-iotanalytics-dataset-versioningconfiguration-maxversions
        Stability:
            stable
        """

        unlimited: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDataset.VersioningConfigurationProperty.Unlimited``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-versioningconfiguration.html#cfn-iotanalytics-dataset-versioningconfiguration-unlimited
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDatasetProps(jsii.compat.TypedDict, total=False):
    contentDeliveryRules: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDataset.DatasetContentDeliveryRuleProperty"]]]
    """``AWS::IoTAnalytics::Dataset.ContentDeliveryRules``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-contentdeliveryrules
    Stability:
        stable
    """
    datasetName: str
    """``AWS::IoTAnalytics::Dataset.DatasetName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-datasetname
    Stability:
        stable
    """
    retentionPeriod: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.RetentionPeriodProperty"]
    """``AWS::IoTAnalytics::Dataset.RetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-retentionperiod
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::IoTAnalytics::Dataset.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-tags
    Stability:
        stable
    """
    triggers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDataset.TriggerProperty"]]]
    """``AWS::IoTAnalytics::Dataset.Triggers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-triggers
    Stability:
        stable
    """
    versioningConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDataset.VersioningConfigurationProperty"]
    """``AWS::IoTAnalytics::Dataset.VersioningConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-versioningconfiguration
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDatasetProps", jsii_struct_bases=[_CfnDatasetProps])
class CfnDatasetProps(_CfnDatasetProps):
    """Properties for defining a ``AWS::IoTAnalytics::Dataset``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html
    Stability:
        stable
    """
    actions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDataset.ActionProperty"]]]
    """``AWS::IoTAnalytics::Dataset.Actions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-actions
    Stability:
        stable
    """

class CfnDatastore(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotanalytics.CfnDatastore"):
    """A CloudFormation ``AWS::IoTAnalytics::Datastore``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoTAnalytics::Datastore
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, datastore_name: typing.Optional[str]=None, retention_period: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RetentionPeriodProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::IoTAnalytics::Datastore``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            datastore_name: ``AWS::IoTAnalytics::Datastore.DatastoreName``.
            retention_period: ``AWS::IoTAnalytics::Datastore.RetentionPeriod``.
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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::IoTAnalytics::Datastore.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html#cfn-iotanalytics-datastore-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="datastoreName")
    def datastore_name(self) -> typing.Optional[str]:
        """``AWS::IoTAnalytics::Datastore.DatastoreName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html#cfn-iotanalytics-datastore-datastorename
        Stability:
            stable
        """
        return jsii.get(self, "datastoreName")

    @datastore_name.setter
    def datastore_name(self, value: typing.Optional[str]):
        return jsii.set(self, "datastoreName", value)

    @property
    @jsii.member(jsii_name="retentionPeriod")
    def retention_period(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RetentionPeriodProperty"]]]:
        """``AWS::IoTAnalytics::Datastore.RetentionPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html#cfn-iotanalytics-datastore-retentionperiod
        Stability:
            stable
        """
        return jsii.get(self, "retentionPeriod")

    @retention_period.setter
    def retention_period(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RetentionPeriodProperty"]]]):
        return jsii.set(self, "retentionPeriod", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDatastore.RetentionPeriodProperty", jsii_struct_bases=[])
    class RetentionPeriodProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-datastore-retentionperiod.html
        Stability:
            stable
        """
        numberOfDays: jsii.Number
        """``CfnDatastore.RetentionPeriodProperty.NumberOfDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-datastore-retentionperiod.html#cfn-iotanalytics-datastore-retentionperiod-numberofdays
        Stability:
            stable
        """

        unlimited: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDatastore.RetentionPeriodProperty.Unlimited``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-datastore-retentionperiod.html#cfn-iotanalytics-datastore-retentionperiod-unlimited
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDatastoreProps", jsii_struct_bases=[])
class CfnDatastoreProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::IoTAnalytics::Datastore``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html
    Stability:
        stable
    """
    datastoreName: str
    """``AWS::IoTAnalytics::Datastore.DatastoreName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html#cfn-iotanalytics-datastore-datastorename
    Stability:
        stable
    """

    retentionPeriod: typing.Union[aws_cdk.core.IResolvable, "CfnDatastore.RetentionPeriodProperty"]
    """``AWS::IoTAnalytics::Datastore.RetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html#cfn-iotanalytics-datastore-retentionperiod
    Stability:
        stable
    """

    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::IoTAnalytics::Datastore.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-datastore.html#cfn-iotanalytics-datastore-tags
    Stability:
        stable
    """

class CfnPipeline(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline"):
    """A CloudFormation ``AWS::IoTAnalytics::Pipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoTAnalytics::Pipeline
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, pipeline_activities: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ActivityProperty"]]], pipeline_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::IoTAnalytics::Pipeline``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            pipeline_activities: ``AWS::IoTAnalytics::Pipeline.PipelineActivities``.
            pipeline_name: ``AWS::IoTAnalytics::Pipeline.PipelineName``.
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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::IoTAnalytics::Pipeline.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="pipelineActivities")
    def pipeline_activities(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ActivityProperty"]]]:
        """``AWS::IoTAnalytics::Pipeline.PipelineActivities``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-pipelineactivities
        Stability:
            stable
        """
        return jsii.get(self, "pipelineActivities")

    @pipeline_activities.setter
    def pipeline_activities(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ActivityProperty"]]]):
        return jsii.set(self, "pipelineActivities", value)

    @property
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> typing.Optional[str]:
        """``AWS::IoTAnalytics::Pipeline.PipelineName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-pipelinename
        Stability:
            stable
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
            stable
        """
        addAttributes: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.AddAttributesProperty"]
        """``CfnPipeline.ActivityProperty.AddAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-addattributes
        Stability:
            stable
        """

        channel: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.ChannelProperty"]
        """``CfnPipeline.ActivityProperty.Channel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-channel
        Stability:
            stable
        """

        datastore: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.DatastoreProperty"]
        """``CfnPipeline.ActivityProperty.Datastore``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-datastore
        Stability:
            stable
        """

        deviceRegistryEnrich: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.DeviceRegistryEnrichProperty"]
        """``CfnPipeline.ActivityProperty.DeviceRegistryEnrich``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-deviceregistryenrich
        Stability:
            stable
        """

        deviceShadowEnrich: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.DeviceShadowEnrichProperty"]
        """``CfnPipeline.ActivityProperty.DeviceShadowEnrich``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-deviceshadowenrich
        Stability:
            stable
        """

        filter: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.FilterProperty"]
        """``CfnPipeline.ActivityProperty.Filter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-filter
        Stability:
            stable
        """

        lambda_: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.LambdaProperty"]
        """``CfnPipeline.ActivityProperty.Lambda``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-lambda
        Stability:
            stable
        """

        math: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.MathProperty"]
        """``CfnPipeline.ActivityProperty.Math``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-math
        Stability:
            stable
        """

        removeAttributes: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.RemoveAttributesProperty"]
        """``CfnPipeline.ActivityProperty.RemoveAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-removeattributes
        Stability:
            stable
        """

        selectAttributes: typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.SelectAttributesProperty"]
        """``CfnPipeline.ActivityProperty.SelectAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-selectattributes
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.AddAttributesProperty", jsii_struct_bases=[])
    class AddAttributesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-addattributes.html
        Stability:
            stable
        """
        attributes: typing.Any
        """``CfnPipeline.AddAttributesProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-addattributes.html#cfn-iotanalytics-pipeline-addattributes-attributes
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.AddAttributesProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-addattributes.html#cfn-iotanalytics-pipeline-addattributes-name
        Stability:
            stable
        """

        next: str
        """``CfnPipeline.AddAttributesProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-addattributes.html#cfn-iotanalytics-pipeline-addattributes-next
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.ChannelProperty", jsii_struct_bases=[])
    class ChannelProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-channel.html
        Stability:
            stable
        """
        channelName: str
        """``CfnPipeline.ChannelProperty.ChannelName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-channel.html#cfn-iotanalytics-pipeline-channel-channelname
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.ChannelProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-channel.html#cfn-iotanalytics-pipeline-channel-name
        Stability:
            stable
        """

        next: str
        """``CfnPipeline.ChannelProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-channel.html#cfn-iotanalytics-pipeline-channel-next
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.DatastoreProperty", jsii_struct_bases=[])
    class DatastoreProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-datastore.html
        Stability:
            stable
        """
        datastoreName: str
        """``CfnPipeline.DatastoreProperty.DatastoreName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-datastore.html#cfn-iotanalytics-pipeline-datastore-datastorename
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.DatastoreProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-datastore.html#cfn-iotanalytics-pipeline-datastore-name
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.DeviceRegistryEnrichProperty", jsii_struct_bases=[])
    class DeviceRegistryEnrichProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceregistryenrich.html
        Stability:
            stable
        """
        attribute: str
        """``CfnPipeline.DeviceRegistryEnrichProperty.Attribute``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceregistryenrich.html#cfn-iotanalytics-pipeline-deviceregistryenrich-attribute
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.DeviceRegistryEnrichProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceregistryenrich.html#cfn-iotanalytics-pipeline-deviceregistryenrich-name
        Stability:
            stable
        """

        next: str
        """``CfnPipeline.DeviceRegistryEnrichProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceregistryenrich.html#cfn-iotanalytics-pipeline-deviceregistryenrich-next
        Stability:
            stable
        """

        roleArn: str
        """``CfnPipeline.DeviceRegistryEnrichProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceregistryenrich.html#cfn-iotanalytics-pipeline-deviceregistryenrich-rolearn
        Stability:
            stable
        """

        thingName: str
        """``CfnPipeline.DeviceRegistryEnrichProperty.ThingName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceregistryenrich.html#cfn-iotanalytics-pipeline-deviceregistryenrich-thingname
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.DeviceShadowEnrichProperty", jsii_struct_bases=[])
    class DeviceShadowEnrichProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceshadowenrich.html
        Stability:
            stable
        """
        attribute: str
        """``CfnPipeline.DeviceShadowEnrichProperty.Attribute``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceshadowenrich.html#cfn-iotanalytics-pipeline-deviceshadowenrich-attribute
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.DeviceShadowEnrichProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceshadowenrich.html#cfn-iotanalytics-pipeline-deviceshadowenrich-name
        Stability:
            stable
        """

        next: str
        """``CfnPipeline.DeviceShadowEnrichProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceshadowenrich.html#cfn-iotanalytics-pipeline-deviceshadowenrich-next
        Stability:
            stable
        """

        roleArn: str
        """``CfnPipeline.DeviceShadowEnrichProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceshadowenrich.html#cfn-iotanalytics-pipeline-deviceshadowenrich-rolearn
        Stability:
            stable
        """

        thingName: str
        """``CfnPipeline.DeviceShadowEnrichProperty.ThingName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-deviceshadowenrich.html#cfn-iotanalytics-pipeline-deviceshadowenrich-thingname
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.FilterProperty", jsii_struct_bases=[])
    class FilterProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-filter.html
        Stability:
            stable
        """
        filter: str
        """``CfnPipeline.FilterProperty.Filter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-filter.html#cfn-iotanalytics-pipeline-filter-filter
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.FilterProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-filter.html#cfn-iotanalytics-pipeline-filter-name
        Stability:
            stable
        """

        next: str
        """``CfnPipeline.FilterProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-filter.html#cfn-iotanalytics-pipeline-filter-next
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.LambdaProperty", jsii_struct_bases=[])
    class LambdaProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-lambda.html
        Stability:
            stable
        """
        batchSize: jsii.Number
        """``CfnPipeline.LambdaProperty.BatchSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-lambda.html#cfn-iotanalytics-pipeline-lambda-batchsize
        Stability:
            stable
        """

        lambdaName: str
        """``CfnPipeline.LambdaProperty.LambdaName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-lambda.html#cfn-iotanalytics-pipeline-lambda-lambdaname
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.LambdaProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-lambda.html#cfn-iotanalytics-pipeline-lambda-name
        Stability:
            stable
        """

        next: str
        """``CfnPipeline.LambdaProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-lambda.html#cfn-iotanalytics-pipeline-lambda-next
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.MathProperty", jsii_struct_bases=[])
    class MathProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-math.html
        Stability:
            stable
        """
        attribute: str
        """``CfnPipeline.MathProperty.Attribute``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-math.html#cfn-iotanalytics-pipeline-math-attribute
        Stability:
            stable
        """

        math: str
        """``CfnPipeline.MathProperty.Math``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-math.html#cfn-iotanalytics-pipeline-math-math
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.MathProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-math.html#cfn-iotanalytics-pipeline-math-name
        Stability:
            stable
        """

        next: str
        """``CfnPipeline.MathProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-math.html#cfn-iotanalytics-pipeline-math-next
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.RemoveAttributesProperty", jsii_struct_bases=[])
    class RemoveAttributesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-removeattributes.html
        Stability:
            stable
        """
        attributes: typing.List[str]
        """``CfnPipeline.RemoveAttributesProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-removeattributes.html#cfn-iotanalytics-pipeline-removeattributes-attributes
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.RemoveAttributesProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-removeattributes.html#cfn-iotanalytics-pipeline-removeattributes-name
        Stability:
            stable
        """

        next: str
        """``CfnPipeline.RemoveAttributesProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-removeattributes.html#cfn-iotanalytics-pipeline-removeattributes-next
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.SelectAttributesProperty", jsii_struct_bases=[])
    class SelectAttributesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-selectattributes.html
        Stability:
            stable
        """
        attributes: typing.List[str]
        """``CfnPipeline.SelectAttributesProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-selectattributes.html#cfn-iotanalytics-pipeline-selectattributes-attributes
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.SelectAttributesProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-selectattributes.html#cfn-iotanalytics-pipeline-selectattributes-name
        Stability:
            stable
        """

        next: str
        """``CfnPipeline.SelectAttributesProperty.Next``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-selectattributes.html#cfn-iotanalytics-pipeline-selectattributes-next
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPipelineProps(jsii.compat.TypedDict, total=False):
    pipelineName: str
    """``AWS::IoTAnalytics::Pipeline.PipelineName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-pipelinename
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::IoTAnalytics::Pipeline.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipelineProps", jsii_struct_bases=[_CfnPipelineProps])
class CfnPipelineProps(_CfnPipelineProps):
    """Properties for defining a ``AWS::IoTAnalytics::Pipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html
    Stability:
        stable
    """
    pipelineActivities: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.ActivityProperty"]]]
    """``AWS::IoTAnalytics::Pipeline.PipelineActivities``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-pipelineactivities
    Stability:
        stable
    """

__all__ = ["CfnChannel", "CfnChannelProps", "CfnDataset", "CfnDatasetProps", "CfnDatastore", "CfnDatastoreProps", "CfnPipeline", "CfnPipelineProps", "__jsii_assembly__"]

publication.publish()
