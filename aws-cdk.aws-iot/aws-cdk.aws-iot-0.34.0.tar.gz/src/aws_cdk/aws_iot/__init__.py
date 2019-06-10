import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-iot", "0.34.0", __name__, "aws-iot@0.34.0.jsii.tgz")
class CfnCertificate(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnCertificate"):
    """A CloudFormation ``AWS::IoT::Certificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoT::Certificate
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, certificate_signing_request: str, status: str) -> None:
        """Create a new ``AWS::IoT::Certificate``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            certificateSigningRequest: ``AWS::IoT::Certificate.CertificateSigningRequest``.
            status: ``AWS::IoT::Certificate.Status``.

        Stability:
            experimental
        """
        props: CfnCertificateProps = {"certificateSigningRequest": certificate_signing_request, "status": status}

        jsii.create(CfnCertificate, self, [scope, id, props])

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
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "certificateArn")

    @property
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "certificateId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnCertificateProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnCertificateProps", jsii_struct_bases=[])
class CfnCertificateProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::IoT::Certificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html
    Stability:
        experimental
    """
    certificateSigningRequest: str
    """``AWS::IoT::Certificate.CertificateSigningRequest``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-certificatesigningrequest
    Stability:
        experimental
    """

    status: str
    """``AWS::IoT::Certificate.Status``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-status
    Stability:
        experimental
    """

class CfnPolicy(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnPolicy"):
    """A CloudFormation ``AWS::IoT::Policy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoT::Policy
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, policy_document: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token], policy_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT::Policy``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            policyDocument: ``AWS::IoT::Policy.PolicyDocument``.
            policyName: ``AWS::IoT::Policy.PolicyName``.

        Stability:
            experimental
        """
        props: CfnPolicyProps = {"policyDocument": policy_document}

        if policy_name is not None:
            props["policyName"] = policy_name

        jsii.create(CfnPolicy, self, [scope, id, props])

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
    @jsii.member(jsii_name="policyArn")
    def policy_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "policyArn")

    @property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "policyName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnPolicyProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


class CfnPolicyPrincipalAttachment(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnPolicyPrincipalAttachment"):
    """A CloudFormation ``AWS::IoT::PolicyPrincipalAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoT::PolicyPrincipalAttachment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, policy_name: str, principal: str) -> None:
        """Create a new ``AWS::IoT::PolicyPrincipalAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            policyName: ``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.
            principal: ``AWS::IoT::PolicyPrincipalAttachment.Principal``.

        Stability:
            experimental
        """
        props: CfnPolicyPrincipalAttachmentProps = {"policyName": policy_name, "principal": principal}

        jsii.create(CfnPolicyPrincipalAttachment, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnPolicyPrincipalAttachmentProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnPolicyPrincipalAttachmentProps", jsii_struct_bases=[])
class CfnPolicyPrincipalAttachmentProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::IoT::PolicyPrincipalAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html
    Stability:
        experimental
    """
    policyName: str
    """``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-policyname
    Stability:
        experimental
    """

    principal: str
    """``AWS::IoT::PolicyPrincipalAttachment.Principal``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-principal
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPolicyProps(jsii.compat.TypedDict, total=False):
    policyName: str
    """``AWS::IoT::Policy.PolicyName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policyname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnPolicyProps", jsii_struct_bases=[_CfnPolicyProps])
class CfnPolicyProps(_CfnPolicyProps):
    """Properties for defining a ``AWS::IoT::Policy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html
    Stability:
        experimental
    """
    policyDocument: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::IoT::Policy.PolicyDocument``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policydocument
    Stability:
        experimental
    """

class CfnThing(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnThing"):
    """A CloudFormation ``AWS::IoT::Thing``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoT::Thing
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, attribute_payload: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["AttributePayloadProperty"]]]=None, thing_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT::Thing``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            attributePayload: ``AWS::IoT::Thing.AttributePayload``.
            thingName: ``AWS::IoT::Thing.ThingName``.

        Stability:
            experimental
        """
        props: CfnThingProps = {}

        if attribute_payload is not None:
            props["attributePayload"] = attribute_payload

        if thing_name is not None:
            props["thingName"] = thing_name

        jsii.create(CfnThing, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnThingProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="thingName")
    def thing_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "thingName")

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnThing.AttributePayloadProperty", jsii_struct_bases=[])
    class AttributePayloadProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-thing-attributepayload.html
        Stability:
            experimental
        """
        attributes: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnThing.AttributePayloadProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-thing-attributepayload.html#cfn-iot-thing-attributepayload-attributes
        Stability:
            experimental
        """


class CfnThingPrincipalAttachment(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnThingPrincipalAttachment"):
    """A CloudFormation ``AWS::IoT::ThingPrincipalAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoT::ThingPrincipalAttachment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, principal: str, thing_name: str) -> None:
        """Create a new ``AWS::IoT::ThingPrincipalAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            principal: ``AWS::IoT::ThingPrincipalAttachment.Principal``.
            thingName: ``AWS::IoT::ThingPrincipalAttachment.ThingName``.

        Stability:
            experimental
        """
        props: CfnThingPrincipalAttachmentProps = {"principal": principal, "thingName": thing_name}

        jsii.create(CfnThingPrincipalAttachment, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnThingPrincipalAttachmentProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnThingPrincipalAttachmentProps", jsii_struct_bases=[])
class CfnThingPrincipalAttachmentProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::IoT::ThingPrincipalAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html
    Stability:
        experimental
    """
    principal: str
    """``AWS::IoT::ThingPrincipalAttachment.Principal``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-principal
    Stability:
        experimental
    """

    thingName: str
    """``AWS::IoT::ThingPrincipalAttachment.ThingName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-thingname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnThingProps", jsii_struct_bases=[])
class CfnThingProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::IoT::Thing``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html
    Stability:
        experimental
    """
    attributePayload: typing.Union[aws_cdk.cdk.Token, "CfnThing.AttributePayloadProperty"]
    """``AWS::IoT::Thing.AttributePayload``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-attributepayload
    Stability:
        experimental
    """

    thingName: str
    """``AWS::IoT::Thing.ThingName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-thingname
    Stability:
        experimental
    """

class CfnTopicRule(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnTopicRule"):
    """A CloudFormation ``AWS::IoT::TopicRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoT::TopicRule
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, topic_rule_payload: typing.Union[aws_cdk.cdk.Token, "TopicRulePayloadProperty"], rule_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT::TopicRule``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            topicRulePayload: ``AWS::IoT::TopicRule.TopicRulePayload``.
            ruleName: ``AWS::IoT::TopicRule.RuleName``.

        Stability:
            experimental
        """
        props: CfnTopicRuleProps = {"topicRulePayload": topic_rule_payload}

        if rule_name is not None:
            props["ruleName"] = rule_name

        jsii.create(CfnTopicRule, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnTopicRuleProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="topicRuleArn")
    def topic_rule_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "topicRuleArn")

    @property
    @jsii.member(jsii_name="topicRuleName")
    def topic_rule_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "topicRuleName")

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.ActionProperty", jsii_struct_bases=[])
    class ActionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html
        Stability:
            experimental
        """
        cloudwatchAlarm: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.CloudwatchAlarmActionProperty"]
        """``CfnTopicRule.ActionProperty.CloudwatchAlarm``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-cloudwatchalarm
        Stability:
            experimental
        """

        cloudwatchMetric: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.CloudwatchMetricActionProperty"]
        """``CfnTopicRule.ActionProperty.CloudwatchMetric``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-cloudwatchmetric
        Stability:
            experimental
        """

        dynamoDb: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.DynamoDBActionProperty"]
        """``CfnTopicRule.ActionProperty.DynamoDB``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-dynamodb
        Stability:
            experimental
        """

        dynamoDBv2: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.DynamoDBv2ActionProperty"]
        """``CfnTopicRule.ActionProperty.DynamoDBv2``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-dynamodbv2
        Stability:
            experimental
        """

        elasticsearch: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.ElasticsearchActionProperty"]
        """``CfnTopicRule.ActionProperty.Elasticsearch``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-elasticsearch
        Stability:
            experimental
        """

        firehose: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.FirehoseActionProperty"]
        """``CfnTopicRule.ActionProperty.Firehose``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-firehose
        Stability:
            experimental
        """

        iotAnalytics: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.IotAnalyticsActionProperty"]
        """``CfnTopicRule.ActionProperty.IotAnalytics``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-iotanalytics
        Stability:
            experimental
        """

        kinesis: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.KinesisActionProperty"]
        """``CfnTopicRule.ActionProperty.Kinesis``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-kinesis
        Stability:
            experimental
        """

        lambda_: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.LambdaActionProperty"]
        """``CfnTopicRule.ActionProperty.Lambda``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-lambda
        Stability:
            experimental
        """

        republish: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.RepublishActionProperty"]
        """``CfnTopicRule.ActionProperty.Republish``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-republish
        Stability:
            experimental
        """

        s3: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.S3ActionProperty"]
        """``CfnTopicRule.ActionProperty.S3``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-s3
        Stability:
            experimental
        """

        sns: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.SnsActionProperty"]
        """``CfnTopicRule.ActionProperty.Sns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-sns
        Stability:
            experimental
        """

        sqs: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.SqsActionProperty"]
        """``CfnTopicRule.ActionProperty.Sqs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-sqs
        Stability:
            experimental
        """

        stepFunctions: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.StepFunctionsActionProperty"]
        """``CfnTopicRule.ActionProperty.StepFunctions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-stepfunctions
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.CloudwatchAlarmActionProperty", jsii_struct_bases=[])
    class CloudwatchAlarmActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html
        Stability:
            experimental
        """
        alarmName: str
        """``CfnTopicRule.CloudwatchAlarmActionProperty.AlarmName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-alarmname
        Stability:
            experimental
        """

        roleArn: str
        """``CfnTopicRule.CloudwatchAlarmActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-rolearn
        Stability:
            experimental
        """

        stateReason: str
        """``CfnTopicRule.CloudwatchAlarmActionProperty.StateReason``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-statereason
        Stability:
            experimental
        """

        stateValue: str
        """``CfnTopicRule.CloudwatchAlarmActionProperty.StateValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-statevalue
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CloudwatchMetricActionProperty(jsii.compat.TypedDict, total=False):
        metricTimestamp: str
        """``CfnTopicRule.CloudwatchMetricActionProperty.MetricTimestamp``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metrictimestamp
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.CloudwatchMetricActionProperty", jsii_struct_bases=[_CloudwatchMetricActionProperty])
    class CloudwatchMetricActionProperty(_CloudwatchMetricActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html
        Stability:
            experimental
        """
        metricName: str
        """``CfnTopicRule.CloudwatchMetricActionProperty.MetricName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricname
        Stability:
            experimental
        """

        metricNamespace: str
        """``CfnTopicRule.CloudwatchMetricActionProperty.MetricNamespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricnamespace
        Stability:
            experimental
        """

        metricUnit: str
        """``CfnTopicRule.CloudwatchMetricActionProperty.MetricUnit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricunit
        Stability:
            experimental
        """

        metricValue: str
        """``CfnTopicRule.CloudwatchMetricActionProperty.MetricValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricvalue
        Stability:
            experimental
        """

        roleArn: str
        """``CfnTopicRule.CloudwatchMetricActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-rolearn
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DynamoDBActionProperty(jsii.compat.TypedDict, total=False):
        hashKeyType: str
        """``CfnTopicRule.DynamoDBActionProperty.HashKeyType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-hashkeytype
        Stability:
            experimental
        """
        payloadField: str
        """``CfnTopicRule.DynamoDBActionProperty.PayloadField``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-payloadfield
        Stability:
            experimental
        """
        rangeKeyField: str
        """``CfnTopicRule.DynamoDBActionProperty.RangeKeyField``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rangekeyfield
        Stability:
            experimental
        """
        rangeKeyType: str
        """``CfnTopicRule.DynamoDBActionProperty.RangeKeyType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rangekeytype
        Stability:
            experimental
        """
        rangeKeyValue: str
        """``CfnTopicRule.DynamoDBActionProperty.RangeKeyValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rangekeyvalue
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.DynamoDBActionProperty", jsii_struct_bases=[_DynamoDBActionProperty])
    class DynamoDBActionProperty(_DynamoDBActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html
        Stability:
            experimental
        """
        hashKeyField: str
        """``CfnTopicRule.DynamoDBActionProperty.HashKeyField``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-hashkeyfield
        Stability:
            experimental
        """

        hashKeyValue: str
        """``CfnTopicRule.DynamoDBActionProperty.HashKeyValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-hashkeyvalue
        Stability:
            experimental
        """

        roleArn: str
        """``CfnTopicRule.DynamoDBActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rolearn
        Stability:
            experimental
        """

        tableName: str
        """``CfnTopicRule.DynamoDBActionProperty.TableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-tablename
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.DynamoDBv2ActionProperty", jsii_struct_bases=[])
    class DynamoDBv2ActionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbv2action.html
        Stability:
            experimental
        """
        putItem: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.PutItemInputProperty"]
        """``CfnTopicRule.DynamoDBv2ActionProperty.PutItem``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbv2action.html#cfn-iot-topicrule-dynamodbv2action-putitem
        Stability:
            experimental
        """

        roleArn: str
        """``CfnTopicRule.DynamoDBv2ActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbv2action.html#cfn-iot-topicrule-dynamodbv2action-rolearn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.ElasticsearchActionProperty", jsii_struct_bases=[])
    class ElasticsearchActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html
        Stability:
            experimental
        """
        endpoint: str
        """``CfnTopicRule.ElasticsearchActionProperty.Endpoint``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-endpoint
        Stability:
            experimental
        """

        id: str
        """``CfnTopicRule.ElasticsearchActionProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-id
        Stability:
            experimental
        """

        index: str
        """``CfnTopicRule.ElasticsearchActionProperty.Index``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-index
        Stability:
            experimental
        """

        roleArn: str
        """``CfnTopicRule.ElasticsearchActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-rolearn
        Stability:
            experimental
        """

        type: str
        """``CfnTopicRule.ElasticsearchActionProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-type
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FirehoseActionProperty(jsii.compat.TypedDict, total=False):
        separator: str
        """``CfnTopicRule.FirehoseActionProperty.Separator``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-separator
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.FirehoseActionProperty", jsii_struct_bases=[_FirehoseActionProperty])
    class FirehoseActionProperty(_FirehoseActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html
        Stability:
            experimental
        """
        deliveryStreamName: str
        """``CfnTopicRule.FirehoseActionProperty.DeliveryStreamName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-deliverystreamname
        Stability:
            experimental
        """

        roleArn: str
        """``CfnTopicRule.FirehoseActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-rolearn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.IotAnalyticsActionProperty", jsii_struct_bases=[])
    class IotAnalyticsActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html
        Stability:
            experimental
        """
        channelName: str
        """``CfnTopicRule.IotAnalyticsActionProperty.ChannelName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html#cfn-iot-topicrule-iotanalyticsaction-channelname
        Stability:
            experimental
        """

        roleArn: str
        """``CfnTopicRule.IotAnalyticsActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html#cfn-iot-topicrule-iotanalyticsaction-rolearn
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _KinesisActionProperty(jsii.compat.TypedDict, total=False):
        partitionKey: str
        """``CfnTopicRule.KinesisActionProperty.PartitionKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html#cfn-iot-topicrule-kinesisaction-partitionkey
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.KinesisActionProperty", jsii_struct_bases=[_KinesisActionProperty])
    class KinesisActionProperty(_KinesisActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html
        Stability:
            experimental
        """
        roleArn: str
        """``CfnTopicRule.KinesisActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html#cfn-iot-topicrule-kinesisaction-rolearn
        Stability:
            experimental
        """

        streamName: str
        """``CfnTopicRule.KinesisActionProperty.StreamName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html#cfn-iot-topicrule-kinesisaction-streamname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.LambdaActionProperty", jsii_struct_bases=[])
    class LambdaActionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-lambdaaction.html
        Stability:
            experimental
        """
        functionArn: str
        """``CfnTopicRule.LambdaActionProperty.FunctionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-lambdaaction.html#cfn-iot-topicrule-lambdaaction-functionarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.PutItemInputProperty", jsii_struct_bases=[])
    class PutItemInputProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putiteminput.html
        Stability:
            experimental
        """
        tableName: str
        """``CfnTopicRule.PutItemInputProperty.TableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putiteminput.html#cfn-iot-topicrule-putiteminput-tablename
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.RepublishActionProperty", jsii_struct_bases=[])
    class RepublishActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html
        Stability:
            experimental
        """
        roleArn: str
        """``CfnTopicRule.RepublishActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html#cfn-iot-topicrule-republishaction-rolearn
        Stability:
            experimental
        """

        topic: str
        """``CfnTopicRule.RepublishActionProperty.Topic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html#cfn-iot-topicrule-republishaction-topic
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.S3ActionProperty", jsii_struct_bases=[])
    class S3ActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html
        Stability:
            experimental
        """
        bucketName: str
        """``CfnTopicRule.S3ActionProperty.BucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-bucketname
        Stability:
            experimental
        """

        key: str
        """``CfnTopicRule.S3ActionProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-key
        Stability:
            experimental
        """

        roleArn: str
        """``CfnTopicRule.S3ActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-rolearn
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SnsActionProperty(jsii.compat.TypedDict, total=False):
        messageFormat: str
        """``CfnTopicRule.SnsActionProperty.MessageFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html#cfn-iot-topicrule-snsaction-messageformat
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.SnsActionProperty", jsii_struct_bases=[_SnsActionProperty])
    class SnsActionProperty(_SnsActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html
        Stability:
            experimental
        """
        roleArn: str
        """``CfnTopicRule.SnsActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html#cfn-iot-topicrule-snsaction-rolearn
        Stability:
            experimental
        """

        targetArn: str
        """``CfnTopicRule.SnsActionProperty.TargetArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html#cfn-iot-topicrule-snsaction-targetarn
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SqsActionProperty(jsii.compat.TypedDict, total=False):
        useBase64: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTopicRule.SqsActionProperty.UseBase64``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html#cfn-iot-topicrule-sqsaction-usebase64
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.SqsActionProperty", jsii_struct_bases=[_SqsActionProperty])
    class SqsActionProperty(_SqsActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html
        Stability:
            experimental
        """
        queueUrl: str
        """``CfnTopicRule.SqsActionProperty.QueueUrl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html#cfn-iot-topicrule-sqsaction-queueurl
        Stability:
            experimental
        """

        roleArn: str
        """``CfnTopicRule.SqsActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html#cfn-iot-topicrule-sqsaction-rolearn
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _StepFunctionsActionProperty(jsii.compat.TypedDict, total=False):
        executionNamePrefix: str
        """``CfnTopicRule.StepFunctionsActionProperty.ExecutionNamePrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html#cfn-iot-topicrule-stepfunctionsaction-executionnameprefix
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.StepFunctionsActionProperty", jsii_struct_bases=[_StepFunctionsActionProperty])
    class StepFunctionsActionProperty(_StepFunctionsActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html
        Stability:
            experimental
        """
        roleArn: str
        """``CfnTopicRule.StepFunctionsActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html#cfn-iot-topicrule-stepfunctionsaction-rolearn
        Stability:
            experimental
        """

        stateMachineName: str
        """``CfnTopicRule.StepFunctionsActionProperty.StateMachineName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html#cfn-iot-topicrule-stepfunctionsaction-statemachinename
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _TopicRulePayloadProperty(jsii.compat.TypedDict, total=False):
        awsIotSqlVersion: str
        """``CfnTopicRule.TopicRulePayloadProperty.AwsIotSqlVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-awsiotsqlversion
        Stability:
            experimental
        """
        description: str
        """``CfnTopicRule.TopicRulePayloadProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-description
        Stability:
            experimental
        """
        errorAction: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.ActionProperty"]
        """``CfnTopicRule.TopicRulePayloadProperty.ErrorAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-erroraction
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.TopicRulePayloadProperty", jsii_struct_bases=[_TopicRulePayloadProperty])
    class TopicRulePayloadProperty(_TopicRulePayloadProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html
        Stability:
            experimental
        """
        actions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.ActionProperty"]]]
        """``CfnTopicRule.TopicRulePayloadProperty.Actions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-actions
        Stability:
            experimental
        """

        ruleDisabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTopicRule.TopicRulePayloadProperty.RuleDisabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-ruledisabled
        Stability:
            experimental
        """

        sql: str
        """``CfnTopicRule.TopicRulePayloadProperty.Sql``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-sql
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnTopicRuleProps(jsii.compat.TypedDict, total=False):
    ruleName: str
    """``AWS::IoT::TopicRule.RuleName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-rulename
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRuleProps", jsii_struct_bases=[_CfnTopicRuleProps])
class CfnTopicRuleProps(_CfnTopicRuleProps):
    """Properties for defining a ``AWS::IoT::TopicRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html
    Stability:
        experimental
    """
    topicRulePayload: typing.Union[aws_cdk.cdk.Token, "CfnTopicRule.TopicRulePayloadProperty"]
    """``AWS::IoT::TopicRule.TopicRulePayload``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-topicrulepayload
    Stability:
        experimental
    """

__all__ = ["CfnCertificate", "CfnCertificateProps", "CfnPolicy", "CfnPolicyPrincipalAttachment", "CfnPolicyPrincipalAttachmentProps", "CfnPolicyProps", "CfnThing", "CfnThingPrincipalAttachment", "CfnThingPrincipalAttachmentProps", "CfnThingProps", "CfnTopicRule", "CfnTopicRuleProps", "__jsii_assembly__"]

publication.publish()
