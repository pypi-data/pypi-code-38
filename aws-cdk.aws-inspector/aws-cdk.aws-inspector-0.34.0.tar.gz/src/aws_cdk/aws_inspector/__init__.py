import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-inspector", "0.34.0", __name__, "aws-inspector@0.34.0.jsii.tgz")
class CfnAssessmentTarget(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-inspector.CfnAssessmentTarget"):
    """A CloudFormation ``AWS::Inspector::AssessmentTarget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttarget.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Inspector::AssessmentTarget
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, assessment_target_name: typing.Optional[str]=None, resource_group_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Inspector::AssessmentTarget``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            assessmentTargetName: ``AWS::Inspector::AssessmentTarget.AssessmentTargetName``.
            resourceGroupArn: ``AWS::Inspector::AssessmentTarget.ResourceGroupArn``.

        Stability:
            experimental
        """
        props: CfnAssessmentTargetProps = {}

        if assessment_target_name is not None:
            props["assessmentTargetName"] = assessment_target_name

        if resource_group_arn is not None:
            props["resourceGroupArn"] = resource_group_arn

        jsii.create(CfnAssessmentTarget, self, [scope, id, props])

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
    @jsii.member(jsii_name="assessmentTargetArn")
    def assessment_target_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "assessmentTargetArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnAssessmentTargetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-inspector.CfnAssessmentTargetProps", jsii_struct_bases=[])
class CfnAssessmentTargetProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::Inspector::AssessmentTarget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttarget.html
    Stability:
        experimental
    """
    assessmentTargetName: str
    """``AWS::Inspector::AssessmentTarget.AssessmentTargetName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttarget.html#cfn-inspector-assessmenttarget-assessmenttargetname
    Stability:
        experimental
    """

    resourceGroupArn: str
    """``AWS::Inspector::AssessmentTarget.ResourceGroupArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttarget.html#cfn-inspector-assessmenttarget-resourcegrouparn
    Stability:
        experimental
    """

class CfnAssessmentTemplate(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-inspector.CfnAssessmentTemplate"):
    """A CloudFormation ``AWS::Inspector::AssessmentTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Inspector::AssessmentTemplate
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, assessment_target_arn: str, duration_in_seconds: typing.Union[jsii.Number, aws_cdk.cdk.Token], rules_package_arns: typing.List[str], assessment_template_name: typing.Optional[str]=None, user_attributes_for_findings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, aws_cdk.cdk.CfnTag]]]]]=None) -> None:
        """Create a new ``AWS::Inspector::AssessmentTemplate``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            assessmentTargetArn: ``AWS::Inspector::AssessmentTemplate.AssessmentTargetArn``.
            durationInSeconds: ``AWS::Inspector::AssessmentTemplate.DurationInSeconds``.
            rulesPackageArns: ``AWS::Inspector::AssessmentTemplate.RulesPackageArns``.
            assessmentTemplateName: ``AWS::Inspector::AssessmentTemplate.AssessmentTemplateName``.
            userAttributesForFindings: ``AWS::Inspector::AssessmentTemplate.UserAttributesForFindings``.

        Stability:
            experimental
        """
        props: CfnAssessmentTemplateProps = {"assessmentTargetArn": assessment_target_arn, "durationInSeconds": duration_in_seconds, "rulesPackageArns": rules_package_arns}

        if assessment_template_name is not None:
            props["assessmentTemplateName"] = assessment_template_name

        if user_attributes_for_findings is not None:
            props["userAttributesForFindings"] = user_attributes_for_findings

        jsii.create(CfnAssessmentTemplate, self, [scope, id, props])

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
    @jsii.member(jsii_name="assessmentTemplateArn")
    def assessment_template_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "assessmentTemplateArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnAssessmentTemplateProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAssessmentTemplateProps(jsii.compat.TypedDict, total=False):
    assessmentTemplateName: str
    """``AWS::Inspector::AssessmentTemplate.AssessmentTemplateName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-assessmenttemplatename
    Stability:
        experimental
    """
    userAttributesForFindings: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, aws_cdk.cdk.CfnTag]]]
    """``AWS::Inspector::AssessmentTemplate.UserAttributesForFindings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-userattributesforfindings
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-inspector.CfnAssessmentTemplateProps", jsii_struct_bases=[_CfnAssessmentTemplateProps])
class CfnAssessmentTemplateProps(_CfnAssessmentTemplateProps):
    """Properties for defining a ``AWS::Inspector::AssessmentTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html
    Stability:
        experimental
    """
    assessmentTargetArn: str
    """``AWS::Inspector::AssessmentTemplate.AssessmentTargetArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-assessmenttargetarn
    Stability:
        experimental
    """

    durationInSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Inspector::AssessmentTemplate.DurationInSeconds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-durationinseconds
    Stability:
        experimental
    """

    rulesPackageArns: typing.List[str]
    """``AWS::Inspector::AssessmentTemplate.RulesPackageArns``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-rulespackagearns
    Stability:
        experimental
    """

class CfnResourceGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-inspector.CfnResourceGroup"):
    """A CloudFormation ``AWS::Inspector::ResourceGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-resourcegroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Inspector::ResourceGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, resource_group_tags: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, aws_cdk.cdk.CfnTag]]]) -> None:
        """Create a new ``AWS::Inspector::ResourceGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            resourceGroupTags: ``AWS::Inspector::ResourceGroup.ResourceGroupTags``.

        Stability:
            experimental
        """
        props: CfnResourceGroupProps = {"resourceGroupTags": resource_group_tags}

        jsii.create(CfnResourceGroup, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnResourceGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="resourceGroupArn")
    def resource_group_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "resourceGroupArn")


@jsii.data_type(jsii_type="@aws-cdk/aws-inspector.CfnResourceGroupProps", jsii_struct_bases=[])
class CfnResourceGroupProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Inspector::ResourceGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-resourcegroup.html
    Stability:
        experimental
    """
    resourceGroupTags: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, aws_cdk.cdk.CfnTag]]]
    """``AWS::Inspector::ResourceGroup.ResourceGroupTags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-resourcegroup.html#cfn-inspector-resourcegroup-resourcegrouptags
    Stability:
        experimental
    """

__all__ = ["CfnAssessmentTarget", "CfnAssessmentTargetProps", "CfnAssessmentTemplate", "CfnAssessmentTemplateProps", "CfnResourceGroup", "CfnResourceGroupProps", "__jsii_assembly__"]

publication.publish()
