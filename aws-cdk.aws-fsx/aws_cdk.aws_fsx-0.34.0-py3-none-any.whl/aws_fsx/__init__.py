import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-fsx", "0.34.0", __name__, "aws-fsx@0.34.0.jsii.tgz")
class CfnFileSystem(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-fsx.CfnFileSystem"):
    """A CloudFormation ``AWS::FSx::FileSystem``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html
    Stability:
        experimental
    cloudformationResource:
        AWS::FSx::FileSystem
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, backup_id: typing.Optional[str]=None, file_system_type: typing.Optional[str]=None, kms_key_id: typing.Optional[str]=None, lustre_configuration: typing.Optional[typing.Union[typing.Optional["LustreConfigurationProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None, security_group_ids: typing.Optional[typing.List[str]]=None, storage_capacity: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, subnet_ids: typing.Optional[typing.List[str]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, windows_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["WindowsConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::FSx::FileSystem``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            backupId: ``AWS::FSx::FileSystem.BackupId``.
            fileSystemType: ``AWS::FSx::FileSystem.FileSystemType``.
            kmsKeyId: ``AWS::FSx::FileSystem.KmsKeyId``.
            lustreConfiguration: ``AWS::FSx::FileSystem.LustreConfiguration``.
            securityGroupIds: ``AWS::FSx::FileSystem.SecurityGroupIds``.
            storageCapacity: ``AWS::FSx::FileSystem.StorageCapacity``.
            subnetIds: ``AWS::FSx::FileSystem.SubnetIds``.
            tags: ``AWS::FSx::FileSystem.Tags``.
            windowsConfiguration: ``AWS::FSx::FileSystem.WindowsConfiguration``.

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
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "fileSystemId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnFileSystemProps":
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

    @jsii.data_type(jsii_type="@aws-cdk/aws-fsx.CfnFileSystem.LustreConfigurationProperty", jsii_struct_bases=[])
    class LustreConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html
        Stability:
            experimental
        """
        exportPath: str
        """``CfnFileSystem.LustreConfigurationProperty.ExportPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-exportpath
        Stability:
            experimental
        """

        importedFileChunkSize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFileSystem.LustreConfigurationProperty.ImportedFileChunkSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-importedfilechunksize
        Stability:
            experimental
        """

        importPath: str
        """``CfnFileSystem.LustreConfigurationProperty.ImportPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-importpath
        Stability:
            experimental
        """

        weeklyMaintenanceStartTime: str
        """``CfnFileSystem.LustreConfigurationProperty.WeeklyMaintenanceStartTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-lustreconfiguration.html#cfn-fsx-filesystem-lustreconfiguration-weeklymaintenancestarttime
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-fsx.CfnFileSystem.WindowsConfigurationProperty", jsii_struct_bases=[])
    class WindowsConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html
        Stability:
            experimental
        """
        activeDirectoryId: str
        """``CfnFileSystem.WindowsConfigurationProperty.ActiveDirectoryId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-activedirectoryid
        Stability:
            experimental
        """

        automaticBackupRetentionDays: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFileSystem.WindowsConfigurationProperty.AutomaticBackupRetentionDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-automaticbackupretentiondays
        Stability:
            experimental
        """

        copyTagsToBackups: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnFileSystem.WindowsConfigurationProperty.CopyTagsToBackups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-copytagstobackups
        Stability:
            experimental
        """

        dailyAutomaticBackupStartTime: str
        """``CfnFileSystem.WindowsConfigurationProperty.DailyAutomaticBackupStartTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-dailyautomaticbackupstarttime
        Stability:
            experimental
        """

        throughputCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnFileSystem.WindowsConfigurationProperty.ThroughputCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-throughputcapacity
        Stability:
            experimental
        """

        weeklyMaintenanceStartTime: str
        """``CfnFileSystem.WindowsConfigurationProperty.WeeklyMaintenanceStartTime``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-windowsconfiguration.html#cfn-fsx-filesystem-windowsconfiguration-weeklymaintenancestarttime
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-fsx.CfnFileSystemProps", jsii_struct_bases=[])
class CfnFileSystemProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::FSx::FileSystem``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html
    Stability:
        experimental
    """
    backupId: str
    """``AWS::FSx::FileSystem.BackupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-backupid
    Stability:
        experimental
    """

    fileSystemType: str
    """``AWS::FSx::FileSystem.FileSystemType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-filesystemtype
    Stability:
        experimental
    """

    kmsKeyId: str
    """``AWS::FSx::FileSystem.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-kmskeyid
    Stability:
        experimental
    """

    lustreConfiguration: typing.Union["CfnFileSystem.LustreConfigurationProperty", aws_cdk.cdk.Token]
    """``AWS::FSx::FileSystem.LustreConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-lustreconfiguration
    Stability:
        experimental
    """

    securityGroupIds: typing.List[str]
    """``AWS::FSx::FileSystem.SecurityGroupIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-securitygroupids
    Stability:
        experimental
    """

    storageCapacity: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::FSx::FileSystem.StorageCapacity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-storagecapacity
    Stability:
        experimental
    """

    subnetIds: typing.List[str]
    """``AWS::FSx::FileSystem.SubnetIds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-subnetids
    Stability:
        experimental
    """

    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::FSx::FileSystem.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-tags
    Stability:
        experimental
    """

    windowsConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnFileSystem.WindowsConfigurationProperty"]
    """``AWS::FSx::FileSystem.WindowsConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-windowsconfiguration
    Stability:
        experimental
    """

__all__ = ["CfnFileSystem", "CfnFileSystemProps", "__jsii_assembly__"]

publication.publish()
