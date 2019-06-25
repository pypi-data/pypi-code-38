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
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-glue", "0.36.0", __name__, "aws-glue@0.36.0.jsii.tgz")
class CfnClassifier(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnClassifier"):
    """A CloudFormation ``AWS::Glue::Classifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html
    Stability:
        stable
    cloudformationResource:
        AWS::Glue::Classifier
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, csv_classifier: typing.Optional[typing.Union[typing.Optional["CsvClassifierProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, grok_classifier: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["GrokClassifierProperty"]]]=None, json_classifier: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["JsonClassifierProperty"]]]=None, xml_classifier: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["XMLClassifierProperty"]]]=None) -> None:
        """Create a new ``AWS::Glue::Classifier``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            csv_classifier: ``AWS::Glue::Classifier.CsvClassifier``.
            grok_classifier: ``AWS::Glue::Classifier.GrokClassifier``.
            json_classifier: ``AWS::Glue::Classifier.JsonClassifier``.
            xml_classifier: ``AWS::Glue::Classifier.XMLClassifier``.

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
    @jsii.member(jsii_name="csvClassifier")
    def csv_classifier(self) -> typing.Optional[typing.Union[typing.Optional["CsvClassifierProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Glue::Classifier.CsvClassifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-csvclassifier
        Stability:
            stable
        """
        return jsii.get(self, "csvClassifier")

    @csv_classifier.setter
    def csv_classifier(self, value: typing.Optional[typing.Union[typing.Optional["CsvClassifierProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "csvClassifier", value)

    @property
    @jsii.member(jsii_name="grokClassifier")
    def grok_classifier(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["GrokClassifierProperty"]]]:
        """``AWS::Glue::Classifier.GrokClassifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-grokclassifier
        Stability:
            stable
        """
        return jsii.get(self, "grokClassifier")

    @grok_classifier.setter
    def grok_classifier(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["GrokClassifierProperty"]]]):
        return jsii.set(self, "grokClassifier", value)

    @property
    @jsii.member(jsii_name="jsonClassifier")
    def json_classifier(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["JsonClassifierProperty"]]]:
        """``AWS::Glue::Classifier.JsonClassifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-jsonclassifier
        Stability:
            stable
        """
        return jsii.get(self, "jsonClassifier")

    @json_classifier.setter
    def json_classifier(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["JsonClassifierProperty"]]]):
        return jsii.set(self, "jsonClassifier", value)

    @property
    @jsii.member(jsii_name="xmlClassifier")
    def xml_classifier(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["XMLClassifierProperty"]]]:
        """``AWS::Glue::Classifier.XMLClassifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-xmlclassifier
        Stability:
            stable
        """
        return jsii.get(self, "xmlClassifier")

    @xml_classifier.setter
    def xml_classifier(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["XMLClassifierProperty"]]]):
        return jsii.set(self, "xmlClassifier", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnClassifier.CsvClassifierProperty", jsii_struct_bases=[])
    class CsvClassifierProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html
        Stability:
            stable
        """
        allowSingleColumn: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnClassifier.CsvClassifierProperty.AllowSingleColumn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-allowsinglecolumn
        Stability:
            stable
        """

        containsHeader: str
        """``CfnClassifier.CsvClassifierProperty.ContainsHeader``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-containsheader
        Stability:
            stable
        """

        delimiter: str
        """``CfnClassifier.CsvClassifierProperty.Delimiter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-delimiter
        Stability:
            stable
        """

        disableValueTrimming: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnClassifier.CsvClassifierProperty.DisableValueTrimming``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-disablevaluetrimming
        Stability:
            stable
        """

        header: typing.List[str]
        """``CfnClassifier.CsvClassifierProperty.Header``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-header
        Stability:
            stable
        """

        name: str
        """``CfnClassifier.CsvClassifierProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-name
        Stability:
            stable
        """

        quoteSymbol: str
        """``CfnClassifier.CsvClassifierProperty.QuoteSymbol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-csvclassifier.html#cfn-glue-classifier-csvclassifier-quotesymbol
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _GrokClassifierProperty(jsii.compat.TypedDict, total=False):
        customPatterns: str
        """``CfnClassifier.GrokClassifierProperty.CustomPatterns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html#cfn-glue-classifier-grokclassifier-custompatterns
        Stability:
            stable
        """
        name: str
        """``CfnClassifier.GrokClassifierProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html#cfn-glue-classifier-grokclassifier-name
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnClassifier.GrokClassifierProperty", jsii_struct_bases=[_GrokClassifierProperty])
    class GrokClassifierProperty(_GrokClassifierProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html
        Stability:
            stable
        """
        classification: str
        """``CfnClassifier.GrokClassifierProperty.Classification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html#cfn-glue-classifier-grokclassifier-classification
        Stability:
            stable
        """

        grokPattern: str
        """``CfnClassifier.GrokClassifierProperty.GrokPattern``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-grokclassifier.html#cfn-glue-classifier-grokclassifier-grokpattern
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _JsonClassifierProperty(jsii.compat.TypedDict, total=False):
        name: str
        """``CfnClassifier.JsonClassifierProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-jsonclassifier.html#cfn-glue-classifier-jsonclassifier-name
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnClassifier.JsonClassifierProperty", jsii_struct_bases=[_JsonClassifierProperty])
    class JsonClassifierProperty(_JsonClassifierProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-jsonclassifier.html
        Stability:
            stable
        """
        jsonPath: str
        """``CfnClassifier.JsonClassifierProperty.JsonPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-jsonclassifier.html#cfn-glue-classifier-jsonclassifier-jsonpath
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _XMLClassifierProperty(jsii.compat.TypedDict, total=False):
        name: str
        """``CfnClassifier.XMLClassifierProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-xmlclassifier.html#cfn-glue-classifier-xmlclassifier-name
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnClassifier.XMLClassifierProperty", jsii_struct_bases=[_XMLClassifierProperty])
    class XMLClassifierProperty(_XMLClassifierProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-xmlclassifier.html
        Stability:
            stable
        """
        classification: str
        """``CfnClassifier.XMLClassifierProperty.Classification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-xmlclassifier.html#cfn-glue-classifier-xmlclassifier-classification
        Stability:
            stable
        """

        rowTag: str
        """``CfnClassifier.XMLClassifierProperty.RowTag``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-classifier-xmlclassifier.html#cfn-glue-classifier-xmlclassifier-rowtag
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnClassifierProps", jsii_struct_bases=[])
class CfnClassifierProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::Glue::Classifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html
    Stability:
        stable
    """
    csvClassifier: typing.Union["CfnClassifier.CsvClassifierProperty", aws_cdk.core.IResolvable]
    """``AWS::Glue::Classifier.CsvClassifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-csvclassifier
    Stability:
        stable
    """

    grokClassifier: typing.Union[aws_cdk.core.IResolvable, "CfnClassifier.GrokClassifierProperty"]
    """``AWS::Glue::Classifier.GrokClassifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-grokclassifier
    Stability:
        stable
    """

    jsonClassifier: typing.Union[aws_cdk.core.IResolvable, "CfnClassifier.JsonClassifierProperty"]
    """``AWS::Glue::Classifier.JsonClassifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-jsonclassifier
    Stability:
        stable
    """

    xmlClassifier: typing.Union[aws_cdk.core.IResolvable, "CfnClassifier.XMLClassifierProperty"]
    """``AWS::Glue::Classifier.XMLClassifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-classifier.html#cfn-glue-classifier-xmlclassifier
    Stability:
        stable
    """

class CfnConnection(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnConnection"):
    """A CloudFormation ``AWS::Glue::Connection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html
    Stability:
        stable
    cloudformationResource:
        AWS::Glue::Connection
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, catalog_id: str, connection_input: typing.Union[aws_cdk.core.IResolvable, "ConnectionInputProperty"]) -> None:
        """Create a new ``AWS::Glue::Connection``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            catalog_id: ``AWS::Glue::Connection.CatalogId``.
            connection_input: ``AWS::Glue::Connection.ConnectionInput``.

        Stability:
            experimental
        """
        props: CfnConnectionProps = {"catalogId": catalog_id, "connectionInput": connection_input}

        jsii.create(CfnConnection, self, [scope, id, props])

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
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> str:
        """``AWS::Glue::Connection.CatalogId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html#cfn-glue-connection-catalogid
        Stability:
            stable
        """
        return jsii.get(self, "catalogId")

    @catalog_id.setter
    def catalog_id(self, value: str):
        return jsii.set(self, "catalogId", value)

    @property
    @jsii.member(jsii_name="connectionInput")
    def connection_input(self) -> typing.Union[aws_cdk.core.IResolvable, "ConnectionInputProperty"]:
        """``AWS::Glue::Connection.ConnectionInput``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html#cfn-glue-connection-connectioninput
        Stability:
            stable
        """
        return jsii.get(self, "connectionInput")

    @connection_input.setter
    def connection_input(self, value: typing.Union[aws_cdk.core.IResolvable, "ConnectionInputProperty"]):
        return jsii.set(self, "connectionInput", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ConnectionInputProperty(jsii.compat.TypedDict, total=False):
        description: str
        """``CfnConnection.ConnectionInputProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-description
        Stability:
            stable
        """
        matchCriteria: typing.List[str]
        """``CfnConnection.ConnectionInputProperty.MatchCriteria``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-matchcriteria
        Stability:
            stable
        """
        name: str
        """``CfnConnection.ConnectionInputProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-name
        Stability:
            stable
        """
        physicalConnectionRequirements: typing.Union[aws_cdk.core.IResolvable, "CfnConnection.PhysicalConnectionRequirementsProperty"]
        """``CfnConnection.ConnectionInputProperty.PhysicalConnectionRequirements``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-physicalconnectionrequirements
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnConnection.ConnectionInputProperty", jsii_struct_bases=[_ConnectionInputProperty])
    class ConnectionInputProperty(_ConnectionInputProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html
        Stability:
            stable
        """
        connectionProperties: typing.Any
        """``CfnConnection.ConnectionInputProperty.ConnectionProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-connectionproperties
        Stability:
            stable
        """

        connectionType: str
        """``CfnConnection.ConnectionInputProperty.ConnectionType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-connectioninput.html#cfn-glue-connection-connectioninput-connectiontype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnConnection.PhysicalConnectionRequirementsProperty", jsii_struct_bases=[])
    class PhysicalConnectionRequirementsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-physicalconnectionrequirements.html
        Stability:
            stable
        """
        availabilityZone: str
        """``CfnConnection.PhysicalConnectionRequirementsProperty.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-physicalconnectionrequirements.html#cfn-glue-connection-physicalconnectionrequirements-availabilityzone
        Stability:
            stable
        """

        securityGroupIdList: typing.List[str]
        """``CfnConnection.PhysicalConnectionRequirementsProperty.SecurityGroupIdList``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-physicalconnectionrequirements.html#cfn-glue-connection-physicalconnectionrequirements-securitygroupidlist
        Stability:
            stable
        """

        subnetId: str
        """``CfnConnection.PhysicalConnectionRequirementsProperty.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-connection-physicalconnectionrequirements.html#cfn-glue-connection-physicalconnectionrequirements-subnetid
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnConnectionProps", jsii_struct_bases=[])
class CfnConnectionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Glue::Connection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html
    Stability:
        stable
    """
    catalogId: str
    """``AWS::Glue::Connection.CatalogId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html#cfn-glue-connection-catalogid
    Stability:
        stable
    """

    connectionInput: typing.Union[aws_cdk.core.IResolvable, "CfnConnection.ConnectionInputProperty"]
    """``AWS::Glue::Connection.ConnectionInput``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-connection.html#cfn-glue-connection-connectioninput
    Stability:
        stable
    """

class CfnCrawler(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnCrawler"):
    """A CloudFormation ``AWS::Glue::Crawler``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html
    Stability:
        stable
    cloudformationResource:
        AWS::Glue::Crawler
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, database_name: str, role: str, targets: typing.Union[aws_cdk.core.IResolvable, "TargetsProperty"], classifiers: typing.Optional[typing.List[str]]=None, configuration: typing.Optional[str]=None, crawler_security_configuration: typing.Optional[str]=None, description: typing.Optional[str]=None, name: typing.Optional[str]=None, schedule: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ScheduleProperty"]]]=None, schema_change_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SchemaChangePolicyProperty"]]]=None, table_prefix: typing.Optional[str]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Glue::Crawler``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            database_name: ``AWS::Glue::Crawler.DatabaseName``.
            role: ``AWS::Glue::Crawler.Role``.
            targets: ``AWS::Glue::Crawler.Targets``.
            classifiers: ``AWS::Glue::Crawler.Classifiers``.
            configuration: ``AWS::Glue::Crawler.Configuration``.
            crawler_security_configuration: ``AWS::Glue::Crawler.CrawlerSecurityConfiguration``.
            description: ``AWS::Glue::Crawler.Description``.
            name: ``AWS::Glue::Crawler.Name``.
            schedule: ``AWS::Glue::Crawler.Schedule``.
            schema_change_policy: ``AWS::Glue::Crawler.SchemaChangePolicy``.
            table_prefix: ``AWS::Glue::Crawler.TablePrefix``.
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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Glue::Crawler.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> str:
        """``AWS::Glue::Crawler.DatabaseName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-databasename
        Stability:
            stable
        """
        return jsii.get(self, "databaseName")

    @database_name.setter
    def database_name(self, value: str):
        return jsii.set(self, "databaseName", value)

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> str:
        """``AWS::Glue::Crawler.Role``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-role
        Stability:
            stable
        """
        return jsii.get(self, "role")

    @role.setter
    def role(self, value: str):
        return jsii.set(self, "role", value)

    @property
    @jsii.member(jsii_name="targets")
    def targets(self) -> typing.Union[aws_cdk.core.IResolvable, "TargetsProperty"]:
        """``AWS::Glue::Crawler.Targets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-targets
        Stability:
            stable
        """
        return jsii.get(self, "targets")

    @targets.setter
    def targets(self, value: typing.Union[aws_cdk.core.IResolvable, "TargetsProperty"]):
        return jsii.set(self, "targets", value)

    @property
    @jsii.member(jsii_name="classifiers")
    def classifiers(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Glue::Crawler.Classifiers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-classifiers
        Stability:
            stable
        """
        return jsii.get(self, "classifiers")

    @classifiers.setter
    def classifiers(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "classifiers", value)

    @property
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> typing.Optional[str]:
        """``AWS::Glue::Crawler.Configuration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-configuration
        Stability:
            stable
        """
        return jsii.get(self, "configuration")

    @configuration.setter
    def configuration(self, value: typing.Optional[str]):
        return jsii.set(self, "configuration", value)

    @property
    @jsii.member(jsii_name="crawlerSecurityConfiguration")
    def crawler_security_configuration(self) -> typing.Optional[str]:
        """``AWS::Glue::Crawler.CrawlerSecurityConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-crawlersecurityconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "crawlerSecurityConfiguration")

    @crawler_security_configuration.setter
    def crawler_security_configuration(self, value: typing.Optional[str]):
        return jsii.set(self, "crawlerSecurityConfiguration", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::Glue::Crawler.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Glue::Crawler.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ScheduleProperty"]]]:
        """``AWS::Glue::Crawler.Schedule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-schedule
        Stability:
            stable
        """
        return jsii.get(self, "schedule")

    @schedule.setter
    def schedule(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ScheduleProperty"]]]):
        return jsii.set(self, "schedule", value)

    @property
    @jsii.member(jsii_name="schemaChangePolicy")
    def schema_change_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SchemaChangePolicyProperty"]]]:
        """``AWS::Glue::Crawler.SchemaChangePolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-schemachangepolicy
        Stability:
            stable
        """
        return jsii.get(self, "schemaChangePolicy")

    @schema_change_policy.setter
    def schema_change_policy(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SchemaChangePolicyProperty"]]]):
        return jsii.set(self, "schemaChangePolicy", value)

    @property
    @jsii.member(jsii_name="tablePrefix")
    def table_prefix(self) -> typing.Optional[str]:
        """``AWS::Glue::Crawler.TablePrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-tableprefix
        Stability:
            stable
        """
        return jsii.get(self, "tablePrefix")

    @table_prefix.setter
    def table_prefix(self, value: typing.Optional[str]):
        return jsii.set(self, "tablePrefix", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnCrawler.JdbcTargetProperty", jsii_struct_bases=[])
    class JdbcTargetProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-jdbctarget.html
        Stability:
            stable
        """
        connectionName: str
        """``CfnCrawler.JdbcTargetProperty.ConnectionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-jdbctarget.html#cfn-glue-crawler-jdbctarget-connectionname
        Stability:
            stable
        """

        exclusions: typing.List[str]
        """``CfnCrawler.JdbcTargetProperty.Exclusions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-jdbctarget.html#cfn-glue-crawler-jdbctarget-exclusions
        Stability:
            stable
        """

        path: str
        """``CfnCrawler.JdbcTargetProperty.Path``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-jdbctarget.html#cfn-glue-crawler-jdbctarget-path
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnCrawler.S3TargetProperty", jsii_struct_bases=[])
    class S3TargetProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-s3target.html
        Stability:
            stable
        """
        exclusions: typing.List[str]
        """``CfnCrawler.S3TargetProperty.Exclusions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-s3target.html#cfn-glue-crawler-s3target-exclusions
        Stability:
            stable
        """

        path: str
        """``CfnCrawler.S3TargetProperty.Path``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-s3target.html#cfn-glue-crawler-s3target-path
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnCrawler.ScheduleProperty", jsii_struct_bases=[])
    class ScheduleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schedule.html
        Stability:
            stable
        """
        scheduleExpression: str
        """``CfnCrawler.ScheduleProperty.ScheduleExpression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schedule.html#cfn-glue-crawler-schedule-scheduleexpression
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnCrawler.SchemaChangePolicyProperty", jsii_struct_bases=[])
    class SchemaChangePolicyProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schemachangepolicy.html
        Stability:
            stable
        """
        deleteBehavior: str
        """``CfnCrawler.SchemaChangePolicyProperty.DeleteBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schemachangepolicy.html#cfn-glue-crawler-schemachangepolicy-deletebehavior
        Stability:
            stable
        """

        updateBehavior: str
        """``CfnCrawler.SchemaChangePolicyProperty.UpdateBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-schemachangepolicy.html#cfn-glue-crawler-schemachangepolicy-updatebehavior
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnCrawler.TargetsProperty", jsii_struct_bases=[])
    class TargetsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-targets.html
        Stability:
            stable
        """
        jdbcTargets: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCrawler.JdbcTargetProperty"]]]
        """``CfnCrawler.TargetsProperty.JdbcTargets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-targets.html#cfn-glue-crawler-targets-jdbctargets
        Stability:
            stable
        """

        s3Targets: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnCrawler.S3TargetProperty"]]]
        """``CfnCrawler.TargetsProperty.S3Targets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-crawler-targets.html#cfn-glue-crawler-targets-s3targets
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnCrawlerProps(jsii.compat.TypedDict, total=False):
    classifiers: typing.List[str]
    """``AWS::Glue::Crawler.Classifiers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-classifiers
    Stability:
        stable
    """
    configuration: str
    """``AWS::Glue::Crawler.Configuration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-configuration
    Stability:
        stable
    """
    crawlerSecurityConfiguration: str
    """``AWS::Glue::Crawler.CrawlerSecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-crawlersecurityconfiguration
    Stability:
        stable
    """
    description: str
    """``AWS::Glue::Crawler.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-description
    Stability:
        stable
    """
    name: str
    """``AWS::Glue::Crawler.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-name
    Stability:
        stable
    """
    schedule: typing.Union[aws_cdk.core.IResolvable, "CfnCrawler.ScheduleProperty"]
    """``AWS::Glue::Crawler.Schedule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-schedule
    Stability:
        stable
    """
    schemaChangePolicy: typing.Union[aws_cdk.core.IResolvable, "CfnCrawler.SchemaChangePolicyProperty"]
    """``AWS::Glue::Crawler.SchemaChangePolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-schemachangepolicy
    Stability:
        stable
    """
    tablePrefix: str
    """``AWS::Glue::Crawler.TablePrefix``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-tableprefix
    Stability:
        stable
    """
    tags: typing.Any
    """``AWS::Glue::Crawler.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnCrawlerProps", jsii_struct_bases=[_CfnCrawlerProps])
class CfnCrawlerProps(_CfnCrawlerProps):
    """Properties for defining a ``AWS::Glue::Crawler``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html
    Stability:
        stable
    """
    databaseName: str
    """``AWS::Glue::Crawler.DatabaseName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-databasename
    Stability:
        stable
    """

    role: str
    """``AWS::Glue::Crawler.Role``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-role
    Stability:
        stable
    """

    targets: typing.Union[aws_cdk.core.IResolvable, "CfnCrawler.TargetsProperty"]
    """``AWS::Glue::Crawler.Targets``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-crawler.html#cfn-glue-crawler-targets
    Stability:
        stable
    """

class CfnDataCatalogEncryptionSettings(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnDataCatalogEncryptionSettings"):
    """A CloudFormation ``AWS::Glue::DataCatalogEncryptionSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html
    Stability:
        stable
    cloudformationResource:
        AWS::Glue::DataCatalogEncryptionSettings
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, catalog_id: str, data_catalog_encryption_settings: typing.Union[aws_cdk.core.IResolvable, "DataCatalogEncryptionSettingsProperty"]) -> None:
        """Create a new ``AWS::Glue::DataCatalogEncryptionSettings``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            catalog_id: ``AWS::Glue::DataCatalogEncryptionSettings.CatalogId``.
            data_catalog_encryption_settings: ``AWS::Glue::DataCatalogEncryptionSettings.DataCatalogEncryptionSettings``.

        Stability:
            experimental
        """
        props: CfnDataCatalogEncryptionSettingsProps = {"catalogId": catalog_id, "dataCatalogEncryptionSettings": data_catalog_encryption_settings}

        jsii.create(CfnDataCatalogEncryptionSettings, self, [scope, id, props])

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
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> str:
        """``AWS::Glue::DataCatalogEncryptionSettings.CatalogId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-catalogid
        Stability:
            stable
        """
        return jsii.get(self, "catalogId")

    @catalog_id.setter
    def catalog_id(self, value: str):
        return jsii.set(self, "catalogId", value)

    @property
    @jsii.member(jsii_name="dataCatalogEncryptionSettings")
    def data_catalog_encryption_settings(self) -> typing.Union[aws_cdk.core.IResolvable, "DataCatalogEncryptionSettingsProperty"]:
        """``AWS::Glue::DataCatalogEncryptionSettings.DataCatalogEncryptionSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-datacatalogencryptionsettings
        Stability:
            stable
        """
        return jsii.get(self, "dataCatalogEncryptionSettings")

    @data_catalog_encryption_settings.setter
    def data_catalog_encryption_settings(self, value: typing.Union[aws_cdk.core.IResolvable, "DataCatalogEncryptionSettingsProperty"]):
        return jsii.set(self, "dataCatalogEncryptionSettings", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty", jsii_struct_bases=[])
    class ConnectionPasswordEncryptionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-connectionpasswordencryption.html
        Stability:
            stable
        """
        kmsKeyId: str
        """``CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-connectionpasswordencryption.html#cfn-glue-datacatalogencryptionsettings-connectionpasswordencryption-kmskeyid
        Stability:
            stable
        """

        returnConnectionPasswordEncrypted: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty.ReturnConnectionPasswordEncrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-connectionpasswordencryption.html#cfn-glue-datacatalogencryptionsettings-connectionpasswordencryption-returnconnectionpasswordencrypted
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty", jsii_struct_bases=[])
    class DataCatalogEncryptionSettingsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-datacatalogencryptionsettings.html
        Stability:
            stable
        """
        connectionPasswordEncryption: typing.Union[aws_cdk.core.IResolvable, "CfnDataCatalogEncryptionSettings.ConnectionPasswordEncryptionProperty"]
        """``CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty.ConnectionPasswordEncryption``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-datacatalogencryptionsettings-connectionpasswordencryption
        Stability:
            stable
        """

        encryptionAtRest: typing.Union[aws_cdk.core.IResolvable, "CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty"]
        """``CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty.EncryptionAtRest``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-datacatalogencryptionsettings-encryptionatrest
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty", jsii_struct_bases=[])
    class EncryptionAtRestProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-encryptionatrest.html
        Stability:
            stable
        """
        catalogEncryptionMode: str
        """``CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty.CatalogEncryptionMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-encryptionatrest.html#cfn-glue-datacatalogencryptionsettings-encryptionatrest-catalogencryptionmode
        Stability:
            stable
        """

        sseAwsKmsKeyId: str
        """``CfnDataCatalogEncryptionSettings.EncryptionAtRestProperty.SseAwsKmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-datacatalogencryptionsettings-encryptionatrest.html#cfn-glue-datacatalogencryptionsettings-encryptionatrest-sseawskmskeyid
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDataCatalogEncryptionSettingsProps", jsii_struct_bases=[])
class CfnDataCatalogEncryptionSettingsProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Glue::DataCatalogEncryptionSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html
    Stability:
        stable
    """
    catalogId: str
    """``AWS::Glue::DataCatalogEncryptionSettings.CatalogId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-catalogid
    Stability:
        stable
    """

    dataCatalogEncryptionSettings: typing.Union[aws_cdk.core.IResolvable, "CfnDataCatalogEncryptionSettings.DataCatalogEncryptionSettingsProperty"]
    """``AWS::Glue::DataCatalogEncryptionSettings.DataCatalogEncryptionSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-datacatalogencryptionsettings.html#cfn-glue-datacatalogencryptionsettings-datacatalogencryptionsettings
    Stability:
        stable
    """

class CfnDatabase(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnDatabase"):
    """A CloudFormation ``AWS::Glue::Database``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html
    Stability:
        stable
    cloudformationResource:
        AWS::Glue::Database
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, catalog_id: str, database_input: typing.Union[aws_cdk.core.IResolvable, "DatabaseInputProperty"]) -> None:
        """Create a new ``AWS::Glue::Database``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            catalog_id: ``AWS::Glue::Database.CatalogId``.
            database_input: ``AWS::Glue::Database.DatabaseInput``.

        Stability:
            experimental
        """
        props: CfnDatabaseProps = {"catalogId": catalog_id, "databaseInput": database_input}

        jsii.create(CfnDatabase, self, [scope, id, props])

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
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> str:
        """``AWS::Glue::Database.CatalogId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html#cfn-glue-database-catalogid
        Stability:
            stable
        """
        return jsii.get(self, "catalogId")

    @catalog_id.setter
    def catalog_id(self, value: str):
        return jsii.set(self, "catalogId", value)

    @property
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Union[aws_cdk.core.IResolvable, "DatabaseInputProperty"]:
        """``AWS::Glue::Database.DatabaseInput``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html#cfn-glue-database-databaseinput
        Stability:
            stable
        """
        return jsii.get(self, "databaseInput")

    @database_input.setter
    def database_input(self, value: typing.Union[aws_cdk.core.IResolvable, "DatabaseInputProperty"]):
        return jsii.set(self, "databaseInput", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDatabase.DatabaseInputProperty", jsii_struct_bases=[])
    class DatabaseInputProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html
        Stability:
            stable
        """
        description: str
        """``CfnDatabase.DatabaseInputProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-description
        Stability:
            stable
        """

        locationUri: str
        """``CfnDatabase.DatabaseInputProperty.LocationUri``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-locationuri
        Stability:
            stable
        """

        name: str
        """``CfnDatabase.DatabaseInputProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-name
        Stability:
            stable
        """

        parameters: typing.Any
        """``CfnDatabase.DatabaseInputProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-database-databaseinput.html#cfn-glue-database-databaseinput-parameters
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDatabaseProps", jsii_struct_bases=[])
class CfnDatabaseProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Glue::Database``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html
    Stability:
        stable
    """
    catalogId: str
    """``AWS::Glue::Database.CatalogId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html#cfn-glue-database-catalogid
    Stability:
        stable
    """

    databaseInput: typing.Union[aws_cdk.core.IResolvable, "CfnDatabase.DatabaseInputProperty"]
    """``AWS::Glue::Database.DatabaseInput``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-database.html#cfn-glue-database-databaseinput
    Stability:
        stable
    """

class CfnDevEndpoint(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnDevEndpoint"):
    """A CloudFormation ``AWS::Glue::DevEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html
    Stability:
        stable
    cloudformationResource:
        AWS::Glue::DevEndpoint
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, role_arn: str, endpoint_name: typing.Optional[str]=None, extra_jars_s3_path: typing.Optional[str]=None, extra_python_libs_s3_path: typing.Optional[str]=None, number_of_nodes: typing.Optional[jsii.Number]=None, public_key: typing.Optional[str]=None, security_configuration: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, subnet_id: typing.Optional[str]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Glue::DevEndpoint``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            role_arn: ``AWS::Glue::DevEndpoint.RoleArn``.
            endpoint_name: ``AWS::Glue::DevEndpoint.EndpointName``.
            extra_jars_s3_path: ``AWS::Glue::DevEndpoint.ExtraJarsS3Path``.
            extra_python_libs_s3_path: ``AWS::Glue::DevEndpoint.ExtraPythonLibsS3Path``.
            number_of_nodes: ``AWS::Glue::DevEndpoint.NumberOfNodes``.
            public_key: ``AWS::Glue::DevEndpoint.PublicKey``.
            security_configuration: ``AWS::Glue::DevEndpoint.SecurityConfiguration``.
            security_group_ids: ``AWS::Glue::DevEndpoint.SecurityGroupIds``.
            subnet_id: ``AWS::Glue::DevEndpoint.SubnetId``.
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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Glue::DevEndpoint.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """``AWS::Glue::DevEndpoint.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-rolearn
        Stability:
            stable
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: str):
        return jsii.set(self, "roleArn", value)

    @property
    @jsii.member(jsii_name="endpointName")
    def endpoint_name(self) -> typing.Optional[str]:
        """``AWS::Glue::DevEndpoint.EndpointName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-endpointname
        Stability:
            stable
        """
        return jsii.get(self, "endpointName")

    @endpoint_name.setter
    def endpoint_name(self, value: typing.Optional[str]):
        return jsii.set(self, "endpointName", value)

    @property
    @jsii.member(jsii_name="extraJarsS3Path")
    def extra_jars_s3_path(self) -> typing.Optional[str]:
        """``AWS::Glue::DevEndpoint.ExtraJarsS3Path``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-extrajarss3path
        Stability:
            stable
        """
        return jsii.get(self, "extraJarsS3Path")

    @extra_jars_s3_path.setter
    def extra_jars_s3_path(self, value: typing.Optional[str]):
        return jsii.set(self, "extraJarsS3Path", value)

    @property
    @jsii.member(jsii_name="extraPythonLibsS3Path")
    def extra_python_libs_s3_path(self) -> typing.Optional[str]:
        """``AWS::Glue::DevEndpoint.ExtraPythonLibsS3Path``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-extrapythonlibss3path
        Stability:
            stable
        """
        return jsii.get(self, "extraPythonLibsS3Path")

    @extra_python_libs_s3_path.setter
    def extra_python_libs_s3_path(self, value: typing.Optional[str]):
        return jsii.set(self, "extraPythonLibsS3Path", value)

    @property
    @jsii.member(jsii_name="numberOfNodes")
    def number_of_nodes(self) -> typing.Optional[jsii.Number]:
        """``AWS::Glue::DevEndpoint.NumberOfNodes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-numberofnodes
        Stability:
            stable
        """
        return jsii.get(self, "numberOfNodes")

    @number_of_nodes.setter
    def number_of_nodes(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "numberOfNodes", value)

    @property
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> typing.Optional[str]:
        """``AWS::Glue::DevEndpoint.PublicKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-publickey
        Stability:
            stable
        """
        return jsii.get(self, "publicKey")

    @public_key.setter
    def public_key(self, value: typing.Optional[str]):
        return jsii.set(self, "publicKey", value)

    @property
    @jsii.member(jsii_name="securityConfiguration")
    def security_configuration(self) -> typing.Optional[str]:
        """``AWS::Glue::DevEndpoint.SecurityConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-securityconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "securityConfiguration")

    @security_configuration.setter
    def security_configuration(self, value: typing.Optional[str]):
        return jsii.set(self, "securityConfiguration", value)

    @property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Glue::DevEndpoint.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-securitygroupids
        Stability:
            stable
        """
        return jsii.get(self, "securityGroupIds")

    @security_group_ids.setter
    def security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "securityGroupIds", value)

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> typing.Optional[str]:
        """``AWS::Glue::DevEndpoint.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-subnetid
        Stability:
            stable
        """
        return jsii.get(self, "subnetId")

    @subnet_id.setter
    def subnet_id(self, value: typing.Optional[str]):
        return jsii.set(self, "subnetId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDevEndpointProps(jsii.compat.TypedDict, total=False):
    endpointName: str
    """``AWS::Glue::DevEndpoint.EndpointName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-endpointname
    Stability:
        stable
    """
    extraJarsS3Path: str
    """``AWS::Glue::DevEndpoint.ExtraJarsS3Path``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-extrajarss3path
    Stability:
        stable
    """
    extraPythonLibsS3Path: str
    """``AWS::Glue::DevEndpoint.ExtraPythonLibsS3Path``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-extrapythonlibss3path
    Stability:
        stable
    """
    numberOfNodes: jsii.Number
    """``AWS::Glue::DevEndpoint.NumberOfNodes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-numberofnodes
    Stability:
        stable
    """
    publicKey: str
    """``AWS::Glue::DevEndpoint.PublicKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-publickey
    Stability:
        stable
    """
    securityConfiguration: str
    """``AWS::Glue::DevEndpoint.SecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-securityconfiguration
    Stability:
        stable
    """
    securityGroupIds: typing.List[str]
    """``AWS::Glue::DevEndpoint.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-securitygroupids
    Stability:
        stable
    """
    subnetId: str
    """``AWS::Glue::DevEndpoint.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-subnetid
    Stability:
        stable
    """
    tags: typing.Any
    """``AWS::Glue::DevEndpoint.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnDevEndpointProps", jsii_struct_bases=[_CfnDevEndpointProps])
class CfnDevEndpointProps(_CfnDevEndpointProps):
    """Properties for defining a ``AWS::Glue::DevEndpoint``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html
    Stability:
        stable
    """
    roleArn: str
    """``AWS::Glue::DevEndpoint.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-devendpoint.html#cfn-glue-devendpoint-rolearn
    Stability:
        stable
    """

class CfnJob(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnJob"):
    """A CloudFormation ``AWS::Glue::Job``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html
    Stability:
        stable
    cloudformationResource:
        AWS::Glue::Job
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, command: typing.Union[aws_cdk.core.IResolvable, "JobCommandProperty"], role: str, allocated_capacity: typing.Optional[jsii.Number]=None, connections: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ConnectionsListProperty"]]]=None, default_arguments: typing.Any=None, description: typing.Optional[str]=None, execution_property: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ExecutionPropertyProperty"]]]=None, log_uri: typing.Optional[str]=None, max_retries: typing.Optional[jsii.Number]=None, name: typing.Optional[str]=None, security_configuration: typing.Optional[str]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::Glue::Job``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            command: ``AWS::Glue::Job.Command``.
            role: ``AWS::Glue::Job.Role``.
            allocated_capacity: ``AWS::Glue::Job.AllocatedCapacity``.
            connections: ``AWS::Glue::Job.Connections``.
            default_arguments: ``AWS::Glue::Job.DefaultArguments``.
            description: ``AWS::Glue::Job.Description``.
            execution_property: ``AWS::Glue::Job.ExecutionProperty``.
            log_uri: ``AWS::Glue::Job.LogUri``.
            max_retries: ``AWS::Glue::Job.MaxRetries``.
            name: ``AWS::Glue::Job.Name``.
            security_configuration: ``AWS::Glue::Job.SecurityConfiguration``.
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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Glue::Job.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="command")
    def command(self) -> typing.Union[aws_cdk.core.IResolvable, "JobCommandProperty"]:
        """``AWS::Glue::Job.Command``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-command
        Stability:
            stable
        """
        return jsii.get(self, "command")

    @command.setter
    def command(self, value: typing.Union[aws_cdk.core.IResolvable, "JobCommandProperty"]):
        return jsii.set(self, "command", value)

    @property
    @jsii.member(jsii_name="defaultArguments")
    def default_arguments(self) -> typing.Any:
        """``AWS::Glue::Job.DefaultArguments``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-defaultarguments
        Stability:
            stable
        """
        return jsii.get(self, "defaultArguments")

    @default_arguments.setter
    def default_arguments(self, value: typing.Any):
        return jsii.set(self, "defaultArguments", value)

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> str:
        """``AWS::Glue::Job.Role``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-role
        Stability:
            stable
        """
        return jsii.get(self, "role")

    @role.setter
    def role(self, value: str):
        return jsii.set(self, "role", value)

    @property
    @jsii.member(jsii_name="allocatedCapacity")
    def allocated_capacity(self) -> typing.Optional[jsii.Number]:
        """``AWS::Glue::Job.AllocatedCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-allocatedcapacity
        Stability:
            stable
        """
        return jsii.get(self, "allocatedCapacity")

    @allocated_capacity.setter
    def allocated_capacity(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "allocatedCapacity", value)

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ConnectionsListProperty"]]]:
        """``AWS::Glue::Job.Connections``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-connections
        Stability:
            stable
        """
        return jsii.get(self, "connections")

    @connections.setter
    def connections(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ConnectionsListProperty"]]]):
        return jsii.set(self, "connections", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::Glue::Job.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="executionProperty")
    def execution_property(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ExecutionPropertyProperty"]]]:
        """``AWS::Glue::Job.ExecutionProperty``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-executionproperty
        Stability:
            stable
        """
        return jsii.get(self, "executionProperty")

    @execution_property.setter
    def execution_property(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ExecutionPropertyProperty"]]]):
        return jsii.set(self, "executionProperty", value)

    @property
    @jsii.member(jsii_name="logUri")
    def log_uri(self) -> typing.Optional[str]:
        """``AWS::Glue::Job.LogUri``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-loguri
        Stability:
            stable
        """
        return jsii.get(self, "logUri")

    @log_uri.setter
    def log_uri(self, value: typing.Optional[str]):
        return jsii.set(self, "logUri", value)

    @property
    @jsii.member(jsii_name="maxRetries")
    def max_retries(self) -> typing.Optional[jsii.Number]:
        """``AWS::Glue::Job.MaxRetries``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-maxretries
        Stability:
            stable
        """
        return jsii.get(self, "maxRetries")

    @max_retries.setter
    def max_retries(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "maxRetries", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Glue::Job.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="securityConfiguration")
    def security_configuration(self) -> typing.Optional[str]:
        """``AWS::Glue::Job.SecurityConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-securityconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "securityConfiguration")

    @security_configuration.setter
    def security_configuration(self, value: typing.Optional[str]):
        return jsii.set(self, "securityConfiguration", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnJob.ConnectionsListProperty", jsii_struct_bases=[])
    class ConnectionsListProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-connectionslist.html
        Stability:
            stable
        """
        connections: typing.List[str]
        """``CfnJob.ConnectionsListProperty.Connections``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-connectionslist.html#cfn-glue-job-connectionslist-connections
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnJob.ExecutionPropertyProperty", jsii_struct_bases=[])
    class ExecutionPropertyProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-executionproperty.html
        Stability:
            stable
        """
        maxConcurrentRuns: jsii.Number
        """``CfnJob.ExecutionPropertyProperty.MaxConcurrentRuns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-executionproperty.html#cfn-glue-job-executionproperty-maxconcurrentruns
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnJob.JobCommandProperty", jsii_struct_bases=[])
    class JobCommandProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-jobcommand.html
        Stability:
            stable
        """
        name: str
        """``CfnJob.JobCommandProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-jobcommand.html#cfn-glue-job-jobcommand-name
        Stability:
            stable
        """

        scriptLocation: str
        """``CfnJob.JobCommandProperty.ScriptLocation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-jobcommand.html#cfn-glue-job-jobcommand-scriptlocation
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnJobProps(jsii.compat.TypedDict, total=False):
    allocatedCapacity: jsii.Number
    """``AWS::Glue::Job.AllocatedCapacity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-allocatedcapacity
    Stability:
        stable
    """
    connections: typing.Union[aws_cdk.core.IResolvable, "CfnJob.ConnectionsListProperty"]
    """``AWS::Glue::Job.Connections``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-connections
    Stability:
        stable
    """
    defaultArguments: typing.Any
    """``AWS::Glue::Job.DefaultArguments``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-defaultarguments
    Stability:
        stable
    """
    description: str
    """``AWS::Glue::Job.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-description
    Stability:
        stable
    """
    executionProperty: typing.Union[aws_cdk.core.IResolvable, "CfnJob.ExecutionPropertyProperty"]
    """``AWS::Glue::Job.ExecutionProperty``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-executionproperty
    Stability:
        stable
    """
    logUri: str
    """``AWS::Glue::Job.LogUri``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-loguri
    Stability:
        stable
    """
    maxRetries: jsii.Number
    """``AWS::Glue::Job.MaxRetries``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-maxretries
    Stability:
        stable
    """
    name: str
    """``AWS::Glue::Job.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-name
    Stability:
        stable
    """
    securityConfiguration: str
    """``AWS::Glue::Job.SecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-securityconfiguration
    Stability:
        stable
    """
    tags: typing.Any
    """``AWS::Glue::Job.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnJobProps", jsii_struct_bases=[_CfnJobProps])
class CfnJobProps(_CfnJobProps):
    """Properties for defining a ``AWS::Glue::Job``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html
    Stability:
        stable
    """
    command: typing.Union[aws_cdk.core.IResolvable, "CfnJob.JobCommandProperty"]
    """``AWS::Glue::Job.Command``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-command
    Stability:
        stable
    """

    role: str
    """``AWS::Glue::Job.Role``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-job.html#cfn-glue-job-role
    Stability:
        stable
    """

class CfnPartition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnPartition"):
    """A CloudFormation ``AWS::Glue::Partition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html
    Stability:
        stable
    cloudformationResource:
        AWS::Glue::Partition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, catalog_id: str, database_name: str, partition_input: typing.Union[aws_cdk.core.IResolvable, "PartitionInputProperty"], table_name: str) -> None:
        """Create a new ``AWS::Glue::Partition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            catalog_id: ``AWS::Glue::Partition.CatalogId``.
            database_name: ``AWS::Glue::Partition.DatabaseName``.
            partition_input: ``AWS::Glue::Partition.PartitionInput``.
            table_name: ``AWS::Glue::Partition.TableName``.

        Stability:
            experimental
        """
        props: CfnPartitionProps = {"catalogId": catalog_id, "databaseName": database_name, "partitionInput": partition_input, "tableName": table_name}

        jsii.create(CfnPartition, self, [scope, id, props])

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
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> str:
        """``AWS::Glue::Partition.CatalogId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-catalogid
        Stability:
            stable
        """
        return jsii.get(self, "catalogId")

    @catalog_id.setter
    def catalog_id(self, value: str):
        return jsii.set(self, "catalogId", value)

    @property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> str:
        """``AWS::Glue::Partition.DatabaseName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-databasename
        Stability:
            stable
        """
        return jsii.get(self, "databaseName")

    @database_name.setter
    def database_name(self, value: str):
        return jsii.set(self, "databaseName", value)

    @property
    @jsii.member(jsii_name="partitionInput")
    def partition_input(self) -> typing.Union[aws_cdk.core.IResolvable, "PartitionInputProperty"]:
        """``AWS::Glue::Partition.PartitionInput``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-partitioninput
        Stability:
            stable
        """
        return jsii.get(self, "partitionInput")

    @partition_input.setter
    def partition_input(self, value: typing.Union[aws_cdk.core.IResolvable, "PartitionInputProperty"]):
        return jsii.set(self, "partitionInput", value)

    @property
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> str:
        """``AWS::Glue::Partition.TableName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-tablename
        Stability:
            stable
        """
        return jsii.get(self, "tableName")

    @table_name.setter
    def table_name(self, value: str):
        return jsii.set(self, "tableName", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ColumnProperty(jsii.compat.TypedDict, total=False):
        comment: str
        """``CfnPartition.ColumnProperty.Comment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-column.html#cfn-glue-partition-column-comment
        Stability:
            stable
        """
        type: str
        """``CfnPartition.ColumnProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-column.html#cfn-glue-partition-column-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartition.ColumnProperty", jsii_struct_bases=[_ColumnProperty])
    class ColumnProperty(_ColumnProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-column.html
        Stability:
            stable
        """
        name: str
        """``CfnPartition.ColumnProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-column.html#cfn-glue-partition-column-name
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _OrderProperty(jsii.compat.TypedDict, total=False):
        sortOrder: jsii.Number
        """``CfnPartition.OrderProperty.SortOrder``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-order.html#cfn-glue-partition-order-sortorder
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartition.OrderProperty", jsii_struct_bases=[_OrderProperty])
    class OrderProperty(_OrderProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-order.html
        Stability:
            stable
        """
        column: str
        """``CfnPartition.OrderProperty.Column``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-order.html#cfn-glue-partition-order-column
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _PartitionInputProperty(jsii.compat.TypedDict, total=False):
        parameters: typing.Any
        """``CfnPartition.PartitionInputProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-partitioninput.html#cfn-glue-partition-partitioninput-parameters
        Stability:
            stable
        """
        storageDescriptor: typing.Union[aws_cdk.core.IResolvable, "CfnPartition.StorageDescriptorProperty"]
        """``CfnPartition.PartitionInputProperty.StorageDescriptor``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-partitioninput.html#cfn-glue-partition-partitioninput-storagedescriptor
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartition.PartitionInputProperty", jsii_struct_bases=[_PartitionInputProperty])
    class PartitionInputProperty(_PartitionInputProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-partitioninput.html
        Stability:
            stable
        """
        values: typing.List[str]
        """``CfnPartition.PartitionInputProperty.Values``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-partitioninput.html#cfn-glue-partition-partitioninput-values
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartition.SerdeInfoProperty", jsii_struct_bases=[])
    class SerdeInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-serdeinfo.html
        Stability:
            stable
        """
        name: str
        """``CfnPartition.SerdeInfoProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-serdeinfo.html#cfn-glue-partition-serdeinfo-name
        Stability:
            stable
        """

        parameters: typing.Any
        """``CfnPartition.SerdeInfoProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-serdeinfo.html#cfn-glue-partition-serdeinfo-parameters
        Stability:
            stable
        """

        serializationLibrary: str
        """``CfnPartition.SerdeInfoProperty.SerializationLibrary``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-serdeinfo.html#cfn-glue-partition-serdeinfo-serializationlibrary
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartition.SkewedInfoProperty", jsii_struct_bases=[])
    class SkewedInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-skewedinfo.html
        Stability:
            stable
        """
        skewedColumnNames: typing.List[str]
        """``CfnPartition.SkewedInfoProperty.SkewedColumnNames``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-skewedinfo.html#cfn-glue-partition-skewedinfo-skewedcolumnnames
        Stability:
            stable
        """

        skewedColumnValueLocationMaps: typing.Any
        """``CfnPartition.SkewedInfoProperty.SkewedColumnValueLocationMaps``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-skewedinfo.html#cfn-glue-partition-skewedinfo-skewedcolumnvaluelocationmaps
        Stability:
            stable
        """

        skewedColumnValues: typing.List[str]
        """``CfnPartition.SkewedInfoProperty.SkewedColumnValues``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-skewedinfo.html#cfn-glue-partition-skewedinfo-skewedcolumnvalues
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartition.StorageDescriptorProperty", jsii_struct_bases=[])
    class StorageDescriptorProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html
        Stability:
            stable
        """
        bucketColumns: typing.List[str]
        """``CfnPartition.StorageDescriptorProperty.BucketColumns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-bucketcolumns
        Stability:
            stable
        """

        columns: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPartition.ColumnProperty"]]]
        """``CfnPartition.StorageDescriptorProperty.Columns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-columns
        Stability:
            stable
        """

        compressed: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnPartition.StorageDescriptorProperty.Compressed``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-compressed
        Stability:
            stable
        """

        inputFormat: str
        """``CfnPartition.StorageDescriptorProperty.InputFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-inputformat
        Stability:
            stable
        """

        location: str
        """``CfnPartition.StorageDescriptorProperty.Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-location
        Stability:
            stable
        """

        numberOfBuckets: jsii.Number
        """``CfnPartition.StorageDescriptorProperty.NumberOfBuckets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-numberofbuckets
        Stability:
            stable
        """

        outputFormat: str
        """``CfnPartition.StorageDescriptorProperty.OutputFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-outputformat
        Stability:
            stable
        """

        parameters: typing.Any
        """``CfnPartition.StorageDescriptorProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-parameters
        Stability:
            stable
        """

        serdeInfo: typing.Union[aws_cdk.core.IResolvable, "CfnPartition.SerdeInfoProperty"]
        """``CfnPartition.StorageDescriptorProperty.SerdeInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-serdeinfo
        Stability:
            stable
        """

        skewedInfo: typing.Union[aws_cdk.core.IResolvable, "CfnPartition.SkewedInfoProperty"]
        """``CfnPartition.StorageDescriptorProperty.SkewedInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-skewedinfo
        Stability:
            stable
        """

        sortColumns: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPartition.OrderProperty"]]]
        """``CfnPartition.StorageDescriptorProperty.SortColumns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-sortcolumns
        Stability:
            stable
        """

        storedAsSubDirectories: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnPartition.StorageDescriptorProperty.StoredAsSubDirectories``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-partition-storagedescriptor.html#cfn-glue-partition-storagedescriptor-storedassubdirectories
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnPartitionProps", jsii_struct_bases=[])
class CfnPartitionProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Glue::Partition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html
    Stability:
        stable
    """
    catalogId: str
    """``AWS::Glue::Partition.CatalogId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-catalogid
    Stability:
        stable
    """

    databaseName: str
    """``AWS::Glue::Partition.DatabaseName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-databasename
    Stability:
        stable
    """

    partitionInput: typing.Union[aws_cdk.core.IResolvable, "CfnPartition.PartitionInputProperty"]
    """``AWS::Glue::Partition.PartitionInput``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-partitioninput
    Stability:
        stable
    """

    tableName: str
    """``AWS::Glue::Partition.TableName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-partition.html#cfn-glue-partition-tablename
    Stability:
        stable
    """

class CfnSecurityConfiguration(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnSecurityConfiguration"):
    """A CloudFormation ``AWS::Glue::SecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html
    Stability:
        stable
    cloudformationResource:
        AWS::Glue::SecurityConfiguration
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, encryption_configuration: typing.Union[aws_cdk.core.IResolvable, "EncryptionConfigurationProperty"], name: str) -> None:
        """Create a new ``AWS::Glue::SecurityConfiguration``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            encryption_configuration: ``AWS::Glue::SecurityConfiguration.EncryptionConfiguration``.
            name: ``AWS::Glue::SecurityConfiguration.Name``.

        Stability:
            experimental
        """
        props: CfnSecurityConfigurationProps = {"encryptionConfiguration": encryption_configuration, "name": name}

        jsii.create(CfnSecurityConfiguration, self, [scope, id, props])

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
    @jsii.member(jsii_name="encryptionConfiguration")
    def encryption_configuration(self) -> typing.Union[aws_cdk.core.IResolvable, "EncryptionConfigurationProperty"]:
        """``AWS::Glue::SecurityConfiguration.EncryptionConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "encryptionConfiguration")

    @encryption_configuration.setter
    def encryption_configuration(self, value: typing.Union[aws_cdk.core.IResolvable, "EncryptionConfigurationProperty"]):
        return jsii.set(self, "encryptionConfiguration", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::Glue::SecurityConfiguration.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html#cfn-glue-securityconfiguration-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnSecurityConfiguration.CloudWatchEncryptionProperty", jsii_struct_bases=[])
    class CloudWatchEncryptionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-cloudwatchencryption.html
        Stability:
            stable
        """
        cloudWatchEncryptionMode: str
        """``CfnSecurityConfiguration.CloudWatchEncryptionProperty.CloudWatchEncryptionMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-cloudwatchencryption.html#cfn-glue-securityconfiguration-cloudwatchencryption-cloudwatchencryptionmode
        Stability:
            stable
        """

        kmsKeyArn: str
        """``CfnSecurityConfiguration.CloudWatchEncryptionProperty.KmsKeyArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-cloudwatchencryption.html#cfn-glue-securityconfiguration-cloudwatchencryption-kmskeyarn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnSecurityConfiguration.EncryptionConfigurationProperty", jsii_struct_bases=[])
    class EncryptionConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-encryptionconfiguration.html
        Stability:
            stable
        """
        cloudWatchEncryption: typing.Union[aws_cdk.core.IResolvable, "CfnSecurityConfiguration.CloudWatchEncryptionProperty"]
        """``CfnSecurityConfiguration.EncryptionConfigurationProperty.CloudWatchEncryption``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-encryptionconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration-cloudwatchencryption
        Stability:
            stable
        """

        jobBookmarksEncryption: typing.Union[aws_cdk.core.IResolvable, "CfnSecurityConfiguration.JobBookmarksEncryptionProperty"]
        """``CfnSecurityConfiguration.EncryptionConfigurationProperty.JobBookmarksEncryption``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-encryptionconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration-jobbookmarksencryption
        Stability:
            stable
        """

        s3Encryptions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSecurityConfiguration.S3EncryptionProperty"]]]
        """``CfnSecurityConfiguration.EncryptionConfigurationProperty.S3Encryptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-encryptionconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration-s3encryptions
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnSecurityConfiguration.JobBookmarksEncryptionProperty", jsii_struct_bases=[])
    class JobBookmarksEncryptionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-jobbookmarksencryption.html
        Stability:
            stable
        """
        jobBookmarksEncryptionMode: str
        """``CfnSecurityConfiguration.JobBookmarksEncryptionProperty.JobBookmarksEncryptionMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-jobbookmarksencryption.html#cfn-glue-securityconfiguration-jobbookmarksencryption-jobbookmarksencryptionmode
        Stability:
            stable
        """

        kmsKeyArn: str
        """``CfnSecurityConfiguration.JobBookmarksEncryptionProperty.KmsKeyArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-jobbookmarksencryption.html#cfn-glue-securityconfiguration-jobbookmarksencryption-kmskeyarn
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnSecurityConfiguration.S3EncryptionProperty", jsii_struct_bases=[])
    class S3EncryptionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-s3encryption.html
        Stability:
            stable
        """
        kmsKeyArn: str
        """``CfnSecurityConfiguration.S3EncryptionProperty.KmsKeyArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-s3encryption.html#cfn-glue-securityconfiguration-s3encryption-kmskeyarn
        Stability:
            stable
        """

        s3EncryptionMode: str
        """``CfnSecurityConfiguration.S3EncryptionProperty.S3EncryptionMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-securityconfiguration-s3encryption.html#cfn-glue-securityconfiguration-s3encryption-s3encryptionmode
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnSecurityConfigurationProps", jsii_struct_bases=[])
class CfnSecurityConfigurationProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Glue::SecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html
    Stability:
        stable
    """
    encryptionConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnSecurityConfiguration.EncryptionConfigurationProperty"]
    """``AWS::Glue::SecurityConfiguration.EncryptionConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html#cfn-glue-securityconfiguration-encryptionconfiguration
    Stability:
        stable
    """

    name: str
    """``AWS::Glue::SecurityConfiguration.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-securityconfiguration.html#cfn-glue-securityconfiguration-name
    Stability:
        stable
    """

class CfnTable(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnTable"):
    """A CloudFormation ``AWS::Glue::Table``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html
    Stability:
        stable
    cloudformationResource:
        AWS::Glue::Table
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, catalog_id: str, database_name: str, table_input: typing.Union[aws_cdk.core.IResolvable, "TableInputProperty"]) -> None:
        """Create a new ``AWS::Glue::Table``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            catalog_id: ``AWS::Glue::Table.CatalogId``.
            database_name: ``AWS::Glue::Table.DatabaseName``.
            table_input: ``AWS::Glue::Table.TableInput``.

        Stability:
            experimental
        """
        props: CfnTableProps = {"catalogId": catalog_id, "databaseName": database_name, "tableInput": table_input}

        jsii.create(CfnTable, self, [scope, id, props])

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
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> str:
        """``AWS::Glue::Table.CatalogId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-catalogid
        Stability:
            stable
        """
        return jsii.get(self, "catalogId")

    @catalog_id.setter
    def catalog_id(self, value: str):
        return jsii.set(self, "catalogId", value)

    @property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> str:
        """``AWS::Glue::Table.DatabaseName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-databasename
        Stability:
            stable
        """
        return jsii.get(self, "databaseName")

    @database_name.setter
    def database_name(self, value: str):
        return jsii.set(self, "databaseName", value)

    @property
    @jsii.member(jsii_name="tableInput")
    def table_input(self) -> typing.Union[aws_cdk.core.IResolvable, "TableInputProperty"]:
        """``AWS::Glue::Table.TableInput``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-tableinput
        Stability:
            stable
        """
        return jsii.get(self, "tableInput")

    @table_input.setter
    def table_input(self, value: typing.Union[aws_cdk.core.IResolvable, "TableInputProperty"]):
        return jsii.set(self, "tableInput", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ColumnProperty(jsii.compat.TypedDict, total=False):
        comment: str
        """``CfnTable.ColumnProperty.Comment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-column.html#cfn-glue-table-column-comment
        Stability:
            stable
        """
        type: str
        """``CfnTable.ColumnProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-column.html#cfn-glue-table-column-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTable.ColumnProperty", jsii_struct_bases=[_ColumnProperty])
    class ColumnProperty(_ColumnProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-column.html
        Stability:
            stable
        """
        name: str
        """``CfnTable.ColumnProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-column.html#cfn-glue-table-column-name
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTable.OrderProperty", jsii_struct_bases=[])
    class OrderProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-order.html
        Stability:
            stable
        """
        column: str
        """``CfnTable.OrderProperty.Column``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-order.html#cfn-glue-table-order-column
        Stability:
            stable
        """

        sortOrder: jsii.Number
        """``CfnTable.OrderProperty.SortOrder``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-order.html#cfn-glue-table-order-sortorder
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTable.SerdeInfoProperty", jsii_struct_bases=[])
    class SerdeInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-serdeinfo.html
        Stability:
            stable
        """
        name: str
        """``CfnTable.SerdeInfoProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-serdeinfo.html#cfn-glue-table-serdeinfo-name
        Stability:
            stable
        """

        parameters: typing.Any
        """``CfnTable.SerdeInfoProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-serdeinfo.html#cfn-glue-table-serdeinfo-parameters
        Stability:
            stable
        """

        serializationLibrary: str
        """``CfnTable.SerdeInfoProperty.SerializationLibrary``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-serdeinfo.html#cfn-glue-table-serdeinfo-serializationlibrary
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTable.SkewedInfoProperty", jsii_struct_bases=[])
    class SkewedInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-skewedinfo.html
        Stability:
            stable
        """
        skewedColumnNames: typing.List[str]
        """``CfnTable.SkewedInfoProperty.SkewedColumnNames``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-skewedinfo.html#cfn-glue-table-skewedinfo-skewedcolumnnames
        Stability:
            stable
        """

        skewedColumnValueLocationMaps: typing.Any
        """``CfnTable.SkewedInfoProperty.SkewedColumnValueLocationMaps``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-skewedinfo.html#cfn-glue-table-skewedinfo-skewedcolumnvaluelocationmaps
        Stability:
            stable
        """

        skewedColumnValues: typing.List[str]
        """``CfnTable.SkewedInfoProperty.SkewedColumnValues``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-skewedinfo.html#cfn-glue-table-skewedinfo-skewedcolumnvalues
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTable.StorageDescriptorProperty", jsii_struct_bases=[])
    class StorageDescriptorProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html
        Stability:
            stable
        """
        bucketColumns: typing.List[str]
        """``CfnTable.StorageDescriptorProperty.BucketColumns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-bucketcolumns
        Stability:
            stable
        """

        columns: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnTable.ColumnProperty"]]]
        """``CfnTable.StorageDescriptorProperty.Columns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-columns
        Stability:
            stable
        """

        compressed: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnTable.StorageDescriptorProperty.Compressed``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-compressed
        Stability:
            stable
        """

        inputFormat: str
        """``CfnTable.StorageDescriptorProperty.InputFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-inputformat
        Stability:
            stable
        """

        location: str
        """``CfnTable.StorageDescriptorProperty.Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-location
        Stability:
            stable
        """

        numberOfBuckets: jsii.Number
        """``CfnTable.StorageDescriptorProperty.NumberOfBuckets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-numberofbuckets
        Stability:
            stable
        """

        outputFormat: str
        """``CfnTable.StorageDescriptorProperty.OutputFormat``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-outputformat
        Stability:
            stable
        """

        parameters: typing.Any
        """``CfnTable.StorageDescriptorProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-parameters
        Stability:
            stable
        """

        serdeInfo: typing.Union[aws_cdk.core.IResolvable, "CfnTable.SerdeInfoProperty"]
        """``CfnTable.StorageDescriptorProperty.SerdeInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-serdeinfo
        Stability:
            stable
        """

        skewedInfo: typing.Union[aws_cdk.core.IResolvable, "CfnTable.SkewedInfoProperty"]
        """``CfnTable.StorageDescriptorProperty.SkewedInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-skewedinfo
        Stability:
            stable
        """

        sortColumns: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnTable.OrderProperty"]]]
        """``CfnTable.StorageDescriptorProperty.SortColumns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-sortcolumns
        Stability:
            stable
        """

        storedAsSubDirectories: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnTable.StorageDescriptorProperty.StoredAsSubDirectories``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-storagedescriptor.html#cfn-glue-table-storagedescriptor-storedassubdirectories
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTable.TableInputProperty", jsii_struct_bases=[])
    class TableInputProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html
        Stability:
            stable
        """
        description: str
        """``CfnTable.TableInputProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-description
        Stability:
            stable
        """

        name: str
        """``CfnTable.TableInputProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-name
        Stability:
            stable
        """

        owner: str
        """``CfnTable.TableInputProperty.Owner``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-owner
        Stability:
            stable
        """

        parameters: typing.Any
        """``CfnTable.TableInputProperty.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-parameters
        Stability:
            stable
        """

        partitionKeys: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnTable.ColumnProperty"]]]
        """``CfnTable.TableInputProperty.PartitionKeys``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-partitionkeys
        Stability:
            stable
        """

        retention: jsii.Number
        """``CfnTable.TableInputProperty.Retention``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-retention
        Stability:
            stable
        """

        storageDescriptor: typing.Union[aws_cdk.core.IResolvable, "CfnTable.StorageDescriptorProperty"]
        """``CfnTable.TableInputProperty.StorageDescriptor``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-storagedescriptor
        Stability:
            stable
        """

        tableType: str
        """``CfnTable.TableInputProperty.TableType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-tabletype
        Stability:
            stable
        """

        viewExpandedText: str
        """``CfnTable.TableInputProperty.ViewExpandedText``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-viewexpandedtext
        Stability:
            stable
        """

        viewOriginalText: str
        """``CfnTable.TableInputProperty.ViewOriginalText``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-table-tableinput.html#cfn-glue-table-tableinput-vieworiginaltext
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTableProps", jsii_struct_bases=[])
class CfnTableProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::Glue::Table``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html
    Stability:
        stable
    """
    catalogId: str
    """``AWS::Glue::Table.CatalogId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-catalogid
    Stability:
        stable
    """

    databaseName: str
    """``AWS::Glue::Table.DatabaseName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-databasename
    Stability:
        stable
    """

    tableInput: typing.Union[aws_cdk.core.IResolvable, "CfnTable.TableInputProperty"]
    """``AWS::Glue::Table.TableInput``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-table.html#cfn-glue-table-tableinput
    Stability:
        stable
    """

class CfnTrigger(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.CfnTrigger"):
    """A CloudFormation ``AWS::Glue::Trigger``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html
    Stability:
        stable
    cloudformationResource:
        AWS::Glue::Trigger
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, actions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ActionProperty"]]], type: str, description: typing.Optional[str]=None, name: typing.Optional[str]=None, predicate: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PredicateProperty"]]]=None, schedule: typing.Optional[str]=None, tags: typing.Any=None) -> None:
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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Glue::Trigger.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ActionProperty"]]]:
        """``AWS::Glue::Trigger.Actions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-actions
        Stability:
            stable
        """
        return jsii.get(self, "actions")

    @actions.setter
    def actions(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ActionProperty"]]]):
        return jsii.set(self, "actions", value)

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """``AWS::Glue::Trigger.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-type
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
        """``AWS::Glue::Trigger.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Glue::Trigger.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="predicate")
    def predicate(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PredicateProperty"]]]:
        """``AWS::Glue::Trigger.Predicate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-predicate
        Stability:
            stable
        """
        return jsii.get(self, "predicate")

    @predicate.setter
    def predicate(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["PredicateProperty"]]]):
        return jsii.set(self, "predicate", value)

    @property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> typing.Optional[str]:
        """``AWS::Glue::Trigger.Schedule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-schedule
        Stability:
            stable
        """
        return jsii.get(self, "schedule")

    @schedule.setter
    def schedule(self, value: typing.Optional[str]):
        return jsii.set(self, "schedule", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTrigger.ActionProperty", jsii_struct_bases=[])
    class ActionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html
        Stability:
            stable
        """
        arguments: typing.Any
        """``CfnTrigger.ActionProperty.Arguments``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html#cfn-glue-trigger-action-arguments
        Stability:
            stable
        """

        jobName: str
        """``CfnTrigger.ActionProperty.JobName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html#cfn-glue-trigger-action-jobname
        Stability:
            stable
        """

        securityConfiguration: str
        """``CfnTrigger.ActionProperty.SecurityConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-action.html#cfn-glue-trigger-action-securityconfiguration
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTrigger.ConditionProperty", jsii_struct_bases=[])
    class ConditionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html
        Stability:
            stable
        """
        jobName: str
        """``CfnTrigger.ConditionProperty.JobName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html#cfn-glue-trigger-condition-jobname
        Stability:
            stable
        """

        logicalOperator: str
        """``CfnTrigger.ConditionProperty.LogicalOperator``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html#cfn-glue-trigger-condition-logicaloperator
        Stability:
            stable
        """

        state: str
        """``CfnTrigger.ConditionProperty.State``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-condition.html#cfn-glue-trigger-condition-state
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTrigger.PredicateProperty", jsii_struct_bases=[])
    class PredicateProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-predicate.html
        Stability:
            stable
        """
        conditions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnTrigger.ConditionProperty"]]]
        """``CfnTrigger.PredicateProperty.Conditions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-predicate.html#cfn-glue-trigger-predicate-conditions
        Stability:
            stable
        """

        logical: str
        """``CfnTrigger.PredicateProperty.Logical``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-trigger-predicate.html#cfn-glue-trigger-predicate-logical
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnTriggerProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::Glue::Trigger.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-description
    Stability:
        stable
    """
    name: str
    """``AWS::Glue::Trigger.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-name
    Stability:
        stable
    """
    predicate: typing.Union[aws_cdk.core.IResolvable, "CfnTrigger.PredicateProperty"]
    """``AWS::Glue::Trigger.Predicate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-predicate
    Stability:
        stable
    """
    schedule: str
    """``AWS::Glue::Trigger.Schedule``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-schedule
    Stability:
        stable
    """
    tags: typing.Any
    """``AWS::Glue::Trigger.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-glue.CfnTriggerProps", jsii_struct_bases=[_CfnTriggerProps])
class CfnTriggerProps(_CfnTriggerProps):
    """Properties for defining a ``AWS::Glue::Trigger``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html
    Stability:
        stable
    """
    actions: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnTrigger.ActionProperty"]]]
    """``AWS::Glue::Trigger.Actions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-actions
    Stability:
        stable
    """

    type: str
    """``AWS::Glue::Trigger.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-glue-trigger.html#cfn-glue-trigger-type
    Stability:
        stable
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
class IDatabase(aws_cdk.core.IResource, jsii.compat.Protocol):
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


class _IDatabaseProxy(jsii.proxy_for(aws_cdk.core.IResource)):
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
class Database(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.Database"):
    """A Glue database.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, database_name: str, location_uri: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            database_name: The name of the database.
            location_uri: The location of the database (for example, an HDFS path). Default: a bucket is created and the database is stored under s3:///

        Stability:
            experimental
        """
        props: DatabaseProps = {"databaseName": database_name}

        if location_uri is not None:
            props["locationUri"] = location_uri

        jsii.create(Database, self, [scope, id, props])

    @jsii.member(jsii_name="fromDatabaseArn")
    @classmethod
    def from_database_arn(cls, scope: aws_cdk.core.Construct, id: str, database_arn: str) -> "IDatabase":
        """
        Arguments:
            scope: -
            id: -
            database_arn: -

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
class ITable(aws_cdk.core.IResource, jsii.compat.Protocol):
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


class _ITableProxy(jsii.proxy_for(aws_cdk.core.IResource)):
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
            class_name: -

        Stability:
            experimental
        """
        jsii.create(InputFormat, self, [class_name])

    @classproperty
    @jsii.member(jsii_name="TEXT_INPUT_FORMAT")
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
        return jsii.sget(cls, "TEXT_INPUT_FORMAT")

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
            class_name: -

        Stability:
            experimental
        """
        jsii.create(OutputFormat, self, [class_name])

    @classproperty
    @jsii.member(jsii_name="HIVE_IGNORE_KEY_TEXT_OUTPUT_FORMAT")
    def HIVE_IGNORE_KEY_TEXT_OUTPUT_FORMAT(cls) -> "OutputFormat":
        """Writes text data with a null key (value only).

        See:
            https://hive.apache.org/javadocs/r2.2.0/api/org/apache/hadoop/hive/ql/io/HiveIgnoreKeyTextOutputFormat.html
        Stability:
            experimental
        """
        return jsii.sget(cls, "HIVE_IGNORE_KEY_TEXT_OUTPUT_FORMAT")

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
            item_type: type contained by the array.
            input_string: Glue InputString for this type.
            is_primitive: Indicates whether this type is a primitive data type.

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
            key_type: type of key, must be a primitive.
            value_type: type fo the value indexed by the key.
            input_string: Glue InputString for this type.
            is_primitive: Indicates whether this type is a primitive data type.

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
    @jsii.member(jsii_name="BIG_INT")
    def BIG_INT(cls) -> "Type":
        """A 64-bit signed INTEGER in two’s complement format, with a minimum value of -2^63 and a maximum value of 2^63-1.

        Stability:
            experimental
        """
        return jsii.sget(cls, "BIG_INT")

    @classproperty
    @jsii.member(jsii_name="BINARY")
    def BINARY(cls) -> "Type":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "BINARY")

    @classproperty
    @jsii.member(jsii_name="BOOLEAN")
    def BOOLEAN(cls) -> "Type":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "BOOLEAN")

    @classproperty
    @jsii.member(jsii_name="DATE")
    def DATE(cls) -> "Type":
        """Date type.

        Stability:
            experimental
        """
        return jsii.sget(cls, "DATE")

    @classproperty
    @jsii.member(jsii_name="DOUBLE")
    def DOUBLE(cls) -> "Type":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "DOUBLE")

    @classproperty
    @jsii.member(jsii_name="FLOAT")
    def FLOAT(cls) -> "Type":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "FLOAT")

    @classproperty
    @jsii.member(jsii_name="INTEGER")
    def INTEGER(cls) -> "Type":
        """A 32-bit signed INTEGER in two’s complement format, with a minimum value of -2^31 and a maximum value of 2^31-1.

        Stability:
            experimental
        """
        return jsii.sget(cls, "INTEGER")

    @classproperty
    @jsii.member(jsii_name="SMALL_INT")
    def SMALL_INT(cls) -> "Type":
        """A 16-bit signed INTEGER in two’s complement format, with a minimum value of -2^15 and a maximum value of 2^15-1.

        Stability:
            experimental
        """
        return jsii.sget(cls, "SMALL_INT")

    @classproperty
    @jsii.member(jsii_name="STRING")
    def STRING(cls) -> "Type":
        """Arbitrary-length string type.

        Stability:
            experimental
        """
        return jsii.sget(cls, "STRING")

    @classproperty
    @jsii.member(jsii_name="TIMESTAMP")
    def TIMESTAMP(cls) -> "Type":
        """Timestamp type (date and time).

        Stability:
            experimental
        """
        return jsii.sget(cls, "TIMESTAMP")

    @classproperty
    @jsii.member(jsii_name="TINY_INT")
    def TINY_INT(cls) -> "Type":
        """A 8-bit signed INTEGER in two’s complement format, with a minimum value of -2^7 and a maximum value of 2^7-1.

        Stability:
            experimental
        """
        return jsii.sget(cls, "TINY_INT")


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
            class_name: -

        Stability:
            experimental
        """
        jsii.create(SerializationLibrary, self, [class_name])

    @classproperty
    @jsii.member(jsii_name="HIVE_JSON")
    def HIVE_JSON(cls) -> "SerializationLibrary":
        """
        See:
            https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-JSON
        Stability:
            experimental
        """
        return jsii.sget(cls, "HIVE_JSON")

    @classproperty
    @jsii.member(jsii_name="OPENX_JSON")
    def OPENX_JSON(cls) -> "SerializationLibrary":
        """
        See:
            https://github.com/rcongiu/Hive-JSON-Serde
        Stability:
            experimental
        """
        return jsii.sget(cls, "OPENX_JSON")

    @property
    @jsii.member(jsii_name="className")
    def class_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "className")


@jsii.implements(ITable)
class Table(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-glue.Table"):
    """A Glue table.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, columns: typing.List["Column"], database: "IDatabase", data_format: "DataFormat", table_name: str, bucket: typing.Optional[aws_cdk.aws_s3.IBucket]=None, compressed: typing.Optional[bool]=None, description: typing.Optional[str]=None, encryption: typing.Optional["TableEncryption"]=None, encryption_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, partition_keys: typing.Optional[typing.List["Column"]]=None, s3_prefix: typing.Optional[str]=None, stored_as_sub_directories: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            columns: Columns of the table.
            database: Database in which to store the table.
            data_format: Storage type of the table's data.
            table_name: Name of the table.
            bucket: S3 bucket in which to store data. Default: one is created for you
            compressed: Indicates whether the table's data is compressed or not. Default: false
            description: Description of the table. Default: generated
            encryption: The kind of encryption to secure the data with. You can only provide this option if you are not explicitly passing in a bucket. If you choose ``SSE-KMS``, you *can* provide an un-managed KMS key with ``encryptionKey``. If you choose ``CSE-KMS``, you *must* provide an un-managed KMS key with ``encryptionKey``. Default: Unencrypted
            encryption_key: External KMS key to use for bucket encryption. The ``encryption`` property must be ``SSE-KMS`` or ``CSE-KMS``. Default: key is managed by KMS.
            partition_keys: Partition columns of the table. Default: table is not partitioned
            s3_prefix: S3 prefix under which table objects are stored. Default: data/
            stored_as_sub_directories: Indicates whether the table data is stored in subdirectories. Default: false

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
    def from_table_arn(cls, scope: aws_cdk.core.Construct, id: str, table_arn: str) -> "ITable":
        """
        Arguments:
            scope: -
            id: -
            table_arn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromTableArn", [scope, id, table_arn])

    @jsii.member(jsii_name="fromTableAttributes")
    @classmethod
    def from_table_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, table_arn: str, table_name: str) -> "ITable":
        """Creates a Table construct that represents an external table.

        Arguments:
            scope: The scope creating construct (usually ``this``).
            id: The construct's id.
            attrs: Import attributes.
            table_arn: 
            table_name: 

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
    UNENCRYPTED = "UNENCRYPTED"
    """
    Stability:
        experimental
    """
    S3_MANAGED = "S3_MANAGED"
    """Server side encryption (SSE) with an Amazon S3-managed key.

    See:
        https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingServerSideEncryption.html
    Stability:
        experimental
    """
    KMS = "KMS"
    """Server-side encryption (SSE) with an AWS KMS key managed by the account owner.

    See:
        https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingKMSEncryption.html
    Stability:
        experimental
    """
    KMS_MANAGED = "KMS_MANAGED"
    """Server-side encryption (SSE) with an AWS KMS key managed by the KMS service.

    Stability:
        experimental
    """
    CLIENT_SIDE_KMS = "CLIENT_SIDE_KMS"
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
