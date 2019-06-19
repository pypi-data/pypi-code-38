import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-gamelift", "0.35.0", __name__, "aws-gamelift@0.35.0.jsii.tgz")
class CfnAlias(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-gamelift.CfnAlias"):
    """A CloudFormation ``AWS::GameLift::Alias``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html
    Stability:
        experimental
    cloudformationResource:
        AWS::GameLift::Alias
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, routing_strategy: typing.Union["RoutingStrategyProperty", aws_cdk.cdk.IResolvable], description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::GameLift::Alias``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::GameLift::Alias.Name``.
            routingStrategy: ``AWS::GameLift::Alias.RoutingStrategy``.
            description: ``AWS::GameLift::Alias.Description``.

        Stability:
            experimental
        """
        props: CfnAliasProps = {"name": name, "routingStrategy": routing_strategy}

        if description is not None:
            props["description"] = description

        jsii.create(CfnAlias, self, [scope, id, props])

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
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::GameLift::Alias.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html#cfn-gamelift-alias-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="routingStrategy")
    def routing_strategy(self) -> typing.Union["RoutingStrategyProperty", aws_cdk.cdk.IResolvable]:
        """``AWS::GameLift::Alias.RoutingStrategy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html#cfn-gamelift-alias-routingstrategy
        Stability:
            experimental
        """
        return jsii.get(self, "routingStrategy")

    @routing_strategy.setter
    def routing_strategy(self, value: typing.Union["RoutingStrategyProperty", aws_cdk.cdk.IResolvable]):
        return jsii.set(self, "routingStrategy", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::GameLift::Alias.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html#cfn-gamelift-alias-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _RoutingStrategyProperty(jsii.compat.TypedDict, total=False):
        fleetId: str
        """``CfnAlias.RoutingStrategyProperty.FleetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-alias-routingstrategy.html#cfn-gamelift-alias-routingstrategy-fleetid
        Stability:
            experimental
        """
        message: str
        """``CfnAlias.RoutingStrategyProperty.Message``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-alias-routingstrategy.html#cfn-gamelift-alias-routingstrategy-message
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-gamelift.CfnAlias.RoutingStrategyProperty", jsii_struct_bases=[_RoutingStrategyProperty])
    class RoutingStrategyProperty(_RoutingStrategyProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-alias-routingstrategy.html
        Stability:
            experimental
        """
        type: str
        """``CfnAlias.RoutingStrategyProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-alias-routingstrategy.html#cfn-gamelift-alias-routingstrategy-type
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnAliasProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::GameLift::Alias.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html#cfn-gamelift-alias-description
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-gamelift.CfnAliasProps", jsii_struct_bases=[_CfnAliasProps])
class CfnAliasProps(_CfnAliasProps):
    """Properties for defining a ``AWS::GameLift::Alias``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html
    Stability:
        experimental
    """
    name: str
    """``AWS::GameLift::Alias.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html#cfn-gamelift-alias-name
    Stability:
        experimental
    """

    routingStrategy: typing.Union["CfnAlias.RoutingStrategyProperty", aws_cdk.cdk.IResolvable]
    """``AWS::GameLift::Alias.RoutingStrategy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-alias.html#cfn-gamelift-alias-routingstrategy
    Stability:
        experimental
    """

class CfnBuild(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-gamelift.CfnBuild"):
    """A CloudFormation ``AWS::GameLift::Build``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html
    Stability:
        experimental
    cloudformationResource:
        AWS::GameLift::Build
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: typing.Optional[str]=None, storage_location: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["S3LocationProperty"]]]=None, version: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::GameLift::Build``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::GameLift::Build.Name``.
            storageLocation: ``AWS::GameLift::Build.StorageLocation``.
            version: ``AWS::GameLift::Build.Version``.

        Stability:
            experimental
        """
        props: CfnBuildProps = {}

        if name is not None:
            props["name"] = name

        if storage_location is not None:
            props["storageLocation"] = storage_location

        if version is not None:
            props["version"] = version

        jsii.create(CfnBuild, self, [scope, id, props])

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
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::GameLift::Build.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html#cfn-gamelift-build-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="storageLocation")
    def storage_location(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["S3LocationProperty"]]]:
        """``AWS::GameLift::Build.StorageLocation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html#cfn-gamelift-build-storagelocation
        Stability:
            experimental
        """
        return jsii.get(self, "storageLocation")

    @storage_location.setter
    def storage_location(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["S3LocationProperty"]]]):
        return jsii.set(self, "storageLocation", value)

    @property
    @jsii.member(jsii_name="version")
    def version(self) -> typing.Optional[str]:
        """``AWS::GameLift::Build.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html#cfn-gamelift-build-version
        Stability:
            experimental
        """
        return jsii.get(self, "version")

    @version.setter
    def version(self, value: typing.Optional[str]):
        return jsii.set(self, "version", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-gamelift.CfnBuild.S3LocationProperty", jsii_struct_bases=[])
    class S3LocationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-build-storagelocation.html
        Stability:
            experimental
        """
        bucket: str
        """``CfnBuild.S3LocationProperty.Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-build-storagelocation.html#cfn-gamelift-build-storage-bucket
        Stability:
            experimental
        """

        key: str
        """``CfnBuild.S3LocationProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-build-storagelocation.html#cfn-gamelift-build-storage-key
        Stability:
            experimental
        """

        roleArn: str
        """``CfnBuild.S3LocationProperty.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-build-storagelocation.html#cfn-gamelift-build-storage-rolearn
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-gamelift.CfnBuildProps", jsii_struct_bases=[])
class CfnBuildProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::GameLift::Build``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html
    Stability:
        experimental
    """
    name: str
    """``AWS::GameLift::Build.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html#cfn-gamelift-build-name
    Stability:
        experimental
    """

    storageLocation: typing.Union[aws_cdk.cdk.IResolvable, "CfnBuild.S3LocationProperty"]
    """``AWS::GameLift::Build.StorageLocation``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html#cfn-gamelift-build-storagelocation
    Stability:
        experimental
    """

    version: str
    """``AWS::GameLift::Build.Version``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-build.html#cfn-gamelift-build-version
    Stability:
        experimental
    """

class CfnFleet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-gamelift.CfnFleet"):
    """A CloudFormation ``AWS::GameLift::Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html
    Stability:
        experimental
    cloudformationResource:
        AWS::GameLift::Fleet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, build_id: str, desired_ec2_instances: jsii.Number, ec2_instance_type: str, name: str, server_launch_path: str, description: typing.Optional[str]=None, ec2_inbound_permissions: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "IpPermissionProperty"]]]]]=None, log_paths: typing.Optional[typing.List[str]]=None, max_size: typing.Optional[jsii.Number]=None, min_size: typing.Optional[jsii.Number]=None, server_launch_parameters: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::GameLift::Fleet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            buildId: ``AWS::GameLift::Fleet.BuildId``.
            desiredEc2Instances: ``AWS::GameLift::Fleet.DesiredEC2Instances``.
            ec2InstanceType: ``AWS::GameLift::Fleet.EC2InstanceType``.
            name: ``AWS::GameLift::Fleet.Name``.
            serverLaunchPath: ``AWS::GameLift::Fleet.ServerLaunchPath``.
            description: ``AWS::GameLift::Fleet.Description``.
            ec2InboundPermissions: ``AWS::GameLift::Fleet.EC2InboundPermissions``.
            logPaths: ``AWS::GameLift::Fleet.LogPaths``.
            maxSize: ``AWS::GameLift::Fleet.MaxSize``.
            minSize: ``AWS::GameLift::Fleet.MinSize``.
            serverLaunchParameters: ``AWS::GameLift::Fleet.ServerLaunchParameters``.

        Stability:
            experimental
        """
        props: CfnFleetProps = {"buildId": build_id, "desiredEc2Instances": desired_ec2_instances, "ec2InstanceType": ec2_instance_type, "name": name, "serverLaunchPath": server_launch_path}

        if description is not None:
            props["description"] = description

        if ec2_inbound_permissions is not None:
            props["ec2InboundPermissions"] = ec2_inbound_permissions

        if log_paths is not None:
            props["logPaths"] = log_paths

        if max_size is not None:
            props["maxSize"] = max_size

        if min_size is not None:
            props["minSize"] = min_size

        if server_launch_parameters is not None:
            props["serverLaunchParameters"] = server_launch_parameters

        jsii.create(CfnFleet, self, [scope, id, props])

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
    @jsii.member(jsii_name="buildId")
    def build_id(self) -> str:
        """``AWS::GameLift::Fleet.BuildId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-buildid
        Stability:
            experimental
        """
        return jsii.get(self, "buildId")

    @build_id.setter
    def build_id(self, value: str):
        return jsii.set(self, "buildId", value)

    @property
    @jsii.member(jsii_name="desiredEc2Instances")
    def desired_ec2_instances(self) -> jsii.Number:
        """``AWS::GameLift::Fleet.DesiredEC2Instances``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-desiredec2instances
        Stability:
            experimental
        """
        return jsii.get(self, "desiredEc2Instances")

    @desired_ec2_instances.setter
    def desired_ec2_instances(self, value: jsii.Number):
        return jsii.set(self, "desiredEc2Instances", value)

    @property
    @jsii.member(jsii_name="ec2InstanceType")
    def ec2_instance_type(self) -> str:
        """``AWS::GameLift::Fleet.EC2InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-ec2instancetype
        Stability:
            experimental
        """
        return jsii.get(self, "ec2InstanceType")

    @ec2_instance_type.setter
    def ec2_instance_type(self, value: str):
        return jsii.set(self, "ec2InstanceType", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::GameLift::Fleet.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="serverLaunchPath")
    def server_launch_path(self) -> str:
        """``AWS::GameLift::Fleet.ServerLaunchPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-serverlaunchpath
        Stability:
            experimental
        """
        return jsii.get(self, "serverLaunchPath")

    @server_launch_path.setter
    def server_launch_path(self, value: str):
        return jsii.set(self, "serverLaunchPath", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::GameLift::Fleet.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="ec2InboundPermissions")
    def ec2_inbound_permissions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "IpPermissionProperty"]]]]]:
        """``AWS::GameLift::Fleet.EC2InboundPermissions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-ec2inboundpermissions
        Stability:
            experimental
        """
        return jsii.get(self, "ec2InboundPermissions")

    @ec2_inbound_permissions.setter
    def ec2_inbound_permissions(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "IpPermissionProperty"]]]]]):
        return jsii.set(self, "ec2InboundPermissions", value)

    @property
    @jsii.member(jsii_name="logPaths")
    def log_paths(self) -> typing.Optional[typing.List[str]]:
        """``AWS::GameLift::Fleet.LogPaths``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-logpaths
        Stability:
            experimental
        """
        return jsii.get(self, "logPaths")

    @log_paths.setter
    def log_paths(self, value: typing.Optional[typing.List[str]]):
        return jsii.set(self, "logPaths", value)

    @property
    @jsii.member(jsii_name="maxSize")
    def max_size(self) -> typing.Optional[jsii.Number]:
        """``AWS::GameLift::Fleet.MaxSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-maxsize
        Stability:
            experimental
        """
        return jsii.get(self, "maxSize")

    @max_size.setter
    def max_size(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "maxSize", value)

    @property
    @jsii.member(jsii_name="minSize")
    def min_size(self) -> typing.Optional[jsii.Number]:
        """``AWS::GameLift::Fleet.MinSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-minsize
        Stability:
            experimental
        """
        return jsii.get(self, "minSize")

    @min_size.setter
    def min_size(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "minSize", value)

    @property
    @jsii.member(jsii_name="serverLaunchParameters")
    def server_launch_parameters(self) -> typing.Optional[str]:
        """``AWS::GameLift::Fleet.ServerLaunchParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-serverlaunchparameters
        Stability:
            experimental
        """
        return jsii.get(self, "serverLaunchParameters")

    @server_launch_parameters.setter
    def server_launch_parameters(self, value: typing.Optional[str]):
        return jsii.set(self, "serverLaunchParameters", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-gamelift.CfnFleet.IpPermissionProperty", jsii_struct_bases=[])
    class IpPermissionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-fleet-ec2inboundpermission.html
        Stability:
            experimental
        """
        fromPort: jsii.Number
        """``CfnFleet.IpPermissionProperty.FromPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-fleet-ec2inboundpermission.html#cfn-gamelift-fleet-ec2inboundpermissions-fromport
        Stability:
            experimental
        """

        ipRange: str
        """``CfnFleet.IpPermissionProperty.IpRange``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-fleet-ec2inboundpermission.html#cfn-gamelift-fleet-ec2inboundpermissions-iprange
        Stability:
            experimental
        """

        protocol: str
        """``CfnFleet.IpPermissionProperty.Protocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-fleet-ec2inboundpermission.html#cfn-gamelift-fleet-ec2inboundpermissions-protocol
        Stability:
            experimental
        """

        toPort: jsii.Number
        """``CfnFleet.IpPermissionProperty.ToPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-gamelift-fleet-ec2inboundpermission.html#cfn-gamelift-fleet-ec2inboundpermissions-toport
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnFleetProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::GameLift::Fleet.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-description
    Stability:
        experimental
    """
    ec2InboundPermissions: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnFleet.IpPermissionProperty"]]]
    """``AWS::GameLift::Fleet.EC2InboundPermissions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-ec2inboundpermissions
    Stability:
        experimental
    """
    logPaths: typing.List[str]
    """``AWS::GameLift::Fleet.LogPaths``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-logpaths
    Stability:
        experimental
    """
    maxSize: jsii.Number
    """``AWS::GameLift::Fleet.MaxSize``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-maxsize
    Stability:
        experimental
    """
    minSize: jsii.Number
    """``AWS::GameLift::Fleet.MinSize``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-minsize
    Stability:
        experimental
    """
    serverLaunchParameters: str
    """``AWS::GameLift::Fleet.ServerLaunchParameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-serverlaunchparameters
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-gamelift.CfnFleetProps", jsii_struct_bases=[_CfnFleetProps])
class CfnFleetProps(_CfnFleetProps):
    """Properties for defining a ``AWS::GameLift::Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html
    Stability:
        experimental
    """
    buildId: str
    """``AWS::GameLift::Fleet.BuildId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-buildid
    Stability:
        experimental
    """

    desiredEc2Instances: jsii.Number
    """``AWS::GameLift::Fleet.DesiredEC2Instances``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-desiredec2instances
    Stability:
        experimental
    """

    ec2InstanceType: str
    """``AWS::GameLift::Fleet.EC2InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-ec2instancetype
    Stability:
        experimental
    """

    name: str
    """``AWS::GameLift::Fleet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-name
    Stability:
        experimental
    """

    serverLaunchPath: str
    """``AWS::GameLift::Fleet.ServerLaunchPath``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-gamelift-fleet.html#cfn-gamelift-fleet-serverlaunchpath
    Stability:
        experimental
    """

__all__ = ["CfnAlias", "CfnAliasProps", "CfnBuild", "CfnBuildProps", "CfnFleet", "CfnFleetProps", "__jsii_assembly__"]

publication.publish()
