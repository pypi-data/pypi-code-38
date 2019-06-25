import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-appsync", "0.36.0", __name__, "aws-appsync@0.36.0.jsii.tgz")
class CfnApiKey(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync.CfnApiKey"):
    """A CloudFormation ``AWS::AppSync::ApiKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html
    Stability:
        stable
    cloudformationResource:
        AWS::AppSync::ApiKey
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_id: str, description: typing.Optional[str]=None, expires: typing.Optional[jsii.Number]=None) -> None:
        """Create a new ``AWS::AppSync::ApiKey``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            api_id: ``AWS::AppSync::ApiKey.ApiId``.
            description: ``AWS::AppSync::ApiKey.Description``.
            expires: ``AWS::AppSync::ApiKey.Expires``.

        Stability:
            experimental
        """
        props: CfnApiKeyProps = {"apiId": api_id}

        if description is not None:
            props["description"] = description

        if expires is not None:
            props["expires"] = expires

        jsii.create(CfnApiKey, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrApiKey")
    def attr_api_key(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            ApiKey
        """
        return jsii.get(self, "attrApiKey")

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> str:
        """``AWS::AppSync::ApiKey.ApiId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html#cfn-appsync-apikey-apiid
        Stability:
            stable
        """
        return jsii.get(self, "apiId")

    @api_id.setter
    def api_id(self, value: str):
        return jsii.set(self, "apiId", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::AppSync::ApiKey.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html#cfn-appsync-apikey-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="expires")
    def expires(self) -> typing.Optional[jsii.Number]:
        """``AWS::AppSync::ApiKey.Expires``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html#cfn-appsync-apikey-expires
        Stability:
            stable
        """
        return jsii.get(self, "expires")

    @expires.setter
    def expires(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "expires", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnApiKeyProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::AppSync::ApiKey.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html#cfn-appsync-apikey-description
    Stability:
        stable
    """
    expires: jsii.Number
    """``AWS::AppSync::ApiKey.Expires``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html#cfn-appsync-apikey-expires
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnApiKeyProps", jsii_struct_bases=[_CfnApiKeyProps])
class CfnApiKeyProps(_CfnApiKeyProps):
    """Properties for defining a ``AWS::AppSync::ApiKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html
    Stability:
        stable
    """
    apiId: str
    """``AWS::AppSync::ApiKey.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-apikey.html#cfn-appsync-apikey-apiid
    Stability:
        stable
    """

class CfnDataSource(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync.CfnDataSource"):
    """A CloudFormation ``AWS::AppSync::DataSource``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html
    Stability:
        stable
    cloudformationResource:
        AWS::AppSync::DataSource
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_id: str, name: str, type: str, description: typing.Optional[str]=None, dynamo_db_config: typing.Optional[typing.Union[typing.Optional["DynamoDBConfigProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, elasticsearch_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ElasticsearchConfigProperty"]]]=None, http_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["HttpConfigProperty"]]]=None, lambda_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LambdaConfigProperty"]]]=None, relational_database_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RelationalDatabaseConfigProperty"]]]=None, service_role_arn: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::AppSync::DataSource``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            api_id: ``AWS::AppSync::DataSource.ApiId``.
            name: ``AWS::AppSync::DataSource.Name``.
            type: ``AWS::AppSync::DataSource.Type``.
            description: ``AWS::AppSync::DataSource.Description``.
            dynamo_db_config: ``AWS::AppSync::DataSource.DynamoDBConfig``.
            elasticsearch_config: ``AWS::AppSync::DataSource.ElasticsearchConfig``.
            http_config: ``AWS::AppSync::DataSource.HttpConfig``.
            lambda_config: ``AWS::AppSync::DataSource.LambdaConfig``.
            relational_database_config: ``AWS::AppSync::DataSource.RelationalDatabaseConfig``.
            service_role_arn: ``AWS::AppSync::DataSource.ServiceRoleArn``.

        Stability:
            experimental
        """
        props: CfnDataSourceProps = {"apiId": api_id, "name": name, "type": type}

        if description is not None:
            props["description"] = description

        if dynamo_db_config is not None:
            props["dynamoDbConfig"] = dynamo_db_config

        if elasticsearch_config is not None:
            props["elasticsearchConfig"] = elasticsearch_config

        if http_config is not None:
            props["httpConfig"] = http_config

        if lambda_config is not None:
            props["lambdaConfig"] = lambda_config

        if relational_database_config is not None:
            props["relationalDatabaseConfig"] = relational_database_config

        if service_role_arn is not None:
            props["serviceRoleArn"] = service_role_arn

        jsii.create(CfnDataSource, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrDataSourceArn")
    def attr_data_source_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            DataSourceArn
        """
        return jsii.get(self, "attrDataSourceArn")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> str:
        """``AWS::AppSync::DataSource.ApiId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-apiid
        Stability:
            stable
        """
        return jsii.get(self, "apiId")

    @api_id.setter
    def api_id(self, value: str):
        return jsii.set(self, "apiId", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::AppSync::DataSource.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """``AWS::AppSync::DataSource.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-type
        Stability:
            stable
        """
        return jsii.get(self, "type")

    @type.setter
    def type(self, value: str):
        return jsii.set(self, "type", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::AppSync::DataSource.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="dynamoDbConfig")
    def dynamo_db_config(self) -> typing.Optional[typing.Union[typing.Optional["DynamoDBConfigProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::AppSync::DataSource.DynamoDBConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-dynamodbconfig
        Stability:
            stable
        """
        return jsii.get(self, "dynamoDbConfig")

    @dynamo_db_config.setter
    def dynamo_db_config(self, value: typing.Optional[typing.Union[typing.Optional["DynamoDBConfigProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "dynamoDbConfig", value)

    @property
    @jsii.member(jsii_name="elasticsearchConfig")
    def elasticsearch_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ElasticsearchConfigProperty"]]]:
        """``AWS::AppSync::DataSource.ElasticsearchConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-elasticsearchconfig
        Stability:
            stable
        """
        return jsii.get(self, "elasticsearchConfig")

    @elasticsearch_config.setter
    def elasticsearch_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ElasticsearchConfigProperty"]]]):
        return jsii.set(self, "elasticsearchConfig", value)

    @property
    @jsii.member(jsii_name="httpConfig")
    def http_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["HttpConfigProperty"]]]:
        """``AWS::AppSync::DataSource.HttpConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-httpconfig
        Stability:
            stable
        """
        return jsii.get(self, "httpConfig")

    @http_config.setter
    def http_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["HttpConfigProperty"]]]):
        return jsii.set(self, "httpConfig", value)

    @property
    @jsii.member(jsii_name="lambdaConfig")
    def lambda_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LambdaConfigProperty"]]]:
        """``AWS::AppSync::DataSource.LambdaConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-lambdaconfig
        Stability:
            stable
        """
        return jsii.get(self, "lambdaConfig")

    @lambda_config.setter
    def lambda_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LambdaConfigProperty"]]]):
        return jsii.set(self, "lambdaConfig", value)

    @property
    @jsii.member(jsii_name="relationalDatabaseConfig")
    def relational_database_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RelationalDatabaseConfigProperty"]]]:
        """``AWS::AppSync::DataSource.RelationalDatabaseConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-relationaldatabaseconfig
        Stability:
            stable
        """
        return jsii.get(self, "relationalDatabaseConfig")

    @relational_database_config.setter
    def relational_database_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RelationalDatabaseConfigProperty"]]]):
        return jsii.set(self, "relationalDatabaseConfig", value)

    @property
    @jsii.member(jsii_name="serviceRoleArn")
    def service_role_arn(self) -> typing.Optional[str]:
        """``AWS::AppSync::DataSource.ServiceRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-servicerolearn
        Stability:
            stable
        """
        return jsii.get(self, "serviceRoleArn")

    @service_role_arn.setter
    def service_role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "serviceRoleArn", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _AuthorizationConfigProperty(jsii.compat.TypedDict, total=False):
        awsIamConfig: typing.Union[aws_cdk.core.IResolvable, "CfnDataSource.AwsIamConfigProperty"]
        """``CfnDataSource.AuthorizationConfigProperty.AwsIamConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-authorizationconfig.html#cfn-appsync-datasource-authorizationconfig-awsiamconfig
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.AuthorizationConfigProperty", jsii_struct_bases=[_AuthorizationConfigProperty])
    class AuthorizationConfigProperty(_AuthorizationConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-authorizationconfig.html
        Stability:
            stable
        """
        authorizationType: str
        """``CfnDataSource.AuthorizationConfigProperty.AuthorizationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-authorizationconfig.html#cfn-appsync-datasource-authorizationconfig-authorizationtype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.AwsIamConfigProperty", jsii_struct_bases=[])
    class AwsIamConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-awsiamconfig.html
        Stability:
            stable
        """
        signingRegion: str
        """``CfnDataSource.AwsIamConfigProperty.SigningRegion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-awsiamconfig.html#cfn-appsync-datasource-awsiamconfig-signingregion
        Stability:
            stable
        """

        signingServiceName: str
        """``CfnDataSource.AwsIamConfigProperty.SigningServiceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-awsiamconfig.html#cfn-appsync-datasource-awsiamconfig-signingservicename
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DynamoDBConfigProperty(jsii.compat.TypedDict, total=False):
        useCallerCredentials: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDataSource.DynamoDBConfigProperty.UseCallerCredentials``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-dynamodbconfig.html#cfn-appsync-datasource-dynamodbconfig-usecallercredentials
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.DynamoDBConfigProperty", jsii_struct_bases=[_DynamoDBConfigProperty])
    class DynamoDBConfigProperty(_DynamoDBConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-dynamodbconfig.html
        Stability:
            stable
        """
        awsRegion: str
        """``CfnDataSource.DynamoDBConfigProperty.AwsRegion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-dynamodbconfig.html#cfn-appsync-datasource-dynamodbconfig-awsregion
        Stability:
            stable
        """

        tableName: str
        """``CfnDataSource.DynamoDBConfigProperty.TableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-dynamodbconfig.html#cfn-appsync-datasource-dynamodbconfig-tablename
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.ElasticsearchConfigProperty", jsii_struct_bases=[])
    class ElasticsearchConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-elasticsearchconfig.html
        Stability:
            stable
        """
        awsRegion: str
        """``CfnDataSource.ElasticsearchConfigProperty.AwsRegion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-elasticsearchconfig.html#cfn-appsync-datasource-elasticsearchconfig-awsregion
        Stability:
            stable
        """

        endpoint: str
        """``CfnDataSource.ElasticsearchConfigProperty.Endpoint``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-elasticsearchconfig.html#cfn-appsync-datasource-elasticsearchconfig-endpoint
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _HttpConfigProperty(jsii.compat.TypedDict, total=False):
        authorizationConfig: typing.Union[aws_cdk.core.IResolvable, "CfnDataSource.AuthorizationConfigProperty"]
        """``CfnDataSource.HttpConfigProperty.AuthorizationConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-httpconfig.html#cfn-appsync-datasource-httpconfig-authorizationconfig
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.HttpConfigProperty", jsii_struct_bases=[_HttpConfigProperty])
    class HttpConfigProperty(_HttpConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-httpconfig.html
        Stability:
            stable
        """
        endpoint: str
        """``CfnDataSource.HttpConfigProperty.Endpoint``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-httpconfig.html#cfn-appsync-datasource-httpconfig-endpoint
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.LambdaConfigProperty", jsii_struct_bases=[])
    class LambdaConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-lambdaconfig.html
        Stability:
            stable
        """
        lambdaFunctionArn: str
        """``CfnDataSource.LambdaConfigProperty.LambdaFunctionArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-lambdaconfig.html#cfn-appsync-datasource-lambdaconfig-lambdafunctionarn
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _RdsHttpEndpointConfigProperty(jsii.compat.TypedDict, total=False):
        databaseName: str
        """``CfnDataSource.RdsHttpEndpointConfigProperty.DatabaseName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-rdshttpendpointconfig.html#cfn-appsync-datasource-rdshttpendpointconfig-databasename
        Stability:
            stable
        """
        schema: str
        """``CfnDataSource.RdsHttpEndpointConfigProperty.Schema``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-rdshttpendpointconfig.html#cfn-appsync-datasource-rdshttpendpointconfig-schema
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.RdsHttpEndpointConfigProperty", jsii_struct_bases=[_RdsHttpEndpointConfigProperty])
    class RdsHttpEndpointConfigProperty(_RdsHttpEndpointConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-rdshttpendpointconfig.html
        Stability:
            stable
        """
        awsRegion: str
        """``CfnDataSource.RdsHttpEndpointConfigProperty.AwsRegion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-rdshttpendpointconfig.html#cfn-appsync-datasource-rdshttpendpointconfig-awsregion
        Stability:
            stable
        """

        awsSecretStoreArn: str
        """``CfnDataSource.RdsHttpEndpointConfigProperty.AwsSecretStoreArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-rdshttpendpointconfig.html#cfn-appsync-datasource-rdshttpendpointconfig-awssecretstorearn
        Stability:
            stable
        """

        dbClusterIdentifier: str
        """``CfnDataSource.RdsHttpEndpointConfigProperty.DbClusterIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-rdshttpendpointconfig.html#cfn-appsync-datasource-rdshttpendpointconfig-dbclusteridentifier
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _RelationalDatabaseConfigProperty(jsii.compat.TypedDict, total=False):
        rdsHttpEndpointConfig: typing.Union[aws_cdk.core.IResolvable, "CfnDataSource.RdsHttpEndpointConfigProperty"]
        """``CfnDataSource.RelationalDatabaseConfigProperty.RdsHttpEndpointConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-relationaldatabaseconfig.html#cfn-appsync-datasource-relationaldatabaseconfig-rdshttpendpointconfig
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSource.RelationalDatabaseConfigProperty", jsii_struct_bases=[_RelationalDatabaseConfigProperty])
    class RelationalDatabaseConfigProperty(_RelationalDatabaseConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-relationaldatabaseconfig.html
        Stability:
            stable
        """
        relationalDatabaseSourceType: str
        """``CfnDataSource.RelationalDatabaseConfigProperty.RelationalDatabaseSourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-datasource-relationaldatabaseconfig.html#cfn-appsync-datasource-relationaldatabaseconfig-relationaldatabasesourcetype
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDataSourceProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::AppSync::DataSource.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-description
    Stability:
        stable
    """
    dynamoDbConfig: typing.Union["CfnDataSource.DynamoDBConfigProperty", aws_cdk.core.IResolvable]
    """``AWS::AppSync::DataSource.DynamoDBConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-dynamodbconfig
    Stability:
        stable
    """
    elasticsearchConfig: typing.Union[aws_cdk.core.IResolvable, "CfnDataSource.ElasticsearchConfigProperty"]
    """``AWS::AppSync::DataSource.ElasticsearchConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-elasticsearchconfig
    Stability:
        stable
    """
    httpConfig: typing.Union[aws_cdk.core.IResolvable, "CfnDataSource.HttpConfigProperty"]
    """``AWS::AppSync::DataSource.HttpConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-httpconfig
    Stability:
        stable
    """
    lambdaConfig: typing.Union[aws_cdk.core.IResolvable, "CfnDataSource.LambdaConfigProperty"]
    """``AWS::AppSync::DataSource.LambdaConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-lambdaconfig
    Stability:
        stable
    """
    relationalDatabaseConfig: typing.Union[aws_cdk.core.IResolvable, "CfnDataSource.RelationalDatabaseConfigProperty"]
    """``AWS::AppSync::DataSource.RelationalDatabaseConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-relationaldatabaseconfig
    Stability:
        stable
    """
    serviceRoleArn: str
    """``AWS::AppSync::DataSource.ServiceRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-servicerolearn
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnDataSourceProps", jsii_struct_bases=[_CfnDataSourceProps])
class CfnDataSourceProps(_CfnDataSourceProps):
    """Properties for defining a ``AWS::AppSync::DataSource``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html
    Stability:
        stable
    """
    apiId: str
    """``AWS::AppSync::DataSource.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-apiid
    Stability:
        stable
    """

    name: str
    """``AWS::AppSync::DataSource.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-name
    Stability:
        stable
    """

    type: str
    """``AWS::AppSync::DataSource.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-datasource.html#cfn-appsync-datasource-type
    Stability:
        stable
    """

class CfnFunctionConfiguration(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync.CfnFunctionConfiguration"):
    """A CloudFormation ``AWS::AppSync::FunctionConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html
    Stability:
        stable
    cloudformationResource:
        AWS::AppSync::FunctionConfiguration
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_id: str, data_source_name: str, function_version: str, name: str, description: typing.Optional[str]=None, request_mapping_template: typing.Optional[str]=None, request_mapping_template_s3_location: typing.Optional[str]=None, response_mapping_template: typing.Optional[str]=None, response_mapping_template_s3_location: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::AppSync::FunctionConfiguration``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            api_id: ``AWS::AppSync::FunctionConfiguration.ApiId``.
            data_source_name: ``AWS::AppSync::FunctionConfiguration.DataSourceName``.
            function_version: ``AWS::AppSync::FunctionConfiguration.FunctionVersion``.
            name: ``AWS::AppSync::FunctionConfiguration.Name``.
            description: ``AWS::AppSync::FunctionConfiguration.Description``.
            request_mapping_template: ``AWS::AppSync::FunctionConfiguration.RequestMappingTemplate``.
            request_mapping_template_s3_location: ``AWS::AppSync::FunctionConfiguration.RequestMappingTemplateS3Location``.
            response_mapping_template: ``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplate``.
            response_mapping_template_s3_location: ``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplateS3Location``.

        Stability:
            experimental
        """
        props: CfnFunctionConfigurationProps = {"apiId": api_id, "dataSourceName": data_source_name, "functionVersion": function_version, "name": name}

        if description is not None:
            props["description"] = description

        if request_mapping_template is not None:
            props["requestMappingTemplate"] = request_mapping_template

        if request_mapping_template_s3_location is not None:
            props["requestMappingTemplateS3Location"] = request_mapping_template_s3_location

        if response_mapping_template is not None:
            props["responseMappingTemplate"] = response_mapping_template

        if response_mapping_template_s3_location is not None:
            props["responseMappingTemplateS3Location"] = response_mapping_template_s3_location

        jsii.create(CfnFunctionConfiguration, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrDataSourceName")
    def attr_data_source_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            DataSourceName
        """
        return jsii.get(self, "attrDataSourceName")

    @property
    @jsii.member(jsii_name="attrFunctionArn")
    def attr_function_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            FunctionArn
        """
        return jsii.get(self, "attrFunctionArn")

    @property
    @jsii.member(jsii_name="attrFunctionId")
    def attr_function_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            FunctionId
        """
        return jsii.get(self, "attrFunctionId")

    @property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "attrName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> str:
        """``AWS::AppSync::FunctionConfiguration.ApiId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-apiid
        Stability:
            stable
        """
        return jsii.get(self, "apiId")

    @api_id.setter
    def api_id(self, value: str):
        return jsii.set(self, "apiId", value)

    @property
    @jsii.member(jsii_name="dataSourceName")
    def data_source_name(self) -> str:
        """``AWS::AppSync::FunctionConfiguration.DataSourceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-datasourcename
        Stability:
            stable
        """
        return jsii.get(self, "dataSourceName")

    @data_source_name.setter
    def data_source_name(self, value: str):
        return jsii.set(self, "dataSourceName", value)

    @property
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> str:
        """``AWS::AppSync::FunctionConfiguration.FunctionVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-functionversion
        Stability:
            stable
        """
        return jsii.get(self, "functionVersion")

    @function_version.setter
    def function_version(self, value: str):
        return jsii.set(self, "functionVersion", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::AppSync::FunctionConfiguration.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="requestMappingTemplate")
    def request_mapping_template(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.RequestMappingTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-requestmappingtemplate
        Stability:
            stable
        """
        return jsii.get(self, "requestMappingTemplate")

    @request_mapping_template.setter
    def request_mapping_template(self, value: typing.Optional[str]):
        return jsii.set(self, "requestMappingTemplate", value)

    @property
    @jsii.member(jsii_name="requestMappingTemplateS3Location")
    def request_mapping_template_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.RequestMappingTemplateS3Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-requestmappingtemplates3location
        Stability:
            stable
        """
        return jsii.get(self, "requestMappingTemplateS3Location")

    @request_mapping_template_s3_location.setter
    def request_mapping_template_s3_location(self, value: typing.Optional[str]):
        return jsii.set(self, "requestMappingTemplateS3Location", value)

    @property
    @jsii.member(jsii_name="responseMappingTemplate")
    def response_mapping_template(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-responsemappingtemplate
        Stability:
            stable
        """
        return jsii.get(self, "responseMappingTemplate")

    @response_mapping_template.setter
    def response_mapping_template(self, value: typing.Optional[str]):
        return jsii.set(self, "responseMappingTemplate", value)

    @property
    @jsii.member(jsii_name="responseMappingTemplateS3Location")
    def response_mapping_template_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplateS3Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-responsemappingtemplates3location
        Stability:
            stable
        """
        return jsii.get(self, "responseMappingTemplateS3Location")

    @response_mapping_template_s3_location.setter
    def response_mapping_template_s3_location(self, value: typing.Optional[str]):
        return jsii.set(self, "responseMappingTemplateS3Location", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnFunctionConfigurationProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::AppSync::FunctionConfiguration.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-description
    Stability:
        stable
    """
    requestMappingTemplate: str
    """``AWS::AppSync::FunctionConfiguration.RequestMappingTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-requestmappingtemplate
    Stability:
        stable
    """
    requestMappingTemplateS3Location: str
    """``AWS::AppSync::FunctionConfiguration.RequestMappingTemplateS3Location``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-requestmappingtemplates3location
    Stability:
        stable
    """
    responseMappingTemplate: str
    """``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-responsemappingtemplate
    Stability:
        stable
    """
    responseMappingTemplateS3Location: str
    """``AWS::AppSync::FunctionConfiguration.ResponseMappingTemplateS3Location``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-responsemappingtemplates3location
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnFunctionConfigurationProps", jsii_struct_bases=[_CfnFunctionConfigurationProps])
class CfnFunctionConfigurationProps(_CfnFunctionConfigurationProps):
    """Properties for defining a ``AWS::AppSync::FunctionConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html
    Stability:
        stable
    """
    apiId: str
    """``AWS::AppSync::FunctionConfiguration.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-apiid
    Stability:
        stable
    """

    dataSourceName: str
    """``AWS::AppSync::FunctionConfiguration.DataSourceName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-datasourcename
    Stability:
        stable
    """

    functionVersion: str
    """``AWS::AppSync::FunctionConfiguration.FunctionVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-functionversion
    Stability:
        stable
    """

    name: str
    """``AWS::AppSync::FunctionConfiguration.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-functionconfiguration.html#cfn-appsync-functionconfiguration-name
    Stability:
        stable
    """

class CfnGraphQLApi(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApi"):
    """A CloudFormation ``AWS::AppSync::GraphQLApi``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html
    Stability:
        stable
    cloudformationResource:
        AWS::AppSync::GraphQLApi
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, authentication_type: str, name: str, additional_authentication_providers: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "AdditionalAuthenticationProviderProperty"]]]]]=None, log_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LogConfigProperty"]]]=None, open_id_connect_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["OpenIDConnectConfigProperty"]]]=None, tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]]]=None, user_pool_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["UserPoolConfigProperty"]]]=None) -> None:
        """Create a new ``AWS::AppSync::GraphQLApi``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            authentication_type: ``AWS::AppSync::GraphQLApi.AuthenticationType``.
            name: ``AWS::AppSync::GraphQLApi.Name``.
            additional_authentication_providers: ``AWS::AppSync::GraphQLApi.AdditionalAuthenticationProviders``.
            log_config: ``AWS::AppSync::GraphQLApi.LogConfig``.
            open_id_connect_config: ``AWS::AppSync::GraphQLApi.OpenIDConnectConfig``.
            tags: ``AWS::AppSync::GraphQLApi.Tags``.
            user_pool_config: ``AWS::AppSync::GraphQLApi.UserPoolConfig``.

        Stability:
            experimental
        """
        props: CfnGraphQLApiProps = {"authenticationType": authentication_type, "name": name}

        if additional_authentication_providers is not None:
            props["additionalAuthenticationProviders"] = additional_authentication_providers

        if log_config is not None:
            props["logConfig"] = log_config

        if open_id_connect_config is not None:
            props["openIdConnectConfig"] = open_id_connect_config

        if tags is not None:
            props["tags"] = tags

        if user_pool_config is not None:
            props["userPoolConfig"] = user_pool_config

        jsii.create(CfnGraphQLApi, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrApiId")
    def attr_api_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            ApiId
        """
        return jsii.get(self, "attrApiId")

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
    @jsii.member(jsii_name="attrGraphQlUrl")
    def attr_graph_ql_url(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            GraphQLUrl
        """
        return jsii.get(self, "attrGraphQlUrl")

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
        """``AWS::AppSync::GraphQLApi.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="authenticationType")
    def authentication_type(self) -> str:
        """``AWS::AppSync::GraphQLApi.AuthenticationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-authenticationtype
        Stability:
            stable
        """
        return jsii.get(self, "authenticationType")

    @authentication_type.setter
    def authentication_type(self, value: str):
        return jsii.set(self, "authenticationType", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::AppSync::GraphQLApi.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="additionalAuthenticationProviders")
    def additional_authentication_providers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "AdditionalAuthenticationProviderProperty"]]]]]:
        """``AWS::AppSync::GraphQLApi.AdditionalAuthenticationProviders``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-additionalauthenticationproviders
        Stability:
            stable
        """
        return jsii.get(self, "additionalAuthenticationProviders")

    @additional_authentication_providers.setter
    def additional_authentication_providers(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "AdditionalAuthenticationProviderProperty"]]]]]):
        return jsii.set(self, "additionalAuthenticationProviders", value)

    @property
    @jsii.member(jsii_name="logConfig")
    def log_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LogConfigProperty"]]]:
        """``AWS::AppSync::GraphQLApi.LogConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-logconfig
        Stability:
            stable
        """
        return jsii.get(self, "logConfig")

    @log_config.setter
    def log_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["LogConfigProperty"]]]):
        return jsii.set(self, "logConfig", value)

    @property
    @jsii.member(jsii_name="openIdConnectConfig")
    def open_id_connect_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["OpenIDConnectConfigProperty"]]]:
        """``AWS::AppSync::GraphQLApi.OpenIDConnectConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-openidconnectconfig
        Stability:
            stable
        """
        return jsii.get(self, "openIdConnectConfig")

    @open_id_connect_config.setter
    def open_id_connect_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["OpenIDConnectConfigProperty"]]]):
        return jsii.set(self, "openIdConnectConfig", value)

    @property
    @jsii.member(jsii_name="userPoolConfig")
    def user_pool_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["UserPoolConfigProperty"]]]:
        """``AWS::AppSync::GraphQLApi.UserPoolConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-userpoolconfig
        Stability:
            stable
        """
        return jsii.get(self, "userPoolConfig")

    @user_pool_config.setter
    def user_pool_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["UserPoolConfigProperty"]]]):
        return jsii.set(self, "userPoolConfig", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _AdditionalAuthenticationProviderProperty(jsii.compat.TypedDict, total=False):
        openIdConnectConfig: typing.Union[aws_cdk.core.IResolvable, "CfnGraphQLApi.OpenIDConnectConfigProperty"]
        """``CfnGraphQLApi.AdditionalAuthenticationProviderProperty.OpenIDConnectConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-additionalauthenticationprovider.html#cfn-appsync-graphqlapi-additionalauthenticationprovider-openidconnectconfig
        Stability:
            stable
        """
        userPoolConfig: typing.Union[aws_cdk.core.IResolvable, "CfnGraphQLApi.CognitoUserPoolConfigProperty"]
        """``CfnGraphQLApi.AdditionalAuthenticationProviderProperty.UserPoolConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-additionalauthenticationprovider.html#cfn-appsync-graphqlapi-additionalauthenticationprovider-userpoolconfig
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApi.AdditionalAuthenticationProviderProperty", jsii_struct_bases=[_AdditionalAuthenticationProviderProperty])
    class AdditionalAuthenticationProviderProperty(_AdditionalAuthenticationProviderProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-additionalauthenticationprovider.html
        Stability:
            stable
        """
        authenticationType: str
        """``CfnGraphQLApi.AdditionalAuthenticationProviderProperty.AuthenticationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-additionalauthenticationprovider.html#cfn-appsync-graphqlapi-additionalauthenticationprovider-authenticationtype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApi.CognitoUserPoolConfigProperty", jsii_struct_bases=[])
    class CognitoUserPoolConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-cognitouserpoolconfig.html
        Stability:
            stable
        """
        appIdClientRegex: str
        """``CfnGraphQLApi.CognitoUserPoolConfigProperty.AppIdClientRegex``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-cognitouserpoolconfig.html#cfn-appsync-graphqlapi-cognitouserpoolconfig-appidclientregex
        Stability:
            stable
        """

        awsRegion: str
        """``CfnGraphQLApi.CognitoUserPoolConfigProperty.AwsRegion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-cognitouserpoolconfig.html#cfn-appsync-graphqlapi-cognitouserpoolconfig-awsregion
        Stability:
            stable
        """

        userPoolId: str
        """``CfnGraphQLApi.CognitoUserPoolConfigProperty.UserPoolId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-cognitouserpoolconfig.html#cfn-appsync-graphqlapi-cognitouserpoolconfig-userpoolid
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApi.LogConfigProperty", jsii_struct_bases=[])
    class LogConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-logconfig.html
        Stability:
            stable
        """
        cloudWatchLogsRoleArn: str
        """``CfnGraphQLApi.LogConfigProperty.CloudWatchLogsRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-logconfig.html#cfn-appsync-graphqlapi-logconfig-cloudwatchlogsrolearn
        Stability:
            stable
        """

        fieldLogLevel: str
        """``CfnGraphQLApi.LogConfigProperty.FieldLogLevel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-logconfig.html#cfn-appsync-graphqlapi-logconfig-fieldloglevel
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApi.OpenIDConnectConfigProperty", jsii_struct_bases=[])
    class OpenIDConnectConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-openidconnectconfig.html
        Stability:
            stable
        """
        authTtl: jsii.Number
        """``CfnGraphQLApi.OpenIDConnectConfigProperty.AuthTTL``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-openidconnectconfig.html#cfn-appsync-graphqlapi-openidconnectconfig-authttl
        Stability:
            stable
        """

        clientId: str
        """``CfnGraphQLApi.OpenIDConnectConfigProperty.ClientId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-openidconnectconfig.html#cfn-appsync-graphqlapi-openidconnectconfig-clientid
        Stability:
            stable
        """

        iatTtl: jsii.Number
        """``CfnGraphQLApi.OpenIDConnectConfigProperty.IatTTL``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-openidconnectconfig.html#cfn-appsync-graphqlapi-openidconnectconfig-iatttl
        Stability:
            stable
        """

        issuer: str
        """``CfnGraphQLApi.OpenIDConnectConfigProperty.Issuer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-openidconnectconfig.html#cfn-appsync-graphqlapi-openidconnectconfig-issuer
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApi.UserPoolConfigProperty", jsii_struct_bases=[])
    class UserPoolConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-userpoolconfig.html
        Stability:
            stable
        """
        appIdClientRegex: str
        """``CfnGraphQLApi.UserPoolConfigProperty.AppIdClientRegex``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-userpoolconfig.html#cfn-appsync-graphqlapi-userpoolconfig-appidclientregex
        Stability:
            stable
        """

        awsRegion: str
        """``CfnGraphQLApi.UserPoolConfigProperty.AwsRegion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-userpoolconfig.html#cfn-appsync-graphqlapi-userpoolconfig-awsregion
        Stability:
            stable
        """

        defaultAction: str
        """``CfnGraphQLApi.UserPoolConfigProperty.DefaultAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-userpoolconfig.html#cfn-appsync-graphqlapi-userpoolconfig-defaultaction
        Stability:
            stable
        """

        userPoolId: str
        """``CfnGraphQLApi.UserPoolConfigProperty.UserPoolId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-userpoolconfig.html#cfn-appsync-graphqlapi-userpoolconfig-userpoolid
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnGraphQLApiProps(jsii.compat.TypedDict, total=False):
    additionalAuthenticationProviders: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnGraphQLApi.AdditionalAuthenticationProviderProperty"]]]
    """``AWS::AppSync::GraphQLApi.AdditionalAuthenticationProviders``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-additionalauthenticationproviders
    Stability:
        stable
    """
    logConfig: typing.Union[aws_cdk.core.IResolvable, "CfnGraphQLApi.LogConfigProperty"]
    """``AWS::AppSync::GraphQLApi.LogConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-logconfig
    Stability:
        stable
    """
    openIdConnectConfig: typing.Union[aws_cdk.core.IResolvable, "CfnGraphQLApi.OpenIDConnectConfigProperty"]
    """``AWS::AppSync::GraphQLApi.OpenIDConnectConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-openidconnectconfig
    Stability:
        stable
    """
    tags: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, aws_cdk.core.CfnTag]]]
    """``AWS::AppSync::GraphQLApi.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-tags
    Stability:
        stable
    """
    userPoolConfig: typing.Union[aws_cdk.core.IResolvable, "CfnGraphQLApi.UserPoolConfigProperty"]
    """``AWS::AppSync::GraphQLApi.UserPoolConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-userpoolconfig
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLApiProps", jsii_struct_bases=[_CfnGraphQLApiProps])
class CfnGraphQLApiProps(_CfnGraphQLApiProps):
    """Properties for defining a ``AWS::AppSync::GraphQLApi``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html
    Stability:
        stable
    """
    authenticationType: str
    """``AWS::AppSync::GraphQLApi.AuthenticationType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-authenticationtype
    Stability:
        stable
    """

    name: str
    """``AWS::AppSync::GraphQLApi.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlapi.html#cfn-appsync-graphqlapi-name
    Stability:
        stable
    """

class CfnGraphQLSchema(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync.CfnGraphQLSchema"):
    """A CloudFormation ``AWS::AppSync::GraphQLSchema``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html
    Stability:
        stable
    cloudformationResource:
        AWS::AppSync::GraphQLSchema
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_id: str, definition: typing.Optional[str]=None, definition_s3_location: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::AppSync::GraphQLSchema``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            api_id: ``AWS::AppSync::GraphQLSchema.ApiId``.
            definition: ``AWS::AppSync::GraphQLSchema.Definition``.
            definition_s3_location: ``AWS::AppSync::GraphQLSchema.DefinitionS3Location``.

        Stability:
            experimental
        """
        props: CfnGraphQLSchemaProps = {"apiId": api_id}

        if definition is not None:
            props["definition"] = definition

        if definition_s3_location is not None:
            props["definitionS3Location"] = definition_s3_location

        jsii.create(CfnGraphQLSchema, self, [scope, id, props])

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
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> str:
        """``AWS::AppSync::GraphQLSchema.ApiId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html#cfn-appsync-graphqlschema-apiid
        Stability:
            stable
        """
        return jsii.get(self, "apiId")

    @api_id.setter
    def api_id(self, value: str):
        return jsii.set(self, "apiId", value)

    @property
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.Optional[str]:
        """``AWS::AppSync::GraphQLSchema.Definition``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html#cfn-appsync-graphqlschema-definition
        Stability:
            stable
        """
        return jsii.get(self, "definition")

    @definition.setter
    def definition(self, value: typing.Optional[str]):
        return jsii.set(self, "definition", value)

    @property
    @jsii.member(jsii_name="definitionS3Location")
    def definition_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::GraphQLSchema.DefinitionS3Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html#cfn-appsync-graphqlschema-definitions3location
        Stability:
            stable
        """
        return jsii.get(self, "definitionS3Location")

    @definition_s3_location.setter
    def definition_s3_location(self, value: typing.Optional[str]):
        return jsii.set(self, "definitionS3Location", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnGraphQLSchemaProps(jsii.compat.TypedDict, total=False):
    definition: str
    """``AWS::AppSync::GraphQLSchema.Definition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html#cfn-appsync-graphqlschema-definition
    Stability:
        stable
    """
    definitionS3Location: str
    """``AWS::AppSync::GraphQLSchema.DefinitionS3Location``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html#cfn-appsync-graphqlschema-definitions3location
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnGraphQLSchemaProps", jsii_struct_bases=[_CfnGraphQLSchemaProps])
class CfnGraphQLSchemaProps(_CfnGraphQLSchemaProps):
    """Properties for defining a ``AWS::AppSync::GraphQLSchema``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html
    Stability:
        stable
    """
    apiId: str
    """``AWS::AppSync::GraphQLSchema.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-graphqlschema.html#cfn-appsync-graphqlschema-apiid
    Stability:
        stable
    """

class CfnResolver(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync.CfnResolver"):
    """A CloudFormation ``AWS::AppSync::Resolver``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html
    Stability:
        stable
    cloudformationResource:
        AWS::AppSync::Resolver
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, api_id: str, field_name: str, type_name: str, data_source_name: typing.Optional[str]=None, kind: typing.Optional[str]=None, pipeline_config: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PipelineConfigProperty"]]]=None, request_mapping_template: typing.Optional[str]=None, request_mapping_template_s3_location: typing.Optional[str]=None, response_mapping_template: typing.Optional[str]=None, response_mapping_template_s3_location: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::AppSync::Resolver``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            api_id: ``AWS::AppSync::Resolver.ApiId``.
            field_name: ``AWS::AppSync::Resolver.FieldName``.
            type_name: ``AWS::AppSync::Resolver.TypeName``.
            data_source_name: ``AWS::AppSync::Resolver.DataSourceName``.
            kind: ``AWS::AppSync::Resolver.Kind``.
            pipeline_config: ``AWS::AppSync::Resolver.PipelineConfig``.
            request_mapping_template: ``AWS::AppSync::Resolver.RequestMappingTemplate``.
            request_mapping_template_s3_location: ``AWS::AppSync::Resolver.RequestMappingTemplateS3Location``.
            response_mapping_template: ``AWS::AppSync::Resolver.ResponseMappingTemplate``.
            response_mapping_template_s3_location: ``AWS::AppSync::Resolver.ResponseMappingTemplateS3Location``.

        Stability:
            experimental
        """
        props: CfnResolverProps = {"apiId": api_id, "fieldName": field_name, "typeName": type_name}

        if data_source_name is not None:
            props["dataSourceName"] = data_source_name

        if kind is not None:
            props["kind"] = kind

        if pipeline_config is not None:
            props["pipelineConfig"] = pipeline_config

        if request_mapping_template is not None:
            props["requestMappingTemplate"] = request_mapping_template

        if request_mapping_template_s3_location is not None:
            props["requestMappingTemplateS3Location"] = request_mapping_template_s3_location

        if response_mapping_template is not None:
            props["responseMappingTemplate"] = response_mapping_template

        if response_mapping_template_s3_location is not None:
            props["responseMappingTemplateS3Location"] = response_mapping_template_s3_location

        jsii.create(CfnResolver, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrFieldName")
    def attr_field_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            FieldName
        """
        return jsii.get(self, "attrFieldName")

    @property
    @jsii.member(jsii_name="attrResolverArn")
    def attr_resolver_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            ResolverArn
        """
        return jsii.get(self, "attrResolverArn")

    @property
    @jsii.member(jsii_name="attrTypeName")
    def attr_type_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            TypeName
        """
        return jsii.get(self, "attrTypeName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> str:
        """``AWS::AppSync::Resolver.ApiId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-apiid
        Stability:
            stable
        """
        return jsii.get(self, "apiId")

    @api_id.setter
    def api_id(self, value: str):
        return jsii.set(self, "apiId", value)

    @property
    @jsii.member(jsii_name="fieldName")
    def field_name(self) -> str:
        """``AWS::AppSync::Resolver.FieldName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-fieldname
        Stability:
            stable
        """
        return jsii.get(self, "fieldName")

    @field_name.setter
    def field_name(self, value: str):
        return jsii.set(self, "fieldName", value)

    @property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> str:
        """``AWS::AppSync::Resolver.TypeName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-typename
        Stability:
            stable
        """
        return jsii.get(self, "typeName")

    @type_name.setter
    def type_name(self, value: str):
        return jsii.set(self, "typeName", value)

    @property
    @jsii.member(jsii_name="dataSourceName")
    def data_source_name(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.DataSourceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-datasourcename
        Stability:
            stable
        """
        return jsii.get(self, "dataSourceName")

    @data_source_name.setter
    def data_source_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dataSourceName", value)

    @property
    @jsii.member(jsii_name="kind")
    def kind(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.Kind``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-kind
        Stability:
            stable
        """
        return jsii.get(self, "kind")

    @kind.setter
    def kind(self, value: typing.Optional[str]):
        return jsii.set(self, "kind", value)

    @property
    @jsii.member(jsii_name="pipelineConfig")
    def pipeline_config(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PipelineConfigProperty"]]]:
        """``AWS::AppSync::Resolver.PipelineConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-pipelineconfig
        Stability:
            stable
        """
        return jsii.get(self, "pipelineConfig")

    @pipeline_config.setter
    def pipeline_config(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PipelineConfigProperty"]]]):
        return jsii.set(self, "pipelineConfig", value)

    @property
    @jsii.member(jsii_name="requestMappingTemplate")
    def request_mapping_template(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.RequestMappingTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-requestmappingtemplate
        Stability:
            stable
        """
        return jsii.get(self, "requestMappingTemplate")

    @request_mapping_template.setter
    def request_mapping_template(self, value: typing.Optional[str]):
        return jsii.set(self, "requestMappingTemplate", value)

    @property
    @jsii.member(jsii_name="requestMappingTemplateS3Location")
    def request_mapping_template_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.RequestMappingTemplateS3Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-requestmappingtemplates3location
        Stability:
            stable
        """
        return jsii.get(self, "requestMappingTemplateS3Location")

    @request_mapping_template_s3_location.setter
    def request_mapping_template_s3_location(self, value: typing.Optional[str]):
        return jsii.set(self, "requestMappingTemplateS3Location", value)

    @property
    @jsii.member(jsii_name="responseMappingTemplate")
    def response_mapping_template(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.ResponseMappingTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-responsemappingtemplate
        Stability:
            stable
        """
        return jsii.get(self, "responseMappingTemplate")

    @response_mapping_template.setter
    def response_mapping_template(self, value: typing.Optional[str]):
        return jsii.set(self, "responseMappingTemplate", value)

    @property
    @jsii.member(jsii_name="responseMappingTemplateS3Location")
    def response_mapping_template_s3_location(self) -> typing.Optional[str]:
        """``AWS::AppSync::Resolver.ResponseMappingTemplateS3Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-responsemappingtemplates3location
        Stability:
            stable
        """
        return jsii.get(self, "responseMappingTemplateS3Location")

    @response_mapping_template_s3_location.setter
    def response_mapping_template_s3_location(self, value: typing.Optional[str]):
        return jsii.set(self, "responseMappingTemplateS3Location", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnResolver.PipelineConfigProperty", jsii_struct_bases=[])
    class PipelineConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-resolver-pipelineconfig.html
        Stability:
            stable
        """
        functions: typing.List[str]
        """``CfnResolver.PipelineConfigProperty.Functions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-resolver-pipelineconfig.html#cfn-appsync-resolver-pipelineconfig-functions
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnResolverProps(jsii.compat.TypedDict, total=False):
    dataSourceName: str
    """``AWS::AppSync::Resolver.DataSourceName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-datasourcename
    Stability:
        stable
    """
    kind: str
    """``AWS::AppSync::Resolver.Kind``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-kind
    Stability:
        stable
    """
    pipelineConfig: typing.Union[aws_cdk.core.IResolvable, "CfnResolver.PipelineConfigProperty"]
    """``AWS::AppSync::Resolver.PipelineConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-pipelineconfig
    Stability:
        stable
    """
    requestMappingTemplate: str
    """``AWS::AppSync::Resolver.RequestMappingTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-requestmappingtemplate
    Stability:
        stable
    """
    requestMappingTemplateS3Location: str
    """``AWS::AppSync::Resolver.RequestMappingTemplateS3Location``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-requestmappingtemplates3location
    Stability:
        stable
    """
    responseMappingTemplate: str
    """``AWS::AppSync::Resolver.ResponseMappingTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-responsemappingtemplate
    Stability:
        stable
    """
    responseMappingTemplateS3Location: str
    """``AWS::AppSync::Resolver.ResponseMappingTemplateS3Location``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-responsemappingtemplates3location
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-appsync.CfnResolverProps", jsii_struct_bases=[_CfnResolverProps])
class CfnResolverProps(_CfnResolverProps):
    """Properties for defining a ``AWS::AppSync::Resolver``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html
    Stability:
        stable
    """
    apiId: str
    """``AWS::AppSync::Resolver.ApiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-apiid
    Stability:
        stable
    """

    fieldName: str
    """``AWS::AppSync::Resolver.FieldName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-fieldname
    Stability:
        stable
    """

    typeName: str
    """``AWS::AppSync::Resolver.TypeName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appsync-resolver.html#cfn-appsync-resolver-typename
    Stability:
        stable
    """

__all__ = ["CfnApiKey", "CfnApiKeyProps", "CfnDataSource", "CfnDataSourceProps", "CfnFunctionConfiguration", "CfnFunctionConfigurationProps", "CfnGraphQLApi", "CfnGraphQLApiProps", "CfnGraphQLSchema", "CfnGraphQLSchemaProps", "CfnResolver", "CfnResolverProps", "__jsii_assembly__"]

publication.publish()
