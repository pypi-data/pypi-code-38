import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-neptune", "0.35.0", __name__, "aws-neptune@0.35.0.jsii.tgz")
class CfnDBCluster(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-neptune.CfnDBCluster"):
    """A CloudFormation ``AWS::Neptune::DBCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Neptune::DBCluster
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, availability_zones: typing.Optional[typing.List[str]]=None, backup_retention_period: typing.Optional[jsii.Number]=None, db_cluster_identifier: typing.Optional[str]=None, db_cluster_parameter_group_name: typing.Optional[str]=None, db_subnet_group_name: typing.Optional[str]=None, iam_auth_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, kms_key_id: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, snapshot_identifier: typing.Optional[str]=None, storage_encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::Neptune::DBCluster``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            availabilityZones: ``AWS::Neptune::DBCluster.AvailabilityZones``.
            backupRetentionPeriod: ``AWS::Neptune::DBCluster.BackupRetentionPeriod``.
            dbClusterIdentifier: ``AWS::Neptune::DBCluster.DBClusterIdentifier``.
            dbClusterParameterGroupName: ``AWS::Neptune::DBCluster.DBClusterParameterGroupName``.
            dbSubnetGroupName: ``AWS::Neptune::DBCluster.DBSubnetGroupName``.
            iamAuthEnabled: ``AWS::Neptune::DBCluster.IamAuthEnabled``.
            kmsKeyId: ``AWS::Neptune::DBCluster.KmsKeyId``.
            port: ``AWS::Neptune::DBCluster.Port``.
            preferredBackupWindow: ``AWS::Neptune::DBCluster.PreferredBackupWindow``.
            preferredMaintenanceWindow: ``AWS::Neptune::DBCluster.PreferredMaintenanceWindow``.
            snapshotIdentifier: ``AWS::Neptune::DBCluster.SnapshotIdentifier``.
            storageEncrypted: ``AWS::Neptune::DBCluster.StorageEncrypted``.
            tags: ``AWS::Neptune::DBCluster.Tags``.
            vpcSecurityGroupIds: ``AWS::Neptune::DBCluster.VpcSecurityGroupIds``.

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

        if iam_auth_enabled is not None:
            props["iamAuthEnabled"] = iam_auth_enabled

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

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
    @jsii.member(jsii_name="attrClusterResourceId")
    def attr_cluster_resource_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ClusterResourceId
        """
        return jsii.get(self, "attrClusterResourceId")

    @property
    @jsii.member(jsii_name="attrEndpoint")
    def attr_endpoint(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint
        """
        return jsii.get(self, "attrEndpoint")

    @property
    @jsii.member(jsii_name="attrPort")
    def attr_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Port
        """
        return jsii.get(self, "attrPort")

    @property
    @jsii.member(jsii_name="attrReadEndpoint")
    def attr_read_endpoint(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ReadEndpoint
        """
        return jsii.get(self, "attrReadEndpoint")

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
        """``AWS::Neptune::DBCluster.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Neptune::DBCluster.AvailabilityZones``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-availabilityzones
        Stability:
            experimental
        """
        return jsii.get(self, "availabilityZones")

    @availability_zones.setter
    def availability_zones(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "availabilityZones", value)

    @property
    @jsii.member(jsii_name="backupRetentionPeriod")
    def backup_retention_period(self) -> typing.Optional[jsii.Number]:
        """``AWS::Neptune::DBCluster.BackupRetentionPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-backupretentionperiod
        Stability:
            experimental
        """
        return jsii.get(self, "backupRetentionPeriod")

    @backup_retention_period.setter
    def backup_retention_period(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "backupRetentionPeriod", value)

    @property
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBCluster.DBClusterIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-dbclusteridentifier
        Stability:
            experimental
        """
        return jsii.get(self, "dbClusterIdentifier")

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "dbClusterIdentifier", value)

    @property
    @jsii.member(jsii_name="dbClusterParameterGroupName")
    def db_cluster_parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBCluster.DBClusterParameterGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-dbclusterparametergroupname
        Stability:
            experimental
        """
        return jsii.get(self, "dbClusterParameterGroupName")

    @db_cluster_parameter_group_name.setter
    def db_cluster_parameter_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbClusterParameterGroupName", value)

    @property
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBCluster.DBSubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-dbsubnetgroupname
        Stability:
            experimental
        """
        return jsii.get(self, "dbSubnetGroupName")

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbSubnetGroupName", value)

    @property
    @jsii.member(jsii_name="iamAuthEnabled")
    def iam_auth_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Neptune::DBCluster.IamAuthEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-iamauthenabled
        Stability:
            experimental
        """
        return jsii.get(self, "iamAuthEnabled")

    @iam_auth_enabled.setter
    def iam_auth_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "iamAuthEnabled", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBCluster.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-kmskeyid
        Stability:
            experimental
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        """``AWS::Neptune::DBCluster.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-port
        Stability:
            experimental
        """
        return jsii.get(self, "port")

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "port", value)

    @property
    @jsii.member(jsii_name="preferredBackupWindow")
    def preferred_backup_window(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBCluster.PreferredBackupWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-preferredbackupwindow
        Stability:
            experimental
        """
        return jsii.get(self, "preferredBackupWindow")

    @preferred_backup_window.setter
    def preferred_backup_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredBackupWindow", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBCluster.PreferredMaintenanceWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-preferredmaintenancewindow
        Stability:
            experimental
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)

    @property
    @jsii.member(jsii_name="snapshotIdentifier")
    def snapshot_identifier(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBCluster.SnapshotIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-snapshotidentifier
        Stability:
            experimental
        """
        return jsii.get(self, "snapshotIdentifier")

    @snapshot_identifier.setter
    def snapshot_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotIdentifier", value)

    @property
    @jsii.member(jsii_name="storageEncrypted")
    def storage_encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Neptune::DBCluster.StorageEncrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-storageencrypted
        Stability:
            experimental
        """
        return jsii.get(self, "storageEncrypted")

    @storage_encrypted.setter
    def storage_encrypted(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "storageEncrypted", value)

    @property
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Neptune::DBCluster.VpcSecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-vpcsecuritygroupids
        Stability:
            experimental
        """
        return jsii.get(self, "vpcSecurityGroupIds")

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "vpcSecurityGroupIds", value)


class CfnDBClusterParameterGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-neptune.CfnDBClusterParameterGroup"):
    """A CloudFormation ``AWS::Neptune::DBClusterParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbclusterparametergroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Neptune::DBClusterParameterGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: str, family: str, parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable], name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::Neptune::DBClusterParameterGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::Neptune::DBClusterParameterGroup.Description``.
            family: ``AWS::Neptune::DBClusterParameterGroup.Family``.
            parameters: ``AWS::Neptune::DBClusterParameterGroup.Parameters``.
            name: ``AWS::Neptune::DBClusterParameterGroup.Name``.
            tags: ``AWS::Neptune::DBClusterParameterGroup.Tags``.

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::Neptune::DBClusterParameterGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbclusterparametergroup.html#cfn-neptune-dbclusterparametergroup-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::Neptune::DBClusterParameterGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbclusterparametergroup.html#cfn-neptune-dbclusterparametergroup-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="family")
    def family(self) -> str:
        """``AWS::Neptune::DBClusterParameterGroup.Family``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbclusterparametergroup.html#cfn-neptune-dbclusterparametergroup-family
        Stability:
            experimental
        """
        return jsii.get(self, "family")

    @family.setter
    def family(self, value: str):
        return jsii.set(self, "family", value)

    @property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]:
        """``AWS::Neptune::DBClusterParameterGroup.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbclusterparametergroup.html#cfn-neptune-dbclusterparametergroup-parameters
        Stability:
            experimental
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]):
        return jsii.set(self, "parameters", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBClusterParameterGroup.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbclusterparametergroup.html#cfn-neptune-dbclusterparametergroup-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBClusterParameterGroupProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::Neptune::DBClusterParameterGroup.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbclusterparametergroup.html#cfn-neptune-dbclusterparametergroup-name
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Neptune::DBClusterParameterGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbclusterparametergroup.html#cfn-neptune-dbclusterparametergroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-neptune.CfnDBClusterParameterGroupProps", jsii_struct_bases=[_CfnDBClusterParameterGroupProps])
class CfnDBClusterParameterGroupProps(_CfnDBClusterParameterGroupProps):
    """Properties for defining a ``AWS::Neptune::DBClusterParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbclusterparametergroup.html
    Stability:
        experimental
    """
    description: str
    """``AWS::Neptune::DBClusterParameterGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbclusterparametergroup.html#cfn-neptune-dbclusterparametergroup-description
    Stability:
        experimental
    """

    family: str
    """``AWS::Neptune::DBClusterParameterGroup.Family``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbclusterparametergroup.html#cfn-neptune-dbclusterparametergroup-family
    Stability:
        experimental
    """

    parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::Neptune::DBClusterParameterGroup.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbclusterparametergroup.html#cfn-neptune-dbclusterparametergroup-parameters
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-neptune.CfnDBClusterProps", jsii_struct_bases=[])
class CfnDBClusterProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::Neptune::DBCluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html
    Stability:
        experimental
    """
    availabilityZones: typing.List[str]
    """``AWS::Neptune::DBCluster.AvailabilityZones``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-availabilityzones
    Stability:
        experimental
    """

    backupRetentionPeriod: jsii.Number
    """``AWS::Neptune::DBCluster.BackupRetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-backupretentionperiod
    Stability:
        experimental
    """

    dbClusterIdentifier: str
    """``AWS::Neptune::DBCluster.DBClusterIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-dbclusteridentifier
    Stability:
        experimental
    """

    dbClusterParameterGroupName: str
    """``AWS::Neptune::DBCluster.DBClusterParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-dbclusterparametergroupname
    Stability:
        experimental
    """

    dbSubnetGroupName: str
    """``AWS::Neptune::DBCluster.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-dbsubnetgroupname
    Stability:
        experimental
    """

    iamAuthEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::Neptune::DBCluster.IamAuthEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-iamauthenabled
    Stability:
        experimental
    """

    kmsKeyId: str
    """``AWS::Neptune::DBCluster.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-kmskeyid
    Stability:
        experimental
    """

    port: jsii.Number
    """``AWS::Neptune::DBCluster.Port``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-port
    Stability:
        experimental
    """

    preferredBackupWindow: str
    """``AWS::Neptune::DBCluster.PreferredBackupWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-preferredbackupwindow
    Stability:
        experimental
    """

    preferredMaintenanceWindow: str
    """``AWS::Neptune::DBCluster.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-preferredmaintenancewindow
    Stability:
        experimental
    """

    snapshotIdentifier: str
    """``AWS::Neptune::DBCluster.SnapshotIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-snapshotidentifier
    Stability:
        experimental
    """

    storageEncrypted: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::Neptune::DBCluster.StorageEncrypted``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-storageencrypted
    Stability:
        experimental
    """

    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Neptune::DBCluster.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-tags
    Stability:
        experimental
    """

    vpcSecurityGroupIds: typing.List[str]
    """``AWS::Neptune::DBCluster.VpcSecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-vpcsecuritygroupids
    Stability:
        experimental
    """

class CfnDBInstance(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-neptune.CfnDBInstance"):
    """A CloudFormation ``AWS::Neptune::DBInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Neptune::DBInstance
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, db_instance_class: str, allow_major_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, auto_minor_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, availability_zone: typing.Optional[str]=None, db_cluster_identifier: typing.Optional[str]=None, db_instance_identifier: typing.Optional[str]=None, db_parameter_group_name: typing.Optional[str]=None, db_snapshot_identifier: typing.Optional[str]=None, db_subnet_group_name: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::Neptune::DBInstance``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            dbInstanceClass: ``AWS::Neptune::DBInstance.DBInstanceClass``.
            allowMajorVersionUpgrade: ``AWS::Neptune::DBInstance.AllowMajorVersionUpgrade``.
            autoMinorVersionUpgrade: ``AWS::Neptune::DBInstance.AutoMinorVersionUpgrade``.
            availabilityZone: ``AWS::Neptune::DBInstance.AvailabilityZone``.
            dbClusterIdentifier: ``AWS::Neptune::DBInstance.DBClusterIdentifier``.
            dbInstanceIdentifier: ``AWS::Neptune::DBInstance.DBInstanceIdentifier``.
            dbParameterGroupName: ``AWS::Neptune::DBInstance.DBParameterGroupName``.
            dbSnapshotIdentifier: ``AWS::Neptune::DBInstance.DBSnapshotIdentifier``.
            dbSubnetGroupName: ``AWS::Neptune::DBInstance.DBSubnetGroupName``.
            preferredMaintenanceWindow: ``AWS::Neptune::DBInstance.PreferredMaintenanceWindow``.
            tags: ``AWS::Neptune::DBInstance.Tags``.

        Stability:
            experimental
        """
        props: CfnDBInstanceProps = {"dbInstanceClass": db_instance_class}

        if allow_major_version_upgrade is not None:
            props["allowMajorVersionUpgrade"] = allow_major_version_upgrade

        if auto_minor_version_upgrade is not None:
            props["autoMinorVersionUpgrade"] = auto_minor_version_upgrade

        if availability_zone is not None:
            props["availabilityZone"] = availability_zone

        if db_cluster_identifier is not None:
            props["dbClusterIdentifier"] = db_cluster_identifier

        if db_instance_identifier is not None:
            props["dbInstanceIdentifier"] = db_instance_identifier

        if db_parameter_group_name is not None:
            props["dbParameterGroupName"] = db_parameter_group_name

        if db_snapshot_identifier is not None:
            props["dbSnapshotIdentifier"] = db_snapshot_identifier

        if db_subnet_group_name is not None:
            props["dbSubnetGroupName"] = db_subnet_group_name

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
    @jsii.member(jsii_name="attrEndpoint")
    def attr_endpoint(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint
        """
        return jsii.get(self, "attrEndpoint")

    @property
    @jsii.member(jsii_name="attrPort")
    def attr_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Port
        """
        return jsii.get(self, "attrPort")

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
        """``AWS::Neptune::DBInstance.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="dbInstanceClass")
    def db_instance_class(self) -> str:
        """``AWS::Neptune::DBInstance.DBInstanceClass``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-dbinstanceclass
        Stability:
            experimental
        """
        return jsii.get(self, "dbInstanceClass")

    @db_instance_class.setter
    def db_instance_class(self, value: str):
        return jsii.set(self, "dbInstanceClass", value)

    @property
    @jsii.member(jsii_name="allowMajorVersionUpgrade")
    def allow_major_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Neptune::DBInstance.AllowMajorVersionUpgrade``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-allowmajorversionupgrade
        Stability:
            experimental
        """
        return jsii.get(self, "allowMajorVersionUpgrade")

    @allow_major_version_upgrade.setter
    def allow_major_version_upgrade(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "allowMajorVersionUpgrade", value)

    @property
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Neptune::DBInstance.AutoMinorVersionUpgrade``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-autominorversionupgrade
        Stability:
            experimental
        """
        return jsii.get(self, "autoMinorVersionUpgrade")

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "autoMinorVersionUpgrade", value)

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBInstance.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-availabilityzone
        Stability:
            experimental
        """
        return jsii.get(self, "availabilityZone")

    @availability_zone.setter
    def availability_zone(self, value: typing.Optional[str]):
        return jsii.set(self, "availabilityZone", value)

    @property
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBInstance.DBClusterIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-dbclusteridentifier
        Stability:
            experimental
        """
        return jsii.get(self, "dbClusterIdentifier")

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "dbClusterIdentifier", value)

    @property
    @jsii.member(jsii_name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBInstance.DBInstanceIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-dbinstanceidentifier
        Stability:
            experimental
        """
        return jsii.get(self, "dbInstanceIdentifier")

    @db_instance_identifier.setter
    def db_instance_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "dbInstanceIdentifier", value)

    @property
    @jsii.member(jsii_name="dbParameterGroupName")
    def db_parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBInstance.DBParameterGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-dbparametergroupname
        Stability:
            experimental
        """
        return jsii.get(self, "dbParameterGroupName")

    @db_parameter_group_name.setter
    def db_parameter_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbParameterGroupName", value)

    @property
    @jsii.member(jsii_name="dbSnapshotIdentifier")
    def db_snapshot_identifier(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBInstance.DBSnapshotIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-dbsnapshotidentifier
        Stability:
            experimental
        """
        return jsii.get(self, "dbSnapshotIdentifier")

    @db_snapshot_identifier.setter
    def db_snapshot_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "dbSnapshotIdentifier", value)

    @property
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBInstance.DBSubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-dbsubnetgroupname
        Stability:
            experimental
        """
        return jsii.get(self, "dbSubnetGroupName")

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbSubnetGroupName", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBInstance.PreferredMaintenanceWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-preferredmaintenancewindow
        Stability:
            experimental
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBInstanceProps(jsii.compat.TypedDict, total=False):
    allowMajorVersionUpgrade: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::Neptune::DBInstance.AllowMajorVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-allowmajorversionupgrade
    Stability:
        experimental
    """
    autoMinorVersionUpgrade: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::Neptune::DBInstance.AutoMinorVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-autominorversionupgrade
    Stability:
        experimental
    """
    availabilityZone: str
    """``AWS::Neptune::DBInstance.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-availabilityzone
    Stability:
        experimental
    """
    dbClusterIdentifier: str
    """``AWS::Neptune::DBInstance.DBClusterIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-dbclusteridentifier
    Stability:
        experimental
    """
    dbInstanceIdentifier: str
    """``AWS::Neptune::DBInstance.DBInstanceIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-dbinstanceidentifier
    Stability:
        experimental
    """
    dbParameterGroupName: str
    """``AWS::Neptune::DBInstance.DBParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-dbparametergroupname
    Stability:
        experimental
    """
    dbSnapshotIdentifier: str
    """``AWS::Neptune::DBInstance.DBSnapshotIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-dbsnapshotidentifier
    Stability:
        experimental
    """
    dbSubnetGroupName: str
    """``AWS::Neptune::DBInstance.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-dbsubnetgroupname
    Stability:
        experimental
    """
    preferredMaintenanceWindow: str
    """``AWS::Neptune::DBInstance.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-preferredmaintenancewindow
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Neptune::DBInstance.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-neptune.CfnDBInstanceProps", jsii_struct_bases=[_CfnDBInstanceProps])
class CfnDBInstanceProps(_CfnDBInstanceProps):
    """Properties for defining a ``AWS::Neptune::DBInstance``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html
    Stability:
        experimental
    """
    dbInstanceClass: str
    """``AWS::Neptune::DBInstance.DBInstanceClass``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbinstance.html#cfn-neptune-dbinstance-dbinstanceclass
    Stability:
        experimental
    """

class CfnDBParameterGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-neptune.CfnDBParameterGroup"):
    """A CloudFormation ``AWS::Neptune::DBParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbparametergroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Neptune::DBParameterGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: str, family: str, parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable], name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::Neptune::DBParameterGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::Neptune::DBParameterGroup.Description``.
            family: ``AWS::Neptune::DBParameterGroup.Family``.
            parameters: ``AWS::Neptune::DBParameterGroup.Parameters``.
            name: ``AWS::Neptune::DBParameterGroup.Name``.
            tags: ``AWS::Neptune::DBParameterGroup.Tags``.

        Stability:
            experimental
        """
        props: CfnDBParameterGroupProps = {"description": description, "family": family, "parameters": parameters}

        if name is not None:
            props["name"] = name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnDBParameterGroup, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::Neptune::DBParameterGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbparametergroup.html#cfn-neptune-dbparametergroup-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::Neptune::DBParameterGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbparametergroup.html#cfn-neptune-dbparametergroup-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="family")
    def family(self) -> str:
        """``AWS::Neptune::DBParameterGroup.Family``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbparametergroup.html#cfn-neptune-dbparametergroup-family
        Stability:
            experimental
        """
        return jsii.get(self, "family")

    @family.setter
    def family(self, value: str):
        return jsii.set(self, "family", value)

    @property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]:
        """``AWS::Neptune::DBParameterGroup.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbparametergroup.html#cfn-neptune-dbparametergroup-parameters
        Stability:
            experimental
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]):
        return jsii.set(self, "parameters", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBParameterGroup.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbparametergroup.html#cfn-neptune-dbparametergroup-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBParameterGroupProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::Neptune::DBParameterGroup.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbparametergroup.html#cfn-neptune-dbparametergroup-name
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Neptune::DBParameterGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbparametergroup.html#cfn-neptune-dbparametergroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-neptune.CfnDBParameterGroupProps", jsii_struct_bases=[_CfnDBParameterGroupProps])
class CfnDBParameterGroupProps(_CfnDBParameterGroupProps):
    """Properties for defining a ``AWS::Neptune::DBParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbparametergroup.html
    Stability:
        experimental
    """
    description: str
    """``AWS::Neptune::DBParameterGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbparametergroup.html#cfn-neptune-dbparametergroup-description
    Stability:
        experimental
    """

    family: str
    """``AWS::Neptune::DBParameterGroup.Family``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbparametergroup.html#cfn-neptune-dbparametergroup-family
    Stability:
        experimental
    """

    parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::Neptune::DBParameterGroup.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbparametergroup.html#cfn-neptune-dbparametergroup-parameters
    Stability:
        experimental
    """

class CfnDBSubnetGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-neptune.CfnDBSubnetGroup"):
    """A CloudFormation ``AWS::Neptune::DBSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbsubnetgroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Neptune::DBSubnetGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, db_subnet_group_description: str, subnet_ids: typing.List[str], db_subnet_group_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::Neptune::DBSubnetGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            dbSubnetGroupDescription: ``AWS::Neptune::DBSubnetGroup.DBSubnetGroupDescription``.
            subnetIds: ``AWS::Neptune::DBSubnetGroup.SubnetIds``.
            dbSubnetGroupName: ``AWS::Neptune::DBSubnetGroup.DBSubnetGroupName``.
            tags: ``AWS::Neptune::DBSubnetGroup.Tags``.

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::Neptune::DBSubnetGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbsubnetgroup.html#cfn-neptune-dbsubnetgroup-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="dbSubnetGroupDescription")
    def db_subnet_group_description(self) -> str:
        """``AWS::Neptune::DBSubnetGroup.DBSubnetGroupDescription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbsubnetgroup.html#cfn-neptune-dbsubnetgroup-dbsubnetgroupdescription
        Stability:
            experimental
        """
        return jsii.get(self, "dbSubnetGroupDescription")

    @db_subnet_group_description.setter
    def db_subnet_group_description(self, value: str):
        return jsii.set(self, "dbSubnetGroupDescription", value)

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[str]:
        """``AWS::Neptune::DBSubnetGroup.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbsubnetgroup.html#cfn-neptune-dbsubnetgroup-subnetids
        Stability:
            experimental
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[str]):
        return jsii.set(self, "subnetIds", value)

    @property
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::Neptune::DBSubnetGroup.DBSubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbsubnetgroup.html#cfn-neptune-dbsubnetgroup-dbsubnetgroupname
        Stability:
            experimental
        """
        return jsii.get(self, "dbSubnetGroupName")

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "dbSubnetGroupName", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDBSubnetGroupProps(jsii.compat.TypedDict, total=False):
    dbSubnetGroupName: str
    """``AWS::Neptune::DBSubnetGroup.DBSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbsubnetgroup.html#cfn-neptune-dbsubnetgroup-dbsubnetgroupname
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Neptune::DBSubnetGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbsubnetgroup.html#cfn-neptune-dbsubnetgroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-neptune.CfnDBSubnetGroupProps", jsii_struct_bases=[_CfnDBSubnetGroupProps])
class CfnDBSubnetGroupProps(_CfnDBSubnetGroupProps):
    """Properties for defining a ``AWS::Neptune::DBSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbsubnetgroup.html
    Stability:
        experimental
    """
    dbSubnetGroupDescription: str
    """``AWS::Neptune::DBSubnetGroup.DBSubnetGroupDescription``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbsubnetgroup.html#cfn-neptune-dbsubnetgroup-dbsubnetgroupdescription
    Stability:
        experimental
    """

    subnetIds: typing.List[str]
    """``AWS::Neptune::DBSubnetGroup.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbsubnetgroup.html#cfn-neptune-dbsubnetgroup-subnetids
    Stability:
        experimental
    """

__all__ = ["CfnDBCluster", "CfnDBClusterParameterGroup", "CfnDBClusterParameterGroupProps", "CfnDBClusterProps", "CfnDBInstance", "CfnDBInstanceProps", "CfnDBParameterGroup", "CfnDBParameterGroupProps", "CfnDBSubnetGroup", "CfnDBSubnetGroupProps", "__jsii_assembly__"]

publication.publish()
