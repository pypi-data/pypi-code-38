import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/alexa-ask", "0.34.0", __name__, "alexa-ask@0.34.0.jsii.tgz")
class CfnSkill(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/alexa-ask.CfnSkill"):
    """A CloudFormation ``Alexa::ASK::Skill``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html
    Stability:
        experimental
    cloudformationResource:
        Alexa::ASK::Skill
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, authentication_configuration: typing.Union["AuthenticationConfigurationProperty", aws_cdk.cdk.Token], skill_package: typing.Union[aws_cdk.cdk.Token, "SkillPackageProperty"], vendor_id: str) -> None:
        """Create a new ``Alexa::ASK::Skill``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            authenticationConfiguration: ``Alexa::ASK::Skill.AuthenticationConfiguration``.
            skillPackage: ``Alexa::ASK::Skill.SkillPackage``.
            vendorId: ``Alexa::ASK::Skill.VendorId``.

        Stability:
            experimental
        """
        props: CfnSkillProps = {"authenticationConfiguration": authentication_configuration, "skillPackage": skill_package, "vendorId": vendor_id}

        jsii.create(CfnSkill, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSkillProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="skillId")
    def skill_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "skillId")

    @jsii.data_type(jsii_type="@aws-cdk/alexa-ask.CfnSkill.AuthenticationConfigurationProperty", jsii_struct_bases=[])
    class AuthenticationConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-authenticationconfiguration.html
        Stability:
            experimental
        """
        clientId: str
        """``CfnSkill.AuthenticationConfigurationProperty.ClientId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-authenticationconfiguration.html#cfn-ask-skill-authenticationconfiguration-clientid
        Stability:
            experimental
        """

        clientSecret: str
        """``CfnSkill.AuthenticationConfigurationProperty.ClientSecret``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-authenticationconfiguration.html#cfn-ask-skill-authenticationconfiguration-clientsecret
        Stability:
            experimental
        """

        refreshToken: str
        """``CfnSkill.AuthenticationConfigurationProperty.RefreshToken``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-authenticationconfiguration.html#cfn-ask-skill-authenticationconfiguration-refreshtoken
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/alexa-ask.CfnSkill.OverridesProperty", jsii_struct_bases=[])
    class OverridesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-overrides.html
        Stability:
            experimental
        """
        manifest: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnSkill.OverridesProperty.Manifest``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-overrides.html#cfn-ask-skill-overrides-manifest
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SkillPackageProperty(jsii.compat.TypedDict, total=False):
        overrides: typing.Union[aws_cdk.cdk.Token, "CfnSkill.OverridesProperty"]
        """``CfnSkill.SkillPackageProperty.Overrides``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-overrides
        Stability:
            experimental
        """
        s3BucketRole: str
        """``CfnSkill.SkillPackageProperty.S3BucketRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-s3bucketrole
        Stability:
            experimental
        """
        s3ObjectVersion: str
        """``CfnSkill.SkillPackageProperty.S3ObjectVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-s3objectversion
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/alexa-ask.CfnSkill.SkillPackageProperty", jsii_struct_bases=[_SkillPackageProperty])
    class SkillPackageProperty(_SkillPackageProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html
        Stability:
            experimental
        """
        s3Bucket: str
        """``CfnSkill.SkillPackageProperty.S3Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-s3bucket
        Stability:
            experimental
        """

        s3Key: str
        """``CfnSkill.SkillPackageProperty.S3Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ask-skill-skillpackage.html#cfn-ask-skill-skillpackage-s3key
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/alexa-ask.CfnSkillProps", jsii_struct_bases=[])
class CfnSkillProps(jsii.compat.TypedDict):
    """Properties for defining a ``Alexa::ASK::Skill``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html
    Stability:
        experimental
    """
    authenticationConfiguration: typing.Union["CfnSkill.AuthenticationConfigurationProperty", aws_cdk.cdk.Token]
    """``Alexa::ASK::Skill.AuthenticationConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-authenticationconfiguration
    Stability:
        experimental
    """

    skillPackage: typing.Union[aws_cdk.cdk.Token, "CfnSkill.SkillPackageProperty"]
    """``Alexa::ASK::Skill.SkillPackage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-skillpackage
    Stability:
        experimental
    """

    vendorId: str
    """``Alexa::ASK::Skill.VendorId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ask-skill.html#cfn-ask-skill-vendorid
    Stability:
        experimental
    """

__all__ = ["CfnSkill", "CfnSkillProps", "__jsii_assembly__"]

publication.publish()
