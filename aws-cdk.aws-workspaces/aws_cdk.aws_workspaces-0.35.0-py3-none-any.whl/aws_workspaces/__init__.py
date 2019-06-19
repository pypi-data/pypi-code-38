import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-workspaces", "0.35.0", __name__, "aws-workspaces@0.35.0.jsii.tgz")
class CfnWorkspace(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-workspaces.CfnWorkspace"):
    """A CloudFormation ``AWS::WorkSpaces::Workspace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html
    Stability:
        experimental
    cloudformationResource:
        AWS::WorkSpaces::Workspace
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, bundle_id: str, directory_id: str, user_name: str, root_volume_encryption_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, user_volume_encryption_enabled: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, volume_encryption_key: typing.Optional[str]=None, workspace_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["WorkspacePropertiesProperty"]]]=None) -> None:
        """Create a new ``AWS::WorkSpaces::Workspace``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            bundleId: ``AWS::WorkSpaces::Workspace.BundleId``.
            directoryId: ``AWS::WorkSpaces::Workspace.DirectoryId``.
            userName: ``AWS::WorkSpaces::Workspace.UserName``.
            rootVolumeEncryptionEnabled: ``AWS::WorkSpaces::Workspace.RootVolumeEncryptionEnabled``.
            tags: ``AWS::WorkSpaces::Workspace.Tags``.
            userVolumeEncryptionEnabled: ``AWS::WorkSpaces::Workspace.UserVolumeEncryptionEnabled``.
            volumeEncryptionKey: ``AWS::WorkSpaces::Workspace.VolumeEncryptionKey``.
            workspaceProperties: ``AWS::WorkSpaces::Workspace.WorkspaceProperties``.

        Stability:
            experimental
        """
        props: CfnWorkspaceProps = {"bundleId": bundle_id, "directoryId": directory_id, "userName": user_name}

        if root_volume_encryption_enabled is not None:
            props["rootVolumeEncryptionEnabled"] = root_volume_encryption_enabled

        if tags is not None:
            props["tags"] = tags

        if user_volume_encryption_enabled is not None:
            props["userVolumeEncryptionEnabled"] = user_volume_encryption_enabled

        if volume_encryption_key is not None:
            props["volumeEncryptionKey"] = volume_encryption_key

        if workspace_properties is not None:
            props["workspaceProperties"] = workspace_properties

        jsii.create(CfnWorkspace, self, [scope, id, props])

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
        """``AWS::WorkSpaces::Workspace.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> str:
        """``AWS::WorkSpaces::Workspace.BundleId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-bundleid
        Stability:
            experimental
        """
        return jsii.get(self, "bundleId")

    @bundle_id.setter
    def bundle_id(self, value: str):
        return jsii.set(self, "bundleId", value)

    @property
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> str:
        """``AWS::WorkSpaces::Workspace.DirectoryId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-directoryid
        Stability:
            experimental
        """
        return jsii.get(self, "directoryId")

    @directory_id.setter
    def directory_id(self, value: str):
        return jsii.set(self, "directoryId", value)

    @property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> str:
        """``AWS::WorkSpaces::Workspace.UserName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-username
        Stability:
            experimental
        """
        return jsii.get(self, "userName")

    @user_name.setter
    def user_name(self, value: str):
        return jsii.set(self, "userName", value)

    @property
    @jsii.member(jsii_name="rootVolumeEncryptionEnabled")
    def root_volume_encryption_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::WorkSpaces::Workspace.RootVolumeEncryptionEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-rootvolumeencryptionenabled
        Stability:
            experimental
        """
        return jsii.get(self, "rootVolumeEncryptionEnabled")

    @root_volume_encryption_enabled.setter
    def root_volume_encryption_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "rootVolumeEncryptionEnabled", value)

    @property
    @jsii.member(jsii_name="userVolumeEncryptionEnabled")
    def user_volume_encryption_enabled(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::WorkSpaces::Workspace.UserVolumeEncryptionEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-uservolumeencryptionenabled
        Stability:
            experimental
        """
        return jsii.get(self, "userVolumeEncryptionEnabled")

    @user_volume_encryption_enabled.setter
    def user_volume_encryption_enabled(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "userVolumeEncryptionEnabled", value)

    @property
    @jsii.member(jsii_name="volumeEncryptionKey")
    def volume_encryption_key(self) -> typing.Optional[str]:
        """``AWS::WorkSpaces::Workspace.VolumeEncryptionKey``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-volumeencryptionkey
        Stability:
            experimental
        """
        return jsii.get(self, "volumeEncryptionKey")

    @volume_encryption_key.setter
    def volume_encryption_key(self, value: typing.Optional[str]):
        return jsii.set(self, "volumeEncryptionKey", value)

    @property
    @jsii.member(jsii_name="workspaceProperties")
    def workspace_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["WorkspacePropertiesProperty"]]]:
        """``AWS::WorkSpaces::Workspace.WorkspaceProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-workspaceproperties
        Stability:
            experimental
        """
        return jsii.get(self, "workspaceProperties")

    @workspace_properties.setter
    def workspace_properties(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["WorkspacePropertiesProperty"]]]):
        return jsii.set(self, "workspaceProperties", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-workspaces.CfnWorkspace.WorkspacePropertiesProperty", jsii_struct_bases=[])
    class WorkspacePropertiesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-workspaces-workspace-workspaceproperties.html
        Stability:
            experimental
        """
        computeTypeName: str
        """``CfnWorkspace.WorkspacePropertiesProperty.ComputeTypeName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-workspaces-workspace-workspaceproperties.html#cfn-workspaces-workspace-workspaceproperties-computetypename
        Stability:
            experimental
        """

        rootVolumeSizeGib: jsii.Number
        """``CfnWorkspace.WorkspacePropertiesProperty.RootVolumeSizeGib``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-workspaces-workspace-workspaceproperties.html#cfn-workspaces-workspace-workspaceproperties-rootvolumesizegib
        Stability:
            experimental
        """

        runningMode: str
        """``CfnWorkspace.WorkspacePropertiesProperty.RunningMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-workspaces-workspace-workspaceproperties.html#cfn-workspaces-workspace-workspaceproperties-runningmode
        Stability:
            experimental
        """

        runningModeAutoStopTimeoutInMinutes: jsii.Number
        """``CfnWorkspace.WorkspacePropertiesProperty.RunningModeAutoStopTimeoutInMinutes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-workspaces-workspace-workspaceproperties.html#cfn-workspaces-workspace-workspaceproperties-runningmodeautostoptimeoutinminutes
        Stability:
            experimental
        """

        userVolumeSizeGib: jsii.Number
        """``CfnWorkspace.WorkspacePropertiesProperty.UserVolumeSizeGib``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-workspaces-workspace-workspaceproperties.html#cfn-workspaces-workspace-workspaceproperties-uservolumesizegib
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnWorkspaceProps(jsii.compat.TypedDict, total=False):
    rootVolumeEncryptionEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::WorkSpaces::Workspace.RootVolumeEncryptionEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-rootvolumeencryptionenabled
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::WorkSpaces::Workspace.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-tags
    Stability:
        experimental
    """
    userVolumeEncryptionEnabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::WorkSpaces::Workspace.UserVolumeEncryptionEnabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-uservolumeencryptionenabled
    Stability:
        experimental
    """
    volumeEncryptionKey: str
    """``AWS::WorkSpaces::Workspace.VolumeEncryptionKey``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-volumeencryptionkey
    Stability:
        experimental
    """
    workspaceProperties: typing.Union[aws_cdk.cdk.IResolvable, "CfnWorkspace.WorkspacePropertiesProperty"]
    """``AWS::WorkSpaces::Workspace.WorkspaceProperties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-workspaceproperties
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-workspaces.CfnWorkspaceProps", jsii_struct_bases=[_CfnWorkspaceProps])
class CfnWorkspaceProps(_CfnWorkspaceProps):
    """Properties for defining a ``AWS::WorkSpaces::Workspace``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html
    Stability:
        experimental
    """
    bundleId: str
    """``AWS::WorkSpaces::Workspace.BundleId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-bundleid
    Stability:
        experimental
    """

    directoryId: str
    """``AWS::WorkSpaces::Workspace.DirectoryId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-directoryid
    Stability:
        experimental
    """

    userName: str
    """``AWS::WorkSpaces::Workspace.UserName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-workspaces-workspace.html#cfn-workspaces-workspace-username
    Stability:
        experimental
    """

__all__ = ["CfnWorkspace", "CfnWorkspaceProps", "__jsii_assembly__"]

publication.publish()
