import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-elasticache", "0.34.0", __name__, "aws-elasticache@0.34.0.jsii.tgz")
class CfnCacheCluster(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticache.CfnCacheCluster"):
    """A CloudFormation ``AWS::ElastiCache::CacheCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ElastiCache::CacheCluster
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cache_node_type: str, engine: str, num_cache_nodes: typing.Union[jsii.Number, aws_cdk.cdk.Token], auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, az_mode: typing.Optional[str]=None, cache_parameter_group_name: typing.Optional[str]=None, cache_security_group_names: typing.Optional[typing.List[str]]=None, cache_subnet_group_name: typing.Optional[str]=None, cluster_name: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, notification_topic_arn: typing.Optional[str]=None, port: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, preferred_availability_zone: typing.Optional[str]=None, preferred_availability_zones: typing.Optional[typing.List[str]]=None, preferred_maintenance_window: typing.Optional[str]=None, snapshot_arns: typing.Optional[typing.List[str]]=None, snapshot_name: typing.Optional[str]=None, snapshot_retention_limit: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, snapshot_window: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::ElastiCache::CacheCluster``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            cacheNodeType: ``AWS::ElastiCache::CacheCluster.CacheNodeType``.
            engine: ``AWS::ElastiCache::CacheCluster.Engine``.
            numCacheNodes: ``AWS::ElastiCache::CacheCluster.NumCacheNodes``.
            autoMinorVersionUpgrade: ``AWS::ElastiCache::CacheCluster.AutoMinorVersionUpgrade``.
            azMode: ``AWS::ElastiCache::CacheCluster.AZMode``.
            cacheParameterGroupName: ``AWS::ElastiCache::CacheCluster.CacheParameterGroupName``.
            cacheSecurityGroupNames: ``AWS::ElastiCache::CacheCluster.CacheSecurityGroupNames``.
            cacheSubnetGroupName: ``AWS::ElastiCache::CacheCluster.CacheSubnetGroupName``.
            clusterName: ``AWS::ElastiCache::CacheCluster.ClusterName``.
            engineVersion: ``AWS::ElastiCache::CacheCluster.EngineVersion``.
            notificationTopicArn: ``AWS::ElastiCache::CacheCluster.NotificationTopicArn``.
            port: ``AWS::ElastiCache::CacheCluster.Port``.
            preferredAvailabilityZone: ``AWS::ElastiCache::CacheCluster.PreferredAvailabilityZone``.
            preferredAvailabilityZones: ``AWS::ElastiCache::CacheCluster.PreferredAvailabilityZones``.
            preferredMaintenanceWindow: ``AWS::ElastiCache::CacheCluster.PreferredMaintenanceWindow``.
            snapshotArns: ``AWS::ElastiCache::CacheCluster.SnapshotArns``.
            snapshotName: ``AWS::ElastiCache::CacheCluster.SnapshotName``.
            snapshotRetentionLimit: ``AWS::ElastiCache::CacheCluster.SnapshotRetentionLimit``.
            snapshotWindow: ``AWS::ElastiCache::CacheCluster.SnapshotWindow``.
            tags: ``AWS::ElastiCache::CacheCluster.Tags``.
            vpcSecurityGroupIds: ``AWS::ElastiCache::CacheCluster.VpcSecurityGroupIds``.

        Stability:
            experimental
        """
        props: CfnCacheClusterProps = {"cacheNodeType": cache_node_type, "engine": engine, "numCacheNodes": num_cache_nodes}

        if auto_minor_version_upgrade is not None:
            props["autoMinorVersionUpgrade"] = auto_minor_version_upgrade

        if az_mode is not None:
            props["azMode"] = az_mode

        if cache_parameter_group_name is not None:
            props["cacheParameterGroupName"] = cache_parameter_group_name

        if cache_security_group_names is not None:
            props["cacheSecurityGroupNames"] = cache_security_group_names

        if cache_subnet_group_name is not None:
            props["cacheSubnetGroupName"] = cache_subnet_group_name

        if cluster_name is not None:
            props["clusterName"] = cluster_name

        if engine_version is not None:
            props["engineVersion"] = engine_version

        if notification_topic_arn is not None:
            props["notificationTopicArn"] = notification_topic_arn

        if port is not None:
            props["port"] = port

        if preferred_availability_zone is not None:
            props["preferredAvailabilityZone"] = preferred_availability_zone

        if preferred_availability_zones is not None:
            props["preferredAvailabilityZones"] = preferred_availability_zones

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if snapshot_arns is not None:
            props["snapshotArns"] = snapshot_arns

        if snapshot_name is not None:
            props["snapshotName"] = snapshot_name

        if snapshot_retention_limit is not None:
            props["snapshotRetentionLimit"] = snapshot_retention_limit

        if snapshot_window is not None:
            props["snapshotWindow"] = snapshot_window

        if tags is not None:
            props["tags"] = tags

        if vpc_security_group_ids is not None:
            props["vpcSecurityGroupIds"] = vpc_security_group_ids

        jsii.create(CfnCacheCluster, self, [scope, id, props])

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
    @jsii.member(jsii_name="cacheClusterConfigurationEndpointAddress")
    def cache_cluster_configuration_endpoint_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ConfigurationEndpoint.Address
        """
        return jsii.get(self, "cacheClusterConfigurationEndpointAddress")

    @property
    @jsii.member(jsii_name="cacheClusterConfigurationEndpointPort")
    def cache_cluster_configuration_endpoint_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ConfigurationEndpoint.Port
        """
        return jsii.get(self, "cacheClusterConfigurationEndpointPort")

    @property
    @jsii.member(jsii_name="cacheClusterName")
    def cache_cluster_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cacheClusterName")

    @property
    @jsii.member(jsii_name="cacheClusterRedisEndpointAddress")
    def cache_cluster_redis_endpoint_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RedisEndpoint.Address
        """
        return jsii.get(self, "cacheClusterRedisEndpointAddress")

    @property
    @jsii.member(jsii_name="cacheClusterRedisEndpointPort")
    def cache_cluster_redis_endpoint_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RedisEndpoint.Port
        """
        return jsii.get(self, "cacheClusterRedisEndpointPort")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnCacheClusterProps":
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
class _CfnCacheClusterProps(jsii.compat.TypedDict, total=False):
    autoMinorVersionUpgrade: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::CacheCluster.AutoMinorVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-autominorversionupgrade
    Stability:
        experimental
    """
    azMode: str
    """``AWS::ElastiCache::CacheCluster.AZMode``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-azmode
    Stability:
        experimental
    """
    cacheParameterGroupName: str
    """``AWS::ElastiCache::CacheCluster.CacheParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-cacheparametergroupname
    Stability:
        experimental
    """
    cacheSecurityGroupNames: typing.List[str]
    """``AWS::ElastiCache::CacheCluster.CacheSecurityGroupNames``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-cachesecuritygroupnames
    Stability:
        experimental
    """
    cacheSubnetGroupName: str
    """``AWS::ElastiCache::CacheCluster.CacheSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-cachesubnetgroupname
    Stability:
        experimental
    """
    clusterName: str
    """``AWS::ElastiCache::CacheCluster.ClusterName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-clustername
    Stability:
        experimental
    """
    engineVersion: str
    """``AWS::ElastiCache::CacheCluster.EngineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-engineversion
    Stability:
        experimental
    """
    notificationTopicArn: str
    """``AWS::ElastiCache::CacheCluster.NotificationTopicArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-notificationtopicarn
    Stability:
        experimental
    """
    port: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::CacheCluster.Port``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-port
    Stability:
        experimental
    """
    preferredAvailabilityZone: str
    """``AWS::ElastiCache::CacheCluster.PreferredAvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-preferredavailabilityzone
    Stability:
        experimental
    """
    preferredAvailabilityZones: typing.List[str]
    """``AWS::ElastiCache::CacheCluster.PreferredAvailabilityZones``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-preferredavailabilityzones
    Stability:
        experimental
    """
    preferredMaintenanceWindow: str
    """``AWS::ElastiCache::CacheCluster.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-preferredmaintenancewindow
    Stability:
        experimental
    """
    snapshotArns: typing.List[str]
    """``AWS::ElastiCache::CacheCluster.SnapshotArns``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-snapshotarns
    Stability:
        experimental
    """
    snapshotName: str
    """``AWS::ElastiCache::CacheCluster.SnapshotName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-snapshotname
    Stability:
        experimental
    """
    snapshotRetentionLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::CacheCluster.SnapshotRetentionLimit``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-snapshotretentionlimit
    Stability:
        experimental
    """
    snapshotWindow: str
    """``AWS::ElastiCache::CacheCluster.SnapshotWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-snapshotwindow
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::ElastiCache::CacheCluster.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-tags
    Stability:
        experimental
    """
    vpcSecurityGroupIds: typing.List[str]
    """``AWS::ElastiCache::CacheCluster.VpcSecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-vpcsecuritygroupids
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticache.CfnCacheClusterProps", jsii_struct_bases=[_CfnCacheClusterProps])
class CfnCacheClusterProps(_CfnCacheClusterProps):
    """Properties for defining a ``AWS::ElastiCache::CacheCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html
    Stability:
        experimental
    """
    cacheNodeType: str
    """``AWS::ElastiCache::CacheCluster.CacheNodeType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-cachenodetype
    Stability:
        experimental
    """

    engine: str
    """``AWS::ElastiCache::CacheCluster.Engine``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-engine
    Stability:
        experimental
    """

    numCacheNodes: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::CacheCluster.NumCacheNodes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-numcachenodes
    Stability:
        experimental
    """

class CfnParameterGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticache.CfnParameterGroup"):
    """A CloudFormation ``AWS::ElastiCache::ParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-parameter-group.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ElastiCache::ParameterGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cache_parameter_group_family: str, description: str, properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.Mapping[str,str]]]]=None) -> None:
        """Create a new ``AWS::ElastiCache::ParameterGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            cacheParameterGroupFamily: ``AWS::ElastiCache::ParameterGroup.CacheParameterGroupFamily``.
            description: ``AWS::ElastiCache::ParameterGroup.Description``.
            properties: ``AWS::ElastiCache::ParameterGroup.Properties``.

        Stability:
            experimental
        """
        props: CfnParameterGroupProps = {"cacheParameterGroupFamily": cache_parameter_group_family, "description": description}

        if properties is not None:
            props["properties"] = properties

        jsii.create(CfnParameterGroup, self, [scope, id, props])

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
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "parameterGroupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnParameterGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnParameterGroupProps(jsii.compat.TypedDict, total=False):
    properties: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
    """``AWS::ElastiCache::ParameterGroup.Properties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-parameter-group.html#cfn-elasticache-parametergroup-properties
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticache.CfnParameterGroupProps", jsii_struct_bases=[_CfnParameterGroupProps])
class CfnParameterGroupProps(_CfnParameterGroupProps):
    """Properties for defining a ``AWS::ElastiCache::ParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-parameter-group.html
    Stability:
        experimental
    """
    cacheParameterGroupFamily: str
    """``AWS::ElastiCache::ParameterGroup.CacheParameterGroupFamily``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-parameter-group.html#cfn-elasticache-parametergroup-cacheparametergroupfamily
    Stability:
        experimental
    """

    description: str
    """``AWS::ElastiCache::ParameterGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-parameter-group.html#cfn-elasticache-parametergroup-description
    Stability:
        experimental
    """

class CfnReplicationGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticache.CfnReplicationGroup"):
    """A CloudFormation ``AWS::ElastiCache::ReplicationGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ElastiCache::ReplicationGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, replication_group_description: str, at_rest_encryption_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, auth_token: typing.Optional[str]=None, automatic_failover_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, cache_node_type: typing.Optional[str]=None, cache_parameter_group_name: typing.Optional[str]=None, cache_security_group_names: typing.Optional[typing.List[str]]=None, cache_subnet_group_name: typing.Optional[str]=None, engine: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, node_group_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "NodeGroupConfigurationProperty"]]]]]=None, notification_topic_arn: typing.Optional[str]=None, num_cache_clusters: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, num_node_groups: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, port: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, preferred_cache_cluster_a_zs: typing.Optional[typing.List[str]]=None, preferred_maintenance_window: typing.Optional[str]=None, primary_cluster_id: typing.Optional[str]=None, replicas_per_node_group: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, replication_group_id: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, snapshot_arns: typing.Optional[typing.List[str]]=None, snapshot_name: typing.Optional[str]=None, snapshot_retention_limit: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, snapshotting_cluster_id: typing.Optional[str]=None, snapshot_window: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, transit_encryption_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::ElastiCache::ReplicationGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            replicationGroupDescription: ``AWS::ElastiCache::ReplicationGroup.ReplicationGroupDescription``.
            atRestEncryptionEnabled: ``AWS::ElastiCache::ReplicationGroup.AtRestEncryptionEnabled``.
            authToken: ``AWS::ElastiCache::ReplicationGroup.AuthToken``.
            automaticFailoverEnabled: ``AWS::ElastiCache::ReplicationGroup.AutomaticFailoverEnabled``.
            autoMinorVersionUpgrade: ``AWS::ElastiCache::ReplicationGroup.AutoMinorVersionUpgrade``.
            cacheNodeType: ``AWS::ElastiCache::ReplicationGroup.CacheNodeType``.
            cacheParameterGroupName: ``AWS::ElastiCache::ReplicationGroup.CacheParameterGroupName``.
            cacheSecurityGroupNames: ``AWS::ElastiCache::ReplicationGroup.CacheSecurityGroupNames``.
            cacheSubnetGroupName: ``AWS::ElastiCache::ReplicationGroup.CacheSubnetGroupName``.
            engine: ``AWS::ElastiCache::ReplicationGroup.Engine``.
            engineVersion: ``AWS::ElastiCache::ReplicationGroup.EngineVersion``.
            nodeGroupConfiguration: ``AWS::ElastiCache::ReplicationGroup.NodeGroupConfiguration``.
            notificationTopicArn: ``AWS::ElastiCache::ReplicationGroup.NotificationTopicArn``.
            numCacheClusters: ``AWS::ElastiCache::ReplicationGroup.NumCacheClusters``.
            numNodeGroups: ``AWS::ElastiCache::ReplicationGroup.NumNodeGroups``.
            port: ``AWS::ElastiCache::ReplicationGroup.Port``.
            preferredCacheClusterAZs: ``AWS::ElastiCache::ReplicationGroup.PreferredCacheClusterAZs``.
            preferredMaintenanceWindow: ``AWS::ElastiCache::ReplicationGroup.PreferredMaintenanceWindow``.
            primaryClusterId: ``AWS::ElastiCache::ReplicationGroup.PrimaryClusterId``.
            replicasPerNodeGroup: ``AWS::ElastiCache::ReplicationGroup.ReplicasPerNodeGroup``.
            replicationGroupId: ``AWS::ElastiCache::ReplicationGroup.ReplicationGroupId``.
            securityGroupIds: ``AWS::ElastiCache::ReplicationGroup.SecurityGroupIds``.
            snapshotArns: ``AWS::ElastiCache::ReplicationGroup.SnapshotArns``.
            snapshotName: ``AWS::ElastiCache::ReplicationGroup.SnapshotName``.
            snapshotRetentionLimit: ``AWS::ElastiCache::ReplicationGroup.SnapshotRetentionLimit``.
            snapshottingClusterId: ``AWS::ElastiCache::ReplicationGroup.SnapshottingClusterId``.
            snapshotWindow: ``AWS::ElastiCache::ReplicationGroup.SnapshotWindow``.
            tags: ``AWS::ElastiCache::ReplicationGroup.Tags``.
            transitEncryptionEnabled: ``AWS::ElastiCache::ReplicationGroup.TransitEncryptionEnabled``.

        Stability:
            experimental
        """
        props: CfnReplicationGroupProps = {"replicationGroupDescription": replication_group_description}

        if at_rest_encryption_enabled is not None:
            props["atRestEncryptionEnabled"] = at_rest_encryption_enabled

        if auth_token is not None:
            props["authToken"] = auth_token

        if automatic_failover_enabled is not None:
            props["automaticFailoverEnabled"] = automatic_failover_enabled

        if auto_minor_version_upgrade is not None:
            props["autoMinorVersionUpgrade"] = auto_minor_version_upgrade

        if cache_node_type is not None:
            props["cacheNodeType"] = cache_node_type

        if cache_parameter_group_name is not None:
            props["cacheParameterGroupName"] = cache_parameter_group_name

        if cache_security_group_names is not None:
            props["cacheSecurityGroupNames"] = cache_security_group_names

        if cache_subnet_group_name is not None:
            props["cacheSubnetGroupName"] = cache_subnet_group_name

        if engine is not None:
            props["engine"] = engine

        if engine_version is not None:
            props["engineVersion"] = engine_version

        if node_group_configuration is not None:
            props["nodeGroupConfiguration"] = node_group_configuration

        if notification_topic_arn is not None:
            props["notificationTopicArn"] = notification_topic_arn

        if num_cache_clusters is not None:
            props["numCacheClusters"] = num_cache_clusters

        if num_node_groups is not None:
            props["numNodeGroups"] = num_node_groups

        if port is not None:
            props["port"] = port

        if preferred_cache_cluster_a_zs is not None:
            props["preferredCacheClusterAZs"] = preferred_cache_cluster_a_zs

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if primary_cluster_id is not None:
            props["primaryClusterId"] = primary_cluster_id

        if replicas_per_node_group is not None:
            props["replicasPerNodeGroup"] = replicas_per_node_group

        if replication_group_id is not None:
            props["replicationGroupId"] = replication_group_id

        if security_group_ids is not None:
            props["securityGroupIds"] = security_group_ids

        if snapshot_arns is not None:
            props["snapshotArns"] = snapshot_arns

        if snapshot_name is not None:
            props["snapshotName"] = snapshot_name

        if snapshot_retention_limit is not None:
            props["snapshotRetentionLimit"] = snapshot_retention_limit

        if snapshotting_cluster_id is not None:
            props["snapshottingClusterId"] = snapshotting_cluster_id

        if snapshot_window is not None:
            props["snapshotWindow"] = snapshot_window

        if tags is not None:
            props["tags"] = tags

        if transit_encryption_enabled is not None:
            props["transitEncryptionEnabled"] = transit_encryption_enabled

        jsii.create(CfnReplicationGroup, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnReplicationGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="replicationGroupConfigurationEndPointAddress")
    def replication_group_configuration_end_point_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ConfigurationEndPoint.Address
        """
        return jsii.get(self, "replicationGroupConfigurationEndPointAddress")

    @property
    @jsii.member(jsii_name="replicationGroupConfigurationEndPointPort")
    def replication_group_configuration_end_point_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ConfigurationEndPoint.Port
        """
        return jsii.get(self, "replicationGroupConfigurationEndPointPort")

    @property
    @jsii.member(jsii_name="replicationGroupName")
    def replication_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "replicationGroupName")

    @property
    @jsii.member(jsii_name="replicationGroupPrimaryEndPointAddress")
    def replication_group_primary_end_point_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            PrimaryEndPoint.Address
        """
        return jsii.get(self, "replicationGroupPrimaryEndPointAddress")

    @property
    @jsii.member(jsii_name="replicationGroupPrimaryEndPointPort")
    def replication_group_primary_end_point_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            PrimaryEndPoint.Port
        """
        return jsii.get(self, "replicationGroupPrimaryEndPointPort")

    @property
    @jsii.member(jsii_name="replicationGroupReadEndPointAddresses")
    def replication_group_read_end_point_addresses(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReadEndPoint.Addresses
        """
        return jsii.get(self, "replicationGroupReadEndPointAddresses")

    @property
    @jsii.member(jsii_name="replicationGroupReadEndPointAddressesList")
    def replication_group_read_end_point_addresses_list(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReadEndPoint.Addresses.List
        """
        return jsii.get(self, "replicationGroupReadEndPointAddressesList")

    @property
    @jsii.member(jsii_name="replicationGroupReadEndPointPorts")
    def replication_group_read_end_point_ports(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReadEndPoint.Ports
        """
        return jsii.get(self, "replicationGroupReadEndPointPorts")

    @property
    @jsii.member(jsii_name="replicationGroupReadEndPointPortsList")
    def replication_group_read_end_point_ports_list(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReadEndPoint.Ports.List
        """
        return jsii.get(self, "replicationGroupReadEndPointPortsList")

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

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticache.CfnReplicationGroup.NodeGroupConfigurationProperty", jsii_struct_bases=[])
    class NodeGroupConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-replicationgroup-nodegroupconfiguration.html
        Stability:
            experimental
        """
        nodeGroupId: str
        """``CfnReplicationGroup.NodeGroupConfigurationProperty.NodeGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-replicationgroup-nodegroupconfiguration.html#cfn-elasticache-replicationgroup-nodegroupconfiguration-nodegroupid
        Stability:
            experimental
        """

        primaryAvailabilityZone: str
        """``CfnReplicationGroup.NodeGroupConfigurationProperty.PrimaryAvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-replicationgroup-nodegroupconfiguration.html#cfn-elasticache-replicationgroup-nodegroupconfiguration-primaryavailabilityzone
        Stability:
            experimental
        """

        replicaAvailabilityZones: typing.List[str]
        """``CfnReplicationGroup.NodeGroupConfigurationProperty.ReplicaAvailabilityZones``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-replicationgroup-nodegroupconfiguration.html#cfn-elasticache-replicationgroup-nodegroupconfiguration-replicaavailabilityzones
        Stability:
            experimental
        """

        replicaCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnReplicationGroup.NodeGroupConfigurationProperty.ReplicaCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-replicationgroup-nodegroupconfiguration.html#cfn-elasticache-replicationgroup-nodegroupconfiguration-replicacount
        Stability:
            experimental
        """

        slots: str
        """``CfnReplicationGroup.NodeGroupConfigurationProperty.Slots``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-replicationgroup-nodegroupconfiguration.html#cfn-elasticache-replicationgroup-nodegroupconfiguration-slots
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnReplicationGroupProps(jsii.compat.TypedDict, total=False):
    atRestEncryptionEnabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::ReplicationGroup.AtRestEncryptionEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-atrestencryptionenabled
    Stability:
        experimental
    """
    authToken: str
    """``AWS::ElastiCache::ReplicationGroup.AuthToken``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-authtoken
    Stability:
        experimental
    """
    automaticFailoverEnabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::ReplicationGroup.AutomaticFailoverEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-automaticfailoverenabled
    Stability:
        experimental
    """
    autoMinorVersionUpgrade: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::ReplicationGroup.AutoMinorVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-autominorversionupgrade
    Stability:
        experimental
    """
    cacheNodeType: str
    """``AWS::ElastiCache::ReplicationGroup.CacheNodeType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-cachenodetype
    Stability:
        experimental
    """
    cacheParameterGroupName: str
    """``AWS::ElastiCache::ReplicationGroup.CacheParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-cacheparametergroupname
    Stability:
        experimental
    """
    cacheSecurityGroupNames: typing.List[str]
    """``AWS::ElastiCache::ReplicationGroup.CacheSecurityGroupNames``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-cachesecuritygroupnames
    Stability:
        experimental
    """
    cacheSubnetGroupName: str
    """``AWS::ElastiCache::ReplicationGroup.CacheSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-cachesubnetgroupname
    Stability:
        experimental
    """
    engine: str
    """``AWS::ElastiCache::ReplicationGroup.Engine``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-engine
    Stability:
        experimental
    """
    engineVersion: str
    """``AWS::ElastiCache::ReplicationGroup.EngineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-engineversion
    Stability:
        experimental
    """
    nodeGroupConfiguration: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnReplicationGroup.NodeGroupConfigurationProperty"]]]
    """``AWS::ElastiCache::ReplicationGroup.NodeGroupConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-nodegroupconfiguration
    Stability:
        experimental
    """
    notificationTopicArn: str
    """``AWS::ElastiCache::ReplicationGroup.NotificationTopicArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-notificationtopicarn
    Stability:
        experimental
    """
    numCacheClusters: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::ReplicationGroup.NumCacheClusters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-numcacheclusters
    Stability:
        experimental
    """
    numNodeGroups: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::ReplicationGroup.NumNodeGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-numnodegroups
    Stability:
        experimental
    """
    port: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::ReplicationGroup.Port``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-port
    Stability:
        experimental
    """
    preferredCacheClusterAZs: typing.List[str]
    """``AWS::ElastiCache::ReplicationGroup.PreferredCacheClusterAZs``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-preferredcacheclusterazs
    Stability:
        experimental
    """
    preferredMaintenanceWindow: str
    """``AWS::ElastiCache::ReplicationGroup.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-preferredmaintenancewindow
    Stability:
        experimental
    """
    primaryClusterId: str
    """``AWS::ElastiCache::ReplicationGroup.PrimaryClusterId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-primaryclusterid
    Stability:
        experimental
    """
    replicasPerNodeGroup: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::ReplicationGroup.ReplicasPerNodeGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-replicaspernodegroup
    Stability:
        experimental
    """
    replicationGroupId: str
    """``AWS::ElastiCache::ReplicationGroup.ReplicationGroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-replicationgroupid
    Stability:
        experimental
    """
    securityGroupIds: typing.List[str]
    """``AWS::ElastiCache::ReplicationGroup.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-securitygroupids
    Stability:
        experimental
    """
    snapshotArns: typing.List[str]
    """``AWS::ElastiCache::ReplicationGroup.SnapshotArns``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-snapshotarns
    Stability:
        experimental
    """
    snapshotName: str
    """``AWS::ElastiCache::ReplicationGroup.SnapshotName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-snapshotname
    Stability:
        experimental
    """
    snapshotRetentionLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::ReplicationGroup.SnapshotRetentionLimit``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-snapshotretentionlimit
    Stability:
        experimental
    """
    snapshottingClusterId: str
    """``AWS::ElastiCache::ReplicationGroup.SnapshottingClusterId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-snapshottingclusterid
    Stability:
        experimental
    """
    snapshotWindow: str
    """``AWS::ElastiCache::ReplicationGroup.SnapshotWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-snapshotwindow
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::ElastiCache::ReplicationGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-tags
    Stability:
        experimental
    """
    transitEncryptionEnabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::ElastiCache::ReplicationGroup.TransitEncryptionEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-transitencryptionenabled
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticache.CfnReplicationGroupProps", jsii_struct_bases=[_CfnReplicationGroupProps])
class CfnReplicationGroupProps(_CfnReplicationGroupProps):
    """Properties for defining a ``AWS::ElastiCache::ReplicationGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html
    Stability:
        experimental
    """
    replicationGroupDescription: str
    """``AWS::ElastiCache::ReplicationGroup.ReplicationGroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-replicationgroupdescription
    Stability:
        experimental
    """

class CfnSecurityGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticache.CfnSecurityGroup"):
    """A CloudFormation ``AWS::ElastiCache::SecurityGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-security-group.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ElastiCache::SecurityGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: str) -> None:
        """Create a new ``AWS::ElastiCache::SecurityGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::ElastiCache::SecurityGroup.Description``.

        Stability:
            experimental
        """
        props: CfnSecurityGroupProps = {"description": description}

        jsii.create(CfnSecurityGroup, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSecurityGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="securityGroupName")
    def security_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupName")


class CfnSecurityGroupIngress(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticache.CfnSecurityGroupIngress"):
    """A CloudFormation ``AWS::ElastiCache::SecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-security-group-ingress.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ElastiCache::SecurityGroupIngress
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cache_security_group_name: str, ec2_security_group_name: str, ec2_security_group_owner_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ElastiCache::SecurityGroupIngress``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            cacheSecurityGroupName: ``AWS::ElastiCache::SecurityGroupIngress.CacheSecurityGroupName``.
            ec2SecurityGroupName: ``AWS::ElastiCache::SecurityGroupIngress.EC2SecurityGroupName``.
            ec2SecurityGroupOwnerId: ``AWS::ElastiCache::SecurityGroupIngress.EC2SecurityGroupOwnerId``.

        Stability:
            experimental
        """
        props: CfnSecurityGroupIngressProps = {"cacheSecurityGroupName": cache_security_group_name, "ec2SecurityGroupName": ec2_security_group_name}

        if ec2_security_group_owner_id is not None:
            props["ec2SecurityGroupOwnerId"] = ec2_security_group_owner_id

        jsii.create(CfnSecurityGroupIngress, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSecurityGroupIngressProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="securityGroupIngressId")
    def security_group_ingress_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupIngressId")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSecurityGroupIngressProps(jsii.compat.TypedDict, total=False):
    ec2SecurityGroupOwnerId: str
    """``AWS::ElastiCache::SecurityGroupIngress.EC2SecurityGroupOwnerId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-security-group-ingress.html#cfn-elasticache-securitygroupingress-ec2securitygroupownerid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticache.CfnSecurityGroupIngressProps", jsii_struct_bases=[_CfnSecurityGroupIngressProps])
class CfnSecurityGroupIngressProps(_CfnSecurityGroupIngressProps):
    """Properties for defining a ``AWS::ElastiCache::SecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-security-group-ingress.html
    Stability:
        experimental
    """
    cacheSecurityGroupName: str
    """``AWS::ElastiCache::SecurityGroupIngress.CacheSecurityGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-security-group-ingress.html#cfn-elasticache-securitygroupingress-cachesecuritygroupname
    Stability:
        experimental
    """

    ec2SecurityGroupName: str
    """``AWS::ElastiCache::SecurityGroupIngress.EC2SecurityGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-security-group-ingress.html#cfn-elasticache-securitygroupingress-ec2securitygroupname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticache.CfnSecurityGroupProps", jsii_struct_bases=[])
class CfnSecurityGroupProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::ElastiCache::SecurityGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-security-group.html
    Stability:
        experimental
    """
    description: str
    """``AWS::ElastiCache::SecurityGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-security-group.html#cfn-elasticache-securitygroup-description
    Stability:
        experimental
    """

class CfnSubnetGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticache.CfnSubnetGroup"):
    """A CloudFormation ``AWS::ElastiCache::SubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-subnetgroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ElastiCache::SubnetGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: str, subnet_ids: typing.List[str], cache_subnet_group_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ElastiCache::SubnetGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::ElastiCache::SubnetGroup.Description``.
            subnetIds: ``AWS::ElastiCache::SubnetGroup.SubnetIds``.
            cacheSubnetGroupName: ``AWS::ElastiCache::SubnetGroup.CacheSubnetGroupName``.

        Stability:
            experimental
        """
        props: CfnSubnetGroupProps = {"description": description, "subnetIds": subnet_ids}

        if cache_subnet_group_name is not None:
            props["cacheSubnetGroupName"] = cache_subnet_group_name

        jsii.create(CfnSubnetGroup, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnSubnetGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="subnetGroupName")
    def subnet_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "subnetGroupName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSubnetGroupProps(jsii.compat.TypedDict, total=False):
    cacheSubnetGroupName: str
    """``AWS::ElastiCache::SubnetGroup.CacheSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-subnetgroup.html#cfn-elasticache-subnetgroup-cachesubnetgroupname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticache.CfnSubnetGroupProps", jsii_struct_bases=[_CfnSubnetGroupProps])
class CfnSubnetGroupProps(_CfnSubnetGroupProps):
    """Properties for defining a ``AWS::ElastiCache::SubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-subnetgroup.html
    Stability:
        experimental
    """
    description: str
    """``AWS::ElastiCache::SubnetGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-subnetgroup.html#cfn-elasticache-subnetgroup-description
    Stability:
        experimental
    """

    subnetIds: typing.List[str]
    """``AWS::ElastiCache::SubnetGroup.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-subnetgroup.html#cfn-elasticache-subnetgroup-subnetids
    Stability:
        experimental
    """

__all__ = ["CfnCacheCluster", "CfnCacheClusterProps", "CfnParameterGroup", "CfnParameterGroupProps", "CfnReplicationGroup", "CfnReplicationGroupProps", "CfnSecurityGroup", "CfnSecurityGroupIngress", "CfnSecurityGroupIngressProps", "CfnSecurityGroupProps", "CfnSubnetGroup", "CfnSubnetGroupProps", "__jsii_assembly__"]

publication.publish()
