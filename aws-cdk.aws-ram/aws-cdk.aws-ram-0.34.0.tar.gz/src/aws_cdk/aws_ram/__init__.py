import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-ram", "0.34.0", __name__, "aws-ram@0.34.0.jsii.tgz")
class CfnResourceShare(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ram.CfnResourceShare"):
    """A CloudFormation ``AWS::RAM::ResourceShare``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RAM::ResourceShare
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, allow_external_principals: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, principals: typing.Optional[typing.List[str]]=None, resource_arns: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::RAM::ResourceShare``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::RAM::ResourceShare.Name``.
            allowExternalPrincipals: ``AWS::RAM::ResourceShare.AllowExternalPrincipals``.
            principals: ``AWS::RAM::ResourceShare.Principals``.
            resourceArns: ``AWS::RAM::ResourceShare.ResourceArns``.
            tags: ``AWS::RAM::ResourceShare.Tags``.

        Stability:
            experimental
        """
        props: CfnResourceShareProps = {"name": name}

        if allow_external_principals is not None:
            props["allowExternalPrincipals"] = allow_external_principals

        if principals is not None:
            props["principals"] = principals

        if resource_arns is not None:
            props["resourceArns"] = resource_arns

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnResourceShare, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnResourceShareProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="resourceShareArn")
    def resource_share_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "resourceShareArn")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """The ``TagManager`` handles setting, removing and formatting tags.

        Tags should be managed either passing them as properties during
        initiation or by calling methods on this object. If both techniques are
        used only the tags from the TagManager will be used. ``Tag`` (aspect)
        will use the manager.

        Stability:
            experimental
        """
        return jsii.get(self, "tags")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnResourceShareProps(jsii.compat.TypedDict, total=False):
    allowExternalPrincipals: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RAM::ResourceShare.AllowExternalPrincipals``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-allowexternalprincipals
    Stability:
        experimental
    """
    principals: typing.List[str]
    """``AWS::RAM::ResourceShare.Principals``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-principals
    Stability:
        experimental
    """
    resourceArns: typing.List[str]
    """``AWS::RAM::ResourceShare.ResourceArns``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-resourcearns
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::RAM::ResourceShare.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ram.CfnResourceShareProps", jsii_struct_bases=[_CfnResourceShareProps])
class CfnResourceShareProps(_CfnResourceShareProps):
    """Properties for defining a ``AWS::RAM::ResourceShare``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html
    Stability:
        experimental
    """
    name: str
    """``AWS::RAM::ResourceShare.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-name
    Stability:
        experimental
    """

__all__ = ["CfnResourceShare", "CfnResourceShareProps", "__jsii_assembly__"]

publication.publish()
