import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-athena", "0.34.0", __name__, "aws-athena@0.34.0.jsii.tgz")
class CfnNamedQuery(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-athena.CfnNamedQuery"):
    """A CloudFormation ``AWS::Athena::NamedQuery``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Athena::NamedQuery
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, database: str, query_string: str, description: typing.Optional[str]=None, name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Athena::NamedQuery``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            database: ``AWS::Athena::NamedQuery.Database``.
            queryString: ``AWS::Athena::NamedQuery.QueryString``.
            description: ``AWS::Athena::NamedQuery.Description``.
            name: ``AWS::Athena::NamedQuery.Name``.

        Stability:
            experimental
        """
        props: CfnNamedQueryProps = {"database": database, "queryString": query_string}

        if description is not None:
            props["description"] = description

        if name is not None:
            props["name"] = name

        jsii.create(CfnNamedQuery, self, [scope, id, props])

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
    @jsii.member(jsii_name="namedQueryName")
    def named_query_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "namedQueryName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnNamedQueryProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnNamedQueryProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::Athena::NamedQuery.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-description
    Stability:
        experimental
    """
    name: str
    """``AWS::Athena::NamedQuery.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-name
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-athena.CfnNamedQueryProps", jsii_struct_bases=[_CfnNamedQueryProps])
class CfnNamedQueryProps(_CfnNamedQueryProps):
    """Properties for defining a ``AWS::Athena::NamedQuery``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html
    Stability:
        experimental
    """
    database: str
    """``AWS::Athena::NamedQuery.Database``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-database
    Stability:
        experimental
    """

    queryString: str
    """``AWS::Athena::NamedQuery.QueryString``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-querystring
    Stability:
        experimental
    """

__all__ = ["CfnNamedQuery", "CfnNamedQueryProps", "__jsii_assembly__"]

publication.publish()
