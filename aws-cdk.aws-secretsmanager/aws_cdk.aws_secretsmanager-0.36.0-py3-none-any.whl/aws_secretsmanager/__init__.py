import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-secretsmanager", "0.36.0", __name__, "aws-secretsmanager@0.36.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.AttachedSecretOptions", jsii_struct_bases=[])
class AttachedSecretOptions(jsii.compat.TypedDict):
    """Options to add a secret attachment to a secret.

    Stability:
        experimental
    """
    target: "ISecretAttachmentTarget"
    """The target to attach the secret to.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-secretsmanager.AttachmentTargetType")
class AttachmentTargetType(enum.Enum):
    """The type of service or database that's being associated with the secret.

    Stability:
        experimental
    """
    INSTANCE = "INSTANCE"
    """A database instance.

    Stability:
        experimental
    """
    CLUSTER = "CLUSTER"
    """A database cluster.

    Stability:
        experimental
    """

class CfnResourcePolicy(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-secretsmanager.CfnResourcePolicy"):
    """A CloudFormation ``AWS::SecretsManager::ResourcePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html
    Stability:
        stable
    cloudformationResource:
        AWS::SecretsManager::ResourcePolicy
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, resource_policy: typing.Any, secret_id: str) -> None:
        """Create a new ``AWS::SecretsManager::ResourcePolicy``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            resource_policy: ``AWS::SecretsManager::ResourcePolicy.ResourcePolicy``.
            secret_id: ``AWS::SecretsManager::ResourcePolicy.SecretId``.

        Stability:
            experimental
        """
        props: CfnResourcePolicyProps = {"resourcePolicy": resource_policy, "secretId": secret_id}

        jsii.create(CfnResourcePolicy, self, [scope, id, props])

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
    @jsii.member(jsii_name="resourcePolicy")
    def resource_policy(self) -> typing.Any:
        """``AWS::SecretsManager::ResourcePolicy.ResourcePolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html#cfn-secretsmanager-resourcepolicy-resourcepolicy
        Stability:
            stable
        """
        return jsii.get(self, "resourcePolicy")

    @resource_policy.setter
    def resource_policy(self, value: typing.Any):
        return jsii.set(self, "resourcePolicy", value)

    @property
    @jsii.member(jsii_name="secretId")
    def secret_id(self) -> str:
        """``AWS::SecretsManager::ResourcePolicy.SecretId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html#cfn-secretsmanager-resourcepolicy-secretid
        Stability:
            stable
        """
        return jsii.get(self, "secretId")

    @secret_id.setter
    def secret_id(self, value: str):
        return jsii.set(self, "secretId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.CfnResourcePolicyProps", jsii_struct_bases=[])
class CfnResourcePolicyProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::SecretsManager::ResourcePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html
    Stability:
        stable
    """
    resourcePolicy: typing.Any
    """``AWS::SecretsManager::ResourcePolicy.ResourcePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html#cfn-secretsmanager-resourcepolicy-resourcepolicy
    Stability:
        stable
    """

    secretId: str
    """``AWS::SecretsManager::ResourcePolicy.SecretId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-resourcepolicy.html#cfn-secretsmanager-resourcepolicy-secretid
    Stability:
        stable
    """

class CfnRotationSchedule(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-secretsmanager.CfnRotationSchedule"):
    """A CloudFormation ``AWS::SecretsManager::RotationSchedule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html
    Stability:
        stable
    cloudformationResource:
        AWS::SecretsManager::RotationSchedule
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, secret_id: str, rotation_lambda_arn: typing.Optional[str]=None, rotation_rules: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RotationRulesProperty"]]]=None) -> None:
        """Create a new ``AWS::SecretsManager::RotationSchedule``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            secret_id: ``AWS::SecretsManager::RotationSchedule.SecretId``.
            rotation_lambda_arn: ``AWS::SecretsManager::RotationSchedule.RotationLambdaARN``.
            rotation_rules: ``AWS::SecretsManager::RotationSchedule.RotationRules``.

        Stability:
            experimental
        """
        props: CfnRotationScheduleProps = {"secretId": secret_id}

        if rotation_lambda_arn is not None:
            props["rotationLambdaArn"] = rotation_lambda_arn

        if rotation_rules is not None:
            props["rotationRules"] = rotation_rules

        jsii.create(CfnRotationSchedule, self, [scope, id, props])

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
    @jsii.member(jsii_name="secretId")
    def secret_id(self) -> str:
        """``AWS::SecretsManager::RotationSchedule.SecretId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-secretid
        Stability:
            stable
        """
        return jsii.get(self, "secretId")

    @secret_id.setter
    def secret_id(self, value: str):
        return jsii.set(self, "secretId", value)

    @property
    @jsii.member(jsii_name="rotationLambdaArn")
    def rotation_lambda_arn(self) -> typing.Optional[str]:
        """``AWS::SecretsManager::RotationSchedule.RotationLambdaARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-rotationlambdaarn
        Stability:
            stable
        """
        return jsii.get(self, "rotationLambdaArn")

    @rotation_lambda_arn.setter
    def rotation_lambda_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "rotationLambdaArn", value)

    @property
    @jsii.member(jsii_name="rotationRules")
    def rotation_rules(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RotationRulesProperty"]]]:
        """``AWS::SecretsManager::RotationSchedule.RotationRules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-rotationrules
        Stability:
            stable
        """
        return jsii.get(self, "rotationRules")

    @rotation_rules.setter
    def rotation_rules(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RotationRulesProperty"]]]):
        return jsii.set(self, "rotationRules", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.CfnRotationSchedule.RotationRulesProperty", jsii_struct_bases=[])
    class RotationRulesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-rotationschedule-rotationrules.html
        Stability:
            stable
        """
        automaticallyAfterDays: jsii.Number
        """``CfnRotationSchedule.RotationRulesProperty.AutomaticallyAfterDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-rotationschedule-rotationrules.html#cfn-secretsmanager-rotationschedule-rotationrules-automaticallyafterdays
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRotationScheduleProps(jsii.compat.TypedDict, total=False):
    rotationLambdaArn: str
    """``AWS::SecretsManager::RotationSchedule.RotationLambdaARN``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-rotationlambdaarn
    Stability:
        stable
    """
    rotationRules: typing.Union[aws_cdk.core.IResolvable, "CfnRotationSchedule.RotationRulesProperty"]
    """``AWS::SecretsManager::RotationSchedule.RotationRules``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-rotationrules
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.CfnRotationScheduleProps", jsii_struct_bases=[_CfnRotationScheduleProps])
class CfnRotationScheduleProps(_CfnRotationScheduleProps):
    """Properties for defining a ``AWS::SecretsManager::RotationSchedule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html
    Stability:
        stable
    """
    secretId: str
    """``AWS::SecretsManager::RotationSchedule.SecretId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-rotationschedule.html#cfn-secretsmanager-rotationschedule-secretid
    Stability:
        stable
    """

class CfnSecret(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-secretsmanager.CfnSecret"):
    """A CloudFormation ``AWS::SecretsManager::Secret``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html
    Stability:
        stable
    cloudformationResource:
        AWS::SecretsManager::Secret
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, description: typing.Optional[str]=None, generate_secret_string: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["GenerateSecretStringProperty"]]]=None, kms_key_id: typing.Optional[str]=None, name: typing.Optional[str]=None, secret_string: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::SecretsManager::Secret``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::SecretsManager::Secret.Description``.
            generate_secret_string: ``AWS::SecretsManager::Secret.GenerateSecretString``.
            kms_key_id: ``AWS::SecretsManager::Secret.KmsKeyId``.
            name: ``AWS::SecretsManager::Secret.Name``.
            secret_string: ``AWS::SecretsManager::Secret.SecretString``.
            tags: ``AWS::SecretsManager::Secret.Tags``.

        Stability:
            experimental
        """
        props: CfnSecretProps = {}

        if description is not None:
            props["description"] = description

        if generate_secret_string is not None:
            props["generateSecretString"] = generate_secret_string

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

        if name is not None:
            props["name"] = name

        if secret_string is not None:
            props["secretString"] = secret_string

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnSecret, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::SecretsManager::Secret.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::SecretsManager::Secret.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="generateSecretString")
    def generate_secret_string(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["GenerateSecretStringProperty"]]]:
        """``AWS::SecretsManager::Secret.GenerateSecretString``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-generatesecretstring
        Stability:
            stable
        """
        return jsii.get(self, "generateSecretString")

    @generate_secret_string.setter
    def generate_secret_string(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["GenerateSecretStringProperty"]]]):
        return jsii.set(self, "generateSecretString", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::SecretsManager::Secret.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-kmskeyid
        Stability:
            stable
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::SecretsManager::Secret.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="secretString")
    def secret_string(self) -> typing.Optional[str]:
        """``AWS::SecretsManager::Secret.SecretString``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-secretstring
        Stability:
            stable
        """
        return jsii.get(self, "secretString")

    @secret_string.setter
    def secret_string(self, value: typing.Optional[str]):
        return jsii.set(self, "secretString", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.CfnSecret.GenerateSecretStringProperty", jsii_struct_bases=[])
    class GenerateSecretStringProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html
        Stability:
            stable
        """
        excludeCharacters: str
        """``CfnSecret.GenerateSecretStringProperty.ExcludeCharacters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-excludecharacters
        Stability:
            stable
        """

        excludeLowercase: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSecret.GenerateSecretStringProperty.ExcludeLowercase``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-excludelowercase
        Stability:
            stable
        """

        excludeNumbers: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSecret.GenerateSecretStringProperty.ExcludeNumbers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-excludenumbers
        Stability:
            stable
        """

        excludePunctuation: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSecret.GenerateSecretStringProperty.ExcludePunctuation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-excludepunctuation
        Stability:
            stable
        """

        excludeUppercase: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSecret.GenerateSecretStringProperty.ExcludeUppercase``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-excludeuppercase
        Stability:
            stable
        """

        generateStringKey: str
        """``CfnSecret.GenerateSecretStringProperty.GenerateStringKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-generatestringkey
        Stability:
            stable
        """

        includeSpace: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSecret.GenerateSecretStringProperty.IncludeSpace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-includespace
        Stability:
            stable
        """

        passwordLength: jsii.Number
        """``CfnSecret.GenerateSecretStringProperty.PasswordLength``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-passwordlength
        Stability:
            stable
        """

        requireEachIncludedType: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnSecret.GenerateSecretStringProperty.RequireEachIncludedType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-requireeachincludedtype
        Stability:
            stable
        """

        secretStringTemplate: str
        """``CfnSecret.GenerateSecretStringProperty.SecretStringTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-secretsmanager-secret-generatesecretstring.html#cfn-secretsmanager-secret-generatesecretstring-secretstringtemplate
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.CfnSecretProps", jsii_struct_bases=[])
class CfnSecretProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::SecretsManager::Secret``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html
    Stability:
        stable
    """
    description: str
    """``AWS::SecretsManager::Secret.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-description
    Stability:
        stable
    """

    generateSecretString: typing.Union[aws_cdk.core.IResolvable, "CfnSecret.GenerateSecretStringProperty"]
    """``AWS::SecretsManager::Secret.GenerateSecretString``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-generatesecretstring
    Stability:
        stable
    """

    kmsKeyId: str
    """``AWS::SecretsManager::Secret.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-kmskeyid
    Stability:
        stable
    """

    name: str
    """``AWS::SecretsManager::Secret.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-name
    Stability:
        stable
    """

    secretString: str
    """``AWS::SecretsManager::Secret.SecretString``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-secretstring
    Stability:
        stable
    """

    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::SecretsManager::Secret.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html#cfn-secretsmanager-secret-tags
    Stability:
        stable
    """

class CfnSecretTargetAttachment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-secretsmanager.CfnSecretTargetAttachment"):
    """A CloudFormation ``AWS::SecretsManager::SecretTargetAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html
    Stability:
        stable
    cloudformationResource:
        AWS::SecretsManager::SecretTargetAttachment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, secret_id: str, target_id: str, target_type: str) -> None:
        """Create a new ``AWS::SecretsManager::SecretTargetAttachment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            secret_id: ``AWS::SecretsManager::SecretTargetAttachment.SecretId``.
            target_id: ``AWS::SecretsManager::SecretTargetAttachment.TargetId``.
            target_type: ``AWS::SecretsManager::SecretTargetAttachment.TargetType``.

        Stability:
            experimental
        """
        props: CfnSecretTargetAttachmentProps = {"secretId": secret_id, "targetId": target_id, "targetType": target_type}

        jsii.create(CfnSecretTargetAttachment, self, [scope, id, props])

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
    @jsii.member(jsii_name="secretId")
    def secret_id(self) -> str:
        """``AWS::SecretsManager::SecretTargetAttachment.SecretId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html#cfn-secretsmanager-secrettargetattachment-secretid
        Stability:
            stable
        """
        return jsii.get(self, "secretId")

    @secret_id.setter
    def secret_id(self, value: str):
        return jsii.set(self, "secretId", value)

    @property
    @jsii.member(jsii_name="targetId")
    def target_id(self) -> str:
        """``AWS::SecretsManager::SecretTargetAttachment.TargetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html#cfn-secretsmanager-secrettargetattachment-targetid
        Stability:
            stable
        """
        return jsii.get(self, "targetId")

    @target_id.setter
    def target_id(self, value: str):
        return jsii.set(self, "targetId", value)

    @property
    @jsii.member(jsii_name="targetType")
    def target_type(self) -> str:
        """``AWS::SecretsManager::SecretTargetAttachment.TargetType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html#cfn-secretsmanager-secrettargetattachment-targettype
        Stability:
            stable
        """
        return jsii.get(self, "targetType")

    @target_type.setter
    def target_type(self, value: str):
        return jsii.set(self, "targetType", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.CfnSecretTargetAttachmentProps", jsii_struct_bases=[])
class CfnSecretTargetAttachmentProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::SecretsManager::SecretTargetAttachment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html
    Stability:
        stable
    """
    secretId: str
    """``AWS::SecretsManager::SecretTargetAttachment.SecretId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html#cfn-secretsmanager-secrettargetattachment-secretid
    Stability:
        stable
    """

    targetId: str
    """``AWS::SecretsManager::SecretTargetAttachment.TargetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html#cfn-secretsmanager-secrettargetattachment-targetid
    Stability:
        stable
    """

    targetType: str
    """``AWS::SecretsManager::SecretTargetAttachment.TargetType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html#cfn-secretsmanager-secrettargetattachment-targettype
    Stability:
        stable
    """

@jsii.interface(jsii_type="@aws-cdk/aws-secretsmanager.ISecret")
class ISecret(aws_cdk.core.IResource, jsii.compat.Protocol):
    """A secret in AWS Secrets Manager.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ISecretProxy

    @property
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> str:
        """The ARN of the secret in AWS Secrets Manager.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="secretValue")
    def secret_value(self) -> aws_cdk.core.SecretValue:
        """Retrieve the value of the stored secret as a ``SecretValue``.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """The customer-managed encryption key that is used to encrypt this secret, if any.

        When not specified, the default
        KMS key for the account and region is being used.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addRotationSchedule")
    def add_rotation_schedule(self, id: str, *, rotation_lambda: aws_cdk.aws_lambda.IFunction, automatically_after: typing.Optional[aws_cdk.core.Duration]=None) -> "RotationSchedule":
        """Adds a rotation schedule to the secret.

        Arguments:
            id: -
            options: -
            rotation_lambda: THe Lambda function that can rotate the secret.
            automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, grantee: aws_cdk.aws_iam.IGrantable, version_stages: typing.Optional[typing.List[str]]=None) -> aws_cdk.aws_iam.Grant:
        """Grants reading the secret value to some role.

        Arguments:
            grantee: the principal being granted permission.
            version_stages: the version stages the grant is limited to. If not specified, no restriction on the version stages is applied.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="secretValueFromJson")
    def secret_value_from_json(self, key: str) -> aws_cdk.core.SecretValue:
        """Interpret the secret as a JSON object and return a field's value from it as a ``SecretValue``.

        Arguments:
            key: -

        Stability:
            experimental
        """
        ...


class _ISecretProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """A secret in AWS Secrets Manager.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-secretsmanager.ISecret"
    @property
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> str:
        """The ARN of the secret in AWS Secrets Manager.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "secretArn")

    @property
    @jsii.member(jsii_name="secretValue")
    def secret_value(self) -> aws_cdk.core.SecretValue:
        """Retrieve the value of the stored secret as a ``SecretValue``.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "secretValue")

    @property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """The customer-managed encryption key that is used to encrypt this secret, if any.

        When not specified, the default
        KMS key for the account and region is being used.

        Stability:
            experimental
        """
        return jsii.get(self, "encryptionKey")

    @jsii.member(jsii_name="addRotationSchedule")
    def add_rotation_schedule(self, id: str, *, rotation_lambda: aws_cdk.aws_lambda.IFunction, automatically_after: typing.Optional[aws_cdk.core.Duration]=None) -> "RotationSchedule":
        """Adds a rotation schedule to the secret.

        Arguments:
            id: -
            options: -
            rotation_lambda: THe Lambda function that can rotate the secret.
            automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)

        Stability:
            experimental
        """
        options: RotationScheduleOptions = {"rotationLambda": rotation_lambda}

        if automatically_after is not None:
            options["automaticallyAfter"] = automatically_after

        return jsii.invoke(self, "addRotationSchedule", [id, options])

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, grantee: aws_cdk.aws_iam.IGrantable, version_stages: typing.Optional[typing.List[str]]=None) -> aws_cdk.aws_iam.Grant:
        """Grants reading the secret value to some role.

        Arguments:
            grantee: the principal being granted permission.
            version_stages: the version stages the grant is limited to. If not specified, no restriction on the version stages is applied.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantRead", [grantee, version_stages])

    @jsii.member(jsii_name="secretValueFromJson")
    def secret_value_from_json(self, key: str) -> aws_cdk.core.SecretValue:
        """Interpret the secret as a JSON object and return a field's value from it as a ``SecretValue``.

        Arguments:
            key: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "secretValueFromJson", [key])


@jsii.interface(jsii_type="@aws-cdk/aws-secretsmanager.ISecretAttachmentTarget")
class ISecretAttachmentTarget(jsii.compat.Protocol):
    """A secret attachment target.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ISecretAttachmentTargetProxy

    @jsii.member(jsii_name="asSecretAttachmentTarget")
    def as_secret_attachment_target(self) -> "SecretAttachmentTargetProps":
        """Renders the target specifications.

        Stability:
            experimental
        """
        ...


class _ISecretAttachmentTargetProxy():
    """A secret attachment target.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-secretsmanager.ISecretAttachmentTarget"
    @jsii.member(jsii_name="asSecretAttachmentTarget")
    def as_secret_attachment_target(self) -> "SecretAttachmentTargetProps":
        """Renders the target specifications.

        Stability:
            experimental
        """
        return jsii.invoke(self, "asSecretAttachmentTarget", [])


@jsii.interface(jsii_type="@aws-cdk/aws-secretsmanager.ISecretTargetAttachment")
class ISecretTargetAttachment(ISecret, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ISecretTargetAttachmentProxy

    @property
    @jsii.member(jsii_name="secretTargetAttachmentSecretArn")
    def secret_target_attachment_secret_arn(self) -> str:
        """Same as ``secretArn``.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _ISecretTargetAttachmentProxy(jsii.proxy_for(ISecret)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-secretsmanager.ISecretTargetAttachment"
    @property
    @jsii.member(jsii_name="secretTargetAttachmentSecretArn")
    def secret_target_attachment_secret_arn(self) -> str:
        """Same as ``secretArn``.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "secretTargetAttachmentSecretArn")


class RotationSchedule(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-secretsmanager.RotationSchedule"):
    """A rotation schedule.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, secret: "ISecret", rotation_lambda: aws_cdk.aws_lambda.IFunction, automatically_after: typing.Optional[aws_cdk.core.Duration]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            secret: The secret to rotate.
            rotation_lambda: THe Lambda function that can rotate the secret.
            automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)

        Stability:
            experimental
        """
        props: RotationScheduleProps = {"secret": secret, "rotationLambda": rotation_lambda}

        if automatically_after is not None:
            props["automaticallyAfter"] = automatically_after

        jsii.create(RotationSchedule, self, [scope, id, props])


@jsii.data_type_optionals(jsii_struct_bases=[])
class _RotationScheduleOptions(jsii.compat.TypedDict, total=False):
    automaticallyAfter: aws_cdk.core.Duration
    """Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation.

    Default:
        Duration.days(30)

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.RotationScheduleOptions", jsii_struct_bases=[_RotationScheduleOptions])
class RotationScheduleOptions(_RotationScheduleOptions):
    """Options to add a rotation schedule to a secret.

    Stability:
        experimental
    """
    rotationLambda: aws_cdk.aws_lambda.IFunction
    """THe Lambda function that can rotate the secret.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.RotationScheduleProps", jsii_struct_bases=[RotationScheduleOptions])
class RotationScheduleProps(RotationScheduleOptions, jsii.compat.TypedDict):
    """Construction properties for a RotationSchedule.

    Stability:
        experimental
    """
    secret: "ISecret"
    """The secret to rotate.

    Stability:
        experimental
    """

@jsii.implements(ISecret)
class Secret(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-secretsmanager.Secret"):
    """Creates a new secret in AWS SecretsManager.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, description: typing.Optional[str]=None, encryption_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, generate_secret_string: typing.Optional["SecretStringGenerator"]=None, secret_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            description: An optional, human-friendly description of the secret. Default: - No description.
            encryption_key: The customer-managed encryption key to use for encrypting the secret value. Default: - A default KMS key for the account and region is used.
            generate_secret_string: Configuration for how to generate a secret value. Default: - 32 characters with upper-case letters, lower-case letters, punctuation and numbers (at least one from each category), per the default values of ``SecretStringGenerator``.
            secret_name: A name for the secret. Note that deleting secrets from SecretsManager does not happen immediately, but after a 7 to 30 days blackout period. During that period, it is not possible to create another secret that shares the same name. Default: - A name is generated by CloudFormation.

        Stability:
            experimental
        """
        props: SecretProps = {}

        if description is not None:
            props["description"] = description

        if encryption_key is not None:
            props["encryptionKey"] = encryption_key

        if generate_secret_string is not None:
            props["generateSecretString"] = generate_secret_string

        if secret_name is not None:
            props["secretName"] = secret_name

        jsii.create(Secret, self, [scope, id, props])

    @jsii.member(jsii_name="fromSecretArn")
    @classmethod
    def from_secret_arn(cls, scope: aws_cdk.core.Construct, id: str, secret_arn: str) -> "ISecret":
        """
        Arguments:
            scope: -
            id: -
            secret_arn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromSecretArn", [scope, id, secret_arn])

    @jsii.member(jsii_name="fromSecretAttributes")
    @classmethod
    def from_secret_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, secret_arn: str, encryption_key: typing.Optional[aws_cdk.aws_kms.IKey]=None) -> "ISecret":
        """Import an existing secret into the Stack.

        Arguments:
            scope: the scope of the import.
            id: the ID of the imported Secret in the construct tree.
            attrs: the attributes of the imported secret.
            secret_arn: The ARN of the secret in SecretsManager.
            encryption_key: The encryption key that is used to encrypt the secret, unless the default SecretsManager key is used.

        Stability:
            experimental
        """
        attrs: SecretAttributes = {"secretArn": secret_arn}

        if encryption_key is not None:
            attrs["encryptionKey"] = encryption_key

        return jsii.sinvoke(cls, "fromSecretAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="addRotationSchedule")
    def add_rotation_schedule(self, id: str, *, rotation_lambda: aws_cdk.aws_lambda.IFunction, automatically_after: typing.Optional[aws_cdk.core.Duration]=None) -> "RotationSchedule":
        """Adds a rotation schedule to the secret.

        Arguments:
            id: -
            options: -
            rotation_lambda: THe Lambda function that can rotate the secret.
            automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)

        Stability:
            experimental
        """
        options: RotationScheduleOptions = {"rotationLambda": rotation_lambda}

        if automatically_after is not None:
            options["automaticallyAfter"] = automatically_after

        return jsii.invoke(self, "addRotationSchedule", [id, options])

    @jsii.member(jsii_name="addTargetAttachment")
    def add_target_attachment(self, id: str, *, target: "ISecretAttachmentTarget") -> "SecretTargetAttachment":
        """Adds a target attachment to the secret.

        Arguments:
            id: -
            options: -
            target: The target to attach the secret to.

        Returns:
            an AttachedSecret

        Stability:
            experimental
        """
        options: AttachedSecretOptions = {"target": target}

        return jsii.invoke(self, "addTargetAttachment", [id, options])

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, grantee: aws_cdk.aws_iam.IGrantable, version_stages: typing.Optional[typing.List[str]]=None) -> aws_cdk.aws_iam.Grant:
        """Grants reading the secret value to some role.

        Arguments:
            grantee: -
            version_stages: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantRead", [grantee, version_stages])

    @jsii.member(jsii_name="secretValueFromJson")
    def secret_value_from_json(self, json_field: str) -> aws_cdk.core.SecretValue:
        """Interpret the secret as a JSON object and return a field's value from it as a ``SecretValue``.

        Arguments:
            json_field: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "secretValueFromJson", [json_field])

    @property
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> str:
        """The ARN of the secret in AWS Secrets Manager.

        Stability:
            experimental
        """
        return jsii.get(self, "secretArn")

    @property
    @jsii.member(jsii_name="secretValue")
    def secret_value(self) -> aws_cdk.core.SecretValue:
        """Retrieve the value of the stored secret as a ``SecretValue``.

        Stability:
            experimental
        """
        return jsii.get(self, "secretValue")

    @property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """The customer-managed encryption key that is used to encrypt this secret, if any.

        When not specified, the default
        KMS key for the account and region is being used.

        Stability:
            experimental
        """
        return jsii.get(self, "encryptionKey")


@jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.SecretAttachmentTargetProps", jsii_struct_bases=[])
class SecretAttachmentTargetProps(jsii.compat.TypedDict):
    """Attachment target specifications.

    Stability:
        experimental
    """
    targetId: str
    """The id of the target to attach the secret to.

    Stability:
        experimental
    """

    targetType: "AttachmentTargetType"
    """The type of the target to attach the secret to.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _SecretAttributes(jsii.compat.TypedDict, total=False):
    encryptionKey: aws_cdk.aws_kms.IKey
    """The encryption key that is used to encrypt the secret, unless the default SecretsManager key is used.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.SecretAttributes", jsii_struct_bases=[_SecretAttributes])
class SecretAttributes(_SecretAttributes):
    """Attributes required to import an existing secret into the Stack.

    Stability:
        experimental
    """
    secretArn: str
    """The ARN of the secret in SecretsManager.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.SecretProps", jsii_struct_bases=[])
class SecretProps(jsii.compat.TypedDict, total=False):
    """The properties required to create a new secret in AWS Secrets Manager.

    Stability:
        experimental
    """
    description: str
    """An optional, human-friendly description of the secret.

    Default:
        - No description.

    Stability:
        experimental
    """

    encryptionKey: aws_cdk.aws_kms.IKey
    """The customer-managed encryption key to use for encrypting the secret value.

    Default:
        - A default KMS key for the account and region is used.

    Stability:
        experimental
    """

    generateSecretString: "SecretStringGenerator"
    """Configuration for how to generate a secret value.

    Default:
        - 32 characters with upper-case letters, lower-case letters, punctuation and numbers (at least one from each
          category), per the default values of ``SecretStringGenerator``.

    Stability:
        experimental
    """

    secretName: str
    """A name for the secret.

    Note that deleting secrets from SecretsManager does not happen immediately, but after a 7 to
    30 days blackout period. During that period, it is not possible to create another secret that shares the same name.

    Default:
        - A name is generated by CloudFormation.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.SecretStringGenerator", jsii_struct_bases=[])
class SecretStringGenerator(jsii.compat.TypedDict, total=False):
    """Configuration to generate secrets such as passwords automatically.

    Stability:
        experimental
    """
    excludeCharacters: str
    """A string that includes characters that shouldn't be included in the generated password.

    The string can be a minimum
    of ``0`` and a maximum of ``4096`` characters long.

    Default:
        no exclusions

    Stability:
        experimental
    """

    excludeLowercase: bool
    """Specifies that the generated password shouldn't include lowercase letters.

    Default:
        false

    Stability:
        experimental
    """

    excludeNumbers: bool
    """Specifies that the generated password shouldn't include digits.

    Default:
        false

    Stability:
        experimental
    """

    excludePunctuation: bool
    """Specifies that the generated password shouldn't include punctuation characters.

    Default:
        false

    Stability:
        experimental
    """

    excludeUppercase: bool
    """Specifies that the generated password shouldn't include uppercase letters.

    Default:
        false

    Stability:
        experimental
    """

    generateStringKey: str
    """The JSON key name that's used to add the generated password to the JSON structure specified by the ``secretStringTemplate`` parameter.

    If you specify ``generateStringKey`` then ``secretStringTemplate``
    must be also be specified.

    Stability:
        experimental
    """

    includeSpace: bool
    """Specifies that the generated password can include the space character.

    Default:
        false

    Stability:
        experimental
    """

    passwordLength: jsii.Number
    """The desired length of the generated password.

    Default:
        32

    Stability:
        experimental
    """

    requireEachIncludedType: bool
    """Specifies whether the generated password must include at least one of every allowed character type.

    Default:
        true

    Stability:
        experimental
    """

    secretStringTemplate: str
    """A properly structured JSON string that the generated password can be added to.

    The ``generateStringKey`` is
    combined with the generated random string and inserted into the JSON structure that's specified by this parameter.
    The merged JSON string is returned as the completed SecretString of the secret. If you specify ``secretStringTemplate``
    then ``generateStringKey`` must be also be specified.

    Stability:
        experimental
    """

@jsii.implements(ISecretTargetAttachment, ISecret)
class SecretTargetAttachment(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-secretsmanager.SecretTargetAttachment"):
    """An attached secret.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, secret: "ISecret", target: "ISecretAttachmentTarget") -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            secret: The secret to attach to the target.
            target: The target to attach the secret to.

        Stability:
            experimental
        """
        props: SecretTargetAttachmentProps = {"secret": secret, "target": target}

        jsii.create(SecretTargetAttachment, self, [scope, id, props])

    @jsii.member(jsii_name="fromSecretTargetAttachmentSecretArn")
    @classmethod
    def from_secret_target_attachment_secret_arn(cls, scope: aws_cdk.core.Construct, id: str, secret_target_attachment_secret_arn: str) -> "ISecretTargetAttachment":
        """
        Arguments:
            scope: -
            id: -
            secret_target_attachment_secret_arn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromSecretTargetAttachmentSecretArn", [scope, id, secret_target_attachment_secret_arn])

    @jsii.member(jsii_name="addRotationSchedule")
    def add_rotation_schedule(self, id: str, *, rotation_lambda: aws_cdk.aws_lambda.IFunction, automatically_after: typing.Optional[aws_cdk.core.Duration]=None) -> "RotationSchedule":
        """Adds a rotation schedule to the secret.

        Arguments:
            id: -
            options: -
            rotation_lambda: THe Lambda function that can rotate the secret.
            automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)

        Stability:
            experimental
        """
        options: RotationScheduleOptions = {"rotationLambda": rotation_lambda}

        if automatically_after is not None:
            options["automaticallyAfter"] = automatically_after

        return jsii.invoke(self, "addRotationSchedule", [id, options])

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, grantee: aws_cdk.aws_iam.IGrantable, version_stages: typing.Optional[typing.List[str]]=None) -> aws_cdk.aws_iam.Grant:
        """Grants reading the secret value to some role.

        Arguments:
            grantee: -
            version_stages: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantRead", [grantee, version_stages])

    @jsii.member(jsii_name="secretValueFromJson")
    def secret_value_from_json(self, json_field: str) -> aws_cdk.core.SecretValue:
        """Interpret the secret as a JSON object and return a field's value from it as a ``SecretValue``.

        Arguments:
            json_field: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "secretValueFromJson", [json_field])

    @property
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> str:
        """The ARN of the secret in AWS Secrets Manager.

        Stability:
            experimental
        """
        return jsii.get(self, "secretArn")

    @property
    @jsii.member(jsii_name="secretTargetAttachmentSecretArn")
    def secret_target_attachment_secret_arn(self) -> str:
        """Same as ``secretArn``.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "secretTargetAttachmentSecretArn")

    @property
    @jsii.member(jsii_name="secretValue")
    def secret_value(self) -> aws_cdk.core.SecretValue:
        """Retrieve the value of the stored secret as a ``SecretValue``.

        Stability:
            experimental
        """
        return jsii.get(self, "secretValue")

    @property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """The customer-managed encryption key that is used to encrypt this secret, if any.

        When not specified, the default
        KMS key for the account and region is being used.

        Stability:
            experimental
        """
        return jsii.get(self, "encryptionKey")


@jsii.data_type(jsii_type="@aws-cdk/aws-secretsmanager.SecretTargetAttachmentProps", jsii_struct_bases=[AttachedSecretOptions])
class SecretTargetAttachmentProps(AttachedSecretOptions, jsii.compat.TypedDict):
    """Construction properties for an AttachedSecret.

    Stability:
        experimental
    """
    secret: "ISecret"
    """The secret to attach to the target.

    Stability:
        experimental
    """

__all__ = ["AttachedSecretOptions", "AttachmentTargetType", "CfnResourcePolicy", "CfnResourcePolicyProps", "CfnRotationSchedule", "CfnRotationScheduleProps", "CfnSecret", "CfnSecretProps", "CfnSecretTargetAttachment", "CfnSecretTargetAttachmentProps", "ISecret", "ISecretAttachmentTarget", "ISecretTargetAttachment", "RotationSchedule", "RotationScheduleOptions", "RotationScheduleProps", "Secret", "SecretAttachmentTargetProps", "SecretAttributes", "SecretProps", "SecretStringGenerator", "SecretTargetAttachment", "SecretTargetAttachmentProps", "__jsii_assembly__"]

publication.publish()
