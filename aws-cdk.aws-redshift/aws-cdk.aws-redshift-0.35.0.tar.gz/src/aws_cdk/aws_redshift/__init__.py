import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-redshift", "0.35.0", __name__, "aws-redshift@0.35.0.jsii.tgz")
class CfnCluster(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-redshift.CfnCluster"):
    """A CloudFormation ``AWS::Redshift::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Redshift::Cluster
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cluster_type: str, db_name: str, master_username: str, master_user_password: str, node_type: str, allow_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, automated_snapshot_retention_period: typing.Optional[jsii.Number]=None, availability_zone: typing.Optional[str]=None, cluster_identifier: typing.Optional[str]=None, cluster_parameter_group_name: typing.Optional[str]=None, cluster_security_groups: typing.Optional[typing.List[str]]=None, cluster_subnet_group_name: typing.Optional[str]=None, cluster_version: typing.Optional[str]=None, elastic_ip: typing.Optional[str]=None, encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, hsm_client_certificate_identifier: typing.Optional[str]=None, hsm_configuration_identifier: typing.Optional[str]=None, iam_roles: typing.Optional[typing.List[str]]=None, kms_key_id: typing.Optional[str]=None, logging_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["LoggingPropertiesProperty"]]]=None, number_of_nodes: typing.Optional[jsii.Number]=None, owner_account: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None, preferred_maintenance_window: typing.Optional[str]=None, publicly_accessible: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, snapshot_cluster_identifier: typing.Optional[str]=None, snapshot_identifier: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::Redshift::Cluster``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            clusterType: ``AWS::Redshift::Cluster.ClusterType``.
            dbName: ``AWS::Redshift::Cluster.DBName``.
            masterUsername: ``AWS::Redshift::Cluster.MasterUsername``.
            masterUserPassword: ``AWS::Redshift::Cluster.MasterUserPassword``.
            nodeType: ``AWS::Redshift::Cluster.NodeType``.
            allowVersionUpgrade: ``AWS::Redshift::Cluster.AllowVersionUpgrade``.
            automatedSnapshotRetentionPeriod: ``AWS::Redshift::Cluster.AutomatedSnapshotRetentionPeriod``.
            availabilityZone: ``AWS::Redshift::Cluster.AvailabilityZone``.
            clusterIdentifier: ``AWS::Redshift::Cluster.ClusterIdentifier``.
            clusterParameterGroupName: ``AWS::Redshift::Cluster.ClusterParameterGroupName``.
            clusterSecurityGroups: ``AWS::Redshift::Cluster.ClusterSecurityGroups``.
            clusterSubnetGroupName: ``AWS::Redshift::Cluster.ClusterSubnetGroupName``.
            clusterVersion: ``AWS::Redshift::Cluster.ClusterVersion``.
            elasticIp: ``AWS::Redshift::Cluster.ElasticIp``.
            encrypted: ``AWS::Redshift::Cluster.Encrypted``.
            hsmClientCertificateIdentifier: ``AWS::Redshift::Cluster.HsmClientCertificateIdentifier``.
            hsmConfigurationIdentifier: ``AWS::Redshift::Cluster.HsmConfigurationIdentifier``.
            iamRoles: ``AWS::Redshift::Cluster.IamRoles``.
            kmsKeyId: ``AWS::Redshift::Cluster.KmsKeyId``.
            loggingProperties: ``AWS::Redshift::Cluster.LoggingProperties``.
            numberOfNodes: ``AWS::Redshift::Cluster.NumberOfNodes``.
            ownerAccount: ``AWS::Redshift::Cluster.OwnerAccount``.
            port: ``AWS::Redshift::Cluster.Port``.
            preferredMaintenanceWindow: ``AWS::Redshift::Cluster.PreferredMaintenanceWindow``.
            publiclyAccessible: ``AWS::Redshift::Cluster.PubliclyAccessible``.
            snapshotClusterIdentifier: ``AWS::Redshift::Cluster.SnapshotClusterIdentifier``.
            snapshotIdentifier: ``AWS::Redshift::Cluster.SnapshotIdentifier``.
            tags: ``AWS::Redshift::Cluster.Tags``.
            vpcSecurityGroupIds: ``AWS::Redshift::Cluster.VpcSecurityGroupIds``.

        Stability:
            experimental
        """
        props: CfnClusterProps = {"clusterType": cluster_type, "dbName": db_name, "masterUsername": master_username, "masterUserPassword": master_user_password, "nodeType": node_type}

        if allow_version_upgrade is not None:
            props["allowVersionUpgrade"] = allow_version_upgrade

        if automated_snapshot_retention_period is not None:
            props["automatedSnapshotRetentionPeriod"] = automated_snapshot_retention_period

        if availability_zone is not None:
            props["availabilityZone"] = availability_zone

        if cluster_identifier is not None:
            props["clusterIdentifier"] = cluster_identifier

        if cluster_parameter_group_name is not None:
            props["clusterParameterGroupName"] = cluster_parameter_group_name

        if cluster_security_groups is not None:
            props["clusterSecurityGroups"] = cluster_security_groups

        if cluster_subnet_group_name is not None:
            props["clusterSubnetGroupName"] = cluster_subnet_group_name

        if cluster_version is not None:
            props["clusterVersion"] = cluster_version

        if elastic_ip is not None:
            props["elasticIp"] = elastic_ip

        if encrypted is not None:
            props["encrypted"] = encrypted

        if hsm_client_certificate_identifier is not None:
            props["hsmClientCertificateIdentifier"] = hsm_client_certificate_identifier

        if hsm_configuration_identifier is not None:
            props["hsmConfigurationIdentifier"] = hsm_configuration_identifier

        if iam_roles is not None:
            props["iamRoles"] = iam_roles

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

        if logging_properties is not None:
            props["loggingProperties"] = logging_properties

        if number_of_nodes is not None:
            props["numberOfNodes"] = number_of_nodes

        if owner_account is not None:
            props["ownerAccount"] = owner_account

        if port is not None:
            props["port"] = port

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if publicly_accessible is not None:
            props["publiclyAccessible"] = publicly_accessible

        if snapshot_cluster_identifier is not None:
            props["snapshotClusterIdentifier"] = snapshot_cluster_identifier

        if snapshot_identifier is not None:
            props["snapshotIdentifier"] = snapshot_identifier

        if tags is not None:
            props["tags"] = tags

        if vpc_security_group_ids is not None:
            props["vpcSecurityGroupIds"] = vpc_security_group_ids

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
    @jsii.member(jsii_name="attrEndpointAddress")
    def attr_endpoint_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint.Address
        """
        return jsii.get(self, "attrEndpointAddress")

    @property
    @jsii.member(jsii_name="attrEndpointPort")
    def attr_endpoint_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint.Port
        """
        return jsii.get(self, "attrEndpointPort")

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
        """``AWS::Redshift::Cluster.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="clusterType")
    def cluster_type(self) -> str:
        """``AWS::Redshift::Cluster.ClusterType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustertype
        Stability:
            experimental
        """
        return jsii.get(self, "clusterType")

    @cluster_type.setter
    def cluster_type(self, value: str):
        return jsii.set(self, "clusterType", value)

    @property
    @jsii.member(jsii_name="dbName")
    def db_name(self) -> str:
        """``AWS::Redshift::Cluster.DBName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-dbname
        Stability:
            experimental
        """
        return jsii.get(self, "dbName")

    @db_name.setter
    def db_name(self, value: str):
        return jsii.set(self, "dbName", value)

    @property
    @jsii.member(jsii_name="masterUsername")
    def master_username(self) -> str:
        """``AWS::Redshift::Cluster.MasterUsername``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-masterusername
        Stability:
            experimental
        """
        return jsii.get(self, "masterUsername")

    @master_username.setter
    def master_username(self, value: str):
        return jsii.set(self, "masterUsername", value)

    @property
    @jsii.member(jsii_name="masterUserPassword")
    def master_user_password(self) -> str:
        """``AWS::Redshift::Cluster.MasterUserPassword``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-masteruserpassword
        Stability:
            experimental
        """
        return jsii.get(self, "masterUserPassword")

    @master_user_password.setter
    def master_user_password(self, value: str):
        return jsii.set(self, "masterUserPassword", value)

    @property
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> str:
        """``AWS::Redshift::Cluster.NodeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-nodetype
        Stability:
            experimental
        """
        return jsii.get(self, "nodeType")

    @node_type.setter
    def node_type(self, value: str):
        return jsii.set(self, "nodeType", value)

    @property
    @jsii.member(jsii_name="allowVersionUpgrade")
    def allow_version_upgrade(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Redshift::Cluster.AllowVersionUpgrade``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-allowversionupgrade
        Stability:
            experimental
        """
        return jsii.get(self, "allowVersionUpgrade")

    @allow_version_upgrade.setter
    def allow_version_upgrade(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "allowVersionUpgrade", value)

    @property
    @jsii.member(jsii_name="automatedSnapshotRetentionPeriod")
    def automated_snapshot_retention_period(self) -> typing.Optional[jsii.Number]:
        """``AWS::Redshift::Cluster.AutomatedSnapshotRetentionPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-automatedsnapshotretentionperiod
        Stability:
            experimental
        """
        return jsii.get(self, "automatedSnapshotRetentionPeriod")

    @automated_snapshot_retention_period.setter
    def automated_snapshot_retention_period(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "automatedSnapshotRetentionPeriod", value)

    @property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-availabilityzone
        Stability:
            experimental
        """
        return jsii.get(self, "availabilityZone")

    @availability_zone.setter
    def availability_zone(self, value: typing.Optional[str]):
        return jsii.set(self, "availabilityZone", value)

    @property
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ClusterIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusteridentifier
        Stability:
            experimental
        """
        return jsii.get(self, "clusterIdentifier")

    @cluster_identifier.setter
    def cluster_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "clusterIdentifier", value)

    @property
    @jsii.member(jsii_name="clusterParameterGroupName")
    def cluster_parameter_group_name(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ClusterParameterGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusterparametergroupname
        Stability:
            experimental
        """
        return jsii.get(self, "clusterParameterGroupName")

    @cluster_parameter_group_name.setter
    def cluster_parameter_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "clusterParameterGroupName", value)

    @property
    @jsii.member(jsii_name="clusterSecurityGroups")
    def cluster_security_groups(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Redshift::Cluster.ClusterSecurityGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustersecuritygroups
        Stability:
            experimental
        """
        return jsii.get(self, "clusterSecurityGroups")

    @cluster_security_groups.setter
    def cluster_security_groups(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "clusterSecurityGroups", value)

    @property
    @jsii.member(jsii_name="clusterSubnetGroupName")
    def cluster_subnet_group_name(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ClusterSubnetGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustersubnetgroupname
        Stability:
            experimental
        """
        return jsii.get(self, "clusterSubnetGroupName")

    @cluster_subnet_group_name.setter
    def cluster_subnet_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "clusterSubnetGroupName", value)

    @property
    @jsii.member(jsii_name="clusterVersion")
    def cluster_version(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ClusterVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusterversion
        Stability:
            experimental
        """
        return jsii.get(self, "clusterVersion")

    @cluster_version.setter
    def cluster_version(self, value: typing.Optional[str]):
        return jsii.set(self, "clusterVersion", value)

    @property
    @jsii.member(jsii_name="elasticIp")
    def elastic_ip(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.ElasticIp``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-elasticip
        Stability:
            experimental
        """
        return jsii.get(self, "elasticIp")

    @elastic_ip.setter
    def elastic_ip(self, value: typing.Optional[str]):
        return jsii.set(self, "elasticIp", value)

    @property
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Redshift::Cluster.Encrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-encrypted
        Stability:
            experimental
        """
        return jsii.get(self, "encrypted")

    @encrypted.setter
    def encrypted(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "encrypted", value)

    @property
    @jsii.member(jsii_name="hsmClientCertificateIdentifier")
    def hsm_client_certificate_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.HsmClientCertificateIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-hsmclientcertidentifier
        Stability:
            experimental
        """
        return jsii.get(self, "hsmClientCertificateIdentifier")

    @hsm_client_certificate_identifier.setter
    def hsm_client_certificate_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "hsmClientCertificateIdentifier", value)

    @property
    @jsii.member(jsii_name="hsmConfigurationIdentifier")
    def hsm_configuration_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.HsmConfigurationIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-HsmConfigurationIdentifier
        Stability:
            experimental
        """
        return jsii.get(self, "hsmConfigurationIdentifier")

    @hsm_configuration_identifier.setter
    def hsm_configuration_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "hsmConfigurationIdentifier", value)

    @property
    @jsii.member(jsii_name="iamRoles")
    def iam_roles(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Redshift::Cluster.IamRoles``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-iamroles
        Stability:
            experimental
        """
        return jsii.get(self, "iamRoles")

    @iam_roles.setter
    def iam_roles(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "iamRoles", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-kmskeyid
        Stability:
            experimental
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="loggingProperties")
    def logging_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["LoggingPropertiesProperty"]]]:
        """``AWS::Redshift::Cluster.LoggingProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-loggingproperties
        Stability:
            experimental
        """
        return jsii.get(self, "loggingProperties")

    @logging_properties.setter
    def logging_properties(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["LoggingPropertiesProperty"]]]):
        return jsii.set(self, "loggingProperties", value)

    @property
    @jsii.member(jsii_name="numberOfNodes")
    def number_of_nodes(self) -> typing.Optional[jsii.Number]:
        """``AWS::Redshift::Cluster.NumberOfNodes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-nodetype
        Stability:
            experimental
        """
        return jsii.get(self, "numberOfNodes")

    @number_of_nodes.setter
    def number_of_nodes(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "numberOfNodes", value)

    @property
    @jsii.member(jsii_name="ownerAccount")
    def owner_account(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.OwnerAccount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-owneraccount
        Stability:
            experimental
        """
        return jsii.get(self, "ownerAccount")

    @owner_account.setter
    def owner_account(self, value: typing.Optional[str]):
        return jsii.set(self, "ownerAccount", value)

    @property
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        """``AWS::Redshift::Cluster.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-port
        Stability:
            experimental
        """
        return jsii.get(self, "port")

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "port", value)

    @property
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.PreferredMaintenanceWindow``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-preferredmaintenancewindow
        Stability:
            experimental
        """
        return jsii.get(self, "preferredMaintenanceWindow")

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: typing.Optional[str]):
        return jsii.set(self, "preferredMaintenanceWindow", value)

    @property
    @jsii.member(jsii_name="publiclyAccessible")
    def publicly_accessible(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Redshift::Cluster.PubliclyAccessible``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-publiclyaccessible
        Stability:
            experimental
        """
        return jsii.get(self, "publiclyAccessible")

    @publicly_accessible.setter
    def publicly_accessible(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "publiclyAccessible", value)

    @property
    @jsii.member(jsii_name="snapshotClusterIdentifier")
    def snapshot_cluster_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.SnapshotClusterIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotclusteridentifier
        Stability:
            experimental
        """
        return jsii.get(self, "snapshotClusterIdentifier")

    @snapshot_cluster_identifier.setter
    def snapshot_cluster_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotClusterIdentifier", value)

    @property
    @jsii.member(jsii_name="snapshotIdentifier")
    def snapshot_identifier(self) -> typing.Optional[str]:
        """``AWS::Redshift::Cluster.SnapshotIdentifier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotidentifier
        Stability:
            experimental
        """
        return jsii.get(self, "snapshotIdentifier")

    @snapshot_identifier.setter
    def snapshot_identifier(self, value: typing.Optional[str]):
        return jsii.set(self, "snapshotIdentifier", value)

    @property
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::Redshift::Cluster.VpcSecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-vpcsecuritygroupids
        Stability:
            experimental
        """
        return jsii.get(self, "vpcSecurityGroupIds")

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "vpcSecurityGroupIds", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LoggingPropertiesProperty(jsii.compat.TypedDict, total=False):
        s3KeyPrefix: str
        """``CfnCluster.LoggingPropertiesProperty.S3KeyPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-redshift-cluster-loggingproperties.html#cfn-redshift-cluster-loggingproperties-s3keyprefix
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnCluster.LoggingPropertiesProperty", jsii_struct_bases=[_LoggingPropertiesProperty])
    class LoggingPropertiesProperty(_LoggingPropertiesProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-redshift-cluster-loggingproperties.html
        Stability:
            experimental
        """
        bucketName: str
        """``CfnCluster.LoggingPropertiesProperty.BucketName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-redshift-cluster-loggingproperties.html#cfn-redshift-cluster-loggingproperties-bucketname
        Stability:
            experimental
        """


class CfnClusterParameterGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-redshift.CfnClusterParameterGroup"):
    """A CloudFormation ``AWS::Redshift::ClusterParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Redshift::ClusterParameterGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: str, parameter_group_family: str, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ParameterProperty"]]]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::Redshift::ClusterParameterGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::Redshift::ClusterParameterGroup.Description``.
            parameterGroupFamily: ``AWS::Redshift::ClusterParameterGroup.ParameterGroupFamily``.
            parameters: ``AWS::Redshift::ClusterParameterGroup.Parameters``.
            tags: ``AWS::Redshift::ClusterParameterGroup.Tags``.

        Stability:
            experimental
        """
        props: CfnClusterParameterGroupProps = {"description": description, "parameterGroupFamily": parameter_group_family}

        if parameters is not None:
            props["parameters"] = parameters

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnClusterParameterGroup, self, [scope, id, props])

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
        """``AWS::Redshift::ClusterParameterGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::Redshift::ClusterParameterGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="parameterGroupFamily")
    def parameter_group_family(self) -> str:
        """``AWS::Redshift::ClusterParameterGroup.ParameterGroupFamily``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-parametergroupfamily
        Stability:
            experimental
        """
        return jsii.get(self, "parameterGroupFamily")

    @parameter_group_family.setter
    def parameter_group_family(self, value: str):
        return jsii.set(self, "parameterGroupFamily", value)

    @property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ParameterProperty"]]]]]:
        """``AWS::Redshift::ClusterParameterGroup.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-parameters
        Stability:
            experimental
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ParameterProperty"]]]]]):
        return jsii.set(self, "parameters", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnClusterParameterGroup.ParameterProperty", jsii_struct_bases=[])
    class ParameterProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-property-redshift-clusterparametergroup-parameter.html
        Stability:
            experimental
        """
        parameterName: str
        """``CfnClusterParameterGroup.ParameterProperty.ParameterName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-property-redshift-clusterparametergroup-parameter.html#cfn-redshift-clusterparametergroup-parameter-parametername
        Stability:
            experimental
        """

        parameterValue: str
        """``CfnClusterParameterGroup.ParameterProperty.ParameterValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-property-redshift-clusterparametergroup-parameter.html#cfn-redshift-clusterparametergroup-parameter-parametervalue
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnClusterParameterGroupProps(jsii.compat.TypedDict, total=False):
    parameters: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnClusterParameterGroup.ParameterProperty"]]]
    """``AWS::Redshift::ClusterParameterGroup.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-parameters
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Redshift::ClusterParameterGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnClusterParameterGroupProps", jsii_struct_bases=[_CfnClusterParameterGroupProps])
class CfnClusterParameterGroupProps(_CfnClusterParameterGroupProps):
    """Properties for defining a ``AWS::Redshift::ClusterParameterGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html
    Stability:
        experimental
    """
    description: str
    """``AWS::Redshift::ClusterParameterGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-description
    Stability:
        experimental
    """

    parameterGroupFamily: str
    """``AWS::Redshift::ClusterParameterGroup.ParameterGroupFamily``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clusterparametergroup.html#cfn-redshift-clusterparametergroup-parametergroupfamily
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnClusterProps(jsii.compat.TypedDict, total=False):
    allowVersionUpgrade: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::Redshift::Cluster.AllowVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-allowversionupgrade
    Stability:
        experimental
    """
    automatedSnapshotRetentionPeriod: jsii.Number
    """``AWS::Redshift::Cluster.AutomatedSnapshotRetentionPeriod``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-automatedsnapshotretentionperiod
    Stability:
        experimental
    """
    availabilityZone: str
    """``AWS::Redshift::Cluster.AvailabilityZone``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-availabilityzone
    Stability:
        experimental
    """
    clusterIdentifier: str
    """``AWS::Redshift::Cluster.ClusterIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusteridentifier
    Stability:
        experimental
    """
    clusterParameterGroupName: str
    """``AWS::Redshift::Cluster.ClusterParameterGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusterparametergroupname
    Stability:
        experimental
    """
    clusterSecurityGroups: typing.List[str]
    """``AWS::Redshift::Cluster.ClusterSecurityGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustersecuritygroups
    Stability:
        experimental
    """
    clusterSubnetGroupName: str
    """``AWS::Redshift::Cluster.ClusterSubnetGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustersubnetgroupname
    Stability:
        experimental
    """
    clusterVersion: str
    """``AWS::Redshift::Cluster.ClusterVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clusterversion
    Stability:
        experimental
    """
    elasticIp: str
    """``AWS::Redshift::Cluster.ElasticIp``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-elasticip
    Stability:
        experimental
    """
    encrypted: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::Redshift::Cluster.Encrypted``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-encrypted
    Stability:
        experimental
    """
    hsmClientCertificateIdentifier: str
    """``AWS::Redshift::Cluster.HsmClientCertificateIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-hsmclientcertidentifier
    Stability:
        experimental
    """
    hsmConfigurationIdentifier: str
    """``AWS::Redshift::Cluster.HsmConfigurationIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-HsmConfigurationIdentifier
    Stability:
        experimental
    """
    iamRoles: typing.List[str]
    """``AWS::Redshift::Cluster.IamRoles``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-iamroles
    Stability:
        experimental
    """
    kmsKeyId: str
    """``AWS::Redshift::Cluster.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-kmskeyid
    Stability:
        experimental
    """
    loggingProperties: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.LoggingPropertiesProperty"]
    """``AWS::Redshift::Cluster.LoggingProperties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-loggingproperties
    Stability:
        experimental
    """
    numberOfNodes: jsii.Number
    """``AWS::Redshift::Cluster.NumberOfNodes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-nodetype
    Stability:
        experimental
    """
    ownerAccount: str
    """``AWS::Redshift::Cluster.OwnerAccount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-owneraccount
    Stability:
        experimental
    """
    port: jsii.Number
    """``AWS::Redshift::Cluster.Port``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-port
    Stability:
        experimental
    """
    preferredMaintenanceWindow: str
    """``AWS::Redshift::Cluster.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-preferredmaintenancewindow
    Stability:
        experimental
    """
    publiclyAccessible: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::Redshift::Cluster.PubliclyAccessible``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-publiclyaccessible
    Stability:
        experimental
    """
    snapshotClusterIdentifier: str
    """``AWS::Redshift::Cluster.SnapshotClusterIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotclusteridentifier
    Stability:
        experimental
    """
    snapshotIdentifier: str
    """``AWS::Redshift::Cluster.SnapshotIdentifier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-snapshotidentifier
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Redshift::Cluster.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-tags
    Stability:
        experimental
    """
    vpcSecurityGroupIds: typing.List[str]
    """``AWS::Redshift::Cluster.VpcSecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-vpcsecuritygroupids
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnClusterProps", jsii_struct_bases=[_CfnClusterProps])
class CfnClusterProps(_CfnClusterProps):
    """Properties for defining a ``AWS::Redshift::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html
    Stability:
        experimental
    """
    clusterType: str
    """``AWS::Redshift::Cluster.ClusterType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-clustertype
    Stability:
        experimental
    """

    dbName: str
    """``AWS::Redshift::Cluster.DBName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-dbname
    Stability:
        experimental
    """

    masterUsername: str
    """``AWS::Redshift::Cluster.MasterUsername``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-masterusername
    Stability:
        experimental
    """

    masterUserPassword: str
    """``AWS::Redshift::Cluster.MasterUserPassword``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-masteruserpassword
    Stability:
        experimental
    """

    nodeType: str
    """``AWS::Redshift::Cluster.NodeType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-nodetype
    Stability:
        experimental
    """

class CfnClusterSecurityGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-redshift.CfnClusterSecurityGroup"):
    """A CloudFormation ``AWS::Redshift::ClusterSecurityGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Redshift::ClusterSecurityGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: str, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::Redshift::ClusterSecurityGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::Redshift::ClusterSecurityGroup.Description``.
            tags: ``AWS::Redshift::ClusterSecurityGroup.Tags``.

        Stability:
            experimental
        """
        props: CfnClusterSecurityGroupProps = {"description": description}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnClusterSecurityGroup, self, [scope, id, props])

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
        """``AWS::Redshift::ClusterSecurityGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html#cfn-redshift-clustersecuritygroup-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::Redshift::ClusterSecurityGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html#cfn-redshift-clustersecuritygroup-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: str):
        return jsii.set(self, "description", value)


class CfnClusterSecurityGroupIngress(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-redshift.CfnClusterSecurityGroupIngress"):
    """A CloudFormation ``AWS::Redshift::ClusterSecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Redshift::ClusterSecurityGroupIngress
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cluster_security_group_name: str, cidrip: typing.Optional[str]=None, ec2_security_group_name: typing.Optional[str]=None, ec2_security_group_owner_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Redshift::ClusterSecurityGroupIngress``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            clusterSecurityGroupName: ``AWS::Redshift::ClusterSecurityGroupIngress.ClusterSecurityGroupName``.
            cidrip: ``AWS::Redshift::ClusterSecurityGroupIngress.CIDRIP``.
            ec2SecurityGroupName: ``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupName``.
            ec2SecurityGroupOwnerId: ``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupOwnerId``.

        Stability:
            experimental
        """
        props: CfnClusterSecurityGroupIngressProps = {"clusterSecurityGroupName": cluster_security_group_name}

        if cidrip is not None:
            props["cidrip"] = cidrip

        if ec2_security_group_name is not None:
            props["ec2SecurityGroupName"] = ec2_security_group_name

        if ec2_security_group_owner_id is not None:
            props["ec2SecurityGroupOwnerId"] = ec2_security_group_owner_id

        jsii.create(CfnClusterSecurityGroupIngress, self, [scope, id, props])

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
    @jsii.member(jsii_name="clusterSecurityGroupName")
    def cluster_security_group_name(self) -> str:
        """``AWS::Redshift::ClusterSecurityGroupIngress.ClusterSecurityGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-clustersecuritygroupname
        Stability:
            experimental
        """
        return jsii.get(self, "clusterSecurityGroupName")

    @cluster_security_group_name.setter
    def cluster_security_group_name(self, value: str):
        return jsii.set(self, "clusterSecurityGroupName", value)

    @property
    @jsii.member(jsii_name="cidrip")
    def cidrip(self) -> typing.Optional[str]:
        """``AWS::Redshift::ClusterSecurityGroupIngress.CIDRIP``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-cidrip
        Stability:
            experimental
        """
        return jsii.get(self, "cidrip")

    @cidrip.setter
    def cidrip(self, value: typing.Optional[str]):
        return jsii.set(self, "cidrip", value)

    @property
    @jsii.member(jsii_name="ec2SecurityGroupName")
    def ec2_security_group_name(self) -> typing.Optional[str]:
        """``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-ec2securitygroupname
        Stability:
            experimental
        """
        return jsii.get(self, "ec2SecurityGroupName")

    @ec2_security_group_name.setter
    def ec2_security_group_name(self, value: typing.Optional[str]):
        return jsii.set(self, "ec2SecurityGroupName", value)

    @property
    @jsii.member(jsii_name="ec2SecurityGroupOwnerId")
    def ec2_security_group_owner_id(self) -> typing.Optional[str]:
        """``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupOwnerId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-ec2securitygroupownerid
        Stability:
            experimental
        """
        return jsii.get(self, "ec2SecurityGroupOwnerId")

    @ec2_security_group_owner_id.setter
    def ec2_security_group_owner_id(self, value: typing.Optional[str]):
        return jsii.set(self, "ec2SecurityGroupOwnerId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnClusterSecurityGroupIngressProps(jsii.compat.TypedDict, total=False):
    cidrip: str
    """``AWS::Redshift::ClusterSecurityGroupIngress.CIDRIP``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-cidrip
    Stability:
        experimental
    """
    ec2SecurityGroupName: str
    """``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-ec2securitygroupname
    Stability:
        experimental
    """
    ec2SecurityGroupOwnerId: str
    """``AWS::Redshift::ClusterSecurityGroupIngress.EC2SecurityGroupOwnerId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-ec2securitygroupownerid
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnClusterSecurityGroupIngressProps", jsii_struct_bases=[_CfnClusterSecurityGroupIngressProps])
class CfnClusterSecurityGroupIngressProps(_CfnClusterSecurityGroupIngressProps):
    """Properties for defining a ``AWS::Redshift::ClusterSecurityGroupIngress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html
    Stability:
        experimental
    """
    clusterSecurityGroupName: str
    """``AWS::Redshift::ClusterSecurityGroupIngress.ClusterSecurityGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroupingress.html#cfn-redshift-clustersecuritygroupingress-clustersecuritygroupname
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnClusterSecurityGroupProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Redshift::ClusterSecurityGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html#cfn-redshift-clustersecuritygroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnClusterSecurityGroupProps", jsii_struct_bases=[_CfnClusterSecurityGroupProps])
class CfnClusterSecurityGroupProps(_CfnClusterSecurityGroupProps):
    """Properties for defining a ``AWS::Redshift::ClusterSecurityGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html
    Stability:
        experimental
    """
    description: str
    """``AWS::Redshift::ClusterSecurityGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersecuritygroup.html#cfn-redshift-clustersecuritygroup-description
    Stability:
        experimental
    """

class CfnClusterSubnetGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-redshift.CfnClusterSubnetGroup"):
    """A CloudFormation ``AWS::Redshift::ClusterSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Redshift::ClusterSubnetGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: str, subnet_ids: typing.List[str], tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
        """Create a new ``AWS::Redshift::ClusterSubnetGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            description: ``AWS::Redshift::ClusterSubnetGroup.Description``.
            subnetIds: ``AWS::Redshift::ClusterSubnetGroup.SubnetIds``.
            tags: ``AWS::Redshift::ClusterSubnetGroup.Tags``.

        Stability:
            experimental
        """
        props: CfnClusterSubnetGroupProps = {"description": description, "subnetIds": subnet_ids}

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnClusterSubnetGroup, self, [scope, id, props])

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
        """``AWS::Redshift::ClusterSubnetGroup.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> str:
        """``AWS::Redshift::ClusterSubnetGroup.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-description
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
        """``AWS::Redshift::ClusterSubnetGroup.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-subnetids
        Stability:
            experimental
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[str]):
        return jsii.set(self, "subnetIds", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnClusterSubnetGroupProps(jsii.compat.TypedDict, total=False):
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::Redshift::ClusterSubnetGroup.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-redshift.CfnClusterSubnetGroupProps", jsii_struct_bases=[_CfnClusterSubnetGroupProps])
class CfnClusterSubnetGroupProps(_CfnClusterSubnetGroupProps):
    """Properties for defining a ``AWS::Redshift::ClusterSubnetGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html
    Stability:
        experimental
    """
    description: str
    """``AWS::Redshift::ClusterSubnetGroup.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-description
    Stability:
        experimental
    """

    subnetIds: typing.List[str]
    """``AWS::Redshift::ClusterSubnetGroup.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-clustersubnetgroup.html#cfn-redshift-clustersubnetgroup-subnetids
    Stability:
        experimental
    """

__all__ = ["CfnCluster", "CfnClusterParameterGroup", "CfnClusterParameterGroupProps", "CfnClusterProps", "CfnClusterSecurityGroup", "CfnClusterSecurityGroupIngress", "CfnClusterSecurityGroupIngressProps", "CfnClusterSecurityGroupProps", "CfnClusterSubnetGroup", "CfnClusterSubnetGroupProps", "__jsii_assembly__"]

publication.publish()
