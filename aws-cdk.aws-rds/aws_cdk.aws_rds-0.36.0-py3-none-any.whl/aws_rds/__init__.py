import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_cloudwatch
import aws_cdk.aws_ec2
import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_logs
import aws_cdk.aws_sam
import aws_cdk.aws_secretsmanager
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-rds", "0.36.0", __name__, "aws-rds@0.36.0.jsii.tgz")
@jsii.data_type_optionals(jsii_struct_bases=[])
class _BackupProps(jsii.compat.TypedDict, total=False):
    preferredWindow: str
    """A daily time range in 24-hours UTC format in which backups preferably execute.

    Must be at least 30 minutes long.

    Example: '01:00-02:00'

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.BackupProps", jsii_struct_bases=[_BackupProps])
class BackupProps(_BackupProps):
    """Backup configuration for RDS databases.

    Default:
        - The retention period for automated backups is 1 day.
          The preferred backup window will be a 30-minute window selected at random
          from an 8-hour block of time for each AWS Region.

    See:
        https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow.Aurora
    Stability:
        experimental
    """
    retention: aws_cdk.core.Duration
    """How many days to retain the backup.

    Stability:
        experimental
    """

class CfnDBCluster(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBCluster"):
    """A CloudFormation ``AWS::RDS::DBCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html
    Stability:
        stable
    cloudformationResource:
        AWS::RDS::DBCluster
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, engine: str, availability_zones: typing.Optional[typing.List[str]]=None, backtrack_window: typing.Optional[jsii.Number]=None, backup_retention_period: typing.Optional[jsii.Number]=None, database_name: typing.Optional[str]=None, db_cluster_identifier: typing.Optional[str]=None, db_cluster_parameter_group_name: typing.Optional[str]=None, db_subnet_group_name: typing.Optional[str]=None, deletion_protection: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, enable_cloudwatch_logs_exports: typing.Optional[typing.List[str]]=None, enable_iam_database_authentication: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, engine_mode: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, master_username: typing.Optional[str]=None, master_user_password: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, replication_source_identifier: typing.Optional[str]=None, scaling_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ScalingConfigurationProperty"]]]=None, snapshot_identifier: typing.Optional[str]=None, source_region: typing.Optional[str]=None, storage_encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::RDS::DBCluster``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            engine: ``AWS::RDS::DBCluster.Engine``.
            availability_zones: ``AWS::RDS::DBCluster.AvailabilityZones``.
            backtrack_window: ``AWS::RDS::DBCluster.BacktrackWindow``.
            backup_retention_period: ``AWS::RDS::DBCluster.BackupRetentionPeriod``.
            database_name: ``AWS::RDS::DBCluster.DatabaseName``.
            db_cluster_identifier: ``AWS::RDS::DBCluster.DBClusterIdentifier``.
            db_cluster_parameter_group_name: ``AWS::RDS::DBCluster.DBClusterParameterGroupName``.
            db_subnet_group_name: ``AWS::RDS::DBCluster.DBSubnetGroupName``.
            deletion_protection: ``AWS::RDS::DBCluster.DeletionProtection``.
            enable_cloudwatch_logs_exports: ``AWS::RDS::DBCluster.EnableCloudwatchLogsExports``.
            enable_iam_database_authentication: ``AWS::RDS::DBCluster.EnableIAMDatabaseAuthentication``.
            engine_mode: ``AWS::RDS::DBCluster.EngineMode``.
            engine_version: ``AWS::RDS::DBCluster.EngineVersion``.
            kms_key_id: ``AWS::RDS::DBCluster.KmsKeyId``.
            master_username: ``AWS::RDS::DBCluster.MasterUsername``.
            master_user_password: ``AWS::RDS::DBCluster.MasterUserPassword``.
            port: ``AWS::RDS::DBCluster.Port``.
            preferred_backup_window: ``AWS::RDS::DBCluster.PreferredBackupWindow``.
            preferred_maintenance_window: ``AWS::RDS::DBCluster.PreferredMaintenanceWindow``.
            replication_source_identifier: ``AWS::RDS::DBCluster.ReplicationSourceIdentifier``.
            scaling_configuration: ``AWS::RDS::DBCluster.ScalingConfiguration``.
            snapshot_identifier: ``AWS::RDS::DBCluster.SnapshotIdentifier``.
            source_region: ``AWS::RDS::DBCluster.SourceRegion``.
            storage_encrypted: ``AWS::RDS::DBCluster.StorageEncrypted``.
            tags: ``AWS::RDS::DBCluster.Tags``.
            vpc_security_group_ids: ``AWS::RDS::DBCluster.VpcSecurityGroupIds``.

        Stability:
            experimental
        """
        props: CfnDBClusterProps = {"engine": engine}

        if availability_zones is not None:
            props["availabilityZones"] = availability_zones

        if backtrack_window is not None:
            props["backtrackWindow"] = backtrack_window

        if backup_retention_period is not None:
            props["backupRetentionPeriod"] = backup_retention_period

        if database_name is not None:
            props["databaseName"] = database_name

        if db_cluster_identifier is not None:
            props["dbClusterIdentifier"] = db_cluster_identifier

        if db_cluster_parameter_group_name is not None:
            props["dbClusterParameterGroupName"] = db_cluster_parameter_group_name

        if db_subnet_group_name is not None:
            props["dbSubnetGroupName"] = db_subnet_group_name

        if deletion_protection is not None:
            props["deletionProtection"] = deletion_protection

        if enable_cloudwatch_logs_exports is not None:
            props["enableCloudwatchLogsExports"] = enable_cloudwatch_logs_exports

        if enable_iam_database_authentication is not None:
            props["enableIamDatabaseAuthentication"] = enable_iam_database_authentication

        if engine_mode is not None:
            props["engineMode"] = engine_mode

        if engine_version is not None:
            props["engineVersion"] = engine_version

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

        if master_username is not None:
            props["masterUsername"] = master_username

        if master_user_password is not None:
            props["masterUserPassword"] = master_user_password

        if port is not None:
            props["port"] = port

        if preferred_backup_window is not None:
            props["preferredBackupWindow"] = preferred_backup_window

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if replication_source_identifier is not None:
            props["replicationSourceIdentifier"] = replication_source_identifier

        if scaling_configuration is not None:
            props["scalingConfiguration"] = scaling_configuration

        if snapshot_identifier is not None:
            props["snapshotIdentifier"] = snapshot_identifier

        if source_region is not None:
            props["sourceRegion"] = source_region

        if storage_encrypted is not None:
            props["storageEncrypted"] = storage_encrypted

        if tags is not None:
            props["tags"] = tags

        if vpc_security_group_ids is not None:
            props["vpcSecurityGroupIds"] = vpc_security_group_ids

        jsii.create(CfnDBCluster, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrEndpointAddress")
    def attr_endpoint_address(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Endpoint.Address
        """
        return jsii.get(self, "attrEndpointAddress")

    @property
    @jsii.member(jsii_name="attrEndpointPort")
    def attr_endpoint_port(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Endpoint.Port
        """
        return jsii.get(self, "attrEndpointPort")

    @property
    @jsii.member(jsii_name="attrReadEndpointAddress")
    def attr_read_endpoint_address(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            ReadEndpoint.Address
        """
        return jsii.get(self, "attrReadEndpointAddress")

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
        """``AWS::RDS::DBCluster.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="engine")
    def engine(self) -> str:
        """``AWS::RDS::DBCluster.Engine``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-engine
        Stability:
            stable
        """
        return jsii.get(self, "engine")

    @engine.setter
    def engine(self, value: str):
        return jsii.set(self, "engine", value)

    @property
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RDS::DBCluster.AvailabilityZones``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-availabilityzones
        Stability:
            stable
        """
        return jsii.get(self, "availabilityZones")

    @availability_zones.setter
    def availability_zones(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "availabilityZones", value)

    @property
    @jsii.member(jsii_name="backtrackWindow")
    def backtrack_window(self) -> typing.Optional[jsii.Number]:
        """``AWS::RDS::DBCluster.BacktrackWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-backtrackwindow
        Stability:
            stable
        """
        return jsii.get(self, "backtrackWindow")

    @backtrack_window.setter
    def backtrack_window(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "backtrackWindow", value)

    @property
    @jsii.member(jsii_name="backupRetentionPeriod")
    def backup_retention_period(self) -> typing.Optional[jsii.Number]:
        """``AWS::RDS::DBCluster.BackupRetentionPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-backuprententionperiod
        Stability:
            stable
        """
        return jsii.get(self, "backupRetentionPeriod")

    @backup_retention_period.setter
    def backup_retention_period(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "backupRetentionPeriod", value)

    @property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.DatabaseName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-databasename
        Stability:
            stable
        """
        return jsii.get(self, "databaseName")

    @database_name.setter
    def database_name(self, value: typing.Optional[str]):
        return jsii.set(self, "databaseName", value)

    @property
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.DBClusterIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-dbclusteridentifier
        Stability:
            stable
        """
        return jsii.get(self, "dbClusterIdentifier")

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "dbClusterIdentifier", value)

    @property
    @jsii.member(jsii_name="dbClusterParameterGroupName")
    def db_cluster_parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.DBClusterParameterGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-dbclusterparametergroupname
        Stability:
            stable
        """
        return jsii.get(self, "dbClusterParameterGroupName")

    @db_cluster_parameter_group_name.setter
    def db_cluster_parameter_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbClusterParameterGroupName", value)

    @property
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.DBSubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-dbsubnetgroupname
        Stability:
            stable
        """
        return jsii.get(self, "dbSubnetGroupName")

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbSubnetGroupName", value)

    @property
    @jsii.member(jsii_name="deletionProtection")
    def deletion_protection(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBCluster.DeletionProtection``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-deletionprotection
        Stability:
            stable
        """
        return jsii.get(self, "deletionProtection")

    @deletion_protection.setter
    def deletion_protection(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "deletionProtection", value)

    @property
    @jsii.member(jsii_name="enableCloudwatchLogsExports")
    def enable_cloudwatch_logs_exports(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RDS::DBCluster.EnableCloudwatchLogsExports``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-enablecloudwatchlogsexports
        Stability:
            stable
        """
        return jsii.get(self, "enableCloudwatchLogsExports")

    @enable_cloudwatch_logs_exports.setter
    def enable_cloudwatch_logs_exports(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "enableCloudwatchLogsExports", value)

    @property
    @jsii.member(jsii_name="enableIamDatabaseAuthentication")
    def enable_iam_database_authentication(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBCluster.EnableIAMDatabaseAuthentication``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-enableiamdatabaseauthentication
        Stability:
            stable
        """
        return jsii.get(self, "enableIamDatabaseAuthentication")

    @enable_iam_database_authentication.setter
    def enable_iam_database_authentication(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enableIamDatabaseAuthentication", value)

    @property
    @jsii.member(jsii_name="engineMode")
    def engine_mode(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.EngineMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-enginemode
        Stability:
            stable
        """
        return jsii.get(self, "engineMode")

    @engine_mode.setter
    def engine_mode(self, value: typing.Optional[str]):
        return jsii.set(self, "engineMode", value)

    @property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.EngineVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-engineversion
        Stability:
            stable
        """
        return jsii.get(self, "engineVersion")

    @engine_version.setter
    def engine_version(self, value: typing.Optional[str]):
        return jsii.set(self, "engineVersion", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-kmskeyid
        Stability:
            stable
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="masterUsername")
    def master_username(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.MasterUsername``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-masterusername
        Stability:
            stable
        """
        return jsii.get(self, "masterUsername")

    @master_username.setter
    def master_username(self, value: typing.Optional[str]):
        return jsii.set(self, "masterUsername", value)

    @property
    @jsii.member(jsii_name="masterUserPassword")
    def master_user_password(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.MasterUserPassword``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-masteruserpassword
        Stability:
            stable
        """
        return jsii.get(self, "masterUserPassword")

    @master_user_password.setter
    def master_user_password(self, value: typing.Optional[str]):
        return jsii.set(self, "masterUserPassword", value)

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        """``AWS::RDS::DBCluster.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-port
        Stability:
            stable
        """
        return jsii.get(self, "port")

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "port", value)

    @property
    @jsii.member(jsii_name="preferredBackupWindow")
    def preferred_backup_window(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.PreferredBackupWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-preferredbackupwindow
        Stability:
            stable
        """
        return jsii.get(self, "preferredBackupWindow")

    @preferred_backup_window.setter
    def preferred_backup_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredBackupWindow", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.PreferredMaintenanceWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-preferredmaintenancewindow
        Stability:
            stable
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)

    @property
    @jsii.member(jsii_name="replicationSourceIdentifier")
    def replication_source_identifier(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.ReplicationSourceIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-replicationsourceidentifier
        Stability:
            stable
        """
        return jsii.get(self, "replicationSourceIdentifier")

    @replication_source_identifier.setter
    def replication_source_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "replicationSourceIdentifier", value)

    @property
    @jsii.member(jsii_name="scalingConfiguration")
    def scaling_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ScalingConfigurationProperty"]]]:
        """``AWS::RDS::DBCluster.ScalingConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-scalingconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "scalingConfiguration")

    @scaling_configuration.setter
    def scaling_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ScalingConfigurationProperty"]]]):
        return jsii.set(self, "scalingConfiguration", value)

    @property
    @jsii.member(jsii_name="snapshotIdentifier")
    def snapshot_identifier(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.SnapshotIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-snapshotidentifier
        Stability:
            stable
        """
        return jsii.get(self, "snapshotIdentifier")

    @snapshot_identifier.setter
    def snapshot_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotIdentifier", value)

    @property
    @jsii.member(jsii_name="sourceRegion")
    def source_region(self) -> typing.Optional[str]:
        """``AWS::RDS::DBCluster.SourceRegion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-sourceregion
        Stability:
            stable
        """
        return jsii.get(self, "sourceRegion")

    @source_region.setter
    def source_region(self, value: typing.Optional[str]):
        return jsii.set(self, "sourceRegion", value)

    @property
    @jsii.member(jsii_name="storageEncrypted")
    def storage_encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBCluster.StorageEncrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-storageencrypted
        Stability:
            stable
        """
        return jsii.get(self, "storageEncrypted")

    @storage_encrypted.setter
    def storage_encrypted(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "storageEncrypted", value)

    @property
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RDS::DBCluster.VpcSecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-vpcsecuritygroupids
        Stability:
            stable
        """
        return jsii.get(self, "vpcSecurityGroupIds")

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "vpcSecurityGroupIds", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBCluster.ScalingConfigurationProperty", jsii_struct_bases=[])
    class ScalingConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbcluster-scalingconfiguration.html
        Stability:
            stable
        """
        autoPause: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnDBCluster.ScalingConfigurationProperty.AutoPause``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbcluster-scalingconfiguration.html#cfn-rds-dbcluster-scalingconfiguration-autopause
        Stability:
            stable
        """

        maxCapacity: jsii.Number
        """``CfnDBCluster.ScalingConfigurationProperty.MaxCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbcluster-scalingconfiguration.html#cfn-rds-dbcluster-scalingconfiguration-maxcapacity
        Stability:
            stable
        """

        minCapacity: jsii.Number
        """``CfnDBCluster.ScalingConfigurationProperty.MinCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbcluster-scalingconfiguration.html#cfn-rds-dbcluster-scalingconfiguration-mincapacity
        Stability:
            stable
        """

        secondsUntilAutoPause: jsii.Number
        """``CfnDBCluster.ScalingConfigurationProperty.SecondsUntilAutoPause``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbcluster-scalingconfiguration.html#cfn-rds-dbcluster-scalingconfiguration-secondsuntilautopause
        Stability:
            stable
        """


class CfnDBClusterParameterGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBClusterParameterGroup"):
    """A CloudFormation ``AWS::RDS::DBClusterParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html
    Stability:
        stable
    cloudformationResource:
        AWS::RDS::DBClusterParameterGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, description: str, family: str, parameters: typing.Any, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::RDS::DBClusterParameterGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::RDS::DBClusterParameterGroup.Description``.
            family: ``AWS::RDS::DBClusterParameterGroup.Family``.
            parameters: ``AWS::RDS::DBClusterParameterGroup.Parameters``.
            tags: ``AWS::RDS::DBClusterParameterGroup.Tags``.

        Stability:
            experimental
        """
        props: CfnDBClusterParameterGroupProps = {"description": description, "family": family, "parameters": parameters}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnDBClusterParameterGroup, self, [scope, id, props])

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
        """``AWS::RDS::DBClusterParameterGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html#cfn-rds-dbclusterparametergroup-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::RDS::DBClusterParameterGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html#cfn-rds-dbclusterparametergroup-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="family")
    def family(self) -> str:
        """``AWS::RDS::DBClusterParameterGroup.Family``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html#cfn-rds-dbclusterparametergroup-family
        Stability:
            stable
        """
        return jsii.get(self, "family")

    @family.setter
    def family(self, value: str):
        return jsii.set(self, "family", value)

    @property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        """``AWS::RDS::DBClusterParameterGroup.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html#cfn-rds-dbclusterparametergroup-parameters
        Stability:
            stable
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Any):
        return jsii.set(self, "parameters", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBClusterParameterGroupProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::RDS::DBClusterParameterGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html#cfn-rds-dbclusterparametergroup-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBClusterParameterGroupProps", jsii_struct_bases=[_CfnDBClusterParameterGroupProps])
class CfnDBClusterParameterGroupProps(_CfnDBClusterParameterGroupProps):
    """Properties for defining a ``AWS::RDS::DBClusterParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html
    Stability:
        stable
    """
    description: str
    """``AWS::RDS::DBClusterParameterGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html#cfn-rds-dbclusterparametergroup-description
    Stability:
        stable
    """

    family: str
    """``AWS::RDS::DBClusterParameterGroup.Family``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html#cfn-rds-dbclusterparametergroup-family
    Stability:
        stable
    """

    parameters: typing.Any
    """``AWS::RDS::DBClusterParameterGroup.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html#cfn-rds-dbclusterparametergroup-parameters
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBClusterProps(jsii.compat.TypedDict, total=False):
    availabilityZones: typing.List[str]
    """``AWS::RDS::DBCluster.AvailabilityZones``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-availabilityzones
    Stability:
        stable
    """
    backtrackWindow: jsii.Number
    """``AWS::RDS::DBCluster.BacktrackWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-backtrackwindow
    Stability:
        stable
    """
    backupRetentionPeriod: jsii.Number
    """``AWS::RDS::DBCluster.BackupRetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-backuprententionperiod
    Stability:
        stable
    """
    databaseName: str
    """``AWS::RDS::DBCluster.DatabaseName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-databasename
    Stability:
        stable
    """
    dbClusterIdentifier: str
    """``AWS::RDS::DBCluster.DBClusterIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-dbclusteridentifier
    Stability:
        stable
    """
    dbClusterParameterGroupName: str
    """``AWS::RDS::DBCluster.DBClusterParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-dbclusterparametergroupname
    Stability:
        stable
    """
    dbSubnetGroupName: str
    """``AWS::RDS::DBCluster.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-dbsubnetgroupname
    Stability:
        stable
    """
    deletionProtection: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBCluster.DeletionProtection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-deletionprotection
    Stability:
        stable
    """
    enableCloudwatchLogsExports: typing.List[str]
    """``AWS::RDS::DBCluster.EnableCloudwatchLogsExports``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-enablecloudwatchlogsexports
    Stability:
        stable
    """
    enableIamDatabaseAuthentication: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBCluster.EnableIAMDatabaseAuthentication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-enableiamdatabaseauthentication
    Stability:
        stable
    """
    engineMode: str
    """``AWS::RDS::DBCluster.EngineMode``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-enginemode
    Stability:
        stable
    """
    engineVersion: str
    """``AWS::RDS::DBCluster.EngineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-engineversion
    Stability:
        stable
    """
    kmsKeyId: str
    """``AWS::RDS::DBCluster.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-kmskeyid
    Stability:
        stable
    """
    masterUsername: str
    """``AWS::RDS::DBCluster.MasterUsername``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-masterusername
    Stability:
        stable
    """
    masterUserPassword: str
    """``AWS::RDS::DBCluster.MasterUserPassword``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-masteruserpassword
    Stability:
        stable
    """
    port: jsii.Number
    """``AWS::RDS::DBCluster.Port``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-port
    Stability:
        stable
    """
    preferredBackupWindow: str
    """``AWS::RDS::DBCluster.PreferredBackupWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-preferredbackupwindow
    Stability:
        stable
    """
    preferredMaintenanceWindow: str
    """``AWS::RDS::DBCluster.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-preferredmaintenancewindow
    Stability:
        stable
    """
    replicationSourceIdentifier: str
    """``AWS::RDS::DBCluster.ReplicationSourceIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-replicationsourceidentifier
    Stability:
        stable
    """
    scalingConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnDBCluster.ScalingConfigurationProperty"]
    """``AWS::RDS::DBCluster.ScalingConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-scalingconfiguration
    Stability:
        stable
    """
    snapshotIdentifier: str
    """``AWS::RDS::DBCluster.SnapshotIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-snapshotidentifier
    Stability:
        stable
    """
    sourceRegion: str
    """``AWS::RDS::DBCluster.SourceRegion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-sourceregion
    Stability:
        stable
    """
    storageEncrypted: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBCluster.StorageEncrypted``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-storageencrypted
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::RDS::DBCluster.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-tags
    Stability:
        stable
    """
    vpcSecurityGroupIds: typing.List[str]
    """``AWS::RDS::DBCluster.VpcSecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-vpcsecuritygroupids
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBClusterProps", jsii_struct_bases=[_CfnDBClusterProps])
class CfnDBClusterProps(_CfnDBClusterProps):
    """Properties for defining a ``AWS::RDS::DBCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html
    Stability:
        stable
    """
    engine: str
    """``AWS::RDS::DBCluster.Engine``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-engine
    Stability:
        stable
    """

class CfnDBInstance(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBInstance"):
    """A CloudFormation ``AWS::RDS::DBInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html
    Stability:
        stable
    cloudformationResource:
        AWS::RDS::DBInstance
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, db_instance_class: str, allocated_storage: typing.Optional[str]=None, allow_major_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, availability_zone: typing.Optional[str]=None, backup_retention_period: typing.Optional[jsii.Number]=None, character_set_name: typing.Optional[str]=None, copy_tags_to_snapshot: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, db_cluster_identifier: typing.Optional[str]=None, db_instance_identifier: typing.Optional[str]=None, db_name: typing.Optional[str]=None, db_parameter_group_name: typing.Optional[str]=None, db_security_groups: typing.Optional[typing.List[str]]=None, db_snapshot_identifier: typing.Optional[str]=None, db_subnet_group_name: typing.Optional[str]=None, delete_automated_backups: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, deletion_protection: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, domain: typing.Optional[str]=None, domain_iam_role_name: typing.Optional[str]=None, enable_cloudwatch_logs_exports: typing.Optional[typing.List[str]]=None, enable_iam_database_authentication: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, enable_performance_insights: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, engine: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, iops: typing.Optional[jsii.Number]=None, kms_key_id: typing.Optional[str]=None, license_model: typing.Optional[str]=None, master_username: typing.Optional[str]=None, master_user_password: typing.Optional[str]=None, monitoring_interval: typing.Optional[jsii.Number]=None, monitoring_role_arn: typing.Optional[str]=None, multi_az: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, option_group_name: typing.Optional[str]=None, performance_insights_kms_key_id: typing.Optional[str]=None, performance_insights_retention_period: typing.Optional[jsii.Number]=None, port: typing.Optional[str]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, processor_features: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ProcessorFeatureProperty"]]]]]=None, promotion_tier: typing.Optional[jsii.Number]=None, publicly_accessible: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, source_db_instance_identifier: typing.Optional[str]=None, source_region: typing.Optional[str]=None, storage_encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, storage_type: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, timezone: typing.Optional[str]=None, use_default_processor_features: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, vpc_security_groups: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::RDS::DBInstance``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            db_instance_class: ``AWS::RDS::DBInstance.DBInstanceClass``.
            allocated_storage: ``AWS::RDS::DBInstance.AllocatedStorage``.
            allow_major_version_upgrade: ``AWS::RDS::DBInstance.AllowMajorVersionUpgrade``.
            auto_minor_version_upgrade: ``AWS::RDS::DBInstance.AutoMinorVersionUpgrade``.
            availability_zone: ``AWS::RDS::DBInstance.AvailabilityZone``.
            backup_retention_period: ``AWS::RDS::DBInstance.BackupRetentionPeriod``.
            character_set_name: ``AWS::RDS::DBInstance.CharacterSetName``.
            copy_tags_to_snapshot: ``AWS::RDS::DBInstance.CopyTagsToSnapshot``.
            db_cluster_identifier: ``AWS::RDS::DBInstance.DBClusterIdentifier``.
            db_instance_identifier: ``AWS::RDS::DBInstance.DBInstanceIdentifier``.
            db_name: ``AWS::RDS::DBInstance.DBName``.
            db_parameter_group_name: ``AWS::RDS::DBInstance.DBParameterGroupName``.
            db_security_groups: ``AWS::RDS::DBInstance.DBSecurityGroups``.
            db_snapshot_identifier: ``AWS::RDS::DBInstance.DBSnapshotIdentifier``.
            db_subnet_group_name: ``AWS::RDS::DBInstance.DBSubnetGroupName``.
            delete_automated_backups: ``AWS::RDS::DBInstance.DeleteAutomatedBackups``.
            deletion_protection: ``AWS::RDS::DBInstance.DeletionProtection``.
            domain: ``AWS::RDS::DBInstance.Domain``.
            domain_iam_role_name: ``AWS::RDS::DBInstance.DomainIAMRoleName``.
            enable_cloudwatch_logs_exports: ``AWS::RDS::DBInstance.EnableCloudwatchLogsExports``.
            enable_iam_database_authentication: ``AWS::RDS::DBInstance.EnableIAMDatabaseAuthentication``.
            enable_performance_insights: ``AWS::RDS::DBInstance.EnablePerformanceInsights``.
            engine: ``AWS::RDS::DBInstance.Engine``.
            engine_version: ``AWS::RDS::DBInstance.EngineVersion``.
            iops: ``AWS::RDS::DBInstance.Iops``.
            kms_key_id: ``AWS::RDS::DBInstance.KmsKeyId``.
            license_model: ``AWS::RDS::DBInstance.LicenseModel``.
            master_username: ``AWS::RDS::DBInstance.MasterUsername``.
            master_user_password: ``AWS::RDS::DBInstance.MasterUserPassword``.
            monitoring_interval: ``AWS::RDS::DBInstance.MonitoringInterval``.
            monitoring_role_arn: ``AWS::RDS::DBInstance.MonitoringRoleArn``.
            multi_az: ``AWS::RDS::DBInstance.MultiAZ``.
            option_group_name: ``AWS::RDS::DBInstance.OptionGroupName``.
            performance_insights_kms_key_id: ``AWS::RDS::DBInstance.PerformanceInsightsKMSKeyId``.
            performance_insights_retention_period: ``AWS::RDS::DBInstance.PerformanceInsightsRetentionPeriod``.
            port: ``AWS::RDS::DBInstance.Port``.
            preferred_backup_window: ``AWS::RDS::DBInstance.PreferredBackupWindow``.
            preferred_maintenance_window: ``AWS::RDS::DBInstance.PreferredMaintenanceWindow``.
            processor_features: ``AWS::RDS::DBInstance.ProcessorFeatures``.
            promotion_tier: ``AWS::RDS::DBInstance.PromotionTier``.
            publicly_accessible: ``AWS::RDS::DBInstance.PubliclyAccessible``.
            source_db_instance_identifier: ``AWS::RDS::DBInstance.SourceDBInstanceIdentifier``.
            source_region: ``AWS::RDS::DBInstance.SourceRegion``.
            storage_encrypted: ``AWS::RDS::DBInstance.StorageEncrypted``.
            storage_type: ``AWS::RDS::DBInstance.StorageType``.
            tags: ``AWS::RDS::DBInstance.Tags``.
            timezone: ``AWS::RDS::DBInstance.Timezone``.
            use_default_processor_features: ``AWS::RDS::DBInstance.UseDefaultProcessorFeatures``.
            vpc_security_groups: ``AWS::RDS::DBInstance.VPCSecurityGroups``.

        Stability:
            experimental
        """
        props: CfnDBInstanceProps = {"dbInstanceClass": db_instance_class}

        if allocated_storage is not None:
            props["allocatedStorage"] = allocated_storage

        if allow_major_version_upgrade is not None:
            props["allowMajorVersionUpgrade"] = allow_major_version_upgrade

        if auto_minor_version_upgrade is not None:
            props["autoMinorVersionUpgrade"] = auto_minor_version_upgrade

        if availability_zone is not None:
            props["availabilityZone"] = availability_zone

        if backup_retention_period is not None:
            props["backupRetentionPeriod"] = backup_retention_period

        if character_set_name is not None:
            props["characterSetName"] = character_set_name

        if copy_tags_to_snapshot is not None:
            props["copyTagsToSnapshot"] = copy_tags_to_snapshot

        if db_cluster_identifier is not None:
            props["dbClusterIdentifier"] = db_cluster_identifier

        if db_instance_identifier is not None:
            props["dbInstanceIdentifier"] = db_instance_identifier

        if db_name is not None:
            props["dbName"] = db_name

        if db_parameter_group_name is not None:
            props["dbParameterGroupName"] = db_parameter_group_name

        if db_security_groups is not None:
            props["dbSecurityGroups"] = db_security_groups

        if db_snapshot_identifier is not None:
            props["dbSnapshotIdentifier"] = db_snapshot_identifier

        if db_subnet_group_name is not None:
            props["dbSubnetGroupName"] = db_subnet_group_name

        if delete_automated_backups is not None:
            props["deleteAutomatedBackups"] = delete_automated_backups

        if deletion_protection is not None:
            props["deletionProtection"] = deletion_protection

        if domain is not None:
            props["domain"] = domain

        if domain_iam_role_name is not None:
            props["domainIamRoleName"] = domain_iam_role_name

        if enable_cloudwatch_logs_exports is not None:
            props["enableCloudwatchLogsExports"] = enable_cloudwatch_logs_exports

        if enable_iam_database_authentication is not None:
            props["enableIamDatabaseAuthentication"] = enable_iam_database_authentication

        if enable_performance_insights is not None:
            props["enablePerformanceInsights"] = enable_performance_insights

        if engine is not None:
            props["engine"] = engine

        if engine_version is not None:
            props["engineVersion"] = engine_version

        if iops is not None:
            props["iops"] = iops

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

        if license_model is not None:
            props["licenseModel"] = license_model

        if master_username is not None:
            props["masterUsername"] = master_username

        if master_user_password is not None:
            props["masterUserPassword"] = master_user_password

        if monitoring_interval is not None:
            props["monitoringInterval"] = monitoring_interval

        if monitoring_role_arn is not None:
            props["monitoringRoleArn"] = monitoring_role_arn

        if multi_az is not None:
            props["multiAz"] = multi_az

        if option_group_name is not None:
            props["optionGroupName"] = option_group_name

        if performance_insights_kms_key_id is not None:
            props["performanceInsightsKmsKeyId"] = performance_insights_kms_key_id

        if performance_insights_retention_period is not None:
            props["performanceInsightsRetentionPeriod"] = performance_insights_retention_period

        if port is not None:
            props["port"] = port

        if preferred_backup_window is not None:
            props["preferredBackupWindow"] = preferred_backup_window

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if processor_features is not None:
            props["processorFeatures"] = processor_features

        if promotion_tier is not None:
            props["promotionTier"] = promotion_tier

        if publicly_accessible is not None:
            props["publiclyAccessible"] = publicly_accessible

        if source_db_instance_identifier is not None:
            props["sourceDbInstanceIdentifier"] = source_db_instance_identifier

        if source_region is not None:
            props["sourceRegion"] = source_region

        if storage_encrypted is not None:
            props["storageEncrypted"] = storage_encrypted

        if storage_type is not None:
            props["storageType"] = storage_type

        if tags is not None:
            props["tags"] = tags

        if timezone is not None:
            props["timezone"] = timezone

        if use_default_processor_features is not None:
            props["useDefaultProcessorFeatures"] = use_default_processor_features

        if vpc_security_groups is not None:
            props["vpcSecurityGroups"] = vpc_security_groups

        jsii.create(CfnDBInstance, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrEndpointAddress")
    def attr_endpoint_address(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Endpoint.Address
        """
        return jsii.get(self, "attrEndpointAddress")

    @property
    @jsii.member(jsii_name="attrEndpointPort")
    def attr_endpoint_port(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Endpoint.Port
        """
        return jsii.get(self, "attrEndpointPort")

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
        """``AWS::RDS::DBInstance.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="dbInstanceClass")
    def db_instance_class(self) -> str:
        """``AWS::RDS::DBInstance.DBInstanceClass``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbinstanceclass
        Stability:
            stable
        """
        return jsii.get(self, "dbInstanceClass")

    @db_instance_class.setter
    def db_instance_class(self, value: str):
        return jsii.set(self, "dbInstanceClass", value)

    @property
    @jsii.member(jsii_name="allocatedStorage")
    def allocated_storage(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.AllocatedStorage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-allocatedstorage
        Stability:
            stable
        """
        return jsii.get(self, "allocatedStorage")

    @allocated_storage.setter
    def allocated_storage(self, value: typing.Optional[str]):
        return jsii.set(self, "allocatedStorage", value)

    @property
    @jsii.member(jsii_name="allowMajorVersionUpgrade")
    def allow_major_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBInstance.AllowMajorVersionUpgrade``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-allowmajorversionupgrade
        Stability:
            stable
        """
        return jsii.get(self, "allowMajorVersionUpgrade")

    @allow_major_version_upgrade.setter
    def allow_major_version_upgrade(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "allowMajorVersionUpgrade", value)

    @property
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBInstance.AutoMinorVersionUpgrade``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-autominorversionupgrade
        Stability:
            stable
        """
        return jsii.get(self, "autoMinorVersionUpgrade")

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "autoMinorVersionUpgrade", value)

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-availabilityzone
        Stability:
            stable
        """
        return jsii.get(self, "availabilityZone")

    @availability_zone.setter
    def availability_zone(self, value: typing.Optional[str]):
        return jsii.set(self, "availabilityZone", value)

    @property
    @jsii.member(jsii_name="backupRetentionPeriod")
    def backup_retention_period(self) -> typing.Optional[jsii.Number]:
        """``AWS::RDS::DBInstance.BackupRetentionPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-backupretentionperiod
        Stability:
            stable
        """
        return jsii.get(self, "backupRetentionPeriod")

    @backup_retention_period.setter
    def backup_retention_period(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "backupRetentionPeriod", value)

    @property
    @jsii.member(jsii_name="characterSetName")
    def character_set_name(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.CharacterSetName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-charactersetname
        Stability:
            stable
        """
        return jsii.get(self, "characterSetName")

    @character_set_name.setter
    def character_set_name(self, value: typing.Optional[str]):
        return jsii.set(self, "characterSetName", value)

    @property
    @jsii.member(jsii_name="copyTagsToSnapshot")
    def copy_tags_to_snapshot(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBInstance.CopyTagsToSnapshot``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-copytagstosnapshot
        Stability:
            stable
        """
        return jsii.get(self, "copyTagsToSnapshot")

    @copy_tags_to_snapshot.setter
    def copy_tags_to_snapshot(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "copyTagsToSnapshot", value)

    @property
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.DBClusterIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbclusteridentifier
        Stability:
            stable
        """
        return jsii.get(self, "dbClusterIdentifier")

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "dbClusterIdentifier", value)

    @property
    @jsii.member(jsii_name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.DBInstanceIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbinstanceidentifier
        Stability:
            stable
        """
        return jsii.get(self, "dbInstanceIdentifier")

    @db_instance_identifier.setter
    def db_instance_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "dbInstanceIdentifier", value)

    @property
    @jsii.member(jsii_name="dbName")
    def db_name(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.DBName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbname
        Stability:
            stable
        """
        return jsii.get(self, "dbName")

    @db_name.setter
    def db_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbName", value)

    @property
    @jsii.member(jsii_name="dbParameterGroupName")
    def db_parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.DBParameterGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbparametergroupname
        Stability:
            stable
        """
        return jsii.get(self, "dbParameterGroupName")

    @db_parameter_group_name.setter
    def db_parameter_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbParameterGroupName", value)

    @property
    @jsii.member(jsii_name="dbSecurityGroups")
    def db_security_groups(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RDS::DBInstance.DBSecurityGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbsecuritygroups
        Stability:
            stable
        """
        return jsii.get(self, "dbSecurityGroups")

    @db_security_groups.setter
    def db_security_groups(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "dbSecurityGroups", value)

    @property
    @jsii.member(jsii_name="dbSnapshotIdentifier")
    def db_snapshot_identifier(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.DBSnapshotIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbsnapshotidentifier
        Stability:
            stable
        """
        return jsii.get(self, "dbSnapshotIdentifier")

    @db_snapshot_identifier.setter
    def db_snapshot_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "dbSnapshotIdentifier", value)

    @property
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.DBSubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbsubnetgroupname
        Stability:
            stable
        """
        return jsii.get(self, "dbSubnetGroupName")

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbSubnetGroupName", value)

    @property
    @jsii.member(jsii_name="deleteAutomatedBackups")
    def delete_automated_backups(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBInstance.DeleteAutomatedBackups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-deleteautomatedbackups
        Stability:
            stable
        """
        return jsii.get(self, "deleteAutomatedBackups")

    @delete_automated_backups.setter
    def delete_automated_backups(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "deleteAutomatedBackups", value)

    @property
    @jsii.member(jsii_name="deletionProtection")
    def deletion_protection(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBInstance.DeletionProtection``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-deletionprotection
        Stability:
            stable
        """
        return jsii.get(self, "deletionProtection")

    @deletion_protection.setter
    def deletion_protection(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "deletionProtection", value)

    @property
    @jsii.member(jsii_name="domain")
    def domain(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.Domain``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-domain
        Stability:
            stable
        """
        return jsii.get(self, "domain")

    @domain.setter
    def domain(self, value: typing.Optional[str]):
        return jsii.set(self, "domain", value)

    @property
    @jsii.member(jsii_name="domainIamRoleName")
    def domain_iam_role_name(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.DomainIAMRoleName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-domainiamrolename
        Stability:
            stable
        """
        return jsii.get(self, "domainIamRoleName")

    @domain_iam_role_name.setter
    def domain_iam_role_name(self, value: typing.Optional[str]):
        return jsii.set(self, "domainIamRoleName", value)

    @property
    @jsii.member(jsii_name="enableCloudwatchLogsExports")
    def enable_cloudwatch_logs_exports(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RDS::DBInstance.EnableCloudwatchLogsExports``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-enablecloudwatchlogsexports
        Stability:
            stable
        """
        return jsii.get(self, "enableCloudwatchLogsExports")

    @enable_cloudwatch_logs_exports.setter
    def enable_cloudwatch_logs_exports(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "enableCloudwatchLogsExports", value)

    @property
    @jsii.member(jsii_name="enableIamDatabaseAuthentication")
    def enable_iam_database_authentication(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBInstance.EnableIAMDatabaseAuthentication``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-enableiamdatabaseauthentication
        Stability:
            stable
        """
        return jsii.get(self, "enableIamDatabaseAuthentication")

    @enable_iam_database_authentication.setter
    def enable_iam_database_authentication(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enableIamDatabaseAuthentication", value)

    @property
    @jsii.member(jsii_name="enablePerformanceInsights")
    def enable_performance_insights(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBInstance.EnablePerformanceInsights``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-enableperformanceinsights
        Stability:
            stable
        """
        return jsii.get(self, "enablePerformanceInsights")

    @enable_performance_insights.setter
    def enable_performance_insights(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enablePerformanceInsights", value)

    @property
    @jsii.member(jsii_name="engine")
    def engine(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.Engine``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-engine
        Stability:
            stable
        """
        return jsii.get(self, "engine")

    @engine.setter
    def engine(self, value: typing.Optional[str]):
        return jsii.set(self, "engine", value)

    @property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.EngineVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-engineversion
        Stability:
            stable
        """
        return jsii.get(self, "engineVersion")

    @engine_version.setter
    def engine_version(self, value: typing.Optional[str]):
        return jsii.set(self, "engineVersion", value)

    @property
    @jsii.member(jsii_name="iops")
    def iops(self) -> typing.Optional[jsii.Number]:
        """``AWS::RDS::DBInstance.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-iops
        Stability:
            stable
        """
        return jsii.get(self, "iops")

    @iops.setter
    def iops(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "iops", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-kmskeyid
        Stability:
            stable
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="licenseModel")
    def license_model(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.LicenseModel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-licensemodel
        Stability:
            stable
        """
        return jsii.get(self, "licenseModel")

    @license_model.setter
    def license_model(self, value: typing.Optional[str]):
        return jsii.set(self, "licenseModel", value)

    @property
    @jsii.member(jsii_name="masterUsername")
    def master_username(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.MasterUsername``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-masterusername
        Stability:
            stable
        """
        return jsii.get(self, "masterUsername")

    @master_username.setter
    def master_username(self, value: typing.Optional[str]):
        return jsii.set(self, "masterUsername", value)

    @property
    @jsii.member(jsii_name="masterUserPassword")
    def master_user_password(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.MasterUserPassword``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-masteruserpassword
        Stability:
            stable
        """
        return jsii.get(self, "masterUserPassword")

    @master_user_password.setter
    def master_user_password(self, value: typing.Optional[str]):
        return jsii.set(self, "masterUserPassword", value)

    @property
    @jsii.member(jsii_name="monitoringInterval")
    def monitoring_interval(self) -> typing.Optional[jsii.Number]:
        """``AWS::RDS::DBInstance.MonitoringInterval``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-monitoringinterval
        Stability:
            stable
        """
        return jsii.get(self, "monitoringInterval")

    @monitoring_interval.setter
    def monitoring_interval(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "monitoringInterval", value)

    @property
    @jsii.member(jsii_name="monitoringRoleArn")
    def monitoring_role_arn(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.MonitoringRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-monitoringrolearn
        Stability:
            stable
        """
        return jsii.get(self, "monitoringRoleArn")

    @monitoring_role_arn.setter
    def monitoring_role_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "monitoringRoleArn", value)

    @property
    @jsii.member(jsii_name="multiAz")
    def multi_az(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBInstance.MultiAZ``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-multiaz
        Stability:
            stable
        """
        return jsii.get(self, "multiAz")

    @multi_az.setter
    def multi_az(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "multiAz", value)

    @property
    @jsii.member(jsii_name="optionGroupName")
    def option_group_name(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.OptionGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-optiongroupname
        Stability:
            stable
        """
        return jsii.get(self, "optionGroupName")

    @option_group_name.setter
    def option_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "optionGroupName", value)

    @property
    @jsii.member(jsii_name="performanceInsightsKmsKeyId")
    def performance_insights_kms_key_id(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.PerformanceInsightsKMSKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-performanceinsightskmskeyid
        Stability:
            stable
        """
        return jsii.get(self, "performanceInsightsKmsKeyId")

    @performance_insights_kms_key_id.setter
    def performance_insights_kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "performanceInsightsKmsKeyId", value)

    @property
    @jsii.member(jsii_name="performanceInsightsRetentionPeriod")
    def performance_insights_retention_period(self) -> typing.Optional[jsii.Number]:
        """``AWS::RDS::DBInstance.PerformanceInsightsRetentionPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-performanceinsightsretentionperiod
        Stability:
            stable
        """
        return jsii.get(self, "performanceInsightsRetentionPeriod")

    @performance_insights_retention_period.setter
    def performance_insights_retention_period(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "performanceInsightsRetentionPeriod", value)

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-port
        Stability:
            stable
        """
        return jsii.get(self, "port")

    @port.setter
    def port(self, value: typing.Optional[str]):
        return jsii.set(self, "port", value)

    @property
    @jsii.member(jsii_name="preferredBackupWindow")
    def preferred_backup_window(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.PreferredBackupWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-preferredbackupwindow
        Stability:
            stable
        """
        return jsii.get(self, "preferredBackupWindow")

    @preferred_backup_window.setter
    def preferred_backup_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredBackupWindow", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.PreferredMaintenanceWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-preferredmaintenancewindow
        Stability:
            stable
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)

    @property
    @jsii.member(jsii_name="processorFeatures")
    def processor_features(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ProcessorFeatureProperty"]]]]]:
        """``AWS::RDS::DBInstance.ProcessorFeatures``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-processorfeatures
        Stability:
            stable
        """
        return jsii.get(self, "processorFeatures")

    @processor_features.setter
    def processor_features(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ProcessorFeatureProperty"]]]]]):
        return jsii.set(self, "processorFeatures", value)

    @property
    @jsii.member(jsii_name="promotionTier")
    def promotion_tier(self) -> typing.Optional[jsii.Number]:
        """``AWS::RDS::DBInstance.PromotionTier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-promotiontier
        Stability:
            stable
        """
        return jsii.get(self, "promotionTier")

    @promotion_tier.setter
    def promotion_tier(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "promotionTier", value)

    @property
    @jsii.member(jsii_name="publiclyAccessible")
    def publicly_accessible(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBInstance.PubliclyAccessible``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-publiclyaccessible
        Stability:
            stable
        """
        return jsii.get(self, "publiclyAccessible")

    @publicly_accessible.setter
    def publicly_accessible(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "publiclyAccessible", value)

    @property
    @jsii.member(jsii_name="sourceDbInstanceIdentifier")
    def source_db_instance_identifier(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.SourceDBInstanceIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-sourcedbinstanceidentifier
        Stability:
            stable
        """
        return jsii.get(self, "sourceDbInstanceIdentifier")

    @source_db_instance_identifier.setter
    def source_db_instance_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "sourceDbInstanceIdentifier", value)

    @property
    @jsii.member(jsii_name="sourceRegion")
    def source_region(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.SourceRegion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-sourceregion
        Stability:
            stable
        """
        return jsii.get(self, "sourceRegion")

    @source_region.setter
    def source_region(self, value: typing.Optional[str]):
        return jsii.set(self, "sourceRegion", value)

    @property
    @jsii.member(jsii_name="storageEncrypted")
    def storage_encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBInstance.StorageEncrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-storageencrypted
        Stability:
            stable
        """
        return jsii.get(self, "storageEncrypted")

    @storage_encrypted.setter
    def storage_encrypted(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "storageEncrypted", value)

    @property
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.StorageType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-storagetype
        Stability:
            stable
        """
        return jsii.get(self, "storageType")

    @storage_type.setter
    def storage_type(self, value: typing.Optional[str]):
        return jsii.set(self, "storageType", value)

    @property
    @jsii.member(jsii_name="timezone")
    def timezone(self) -> typing.Optional[str]:
        """``AWS::RDS::DBInstance.Timezone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-timezone
        Stability:
            stable
        """
        return jsii.get(self, "timezone")

    @timezone.setter
    def timezone(self, value: typing.Optional[str]):
        return jsii.set(self, "timezone", value)

    @property
    @jsii.member(jsii_name="useDefaultProcessorFeatures")
    def use_default_processor_features(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::DBInstance.UseDefaultProcessorFeatures``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-usedefaultprocessorfeatures
        Stability:
            stable
        """
        return jsii.get(self, "useDefaultProcessorFeatures")

    @use_default_processor_features.setter
    def use_default_processor_features(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "useDefaultProcessorFeatures", value)

    @property
    @jsii.member(jsii_name="vpcSecurityGroups")
    def vpc_security_groups(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RDS::DBInstance.VPCSecurityGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-vpcsecuritygroups
        Stability:
            stable
        """
        return jsii.get(self, "vpcSecurityGroups")

    @vpc_security_groups.setter
    def vpc_security_groups(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "vpcSecurityGroups", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBInstance.ProcessorFeatureProperty", jsii_struct_bases=[])
    class ProcessorFeatureProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbinstance-processorfeature.html
        Stability:
            stable
        """
        name: str
        """``CfnDBInstance.ProcessorFeatureProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbinstance-processorfeature.html#cfn-rds-dbinstance-processorfeature-name
        Stability:
            stable
        """

        value: str
        """``CfnDBInstance.ProcessorFeatureProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbinstance-processorfeature.html#cfn-rds-dbinstance-processorfeature-value
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBInstanceProps(jsii.compat.TypedDict, total=False):
    allocatedStorage: str
    """``AWS::RDS::DBInstance.AllocatedStorage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-allocatedstorage
    Stability:
        stable
    """
    allowMajorVersionUpgrade: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBInstance.AllowMajorVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-allowmajorversionupgrade
    Stability:
        stable
    """
    autoMinorVersionUpgrade: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBInstance.AutoMinorVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-autominorversionupgrade
    Stability:
        stable
    """
    availabilityZone: str
    """``AWS::RDS::DBInstance.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-availabilityzone
    Stability:
        stable
    """
    backupRetentionPeriod: jsii.Number
    """``AWS::RDS::DBInstance.BackupRetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-backupretentionperiod
    Stability:
        stable
    """
    characterSetName: str
    """``AWS::RDS::DBInstance.CharacterSetName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-charactersetname
    Stability:
        stable
    """
    copyTagsToSnapshot: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBInstance.CopyTagsToSnapshot``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-copytagstosnapshot
    Stability:
        stable
    """
    dbClusterIdentifier: str
    """``AWS::RDS::DBInstance.DBClusterIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbclusteridentifier
    Stability:
        stable
    """
    dbInstanceIdentifier: str
    """``AWS::RDS::DBInstance.DBInstanceIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbinstanceidentifier
    Stability:
        stable
    """
    dbName: str
    """``AWS::RDS::DBInstance.DBName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbname
    Stability:
        stable
    """
    dbParameterGroupName: str
    """``AWS::RDS::DBInstance.DBParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbparametergroupname
    Stability:
        stable
    """
    dbSecurityGroups: typing.List[str]
    """``AWS::RDS::DBInstance.DBSecurityGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbsecuritygroups
    Stability:
        stable
    """
    dbSnapshotIdentifier: str
    """``AWS::RDS::DBInstance.DBSnapshotIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbsnapshotidentifier
    Stability:
        stable
    """
    dbSubnetGroupName: str
    """``AWS::RDS::DBInstance.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbsubnetgroupname
    Stability:
        stable
    """
    deleteAutomatedBackups: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBInstance.DeleteAutomatedBackups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-deleteautomatedbackups
    Stability:
        stable
    """
    deletionProtection: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBInstance.DeletionProtection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-deletionprotection
    Stability:
        stable
    """
    domain: str
    """``AWS::RDS::DBInstance.Domain``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-domain
    Stability:
        stable
    """
    domainIamRoleName: str
    """``AWS::RDS::DBInstance.DomainIAMRoleName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-domainiamrolename
    Stability:
        stable
    """
    enableCloudwatchLogsExports: typing.List[str]
    """``AWS::RDS::DBInstance.EnableCloudwatchLogsExports``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-enablecloudwatchlogsexports
    Stability:
        stable
    """
    enableIamDatabaseAuthentication: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBInstance.EnableIAMDatabaseAuthentication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-enableiamdatabaseauthentication
    Stability:
        stable
    """
    enablePerformanceInsights: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBInstance.EnablePerformanceInsights``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-enableperformanceinsights
    Stability:
        stable
    """
    engine: str
    """``AWS::RDS::DBInstance.Engine``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-engine
    Stability:
        stable
    """
    engineVersion: str
    """``AWS::RDS::DBInstance.EngineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-engineversion
    Stability:
        stable
    """
    iops: jsii.Number
    """``AWS::RDS::DBInstance.Iops``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-iops
    Stability:
        stable
    """
    kmsKeyId: str
    """``AWS::RDS::DBInstance.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-kmskeyid
    Stability:
        stable
    """
    licenseModel: str
    """``AWS::RDS::DBInstance.LicenseModel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-licensemodel
    Stability:
        stable
    """
    masterUsername: str
    """``AWS::RDS::DBInstance.MasterUsername``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-masterusername
    Stability:
        stable
    """
    masterUserPassword: str
    """``AWS::RDS::DBInstance.MasterUserPassword``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-masteruserpassword
    Stability:
        stable
    """
    monitoringInterval: jsii.Number
    """``AWS::RDS::DBInstance.MonitoringInterval``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-monitoringinterval
    Stability:
        stable
    """
    monitoringRoleArn: str
    """``AWS::RDS::DBInstance.MonitoringRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-monitoringrolearn
    Stability:
        stable
    """
    multiAz: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBInstance.MultiAZ``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-multiaz
    Stability:
        stable
    """
    optionGroupName: str
    """``AWS::RDS::DBInstance.OptionGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-optiongroupname
    Stability:
        stable
    """
    performanceInsightsKmsKeyId: str
    """``AWS::RDS::DBInstance.PerformanceInsightsKMSKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-performanceinsightskmskeyid
    Stability:
        stable
    """
    performanceInsightsRetentionPeriod: jsii.Number
    """``AWS::RDS::DBInstance.PerformanceInsightsRetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-performanceinsightsretentionperiod
    Stability:
        stable
    """
    port: str
    """``AWS::RDS::DBInstance.Port``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-port
    Stability:
        stable
    """
    preferredBackupWindow: str
    """``AWS::RDS::DBInstance.PreferredBackupWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-preferredbackupwindow
    Stability:
        stable
    """
    preferredMaintenanceWindow: str
    """``AWS::RDS::DBInstance.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-preferredmaintenancewindow
    Stability:
        stable
    """
    processorFeatures: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDBInstance.ProcessorFeatureProperty"]]]
    """``AWS::RDS::DBInstance.ProcessorFeatures``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-processorfeatures
    Stability:
        stable
    """
    promotionTier: jsii.Number
    """``AWS::RDS::DBInstance.PromotionTier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-promotiontier
    Stability:
        stable
    """
    publiclyAccessible: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBInstance.PubliclyAccessible``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-publiclyaccessible
    Stability:
        stable
    """
    sourceDbInstanceIdentifier: str
    """``AWS::RDS::DBInstance.SourceDBInstanceIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-sourcedbinstanceidentifier
    Stability:
        stable
    """
    sourceRegion: str
    """``AWS::RDS::DBInstance.SourceRegion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-sourceregion
    Stability:
        stable
    """
    storageEncrypted: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBInstance.StorageEncrypted``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-storageencrypted
    Stability:
        stable
    """
    storageType: str
    """``AWS::RDS::DBInstance.StorageType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-storagetype
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::RDS::DBInstance.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-tags
    Stability:
        stable
    """
    timezone: str
    """``AWS::RDS::DBInstance.Timezone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-timezone
    Stability:
        stable
    """
    useDefaultProcessorFeatures: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::DBInstance.UseDefaultProcessorFeatures``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-usedefaultprocessorfeatures
    Stability:
        stable
    """
    vpcSecurityGroups: typing.List[str]
    """``AWS::RDS::DBInstance.VPCSecurityGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-vpcsecuritygroups
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBInstanceProps", jsii_struct_bases=[_CfnDBInstanceProps])
class CfnDBInstanceProps(_CfnDBInstanceProps):
    """Properties for defining a ``AWS::RDS::DBInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html
    Stability:
        stable
    """
    dbInstanceClass: str
    """``AWS::RDS::DBInstance.DBInstanceClass``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbinstanceclass
    Stability:
        stable
    """

class CfnDBParameterGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBParameterGroup"):
    """A CloudFormation ``AWS::RDS::DBParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html
    Stability:
        stable
    cloudformationResource:
        AWS::RDS::DBParameterGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, description: str, family: str, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::RDS::DBParameterGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::RDS::DBParameterGroup.Description``.
            family: ``AWS::RDS::DBParameterGroup.Family``.
            parameters: ``AWS::RDS::DBParameterGroup.Parameters``.
            tags: ``AWS::RDS::DBParameterGroup.Tags``.

        Stability:
            experimental
        """
        props: CfnDBParameterGroupProps = {"description": description, "family": family}

        if parameters is not None:
            props["parameters"] = parameters

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnDBParameterGroup, self, [scope, id, props])

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
        """``AWS::RDS::DBParameterGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html#cfn-rds-dbparametergroup-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::RDS::DBParameterGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html#cfn-rds-dbparametergroup-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="family")
    def family(self) -> str:
        """``AWS::RDS::DBParameterGroup.Family``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html#cfn-rds-dbparametergroup-family
        Stability:
            stable
        """
        return jsii.get(self, "family")

    @family.setter
    def family(self, value: str):
        return jsii.set(self, "family", value)

    @property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]:
        """``AWS::RDS::DBParameterGroup.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html#cfn-rds-dbparametergroup-parameters
        Stability:
            stable
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.Mapping[str,str]]]]):
        return jsii.set(self, "parameters", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBParameterGroupProps(jsii.compat.TypedDict, total=False):
    parameters: typing.Union[aws_cdk.core.IResolvable, typing.Mapping[str,str]]
    """``AWS::RDS::DBParameterGroup.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html#cfn-rds-dbparametergroup-parameters
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::RDS::DBParameterGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html#cfn-rds-dbparametergroup-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBParameterGroupProps", jsii_struct_bases=[_CfnDBParameterGroupProps])
class CfnDBParameterGroupProps(_CfnDBParameterGroupProps):
    """Properties for defining a ``AWS::RDS::DBParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html
    Stability:
        stable
    """
    description: str
    """``AWS::RDS::DBParameterGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html#cfn-rds-dbparametergroup-description
    Stability:
        stable
    """

    family: str
    """``AWS::RDS::DBParameterGroup.Family``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html#cfn-rds-dbparametergroup-family
    Stability:
        stable
    """

class CfnDBSecurityGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBSecurityGroup"):
    """A CloudFormation ``AWS::RDS::DBSecurityGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html
    Stability:
        stable
    cloudformationResource:
        AWS::RDS::DBSecurityGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, db_security_group_ingress: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "IngressProperty"]]], group_description: str, ec2_vpc_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::RDS::DBSecurityGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            db_security_group_ingress: ``AWS::RDS::DBSecurityGroup.DBSecurityGroupIngress``.
            group_description: ``AWS::RDS::DBSecurityGroup.GroupDescription``.
            ec2_vpc_id: ``AWS::RDS::DBSecurityGroup.EC2VpcId``.
            tags: ``AWS::RDS::DBSecurityGroup.Tags``.

        Stability:
            experimental
        """
        props: CfnDBSecurityGroupProps = {"dbSecurityGroupIngress": db_security_group_ingress, "groupDescription": group_description}

        if ec2_vpc_id is not None:
            props["ec2VpcId"] = ec2_vpc_id

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnDBSecurityGroup, self, [scope, id, props])

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
        """``AWS::RDS::DBSecurityGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html#cfn-rds-dbsecuritygroup-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="dbSecurityGroupIngress")
    def db_security_group_ingress(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "IngressProperty"]]]:
        """``AWS::RDS::DBSecurityGroup.DBSecurityGroupIngress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html#cfn-rds-dbsecuritygroup-dbsecuritygroupingress
        Stability:
            stable
        """
        return jsii.get(self, "dbSecurityGroupIngress")

    @db_security_group_ingress.setter
    def db_security_group_ingress(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "IngressProperty"]]]):
        return jsii.set(self, "dbSecurityGroupIngress", value)

    @property
    @jsii.member(jsii_name="groupDescription")
    def group_description(self) -> str:
        """``AWS::RDS::DBSecurityGroup.GroupDescription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html#cfn-rds-dbsecuritygroup-groupdescription
        Stability:
            stable
        """
        return jsii.get(self, "groupDescription")

    @group_description.setter
    def group_description(self, value: str):
        return jsii.set(self, "groupDescription", value)

    @property
    @jsii.member(jsii_name="ec2VpcId")
    def ec2_vpc_id(self) -> typing.Optional[str]:
        """``AWS::RDS::DBSecurityGroup.EC2VpcId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html#cfn-rds-dbsecuritygroup-ec2vpcid
        Stability:
            stable
        """
        return jsii.get(self, "ec2VpcId")

    @ec2_vpc_id.setter
    def ec2_vpc_id(self, value: typing.Optional[str]):
        return jsii.set(self, "ec2VpcId", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBSecurityGroup.IngressProperty", jsii_struct_bases=[])
    class IngressProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group-rule.html
        Stability:
            stable
        """
        cidrip: str
        """``CfnDBSecurityGroup.IngressProperty.CIDRIP``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group-rule.html#cfn-rds-securitygroup-cidrip
        Stability:
            stable
        """

        ec2SecurityGroupId: str
        """``CfnDBSecurityGroup.IngressProperty.EC2SecurityGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group-rule.html#cfn-rds-securitygroup-ec2securitygroupid
        Stability:
            stable
        """

        ec2SecurityGroupName: str
        """``CfnDBSecurityGroup.IngressProperty.EC2SecurityGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group-rule.html#cfn-rds-securitygroup-ec2securitygroupname
        Stability:
            stable
        """

        ec2SecurityGroupOwnerId: str
        """``CfnDBSecurityGroup.IngressProperty.EC2SecurityGroupOwnerId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group-rule.html#cfn-rds-securitygroup-ec2securitygroupownerid
        Stability:
            stable
        """


class CfnDBSecurityGroupIngress(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBSecurityGroupIngress"):
    """A CloudFormation ``AWS::RDS::DBSecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html
    Stability:
        stable
    cloudformationResource:
        AWS::RDS::DBSecurityGroupIngress
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, db_security_group_name: str, cidrip: typing.Optional[str]=None, ec2_security_group_id: typing.Optional[str]=None, ec2_security_group_name: typing.Optional[str]=None, ec2_security_group_owner_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::RDS::DBSecurityGroupIngress``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            db_security_group_name: ``AWS::RDS::DBSecurityGroupIngress.DBSecurityGroupName``.
            cidrip: ``AWS::RDS::DBSecurityGroupIngress.CIDRIP``.
            ec2_security_group_id: ``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupId``.
            ec2_security_group_name: ``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupName``.
            ec2_security_group_owner_id: ``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupOwnerId``.

        Stability:
            experimental
        """
        props: CfnDBSecurityGroupIngressProps = {"dbSecurityGroupName": db_security_group_name}

        if cidrip is not None:
            props["cidrip"] = cidrip

        if ec2_security_group_id is not None:
            props["ec2SecurityGroupId"] = ec2_security_group_id

        if ec2_security_group_name is not None:
            props["ec2SecurityGroupName"] = ec2_security_group_name

        if ec2_security_group_owner_id is not None:
            props["ec2SecurityGroupOwnerId"] = ec2_security_group_owner_id

        jsii.create(CfnDBSecurityGroupIngress, self, [scope, id, props])

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
    @jsii.member(jsii_name="dbSecurityGroupName")
    def db_security_group_name(self) -> str:
        """``AWS::RDS::DBSecurityGroupIngress.DBSecurityGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-dbsecuritygroupname
        Stability:
            stable
        """
        return jsii.get(self, "dbSecurityGroupName")

    @db_security_group_name.setter
    def db_security_group_name(self, value: str):
        return jsii.set(self, "dbSecurityGroupName", value)

    @property
    @jsii.member(jsii_name="cidrip")
    def cidrip(self) -> typing.Optional[str]:
        """``AWS::RDS::DBSecurityGroupIngress.CIDRIP``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-cidrip
        Stability:
            stable
        """
        return jsii.get(self, "cidrip")

    @cidrip.setter
    def cidrip(self, value: typing.Optional[str]):
        return jsii.set(self, "cidrip", value)

    @property
    @jsii.member(jsii_name="ec2SecurityGroupId")
    def ec2_security_group_id(self) -> typing.Optional[str]:
        """``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-ec2securitygroupid
        Stability:
            stable
        """
        return jsii.get(self, "ec2SecurityGroupId")

    @ec2_security_group_id.setter
    def ec2_security_group_id(self, value: typing.Optional[str]):
        return jsii.set(self, "ec2SecurityGroupId", value)

    @property
    @jsii.member(jsii_name="ec2SecurityGroupName")
    def ec2_security_group_name(self) -> typing.Optional[str]:
        """``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-ec2securitygroupname
        Stability:
            stable
        """
        return jsii.get(self, "ec2SecurityGroupName")

    @ec2_security_group_name.setter
    def ec2_security_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "ec2SecurityGroupName", value)

    @property
    @jsii.member(jsii_name="ec2SecurityGroupOwnerId")
    def ec2_security_group_owner_id(self) -> typing.Optional[str]:
        """``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupOwnerId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-ec2securitygroupownerid
        Stability:
            stable
        """
        return jsii.get(self, "ec2SecurityGroupOwnerId")

    @ec2_security_group_owner_id.setter
    def ec2_security_group_owner_id(self, value: typing.Optional[str]):
        return jsii.set(self, "ec2SecurityGroupOwnerId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBSecurityGroupIngressProps(jsii.compat.TypedDict, total=False):
    cidrip: str
    """``AWS::RDS::DBSecurityGroupIngress.CIDRIP``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-cidrip
    Stability:
        stable
    """
    ec2SecurityGroupId: str
    """``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-ec2securitygroupid
    Stability:
        stable
    """
    ec2SecurityGroupName: str
    """``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-ec2securitygroupname
    Stability:
        stable
    """
    ec2SecurityGroupOwnerId: str
    """``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupOwnerId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-ec2securitygroupownerid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBSecurityGroupIngressProps", jsii_struct_bases=[_CfnDBSecurityGroupIngressProps])
class CfnDBSecurityGroupIngressProps(_CfnDBSecurityGroupIngressProps):
    """Properties for defining a ``AWS::RDS::DBSecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html
    Stability:
        stable
    """
    dbSecurityGroupName: str
    """``AWS::RDS::DBSecurityGroupIngress.DBSecurityGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-dbsecuritygroupname
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBSecurityGroupProps(jsii.compat.TypedDict, total=False):
    ec2VpcId: str
    """``AWS::RDS::DBSecurityGroup.EC2VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html#cfn-rds-dbsecuritygroup-ec2vpcid
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::RDS::DBSecurityGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html#cfn-rds-dbsecuritygroup-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBSecurityGroupProps", jsii_struct_bases=[_CfnDBSecurityGroupProps])
class CfnDBSecurityGroupProps(_CfnDBSecurityGroupProps):
    """Properties for defining a ``AWS::RDS::DBSecurityGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html
    Stability:
        stable
    """
    dbSecurityGroupIngress: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnDBSecurityGroup.IngressProperty"]]]
    """``AWS::RDS::DBSecurityGroup.DBSecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html#cfn-rds-dbsecuritygroup-dbsecuritygroupingress
    Stability:
        stable
    """

    groupDescription: str
    """``AWS::RDS::DBSecurityGroup.GroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html#cfn-rds-dbsecuritygroup-groupdescription
    Stability:
        stable
    """

class CfnDBSubnetGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBSubnetGroup"):
    """A CloudFormation ``AWS::RDS::DBSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html
    Stability:
        stable
    cloudformationResource:
        AWS::RDS::DBSubnetGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, db_subnet_group_description: str, subnet_ids: typing.List[str], db_subnet_group_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::RDS::DBSubnetGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            db_subnet_group_description: ``AWS::RDS::DBSubnetGroup.DBSubnetGroupDescription``.
            subnet_ids: ``AWS::RDS::DBSubnetGroup.SubnetIds``.
            db_subnet_group_name: ``AWS::RDS::DBSubnetGroup.DBSubnetGroupName``.
            tags: ``AWS::RDS::DBSubnetGroup.Tags``.

        Stability:
            experimental
        """
        props: CfnDBSubnetGroupProps = {"dbSubnetGroupDescription": db_subnet_group_description, "subnetIds": subnet_ids}

        if db_subnet_group_name is not None:
            props["dbSubnetGroupName"] = db_subnet_group_name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnDBSubnetGroup, self, [scope, id, props])

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
        """``AWS::RDS::DBSubnetGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html#cfn-rds-dbsubnetgroup-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="dbSubnetGroupDescription")
    def db_subnet_group_description(self) -> str:
        """``AWS::RDS::DBSubnetGroup.DBSubnetGroupDescription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html#cfn-rds-dbsubnetgroup-dbsubnetgroupdescription
        Stability:
            stable
        """
        return jsii.get(self, "dbSubnetGroupDescription")

    @db_subnet_group_description.setter
    def db_subnet_group_description(self, value: str):
        return jsii.set(self, "dbSubnetGroupDescription", value)

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::RDS::DBSubnetGroup.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html#cfn-rds-dbsubnetgroup-subnetids
        Stability:
            stable
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[str]):
        return jsii.set(self, "subnetIds", value)

    @property
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::RDS::DBSubnetGroup.DBSubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html#cfn-rds-dbsubnetgroup-dbsubnetgroupname
        Stability:
            stable
        """
        return jsii.get(self, "dbSubnetGroupName")

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbSubnetGroupName", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBSubnetGroupProps(jsii.compat.TypedDict, total=False):
    dbSubnetGroupName: str
    """``AWS::RDS::DBSubnetGroup.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html#cfn-rds-dbsubnetgroup-dbsubnetgroupname
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::RDS::DBSubnetGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html#cfn-rds-dbsubnetgroup-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBSubnetGroupProps", jsii_struct_bases=[_CfnDBSubnetGroupProps])
class CfnDBSubnetGroupProps(_CfnDBSubnetGroupProps):
    """Properties for defining a ``AWS::RDS::DBSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html
    Stability:
        stable
    """
    dbSubnetGroupDescription: str
    """``AWS::RDS::DBSubnetGroup.DBSubnetGroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html#cfn-rds-dbsubnetgroup-dbsubnetgroupdescription
    Stability:
        stable
    """

    subnetIds: typing.List[str]
    """``AWS::RDS::DBSubnetGroup.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html#cfn-rds-dbsubnetgroup-subnetids
    Stability:
        stable
    """

class CfnEventSubscription(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnEventSubscription"):
    """A CloudFormation ``AWS::RDS::EventSubscription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html
    Stability:
        stable
    cloudformationResource:
        AWS::RDS::EventSubscription
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, sns_topic_arn: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, event_categories: typing.Optional[typing.List[str]]=None, source_ids: typing.Optional[typing.List[str]]=None, source_type: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::RDS::EventSubscription``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            sns_topic_arn: ``AWS::RDS::EventSubscription.SnsTopicArn``.
            enabled: ``AWS::RDS::EventSubscription.Enabled``.
            event_categories: ``AWS::RDS::EventSubscription.EventCategories``.
            source_ids: ``AWS::RDS::EventSubscription.SourceIds``.
            source_type: ``AWS::RDS::EventSubscription.SourceType``.

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

        jsii.create(CfnEventSubscription, self, [scope, id, props])

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
    @jsii.member(jsii_name="snsTopicArn")
    def sns_topic_arn(self) -> str:
        """``AWS::RDS::EventSubscription.SnsTopicArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-snstopicarn
        Stability:
            stable
        """
        return jsii.get(self, "snsTopicArn")

    @sns_topic_arn.setter
    def sns_topic_arn(self, value: str):
        return jsii.set(self, "snsTopicArn", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::RDS::EventSubscription.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-enabled
        Stability:
            stable
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "enabled", value)

    @property
    @jsii.member(jsii_name="eventCategories")
    def event_categories(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RDS::EventSubscription.EventCategories``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-eventcategories
        Stability:
            stable
        """
        return jsii.get(self, "eventCategories")

    @event_categories.setter
    def event_categories(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "eventCategories", value)

    @property
    @jsii.member(jsii_name="sourceIds")
    def source_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::RDS::EventSubscription.SourceIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-sourceids
        Stability:
            stable
        """
        return jsii.get(self, "sourceIds")

    @source_ids.setter
    def source_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "sourceIds", value)

    @property
    @jsii.member(jsii_name="sourceType")
    def source_type(self) -> typing.Optional[str]:
        """``AWS::RDS::EventSubscription.SourceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-sourcetype
        Stability:
            stable
        """
        return jsii.get(self, "sourceType")

    @source_type.setter
    def source_type(self, value: typing.Optional[str]):
        return jsii.set(self, "sourceType", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEventSubscriptionProps(jsii.compat.TypedDict, total=False):
    enabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::RDS::EventSubscription.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-enabled
    Stability:
        stable
    """
    eventCategories: typing.List[str]
    """``AWS::RDS::EventSubscription.EventCategories``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-eventcategories
    Stability:
        stable
    """
    sourceIds: typing.List[str]
    """``AWS::RDS::EventSubscription.SourceIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-sourceids
    Stability:
        stable
    """
    sourceType: str
    """``AWS::RDS::EventSubscription.SourceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-sourcetype
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnEventSubscriptionProps", jsii_struct_bases=[_CfnEventSubscriptionProps])
class CfnEventSubscriptionProps(_CfnEventSubscriptionProps):
    """Properties for defining a ``AWS::RDS::EventSubscription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html
    Stability:
        stable
    """
    snsTopicArn: str
    """``AWS::RDS::EventSubscription.SnsTopicArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-snstopicarn
    Stability:
        stable
    """

class CfnOptionGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnOptionGroup"):
    """A CloudFormation ``AWS::RDS::OptionGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html
    Stability:
        stable
    cloudformationResource:
        AWS::RDS::OptionGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, engine_name: str, major_engine_version: str, option_configurations: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "OptionConfigurationProperty"]]], option_group_description: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::RDS::OptionGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            engine_name: ``AWS::RDS::OptionGroup.EngineName``.
            major_engine_version: ``AWS::RDS::OptionGroup.MajorEngineVersion``.
            option_configurations: ``AWS::RDS::OptionGroup.OptionConfigurations``.
            option_group_description: ``AWS::RDS::OptionGroup.OptionGroupDescription``.
            tags: ``AWS::RDS::OptionGroup.Tags``.

        Stability:
            experimental
        """
        props: CfnOptionGroupProps = {"engineName": engine_name, "majorEngineVersion": major_engine_version, "optionConfigurations": option_configurations, "optionGroupDescription": option_group_description}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnOptionGroup, self, [scope, id, props])

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
        """``AWS::RDS::OptionGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="engineName")
    def engine_name(self) -> str:
        """``AWS::RDS::OptionGroup.EngineName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-enginename
        Stability:
            stable
        """
        return jsii.get(self, "engineName")

    @engine_name.setter
    def engine_name(self, value: str):
        return jsii.set(self, "engineName", value)

    @property
    @jsii.member(jsii_name="majorEngineVersion")
    def major_engine_version(self) -> str:
        """``AWS::RDS::OptionGroup.MajorEngineVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-majorengineversion
        Stability:
            stable
        """
        return jsii.get(self, "majorEngineVersion")

    @major_engine_version.setter
    def major_engine_version(self, value: str):
        return jsii.set(self, "majorEngineVersion", value)

    @property
    @jsii.member(jsii_name="optionConfigurations")
    def option_configurations(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "OptionConfigurationProperty"]]]:
        """``AWS::RDS::OptionGroup.OptionConfigurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-optionconfigurations
        Stability:
            stable
        """
        return jsii.get(self, "optionConfigurations")

    @option_configurations.setter
    def option_configurations(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "OptionConfigurationProperty"]]]):
        return jsii.set(self, "optionConfigurations", value)

    @property
    @jsii.member(jsii_name="optionGroupDescription")
    def option_group_description(self) -> str:
        """``AWS::RDS::OptionGroup.OptionGroupDescription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-optiongroupdescription
        Stability:
            stable
        """
        return jsii.get(self, "optionGroupDescription")

    @option_group_description.setter
    def option_group_description(self, value: str):
        return jsii.set(self, "optionGroupDescription", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _OptionConfigurationProperty(jsii.compat.TypedDict, total=False):
        dbSecurityGroupMemberships: typing.List[str]
        """``CfnOptionGroup.OptionConfigurationProperty.DBSecurityGroupMemberships``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html#cfn-rds-optiongroup-optionconfigurations-dbsecuritygroupmemberships
        Stability:
            stable
        """
        optionSettings: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnOptionGroup.OptionSettingProperty"]]]
        """``CfnOptionGroup.OptionConfigurationProperty.OptionSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html#cfn-rds-optiongroup-optionconfigurations-optionsettings
        Stability:
            stable
        """
        optionVersion: str
        """``CfnOptionGroup.OptionConfigurationProperty.OptionVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html#cfn-rds-optiongroup-optionconfiguration-optionversion
        Stability:
            stable
        """
        port: jsii.Number
        """``CfnOptionGroup.OptionConfigurationProperty.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html#cfn-rds-optiongroup-optionconfigurations-port
        Stability:
            stable
        """
        vpcSecurityGroupMemberships: typing.List[str]
        """``CfnOptionGroup.OptionConfigurationProperty.VpcSecurityGroupMemberships``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html#cfn-rds-optiongroup-optionconfigurations-vpcsecuritygroupmemberships
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnOptionGroup.OptionConfigurationProperty", jsii_struct_bases=[_OptionConfigurationProperty])
    class OptionConfigurationProperty(_OptionConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html
        Stability:
            stable
        """
        optionName: str
        """``CfnOptionGroup.OptionConfigurationProperty.OptionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html#cfn-rds-optiongroup-optionconfigurations-optionname
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnOptionGroup.OptionSettingProperty", jsii_struct_bases=[])
    class OptionSettingProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations-optionsettings.html
        Stability:
            stable
        """
        name: str
        """``CfnOptionGroup.OptionSettingProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations-optionsettings.html#cfn-rds-optiongroup-optionconfigurations-optionsettings-name
        Stability:
            stable
        """

        value: str
        """``CfnOptionGroup.OptionSettingProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations-optionsettings.html#cfn-rds-optiongroup-optionconfigurations-optionsettings-value
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnOptionGroupProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::RDS::OptionGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnOptionGroupProps", jsii_struct_bases=[_CfnOptionGroupProps])
class CfnOptionGroupProps(_CfnOptionGroupProps):
    """Properties for defining a ``AWS::RDS::OptionGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html
    Stability:
        stable
    """
    engineName: str
    """``AWS::RDS::OptionGroup.EngineName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-enginename
    Stability:
        stable
    """

    majorEngineVersion: str
    """``AWS::RDS::OptionGroup.MajorEngineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-majorengineversion
    Stability:
        stable
    """

    optionConfigurations: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnOptionGroup.OptionConfigurationProperty"]]]
    """``AWS::RDS::OptionGroup.OptionConfigurations``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-optionconfigurations
    Stability:
        stable
    """

    optionGroupDescription: str
    """``AWS::RDS::OptionGroup.OptionGroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-optiongroupdescription
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.DatabaseClusterAttributes", jsii_struct_bases=[])
class DatabaseClusterAttributes(jsii.compat.TypedDict):
    """Properties that describe an existing cluster instance.

    Stability:
        experimental
    """
    clusterEndpointAddress: str
    """Cluster endpoint address.

    Stability:
        experimental
    """

    clusterIdentifier: str
    """Identifier for the cluster.

    Stability:
        experimental
    """

    instanceEndpointAddresses: typing.List[str]
    """Endpoint addresses of individual instances.

    Stability:
        experimental
    """

    instanceIdentifiers: typing.List[str]
    """Identifier for the instances.

    Stability:
        experimental
    """

    port: jsii.Number
    """The database port.

    Stability:
        experimental
    """

    readerEndpointAddress: str
    """Reader endpoint address.

    Stability:
        experimental
    """

    securityGroupId: str
    """The security group for this database cluster.

    Stability:
        experimental
    """

class DatabaseClusterEngine(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.DatabaseClusterEngine"):
    """A database cluster engine.

    Provides mapping to the serverless application
    used for secret rotation.

    Stability:
        experimental
    """
    def __init__(self, name: str, secret_rotation_application: "SecretRotationApplication") -> None:
        """
        Arguments:
            name: -
            secret_rotation_application: -

        Stability:
            experimental
        """
        jsii.create(DatabaseClusterEngine, self, [name, secret_rotation_application])

    @classproperty
    @jsii.member(jsii_name="AURORA")
    def AURORA(cls) -> "DatabaseClusterEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "AURORA")

    @classproperty
    @jsii.member(jsii_name="AURORA_MYSQL")
    def AURORA_MYSQL(cls) -> "DatabaseClusterEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "AURORA_MYSQL")

    @classproperty
    @jsii.member(jsii_name="AURORA_POSTGRESQL")
    def AURORA_POSTGRESQL(cls) -> "DatabaseClusterEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "AURORA_POSTGRESQL")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """The engine.

        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @property
    @jsii.member(jsii_name="secretRotationApplication")
    def secret_rotation_application(self) -> "SecretRotationApplication":
        """The secret rotation application.

        Stability:
            experimental
        """
        return jsii.get(self, "secretRotationApplication")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _DatabaseClusterProps(jsii.compat.TypedDict, total=False):
    backup: "BackupProps"
    """Backup settings.

    Default:
        - Backup retention period for automated backups is 1 day.
          Backup preferred window is set to a 30-minute window selected at random from an
          8-hour block of time for each AWS Region, occurring on a random day of the week.

    See:
        https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow.Aurora
    Stability:
        experimental
    """
    clusterIdentifier: str
    """An optional identifier for the cluster.

    Default:
        - A name is automatically generated.

    Stability:
        experimental
    """
    defaultDatabaseName: str
    """Name of a database which is automatically created inside the cluster.

    Default:
        - Database is not created in cluster.

    Stability:
        experimental
    """
    engineVersion: str
    """What version of the database to start.

    Default:
        - The default for the engine is used.

    Stability:
        experimental
    """
    instanceIdentifierBase: str
    """Base identifier for instances.

    Every replica is named by appending the replica number to this string, 1-based.

    Default:
        - clusterIdentifier is used with the word "Instance" appended.
          If clusterIdentifier is not provided, the identifier is automatically generated.

    Stability:
        experimental
    """
    instances: jsii.Number
    """How many replicas/instances to create.

    Has to be at least 1.

    Default:
        2

    Stability:
        experimental
    """
    kmsKey: aws_cdk.aws_kms.IKey
    """The KMS key for storage encryption.

    If specified ``storageEncrypted``
    will be set to ``true``.

    Default:
        - default master key.

    Stability:
        experimental
    """
    parameterGroup: "IParameterGroup"
    """Additional parameters to pass to the database engine.

    Default:
        - No parameter group.

    Stability:
        experimental
    """
    port: jsii.Number
    """What port to listen on.

    Default:
        - The default for the engine is used.

    Stability:
        experimental
    """
    preferredMaintenanceWindow: str
    """A daily time range in 24-hours UTC format in which backups preferably execute.

    Must be at least 30 minutes long.

    Example: '01:00-02:00'

    Default:
        - 30-minute window selected at random from an 8-hour block of time for
          each AWS Region, occurring on a random day of the week.

    See:
        https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow.Aurora
    Stability:
        experimental
    """
    removalPolicy: aws_cdk.core.RemovalPolicy
    """The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update.

    Default:
        - Retain cluster.

    Stability:
        experimental
    """
    storageEncrypted: bool
    """Whether to enable storage encryption.

    Default:
        false

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.DatabaseClusterProps", jsii_struct_bases=[_DatabaseClusterProps])
class DatabaseClusterProps(_DatabaseClusterProps):
    """Properties for a new database cluster.

    Stability:
        experimental
    """
    engine: "DatabaseClusterEngine"
    """What kind of database to start.

    Stability:
        experimental
    """

    instanceProps: "InstanceProps"
    """Settings for the individual instances that are launched.

    Stability:
        experimental
    """

    masterUser: "Login"
    """Username and password for the administrative user.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.DatabaseInstanceAttributes", jsii_struct_bases=[])
class DatabaseInstanceAttributes(jsii.compat.TypedDict):
    """Properties that describe an existing instance.

    Stability:
        experimental
    """
    instanceEndpointAddress: str
    """The endpoint address.

    Stability:
        experimental
    """

    instanceIdentifier: str
    """The instance identifier.

    Stability:
        experimental
    """

    port: jsii.Number
    """The database port.

    Stability:
        experimental
    """

    securityGroupId: str
    """The security group identifier of the instance.

    Stability:
        experimental
    """

class DatabaseInstanceEngine(DatabaseClusterEngine, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.DatabaseInstanceEngine"):
    """A database instance engine.

    Provides mapping to DatabaseEngine used for
    secret rotation.

    Stability:
        experimental
    """
    def __init__(self, name: str, secret_rotation_application: "SecretRotationApplication") -> None:
        """
        Arguments:
            name: -
            secret_rotation_application: -

        Stability:
            experimental
        """
        jsii.create(DatabaseInstanceEngine, self, [name, secret_rotation_application])

    @classproperty
    @jsii.member(jsii_name="MARIADB")
    def MARIADB(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MARIADB")

    @classproperty
    @jsii.member(jsii_name="MYSQL")
    def MYSQL(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MYSQL")

    @classproperty
    @jsii.member(jsii_name="ORACLE_EE")
    def ORACLE_EE(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ORACLE_EE")

    @classproperty
    @jsii.member(jsii_name="ORACLE_SE")
    def ORACLE_SE(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ORACLE_SE")

    @classproperty
    @jsii.member(jsii_name="ORACLE_SE1")
    def ORACLE_S_E1(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ORACLE_SE1")

    @classproperty
    @jsii.member(jsii_name="ORACLE_SE2")
    def ORACLE_S_E2(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ORACLE_SE2")

    @classproperty
    @jsii.member(jsii_name="POSTGRES")
    def POSTGRES(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "POSTGRES")

    @classproperty
    @jsii.member(jsii_name="SQL_SERVER_EE")
    def SQL_SERVER_EE(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SQL_SERVER_EE")

    @classproperty
    @jsii.member(jsii_name="SQL_SERVER_EX")
    def SQL_SERVER_EX(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SQL_SERVER_EX")

    @classproperty
    @jsii.member(jsii_name="SQL_SERVER_SE")
    def SQL_SERVER_SE(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SQL_SERVER_SE")

    @classproperty
    @jsii.member(jsii_name="SQL_SERVER_WEB")
    def SQL_SERVER_WEB(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SQL_SERVER_WEB")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _DatabaseInstanceNewProps(jsii.compat.TypedDict, total=False):
    autoMinorVersionUpgrade: bool
    """Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window.

    Default:
        true

    Stability:
        experimental
    """
    availabilityZone: str
    """The name of the Availability Zone where the DB instance will be located.

    Default:
        no preference

    Stability:
        experimental
    """
    backupRetention: aws_cdk.core.Duration
    """The number of days during which automatic DB snapshots are retained.

    Set
    to zero to disable backups.

    Default:
        1 day

    Stability:
        experimental
    """
    cloudwatchLogsExports: typing.List[str]
    """The list of log types that need to be enabled for exporting to CloudWatch Logs.

    Default:
        no log exports

    Stability:
        experimental
    """
    cloudwatchLogsRetention: aws_cdk.aws_logs.RetentionDays
    """The number of days log events are kept in CloudWatch Logs.

    When updating
    this property, unsetting it doesn't remove the log retention policy. To
    remove the retention policy, set the value to ``Infinity``.

    Default:
        logs never expire

    Stability:
        experimental
    """
    copyTagsToSnapshot: bool
    """Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance.

    Default:
        true

    Stability:
        experimental
    """
    deleteAutomatedBackups: bool
    """Indicates whether automated backups should be deleted or retained when you delete a DB instance.

    Default:
        false

    Stability:
        experimental
    """
    deletionProtection: bool
    """Indicates whether the DB instance should have deletion protection enabled.

    Default:
        true

    Stability:
        experimental
    """
    enablePerformanceInsights: bool
    """Whether to enable Performance Insights for the DB instance.

    Default:
        false

    Stability:
        experimental
    """
    iamAuthentication: bool
    """Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts.

    Default:
        false

    Stability:
        experimental
    """
    instanceIdentifier: str
    """A name for the DB instance.

    If you specify a name, AWS CloudFormation
    converts it to lowercase.

    Default:
        a CloudFormation generated name

    Stability:
        experimental
    """
    iops: jsii.Number
    """The number of I/O operations per second (IOPS) that the database provisions. The value must be equal to or greater than 1000.

    Default:
        no provisioned iops

    Stability:
        experimental
    """
    monitoringInterval: aws_cdk.core.Duration
    """The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance.

    Default:
        no enhanced monitoring

    Stability:
        experimental
    """
    multiAz: bool
    """Specifies if the database instance is a multiple Availability Zone deployment.

    Default:
        false

    Stability:
        experimental
    """
    optionGroup: "IOptionGroup"
    """The option group to associate with the instance.

    Default:
        no option group

    Stability:
        experimental
    """
    performanceInsightKmsKey: aws_cdk.aws_kms.IKey
    """The AWS KMS key for encryption of Performance Insights data.

    Default:
        default master key

    Stability:
        experimental
    """
    performanceInsightRetention: "PerformanceInsightRetention"
    """The amount of time, in days, to retain Performance Insights data.

    Default:
        7 days

    Stability:
        experimental
    """
    port: jsii.Number
    """The port for the instance.

    Default:
        the default port for the chosen engine.

    Stability:
        experimental
    """
    preferredBackupWindow: str
    """The daily time range during which automated backups are performed.

    Constraints:

    - Must be in the format ``hh24:mi-hh24:mi``.
    - Must be in Universal Coordinated Time (UTC).
    - Must not conflict with the preferred maintenance window.
    - Must be at least 30 minutes.

    Default:
        a 30-minute window selected at random from an 8-hour block of
        time for each AWS Region. To see the time blocks available, see
        https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow

    Stability:
        experimental
    """
    preferredMaintenanceWindow: str
    """The weekly time range (in UTC) during which system maintenance can occur.

    Format: ``ddd:hh24:mi-ddd:hh24:mi``
    Constraint: Minimum 30-minute window

    Default:
        a 30-minute window selected at random from an 8-hour block of
        time for each AWS Region, occurring on a random day of the week. To see
        the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow

    Stability:
        experimental
    """
    processorFeatures: "ProcessorFeatures"
    """The number of CPU cores and the number of threads per core.

    Default:
        the default number of CPU cores and threads per core for the
        chosen instance class.
        
        See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#USER_ConfigureProcessor

    Stability:
        experimental
    """
    removalPolicy: aws_cdk.core.RemovalPolicy
    """The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update.

    Default:
        RemovalPolicy.Retain

    Stability:
        experimental
    """
    storageType: "StorageType"
    """The storage type.

    Default:
        GP2

    Stability:
        experimental
    """
    vpcPlacement: aws_cdk.aws_ec2.SubnetSelection
    """The type of subnets to add to the created DB subnet group.

    Default:
        private

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.DatabaseInstanceNewProps", jsii_struct_bases=[_DatabaseInstanceNewProps])
class DatabaseInstanceNewProps(_DatabaseInstanceNewProps):
    """Construction properties for a DatabaseInstanceNew.

    Stability:
        experimental
    """
    instanceClass: aws_cdk.aws_ec2.InstanceType
    """The name of the compute and memory capacity classes.

    Stability:
        experimental
    """

    vpc: aws_cdk.aws_ec2.IVpc
    """The VPC network where the DB subnet group should be created.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[DatabaseInstanceNewProps])
class _DatabaseInstanceSourceProps(DatabaseInstanceNewProps, jsii.compat.TypedDict, total=False):
    allocatedStorage: jsii.Number
    """The allocated storage size, specified in gigabytes (GB).

    Default:
        100

    Stability:
        experimental
    """
    allowMajorVersionUpgrade: bool
    """Whether to allow major version upgrades.

    Default:
        false

    Stability:
        experimental
    """
    databaseName: str
    """The name of the database.

    Default:
        no name

    Stability:
        experimental
    """
    engineVersion: str
    """The engine version.

    To prevent automatic upgrades, be sure to specify the
    full version number.

    Default:
        RDS default engine version

    Stability:
        experimental
    """
    licenseModel: "LicenseModel"
    """The license model.

    Default:
        RDS default license model

    Stability:
        experimental
    """
    masterUserPassword: aws_cdk.core.SecretValue
    """The master user password.

    Default:
        a Secrets Manager generated password

    Stability:
        experimental
    """
    parameterGroup: "IParameterGroup"
    """The DB parameter group to associate with the instance.

    Default:
        no parameter group

    Stability:
        experimental
    """
    secretKmsKey: aws_cdk.aws_kms.IKey
    """The KMS key to use to encrypt the secret for the master user password.

    Default:
        default master key

    Stability:
        experimental
    """
    timezone: str
    """The time zone of the instance.

    Default:
        RDS default timezone

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.DatabaseInstanceSourceProps", jsii_struct_bases=[_DatabaseInstanceSourceProps])
class DatabaseInstanceSourceProps(_DatabaseInstanceSourceProps):
    """Construction properties for a DatabaseInstanceSource.

    Stability:
        experimental
    """
    engine: "DatabaseInstanceEngine"
    """The database engine.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[DatabaseInstanceSourceProps])
class _DatabaseInstanceFromSnapshotProps(DatabaseInstanceSourceProps, jsii.compat.TypedDict, total=False):
    generateMasterUserPassword: bool
    """Whether to generate a new master user password and store it in Secrets Manager.

    ``masterUsername`` must be specified when this property
    is set to true.

    Default:
        false

    Stability:
        experimental
    """
    masterUsername: str
    """The master user name.

    Default:
        inherited from the snapshot

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.DatabaseInstanceFromSnapshotProps", jsii_struct_bases=[_DatabaseInstanceFromSnapshotProps])
class DatabaseInstanceFromSnapshotProps(_DatabaseInstanceFromSnapshotProps):
    """Construction properties for a DatabaseInstanceFromSnapshot.

    Stability:
        experimental
    """
    snapshotIdentifier: str
    """The name or Amazon Resource Name (ARN) of the DB snapshot that's used to restore the DB instance.

    If you're restoring from a shared manual DB
    snapshot, you must specify the ARN of the snapshot.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[DatabaseInstanceSourceProps])
class _DatabaseInstanceProps(DatabaseInstanceSourceProps, jsii.compat.TypedDict, total=False):
    characterSetName: str
    """For supported engines, specifies the character set to associate with the DB instance.

    Default:
        RDS default character set name

    Stability:
        experimental
    """
    kmsKey: aws_cdk.aws_kms.IKey
    """The master key that's used to encrypt the DB instance.

    Default:
        default master key

    Stability:
        experimental
    """
    storageEncrypted: bool
    """Indicates whether the DB instance is encrypted.

    Default:
        false

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.DatabaseInstanceProps", jsii_struct_bases=[_DatabaseInstanceProps])
class DatabaseInstanceProps(_DatabaseInstanceProps):
    """Construction properties for a DatabaseInstance.

    Stability:
        experimental
    """
    masterUsername: str
    """The master user name.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[DatabaseInstanceSourceProps])
class _DatabaseInstanceReadReplicaProps(DatabaseInstanceSourceProps, jsii.compat.TypedDict, total=False):
    kmsKey: aws_cdk.aws_kms.IKey
    """The master key that's used to encrypt the DB instance.

    Default:
        default master key

    Stability:
        experimental
    """
    storageEncrypted: bool
    """Indicates whether the DB instance is encrypted.

    Default:
        false

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.DatabaseInstanceReadReplicaProps", jsii_struct_bases=[_DatabaseInstanceReadReplicaProps])
class DatabaseInstanceReadReplicaProps(_DatabaseInstanceReadReplicaProps):
    """Construction properties for a DatabaseInstanceReadReplica.

    Stability:
        experimental
    """
    sourceDatabaseInstance: "IDatabaseInstance"
    """The source database instance.

    Each DB instance can have a limited number of read replicas. For more
    information, see https://docs.aws.amazon.com/AmazonRDS/latest/DeveloperGuide/USER_ReadRepl.html.

    Stability:
        experimental
    """

class DatabaseSecret(aws_cdk.aws_secretsmanager.Secret, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.DatabaseSecret"):
    """A database secret.

    Stability:
        experimental
    resource:
        AWS::SecretsManager::Secret
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, username: str, encryption_key: typing.Optional[aws_cdk.aws_kms.IKey]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            username: The username.
            encryption_key: The KMS key to use to encrypt the secret. Default: default master key

        Stability:
            experimental
        """
        props: DatabaseSecretProps = {"username": username}

        if encryption_key is not None:
            props["encryptionKey"] = encryption_key

        jsii.create(DatabaseSecret, self, [scope, id, props])


@jsii.data_type_optionals(jsii_struct_bases=[])
class _DatabaseSecretProps(jsii.compat.TypedDict, total=False):
    encryptionKey: aws_cdk.aws_kms.IKey
    """The KMS key to use to encrypt the secret.

    Default:
        default master key

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.DatabaseSecretProps", jsii_struct_bases=[_DatabaseSecretProps])
class DatabaseSecretProps(_DatabaseSecretProps):
    """Construction properties for a DatabaseSecret.

    Stability:
        experimental
    """
    username: str
    """The username.

    Stability:
        experimental
    """

class Endpoint(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.Endpoint"):
    """Connection endpoint of a database cluster or instance.

    Consists of a combination of hostname and port.

    Stability:
        experimental
    """
    def __init__(self, address: str, port: jsii.Number) -> None:
        """
        Arguments:
            address: -
            port: -

        Stability:
            experimental
        """
        jsii.create(Endpoint, self, [address, port])

    @property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> str:
        """The hostname of the endpoint.

        Stability:
            experimental
        """
        return jsii.get(self, "hostname")

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        """The port of the endpoint.

        Stability:
            experimental
        """
        return jsii.get(self, "port")

    @property
    @jsii.member(jsii_name="socketAddress")
    def socket_address(self) -> str:
        """The combination of "HOSTNAME:PORT" for this endpoint.

        Stability:
            experimental
        """
        return jsii.get(self, "socketAddress")


@jsii.interface(jsii_type="@aws-cdk/aws-rds.IDatabaseCluster")
class IDatabaseCluster(aws_cdk.core.IResource, aws_cdk.aws_ec2.IConnectable, aws_cdk.aws_secretsmanager.ISecretAttachmentTarget, jsii.compat.Protocol):
    """Create a clustered database with a given number of instances.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IDatabaseClusterProxy

    @property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> "Endpoint":
        """The endpoint to use for read/write operations.

        Stability:
            experimental
        attribute:
            dbClusterEndpointAddress,dbClusterEndpointPort
        """
        ...

    @property
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> str:
        """Identifier of the cluster.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="clusterReadEndpoint")
    def cluster_read_endpoint(self) -> "Endpoint":
        """Endpoint to use for load-balanced read-only operations.

        Stability:
            experimental
        attribute:
            dbClusterReadEndpointAddress
        """
        ...

    @property
    @jsii.member(jsii_name="instanceEndpoints")
    def instance_endpoints(self) -> typing.List["Endpoint"]:
        """Endpoints which address each individual replica.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="instanceIdentifiers")
    def instance_identifiers(self) -> typing.List[str]:
        """Identifiers of the replicas.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """The security group for this database cluster.

        Stability:
            experimental
        """
        ...


class _IDatabaseClusterProxy(jsii.proxy_for(aws_cdk.core.IResource), jsii.proxy_for(aws_cdk.aws_ec2.IConnectable), jsii.proxy_for(aws_cdk.aws_secretsmanager.ISecretAttachmentTarget)):
    """Create a clustered database with a given number of instances.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-rds.IDatabaseCluster"
    @property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> "Endpoint":
        """The endpoint to use for read/write operations.

        Stability:
            experimental
        attribute:
            dbClusterEndpointAddress,dbClusterEndpointPort
        """
        return jsii.get(self, "clusterEndpoint")

    @property
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> str:
        """Identifier of the cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "clusterIdentifier")

    @property
    @jsii.member(jsii_name="clusterReadEndpoint")
    def cluster_read_endpoint(self) -> "Endpoint":
        """Endpoint to use for load-balanced read-only operations.

        Stability:
            experimental
        attribute:
            dbClusterReadEndpointAddress
        """
        return jsii.get(self, "clusterReadEndpoint")

    @property
    @jsii.member(jsii_name="instanceEndpoints")
    def instance_endpoints(self) -> typing.List["Endpoint"]:
        """Endpoints which address each individual replica.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceEndpoints")

    @property
    @jsii.member(jsii_name="instanceIdentifiers")
    def instance_identifiers(self) -> typing.List[str]:
        """Identifiers of the replicas.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceIdentifiers")

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """The security group for this database cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupId")


@jsii.implements(IDatabaseCluster)
class DatabaseCluster(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.DatabaseCluster"):
    """Create a clustered database with a given number of instances.

    Stability:
        experimental
    resource:
        AWS::RDS::DBCluster
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, engine: "DatabaseClusterEngine", instance_props: "InstanceProps", master_user: "Login", backup: typing.Optional["BackupProps"]=None, cluster_identifier: typing.Optional[str]=None, default_database_name: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, instance_identifier_base: typing.Optional[str]=None, instances: typing.Optional[jsii.Number]=None, kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, parameter_group: typing.Optional["IParameterGroup"]=None, port: typing.Optional[jsii.Number]=None, preferred_maintenance_window: typing.Optional[str]=None, removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy]=None, storage_encrypted: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            engine: What kind of database to start.
            instance_props: Settings for the individual instances that are launched.
            master_user: Username and password for the administrative user.
            backup: Backup settings. Default: - Backup retention period for automated backups is 1 day. Backup preferred window is set to a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
            cluster_identifier: An optional identifier for the cluster. Default: - A name is automatically generated.
            default_database_name: Name of a database which is automatically created inside the cluster. Default: - Database is not created in cluster.
            engine_version: What version of the database to start. Default: - The default for the engine is used.
            instance_identifier_base: Base identifier for instances. Every replica is named by appending the replica number to this string, 1-based. Default: - clusterIdentifier is used with the word "Instance" appended. If clusterIdentifier is not provided, the identifier is automatically generated.
            instances: How many replicas/instances to create. Has to be at least 1. Default: 2
            kms_key: The KMS key for storage encryption. If specified ``storageEncrypted`` will be set to ``true``. Default: - default master key.
            parameter_group: Additional parameters to pass to the database engine. Default: - No parameter group.
            port: What port to listen on. Default: - The default for the engine is used.
            preferred_maintenance_window: A daily time range in 24-hours UTC format in which backups preferably execute. Must be at least 30 minutes long. Example: '01:00-02:00' Default: - 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
            removal_policy: The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update. Default: - Retain cluster.
            storage_encrypted: Whether to enable storage encryption. Default: false

        Stability:
            experimental
        """
        props: DatabaseClusterProps = {"engine": engine, "instanceProps": instance_props, "masterUser": master_user}

        if backup is not None:
            props["backup"] = backup

        if cluster_identifier is not None:
            props["clusterIdentifier"] = cluster_identifier

        if default_database_name is not None:
            props["defaultDatabaseName"] = default_database_name

        if engine_version is not None:
            props["engineVersion"] = engine_version

        if instance_identifier_base is not None:
            props["instanceIdentifierBase"] = instance_identifier_base

        if instances is not None:
            props["instances"] = instances

        if kms_key is not None:
            props["kmsKey"] = kms_key

        if parameter_group is not None:
            props["parameterGroup"] = parameter_group

        if port is not None:
            props["port"] = port

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if removal_policy is not None:
            props["removalPolicy"] = removal_policy

        if storage_encrypted is not None:
            props["storageEncrypted"] = storage_encrypted

        jsii.create(DatabaseCluster, self, [scope, id, props])

    @jsii.member(jsii_name="fromDatabaseClusterAttributes")
    @classmethod
    def from_database_cluster_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, cluster_endpoint_address: str, cluster_identifier: str, instance_endpoint_addresses: typing.List[str], instance_identifiers: typing.List[str], port: jsii.Number, reader_endpoint_address: str, security_group_id: str) -> "IDatabaseCluster":
        """Import an existing DatabaseCluster from properties.

        Arguments:
            scope: -
            id: -
            attrs: -
            cluster_endpoint_address: Cluster endpoint address.
            cluster_identifier: Identifier for the cluster.
            instance_endpoint_addresses: Endpoint addresses of individual instances.
            instance_identifiers: Identifier for the instances.
            port: The database port.
            reader_endpoint_address: Reader endpoint address.
            security_group_id: The security group for this database cluster.

        Stability:
            experimental
        """
        attrs: DatabaseClusterAttributes = {"clusterEndpointAddress": cluster_endpoint_address, "clusterIdentifier": cluster_identifier, "instanceEndpointAddresses": instance_endpoint_addresses, "instanceIdentifiers": instance_identifiers, "port": port, "readerEndpointAddress": reader_endpoint_address, "securityGroupId": security_group_id}

        return jsii.sinvoke(cls, "fromDatabaseClusterAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="addRotationSingleUser")
    def add_rotation_single_user(self, id: str, *, automatically_after: typing.Optional[aws_cdk.core.Duration]=None) -> "SecretRotation":
        """Adds the single user rotation of the master password to this cluster.

        Arguments:
            id: -
            options: -
            automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)

        Stability:
            experimental
        """
        options: SecretRotationOptions = {}

        if automatically_after is not None:
            options["automaticallyAfter"] = automatically_after

        return jsii.invoke(self, "addRotationSingleUser", [id, options])

    @jsii.member(jsii_name="asSecretAttachmentTarget")
    def as_secret_attachment_target(self) -> aws_cdk.aws_secretsmanager.SecretAttachmentTargetProps:
        """Renders the secret attachment target specifications.

        Stability:
            experimental
        """
        return jsii.invoke(self, "asSecretAttachmentTarget", [])

    @property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> "Endpoint":
        """The endpoint to use for read/write operations.

        Stability:
            experimental
        """
        return jsii.get(self, "clusterEndpoint")

    @property
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> str:
        """Identifier of the cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "clusterIdentifier")

    @property
    @jsii.member(jsii_name="clusterReadEndpoint")
    def cluster_read_endpoint(self) -> "Endpoint":
        """Endpoint to use for load-balanced read-only operations.

        Stability:
            experimental
        """
        return jsii.get(self, "clusterReadEndpoint")

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """Access to the network connections.

        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="instanceEndpoints")
    def instance_endpoints(self) -> typing.List["Endpoint"]:
        """Endpoints which address each individual replica.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceEndpoints")

    @property
    @jsii.member(jsii_name="instanceIdentifiers")
    def instance_identifiers(self) -> typing.List[str]:
        """Identifiers of the replicas.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceIdentifiers")

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """Security group identifier of this database.

        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupId")

    @property
    @jsii.member(jsii_name="secret")
    def secret(self) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        """The secret attached to this cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "secret")


@jsii.interface(jsii_type="@aws-cdk/aws-rds.IDatabaseInstance")
class IDatabaseInstance(aws_cdk.core.IResource, aws_cdk.aws_ec2.IConnectable, aws_cdk.aws_secretsmanager.ISecretAttachmentTarget, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IDatabaseInstanceProxy

    @property
    @jsii.member(jsii_name="dbInstanceEndpointAddress")
    def db_instance_endpoint_address(self) -> str:
        """The instance endpoint address.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="dbInstanceEndpointPort")
    def db_instance_endpoint_port(self) -> str:
        """The instance endpoint port.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> str:
        """The instance arn.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="instanceEndpoint")
    def instance_endpoint(self) -> "Endpoint":
        """The instance endpoint.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="instanceIdentifier")
    def instance_identifier(self) -> str:
        """The instance identifier.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """The security group identifier of the instance.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this DBInstance.

        Arguments:
            metric_name: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricCPUUtilization")
    def metric_cpu_utilization(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The percentage of CPU utilization.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricDatabaseConnections")
    def metric_database_connections(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of database connections in use.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricFreeableMemory")
    def metric_freeable_memory(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The amount of available random access memory.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricFreeStorageSpace")
    def metric_free_storage_space(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The amount of available storage space.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricReadIOPS")
    def metric_read_iops(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The average number of disk write I/O operations per second.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricWriteIOPS")
    def metric_write_iops(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The average number of disk read I/O operations per second.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for instance events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        ...


class _IDatabaseInstanceProxy(jsii.proxy_for(aws_cdk.core.IResource), jsii.proxy_for(aws_cdk.aws_ec2.IConnectable), jsii.proxy_for(aws_cdk.aws_secretsmanager.ISecretAttachmentTarget)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-rds.IDatabaseInstance"
    @property
    @jsii.member(jsii_name="dbInstanceEndpointAddress")
    def db_instance_endpoint_address(self) -> str:
        """The instance endpoint address.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "dbInstanceEndpointAddress")

    @property
    @jsii.member(jsii_name="dbInstanceEndpointPort")
    def db_instance_endpoint_port(self) -> str:
        """The instance endpoint port.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "dbInstanceEndpointPort")

    @property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> str:
        """The instance arn.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceArn")

    @property
    @jsii.member(jsii_name="instanceEndpoint")
    def instance_endpoint(self) -> "Endpoint":
        """The instance endpoint.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceEndpoint")

    @property
    @jsii.member(jsii_name="instanceIdentifier")
    def instance_identifier(self) -> str:
        """The instance identifier.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceIdentifier")

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """The security group identifier of the instance.

        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupId")

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this DBInstance.

        Arguments:
            metric_name: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricCPUUtilization")
    def metric_cpu_utilization(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The percentage of CPU utilization.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricCPUUtilization", [props])

    @jsii.member(jsii_name="metricDatabaseConnections")
    def metric_database_connections(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of database connections in use.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricDatabaseConnections", [props])

    @jsii.member(jsii_name="metricFreeableMemory")
    def metric_freeable_memory(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The amount of available random access memory.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricFreeableMemory", [props])

    @jsii.member(jsii_name="metricFreeStorageSpace")
    def metric_free_storage_space(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The amount of available storage space.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricFreeStorageSpace", [props])

    @jsii.member(jsii_name="metricReadIOPS")
    def metric_read_iops(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The average number of disk write I/O operations per second.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricReadIOPS", [props])

    @jsii.member(jsii_name="metricWriteIOPS")
    def metric_write_iops(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The average number of disk read I/O operations per second.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricWriteIOPS", [props])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for instance events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        if target is not None:
            options["target"] = target

        return jsii.invoke(self, "onEvent", [id, options])


@jsii.implements(IDatabaseInstance)
class DatabaseInstanceBase(aws_cdk.core.Resource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-rds.DatabaseInstanceBase"):
    """A new or imported database instance.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _DatabaseInstanceBaseProxy

    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, physical_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time

        Stability:
            experimental
        """
        props: aws_cdk.core.ResourceProps = {}

        if physical_name is not None:
            props["physicalName"] = physical_name

        jsii.create(DatabaseInstanceBase, self, [scope, id, props])

    @jsii.member(jsii_name="fromDatabaseInstanceAttributes")
    @classmethod
    def from_database_instance_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, instance_endpoint_address: str, instance_identifier: str, port: jsii.Number, security_group_id: str) -> "IDatabaseInstance":
        """Import an existing database instance.

        Arguments:
            scope: -
            id: -
            attrs: -
            instance_endpoint_address: The endpoint address.
            instance_identifier: The instance identifier.
            port: The database port.
            security_group_id: The security group identifier of the instance.

        Stability:
            experimental
        """
        attrs: DatabaseInstanceAttributes = {"instanceEndpointAddress": instance_endpoint_address, "instanceIdentifier": instance_identifier, "port": port, "securityGroupId": security_group_id}

        return jsii.sinvoke(cls, "fromDatabaseInstanceAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="asSecretAttachmentTarget")
    def as_secret_attachment_target(self) -> aws_cdk.aws_secretsmanager.SecretAttachmentTargetProps:
        """Renders the secret attachment target specifications.

        Stability:
            experimental
        """
        return jsii.invoke(self, "asSecretAttachmentTarget", [])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this DBInstance.

        Arguments:
            metric_name: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricCPUUtilization")
    def metric_cpu_utilization(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The percentage of CPU utilization.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricCPUUtilization", [props])

    @jsii.member(jsii_name="metricDatabaseConnections")
    def metric_database_connections(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of database connections in use.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricDatabaseConnections", [props])

    @jsii.member(jsii_name="metricFreeableMemory")
    def metric_freeable_memory(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The amount of available random access memory.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricFreeableMemory", [props])

    @jsii.member(jsii_name="metricFreeStorageSpace")
    def metric_free_storage_space(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The amount of available storage space.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricFreeStorageSpace", [props])

    @jsii.member(jsii_name="metricReadIOPS")
    def metric_read_iops(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The average number of disk write I/O operations per second.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricReadIOPS", [props])

    @jsii.member(jsii_name="metricWriteIOPS")
    def metric_write_iops(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period: typing.Optional[aws_cdk.core.Duration]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The average number of disk read I/O operations per second.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period is not None:
            props["period"] = period

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricWriteIOPS", [props])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None, target: typing.Optional[aws_cdk.aws_events.IRuleTarget]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for instance events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
            description: A description of the rule's purpose. Default: - No description
            event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
            rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
            target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        if target is not None:
            options["target"] = target

        return jsii.invoke(self, "onEvent", [id, options])

    @property
    @jsii.member(jsii_name="connections")
    @abc.abstractmethod
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """
        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="dbInstanceEndpointAddress")
    @abc.abstractmethod
    def db_instance_endpoint_address(self) -> str:
        """The instance endpoint address.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="dbInstanceEndpointPort")
    @abc.abstractmethod
    def db_instance_endpoint_port(self) -> str:
        """The instance endpoint port.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> str:
        """The instance arn.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceArn")

    @property
    @jsii.member(jsii_name="instanceEndpoint")
    @abc.abstractmethod
    def instance_endpoint(self) -> "Endpoint":
        """The instance endpoint.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="instanceIdentifier")
    @abc.abstractmethod
    def instance_identifier(self) -> str:
        """The instance identifier.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="securityGroupId")
    @abc.abstractmethod
    def security_group_id(self) -> str:
        """The security group identifier of the instance.

        Stability:
            experimental
        """
        ...


class _DatabaseInstanceBaseProxy(DatabaseInstanceBase, jsii.proxy_for(aws_cdk.core.Resource)):
    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="dbInstanceEndpointAddress")
    def db_instance_endpoint_address(self) -> str:
        """The instance endpoint address.

        Stability:
            experimental
        """
        return jsii.get(self, "dbInstanceEndpointAddress")

    @property
    @jsii.member(jsii_name="dbInstanceEndpointPort")
    def db_instance_endpoint_port(self) -> str:
        """The instance endpoint port.

        Stability:
            experimental
        """
        return jsii.get(self, "dbInstanceEndpointPort")

    @property
    @jsii.member(jsii_name="instanceEndpoint")
    def instance_endpoint(self) -> "Endpoint":
        """The instance endpoint.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceEndpoint")

    @property
    @jsii.member(jsii_name="instanceIdentifier")
    def instance_identifier(self) -> str:
        """The instance identifier.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceIdentifier")

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """The security group identifier of the instance.

        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupId")


@jsii.implements(IDatabaseInstance)
class DatabaseInstance(DatabaseInstanceBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.DatabaseInstance"):
    """A database instance.

    Stability:
        experimental
    resource:
        AWS::RDS::DBInstance
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, master_username: str, character_set_name: typing.Optional[str]=None, kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, storage_encrypted: typing.Optional[bool]=None, engine: "DatabaseInstanceEngine", allocated_storage: typing.Optional[jsii.Number]=None, allow_major_version_upgrade: typing.Optional[bool]=None, database_name: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, license_model: typing.Optional["LicenseModel"]=None, master_user_password: typing.Optional[aws_cdk.core.SecretValue]=None, parameter_group: typing.Optional["IParameterGroup"]=None, secret_kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, timezone: typing.Optional[str]=None, instance_class: aws_cdk.aws_ec2.InstanceType, vpc: aws_cdk.aws_ec2.IVpc, auto_minor_version_upgrade: typing.Optional[bool]=None, availability_zone: typing.Optional[str]=None, backup_retention: typing.Optional[aws_cdk.core.Duration]=None, cloudwatch_logs_exports: typing.Optional[typing.List[str]]=None, cloudwatch_logs_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays]=None, copy_tags_to_snapshot: typing.Optional[bool]=None, delete_automated_backups: typing.Optional[bool]=None, deletion_protection: typing.Optional[bool]=None, enable_performance_insights: typing.Optional[bool]=None, iam_authentication: typing.Optional[bool]=None, instance_identifier: typing.Optional[str]=None, iops: typing.Optional[jsii.Number]=None, monitoring_interval: typing.Optional[aws_cdk.core.Duration]=None, multi_az: typing.Optional[bool]=None, option_group: typing.Optional["IOptionGroup"]=None, performance_insight_kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, performance_insight_retention: typing.Optional["PerformanceInsightRetention"]=None, port: typing.Optional[jsii.Number]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, processor_features: typing.Optional["ProcessorFeatures"]=None, removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy]=None, storage_type: typing.Optional["StorageType"]=None, vpc_placement: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            master_username: The master user name.
            character_set_name: For supported engines, specifies the character set to associate with the DB instance. Default: RDS default character set name
            kms_key: The master key that's used to encrypt the DB instance. Default: default master key
            storage_encrypted: Indicates whether the DB instance is encrypted. Default: false
            engine: The database engine.
            allocated_storage: The allocated storage size, specified in gigabytes (GB). Default: 100
            allow_major_version_upgrade: Whether to allow major version upgrades. Default: false
            database_name: The name of the database. Default: no name
            engine_version: The engine version. To prevent automatic upgrades, be sure to specify the full version number. Default: RDS default engine version
            license_model: The license model. Default: RDS default license model
            master_user_password: The master user password. Default: a Secrets Manager generated password
            parameter_group: The DB parameter group to associate with the instance. Default: no parameter group
            secret_kms_key: The KMS key to use to encrypt the secret for the master user password. Default: default master key
            timezone: The time zone of the instance. Default: RDS default timezone
            instance_class: The name of the compute and memory capacity classes.
            vpc: The VPC network where the DB subnet group should be created.
            auto_minor_version_upgrade: Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window. Default: true
            availability_zone: The name of the Availability Zone where the DB instance will be located. Default: no preference
            backup_retention: The number of days during which automatic DB snapshots are retained. Set to zero to disable backups. Default: 1 day
            cloudwatch_logs_exports: The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: no log exports
            cloudwatch_logs_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: logs never expire
            copy_tags_to_snapshot: Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance. Default: true
            delete_automated_backups: Indicates whether automated backups should be deleted or retained when you delete a DB instance. Default: false
            deletion_protection: Indicates whether the DB instance should have deletion protection enabled. Default: true
            enable_performance_insights: Whether to enable Performance Insights for the DB instance. Default: false
            iam_authentication: Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. Default: false
            instance_identifier: A name for the DB instance. If you specify a name, AWS CloudFormation converts it to lowercase. Default: a CloudFormation generated name
            iops: The number of I/O operations per second (IOPS) that the database provisions. The value must be equal to or greater than 1000. Default: no provisioned iops
            monitoring_interval: The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance. Default: no enhanced monitoring
            multi_az: Specifies if the database instance is a multiple Availability Zone deployment. Default: false
            option_group: The option group to associate with the instance. Default: no option group
            performance_insight_kms_key: The AWS KMS key for encryption of Performance Insights data. Default: default master key
            performance_insight_retention: The amount of time, in days, to retain Performance Insights data. Default: 7 days
            port: The port for the instance. Default: the default port for the chosen engine.
            preferred_backup_window: The daily time range during which automated backups are performed. Constraints: - Must be in the format ``hh24:mi-hh24:mi``. - Must be in Universal Coordinated Time (UTC). - Must not conflict with the preferred maintenance window. - Must be at least 30 minutes. Default: a 30-minute window selected at random from an 8-hour block of time for each AWS Region. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow
            preferred_maintenance_window: The weekly time range (in UTC) during which system maintenance can occur. Format: ``ddd:hh24:mi-ddd:hh24:mi`` Constraint: Minimum 30-minute window Default: a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow
            processor_features: The number of CPU cores and the number of threads per core. Default: the default number of CPU cores and threads per core for the chosen instance class. See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#USER_ConfigureProcessor
            removal_policy: The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update. Default: RemovalPolicy.Retain
            storage_type: The storage type. Default: GP2
            vpc_placement: The type of subnets to add to the created DB subnet group. Default: private

        Stability:
            experimental
        """
        props: DatabaseInstanceProps = {"masterUsername": master_username, "engine": engine, "instanceClass": instance_class, "vpc": vpc}

        if character_set_name is not None:
            props["characterSetName"] = character_set_name

        if kms_key is not None:
            props["kmsKey"] = kms_key

        if storage_encrypted is not None:
            props["storageEncrypted"] = storage_encrypted

        if allocated_storage is not None:
            props["allocatedStorage"] = allocated_storage

        if allow_major_version_upgrade is not None:
            props["allowMajorVersionUpgrade"] = allow_major_version_upgrade

        if database_name is not None:
            props["databaseName"] = database_name

        if engine_version is not None:
            props["engineVersion"] = engine_version

        if license_model is not None:
            props["licenseModel"] = license_model

        if master_user_password is not None:
            props["masterUserPassword"] = master_user_password

        if parameter_group is not None:
            props["parameterGroup"] = parameter_group

        if secret_kms_key is not None:
            props["secretKmsKey"] = secret_kms_key

        if timezone is not None:
            props["timezone"] = timezone

        if auto_minor_version_upgrade is not None:
            props["autoMinorVersionUpgrade"] = auto_minor_version_upgrade

        if availability_zone is not None:
            props["availabilityZone"] = availability_zone

        if backup_retention is not None:
            props["backupRetention"] = backup_retention

        if cloudwatch_logs_exports is not None:
            props["cloudwatchLogsExports"] = cloudwatch_logs_exports

        if cloudwatch_logs_retention is not None:
            props["cloudwatchLogsRetention"] = cloudwatch_logs_retention

        if copy_tags_to_snapshot is not None:
            props["copyTagsToSnapshot"] = copy_tags_to_snapshot

        if delete_automated_backups is not None:
            props["deleteAutomatedBackups"] = delete_automated_backups

        if deletion_protection is not None:
            props["deletionProtection"] = deletion_protection

        if enable_performance_insights is not None:
            props["enablePerformanceInsights"] = enable_performance_insights

        if iam_authentication is not None:
            props["iamAuthentication"] = iam_authentication

        if instance_identifier is not None:
            props["instanceIdentifier"] = instance_identifier

        if iops is not None:
            props["iops"] = iops

        if monitoring_interval is not None:
            props["monitoringInterval"] = monitoring_interval

        if multi_az is not None:
            props["multiAz"] = multi_az

        if option_group is not None:
            props["optionGroup"] = option_group

        if performance_insight_kms_key is not None:
            props["performanceInsightKmsKey"] = performance_insight_kms_key

        if performance_insight_retention is not None:
            props["performanceInsightRetention"] = performance_insight_retention

        if port is not None:
            props["port"] = port

        if preferred_backup_window is not None:
            props["preferredBackupWindow"] = preferred_backup_window

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if processor_features is not None:
            props["processorFeatures"] = processor_features

        if removal_policy is not None:
            props["removalPolicy"] = removal_policy

        if storage_type is not None:
            props["storageType"] = storage_type

        if vpc_placement is not None:
            props["vpcPlacement"] = vpc_placement

        jsii.create(DatabaseInstance, self, [scope, id, props])

    @jsii.member(jsii_name="addRotationSingleUser")
    def add_rotation_single_user(self, id: str, *, automatically_after: typing.Optional[aws_cdk.core.Duration]=None) -> "SecretRotation":
        """Adds the single user rotation of the master password to this instance.

        Arguments:
            id: -
            options: -
            automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)

        Stability:
            experimental
        """
        options: SecretRotationOptions = {}

        if automatically_after is not None:
            options["automaticallyAfter"] = automatically_after

        return jsii.invoke(self, "addRotationSingleUser", [id, options])

    @jsii.member(jsii_name="setLogRetention")
    def _set_log_retention(self) -> None:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "setLogRetention", [])

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="dbInstanceEndpointAddress")
    def db_instance_endpoint_address(self) -> str:
        """The instance endpoint address.

        Stability:
            experimental
        """
        return jsii.get(self, "dbInstanceEndpointAddress")

    @property
    @jsii.member(jsii_name="dbInstanceEndpointPort")
    def db_instance_endpoint_port(self) -> str:
        """The instance endpoint port.

        Stability:
            experimental
        """
        return jsii.get(self, "dbInstanceEndpointPort")

    @property
    @jsii.member(jsii_name="instanceEndpoint")
    def instance_endpoint(self) -> "Endpoint":
        """The instance endpoint.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceEndpoint")

    @property
    @jsii.member(jsii_name="instanceIdentifier")
    def instance_identifier(self) -> str:
        """The instance identifier.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceIdentifier")

    @property
    @jsii.member(jsii_name="newCfnProps")
    def _new_cfn_props(self) -> "CfnDBInstanceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "newCfnProps")

    @property
    @jsii.member(jsii_name="securityGroup")
    def _security_group(self) -> aws_cdk.aws_ec2.SecurityGroup:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroup")

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """The security group identifier of the instance.

        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupId")

    @property
    @jsii.member(jsii_name="sourceCfnProps")
    def _source_cfn_props(self) -> "CfnDBInstanceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "sourceCfnProps")

    @property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpc")

    @property
    @jsii.member(jsii_name="secret")
    def secret(self) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "secret")

    @property
    @jsii.member(jsii_name="vpcPlacement")
    def _vpc_placement(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpcPlacement")


@jsii.implements(IDatabaseInstance)
class DatabaseInstanceFromSnapshot(DatabaseInstanceBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.DatabaseInstanceFromSnapshot"):
    """A database instance restored from a snapshot.

    Stability:
        experimental
    resource:
        AWS::RDS::DBInstance
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, snapshot_identifier: str, generate_master_user_password: typing.Optional[bool]=None, master_username: typing.Optional[str]=None, engine: "DatabaseInstanceEngine", allocated_storage: typing.Optional[jsii.Number]=None, allow_major_version_upgrade: typing.Optional[bool]=None, database_name: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, license_model: typing.Optional["LicenseModel"]=None, master_user_password: typing.Optional[aws_cdk.core.SecretValue]=None, parameter_group: typing.Optional["IParameterGroup"]=None, secret_kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, timezone: typing.Optional[str]=None, instance_class: aws_cdk.aws_ec2.InstanceType, vpc: aws_cdk.aws_ec2.IVpc, auto_minor_version_upgrade: typing.Optional[bool]=None, availability_zone: typing.Optional[str]=None, backup_retention: typing.Optional[aws_cdk.core.Duration]=None, cloudwatch_logs_exports: typing.Optional[typing.List[str]]=None, cloudwatch_logs_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays]=None, copy_tags_to_snapshot: typing.Optional[bool]=None, delete_automated_backups: typing.Optional[bool]=None, deletion_protection: typing.Optional[bool]=None, enable_performance_insights: typing.Optional[bool]=None, iam_authentication: typing.Optional[bool]=None, instance_identifier: typing.Optional[str]=None, iops: typing.Optional[jsii.Number]=None, monitoring_interval: typing.Optional[aws_cdk.core.Duration]=None, multi_az: typing.Optional[bool]=None, option_group: typing.Optional["IOptionGroup"]=None, performance_insight_kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, performance_insight_retention: typing.Optional["PerformanceInsightRetention"]=None, port: typing.Optional[jsii.Number]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, processor_features: typing.Optional["ProcessorFeatures"]=None, removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy]=None, storage_type: typing.Optional["StorageType"]=None, vpc_placement: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            snapshot_identifier: The name or Amazon Resource Name (ARN) of the DB snapshot that's used to restore the DB instance. If you're restoring from a shared manual DB snapshot, you must specify the ARN of the snapshot.
            generate_master_user_password: Whether to generate a new master user password and store it in Secrets Manager. ``masterUsername`` must be specified when this property is set to true. Default: false
            master_username: The master user name. Default: inherited from the snapshot
            engine: The database engine.
            allocated_storage: The allocated storage size, specified in gigabytes (GB). Default: 100
            allow_major_version_upgrade: Whether to allow major version upgrades. Default: false
            database_name: The name of the database. Default: no name
            engine_version: The engine version. To prevent automatic upgrades, be sure to specify the full version number. Default: RDS default engine version
            license_model: The license model. Default: RDS default license model
            master_user_password: The master user password. Default: a Secrets Manager generated password
            parameter_group: The DB parameter group to associate with the instance. Default: no parameter group
            secret_kms_key: The KMS key to use to encrypt the secret for the master user password. Default: default master key
            timezone: The time zone of the instance. Default: RDS default timezone
            instance_class: The name of the compute and memory capacity classes.
            vpc: The VPC network where the DB subnet group should be created.
            auto_minor_version_upgrade: Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window. Default: true
            availability_zone: The name of the Availability Zone where the DB instance will be located. Default: no preference
            backup_retention: The number of days during which automatic DB snapshots are retained. Set to zero to disable backups. Default: 1 day
            cloudwatch_logs_exports: The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: no log exports
            cloudwatch_logs_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: logs never expire
            copy_tags_to_snapshot: Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance. Default: true
            delete_automated_backups: Indicates whether automated backups should be deleted or retained when you delete a DB instance. Default: false
            deletion_protection: Indicates whether the DB instance should have deletion protection enabled. Default: true
            enable_performance_insights: Whether to enable Performance Insights for the DB instance. Default: false
            iam_authentication: Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. Default: false
            instance_identifier: A name for the DB instance. If you specify a name, AWS CloudFormation converts it to lowercase. Default: a CloudFormation generated name
            iops: The number of I/O operations per second (IOPS) that the database provisions. The value must be equal to or greater than 1000. Default: no provisioned iops
            monitoring_interval: The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance. Default: no enhanced monitoring
            multi_az: Specifies if the database instance is a multiple Availability Zone deployment. Default: false
            option_group: The option group to associate with the instance. Default: no option group
            performance_insight_kms_key: The AWS KMS key for encryption of Performance Insights data. Default: default master key
            performance_insight_retention: The amount of time, in days, to retain Performance Insights data. Default: 7 days
            port: The port for the instance. Default: the default port for the chosen engine.
            preferred_backup_window: The daily time range during which automated backups are performed. Constraints: - Must be in the format ``hh24:mi-hh24:mi``. - Must be in Universal Coordinated Time (UTC). - Must not conflict with the preferred maintenance window. - Must be at least 30 minutes. Default: a 30-minute window selected at random from an 8-hour block of time for each AWS Region. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow
            preferred_maintenance_window: The weekly time range (in UTC) during which system maintenance can occur. Format: ``ddd:hh24:mi-ddd:hh24:mi`` Constraint: Minimum 30-minute window Default: a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow
            processor_features: The number of CPU cores and the number of threads per core. Default: the default number of CPU cores and threads per core for the chosen instance class. See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#USER_ConfigureProcessor
            removal_policy: The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update. Default: RemovalPolicy.Retain
            storage_type: The storage type. Default: GP2
            vpc_placement: The type of subnets to add to the created DB subnet group. Default: private

        Stability:
            experimental
        """
        props: DatabaseInstanceFromSnapshotProps = {"snapshotIdentifier": snapshot_identifier, "engine": engine, "instanceClass": instance_class, "vpc": vpc}

        if generate_master_user_password is not None:
            props["generateMasterUserPassword"] = generate_master_user_password

        if master_username is not None:
            props["masterUsername"] = master_username

        if allocated_storage is not None:
            props["allocatedStorage"] = allocated_storage

        if allow_major_version_upgrade is not None:
            props["allowMajorVersionUpgrade"] = allow_major_version_upgrade

        if database_name is not None:
            props["databaseName"] = database_name

        if engine_version is not None:
            props["engineVersion"] = engine_version

        if license_model is not None:
            props["licenseModel"] = license_model

        if master_user_password is not None:
            props["masterUserPassword"] = master_user_password

        if parameter_group is not None:
            props["parameterGroup"] = parameter_group

        if secret_kms_key is not None:
            props["secretKmsKey"] = secret_kms_key

        if timezone is not None:
            props["timezone"] = timezone

        if auto_minor_version_upgrade is not None:
            props["autoMinorVersionUpgrade"] = auto_minor_version_upgrade

        if availability_zone is not None:
            props["availabilityZone"] = availability_zone

        if backup_retention is not None:
            props["backupRetention"] = backup_retention

        if cloudwatch_logs_exports is not None:
            props["cloudwatchLogsExports"] = cloudwatch_logs_exports

        if cloudwatch_logs_retention is not None:
            props["cloudwatchLogsRetention"] = cloudwatch_logs_retention

        if copy_tags_to_snapshot is not None:
            props["copyTagsToSnapshot"] = copy_tags_to_snapshot

        if delete_automated_backups is not None:
            props["deleteAutomatedBackups"] = delete_automated_backups

        if deletion_protection is not None:
            props["deletionProtection"] = deletion_protection

        if enable_performance_insights is not None:
            props["enablePerformanceInsights"] = enable_performance_insights

        if iam_authentication is not None:
            props["iamAuthentication"] = iam_authentication

        if instance_identifier is not None:
            props["instanceIdentifier"] = instance_identifier

        if iops is not None:
            props["iops"] = iops

        if monitoring_interval is not None:
            props["monitoringInterval"] = monitoring_interval

        if multi_az is not None:
            props["multiAz"] = multi_az

        if option_group is not None:
            props["optionGroup"] = option_group

        if performance_insight_kms_key is not None:
            props["performanceInsightKmsKey"] = performance_insight_kms_key

        if performance_insight_retention is not None:
            props["performanceInsightRetention"] = performance_insight_retention

        if port is not None:
            props["port"] = port

        if preferred_backup_window is not None:
            props["preferredBackupWindow"] = preferred_backup_window

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if processor_features is not None:
            props["processorFeatures"] = processor_features

        if removal_policy is not None:
            props["removalPolicy"] = removal_policy

        if storage_type is not None:
            props["storageType"] = storage_type

        if vpc_placement is not None:
            props["vpcPlacement"] = vpc_placement

        jsii.create(DatabaseInstanceFromSnapshot, self, [scope, id, props])

    @jsii.member(jsii_name="addRotationSingleUser")
    def add_rotation_single_user(self, id: str, *, automatically_after: typing.Optional[aws_cdk.core.Duration]=None) -> "SecretRotation":
        """Adds the single user rotation of the master password to this instance.

        Arguments:
            id: -
            options: -
            automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)

        Stability:
            experimental
        """
        options: SecretRotationOptions = {}

        if automatically_after is not None:
            options["automaticallyAfter"] = automatically_after

        return jsii.invoke(self, "addRotationSingleUser", [id, options])

    @jsii.member(jsii_name="setLogRetention")
    def _set_log_retention(self) -> None:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "setLogRetention", [])

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="dbInstanceEndpointAddress")
    def db_instance_endpoint_address(self) -> str:
        """The instance endpoint address.

        Stability:
            experimental
        """
        return jsii.get(self, "dbInstanceEndpointAddress")

    @property
    @jsii.member(jsii_name="dbInstanceEndpointPort")
    def db_instance_endpoint_port(self) -> str:
        """The instance endpoint port.

        Stability:
            experimental
        """
        return jsii.get(self, "dbInstanceEndpointPort")

    @property
    @jsii.member(jsii_name="instanceEndpoint")
    def instance_endpoint(self) -> "Endpoint":
        """The instance endpoint.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceEndpoint")

    @property
    @jsii.member(jsii_name="instanceIdentifier")
    def instance_identifier(self) -> str:
        """The instance identifier.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceIdentifier")

    @property
    @jsii.member(jsii_name="newCfnProps")
    def _new_cfn_props(self) -> "CfnDBInstanceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "newCfnProps")

    @property
    @jsii.member(jsii_name="securityGroup")
    def _security_group(self) -> aws_cdk.aws_ec2.SecurityGroup:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroup")

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """The security group identifier of the instance.

        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupId")

    @property
    @jsii.member(jsii_name="sourceCfnProps")
    def _source_cfn_props(self) -> "CfnDBInstanceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "sourceCfnProps")

    @property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpc")

    @property
    @jsii.member(jsii_name="secret")
    def secret(self) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "secret")

    @property
    @jsii.member(jsii_name="vpcPlacement")
    def _vpc_placement(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpcPlacement")


@jsii.implements(IDatabaseInstance)
class DatabaseInstanceReadReplica(DatabaseInstanceBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.DatabaseInstanceReadReplica"):
    """A read replica database instance.

    Stability:
        experimental
    resource:
        AWS::RDS::DBInstance
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, source_database_instance: "IDatabaseInstance", kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, storage_encrypted: typing.Optional[bool]=None, engine: "DatabaseInstanceEngine", allocated_storage: typing.Optional[jsii.Number]=None, allow_major_version_upgrade: typing.Optional[bool]=None, database_name: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, license_model: typing.Optional["LicenseModel"]=None, master_user_password: typing.Optional[aws_cdk.core.SecretValue]=None, parameter_group: typing.Optional["IParameterGroup"]=None, secret_kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, timezone: typing.Optional[str]=None, instance_class: aws_cdk.aws_ec2.InstanceType, vpc: aws_cdk.aws_ec2.IVpc, auto_minor_version_upgrade: typing.Optional[bool]=None, availability_zone: typing.Optional[str]=None, backup_retention: typing.Optional[aws_cdk.core.Duration]=None, cloudwatch_logs_exports: typing.Optional[typing.List[str]]=None, cloudwatch_logs_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays]=None, copy_tags_to_snapshot: typing.Optional[bool]=None, delete_automated_backups: typing.Optional[bool]=None, deletion_protection: typing.Optional[bool]=None, enable_performance_insights: typing.Optional[bool]=None, iam_authentication: typing.Optional[bool]=None, instance_identifier: typing.Optional[str]=None, iops: typing.Optional[jsii.Number]=None, monitoring_interval: typing.Optional[aws_cdk.core.Duration]=None, multi_az: typing.Optional[bool]=None, option_group: typing.Optional["IOptionGroup"]=None, performance_insight_kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, performance_insight_retention: typing.Optional["PerformanceInsightRetention"]=None, port: typing.Optional[jsii.Number]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, processor_features: typing.Optional["ProcessorFeatures"]=None, removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy]=None, storage_type: typing.Optional["StorageType"]=None, vpc_placement: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            source_database_instance: The source database instance. Each DB instance can have a limited number of read replicas. For more information, see https://docs.aws.amazon.com/AmazonRDS/latest/DeveloperGuide/USER_ReadRepl.html.
            kms_key: The master key that's used to encrypt the DB instance. Default: default master key
            storage_encrypted: Indicates whether the DB instance is encrypted. Default: false
            engine: The database engine.
            allocated_storage: The allocated storage size, specified in gigabytes (GB). Default: 100
            allow_major_version_upgrade: Whether to allow major version upgrades. Default: false
            database_name: The name of the database. Default: no name
            engine_version: The engine version. To prevent automatic upgrades, be sure to specify the full version number. Default: RDS default engine version
            license_model: The license model. Default: RDS default license model
            master_user_password: The master user password. Default: a Secrets Manager generated password
            parameter_group: The DB parameter group to associate with the instance. Default: no parameter group
            secret_kms_key: The KMS key to use to encrypt the secret for the master user password. Default: default master key
            timezone: The time zone of the instance. Default: RDS default timezone
            instance_class: The name of the compute and memory capacity classes.
            vpc: The VPC network where the DB subnet group should be created.
            auto_minor_version_upgrade: Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window. Default: true
            availability_zone: The name of the Availability Zone where the DB instance will be located. Default: no preference
            backup_retention: The number of days during which automatic DB snapshots are retained. Set to zero to disable backups. Default: 1 day
            cloudwatch_logs_exports: The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: no log exports
            cloudwatch_logs_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: logs never expire
            copy_tags_to_snapshot: Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance. Default: true
            delete_automated_backups: Indicates whether automated backups should be deleted or retained when you delete a DB instance. Default: false
            deletion_protection: Indicates whether the DB instance should have deletion protection enabled. Default: true
            enable_performance_insights: Whether to enable Performance Insights for the DB instance. Default: false
            iam_authentication: Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. Default: false
            instance_identifier: A name for the DB instance. If you specify a name, AWS CloudFormation converts it to lowercase. Default: a CloudFormation generated name
            iops: The number of I/O operations per second (IOPS) that the database provisions. The value must be equal to or greater than 1000. Default: no provisioned iops
            monitoring_interval: The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance. Default: no enhanced monitoring
            multi_az: Specifies if the database instance is a multiple Availability Zone deployment. Default: false
            option_group: The option group to associate with the instance. Default: no option group
            performance_insight_kms_key: The AWS KMS key for encryption of Performance Insights data. Default: default master key
            performance_insight_retention: The amount of time, in days, to retain Performance Insights data. Default: 7 days
            port: The port for the instance. Default: the default port for the chosen engine.
            preferred_backup_window: The daily time range during which automated backups are performed. Constraints: - Must be in the format ``hh24:mi-hh24:mi``. - Must be in Universal Coordinated Time (UTC). - Must not conflict with the preferred maintenance window. - Must be at least 30 minutes. Default: a 30-minute window selected at random from an 8-hour block of time for each AWS Region. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow
            preferred_maintenance_window: The weekly time range (in UTC) during which system maintenance can occur. Format: ``ddd:hh24:mi-ddd:hh24:mi`` Constraint: Minimum 30-minute window Default: a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow
            processor_features: The number of CPU cores and the number of threads per core. Default: the default number of CPU cores and threads per core for the chosen instance class. See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#USER_ConfigureProcessor
            removal_policy: The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update. Default: RemovalPolicy.Retain
            storage_type: The storage type. Default: GP2
            vpc_placement: The type of subnets to add to the created DB subnet group. Default: private

        Stability:
            experimental
        """
        props: DatabaseInstanceReadReplicaProps = {"sourceDatabaseInstance": source_database_instance, "engine": engine, "instanceClass": instance_class, "vpc": vpc}

        if kms_key is not None:
            props["kmsKey"] = kms_key

        if storage_encrypted is not None:
            props["storageEncrypted"] = storage_encrypted

        if allocated_storage is not None:
            props["allocatedStorage"] = allocated_storage

        if allow_major_version_upgrade is not None:
            props["allowMajorVersionUpgrade"] = allow_major_version_upgrade

        if database_name is not None:
            props["databaseName"] = database_name

        if engine_version is not None:
            props["engineVersion"] = engine_version

        if license_model is not None:
            props["licenseModel"] = license_model

        if master_user_password is not None:
            props["masterUserPassword"] = master_user_password

        if parameter_group is not None:
            props["parameterGroup"] = parameter_group

        if secret_kms_key is not None:
            props["secretKmsKey"] = secret_kms_key

        if timezone is not None:
            props["timezone"] = timezone

        if auto_minor_version_upgrade is not None:
            props["autoMinorVersionUpgrade"] = auto_minor_version_upgrade

        if availability_zone is not None:
            props["availabilityZone"] = availability_zone

        if backup_retention is not None:
            props["backupRetention"] = backup_retention

        if cloudwatch_logs_exports is not None:
            props["cloudwatchLogsExports"] = cloudwatch_logs_exports

        if cloudwatch_logs_retention is not None:
            props["cloudwatchLogsRetention"] = cloudwatch_logs_retention

        if copy_tags_to_snapshot is not None:
            props["copyTagsToSnapshot"] = copy_tags_to_snapshot

        if delete_automated_backups is not None:
            props["deleteAutomatedBackups"] = delete_automated_backups

        if deletion_protection is not None:
            props["deletionProtection"] = deletion_protection

        if enable_performance_insights is not None:
            props["enablePerformanceInsights"] = enable_performance_insights

        if iam_authentication is not None:
            props["iamAuthentication"] = iam_authentication

        if instance_identifier is not None:
            props["instanceIdentifier"] = instance_identifier

        if iops is not None:
            props["iops"] = iops

        if monitoring_interval is not None:
            props["monitoringInterval"] = monitoring_interval

        if multi_az is not None:
            props["multiAz"] = multi_az

        if option_group is not None:
            props["optionGroup"] = option_group

        if performance_insight_kms_key is not None:
            props["performanceInsightKmsKey"] = performance_insight_kms_key

        if performance_insight_retention is not None:
            props["performanceInsightRetention"] = performance_insight_retention

        if port is not None:
            props["port"] = port

        if preferred_backup_window is not None:
            props["preferredBackupWindow"] = preferred_backup_window

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if processor_features is not None:
            props["processorFeatures"] = processor_features

        if removal_policy is not None:
            props["removalPolicy"] = removal_policy

        if storage_type is not None:
            props["storageType"] = storage_type

        if vpc_placement is not None:
            props["vpcPlacement"] = vpc_placement

        jsii.create(DatabaseInstanceReadReplica, self, [scope, id, props])

    @jsii.member(jsii_name="setLogRetention")
    def _set_log_retention(self) -> None:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "setLogRetention", [])

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="dbInstanceEndpointAddress")
    def db_instance_endpoint_address(self) -> str:
        """The instance endpoint address.

        Stability:
            experimental
        """
        return jsii.get(self, "dbInstanceEndpointAddress")

    @property
    @jsii.member(jsii_name="dbInstanceEndpointPort")
    def db_instance_endpoint_port(self) -> str:
        """The instance endpoint port.

        Stability:
            experimental
        """
        return jsii.get(self, "dbInstanceEndpointPort")

    @property
    @jsii.member(jsii_name="instanceEndpoint")
    def instance_endpoint(self) -> "Endpoint":
        """The instance endpoint.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceEndpoint")

    @property
    @jsii.member(jsii_name="instanceIdentifier")
    def instance_identifier(self) -> str:
        """The instance identifier.

        Stability:
            experimental
        """
        return jsii.get(self, "instanceIdentifier")

    @property
    @jsii.member(jsii_name="newCfnProps")
    def _new_cfn_props(self) -> "CfnDBInstanceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "newCfnProps")

    @property
    @jsii.member(jsii_name="securityGroup")
    def _security_group(self) -> aws_cdk.aws_ec2.SecurityGroup:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "securityGroup")

    @property
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> str:
        """The security group identifier of the instance.

        Stability:
            experimental
        """
        return jsii.get(self, "securityGroupId")

    @property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpc")

    @property
    @jsii.member(jsii_name="vpcPlacement")
    def _vpc_placement(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "vpcPlacement")


@jsii.interface(jsii_type="@aws-cdk/aws-rds.IOptionGroup")
class IOptionGroup(aws_cdk.core.IResource, jsii.compat.Protocol):
    """An option group.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IOptionGroupProxy

    @property
    @jsii.member(jsii_name="optionGroupName")
    def option_group_name(self) -> str:
        """The name of the option group.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IOptionGroupProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """An option group.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-rds.IOptionGroup"
    @property
    @jsii.member(jsii_name="optionGroupName")
    def option_group_name(self) -> str:
        """The name of the option group.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "optionGroupName")


@jsii.interface(jsii_type="@aws-cdk/aws-rds.IParameterGroup")
class IParameterGroup(aws_cdk.core.IResource, jsii.compat.Protocol):
    """A parameter group.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IParameterGroupProxy

    @property
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> str:
        """The name of this parameter group.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IParameterGroupProxy(jsii.proxy_for(aws_cdk.core.IResource)):
    """A parameter group.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-rds.IParameterGroup"
    @property
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> str:
        """The name of this parameter group.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "parameterGroupName")


@jsii.implements(IParameterGroup)
class ClusterParameterGroup(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.ClusterParameterGroup"):
    """A cluster parameter group.

    Stability:
        experimental
    resource:
        AWS::RDS::DBClusterParameterGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, family: str, parameters: typing.Mapping[str,str], description: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            family: Database family of this parameter group.
            parameters: The parameters in this parameter group.
            description: Description for this parameter group. Default: a CDK generated description

        Stability:
            experimental
        """
        props: ClusterParameterGroupProps = {"family": family, "parameters": parameters}

        if description is not None:
            props["description"] = description

        jsii.create(ClusterParameterGroup, self, [scope, id, props])

    @jsii.member(jsii_name="fromParameterGroupName")
    @classmethod
    def from_parameter_group_name(cls, scope: aws_cdk.core.Construct, id: str, parameter_group_name: str) -> "IParameterGroup":
        """Imports a parameter group.

        Arguments:
            scope: -
            id: -
            parameter_group_name: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromParameterGroupName", [scope, id, parameter_group_name])

    @property
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> str:
        """The name of the parameter group.

        Stability:
            experimental
        """
        return jsii.get(self, "parameterGroupName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _InstanceProps(jsii.compat.TypedDict, total=False):
    parameterGroup: "IParameterGroup"
    """The DB parameter group to associate with the instance.

    Default:
        no parameter group

    Stability:
        experimental
    """
    securityGroup: aws_cdk.aws_ec2.ISecurityGroup
    """Security group.

    Default:
        a new security group is created.

    Stability:
        experimental
    """
    vpcSubnets: aws_cdk.aws_ec2.SubnetSelection
    """Where to place the instances within the VPC.

    Default:
        private subnets

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.InstanceProps", jsii_struct_bases=[_InstanceProps])
class InstanceProps(_InstanceProps):
    """Instance properties for database instances.

    Stability:
        experimental
    """
    instanceType: aws_cdk.aws_ec2.InstanceType
    """What type of instance to start for the replicas.

    Stability:
        experimental
    """

    vpc: aws_cdk.aws_ec2.IVpc
    """What subnets to run the RDS instances in.

    Must be at least 2 subnets in two different AZs.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-rds.LicenseModel")
class LicenseModel(enum.Enum):
    """The license model.

    Stability:
        experimental
    """
    LICENSE_INCLUDED = "LICENSE_INCLUDED"
    """License included.

    Stability:
        experimental
    """
    BRING_YOUR_OWN_LICENSE = "BRING_YOUR_OWN_LICENSE"
    """Bring your own licencse.

    Stability:
        experimental
    """
    GENERAL_PUBLIC_LICENSE = "GENERAL_PUBLIC_LICENSE"
    """General public license.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _Login(jsii.compat.TypedDict, total=False):
    kmsKey: aws_cdk.aws_kms.IKey
    """KMS encryption key to encrypt the generated secret.

    Default:
        default master key

    Stability:
        experimental
    """
    password: aws_cdk.core.SecretValue
    """Password.

    Do not put passwords in your CDK code directly.

    Default:
        a Secrets Manager generated password

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.Login", jsii_struct_bases=[_Login])
class Login(_Login):
    """Username and password combination.

    Stability:
        experimental
    """
    username: str
    """Username.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _OptionConfiguration(jsii.compat.TypedDict, total=False):
    port: jsii.Number
    """The port number that this option uses.

    If ``port`` is specified then ``vpc``
    must also be specified.

    Default:
        no port

    Stability:
        experimental
    """
    settings: typing.Mapping[str,str]
    """The settings for the option.

    Default:
        no settings

    Stability:
        experimental
    """
    version: str
    """The version for the option.

    Default:
        no version

    Stability:
        experimental
    """
    vpc: aws_cdk.aws_ec2.IVpc
    """The VPC where a security group should be created for this option.

    If ``vpc``
    is specified then ``port`` must also be specified.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.OptionConfiguration", jsii_struct_bases=[_OptionConfiguration])
class OptionConfiguration(_OptionConfiguration):
    """Configuration properties for an option.

    Stability:
        experimental
    """
    name: str
    """The name of the option.

    Stability:
        experimental
    """

@jsii.implements(IOptionGroup)
class OptionGroup(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.OptionGroup"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, configurations: typing.List["OptionConfiguration"], engine: "DatabaseInstanceEngine", major_engine_version: str, description: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            configurations: The configurations for this option group.
            engine: The database engine that this option group is associated with.
            major_engine_version: The major version number of the database engine that this option group is associated with.
            description: A description of the option group. Default: a CDK generated description

        Stability:
            experimental
        """
        props: OptionGroupProps = {"configurations": configurations, "engine": engine, "majorEngineVersion": major_engine_version}

        if description is not None:
            props["description"] = description

        jsii.create(OptionGroup, self, [scope, id, props])

    @jsii.member(jsii_name="fromOptionGroupName")
    @classmethod
    def from_option_group_name(cls, scope: aws_cdk.core.Construct, id: str, option_group_name: str) -> "IOptionGroup":
        """Import an existing option group.

        Arguments:
            scope: -
            id: -
            option_group_name: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromOptionGroupName", [scope, id, option_group_name])

    @property
    @jsii.member(jsii_name="optionConnections")
    def option_connections(self) -> typing.Mapping[str,aws_cdk.aws_ec2.Connections]:
        """The connections object for the options.

        Stability:
            experimental
        """
        return jsii.get(self, "optionConnections")

    @property
    @jsii.member(jsii_name="optionGroupName")
    def option_group_name(self) -> str:
        """The name of the option group.

        Stability:
            experimental
        """
        return jsii.get(self, "optionGroupName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _OptionGroupProps(jsii.compat.TypedDict, total=False):
    description: str
    """A description of the option group.

    Default:
        a CDK generated description

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.OptionGroupProps", jsii_struct_bases=[_OptionGroupProps])
class OptionGroupProps(_OptionGroupProps):
    """Construction properties for an OptionGroup.

    Stability:
        experimental
    """
    configurations: typing.List["OptionConfiguration"]
    """The configurations for this option group.

    Stability:
        experimental
    """

    engine: "DatabaseInstanceEngine"
    """The database engine that this option group is associated with.

    Stability:
        experimental
    """

    majorEngineVersion: str
    """The major version number of the database engine that this option group is associated with.

    Stability:
        experimental
    """

@jsii.implements(IParameterGroup)
class ParameterGroup(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.ParameterGroup"):
    """A parameter group.

    Stability:
        experimental
    resource:
        AWS::RDS::DBParameterGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, family: str, parameters: typing.Mapping[str,str], description: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            family: Database family of this parameter group.
            parameters: The parameters in this parameter group.
            description: Description for this parameter group. Default: a CDK generated description

        Stability:
            experimental
        """
        props: ParameterGroupProps = {"family": family, "parameters": parameters}

        if description is not None:
            props["description"] = description

        jsii.create(ParameterGroup, self, [scope, id, props])

    @jsii.member(jsii_name="fromParameterGroupName")
    @classmethod
    def from_parameter_group_name(cls, scope: aws_cdk.core.Construct, id: str, parameter_group_name: str) -> "IParameterGroup":
        """Imports a parameter group.

        Arguments:
            scope: -
            id: -
            parameter_group_name: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromParameterGroupName", [scope, id, parameter_group_name])

    @property
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> str:
        """The name of the parameter group.

        Stability:
            experimental
        """
        return jsii.get(self, "parameterGroupName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ParameterGroupProps(jsii.compat.TypedDict, total=False):
    description: str
    """Description for this parameter group.

    Default:
        a CDK generated description

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.ParameterGroupProps", jsii_struct_bases=[_ParameterGroupProps])
class ParameterGroupProps(_ParameterGroupProps):
    """Properties for a parameter group.

    Stability:
        experimental
    """
    family: str
    """Database family of this parameter group.

    Stability:
        experimental
    """

    parameters: typing.Mapping[str,str]
    """The parameters in this parameter group.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.ClusterParameterGroupProps", jsii_struct_bases=[ParameterGroupProps])
class ClusterParameterGroupProps(ParameterGroupProps, jsii.compat.TypedDict):
    """Construction properties for a ClusterParameterGroup.

    Stability:
        experimental
    """
    pass

@jsii.enum(jsii_type="@aws-cdk/aws-rds.PerformanceInsightRetention")
class PerformanceInsightRetention(enum.Enum):
    """The retention period for Performance Insight.

    Stability:
        experimental
    """
    DEFAULT = "DEFAULT"
    """Default retention period of 7 days.

    Stability:
        experimental
    """
    LONG_TERM = "LONG_TERM"
    """Long term retention period of 2 years.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.ProcessorFeatures", jsii_struct_bases=[])
class ProcessorFeatures(jsii.compat.TypedDict, total=False):
    """The processor features.

    Stability:
        experimental
    """
    coreCount: jsii.Number
    """The number of CPU core.

    Stability:
        experimental
    """

    threadsPerCore: jsii.Number
    """The number of threads per core.

    Stability:
        experimental
    """

class SecretRotation(aws_cdk.core.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.SecretRotation"):
    """Secret rotation for a database instance or cluster.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application: "SecretRotationApplication", secret: aws_cdk.aws_secretsmanager.ISecret, target: aws_cdk.aws_ec2.IConnectable, vpc: aws_cdk.aws_ec2.IVpc, vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None, automatically_after: typing.Optional[aws_cdk.core.Duration]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            application: The serverless application for the rotation.
            secret: The secret to rotate. It must be a JSON string with the following format: { 'engine': <required: database engine>, 'host': <required: instance host name>, 'username': <required: username>, 'password': <required: password>, 'dbname': <optional: database name>, 'port': <optional: if not specified, default port will be used>, 'masterarn': <required for multi user rotation: the arn of the master secret which will be used to create users/change passwords> } This is typically the case for a secret referenced from an AWS::SecretsManager::SecretTargetAttachment https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html
            target: The target database cluster or instance.
            vpc: The VPC where the Lambda rotation function will run.
            vpc_subnets: The type of subnets in the VPC where the Lambda rotation function will run. Default: - Private subnets.
            automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)

        Stability:
            experimental
        """
        props: SecretRotationProps = {"application": application, "secret": secret, "target": target, "vpc": vpc}

        if vpc_subnets is not None:
            props["vpcSubnets"] = vpc_subnets

        if automatically_after is not None:
            props["automaticallyAfter"] = automatically_after

        jsii.create(SecretRotation, self, [scope, id, props])


class SecretRotationApplication(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.SecretRotationApplication"):
    """A secret rotation serverless application.

    Stability:
        experimental
    """
    def __init__(self, application_id: str, semantic_version: str) -> None:
        """
        Arguments:
            application_id: -
            semantic_version: -

        Stability:
            experimental
        """
        jsii.create(SecretRotationApplication, self, [application_id, semantic_version])

    @classproperty
    @jsii.member(jsii_name="MARIADB_ROTATION_MULTI_USER")
    def MARIADB_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MARIADB_ROTATION_MULTI_USER")

    @classproperty
    @jsii.member(jsii_name="MARIADB_ROTATION_SINGLE_USER")
    def MARIADB_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MARIADB_ROTATION_SINGLE_USER")

    @classproperty
    @jsii.member(jsii_name="MYSQL_ROTATION_MULTI_USER")
    def MYSQL_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MYSQL_ROTATION_MULTI_USER")

    @classproperty
    @jsii.member(jsii_name="MYSQL_ROTATION_SINGLE_USER")
    def MYSQL_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MYSQL_ROTATION_SINGLE_USER")

    @classproperty
    @jsii.member(jsii_name="ORACLE_ROTATION_MULTI_USER")
    def ORACLE_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ORACLE_ROTATION_MULTI_USER")

    @classproperty
    @jsii.member(jsii_name="ORACLE_ROTATION_SINGLE_USER")
    def ORACLE_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "ORACLE_ROTATION_SINGLE_USER")

    @classproperty
    @jsii.member(jsii_name="POSTGRES_ROTATION_MULTI_USER")
    def POSTGRES_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "POSTGRES_ROTATION_MULTI_USER")

    @classproperty
    @jsii.member(jsii_name="POSTGRES_ROTATION_SINGLE_USER")
    def POSTGRES_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "POSTGRES_ROTATION_SINGLE_USER")

    @classproperty
    @jsii.member(jsii_name="SQLSERVER_ROTATION_MULTI_USER")
    def SQLSERVER_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SQLSERVER_ROTATION_MULTI_USER")

    @classproperty
    @jsii.member(jsii_name="SQLSERVER_ROTATION_SINGLE_USER")
    def SQLSERVER_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SQLSERVER_ROTATION_SINGLE_USER")

    @property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "applicationId")

    @property
    @jsii.member(jsii_name="semanticVersion")
    def semantic_version(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "semanticVersion")


@jsii.data_type(jsii_type="@aws-cdk/aws-rds.SecretRotationOptions", jsii_struct_bases=[])
class SecretRotationOptions(jsii.compat.TypedDict, total=False):
    """Options to add secret rotation to a database instance or cluster.

    Stability:
        experimental
    """
    automaticallyAfter: aws_cdk.core.Duration
    """Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation.

    Default:
        Duration.days(30)

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[SecretRotationOptions])
class _SecretRotationProps(SecretRotationOptions, jsii.compat.TypedDict, total=False):
    vpcSubnets: aws_cdk.aws_ec2.SubnetSelection
    """The type of subnets in the VPC where the Lambda rotation function will run.

    Default:
        - Private subnets.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.SecretRotationProps", jsii_struct_bases=[_SecretRotationProps])
class SecretRotationProps(_SecretRotationProps):
    """Construction properties for a SecretRotation.

    Stability:
        experimental
    """
    application: "SecretRotationApplication"
    """The serverless application for the rotation.

    Stability:
        experimental
    """

    secret: aws_cdk.aws_secretsmanager.ISecret
    """The secret to rotate.

    It must be a JSON string with the following format:
    {
    'engine': <required: database engine>,
    'host': <required: instance host name>,
    'username': <required: username>,
    'password': <required: password>,
    'dbname': <optional: database name>,
    'port': <optional: if not specified, default port will be used>,
    'masterarn': <required for multi user rotation: the arn of the master secret which will be used to create users/change passwords>
    }

    This is typically the case for a secret referenced from an AWS::SecretsManager::SecretTargetAttachment
    https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html

    Stability:
        experimental
    """

    target: aws_cdk.aws_ec2.IConnectable
    """The target database cluster or instance.

    Stability:
        experimental
    """

    vpc: aws_cdk.aws_ec2.IVpc
    """The VPC where the Lambda rotation function will run.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-rds.StorageType")
class StorageType(enum.Enum):
    """The type of storage.

    Stability:
        experimental
    """
    STANDARD = "STANDARD"
    """Standard.

    Stability:
        experimental
    """
    GP2 = "GP2"
    """General purpose (SSD).

    Stability:
        experimental
    """
    IO1 = "IO1"
    """Provisioned IOPS (SSD).

    Stability:
        experimental
    """

__all__ = ["BackupProps", "CfnDBCluster", "CfnDBClusterParameterGroup", "CfnDBClusterParameterGroupProps", "CfnDBClusterProps", "CfnDBInstance", "CfnDBInstanceProps", "CfnDBParameterGroup", "CfnDBParameterGroupProps", "CfnDBSecurityGroup", "CfnDBSecurityGroupIngress", "CfnDBSecurityGroupIngressProps", "CfnDBSecurityGroupProps", "CfnDBSubnetGroup", "CfnDBSubnetGroupProps", "CfnEventSubscription", "CfnEventSubscriptionProps", "CfnOptionGroup", "CfnOptionGroupProps", "ClusterParameterGroup", "ClusterParameterGroupProps", "DatabaseCluster", "DatabaseClusterAttributes", "DatabaseClusterEngine", "DatabaseClusterProps", "DatabaseInstance", "DatabaseInstanceAttributes", "DatabaseInstanceBase", "DatabaseInstanceEngine", "DatabaseInstanceFromSnapshot", "DatabaseInstanceFromSnapshotProps", "DatabaseInstanceNewProps", "DatabaseInstanceProps", "DatabaseInstanceReadReplica", "DatabaseInstanceReadReplicaProps", "DatabaseInstanceSourceProps", "DatabaseSecret", "DatabaseSecretProps", "Endpoint", "IDatabaseCluster", "IDatabaseInstance", "IOptionGroup", "IParameterGroup", "InstanceProps", "LicenseModel", "Login", "OptionConfiguration", "OptionGroup", "OptionGroupProps", "ParameterGroup", "ParameterGroupProps", "PerformanceInsightRetention", "ProcessorFeatures", "SecretRotation", "SecretRotationApplication", "SecretRotationOptions", "SecretRotationProps", "StorageType", "__jsii_assembly__"]

publication.publish()
