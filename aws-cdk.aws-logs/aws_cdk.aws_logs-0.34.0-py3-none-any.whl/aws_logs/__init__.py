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
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-logs", "0.34.0", __name__, "aws-logs@0.34.0.jsii.tgz")
class CfnDestination(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs.CfnDestination"):
    """A CloudFormation ``AWS::Logs::Destination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-destination.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Logs::Destination
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, destination_name: str, destination_policy: str, role_arn: str, target_arn: str) -> None:
        """Create a new ``AWS::Logs::Destination``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            destinationName: ``AWS::Logs::Destination.DestinationName``.
            destinationPolicy: ``AWS::Logs::Destination.DestinationPolicy``.
            roleArn: ``AWS::Logs::Destination.RoleArn``.
            targetArn: ``AWS::Logs::Destination.TargetArn``.

        Stability:
            experimental
        """
        props: CfnDestinationProps = {"destinationName": destination_name, "destinationPolicy": destination_policy, "roleArn": role_arn, "targetArn": target_arn}

        jsii.create(CfnDestination, self, [scope, id, props])

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
    @jsii.member(jsii_name="destinationArn")
    def destination_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "destinationArn")

    @property
    @jsii.member(jsii_name="destinationName")
    def destination_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "destinationName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDestinationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-logs.CfnDestinationProps", jsii_struct_bases=[])
class CfnDestinationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Logs::Destination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-destination.html
    Stability:
        experimental
    """
    destinationName: str
    """``AWS::Logs::Destination.DestinationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-destination.html#cfn-logs-destination-destinationname
    Stability:
        experimental
    """

    destinationPolicy: str
    """``AWS::Logs::Destination.DestinationPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-destination.html#cfn-logs-destination-destinationpolicy
    Stability:
        experimental
    """

    roleArn: str
    """``AWS::Logs::Destination.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-destination.html#cfn-logs-destination-rolearn
    Stability:
        experimental
    """

    targetArn: str
    """``AWS::Logs::Destination.TargetArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-destination.html#cfn-logs-destination-targetarn
    Stability:
        experimental
    """

class CfnLogGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs.CfnLogGroup"):
    """A CloudFormation ``AWS::Logs::LogGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-loggroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Logs::LogGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, log_group_name: typing.Optional[str]=None, retention_in_days: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::Logs::LogGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            logGroupName: ``AWS::Logs::LogGroup.LogGroupName``.
            retentionInDays: ``AWS::Logs::LogGroup.RetentionInDays``.

        Stability:
            experimental
        """
        props: CfnLogGroupProps = {}

        if log_group_name is not None:
            props["logGroupName"] = log_group_name

        if retention_in_days is not None:
            props["retentionInDays"] = retention_in_days

        jsii.create(CfnLogGroup, self, [scope, id, props])

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
    @jsii.member(jsii_name="logGroupArn")
    def log_group_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "logGroupArn")

    @property
    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "logGroupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnLogGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-logs.CfnLogGroupProps", jsii_struct_bases=[])
class CfnLogGroupProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::Logs::LogGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-loggroup.html
    Stability:
        experimental
    """
    logGroupName: str
    """``AWS::Logs::LogGroup.LogGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-loggroup.html#cfn-cwl-loggroup-loggroupname
    Stability:
        experimental
    """

    retentionInDays: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Logs::LogGroup.RetentionInDays``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-loggroup.html#cfn-cwl-loggroup-retentionindays
    Stability:
        experimental
    """

class CfnLogStream(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs.CfnLogStream"):
    """A CloudFormation ``AWS::Logs::LogStream``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-logstream.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Logs::LogStream
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, log_group_name: str, log_stream_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Logs::LogStream``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            logGroupName: ``AWS::Logs::LogStream.LogGroupName``.
            logStreamName: ``AWS::Logs::LogStream.LogStreamName``.

        Stability:
            experimental
        """
        props: CfnLogStreamProps = {"logGroupName": log_group_name}

        if log_stream_name is not None:
            props["logStreamName"] = log_stream_name

        jsii.create(CfnLogStream, self, [scope, id, props])

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
    @jsii.member(jsii_name="logStreamName")
    def log_stream_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "logStreamName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnLogStreamProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnLogStreamProps(jsii.compat.TypedDict, total=False):
    logStreamName: str
    """``AWS::Logs::LogStream.LogStreamName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-logstream.html#cfn-logs-logstream-logstreamname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-logs.CfnLogStreamProps", jsii_struct_bases=[_CfnLogStreamProps])
class CfnLogStreamProps(_CfnLogStreamProps):
    """Properties for defining a ``AWS::Logs::LogStream``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-logstream.html
    Stability:
        experimental
    """
    logGroupName: str
    """``AWS::Logs::LogStream.LogGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-logstream.html#cfn-logs-logstream-loggroupname
    Stability:
        experimental
    """

class CfnMetricFilter(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs.CfnMetricFilter"):
    """A CloudFormation ``AWS::Logs::MetricFilter``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-metricfilter.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Logs::MetricFilter
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, filter_pattern: str, log_group_name: str, metric_transformations: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "MetricTransformationProperty"]]]) -> None:
        """Create a new ``AWS::Logs::MetricFilter``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            filterPattern: ``AWS::Logs::MetricFilter.FilterPattern``.
            logGroupName: ``AWS::Logs::MetricFilter.LogGroupName``.
            metricTransformations: ``AWS::Logs::MetricFilter.MetricTransformations``.

        Stability:
            experimental
        """
        props: CfnMetricFilterProps = {"filterPattern": filter_pattern, "logGroupName": log_group_name, "metricTransformations": metric_transformations}

        jsii.create(CfnMetricFilter, self, [scope, id, props])

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
    @jsii.member(jsii_name="metricFilterName")
    def metric_filter_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "metricFilterName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnMetricFilterProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _MetricTransformationProperty(jsii.compat.TypedDict, total=False):
        defaultValue: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnMetricFilter.MetricTransformationProperty.DefaultValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-logs-metricfilter-metrictransformation.html#cfn-cwl-metricfilter-metrictransformation-defaultvalue
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-logs.CfnMetricFilter.MetricTransformationProperty", jsii_struct_bases=[_MetricTransformationProperty])
    class MetricTransformationProperty(_MetricTransformationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-logs-metricfilter-metrictransformation.html
        Stability:
            experimental
        """
        metricName: str
        """``CfnMetricFilter.MetricTransformationProperty.MetricName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-logs-metricfilter-metrictransformation.html#cfn-cwl-metricfilter-metrictransformation-metricname
        Stability:
            experimental
        """

        metricNamespace: str
        """``CfnMetricFilter.MetricTransformationProperty.MetricNamespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-logs-metricfilter-metrictransformation.html#cfn-cwl-metricfilter-metrictransformation-metricnamespace
        Stability:
            experimental
        """

        metricValue: str
        """``CfnMetricFilter.MetricTransformationProperty.MetricValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-logs-metricfilter-metrictransformation.html#cfn-cwl-metricfilter-metrictransformation-metricvalue
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-logs.CfnMetricFilterProps", jsii_struct_bases=[])
class CfnMetricFilterProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Logs::MetricFilter``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-metricfilter.html
    Stability:
        experimental
    """
    filterPattern: str
    """``AWS::Logs::MetricFilter.FilterPattern``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-metricfilter.html#cfn-cwl-metricfilter-filterpattern
    Stability:
        experimental
    """

    logGroupName: str
    """``AWS::Logs::MetricFilter.LogGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-metricfilter.html#cfn-cwl-metricfilter-loggroupname
    Stability:
        experimental
    """

    metricTransformations: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnMetricFilter.MetricTransformationProperty"]]]
    """``AWS::Logs::MetricFilter.MetricTransformations``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-metricfilter.html#cfn-cwl-metricfilter-metrictransformations
    Stability:
        experimental
    """

class CfnSubscriptionFilter(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs.CfnSubscriptionFilter"):
    """A CloudFormation ``AWS::Logs::SubscriptionFilter``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-subscriptionfilter.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Logs::SubscriptionFilter
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, destination_arn: str, filter_pattern: str, log_group_name: str, role_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Logs::SubscriptionFilter``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            destinationArn: ``AWS::Logs::SubscriptionFilter.DestinationArn``.
            filterPattern: ``AWS::Logs::SubscriptionFilter.FilterPattern``.
            logGroupName: ``AWS::Logs::SubscriptionFilter.LogGroupName``.
            roleArn: ``AWS::Logs::SubscriptionFilter.RoleArn``.

        Stability:
            experimental
        """
        props: CfnSubscriptionFilterProps = {"destinationArn": destination_arn, "filterPattern": filter_pattern, "logGroupName": log_group_name}

        if role_arn is not None:
            props["roleArn"] = role_arn

        jsii.create(CfnSubscriptionFilter, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSubscriptionFilterProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="subscriptionFilterName")
    def subscription_filter_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "subscriptionFilterName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSubscriptionFilterProps(jsii.compat.TypedDict, total=False):
    roleArn: str
    """``AWS::Logs::SubscriptionFilter.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-subscriptionfilter.html#cfn-cwl-subscriptionfilter-rolearn
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-logs.CfnSubscriptionFilterProps", jsii_struct_bases=[_CfnSubscriptionFilterProps])
class CfnSubscriptionFilterProps(_CfnSubscriptionFilterProps):
    """Properties for defining a ``AWS::Logs::SubscriptionFilter``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-subscriptionfilter.html
    Stability:
        experimental
    """
    destinationArn: str
    """``AWS::Logs::SubscriptionFilter.DestinationArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-subscriptionfilter.html#cfn-cwl-subscriptionfilter-destinationarn
    Stability:
        experimental
    """

    filterPattern: str
    """``AWS::Logs::SubscriptionFilter.FilterPattern``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-subscriptionfilter.html#cfn-cwl-subscriptionfilter-filterpattern
    Stability:
        experimental
    """

    logGroupName: str
    """``AWS::Logs::SubscriptionFilter.LogGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-subscriptionfilter.html#cfn-cwl-subscriptionfilter-loggroupname
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _ColumnRestriction(jsii.compat.TypedDict, total=False):
    numberValue: jsii.Number
    """Number value to compare to.

    Exactly one of 'stringValue' and 'numberValue' must be set.

    Stability:
        experimental
    """
    stringValue: str
    """String value to compare to.

    Exactly one of 'stringValue' and 'numberValue' must be set.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-logs.ColumnRestriction", jsii_struct_bases=[_ColumnRestriction])
class ColumnRestriction(_ColumnRestriction):
    """
    Stability:
        experimental
    """
    comparison: str
    """Comparison operator to use.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CrossAccountDestinationProps(jsii.compat.TypedDict, total=False):
    destinationName: str
    """The name of the log destination.

    Default:
        Automatically generated

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-logs.CrossAccountDestinationProps", jsii_struct_bases=[_CrossAccountDestinationProps])
class CrossAccountDestinationProps(_CrossAccountDestinationProps):
    """Properties for a CrossAccountDestination.

    Stability:
        experimental
    """
    role: aws_cdk.aws_iam.IRole
    """The role to assume that grants permissions to write to 'target'.

    The role must be assumable by 'logs.{REGION}.amazonaws.com'.

    Stability:
        experimental
    """

    targetArn: str
    """The log destination target's ARN.

    Stability:
        experimental
    """

class FilterPattern(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs.FilterPattern"):
    """A collection of static methods to generate appropriate ILogPatterns.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(FilterPattern, self, [])

    @jsii.member(jsii_name="all")
    @classmethod
    def all(cls, *patterns: "JSONPattern") -> "JSONPattern":
        """A JSON log pattern that matches if all given JSON log patterns match.

        Arguments:
            patterns: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "all", [*patterns])

    @jsii.member(jsii_name="allEvents")
    @classmethod
    def all_events(cls) -> "IFilterPattern":
        """A log pattern that matches all events.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "allEvents", [])

    @jsii.member(jsii_name="allTerms")
    @classmethod
    def all_terms(cls, *terms: str) -> "IFilterPattern":
        """A log pattern that matches if all the strings given appear in the event.

        Arguments:
            terms: The words to search for. All terms must match.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "allTerms", [*terms])

    @jsii.member(jsii_name="any")
    @classmethod
    def any(cls, *patterns: "JSONPattern") -> "JSONPattern":
        """A JSON log pattern that matches if any of the given JSON log patterns match.

        Arguments:
            patterns: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "any", [*patterns])

    @jsii.member(jsii_name="anyTerm")
    @classmethod
    def any_term(cls, *terms: str) -> "IFilterPattern":
        """A log pattern that matches if any of the strings given appear in the event.

        Arguments:
            terms: The words to search for. Any terms must match.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "anyTerm", [*terms])

    @jsii.member(jsii_name="anyTermGroup")
    @classmethod
    def any_term_group(cls, *term_groups: typing.List[str]) -> "IFilterPattern":
        """A log pattern that matches if any of the given term groups matches the event.

        A term group matches an event if all the terms in it appear in the event string.

        Arguments:
            termGroups: A list of term groups to search for. Any one of the clauses must match.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "anyTermGroup", [*term_groups])

    @jsii.member(jsii_name="booleanValue")
    @classmethod
    def boolean_value(cls, json_field: str, value: bool) -> "JSONPattern":
        """A JSON log pattern that matches if the field exists and equals the boolean value.

        Arguments:
            jsonField: Field inside JSON. Example: "$.myField"
            value: The value to match.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "booleanValue", [json_field, value])

    @jsii.member(jsii_name="exists")
    @classmethod
    def exists(cls, json_field: str) -> "JSONPattern":
        """A JSON log patter that matches if the field exists.

        This is a readable convenience wrapper over 'field = *'

        Arguments:
            jsonField: Field inside JSON. Example: "$.myField"

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "exists", [json_field])

    @jsii.member(jsii_name="isNull")
    @classmethod
    def is_null(cls, json_field: str) -> "JSONPattern":
        """A JSON log pattern that matches if the field exists and has the special value 'null'.

        Arguments:
            jsonField: Field inside JSON. Example: "$.myField"

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "isNull", [json_field])

    @jsii.member(jsii_name="literal")
    @classmethod
    def literal(cls, log_pattern_string: str) -> "IFilterPattern":
        """Use the given string as log pattern.

        See https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html
        for information on writing log patterns.

        Arguments:
            logPatternString: The pattern string to use.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "literal", [log_pattern_string])

    @jsii.member(jsii_name="notExists")
    @classmethod
    def not_exists(cls, json_field: str) -> "JSONPattern":
        """A JSON log pattern that matches if the field does not exist.

        Arguments:
            jsonField: Field inside JSON. Example: "$.myField"

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "notExists", [json_field])

    @jsii.member(jsii_name="numberValue")
    @classmethod
    def number_value(cls, json_field: str, comparison: str, value: jsii.Number) -> "JSONPattern":
        """A JSON log pattern that compares numerical values.

        This pattern only matches if the event is a JSON event, and the indicated field inside
        compares with the value in the indicated way.

        Use '$' to indicate the root of the JSON structure. The comparison operator can only
        compare equality or inequality. The '*' wildcard may appear in the value may at the
        start or at the end.

        For more information, see:

        https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html

        Arguments:
            jsonField: Field inside JSON. Example: "$.myField"
            comparison: Comparison to carry out. One of =, !=, <, <=, >, >=.
            value: The numerical value to compare to.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "numberValue", [json_field, comparison, value])

    @jsii.member(jsii_name="spaceDelimited")
    @classmethod
    def space_delimited(cls, *columns: str) -> "SpaceDelimitedTextPattern":
        """A space delimited log pattern matcher.

        The log event is divided into space-delimited columns (optionally
        enclosed by "" or [] to capture spaces into column values), and names
        are given to each column.

        '...' may be specified once to match any number of columns.

        Afterwards, conditions may be added to individual columns.

        Arguments:
            columns: The columns in the space-delimited log stream.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "spaceDelimited", [*columns])

    @jsii.member(jsii_name="stringValue")
    @classmethod
    def string_value(cls, json_field: str, comparison: str, value: str) -> "JSONPattern":
        """A JSON log pattern that compares string values.

        This pattern only matches if the event is a JSON event, and the indicated field inside
        compares with the string value.

        Use '$' to indicate the root of the JSON structure. The comparison operator can only
        compare equality or inequality. The '*' wildcard may appear in the value may at the
        start or at the end.

        For more information, see:

        https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html

        Arguments:
            jsonField: Field inside JSON. Example: "$.myField"
            comparison: Comparison to carry out. Either = or !=.
            value: The string value to compare to. May use '*' as wildcard at start or end of string.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "stringValue", [json_field, comparison, value])


@jsii.interface(jsii_type="@aws-cdk/aws-logs.IFilterPattern")
class IFilterPattern(jsii.compat.Protocol):
    """Interface for objects that can render themselves to log patterns.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IFilterPatternProxy

    @property
    @jsii.member(jsii_name="logPatternString")
    def log_pattern_string(self) -> str:
        """
        Stability:
            experimental
        """
        ...


class _IFilterPatternProxy():
    """Interface for objects that can render themselves to log patterns.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-logs.IFilterPattern"
    @property
    @jsii.member(jsii_name="logPatternString")
    def log_pattern_string(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "logPatternString")


@jsii.interface(jsii_type="@aws-cdk/aws-logs.ILogGroup")
class ILogGroup(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ILogGroupProxy

    @property
    @jsii.member(jsii_name="logGroupArn")
    def log_group_arn(self) -> str:
        """The ARN of this log group.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self) -> str:
        """The name of this log group.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @jsii.member(jsii_name="extractMetric")
    def extract_metric(self, json_field: str, metric_namespace: str, metric_name: str) -> aws_cdk.aws_cloudwatch.Metric:
        """Extract a metric from structured log events in the LogGroup.

        Creates a MetricFilter on this LogGroup that will extract the value
        of the indicated JSON field in all records where it occurs.

        The metric will be available in CloudWatch Metrics under the
        indicated namespace and name.

        Arguments:
            jsonField: JSON field to extract (example: '$.myfield').
            metricNamespace: Namespace to emit the metric under.
            metricName: Name to emit the metric under.

        Returns:
            A Metric object representing the extracted metric

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *actions: str) -> aws_cdk.aws_iam.Grant:
        """Give the indicated permissions on this log group and all streams.

        Arguments:
            grantee: -
            actions: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Give permissions to write to create and write to streams in this log group.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="newMetricFilter")
    def new_metric_filter(self, scope: aws_cdk.cdk.Construct, id: str, *, filter_pattern: "IFilterPattern", metric_name: str, metric_namespace: str, default_value: typing.Optional[jsii.Number]=None, metric_value: typing.Optional[str]=None) -> "MetricFilter":
        """Create a new Metric Filter on this Log Group.

        Arguments:
            scope: Parent construct.
            id: Unique identifier for the construct in its parent.
            props: Properties for creating the MetricFilter.
            filterPattern: Pattern to search for log events.
            metricName: The name of the metric to emit.
            metricNamespace: The namespace of the metric to emit.
            defaultValue: The value to emit if the pattern does not match a particular event. Default: No metric emitted.
            metricValue: The value to emit for the metric. Can either be a literal number (typically "1"), or the name of a field in the structure to take the value from the matched event. If you are using a field value, the field value must have been matched using the pattern. If you want to specify a field from a matched JSON structure, use '$.fieldName', and make sure the field is in the pattern (if only as '$.fieldName = *'). If you want to specify a field from a matched space-delimited structure, use '$fieldName'. Default: "1"

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="newStream")
    def new_stream(self, scope: aws_cdk.cdk.Construct, id: str, *, log_stream_name: typing.Optional[str]=None) -> "LogStream":
        """Create a new Log Stream for this Log Group.

        Arguments:
            scope: Parent construct.
            id: Unique identifier for the construct in its parent.
            props: Properties for creating the LogStream.
            logStreamName: The name of the log stream to create. The name must be unique within the log group. Default: Automatically generated

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="newSubscriptionFilter")
    def new_subscription_filter(self, scope: aws_cdk.cdk.Construct, id: str, *, destination: "ILogSubscriptionDestination", filter_pattern: "IFilterPattern") -> "SubscriptionFilter":
        """Create a new Subscription Filter on this Log Group.

        Arguments:
            scope: Parent construct.
            id: Unique identifier for the construct in its parent.
            props: Properties for creating the SubscriptionFilter.
            destination: The destination to send the filtered events to. For example, a Kinesis stream or a Lambda function.
            filterPattern: Log events matching this pattern will be sent to the destination.

        Stability:
            experimental
        """
        ...


class _ILogGroupProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-logs.ILogGroup"
    @property
    @jsii.member(jsii_name="logGroupArn")
    def log_group_arn(self) -> str:
        """The ARN of this log group.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "logGroupArn")

    @property
    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self) -> str:
        """The name of this log group.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "logGroupName")

    @jsii.member(jsii_name="extractMetric")
    def extract_metric(self, json_field: str, metric_namespace: str, metric_name: str) -> aws_cdk.aws_cloudwatch.Metric:
        """Extract a metric from structured log events in the LogGroup.

        Creates a MetricFilter on this LogGroup that will extract the value
        of the indicated JSON field in all records where it occurs.

        The metric will be available in CloudWatch Metrics under the
        indicated namespace and name.

        Arguments:
            jsonField: JSON field to extract (example: '$.myfield').
            metricNamespace: Namespace to emit the metric under.
            metricName: Name to emit the metric under.

        Returns:
            A Metric object representing the extracted metric

        Stability:
            experimental
        """
        return jsii.invoke(self, "extractMetric", [json_field, metric_namespace, metric_name])

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *actions: str) -> aws_cdk.aws_iam.Grant:
        """Give the indicated permissions on this log group and all streams.

        Arguments:
            grantee: -
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grant", [grantee, *actions])

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Give permissions to write to create and write to streams in this log group.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantWrite", [grantee])

    @jsii.member(jsii_name="newMetricFilter")
    def new_metric_filter(self, scope: aws_cdk.cdk.Construct, id: str, *, filter_pattern: "IFilterPattern", metric_name: str, metric_namespace: str, default_value: typing.Optional[jsii.Number]=None, metric_value: typing.Optional[str]=None) -> "MetricFilter":
        """Create a new Metric Filter on this Log Group.

        Arguments:
            scope: Parent construct.
            id: Unique identifier for the construct in its parent.
            props: Properties for creating the MetricFilter.
            filterPattern: Pattern to search for log events.
            metricName: The name of the metric to emit.
            metricNamespace: The namespace of the metric to emit.
            defaultValue: The value to emit if the pattern does not match a particular event. Default: No metric emitted.
            metricValue: The value to emit for the metric. Can either be a literal number (typically "1"), or the name of a field in the structure to take the value from the matched event. If you are using a field value, the field value must have been matched using the pattern. If you want to specify a field from a matched JSON structure, use '$.fieldName', and make sure the field is in the pattern (if only as '$.fieldName = *'). If you want to specify a field from a matched space-delimited structure, use '$fieldName'. Default: "1"

        Stability:
            experimental
        """
        props: NewMetricFilterProps = {"filterPattern": filter_pattern, "metricName": metric_name, "metricNamespace": metric_namespace}

        if default_value is not None:
            props["defaultValue"] = default_value

        if metric_value is not None:
            props["metricValue"] = metric_value

        return jsii.invoke(self, "newMetricFilter", [scope, id, props])

    @jsii.member(jsii_name="newStream")
    def new_stream(self, scope: aws_cdk.cdk.Construct, id: str, *, log_stream_name: typing.Optional[str]=None) -> "LogStream":
        """Create a new Log Stream for this Log Group.

        Arguments:
            scope: Parent construct.
            id: Unique identifier for the construct in its parent.
            props: Properties for creating the LogStream.
            logStreamName: The name of the log stream to create. The name must be unique within the log group. Default: Automatically generated

        Stability:
            experimental
        """
        props: NewLogStreamProps = {}

        if log_stream_name is not None:
            props["logStreamName"] = log_stream_name

        return jsii.invoke(self, "newStream", [scope, id, props])

    @jsii.member(jsii_name="newSubscriptionFilter")
    def new_subscription_filter(self, scope: aws_cdk.cdk.Construct, id: str, *, destination: "ILogSubscriptionDestination", filter_pattern: "IFilterPattern") -> "SubscriptionFilter":
        """Create a new Subscription Filter on this Log Group.

        Arguments:
            scope: Parent construct.
            id: Unique identifier for the construct in its parent.
            props: Properties for creating the SubscriptionFilter.
            destination: The destination to send the filtered events to. For example, a Kinesis stream or a Lambda function.
            filterPattern: Log events matching this pattern will be sent to the destination.

        Stability:
            experimental
        """
        props: NewSubscriptionFilterProps = {"destination": destination, "filterPattern": filter_pattern}

        return jsii.invoke(self, "newSubscriptionFilter", [scope, id, props])


@jsii.interface(jsii_type="@aws-cdk/aws-logs.ILogStream")
class ILogStream(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ILogStreamProxy

    @property
    @jsii.member(jsii_name="logStreamName")
    def log_stream_name(self) -> str:
        """The name of this log stream.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _ILogStreamProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-logs.ILogStream"
    @property
    @jsii.member(jsii_name="logStreamName")
    def log_stream_name(self) -> str:
        """The name of this log stream.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "logStreamName")


@jsii.interface(jsii_type="@aws-cdk/aws-logs.ILogSubscriptionDestination")
class ILogSubscriptionDestination(jsii.compat.Protocol):
    """Interface for classes that can be the destination of a log Subscription.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ILogSubscriptionDestinationProxy

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.cdk.Construct, source_log_group: "ILogGroup") -> "LogSubscriptionDestinationConfig":
        """Return the properties required to send subscription events to this destination.

        If necessary, the destination can use the properties of the SubscriptionFilter
        object itself to configure its permissions to allow the subscription to write
        to it.

        The destination may reconfigure its own permissions in response to this
        function call.

        Arguments:
            scope: -
            sourceLogGroup: -

        Stability:
            experimental
        """
        ...


class _ILogSubscriptionDestinationProxy():
    """Interface for classes that can be the destination of a log Subscription.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-logs.ILogSubscriptionDestination"
    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.cdk.Construct, source_log_group: "ILogGroup") -> "LogSubscriptionDestinationConfig":
        """Return the properties required to send subscription events to this destination.

        If necessary, the destination can use the properties of the SubscriptionFilter
        object itself to configure its permissions to allow the subscription to write
        to it.

        The destination may reconfigure its own permissions in response to this
        function call.

        Arguments:
            scope: -
            sourceLogGroup: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [scope, source_log_group])


@jsii.implements(ILogSubscriptionDestination)
class CrossAccountDestination(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs.CrossAccountDestination"):
    """A new CloudWatch Logs Destination for use in cross-account scenarios.

    CrossAccountDestinations are used to subscribe a Kinesis stream in a
    different account to a CloudWatch Subscription.

    Consumers will hardly ever need to use this class. Instead, directly
    subscribe a Kinesis stream using the integration class in the
    ``@aws-cdk/aws-logs-destinations`` package; if necessary, a
    ``CrossAccountDestination`` will be created automatically.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, role: aws_cdk.aws_iam.IRole, target_arn: str, destination_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            role: The role to assume that grants permissions to write to 'target'. The role must be assumable by 'logs.{REGION}.amazonaws.com'.
            targetArn: The log destination target's ARN.
            destinationName: The name of the log destination. Default: Automatically generated

        Stability:
            experimental
        """
        props: CrossAccountDestinationProps = {"role": role, "targetArn": target_arn}

        if destination_name is not None:
            props["destinationName"] = destination_name

        jsii.create(CrossAccountDestination, self, [scope, id, props])

    @jsii.member(jsii_name="addToPolicy")
    def add_to_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """
        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToPolicy", [statement])

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: aws_cdk.cdk.Construct, _source_log_group: "ILogGroup") -> "LogSubscriptionDestinationConfig":
        """Return the properties required to send subscription events to this destination.

        If necessary, the destination can use the properties of the SubscriptionFilter
        object itself to configure its permissions to allow the subscription to write
        to it.

        The destination may reconfigure its own permissions in response to this
        function call.

        Arguments:
            _scope: -
            _sourceLogGroup: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_scope, _source_log_group])

    @property
    @jsii.member(jsii_name="destinationArn")
    def destination_arn(self) -> str:
        """The ARN of this CrossAccountDestination object.

        Stability:
            experimental
        """
        return jsii.get(self, "destinationArn")

    @property
    @jsii.member(jsii_name="destinationName")
    def destination_name(self) -> str:
        """The name of this CrossAccountDestination object.

        Stability:
            experimental
        """
        return jsii.get(self, "destinationName")

    @property
    @jsii.member(jsii_name="policyDocument")
    def policy_document(self) -> aws_cdk.aws_iam.PolicyDocument:
        """Policy object of this CrossAccountDestination object.

        Stability:
            experimental
        """
        return jsii.get(self, "policyDocument")


@jsii.implements(IFilterPattern)
class JSONPattern(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-logs.JSONPattern"):
    """Base class for patterns that only match JSON log events.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _JSONPatternProxy

    def __init__(self, json_pattern_string: str) -> None:
        """
        Arguments:
            jsonPatternString: -

        Stability:
            experimental
        """
        jsii.create(JSONPattern, self, [json_pattern_string])

    @property
    @jsii.member(jsii_name="jsonPatternString")
    def json_pattern_string(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "jsonPatternString")

    @property
    @jsii.member(jsii_name="logPatternString")
    def log_pattern_string(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "logPatternString")


class _JSONPatternProxy(JSONPattern):
    pass

@jsii.implements(ILogGroup)
class LogGroup(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs.LogGroup"):
    """Define a CloudWatch Log Group.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, log_group_name: typing.Optional[str]=None, retain_log_group: typing.Optional[bool]=None, retention_days: typing.Optional["RetentionDays"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            logGroupName: Name of the log group. Default: Automatically generated
            retainLogGroup: Retain the log group if the stack or containing construct ceases to exist. Normally you want to retain the log group so you can diagnose issues from logs even after a deployment that no longer includes the log group. In that case, use the normal date-based retention policy to age out your logs. Default: true
            retentionDays: How long, in days, the log contents will be retained. To retain all logs, set this value to Infinity. Default: 731 days (2 years)

        Stability:
            experimental
        """
        props: LogGroupProps = {}

        if log_group_name is not None:
            props["logGroupName"] = log_group_name

        if retain_log_group is not None:
            props["retainLogGroup"] = retain_log_group

        if retention_days is not None:
            props["retentionDays"] = retention_days

        jsii.create(LogGroup, self, [scope, id, props])

    @jsii.member(jsii_name="fromLogGroupArn")
    @classmethod
    def from_log_group_arn(cls, scope: aws_cdk.cdk.Construct, id: str, log_group_arn: str) -> "ILogGroup":
        """Import an existing LogGroup.

        Arguments:
            scope: -
            id: -
            logGroupArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromLogGroupArn", [scope, id, log_group_arn])

    @jsii.member(jsii_name="extractMetric")
    def extract_metric(self, json_field: str, metric_namespace: str, metric_name: str) -> aws_cdk.aws_cloudwatch.Metric:
        """Extract a metric from structured log events in the LogGroup.

        Creates a MetricFilter on this LogGroup that will extract the value
        of the indicated JSON field in all records where it occurs.

        The metric will be available in CloudWatch Metrics under the
        indicated namespace and name.

        Arguments:
            jsonField: JSON field to extract (example: '$.myfield').
            metricNamespace: Namespace to emit the metric under.
            metricName: Name to emit the metric under.

        Returns:
            A Metric object representing the extracted metric

        Stability:
            experimental
        """
        return jsii.invoke(self, "extractMetric", [json_field, metric_namespace, metric_name])

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *actions: str) -> aws_cdk.aws_iam.Grant:
        """Give the indicated permissions on this log group and all streams.

        Arguments:
            grantee: -
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grant", [grantee, *actions])

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Give permissions to write to create and write to streams in this log group.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantWrite", [grantee])

    @jsii.member(jsii_name="newMetricFilter")
    def new_metric_filter(self, scope: aws_cdk.cdk.Construct, id: str, *, filter_pattern: "IFilterPattern", metric_name: str, metric_namespace: str, default_value: typing.Optional[jsii.Number]=None, metric_value: typing.Optional[str]=None) -> "MetricFilter":
        """Create a new Metric Filter on this Log Group.

        Arguments:
            scope: Parent construct.
            id: Unique identifier for the construct in its parent.
            props: Properties for creating the MetricFilter.
            filterPattern: Pattern to search for log events.
            metricName: The name of the metric to emit.
            metricNamespace: The namespace of the metric to emit.
            defaultValue: The value to emit if the pattern does not match a particular event. Default: No metric emitted.
            metricValue: The value to emit for the metric. Can either be a literal number (typically "1"), or the name of a field in the structure to take the value from the matched event. If you are using a field value, the field value must have been matched using the pattern. If you want to specify a field from a matched JSON structure, use '$.fieldName', and make sure the field is in the pattern (if only as '$.fieldName = *'). If you want to specify a field from a matched space-delimited structure, use '$fieldName'. Default: "1"

        Stability:
            experimental
        """
        props: NewMetricFilterProps = {"filterPattern": filter_pattern, "metricName": metric_name, "metricNamespace": metric_namespace}

        if default_value is not None:
            props["defaultValue"] = default_value

        if metric_value is not None:
            props["metricValue"] = metric_value

        return jsii.invoke(self, "newMetricFilter", [scope, id, props])

    @jsii.member(jsii_name="newStream")
    def new_stream(self, scope: aws_cdk.cdk.Construct, id: str, *, log_stream_name: typing.Optional[str]=None) -> "LogStream":
        """Create a new Log Stream for this Log Group.

        Arguments:
            scope: Parent construct.
            id: Unique identifier for the construct in its parent.
            props: Properties for creating the LogStream.
            logStreamName: The name of the log stream to create. The name must be unique within the log group. Default: Automatically generated

        Stability:
            experimental
        """
        props: NewLogStreamProps = {}

        if log_stream_name is not None:
            props["logStreamName"] = log_stream_name

        return jsii.invoke(self, "newStream", [scope, id, props])

    @jsii.member(jsii_name="newSubscriptionFilter")
    def new_subscription_filter(self, scope: aws_cdk.cdk.Construct, id: str, *, destination: "ILogSubscriptionDestination", filter_pattern: "IFilterPattern") -> "SubscriptionFilter":
        """Create a new Subscription Filter on this Log Group.

        Arguments:
            scope: Parent construct.
            id: Unique identifier for the construct in its parent.
            props: Properties for creating the SubscriptionFilter.
            destination: The destination to send the filtered events to. For example, a Kinesis stream or a Lambda function.
            filterPattern: Log events matching this pattern will be sent to the destination.

        Stability:
            experimental
        """
        props: NewSubscriptionFilterProps = {"destination": destination, "filterPattern": filter_pattern}

        return jsii.invoke(self, "newSubscriptionFilter", [scope, id, props])

    @property
    @jsii.member(jsii_name="logGroupArn")
    def log_group_arn(self) -> str:
        """The ARN of this log group.

        Stability:
            experimental
        """
        return jsii.get(self, "logGroupArn")

    @property
    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self) -> str:
        """The name of this log group.

        Stability:
            experimental
        """
        return jsii.get(self, "logGroupName")


@jsii.data_type(jsii_type="@aws-cdk/aws-logs.LogGroupProps", jsii_struct_bases=[])
class LogGroupProps(jsii.compat.TypedDict, total=False):
    """Properties for a LogGroup.

    Stability:
        experimental
    """
    logGroupName: str
    """Name of the log group.

    Default:
        Automatically generated

    Stability:
        experimental
    """

    retainLogGroup: bool
    """Retain the log group if the stack or containing construct ceases to exist.

    Normally you want to retain the log group so you can diagnose issues
    from logs even after a deployment that no longer includes the log group.
    In that case, use the normal date-based retention policy to age out your
    logs.

    Default:
        true

    Stability:
        experimental
    """

    retentionDays: "RetentionDays"
    """How long, in days, the log contents will be retained.

    To retain all logs, set this value to Infinity.

    Default:
        731 days (2 years)

    Stability:
        experimental
    """

@jsii.implements(ILogStream)
class LogStream(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs.LogStream"):
    """Define a Log Stream in a Log Group.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, log_group: "ILogGroup", log_stream_name: typing.Optional[str]=None, retain_log_stream: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            logGroup: The log group to create a log stream for.
            logStreamName: The name of the log stream to create. The name must be unique within the log group. Default: Automatically generated
            retainLogStream: Retain the log stream if the stack or containing construct ceases to exist. Normally you want to retain the log stream so you can diagnose issues from logs even after a deployment that no longer includes the log stream. The date-based retention policy of your log group will age out the logs after a certain time. Default: true

        Stability:
            experimental
        """
        props: LogStreamProps = {"logGroup": log_group}

        if log_stream_name is not None:
            props["logStreamName"] = log_stream_name

        if retain_log_stream is not None:
            props["retainLogStream"] = retain_log_stream

        jsii.create(LogStream, self, [scope, id, props])

    @jsii.member(jsii_name="fromLogStreamName")
    @classmethod
    def from_log_stream_name(cls, scope: aws_cdk.cdk.Construct, id: str, log_stream_name: str) -> "ILogStream":
        """Import an existing LogGroup.

        Arguments:
            scope: -
            id: -
            logStreamName: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromLogStreamName", [scope, id, log_stream_name])

    @property
    @jsii.member(jsii_name="logStreamName")
    def log_stream_name(self) -> str:
        """The name of this log stream.

        Stability:
            experimental
        """
        return jsii.get(self, "logStreamName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _LogStreamProps(jsii.compat.TypedDict, total=False):
    logStreamName: str
    """The name of the log stream to create.

    The name must be unique within the log group.

    Default:
        Automatically generated

    Stability:
        experimental
    """
    retainLogStream: bool
    """Retain the log stream if the stack or containing construct ceases to exist.

    Normally you want to retain the log stream so you can diagnose issues
    from logs even after a deployment that no longer includes the log stream.

    The date-based retention policy of your log group will age out the logs
    after a certain time.

    Default:
        true

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-logs.LogStreamProps", jsii_struct_bases=[_LogStreamProps])
class LogStreamProps(_LogStreamProps):
    """Properties for a LogStream.

    Stability:
        experimental
    """
    logGroup: "ILogGroup"
    """The log group to create a log stream for.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _LogSubscriptionDestinationConfig(jsii.compat.TypedDict, total=False):
    role: aws_cdk.aws_iam.IRole
    """The role to assume to write log events to the destination.

    Default:
        No role assumed

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-logs.LogSubscriptionDestinationConfig", jsii_struct_bases=[_LogSubscriptionDestinationConfig])
class LogSubscriptionDestinationConfig(_LogSubscriptionDestinationConfig):
    """Properties returned by a Subscription destination.

    Stability:
        experimental
    """
    arn: str
    """The ARN of the subscription's destination.

    Stability:
        experimental
    """

class MetricFilter(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs.MetricFilter"):
    """A filter that extracts information from CloudWatch Logs and emits to CloudWatch Metrics.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, filter_pattern: "IFilterPattern", log_group: "ILogGroup", metric_name: str, metric_namespace: str, default_value: typing.Optional[jsii.Number]=None, metric_value: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            filterPattern: Pattern to search for log events.
            logGroup: The log group to create the filter on.
            metricName: The name of the metric to emit.
            metricNamespace: The namespace of the metric to emit.
            defaultValue: The value to emit if the pattern does not match a particular event. Default: No metric emitted.
            metricValue: The value to emit for the metric. Can either be a literal number (typically "1"), or the name of a field in the structure to take the value from the matched event. If you are using a field value, the field value must have been matched using the pattern. If you want to specify a field from a matched JSON structure, use '$.fieldName', and make sure the field is in the pattern (if only as '$.fieldName = *'). If you want to specify a field from a matched space-delimited structure, use '$fieldName'. Default: "1"

        Stability:
            experimental
        """
        props: MetricFilterProps = {"filterPattern": filter_pattern, "logGroup": log_group, "metricName": metric_name, "metricNamespace": metric_namespace}

        if default_value is not None:
            props["defaultValue"] = default_value

        if metric_value is not None:
            props["metricValue"] = metric_value

        jsii.create(MetricFilter, self, [scope, id, props])


@jsii.data_type_optionals(jsii_struct_bases=[])
class _MetricFilterProps(jsii.compat.TypedDict, total=False):
    defaultValue: jsii.Number
    """The value to emit if the pattern does not match a particular event.

    Default:
        No metric emitted.

    Stability:
        experimental
    """
    metricValue: str
    """The value to emit for the metric.

    Can either be a literal number (typically "1"), or the name of a field in the structure
    to take the value from the matched event. If you are using a field value, the field
    value must have been matched using the pattern.

    If you want to specify a field from a matched JSON structure, use '$.fieldName',
    and make sure the field is in the pattern (if only as '$.fieldName = *').

    If you want to specify a field from a matched space-delimited structure,
    use '$fieldName'.

    Default:
        "1"

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-logs.MetricFilterProps", jsii_struct_bases=[_MetricFilterProps])
class MetricFilterProps(_MetricFilterProps):
    """Properties for a MetricFilter.

    Stability:
        experimental
    """
    filterPattern: "IFilterPattern"
    """Pattern to search for log events.

    Stability:
        experimental
    """

    logGroup: "ILogGroup"
    """The log group to create the filter on.

    Stability:
        experimental
    """

    metricName: str
    """The name of the metric to emit.

    Stability:
        experimental
    """

    metricNamespace: str
    """The namespace of the metric to emit.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-logs.NewLogStreamProps", jsii_struct_bases=[])
class NewLogStreamProps(jsii.compat.TypedDict, total=False):
    """Properties for a new LogStream created from a LogGroup.

    Stability:
        experimental
    """
    logStreamName: str
    """The name of the log stream to create.

    The name must be unique within the log group.

    Default:
        Automatically generated

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _NewMetricFilterProps(jsii.compat.TypedDict, total=False):
    defaultValue: jsii.Number
    """The value to emit if the pattern does not match a particular event.

    Default:
        No metric emitted.

    Stability:
        experimental
    """
    metricValue: str
    """The value to emit for the metric.

    Can either be a literal number (typically "1"), or the name of a field in the structure
    to take the value from the matched event. If you are using a field value, the field
    value must have been matched using the pattern.

    If you want to specify a field from a matched JSON structure, use '$.fieldName',
    and make sure the field is in the pattern (if only as '$.fieldName = *').

    If you want to specify a field from a matched space-delimited structure,
    use '$fieldName'.

    Default:
        "1"

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-logs.NewMetricFilterProps", jsii_struct_bases=[_NewMetricFilterProps])
class NewMetricFilterProps(_NewMetricFilterProps):
    """Properties for a MetricFilter created from a LogGroup.

    Stability:
        experimental
    """
    filterPattern: "IFilterPattern"
    """Pattern to search for log events.

    Stability:
        experimental
    """

    metricName: str
    """The name of the metric to emit.

    Stability:
        experimental
    """

    metricNamespace: str
    """The namespace of the metric to emit.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-logs.NewSubscriptionFilterProps", jsii_struct_bases=[])
class NewSubscriptionFilterProps(jsii.compat.TypedDict):
    """Properties for a new SubscriptionFilter created from a LogGroup.

    Stability:
        experimental
    """
    destination: "ILogSubscriptionDestination"
    """The destination to send the filtered events to.

    For example, a Kinesis stream or a Lambda function.

    Stability:
        experimental
    """

    filterPattern: "IFilterPattern"
    """Log events matching this pattern will be sent to the destination.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-logs.RetentionDays")
class RetentionDays(enum.Enum):
    """How long, in days, the log contents will be retained.

    Stability:
        experimental
    """
    OneDay = "OneDay"
    """1 day.

    Stability:
        experimental
    """
    ThreeDays = "ThreeDays"
    """3 days.

    Stability:
        experimental
    """
    FiveDays = "FiveDays"
    """5 days.

    Stability:
        experimental
    """
    OneWeek = "OneWeek"
    """1 week.

    Stability:
        experimental
    """
    TwoWeeks = "TwoWeeks"
    """2 weeks.

    Stability:
        experimental
    """
    OneMonth = "OneMonth"
    """1 month.

    Stability:
        experimental
    """
    TwoMonths = "TwoMonths"
    """2 months.

    Stability:
        experimental
    """
    ThreeMonths = "ThreeMonths"
    """3 months.

    Stability:
        experimental
    """
    FourMonths = "FourMonths"
    """4 months.

    Stability:
        experimental
    """
    FiveMonths = "FiveMonths"
    """5 months.

    Stability:
        experimental
    """
    SixMonths = "SixMonths"
    """6 months.

    Stability:
        experimental
    """
    OneYear = "OneYear"
    """1 year.

    Stability:
        experimental
    """
    ThirteenMonths = "ThirteenMonths"
    """13 months.

    Stability:
        experimental
    """
    EighteenMonths = "EighteenMonths"
    """18 months.

    Stability:
        experimental
    """
    TwoYears = "TwoYears"
    """2 years.

    Stability:
        experimental
    """
    FiveYears = "FiveYears"
    """5 years.

    Stability:
        experimental
    """
    TenYears = "TenYears"
    """10 years.

    Stability:
        experimental
    """

@jsii.implements(IFilterPattern)
class SpaceDelimitedTextPattern(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs.SpaceDelimitedTextPattern"):
    """Space delimited text pattern.

    Stability:
        experimental
    """
    def __init__(self, columns: typing.List[str], restrictions: typing.Mapping[str,typing.List["ColumnRestriction"]]) -> None:
        """
        Arguments:
            columns: -
            restrictions: -

        Stability:
            experimental
        """
        jsii.create(SpaceDelimitedTextPattern, self, [columns, restrictions])

    @jsii.member(jsii_name="construct")
    @classmethod
    def construct(cls, columns: typing.List[str]) -> "SpaceDelimitedTextPattern":
        """Construct a new instance of a space delimited text pattern.

        Since this class must be public, we can't rely on the user only creating it through
        the ``LogPattern.spaceDelimited()`` factory function. We must therefore validate the
        argument in the constructor. Since we're returning a copy on every mutation, and we
        don't want to re-validate the same things on every construction, we provide a limited
        set of mutator functions and only validate the new data every time.

        Arguments:
            columns: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "construct", [columns])

    @jsii.member(jsii_name="whereNumber")
    def where_number(self, column_name: str, comparison: str, value: jsii.Number) -> "SpaceDelimitedTextPattern":
        """Restrict where the pattern applies.

        Arguments:
            columnName: -
            comparison: -
            value: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "whereNumber", [column_name, comparison, value])

    @jsii.member(jsii_name="whereString")
    def where_string(self, column_name: str, comparison: str, value: str) -> "SpaceDelimitedTextPattern":
        """Restrict where the pattern applies.

        Arguments:
            columnName: -
            comparison: -
            value: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "whereString", [column_name, comparison, value])

    @property
    @jsii.member(jsii_name="columns")
    def columns(self) -> typing.List[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "columns")

    @property
    @jsii.member(jsii_name="logPatternString")
    def log_pattern_string(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "logPatternString")

    @property
    @jsii.member(jsii_name="restrictions")
    def restrictions(self) -> typing.Mapping[str,typing.List["ColumnRestriction"]]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "restrictions")


class SubscriptionFilter(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-logs.SubscriptionFilter"):
    """A new Subscription on a CloudWatch log group.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, destination: "ILogSubscriptionDestination", filter_pattern: "IFilterPattern", log_group: "ILogGroup") -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            destination: The destination to send the filtered events to. For example, a Kinesis stream or a Lambda function.
            filterPattern: Log events matching this pattern will be sent to the destination.
            logGroup: The log group to create the subscription on.

        Stability:
            experimental
        """
        props: SubscriptionFilterProps = {"destination": destination, "filterPattern": filter_pattern, "logGroup": log_group}

        jsii.create(SubscriptionFilter, self, [scope, id, props])


@jsii.data_type(jsii_type="@aws-cdk/aws-logs.SubscriptionFilterProps", jsii_struct_bases=[])
class SubscriptionFilterProps(jsii.compat.TypedDict):
    """Properties for a SubscriptionFilter.

    Stability:
        experimental
    """
    destination: "ILogSubscriptionDestination"
    """The destination to send the filtered events to.

    For example, a Kinesis stream or a Lambda function.

    Stability:
        experimental
    """

    filterPattern: "IFilterPattern"
    """Log events matching this pattern will be sent to the destination.

    Stability:
        experimental
    """

    logGroup: "ILogGroup"
    """The log group to create the subscription on.

    Stability:
        experimental
    """

__all__ = ["CfnDestination", "CfnDestinationProps", "CfnLogGroup", "CfnLogGroupProps", "CfnLogStream", "CfnLogStreamProps", "CfnMetricFilter", "CfnMetricFilterProps", "CfnSubscriptionFilter", "CfnSubscriptionFilterProps", "ColumnRestriction", "CrossAccountDestination", "CrossAccountDestinationProps", "FilterPattern", "IFilterPattern", "ILogGroup", "ILogStream", "ILogSubscriptionDestination", "JSONPattern", "LogGroup", "LogGroupProps", "LogStream", "LogStreamProps", "LogSubscriptionDestinationConfig", "MetricFilter", "MetricFilterProps", "NewLogStreamProps", "NewMetricFilterProps", "NewSubscriptionFilterProps", "RetentionDays", "SpaceDelimitedTextPattern", "SubscriptionFilter", "SubscriptionFilterProps", "__jsii_assembly__"]

publication.publish()
