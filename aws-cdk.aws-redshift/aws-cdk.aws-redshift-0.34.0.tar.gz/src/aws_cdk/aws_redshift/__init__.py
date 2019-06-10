import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-redshift", "0.34.0", __name__, "aws-redshift@0.34.0.jsii.tgz")
class CfnCluster(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-redshift.CfnCluster"):
    """A CloudFormation ``AWS::Redshift::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Redshift::Cluster
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cluster_type: str, db_name: str, master_username: str, master_user_password: str, node_type: str, allow_version_upgrade: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, automated_snapshot_retention_period: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, availability_zone: typing.Optional[str]=None, cluster_identifier: typing.Optional[str]=None, cluster_parameter_group_name: typing.Optional[str]=None, cluster_security_groups: typing.Optional[typing.List[str]]=None, cluster_subnet_group_name: typing.Optional[str]=None, cluster_version: typing.Optional[str]=None, elastic_ip: typing.Optional[str]=None, encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, hsm_client_certificate_identifier: typing.Optional[str]=None, hsm_configuration_identifier: typing.Optional[str]=None, iam_roles: typing.Optional[typing.List[str]]=None, kms_key_id: typing.Optional[str]=None, logging_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["LoggingPropertiesProperty"]]]=None, number_of_nodes: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, owner_account: typing.Optional[str]=None, port: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, preferred_maintenance_window: typing.Optional[str]=None, publicly_accessible: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, snapshot_cluster_identifier: typing.Optional[str]=None, snapshot_identifier: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, vpc_security_group_ids: typing.Optional[typing.List[str]]=None) -> None:
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
    @jsii.member(jsii_name="clusterEndpointAddress")
    def cluster_endpoint_address(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint.Address
        """
        return jsii.get(self, "clusterEndpointAddress")

    @property
    @jsii.member(jsii_name="clusterEndpointPort")
    def cluster_endpoint_port(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint.Port
        """
        return jsii.get(self, "clusterEndpointPort")

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "clusterName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnClusterProps":
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, description: str, parameter_group_family: str, parameters: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "ParameterProperty"]]]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None) -> None:
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
    @jsii.member(jsii_name="clusterParameterGroupName")
    def cluster_parameter_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "clusterParameterGroupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnClusterParameterGroupProps":
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
    parameters: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnClusterParameterGroup.ParameterProperty"]]]
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
    allowVersionUpgrade: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::Redshift::Cluster.AllowVersionUpgrade``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-allowversionupgrade
    Stability:
        experimental
    """
    automatedSnapshotRetentionPeriod: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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
    encrypted: typing.Union[bool, aws_cdk.cdk.Token]
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
    loggingProperties: typing.Union[aws_cdk.cdk.Token, "CfnCluster.LoggingPropertiesProperty"]
    """``AWS::Redshift::Cluster.LoggingProperties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-loggingproperties
    Stability:
        experimental
    """
    numberOfNodes: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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
    port: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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
    publiclyAccessible: typing.Union[bool, aws_cdk.cdk.Token]
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
    @jsii.member(jsii_name="clusterSecurityGroupName")
    def cluster_security_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "clusterSecurityGroupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnClusterSecurityGroupProps":
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
    def property_overrides(self) -> "CfnClusterSecurityGroupIngressProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


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
    @jsii.member(jsii_name="clusterSubnetGroupName")
    def cluster_subnet_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "clusterSubnetGroupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnClusterSubnetGroupProps":
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
