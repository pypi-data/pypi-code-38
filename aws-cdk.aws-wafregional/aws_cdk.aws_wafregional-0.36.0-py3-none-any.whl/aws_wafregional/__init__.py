import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-wafregional", "0.36.0", __name__, "aws-wafregional@0.36.0.jsii.tgz")
class CfnByteMatchSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnByteMatchSet"):
    """A CloudFormation ``AWS::WAFRegional::ByteMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html
    Stability:
        stable
    cloudformationResource:
        AWS::WAFRegional::ByteMatchSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, byte_match_tuples: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["ByteMatchTupleProperty", aws_cdk.core.IResolvable]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::ByteMatchSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::ByteMatchSet.Name``.
            byte_match_tuples: ``AWS::WAFRegional::ByteMatchSet.ByteMatchTuples``.

        Stability:
            experimental
        """
        props: CfnByteMatchSetProps = {"name": name}

        if byte_match_tuples is not None:
            props["byteMatchTuples"] = byte_match_tuples

        jsii.create(CfnByteMatchSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::ByteMatchSet.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html#cfn-wafregional-bytematchset-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="byteMatchTuples")
    def byte_match_tuples(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["ByteMatchTupleProperty", aws_cdk.core.IResolvable]]]]]:
        """``AWS::WAFRegional::ByteMatchSet.ByteMatchTuples``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html#cfn-wafregional-bytematchset-bytematchtuples
        Stability:
            stable
        """
        return jsii.get(self, "byteMatchTuples")

    @byte_match_tuples.setter
    def byte_match_tuples(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union["ByteMatchTupleProperty", aws_cdk.core.IResolvable]]]]]):
        return jsii.set(self, "byteMatchTuples", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ByteMatchTupleProperty(jsii.compat.TypedDict, total=False):
        targetString: str
        """``CfnByteMatchSet.ByteMatchTupleProperty.TargetString``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-targetstring
        Stability:
            stable
        """
        targetStringBase64: str
        """``CfnByteMatchSet.ByteMatchTupleProperty.TargetStringBase64``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-targetstringbase64
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnByteMatchSet.ByteMatchTupleProperty", jsii_struct_bases=[_ByteMatchTupleProperty])
    class ByteMatchTupleProperty(_ByteMatchTupleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html
        Stability:
            stable
        """
        fieldToMatch: typing.Union[aws_cdk.core.IResolvable, "CfnByteMatchSet.FieldToMatchProperty"]
        """``CfnByteMatchSet.ByteMatchTupleProperty.FieldToMatch``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-fieldtomatch
        Stability:
            stable
        """

        positionalConstraint: str
        """``CfnByteMatchSet.ByteMatchTupleProperty.PositionalConstraint``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-positionalconstraint
        Stability:
            stable
        """

        textTransformation: str
        """``CfnByteMatchSet.ByteMatchTupleProperty.TextTransformation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-texttransformation
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FieldToMatchProperty(jsii.compat.TypedDict, total=False):
        data: str
        """``CfnByteMatchSet.FieldToMatchProperty.Data``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-fieldtomatch.html#cfn-wafregional-bytematchset-fieldtomatch-data
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnByteMatchSet.FieldToMatchProperty", jsii_struct_bases=[_FieldToMatchProperty])
    class FieldToMatchProperty(_FieldToMatchProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-fieldtomatch.html
        Stability:
            stable
        """
        type: str
        """``CfnByteMatchSet.FieldToMatchProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-fieldtomatch.html#cfn-wafregional-bytematchset-fieldtomatch-type
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnByteMatchSetProps(jsii.compat.TypedDict, total=False):
    byteMatchTuples: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnByteMatchSet.ByteMatchTupleProperty", aws_cdk.core.IResolvable]]]
    """``AWS::WAFRegional::ByteMatchSet.ByteMatchTuples``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html#cfn-wafregional-bytematchset-bytematchtuples
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnByteMatchSetProps", jsii_struct_bases=[_CfnByteMatchSetProps])
class CfnByteMatchSetProps(_CfnByteMatchSetProps):
    """Properties for defining a ``AWS::WAFRegional::ByteMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html
    Stability:
        stable
    """
    name: str
    """``AWS::WAFRegional::ByteMatchSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html#cfn-wafregional-bytematchset-name
    Stability:
        stable
    """

class CfnGeoMatchSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnGeoMatchSet"):
    """A CloudFormation ``AWS::WAFRegional::GeoMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html
    Stability:
        stable
    cloudformationResource:
        AWS::WAFRegional::GeoMatchSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, geo_match_constraints: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "GeoMatchConstraintProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::GeoMatchSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::GeoMatchSet.Name``.
            geo_match_constraints: ``AWS::WAFRegional::GeoMatchSet.GeoMatchConstraints``.

        Stability:
            experimental
        """
        props: CfnGeoMatchSetProps = {"name": name}

        if geo_match_constraints is not None:
            props["geoMatchConstraints"] = geo_match_constraints

        jsii.create(CfnGeoMatchSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::GeoMatchSet.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html#cfn-wafregional-geomatchset-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="geoMatchConstraints")
    def geo_match_constraints(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "GeoMatchConstraintProperty"]]]]]:
        """``AWS::WAFRegional::GeoMatchSet.GeoMatchConstraints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html#cfn-wafregional-geomatchset-geomatchconstraints
        Stability:
            stable
        """
        return jsii.get(self, "geoMatchConstraints")

    @geo_match_constraints.setter
    def geo_match_constraints(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "GeoMatchConstraintProperty"]]]]]):
        return jsii.set(self, "geoMatchConstraints", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnGeoMatchSet.GeoMatchConstraintProperty", jsii_struct_bases=[])
    class GeoMatchConstraintProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-geomatchset-geomatchconstraint.html
        Stability:
            stable
        """
        type: str
        """``CfnGeoMatchSet.GeoMatchConstraintProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-geomatchset-geomatchconstraint.html#cfn-wafregional-geomatchset-geomatchconstraint-type
        Stability:
            stable
        """

        value: str
        """``CfnGeoMatchSet.GeoMatchConstraintProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-geomatchset-geomatchconstraint.html#cfn-wafregional-geomatchset-geomatchconstraint-value
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnGeoMatchSetProps(jsii.compat.TypedDict, total=False):
    geoMatchConstraints: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnGeoMatchSet.GeoMatchConstraintProperty"]]]
    """``AWS::WAFRegional::GeoMatchSet.GeoMatchConstraints``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html#cfn-wafregional-geomatchset-geomatchconstraints
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnGeoMatchSetProps", jsii_struct_bases=[_CfnGeoMatchSetProps])
class CfnGeoMatchSetProps(_CfnGeoMatchSetProps):
    """Properties for defining a ``AWS::WAFRegional::GeoMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html
    Stability:
        stable
    """
    name: str
    """``AWS::WAFRegional::GeoMatchSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html#cfn-wafregional-geomatchset-name
    Stability:
        stable
    """

class CfnIPSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnIPSet"):
    """A CloudFormation ``AWS::WAFRegional::IPSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html
    Stability:
        stable
    cloudformationResource:
        AWS::WAFRegional::IPSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, ip_set_descriptors: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "IPSetDescriptorProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::IPSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::IPSet.Name``.
            ip_set_descriptors: ``AWS::WAFRegional::IPSet.IPSetDescriptors``.

        Stability:
            experimental
        """
        props: CfnIPSetProps = {"name": name}

        if ip_set_descriptors is not None:
            props["ipSetDescriptors"] = ip_set_descriptors

        jsii.create(CfnIPSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::IPSet.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html#cfn-wafregional-ipset-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="ipSetDescriptors")
    def ip_set_descriptors(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "IPSetDescriptorProperty"]]]]]:
        """``AWS::WAFRegional::IPSet.IPSetDescriptors``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html#cfn-wafregional-ipset-ipsetdescriptors
        Stability:
            stable
        """
        return jsii.get(self, "ipSetDescriptors")

    @ip_set_descriptors.setter
    def ip_set_descriptors(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "IPSetDescriptorProperty"]]]]]):
        return jsii.set(self, "ipSetDescriptors", value)

    @jsii.interface(jsii_type="@aws-cdk/aws-wafregional.CfnIPSet.IPSetDescriptorProperty")
    class IPSetDescriptorProperty(jsii.compat.Protocol):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html
        Stability:
            stable
        """
        @staticmethod
        def __jsii_proxy_class__():
            return _IPSetDescriptorPropertyProxy

        @property
        @jsii.member(jsii_name="type")
        def type(self) -> str:
            """``CfnIPSet.IPSetDescriptorProperty.Type``.

            See:
                http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html#cfn-wafregional-ipset-ipsetdescriptor-type
            Stability:
                stable
            """
            ...

        @property
        @jsii.member(jsii_name="value")
        def value(self) -> str:
            """``CfnIPSet.IPSetDescriptorProperty.Value``.

            See:
                http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html#cfn-wafregional-ipset-ipsetdescriptor-value
            Stability:
                stable
            """
            ...


    class _IPSetDescriptorPropertyProxy():
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html
        Stability:
            stable
        """
        __jsii_type__ = "@aws-cdk/aws-wafregional.CfnIPSet.IPSetDescriptorProperty"
        @property
        @jsii.member(jsii_name="type")
        def type(self) -> str:
            """``CfnIPSet.IPSetDescriptorProperty.Type``.

            See:
                http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html#cfn-wafregional-ipset-ipsetdescriptor-type
            Stability:
                stable
            """
            return jsii.get(self, "type")

        @property
        @jsii.member(jsii_name="value")
        def value(self) -> str:
            """``CfnIPSet.IPSetDescriptorProperty.Value``.

            See:
                http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html#cfn-wafregional-ipset-ipsetdescriptor-value
            Stability:
                stable
            """
            return jsii.get(self, "value")



@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnIPSetProps(jsii.compat.TypedDict, total=False):
    ipSetDescriptors: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnIPSet.IPSetDescriptorProperty"]]]
    """``AWS::WAFRegional::IPSet.IPSetDescriptors``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html#cfn-wafregional-ipset-ipsetdescriptors
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnIPSetProps", jsii_struct_bases=[_CfnIPSetProps])
class CfnIPSetProps(_CfnIPSetProps):
    """Properties for defining a ``AWS::WAFRegional::IPSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html
    Stability:
        stable
    """
    name: str
    """``AWS::WAFRegional::IPSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html#cfn-wafregional-ipset-name
    Stability:
        stable
    """

class CfnRateBasedRule(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnRateBasedRule"):
    """A CloudFormation ``AWS::WAFRegional::RateBasedRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html
    Stability:
        stable
    cloudformationResource:
        AWS::WAFRegional::RateBasedRule
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, metric_name: str, name: str, rate_key: str, rate_limit: jsii.Number, match_predicates: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PredicateProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::RateBasedRule``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            metric_name: ``AWS::WAFRegional::RateBasedRule.MetricName``.
            name: ``AWS::WAFRegional::RateBasedRule.Name``.
            rate_key: ``AWS::WAFRegional::RateBasedRule.RateKey``.
            rate_limit: ``AWS::WAFRegional::RateBasedRule.RateLimit``.
            match_predicates: ``AWS::WAFRegional::RateBasedRule.MatchPredicates``.

        Stability:
            experimental
        """
        props: CfnRateBasedRuleProps = {"metricName": metric_name, "name": name, "rateKey": rate_key, "rateLimit": rate_limit}

        if match_predicates is not None:
            props["matchPredicates"] = match_predicates

        jsii.create(CfnRateBasedRule, self, [scope, id, props])

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
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> str:
        """``AWS::WAFRegional::RateBasedRule.MetricName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-metricname
        Stability:
            stable
        """
        return jsii.get(self, "metricName")

    @metric_name.setter
    def metric_name(self, value: str):
        return jsii.set(self, "metricName", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::RateBasedRule.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="rateKey")
    def rate_key(self) -> str:
        """``AWS::WAFRegional::RateBasedRule.RateKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-ratekey
        Stability:
            stable
        """
        return jsii.get(self, "rateKey")

    @rate_key.setter
    def rate_key(self, value: str):
        return jsii.set(self, "rateKey", value)

    @property
    @jsii.member(jsii_name="rateLimit")
    def rate_limit(self) -> jsii.Number:
        """``AWS::WAFRegional::RateBasedRule.RateLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-ratelimit
        Stability:
            stable
        """
        return jsii.get(self, "rateLimit")

    @rate_limit.setter
    def rate_limit(self, value: jsii.Number):
        return jsii.set(self, "rateLimit", value)

    @property
    @jsii.member(jsii_name="matchPredicates")
    def match_predicates(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PredicateProperty"]]]]]:
        """``AWS::WAFRegional::RateBasedRule.MatchPredicates``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-matchpredicates
        Stability:
            stable
        """
        return jsii.get(self, "matchPredicates")

    @match_predicates.setter
    def match_predicates(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PredicateProperty"]]]]]):
        return jsii.set(self, "matchPredicates", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRateBasedRule.PredicateProperty", jsii_struct_bases=[])
    class PredicateProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ratebasedrule-predicate.html
        Stability:
            stable
        """
        dataId: str
        """``CfnRateBasedRule.PredicateProperty.DataId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ratebasedrule-predicate.html#cfn-wafregional-ratebasedrule-predicate-dataid
        Stability:
            stable
        """

        negated: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnRateBasedRule.PredicateProperty.Negated``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ratebasedrule-predicate.html#cfn-wafregional-ratebasedrule-predicate-negated
        Stability:
            stable
        """

        type: str
        """``CfnRateBasedRule.PredicateProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ratebasedrule-predicate.html#cfn-wafregional-ratebasedrule-predicate-type
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRateBasedRuleProps(jsii.compat.TypedDict, total=False):
    matchPredicates: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRateBasedRule.PredicateProperty"]]]
    """``AWS::WAFRegional::RateBasedRule.MatchPredicates``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-matchpredicates
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRateBasedRuleProps", jsii_struct_bases=[_CfnRateBasedRuleProps])
class CfnRateBasedRuleProps(_CfnRateBasedRuleProps):
    """Properties for defining a ``AWS::WAFRegional::RateBasedRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html
    Stability:
        stable
    """
    metricName: str
    """``AWS::WAFRegional::RateBasedRule.MetricName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-metricname
    Stability:
        stable
    """

    name: str
    """``AWS::WAFRegional::RateBasedRule.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-name
    Stability:
        stable
    """

    rateKey: str
    """``AWS::WAFRegional::RateBasedRule.RateKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-ratekey
    Stability:
        stable
    """

    rateLimit: jsii.Number
    """``AWS::WAFRegional::RateBasedRule.RateLimit``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-ratelimit
    Stability:
        stable
    """

class CfnRegexPatternSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnRegexPatternSet"):
    """A CloudFormation ``AWS::WAFRegional::RegexPatternSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html
    Stability:
        stable
    cloudformationResource:
        AWS::WAFRegional::RegexPatternSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, regex_pattern_strings: typing.List[str]) -> None:
        """Create a new ``AWS::WAFRegional::RegexPatternSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::RegexPatternSet.Name``.
            regex_pattern_strings: ``AWS::WAFRegional::RegexPatternSet.RegexPatternStrings``.

        Stability:
            experimental
        """
        props: CfnRegexPatternSetProps = {"name": name, "regexPatternStrings": regex_pattern_strings}

        jsii.create(CfnRegexPatternSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::RegexPatternSet.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html#cfn-wafregional-regexpatternset-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="regexPatternStrings")
    def regex_pattern_strings(self) -> typing.List[str]:
        """``AWS::WAFRegional::RegexPatternSet.RegexPatternStrings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html#cfn-wafregional-regexpatternset-regexpatternstrings
        Stability:
            stable
        """
        return jsii.get(self, "regexPatternStrings")

    @regex_pattern_strings.setter
    def regex_pattern_strings(self, value: typing.List[str]):
        return jsii.set(self, "regexPatternStrings", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRegexPatternSetProps", jsii_struct_bases=[])
class CfnRegexPatternSetProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::WAFRegional::RegexPatternSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html
    Stability:
        stable
    """
    name: str
    """``AWS::WAFRegional::RegexPatternSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html#cfn-wafregional-regexpatternset-name
    Stability:
        stable
    """

    regexPatternStrings: typing.List[str]
    """``AWS::WAFRegional::RegexPatternSet.RegexPatternStrings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html#cfn-wafregional-regexpatternset-regexpatternstrings
    Stability:
        stable
    """

class CfnRule(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnRule"):
    """A CloudFormation ``AWS::WAFRegional::Rule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html
    Stability:
        stable
    cloudformationResource:
        AWS::WAFRegional::Rule
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, metric_name: str, name: str, predicates: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PredicateProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::Rule``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            metric_name: ``AWS::WAFRegional::Rule.MetricName``.
            name: ``AWS::WAFRegional::Rule.Name``.
            predicates: ``AWS::WAFRegional::Rule.Predicates``.

        Stability:
            experimental
        """
        props: CfnRuleProps = {"metricName": metric_name, "name": name}

        if predicates is not None:
            props["predicates"] = predicates

        jsii.create(CfnRule, self, [scope, id, props])

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
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> str:
        """``AWS::WAFRegional::Rule.MetricName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-metricname
        Stability:
            stable
        """
        return jsii.get(self, "metricName")

    @metric_name.setter
    def metric_name(self, value: str):
        return jsii.set(self, "metricName", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::Rule.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="predicates")
    def predicates(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PredicateProperty"]]]]]:
        """``AWS::WAFRegional::Rule.Predicates``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-predicates
        Stability:
            stable
        """
        return jsii.get(self, "predicates")

    @predicates.setter
    def predicates(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PredicateProperty"]]]]]):
        return jsii.set(self, "predicates", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRule.PredicateProperty", jsii_struct_bases=[])
    class PredicateProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-rule-predicate.html
        Stability:
            stable
        """
        dataId: str
        """``CfnRule.PredicateProperty.DataId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-rule-predicate.html#cfn-wafregional-rule-predicate-dataid
        Stability:
            stable
        """

        negated: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnRule.PredicateProperty.Negated``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-rule-predicate.html#cfn-wafregional-rule-predicate-negated
        Stability:
            stable
        """

        type: str
        """``CfnRule.PredicateProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-rule-predicate.html#cfn-wafregional-rule-predicate-type
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRuleProps(jsii.compat.TypedDict, total=False):
    predicates: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRule.PredicateProperty"]]]
    """``AWS::WAFRegional::Rule.Predicates``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-predicates
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRuleProps", jsii_struct_bases=[_CfnRuleProps])
class CfnRuleProps(_CfnRuleProps):
    """Properties for defining a ``AWS::WAFRegional::Rule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html
    Stability:
        stable
    """
    metricName: str
    """``AWS::WAFRegional::Rule.MetricName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-metricname
    Stability:
        stable
    """

    name: str
    """``AWS::WAFRegional::Rule.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-name
    Stability:
        stable
    """

class CfnSizeConstraintSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnSizeConstraintSet"):
    """A CloudFormation ``AWS::WAFRegional::SizeConstraintSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html
    Stability:
        stable
    cloudformationResource:
        AWS::WAFRegional::SizeConstraintSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, size_constraints: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SizeConstraintProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::SizeConstraintSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::SizeConstraintSet.Name``.
            size_constraints: ``AWS::WAFRegional::SizeConstraintSet.SizeConstraints``.

        Stability:
            experimental
        """
        props: CfnSizeConstraintSetProps = {"name": name}

        if size_constraints is not None:
            props["sizeConstraints"] = size_constraints

        jsii.create(CfnSizeConstraintSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::SizeConstraintSet.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html#cfn-wafregional-sizeconstraintset-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="sizeConstraints")
    def size_constraints(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SizeConstraintProperty"]]]]]:
        """``AWS::WAFRegional::SizeConstraintSet.SizeConstraints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html#cfn-wafregional-sizeconstraintset-sizeconstraints
        Stability:
            stable
        """
        return jsii.get(self, "sizeConstraints")

    @size_constraints.setter
    def size_constraints(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SizeConstraintProperty"]]]]]):
        return jsii.set(self, "sizeConstraints", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FieldToMatchProperty(jsii.compat.TypedDict, total=False):
        data: str
        """``CfnSizeConstraintSet.FieldToMatchProperty.Data``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-fieldtomatch.html#cfn-wafregional-sizeconstraintset-fieldtomatch-data
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSizeConstraintSet.FieldToMatchProperty", jsii_struct_bases=[_FieldToMatchProperty])
    class FieldToMatchProperty(_FieldToMatchProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-fieldtomatch.html
        Stability:
            stable
        """
        type: str
        """``CfnSizeConstraintSet.FieldToMatchProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-fieldtomatch.html#cfn-wafregional-sizeconstraintset-fieldtomatch-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSizeConstraintSet.SizeConstraintProperty", jsii_struct_bases=[])
    class SizeConstraintProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html
        Stability:
            stable
        """
        comparisonOperator: str
        """``CfnSizeConstraintSet.SizeConstraintProperty.ComparisonOperator``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html#cfn-wafregional-sizeconstraintset-sizeconstraint-comparisonoperator
        Stability:
            stable
        """

        fieldToMatch: typing.Union[aws_cdk.core.IResolvable, "CfnSizeConstraintSet.FieldToMatchProperty"]
        """``CfnSizeConstraintSet.SizeConstraintProperty.FieldToMatch``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html#cfn-wafregional-sizeconstraintset-sizeconstraint-fieldtomatch
        Stability:
            stable
        """

        size: jsii.Number
        """``CfnSizeConstraintSet.SizeConstraintProperty.Size``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html#cfn-wafregional-sizeconstraintset-sizeconstraint-size
        Stability:
            stable
        """

        textTransformation: str
        """``CfnSizeConstraintSet.SizeConstraintProperty.TextTransformation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html#cfn-wafregional-sizeconstraintset-sizeconstraint-texttransformation
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSizeConstraintSetProps(jsii.compat.TypedDict, total=False):
    sizeConstraints: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSizeConstraintSet.SizeConstraintProperty"]]]
    """``AWS::WAFRegional::SizeConstraintSet.SizeConstraints``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html#cfn-wafregional-sizeconstraintset-sizeconstraints
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSizeConstraintSetProps", jsii_struct_bases=[_CfnSizeConstraintSetProps])
class CfnSizeConstraintSetProps(_CfnSizeConstraintSetProps):
    """Properties for defining a ``AWS::WAFRegional::SizeConstraintSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html
    Stability:
        stable
    """
    name: str
    """``AWS::WAFRegional::SizeConstraintSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html#cfn-wafregional-sizeconstraintset-name
    Stability:
        stable
    """

class CfnSqlInjectionMatchSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnSqlInjectionMatchSet"):
    """A CloudFormation ``AWS::WAFRegional::SqlInjectionMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html
    Stability:
        stable
    cloudformationResource:
        AWS::WAFRegional::SqlInjectionMatchSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, sql_injection_match_tuples: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SqlInjectionMatchTupleProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::SqlInjectionMatchSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::SqlInjectionMatchSet.Name``.
            sql_injection_match_tuples: ``AWS::WAFRegional::SqlInjectionMatchSet.SqlInjectionMatchTuples``.

        Stability:
            experimental
        """
        props: CfnSqlInjectionMatchSetProps = {"name": name}

        if sql_injection_match_tuples is not None:
            props["sqlInjectionMatchTuples"] = sql_injection_match_tuples

        jsii.create(CfnSqlInjectionMatchSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::SqlInjectionMatchSet.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html#cfn-wafregional-sqlinjectionmatchset-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="sqlInjectionMatchTuples")
    def sql_injection_match_tuples(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SqlInjectionMatchTupleProperty"]]]]]:
        """``AWS::WAFRegional::SqlInjectionMatchSet.SqlInjectionMatchTuples``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html#cfn-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuples
        Stability:
            stable
        """
        return jsii.get(self, "sqlInjectionMatchTuples")

    @sql_injection_match_tuples.setter
    def sql_injection_match_tuples(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "SqlInjectionMatchTupleProperty"]]]]]):
        return jsii.set(self, "sqlInjectionMatchTuples", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FieldToMatchProperty(jsii.compat.TypedDict, total=False):
        data: str
        """``CfnSqlInjectionMatchSet.FieldToMatchProperty.Data``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-fieldtomatch.html#cfn-wafregional-sqlinjectionmatchset-fieldtomatch-data
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSqlInjectionMatchSet.FieldToMatchProperty", jsii_struct_bases=[_FieldToMatchProperty])
    class FieldToMatchProperty(_FieldToMatchProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-fieldtomatch.html
        Stability:
            stable
        """
        type: str
        """``CfnSqlInjectionMatchSet.FieldToMatchProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-fieldtomatch.html#cfn-wafregional-sqlinjectionmatchset-fieldtomatch-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty", jsii_struct_bases=[])
    class SqlInjectionMatchTupleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple.html
        Stability:
            stable
        """
        fieldToMatch: typing.Union[aws_cdk.core.IResolvable, "CfnSqlInjectionMatchSet.FieldToMatchProperty"]
        """``CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty.FieldToMatch``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple.html#cfn-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple-fieldtomatch
        Stability:
            stable
        """

        textTransformation: str
        """``CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty.TextTransformation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple.html#cfn-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple-texttransformation
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSqlInjectionMatchSetProps(jsii.compat.TypedDict, total=False):
    sqlInjectionMatchTuples: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty"]]]
    """``AWS::WAFRegional::SqlInjectionMatchSet.SqlInjectionMatchTuples``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html#cfn-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuples
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSqlInjectionMatchSetProps", jsii_struct_bases=[_CfnSqlInjectionMatchSetProps])
class CfnSqlInjectionMatchSetProps(_CfnSqlInjectionMatchSetProps):
    """Properties for defining a ``AWS::WAFRegional::SqlInjectionMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html
    Stability:
        stable
    """
    name: str
    """``AWS::WAFRegional::SqlInjectionMatchSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html#cfn-wafregional-sqlinjectionmatchset-name
    Stability:
        stable
    """

class CfnWebACL(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnWebACL"):
    """A CloudFormation ``AWS::WAFRegional::WebACL``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html
    Stability:
        stable
    cloudformationResource:
        AWS::WAFRegional::WebACL
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, default_action: typing.Union[aws_cdk.core.IResolvable, "ActionProperty"], metric_name: str, name: str, rules: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "RuleProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::WebACL``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            default_action: ``AWS::WAFRegional::WebACL.DefaultAction``.
            metric_name: ``AWS::WAFRegional::WebACL.MetricName``.
            name: ``AWS::WAFRegional::WebACL.Name``.
            rules: ``AWS::WAFRegional::WebACL.Rules``.

        Stability:
            experimental
        """
        props: CfnWebACLProps = {"defaultAction": default_action, "metricName": metric_name, "name": name}

        if rules is not None:
            props["rules"] = rules

        jsii.create(CfnWebACL, self, [scope, id, props])

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
    @jsii.member(jsii_name="defaultAction")
    def default_action(self) -> typing.Union[aws_cdk.core.IResolvable, "ActionProperty"]:
        """``AWS::WAFRegional::WebACL.DefaultAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-defaultaction
        Stability:
            stable
        """
        return jsii.get(self, "defaultAction")

    @default_action.setter
    def default_action(self, value: typing.Union[aws_cdk.core.IResolvable, "ActionProperty"]):
        return jsii.set(self, "defaultAction", value)

    @property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> str:
        """``AWS::WAFRegional::WebACL.MetricName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-metricname
        Stability:
            stable
        """
        return jsii.get(self, "metricName")

    @metric_name.setter
    def metric_name(self, value: str):
        return jsii.set(self, "metricName", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::WebACL.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "RuleProperty"]]]]]:
        """``AWS::WAFRegional::WebACL.Rules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-rules
        Stability:
            stable
        """
        return jsii.get(self, "rules")

    @rules.setter
    def rules(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "RuleProperty"]]]]]):
        return jsii.set(self, "rules", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnWebACL.ActionProperty", jsii_struct_bases=[])
    class ActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-action.html
        Stability:
            stable
        """
        type: str
        """``CfnWebACL.ActionProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-action.html#cfn-wafregional-webacl-action-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnWebACL.RuleProperty", jsii_struct_bases=[])
    class RuleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-rule.html
        Stability:
            stable
        """
        action: typing.Union[aws_cdk.core.IResolvable, "CfnWebACL.ActionProperty"]
        """``CfnWebACL.RuleProperty.Action``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-rule.html#cfn-wafregional-webacl-rule-action
        Stability:
            stable
        """

        priority: jsii.Number
        """``CfnWebACL.RuleProperty.Priority``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-rule.html#cfn-wafregional-webacl-rule-priority
        Stability:
            stable
        """

        ruleId: str
        """``CfnWebACL.RuleProperty.RuleId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-rule.html#cfn-wafregional-webacl-rule-ruleid
        Stability:
            stable
        """


class CfnWebACLAssociation(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnWebACLAssociation"):
    """A CloudFormation ``AWS::WAFRegional::WebACLAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html
    Stability:
        stable
    cloudformationResource:
        AWS::WAFRegional::WebACLAssociation
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, resource_arn: str, web_acl_id: str) -> None:
        """Create a new ``AWS::WAFRegional::WebACLAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            resource_arn: ``AWS::WAFRegional::WebACLAssociation.ResourceArn``.
            web_acl_id: ``AWS::WAFRegional::WebACLAssociation.WebACLId``.

        Stability:
            experimental
        """
        props: CfnWebACLAssociationProps = {"resourceArn": resource_arn, "webAclId": web_acl_id}

        jsii.create(CfnWebACLAssociation, self, [scope, id, props])

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
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> str:
        """``AWS::WAFRegional::WebACLAssociation.ResourceArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html#cfn-wafregional-webaclassociation-resourcearn
        Stability:
            stable
        """
        return jsii.get(self, "resourceArn")

    @resource_arn.setter
    def resource_arn(self, value: str):
        return jsii.set(self, "resourceArn", value)

    @property
    @jsii.member(jsii_name="webAclId")
    def web_acl_id(self) -> str:
        """``AWS::WAFRegional::WebACLAssociation.WebACLId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html#cfn-wafregional-webaclassociation-webaclid
        Stability:
            stable
        """
        return jsii.get(self, "webAclId")

    @web_acl_id.setter
    def web_acl_id(self, value: str):
        return jsii.set(self, "webAclId", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnWebACLAssociationProps", jsii_struct_bases=[])
class CfnWebACLAssociationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::WAFRegional::WebACLAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html
    Stability:
        stable
    """
    resourceArn: str
    """``AWS::WAFRegional::WebACLAssociation.ResourceArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html#cfn-wafregional-webaclassociation-resourcearn
    Stability:
        stable
    """

    webAclId: str
    """``AWS::WAFRegional::WebACLAssociation.WebACLId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html#cfn-wafregional-webaclassociation-webaclid
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnWebACLProps(jsii.compat.TypedDict, total=False):
    rules: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnWebACL.RuleProperty"]]]
    """``AWS::WAFRegional::WebACL.Rules``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-rules
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnWebACLProps", jsii_struct_bases=[_CfnWebACLProps])
class CfnWebACLProps(_CfnWebACLProps):
    """Properties for defining a ``AWS::WAFRegional::WebACL``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html
    Stability:
        stable
    """
    defaultAction: typing.Union[aws_cdk.core.IResolvable, "CfnWebACL.ActionProperty"]
    """``AWS::WAFRegional::WebACL.DefaultAction``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-defaultaction
    Stability:
        stable
    """

    metricName: str
    """``AWS::WAFRegional::WebACL.MetricName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-metricname
    Stability:
        stable
    """

    name: str
    """``AWS::WAFRegional::WebACL.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-name
    Stability:
        stable
    """

class CfnXssMatchSet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnXssMatchSet"):
    """A CloudFormation ``AWS::WAFRegional::XssMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html
    Stability:
        stable
    cloudformationResource:
        AWS::WAFRegional::XssMatchSet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, xss_match_tuples: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "XssMatchTupleProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::XssMatchSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::XssMatchSet.Name``.
            xss_match_tuples: ``AWS::WAFRegional::XssMatchSet.XssMatchTuples``.

        Stability:
            experimental
        """
        props: CfnXssMatchSetProps = {"name": name}

        if xss_match_tuples is not None:
            props["xssMatchTuples"] = xss_match_tuples

        jsii.create(CfnXssMatchSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::WAFRegional::XssMatchSet.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html#cfn-wafregional-xssmatchset-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="xssMatchTuples")
    def xss_match_tuples(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "XssMatchTupleProperty"]]]]]:
        """``AWS::WAFRegional::XssMatchSet.XssMatchTuples``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html#cfn-wafregional-xssmatchset-xssmatchtuples
        Stability:
            stable
        """
        return jsii.get(self, "xssMatchTuples")

    @xss_match_tuples.setter
    def xss_match_tuples(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "XssMatchTupleProperty"]]]]]):
        return jsii.set(self, "xssMatchTuples", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FieldToMatchProperty(jsii.compat.TypedDict, total=False):
        data: str
        """``CfnXssMatchSet.FieldToMatchProperty.Data``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-fieldtomatch.html#cfn-wafregional-xssmatchset-fieldtomatch-data
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnXssMatchSet.FieldToMatchProperty", jsii_struct_bases=[_FieldToMatchProperty])
    class FieldToMatchProperty(_FieldToMatchProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-fieldtomatch.html
        Stability:
            stable
        """
        type: str
        """``CfnXssMatchSet.FieldToMatchProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-fieldtomatch.html#cfn-wafregional-xssmatchset-fieldtomatch-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnXssMatchSet.XssMatchTupleProperty", jsii_struct_bases=[])
    class XssMatchTupleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-xssmatchtuple.html
        Stability:
            stable
        """
        fieldToMatch: typing.Union[aws_cdk.core.IResolvable, "CfnXssMatchSet.FieldToMatchProperty"]
        """``CfnXssMatchSet.XssMatchTupleProperty.FieldToMatch``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-xssmatchtuple.html#cfn-wafregional-xssmatchset-xssmatchtuple-fieldtomatch
        Stability:
            stable
        """

        textTransformation: str
        """``CfnXssMatchSet.XssMatchTupleProperty.TextTransformation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-xssmatchtuple.html#cfn-wafregional-xssmatchset-xssmatchtuple-texttransformation
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnXssMatchSetProps(jsii.compat.TypedDict, total=False):
    xssMatchTuples: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnXssMatchSet.XssMatchTupleProperty"]]]
    """``AWS::WAFRegional::XssMatchSet.XssMatchTuples``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html#cfn-wafregional-xssmatchset-xssmatchtuples
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnXssMatchSetProps", jsii_struct_bases=[_CfnXssMatchSetProps])
class CfnXssMatchSetProps(_CfnXssMatchSetProps):
    """Properties for defining a ``AWS::WAFRegional::XssMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html
    Stability:
        stable
    """
    name: str
    """``AWS::WAFRegional::XssMatchSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html#cfn-wafregional-xssmatchset-name
    Stability:
        stable
    """

__all__ = ["CfnByteMatchSet", "CfnByteMatchSetProps", "CfnGeoMatchSet", "CfnGeoMatchSetProps", "CfnIPSet", "CfnIPSetProps", "CfnRateBasedRule", "CfnRateBasedRuleProps", "CfnRegexPatternSet", "CfnRegexPatternSetProps", "CfnRule", "CfnRuleProps", "CfnSizeConstraintSet", "CfnSizeConstraintSetProps", "CfnSqlInjectionMatchSet", "CfnSqlInjectionMatchSetProps", "CfnWebACL", "CfnWebACLAssociation", "CfnWebACLAssociationProps", "CfnWebACLProps", "CfnXssMatchSet", "CfnXssMatchSetProps", "__jsii_assembly__"]

publication.publish()
