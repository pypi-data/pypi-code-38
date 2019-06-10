import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-opsworkscm", "0.34.0", __name__, "aws-opsworkscm@0.34.0.jsii.tgz")
class CfnServer(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-opsworkscm.CfnServer"):
    """A CloudFormation ``AWS::OpsWorksCM::Server``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html
    Stability:
        experimental
    cloudformationResource:
        AWS::OpsWorksCM::Server
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, instance_profile_arn: str, instance_type: str, service_role_arn: str, associate_public_ip_address: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, backup_id: typing.Optional[str]=None, backup_retention_count: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, disable_automated_backup: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.Token]]]=None, engine: typing.Optional[str]=None, engine_attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "EngineAttributeProperty"]]]]]=None, engine_model: typing.Optional[str]=None, engine_version: typing.Optional[str]=None, key_pair: typing.Optional[str]=None, preferred_backup_window: typing.Optional[str]=None, preferred_maintenance_window: typing.Optional[str]=None, security_group_ids: typing.Optional[typing.List[str]]=None, server_name: typing.Optional[str]=None, subnet_ids: typing.Optional[typing.List[str]]=None) -> None:
        """Create a new ``AWS::OpsWorksCM::Server``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            instanceProfileArn: ``AWS::OpsWorksCM::Server.InstanceProfileArn``.
            instanceType: ``AWS::OpsWorksCM::Server.InstanceType``.
            serviceRoleArn: ``AWS::OpsWorksCM::Server.ServiceRoleArn``.
            associatePublicIpAddress: ``AWS::OpsWorksCM::Server.AssociatePublicIpAddress``.
            backupId: ``AWS::OpsWorksCM::Server.BackupId``.
            backupRetentionCount: ``AWS::OpsWorksCM::Server.BackupRetentionCount``.
            disableAutomatedBackup: ``AWS::OpsWorksCM::Server.DisableAutomatedBackup``.
            engine: ``AWS::OpsWorksCM::Server.Engine``.
            engineAttributes: ``AWS::OpsWorksCM::Server.EngineAttributes``.
            engineModel: ``AWS::OpsWorksCM::Server.EngineModel``.
            engineVersion: ``AWS::OpsWorksCM::Server.EngineVersion``.
            keyPair: ``AWS::OpsWorksCM::Server.KeyPair``.
            preferredBackupWindow: ``AWS::OpsWorksCM::Server.PreferredBackupWindow``.
            preferredMaintenanceWindow: ``AWS::OpsWorksCM::Server.PreferredMaintenanceWindow``.
            securityGroupIds: ``AWS::OpsWorksCM::Server.SecurityGroupIds``.
            serverName: ``AWS::OpsWorksCM::Server.ServerName``.
            subnetIds: ``AWS::OpsWorksCM::Server.SubnetIds``.

        Stability:
            experimental
        """
        props: CfnServerProps = {"instanceProfileArn": instance_profile_arn, "instanceType": instance_type, "serviceRoleArn": service_role_arn}

        if associate_public_ip_address is not None:
            props["associatePublicIpAddress"] = associate_public_ip_address

        if backup_id is not None:
            props["backupId"] = backup_id

        if backup_retention_count is not None:
            props["backupRetentionCount"] = backup_retention_count

        if disable_automated_backup is not None:
            props["disableAutomatedBackup"] = disable_automated_backup

        if engine is not None:
            props["engine"] = engine

        if engine_attributes is not None:
            props["engineAttributes"] = engine_attributes

        if engine_model is not None:
            props["engineModel"] = engine_model

        if engine_version is not None:
            props["engineVersion"] = engine_version

        if key_pair is not None:
            props["keyPair"] = key_pair

        if preferred_backup_window is not None:
            props["preferredBackupWindow"] = preferred_backup_window

        if preferred_maintenance_window is not None:
            props["preferredMaintenanceWindow"] = preferred_maintenance_window

        if security_group_ids is not None:
            props["securityGroupIds"] = security_group_ids

        if server_name is not None:
            props["serverName"] = server_name

        if subnet_ids is not None:
            props["subnetIds"] = subnet_ids

        jsii.create(CfnServer, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnServerProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="serverArn")
    def server_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "serverArn")

    @property
    @jsii.member(jsii_name="serverEndpoint")
    def server_endpoint(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint
        """
        return jsii.get(self, "serverEndpoint")

    @jsii.data_type(jsii_type="@aws-cdk/aws-opsworkscm.CfnServer.EngineAttributeProperty", jsii_struct_bases=[])
    class EngineAttributeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-opsworkscm-server-engineattribute.html
        Stability:
            experimental
        """
        name: str
        """``CfnServer.EngineAttributeProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-opsworkscm-server-engineattribute.html#cfn-opsworkscm-server-engineattribute-name
        Stability:
            experimental
        """

        value: str
        """``CfnServer.EngineAttributeProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-opsworkscm-server-engineattribute.html#cfn-opsworkscm-server-engineattribute-value
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnServerProps(jsii.compat.TypedDict, total=False):
    associatePublicIpAddress: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::OpsWorksCM::Server.AssociatePublicIpAddress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-associatepublicipaddress
    Stability:
        experimental
    """
    backupId: str
    """``AWS::OpsWorksCM::Server.BackupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-backupid
    Stability:
        experimental
    """
    backupRetentionCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::OpsWorksCM::Server.BackupRetentionCount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-backupretentioncount
    Stability:
        experimental
    """
    disableAutomatedBackup: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::OpsWorksCM::Server.DisableAutomatedBackup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-disableautomatedbackup
    Stability:
        experimental
    """
    engine: str
    """``AWS::OpsWorksCM::Server.Engine``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-engine
    Stability:
        experimental
    """
    engineAttributes: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnServer.EngineAttributeProperty"]]]
    """``AWS::OpsWorksCM::Server.EngineAttributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-engineattributes
    Stability:
        experimental
    """
    engineModel: str
    """``AWS::OpsWorksCM::Server.EngineModel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-enginemodel
    Stability:
        experimental
    """
    engineVersion: str
    """``AWS::OpsWorksCM::Server.EngineVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-engineversion
    Stability:
        experimental
    """
    keyPair: str
    """``AWS::OpsWorksCM::Server.KeyPair``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-keypair
    Stability:
        experimental
    """
    preferredBackupWindow: str
    """``AWS::OpsWorksCM::Server.PreferredBackupWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-preferredbackupwindow
    Stability:
        experimental
    """
    preferredMaintenanceWindow: str
    """``AWS::OpsWorksCM::Server.PreferredMaintenanceWindow``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-preferredmaintenancewindow
    Stability:
        experimental
    """
    securityGroupIds: typing.List[str]
    """``AWS::OpsWorksCM::Server.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-securitygroupids
    Stability:
        experimental
    """
    serverName: str
    """``AWS::OpsWorksCM::Server.ServerName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-servername
    Stability:
        experimental
    """
    subnetIds: typing.List[str]
    """``AWS::OpsWorksCM::Server.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-subnetids
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-opsworkscm.CfnServerProps", jsii_struct_bases=[_CfnServerProps])
class CfnServerProps(_CfnServerProps):
    """Properties for defining a ``AWS::OpsWorksCM::Server``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html
    Stability:
        experimental
    """
    instanceProfileArn: str
    """``AWS::OpsWorksCM::Server.InstanceProfileArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-instanceprofilearn
    Stability:
        experimental
    """

    instanceType: str
    """``AWS::OpsWorksCM::Server.InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-instancetype
    Stability:
        experimental
    """

    serviceRoleArn: str
    """``AWS::OpsWorksCM::Server.ServiceRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworkscm-server.html#cfn-opsworkscm-server-servicerolearn
    Stability:
        experimental
    """

__all__ = ["CfnServer", "CfnServerProps", "__jsii_assembly__"]

publication.publish()
