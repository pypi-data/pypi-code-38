import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-apigateway", "0.34.0", __name__, "aws-apigateway@0.34.0.jsii.tgz")
@jsii.enum(jsii_type="@aws-cdk/aws-apigateway.ApiKey")
class ApiKey(enum.Enum):
    """
    Stability:
        experimental
    """
    pass

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.ApiKeyAttributes", jsii_struct_bases=[])
class ApiKeyAttributes(jsii.compat.TypedDict):
    """API keys are alphanumeric string values that you distribute to app developer customers to grant access to your API.

    Stability:
        experimental
    """
    keyId: str
    """The API key ID.

    Stability:
        experimental
    attribute:
        true
    """

@jsii.enum(jsii_type="@aws-cdk/aws-apigateway.ApiKeySourceType")
class ApiKeySourceType(enum.Enum):
    """
    Stability:
        experimental
    """
    Header = "Header"
    """To read the API key from the ``X-API-Key`` header of a request.

    Stability:
        experimental
    """
    Authorizer = "Authorizer"
    """To read the API key from the ``UsageIdentifierKey`` from a custom authorizer.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-apigateway.AuthorizationType")
class AuthorizationType(enum.Enum):
    """
    Stability:
        experimental
    """
    None_ = "None"
    """Open access.

    Stability:
        experimental
    """
    IAM = "IAM"
    """Use AWS IAM permissions.

    Stability:
        experimental
    """
    Custom = "Custom"
    """Use a custom authorizer.

    Stability:
        experimental
    """
    Cognito = "Cognito"
    """Use an AWS Cognito user pool.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _AwsIntegrationProps(jsii.compat.TypedDict, total=False):
    action: str
    """The AWS action to perform in the integration.

    Use ``actionParams`` to specify key-value params for the action.

    Mutually exclusive with ``path``.

    Stability:
        experimental
    """
    actionParameters: typing.Mapping[str,str]
    """Parameters for the action.

    ``action`` must be set, and ``path`` must be undefined.
    The action params will be URL encoded.

    Stability:
        experimental
    """
    integrationHttpMethod: str
    """The integration's HTTP method type.

    Default:
        POST

    Stability:
        experimental
    """
    options: "IntegrationOptions"
    """Integration options, such as content handling, request/response mapping, etc.

    Stability:
        experimental
    """
    path: str
    """The path to use for path-base APIs.

    For example, for S3 GET, you can set path to ``bucket/key``.
    For lambda, you can set path to ``2015-03-31/functions/${function-arn}/invocations``

    Mutually exclusive with the ``action`` options.

    Stability:
        experimental
    """
    proxy: bool
    """Use AWS_PROXY integration.

    Default:
        false

    Stability:
        experimental
    """
    subdomain: str
    """A designated subdomain supported by certain AWS service for fast host-name lookup.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.AwsIntegrationProps", jsii_struct_bases=[_AwsIntegrationProps])
class AwsIntegrationProps(_AwsIntegrationProps):
    """
    Stability:
        experimental
    """
    service: str
    """The name of the integrated AWS service (e.g. ``s3``).

    Stability:
        experimental
    """

class CfnAccount(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnAccount"):
    """A CloudFormation ``AWS::ApiGateway::Account``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-account.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::Account
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cloud_watch_role_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGateway::Account``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            cloudWatchRoleArn: ``AWS::ApiGateway::Account.CloudWatchRoleArn``.

        Stability:
            experimental
        """
        props: CfnAccountProps = {}

        if cloud_watch_role_arn is not None:
            props["cloudWatchRoleArn"] = cloud_watch_role_arn

        jsii.create(CfnAccount, self, [scope, id, props])

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
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "accountId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnAccountProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnAccountProps", jsii_struct_bases=[])
class CfnAccountProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::ApiGateway::Account``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-account.html
    Stability:
        experimental
    """
    cloudWatchRoleArn: str
    """``AWS::ApiGateway::Account.CloudWatchRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-account.html#cfn-apigateway-account-cloudwatchrolearn
    Stability:
        experimental
    """

class CfnApiKey(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnApiKey"):
    """A CloudFormation ``AWS::ApiGateway::ApiKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::ApiKey
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, customer_id: typing.Optional[str]=None, description: typing.Optional[str]=None, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, generate_distinct_id: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, name: typing.Optional[str]=None, stage_keys: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "StageKeyProperty"]]]]]=None, value: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGateway::ApiKey``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            customerId: ``AWS::ApiGateway::ApiKey.CustomerId``.
            description: ``AWS::ApiGateway::ApiKey.Description``.
            enabled: ``AWS::ApiGateway::ApiKey.Enabled``.
            generateDistinctId: ``AWS::ApiGateway::ApiKey.GenerateDistinctId``.
            name: ``AWS::ApiGateway::ApiKey.Name``.
            stageKeys: ``AWS::ApiGateway::ApiKey.StageKeys``.
            value: ``AWS::ApiGateway::ApiKey.Value``.

        Stability:
            experimental
        """
        props: CfnApiKeyProps = {}

        if customer_id is not None:
            props["customerId"] = customer_id

        if description is not None:
            props["description"] = description

        if enabled is not None:
            props["enabled"] = enabled

        if generate_distinct_id is not None:
            props["generateDistinctId"] = generate_distinct_id

        if name is not None:
            props["name"] = name

        if stage_keys is not None:
            props["stageKeys"] = stage_keys

        if value is not None:
            props["value"] = value

        jsii.create(CfnApiKey, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiKeyId")
    def api_key_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "apiKeyId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnApiKeyProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnApiKey.StageKeyProperty", jsii_struct_bases=[])
    class StageKeyProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-apikey-stagekey.html
        Stability:
            experimental
        """
        restApiId: str
        """``CfnApiKey.StageKeyProperty.RestApiId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-apikey-stagekey.html#cfn-apigateway-apikey-stagekey-restapiid
        Stability:
            experimental
        """

        stageName: str
        """``CfnApiKey.StageKeyProperty.StageName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-apikey-stagekey.html#cfn-apigateway-apikey-stagekey-stagename
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnApiKeyProps", jsii_struct_bases=[])
class CfnApiKeyProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::ApiGateway::ApiKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html
    Stability:
        experimental
    """
    customerId: str
    """``AWS::ApiGateway::ApiKey.CustomerId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html#cfn-apigateway-apikey-customerid
    Stability:
        experimental
    """

    description: str
    """``AWS::ApiGateway::ApiKey.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html#cfn-apigateway-apikey-description
    Stability:
        experimental
    """

    enabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ApiGateway::ApiKey.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html#cfn-apigateway-apikey-enabled
    Stability:
        experimental
    """

    generateDistinctId: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ApiGateway::ApiKey.GenerateDistinctId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html#cfn-apigateway-apikey-generatedistinctid
    Stability:
        experimental
    """

    name: str
    """``AWS::ApiGateway::ApiKey.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html#cfn-apigateway-apikey-name
    Stability:
        experimental
    """

    stageKeys: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnApiKey.StageKeyProperty"]]]
    """``AWS::ApiGateway::ApiKey.StageKeys``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html#cfn-apigateway-apikey-stagekeys
    Stability:
        experimental
    """

    value: str
    """``AWS::ApiGateway::ApiKey.Value``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html#cfn-apigateway-apikey-value
    Stability:
        experimental
    """

class CfnApiMappingV2(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnApiMappingV2"):
    """A CloudFormation ``AWS::ApiGatewayV2::ApiMapping``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGatewayV2::ApiMapping
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_id: str, domain_name: str, stage: str, api_mapping_key: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGatewayV2::ApiMapping``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            apiId: ``AWS::ApiGatewayV2::ApiMapping.ApiId``.
            domainName: ``AWS::ApiGatewayV2::ApiMapping.DomainName``.
            stage: ``AWS::ApiGatewayV2::ApiMapping.Stage``.
            apiMappingKey: ``AWS::ApiGatewayV2::ApiMapping.ApiMappingKey``.

        Stability:
            experimental
        """
        props: CfnApiMappingV2Props = {"apiId": api_id, "domainName": domain_name, "stage": stage}

        if api_mapping_key is not None:
            props["apiMappingKey"] = api_mapping_key

        jsii.create(CfnApiMappingV2, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiMappingId")
    def api_mapping_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "apiMappingId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnApiMappingV2Props":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnApiMappingV2Props(jsii.compat.TypedDict, total=False):
    apiMappingKey: str
    """``AWS::ApiGatewayV2::ApiMapping.ApiMappingKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html#cfn-apigatewayv2-apimapping-apimappingkey
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnApiMappingV2Props", jsii_struct_bases=[_CfnApiMappingV2Props])
class CfnApiMappingV2Props(_CfnApiMappingV2Props):
    """Properties for defining a ``AWS::ApiGatewayV2::ApiMapping``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html
    Stability:
        experimental
    """
    apiId: str
    """``AWS::ApiGatewayV2::ApiMapping.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html#cfn-apigatewayv2-apimapping-apiid
    Stability:
        experimental
    """

    domainName: str
    """``AWS::ApiGatewayV2::ApiMapping.DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html#cfn-apigatewayv2-apimapping-domainname
    Stability:
        experimental
    """

    stage: str
    """``AWS::ApiGatewayV2::ApiMapping.Stage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-apimapping.html#cfn-apigatewayv2-apimapping-stage
    Stability:
        experimental
    """

class CfnApiV2(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnApiV2"):
    """A CloudFormation ``AWS::ApiGatewayV2::Api``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGatewayV2::Api
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, protocol_type: str, route_selection_expression: str, api_key_selection_expression: typing.Optional[str]=None, description: typing.Optional[str]=None, disable_schema_validation: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, version: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGatewayV2::Api``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::ApiGatewayV2::Api.Name``.
            protocolType: ``AWS::ApiGatewayV2::Api.ProtocolType``.
            routeSelectionExpression: ``AWS::ApiGatewayV2::Api.RouteSelectionExpression``.
            apiKeySelectionExpression: ``AWS::ApiGatewayV2::Api.ApiKeySelectionExpression``.
            description: ``AWS::ApiGatewayV2::Api.Description``.
            disableSchemaValidation: ``AWS::ApiGatewayV2::Api.DisableSchemaValidation``.
            version: ``AWS::ApiGatewayV2::Api.Version``.

        Stability:
            experimental
        """
        props: CfnApiV2Props = {"name": name, "protocolType": protocol_type, "routeSelectionExpression": route_selection_expression}

        if api_key_selection_expression is not None:
            props["apiKeySelectionExpression"] = api_key_selection_expression

        if description is not None:
            props["description"] = description

        if disable_schema_validation is not None:
            props["disableSchemaValidation"] = disable_schema_validation

        if version is not None:
            props["version"] = version

        jsii.create(CfnApiV2, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "apiId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnApiV2Props":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnApiV2Props(jsii.compat.TypedDict, total=False):
    apiKeySelectionExpression: str
    """``AWS::ApiGatewayV2::Api.ApiKeySelectionExpression``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-apikeyselectionexpression
    Stability:
        experimental
    """
    description: str
    """``AWS::ApiGatewayV2::Api.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-description
    Stability:
        experimental
    """
    disableSchemaValidation: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::Api.DisableSchemaValidation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-disableschemavalidation
    Stability:
        experimental
    """
    version: str
    """``AWS::ApiGatewayV2::Api.Version``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-version
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnApiV2Props", jsii_struct_bases=[_CfnApiV2Props])
class CfnApiV2Props(_CfnApiV2Props):
    """Properties for defining a ``AWS::ApiGatewayV2::Api``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html
    Stability:
        experimental
    """
    name: str
    """``AWS::ApiGatewayV2::Api.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-name
    Stability:
        experimental
    """

    protocolType: str
    """``AWS::ApiGatewayV2::Api.ProtocolType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-protocoltype
    Stability:
        experimental
    """

    routeSelectionExpression: str
    """``AWS::ApiGatewayV2::Api.RouteSelectionExpression``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-api.html#cfn-apigatewayv2-api-routeselectionexpression
    Stability:
        experimental
    """

class CfnAuthorizer(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnAuthorizer"):
    """A CloudFormation ``AWS::ApiGateway::Authorizer``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::Authorizer
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, rest_api_id: str, type: str, authorizer_credentials: typing.Optional[str]=None, authorizer_result_ttl_in_seconds: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, authorizer_uri: typing.Optional[str]=None, auth_type: typing.Optional[str]=None, identity_source: typing.Optional[str]=None, identity_validation_expression: typing.Optional[str]=None, name: typing.Optional[str]=None, provider_arns: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::ApiGateway::Authorizer``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            restApiId: ``AWS::ApiGateway::Authorizer.RestApiId``.
            type: ``AWS::ApiGateway::Authorizer.Type``.
            authorizerCredentials: ``AWS::ApiGateway::Authorizer.AuthorizerCredentials``.
            authorizerResultTtlInSeconds: ``AWS::ApiGateway::Authorizer.AuthorizerResultTtlInSeconds``.
            authorizerUri: ``AWS::ApiGateway::Authorizer.AuthorizerUri``.
            authType: ``AWS::ApiGateway::Authorizer.AuthType``.
            identitySource: ``AWS::ApiGateway::Authorizer.IdentitySource``.
            identityValidationExpression: ``AWS::ApiGateway::Authorizer.IdentityValidationExpression``.
            name: ``AWS::ApiGateway::Authorizer.Name``.
            providerArns: ``AWS::ApiGateway::Authorizer.ProviderARNs``.

        Stability:
            experimental
        """
        props: CfnAuthorizerProps = {"restApiId": rest_api_id, "type": type}

        if authorizer_credentials is not None:
            props["authorizerCredentials"] = authorizer_credentials

        if authorizer_result_ttl_in_seconds is not None:
            props["authorizerResultTtlInSeconds"] = authorizer_result_ttl_in_seconds

        if authorizer_uri is not None:
            props["authorizerUri"] = authorizer_uri

        if auth_type is not None:
            props["authType"] = auth_type

        if identity_source is not None:
            props["identitySource"] = identity_source

        if identity_validation_expression is not None:
            props["identityValidationExpression"] = identity_validation_expression

        if name is not None:
            props["name"] = name

        if provider_arns is not None:
            props["providerArns"] = provider_arns

        jsii.create(CfnAuthorizer, self, [scope, id, props])

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
    @jsii.member(jsii_name="authorizerId")
    def authorizer_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "authorizerId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnAuthorizerProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAuthorizerProps(jsii.compat.TypedDict, total=False):
    authorizerCredentials: str
    """``AWS::ApiGateway::Authorizer.AuthorizerCredentials``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-authorizercredentials
    Stability:
        experimental
    """
    authorizerResultTtlInSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ApiGateway::Authorizer.AuthorizerResultTtlInSeconds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-authorizerresultttlinseconds
    Stability:
        experimental
    """
    authorizerUri: str
    """``AWS::ApiGateway::Authorizer.AuthorizerUri``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-authorizeruri
    Stability:
        experimental
    """
    authType: str
    """``AWS::ApiGateway::Authorizer.AuthType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-authtype
    Stability:
        experimental
    """
    identitySource: str
    """``AWS::ApiGateway::Authorizer.IdentitySource``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-identitysource
    Stability:
        experimental
    """
    identityValidationExpression: str
    """``AWS::ApiGateway::Authorizer.IdentityValidationExpression``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-identityvalidationexpression
    Stability:
        experimental
    """
    name: str
    """``AWS::ApiGateway::Authorizer.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-name
    Stability:
        experimental
    """
    providerArns: typing.List[str]
    """``AWS::ApiGateway::Authorizer.ProviderARNs``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-providerarns
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnAuthorizerProps", jsii_struct_bases=[_CfnAuthorizerProps])
class CfnAuthorizerProps(_CfnAuthorizerProps):
    """Properties for defining a ``AWS::ApiGateway::Authorizer``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html
    Stability:
        experimental
    """
    restApiId: str
    """``AWS::ApiGateway::Authorizer.RestApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-restapiid
    Stability:
        experimental
    """

    type: str
    """``AWS::ApiGateway::Authorizer.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-type
    Stability:
        experimental
    """

class CfnAuthorizerV2(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnAuthorizerV2"):
    """A CloudFormation ``AWS::ApiGatewayV2::Authorizer``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGatewayV2::Authorizer
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_id: str, authorizer_type: str, authorizer_uri: str, identity_source: typing.List[str], name: str, authorizer_credentials_arn: typing.Optional[str]=None, authorizer_result_ttl_in_seconds: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, identity_validation_expression: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGatewayV2::Authorizer``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            apiId: ``AWS::ApiGatewayV2::Authorizer.ApiId``.
            authorizerType: ``AWS::ApiGatewayV2::Authorizer.AuthorizerType``.
            authorizerUri: ``AWS::ApiGatewayV2::Authorizer.AuthorizerUri``.
            identitySource: ``AWS::ApiGatewayV2::Authorizer.IdentitySource``.
            name: ``AWS::ApiGatewayV2::Authorizer.Name``.
            authorizerCredentialsArn: ``AWS::ApiGatewayV2::Authorizer.AuthorizerCredentialsArn``.
            authorizerResultTtlInSeconds: ``AWS::ApiGatewayV2::Authorizer.AuthorizerResultTtlInSeconds``.
            identityValidationExpression: ``AWS::ApiGatewayV2::Authorizer.IdentityValidationExpression``.

        Stability:
            experimental
        """
        props: CfnAuthorizerV2Props = {"apiId": api_id, "authorizerType": authorizer_type, "authorizerUri": authorizer_uri, "identitySource": identity_source, "name": name}

        if authorizer_credentials_arn is not None:
            props["authorizerCredentialsArn"] = authorizer_credentials_arn

        if authorizer_result_ttl_in_seconds is not None:
            props["authorizerResultTtlInSeconds"] = authorizer_result_ttl_in_seconds

        if identity_validation_expression is not None:
            props["identityValidationExpression"] = identity_validation_expression

        jsii.create(CfnAuthorizerV2, self, [scope, id, props])

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
    @jsii.member(jsii_name="authorizerId")
    def authorizer_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "authorizerId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnAuthorizerV2Props":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAuthorizerV2Props(jsii.compat.TypedDict, total=False):
    authorizerCredentialsArn: str
    """``AWS::ApiGatewayV2::Authorizer.AuthorizerCredentialsArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizercredentialsarn
    Stability:
        experimental
    """
    authorizerResultTtlInSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::Authorizer.AuthorizerResultTtlInSeconds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizerresultttlinseconds
    Stability:
        experimental
    """
    identityValidationExpression: str
    """``AWS::ApiGatewayV2::Authorizer.IdentityValidationExpression``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-identityvalidationexpression
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnAuthorizerV2Props", jsii_struct_bases=[_CfnAuthorizerV2Props])
class CfnAuthorizerV2Props(_CfnAuthorizerV2Props):
    """Properties for defining a ``AWS::ApiGatewayV2::Authorizer``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html
    Stability:
        experimental
    """
    apiId: str
    """``AWS::ApiGatewayV2::Authorizer.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-apiid
    Stability:
        experimental
    """

    authorizerType: str
    """``AWS::ApiGatewayV2::Authorizer.AuthorizerType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizertype
    Stability:
        experimental
    """

    authorizerUri: str
    """``AWS::ApiGatewayV2::Authorizer.AuthorizerUri``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-authorizeruri
    Stability:
        experimental
    """

    identitySource: typing.List[str]
    """``AWS::ApiGatewayV2::Authorizer.IdentitySource``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-identitysource
    Stability:
        experimental
    """

    name: str
    """``AWS::ApiGatewayV2::Authorizer.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html#cfn-apigatewayv2-authorizer-name
    Stability:
        experimental
    """

class CfnBasePathMapping(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnBasePathMapping"):
    """A CloudFormation ``AWS::ApiGateway::BasePathMapping``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-basepathmapping.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::BasePathMapping
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, domain_name: str, base_path: typing.Optional[str]=None, rest_api_id: typing.Optional[str]=None, stage: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGateway::BasePathMapping``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            domainName: ``AWS::ApiGateway::BasePathMapping.DomainName``.
            basePath: ``AWS::ApiGateway::BasePathMapping.BasePath``.
            restApiId: ``AWS::ApiGateway::BasePathMapping.RestApiId``.
            stage: ``AWS::ApiGateway::BasePathMapping.Stage``.

        Stability:
            experimental
        """
        props: CfnBasePathMappingProps = {"domainName": domain_name}

        if base_path is not None:
            props["basePath"] = base_path

        if rest_api_id is not None:
            props["restApiId"] = rest_api_id

        if stage is not None:
            props["stage"] = stage

        jsii.create(CfnBasePathMapping, self, [scope, id, props])

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
    @jsii.member(jsii_name="basePathMappingId")
    def base_path_mapping_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "basePathMappingId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnBasePathMappingProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnBasePathMappingProps(jsii.compat.TypedDict, total=False):
    basePath: str
    """``AWS::ApiGateway::BasePathMapping.BasePath``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-basepathmapping.html#cfn-apigateway-basepathmapping-basepath
    Stability:
        experimental
    """
    restApiId: str
    """``AWS::ApiGateway::BasePathMapping.RestApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-basepathmapping.html#cfn-apigateway-basepathmapping-restapiid
    Stability:
        experimental
    """
    stage: str
    """``AWS::ApiGateway::BasePathMapping.Stage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-basepathmapping.html#cfn-apigateway-basepathmapping-stage
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnBasePathMappingProps", jsii_struct_bases=[_CfnBasePathMappingProps])
class CfnBasePathMappingProps(_CfnBasePathMappingProps):
    """Properties for defining a ``AWS::ApiGateway::BasePathMapping``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-basepathmapping.html
    Stability:
        experimental
    """
    domainName: str
    """``AWS::ApiGateway::BasePathMapping.DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-basepathmapping.html#cfn-apigateway-basepathmapping-domainname
    Stability:
        experimental
    """

class CfnClientCertificate(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnClientCertificate"):
    """A CloudFormation ``AWS::ApiGateway::ClientCertificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-clientcertificate.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::ClientCertificate
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGateway::ClientCertificate``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::ApiGateway::ClientCertificate.Description``.

        Stability:
            experimental
        """
        props: CfnClientCertificateProps = {}

        if description is not None:
            props["description"] = description

        jsii.create(CfnClientCertificate, self, [scope, id, props])

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
    @jsii.member(jsii_name="clientCertificateName")
    def client_certificate_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "clientCertificateName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnClientCertificateProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnClientCertificateProps", jsii_struct_bases=[])
class CfnClientCertificateProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::ApiGateway::ClientCertificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-clientcertificate.html
    Stability:
        experimental
    """
    description: str
    """``AWS::ApiGateway::ClientCertificate.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-clientcertificate.html#cfn-apigateway-clientcertificate-description
    Stability:
        experimental
    """

class CfnDeployment(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnDeployment"):
    """A CloudFormation ``AWS::ApiGateway::Deployment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-deployment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::Deployment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, rest_api_id: str, deployment_canary_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["DeploymentCanarySettingsProperty"]]]=None, description: typing.Optional[str]=None, stage_description: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["StageDescriptionProperty"]]]=None, stage_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGateway::Deployment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            restApiId: ``AWS::ApiGateway::Deployment.RestApiId``.
            deploymentCanarySettings: ``AWS::ApiGateway::Deployment.DeploymentCanarySettings``.
            description: ``AWS::ApiGateway::Deployment.Description``.
            stageDescription: ``AWS::ApiGateway::Deployment.StageDescription``.
            stageName: ``AWS::ApiGateway::Deployment.StageName``.

        Stability:
            experimental
        """
        props: CfnDeploymentProps = {"restApiId": rest_api_id}

        if deployment_canary_settings is not None:
            props["deploymentCanarySettings"] = deployment_canary_settings

        if description is not None:
            props["description"] = description

        if stage_description is not None:
            props["stageDescription"] = stage_description

        if stage_name is not None:
            props["stageName"] = stage_name

        jsii.create(CfnDeployment, self, [scope, id, props])

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
    @jsii.member(jsii_name="deploymentId")
    def deployment_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDeploymentProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDeployment.AccessLogSettingProperty", jsii_struct_bases=[])
    class AccessLogSettingProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-accesslogsetting.html
        Stability:
            experimental
        """
        destinationArn: str
        """``CfnDeployment.AccessLogSettingProperty.DestinationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-accesslogsetting.html#cfn-apigateway-deployment-accesslogsetting-destinationarn
        Stability:
            experimental
        """

        format: str
        """``CfnDeployment.AccessLogSettingProperty.Format``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-accesslogsetting.html#cfn-apigateway-deployment-accesslogsetting-format
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDeployment.CanarySettingProperty", jsii_struct_bases=[])
    class CanarySettingProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-canarysetting.html
        Stability:
            experimental
        """
        percentTraffic: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeployment.CanarySettingProperty.PercentTraffic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-canarysetting.html#cfn-apigateway-deployment-canarysetting-percenttraffic
        Stability:
            experimental
        """

        stageVariableOverrides: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnDeployment.CanarySettingProperty.StageVariableOverrides``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-canarysetting.html#cfn-apigateway-deployment-canarysetting-stagevariableoverrides
        Stability:
            experimental
        """

        useStageCache: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeployment.CanarySettingProperty.UseStageCache``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-canarysetting.html#cfn-apigateway-deployment-canarysetting-usestagecache
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDeployment.DeploymentCanarySettingsProperty", jsii_struct_bases=[])
    class DeploymentCanarySettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-deploymentcanarysettings.html
        Stability:
            experimental
        """
        percentTraffic: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeployment.DeploymentCanarySettingsProperty.PercentTraffic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-deploymentcanarysettings.html#cfn-apigateway-deployment-deploymentcanarysettings-percenttraffic
        Stability:
            experimental
        """

        stageVariableOverrides: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnDeployment.DeploymentCanarySettingsProperty.StageVariableOverrides``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-deploymentcanarysettings.html#cfn-apigateway-deployment-deploymentcanarysettings-stagevariableoverrides
        Stability:
            experimental
        """

        useStageCache: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeployment.DeploymentCanarySettingsProperty.UseStageCache``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-deploymentcanarysettings.html#cfn-apigateway-deployment-deploymentcanarysettings-usestagecache
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDeployment.MethodSettingProperty", jsii_struct_bases=[])
    class MethodSettingProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription-methodsetting.html
        Stability:
            experimental
        """
        cacheDataEncrypted: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeployment.MethodSettingProperty.CacheDataEncrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription-methodsetting.html#cfn-apigateway-deployment-stagedescription-methodsetting-cachedataencrypted
        Stability:
            experimental
        """

        cacheTtlInSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeployment.MethodSettingProperty.CacheTtlInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription-methodsetting.html#cfn-apigateway-deployment-stagedescription-methodsetting-cachettlinseconds
        Stability:
            experimental
        """

        cachingEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeployment.MethodSettingProperty.CachingEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription-methodsetting.html#cfn-apigateway-deployment-stagedescription-methodsetting-cachingenabled
        Stability:
            experimental
        """

        dataTraceEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeployment.MethodSettingProperty.DataTraceEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription-methodsetting.html#cfn-apigateway-deployment-stagedescription-methodsetting-datatraceenabled
        Stability:
            experimental
        """

        httpMethod: str
        """``CfnDeployment.MethodSettingProperty.HttpMethod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription-methodsetting.html#cfn-apigateway-deployment-stagedescription-methodsetting-httpmethod
        Stability:
            experimental
        """

        loggingLevel: str
        """``CfnDeployment.MethodSettingProperty.LoggingLevel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription-methodsetting.html#cfn-apigateway-deployment-stagedescription-methodsetting-logginglevel
        Stability:
            experimental
        """

        metricsEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeployment.MethodSettingProperty.MetricsEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription-methodsetting.html#cfn-apigateway-deployment-stagedescription-methodsetting-metricsenabled
        Stability:
            experimental
        """

        resourcePath: str
        """``CfnDeployment.MethodSettingProperty.ResourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription-methodsetting.html#cfn-apigateway-deployment-stagedescription-methodsetting-resourcepath
        Stability:
            experimental
        """

        throttlingBurstLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeployment.MethodSettingProperty.ThrottlingBurstLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription-methodsetting.html#cfn-apigateway-deployment-stagedescription-methodsetting-throttlingburstlimit
        Stability:
            experimental
        """

        throttlingRateLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeployment.MethodSettingProperty.ThrottlingRateLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription-methodsetting.html#cfn-apigateway-deployment-stagedescription-methodsetting-throttlingratelimit
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDeployment.StageDescriptionProperty", jsii_struct_bases=[])
    class StageDescriptionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html
        Stability:
            experimental
        """
        accessLogSetting: typing.Union[aws_cdk.cdk.Token, "CfnDeployment.AccessLogSettingProperty"]
        """``CfnDeployment.StageDescriptionProperty.AccessLogSetting``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-accesslogsetting
        Stability:
            experimental
        """

        cacheClusterEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeployment.StageDescriptionProperty.CacheClusterEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-cacheclusterenabled
        Stability:
            experimental
        """

        cacheClusterSize: str
        """``CfnDeployment.StageDescriptionProperty.CacheClusterSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-cacheclustersize
        Stability:
            experimental
        """

        cacheDataEncrypted: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeployment.StageDescriptionProperty.CacheDataEncrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-cachedataencrypted
        Stability:
            experimental
        """

        cacheTtlInSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeployment.StageDescriptionProperty.CacheTtlInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-cachettlinseconds
        Stability:
            experimental
        """

        cachingEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeployment.StageDescriptionProperty.CachingEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-cachingenabled
        Stability:
            experimental
        """

        canarySetting: typing.Union[aws_cdk.cdk.Token, "CfnDeployment.CanarySettingProperty"]
        """``CfnDeployment.StageDescriptionProperty.CanarySetting``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-canarysetting
        Stability:
            experimental
        """

        clientCertificateId: str
        """``CfnDeployment.StageDescriptionProperty.ClientCertificateId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-clientcertificateid
        Stability:
            experimental
        """

        dataTraceEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeployment.StageDescriptionProperty.DataTraceEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-datatraceenabled
        Stability:
            experimental
        """

        description: str
        """``CfnDeployment.StageDescriptionProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-description
        Stability:
            experimental
        """

        documentationVersion: str
        """``CfnDeployment.StageDescriptionProperty.DocumentationVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-documentationversion
        Stability:
            experimental
        """

        loggingLevel: str
        """``CfnDeployment.StageDescriptionProperty.LoggingLevel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-logginglevel
        Stability:
            experimental
        """

        methodSettings: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeployment.MethodSettingProperty"]]]
        """``CfnDeployment.StageDescriptionProperty.MethodSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-methodsettings
        Stability:
            experimental
        """

        metricsEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeployment.StageDescriptionProperty.MetricsEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-metricsenabled
        Stability:
            experimental
        """

        tags: typing.List[aws_cdk.cdk.CfnTag]
        """``CfnDeployment.StageDescriptionProperty.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-tags
        Stability:
            experimental
        """

        throttlingBurstLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeployment.StageDescriptionProperty.ThrottlingBurstLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-throttlingburstlimit
        Stability:
            experimental
        """

        throttlingRateLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeployment.StageDescriptionProperty.ThrottlingRateLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-throttlingratelimit
        Stability:
            experimental
        """

        tracingEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeployment.StageDescriptionProperty.TracingEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-tracingenabled
        Stability:
            experimental
        """

        variables: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnDeployment.StageDescriptionProperty.Variables``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-deployment-stagedescription.html#cfn-apigateway-deployment-stagedescription-variables
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDeploymentProps(jsii.compat.TypedDict, total=False):
    deploymentCanarySettings: typing.Union[aws_cdk.cdk.Token, "CfnDeployment.DeploymentCanarySettingsProperty"]
    """``AWS::ApiGateway::Deployment.DeploymentCanarySettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-deployment.html#cfn-apigateway-deployment-deploymentcanarysettings
    Stability:
        experimental
    """
    description: str
    """``AWS::ApiGateway::Deployment.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-deployment.html#cfn-apigateway-deployment-description
    Stability:
        experimental
    """
    stageDescription: typing.Union[aws_cdk.cdk.Token, "CfnDeployment.StageDescriptionProperty"]
    """``AWS::ApiGateway::Deployment.StageDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-deployment.html#cfn-apigateway-deployment-stagedescription
    Stability:
        experimental
    """
    stageName: str
    """``AWS::ApiGateway::Deployment.StageName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-deployment.html#cfn-apigateway-deployment-stagename
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDeploymentProps", jsii_struct_bases=[_CfnDeploymentProps])
class CfnDeploymentProps(_CfnDeploymentProps):
    """Properties for defining a ``AWS::ApiGateway::Deployment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-deployment.html
    Stability:
        experimental
    """
    restApiId: str
    """``AWS::ApiGateway::Deployment.RestApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-deployment.html#cfn-apigateway-deployment-restapiid
    Stability:
        experimental
    """

class CfnDeploymentV2(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnDeploymentV2"):
    """A CloudFormation ``AWS::ApiGatewayV2::Deployment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGatewayV2::Deployment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_id: str, description: typing.Optional[str]=None, stage_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGatewayV2::Deployment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            apiId: ``AWS::ApiGatewayV2::Deployment.ApiId``.
            description: ``AWS::ApiGatewayV2::Deployment.Description``.
            stageName: ``AWS::ApiGatewayV2::Deployment.StageName``.

        Stability:
            experimental
        """
        props: CfnDeploymentV2Props = {"apiId": api_id}

        if description is not None:
            props["description"] = description

        if stage_name is not None:
            props["stageName"] = stage_name

        jsii.create(CfnDeploymentV2, self, [scope, id, props])

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
    @jsii.member(jsii_name="deploymentId")
    def deployment_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDeploymentV2Props":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDeploymentV2Props(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::ApiGatewayV2::Deployment.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html#cfn-apigatewayv2-deployment-description
    Stability:
        experimental
    """
    stageName: str
    """``AWS::ApiGatewayV2::Deployment.StageName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html#cfn-apigatewayv2-deployment-stagename
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDeploymentV2Props", jsii_struct_bases=[_CfnDeploymentV2Props])
class CfnDeploymentV2Props(_CfnDeploymentV2Props):
    """Properties for defining a ``AWS::ApiGatewayV2::Deployment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html
    Stability:
        experimental
    """
    apiId: str
    """``AWS::ApiGatewayV2::Deployment.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-deployment.html#cfn-apigatewayv2-deployment-apiid
    Stability:
        experimental
    """

class CfnDocumentationPart(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnDocumentationPart"):
    """A CloudFormation ``AWS::ApiGateway::DocumentationPart``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-documentationpart.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::DocumentationPart
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, location: typing.Union[aws_cdk.cdk.Token, "LocationProperty"], properties: str, rest_api_id: str) -> None:
        """Create a new ``AWS::ApiGateway::DocumentationPart``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            location: ``AWS::ApiGateway::DocumentationPart.Location``.
            properties: ``AWS::ApiGateway::DocumentationPart.Properties``.
            restApiId: ``AWS::ApiGateway::DocumentationPart.RestApiId``.

        Stability:
            experimental
        """
        props: CfnDocumentationPartProps = {"location": location, "properties": properties, "restApiId": rest_api_id}

        jsii.create(CfnDocumentationPart, self, [scope, id, props])

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
    @jsii.member(jsii_name="documentationPartId")
    def documentation_part_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "documentationPartId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDocumentationPartProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDocumentationPart.LocationProperty", jsii_struct_bases=[])
    class LocationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-documentationpart-location.html
        Stability:
            experimental
        """
        method: str
        """``CfnDocumentationPart.LocationProperty.Method``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-documentationpart-location.html#cfn-apigateway-documentationpart-location-method
        Stability:
            experimental
        """

        name: str
        """``CfnDocumentationPart.LocationProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-documentationpart-location.html#cfn-apigateway-documentationpart-location-name
        Stability:
            experimental
        """

        path: str
        """``CfnDocumentationPart.LocationProperty.Path``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-documentationpart-location.html#cfn-apigateway-documentationpart-location-path
        Stability:
            experimental
        """

        statusCode: str
        """``CfnDocumentationPart.LocationProperty.StatusCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-documentationpart-location.html#cfn-apigateway-documentationpart-location-statuscode
        Stability:
            experimental
        """

        type: str
        """``CfnDocumentationPart.LocationProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-documentationpart-location.html#cfn-apigateway-documentationpart-location-type
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDocumentationPartProps", jsii_struct_bases=[])
class CfnDocumentationPartProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::ApiGateway::DocumentationPart``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-documentationpart.html
    Stability:
        experimental
    """
    location: typing.Union[aws_cdk.cdk.Token, "CfnDocumentationPart.LocationProperty"]
    """``AWS::ApiGateway::DocumentationPart.Location``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-documentationpart.html#cfn-apigateway-documentationpart-location
    Stability:
        experimental
    """

    properties: str
    """``AWS::ApiGateway::DocumentationPart.Properties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-documentationpart.html#cfn-apigateway-documentationpart-properties
    Stability:
        experimental
    """

    restApiId: str
    """``AWS::ApiGateway::DocumentationPart.RestApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-documentationpart.html#cfn-apigateway-documentationpart-restapiid
    Stability:
        experimental
    """

class CfnDocumentationVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnDocumentationVersion"):
    """A CloudFormation ``AWS::ApiGateway::DocumentationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-documentationversion.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::DocumentationVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, documentation_version: str, rest_api_id: str, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGateway::DocumentationVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            documentationVersion: ``AWS::ApiGateway::DocumentationVersion.DocumentationVersion``.
            restApiId: ``AWS::ApiGateway::DocumentationVersion.RestApiId``.
            description: ``AWS::ApiGateway::DocumentationVersion.Description``.

        Stability:
            experimental
        """
        props: CfnDocumentationVersionProps = {"documentationVersion": documentation_version, "restApiId": rest_api_id}

        if description is not None:
            props["description"] = description

        jsii.create(CfnDocumentationVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="documentationVersionId")
    def documentation_version_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "documentationVersionId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDocumentationVersionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDocumentationVersionProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::ApiGateway::DocumentationVersion.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-documentationversion.html#cfn-apigateway-documentationversion-description
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDocumentationVersionProps", jsii_struct_bases=[_CfnDocumentationVersionProps])
class CfnDocumentationVersionProps(_CfnDocumentationVersionProps):
    """Properties for defining a ``AWS::ApiGateway::DocumentationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-documentationversion.html
    Stability:
        experimental
    """
    documentationVersion: str
    """``AWS::ApiGateway::DocumentationVersion.DocumentationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-documentationversion.html#cfn-apigateway-documentationversion-documentationversion
    Stability:
        experimental
    """

    restApiId: str
    """``AWS::ApiGateway::DocumentationVersion.RestApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-documentationversion.html#cfn-apigateway-documentationversion-restapiid
    Stability:
        experimental
    """

class CfnDomainName(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnDomainName"):
    """A CloudFormation ``AWS::ApiGateway::DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-domainname.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::DomainName
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, domain_name: str, certificate_arn: typing.Optional[str]=None, endpoint_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["EndpointConfigurationProperty"]]]=None, regional_certificate_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGateway::DomainName``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            domainName: ``AWS::ApiGateway::DomainName.DomainName``.
            certificateArn: ``AWS::ApiGateway::DomainName.CertificateArn``.
            endpointConfiguration: ``AWS::ApiGateway::DomainName.EndpointConfiguration``.
            regionalCertificateArn: ``AWS::ApiGateway::DomainName.RegionalCertificateArn``.

        Stability:
            experimental
        """
        props: CfnDomainNameProps = {"domainName": domain_name}

        if certificate_arn is not None:
            props["certificateArn"] = certificate_arn

        if endpoint_configuration is not None:
            props["endpointConfiguration"] = endpoint_configuration

        if regional_certificate_arn is not None:
            props["regionalCertificateArn"] = regional_certificate_arn

        jsii.create(CfnDomainName, self, [scope, id, props])

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
    @jsii.member(jsii_name="domainNameDistributionDomainName")
    def domain_name_distribution_domain_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DistributionDomainName
        """
        return jsii.get(self, "domainNameDistributionDomainName")

    @property
    @jsii.member(jsii_name="domainNameDistributionHostedZoneId")
    def domain_name_distribution_hosted_zone_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DistributionHostedZoneId
        """
        return jsii.get(self, "domainNameDistributionHostedZoneId")

    @property
    @jsii.member(jsii_name="domainNameName")
    def domain_name_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "domainNameName")

    @property
    @jsii.member(jsii_name="domainNameRegionalDomainName")
    def domain_name_regional_domain_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RegionalDomainName
        """
        return jsii.get(self, "domainNameRegionalDomainName")

    @property
    @jsii.member(jsii_name="domainNameRegionalHostedZoneId")
    def domain_name_regional_hosted_zone_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RegionalHostedZoneId
        """
        return jsii.get(self, "domainNameRegionalHostedZoneId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDomainNameProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDomainName.EndpointConfigurationProperty", jsii_struct_bases=[])
    class EndpointConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-domainname-endpointconfiguration.html
        Stability:
            experimental
        """
        types: typing.List[str]
        """``CfnDomainName.EndpointConfigurationProperty.Types``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-domainname-endpointconfiguration.html#cfn-apigateway-domainname-endpointconfiguration-types
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDomainNameProps(jsii.compat.TypedDict, total=False):
    certificateArn: str
    """``AWS::ApiGateway::DomainName.CertificateArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-domainname.html#cfn-apigateway-domainname-certificatearn
    Stability:
        experimental
    """
    endpointConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDomainName.EndpointConfigurationProperty"]
    """``AWS::ApiGateway::DomainName.EndpointConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-domainname.html#cfn-apigateway-domainname-endpointconfiguration
    Stability:
        experimental
    """
    regionalCertificateArn: str
    """``AWS::ApiGateway::DomainName.RegionalCertificateArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-domainname.html#cfn-apigateway-domainname-regionalcertificatearn
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDomainNameProps", jsii_struct_bases=[_CfnDomainNameProps])
class CfnDomainNameProps(_CfnDomainNameProps):
    """Properties for defining a ``AWS::ApiGateway::DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-domainname.html
    Stability:
        experimental
    """
    domainName: str
    """``AWS::ApiGateway::DomainName.DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-domainname.html#cfn-apigateway-domainname-domainname
    Stability:
        experimental
    """

class CfnDomainNameV2(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnDomainNameV2"):
    """A CloudFormation ``AWS::ApiGatewayV2::DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGatewayV2::DomainName
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, domain_name: str, domain_name_configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "DomainNameConfigurationProperty"]]]]]=None) -> None:
        """Create a new ``AWS::ApiGatewayV2::DomainName``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            domainName: ``AWS::ApiGatewayV2::DomainName.DomainName``.
            domainNameConfigurations: ``AWS::ApiGatewayV2::DomainName.DomainNameConfigurations``.

        Stability:
            experimental
        """
        props: CfnDomainNameV2Props = {"domainName": domain_name}

        if domain_name_configurations is not None:
            props["domainNameConfigurations"] = domain_name_configurations

        jsii.create(CfnDomainNameV2, self, [scope, id, props])

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
    @jsii.member(jsii_name="domainNameName")
    def domain_name_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "domainNameName")

    @property
    @jsii.member(jsii_name="domainNameRegionalDomainName")
    def domain_name_regional_domain_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RegionalDomainName
        """
        return jsii.get(self, "domainNameRegionalDomainName")

    @property
    @jsii.member(jsii_name="domainNameRegionalHostedZoneId")
    def domain_name_regional_hosted_zone_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RegionalHostedZoneId
        """
        return jsii.get(self, "domainNameRegionalHostedZoneId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDomainNameV2Props":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDomainNameV2.DomainNameConfigurationProperty", jsii_struct_bases=[])
    class DomainNameConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-domainname-domainnameconfiguration.html
        Stability:
            experimental
        """
        certificateArn: str
        """``CfnDomainNameV2.DomainNameConfigurationProperty.CertificateArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-domainname-domainnameconfiguration.html#cfn-apigatewayv2-domainname-domainnameconfiguration-certificatearn
        Stability:
            experimental
        """

        certificateName: str
        """``CfnDomainNameV2.DomainNameConfigurationProperty.CertificateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-domainname-domainnameconfiguration.html#cfn-apigatewayv2-domainname-domainnameconfiguration-certificatename
        Stability:
            experimental
        """

        endpointType: str
        """``CfnDomainNameV2.DomainNameConfigurationProperty.EndpointType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-domainname-domainnameconfiguration.html#cfn-apigatewayv2-domainname-domainnameconfiguration-endpointtype
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDomainNameV2Props(jsii.compat.TypedDict, total=False):
    domainNameConfigurations: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDomainNameV2.DomainNameConfigurationProperty"]]]
    """``AWS::ApiGatewayV2::DomainName.DomainNameConfigurations``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html#cfn-apigatewayv2-domainname-domainnameconfigurations
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnDomainNameV2Props", jsii_struct_bases=[_CfnDomainNameV2Props])
class CfnDomainNameV2Props(_CfnDomainNameV2Props):
    """Properties for defining a ``AWS::ApiGatewayV2::DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html
    Stability:
        experimental
    """
    domainName: str
    """``AWS::ApiGatewayV2::DomainName.DomainName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-domainname.html#cfn-apigatewayv2-domainname-domainname
    Stability:
        experimental
    """

class CfnGatewayResponse(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnGatewayResponse"):
    """A CloudFormation ``AWS::ApiGateway::GatewayResponse``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-gatewayresponse.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::GatewayResponse
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, response_type: str, rest_api_id: str, response_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.Mapping[str,str]]]]=None, response_templates: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.Mapping[str,str]]]]=None, status_code: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGateway::GatewayResponse``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            responseType: ``AWS::ApiGateway::GatewayResponse.ResponseType``.
            restApiId: ``AWS::ApiGateway::GatewayResponse.RestApiId``.
            responseParameters: ``AWS::ApiGateway::GatewayResponse.ResponseParameters``.
            responseTemplates: ``AWS::ApiGateway::GatewayResponse.ResponseTemplates``.
            statusCode: ``AWS::ApiGateway::GatewayResponse.StatusCode``.

        Stability:
            experimental
        """
        props: CfnGatewayResponseProps = {"responseType": response_type, "restApiId": rest_api_id}

        if response_parameters is not None:
            props["responseParameters"] = response_parameters

        if response_templates is not None:
            props["responseTemplates"] = response_templates

        if status_code is not None:
            props["statusCode"] = status_code

        jsii.create(CfnGatewayResponse, self, [scope, id, props])

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
    @jsii.member(jsii_name="gatewayResponseId")
    def gateway_response_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "gatewayResponseId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnGatewayResponseProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnGatewayResponseProps(jsii.compat.TypedDict, total=False):
    responseParameters: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
    """``AWS::ApiGateway::GatewayResponse.ResponseParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-gatewayresponse.html#cfn-apigateway-gatewayresponse-responseparameters
    Stability:
        experimental
    """
    responseTemplates: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
    """``AWS::ApiGateway::GatewayResponse.ResponseTemplates``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-gatewayresponse.html#cfn-apigateway-gatewayresponse-responsetemplates
    Stability:
        experimental
    """
    statusCode: str
    """``AWS::ApiGateway::GatewayResponse.StatusCode``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-gatewayresponse.html#cfn-apigateway-gatewayresponse-statuscode
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnGatewayResponseProps", jsii_struct_bases=[_CfnGatewayResponseProps])
class CfnGatewayResponseProps(_CfnGatewayResponseProps):
    """Properties for defining a ``AWS::ApiGateway::GatewayResponse``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-gatewayresponse.html
    Stability:
        experimental
    """
    responseType: str
    """``AWS::ApiGateway::GatewayResponse.ResponseType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-gatewayresponse.html#cfn-apigateway-gatewayresponse-responsetype
    Stability:
        experimental
    """

    restApiId: str
    """``AWS::ApiGateway::GatewayResponse.RestApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-gatewayresponse.html#cfn-apigateway-gatewayresponse-restapiid
    Stability:
        experimental
    """

class CfnIntegrationResponseV2(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnIntegrationResponseV2"):
    """A CloudFormation ``AWS::ApiGatewayV2::IntegrationResponse``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGatewayV2::IntegrationResponse
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_id: str, integration_id: str, integration_response_key: str, content_handling_strategy: typing.Optional[str]=None, response_parameters: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, response_templates: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, template_selection_expression: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGatewayV2::IntegrationResponse``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            apiId: ``AWS::ApiGatewayV2::IntegrationResponse.ApiId``.
            integrationId: ``AWS::ApiGatewayV2::IntegrationResponse.IntegrationId``.
            integrationResponseKey: ``AWS::ApiGatewayV2::IntegrationResponse.IntegrationResponseKey``.
            contentHandlingStrategy: ``AWS::ApiGatewayV2::IntegrationResponse.ContentHandlingStrategy``.
            responseParameters: ``AWS::ApiGatewayV2::IntegrationResponse.ResponseParameters``.
            responseTemplates: ``AWS::ApiGatewayV2::IntegrationResponse.ResponseTemplates``.
            templateSelectionExpression: ``AWS::ApiGatewayV2::IntegrationResponse.TemplateSelectionExpression``.

        Stability:
            experimental
        """
        props: CfnIntegrationResponseV2Props = {"apiId": api_id, "integrationId": integration_id, "integrationResponseKey": integration_response_key}

        if content_handling_strategy is not None:
            props["contentHandlingStrategy"] = content_handling_strategy

        if response_parameters is not None:
            props["responseParameters"] = response_parameters

        if response_templates is not None:
            props["responseTemplates"] = response_templates

        if template_selection_expression is not None:
            props["templateSelectionExpression"] = template_selection_expression

        jsii.create(CfnIntegrationResponseV2, self, [scope, id, props])

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
    @jsii.member(jsii_name="integrationResponseId")
    def integration_response_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "integrationResponseId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnIntegrationResponseV2Props":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnIntegrationResponseV2Props(jsii.compat.TypedDict, total=False):
    contentHandlingStrategy: str
    """``AWS::ApiGatewayV2::IntegrationResponse.ContentHandlingStrategy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-contenthandlingstrategy
    Stability:
        experimental
    """
    responseParameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::IntegrationResponse.ResponseParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-responseparameters
    Stability:
        experimental
    """
    responseTemplates: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::IntegrationResponse.ResponseTemplates``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-responsetemplates
    Stability:
        experimental
    """
    templateSelectionExpression: str
    """``AWS::ApiGatewayV2::IntegrationResponse.TemplateSelectionExpression``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-templateselectionexpression
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnIntegrationResponseV2Props", jsii_struct_bases=[_CfnIntegrationResponseV2Props])
class CfnIntegrationResponseV2Props(_CfnIntegrationResponseV2Props):
    """Properties for defining a ``AWS::ApiGatewayV2::IntegrationResponse``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html
    Stability:
        experimental
    """
    apiId: str
    """``AWS::ApiGatewayV2::IntegrationResponse.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-apiid
    Stability:
        experimental
    """

    integrationId: str
    """``AWS::ApiGatewayV2::IntegrationResponse.IntegrationId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-integrationid
    Stability:
        experimental
    """

    integrationResponseKey: str
    """``AWS::ApiGatewayV2::IntegrationResponse.IntegrationResponseKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integrationresponse.html#cfn-apigatewayv2-integrationresponse-integrationresponsekey
    Stability:
        experimental
    """

class CfnIntegrationV2(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnIntegrationV2"):
    """A CloudFormation ``AWS::ApiGatewayV2::Integration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGatewayV2::Integration
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_id: str, integration_type: str, connection_type: typing.Optional[str]=None, content_handling_strategy: typing.Optional[str]=None, credentials_arn: typing.Optional[str]=None, description: typing.Optional[str]=None, integration_method: typing.Optional[str]=None, integration_uri: typing.Optional[str]=None, passthrough_behavior: typing.Optional[str]=None, request_parameters: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, request_templates: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, template_selection_expression: typing.Optional[str]=None, timeout_in_millis: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::ApiGatewayV2::Integration``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            apiId: ``AWS::ApiGatewayV2::Integration.ApiId``.
            integrationType: ``AWS::ApiGatewayV2::Integration.IntegrationType``.
            connectionType: ``AWS::ApiGatewayV2::Integration.ConnectionType``.
            contentHandlingStrategy: ``AWS::ApiGatewayV2::Integration.ContentHandlingStrategy``.
            credentialsArn: ``AWS::ApiGatewayV2::Integration.CredentialsArn``.
            description: ``AWS::ApiGatewayV2::Integration.Description``.
            integrationMethod: ``AWS::ApiGatewayV2::Integration.IntegrationMethod``.
            integrationUri: ``AWS::ApiGatewayV2::Integration.IntegrationUri``.
            passthroughBehavior: ``AWS::ApiGatewayV2::Integration.PassthroughBehavior``.
            requestParameters: ``AWS::ApiGatewayV2::Integration.RequestParameters``.
            requestTemplates: ``AWS::ApiGatewayV2::Integration.RequestTemplates``.
            templateSelectionExpression: ``AWS::ApiGatewayV2::Integration.TemplateSelectionExpression``.
            timeoutInMillis: ``AWS::ApiGatewayV2::Integration.TimeoutInMillis``.

        Stability:
            experimental
        """
        props: CfnIntegrationV2Props = {"apiId": api_id, "integrationType": integration_type}

        if connection_type is not None:
            props["connectionType"] = connection_type

        if content_handling_strategy is not None:
            props["contentHandlingStrategy"] = content_handling_strategy

        if credentials_arn is not None:
            props["credentialsArn"] = credentials_arn

        if description is not None:
            props["description"] = description

        if integration_method is not None:
            props["integrationMethod"] = integration_method

        if integration_uri is not None:
            props["integrationUri"] = integration_uri

        if passthrough_behavior is not None:
            props["passthroughBehavior"] = passthrough_behavior

        if request_parameters is not None:
            props["requestParameters"] = request_parameters

        if request_templates is not None:
            props["requestTemplates"] = request_templates

        if template_selection_expression is not None:
            props["templateSelectionExpression"] = template_selection_expression

        if timeout_in_millis is not None:
            props["timeoutInMillis"] = timeout_in_millis

        jsii.create(CfnIntegrationV2, self, [scope, id, props])

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
    @jsii.member(jsii_name="integrationId")
    def integration_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "integrationId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnIntegrationV2Props":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnIntegrationV2Props(jsii.compat.TypedDict, total=False):
    connectionType: str
    """``AWS::ApiGatewayV2::Integration.ConnectionType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-connectiontype
    Stability:
        experimental
    """
    contentHandlingStrategy: str
    """``AWS::ApiGatewayV2::Integration.ContentHandlingStrategy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-contenthandlingstrategy
    Stability:
        experimental
    """
    credentialsArn: str
    """``AWS::ApiGatewayV2::Integration.CredentialsArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-credentialsarn
    Stability:
        experimental
    """
    description: str
    """``AWS::ApiGatewayV2::Integration.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-description
    Stability:
        experimental
    """
    integrationMethod: str
    """``AWS::ApiGatewayV2::Integration.IntegrationMethod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-integrationmethod
    Stability:
        experimental
    """
    integrationUri: str
    """``AWS::ApiGatewayV2::Integration.IntegrationUri``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-integrationuri
    Stability:
        experimental
    """
    passthroughBehavior: str
    """``AWS::ApiGatewayV2::Integration.PassthroughBehavior``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-passthroughbehavior
    Stability:
        experimental
    """
    requestParameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::Integration.RequestParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-requestparameters
    Stability:
        experimental
    """
    requestTemplates: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::Integration.RequestTemplates``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-requesttemplates
    Stability:
        experimental
    """
    templateSelectionExpression: str
    """``AWS::ApiGatewayV2::Integration.TemplateSelectionExpression``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-templateselectionexpression
    Stability:
        experimental
    """
    timeoutInMillis: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::Integration.TimeoutInMillis``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-timeoutinmillis
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnIntegrationV2Props", jsii_struct_bases=[_CfnIntegrationV2Props])
class CfnIntegrationV2Props(_CfnIntegrationV2Props):
    """Properties for defining a ``AWS::ApiGatewayV2::Integration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html
    Stability:
        experimental
    """
    apiId: str
    """``AWS::ApiGatewayV2::Integration.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-apiid
    Stability:
        experimental
    """

    integrationType: str
    """``AWS::ApiGatewayV2::Integration.IntegrationType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-integration.html#cfn-apigatewayv2-integration-integrationtype
    Stability:
        experimental
    """

class CfnMethod(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnMethod"):
    """A CloudFormation ``AWS::ApiGateway::Method``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::Method
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, http_method: str, resource_id: str, rest_api_id: str, api_key_required: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, authorization_scopes: typing.Optional[typing.List[str]]=None, authorization_type: typing.Optional[str]=None, authorizer_id: typing.Optional[str]=None, integration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["IntegrationProperty"]]]=None, method_responses: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "MethodResponseProperty"]]]]]=None, operation_name: typing.Optional[str]=None, request_models: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.Mapping[str,str]]]]=None, request_parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.Mapping[str,typing.Union[bool, aws_cdk.cdk.Token]]]]]=None, request_validator_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGateway::Method``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            httpMethod: ``AWS::ApiGateway::Method.HttpMethod``.
            resourceId: ``AWS::ApiGateway::Method.ResourceId``.
            restApiId: ``AWS::ApiGateway::Method.RestApiId``.
            apiKeyRequired: ``AWS::ApiGateway::Method.ApiKeyRequired``.
            authorizationScopes: ``AWS::ApiGateway::Method.AuthorizationScopes``.
            authorizationType: ``AWS::ApiGateway::Method.AuthorizationType``.
            authorizerId: ``AWS::ApiGateway::Method.AuthorizerId``.
            integration: ``AWS::ApiGateway::Method.Integration``.
            methodResponses: ``AWS::ApiGateway::Method.MethodResponses``.
            operationName: ``AWS::ApiGateway::Method.OperationName``.
            requestModels: ``AWS::ApiGateway::Method.RequestModels``.
            requestParameters: ``AWS::ApiGateway::Method.RequestParameters``.
            requestValidatorId: ``AWS::ApiGateway::Method.RequestValidatorId``.

        Stability:
            experimental
        """
        props: CfnMethodProps = {"httpMethod": http_method, "resourceId": resource_id, "restApiId": rest_api_id}

        if api_key_required is not None:
            props["apiKeyRequired"] = api_key_required

        if authorization_scopes is not None:
            props["authorizationScopes"] = authorization_scopes

        if authorization_type is not None:
            props["authorizationType"] = authorization_type

        if authorizer_id is not None:
            props["authorizerId"] = authorizer_id

        if integration is not None:
            props["integration"] = integration

        if method_responses is not None:
            props["methodResponses"] = method_responses

        if operation_name is not None:
            props["operationName"] = operation_name

        if request_models is not None:
            props["requestModels"] = request_models

        if request_parameters is not None:
            props["requestParameters"] = request_parameters

        if request_validator_id is not None:
            props["requestValidatorId"] = request_validator_id

        jsii.create(CfnMethod, self, [scope, id, props])

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
    @jsii.member(jsii_name="methodId")
    def method_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "methodId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnMethodProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnMethod.IntegrationProperty", jsii_struct_bases=[])
    class IntegrationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html
        Stability:
            experimental
        """
        cacheKeyParameters: typing.List[str]
        """``CfnMethod.IntegrationProperty.CacheKeyParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-cachekeyparameters
        Stability:
            experimental
        """

        cacheNamespace: str
        """``CfnMethod.IntegrationProperty.CacheNamespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-cachenamespace
        Stability:
            experimental
        """

        connectionId: str
        """``CfnMethod.IntegrationProperty.ConnectionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-connectionid
        Stability:
            experimental
        """

        connectionType: str
        """``CfnMethod.IntegrationProperty.ConnectionType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-connectiontype
        Stability:
            experimental
        """

        contentHandling: str
        """``CfnMethod.IntegrationProperty.ContentHandling``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-contenthandling
        Stability:
            experimental
        """

        credentials: str
        """``CfnMethod.IntegrationProperty.Credentials``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-credentials
        Stability:
            experimental
        """

        integrationHttpMethod: str
        """``CfnMethod.IntegrationProperty.IntegrationHttpMethod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-integrationhttpmethod
        Stability:
            experimental
        """

        integrationResponses: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnMethod.IntegrationResponseProperty"]]]
        """``CfnMethod.IntegrationProperty.IntegrationResponses``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-integrationresponses
        Stability:
            experimental
        """

        passthroughBehavior: str
        """``CfnMethod.IntegrationProperty.PassthroughBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-passthroughbehavior
        Stability:
            experimental
        """

        requestParameters: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnMethod.IntegrationProperty.RequestParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-requestparameters
        Stability:
            experimental
        """

        requestTemplates: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnMethod.IntegrationProperty.RequestTemplates``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-requesttemplates
        Stability:
            experimental
        """

        timeoutInMillis: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnMethod.IntegrationProperty.TimeoutInMillis``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-timeoutinmillis
        Stability:
            experimental
        """

        type: str
        """``CfnMethod.IntegrationProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-type
        Stability:
            experimental
        """

        uri: str
        """``CfnMethod.IntegrationProperty.Uri``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html#cfn-apigateway-method-integration-uri
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _IntegrationResponseProperty(jsii.compat.TypedDict, total=False):
        contentHandling: str
        """``CfnMethod.IntegrationResponseProperty.ContentHandling``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration-integrationresponse.html#cfn-apigateway-method-integrationresponse-contenthandling
        Stability:
            experimental
        """
        responseParameters: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnMethod.IntegrationResponseProperty.ResponseParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration-integrationresponse.html#cfn-apigateway-method-integration-integrationresponse-responseparameters
        Stability:
            experimental
        """
        responseTemplates: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnMethod.IntegrationResponseProperty.ResponseTemplates``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration-integrationresponse.html#cfn-apigateway-method-integration-integrationresponse-responsetemplates
        Stability:
            experimental
        """
        selectionPattern: str
        """``CfnMethod.IntegrationResponseProperty.SelectionPattern``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration-integrationresponse.html#cfn-apigateway-method-integration-integrationresponse-selectionpattern
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnMethod.IntegrationResponseProperty", jsii_struct_bases=[_IntegrationResponseProperty])
    class IntegrationResponseProperty(_IntegrationResponseProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration-integrationresponse.html
        Stability:
            experimental
        """
        statusCode: str
        """``CfnMethod.IntegrationResponseProperty.StatusCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration-integrationresponse.html#cfn-apigateway-method-integration-integrationresponse-statuscode
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _MethodResponseProperty(jsii.compat.TypedDict, total=False):
        responseModels: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnMethod.MethodResponseProperty.ResponseModels``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-methodresponse.html#cfn-apigateway-method-methodresponse-responsemodels
        Stability:
            experimental
        """
        responseParameters: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,typing.Union[bool, aws_cdk.cdk.Token]]]
        """``CfnMethod.MethodResponseProperty.ResponseParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-methodresponse.html#cfn-apigateway-method-methodresponse-responseparameters
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnMethod.MethodResponseProperty", jsii_struct_bases=[_MethodResponseProperty])
    class MethodResponseProperty(_MethodResponseProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-methodresponse.html
        Stability:
            experimental
        """
        statusCode: str
        """``CfnMethod.MethodResponseProperty.StatusCode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-methodresponse.html#cfn-apigateway-method-methodresponse-statuscode
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnMethodProps(jsii.compat.TypedDict, total=False):
    apiKeyRequired: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ApiGateway::Method.ApiKeyRequired``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-apikeyrequired
    Stability:
        experimental
    """
    authorizationScopes: typing.List[str]
    """``AWS::ApiGateway::Method.AuthorizationScopes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-authorizationscopes
    Stability:
        experimental
    """
    authorizationType: str
    """``AWS::ApiGateway::Method.AuthorizationType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-authorizationtype
    Stability:
        experimental
    """
    authorizerId: str
    """``AWS::ApiGateway::Method.AuthorizerId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-authorizerid
    Stability:
        experimental
    """
    integration: typing.Union[aws_cdk.cdk.Token, "CfnMethod.IntegrationProperty"]
    """``AWS::ApiGateway::Method.Integration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-integration
    Stability:
        experimental
    """
    methodResponses: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnMethod.MethodResponseProperty"]]]
    """``AWS::ApiGateway::Method.MethodResponses``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-methodresponses
    Stability:
        experimental
    """
    operationName: str
    """``AWS::ApiGateway::Method.OperationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-operationname
    Stability:
        experimental
    """
    requestModels: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
    """``AWS::ApiGateway::Method.RequestModels``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-requestmodels
    Stability:
        experimental
    """
    requestParameters: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,typing.Union[bool, aws_cdk.cdk.Token]]]
    """``AWS::ApiGateway::Method.RequestParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-requestparameters
    Stability:
        experimental
    """
    requestValidatorId: str
    """``AWS::ApiGateway::Method.RequestValidatorId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-requestvalidatorid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnMethodProps", jsii_struct_bases=[_CfnMethodProps])
class CfnMethodProps(_CfnMethodProps):
    """Properties for defining a ``AWS::ApiGateway::Method``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html
    Stability:
        experimental
    """
    httpMethod: str
    """``AWS::ApiGateway::Method.HttpMethod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-httpmethod
    Stability:
        experimental
    """

    resourceId: str
    """``AWS::ApiGateway::Method.ResourceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-resourceid
    Stability:
        experimental
    """

    restApiId: str
    """``AWS::ApiGateway::Method.RestApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-restapiid
    Stability:
        experimental
    """

class CfnModel(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnModel"):
    """A CloudFormation ``AWS::ApiGateway::Model``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-model.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::Model
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, rest_api_id: str, content_type: typing.Optional[str]=None, description: typing.Optional[str]=None, name: typing.Optional[str]=None, schema: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::ApiGateway::Model``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            restApiId: ``AWS::ApiGateway::Model.RestApiId``.
            contentType: ``AWS::ApiGateway::Model.ContentType``.
            description: ``AWS::ApiGateway::Model.Description``.
            name: ``AWS::ApiGateway::Model.Name``.
            schema: ``AWS::ApiGateway::Model.Schema``.

        Stability:
            experimental
        """
        props: CfnModelProps = {"restApiId": rest_api_id}

        if content_type is not None:
            props["contentType"] = content_type

        if description is not None:
            props["description"] = description

        if name is not None:
            props["name"] = name

        if schema is not None:
            props["schema"] = schema

        jsii.create(CfnModel, self, [scope, id, props])

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
    @jsii.member(jsii_name="modelName")
    def model_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "modelName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnModelProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnModelProps(jsii.compat.TypedDict, total=False):
    contentType: str
    """``AWS::ApiGateway::Model.ContentType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-model.html#cfn-apigateway-model-contenttype
    Stability:
        experimental
    """
    description: str
    """``AWS::ApiGateway::Model.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-model.html#cfn-apigateway-model-description
    Stability:
        experimental
    """
    name: str
    """``AWS::ApiGateway::Model.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-model.html#cfn-apigateway-model-name
    Stability:
        experimental
    """
    schema: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGateway::Model.Schema``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-model.html#cfn-apigateway-model-schema
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnModelProps", jsii_struct_bases=[_CfnModelProps])
class CfnModelProps(_CfnModelProps):
    """Properties for defining a ``AWS::ApiGateway::Model``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-model.html
    Stability:
        experimental
    """
    restApiId: str
    """``AWS::ApiGateway::Model.RestApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-model.html#cfn-apigateway-model-restapiid
    Stability:
        experimental
    """

class CfnModelV2(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnModelV2"):
    """A CloudFormation ``AWS::ApiGatewayV2::Model``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGatewayV2::Model
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_id: str, name: str, schema: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token], content_type: typing.Optional[str]=None, description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGatewayV2::Model``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            apiId: ``AWS::ApiGatewayV2::Model.ApiId``.
            name: ``AWS::ApiGatewayV2::Model.Name``.
            schema: ``AWS::ApiGatewayV2::Model.Schema``.
            contentType: ``AWS::ApiGatewayV2::Model.ContentType``.
            description: ``AWS::ApiGatewayV2::Model.Description``.

        Stability:
            experimental
        """
        props: CfnModelV2Props = {"apiId": api_id, "name": name, "schema": schema}

        if content_type is not None:
            props["contentType"] = content_type

        if description is not None:
            props["description"] = description

        jsii.create(CfnModelV2, self, [scope, id, props])

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
    @jsii.member(jsii_name="modelId")
    def model_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "modelId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnModelV2Props":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnModelV2Props(jsii.compat.TypedDict, total=False):
    contentType: str
    """``AWS::ApiGatewayV2::Model.ContentType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-contenttype
    Stability:
        experimental
    """
    description: str
    """``AWS::ApiGatewayV2::Model.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-description
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnModelV2Props", jsii_struct_bases=[_CfnModelV2Props])
class CfnModelV2Props(_CfnModelV2Props):
    """Properties for defining a ``AWS::ApiGatewayV2::Model``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html
    Stability:
        experimental
    """
    apiId: str
    """``AWS::ApiGatewayV2::Model.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-apiid
    Stability:
        experimental
    """

    name: str
    """``AWS::ApiGatewayV2::Model.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-name
    Stability:
        experimental
    """

    schema: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::Model.Schema``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-model.html#cfn-apigatewayv2-model-schema
    Stability:
        experimental
    """

class CfnRequestValidator(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnRequestValidator"):
    """A CloudFormation ``AWS::ApiGateway::RequestValidator``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-requestvalidator.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::RequestValidator
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, rest_api_id: str, name: typing.Optional[str]=None, validate_request_body: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, validate_request_parameters: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::ApiGateway::RequestValidator``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            restApiId: ``AWS::ApiGateway::RequestValidator.RestApiId``.
            name: ``AWS::ApiGateway::RequestValidator.Name``.
            validateRequestBody: ``AWS::ApiGateway::RequestValidator.ValidateRequestBody``.
            validateRequestParameters: ``AWS::ApiGateway::RequestValidator.ValidateRequestParameters``.

        Stability:
            experimental
        """
        props: CfnRequestValidatorProps = {"restApiId": rest_api_id}

        if name is not None:
            props["name"] = name

        if validate_request_body is not None:
            props["validateRequestBody"] = validate_request_body

        if validate_request_parameters is not None:
            props["validateRequestParameters"] = validate_request_parameters

        jsii.create(CfnRequestValidator, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnRequestValidatorProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="requestValidatorId")
    def request_validator_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "requestValidatorId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRequestValidatorProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::ApiGateway::RequestValidator.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-requestvalidator.html#cfn-apigateway-requestvalidator-name
    Stability:
        experimental
    """
    validateRequestBody: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ApiGateway::RequestValidator.ValidateRequestBody``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-requestvalidator.html#cfn-apigateway-requestvalidator-validaterequestbody
    Stability:
        experimental
    """
    validateRequestParameters: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ApiGateway::RequestValidator.ValidateRequestParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-requestvalidator.html#cfn-apigateway-requestvalidator-validaterequestparameters
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnRequestValidatorProps", jsii_struct_bases=[_CfnRequestValidatorProps])
class CfnRequestValidatorProps(_CfnRequestValidatorProps):
    """Properties for defining a ``AWS::ApiGateway::RequestValidator``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-requestvalidator.html
    Stability:
        experimental
    """
    restApiId: str
    """``AWS::ApiGateway::RequestValidator.RestApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-requestvalidator.html#cfn-apigateway-requestvalidator-restapiid
    Stability:
        experimental
    """

class CfnResource(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnResource"):
    """A CloudFormation ``AWS::ApiGateway::Resource``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-resource.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::Resource
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, parent_id: str, path_part: str, rest_api_id: str) -> None:
        """Create a new ``AWS::ApiGateway::Resource``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            parentId: ``AWS::ApiGateway::Resource.ParentId``.
            pathPart: ``AWS::ApiGateway::Resource.PathPart``.
            restApiId: ``AWS::ApiGateway::Resource.RestApiId``.

        Stability:
            experimental
        """
        props: CfnResourceProps = {"parentId": parent_id, "pathPart": path_part, "restApiId": rest_api_id}

        jsii.create(CfnResource, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnResourceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "resourceId")


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnResourceProps", jsii_struct_bases=[])
class CfnResourceProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::ApiGateway::Resource``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-resource.html
    Stability:
        experimental
    """
    parentId: str
    """``AWS::ApiGateway::Resource.ParentId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-resource.html#cfn-apigateway-resource-parentid
    Stability:
        experimental
    """

    pathPart: str
    """``AWS::ApiGateway::Resource.PathPart``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-resource.html#cfn-apigateway-resource-pathpart
    Stability:
        experimental
    """

    restApiId: str
    """``AWS::ApiGateway::Resource.RestApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-resource.html#cfn-apigateway-resource-restapiid
    Stability:
        experimental
    """

class CfnRestApi(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnRestApi"):
    """A CloudFormation ``AWS::ApiGateway::RestApi``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::RestApi
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_key_source_type: typing.Optional[str]=None, binary_media_types: typing.Optional[typing.List[str]]=None, body: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, body_s3_location: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["S3LocationProperty"]]]=None, clone_from: typing.Optional[str]=None, description: typing.Optional[str]=None, endpoint_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["EndpointConfigurationProperty"]]]=None, fail_on_warnings: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, minimum_compression_size: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, name: typing.Optional[str]=None, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.Mapping[str,str]]]]=None, policy: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::ApiGateway::RestApi``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            apiKeySourceType: ``AWS::ApiGateway::RestApi.ApiKeySourceType``.
            binaryMediaTypes: ``AWS::ApiGateway::RestApi.BinaryMediaTypes``.
            body: ``AWS::ApiGateway::RestApi.Body``.
            bodyS3Location: ``AWS::ApiGateway::RestApi.BodyS3Location``.
            cloneFrom: ``AWS::ApiGateway::RestApi.CloneFrom``.
            description: ``AWS::ApiGateway::RestApi.Description``.
            endpointConfiguration: ``AWS::ApiGateway::RestApi.EndpointConfiguration``.
            failOnWarnings: ``AWS::ApiGateway::RestApi.FailOnWarnings``.
            minimumCompressionSize: ``AWS::ApiGateway::RestApi.MinimumCompressionSize``.
            name: ``AWS::ApiGateway::RestApi.Name``.
            parameters: ``AWS::ApiGateway::RestApi.Parameters``.
            policy: ``AWS::ApiGateway::RestApi.Policy``.

        Stability:
            experimental
        """
        props: CfnRestApiProps = {}

        if api_key_source_type is not None:
            props["apiKeySourceType"] = api_key_source_type

        if binary_media_types is not None:
            props["binaryMediaTypes"] = binary_media_types

        if body is not None:
            props["body"] = body

        if body_s3_location is not None:
            props["bodyS3Location"] = body_s3_location

        if clone_from is not None:
            props["cloneFrom"] = clone_from

        if description is not None:
            props["description"] = description

        if endpoint_configuration is not None:
            props["endpointConfiguration"] = endpoint_configuration

        if fail_on_warnings is not None:
            props["failOnWarnings"] = fail_on_warnings

        if minimum_compression_size is not None:
            props["minimumCompressionSize"] = minimum_compression_size

        if name is not None:
            props["name"] = name

        if parameters is not None:
            props["parameters"] = parameters

        if policy is not None:
            props["policy"] = policy

        jsii.create(CfnRestApi, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnRestApiProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "restApiId")

    @property
    @jsii.member(jsii_name="restApiRootResourceId")
    def rest_api_root_resource_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RootResourceId
        """
        return jsii.get(self, "restApiRootResourceId")

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnRestApi.EndpointConfigurationProperty", jsii_struct_bases=[])
    class EndpointConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-restapi-endpointconfiguration.html
        Stability:
            experimental
        """
        types: typing.List[str]
        """``CfnRestApi.EndpointConfigurationProperty.Types``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-restapi-endpointconfiguration.html#cfn-apigateway-restapi-endpointconfiguration-types
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnRestApi.S3LocationProperty", jsii_struct_bases=[])
    class S3LocationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-restapi-s3location.html
        Stability:
            experimental
        """
        bucket: str
        """``CfnRestApi.S3LocationProperty.Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-restapi-s3location.html#cfn-apigateway-restapi-s3location-bucket
        Stability:
            experimental
        """

        eTag: str
        """``CfnRestApi.S3LocationProperty.ETag``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-restapi-s3location.html#cfn-apigateway-restapi-s3location-etag
        Stability:
            experimental
        """

        key: str
        """``CfnRestApi.S3LocationProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-restapi-s3location.html#cfn-apigateway-restapi-s3location-key
        Stability:
            experimental
        """

        version: str
        """``CfnRestApi.S3LocationProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-restapi-s3location.html#cfn-apigateway-restapi-s3location-version
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnRestApiProps", jsii_struct_bases=[])
class CfnRestApiProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::ApiGateway::RestApi``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html
    Stability:
        experimental
    """
    apiKeySourceType: str
    """``AWS::ApiGateway::RestApi.ApiKeySourceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-apikeysourcetype
    Stability:
        experimental
    """

    binaryMediaTypes: typing.List[str]
    """``AWS::ApiGateway::RestApi.BinaryMediaTypes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-binarymediatypes
    Stability:
        experimental
    """

    body: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGateway::RestApi.Body``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-body
    Stability:
        experimental
    """

    bodyS3Location: typing.Union[aws_cdk.cdk.Token, "CfnRestApi.S3LocationProperty"]
    """``AWS::ApiGateway::RestApi.BodyS3Location``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-bodys3location
    Stability:
        experimental
    """

    cloneFrom: str
    """``AWS::ApiGateway::RestApi.CloneFrom``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-clonefrom
    Stability:
        experimental
    """

    description: str
    """``AWS::ApiGateway::RestApi.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-description
    Stability:
        experimental
    """

    endpointConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnRestApi.EndpointConfigurationProperty"]
    """``AWS::ApiGateway::RestApi.EndpointConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-endpointconfiguration
    Stability:
        experimental
    """

    failOnWarnings: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ApiGateway::RestApi.FailOnWarnings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-failonwarnings
    Stability:
        experimental
    """

    minimumCompressionSize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ApiGateway::RestApi.MinimumCompressionSize``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-minimumcompressionsize
    Stability:
        experimental
    """

    name: str
    """``AWS::ApiGateway::RestApi.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-name
    Stability:
        experimental
    """

    parameters: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
    """``AWS::ApiGateway::RestApi.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-parameters
    Stability:
        experimental
    """

    policy: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGateway::RestApi.Policy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html#cfn-apigateway-restapi-policy
    Stability:
        experimental
    """

class CfnRouteResponseV2(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnRouteResponseV2"):
    """A CloudFormation ``AWS::ApiGatewayV2::RouteResponse``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGatewayV2::RouteResponse
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_id: str, route_id: str, route_response_key: str, model_selection_expression: typing.Optional[str]=None, response_models: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, response_parameters: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::ApiGatewayV2::RouteResponse``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            apiId: ``AWS::ApiGatewayV2::RouteResponse.ApiId``.
            routeId: ``AWS::ApiGatewayV2::RouteResponse.RouteId``.
            routeResponseKey: ``AWS::ApiGatewayV2::RouteResponse.RouteResponseKey``.
            modelSelectionExpression: ``AWS::ApiGatewayV2::RouteResponse.ModelSelectionExpression``.
            responseModels: ``AWS::ApiGatewayV2::RouteResponse.ResponseModels``.
            responseParameters: ``AWS::ApiGatewayV2::RouteResponse.ResponseParameters``.

        Stability:
            experimental
        """
        props: CfnRouteResponseV2Props = {"apiId": api_id, "routeId": route_id, "routeResponseKey": route_response_key}

        if model_selection_expression is not None:
            props["modelSelectionExpression"] = model_selection_expression

        if response_models is not None:
            props["responseModels"] = response_models

        if response_parameters is not None:
            props["responseParameters"] = response_parameters

        jsii.create(CfnRouteResponseV2, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnRouteResponseV2Props":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="routeResponseId")
    def route_response_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "routeResponseId")

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnRouteResponseV2.ParameterConstraintsProperty", jsii_struct_bases=[])
    class ParameterConstraintsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-routeresponse-parameterconstraints.html
        Stability:
            experimental
        """
        required: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnRouteResponseV2.ParameterConstraintsProperty.Required``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-routeresponse-parameterconstraints.html#cfn-apigatewayv2-routeresponse-parameterconstraints-required
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRouteResponseV2Props(jsii.compat.TypedDict, total=False):
    modelSelectionExpression: str
    """``AWS::ApiGatewayV2::RouteResponse.ModelSelectionExpression``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-modelselectionexpression
    Stability:
        experimental
    """
    responseModels: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::RouteResponse.ResponseModels``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-responsemodels
    Stability:
        experimental
    """
    responseParameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::RouteResponse.ResponseParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-responseparameters
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnRouteResponseV2Props", jsii_struct_bases=[_CfnRouteResponseV2Props])
class CfnRouteResponseV2Props(_CfnRouteResponseV2Props):
    """Properties for defining a ``AWS::ApiGatewayV2::RouteResponse``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html
    Stability:
        experimental
    """
    apiId: str
    """``AWS::ApiGatewayV2::RouteResponse.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-apiid
    Stability:
        experimental
    """

    routeId: str
    """``AWS::ApiGatewayV2::RouteResponse.RouteId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-routeid
    Stability:
        experimental
    """

    routeResponseKey: str
    """``AWS::ApiGatewayV2::RouteResponse.RouteResponseKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-routeresponse.html#cfn-apigatewayv2-routeresponse-routeresponsekey
    Stability:
        experimental
    """

class CfnRouteV2(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnRouteV2"):
    """A CloudFormation ``AWS::ApiGatewayV2::Route``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGatewayV2::Route
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_id: str, route_key: str, api_key_required: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, authorization_scopes: typing.Optional[typing.List[str]]=None, authorization_type: typing.Optional[str]=None, authorizer_id: typing.Optional[str]=None, model_selection_expression: typing.Optional[str]=None, operation_name: typing.Optional[str]=None, request_models: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, request_parameters: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, route_response_selection_expression: typing.Optional[str]=None, target: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGatewayV2::Route``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            apiId: ``AWS::ApiGatewayV2::Route.ApiId``.
            routeKey: ``AWS::ApiGatewayV2::Route.RouteKey``.
            apiKeyRequired: ``AWS::ApiGatewayV2::Route.ApiKeyRequired``.
            authorizationScopes: ``AWS::ApiGatewayV2::Route.AuthorizationScopes``.
            authorizationType: ``AWS::ApiGatewayV2::Route.AuthorizationType``.
            authorizerId: ``AWS::ApiGatewayV2::Route.AuthorizerId``.
            modelSelectionExpression: ``AWS::ApiGatewayV2::Route.ModelSelectionExpression``.
            operationName: ``AWS::ApiGatewayV2::Route.OperationName``.
            requestModels: ``AWS::ApiGatewayV2::Route.RequestModels``.
            requestParameters: ``AWS::ApiGatewayV2::Route.RequestParameters``.
            routeResponseSelectionExpression: ``AWS::ApiGatewayV2::Route.RouteResponseSelectionExpression``.
            target: ``AWS::ApiGatewayV2::Route.Target``.

        Stability:
            experimental
        """
        props: CfnRouteV2Props = {"apiId": api_id, "routeKey": route_key}

        if api_key_required is not None:
            props["apiKeyRequired"] = api_key_required

        if authorization_scopes is not None:
            props["authorizationScopes"] = authorization_scopes

        if authorization_type is not None:
            props["authorizationType"] = authorization_type

        if authorizer_id is not None:
            props["authorizerId"] = authorizer_id

        if model_selection_expression is not None:
            props["modelSelectionExpression"] = model_selection_expression

        if operation_name is not None:
            props["operationName"] = operation_name

        if request_models is not None:
            props["requestModels"] = request_models

        if request_parameters is not None:
            props["requestParameters"] = request_parameters

        if route_response_selection_expression is not None:
            props["routeResponseSelectionExpression"] = route_response_selection_expression

        if target is not None:
            props["target"] = target

        jsii.create(CfnRouteV2, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnRouteV2Props":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="routeId")
    def route_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "routeId")

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnRouteV2.ParameterConstraintsProperty", jsii_struct_bases=[])
    class ParameterConstraintsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-route-parameterconstraints.html
        Stability:
            experimental
        """
        required: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnRouteV2.ParameterConstraintsProperty.Required``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-route-parameterconstraints.html#cfn-apigatewayv2-route-parameterconstraints-required
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRouteV2Props(jsii.compat.TypedDict, total=False):
    apiKeyRequired: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::Route.ApiKeyRequired``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-apikeyrequired
    Stability:
        experimental
    """
    authorizationScopes: typing.List[str]
    """``AWS::ApiGatewayV2::Route.AuthorizationScopes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-authorizationscopes
    Stability:
        experimental
    """
    authorizationType: str
    """``AWS::ApiGatewayV2::Route.AuthorizationType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-authorizationtype
    Stability:
        experimental
    """
    authorizerId: str
    """``AWS::ApiGatewayV2::Route.AuthorizerId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-authorizerid
    Stability:
        experimental
    """
    modelSelectionExpression: str
    """``AWS::ApiGatewayV2::Route.ModelSelectionExpression``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-modelselectionexpression
    Stability:
        experimental
    """
    operationName: str
    """``AWS::ApiGatewayV2::Route.OperationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-operationname
    Stability:
        experimental
    """
    requestModels: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::Route.RequestModels``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-requestmodels
    Stability:
        experimental
    """
    requestParameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::Route.RequestParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-requestparameters
    Stability:
        experimental
    """
    routeResponseSelectionExpression: str
    """``AWS::ApiGatewayV2::Route.RouteResponseSelectionExpression``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-routeresponseselectionexpression
    Stability:
        experimental
    """
    target: str
    """``AWS::ApiGatewayV2::Route.Target``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-target
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnRouteV2Props", jsii_struct_bases=[_CfnRouteV2Props])
class CfnRouteV2Props(_CfnRouteV2Props):
    """Properties for defining a ``AWS::ApiGatewayV2::Route``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html
    Stability:
        experimental
    """
    apiId: str
    """``AWS::ApiGatewayV2::Route.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-apiid
    Stability:
        experimental
    """

    routeKey: str
    """``AWS::ApiGatewayV2::Route.RouteKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-routekey
    Stability:
        experimental
    """

class CfnStage(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnStage"):
    """A CloudFormation ``AWS::ApiGateway::Stage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::Stage
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, rest_api_id: str, access_log_setting: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["AccessLogSettingProperty"]]]=None, cache_cluster_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, cache_cluster_size: typing.Optional[str]=None, canary_setting: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["CanarySettingProperty"]]]=None, client_certificate_id: typing.Optional[str]=None, deployment_id: typing.Optional[str]=None, description: typing.Optional[str]=None, documentation_version: typing.Optional[str]=None, method_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "MethodSettingProperty"]]]]]=None, stage_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, tracing_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, variables: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.Mapping[str,str]]]]=None) -> None:
        """Create a new ``AWS::ApiGateway::Stage``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            restApiId: ``AWS::ApiGateway::Stage.RestApiId``.
            accessLogSetting: ``AWS::ApiGateway::Stage.AccessLogSetting``.
            cacheClusterEnabled: ``AWS::ApiGateway::Stage.CacheClusterEnabled``.
            cacheClusterSize: ``AWS::ApiGateway::Stage.CacheClusterSize``.
            canarySetting: ``AWS::ApiGateway::Stage.CanarySetting``.
            clientCertificateId: ``AWS::ApiGateway::Stage.ClientCertificateId``.
            deploymentId: ``AWS::ApiGateway::Stage.DeploymentId``.
            description: ``AWS::ApiGateway::Stage.Description``.
            documentationVersion: ``AWS::ApiGateway::Stage.DocumentationVersion``.
            methodSettings: ``AWS::ApiGateway::Stage.MethodSettings``.
            stageName: ``AWS::ApiGateway::Stage.StageName``.
            tags: ``AWS::ApiGateway::Stage.Tags``.
            tracingEnabled: ``AWS::ApiGateway::Stage.TracingEnabled``.
            variables: ``AWS::ApiGateway::Stage.Variables``.

        Stability:
            experimental
        """
        props: CfnStageProps = {"restApiId": rest_api_id}

        if access_log_setting is not None:
            props["accessLogSetting"] = access_log_setting

        if cache_cluster_enabled is not None:
            props["cacheClusterEnabled"] = cache_cluster_enabled

        if cache_cluster_size is not None:
            props["cacheClusterSize"] = cache_cluster_size

        if canary_setting is not None:
            props["canarySetting"] = canary_setting

        if client_certificate_id is not None:
            props["clientCertificateId"] = client_certificate_id

        if deployment_id is not None:
            props["deploymentId"] = deployment_id

        if description is not None:
            props["description"] = description

        if documentation_version is not None:
            props["documentationVersion"] = documentation_version

        if method_settings is not None:
            props["methodSettings"] = method_settings

        if stage_name is not None:
            props["stageName"] = stage_name

        if tags is not None:
            props["tags"] = tags

        if tracing_enabled is not None:
            props["tracingEnabled"] = tracing_enabled

        if variables is not None:
            props["variables"] = variables

        jsii.create(CfnStage, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnStageProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "stageName")

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

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnStage.AccessLogSettingProperty", jsii_struct_bases=[])
    class AccessLogSettingProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-accesslogsetting.html
        Stability:
            experimental
        """
        destinationArn: str
        """``CfnStage.AccessLogSettingProperty.DestinationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-accesslogsetting.html#cfn-apigateway-stage-accesslogsetting-destinationarn
        Stability:
            experimental
        """

        format: str
        """``CfnStage.AccessLogSettingProperty.Format``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-accesslogsetting.html#cfn-apigateway-stage-accesslogsetting-format
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnStage.CanarySettingProperty", jsii_struct_bases=[])
    class CanarySettingProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-canarysetting.html
        Stability:
            experimental
        """
        deploymentId: str
        """``CfnStage.CanarySettingProperty.DeploymentId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-canarysetting.html#cfn-apigateway-stage-canarysetting-deploymentid
        Stability:
            experimental
        """

        percentTraffic: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnStage.CanarySettingProperty.PercentTraffic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-canarysetting.html#cfn-apigateway-stage-canarysetting-percenttraffic
        Stability:
            experimental
        """

        stageVariableOverrides: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnStage.CanarySettingProperty.StageVariableOverrides``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-canarysetting.html#cfn-apigateway-stage-canarysetting-stagevariableoverrides
        Stability:
            experimental
        """

        useStageCache: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnStage.CanarySettingProperty.UseStageCache``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-stage-canarysetting.html#cfn-apigateway-stage-canarysetting-usestagecache
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnStage.MethodSettingProperty", jsii_struct_bases=[])
    class MethodSettingProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-stage-methodsetting.html
        Stability:
            experimental
        """
        cacheDataEncrypted: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnStage.MethodSettingProperty.CacheDataEncrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-stage-methodsetting.html#cfn-apigateway-stage-methodsetting-cachedataencrypted
        Stability:
            experimental
        """

        cacheTtlInSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnStage.MethodSettingProperty.CacheTtlInSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-stage-methodsetting.html#cfn-apigateway-stage-methodsetting-cachettlinseconds
        Stability:
            experimental
        """

        cachingEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnStage.MethodSettingProperty.CachingEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-stage-methodsetting.html#cfn-apigateway-stage-methodsetting-cachingenabled
        Stability:
            experimental
        """

        dataTraceEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnStage.MethodSettingProperty.DataTraceEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-stage-methodsetting.html#cfn-apigateway-stage-methodsetting-datatraceenabled
        Stability:
            experimental
        """

        httpMethod: str
        """``CfnStage.MethodSettingProperty.HttpMethod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-stage-methodsetting.html#cfn-apigateway-stage-methodsetting-httpmethod
        Stability:
            experimental
        """

        loggingLevel: str
        """``CfnStage.MethodSettingProperty.LoggingLevel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-stage-methodsetting.html#cfn-apigateway-stage-methodsetting-logginglevel
        Stability:
            experimental
        """

        metricsEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnStage.MethodSettingProperty.MetricsEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-stage-methodsetting.html#cfn-apigateway-stage-methodsetting-metricsenabled
        Stability:
            experimental
        """

        resourcePath: str
        """``CfnStage.MethodSettingProperty.ResourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-stage-methodsetting.html#cfn-apigateway-stage-methodsetting-resourcepath
        Stability:
            experimental
        """

        throttlingBurstLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnStage.MethodSettingProperty.ThrottlingBurstLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-stage-methodsetting.html#cfn-apigateway-stage-methodsetting-throttlingburstlimit
        Stability:
            experimental
        """

        throttlingRateLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnStage.MethodSettingProperty.ThrottlingRateLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-stage-methodsetting.html#cfn-apigateway-stage-methodsetting-throttlingratelimit
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnStageProps(jsii.compat.TypedDict, total=False):
    accessLogSetting: typing.Union[aws_cdk.cdk.Token, "CfnStage.AccessLogSettingProperty"]
    """``AWS::ApiGateway::Stage.AccessLogSetting``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-accesslogsetting
    Stability:
        experimental
    """
    cacheClusterEnabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ApiGateway::Stage.CacheClusterEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-cacheclusterenabled
    Stability:
        experimental
    """
    cacheClusterSize: str
    """``AWS::ApiGateway::Stage.CacheClusterSize``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-cacheclustersize
    Stability:
        experimental
    """
    canarySetting: typing.Union[aws_cdk.cdk.Token, "CfnStage.CanarySettingProperty"]
    """``AWS::ApiGateway::Stage.CanarySetting``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-canarysetting
    Stability:
        experimental
    """
    clientCertificateId: str
    """``AWS::ApiGateway::Stage.ClientCertificateId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-clientcertificateid
    Stability:
        experimental
    """
    deploymentId: str
    """``AWS::ApiGateway::Stage.DeploymentId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-deploymentid
    Stability:
        experimental
    """
    description: str
    """``AWS::ApiGateway::Stage.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-description
    Stability:
        experimental
    """
    documentationVersion: str
    """``AWS::ApiGateway::Stage.DocumentationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-documentationversion
    Stability:
        experimental
    """
    methodSettings: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnStage.MethodSettingProperty"]]]
    """``AWS::ApiGateway::Stage.MethodSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-methodsettings
    Stability:
        experimental
    """
    stageName: str
    """``AWS::ApiGateway::Stage.StageName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-stagename
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::ApiGateway::Stage.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-tags
    Stability:
        experimental
    """
    tracingEnabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ApiGateway::Stage.TracingEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-tracingenabled
    Stability:
        experimental
    """
    variables: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
    """``AWS::ApiGateway::Stage.Variables``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-variables
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnStageProps", jsii_struct_bases=[_CfnStageProps])
class CfnStageProps(_CfnStageProps):
    """Properties for defining a ``AWS::ApiGateway::Stage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html
    Stability:
        experimental
    """
    restApiId: str
    """``AWS::ApiGateway::Stage.RestApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html#cfn-apigateway-stage-restapiid
    Stability:
        experimental
    """

class CfnStageV2(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnStageV2"):
    """A CloudFormation ``AWS::ApiGatewayV2::Stage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGatewayV2::Stage
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_id: str, deployment_id: str, stage_name: str, access_log_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["AccessLogSettingsProperty"]]]=None, client_certificate_id: typing.Optional[str]=None, default_route_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["RouteSettingsProperty"]]]=None, description: typing.Optional[str]=None, route_settings: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, stage_variables: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::ApiGatewayV2::Stage``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            apiId: ``AWS::ApiGatewayV2::Stage.ApiId``.
            deploymentId: ``AWS::ApiGatewayV2::Stage.DeploymentId``.
            stageName: ``AWS::ApiGatewayV2::Stage.StageName``.
            accessLogSettings: ``AWS::ApiGatewayV2::Stage.AccessLogSettings``.
            clientCertificateId: ``AWS::ApiGatewayV2::Stage.ClientCertificateId``.
            defaultRouteSettings: ``AWS::ApiGatewayV2::Stage.DefaultRouteSettings``.
            description: ``AWS::ApiGatewayV2::Stage.Description``.
            routeSettings: ``AWS::ApiGatewayV2::Stage.RouteSettings``.
            stageVariables: ``AWS::ApiGatewayV2::Stage.StageVariables``.

        Stability:
            experimental
        """
        props: CfnStageV2Props = {"apiId": api_id, "deploymentId": deployment_id, "stageName": stage_name}

        if access_log_settings is not None:
            props["accessLogSettings"] = access_log_settings

        if client_certificate_id is not None:
            props["clientCertificateId"] = client_certificate_id

        if default_route_settings is not None:
            props["defaultRouteSettings"] = default_route_settings

        if description is not None:
            props["description"] = description

        if route_settings is not None:
            props["routeSettings"] = route_settings

        if stage_variables is not None:
            props["stageVariables"] = stage_variables

        jsii.create(CfnStageV2, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnStageV2Props":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "stageName")

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnStageV2.AccessLogSettingsProperty", jsii_struct_bases=[])
    class AccessLogSettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-accesslogsettings.html
        Stability:
            experimental
        """
        destinationArn: str
        """``CfnStageV2.AccessLogSettingsProperty.DestinationArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-accesslogsettings.html#cfn-apigatewayv2-stage-accesslogsettings-destinationarn
        Stability:
            experimental
        """

        format: str
        """``CfnStageV2.AccessLogSettingsProperty.Format``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-accesslogsettings.html#cfn-apigatewayv2-stage-accesslogsettings-format
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnStageV2.RouteSettingsProperty", jsii_struct_bases=[])
    class RouteSettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html
        Stability:
            experimental
        """
        dataTraceEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnStageV2.RouteSettingsProperty.DataTraceEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html#cfn-apigatewayv2-stage-routesettings-datatraceenabled
        Stability:
            experimental
        """

        detailedMetricsEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnStageV2.RouteSettingsProperty.DetailedMetricsEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html#cfn-apigatewayv2-stage-routesettings-detailedmetricsenabled
        Stability:
            experimental
        """

        loggingLevel: str
        """``CfnStageV2.RouteSettingsProperty.LoggingLevel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html#cfn-apigatewayv2-stage-routesettings-logginglevel
        Stability:
            experimental
        """

        throttlingBurstLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnStageV2.RouteSettingsProperty.ThrottlingBurstLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html#cfn-apigatewayv2-stage-routesettings-throttlingburstlimit
        Stability:
            experimental
        """

        throttlingRateLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnStageV2.RouteSettingsProperty.ThrottlingRateLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-stage-routesettings.html#cfn-apigatewayv2-stage-routesettings-throttlingratelimit
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnStageV2Props(jsii.compat.TypedDict, total=False):
    accessLogSettings: typing.Union[aws_cdk.cdk.Token, "CfnStageV2.AccessLogSettingsProperty"]
    """``AWS::ApiGatewayV2::Stage.AccessLogSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-accesslogsettings
    Stability:
        experimental
    """
    clientCertificateId: str
    """``AWS::ApiGatewayV2::Stage.ClientCertificateId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-clientcertificateid
    Stability:
        experimental
    """
    defaultRouteSettings: typing.Union[aws_cdk.cdk.Token, "CfnStageV2.RouteSettingsProperty"]
    """``AWS::ApiGatewayV2::Stage.DefaultRouteSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-defaultroutesettings
    Stability:
        experimental
    """
    description: str
    """``AWS::ApiGatewayV2::Stage.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-description
    Stability:
        experimental
    """
    routeSettings: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::Stage.RouteSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-routesettings
    Stability:
        experimental
    """
    stageVariables: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::ApiGatewayV2::Stage.StageVariables``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-stagevariables
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnStageV2Props", jsii_struct_bases=[_CfnStageV2Props])
class CfnStageV2Props(_CfnStageV2Props):
    """Properties for defining a ``AWS::ApiGatewayV2::Stage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html
    Stability:
        experimental
    """
    apiId: str
    """``AWS::ApiGatewayV2::Stage.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-apiid
    Stability:
        experimental
    """

    deploymentId: str
    """``AWS::ApiGatewayV2::Stage.DeploymentId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-deploymentid
    Stability:
        experimental
    """

    stageName: str
    """``AWS::ApiGatewayV2::Stage.StageName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-stage.html#cfn-apigatewayv2-stage-stagename
    Stability:
        experimental
    """

class CfnUsagePlan(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnUsagePlan"):
    """A CloudFormation ``AWS::ApiGateway::UsagePlan``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplan.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::UsagePlan
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_stages: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "ApiStageProperty"]]]]]=None, description: typing.Optional[str]=None, quota: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["QuotaSettingsProperty"]]]=None, throttle: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ThrottleSettingsProperty"]]]=None, usage_plan_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGateway::UsagePlan``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            apiStages: ``AWS::ApiGateway::UsagePlan.ApiStages``.
            description: ``AWS::ApiGateway::UsagePlan.Description``.
            quota: ``AWS::ApiGateway::UsagePlan.Quota``.
            throttle: ``AWS::ApiGateway::UsagePlan.Throttle``.
            usagePlanName: ``AWS::ApiGateway::UsagePlan.UsagePlanName``.

        Stability:
            experimental
        """
        props: CfnUsagePlanProps = {}

        if api_stages is not None:
            props["apiStages"] = api_stages

        if description is not None:
            props["description"] = description

        if quota is not None:
            props["quota"] = quota

        if throttle is not None:
            props["throttle"] = throttle

        if usage_plan_name is not None:
            props["usagePlanName"] = usage_plan_name

        jsii.create(CfnUsagePlan, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnUsagePlanProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="usagePlanId")
    def usage_plan_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "usagePlanId")

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnUsagePlan.ApiStageProperty", jsii_struct_bases=[])
    class ApiStageProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-usageplan-apistage.html
        Stability:
            experimental
        """
        apiId: str
        """``CfnUsagePlan.ApiStageProperty.ApiId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-usageplan-apistage.html#cfn-apigateway-usageplan-apistage-apiid
        Stability:
            experimental
        """

        stage: str
        """``CfnUsagePlan.ApiStageProperty.Stage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-usageplan-apistage.html#cfn-apigateway-usageplan-apistage-stage
        Stability:
            experimental
        """

        throttle: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,typing.Union[aws_cdk.cdk.Token, "CfnUsagePlan.ThrottleSettingsProperty"]]]
        """``CfnUsagePlan.ApiStageProperty.Throttle``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-usageplan-apistage.html#cfn-apigateway-usageplan-apistage-throttle
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnUsagePlan.QuotaSettingsProperty", jsii_struct_bases=[])
    class QuotaSettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-usageplan-quotasettings.html
        Stability:
            experimental
        """
        limit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnUsagePlan.QuotaSettingsProperty.Limit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-usageplan-quotasettings.html#cfn-apigateway-usageplan-quotasettings-limit
        Stability:
            experimental
        """

        offset: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnUsagePlan.QuotaSettingsProperty.Offset``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-usageplan-quotasettings.html#cfn-apigateway-usageplan-quotasettings-offset
        Stability:
            experimental
        """

        period: str
        """``CfnUsagePlan.QuotaSettingsProperty.Period``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-usageplan-quotasettings.html#cfn-apigateway-usageplan-quotasettings-period
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnUsagePlan.ThrottleSettingsProperty", jsii_struct_bases=[])
    class ThrottleSettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-usageplan-throttlesettings.html
        Stability:
            experimental
        """
        burstLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnUsagePlan.ThrottleSettingsProperty.BurstLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-usageplan-throttlesettings.html#cfn-apigateway-usageplan-throttlesettings-burstlimit
        Stability:
            experimental
        """

        rateLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnUsagePlan.ThrottleSettingsProperty.RateLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigateway-usageplan-throttlesettings.html#cfn-apigateway-usageplan-throttlesettings-ratelimit
        Stability:
            experimental
        """


class CfnUsagePlanKey(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnUsagePlanKey"):
    """A CloudFormation ``AWS::ApiGateway::UsagePlanKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplankey.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::UsagePlanKey
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, key_id: str, key_type: str, usage_plan_id: str) -> None:
        """Create a new ``AWS::ApiGateway::UsagePlanKey``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            keyId: ``AWS::ApiGateway::UsagePlanKey.KeyId``.
            keyType: ``AWS::ApiGateway::UsagePlanKey.KeyType``.
            usagePlanId: ``AWS::ApiGateway::UsagePlanKey.UsagePlanId``.

        Stability:
            experimental
        """
        props: CfnUsagePlanKeyProps = {"keyId": key_id, "keyType": key_type, "usagePlanId": usage_plan_id}

        jsii.create(CfnUsagePlanKey, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnUsagePlanKeyProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="usagePlanKeyId")
    def usage_plan_key_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "usagePlanKeyId")


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnUsagePlanKeyProps", jsii_struct_bases=[])
class CfnUsagePlanKeyProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::ApiGateway::UsagePlanKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplankey.html
    Stability:
        experimental
    """
    keyId: str
    """``AWS::ApiGateway::UsagePlanKey.KeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplankey.html#cfn-apigateway-usageplankey-keyid
    Stability:
        experimental
    """

    keyType: str
    """``AWS::ApiGateway::UsagePlanKey.KeyType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplankey.html#cfn-apigateway-usageplankey-keytype
    Stability:
        experimental
    """

    usagePlanId: str
    """``AWS::ApiGateway::UsagePlanKey.UsagePlanId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplankey.html#cfn-apigateway-usageplankey-usageplanid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnUsagePlanProps", jsii_struct_bases=[])
class CfnUsagePlanProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::ApiGateway::UsagePlan``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplan.html
    Stability:
        experimental
    """
    apiStages: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnUsagePlan.ApiStageProperty"]]]
    """``AWS::ApiGateway::UsagePlan.ApiStages``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplan.html#cfn-apigateway-usageplan-apistages
    Stability:
        experimental
    """

    description: str
    """``AWS::ApiGateway::UsagePlan.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplan.html#cfn-apigateway-usageplan-description
    Stability:
        experimental
    """

    quota: typing.Union[aws_cdk.cdk.Token, "CfnUsagePlan.QuotaSettingsProperty"]
    """``AWS::ApiGateway::UsagePlan.Quota``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplan.html#cfn-apigateway-usageplan-quota
    Stability:
        experimental
    """

    throttle: typing.Union[aws_cdk.cdk.Token, "CfnUsagePlan.ThrottleSettingsProperty"]
    """``AWS::ApiGateway::UsagePlan.Throttle``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplan.html#cfn-apigateway-usageplan-throttle
    Stability:
        experimental
    """

    usagePlanName: str
    """``AWS::ApiGateway::UsagePlan.UsagePlanName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplan.html#cfn-apigateway-usageplan-usageplanname
    Stability:
        experimental
    """

class CfnVpcLink(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.CfnVpcLink"):
    """A CloudFormation ``AWS::ApiGateway::VpcLink``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-vpclink.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ApiGateway::VpcLink
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, target_arns: typing.List[str], description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ApiGateway::VpcLink``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::ApiGateway::VpcLink.Name``.
            targetArns: ``AWS::ApiGateway::VpcLink.TargetArns``.
            description: ``AWS::ApiGateway::VpcLink.Description``.

        Stability:
            experimental
        """
        props: CfnVpcLinkProps = {"name": name, "targetArns": target_arns}

        if description is not None:
            props["description"] = description

        jsii.create(CfnVpcLink, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnVpcLinkProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="vpcLinkId")
    def vpc_link_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpcLinkId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnVpcLinkProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::ApiGateway::VpcLink.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-vpclink.html#cfn-apigateway-vpclink-description
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.CfnVpcLinkProps", jsii_struct_bases=[_CfnVpcLinkProps])
class CfnVpcLinkProps(_CfnVpcLinkProps):
    """Properties for defining a ``AWS::ApiGateway::VpcLink``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-vpclink.html
    Stability:
        experimental
    """
    name: str
    """``AWS::ApiGateway::VpcLink.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-vpclink.html#cfn-apigateway-vpclink-name
    Stability:
        experimental
    """

    targetArns: typing.List[str]
    """``AWS::ApiGateway::VpcLink.TargetArns``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-vpclink.html#cfn-apigateway-vpclink-targetarns
    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-apigateway.ConnectionType")
class ConnectionType(enum.Enum):
    """
    Stability:
        experimental
    """
    Internet = "Internet"
    """For connections through the public routable internet.

    Stability:
        experimental
    """
    VpcLink = "VpcLink"
    """For private connections between API Gateway and a network load balancer in a VPC.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-apigateway.ContentHandling")
class ContentHandling(enum.Enum):
    """
    Stability:
        experimental
    """
    ConvertToBinary = "ConvertToBinary"
    """Converts a request payload from a base64-encoded string to a binary blob.

    Stability:
        experimental
    """
    ConvertToText = "ConvertToText"
    """Converts a request payload from a binary blob to a base64-encoded string.

    Stability:
        experimental
    """

class Deployment(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.Deployment"):
    """A Deployment of a REST API.

    An immutable representation of a RestApi resource that can be called by users
    using Stages. A deployment must be associated with a Stage for it to be
    callable over the Internet.

    Normally, you don't need to define deployments manually. The RestApi
    construct manages a Deployment resource that represents the latest model. It
    can be accessed through ``restApi.latestDeployment`` (unless ``deploy: false`` is
    set when defining the ``RestApi``).

    If you manually define this resource, you will need to know that since
    deployments are immutable, as long as the resource's logical ID doesn't
    change, the deployment will represent the snapshot in time in which the
    resource was created. This means that if you modify the RestApi model (i.e.
    add methods or resources), these changes will not be reflected unless a new
    deployment resource is created.

    To achieve this behavior, the method ``addToLogicalId(data)`` can be used to
    augment the logical ID generated for the deployment resource such that it
    will include arbitrary data. This is done automatically for the
    ``restApi.latestDeployment`` deployment.

    Furthermore, since a deployment does not reference any of the REST API
    resources and methods, CloudFormation will likely provision it before these
    resources are created, which means that it will represent a "half-baked"
    model. Use the ``node.addDependency(dep)`` method to circumvent that. This is done
    automatically for the ``restApi.latestDeployment`` deployment.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api: "IRestApi", description: typing.Optional[str]=None, retain_deployments: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            api: The Rest API to deploy.
            description: A description of the purpose of the API Gateway deployment. Default: - No description.
            retainDeployments: When an API Gateway model is updated, a new deployment will automatically be created. If this is true (default), the old API Gateway Deployment resource will not be deleted. This will allow manually reverting back to a previous deployment in case for example. Default: false

        Stability:
            experimental
        """
        props: DeploymentProps = {"api": api}

        if description is not None:
            props["description"] = description

        if retain_deployments is not None:
            props["retainDeployments"] = retain_deployments

        jsii.create(Deployment, self, [scope, id, props])

    @jsii.member(jsii_name="addToLogicalId")
    def add_to_logical_id(self, data: typing.Any) -> None:
        """Adds a component to the hash that determines this Deployment resource's logical ID.

        This should be called by constructs of the API Gateway model that want to
        invalidate the deployment when their settings change. The component will
        be resolve()ed during synthesis so tokens are welcome.

        Arguments:
            data: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToLogicalId", [data])

    @property
    @jsii.member(jsii_name="api")
    def api(self) -> "IRestApi":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "api")

    @property
    @jsii.member(jsii_name="deploymentId")
    def deployment_id(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "deploymentId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _DeploymentProps(jsii.compat.TypedDict, total=False):
    description: str
    """A description of the purpose of the API Gateway deployment.

    Default:
        - No description.

    Stability:
        experimental
    """
    retainDeployments: bool
    """When an API Gateway model is updated, a new deployment will automatically be created. If this is true (default), the old API Gateway Deployment resource will not be deleted. This will allow manually reverting back to a previous deployment in case for example.

    Default:
        false

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.DeploymentProps", jsii_struct_bases=[_DeploymentProps])
class DeploymentProps(_DeploymentProps):
    """
    Stability:
        experimental
    """
    api: "IRestApi"
    """The Rest API to deploy.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-apigateway.EndpointType")
class EndpointType(enum.Enum):
    """
    Stability:
        experimental
    """
    Edge = "Edge"
    """For an edge-optimized API and its custom domain name.

    Stability:
        experimental
    """
    Regional = "Regional"
    """For a regional API and its custom domain name.

    Stability:
        experimental
    """
    Private = "Private"
    """For a private API and its custom domain name.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.HttpIntegrationProps", jsii_struct_bases=[])
class HttpIntegrationProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    httpMethod: str
    """HTTP method to use when invoking the backend URL.

    Default:
        GET

    Stability:
        experimental
    """

    options: "IntegrationOptions"
    """Integration options, such as request/resopnse mapping, content handling, etc.

    Default:
        defaults based on ``IntegrationOptions`` defaults

    Stability:
        experimental
    """

    proxy: bool
    """Determines whether to use proxy integration or custom integration.

    Default:
        true

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-apigateway.IApiKey")
class IApiKey(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """API keys are alphanumeric string values that you distribute to app developer customers to grant access to your API.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IApiKeyProxy

    @property
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> str:
        """The API key ID.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IApiKeyProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """API keys are alphanumeric string values that you distribute to app developer customers to grant access to your API.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-apigateway.IApiKey"
    @property
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> str:
        """The API key ID.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "keyId")


@jsii.interface(jsii_type="@aws-cdk/aws-apigateway.IModel")
class IModel(jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IModelProxy

    @property
    @jsii.member(jsii_name="modelId")
    def model_id(self) -> str:
        """
        Stability:
            experimental
        """
        ...


class _IModelProxy():
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-apigateway.IModel"
    @property
    @jsii.member(jsii_name="modelId")
    def model_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "modelId")


@jsii.implements(IModel)
class EmptyModel(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.EmptyModel"):
    """Represents a reference to a REST API's Empty model, which is available as part of the model collection by default.

    This can be used for mapping
    JSON responses from an integration to what is returned to a client,
    where strong typing is not required. In the absence of any defined
    model, the Empty model will be used to return the response payload
    unmapped.

    Definition
    {
    "$schema" : "http://json-schema.org/draft-04/schema#",
    "title" : "Empty Schema",
    "type" : "object"
    }

    See:
        https://docs.amazonaws.cn/en_us/apigateway/latest/developerguide/models-mappings.html#models-mappings-models
    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(EmptyModel, self, [])

    @property
    @jsii.member(jsii_name="modelId")
    def model_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "modelId")


@jsii.implements(IModel)
class ErrorModel(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.ErrorModel"):
    """Represents a reference to a REST API's Error model, which is available as part of the model collection by default.

    This can be used for mapping
    error JSON responses from an integration to a client, where a simple
    generic message field is sufficient to map and return an error payload.

    Definition
    {
    "$schema" : "http://json-schema.org/draft-04/schema#",
    "title" : "Error Schema",
    "type" : "object",
    "properties" : {
    "message" : { "type" : "string" }
    }
    }

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(ErrorModel, self, [])

    @property
    @jsii.member(jsii_name="modelId")
    def model_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "modelId")


@jsii.interface(jsii_type="@aws-cdk/aws-apigateway.IResource")
class IResource(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IResourceProxy

    @property
    @jsii.member(jsii_name="path")
    def path(self) -> str:
        """The full path of this resuorce.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> str:
        """The ID of the resource.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="restApi")
    def rest_api(self) -> "RestApi":
        """The rest API that this resource is part of.

        The reason we need the RestApi object itself and not just the ID is because the model
        is being tracked by the top-level RestApi object for the purpose of calculating it's
        hash to determine the ID of the deployment. This allows us to automatically update
        the deployment when the model of the REST API changes.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="defaultIntegration")
    def default_integration(self) -> typing.Optional["Integration"]:
        """An integration to use as a default for all methods created within this API unless an integration is specified.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="defaultMethodOptions")
    def default_method_options(self) -> typing.Optional["MethodOptions"]:
        """Method options to use as a default for all methods created within this API unless custom options are specified.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="parentResource")
    def parent_resource(self) -> typing.Optional["IResource"]:
        """The parent of this resource or undefined for the root resource.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addMethod")
    def add_method(self, http_method: str, target: typing.Optional["Integration"]=None, *, api_key_required: typing.Optional[bool]=None, authorization_type: typing.Optional["AuthorizationType"]=None, authorizer_id: typing.Optional[str]=None, method_responses: typing.Optional[typing.List["MethodResponse"]]=None, operation_name: typing.Optional[str]=None, request_parameters: typing.Optional[typing.Mapping[str,bool]]=None) -> "Method":
        """Defines a new method for this resource.

        Arguments:
            httpMethod: The HTTP method.
            target: The target backend integration for this method.
            options: Method options, such as authentication.
            apiKeyRequired: Indicates whether the method requires clients to submit a valid API key. Default: false
            authorizationType: Method authorization. Default: None open access
            authorizerId: If ``authorizationType`` is ``Custom``, this specifies the ID of the method authorizer resource. NOTE: in the future this will be replaced with an ``IAuthorizer`` construct.
            methodResponses: The responses that can be sent to the client who calls the method. Default: None This property is not required, but if these are not supplied for a Lambda proxy integration, the Lambda function must return a value of the correct format, for the integration response to be correctly mapped to a response to the client.
            operationName: A friendly operation name for the method. For example, you can assign the OperationName of ListPets for the GET /pets method.
            requestParameters: The request parameters that API Gateway accepts. Specify request parameters as key-value pairs (string-to-Boolean mapping), with a source as the key and a Boolean as the value. The Boolean specifies whether a parameter is required. A source must match the format method.request.location.name, where the location is querystring, path, or header, and name is a valid, unique parameter name. Default: None

        Returns:
            The newly created ``Method`` object.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addProxy")
    def add_proxy(self, *, default_integration: typing.Optional["Integration"]=None, default_method_options: typing.Optional["MethodOptions"]=None) -> "ProxyResource":
        """Adds a greedy proxy resource ("{proxy+}") and an ANY method to this route.

        Arguments:
            options: Default integration and method options.
            defaultIntegration: An integration to use as a default for all methods created within this API unless an integration is specified. Default: - Inherited from parent.
            defaultMethodOptions: Method options to use as a default for all methods created within this API unless custom options are specified. Default: - Inherited from parent.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="addResource")
    def add_resource(self, path_part: str, *, default_integration: typing.Optional["Integration"]=None, default_method_options: typing.Optional["MethodOptions"]=None) -> "Resource":
        """Defines a new child resource where this resource is the parent.

        Arguments:
            pathPart: The path part for the child resource.
            options: Resource options.
            defaultIntegration: An integration to use as a default for all methods created within this API unless an integration is specified. Default: - Inherited from parent.
            defaultMethodOptions: Method options to use as a default for all methods created within this API unless custom options are specified. Default: - Inherited from parent.

        Returns:
            A Resource object

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="getResource")
    def get_resource(self, path_part: str) -> typing.Optional["IResource"]:
        """Retrieves a child resource by path part.

        Arguments:
            pathPart: The path part of the child resource.

        Returns:
            the child resource or undefined if not found

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="resourceForPath")
    def resource_for_path(self, path: str) -> "Resource":
        """Gets or create all resources leading up to the specified path.

        - Path may only start with "/" if this method is called on the root resource.
        - All resources are created using default options.

        Arguments:
            path: The relative path.

        Returns:
            a new or existing resource.

        Stability:
            experimental
        """
        ...


class _IResourceProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-apigateway.IResource"
    @property
    @jsii.member(jsii_name="path")
    def path(self) -> str:
        """The full path of this resuorce.

        Stability:
            experimental
        """
        return jsii.get(self, "path")

    @property
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> str:
        """The ID of the resource.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "resourceId")

    @property
    @jsii.member(jsii_name="restApi")
    def rest_api(self) -> "RestApi":
        """The rest API that this resource is part of.

        The reason we need the RestApi object itself and not just the ID is because the model
        is being tracked by the top-level RestApi object for the purpose of calculating it's
        hash to determine the ID of the deployment. This allows us to automatically update
        the deployment when the model of the REST API changes.

        Stability:
            experimental
        """
        return jsii.get(self, "restApi")

    @property
    @jsii.member(jsii_name="defaultIntegration")
    def default_integration(self) -> typing.Optional["Integration"]:
        """An integration to use as a default for all methods created within this API unless an integration is specified.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultIntegration")

    @property
    @jsii.member(jsii_name="defaultMethodOptions")
    def default_method_options(self) -> typing.Optional["MethodOptions"]:
        """Method options to use as a default for all methods created within this API unless custom options are specified.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultMethodOptions")

    @property
    @jsii.member(jsii_name="parentResource")
    def parent_resource(self) -> typing.Optional["IResource"]:
        """The parent of this resource or undefined for the root resource.

        Stability:
            experimental
        """
        return jsii.get(self, "parentResource")

    @jsii.member(jsii_name="addMethod")
    def add_method(self, http_method: str, target: typing.Optional["Integration"]=None, *, api_key_required: typing.Optional[bool]=None, authorization_type: typing.Optional["AuthorizationType"]=None, authorizer_id: typing.Optional[str]=None, method_responses: typing.Optional[typing.List["MethodResponse"]]=None, operation_name: typing.Optional[str]=None, request_parameters: typing.Optional[typing.Mapping[str,bool]]=None) -> "Method":
        """Defines a new method for this resource.

        Arguments:
            httpMethod: The HTTP method.
            target: The target backend integration for this method.
            options: Method options, such as authentication.
            apiKeyRequired: Indicates whether the method requires clients to submit a valid API key. Default: false
            authorizationType: Method authorization. Default: None open access
            authorizerId: If ``authorizationType`` is ``Custom``, this specifies the ID of the method authorizer resource. NOTE: in the future this will be replaced with an ``IAuthorizer`` construct.
            methodResponses: The responses that can be sent to the client who calls the method. Default: None This property is not required, but if these are not supplied for a Lambda proxy integration, the Lambda function must return a value of the correct format, for the integration response to be correctly mapped to a response to the client.
            operationName: A friendly operation name for the method. For example, you can assign the OperationName of ListPets for the GET /pets method.
            requestParameters: The request parameters that API Gateway accepts. Specify request parameters as key-value pairs (string-to-Boolean mapping), with a source as the key and a Boolean as the value. The Boolean specifies whether a parameter is required. A source must match the format method.request.location.name, where the location is querystring, path, or header, and name is a valid, unique parameter name. Default: None

        Returns:
            The newly created ``Method`` object.

        Stability:
            experimental
        """
        options: MethodOptions = {}

        if api_key_required is not None:
            options["apiKeyRequired"] = api_key_required

        if authorization_type is not None:
            options["authorizationType"] = authorization_type

        if authorizer_id is not None:
            options["authorizerId"] = authorizer_id

        if method_responses is not None:
            options["methodResponses"] = method_responses

        if operation_name is not None:
            options["operationName"] = operation_name

        if request_parameters is not None:
            options["requestParameters"] = request_parameters

        return jsii.invoke(self, "addMethod", [http_method, target, options])

    @jsii.member(jsii_name="addProxy")
    def add_proxy(self, *, default_integration: typing.Optional["Integration"]=None, default_method_options: typing.Optional["MethodOptions"]=None) -> "ProxyResource":
        """Adds a greedy proxy resource ("{proxy+}") and an ANY method to this route.

        Arguments:
            options: Default integration and method options.
            defaultIntegration: An integration to use as a default for all methods created within this API unless an integration is specified. Default: - Inherited from parent.
            defaultMethodOptions: Method options to use as a default for all methods created within this API unless custom options are specified. Default: - Inherited from parent.

        Stability:
            experimental
        """
        options: ResourceOptions = {}

        if default_integration is not None:
            options["defaultIntegration"] = default_integration

        if default_method_options is not None:
            options["defaultMethodOptions"] = default_method_options

        return jsii.invoke(self, "addProxy", [options])

    @jsii.member(jsii_name="addResource")
    def add_resource(self, path_part: str, *, default_integration: typing.Optional["Integration"]=None, default_method_options: typing.Optional["MethodOptions"]=None) -> "Resource":
        """Defines a new child resource where this resource is the parent.

        Arguments:
            pathPart: The path part for the child resource.
            options: Resource options.
            defaultIntegration: An integration to use as a default for all methods created within this API unless an integration is specified. Default: - Inherited from parent.
            defaultMethodOptions: Method options to use as a default for all methods created within this API unless custom options are specified. Default: - Inherited from parent.

        Returns:
            A Resource object

        Stability:
            experimental
        """
        options: ResourceOptions = {}

        if default_integration is not None:
            options["defaultIntegration"] = default_integration

        if default_method_options is not None:
            options["defaultMethodOptions"] = default_method_options

        return jsii.invoke(self, "addResource", [path_part, options])

    @jsii.member(jsii_name="getResource")
    def get_resource(self, path_part: str) -> typing.Optional["IResource"]:
        """Retrieves a child resource by path part.

        Arguments:
            pathPart: The path part of the child resource.

        Returns:
            the child resource or undefined if not found

        Stability:
            experimental
        """
        return jsii.invoke(self, "getResource", [path_part])

    @jsii.member(jsii_name="resourceForPath")
    def resource_for_path(self, path: str) -> "Resource":
        """Gets or create all resources leading up to the specified path.

        - Path may only start with "/" if this method is called on the root resource.
        - All resources are created using default options.

        Arguments:
            path: The relative path.

        Returns:
            a new or existing resource.

        Stability:
            experimental
        """
        return jsii.invoke(self, "resourceForPath", [path])


@jsii.interface(jsii_type="@aws-cdk/aws-apigateway.IRestApi")
class IRestApi(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IRestApiProxy

    @property
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> str:
        """The ID of this API Gateway RestApi.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IRestApiProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-apigateway.IRestApi"
    @property
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> str:
        """The ID of this API Gateway RestApi.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "restApiId")


class Integration(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.Integration"):
    """Base class for backend integrations for an API Gateway method.

    Use one of the concrete classes such as ``MockIntegration``, ``AwsIntegration``, ``LambdaIntegration``
    or implement on your own by specifying the set of props.

    Stability:
        experimental
    """
    def __init__(self, *, type: "IntegrationType", integration_http_method: typing.Optional[str]=None, options: typing.Optional["IntegrationOptions"]=None, uri: typing.Any=None) -> None:
        """
        Arguments:
            props: -
            type: Specifies an API method integration type.
            integrationHttpMethod: The integration's HTTP method type. Required unless you use a MOCK integration.
            options: Integration options.
            uri: The Uniform Resource Identifier (URI) for the integration. - If you specify HTTP for the ``type`` property, specify the API endpoint URL. - If you specify MOCK for the ``type`` property, don't specify this property. - If you specify AWS for the ``type`` property, specify an AWS service that follows this form: ``arn:aws:apigateway:region:subdomain.service|service:path|action/service_api.`` For example, a Lambda function URI follows this form: arn:aws:apigateway:region:lambda:path/path. The path is usually in the form /2015-03-31/functions/LambdaFunctionARN/invocations.

        Stability:
            experimental
        """
        props: IntegrationProps = {"type": type}

        if integration_http_method is not None:
            props["integrationHttpMethod"] = integration_http_method

        if options is not None:
            props["options"] = options

        if uri is not None:
            props["uri"] = uri

        jsii.create(Integration, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(self, _method: "Method") -> None:
        """Can be overridden by subclasses to allow the integration to interact with the method being integrated, access the REST API object, method ARNs, etc.

        Arguments:
            _method: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_method])

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "IntegrationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")


class AwsIntegration(Integration, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.AwsIntegration"):
    """This type of integration lets an API expose AWS service actions.

    It is
    intended for calling all AWS service actions, but is not recommended for
    calling a Lambda function, because the Lambda custom integration is a legacy
    technology.

    Stability:
        experimental
    """
    def __init__(self, *, service: str, action: typing.Optional[str]=None, action_parameters: typing.Optional[typing.Mapping[str,str]]=None, integration_http_method: typing.Optional[str]=None, options: typing.Optional["IntegrationOptions"]=None, path: typing.Optional[str]=None, proxy: typing.Optional[bool]=None, subdomain: typing.Optional[str]=None) -> None:
        """
        Arguments:
            props: -
            service: The name of the integrated AWS service (e.g. ``s3``).
            action: The AWS action to perform in the integration. Use ``actionParams`` to specify key-value params for the action. Mutually exclusive with ``path``.
            actionParameters: Parameters for the action. ``action`` must be set, and ``path`` must be undefined. The action params will be URL encoded.
            integrationHttpMethod: The integration's HTTP method type. Default: POST
            options: Integration options, such as content handling, request/response mapping, etc.
            path: The path to use for path-base APIs. For example, for S3 GET, you can set path to ``bucket/key``. For lambda, you can set path to ``2015-03-31/functions/${function-arn}/invocations`` Mutually exclusive with the ``action`` options.
            proxy: Use AWS_PROXY integration. Default: false
            subdomain: A designated subdomain supported by certain AWS service for fast host-name lookup.

        Stability:
            experimental
        """
        props: AwsIntegrationProps = {"service": service}

        if action is not None:
            props["action"] = action

        if action_parameters is not None:
            props["actionParameters"] = action_parameters

        if integration_http_method is not None:
            props["integrationHttpMethod"] = integration_http_method

        if options is not None:
            props["options"] = options

        if path is not None:
            props["path"] = path

        if proxy is not None:
            props["proxy"] = proxy

        if subdomain is not None:
            props["subdomain"] = subdomain

        jsii.create(AwsIntegration, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(self, method: "Method") -> None:
        """Can be overridden by subclasses to allow the integration to interact with the method being integrated, access the REST API object, method ARNs, etc.

        Arguments:
            method: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [method])


class HttpIntegration(Integration, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.HttpIntegration"):
    """You can integrate an API method with an HTTP endpoint using the HTTP proxy integration or the HTTP custom integration,.

    With the proxy integration, the setup is simple. You only need to set the
    HTTP method and the HTTP endpoint URI, according to the backend requirements,
    if you are not concerned with content encoding or caching.

    With the custom integration, the setup is more involved. In addition to the
    proxy integration setup steps, you need to specify how the incoming request
    data is mapped to the integration request and how the resulting integration
    response data is mapped to the method response.

    Stability:
        experimental
    """
    def __init__(self, url: str, *, http_method: typing.Optional[str]=None, options: typing.Optional["IntegrationOptions"]=None, proxy: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            url: -
            props: -
            httpMethod: HTTP method to use when invoking the backend URL. Default: GET
            options: Integration options, such as request/resopnse mapping, content handling, etc. Default: defaults based on ``IntegrationOptions`` defaults
            proxy: Determines whether to use proxy integration or custom integration. Default: true

        Stability:
            experimental
        """
        props: HttpIntegrationProps = {}

        if http_method is not None:
            props["httpMethod"] = http_method

        if options is not None:
            props["options"] = options

        if proxy is not None:
            props["proxy"] = proxy

        jsii.create(HttpIntegration, self, [url, props])


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.IntegrationOptions", jsii_struct_bases=[])
class IntegrationOptions(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    cacheKeyParameters: typing.List[str]
    """A list of request parameters whose values are to be cached.

    It determines
    request parameters that will make it into the cache key.

    Stability:
        experimental
    """

    cacheNamespace: str
    """An API-specific tag group of related cached parameters.

    Stability:
        experimental
    """

    connectionType: "ConnectionType"
    """The type of network connection to the integration endpoint.

    Default:
        ConnectionType.Internet

    Stability:
        experimental
    """

    contentHandling: "ContentHandling"
    """Specifies how to handle request payload content type conversions.

    Default:
        none if this property isn't defined, the request payload is passed
        through from the method request to the integration request without
        modification, provided that the ``passthroughBehaviors`` property is
        configured to support payload pass-through.

    Stability:
        experimental
    """

    credentialsPassthrough: bool
    """Requires that the caller's identity be passed through from the request.

    Default:
        Caller identity is not passed through

    Stability:
        experimental
    """

    credentialsRole: aws_cdk.aws_iam.Role
    """An IAM role that API Gateway assumes.

    Mutually exclusive with ``credentialsPassThrough``.

    Default:
        A role is not assumed

    Stability:
        experimental
    """

    integrationResponses: typing.List["IntegrationResponse"]
    """The response that API Gateway provides after a method's backend completes processing a request.

    API Gateway intercepts the response from the
    backend so that you can control how API Gateway surfaces backend
    responses. For example, you can map the backend status codes to codes
    that you define.

    Stability:
        experimental
    """

    passthroughBehavior: "PassthroughBehavior"
    """Specifies the pass-through behavior for incoming requests based on the Content-Type header in the request, and the available mapping templates specified as the requestTemplates property on the Integration resource. There are three valid values: WHEN_NO_MATCH, WHEN_NO_TEMPLATES, and NEVER.

    Stability:
        experimental
    """

    requestParameters: typing.Mapping[str,str]
    """The request parameters that API Gateway sends with the backend request. Specify request parameters as key-value pairs (string-to-string mappings), with a destination as the key and a source as the value.

    Specify the destination by using the following pattern
    integration.request.location.name, where location is querystring, path,
    or header, and name is a valid, unique parameter name.

    The source must be an existing method request parameter or a static
    value. You must enclose static values in single quotation marks and
    pre-encode these values based on their destination in the request.

    Stability:
        experimental
    """

    requestTemplates: typing.Mapping[str,str]
    """A map of Apache Velocity templates that are applied on the request payload.

    The template that API Gateway uses is based on the value of the
    Content-Type header that's sent by the client. The content type value is
    the key, and the template is the value (specified as a string), such as
    the following snippet:

    { "application/json": "{\n  "statusCode": "200"\n}" }

    See:
        http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
    Stability:
        experimental
    """

    vpcLink: "VpcLink"
    """The VpcLink used for the integration. Required if connectionType is VPC_LINK.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _IntegrationProps(jsii.compat.TypedDict, total=False):
    integrationHttpMethod: str
    """The integration's HTTP method type. Required unless you use a MOCK integration.

    Stability:
        experimental
    """
    options: "IntegrationOptions"
    """Integration options.

    Stability:
        experimental
    """
    uri: typing.Any
    """The Uniform Resource Identifier (URI) for the integration.

    - If you specify HTTP for the ``type`` property, specify the API endpoint URL.
    - If you specify MOCK for the ``type`` property, don't specify this property.
    - If you specify AWS for the ``type`` property, specify an AWS service that
      follows this form: ``arn:aws:apigateway:region:subdomain.service|service:path|action/service_api.``
      For example, a Lambda function URI follows this form:
      arn:aws:apigateway:region:lambda:path/path. The path is usually in the
      form /2015-03-31/functions/LambdaFunctionARN/invocations.

    See:
        https://docs.aws.amazon.com/apigateway/api-reference/resource/integration/#uri
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.IntegrationProps", jsii_struct_bases=[_IntegrationProps])
class IntegrationProps(_IntegrationProps):
    """
    Stability:
        experimental
    """
    type: "IntegrationType"
    """Specifies an API method integration type.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _IntegrationResponse(jsii.compat.TypedDict, total=False):
    contentHandling: "ContentHandling"
    """Specifies how to handle request payload content type conversions.

    Default:
        none the request payload is passed through from the method
        request to the integration request without modification.

    Stability:
        experimental
    """
    responseParameters: typing.Mapping[str,str]
    """The response parameters from the backend response that API Gateway sends to the method response.

    Use the destination as the key and the source as the value:

    - The destination must be an existing response parameter in the
      MethodResponse property.
    - The source must be an existing method request parameter or a static
      value. You must enclose static values in single quotation marks and
      pre-encode these values based on the destination specified in the
      request.

    See:
        http://docs.aws.amazon.com/apigateway/latest/developerguide/request-response-data-mappings.html
    Stability:
        experimental
    """
    responseTemplates: typing.Mapping[str,str]
    """The templates that are used to transform the integration response body. Specify templates as key-value pairs, with a content type as the key and a template as the value.

    See:
        http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
    Stability:
        experimental
    """
    selectionPattern: str
    """Specifies the regular expression (regex) pattern used to choose an integration response based on the response from the back end.

    For example, if the success response returns nothing and the error response returns some string, you
    could use the ``.+`` regex to match error response. However, make sure that the error response does not contain any
    newline (``\n``) character in such cases. If the back end is an AWS Lambda function, the AWS Lambda function error
    header is matched. For all other HTTP and AWS back ends, the HTTP status code is matched.

    See:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-integration-settings-integration-response.html
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.IntegrationResponse", jsii_struct_bases=[_IntegrationResponse])
class IntegrationResponse(_IntegrationResponse):
    """
    Stability:
        experimental
    """
    statusCode: str
    """The status code that API Gateway uses to map the integration response to a MethodResponse status code.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-apigateway.IntegrationType")
class IntegrationType(enum.Enum):
    """
    Stability:
        experimental
    """
    Aws = "Aws"
    """For integrating the API method request with an AWS service action, including the Lambda function-invoking action.

    With the Lambda
    function-invoking action, this is referred to as the Lambda custom
    integration. With any other AWS service action, this is known as AWS
    integration.

    Stability:
        experimental
    """
    AwsProxy = "AwsProxy"
    """For integrating the API method request with the Lambda function-invoking action with the client request passed through as-is.

    This integration is
    also referred to as the Lambda proxy integration

    Stability:
        experimental
    """
    Http = "Http"
    """For integrating the API method request with an HTTP endpoint, including a private HTTP endpoint within a VPC.

    This integration is also referred to
    as the HTTP custom integration.

    Stability:
        experimental
    """
    HttpProxy = "HttpProxy"
    """For integrating the API method request with an HTTP endpoint, including a private HTTP endpoint within a VPC, with the client request passed through as-is.

    This is also referred to as the HTTP proxy integration

    Stability:
        experimental
    """
    Mock = "Mock"
    """For integrating the API method request with API Gateway as a "loop-back" endpoint without invoking any backend.

    Stability:
        experimental
    """

class LambdaIntegration(AwsIntegration, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.LambdaIntegration"):
    """Integrates an AWS Lambda function to an API Gateway method.

    Stability:
        experimental

    Example::
           const handler = new lambda.Function(this, 'MyFunction', ...);
           api.addMethod('GET', new LambdaIntegration(handler));
    """
    def __init__(self, handler: aws_cdk.aws_lambda.IFunction, *, allow_test_invoke: typing.Optional[bool]=None, proxy: typing.Optional[bool]=None, cache_key_parameters: typing.Optional[typing.List[str]]=None, cache_namespace: typing.Optional[str]=None, connection_type: typing.Optional["ConnectionType"]=None, content_handling: typing.Optional["ContentHandling"]=None, credentials_passthrough: typing.Optional[bool]=None, credentials_role: typing.Optional[aws_cdk.aws_iam.Role]=None, integration_responses: typing.Optional[typing.List["IntegrationResponse"]]=None, passthrough_behavior: typing.Optional["PassthroughBehavior"]=None, request_parameters: typing.Optional[typing.Mapping[str,str]]=None, request_templates: typing.Optional[typing.Mapping[str,str]]=None, vpc_link: typing.Optional["VpcLink"]=None) -> None:
        """
        Arguments:
            handler: -
            options: -
            allowTestInvoke: Allow invoking method from AWS Console UI (for testing purposes). This will add another permission to the AWS Lambda resource policy which will allow the ``test-invoke-stage`` stage to invoke this handler. If this is set to ``false``, the function will only be usable from the deployment endpoint. Default: true
            proxy: Use proxy integration or normal (request/response mapping) integration. Default: true
            cacheKeyParameters: A list of request parameters whose values are to be cached. It determines request parameters that will make it into the cache key.
            cacheNamespace: An API-specific tag group of related cached parameters.
            connectionType: The type of network connection to the integration endpoint. Default: ConnectionType.Internet
            contentHandling: Specifies how to handle request payload content type conversions. Default: none if this property isn't defined, the request payload is passed through from the method request to the integration request without modification, provided that the ``passthroughBehaviors`` property is configured to support payload pass-through.
            credentialsPassthrough: Requires that the caller's identity be passed through from the request. Default: Caller identity is not passed through
            credentialsRole: An IAM role that API Gateway assumes. Mutually exclusive with ``credentialsPassThrough``. Default: A role is not assumed
            integrationResponses: The response that API Gateway provides after a method's backend completes processing a request. API Gateway intercepts the response from the backend so that you can control how API Gateway surfaces backend responses. For example, you can map the backend status codes to codes that you define.
            passthroughBehavior: Specifies the pass-through behavior for incoming requests based on the Content-Type header in the request, and the available mapping templates specified as the requestTemplates property on the Integration resource. There are three valid values: WHEN_NO_MATCH, WHEN_NO_TEMPLATES, and NEVER.
            requestParameters: The request parameters that API Gateway sends with the backend request. Specify request parameters as key-value pairs (string-to-string mappings), with a destination as the key and a source as the value. Specify the destination by using the following pattern integration.request.location.name, where location is querystring, path, or header, and name is a valid, unique parameter name. The source must be an existing method request parameter or a static value. You must enclose static values in single quotation marks and pre-encode these values based on their destination in the request.
            requestTemplates: A map of Apache Velocity templates that are applied on the request payload. The template that API Gateway uses is based on the value of the Content-Type header that's sent by the client. The content type value is the key, and the template is the value (specified as a string), such as the following snippet: { "application/json": "{\n "statusCode": "200"\n}" }
            vpcLink: The VpcLink used for the integration. Required if connectionType is VPC_LINK.

        Stability:
            experimental
        """
        options: LambdaIntegrationOptions = {}

        if allow_test_invoke is not None:
            options["allowTestInvoke"] = allow_test_invoke

        if proxy is not None:
            options["proxy"] = proxy

        if cache_key_parameters is not None:
            options["cacheKeyParameters"] = cache_key_parameters

        if cache_namespace is not None:
            options["cacheNamespace"] = cache_namespace

        if connection_type is not None:
            options["connectionType"] = connection_type

        if content_handling is not None:
            options["contentHandling"] = content_handling

        if credentials_passthrough is not None:
            options["credentialsPassthrough"] = credentials_passthrough

        if credentials_role is not None:
            options["credentialsRole"] = credentials_role

        if integration_responses is not None:
            options["integrationResponses"] = integration_responses

        if passthrough_behavior is not None:
            options["passthroughBehavior"] = passthrough_behavior

        if request_parameters is not None:
            options["requestParameters"] = request_parameters

        if request_templates is not None:
            options["requestTemplates"] = request_templates

        if vpc_link is not None:
            options["vpcLink"] = vpc_link

        jsii.create(LambdaIntegration, self, [handler, options])

    @jsii.member(jsii_name="bind")
    def bind(self, method: "Method") -> None:
        """Can be overridden by subclasses to allow the integration to interact with the method being integrated, access the REST API object, method ARNs, etc.

        Arguments:
            method: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [method])


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.LambdaIntegrationOptions", jsii_struct_bases=[IntegrationOptions])
class LambdaIntegrationOptions(IntegrationOptions, jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    allowTestInvoke: bool
    """Allow invoking method from AWS Console UI (for testing purposes).

    This will add another permission to the AWS Lambda resource policy which
    will allow the ``test-invoke-stage`` stage to invoke this handler. If this
    is set to ``false``, the function will only be usable from the deployment
    endpoint.

    Default:
        true

    Stability:
        experimental
    """

    proxy: bool
    """Use proxy integration or normal (request/response mapping) integration.

    Default:
        true

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _LambdaRestApiProps(jsii.compat.TypedDict, total=False):
    options: "RestApiProps"
    """Further customization of the REST API.

    Default:
        defaults

    Stability:
        experimental
    """
    proxy: bool
    """If true, route all requests to the Lambda Function.

    If set to false, you will need to explicitly define the API model using
    ``addResource`` and ``addMethod`` (or ``addProxy``).

    Default:
        true

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.LambdaRestApiProps", jsii_struct_bases=[_LambdaRestApiProps])
class LambdaRestApiProps(_LambdaRestApiProps):
    """
    Stability:
        experimental
    """
    handler: aws_cdk.aws_lambda.IFunction
    """The default Lambda function that handles all requests from this API.

    This handler will be used as a the default integration for all methods in
    this API, unless specified otherwise in ``addMethod``.

    Stability:
        experimental
    """

class Method(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.Method"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, http_method: str, resource: "IResource", integration: typing.Optional["Integration"]=None, options: typing.Optional["MethodOptions"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            httpMethod: The HTTP method ("GET", "POST", "PUT", ...) that clients use to call this method.
            resource: The resource this method is associated with. For root resource methods, specify the ``RestApi`` object.
            integration: The backend system that the method calls when it receives a request. Default: - a new ``MockIntegration``.
            options: Method options. Default: - No options.

        Stability:
            experimental
        """
        props: MethodProps = {"httpMethod": http_method, "resource": resource}

        if integration is not None:
            props["integration"] = integration

        if options is not None:
            props["options"] = options

        jsii.create(Method, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="httpMethod")
    def http_method(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "httpMethod")

    @property
    @jsii.member(jsii_name="methodArn")
    def method_arn(self) -> str:
        """Returns an execute-api ARN for this method:.

        arn:aws:execute-api:{region}:{account}:{restApiId}/{stage}/{method}/{path}

        NOTE: {stage} will refer to the ``restApi.deploymentStage``, which will
        automatically set if auto-deploy is enabled.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "methodArn")

    @property
    @jsii.member(jsii_name="methodId")
    def method_id(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "methodId")

    @property
    @jsii.member(jsii_name="resource")
    def resource(self) -> "IResource":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "resource")

    @property
    @jsii.member(jsii_name="restApi")
    def rest_api(self) -> "RestApi":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "restApi")

    @property
    @jsii.member(jsii_name="testMethodArn")
    def test_method_arn(self) -> str:
        """Returns an execute-api ARN for this method's "test-invoke-stage" stage. This stage is used by the AWS Console UI when testing the method.

        Stability:
            experimental
        """
        return jsii.get(self, "testMethodArn")


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.MethodDeploymentOptions", jsii_struct_bases=[])
class MethodDeploymentOptions(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    cacheDataEncrypted: bool
    """Indicates whether the cached responses are encrypted.

    Default:
        false

    Stability:
        experimental
    """

    cacheTtlSeconds: jsii.Number
    """Specifies the time to live (TTL), in seconds, for cached responses.

    The
    higher the TTL, the longer the response will be cached.

    Default:
        300

    See:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-caching.html
    Stability:
        experimental
    """

    cachingEnabled: bool
    """Specifies whether responses should be cached and returned for requests.

    A
    cache cluster must be enabled on the stage for responses to be cached.

    Default:
        - Caching is Disabled.

    Stability:
        experimental
    """

    dataTraceEnabled: bool
    """Specifies whether data trace logging is enabled for this method, which effects the log entries pushed to Amazon CloudWatch Logs.

    Default:
        false

    Stability:
        experimental
    """

    loggingLevel: "MethodLoggingLevel"
    """Specifies the logging level for this method, which effects the log entries pushed to Amazon CloudWatch Logs.

    Default:
        - Off

    Stability:
        experimental
    """

    metricsEnabled: bool
    """Specifies whether Amazon CloudWatch metrics are enabled for this method.

    Default:
        false

    Stability:
        experimental
    """

    throttlingBurstLimit: jsii.Number
    """Specifies the throttling burst limit. The total rate of all requests in your AWS account is limited to 5,000 requests.

    Default:
        - No additional restriction.

    See:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html
    Stability:
        experimental
    """

    throttlingRateLimit: jsii.Number
    """Specifies the throttling rate limit. The total rate of all requests in your AWS account is limited to 10,000 requests per second (rps).

    Default:
        - No additional restriction.

    See:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html
    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-apigateway.MethodLoggingLevel")
class MethodLoggingLevel(enum.Enum):
    """
    Stability:
        experimental
    """
    Off = "Off"
    """
    Stability:
        experimental
    """
    Error = "Error"
    """
    Stability:
        experimental
    """
    Info = "Info"
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.MethodOptions", jsii_struct_bases=[])
class MethodOptions(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    apiKeyRequired: bool
    """Indicates whether the method requires clients to submit a valid API key.

    Default:
        false

    Stability:
        experimental
    """

    authorizationType: "AuthorizationType"
    """Method authorization.

    Default:
        None open access

    Stability:
        experimental
    """

    authorizerId: str
    """If ``authorizationType`` is ``Custom``, this specifies the ID of the method authorizer resource.

    NOTE: in the future this will be replaced with an ``IAuthorizer``
    construct.

    Stability:
        experimental
    """

    methodResponses: typing.List["MethodResponse"]
    """The responses that can be sent to the client who calls the method.

    Default:
        None
        
        This property is not required, but if these are not supplied for a Lambda
        proxy integration, the Lambda function must return a value of the correct format,
        for the integration response to be correctly mapped to a response to the client.

    See:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-method-settings-method-response.html
    Stability:
        experimental
    """

    operationName: str
    """A friendly operation name for the method.

    For example, you can assign the
    OperationName of ListPets for the GET /pets method.

    Stability:
        experimental
    """

    requestParameters: typing.Mapping[str,bool]
    """The request parameters that API Gateway accepts.

    Specify request parameters
    as key-value pairs (string-to-Boolean mapping), with a source as the key and
    a Boolean as the value. The Boolean specifies whether a parameter is required.
    A source must match the format method.request.location.name, where the location
    is querystring, path, or header, and name is a valid, unique parameter name.

    Default:
        None

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _MethodProps(jsii.compat.TypedDict, total=False):
    integration: "Integration"
    """The backend system that the method calls when it receives a request.

    Default:
        - a new ``MockIntegration``.

    Stability:
        experimental
    """
    options: "MethodOptions"
    """Method options.

    Default:
        - No options.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.MethodProps", jsii_struct_bases=[_MethodProps])
class MethodProps(_MethodProps):
    """
    Stability:
        experimental
    """
    httpMethod: str
    """The HTTP method ("GET", "POST", "PUT", ...) that clients use to call this method.

    Stability:
        experimental
    """

    resource: "IResource"
    """The resource this method is associated with.

    For root resource methods,
    specify the ``RestApi`` object.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _MethodResponse(jsii.compat.TypedDict, total=False):
    responseModels: typing.Mapping[str,"IModel"]
    """The resources used for the response's content type.

    Specify response models as
    key-value pairs (string-to-string maps), with a content type as the key and a Model
    resource name as the value.

    Default:
        None

    Stability:
        experimental
    """
    responseParameters: typing.Mapping[str,bool]
    """Response parameters that API Gateway sends to the client that called a method. Specify response parameters as key-value pairs (string-to-Boolean maps), with a destination as the key and a Boolean as the value. Specify the destination using the following pattern: method.response.header.name, where the name is a valid, unique header name. The Boolean specifies whether a parameter is required.

    Default:
        None

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.MethodResponse", jsii_struct_bases=[_MethodResponse])
class MethodResponse(_MethodResponse):
    """
    Stability:
        experimental
    """
    statusCode: str
    """The method response's status code, which you map to an IntegrationResponse. Required.

    Stability:
        experimental
    """

class MockIntegration(Integration, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.MockIntegration"):
    """This type of integration lets API Gateway return a response without sending the request further to the backend.

    This is useful for API testing because it
    can be used to test the integration set up without incurring charges for
    using the backend and to enable collaborative development of an API. In
    collaborative development, a team can isolate their development effort by
    setting up simulations of API components owned by other teams by using the
    MOCK integrations. It is also used to return CORS-related headers to ensure
    that the API method permits CORS access. In fact, the API Gateway console
    integrates the OPTIONS method to support CORS with a mock integration.
    Gateway responses are other examples of mock integrations.

    Stability:
        experimental
    """
    def __init__(self, *, cache_key_parameters: typing.Optional[typing.List[str]]=None, cache_namespace: typing.Optional[str]=None, connection_type: typing.Optional["ConnectionType"]=None, content_handling: typing.Optional["ContentHandling"]=None, credentials_passthrough: typing.Optional[bool]=None, credentials_role: typing.Optional[aws_cdk.aws_iam.Role]=None, integration_responses: typing.Optional[typing.List["IntegrationResponse"]]=None, passthrough_behavior: typing.Optional["PassthroughBehavior"]=None, request_parameters: typing.Optional[typing.Mapping[str,str]]=None, request_templates: typing.Optional[typing.Mapping[str,str]]=None, vpc_link: typing.Optional["VpcLink"]=None) -> None:
        """
        Arguments:
            options: -
            cacheKeyParameters: A list of request parameters whose values are to be cached. It determines request parameters that will make it into the cache key.
            cacheNamespace: An API-specific tag group of related cached parameters.
            connectionType: The type of network connection to the integration endpoint. Default: ConnectionType.Internet
            contentHandling: Specifies how to handle request payload content type conversions. Default: none if this property isn't defined, the request payload is passed through from the method request to the integration request without modification, provided that the ``passthroughBehaviors`` property is configured to support payload pass-through.
            credentialsPassthrough: Requires that the caller's identity be passed through from the request. Default: Caller identity is not passed through
            credentialsRole: An IAM role that API Gateway assumes. Mutually exclusive with ``credentialsPassThrough``. Default: A role is not assumed
            integrationResponses: The response that API Gateway provides after a method's backend completes processing a request. API Gateway intercepts the response from the backend so that you can control how API Gateway surfaces backend responses. For example, you can map the backend status codes to codes that you define.
            passthroughBehavior: Specifies the pass-through behavior for incoming requests based on the Content-Type header in the request, and the available mapping templates specified as the requestTemplates property on the Integration resource. There are three valid values: WHEN_NO_MATCH, WHEN_NO_TEMPLATES, and NEVER.
            requestParameters: The request parameters that API Gateway sends with the backend request. Specify request parameters as key-value pairs (string-to-string mappings), with a destination as the key and a source as the value. Specify the destination by using the following pattern integration.request.location.name, where location is querystring, path, or header, and name is a valid, unique parameter name. The source must be an existing method request parameter or a static value. You must enclose static values in single quotation marks and pre-encode these values based on their destination in the request.
            requestTemplates: A map of Apache Velocity templates that are applied on the request payload. The template that API Gateway uses is based on the value of the Content-Type header that's sent by the client. The content type value is the key, and the template is the value (specified as a string), such as the following snippet: { "application/json": "{\n "statusCode": "200"\n}" }
            vpcLink: The VpcLink used for the integration. Required if connectionType is VPC_LINK.

        Stability:
            experimental
        """
        options: IntegrationOptions = {}

        if cache_key_parameters is not None:
            options["cacheKeyParameters"] = cache_key_parameters

        if cache_namespace is not None:
            options["cacheNamespace"] = cache_namespace

        if connection_type is not None:
            options["connectionType"] = connection_type

        if content_handling is not None:
            options["contentHandling"] = content_handling

        if credentials_passthrough is not None:
            options["credentialsPassthrough"] = credentials_passthrough

        if credentials_role is not None:
            options["credentialsRole"] = credentials_role

        if integration_responses is not None:
            options["integrationResponses"] = integration_responses

        if passthrough_behavior is not None:
            options["passthroughBehavior"] = passthrough_behavior

        if request_parameters is not None:
            options["requestParameters"] = request_parameters

        if request_templates is not None:
            options["requestTemplates"] = request_templates

        if vpc_link is not None:
            options["vpcLink"] = vpc_link

        jsii.create(MockIntegration, self, [options])


@jsii.enum(jsii_type="@aws-cdk/aws-apigateway.PassthroughBehavior")
class PassthroughBehavior(enum.Enum):
    """
    Stability:
        experimental
    """
    WhenNoMatch = "WhenNoMatch"
    """Passes the request body for unmapped content types through to the integration back end without transformation.

    Stability:
        experimental
    """
    Never = "Never"
    """Rejects unmapped content types with an HTTP 415 'Unsupported Media Type' response.

    Stability:
        experimental
    """
    WhenNoTemplates = "WhenNoTemplates"
    """Allows pass-through when the integration has NO content types mapped to templates.

    However if there is at least one content type defined,
    unmapped content types will be rejected with the same 415 response.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-apigateway.Period")
class Period(enum.Enum):
    """Time period for which quota settings apply.

    Stability:
        experimental
    """
    Day = "Day"
    """
    Stability:
        experimental
    """
    Week = "Week"
    """
    Stability:
        experimental
    """
    Month = "Month"
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.QuotaSettings", jsii_struct_bases=[])
class QuotaSettings(jsii.compat.TypedDict, total=False):
    """Specifies the maximum number of requests that clients can make to API Gateway APIs.

    Stability:
        experimental
    """
    limit: jsii.Number
    """The maximum number of requests that users can make within the specified time period.

    Default:
        none

    Stability:
        experimental
    """

    offset: jsii.Number
    """For the initial time period, the number of requests to subtract from the specified limit.

    Default:
        none

    Stability:
        experimental
    """

    period: "Period"
    """The time period for which the maximum limit of requests applies.

    Default:
        none

    Stability:
        experimental
    """

@jsii.implements(IResource)
class ResourceBase(aws_cdk.cdk.Resource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-apigateway.ResourceBase"):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ResourceBaseProxy

    def __init__(self, scope: aws_cdk.cdk.Construct, id: str) -> None:
        """
        Arguments:
            scope: -
            id: -

        Stability:
            experimental
        """
        jsii.create(ResourceBase, self, [scope, id])

    @jsii.member(jsii_name="addMethod")
    def add_method(self, http_method: str, integration: typing.Optional["Integration"]=None, *, api_key_required: typing.Optional[bool]=None, authorization_type: typing.Optional["AuthorizationType"]=None, authorizer_id: typing.Optional[str]=None, method_responses: typing.Optional[typing.List["MethodResponse"]]=None, operation_name: typing.Optional[str]=None, request_parameters: typing.Optional[typing.Mapping[str,bool]]=None) -> "Method":
        """Defines a new method for this resource.

        Arguments:
            httpMethod: -
            integration: -
            options: -
            apiKeyRequired: Indicates whether the method requires clients to submit a valid API key. Default: false
            authorizationType: Method authorization. Default: None open access
            authorizerId: If ``authorizationType`` is ``Custom``, this specifies the ID of the method authorizer resource. NOTE: in the future this will be replaced with an ``IAuthorizer`` construct.
            methodResponses: The responses that can be sent to the client who calls the method. Default: None This property is not required, but if these are not supplied for a Lambda proxy integration, the Lambda function must return a value of the correct format, for the integration response to be correctly mapped to a response to the client.
            operationName: A friendly operation name for the method. For example, you can assign the OperationName of ListPets for the GET /pets method.
            requestParameters: The request parameters that API Gateway accepts. Specify request parameters as key-value pairs (string-to-Boolean mapping), with a source as the key and a Boolean as the value. The Boolean specifies whether a parameter is required. A source must match the format method.request.location.name, where the location is querystring, path, or header, and name is a valid, unique parameter name. Default: None

        Stability:
            experimental
        """
        options: MethodOptions = {}

        if api_key_required is not None:
            options["apiKeyRequired"] = api_key_required

        if authorization_type is not None:
            options["authorizationType"] = authorization_type

        if authorizer_id is not None:
            options["authorizerId"] = authorizer_id

        if method_responses is not None:
            options["methodResponses"] = method_responses

        if operation_name is not None:
            options["operationName"] = operation_name

        if request_parameters is not None:
            options["requestParameters"] = request_parameters

        return jsii.invoke(self, "addMethod", [http_method, integration, options])

    @jsii.member(jsii_name="addProxy")
    def add_proxy(self, *, default_integration: typing.Optional["Integration"]=None, default_method_options: typing.Optional["MethodOptions"]=None) -> "ProxyResource":
        """Adds a greedy proxy resource ("{proxy+}") and an ANY method to this route.

        Arguments:
            options: -
            defaultIntegration: An integration to use as a default for all methods created within this API unless an integration is specified. Default: - Inherited from parent.
            defaultMethodOptions: Method options to use as a default for all methods created within this API unless custom options are specified. Default: - Inherited from parent.

        Stability:
            experimental
        """
        options: ResourceOptions = {}

        if default_integration is not None:
            options["defaultIntegration"] = default_integration

        if default_method_options is not None:
            options["defaultMethodOptions"] = default_method_options

        return jsii.invoke(self, "addProxy", [options])

    @jsii.member(jsii_name="addResource")
    def add_resource(self, path_part: str, *, default_integration: typing.Optional["Integration"]=None, default_method_options: typing.Optional["MethodOptions"]=None) -> "Resource":
        """Defines a new child resource where this resource is the parent.

        Arguments:
            pathPart: -
            options: -
            defaultIntegration: An integration to use as a default for all methods created within this API unless an integration is specified. Default: - Inherited from parent.
            defaultMethodOptions: Method options to use as a default for all methods created within this API unless custom options are specified. Default: - Inherited from parent.

        Stability:
            experimental
        """
        options: ResourceOptions = {}

        if default_integration is not None:
            options["defaultIntegration"] = default_integration

        if default_method_options is not None:
            options["defaultMethodOptions"] = default_method_options

        return jsii.invoke(self, "addResource", [path_part, options])

    @jsii.member(jsii_name="getResource")
    def get_resource(self, path_part: str) -> typing.Optional["IResource"]:
        """Retrieves a child resource by path part.

        Arguments:
            pathPart: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getResource", [path_part])

    @jsii.member(jsii_name="resourceForPath")
    def resource_for_path(self, path: str) -> "Resource":
        """Gets or create all resources leading up to the specified path.

        - Path may only start with "/" if this method is called on the root resource.
        - All resources are created using default options.

        Arguments:
            path: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "resourceForPath", [path])

    @property
    @jsii.member(jsii_name="path")
    @abc.abstractmethod
    def path(self) -> str:
        """The full path of this resuorce.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="resourceId")
    @abc.abstractmethod
    def resource_id(self) -> str:
        """The ID of the resource.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="restApi")
    @abc.abstractmethod
    def rest_api(self) -> "RestApi":
        """The rest API that this resource is part of.

        The reason we need the RestApi object itself and not just the ID is because the model
        is being tracked by the top-level RestApi object for the purpose of calculating it's
        hash to determine the ID of the deployment. This allows us to automatically update
        the deployment when the model of the REST API changes.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="defaultIntegration")
    @abc.abstractmethod
    def default_integration(self) -> typing.Optional["Integration"]:
        """An integration to use as a default for all methods created within this API unless an integration is specified.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="defaultMethodOptions")
    @abc.abstractmethod
    def default_method_options(self) -> typing.Optional["MethodOptions"]:
        """Method options to use as a default for all methods created within this API unless custom options are specified.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="parentResource")
    @abc.abstractmethod
    def parent_resource(self) -> typing.Optional["IResource"]:
        """The parent of this resource or undefined for the root resource.

        Stability:
            experimental
        """
        ...


class _ResourceBaseProxy(ResourceBase, jsii.proxy_for(aws_cdk.cdk.Resource)):
    @property
    @jsii.member(jsii_name="path")
    def path(self) -> str:
        """The full path of this resuorce.

        Stability:
            experimental
        """
        return jsii.get(self, "path")

    @property
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> str:
        """The ID of the resource.

        Stability:
            experimental
        """
        return jsii.get(self, "resourceId")

    @property
    @jsii.member(jsii_name="restApi")
    def rest_api(self) -> "RestApi":
        """The rest API that this resource is part of.

        The reason we need the RestApi object itself and not just the ID is because the model
        is being tracked by the top-level RestApi object for the purpose of calculating it's
        hash to determine the ID of the deployment. This allows us to automatically update
        the deployment when the model of the REST API changes.

        Stability:
            experimental
        """
        return jsii.get(self, "restApi")

    @property
    @jsii.member(jsii_name="defaultIntegration")
    def default_integration(self) -> typing.Optional["Integration"]:
        """An integration to use as a default for all methods created within this API unless an integration is specified.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultIntegration")

    @property
    @jsii.member(jsii_name="defaultMethodOptions")
    def default_method_options(self) -> typing.Optional["MethodOptions"]:
        """Method options to use as a default for all methods created within this API unless custom options are specified.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultMethodOptions")

    @property
    @jsii.member(jsii_name="parentResource")
    def parent_resource(self) -> typing.Optional["IResource"]:
        """The parent of this resource or undefined for the root resource.

        Stability:
            experimental
        """
        return jsii.get(self, "parentResource")


class Resource(ResourceBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.Resource"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, parent: "IResource", path_part: str, default_integration: typing.Optional["Integration"]=None, default_method_options: typing.Optional["MethodOptions"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            parent: The parent resource of this resource. You can either pass another ``Resource`` object or a ``RestApi`` object here.
            pathPart: A path name for the resource.
            defaultIntegration: An integration to use as a default for all methods created within this API unless an integration is specified. Default: - Inherited from parent.
            defaultMethodOptions: Method options to use as a default for all methods created within this API unless custom options are specified. Default: - Inherited from parent.

        Stability:
            experimental
        """
        props: ResourceProps = {"parent": parent, "pathPart": path_part}

        if default_integration is not None:
            props["defaultIntegration"] = default_integration

        if default_method_options is not None:
            props["defaultMethodOptions"] = default_method_options

        jsii.create(Resource, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="path")
    def path(self) -> str:
        """The full path of this resuorce.

        Stability:
            experimental
        """
        return jsii.get(self, "path")

    @property
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> str:
        """The ID of the resource.

        Stability:
            experimental
        """
        return jsii.get(self, "resourceId")

    @property
    @jsii.member(jsii_name="restApi")
    def rest_api(self) -> "RestApi":
        """The rest API that this resource is part of.

        The reason we need the RestApi object itself and not just the ID is because the model
        is being tracked by the top-level RestApi object for the purpose of calculating it's
        hash to determine the ID of the deployment. This allows us to automatically update
        the deployment when the model of the REST API changes.

        Stability:
            experimental
        """
        return jsii.get(self, "restApi")

    @property
    @jsii.member(jsii_name="defaultIntegration")
    def default_integration(self) -> typing.Optional["Integration"]:
        """An integration to use as a default for all methods created within this API unless an integration is specified.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultIntegration")

    @property
    @jsii.member(jsii_name="defaultMethodOptions")
    def default_method_options(self) -> typing.Optional["MethodOptions"]:
        """Method options to use as a default for all methods created within this API unless custom options are specified.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultMethodOptions")

    @property
    @jsii.member(jsii_name="parentResource")
    def parent_resource(self) -> typing.Optional["IResource"]:
        """The parent of this resource or undefined for the root resource.

        Stability:
            experimental
        """
        return jsii.get(self, "parentResource")


class ProxyResource(Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.ProxyResource"):
    """Defines a {proxy+} greedy resource and an ANY method on a route.

    See:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-set-up-simple-proxy.html
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, parent: "IResource", any_method: typing.Optional[bool]=None, default_integration: typing.Optional["Integration"]=None, default_method_options: typing.Optional["MethodOptions"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            parent: The parent resource of this resource. You can either pass another ``Resource`` object or a ``RestApi`` object here.
            anyMethod: Adds an "ANY" method to this resource. If set to ``false``, you will have to explicitly add methods to this resource after it's created. Default: true
            defaultIntegration: An integration to use as a default for all methods created within this API unless an integration is specified. Default: - Inherited from parent.
            defaultMethodOptions: Method options to use as a default for all methods created within this API unless custom options are specified. Default: - Inherited from parent.

        Stability:
            experimental
        """
        props: ProxyResourceProps = {"parent": parent}

        if any_method is not None:
            props["anyMethod"] = any_method

        if default_integration is not None:
            props["defaultIntegration"] = default_integration

        if default_method_options is not None:
            props["defaultMethodOptions"] = default_method_options

        jsii.create(ProxyResource, self, [scope, id, props])

    @jsii.member(jsii_name="addMethod")
    def add_method(self, http_method: str, integration: typing.Optional["Integration"]=None, *, api_key_required: typing.Optional[bool]=None, authorization_type: typing.Optional["AuthorizationType"]=None, authorizer_id: typing.Optional[str]=None, method_responses: typing.Optional[typing.List["MethodResponse"]]=None, operation_name: typing.Optional[str]=None, request_parameters: typing.Optional[typing.Mapping[str,bool]]=None) -> "Method":
        """Defines a new method for this resource.

        Arguments:
            httpMethod: -
            integration: -
            options: -
            apiKeyRequired: Indicates whether the method requires clients to submit a valid API key. Default: false
            authorizationType: Method authorization. Default: None open access
            authorizerId: If ``authorizationType`` is ``Custom``, this specifies the ID of the method authorizer resource. NOTE: in the future this will be replaced with an ``IAuthorizer`` construct.
            methodResponses: The responses that can be sent to the client who calls the method. Default: None This property is not required, but if these are not supplied for a Lambda proxy integration, the Lambda function must return a value of the correct format, for the integration response to be correctly mapped to a response to the client.
            operationName: A friendly operation name for the method. For example, you can assign the OperationName of ListPets for the GET /pets method.
            requestParameters: The request parameters that API Gateway accepts. Specify request parameters as key-value pairs (string-to-Boolean mapping), with a source as the key and a Boolean as the value. The Boolean specifies whether a parameter is required. A source must match the format method.request.location.name, where the location is querystring, path, or header, and name is a valid, unique parameter name. Default: None

        Stability:
            experimental
        """
        options: MethodOptions = {}

        if api_key_required is not None:
            options["apiKeyRequired"] = api_key_required

        if authorization_type is not None:
            options["authorizationType"] = authorization_type

        if authorizer_id is not None:
            options["authorizerId"] = authorizer_id

        if method_responses is not None:
            options["methodResponses"] = method_responses

        if operation_name is not None:
            options["operationName"] = operation_name

        if request_parameters is not None:
            options["requestParameters"] = request_parameters

        return jsii.invoke(self, "addMethod", [http_method, integration, options])

    @property
    @jsii.member(jsii_name="anyMethod")
    def any_method(self) -> typing.Optional["Method"]:
        """If ``props.anyMethod`` is ``true``, this will be the reference to the 'ANY' method associated with this proxy resource.

        Stability:
            experimental
        """
        return jsii.get(self, "anyMethod")


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.ResourceOptions", jsii_struct_bases=[])
class ResourceOptions(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    defaultIntegration: "Integration"
    """An integration to use as a default for all methods created within this API unless an integration is specified.

    Default:
        - Inherited from parent.

    Stability:
        experimental
    """

    defaultMethodOptions: "MethodOptions"
    """Method options to use as a default for all methods created within this API unless custom options are specified.

    Default:
        - Inherited from parent.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.ApiKeyProps", jsii_struct_bases=[ResourceOptions])
class ApiKeyProps(ResourceOptions, jsii.compat.TypedDict, total=False):
    """ApiKey Properties.

    Stability:
        experimental
    """
    customerId: str
    """An AWS Marketplace customer identifier to use when integrating with the AWS SaaS Marketplace.

    Default:
        none

    Stability:
        experimental
    link:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html#cfn-apigateway-apikey-customerid
    """

    description: str
    """A description of the purpose of the API key.

    Default:
        none

    Stability:
        experimental
    link:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html#cfn-apigateway-apikey-description
    """

    enabled: bool
    """Indicates whether the API key can be used by clients.

    Default:
        true

    Stability:
        experimental
    link:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html#cfn-apigateway-apikey-enabled
    """

    generateDistinctId: bool
    """Specifies whether the key identifier is distinct from the created API key value.

    Default:
        false

    Stability:
        experimental
    link:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html#cfn-apigateway-apikey-generatedistinctid
    """

    name: str
    """A name for the API key.

    If you don't specify a name, AWS CloudFormation generates a unique physical ID and uses that ID for the API key name.

    Default:
        automically generated name

    Stability:
        experimental
    link:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html#cfn-apigateway-apikey-name
    """

    resources: typing.List["RestApi"]
    """A list of resources this api key is associated with.

    Default:
        none

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[ResourceOptions])
class _ProxyResourceProps(ResourceOptions, jsii.compat.TypedDict, total=False):
    anyMethod: bool
    """Adds an "ANY" method to this resource.

    If set to ``false``, you will have to explicitly
    add methods to this resource after it's created.

    Default:
        true

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.ProxyResourceProps", jsii_struct_bases=[_ProxyResourceProps])
class ProxyResourceProps(_ProxyResourceProps):
    """
    Stability:
        experimental
    """
    parent: "IResource"
    """The parent resource of this resource.

    You can either pass another
    ``Resource`` object or a ``RestApi`` object here.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.ResourceProps", jsii_struct_bases=[ResourceOptions])
class ResourceProps(ResourceOptions, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    parent: "IResource"
    """The parent resource of this resource.

    You can either pass another
    ``Resource`` object or a ``RestApi`` object here.

    Stability:
        experimental
    """

    pathPart: str
    """A path name for the resource.

    Stability:
        experimental
    """

@jsii.implements(IRestApi)
class RestApi(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.RestApi"):
    """Represents a REST API in Amazon API Gateway.

    Use ``addResource`` and ``addMethod`` to configure the API model.

    By default, the API will automatically be deployed and accessible from a
    public endpoint.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_key_source_type: typing.Optional["ApiKeySourceType"]=None, binary_media_types: typing.Optional[typing.List[str]]=None, clone_from: typing.Optional["IRestApi"]=None, cloud_watch_role: typing.Optional[bool]=None, deploy: typing.Optional[bool]=None, deploy_options: typing.Optional["StageOptions"]=None, description: typing.Optional[str]=None, endpoint_types: typing.Optional[typing.List["EndpointType"]]=None, fail_on_warnings: typing.Optional[bool]=None, minimum_compression_size: typing.Optional[jsii.Number]=None, parameters: typing.Optional[typing.Mapping[str,str]]=None, policy: typing.Optional[aws_cdk.aws_iam.PolicyDocument]=None, rest_api_name: typing.Optional[str]=None, retain_deployments: typing.Optional[bool]=None, default_integration: typing.Optional["Integration"]=None, default_method_options: typing.Optional["MethodOptions"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            apiKeySourceType: The source of the API key for metering requests according to a usage plan. Default: - Metering is disabled.
            binaryMediaTypes: The list of binary media mine-types that are supported by the RestApi resource, such as "image/png" or "application/octet-stream". Default: - RestApi supports only UTF-8-encoded text payloads.
            cloneFrom: The ID of the API Gateway RestApi resource that you want to clone. Default: - None.
            cloudWatchRole: Automatically configure an AWS CloudWatch role for API Gateway. Default: true
            deploy: Indicates if a Deployment should be automatically created for this API, and recreated when the API model (resources, methods) changes. Since API Gateway deployments are immutable, When this option is enabled (by default), an AWS::ApiGateway::Deployment resource will automatically created with a logical ID that hashes the API model (methods, resources and options). This means that when the model changes, the logical ID of this CloudFormation resource will change, and a new deployment will be created. If this is set, ``latestDeployment`` will refer to the ``Deployment`` object and ``deploymentStage`` will refer to a ``Stage`` that points to this deployment. To customize the stage options, use the ``deployStageOptions`` property. A CloudFormation Output will also be defined with the root URL endpoint of this REST API. Default: true
            deployOptions: Options for the API Gateway stage that will always point to the latest deployment when ``deploy`` is enabled. If ``deploy`` is disabled, this value cannot be set. Default: - Based on defaults of ``StageOptions``.
            description: A description of the purpose of this API Gateway RestApi resource. Default: - No description.
            endpointTypes: A list of the endpoint types of the API. Use this property when creating an API. Default: - No endpoint types.
            failOnWarnings: Indicates whether to roll back the resource if a warning occurs while API Gateway is creating the RestApi resource. Default: false
            minimumCompressionSize: A nullable integer that is used to enable compression (with non-negative between 0 and 10485760 (10M) bytes, inclusive) or disable compression (when undefined) on an API. When compression is enabled, compression or decompression is not applied on the payload if the payload size is smaller than this value. Setting it to zero allows compression for any payload size. Default: - Compression is disabled.
            parameters: Custom header parameters for the request. Default: - No parameters.
            policy: A policy document that contains the permissions for this RestApi. Default: - No policy.
            restApiName: A name for the API Gateway RestApi resource. Default: - ID of the RestApi construct.
            retainDeployments: Retains old deployment resources when the API changes. This allows manually reverting stages to point to old deployments via the AWS Console. Default: false
            defaultIntegration: An integration to use as a default for all methods created within this API unless an integration is specified. Default: - Inherited from parent.
            defaultMethodOptions: Method options to use as a default for all methods created within this API unless custom options are specified. Default: - Inherited from parent.

        Stability:
            experimental
        """
        props: RestApiProps = {}

        if api_key_source_type is not None:
            props["apiKeySourceType"] = api_key_source_type

        if binary_media_types is not None:
            props["binaryMediaTypes"] = binary_media_types

        if clone_from is not None:
            props["cloneFrom"] = clone_from

        if cloud_watch_role is not None:
            props["cloudWatchRole"] = cloud_watch_role

        if deploy is not None:
            props["deploy"] = deploy

        if deploy_options is not None:
            props["deployOptions"] = deploy_options

        if description is not None:
            props["description"] = description

        if endpoint_types is not None:
            props["endpointTypes"] = endpoint_types

        if fail_on_warnings is not None:
            props["failOnWarnings"] = fail_on_warnings

        if minimum_compression_size is not None:
            props["minimumCompressionSize"] = minimum_compression_size

        if parameters is not None:
            props["parameters"] = parameters

        if policy is not None:
            props["policy"] = policy

        if rest_api_name is not None:
            props["restApiName"] = rest_api_name

        if retain_deployments is not None:
            props["retainDeployments"] = retain_deployments

        if default_integration is not None:
            props["defaultIntegration"] = default_integration

        if default_method_options is not None:
            props["defaultMethodOptions"] = default_method_options

        jsii.create(RestApi, self, [scope, id, props])

    @jsii.member(jsii_name="fromRestApiId")
    @classmethod
    def from_rest_api_id(cls, scope: aws_cdk.cdk.Construct, id: str, rest_api_id: str) -> "IRestApi":
        """
        Arguments:
            scope: -
            id: -
            restApiId: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromRestApiId", [scope, id, rest_api_id])

    @jsii.member(jsii_name="addApiKey")
    def add_api_key(self, id: str) -> "IApiKey":
        """Add an ApiKey.

        Arguments:
            id: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addApiKey", [id])

    @jsii.member(jsii_name="addUsagePlan")
    def add_usage_plan(self, id: str, *, api_key: typing.Optional["IApiKey"]=None, api_stages: typing.Optional[typing.List["UsagePlanPerApiStage"]]=None, description: typing.Optional[str]=None, name: typing.Optional[str]=None, quota: typing.Optional["QuotaSettings"]=None, throttle: typing.Optional["ThrottleSettings"]=None) -> "UsagePlan":
        """Adds a usage plan.

        Arguments:
            id: -
            props: -
            apiKey: ApiKey to be associated with the usage plan. Default: none
            apiStages: API Stages to be associated which the usage plan. Default: none
            description: Represents usage plan purpose. Default: none
            name: Name for this usage plan. Default: none
            quota: Number of requests clients can make in a given time period. Default: none
            throttle: Overall throttle settings for the API. Default: none

        Stability:
            experimental
        """
        props: UsagePlanProps = {}

        if api_key is not None:
            props["apiKey"] = api_key

        if api_stages is not None:
            props["apiStages"] = api_stages

        if description is not None:
            props["description"] = description

        if name is not None:
            props["name"] = name

        if quota is not None:
            props["quota"] = quota

        if throttle is not None:
            props["throttle"] = throttle

        return jsii.invoke(self, "addUsagePlan", [id, props])

    @jsii.member(jsii_name="executeApiArn")
    def execute_api_arn(self, method: typing.Optional[str]=None, path: typing.Optional[str]=None, stage: typing.Optional[str]=None) -> str:
        """
        Arguments:
            method: The method (default ``*``).
            path: The resource path. Must start with '/' (default ``*``)
            stage: The stage (default ``*``).

        Default:
            "*" returns the execute API ARN for all methods/resources in
            this API.

        Returns:
            The "execute-api" ARN.

        Stability:
            experimental
        """
        return jsii.invoke(self, "executeApiArn", [method, path, stage])

    @jsii.member(jsii_name="urlForPath")
    def url_for_path(self, path: typing.Optional[str]=None) -> str:
        """Returns the URL for an HTTP path.

        Fails if ``deploymentStage`` is not set either by ``deploy`` or explicitly.

        Arguments:
            path: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "urlForPath", [path])

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[str]:
        """Performs validation of the REST API.

        Stability:
            experimental
        """
        return jsii.invoke(self, "validate", [])

    @property
    @jsii.member(jsii_name="restApiId")
    def rest_api_id(self) -> str:
        """The ID of this API Gateway RestApi.

        Stability:
            experimental
        """
        return jsii.get(self, "restApiId")

    @property
    @jsii.member(jsii_name="restApiRootResourceId")
    def rest_api_root_resource_id(self) -> str:
        """The resource ID of the root resource.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "restApiRootResourceId")

    @property
    @jsii.member(jsii_name="root")
    def root(self) -> "IResource":
        """Represents the root resource ("/") of this API. Use it to define the API model:.

        api.root.addMethod('ANY', redirectToHomePage); // "ANY /"
        api.root.addResource('friends').addMethod('GET', getFriendsHandler); // "GET /friends"

        Stability:
            experimental
        """
        return jsii.get(self, "root")

    @property
    @jsii.member(jsii_name="url")
    def url(self) -> str:
        """The deployed root URL of this REST API.

        Stability:
            experimental
        """
        return jsii.get(self, "url")

    @property
    @jsii.member(jsii_name="deploymentStage")
    def deployment_stage(self) -> typing.Optional["Stage"]:
        """API Gateway stage that points to the latest deployment (if defined).

        If ``deploy`` is disabled, you will need to explicitly assign this value in order to
        set up integrations.

        Stability:
            experimental
        """
        return jsii.get(self, "deploymentStage")

    @deployment_stage.setter
    def deployment_stage(self, value: typing.Optional["Stage"]):
        return jsii.set(self, "deploymentStage", value)

    @property
    @jsii.member(jsii_name="latestDeployment")
    def latest_deployment(self) -> typing.Optional["Deployment"]:
        """API Gateway deployment that represents the latest changes of the API. This resource will be automatically updated every time the REST API model changes. This will be undefined if ``deploy`` is false.

        Stability:
            experimental
        """
        return jsii.get(self, "latestDeployment")

    @latest_deployment.setter
    def latest_deployment(self, value: typing.Optional["Deployment"]):
        return jsii.set(self, "latestDeployment", value)


class LambdaRestApi(RestApi, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.LambdaRestApi"):
    """Defines an API Gateway REST API with AWS Lambda proxy integration.

    Use the ``proxyPath`` property to define a greedy proxy ("{proxy+}") and "ANY"
    method from the specified path. If not defined, you will need to explicity
    add resources and methods to the API.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, handler: aws_cdk.aws_lambda.IFunction, options: typing.Optional["RestApiProps"]=None, proxy: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            handler: The default Lambda function that handles all requests from this API. This handler will be used as a the default integration for all methods in this API, unless specified otherwise in ``addMethod``.
            options: Further customization of the REST API. Default: defaults
            proxy: If true, route all requests to the Lambda Function. If set to false, you will need to explicitly define the API model using ``addResource`` and ``addMethod`` (or ``addProxy``). Default: true

        Stability:
            experimental
        """
        props: LambdaRestApiProps = {"handler": handler}

        if options is not None:
            props["options"] = options

        if proxy is not None:
            props["proxy"] = proxy

        jsii.create(LambdaRestApi, self, [scope, id, props])


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.RestApiProps", jsii_struct_bases=[ResourceOptions])
class RestApiProps(ResourceOptions, jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    apiKeySourceType: "ApiKeySourceType"
    """The source of the API key for metering requests according to a usage plan.

    Default:
        - Metering is disabled.

    Stability:
        experimental
    """

    binaryMediaTypes: typing.List[str]
    """The list of binary media mine-types that are supported by the RestApi resource, such as "image/png" or "application/octet-stream".

    Default:
        - RestApi supports only UTF-8-encoded text payloads.

    Stability:
        experimental
    """

    cloneFrom: "IRestApi"
    """The ID of the API Gateway RestApi resource that you want to clone.

    Default:
        - None.

    Stability:
        experimental
    """

    cloudWatchRole: bool
    """Automatically configure an AWS CloudWatch role for API Gateway.

    Default:
        true

    Stability:
        experimental
    """

    deploy: bool
    """Indicates if a Deployment should be automatically created for this API, and recreated when the API model (resources, methods) changes.

    Since API Gateway deployments are immutable, When this option is enabled
    (by default), an AWS::ApiGateway::Deployment resource will automatically
    created with a logical ID that hashes the API model (methods, resources
    and options). This means that when the model changes, the logical ID of
    this CloudFormation resource will change, and a new deployment will be
    created.

    If this is set, ``latestDeployment`` will refer to the ``Deployment`` object
    and ``deploymentStage`` will refer to a ``Stage`` that points to this
    deployment. To customize the stage options, use the ``deployStageOptions``
    property.

    A CloudFormation Output will also be defined with the root URL endpoint
    of this REST API.

    Default:
        true

    Stability:
        experimental
    """

    deployOptions: "StageOptions"
    """Options for the API Gateway stage that will always point to the latest deployment when ``deploy`` is enabled.

    If ``deploy`` is disabled,
    this value cannot be set.

    Default:
        - Based on defaults of ``StageOptions``.

    Stability:
        experimental
    """

    description: str
    """A description of the purpose of this API Gateway RestApi resource.

    Default:
        - No description.

    Stability:
        experimental
    """

    endpointTypes: typing.List["EndpointType"]
    """A list of the endpoint types of the API.

    Use this property when creating
    an API.

    Default:
        - No endpoint types.

    Stability:
        experimental
    """

    failOnWarnings: bool
    """Indicates whether to roll back the resource if a warning occurs while API Gateway is creating the RestApi resource.

    Default:
        false

    Stability:
        experimental
    """

    minimumCompressionSize: jsii.Number
    """A nullable integer that is used to enable compression (with non-negative between 0 and 10485760 (10M) bytes, inclusive) or disable compression (when undefined) on an API.

    When compression is enabled, compression or
    decompression is not applied on the payload if the payload size is
    smaller than this value. Setting it to zero allows compression for any
    payload size.

    Default:
        - Compression is disabled.

    Stability:
        experimental
    """

    parameters: typing.Mapping[str,str]
    """Custom header parameters for the request.

    Default:
        - No parameters.

    See:
        https://docs.aws.amazon.com/cli/latest/reference/apigateway/import-rest-api.html
    Stability:
        experimental
    """

    policy: aws_cdk.aws_iam.PolicyDocument
    """A policy document that contains the permissions for this RestApi.

    Default:
        - No policy.

    Stability:
        experimental
    """

    restApiName: str
    """A name for the API Gateway RestApi resource.

    Default:
        - ID of the RestApi construct.

    Stability:
        experimental
    """

    retainDeployments: bool
    """Retains old deployment resources when the API changes.

    This allows
    manually reverting stages to point to old deployments via the AWS
    Console.

    Default:
        false

    Stability:
        experimental
    """

class Stage(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.Stage"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, deployment: "Deployment", cache_cluster_enabled: typing.Optional[bool]=None, cache_cluster_size: typing.Optional[str]=None, client_certificate_id: typing.Optional[str]=None, description: typing.Optional[str]=None, documentation_version: typing.Optional[str]=None, method_options: typing.Optional[typing.Mapping[str,"MethodDeploymentOptions"]]=None, stage_name: typing.Optional[str]=None, tracing_enabled: typing.Optional[bool]=None, variables: typing.Optional[typing.Mapping[str,str]]=None, cache_data_encrypted: typing.Optional[bool]=None, cache_ttl_seconds: typing.Optional[jsii.Number]=None, caching_enabled: typing.Optional[bool]=None, data_trace_enabled: typing.Optional[bool]=None, logging_level: typing.Optional["MethodLoggingLevel"]=None, metrics_enabled: typing.Optional[bool]=None, throttling_burst_limit: typing.Optional[jsii.Number]=None, throttling_rate_limit: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            deployment: The deployment that this stage points to [disable-awslint:ref-via-interface].
            cacheClusterEnabled: Indicates whether cache clustering is enabled for the stage. Default: - Disabled for the stage.
            cacheClusterSize: The stage's cache cluster size. Default: 0.5
            clientCertificateId: The identifier of the client certificate that API Gateway uses to call your integration endpoints in the stage. Default: - None.
            description: A description of the purpose of the stage. Default: - No description.
            documentationVersion: The version identifier of the API documentation snapshot. Default: - No documentation version.
            methodOptions: Method deployment options for specific resources/methods. These will override common options defined in ``StageOptions#methodOptions``. Default: - Common options will be used.
            stageName: The name of the stage, which API Gateway uses as the first path segment in the invoked Uniform Resource Identifier (URI). Default: - "prod"
            tracingEnabled: Specifies whether Amazon X-Ray tracing is enabled for this method. Default: false
            variables: A map that defines the stage variables. Variable names must consist of alphanumeric characters, and the values must match the following regular expression: [A-Za-z0-9-._~:/?#&=,]+. Default: - No stage variables.
            cacheDataEncrypted: Indicates whether the cached responses are encrypted. Default: false
            cacheTtlSeconds: Specifies the time to live (TTL), in seconds, for cached responses. The higher the TTL, the longer the response will be cached. Default: 300
            cachingEnabled: Specifies whether responses should be cached and returned for requests. A cache cluster must be enabled on the stage for responses to be cached. Default: - Caching is Disabled.
            dataTraceEnabled: Specifies whether data trace logging is enabled for this method, which effects the log entries pushed to Amazon CloudWatch Logs. Default: false
            loggingLevel: Specifies the logging level for this method, which effects the log entries pushed to Amazon CloudWatch Logs. Default: - Off
            metricsEnabled: Specifies whether Amazon CloudWatch metrics are enabled for this method. Default: false
            throttlingBurstLimit: Specifies the throttling burst limit. The total rate of all requests in your AWS account is limited to 5,000 requests. Default: - No additional restriction.
            throttlingRateLimit: Specifies the throttling rate limit. The total rate of all requests in your AWS account is limited to 10,000 requests per second (rps). Default: - No additional restriction.

        Stability:
            experimental
        """
        props: StageProps = {"deployment": deployment}

        if cache_cluster_enabled is not None:
            props["cacheClusterEnabled"] = cache_cluster_enabled

        if cache_cluster_size is not None:
            props["cacheClusterSize"] = cache_cluster_size

        if client_certificate_id is not None:
            props["clientCertificateId"] = client_certificate_id

        if description is not None:
            props["description"] = description

        if documentation_version is not None:
            props["documentationVersion"] = documentation_version

        if method_options is not None:
            props["methodOptions"] = method_options

        if stage_name is not None:
            props["stageName"] = stage_name

        if tracing_enabled is not None:
            props["tracingEnabled"] = tracing_enabled

        if variables is not None:
            props["variables"] = variables

        if cache_data_encrypted is not None:
            props["cacheDataEncrypted"] = cache_data_encrypted

        if cache_ttl_seconds is not None:
            props["cacheTtlSeconds"] = cache_ttl_seconds

        if caching_enabled is not None:
            props["cachingEnabled"] = caching_enabled

        if data_trace_enabled is not None:
            props["dataTraceEnabled"] = data_trace_enabled

        if logging_level is not None:
            props["loggingLevel"] = logging_level

        if metrics_enabled is not None:
            props["metricsEnabled"] = metrics_enabled

        if throttling_burst_limit is not None:
            props["throttlingBurstLimit"] = throttling_burst_limit

        if throttling_rate_limit is not None:
            props["throttlingRateLimit"] = throttling_rate_limit

        jsii.create(Stage, self, [scope, id, props])

    @jsii.member(jsii_name="urlForPath")
    def url_for_path(self, path: typing.Optional[str]=None) -> str:
        """Returns the invoke URL for a certain path.

        Arguments:
            path: The resource path.

        Stability:
            experimental
        """
        return jsii.invoke(self, "urlForPath", [path])

    @property
    @jsii.member(jsii_name="restApi")
    def rest_api(self) -> "IRestApi":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "restApi")

    @property
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "stageName")


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.StageOptions", jsii_struct_bases=[MethodDeploymentOptions])
class StageOptions(MethodDeploymentOptions, jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    cacheClusterEnabled: bool
    """Indicates whether cache clustering is enabled for the stage.

    Default:
        - Disabled for the stage.

    Stability:
        experimental
    """

    cacheClusterSize: str
    """The stage's cache cluster size.

    Default:
        0.5

    Stability:
        experimental
    """

    clientCertificateId: str
    """The identifier of the client certificate that API Gateway uses to call your integration endpoints in the stage.

    Default:
        - None.

    Stability:
        experimental
    """

    description: str
    """A description of the purpose of the stage.

    Default:
        - No description.

    Stability:
        experimental
    """

    documentationVersion: str
    """The version identifier of the API documentation snapshot.

    Default:
        - No documentation version.

    Stability:
        experimental
    """

    methodOptions: typing.Mapping[str,"MethodDeploymentOptions"]
    """Method deployment options for specific resources/methods.

    These will
    override common options defined in ``StageOptions#methodOptions``.

    Default:
        - Common options will be used.

    Stability:
        experimental
    """

    stageName: str
    """The name of the stage, which API Gateway uses as the first path segment in the invoked Uniform Resource Identifier (URI).

    Default:
        - "prod"

    Stability:
        experimental
    """

    tracingEnabled: bool
    """Specifies whether Amazon X-Ray tracing is enabled for this method.

    Default:
        false

    Stability:
        experimental
    """

    variables: typing.Mapping[str,str]
    """A map that defines the stage variables.

    Variable names must consist of
    alphanumeric characters, and the values must match the following regular
    expression: [A-Za-z0-9-._~:/?#&=,]+.

    Default:
        - No stage variables.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.StageProps", jsii_struct_bases=[StageOptions])
class StageProps(StageOptions, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    deployment: "Deployment"
    """The deployment that this stage points to [disable-awslint:ref-via-interface].

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.ThrottleSettings", jsii_struct_bases=[])
class ThrottleSettings(jsii.compat.TypedDict, total=False):
    """Container for defining throttling parameters to API stages or methods.

    Stability:
        experimental
    link:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html
    """
    burstLimit: jsii.Number
    """The maximum API request rate limit over a time ranging from one to a few seconds.

    Default:
        none

    Stability:
        experimental
    """

    rateLimit: jsii.Number
    """The API request steady-state rate limit (average requests per second over an extended period of time).

    Default:
        none

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.ThrottlingPerMethod", jsii_struct_bases=[])
class ThrottlingPerMethod(jsii.compat.TypedDict):
    """Represents per-method throttling for a resource.

    Stability:
        experimental
    """
    method: "Method"
    """[disable-awslint:ref-via-interface] The method for which you specify the throttling settings.

    Default:
        none

    Stability:
        experimental
    """

    throttle: "ThrottleSettings"
    """Specifies the overall request rate (average requests per second) and burst capacity.

    Default:
        none

    Stability:
        experimental
    """

class UsagePlan(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.UsagePlan"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, api_key: typing.Optional["IApiKey"]=None, api_stages: typing.Optional[typing.List["UsagePlanPerApiStage"]]=None, description: typing.Optional[str]=None, name: typing.Optional[str]=None, quota: typing.Optional["QuotaSettings"]=None, throttle: typing.Optional["ThrottleSettings"]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            apiKey: ApiKey to be associated with the usage plan. Default: none
            apiStages: API Stages to be associated which the usage plan. Default: none
            description: Represents usage plan purpose. Default: none
            name: Name for this usage plan. Default: none
            quota: Number of requests clients can make in a given time period. Default: none
            throttle: Overall throttle settings for the API. Default: none

        Stability:
            experimental
        """
        props: UsagePlanProps = {}

        if api_key is not None:
            props["apiKey"] = api_key

        if api_stages is not None:
            props["apiStages"] = api_stages

        if description is not None:
            props["description"] = description

        if name is not None:
            props["name"] = name

        if quota is not None:
            props["quota"] = quota

        if throttle is not None:
            props["throttle"] = throttle

        jsii.create(UsagePlan, self, [scope, id, props])

    @jsii.member(jsii_name="addApiKey")
    def add_api_key(self, api_key: "IApiKey") -> None:
        """Adds an ApiKey.

        Arguments:
            apiKey: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addApiKey", [api_key])

    @jsii.member(jsii_name="addApiStage")
    def add_api_stage(self, *, api: typing.Optional["IRestApi"]=None, stage: typing.Optional["Stage"]=None, throttle: typing.Optional[typing.List["ThrottlingPerMethod"]]=None) -> None:
        """Adds an apiStage.

        Arguments:
            apiStage: -
            api: Default: none
            stage: [disable-awslint:ref-via-interface]. Default: none
            throttle: Default: none

        Stability:
            experimental
        """
        api_stage: UsagePlanPerApiStage = {}

        if api is not None:
            api_stage["api"] = api

        if stage is not None:
            api_stage["stage"] = stage

        if throttle is not None:
            api_stage["throttle"] = throttle

        return jsii.invoke(self, "addApiStage", [api_stage])

    @property
    @jsii.member(jsii_name="usagePlanId")
    def usage_plan_id(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "usagePlanId")


@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.UsagePlanPerApiStage", jsii_struct_bases=[])
class UsagePlanPerApiStage(jsii.compat.TypedDict, total=False):
    """Represents the API stages that a usage plan applies to.

    Stability:
        experimental
    """
    api: "IRestApi"
    """
    Default:
        none

    Stability:
        experimental
    """

    stage: "Stage"
    """[disable-awslint:ref-via-interface].

    Default:
        none

    Stability:
        experimental
    """

    throttle: typing.List["ThrottlingPerMethod"]
    """
    Default:
        none

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.UsagePlanProps", jsii_struct_bases=[])
class UsagePlanProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    apiKey: "IApiKey"
    """ApiKey to be associated with the usage plan.

    Default:
        none

    Stability:
        experimental
    """

    apiStages: typing.List["UsagePlanPerApiStage"]
    """API Stages to be associated which the usage plan.

    Default:
        none

    Stability:
        experimental
    """

    description: str
    """Represents usage plan purpose.

    Default:
        none

    Stability:
        experimental
    """

    name: str
    """Name for this usage plan.

    Default:
        none

    Stability:
        experimental
    """

    quota: "QuotaSettings"
    """Number of requests clients can make in a given time period.

    Default:
        none

    Stability:
        experimental
    """

    throttle: "ThrottleSettings"
    """Overall throttle settings for the API.

    Default:
        none

    Stability:
        experimental
    """

class VpcLink(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-apigateway.VpcLink"):
    """Define a new VPC Link Specifies an API Gateway VPC link for a RestApi to access resources in an Amazon Virtual Private Cloud (VPC).

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, targets: typing.List[aws_cdk.aws_elasticloadbalancingv2.INetworkLoadBalancer], description: typing.Optional[str]=None, name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            targets: The network load balancers of the VPC targeted by the VPC link. The network load balancers must be owned by the same AWS account of the API owner.
            description: The description of the VPC link. Default: no description
            name: The name used to label and identify the VPC link. Default: automatically generated name

        Stability:
            experimental
        """
        props: VpcLinkProps = {"targets": targets}

        if description is not None:
            props["description"] = description

        if name is not None:
            props["name"] = name

        jsii.create(VpcLink, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="vpcLinkId")
    def vpc_link_id(self) -> str:
        """Physical ID of the VpcLink resource.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "vpcLinkId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _VpcLinkProps(jsii.compat.TypedDict, total=False):
    description: str
    """The description of the VPC link.

    Default:
        no description

    Stability:
        experimental
    """
    name: str
    """The name used to label and identify the VPC link.

    Default:
        automatically generated name

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-apigateway.VpcLinkProps", jsii_struct_bases=[_VpcLinkProps])
class VpcLinkProps(_VpcLinkProps):
    """Properties for a VpcLink.

    Stability:
        experimental
    """
    targets: typing.List[aws_cdk.aws_elasticloadbalancingv2.INetworkLoadBalancer]
    """The network load balancers of the VPC targeted by the VPC link. The network load balancers must be owned by the same AWS account of the API owner.

    Stability:
        experimental
    """

__all__ = ["ApiKey", "ApiKeyAttributes", "ApiKeyProps", "ApiKeySourceType", "AuthorizationType", "AwsIntegration", "AwsIntegrationProps", "CfnAccount", "CfnAccountProps", "CfnApiKey", "CfnApiKeyProps", "CfnApiMappingV2", "CfnApiMappingV2Props", "CfnApiV2", "CfnApiV2Props", "CfnAuthorizer", "CfnAuthorizerProps", "CfnAuthorizerV2", "CfnAuthorizerV2Props", "CfnBasePathMapping", "CfnBasePathMappingProps", "CfnClientCertificate", "CfnClientCertificateProps", "CfnDeployment", "CfnDeploymentProps", "CfnDeploymentV2", "CfnDeploymentV2Props", "CfnDocumentationPart", "CfnDocumentationPartProps", "CfnDocumentationVersion", "CfnDocumentationVersionProps", "CfnDomainName", "CfnDomainNameProps", "CfnDomainNameV2", "CfnDomainNameV2Props", "CfnGatewayResponse", "CfnGatewayResponseProps", "CfnIntegrationResponseV2", "CfnIntegrationResponseV2Props", "CfnIntegrationV2", "CfnIntegrationV2Props", "CfnMethod", "CfnMethodProps", "CfnModel", "CfnModelProps", "CfnModelV2", "CfnModelV2Props", "CfnRequestValidator", "CfnRequestValidatorProps", "CfnResource", "CfnResourceProps", "CfnRestApi", "CfnRestApiProps", "CfnRouteResponseV2", "CfnRouteResponseV2Props", "CfnRouteV2", "CfnRouteV2Props", "CfnStage", "CfnStageProps", "CfnStageV2", "CfnStageV2Props", "CfnUsagePlan", "CfnUsagePlanKey", "CfnUsagePlanKeyProps", "CfnUsagePlanProps", "CfnVpcLink", "CfnVpcLinkProps", "ConnectionType", "ContentHandling", "Deployment", "DeploymentProps", "EmptyModel", "EndpointType", "ErrorModel", "HttpIntegration", "HttpIntegrationProps", "IApiKey", "IModel", "IResource", "IRestApi", "Integration", "IntegrationOptions", "IntegrationProps", "IntegrationResponse", "IntegrationType", "LambdaIntegration", "LambdaIntegrationOptions", "LambdaRestApi", "LambdaRestApiProps", "Method", "MethodDeploymentOptions", "MethodLoggingLevel", "MethodOptions", "MethodProps", "MethodResponse", "MockIntegration", "PassthroughBehavior", "Period", "ProxyResource", "ProxyResourceProps", "QuotaSettings", "Resource", "ResourceBase", "ResourceOptions", "ResourceProps", "RestApi", "RestApiProps", "Stage", "StageOptions", "StageProps", "ThrottleSettings", "ThrottlingPerMethod", "UsagePlan", "UsagePlanPerApiStage", "UsagePlanProps", "VpcLink", "VpcLinkProps", "__jsii_assembly__"]

publication.publish()
