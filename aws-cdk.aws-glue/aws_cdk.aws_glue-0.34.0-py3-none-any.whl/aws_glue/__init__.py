import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_s3
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-glue", "0.34.0", __name__, "aws-glue@0.34.0.jsii.tgz")
class CfnClassifier(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnClassifier"):
    """A CloudFormation ``AWS::Glue::Classifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Glue::Classifier
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, csv_classifier: typing.Optional[typing.Union[typing.Optional["CsvClassifierProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None, grok_classifier: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["GrokClassifierProperty"]]]=None, json_classifier: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["JsonClassifierProperty"]]]=None, xml_classifier: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["XMLClassifierProperty"]]]=None) -> None:
        """Create a new ``AWS::Glue::Classifier``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            csvClassifier: ``AWS::Glue::Classifier.CsvClassifier``.
            grokClassifier: ``AWS::Glue::Classifier.GrokClassifier``.
            jsonClassifier: ``AWS::Glue::Classifier.JsonClassifier``.
            xmlClassifier: ``AWS::Glue::Classifier.XMLClassifier``.

        Stability:
            experimental
        """
        props: CfnClassifierProps = {}

        if csv_classifier is not None:
            props["csvClassifier"] = csv_classifier

        if grok_classifier is not None:
            props["grokClassifier"] = grok_classifier

        if json_classifier is not None:
            props["jsonClassifier"] = json_classifier

        if xml_classifier is not None:
            props["xmlClassifier"] = xml_classifier

        jsii.create(CfnClassifier, self, [scope, id, props])

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
    @jsii.member(jsii_name="classifierName")
    def classifier_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "classifierName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnClassifierProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnClassifier.CsvClassifierProperty", jsii_struct_bases=[])
    class CsvClassifierProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html
        Stability:
            experimental
        """
        allowSingleColumn: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnClassifier.CsvClassifierProperty.AllowSingleColumn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-allowsinglecolumn
        Stability:
            experimental
        """

        containsHeader: str
        """``CfnClassifier.CsvClassifierProperty.ContainsHeader``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-containsheader
        Stability:
            experimental
        """

        delimiter: str
        """``CfnClassifier.CsvClassifierProperty.Delimiter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-delimiter
        Stability:
            experimental
        """

        disableValueTrimming: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnClassifier.CsvClassifierProperty.DisableValueTrimming``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-disablevaluetrimming
        Stability:
            experimental
        """

        header: typing.List[str]
        """``CfnClassifier.CsvClassifierProperty.Header``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-header
        Stability:
            experimental
        """

        name: str
        """``CfnClassifier.CsvClassifierProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-name
        Stability:
            experimental
        """

        quoteSymbol: str
        """``CfnClassifier.CsvClassifierProperty.QuoteSymbol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-quotesymbol
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _GrokClassifierProperty(jsii.compat.TypedDict, total=False):
        customPatterns: str
        """``CfnClassifier.GrokClassifierProperty.CustomPatterns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html#cfn-glue-classifier-grokclassifier-custompatterns
        Stability:
            experimental
        """
        name: str
        """``CfnClassifier.GrokClassifierProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html#cfn-glue-classifier-grokclassifier-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnClassifier.GrokClassifierProperty", jsii_struct_bases=[_GrokClassifierProperty])
    class GrokClassifierProperty(_GrokClassifierProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html
        Stability:
            experimental
        """
        classification: str
        """``CfnClassifier.GrokClassifierProperty.Classification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html#cfn-glue-classifier-grokclassifier-classification
        Stability:
            experimental
        """

        grokPattern: str
        """``CfnClassifier.GrokClassifierProperty.GrokPattern``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html#cfn-glue-classifier-grokclassifier-grokpattern
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _JsonClassifierProperty(jsii.compat.TypedDict, total=False):
        name: str
        """``CfnClassifier.JsonClassifierProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-jsonclassifier.html#cfn-glue-classifier-jsonclassifier-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnClassifier.JsonClassifierProperty", jsii_struct_bases=[_JsonClassifierProperty])
    class JsonClassifierProperty(_JsonClassifierProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-jsonclassifier.html
        Stability:
            experimental
        """
        jsonPath: str
        """``CfnClassifier.JsonClassifierProperty.JsonPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-jsonclassifier.html#cfn-glue-classifier-jsonclassifier-jsonpath
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _XMLClassifierProperty(jsii.compat.TypedDict, total=False):
        name: str
        """``CfnClassifier.XMLClassifierProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-xmlclassifier.html#cfn-glue-classifier-xmlclassifier-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnClassifier.XMLClassifierProperty", jsii_struct_bases=[_XMLClassifierProperty])
    class XMLClassifierProperty(_XMLClassifierProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-xmlclassifier.html
        Stability:
            experimental
        """
        classification: str
        """``CfnClassifier.XMLClassifierProperty.Classification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-xmlclassifier.html#cfn-glue-classifier-xmlclassifier-classification
        Stability:
            experimental
        """

        rowTag: str
        """``CfnClassifier.XMLClassifierProperty.RowTag``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-xmlclassifier.html#cfn-glue-classifier-xmlclassifier-rowtag
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnClassifierProps", jsii_struct_bases=[])
class CfnClassifierProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::Glue::Classifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html
    Stability:
        experimental
    """
    csvClassifier: typing.Union["CfnClassifier.CsvClassifierProperty", aws_cdk.cdk.Token]
    """``AWS::Glue::Classifier.CsvClassifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-csvclassifier
    Stability:
        experimental
    """

    grokClassifier: typing.Union[aws_cdk.cdk.Token, "CfnClassifier.GrokClassifierProperty"]
    """``AWS::Glue::Classifier.GrokClassifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-grokclassifier
    Stability:
        experimental
    """

    jsonClassifier: typing.Union[aws_cdk.cdk.Token, "CfnClassifier.JsonClassifierProperty"]
    """``AWS::Glue::Classifier.JsonClassifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-jsonclassifier
    Stability:
        experimental
    """

    xmlClassifier: typing.Union[aws_cdk.cdk.Token, "CfnClassifier.XMLClassifierProperty"]
    """``AWS::Glue::Classifier.XMLClassifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-xmlclassifier
    Stability:
        experimental
    """

class CfnConnection(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnConnection"):
    """A CloudFormation ``AWS::Glue::Connection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Glue::Connection
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, catalog_id: str, connection_input: typing.Union[aws_cdk.cdk.Token, "ConnectionInputProperty"]) -> None:
        """Create a new ``AWS::Glue::Connection``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            catalogId: ``AWS::Glue::Connection.CatalogId``.
            connectionInput: ``AWS::Glue::Connection.ConnectionInput``.

        Stability:
            experimental
        """
        props: CfnConnectionProps = {"catalogId": catalog_id, "connectionInput": connection_input}

        jsii.create(CfnConnection, self, [scope, id, props])

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
    @jsii.member(jsii_name="connectionName")
    def connection_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "connectionName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnConnectionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ConnectionInputProperty(jsii.compat.TypedDict, total=False):
        description: str
        """``CfnConnection.ConnectionInputProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-description
        Stability:
            experimental
        """
        matchCriteria: typing.List[str]
        """``CfnConnection.ConnectionInputProperty.MatchCriteria``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-matchcriteria
        Stability:
            experimental
        """
        name: str
        """``CfnConnection.ConnectionInputProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-name
        Stability:
            experimental
        """
        physicalConnectionRequirements: typing.Union[aws_cdk.cdk.Token, "CfnConnection.PhysicalConnectionRequirementsProperty"]
        """``CfnConnection.ConnectionInputProperty.PhysicalConnectionRequirements``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-physicalconnectionrequirements
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnConnection.ConnectionInputProperty", jsii_struct_bases=[_ConnectionInputProperty])
    class ConnectionInputProperty(_ConnectionInputProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html
        Stability:
            experimental
        """
        connectionProperties: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnConnection.ConnectionInputProperty.ConnectionProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-connectionproperties
        Stability:
            experimental
        """

        connectionType: str
        """``CfnConnection.ConnectionInputProperty.ConnectionType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-connectiontype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnConnection.PhysicalConnectionRequirementsProperty", jsii_struct_bases=[])
    class PhysicalConnectionRequirementsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-physicalconnectionrequirements.html
        Stability:
            experimental
        """
        availabilityZone: str
        """``CfnConnection.PhysicalConnectionRequirementsProperty.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-physicalconnectionrequirements.html#cfn-glue-connection-physicalconnectionrequirements-availabilityzone
        Stability:
            experimental
        """

        securityGroupIdList: typing.List[str]
        """``CfnConnection.PhysicalConnectionRequirementsProperty.SecurityGroupIdList``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-physicalconnectionrequirements.html#cfn-glue-connection-physicalconnectionrequirements-securitygroupidlist
        Stability:
            experimental
        """

        subnetId: str
        """``CfnConnection.PhysicalConnectionRequirementsProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-physicalconnectionrequirements.html#cfn-glue-connection-physicalconnectionrequirements-subnetid
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnConnectionProps", jsii_struct_bases=[])
class CfnConnectionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Glue::Connection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html
    Stability:
        experimental
    """
    catalogId: str
    """``AWS::Glue::Connection.CatalogId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html#cfn-glue-connection-catalogid
    Stability:
        experimental
    """

    connectionInput: typing.Union[aws_cdk.cdk.Token, "CfnConnection.ConnectionInputProperty"]
    """``AWS::Glue::Connection.ConnectionInput``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html#cfn-glue-connection-connectioninput
    Stability:
        experimental
    """

class CfnCrawler(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnCrawler"):
    """A CloudFormation ``AWS::Glue::Crawler``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Glue::Crawler
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, database_name: str, role: str, targets: typing.Union[aws_cdk.cdk.Token, "TargetsProperty"], classifiers: typing.Optional[typing.List[str]]=None, configuration: typing.Optional[str]=None, crawler_security_configuration: typing.Optional[str]=None, description: typing.Optional[str]=None, name: typing.Optional[str]=None, schedule: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ScheduleProperty"]]]=None, schema_change_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["SchemaChangePolicyProperty"]]]=None, table_prefix: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[typing.Any, typing.Any]]=None) -> None:
        """Create a new ``AWS::Glue::Crawler``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            databaseName: ``AWS::Glue::Crawler.DatabaseName``.
            role: ``AWS::Glue::Crawler.Role``.
            targets: ``AWS::Glue::Crawler.Targets``.
            classifiers: ``AWS::Glue::Crawler.Classifiers``.
            configuration: ``AWS::Glue::Crawler.Configuration``.
            crawlerSecurityConfiguration: ``AWS::Glue::Crawler.CrawlerSecurityConfiguration``.
            description: ``AWS::Glue::Crawler.Description``.
            name: ``AWS::Glue::Crawler.Name``.
            schedule: ``AWS::Glue::Crawler.Schedule``.
            schemaChangePolicy: ``AWS::Glue::Crawler.SchemaChangePolicy``.
            tablePrefix: ``AWS::Glue::Crawler.TablePrefix``.
            tags: ``AWS::Glue::Crawler.Tags``.

        Stability:
            experimental
        """
        props: CfnCrawlerProps = {"databaseName": database_name, "role": role, "targets": targets}

        if classifiers is not None:
            props["classifiers"] = classifiers

        if configuration is not None:
            props["configuration"] = configuration

        if crawler_security_configuration is not None:
            props["crawlerSecurityConfiguration"] = crawler_security_configuration

        if description is not None:
            props["description"] = description

        if name is not None:
            props["name"] = name

        if schedule is not None:
            props["schedule"] = schedule

        if schema_change_policy is not None:
            props["schemaChangePolicy"] = schema_change_policy

        if table_prefix is not None:
            props["tablePrefix"] = table_prefix

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnCrawler, self, [scope, id, props])

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
    @jsii.member(jsii_name="crawlerName")
    def crawler_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "crawlerName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnCrawlerProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnCrawler.JdbcTargetProperty", jsii_struct_bases=[])
    class JdbcTargetProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-jdbctarget.html
        Stability:
            experimental
        """
        connectionName: str
        """``CfnCrawler.JdbcTargetProperty.ConnectionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-jdbctarget.html#cfn-glue-crawler-jdbctarget-connectionname
        Stability:
            experimental
        """

        exclusions: typing.List[str]
        """``CfnCrawler.JdbcTargetProperty.Exclusions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-jdbctarget.html#cfn-glue-crawler-jdbctarget-exclusions
        Stability:
            experimental
        """

        path: str
        """``CfnCrawler.JdbcTargetProperty.Path``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-jdbctarget.html#cfn-glue-crawler-jdbctarget-path
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnCrawler.S3TargetProperty", jsii_struct_bases=[])
    class S3TargetProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-s3target.html
        Stability:
            experimental
        """
        exclusions: typing.List[str]
        """``CfnCrawler.S3TargetProperty.Exclusions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-s3target.html#cfn-glue-crawler-s3target-exclusions
        Stability:
            experimental
        """

        path: str
        """``CfnCrawler.S3TargetProperty.Path``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-s3target.html#cfn-glue-crawler-s3target-path
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnCrawler.ScheduleProperty", jsii_struct_bases=[])
    class ScheduleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schedule.html
        Stability:
            experimental
        """
        scheduleExpression: str
        """``CfnCrawler.ScheduleProperty.ScheduleExpression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schedule.html#cfn-glue-crawler-schedule-scheduleexpression
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnCrawler.SchemaChangePolicyProperty", jsii_struct_bases=[])
    class SchemaChangePolicyProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schemachangepolicy.html
        Stability:
            experimental
        """
        deleteBehavior: str
        """``CfnCrawler.SchemaChangePolicyProperty.DeleteBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schemachangepolicy.html#cfn-glue-crawler-schemachangepolicy-deletebehavior
        Stability:
            experimental
        """

        updateBehavior: str
        """``CfnCrawler.SchemaChangePolicyProperty.UpdateBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schemachangepolicy.html#cfn-glue-crawler-schemachangepolicy-updatebehavior
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnCrawler.TargetsProperty", jsii_struct_bases=[])
    class TargetsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-targets.html
        Stability:
            experimental
        """
        jdbcTargets: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnCrawler.JdbcTargetProperty"]]]
        """``CfnCrawler.TargetsProperty.JdbcTargets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-targets.html#cfn-glue-crawler-targets-jdbctargets
        Stability:
            experimental
        """

        s3Targets: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnCrawler.S3TargetProperty"]]]
        """``CfnCrawler.TargetsProperty.S3Targets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-targets.html#cfn-glue-crawler-targets-s3targets
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnCrawlerProps(jsii.compat.TypedDict, total=False):
    classifiers: typing.List[str]
    """``AWS::Glue::Crawler.Classifiers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-classifiers
    Stability:
        experimental
    """
    configuration: str
    """``AWS::Glue::Crawler.Configuration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-configuration
    Stability:
        experimental
    """
    crawlerSecurityConfiguration: str
    """``AWS::Glue::Crawler.CrawlerSecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-crawlersecurityconfiguration
    Stability:
        experimental
    """
    description: str
    """``AWS::Glue::Crawler.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-description
    Stability:
        experimental
    """
    name: str
    """``AWS::Glue::Crawler.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-name
    Stability:
        experimental
    """
    schedule: typing.Union[aws_cdk.cdk.Token, "CfnCrawler.ScheduleProperty"]
    """``AWS::Glue::Crawler.Schedule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-schedule
    Stability:
        experimental
    """
    schemaChangePolicy: typing.Union[aws_cdk.cdk.Token, "CfnCrawler.SchemaChangePolicyProperty"]
    """``AWS::Glue::Crawler.SchemaChangePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-schemachangepolicy
    Stability:
        experimental
    """
    tablePrefix: str
    """``AWS::Glue::Crawler.TablePrefix``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-tableprefix
    Stability:
        experimental
    """
    tags: typing.Mapping[typing.Any, typing.Any]
    """``AWS::Glue::Crawler.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnCrawlerProps", jsii_struct_bases=[_CfnCrawlerProps])
class CfnCrawlerProps(_CfnCrawlerProps):
    """Properties for defining a ``AWS::Glue::Crawler``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html
    Stability:
        experimental
    """
    databaseName: str
    """``AWS::Glue::Crawler.DatabaseName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-databasename
    Stability:
        experimental
    """

    role: str
    """``AWS::Glue::Crawler.Role``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-role
    Stability:
        experimental
    """

    targets: typing.Union[aws_cdk.cdk.Token, "CfnCrawler.TargetsProperty"]
    """``AWS::Glue::Crawler.Targets``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-targets
    Stability:
        experimental
    """

class CfnDataCatalogEncryptionSettings(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnDataCatalogEncryptionSettings"):
    """A CloudFormation ``AWS::Glue::DataCatalogEncryptionSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Glue::DataCatalogEncryptionSettings
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, catalog_id: str, data_catalog_encryption_settings: typing.Union[aws_cdk.cdk.Token, "DataCatalogEncryptionSettingsProperty"]) -> None:
        """Create a new ``AWS::Glue::DataCatalogEncryptionSettings``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            catalogId: ``AWS::Glue::DataCatalogEncryptionSettings.CatalogId``.
            dataCatalogEncryptionSettings: ``AWS::Glue::DataCatalogEncryptionSettings.DataCatalogEncryptionSettings``.

        Stability:
            experimental
        """
        props: CfnDataCatalogEncryptionSettingsProps = {"catalogId": catalog_id, "dataCatalogEncryptionSettings": data_catalog_encryption_settings}

        jsii.create(CfnDataCatalogEncryptionSettings, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnDataCatalogEncryptionSettingsProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty", jsii_struct_bases=[])
    class ConnectionPasswordEncryptionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-connectionpasswordencryption.html
        Stability:
            experimental
        """
        kmsKeyId: str
        """``CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-connectionpasswordencryption.html#cfn-glue-datacatalogencryptionsettings-connectionpasswordencryption-kmskeyid
        Stability:
            experimental
        """

        returnConnectionPasswordEncrypted: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty.ReturnConnectionPasswordEncrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-connectionpasswordencryption.html#cfn-glue-datacatalogencryptionsettings-connectionpasswordencryption-returnconnectionpasswordencrypted
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty", jsii_struct_bases=[])
    class DataCatalogEncryptionSettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-datacatalogencryptionsettings.html
        Stability:
            experimental
        """
        connectionPasswordEncryption: typing.Union[aws_cdk.cdk.Token, "CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty"]
        """``CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty.ConnectionPasswordEncryption``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-datacatalogencryptionsettings-connectionpasswordencryption
        Stability:
            experimental
        """

        encryptionAtRest: typing.Union[aws_cdk.cdk.Token, "CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty"]
        """``CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty.EncryptionAtRest``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-datacatalogencryptionsettings-encryptionatrest
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty", jsii_struct_bases=[])
    class EncryptionAtRestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-encryptionatrest.html
        Stability:
            experimental
        """
        catalogEncryptionMode: str
        """``CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty.CatalogEncryptionMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-encryptionatrest.html#cfn-glue-datacatalogencryptionsettings-encryptionatrest-catalogencryptionmode
        Stability:
            experimental
        """

        sseAwsKmsKeyId: str
        """``CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty.SseAwsKmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-encryptionatrest.html#cfn-glue-datacatalogencryptionsettings-encryptionatrest-sseawskmskeyid
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDataCatalogEncryptionSettingsProps", jsii_struct_bases=[])
class CfnDataCatalogEncryptionSettingsProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Glue::DataCatalogEncryptionSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html
    Stability:
        experimental
    """
    catalogId: str
    """``AWS::Glue::DataCatalogEncryptionSettings.CatalogId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-catalogid
    Stability:
        experimental
    """

    dataCatalogEncryptionSettings: typing.Union[aws_cdk.cdk.Token, "CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty"]
    """``AWS::Glue::DataCatalogEncryptionSettings.DataCatalogEncryptionSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-datacatalogencryptionsettings
    Stability:
        experimental
    """

class CfnDatabase(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnDatabase"):
    """A CloudFormation ``AWS::Glue::Database``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Glue::Database
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, catalog_id: str, database_input: typing.Union[aws_cdk.cdk.Token, "DatabaseInputProperty"]) -> None:
        """Create a new ``AWS::Glue::Database``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            catalogId: ``AWS::Glue::Database.CatalogId``.
            databaseInput: ``AWS::Glue::Database.DatabaseInput``.

        Stability:
            experimental
        """
        props: CfnDatabaseProps = {"catalogId": catalog_id, "databaseInput": database_input}

        jsii.create(CfnDatabase, self, [scope, id, props])

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
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "databaseName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDatabaseProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDatabase.DatabaseInputProperty", jsii_struct_bases=[])
    class DatabaseInputProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html
        Stability:
            experimental
        """
        description: str
        """``CfnDatabase.DatabaseInputProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-description
        Stability:
            experimental
        """

        locationUri: str
        """``CfnDatabase.DatabaseInputProperty.LocationUri``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-locationuri
        Stability:
            experimental
        """

        name: str
        """``CfnDatabase.DatabaseInputProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-name
        Stability:
            experimental
        """

        parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnDatabase.DatabaseInputProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-parameters
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDatabaseProps", jsii_struct_bases=[])
class CfnDatabaseProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Glue::Database``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html
    Stability:
        experimental
    """
    catalogId: str
    """``AWS::Glue::Database.CatalogId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html#cfn-glue-database-catalogid
    Stability:
        experimental
    """

    databaseInput: typing.Union[aws_cdk.cdk.Token, "CfnDatabase.DatabaseInputProperty"]
    """``AWS::Glue::Database.DatabaseInput``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html#cfn-glue-database-databaseinput
    Stability:
        experimental
    """

class CfnDevEndpoint(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnDevEndpoint"):
    """A CloudFormation ``AWS::Glue::DevEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Glue::DevEndpoint
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, role_arn: str, endpoint_name: typing.Optional[str]=None, extra_jars_s3_path: typing.Optional[str]=None, extra_python_libs_s3_path: typing.Optional[str]=None, number_of_nodes: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, public_key: typing.Optional[str]=None, security_configuration: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, subnet_id: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[typing.Any, typing.Any]]=None) -> None:
        """Create a new ``AWS::Glue::DevEndpoint``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            roleArn: ``AWS::Glue::DevEndpoint.RoleArn``.
            endpointName: ``AWS::Glue::DevEndpoint.EndpointName``.
            extraJarsS3Path: ``AWS::Glue::DevEndpoint.ExtraJarsS3Path``.
            extraPythonLibsS3Path: ``AWS::Glue::DevEndpoint.ExtraPythonLibsS3Path``.
            numberOfNodes: ``AWS::Glue::DevEndpoint.NumberOfNodes``.
            publicKey: ``AWS::Glue::DevEndpoint.PublicKey``.
            securityConfiguration: ``AWS::Glue::DevEndpoint.SecurityConfiguration``.
            securityGroupIds: ``AWS::Glue::DevEndpoint.SecurityGroupIds``.
            subnetId: ``AWS::Glue::DevEndpoint.SubnetId``.
            tags: ``AWS::Glue::DevEndpoint.Tags``.

        Stability:
            experimental
        """
        props: CfnDevEndpointProps = {"roleArn": role_arn}

        if endpoint_name is not None:
            props["endpointName"] = endpoint_name

        if extra_jars_s3_path is not None:
            props["extraJarsS3Path"] = extra_jars_s3_path

        if extra_python_libs_s3_path is not None:
            props["extraPythonLibsS3Path"] = extra_python_libs_s3_path

        if number_of_nodes is not None:
            props["numberOfNodes"] = number_of_nodes

        if public_key is not None:
            props["publicKey"] = public_key

        if security_configuration is not None:
            props["securityConfiguration"] = security_configuration

        if security_group_ids is not None:
            props["securityGroupIds"] = security_group_ids

        if subnet_id is not None:
            props["subnetId"] = subnet_id

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnDevEndpoint, self, [scope, id, props])

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
    @jsii.member(jsii_name="devEndpointId")
    def dev_endpoint_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "devEndpointId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDevEndpointProps":
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
class _CfnDevEndpointProps(jsii.compat.TypedDict, total=False):
    endpointName: str
    """``AWS::Glue::DevEndpoint.EndpointName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-endpointname
    Stability:
        experimental
    """
    extraJarsS3Path: str
    """``AWS::Glue::DevEndpoint.ExtraJarsS3Path``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-extrajarss3path
    Stability:
        experimental
    """
    extraPythonLibsS3Path: str
    """``AWS::Glue::DevEndpoint.ExtraPythonLibsS3Path``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-extrapythonlibss3path
    Stability:
        experimental
    """
    numberOfNodes: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Glue::DevEndpoint.NumberOfNodes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-numberofnodes
    Stability:
        experimental
    """
    publicKey: str
    """``AWS::Glue::DevEndpoint.PublicKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-publickey
    Stability:
        experimental
    """
    securityConfiguration: str
    """``AWS::Glue::DevEndpoint.SecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-securityconfiguration
    Stability:
        experimental
    """
    securityGroupIds: typing.List[str]
    """``AWS::Glue::DevEndpoint.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-securitygroupids
    Stability:
        experimental
    """
    subnetId: str
    """``AWS::Glue::DevEndpoint.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-subnetid
    Stability:
        experimental
    """
    tags: typing.Mapping[typing.Any, typing.Any]
    """``AWS::Glue::DevEndpoint.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDevEndpointProps", jsii_struct_bases=[_CfnDevEndpointProps])
class CfnDevEndpointProps(_CfnDevEndpointProps):
    """Properties for defining a ``AWS::Glue::DevEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html
    Stability:
        experimental
    """
    roleArn: str
    """``AWS::Glue::DevEndpoint.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-rolearn
    Stability:
        experimental
    """

class CfnJob(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnJob"):
    """A CloudFormation ``AWS::Glue::Job``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Glue::Job
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, command: typing.Union[aws_cdk.cdk.Token, "JobCommandProperty"], role: str, allocated_capacity: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, connections: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ConnectionsListProperty"]]]=None, default_arguments: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, description: typing.Optional[str]=None, execution_property: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ExecutionPropertyProperty"]]]=None, log_uri: typing.Optional[str]=None, max_retries: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, name: typing.Optional[str]=None, security_configuration: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[typing.Any, typing.Any]]=None) -> None:
        """Create a new ``AWS::Glue::Job``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            command: ``AWS::Glue::Job.Command``.
            role: ``AWS::Glue::Job.Role``.
            allocatedCapacity: ``AWS::Glue::Job.AllocatedCapacity``.
            connections: ``AWS::Glue::Job.Connections``.
            defaultArguments: ``AWS::Glue::Job.DefaultArguments``.
            description: ``AWS::Glue::Job.Description``.
            executionProperty: ``AWS::Glue::Job.ExecutionProperty``.
            logUri: ``AWS::Glue::Job.LogUri``.
            maxRetries: ``AWS::Glue::Job.MaxRetries``.
            name: ``AWS::Glue::Job.Name``.
            securityConfiguration: ``AWS::Glue::Job.SecurityConfiguration``.
            tags: ``AWS::Glue::Job.Tags``.

        Stability:
            experimental
        """
        props: CfnJobProps = {"command": command, "role": role}

        if allocated_capacity is not None:
            props["allocatedCapacity"] = allocated_capacity

        if connections is not None:
            props["connections"] = connections

        if default_arguments is not None:
            props["defaultArguments"] = default_arguments

        if description is not None:
            props["description"] = description

        if execution_property is not None:
            props["executionProperty"] = execution_property

        if log_uri is not None:
            props["logUri"] = log_uri

        if max_retries is not None:
            props["maxRetries"] = max_retries

        if name is not None:
            props["name"] = name

        if security_configuration is not None:
            props["securityConfiguration"] = security_configuration

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnJob, self, [scope, id, props])

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
    @jsii.member(jsii_name="jobName")
    def job_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "jobName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnJobProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnJob.ConnectionsListProperty", jsii_struct_bases=[])
    class ConnectionsListProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-connectionslist.html
        Stability:
            experimental
        """
        connections: typing.List[str]
        """``CfnJob.ConnectionsListProperty.Connections``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-connectionslist.html#cfn-glue-job-connectionslist-connections
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnJob.ExecutionPropertyProperty", jsii_struct_bases=[])
    class ExecutionPropertyProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-executionproperty.html
        Stability:
            experimental
        """
        maxConcurrentRuns: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnJob.ExecutionPropertyProperty.MaxConcurrentRuns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-executionproperty.html#cfn-glue-job-executionproperty-maxconcurrentruns
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnJob.JobCommandProperty", jsii_struct_bases=[])
    class JobCommandProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-jobcommand.html
        Stability:
            experimental
        """
        name: str
        """``CfnJob.JobCommandProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-jobcommand.html#cfn-glue-job-jobcommand-name
        Stability:
            experimental
        """

        scriptLocation: str
        """``CfnJob.JobCommandProperty.ScriptLocation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-jobcommand.html#cfn-glue-job-jobcommand-scriptlocation
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnJobProps(jsii.compat.TypedDict, total=False):
    allocatedCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Glue::Job.AllocatedCapacity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-allocatedcapacity
    Stability:
        experimental
    """
    connections: typing.Union[aws_cdk.cdk.Token, "CfnJob.ConnectionsListProperty"]
    """``AWS::Glue::Job.Connections``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-connections
    Stability:
        experimental
    """
    defaultArguments: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::Glue::Job.DefaultArguments``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-defaultarguments
    Stability:
        experimental
    """
    description: str
    """``AWS::Glue::Job.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-description
    Stability:
        experimental
    """
    executionProperty: typing.Union[aws_cdk.cdk.Token, "CfnJob.ExecutionPropertyProperty"]
    """``AWS::Glue::Job.ExecutionProperty``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-executionproperty
    Stability:
        experimental
    """
    logUri: str
    """``AWS::Glue::Job.LogUri``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-loguri
    Stability:
        experimental
    """
    maxRetries: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Glue::Job.MaxRetries``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-maxretries
    Stability:
        experimental
    """
    name: str
    """``AWS::Glue::Job.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-name
    Stability:
        experimental
    """
    securityConfiguration: str
    """``AWS::Glue::Job.SecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-securityconfiguration
    Stability:
        experimental
    """
    tags: typing.Mapping[typing.Any, typing.Any]
    """``AWS::Glue::Job.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnJobProps", jsii_struct_bases=[_CfnJobProps])
class CfnJobProps(_CfnJobProps):
    """Properties for defining a ``AWS::Glue::Job``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html
    Stability:
        experimental
    """
    command: typing.Union[aws_cdk.cdk.Token, "CfnJob.JobCommandProperty"]
    """``AWS::Glue::Job.Command``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-command
    Stability:
        experimental
    """

    role: str
    """``AWS::Glue::Job.Role``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-role
    Stability:
        experimental
    """

class CfnPartition(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnPartition"):
    """A CloudFormation ``AWS::Glue::Partition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Glue::Partition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, catalog_id: str, database_name: str, partition_input: typing.Union[aws_cdk.cdk.Token, "PartitionInputProperty"], table_name: str) -> None:
        """Create a new ``AWS::Glue::Partition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            catalogId: ``AWS::Glue::Partition.CatalogId``.
            databaseName: ``AWS::Glue::Partition.DatabaseName``.
            partitionInput: ``AWS::Glue::Partition.PartitionInput``.
            tableName: ``AWS::Glue::Partition.TableName``.

        Stability:
            experimental
        """
        props: CfnPartitionProps = {"catalogId": catalog_id, "databaseName": database_name, "partitionInput": partition_input, "tableName": table_name}

        jsii.create(CfnPartition, self, [scope, id, props])

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
    @jsii.member(jsii_name="partitionId")
    def partition_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "partitionId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnPartitionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ColumnProperty(jsii.compat.TypedDict, total=False):
        comment: str
        """``CfnPartition.ColumnProperty.Comment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-column.html#cfn-glue-partition-column-comment
        Stability:
            experimental
        """
        type: str
        """``CfnPartition.ColumnProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-column.html#cfn-glue-partition-column-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartition.ColumnProperty", jsii_struct_bases=[_ColumnProperty])
    class ColumnProperty(_ColumnProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-column.html
        Stability:
            experimental
        """
        name: str
        """``CfnPartition.ColumnProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-column.html#cfn-glue-partition-column-name
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _OrderProperty(jsii.compat.TypedDict, total=False):
        sortOrder: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnPartition.OrderProperty.SortOrder``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-order.html#cfn-glue-partition-order-sortorder
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartition.OrderProperty", jsii_struct_bases=[_OrderProperty])
    class OrderProperty(_OrderProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-order.html
        Stability:
            experimental
        """
        column: str
        """``CfnPartition.OrderProperty.Column``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-order.html#cfn-glue-partition-order-column
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _PartitionInputProperty(jsii.compat.TypedDict, total=False):
        parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnPartition.PartitionInputProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-partitioninput.html#cfn-glue-partition-partitioninput-parameters
        Stability:
            experimental
        """
        storageDescriptor: typing.Union[aws_cdk.cdk.Token, "CfnPartition.StorageDescriptorProperty"]
        """``CfnPartition.PartitionInputProperty.StorageDescriptor``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-partitioninput.html#cfn-glue-partition-partitioninput-storagedescriptor
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartition.PartitionInputProperty", jsii_struct_bases=[_PartitionInputProperty])
    class PartitionInputProperty(_PartitionInputProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-partitioninput.html
        Stability:
            experimental
        """
        values: typing.List[str]
        """``CfnPartition.PartitionInputProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-partitioninput.html#cfn-glue-partition-partitioninput-values
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartition.SerdeInfoProperty", jsii_struct_bases=[])
    class SerdeInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-serdeinfo.html
        Stability:
            experimental
        """
        name: str
        """``CfnPartition.SerdeInfoProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-serdeinfo.html#cfn-glue-partition-serdeinfo-name
        Stability:
            experimental
        """

        parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnPartition.SerdeInfoProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-serdeinfo.html#cfn-glue-partition-serdeinfo-parameters
        Stability:
            experimental
        """

        serializationLibrary: str
        """``CfnPartition.SerdeInfoProperty.SerializationLibrary``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-serdeinfo.html#cfn-glue-partition-serdeinfo-serializationlibrary
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartition.SkewedInfoProperty", jsii_struct_bases=[])
    class SkewedInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-skewedinfo.html
        Stability:
            experimental
        """
        skewedColumnNames: typing.List[str]
        """``CfnPartition.SkewedInfoProperty.SkewedColumnNames``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-skewedinfo.html#cfn-glue-partition-skewedinfo-skewedcolumnnames
        Stability:
            experimental
        """

        skewedColumnValueLocationMaps: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnPartition.SkewedInfoProperty.SkewedColumnValueLocationMaps``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-skewedinfo.html#cfn-glue-partition-skewedinfo-skewedcolumnvaluelocationmaps
        Stability:
            experimental
        """

        skewedColumnValues: typing.List[str]
        """``CfnPartition.SkewedInfoProperty.SkewedColumnValues``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-skewedinfo.html#cfn-glue-partition-skewedinfo-skewedcolumnvalues
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartition.StorageDescriptorProperty", jsii_struct_bases=[])
    class StorageDescriptorProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html
        Stability:
            experimental
        """
        bucketColumns: typing.List[str]
        """``CfnPartition.StorageDescriptorProperty.BucketColumns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-bucketcolumns
        Stability:
            experimental
        """

        columns: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPartition.ColumnProperty"]]]
        """``CfnPartition.StorageDescriptorProperty.Columns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-columns
        Stability:
            experimental
        """

        compressed: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnPartition.StorageDescriptorProperty.Compressed``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-compressed
        Stability:
            experimental
        """

        inputFormat: str
        """``CfnPartition.StorageDescriptorProperty.InputFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-inputformat
        Stability:
            experimental
        """

        location: str
        """``CfnPartition.StorageDescriptorProperty.Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-location
        Stability:
            experimental
        """

        numberOfBuckets: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnPartition.StorageDescriptorProperty.NumberOfBuckets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-numberofbuckets
        Stability:
            experimental
        """

        outputFormat: str
        """``CfnPartition.StorageDescriptorProperty.OutputFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-outputformat
        Stability:
            experimental
        """

        parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnPartition.StorageDescriptorProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-parameters
        Stability:
            experimental
        """

        serdeInfo: typing.Union[aws_cdk.cdk.Token, "CfnPartition.SerdeInfoProperty"]
        """``CfnPartition.StorageDescriptorProperty.SerdeInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-serdeinfo
        Stability:
            experimental
        """

        skewedInfo: typing.Union[aws_cdk.cdk.Token, "CfnPartition.SkewedInfoProperty"]
        """``CfnPartition.StorageDescriptorProperty.SkewedInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-skewedinfo
        Stability:
            experimental
        """

        sortColumns: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnPartition.OrderProperty"]]]
        """``CfnPartition.StorageDescriptorProperty.SortColumns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-sortcolumns
        Stability:
            experimental
        """

        storedAsSubDirectories: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnPartition.StorageDescriptorProperty.StoredAsSubDirectories``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-storedassubdirectories
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartitionProps", jsii_struct_bases=[])
class CfnPartitionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Glue::Partition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html
    Stability:
        experimental
    """
    catalogId: str
    """``AWS::Glue::Partition.CatalogId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-catalogid
    Stability:
        experimental
    """

    databaseName: str
    """``AWS::Glue::Partition.DatabaseName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-databasename
    Stability:
        experimental
    """

    partitionInput: typing.Union[aws_cdk.cdk.Token, "CfnPartition.PartitionInputProperty"]
    """``AWS::Glue::Partition.PartitionInput``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-partitioninput
    Stability:
        experimental
    """

    tableName: str
    """``AWS::Glue::Partition.TableName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-tablename
    Stability:
        experimental
    """

class CfnSecurityConfiguration(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnSecurityConfiguration"):
    """A CloudFormation ``AWS::Glue::SecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Glue::SecurityConfiguration
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, encryption_configuration: typing.Union[aws_cdk.cdk.Token, "EncryptionConfigurationProperty"], name: str) -> None:
        """Create a new ``AWS::Glue::SecurityConfiguration``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            encryptionConfiguration: ``AWS::Glue::SecurityConfiguration.EncryptionConfiguration``.
            name: ``AWS::Glue::SecurityConfiguration.Name``.

        Stability:
            experimental
        """
        props: CfnSecurityConfigurationProps = {"encryptionConfiguration": encryption_configuration, "name": name}

        jsii.create(CfnSecurityConfiguration, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSecurityConfigurationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="securityConfigurationName")
    def security_configuration_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "securityConfigurationName")

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnSecurityConfiguration.CloudWatchEncryptionProperty", jsii_struct_bases=[])
    class CloudWatchEncryptionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-cloudwatchencryption.html
        Stability:
            experimental
        """
        cloudWatchEncryptionMode: str
        """``CfnSecurityConfiguration.CloudWatchEncryptionProperty.CloudWatchEncryptionMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-cloudwatchencryption.html#cfn-glue-securityconfiguration-cloudwatchencryption-cloudwatchencryptionmode
        Stability:
            experimental
        """

        kmsKeyArn: str
        """``CfnSecurityConfiguration.CloudWatchEncryptionProperty.KmsKeyArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-cloudwatchencryption.html#cfn-glue-securityconfiguration-cloudwatchencryption-kmskeyarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnSecurityConfiguration.EncryptionConfigurationProperty", jsii_struct_bases=[])
    class EncryptionConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-encryptionconfiguration.html
        Stability:
            experimental
        """
        cloudWatchEncryption: typing.Union[aws_cdk.cdk.Token, "CfnSecurityConfiguration.CloudWatchEncryptionProperty"]
        """``CfnSecurityConfiguration.EncryptionConfigurationProperty.CloudWatchEncryption``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-encryptionconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration-cloudwatchencryption
        Stability:
            experimental
        """

        jobBookmarksEncryption: typing.Union[aws_cdk.cdk.Token, "CfnSecurityConfiguration.JobBookmarksEncryptionProperty"]
        """``CfnSecurityConfiguration.EncryptionConfigurationProperty.JobBookmarksEncryption``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-encryptionconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration-jobbookmarksencryption
        Stability:
            experimental
        """

        s3Encryptions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnSecurityConfiguration.S3EncryptionProperty"]]]
        """``CfnSecurityConfiguration.EncryptionConfigurationProperty.S3Encryptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-encryptionconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration-s3encryptions
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnSecurityConfiguration.JobBookmarksEncryptionProperty", jsii_struct_bases=[])
    class JobBookmarksEncryptionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-jobbookmarksencryption.html
        Stability:
            experimental
        """
        jobBookmarksEncryptionMode: str
        """``CfnSecurityConfiguration.JobBookmarksEncryptionProperty.JobBookmarksEncryptionMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-jobbookmarksencryption.html#cfn-glue-securityconfiguration-jobbookmarksencryption-jobbookmarksencryptionmode
        Stability:
            experimental
        """

        kmsKeyArn: str
        """``CfnSecurityConfiguration.JobBookmarksEncryptionProperty.KmsKeyArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-jobbookmarksencryption.html#cfn-glue-securityconfiguration-jobbookmarksencryption-kmskeyarn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnSecurityConfiguration.S3EncryptionProperty", jsii_struct_bases=[])
    class S3EncryptionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-s3encryption.html
        Stability:
            experimental
        """
        kmsKeyArn: str
        """``CfnSecurityConfiguration.S3EncryptionProperty.KmsKeyArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-s3encryption.html#cfn-glue-securityconfiguration-s3encryption-kmskeyarn
        Stability:
            experimental
        """

        s3EncryptionMode: str
        """``CfnSecurityConfiguration.S3EncryptionProperty.S3EncryptionMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-s3encryption.html#cfn-glue-securityconfiguration-s3encryption-s3encryptionmode
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnSecurityConfigurationProps", jsii_struct_bases=[])
class CfnSecurityConfigurationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Glue::SecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html
    Stability:
        experimental
    """
    encryptionConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnSecurityConfiguration.EncryptionConfigurationProperty"]
    """``AWS::Glue::SecurityConfiguration.EncryptionConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration
    Stability:
        experimental
    """

    name: str
    """``AWS::Glue::SecurityConfiguration.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html#cfn-glue-securityconfiguration-name
    Stability:
        experimental
    """

class CfnTable(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnTable"):
    """A CloudFormation ``AWS::Glue::Table``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Glue::Table
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, catalog_id: str, database_name: str, table_input: typing.Union[aws_cdk.cdk.Token, "TableInputProperty"]) -> None:
        """Create a new ``AWS::Glue::Table``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            catalogId: ``AWS::Glue::Table.CatalogId``.
            databaseName: ``AWS::Glue::Table.DatabaseName``.
            tableInput: ``AWS::Glue::Table.TableInput``.

        Stability:
            experimental
        """
        props: CfnTableProps = {"catalogId": catalog_id, "databaseName": database_name, "tableInput": table_input}

        jsii.create(CfnTable, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnTableProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "tableName")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ColumnProperty(jsii.compat.TypedDict, total=False):
        comment: str
        """``CfnTable.ColumnProperty.Comment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-column.html#cfn-glue-table-column-comment
        Stability:
            experimental
        """
        type: str
        """``CfnTable.ColumnProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-column.html#cfn-glue-table-column-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTable.ColumnProperty", jsii_struct_bases=[_ColumnProperty])
    class ColumnProperty(_ColumnProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-column.html
        Stability:
            experimental
        """
        name: str
        """``CfnTable.ColumnProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-column.html#cfn-glue-table-column-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTable.OrderProperty", jsii_struct_bases=[])
    class OrderProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-order.html
        Stability:
            experimental
        """
        column: str
        """``CfnTable.OrderProperty.Column``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-order.html#cfn-glue-table-order-column
        Stability:
            experimental
        """

        sortOrder: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTable.OrderProperty.SortOrder``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-order.html#cfn-glue-table-order-sortorder
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTable.SerdeInfoProperty", jsii_struct_bases=[])
    class SerdeInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-serdeinfo.html
        Stability:
            experimental
        """
        name: str
        """``CfnTable.SerdeInfoProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-serdeinfo.html#cfn-glue-table-serdeinfo-name
        Stability:
            experimental
        """

        parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnTable.SerdeInfoProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-serdeinfo.html#cfn-glue-table-serdeinfo-parameters
        Stability:
            experimental
        """

        serializationLibrary: str
        """``CfnTable.SerdeInfoProperty.SerializationLibrary``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-serdeinfo.html#cfn-glue-table-serdeinfo-serializationlibrary
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTable.SkewedInfoProperty", jsii_struct_bases=[])
    class SkewedInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-skewedinfo.html
        Stability:
            experimental
        """
        skewedColumnNames: typing.List[str]
        """``CfnTable.SkewedInfoProperty.SkewedColumnNames``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-skewedinfo.html#cfn-glue-table-skewedinfo-skewedcolumnnames
        Stability:
            experimental
        """

        skewedColumnValueLocationMaps: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnTable.SkewedInfoProperty.SkewedColumnValueLocationMaps``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-skewedinfo.html#cfn-glue-table-skewedinfo-skewedcolumnvaluelocationmaps
        Stability:
            experimental
        """

        skewedColumnValues: typing.List[str]
        """``CfnTable.SkewedInfoProperty.SkewedColumnValues``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-skewedinfo.html#cfn-glue-table-skewedinfo-skewedcolumnvalues
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTable.StorageDescriptorProperty", jsii_struct_bases=[])
    class StorageDescriptorProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html
        Stability:
            experimental
        """
        bucketColumns: typing.List[str]
        """``CfnTable.StorageDescriptorProperty.BucketColumns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-bucketcolumns
        Stability:
            experimental
        """

        columns: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTable.ColumnProperty"]]]
        """``CfnTable.StorageDescriptorProperty.Columns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-columns
        Stability:
            experimental
        """

        compressed: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTable.StorageDescriptorProperty.Compressed``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-compressed
        Stability:
            experimental
        """

        inputFormat: str
        """``CfnTable.StorageDescriptorProperty.InputFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-inputformat
        Stability:
            experimental
        """

        location: str
        """``CfnTable.StorageDescriptorProperty.Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-location
        Stability:
            experimental
        """

        numberOfBuckets: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTable.StorageDescriptorProperty.NumberOfBuckets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-numberofbuckets
        Stability:
            experimental
        """

        outputFormat: str
        """``CfnTable.StorageDescriptorProperty.OutputFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-outputformat
        Stability:
            experimental
        """

        parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnTable.StorageDescriptorProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-parameters
        Stability:
            experimental
        """

        serdeInfo: typing.Union[aws_cdk.cdk.Token, "CfnTable.SerdeInfoProperty"]
        """``CfnTable.StorageDescriptorProperty.SerdeInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-serdeinfo
        Stability:
            experimental
        """

        skewedInfo: typing.Union[aws_cdk.cdk.Token, "CfnTable.SkewedInfoProperty"]
        """``CfnTable.StorageDescriptorProperty.SkewedInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-skewedinfo
        Stability:
            experimental
        """

        sortColumns: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTable.OrderProperty"]]]
        """``CfnTable.StorageDescriptorProperty.SortColumns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-sortcolumns
        Stability:
            experimental
        """

        storedAsSubDirectories: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTable.StorageDescriptorProperty.StoredAsSubDirectories``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-storedassubdirectories
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTable.TableInputProperty", jsii_struct_bases=[])
    class TableInputProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html
        Stability:
            experimental
        """
        description: str
        """``CfnTable.TableInputProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-description
        Stability:
            experimental
        """

        name: str
        """``CfnTable.TableInputProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-name
        Stability:
            experimental
        """

        owner: str
        """``CfnTable.TableInputProperty.Owner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-owner
        Stability:
            experimental
        """

        parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnTable.TableInputProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-parameters
        Stability:
            experimental
        """

        partitionKeys: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTable.ColumnProperty"]]]
        """``CfnTable.TableInputProperty.PartitionKeys``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-partitionkeys
        Stability:
            experimental
        """

        retention: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTable.TableInputProperty.Retention``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-retention
        Stability:
            experimental
        """

        storageDescriptor: typing.Union[aws_cdk.cdk.Token, "CfnTable.StorageDescriptorProperty"]
        """``CfnTable.TableInputProperty.StorageDescriptor``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-storagedescriptor
        Stability:
            experimental
        """

        tableType: str
        """``CfnTable.TableInputProperty.TableType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-tabletype
        Stability:
            experimental
        """

        viewExpandedText: str
        """``CfnTable.TableInputProperty.ViewExpandedText``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-viewexpandedtext
        Stability:
            experimental
        """

        viewOriginalText: str
        """``CfnTable.TableInputProperty.ViewOriginalText``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-vieworiginaltext
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTableProps", jsii_struct_bases=[])
class CfnTableProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Glue::Table``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html
    Stability:
        experimental
    """
    catalogId: str
    """``AWS::Glue::Table.CatalogId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-catalogid
    Stability:
        experimental
    """

    databaseName: str
    """``AWS::Glue::Table.DatabaseName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-databasename
    Stability:
        experimental
    """

    tableInput: typing.Union[aws_cdk.cdk.Token, "CfnTable.TableInputProperty"]
    """``AWS::Glue::Table.TableInput``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-tableinput
    Stability:
        experimental
    """

class CfnTrigger(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnTrigger"):
    """A CloudFormation ``AWS::Glue::Trigger``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Glue::Trigger
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, actions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "ActionProperty"]]], type: str, description: typing.Optional[str]=None, name: typing.Optional[str]=None, predicate: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["PredicateProperty"]]]=None, schedule: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[typing.Any, typing.Any]]=None) -> None:
        """Create a new ``AWS::Glue::Trigger``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            actions: ``AWS::Glue::Trigger.Actions``.
            type: ``AWS::Glue::Trigger.Type``.
            description: ``AWS::Glue::Trigger.Description``.
            name: ``AWS::Glue::Trigger.Name``.
            predicate: ``AWS::Glue::Trigger.Predicate``.
            schedule: ``AWS::Glue::Trigger.Schedule``.
            tags: ``AWS::Glue::Trigger.Tags``.

        Stability:
            experimental
        """
        props: CfnTriggerProps = {"actions": actions, "type": type}

        if description is not None:
            props["description"] = description

        if name is not None:
            props["name"] = name

        if predicate is not None:
            props["predicate"] = predicate

        if schedule is not None:
            props["schedule"] = schedule

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnTrigger, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnTriggerProps":
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

    @property
    @jsii.member(jsii_name="triggerName")
    def trigger_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "triggerName")

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTrigger.ActionProperty", jsii_struct_bases=[])
    class ActionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html
        Stability:
            experimental
        """
        arguments: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnTrigger.ActionProperty.Arguments``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html#cfn-glue-trigger-action-arguments
        Stability:
            experimental
        """

        jobName: str
        """``CfnTrigger.ActionProperty.JobName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html#cfn-glue-trigger-action-jobname
        Stability:
            experimental
        """

        securityConfiguration: str
        """``CfnTrigger.ActionProperty.SecurityConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html#cfn-glue-trigger-action-securityconfiguration
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTrigger.ConditionProperty", jsii_struct_bases=[])
    class ConditionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html
        Stability:
            experimental
        """
        jobName: str
        """``CfnTrigger.ConditionProperty.JobName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html#cfn-glue-trigger-condition-jobname
        Stability:
            experimental
        """

        logicalOperator: str
        """``CfnTrigger.ConditionProperty.LogicalOperator``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html#cfn-glue-trigger-condition-logicaloperator
        Stability:
            experimental
        """

        state: str
        """``CfnTrigger.ConditionProperty.State``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html#cfn-glue-trigger-condition-state
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTrigger.PredicateProperty", jsii_struct_bases=[])
    class PredicateProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-predicate.html
        Stability:
            experimental
        """
        conditions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTrigger.ConditionProperty"]]]
        """``CfnTrigger.PredicateProperty.Conditions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-predicate.html#cfn-glue-trigger-predicate-conditions
        Stability:
            experimental
        """

        logical: str
        """``CfnTrigger.PredicateProperty.Logical``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-predicate.html#cfn-glue-trigger-predicate-logical
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnTriggerProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::Glue::Trigger.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-description
    Stability:
        experimental
    """
    name: str
    """``AWS::Glue::Trigger.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-name
    Stability:
        experimental
    """
    predicate: typing.Union[aws_cdk.cdk.Token, "CfnTrigger.PredicateProperty"]
    """``AWS::Glue::Trigger.Predicate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-predicate
    Stability:
        experimental
    """
    schedule: str
    """``AWS::Glue::Trigger.Schedule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-schedule
    Stability:
        experimental
    """
    tags: typing.Mapping[typing.Any, typing.Any]
    """``AWS::Glue::Trigger.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTriggerProps", jsii_struct_bases=[_CfnTriggerProps])
class CfnTriggerProps(_CfnTriggerProps):
    """Properties for defining a ``AWS::Glue::Trigger``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html
    Stability:
        experimental
    """
    actions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTrigger.ActionProperty"]]]
    """``AWS::Glue::Trigger.Actions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-actions
    Stability:
        experimental
    """

    type: str
    """``AWS::Glue::Trigger.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-type
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _Column(jsii.compat.TypedDict, total=False):
    comment: str
    """Coment describing the column.

    Default:
        none

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.Column", jsii_struct_bases=[_Column])
class Column(_Column):
    """A column of a table.

    Stability:
        experimental
    """
    name: str
    """Name of the column.

    Stability:
        experimental
    """

    type: "Type"
    """Type of the column.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.DataFormat", jsii_struct_bases=[])
class DataFormat(jsii.compat.TypedDict):
    """Defines the input/output formats and ser/de for a single DataFormat.

    Stability:
        experimental
    """
    inputFormat: "InputFormat"
    """``InputFormat`` for this data format.

    Stability:
        experimental
    """

    outputFormat: "OutputFormat"
    """``OutputFormat`` for this data format.

    Stability:
        experimental
    """

    serializationLibrary: "SerializationLibrary"
    """Serialization library for this data format.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _DatabaseProps(jsii.compat.TypedDict, total=False):
    locationUri: str
    """The location of the database (for example, an HDFS path).

    Default:
        a bucket is created and the database is stored under s3:///

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.DatabaseProps", jsii_struct_bases=[_DatabaseProps])
class DatabaseProps(_DatabaseProps):
    """
    Stability:
        experimental
    """
    databaseName: str
    """The name of the database.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-glue.IDatabase")
class IDatabase(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IDatabaseProxy

    @property
    @jsii.member(jsii_name="catalogArn")
    def catalog_arn(self) -> str:
        """The ARN of the catalog.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> str:
        """The catalog id of the database (usually, the AWS account id).

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="databaseArn")
    def database_arn(self) -> str:
        """The ARN of the database.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> str:
        """The name of the database.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IDatabaseProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-glue.IDatabase"
    @property
    @jsii.member(jsii_name="catalogArn")
    def catalog_arn(self) -> str:
        """The ARN of the catalog.

        Stability:
            experimental
        """
        return jsii.get(self, "catalogArn")

    @property
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> str:
        """The catalog id of the database (usually, the AWS account id).

        Stability:
            experimental
        """
        return jsii.get(self, "catalogId")

    @property
    @jsii.member(jsii_name="databaseArn")
    def database_arn(self) -> str:
        """The ARN of the database.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "databaseArn")

    @property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> str:
        """The name of the database.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "databaseName")


@jsii.implements(IDatabase)
class Database(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.Database"):
    """A Glue database.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, database_name: str, location_uri: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            databaseName: The name of the database.
            locationUri: The location of the database (for example, an HDFS path). Default: a bucket is created and the database is stored under s3:///

        Stability:
            experimental
        """
        props: DatabaseProps = {"databaseName": database_name}

        if location_uri is not None:
            props["locationUri"] = location_uri

        jsii.create(Database, self, [scope, id, props])

    @jsii.member(jsii_name="fromDatabaseArn")
    @classmethod
    def from_database_arn(cls, scope: aws_cdk.cdk.Construct, id: str, database_arn: str) -> "IDatabase":
        """
        Arguments:
            scope: -
            id: -
            databaseArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromDatabaseArn", [scope, id, database_arn])

    @property
    @jsii.member(jsii_name="catalogArn")
    def catalog_arn(self) -> str:
        """ARN of the Glue catalog in which this database is stored.

        Stability:
            experimental
        """
        return jsii.get(self, "catalogArn")

    @property
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> str:
        """ID of the Glue catalog in which this database is stored.

        Stability:
            experimental
        """
        return jsii.get(self, "catalogId")

    @property
    @jsii.member(jsii_name="databaseArn")
    def database_arn(self) -> str:
        """ARN of this database.

        Stability:
            experimental
        """
        return jsii.get(self, "databaseArn")

    @property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> str:
        """Name of this database.

        Stability:
            experimental
        """
        return jsii.get(self, "databaseName")

    @property
    @jsii.member(jsii_name="locationUri")
    def location_uri(self) -> str:
        """Location URI of this database.

        Stability:
            experimental
        """
        return jsii.get(self, "locationUri")


@jsii.interface(jsii_type="@aws-cdk/aws-glue.ITable")
class ITable(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ITableProxy

    @property
    @jsii.member(jsii_name="tableArn")
    def table_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...


class _ITableProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-glue.ITable"
    @property
    @jsii.member(jsii_name="tableArn")
    def table_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "tableArn")

    @property
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "tableName")


class InputFormat(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.InputFormat"):
    """Absolute class name of the Hadoop ``InputFormat`` to use when reading table files.

    Stability:
        experimental
    """
    def __init__(self, class_name: str) -> None:
        """
        Arguments:
            className: -

        Stability:
            experimental
        """
        jsii.create(InputFormat, self, [class_name])

    @classproperty
    @jsii.member(jsii_name="TextInputFormat")
    def TEXT_INPUT_FORMAT(cls) -> "InputFormat":
        """An InputFormat for plain text files.

        Files are broken into lines. Either linefeed or
        carriage-return are used to signal end of line. Keys are the position in the file, and
        values are the line of text.

        See:
            https://hadoop.apache.org/docs/stable/api/org/apache/hadoop/mapred/TextInputFormat.html
        Stability:
            experimental
        """
        return jsii.sget(cls, "TextInputFormat")

    @property
    @jsii.member(jsii_name="className")
    def class_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "className")


class OutputFormat(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.OutputFormat"):
    """Absolute class name of the Hadoop ``OutputFormat`` to use when writing table files.

    Stability:
        experimental
    """
    def __init__(self, class_name: str) -> None:
        """
        Arguments:
            className: -

        Stability:
            experimental
        """
        jsii.create(OutputFormat, self, [class_name])

    @classproperty
    @jsii.member(jsii_name="HiveIgnoreKeyTextOutputFormat")
    def HIVE_IGNORE_KEY_TEXT_OUTPUT_FORMAT(cls) -> "OutputFormat":
        """Writes text data with a null key (value only).

        See:
            https://hive.apache.org/javadocs/r2.2.0/api/org/apache/hadoop/hive/ql/io/HiveIgnoreKeyTextOutputFormat.html
        Stability:
            experimental
        """
        return jsii.sget(cls, "HiveIgnoreKeyTextOutputFormat")

    @property
    @jsii.member(jsii_name="className")
    def class_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "className")


class Schema(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.Schema"):
    """
    See:
        https://docs.aws.amazon.com/athena/latest/ug/data-types.html
    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(Schema, self, [])

    @jsii.member(jsii_name="array")
    @classmethod
    def array(cls, *, input_string: str, is_primitive: bool) -> "Type":
        """Creates an array of some other type.

        Arguments:
            itemType: type contained by the array.
            inputString: Glue InputString for this type.
            isPrimitive: Indicates whether this type is a primitive data type.

        Stability:
            experimental
        """
        item_type: Type = {"inputString": input_string, "isPrimitive": is_primitive}

        return jsii.sinvoke(cls, "array", [item_type])

    @jsii.member(jsii_name="char")
    @classmethod
    def char(cls, length: jsii.Number) -> "Type":
        """Fixed length character data, with a specified length between 1 and 255.

        Arguments:
            length: length between 1 and 255.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "char", [length])

    @jsii.member(jsii_name="decimal")
    @classmethod
    def decimal(cls, precision: jsii.Number, scale: typing.Optional[jsii.Number]=None) -> "Type":
        """Creates a decimal type.

        TODO: Bounds

        Arguments:
            precision: the total number of digits.
            scale: the number of digits in fractional part, the default is 0.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "decimal", [precision, scale])

    @jsii.member(jsii_name="map")
    @classmethod
    def map(cls, key_type: "Type", *, input_string: str, is_primitive: bool) -> "Type":
        """Creates a map of some primitive key type to some value type.

        Arguments:
            keyType: type of key, must be a primitive.
            valueType: type fo the value indexed by the key.
            inputString: Glue InputString for this type.
            isPrimitive: Indicates whether this type is a primitive data type.

        Stability:
            experimental
        """
        value_type: Type = {"inputString": input_string, "isPrimitive": is_primitive}

        return jsii.sinvoke(cls, "map", [key_type, value_type])

    @jsii.member(jsii_name="struct")
    @classmethod
    def struct(cls, columns: typing.List["Column"]) -> "Type":
        """Creates a nested structure containing individually named and typed columns.

        Arguments:
            columns: the columns of the structure.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "struct", [columns])

    @jsii.member(jsii_name="varchar")
    @classmethod
    def varchar(cls, length: jsii.Number) -> "Type":
        """Variable length character data, with a specified length between 1 and 65535.

        Arguments:
            length: length between 1 and 65535.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "varchar", [length])

    @classproperty
    @jsii.member(jsii_name="bigint")
    def BIGINT(cls) -> "Type":
        """A 64-bit signed INTEGER in two’s complement format, with a minimum value of -2^63 and a maximum value of 2^63-1.

        Stability:
            experimental
        """
        return jsii.sget(cls, "bigint")

    @classproperty
    @jsii.member(jsii_name="binary")
    def BINARY(cls) -> "Type":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "binary")

    @classproperty
    @jsii.member(jsii_name="boolean")
    def BOOLEAN(cls) -> "Type":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "boolean")

    @classproperty
    @jsii.member(jsii_name="date")
    def DATE(cls) -> "Type":
        """Date type.

        Stability:
            experimental
        """
        return jsii.sget(cls, "date")

    @classproperty
    @jsii.member(jsii_name="double")
    def DOUBLE(cls) -> "Type":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "double")

    @classproperty
    @jsii.member(jsii_name="float")
    def FLOAT(cls) -> "Type":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "float")

    @classproperty
    @jsii.member(jsii_name="integer")
    def INTEGER(cls) -> "Type":
        """A 32-bit signed INTEGER in two’s complement format, with a minimum value of -2^31 and a maximum value of 2^31-1.

        Stability:
            experimental
        """
        return jsii.sget(cls, "integer")

    @classproperty
    @jsii.member(jsii_name="smallint")
    def SMALLINT(cls) -> "Type":
        """A 16-bit signed INTEGER in two’s complement format, with a minimum value of -2^15 and a maximum value of 2^15-1.

        Stability:
            experimental
        """
        return jsii.sget(cls, "smallint")

    @classproperty
    @jsii.member(jsii_name="string")
    def STRING(cls) -> "Type":
        """Arbitrary-length string type.

        Stability:
            experimental
        """
        return jsii.sget(cls, "string")

    @classproperty
    @jsii.member(jsii_name="timestamp")
    def TIMESTAMP(cls) -> "Type":
        """Timestamp type (date and time).

        Stability:
            experimental
        """
        return jsii.sget(cls, "timestamp")

    @classproperty
    @jsii.member(jsii_name="tinyint")
    def TINYINT(cls) -> "Type":
        """A 8-bit signed INTEGER in two’s complement format, with a minimum value of -2^7 and a maximum value of 2^7-1.

        Stability:
            experimental
        """
        return jsii.sget(cls, "tinyint")


class SerializationLibrary(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.SerializationLibrary"):
    """Serialization library to use when serializing/deserializing (SerDe) table records.

    See:
        https://cwiki.apache.org/confluence/display/Hive/SerDe
    Stability:
        experimental
    """
    def __init__(self, class_name: str) -> None:
        """
        Arguments:
            className: -

        Stability:
            experimental
        """
        jsii.create(SerializationLibrary, self, [class_name])

    @classproperty
    @jsii.member(jsii_name="HiveJson")
    def HIVE_JSON(cls) -> "SerializationLibrary":
        """
        See:
            https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-JSON
        Stability:
            experimental
        """
        return jsii.sget(cls, "HiveJson")

    @classproperty
    @jsii.member(jsii_name="OpenXJson")
    def OPEN_X_JSON(cls) -> "SerializationLibrary":
        """
        See:
            https://github.com/rcongiu/Hive-JSON-Serde
        Stability:
            experimental
        """
        return jsii.sget(cls, "OpenXJson")

    @property
    @jsii.member(jsii_name="className")
    def class_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "className")


@jsii.implements(ITable)
class Table(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.Table"):
    """A Glue table.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, columns: typing.List["Column"], database: "IDatabase", data_format: "DataFormat", table_name: str, bucket: typing.Optional[aws_cdk.aws_s3.IBucket]=None, compressed: typing.Optional[bool]=None, description: typing.Optional[str]=None, encryption: typing.Optional["TableEncryption"]=None, encryption_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, partition_keys: typing.Optional[typing.List["Column"]]=None, s3_prefix: typing.Optional[str]=None, stored_as_sub_directories: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            columns: Columns of the table.
            database: Database in which to store the table.
            dataFormat: Storage type of the table's data.
            tableName: Name of the table.
            bucket: S3 bucket in which to store data. Default: one is created for you
            compressed: Indicates whether the table's data is compressed or not. Default: false
            description: Description of the table. Default: generated
            encryption: The kind of encryption to secure the data with. You can only provide this option if you are not explicitly passing in a bucket. If you choose ``SSE-KMS``, you *can* provide an un-managed KMS key with ``encryptionKey``. If you choose ``CSE-KMS``, you *must* provide an un-managed KMS key with ``encryptionKey``. Default: Unencrypted
            encryptionKey: External KMS key to use for bucket encryption. The ``encryption`` property must be ``SSE-KMS`` or ``CSE-KMS``. Default: key is managed by KMS.
            partitionKeys: Partition columns of the table. Default: table is not partitioned
            s3Prefix: S3 prefix under which table objects are stored. Default: data/
            storedAsSubDirectories: Indicates whether the table data is stored in subdirectories. Default: false

        Stability:
            experimental
        """
        props: TableProps = {"columns": columns, "database": database, "dataFormat": data_format, "tableName": table_name}

        if bucket is not None:
            props["bucket"] = bucket

        if compressed is not None:
            props["compressed"] = compressed

        if description is not None:
            props["description"] = description

        if encryption is not None:
            props["encryption"] = encryption

        if encryption_key is not None:
            props["encryptionKey"] = encryption_key

        if partition_keys is not None:
            props["partitionKeys"] = partition_keys

        if s3_prefix is not None:
            props["s3Prefix"] = s3_prefix

        if stored_as_sub_directories is not None:
            props["storedAsSubDirectories"] = stored_as_sub_directories

        jsii.create(Table, self, [scope, id, props])

    @jsii.member(jsii_name="fromTableArn")
    @classmethod
    def from_table_arn(cls, scope: aws_cdk.cdk.Construct, id: str, table_arn: str) -> "ITable":
        """
        Arguments:
            scope: -
            id: -
            tableArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromTableArn", [scope, id, table_arn])

    @jsii.member(jsii_name="fromTableAttributes")
    @classmethod
    def from_table_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, table_arn: str, table_name: str) -> "ITable":
        """Creates a Table construct that represents an external table.

        Arguments:
            scope: The scope creating construct (usually ``this``).
            id: The construct's id.
            attrs: Import attributes.
            tableArn: 
            tableName: 

        Stability:
            experimental
        """
        attrs: TableAttributes = {"tableArn": table_arn, "tableName": table_name}

        return jsii.sinvoke(cls, "fromTableAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant read permissions to the table and the underlying data stored in S3 to an IAM principal.

        Arguments:
            grantee: the principal.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantRead", [grantee])

    @jsii.member(jsii_name="grantReadWrite")
    def grant_read_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant read and write permissions to the table and the underlying data stored in S3 to an IAM principal.

        Arguments:
            grantee: the principal.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantReadWrite", [grantee])

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant write permissions to the table and the underlying data stored in S3 to an IAM principal.

        Arguments:
            grantee: the principal.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantWrite", [grantee])

    @property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> aws_cdk.aws_s3.IBucket:
        """S3 bucket in which the table's data resides.

        Stability:
            experimental
        """
        return jsii.get(self, "bucket")

    @property
    @jsii.member(jsii_name="columns")
    def columns(self) -> typing.List["Column"]:
        """This table's columns.

        Stability:
            experimental
        """
        return jsii.get(self, "columns")

    @property
    @jsii.member(jsii_name="compressed")
    def compressed(self) -> bool:
        """Indicates whether the table's data is compressed or not.

        Stability:
            experimental
        """
        return jsii.get(self, "compressed")

    @property
    @jsii.member(jsii_name="database")
    def database(self) -> "IDatabase":
        """Database this table belongs to.

        Stability:
            experimental
        """
        return jsii.get(self, "database")

    @property
    @jsii.member(jsii_name="dataFormat")
    def data_format(self) -> "DataFormat":
        """Format of this table's data files.

        Stability:
            experimental
        """
        return jsii.get(self, "dataFormat")

    @property
    @jsii.member(jsii_name="encryption")
    def encryption(self) -> "TableEncryption":
        """The type of encryption enabled for the table.

        Stability:
            experimental
        """
        return jsii.get(self, "encryption")

    @property
    @jsii.member(jsii_name="s3Prefix")
    def s3_prefix(self) -> str:
        """S3 Key Prefix under which this table's files are stored in S3.

        Stability:
            experimental
        """
        return jsii.get(self, "s3Prefix")

    @property
    @jsii.member(jsii_name="tableArn")
    def table_arn(self) -> str:
        """ARN of this table.

        Stability:
            experimental
        """
        return jsii.get(self, "tableArn")

    @property
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> str:
        """Name of this table.

        Stability:
            experimental
        """
        return jsii.get(self, "tableName")

    @property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        """The KMS key used to secure the data if ``encryption`` is set to ``CSE-KMS`` or ``SSE-KMS``.

        Otherwise, ``undefined``.

        Stability:
            experimental
        """
        return jsii.get(self, "encryptionKey")

    @property
    @jsii.member(jsii_name="partitionKeys")
    def partition_keys(self) -> typing.Optional[typing.List["Column"]]:
        """This table's partition keys if the table is partitioned.

        Stability:
            experimental
        """
        return jsii.get(self, "partitionKeys")


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.TableAttributes", jsii_struct_bases=[])
class TableAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    tableArn: str
    """
    Stability:
        experimental
    """

    tableName: str
    """
    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-glue.TableEncryption")
class TableEncryption(enum.Enum):
    """Encryption options for a Table.

    See:
        https://docs.aws.amazon.com/athena/latest/ug/encryption.html
    Stability:
        experimental
    """
    Unencrypted = "Unencrypted"
    """
    Stability:
        experimental
    """
    S3Managed = "S3Managed"
    """Server side encryption (SSE) with an Amazon S3-managed key.

    See:
        https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingServerSideEncryption.html
    Stability:
        experimental
    """
    Kms = "Kms"
    """Server-side encryption (SSE) with an AWS KMS key managed by the account owner.

    See:
        https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingKMSEncryption.html
    Stability:
        experimental
    """
    KmsManaged = "KmsManaged"
    """Server-side encryption (SSE) with an AWS KMS key managed by the KMS service.

    Stability:
        experimental
    """
    ClientSideKms = "ClientSideKms"
    """Client-side encryption (CSE) with an AWS KMS key managed by the account owner.

    See:
        https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingClientSideEncryption.html
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _TableProps(jsii.compat.TypedDict, total=False):
    bucket: aws_cdk.aws_s3.IBucket
    """S3 bucket in which to store data.

    Default:
        one is created for you

    Stability:
        experimental
    """
    compressed: bool
    """Indicates whether the table's data is compressed or not.

    Default:
        false

    Stability:
        experimental
    """
    description: str
    """Description of the table.

    Default:
        generated

    Stability:
        experimental
    """
    encryption: "TableEncryption"
    """The kind of encryption to secure the data with.

    You can only provide this option if you are not explicitly passing in a bucket.

    If you choose ``SSE-KMS``, you *can* provide an un-managed KMS key with ``encryptionKey``.
    If you choose ``CSE-KMS``, you *must* provide an un-managed KMS key with ``encryptionKey``.

    Default:
        Unencrypted

    Stability:
        experimental
    """
    encryptionKey: aws_cdk.aws_kms.IKey
    """External KMS key to use for bucket encryption.

    The ``encryption`` property must be ``SSE-KMS`` or ``CSE-KMS``.

    Default:
        key is managed by KMS.

    Stability:
        experimental
    """
    partitionKeys: typing.List["Column"]
    """Partition columns of the table.

    Default:
        table is not partitioned

    Stability:
        experimental
    """
    s3Prefix: str
    """S3 prefix under which table objects are stored.

    Default:
        data/

    Stability:
        experimental
    """
    storedAsSubDirectories: bool
    """Indicates whether the table data is stored in subdirectories.

    Default:
        false

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.TableProps", jsii_struct_bases=[_TableProps])
class TableProps(_TableProps):
    """
    Stability:
        experimental
    """
    columns: typing.List["Column"]
    """Columns of the table.

    Stability:
        experimental
    """

    database: "IDatabase"
    """Database in which to store the table.

    Stability:
        experimental
    """

    dataFormat: "DataFormat"
    """Storage type of the table's data.

    Stability:
        experimental
    """

    tableName: str
    """Name of the table.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.Type", jsii_struct_bases=[])
class Type(jsii.compat.TypedDict):
    """Represents a type of a column in a table schema.

    Stability:
        experimental
    """
    inputString: str
    """Glue InputString for this type.

    Stability:
        experimental
    """

    isPrimitive: bool
    """Indicates whether this type is a primitive data type.

    Stability:
        experimental
    """

__all__ = ["CfnClassifier", "CfnClassifierProps", "CfnConnection", "CfnConnectionProps", "CfnCrawler", "CfnCrawlerProps", "CfnDataCatalogEncryptionSettings", "CfnDataCatalogEncryptionSettingsProps", "CfnDatabase", "CfnDatabaseProps", "CfnDevEndpoint", "CfnDevEndpointProps", "CfnJob", "CfnJobProps", "CfnPartition", "CfnPartitionProps", "CfnSecurityConfiguration", "CfnSecurityConfigurationProps", "CfnTable", "CfnTableProps", "CfnTrigger", "CfnTriggerProps", "Column", "DataFormat", "Database", "DatabaseProps", "IDatabase", "ITable", "InputFormat", "OutputFormat", "Schema", "SerializationLibrary", "Table", "TableAttributes", "TableEncryption", "TableProps", "Type", "__jsii_assembly__"]

publication.publish()
