import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_cloudformation
import aws_cdk.aws_dynamodb
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-dynamodb-global", "0.34.0", __name__, "aws-dynamodb-global@0.34.0.jsii.tgz")
class GlobalTable(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dynamodb-global.GlobalTable"):
    """This class works by deploying an AWS DynamoDB table into each region specified in  GlobalTableProps.regions[], then triggering a CloudFormation Custom Resource Lambda to link them all together to create linked AWS Global DynamoDB tables.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, regions: typing.List[str], table_name: str, env: typing.Optional[aws_cdk.cdk.Environment]=None, naming_scheme: typing.Optional[aws_cdk.cdk.IAddressingScheme]=None, stack_name: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[str,str]]=None, partition_key: aws_cdk.aws_dynamodb.Attribute, billing_mode: typing.Optional[aws_cdk.aws_dynamodb.BillingMode]=None, pitr_enabled: typing.Optional[bool]=None, read_capacity: typing.Optional[jsii.Number]=None, sort_key: typing.Optional[aws_cdk.aws_dynamodb.Attribute]=None, sse_enabled: typing.Optional[bool]=None, stream_specification: typing.Optional[aws_cdk.aws_dynamodb.StreamViewType]=None, ttl_attribute_name: typing.Optional[str]=None, write_capacity: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            regions: Array of environments to create DynamoDB tables in. The tables will all be created in the same account.
            tableName: Name of the DynamoDB table to use across all regional tables. This is required for global tables.
            env: The AWS environment (account/region) where this stack will be deployed. Default: - The ``default-account`` and ``default-region`` context parameters will be used. If they are undefined, it will not be possible to deploy the stack.
            namingScheme: Strategy for logical ID generation. Default: - The HashedNamingScheme will be used.
            stackName: Name to deploy the stack with. Default: - Derived from construct path.
            tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
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
        props: GlobalTableProps = {"regions": regions, "tableName": table_name, "partitionKey": partition_key}

        if env is not None:
            props["env"] = env

        if naming_scheme is not None:
            props["namingScheme"] = naming_scheme

        if stack_name is not None:
            props["stackName"] = stack_name

        if tags is not None:
            props["tags"] = tags

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

        jsii.create(GlobalTable, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="regionalTables")
    def regional_tables(self) -> typing.List[aws_cdk.aws_dynamodb.Table]:
        """Obtain tables deployed in other each region.

        Stability:
            experimental
        """
        return jsii.get(self, "regionalTables")


@jsii.data_type(jsii_type="@aws-cdk/aws-dynamodb-global.GlobalTableProps", jsii_struct_bases=[aws_cdk.cdk.StackProps, aws_cdk.aws_dynamodb.TableOptions])
class GlobalTableProps(aws_cdk.cdk.StackProps, aws_cdk.aws_dynamodb.TableOptions, jsii.compat.TypedDict):
    """Properties for the mutliple DynamoDB tables to mash together into a global table.

    Stability:
        experimental
    """
    regions: typing.List[str]
    """Array of environments to create DynamoDB tables in. The tables will all be created in the same account.

    Stability:
        experimental
    """

    tableName: str
    """Name of the DynamoDB table to use across all regional tables. This is required for global tables.

    Stability:
        experimental
    """

__all__ = ["GlobalTable", "GlobalTableProps", "__jsii_assembly__"]

publication.publish()
