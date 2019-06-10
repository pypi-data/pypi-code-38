import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
import aws_cdk.region_info
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-iam", "0.34.0", __name__, "aws-iam@0.34.0.jsii.tgz")
class AwsManagedPolicy(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.AwsManagedPolicy"):
    """A policy managed by AWS.

    For this managed policy, you only need to know the name to be able to use it.

    Some managed policy names start with "service-role/", some start with
    "job-function/", and some don't start with anything. Do include the
    prefix when constructing this object.

    Stability:
        experimental
    """
    def __init__(self, managed_policy_name: str, scope: aws_cdk.cdk.IConstruct) -> None:
        """
        Arguments:
            managedPolicyName: -
            scope: -

        Stability:
            experimental
        """
        jsii.create(AwsManagedPolicy, self, [managed_policy_name, scope])

    @property
    @jsii.member(jsii_name="managedPolicyName")
    def managed_policy_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "managedPolicyName")

    @property
    @jsii.member(jsii_name="policyArn")
    def policy_arn(self) -> str:
        """The Arn of this managed policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyArn")

    @property
    @jsii.member(jsii_name="scope")
    def scope(self) -> aws_cdk.cdk.IConstruct:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "scope")


class CfnAccessKey(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.CfnAccessKey"):
    """A CloudFormation ``AWS::IAM::AccessKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-accesskey.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IAM::AccessKey
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, user_name: str, serial: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, status: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IAM::AccessKey``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            userName: ``AWS::IAM::AccessKey.UserName``.
            serial: ``AWS::IAM::AccessKey.Serial``.
            status: ``AWS::IAM::AccessKey.Status``.

        Stability:
            experimental
        """
        props: CfnAccessKeyProps = {"userName": user_name}

        if serial is not None:
            props["serial"] = serial

        if status is not None:
            props["status"] = status

        jsii.create(CfnAccessKey, self, [scope, id, props])

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
    @jsii.member(jsii_name="accessKeyId")
    def access_key_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "accessKeyId")

    @property
    @jsii.member(jsii_name="accessKeySecretAccessKey")
    def access_key_secret_access_key(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            SecretAccessKey
        """
        return jsii.get(self, "accessKeySecretAccessKey")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnAccessKeyProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAccessKeyProps(jsii.compat.TypedDict, total=False):
    serial: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::IAM::AccessKey.Serial``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-accesskey.html#cfn-iam-accesskey-serial
    Stability:
        experimental
    """
    status: str
    """``AWS::IAM::AccessKey.Status``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-accesskey.html#cfn-iam-accesskey-status
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnAccessKeyProps", jsii_struct_bases=[_CfnAccessKeyProps])
class CfnAccessKeyProps(_CfnAccessKeyProps):
    """Properties for defining a ``AWS::IAM::AccessKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-accesskey.html
    Stability:
        experimental
    """
    userName: str
    """``AWS::IAM::AccessKey.UserName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-accesskey.html#cfn-iam-accesskey-username
    Stability:
        experimental
    """

class CfnGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.CfnGroup"):
    """A CloudFormation ``AWS::IAM::Group``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-group.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IAM::Group
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, group_name: typing.Optional[str]=None, managed_policy_arns: typing.Optional[typing.List[str]]=None, path: typing.Optional[str]=None, policies: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "PolicyProperty"]]]]]=None) -> None:
        """Create a new ``AWS::IAM::Group``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            groupName: ``AWS::IAM::Group.GroupName``.
            managedPolicyArns: ``AWS::IAM::Group.ManagedPolicyArns``.
            path: ``AWS::IAM::Group.Path``.
            policies: ``AWS::IAM::Group.Policies``.

        Stability:
            experimental
        """
        props: CfnGroupProps = {}

        if group_name is not None:
            props["groupName"] = group_name

        if managed_policy_arns is not None:
            props["managedPolicyArns"] = managed_policy_arns

        if path is not None:
            props["path"] = path

        if policies is not None:
            props["policies"] = policies

        jsii.create(CfnGroup, self, [scope, id, props])

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
    @jsii.member(jsii_name="groupArn")
    def group_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "groupArn")

    @property
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "groupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnGroup.PolicyProperty", jsii_struct_bases=[])
    class PolicyProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-policy.html
        Stability:
            experimental
        """
        policyDocument: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnGroup.PolicyProperty.PolicyDocument``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-policy.html#cfn-iam-policies-policydocument
        Stability:
            experimental
        """

        policyName: str
        """``CfnGroup.PolicyProperty.PolicyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-policy.html#cfn-iam-policies-policyname
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnGroupProps", jsii_struct_bases=[])
class CfnGroupProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::IAM::Group``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-group.html
    Stability:
        experimental
    """
    groupName: str
    """``AWS::IAM::Group.GroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-group.html#cfn-iam-group-groupname
    Stability:
        experimental
    """

    managedPolicyArns: typing.List[str]
    """``AWS::IAM::Group.ManagedPolicyArns``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-group.html#cfn-iam-group-managepolicyarns
    Stability:
        experimental
    """

    path: str
    """``AWS::IAM::Group.Path``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-group.html#cfn-iam-group-path
    Stability:
        experimental
    """

    policies: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnGroup.PolicyProperty"]]]
    """``AWS::IAM::Group.Policies``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-group.html#cfn-iam-group-policies
    Stability:
        experimental
    """

class CfnInstanceProfile(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.CfnInstanceProfile"):
    """A CloudFormation ``AWS::IAM::InstanceProfile``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-instanceprofile.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IAM::InstanceProfile
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, roles: typing.List[str], instance_profile_name: typing.Optional[str]=None, path: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IAM::InstanceProfile``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            roles: ``AWS::IAM::InstanceProfile.Roles``.
            instanceProfileName: ``AWS::IAM::InstanceProfile.InstanceProfileName``.
            path: ``AWS::IAM::InstanceProfile.Path``.

        Stability:
            experimental
        """
        props: CfnInstanceProfileProps = {"roles": roles}

        if instance_profile_name is not None:
            props["instanceProfileName"] = instance_profile_name

        if path is not None:
            props["path"] = path

        jsii.create(CfnInstanceProfile, self, [scope, id, props])

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
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "instanceProfileArn")

    @property
    @jsii.member(jsii_name="instanceProfileName")
    def instance_profile_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "instanceProfileName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnInstanceProfileProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnInstanceProfileProps(jsii.compat.TypedDict, total=False):
    instanceProfileName: str
    """``AWS::IAM::InstanceProfile.InstanceProfileName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-instanceprofile.html#cfn-iam-instanceprofile-instanceprofilename
    Stability:
        experimental
    """
    path: str
    """``AWS::IAM::InstanceProfile.Path``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-instanceprofile.html#cfn-iam-instanceprofile-path
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnInstanceProfileProps", jsii_struct_bases=[_CfnInstanceProfileProps])
class CfnInstanceProfileProps(_CfnInstanceProfileProps):
    """Properties for defining a ``AWS::IAM::InstanceProfile``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-instanceprofile.html
    Stability:
        experimental
    """
    roles: typing.List[str]
    """``AWS::IAM::InstanceProfile.Roles``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-instanceprofile.html#cfn-iam-instanceprofile-roles
    Stability:
        experimental
    """

class CfnManagedPolicy(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.CfnManagedPolicy"):
    """A CloudFormation ``AWS::IAM::ManagedPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-managedpolicy.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IAM::ManagedPolicy
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, policy_document: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token], description: typing.Optional[str]=None, groups: typing.Optional[typing.List[str]]=None, managed_policy_name: typing.Optional[str]=None, path: typing.Optional[str]=None, roles: typing.Optional[typing.List[str]]=None, users: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::IAM::ManagedPolicy``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            policyDocument: ``AWS::IAM::ManagedPolicy.PolicyDocument``.
            description: ``AWS::IAM::ManagedPolicy.Description``.
            groups: ``AWS::IAM::ManagedPolicy.Groups``.
            managedPolicyName: ``AWS::IAM::ManagedPolicy.ManagedPolicyName``.
            path: ``AWS::IAM::ManagedPolicy.Path``.
            roles: ``AWS::IAM::ManagedPolicy.Roles``.
            users: ``AWS::IAM::ManagedPolicy.Users``.

        Stability:
            experimental
        """
        props: CfnManagedPolicyProps = {"policyDocument": policy_document}

        if description is not None:
            props["description"] = description

        if groups is not None:
            props["groups"] = groups

        if managed_policy_name is not None:
            props["managedPolicyName"] = managed_policy_name

        if path is not None:
            props["path"] = path

        if roles is not None:
            props["roles"] = roles

        if users is not None:
            props["users"] = users

        jsii.create(CfnManagedPolicy, self, [scope, id, props])

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
    @jsii.member(jsii_name="managedPolicyArn")
    def managed_policy_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "managedPolicyArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnManagedPolicyProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnManagedPolicyProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::IAM::ManagedPolicy.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-managedpolicy.html#cfn-iam-managedpolicy-description
    Stability:
        experimental
    """
    groups: typing.List[str]
    """``AWS::IAM::ManagedPolicy.Groups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-managedpolicy.html#cfn-iam-managedpolicy-groups
    Stability:
        experimental
    """
    managedPolicyName: str
    """``AWS::IAM::ManagedPolicy.ManagedPolicyName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-managedpolicy.html#cfn-iam-managedpolicy-managedpolicyname
    Stability:
        experimental
    """
    path: str
    """``AWS::IAM::ManagedPolicy.Path``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-managedpolicy.html#cfn-ec2-dhcpoptions-path
    Stability:
        experimental
    """
    roles: typing.List[str]
    """``AWS::IAM::ManagedPolicy.Roles``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-managedpolicy.html#cfn-iam-managedpolicy-roles
    Stability:
        experimental
    """
    users: typing.List[str]
    """``AWS::IAM::ManagedPolicy.Users``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-managedpolicy.html#cfn-iam-managedpolicy-users
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnManagedPolicyProps", jsii_struct_bases=[_CfnManagedPolicyProps])
class CfnManagedPolicyProps(_CfnManagedPolicyProps):
    """Properties for defining a ``AWS::IAM::ManagedPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-managedpolicy.html
    Stability:
        experimental
    """
    policyDocument: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::IAM::ManagedPolicy.PolicyDocument``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-managedpolicy.html#cfn-iam-managedpolicy-policydocument
    Stability:
        experimental
    """

class CfnPolicy(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.CfnPolicy"):
    """A CloudFormation ``AWS::IAM::Policy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-policy.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IAM::Policy
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, policy_document: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token], policy_name: str, groups: typing.Optional[typing.List[str]]=None, roles: typing.Optional[typing.List[str]]=None, users: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::IAM::Policy``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            policyDocument: ``AWS::IAM::Policy.PolicyDocument``.
            policyName: ``AWS::IAM::Policy.PolicyName``.
            groups: ``AWS::IAM::Policy.Groups``.
            roles: ``AWS::IAM::Policy.Roles``.
            users: ``AWS::IAM::Policy.Users``.

        Stability:
            experimental
        """
        props: CfnPolicyProps = {"policyDocument": policy_document, "policyName": policy_name}

        if groups is not None:
            props["groups"] = groups

        if roles is not None:
            props["roles"] = roles

        if users is not None:
            props["users"] = users

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


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPolicyProps(jsii.compat.TypedDict, total=False):
    groups: typing.List[str]
    """``AWS::IAM::Policy.Groups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-policy.html#cfn-iam-policy-groups
    Stability:
        experimental
    """
    roles: typing.List[str]
    """``AWS::IAM::Policy.Roles``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-policy.html#cfn-iam-policy-roles
    Stability:
        experimental
    """
    users: typing.List[str]
    """``AWS::IAM::Policy.Users``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-policy.html#cfn-iam-policy-users
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnPolicyProps", jsii_struct_bases=[_CfnPolicyProps])
class CfnPolicyProps(_CfnPolicyProps):
    """Properties for defining a ``AWS::IAM::Policy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-policy.html
    Stability:
        experimental
    """
    policyDocument: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::IAM::Policy.PolicyDocument``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-policy.html#cfn-iam-policy-policydocument
    Stability:
        experimental
    """

    policyName: str
    """``AWS::IAM::Policy.PolicyName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-policy.html#cfn-iam-policy-policyname
    Stability:
        experimental
    """

class CfnRole(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.CfnRole"):
    """A CloudFormation ``AWS::IAM::Role``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IAM::Role
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, assume_role_policy_document: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token], managed_policy_arns: typing.Optional[typing.List[str]]=None, max_session_duration: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, path: typing.Optional[str]=None, permissions_boundary: typing.Optional[str]=None, policies: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "PolicyProperty"]]]]]=None, role_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IAM::Role``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            assumeRolePolicyDocument: ``AWS::IAM::Role.AssumeRolePolicyDocument``.
            managedPolicyArns: ``AWS::IAM::Role.ManagedPolicyArns``.
            maxSessionDuration: ``AWS::IAM::Role.MaxSessionDuration``.
            path: ``AWS::IAM::Role.Path``.
            permissionsBoundary: ``AWS::IAM::Role.PermissionsBoundary``.
            policies: ``AWS::IAM::Role.Policies``.
            roleName: ``AWS::IAM::Role.RoleName``.

        Stability:
            experimental
        """
        props: CfnRoleProps = {"assumeRolePolicyDocument": assume_role_policy_document}

        if managed_policy_arns is not None:
            props["managedPolicyArns"] = managed_policy_arns

        if max_session_duration is not None:
            props["maxSessionDuration"] = max_session_duration

        if path is not None:
            props["path"] = path

        if permissions_boundary is not None:
            props["permissionsBoundary"] = permissions_boundary

        if policies is not None:
            props["policies"] = policies

        if role_name is not None:
            props["roleName"] = role_name

        jsii.create(CfnRole, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnRoleProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "roleArn")

    @property
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RoleId
        """
        return jsii.get(self, "roleId")

    @property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "roleName")

    @jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnRole.PolicyProperty", jsii_struct_bases=[])
    class PolicyProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-policy.html
        Stability:
            experimental
        """
        policyDocument: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnRole.PolicyProperty.PolicyDocument``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-policy.html#cfn-iam-policies-policydocument
        Stability:
            experimental
        """

        policyName: str
        """``CfnRole.PolicyProperty.PolicyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-policy.html#cfn-iam-policies-policyname
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRoleProps(jsii.compat.TypedDict, total=False):
    managedPolicyArns: typing.List[str]
    """``AWS::IAM::Role.ManagedPolicyArns``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html#cfn-iam-role-managepolicyarns
    Stability:
        experimental
    """
    maxSessionDuration: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::IAM::Role.MaxSessionDuration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html#cfn-iam-role-maxsessionduration
    Stability:
        experimental
    """
    path: str
    """``AWS::IAM::Role.Path``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html#cfn-iam-role-path
    Stability:
        experimental
    """
    permissionsBoundary: str
    """``AWS::IAM::Role.PermissionsBoundary``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html#cfn-iam-role-permissionsboundary
    Stability:
        experimental
    """
    policies: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnRole.PolicyProperty"]]]
    """``AWS::IAM::Role.Policies``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html#cfn-iam-role-policies
    Stability:
        experimental
    """
    roleName: str
    """``AWS::IAM::Role.RoleName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html#cfn-iam-role-rolename
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnRoleProps", jsii_struct_bases=[_CfnRoleProps])
class CfnRoleProps(_CfnRoleProps):
    """Properties for defining a ``AWS::IAM::Role``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html
    Stability:
        experimental
    """
    assumeRolePolicyDocument: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::IAM::Role.AssumeRolePolicyDocument``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html#cfn-iam-role-assumerolepolicydocument
    Stability:
        experimental
    """

class CfnServiceLinkedRole(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.CfnServiceLinkedRole"):
    """A CloudFormation ``AWS::IAM::ServiceLinkedRole``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-servicelinkedrole.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IAM::ServiceLinkedRole
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, aws_service_name: str, custom_suffix: typing.Optional[str]=None, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IAM::ServiceLinkedRole``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            awsServiceName: ``AWS::IAM::ServiceLinkedRole.AWSServiceName``.
            customSuffix: ``AWS::IAM::ServiceLinkedRole.CustomSuffix``.
            description: ``AWS::IAM::ServiceLinkedRole.Description``.

        Stability:
            experimental
        """
        props: CfnServiceLinkedRoleProps = {"awsServiceName": aws_service_name}

        if custom_suffix is not None:
            props["customSuffix"] = custom_suffix

        if description is not None:
            props["description"] = description

        jsii.create(CfnServiceLinkedRole, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnServiceLinkedRoleProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnServiceLinkedRoleProps(jsii.compat.TypedDict, total=False):
    customSuffix: str
    """``AWS::IAM::ServiceLinkedRole.CustomSuffix``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-servicelinkedrole.html#cfn-iam-servicelinkedrole-customsuffix
    Stability:
        experimental
    """
    description: str
    """``AWS::IAM::ServiceLinkedRole.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-servicelinkedrole.html#cfn-iam-servicelinkedrole-description
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnServiceLinkedRoleProps", jsii_struct_bases=[_CfnServiceLinkedRoleProps])
class CfnServiceLinkedRoleProps(_CfnServiceLinkedRoleProps):
    """Properties for defining a ``AWS::IAM::ServiceLinkedRole``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-servicelinkedrole.html
    Stability:
        experimental
    """
    awsServiceName: str
    """``AWS::IAM::ServiceLinkedRole.AWSServiceName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-servicelinkedrole.html#cfn-iam-servicelinkedrole-awsservicename
    Stability:
        experimental
    """

class CfnUser(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.CfnUser"):
    """A CloudFormation ``AWS::IAM::User``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-user.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IAM::User
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, groups: typing.Optional[typing.List[str]]=None, login_profile: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["LoginProfileProperty"]]]=None, managed_policy_arns: typing.Optional[typing.List[str]]=None, path: typing.Optional[str]=None, permissions_boundary: typing.Optional[str]=None, policies: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "PolicyProperty"]]]]]=None, user_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IAM::User``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            groups: ``AWS::IAM::User.Groups``.
            loginProfile: ``AWS::IAM::User.LoginProfile``.
            managedPolicyArns: ``AWS::IAM::User.ManagedPolicyArns``.
            path: ``AWS::IAM::User.Path``.
            permissionsBoundary: ``AWS::IAM::User.PermissionsBoundary``.
            policies: ``AWS::IAM::User.Policies``.
            userName: ``AWS::IAM::User.UserName``.

        Stability:
            experimental
        """
        props: CfnUserProps = {}

        if groups is not None:
            props["groups"] = groups

        if login_profile is not None:
            props["loginProfile"] = login_profile

        if managed_policy_arns is not None:
            props["managedPolicyArns"] = managed_policy_arns

        if path is not None:
            props["path"] = path

        if permissions_boundary is not None:
            props["permissionsBoundary"] = permissions_boundary

        if policies is not None:
            props["policies"] = policies

        if user_name is not None:
            props["userName"] = user_name

        jsii.create(CfnUser, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnUserProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="userArn")
    def user_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "userArn")

    @property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "userName")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LoginProfileProperty(jsii.compat.TypedDict, total=False):
        passwordResetRequired: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnUser.LoginProfileProperty.PasswordResetRequired``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-user-loginprofile.html#cfn-iam-user-loginprofile-passwordresetrequired
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnUser.LoginProfileProperty", jsii_struct_bases=[_LoginProfileProperty])
    class LoginProfileProperty(_LoginProfileProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-user-loginprofile.html
        Stability:
            experimental
        """
        password: str
        """``CfnUser.LoginProfileProperty.Password``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-user-loginprofile.html#cfn-iam-user-loginprofile-password
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnUser.PolicyProperty", jsii_struct_bases=[])
    class PolicyProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-policy.html
        Stability:
            experimental
        """
        policyDocument: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnUser.PolicyProperty.PolicyDocument``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-policy.html#cfn-iam-policies-policydocument
        Stability:
            experimental
        """

        policyName: str
        """``CfnUser.PolicyProperty.PolicyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-policy.html#cfn-iam-policies-policyname
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnUserProps", jsii_struct_bases=[])
class CfnUserProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::IAM::User``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-user.html
    Stability:
        experimental
    """
    groups: typing.List[str]
    """``AWS::IAM::User.Groups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-user.html#cfn-iam-user-groups
    Stability:
        experimental
    """

    loginProfile: typing.Union[aws_cdk.cdk.Token, "CfnUser.LoginProfileProperty"]
    """``AWS::IAM::User.LoginProfile``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-user.html#cfn-iam-user-loginprofile
    Stability:
        experimental
    """

    managedPolicyArns: typing.List[str]
    """``AWS::IAM::User.ManagedPolicyArns``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-user.html#cfn-iam-user-managepolicyarns
    Stability:
        experimental
    """

    path: str
    """``AWS::IAM::User.Path``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-user.html#cfn-iam-user-path
    Stability:
        experimental
    """

    permissionsBoundary: str
    """``AWS::IAM::User.PermissionsBoundary``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-user.html#cfn-iam-user-permissionsboundary
    Stability:
        experimental
    """

    policies: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnUser.PolicyProperty"]]]
    """``AWS::IAM::User.Policies``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-user.html#cfn-iam-user-policies
    Stability:
        experimental
    """

    userName: str
    """``AWS::IAM::User.UserName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-user.html#cfn-iam-user-username
    Stability:
        experimental
    """

class CfnUserToGroupAddition(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.CfnUserToGroupAddition"):
    """A CloudFormation ``AWS::IAM::UserToGroupAddition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-addusertogroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IAM::UserToGroupAddition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, group_name: str, users: typing.List[str]) -> None:
        """Create a new ``AWS::IAM::UserToGroupAddition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            groupName: ``AWS::IAM::UserToGroupAddition.GroupName``.
            users: ``AWS::IAM::UserToGroupAddition.Users``.

        Stability:
            experimental
        """
        props: CfnUserToGroupAdditionProps = {"groupName": group_name, "users": users}

        jsii.create(CfnUserToGroupAddition, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnUserToGroupAdditionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-iam.CfnUserToGroupAdditionProps", jsii_struct_bases=[])
class CfnUserToGroupAdditionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::IAM::UserToGroupAddition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-addusertogroup.html
    Stability:
        experimental
    """
    groupName: str
    """``AWS::IAM::UserToGroupAddition.GroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-addusertogroup.html#cfn-iam-addusertogroup-groupname
    Stability:
        experimental
    """

    users: typing.List[str]
    """``AWS::IAM::UserToGroupAddition.Users``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-addusertogroup.html#cfn-iam-addusertogroup-users
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.CommonGrantOptions", jsii_struct_bases=[])
class CommonGrantOptions(jsii.compat.TypedDict):
    """Basic options for a grant operation.

    Stability:
        experimental
    """
    actions: typing.List[str]
    """The actions to grant.

    Stability:
        experimental
    """

    grantee: "IGrantable"
    """The principal to grant to.

    Default:
        if principal is undefined, no work is done.

    Stability:
        experimental
    """

    resourceArns: typing.List[str]
    """The resource ARNs to grant to.

    Stability:
        experimental
    """

class Grant(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.Grant"):
    """Result of a grant() operation.

    This class is not instantiable by consumers on purpose, so that they will be
    required to call the Grant factory functions.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="addToPrincipal")
    @classmethod
    def add_to_principal(cls, *, scope: typing.Optional[aws_cdk.cdk.IConstruct]=None, actions: typing.List[str], grantee: "IGrantable", resource_arns: typing.List[str]) -> "Grant":
        """Try to grant the given permissions to the given principal.

        Absence of a principal leads to a warning, but failing to add
        the permissions to a present principal is not an error.

        Arguments:
            options: -
            scope: Construct to report warnings on in case grant could not be registered.
            actions: The actions to grant.
            grantee: The principal to grant to. Default: if principal is undefined, no work is done.
            resourceArns: The resource ARNs to grant to.

        Stability:
            experimental
        """
        options: GrantOnPrincipalOptions = {"actions": actions, "grantee": grantee, "resourceArns": resource_arns}

        if scope is not None:
            options["scope"] = scope

        return jsii.sinvoke(cls, "addToPrincipal", [options])

    @jsii.member(jsii_name="addToPrincipalAndResource")
    @classmethod
    def add_to_principal_and_resource(cls, *, resource: "IResourceWithPolicy", resource_self_arns: typing.Optional[typing.List[str]]=None, actions: typing.List[str], grantee: "IGrantable", resource_arns: typing.List[str]) -> "Grant":
        """Add a grant both on the principal and on the resource.

        As long as any principal is given, granting on the pricipal may fail (in
        case of a non-identity principal), but granting on the resource will
        never fail.

        Statement will be the resource statement.

        Arguments:
            options: -
            resource: The resource with a resource policy. The statement will always be added to the resource policy.
            resourceSelfArns: When referring to the resource in a resource policy, use this as ARN. (Depending on the resource type, this needs to be '*' in a resource policy). Default: Same as regular resource ARNs
            actions: The actions to grant.
            grantee: The principal to grant to. Default: if principal is undefined, no work is done.
            resourceArns: The resource ARNs to grant to.

        Stability:
            experimental
        """
        options: GrantOnPrincipalAndResourceOptions = {"resource": resource, "actions": actions, "grantee": grantee, "resourceArns": resource_arns}

        if resource_self_arns is not None:
            options["resourceSelfArns"] = resource_self_arns

        return jsii.sinvoke(cls, "addToPrincipalAndResource", [options])

    @jsii.member(jsii_name="addToPrincipalOrResource")
    @classmethod
    def add_to_principal_or_resource(cls, *, resource: "IResourceWithPolicy", resource_self_arns: typing.Optional[typing.List[str]]=None, actions: typing.List[str], grantee: "IGrantable", resource_arns: typing.List[str]) -> "Grant":
        """Grant the given permissions to the principal.

        The permissions will be added to the principal policy primarily, falling
        back to the resource policy if necessary. The permissions must be granted
        somewhere.

        - Trying to grant permissions to a principal that does not admit adding to
          the principal policy while not providing a resource with a resource policy
          is an error.
        - Trying to grant permissions to an absent principal (possible in the
          case of imported resources) leads to a warning being added to the
          resource construct.

        Arguments:
            options: -
            resource: The resource with a resource policy. The statement will be added to the resource policy if it couldn't be added to the principal policy.
            resourceSelfArns: When referring to the resource in a resource policy, use this as ARN. (Depending on the resource type, this needs to be '*' in a resource policy). Default: Same as regular resource ARNs
            actions: The actions to grant.
            grantee: The principal to grant to. Default: if principal is undefined, no work is done.
            resourceArns: The resource ARNs to grant to.

        Stability:
            experimental
        """
        options: GrantWithResourceOptions = {"resource": resource, "actions": actions, "grantee": grantee, "resourceArns": resource_arns}

        if resource_self_arns is not None:
            options["resourceSelfArns"] = resource_self_arns

        return jsii.sinvoke(cls, "addToPrincipalOrResource", [options])

    @jsii.member(jsii_name="drop")
    @classmethod
    def drop(cls, grantee: "IGrantable", _intent: str) -> "Grant":
        """Returns a "no-op" ``Grant`` object which represents a "dropped grant".

        This can be used for e.g. imported resources where you may not be able to modify
        the resource's policy or some underlying policy which you don't know about.

        Arguments:
            grantee: The intended grantee.
            _intent: The user's intent (will be ignored at the moment).

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "drop", [grantee, _intent])

    @jsii.member(jsii_name="assertSuccess")
    def assert_success(self) -> None:
        """Throw an error if this grant wasn't successful.

        Stability:
            experimental
        """
        return jsii.invoke(self, "assertSuccess", [])

    @property
    @jsii.member(jsii_name="success")
    def success(self) -> bool:
        """Whether the grant operation was successful.

        Stability:
            experimental
        """
        return jsii.get(self, "success")

    @property
    @jsii.member(jsii_name="principalStatement")
    def principal_statement(self) -> typing.Optional["PolicyStatement"]:
        """The statement that was added to the principal's policy.

        Can be accessed to (e.g.) add additional conditions to the statement.

        Stability:
            experimental
        """
        return jsii.get(self, "principalStatement")

    @property
    @jsii.member(jsii_name="resourceStatement")
    def resource_statement(self) -> typing.Optional["PolicyStatement"]:
        """The statement that was added to the resource policy.

        Can be accessed to (e.g.) add additional conditions to the statement.

        Stability:
            experimental
        """
        return jsii.get(self, "resourceStatement")


@jsii.data_type_optionals(jsii_struct_bases=[CommonGrantOptions])
class _GrantOnPrincipalAndResourceOptions(CommonGrantOptions, jsii.compat.TypedDict, total=False):
    resourceSelfArns: typing.List[str]
    """When referring to the resource in a resource policy, use this as ARN.

    (Depending on the resource type, this needs to be '*' in a resource policy).

    Default:
        Same as regular resource ARNs

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.GrantOnPrincipalAndResourceOptions", jsii_struct_bases=[_GrantOnPrincipalAndResourceOptions])
class GrantOnPrincipalAndResourceOptions(_GrantOnPrincipalAndResourceOptions):
    """Options for a grant operation to both identity and resource.

    Stability:
        experimental
    """
    resource: "IResourceWithPolicy"
    """The resource with a resource policy.

    The statement will always be added to the resource policy.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.GrantOnPrincipalOptions", jsii_struct_bases=[CommonGrantOptions])
class GrantOnPrincipalOptions(CommonGrantOptions, jsii.compat.TypedDict, total=False):
    """Options for a grant operation that only applies to principals.

    Stability:
        experimental
    """
    scope: aws_cdk.cdk.IConstruct
    """Construct to report warnings on in case grant could not be registered.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[CommonGrantOptions])
class _GrantWithResourceOptions(CommonGrantOptions, jsii.compat.TypedDict, total=False):
    resourceSelfArns: typing.List[str]
    """When referring to the resource in a resource policy, use this as ARN.

    (Depending on the resource type, this needs to be '*' in a resource policy).

    Default:
        Same as regular resource ARNs

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.GrantWithResourceOptions", jsii_struct_bases=[_GrantWithResourceOptions])
class GrantWithResourceOptions(_GrantWithResourceOptions):
    """Options for a grant operation.

    Stability:
        experimental
    """
    resource: "IResourceWithPolicy"
    """The resource with a resource policy.

    The statement will be added to the resource policy if it couldn't be
    added to the principal policy.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.GroupProps", jsii_struct_bases=[])
class GroupProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    groupName: str
    """A name for the IAM group.

    For valid values, see the GroupName parameter
    for the CreateGroup action in the IAM API Reference. If you don't specify
    a name, AWS CloudFormation generates a unique physical ID and uses that
    ID for the group name.

    If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to
    acknowledge your template's capabilities. For more information, see
    Acknowledging IAM Resources in AWS CloudFormation Templates.

    Default:
        Generated by CloudFormation (recommended)

    Stability:
        experimental
    """

    managedPolicyArns: typing.List[typing.Any]
    """A list of ARNs for managed policies associated with group.

    Default:
        - No managed policies.

    Stability:
        experimental
    """

    path: str
    """The path to the group.

    For more information about paths, see `IAM
    Identifiers <http://docs.aws.amazon.com/IAM/latest/UserGuide/index.html?Using_Identifiers.html>`_
    in the IAM User Guide.

    Default:
        /

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-iam.IGrantable")
class IGrantable(jsii.compat.Protocol):
    """Any object that has an associated principal that a permission can be granted to.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IGrantableProxy

    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> "IPrincipal":
        """The principal to grant permissions to.

        Stability:
            experimental
        """
        ...


class _IGrantableProxy():
    """Any object that has an associated principal that a permission can be granted to.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-iam.IGrantable"
    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> "IPrincipal":
        """The principal to grant permissions to.

        Stability:
            experimental
        """
        return jsii.get(self, "grantPrincipal")


@jsii.interface(jsii_type="@aws-cdk/aws-iam.IPolicy")
class IPolicy(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IPolicyProxy

    @property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IPolicyProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-iam.IPolicy"
    @property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "policyName")


@jsii.interface(jsii_type="@aws-cdk/aws-iam.IPrincipal")
class IPrincipal(IGrantable, jsii.compat.Protocol):
    """Represents a logical IAM principal.

    An IPrincipal describes a logical entity that can perform AWS API calls
    against sets of resources, optionally under certain conditions.

    Examples of simple principals are IAM objects that you create, such
    as Users or Roles.

    An example of a more complex principals is a ``ServicePrincipal`` (such as
    ``new ServicePrincipal("sns.amazonaws.com")``, which represents the Simple
    Notifications Service).

    A single logical Principal may also map to a set of physical principals.
    For example, ``new OrganizationPrincipal('o-1234')`` represents all
    identities that are part of the given AWS Organization.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IPrincipalProxy

    @property
    @jsii.member(jsii_name="assumeRoleAction")
    def assume_role_action(self) -> str:
        """When this Principal is used in an AssumeRole policy, the action to use.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addToPolicy")
    def add_to_policy(self, statement: "PolicyStatement") -> bool:
        """Add to the policy of this principal.

        Arguments:
            statement: -

        Returns:
            true if the statement was added, false if the principal in
            question does not have a policy document to add the statement to.

        Stability:
            experimental
        """
        ...


class _IPrincipalProxy(jsii.proxy_for(IGrantable)):
    """Represents a logical IAM principal.

    An IPrincipal describes a logical entity that can perform AWS API calls
    against sets of resources, optionally under certain conditions.

    Examples of simple principals are IAM objects that you create, such
    as Users or Roles.

    An example of a more complex principals is a ``ServicePrincipal`` (such as
    ``new ServicePrincipal("sns.amazonaws.com")``, which represents the Simple
    Notifications Service).

    A single logical Principal may also map to a set of physical principals.
    For example, ``new OrganizationPrincipal('o-1234')`` represents all
    identities that are part of the given AWS Organization.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-iam.IPrincipal"
    @property
    @jsii.member(jsii_name="assumeRoleAction")
    def assume_role_action(self) -> str:
        """When this Principal is used in an AssumeRole policy, the action to use.

        Stability:
            experimental
        """
        return jsii.get(self, "assumeRoleAction")

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")

    @jsii.member(jsii_name="addToPolicy")
    def add_to_policy(self, statement: "PolicyStatement") -> bool:
        """Add to the policy of this principal.

        Arguments:
            statement: -

        Returns:
            true if the statement was added, false if the principal in
            question does not have a policy document to add the statement to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToPolicy", [statement])


@jsii.interface(jsii_type="@aws-cdk/aws-iam.IIdentity")
class IIdentity(IPrincipal, aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """A construct that represents an IAM principal, such as a user, group or role.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IIdentityProxy

    @jsii.member(jsii_name="attachInlinePolicy")
    def attach_inline_policy(self, policy: "Policy") -> None:
        """Attaches an inline policy to this principal. This is the same as calling ``policy.addToXxx(principal)``.

        Arguments:
            policy: The policy resource to attach to this principal [disable-awslint:ref-via-interface].

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="attachManagedPolicy")
    def attach_managed_policy(self, arn: str) -> None:
        """Attaches a managed policy to this principal.

        Arguments:
            arn: The ARN of the managed policy.

        Stability:
            experimental
        """
        ...


class _IIdentityProxy(jsii.proxy_for(IPrincipal), jsii.proxy_for(aws_cdk.cdk.IResource)):
    """A construct that represents an IAM principal, such as a user, group or role.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-iam.IIdentity"
    @jsii.member(jsii_name="attachInlinePolicy")
    def attach_inline_policy(self, policy: "Policy") -> None:
        """Attaches an inline policy to this principal. This is the same as calling ``policy.addToXxx(principal)``.

        Arguments:
            policy: The policy resource to attach to this principal [disable-awslint:ref-via-interface].

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachInlinePolicy", [policy])

    @jsii.member(jsii_name="attachManagedPolicy")
    def attach_managed_policy(self, arn: str) -> None:
        """Attaches a managed policy to this principal.

        Arguments:
            arn: The ARN of the managed policy.

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachManagedPolicy", [arn])


@jsii.interface(jsii_type="@aws-cdk/aws-iam.IGroup")
class IGroup(IIdentity, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IGroupProxy

    @property
    @jsii.member(jsii_name="groupArn")
    def group_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IGroupProxy(jsii.proxy_for(IIdentity)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-iam.IGroup"
    @property
    @jsii.member(jsii_name="groupArn")
    def group_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "groupArn")

    @property
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "groupName")


@jsii.implements(IGroup)
class Group(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.Group"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, group_name: typing.Optional[str]=None, managed_policy_arns: typing.Optional[typing.List[typing.Any]]=None, path: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            groupName: A name for the IAM group. For valid values, see the GroupName parameter for the CreateGroup action in the IAM API Reference. If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the group name. If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to acknowledge your template's capabilities. For more information, see Acknowledging IAM Resources in AWS CloudFormation Templates. Default: Generated by CloudFormation (recommended)
            managedPolicyArns: A list of ARNs for managed policies associated with group. Default: - No managed policies.
            path: The path to the group. For more information about paths, see `IAM Identifiers <http://docs.aws.amazon.com/IAM/latest/UserGuide/index.html?Using_Identifiers.html>`_ in the IAM User Guide. Default: /

        Stability:
            experimental
        """
        props: GroupProps = {}

        if group_name is not None:
            props["groupName"] = group_name

        if managed_policy_arns is not None:
            props["managedPolicyArns"] = managed_policy_arns

        if path is not None:
            props["path"] = path

        jsii.create(Group, self, [scope, id, props])

    @jsii.member(jsii_name="fromGroupArn")
    @classmethod
    def from_group_arn(cls, scope: aws_cdk.cdk.Construct, id: str, group_arn: str) -> "IGroup":
        """Imports a group from ARN.

        Arguments:
            scope: -
            id: -
            groupArn: (e.g. ``arn:aws:iam::account-id:group/group-name``).

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromGroupArn", [scope, id, group_arn])

    @jsii.member(jsii_name="addToPolicy")
    def add_to_policy(self, statement: "PolicyStatement") -> bool:
        """Adds an IAM statement to the default policy.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToPolicy", [statement])

    @jsii.member(jsii_name="addUser")
    def add_user(self, user: "IUser") -> None:
        """Adds a user to this group.

        Arguments:
            user: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addUser", [user])

    @jsii.member(jsii_name="attachInlinePolicy")
    def attach_inline_policy(self, policy: "Policy") -> None:
        """Attaches a policy to this group.

        Arguments:
            policy: The policy to attach.

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachInlinePolicy", [policy])

    @jsii.member(jsii_name="attachManagedPolicy")
    def attach_managed_policy(self, arn: str) -> None:
        """Attaches a managed policy to this group.

        Arguments:
            arn: The ARN of the managed policy to attach.

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachManagedPolicy", [arn])

    @property
    @jsii.member(jsii_name="assumeRoleAction")
    def assume_role_action(self) -> str:
        """When this Principal is used in an AssumeRole policy, the action to use.

        Stability:
            experimental
        """
        return jsii.get(self, "assumeRoleAction")

    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> "IPrincipal":
        """The principal to grant permissions to.

        Stability:
            experimental
        """
        return jsii.get(self, "grantPrincipal")

    @property
    @jsii.member(jsii_name="groupArn")
    def group_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "groupArn")

    @property
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "groupName")

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")


@jsii.interface(jsii_type="@aws-cdk/aws-iam.IResourceWithPolicy")
class IResourceWithPolicy(aws_cdk.cdk.IConstruct, jsii.compat.Protocol):
    """A resource with a resource policy that can be added to.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IResourceWithPolicyProxy

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: "PolicyStatement") -> None:
        """Add a statement to the resource's resource policy.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        ...


class _IResourceWithPolicyProxy(jsii.proxy_for(aws_cdk.cdk.IConstruct)):
    """A resource with a resource policy that can be added to.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-iam.IResourceWithPolicy"
    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: "PolicyStatement") -> None:
        """Add a statement to the resource's resource policy.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToResourcePolicy", [statement])


@jsii.interface(jsii_type="@aws-cdk/aws-iam.IRole")
class IRole(IIdentity, jsii.compat.Protocol):
    """A Role object.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IRoleProxy

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """Returns the ARN of this role.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> str:
        """Returns the name of this role.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: "IPrincipal", *actions: str) -> "Grant":
        """Grant the actions defined in actions to the identity Principal on this resource.

        Arguments:
            grantee: -
            actions: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantPassRole")
    def grant_pass_role(self, grantee: "IPrincipal") -> "Grant":
        """Grant permissions to the given principal to pass this role.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        ...


class _IRoleProxy(jsii.proxy_for(IIdentity)):
    """A Role object.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-iam.IRole"
    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """Returns the ARN of this role.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "roleArn")

    @property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> str:
        """Returns the name of this role.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "roleName")

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: "IPrincipal", *actions: str) -> "Grant":
        """Grant the actions defined in actions to the identity Principal on this resource.

        Arguments:
            grantee: -
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grant", [grantee, *actions])

    @jsii.member(jsii_name="grantPassRole")
    def grant_pass_role(self, grantee: "IPrincipal") -> "Grant":
        """Grant permissions to the given principal to pass this role.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPassRole", [grantee])


@jsii.interface(jsii_type="@aws-cdk/aws-iam.IUser")
class IUser(IIdentity, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IUserProxy

    @property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> str:
        """
        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addToGroup")
    def add_to_group(self, group: "IGroup") -> None:
        """
        Arguments:
            group: -

        Stability:
            experimental
        """
        ...


class _IUserProxy(jsii.proxy_for(IIdentity)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-iam.IUser"
    @property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "userName")

    @jsii.member(jsii_name="addToGroup")
    def add_to_group(self, group: "IGroup") -> None:
        """
        Arguments:
            group: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToGroup", [group])


@jsii.implements(IPrincipal)
class ImportedResourcePrincipal(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.ImportedResourcePrincipal"):
    """A principal associated with an imported resource.

    Some resources have roles associated with them which they assume, such as
    Lambda Functions, CodeBuild projects, StepFunctions machines, etc.

    When those resources are imported, their actual roles are not always
    imported with them. When that happens, we use an instance of this class
    instead, which will add user warnings when statements are attempted to be
    added to it.

    Stability:
        experimental
    """
    def __init__(self, *, resource: aws_cdk.cdk.IConstruct) -> None:
        """
        Arguments:
            props: -
            resource: The resource the role proxy is for.

        Stability:
            experimental
        """
        props: ImportedResourcePrincipalProps = {"resource": resource}

        jsii.create(ImportedResourcePrincipal, self, [props])

    @jsii.member(jsii_name="addToPolicy")
    def add_to_policy(self, statement: "PolicyStatement") -> bool:
        """Add to the policy of this principal.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToPolicy", [statement])

    @property
    @jsii.member(jsii_name="assumeRoleAction")
    def assume_role_action(self) -> str:
        """When this Principal is used in an AssumeRole policy, the action to use.

        Stability:
            experimental
        """
        return jsii.get(self, "assumeRoleAction")

    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> "IPrincipal":
        """The principal to grant permissions to.

        Stability:
            experimental
        """
        return jsii.get(self, "grantPrincipal")

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")


@jsii.data_type(jsii_type="@aws-cdk/aws-iam.ImportedResourcePrincipalProps", jsii_struct_bases=[])
class ImportedResourcePrincipalProps(jsii.compat.TypedDict):
    """Properties for an ImportedResourcePrincipal.

    Stability:
        experimental
    """
    resource: aws_cdk.cdk.IConstruct
    """The resource the role proxy is for.

    Stability:
        experimental
    """

@jsii.implements(IRole)
class LazyRole(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.LazyRole"):
    """An IAM role that only gets attached to the construct tree once it gets used, not before.

    This construct can be used to simplify logic in other constructs
    which need to create a role but only if certain configurations occur
    (such as when AutoScaling is configured). The role can be configured in one
    place, but if it never gets used it doesn't get instantiated and will
    not be synthesized or deployed.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, assumed_by: "IPrincipal", external_id: typing.Optional[str]=None, inline_policies: typing.Optional[typing.Mapping[str,"PolicyDocument"]]=None, managed_policy_arns: typing.Optional[typing.List[str]]=None, max_session_duration_sec: typing.Optional[jsii.Number]=None, path: typing.Optional[str]=None, role_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            assumedBy: The IAM principal (i.e. ``new ServicePrincipal('sns.amazonaws.com')``) which can assume this role. You can later modify the assume role policy document by accessing it via the ``assumeRolePolicy`` property.
            externalId: ID that the role assumer needs to provide when assuming this role. If the configured and provided external IDs do not match, the AssumeRole operation will fail. Default: No external ID required
            inlinePolicies: A list of named policies to inline into this role. These policies will be created with the role, whereas those added by ``addToPolicy`` are added using a separate CloudFormation resource (allowing a way around circular dependencies that could otherwise be introduced). Default: - No policy is inlined in the Role resource.
            managedPolicyArns: A list of ARNs for managed policies associated with this role. You can add managed policies later using ``attachManagedPolicy(arn)``. Default: - No managed policies.
            maxSessionDurationSec: The maximum session duration (in seconds) that you want to set for the specified role. This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours. Anyone who assumes the role from the AWS CLI or API can use the DurationSeconds API parameter or the duration-seconds CLI parameter to request a longer session. The MaxSessionDuration setting determines the maximum duration that can be requested using the DurationSeconds parameter. If users don't specify a value for the DurationSeconds parameter, their security credentials are valid for one hour by default. This applies when you use the AssumeRole* API operations or the assume-role* CLI operations but does not apply when you use those operations to create a console URL. Default: 3600 (1 hour)
            path: The path associated with this role. For information about IAM paths, see Friendly Names and Paths in IAM User Guide. Default: /
            roleName: A name for the IAM role. For valid values, see the RoleName parameter for the CreateRole action in the IAM API Reference. IMPORTANT: If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name. If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to acknowledge your template's capabilities. For more information, see Acknowledging IAM Resources in AWS CloudFormation Templates. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the group name.

        Stability:
            experimental
        """
        props: LazyRoleProps = {"assumedBy": assumed_by}

        if external_id is not None:
            props["externalId"] = external_id

        if inline_policies is not None:
            props["inlinePolicies"] = inline_policies

        if managed_policy_arns is not None:
            props["managedPolicyArns"] = managed_policy_arns

        if max_session_duration_sec is not None:
            props["maxSessionDurationSec"] = max_session_duration_sec

        if path is not None:
            props["path"] = path

        if role_name is not None:
            props["roleName"] = role_name

        jsii.create(LazyRole, self, [scope, id, props])

    @jsii.member(jsii_name="addToPolicy")
    def add_to_policy(self, statement: "PolicyStatement") -> bool:
        """Adds a permission to the role's default policy document. If there is no default policy attached to this role, it will be created.

        Arguments:
            statement: The permission statement to add to the policy document.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToPolicy", [statement])

    @jsii.member(jsii_name="attachInlinePolicy")
    def attach_inline_policy(self, policy: "Policy") -> None:
        """Attaches a policy to this role.

        Arguments:
            policy: The policy to attach.

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachInlinePolicy", [policy])

    @jsii.member(jsii_name="attachManagedPolicy")
    def attach_managed_policy(self, arn: str) -> None:
        """Attaches a managed policy to this role.

        Arguments:
            arn: The ARN of the managed policy to attach.

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachManagedPolicy", [arn])

    @jsii.member(jsii_name="grant")
    def grant(self, identity: "IPrincipal", *actions: str) -> "Grant":
        """Grant the actions defined in actions to the identity Principal on this resource.

        Arguments:
            identity: -
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grant", [identity, *actions])

    @jsii.member(jsii_name="grantPassRole")
    def grant_pass_role(self, identity: "IPrincipal") -> "Grant":
        """Grant permissions to the given principal to pass this role.

        Arguments:
            identity: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPassRole", [identity])

    @property
    @jsii.member(jsii_name="assumeRoleAction")
    def assume_role_action(self) -> str:
        """When this Principal is used in an AssumeRole policy, the action to use.

        Stability:
            experimental
        """
        return jsii.get(self, "assumeRoleAction")

    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> "IPrincipal":
        """The principal to grant permissions to.

        Stability:
            experimental
        """
        return jsii.get(self, "grantPrincipal")

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "LazyRoleProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """Returns the ARN of this role.

        Stability:
            experimental
        """
        return jsii.get(self, "roleArn")

    @property
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "roleId")

    @property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> str:
        """Returns the name of this role.

        Stability:
            experimental
        """
        return jsii.get(self, "roleName")


@jsii.implements(IPolicy)
class Policy(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.Policy"):
    """The AWS::IAM::Policy resource associates an IAM policy with IAM users, roles, or groups.

    For more information about IAM policies, see `Overview of IAM
    Policies <http://docs.aws.amazon.com/IAM/latest/UserGuide/policies_overview.html>`_
    in the IAM User Guide guide.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, groups: typing.Optional[typing.List["IGroup"]]=None, policy_name: typing.Optional[str]=None, roles: typing.Optional[typing.List["IRole"]]=None, statements: typing.Optional[typing.List["PolicyStatement"]]=None, users: typing.Optional[typing.List["IUser"]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            groups: Groups to attach this policy to. You can also use ``attachToGroup(group)`` to attach this policy to a group. Default: - No groups.
            policyName: The name of the policy. If you specify multiple policies for an entity, specify unique names. For example, if you specify a list of policies for an IAM role, each policy must have a unique name. Default: - Uses the logical ID of the policy resource, which is ensured to be unique within the stack.
            roles: Roles to attach this policy to. You can also use ``attachToRole(role)`` to attach this policy to a role. Default: - No roles.
            statements: Initial set of permissions to add to this policy document. You can also use ``addPermission(statement)`` to add permissions later. Default: - No statements.
            users: Users to attach this policy to. You can also use ``attachToUser(user)`` to attach this policy to a user. Default: - No users.

        Stability:
            experimental
        """
        props: PolicyProps = {}

        if groups is not None:
            props["groups"] = groups

        if policy_name is not None:
            props["policyName"] = policy_name

        if roles is not None:
            props["roles"] = roles

        if statements is not None:
            props["statements"] = statements

        if users is not None:
            props["users"] = users

        jsii.create(Policy, self, [scope, id, props])

    @jsii.member(jsii_name="fromPolicyName")
    @classmethod
    def from_policy_name(cls, scope: aws_cdk.cdk.Construct, id: str, policy_name: str) -> "IPolicy":
        """
        Arguments:
            scope: -
            id: -
            policyName: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromPolicyName", [scope, id, policy_name])

    @jsii.member(jsii_name="addStatement")
    def add_statement(self, statement: "PolicyStatement") -> None:
        """Adds a statement to the policy document.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addStatement", [statement])

    @jsii.member(jsii_name="attachToGroup")
    def attach_to_group(self, group: "IGroup") -> None:
        """Attaches this policy to a group.

        Arguments:
            group: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachToGroup", [group])

    @jsii.member(jsii_name="attachToRole")
    def attach_to_role(self, role: "IRole") -> None:
        """Attaches this policy to a role.

        Arguments:
            role: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachToRole", [role])

    @jsii.member(jsii_name="attachToUser")
    def attach_to_user(self, user: "IUser") -> None:
        """Attaches this policy to a user.

        Arguments:
            user: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachToUser", [user])

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[str]:
        """Validate the current construct.

        This method can be implemented by derived constructs in order to perform
        validation logic. It is called on all constructs before synthesis.

        Stability:
            experimental
        """
        return jsii.invoke(self, "validate", [])

    @property
    @jsii.member(jsii_name="document")
    def document(self) -> "PolicyDocument":
        """The policy document.

        Stability:
            experimental
        """
        return jsii.get(self, "document")

    @property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> str:
        """The name of this policy.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "policyName")


@jsii.implements(aws_cdk.cdk.IResolvedValuePostProcessor)
class PolicyDocument(aws_cdk.cdk.Token, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.PolicyDocument"):
    """
    Stability:
        experimental
    """
    def __init__(self, base_document: typing.Any=None) -> None:
        """Creates a new IAM policy document.

        Arguments:
            baseDocument: -

        Stability:
            experimental
        """
        jsii.create(PolicyDocument, self, [base_document])

    @jsii.member(jsii_name="addStatement")
    def add_statement(self, statement: "PolicyStatement") -> "PolicyDocument":
        """Adds a statement to the policy document.

        Arguments:
            statement: the statement to add.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addStatement", [statement])

    @jsii.member(jsii_name="autoAssignSids")
    def auto_assign_sids(self) -> None:
        """Will automatically assign a unique SID to each statement, unless an SID is provided.

        Stability:
            experimental
        """
        return jsii.invoke(self, "autoAssignSids", [])

    @jsii.member(jsii_name="postProcess")
    def post_process(self, input: typing.Any, _context: aws_cdk.cdk.IResolveContext) -> typing.Any:
        """Removes duplicate statements.

        Arguments:
            input: -
            _context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "postProcess", [input, _context])

    @jsii.member(jsii_name="resolve")
    def resolve(self, _context: aws_cdk.cdk.IResolveContext) -> typing.Any:
        """
        Arguments:
            _context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolve", [_context])

    @property
    @jsii.member(jsii_name="baseDocument")
    def base_document(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "baseDocument")

    @property
    @jsii.member(jsii_name="isEmpty")
    def is_empty(self) -> bool:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "isEmpty")

    @property
    @jsii.member(jsii_name="statementCount")
    def statement_count(self) -> jsii.Number:
        """The number of statements already added to this policy. Can be used, for example, to generate uniuqe "sid"s within the policy.

        Stability:
            experimental
        """
        return jsii.get(self, "statementCount")


@jsii.data_type(jsii_type="@aws-cdk/aws-iam.PolicyProps", jsii_struct_bases=[])
class PolicyProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    groups: typing.List["IGroup"]
    """Groups to attach this policy to. You can also use ``attachToGroup(group)`` to attach this policy to a group.

    Default:
        - No groups.

    Stability:
        experimental
    """

    policyName: str
    """The name of the policy.

    If you specify multiple policies for an entity,
    specify unique names. For example, if you specify a list of policies for
    an IAM role, each policy must have a unique name.

    Default:
        - Uses the logical ID of the policy resource, which is ensured
          to be unique within the stack.

    Stability:
        experimental
    """

    roles: typing.List["IRole"]
    """Roles to attach this policy to. You can also use ``attachToRole(role)`` to attach this policy to a role.

    Default:
        - No roles.

    Stability:
        experimental
    """

    statements: typing.List["PolicyStatement"]
    """Initial set of permissions to add to this policy document. You can also use ``addPermission(statement)`` to add permissions later.

    Default:
        - No statements.

    Stability:
        experimental
    """

    users: typing.List["IUser"]
    """Users to attach this policy to. You can also use ``attachToUser(user)`` to attach this policy to a user.

    Default:
        - No users.

    Stability:
        experimental
    """

class PolicyStatement(aws_cdk.cdk.Token, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.PolicyStatement"):
    """Represents a statement in an IAM policy document.

    Stability:
        experimental
    """
    def __init__(self, effect: typing.Optional["PolicyStatementEffect"]=None) -> None:
        """
        Arguments:
            effect: -

        Stability:
            experimental
        """
        jsii.create(PolicyStatement, self, [effect])

    @jsii.member(jsii_name="addAccountRootPrincipal")
    def add_account_root_principal(self) -> "PolicyStatement":
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "addAccountRootPrincipal", [])

    @jsii.member(jsii_name="addAction")
    def add_action(self, action: str) -> "PolicyStatement":
        """
        Arguments:
            action: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAction", [action])

    @jsii.member(jsii_name="addActions")
    def add_actions(self, *actions: str) -> "PolicyStatement":
        """
        Arguments:
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addActions", [*actions])

    @jsii.member(jsii_name="addAllResources")
    def add_all_resources(self) -> "PolicyStatement":
        """Adds a ``"*"`` resource to this statement.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAllResources", [])

    @jsii.member(jsii_name="addAnyPrincipal")
    def add_any_principal(self) -> "PolicyStatement":
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "addAnyPrincipal", [])

    @jsii.member(jsii_name="addArnPrincipal")
    def add_arn_principal(self, arn: str) -> "PolicyStatement":
        """
        Arguments:
            arn: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addArnPrincipal", [arn])

    @jsii.member(jsii_name="addAwsAccountPrincipal")
    def add_aws_account_principal(self, account_id: str) -> "PolicyStatement":
        """
        Arguments:
            accountId: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAwsAccountPrincipal", [account_id])

    @jsii.member(jsii_name="addAwsPrincipal")
    def add_aws_principal(self, arn: str) -> "PolicyStatement":
        """
        Arguments:
            arn: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAwsPrincipal", [arn])

    @jsii.member(jsii_name="addCanonicalUserPrincipal")
    def add_canonical_user_principal(self, canonical_user_id: str) -> "PolicyStatement":
        """
        Arguments:
            canonicalUserId: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addCanonicalUserPrincipal", [canonical_user_id])

    @jsii.member(jsii_name="addCondition")
    def add_condition(self, key: str, value: typing.Any) -> "PolicyStatement":
        """Add a condition to the Policy.

        Arguments:
            key: -
            value: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addCondition", [key, value])

    @jsii.member(jsii_name="addConditions")
    def add_conditions(self, conditions: typing.Mapping[str,typing.Any]) -> "PolicyStatement":
        """Add multiple conditions to the Policy.

        Arguments:
            conditions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addConditions", [conditions])

    @jsii.member(jsii_name="addFederatedPrincipal")
    def add_federated_principal(self, federated: typing.Any, conditions: typing.Mapping[str,typing.Any]) -> "PolicyStatement":
        """
        Arguments:
            federated: -
            conditions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addFederatedPrincipal", [federated, conditions])

    @jsii.member(jsii_name="addPrincipal")
    def add_principal(self, principal: "IPrincipal") -> "PolicyStatement":
        """
        Arguments:
            principal: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addPrincipal", [principal])

    @jsii.member(jsii_name="addResource")
    def add_resource(self, arn: str) -> "PolicyStatement":
        """
        Arguments:
            arn: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addResource", [arn])

    @jsii.member(jsii_name="addResources")
    def add_resources(self, *arns: str) -> "PolicyStatement":
        """
        Arguments:
            arns: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addResources", [*arns])

    @jsii.member(jsii_name="addServicePrincipal")
    def add_service_principal(self, service: str, *, conditions: typing.Optional[typing.Mapping[str,typing.Any]]=None, region: typing.Optional[str]=None) -> "PolicyStatement":
        """Adds a service principal to this policy statement.

        Arguments:
            service: the service name for which a service principal is requested (e.g: ``s3.amazonaws.com``).
            opts: options for adding the service principal (such as specifying a principal in a different region).
            conditions: Additional conditions to add to the Service Principal. Default: - No conditions
            region: The region in which the service is operating. Default: the current Stack's region.

        Stability:
            experimental
        """
        opts: ServicePrincipalOpts = {}

        if conditions is not None:
            opts["conditions"] = conditions

        if region is not None:
            opts["region"] = region

        return jsii.invoke(self, "addServicePrincipal", [service, opts])

    @jsii.member(jsii_name="allow")
    def allow(self) -> "PolicyStatement":
        """Sets the permission effect to allow access to resources.

        Stability:
            experimental
        """
        return jsii.invoke(self, "allow", [])

    @jsii.member(jsii_name="deny")
    def deny(self) -> "PolicyStatement":
        """Sets the permission effect to deny access to resources.

        Stability:
            experimental
        """
        return jsii.invoke(self, "deny", [])

    @jsii.member(jsii_name="describe")
    def describe(self, sid: str) -> "PolicyStatement":
        """
        Arguments:
            sid: -

        Deprecated:
            Use ``statement.sid = value``

        Stability:
            deprecated
        """
        return jsii.invoke(self, "describe", [sid])

    @jsii.member(jsii_name="limitToAccount")
    def limit_to_account(self, account_id: str) -> "PolicyStatement":
        """
        Arguments:
            accountId: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "limitToAccount", [account_id])

    @jsii.member(jsii_name="resolve")
    def resolve(self, _context: aws_cdk.cdk.IResolveContext) -> typing.Any:
        """
        Arguments:
            _context: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resolve", [_context])

    @jsii.member(jsii_name="setCondition")
    def set_condition(self, key: str, value: typing.Any) -> "PolicyStatement":
        """Add a condition to the Policy.

        Arguments:
            key: -
            value: -

        Deprecated:
            For backwards compatibility. Use addCondition() instead.

        Stability:
            deprecated
        """
        return jsii.invoke(self, "setCondition", [key, value])

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toJson", [])

    @property
    @jsii.member(jsii_name="hasPrincipal")
    def has_principal(self) -> bool:
        """Indicates if this permission has a "Principal" section.

        Stability:
            experimental
        """
        return jsii.get(self, "hasPrincipal")

    @property
    @jsii.member(jsii_name="hasResource")
    def has_resource(self) -> bool:
        """Indicates if this permission as at least one resource associated with it.

        Stability:
            experimental
        """
        return jsii.get(self, "hasResource")

    @property
    @jsii.member(jsii_name="sid")
    def sid(self) -> typing.Optional[str]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "sid")

    @sid.setter
    def sid(self, value: typing.Optional[str]):
        return jsii.set(self, "sid", value)


@jsii.enum(jsii_type="@aws-cdk/aws-iam.PolicyStatementEffect")
class PolicyStatementEffect(enum.Enum):
    """
    Stability:
        experimental
    """
    Allow = "Allow"
    """
    Stability:
        experimental
    """
    Deny = "Deny"
    """
    Stability:
        experimental
    """

@jsii.implements(IPrincipal)
class PrincipalBase(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-iam.PrincipalBase"):
    """Base class for policy principals.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _PrincipalBaseProxy

    def __init__(self) -> None:
        jsii.create(PrincipalBase, self, [])

    @jsii.member(jsii_name="addToPolicy")
    def add_to_policy(self, _statement: "PolicyStatement") -> bool:
        """Add to the policy of this principal.

        Arguments:
            _statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToPolicy", [_statement])

    @jsii.member(jsii_name="toJSON")
    def to_json(self) -> typing.Mapping[str,typing.List[str]]:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "toJSON", [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="assumeRoleAction")
    def assume_role_action(self) -> str:
        """When this Principal is used in an AssumeRole policy, the action to use.

        Stability:
            experimental
        """
        return jsii.get(self, "assumeRoleAction")

    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> "IPrincipal":
        """The principal to grant permissions to.

        Stability:
            experimental
        """
        return jsii.get(self, "grantPrincipal")

    @property
    @jsii.member(jsii_name="policyFragment")
    @abc.abstractmethod
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        ...


class _PrincipalBaseProxy(PrincipalBase):
    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")


class ArnPrincipal(PrincipalBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.ArnPrincipal"):
    """
    Stability:
        experimental
    """
    def __init__(self, arn: str) -> None:
        """
        Arguments:
            arn: -

        Stability:
            experimental
        """
        jsii.create(ArnPrincipal, self, [arn])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="arn")
    def arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "arn")

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")


class AccountPrincipal(ArnPrincipal, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.AccountPrincipal"):
    """
    Stability:
        experimental
    """
    def __init__(self, account_id: typing.Any) -> None:
        """
        Arguments:
            accountId: -

        Stability:
            experimental
        """
        jsii.create(AccountPrincipal, self, [account_id])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> typing.Any:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "accountId")


class AccountRootPrincipal(AccountPrincipal, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.AccountRootPrincipal"):
    """
    Stability:
        experimental
    """
    def __init__(self) -> None:
        """
        Stability:
            experimental
        """
        jsii.create(AccountRootPrincipal, self, [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])


class AnyPrincipal(ArnPrincipal, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.AnyPrincipal"):
    """A principal representing all identities in all accounts.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        """
        Stability:
            experimental
        """
        jsii.create(AnyPrincipal, self, [])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])


class Anyone(AnyPrincipal, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.Anyone"):
    """A principal representing all identities in all accounts.

    Deprecated:
        use ``AnyPrincipal``

    Stability:
        deprecated
    """
    def __init__(self) -> None:
        """
        Stability:
            experimental
        """
        jsii.create(Anyone, self, [])


class CanonicalUserPrincipal(PrincipalBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.CanonicalUserPrincipal"):
    """A policy prinicipal for canonicalUserIds - useful for S3 bucket policies that use Origin Access identities.

    See https://docs.aws.amazon.com/general/latest/gr/acct-identifiers.html

    and

    https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html

    for more details.

    Stability:
        experimental
    """
    def __init__(self, canonical_user_id: str) -> None:
        """
        Arguments:
            canonicalUserId: -

        Stability:
            experimental
        """
        jsii.create(CanonicalUserPrincipal, self, [canonical_user_id])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="canonicalUserId")
    def canonical_user_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "canonicalUserId")

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")


class CompositePrincipal(PrincipalBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.CompositePrincipal"):
    """
    Stability:
        experimental
    """
    def __init__(self, *principals: "PrincipalBase") -> None:
        """
        Arguments:
            principals: -

        Stability:
            experimental
        """
        jsii.create(CompositePrincipal, self, [*principals])

    @jsii.member(jsii_name="addPrincipals")
    def add_principals(self, *principals: "PrincipalBase") -> "CompositePrincipal":
        """
        Arguments:
            principals: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addPrincipals", [*principals])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="assumeRoleAction")
    def assume_role_action(self) -> str:
        """When this Principal is used in an AssumeRole policy, the action to use.

        Stability:
            experimental
        """
        return jsii.get(self, "assumeRoleAction")

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")


class FederatedPrincipal(PrincipalBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.FederatedPrincipal"):
    """
    Stability:
        experimental
    """
    def __init__(self, federated: str, conditions: typing.Mapping[str,typing.Any], assume_role_action: typing.Optional[str]=None) -> None:
        """
        Arguments:
            federated: -
            conditions: -
            assumeRoleAction: -

        Stability:
            experimental
        """
        jsii.create(FederatedPrincipal, self, [federated, conditions, assume_role_action])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="assumeRoleAction")
    def assume_role_action(self) -> str:
        """When this Principal is used in an AssumeRole policy, the action to use.

        Stability:
            experimental
        """
        return jsii.get(self, "assumeRoleAction")

    @property
    @jsii.member(jsii_name="conditions")
    def conditions(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "conditions")

    @property
    @jsii.member(jsii_name="federated")
    def federated(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "federated")

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")


class OrganizationPrincipal(PrincipalBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.OrganizationPrincipal"):
    """A principal that represents an AWS Organization.

    Stability:
        experimental
    """
    def __init__(self, organization_id: str) -> None:
        """
        Arguments:
            organizationId: -

        Stability:
            experimental
        """
        jsii.create(OrganizationPrincipal, self, [organization_id])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "organizationId")

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")


class PrincipalPolicyFragment(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.PrincipalPolicyFragment"):
    """A collection of the fields in a PolicyStatement that can be used to identify a principal.

    This consists of the JSON used in the "Principal" field, and optionally a
    set of "Condition"s that need to be applied to the policy.

    Stability:
        experimental
    """
    def __init__(self, principal_json: typing.Mapping[str,typing.List[str]], conditions: typing.Optional[typing.Mapping[str,typing.Any]]=None) -> None:
        """
        Arguments:
            principalJson: -
            conditions: -

        Stability:
            experimental
        """
        jsii.create(PrincipalPolicyFragment, self, [principal_json, conditions])

    @property
    @jsii.member(jsii_name="conditions")
    def conditions(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "conditions")

    @property
    @jsii.member(jsii_name="principalJson")
    def principal_json(self) -> typing.Mapping[str,typing.List[str]]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "principalJson")


@jsii.implements(IRole)
class Role(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.Role"):
    """IAM Role.

    Defines an IAM role. The role is created with an assume policy document associated with
    the specified AWS service principal defined in ``serviceAssumeRole``.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, assumed_by: "IPrincipal", external_id: typing.Optional[str]=None, inline_policies: typing.Optional[typing.Mapping[str,"PolicyDocument"]]=None, managed_policy_arns: typing.Optional[typing.List[str]]=None, max_session_duration_sec: typing.Optional[jsii.Number]=None, path: typing.Optional[str]=None, role_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            assumedBy: The IAM principal (i.e. ``new ServicePrincipal('sns.amazonaws.com')``) which can assume this role. You can later modify the assume role policy document by accessing it via the ``assumeRolePolicy`` property.
            externalId: ID that the role assumer needs to provide when assuming this role. If the configured and provided external IDs do not match, the AssumeRole operation will fail. Default: No external ID required
            inlinePolicies: A list of named policies to inline into this role. These policies will be created with the role, whereas those added by ``addToPolicy`` are added using a separate CloudFormation resource (allowing a way around circular dependencies that could otherwise be introduced). Default: - No policy is inlined in the Role resource.
            managedPolicyArns: A list of ARNs for managed policies associated with this role. You can add managed policies later using ``attachManagedPolicy(arn)``. Default: - No managed policies.
            maxSessionDurationSec: The maximum session duration (in seconds) that you want to set for the specified role. This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours. Anyone who assumes the role from the AWS CLI or API can use the DurationSeconds API parameter or the duration-seconds CLI parameter to request a longer session. The MaxSessionDuration setting determines the maximum duration that can be requested using the DurationSeconds parameter. If users don't specify a value for the DurationSeconds parameter, their security credentials are valid for one hour by default. This applies when you use the AssumeRole* API operations or the assume-role* CLI operations but does not apply when you use those operations to create a console URL. Default: 3600 (1 hour)
            path: The path associated with this role. For information about IAM paths, see Friendly Names and Paths in IAM User Guide. Default: /
            roleName: A name for the IAM role. For valid values, see the RoleName parameter for the CreateRole action in the IAM API Reference. IMPORTANT: If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name. If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to acknowledge your template's capabilities. For more information, see Acknowledging IAM Resources in AWS CloudFormation Templates. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the group name.

        Stability:
            experimental
        """
        props: RoleProps = {"assumedBy": assumed_by}

        if external_id is not None:
            props["externalId"] = external_id

        if inline_policies is not None:
            props["inlinePolicies"] = inline_policies

        if managed_policy_arns is not None:
            props["managedPolicyArns"] = managed_policy_arns

        if max_session_duration_sec is not None:
            props["maxSessionDurationSec"] = max_session_duration_sec

        if path is not None:
            props["path"] = path

        if role_name is not None:
            props["roleName"] = role_name

        jsii.create(Role, self, [scope, id, props])

    @jsii.member(jsii_name="fromRoleArn")
    @classmethod
    def from_role_arn(cls, scope: aws_cdk.cdk.Construct, id: str, role_arn: str) -> "IRole":
        """Imports an external role by ARN.

        Arguments:
            scope: construct scope.
            id: construct id.
            roleArn: the ARN of the role to import.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromRoleArn", [scope, id, role_arn])

    @jsii.member(jsii_name="addToPolicy")
    def add_to_policy(self, statement: "PolicyStatement") -> bool:
        """Adds a permission to the role's default policy document. If there is no default policy attached to this role, it will be created.

        Arguments:
            statement: The permission statement to add to the policy document.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToPolicy", [statement])

    @jsii.member(jsii_name="attachInlinePolicy")
    def attach_inline_policy(self, policy: "Policy") -> None:
        """Attaches a policy to this role.

        Arguments:
            policy: The policy to attach.

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachInlinePolicy", [policy])

    @jsii.member(jsii_name="attachManagedPolicy")
    def attach_managed_policy(self, arn: str) -> None:
        """Attaches a managed policy to this role.

        Arguments:
            arn: The ARN of the managed policy to attach.

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachManagedPolicy", [arn])

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: "IPrincipal", *actions: str) -> "Grant":
        """Grant the actions defined in actions to the identity Principal on this resource.

        Arguments:
            grantee: -
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grant", [grantee, *actions])

    @jsii.member(jsii_name="grantPassRole")
    def grant_pass_role(self, identity: "IPrincipal") -> "Grant":
        """Grant permissions to the given principal to pass this role.

        Arguments:
            identity: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPassRole", [identity])

    @property
    @jsii.member(jsii_name="assumeRoleAction")
    def assume_role_action(self) -> str:
        """When this Principal is used in an AssumeRole policy, the action to use.

        Stability:
            experimental
        """
        return jsii.get(self, "assumeRoleAction")

    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> "IPrincipal":
        """The principal to grant permissions to.

        Stability:
            experimental
        """
        return jsii.get(self, "grantPrincipal")

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Returns the role.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """Returns the ARN of this role.

        Stability:
            experimental
        """
        return jsii.get(self, "roleArn")

    @property
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> str:
        """Returns the stable and unique string identifying the role.

        For example,
        AIDAJQABLZS4A3QDU576Q.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "roleId")

    @property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> str:
        """Returns the name of the role.

        Stability:
            experimental
        """
        return jsii.get(self, "roleName")

    @property
    @jsii.member(jsii_name="assumeRolePolicy")
    def assume_role_policy(self) -> typing.Optional["PolicyDocument"]:
        """The assume role policy document associated with this role.

        Stability:
            experimental
        """
        return jsii.get(self, "assumeRolePolicy")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _RoleProps(jsii.compat.TypedDict, total=False):
    externalId: str
    """ID that the role assumer needs to provide when assuming this role.

    If the configured and provided external IDs do not match, the
    AssumeRole operation will fail.

    Default:
        No external ID required

    Stability:
        experimental
    """
    inlinePolicies: typing.Mapping[str,"PolicyDocument"]
    """A list of named policies to inline into this role.

    These policies will be
    created with the role, whereas those added by ``addToPolicy`` are added
    using a separate CloudFormation resource (allowing a way around circular
    dependencies that could otherwise be introduced).

    Default:
        - No policy is inlined in the Role resource.

    Stability:
        experimental
    """
    managedPolicyArns: typing.List[str]
    """A list of ARNs for managed policies associated with this role. You can add managed policies later using ``attachManagedPolicy(arn)``.

    Default:
        - No managed policies.

    Stability:
        experimental
    """
    maxSessionDurationSec: jsii.Number
    """The maximum session duration (in seconds) that you want to set for the specified role.

    This setting can have a value from 1 hour (3600sec) to
    12 (43200sec) hours.

    Anyone who assumes the role from the AWS CLI or API can use the
    DurationSeconds API parameter or the duration-seconds CLI parameter to
    request a longer session. The MaxSessionDuration setting determines the
    maximum duration that can be requested using the DurationSeconds
    parameter.

    If users don't specify a value for the DurationSeconds parameter, their
    security credentials are valid for one hour by default. This applies when
    you use the AssumeRole* API operations or the assume-role* CLI operations
    but does not apply when you use those operations to create a console URL.

    Default:
        3600 (1 hour)

    Stability:
        experimental
    link:
        https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use.html
    """
    path: str
    """The path associated with this role.

    For information about IAM paths, see
    Friendly Names and Paths in IAM User Guide.

    Default:
        /

    Stability:
        experimental
    """
    roleName: str
    """A name for the IAM role.

    For valid values, see the RoleName parameter for
    the CreateRole action in the IAM API Reference.

    IMPORTANT: If you specify a name, you cannot perform updates that require
    replacement of this resource. You can perform updates that require no or
    some interruption. If you must replace the resource, specify a new name.

    If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to
    acknowledge your template's capabilities. For more information, see
    Acknowledging IAM Resources in AWS CloudFormation Templates.

    Default:
        - AWS CloudFormation generates a unique physical ID and uses that ID
          for the group name.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.RoleProps", jsii_struct_bases=[_RoleProps])
class RoleProps(_RoleProps):
    """
    Stability:
        experimental
    """
    assumedBy: "IPrincipal"
    """The IAM principal (i.e. ``new ServicePrincipal('sns.amazonaws.com')``) which can assume this role.

    You can later modify the assume role policy document by accessing it via
    the ``assumeRolePolicy`` property.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iam.LazyRoleProps", jsii_struct_bases=[RoleProps])
class LazyRoleProps(RoleProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    pass

class ServicePrincipal(PrincipalBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.ServicePrincipal"):
    """An IAM principal that represents an AWS service (i.e. sqs.amazonaws.com).

    Stability:
        experimental
    """
    def __init__(self, service: str, *, conditions: typing.Optional[typing.Mapping[str,typing.Any]]=None, region: typing.Optional[str]=None) -> None:
        """
        Arguments:
            service: -
            opts: -
            conditions: Additional conditions to add to the Service Principal. Default: - No conditions
            region: The region in which the service is operating. Default: the current Stack's region.

        Stability:
            experimental
        """
        opts: ServicePrincipalOpts = {}

        if conditions is not None:
            opts["conditions"] = conditions

        if region is not None:
            opts["region"] = region

        jsii.create(ServicePrincipal, self, [service, opts])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> str:
        """Returns a string representation of an object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toString", [])

    @property
    @jsii.member(jsii_name="opts")
    def opts(self) -> "ServicePrincipalOpts":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "opts")

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")

    @property
    @jsii.member(jsii_name="service")
    def service(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "service")


@jsii.data_type(jsii_type="@aws-cdk/aws-iam.ServicePrincipalOpts", jsii_struct_bases=[])
class ServicePrincipalOpts(jsii.compat.TypedDict, total=False):
    """Options for a service principal.

    Stability:
        experimental
    """
    conditions: typing.Mapping[str,typing.Any]
    """Additional conditions to add to the Service Principal.

    Default:
        - No conditions

    Stability:
        experimental
    """

    region: str
    """The region in which the service is operating.

    Default:
        the current Stack's region.

    Stability:
        experimental
    """

@jsii.implements(IIdentity)
class User(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iam.User"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, groups: typing.Optional[typing.List["IGroup"]]=None, managed_policy_arns: typing.Optional[typing.List[typing.Any]]=None, password: typing.Optional[aws_cdk.cdk.SecretValue]=None, password_reset_required: typing.Optional[bool]=None, path: typing.Optional[str]=None, user_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            groups: Groups to add this user to. You can also use ``addToGroup`` to add this user to a group. Default: - No groups.
            managedPolicyArns: A list of ARNs for managed policies attacherd to this user. You can use ``addManagedPolicy(arn)`` to attach a managed policy to this user. Default: - No managed policies.
            password: The password for the user. This is required so the user can access the AWS Management Console. You can use ``SecretValue.plainText`` to specify a password in plain text or use ``secretsmanager.Secret.import`` to reference a secret in Secrets Manager. Default: User won't be able to access the management console without a password.
            passwordResetRequired: Specifies whether the user is required to set a new password the next time the user logs in to the AWS Management Console. If this is set to 'true', you must also specify "initialPassword". Default: false
            path: The path for the user name. For more information about paths, see IAM Identifiers in the IAM User Guide. Default: /
            userName: A name for the IAM user. For valid values, see the UserName parameter for the CreateUser action in the IAM API Reference. If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the user name. If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name. If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to acknowledge your template's capabilities. For more information, see Acknowledging IAM Resources in AWS CloudFormation Templates. Default: Generated by CloudFormation (recommended)

        Stability:
            experimental
        """
        props: UserProps = {}

        if groups is not None:
            props["groups"] = groups

        if managed_policy_arns is not None:
            props["managedPolicyArns"] = managed_policy_arns

        if password is not None:
            props["password"] = password

        if password_reset_required is not None:
            props["passwordResetRequired"] = password_reset_required

        if path is not None:
            props["path"] = path

        if user_name is not None:
            props["userName"] = user_name

        jsii.create(User, self, [scope, id, props])

    @jsii.member(jsii_name="addToGroup")
    def add_to_group(self, group: "IGroup") -> None:
        """Adds this user to a group.

        Arguments:
            group: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToGroup", [group])

    @jsii.member(jsii_name="addToPolicy")
    def add_to_policy(self, statement: "PolicyStatement") -> bool:
        """Adds an IAM statement to the default policy.

        Arguments:
            statement: -

        Returns:
            true

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToPolicy", [statement])

    @jsii.member(jsii_name="attachInlinePolicy")
    def attach_inline_policy(self, policy: "Policy") -> None:
        """Attaches a policy to this user.

        Arguments:
            policy: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachInlinePolicy", [policy])

    @jsii.member(jsii_name="attachManagedPolicy")
    def attach_managed_policy(self, arn: str) -> None:
        """Attaches a managed policy to the user.

        Arguments:
            arn: The ARN of the managed policy to attach.

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachManagedPolicy", [arn])

    @property
    @jsii.member(jsii_name="assumeRoleAction")
    def assume_role_action(self) -> str:
        """When this Principal is used in an AssumeRole policy, the action to use.

        Stability:
            experimental
        """
        return jsii.get(self, "assumeRoleAction")

    @property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> "IPrincipal":
        """The principal to grant permissions to.

        Stability:
            experimental
        """
        return jsii.get(self, "grantPrincipal")

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> "PrincipalPolicyFragment":
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")

    @property
    @jsii.member(jsii_name="userArn")
    def user_arn(self) -> str:
        """An attribute that represents the user's ARN.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "userArn")

    @property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> str:
        """An attribute that represents the user name.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "userName")


@jsii.data_type(jsii_type="@aws-cdk/aws-iam.UserProps", jsii_struct_bases=[])
class UserProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    groups: typing.List["IGroup"]
    """Groups to add this user to.

    You can also use ``addToGroup`` to add this
    user to a group.

    Default:
        - No groups.

    Stability:
        experimental
    """

    managedPolicyArns: typing.List[typing.Any]
    """A list of ARNs for managed policies attacherd to this user. You can use ``addManagedPolicy(arn)`` to attach a managed policy to this user.

    Default:
        - No managed policies.

    Stability:
        experimental
    """

    password: aws_cdk.cdk.SecretValue
    """The password for the user. This is required so the user can access the AWS Management Console.

    You can use ``SecretValue.plainText`` to specify a password in plain text or
    use ``secretsmanager.Secret.import`` to reference a secret in Secrets Manager.

    Default:
        User won't be able to access the management console without a password.

    Stability:
        experimental
    """

    passwordResetRequired: bool
    """Specifies whether the user is required to set a new password the next time the user logs in to the AWS Management Console.

    If this is set to 'true', you must also specify "initialPassword".

    Default:
        false

    Stability:
        experimental
    """

    path: str
    """The path for the user name.

    For more information about paths, see IAM
    Identifiers in the IAM User Guide.

    Default:
        /

    Stability:
        experimental
    """

    userName: str
    """A name for the IAM user.

    For valid values, see the UserName parameter for
    the CreateUser action in the IAM API Reference. If you don't specify a
    name, AWS CloudFormation generates a unique physical ID and uses that ID
    for the user name.

    If you specify a name, you cannot perform updates that require
    replacement of this resource. You can perform updates that require no or
    some interruption. If you must replace the resource, specify a new name.

    If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to
    acknowledge your template's capabilities. For more information, see
    Acknowledging IAM Resources in AWS CloudFormation Templates.

    Default:
        Generated by CloudFormation (recommended)

    Stability:
        experimental
    """

__all__ = ["AccountPrincipal", "AccountRootPrincipal", "AnyPrincipal", "Anyone", "ArnPrincipal", "AwsManagedPolicy", "CanonicalUserPrincipal", "CfnAccessKey", "CfnAccessKeyProps", "CfnGroup", "CfnGroupProps", "CfnInstanceProfile", "CfnInstanceProfileProps", "CfnManagedPolicy", "CfnManagedPolicyProps", "CfnPolicy", "CfnPolicyProps", "CfnRole", "CfnRoleProps", "CfnServiceLinkedRole", "CfnServiceLinkedRoleProps", "CfnUser", "CfnUserProps", "CfnUserToGroupAddition", "CfnUserToGroupAdditionProps", "CommonGrantOptions", "CompositePrincipal", "FederatedPrincipal", "Grant", "GrantOnPrincipalAndResourceOptions", "GrantOnPrincipalOptions", "GrantWithResourceOptions", "Group", "GroupProps", "IGrantable", "IGroup", "IIdentity", "IPolicy", "IPrincipal", "IResourceWithPolicy", "IRole", "IUser", "ImportedResourcePrincipal", "ImportedResourcePrincipalProps", "LazyRole", "LazyRoleProps", "OrganizationPrincipal", "Policy", "PolicyDocument", "PolicyProps", "PolicyStatement", "PolicyStatementEffect", "PrincipalBase", "PrincipalPolicyFragment", "Role", "RoleProps", "ServicePrincipal", "ServicePrincipalOpts", "User", "UserProps", "__jsii_assembly__"]

publication.publish()
