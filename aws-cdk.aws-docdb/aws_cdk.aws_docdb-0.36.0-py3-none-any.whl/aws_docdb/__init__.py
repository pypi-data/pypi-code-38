import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-docdb", "0.36.0", __name__, "aws-docdb@0.36.0.jsii.tgz")
class CfnDBCluster(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-docdb.CfnDBCluster"):
    """A CloudFormation ``AWS::DocDB::DBCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html
    Stability:
        stable
    cloudformationResource:
        AWS::DocDB::DBCluster
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, availability_zones: typing.Optional[typing.List[str]]=None, backup_retention_period: typing.Optional[jsii.Number]=None, db_cluster_identifier: typing.Optional[str]=None, db_cluster_parameter_group_name: typing.Optional[str]=None, db_subnet_group_name: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, master_username: typing.Optional[str]=None, master_user_password: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, snapshot_identifier: typing.Optional[str]=None, storage_encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::DocDB::DBCluster``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            availability_zones: ``AWS::DocDB::DBCluster.AvailabilityZones``.
            backup_retention_period: ``AWS::DocDB::DBCluster.BackupRetentionPeriod``.
            db_cluster_identifier: ``AWS::DocDB::DBCluster.DBClusterIdentifier``.
            db_cluster_parameter_group_name: ``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.
            db_subnet_group_name: ``AWS::DocDB::DBCluster.DBSubnetGroupName``.
            engine_version: ``AWS::DocDB::DBCluster.EngineVersion``.
            kms_key_id: ``AWS::DocDB::DBCluster.KmsKeyId``.
            master_username: ``AWS::DocDB::DBCluster.MasterUsername``.
            master_user_password: ``AWS::DocDB::DBCluster.MasterUserPassword``.
            port: ``AWS::DocDB::DBCluster.Port``.
            preferred_backup_window: ``AWS::DocDB::DBCluster.PreferredBackupWindow``.
            preferred_maintenance_window: ``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.
            snapshot_identifier: ``AWS::DocDB::DBCluster.SnapshotIdentifier``.
            storage_encrypted: ``AWS::DocDB::DBCluster.StorageEncrypted``.
            tags: ``AWS::DocDB::DBCluster.Tags``.
            vpc_security_group_ids: ``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.

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
    @jsii.member(jsii_name="attrClusterResourceId")
    def attr_cluster_resource_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            ClusterResourceId
        """
        return jsii.get(self, "attrClusterResourceId")

    @property
    @jsii.member(jsii_name="attrEndpoint")
    def attr_endpoint(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Endpoint
        """
        return jsii.get(self, "attrEndpoint")

    @property
    @jsii.member(jsii_name="attrPort")
    def attr_port(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Port
        """
        return jsii.get(self, "attrPort")

    @property
    @jsii.member(jsii_name="attrReadEndpoint")
    def attr_read_endpoint(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            ReadEndpoint
        """
        return jsii.get(self, "attrReadEndpoint")

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
        """``AWS::DocDB::DBCluster.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.Optional[typing.List[str]]:
        """``AWS::DocDB::DBCluster.AvailabilityZones``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-availabilityzones
        Stability:
            stable
        """
        return jsii.get(self, "availabilityZones")

    @availability_zones.setter
    def availability_zones(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "availabilityZones", value)

    @property
    @jsii.member(jsii_name="backupRetentionPeriod")
    def backup_retention_period(self) -> typing.Optional[jsii.Number]:
        """``AWS::DocDB::DBCluster.BackupRetentionPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-backupretentionperiod
        Stability:
            stable
        """
        return jsii.get(self, "backupRetentionPeriod")

    @backup_retention_period.setter
    def backup_retention_period(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "backupRetentionPeriod", value)

    @property
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.DBClusterIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusteridentifier
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
        """``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusterparametergroupname
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
        """``AWS::DocDB::DBCluster.DBSubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbsubnetgroupname
        Stability:
            stable
        """
        return jsii.get(self, "dbSubnetGroupName")

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbSubnetGroupName", value)

    @property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.EngineVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-engineversion
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
        """``AWS::DocDB::DBCluster.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-kmskeyid
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
        """``AWS::DocDB::DBCluster.MasterUsername``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masterusername
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
        """``AWS::DocDB::DBCluster.MasterUserPassword``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masteruserpassword
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
        """``AWS::DocDB::DBCluster.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-port
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
        """``AWS::DocDB::DBCluster.PreferredBackupWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredbackupwindow
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
        """``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredmaintenancewindow
        Stability:
            stable
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)

    @property
    @jsii.member(jsii_name="snapshotIdentifier")
    def snapshot_identifier(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBCluster.SnapshotIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-snapshotidentifier
        Stability:
            stable
        """
        return jsii.get(self, "snapshotIdentifier")

    @snapshot_identifier.setter
    def snapshot_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotIdentifier", value)

    @property
    @jsii.member(jsii_name="storageEncrypted")
    def storage_encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DocDB::DBCluster.StorageEncrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-storageencrypted
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
        """``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-vpcsecuritygroupids
        Stability:
            stable
        """
        return jsii.get(self, "vpcSecurityGroupIds")

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "vpcSecurityGroupIds", value)


class CfnDBClusterParameterGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-docdb.CfnDBClusterParameterGroup"):
    """A CloudFormation ``AWS::DocDB::DBClusterParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html
    Stability:
        stable
    cloudformationResource:
        AWS::DocDB::DBClusterParameterGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, description: str, family: str, parameters: typing.Any, name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
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
        """``AWS::DocDB::DBClusterParameterGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::DocDB::DBClusterParameterGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-description
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
        """``AWS::DocDB::DBClusterParameterGroup.Family``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-family
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
        """``AWS::DocDB::DBClusterParameterGroup.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-parameters
        Stability:
            stable
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Any):
        return jsii.set(self, "parameters", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBClusterParameterGroup.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBClusterParameterGroupProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::DocDB::DBClusterParameterGroup.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-name
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::DocDB::DBClusterParameterGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-docdb.CfnDBClusterParameterGroupProps", jsii_struct_bases=[_CfnDBClusterParameterGroupProps])
class CfnDBClusterParameterGroupProps(_CfnDBClusterParameterGroupProps):
    """Properties for defining a ``AWS::DocDB::DBClusterParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html
    Stability:
        stable
    """
    description: str
    """``AWS::DocDB::DBClusterParameterGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-description
    Stability:
        stable
    """

    family: str
    """``AWS::DocDB::DBClusterParameterGroup.Family``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-family
    Stability:
        stable
    """

    parameters: typing.Any
    """``AWS::DocDB::DBClusterParameterGroup.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbclusterparametergroup.html#cfn-docdb-dbclusterparametergroup-parameters
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-docdb.CfnDBClusterProps", jsii_struct_bases=[])
class CfnDBClusterProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::DocDB::DBCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html
    Stability:
        stable
    """
    availabilityZones: typing.List[str]
    """``AWS::DocDB::DBCluster.AvailabilityZones``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-availabilityzones
    Stability:
        stable
    """

    backupRetentionPeriod: jsii.Number
    """``AWS::DocDB::DBCluster.BackupRetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-backupretentionperiod
    Stability:
        stable
    """

    dbClusterIdentifier: str
    """``AWS::DocDB::DBCluster.DBClusterIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusteridentifier
    Stability:
        stable
    """

    dbClusterParameterGroupName: str
    """``AWS::DocDB::DBCluster.DBClusterParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbclusterparametergroupname
    Stability:
        stable
    """

    dbSubnetGroupName: str
    """``AWS::DocDB::DBCluster.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-dbsubnetgroupname
    Stability:
        stable
    """

    engineVersion: str
    """``AWS::DocDB::DBCluster.EngineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-engineversion
    Stability:
        stable
    """

    kmsKeyId: str
    """``AWS::DocDB::DBCluster.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-kmskeyid
    Stability:
        stable
    """

    masterUsername: str
    """``AWS::DocDB::DBCluster.MasterUsername``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masterusername
    Stability:
        stable
    """

    masterUserPassword: str
    """``AWS::DocDB::DBCluster.MasterUserPassword``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-masteruserpassword
    Stability:
        stable
    """

    port: jsii.Number
    """``AWS::DocDB::DBCluster.Port``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-port
    Stability:
        stable
    """

    preferredBackupWindow: str
    """``AWS::DocDB::DBCluster.PreferredBackupWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredbackupwindow
    Stability:
        stable
    """

    preferredMaintenanceWindow: str
    """``AWS::DocDB::DBCluster.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-preferredmaintenancewindow
    Stability:
        stable
    """

    snapshotIdentifier: str
    """``AWS::DocDB::DBCluster.SnapshotIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-snapshotidentifier
    Stability:
        stable
    """

    storageEncrypted: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::DocDB::DBCluster.StorageEncrypted``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-storageencrypted
    Stability:
        stable
    """

    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::DocDB::DBCluster.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-tags
    Stability:
        stable
    """

    vpcSecurityGroupIds: typing.List[str]
    """``AWS::DocDB::DBCluster.VpcSecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-vpcsecuritygroupids
    Stability:
        stable
    """

class CfnDBInstance(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-docdb.CfnDBInstance"):
    """A CloudFormation ``AWS::DocDB::DBInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html
    Stability:
        stable
    cloudformationResource:
        AWS::DocDB::DBInstance
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, db_cluster_identifier: str, db_instance_class: str, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, availability_zone: typing.Optional[str]=None, db_instance_identifier: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::DocDB::DBInstance``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            db_cluster_identifier: ``AWS::DocDB::DBInstance.DBClusterIdentifier``.
            db_instance_class: ``AWS::DocDB::DBInstance.DBInstanceClass``.
            auto_minor_version_upgrade: ``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.
            availability_zone: ``AWS::DocDB::DBInstance.AvailabilityZone``.
            db_instance_identifier: ``AWS::DocDB::DBInstance.DBInstanceIdentifier``.
            preferred_maintenance_window: ``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.
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
    @jsii.member(jsii_name="attrEndpoint")
    def attr_endpoint(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Endpoint
        """
        return jsii.get(self, "attrEndpoint")

    @property
    @jsii.member(jsii_name="attrPort")
    def attr_port(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Port
        """
        return jsii.get(self, "attrPort")

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
        """``AWS::DocDB::DBInstance.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> str:
        """``AWS::DocDB::DBInstance.DBClusterIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbclusteridentifier
        Stability:
            stable
        """
        return jsii.get(self, "dbClusterIdentifier")

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: str):
        return jsii.set(self, "dbClusterIdentifier", value)

    @property
    @jsii.member(jsii_name="dbInstanceClass")
    def db_instance_class(self) -> str:
        """``AWS::DocDB::DBInstance.DBInstanceClass``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceclass
        Stability:
            stable
        """
        return jsii.get(self, "dbInstanceClass")

    @db_instance_class.setter
    def db_instance_class(self, value: str):
        return jsii.set(self, "dbInstanceClass", value)

    @property
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-autominorversionupgrade
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
        """``AWS::DocDB::DBInstance.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-availabilityzone
        Stability:
            stable
        """
        return jsii.get(self, "availabilityZone")

    @availability_zone.setter
    def availability_zone(self, value: typing.Optional[str]):
        return jsii.set(self, "availabilityZone", value)

    @property
    @jsii.member(jsii_name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBInstance.DBInstanceIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceidentifier
        Stability:
            stable
        """
        return jsii.get(self, "dbInstanceIdentifier")

    @db_instance_identifier.setter
    def db_instance_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "dbInstanceIdentifier", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-preferredmaintenancewindow
        Stability:
            stable
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBInstanceProps(jsii.compat.TypedDict, total=False):
    autoMinorVersionUpgrade: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::DocDB::DBInstance.AutoMinorVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-autominorversionupgrade
    Stability:
        stable
    """
    availabilityZone: str
    """``AWS::DocDB::DBInstance.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-availabilityzone
    Stability:
        stable
    """
    dbInstanceIdentifier: str
    """``AWS::DocDB::DBInstance.DBInstanceIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceidentifier
    Stability:
        stable
    """
    preferredMaintenanceWindow: str
    """``AWS::DocDB::DBInstance.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-preferredmaintenancewindow
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::DocDB::DBInstance.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-docdb.CfnDBInstanceProps", jsii_struct_bases=[_CfnDBInstanceProps])
class CfnDBInstanceProps(_CfnDBInstanceProps):
    """Properties for defining a ``AWS::DocDB::DBInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html
    Stability:
        stable
    """
    dbClusterIdentifier: str
    """``AWS::DocDB::DBInstance.DBClusterIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbclusteridentifier
    Stability:
        stable
    """

    dbInstanceClass: str
    """``AWS::DocDB::DBInstance.DBInstanceClass``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbinstance.html#cfn-docdb-dbinstance-dbinstanceclass
    Stability:
        stable
    """

class CfnDBSubnetGroup(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-docdb.CfnDBSubnetGroup"):
    """A CloudFormation ``AWS::DocDB::DBSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html
    Stability:
        stable
    cloudformationResource:
        AWS::DocDB::DBSubnetGroup
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, db_subnet_group_description: str, subnet_ids: typing.List[str], db_subnet_group_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::DocDB::DBSubnetGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            db_subnet_group_description: ``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.
            subnet_ids: ``AWS::DocDB::DBSubnetGroup.SubnetIds``.
            db_subnet_group_name: ``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.
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
        """``AWS::DocDB::DBSubnetGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="dbSubnetGroupDescription")
    def db_subnet_group_description(self) -> str:
        """``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupdescription
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
        """``AWS::DocDB::DBSubnetGroup.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-subnetids
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
        """``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupname
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
    """``AWS::DocDB::DBSubnetGroup.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupname
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::DocDB::DBSubnetGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-docdb.CfnDBSubnetGroupProps", jsii_struct_bases=[_CfnDBSubnetGroupProps])
class CfnDBSubnetGroupProps(_CfnDBSubnetGroupProps):
    """Properties for defining a ``AWS::DocDB::DBSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html
    Stability:
        stable
    """
    dbSubnetGroupDescription: str
    """``AWS::DocDB::DBSubnetGroup.DBSubnetGroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-dbsubnetgroupdescription
    Stability:
        stable
    """

    subnetIds: typing.List[str]
    """``AWS::DocDB::DBSubnetGroup.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbsubnetgroup.html#cfn-docdb-dbsubnetgroup-subnetids
    Stability:
        stable
    """

__all__ = ["CfnDBCluster", "CfnDBClusterParameterGroup", "CfnDBClusterParameterGroupProps", "CfnDBClusterProps", "CfnDBInstance", "CfnDBInstanceProps", "CfnDBSubnetGroup", "CfnDBSubnetGroupProps", "__jsii_assembly__"]

publication.publish()
