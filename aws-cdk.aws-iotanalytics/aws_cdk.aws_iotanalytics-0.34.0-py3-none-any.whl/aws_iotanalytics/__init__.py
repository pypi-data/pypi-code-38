import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-iotanalytics", "0.34.0", __name__, "aws-iotanalytics@0.34.0.jsii.tgz")
class CfnChannel(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotanalytics.CfnChannel"):
    """A CloudFormation ``AWS::IoTAnalytics::Channel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-channel.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoTAnalytics::Channel
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, channel_name: typing.Optional[str]=None, retention_period: typing.Optional[typing.Union[typing.Optional["RetentionPeriodProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
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
    @jsii.member(jsii_name="channelId")
    def channel_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "channelId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnChannelProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnChannel.RetentionPeriodProperty", jsii_struct_bases=[])
    class RetentionPeriodProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-channel-retentionperiod.html
        Stability:
            experimental
        """
        numberOfDays: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnChannel.RetentionPeriodProperty.NumberOfDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-channel-retentionperiod.html#cfn-iotanalytics-channel-retentionperiod-numberofdays
        Stability:
            experimental
        """

        unlimited: typing.Union[bool, aws_cdk.cdk.Token]
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

    retentionPeriod: typing.Union["CfnChannel.RetentionPeriodProperty", aws_cdk.cdk.Token]
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, actions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "ActionProperty"]]], dataset_name: typing.Optional[str]=None, retention_period: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["RetentionPeriodProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, triggers: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "TriggerProperty"]]]]]=None) -> None:
        """Create a new ``AWS::IoTAnalytics::Dataset``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            actions: ``AWS::IoTAnalytics::Dataset.Actions``.
            datasetName: ``AWS::IoTAnalytics::Dataset.DatasetName``.
            retentionPeriod: ``AWS::IoTAnalytics::Dataset.RetentionPeriod``.
            tags: ``AWS::IoTAnalytics::Dataset.Tags``.
            triggers: ``AWS::IoTAnalytics::Dataset.Triggers``.

        Stability:
            experimental
        """
        props: CfnDatasetProps = {"actions": actions}

        if dataset_name is not None:
            props["datasetName"] = dataset_name

        if retention_period is not None:
            props["retentionPeriod"] = retention_period

        if tags is not None:
            props["tags"] = tags

        if triggers is not None:
            props["triggers"] = triggers

        jsii.create(CfnDataset, self, [scope, id, props])

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
    @jsii.member(jsii_name="datasetId")
    def dataset_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "datasetId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDatasetProps":
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

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ActionProperty(jsii.compat.TypedDict, total=False):
        containerAction: typing.Union[aws_cdk.cdk.Token, "CfnDataset.ContainerActionProperty"]
        """``CfnDataset.ActionProperty.ContainerAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-action.html#cfn-iotanalytics-dataset-action-containeraction
        Stability:
            experimental
        """
        queryAction: typing.Union[aws_cdk.cdk.Token, "CfnDataset.QueryActionProperty"]
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
        variables: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDataset.VariableProperty"]]]
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

        resourceConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDataset.ResourceConfigurationProperty"]
        """``CfnDataset.ContainerActionProperty.ResourceConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-containeraction.html#cfn-iotanalytics-dataset-containeraction-resourceconfiguration
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
        offsetSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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
        deltaTime: typing.Union[aws_cdk.cdk.Token, "CfnDataset.DeltaTimeProperty"]
        """``CfnDataset.FilterProperty.DeltaTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-filter.html#cfn-iotanalytics-dataset-filter-deltatime
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
        filters: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDataset.FilterProperty"]]]
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

        volumeSizeInGb: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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
        numberOfDays: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDataset.RetentionPeriodProperty.NumberOfDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-retentionperiod.html#cfn-iotanalytics-dataset-retentionperiod-numberofdays
        Stability:
            experimental
        """

        unlimited: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDataset.RetentionPeriodProperty.Unlimited``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-retentionperiod.html#cfn-iotanalytics-dataset-retentionperiod-unlimited
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
        schedule: typing.Union[aws_cdk.cdk.Token, "CfnDataset.ScheduleProperty"]
        """``CfnDataset.TriggerProperty.Schedule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-trigger.html#cfn-iotanalytics-dataset-trigger-schedule
        Stability:
            experimental
        """

        triggeringDataset: typing.Union[aws_cdk.cdk.Token, "CfnDataset.TriggeringDatasetProperty"]
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
        datasetContentVersionValue: typing.Union[aws_cdk.cdk.Token, "CfnDataset.DatasetContentVersionValueProperty"]
        """``CfnDataset.VariableProperty.DatasetContentVersionValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html#cfn-iotanalytics-dataset-variable-datasetcontentversionvalue
        Stability:
            experimental
        """
        doubleValue: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDataset.VariableProperty.DoubleValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-dataset-variable.html#cfn-iotanalytics-dataset-variable-doublevalue
        Stability:
            experimental
        """
        outputFileUriValue: typing.Union[aws_cdk.cdk.Token, "CfnDataset.OutputFileUriValueProperty"]
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


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDatasetProps(jsii.compat.TypedDict, total=False):
    datasetName: str
    """``AWS::IoTAnalytics::Dataset.DatasetName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-datasetname
    Stability:
        experimental
    """
    retentionPeriod: typing.Union[aws_cdk.cdk.Token, "CfnDataset.RetentionPeriodProperty"]
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
    triggers: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDataset.TriggerProperty"]]]
    """``AWS::IoTAnalytics::Dataset.Triggers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-dataset.html#cfn-iotanalytics-dataset-triggers
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
    actions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDataset.ActionProperty"]]]
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, datastore_name: typing.Optional[str]=None, retention_period: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["RetentionPeriodProperty"]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
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
    @jsii.member(jsii_name="datastoreId")
    def datastore_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "datastoreId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDatastoreProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnDatastore.RetentionPeriodProperty", jsii_struct_bases=[])
    class RetentionPeriodProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-datastore-retentionperiod.html
        Stability:
            experimental
        """
        numberOfDays: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDatastore.RetentionPeriodProperty.NumberOfDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-datastore-retentionperiod.html#cfn-iotanalytics-datastore-retentionperiod-numberofdays
        Stability:
            experimental
        """

        unlimited: typing.Union[bool, aws_cdk.cdk.Token]
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

    retentionPeriod: typing.Union[aws_cdk.cdk.Token, "CfnDatastore.RetentionPeriodProperty"]
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, pipeline_activities: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "ActivityProperty"]]], pipeline_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
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
    @jsii.member(jsii_name="pipelineId")
    def pipeline_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "pipelineId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnPipelineProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-iotanalytics.CfnPipeline.ActivityProperty", jsii_struct_bases=[])
    class ActivityProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html
        Stability:
            experimental
        """
        addAttributes: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.AddAttributesProperty"]
        """``CfnPipeline.ActivityProperty.AddAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-addattributes
        Stability:
            experimental
        """

        channel: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.ChannelProperty"]
        """``CfnPipeline.ActivityProperty.Channel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-channel
        Stability:
            experimental
        """

        datastore: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.DatastoreProperty"]
        """``CfnPipeline.ActivityProperty.Datastore``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-datastore
        Stability:
            experimental
        """

        deviceRegistryEnrich: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.DeviceRegistryEnrichProperty"]
        """``CfnPipeline.ActivityProperty.DeviceRegistryEnrich``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-deviceregistryenrich
        Stability:
            experimental
        """

        deviceShadowEnrich: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.DeviceShadowEnrichProperty"]
        """``CfnPipeline.ActivityProperty.DeviceShadowEnrich``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-deviceshadowenrich
        Stability:
            experimental
        """

        filter: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.FilterProperty"]
        """``CfnPipeline.ActivityProperty.Filter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-filter
        Stability:
            experimental
        """

        lambda_: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.LambdaProperty"]
        """``CfnPipeline.ActivityProperty.Lambda``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-lambda
        Stability:
            experimental
        """

        math: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.MathProperty"]
        """``CfnPipeline.ActivityProperty.Math``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-math
        Stability:
            experimental
        """

        removeAttributes: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.RemoveAttributesProperty"]
        """``CfnPipeline.ActivityProperty.RemoveAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotanalytics-pipeline-activity.html#cfn-iotanalytics-pipeline-activity-removeattributes
        Stability:
            experimental
        """

        selectAttributes: typing.Union[aws_cdk.cdk.Token, "CfnPipeline.SelectAttributesProperty"]
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
        attributes: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
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
        batchSize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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
    pipelineActivities: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPipeline.ActivityProperty"]]]
    """``AWS::IoTAnalytics::Pipeline.PipelineActivities``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotanalytics-pipeline.html#cfn-iotanalytics-pipeline-pipelineactivities
    Stability:
        experimental
    """

__all__ = ["CfnChannel", "CfnChannelProps", "CfnDataset", "CfnDatasetProps", "CfnDatastore", "CfnDatastoreProps", "CfnPipeline", "CfnPipelineProps", "__jsii_assembly__"]

publication.publish()
