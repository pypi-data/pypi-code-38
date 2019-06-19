import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-pinpointemail", "0.35.0", __name__, "aws-pinpointemail@0.35.0.jsii.tgz")
class CfnConfigurationSet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSet"):
    """A CloudFormation ``AWS::PinpointEmail::ConfigurationSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html
    Stability:
        experimental
    cloudformationResource:
        AWS::PinpointEmail::ConfigurationSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, delivery_options: typing.Optional[typing.Union[typing.Optional["DeliveryOptionsProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, reputation_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ReputationOptionsProperty"]]]=None, sending_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SendingOptionsProperty"]]]=None, tags: typing.Optional[typing.List["TagsProperty"]]=None, tracking_options: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["TrackingOptionsProperty"]]]=None) -> None:
        """Create a new ``AWS::PinpointEmail::ConfigurationSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::PinpointEmail::ConfigurationSet.Name``.
            deliveryOptions: ``AWS::PinpointEmail::ConfigurationSet.DeliveryOptions``.
            reputationOptions: ``AWS::PinpointEmail::ConfigurationSet.ReputationOptions``.
            sendingOptions: ``AWS::PinpointEmail::ConfigurationSet.SendingOptions``.
            tags: ``AWS::PinpointEmail::ConfigurationSet.Tags``.
            trackingOptions: ``AWS::PinpointEmail::ConfigurationSet.TrackingOptions``.

        Stability:
            experimental
        """
        props: CfnConfigurationSetProps = {"name": name}

        if delivery_options is not None:
            props["deliveryOptions"] = delivery_options

        if reputation_options is not None:
            props["reputationOptions"] = reputation_options

        if sending_options is not None:
            props["sendingOptions"] = sending_options

        if tags is not None:
            props["tags"] = tags

        if tracking_options is not None:
            props["trackingOptions"] = tracking_options

        jsii.create(CfnConfigurationSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::PinpointEmail::ConfigurationSet.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="deliveryOptions")
    def delivery_options(self) -> typing.Optional[typing.Union[typing.Optional["DeliveryOptionsProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::PinpointEmail::ConfigurationSet.DeliveryOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-deliveryoptions
        Stability:
            experimental
        """
        return jsii.get(self, "deliveryOptions")

    @delivery_options.setter
    def delivery_options(self, value: typing.Optional[typing.Union[typing.Optional["DeliveryOptionsProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "deliveryOptions", value)

    @property
    @jsii.member(jsii_name="reputationOptions")
    def reputation_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ReputationOptionsProperty"]]]:
        """``AWS::PinpointEmail::ConfigurationSet.ReputationOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-reputationoptions
        Stability:
            experimental
        """
        return jsii.get(self, "reputationOptions")

    @reputation_options.setter
    def reputation_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ReputationOptionsProperty"]]]):
        return jsii.set(self, "reputationOptions", value)

    @property
    @jsii.member(jsii_name="sendingOptions")
    def sending_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SendingOptionsProperty"]]]:
        """``AWS::PinpointEmail::ConfigurationSet.SendingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-sendingoptions
        Stability:
            experimental
        """
        return jsii.get(self, "sendingOptions")

    @sending_options.setter
    def sending_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SendingOptionsProperty"]]]):
        return jsii.set(self, "sendingOptions", value)

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List["TagsProperty"]]:
        """``AWS::PinpointEmail::ConfigurationSet.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @tags.setter
    def tags(self, value: typing.Optional[typing.List["TagsProperty"]]):
        return jsii.set(self, "tags", value)

    @property
    @jsii.member(jsii_name="trackingOptions")
    def tracking_options(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["TrackingOptionsProperty"]]]:
        """``AWS::PinpointEmail::ConfigurationSet.TrackingOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-trackingoptions
        Stability:
            experimental
        """
        return jsii.get(self, "trackingOptions")

    @tracking_options.setter
    def tracking_options(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["TrackingOptionsProperty"]]]):
        return jsii.set(self, "trackingOptions", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSet.DeliveryOptionsProperty", jsii_struct_bases=[])
    class DeliveryOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-deliveryoptions.html
        Stability:
            experimental
        """
        sendingPoolName: str
        """``CfnConfigurationSet.DeliveryOptionsProperty.SendingPoolName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-deliveryoptions.html#cfn-pinpointemail-configurationset-deliveryoptions-sendingpoolname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSet.ReputationOptionsProperty", jsii_struct_bases=[])
    class ReputationOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-reputationoptions.html
        Stability:
            experimental
        """
        reputationMetricsEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnConfigurationSet.ReputationOptionsProperty.ReputationMetricsEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-reputationoptions.html#cfn-pinpointemail-configurationset-reputationoptions-reputationmetricsenabled
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSet.SendingOptionsProperty", jsii_struct_bases=[])
    class SendingOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-sendingoptions.html
        Stability:
            experimental
        """
        sendingEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnConfigurationSet.SendingOptionsProperty.SendingEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-sendingoptions.html#cfn-pinpointemail-configurationset-sendingoptions-sendingenabled
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSet.TagsProperty", jsii_struct_bases=[])
    class TagsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-tags.html
        Stability:
            experimental
        """
        key: str
        """``CfnConfigurationSet.TagsProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-tags.html#cfn-pinpointemail-configurationset-tags-key
        Stability:
            experimental
        """

        value: str
        """``CfnConfigurationSet.TagsProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-tags.html#cfn-pinpointemail-configurationset-tags-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSet.TrackingOptionsProperty", jsii_struct_bases=[])
    class TrackingOptionsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-trackingoptions.html
        Stability:
            experimental
        """
        customRedirectDomain: str
        """``CfnConfigurationSet.TrackingOptionsProperty.CustomRedirectDomain``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationset-trackingoptions.html#cfn-pinpointemail-configurationset-trackingoptions-customredirectdomain
        Stability:
            experimental
        """


class CfnConfigurationSetEventDestination(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination"):
    """A CloudFormation ``AWS::PinpointEmail::ConfigurationSetEventDestination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html
    Stability:
        experimental
    cloudformationResource:
        AWS::PinpointEmail::ConfigurationSetEventDestination
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, configuration_set_name: str, event_destination_name: str, event_destination: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EventDestinationProperty"]]]=None) -> None:
        """Create a new ``AWS::PinpointEmail::ConfigurationSetEventDestination``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            configurationSetName: ``AWS::PinpointEmail::ConfigurationSetEventDestination.ConfigurationSetName``.
            eventDestinationName: ``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestinationName``.
            eventDestination: ``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestination``.

        Stability:
            experimental
        """
        props: CfnConfigurationSetEventDestinationProps = {"configurationSetName": configuration_set_name, "eventDestinationName": event_destination_name}

        if event_destination is not None:
            props["eventDestination"] = event_destination

        jsii.create(CfnConfigurationSetEventDestination, self, [scope, id, props])

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
    @jsii.member(jsii_name="configurationSetName")
    def configuration_set_name(self) -> str:
        """``AWS::PinpointEmail::ConfigurationSetEventDestination.ConfigurationSetName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html#cfn-pinpointemail-configurationseteventdestination-configurationsetname
        Stability:
            experimental
        """
        return jsii.get(self, "configurationSetName")

    @configuration_set_name.setter
    def configuration_set_name(self, value: str):
        return jsii.set(self, "configurationSetName", value)

    @property
    @jsii.member(jsii_name="eventDestinationName")
    def event_destination_name(self) -> str:
        """``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestinationName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestinationname
        Stability:
            experimental
        """
        return jsii.get(self, "eventDestinationName")

    @event_destination_name.setter
    def event_destination_name(self, value: str):
        return jsii.set(self, "eventDestinationName", value)

    @property
    @jsii.member(jsii_name="eventDestination")
    def event_destination(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EventDestinationProperty"]]]:
        """``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination
        Stability:
            experimental
        """
        return jsii.get(self, "eventDestination")

    @event_destination.setter
    def event_destination(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EventDestinationProperty"]]]):
        return jsii.set(self, "eventDestination", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination.CloudWatchDestinationProperty", jsii_struct_bases=[])
    class CloudWatchDestinationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-cloudwatchdestination.html
        Stability:
            experimental
        """
        dimensionConfigurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnConfigurationSetEventDestination.DimensionConfigurationProperty"]]]
        """``CfnConfigurationSetEventDestination.CloudWatchDestinationProperty.DimensionConfigurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-cloudwatchdestination.html#cfn-pinpointemail-configurationseteventdestination-cloudwatchdestination-dimensionconfigurations
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination.DimensionConfigurationProperty", jsii_struct_bases=[])
    class DimensionConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-dimensionconfiguration.html
        Stability:
            experimental
        """
        defaultDimensionValue: str
        """``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DefaultDimensionValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-dimensionconfiguration.html#cfn-pinpointemail-configurationseteventdestination-dimensionconfiguration-defaultdimensionvalue
        Stability:
            experimental
        """

        dimensionName: str
        """``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DimensionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-dimensionconfiguration.html#cfn-pinpointemail-configurationseteventdestination-dimensionconfiguration-dimensionname
        Stability:
            experimental
        """

        dimensionValueSource: str
        """``CfnConfigurationSetEventDestination.DimensionConfigurationProperty.DimensionValueSource``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-dimensionconfiguration.html#cfn-pinpointemail-configurationseteventdestination-dimensionconfiguration-dimensionvaluesource
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _EventDestinationProperty(jsii.compat.TypedDict, total=False):
        cloudWatchDestination: typing.Union[aws_cdk.cdk.IResolvable, "CfnConfigurationSetEventDestination.CloudWatchDestinationProperty"]
        """``CfnConfigurationSetEventDestination.EventDestinationProperty.CloudWatchDestination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination-cloudwatchdestination
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnConfigurationSetEventDestination.EventDestinationProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination-enabled
        Stability:
            experimental
        """
        kinesisFirehoseDestination: typing.Union[aws_cdk.cdk.IResolvable, "CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty"]
        """``CfnConfigurationSetEventDestination.EventDestinationProperty.KinesisFirehoseDestination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination-kinesisfirehosedestination
        Stability:
            experimental
        """
        pinpointDestination: typing.Union[aws_cdk.cdk.IResolvable, "CfnConfigurationSetEventDestination.PinpointDestinationProperty"]
        """``CfnConfigurationSetEventDestination.EventDestinationProperty.PinpointDestination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination-pinpointdestination
        Stability:
            experimental
        """
        snsDestination: typing.Union[aws_cdk.cdk.IResolvable, "CfnConfigurationSetEventDestination.SnsDestinationProperty"]
        """``CfnConfigurationSetEventDestination.EventDestinationProperty.SnsDestination``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination-snsdestination
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination.EventDestinationProperty", jsii_struct_bases=[_EventDestinationProperty])
    class EventDestinationProperty(_EventDestinationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html
        Stability:
            experimental
        """
        matchingEventTypes: typing.List[str]
        """``CfnConfigurationSetEventDestination.EventDestinationProperty.MatchingEventTypes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-eventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination-matchingeventtypes
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty", jsii_struct_bases=[])
    class KinesisFirehoseDestinationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-kinesisfirehosedestination.html
        Stability:
            experimental
        """
        deliveryStreamArn: str
        """``CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty.DeliveryStreamArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-kinesisfirehosedestination.html#cfn-pinpointemail-configurationseteventdestination-kinesisfirehosedestination-deliverystreamarn
        Stability:
            experimental
        """

        iamRoleArn: str
        """``CfnConfigurationSetEventDestination.KinesisFirehoseDestinationProperty.IamRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-kinesisfirehosedestination.html#cfn-pinpointemail-configurationseteventdestination-kinesisfirehosedestination-iamrolearn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination.PinpointDestinationProperty", jsii_struct_bases=[])
    class PinpointDestinationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-pinpointdestination.html
        Stability:
            experimental
        """
        applicationArn: str
        """``CfnConfigurationSetEventDestination.PinpointDestinationProperty.ApplicationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-pinpointdestination.html#cfn-pinpointemail-configurationseteventdestination-pinpointdestination-applicationarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestination.SnsDestinationProperty", jsii_struct_bases=[])
    class SnsDestinationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-snsdestination.html
        Stability:
            experimental
        """
        topicArn: str
        """``CfnConfigurationSetEventDestination.SnsDestinationProperty.TopicArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-configurationseteventdestination-snsdestination.html#cfn-pinpointemail-configurationseteventdestination-snsdestination-topicarn
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnConfigurationSetEventDestinationProps(jsii.compat.TypedDict, total=False):
    eventDestination: typing.Union[aws_cdk.cdk.IResolvable, "CfnConfigurationSetEventDestination.EventDestinationProperty"]
    """``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestination
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetEventDestinationProps", jsii_struct_bases=[_CfnConfigurationSetEventDestinationProps])
class CfnConfigurationSetEventDestinationProps(_CfnConfigurationSetEventDestinationProps):
    """Properties for defining a ``AWS::PinpointEmail::ConfigurationSetEventDestination``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html
    Stability:
        experimental
    """
    configurationSetName: str
    """``AWS::PinpointEmail::ConfigurationSetEventDestination.ConfigurationSetName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html#cfn-pinpointemail-configurationseteventdestination-configurationsetname
    Stability:
        experimental
    """

    eventDestinationName: str
    """``AWS::PinpointEmail::ConfigurationSetEventDestination.EventDestinationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationseteventdestination.html#cfn-pinpointemail-configurationseteventdestination-eventdestinationname
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnConfigurationSetProps(jsii.compat.TypedDict, total=False):
    deliveryOptions: typing.Union["CfnConfigurationSet.DeliveryOptionsProperty", aws_cdk.cdk.IResolvable]
    """``AWS::PinpointEmail::ConfigurationSet.DeliveryOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-deliveryoptions
    Stability:
        experimental
    """
    reputationOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnConfigurationSet.ReputationOptionsProperty"]
    """``AWS::PinpointEmail::ConfigurationSet.ReputationOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-reputationoptions
    Stability:
        experimental
    """
    sendingOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnConfigurationSet.SendingOptionsProperty"]
    """``AWS::PinpointEmail::ConfigurationSet.SendingOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-sendingoptions
    Stability:
        experimental
    """
    tags: typing.List["CfnConfigurationSet.TagsProperty"]
    """``AWS::PinpointEmail::ConfigurationSet.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-tags
    Stability:
        experimental
    """
    trackingOptions: typing.Union[aws_cdk.cdk.IResolvable, "CfnConfigurationSet.TrackingOptionsProperty"]
    """``AWS::PinpointEmail::ConfigurationSet.TrackingOptions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-trackingoptions
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnConfigurationSetProps", jsii_struct_bases=[_CfnConfigurationSetProps])
class CfnConfigurationSetProps(_CfnConfigurationSetProps):
    """Properties for defining a ``AWS::PinpointEmail::ConfigurationSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html
    Stability:
        experimental
    """
    name: str
    """``AWS::PinpointEmail::ConfigurationSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-configurationset.html#cfn-pinpointemail-configurationset-name
    Stability:
        experimental
    """

class CfnDedicatedIpPool(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpointemail.CfnDedicatedIpPool"):
    """A CloudFormation ``AWS::PinpointEmail::DedicatedIpPool``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-dedicatedippool.html
    Stability:
        experimental
    cloudformationResource:
        AWS::PinpointEmail::DedicatedIpPool
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, pool_name: typing.Optional[str]=None, tags: typing.Optional[typing.List["TagsProperty"]]=None) -> None:
        """Create a new ``AWS::PinpointEmail::DedicatedIpPool``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            poolName: ``AWS::PinpointEmail::DedicatedIpPool.PoolName``.
            tags: ``AWS::PinpointEmail::DedicatedIpPool.Tags``.

        Stability:
            experimental
        """
        props: CfnDedicatedIpPoolProps = {}

        if pool_name is not None:
            props["poolName"] = pool_name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnDedicatedIpPool, self, [scope, id, props])

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
    @jsii.member(jsii_name="poolName")
    def pool_name(self) -> typing.Optional[str]:
        """``AWS::PinpointEmail::DedicatedIpPool.PoolName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-dedicatedippool.html#cfn-pinpointemail-dedicatedippool-poolname
        Stability:
            experimental
        """
        return jsii.get(self, "poolName")

    @pool_name.setter
    def pool_name(self, value: typing.Optional[str]):
        return jsii.set(self, "poolName", value)

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List["TagsProperty"]]:
        """``AWS::PinpointEmail::DedicatedIpPool.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-dedicatedippool.html#cfn-pinpointemail-dedicatedippool-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @tags.setter
    def tags(self, value: typing.Optional[typing.List["TagsProperty"]]):
        return jsii.set(self, "tags", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnDedicatedIpPool.TagsProperty", jsii_struct_bases=[])
    class TagsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-dedicatedippool-tags.html
        Stability:
            experimental
        """
        key: str
        """``CfnDedicatedIpPool.TagsProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-dedicatedippool-tags.html#cfn-pinpointemail-dedicatedippool-tags-key
        Stability:
            experimental
        """

        value: str
        """``CfnDedicatedIpPool.TagsProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-dedicatedippool-tags.html#cfn-pinpointemail-dedicatedippool-tags-value
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnDedicatedIpPoolProps", jsii_struct_bases=[])
class CfnDedicatedIpPoolProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::PinpointEmail::DedicatedIpPool``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-dedicatedippool.html
    Stability:
        experimental
    """
    poolName: str
    """``AWS::PinpointEmail::DedicatedIpPool.PoolName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-dedicatedippool.html#cfn-pinpointemail-dedicatedippool-poolname
    Stability:
        experimental
    """

    tags: typing.List["CfnDedicatedIpPool.TagsProperty"]
    """``AWS::PinpointEmail::DedicatedIpPool.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-dedicatedippool.html#cfn-pinpointemail-dedicatedippool-tags
    Stability:
        experimental
    """

class CfnIdentity(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-pinpointemail.CfnIdentity"):
    """A CloudFormation ``AWS::PinpointEmail::Identity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html
    Stability:
        experimental
    cloudformationResource:
        AWS::PinpointEmail::Identity
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, dkim_signing_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, feedback_forwarding_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, mail_from_attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["MailFromAttributesProperty"]]]=None, tags: typing.Optional[typing.List["TagsProperty"]]=None) -> None:
        """Create a new ``AWS::PinpointEmail::Identity``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::PinpointEmail::Identity.Name``.
            dkimSigningEnabled: ``AWS::PinpointEmail::Identity.DkimSigningEnabled``.
            feedbackForwardingEnabled: ``AWS::PinpointEmail::Identity.FeedbackForwardingEnabled``.
            mailFromAttributes: ``AWS::PinpointEmail::Identity.MailFromAttributes``.
            tags: ``AWS::PinpointEmail::Identity.Tags``.

        Stability:
            experimental
        """
        props: CfnIdentityProps = {"name": name}

        if dkim_signing_enabled is not None:
            props["dkimSigningEnabled"] = dkim_signing_enabled

        if feedback_forwarding_enabled is not None:
            props["feedbackForwardingEnabled"] = feedback_forwarding_enabled

        if mail_from_attributes is not None:
            props["mailFromAttributes"] = mail_from_attributes

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnIdentity, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrIdentityDnsRecordName1")
    def attr_identity_dns_record_name1(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            IdentityDNSRecordName1
        """
        return jsii.get(self, "attrIdentityDnsRecordName1")

    @property
    @jsii.member(jsii_name="attrIdentityDnsRecordName2")
    def attr_identity_dns_record_name2(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            IdentityDNSRecordName2
        """
        return jsii.get(self, "attrIdentityDnsRecordName2")

    @property
    @jsii.member(jsii_name="attrIdentityDnsRecordName3")
    def attr_identity_dns_record_name3(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            IdentityDNSRecordName3
        """
        return jsii.get(self, "attrIdentityDnsRecordName3")

    @property
    @jsii.member(jsii_name="attrIdentityDnsRecordValue1")
    def attr_identity_dns_record_value1(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            IdentityDNSRecordValue1
        """
        return jsii.get(self, "attrIdentityDnsRecordValue1")

    @property
    @jsii.member(jsii_name="attrIdentityDnsRecordValue2")
    def attr_identity_dns_record_value2(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            IdentityDNSRecordValue2
        """
        return jsii.get(self, "attrIdentityDnsRecordValue2")

    @property
    @jsii.member(jsii_name="attrIdentityDnsRecordValue3")
    def attr_identity_dns_record_value3(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            IdentityDNSRecordValue3
        """
        return jsii.get(self, "attrIdentityDnsRecordValue3")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::PinpointEmail::Identity.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="dkimSigningEnabled")
    def dkim_signing_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::PinpointEmail::Identity.DkimSigningEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-dkimsigningenabled
        Stability:
            experimental
        """
        return jsii.get(self, "dkimSigningEnabled")

    @dkim_signing_enabled.setter
    def dkim_signing_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "dkimSigningEnabled", value)

    @property
    @jsii.member(jsii_name="feedbackForwardingEnabled")
    def feedback_forwarding_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::PinpointEmail::Identity.FeedbackForwardingEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-feedbackforwardingenabled
        Stability:
            experimental
        """
        return jsii.get(self, "feedbackForwardingEnabled")

    @feedback_forwarding_enabled.setter
    def feedback_forwarding_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "feedbackForwardingEnabled", value)

    @property
    @jsii.member(jsii_name="mailFromAttributes")
    def mail_from_attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["MailFromAttributesProperty"]]]:
        """``AWS::PinpointEmail::Identity.MailFromAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-mailfromattributes
        Stability:
            experimental
        """
        return jsii.get(self, "mailFromAttributes")

    @mail_from_attributes.setter
    def mail_from_attributes(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["MailFromAttributesProperty"]]]):
        return jsii.set(self, "mailFromAttributes", value)

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List["TagsProperty"]]:
        """``AWS::PinpointEmail::Identity.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @tags.setter
    def tags(self, value: typing.Optional[typing.List["TagsProperty"]]):
        return jsii.set(self, "tags", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnIdentity.MailFromAttributesProperty", jsii_struct_bases=[])
    class MailFromAttributesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-identity-mailfromattributes.html
        Stability:
            experimental
        """
        behaviorOnMxFailure: str
        """``CfnIdentity.MailFromAttributesProperty.BehaviorOnMxFailure``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-identity-mailfromattributes.html#cfn-pinpointemail-identity-mailfromattributes-behavioronmxfailure
        Stability:
            experimental
        """

        mailFromDomain: str
        """``CfnIdentity.MailFromAttributesProperty.MailFromDomain``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-identity-mailfromattributes.html#cfn-pinpointemail-identity-mailfromattributes-mailfromdomain
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnIdentity.TagsProperty", jsii_struct_bases=[])
    class TagsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-identity-tags.html
        Stability:
            experimental
        """
        key: str
        """``CfnIdentity.TagsProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-identity-tags.html#cfn-pinpointemail-identity-tags-key
        Stability:
            experimental
        """

        value: str
        """``CfnIdentity.TagsProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-pinpointemail-identity-tags.html#cfn-pinpointemail-identity-tags-value
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnIdentityProps(jsii.compat.TypedDict, total=False):
    dkimSigningEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::PinpointEmail::Identity.DkimSigningEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-dkimsigningenabled
    Stability:
        experimental
    """
    feedbackForwardingEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::PinpointEmail::Identity.FeedbackForwardingEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-feedbackforwardingenabled
    Stability:
        experimental
    """
    mailFromAttributes: typing.Union[aws_cdk.cdk.IResolvable, "CfnIdentity.MailFromAttributesProperty"]
    """``AWS::PinpointEmail::Identity.MailFromAttributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-mailfromattributes
    Stability:
        experimental
    """
    tags: typing.List["CfnIdentity.TagsProperty"]
    """``AWS::PinpointEmail::Identity.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-pinpointemail.CfnIdentityProps", jsii_struct_bases=[_CfnIdentityProps])
class CfnIdentityProps(_CfnIdentityProps):
    """Properties for defining a ``AWS::PinpointEmail::Identity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html
    Stability:
        experimental
    """
    name: str
    """``AWS::PinpointEmail::Identity.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-pinpointemail-identity.html#cfn-pinpointemail-identity-name
    Stability:
        experimental
    """

__all__ = ["CfnConfigurationSet", "CfnConfigurationSetEventDestination", "CfnConfigurationSetEventDestinationProps", "CfnConfigurationSetProps", "CfnDedicatedIpPool", "CfnDedicatedIpPoolProps", "CfnIdentity", "CfnIdentityProps", "__jsii_assembly__"]

publication.publish()
