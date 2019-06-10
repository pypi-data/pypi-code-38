import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-dms", "0.34.0", __name__, "aws-dms@0.34.0.jsii.tgz")
class CfnCertificate(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dms.CfnCertificate"):
    """A CloudFormation ``AWS::DMS::Certificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DMS::Certificate
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, certificate_identifier: typing.Optional[str]=None, certificate_pem: typing.Optional[str]=None, certificate_wallet: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::DMS::Certificate``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            certificateIdentifier: ``AWS::DMS::Certificate.CertificateIdentifier``.
            certificatePem: ``AWS::DMS::Certificate.CertificatePem``.
            certificateWallet: ``AWS::DMS::Certificate.CertificateWallet``.

        Stability:
            experimental
        """
        props: CfnCertificateProps = {}

        if certificate_identifier is not None:
            props["certificateIdentifier"] = certificate_identifier

        if certificate_pem is not None:
            props["certificatePem"] = certificate_pem

        if certificate_wallet is not None:
            props["certificateWallet"] = certificate_wallet

        jsii.create(CfnCertificate, self, [scope, id, props])

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
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "certificateArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnCertificateProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnCertificateProps", jsii_struct_bases=[])
class CfnCertificateProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::DMS::Certificate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html
    Stability:
        experimental
    """
    certificateIdentifier: str
    """``AWS::DMS::Certificate.CertificateIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificateidentifier
    Stability:
        experimental
    """

    certificatePem: str
    """``AWS::DMS::Certificate.CertificatePem``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificatepem
    Stability:
        experimental
    """

    certificateWallet: str
    """``AWS::DMS::Certificate.CertificateWallet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificatewallet
    Stability:
        experimental
    """

class CfnEndpoint(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dms.CfnEndpoint"):
    """A CloudFormation ``AWS::DMS::Endpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DMS::Endpoint
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, endpoint_type: str, engine_name: str, certificate_arn: typing.Optional[str]=None, database_name: typing.Optional[str]=None, dynamo_db_settings: typing.Optional[typing.Union[typing.Optional["DynamoDbSettingsProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None, elasticsearch_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ElasticsearchSettingsProperty"]]]=None, endpoint_identifier: typing.Optional[str]=None, extra_connection_attributes: typing.Optional[str]=None, kinesis_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["KinesisSettingsProperty"]]]=None, kms_key_id: typing.Optional[str]=None, mongo_db_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["MongoDbSettingsProperty"]]]=None, password: typing.Optional[str]=None, port: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, s3_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["S3SettingsProperty"]]]=None, server_name: typing.Optional[str]=None, ssl_mode: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, username: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::DMS::Endpoint``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            endpointType: ``AWS::DMS::Endpoint.EndpointType``.
            engineName: ``AWS::DMS::Endpoint.EngineName``.
            certificateArn: ``AWS::DMS::Endpoint.CertificateArn``.
            databaseName: ``AWS::DMS::Endpoint.DatabaseName``.
            dynamoDbSettings: ``AWS::DMS::Endpoint.DynamoDbSettings``.
            elasticsearchSettings: ``AWS::DMS::Endpoint.ElasticsearchSettings``.
            endpointIdentifier: ``AWS::DMS::Endpoint.EndpointIdentifier``.
            extraConnectionAttributes: ``AWS::DMS::Endpoint.ExtraConnectionAttributes``.
            kinesisSettings: ``AWS::DMS::Endpoint.KinesisSettings``.
            kmsKeyId: ``AWS::DMS::Endpoint.KmsKeyId``.
            mongoDbSettings: ``AWS::DMS::Endpoint.MongoDbSettings``.
            password: ``AWS::DMS::Endpoint.Password``.
            port: ``AWS::DMS::Endpoint.Port``.
            s3Settings: ``AWS::DMS::Endpoint.S3Settings``.
            serverName: ``AWS::DMS::Endpoint.ServerName``.
            sslMode: ``AWS::DMS::Endpoint.SslMode``.
            tags: ``AWS::DMS::Endpoint.Tags``.
            username: ``AWS::DMS::Endpoint.Username``.

        Stability:
            experimental
        """
        props: CfnEndpointProps = {"endpointType": endpoint_type, "engineName": engine_name}

        if certificate_arn is not None:
            props["certificateArn"] = certificate_arn

        if database_name is not None:
            props["databaseName"] = database_name

        if dynamo_db_settings is not None:
            props["dynamoDbSettings"] = dynamo_db_settings

        if elasticsearch_settings is not None:
            props["elasticsearchSettings"] = elasticsearch_settings

        if endpoint_identifier is not None:
            props["endpointIdentifier"] = endpoint_identifier

        if extra_connection_attributes is not None:
            props["extraConnectionAttributes"] = extra_connection_attributes

        if kinesis_settings is not None:
            props["kinesisSettings"] = kinesis_settings

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

        if mongo_db_settings is not None:
            props["mongoDbSettings"] = mongo_db_settings

        if password is not None:
            props["password"] = password

        if port is not None:
            props["port"] = port

        if s3_settings is not None:
            props["s3Settings"] = s3_settings

        if server_name is not None:
            props["serverName"] = server_name

        if ssl_mode is not None:
            props["sslMode"] = ssl_mode

        if tags is not None:
            props["tags"] = tags

        if username is not None:
            props["username"] = username

        jsii.create(CfnEndpoint, self, [scope, id, props])

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
    @jsii.member(jsii_name="endpointArn")
    def endpoint_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "endpointArn")

    @property
    @jsii.member(jsii_name="endpointExternalId")
    def endpoint_external_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ExternalId
        """
        return jsii.get(self, "endpointExternalId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnEndpointProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

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

    @jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEndpoint.DynamoDbSettingsProperty", jsii_struct_bases=[])
    class DynamoDbSettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-dynamodbsettings.html
        Stability:
            experimental
        """
        serviceAccessRoleArn: str
        """``CfnEndpoint.DynamoDbSettingsProperty.ServiceAccessRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-dynamodbsettings.html#cfn-dms-endpoint-dynamodbsettings-serviceaccessrolearn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEndpoint.ElasticsearchSettingsProperty", jsii_struct_bases=[])
    class ElasticsearchSettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html
        Stability:
            experimental
        """
        endpointUri: str
        """``CfnEndpoint.ElasticsearchSettingsProperty.EndpointUri``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html#cfn-dms-endpoint-elasticsearchsettings-endpointuri
        Stability:
            experimental
        """

        errorRetryDuration: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnEndpoint.ElasticsearchSettingsProperty.ErrorRetryDuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html#cfn-dms-endpoint-elasticsearchsettings-errorretryduration
        Stability:
            experimental
        """

        fullLoadErrorPercentage: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnEndpoint.ElasticsearchSettingsProperty.FullLoadErrorPercentage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html#cfn-dms-endpoint-elasticsearchsettings-fullloaderrorpercentage
        Stability:
            experimental
        """

        serviceAccessRoleArn: str
        """``CfnEndpoint.ElasticsearchSettingsProperty.ServiceAccessRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html#cfn-dms-endpoint-elasticsearchsettings-serviceaccessrolearn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEndpoint.KinesisSettingsProperty", jsii_struct_bases=[])
    class KinesisSettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html
        Stability:
            experimental
        """
        messageFormat: str
        """``CfnEndpoint.KinesisSettingsProperty.MessageFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-messageformat
        Stability:
            experimental
        """

        serviceAccessRoleArn: str
        """``CfnEndpoint.KinesisSettingsProperty.ServiceAccessRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-serviceaccessrolearn
        Stability:
            experimental
        """

        streamArn: str
        """``CfnEndpoint.KinesisSettingsProperty.StreamArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-streamarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEndpoint.MongoDbSettingsProperty", jsii_struct_bases=[])
    class MongoDbSettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html
        Stability:
            experimental
        """
        authMechanism: str
        """``CfnEndpoint.MongoDbSettingsProperty.AuthMechanism``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-authmechanism
        Stability:
            experimental
        """

        authSource: str
        """``CfnEndpoint.MongoDbSettingsProperty.AuthSource``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-authsource
        Stability:
            experimental
        """

        authType: str
        """``CfnEndpoint.MongoDbSettingsProperty.AuthType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-authtype
        Stability:
            experimental
        """

        databaseName: str
        """``CfnEndpoint.MongoDbSettingsProperty.DatabaseName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-databasename
        Stability:
            experimental
        """

        docsToInvestigate: str
        """``CfnEndpoint.MongoDbSettingsProperty.DocsToInvestigate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-docstoinvestigate
        Stability:
            experimental
        """

        extractDocId: str
        """``CfnEndpoint.MongoDbSettingsProperty.ExtractDocId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-extractdocid
        Stability:
            experimental
        """

        nestingLevel: str
        """``CfnEndpoint.MongoDbSettingsProperty.NestingLevel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-nestinglevel
        Stability:
            experimental
        """

        password: str
        """``CfnEndpoint.MongoDbSettingsProperty.Password``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-password
        Stability:
            experimental
        """

        port: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnEndpoint.MongoDbSettingsProperty.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-port
        Stability:
            experimental
        """

        serverName: str
        """``CfnEndpoint.MongoDbSettingsProperty.ServerName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-servername
        Stability:
            experimental
        """

        username: str
        """``CfnEndpoint.MongoDbSettingsProperty.Username``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-username
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEndpoint.S3SettingsProperty", jsii_struct_bases=[])
    class S3SettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html
        Stability:
            experimental
        """
        bucketFolder: str
        """``CfnEndpoint.S3SettingsProperty.BucketFolder``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-bucketfolder
        Stability:
            experimental
        """

        bucketName: str
        """``CfnEndpoint.S3SettingsProperty.BucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-bucketname
        Stability:
            experimental
        """

        compressionType: str
        """``CfnEndpoint.S3SettingsProperty.CompressionType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-compressiontype
        Stability:
            experimental
        """

        csvDelimiter: str
        """``CfnEndpoint.S3SettingsProperty.CsvDelimiter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-csvdelimiter
        Stability:
            experimental
        """

        csvRowDelimiter: str
        """``CfnEndpoint.S3SettingsProperty.CsvRowDelimiter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-csvrowdelimiter
        Stability:
            experimental
        """

        externalTableDefinition: str
        """``CfnEndpoint.S3SettingsProperty.ExternalTableDefinition``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-externaltabledefinition
        Stability:
            experimental
        """

        serviceAccessRoleArn: str
        """``CfnEndpoint.S3SettingsProperty.ServiceAccessRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-serviceaccessrolearn
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEndpointProps(jsii.compat.TypedDict, total=False):
    certificateArn: str
    """``AWS::DMS::Endpoint.CertificateArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-certificatearn
    Stability:
        experimental
    """
    databaseName: str
    """``AWS::DMS::Endpoint.DatabaseName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-databasename
    Stability:
        experimental
    """
    dynamoDbSettings: typing.Union["CfnEndpoint.DynamoDbSettingsProperty", aws_cdk.cdk.Token]
    """``AWS::DMS::Endpoint.DynamoDbSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-dynamodbsettings
    Stability:
        experimental
    """
    elasticsearchSettings: typing.Union[aws_cdk.cdk.Token, "CfnEndpoint.ElasticsearchSettingsProperty"]
    """``AWS::DMS::Endpoint.ElasticsearchSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-elasticsearchsettings
    Stability:
        experimental
    """
    endpointIdentifier: str
    """``AWS::DMS::Endpoint.EndpointIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-endpointidentifier
    Stability:
        experimental
    """
    extraConnectionAttributes: str
    """``AWS::DMS::Endpoint.ExtraConnectionAttributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-extraconnectionattributes
    Stability:
        experimental
    """
    kinesisSettings: typing.Union[aws_cdk.cdk.Token, "CfnEndpoint.KinesisSettingsProperty"]
    """``AWS::DMS::Endpoint.KinesisSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-kinesissettings
    Stability:
        experimental
    """
    kmsKeyId: str
    """``AWS::DMS::Endpoint.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-kmskeyid
    Stability:
        experimental
    """
    mongoDbSettings: typing.Union[aws_cdk.cdk.Token, "CfnEndpoint.MongoDbSettingsProperty"]
    """``AWS::DMS::Endpoint.MongoDbSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-mongodbsettings
    Stability:
        experimental
    """
    password: str
    """``AWS::DMS::Endpoint.Password``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-password
    Stability:
        experimental
    """
    port: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::DMS::Endpoint.Port``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-port
    Stability:
        experimental
    """
    s3Settings: typing.Union[aws_cdk.cdk.Token, "CfnEndpoint.S3SettingsProperty"]
    """``AWS::DMS::Endpoint.S3Settings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-s3settings
    Stability:
        experimental
    """
    serverName: str
    """``AWS::DMS::Endpoint.ServerName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-servername
    Stability:
        experimental
    """
    sslMode: str
    """``AWS::DMS::Endpoint.SslMode``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-sslmode
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::DMS::Endpoint.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-tags
    Stability:
        experimental
    """
    username: str
    """``AWS::DMS::Endpoint.Username``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-username
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEndpointProps", jsii_struct_bases=[_CfnEndpointProps])
class CfnEndpointProps(_CfnEndpointProps):
    """Properties for defining a ``AWS::DMS::Endpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html
    Stability:
        experimental
    """
    endpointType: str
    """``AWS::DMS::Endpoint.EndpointType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-endpointtype
    Stability:
        experimental
    """

    engineName: str
    """``AWS::DMS::Endpoint.EngineName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-enginename
    Stability:
        experimental
    """

class CfnEventSubscription(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dms.CfnEventSubscription"):
    """A CloudFormation ``AWS::DMS::EventSubscription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DMS::EventSubscription
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, sns_topic_arn: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, event_categories: typing.Optional[typing.List[str]]=None, source_ids: typing.Optional[typing.List[str]]=None, source_type: typing.Optional[str]=None, subscription_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::DMS::EventSubscription``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            snsTopicArn: ``AWS::DMS::EventSubscription.SnsTopicArn``.
            enabled: ``AWS::DMS::EventSubscription.Enabled``.
            eventCategories: ``AWS::DMS::EventSubscription.EventCategories``.
            sourceIds: ``AWS::DMS::EventSubscription.SourceIds``.
            sourceType: ``AWS::DMS::EventSubscription.SourceType``.
            subscriptionName: ``AWS::DMS::EventSubscription.SubscriptionName``.
            tags: ``AWS::DMS::EventSubscription.Tags``.

        Stability:
            experimental
        """
        props: CfnEventSubscriptionProps = {"snsTopicArn": sns_topic_arn}

        if enabled is not None:
            props["enabled"] = enabled

        if event_categories is not None:
            props["eventCategories"] = event_categories

        if source_ids is not None:
            props["sourceIds"] = source_ids

        if source_type is not None:
            props["sourceType"] = source_type

        if subscription_name is not None:
            props["subscriptionName"] = subscription_name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnEventSubscription, self, [scope, id, props])

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
    @jsii.member(jsii_name="eventSubscriptionName")
    def event_subscription_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "eventSubscriptionName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnEventSubscriptionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

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
class _CfnEventSubscriptionProps(jsii.compat.TypedDict, total=False):
    enabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::DMS::EventSubscription.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-enabled
    Stability:
        experimental
    """
    eventCategories: typing.List[str]
    """``AWS::DMS::EventSubscription.EventCategories``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-eventcategories
    Stability:
        experimental
    """
    sourceIds: typing.List[str]
    """``AWS::DMS::EventSubscription.SourceIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-sourceids
    Stability:
        experimental
    """
    sourceType: str
    """``AWS::DMS::EventSubscription.SourceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-sourcetype
    Stability:
        experimental
    """
    subscriptionName: str
    """``AWS::DMS::EventSubscription.SubscriptionName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-subscriptionname
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::DMS::EventSubscription.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnEventSubscriptionProps", jsii_struct_bases=[_CfnEventSubscriptionProps])
class CfnEventSubscriptionProps(_CfnEventSubscriptionProps):
    """Properties for defining a ``AWS::DMS::EventSubscription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html
    Stability:
        experimental
    """
    snsTopicArn: str
    """``AWS::DMS::EventSubscription.SnsTopicArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-snstopicarn
    Stability:
        experimental
    """

class CfnReplicationInstance(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dms.CfnReplicationInstance"):
    """A CloudFormation ``AWS::DMS::ReplicationInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DMS::ReplicationInstance
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, replication_instance_class: str, allocated_storage: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, allow_major_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, availability_zone: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, multi_az: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, preferred_maintenance_window: typing.Optional[str]=None, publicly_accessible: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, replication_instance_identifier: typing.Optional[str]=None, replication_subnet_group_identifier: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::DMS::ReplicationInstance``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            replicationInstanceClass: ``AWS::DMS::ReplicationInstance.ReplicationInstanceClass``.
            allocatedStorage: ``AWS::DMS::ReplicationInstance.AllocatedStorage``.
            allowMajorVersionUpgrade: ``AWS::DMS::ReplicationInstance.AllowMajorVersionUpgrade``.
            autoMinorVersionUpgrade: ``AWS::DMS::ReplicationInstance.AutoMinorVersionUpgrade``.
            availabilityZone: ``AWS::DMS::ReplicationInstance.AvailabilityZone``.
            engineVersion: ``AWS::DMS::ReplicationInstance.EngineVersion``.
            kmsKeyId: ``AWS::DMS::ReplicationInstance.KmsKeyId``.
            multiAz: ``AWS::DMS::ReplicationInstance.MultiAZ``.
            preferredMaintenanceWindow: ``AWS::DMS::ReplicationInstance.PreferredMaintenanceWindow``.
            publiclyAccessible: ``AWS::DMS::ReplicationInstance.PubliclyAccessible``.
            replicationInstanceIdentifier: ``AWS::DMS::ReplicationInstance.ReplicationInstanceIdentifier``.
            replicationSubnetGroupIdentifier: ``AWS::DMS::ReplicationInstance.ReplicationSubnetGroupIdentifier``.
            tags: ``AWS::DMS::ReplicationInstance.Tags``.
            vpcSecurityGroupIds: ``AWS::DMS::ReplicationInstance.VpcSecurityGroupIds``.

        Stability:
            experimental
        """
        props: CfnReplicationInstanceProps = {"replicationInstanceClass": replication_instance_class}

        if allocated_storage is not None:
            props["allocatedStorage"] = allocated_storage

        if allow_major_version_upgrade is not None:
            props["allowMajorVersionUpgrade"] = allow_major_version_upgrade

        if auto_minor_version_upgrade is not None:
            props["autoMinorVersionUpgrade"] = auto_minor_version_upgrade

        if availability_zone is not None:
            props["availabilityZone"] = availability_zone

        if engine_version is not None:
            props["engineVersion"] = engine_version

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

        if multi_az is not None:
            props["multiAz"] = multi_az

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if publicly_accessible is not None:
            props["publiclyAccessible"] = publicly_accessible

        if replication_instance_identifier is not None:
            props["replicationInstanceIdentifier"] = replication_instance_identifier

        if replication_subnet_group_identifier is not None:
            props["replicationSubnetGroupIdentifier"] = replication_subnet_group_identifier

        if tags is not None:
            props["tags"] = tags

        if vpc_security_group_ids is not None:
            props["vpcSecurityGroupIds"] = vpc_security_group_ids

        jsii.create(CfnReplicationInstance, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnReplicationInstanceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="replicationInstanceArn")
    def replication_instance_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "replicationInstanceArn")

    @property
    @jsii.member(jsii_name="replicationInstancePrivateIpAddresses")
    def replication_instance_private_ip_addresses(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReplicationInstancePrivateIpAddresses
        """
        return jsii.get(self, "replicationInstancePrivateIpAddresses")

    @property
    @jsii.member(jsii_name="replicationInstancePublicIpAddresses")
    def replication_instance_public_ip_addresses(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReplicationInstancePublicIpAddresses
        """
        return jsii.get(self, "replicationInstancePublicIpAddresses")

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
class _CfnReplicationInstanceProps(jsii.compat.TypedDict, total=False):
    allocatedStorage: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::DMS::ReplicationInstance.AllocatedStorage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-allocatedstorage
    Stability:
        experimental
    """
    allowMajorVersionUpgrade: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::DMS::ReplicationInstance.AllowMajorVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-allowmajorversionupgrade
    Stability:
        experimental
    """
    autoMinorVersionUpgrade: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::DMS::ReplicationInstance.AutoMinorVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-autominorversionupgrade
    Stability:
        experimental
    """
    availabilityZone: str
    """``AWS::DMS::ReplicationInstance.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-availabilityzone
    Stability:
        experimental
    """
    engineVersion: str
    """``AWS::DMS::ReplicationInstance.EngineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-engineversion
    Stability:
        experimental
    """
    kmsKeyId: str
    """``AWS::DMS::ReplicationInstance.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-kmskeyid
    Stability:
        experimental
    """
    multiAz: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::DMS::ReplicationInstance.MultiAZ``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-multiaz
    Stability:
        experimental
    """
    preferredMaintenanceWindow: str
    """``AWS::DMS::ReplicationInstance.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-preferredmaintenancewindow
    Stability:
        experimental
    """
    publiclyAccessible: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::DMS::ReplicationInstance.PubliclyAccessible``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-publiclyaccessible
    Stability:
        experimental
    """
    replicationInstanceIdentifier: str
    """``AWS::DMS::ReplicationInstance.ReplicationInstanceIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationinstanceidentifier
    Stability:
        experimental
    """
    replicationSubnetGroupIdentifier: str
    """``AWS::DMS::ReplicationInstance.ReplicationSubnetGroupIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationsubnetgroupidentifier
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::DMS::ReplicationInstance.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-tags
    Stability:
        experimental
    """
    vpcSecurityGroupIds: typing.List[str]
    """``AWS::DMS::ReplicationInstance.VpcSecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-vpcsecuritygroupids
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnReplicationInstanceProps", jsii_struct_bases=[_CfnReplicationInstanceProps])
class CfnReplicationInstanceProps(_CfnReplicationInstanceProps):
    """Properties for defining a ``AWS::DMS::ReplicationInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html
    Stability:
        experimental
    """
    replicationInstanceClass: str
    """``AWS::DMS::ReplicationInstance.ReplicationInstanceClass``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationinstanceclass
    Stability:
        experimental
    """

class CfnReplicationSubnetGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dms.CfnReplicationSubnetGroup"):
    """A CloudFormation ``AWS::DMS::ReplicationSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DMS::ReplicationSubnetGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, replication_subnet_group_description: str, subnet_ids: typing.List[str], replication_subnet_group_identifier: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::DMS::ReplicationSubnetGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            replicationSubnetGroupDescription: ``AWS::DMS::ReplicationSubnetGroup.ReplicationSubnetGroupDescription``.
            subnetIds: ``AWS::DMS::ReplicationSubnetGroup.SubnetIds``.
            replicationSubnetGroupIdentifier: ``AWS::DMS::ReplicationSubnetGroup.ReplicationSubnetGroupIdentifier``.
            tags: ``AWS::DMS::ReplicationSubnetGroup.Tags``.

        Stability:
            experimental
        """
        props: CfnReplicationSubnetGroupProps = {"replicationSubnetGroupDescription": replication_subnet_group_description, "subnetIds": subnet_ids}

        if replication_subnet_group_identifier is not None:
            props["replicationSubnetGroupIdentifier"] = replication_subnet_group_identifier

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnReplicationSubnetGroup, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnReplicationSubnetGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="replicationSubnetGroupName")
    def replication_subnet_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "replicationSubnetGroupName")

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
class _CfnReplicationSubnetGroupProps(jsii.compat.TypedDict, total=False):
    replicationSubnetGroupIdentifier: str
    """``AWS::DMS::ReplicationSubnetGroup.ReplicationSubnetGroupIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-replicationsubnetgroupidentifier
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::DMS::ReplicationSubnetGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnReplicationSubnetGroupProps", jsii_struct_bases=[_CfnReplicationSubnetGroupProps])
class CfnReplicationSubnetGroupProps(_CfnReplicationSubnetGroupProps):
    """Properties for defining a ``AWS::DMS::ReplicationSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html
    Stability:
        experimental
    """
    replicationSubnetGroupDescription: str
    """``AWS::DMS::ReplicationSubnetGroup.ReplicationSubnetGroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-replicationsubnetgroupdescription
    Stability:
        experimental
    """

    subnetIds: typing.List[str]
    """``AWS::DMS::ReplicationSubnetGroup.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-subnetids
    Stability:
        experimental
    """

class CfnReplicationTask(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dms.CfnReplicationTask"):
    """A CloudFormation ``AWS::DMS::ReplicationTask``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DMS::ReplicationTask
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, migration_type: str, replication_instance_arn: str, source_endpoint_arn: str, table_mappings: str, target_endpoint_arn: str, cdc_start_time: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, replication_task_identifier: typing.Optional[str]=None, replication_task_settings: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::DMS::ReplicationTask``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            migrationType: ``AWS::DMS::ReplicationTask.MigrationType``.
            replicationInstanceArn: ``AWS::DMS::ReplicationTask.ReplicationInstanceArn``.
            sourceEndpointArn: ``AWS::DMS::ReplicationTask.SourceEndpointArn``.
            tableMappings: ``AWS::DMS::ReplicationTask.TableMappings``.
            targetEndpointArn: ``AWS::DMS::ReplicationTask.TargetEndpointArn``.
            cdcStartTime: ``AWS::DMS::ReplicationTask.CdcStartTime``.
            replicationTaskIdentifier: ``AWS::DMS::ReplicationTask.ReplicationTaskIdentifier``.
            replicationTaskSettings: ``AWS::DMS::ReplicationTask.ReplicationTaskSettings``.
            tags: ``AWS::DMS::ReplicationTask.Tags``.

        Stability:
            experimental
        """
        props: CfnReplicationTaskProps = {"migrationType": migration_type, "replicationInstanceArn": replication_instance_arn, "sourceEndpointArn": source_endpoint_arn, "tableMappings": table_mappings, "targetEndpointArn": target_endpoint_arn}

        if cdc_start_time is not None:
            props["cdcStartTime"] = cdc_start_time

        if replication_task_identifier is not None:
            props["replicationTaskIdentifier"] = replication_task_identifier

        if replication_task_settings is not None:
            props["replicationTaskSettings"] = replication_task_settings

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnReplicationTask, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnReplicationTaskProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="replicationTaskArn")
    def replication_task_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "replicationTaskArn")

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
class _CfnReplicationTaskProps(jsii.compat.TypedDict, total=False):
    cdcStartTime: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::DMS::ReplicationTask.CdcStartTime``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstarttime
    Stability:
        experimental
    """
    replicationTaskIdentifier: str
    """``AWS::DMS::ReplicationTask.ReplicationTaskIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationtaskidentifier
    Stability:
        experimental
    """
    replicationTaskSettings: str
    """``AWS::DMS::ReplicationTask.ReplicationTaskSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationtasksettings
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::DMS::ReplicationTask.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dms.CfnReplicationTaskProps", jsii_struct_bases=[_CfnReplicationTaskProps])
class CfnReplicationTaskProps(_CfnReplicationTaskProps):
    """Properties for defining a ``AWS::DMS::ReplicationTask``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html
    Stability:
        experimental
    """
    migrationType: str
    """``AWS::DMS::ReplicationTask.MigrationType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-migrationtype
    Stability:
        experimental
    """

    replicationInstanceArn: str
    """``AWS::DMS::ReplicationTask.ReplicationInstanceArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationinstancearn
    Stability:
        experimental
    """

    sourceEndpointArn: str
    """``AWS::DMS::ReplicationTask.SourceEndpointArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-sourceendpointarn
    Stability:
        experimental
    """

    tableMappings: str
    """``AWS::DMS::ReplicationTask.TableMappings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-tablemappings
    Stability:
        experimental
    """

    targetEndpointArn: str
    """``AWS::DMS::ReplicationTask.TargetEndpointArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-targetendpointarn
    Stability:
        experimental
    """

__all__ = ["CfnCertificate", "CfnCertificateProps", "CfnEndpoint", "CfnEndpointProps", "CfnEventSubscription", "CfnEventSubscriptionProps", "CfnReplicationInstance", "CfnReplicationInstanceProps", "CfnReplicationSubnetGroup", "CfnReplicationSubnetGroupProps", "CfnReplicationTask", "CfnReplicationTaskProps", "__jsii_assembly__"]

publication.publish()
