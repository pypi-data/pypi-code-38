import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-fsx", "0.36.0", __name__, "aws-fsx@0.36.0.jsii.tgz")
class CfnFileSystem(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-fsx.CfnFileSystem"):
    """A CloudFormation ``AWS::FSx::FileSystem``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html
    Stability:
        stable
    cloudformationResource:
        AWS::FSx::FileSystem
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, backup_id: typing.Optional[str]=None, file_system_type: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, lustre_configuration: typing.Optional[typing.Union[typing.Optional["LustreConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, security_group_ids: typing.Optional[typing.List[str]]=None, storage_capacity: typing.Optional[jsii.Number]=None, subnet_ids: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, windows_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["WindowsConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::FSx::FileSystem``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            backup_id: ``AWS::FSx::FileSystem.BackupId``.
            file_system_type: ``AWS::FSx::FileSystem.FileSystemType``.
            kms_key_id: ``AWS::FSx::FileSystem.KmsKeyId``.
            lustre_configuration: ``AWS::FSx::FileSystem.LustreConfiguration``.
            security_group_ids: ``AWS::FSx::FileSystem.SecurityGroupIds``.
            storage_capacity: ``AWS::FSx::FileSystem.StorageCapacity``.
            subnet_ids: ``AWS::FSx::FileSystem.SubnetIds``.
            tags: ``AWS::FSx::FileSystem.Tags``.
            windows_configuration: ``AWS::FSx::FileSystem.WindowsConfiguration``.

        Stability:
            experimental
        """
        props: CfnFileSystemProps = {}

        if backup_id is not None:
            props["backupId"] = backup_id

        if file_system_type is not None:
            props["fileSystemType"] = file_system_type

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

        if lustre_configuration is not None:
            props["lustreConfiguration"] = lustre_configuration

        if security_group_ids is not None:
            props["securityGroupIds"] = security_group_ids

        if storage_capacity is not None:
            props["storageCapacity"] = storage_capacity

        if subnet_ids is not None:
            props["subnetIds"] = subnet_ids

        if tags is not None:
            props["tags"] = tags

        if windows_configuration is not None:
            props["windowsConfiguration"] = windows_configuration

        jsii.create(CfnFileSystem, self, [scope, id, props])

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
        """``AWS::FSx::FileSystem.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="backupId")
    def backup_id(self) -> typing.Optional[str]:
        """``AWS::FSx::FileSystem.BackupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-backupid
        Stability:
            stable
        """
        return jsii.get(self, "backupId")

    @backup_id.setter
    def backup_id(self, value: typing.Optional[str]):
        return jsii.set(self, "backupId", value)

    @property
    @jsii.member(jsii_name="fileSystemType")
    def file_system_type(self) -> typing.Optional[str]:
        """``AWS::FSx::FileSystem.FileSystemType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-filesystemtype
        Stability:
            stable
        """
        return jsii.get(self, "fileSystemType")

    @file_system_type.setter
    def file_system_type(self, value: typing.Optional[str]):
        return jsii.set(self, "fileSystemType", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::FSx::FileSystem.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-kmskeyid
        Stability:
            stable
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="lustreConfiguration")
    def lustre_configuration(self) -> typing.Optional[typing.Union[typing.Optional["LustreConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::FSx::FileSystem.LustreConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-lustreconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "lustreConfiguration")

    @lustre_configuration.setter
    def lustre_configuration(self, value: typing.Optional[typing.Union[typing.Optional["LustreConfigurationProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "lustreConfiguration", value)

    @property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::FSx::FileSystem.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-securitygroupids
        Stability:
            stable
        """
        return jsii.get(self, "securityGroupIds")

    @security_group_ids.setter
    def security_group_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "securityGroupIds", value)

    @property
    @jsii.member(jsii_name="storageCapacity")
    def storage_capacity(self) -> typing.Optional[jsii.Number]:
        """``AWS::FSx::FileSystem.StorageCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-storagecapacity
        Stability:
            stable
        """
        return jsii.get(self, "storageCapacity")

    @storage_capacity.setter
    def storage_capacity(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "storageCapacity", value)

    @property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.Optional[typing.List[str]]:
        """``AWS::FSx::FileSystem.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-subnetids
        Stability:
            stable
        """
        return jsii.get(self, "subnetIds")

    @subnet_ids.setter
    def subnet_ids(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "subnetIds", value)

    @property
    @jsii.member(jsii_name="windowsConfiguration")
    def windows_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["WindowsConfigurationProperty"]]]:
        """``AWS::FSx::FileSystem.WindowsConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-windowsconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "windowsConfiguration")

    @windows_configuration.setter
    def windows_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["WindowsConfigurationProperty"]]]):
        return jsii.set(self, "windowsConfiguration", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-fsx.CfnFileSystem.LustreConfigurationProperty", jsii_struct_bases=[])
    class LustreConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html
        Stability:
            stable
        """
        exportPath: str
        """``CfnFileSystem.LustreConfigurationProperty.ExportPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-exportpath
        Stability:
            stable
        """

        importedFileChunkSize: jsii.Number
        """``CfnFileSystem.LustreConfigurationProperty.ImportedFileChunkSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-importedfilechunksize
        Stability:
            stable
        """

        importPath: str
        """``CfnFileSystem.LustreConfigurationProperty.ImportPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-importpath
        Stability:
            stable
        """

        weeklyMaintenanceStartTime: str
        """``CfnFileSystem.LustreConfigurationProperty.WeeklyMaintenanceStartTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-weeklymaintenancestarttime
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-fsx.CfnFileSystem.WindowsConfigurationProperty", jsii_struct_bases=[])
    class WindowsConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html
        Stability:
            stable
        """
        activeDirectoryId: str
        """``CfnFileSystem.WindowsConfigurationProperty.ActiveDirectoryId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-activedirectoryid
        Stability:
            stable
        """

        automaticBackupRetentionDays: jsii.Number
        """``CfnFileSystem.WindowsConfigurationProperty.AutomaticBackupRetentionDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-automaticbackupretentiondays
        Stability:
            stable
        """

        copyTagsToBackups: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnFileSystem.WindowsConfigurationProperty.CopyTagsToBackups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-copytagstobackups
        Stability:
            stable
        """

        dailyAutomaticBackupStartTime: str
        """``CfnFileSystem.WindowsConfigurationProperty.DailyAutomaticBackupStartTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-dailyautomaticbackupstarttime
        Stability:
            stable
        """

        throughputCapacity: jsii.Number
        """``CfnFileSystem.WindowsConfigurationProperty.ThroughputCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-throughputcapacity
        Stability:
            stable
        """

        weeklyMaintenanceStartTime: str
        """``CfnFileSystem.WindowsConfigurationProperty.WeeklyMaintenanceStartTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-weeklymaintenancestarttime
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-fsx.CfnFileSystemProps", jsii_struct_bases=[])
class CfnFileSystemProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::FSx::FileSystem``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html
    Stability:
        stable
    """
    backupId: str
    """``AWS::FSx::FileSystem.BackupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-backupid
    Stability:
        stable
    """

    fileSystemType: str
    """``AWS::FSx::FileSystem.FileSystemType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-filesystemtype
    Stability:
        stable
    """

    kmsKeyId: str
    """``AWS::FSx::FileSystem.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-kmskeyid
    Stability:
        stable
    """

    lustreConfiguration: typing.Union["CfnFileSystem.LustreConfigurationProperty", aws_cdk.core.IResolvable]
    """``AWS::FSx::FileSystem.LustreConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-lustreconfiguration
    Stability:
        stable
    """

    securityGroupIds: typing.List[str]
    """``AWS::FSx::FileSystem.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-securitygroupids
    Stability:
        stable
    """

    storageCapacity: jsii.Number
    """``AWS::FSx::FileSystem.StorageCapacity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-storagecapacity
    Stability:
        stable
    """

    subnetIds: typing.List[str]
    """``AWS::FSx::FileSystem.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-subnetids
    Stability:
        stable
    """

    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::FSx::FileSystem.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-tags
    Stability:
        stable
    """

    windowsConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnFileSystem.WindowsConfigurationProperty"]
    """``AWS::FSx::FileSystem.WindowsConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-windowsconfiguration
    Stability:
        stable
    """

__all__ = ["CfnFileSystem", "CfnFileSystemProps", "__jsii_assembly__"]

publication.publish()
