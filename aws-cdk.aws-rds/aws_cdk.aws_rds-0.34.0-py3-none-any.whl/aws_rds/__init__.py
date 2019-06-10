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
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-rds", "0.34.0", __name__, "aws-rds@0.34.0.jsii.tgz")
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
    retentionDays: jsii.Number
    """How many days to retain the backup.

    Stability:
        experimental
    """

class CfnDBCluster(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBCluster"):
    """A CloudFormation ``AWS::RDS::DBCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RDS::DBCluster
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, engine: str, availability_zones: typing.Optional[typing.List[str]]=None, backtrack_window: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, backup_retention_period: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, database_name: typing.Optional[str]=None, db_cluster_identifier: typing.Optional[str]=None, db_cluster_parameter_group_name: typing.Optional[str]=None, db_subnet_group_name: typing.Optional[str]=None, deletion_protection: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, enable_cloudwatch_logs_exports: typing.Optional[typing.List[str]]=None, enable_iam_database_authentication: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, engine_mode: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, master_username: typing.Optional[str]=None, master_user_password: typing.Optional[str]=None, port: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, replication_source_identifier: typing.Optional[str]=None, scaling_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ScalingConfigurationProperty"]]]=None, snapshot_identifier: typing.Optional[str]=None, source_region: typing.Optional[str]=None, storage_encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::RDS::DBCluster``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            engine: ``AWS::RDS::DBCluster.Engine``.
            availabilityZones: ``AWS::RDS::DBCluster.AvailabilityZones``.
            backtrackWindow: ``AWS::RDS::DBCluster.BacktrackWindow``.
            backupRetentionPeriod: ``AWS::RDS::DBCluster.BackupRetentionPeriod``.
            databaseName: ``AWS::RDS::DBCluster.DatabaseName``.
            dbClusterIdentifier: ``AWS::RDS::DBCluster.DBClusterIdentifier``.
            dbClusterParameterGroupName: ``AWS::RDS::DBCluster.DBClusterParameterGroupName``.
            dbSubnetGroupName: ``AWS::RDS::DBCluster.DBSubnetGroupName``.
            deletionProtection: ``AWS::RDS::DBCluster.DeletionProtection``.
            enableCloudwatchLogsExports: ``AWS::RDS::DBCluster.EnableCloudwatchLogsExports``.
            enableIamDatabaseAuthentication: ``AWS::RDS::DBCluster.EnableIAMDatabaseAuthentication``.
            engineMode: ``AWS::RDS::DBCluster.EngineMode``.
            engineVersion: ``AWS::RDS::DBCluster.EngineVersion``.
            kmsKeyId: ``AWS::RDS::DBCluster.KmsKeyId``.
            masterUsername: ``AWS::RDS::DBCluster.MasterUsername``.
            masterUserPassword: ``AWS::RDS::DBCluster.MasterUserPassword``.
            port: ``AWS::RDS::DBCluster.Port``.
            preferredBackupWindow: ``AWS::RDS::DBCluster.PreferredBackupWindow``.
            preferredMaintenanceWindow: ``AWS::RDS::DBCluster.PreferredMaintenanceWindow``.
            replicationSourceIdentifier: ``AWS::RDS::DBCluster.ReplicationSourceIdentifier``.
            scalingConfiguration: ``AWS::RDS::DBCluster.ScalingConfiguration``.
            snapshotIdentifier: ``AWS::RDS::DBCluster.SnapshotIdentifier``.
            sourceRegion: ``AWS::RDS::DBCluster.SourceRegion``.
            storageEncrypted: ``AWS::RDS::DBCluster.StorageEncrypted``.
            tags: ``AWS::RDS::DBCluster.Tags``.
            vpcSecurityGroupIds: ``AWS::RDS::DBCluster.VpcSecurityGroupIds``.

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
    @jsii.member(jsii_name="dbClusterEndpointAddress")
    def db_cluster_endpoint_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint.Address
        """
        return jsii.get(self, "dbClusterEndpointAddress")

    @property
    @jsii.member(jsii_name="dbClusterEndpointPort")
    def db_cluster_endpoint_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint.Port
        """
        return jsii.get(self, "dbClusterEndpointPort")

    @property
    @jsii.member(jsii_name="dbClusterName")
    def db_cluster_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "dbClusterName")

    @property
    @jsii.member(jsii_name="dbClusterReadEndpointAddress")
    def db_cluster_read_endpoint_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReadEndpoint.Address
        """
        return jsii.get(self, "dbClusterReadEndpointAddress")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDBClusterProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBCluster.ScalingConfigurationProperty", jsii_struct_bases=[])
    class ScalingConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbcluster-scalingconfiguration.html
        Stability:
            experimental
        """
        autoPause: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDBCluster.ScalingConfigurationProperty.AutoPause``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbcluster-scalingconfiguration.html#cfn-rds-dbcluster-scalingconfiguration-autopause
        Stability:
            experimental
        """

        maxCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDBCluster.ScalingConfigurationProperty.MaxCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbcluster-scalingconfiguration.html#cfn-rds-dbcluster-scalingconfiguration-maxcapacity
        Stability:
            experimental
        """

        minCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDBCluster.ScalingConfigurationProperty.MinCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbcluster-scalingconfiguration.html#cfn-rds-dbcluster-scalingconfiguration-mincapacity
        Stability:
            experimental
        """

        secondsUntilAutoPause: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDBCluster.ScalingConfigurationProperty.SecondsUntilAutoPause``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbcluster-scalingconfiguration.html#cfn-rds-dbcluster-scalingconfiguration-secondsuntilautopause
        Stability:
            experimental
        """


class CfnDBClusterParameterGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBClusterParameterGroup"):
    """A CloudFormation ``AWS::RDS::DBClusterParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RDS::DBClusterParameterGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: str, family: str, parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token], tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
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
    @jsii.member(jsii_name="dbClusterParameterGroupName")
    def db_cluster_parameter_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "dbClusterParameterGroupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDBClusterParameterGroupProps":
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
class _CfnDBClusterParameterGroupProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::RDS::DBClusterParameterGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html#cfn-rds-dbclusterparametergroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBClusterParameterGroupProps", jsii_struct_bases=[_CfnDBClusterParameterGroupProps])
class CfnDBClusterParameterGroupProps(_CfnDBClusterParameterGroupProps):
    """Properties for defining a ``AWS::RDS::DBClusterParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html
    Stability:
        experimental
    """
    description: str
    """``AWS::RDS::DBClusterParameterGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html#cfn-rds-dbclusterparametergroup-description
    Stability:
        experimental
    """

    family: str
    """``AWS::RDS::DBClusterParameterGroup.Family``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html#cfn-rds-dbclusterparametergroup-family
    Stability:
        experimental
    """

    parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::RDS::DBClusterParameterGroup.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbclusterparametergroup.html#cfn-rds-dbclusterparametergroup-parameters
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBClusterProps(jsii.compat.TypedDict, total=False):
    availabilityZones: typing.List[str]
    """``AWS::RDS::DBCluster.AvailabilityZones``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-availabilityzones
    Stability:
        experimental
    """
    backtrackWindow: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::RDS::DBCluster.BacktrackWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-backtrackwindow
    Stability:
        experimental
    """
    backupRetentionPeriod: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::RDS::DBCluster.BackupRetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-backuprententionperiod
    Stability:
        experimental
    """
    databaseName: str
    """``AWS::RDS::DBCluster.DatabaseName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-databasename
    Stability:
        experimental
    """
    dbClusterIdentifier: str
    """``AWS::RDS::DBCluster.DBClusterIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-dbclusteridentifier
    Stability:
        experimental
    """
    dbClusterParameterGroupName: str
    """``AWS::RDS::DBCluster.DBClusterParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-dbclusterparametergroupname
    Stability:
        experimental
    """
    dbSubnetGroupName: str
    """``AWS::RDS::DBCluster.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-dbsubnetgroupname
    Stability:
        experimental
    """
    deletionProtection: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBCluster.DeletionProtection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-deletionprotection
    Stability:
        experimental
    """
    enableCloudwatchLogsExports: typing.List[str]
    """``AWS::RDS::DBCluster.EnableCloudwatchLogsExports``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-enablecloudwatchlogsexports
    Stability:
        experimental
    """
    enableIamDatabaseAuthentication: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBCluster.EnableIAMDatabaseAuthentication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-enableiamdatabaseauthentication
    Stability:
        experimental
    """
    engineMode: str
    """``AWS::RDS::DBCluster.EngineMode``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-enginemode
    Stability:
        experimental
    """
    engineVersion: str
    """``AWS::RDS::DBCluster.EngineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-engineversion
    Stability:
        experimental
    """
    kmsKeyId: str
    """``AWS::RDS::DBCluster.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-kmskeyid
    Stability:
        experimental
    """
    masterUsername: str
    """``AWS::RDS::DBCluster.MasterUsername``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-masterusername
    Stability:
        experimental
    """
    masterUserPassword: str
    """``AWS::RDS::DBCluster.MasterUserPassword``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-masteruserpassword
    Stability:
        experimental
    """
    port: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::RDS::DBCluster.Port``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-port
    Stability:
        experimental
    """
    preferredBackupWindow: str
    """``AWS::RDS::DBCluster.PreferredBackupWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-preferredbackupwindow
    Stability:
        experimental
    """
    preferredMaintenanceWindow: str
    """``AWS::RDS::DBCluster.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-preferredmaintenancewindow
    Stability:
        experimental
    """
    replicationSourceIdentifier: str
    """``AWS::RDS::DBCluster.ReplicationSourceIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-replicationsourceidentifier
    Stability:
        experimental
    """
    scalingConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDBCluster.ScalingConfigurationProperty"]
    """``AWS::RDS::DBCluster.ScalingConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-scalingconfiguration
    Stability:
        experimental
    """
    snapshotIdentifier: str
    """``AWS::RDS::DBCluster.SnapshotIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-snapshotidentifier
    Stability:
        experimental
    """
    sourceRegion: str
    """``AWS::RDS::DBCluster.SourceRegion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-sourceregion
    Stability:
        experimental
    """
    storageEncrypted: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBCluster.StorageEncrypted``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-storageencrypted
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::RDS::DBCluster.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-tags
    Stability:
        experimental
    """
    vpcSecurityGroupIds: typing.List[str]
    """``AWS::RDS::DBCluster.VpcSecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-vpcsecuritygroupids
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBClusterProps", jsii_struct_bases=[_CfnDBClusterProps])
class CfnDBClusterProps(_CfnDBClusterProps):
    """Properties for defining a ``AWS::RDS::DBCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html
    Stability:
        experimental
    """
    engine: str
    """``AWS::RDS::DBCluster.Engine``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-engine
    Stability:
        experimental
    """

class CfnDBInstance(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBInstance"):
    """A CloudFormation ``AWS::RDS::DBInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RDS::DBInstance
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, db_instance_class: str, allocated_storage: typing.Optional[str]=None, allow_major_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, availability_zone: typing.Optional[str]=None, backup_retention_period: typing.Optional[str]=None, character_set_name: typing.Optional[str]=None, copy_tags_to_snapshot: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, db_cluster_identifier: typing.Optional[str]=None, db_instance_identifier: typing.Optional[str]=None, db_name: typing.Optional[str]=None, db_parameter_group_name: typing.Optional[str]=None, db_security_groups: typing.Optional[typing.List[str]]=None, db_snapshot_identifier: typing.Optional[str]=None, db_subnet_group_name: typing.Optional[str]=None, delete_automated_backups: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, deletion_protection: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, domain: typing.Optional[str]=None, domain_iam_role_name: typing.Optional[str]=None, enable_cloudwatch_logs_exports: typing.Optional[typing.List[str]]=None, enable_iam_database_authentication: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, enable_performance_insights: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, engine: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, iops: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, kms_key_id: typing.Optional[str]=None, license_model: typing.Optional[str]=None, master_username: typing.Optional[str]=None, master_user_password: typing.Optional[str]=None, monitoring_interval: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, monitoring_role_arn: typing.Optional[str]=None, multi_az: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, option_group_name: typing.Optional[str]=None, performance_insights_kms_key_id: typing.Optional[str]=None, performance_insights_retention_period: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, port: typing.Optional[str]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, processor_features: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "ProcessorFeatureProperty"]]]]]=None, promotion_tier: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, publicly_accessible: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, source_db_instance_identifier: typing.Optional[str]=None, source_region: typing.Optional[str]=None, storage_encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, storage_type: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, timezone: typing.Optional[str]=None, use_default_processor_features: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, vpc_security_groups: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::RDS::DBInstance``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            dbInstanceClass: ``AWS::RDS::DBInstance.DBInstanceClass``.
            allocatedStorage: ``AWS::RDS::DBInstance.AllocatedStorage``.
            allowMajorVersionUpgrade: ``AWS::RDS::DBInstance.AllowMajorVersionUpgrade``.
            autoMinorVersionUpgrade: ``AWS::RDS::DBInstance.AutoMinorVersionUpgrade``.
            availabilityZone: ``AWS::RDS::DBInstance.AvailabilityZone``.
            backupRetentionPeriod: ``AWS::RDS::DBInstance.BackupRetentionPeriod``.
            characterSetName: ``AWS::RDS::DBInstance.CharacterSetName``.
            copyTagsToSnapshot: ``AWS::RDS::DBInstance.CopyTagsToSnapshot``.
            dbClusterIdentifier: ``AWS::RDS::DBInstance.DBClusterIdentifier``.
            dbInstanceIdentifier: ``AWS::RDS::DBInstance.DBInstanceIdentifier``.
            dbName: ``AWS::RDS::DBInstance.DBName``.
            dbParameterGroupName: ``AWS::RDS::DBInstance.DBParameterGroupName``.
            dbSecurityGroups: ``AWS::RDS::DBInstance.DBSecurityGroups``.
            dbSnapshotIdentifier: ``AWS::RDS::DBInstance.DBSnapshotIdentifier``.
            dbSubnetGroupName: ``AWS::RDS::DBInstance.DBSubnetGroupName``.
            deleteAutomatedBackups: ``AWS::RDS::DBInstance.DeleteAutomatedBackups``.
            deletionProtection: ``AWS::RDS::DBInstance.DeletionProtection``.
            domain: ``AWS::RDS::DBInstance.Domain``.
            domainIamRoleName: ``AWS::RDS::DBInstance.DomainIAMRoleName``.
            enableCloudwatchLogsExports: ``AWS::RDS::DBInstance.EnableCloudwatchLogsExports``.
            enableIamDatabaseAuthentication: ``AWS::RDS::DBInstance.EnableIAMDatabaseAuthentication``.
            enablePerformanceInsights: ``AWS::RDS::DBInstance.EnablePerformanceInsights``.
            engine: ``AWS::RDS::DBInstance.Engine``.
            engineVersion: ``AWS::RDS::DBInstance.EngineVersion``.
            iops: ``AWS::RDS::DBInstance.Iops``.
            kmsKeyId: ``AWS::RDS::DBInstance.KmsKeyId``.
            licenseModel: ``AWS::RDS::DBInstance.LicenseModel``.
            masterUsername: ``AWS::RDS::DBInstance.MasterUsername``.
            masterUserPassword: ``AWS::RDS::DBInstance.MasterUserPassword``.
            monitoringInterval: ``AWS::RDS::DBInstance.MonitoringInterval``.
            monitoringRoleArn: ``AWS::RDS::DBInstance.MonitoringRoleArn``.
            multiAz: ``AWS::RDS::DBInstance.MultiAZ``.
            optionGroupName: ``AWS::RDS::DBInstance.OptionGroupName``.
            performanceInsightsKmsKeyId: ``AWS::RDS::DBInstance.PerformanceInsightsKMSKeyId``.
            performanceInsightsRetentionPeriod: ``AWS::RDS::DBInstance.PerformanceInsightsRetentionPeriod``.
            port: ``AWS::RDS::DBInstance.Port``.
            preferredBackupWindow: ``AWS::RDS::DBInstance.PreferredBackupWindow``.
            preferredMaintenanceWindow: ``AWS::RDS::DBInstance.PreferredMaintenanceWindow``.
            processorFeatures: ``AWS::RDS::DBInstance.ProcessorFeatures``.
            promotionTier: ``AWS::RDS::DBInstance.PromotionTier``.
            publiclyAccessible: ``AWS::RDS::DBInstance.PubliclyAccessible``.
            sourceDbInstanceIdentifier: ``AWS::RDS::DBInstance.SourceDBInstanceIdentifier``.
            sourceRegion: ``AWS::RDS::DBInstance.SourceRegion``.
            storageEncrypted: ``AWS::RDS::DBInstance.StorageEncrypted``.
            storageType: ``AWS::RDS::DBInstance.StorageType``.
            tags: ``AWS::RDS::DBInstance.Tags``.
            timezone: ``AWS::RDS::DBInstance.Timezone``.
            useDefaultProcessorFeatures: ``AWS::RDS::DBInstance.UseDefaultProcessorFeatures``.
            vpcSecurityGroups: ``AWS::RDS::DBInstance.VPCSecurityGroups``.

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
    @jsii.member(jsii_name="dbInstanceEndpointAddress")
    def db_instance_endpoint_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint.Address
        """
        return jsii.get(self, "dbInstanceEndpointAddress")

    @property
    @jsii.member(jsii_name="dbInstanceEndpointPort")
    def db_instance_endpoint_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint.Port
        """
        return jsii.get(self, "dbInstanceEndpointPort")

    @property
    @jsii.member(jsii_name="dbInstanceId")
    def db_instance_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "dbInstanceId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDBInstanceProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBInstance.ProcessorFeatureProperty", jsii_struct_bases=[])
    class ProcessorFeatureProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbinstance-processorfeature.html
        Stability:
            experimental
        """
        name: str
        """``CfnDBInstance.ProcessorFeatureProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbinstance-processorfeature.html#cfn-rds-dbinstance-processorfeature-name
        Stability:
            experimental
        """

        value: str
        """``CfnDBInstance.ProcessorFeatureProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbinstance-processorfeature.html#cfn-rds-dbinstance-processorfeature-value
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBInstanceProps(jsii.compat.TypedDict, total=False):
    allocatedStorage: str
    """``AWS::RDS::DBInstance.AllocatedStorage``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-allocatedstorage
    Stability:
        experimental
    """
    allowMajorVersionUpgrade: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.AllowMajorVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-allowmajorversionupgrade
    Stability:
        experimental
    """
    autoMinorVersionUpgrade: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.AutoMinorVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-autominorversionupgrade
    Stability:
        experimental
    """
    availabilityZone: str
    """``AWS::RDS::DBInstance.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-availabilityzone
    Stability:
        experimental
    """
    backupRetentionPeriod: str
    """``AWS::RDS::DBInstance.BackupRetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-backupretentionperiod
    Stability:
        experimental
    """
    characterSetName: str
    """``AWS::RDS::DBInstance.CharacterSetName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-charactersetname
    Stability:
        experimental
    """
    copyTagsToSnapshot: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.CopyTagsToSnapshot``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-copytagstosnapshot
    Stability:
        experimental
    """
    dbClusterIdentifier: str
    """``AWS::RDS::DBInstance.DBClusterIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbclusteridentifier
    Stability:
        experimental
    """
    dbInstanceIdentifier: str
    """``AWS::RDS::DBInstance.DBInstanceIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbinstanceidentifier
    Stability:
        experimental
    """
    dbName: str
    """``AWS::RDS::DBInstance.DBName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbname
    Stability:
        experimental
    """
    dbParameterGroupName: str
    """``AWS::RDS::DBInstance.DBParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbparametergroupname
    Stability:
        experimental
    """
    dbSecurityGroups: typing.List[str]
    """``AWS::RDS::DBInstance.DBSecurityGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbsecuritygroups
    Stability:
        experimental
    """
    dbSnapshotIdentifier: str
    """``AWS::RDS::DBInstance.DBSnapshotIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbsnapshotidentifier
    Stability:
        experimental
    """
    dbSubnetGroupName: str
    """``AWS::RDS::DBInstance.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbsubnetgroupname
    Stability:
        experimental
    """
    deleteAutomatedBackups: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.DeleteAutomatedBackups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-deleteautomatedbackups
    Stability:
        experimental
    """
    deletionProtection: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.DeletionProtection``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-deletionprotection
    Stability:
        experimental
    """
    domain: str
    """``AWS::RDS::DBInstance.Domain``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-domain
    Stability:
        experimental
    """
    domainIamRoleName: str
    """``AWS::RDS::DBInstance.DomainIAMRoleName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-domainiamrolename
    Stability:
        experimental
    """
    enableCloudwatchLogsExports: typing.List[str]
    """``AWS::RDS::DBInstance.EnableCloudwatchLogsExports``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-enablecloudwatchlogsexports
    Stability:
        experimental
    """
    enableIamDatabaseAuthentication: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.EnableIAMDatabaseAuthentication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-enableiamdatabaseauthentication
    Stability:
        experimental
    """
    enablePerformanceInsights: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.EnablePerformanceInsights``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-enableperformanceinsights
    Stability:
        experimental
    """
    engine: str
    """``AWS::RDS::DBInstance.Engine``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-engine
    Stability:
        experimental
    """
    engineVersion: str
    """``AWS::RDS::DBInstance.EngineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-engineversion
    Stability:
        experimental
    """
    iops: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.Iops``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-iops
    Stability:
        experimental
    """
    kmsKeyId: str
    """``AWS::RDS::DBInstance.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-kmskeyid
    Stability:
        experimental
    """
    licenseModel: str
    """``AWS::RDS::DBInstance.LicenseModel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-licensemodel
    Stability:
        experimental
    """
    masterUsername: str
    """``AWS::RDS::DBInstance.MasterUsername``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-masterusername
    Stability:
        experimental
    """
    masterUserPassword: str
    """``AWS::RDS::DBInstance.MasterUserPassword``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-masteruserpassword
    Stability:
        experimental
    """
    monitoringInterval: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.MonitoringInterval``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-monitoringinterval
    Stability:
        experimental
    """
    monitoringRoleArn: str
    """``AWS::RDS::DBInstance.MonitoringRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-monitoringrolearn
    Stability:
        experimental
    """
    multiAz: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.MultiAZ``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-multiaz
    Stability:
        experimental
    """
    optionGroupName: str
    """``AWS::RDS::DBInstance.OptionGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-optiongroupname
    Stability:
        experimental
    """
    performanceInsightsKmsKeyId: str
    """``AWS::RDS::DBInstance.PerformanceInsightsKMSKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-performanceinsightskmskeyid
    Stability:
        experimental
    """
    performanceInsightsRetentionPeriod: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.PerformanceInsightsRetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-performanceinsightsretentionperiod
    Stability:
        experimental
    """
    port: str
    """``AWS::RDS::DBInstance.Port``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-port
    Stability:
        experimental
    """
    preferredBackupWindow: str
    """``AWS::RDS::DBInstance.PreferredBackupWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-preferredbackupwindow
    Stability:
        experimental
    """
    preferredMaintenanceWindow: str
    """``AWS::RDS::DBInstance.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-preferredmaintenancewindow
    Stability:
        experimental
    """
    processorFeatures: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDBInstance.ProcessorFeatureProperty"]]]
    """``AWS::RDS::DBInstance.ProcessorFeatures``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-processorfeatures
    Stability:
        experimental
    """
    promotionTier: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.PromotionTier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-promotiontier
    Stability:
        experimental
    """
    publiclyAccessible: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.PubliclyAccessible``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-publiclyaccessible
    Stability:
        experimental
    """
    sourceDbInstanceIdentifier: str
    """``AWS::RDS::DBInstance.SourceDBInstanceIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-sourcedbinstanceidentifier
    Stability:
        experimental
    """
    sourceRegion: str
    """``AWS::RDS::DBInstance.SourceRegion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-sourceregion
    Stability:
        experimental
    """
    storageEncrypted: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.StorageEncrypted``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-storageencrypted
    Stability:
        experimental
    """
    storageType: str
    """``AWS::RDS::DBInstance.StorageType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-storagetype
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::RDS::DBInstance.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-tags
    Stability:
        experimental
    """
    timezone: str
    """``AWS::RDS::DBInstance.Timezone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-timezone
    Stability:
        experimental
    """
    useDefaultProcessorFeatures: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::DBInstance.UseDefaultProcessorFeatures``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-usedefaultprocessorfeatures
    Stability:
        experimental
    """
    vpcSecurityGroups: typing.List[str]
    """``AWS::RDS::DBInstance.VPCSecurityGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-vpcsecuritygroups
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBInstanceProps", jsii_struct_bases=[_CfnDBInstanceProps])
class CfnDBInstanceProps(_CfnDBInstanceProps):
    """Properties for defining a ``AWS::RDS::DBInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html
    Stability:
        experimental
    """
    dbInstanceClass: str
    """``AWS::RDS::DBInstance.DBInstanceClass``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-dbinstanceclass
    Stability:
        experimental
    """

class CfnDBParameterGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBParameterGroup"):
    """A CloudFormation ``AWS::RDS::DBParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RDS::DBParameterGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: str, family: str, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.Mapping[str,str]]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
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
    @jsii.member(jsii_name="dbParameterGroupName")
    def db_parameter_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "dbParameterGroupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDBParameterGroupProps":
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
class _CfnDBParameterGroupProps(jsii.compat.TypedDict, total=False):
    parameters: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
    """``AWS::RDS::DBParameterGroup.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html#cfn-rds-dbparametergroup-parameters
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::RDS::DBParameterGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html#cfn-rds-dbparametergroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBParameterGroupProps", jsii_struct_bases=[_CfnDBParameterGroupProps])
class CfnDBParameterGroupProps(_CfnDBParameterGroupProps):
    """Properties for defining a ``AWS::RDS::DBParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html
    Stability:
        experimental
    """
    description: str
    """``AWS::RDS::DBParameterGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html#cfn-rds-dbparametergroup-description
    Stability:
        experimental
    """

    family: str
    """``AWS::RDS::DBParameterGroup.Family``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html#cfn-rds-dbparametergroup-family
    Stability:
        experimental
    """

class CfnDBSecurityGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBSecurityGroup"):
    """A CloudFormation ``AWS::RDS::DBSecurityGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RDS::DBSecurityGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, db_security_group_ingress: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "IngressProperty"]]], group_description: str, ec2_vpc_id: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::RDS::DBSecurityGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            dbSecurityGroupIngress: ``AWS::RDS::DBSecurityGroup.DBSecurityGroupIngress``.
            groupDescription: ``AWS::RDS::DBSecurityGroup.GroupDescription``.
            ec2VpcId: ``AWS::RDS::DBSecurityGroup.EC2VpcId``.
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
    @jsii.member(jsii_name="dbSecurityGroupName")
    def db_security_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "dbSecurityGroupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDBSecurityGroupProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBSecurityGroup.IngressProperty", jsii_struct_bases=[])
    class IngressProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group-rule.html
        Stability:
            experimental
        """
        cidrip: str
        """``CfnDBSecurityGroup.IngressProperty.CIDRIP``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group-rule.html#cfn-rds-securitygroup-cidrip
        Stability:
            experimental
        """

        ec2SecurityGroupId: str
        """``CfnDBSecurityGroup.IngressProperty.EC2SecurityGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group-rule.html#cfn-rds-securitygroup-ec2securitygroupid
        Stability:
            experimental
        """

        ec2SecurityGroupName: str
        """``CfnDBSecurityGroup.IngressProperty.EC2SecurityGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group-rule.html#cfn-rds-securitygroup-ec2securitygroupname
        Stability:
            experimental
        """

        ec2SecurityGroupOwnerId: str
        """``CfnDBSecurityGroup.IngressProperty.EC2SecurityGroupOwnerId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group-rule.html#cfn-rds-securitygroup-ec2securitygroupownerid
        Stability:
            experimental
        """


class CfnDBSecurityGroupIngress(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBSecurityGroupIngress"):
    """A CloudFormation ``AWS::RDS::DBSecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RDS::DBSecurityGroupIngress
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, db_security_group_name: str, cidrip: typing.Optional[str]=None, ec2_security_group_id: typing.Optional[str]=None, ec2_security_group_name: typing.Optional[str]=None, ec2_security_group_owner_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::RDS::DBSecurityGroupIngress``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            dbSecurityGroupName: ``AWS::RDS::DBSecurityGroupIngress.DBSecurityGroupName``.
            cidrip: ``AWS::RDS::DBSecurityGroupIngress.CIDRIP``.
            ec2SecurityGroupId: ``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupId``.
            ec2SecurityGroupName: ``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupName``.
            ec2SecurityGroupOwnerId: ``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupOwnerId``.

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
    @jsii.member(jsii_name="dbSecurityGroupIngressName")
    def db_security_group_ingress_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "dbSecurityGroupIngressName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDBSecurityGroupIngressProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBSecurityGroupIngressProps(jsii.compat.TypedDict, total=False):
    cidrip: str
    """``AWS::RDS::DBSecurityGroupIngress.CIDRIP``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-cidrip
    Stability:
        experimental
    """
    ec2SecurityGroupId: str
    """``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-ec2securitygroupid
    Stability:
        experimental
    """
    ec2SecurityGroupName: str
    """``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-ec2securitygroupname
    Stability:
        experimental
    """
    ec2SecurityGroupOwnerId: str
    """``AWS::RDS::DBSecurityGroupIngress.EC2SecurityGroupOwnerId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-ec2securitygroupownerid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBSecurityGroupIngressProps", jsii_struct_bases=[_CfnDBSecurityGroupIngressProps])
class CfnDBSecurityGroupIngressProps(_CfnDBSecurityGroupIngressProps):
    """Properties for defining a ``AWS::RDS::DBSecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html
    Stability:
        experimental
    """
    dbSecurityGroupName: str
    """``AWS::RDS::DBSecurityGroupIngress.DBSecurityGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-security-group-ingress.html#cfn-rds-securitygroup-ingress-dbsecuritygroupname
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBSecurityGroupProps(jsii.compat.TypedDict, total=False):
    ec2VpcId: str
    """``AWS::RDS::DBSecurityGroup.EC2VpcId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html#cfn-rds-dbsecuritygroup-ec2vpcid
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::RDS::DBSecurityGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html#cfn-rds-dbsecuritygroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBSecurityGroupProps", jsii_struct_bases=[_CfnDBSecurityGroupProps])
class CfnDBSecurityGroupProps(_CfnDBSecurityGroupProps):
    """Properties for defining a ``AWS::RDS::DBSecurityGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html
    Stability:
        experimental
    """
    dbSecurityGroupIngress: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDBSecurityGroup.IngressProperty"]]]
    """``AWS::RDS::DBSecurityGroup.DBSecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html#cfn-rds-dbsecuritygroup-dbsecuritygroupingress
    Stability:
        experimental
    """

    groupDescription: str
    """``AWS::RDS::DBSecurityGroup.GroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-security-group.html#cfn-rds-dbsecuritygroup-groupdescription
    Stability:
        experimental
    """

class CfnDBSubnetGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnDBSubnetGroup"):
    """A CloudFormation ``AWS::RDS::DBSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RDS::DBSubnetGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, db_subnet_group_description: str, subnet_ids: typing.List[str], db_subnet_group_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::RDS::DBSubnetGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            dbSubnetGroupDescription: ``AWS::RDS::DBSubnetGroup.DBSubnetGroupDescription``.
            subnetIds: ``AWS::RDS::DBSubnetGroup.SubnetIds``.
            dbSubnetGroupName: ``AWS::RDS::DBSubnetGroup.DBSubnetGroupName``.
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
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "dbSubnetGroupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDBSubnetGroupProps":
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
class _CfnDBSubnetGroupProps(jsii.compat.TypedDict, total=False):
    dbSubnetGroupName: str
    """``AWS::RDS::DBSubnetGroup.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html#cfn-rds-dbsubnetgroup-dbsubnetgroupname
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::RDS::DBSubnetGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html#cfn-rds-dbsubnetgroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnDBSubnetGroupProps", jsii_struct_bases=[_CfnDBSubnetGroupProps])
class CfnDBSubnetGroupProps(_CfnDBSubnetGroupProps):
    """Properties for defining a ``AWS::RDS::DBSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html
    Stability:
        experimental
    """
    dbSubnetGroupDescription: str
    """``AWS::RDS::DBSubnetGroup.DBSubnetGroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html#cfn-rds-dbsubnetgroup-dbsubnetgroupdescription
    Stability:
        experimental
    """

    subnetIds: typing.List[str]
    """``AWS::RDS::DBSubnetGroup.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbsubnet-group.html#cfn-rds-dbsubnetgroup-subnetids
    Stability:
        experimental
    """

class CfnEventSubscription(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnEventSubscription"):
    """A CloudFormation ``AWS::RDS::EventSubscription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RDS::EventSubscription
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, sns_topic_arn: str, enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, event_categories: typing.Optional[typing.List[str]]=None, source_ids: typing.Optional[typing.List[str]]=None, source_type: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::RDS::EventSubscription``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            snsTopicArn: ``AWS::RDS::EventSubscription.SnsTopicArn``.
            enabled: ``AWS::RDS::EventSubscription.Enabled``.
            eventCategories: ``AWS::RDS::EventSubscription.EventCategories``.
            sourceIds: ``AWS::RDS::EventSubscription.SourceIds``.
            sourceType: ``AWS::RDS::EventSubscription.SourceType``.

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


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEventSubscriptionProps(jsii.compat.TypedDict, total=False):
    enabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::RDS::EventSubscription.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-enabled
    Stability:
        experimental
    """
    eventCategories: typing.List[str]
    """``AWS::RDS::EventSubscription.EventCategories``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-eventcategories
    Stability:
        experimental
    """
    sourceIds: typing.List[str]
    """``AWS::RDS::EventSubscription.SourceIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-sourceids
    Stability:
        experimental
    """
    sourceType: str
    """``AWS::RDS::EventSubscription.SourceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-sourcetype
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnEventSubscriptionProps", jsii_struct_bases=[_CfnEventSubscriptionProps])
class CfnEventSubscriptionProps(_CfnEventSubscriptionProps):
    """Properties for defining a ``AWS::RDS::EventSubscription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html
    Stability:
        experimental
    """
    snsTopicArn: str
    """``AWS::RDS::EventSubscription.SnsTopicArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-eventsubscription.html#cfn-rds-eventsubscription-snstopicarn
    Stability:
        experimental
    """

class CfnOptionGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.CfnOptionGroup"):
    """A CloudFormation ``AWS::RDS::OptionGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RDS::OptionGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, engine_name: str, major_engine_version: str, option_configurations: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "OptionConfigurationProperty"]]], option_group_description: str, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::RDS::OptionGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            engineName: ``AWS::RDS::OptionGroup.EngineName``.
            majorEngineVersion: ``AWS::RDS::OptionGroup.MajorEngineVersion``.
            optionConfigurations: ``AWS::RDS::OptionGroup.OptionConfigurations``.
            optionGroupDescription: ``AWS::RDS::OptionGroup.OptionGroupDescription``.
            tags: ``AWS::RDS::OptionGroup.Tags``.

        Stability:
            experimental
        """
        props: CfnOptionGroupProps = {"engineName": engine_name, "majorEngineVersion": major_engine_version, "optionConfigurations": option_configurations, "optionGroupDescription": option_group_description}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnOptionGroup, self, [scope, id, props])

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
    @jsii.member(jsii_name="optionGroupName")
    def option_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "optionGroupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnOptionGroupProps":
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
    class _OptionConfigurationProperty(jsii.compat.TypedDict, total=False):
        dbSecurityGroupMemberships: typing.List[str]
        """``CfnOptionGroup.OptionConfigurationProperty.DBSecurityGroupMemberships``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html#cfn-rds-optiongroup-optionconfigurations-dbsecuritygroupmemberships
        Stability:
            experimental
        """
        optionSettings: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnOptionGroup.OptionSettingProperty"]]]
        """``CfnOptionGroup.OptionConfigurationProperty.OptionSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html#cfn-rds-optiongroup-optionconfigurations-optionsettings
        Stability:
            experimental
        """
        optionVersion: str
        """``CfnOptionGroup.OptionConfigurationProperty.OptionVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html#cfn-rds-optiongroup-optionconfiguration-optionversion
        Stability:
            experimental
        """
        port: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnOptionGroup.OptionConfigurationProperty.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html#cfn-rds-optiongroup-optionconfigurations-port
        Stability:
            experimental
        """
        vpcSecurityGroupMemberships: typing.List[str]
        """``CfnOptionGroup.OptionConfigurationProperty.VpcSecurityGroupMemberships``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html#cfn-rds-optiongroup-optionconfigurations-vpcsecuritygroupmemberships
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnOptionGroup.OptionConfigurationProperty", jsii_struct_bases=[_OptionConfigurationProperty])
    class OptionConfigurationProperty(_OptionConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html
        Stability:
            experimental
        """
        optionName: str
        """``CfnOptionGroup.OptionConfigurationProperty.OptionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations.html#cfn-rds-optiongroup-optionconfigurations-optionname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnOptionGroup.OptionSettingProperty", jsii_struct_bases=[])
    class OptionSettingProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations-optionsettings.html
        Stability:
            experimental
        """
        name: str
        """``CfnOptionGroup.OptionSettingProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations-optionsettings.html#cfn-rds-optiongroup-optionconfigurations-optionsettings-name
        Stability:
            experimental
        """

        value: str
        """``CfnOptionGroup.OptionSettingProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-optiongroup-optionconfigurations-optionsettings.html#cfn-rds-optiongroup-optionconfigurations-optionsettings-value
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnOptionGroupProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::RDS::OptionGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-rds.CfnOptionGroupProps", jsii_struct_bases=[_CfnOptionGroupProps])
class CfnOptionGroupProps(_CfnOptionGroupProps):
    """Properties for defining a ``AWS::RDS::OptionGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html
    Stability:
        experimental
    """
    engineName: str
    """``AWS::RDS::OptionGroup.EngineName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-enginename
    Stability:
        experimental
    """

    majorEngineVersion: str
    """``AWS::RDS::OptionGroup.MajorEngineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-majorengineversion
    Stability:
        experimental
    """

    optionConfigurations: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnOptionGroup.OptionConfigurationProperty"]]]
    """``AWS::RDS::OptionGroup.OptionConfigurations``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-optionconfigurations
    Stability:
        experimental
    """

    optionGroupDescription: str
    """``AWS::RDS::OptionGroup.OptionGroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-optiongroup.html#cfn-rds-optiongroup-optiongroupdescription
    Stability:
        experimental
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
            secretRotationApplication: -

        Stability:
            experimental
        """
        jsii.create(DatabaseClusterEngine, self, [name, secret_rotation_application])

    @classproperty
    @jsii.member(jsii_name="Aurora")
    def AURORA(cls) -> "DatabaseClusterEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Aurora")

    @classproperty
    @jsii.member(jsii_name="AuroraMysql")
    def AURORA_MYSQL(cls) -> "DatabaseClusterEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "AuroraMysql")

    @classproperty
    @jsii.member(jsii_name="AuroraPostgresql")
    def AURORA_POSTGRESQL(cls) -> "DatabaseClusterEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "AuroraPostgresql")

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
    deleteReplacePolicy: aws_cdk.cdk.DeletionPolicy
    """The CloudFormation policy to apply when the cluster and its instances are removed from the stack or replaced during an update.

    Default:
        - Retain cluster.

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
            secretRotationApplication: -

        Stability:
            experimental
        """
        jsii.create(DatabaseInstanceEngine, self, [name, secret_rotation_application])

    @classproperty
    @jsii.member(jsii_name="MariaDb")
    def MARIA_DB(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MariaDb")

    @classproperty
    @jsii.member(jsii_name="Mysql")
    def MYSQL(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Mysql")

    @classproperty
    @jsii.member(jsii_name="OracleEE")
    def ORACLE_EE(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "OracleEE")

    @classproperty
    @jsii.member(jsii_name="OracleSE")
    def ORACLE_SE(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "OracleSE")

    @classproperty
    @jsii.member(jsii_name="OracleSE1")
    def ORACLE_S_E1(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "OracleSE1")

    @classproperty
    @jsii.member(jsii_name="OracleSE2")
    def ORACLE_S_E2(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "OracleSE2")

    @classproperty
    @jsii.member(jsii_name="Postgres")
    def POSTGRES(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Postgres")

    @classproperty
    @jsii.member(jsii_name="SqlServerEE")
    def SQL_SERVER_EE(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SqlServerEE")

    @classproperty
    @jsii.member(jsii_name="SqlServerEX")
    def SQL_SERVER_EX(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SqlServerEX")

    @classproperty
    @jsii.member(jsii_name="SqlServerSE")
    def SQL_SERVER_SE(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SqlServerSE")

    @classproperty
    @jsii.member(jsii_name="SqlServerWeb")
    def SQL_SERVER_WEB(cls) -> "DatabaseInstanceEngine":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SqlServerWeb")


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
    backupRetentionPeriod: jsii.Number
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
    deleteReplacePolicy: aws_cdk.cdk.DeletionPolicy
    """The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update.

    Default:
        Retain

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
    monitoringInterval: jsii.Number
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
    performanceInsightRetentionPeriod: "PerformanceInsightRetentionPeriod"
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
    masterUserPassword: aws_cdk.cdk.SecretValue
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, username: str, encryption_key: typing.Optional[aws_cdk.aws_kms.IKey]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            username: The username.
            encryptionKey: The KMS key to use to encrypt the secret. Default: default master key

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
class IDatabaseCluster(aws_cdk.cdk.IResource, aws_cdk.aws_ec2.IConnectable, aws_cdk.aws_secretsmanager.ISecretAttachmentTarget, jsii.compat.Protocol):
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


class _IDatabaseClusterProxy(jsii.proxy_for(aws_cdk.cdk.IResource), jsii.proxy_for(aws_cdk.aws_ec2.IConnectable), jsii.proxy_for(aws_cdk.aws_secretsmanager.ISecretAttachmentTarget)):
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
class DatabaseCluster(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.DatabaseCluster"):
    """Create a clustered database with a given number of instances.

    Stability:
        experimental
    resource:
        AWS::RDS::DBCluster
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, engine: "DatabaseClusterEngine", instance_props: "InstanceProps", master_user: "Login", backup: typing.Optional["BackupProps"]=None, cluster_identifier: typing.Optional[str]=None, default_database_name: typing.Optional[str]=None, delete_replace_policy: typing.Optional[aws_cdk.cdk.DeletionPolicy]=None, engine_version: typing.Optional[str]=None, instance_identifier_base: typing.Optional[str]=None, instances: typing.Optional[jsii.Number]=None, kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, parameter_group: typing.Optional["IParameterGroup"]=None, port: typing.Optional[jsii.Number]=None, preferred_maintenance_window: typing.Optional[str]=None, storage_encrypted: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            engine: What kind of database to start.
            instanceProps: Settings for the individual instances that are launched.
            masterUser: Username and password for the administrative user.
            backup: Backup settings. Default: - Backup retention period for automated backups is 1 day. Backup preferred window is set to a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
            clusterIdentifier: An optional identifier for the cluster. Default: - A name is automatically generated.
            defaultDatabaseName: Name of a database which is automatically created inside the cluster. Default: - Database is not created in cluster.
            deleteReplacePolicy: The CloudFormation policy to apply when the cluster and its instances are removed from the stack or replaced during an update. Default: - Retain cluster.
            engineVersion: What version of the database to start. Default: - The default for the engine is used.
            instanceIdentifierBase: Base identifier for instances. Every replica is named by appending the replica number to this string, 1-based. Default: - clusterIdentifier is used with the word "Instance" appended. If clusterIdentifier is not provided, the identifier is automatically generated.
            instances: How many replicas/instances to create. Has to be at least 1. Default: 2
            kmsKey: The KMS key for storage encryption. If specified ``storageEncrypted`` will be set to ``true``. Default: - default master key.
            parameterGroup: Additional parameters to pass to the database engine. Default: - No parameter group.
            port: What port to listen on. Default: - The default for the engine is used.
            preferredMaintenanceWindow: A daily time range in 24-hours UTC format in which backups preferably execute. Must be at least 30 minutes long. Example: '01:00-02:00' Default: - 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week.
            storageEncrypted: Whether to enable storage encryption. Default: false

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

        if delete_replace_policy is not None:
            props["deleteReplacePolicy"] = delete_replace_policy

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

        if storage_encrypted is not None:
            props["storageEncrypted"] = storage_encrypted

        jsii.create(DatabaseCluster, self, [scope, id, props])

    @jsii.member(jsii_name="fromDatabaseClusterAttributes")
    @classmethod
    def from_database_cluster_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, cluster_endpoint_address: str, cluster_identifier: str, instance_endpoint_addresses: typing.List[str], instance_identifiers: typing.List[str], port: jsii.Number, reader_endpoint_address: str, security_group_id: str) -> "IDatabaseCluster":
        """Import an existing DatabaseCluster from properties.

        Arguments:
            scope: -
            id: -
            attrs: -
            clusterEndpointAddress: Cluster endpoint address.
            clusterIdentifier: Identifier for the cluster.
            instanceEndpointAddresses: Endpoint addresses of individual instances.
            instanceIdentifiers: Identifier for the instances.
            port: The database port.
            readerEndpointAddress: Reader endpoint address.
            securityGroupId: The security group for this database cluster.

        Stability:
            experimental
        """
        attrs: DatabaseClusterAttributes = {"clusterEndpointAddress": cluster_endpoint_address, "clusterIdentifier": cluster_identifier, "instanceEndpointAddresses": instance_endpoint_addresses, "instanceIdentifiers": instance_identifiers, "port": port, "readerEndpointAddress": reader_endpoint_address, "securityGroupId": security_group_id}

        return jsii.sinvoke(cls, "fromDatabaseClusterAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="addRotationSingleUser")
    def add_rotation_single_user(self, id: str, *, automatically_after_days: typing.Optional[jsii.Number]=None) -> "SecretRotation":
        """Adds the single user rotation of the master password to this cluster.

        Arguments:
            id: -
            options: -
            automaticallyAfterDays: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: 30 days

        Stability:
            experimental
        """
        options: SecretRotationOptions = {}

        if automatically_after_days is not None:
            options["automaticallyAfterDays"] = automatically_after_days

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
class IDatabaseInstance(aws_cdk.cdk.IResource, aws_cdk.aws_ec2.IConnectable, aws_cdk.aws_secretsmanager.ISecretAttachmentTarget, jsii.compat.Protocol):
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
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this DBInstance.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricCPUUtilization")
    def metric_cpu_utilization(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The percentage of CPU utilization.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricDatabaseConnections")
    def metric_database_connections(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of database connections in use.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricFreeableMemory")
    def metric_freeable_memory(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The amount of available random access memory.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricFreeStorageSpace")
    def metric_free_storage_space(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The amount of available storage space.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricReadIOPS")
    def metric_read_iops(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The average number of disk write I/O operations per second.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="metricWriteIOPS")
    def metric_write_iops(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The average number of disk read I/O operations per second.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for instance events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        ...


class _IDatabaseInstanceProxy(jsii.proxy_for(aws_cdk.cdk.IResource), jsii.proxy_for(aws_cdk.aws_ec2.IConnectable), jsii.proxy_for(aws_cdk.aws_secretsmanager.ISecretAttachmentTarget)):
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
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this DBInstance.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricCPUUtilization")
    def metric_cpu_utilization(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The percentage of CPU utilization.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricCPUUtilization", [props])

    @jsii.member(jsii_name="metricDatabaseConnections")
    def metric_database_connections(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of database connections in use.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricDatabaseConnections", [props])

    @jsii.member(jsii_name="metricFreeableMemory")
    def metric_freeable_memory(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The amount of available random access memory.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricFreeableMemory", [props])

    @jsii.member(jsii_name="metricFreeStorageSpace")
    def metric_free_storage_space(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The amount of available storage space.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricFreeStorageSpace", [props])

    @jsii.member(jsii_name="metricReadIOPS")
    def metric_read_iops(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The average number of disk write I/O operations per second.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricReadIOPS", [props])

    @jsii.member(jsii_name="metricWriteIOPS")
    def metric_write_iops(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The average number of disk read I/O operations per second.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricWriteIOPS", [props])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for instance events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

        return jsii.invoke(self, "onEvent", [id, options])


@jsii.implements(IDatabaseInstance)
class DatabaseInstanceBase(aws_cdk.cdk.Resource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-rds.DatabaseInstanceBase"):
    """A new or imported database instance.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _DatabaseInstanceBaseProxy

    def __init__(self, scope: aws_cdk.cdk.Construct, id: str) -> None:
        """Creates a new construct node.

        Arguments:
            scope: The scope in which to define this construct.
            id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.

        Stability:
            experimental
        """
        jsii.create(DatabaseInstanceBase, self, [scope, id])

    @jsii.member(jsii_name="fromDatabaseInstanceAttributes")
    @classmethod
    def from_database_instance_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, instance_endpoint_address: str, instance_identifier: str, port: jsii.Number, security_group_id: str) -> "IDatabaseInstance":
        """Import an existing database instance.

        Arguments:
            scope: -
            id: -
            attrs: -
            instanceEndpointAddress: The endpoint address.
            instanceIdentifier: The instance identifier.
            port: The database port.
            securityGroupId: The security group identifier of the instance.

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
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this DBInstance.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricCPUUtilization")
    def metric_cpu_utilization(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The percentage of CPU utilization.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricCPUUtilization", [props])

    @jsii.member(jsii_name="metricDatabaseConnections")
    def metric_database_connections(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The number of database connections in use.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricDatabaseConnections", [props])

    @jsii.member(jsii_name="metricFreeableMemory")
    def metric_freeable_memory(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The amount of available random access memory.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricFreeableMemory", [props])

    @jsii.member(jsii_name="metricFreeStorageSpace")
    def metric_free_storage_space(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The amount of available storage space.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricFreeStorageSpace", [props])

    @jsii.member(jsii_name="metricReadIOPS")
    def metric_read_iops(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The average number of disk write I/O operations per second.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricReadIOPS", [props])

    @jsii.member(jsii_name="metricWriteIOPS")
    def metric_write_iops(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """The average number of disk read I/O operations per second.

        Average over 5 minutes

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
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

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricWriteIOPS", [props])

    @jsii.member(jsii_name="onEvent")
    def on_event(self, id: str, *, target: aws_cdk.aws_events.IRuleTarget, description: typing.Optional[str]=None, event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern]=None, rule_name: typing.Optional[str]=None) -> aws_cdk.aws_events.Rule:
        """Defines a CloudWatch event rule which triggers for instance events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        Arguments:
            id: -
            options: -
            target: The target to register for the event.
            description: A description of the rule's purpose.
            eventPattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering.
            ruleName: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        Stability:
            experimental
        """
        options: aws_cdk.aws_events.OnEventOptions = {"target": target}

        if description is not None:
            options["description"] = description

        if event_pattern is not None:
            options["eventPattern"] = event_pattern

        if rule_name is not None:
            options["ruleName"] = rule_name

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


class _DatabaseInstanceBaseProxy(DatabaseInstanceBase, jsii.proxy_for(aws_cdk.cdk.Resource)):
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, master_username: str, character_set_name: typing.Optional[str]=None, kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, storage_encrypted: typing.Optional[bool]=None, engine: "DatabaseInstanceEngine", allocated_storage: typing.Optional[jsii.Number]=None, allow_major_version_upgrade: typing.Optional[bool]=None, database_name: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, license_model: typing.Optional["LicenseModel"]=None, master_user_password: typing.Optional[aws_cdk.cdk.SecretValue]=None, parameter_group: typing.Optional["IParameterGroup"]=None, secret_kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, timezone: typing.Optional[str]=None, instance_class: aws_cdk.aws_ec2.InstanceType, vpc: aws_cdk.aws_ec2.IVpc, auto_minor_version_upgrade: typing.Optional[bool]=None, availability_zone: typing.Optional[str]=None, backup_retention_period: typing.Optional[jsii.Number]=None, cloudwatch_logs_exports: typing.Optional[typing.List[str]]=None, cloudwatch_logs_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays]=None, copy_tags_to_snapshot: typing.Optional[bool]=None, delete_automated_backups: typing.Optional[bool]=None, delete_replace_policy: typing.Optional[aws_cdk.cdk.DeletionPolicy]=None, deletion_protection: typing.Optional[bool]=None, enable_performance_insights: typing.Optional[bool]=None, iam_authentication: typing.Optional[bool]=None, instance_identifier: typing.Optional[str]=None, iops: typing.Optional[jsii.Number]=None, monitoring_interval: typing.Optional[jsii.Number]=None, multi_az: typing.Optional[bool]=None, option_group: typing.Optional["IOptionGroup"]=None, performance_insight_kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, performance_insight_retention_period: typing.Optional["PerformanceInsightRetentionPeriod"]=None, port: typing.Optional[jsii.Number]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, processor_features: typing.Optional["ProcessorFeatures"]=None, storage_type: typing.Optional["StorageType"]=None, vpc_placement: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            masterUsername: The master user name.
            characterSetName: For supported engines, specifies the character set to associate with the DB instance. Default: RDS default character set name
            kmsKey: The master key that's used to encrypt the DB instance. Default: default master key
            storageEncrypted: Indicates whether the DB instance is encrypted. Default: false
            engine: The database engine.
            allocatedStorage: The allocated storage size, specified in gigabytes (GB). Default: 100
            allowMajorVersionUpgrade: Whether to allow major version upgrades. Default: false
            databaseName: The name of the database. Default: no name
            engineVersion: The engine version. To prevent automatic upgrades, be sure to specify the full version number. Default: RDS default engine version
            licenseModel: The license model. Default: RDS default license model
            masterUserPassword: The master user password. Default: a Secrets Manager generated password
            parameterGroup: The DB parameter group to associate with the instance. Default: no parameter group
            secretKmsKey: The KMS key to use to encrypt the secret for the master user password. Default: default master key
            timezone: The time zone of the instance. Default: RDS default timezone
            instanceClass: The name of the compute and memory capacity classes.
            vpc: The VPC network where the DB subnet group should be created.
            autoMinorVersionUpgrade: Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window. Default: true
            availabilityZone: The name of the Availability Zone where the DB instance will be located. Default: no preference
            backupRetentionPeriod: The number of days during which automatic DB snapshots are retained. Set to zero to disable backups. Default: 1 day
            cloudwatchLogsExports: The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: no log exports
            cloudwatchLogsRetention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: logs never expire
            copyTagsToSnapshot: Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance. Default: true
            deleteAutomatedBackups: Indicates whether automated backups should be deleted or retained when you delete a DB instance. Default: false
            deleteReplacePolicy: The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update. Default: Retain
            deletionProtection: Indicates whether the DB instance should have deletion protection enabled. Default: true
            enablePerformanceInsights: Whether to enable Performance Insights for the DB instance. Default: false
            iamAuthentication: Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. Default: false
            instanceIdentifier: A name for the DB instance. If you specify a name, AWS CloudFormation converts it to lowercase. Default: a CloudFormation generated name
            iops: The number of I/O operations per second (IOPS) that the database provisions. The value must be equal to or greater than 1000. Default: no provisioned iops
            monitoringInterval: The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance. Default: no enhanced monitoring
            multiAz: Specifies if the database instance is a multiple Availability Zone deployment. Default: false
            optionGroup: The option group to associate with the instance. Default: no option group
            performanceInsightKmsKey: The AWS KMS key for encryption of Performance Insights data. Default: default master key
            performanceInsightRetentionPeriod: The amount of time, in days, to retain Performance Insights data. Default: 7 days
            port: The port for the instance. Default: the default port for the chosen engine.
            preferredBackupWindow: The daily time range during which automated backups are performed. Constraints: - Must be in the format ``hh24:mi-hh24:mi``. - Must be in Universal Coordinated Time (UTC). - Must not conflict with the preferred maintenance window. - Must be at least 30 minutes. Default: a 30-minute window selected at random from an 8-hour block of time for each AWS Region. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow
            preferredMaintenanceWindow: The weekly time range (in UTC) during which system maintenance can occur. Format: ``ddd:hh24:mi-ddd:hh24:mi`` Constraint: Minimum 30-minute window Default: a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow
            processorFeatures: The number of CPU cores and the number of threads per core. Default: the default number of CPU cores and threads per core for the chosen instance class. See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#USER_ConfigureProcessor
            storageType: The storage type. Default: GP2
            vpcPlacement: The type of subnets to add to the created DB subnet group. Default: private

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

        if backup_retention_period is not None:
            props["backupRetentionPeriod"] = backup_retention_period

        if cloudwatch_logs_exports is not None:
            props["cloudwatchLogsExports"] = cloudwatch_logs_exports

        if cloudwatch_logs_retention is not None:
            props["cloudwatchLogsRetention"] = cloudwatch_logs_retention

        if copy_tags_to_snapshot is not None:
            props["copyTagsToSnapshot"] = copy_tags_to_snapshot

        if delete_automated_backups is not None:
            props["deleteAutomatedBackups"] = delete_automated_backups

        if delete_replace_policy is not None:
            props["deleteReplacePolicy"] = delete_replace_policy

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

        if performance_insight_retention_period is not None:
            props["performanceInsightRetentionPeriod"] = performance_insight_retention_period

        if port is not None:
            props["port"] = port

        if preferred_backup_window is not None:
            props["preferredBackupWindow"] = preferred_backup_window

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if processor_features is not None:
            props["processorFeatures"] = processor_features

        if storage_type is not None:
            props["storageType"] = storage_type

        if vpc_placement is not None:
            props["vpcPlacement"] = vpc_placement

        jsii.create(DatabaseInstance, self, [scope, id, props])

    @jsii.member(jsii_name="addRotationSingleUser")
    def add_rotation_single_user(self, id: str, *, automatically_after_days: typing.Optional[jsii.Number]=None) -> "SecretRotation":
        """Adds the single user rotation of the master password to this instance.

        Arguments:
            id: -
            options: -
            automaticallyAfterDays: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: 30 days

        Stability:
            experimental
        """
        options: SecretRotationOptions = {}

        if automatically_after_days is not None:
            options["automaticallyAfterDays"] = automatically_after_days

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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, snapshot_identifier: str, generate_master_user_password: typing.Optional[bool]=None, master_username: typing.Optional[str]=None, engine: "DatabaseInstanceEngine", allocated_storage: typing.Optional[jsii.Number]=None, allow_major_version_upgrade: typing.Optional[bool]=None, database_name: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, license_model: typing.Optional["LicenseModel"]=None, master_user_password: typing.Optional[aws_cdk.cdk.SecretValue]=None, parameter_group: typing.Optional["IParameterGroup"]=None, secret_kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, timezone: typing.Optional[str]=None, instance_class: aws_cdk.aws_ec2.InstanceType, vpc: aws_cdk.aws_ec2.IVpc, auto_minor_version_upgrade: typing.Optional[bool]=None, availability_zone: typing.Optional[str]=None, backup_retention_period: typing.Optional[jsii.Number]=None, cloudwatch_logs_exports: typing.Optional[typing.List[str]]=None, cloudwatch_logs_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays]=None, copy_tags_to_snapshot: typing.Optional[bool]=None, delete_automated_backups: typing.Optional[bool]=None, delete_replace_policy: typing.Optional[aws_cdk.cdk.DeletionPolicy]=None, deletion_protection: typing.Optional[bool]=None, enable_performance_insights: typing.Optional[bool]=None, iam_authentication: typing.Optional[bool]=None, instance_identifier: typing.Optional[str]=None, iops: typing.Optional[jsii.Number]=None, monitoring_interval: typing.Optional[jsii.Number]=None, multi_az: typing.Optional[bool]=None, option_group: typing.Optional["IOptionGroup"]=None, performance_insight_kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, performance_insight_retention_period: typing.Optional["PerformanceInsightRetentionPeriod"]=None, port: typing.Optional[jsii.Number]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, processor_features: typing.Optional["ProcessorFeatures"]=None, storage_type: typing.Optional["StorageType"]=None, vpc_placement: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            snapshotIdentifier: The name or Amazon Resource Name (ARN) of the DB snapshot that's used to restore the DB instance. If you're restoring from a shared manual DB snapshot, you must specify the ARN of the snapshot.
            generateMasterUserPassword: Whether to generate a new master user password and store it in Secrets Manager. ``masterUsername`` must be specified when this property is set to true. Default: false
            masterUsername: The master user name. Default: inherited from the snapshot
            engine: The database engine.
            allocatedStorage: The allocated storage size, specified in gigabytes (GB). Default: 100
            allowMajorVersionUpgrade: Whether to allow major version upgrades. Default: false
            databaseName: The name of the database. Default: no name
            engineVersion: The engine version. To prevent automatic upgrades, be sure to specify the full version number. Default: RDS default engine version
            licenseModel: The license model. Default: RDS default license model
            masterUserPassword: The master user password. Default: a Secrets Manager generated password
            parameterGroup: The DB parameter group to associate with the instance. Default: no parameter group
            secretKmsKey: The KMS key to use to encrypt the secret for the master user password. Default: default master key
            timezone: The time zone of the instance. Default: RDS default timezone
            instanceClass: The name of the compute and memory capacity classes.
            vpc: The VPC network where the DB subnet group should be created.
            autoMinorVersionUpgrade: Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window. Default: true
            availabilityZone: The name of the Availability Zone where the DB instance will be located. Default: no preference
            backupRetentionPeriod: The number of days during which automatic DB snapshots are retained. Set to zero to disable backups. Default: 1 day
            cloudwatchLogsExports: The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: no log exports
            cloudwatchLogsRetention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: logs never expire
            copyTagsToSnapshot: Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance. Default: true
            deleteAutomatedBackups: Indicates whether automated backups should be deleted or retained when you delete a DB instance. Default: false
            deleteReplacePolicy: The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update. Default: Retain
            deletionProtection: Indicates whether the DB instance should have deletion protection enabled. Default: true
            enablePerformanceInsights: Whether to enable Performance Insights for the DB instance. Default: false
            iamAuthentication: Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. Default: false
            instanceIdentifier: A name for the DB instance. If you specify a name, AWS CloudFormation converts it to lowercase. Default: a CloudFormation generated name
            iops: The number of I/O operations per second (IOPS) that the database provisions. The value must be equal to or greater than 1000. Default: no provisioned iops
            monitoringInterval: The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance. Default: no enhanced monitoring
            multiAz: Specifies if the database instance is a multiple Availability Zone deployment. Default: false
            optionGroup: The option group to associate with the instance. Default: no option group
            performanceInsightKmsKey: The AWS KMS key for encryption of Performance Insights data. Default: default master key
            performanceInsightRetentionPeriod: The amount of time, in days, to retain Performance Insights data. Default: 7 days
            port: The port for the instance. Default: the default port for the chosen engine.
            preferredBackupWindow: The daily time range during which automated backups are performed. Constraints: - Must be in the format ``hh24:mi-hh24:mi``. - Must be in Universal Coordinated Time (UTC). - Must not conflict with the preferred maintenance window. - Must be at least 30 minutes. Default: a 30-minute window selected at random from an 8-hour block of time for each AWS Region. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow
            preferredMaintenanceWindow: The weekly time range (in UTC) during which system maintenance can occur. Format: ``ddd:hh24:mi-ddd:hh24:mi`` Constraint: Minimum 30-minute window Default: a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow
            processorFeatures: The number of CPU cores and the number of threads per core. Default: the default number of CPU cores and threads per core for the chosen instance class. See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#USER_ConfigureProcessor
            storageType: The storage type. Default: GP2
            vpcPlacement: The type of subnets to add to the created DB subnet group. Default: private

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

        if backup_retention_period is not None:
            props["backupRetentionPeriod"] = backup_retention_period

        if cloudwatch_logs_exports is not None:
            props["cloudwatchLogsExports"] = cloudwatch_logs_exports

        if cloudwatch_logs_retention is not None:
            props["cloudwatchLogsRetention"] = cloudwatch_logs_retention

        if copy_tags_to_snapshot is not None:
            props["copyTagsToSnapshot"] = copy_tags_to_snapshot

        if delete_automated_backups is not None:
            props["deleteAutomatedBackups"] = delete_automated_backups

        if delete_replace_policy is not None:
            props["deleteReplacePolicy"] = delete_replace_policy

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

        if performance_insight_retention_period is not None:
            props["performanceInsightRetentionPeriod"] = performance_insight_retention_period

        if port is not None:
            props["port"] = port

        if preferred_backup_window is not None:
            props["preferredBackupWindow"] = preferred_backup_window

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if processor_features is not None:
            props["processorFeatures"] = processor_features

        if storage_type is not None:
            props["storageType"] = storage_type

        if vpc_placement is not None:
            props["vpcPlacement"] = vpc_placement

        jsii.create(DatabaseInstanceFromSnapshot, self, [scope, id, props])

    @jsii.member(jsii_name="addRotationSingleUser")
    def add_rotation_single_user(self, id: str, *, automatically_after_days: typing.Optional[jsii.Number]=None) -> "SecretRotation":
        """Adds the single user rotation of the master password to this instance.

        Arguments:
            id: -
            options: -
            automaticallyAfterDays: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: 30 days

        Stability:
            experimental
        """
        options: SecretRotationOptions = {}

        if automatically_after_days is not None:
            options["automaticallyAfterDays"] = automatically_after_days

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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, source_database_instance: "IDatabaseInstance", kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, storage_encrypted: typing.Optional[bool]=None, engine: "DatabaseInstanceEngine", allocated_storage: typing.Optional[jsii.Number]=None, allow_major_version_upgrade: typing.Optional[bool]=None, database_name: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, license_model: typing.Optional["LicenseModel"]=None, master_user_password: typing.Optional[aws_cdk.cdk.SecretValue]=None, parameter_group: typing.Optional["IParameterGroup"]=None, secret_kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, timezone: typing.Optional[str]=None, instance_class: aws_cdk.aws_ec2.InstanceType, vpc: aws_cdk.aws_ec2.IVpc, auto_minor_version_upgrade: typing.Optional[bool]=None, availability_zone: typing.Optional[str]=None, backup_retention_period: typing.Optional[jsii.Number]=None, cloudwatch_logs_exports: typing.Optional[typing.List[str]]=None, cloudwatch_logs_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays]=None, copy_tags_to_snapshot: typing.Optional[bool]=None, delete_automated_backups: typing.Optional[bool]=None, delete_replace_policy: typing.Optional[aws_cdk.cdk.DeletionPolicy]=None, deletion_protection: typing.Optional[bool]=None, enable_performance_insights: typing.Optional[bool]=None, iam_authentication: typing.Optional[bool]=None, instance_identifier: typing.Optional[str]=None, iops: typing.Optional[jsii.Number]=None, monitoring_interval: typing.Optional[jsii.Number]=None, multi_az: typing.Optional[bool]=None, option_group: typing.Optional["IOptionGroup"]=None, performance_insight_kms_key: typing.Optional[aws_cdk.aws_kms.IKey]=None, performance_insight_retention_period: typing.Optional["PerformanceInsightRetentionPeriod"]=None, port: typing.Optional[jsii.Number]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, processor_features: typing.Optional["ProcessorFeatures"]=None, storage_type: typing.Optional["StorageType"]=None, vpc_placement: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            sourceDatabaseInstance: The source database instance. Each DB instance can have a limited number of read replicas. For more information, see https://docs.aws.amazon.com/AmazonRDS/latest/DeveloperGuide/USER_ReadRepl.html.
            kmsKey: The master key that's used to encrypt the DB instance. Default: default master key
            storageEncrypted: Indicates whether the DB instance is encrypted. Default: false
            engine: The database engine.
            allocatedStorage: The allocated storage size, specified in gigabytes (GB). Default: 100
            allowMajorVersionUpgrade: Whether to allow major version upgrades. Default: false
            databaseName: The name of the database. Default: no name
            engineVersion: The engine version. To prevent automatic upgrades, be sure to specify the full version number. Default: RDS default engine version
            licenseModel: The license model. Default: RDS default license model
            masterUserPassword: The master user password. Default: a Secrets Manager generated password
            parameterGroup: The DB parameter group to associate with the instance. Default: no parameter group
            secretKmsKey: The KMS key to use to encrypt the secret for the master user password. Default: default master key
            timezone: The time zone of the instance. Default: RDS default timezone
            instanceClass: The name of the compute and memory capacity classes.
            vpc: The VPC network where the DB subnet group should be created.
            autoMinorVersionUpgrade: Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window. Default: true
            availabilityZone: The name of the Availability Zone where the DB instance will be located. Default: no preference
            backupRetentionPeriod: The number of days during which automatic DB snapshots are retained. Set to zero to disable backups. Default: 1 day
            cloudwatchLogsExports: The list of log types that need to be enabled for exporting to CloudWatch Logs. Default: no log exports
            cloudwatchLogsRetention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``Infinity``. Default: logs never expire
            copyTagsToSnapshot: Indicates whether to copy all of the user-defined tags from the DB instance to snapshots of the DB instance. Default: true
            deleteAutomatedBackups: Indicates whether automated backups should be deleted or retained when you delete a DB instance. Default: false
            deleteReplacePolicy: The CloudFormation policy to apply when the instance is removed from the stack or replaced during an update. Default: Retain
            deletionProtection: Indicates whether the DB instance should have deletion protection enabled. Default: true
            enablePerformanceInsights: Whether to enable Performance Insights for the DB instance. Default: false
            iamAuthentication: Whether to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts. Default: false
            instanceIdentifier: A name for the DB instance. If you specify a name, AWS CloudFormation converts it to lowercase. Default: a CloudFormation generated name
            iops: The number of I/O operations per second (IOPS) that the database provisions. The value must be equal to or greater than 1000. Default: no provisioned iops
            monitoringInterval: The interval, in seconds, between points when Amazon RDS collects enhanced monitoring metrics for the DB instance. Default: no enhanced monitoring
            multiAz: Specifies if the database instance is a multiple Availability Zone deployment. Default: false
            optionGroup: The option group to associate with the instance. Default: no option group
            performanceInsightKmsKey: The AWS KMS key for encryption of Performance Insights data. Default: default master key
            performanceInsightRetentionPeriod: The amount of time, in days, to retain Performance Insights data. Default: 7 days
            port: The port for the instance. Default: the default port for the chosen engine.
            preferredBackupWindow: The daily time range during which automated backups are performed. Constraints: - Must be in the format ``hh24:mi-hh24:mi``. - Must be in Universal Coordinated Time (UTC). - Must not conflict with the preferred maintenance window. - Must be at least 30 minutes. Default: a 30-minute window selected at random from an 8-hour block of time for each AWS Region. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow
            preferredMaintenanceWindow: The weekly time range (in UTC) during which system maintenance can occur. Format: ``ddd:hh24:mi-ddd:hh24:mi`` Constraint: Minimum 30-minute window Default: a 30-minute window selected at random from an 8-hour block of time for each AWS Region, occurring on a random day of the week. To see the time blocks available, see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html#AdjustingTheMaintenanceWindow
            processorFeatures: The number of CPU cores and the number of threads per core. Default: the default number of CPU cores and threads per core for the chosen instance class. See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#USER_ConfigureProcessor
            storageType: The storage type. Default: GP2
            vpcPlacement: The type of subnets to add to the created DB subnet group. Default: private

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

        if backup_retention_period is not None:
            props["backupRetentionPeriod"] = backup_retention_period

        if cloudwatch_logs_exports is not None:
            props["cloudwatchLogsExports"] = cloudwatch_logs_exports

        if cloudwatch_logs_retention is not None:
            props["cloudwatchLogsRetention"] = cloudwatch_logs_retention

        if copy_tags_to_snapshot is not None:
            props["copyTagsToSnapshot"] = copy_tags_to_snapshot

        if delete_automated_backups is not None:
            props["deleteAutomatedBackups"] = delete_automated_backups

        if delete_replace_policy is not None:
            props["deleteReplacePolicy"] = delete_replace_policy

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

        if performance_insight_retention_period is not None:
            props["performanceInsightRetentionPeriod"] = performance_insight_retention_period

        if port is not None:
            props["port"] = port

        if preferred_backup_window is not None:
            props["preferredBackupWindow"] = preferred_backup_window

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if processor_features is not None:
            props["processorFeatures"] = processor_features

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
class IOptionGroup(aws_cdk.cdk.IResource, jsii.compat.Protocol):
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


class _IOptionGroupProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
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
class IParameterGroup(aws_cdk.cdk.IResource, jsii.compat.Protocol):
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
        """
        ...


class _IParameterGroupProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
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
        """
        return jsii.get(self, "parameterGroupName")


@jsii.implements(IParameterGroup)
class ClusterParameterGroup(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.ClusterParameterGroup"):
    """A cluster parameter group.

    Stability:
        experimental
    resource:
        AWS::RDS::DBClusterParameterGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, family: str, parameters: typing.Mapping[str,str], description: typing.Optional[str]=None) -> None:
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
    def from_parameter_group_name(cls, scope: aws_cdk.cdk.Construct, id: str, parameter_group_name: str) -> "IParameterGroup":
        """Imports a parameter group.

        Arguments:
            scope: -
            id: -
            parameterGroupName: -

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
    LicenseIncluded = "LicenseIncluded"
    """License included.

    Stability:
        experimental
    """
    BringYourOwnLicense = "BringYourOwnLicense"
    """Bring your own licencse.

    Stability:
        experimental
    """
    GeneralPublicLicense = "GeneralPublicLicense"
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
    password: aws_cdk.cdk.SecretValue
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
class OptionGroup(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.OptionGroup"):
    """
    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, configurations: typing.List["OptionConfiguration"], engine: "DatabaseInstanceEngine", major_engine_version: str, description: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            configurations: The configurations for this option group.
            engine: The database engine that this option group is associated with.
            majorEngineVersion: The major version number of the database engine that this option group is associated with.
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
    def from_option_group_name(cls, scope: aws_cdk.cdk.Construct, id: str, option_group_name: str) -> "IOptionGroup":
        """Import an existing option group.

        Arguments:
            scope: -
            id: -
            optionGroupName: -

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


@jsii.data_type(jsii_type="@aws-cdk/aws-rds.OptionGroupAttributes", jsii_struct_bases=[])
class OptionGroupAttributes(jsii.compat.TypedDict):
    """Reference to an existing option group.

    Stability:
        experimental
    """
    optionGroupName: str
    """The name of the option group.

    Stability:
        experimental
    """

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
class ParameterGroup(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.ParameterGroup"):
    """A parameter group.

    Stability:
        experimental
    resource:
        AWS::RDS::DBParameterGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, family: str, parameters: typing.Mapping[str,str], description: typing.Optional[str]=None) -> None:
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
    def from_parameter_group_name(cls, scope: aws_cdk.cdk.Construct, id: str, parameter_group_name: str) -> "IParameterGroup":
        """Imports a parameter group.

        Arguments:
            scope: -
            id: -
            parameterGroupName: -

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


@jsii.data_type(jsii_type="@aws-cdk/aws-rds.ParameterGroupAttributes", jsii_struct_bases=[])
class ParameterGroupAttributes(jsii.compat.TypedDict):
    """Reference to an existing parameter group.

    Stability:
        experimental
    """
    parameterGroupName: str
    """The name of the parameter group.

    Stability:
        experimental
    """

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

@jsii.enum(jsii_type="@aws-cdk/aws-rds.PerformanceInsightRetentionPeriod")
class PerformanceInsightRetentionPeriod(enum.Enum):
    """The retention period for Performance Insight.

    Stability:
        experimental
    """
    Default = "Default"
    """Default retention period of 7 days.

    Stability:
        experimental
    """
    LongTerm = "LongTerm"
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

class SecretRotation(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.SecretRotation"):
    """Secret rotation for a database instance or cluster.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, application: "SecretRotationApplication", secret: aws_cdk.aws_secretsmanager.ISecret, target: aws_cdk.aws_ec2.IConnectable, vpc: aws_cdk.aws_ec2.IVpc, vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None, automatically_after_days: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            application: The serverless application for the rotation.
            secret: The secret to rotate. It must be a JSON string with the following format: { 'engine': <required: database engine>, 'host': <required: instance host name>, 'username': <required: username>, 'password': <required: password>, 'dbname': <optional: database name>, 'port': <optional: if not specified, default port will be used>, 'masterarn': <required for multi user rotation: the arn of the master secret which will be used to create users/change passwords> } This is typically the case for a secret referenced from an AWS::SecretsManager::SecretTargetAttachment https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secrettargetattachment.html
            target: The target database cluster or instance.
            vpc: The VPC where the Lambda rotation function will run.
            vpcSubnets: The type of subnets in the VPC where the Lambda rotation function will run. Default: - Private subnets.
            automaticallyAfterDays: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: 30 days

        Stability:
            experimental
        """
        props: SecretRotationProps = {"application": application, "secret": secret, "target": target, "vpc": vpc}

        if vpc_subnets is not None:
            props["vpcSubnets"] = vpc_subnets

        if automatically_after_days is not None:
            props["automaticallyAfterDays"] = automatically_after_days

        jsii.create(SecretRotation, self, [scope, id, props])


class SecretRotationApplication(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-rds.SecretRotationApplication"):
    """A secret rotation serverless application.

    Stability:
        experimental
    """
    def __init__(self, application_id: str, semantic_version: str) -> None:
        """
        Arguments:
            applicationId: -
            semanticVersion: -

        Stability:
            experimental
        """
        jsii.create(SecretRotationApplication, self, [application_id, semantic_version])

    @classproperty
    @jsii.member(jsii_name="MariaDBRotationMultiUser")
    def MARIA_DB_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MariaDBRotationMultiUser")

    @classproperty
    @jsii.member(jsii_name="MariaDbRotationSingleUser")
    def MARIA_DB_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MariaDbRotationSingleUser")

    @classproperty
    @jsii.member(jsii_name="MysqlRotationMultiUser")
    def MYSQL_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MysqlRotationMultiUser")

    @classproperty
    @jsii.member(jsii_name="MysqlRotationSingleUser")
    def MYSQL_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "MysqlRotationSingleUser")

    @classproperty
    @jsii.member(jsii_name="OracleRotationMultiUser")
    def ORACLE_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "OracleRotationMultiUser")

    @classproperty
    @jsii.member(jsii_name="OracleRotationSingleUser")
    def ORACLE_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "OracleRotationSingleUser")

    @classproperty
    @jsii.member(jsii_name="PostgreSQLRotationMultiUser")
    def POSTGRE_SQL_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "PostgreSQLRotationMultiUser")

    @classproperty
    @jsii.member(jsii_name="PostgresRotationSingleUser")
    def POSTGRES_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "PostgresRotationSingleUser")

    @classproperty
    @jsii.member(jsii_name="SqlServerRotationMultiUser")
    def SQL_SERVER_ROTATION_MULTI_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SqlServerRotationMultiUser")

    @classproperty
    @jsii.member(jsii_name="SqlServerRotationSingleUser")
    def SQL_SERVER_ROTATION_SINGLE_USER(cls) -> "SecretRotationApplication":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "SqlServerRotationSingleUser")

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
    automaticallyAfterDays: jsii.Number
    """Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation.

    Default:
        30 days

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
    Standard = "Standard"
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

__all__ = ["BackupProps", "CfnDBCluster", "CfnDBClusterParameterGroup", "CfnDBClusterParameterGroupProps", "CfnDBClusterProps", "CfnDBInstance", "CfnDBInstanceProps", "CfnDBParameterGroup", "CfnDBParameterGroupProps", "CfnDBSecurityGroup", "CfnDBSecurityGroupIngress", "CfnDBSecurityGroupIngressProps", "CfnDBSecurityGroupProps", "CfnDBSubnetGroup", "CfnDBSubnetGroupProps", "CfnEventSubscription", "CfnEventSubscriptionProps", "CfnOptionGroup", "CfnOptionGroupProps", "ClusterParameterGroup", "ClusterParameterGroupProps", "DatabaseCluster", "DatabaseClusterAttributes", "DatabaseClusterEngine", "DatabaseClusterProps", "DatabaseInstance", "DatabaseInstanceAttributes", "DatabaseInstanceBase", "DatabaseInstanceEngine", "DatabaseInstanceFromSnapshot", "DatabaseInstanceFromSnapshotProps", "DatabaseInstanceNewProps", "DatabaseInstanceProps", "DatabaseInstanceReadReplica", "DatabaseInstanceReadReplicaProps", "DatabaseInstanceSourceProps", "DatabaseSecret", "DatabaseSecretProps", "Endpoint", "IDatabaseCluster", "IDatabaseInstance", "IOptionGroup", "IParameterGroup", "InstanceProps", "LicenseModel", "Login", "OptionConfiguration", "OptionGroup", "OptionGroupAttributes", "OptionGroupProps", "ParameterGroup", "ParameterGroupAttributes", "ParameterGroupProps", "PerformanceInsightRetentionPeriod", "ProcessorFeatures", "SecretRotation", "SecretRotationApplication", "SecretRotationOptions", "SecretRotationProps", "StorageType", "__jsii_assembly__"]

publication.publish()
