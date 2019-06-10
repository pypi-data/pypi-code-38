import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_sns
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-config", "0.34.0", __name__, "aws-config@0.34.0.jsii.tgz")
class CfnAggregationAuthorization(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-config.CfnAggregationAuthorization"):
    """A CloudFormation ``AWS::Config::AggregationAuthorization``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-aggregationauthorization.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Config::AggregationAuthorization
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, authorized_account_id: str, authorized_aws_region: str) -> None:
        """Create a new ``AWS::Config::AggregationAuthorization``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            authorizedAccountId: ``AWS::Config::AggregationAuthorization.AuthorizedAccountId``.
            authorizedAwsRegion: ``AWS::Config::AggregationAuthorization.AuthorizedAwsRegion``.

        Stability:
            experimental
        """
        props: CfnAggregationAuthorizationProps = {"authorizedAccountId": authorized_account_id, "authorizedAwsRegion": authorized_aws_region}

        jsii.create(CfnAggregationAuthorization, self, [scope, id, props])

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
    @jsii.member(jsii_name="aggregationAuthorizationArn")
    def aggregation_authorization_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "aggregationAuthorizationArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnAggregationAuthorizationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-config.CfnAggregationAuthorizationProps", jsii_struct_bases=[])
class CfnAggregationAuthorizationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Config::AggregationAuthorization``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-aggregationauthorization.html
    Stability:
        experimental
    """
    authorizedAccountId: str
    """``AWS::Config::AggregationAuthorization.AuthorizedAccountId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-aggregationauthorization.html#cfn-config-aggregationauthorization-authorizedaccountid
    Stability:
        experimental
    """

    authorizedAwsRegion: str
    """``AWS::Config::AggregationAuthorization.AuthorizedAwsRegion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-aggregationauthorization.html#cfn-config-aggregationauthorization-authorizedawsregion
    Stability:
        experimental
    """

class CfnConfigRule(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-config.CfnConfigRule"):
    """A CloudFormation ``AWS::Config::ConfigRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Config::ConfigRule
    """
    def __init__(self, scope_: aws_cdk.cdk.Construct, id: str, *, source: typing.Union["SourceProperty", aws_cdk.cdk.Token], config_rule_name: typing.Optional[str]=None, description: typing.Optional[str]=None, input_parameters: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, maximum_execution_frequency: typing.Optional[str]=None, scope: typing.Optional[typing.Union[typing.Optional["ScopeProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::Config::ConfigRule``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            source: ``AWS::Config::ConfigRule.Source``.
            configRuleName: ``AWS::Config::ConfigRule.ConfigRuleName``.
            description: ``AWS::Config::ConfigRule.Description``.
            inputParameters: ``AWS::Config::ConfigRule.InputParameters``.
            maximumExecutionFrequency: ``AWS::Config::ConfigRule.MaximumExecutionFrequency``.
            scope: ``AWS::Config::ConfigRule.Scope``.

        Stability:
            experimental
        """
        props: CfnConfigRuleProps = {"source": source}

        if config_rule_name is not None:
            props["configRuleName"] = config_rule_name

        if description is not None:
            props["description"] = description

        if input_parameters is not None:
            props["inputParameters"] = input_parameters

        if maximum_execution_frequency is not None:
            props["maximumExecutionFrequency"] = maximum_execution_frequency

        if scope is not None:
            props["scope"] = scope

        jsii.create(CfnConfigRule, self, [scope, id, props])

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
    @jsii.member(jsii_name="configRuleArn")
    def config_rule_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "configRuleArn")

    @property
    @jsii.member(jsii_name="configRuleComplianceType")
    def config_rule_compliance_type(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Compliance.Type
        """
        return jsii.get(self, "configRuleComplianceType")

    @property
    @jsii.member(jsii_name="configRuleId")
    def config_rule_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ConfigRuleId
        """
        return jsii.get(self, "configRuleId")

    @property
    @jsii.member(jsii_name="configRuleName")
    def config_rule_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "configRuleName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnConfigRuleProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-config.CfnConfigRule.ScopeProperty", jsii_struct_bases=[])
    class ScopeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-scope.html
        Stability:
            experimental
        """
        complianceResourceId: str
        """``CfnConfigRule.ScopeProperty.ComplianceResourceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-scope.html#cfn-config-configrule-scope-complianceresourceid
        Stability:
            experimental
        """

        complianceResourceTypes: typing.List[str]
        """``CfnConfigRule.ScopeProperty.ComplianceResourceTypes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-scope.html#cfn-config-configrule-scope-complianceresourcetypes
        Stability:
            experimental
        """

        tagKey: str
        """``CfnConfigRule.ScopeProperty.TagKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-scope.html#cfn-config-configrule-scope-tagkey
        Stability:
            experimental
        """

        tagValue: str
        """``CfnConfigRule.ScopeProperty.TagValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-scope.html#cfn-config-configrule-scope-tagvalue
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SourceDetailProperty(jsii.compat.TypedDict, total=False):
        maximumExecutionFrequency: str
        """``CfnConfigRule.SourceDetailProperty.MaximumExecutionFrequency``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source-sourcedetails.html#cfn-config-configrule-sourcedetail-maximumexecutionfrequency
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-config.CfnConfigRule.SourceDetailProperty", jsii_struct_bases=[_SourceDetailProperty])
    class SourceDetailProperty(_SourceDetailProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source-sourcedetails.html
        Stability:
            experimental
        """
        eventSource: str
        """``CfnConfigRule.SourceDetailProperty.EventSource``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source-sourcedetails.html#cfn-config-configrule-source-sourcedetail-eventsource
        Stability:
            experimental
        """

        messageType: str
        """``CfnConfigRule.SourceDetailProperty.MessageType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source-sourcedetails.html#cfn-config-configrule-source-sourcedetail-messagetype
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SourceProperty(jsii.compat.TypedDict, total=False):
        sourceDetails: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnConfigRule.SourceDetailProperty"]]]
        """``CfnConfigRule.SourceProperty.SourceDetails``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source.html#cfn-config-configrule-source-sourcedetails
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-config.CfnConfigRule.SourceProperty", jsii_struct_bases=[_SourceProperty])
    class SourceProperty(_SourceProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source.html
        Stability:
            experimental
        """
        owner: str
        """``CfnConfigRule.SourceProperty.Owner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source.html#cfn-config-configrule-source-owner
        Stability:
            experimental
        """

        sourceIdentifier: str
        """``CfnConfigRule.SourceProperty.SourceIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source.html#cfn-config-configrule-source-sourceidentifier
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnConfigRuleProps(jsii.compat.TypedDict, total=False):
    configRuleName: str
    """``AWS::Config::ConfigRule.ConfigRuleName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-configrulename
    Stability:
        experimental
    """
    description: str
    """``AWS::Config::ConfigRule.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-description
    Stability:
        experimental
    """
    inputParameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::Config::ConfigRule.InputParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-inputparameters
    Stability:
        experimental
    """
    maximumExecutionFrequency: str
    """``AWS::Config::ConfigRule.MaximumExecutionFrequency``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-maximumexecutionfrequency
    Stability:
        experimental
    """
    scope: typing.Union["CfnConfigRule.ScopeProperty", aws_cdk.cdk.Token]
    """``AWS::Config::ConfigRule.Scope``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-scope
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-config.CfnConfigRuleProps", jsii_struct_bases=[_CfnConfigRuleProps])
class CfnConfigRuleProps(_CfnConfigRuleProps):
    """Properties for defining a ``AWS::Config::ConfigRule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html
    Stability:
        experimental
    """
    source: typing.Union["CfnConfigRule.SourceProperty", aws_cdk.cdk.Token]
    """``AWS::Config::ConfigRule.Source``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-source
    Stability:
        experimental
    """

class CfnConfigurationAggregator(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-config.CfnConfigurationAggregator"):
    """A CloudFormation ``AWS::Config::ConfigurationAggregator``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Config::ConfigurationAggregator
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, configuration_aggregator_name: str, account_aggregation_sources: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "AccountAggregationSourceProperty"]]]]]=None, organization_aggregation_source: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["OrganizationAggregationSourceProperty"]]]=None) -> None:
        """Create a new ``AWS::Config::ConfigurationAggregator``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            configurationAggregatorName: ``AWS::Config::ConfigurationAggregator.ConfigurationAggregatorName``.
            accountAggregationSources: ``AWS::Config::ConfigurationAggregator.AccountAggregationSources``.
            organizationAggregationSource: ``AWS::Config::ConfigurationAggregator.OrganizationAggregationSource``.

        Stability:
            experimental
        """
        props: CfnConfigurationAggregatorProps = {"configurationAggregatorName": configuration_aggregator_name}

        if account_aggregation_sources is not None:
            props["accountAggregationSources"] = account_aggregation_sources

        if organization_aggregation_source is not None:
            props["organizationAggregationSource"] = organization_aggregation_source

        jsii.create(CfnConfigurationAggregator, self, [scope, id, props])

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
    @jsii.member(jsii_name="configurationAggregatorName")
    def configuration_aggregator_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "configurationAggregatorName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnConfigurationAggregatorProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _AccountAggregationSourceProperty(jsii.compat.TypedDict, total=False):
        allAwsRegions: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnConfigurationAggregator.AccountAggregationSourceProperty.AllAwsRegions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-accountaggregationsource.html#cfn-config-configurationaggregator-accountaggregationsource-allawsregions
        Stability:
            experimental
        """
        awsRegions: typing.List[str]
        """``CfnConfigurationAggregator.AccountAggregationSourceProperty.AwsRegions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-accountaggregationsource.html#cfn-config-configurationaggregator-accountaggregationsource-awsregions
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-config.CfnConfigurationAggregator.AccountAggregationSourceProperty", jsii_struct_bases=[_AccountAggregationSourceProperty])
    class AccountAggregationSourceProperty(_AccountAggregationSourceProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-accountaggregationsource.html
        Stability:
            experimental
        """
        accountIds: typing.List[str]
        """``CfnConfigurationAggregator.AccountAggregationSourceProperty.AccountIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-accountaggregationsource.html#cfn-config-configurationaggregator-accountaggregationsource-accountids
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _OrganizationAggregationSourceProperty(jsii.compat.TypedDict, total=False):
        allAwsRegions: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnConfigurationAggregator.OrganizationAggregationSourceProperty.AllAwsRegions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-organizationaggregationsource.html#cfn-config-configurationaggregator-organizationaggregationsource-allawsregions
        Stability:
            experimental
        """
        awsRegions: typing.List[str]
        """``CfnConfigurationAggregator.OrganizationAggregationSourceProperty.AwsRegions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-organizationaggregationsource.html#cfn-config-configurationaggregator-organizationaggregationsource-awsregions
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-config.CfnConfigurationAggregator.OrganizationAggregationSourceProperty", jsii_struct_bases=[_OrganizationAggregationSourceProperty])
    class OrganizationAggregationSourceProperty(_OrganizationAggregationSourceProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-organizationaggregationsource.html
        Stability:
            experimental
        """
        roleArn: str
        """``CfnConfigurationAggregator.OrganizationAggregationSourceProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-organizationaggregationsource.html#cfn-config-configurationaggregator-organizationaggregationsource-rolearn
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnConfigurationAggregatorProps(jsii.compat.TypedDict, total=False):
    accountAggregationSources: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnConfigurationAggregator.AccountAggregationSourceProperty"]]]
    """``AWS::Config::ConfigurationAggregator.AccountAggregationSources``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html#cfn-config-configurationaggregator-accountaggregationsources
    Stability:
        experimental
    """
    organizationAggregationSource: typing.Union[aws_cdk.cdk.Token, "CfnConfigurationAggregator.OrganizationAggregationSourceProperty"]
    """``AWS::Config::ConfigurationAggregator.OrganizationAggregationSource``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html#cfn-config-configurationaggregator-organizationaggregationsource
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-config.CfnConfigurationAggregatorProps", jsii_struct_bases=[_CfnConfigurationAggregatorProps])
class CfnConfigurationAggregatorProps(_CfnConfigurationAggregatorProps):
    """Properties for defining a ``AWS::Config::ConfigurationAggregator``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html
    Stability:
        experimental
    """
    configurationAggregatorName: str
    """``AWS::Config::ConfigurationAggregator.ConfigurationAggregatorName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html#cfn-config-configurationaggregator-configurationaggregatorname
    Stability:
        experimental
    """

class CfnConfigurationRecorder(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-config.CfnConfigurationRecorder"):
    """A CloudFormation ``AWS::Config::ConfigurationRecorder``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Config::ConfigurationRecorder
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, role_arn: str, name: typing.Optional[str]=None, recording_group: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["RecordingGroupProperty"]]]=None) -> None:
        """Create a new ``AWS::Config::ConfigurationRecorder``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            roleArn: ``AWS::Config::ConfigurationRecorder.RoleARN``.
            name: ``AWS::Config::ConfigurationRecorder.Name``.
            recordingGroup: ``AWS::Config::ConfigurationRecorder.RecordingGroup``.

        Stability:
            experimental
        """
        props: CfnConfigurationRecorderProps = {"roleArn": role_arn}

        if name is not None:
            props["name"] = name

        if recording_group is not None:
            props["recordingGroup"] = recording_group

        jsii.create(CfnConfigurationRecorder, self, [scope, id, props])

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
    @jsii.member(jsii_name="configurationRecorderName")
    def configuration_recorder_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "configurationRecorderName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnConfigurationRecorderProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-config.CfnConfigurationRecorder.RecordingGroupProperty", jsii_struct_bases=[])
    class RecordingGroupProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationrecorder-recordinggroup.html
        Stability:
            experimental
        """
        allSupported: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnConfigurationRecorder.RecordingGroupProperty.AllSupported``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationrecorder-recordinggroup.html#cfn-config-configurationrecorder-recordinggroup-allsupported
        Stability:
            experimental
        """

        includeGlobalResourceTypes: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnConfigurationRecorder.RecordingGroupProperty.IncludeGlobalResourceTypes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationrecorder-recordinggroup.html#cfn-config-configurationrecorder-recordinggroup-includeglobalresourcetypes
        Stability:
            experimental
        """

        resourceTypes: typing.List[str]
        """``CfnConfigurationRecorder.RecordingGroupProperty.ResourceTypes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationrecorder-recordinggroup.html#cfn-config-configurationrecorder-recordinggroup-resourcetypes
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnConfigurationRecorderProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::Config::ConfigurationRecorder.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html#cfn-config-configurationrecorder-name
    Stability:
        experimental
    """
    recordingGroup: typing.Union[aws_cdk.cdk.Token, "CfnConfigurationRecorder.RecordingGroupProperty"]
    """``AWS::Config::ConfigurationRecorder.RecordingGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html#cfn-config-configurationrecorder-recordinggroup
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-config.CfnConfigurationRecorderProps", jsii_struct_bases=[_CfnConfigurationRecorderProps])
class CfnConfigurationRecorderProps(_CfnConfigurationRecorderProps):
    """Properties for defining a ``AWS::Config::ConfigurationRecorder``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html
    Stability:
        experimental
    """
    roleArn: str
    """``AWS::Config::ConfigurationRecorder.RoleARN``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html#cfn-config-configurationrecorder-rolearn
    Stability:
        experimental
    """

class CfnDeliveryChannel(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-config.CfnDeliveryChannel"):
    """A CloudFormation ``AWS::Config::DeliveryChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Config::DeliveryChannel
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, s3_bucket_name: str, config_snapshot_delivery_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ConfigSnapshotDeliveryPropertiesProperty"]]]=None, name: typing.Optional[str]=None, s3_key_prefix: typing.Optional[str]=None, sns_topic_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Config::DeliveryChannel``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            s3BucketName: ``AWS::Config::DeliveryChannel.S3BucketName``.
            configSnapshotDeliveryProperties: ``AWS::Config::DeliveryChannel.ConfigSnapshotDeliveryProperties``.
            name: ``AWS::Config::DeliveryChannel.Name``.
            s3KeyPrefix: ``AWS::Config::DeliveryChannel.S3KeyPrefix``.
            snsTopicArn: ``AWS::Config::DeliveryChannel.SnsTopicARN``.

        Stability:
            experimental
        """
        props: CfnDeliveryChannelProps = {"s3BucketName": s3_bucket_name}

        if config_snapshot_delivery_properties is not None:
            props["configSnapshotDeliveryProperties"] = config_snapshot_delivery_properties

        if name is not None:
            props["name"] = name

        if s3_key_prefix is not None:
            props["s3KeyPrefix"] = s3_key_prefix

        if sns_topic_arn is not None:
            props["snsTopicArn"] = sns_topic_arn

        jsii.create(CfnDeliveryChannel, self, [scope, id, props])

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
    @jsii.member(jsii_name="deliveryChannelName")
    def delivery_channel_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deliveryChannelName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDeliveryChannelProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-config.CfnDeliveryChannel.ConfigSnapshotDeliveryPropertiesProperty", jsii_struct_bases=[])
    class ConfigSnapshotDeliveryPropertiesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-deliverychannel-configsnapshotdeliveryproperties.html
        Stability:
            experimental
        """
        deliveryFrequency: str
        """``CfnDeliveryChannel.ConfigSnapshotDeliveryPropertiesProperty.DeliveryFrequency``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-deliverychannel-configsnapshotdeliveryproperties.html#cfn-config-deliverychannel-configsnapshotdeliveryproperties-deliveryfrequency
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDeliveryChannelProps(jsii.compat.TypedDict, total=False):
    configSnapshotDeliveryProperties: typing.Union[aws_cdk.cdk.Token, "CfnDeliveryChannel.ConfigSnapshotDeliveryPropertiesProperty"]
    """``AWS::Config::DeliveryChannel.ConfigSnapshotDeliveryProperties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-configsnapshotdeliveryproperties
    Stability:
        experimental
    """
    name: str
    """``AWS::Config::DeliveryChannel.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-name
    Stability:
        experimental
    """
    s3KeyPrefix: str
    """``AWS::Config::DeliveryChannel.S3KeyPrefix``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-s3keyprefix
    Stability:
        experimental
    """
    snsTopicArn: str
    """``AWS::Config::DeliveryChannel.SnsTopicARN``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-snstopicarn
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-config.CfnDeliveryChannelProps", jsii_struct_bases=[_CfnDeliveryChannelProps])
class CfnDeliveryChannelProps(_CfnDeliveryChannelProps):
    """Properties for defining a ``AWS::Config::DeliveryChannel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html
    Stability:
        experimental
    """
    s3BucketName: str
    """``AWS::Config::DeliveryChannel.S3BucketName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-s3bucketname
    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-config.IRule")
class IRule(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """A config rule.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IRuleProxy

    @property
    @jsii.member(jsii_name="configRuleName")
    def config_rule_name(self) -> str:
        """The name of the rule.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @jsii.member(jsii_name="onComplianceChange")
    def on_compliance_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for rule compliance events.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for rule events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onReEvaluationStatus")
    def on_re_evaluation_status(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for rule re-evaluation status events.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...


class _IRuleProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """A config rule.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-config.IRule"
    @property
    @jsii.member(jsii_name="configRuleName")
    def config_rule_name(self) -> str:
        """The name of the rule.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "configRuleName")

    @jsii.member(jsii_name="onComplianceChange")
    def on_compliance_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for rule compliance events.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onComplianceChange", [id, options])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for rule events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onEvent", [id, options])

    @jsii.member(jsii_name="onReEvaluationStatus")
    def on_re_evaluation_status(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for rule re-evaluation status events.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onReEvaluationStatus", [id, options])


@jsii.implements(IRule)
class CustomRule(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-config.CustomRule"):
    """A new custom rule.

    Stability:
        experimental
    resource:
        AWS::Config::ConfigRule
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, lambda_function: aws_cdk.aws_lambda.IFunction, configuration_changes: typing.Optional[bool]=None, periodic: typing.Optional[bool]=None, description: typing.Optional[str]=None, input_parameters: typing.Optional[typing.Mapping[str,typing.Any]]=None, maximum_execution_frequency: typing.Optional["MaximumExecutionFrequency"]=None, name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            lambdaFunction: The Lambda function to run.
            configurationChanges: Whether to run the rule on configuration changes. Default: false
            periodic: Whether to run the rule on a fixed frequency. Default: false
            description: A description about this AWS Config rule. Default: no description
            inputParameters: Input parameter values that are passed to the AWS Config rule. Default: no input parameters
            maximumExecutionFrequency: The maximum frequency at which the AWS Config rule runs evaluations. Default: 24 hours
            name: A name for the AWS Config rule. Default: a CloudFormation generated name

        Stability:
            experimental
        """
        props: CustomRuleProps = {"lambdaFunction": lambda_function}

        if configuration_changes is not None:
            props["configurationChanges"] = configuration_changes

        if periodic is not None:
            props["periodic"] = periodic

        if description is not None:
            props["description"] = description

        if input_parameters is not None:
            props["inputParameters"] = input_parameters

        if maximum_execution_frequency is not None:
            props["maximumExecutionFrequency"] = maximum_execution_frequency

        if name is not None:
            props["name"] = name

        jsii.create(CustomRule, self, [scope, id, props])

    @jsii.member(jsii_name="fromConfigRuleName")
    @classmethod
    def from_config_rule_name(cls, scope: aws_cdk.cdk.Construct, id: str, config_rule_name: str) -> "IRule":
        """Imports an existing rule.

        Arguments:
            scope: -
            id: -
            configRuleName: the name of the rule.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromConfigRuleName", [scope, id, config_rule_name])

    @jsii.member(jsii_name="onComplianceChange")
    def on_compliance_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for rule compliance events.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onComplianceChange", [id, options])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for rule events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onEvent", [id, options])

    @jsii.member(jsii_name="onReEvaluationStatus")
    def on_re_evaluation_status(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for rule re-evaluation status events.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onReEvaluationStatus", [id, options])

    @jsii.member(jsii_name="scopeToResource")
    def scope_to_resource(self, type: str, identifier: typing.Optional[str]=None) -> None:
        """Restrict scope of changes to a specific resource.

        Arguments:
            type: the resource type.
            identifier: the resource identifier.

        See:
            https://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources
        Stability:
            experimental
        """
        return jsii.invoke(self, "scopeToResource", [type, identifier])

    @jsii.member(jsii_name="scopeToResources")
    def scope_to_resources(self, *types: str) -> None:
        """Restrict scope of changes to specific resource types.

        Arguments:
            types: resource types.

        See:
            https://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources
        Stability:
            experimental
        """
        return jsii.invoke(self, "scopeToResources", [*types])

    @jsii.member(jsii_name="scopeToTag")
    def scope_to_tag(self, key: str, value: typing.Optional[str]=None) -> None:
        """Restrict scope of changes to a specific tag.

        Arguments:
            key: the tag key.
            value: the tag value.

        Stability:
            experimental
        """
        return jsii.invoke(self, "scopeToTag", [key, value])

    @property
    @jsii.member(jsii_name="configRuleArn")
    def config_rule_arn(self) -> str:
        """The arn of the rule.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "configRuleArn")

    @property
    @jsii.member(jsii_name="configRuleComplianceType")
    def config_rule_compliance_type(self) -> str:
        """The compliance status of the rule.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "configRuleComplianceType")

    @property
    @jsii.member(jsii_name="configRuleId")
    def config_rule_id(self) -> str:
        """The id of the rule.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "configRuleId")

    @property
    @jsii.member(jsii_name="configRuleName")
    def config_rule_name(self) -> str:
        """The name of the rule.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "configRuleName")

    @property
    @jsii.member(jsii_name="isCustomWithChanges")
    def _is_custom_with_changes(self) -> typing.Optional[bool]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "isCustomWithChanges")

    @_is_custom_with_changes.setter
    def _is_custom_with_changes(self, value: typing.Optional[bool]):
        return jsii.set(self, "isCustomWithChanges", value)

    @property
    @jsii.member(jsii_name="isManaged")
    def _is_managed(self) -> typing.Optional[bool]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "isManaged")

    @_is_managed.setter
    def _is_managed(self, value: typing.Optional[bool]):
        return jsii.set(self, "isManaged", value)

    @property
    @jsii.member(jsii_name="scope")
    def _scope(self) -> typing.Optional["CfnConfigRule.ScopeProperty"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "scope")

    @_scope.setter
    def _scope(self, value: typing.Optional["CfnConfigRule.ScopeProperty"]):
        return jsii.set(self, "scope", value)


@jsii.implements(IRule)
class ManagedRule(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-config.ManagedRule"):
    """A new managed rule.

    Stability:
        experimental
    resource:
        AWS::Config::ConfigRule
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, identifier: str, description: typing.Optional[str]=None, input_parameters: typing.Optional[typing.Mapping[str,typing.Any]]=None, maximum_execution_frequency: typing.Optional["MaximumExecutionFrequency"]=None, name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            identifier: The identifier of the AWS managed rule.
            description: A description about this AWS Config rule. Default: no description
            inputParameters: Input parameter values that are passed to the AWS Config rule. Default: no input parameters
            maximumExecutionFrequency: The maximum frequency at which the AWS Config rule runs evaluations. Default: 24 hours
            name: A name for the AWS Config rule. Default: a CloudFormation generated name

        Stability:
            experimental
        """
        props: ManagedRuleProps = {"identifier": identifier}

        if description is not None:
            props["description"] = description

        if input_parameters is not None:
            props["inputParameters"] = input_parameters

        if maximum_execution_frequency is not None:
            props["maximumExecutionFrequency"] = maximum_execution_frequency

        if name is not None:
            props["name"] = name

        jsii.create(ManagedRule, self, [scope, id, props])

    @jsii.member(jsii_name="fromConfigRuleName")
    @classmethod
    def from_config_rule_name(cls, scope: aws_cdk.cdk.Construct, id: str, config_rule_name: str) -> "IRule":
        """Imports an existing rule.

        Arguments:
            scope: -
            id: -
            configRuleName: the name of the rule.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromConfigRuleName", [scope, id, config_rule_name])

    @jsii.member(jsii_name="onComplianceChange")
    def on_compliance_change(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for rule compliance events.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onComplianceChange", [id, options])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for rule events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onEvent", [id, options])

    @jsii.member(jsii_name="onReEvaluationStatus")
    def on_re_evaluation_status(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for rule re-evaluation status events.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onReEvaluationStatus", [id, options])

    @jsii.member(jsii_name="scopeToResource")
    def scope_to_resource(self, type: str, identifier: typing.Optional[str]=None) -> None:
        """Restrict scope of changes to a specific resource.

        Arguments:
            type: the resource type.
            identifier: the resource identifier.

        See:
            https://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources
        Stability:
            experimental
        """
        return jsii.invoke(self, "scopeToResource", [type, identifier])

    @jsii.member(jsii_name="scopeToResources")
    def scope_to_resources(self, *types: str) -> None:
        """Restrict scope of changes to specific resource types.

        Arguments:
            types: resource types.

        See:
            https://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources
        Stability:
            experimental
        """
        return jsii.invoke(self, "scopeToResources", [*types])

    @jsii.member(jsii_name="scopeToTag")
    def scope_to_tag(self, key: str, value: typing.Optional[str]=None) -> None:
        """Restrict scope of changes to a specific tag.

        Arguments:
            key: the tag key.
            value: the tag value.

        Stability:
            experimental
        """
        return jsii.invoke(self, "scopeToTag", [key, value])

    @property
    @jsii.member(jsii_name="configRuleArn")
    def config_rule_arn(self) -> str:
        """The arn of the rule.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "configRuleArn")

    @property
    @jsii.member(jsii_name="configRuleComplianceType")
    def config_rule_compliance_type(self) -> str:
        """The compliance status of the rule.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "configRuleComplianceType")

    @property
    @jsii.member(jsii_name="configRuleId")
    def config_rule_id(self) -> str:
        """The id of the rule.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "configRuleId")

    @property
    @jsii.member(jsii_name="configRuleName")
    def config_rule_name(self) -> str:
        """The name of the rule.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "configRuleName")

    @property
    @jsii.member(jsii_name="isCustomWithChanges")
    def _is_custom_with_changes(self) -> typing.Optional[bool]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "isCustomWithChanges")

    @_is_custom_with_changes.setter
    def _is_custom_with_changes(self, value: typing.Optional[bool]):
        return jsii.set(self, "isCustomWithChanges", value)

    @property
    @jsii.member(jsii_name="isManaged")
    def _is_managed(self) -> typing.Optional[bool]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "isManaged")

    @_is_managed.setter
    def _is_managed(self, value: typing.Optional[bool]):
        return jsii.set(self, "isManaged", value)

    @property
    @jsii.member(jsii_name="scope")
    def _scope(self) -> typing.Optional["CfnConfigRule.ScopeProperty"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "scope")

    @_scope.setter
    def _scope(self, value: typing.Optional["CfnConfigRule.ScopeProperty"]):
        return jsii.set(self, "scope", value)


class AccessKeysRotated(ManagedRule, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-config.AccessKeysRotated"):
    """Checks whether the active access keys are rotated within the number of days specified in ``maxDays``.

    See:
        https://docs.aws.amazon.com/config/latest/developerguide/access-keys-rotated.html
    Stability:
        experimental
    resource:
        AWS::Config::ConfigRule
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, max_days: typing.Optional[jsii.Number]=None, description: typing.Optional[str]=None, input_parameters: typing.Optional[typing.Mapping[str,typing.Any]]=None, maximum_execution_frequency: typing.Optional["MaximumExecutionFrequency"]=None, name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            maxDays: The maximum number of days within which the access keys must be rotated. Default: 90 days
            description: A description about this AWS Config rule. Default: no description
            inputParameters: Input parameter values that are passed to the AWS Config rule. Default: no input parameters
            maximumExecutionFrequency: The maximum frequency at which the AWS Config rule runs evaluations. Default: 24 hours
            name: A name for the AWS Config rule. Default: a CloudFormation generated name

        Stability:
            experimental
        """
        props: AccessKeysRotatedProps = {}

        if max_days is not None:
            props["maxDays"] = max_days

        if description is not None:
            props["description"] = description

        if input_parameters is not None:
            props["inputParameters"] = input_parameters

        if maximum_execution_frequency is not None:
            props["maximumExecutionFrequency"] = maximum_execution_frequency

        if name is not None:
            props["name"] = name

        jsii.create(AccessKeysRotated, self, [scope, id, props])


class CloudFormationStackDriftDetectionCheck(ManagedRule, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-config.CloudFormationStackDriftDetectionCheck"):
    """Checks whether your CloudFormation stacks' actual configuration differs, or has drifted, from its expected configuration.

    See:
        https://docs.aws.amazon.com/config/latest/developerguide/cloudformation-stack-drift-detection-check.html
    Stability:
        experimental
    resource:
        AWS::Config::ConfigRule
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, own_stack_only: typing.Optional[bool]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, description: typing.Optional[str]=None, input_parameters: typing.Optional[typing.Mapping[str,typing.Any]]=None, maximum_execution_frequency: typing.Optional["MaximumExecutionFrequency"]=None, name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            ownStackOnly: Whether to check only the stack where this rule is deployed. Default: false
            role: The IAM role to use for this rule. It must have permissions to detect drift for AWS CloudFormation stacks. Ensure to attach ``config.amazonaws.com`` trusted permissions and ``ReadOnlyAccess`` policy permissions. For specific policy permissions, refer to https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html. Default: a role will be created
            description: A description about this AWS Config rule. Default: no description
            inputParameters: Input parameter values that are passed to the AWS Config rule. Default: no input parameters
            maximumExecutionFrequency: The maximum frequency at which the AWS Config rule runs evaluations. Default: 24 hours
            name: A name for the AWS Config rule. Default: a CloudFormation generated name

        Stability:
            experimental
        """
        props: CloudFormationStackDriftDetectionCheckProps = {}

        if own_stack_only is not None:
            props["ownStackOnly"] = own_stack_only

        if role is not None:
            props["role"] = role

        if description is not None:
            props["description"] = description

        if input_parameters is not None:
            props["inputParameters"] = input_parameters

        if maximum_execution_frequency is not None:
            props["maximumExecutionFrequency"] = maximum_execution_frequency

        if name is not None:
            props["name"] = name

        jsii.create(CloudFormationStackDriftDetectionCheck, self, [scope, id, props])


class CloudFormationStackNotificationCheck(ManagedRule, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-config.CloudFormationStackNotificationCheck"):
    """Checks whether your CloudFormation stacks are sending event notifications to a SNS topic.

    Optionally checks whether specified SNS topics are used.

    See:
        https://docs.aws.amazon.com/config/latest/developerguide/cloudformation-stack-notification-check.html
    Stability:
        experimental
    resource:
        AWS::Config::ConfigRule
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, topics: typing.Optional[typing.List[aws_cdk.aws_sns.ITopic]]=None, description: typing.Optional[str]=None, input_parameters: typing.Optional[typing.Mapping[str,typing.Any]]=None, maximum_execution_frequency: typing.Optional["MaximumExecutionFrequency"]=None, name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            topics: A list of allowed topics. At most 5 topics. Default: - No topics.
            description: A description about this AWS Config rule. Default: no description
            inputParameters: Input parameter values that are passed to the AWS Config rule. Default: no input parameters
            maximumExecutionFrequency: The maximum frequency at which the AWS Config rule runs evaluations. Default: 24 hours
            name: A name for the AWS Config rule. Default: a CloudFormation generated name

        Stability:
            experimental
        """
        props: CloudFormationStackNotificationCheckProps = {}

        if topics is not None:
            props["topics"] = topics

        if description is not None:
            props["description"] = description

        if input_parameters is not None:
            props["inputParameters"] = input_parameters

        if maximum_execution_frequency is not None:
            props["maximumExecutionFrequency"] = maximum_execution_frequency

        if name is not None:
            props["name"] = name

        jsii.create(CloudFormationStackNotificationCheck, self, [scope, id, props])


@jsii.enum(jsii_type="@aws-cdk/aws-config.MaximumExecutionFrequency")
class MaximumExecutionFrequency(enum.Enum):
    """The maximum frequency at which the AWS Config rule runs evaluations.

    Stability:
        experimental
    """
    ONE_HOUR = "ONE_HOUR"
    """
    Stability:
        experimental
    """
    THREE_HOURS = "THREE_HOURS"
    """
    Stability:
        experimental
    """
    SIX_HOURS = "SIX_HOURS"
    """
    Stability:
        experimental
    """
    TWELVE_HOURS = "TWELVE_HOURS"
    """
    Stability:
        experimental
    """
    TWENTY_FOUR_HOURS = "TWENTY_FOUR_HOURS"
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-config.RuleAttributes", jsii_struct_bases=[])
class RuleAttributes(jsii.compat.TypedDict):
    """Reference to an existing rule.

    Stability:
        experimental
    """
    configRuleName: str
    """The rule name.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-config.RuleProps", jsii_struct_bases=[])
class RuleProps(jsii.compat.TypedDict, total=False):
    """Construction properties for a new rule.

    Stability:
        experimental
    """
    description: str
    """A description about this AWS Config rule.

    Default:
        no description

    Stability:
        experimental
    """

    inputParameters: typing.Mapping[str,typing.Any]
    """Input parameter values that are passed to the AWS Config rule.

    Default:
        no input parameters

    Stability:
        experimental
    """

    maximumExecutionFrequency: "MaximumExecutionFrequency"
    """The maximum frequency at which the AWS Config rule runs evaluations.

    Default:
        24 hours

    Stability:
        experimental
    """

    name: str
    """A name for the AWS Config rule.

    Default:
        a CloudFormation generated name

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-config.AccessKeysRotatedProps", jsii_struct_bases=[RuleProps])
class AccessKeysRotatedProps(RuleProps, jsii.compat.TypedDict, total=False):
    """Construction properties for a AccessKeysRotated.

    Stability:
        experimental
    """
    maxDays: jsii.Number
    """The maximum number of days within which the access keys must be rotated.

    Default:
        90 days

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-config.CloudFormationStackDriftDetectionCheckProps", jsii_struct_bases=[RuleProps])
class CloudFormationStackDriftDetectionCheckProps(RuleProps, jsii.compat.TypedDict, total=False):
    """Construction properties for a CloudFormationStackDriftDetectionCheck.

    Stability:
        experimental
    """
    ownStackOnly: bool
    """Whether to check only the stack where this rule is deployed.

    Default:
        false

    Stability:
        experimental
    """

    role: aws_cdk.aws_iam.IRole
    """The IAM role to use for this rule.

    It must have permissions to detect drift
    for AWS CloudFormation stacks. Ensure to attach ``config.amazonaws.com`` trusted
    permissions and ``ReadOnlyAccess`` policy permissions. For specific policy permissions,
    refer to https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html.

    Default:
        a role will be created

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-config.CloudFormationStackNotificationCheckProps", jsii_struct_bases=[RuleProps])
class CloudFormationStackNotificationCheckProps(RuleProps, jsii.compat.TypedDict, total=False):
    """Construction properties for a CloudFormationStackNotificationCheck.

    Stability:
        experimental
    """
    topics: typing.List[aws_cdk.aws_sns.ITopic]
    """A list of allowed topics.

    At most 5 topics.

    Default:
        - No topics.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[RuleProps])
class _CustomRuleProps(RuleProps, jsii.compat.TypedDict, total=False):
    configurationChanges: bool
    """Whether to run the rule on configuration changes.

    Default:
        false

    Stability:
        experimental
    """
    periodic: bool
    """Whether to run the rule on a fixed frequency.

    Default:
        false

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-config.CustomRuleProps", jsii_struct_bases=[_CustomRuleProps])
class CustomRuleProps(_CustomRuleProps):
    """Consruction properties for a CustomRule.

    Stability:
        experimental
    """
    lambdaFunction: aws_cdk.aws_lambda.IFunction
    """The Lambda function to run.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-config.ManagedRuleProps", jsii_struct_bases=[RuleProps])
class ManagedRuleProps(RuleProps, jsii.compat.TypedDict):
    """Construction properties for a ManagedRule.

    Stability:
        experimental
    """
    identifier: str
    """The identifier of the AWS managed rule.

    See:
        https://docs.aws.amazon.com/config/latest/developerguide/managed-rules-by-aws-config.html
    Stability:
        experimental
    """

__all__ = ["AccessKeysRotated", "AccessKeysRotatedProps", "CfnAggregationAuthorization", "CfnAggregationAuthorizationProps", "CfnConfigRule", "CfnConfigRuleProps", "CfnConfigurationAggregator", "CfnConfigurationAggregatorProps", "CfnConfigurationRecorder", "CfnConfigurationRecorderProps", "CfnDeliveryChannel", "CfnDeliveryChannelProps", "CloudFormationStackDriftDetectionCheck", "CloudFormationStackDriftDetectionCheckProps", "CloudFormationStackNotificationCheck", "CloudFormationStackNotificationCheckProps", "CustomRule", "CustomRuleProps", "IRule", "ManagedRule", "ManagedRuleProps", "MaximumExecutionFrequency", "RuleAttributes", "RuleProps", "__jsii_assembly__"]

publication.publish()
