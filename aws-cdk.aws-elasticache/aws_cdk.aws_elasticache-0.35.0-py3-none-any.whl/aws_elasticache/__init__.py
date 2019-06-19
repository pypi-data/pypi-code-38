import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-elasticache", "0.35.0", __name__, "aws-elasticache@0.35.0.jsii.tgz")
class CfnCacheCluster(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticache.CfnCacheCluster"):
    """A CloudFormation ``AWS::ElastiCache::CacheCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ElastiCache::CacheCluster
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cache_node_type: str, engine: str, num_cache_nodes: jsii.Number, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, az_mode: typing.Optional[str]=None, cache_parameter_group_name: typing.Optional[str]=None, cache_security_group_names: typing.Optional[typing.List[str]]=None, cache_subnet_group_name: typing.Optional[str]=None, cluster_name: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, notification_topic_arn: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, preferred_availability_zone: typing.Optional[str]=None, preferred_availability_zones: typing.Optional[typing.List[str]]=None, preferred_maintenance_window: typing.Optional[str]=None, snapshot_arns: typing.Optional[typing.List[str]]=None, snapshot_name: typing.Optional[str]=None, snapshot_retention_limit: typing.Optional[jsii.Number]=None, snapshot_window: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
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
    @jsii.member(jsii_name="attrConfigurationEndpointAddress")
    def attr_configuration_endpoint_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ConfigurationEndpoint.Address
        """
        return jsii.get(self, "attrConfigurationEndpointAddress")

    @property
    @jsii.member(jsii_name="attrConfigurationEndpointPort")
    def attr_configuration_endpoint_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ConfigurationEndpoint.Port
        """
        return jsii.get(self, "attrConfigurationEndpointPort")

    @property
    @jsii.member(jsii_name="attrRedisEndpointAddress")
    def attr_redis_endpoint_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RedisEndpoint.Address
        """
        return jsii.get(self, "attrRedisEndpointAddress")

    @property
    @jsii.member(jsii_name="attrRedisEndpointPort")
    def attr_redis_endpoint_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            RedisEndpoint.Port
        """
        return jsii.get(self, "attrRedisEndpointPort")

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
        """``AWS::ElastiCache::CacheCluster.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="cacheNodeType")
    def cache_node_type(self) -> str:
        """``AWS::ElastiCache::CacheCluster.CacheNodeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-cachenodetype
        Stability:
            experimental
        """
        return jsii.get(self, "cacheNodeType")

    @cache_node_type.setter
    def cache_node_type(self, value: str):
        return jsii.set(self, "cacheNodeType", value)

    @property
    @jsii.member(jsii_name="engine")
    def engine(self) -> str:
        """``AWS::ElastiCache::CacheCluster.Engine``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-engine
        Stability:
            experimental
        """
        return jsii.get(self, "engine")

    @engine.setter
    def engine(self, value: str):
        return jsii.set(self, "engine", value)

    @property
    @jsii.member(jsii_name="numCacheNodes")
    def num_cache_nodes(self) -> jsii.Number:
        """``AWS::ElastiCache::CacheCluster.NumCacheNodes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-numcachenodes
        Stability:
            experimental
        """
        return jsii.get(self, "numCacheNodes")

    @num_cache_nodes.setter
    def num_cache_nodes(self, value: jsii.Number):
        return jsii.set(self, "numCacheNodes", value)

    @property
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::ElastiCache::CacheCluster.AutoMinorVersionUpgrade``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-autominorversionupgrade
        Stability:
            experimental
        """
        return jsii.get(self, "autoMinorVersionUpgrade")

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "autoMinorVersionUpgrade", value)

    @property
    @jsii.member(jsii_name="azMode")
    def az_mode(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::CacheCluster.AZMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-azmode
        Stability:
            experimental
        """
        return jsii.get(self, "azMode")

    @az_mode.setter
    def az_mode(self, value: typing.Optional[str]):
        return jsii.set(self, "azMode", value)

    @property
    @jsii.member(jsii_name="cacheParameterGroupName")
    def cache_parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::CacheCluster.CacheParameterGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-cacheparametergroupname
        Stability:
            experimental
        """
        return jsii.get(self, "cacheParameterGroupName")

    @cache_parameter_group_name.setter
    def cache_parameter_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "cacheParameterGroupName", value)

    @property
    @jsii.member(jsii_name="cacheSecurityGroupNames")
    def cache_security_group_names(self) -> typing.Optional[typing.List[str]]:
        """``AWS::ElastiCache::CacheCluster.CacheSecurityGroupNames``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-cachesecuritygroupnames
        Stability:
            experimental
        """
        return jsii.get(self, "cacheSecurityGroupNames")

    @cache_security_group_names.setter
    def cache_security_group_names(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "cacheSecurityGroupNames", value)

    @property
    @jsii.member(jsii_name="cacheSubnetGroupName")
    def cache_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::CacheCluster.CacheSubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-cachesubnetgroupname
        Stability:
            experimental
        """
        return jsii.get(self, "cacheSubnetGroupName")

    @cache_subnet_group_name.setter
    def cache_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "cacheSubnetGroupName", value)

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::CacheCluster.ClusterName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-clustername
        Stability:
            experimental
        """
        return jsii.get(self, "clusterName")

    @cluster_name.setter
    def cluster_name(self, value: typing.Optional[str]):
        return jsii.set(self, "clusterName", value)

    @property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::CacheCluster.EngineVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-engineversion
        Stability:
            experimental
        """
        return jsii.get(self, "engineVersion")

    @engine_version.setter
    def engine_version(self, value: typing.Optional[str]):
        return jsii.set(self, "engineVersion", value)

    @property
    @jsii.member(jsii_name="notificationTopicArn")
    def notification_topic_arn(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::CacheCluster.NotificationTopicArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-notificationtopicarn
        Stability:
            experimental
        """
        return jsii.get(self, "notificationTopicArn")

    @notification_topic_arn.setter
    def notification_topic_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "notificationTopicArn", value)

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        """``AWS::ElastiCache::CacheCluster.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-port
        Stability:
            experimental
        """
        return jsii.get(self, "port")

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "port", value)

    @property
    @jsii.member(jsii_name="preferredAvailabilityZone")
    def preferred_availability_zone(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::CacheCluster.PreferredAvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-preferredavailabilityzone
        Stability:
            experimental
        """
        return jsii.get(self, "preferredAvailabilityZone")

    @preferred_availability_zone.setter
    def preferred_availability_zone(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredAvailabilityZone", value)

    @property
    @jsii.member(jsii_name="preferredAvailabilityZones")
    def preferred_availability_zones(self) -> typing.Optional[typing.List[str]]:
        """``AWS::ElastiCache::CacheCluster.PreferredAvailabilityZones``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-preferredavailabilityzones
        Stability:
            experimental
        """
        return jsii.get(self, "preferredAvailabilityZones")

    @preferred_availability_zones.setter
    def preferred_availability_zones(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "preferredAvailabilityZones", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::CacheCluster.PreferredMaintenanceWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-preferredmaintenancewindow
        Stability:
            experimental
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)

    @property
    @jsii.member(jsii_name="snapshotArns")
    def snapshot_arns(self) -> typing.Optional[typing.List[str]]:
        """``AWS::ElastiCache::CacheCluster.SnapshotArns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-snapshotarns
        Stability:
            experimental
        """
        return jsii.get(self, "snapshotArns")

    @snapshot_arns.setter
    def snapshot_arns(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "snapshotArns", value)

    @property
    @jsii.member(jsii_name="snapshotName")
    def snapshot_name(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::CacheCluster.SnapshotName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-snapshotname
        Stability:
            experimental
        """
        return jsii.get(self, "snapshotName")

    @snapshot_name.setter
    def snapshot_name(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotName", value)

    @property
    @jsii.member(jsii_name="snapshotRetentionLimit")
    def snapshot_retention_limit(self) -> typing.Optional[jsii.Number]:
        """``AWS::ElastiCache::CacheCluster.SnapshotRetentionLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-snapshotretentionlimit
        Stability:
            experimental
        """
        return jsii.get(self, "snapshotRetentionLimit")

    @snapshot_retention_limit.setter
    def snapshot_retention_limit(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "snapshotRetentionLimit", value)

    @property
    @jsii.member(jsii_name="snapshotWindow")
    def snapshot_window(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::CacheCluster.SnapshotWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-snapshotwindow
        Stability:
            experimental
        """
        return jsii.get(self, "snapshotWindow")

    @snapshot_window.setter
    def snapshot_window(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotWindow", value)

    @property
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::ElastiCache::CacheCluster.VpcSecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html#cfn-elasticache-cachecluster-vpcsecuritygroupids
        Stability:
            experimental
        """
        return jsii.get(self, "vpcSecurityGroupIds")

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "vpcSecurityGroupIds", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnCacheClusterProps(jsii.compat.TypedDict, total=False):
    autoMinorVersionUpgrade: typing.Union[bool, aws_cdk.cdk.IResolvable]
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
    port: jsii.Number
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
    snapshotRetentionLimit: jsii.Number
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

    numCacheNodes: jsii.Number
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cache_parameter_group_family: str, description: str, properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None) -> None:
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
    @jsii.member(jsii_name="cacheParameterGroupFamily")
    def cache_parameter_group_family(self) -> str:
        """``AWS::ElastiCache::ParameterGroup.CacheParameterGroupFamily``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-parameter-group.html#cfn-elasticache-parametergroup-cacheparametergroupfamily
        Stability:
            experimental
        """
        return jsii.get(self, "cacheParameterGroupFamily")

    @cache_parameter_group_family.setter
    def cache_parameter_group_family(self, value: str):
        return jsii.set(self, "cacheParameterGroupFamily", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::ElastiCache::ParameterGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-parameter-group.html#cfn-elasticache-parametergroup-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="properties")
    def properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
        """``AWS::ElastiCache::ParameterGroup.Properties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-parameter-group.html#cfn-elasticache-parametergroup-properties
        Stability:
            experimental
        """
        return jsii.get(self, "properties")

    @properties.setter
    def properties(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.Mapping[str,str]]]]):
        return jsii.set(self, "properties", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnParameterGroupProps(jsii.compat.TypedDict, total=False):
    properties: typing.Union[aws_cdk.cdk.IResolvable, typing.Mapping[str,str]]
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, replication_group_description: str, at_rest_encryption_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, auth_token: typing.Optional[str]=None, automatic_failover_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, cache_node_type: typing.Optional[str]=None, cache_parameter_group_name: typing.Optional[str]=None, cache_security_group_names: typing.Optional[typing.List[str]]=None, cache_subnet_group_name: typing.Optional[str]=None, engine: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, node_group_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "NodeGroupConfigurationProperty"]]]]]=None, notification_topic_arn: typing.Optional[str]=None, num_cache_clusters: typing.Optional[jsii.Number]=None, num_node_groups: typing.Optional[jsii.Number]=None, port: typing.Optional[jsii.Number]=None, preferred_cache_cluster_a_zs: typing.Optional[typing.List[str]]=None, preferred_maintenance_window: typing.Optional[str]=None, primary_cluster_id: typing.Optional[str]=None, replicas_per_node_group: typing.Optional[jsii.Number]=None, replication_group_id: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, snapshot_arns: typing.Optional[typing.List[str]]=None, snapshot_name: typing.Optional[str]=None, snapshot_retention_limit: typing.Optional[jsii.Number]=None, snapshotting_cluster_id: typing.Optional[str]=None, snapshot_window: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, transit_encryption_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None) -> None:
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
    @jsii.member(jsii_name="attrConfigurationEndPointAddress")
    def attr_configuration_end_point_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ConfigurationEndPoint.Address
        """
        return jsii.get(self, "attrConfigurationEndPointAddress")

    @property
    @jsii.member(jsii_name="attrConfigurationEndPointPort")
    def attr_configuration_end_point_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ConfigurationEndPoint.Port
        """
        return jsii.get(self, "attrConfigurationEndPointPort")

    @property
    @jsii.member(jsii_name="attrPrimaryEndPointAddress")
    def attr_primary_end_point_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            PrimaryEndPoint.Address
        """
        return jsii.get(self, "attrPrimaryEndPointAddress")

    @property
    @jsii.member(jsii_name="attrPrimaryEndPointPort")
    def attr_primary_end_point_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            PrimaryEndPoint.Port
        """
        return jsii.get(self, "attrPrimaryEndPointPort")

    @property
    @jsii.member(jsii_name="attrReadEndPointAddresses")
    def attr_read_end_point_addresses(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReadEndPoint.Addresses
        """
        return jsii.get(self, "attrReadEndPointAddresses")

    @property
    @jsii.member(jsii_name="attrReadEndPointAddressesList")
    def attr_read_end_point_addresses_list(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReadEndPoint.Addresses.List
        """
        return jsii.get(self, "attrReadEndPointAddressesList")

    @property
    @jsii.member(jsii_name="attrReadEndPointPorts")
    def attr_read_end_point_ports(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReadEndPoint.Ports
        """
        return jsii.get(self, "attrReadEndPointPorts")

    @property
    @jsii.member(jsii_name="attrReadEndPointPortsList")
    def attr_read_end_point_ports_list(self) -> typing.List[str]:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReadEndPoint.Ports.List
        """
        return jsii.get(self, "attrReadEndPointPortsList")

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
        """``AWS::ElastiCache::ReplicationGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="replicationGroupDescription")
    def replication_group_description(self) -> str:
        """``AWS::ElastiCache::ReplicationGroup.ReplicationGroupDescription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-replicationgroupdescription
        Stability:
            experimental
        """
        return jsii.get(self, "replicationGroupDescription")

    @replication_group_description.setter
    def replication_group_description(self, value: str):
        return jsii.set(self, "replicationGroupDescription", value)

    @property
    @jsii.member(jsii_name="atRestEncryptionEnabled")
    def at_rest_encryption_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::ElastiCache::ReplicationGroup.AtRestEncryptionEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-atrestencryptionenabled
        Stability:
            experimental
        """
        return jsii.get(self, "atRestEncryptionEnabled")

    @at_rest_encryption_enabled.setter
    def at_rest_encryption_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "atRestEncryptionEnabled", value)

    @property
    @jsii.member(jsii_name="authToken")
    def auth_token(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.AuthToken``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-authtoken
        Stability:
            experimental
        """
        return jsii.get(self, "authToken")

    @auth_token.setter
    def auth_token(self, value: typing.Optional[str]):
        return jsii.set(self, "authToken", value)

    @property
    @jsii.member(jsii_name="automaticFailoverEnabled")
    def automatic_failover_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::ElastiCache::ReplicationGroup.AutomaticFailoverEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-automaticfailoverenabled
        Stability:
            experimental
        """
        return jsii.get(self, "automaticFailoverEnabled")

    @automatic_failover_enabled.setter
    def automatic_failover_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "automaticFailoverEnabled", value)

    @property
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::ElastiCache::ReplicationGroup.AutoMinorVersionUpgrade``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-autominorversionupgrade
        Stability:
            experimental
        """
        return jsii.get(self, "autoMinorVersionUpgrade")

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "autoMinorVersionUpgrade", value)

    @property
    @jsii.member(jsii_name="cacheNodeType")
    def cache_node_type(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.CacheNodeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-cachenodetype
        Stability:
            experimental
        """
        return jsii.get(self, "cacheNodeType")

    @cache_node_type.setter
    def cache_node_type(self, value: typing.Optional[str]):
        return jsii.set(self, "cacheNodeType", value)

    @property
    @jsii.member(jsii_name="cacheParameterGroupName")
    def cache_parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.CacheParameterGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-cacheparametergroupname
        Stability:
            experimental
        """
        return jsii.get(self, "cacheParameterGroupName")

    @cache_parameter_group_name.setter
    def cache_parameter_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "cacheParameterGroupName", value)

    @property
    @jsii.member(jsii_name="cacheSecurityGroupNames")
    def cache_security_group_names(self) -> typing.Optional[typing.List[str]]:
        """``AWS::ElastiCache::ReplicationGroup.CacheSecurityGroupNames``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-cachesecuritygroupnames
        Stability:
            experimental
        """
        return jsii.get(self, "cacheSecurityGroupNames")

    @cache_security_group_names.setter
    def cache_security_group_names(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "cacheSecurityGroupNames", value)

    @property
    @jsii.member(jsii_name="cacheSubnetGroupName")
    def cache_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.CacheSubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-cachesubnetgroupname
        Stability:
            experimental
        """
        return jsii.get(self, "cacheSubnetGroupName")

    @cache_subnet_group_name.setter
    def cache_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "cacheSubnetGroupName", value)

    @property
    @jsii.member(jsii_name="engine")
    def engine(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.Engine``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-engine
        Stability:
            experimental
        """
        return jsii.get(self, "engine")

    @engine.setter
    def engine(self, value: typing.Optional[str]):
        return jsii.set(self, "engine", value)

    @property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.EngineVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-engineversion
        Stability:
            experimental
        """
        return jsii.get(self, "engineVersion")

    @engine_version.setter
    def engine_version(self, value: typing.Optional[str]):
        return jsii.set(self, "engineVersion", value)

    @property
    @jsii.member(jsii_name="nodeGroupConfiguration")
    def node_group_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "NodeGroupConfigurationProperty"]]]]]:
        """``AWS::ElastiCache::ReplicationGroup.NodeGroupConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-nodegroupconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "nodeGroupConfiguration")

    @node_group_configuration.setter
    def node_group_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "NodeGroupConfigurationProperty"]]]]]):
        return jsii.set(self, "nodeGroupConfiguration", value)

    @property
    @jsii.member(jsii_name="notificationTopicArn")
    def notification_topic_arn(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.NotificationTopicArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-notificationtopicarn
        Stability:
            experimental
        """
        return jsii.get(self, "notificationTopicArn")

    @notification_topic_arn.setter
    def notification_topic_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "notificationTopicArn", value)

    @property
    @jsii.member(jsii_name="numCacheClusters")
    def num_cache_clusters(self) -> typing.Optional[jsii.Number]:
        """``AWS::ElastiCache::ReplicationGroup.NumCacheClusters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-numcacheclusters
        Stability:
            experimental
        """
        return jsii.get(self, "numCacheClusters")

    @num_cache_clusters.setter
    def num_cache_clusters(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "numCacheClusters", value)

    @property
    @jsii.member(jsii_name="numNodeGroups")
    def num_node_groups(self) -> typing.Optional[jsii.Number]:
        """``AWS::ElastiCache::ReplicationGroup.NumNodeGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-numnodegroups
        Stability:
            experimental
        """
        return jsii.get(self, "numNodeGroups")

    @num_node_groups.setter
    def num_node_groups(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "numNodeGroups", value)

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        """``AWS::ElastiCache::ReplicationGroup.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-port
        Stability:
            experimental
        """
        return jsii.get(self, "port")

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "port", value)

    @property
    @jsii.member(jsii_name="preferredCacheClusterAZs")
    def preferred_cache_cluster_a_zs(self) -> typing.Optional[typing.List[str]]:
        """``AWS::ElastiCache::ReplicationGroup.PreferredCacheClusterAZs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-preferredcacheclusterazs
        Stability:
            experimental
        """
        return jsii.get(self, "preferredCacheClusterAZs")

    @preferred_cache_cluster_a_zs.setter
    def preferred_cache_cluster_a_zs(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "preferredCacheClusterAZs", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.PreferredMaintenanceWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-preferredmaintenancewindow
        Stability:
            experimental
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)

    @property
    @jsii.member(jsii_name="primaryClusterId")
    def primary_cluster_id(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.PrimaryClusterId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-primaryclusterid
        Stability:
            experimental
        """
        return jsii.get(self, "primaryClusterId")

    @primary_cluster_id.setter
    def primary_cluster_id(self, value: typing.Optional[str]):
        return jsii.set(self, "primaryClusterId", value)

    @property
    @jsii.member(jsii_name="replicasPerNodeGroup")
    def replicas_per_node_group(self) -> typing.Optional[jsii.Number]:
        """``AWS::ElastiCache::ReplicationGroup.ReplicasPerNodeGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-replicaspernodegroup
        Stability:
            experimental
        """
        return jsii.get(self, "replicasPerNodeGroup")

    @replicas_per_node_group.setter
    def replicas_per_node_group(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "replicasPerNodeGroup", value)

    @property
    @jsii.member(jsii_name="replicationGroupId")
    def replication_group_id(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.ReplicationGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-replicationgroupid
        Stability:
            experimental
        """
        return jsii.get(self, "replicationGroupId")

    @replication_group_id.setter
    def replication_group_id(self, value: typing.Optional[str]):
        return jsii.set(self, "replicationGroupId", value)

    @property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::ElastiCache::ReplicationGroup.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-securitygroupids
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupIds")

    @security_group_ids.setter
    def security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "securityGroupIds", value)

    @property
    @jsii.member(jsii_name="snapshotArns")
    def snapshot_arns(self) -> typing.Optional[typing.List[str]]:
        """``AWS::ElastiCache::ReplicationGroup.SnapshotArns``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-snapshotarns
        Stability:
            experimental
        """
        return jsii.get(self, "snapshotArns")

    @snapshot_arns.setter
    def snapshot_arns(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "snapshotArns", value)

    @property
    @jsii.member(jsii_name="snapshotName")
    def snapshot_name(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.SnapshotName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-snapshotname
        Stability:
            experimental
        """
        return jsii.get(self, "snapshotName")

    @snapshot_name.setter
    def snapshot_name(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotName", value)

    @property
    @jsii.member(jsii_name="snapshotRetentionLimit")
    def snapshot_retention_limit(self) -> typing.Optional[jsii.Number]:
        """``AWS::ElastiCache::ReplicationGroup.SnapshotRetentionLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-snapshotretentionlimit
        Stability:
            experimental
        """
        return jsii.get(self, "snapshotRetentionLimit")

    @snapshot_retention_limit.setter
    def snapshot_retention_limit(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "snapshotRetentionLimit", value)

    @property
    @jsii.member(jsii_name="snapshottingClusterId")
    def snapshotting_cluster_id(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.SnapshottingClusterId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-snapshottingclusterid
        Stability:
            experimental
        """
        return jsii.get(self, "snapshottingClusterId")

    @snapshotting_cluster_id.setter
    def snapshotting_cluster_id(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshottingClusterId", value)

    @property
    @jsii.member(jsii_name="snapshotWindow")
    def snapshot_window(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::ReplicationGroup.SnapshotWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-snapshotwindow
        Stability:
            experimental
        """
        return jsii.get(self, "snapshotWindow")

    @snapshot_window.setter
    def snapshot_window(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotWindow", value)

    @property
    @jsii.member(jsii_name="transitEncryptionEnabled")
    def transit_encryption_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::ElastiCache::ReplicationGroup.TransitEncryptionEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-transitencryptionenabled
        Stability:
            experimental
        """
        return jsii.get(self, "transitEncryptionEnabled")

    @transit_encryption_enabled.setter
    def transit_encryption_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "transitEncryptionEnabled", value)

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

        replicaCount: jsii.Number
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
    atRestEncryptionEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
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
    automaticFailoverEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::ElastiCache::ReplicationGroup.AutomaticFailoverEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-automaticfailoverenabled
    Stability:
        experimental
    """
    autoMinorVersionUpgrade: typing.Union[bool, aws_cdk.cdk.IResolvable]
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
    nodeGroupConfiguration: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnReplicationGroup.NodeGroupConfigurationProperty"]]]
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
    numCacheClusters: jsii.Number
    """``AWS::ElastiCache::ReplicationGroup.NumCacheClusters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-numcacheclusters
    Stability:
        experimental
    """
    numNodeGroups: jsii.Number
    """``AWS::ElastiCache::ReplicationGroup.NumNodeGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-numnodegroups
    Stability:
        experimental
    """
    port: jsii.Number
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
    replicasPerNodeGroup: jsii.Number
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
    snapshotRetentionLimit: jsii.Number
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
    transitEncryptionEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
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
    def description(self) -> str:
        """``AWS::ElastiCache::SecurityGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-security-group.html#cfn-elasticache-securitygroup-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)


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
    @jsii.member(jsii_name="cacheSecurityGroupName")
    def cache_security_group_name(self) -> str:
        """``AWS::ElastiCache::SecurityGroupIngress.CacheSecurityGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-security-group-ingress.html#cfn-elasticache-securitygroupingress-cachesecuritygroupname
        Stability:
            experimental
        """
        return jsii.get(self, "cacheSecurityGroupName")

    @cache_security_group_name.setter
    def cache_security_group_name(self, value: str):
        return jsii.set(self, "cacheSecurityGroupName", value)

    @property
    @jsii.member(jsii_name="ec2SecurityGroupName")
    def ec2_security_group_name(self) -> str:
        """``AWS::ElastiCache::SecurityGroupIngress.EC2SecurityGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-security-group-ingress.html#cfn-elasticache-securitygroupingress-ec2securitygroupname
        Stability:
            experimental
        """
        return jsii.get(self, "ec2SecurityGroupName")

    @ec2_security_group_name.setter
    def ec2_security_group_name(self, value: str):
        return jsii.set(self, "ec2SecurityGroupName", value)

    @property
    @jsii.member(jsii_name="ec2SecurityGroupOwnerId")
    def ec2_security_group_owner_id(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::SecurityGroupIngress.EC2SecurityGroupOwnerId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-security-group-ingress.html#cfn-elasticache-securitygroupingress-ec2securitygroupownerid
        Stability:
            experimental
        """
        return jsii.get(self, "ec2SecurityGroupOwnerId")

    @ec2_security_group_owner_id.setter
    def ec2_security_group_owner_id(self, value: typing.Optional[str]):
        return jsii.set(self, "ec2SecurityGroupOwnerId", value)


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
    def description(self) -> str:
        """``AWS::ElastiCache::SubnetGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-subnetgroup.html#cfn-elasticache-subnetgroup-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::ElastiCache::SubnetGroup.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-subnetgroup.html#cfn-elasticache-subnetgroup-subnetids
        Stability:
            experimental
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[str]):
        return jsii.set(self, "subnetIds", value)

    @property
    @jsii.member(jsii_name="cacheSubnetGroupName")
    def cache_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::ElastiCache::SubnetGroup.CacheSubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-subnetgroup.html#cfn-elasticache-subnetgroup-cachesubnetgroupname
        Stability:
            experimental
        """
        return jsii.get(self, "cacheSubnetGroupName")

    @cache_subnet_group_name.setter
    def cache_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "cacheSubnetGroupName", value)


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
