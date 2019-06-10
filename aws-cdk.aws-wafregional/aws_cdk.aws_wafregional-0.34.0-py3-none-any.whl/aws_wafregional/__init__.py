import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-wafregional", "0.34.0", __name__, "aws-wafregional@0.34.0.jsii.tgz")
class CfnByteMatchSet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnByteMatchSet"):
    """A CloudFormation ``AWS::WAFRegional::ByteMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html
    Stability:
        experimental
    cloudformationResource:
        AWS::WAFRegional::ByteMatchSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, byte_match_tuples: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union["ByteMatchTupleProperty", aws_cdk.cdk.Token]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::ByteMatchSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::ByteMatchSet.Name``.
            byteMatchTuples: ``AWS::WAFRegional::ByteMatchSet.ByteMatchTuples``.

        Stability:
            experimental
        """
        props: CfnByteMatchSetProps = {"name": name}

        if byte_match_tuples is not None:
            props["byteMatchTuples"] = byte_match_tuples

        jsii.create(CfnByteMatchSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="byteMatchSetId")
    def byte_match_set_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "byteMatchSetId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnByteMatchSetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ByteMatchTupleProperty(jsii.compat.TypedDict, total=False):
        targetString: str
        """``CfnByteMatchSet.ByteMatchTupleProperty.TargetString``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-targetstring
        Stability:
            experimental
        """
        targetStringBase64: str
        """``CfnByteMatchSet.ByteMatchTupleProperty.TargetStringBase64``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-targetstringbase64
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnByteMatchSet.ByteMatchTupleProperty", jsii_struct_bases=[_ByteMatchTupleProperty])
    class ByteMatchTupleProperty(_ByteMatchTupleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html
        Stability:
            experimental
        """
        fieldToMatch: typing.Union[aws_cdk.cdk.Token, "CfnByteMatchSet.FieldToMatchProperty"]
        """``CfnByteMatchSet.ByteMatchTupleProperty.FieldToMatch``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-fieldtomatch
        Stability:
            experimental
        """

        positionalConstraint: str
        """``CfnByteMatchSet.ByteMatchTupleProperty.PositionalConstraint``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-positionalconstraint
        Stability:
            experimental
        """

        textTransformation: str
        """``CfnByteMatchSet.ByteMatchTupleProperty.TextTransformation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-bytematchtuple.html#cfn-wafregional-bytematchset-bytematchtuple-texttransformation
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FieldToMatchProperty(jsii.compat.TypedDict, total=False):
        data: str
        """``CfnByteMatchSet.FieldToMatchProperty.Data``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-fieldtomatch.html#cfn-wafregional-bytematchset-fieldtomatch-data
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnByteMatchSet.FieldToMatchProperty", jsii_struct_bases=[_FieldToMatchProperty])
    class FieldToMatchProperty(_FieldToMatchProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-fieldtomatch.html
        Stability:
            experimental
        """
        type: str
        """``CfnByteMatchSet.FieldToMatchProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-bytematchset-fieldtomatch.html#cfn-wafregional-bytematchset-fieldtomatch-type
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnByteMatchSetProps(jsii.compat.TypedDict, total=False):
    byteMatchTuples: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnByteMatchSet.ByteMatchTupleProperty", aws_cdk.cdk.Token]]]
    """``AWS::WAFRegional::ByteMatchSet.ByteMatchTuples``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html#cfn-wafregional-bytematchset-bytematchtuples
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnByteMatchSetProps", jsii_struct_bases=[_CfnByteMatchSetProps])
class CfnByteMatchSetProps(_CfnByteMatchSetProps):
    """Properties for defining a ``AWS::WAFRegional::ByteMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html
    Stability:
        experimental
    """
    name: str
    """``AWS::WAFRegional::ByteMatchSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-bytematchset.html#cfn-wafregional-bytematchset-name
    Stability:
        experimental
    """

class CfnGeoMatchSet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnGeoMatchSet"):
    """A CloudFormation ``AWS::WAFRegional::GeoMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html
    Stability:
        experimental
    cloudformationResource:
        AWS::WAFRegional::GeoMatchSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, geo_match_constraints: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "GeoMatchConstraintProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::GeoMatchSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::GeoMatchSet.Name``.
            geoMatchConstraints: ``AWS::WAFRegional::GeoMatchSet.GeoMatchConstraints``.

        Stability:
            experimental
        """
        props: CfnGeoMatchSetProps = {"name": name}

        if geo_match_constraints is not None:
            props["geoMatchConstraints"] = geo_match_constraints

        jsii.create(CfnGeoMatchSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="geoMatchSetId")
    def geo_match_set_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "geoMatchSetId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnGeoMatchSetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnGeoMatchSet.GeoMatchConstraintProperty", jsii_struct_bases=[])
    class GeoMatchConstraintProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-geomatchset-geomatchconstraint.html
        Stability:
            experimental
        """
        type: str
        """``CfnGeoMatchSet.GeoMatchConstraintProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-geomatchset-geomatchconstraint.html#cfn-wafregional-geomatchset-geomatchconstraint-type
        Stability:
            experimental
        """

        value: str
        """``CfnGeoMatchSet.GeoMatchConstraintProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-geomatchset-geomatchconstraint.html#cfn-wafregional-geomatchset-geomatchconstraint-value
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnGeoMatchSetProps(jsii.compat.TypedDict, total=False):
    geoMatchConstraints: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnGeoMatchSet.GeoMatchConstraintProperty"]]]
    """``AWS::WAFRegional::GeoMatchSet.GeoMatchConstraints``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html#cfn-wafregional-geomatchset-geomatchconstraints
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnGeoMatchSetProps", jsii_struct_bases=[_CfnGeoMatchSetProps])
class CfnGeoMatchSetProps(_CfnGeoMatchSetProps):
    """Properties for defining a ``AWS::WAFRegional::GeoMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html
    Stability:
        experimental
    """
    name: str
    """``AWS::WAFRegional::GeoMatchSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-geomatchset.html#cfn-wafregional-geomatchset-name
    Stability:
        experimental
    """

class CfnIPSet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnIPSet"):
    """A CloudFormation ``AWS::WAFRegional::IPSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html
    Stability:
        experimental
    cloudformationResource:
        AWS::WAFRegional::IPSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, ip_set_descriptors: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "IPSetDescriptorProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::IPSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::IPSet.Name``.
            ipSetDescriptors: ``AWS::WAFRegional::IPSet.IPSetDescriptors``.

        Stability:
            experimental
        """
        props: CfnIPSetProps = {"name": name}

        if ip_set_descriptors is not None:
            props["ipSetDescriptors"] = ip_set_descriptors

        jsii.create(CfnIPSet, self, [scope, id, props])

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
    @jsii.member(jsii_name="ipSetId")
    def ip_set_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "ipSetId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnIPSetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.interface(jsii_type="@aws-cdk/aws-wafregional.CfnIPSet.IPSetDescriptorProperty")
    class IPSetDescriptorProperty(jsii.compat.Protocol):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html
        Stability:
            experimental
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
                experimental
            """
            ...

        @property
        @jsii.member(jsii_name="value")
        def value(self) -> str:
            """``CfnIPSet.IPSetDescriptorProperty.Value``.

            See:
                http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html#cfn-wafregional-ipset-ipsetdescriptor-value
            Stability:
                experimental
            """
            ...


    class _IPSetDescriptorPropertyProxy():
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html
        Stability:
            experimental
        """
        __jsii_type__ = "@aws-cdk/aws-wafregional.CfnIPSet.IPSetDescriptorProperty"
        @property
        @jsii.member(jsii_name="type")
        def type(self) -> str:
            """``CfnIPSet.IPSetDescriptorProperty.Type``.

            See:
                http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html#cfn-wafregional-ipset-ipsetdescriptor-type
            Stability:
                experimental
            """
            return jsii.get(self, "type")

        @property
        @jsii.member(jsii_name="value")
        def value(self) -> str:
            """``CfnIPSet.IPSetDescriptorProperty.Value``.

            See:
                http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ipset-ipsetdescriptor.html#cfn-wafregional-ipset-ipsetdescriptor-value
            Stability:
                experimental
            """
            return jsii.get(self, "value")



@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnIPSetProps(jsii.compat.TypedDict, total=False):
    ipSetDescriptors: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnIPSet.IPSetDescriptorProperty"]]]
    """``AWS::WAFRegional::IPSet.IPSetDescriptors``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html#cfn-wafregional-ipset-ipsetdescriptors
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnIPSetProps", jsii_struct_bases=[_CfnIPSetProps])
class CfnIPSetProps(_CfnIPSetProps):
    """Properties for defining a ``AWS::WAFRegional::IPSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html
    Stability:
        experimental
    """
    name: str
    """``AWS::WAFRegional::IPSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ipset.html#cfn-wafregional-ipset-name
    Stability:
        experimental
    """

class CfnRateBasedRule(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnRateBasedRule"):
    """A CloudFormation ``AWS::WAFRegional::RateBasedRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html
    Stability:
        experimental
    cloudformationResource:
        AWS::WAFRegional::RateBasedRule
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, metric_name: str, name: str, rate_key: str, rate_limit: typing.Union[jsii.Number, aws_cdk.cdk.Token], match_predicates: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "PredicateProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::RateBasedRule``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            metricName: ``AWS::WAFRegional::RateBasedRule.MetricName``.
            name: ``AWS::WAFRegional::RateBasedRule.Name``.
            rateKey: ``AWS::WAFRegional::RateBasedRule.RateKey``.
            rateLimit: ``AWS::WAFRegional::RateBasedRule.RateLimit``.
            matchPredicates: ``AWS::WAFRegional::RateBasedRule.MatchPredicates``.

        Stability:
            experimental
        """
        props: CfnRateBasedRuleProps = {"metricName": metric_name, "name": name, "rateKey": rate_key, "rateLimit": rate_limit}

        if match_predicates is not None:
            props["matchPredicates"] = match_predicates

        jsii.create(CfnRateBasedRule, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnRateBasedRuleProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="rateBasedRuleId")
    def rate_based_rule_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "rateBasedRuleId")

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRateBasedRule.PredicateProperty", jsii_struct_bases=[])
    class PredicateProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ratebasedrule-predicate.html
        Stability:
            experimental
        """
        dataId: str
        """``CfnRateBasedRule.PredicateProperty.DataId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ratebasedrule-predicate.html#cfn-wafregional-ratebasedrule-predicate-dataid
        Stability:
            experimental
        """

        negated: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnRateBasedRule.PredicateProperty.Negated``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ratebasedrule-predicate.html#cfn-wafregional-ratebasedrule-predicate-negated
        Stability:
            experimental
        """

        type: str
        """``CfnRateBasedRule.PredicateProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-ratebasedrule-predicate.html#cfn-wafregional-ratebasedrule-predicate-type
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRateBasedRuleProps(jsii.compat.TypedDict, total=False):
    matchPredicates: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnRateBasedRule.PredicateProperty"]]]
    """``AWS::WAFRegional::RateBasedRule.MatchPredicates``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-matchpredicates
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRateBasedRuleProps", jsii_struct_bases=[_CfnRateBasedRuleProps])
class CfnRateBasedRuleProps(_CfnRateBasedRuleProps):
    """Properties for defining a ``AWS::WAFRegional::RateBasedRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html
    Stability:
        experimental
    """
    metricName: str
    """``AWS::WAFRegional::RateBasedRule.MetricName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-metricname
    Stability:
        experimental
    """

    name: str
    """``AWS::WAFRegional::RateBasedRule.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-name
    Stability:
        experimental
    """

    rateKey: str
    """``AWS::WAFRegional::RateBasedRule.RateKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-ratekey
    Stability:
        experimental
    """

    rateLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::WAFRegional::RateBasedRule.RateLimit``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-ratebasedrule.html#cfn-wafregional-ratebasedrule-ratelimit
    Stability:
        experimental
    """

class CfnRegexPatternSet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnRegexPatternSet"):
    """A CloudFormation ``AWS::WAFRegional::RegexPatternSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html
    Stability:
        experimental
    cloudformationResource:
        AWS::WAFRegional::RegexPatternSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, regex_pattern_strings: typing.List[str]) -> None:
        """Create a new ``AWS::WAFRegional::RegexPatternSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::RegexPatternSet.Name``.
            regexPatternStrings: ``AWS::WAFRegional::RegexPatternSet.RegexPatternStrings``.

        Stability:
            experimental
        """
        props: CfnRegexPatternSetProps = {"name": name, "regexPatternStrings": regex_pattern_strings}

        jsii.create(CfnRegexPatternSet, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnRegexPatternSetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="regexPatternSetId")
    def regex_pattern_set_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "regexPatternSetId")


@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRegexPatternSetProps", jsii_struct_bases=[])
class CfnRegexPatternSetProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::WAFRegional::RegexPatternSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html
    Stability:
        experimental
    """
    name: str
    """``AWS::WAFRegional::RegexPatternSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html#cfn-wafregional-regexpatternset-name
    Stability:
        experimental
    """

    regexPatternStrings: typing.List[str]
    """``AWS::WAFRegional::RegexPatternSet.RegexPatternStrings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-regexpatternset.html#cfn-wafregional-regexpatternset-regexpatternstrings
    Stability:
        experimental
    """

class CfnRule(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnRule"):
    """A CloudFormation ``AWS::WAFRegional::Rule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html
    Stability:
        experimental
    cloudformationResource:
        AWS::WAFRegional::Rule
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, metric_name: str, name: str, predicates: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "PredicateProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::Rule``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            metricName: ``AWS::WAFRegional::Rule.MetricName``.
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
    def property_overrides(self) -> "CfnRuleProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="ruleId")
    def rule_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "ruleId")

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRule.PredicateProperty", jsii_struct_bases=[])
    class PredicateProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-rule-predicate.html
        Stability:
            experimental
        """
        dataId: str
        """``CfnRule.PredicateProperty.DataId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-rule-predicate.html#cfn-wafregional-rule-predicate-dataid
        Stability:
            experimental
        """

        negated: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnRule.PredicateProperty.Negated``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-rule-predicate.html#cfn-wafregional-rule-predicate-negated
        Stability:
            experimental
        """

        type: str
        """``CfnRule.PredicateProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-rule-predicate.html#cfn-wafregional-rule-predicate-type
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRuleProps(jsii.compat.TypedDict, total=False):
    predicates: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnRule.PredicateProperty"]]]
    """``AWS::WAFRegional::Rule.Predicates``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-predicates
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnRuleProps", jsii_struct_bases=[_CfnRuleProps])
class CfnRuleProps(_CfnRuleProps):
    """Properties for defining a ``AWS::WAFRegional::Rule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html
    Stability:
        experimental
    """
    metricName: str
    """``AWS::WAFRegional::Rule.MetricName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-metricname
    Stability:
        experimental
    """

    name: str
    """``AWS::WAFRegional::Rule.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-rule.html#cfn-wafregional-rule-name
    Stability:
        experimental
    """

class CfnSizeConstraintSet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnSizeConstraintSet"):
    """A CloudFormation ``AWS::WAFRegional::SizeConstraintSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html
    Stability:
        experimental
    cloudformationResource:
        AWS::WAFRegional::SizeConstraintSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, size_constraints: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "SizeConstraintProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::SizeConstraintSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::SizeConstraintSet.Name``.
            sizeConstraints: ``AWS::WAFRegional::SizeConstraintSet.SizeConstraints``.

        Stability:
            experimental
        """
        props: CfnSizeConstraintSetProps = {"name": name}

        if size_constraints is not None:
            props["sizeConstraints"] = size_constraints

        jsii.create(CfnSizeConstraintSet, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSizeConstraintSetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="sizeConstraintSetId")
    def size_constraint_set_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "sizeConstraintSetId")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FieldToMatchProperty(jsii.compat.TypedDict, total=False):
        data: str
        """``CfnSizeConstraintSet.FieldToMatchProperty.Data``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-fieldtomatch.html#cfn-wafregional-sizeconstraintset-fieldtomatch-data
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSizeConstraintSet.FieldToMatchProperty", jsii_struct_bases=[_FieldToMatchProperty])
    class FieldToMatchProperty(_FieldToMatchProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-fieldtomatch.html
        Stability:
            experimental
        """
        type: str
        """``CfnSizeConstraintSet.FieldToMatchProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-fieldtomatch.html#cfn-wafregional-sizeconstraintset-fieldtomatch-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSizeConstraintSet.SizeConstraintProperty", jsii_struct_bases=[])
    class SizeConstraintProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html
        Stability:
            experimental
        """
        comparisonOperator: str
        """``CfnSizeConstraintSet.SizeConstraintProperty.ComparisonOperator``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html#cfn-wafregional-sizeconstraintset-sizeconstraint-comparisonoperator
        Stability:
            experimental
        """

        fieldToMatch: typing.Union[aws_cdk.cdk.Token, "CfnSizeConstraintSet.FieldToMatchProperty"]
        """``CfnSizeConstraintSet.SizeConstraintProperty.FieldToMatch``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html#cfn-wafregional-sizeconstraintset-sizeconstraint-fieldtomatch
        Stability:
            experimental
        """

        size: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnSizeConstraintSet.SizeConstraintProperty.Size``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html#cfn-wafregional-sizeconstraintset-sizeconstraint-size
        Stability:
            experimental
        """

        textTransformation: str
        """``CfnSizeConstraintSet.SizeConstraintProperty.TextTransformation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sizeconstraintset-sizeconstraint.html#cfn-wafregional-sizeconstraintset-sizeconstraint-texttransformation
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSizeConstraintSetProps(jsii.compat.TypedDict, total=False):
    sizeConstraints: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSizeConstraintSet.SizeConstraintProperty"]]]
    """``AWS::WAFRegional::SizeConstraintSet.SizeConstraints``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html#cfn-wafregional-sizeconstraintset-sizeconstraints
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSizeConstraintSetProps", jsii_struct_bases=[_CfnSizeConstraintSetProps])
class CfnSizeConstraintSetProps(_CfnSizeConstraintSetProps):
    """Properties for defining a ``AWS::WAFRegional::SizeConstraintSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html
    Stability:
        experimental
    """
    name: str
    """``AWS::WAFRegional::SizeConstraintSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sizeconstraintset.html#cfn-wafregional-sizeconstraintset-name
    Stability:
        experimental
    """

class CfnSqlInjectionMatchSet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnSqlInjectionMatchSet"):
    """A CloudFormation ``AWS::WAFRegional::SqlInjectionMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html
    Stability:
        experimental
    cloudformationResource:
        AWS::WAFRegional::SqlInjectionMatchSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, sql_injection_match_tuples: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "SqlInjectionMatchTupleProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::SqlInjectionMatchSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::SqlInjectionMatchSet.Name``.
            sqlInjectionMatchTuples: ``AWS::WAFRegional::SqlInjectionMatchSet.SqlInjectionMatchTuples``.

        Stability:
            experimental
        """
        props: CfnSqlInjectionMatchSetProps = {"name": name}

        if sql_injection_match_tuples is not None:
            props["sqlInjectionMatchTuples"] = sql_injection_match_tuples

        jsii.create(CfnSqlInjectionMatchSet, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSqlInjectionMatchSetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="sqlInjectionMatchSetId")
    def sql_injection_match_set_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "sqlInjectionMatchSetId")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FieldToMatchProperty(jsii.compat.TypedDict, total=False):
        data: str
        """``CfnSqlInjectionMatchSet.FieldToMatchProperty.Data``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-fieldtomatch.html#cfn-wafregional-sqlinjectionmatchset-fieldtomatch-data
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSqlInjectionMatchSet.FieldToMatchProperty", jsii_struct_bases=[_FieldToMatchProperty])
    class FieldToMatchProperty(_FieldToMatchProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-fieldtomatch.html
        Stability:
            experimental
        """
        type: str
        """``CfnSqlInjectionMatchSet.FieldToMatchProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-fieldtomatch.html#cfn-wafregional-sqlinjectionmatchset-fieldtomatch-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty", jsii_struct_bases=[])
    class SqlInjectionMatchTupleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple.html
        Stability:
            experimental
        """
        fieldToMatch: typing.Union[aws_cdk.cdk.Token, "CfnSqlInjectionMatchSet.FieldToMatchProperty"]
        """``CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty.FieldToMatch``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple.html#cfn-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple-fieldtomatch
        Stability:
            experimental
        """

        textTransformation: str
        """``CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty.TextTransformation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple.html#cfn-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuple-texttransformation
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSqlInjectionMatchSetProps(jsii.compat.TypedDict, total=False):
    sqlInjectionMatchTuples: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSqlInjectionMatchSet.SqlInjectionMatchTupleProperty"]]]
    """``AWS::WAFRegional::SqlInjectionMatchSet.SqlInjectionMatchTuples``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html#cfn-wafregional-sqlinjectionmatchset-sqlinjectionmatchtuples
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnSqlInjectionMatchSetProps", jsii_struct_bases=[_CfnSqlInjectionMatchSetProps])
class CfnSqlInjectionMatchSetProps(_CfnSqlInjectionMatchSetProps):
    """Properties for defining a ``AWS::WAFRegional::SqlInjectionMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html
    Stability:
        experimental
    """
    name: str
    """``AWS::WAFRegional::SqlInjectionMatchSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-sqlinjectionmatchset.html#cfn-wafregional-sqlinjectionmatchset-name
    Stability:
        experimental
    """

class CfnWebACL(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnWebACL"):
    """A CloudFormation ``AWS::WAFRegional::WebACL``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html
    Stability:
        experimental
    cloudformationResource:
        AWS::WAFRegional::WebACL
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, default_action: typing.Union[aws_cdk.cdk.Token, "ActionProperty"], metric_name: str, name: str, rules: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "RuleProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::WebACL``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            defaultAction: ``AWS::WAFRegional::WebACL.DefaultAction``.
            metricName: ``AWS::WAFRegional::WebACL.MetricName``.
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
    def property_overrides(self) -> "CfnWebACLProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="webAclId")
    def web_acl_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "webAclId")

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnWebACL.ActionProperty", jsii_struct_bases=[])
    class ActionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-action.html
        Stability:
            experimental
        """
        type: str
        """``CfnWebACL.ActionProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-action.html#cfn-wafregional-webacl-action-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnWebACL.RuleProperty", jsii_struct_bases=[])
    class RuleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-rule.html
        Stability:
            experimental
        """
        action: typing.Union[aws_cdk.cdk.Token, "CfnWebACL.ActionProperty"]
        """``CfnWebACL.RuleProperty.Action``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-rule.html#cfn-wafregional-webacl-rule-action
        Stability:
            experimental
        """

        priority: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnWebACL.RuleProperty.Priority``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-rule.html#cfn-wafregional-webacl-rule-priority
        Stability:
            experimental
        """

        ruleId: str
        """``CfnWebACL.RuleProperty.RuleId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-webacl-rule.html#cfn-wafregional-webacl-rule-ruleid
        Stability:
            experimental
        """


class CfnWebACLAssociation(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnWebACLAssociation"):
    """A CloudFormation ``AWS::WAFRegional::WebACLAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html
    Stability:
        experimental
    cloudformationResource:
        AWS::WAFRegional::WebACLAssociation
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, resource_arn: str, web_acl_id: str) -> None:
        """Create a new ``AWS::WAFRegional::WebACLAssociation``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            resourceArn: ``AWS::WAFRegional::WebACLAssociation.ResourceArn``.
            webAclId: ``AWS::WAFRegional::WebACLAssociation.WebACLId``.

        Stability:
            experimental
        """
        props: CfnWebACLAssociationProps = {"resourceArn": resource_arn, "webAclId": web_acl_id}

        jsii.create(CfnWebACLAssociation, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnWebACLAssociationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="webAclAssociationId")
    def web_acl_association_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "webAclAssociationId")


@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnWebACLAssociationProps", jsii_struct_bases=[])
class CfnWebACLAssociationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::WAFRegional::WebACLAssociation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html
    Stability:
        experimental
    """
    resourceArn: str
    """``AWS::WAFRegional::WebACLAssociation.ResourceArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html#cfn-wafregional-webaclassociation-resourcearn
    Stability:
        experimental
    """

    webAclId: str
    """``AWS::WAFRegional::WebACLAssociation.WebACLId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webaclassociation.html#cfn-wafregional-webaclassociation-webaclid
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnWebACLProps(jsii.compat.TypedDict, total=False):
    rules: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnWebACL.RuleProperty"]]]
    """``AWS::WAFRegional::WebACL.Rules``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-rules
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnWebACLProps", jsii_struct_bases=[_CfnWebACLProps])
class CfnWebACLProps(_CfnWebACLProps):
    """Properties for defining a ``AWS::WAFRegional::WebACL``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html
    Stability:
        experimental
    """
    defaultAction: typing.Union[aws_cdk.cdk.Token, "CfnWebACL.ActionProperty"]
    """``AWS::WAFRegional::WebACL.DefaultAction``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-defaultaction
    Stability:
        experimental
    """

    metricName: str
    """``AWS::WAFRegional::WebACL.MetricName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-metricname
    Stability:
        experimental
    """

    name: str
    """``AWS::WAFRegional::WebACL.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-webacl.html#cfn-wafregional-webacl-name
    Stability:
        experimental
    """

class CfnXssMatchSet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-wafregional.CfnXssMatchSet"):
    """A CloudFormation ``AWS::WAFRegional::XssMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html
    Stability:
        experimental
    cloudformationResource:
        AWS::WAFRegional::XssMatchSet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, xss_match_tuples: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "XssMatchTupleProperty"]]]]]=None) -> None:
        """Create a new ``AWS::WAFRegional::XssMatchSet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::WAFRegional::XssMatchSet.Name``.
            xssMatchTuples: ``AWS::WAFRegional::XssMatchSet.XssMatchTuples``.

        Stability:
            experimental
        """
        props: CfnXssMatchSetProps = {"name": name}

        if xss_match_tuples is not None:
            props["xssMatchTuples"] = xss_match_tuples

        jsii.create(CfnXssMatchSet, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnXssMatchSetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="xssMatchSetId")
    def xss_match_set_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "xssMatchSetId")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FieldToMatchProperty(jsii.compat.TypedDict, total=False):
        data: str
        """``CfnXssMatchSet.FieldToMatchProperty.Data``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-fieldtomatch.html#cfn-wafregional-xssmatchset-fieldtomatch-data
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnXssMatchSet.FieldToMatchProperty", jsii_struct_bases=[_FieldToMatchProperty])
    class FieldToMatchProperty(_FieldToMatchProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-fieldtomatch.html
        Stability:
            experimental
        """
        type: str
        """``CfnXssMatchSet.FieldToMatchProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-fieldtomatch.html#cfn-wafregional-xssmatchset-fieldtomatch-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnXssMatchSet.XssMatchTupleProperty", jsii_struct_bases=[])
    class XssMatchTupleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-xssmatchtuple.html
        Stability:
            experimental
        """
        fieldToMatch: typing.Union[aws_cdk.cdk.Token, "CfnXssMatchSet.FieldToMatchProperty"]
        """``CfnXssMatchSet.XssMatchTupleProperty.FieldToMatch``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-xssmatchtuple.html#cfn-wafregional-xssmatchset-xssmatchtuple-fieldtomatch
        Stability:
            experimental
        """

        textTransformation: str
        """``CfnXssMatchSet.XssMatchTupleProperty.TextTransformation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-wafregional-xssmatchset-xssmatchtuple.html#cfn-wafregional-xssmatchset-xssmatchtuple-texttransformation
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnXssMatchSetProps(jsii.compat.TypedDict, total=False):
    xssMatchTuples: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnXssMatchSet.XssMatchTupleProperty"]]]
    """``AWS::WAFRegional::XssMatchSet.XssMatchTuples``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html#cfn-wafregional-xssmatchset-xssmatchtuples
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-wafregional.CfnXssMatchSetProps", jsii_struct_bases=[_CfnXssMatchSetProps])
class CfnXssMatchSetProps(_CfnXssMatchSetProps):
    """Properties for defining a ``AWS::WAFRegional::XssMatchSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html
    Stability:
        experimental
    """
    name: str
    """``AWS::WAFRegional::XssMatchSet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafregional-xssmatchset.html#cfn-wafregional-xssmatchset-name
    Stability:
        experimental
    """

__all__ = ["CfnByteMatchSet", "CfnByteMatchSetProps", "CfnGeoMatchSet", "CfnGeoMatchSetProps", "CfnIPSet", "CfnIPSetProps", "CfnRateBasedRule", "CfnRateBasedRuleProps", "CfnRegexPatternSet", "CfnRegexPatternSetProps", "CfnRule", "CfnRuleProps", "CfnSizeConstraintSet", "CfnSizeConstraintSetProps", "CfnSqlInjectionMatchSet", "CfnSqlInjectionMatchSetProps", "CfnWebACL", "CfnWebACLAssociation", "CfnWebACLAssociationProps", "CfnWebACLProps", "CfnXssMatchSet", "CfnXssMatchSetProps", "__jsii_assembly__"]

publication.publish()
