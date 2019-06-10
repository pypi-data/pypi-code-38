import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-docdb", "0.34.0", __name__, "aws-docdb@0.34.0.jsii.tgz")
class CfnDBCluster(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-docdb.CfnDBCluster"):
    """A CloudFormation ``AWS::DocDB::DBCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DocDB::DBCluster
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, availability_zones: typing.Optional[typing.List[str]]=None, backup_retention_period: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, db_cluster_identifier: typing.Optional[str]=None, db_cluster_parameter_group_name: typing.Optional[str]=None, db_subnet_group_name: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, master_username: typing.Optional[str]=None, master_user_password: typing.Optional[str]=None, port: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, snapshot_identifier: typing.Optional[str]=None, storage_encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::DocDB::DBCluster``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            availabilityZones: ``AWS::DocDB::DBCluster.AvailabilityZones``.
            backupRetentionPeriod: ``AWS::DocDB::DBCluster.BackupRetentionPeriod``.
            dbClusterIdentifier: ``AWS::DocDB::DBCluster.DBClusterIdentifier``.
            dbClusterParameterGroupName: ``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.
            dbSubnetGroupName: ``AWS::DocDB::DBCluster.DBSubnetGroupName``.
            engineVersion: ``AWS::DocDB::DBCluster.EngineVersion``.
            kmsKeyId: ``AWS::DocDB::DBCluster.KmsKeyId``.
            masterUsername: ``AWS::DocDB::DBCluster.MasterUsername``.
            masterUserPassword: ``AWS::DocDB::DBCluster.MasterUserPassword``.
            port: ``AWS::DocDB::DBCluster.Port``.
            preferredBackupWindow: ``AWS::DocDB::DBCluster.PreferredBackupWindow``.
            preferredMaintenanceWindow: ``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.
            snapshotIdentifier: ``AWS::DocDB::DBCluster.SnapshotIdentifier``.
            storageEncrypted: ``AWS::DocDB::DBCluster.StorageEncrypted``.
            tags: ``AWS::DocDB::DBCluster.Tags``.
            vpcSecurityGroupIds: ``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.

        Stability:
            experimental
        """
        props: CfnDBClusterProps = {}

        if availability_zones is not None:
            props["availabilityZones"] = availability_zones

        if backup_retention_period is not None:
            props["backupRetentionPeriod"] = backup_retention_period

        if db_cluster_identifier is not None:
            props["dbClusterIdentifier"] = db_cluster_identifier

        if db_cluster_parameter_group_name is not None:
            props["dbClusterParameterGroupName"] = db_cluster_parameter_group_name

        if db_subnet_group_name is not None:
            props["dbSubnetGroupName"] = db_subnet_group_name

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

        if snapshot_identifier is not None:
            props["snapshotIdentifier"] = snapshot_identifier

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
    @jsii.member(jsii_name="dbClusterClusterResourceId")
    def db_cluster_cluster_resource_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ClusterResourceId
        """
        return jsii.get(self, "dbClusterClusterResourceId")

    @property
    @jsii.member(jsii_name="dbClusterEndpoint")
    def db_cluster_endpoint(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint
        """
        return jsii.get(self, "dbClusterEndpoint")

    @property
    @jsii.member(jsii_name="dbClusterName")
    def db_cluster_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "dbClusterName")

    @property
    @jsii.member(jsii_name="dbClusterPort")
    def db_cluster_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Port
        """
        return jsii.get(self, "dbClusterPort")

    @property
    @jsii.member(jsii_name="dbClusterReadEndpoint")
    def db_cluster_read_endpoint(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReadEndpoint
        """
        return jsii.get(self, "dbClusterReadEndpoint")

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


class CfnDBClusterParameterGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-docdb.CfnDBClusterParameterGroup"):
    """A CloudFormation ``AWS::DocDB::DBClusterParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DocDB::DBClusterParameterGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: str, family: str, parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token], name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::DocDB::DBClusterParameterGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::DocDB::DBClusterParameterGroup.Description``.
            family: ``AWS::DocDB::DBClusterParameterGroup.Family``.
            parameters: ``AWS::DocDB::DBClusterParameterGroup.Parameters``.
            name: ``AWS::DocDB::DBClusterParameterGroup.Name``.
            tags: ``AWS::DocDB::DBClusterParameterGroup.Tags``.

        Stability:
            experimental
        """
        props: CfnDBClusterParameterGroupProps = {"description": description, "family": family, "parameters": parameters}

        if name is not None:
            props["name"] = name

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
    name: str
    """``AWS::DocDB::DBClusterParameterGroup.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-name
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::DocDB::DBClusterParameterGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-docdb.CfnDBClusterParameterGroupProps", jsii_struct_bases=[_CfnDBClusterParameterGroupProps])
class CfnDBClusterParameterGroupProps(_CfnDBClusterParameterGroupProps):
    """Properties for defining a ``AWS::DocDB::DBClusterParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html
    Stability:
        experimental
    """
    description: str
    """``AWS::DocDB::DBClusterParameterGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-description
    Stability:
        experimental
    """

    family: str
    """``AWS::DocDB::DBClusterParameterGroup.Family``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-family
    Stability:
        experimental
    """

    parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::DocDB::DBClusterParameterGroup.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-parameters
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-docdb.CfnDBClusterProps", jsii_struct_bases=[])
class CfnDBClusterProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::DocDB::DBCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html
    Stability:
        experimental
    """
    availabilityZones: typing.List[str]
    """``AWS::DocDB::DBCluster.AvailabilityZones``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-availabilityzones
    Stability:
        experimental
    """

    backupRetentionPeriod: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::DocDB::DBCluster.BackupRetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-backupretentionperiod
    Stability:
        experimental
    """

    dbClusterIdentifier: str
    """``AWS::DocDB::DBCluster.DBClusterIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusteridentifier
    Stability:
        experimental
    """

    dbClusterParameterGroupName: str
    """``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusterparametergroupname
    Stability:
        experimental
    """

    dbSubnetGroupName: str
    """``AWS::DocDB::DBCluster.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbsubnetgroupname
    Stability:
        experimental
    """

    engineVersion: str
    """``AWS::DocDB::DBCluster.EngineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-engineversion
    Stability:
        experimental
    """

    kmsKeyId: str
    """``AWS::DocDB::DBCluster.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-kmskeyid
    Stability:
        experimental
    """

    masterUsername: str
    """``AWS::DocDB::DBCluster.MasterUsername``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masterusername
    Stability:
        experimental
    """

    masterUserPassword: str
    """``AWS::DocDB::DBCluster.MasterUserPassword``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masteruserpassword
    Stability:
        experimental
    """

    port: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::DocDB::DBCluster.Port``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-port
    Stability:
        experimental
    """

    preferredBackupWindow: str
    """``AWS::DocDB::DBCluster.PreferredBackupWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredbackupwindow
    Stability:
        experimental
    """

    preferredMaintenanceWindow: str
    """``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredmaintenancewindow
    Stability:
        experimental
    """

    snapshotIdentifier: str
    """``AWS::DocDB::DBCluster.SnapshotIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-snapshotidentifier
    Stability:
        experimental
    """

    storageEncrypted: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::DocDB::DBCluster.StorageEncrypted``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-storageencrypted
    Stability:
        experimental
    """

    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::DocDB::DBCluster.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-tags
    Stability:
        experimental
    """

    vpcSecurityGroupIds: typing.List[str]
    """``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-vpcsecuritygroupids
    Stability:
        experimental
    """

class CfnDBInstance(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-docdb.CfnDBInstance"):
    """A CloudFormation ``AWS::DocDB::DBInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DocDB::DBInstance
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, db_cluster_identifier: str, db_instance_class: str, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, availability_zone: typing.Optional[str]=None, db_instance_identifier: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::DocDB::DBInstance``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            dbClusterIdentifier: ``AWS::DocDB::DBInstance.DBClusterIdentifier``.
            dbInstanceClass: ``AWS::DocDB::DBInstance.DBInstanceClass``.
            autoMinorVersionUpgrade: ``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.
            availabilityZone: ``AWS::DocDB::DBInstance.AvailabilityZone``.
            dbInstanceIdentifier: ``AWS::DocDB::DBInstance.DBInstanceIdentifier``.
            preferredMaintenanceWindow: ``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.
            tags: ``AWS::DocDB::DBInstance.Tags``.

        Stability:
            experimental
        """
        props: CfnDBInstanceProps = {"dbClusterIdentifier": db_cluster_identifier, "dbInstanceClass": db_instance_class}

        if auto_minor_version_upgrade is not None:
            props["autoMinorVersionUpgrade"] = auto_minor_version_upgrade

        if availability_zone is not None:
            props["availabilityZone"] = availability_zone

        if db_instance_identifier is not None:
            props["dbInstanceIdentifier"] = db_instance_identifier

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if tags is not None:
            props["tags"] = tags

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
    @jsii.member(jsii_name="dbInstanceEndpoint")
    def db_instance_endpoint(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint
        """
        return jsii.get(self, "dbInstanceEndpoint")

    @property
    @jsii.member(jsii_name="dbInstanceId")
    def db_instance_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "dbInstanceId")

    @property
    @jsii.member(jsii_name="dbInstancePort")
    def db_instance_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Port
        """
        return jsii.get(self, "dbInstancePort")

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


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBInstanceProps(jsii.compat.TypedDict, total=False):
    autoMinorVersionUpgrade: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-autominorversionupgrade
    Stability:
        experimental
    """
    availabilityZone: str
    """``AWS::DocDB::DBInstance.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-availabilityzone
    Stability:
        experimental
    """
    dbInstanceIdentifier: str
    """``AWS::DocDB::DBInstance.DBInstanceIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceidentifier
    Stability:
        experimental
    """
    preferredMaintenanceWindow: str
    """``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-preferredmaintenancewindow
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::DocDB::DBInstance.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-docdb.CfnDBInstanceProps", jsii_struct_bases=[_CfnDBInstanceProps])
class CfnDBInstanceProps(_CfnDBInstanceProps):
    """Properties for defining a ``AWS::DocDB::DBInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html
    Stability:
        experimental
    """
    dbClusterIdentifier: str
    """``AWS::DocDB::DBInstance.DBClusterIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbclusteridentifier
    Stability:
        experimental
    """

    dbInstanceClass: str
    """``AWS::DocDB::DBInstance.DBInstanceClass``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceclass
    Stability:
        experimental
    """

class CfnDBSubnetGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-docdb.CfnDBSubnetGroup"):
    """A CloudFormation ``AWS::DocDB::DBSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DocDB::DBSubnetGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, db_subnet_group_description: str, subnet_ids: typing.List[str], db_subnet_group_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::DocDB::DBSubnetGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            dbSubnetGroupDescription: ``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.
            subnetIds: ``AWS::DocDB::DBSubnetGroup.SubnetIds``.
            dbSubnetGroupName: ``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.
            tags: ``AWS::DocDB::DBSubnetGroup.Tags``.

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
    """``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupname
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::DocDB::DBSubnetGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-docdb.CfnDBSubnetGroupProps", jsii_struct_bases=[_CfnDBSubnetGroupProps])
class CfnDBSubnetGroupProps(_CfnDBSubnetGroupProps):
    """Properties for defining a ``AWS::DocDB::DBSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html
    Stability:
        experimental
    """
    dbSubnetGroupDescription: str
    """``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupdescription
    Stability:
        experimental
    """

    subnetIds: typing.List[str]
    """``AWS::DocDB::DBSubnetGroup.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-subnetids
    Stability:
        experimental
    """

__all__ = ["CfnDBCluster", "CfnDBClusterParameterGroup", "CfnDBClusterParameterGroupProps", "CfnDBClusterProps", "CfnDBInstance", "CfnDBInstanceProps", "CfnDBSubnetGroup", "CfnDBSubnetGroupProps", "__jsii_assembly__"]

publication.publish()
