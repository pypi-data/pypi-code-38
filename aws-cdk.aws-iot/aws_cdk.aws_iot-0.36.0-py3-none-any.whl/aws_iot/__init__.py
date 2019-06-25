import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-iot", "0.36.0", __name__, "aws-iot@0.36.0.jsii.tgz")
class CfnCertificate(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnCertificate"):
    """A CloudFormation ``AWS::IoT::Certificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoT::Certificate
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, certificate_signing_request: str, status: str) -> None:
        """Create a new ``AWS::IoT::Certificate``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            certificate_signing_request: ``AWS::IoT::Certificate.CertificateSigningRequest``.
            status: ``AWS::IoT::Certificate.Status``.

        Stability:
            experimental
        """
        props: CfnCertificateProps = {"certificateSigningRequest": certificate_signing_request, "status": status}

        jsii.create(CfnCertificate, self, [scope, id, props])

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
    @jsii.member(jsii_name="certificateSigningRequest")
    def certificate_signing_request(self) -> str:
        """``AWS::IoT::Certificate.CertificateSigningRequest``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-certificatesigningrequest
        Stability:
            stable
        """
        return jsii.get(self, "certificateSigningRequest")

    @certificate_signing_request.setter
    def certificate_signing_request(self, value: str):
        return jsii.set(self, "certificateSigningRequest", value)

    @property
    @jsii.member(jsii_name="status")
    def status(self) -> str:
        """``AWS::IoT::Certificate.Status``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-status
        Stability:
            stable
        """
        return jsii.get(self, "status")

    @status.setter
    def status(self, value: str):
        return jsii.set(self, "status", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnCertificateProps", jsii_struct_bases=[])
class CfnCertificateProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::IoT::Certificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html
    Stability:
        stable
    """
    certificateSigningRequest: str
    """``AWS::IoT::Certificate.CertificateSigningRequest``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-certificatesigningrequest
    Stability:
        stable
    """

    status: str
    """``AWS::IoT::Certificate.Status``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-status
    Stability:
        stable
    """

class CfnPolicy(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnPolicy"):
    """A CloudFormation ``AWS::IoT::Policy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoT::Policy
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, policy_document: typing.Any, policy_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT::Policy``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            policy_document: ``AWS::IoT::Policy.PolicyDocument``.
            policy_name: ``AWS::IoT::Policy.PolicyName``.

        Stability:
            experimental
        """
        props: CfnPolicyProps = {"policyDocument": policy_document}

        if policy_name is not None:
            props["policyName"] = policy_name

        jsii.create(CfnPolicy, self, [scope, id, props])

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
    @jsii.member(jsii_name="policyDocument")
    def policy_document(self) -> typing.Any:
        """``AWS::IoT::Policy.PolicyDocument``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policydocument
        Stability:
            stable
        """
        return jsii.get(self, "policyDocument")

    @policy_document.setter
    def policy_document(self, value: typing.Any):
        return jsii.set(self, "policyDocument", value)

    @property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> typing.Optional[str]:
        """``AWS::IoT::Policy.PolicyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policyname
        Stability:
            stable
        """
        return jsii.get(self, "policyName")

    @policy_name.setter
    def policy_name(self, value: typing.Optional[str]):
        return jsii.set(self, "policyName", value)


class CfnPolicyPrincipalAttachment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnPolicyPrincipalAttachment"):
    """A CloudFormation ``AWS::IoT::PolicyPrincipalAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoT::PolicyPrincipalAttachment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, policy_name: str, principal: str) -> None:
        """Create a new ``AWS::IoT::PolicyPrincipalAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            policy_name: ``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.
            principal: ``AWS::IoT::PolicyPrincipalAttachment.Principal``.

        Stability:
            experimental
        """
        props: CfnPolicyPrincipalAttachmentProps = {"policyName": policy_name, "principal": principal}

        jsii.create(CfnPolicyPrincipalAttachment, self, [scope, id, props])

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
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> str:
        """``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-policyname
        Stability:
            stable
        """
        return jsii.get(self, "policyName")

    @policy_name.setter
    def policy_name(self, value: str):
        return jsii.set(self, "policyName", value)

    @property
    @jsii.member(jsii_name="principal")
    def principal(self) -> str:
        """``AWS::IoT::PolicyPrincipalAttachment.Principal``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-principal
        Stability:
            stable
        """
        return jsii.get(self, "principal")

    @principal.setter
    def principal(self, value: str):
        return jsii.set(self, "principal", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnPolicyPrincipalAttachmentProps", jsii_struct_bases=[])
class CfnPolicyPrincipalAttachmentProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::IoT::PolicyPrincipalAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html
    Stability:
        stable
    """
    policyName: str
    """``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-policyname
    Stability:
        stable
    """

    principal: str
    """``AWS::IoT::PolicyPrincipalAttachment.Principal``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-principal
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPolicyProps(jsii.compat.TypedDict, total=False):
    policyName: str
    """``AWS::IoT::Policy.PolicyName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policyname
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnPolicyProps", jsii_struct_bases=[_CfnPolicyProps])
class CfnPolicyProps(_CfnPolicyProps):
    """Properties for defining a ``AWS::IoT::Policy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html
    Stability:
        stable
    """
    policyDocument: typing.Any
    """``AWS::IoT::Policy.PolicyDocument``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policydocument
    Stability:
        stable
    """

class CfnThing(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnThing"):
    """A CloudFormation ``AWS::IoT::Thing``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoT::Thing
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, attribute_payload: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AttributePayloadProperty"]]]=None, thing_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT::Thing``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            attribute_payload: ``AWS::IoT::Thing.AttributePayload``.
            thing_name: ``AWS::IoT::Thing.ThingName``.

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
    @jsii.member(jsii_name="attributePayload")
    def attribute_payload(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AttributePayloadProperty"]]]:
        """``AWS::IoT::Thing.AttributePayload``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-attributepayload
        Stability:
            stable
        """
        return jsii.get(self, "attributePayload")

    @attribute_payload.setter
    def attribute_payload(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["AttributePayloadProperty"]]]):
        return jsii.set(self, "attributePayload", value)

    @property
    @jsii.member(jsii_name="thingName")
    def thing_name(self) -> typing.Optional[str]:
        """``AWS::IoT::Thing.ThingName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-thingname
        Stability:
            stable
        """
        return jsii.get(self, "thingName")

    @thing_name.setter
    def thing_name(self, value: typing.Optional[str]):
        return jsii.set(self, "thingName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnThing.AttributePayloadProperty", jsii_struct_bases=[])
    class AttributePayloadProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-thing-attributepayload.html
        Stability:
            stable
        """
        attributes: typing.Union[aws_cdk.core.IResolvable, typing.Mapping[str,str]]
        """``CfnThing.AttributePayloadProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-thing-attributepayload.html#cfn-iot-thing-attributepayload-attributes
        Stability:
            stable
        """


class CfnThingPrincipalAttachment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnThingPrincipalAttachment"):
    """A CloudFormation ``AWS::IoT::ThingPrincipalAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoT::ThingPrincipalAttachment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, principal: str, thing_name: str) -> None:
        """Create a new ``AWS::IoT::ThingPrincipalAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            principal: ``AWS::IoT::ThingPrincipalAttachment.Principal``.
            thing_name: ``AWS::IoT::ThingPrincipalAttachment.ThingName``.

        Stability:
            experimental
        """
        props: CfnThingPrincipalAttachmentProps = {"principal": principal, "thingName": thing_name}

        jsii.create(CfnThingPrincipalAttachment, self, [scope, id, props])

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
    @jsii.member(jsii_name="principal")
    def principal(self) -> str:
        """``AWS::IoT::ThingPrincipalAttachment.Principal``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-principal
        Stability:
            stable
        """
        return jsii.get(self, "principal")

    @principal.setter
    def principal(self, value: str):
        return jsii.set(self, "principal", value)

    @property
    @jsii.member(jsii_name="thingName")
    def thing_name(self) -> str:
        """``AWS::IoT::ThingPrincipalAttachment.ThingName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-thingname
        Stability:
            stable
        """
        return jsii.get(self, "thingName")

    @thing_name.setter
    def thing_name(self, value: str):
        return jsii.set(self, "thingName", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnThingPrincipalAttachmentProps", jsii_struct_bases=[])
class CfnThingPrincipalAttachmentProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::IoT::ThingPrincipalAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html
    Stability:
        stable
    """
    principal: str
    """``AWS::IoT::ThingPrincipalAttachment.Principal``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-principal
    Stability:
        stable
    """

    thingName: str
    """``AWS::IoT::ThingPrincipalAttachment.ThingName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-thingname
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnThingProps", jsii_struct_bases=[])
class CfnThingProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::IoT::Thing``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html
    Stability:
        stable
    """
    attributePayload: typing.Union[aws_cdk.core.IResolvable, "CfnThing.AttributePayloadProperty"]
    """``AWS::IoT::Thing.AttributePayload``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-attributepayload
    Stability:
        stable
    """

    thingName: str
    """``AWS::IoT::Thing.ThingName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-thingname
    Stability:
        stable
    """

class CfnTopicRule(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot.CfnTopicRule"):
    """A CloudFormation ``AWS::IoT::TopicRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoT::TopicRule
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, topic_rule_payload: typing.Union[aws_cdk.core.IResolvable, "TopicRulePayloadProperty"], rule_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT::TopicRule``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            topic_rule_payload: ``AWS::IoT::TopicRule.TopicRulePayload``.
            rule_name: ``AWS::IoT::TopicRule.RuleName``.

        Stability:
            experimental
        """
        props: CfnTopicRuleProps = {"topicRulePayload": topic_rule_payload}

        if rule_name is not None:
            props["ruleName"] = rule_name

        jsii.create(CfnTopicRule, self, [scope, id, props])

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
    @jsii.member(jsii_name="topicRulePayload")
    def topic_rule_payload(self) -> typing.Union[aws_cdk.core.IResolvable, "TopicRulePayloadProperty"]:
        """``AWS::IoT::TopicRule.TopicRulePayload``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-topicrulepayload
        Stability:
            stable
        """
        return jsii.get(self, "topicRulePayload")

    @topic_rule_payload.setter
    def topic_rule_payload(self, value: typing.Union[aws_cdk.core.IResolvable, "TopicRulePayloadProperty"]):
        return jsii.set(self, "topicRulePayload", value)

    @property
    @jsii.member(jsii_name="ruleName")
    def rule_name(self) -> typing.Optional[str]:
        """``AWS::IoT::TopicRule.RuleName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-rulename
        Stability:
            stable
        """
        return jsii.get(self, "ruleName")

    @rule_name.setter
    def rule_name(self, value: typing.Optional[str]):
        return jsii.set(self, "ruleName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.ActionProperty", jsii_struct_bases=[])
    class ActionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html
        Stability:
            stable
        """
        cloudwatchAlarm: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.CloudwatchAlarmActionProperty"]
        """``CfnTopicRule.ActionProperty.CloudwatchAlarm``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-cloudwatchalarm
        Stability:
            stable
        """

        cloudwatchMetric: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.CloudwatchMetricActionProperty"]
        """``CfnTopicRule.ActionProperty.CloudwatchMetric``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-cloudwatchmetric
        Stability:
            stable
        """

        dynamoDb: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.DynamoDBActionProperty"]
        """``CfnTopicRule.ActionProperty.DynamoDB``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-dynamodb
        Stability:
            stable
        """

        dynamoDBv2: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.DynamoDBv2ActionProperty"]
        """``CfnTopicRule.ActionProperty.DynamoDBv2``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-dynamodbv2
        Stability:
            stable
        """

        elasticsearch: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.ElasticsearchActionProperty"]
        """``CfnTopicRule.ActionProperty.Elasticsearch``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-elasticsearch
        Stability:
            stable
        """

        firehose: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.FirehoseActionProperty"]
        """``CfnTopicRule.ActionProperty.Firehose``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-firehose
        Stability:
            stable
        """

        iotAnalytics: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.IotAnalyticsActionProperty"]
        """``CfnTopicRule.ActionProperty.IotAnalytics``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-iotanalytics
        Stability:
            stable
        """

        kinesis: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.KinesisActionProperty"]
        """``CfnTopicRule.ActionProperty.Kinesis``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-kinesis
        Stability:
            stable
        """

        lambda_: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.LambdaActionProperty"]
        """``CfnTopicRule.ActionProperty.Lambda``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-lambda
        Stability:
            stable
        """

        republish: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.RepublishActionProperty"]
        """``CfnTopicRule.ActionProperty.Republish``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-republish
        Stability:
            stable
        """

        s3: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.S3ActionProperty"]
        """``CfnTopicRule.ActionProperty.S3``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-s3
        Stability:
            stable
        """

        sns: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.SnsActionProperty"]
        """``CfnTopicRule.ActionProperty.Sns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-sns
        Stability:
            stable
        """

        sqs: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.SqsActionProperty"]
        """``CfnTopicRule.ActionProperty.Sqs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-sqs
        Stability:
            stable
        """

        stepFunctions: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.StepFunctionsActionProperty"]
        """``CfnTopicRule.ActionProperty.StepFunctions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-stepfunctions
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.CloudwatchAlarmActionProperty", jsii_struct_bases=[])
    class CloudwatchAlarmActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html
        Stability:
            stable
        """
        alarmName: str
        """``CfnTopicRule.CloudwatchAlarmActionProperty.AlarmName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-alarmname
        Stability:
            stable
        """

        roleArn: str
        """``CfnTopicRule.CloudwatchAlarmActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-rolearn
        Stability:
            stable
        """

        stateReason: str
        """``CfnTopicRule.CloudwatchAlarmActionProperty.StateReason``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-statereason
        Stability:
            stable
        """

        stateValue: str
        """``CfnTopicRule.CloudwatchAlarmActionProperty.StateValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-statevalue
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CloudwatchMetricActionProperty(jsii.compat.TypedDict, total=False):
        metricTimestamp: str
        """``CfnTopicRule.CloudwatchMetricActionProperty.MetricTimestamp``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metrictimestamp
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.CloudwatchMetricActionProperty", jsii_struct_bases=[_CloudwatchMetricActionProperty])
    class CloudwatchMetricActionProperty(_CloudwatchMetricActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html
        Stability:
            stable
        """
        metricName: str
        """``CfnTopicRule.CloudwatchMetricActionProperty.MetricName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricname
        Stability:
            stable
        """

        metricNamespace: str
        """``CfnTopicRule.CloudwatchMetricActionProperty.MetricNamespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricnamespace
        Stability:
            stable
        """

        metricUnit: str
        """``CfnTopicRule.CloudwatchMetricActionProperty.MetricUnit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricunit
        Stability:
            stable
        """

        metricValue: str
        """``CfnTopicRule.CloudwatchMetricActionProperty.MetricValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricvalue
        Stability:
            stable
        """

        roleArn: str
        """``CfnTopicRule.CloudwatchMetricActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-rolearn
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DynamoDBActionProperty(jsii.compat.TypedDict, total=False):
        hashKeyType: str
        """``CfnTopicRule.DynamoDBActionProperty.HashKeyType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-hashkeytype
        Stability:
            stable
        """
        payloadField: str
        """``CfnTopicRule.DynamoDBActionProperty.PayloadField``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-payloadfield
        Stability:
            stable
        """
        rangeKeyField: str
        """``CfnTopicRule.DynamoDBActionProperty.RangeKeyField``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rangekeyfield
        Stability:
            stable
        """
        rangeKeyType: str
        """``CfnTopicRule.DynamoDBActionProperty.RangeKeyType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rangekeytype
        Stability:
            stable
        """
        rangeKeyValue: str
        """``CfnTopicRule.DynamoDBActionProperty.RangeKeyValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rangekeyvalue
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.DynamoDBActionProperty", jsii_struct_bases=[_DynamoDBActionProperty])
    class DynamoDBActionProperty(_DynamoDBActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html
        Stability:
            stable
        """
        hashKeyField: str
        """``CfnTopicRule.DynamoDBActionProperty.HashKeyField``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-hashkeyfield
        Stability:
            stable
        """

        hashKeyValue: str
        """``CfnTopicRule.DynamoDBActionProperty.HashKeyValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-hashkeyvalue
        Stability:
            stable
        """

        roleArn: str
        """``CfnTopicRule.DynamoDBActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rolearn
        Stability:
            stable
        """

        tableName: str
        """``CfnTopicRule.DynamoDBActionProperty.TableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-tablename
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.DynamoDBv2ActionProperty", jsii_struct_bases=[])
    class DynamoDBv2ActionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbv2action.html
        Stability:
            stable
        """
        putItem: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.PutItemInputProperty"]
        """``CfnTopicRule.DynamoDBv2ActionProperty.PutItem``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbv2action.html#cfn-iot-topicrule-dynamodbv2action-putitem
        Stability:
            stable
        """

        roleArn: str
        """``CfnTopicRule.DynamoDBv2ActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbv2action.html#cfn-iot-topicrule-dynamodbv2action-rolearn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.ElasticsearchActionProperty", jsii_struct_bases=[])
    class ElasticsearchActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html
        Stability:
            stable
        """
        endpoint: str
        """``CfnTopicRule.ElasticsearchActionProperty.Endpoint``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-endpoint
        Stability:
            stable
        """

        id: str
        """``CfnTopicRule.ElasticsearchActionProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-id
        Stability:
            stable
        """

        index: str
        """``CfnTopicRule.ElasticsearchActionProperty.Index``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-index
        Stability:
            stable
        """

        roleArn: str
        """``CfnTopicRule.ElasticsearchActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-rolearn
        Stability:
            stable
        """

        type: str
        """``CfnTopicRule.ElasticsearchActionProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-type
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FirehoseActionProperty(jsii.compat.TypedDict, total=False):
        separator: str
        """``CfnTopicRule.FirehoseActionProperty.Separator``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-separator
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.FirehoseActionProperty", jsii_struct_bases=[_FirehoseActionProperty])
    class FirehoseActionProperty(_FirehoseActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html
        Stability:
            stable
        """
        deliveryStreamName: str
        """``CfnTopicRule.FirehoseActionProperty.DeliveryStreamName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-deliverystreamname
        Stability:
            stable
        """

        roleArn: str
        """``CfnTopicRule.FirehoseActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-rolearn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.IotAnalyticsActionProperty", jsii_struct_bases=[])
    class IotAnalyticsActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html
        Stability:
            stable
        """
        channelName: str
        """``CfnTopicRule.IotAnalyticsActionProperty.ChannelName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html#cfn-iot-topicrule-iotanalyticsaction-channelname
        Stability:
            stable
        """

        roleArn: str
        """``CfnTopicRule.IotAnalyticsActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html#cfn-iot-topicrule-iotanalyticsaction-rolearn
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _KinesisActionProperty(jsii.compat.TypedDict, total=False):
        partitionKey: str
        """``CfnTopicRule.KinesisActionProperty.PartitionKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html#cfn-iot-topicrule-kinesisaction-partitionkey
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.KinesisActionProperty", jsii_struct_bases=[_KinesisActionProperty])
    class KinesisActionProperty(_KinesisActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html
        Stability:
            stable
        """
        roleArn: str
        """``CfnTopicRule.KinesisActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html#cfn-iot-topicrule-kinesisaction-rolearn
        Stability:
            stable
        """

        streamName: str
        """``CfnTopicRule.KinesisActionProperty.StreamName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html#cfn-iot-topicrule-kinesisaction-streamname
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.LambdaActionProperty", jsii_struct_bases=[])
    class LambdaActionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-lambdaaction.html
        Stability:
            stable
        """
        functionArn: str
        """``CfnTopicRule.LambdaActionProperty.FunctionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-lambdaaction.html#cfn-iot-topicrule-lambdaaction-functionarn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.PutItemInputProperty", jsii_struct_bases=[])
    class PutItemInputProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putiteminput.html
        Stability:
            stable
        """
        tableName: str
        """``CfnTopicRule.PutItemInputProperty.TableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putiteminput.html#cfn-iot-topicrule-putiteminput-tablename
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.RepublishActionProperty", jsii_struct_bases=[])
    class RepublishActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html
        Stability:
            stable
        """
        roleArn: str
        """``CfnTopicRule.RepublishActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html#cfn-iot-topicrule-republishaction-rolearn
        Stability:
            stable
        """

        topic: str
        """``CfnTopicRule.RepublishActionProperty.Topic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html#cfn-iot-topicrule-republishaction-topic
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.S3ActionProperty", jsii_struct_bases=[])
    class S3ActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html
        Stability:
            stable
        """
        bucketName: str
        """``CfnTopicRule.S3ActionProperty.BucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-bucketname
        Stability:
            stable
        """

        key: str
        """``CfnTopicRule.S3ActionProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-key
        Stability:
            stable
        """

        roleArn: str
        """``CfnTopicRule.S3ActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-rolearn
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SnsActionProperty(jsii.compat.TypedDict, total=False):
        messageFormat: str
        """``CfnTopicRule.SnsActionProperty.MessageFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html#cfn-iot-topicrule-snsaction-messageformat
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.SnsActionProperty", jsii_struct_bases=[_SnsActionProperty])
    class SnsActionProperty(_SnsActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html
        Stability:
            stable
        """
        roleArn: str
        """``CfnTopicRule.SnsActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html#cfn-iot-topicrule-snsaction-rolearn
        Stability:
            stable
        """

        targetArn: str
        """``CfnTopicRule.SnsActionProperty.TargetArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html#cfn-iot-topicrule-snsaction-targetarn
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SqsActionProperty(jsii.compat.TypedDict, total=False):
        useBase64: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnTopicRule.SqsActionProperty.UseBase64``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html#cfn-iot-topicrule-sqsaction-usebase64
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.SqsActionProperty", jsii_struct_bases=[_SqsActionProperty])
    class SqsActionProperty(_SqsActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html
        Stability:
            stable
        """
        queueUrl: str
        """``CfnTopicRule.SqsActionProperty.QueueUrl``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html#cfn-iot-topicrule-sqsaction-queueurl
        Stability:
            stable
        """

        roleArn: str
        """``CfnTopicRule.SqsActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html#cfn-iot-topicrule-sqsaction-rolearn
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _StepFunctionsActionProperty(jsii.compat.TypedDict, total=False):
        executionNamePrefix: str
        """``CfnTopicRule.StepFunctionsActionProperty.ExecutionNamePrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html#cfn-iot-topicrule-stepfunctionsaction-executionnameprefix
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.StepFunctionsActionProperty", jsii_struct_bases=[_StepFunctionsActionProperty])
    class StepFunctionsActionProperty(_StepFunctionsActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html
        Stability:
            stable
        """
        roleArn: str
        """``CfnTopicRule.StepFunctionsActionProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html#cfn-iot-topicrule-stepfunctionsaction-rolearn
        Stability:
            stable
        """

        stateMachineName: str
        """``CfnTopicRule.StepFunctionsActionProperty.StateMachineName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html#cfn-iot-topicrule-stepfunctionsaction-statemachinename
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _TopicRulePayloadProperty(jsii.compat.TypedDict, total=False):
        awsIotSqlVersion: str
        """``CfnTopicRule.TopicRulePayloadProperty.AwsIotSqlVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-awsiotsqlversion
        Stability:
            stable
        """
        description: str
        """``CfnTopicRule.TopicRulePayloadProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-description
        Stability:
            stable
        """
        errorAction: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.ActionProperty"]
        """``CfnTopicRule.TopicRulePayloadProperty.ErrorAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-erroraction
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRule.TopicRulePayloadProperty", jsii_struct_bases=[_TopicRulePayloadProperty])
    class TopicRulePayloadProperty(_TopicRulePayloadProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html
        Stability:
            stable
        """
        actions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.ActionProperty"]]]
        """``CfnTopicRule.TopicRulePayloadProperty.Actions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-actions
        Stability:
            stable
        """

        ruleDisabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnTopicRule.TopicRulePayloadProperty.RuleDisabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-ruledisabled
        Stability:
            stable
        """

        sql: str
        """``CfnTopicRule.TopicRulePayloadProperty.Sql``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-sql
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnTopicRuleProps(jsii.compat.TypedDict, total=False):
    ruleName: str
    """``AWS::IoT::TopicRule.RuleName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-rulename
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iot.CfnTopicRuleProps", jsii_struct_bases=[_CfnTopicRuleProps])
class CfnTopicRuleProps(_CfnTopicRuleProps):
    """Properties for defining a ``AWS::IoT::TopicRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html
    Stability:
        stable
    """
    topicRulePayload: typing.Union[aws_cdk.core.IResolvable, "CfnTopicRule.TopicRulePayloadProperty"]
    """``AWS::IoT::TopicRule.TopicRulePayload``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-topicrulepayload
    Stability:
        stable
    """

__all__ = ["CfnCertificate", "CfnCertificateProps", "CfnPolicy", "CfnPolicyPrincipalAttachment", "CfnPolicyPrincipalAttachmentProps", "CfnPolicyProps", "CfnThing", "CfnThingPrincipalAttachment", "CfnThingPrincipalAttachmentProps", "CfnThingProps", "CfnTopicRule", "CfnTopicRuleProps", "__jsii_assembly__"]

publication.publish()
