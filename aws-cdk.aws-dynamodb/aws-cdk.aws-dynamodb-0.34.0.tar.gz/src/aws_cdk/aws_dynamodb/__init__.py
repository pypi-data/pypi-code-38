import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_applicationautoscaling
import aws_cdk.aws_iam
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-dynamodb", "0.34.0", __name__, "aws-dynamodb@0.34.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.Attribute", jsii_struct_bases=[])
class Attribute(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    name: str
    """The name of an attribute.

    Stability:
        experimental
    """

    type: "AttributeType"
    """The data type of an attribute.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-dynamodb.AttributeType")
class AttributeType(enum.Enum):
    """
    Stability:
        experimental
    """
    Binary = "Binary"
    """
    Stability:
        experimental
    """
    Number = "Number"
    """
    Stability:
        experimental
    """
    String = "String"
    """
    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-dynamodb.BillingMode")
class BillingMode(enum.Enum):
    """DyanmoDB's Read/Write capacity modes.

    Stability:
        experimental
    """
    PayPerRequest = "PayPerRequest"
    """Pay only for what you use.

    You don't configure Read/Write capacity units.

    Stability:
        experimental
    """
    Provisioned = "Provisioned"
    """Explicitly specified Read/Write capacity units.

    Stability:
        experimental
    """

class CfnTable(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dynamodb.CfnTable"):
    """A CloudFormation ``AWS::DynamoDB::Table``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DynamoDB::Table
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, key_schema: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["KeySchemaProperty", aws_cdk.cdk.Token]]], attribute_definitions: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "AttributeDefinitionProperty"]]]]]=None, billing_mode: typing.Optional[str]=None, global_secondary_indexes: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "GlobalSecondaryIndexProperty"]]]]]=None, local_secondary_indexes: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "LocalSecondaryIndexProperty"]]]]]=None, point_in_time_recovery_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["PointInTimeRecoverySpecificationProperty"]]]=None, provisioned_throughput: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ProvisionedThroughputProperty"]]]=None, sse_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["SSESpecificationProperty"]]]=None, stream_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["StreamSpecificationProperty"]]]=None, table_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, time_to_live_specification: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["TimeToLiveSpecificationProperty"]]]=None) -> None:
        """Create a new ``AWS::DynamoDB::Table``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            keySchema: ``AWS::DynamoDB::Table.KeySchema``.
            attributeDefinitions: ``AWS::DynamoDB::Table.AttributeDefinitions``.
            billingMode: ``AWS::DynamoDB::Table.BillingMode``.
            globalSecondaryIndexes: ``AWS::DynamoDB::Table.GlobalSecondaryIndexes``.
            localSecondaryIndexes: ``AWS::DynamoDB::Table.LocalSecondaryIndexes``.
            pointInTimeRecoverySpecification: ``AWS::DynamoDB::Table.PointInTimeRecoverySpecification``.
            provisionedThroughput: ``AWS::DynamoDB::Table.ProvisionedThroughput``.
            sseSpecification: ``AWS::DynamoDB::Table.SSESpecification``.
            streamSpecification: ``AWS::DynamoDB::Table.StreamSpecification``.
            tableName: ``AWS::DynamoDB::Table.TableName``.
            tags: ``AWS::DynamoDB::Table.Tags``.
            timeToLiveSpecification: ``AWS::DynamoDB::Table.TimeToLiveSpecification``.

        Stability:
            experimental
        """
        props: CfnTableProps = {"keySchema": key_schema}

        if attribute_definitions is not None:
            props["attributeDefinitions"] = attribute_definitions

        if billing_mode is not None:
            props["billingMode"] = billing_mode

        if global_secondary_indexes is not None:
            props["globalSecondaryIndexes"] = global_secondary_indexes

        if local_secondary_indexes is not None:
            props["localSecondaryIndexes"] = local_secondary_indexes

        if point_in_time_recovery_specification is not None:
            props["pointInTimeRecoverySpecification"] = point_in_time_recovery_specification

        if provisioned_throughput is not None:
            props["provisionedThroughput"] = provisioned_throughput

        if sse_specification is not None:
            props["sseSpecification"] = sse_specification

        if stream_specification is not None:
            props["streamSpecification"] = stream_specification

        if table_name is not None:
            props["tableName"] = table_name

        if tags is not None:
            props["tags"] = tags

        if time_to_live_specification is not None:
            props["timeToLiveSpecification"] = time_to_live_specification

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
    @jsii.member(jsii_name="tableArn")
    def table_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "tableArn")

    @property
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "tableName")

    @property
    @jsii.member(jsii_name="tableStreamArn")
    def table_stream_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            StreamArn
        """
        return jsii.get(self, "tableStreamArn")

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

    @jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.CfnTable.AttributeDefinitionProperty", jsii_struct_bases=[])
    class AttributeDefinitionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-attributedef.html
        Stability:
            experimental
        """
        attributeName: str
        """``CfnTable.AttributeDefinitionProperty.AttributeName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-attributedef.html#cfn-dynamodb-attributedef-attributename
        Stability:
            experimental
        """

        attributeType: str
        """``CfnTable.AttributeDefinitionProperty.AttributeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-attributedef.html#cfn-dynamodb-attributedef-attributename-attributetype
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _GlobalSecondaryIndexProperty(jsii.compat.TypedDict, total=False):
        provisionedThroughput: typing.Union[aws_cdk.cdk.Token, "CfnTable.ProvisionedThroughputProperty"]
        """``CfnTable.GlobalSecondaryIndexProperty.ProvisionedThroughput``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-gsi.html#cfn-dynamodb-gsi-provisionedthroughput
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.CfnTable.GlobalSecondaryIndexProperty", jsii_struct_bases=[_GlobalSecondaryIndexProperty])
    class GlobalSecondaryIndexProperty(_GlobalSecondaryIndexProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-gsi.html
        Stability:
            experimental
        """
        indexName: str
        """``CfnTable.GlobalSecondaryIndexProperty.IndexName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-gsi.html#cfn-dynamodb-gsi-indexname
        Stability:
            experimental
        """

        keySchema: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnTable.KeySchemaProperty", aws_cdk.cdk.Token]]]
        """``CfnTable.GlobalSecondaryIndexProperty.KeySchema``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-gsi.html#cfn-dynamodb-gsi-keyschema
        Stability:
            experimental
        """

        projection: typing.Union[aws_cdk.cdk.Token, "CfnTable.ProjectionProperty"]
        """``CfnTable.GlobalSecondaryIndexProperty.Projection``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-gsi.html#cfn-dynamodb-gsi-projection
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.CfnTable.KeySchemaProperty", jsii_struct_bases=[])
    class KeySchemaProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-keyschema.html
        Stability:
            experimental
        """
        attributeName: str
        """``CfnTable.KeySchemaProperty.AttributeName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-keyschema.html#aws-properties-dynamodb-keyschema-attributename
        Stability:
            experimental
        """

        keyType: str
        """``CfnTable.KeySchemaProperty.KeyType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-keyschema.html#aws-properties-dynamodb-keyschema-keytype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.CfnTable.LocalSecondaryIndexProperty", jsii_struct_bases=[])
    class LocalSecondaryIndexProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-lsi.html
        Stability:
            experimental
        """
        indexName: str
        """``CfnTable.LocalSecondaryIndexProperty.IndexName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-lsi.html#cfn-dynamodb-lsi-indexname
        Stability:
            experimental
        """

        keySchema: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnTable.KeySchemaProperty", aws_cdk.cdk.Token]]]
        """``CfnTable.LocalSecondaryIndexProperty.KeySchema``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-lsi.html#cfn-dynamodb-lsi-keyschema
        Stability:
            experimental
        """

        projection: typing.Union[aws_cdk.cdk.Token, "CfnTable.ProjectionProperty"]
        """``CfnTable.LocalSecondaryIndexProperty.Projection``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-lsi.html#cfn-dynamodb-lsi-projection
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.CfnTable.PointInTimeRecoverySpecificationProperty", jsii_struct_bases=[])
    class PointInTimeRecoverySpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-table-pointintimerecoveryspecification.html
        Stability:
            experimental
        """
        pointInTimeRecoveryEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTable.PointInTimeRecoverySpecificationProperty.PointInTimeRecoveryEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-table-pointintimerecoveryspecification.html#cfn-dynamodb-table-pointintimerecoveryspecification-pointintimerecoveryenabled
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.CfnTable.ProjectionProperty", jsii_struct_bases=[])
    class ProjectionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-projectionobject.html
        Stability:
            experimental
        """
        nonKeyAttributes: typing.List[str]
        """``CfnTable.ProjectionProperty.NonKeyAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-projectionobject.html#cfn-dynamodb-projectionobj-nonkeyatt
        Stability:
            experimental
        """

        projectionType: str
        """``CfnTable.ProjectionProperty.ProjectionType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-projectionobject.html#cfn-dynamodb-projectionobj-projtype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.CfnTable.ProvisionedThroughputProperty", jsii_struct_bases=[])
    class ProvisionedThroughputProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-provisionedthroughput.html
        Stability:
            experimental
        """
        readCapacityUnits: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTable.ProvisionedThroughputProperty.ReadCapacityUnits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-provisionedthroughput.html#cfn-dynamodb-provisionedthroughput-readcapacityunits
        Stability:
            experimental
        """

        writeCapacityUnits: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTable.ProvisionedThroughputProperty.WriteCapacityUnits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-provisionedthroughput.html#cfn-dynamodb-provisionedthroughput-writecapacityunits
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.CfnTable.SSESpecificationProperty", jsii_struct_bases=[])
    class SSESpecificationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-table-ssespecification.html
        Stability:
            experimental
        """
        sseEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTable.SSESpecificationProperty.SSEEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-table-ssespecification.html#cfn-dynamodb-table-ssespecification-sseenabled
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.CfnTable.StreamSpecificationProperty", jsii_struct_bases=[])
    class StreamSpecificationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-streamspecification.html
        Stability:
            experimental
        """
        streamViewType: str
        """``CfnTable.StreamSpecificationProperty.StreamViewType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-streamspecification.html#cfn-dynamodb-streamspecification-streamviewtype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.CfnTable.TimeToLiveSpecificationProperty", jsii_struct_bases=[])
    class TimeToLiveSpecificationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-timetolivespecification.html
        Stability:
            experimental
        """
        attributeName: str
        """``CfnTable.TimeToLiveSpecificationProperty.AttributeName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-timetolivespecification.html#cfn-dynamodb-timetolivespecification-attributename
        Stability:
            experimental
        """

        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTable.TimeToLiveSpecificationProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dynamodb-timetolivespecification.html#cfn-dynamodb-timetolivespecification-enabled
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnTableProps(jsii.compat.TypedDict, total=False):
    attributeDefinitions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTable.AttributeDefinitionProperty"]]]
    """``AWS::DynamoDB::Table.AttributeDefinitions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-attributedef
    Stability:
        experimental
    """
    billingMode: str
    """``AWS::DynamoDB::Table.BillingMode``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-billingmode
    Stability:
        experimental
    """
    globalSecondaryIndexes: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTable.GlobalSecondaryIndexProperty"]]]
    """``AWS::DynamoDB::Table.GlobalSecondaryIndexes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-gsi
    Stability:
        experimental
    """
    localSecondaryIndexes: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTable.LocalSecondaryIndexProperty"]]]
    """``AWS::DynamoDB::Table.LocalSecondaryIndexes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-lsi
    Stability:
        experimental
    """
    pointInTimeRecoverySpecification: typing.Union[aws_cdk.cdk.Token, "CfnTable.PointInTimeRecoverySpecificationProperty"]
    """``AWS::DynamoDB::Table.PointInTimeRecoverySpecification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-pointintimerecoveryspecification
    Stability:
        experimental
    """
    provisionedThroughput: typing.Union[aws_cdk.cdk.Token, "CfnTable.ProvisionedThroughputProperty"]
    """``AWS::DynamoDB::Table.ProvisionedThroughput``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-provisionedthroughput
    Stability:
        experimental
    """
    sseSpecification: typing.Union[aws_cdk.cdk.Token, "CfnTable.SSESpecificationProperty"]
    """``AWS::DynamoDB::Table.SSESpecification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-ssespecification
    Stability:
        experimental
    """
    streamSpecification: typing.Union[aws_cdk.cdk.Token, "CfnTable.StreamSpecificationProperty"]
    """``AWS::DynamoDB::Table.StreamSpecification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-streamspecification
    Stability:
        experimental
    """
    tableName: str
    """``AWS::DynamoDB::Table.TableName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-tablename
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::DynamoDB::Table.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-tags
    Stability:
        experimental
    """
    timeToLiveSpecification: typing.Union[aws_cdk.cdk.Token, "CfnTable.TimeToLiveSpecificationProperty"]
    """``AWS::DynamoDB::Table.TimeToLiveSpecification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-timetolivespecification
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.CfnTableProps", jsii_struct_bases=[_CfnTableProps])
class CfnTableProps(_CfnTableProps):
    """Properties for defining a ``AWS::DynamoDB::Table``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html
    Stability:
        experimental
    """
    keySchema: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnTable.KeySchemaProperty", aws_cdk.cdk.Token]]]
    """``AWS::DynamoDB::Table.KeySchema``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-keyschema
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.EnableScalingProps", jsii_struct_bases=[])
class EnableScalingProps(jsii.compat.TypedDict):
    """Properties for enabling DynamoDB capacity scaling.

    Stability:
        experimental
    """
    maxCapacity: jsii.Number
    """Maximum capacity to scale to.

    Stability:
        experimental
    """

    minCapacity: jsii.Number
    """Minimum capacity to scale to.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-dynamodb.IScalableTableAttribute")
class IScalableTableAttribute(jsii.compat.Protocol):
    """Interface for scalable attributes.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IScalableTableAttributeProxy

    @jsii.member(jsii_name="scaleOnSchedule")
    def scale_on_schedule(self, id: str, *, schedule: str, end_time: typing.Optional[datetime.datetime]=None, max_capacity: typing.Optional[jsii.Number]=None, min_capacity: typing.Optional[jsii.Number]=None, start_time: typing.Optional[datetime.datetime]=None) -> None:
        """Add scheduled scaling for this scaling attribute.

        Arguments:
            id: -
            actions: -
            schedule: When to perform this action. Support formats: - at(yyyy-mm-ddThh:mm:ss) - rate(value unit) - cron(fields) "At" expressions are useful for one-time schedules. Specify the time in UTC. For "rate" expressions, value is a positive integer, and unit is minute, minutes, hour, hours, day, or days. For more information about cron expressions, see https://en.wikipedia.org/wiki/Cron.
            endTime: When this scheduled action expires. Default: The rule never expires.
            maxCapacity: The new maximum capacity. During the scheduled time, the current capacity is above the maximum capacity, Application Auto Scaling scales in to the maximum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new maximum capacity
            minCapacity: The new minimum capacity. During the scheduled time, if the current capacity is below the minimum capacity, Application Auto Scaling scales out to the minimum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new minimum capacity
            startTime: When this scheduled action becomes active. Default: The rule is activate immediately

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="scaleOnUtilization")
    def scale_on_utilization(self, *, target_utilization_percent: jsii.Number, disable_scale_in: typing.Optional[bool]=None, policy_name: typing.Optional[str]=None, scale_in_cooldown_sec: typing.Optional[jsii.Number]=None, scale_out_cooldown_sec: typing.Optional[jsii.Number]=None) -> None:
        """Scale out or in to keep utilization at a given level.

        Arguments:
            props: -
            targetUtilizationPercent: Target utilization percentage for the attribute.
            disableScaleIn: Indicates whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. Default: false
            policyName: A name for the scaling policy. Default: - Automatically generated name.
            scaleInCooldownSec: Period after a scale in activity completes before another scale in activity can start. Default: - No scale in cooldown.
            scaleOutCooldownSec: Period after a scale out activity completes before another scale out activity can start. Default: - No scale out cooldown.

        Stability:
            experimental
        """
        ...


class _IScalableTableAttributeProxy():
    """Interface for scalable attributes.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-dynamodb.IScalableTableAttribute"
    @jsii.member(jsii_name="scaleOnSchedule")
    def scale_on_schedule(self, id: str, *, schedule: str, end_time: typing.Optional[datetime.datetime]=None, max_capacity: typing.Optional[jsii.Number]=None, min_capacity: typing.Optional[jsii.Number]=None, start_time: typing.Optional[datetime.datetime]=None) -> None:
        """Add scheduled scaling for this scaling attribute.

        Arguments:
            id: -
            actions: -
            schedule: When to perform this action. Support formats: - at(yyyy-mm-ddThh:mm:ss) - rate(value unit) - cron(fields) "At" expressions are useful for one-time schedules. Specify the time in UTC. For "rate" expressions, value is a positive integer, and unit is minute, minutes, hour, hours, day, or days. For more information about cron expressions, see https://en.wikipedia.org/wiki/Cron.
            endTime: When this scheduled action expires. Default: The rule never expires.
            maxCapacity: The new maximum capacity. During the scheduled time, the current capacity is above the maximum capacity, Application Auto Scaling scales in to the maximum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new maximum capacity
            minCapacity: The new minimum capacity. During the scheduled time, if the current capacity is below the minimum capacity, Application Auto Scaling scales out to the minimum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new minimum capacity
            startTime: When this scheduled action becomes active. Default: The rule is activate immediately

        Stability:
            experimental
        """
        actions: aws_cdk.aws_applicationautoscaling.ScalingSchedule = {"schedule": schedule}

        if end_time is not None:
            actions["endTime"] = end_time

        if max_capacity is not None:
            actions["maxCapacity"] = max_capacity

        if min_capacity is not None:
            actions["minCapacity"] = min_capacity

        if start_time is not None:
            actions["startTime"] = start_time

        return jsii.invoke(self, "scaleOnSchedule", [id, actions])

    @jsii.member(jsii_name="scaleOnUtilization")
    def scale_on_utilization(self, *, target_utilization_percent: jsii.Number, disable_scale_in: typing.Optional[bool]=None, policy_name: typing.Optional[str]=None, scale_in_cooldown_sec: typing.Optional[jsii.Number]=None, scale_out_cooldown_sec: typing.Optional[jsii.Number]=None) -> None:
        """Scale out or in to keep utilization at a given level.

        Arguments:
            props: -
            targetUtilizationPercent: Target utilization percentage for the attribute.
            disableScaleIn: Indicates whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. Default: false
            policyName: A name for the scaling policy. Default: - Automatically generated name.
            scaleInCooldownSec: Period after a scale in activity completes before another scale in activity can start. Default: - No scale in cooldown.
            scaleOutCooldownSec: Period after a scale out activity completes before another scale out activity can start. Default: - No scale out cooldown.

        Stability:
            experimental
        """
        props: UtilizationScalingProps = {"targetUtilizationPercent": target_utilization_percent}

        if disable_scale_in is not None:
            props["disableScaleIn"] = disable_scale_in

        if policy_name is not None:
            props["policyName"] = policy_name

        if scale_in_cooldown_sec is not None:
            props["scaleInCooldownSec"] = scale_in_cooldown_sec

        if scale_out_cooldown_sec is not None:
            props["scaleOutCooldownSec"] = scale_out_cooldown_sec

        return jsii.invoke(self, "scaleOnUtilization", [props])


@jsii.enum(jsii_type="@aws-cdk/aws-dynamodb.ProjectionType")
class ProjectionType(enum.Enum):
    """
    Stability:
        experimental
    """
    KeysOnly = "KeysOnly"
    """
    Stability:
        experimental
    """
    Include = "Include"
    """
    Stability:
        experimental
    """
    All = "All"
    """
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _SecondaryIndexProps(jsii.compat.TypedDict, total=False):
    nonKeyAttributes: typing.List[str]
    """The non-key attributes that are projected into the secondary index.

    Default:
        undefined

    Stability:
        experimental
    """
    projectionType: "ProjectionType"
    """The set of attributes that are projected into the secondary index.

    Default:
        ALL

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.SecondaryIndexProps", jsii_struct_bases=[_SecondaryIndexProps])
class SecondaryIndexProps(_SecondaryIndexProps):
    """
    Stability:
        experimental
    """
    indexName: str
    """The name of the secondary index.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[SecondaryIndexProps])
class _GlobalSecondaryIndexProps(SecondaryIndexProps, jsii.compat.TypedDict, total=False):
    readCapacity: jsii.Number
    """The read capacity for the global secondary index.

    Can only be provided if table billingMode is Provisioned or undefined.

    Default:
        5

    Stability:
        experimental
    """
    sortKey: "Attribute"
    """The attribute of a sort key for the global secondary index.

    Default:
        undefined

    Stability:
        experimental
    """
    writeCapacity: jsii.Number
    """The write capacity for the global secondary index.

    Can only be provided if table billingMode is Provisioned or undefined.

    Default:
        5

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.GlobalSecondaryIndexProps", jsii_struct_bases=[_GlobalSecondaryIndexProps])
class GlobalSecondaryIndexProps(_GlobalSecondaryIndexProps):
    """
    Stability:
        experimental
    """
    partitionKey: "Attribute"
    """The attribute of a partition key for the global secondary index.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.LocalSecondaryIndexProps", jsii_struct_bases=[SecondaryIndexProps])
class LocalSecondaryIndexProps(SecondaryIndexProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    sortKey: "Attribute"
    """The attribute of a sort key for the local secondary index.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-dynamodb.StreamViewType")
class StreamViewType(enum.Enum):
    """When an item in the table is modified, StreamViewType determines what information is written to the stream for this table.

    Valid values for StreamViewType are:

    Stability:
        experimental
    enum:
        true
    link:
        https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_StreamSpecification.html
    """
    NewImage = "NewImage"
    """The entire item, as it appears after it was modified, is written to the stream.

    Stability:
        experimental
    """
    OldImage = "OldImage"
    """The entire item, as it appeared before it was modified, is written to the stream.

    Stability:
        experimental
    """
    NewAndOldImages = "NewAndOldImages"
    """Both the new and the old item images of the item are written to the stream.

    Stability:
        experimental
    """
    KeysOnly = "KeysOnly"
    """Only the key attributes of the modified item are written to the stream.

    Stability:
        experimental
    """

class Table(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dynamodb.Table"):
    """Provides a DynamoDB table.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, table_name: typing.Optional[str]=None, partition_key: "Attribute", billing_mode: typing.Optional["BillingMode"]=None, pitr_enabled: typing.Optional[bool]=None, read_capacity: typing.Optional[jsii.Number]=None, sort_key: typing.Optional["Attribute"]=None, sse_enabled: typing.Optional[bool]=None, stream_specification: typing.Optional["StreamViewType"]=None, ttl_attribute_name: typing.Optional[str]=None, write_capacity: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            tableName: Enforces a particular physical table name. Default: 
            partitionKey: Partition key attribute definition.
            billingMode: Specify how you are charged for read and write throughput and how you manage capacity. Default: Provisioned
            pitrEnabled: Whether point-in-time recovery is enabled. Default: undefined, point-in-time recovery is disabled
            readCapacity: The read capacity for the table. Careful if you add Global Secondary Indexes, as those will share the table's provisioned throughput. Can only be provided if billingMode is Provisioned. Default: 5
            sortKey: Table sort key attribute definition. Default: no sort key
            sseEnabled: Whether server-side encryption with an AWS managed customer master key is enabled. Default: undefined, server-side encryption is enabled with an AWS owned customer master key
            streamSpecification: When an item in the table is modified, StreamViewType determines what information is written to the stream for this table. Valid values for StreamViewType are: Default: undefined, streams are disabled
            ttlAttributeName: The name of TTL attribute. Default: undefined, TTL is disabled
            writeCapacity: The write capacity for the table. Careful if you add Global Secondary Indexes, as those will share the table's provisioned throughput. Can only be provided if billingMode is Provisioned. Default: 5

        Stability:
            experimental
        """
        props: TableProps = {"partitionKey": partition_key}

        if table_name is not None:
            props["tableName"] = table_name

        if billing_mode is not None:
            props["billingMode"] = billing_mode

        if pitr_enabled is not None:
            props["pitrEnabled"] = pitr_enabled

        if read_capacity is not None:
            props["readCapacity"] = read_capacity

        if sort_key is not None:
            props["sortKey"] = sort_key

        if sse_enabled is not None:
            props["sseEnabled"] = sse_enabled

        if stream_specification is not None:
            props["streamSpecification"] = stream_specification

        if ttl_attribute_name is not None:
            props["ttlAttributeName"] = ttl_attribute_name

        if write_capacity is not None:
            props["writeCapacity"] = write_capacity

        jsii.create(Table, self, [scope, id, props])

    @jsii.member(jsii_name="grantListStreams")
    @classmethod
    def grant_list_streams(cls, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Permits an IAM Principal to list all DynamoDB Streams.

        Arguments:
            grantee: The principal (no-op if undefined).

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "grantListStreams", [grantee])

    @jsii.member(jsii_name="addGlobalSecondaryIndex")
    def add_global_secondary_index(self, *, partition_key: "Attribute", read_capacity: typing.Optional[jsii.Number]=None, sort_key: typing.Optional["Attribute"]=None, write_capacity: typing.Optional[jsii.Number]=None, index_name: str, non_key_attributes: typing.Optional[typing.List[str]]=None, projection_type: typing.Optional["ProjectionType"]=None) -> None:
        """Add a global secondary index of table.

        Arguments:
            props: the property of global secondary index.
            partitionKey: The attribute of a partition key for the global secondary index.
            readCapacity: The read capacity for the global secondary index. Can only be provided if table billingMode is Provisioned or undefined. Default: 5
            sortKey: The attribute of a sort key for the global secondary index. Default: undefined
            writeCapacity: The write capacity for the global secondary index. Can only be provided if table billingMode is Provisioned or undefined. Default: 5
            indexName: The name of the secondary index.
            nonKeyAttributes: The non-key attributes that are projected into the secondary index. Default: undefined
            projectionType: The set of attributes that are projected into the secondary index. Default: ALL

        Stability:
            experimental
        """
        props: GlobalSecondaryIndexProps = {"partitionKey": partition_key, "indexName": index_name}

        if read_capacity is not None:
            props["readCapacity"] = read_capacity

        if sort_key is not None:
            props["sortKey"] = sort_key

        if write_capacity is not None:
            props["writeCapacity"] = write_capacity

        if non_key_attributes is not None:
            props["nonKeyAttributes"] = non_key_attributes

        if projection_type is not None:
            props["projectionType"] = projection_type

        return jsii.invoke(self, "addGlobalSecondaryIndex", [props])

    @jsii.member(jsii_name="addLocalSecondaryIndex")
    def add_local_secondary_index(self, *, sort_key: "Attribute", index_name: str, non_key_attributes: typing.Optional[typing.List[str]]=None, projection_type: typing.Optional["ProjectionType"]=None) -> None:
        """Add a local secondary index of table.

        Arguments:
            props: the property of local secondary index.
            sortKey: The attribute of a sort key for the local secondary index.
            indexName: The name of the secondary index.
            nonKeyAttributes: The non-key attributes that are projected into the secondary index. Default: undefined
            projectionType: The set of attributes that are projected into the secondary index. Default: ALL

        Stability:
            experimental
        """
        props: LocalSecondaryIndexProps = {"sortKey": sort_key, "indexName": index_name}

        if non_key_attributes is not None:
            props["nonKeyAttributes"] = non_key_attributes

        if projection_type is not None:
            props["projectionType"] = projection_type

        return jsii.invoke(self, "addLocalSecondaryIndex", [props])

    @jsii.member(jsii_name="autoScaleGlobalSecondaryIndexReadCapacity")
    def auto_scale_global_secondary_index_read_capacity(self, index_name: str, *, max_capacity: jsii.Number, min_capacity: jsii.Number) -> "IScalableTableAttribute":
        """Enable read capacity scaling for the given GSI.

        Arguments:
            indexName: -
            props: -
            maxCapacity: Maximum capacity to scale to.
            minCapacity: Minimum capacity to scale to.

        Returns:
            An object to configure additional AutoScaling settings for this attribute

        Stability:
            experimental
        """
        props: EnableScalingProps = {"maxCapacity": max_capacity, "minCapacity": min_capacity}

        return jsii.invoke(self, "autoScaleGlobalSecondaryIndexReadCapacity", [index_name, props])

    @jsii.member(jsii_name="autoScaleGlobalSecondaryIndexWriteCapacity")
    def auto_scale_global_secondary_index_write_capacity(self, index_name: str, *, max_capacity: jsii.Number, min_capacity: jsii.Number) -> "IScalableTableAttribute":
        """Enable write capacity scaling for the given GSI.

        Arguments:
            indexName: -
            props: -
            maxCapacity: Maximum capacity to scale to.
            minCapacity: Minimum capacity to scale to.

        Returns:
            An object to configure additional AutoScaling settings for this attribute

        Stability:
            experimental
        """
        props: EnableScalingProps = {"maxCapacity": max_capacity, "minCapacity": min_capacity}

        return jsii.invoke(self, "autoScaleGlobalSecondaryIndexWriteCapacity", [index_name, props])

    @jsii.member(jsii_name="autoScaleReadCapacity")
    def auto_scale_read_capacity(self, *, max_capacity: jsii.Number, min_capacity: jsii.Number) -> "IScalableTableAttribute":
        """Enable read capacity scaling for this table.

        Arguments:
            props: -
            maxCapacity: Maximum capacity to scale to.
            minCapacity: Minimum capacity to scale to.

        Returns:
            An object to configure additional AutoScaling settings

        Stability:
            experimental
        """
        props: EnableScalingProps = {"maxCapacity": max_capacity, "minCapacity": min_capacity}

        return jsii.invoke(self, "autoScaleReadCapacity", [props])

    @jsii.member(jsii_name="autoScaleWriteCapacity")
    def auto_scale_write_capacity(self, *, max_capacity: jsii.Number, min_capacity: jsii.Number) -> "IScalableTableAttribute":
        """Enable write capacity scaling for this table.

        Arguments:
            props: -
            maxCapacity: Maximum capacity to scale to.
            minCapacity: Minimum capacity to scale to.

        Returns:
            An object to configure additional AutoScaling settings for this attribute

        Stability:
            experimental
        """
        props: EnableScalingProps = {"maxCapacity": max_capacity, "minCapacity": min_capacity}

        return jsii.invoke(self, "autoScaleWriteCapacity", [props])

    @jsii.member(jsii_name="grant")
    def grant(self, grantee: aws_cdk.aws_iam.IGrantable, *actions: str) -> aws_cdk.aws_iam.Grant:
        """Adds an IAM policy statement associated with this table to an IAM principal's policy.

        Arguments:
            grantee: The principal (no-op if undefined).
            actions: The set of actions to allow (i.e. "dynamodb:PutItem", "dynamodb:GetItem", ...).

        Stability:
            experimental
        """
        return jsii.invoke(self, "grant", [grantee, *actions])

    @jsii.member(jsii_name="grantFullAccess")
    def grant_full_access(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Permits all DynamoDB operations ("dynamodb:*") to an IAM principal.

        Arguments:
            grantee: The principal to grant access to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantFullAccess", [grantee])

    @jsii.member(jsii_name="grantReadData")
    def grant_read_data(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Permits an IAM principal all data read operations from this table: BatchGetItem, GetRecords, GetShardIterator, Query, GetItem, Scan.

        Arguments:
            grantee: The principal to grant access to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantReadData", [grantee])

    @jsii.member(jsii_name="grantReadWriteData")
    def grant_read_write_data(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Permits an IAM principal to all data read/write operations to this table. BatchGetItem, GetRecords, GetShardIterator, Query, GetItem, Scan, BatchWriteItem, PutItem, UpdateItem, DeleteItem.

        Arguments:
            grantee: The principal to grant access to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantReadWriteData", [grantee])

    @jsii.member(jsii_name="grantStream")
    def grant_stream(self, grantee: aws_cdk.aws_iam.IGrantable, *actions: str) -> aws_cdk.aws_iam.Grant:
        """Adds an IAM policy statement associated with this table's stream to an IAM principal's policy.

        Arguments:
            grantee: The principal (no-op if undefined).
            actions: The set of actions to allow (i.e. "dynamodb:DescribeStream", "dynamodb:GetRecords", ...).

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantStream", [grantee, *actions])

    @jsii.member(jsii_name="grantStreamRead")
    def grant_stream_read(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Permis an IAM principal all stream data read operations for this table's stream: DescribeStream, GetRecords, GetShardIterator, ListStreams.

        Arguments:
            grantee: The principal to grant access to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantStreamRead", [grantee])

    @jsii.member(jsii_name="grantWriteData")
    def grant_write_data(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Permits an IAM principal all data write operations to this table: BatchWriteItem, PutItem, UpdateItem, DeleteItem.

        Arguments:
            grantee: The principal to grant access to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantWriteData", [grantee])

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[str]:
        """Validate the table construct.

        Returns:
            an array of validation error message

        Stability:
            experimental
        """
        return jsii.invoke(self, "validate", [])

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

    @property
    @jsii.member(jsii_name="tableStreamArn")
    def table_stream_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "tableStreamArn")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _TableOptions(jsii.compat.TypedDict, total=False):
    billingMode: "BillingMode"
    """Specify how you are charged for read and write throughput and how you manage capacity.

    Default:
        Provisioned

    Stability:
        experimental
    """
    pitrEnabled: bool
    """Whether point-in-time recovery is enabled.

    Default:
        undefined, point-in-time recovery is disabled

    Stability:
        experimental
    """
    readCapacity: jsii.Number
    """The read capacity for the table.

    Careful if you add Global Secondary Indexes, as
    those will share the table's provisioned throughput.

    Can only be provided if billingMode is Provisioned.

    Default:
        5

    Stability:
        experimental
    """
    sortKey: "Attribute"
    """Table sort key attribute definition.

    Default:
        no sort key

    Stability:
        experimental
    """
    sseEnabled: bool
    """Whether server-side encryption with an AWS managed customer master key is enabled.

    Default:
        undefined, server-side encryption is enabled with an AWS owned customer master key

    Stability:
        experimental
    """
    streamSpecification: "StreamViewType"
    """When an item in the table is modified, StreamViewType determines what information is written to the stream for this table.

    Valid values for StreamViewType are:

    Default:
        undefined, streams are disabled

    Stability:
        experimental
    """
    ttlAttributeName: str
    """The name of TTL attribute.

    Default:
        undefined, TTL is disabled

    Stability:
        experimental
    """
    writeCapacity: jsii.Number
    """The write capacity for the table.

    Careful if you add Global Secondary Indexes, as
    those will share the table's provisioned throughput.

    Can only be provided if billingMode is Provisioned.

    Default:
        5

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.TableOptions", jsii_struct_bases=[_TableOptions])
class TableOptions(_TableOptions):
    """
    Stability:
        experimental
    """
    partitionKey: "Attribute"
    """Partition key attribute definition.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.TableProps", jsii_struct_bases=[TableOptions])
class TableProps(TableOptions, jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    tableName: str
    """Enforces a particular physical table name.

    Default:
        
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb.UtilizationScalingProps", jsii_struct_bases=[aws_cdk.aws_applicationautoscaling.BaseTargetTrackingProps])
class UtilizationScalingProps(aws_cdk.aws_applicationautoscaling.BaseTargetTrackingProps, jsii.compat.TypedDict):
    """Properties for enabling DynamoDB utilization tracking.

    Stability:
        experimental
    """
    targetUtilizationPercent: jsii.Number
    """Target utilization percentage for the attribute.

    Stability:
        experimental
    """

__all__ = ["Attribute", "AttributeType", "BillingMode", "CfnTable", "CfnTableProps", "EnableScalingProps", "GlobalSecondaryIndexProps", "IScalableTableAttribute", "LocalSecondaryIndexProps", "ProjectionType", "SecondaryIndexProps", "StreamViewType", "Table", "TableOptions", "TableProps", "UtilizationScalingProps", "__jsii_assembly__"]

publication.publish()
