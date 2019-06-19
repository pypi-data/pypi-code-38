import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_iam
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-kms", "0.35.0", __name__, "aws-kms@0.35.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-kms.AliasAttributes", jsii_struct_bases=[])
class AliasAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    aliasName: str
    """
    Stability:
        experimental
    """

    aliasTargetKey: "IKey"
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-kms.AliasProps", jsii_struct_bases=[])
class AliasProps(jsii.compat.TypedDict):
    """Construction properties for a KMS Key Alias object.

    Stability:
        experimental
    """
    name: str
    """The name of the alias.

    The name must start with alias followed by a
    forward slash, such as alias/. You can't specify aliases that begin with
    alias/AWS. These aliases are reserved.

    Stability:
        experimental
    """

    targetKey: "IKey"
    """The ID of the key for which you are creating the alias.

    Specify the key's
    globally unique identifier or Amazon Resource Name (ARN). You can't
    specify another alias.

    Stability:
        experimental
    """

class CfnAlias(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kms.CfnAlias"):
    """A CloudFormation ``AWS::KMS::Alias``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-alias.html
    Stability:
        experimental
    cloudformationResource:
        AWS::KMS::Alias
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, alias_name: str, target_key_id: str) -> None:
        """Create a new ``AWS::KMS::Alias``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            aliasName: ``AWS::KMS::Alias.AliasName``.
            targetKeyId: ``AWS::KMS::Alias.TargetKeyId``.

        Stability:
            experimental
        """
        props: CfnAliasProps = {"aliasName": alias_name, "targetKeyId": target_key_id}

        jsii.create(CfnAlias, self, [scope, id, props])

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
    @jsii.member(jsii_name="aliasName")
    def alias_name(self) -> str:
        """``AWS::KMS::Alias.AliasName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-alias.html#cfn-kms-alias-aliasname
        Stability:
            experimental
        """
        return jsii.get(self, "aliasName")

    @alias_name.setter
    def alias_name(self, value: str):
        return jsii.set(self, "aliasName", value)

    @property
    @jsii.member(jsii_name="targetKeyId")
    def target_key_id(self) -> str:
        """``AWS::KMS::Alias.TargetKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-alias.html#cfn-kms-alias-targetkeyid
        Stability:
            experimental
        """
        return jsii.get(self, "targetKeyId")

    @target_key_id.setter
    def target_key_id(self, value: str):
        return jsii.set(self, "targetKeyId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-kms.CfnAliasProps", jsii_struct_bases=[])
class CfnAliasProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::KMS::Alias``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-alias.html
    Stability:
        experimental
    """
    aliasName: str
    """``AWS::KMS::Alias.AliasName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-alias.html#cfn-kms-alias-aliasname
    Stability:
        experimental
    """

    targetKeyId: str
    """``AWS::KMS::Alias.TargetKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-alias.html#cfn-kms-alias-targetkeyid
    Stability:
        experimental
    """

class CfnKey(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kms.CfnKey"):
    """A CloudFormation ``AWS::KMS::Key``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html
    Stability:
        experimental
    cloudformationResource:
        AWS::KMS::Key
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, key_policy: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable], description: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, enable_key_rotation: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, key_usage: typing.Optional[str]=None, pending_window_in_days: typing.Optional[jsii.Number]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::KMS::Key``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            keyPolicy: ``AWS::KMS::Key.KeyPolicy``.
            description: ``AWS::KMS::Key.Description``.
            enabled: ``AWS::KMS::Key.Enabled``.
            enableKeyRotation: ``AWS::KMS::Key.EnableKeyRotation``.
            keyUsage: ``AWS::KMS::Key.KeyUsage``.
            pendingWindowInDays: ``AWS::KMS::Key.PendingWindowInDays``.
            tags: ``AWS::KMS::Key.Tags``.

        Stability:
            experimental
        """
        props: CfnKeyProps = {"keyPolicy": key_policy}

        if description is not None:
            props["description"] = description

        if enabled is not None:
            props["enabled"] = enabled

        if enable_key_rotation is not None:
            props["enableKeyRotation"] = enable_key_rotation

        if key_usage is not None:
            props["keyUsage"] = key_usage

        if pending_window_in_days is not None:
            props["pendingWindowInDays"] = pending_window_in_days

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnKey, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::KMS::Key.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="keyPolicy")
    def key_policy(self) -> typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]:
        """``AWS::KMS::Key.KeyPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-keypolicy
        Stability:
            experimental
        """
        return jsii.get(self, "keyPolicy")

    @key_policy.setter
    def key_policy(self, value: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]):
        return jsii.set(self, "keyPolicy", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::KMS::Key.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::KMS::Key.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-enabled
        Stability:
            experimental
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="enableKeyRotation")
    def enable_key_rotation(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::KMS::Key.EnableKeyRotation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-enablekeyrotation
        Stability:
            experimental
        """
        return jsii.get(self, "enableKeyRotation")

    @enable_key_rotation.setter
    def enable_key_rotation(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "enableKeyRotation", value)

    @property
    @jsii.member(jsii_name="keyUsage")
    def key_usage(self) -> typing.Optional[str]:
        """``AWS::KMS::Key.KeyUsage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-keyusage
        Stability:
            experimental
        """
        return jsii.get(self, "keyUsage")

    @key_usage.setter
    def key_usage(self, value: typing.Optional[str]):
        return jsii.set(self, "keyUsage", value)

    @property
    @jsii.member(jsii_name="pendingWindowInDays")
    def pending_window_in_days(self) -> typing.Optional[jsii.Number]:
        """``AWS::KMS::Key.PendingWindowInDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-pendingwindowindays
        Stability:
            experimental
        """
        return jsii.get(self, "pendingWindowInDays")

    @pending_window_in_days.setter
    def pending_window_in_days(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "pendingWindowInDays", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnKeyProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::KMS::Key.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-description
    Stability:
        experimental
    """
    enabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::KMS::Key.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-enabled
    Stability:
        experimental
    """
    enableKeyRotation: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::KMS::Key.EnableKeyRotation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-enablekeyrotation
    Stability:
        experimental
    """
    keyUsage: str
    """``AWS::KMS::Key.KeyUsage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-keyusage
    Stability:
        experimental
    """
    pendingWindowInDays: jsii.Number
    """``AWS::KMS::Key.PendingWindowInDays``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-pendingwindowindays
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::KMS::Key.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-kms.CfnKeyProps", jsii_struct_bases=[_CfnKeyProps])
class CfnKeyProps(_CfnKeyProps):
    """Properties for defining a ``AWS::KMS::Key``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html
    Stability:
        experimental
    """
    keyPolicy: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::KMS::Key.KeyPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html#cfn-kms-key-keypolicy
    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-kms.IAlias")
class IAlias(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """A KMS Key alias.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IAliasProxy

    @property
    @jsii.member(jsii_name="aliasName")
    def alias_name(self) -> str:
        """The name of the alias.

        Stability:
            experimental
        attribute:
            AliasName
        """
        ...

    @property
    @jsii.member(jsii_name="aliasTargetKey")
    def alias_target_key(self) -> "IKey":
        """The Key to which the Alias refers.

        Stability:
            experimental
        attribute:
            TargetKeyId
        """
        ...


class _IAliasProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """A KMS Key alias.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-kms.IAlias"
    @property
    @jsii.member(jsii_name="aliasName")
    def alias_name(self) -> str:
        """The name of the alias.

        Stability:
            experimental
        attribute:
            AliasName
        """
        return jsii.get(self, "aliasName")

    @property
    @jsii.member(jsii_name="aliasTargetKey")
    def alias_target_key(self) -> "IKey":
        """The Key to which the Alias refers.

        Stability:
            experimental
        attribute:
            TargetKeyId
        """
        return jsii.get(self, "aliasTargetKey")


@jsii.implements(IAlias)
class Alias(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kms.Alias"):
    """Defines a display name for a customer master key (CMK) in AWS Key Management Service (AWS KMS).

    Using an alias to refer to a key can help you simplify key
    management. For example, when rotating keys, you can just update the alias
    mapping instead of tracking and changing key IDs. For more information, see
    Working with Aliases in the AWS Key Management Service Developer Guide.

    You can also add an alias for a key by calling ``key.addAlias(alias)``.

    Stability:
        experimental
    resource:
        AWS::KMS::Alias
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, target_key: "IKey") -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            name: The name of the alias. The name must start with alias followed by a forward slash, such as alias/. You can't specify aliases that begin with alias/AWS. These aliases are reserved.
            targetKey: The ID of the key for which you are creating the alias. Specify the key's globally unique identifier or Amazon Resource Name (ARN). You can't specify another alias.

        Stability:
            experimental
        """
        props: AliasProps = {"name": name, "targetKey": target_key}

        jsii.create(Alias, self, [scope, id, props])

    @jsii.member(jsii_name="fromAliasAttributes")
    @classmethod
    def from_alias_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, alias_name: str, alias_target_key: "IKey") -> "IAlias":
        """
        Arguments:
            scope: -
            id: -
            attrs: -
            aliasName: 
            aliasTargetKey: 

        Stability:
            experimental
        """
        attrs: AliasAttributes = {"aliasName": alias_name, "aliasTargetKey": alias_target_key}

        return jsii.sinvoke(cls, "fromAliasAttributes", [scope, id, attrs])

    @property
    @jsii.member(jsii_name="aliasName")
    def alias_name(self) -> str:
        """The name of the alias.

        Stability:
            experimental
        """
        return jsii.get(self, "aliasName")

    @property
    @jsii.member(jsii_name="aliasTargetKey")
    def alias_target_key(self) -> "IKey":
        """The Key to which the Alias refers.

        Stability:
            experimental
        """
        return jsii.get(self, "aliasTargetKey")


@jsii.interface(jsii_type="@aws-cdk/aws-kms.IKey")
class IKey(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """A KMS Key, either managed by this CDK app, or imported.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IKeyProxy

    @property
    @jsii.member(jsii_name="keyArn")
    def key_arn(self) -> str:
        """The ARN of the key.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @jsii.member(jsii_name="addAlias")
    def add_alias(self, alias: str) -> "Alias":
        """Defines a new alias for the key.

        Arguments:
            alias: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement, allow_no_op: typing.Optional[bool]=None) -> None:
        """Adds a statement to the KMS key resource policy.

        Arguments:
            statement: The policy statement to add.
            allowNoOp: If this is set to ``false`` and there is no policy defined (i.e. external key), the operation will fail. Otherwise, it will no-op.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *actions: str) -> aws_cdk.aws_iam.Grant:
        """Grant the indicated permissions on this key to the given principal.

        Arguments:
            grantee: -
            actions: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantDecrypt")
    def grant_decrypt(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant decryption permisisons using this key to the given principal.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantEncrypt")
    def grant_encrypt(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant encryption permisisons using this key to the given principal.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="grantEncryptDecrypt")
    def grant_encrypt_decrypt(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant encryption and decryption permisisons using this key to the given principal.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        ...


class _IKeyProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """A KMS Key, either managed by this CDK app, or imported.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-kms.IKey"
    @property
    @jsii.member(jsii_name="keyArn")
    def key_arn(self) -> str:
        """The ARN of the key.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "keyArn")

    @jsii.member(jsii_name="addAlias")
    def add_alias(self, alias: str) -> "Alias":
        """Defines a new alias for the key.

        Arguments:
            alias: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAlias", [alias])

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement, allow_no_op: typing.Optional[bool]=None) -> None:
        """Adds a statement to the KMS key resource policy.

        Arguments:
            statement: The policy statement to add.
            allowNoOp: If this is set to ``false`` and there is no policy defined (i.e. external key), the operation will fail. Otherwise, it will no-op.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToResourcePolicy", [statement, allow_no_op])

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *actions: str) -> aws_cdk.aws_iam.Grant:
        """Grant the indicated permissions on this key to the given principal.

        Arguments:
            grantee: -
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grant", [grantee, *actions])

    @jsii.member(jsii_name="grantDecrypt")
    def grant_decrypt(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant decryption permisisons using this key to the given principal.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantDecrypt", [grantee])

    @jsii.member(jsii_name="grantEncrypt")
    def grant_encrypt(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant encryption permisisons using this key to the given principal.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantEncrypt", [grantee])

    @jsii.member(jsii_name="grantEncryptDecrypt")
    def grant_encrypt_decrypt(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant encryption and decryption permisisons using this key to the given principal.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantEncryptDecrypt", [grantee])


@jsii.implements(IKey)
class Key(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kms.Key"):
    """Defines a KMS key.

    Stability:
        experimental
    resource:
        AWS::KMS::Key
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: typing.Optional[str]=None, enabled: typing.Optional[bool]=None, enable_key_rotation: typing.Optional[bool]=None, policy: typing.Optional[aws_cdk.aws_iam.PolicyDocument]=None, removal_policy: typing.Optional[aws_cdk.cdk.RemovalPolicy]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            description: A description of the key. Use a description that helps your users decide whether the key is appropriate for a particular task. Default: - No description.
            enabled: Indicates whether the key is available for use. Default: - Key is enabled.
            enableKeyRotation: Indicates whether AWS KMS rotates the key. Default: false
            policy: Custom policy document to attach to the KMS key. Default: - A policy document with permissions for the account root to administer the key will be created.
            removalPolicy: Whether the encryption key should be retained when it is removed from the Stack. This is useful when one wants to retain access to data that was encrypted with a key that is being retired. Default: RemovalPolicy.Retain

        Stability:
            experimental
        """
        props: KeyProps = {}

        if description is not None:
            props["description"] = description

        if enabled is not None:
            props["enabled"] = enabled

        if enable_key_rotation is not None:
            props["enableKeyRotation"] = enable_key_rotation

        if policy is not None:
            props["policy"] = policy

        if removal_policy is not None:
            props["removalPolicy"] = removal_policy

        jsii.create(Key, self, [scope, id, props])

    @jsii.member(jsii_name="fromKeyArn")
    @classmethod
    def from_key_arn(cls, scope: aws_cdk.cdk.Construct, id: str, key_arn: str) -> "IKey":
        """Import an externally defined KMS Key using its ARN.

        Arguments:
            scope: the construct that will "own" the imported key.
            id: the id of the imported key in the construct tree.
            keyArn: the ARN of an existing KMS key.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromKeyArn", [scope, id, key_arn])

    @jsii.member(jsii_name="addAlias")
    def add_alias(self, alias: str) -> "Alias":
        """Defines a new alias for the key.

        Arguments:
            alias: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAlias", [alias])

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(self, statement: aws_cdk.aws_iam.PolicyStatement, allow_no_op: typing.Optional[bool]=None) -> None:
        """Adds a statement to the KMS key resource policy.

        Arguments:
            statement: The policy statement to add.
            allowNoOp: If this is set to ``false`` and there is no policy defined (i.e. external key), the operation will fail. Otherwise, it will no-op.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToResourcePolicy", [statement, allow_no_op])

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *actions: str) -> aws_cdk.aws_iam.Grant:
        """Grant the indicated permissions on this key to the given principal.

        This modifies both the principal's policy as well as the resource policy,
        since the default CloudFormation setup for KMS keys is that the policy
        must not be empty and so default grants won't work.

        Arguments:
            grantee: -
            actions: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grant", [grantee, *actions])

    @jsii.member(jsii_name="grantDecrypt")
    def grant_decrypt(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant decryption permisisons using this key to the given principal.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantDecrypt", [grantee])

    @jsii.member(jsii_name="grantEncrypt")
    def grant_encrypt(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant encryption permisisons using this key to the given principal.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantEncrypt", [grantee])

    @jsii.member(jsii_name="grantEncryptDecrypt")
    def grant_encrypt_decrypt(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant encryption and decryption permisisons using this key to the given principal.

        Arguments:
            grantee: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantEncryptDecrypt", [grantee])

    @property
    @jsii.member(jsii_name="keyArn")
    def key_arn(self) -> str:
        """The ARN of the key.

        Stability:
            experimental
        """
        return jsii.get(self, "keyArn")

    @property
    @jsii.member(jsii_name="policy")
    def _policy(self) -> typing.Optional[aws_cdk.aws_iam.PolicyDocument]:
        """Optional policy document that represents the resource policy of this key.

        If specified, addToResourcePolicy can be used to edit this policy.
        Otherwise this method will no-op.

        Stability:
            experimental
        """
        return jsii.get(self, "policy")


@jsii.data_type(jsii_type="@aws-cdk/aws-kms.KeyProps", jsii_struct_bases=[])
class KeyProps(jsii.compat.TypedDict, total=False):
    """Construction properties for a KMS Key object.

    Stability:
        experimental
    """
    description: str
    """A description of the key.

    Use a description that helps your users decide
    whether the key is appropriate for a particular task.

    Default:
        - No description.

    Stability:
        experimental
    """

    enabled: bool
    """Indicates whether the key is available for use.

    Default:
        - Key is enabled.

    Stability:
        experimental
    """

    enableKeyRotation: bool
    """Indicates whether AWS KMS rotates the key.

    Default:
        false

    Stability:
        experimental
    """

    policy: aws_cdk.aws_iam.PolicyDocument
    """Custom policy document to attach to the KMS key.

    Default:
        - A policy document with permissions for the account root to
          administer the key will be created.

    Stability:
        experimental
    """

    removalPolicy: aws_cdk.cdk.RemovalPolicy
    """Whether the encryption key should be retained when it is removed from the Stack.

    This is useful when one wants to
    retain access to data that was encrypted with a key that is being retired.

    Default:
        RemovalPolicy.Retain

    Stability:
        experimental
    """

class ViaServicePrincipal(aws_cdk.aws_iam.PrincipalBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-kms.ViaServicePrincipal"):
    """A principal to allow access to a key if it's being used through another AWS service.

    Stability:
        experimental
    """
    def __init__(self, service_name: str, base_principal: typing.Optional[aws_cdk.aws_iam.IPrincipal]=None) -> None:
        """
        Arguments:
            serviceName: -
            basePrincipal: -

        Stability:
            experimental
        """
        jsii.create(ViaServicePrincipal, self, [service_name, base_principal])

    @property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> aws_cdk.aws_iam.PrincipalPolicyFragment:
        """Return the policy fragment that identifies this principal in a Policy.

        Stability:
            experimental
        """
        return jsii.get(self, "policyFragment")


__all__ = ["Alias", "AliasAttributes", "AliasProps", "CfnAlias", "CfnAliasProps", "CfnKey", "CfnKeyProps", "IAlias", "IKey", "Key", "KeyProps", "ViaServicePrincipal", "__jsii_assembly__"]

publication.publish()
