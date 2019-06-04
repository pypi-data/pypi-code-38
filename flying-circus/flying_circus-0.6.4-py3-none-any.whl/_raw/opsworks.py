"""Raw representations of every data type in the AWS OpsWorks service.

See Also:
    `AWS developer guide for OpsWorks
    <https://docs.aws.amazon.com/opsworks/latest/userguide/index.html>`_

This file is automatically generated, and should not be directly edited.
"""

from attr import attrib
from attr import attrs

from ..core import ATTRSCONFIG
from ..core import Resource
from ..core import ResourceProperties
from ..core import create_object_converter

__all__ = [
    "App",
    "AppProperties",
    "ElasticLoadBalancerAttachment",
    "ElasticLoadBalancerAttachmentProperties",
    "Instance",
    "InstanceProperties",
    "Layer",
    "LayerProperties",
    "Stack",
    "StackProperties",
    "UserProfile",
    "UserProfileProperties",
    "Volume",
    "VolumeProperties",
]


@attrs(**ATTRSCONFIG)
class AppProperties(ResourceProperties):
    AppSource = attrib(default=None)
    Attributes = attrib(default=None)
    DataSources = attrib(default=None)
    Description = attrib(default=None)
    Domains = attrib(default=None)
    EnableSsl = attrib(default=None)
    Environment = attrib(default=None)
    Name = attrib(default=None)
    Shortname = attrib(default=None)
    SslConfiguration = attrib(default=None)
    StackId = attrib(default=None)
    Type = attrib(default=None)


@attrs(**ATTRSCONFIG)
class App(Resource):
    """A App for OpsWorks.

    See Also:
        `AWS Cloud Formation documentation for App
        <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworks-app.html>`_
    """

    RESOURCE_TYPE = "AWS::OpsWorks::App"

    Properties: AppProperties = attrib(
        factory=AppProperties, converter=create_object_converter(AppProperties)
    )


@attrs(**ATTRSCONFIG)
class ElasticLoadBalancerAttachmentProperties(ResourceProperties):
    ElasticLoadBalancerName = attrib(default=None)
    LayerId = attrib(default=None)


@attrs(**ATTRSCONFIG)
class ElasticLoadBalancerAttachment(Resource):
    """A Elastic Load Balancer Attachment for OpsWorks.

    See Also:
        `AWS Cloud Formation documentation for ElasticLoadBalancerAttachment
        <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworks-elbattachment.html>`_
    """

    RESOURCE_TYPE = "AWS::OpsWorks::ElasticLoadBalancerAttachment"

    Properties: ElasticLoadBalancerAttachmentProperties = attrib(
        factory=ElasticLoadBalancerAttachmentProperties,
        converter=create_object_converter(ElasticLoadBalancerAttachmentProperties),
    )


@attrs(**ATTRSCONFIG)
class InstanceProperties(ResourceProperties):
    AgentVersion = attrib(default=None)
    AmiId = attrib(default=None)
    Architecture = attrib(default=None)
    AutoScalingType = attrib(default=None)
    AvailabilityZone = attrib(default=None)
    BlockDeviceMappings = attrib(default=None)
    EbsOptimized = attrib(default=None)
    ElasticIps = attrib(default=None)
    Hostname = attrib(default=None)
    InstallUpdatesOnBoot = attrib(default=None)
    InstanceType = attrib(default=None)
    LayerIds = attrib(default=None)
    Os = attrib(default=None)
    RootDeviceType = attrib(default=None)
    SshKeyName = attrib(default=None)
    StackId = attrib(default=None)
    SubnetId = attrib(default=None)
    Tenancy = attrib(default=None)
    TimeBasedAutoScaling = attrib(default=None)
    VirtualizationType = attrib(default=None)
    Volumes = attrib(default=None)


@attrs(**ATTRSCONFIG)
class Instance(Resource):
    """A Instance for OpsWorks.

    See Also:
        `AWS Cloud Formation documentation for Instance
        <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworks-instance.html>`_
    """

    RESOURCE_TYPE = "AWS::OpsWorks::Instance"

    Properties: InstanceProperties = attrib(
        factory=InstanceProperties,
        converter=create_object_converter(InstanceProperties),
    )


@attrs(**ATTRSCONFIG)
class LayerProperties(ResourceProperties):
    Attributes = attrib(default=None)
    AutoAssignElasticIps = attrib(default=None)
    AutoAssignPublicIps = attrib(default=None)
    CustomInstanceProfileArn = attrib(default=None)
    CustomJson = attrib(default=None)
    CustomRecipes = attrib(default=None)
    CustomSecurityGroupIds = attrib(default=None)
    EnableAutoHealing = attrib(default=None)
    InstallUpdatesOnBoot = attrib(default=None)
    LifecycleEventConfiguration = attrib(default=None)
    LoadBasedAutoScaling = attrib(default=None)
    Name = attrib(default=None)
    Packages = attrib(default=None)
    Shortname = attrib(default=None)
    StackId = attrib(default=None)
    Tags = attrib(default=None)
    Type = attrib(default=None)
    UseEbsOptimizedInstances = attrib(default=None)
    VolumeConfigurations = attrib(default=None)


@attrs(**ATTRSCONFIG)
class Layer(Resource):
    """A Layer for OpsWorks.

    See Also:
        `AWS Cloud Formation documentation for Layer
        <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworks-layer.html>`_
    """

    RESOURCE_TYPE = "AWS::OpsWorks::Layer"

    Properties: LayerProperties = attrib(
        factory=LayerProperties, converter=create_object_converter(LayerProperties)
    )


@attrs(**ATTRSCONFIG)
class StackProperties(ResourceProperties):
    AgentVersion = attrib(default=None)
    Attributes = attrib(default=None)
    ChefConfiguration = attrib(default=None)
    CloneAppIds = attrib(default=None)
    ClonePermissions = attrib(default=None)
    ConfigurationManager = attrib(default=None)
    CustomCookbooksSource = attrib(default=None)
    CustomJson = attrib(default=None)
    DefaultAvailabilityZone = attrib(default=None)
    DefaultInstanceProfileArn = attrib(default=None)
    DefaultOs = attrib(default=None)
    DefaultRootDeviceType = attrib(default=None)
    DefaultSshKeyName = attrib(default=None)
    DefaultSubnetId = attrib(default=None)
    EcsClusterArn = attrib(default=None)
    ElasticIps = attrib(default=None)
    HostnameTheme = attrib(default=None)
    Name = attrib(default=None)
    RdsDbInstances = attrib(default=None)
    ServiceRoleArn = attrib(default=None)
    SourceStackId = attrib(default=None)
    Tags = attrib(default=None)
    UseCustomCookbooks = attrib(default=None)
    UseOpsworksSecurityGroups = attrib(default=None)
    VpcId = attrib(default=None)


@attrs(**ATTRSCONFIG)
class Stack(Resource):
    """A Stack for OpsWorks.

    See Also:
        `AWS Cloud Formation documentation for Stack
        <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworks-stack.html>`_
    """

    RESOURCE_TYPE = "AWS::OpsWorks::Stack"

    Properties: StackProperties = attrib(
        factory=StackProperties, converter=create_object_converter(StackProperties)
    )


@attrs(**ATTRSCONFIG)
class UserProfileProperties(ResourceProperties):
    AllowSelfManagement = attrib(default=None)
    IamUserArn = attrib(default=None)
    SshPublicKey = attrib(default=None)
    SshUsername = attrib(default=None)


@attrs(**ATTRSCONFIG)
class UserProfile(Resource):
    """A User Profile for OpsWorks.

    See Also:
        `AWS Cloud Formation documentation for UserProfile
        <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworks-userprofile.html>`_
    """

    RESOURCE_TYPE = "AWS::OpsWorks::UserProfile"

    Properties: UserProfileProperties = attrib(
        factory=UserProfileProperties,
        converter=create_object_converter(UserProfileProperties),
    )


@attrs(**ATTRSCONFIG)
class VolumeProperties(ResourceProperties):
    Ec2VolumeId = attrib(default=None)
    MountPoint = attrib(default=None)
    Name = attrib(default=None)
    StackId = attrib(default=None)


@attrs(**ATTRSCONFIG)
class Volume(Resource):
    """A Volume for OpsWorks.

    See Also:
        `AWS Cloud Formation documentation for Volume
        <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opsworks-volume.html>`_
    """

    RESOURCE_TYPE = "AWS::OpsWorks::Volume"

    Properties: VolumeProperties = attrib(
        factory=VolumeProperties, converter=create_object_converter(VolumeProperties)
    )
