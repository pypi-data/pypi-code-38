import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.aws_sns
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-ses", "0.34.0", __name__, "aws-ses@0.34.0.jsii.tgz")
class CfnConfigurationSet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.CfnConfigurationSet"):
    """A CloudFormation ``AWS::SES::ConfigurationSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationset.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SES::ConfigurationSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SES::ConfigurationSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::SES::ConfigurationSet.Name``.

        Stability:
            experimental
        """
        props: CfnConfigurationSetProps = {}

        if name is not None:
            props["name"] = name

        jsii.create(CfnConfigurationSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="configurationSetName")
    def configuration_set_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "configurationSetName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnConfigurationSetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


class CfnConfigurationSetEventDestination(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetEventDestination"):
    """A CloudFormation ``AWS::SES::ConfigurationSetEventDestination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationseteventdestination.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SES::ConfigurationSetEventDestination
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, configuration_set_name: str, event_destination: typing.Union["EventDestinationProperty", aws_cdk.cdk.Token]) -> None:
        """Create a new ``AWS::SES::ConfigurationSetEventDestination``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            configurationSetName: ``AWS::SES::ConfigurationSetEventDestination.ConfigurationSetName``.
            eventDestination: ``AWS::SES::ConfigurationSetEventDestination.EventDestination``.

        Stability:
            experimental
        """
        props: CfnConfigurationSetEventDestinationProps = {"configurationSetName": configuration_set_name, "eventDestination": event_destination}

        jsii.create(CfnConfigurationSetEventDestination, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnConfigurationSetEventDestinationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetEventDestination.CloudWatchDestinationProperty", jsii_struct_bases=[])
    class CloudWatchDestinationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-cloudwatchdestination.html
        Stability:
            experimental
        """
        dimensionConfigurations: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnConfigurationSetEventDestination.DimensionConfigurationProperty"]]]
        """``CfnConfigurationSetEventDestination.CloudWatchDestinationProperty.DimensionConfigurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-cloudwatchdestination.html#cfn-ses-configurationseteventdestination-cloudwatchdestination-dimensionconfigurations
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetEventDestination.DimensionConfigurationProperty", jsii_struct_bases=[])
    class DimensionConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-dimensionconfiguration.html
        Stability:
            experimental
        """
        defaultDimensionValue: str
        """``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DefaultDimensionValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-dimensionconfiguration.html#cfn-ses-configurationseteventdestination-dimensionconfiguration-defaultdimensionvalue
        Stability:
            experimental
        """

        dimensionName: str
        """``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DimensionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-dimensionconfiguration.html#cfn-ses-configurationseteventdestination-dimensionconfiguration-dimensionname
        Stability:
            experimental
        """

        dimensionValueSource: str
        """``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DimensionValueSource``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-dimensionconfiguration.html#cfn-ses-configurationseteventdestination-dimensionconfiguration-dimensionvaluesource
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _EventDestinationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchDestination: typing.Union[aws_cdk.cdk.Token, "CfnConfigurationSetEventDestination.CloudWatchDestinationProperty"]
        """``CfnConfigurationSetEventDestination.EventDestinationProperty.CloudWatchDestination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-eventdestination.html#cfn-ses-configurationseteventdestination-eventdestination-cloudwatchdestination
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnConfigurationSetEventDestination.EventDestinationProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-eventdestination.html#cfn-ses-configurationseteventdestination-eventdestination-enabled
        Stability:
            experimental
        """
        kinesisFirehoseDestination: typing.Union[aws_cdk.cdk.Token, "CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty"]
        """``CfnConfigurationSetEventDestination.EventDestinationProperty.KinesisFirehoseDestination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-eventdestination.html#cfn-ses-configurationseteventdestination-eventdestination-kinesisfirehosedestination
        Stability:
            experimental
        """
        name: str
        """``CfnConfigurationSetEventDestination.EventDestinationProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-eventdestination.html#cfn-ses-configurationseteventdestination-eventdestination-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetEventDestination.EventDestinationProperty", jsii_struct_bases=[_EventDestinationProperty])
    class EventDestinationProperty(_EventDestinationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-eventdestination.html
        Stability:
            experimental
        """
        matchingEventTypes: typing.List[str]
        """``CfnConfigurationSetEventDestination.EventDestinationProperty.MatchingEventTypes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-eventdestination.html#cfn-ses-configurationseteventdestination-eventdestination-matchingeventtypes
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty", jsii_struct_bases=[])
    class KinesisFirehoseDestinationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-kinesisfirehosedestination.html
        Stability:
            experimental
        """
        deliveryStreamArn: str
        """``CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty.DeliveryStreamARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-kinesisfirehosedestination.html#cfn-ses-configurationseteventdestination-kinesisfirehosedestination-deliverystreamarn
        Stability:
            experimental
        """

        iamRoleArn: str
        """``CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty.IAMRoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-configurationseteventdestination-kinesisfirehosedestination.html#cfn-ses-configurationseteventdestination-kinesisfirehosedestination-iamrolearn
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetEventDestinationProps", jsii_struct_bases=[])
class CfnConfigurationSetEventDestinationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::SES::ConfigurationSetEventDestination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationseteventdestination.html
    Stability:
        experimental
    """
    configurationSetName: str
    """``AWS::SES::ConfigurationSetEventDestination.ConfigurationSetName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationseteventdestination.html#cfn-ses-configurationseteventdestination-configurationsetname
    Stability:
        experimental
    """

    eventDestination: typing.Union["CfnConfigurationSetEventDestination.EventDestinationProperty", aws_cdk.cdk.Token]
    """``AWS::SES::ConfigurationSetEventDestination.EventDestination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationseteventdestination.html#cfn-ses-configurationseteventdestination-eventdestination
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnConfigurationSetProps", jsii_struct_bases=[])
class CfnConfigurationSetProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::SES::ConfigurationSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationset.html
    Stability:
        experimental
    """
    name: str
    """``AWS::SES::ConfigurationSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-configurationset.html#cfn-ses-configurationset-name
    Stability:
        experimental
    """

class CfnReceiptFilter(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.CfnReceiptFilter"):
    """A CloudFormation ``AWS::SES::ReceiptFilter``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptfilter.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SES::ReceiptFilter
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, filter: typing.Union[aws_cdk.cdk.Token, "FilterProperty"]) -> None:
        """Create a new ``AWS::SES::ReceiptFilter``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            filter: ``AWS::SES::ReceiptFilter.Filter``.

        Stability:
            experimental
        """
        props: CfnReceiptFilterProps = {"filter": filter}

        jsii.create(CfnReceiptFilter, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnReceiptFilterProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="receiptFilterName")
    def receipt_filter_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "receiptFilterName")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FilterProperty(jsii.compat.TypedDict, total=False):
        name: str
        """``CfnReceiptFilter.FilterProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptfilter-filter.html#cfn-ses-receiptfilter-filter-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptFilter.FilterProperty", jsii_struct_bases=[_FilterProperty])
    class FilterProperty(_FilterProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptfilter-filter.html
        Stability:
            experimental
        """
        ipFilter: typing.Union[aws_cdk.cdk.Token, "CfnReceiptFilter.IpFilterProperty"]
        """``CfnReceiptFilter.FilterProperty.IpFilter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptfilter-filter.html#cfn-ses-receiptfilter-filter-ipfilter
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptFilter.IpFilterProperty", jsii_struct_bases=[])
    class IpFilterProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptfilter-ipfilter.html
        Stability:
            experimental
        """
        cidr: str
        """``CfnReceiptFilter.IpFilterProperty.Cidr``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptfilter-ipfilter.html#cfn-ses-receiptfilter-ipfilter-cidr
        Stability:
            experimental
        """

        policy: str
        """``CfnReceiptFilter.IpFilterProperty.Policy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptfilter-ipfilter.html#cfn-ses-receiptfilter-ipfilter-policy
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptFilterProps", jsii_struct_bases=[])
class CfnReceiptFilterProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::SES::ReceiptFilter``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptfilter.html
    Stability:
        experimental
    """
    filter: typing.Union[aws_cdk.cdk.Token, "CfnReceiptFilter.FilterProperty"]
    """``AWS::SES::ReceiptFilter.Filter``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptfilter.html#cfn-ses-receiptfilter-filter
    Stability:
        experimental
    """

class CfnReceiptRule(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.CfnReceiptRule"):
    """A CloudFormation ``AWS::SES::ReceiptRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SES::ReceiptRule
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, rule: typing.Union[aws_cdk.cdk.Token, "RuleProperty"], rule_set_name: str, after: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SES::ReceiptRule``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            rule: ``AWS::SES::ReceiptRule.Rule``.
            ruleSetName: ``AWS::SES::ReceiptRule.RuleSetName``.
            after: ``AWS::SES::ReceiptRule.After``.

        Stability:
            experimental
        """
        props: CfnReceiptRuleProps = {"rule": rule, "ruleSetName": rule_set_name}

        if after is not None:
            props["after"] = after

        jsii.create(CfnReceiptRule, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnReceiptRuleProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="receiptRuleName")
    def receipt_rule_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "receiptRuleName")

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.ActionProperty", jsii_struct_bases=[])
    class ActionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html
        Stability:
            experimental
        """
        addHeaderAction: typing.Union["CfnReceiptRule.AddHeaderActionProperty", aws_cdk.cdk.Token]
        """``CfnReceiptRule.ActionProperty.AddHeaderAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-addheaderaction
        Stability:
            experimental
        """

        bounceAction: typing.Union["CfnReceiptRule.BounceActionProperty", aws_cdk.cdk.Token]
        """``CfnReceiptRule.ActionProperty.BounceAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-bounceaction
        Stability:
            experimental
        """

        lambdaAction: typing.Union["CfnReceiptRule.LambdaActionProperty", aws_cdk.cdk.Token]
        """``CfnReceiptRule.ActionProperty.LambdaAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-lambdaaction
        Stability:
            experimental
        """

        s3Action: typing.Union["CfnReceiptRule.S3ActionProperty", aws_cdk.cdk.Token]
        """``CfnReceiptRule.ActionProperty.S3Action``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-s3action
        Stability:
            experimental
        """

        snsAction: typing.Union["CfnReceiptRule.SNSActionProperty", aws_cdk.cdk.Token]
        """``CfnReceiptRule.ActionProperty.SNSAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-snsaction
        Stability:
            experimental
        """

        stopAction: typing.Union["CfnReceiptRule.StopActionProperty", aws_cdk.cdk.Token]
        """``CfnReceiptRule.ActionProperty.StopAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-stopaction
        Stability:
            experimental
        """

        workmailAction: typing.Union["CfnReceiptRule.WorkmailActionProperty", aws_cdk.cdk.Token]
        """``CfnReceiptRule.ActionProperty.WorkmailAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-action.html#cfn-ses-receiptrule-action-workmailaction
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.AddHeaderActionProperty", jsii_struct_bases=[])
    class AddHeaderActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-addheaderaction.html
        Stability:
            experimental
        """
        headerName: str
        """``CfnReceiptRule.AddHeaderActionProperty.HeaderName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-addheaderaction.html#cfn-ses-receiptrule-addheaderaction-headername
        Stability:
            experimental
        """

        headerValue: str
        """``CfnReceiptRule.AddHeaderActionProperty.HeaderValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-addheaderaction.html#cfn-ses-receiptrule-addheaderaction-headervalue
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _BounceActionProperty(jsii.compat.TypedDict, total=False):
        statusCode: str
        """``CfnReceiptRule.BounceActionProperty.StatusCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-bounceaction.html#cfn-ses-receiptrule-bounceaction-statuscode
        Stability:
            experimental
        """
        topicArn: str
        """``CfnReceiptRule.BounceActionProperty.TopicArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-bounceaction.html#cfn-ses-receiptrule-bounceaction-topicarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.BounceActionProperty", jsii_struct_bases=[_BounceActionProperty])
    class BounceActionProperty(_BounceActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-bounceaction.html
        Stability:
            experimental
        """
        message: str
        """``CfnReceiptRule.BounceActionProperty.Message``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-bounceaction.html#cfn-ses-receiptrule-bounceaction-message
        Stability:
            experimental
        """

        sender: str
        """``CfnReceiptRule.BounceActionProperty.Sender``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-bounceaction.html#cfn-ses-receiptrule-bounceaction-sender
        Stability:
            experimental
        """

        smtpReplyCode: str
        """``CfnReceiptRule.BounceActionProperty.SmtpReplyCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-bounceaction.html#cfn-ses-receiptrule-bounceaction-smtpreplycode
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LambdaActionProperty(jsii.compat.TypedDict, total=False):
        invocationType: str
        """``CfnReceiptRule.LambdaActionProperty.InvocationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-lambdaaction.html#cfn-ses-receiptrule-lambdaaction-invocationtype
        Stability:
            experimental
        """
        topicArn: str
        """``CfnReceiptRule.LambdaActionProperty.TopicArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-lambdaaction.html#cfn-ses-receiptrule-lambdaaction-topicarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.LambdaActionProperty", jsii_struct_bases=[_LambdaActionProperty])
    class LambdaActionProperty(_LambdaActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-lambdaaction.html
        Stability:
            experimental
        """
        functionArn: str
        """``CfnReceiptRule.LambdaActionProperty.FunctionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-lambdaaction.html#cfn-ses-receiptrule-lambdaaction-functionarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.RuleProperty", jsii_struct_bases=[])
    class RuleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html
        Stability:
            experimental
        """
        actions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnReceiptRule.ActionProperty"]]]
        """``CfnReceiptRule.RuleProperty.Actions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html#cfn-ses-receiptrule-rule-actions
        Stability:
            experimental
        """

        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnReceiptRule.RuleProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html#cfn-ses-receiptrule-rule-enabled
        Stability:
            experimental
        """

        name: str
        """``CfnReceiptRule.RuleProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html#cfn-ses-receiptrule-rule-name
        Stability:
            experimental
        """

        recipients: typing.List[str]
        """``CfnReceiptRule.RuleProperty.Recipients``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html#cfn-ses-receiptrule-rule-recipients
        Stability:
            experimental
        """

        scanEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnReceiptRule.RuleProperty.ScanEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html#cfn-ses-receiptrule-rule-scanenabled
        Stability:
            experimental
        """

        tlsPolicy: str
        """``CfnReceiptRule.RuleProperty.TlsPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-rule.html#cfn-ses-receiptrule-rule-tlspolicy
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _S3ActionProperty(jsii.compat.TypedDict, total=False):
        kmsKeyArn: str
        """``CfnReceiptRule.S3ActionProperty.KmsKeyArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-s3action.html#cfn-ses-receiptrule-s3action-kmskeyarn
        Stability:
            experimental
        """
        objectKeyPrefix: str
        """``CfnReceiptRule.S3ActionProperty.ObjectKeyPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-s3action.html#cfn-ses-receiptrule-s3action-objectkeyprefix
        Stability:
            experimental
        """
        topicArn: str
        """``CfnReceiptRule.S3ActionProperty.TopicArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-s3action.html#cfn-ses-receiptrule-s3action-topicarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.S3ActionProperty", jsii_struct_bases=[_S3ActionProperty])
    class S3ActionProperty(_S3ActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-s3action.html
        Stability:
            experimental
        """
        bucketName: str
        """``CfnReceiptRule.S3ActionProperty.BucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-s3action.html#cfn-ses-receiptrule-s3action-bucketname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.SNSActionProperty", jsii_struct_bases=[])
    class SNSActionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-snsaction.html
        Stability:
            experimental
        """
        encoding: str
        """``CfnReceiptRule.SNSActionProperty.Encoding``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-snsaction.html#cfn-ses-receiptrule-snsaction-encoding
        Stability:
            experimental
        """

        topicArn: str
        """``CfnReceiptRule.SNSActionProperty.TopicArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-snsaction.html#cfn-ses-receiptrule-snsaction-topicarn
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _StopActionProperty(jsii.compat.TypedDict, total=False):
        topicArn: str
        """``CfnReceiptRule.StopActionProperty.TopicArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-stopaction.html#cfn-ses-receiptrule-stopaction-topicarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.StopActionProperty", jsii_struct_bases=[_StopActionProperty])
    class StopActionProperty(_StopActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-stopaction.html
        Stability:
            experimental
        """
        scope: str
        """``CfnReceiptRule.StopActionProperty.Scope``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-stopaction.html#cfn-ses-receiptrule-stopaction-scope
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _WorkmailActionProperty(jsii.compat.TypedDict, total=False):
        topicArn: str
        """``CfnReceiptRule.WorkmailActionProperty.TopicArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-workmailaction.html#cfn-ses-receiptrule-workmailaction-topicarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRule.WorkmailActionProperty", jsii_struct_bases=[_WorkmailActionProperty])
    class WorkmailActionProperty(_WorkmailActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-workmailaction.html
        Stability:
            experimental
        """
        organizationArn: str
        """``CfnReceiptRule.WorkmailActionProperty.OrganizationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-receiptrule-workmailaction.html#cfn-ses-receiptrule-workmailaction-organizationarn
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnReceiptRuleProps(jsii.compat.TypedDict, total=False):
    after: str
    """``AWS::SES::ReceiptRule.After``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html#cfn-ses-receiptrule-after
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRuleProps", jsii_struct_bases=[_CfnReceiptRuleProps])
class CfnReceiptRuleProps(_CfnReceiptRuleProps):
    """Properties for defining a ``AWS::SES::ReceiptRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html
    Stability:
        experimental
    """
    rule: typing.Union[aws_cdk.cdk.Token, "CfnReceiptRule.RuleProperty"]
    """``AWS::SES::ReceiptRule.Rule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html#cfn-ses-receiptrule-rule
    Stability:
        experimental
    """

    ruleSetName: str
    """``AWS::SES::ReceiptRule.RuleSetName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptrule.html#cfn-ses-receiptrule-rulesetname
    Stability:
        experimental
    """

class CfnReceiptRuleSet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.CfnReceiptRuleSet"):
    """A CloudFormation ``AWS::SES::ReceiptRuleSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptruleset.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SES::ReceiptRuleSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, rule_set_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::SES::ReceiptRuleSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            ruleSetName: ``AWS::SES::ReceiptRuleSet.RuleSetName``.

        Stability:
            experimental
        """
        props: CfnReceiptRuleSetProps = {}

        if rule_set_name is not None:
            props["ruleSetName"] = rule_set_name

        jsii.create(CfnReceiptRuleSet, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnReceiptRuleSetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="receiptRuleSetName")
    def receipt_rule_set_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "receiptRuleSetName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnReceiptRuleSetProps", jsii_struct_bases=[])
class CfnReceiptRuleSetProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::SES::ReceiptRuleSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptruleset.html
    Stability:
        experimental
    """
    ruleSetName: str
    """``AWS::SES::ReceiptRuleSet.RuleSetName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-receiptruleset.html#cfn-ses-receiptruleset-rulesetname
    Stability:
        experimental
    """

class CfnTemplate(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.CfnTemplate"):
    """A CloudFormation ``AWS::SES::Template``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-template.html
    Stability:
        experimental
    cloudformationResource:
        AWS::SES::Template
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, template: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["TemplateProperty"]]]=None) -> None:
        """Create a new ``AWS::SES::Template``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            template: ``AWS::SES::Template.Template``.

        Stability:
            experimental
        """
        props: CfnTemplateProps = {}

        if template is not None:
            props["template"] = template

        jsii.create(CfnTemplate, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnTemplateProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="templateId")
    def template_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "templateId")

    @jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnTemplate.TemplateProperty", jsii_struct_bases=[])
    class TemplateProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-template-template.html
        Stability:
            experimental
        """
        htmlPart: str
        """``CfnTemplate.TemplateProperty.HtmlPart``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-template-template.html#cfn-ses-template-template-htmlpart
        Stability:
            experimental
        """

        subjectPart: str
        """``CfnTemplate.TemplateProperty.SubjectPart``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-template-template.html#cfn-ses-template-template-subjectpart
        Stability:
            experimental
        """

        templateName: str
        """``CfnTemplate.TemplateProperty.TemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-template-template.html#cfn-ses-template-template-templatename
        Stability:
            experimental
        """

        textPart: str
        """``CfnTemplate.TemplateProperty.TextPart``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ses-template-template.html#cfn-ses-template-template-textpart
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.CfnTemplateProps", jsii_struct_bases=[])
class CfnTemplateProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::SES::Template``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-template.html
    Stability:
        experimental
    """
    template: typing.Union[aws_cdk.cdk.Token, "CfnTemplate.TemplateProperty"]
    """``AWS::SES::Template.Template``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ses-template.html#cfn-ses-template-template
    Stability:
        experimental
    """

class DropSpamReceiptRule(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.DropSpamReceiptRule"):
    """A rule added at the top of the rule set to drop spam/virus.

    See:
        https://docs.aws.amazon.com/ses/latest/DeveloperGuide/receiving-email-action-lambda-example-functions.html
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, rule_set: "IReceiptRuleSet", actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            ruleSet: The name of the rule set that the receipt rule will be added to.
            actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
            after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
            enabled: Whether the rule is active. Default: true
            name: The name for the rule. Default: - A CloudFormation generated name.
            recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
            scanEnabled: Whether to scan for spam and viruses. Default: false
            tlsPolicy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.

        Stability:
            experimental
        """
        props: DropSpamReceiptRuleProps = {"ruleSet": rule_set}

        if actions is not None:
            props["actions"] = actions

        if after is not None:
            props["after"] = after

        if enabled is not None:
            props["enabled"] = enabled

        if name is not None:
            props["name"] = name

        if recipients is not None:
            props["recipients"] = recipients

        if scan_enabled is not None:
            props["scanEnabled"] = scan_enabled

        if tls_policy is not None:
            props["tlsPolicy"] = tls_policy

        jsii.create(DropSpamReceiptRule, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="rule")
    def rule(self) -> "ReceiptRule":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "rule")


@jsii.enum(jsii_type="@aws-cdk/aws-ses.EmailEncoding")
class EmailEncoding(enum.Enum):
    """The type of email encoding to use for a SNS action.

    Stability:
        experimental
    """
    Base64 = "Base64"
    """Base 64.

    Stability:
        experimental
    """
    UTF8 = "UTF8"
    """UTF-8.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-ses.IReceiptRule")
class IReceiptRule(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """A receipt rule.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IReceiptRuleProxy

    @property
    @jsii.member(jsii_name="receiptRuleName")
    def receipt_rule_name(self) -> str:
        """The name of the receipt rule.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IReceiptRuleProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """A receipt rule.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ses.IReceiptRule"
    @property
    @jsii.member(jsii_name="receiptRuleName")
    def receipt_rule_name(self) -> str:
        """The name of the receipt rule.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "receiptRuleName")


@jsii.interface(jsii_type="@aws-cdk/aws-ses.IReceiptRuleAction")
class IReceiptRuleAction(jsii.compat.Protocol):
    """An abstract action for a receipt rule.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IReceiptRuleActionProxy

    @jsii.member(jsii_name="render")
    def render(self) -> "ReceiptRuleActionProps":
        """Renders the action specification.

        Stability:
            experimental
        """
        ...


class _IReceiptRuleActionProxy():
    """An abstract action for a receipt rule.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ses.IReceiptRuleAction"
    @jsii.member(jsii_name="render")
    def render(self) -> "ReceiptRuleActionProps":
        """Renders the action specification.

        Stability:
            experimental
        """
        return jsii.invoke(self, "render", [])


@jsii.interface(jsii_type="@aws-cdk/aws-ses.IReceiptRuleSet")
class IReceiptRuleSet(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """A receipt rule set.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IReceiptRuleSetProxy

    @property
    @jsii.member(jsii_name="receiptRuleSetName")
    def receipt_rule_set_name(self) -> str:
        """The receipt rule set name.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @jsii.member(jsii_name="addRule")
    def add_rule(self, id: str, *, actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None) -> "ReceiptRule":
        """Adds a new receipt rule in this rule set.

        The new rule is added after
        the last added rule unless ``after`` is specified.

        Arguments:
            id: -
            options: -
            actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
            after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
            enabled: Whether the rule is active. Default: true
            name: The name for the rule. Default: - A CloudFormation generated name.
            recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
            scanEnabled: Whether to scan for spam and viruses. Default: false
            tlsPolicy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.

        Stability:
            experimental
        """
        ...


class _IReceiptRuleSetProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """A receipt rule set.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ses.IReceiptRuleSet"
    @property
    @jsii.member(jsii_name="receiptRuleSetName")
    def receipt_rule_set_name(self) -> str:
        """The receipt rule set name.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "receiptRuleSetName")

    @jsii.member(jsii_name="addRule")
    def add_rule(self, id: str, *, actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None) -> "ReceiptRule":
        """Adds a new receipt rule in this rule set.

        The new rule is added after
        the last added rule unless ``after`` is specified.

        Arguments:
            id: -
            options: -
            actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
            after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
            enabled: Whether the rule is active. Default: true
            name: The name for the rule. Default: - A CloudFormation generated name.
            recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
            scanEnabled: Whether to scan for spam and viruses. Default: false
            tlsPolicy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.

        Stability:
            experimental
        """
        options: ReceiptRuleOptions = {}

        if actions is not None:
            options["actions"] = actions

        if after is not None:
            options["after"] = after

        if enabled is not None:
            options["enabled"] = enabled

        if name is not None:
            options["name"] = name

        if recipients is not None:
            options["recipients"] = recipients

        if scan_enabled is not None:
            options["scanEnabled"] = scan_enabled

        if tls_policy is not None:
            options["tlsPolicy"] = tls_policy

        return jsii.invoke(self, "addRule", [id, options])


@jsii.enum(jsii_type="@aws-cdk/aws-ses.LambdaInvocationType")
class LambdaInvocationType(enum.Enum):
    """The type of invocation to use for a Lambda Action.

    Stability:
        experimental
    """
    Event = "Event"
    """The function will be invoked asynchronously.

    Stability:
        experimental
    """
    RequestResponse = "RequestResponse"
    """The function will be invoked sychronously.

    Use RequestResponse only when
    you want to make a mail flow decision, such as whether to stop the receipt
    rule or the receipt rule set.

    Stability:
        experimental
    """

class ReceiptFilter(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptFilter"):
    """A receipt filter.

    When instantiated without props, it creates a
    block all receipt filter.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, ip: typing.Optional[str]=None, name: typing.Optional[str]=None, policy: typing.Optional["ReceiptFilterPolicy"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            ip: The ip address or range to filter. Default: 0.0.0.0/0
            name: The name for the receipt filter. Default: a CloudFormation generated name
            policy: The policy for the filter. Default: Block

        Stability:
            experimental
        """
        props: ReceiptFilterProps = {}

        if ip is not None:
            props["ip"] = ip

        if name is not None:
            props["name"] = name

        if policy is not None:
            props["policy"] = policy

        jsii.create(ReceiptFilter, self, [scope, id, props])


@jsii.enum(jsii_type="@aws-cdk/aws-ses.ReceiptFilterPolicy")
class ReceiptFilterPolicy(enum.Enum):
    """The policy for the receipt filter.

    Stability:
        experimental
    """
    Allow = "Allow"
    """Allow the ip address or range.

    Stability:
        experimental
    """
    Block = "Block"
    """Block the ip address or range.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptFilterProps", jsii_struct_bases=[])
class ReceiptFilterProps(jsii.compat.TypedDict, total=False):
    """Construction properties for a ReceiptFilter.

    Stability:
        experimental
    """
    ip: str
    """The ip address or range to filter.

    Default:
        0.0.0.0/0

    Stability:
        experimental
    """

    name: str
    """The name for the receipt filter.

    Default:
        a CloudFormation generated name

    Stability:
        experimental
    """

    policy: "ReceiptFilterPolicy"
    """The policy for the filter.

    Default:
        Block

    Stability:
        experimental
    """

@jsii.implements(IReceiptRule)
class ReceiptRule(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptRule"):
    """A new receipt rule.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, rule_set: "IReceiptRuleSet", actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            ruleSet: The name of the rule set that the receipt rule will be added to.
            actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
            after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
            enabled: Whether the rule is active. Default: true
            name: The name for the rule. Default: - A CloudFormation generated name.
            recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
            scanEnabled: Whether to scan for spam and viruses. Default: false
            tlsPolicy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.

        Stability:
            experimental
        """
        props: ReceiptRuleProps = {"ruleSet": rule_set}

        if actions is not None:
            props["actions"] = actions

        if after is not None:
            props["after"] = after

        if enabled is not None:
            props["enabled"] = enabled

        if name is not None:
            props["name"] = name

        if recipients is not None:
            props["recipients"] = recipients

        if scan_enabled is not None:
            props["scanEnabled"] = scan_enabled

        if tls_policy is not None:
            props["tlsPolicy"] = tls_policy

        jsii.create(ReceiptRule, self, [scope, id, props])

    @jsii.member(jsii_name="fromReceiptRuleName")
    @classmethod
    def from_receipt_rule_name(cls, scope: aws_cdk.cdk.Construct, id: str, receipt_rule_name: str) -> "IReceiptRule":
        """
        Arguments:
            scope: -
            id: -
            receiptRuleName: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromReceiptRuleName", [scope, id, receipt_rule_name])

    @jsii.member(jsii_name="addAction")
    def add_action(self, action: "IReceiptRuleAction") -> None:
        """Adds an action to this receipt rule.

        Arguments:
            action: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAction", [action])

    @property
    @jsii.member(jsii_name="receiptRuleName")
    def receipt_rule_name(self) -> str:
        """The name of the receipt rule.

        Stability:
            experimental
        """
        return jsii.get(self, "receiptRuleName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleActionProps", jsii_struct_bases=[])
class ReceiptRuleActionProps(jsii.compat.TypedDict, total=False):
    """Properties for a receipt rule action.

    Stability:
        experimental
    """
    addHeaderAction: "CfnReceiptRule.AddHeaderActionProperty"
    """Adds a header to the received email.

    Stability:
        experimental
    """

    bounceAction: "CfnReceiptRule.BounceActionProperty"
    """Rejects the received email by returning a bounce response to the sender and, optionally, publishes a notification to Amazon SNS.

    Stability:
        experimental
    """

    lambdaAction: "CfnReceiptRule.LambdaActionProperty"
    """Calls an AWS Lambda function, and optionally, publishes a notification to Amazon SNS.

    Stability:
        experimental
    """

    s3Action: "CfnReceiptRule.S3ActionProperty"
    """Saves the received message to an Amazon S3 bucket and, optionally, publishes a notification to Amazon SNS.

    Stability:
        experimental
    """

    snsAction: "CfnReceiptRule.SNSActionProperty"
    """Publishes the email content within a notification to Amazon SNS.

    Stability:
        experimental
    """

    stopAction: "CfnReceiptRule.StopActionProperty"
    """Terminates the evaluation of the receipt rule set and optionally publishes a notification to Amazon SNS.

    Stability:
        experimental
    """

    workmailAction: "CfnReceiptRule.WorkmailActionProperty"
    """Calls Amazon WorkMail and, optionally, publishes a notification to Amazon SNS.

    Stability:
        experimental
    """

@jsii.implements(IReceiptRuleAction)
class ReceiptRuleAddHeaderAction(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptRuleAddHeaderAction"):
    """Adds a header to the received email.

    Stability:
        experimental
    """
    def __init__(self, *, name: str, value: str) -> None:
        """
        Arguments:
            props: -
            name: The name of the header to add. Must be between 1 and 50 characters, inclusive, and consist of alphanumeric (a-z, A-Z, 0-9) characters and dashes only.
            value: The value of the header to add. Must be less than 2048 characters, and must not contain newline characters ("\r" or "\n").

        Stability:
            experimental
        """
        props: ReceiptRuleAddHeaderActionProps = {"name": name, "value": value}

        jsii.create(ReceiptRuleAddHeaderAction, self, [props])

    @jsii.member(jsii_name="render")
    def render(self) -> "ReceiptRuleActionProps":
        """Renders the action specification.

        Stability:
            experimental
        """
        return jsii.invoke(self, "render", [])


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleAddHeaderActionProps", jsii_struct_bases=[])
class ReceiptRuleAddHeaderActionProps(jsii.compat.TypedDict):
    """Construction properties for a ReceiptRuleAddHeaderAction.

    Stability:
        experimental
    """
    name: str
    """The name of the header to add.

    Must be between 1 and 50 characters,
    inclusive, and consist of alphanumeric (a-z, A-Z, 0-9) characters
    and dashes only.

    Stability:
        experimental
    """

    value: str
    """The value of the header to add.

    Must be less than 2048 characters,
    and must not contain newline characters ("\r" or "\n").

    Stability:
        experimental
    """

@jsii.implements(IReceiptRuleAction)
class ReceiptRuleBounceAction(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptRuleBounceAction"):
    """Rejects the received email by returning a bounce response to the sender and, optionally, publishes a notification to Amazon SNS.

    Stability:
        experimental
    """
    def __init__(self, *, sender: str, template: "ReceiptRuleBounceActionTemplate", topic: typing.Optional[aws_cdk.aws_sns.ITopic]=None) -> None:
        """
        Arguments:
            props: -
            sender: The email address of the sender of the bounced email. This is the address from which the bounce message will be sent.
            template: The template containing the message, reply code and status code.
            topic: The SNS topic to notify when the bounce action is taken. Default: no notification

        Stability:
            experimental
        """
        props: ReceiptRuleBounceActionProps = {"sender": sender, "template": template}

        if topic is not None:
            props["topic"] = topic

        jsii.create(ReceiptRuleBounceAction, self, [props])

    @jsii.member(jsii_name="render")
    def render(self) -> "ReceiptRuleActionProps":
        """Renders the action specification.

        Stability:
            experimental
        """
        return jsii.invoke(self, "render", [])

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "ReceiptRuleBounceActionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ReceiptRuleBounceActionProps(jsii.compat.TypedDict, total=False):
    topic: aws_cdk.aws_sns.ITopic
    """The SNS topic to notify when the bounce action is taken.

    Default:
        no notification

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleBounceActionProps", jsii_struct_bases=[_ReceiptRuleBounceActionProps])
class ReceiptRuleBounceActionProps(_ReceiptRuleBounceActionProps):
    """Construction properties for a ReceiptRuleBounceAction.

    Stability:
        experimental
    """
    sender: str
    """The email address of the sender of the bounced email.

    This is the address
    from which the bounce message will be sent.

    Stability:
        experimental
    """

    template: "ReceiptRuleBounceActionTemplate"
    """The template containing the message, reply code and status code.

    Stability:
        experimental
    """

class ReceiptRuleBounceActionTemplate(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptRuleBounceActionTemplate"):
    """A bounce action template.

    Stability:
        experimental
    """
    def __init__(self, *, message: str, smtp_reply_code: str, status_code: typing.Optional[str]=None) -> None:
        """
        Arguments:
            props: -
            message: Human-readable text to include in the bounce message.
            smtpReplyCode: The SMTP reply code, as defined by RFC 5321.
            statusCode: The SMTP enhanced status code, as defined by RFC 3463.

        Stability:
            experimental
        """
        props: ReceiptRuleBounceActionTemplateProps = {"message": message, "smtpReplyCode": smtp_reply_code}

        if status_code is not None:
            props["statusCode"] = status_code

        jsii.create(ReceiptRuleBounceActionTemplate, self, [props])

    @classproperty
    @jsii.member(jsii_name="MailboxDoesNotExist")
    def MAILBOX_DOES_NOT_EXIST(cls) -> "ReceiptRuleBounceActionTemplate":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MailboxDoesNotExist")

    @classproperty
    @jsii.member(jsii_name="MailboxFull")
    def MAILBOX_FULL(cls) -> "ReceiptRuleBounceActionTemplate":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MailboxFull")

    @classproperty
    @jsii.member(jsii_name="MessageContentRejected")
    def MESSAGE_CONTENT_REJECTED(cls) -> "ReceiptRuleBounceActionTemplate":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MessageContentRejected")

    @classproperty
    @jsii.member(jsii_name="MessageTooLarge")
    def MESSAGE_TOO_LARGE(cls) -> "ReceiptRuleBounceActionTemplate":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MessageTooLarge")

    @classproperty
    @jsii.member(jsii_name="TemporaryFailure")
    def TEMPORARY_FAILURE(cls) -> "ReceiptRuleBounceActionTemplate":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "TemporaryFailure")

    @property
    @jsii.member(jsii_name="message")
    def message(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "message")

    @property
    @jsii.member(jsii_name="smtpReplyCode")
    def smtp_reply_code(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "smtpReplyCode")

    @property
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "statusCode")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ReceiptRuleBounceActionTemplateProps(jsii.compat.TypedDict, total=False):
    statusCode: str
    """The SMTP enhanced status code, as defined by RFC 3463.

    See:
        https://tools.ietf.org/html/rfc3463
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleBounceActionTemplateProps", jsii_struct_bases=[_ReceiptRuleBounceActionTemplateProps])
class ReceiptRuleBounceActionTemplateProps(_ReceiptRuleBounceActionTemplateProps):
    """Construction properties for a ReceiptRuleBounceActionTemplate.

    Stability:
        experimental
    """
    message: str
    """Human-readable text to include in the bounce message.

    Stability:
        experimental
    """

    smtpReplyCode: str
    """The SMTP reply code, as defined by RFC 5321.

    See:
        https://tools.ietf.org/html/rfc5321
    Stability:
        experimental
    """

@jsii.implements(IReceiptRuleAction)
class ReceiptRuleLambdaAction(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptRuleLambdaAction"):
    """Calls an AWS Lambda function, and optionally, publishes a notification to Amazon SNS.

    Stability:
        experimental
    """
    def __init__(self, *, function: aws_cdk.aws_lambda.IFunction, invocation_type: typing.Optional["LambdaInvocationType"]=None, topic: typing.Optional[aws_cdk.aws_sns.ITopic]=None) -> None:
        """
        Arguments:
            props: -
            function: The Lambda function to invoke.
            invocationType: The invocation type of the Lambda function. Default: Event
            topic: The SNS topic to notify when the Lambda action is taken. Default: no notification

        Stability:
            experimental
        """
        props: ReceiptRuleLambdaActionProps = {"function": function}

        if invocation_type is not None:
            props["invocationType"] = invocation_type

        if topic is not None:
            props["topic"] = topic

        jsii.create(ReceiptRuleLambdaAction, self, [props])

    @jsii.member(jsii_name="render")
    def render(self) -> "ReceiptRuleActionProps":
        """Renders the action specification.

        Stability:
            experimental
        """
        return jsii.invoke(self, "render", [])

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "ReceiptRuleLambdaActionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ReceiptRuleLambdaActionProps(jsii.compat.TypedDict, total=False):
    invocationType: "LambdaInvocationType"
    """The invocation type of the Lambda function.

    Default:
        Event

    Stability:
        experimental
    """
    topic: aws_cdk.aws_sns.ITopic
    """The SNS topic to notify when the Lambda action is taken.

    Default:
        no notification

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleLambdaActionProps", jsii_struct_bases=[_ReceiptRuleLambdaActionProps])
class ReceiptRuleLambdaActionProps(_ReceiptRuleLambdaActionProps):
    """Construction properties for a ReceiptRuleLambdaAction.

    Stability:
        experimental
    """
    function: aws_cdk.aws_lambda.IFunction
    """The Lambda function to invoke.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleOptions", jsii_struct_bases=[])
class ReceiptRuleOptions(jsii.compat.TypedDict, total=False):
    """Options to add a receipt rule to a receipt rule set.

    Stability:
        experimental
    """
    actions: typing.List["IReceiptRuleAction"]
    """An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule.

    Default:
        - No actions.

    Stability:
        experimental
    """

    after: "IReceiptRule"
    """An existing rule after which the new rule will be placed.

    Default:
        - The new rule is inserted at the beginning of the rule list.

    Stability:
        experimental
    """

    enabled: bool
    """Whether the rule is active.

    Default:
        true

    Stability:
        experimental
    """

    name: str
    """The name for the rule.

    Default:
        - A CloudFormation generated name.

    Stability:
        experimental
    """

    recipients: typing.List[str]
    """The recipient domains and email addresses that the receipt rule applies to.

    Default:
        - Match all recipients under all verified domains.

    Stability:
        experimental
    """

    scanEnabled: bool
    """Whether to scan for spam and viruses.

    Default:
        false

    Stability:
        experimental
    """

    tlsPolicy: "TlsPolicy"
    """Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS).

    Default:
        - Optional which will not check for TLS.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleProps", jsii_struct_bases=[ReceiptRuleOptions])
class ReceiptRuleProps(ReceiptRuleOptions, jsii.compat.TypedDict):
    """Construction properties for a ReceiptRule.

    Stability:
        experimental
    """
    ruleSet: "IReceiptRuleSet"
    """The name of the rule set that the receipt rule will be added to.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ses.DropSpamReceiptRuleProps", jsii_struct_bases=[ReceiptRuleProps])
class DropSpamReceiptRuleProps(ReceiptRuleProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    pass

@jsii.implements(IReceiptRuleAction)
class ReceiptRuleS3Action(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptRuleS3Action"):
    """Saves the received message to an Amazon S3 bucket and, optionally, publishes a notification to Amazon SNS.

    Stability:
        experimental
    """
    def __init__(self, *, bucket: aws_cdk.aws_s3.IBucket, kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, object_key_prefix: typing.Optional[str]=None, topic: typing.Optional[aws_cdk.aws_sns.ITopic]=None) -> None:
        """
        Arguments:
            props: -
            bucket: The S3 bucket that incoming email will be saved to.
            kmsKey: The master key that SES should use to encrypt your emails before saving them to the S3 bucket. Default: no encryption
            objectKeyPrefix: The key prefix of the S3 bucket. Default: no prefix
            topic: The SNS topic to notify when the S3 action is taken. Default: no notification

        Stability:
            experimental
        """
        props: ReceiptRuleS3ActionProps = {"bucket": bucket}

        if kms_key is not None:
            props["kmsKey"] = kms_key

        if object_key_prefix is not None:
            props["objectKeyPrefix"] = object_key_prefix

        if topic is not None:
            props["topic"] = topic

        jsii.create(ReceiptRuleS3Action, self, [props])

    @jsii.member(jsii_name="render")
    def render(self) -> "ReceiptRuleActionProps":
        """Renders the action specification.

        Stability:
            experimental
        """
        return jsii.invoke(self, "render", [])

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "ReceiptRuleS3ActionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ReceiptRuleS3ActionProps(jsii.compat.TypedDict, total=False):
    kmsKey: aws_cdk.aws_kms.IKey
    """The master key that SES should use to encrypt your emails before saving them to the S3 bucket.

    Default:
        no encryption

    Stability:
        experimental
    """
    objectKeyPrefix: str
    """The key prefix of the S3 bucket.

    Default:
        no prefix

    Stability:
        experimental
    """
    topic: aws_cdk.aws_sns.ITopic
    """The SNS topic to notify when the S3 action is taken.

    Default:
        no notification

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleS3ActionProps", jsii_struct_bases=[_ReceiptRuleS3ActionProps])
class ReceiptRuleS3ActionProps(_ReceiptRuleS3ActionProps):
    """Construction properties for a ReceiptRuleS3Action.

    Stability:
        experimental
    """
    bucket: aws_cdk.aws_s3.IBucket
    """The S3 bucket that incoming email will be saved to.

    Stability:
        experimental
    """

@jsii.implements(IReceiptRuleSet)
class ReceiptRuleSet(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptRuleSet"):
    """A new receipt rule set.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, drop_spam: typing.Optional[bool]=None, name: typing.Optional[str]=None, rules: typing.Optional[typing.List["ReceiptRuleOptions"]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            dropSpam: Whether to add a first rule to stop processing messages that have at least one spam indicator. Default: false
            name: The name for the receipt rule set. Default: - A CloudFormation generated name.
            rules: The list of rules to add to this rule set. Rules are added in the same order as they appear in the list. Default: - No rules are added to the rule set.

        Stability:
            experimental
        """
        props: ReceiptRuleSetProps = {}

        if drop_spam is not None:
            props["dropSpam"] = drop_spam

        if name is not None:
            props["name"] = name

        if rules is not None:
            props["rules"] = rules

        jsii.create(ReceiptRuleSet, self, [scope, id, props])

    @jsii.member(jsii_name="fromReceiptRuleSetName")
    @classmethod
    def from_receipt_rule_set_name(cls, scope: aws_cdk.cdk.Construct, id: str, receipt_rule_set_name: str) -> "IReceiptRuleSet":
        """Import an exported receipt rule set.

        Arguments:
            scope: -
            id: -
            receiptRuleSetName: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromReceiptRuleSetName", [scope, id, receipt_rule_set_name])

    @jsii.member(jsii_name="addDropSpamRule")
    def _add_drop_spam_rule(self) -> None:
        """Adds a drop spam rule.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addDropSpamRule", [])

    @jsii.member(jsii_name="addRule")
    def add_rule(self, id: str, *, actions: typing.Optional[typing.List["IReceiptRuleAction"]]=None, after: typing.Optional["IReceiptRule"]=None, enabled: typing.Optional[bool]=None, name: typing.Optional[str]=None, recipients: typing.Optional[typing.List[str]]=None, scan_enabled: typing.Optional[bool]=None, tls_policy: typing.Optional["TlsPolicy"]=None) -> "ReceiptRule":
        """Adds a new receipt rule in this rule set.

        The new rule is added after
        the last added rule unless ``after`` is specified.

        Arguments:
            id: -
            options: -
            actions: An ordered list of actions to perform on messages that match at least one of the recipient email addresses or domains specified in the receipt rule. Default: - No actions.
            after: An existing rule after which the new rule will be placed. Default: - The new rule is inserted at the beginning of the rule list.
            enabled: Whether the rule is active. Default: true
            name: The name for the rule. Default: - A CloudFormation generated name.
            recipients: The recipient domains and email addresses that the receipt rule applies to. Default: - Match all recipients under all verified domains.
            scanEnabled: Whether to scan for spam and viruses. Default: false
            tlsPolicy: Whether Amazon SES should require that incoming email is delivered over a connection encrypted with Transport Layer Security (TLS). Default: - Optional which will not check for TLS.

        Stability:
            experimental
        """
        options: ReceiptRuleOptions = {}

        if actions is not None:
            options["actions"] = actions

        if after is not None:
            options["after"] = after

        if enabled is not None:
            options["enabled"] = enabled

        if name is not None:
            options["name"] = name

        if recipients is not None:
            options["recipients"] = recipients

        if scan_enabled is not None:
            options["scanEnabled"] = scan_enabled

        if tls_policy is not None:
            options["tlsPolicy"] = tls_policy

        return jsii.invoke(self, "addRule", [id, options])

    @property
    @jsii.member(jsii_name="receiptRuleSetName")
    def receipt_rule_set_name(self) -> str:
        """The receipt rule set name.

        Stability:
            experimental
        """
        return jsii.get(self, "receiptRuleSetName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleSetProps", jsii_struct_bases=[])
class ReceiptRuleSetProps(jsii.compat.TypedDict, total=False):
    """Construction properties for a ReceiptRuleSet.

    Stability:
        experimental
    """
    dropSpam: bool
    """Whether to add a first rule to stop processing messages that have at least one spam indicator.

    Default:
        false

    Stability:
        experimental
    """

    name: str
    """The name for the receipt rule set.

    Default:
        - A CloudFormation generated name.

    Stability:
        experimental
    """

    rules: typing.List["ReceiptRuleOptions"]
    """The list of rules to add to this rule set.

    Rules are added in the same
    order as they appear in the list.

    Default:
        - No rules are added to the rule set.

    Stability:
        experimental
    """

@jsii.implements(IReceiptRuleAction)
class ReceiptRuleSnsAction(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptRuleSnsAction"):
    """Publishes the email content within a notification to Amazon SNS.

    Stability:
        experimental
    """
    def __init__(self, *, topic: aws_cdk.aws_sns.ITopic, encoding: typing.Optional["EmailEncoding"]=None) -> None:
        """
        Arguments:
            props: -
            topic: The SNS topic to notify.
            encoding: The encoding to use for the email within the Amazon SNS notification. Default: UTF-8

        Stability:
            experimental
        """
        props: ReceiptRuleSnsActionProps = {"topic": topic}

        if encoding is not None:
            props["encoding"] = encoding

        jsii.create(ReceiptRuleSnsAction, self, [props])

    @jsii.member(jsii_name="render")
    def render(self) -> "ReceiptRuleActionProps":
        """Renders the action specification.

        Stability:
            experimental
        """
        return jsii.invoke(self, "render", [])

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "ReceiptRuleSnsActionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ReceiptRuleSnsActionProps(jsii.compat.TypedDict, total=False):
    encoding: "EmailEncoding"
    """The encoding to use for the email within the Amazon SNS notification.

    Default:
        UTF-8

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleSnsActionProps", jsii_struct_bases=[_ReceiptRuleSnsActionProps])
class ReceiptRuleSnsActionProps(_ReceiptRuleSnsActionProps):
    """Construction properties for a ReceiptRuleSnsAction.

    Stability:
        experimental
    """
    topic: aws_cdk.aws_sns.ITopic
    """The SNS topic to notify.

    Stability:
        experimental
    """

@jsii.implements(IReceiptRuleAction)
class ReceiptRuleStopAction(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.ReceiptRuleStopAction"):
    """Terminates the evaluation of the receipt rule set and optionally publishes a notification to Amazon SNS.

    Stability:
        experimental
    """
    def __init__(self, *, topic: typing.Optional[aws_cdk.aws_sns.ITopic]=None) -> None:
        """
        Arguments:
            props: -
            topic: The SNS topic to notify when the stop action is taken.

        Stability:
            experimental
        """
        props: ReceiptRuleStopActionProps = {}

        if topic is not None:
            props["topic"] = topic

        jsii.create(ReceiptRuleStopAction, self, [props])

    @jsii.member(jsii_name="render")
    def render(self) -> "ReceiptRuleActionProps":
        """Renders the action specification.

        Stability:
            experimental
        """
        return jsii.invoke(self, "render", [])

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> typing.Optional["ReceiptRuleStopActionProps"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.ReceiptRuleStopActionProps", jsii_struct_bases=[])
class ReceiptRuleStopActionProps(jsii.compat.TypedDict, total=False):
    """Construction properties for a ReceiptRuleStopAction.

    Stability:
        experimental
    """
    topic: aws_cdk.aws_sns.ITopic
    """The SNS topic to notify when the stop action is taken.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ses.TlsPolicy")
class TlsPolicy(enum.Enum):
    """The type of TLS policy for a receipt rule.

    Stability:
        experimental
    """
    Optional = "Optional"
    """Do not check for TLS.

    Stability:
        experimental
    """
    Require = "Require"
    """Bounce emails that are not received over TLS.

    Stability:
        experimental
    """

class WhiteListReceiptFilter(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ses.WhiteListReceiptFilter"):
    """A white list receipt filter.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, ips: typing.List[str]) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            ips: A list of ip addresses or ranges to white list.

        Stability:
            experimental
        """
        props: WhiteListReceiptFilterProps = {"ips": ips}

        jsii.create(WhiteListReceiptFilter, self, [scope, id, props])


@jsii.data_type(jsii_type="@aws-cdk/aws-ses.WhiteListReceiptFilterProps", jsii_struct_bases=[])
class WhiteListReceiptFilterProps(jsii.compat.TypedDict):
    """Construction properties for a WhiteListReceiptFilter.

    Stability:
        experimental
    """
    ips: typing.List[str]
    """A list of ip addresses or ranges to white list.

    Stability:
        experimental
    """

__all__ = ["CfnConfigurationSet", "CfnConfigurationSetEventDestination", "CfnConfigurationSetEventDestinationProps", "CfnConfigurationSetProps", "CfnReceiptFilter", "CfnReceiptFilterProps", "CfnReceiptRule", "CfnReceiptRuleProps", "CfnReceiptRuleSet", "CfnReceiptRuleSetProps", "CfnTemplate", "CfnTemplateProps", "DropSpamReceiptRule", "DropSpamReceiptRuleProps", "EmailEncoding", "IReceiptRule", "IReceiptRuleAction", "IReceiptRuleSet", "LambdaInvocationType", "ReceiptFilter", "ReceiptFilterPolicy", "ReceiptFilterProps", "ReceiptRule", "ReceiptRuleActionProps", "ReceiptRuleAddHeaderAction", "ReceiptRuleAddHeaderActionProps", "ReceiptRuleBounceAction", "ReceiptRuleBounceActionProps", "ReceiptRuleBounceActionTemplate", "ReceiptRuleBounceActionTemplateProps", "ReceiptRuleLambdaAction", "ReceiptRuleLambdaActionProps", "ReceiptRuleOptions", "ReceiptRuleProps", "ReceiptRuleS3Action", "ReceiptRuleS3ActionProps", "ReceiptRuleSet", "ReceiptRuleSetProps", "ReceiptRuleSnsAction", "ReceiptRuleSnsActionProps", "ReceiptRuleStopAction", "ReceiptRuleStopActionProps", "TlsPolicy", "WhiteListReceiptFilter", "WhiteListReceiptFilterProps", "__jsii_assembly__"]

publication.publish()
