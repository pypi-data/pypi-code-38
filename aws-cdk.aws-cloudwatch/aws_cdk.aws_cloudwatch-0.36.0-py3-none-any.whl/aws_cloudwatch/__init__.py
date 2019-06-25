import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_iam
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-cloudwatch", "0.36.0", __name__, "aws-cloudwatch@0.36.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.AlarmActionConfig", jsii_struct_bases=[])
class AlarmActionConfig(jsii.compat.TypedDict):
    """Properties for an alarm action.

    Stability:
        experimental
    """
    alarmActionArn: str
    """Return the ARN that should be used for a CloudWatch Alarm action.

    Stability:
        experimental
    """

class CfnAlarm(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch.CfnAlarm"):
    """A CloudFormation ``AWS::CloudWatch::Alarm``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html
    Stability:
        stable
    cloudformationResource:
        AWS::CloudWatch::Alarm
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, comparison_operator: str, evaluation_periods: jsii.Number, threshold: jsii.Number, actions_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, alarm_actions: typing.Optional[typing.List[str]]=None, alarm_description: typing.Optional[str]=None, alarm_name: typing.Optional[str]=None, datapoints_to_alarm: typing.Optional[jsii.Number]=None, dimensions: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "DimensionProperty"]]]]]=None, evaluate_low_sample_count_percentile: typing.Optional[str]=None, extended_statistic: typing.Optional[str]=None, insufficient_data_actions: typing.Optional[typing.List[str]]=None, metric_name: typing.Optional[str]=None, metrics: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "MetricDataQueryProperty"]]]]]=None, namespace: typing.Optional[str]=None, ok_actions: typing.Optional[typing.List[str]]=None, period: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, treat_missing_data: typing.Optional[str]=None, unit: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::CloudWatch::Alarm``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            comparison_operator: ``AWS::CloudWatch::Alarm.ComparisonOperator``.
            evaluation_periods: ``AWS::CloudWatch::Alarm.EvaluationPeriods``.
            threshold: ``AWS::CloudWatch::Alarm.Threshold``.
            actions_enabled: ``AWS::CloudWatch::Alarm.ActionsEnabled``.
            alarm_actions: ``AWS::CloudWatch::Alarm.AlarmActions``.
            alarm_description: ``AWS::CloudWatch::Alarm.AlarmDescription``.
            alarm_name: ``AWS::CloudWatch::Alarm.AlarmName``.
            datapoints_to_alarm: ``AWS::CloudWatch::Alarm.DatapointsToAlarm``.
            dimensions: ``AWS::CloudWatch::Alarm.Dimensions``.
            evaluate_low_sample_count_percentile: ``AWS::CloudWatch::Alarm.EvaluateLowSampleCountPercentile``.
            extended_statistic: ``AWS::CloudWatch::Alarm.ExtendedStatistic``.
            insufficient_data_actions: ``AWS::CloudWatch::Alarm.InsufficientDataActions``.
            metric_name: ``AWS::CloudWatch::Alarm.MetricName``.
            metrics: ``AWS::CloudWatch::Alarm.Metrics``.
            namespace: ``AWS::CloudWatch::Alarm.Namespace``.
            ok_actions: ``AWS::CloudWatch::Alarm.OKActions``.
            period: ``AWS::CloudWatch::Alarm.Period``.
            statistic: ``AWS::CloudWatch::Alarm.Statistic``.
            treat_missing_data: ``AWS::CloudWatch::Alarm.TreatMissingData``.
            unit: ``AWS::CloudWatch::Alarm.Unit``.

        Stability:
            experimental
        """
        props: CfnAlarmProps = {"comparisonOperator": comparison_operator, "evaluationPeriods": evaluation_periods, "threshold": threshold}

        if actions_enabled is not None:
            props["actionsEnabled"] = actions_enabled

        if alarm_actions is not None:
            props["alarmActions"] = alarm_actions

        if alarm_description is not None:
            props["alarmDescription"] = alarm_description

        if alarm_name is not None:
            props["alarmName"] = alarm_name

        if datapoints_to_alarm is not None:
            props["datapointsToAlarm"] = datapoints_to_alarm

        if dimensions is not None:
            props["dimensions"] = dimensions

        if evaluate_low_sample_count_percentile is not None:
            props["evaluateLowSampleCountPercentile"] = evaluate_low_sample_count_percentile

        if extended_statistic is not None:
            props["extendedStatistic"] = extended_statistic

        if insufficient_data_actions is not None:
            props["insufficientDataActions"] = insufficient_data_actions

        if metric_name is not None:
            props["metricName"] = metric_name

        if metrics is not None:
            props["metrics"] = metrics

        if namespace is not None:
            props["namespace"] = namespace

        if ok_actions is not None:
            props["okActions"] = ok_actions

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if treat_missing_data is not None:
            props["treatMissingData"] = treat_missing_data

        if unit is not None:
            props["unit"] = unit

        jsii.create(CfnAlarm, self, [scope, id, props])

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
    @jsii.member(jsii_name="comparisonOperator")
    def comparison_operator(self) -> str:
        """``AWS::CloudWatch::Alarm.ComparisonOperator``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-comparisonoperator
        Stability:
            stable
        """
        return jsii.get(self, "comparisonOperator")

    @comparison_operator.setter
    def comparison_operator(self, value: str):
        return jsii.set(self, "comparisonOperator", value)

    @property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        """``AWS::CloudWatch::Alarm.EvaluationPeriods``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-evaluationperiods
        Stability:
            stable
        """
        return jsii.get(self, "evaluationPeriods")

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number):
        return jsii.set(self, "evaluationPeriods", value)

    @property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        """``AWS::CloudWatch::Alarm.Threshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-threshold
        Stability:
            stable
        """
        return jsii.get(self, "threshold")

    @threshold.setter
    def threshold(self, value: jsii.Number):
        return jsii.set(self, "threshold", value)

    @property
    @jsii.member(jsii_name="actionsEnabled")
    def actions_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::CloudWatch::Alarm.ActionsEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-actionsenabled
        Stability:
            stable
        """
        return jsii.get(self, "actionsEnabled")

    @actions_enabled.setter
    def actions_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "actionsEnabled", value)

    @property
    @jsii.member(jsii_name="alarmActions")
    def alarm_actions(self) -> typing.Optional[typing.List[str]]:
        """``AWS::CloudWatch::Alarm.AlarmActions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-alarmactions
        Stability:
            stable
        """
        return jsii.get(self, "alarmActions")

    @alarm_actions.setter
    def alarm_actions(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "alarmActions", value)

    @property
    @jsii.member(jsii_name="alarmDescription")
    def alarm_description(self) -> typing.Optional[str]:
        """``AWS::CloudWatch::Alarm.AlarmDescription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-alarmdescription
        Stability:
            stable
        """
        return jsii.get(self, "alarmDescription")

    @alarm_description.setter
    def alarm_description(self, value: typing.Optional[str]):
        return jsii.set(self, "alarmDescription", value)

    @property
    @jsii.member(jsii_name="alarmName")
    def alarm_name(self) -> typing.Optional[str]:
        """``AWS::CloudWatch::Alarm.AlarmName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-alarmname
        Stability:
            stable
        """
        return jsii.get(self, "alarmName")

    @alarm_name.setter
    def alarm_name(self, value: typing.Optional[str]):
        return jsii.set(self, "alarmName", value)

    @property
    @jsii.member(jsii_name="datapointsToAlarm")
    def datapoints_to_alarm(self) -> typing.Optional[jsii.Number]:
        """``AWS::CloudWatch::Alarm.DatapointsToAlarm``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarm-datapointstoalarm
        Stability:
            stable
        """
        return jsii.get(self, "datapointsToAlarm")

    @datapoints_to_alarm.setter
    def datapoints_to_alarm(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "datapointsToAlarm", value)

    @property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "DimensionProperty"]]]]]:
        """``AWS::CloudWatch::Alarm.Dimensions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-dimension
        Stability:
            stable
        """
        return jsii.get(self, "dimensions")

    @dimensions.setter
    def dimensions(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "DimensionProperty"]]]]]):
        return jsii.set(self, "dimensions", value)

    @property
    @jsii.member(jsii_name="evaluateLowSampleCountPercentile")
    def evaluate_low_sample_count_percentile(self) -> typing.Optional[str]:
        """``AWS::CloudWatch::Alarm.EvaluateLowSampleCountPercentile``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-evaluatelowsamplecountpercentile
        Stability:
            stable
        """
        return jsii.get(self, "evaluateLowSampleCountPercentile")

    @evaluate_low_sample_count_percentile.setter
    def evaluate_low_sample_count_percentile(self, value: typing.Optional[str]):
        return jsii.set(self, "evaluateLowSampleCountPercentile", value)

    @property
    @jsii.member(jsii_name="extendedStatistic")
    def extended_statistic(self) -> typing.Optional[str]:
        """``AWS::CloudWatch::Alarm.ExtendedStatistic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-extendedstatistic
        Stability:
            stable
        """
        return jsii.get(self, "extendedStatistic")

    @extended_statistic.setter
    def extended_statistic(self, value: typing.Optional[str]):
        return jsii.set(self, "extendedStatistic", value)

    @property
    @jsii.member(jsii_name="insufficientDataActions")
    def insufficient_data_actions(self) -> typing.Optional[typing.List[str]]:
        """``AWS::CloudWatch::Alarm.InsufficientDataActions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-insufficientdataactions
        Stability:
            stable
        """
        return jsii.get(self, "insufficientDataActions")

    @insufficient_data_actions.setter
    def insufficient_data_actions(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "insufficientDataActions", value)

    @property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> typing.Optional[str]:
        """``AWS::CloudWatch::Alarm.MetricName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-metricname
        Stability:
            stable
        """
        return jsii.get(self, "metricName")

    @metric_name.setter
    def metric_name(self, value: typing.Optional[str]):
        return jsii.set(self, "metricName", value)

    @property
    @jsii.member(jsii_name="metrics")
    def metrics(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "MetricDataQueryProperty"]]]]]:
        """``AWS::CloudWatch::Alarm.Metrics``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarm-metrics
        Stability:
            stable
        """
        return jsii.get(self, "metrics")

    @metrics.setter
    def metrics(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "MetricDataQueryProperty"]]]]]):
        return jsii.set(self, "metrics", value)

    @property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> typing.Optional[str]:
        """``AWS::CloudWatch::Alarm.Namespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-namespace
        Stability:
            stable
        """
        return jsii.get(self, "namespace")

    @namespace.setter
    def namespace(self, value: typing.Optional[str]):
        return jsii.set(self, "namespace", value)

    @property
    @jsii.member(jsii_name="okActions")
    def ok_actions(self) -> typing.Optional[typing.List[str]]:
        """``AWS::CloudWatch::Alarm.OKActions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-okactions
        Stability:
            stable
        """
        return jsii.get(self, "okActions")

    @ok_actions.setter
    def ok_actions(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "okActions", value)

    @property
    @jsii.member(jsii_name="period")
    def period(self) -> typing.Optional[jsii.Number]:
        """``AWS::CloudWatch::Alarm.Period``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-period
        Stability:
            stable
        """
        return jsii.get(self, "period")

    @period.setter
    def period(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "period", value)

    @property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> typing.Optional[str]:
        """``AWS::CloudWatch::Alarm.Statistic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-statistic
        Stability:
            stable
        """
        return jsii.get(self, "statistic")

    @statistic.setter
    def statistic(self, value: typing.Optional[str]):
        return jsii.set(self, "statistic", value)

    @property
    @jsii.member(jsii_name="treatMissingData")
    def treat_missing_data(self) -> typing.Optional[str]:
        """``AWS::CloudWatch::Alarm.TreatMissingData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-treatmissingdata
        Stability:
            stable
        """
        return jsii.get(self, "treatMissingData")

    @treat_missing_data.setter
    def treat_missing_data(self, value: typing.Optional[str]):
        return jsii.set(self, "treatMissingData", value)

    @property
    @jsii.member(jsii_name="unit")
    def unit(self) -> typing.Optional[str]:
        """``AWS::CloudWatch::Alarm.Unit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-unit
        Stability:
            stable
        """
        return jsii.get(self, "unit")

    @unit.setter
    def unit(self, value: typing.Optional[str]):
        return jsii.set(self, "unit", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.CfnAlarm.DimensionProperty", jsii_struct_bases=[])
    class DimensionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-dimension.html
        Stability:
            stable
        """
        name: str
        """``CfnAlarm.DimensionProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-dimension.html#cfn-cloudwatch-alarm-dimension-name
        Stability:
            stable
        """

        value: str
        """``CfnAlarm.DimensionProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-dimension.html#cfn-cloudwatch-alarm-dimension-value
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _MetricDataQueryProperty(jsii.compat.TypedDict, total=False):
        expression: str
        """``CfnAlarm.MetricDataQueryProperty.Expression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metricdataquery.html#cfn-cloudwatch-alarm-metricdataquery-expression
        Stability:
            stable
        """
        label: str
        """``CfnAlarm.MetricDataQueryProperty.Label``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metricdataquery.html#cfn-cloudwatch-alarm-metricdataquery-label
        Stability:
            stable
        """
        metricStat: typing.Union[aws_cdk.core.IResolvable, "CfnAlarm.MetricStatProperty"]
        """``CfnAlarm.MetricDataQueryProperty.MetricStat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metricdataquery.html#cfn-cloudwatch-alarm-metricdataquery-metricstat
        Stability:
            stable
        """
        returnData: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnAlarm.MetricDataQueryProperty.ReturnData``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metricdataquery.html#cfn-cloudwatch-alarm-metricdataquery-returndata
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.CfnAlarm.MetricDataQueryProperty", jsii_struct_bases=[_MetricDataQueryProperty])
    class MetricDataQueryProperty(_MetricDataQueryProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metricdataquery.html
        Stability:
            stable
        """
        id: str
        """``CfnAlarm.MetricDataQueryProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metricdataquery.html#cfn-cloudwatch-alarm-metricdataquery-id
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.CfnAlarm.MetricProperty", jsii_struct_bases=[])
    class MetricProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metric.html
        Stability:
            stable
        """
        dimensions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnAlarm.DimensionProperty"]]]
        """``CfnAlarm.MetricProperty.Dimensions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metric.html#cfn-cloudwatch-alarm-metric-dimensions
        Stability:
            stable
        """

        metricName: str
        """``CfnAlarm.MetricProperty.MetricName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metric.html#cfn-cloudwatch-alarm-metric-metricname
        Stability:
            stable
        """

        namespace: str
        """``CfnAlarm.MetricProperty.Namespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metric.html#cfn-cloudwatch-alarm-metric-namespace
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _MetricStatProperty(jsii.compat.TypedDict, total=False):
        unit: str
        """``CfnAlarm.MetricStatProperty.Unit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metricstat.html#cfn-cloudwatch-alarm-metricstat-unit
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.CfnAlarm.MetricStatProperty", jsii_struct_bases=[_MetricStatProperty])
    class MetricStatProperty(_MetricStatProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metricstat.html
        Stability:
            stable
        """
        metric: typing.Union[aws_cdk.core.IResolvable, "CfnAlarm.MetricProperty"]
        """``CfnAlarm.MetricStatProperty.Metric``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metricstat.html#cfn-cloudwatch-alarm-metricstat-metric
        Stability:
            stable
        """

        period: jsii.Number
        """``CfnAlarm.MetricStatProperty.Period``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metricstat.html#cfn-cloudwatch-alarm-metricstat-period
        Stability:
            stable
        """

        stat: str
        """``CfnAlarm.MetricStatProperty.Stat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudwatch-alarm-metricstat.html#cfn-cloudwatch-alarm-metricstat-stat
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAlarmProps(jsii.compat.TypedDict, total=False):
    actionsEnabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::CloudWatch::Alarm.ActionsEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-actionsenabled
    Stability:
        stable
    """
    alarmActions: typing.List[str]
    """``AWS::CloudWatch::Alarm.AlarmActions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-alarmactions
    Stability:
        stable
    """
    alarmDescription: str
    """``AWS::CloudWatch::Alarm.AlarmDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-alarmdescription
    Stability:
        stable
    """
    alarmName: str
    """``AWS::CloudWatch::Alarm.AlarmName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-alarmname
    Stability:
        stable
    """
    datapointsToAlarm: jsii.Number
    """``AWS::CloudWatch::Alarm.DatapointsToAlarm``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarm-datapointstoalarm
    Stability:
        stable
    """
    dimensions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnAlarm.DimensionProperty"]]]
    """``AWS::CloudWatch::Alarm.Dimensions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-dimension
    Stability:
        stable
    """
    evaluateLowSampleCountPercentile: str
    """``AWS::CloudWatch::Alarm.EvaluateLowSampleCountPercentile``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-evaluatelowsamplecountpercentile
    Stability:
        stable
    """
    extendedStatistic: str
    """``AWS::CloudWatch::Alarm.ExtendedStatistic``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-extendedstatistic
    Stability:
        stable
    """
    insufficientDataActions: typing.List[str]
    """``AWS::CloudWatch::Alarm.InsufficientDataActions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-insufficientdataactions
    Stability:
        stable
    """
    metricName: str
    """``AWS::CloudWatch::Alarm.MetricName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-metricname
    Stability:
        stable
    """
    metrics: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnAlarm.MetricDataQueryProperty"]]]
    """``AWS::CloudWatch::Alarm.Metrics``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarm-metrics
    Stability:
        stable
    """
    namespace: str
    """``AWS::CloudWatch::Alarm.Namespace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-namespace
    Stability:
        stable
    """
    okActions: typing.List[str]
    """``AWS::CloudWatch::Alarm.OKActions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-okactions
    Stability:
        stable
    """
    period: jsii.Number
    """``AWS::CloudWatch::Alarm.Period``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-period
    Stability:
        stable
    """
    statistic: str
    """``AWS::CloudWatch::Alarm.Statistic``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-statistic
    Stability:
        stable
    """
    treatMissingData: str
    """``AWS::CloudWatch::Alarm.TreatMissingData``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-treatmissingdata
    Stability:
        stable
    """
    unit: str
    """``AWS::CloudWatch::Alarm.Unit``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-unit
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.CfnAlarmProps", jsii_struct_bases=[_CfnAlarmProps])
class CfnAlarmProps(_CfnAlarmProps):
    """Properties for defining a ``AWS::CloudWatch::Alarm``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html
    Stability:
        stable
    """
    comparisonOperator: str
    """``AWS::CloudWatch::Alarm.ComparisonOperator``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-comparisonoperator
    Stability:
        stable
    """

    evaluationPeriods: jsii.Number
    """``AWS::CloudWatch::Alarm.EvaluationPeriods``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-evaluationperiods
    Stability:
        stable
    """

    threshold: jsii.Number
    """``AWS::CloudWatch::Alarm.Threshold``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html#cfn-cloudwatch-alarms-threshold
    Stability:
        stable
    """

class CfnDashboard(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch.CfnDashboard"):
    """A CloudFormation ``AWS::CloudWatch::Dashboard``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudwatch-dashboard.html
    Stability:
        stable
    cloudformationResource:
        AWS::CloudWatch::Dashboard
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, dashboard_body: str, dashboard_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::CloudWatch::Dashboard``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            dashboard_body: ``AWS::CloudWatch::Dashboard.DashboardBody``.
            dashboard_name: ``AWS::CloudWatch::Dashboard.DashboardName``.

        Stability:
            experimental
        """
        props: CfnDashboardProps = {"dashboardBody": dashboard_body}

        if dashboard_name is not None:
            props["dashboardName"] = dashboard_name

        jsii.create(CfnDashboard, self, [scope, id, props])

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
    @jsii.member(jsii_name="dashboardBody")
    def dashboard_body(self) -> str:
        """``AWS::CloudWatch::Dashboard.DashboardBody``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudwatch-dashboard.html#cfn-cloudwatch-dashboard-dashboardbody
        Stability:
            stable
        """
        return jsii.get(self, "dashboardBody")

    @dashboard_body.setter
    def dashboard_body(self, value: str):
        return jsii.set(self, "dashboardBody", value)

    @property
    @jsii.member(jsii_name="dashboardName")
    def dashboard_name(self) -> typing.Optional[str]:
        """``AWS::CloudWatch::Dashboard.DashboardName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudwatch-dashboard.html#cfn-cloudwatch-dashboard-dashboardname
        Stability:
            stable
        """
        return jsii.get(self, "dashboardName")

    @dashboard_name.setter
    def dashboard_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dashboardName", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDashboardProps(jsii.compat.TypedDict, total=False):
    dashboardName: str
    """``AWS::CloudWatch::Dashboard.DashboardName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudwatch-dashboard.html#cfn-cloudwatch-dashboard-dashboardname
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.CfnDashboardProps", jsii_struct_bases=[_CfnDashboardProps])
class CfnDashboardProps(_CfnDashboardProps):
    """Properties for defining a ``AWS::CloudWatch::Dashboard``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudwatch-dashboard.html
    Stability:
        stable
    """
    dashboardBody: str
    """``AWS::CloudWatch::Dashboard.DashboardBody``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudwatch-dashboard.html#cfn-cloudwatch-dashboard-dashboardbody
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.CommonMetricOptions", jsii_struct_bases=[])
class CommonMetricOptions(jsii.compat.TypedDict, total=False):
    """Options shared by most methods accepting metric options.

    Stability:
        experimental
    """
    color: str
    """Color for this metric when added to a Graph in a Dashboard.

    Stability:
        experimental
    """

    dimensions: typing.Mapping[str,typing.Any]
    """Dimensions of the metric.

    Default:
        - No dimensions.

    Stability:
        experimental
    """

    label: str
    """Label for this metric when added to a Graph in a Dashboard.

    Stability:
        experimental
    """

    period: aws_cdk.core.Duration
    """The period over which the specified statistic is applied.

    Default:
        Duration.minutes(5)

    Stability:
        experimental
    """

    statistic: str
    """What function to use for aggregating.

    Can be one of the following:

    - "Minimum" | "min"
    - "Maximum" | "max"
    - "Average" | "avg"
    - "Sum" | "sum"
    - "SampleCount | "n"
    - "pNN.NN"

    Default:
        Average

    Stability:
        experimental
    """

    unit: "Unit"
    """Unit for the metric that is associated with the alarm.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-cloudwatch.ComparisonOperator")
class ComparisonOperator(enum.Enum):
    """Comparison operator for evaluating alarms.

    Stability:
        experimental
    """
    GREATER_THAN_OR_EQUAL_TO_THRESHOLD = "GREATER_THAN_OR_EQUAL_TO_THRESHOLD"
    """
    Stability:
        experimental
    """
    GREATER_THAN_THRESHOLD = "GREATER_THAN_THRESHOLD"
    """
    Stability:
        experimental
    """
    LESS_THAN_THRESHOLD = "LESS_THAN_THRESHOLD"
    """
    Stability:
        experimental
    """
    LESS_THAN_OR_EQUAL_TO_THRESHOLD = "LESS_THAN_OR_EQUAL_TO_THRESHOLD"
    """
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CreateAlarmOptions(jsii.compat.TypedDict, total=False):
    actionsEnabled: bool
    """Whether the actions for this alarm are enabled.

    Default:
        true

    Stability:
        experimental
    """
    alarmDescription: str
    """Description for the alarm.

    Default:
        No description

    Stability:
        experimental
    """
    alarmName: str
    """Name of the alarm.

    Default:
        Automatically generated name

    Stability:
        experimental
    """
    comparisonOperator: "ComparisonOperator"
    """Comparison to use to check if metric is breaching.

    Default:
        GreaterThanOrEqualToThreshold

    Stability:
        experimental
    """
    datapointsToAlarm: jsii.Number
    """The number of datapoints that must be breaching to trigger the alarm.

    This is used only if you are setting an "M
    out of N" alarm. In that case, this value is the M. For more information, see Evaluating an Alarm in the Amazon
    CloudWatch User Guide.

    Default:
        ``evaluationPeriods``

    See:
        https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html#alarm-evaluation
    Stability:
        experimental
    """
    evaluateLowSampleCountPercentile: str
    """Specifies whether to evaluate the data and potentially change the alarm state if there are too few data points to be statistically significant.

    Used only for alarms that are based on percentiles.

    Default:
        - Not configured.

    Stability:
        experimental
    """
    period: aws_cdk.core.Duration
    """The period over which the specified statistic is applied.

    Default:
        Duration.minutes(5)

    Stability:
        experimental
    """
    statistic: str
    """What function to use for aggregating.

    Can be one of the following:

    - "Minimum" | "min"
    - "Maximum" | "max"
    - "Average" | "avg"
    - "Sum" | "sum"
    - "SampleCount | "n"
    - "pNN.NN"

    Default:
        Average

    Stability:
        experimental
    """
    treatMissingData: "TreatMissingData"
    """Sets how this alarm is to handle missing data points.

    Default:
        TreatMissingData.Missing

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.CreateAlarmOptions", jsii_struct_bases=[_CreateAlarmOptions])
class CreateAlarmOptions(_CreateAlarmOptions):
    """Properties needed to make an alarm from a metric.

    Stability:
        experimental
    """
    evaluationPeriods: jsii.Number
    """The number of periods over which data is compared to the specified threshold.

    Stability:
        experimental
    """

    threshold: jsii.Number
    """The value against which the specified statistic is compared.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.AlarmProps", jsii_struct_bases=[CreateAlarmOptions])
class AlarmProps(CreateAlarmOptions, jsii.compat.TypedDict):
    """Properties for Alarms.

    Stability:
        experimental
    """
    metric: "IMetric"
    """The metric to add the alarm on.

    Metric objects can be obtained from most resources, or you can construct
    custom Metric objects by instantiating one.

    Stability:
        experimental
    """

class Dashboard(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch.Dashboard"):
    """A CloudWatch dashboard.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, dashboard_name: typing.Optional[str]=None, end: typing.Optional[str]=None, period_override: typing.Optional["PeriodOverride"]=None, start: typing.Optional[str]=None, widgets: typing.Optional[typing.List[typing.List["IWidget"]]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            dashboard_name: Name of the dashboard. Default: Automatically generated name
            end: The end of the time range to use for each widget on the dashboard when the dashboard loads. If you specify a value for end, you must also specify a value for start. Specify an absolute time in the ISO 8601 format. For example, 2018-12-17T06:00:00.000Z. Default: When the dashboard loads, the end date will be the current time.
            period_override: Use this field to specify the period for the graphs when the dashboard loads. Specifying ``Auto`` causes the period of all graphs on the dashboard to automatically adapt to the time range of the dashboard. Specifying ``Inherit`` ensures that the period set for each graph is always obeyed. Default: Auto
            start: The start of the time range to use for each widget on the dashboard. You can specify start without specifying end to specify a relative time range that ends with the current time. In this case, the value of start must begin with -P, and you can use M, H, D, W and M as abbreviations for minutes, hours, days, weeks and months. For example, -PT8H shows the last 8 hours and -P3M shows the last three months. You can also use start along with an end field, to specify an absolute time range. When specifying an absolute time range, use the ISO 8601 format. For example, 2018-12-17T06:00:00.000Z. Default: When the dashboard loads, the start time will be the default time range.
            widgets: Initial set of widgets on the dashboard. One array represents a row of widgets. Default: - No widgets

        Stability:
            experimental
        """
        props: DashboardProps = {}

        if dashboard_name is not None:
            props["dashboardName"] = dashboard_name

        if end is not None:
            props["end"] = end

        if period_override is not None:
            props["periodOverride"] = period_override

        if start is not None:
            props["start"] = start

        if widgets is not None:
            props["widgets"] = widgets

        jsii.create(Dashboard, self, [scope, id, props])

    @jsii.member(jsii_name="addWidgets")
    def add_widgets(self, *widgets: "IWidget") -> None:
        """Add a widget to the dashboard.

        Widgets given in multiple calls to add() will be laid out stacked on
        top of each other.

        Multiple widgets added in the same call to add() will be laid out next
        to each other.

        Arguments:
            widgets: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addWidgets", [*widgets])


@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.DashboardProps", jsii_struct_bases=[])
class DashboardProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    dashboardName: str
    """Name of the dashboard.

    Default:
        Automatically generated name

    Stability:
        experimental
    """

    end: str
    """The end of the time range to use for each widget on the dashboard when the dashboard loads. If you specify a value for end, you must also specify a value for start. Specify an absolute time in the ISO 8601 format. For example, 2018-12-17T06:00:00.000Z.

    Default:
        When the dashboard loads, the end date will be the current time.

    Stability:
        experimental
    """

    periodOverride: "PeriodOverride"
    """Use this field to specify the period for the graphs when the dashboard loads. Specifying ``Auto`` causes the period of all graphs on the dashboard to automatically adapt to the time range of the dashboard. Specifying ``Inherit`` ensures that the period set for each graph is always obeyed.

    Default:
        Auto

    Stability:
        experimental
    """

    start: str
    """The start of the time range to use for each widget on the dashboard. You can specify start without specifying end to specify a relative time range that ends with the current time. In this case, the value of start must begin with -P, and you can use M, H, D, W and M as abbreviations for minutes, hours, days, weeks and months. For example, -PT8H shows the last 8 hours and -P3M shows the last three months. You can also use start along with an end field, to specify an absolute time range. When specifying an absolute time range, use the ISO 8601 format. For example, 2018-12-17T06:00:00.000Z.

    Default:
        When the dashboard loads, the start time will be the default time range.

    Stability:
        experimental
    """

    widgets: typing.List[typing.List["IWidget"]]
    """Initial set of widgets on the dashboard.

    One array represents a row of widgets.

    Default:
        - No widgets

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.Dimension", jsii_struct_bases=[])
class Dimension(jsii.compat.TypedDict):
    """Metric dimension.

    Stability:
        experimental
    """
    name: str
    """Name of the dimension.

    Stability:
        experimental
    """

    value: typing.Any
    """Value of the dimension.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _HorizontalAnnotation(jsii.compat.TypedDict, total=False):
    color: str
    """Hex color code to be used for the annotation.

    Default:
        Automatic color

    Stability:
        experimental
    """
    fill: "Shading"
    """Add shading above or below the annotation.

    Default:
        No shading

    Stability:
        experimental
    """
    label: str
    """Label for the annotation.

    Default:
        No label

    Stability:
        experimental
    """
    visible: bool
    """Whether the annotation is visible.

    Default:
        true

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.HorizontalAnnotation", jsii_struct_bases=[_HorizontalAnnotation])
class HorizontalAnnotation(_HorizontalAnnotation):
    """Horizontal annotation to be added to a graph.

    Stability:
        experimental
    """
    value: jsii.Number
    """The value of the annotation.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-cloudwatch.IAlarm")
class IAlarm(aws_cdk.core.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IAlarmProxy

    @property
    @jsii.member(jsii_name="alarmArn")
    def alarm_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="alarmName")
    def alarm_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IAlarmProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-cloudwatch.IAlarm"
    @property
    @jsii.member(jsii_name="alarmArn")
    def alarm_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "alarmArn")

    @property
    @jsii.member(jsii_name="alarmName")
    def alarm_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "alarmName")


@jsii.implements(IAlarm)
class Alarm(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch.Alarm"):
    """An alarm on a CloudWatch metric.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, metric: "IMetric", evaluation_periods: jsii.Number, threshold: jsii.Number, actions_enabled: typing.Optional[bool]=None, alarm_description: typing.Optional[str]=None, alarm_name: typing.Optional[str]=None, comparison_operator: typing.Optional["ComparisonOperator"]=None, datapoints_to_alarm: typing.Optional[jsii.Number]=None, evaluate_low_sample_count_percentile: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, treat_missing_data: typing.Optional["TreatMissingData"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            metric: The metric to add the alarm on. Metric objects can be obtained from most resources, or you can construct custom Metric objects by instantiating one.
            evaluation_periods: The number of periods over which data is compared to the specified threshold.
            threshold: The value against which the specified statistic is compared.
            actions_enabled: Whether the actions for this alarm are enabled. Default: true
            alarm_description: Description for the alarm. Default: No description
            alarm_name: Name of the alarm. Default: Automatically generated name
            comparison_operator: Comparison to use to check if metric is breaching. Default: GreaterThanOrEqualToThreshold
            datapoints_to_alarm: The number of datapoints that must be breaching to trigger the alarm. This is used only if you are setting an "M out of N" alarm. In that case, this value is the M. For more information, see Evaluating an Alarm in the Amazon CloudWatch User Guide. Default: ``evaluationPeriods``
            evaluate_low_sample_count_percentile: Specifies whether to evaluate the data and potentially change the alarm state if there are too few data points to be statistically significant. Used only for alarms that are based on percentiles. Default: - Not configured.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            treat_missing_data: Sets how this alarm is to handle missing data points. Default: TreatMissingData.Missing

        Stability:
            experimental
        """
        props: AlarmProps = {"metric": metric, "evaluationPeriods": evaluation_periods, "threshold": threshold}

        if actions_enabled is not None:
            props["actionsEnabled"] = actions_enabled

        if alarm_description is not None:
            props["alarmDescription"] = alarm_description

        if alarm_name is not None:
            props["alarmName"] = alarm_name

        if comparison_operator is not None:
            props["comparisonOperator"] = comparison_operator

        if datapoints_to_alarm is not None:
            props["datapointsToAlarm"] = datapoints_to_alarm

        if evaluate_low_sample_count_percentile is not None:
            props["evaluateLowSampleCountPercentile"] = evaluate_low_sample_count_percentile

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if treat_missing_data is not None:
            props["treatMissingData"] = treat_missing_data

        jsii.create(Alarm, self, [scope, id, props])

    @jsii.member(jsii_name="fromAlarmArn")
    @classmethod
    def from_alarm_arn(cls, scope: aws_cdk.core.Construct, id: str, alarm_arn: str) -> "IAlarm":
        """
        Arguments:
            scope: -
            id: -
            alarm_arn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromAlarmArn", [scope, id, alarm_arn])

    @jsii.member(jsii_name="addAlarmAction")
    def add_alarm_action(self, *actions: "IAlarmAction") -> None:
        """Trigger this action if the alarm fires.

        Typically the ARN of an SNS topic or ARN of an AutoScaling policy.

        Arguments:
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAlarmAction", [*actions])

    @jsii.member(jsii_name="addInsufficientDataAction")
    def add_insufficient_data_action(self, *actions: "IAlarmAction") -> None:
        """Trigger this action if there is insufficient data to evaluate the alarm.

        Typically the ARN of an SNS topic or ARN of an AutoScaling policy.

        Arguments:
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addInsufficientDataAction", [*actions])

    @jsii.member(jsii_name="addOkAction")
    def add_ok_action(self, *actions: "IAlarmAction") -> None:
        """Trigger this action if the alarm returns from breaching state into ok state.

        Typically the ARN of an SNS topic or ARN of an AutoScaling policy.

        Arguments:
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addOkAction", [*actions])

    @jsii.member(jsii_name="toAnnotation")
    def to_annotation(self) -> "HorizontalAnnotation":
        """Turn this alarm into a horizontal annotation.

        This is useful if you want to represent an Alarm in a non-AlarmWidget.
        An ``AlarmWidget`` can directly show an alarm, but it can only show a
        single alarm and no other metrics. Instead, you can convert the alarm to
        a HorizontalAnnotation and add it as an annotation to another graph.

        This might be useful if:

        - You want to show multiple alarms inside a single graph, for example if
          you have both a "small margin/long period" alarm as well as a
          "large margin/short period" alarm.
        - You want to show an Alarm line in a graph with multiple metrics in it.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toAnnotation", [])

    @property
    @jsii.member(jsii_name="alarmArn")
    def alarm_arn(self) -> str:
        """ARN of this alarm.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "alarmArn")

    @property
    @jsii.member(jsii_name="alarmName")
    def alarm_name(self) -> str:
        """Name of this alarm.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "alarmName")

    @property
    @jsii.member(jsii_name="metric")
    def metric(self) -> "IMetric":
        """The metric object this alarm was based on.

        Stability:
            experimental
        """
        return jsii.get(self, "metric")


@jsii.interface(jsii_type="@aws-cdk/aws-cloudwatch.IAlarmAction")
class IAlarmAction(jsii.compat.Protocol):
    """Interface for objects that can be the targets of CloudWatch alarm actions.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IAlarmActionProxy

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.core.Construct, alarm: "IAlarm") -> "AlarmActionConfig":
        """
        Arguments:
            scope: -
            alarm: -

        Stability:
            experimental
        """
        ...


class _IAlarmActionProxy():
    """Interface for objects that can be the targets of CloudWatch alarm actions.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-cloudwatch.IAlarmAction"
    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.core.Construct, alarm: "IAlarm") -> "AlarmActionConfig":
        """
        Arguments:
            scope: -
            alarm: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [scope, alarm])


@jsii.interface(jsii_type="@aws-cdk/aws-cloudwatch.IMetric")
class IMetric(jsii.compat.Protocol):
    """Interface for metrics.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IMetricProxy

    @jsii.member(jsii_name="toAlarmConfig")
    def to_alarm_config(self) -> "MetricAlarmConfig":
        """Turn this metric object into an alarm configuration.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="toGraphConfig")
    def to_graph_config(self) -> "MetricGraphConfig":
        """Turn this metric object into a graph configuration.

        Stability:
            experimental
        """
        ...


class _IMetricProxy():
    """Interface for metrics.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-cloudwatch.IMetric"
    @jsii.member(jsii_name="toAlarmConfig")
    def to_alarm_config(self) -> "MetricAlarmConfig":
        """Turn this metric object into an alarm configuration.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toAlarmConfig", [])

    @jsii.member(jsii_name="toGraphConfig")
    def to_graph_config(self) -> "MetricGraphConfig":
        """Turn this metric object into a graph configuration.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toGraphConfig", [])


@jsii.interface(jsii_type="@aws-cdk/aws-cloudwatch.IWidget")
class IWidget(jsii.compat.Protocol):
    """A single dashboard widget.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IWidgetProxy

    @property
    @jsii.member(jsii_name="height")
    def height(self) -> jsii.Number:
        """The amount of vertical grid units the widget will take up.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="width")
    def width(self) -> jsii.Number:
        """The amount of horizontal grid units the widget will take up.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="position")
    def position(self, x: jsii.Number, y: jsii.Number) -> None:
        """Place the widget at a given position.

        Arguments:
            x: -
            y: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List[typing.Any]:
        """Return the widget JSON for use in the dashboard.

        Stability:
            experimental
        """
        ...


class _IWidgetProxy():
    """A single dashboard widget.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-cloudwatch.IWidget"
    @property
    @jsii.member(jsii_name="height")
    def height(self) -> jsii.Number:
        """The amount of vertical grid units the widget will take up.

        Stability:
            experimental
        """
        return jsii.get(self, "height")

    @property
    @jsii.member(jsii_name="width")
    def width(self) -> jsii.Number:
        """The amount of horizontal grid units the widget will take up.

        Stability:
            experimental
        """
        return jsii.get(self, "width")

    @jsii.member(jsii_name="position")
    def position(self, x: jsii.Number, y: jsii.Number) -> None:
        """Place the widget at a given position.

        Arguments:
            x: -
            y: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "position", [x, y])

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List[typing.Any]:
        """Return the widget JSON for use in the dashboard.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJson", [])


@jsii.implements(IWidget)
class Column(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch.Column"):
    """A widget that contains other widgets in a vertical column.

    Widgets will be laid out next to each other

    Stability:
        experimental
    """
    def __init__(self, *widgets: "IWidget") -> None:
        """
        Arguments:
            widgets: -

        Stability:
            experimental
        """
        jsii.create(Column, self, [*widgets])

    @jsii.member(jsii_name="position")
    def position(self, x: jsii.Number, y: jsii.Number) -> None:
        """Place the widget at a given position.

        Arguments:
            x: -
            y: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "position", [x, y])

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List[typing.Any]:
        """Return the widget JSON for use in the dashboard.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJson", [])

    @property
    @jsii.member(jsii_name="height")
    def height(self) -> jsii.Number:
        """The amount of vertical grid units the widget will take up.

        Stability:
            experimental
        """
        return jsii.get(self, "height")

    @property
    @jsii.member(jsii_name="width")
    def width(self) -> jsii.Number:
        """The amount of horizontal grid units the widget will take up.

        Stability:
            experimental
        """
        return jsii.get(self, "width")


@jsii.implements(IWidget)
class ConcreteWidget(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-cloudwatch.ConcreteWidget"):
    """A real CloudWatch widget that has its own fixed size and remembers its position.

    This is in contrast to other widgets which exist for layout purposes.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ConcreteWidgetProxy

    def __init__(self, width: jsii.Number, height: jsii.Number) -> None:
        """
        Arguments:
            width: -
            height: -

        Stability:
            experimental
        """
        jsii.create(ConcreteWidget, self, [width, height])

    @jsii.member(jsii_name="position")
    def position(self, x: jsii.Number, y: jsii.Number) -> None:
        """Place the widget at a given position.

        Arguments:
            x: -
            y: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "position", [x, y])

    @jsii.member(jsii_name="toJson")
    @abc.abstractmethod
    def to_json(self) -> typing.List[typing.Any]:
        """Return the widget JSON for use in the dashboard.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="height")
    def height(self) -> jsii.Number:
        """The amount of vertical grid units the widget will take up.

        Stability:
            experimental
        """
        return jsii.get(self, "height")

    @property
    @jsii.member(jsii_name="width")
    def width(self) -> jsii.Number:
        """The amount of horizontal grid units the widget will take up.

        Stability:
            experimental
        """
        return jsii.get(self, "width")

    @property
    @jsii.member(jsii_name="x")
    def _x(self) -> typing.Optional[jsii.Number]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "x")

    @_x.setter
    def _x(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "x", value)

    @property
    @jsii.member(jsii_name="y")
    def _y(self) -> typing.Optional[jsii.Number]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "y")

    @_y.setter
    def _y(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "y", value)


class _ConcreteWidgetProxy(ConcreteWidget):
    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List[typing.Any]:
        """Return the widget JSON for use in the dashboard.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJson", [])


class AlarmWidget(ConcreteWidget, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch.AlarmWidget"):
    """Display the metric associated with an alarm, including the alarm line.

    Stability:
        experimental
    """
    def __init__(self, *, alarm: "Alarm", left_y_axis: typing.Optional["YAxisProps"]=None, height: typing.Optional[jsii.Number]=None, region: typing.Optional[str]=None, title: typing.Optional[str]=None, width: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            props: -
            alarm: The alarm to show.
            left_y_axis: Left Y axis.
            height: Height of the widget. Default: Depends on the type of widget
            region: The region the metrics of this graph should be taken from. Default: Current region
            title: Title for the graph.
            width: Width of the widget, in a grid of 24 units wide. Default: 6

        Stability:
            experimental
        """
        props: AlarmWidgetProps = {"alarm": alarm}

        if left_y_axis is not None:
            props["leftYAxis"] = left_y_axis

        if height is not None:
            props["height"] = height

        if region is not None:
            props["region"] = region

        if title is not None:
            props["title"] = title

        if width is not None:
            props["width"] = width

        jsii.create(AlarmWidget, self, [props])

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List[typing.Any]:
        """Return the widget JSON for use in the dashboard.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJson", [])


class GraphWidget(ConcreteWidget, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch.GraphWidget"):
    """A dashboard widget that displays metrics.

    Stability:
        experimental
    """
    def __init__(self, *, left: typing.Optional[typing.List["IMetric"]]=None, left_annotations: typing.Optional[typing.List["HorizontalAnnotation"]]=None, left_y_axis: typing.Optional["YAxisProps"]=None, right: typing.Optional[typing.List["IMetric"]]=None, right_annotations: typing.Optional[typing.List["HorizontalAnnotation"]]=None, right_y_axis: typing.Optional["YAxisProps"]=None, stacked: typing.Optional[bool]=None, height: typing.Optional[jsii.Number]=None, region: typing.Optional[str]=None, title: typing.Optional[str]=None, width: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            props: -
            left: Metrics to display on left Y axis.
            left_annotations: Annotations for the left Y axis.
            left_y_axis: Left Y axis.
            right: Metrics to display on right Y axis.
            right_annotations: Annotations for the right Y axis.
            right_y_axis: Right Y axis.
            stacked: Whether the graph should be shown as stacked lines.
            height: Height of the widget. Default: Depends on the type of widget
            region: The region the metrics of this graph should be taken from. Default: Current region
            title: Title for the graph.
            width: Width of the widget, in a grid of 24 units wide. Default: 6

        Stability:
            experimental
        """
        props: GraphWidgetProps = {}

        if left is not None:
            props["left"] = left

        if left_annotations is not None:
            props["leftAnnotations"] = left_annotations

        if left_y_axis is not None:
            props["leftYAxis"] = left_y_axis

        if right is not None:
            props["right"] = right

        if right_annotations is not None:
            props["rightAnnotations"] = right_annotations

        if right_y_axis is not None:
            props["rightYAxis"] = right_y_axis

        if stacked is not None:
            props["stacked"] = stacked

        if height is not None:
            props["height"] = height

        if region is not None:
            props["region"] = region

        if title is not None:
            props["title"] = title

        if width is not None:
            props["width"] = width

        jsii.create(GraphWidget, self, [props])

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List[typing.Any]:
        """Return the widget JSON for use in the dashboard.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJson", [])


@jsii.implements(IMetric)
class Metric(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch.Metric"):
    """A metric emitted by a service.

    The metric is a combination of a metric identifier (namespace, name and dimensions)
    and an aggregation function (statistic, period and unit).

    It also contains metadata which is used only in graphs, such as color and label.
    It makes sense to embed this in here, so that compound constructs can attach
    that metadata to metrics they expose.

    This class does not represent a resource, so hence is not a construct. Instead,
    Metric is an abstraction that makes it easy to specify metrics for use in both
    alarms and graphs.

    Stability:
        experimental
    """
    def __init__(self, *, metric_name: str, namespace: str, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional["Unit"]=None) -> None:
        """
        Arguments:
            props: -
            metric_name: Name of the metric.
            namespace: Namespace of the metric.
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: MetricProps = {"metricName": metric_name, "namespace": namespace}

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

        jsii.create(Metric, self, [props])

    @jsii.member(jsii_name="grantPutMetricData")
    @classmethod
    def grant_put_metric_data(cls, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant permissions to the given identity to write metrics.

        Arguments:
            grantee: The IAM identity to give permissions to.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "grantPutMetricData", [grantee])

    @jsii.member(jsii_name="createAlarm")
    def create_alarm(self, scope: aws_cdk.core.Construct, id: str, *, evaluation_periods: jsii.Number, threshold: jsii.Number, actions_enabled: typing.Optional[bool]=None, alarm_description: typing.Optional[str]=None, alarm_name: typing.Optional[str]=None, comparison_operator: typing.Optional["ComparisonOperator"]=None, datapoints_to_alarm: typing.Optional[jsii.Number]=None, evaluate_low_sample_count_percentile: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, treat_missing_data: typing.Optional["TreatMissingData"]=None) -> "Alarm":
        """Make a new Alarm for this metric.

        Combines both properties that may adjust the metric (aggregation) as well
        as alarm properties.

        Arguments:
            scope: -
            id: -
            props: -
            evaluation_periods: The number of periods over which data is compared to the specified threshold.
            threshold: The value against which the specified statistic is compared.
            actions_enabled: Whether the actions for this alarm are enabled. Default: true
            alarm_description: Description for the alarm. Default: No description
            alarm_name: Name of the alarm. Default: Automatically generated name
            comparison_operator: Comparison to use to check if metric is breaching. Default: GreaterThanOrEqualToThreshold
            datapoints_to_alarm: The number of datapoints that must be breaching to trigger the alarm. This is used only if you are setting an "M out of N" alarm. In that case, this value is the M. For more information, see Evaluating an Alarm in the Amazon CloudWatch User Guide. Default: ``evaluationPeriods``
            evaluate_low_sample_count_percentile: Specifies whether to evaluate the data and potentially change the alarm state if there are too few data points to be statistically significant. Used only for alarms that are based on percentiles. Default: - Not configured.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            treat_missing_data: Sets how this alarm is to handle missing data points. Default: TreatMissingData.Missing

        Stability:
            experimental
        """
        props: CreateAlarmOptions = {"evaluationPeriods": evaluation_periods, "threshold": threshold}

        if actions_enabled is not None:
            props["actionsEnabled"] = actions_enabled

        if alarm_description is not None:
            props["alarmDescription"] = alarm_description

        if alarm_name is not None:
            props["alarmName"] = alarm_name

        if comparison_operator is not None:
            props["comparisonOperator"] = comparison_operator

        if datapoints_to_alarm is not None:
            props["datapointsToAlarm"] = datapoints_to_alarm

        if evaluate_low_sample_count_percentile is not None:
            props["evaluateLowSampleCountPercentile"] = evaluate_low_sample_count_percentile

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if treat_missing_data is not None:
            props["treatMissingData"] = treat_missing_data

        return jsii.invoke(self, "createAlarm", [scope, id, props])

    @jsii.member(jsii_name="toAlarmConfig")
    def to_alarm_config(self) -> "MetricAlarmConfig":
        """Turn this metric object into an alarm configuration.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toAlarmConfig", [])

    @jsii.member(jsii_name="toGraphConfig")
    def to_graph_config(self) -> "MetricGraphConfig":
        """Turn this metric object into a graph configuration.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toGraphConfig", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @jsii.member(jsii_name="with")
    def with_(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional["Unit"]=None) -> "Metric":
        """Return a copy of Metric with properties changed.

        All properties except namespace and metricName can be changed.

        Arguments:
            props: The set of properties to change.
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: MetricOptions = {}

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

        return jsii.invoke(self, "with", [props])

    @property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "metricName")

    @property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "namespace")

    @property
    @jsii.member(jsii_name="period")
    def period(self) -> aws_cdk.core.Duration:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "period")

    @property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "statistic")

    @property
    @jsii.member(jsii_name="color")
    def color(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "color")

    @property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> typing.Optional[typing.Mapping[str,typing.Any]]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "dimensions")

    @property
    @jsii.member(jsii_name="label")
    def label(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "label")

    @property
    @jsii.member(jsii_name="unit")
    def unit(self) -> typing.Optional["Unit"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "unit")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _MetricAlarmConfig(jsii.compat.TypedDict, total=False):
    dimensions: typing.List["Dimension"]
    """The dimensions to apply to the alarm.

    Stability:
        experimental
    """
    extendedStatistic: str
    """Percentile aggregation function to use.

    Stability:
        experimental
    """
    statistic: "Statistic"
    """Simple aggregation function to use.

    Stability:
        experimental
    """
    unit: "Unit"
    """The unit of the alarm.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.MetricAlarmConfig", jsii_struct_bases=[_MetricAlarmConfig])
class MetricAlarmConfig(_MetricAlarmConfig):
    """Properties used to construct the Metric identifying part of an Alarm.

    Stability:
        experimental
    """
    metricName: str
    """Name of the metric.

    Stability:
        experimental
    """

    namespace: str
    """Namespace of the metric.

    Stability:
        experimental
    """

    period: jsii.Number
    """How many seconds to aggregate over.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _MetricGraphConfig(jsii.compat.TypedDict, total=False):
    color: str
    """Color for the graph line.

    Stability:
        experimental
    """
    dimensions: typing.List["Dimension"]
    """The dimensions to apply to the alarm.

    Stability:
        experimental
    """
    label: str
    """Label for the metric.

    Stability:
        experimental
    """
    statistic: str
    """Aggregation function to use (can be either simple or a percentile).

    Stability:
        experimental
    """
    unit: "Unit"
    """The unit of the alarm.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.MetricGraphConfig", jsii_struct_bases=[_MetricGraphConfig])
class MetricGraphConfig(_MetricGraphConfig):
    """Properties used to construct the Metric identifying part of a Graph.

    Stability:
        experimental
    """
    metricName: str
    """Name of the metric.

    Stability:
        experimental
    """

    namespace: str
    """Namespace of the metric.

    Stability:
        experimental
    """

    period: jsii.Number
    """How many seconds to aggregate over.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.MetricOptions", jsii_struct_bases=[CommonMetricOptions])
class MetricOptions(CommonMetricOptions, jsii.compat.TypedDict):
    """Properties of a metric that can be changed.

    Stability:
        experimental
    """
    pass

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.MetricProps", jsii_struct_bases=[CommonMetricOptions])
class MetricProps(CommonMetricOptions, jsii.compat.TypedDict):
    """Properties for a metric.

    Stability:
        experimental
    """
    metricName: str
    """Name of the metric.

    Stability:
        experimental
    """

    namespace: str
    """Namespace of the metric.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.MetricWidgetProps", jsii_struct_bases=[])
class MetricWidgetProps(jsii.compat.TypedDict, total=False):
    """Basic properties for widgets that display metrics.

    Stability:
        experimental
    """
    height: jsii.Number
    """Height of the widget.

    Default:
        Depends on the type of widget

    Stability:
        experimental
    """

    region: str
    """The region the metrics of this graph should be taken from.

    Default:
        Current region

    Stability:
        experimental
    """

    title: str
    """Title for the graph.

    Stability:
        experimental
    """

    width: jsii.Number
    """Width of the widget, in a grid of 24 units wide.

    Default:
        6

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[MetricWidgetProps])
class _AlarmWidgetProps(MetricWidgetProps, jsii.compat.TypedDict, total=False):
    leftYAxis: "YAxisProps"
    """Left Y axis.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.AlarmWidgetProps", jsii_struct_bases=[_AlarmWidgetProps])
class AlarmWidgetProps(_AlarmWidgetProps):
    """Properties for an AlarmWidget.

    Stability:
        experimental
    """
    alarm: "Alarm"
    """The alarm to show.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.GraphWidgetProps", jsii_struct_bases=[MetricWidgetProps])
class GraphWidgetProps(MetricWidgetProps, jsii.compat.TypedDict, total=False):
    """Properties for a GraphWidget.

    Stability:
        experimental
    """
    left: typing.List["IMetric"]
    """Metrics to display on left Y axis.

    Stability:
        experimental
    """

    leftAnnotations: typing.List["HorizontalAnnotation"]
    """Annotations for the left Y axis.

    Stability:
        experimental
    """

    leftYAxis: "YAxisProps"
    """Left Y axis.

    Stability:
        experimental
    """

    right: typing.List["IMetric"]
    """Metrics to display on right Y axis.

    Stability:
        experimental
    """

    rightAnnotations: typing.List["HorizontalAnnotation"]
    """Annotations for the right Y axis.

    Stability:
        experimental
    """

    rightYAxis: "YAxisProps"
    """Right Y axis.

    Stability:
        experimental
    """

    stacked: bool
    """Whether the graph should be shown as stacked lines.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-cloudwatch.PeriodOverride")
class PeriodOverride(enum.Enum):
    """
    Stability:
        experimental
    """
    AUTO = "AUTO"
    """
    Stability:
        experimental
    """
    INHERIT = "INHERIT"
    """
    Stability:
        experimental
    """

@jsii.implements(IWidget)
class Row(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch.Row"):
    """A widget that contains other widgets in a horizontal row.

    Widgets will be laid out next to each other

    Stability:
        experimental
    """
    def __init__(self, *widgets: "IWidget") -> None:
        """
        Arguments:
            widgets: -

        Stability:
            experimental
        """
        jsii.create(Row, self, [*widgets])

    @jsii.member(jsii_name="position")
    def position(self, x: jsii.Number, y: jsii.Number) -> None:
        """Place the widget at a given position.

        Arguments:
            x: -
            y: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "position", [x, y])

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List[typing.Any]:
        """Return the widget JSON for use in the dashboard.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJson", [])

    @property
    @jsii.member(jsii_name="height")
    def height(self) -> jsii.Number:
        """The amount of vertical grid units the widget will take up.

        Stability:
            experimental
        """
        return jsii.get(self, "height")

    @property
    @jsii.member(jsii_name="width")
    def width(self) -> jsii.Number:
        """The amount of horizontal grid units the widget will take up.

        Stability:
            experimental
        """
        return jsii.get(self, "width")


@jsii.enum(jsii_type="@aws-cdk/aws-cloudwatch.Shading")
class Shading(enum.Enum):
    """
    Stability:
        experimental
    """
    NONE = "NONE"
    """Don't add shading.

    Stability:
        experimental
    """
    ABOVE = "ABOVE"
    """Add shading above the annotation.

    Stability:
        experimental
    """
    BELOW = "BELOW"
    """Add shading below the annotation.

    Stability:
        experimental
    """

class SingleValueWidget(ConcreteWidget, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch.SingleValueWidget"):
    """A dashboard widget that displays the most recent value for every metric.

    Stability:
        experimental
    """
    def __init__(self, *, metrics: typing.List["IMetric"], height: typing.Optional[jsii.Number]=None, region: typing.Optional[str]=None, title: typing.Optional[str]=None, width: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            props: -
            metrics: Metrics to display.
            height: Height of the widget. Default: Depends on the type of widget
            region: The region the metrics of this graph should be taken from. Default: Current region
            title: Title for the graph.
            width: Width of the widget, in a grid of 24 units wide. Default: 6

        Stability:
            experimental
        """
        props: SingleValueWidgetProps = {"metrics": metrics}

        if height is not None:
            props["height"] = height

        if region is not None:
            props["region"] = region

        if title is not None:
            props["title"] = title

        if width is not None:
            props["width"] = width

        jsii.create(SingleValueWidget, self, [props])

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List[typing.Any]:
        """Return the widget JSON for use in the dashboard.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJson", [])


@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.SingleValueWidgetProps", jsii_struct_bases=[MetricWidgetProps])
class SingleValueWidgetProps(MetricWidgetProps, jsii.compat.TypedDict):
    """Properties for a SingleValueWidget.

    Stability:
        experimental
    """
    metrics: typing.List["IMetric"]
    """Metrics to display.

    Stability:
        experimental
    """

@jsii.implements(IWidget)
class Spacer(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch.Spacer"):
    """A widget that doesn't display anything but takes up space.

    Stability:
        experimental
    """
    def __init__(self, *, height: typing.Optional[jsii.Number]=None, width: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            props: -
            height: Height of the spacer. Default: : 1
            width: Width of the spacer. Default: 1

        Stability:
            experimental
        """
        props: SpacerProps = {}

        if height is not None:
            props["height"] = height

        if width is not None:
            props["width"] = width

        jsii.create(Spacer, self, [props])

    @jsii.member(jsii_name="position")
    def position(self, _x: jsii.Number, _y: jsii.Number) -> None:
        """Place the widget at a given position.

        Arguments:
            _x: -
            _y: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "position", [_x, _y])

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List[typing.Any]:
        """Return the widget JSON for use in the dashboard.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJson", [])

    @property
    @jsii.member(jsii_name="height")
    def height(self) -> jsii.Number:
        """The amount of vertical grid units the widget will take up.

        Stability:
            experimental
        """
        return jsii.get(self, "height")

    @property
    @jsii.member(jsii_name="width")
    def width(self) -> jsii.Number:
        """The amount of horizontal grid units the widget will take up.

        Stability:
            experimental
        """
        return jsii.get(self, "width")


@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.SpacerProps", jsii_struct_bases=[])
class SpacerProps(jsii.compat.TypedDict, total=False):
    """Props of the spacer.

    Stability:
        experimental
    """
    height: jsii.Number
    """Height of the spacer.

    Default:
        : 1

    Stability:
        experimental
    """

    width: jsii.Number
    """Width of the spacer.

    Default:
        1

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-cloudwatch.Statistic")
class Statistic(enum.Enum):
    """Statistic to use over the aggregation period.

    Stability:
        experimental
    """
    SAMPLE_COUNT = "SAMPLE_COUNT"
    """
    Stability:
        experimental
    """
    AVERAGE = "AVERAGE"
    """
    Stability:
        experimental
    """
    SUM = "SUM"
    """
    Stability:
        experimental
    """
    MINIMUM = "MINIMUM"
    """
    Stability:
        experimental
    """
    MAXIMUM = "MAXIMUM"
    """
    Stability:
        experimental
    """

class TextWidget(ConcreteWidget, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-cloudwatch.TextWidget"):
    """A dashboard widget that displays MarkDown.

    Stability:
        experimental
    """
    def __init__(self, *, markdown: str, height: typing.Optional[jsii.Number]=None, width: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            props: -
            markdown: The text to display, in MarkDown format.
            height: Height of the widget. Default: 2
            width: Width of the widget, in a grid of 24 units wide. Default: 6

        Stability:
            experimental
        """
        props: TextWidgetProps = {"markdown": markdown}

        if height is not None:
            props["height"] = height

        if width is not None:
            props["width"] = width

        jsii.create(TextWidget, self, [props])

    @jsii.member(jsii_name="position")
    def position(self, x: jsii.Number, y: jsii.Number) -> None:
        """Place the widget at a given position.

        Arguments:
            x: -
            y: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "position", [x, y])

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List[typing.Any]:
        """Return the widget JSON for use in the dashboard.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJson", [])


@jsii.data_type_optionals(jsii_struct_bases=[])
class _TextWidgetProps(jsii.compat.TypedDict, total=False):
    height: jsii.Number
    """Height of the widget.

    Default:
        2

    Stability:
        experimental
    """
    width: jsii.Number
    """Width of the widget, in a grid of 24 units wide.

    Default:
        6

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.TextWidgetProps", jsii_struct_bases=[_TextWidgetProps])
class TextWidgetProps(_TextWidgetProps):
    """Properties for a Text widget.

    Stability:
        experimental
    """
    markdown: str
    """The text to display, in MarkDown format.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-cloudwatch.TreatMissingData")
class TreatMissingData(enum.Enum):
    """Specify how missing data points are treated during alarm evaluation.

    Stability:
        experimental
    """
    BREACHING = "BREACHING"
    """Missing data points are treated as breaching the threshold.

    Stability:
        experimental
    """
    NOT_BREACHING = "NOT_BREACHING"
    """Missing data points are treated as being within the threshold.

    Stability:
        experimental
    """
    IGNORE = "IGNORE"
    """The current alarm state is maintained.

    Stability:
        experimental
    """
    MISSING = "MISSING"
    """The alarm does not consider missing data points when evaluating whether to change state.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-cloudwatch.Unit")
class Unit(enum.Enum):
    """Unit for metric.

    Stability:
        experimental
    """
    SECONDS = "SECONDS"
    """
    Stability:
        experimental
    """
    MICROSECONDS = "MICROSECONDS"
    """
    Stability:
        experimental
    """
    MILLISECONDS = "MILLISECONDS"
    """
    Stability:
        experimental
    """
    BYTES = "BYTES"
    """
    Stability:
        experimental
    """
    KILOBYTES = "KILOBYTES"
    """
    Stability:
        experimental
    """
    MEGABYTES = "MEGABYTES"
    """
    Stability:
        experimental
    """
    GIGABYTES = "GIGABYTES"
    """
    Stability:
        experimental
    """
    TERABYTES = "TERABYTES"
    """
    Stability:
        experimental
    """
    BITS = "BITS"
    """
    Stability:
        experimental
    """
    KILOBITS = "KILOBITS"
    """
    Stability:
        experimental
    """
    MEGABITS = "MEGABITS"
    """
    Stability:
        experimental
    """
    GIGABITS = "GIGABITS"
    """
    Stability:
        experimental
    """
    TERABITS = "TERABITS"
    """
    Stability:
        experimental
    """
    PERCENT = "PERCENT"
    """
    Stability:
        experimental
    """
    COUNT = "COUNT"
    """
    Stability:
        experimental
    """
    BYTES_PER_SECOND = "BYTES_PER_SECOND"
    """
    Stability:
        experimental
    """
    KILOBYTES_PER_SECOND = "KILOBYTES_PER_SECOND"
    """
    Stability:
        experimental
    """
    MEGABYTES_PER_SECOND = "MEGABYTES_PER_SECOND"
    """
    Stability:
        experimental
    """
    GIGABYTES_PER_SECOND = "GIGABYTES_PER_SECOND"
    """
    Stability:
        experimental
    """
    TERABYTES_PER_SECOND = "TERABYTES_PER_SECOND"
    """
    Stability:
        experimental
    """
    BITS_PER_SECOND = "BITS_PER_SECOND"
    """
    Stability:
        experimental
    """
    KILOBITS_PER_SECOND = "KILOBITS_PER_SECOND"
    """
    Stability:
        experimental
    """
    MEGABITS_PER_SECOND = "MEGABITS_PER_SECOND"
    """
    Stability:
        experimental
    """
    GIGABITS_PER_SECOND = "GIGABITS_PER_SECOND"
    """
    Stability:
        experimental
    """
    TERABITS_PER_SECOND = "TERABITS_PER_SECOND"
    """
    Stability:
        experimental
    """
    COUNT_PER_SECOND = "COUNT_PER_SECOND"
    """
    Stability:
        experimental
    """
    NONE = "NONE"
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-cloudwatch.YAxisProps", jsii_struct_bases=[])
class YAxisProps(jsii.compat.TypedDict, total=False):
    """Properties for a Y-Axis.

    Stability:
        experimental
    """
    label: str
    """The label.

    Default:
        No label

    Stability:
        experimental
    """

    max: jsii.Number
    """The max value.

    Default:
        No maximum value

    Stability:
        experimental
    """

    min: jsii.Number
    """The min value.

    Default:
        0

    Stability:
        experimental
    """

    showUnits: bool
    """Whether to show units.

    Default:
        true

    Stability:
        experimental
    """

__all__ = ["Alarm", "AlarmActionConfig", "AlarmProps", "AlarmWidget", "AlarmWidgetProps", "CfnAlarm", "CfnAlarmProps", "CfnDashboard", "CfnDashboardProps", "Column", "CommonMetricOptions", "ComparisonOperator", "ConcreteWidget", "CreateAlarmOptions", "Dashboard", "DashboardProps", "Dimension", "GraphWidget", "GraphWidgetProps", "HorizontalAnnotation", "IAlarm", "IAlarmAction", "IMetric", "IWidget", "Metric", "MetricAlarmConfig", "MetricGraphConfig", "MetricOptions", "MetricProps", "MetricWidgetProps", "PeriodOverride", "Row", "Shading", "SingleValueWidget", "SingleValueWidgetProps", "Spacer", "SpacerProps", "Statistic", "TextWidget", "TextWidgetProps", "TreatMissingData", "Unit", "YAxisProps", "__jsii_assembly__"]

publication.publish()
