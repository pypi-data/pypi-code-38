import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-dax", "0.35.0", __name__, "aws-dax@0.35.0.jsii.tgz")
class CfnCluster(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dax.CfnCluster"):
    """A CloudFormation ``AWS::DAX::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DAX::Cluster
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, iam_role_arn: str, node_type: str, replication_factor: jsii.Number, availability_zones: typing.Optional[typing.List[str]]=None, cluster_name: typing.Optional[str]=None, description: typing.Optional[str]=None, notification_topic_arn: typing.Optional[str]=None, parameter_group_name: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, sse_specification: typing.Optional[typing.Union[typing.Optional["SSESpecificationProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, subnet_group_name: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[typing.Any, typing.Any]]=None) -> None:
        """Create a new ``AWS::DAX::Cluster``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            iamRoleArn: ``AWS::DAX::Cluster.IAMRoleARN``.
            nodeType: ``AWS::DAX::Cluster.NodeType``.
            replicationFactor: ``AWS::DAX::Cluster.ReplicationFactor``.
            availabilityZones: ``AWS::DAX::Cluster.AvailabilityZones``.
            clusterName: ``AWS::DAX::Cluster.ClusterName``.
            description: ``AWS::DAX::Cluster.Description``.
            notificationTopicArn: ``AWS::DAX::Cluster.NotificationTopicARN``.
            parameterGroupName: ``AWS::DAX::Cluster.ParameterGroupName``.
            preferredMaintenanceWindow: ``AWS::DAX::Cluster.PreferredMaintenanceWindow``.
            securityGroupIds: ``AWS::DAX::Cluster.SecurityGroupIds``.
            sseSpecification: ``AWS::DAX::Cluster.SSESpecification``.
            subnetGroupName: ``AWS::DAX::Cluster.SubnetGroupName``.
            tags: ``AWS::DAX::Cluster.Tags``.

        Stability:
            experimental
        """
        props: CfnClusterProps = {"iamRoleArn": iam_role_arn, "nodeType": node_type, "replicationFactor": replication_factor}

        if availability_zones is not None:
            props["availabilityZones"] = availability_zones

        if cluster_name is not None:
            props["clusterName"] = cluster_name

        if description is not None:
            props["description"] = description

        if notification_topic_arn is not None:
            props["notificationTopicArn"] = notification_topic_arn

        if parameter_group_name is not None:
            props["parameterGroupName"] = parameter_group_name

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if security_group_ids is not None:
            props["securityGroupIds"] = security_group_ids

        if sse_specification is not None:
            props["sseSpecification"] = sse_specification

        if subnet_group_name is not None:
            props["subnetGroupName"] = subnet_group_name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnCluster, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrClusterDiscoveryEndpoint")
    def attr_cluster_discovery_endpoint(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ClusterDiscoveryEndpoint
        """
        return jsii.get(self, "attrClusterDiscoveryEndpoint")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::DAX::Cluster.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="iamRoleArn")
    def iam_role_arn(self) -> str:
        """``AWS::DAX::Cluster.IAMRoleARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-iamrolearn
        Stability:
            experimental
        """
        return jsii.get(self, "iamRoleArn")

    @iam_role_arn.setter
    def iam_role_arn(self, value: str):
        return jsii.set(self, "iamRoleArn", value)

    @property
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> str:
        """``AWS::DAX::Cluster.NodeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-nodetype
        Stability:
            experimental
        """
        return jsii.get(self, "nodeType")

    @node_type.setter
    def node_type(self, value: str):
        return jsii.set(self, "nodeType", value)

    @property
    @jsii.member(jsii_name="replicationFactor")
    def replication_factor(self) -> jsii.Number:
        """``AWS::DAX::Cluster.ReplicationFactor``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-replicationfactor
        Stability:
            experimental
        """
        return jsii.get(self, "replicationFactor")

    @replication_factor.setter
    def replication_factor(self, value: jsii.Number):
        return jsii.set(self, "replicationFactor", value)

    @property
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DAX::Cluster.AvailabilityZones``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-availabilityzones
        Stability:
            experimental
        """
        return jsii.get(self, "availabilityZones")

    @availability_zones.setter
    def availability_zones(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "availabilityZones", value)

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> typing.Optional[str]:
        """``AWS::DAX::Cluster.ClusterName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-clustername
        Stability:
            experimental
        """
        return jsii.get(self, "clusterName")

    @cluster_name.setter
    def cluster_name(self, value: typing.Optional[str]):
        return jsii.set(self, "clusterName", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::DAX::Cluster.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="notificationTopicArn")
    def notification_topic_arn(self) -> typing.Optional[str]:
        """``AWS::DAX::Cluster.NotificationTopicARN``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-notificationtopicarn
        Stability:
            experimental
        """
        return jsii.get(self, "notificationTopicArn")

    @notification_topic_arn.setter
    def notification_topic_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "notificationTopicArn", value)

    @property
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::DAX::Cluster.ParameterGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-parametergroupname
        Stability:
            experimental
        """
        return jsii.get(self, "parameterGroupName")

    @parameter_group_name.setter
    def parameter_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "parameterGroupName", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::DAX::Cluster.PreferredMaintenanceWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-preferredmaintenancewindow
        Stability:
            experimental
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)

    @property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DAX::Cluster.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-securitygroupids
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupIds")

    @security_group_ids.setter
    def security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "securityGroupIds", value)

    @property
    @jsii.member(jsii_name="sseSpecification")
    def sse_specification(self) -> typing.Optional[typing.Union[typing.Optional["SSESpecificationProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::DAX::Cluster.SSESpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-ssespecification
        Stability:
            experimental
        """
        return jsii.get(self, "sseSpecification")

    @sse_specification.setter
    def sse_specification(self, value: typing.Optional[typing.Union[typing.Optional["SSESpecificationProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "sseSpecification", value)

    @property
    @jsii.member(jsii_name="subnetGroupName")
    def subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::DAX::Cluster.SubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-subnetgroupname
        Stability:
            experimental
        """
        return jsii.get(self, "subnetGroupName")

    @subnet_group_name.setter
    def subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "subnetGroupName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-dax.CfnCluster.SSESpecificationProperty", jsii_struct_bases=[])
    class SSESpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dax-cluster-ssespecification.html
        Stability:
            experimental
        """
        sseEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnCluster.SSESpecificationProperty.SSEEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dax-cluster-ssespecification.html#cfn-dax-cluster-ssespecification-sseenabled
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnClusterProps(jsii.compat.TypedDict, total=False):
    availabilityZones: typing.List[str]
    """``AWS::DAX::Cluster.AvailabilityZones``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-availabilityzones
    Stability:
        experimental
    """
    clusterName: str
    """``AWS::DAX::Cluster.ClusterName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-clustername
    Stability:
        experimental
    """
    description: str
    """``AWS::DAX::Cluster.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-description
    Stability:
        experimental
    """
    notificationTopicArn: str
    """``AWS::DAX::Cluster.NotificationTopicARN``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-notificationtopicarn
    Stability:
        experimental
    """
    parameterGroupName: str
    """``AWS::DAX::Cluster.ParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-parametergroupname
    Stability:
        experimental
    """
    preferredMaintenanceWindow: str
    """``AWS::DAX::Cluster.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-preferredmaintenancewindow
    Stability:
        experimental
    """
    securityGroupIds: typing.List[str]
    """``AWS::DAX::Cluster.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-securitygroupids
    Stability:
        experimental
    """
    sseSpecification: typing.Union["CfnCluster.SSESpecificationProperty", aws_cdk.cdk.IResolvable]
    """``AWS::DAX::Cluster.SSESpecification``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-ssespecification
    Stability:
        experimental
    """
    subnetGroupName: str
    """``AWS::DAX::Cluster.SubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-subnetgroupname
    Stability:
        experimental
    """
    tags: typing.Mapping[typing.Any, typing.Any]
    """``AWS::DAX::Cluster.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dax.CfnClusterProps", jsii_struct_bases=[_CfnClusterProps])
class CfnClusterProps(_CfnClusterProps):
    """Properties for defining a ``AWS::DAX::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html
    Stability:
        experimental
    """
    iamRoleArn: str
    """``AWS::DAX::Cluster.IAMRoleARN``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-iamrolearn
    Stability:
        experimental
    """

    nodeType: str
    """``AWS::DAX::Cluster.NodeType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-nodetype
    Stability:
        experimental
    """

    replicationFactor: jsii.Number
    """``AWS::DAX::Cluster.ReplicationFactor``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-cluster.html#cfn-dax-cluster-replicationfactor
    Stability:
        experimental
    """

class CfnParameterGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dax.CfnParameterGroup"):
    """A CloudFormation ``AWS::DAX::ParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-parametergroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DAX::ParameterGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: typing.Optional[str]=None, parameter_group_name: typing.Optional[str]=None, parameter_name_values: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]=None) -> None:
        """Create a new ``AWS::DAX::ParameterGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::DAX::ParameterGroup.Description``.
            parameterGroupName: ``AWS::DAX::ParameterGroup.ParameterGroupName``.
            parameterNameValues: ``AWS::DAX::ParameterGroup.ParameterNameValues``.

        Stability:
            experimental
        """
        props: CfnParameterGroupProps = {}

        if description is not None:
            props["description"] = description

        if parameter_group_name is not None:
            props["parameterGroupName"] = parameter_group_name

        if parameter_name_values is not None:
            props["parameterNameValues"] = parameter_name_values

        jsii.create(CfnParameterGroup, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::DAX::ParameterGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-parametergroup.html#cfn-dax-parametergroup-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::DAX::ParameterGroup.ParameterGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-parametergroup.html#cfn-dax-parametergroup-parametergroupname
        Stability:
            experimental
        """
        return jsii.get(self, "parameterGroupName")

    @parameter_group_name.setter
    def parameter_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "parameterGroupName", value)

    @property
    @jsii.member(jsii_name="parameterNameValues")
    def parameter_name_values(self) -> typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::DAX::ParameterGroup.ParameterNameValues``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-parametergroup.html#cfn-dax-parametergroup-parameternamevalues
        Stability:
            experimental
        """
        return jsii.get(self, "parameterNameValues")

    @parameter_name_values.setter
    def parameter_name_values(self, value: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "parameterNameValues", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-dax.CfnParameterGroupProps", jsii_struct_bases=[])
class CfnParameterGroupProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::DAX::ParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-parametergroup.html
    Stability:
        experimental
    """
    description: str
    """``AWS::DAX::ParameterGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-parametergroup.html#cfn-dax-parametergroup-description
    Stability:
        experimental
    """

    parameterGroupName: str
    """``AWS::DAX::ParameterGroup.ParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-parametergroup.html#cfn-dax-parametergroup-parametergroupname
    Stability:
        experimental
    """

    parameterNameValues: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::DAX::ParameterGroup.ParameterNameValues``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-parametergroup.html#cfn-dax-parametergroup-parameternamevalues
    Stability:
        experimental
    """

class CfnSubnetGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-dax.CfnSubnetGroup"):
    """A CloudFormation ``AWS::DAX::SubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-subnetgroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DAX::SubnetGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, subnet_ids: typing.List[str], description: typing.Optional[str]=None, subnet_group_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::DAX::SubnetGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            subnetIds: ``AWS::DAX::SubnetGroup.SubnetIds``.
            description: ``AWS::DAX::SubnetGroup.Description``.
            subnetGroupName: ``AWS::DAX::SubnetGroup.SubnetGroupName``.

        Stability:
            experimental
        """
        props: CfnSubnetGroupProps = {"subnetIds": subnet_ids}

        if description is not None:
            props["description"] = description

        if subnet_group_name is not None:
            props["subnetGroupName"] = subnet_group_name

        jsii.create(CfnSubnetGroup, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::DAX::SubnetGroup.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-subnetgroup.html#cfn-dax-subnetgroup-subnetids
        Stability:
            experimental
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[str]):
        return jsii.set(self, "subnetIds", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::DAX::SubnetGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-subnetgroup.html#cfn-dax-subnetgroup-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="subnetGroupName")
    def subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::DAX::SubnetGroup.SubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-subnetgroup.html#cfn-dax-subnetgroup-subnetgroupname
        Stability:
            experimental
        """
        return jsii.get(self, "subnetGroupName")

    @subnet_group_name.setter
    def subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "subnetGroupName", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSubnetGroupProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::DAX::SubnetGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-subnetgroup.html#cfn-dax-subnetgroup-description
    Stability:
        experimental
    """
    subnetGroupName: str
    """``AWS::DAX::SubnetGroup.SubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-subnetgroup.html#cfn-dax-subnetgroup-subnetgroupname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-dax.CfnSubnetGroupProps", jsii_struct_bases=[_CfnSubnetGroupProps])
class CfnSubnetGroupProps(_CfnSubnetGroupProps):
    """Properties for defining a ``AWS::DAX::SubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-subnetgroup.html
    Stability:
        experimental
    """
    subnetIds: typing.List[str]
    """``AWS::DAX::SubnetGroup.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dax-subnetgroup.html#cfn-dax-subnetgroup-subnetids
    Stability:
        experimental
    """

__all__ = ["CfnCluster", "CfnClusterProps", "CfnParameterGroup", "CfnParameterGroupProps", "CfnSubnetGroup", "CfnSubnetGroupProps", "__jsii_assembly__"]

publication.publish()
