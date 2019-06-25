import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-efs", "0.36.0", __name__, "aws-efs@0.36.0.jsii.tgz")
class CfnFileSystem(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-efs.CfnFileSystem"):
    """A CloudFormation ``AWS::EFS::FileSystem``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html
    Stability:
        stable
    cloudformationResource:
        AWS::EFS::FileSystem
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, encrypted: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, file_system_tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ElasticFileSystemTagProperty"]]]]]=None, kms_key_id: typing.Optional[str]=None, lifecycle_policies: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "LifecyclePolicyProperty"]]]]]=None, performance_mode: typing.Optional[str]=None, provisioned_throughput_in_mibps: typing.Optional[jsii.Number]=None, throughput_mode: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EFS::FileSystem``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            encrypted: ``AWS::EFS::FileSystem.Encrypted``.
            file_system_tags: ``AWS::EFS::FileSystem.FileSystemTags``.
            kms_key_id: ``AWS::EFS::FileSystem.KmsKeyId``.
            lifecycle_policies: ``AWS::EFS::FileSystem.LifecyclePolicies``.
            performance_mode: ``AWS::EFS::FileSystem.PerformanceMode``.
            provisioned_throughput_in_mibps: ``AWS::EFS::FileSystem.ProvisionedThroughputInMibps``.
            throughput_mode: ``AWS::EFS::FileSystem.ThroughputMode``.

        Stability:
            experimental
        """
        props: CfnFileSystemProps = {}

        if encrypted is not None:
            props["encrypted"] = encrypted

        if file_system_tags is not None:
            props["fileSystemTags"] = file_system_tags

        if kms_key_id is not None:
            props["kmsKeyId"] = kms_key_id

        if lifecycle_policies is not None:
            props["lifecyclePolicies"] = lifecycle_policies

        if performance_mode is not None:
            props["performanceMode"] = performance_mode

        if provisioned_throughput_in_mibps is not None:
            props["provisionedThroughputInMibps"] = provisioned_throughput_in_mibps

        if throughput_mode is not None:
            props["throughputMode"] = throughput_mode

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
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::EFS::FileSystem.Encrypted``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-encrypted
        Stability:
            stable
        """
        return jsii.get(self, "encrypted")

    @encrypted.setter
    def encrypted(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "encrypted", value)

    @property
    @jsii.member(jsii_name="fileSystemTags")
    def file_system_tags(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ElasticFileSystemTagProperty"]]]]]:
        """``AWS::EFS::FileSystem.FileSystemTags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-filesystemtags
        Stability:
            stable
        """
        return jsii.get(self, "fileSystemTags")

    @file_system_tags.setter
    def file_system_tags(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ElasticFileSystemTagProperty"]]]]]):
        return jsii.set(self, "fileSystemTags", value)

    @property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[str]:
        """``AWS::EFS::FileSystem.KmsKeyId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-kmskeyid
        Stability:
            stable
        """
        return jsii.get(self, "kmsKeyId")

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[str]):
        return jsii.set(self, "kmsKeyId", value)

    @property
    @jsii.member(jsii_name="lifecyclePolicies")
    def lifecycle_policies(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "LifecyclePolicyProperty"]]]]]:
        """``AWS::EFS::FileSystem.LifecyclePolicies``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-lifecyclepolicies
        Stability:
            stable
        """
        return jsii.get(self, "lifecyclePolicies")

    @lifecycle_policies.setter
    def lifecycle_policies(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "LifecyclePolicyProperty"]]]]]):
        return jsii.set(self, "lifecyclePolicies", value)

    @property
    @jsii.member(jsii_name="performanceMode")
    def performance_mode(self) -> typing.Optional[str]:
        """``AWS::EFS::FileSystem.PerformanceMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-performancemode
        Stability:
            stable
        """
        return jsii.get(self, "performanceMode")

    @performance_mode.setter
    def performance_mode(self, value: typing.Optional[str]):
        return jsii.set(self, "performanceMode", value)

    @property
    @jsii.member(jsii_name="provisionedThroughputInMibps")
    def provisioned_throughput_in_mibps(self) -> typing.Optional[jsii.Number]:
        """``AWS::EFS::FileSystem.ProvisionedThroughputInMibps``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-provisionedthroughputinmibps
        Stability:
            stable
        """
        return jsii.get(self, "provisionedThroughputInMibps")

    @provisioned_throughput_in_mibps.setter
    def provisioned_throughput_in_mibps(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "provisionedThroughputInMibps", value)

    @property
    @jsii.member(jsii_name="throughputMode")
    def throughput_mode(self) -> typing.Optional[str]:
        """``AWS::EFS::FileSystem.ThroughputMode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-throughputmode
        Stability:
            stable
        """
        return jsii.get(self, "throughputMode")

    @throughput_mode.setter
    def throughput_mode(self, value: typing.Optional[str]):
        return jsii.set(self, "throughputMode", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-efs.CfnFileSystem.ElasticFileSystemTagProperty", jsii_struct_bases=[])
    class ElasticFileSystemTagProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-filesystemtags.html
        Stability:
            stable
        """
        key: str
        """``CfnFileSystem.ElasticFileSystemTagProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-filesystemtags.html#cfn-efs-filesystem-filesystemtags-key
        Stability:
            stable
        """

        value: str
        """``CfnFileSystem.ElasticFileSystemTagProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-efs-filesystem-filesystemtags.html#cfn-efs-filesystem-filesystemtags-value
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-efs.CfnFileSystem.LifecyclePolicyProperty", jsii_struct_bases=[])
    class LifecyclePolicyProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticfilesystem-filesystem-lifecyclepolicy.html
        Stability:
            stable
        """
        transitionToIa: str
        """``CfnFileSystem.LifecyclePolicyProperty.TransitionToIA``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticfilesystem-filesystem-lifecyclepolicy.html#cfn-elasticfilesystem-filesystem-lifecyclepolicy-transitiontoia
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-efs.CfnFileSystemProps", jsii_struct_bases=[])
class CfnFileSystemProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::EFS::FileSystem``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html
    Stability:
        stable
    """
    encrypted: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::EFS::FileSystem.Encrypted``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-encrypted
    Stability:
        stable
    """

    fileSystemTags: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFileSystem.ElasticFileSystemTagProperty"]]]
    """``AWS::EFS::FileSystem.FileSystemTags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-filesystemtags
    Stability:
        stable
    """

    kmsKeyId: str
    """``AWS::EFS::FileSystem.KmsKeyId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-kmskeyid
    Stability:
        stable
    """

    lifecyclePolicies: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnFileSystem.LifecyclePolicyProperty"]]]
    """``AWS::EFS::FileSystem.LifecyclePolicies``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-lifecyclepolicies
    Stability:
        stable
    """

    performanceMode: str
    """``AWS::EFS::FileSystem.PerformanceMode``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-efs-filesystem-performancemode
    Stability:
        stable
    """

    provisionedThroughputInMibps: jsii.Number
    """``AWS::EFS::FileSystem.ProvisionedThroughputInMibps``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-provisionedthroughputinmibps
    Stability:
        stable
    """

    throughputMode: str
    """``AWS::EFS::FileSystem.ThroughputMode``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-filesystem.html#cfn-elasticfilesystem-filesystem-throughputmode
    Stability:
        stable
    """

class CfnMountTarget(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-efs.CfnMountTarget"):
    """A CloudFormation ``AWS::EFS::MountTarget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html
    Stability:
        stable
    cloudformationResource:
        AWS::EFS::MountTarget
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, file_system_id: str, security_groups: typing.List[str], subnet_id: str, ip_address: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EFS::MountTarget``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            file_system_id: ``AWS::EFS::MountTarget.FileSystemId``.
            security_groups: ``AWS::EFS::MountTarget.SecurityGroups``.
            subnet_id: ``AWS::EFS::MountTarget.SubnetId``.
            ip_address: ``AWS::EFS::MountTarget.IpAddress``.

        Stability:
            experimental
        """
        props: CfnMountTargetProps = {"fileSystemId": file_system_id, "securityGroups": security_groups, "subnetId": subnet_id}

        if ip_address is not None:
            props["ipAddress"] = ip_address

        jsii.create(CfnMountTarget, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrIpAddress")
    def attr_ip_address(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            IpAddress
        """
        return jsii.get(self, "attrIpAddress")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> str:
        """``AWS::EFS::MountTarget.FileSystemId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-filesystemid
        Stability:
            stable
        """
        return jsii.get(self, "fileSystemId")

    @file_system_id.setter
    def file_system_id(self, value: str):
        return jsii.set(self, "fileSystemId", value)

    @property
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[str]:
        """``AWS::EFS::MountTarget.SecurityGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-securitygroups
        Stability:
            stable
        """
        return jsii.get(self, "securityGroups")

    @security_groups.setter
    def security_groups(self, value: typing.List[str]):
        return jsii.set(self, "securityGroups", value)

    @property
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        """``AWS::EFS::MountTarget.SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-subnetid
        Stability:
            stable
        """
        return jsii.get(self, "subnetId")

    @subnet_id.setter
    def subnet_id(self, value: str):
        return jsii.set(self, "subnetId", value)

    @property
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> typing.Optional[str]:
        """``AWS::EFS::MountTarget.IpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-ipaddress
        Stability:
            stable
        """
        return jsii.get(self, "ipAddress")

    @ip_address.setter
    def ip_address(self, value: typing.Optional[str]):
        return jsii.set(self, "ipAddress", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnMountTargetProps(jsii.compat.TypedDict, total=False):
    ipAddress: str
    """``AWS::EFS::MountTarget.IpAddress``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-ipaddress
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-efs.CfnMountTargetProps", jsii_struct_bases=[_CfnMountTargetProps])
class CfnMountTargetProps(_CfnMountTargetProps):
    """Properties for defining a ``AWS::EFS::MountTarget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html
    Stability:
        stable
    """
    fileSystemId: str
    """``AWS::EFS::MountTarget.FileSystemId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-filesystemid
    Stability:
        stable
    """

    securityGroups: typing.List[str]
    """``AWS::EFS::MountTarget.SecurityGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-securitygroups
    Stability:
        stable
    """

    subnetId: str
    """``AWS::EFS::MountTarget.SubnetId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-efs-mounttarget.html#cfn-efs-mounttarget-subnetid
    Stability:
        stable
    """

__all__ = ["CfnFileSystem", "CfnFileSystemProps", "CfnMountTarget", "CfnMountTargetProps", "__jsii_assembly__"]

publication.publish()
