import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-ram", "0.36.0", __name__, "aws-ram@0.36.0.jsii.tgz")
class CfnResourceShare(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ram.CfnResourceShare"):
    """A CloudFormation ``AWS::RAM::ResourceShare``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html
    Stability:
        stable
    cloudformationResource:
        AWS::RAM::ResourceShare
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, allow_external_principals: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, principals: typing.Optional[typing.List[str]]=None, resource_arns: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::RAM::ResourceShare``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::RAM::ResourceShare.Name``.
            allow_external_principals: ``AWS::RAM::ResourceShare.AllowExternalPrincipals``.
            principals: ``AWS::RAM::ResourceShare.Principals``.
            resource_arns: ``AWS::RAM::ResourceShare.ResourceArns``.
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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::RAM::ResourceShare.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::RAM::ResourceShare.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="allowExternalPrincipals")
    def allow_external_principals(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RAM::ResourceShare.AllowExternalPrincipals``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-allowexternalprincipals
        Stability:
            stable
        """
        return jsii.get(self, "allowExternalPrincipals")

    @allow_external_principals.setter
    def allow_external_principals(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "allowExternalPrincipals", value)

    @property
    @jsii.member(jsii_name="principals")
    def principals(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RAM::ResourceShare.Principals``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-principals
        Stability:
            stable
        """
        return jsii.get(self, "principals")

    @principals.setter
    def principals(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "principals", value)

    @property
    @jsii.member(jsii_name="resourceArns")
    def resource_arns(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RAM::ResourceShare.ResourceArns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-resourcearns
        Stability:
            stable
        """
        return jsii.get(self, "resourceArns")

    @resource_arns.setter
    def resource_arns(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "resourceArns", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnResourceShareProps(jsii.compat.TypedDict, total=False):
    allowExternalPrincipals: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RAM::ResourceShare.AllowExternalPrincipals``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-allowexternalprincipals
    Stability:
        stable
    """
    principals: typing.List[str]
    """``AWS::RAM::ResourceShare.Principals``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-principals
    Stability:
        stable
    """
    resourceArns: typing.List[str]
    """``AWS::RAM::ResourceShare.ResourceArns``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-resourcearns
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::RAM::ResourceShare.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ram.CfnResourceShareProps", jsii_struct_bases=[_CfnResourceShareProps])
class CfnResourceShareProps(_CfnResourceShareProps):
    """Properties for defining a ``AWS::RAM::ResourceShare``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html
    Stability:
        stable
    """
    name: str
    """``AWS::RAM::ResourceShare.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-name
    Stability:
        stable
    """

__all__ = ["CfnResourceShare", "CfnResourceShareProps", "__jsii_assembly__"]

publication.publish()
