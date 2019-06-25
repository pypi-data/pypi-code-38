import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-inspector", "0.36.0", __name__, "aws-inspector@0.36.0.jsii.tgz")
class CfnAssessmentTarget(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-inspector.CfnAssessmentTarget"):
    """A CloudFormation ``AWS::Inspector::AssessmentTarget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttarget.html
    Stability:
        stable
    cloudformationResource:
        AWS::Inspector::AssessmentTarget
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, assessment_target_name: typing.Optional[str]=None, resource_group_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Inspector::AssessmentTarget``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            assessment_target_name: ``AWS::Inspector::AssessmentTarget.AssessmentTargetName``.
            resource_group_arn: ``AWS::Inspector::AssessmentTarget.ResourceGroupArn``.

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
    @jsii.member(jsii_name="assessmentTargetName")
    def assessment_target_name(self) -> typing.Optional[str]:
        """``AWS::Inspector::AssessmentTarget.AssessmentTargetName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttarget.html#cfn-inspector-assessmenttarget-assessmenttargetname
        Stability:
            stable
        """
        return jsii.get(self, "assessmentTargetName")

    @assessment_target_name.setter
    def assessment_target_name(self, value: typing.Optional[str]):
        return jsii.set(self, "assessmentTargetName", value)

    @property
    @jsii.member(jsii_name="resourceGroupArn")
    def resource_group_arn(self) -> typing.Optional[str]:
        """``AWS::Inspector::AssessmentTarget.ResourceGroupArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttarget.html#cfn-inspector-assessmenttarget-resourcegrouparn
        Stability:
            stable
        """
        return jsii.get(self, "resourceGroupArn")

    @resource_group_arn.setter
    def resource_group_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "resourceGroupArn", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-inspector.CfnAssessmentTargetProps", jsii_struct_bases=[])
class CfnAssessmentTargetProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::Inspector::AssessmentTarget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttarget.html
    Stability:
        stable
    """
    assessmentTargetName: str
    """``AWS::Inspector::AssessmentTarget.AssessmentTargetName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttarget.html#cfn-inspector-assessmenttarget-assessmenttargetname
    Stability:
        stable
    """

    resourceGroupArn: str
    """``AWS::Inspector::AssessmentTarget.ResourceGroupArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttarget.html#cfn-inspector-assessmenttarget-resourcegrouparn
    Stability:
        stable
    """

class CfnAssessmentTemplate(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-inspector.CfnAssessmentTemplate"):
    """A CloudFormation ``AWS::Inspector::AssessmentTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html
    Stability:
        stable
    cloudformationResource:
        AWS::Inspector::AssessmentTemplate
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, assessment_target_arn: str, duration_in_seconds: jsii.Number, rules_package_arns: typing.List[str], assessment_template_name: typing.Optional[str]=None, user_attributes_for_findings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.CfnTag, aws_cdk.core.IResolvable]]]]]=None) -> None:
        """Create a new ``AWS::Inspector::AssessmentTemplate``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            assessment_target_arn: ``AWS::Inspector::AssessmentTemplate.AssessmentTargetArn``.
            duration_in_seconds: ``AWS::Inspector::AssessmentTemplate.DurationInSeconds``.
            rules_package_arns: ``AWS::Inspector::AssessmentTemplate.RulesPackageArns``.
            assessment_template_name: ``AWS::Inspector::AssessmentTemplate.AssessmentTemplateName``.
            user_attributes_for_findings: ``AWS::Inspector::AssessmentTemplate.UserAttributesForFindings``.

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
    @jsii.member(jsii_name="assessmentTargetArn")
    def assessment_target_arn(self) -> str:
        """``AWS::Inspector::AssessmentTemplate.AssessmentTargetArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-assessmenttargetarn
        Stability:
            stable
        """
        return jsii.get(self, "assessmentTargetArn")

    @assessment_target_arn.setter
    def assessment_target_arn(self, value: str):
        return jsii.set(self, "assessmentTargetArn", value)

    @property
    @jsii.member(jsii_name="durationInSeconds")
    def duration_in_seconds(self) -> jsii.Number:
        """``AWS::Inspector::AssessmentTemplate.DurationInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-durationinseconds
        Stability:
            stable
        """
        return jsii.get(self, "durationInSeconds")

    @duration_in_seconds.setter
    def duration_in_seconds(self, value: jsii.Number):
        return jsii.set(self, "durationInSeconds", value)

    @property
    @jsii.member(jsii_name="rulesPackageArns")
    def rules_package_arns(self) -> typing.List[str]:
        """``AWS::Inspector::AssessmentTemplate.RulesPackageArns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-rulespackagearns
        Stability:
            stable
        """
        return jsii.get(self, "rulesPackageArns")

    @rules_package_arns.setter
    def rules_package_arns(self, value: typing.List[str]):
        return jsii.set(self, "rulesPackageArns", value)

    @property
    @jsii.member(jsii_name="assessmentTemplateName")
    def assessment_template_name(self) -> typing.Optional[str]:
        """``AWS::Inspector::AssessmentTemplate.AssessmentTemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-assessmenttemplatename
        Stability:
            stable
        """
        return jsii.get(self, "assessmentTemplateName")

    @assessment_template_name.setter
    def assessment_template_name(self, value: typing.Optional[str]):
        return jsii.set(self, "assessmentTemplateName", value)

    @property
    @jsii.member(jsii_name="userAttributesForFindings")
    def user_attributes_for_findings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.CfnTag, aws_cdk.core.IResolvable]]]]]:
        """``AWS::Inspector::AssessmentTemplate.UserAttributesForFindings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-userattributesforfindings
        Stability:
            stable
        """
        return jsii.get(self, "userAttributesForFindings")

    @user_attributes_for_findings.setter
    def user_attributes_for_findings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.CfnTag, aws_cdk.core.IResolvable]]]]]):
        return jsii.set(self, "userAttributesForFindings", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAssessmentTemplateProps(jsii.compat.TypedDict, total=False):
    assessmentTemplateName: str
    """``AWS::Inspector::AssessmentTemplate.AssessmentTemplateName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-assessmenttemplatename
    Stability:
        stable
    """
    userAttributesForFindings: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.CfnTag, aws_cdk.core.IResolvable]]]
    """``AWS::Inspector::AssessmentTemplate.UserAttributesForFindings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-userattributesforfindings
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-inspector.CfnAssessmentTemplateProps", jsii_struct_bases=[_CfnAssessmentTemplateProps])
class CfnAssessmentTemplateProps(_CfnAssessmentTemplateProps):
    """Properties for defining a ``AWS::Inspector::AssessmentTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html
    Stability:
        stable
    """
    assessmentTargetArn: str
    """``AWS::Inspector::AssessmentTemplate.AssessmentTargetArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-assessmenttargetarn
    Stability:
        stable
    """

    durationInSeconds: jsii.Number
    """``AWS::Inspector::AssessmentTemplate.DurationInSeconds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-durationinseconds
    Stability:
        stable
    """

    rulesPackageArns: typing.List[str]
    """``AWS::Inspector::AssessmentTemplate.RulesPackageArns``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-assessmenttemplate.html#cfn-inspector-assessmenttemplate-rulespackagearns
    Stability:
        stable
    """

class CfnResourceGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-inspector.CfnResourceGroup"):
    """A CloudFormation ``AWS::Inspector::ResourceGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-resourcegroup.html
    Stability:
        stable
    cloudformationResource:
        AWS::Inspector::ResourceGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, resource_group_tags: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.CfnTag, aws_cdk.core.IResolvable]]]) -> None:
        """Create a new ``AWS::Inspector::ResourceGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            resource_group_tags: ``AWS::Inspector::ResourceGroup.ResourceGroupTags``.

        Stability:
            experimental
        """
        props: CfnResourceGroupProps = {"resourceGroupTags": resource_group_tags}

        jsii.create(CfnResourceGroup, self, [scope, id, props])

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
    @jsii.member(jsii_name="resourceGroupTags")
    def resource_group_tags(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.CfnTag, aws_cdk.core.IResolvable]]]:
        """``AWS::Inspector::ResourceGroup.ResourceGroupTags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-resourcegroup.html#cfn-inspector-resourcegroup-resourcegrouptags
        Stability:
            stable
        """
        return jsii.get(self, "resourceGroupTags")

    @resource_group_tags.setter
    def resource_group_tags(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.CfnTag, aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "resourceGroupTags", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-inspector.CfnResourceGroupProps", jsii_struct_bases=[])
class CfnResourceGroupProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Inspector::ResourceGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-resourcegroup.html
    Stability:
        stable
    """
    resourceGroupTags: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.CfnTag, aws_cdk.core.IResolvable]]]
    """``AWS::Inspector::ResourceGroup.ResourceGroupTags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-inspector-resourcegroup.html#cfn-inspector-resourcegroup-resourcegrouptags
    Stability:
        stable
    """

__all__ = ["CfnAssessmentTarget", "CfnAssessmentTargetProps", "CfnAssessmentTemplate", "CfnAssessmentTemplateProps", "CfnResourceGroup", "CfnResourceGroupProps", "__jsii_assembly__"]

publication.publish()
