import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/alexa-ask", "0.36.0", __name__, "alexa-ask@0.36.0.jsii.tgz")
class CfnSkill(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/alexa-ask.CfnSkill"):
    """A CloudFormation ``Alexa::ASK::Skill``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html
    Stability:
        stable
    cloudformationResource:
        Alexa::ASK::Skill
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, authentication_configuration: typing.Union["AuthenticationConfigurationProperty", aws_cdk.core.IResolvable], skill_package: typing.Union[aws_cdk.core.IResolvable, "SkillPackageProperty"], vendor_id: str) -> None:
        """Create a new ``Alexa::ASK::Skill``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            authentication_configuration: ``Alexa::ASK::Skill.AuthenticationConfiguration``.
            skill_package: ``Alexa::ASK::Skill.SkillPackage``.
            vendor_id: ``Alexa::ASK::Skill.VendorId``.

        Stability:
            experimental
        """
        props: CfnSkillProps = {"authenticationConfiguration": authentication_configuration, "skillPackage": skill_package, "vendorId": vendor_id}

        jsii.create(CfnSkill, self, [scope, id, props])

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
    @jsii.member(jsii_name="authenticationConfiguration")
    def authentication_configuration(self) -> typing.Union["AuthenticationConfigurationProperty", aws_cdk.core.IResolvable]:
        """``Alexa::ASK::Skill.AuthenticationConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-authenticationconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "authenticationConfiguration")

    @authentication_configuration.setter
    def authentication_configuration(self, value: typing.Union["AuthenticationConfigurationProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "authenticationConfiguration", value)

    @property
    @jsii.member(jsii_name="skillPackage")
    def skill_package(self) -> typing.Union[aws_cdk.core.IResolvable, "SkillPackageProperty"]:
        """``Alexa::ASK::Skill.SkillPackage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-skillpackage
        Stability:
            stable
        """
        return jsii.get(self, "skillPackage")

    @skill_package.setter
    def skill_package(self, value: typing.Union[aws_cdk.core.IResolvable, "SkillPackageProperty"]):
        return jsii.set(self, "skillPackage", value)

    @property
    @jsii.member(jsii_name="vendorId")
    def vendor_id(self) -> str:
        """``Alexa::ASK::Skill.VendorId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-vendorid
        Stability:
            stable
        """
        return jsii.get(self, "vendorId")

    @vendor_id.setter
    def vendor_id(self, value: str):
        return jsii.set(self, "vendorId", value)

    @jsii.data_type(jsii_type="@aws-cdk/alexa-ask.CfnSkill.AuthenticationConfigurationProperty", jsii_struct_bases=[])
    class AuthenticationConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-authenticationconfiguration.html
        Stability:
            stable
        """
        clientId: str
        """``CfnSkill.AuthenticationConfigurationProperty.ClientId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-authenticationconfiguration.html#cfn-ask-skill-authenticationconfiguration-clientid
        Stability:
            stable
        """

        clientSecret: str
        """``CfnSkill.AuthenticationConfigurationProperty.ClientSecret``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-authenticationconfiguration.html#cfn-ask-skill-authenticationconfiguration-clientsecret
        Stability:
            stable
        """

        refreshToken: str
        """``CfnSkill.AuthenticationConfigurationProperty.RefreshToken``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-authenticationconfiguration.html#cfn-ask-skill-authenticationconfiguration-refreshtoken
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/alexa-ask.CfnSkill.OverridesProperty", jsii_struct_bases=[])
    class OverridesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-overrides.html
        Stability:
            stable
        """
        manifest: typing.Any
        """``CfnSkill.OverridesProperty.Manifest``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-overrides.html#cfn-ask-skill-overrides-manifest
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SkillPackageProperty(jsii.compat.TypedDict, total=False):
        overrides: typing.Union[aws_cdk.core.IResolvable, "CfnSkill.OverridesProperty"]
        """``CfnSkill.SkillPackageProperty.Overrides``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-overrides
        Stability:
            stable
        """
        s3BucketRole: str
        """``CfnSkill.SkillPackageProperty.S3BucketRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-s3bucketrole
        Stability:
            stable
        """
        s3ObjectVersion: str
        """``CfnSkill.SkillPackageProperty.S3ObjectVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-s3objectversion
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/alexa-ask.CfnSkill.SkillPackageProperty", jsii_struct_bases=[_SkillPackageProperty])
    class SkillPackageProperty(_SkillPackageProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html
        Stability:
            stable
        """
        s3Bucket: str
        """``CfnSkill.SkillPackageProperty.S3Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-s3bucket
        Stability:
            stable
        """

        s3Key: str
        """``CfnSkill.SkillPackageProperty.S3Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-s3key
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/alexa-ask.CfnSkillProps", jsii_struct_bases=[])
class CfnSkillProps(jsii.compat.TypedDict):
    """Properties for defining a ``Alexa::ASK::Skill``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html
    Stability:
        stable
    """
    authenticationConfiguration: typing.Union["CfnSkill.AuthenticationConfigurationProperty", aws_cdk.core.IResolvable]
    """``Alexa::ASK::Skill.AuthenticationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-authenticationconfiguration
    Stability:
        stable
    """

    skillPackage: typing.Union[aws_cdk.core.IResolvable, "CfnSkill.SkillPackageProperty"]
    """``Alexa::ASK::Skill.SkillPackage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-skillpackage
    Stability:
        stable
    """

    vendorId: str
    """``Alexa::ASK::Skill.VendorId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-vendorid
    Stability:
        stable
    """

__all__ = ["CfnSkill", "CfnSkillProps", "__jsii_assembly__"]

publication.publish()
