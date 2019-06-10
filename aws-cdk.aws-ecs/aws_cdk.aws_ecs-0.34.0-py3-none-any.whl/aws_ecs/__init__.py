import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.assets_docker
import aws_cdk.aws_applicationautoscaling
import aws_cdk.aws_autoscaling
import aws_cdk.aws_autoscaling_hooktargets
import aws_cdk.aws_certificatemanager
import aws_cdk.aws_cloudformation
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_ec2
import aws_cdk.aws_ecr
import aws_cdk.aws_elasticloadbalancing
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_logs
import aws_cdk.aws_route53
import aws_cdk.aws_route53_targets
import aws_cdk.aws_secretsmanager
import aws_cdk.aws_servicediscovery
import aws_cdk.aws_sns
import aws_cdk.aws_sqs
import aws_cdk.cdk
import aws_cdk.cx_api
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-ecs", "0.34.0", __name__, "aws-ecs@0.34.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.AddAutoScalingGroupCapacityOptions", jsii_struct_bases=[])
class AddAutoScalingGroupCapacityOptions(jsii.compat.TypedDict, total=False):
    """Properties for adding an autoScalingGroup.

    Stability:
        experimental
    """
    containersAccessInstanceRole: bool
    """Whether or not the containers can access the instance role.

    Default:
        false

    Stability:
        experimental
    """

    taskDrainTimeSeconds: jsii.Number
    """Give tasks this many seconds to complete when instances are being scaled in.

    Task draining adds a Lambda and a Lifecycle hook to your AutoScalingGroup
    that will delay instance termination until all ECS tasks have drained from
    the instance.

    Set to 0 to disable task draining.

    Default:
        300

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[AddAutoScalingGroupCapacityOptions, aws_cdk.aws_autoscaling.CommonAutoScalingGroupProps])
class _AddCapacityOptions(AddAutoScalingGroupCapacityOptions, aws_cdk.aws_autoscaling.CommonAutoScalingGroupProps, jsii.compat.TypedDict, total=False):
    machineImage: aws_cdk.aws_ec2.IMachineImageSource
    """The machine image for the ECS instances.

    Default:
        - Amazon Linux 1

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.AddCapacityOptions", jsii_struct_bases=[_AddCapacityOptions])
class AddCapacityOptions(_AddCapacityOptions):
    """Properties for adding autoScalingGroup.

    Stability:
        experimental
    """
    instanceType: aws_cdk.aws_ec2.InstanceType
    """The type of EC2 instance to launch into your Autoscaling Group.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ecs.AmiHardwareType")
class AmiHardwareType(enum.Enum):
    """The type of HW for the ECS Optimized AMI.

    Stability:
        experimental
    """
    Standard = "Standard"
    """Create a standard AMI.

    Stability:
        experimental
    """
    Gpu = "Gpu"
    """Create a GPU optimized AMI.

    Stability:
        experimental
    """
    Arm = "Arm"
    """Create a ARM64 optimized AMI.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _AssetImageProps(jsii.compat.TypedDict, total=False):
    buildArgs: typing.Mapping[str,str]
    """Build args to pass to the ``docker build`` command.

    Default:
        no build args are passed

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.AssetImageProps", jsii_struct_bases=[_AssetImageProps])
class AssetImageProps(_AssetImageProps):
    """
    Stability:
        experimental
    """
    directory: str
    """The directory where the Dockerfile is stored.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _AwsLogDriverProps(jsii.compat.TypedDict, total=False):
    datetimeFormat: str
    """This option defines a multiline start pattern in Python strftime format.

    A log message consists of a line that matches the pattern and any
    following lines that don’t match the pattern. Thus the matched line is
    the delimiter between log messages.

    Default:
        - No multiline matching.

    Stability:
        experimental
    """
    logGroup: aws_cdk.aws_logs.ILogGroup
    """The log group to log to.

    Default:
        - A log group is automatically created.

    Stability:
        experimental
    """
    logRetentionDays: aws_cdk.aws_logs.RetentionDays
    """The number of days log events are kept in CloudWatch Logs when the log group is automatically created by this construct.

    Default:
        - Logs never expire.

    Stability:
        experimental
    """
    multilinePattern: str
    """This option defines a multiline start pattern using a regular expression.

    A log message consists of a line that matches the pattern and any
    following lines that don’t match the pattern. Thus the matched line is
    the delimiter between log messages.

    This option is ignored if datetimeFormat is also configured.

    Default:
        - No multiline matching.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.AwsLogDriverProps", jsii_struct_bases=[_AwsLogDriverProps])
class AwsLogDriverProps(_AwsLogDriverProps):
    """Properties for defining a new AWS Log Driver.

    Stability:
        experimental
    """
    streamPrefix: str
    """Prefix for the log streams.

    The awslogs-stream-prefix option allows you to associate a log stream
    with the specified prefix, the container name, and the ID of the Amazon
    ECS task to which the container belongs. If you specify a prefix with
    this option, then the log stream takes the following format::

        prefix-name/container-name/ecs-task-id

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _BaseServiceProps(jsii.compat.TypedDict, total=False):
    desiredCount: jsii.Number
    """Number of desired copies of running tasks.

    Default:
        1

    Stability:
        experimental
    """
    healthCheckGracePeriodSeconds: jsii.Number
    """Time after startup to ignore unhealthy load balancer checks.

    Default:
        ??? FIXME

    Stability:
        experimental
    """
    longArnEnabled: bool
    """Whether the new long ARN format has been enabled on ECS services. NOTE: This assumes customer has opted into the new format for the IAM role used for the service, and is a workaround for a current bug in Cloudformation in which the service name is not correctly returned when long ARN is enabled.

    Old ARN format: arn:aws:ecs:region:aws_account_id:service/service-name
    New ARN format: arn:aws:ecs:region:aws_account_id:service/cluster-name/service-name

    See: https://docs.aws.amazon.com/AmazonECS/latest/userguide/ecs-resource-ids.html

    Default:
        false

    Stability:
        experimental
    """
    maximumPercent: jsii.Number
    """The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment.

    Default:
        - 100 if daemon, otherwise 200

    Stability:
        experimental
    """
    minimumHealthyPercent: jsii.Number
    """The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment.

    Default:
        - 0 if daemon, otherwise 50

    Stability:
        experimental
    """
    serviceDiscoveryOptions: "ServiceDiscoveryOptions"
    """Options for enabling AWS Cloud Map service discovery for the service.

    Default:
        - AWS Cloud Map service discovery is not enabled.

    Stability:
        experimental
    """
    serviceName: str
    """A name for the service.

    Default:
        - CloudFormation-generated name.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.BaseServiceProps", jsii_struct_bases=[_BaseServiceProps])
class BaseServiceProps(_BaseServiceProps):
    """Basic service properties.

    Stability:
        experimental
    """
    cluster: "ICluster"
    """Cluster where service will be deployed.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ecs.BinPackResource")
class BinPackResource(enum.Enum):
    """Instance resource used for bin packing.

    Stability:
        experimental
    """
    Cpu = "Cpu"
    """Fill up hosts' CPU allocations first.

    Stability:
        experimental
    """
    Memory = "Memory"
    """Fill up hosts' memory allocations first.

    Stability:
        experimental
    """

class BuiltInAttributes(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.BuiltInAttributes"):
    """Built-in container instance attributes.

    Stability:
        experimental
    """
    def __init__(self) -> None:
        jsii.create(BuiltInAttributes, self, [])

    @classproperty
    @jsii.member(jsii_name="AmiId")
    def AMI_ID(cls) -> str:
        """The AMI ID of the instance.

        Stability:
            experimental
        """
        return jsii.sget(cls, "AmiId")

    @classproperty
    @jsii.member(jsii_name="AvailabilityZone")
    def AVAILABILITY_ZONE(cls) -> str:
        """The AZ where the instance is running.

        Stability:
            experimental
        """
        return jsii.sget(cls, "AvailabilityZone")

    @classproperty
    @jsii.member(jsii_name="InstanceId")
    def INSTANCE_ID(cls) -> str:
        """The Instance ID of the instance.

        Stability:
            experimental
        """
        return jsii.sget(cls, "InstanceId")

    @classproperty
    @jsii.member(jsii_name="InstanceType")
    def INSTANCE_TYPE(cls) -> str:
        """The instance type.

        Stability:
            experimental
        """
        return jsii.sget(cls, "InstanceType")

    @classproperty
    @jsii.member(jsii_name="OsType")
    def OS_TYPE(cls) -> str:
        """The OS type.

        Either 'linux' or 'windows'.

        Stability:
            experimental
        """
        return jsii.sget(cls, "OsType")


@jsii.enum(jsii_type="@aws-cdk/aws-ecs.Capability")
class Capability(enum.Enum):
    """A Linux capability.

    Stability:
        experimental
    """
    All = "All"
    """
    Stability:
        experimental
    """
    AuditControl = "AuditControl"
    """
    Stability:
        experimental
    """
    AuditWrite = "AuditWrite"
    """
    Stability:
        experimental
    """
    BlockSuspend = "BlockSuspend"
    """
    Stability:
        experimental
    """
    Chown = "Chown"
    """
    Stability:
        experimental
    """
    DacOverride = "DacOverride"
    """
    Stability:
        experimental
    """
    DacReadSearch = "DacReadSearch"
    """
    Stability:
        experimental
    """
    Fowner = "Fowner"
    """
    Stability:
        experimental
    """
    Fsetid = "Fsetid"
    """
    Stability:
        experimental
    """
    IpcLock = "IpcLock"
    """
    Stability:
        experimental
    """
    IpcOwner = "IpcOwner"
    """
    Stability:
        experimental
    """
    Kill = "Kill"
    """
    Stability:
        experimental
    """
    Lease = "Lease"
    """
    Stability:
        experimental
    """
    LinuxImmutable = "LinuxImmutable"
    """
    Stability:
        experimental
    """
    MacAdmin = "MacAdmin"
    """
    Stability:
        experimental
    """
    MacOverride = "MacOverride"
    """
    Stability:
        experimental
    """
    Mknod = "Mknod"
    """
    Stability:
        experimental
    """
    NetAdmin = "NetAdmin"
    """
    Stability:
        experimental
    """
    NetBindService = "NetBindService"
    """
    Stability:
        experimental
    """
    NetBroadcast = "NetBroadcast"
    """
    Stability:
        experimental
    """
    NetRaw = "NetRaw"
    """
    Stability:
        experimental
    """
    Setfcap = "Setfcap"
    """
    Stability:
        experimental
    """
    Setgid = "Setgid"
    """
    Stability:
        experimental
    """
    Setpcap = "Setpcap"
    """
    Stability:
        experimental
    """
    Setuid = "Setuid"
    """
    Stability:
        experimental
    """
    SysAdmin = "SysAdmin"
    """
    Stability:
        experimental
    """
    SysBoot = "SysBoot"
    """
    Stability:
        experimental
    """
    SysChroot = "SysChroot"
    """
    Stability:
        experimental
    """
    SysModule = "SysModule"
    """
    Stability:
        experimental
    """
    SysNice = "SysNice"
    """
    Stability:
        experimental
    """
    SysPacct = "SysPacct"
    """
    Stability:
        experimental
    """
    SysPtrace = "SysPtrace"
    """
    Stability:
        experimental
    """
    SysRawio = "SysRawio"
    """
    Stability:
        experimental
    """
    SysResource = "SysResource"
    """
    Stability:
        experimental
    """
    SysTime = "SysTime"
    """
    Stability:
        experimental
    """
    SysTtyConfig = "SysTtyConfig"
    """
    Stability:
        experimental
    """
    Syslog = "Syslog"
    """
    Stability:
        experimental
    """
    WakeAlarm = "WakeAlarm"
    """
    Stability:
        experimental
    """

class CfnCluster(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.CfnCluster"):
    """A CloudFormation ``AWS::ECS::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-cluster.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ECS::Cluster
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cluster_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ECS::Cluster``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            clusterName: ``AWS::ECS::Cluster.ClusterName``.

        Stability:
            experimental
        """
        props: CfnClusterProps = {}

        if cluster_name is not None:
            props["clusterName"] = cluster_name

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
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "clusterArn")

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


@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnClusterProps", jsii_struct_bases=[])
class CfnClusterProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::ECS::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-cluster.html
    Stability:
        experimental
    """
    clusterName: str
    """``AWS::ECS::Cluster.ClusterName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-cluster.html#cfn-ecs-cluster-clustername
    Stability:
        experimental
    """

class CfnService(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.CfnService"):
    """A CloudFormation ``AWS::ECS::Service``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ECS::Service
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, task_definition: str, cluster: typing.Optional[str]=None, deployment_configuration: typing.Optional[typing.Union[typing.Optional["DeploymentConfigurationProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None, desired_count: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, health_check_grace_period_seconds: typing.Optional[typing.Union[typing.Optional[jsii.Number], typing.Optional[aws_cdk.cdk.Token]]]=None, launch_type: typing.Optional[str]=None, load_balancers: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union["LoadBalancerProperty", aws_cdk.cdk.Token]]]]]=None, network_configuration: typing.Optional[typing.Union[typing.Optional["NetworkConfigurationProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None, placement_constraints: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union["PlacementConstraintProperty", aws_cdk.cdk.Token]]]]]=None, placement_strategies: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union["PlacementStrategyProperty", aws_cdk.cdk.Token]]]]]=None, platform_version: typing.Optional[str]=None, role: typing.Optional[str]=None, scheduling_strategy: typing.Optional[str]=None, service_name: typing.Optional[str]=None, service_registries: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union["ServiceRegistryProperty", aws_cdk.cdk.Token]]]]]=None) -> None:
        """Create a new ``AWS::ECS::Service``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            taskDefinition: ``AWS::ECS::Service.TaskDefinition``.
            cluster: ``AWS::ECS::Service.Cluster``.
            deploymentConfiguration: ``AWS::ECS::Service.DeploymentConfiguration``.
            desiredCount: ``AWS::ECS::Service.DesiredCount``.
            healthCheckGracePeriodSeconds: ``AWS::ECS::Service.HealthCheckGracePeriodSeconds``.
            launchType: ``AWS::ECS::Service.LaunchType``.
            loadBalancers: ``AWS::ECS::Service.LoadBalancers``.
            networkConfiguration: ``AWS::ECS::Service.NetworkConfiguration``.
            placementConstraints: ``AWS::ECS::Service.PlacementConstraints``.
            placementStrategies: ``AWS::ECS::Service.PlacementStrategies``.
            platformVersion: ``AWS::ECS::Service.PlatformVersion``.
            role: ``AWS::ECS::Service.Role``.
            schedulingStrategy: ``AWS::ECS::Service.SchedulingStrategy``.
            serviceName: ``AWS::ECS::Service.ServiceName``.
            serviceRegistries: ``AWS::ECS::Service.ServiceRegistries``.

        Stability:
            experimental
        """
        props: CfnServiceProps = {"taskDefinition": task_definition}

        if cluster is not None:
            props["cluster"] = cluster

        if deployment_configuration is not None:
            props["deploymentConfiguration"] = deployment_configuration

        if desired_count is not None:
            props["desiredCount"] = desired_count

        if health_check_grace_period_seconds is not None:
            props["healthCheckGracePeriodSeconds"] = health_check_grace_period_seconds

        if launch_type is not None:
            props["launchType"] = launch_type

        if load_balancers is not None:
            props["loadBalancers"] = load_balancers

        if network_configuration is not None:
            props["networkConfiguration"] = network_configuration

        if placement_constraints is not None:
            props["placementConstraints"] = placement_constraints

        if placement_strategies is not None:
            props["placementStrategies"] = placement_strategies

        if platform_version is not None:
            props["platformVersion"] = platform_version

        if role is not None:
            props["role"] = role

        if scheduling_strategy is not None:
            props["schedulingStrategy"] = scheduling_strategy

        if service_name is not None:
            props["serviceName"] = service_name

        if service_registries is not None:
            props["serviceRegistries"] = service_registries

        jsii.create(CfnService, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnServiceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="serviceArn")
    def service_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "serviceArn")

    @property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Name
        """
        return jsii.get(self, "serviceName")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _AwsVpcConfigurationProperty(jsii.compat.TypedDict, total=False):
        assignPublicIp: str
        """``CfnService.AwsVpcConfigurationProperty.AssignPublicIp``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-awsvpcconfiguration.html#cfn-ecs-service-awsvpcconfiguration-assignpublicip
        Stability:
            experimental
        """
        securityGroups: typing.List[str]
        """``CfnService.AwsVpcConfigurationProperty.SecurityGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-awsvpcconfiguration.html#cfn-ecs-service-awsvpcconfiguration-securitygroups
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnService.AwsVpcConfigurationProperty", jsii_struct_bases=[_AwsVpcConfigurationProperty])
    class AwsVpcConfigurationProperty(_AwsVpcConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-awsvpcconfiguration.html
        Stability:
            experimental
        """
        subnets: typing.List[str]
        """``CfnService.AwsVpcConfigurationProperty.Subnets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-awsvpcconfiguration.html#cfn-ecs-service-awsvpcconfiguration-subnets
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnService.DeploymentConfigurationProperty", jsii_struct_bases=[])
    class DeploymentConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-deploymentconfiguration.html
        Stability:
            experimental
        """
        maximumPercent: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnService.DeploymentConfigurationProperty.MaximumPercent``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-deploymentconfiguration.html#cfn-ecs-service-deploymentconfiguration-maximumpercent
        Stability:
            experimental
        """

        minimumHealthyPercent: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnService.DeploymentConfigurationProperty.MinimumHealthyPercent``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-deploymentconfiguration.html#cfn-ecs-service-deploymentconfiguration-minimumhealthypercent
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LoadBalancerProperty(jsii.compat.TypedDict, total=False):
        containerName: str
        """``CfnService.LoadBalancerProperty.ContainerName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-loadbalancers.html#cfn-ecs-service-loadbalancers-containername
        Stability:
            experimental
        """
        loadBalancerName: str
        """``CfnService.LoadBalancerProperty.LoadBalancerName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-loadbalancers.html#cfn-ecs-service-loadbalancers-loadbalancername
        Stability:
            experimental
        """
        targetGroupArn: str
        """``CfnService.LoadBalancerProperty.TargetGroupArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-loadbalancers.html#cfn-ecs-service-loadbalancers-targetgrouparn
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnService.LoadBalancerProperty", jsii_struct_bases=[_LoadBalancerProperty])
    class LoadBalancerProperty(_LoadBalancerProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-loadbalancers.html
        Stability:
            experimental
        """
        containerPort: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnService.LoadBalancerProperty.ContainerPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-loadbalancers.html#cfn-ecs-service-loadbalancers-containerport
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnService.NetworkConfigurationProperty", jsii_struct_bases=[])
    class NetworkConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-networkconfiguration.html
        Stability:
            experimental
        """
        awsvpcConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnService.AwsVpcConfigurationProperty"]
        """``CfnService.NetworkConfigurationProperty.AwsvpcConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-networkconfiguration.html#cfn-ecs-service-networkconfiguration-awsvpcconfiguration
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _PlacementConstraintProperty(jsii.compat.TypedDict, total=False):
        expression: str
        """``CfnService.PlacementConstraintProperty.Expression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-placementconstraint.html#cfn-ecs-service-placementconstraint-expression
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnService.PlacementConstraintProperty", jsii_struct_bases=[_PlacementConstraintProperty])
    class PlacementConstraintProperty(_PlacementConstraintProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-placementconstraint.html
        Stability:
            experimental
        """
        type: str
        """``CfnService.PlacementConstraintProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-placementconstraint.html#cfn-ecs-service-placementconstraint-type
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _PlacementStrategyProperty(jsii.compat.TypedDict, total=False):
        field: str
        """``CfnService.PlacementStrategyProperty.Field``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-placementstrategy.html#cfn-ecs-service-placementstrategy-field
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnService.PlacementStrategyProperty", jsii_struct_bases=[_PlacementStrategyProperty])
    class PlacementStrategyProperty(_PlacementStrategyProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-placementstrategy.html
        Stability:
            experimental
        """
        type: str
        """``CfnService.PlacementStrategyProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-placementstrategy.html#cfn-ecs-service-placementstrategy-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnService.ServiceRegistryProperty", jsii_struct_bases=[])
    class ServiceRegistryProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-serviceregistry.html
        Stability:
            experimental
        """
        containerName: str
        """``CfnService.ServiceRegistryProperty.ContainerName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-serviceregistry.html#cfn-ecs-service-serviceregistry-containername
        Stability:
            experimental
        """

        containerPort: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnService.ServiceRegistryProperty.ContainerPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-serviceregistry.html#cfn-ecs-service-serviceregistry-containerport
        Stability:
            experimental
        """

        port: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnService.ServiceRegistryProperty.Port``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-serviceregistry.html#cfn-ecs-service-serviceregistry-port
        Stability:
            experimental
        """

        registryArn: str
        """``CfnService.ServiceRegistryProperty.RegistryArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-service-serviceregistry.html#cfn-ecs-service-serviceregistry-registryarn
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnServiceProps(jsii.compat.TypedDict, total=False):
    cluster: str
    """``AWS::ECS::Service.Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-cluster
    Stability:
        experimental
    """
    deploymentConfiguration: typing.Union["CfnService.DeploymentConfigurationProperty", aws_cdk.cdk.Token]
    """``AWS::ECS::Service.DeploymentConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-deploymentconfiguration
    Stability:
        experimental
    """
    desiredCount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ECS::Service.DesiredCount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-desiredcount
    Stability:
        experimental
    """
    healthCheckGracePeriodSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::ECS::Service.HealthCheckGracePeriodSeconds``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-healthcheckgraceperiodseconds
    Stability:
        experimental
    """
    launchType: str
    """``AWS::ECS::Service.LaunchType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-launchtype
    Stability:
        experimental
    """
    loadBalancers: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnService.LoadBalancerProperty", aws_cdk.cdk.Token]]]
    """``AWS::ECS::Service.LoadBalancers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-loadbalancers
    Stability:
        experimental
    """
    networkConfiguration: typing.Union["CfnService.NetworkConfigurationProperty", aws_cdk.cdk.Token]
    """``AWS::ECS::Service.NetworkConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-networkconfiguration
    Stability:
        experimental
    """
    placementConstraints: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnService.PlacementConstraintProperty", aws_cdk.cdk.Token]]]
    """``AWS::ECS::Service.PlacementConstraints``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-placementconstraints
    Stability:
        experimental
    """
    placementStrategies: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnService.PlacementStrategyProperty", aws_cdk.cdk.Token]]]
    """``AWS::ECS::Service.PlacementStrategies``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-placementstrategies
    Stability:
        experimental
    """
    platformVersion: str
    """``AWS::ECS::Service.PlatformVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-platformversion
    Stability:
        experimental
    """
    role: str
    """``AWS::ECS::Service.Role``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-role
    Stability:
        experimental
    """
    schedulingStrategy: str
    """``AWS::ECS::Service.SchedulingStrategy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-schedulingstrategy
    Stability:
        experimental
    """
    serviceName: str
    """``AWS::ECS::Service.ServiceName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-servicename
    Stability:
        experimental
    """
    serviceRegistries: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnService.ServiceRegistryProperty", aws_cdk.cdk.Token]]]
    """``AWS::ECS::Service.ServiceRegistries``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-serviceregistries
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnServiceProps", jsii_struct_bases=[_CfnServiceProps])
class CfnServiceProps(_CfnServiceProps):
    """Properties for defining a ``AWS::ECS::Service``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html
    Stability:
        experimental
    """
    taskDefinition: str
    """``AWS::ECS::Service.TaskDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-taskdefinition
    Stability:
        experimental
    """

class CfnTaskDefinition(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition"):
    """A CloudFormation ``AWS::ECS::TaskDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ECS::TaskDefinition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, container_definitions: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union["ContainerDefinitionProperty", aws_cdk.cdk.Token]]]]]=None, cpu: typing.Optional[str]=None, execution_role_arn: typing.Optional[str]=None, family: typing.Optional[str]=None, memory: typing.Optional[str]=None, network_mode: typing.Optional[str]=None, placement_constraints: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "TaskDefinitionPlacementConstraintProperty"]]]]]=None, proxy_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ProxyConfigurationProperty"]]]=None, requires_compatibilities: typing.Optional[typing.List[str]]=None, task_role_arn: typing.Optional[str]=None, volumes: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "VolumeProperty"]]]]]=None) -> None:
        """Create a new ``AWS::ECS::TaskDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            containerDefinitions: ``AWS::ECS::TaskDefinition.ContainerDefinitions``.
            cpu: ``AWS::ECS::TaskDefinition.Cpu``.
            executionRoleArn: ``AWS::ECS::TaskDefinition.ExecutionRoleArn``.
            family: ``AWS::ECS::TaskDefinition.Family``.
            memory: ``AWS::ECS::TaskDefinition.Memory``.
            networkMode: ``AWS::ECS::TaskDefinition.NetworkMode``.
            placementConstraints: ``AWS::ECS::TaskDefinition.PlacementConstraints``.
            proxyConfiguration: ``AWS::ECS::TaskDefinition.ProxyConfiguration``.
            requiresCompatibilities: ``AWS::ECS::TaskDefinition.RequiresCompatibilities``.
            taskRoleArn: ``AWS::ECS::TaskDefinition.TaskRoleArn``.
            volumes: ``AWS::ECS::TaskDefinition.Volumes``.

        Stability:
            experimental
        """
        props: CfnTaskDefinitionProps = {}

        if container_definitions is not None:
            props["containerDefinitions"] = container_definitions

        if cpu is not None:
            props["cpu"] = cpu

        if execution_role_arn is not None:
            props["executionRoleArn"] = execution_role_arn

        if family is not None:
            props["family"] = family

        if memory is not None:
            props["memory"] = memory

        if network_mode is not None:
            props["networkMode"] = network_mode

        if placement_constraints is not None:
            props["placementConstraints"] = placement_constraints

        if proxy_configuration is not None:
            props["proxyConfiguration"] = proxy_configuration

        if requires_compatibilities is not None:
            props["requiresCompatibilities"] = requires_compatibilities

        if task_role_arn is not None:
            props["taskRoleArn"] = task_role_arn

        if volumes is not None:
            props["volumes"] = volumes

        jsii.create(CfnTaskDefinition, self, [scope, id, props])

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
    def property_overrides(self) -> "CfnTaskDefinitionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @property
    @jsii.member(jsii_name="taskDefinitionArn")
    def task_definition_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "taskDefinitionArn")

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.ContainerDefinitionProperty", jsii_struct_bases=[])
    class ContainerDefinitionProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html
        Stability:
            experimental
        """
        command: typing.List[str]
        """``CfnTaskDefinition.ContainerDefinitionProperty.Command``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-command
        Stability:
            experimental
        """

        cpu: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.ContainerDefinitionProperty.Cpu``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-cpu
        Stability:
            experimental
        """

        dependsOn: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.ContainerDependencyProperty"]]]
        """``CfnTaskDefinition.ContainerDefinitionProperty.DependsOn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-dependson
        Stability:
            experimental
        """

        disableNetworking: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.ContainerDefinitionProperty.DisableNetworking``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-disablenetworking
        Stability:
            experimental
        """

        dnsSearchDomains: typing.List[str]
        """``CfnTaskDefinition.ContainerDefinitionProperty.DnsSearchDomains``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-dnssearchdomains
        Stability:
            experimental
        """

        dnsServers: typing.List[str]
        """``CfnTaskDefinition.ContainerDefinitionProperty.DnsServers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-dnsservers
        Stability:
            experimental
        """

        dockerLabels: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnTaskDefinition.ContainerDefinitionProperty.DockerLabels``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-dockerlabels
        Stability:
            experimental
        """

        dockerSecurityOptions: typing.List[str]
        """``CfnTaskDefinition.ContainerDefinitionProperty.DockerSecurityOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-dockersecurityoptions
        Stability:
            experimental
        """

        entryPoint: typing.List[str]
        """``CfnTaskDefinition.ContainerDefinitionProperty.EntryPoint``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-entrypoint
        Stability:
            experimental
        """

        environment: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.KeyValuePairProperty"]]]
        """``CfnTaskDefinition.ContainerDefinitionProperty.Environment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-environment
        Stability:
            experimental
        """

        essential: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.ContainerDefinitionProperty.Essential``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-essential
        Stability:
            experimental
        """

        extraHosts: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.HostEntryProperty"]]]
        """``CfnTaskDefinition.ContainerDefinitionProperty.ExtraHosts``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-extrahosts
        Stability:
            experimental
        """

        healthCheck: typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.HealthCheckProperty"]
        """``CfnTaskDefinition.ContainerDefinitionProperty.HealthCheck``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-healthcheck
        Stability:
            experimental
        """

        hostname: str
        """``CfnTaskDefinition.ContainerDefinitionProperty.Hostname``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-hostname
        Stability:
            experimental
        """

        image: str
        """``CfnTaskDefinition.ContainerDefinitionProperty.Image``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-image
        Stability:
            experimental
        """

        links: typing.List[str]
        """``CfnTaskDefinition.ContainerDefinitionProperty.Links``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-links
        Stability:
            experimental
        """

        linuxParameters: typing.Union["CfnTaskDefinition.LinuxParametersProperty", aws_cdk.cdk.Token]
        """``CfnTaskDefinition.ContainerDefinitionProperty.LinuxParameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-linuxparameters
        Stability:
            experimental
        """

        logConfiguration: typing.Union["CfnTaskDefinition.LogConfigurationProperty", aws_cdk.cdk.Token]
        """``CfnTaskDefinition.ContainerDefinitionProperty.LogConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-logconfiguration
        Stability:
            experimental
        """

        memory: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.ContainerDefinitionProperty.Memory``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-memory
        Stability:
            experimental
        """

        memoryReservation: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.ContainerDefinitionProperty.MemoryReservation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-memoryreservation
        Stability:
            experimental
        """

        mountPoints: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.MountPointProperty"]]]
        """``CfnTaskDefinition.ContainerDefinitionProperty.MountPoints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-mountpoints
        Stability:
            experimental
        """

        name: str
        """``CfnTaskDefinition.ContainerDefinitionProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-name
        Stability:
            experimental
        """

        portMappings: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.PortMappingProperty"]]]
        """``CfnTaskDefinition.ContainerDefinitionProperty.PortMappings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-portmappings
        Stability:
            experimental
        """

        privileged: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.ContainerDefinitionProperty.Privileged``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-privileged
        Stability:
            experimental
        """

        readonlyRootFilesystem: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.ContainerDefinitionProperty.ReadonlyRootFilesystem``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-readonlyrootfilesystem
        Stability:
            experimental
        """

        repositoryCredentials: typing.Union["CfnTaskDefinition.RepositoryCredentialsProperty", aws_cdk.cdk.Token]
        """``CfnTaskDefinition.ContainerDefinitionProperty.RepositoryCredentials``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-repositorycredentials
        Stability:
            experimental
        """

        startTimeout: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.ContainerDefinitionProperty.StartTimeout``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-starttimeout
        Stability:
            experimental
        """

        stopTimeout: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.ContainerDefinitionProperty.StopTimeout``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-stoptimeout
        Stability:
            experimental
        """

        ulimits: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.UlimitProperty"]]]
        """``CfnTaskDefinition.ContainerDefinitionProperty.Ulimits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-ulimits
        Stability:
            experimental
        """

        user: str
        """``CfnTaskDefinition.ContainerDefinitionProperty.User``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-user
        Stability:
            experimental
        """

        volumesFrom: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.VolumeFromProperty"]]]
        """``CfnTaskDefinition.ContainerDefinitionProperty.VolumesFrom``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-volumesfrom
        Stability:
            experimental
        """

        workingDirectory: str
        """``CfnTaskDefinition.ContainerDefinitionProperty.WorkingDirectory``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-workingdirectory
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.ContainerDependencyProperty", jsii_struct_bases=[])
    class ContainerDependencyProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdependency.html
        Stability:
            experimental
        """
        condition: str
        """``CfnTaskDefinition.ContainerDependencyProperty.Condition``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdependency.html#cfn-ecs-taskdefinition-containerdependency-condition
        Stability:
            experimental
        """

        containerName: str
        """``CfnTaskDefinition.ContainerDependencyProperty.ContainerName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdependency.html#cfn-ecs-taskdefinition-containerdependency-containername
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DeviceProperty(jsii.compat.TypedDict, total=False):
        containerPath: str
        """``CfnTaskDefinition.DeviceProperty.ContainerPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-device.html#cfn-ecs-taskdefinition-device-containerpath
        Stability:
            experimental
        """
        permissions: typing.List[str]
        """``CfnTaskDefinition.DeviceProperty.Permissions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-device.html#cfn-ecs-taskdefinition-device-permissions
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.DeviceProperty", jsii_struct_bases=[_DeviceProperty])
    class DeviceProperty(_DeviceProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-device.html
        Stability:
            experimental
        """
        hostPath: str
        """``CfnTaskDefinition.DeviceProperty.HostPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-device.html#cfn-ecs-taskdefinition-device-hostpath
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.DockerVolumeConfigurationProperty", jsii_struct_bases=[])
    class DockerVolumeConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-dockervolumeconfiguration.html
        Stability:
            experimental
        """
        autoprovision: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.DockerVolumeConfigurationProperty.Autoprovision``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-dockervolumeconfiguration.html#cfn-ecs-taskdefinition-dockervolumeconfiguration-autoprovision
        Stability:
            experimental
        """

        driver: str
        """``CfnTaskDefinition.DockerVolumeConfigurationProperty.Driver``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-dockervolumeconfiguration.html#cfn-ecs-taskdefinition-dockervolumeconfiguration-driver
        Stability:
            experimental
        """

        driverOpts: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnTaskDefinition.DockerVolumeConfigurationProperty.DriverOpts``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-dockervolumeconfiguration.html#cfn-ecs-taskdefinition-dockervolumeconfiguration-driveropts
        Stability:
            experimental
        """

        labels: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnTaskDefinition.DockerVolumeConfigurationProperty.Labels``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-dockervolumeconfiguration.html#cfn-ecs-taskdefinition-dockervolumeconfiguration-labels
        Stability:
            experimental
        """

        scope: str
        """``CfnTaskDefinition.DockerVolumeConfigurationProperty.Scope``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-dockervolumeconfiguration.html#cfn-ecs-taskdefinition-dockervolumeconfiguration-scope
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _HealthCheckProperty(jsii.compat.TypedDict, total=False):
        interval: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.HealthCheckProperty.Interval``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-healthcheck.html#cfn-ecs-taskdefinition-healthcheck-interval
        Stability:
            experimental
        """
        retries: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.HealthCheckProperty.Retries``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-healthcheck.html#cfn-ecs-taskdefinition-healthcheck-retries
        Stability:
            experimental
        """
        startPeriod: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.HealthCheckProperty.StartPeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-healthcheck.html#cfn-ecs-taskdefinition-healthcheck-startperiod
        Stability:
            experimental
        """
        timeout: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.HealthCheckProperty.Timeout``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-healthcheck.html#cfn-ecs-taskdefinition-healthcheck-timeout
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.HealthCheckProperty", jsii_struct_bases=[_HealthCheckProperty])
    class HealthCheckProperty(_HealthCheckProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-healthcheck.html
        Stability:
            experimental
        """
        command: typing.List[str]
        """``CfnTaskDefinition.HealthCheckProperty.Command``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-healthcheck.html#cfn-ecs-taskdefinition-healthcheck-command
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.HostEntryProperty", jsii_struct_bases=[])
    class HostEntryProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-hostentry.html
        Stability:
            experimental
        """
        hostname: str
        """``CfnTaskDefinition.HostEntryProperty.Hostname``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-hostentry.html#cfn-ecs-taskdefinition-containerdefinition-hostentry-hostname
        Stability:
            experimental
        """

        ipAddress: str
        """``CfnTaskDefinition.HostEntryProperty.IpAddress``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-hostentry.html#cfn-ecs-taskdefinition-containerdefinition-hostentry-ipaddress
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.HostVolumePropertiesProperty", jsii_struct_bases=[])
    class HostVolumePropertiesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-volumes-host.html
        Stability:
            experimental
        """
        sourcePath: str
        """``CfnTaskDefinition.HostVolumePropertiesProperty.SourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-volumes-host.html#cfn-ecs-taskdefinition-volumes-host-sourcepath
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.KernelCapabilitiesProperty", jsii_struct_bases=[])
    class KernelCapabilitiesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-kernelcapabilities.html
        Stability:
            experimental
        """
        add: typing.List[str]
        """``CfnTaskDefinition.KernelCapabilitiesProperty.Add``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-kernelcapabilities.html#cfn-ecs-taskdefinition-kernelcapabilities-add
        Stability:
            experimental
        """

        drop: typing.List[str]
        """``CfnTaskDefinition.KernelCapabilitiesProperty.Drop``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-kernelcapabilities.html#cfn-ecs-taskdefinition-kernelcapabilities-drop
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.KeyValuePairProperty", jsii_struct_bases=[])
    class KeyValuePairProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-environment.html
        Stability:
            experimental
        """
        name: str
        """``CfnTaskDefinition.KeyValuePairProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-environment.html#cfn-ecs-taskdefinition-containerdefinition-environment-name
        Stability:
            experimental
        """

        value: str
        """``CfnTaskDefinition.KeyValuePairProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-environment.html#cfn-ecs-taskdefinition-containerdefinition-environment-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.LinuxParametersProperty", jsii_struct_bases=[])
    class LinuxParametersProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-linuxparameters.html
        Stability:
            experimental
        """
        capabilities: typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.KernelCapabilitiesProperty"]
        """``CfnTaskDefinition.LinuxParametersProperty.Capabilities``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-linuxparameters.html#cfn-ecs-taskdefinition-linuxparameters-capabilities
        Stability:
            experimental
        """

        devices: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.DeviceProperty"]]]
        """``CfnTaskDefinition.LinuxParametersProperty.Devices``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-linuxparameters.html#cfn-ecs-taskdefinition-linuxparameters-devices
        Stability:
            experimental
        """

        initProcessEnabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.LinuxParametersProperty.InitProcessEnabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-linuxparameters.html#cfn-ecs-taskdefinition-linuxparameters-initprocessenabled
        Stability:
            experimental
        """

        sharedMemorySize: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.LinuxParametersProperty.SharedMemorySize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-linuxparameters.html#cfn-ecs-taskdefinition-linuxparameters-sharedmemorysize
        Stability:
            experimental
        """

        tmpfs: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.TmpfsProperty"]]]
        """``CfnTaskDefinition.LinuxParametersProperty.Tmpfs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-linuxparameters.html#cfn-ecs-taskdefinition-linuxparameters-tmpfs
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _LogConfigurationProperty(jsii.compat.TypedDict, total=False):
        options: typing.Union[aws_cdk.cdk.Token, typing.Mapping[str,str]]
        """``CfnTaskDefinition.LogConfigurationProperty.Options``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-logconfiguration.html#cfn-ecs-taskdefinition-containerdefinition-logconfiguration-options
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.LogConfigurationProperty", jsii_struct_bases=[_LogConfigurationProperty])
    class LogConfigurationProperty(_LogConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-logconfiguration.html
        Stability:
            experimental
        """
        logDriver: str
        """``CfnTaskDefinition.LogConfigurationProperty.LogDriver``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-logconfiguration.html#cfn-ecs-taskdefinition-containerdefinition-logconfiguration-logdriver
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.MountPointProperty", jsii_struct_bases=[])
    class MountPointProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-mountpoints.html
        Stability:
            experimental
        """
        containerPath: str
        """``CfnTaskDefinition.MountPointProperty.ContainerPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-mountpoints.html#cfn-ecs-taskdefinition-containerdefinition-mountpoints-containerpath
        Stability:
            experimental
        """

        readOnly: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.MountPointProperty.ReadOnly``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-mountpoints.html#cfn-ecs-taskdefinition-containerdefinition-mountpoints-readonly
        Stability:
            experimental
        """

        sourceVolume: str
        """``CfnTaskDefinition.MountPointProperty.SourceVolume``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-mountpoints.html#cfn-ecs-taskdefinition-containerdefinition-mountpoints-sourcevolume
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.PortMappingProperty", jsii_struct_bases=[])
    class PortMappingProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-portmappings.html
        Stability:
            experimental
        """
        containerPort: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.PortMappingProperty.ContainerPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-portmappings.html#cfn-ecs-taskdefinition-containerdefinition-portmappings-containerport
        Stability:
            experimental
        """

        hostPort: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.PortMappingProperty.HostPort``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-portmappings.html#cfn-ecs-taskdefinition-containerdefinition-portmappings-readonly
        Stability:
            experimental
        """

        protocol: str
        """``CfnTaskDefinition.PortMappingProperty.Protocol``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-portmappings.html#cfn-ecs-taskdefinition-containerdefinition-portmappings-sourcevolume
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ProxyConfigurationProperty(jsii.compat.TypedDict, total=False):
        proxyConfigurationProperties: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.KeyValuePairProperty"]]]
        """``CfnTaskDefinition.ProxyConfigurationProperty.ProxyConfigurationProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-proxyconfiguration.html#cfn-ecs-taskdefinition-proxyconfiguration-proxyconfigurationproperties
        Stability:
            experimental
        """
        type: str
        """``CfnTaskDefinition.ProxyConfigurationProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-proxyconfiguration.html#cfn-ecs-taskdefinition-proxyconfiguration-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.ProxyConfigurationProperty", jsii_struct_bases=[_ProxyConfigurationProperty])
    class ProxyConfigurationProperty(_ProxyConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-proxyconfiguration.html
        Stability:
            experimental
        """
        containerName: str
        """``CfnTaskDefinition.ProxyConfigurationProperty.ContainerName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-proxyconfiguration.html#cfn-ecs-taskdefinition-proxyconfiguration-containername
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.RepositoryCredentialsProperty", jsii_struct_bases=[])
    class RepositoryCredentialsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-repositorycredentials.html
        Stability:
            experimental
        """
        credentialsParameter: str
        """``CfnTaskDefinition.RepositoryCredentialsProperty.CredentialsParameter``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-repositorycredentials.html#cfn-ecs-taskdefinition-repositorycredentials-credentialsparameter
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _TaskDefinitionPlacementConstraintProperty(jsii.compat.TypedDict, total=False):
        expression: str
        """``CfnTaskDefinition.TaskDefinitionPlacementConstraintProperty.Expression``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-taskdefinitionplacementconstraint.html#cfn-ecs-taskdefinition-taskdefinitionplacementconstraint-expression
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.TaskDefinitionPlacementConstraintProperty", jsii_struct_bases=[_TaskDefinitionPlacementConstraintProperty])
    class TaskDefinitionPlacementConstraintProperty(_TaskDefinitionPlacementConstraintProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-taskdefinitionplacementconstraint.html
        Stability:
            experimental
        """
        type: str
        """``CfnTaskDefinition.TaskDefinitionPlacementConstraintProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-taskdefinitionplacementconstraint.html#cfn-ecs-taskdefinition-taskdefinitionplacementconstraint-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.TmpfsProperty", jsii_struct_bases=[])
    class TmpfsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-tmpfs.html
        Stability:
            experimental
        """
        containerPath: str
        """``CfnTaskDefinition.TmpfsProperty.ContainerPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-tmpfs.html#cfn-ecs-taskdefinition-tmpfs-containerpath
        Stability:
            experimental
        """

        mountOptions: typing.List[str]
        """``CfnTaskDefinition.TmpfsProperty.MountOptions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-tmpfs.html#cfn-ecs-taskdefinition-tmpfs-mountoptions
        Stability:
            experimental
        """

        size: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.TmpfsProperty.Size``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-tmpfs.html#cfn-ecs-taskdefinition-tmpfs-size
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.UlimitProperty", jsii_struct_bases=[])
    class UlimitProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-ulimit.html
        Stability:
            experimental
        """
        hardLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.UlimitProperty.HardLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-ulimit.html#cfn-ecs-taskdefinition-containerdefinition-ulimit-hardlimit
        Stability:
            experimental
        """

        name: str
        """``CfnTaskDefinition.UlimitProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-ulimit.html#cfn-ecs-taskdefinition-containerdefinition-ulimit-name
        Stability:
            experimental
        """

        softLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.UlimitProperty.SoftLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-ulimit.html#cfn-ecs-taskdefinition-containerdefinition-ulimit-softlimit
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.VolumeFromProperty", jsii_struct_bases=[])
    class VolumeFromProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-volumesfrom.html
        Stability:
            experimental
        """
        readOnly: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnTaskDefinition.VolumeFromProperty.ReadOnly``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-volumesfrom.html#cfn-ecs-taskdefinition-containerdefinition-volumesfrom-readonly
        Stability:
            experimental
        """

        sourceContainer: str
        """``CfnTaskDefinition.VolumeFromProperty.SourceContainer``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions-volumesfrom.html#cfn-ecs-taskdefinition-containerdefinition-volumesfrom-sourcecontainer
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinition.VolumeProperty", jsii_struct_bases=[])
    class VolumeProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-volumes.html
        Stability:
            experimental
        """
        dockerVolumeConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.DockerVolumeConfigurationProperty"]
        """``CfnTaskDefinition.VolumeProperty.DockerVolumeConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-volumes.html#cfn-ecs-taskdefinition-volume-dockervolumeconfiguration
        Stability:
            experimental
        """

        host: typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.HostVolumePropertiesProperty"]
        """``CfnTaskDefinition.VolumeProperty.Host``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-volumes.html#cfn-ecs-taskdefinition-volumes-host
        Stability:
            experimental
        """

        name: str
        """``CfnTaskDefinition.VolumeProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-volumes.html#cfn-ecs-taskdefinition-volumes-name
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CfnTaskDefinitionProps", jsii_struct_bases=[])
class CfnTaskDefinitionProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::ECS::TaskDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html
    Stability:
        experimental
    """
    containerDefinitions: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union["CfnTaskDefinition.ContainerDefinitionProperty", aws_cdk.cdk.Token]]]
    """``AWS::ECS::TaskDefinition.ContainerDefinitions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-containerdefinitions
    Stability:
        experimental
    """

    cpu: str
    """``AWS::ECS::TaskDefinition.Cpu``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-cpu
    Stability:
        experimental
    """

    executionRoleArn: str
    """``AWS::ECS::TaskDefinition.ExecutionRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-executionrolearn
    Stability:
        experimental
    """

    family: str
    """``AWS::ECS::TaskDefinition.Family``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-family
    Stability:
        experimental
    """

    memory: str
    """``AWS::ECS::TaskDefinition.Memory``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-memory
    Stability:
        experimental
    """

    networkMode: str
    """``AWS::ECS::TaskDefinition.NetworkMode``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-networkmode
    Stability:
        experimental
    """

    placementConstraints: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.TaskDefinitionPlacementConstraintProperty"]]]
    """``AWS::ECS::TaskDefinition.PlacementConstraints``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-placementconstraints
    Stability:
        experimental
    """

    proxyConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.ProxyConfigurationProperty"]
    """``AWS::ECS::TaskDefinition.ProxyConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-proxyconfiguration
    Stability:
        experimental
    """

    requiresCompatibilities: typing.List[str]
    """``AWS::ECS::TaskDefinition.RequiresCompatibilities``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-requirescompatibilities
    Stability:
        experimental
    """

    taskRoleArn: str
    """``AWS::ECS::TaskDefinition.TaskRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-taskrolearn
    Stability:
        experimental
    """

    volumes: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnTaskDefinition.VolumeProperty"]]]
    """``AWS::ECS::TaskDefinition.Volumes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-taskdefinition.html#cfn-ecs-taskdefinition-volumes
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _ClusterAttributes(jsii.compat.TypedDict, total=False):
    clusterArn: str
    """ARN of the cluster.

    Default:
        Derived from clusterName

    Stability:
        experimental
    """
    defaultNamespace: aws_cdk.aws_servicediscovery.INamespace
    """Default namespace properties.

    Default:
        - No default namespace

    Stability:
        experimental
    """
    hasEc2Capacity: bool
    """Whether the given cluster has EC2 capacity.

    Default:
        true

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.ClusterAttributes", jsii_struct_bases=[_ClusterAttributes])
class ClusterAttributes(_ClusterAttributes):
    """Properties to import an ECS cluster.

    Stability:
        experimental
    """
    clusterName: str
    """Name of the cluster.

    Stability:
        experimental
    """

    securityGroups: typing.List[aws_cdk.aws_ec2.ISecurityGroup]
    """Security group of the cluster instances.

    Stability:
        experimental
    """

    vpc: aws_cdk.aws_ec2.IVpc
    """VPC that the cluster instances are running in.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _ClusterProps(jsii.compat.TypedDict, total=False):
    clusterName: str
    """A name for the cluster.

    Default:
        CloudFormation-generated name

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.ClusterProps", jsii_struct_bases=[_ClusterProps])
class ClusterProps(_ClusterProps):
    """Properties to define an ECS cluster.

    Stability:
        experimental
    """
    vpc: aws_cdk.aws_ec2.IVpc
    """The VPC where your ECS instances will be running or your ENIs will be deployed.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CommonTaskDefinitionProps", jsii_struct_bases=[])
class CommonTaskDefinitionProps(jsii.compat.TypedDict, total=False):
    """Properties common to all Task definitions.

    Stability:
        experimental
    """
    executionRole: aws_cdk.aws_iam.IRole
    """The IAM role assumed by the ECS agent.

    The role will be used to retrieve container images from ECR and
    create CloudWatch log groups.

    Default:
        - An execution role will be automatically created if you use ECR images in your task definition.

    Stability:
        experimental
    """

    family: str
    """Namespace for task definition versions.

    Default:
        - Automatically generated name.

    Stability:
        experimental
    """

    taskRole: aws_cdk.aws_iam.IRole
    """The IAM role assumable by your application code running inside the container.

    Default:
        - A task role is automatically created for you.

    Stability:
        experimental
    """

    volumes: typing.List["Volume"]
    """See: https://docs.aws.amazon.com/AmazonECS/latest/developerguide//task_definition_parameters.html#volumes.

    Default:
        - No volumes are passed to the Docker daemon on a container instance.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ecs.Compatibility")
class Compatibility(enum.Enum):
    """Task compatibility.

    Stability:
        experimental
    """
    Ec2 = "Ec2"
    """Task should be launchable on EC2 clusters.

    Stability:
        experimental
    """
    Fargate = "Fargate"
    """Task should be launchable on Fargate clusters.

    Stability:
        experimental
    """
    Ec2AndFargate = "Ec2AndFargate"
    """Task should be launchable on both types of clusters.

    Stability:
        experimental
    """

class ContainerDefinition(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.ContainerDefinition"):
    """A definition for a single container in a Task.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, task_definition: "TaskDefinition", image: "ContainerImage", command: typing.Optional[typing.List[str]]=None, cpu: typing.Optional[jsii.Number]=None, disable_networking: typing.Optional[bool]=None, dns_search_domains: typing.Optional[typing.List[str]]=None, dns_servers: typing.Optional[typing.List[str]]=None, docker_labels: typing.Optional[typing.Mapping[str,str]]=None, docker_security_options: typing.Optional[typing.List[str]]=None, entry_point: typing.Optional[typing.List[str]]=None, environment: typing.Optional[typing.Mapping[str,str]]=None, essential: typing.Optional[bool]=None, extra_hosts: typing.Optional[typing.Mapping[str,str]]=None, health_check: typing.Optional["HealthCheck"]=None, hostname: typing.Optional[str]=None, linux_parameters: typing.Optional["LinuxParameters"]=None, logging: typing.Optional["LogDriver"]=None, memory_limit_mi_b: typing.Optional[jsii.Number]=None, memory_reservation_mi_b: typing.Optional[jsii.Number]=None, privileged: typing.Optional[bool]=None, readonly_root_filesystem: typing.Optional[bool]=None, user: typing.Optional[str]=None, working_directory: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            taskDefinition: The task this container definition belongs to. [disable-awslint:ref-via-interface]
            image: The image to use for a container. You can use images in the Docker Hub registry or specify other repositories (repository-url/image:tag). TODO: Update these to specify using classes of IContainerImage
            command: The CMD value to pass to the container. If you provide a shell command as a single string, you have to quote command-line arguments. Default: - CMD value built into container image.
            cpu: The minimum number of CPU units to reserve for the container. Default: - No minimum CPU units reserved.
            disableNetworking: Indicates whether networking is disabled within the container. Default: false
            dnsSearchDomains: A list of DNS search domains that are provided to the container. Default: - No search domains.
            dnsServers: A list of DNS servers that Amazon ECS provides to the container. Default: - Default DNS servers.
            dockerLabels: A key-value map of labels for the container. Default: - No labels.
            dockerSecurityOptions: A list of custom labels for SELinux and AppArmor multi-level security systems. Default: - No security labels.
            entryPoint: The ENTRYPOINT value to pass to the container. Default: - Entry point configured in container.
            environment: The environment variables to pass to the container. Default: - No environment variables.
            essential: Indicates whether the task stops if this container fails. If you specify true and the container fails, all other containers in the task stop. If you specify false and the container fails, none of the other containers in the task is affected. You must have at least one essential container in a task. Default: true
            extraHosts: A list of hostnames and IP address mappings to append to the /etc/hosts file on the container. Default: - No extra hosts.
            healthCheck: Container health check. Default: - Health check configuration from container.
            hostname: The name that Docker uses for the container hostname. Default: - Automatic hostname.
            linuxParameters: Configures Linux Parameters. Default: - No Linux paramters.
            logging: Configures a custom log driver for the container. Default: - Containers use the same logging driver that the Docker daemon uses.
            memoryLimitMiB: The hard limit (in MiB) of memory to present to the container. If your container attempts to exceed the allocated memory, the container is terminated. At least one of memoryLimitMiB and memoryReservationMiB is required for non-Fargate services. Default: - No memory limit.
            memoryReservationMiB: The soft limit (in MiB) of memory to reserve for the container. When system memory is under contention, Docker attempts to keep the container memory within the limit. If the container requires more memory, it can consume up to the value specified by the Memory property or all of the available memory on the container instance—whichever comes first. At least one of memoryLimitMiB and memoryReservationMiB is required for non-Fargate services. Default: - No memory reserved.
            privileged: Indicates whether the container is given full access to the host container instance. Default: false
            readonlyRootFilesystem: Indicates whether the container's root file system is mounted as read only. Default: false
            user: The user name to use inside the container. Default: root
            workingDirectory: The working directory in the container to run commands in. Default: /

        Stability:
            experimental
        """
        props: ContainerDefinitionProps = {"taskDefinition": task_definition, "image": image}

        if command is not None:
            props["command"] = command

        if cpu is not None:
            props["cpu"] = cpu

        if disable_networking is not None:
            props["disableNetworking"] = disable_networking

        if dns_search_domains is not None:
            props["dnsSearchDomains"] = dns_search_domains

        if dns_servers is not None:
            props["dnsServers"] = dns_servers

        if docker_labels is not None:
            props["dockerLabels"] = docker_labels

        if docker_security_options is not None:
            props["dockerSecurityOptions"] = docker_security_options

        if entry_point is not None:
            props["entryPoint"] = entry_point

        if environment is not None:
            props["environment"] = environment

        if essential is not None:
            props["essential"] = essential

        if extra_hosts is not None:
            props["extraHosts"] = extra_hosts

        if health_check is not None:
            props["healthCheck"] = health_check

        if hostname is not None:
            props["hostname"] = hostname

        if linux_parameters is not None:
            props["linuxParameters"] = linux_parameters

        if logging is not None:
            props["logging"] = logging

        if memory_limit_mi_b is not None:
            props["memoryLimitMiB"] = memory_limit_mi_b

        if memory_reservation_mi_b is not None:
            props["memoryReservationMiB"] = memory_reservation_mi_b

        if privileged is not None:
            props["privileged"] = privileged

        if readonly_root_filesystem is not None:
            props["readonlyRootFilesystem"] = readonly_root_filesystem

        if user is not None:
            props["user"] = user

        if working_directory is not None:
            props["workingDirectory"] = working_directory

        jsii.create(ContainerDefinition, self, [scope, id, props])

    @jsii.member(jsii_name="addLink")
    def add_link(self, container: "ContainerDefinition", alias: typing.Optional[str]=None) -> None:
        """Add a link from this container to a different container The link parameter allows containers to communicate with each other without the need for port mappings. Only supported if the network mode of a task definition is set to bridge. Warning: The --link flag is a legacy feature of Docker. It may eventually be removed.

        Arguments:
            container: -
            alias: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addLink", [container, alias])

    @jsii.member(jsii_name="addMountPoints")
    def add_mount_points(self, *, container_path: str, read_only: bool, source_volume: str) -> None:
        """Add one or more mount points to this container.

        Arguments:
            mountPoints: -
            containerPath: 
            readOnly: 
            sourceVolume: 

        Stability:
            experimental
        """
        mount_points: MountPoint = {"containerPath": container_path, "readOnly": read_only, "sourceVolume": source_volume}

        return jsii.invoke(self, "addMountPoints", [*mount_points])

    @jsii.member(jsii_name="addPortMappings")
    def add_port_mappings(self, *, container_port: jsii.Number, host_port: typing.Optional[jsii.Number]=None, protocol: typing.Optional["Protocol"]=None) -> None:
        """Add one or more port mappings to this container.

        Arguments:
            portMappings: -
            containerPort: Port inside the container.
            hostPort: Port on the host. In AwsVpc or Host networking mode, leave this out or set it to the same value as containerPort. In Bridge networking mode, leave this out or set it to non-reserved non-ephemeral port.
            protocol: Protocol. Default: Tcp

        Stability:
            experimental
        """
        port_mappings: PortMapping = {"containerPort": container_port}

        if host_port is not None:
            port_mappings["hostPort"] = host_port

        if protocol is not None:
            port_mappings["protocol"] = protocol

        return jsii.invoke(self, "addPortMappings", [*port_mappings])

    @jsii.member(jsii_name="addScratch")
    def add_scratch(self, *, container_path: str, name: str, read_only: bool, source_path: str) -> None:
        """Mount temporary disc space to a container. This adds the correct container mountPoint and task definition volume.

        Arguments:
            scratch: -
            containerPath: 
            name: 
            readOnly: 
            sourcePath: 

        Stability:
            experimental
        """
        scratch: ScratchSpace = {"containerPath": container_path, "name": name, "readOnly": read_only, "sourcePath": source_path}

        return jsii.invoke(self, "addScratch", [scratch])

    @jsii.member(jsii_name="addToExecutionPolicy")
    def add_to_execution_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add a statement to the Task Definition's Execution policy.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToExecutionPolicy", [statement])

    @jsii.member(jsii_name="addUlimits")
    def add_ulimits(self, *, hard_limit: jsii.Number, name: "UlimitName", soft_limit: jsii.Number) -> None:
        """Add one or more ulimits to this container.

        Arguments:
            ulimits: -
            hardLimit: Hard limit of the resource.
            name: What resource to enforce a limit on.
            softLimit: Soft limit of the resource.

        Stability:
            experimental
        """
        ulimits: Ulimit = {"hardLimit": hard_limit, "name": name, "softLimit": soft_limit}

        return jsii.invoke(self, "addUlimits", [*ulimits])

    @jsii.member(jsii_name="addVolumesFrom")
    def add_volumes_from(self, *, read_only: bool, source_container: str) -> None:
        """Add one or more volumes to this container.

        Arguments:
            volumesFrom: -
            readOnly: Whether the volume is read only.
            sourceContainer: Name of the source container.

        Stability:
            experimental
        """
        volumes_from: VolumeFrom = {"readOnly": read_only, "sourceContainer": source_container}

        return jsii.invoke(self, "addVolumesFrom", [*volumes_from])

    @jsii.member(jsii_name="renderContainerDefinition")
    def render_container_definition(self) -> "CfnTaskDefinition.ContainerDefinitionProperty":
        """Render this container definition to a CloudFormation object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderContainerDefinition", [])

    @property
    @jsii.member(jsii_name="containerPort")
    def container_port(self) -> jsii.Number:
        """Return the port that the container will be listening on by default.

        Stability:
            experimental
        """
        return jsii.get(self, "containerPort")

    @property
    @jsii.member(jsii_name="essential")
    def essential(self) -> bool:
        """Whether or not this container is essential.

        Stability:
            experimental
        """
        return jsii.get(self, "essential")

    @property
    @jsii.member(jsii_name="ingressPort")
    def ingress_port(self) -> jsii.Number:
        """Ingress Port is needed to set the security group ingress for the task/service.

        Stability:
            experimental
        """
        return jsii.get(self, "ingressPort")

    @property
    @jsii.member(jsii_name="memoryLimitSpecified")
    def memory_limit_specified(self) -> bool:
        """Whether there was at least one memory limit specified in this definition.

        Stability:
            experimental
        """
        return jsii.get(self, "memoryLimitSpecified")

    @property
    @jsii.member(jsii_name="mountPoints")
    def mount_points(self) -> typing.List["MountPoint"]:
        """The configured mount points.

        Stability:
            experimental
        """
        return jsii.get(self, "mountPoints")

    @property
    @jsii.member(jsii_name="portMappings")
    def port_mappings(self) -> typing.List["PortMapping"]:
        """The configured port mappings.

        Stability:
            experimental
        """
        return jsii.get(self, "portMappings")

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "ContainerDefinitionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")

    @property
    @jsii.member(jsii_name="taskDefinition")
    def task_definition(self) -> "TaskDefinition":
        """The task definition this container definition is part of.

        Stability:
            experimental
        """
        return jsii.get(self, "taskDefinition")

    @property
    @jsii.member(jsii_name="ulimits")
    def ulimits(self) -> typing.List["Ulimit"]:
        """The configured ulimits.

        Stability:
            experimental
        """
        return jsii.get(self, "ulimits")

    @property
    @jsii.member(jsii_name="volumesFrom")
    def volumes_from(self) -> typing.List["VolumeFrom"]:
        """The configured volumes.

        Stability:
            experimental
        """
        return jsii.get(self, "volumesFrom")

    @property
    @jsii.member(jsii_name="linuxParameters")
    def linux_parameters(self) -> typing.Optional["LinuxParameters"]:
        """Access Linux Parameters.

        Stability:
            experimental
        """
        return jsii.get(self, "linuxParameters")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ContainerDefinitionOptions(jsii.compat.TypedDict, total=False):
    command: typing.List[str]
    """The CMD value to pass to the container.

    If you provide a shell command as a single string, you have to quote command-line arguments.

    Default:
        - CMD value built into container image.

    Stability:
        experimental
    """
    cpu: jsii.Number
    """The minimum number of CPU units to reserve for the container.

    Default:
        - No minimum CPU units reserved.

    Stability:
        experimental
    """
    disableNetworking: bool
    """Indicates whether networking is disabled within the container.

    Default:
        false

    Stability:
        experimental
    """
    dnsSearchDomains: typing.List[str]
    """A list of DNS search domains that are provided to the container.

    Default:
        - No search domains.

    Stability:
        experimental
    """
    dnsServers: typing.List[str]
    """A list of DNS servers that Amazon ECS provides to the container.

    Default:
        - Default DNS servers.

    Stability:
        experimental
    """
    dockerLabels: typing.Mapping[str,str]
    """A key-value map of labels for the container.

    Default:
        - No labels.

    Stability:
        experimental
    """
    dockerSecurityOptions: typing.List[str]
    """A list of custom labels for SELinux and AppArmor multi-level security systems.

    Default:
        - No security labels.

    Stability:
        experimental
    """
    entryPoint: typing.List[str]
    """The ENTRYPOINT value to pass to the container.

    Default:
        - Entry point configured in container.

    See:
        https://docs.docker.com/engine/reference/builder/#entrypoint
    Stability:
        experimental
    """
    environment: typing.Mapping[str,str]
    """The environment variables to pass to the container.

    Default:
        - No environment variables.

    Stability:
        experimental
    """
    essential: bool
    """Indicates whether the task stops if this container fails.

    If you specify true and the container fails, all other containers in the
    task stop. If you specify false and the container fails, none of the other
    containers in the task is affected.

    You must have at least one essential container in a task.

    Default:
        true

    Stability:
        experimental
    """
    extraHosts: typing.Mapping[str,str]
    """A list of hostnames and IP address mappings to append to the /etc/hosts file on the container.

    Default:
        - No extra hosts.

    Stability:
        experimental
    """
    healthCheck: "HealthCheck"
    """Container health check.

    Default:
        - Health check configuration from container.

    Stability:
        experimental
    """
    hostname: str
    """The name that Docker uses for the container hostname.

    Default:
        - Automatic hostname.

    Stability:
        experimental
    """
    linuxParameters: "LinuxParameters"
    """Configures Linux Parameters.

    Default:
        - No Linux paramters.

    Stability:
        experimental
    """
    logging: "LogDriver"
    """Configures a custom log driver for the container.

    Default:
        - Containers use the same logging driver that the Docker daemon uses.

    Stability:
        experimental
    """
    memoryLimitMiB: jsii.Number
    """The hard limit (in MiB) of memory to present to the container.

    If your container attempts to exceed the allocated memory, the container
    is terminated.

    At least one of memoryLimitMiB and memoryReservationMiB is required for non-Fargate services.

    Default:
        - No memory limit.

    Stability:
        experimental
    """
    memoryReservationMiB: jsii.Number
    """The soft limit (in MiB) of memory to reserve for the container.

    When system memory is under contention, Docker attempts to keep the
    container memory within the limit. If the container requires more memory,
    it can consume up to the value specified by the Memory property or all of
    the available memory on the container instance—whichever comes first.

    At least one of memoryLimitMiB and memoryReservationMiB is required for non-Fargate services.

    Default:
        - No memory reserved.

    Stability:
        experimental
    """
    privileged: bool
    """Indicates whether the container is given full access to the host container instance.

    Default:
        false

    Stability:
        experimental
    """
    readonlyRootFilesystem: bool
    """Indicates whether the container's root file system is mounted as read only.

    Default:
        false

    Stability:
        experimental
    """
    user: str
    """The user name to use inside the container.

    Default:
        root

    Stability:
        experimental
    """
    workingDirectory: str
    """The working directory in the container to run commands in.

    Default:
        /

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.ContainerDefinitionOptions", jsii_struct_bases=[_ContainerDefinitionOptions])
class ContainerDefinitionOptions(_ContainerDefinitionOptions):
    """
    Stability:
        experimental
    """
    image: "ContainerImage"
    """The image to use for a container.

    You can use images in the Docker Hub registry or specify other
    repositories (repository-url/image:tag).
    TODO: Update these to specify using classes of IContainerImage

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.ContainerDefinitionProps", jsii_struct_bases=[ContainerDefinitionOptions])
class ContainerDefinitionProps(ContainerDefinitionOptions, jsii.compat.TypedDict):
    """Properties of a container definition.

    Stability:
        experimental
    """
    taskDefinition: "TaskDefinition"
    """The task this container definition belongs to.

    [disable-awslint:ref-via-interface]

    Stability:
        experimental
    """

class ContainerImage(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-ecs.ContainerImage"):
    """Constructs for types of container images.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ContainerImageProxy

    def __init__(self) -> None:
        jsii.create(ContainerImage, self, [])

    @jsii.member(jsii_name="fromAsset")
    @classmethod
    def from_asset(cls, scope: aws_cdk.cdk.Construct, id: str, *, directory: str, build_args: typing.Optional[typing.Mapping[str,str]]=None) -> "AssetImage":
        """Reference an image that's constructed directly from sources on disk.

        Arguments:
            scope: -
            id: -
            props: -
            directory: The directory where the Dockerfile is stored.
            buildArgs: Build args to pass to the ``docker build`` command. Default: no build args are passed

        Stability:
            experimental
        """
        props: AssetImageProps = {"directory": directory}

        if build_args is not None:
            props["buildArgs"] = build_args

        return jsii.sinvoke(cls, "fromAsset", [scope, id, props])

    @jsii.member(jsii_name="fromEcrRepository")
    @classmethod
    def from_ecr_repository(cls, repository: aws_cdk.aws_ecr.IRepository, tag: typing.Optional[str]=None) -> "EcrImage":
        """Reference an image in an ECR repository.

        Arguments:
            repository: -
            tag: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromEcrRepository", [repository, tag])

    @jsii.member(jsii_name="fromRegistry")
    @classmethod
    def from_registry(cls, name: str, *, credentials: typing.Optional[aws_cdk.aws_secretsmanager.ISecret]=None) -> "RepositoryImage":
        """Reference an image on DockerHub or another online registry.

        Arguments:
            name: -
            props: -
            credentials: Optional secret that houses credentials for the image registry.

        Stability:
            experimental
        """
        props: RepositoryImageProps = {}

        if credentials is not None:
            props["credentials"] = credentials

        return jsii.sinvoke(cls, "fromRegistry", [name, props])

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def bind(self, container_definition: "ContainerDefinition") -> None:
        """Called when the image is used by a ContainerDefinition.

        Arguments:
            containerDefinition: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="toRepositoryCredentialsJson")
    @abc.abstractmethod
    def to_repository_credentials_json(self) -> typing.Optional["CfnTaskDefinition.RepositoryCredentialsProperty"]:
        """Render the Repository credentials to the CloudFormation object.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="imageName")
    @abc.abstractmethod
    def image_name(self) -> str:
        """Name of the image.

        Stability:
            experimental
        """
        ...


class _ContainerImageProxy(ContainerImage):
    @jsii.member(jsii_name="bind")
    def bind(self, container_definition: "ContainerDefinition") -> None:
        """Called when the image is used by a ContainerDefinition.

        Arguments:
            containerDefinition: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [container_definition])

    @jsii.member(jsii_name="toRepositoryCredentialsJson")
    def to_repository_credentials_json(self) -> typing.Optional["CfnTaskDefinition.RepositoryCredentialsProperty"]:
        """Render the Repository credentials to the CloudFormation object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRepositoryCredentialsJson", [])

    @property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> str:
        """Name of the image.

        Stability:
            experimental
        """
        return jsii.get(self, "imageName")


class AssetImage(ContainerImage, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.AssetImage"):
    """An image that will be built at synthesis time.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, directory: str, build_args: typing.Optional[typing.Mapping[str,str]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            directory: The directory where the Dockerfile is stored.
            buildArgs: Build args to pass to the ``docker build`` command. Default: no build args are passed

        Stability:
            experimental
        """
        props: AssetImageProps = {"directory": directory}

        if build_args is not None:
            props["buildArgs"] = build_args

        jsii.create(AssetImage, self, [scope, id, props])

    @jsii.member(jsii_name="bind")
    def bind(self, container_definition: "ContainerDefinition") -> None:
        """Called when the image is used by a ContainerDefinition.

        Arguments:
            containerDefinition: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [container_definition])

    @jsii.member(jsii_name="toRepositoryCredentialsJson")
    def to_repository_credentials_json(self) -> typing.Optional["CfnTaskDefinition.RepositoryCredentialsProperty"]:
        """Render the Repository credentials to the CloudFormation object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRepositoryCredentialsJson", [])

    @property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> str:
        """Name of the image.

        Stability:
            experimental
        """
        return jsii.get(self, "imageName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.CpuUtilizationScalingProps", jsii_struct_bases=[aws_cdk.aws_applicationautoscaling.BaseTargetTrackingProps])
class CpuUtilizationScalingProps(aws_cdk.aws_applicationautoscaling.BaseTargetTrackingProps, jsii.compat.TypedDict):
    """Properties for enabling scaling based on CPU utilization.

    Stability:
        experimental
    """
    targetUtilizationPercent: jsii.Number
    """Target average CPU utilization across the task.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _Device(jsii.compat.TypedDict, total=False):
    containerPath: str
    """Path in the container.

    Default:
        Same path as the host

    Stability:
        experimental
    """
    permissions: typing.List["DevicePermission"]
    """Permissions.

    Default:
        Readonly

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.Device", jsii_struct_bases=[_Device])
class Device(_Device):
    """A host device.

    Stability:
        experimental
    """
    hostPath: str
    """Path on the host.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ecs.DevicePermission")
class DevicePermission(enum.Enum):
    """Permissions for device access.

    Stability:
        experimental
    """
    Read = "Read"
    """Read.

    Stability:
        experimental
    """
    Write = "Write"
    """Write.

    Stability:
        experimental
    """
    Mknod = "Mknod"
    """Make a node.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _DockerVolumeConfiguration(jsii.compat.TypedDict, total=False):
    autoprovision: bool
    """If true, the Docker volume is created if it does not already exist.

    Default:
        false

    Stability:
        experimental
    """
    driverOpts: typing.List[str]
    """A map of Docker driver specific options passed through.

    Default:
        No options

    Stability:
        experimental
    """
    labels: typing.List[str]
    """Custom metadata to add to your Docker volume.

    Default:
        No labels

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.DockerVolumeConfiguration", jsii_struct_bases=[_DockerVolumeConfiguration])
class DockerVolumeConfiguration(_DockerVolumeConfiguration):
    """A configuration of a Docker volume.

    Stability:
        experimental
    """
    driver: str
    """The Docker volume driver to use.

    Stability:
        experimental
    """

    scope: "Scope"
    """The scope for the Docker volume which determines it's lifecycle.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[BaseServiceProps])
class _Ec2ServiceProps(BaseServiceProps, jsii.compat.TypedDict, total=False):
    daemon: bool
    """Deploy exactly one task on each instance in your cluster.

    When using this strategy, do not specify a desired number of tasks or any
    task placement strategies.

    Default:
        false

    Stability:
        experimental
    """
    placementConstraints: typing.List["PlacementConstraint"]
    """Placement constraints.

    Default:
        - No constraints.

    Stability:
        experimental
    """
    placementStrategies: typing.List["PlacementStrategy"]
    """Placement strategies.

    Default:
        - No strategies.

    Stability:
        experimental
    """
    securityGroup: aws_cdk.aws_ec2.ISecurityGroup
    """Existing security group to use for the task's ENIs.

    (Only applicable in case the TaskDefinition is configured for AwsVpc networking)

    Default:
        - A new security group is created.

    Stability:
        experimental
    """
    vpcSubnets: aws_cdk.aws_ec2.SubnetSelection
    """In what subnets to place the task's ENIs.

    (Only applicable in case the TaskDefinition is configured for AwsVpc networking)

    Default:
        - Private subnets.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.Ec2ServiceProps", jsii_struct_bases=[_Ec2ServiceProps])
class Ec2ServiceProps(_Ec2ServiceProps):
    """Properties to define an ECS service.

    Stability:
        experimental
    """
    taskDefinition: "TaskDefinition"
    """Task Definition used for running tasks in the service.

    [disable-awslint:ref-via-interface]

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.Ec2TaskDefinitionProps", jsii_struct_bases=[CommonTaskDefinitionProps])
class Ec2TaskDefinitionProps(CommonTaskDefinitionProps, jsii.compat.TypedDict, total=False):
    """Properties to define an ECS task definition.

    Stability:
        experimental
    """
    networkMode: "NetworkMode"
    """The Docker networking mode to use for the containers in the task.

    On Fargate, the only supported networking mode is AwsVpc.

    Default:
        - NetworkMode.Bridge for EC2 tasks, AwsVpc for Fargate tasks.

    Stability:
        experimental
    """

    placementConstraints: typing.List["PlacementConstraint"]
    """An array of placement constraint objects to use for the task.

    You can
    specify a maximum of 10 constraints per task (this limit includes
    constraints in the task definition and those specified at run time).

    Not supported in Fargate.

    Default:
        - No placement constraints.

    Stability:
        experimental
    """

class EcrImage(ContainerImage, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.EcrImage"):
    """An image from an ECR repository.

    Stability:
        experimental
    """
    def __init__(self, repository: aws_cdk.aws_ecr.IRepository, tag: str) -> None:
        """
        Arguments:
            repository: -
            tag: -

        Stability:
            experimental
        """
        jsii.create(EcrImage, self, [repository, tag])

    @jsii.member(jsii_name="bind")
    def bind(self, container_definition: "ContainerDefinition") -> None:
        """Called when the image is used by a ContainerDefinition.

        Arguments:
            containerDefinition: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [container_definition])

    @jsii.member(jsii_name="toRepositoryCredentialsJson")
    def to_repository_credentials_json(self) -> typing.Optional["CfnTaskDefinition.RepositoryCredentialsProperty"]:
        """Render the Repository credentials to the CloudFormation object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRepositoryCredentialsJson", [])

    @property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> str:
        """Name of the image.

        Stability:
            experimental
        """
        return jsii.get(self, "imageName")


@jsii.implements(aws_cdk.aws_ec2.IMachineImageSource)
class EcsOptimizedAmi(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.EcsOptimizedAmi"):
    """Construct a Linux machine image from the latest ECS Optimized AMI published in SSM.

    Stability:
        experimental
    """
    def __init__(self, *, generation: typing.Optional[aws_cdk.aws_ec2.AmazonLinuxGeneration]=None, hw_type: typing.Optional["AmiHardwareType"]=None) -> None:
        """
        Arguments:
            props: -
            generation: What generation of Amazon Linux to use. Default: AmazonLinuxGeneration.AmazonLinux if hwType equal to AmiHardwareType.Standard else AmazonLinuxGeneration.AmazonLinux2
            hwType: What ECS Optimized AMI type to use. Default: AmiHardwareType.Standard

        Stability:
            experimental
        """
        props: EcsOptimizedAmiProps = {}

        if generation is not None:
            props["generation"] = generation

        if hw_type is not None:
            props["hwType"] = hw_type

        jsii.create(EcsOptimizedAmi, self, [props])

    @jsii.member(jsii_name="getImage")
    def get_image(self, scope: aws_cdk.cdk.Construct) -> aws_cdk.aws_ec2.MachineImage:
        """Return the correct image.

        Arguments:
            scope: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "getImage", [scope])


@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.EcsOptimizedAmiProps", jsii_struct_bases=[])
class EcsOptimizedAmiProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    generation: aws_cdk.aws_ec2.AmazonLinuxGeneration
    """What generation of Amazon Linux to use.

    Default:
        AmazonLinuxGeneration.AmazonLinux if hwType equal to AmiHardwareType.Standard else AmazonLinuxGeneration.AmazonLinux2

    Stability:
        experimental
    """

    hwType: "AmiHardwareType"
    """What ECS Optimized AMI type to use.

    Default:
        AmiHardwareType.Standard

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ecs.FargatePlatformVersion")
class FargatePlatformVersion(enum.Enum):
    """Fargate platform version.

    See:
        https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html
    Stability:
        experimental
    """
    Latest = "Latest"
    """The latest, recommended platform version.

    Stability:
        experimental
    """
    Version1_3 = "Version1_3"
    """Version 1.3.0.

    Supports secrets, task recycling.

    Stability:
        experimental
    """
    Version1_2 = "Version1_2"
    """Version 1.2.0.

    Supports private registries.

    Stability:
        experimental
    """
    Version1_1 = "Version1_1"
    """Version 1.1.0.

    Supports task metadata, health checks, service discovery.

    Stability:
        experimental
    """
    Version1_0 = "Version1_0"
    """Initial release.

    Based on Amazon Linux 2017.09.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[BaseServiceProps])
class _FargateServiceProps(BaseServiceProps, jsii.compat.TypedDict, total=False):
    assignPublicIp: bool
    """Assign public IP addresses to each task.

    Default:
        - Use subnet default.

    Stability:
        experimental
    """
    platformVersion: "FargatePlatformVersion"
    """Fargate platform version to run this service on.

    Unless you have specific compatibility requirements, you don't need to
    specify this.

    Default:
        Latest

    Stability:
        experimental
    """
    securityGroup: aws_cdk.aws_ec2.ISecurityGroup
    """Existing security group to use for the tasks.

    Default:
        - A new security group is created.

    Stability:
        experimental
    """
    vpcSubnets: aws_cdk.aws_ec2.SubnetSelection
    """In what subnets to place the task's ENIs.

    Default:
        - Private subnets.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.FargateServiceProps", jsii_struct_bases=[_FargateServiceProps])
class FargateServiceProps(_FargateServiceProps):
    """Properties to define a Fargate service.

    Stability:
        experimental
    """
    taskDefinition: "TaskDefinition"
    """Task Definition used for running tasks in the service.

    [disable-awslint:ref-via-interface]

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.FargateTaskDefinitionProps", jsii_struct_bases=[CommonTaskDefinitionProps])
class FargateTaskDefinitionProps(CommonTaskDefinitionProps, jsii.compat.TypedDict, total=False):
    """Properties to define a Fargate Task.

    Stability:
        experimental
    """
    cpu: str
    """The number of cpu units used by the task. Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments.

    Default:
        256

    Stability:
        experimental
    """

    memoryMiB: str
    """The amount (in MiB) of memory used by the task.

    This field is required and you must use one of the following values, which determines your range of valid values
    for the cpu parameter:

    0.5GB, 1GB, 2GB - Available cpu values: 256 (.25 vCPU)

    1GB, 2GB, 3GB, 4GB - Available cpu values: 512 (.5 vCPU)

    2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB - Available cpu values: 1024 (1 vCPU)

    Between 4GB and 16GB in 1GB increments - Available cpu values: 2048 (2 vCPU)

    Between 8GB and 30GB in 1GB increments - Available cpu values: 4096 (4 vCPU)

    Default:
        512

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _HealthCheck(jsii.compat.TypedDict, total=False):
    intervalSeconds: jsii.Number
    """Time period in seconds between each health check execution.

    You may specify between 5 and 300 seconds.

    Default:
        30

    Stability:
        experimental
    """
    retries: jsii.Number
    """Number of times to retry a failed health check before the container is considered unhealthy.

    You may specify between 1 and 10 retries.

    Default:
        3

    Stability:
        experimental
    """
    startPeriod: jsii.Number
    """Grace period after startup before failed health checks count.

    You may specify between 0 and 300 seconds.

    Default:
        No start period

    Stability:
        experimental
    """
    timeout: jsii.Number
    """The time period in seconds to wait for a health check to succeed before it is considered a failure.

    You may specify between 2 and 60 seconds.

    Default:
        5

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.HealthCheck", jsii_struct_bases=[_HealthCheck])
class HealthCheck(_HealthCheck):
    """Container health check configuration.

    Stability:
        experimental
    """
    command: typing.List[str]
    """Command to run, as the binary path and arguments.

    If you provide a shell command as a single string, you have to quote command-line arguments.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.Host", jsii_struct_bases=[])
class Host(jsii.compat.TypedDict, total=False):
    """A volume host.

    Stability:
        experimental
    """
    sourcePath: str
    """Source path on the host.

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-ecs.ICluster")
class ICluster(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """An ECS cluster.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IClusterProxy

    @property
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> str:
        """The ARN of this cluster.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """Name of the cluster.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """Connections manager of the cluster instances.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="hasEc2Capacity")
    def has_ec2_capacity(self) -> bool:
        """Whether the cluster has EC2 capacity associated with it.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """VPC that the cluster instances are running in.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="defaultNamespace")
    def default_namespace(self) -> typing.Optional[aws_cdk.aws_servicediscovery.INamespace]:
        """Getter for Cloudmap namespace created in the cluster.

        Stability:
            experimental
        """
        ...


class _IClusterProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """An ECS cluster.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ecs.ICluster"
    @property
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> str:
        """The ARN of this cluster.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "clusterArn")

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """Name of the cluster.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "clusterName")

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """Connections manager of the cluster instances.

        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="hasEc2Capacity")
    def has_ec2_capacity(self) -> bool:
        """Whether the cluster has EC2 capacity associated with it.

        Stability:
            experimental
        """
        return jsii.get(self, "hasEc2Capacity")

    @property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """VPC that the cluster instances are running in.

        Stability:
            experimental
        """
        return jsii.get(self, "vpc")

    @property
    @jsii.member(jsii_name="defaultNamespace")
    def default_namespace(self) -> typing.Optional[aws_cdk.aws_servicediscovery.INamespace]:
        """Getter for Cloudmap namespace created in the cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultNamespace")


@jsii.implements(ICluster)
class Cluster(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.Cluster"):
    """A container cluster that runs on your EC2 instances.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc: aws_cdk.aws_ec2.IVpc, cluster_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            vpc: The VPC where your ECS instances will be running or your ENIs will be deployed.
            clusterName: A name for the cluster. Default: CloudFormation-generated name

        Stability:
            experimental
        """
        props: ClusterProps = {"vpc": vpc}

        if cluster_name is not None:
            props["clusterName"] = cluster_name

        jsii.create(Cluster, self, [scope, id, props])

    @jsii.member(jsii_name="fromClusterAttributes")
    @classmethod
    def from_cluster_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, cluster_name: str, security_groups: typing.List[aws_cdk.aws_ec2.ISecurityGroup], vpc: aws_cdk.aws_ec2.IVpc, cluster_arn: typing.Optional[str]=None, default_namespace: typing.Optional[aws_cdk.aws_servicediscovery.INamespace]=None, has_ec2_capacity: typing.Optional[bool]=None) -> "ICluster":
        """Import an existing cluster.

        Arguments:
            scope: -
            id: -
            attrs: -
            clusterName: Name of the cluster.
            securityGroups: Security group of the cluster instances.
            vpc: VPC that the cluster instances are running in.
            clusterArn: ARN of the cluster. Default: Derived from clusterName
            defaultNamespace: Default namespace properties. Default: - No default namespace
            hasEc2Capacity: Whether the given cluster has EC2 capacity. Default: true

        Stability:
            experimental
        """
        attrs: ClusterAttributes = {"clusterName": cluster_name, "securityGroups": security_groups, "vpc": vpc}

        if cluster_arn is not None:
            attrs["clusterArn"] = cluster_arn

        if default_namespace is not None:
            attrs["defaultNamespace"] = default_namespace

        if has_ec2_capacity is not None:
            attrs["hasEc2Capacity"] = has_ec2_capacity

        return jsii.sinvoke(cls, "fromClusterAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="addAutoScalingGroup")
    def add_auto_scaling_group(self, auto_scaling_group: aws_cdk.aws_autoscaling.AutoScalingGroup, *, containers_access_instance_role: typing.Optional[bool]=None, task_drain_time_seconds: typing.Optional[jsii.Number]=None) -> None:
        """Add compute capacity to this ECS cluster in the form of an AutoScalingGroup.

        Arguments:
            autoScalingGroup: the ASG to add to this cluster. [disable-awslint:ref-via-interface] is needed in order to install the ECS agent by updating the ASGs user data.
            options: -
            containersAccessInstanceRole: Whether or not the containers can access the instance role. Default: false
            taskDrainTimeSeconds: Give tasks this many seconds to complete when instances are being scaled in. Task draining adds a Lambda and a Lifecycle hook to your AutoScalingGroup that will delay instance termination until all ECS tasks have drained from the instance. Set to 0 to disable task draining. Default: 300

        Stability:
            experimental
        """
        options: AddAutoScalingGroupCapacityOptions = {}

        if containers_access_instance_role is not None:
            options["containersAccessInstanceRole"] = containers_access_instance_role

        if task_drain_time_seconds is not None:
            options["taskDrainTimeSeconds"] = task_drain_time_seconds

        return jsii.invoke(self, "addAutoScalingGroup", [auto_scaling_group, options])

    @jsii.member(jsii_name="addCapacity")
    def add_capacity(self, id: str, *, instance_type: aws_cdk.aws_ec2.InstanceType, machine_image: typing.Optional[aws_cdk.aws_ec2.IMachineImageSource]=None, containers_access_instance_role: typing.Optional[bool]=None, task_drain_time_seconds: typing.Optional[jsii.Number]=None, allow_all_outbound: typing.Optional[bool]=None, associate_public_ip_address: typing.Optional[bool]=None, cooldown_seconds: typing.Optional[jsii.Number]=None, desired_capacity: typing.Optional[jsii.Number]=None, ignore_unmodified_size_properties: typing.Optional[bool]=None, key_name: typing.Optional[str]=None, max_capacity: typing.Optional[jsii.Number]=None, min_capacity: typing.Optional[jsii.Number]=None, notifications_topic: typing.Optional[aws_cdk.aws_sns.ITopic]=None, replacing_update_min_successful_instances_percent: typing.Optional[jsii.Number]=None, resource_signal_count: typing.Optional[jsii.Number]=None, resource_signal_timeout_sec: typing.Optional[jsii.Number]=None, rolling_update_configuration: typing.Optional[aws_cdk.aws_autoscaling.RollingUpdateConfiguration]=None, spot_price: typing.Optional[str]=None, update_type: typing.Optional[aws_cdk.aws_autoscaling.UpdateType]=None, vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None) -> aws_cdk.aws_autoscaling.AutoScalingGroup:
        """Add a default-configured AutoScalingGroup running the ECS-optimized AMI to this Cluster.

        Returns the AutoScalingGroup so you can add autoscaling settings to it.

        Arguments:
            id: -
            options: -
            instanceType: The type of EC2 instance to launch into your Autoscaling Group.
            machineImage: The machine image for the ECS instances. Default: - Amazon Linux 1
            containersAccessInstanceRole: Whether or not the containers can access the instance role. Default: false
            taskDrainTimeSeconds: Give tasks this many seconds to complete when instances are being scaled in. Task draining adds a Lambda and a Lifecycle hook to your AutoScalingGroup that will delay instance termination until all ECS tasks have drained from the instance. Set to 0 to disable task draining. Default: 300
            allowAllOutbound: Whether the instances can initiate connections to anywhere by default. Default: true
            associatePublicIpAddress: Whether instances in the Auto Scaling Group should have public IP addresses associated with them. Default: - Use subnet setting.
            cooldownSeconds: Default scaling cooldown for this AutoScalingGroup. Default: 300 (5 minutes)
            desiredCapacity: Initial amount of instances in the fleet. Default: 1
            ignoreUnmodifiedSizeProperties: If the ASG has scheduled actions, don't reset unchanged group sizes. Only used if the ASG has scheduled actions (which may scale your ASG up or down regardless of cdk deployments). If true, the size of the group will only be reset if it has been changed in the CDK app. If false, the sizes will always be changed back to what they were in the CDK app on deployment. Default: true
            keyName: Name of SSH keypair to grant access to instances. Default: - No SSH access will be possible.
            maxCapacity: Maximum number of instances in the fleet. Default: desiredCapacity
            minCapacity: Minimum number of instances in the fleet. Default: 1
            notificationsTopic: SNS topic to send notifications about fleet changes. Default: - No fleet change notifications will be sent.
            replacingUpdateMinSuccessfulInstancesPercent: Configuration for replacing updates. Only used if updateType == UpdateType.ReplacingUpdate. Specifies how many instances must signal success for the update to succeed. Default: minSuccessfulInstancesPercent
            resourceSignalCount: How many ResourceSignal calls CloudFormation expects before the resource is considered created. Default: 1
            resourceSignalTimeoutSec: The length of time to wait for the resourceSignalCount. The maximum value is 43200 (12 hours). Default: 300 (5 minutes)
            rollingUpdateConfiguration: Configuration for rolling updates. Only used if updateType == UpdateType.RollingUpdate. Default: - RollingUpdateConfiguration with defaults.
            spotPrice: The maximum hourly price (in USD) to be paid for any Spot Instance launched to fulfill the request. Spot Instances are launched when the price you specify exceeds the current Spot market price. Default: none
            updateType: What to do when an AutoScalingGroup's instance configuration is changed. This is applied when any of the settings on the ASG are changed that affect how the instances should be created (VPC, instance type, startup scripts, etc.). It indicates how the existing instances should be replaced with new instances matching the new config. By default, nothing is done and only new instances are launched with the new config. Default: UpdateType.None
            vpcSubnets: Where to place instances within the VPC. Default: - All Private subnets.

        Stability:
            experimental
        """
        options: AddCapacityOptions = {"instanceType": instance_type}

        if machine_image is not None:
            options["machineImage"] = machine_image

        if containers_access_instance_role is not None:
            options["containersAccessInstanceRole"] = containers_access_instance_role

        if task_drain_time_seconds is not None:
            options["taskDrainTimeSeconds"] = task_drain_time_seconds

        if allow_all_outbound is not None:
            options["allowAllOutbound"] = allow_all_outbound

        if associate_public_ip_address is not None:
            options["associatePublicIpAddress"] = associate_public_ip_address

        if cooldown_seconds is not None:
            options["cooldownSeconds"] = cooldown_seconds

        if desired_capacity is not None:
            options["desiredCapacity"] = desired_capacity

        if ignore_unmodified_size_properties is not None:
            options["ignoreUnmodifiedSizeProperties"] = ignore_unmodified_size_properties

        if key_name is not None:
            options["keyName"] = key_name

        if max_capacity is not None:
            options["maxCapacity"] = max_capacity

        if min_capacity is not None:
            options["minCapacity"] = min_capacity

        if notifications_topic is not None:
            options["notificationsTopic"] = notifications_topic

        if replacing_update_min_successful_instances_percent is not None:
            options["replacingUpdateMinSuccessfulInstancesPercent"] = replacing_update_min_successful_instances_percent

        if resource_signal_count is not None:
            options["resourceSignalCount"] = resource_signal_count

        if resource_signal_timeout_sec is not None:
            options["resourceSignalTimeoutSec"] = resource_signal_timeout_sec

        if rolling_update_configuration is not None:
            options["rollingUpdateConfiguration"] = rolling_update_configuration

        if spot_price is not None:
            options["spotPrice"] = spot_price

        if update_type is not None:
            options["updateType"] = update_type

        if vpc_subnets is not None:
            options["vpcSubnets"] = vpc_subnets

        return jsii.invoke(self, "addCapacity", [id, options])

    @jsii.member(jsii_name="addDefaultCloudMapNamespace")
    def add_default_cloud_map_namespace(self, *, name: str, type: typing.Optional["NamespaceType"]=None, vpc: typing.Optional[aws_cdk.aws_ec2.IVpc]=None) -> aws_cdk.aws_servicediscovery.INamespace:
        """Add an AWS Cloud Map DNS namespace for this cluster. NOTE: HttpNamespaces are not supported, as ECS always requires a DNSConfig when registering an instance to a Cloud Map service.

        Arguments:
            options: -
            name: The domain name for the namespace, such as foo.com.
            type: The type of CloudMap Namespace to create in your cluster. Default: PrivateDns
            vpc: The Amazon VPC that you want to associate the namespace with. Required for Private DNS namespaces Default: VPC of the cluster for Private DNS Namespace, otherwise none

        Stability:
            experimental
        """
        options: NamespaceOptions = {"name": name}

        if type is not None:
            options["type"] = type

        if vpc is not None:
            options["vpc"] = vpc

        return jsii.invoke(self, "addDefaultCloudMapNamespace", [options])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Cluster.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricCpuReservation")
    def metric_cpu_reservation(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for cluster CPU reservation.

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            average over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricCpuReservation", [props])

    @jsii.member(jsii_name="metricMemoryReservation")
    def metric_memory_reservation(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for cluster Memory reservation.

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            average over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricMemoryReservation", [props])

    @property
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> str:
        """The ARN of this cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "clusterArn")

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """The name of this cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "clusterName")

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """Connections manager for the EC2 cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="hasEc2Capacity")
    def has_ec2_capacity(self) -> bool:
        """Whether the cluster has EC2 capacity associated with it.

        Stability:
            experimental
        """
        return jsii.get(self, "hasEc2Capacity")

    @property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """The VPC this cluster was created in.

        Stability:
            experimental
        """
        return jsii.get(self, "vpc")

    @property
    @jsii.member(jsii_name="defaultNamespace")
    def default_namespace(self) -> typing.Optional[aws_cdk.aws_servicediscovery.INamespace]:
        """Getter for namespace added to cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultNamespace")


@jsii.interface(jsii_type="@aws-cdk/aws-ecs.IService")
class IService(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IServiceProxy

    @property
    @jsii.member(jsii_name="serviceArn")
    def service_arn(self) -> str:
        """ARN of this service.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IServiceProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ecs.IService"
    @property
    @jsii.member(jsii_name="serviceArn")
    def service_arn(self) -> str:
        """ARN of this service.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "serviceArn")


@jsii.implements(IService, aws_cdk.aws_elasticloadbalancingv2.IApplicationLoadBalancerTarget, aws_cdk.aws_elasticloadbalancingv2.INetworkLoadBalancerTarget)
class BaseService(aws_cdk.cdk.Resource, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-ecs.BaseService"):
    """Base class for Ecs and Fargate services.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _BaseServiceProxy

    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, props: "BaseServiceProps", additional_props: typing.Any, cluster_name: str, task_definition: "TaskDefinition") -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            additionalProps: -
            clusterName: -
            taskDefinition: -

        Stability:
            experimental
        """
        jsii.create(BaseService, self, [scope, id, props, additional_props, cluster_name, task_definition])

    @jsii.member(jsii_name="attachToApplicationTargetGroup")
    def attach_to_application_target_group(self, target_group: aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup) -> aws_cdk.aws_elasticloadbalancingv2.LoadBalancerTargetProps:
        """Called when the service is attached to an ALB.

        Don't call this function directly. Instead, call listener.addTarget()
        to add this service to a load balancer.

        Arguments:
            targetGroup: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachToApplicationTargetGroup", [target_group])

    @jsii.member(jsii_name="attachToNetworkTargetGroup")
    def attach_to_network_target_group(self, target_group: aws_cdk.aws_elasticloadbalancingv2.NetworkTargetGroup) -> aws_cdk.aws_elasticloadbalancingv2.LoadBalancerTargetProps:
        """Called when the service is attached to an NLB.

        Don't call this function directly. Instead, call listener.addTarget()
        to add this service to a load balancer.

        Arguments:
            targetGroup: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachToNetworkTargetGroup", [target_group])

    @jsii.member(jsii_name="autoScaleTaskCount")
    def auto_scale_task_count(self, *, max_capacity: jsii.Number, min_capacity: typing.Optional[jsii.Number]=None) -> "ScalableTaskCount":
        """Enable autoscaling for the number of tasks in this service.

        Arguments:
            props: -
            maxCapacity: Maximum capacity to scale to.
            minCapacity: Minimum capacity to scale to. Default: 1

        Stability:
            experimental
        """
        props: aws_cdk.aws_applicationautoscaling.EnableScalingProps = {"maxCapacity": max_capacity}

        if min_capacity is not None:
            props["minCapacity"] = min_capacity

        return jsii.invoke(self, "autoScaleTaskCount", [props])

    @jsii.member(jsii_name="configureAwsVpcNetworking")
    def _configure_aws_vpc_networking(self, vpc: aws_cdk.aws_ec2.IVpc, assign_public_ip: typing.Optional[bool]=None, vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None, security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]=None) -> None:
        """Set up AWSVPC networking for this construct.

        Arguments:
            vpc: -
            assignPublicIp: -
            vpcSubnets: -
            securityGroup: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "configureAwsVpcNetworking", [vpc, assign_public_ip, vpc_subnets, security_group])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Service.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """Name of this service's cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "clusterName")

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """Manage allowed network traffic for this service.

        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="serviceArn")
    def service_arn(self) -> str:
        """ARN of this service.

        Stability:
            experimental
        """
        return jsii.get(self, "serviceArn")

    @property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> str:
        """Name of this service.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "serviceName")

    @property
    @jsii.member(jsii_name="taskDefinition")
    def task_definition(self) -> "TaskDefinition":
        """Task definition this service is associated with.

        Stability:
            experimental
        """
        return jsii.get(self, "taskDefinition")

    @property
    @jsii.member(jsii_name="cluster")
    def _cluster(self) -> "ICluster":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cluster")

    @_cluster.setter
    def _cluster(self, value: "ICluster"):
        return jsii.set(self, "cluster", value)

    @property
    @jsii.member(jsii_name="loadBalancers")
    def _load_balancers(self) -> typing.List["CfnService.LoadBalancerProperty"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "loadBalancers")

    @_load_balancers.setter
    def _load_balancers(self, value: typing.List["CfnService.LoadBalancerProperty"]):
        return jsii.set(self, "loadBalancers", value)

    @property
    @jsii.member(jsii_name="serviceRegistries")
    def _service_registries(self) -> typing.List["CfnService.ServiceRegistryProperty"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "serviceRegistries")

    @_service_registries.setter
    def _service_registries(self, value: typing.List["CfnService.ServiceRegistryProperty"]):
        return jsii.set(self, "serviceRegistries", value)

    @property
    @jsii.member(jsii_name="cloudmapService")
    def _cloudmap_service(self) -> typing.Optional[aws_cdk.aws_servicediscovery.Service]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cloudmapService")

    @_cloudmap_service.setter
    def _cloudmap_service(self, value: typing.Optional[aws_cdk.aws_servicediscovery.Service]):
        return jsii.set(self, "cloudmapService", value)

    @property
    @jsii.member(jsii_name="networkConfiguration")
    def _network_configuration(self) -> typing.Optional["CfnService.NetworkConfigurationProperty"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "networkConfiguration")

    @_network_configuration.setter
    def _network_configuration(self, value: typing.Optional["CfnService.NetworkConfigurationProperty"]):
        return jsii.set(self, "networkConfiguration", value)


class _BaseServiceProxy(BaseService, jsii.proxy_for(aws_cdk.cdk.Resource)):
    pass

@jsii.interface(jsii_type="@aws-cdk/aws-ecs.IEc2Service")
class IEc2Service(IService, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IEc2ServiceProxy

    pass

class _IEc2ServiceProxy(jsii.proxy_for(IService)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ecs.IEc2Service"
    pass

@jsii.implements(IEc2Service, aws_cdk.aws_elasticloadbalancing.ILoadBalancerTarget)
class Ec2Service(BaseService, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.Ec2Service"):
    """Start a service on an ECS cluster.

    Stability:
        experimental
    resource:
        AWS::ECS::Service
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, task_definition: "TaskDefinition", daemon: typing.Optional[bool]=None, placement_constraints: typing.Optional[typing.List["PlacementConstraint"]]=None, placement_strategies: typing.Optional[typing.List["PlacementStrategy"]]=None, security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]=None, vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None, cluster: "ICluster", desired_count: typing.Optional[jsii.Number]=None, health_check_grace_period_seconds: typing.Optional[jsii.Number]=None, long_arn_enabled: typing.Optional[bool]=None, maximum_percent: typing.Optional[jsii.Number]=None, minimum_healthy_percent: typing.Optional[jsii.Number]=None, service_discovery_options: typing.Optional["ServiceDiscoveryOptions"]=None, service_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            taskDefinition: Task Definition used for running tasks in the service. [disable-awslint:ref-via-interface]
            daemon: Deploy exactly one task on each instance in your cluster. When using this strategy, do not specify a desired number of tasks or any task placement strategies. Default: false
            placementConstraints: Placement constraints. Default: - No constraints.
            placementStrategies: Placement strategies. Default: - No strategies.
            securityGroup: Existing security group to use for the task's ENIs. (Only applicable in case the TaskDefinition is configured for AwsVpc networking) Default: - A new security group is created.
            vpcSubnets: In what subnets to place the task's ENIs. (Only applicable in case the TaskDefinition is configured for AwsVpc networking) Default: - Private subnets.
            cluster: Cluster where service will be deployed.
            desiredCount: Number of desired copies of running tasks. Default: 1
            healthCheckGracePeriodSeconds: Time after startup to ignore unhealthy load balancer checks. Default: ??? FIXME
            longArnEnabled: Whether the new long ARN format has been enabled on ECS services. NOTE: This assumes customer has opted into the new format for the IAM role used for the service, and is a workaround for a current bug in Cloudformation in which the service name is not correctly returned when long ARN is enabled. Old ARN format: arn:aws:ecs:region:aws_account_id:service/service-name New ARN format: arn:aws:ecs:region:aws_account_id:service/cluster-name/service-name See: https://docs.aws.amazon.com/AmazonECS/latest/userguide/ecs-resource-ids.html Default: false
            maximumPercent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
            minimumHealthyPercent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
            serviceDiscoveryOptions: Options for enabling AWS Cloud Map service discovery for the service. Default: - AWS Cloud Map service discovery is not enabled.
            serviceName: A name for the service. Default: - CloudFormation-generated name.

        Stability:
            experimental
        """
        props: Ec2ServiceProps = {"taskDefinition": task_definition, "cluster": cluster}

        if daemon is not None:
            props["daemon"] = daemon

        if placement_constraints is not None:
            props["placementConstraints"] = placement_constraints

        if placement_strategies is not None:
            props["placementStrategies"] = placement_strategies

        if security_group is not None:
            props["securityGroup"] = security_group

        if vpc_subnets is not None:
            props["vpcSubnets"] = vpc_subnets

        if desired_count is not None:
            props["desiredCount"] = desired_count

        if health_check_grace_period_seconds is not None:
            props["healthCheckGracePeriodSeconds"] = health_check_grace_period_seconds

        if long_arn_enabled is not None:
            props["longArnEnabled"] = long_arn_enabled

        if maximum_percent is not None:
            props["maximumPercent"] = maximum_percent

        if minimum_healthy_percent is not None:
            props["minimumHealthyPercent"] = minimum_healthy_percent

        if service_discovery_options is not None:
            props["serviceDiscoveryOptions"] = service_discovery_options

        if service_name is not None:
            props["serviceName"] = service_name

        jsii.create(Ec2Service, self, [scope, id, props])

    @jsii.member(jsii_name="fromEc2ServiceArn")
    @classmethod
    def from_ec2_service_arn(cls, scope: aws_cdk.cdk.Construct, id: str, ec2_service_arn: str) -> "IEc2Service":
        """
        Arguments:
            scope: -
            id: -
            ec2ServiceArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromEc2ServiceArn", [scope, id, ec2_service_arn])

    @jsii.member(jsii_name="addPlacementConstraints")
    def add_placement_constraints(self, *constraints: "PlacementConstraint") -> None:
        """Add one or more placement strategies.

        Arguments:
            constraints: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addPlacementConstraints", [*constraints])

    @jsii.member(jsii_name="addPlacementStrategies")
    def add_placement_strategies(self, *strategies: "PlacementStrategy") -> None:
        """Add one or more placement strategies.

        Arguments:
            strategies: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addPlacementStrategies", [*strategies])

    @jsii.member(jsii_name="attachToClassicLB")
    def attach_to_classic_lb(self, load_balancer: aws_cdk.aws_elasticloadbalancing.LoadBalancer) -> None:
        """Register this service as the target of a Classic Load Balancer.

        Don't call this. Call ``loadBalancer.addTarget()`` instead.

        Arguments:
            loadBalancer: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "attachToClassicLB", [load_balancer])

    @jsii.member(jsii_name="metric")
    def metric(self, metric_name: str, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Return the given named metric for this Service.

        Arguments:
            metricName: -
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metric", [metric_name, props])

    @jsii.member(jsii_name="metricCpuUtilization")
    def metric_cpu_utilization(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for cluster CPU utilization.

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            average over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricCpuUtilization", [props])

    @jsii.member(jsii_name="metricMemoryUtilization")
    def metric_memory_utilization(self, *, color: typing.Optional[str]=None, dimensions: typing.Optional[typing.Mapping[str,typing.Any]]=None, label: typing.Optional[str]=None, period_sec: typing.Optional[jsii.Number]=None, statistic: typing.Optional[str]=None, unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit]=None) -> aws_cdk.aws_cloudwatch.Metric:
        """Metric for cluster Memory utilization.

        Arguments:
            props: -
            color: Color for this metric when added to a Graph in a Dashboard.
            dimensions: Dimensions of the metric. Default: - No dimensions.
            label: Label for this metric when added to a Graph in a Dashboard.
            periodSec: The period over which the specified statistic is applied. Specify time in seconds, in multiples of 60. Default: 300
            statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
            unit: Unit for the metric that is associated with the alarm.

        Default:
            average over 5 minutes

        Stability:
            experimental
        """
        props: aws_cdk.aws_cloudwatch.MetricOptions = {}

        if color is not None:
            props["color"] = color

        if dimensions is not None:
            props["dimensions"] = dimensions

        if label is not None:
            props["label"] = label

        if period_sec is not None:
            props["periodSec"] = period_sec

        if statistic is not None:
            props["statistic"] = statistic

        if unit is not None:
            props["unit"] = unit

        return jsii.invoke(self, "metricMemoryUtilization", [props])

    @jsii.member(jsii_name="placeOnMemberOf")
    def place_on_member_of(self, *expressions: str) -> None:
        """Place tasks only on instances matching the given query expression.

        You can specify multiple expressions in one call. The tasks will only
        be placed on instances matching all expressions.

        Arguments:
            expressions: -

        Deprecated:
            Use addPlacementConstraints() instead.

        See:
            https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cluster-query-language.html
        Stability:
            deprecated
        """
        return jsii.invoke(self, "placeOnMemberOf", [*expressions])

    @jsii.member(jsii_name="placePackedBy")
    def place_packed_by(self, resource: "BinPackResource") -> None:
        """Try to place tasks on instances with the least amount of indicated resource available.

        This ensures the total consumption of this resource is lowest.

        Arguments:
            resource: -

        Deprecated:
            Use addPlacementStrategies() instead.

        Stability:
            deprecated
        """
        return jsii.invoke(self, "placePackedBy", [resource])

    @jsii.member(jsii_name="placeRandomly")
    def place_randomly(self) -> None:
        """Place tasks randomly across the available instances.

        Deprecated:
            Use addPlacementStrategies() instead.

        Stability:
            deprecated
        """
        return jsii.invoke(self, "placeRandomly", [])

    @jsii.member(jsii_name="placeSpreadAcross")
    def place_spread_across(self, *fields: str) -> None:
        """Try to place tasks spread across instance attributes.

        You can use one of the built-in attributes found on ``BuiltInAttributes``
        or supply your own custom instance attributes. If more than one attribute
        is supplied, spreading is done in order.

        Arguments:
            fields: -

        Default:
            attributes instanceId

        Deprecated:
            Use addPlacementStrategies() instead.

        Stability:
            deprecated
        """
        return jsii.invoke(self, "placeSpreadAcross", [*fields])

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[str]:
        """Validate this Ec2Service.

        Stability:
            experimental
        """
        return jsii.invoke(self, "validate", [])

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """Name of the cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "clusterName")


@jsii.interface(jsii_type="@aws-cdk/aws-ecs.IFargateService")
class IFargateService(IService, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IFargateServiceProxy

    pass

class _IFargateServiceProxy(jsii.proxy_for(IService)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ecs.IFargateService"
    pass

@jsii.implements(IFargateService)
class FargateService(BaseService, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.FargateService"):
    """Start a service on an ECS cluster.

    Stability:
        experimental
    resource:
        AWS::ECS::Service
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, task_definition: "TaskDefinition", assign_public_ip: typing.Optional[bool]=None, platform_version: typing.Optional["FargatePlatformVersion"]=None, security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]=None, vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None, cluster: "ICluster", desired_count: typing.Optional[jsii.Number]=None, health_check_grace_period_seconds: typing.Optional[jsii.Number]=None, long_arn_enabled: typing.Optional[bool]=None, maximum_percent: typing.Optional[jsii.Number]=None, minimum_healthy_percent: typing.Optional[jsii.Number]=None, service_discovery_options: typing.Optional["ServiceDiscoveryOptions"]=None, service_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            taskDefinition: Task Definition used for running tasks in the service. [disable-awslint:ref-via-interface]
            assignPublicIp: Assign public IP addresses to each task. Default: - Use subnet default.
            platformVersion: Fargate platform version to run this service on. Unless you have specific compatibility requirements, you don't need to specify this. Default: Latest
            securityGroup: Existing security group to use for the tasks. Default: - A new security group is created.
            vpcSubnets: In what subnets to place the task's ENIs. Default: - Private subnets.
            cluster: Cluster where service will be deployed.
            desiredCount: Number of desired copies of running tasks. Default: 1
            healthCheckGracePeriodSeconds: Time after startup to ignore unhealthy load balancer checks. Default: ??? FIXME
            longArnEnabled: Whether the new long ARN format has been enabled on ECS services. NOTE: This assumes customer has opted into the new format for the IAM role used for the service, and is a workaround for a current bug in Cloudformation in which the service name is not correctly returned when long ARN is enabled. Old ARN format: arn:aws:ecs:region:aws_account_id:service/service-name New ARN format: arn:aws:ecs:region:aws_account_id:service/cluster-name/service-name See: https://docs.aws.amazon.com/AmazonECS/latest/userguide/ecs-resource-ids.html Default: false
            maximumPercent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
            minimumHealthyPercent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
            serviceDiscoveryOptions: Options for enabling AWS Cloud Map service discovery for the service. Default: - AWS Cloud Map service discovery is not enabled.
            serviceName: A name for the service. Default: - CloudFormation-generated name.

        Stability:
            experimental
        """
        props: FargateServiceProps = {"taskDefinition": task_definition, "cluster": cluster}

        if assign_public_ip is not None:
            props["assignPublicIp"] = assign_public_ip

        if platform_version is not None:
            props["platformVersion"] = platform_version

        if security_group is not None:
            props["securityGroup"] = security_group

        if vpc_subnets is not None:
            props["vpcSubnets"] = vpc_subnets

        if desired_count is not None:
            props["desiredCount"] = desired_count

        if health_check_grace_period_seconds is not None:
            props["healthCheckGracePeriodSeconds"] = health_check_grace_period_seconds

        if long_arn_enabled is not None:
            props["longArnEnabled"] = long_arn_enabled

        if maximum_percent is not None:
            props["maximumPercent"] = maximum_percent

        if minimum_healthy_percent is not None:
            props["minimumHealthyPercent"] = minimum_healthy_percent

        if service_discovery_options is not None:
            props["serviceDiscoveryOptions"] = service_discovery_options

        if service_name is not None:
            props["serviceName"] = service_name

        jsii.create(FargateService, self, [scope, id, props])

    @jsii.member(jsii_name="fromFargateServiceArn")
    @classmethod
    def from_fargate_service_arn(cls, scope: aws_cdk.cdk.Construct, id: str, fargate_service_arn: str) -> "IFargateService":
        """
        Arguments:
            scope: -
            id: -
            fargateServiceArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromFargateServiceArn", [scope, id, fargate_service_arn])


@jsii.interface(jsii_type="@aws-cdk/aws-ecs.ITaskDefinition")
class ITaskDefinition(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ITaskDefinitionProxy

    @property
    @jsii.member(jsii_name="compatibility")
    def compatibility(self) -> "Compatibility":
        """What launch types this task definition should be compatible with.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="isEc2Compatible")
    def is_ec2_compatible(self) -> bool:
        """Return true if the task definition can be run on an EC2 cluster.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="isFargateCompatible")
    def is_fargate_compatible(self) -> bool:
        """Return true if the task definition can be run on a Fargate cluster.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="taskDefinitionArn")
    def task_definition_arn(self) -> str:
        """ARN of this task definition.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """Execution role for this task definition.

        Stability:
            experimental
        """
        ...


class _ITaskDefinitionProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ecs.ITaskDefinition"
    @property
    @jsii.member(jsii_name="compatibility")
    def compatibility(self) -> "Compatibility":
        """What launch types this task definition should be compatible with.

        Stability:
            experimental
        """
        return jsii.get(self, "compatibility")

    @property
    @jsii.member(jsii_name="isEc2Compatible")
    def is_ec2_compatible(self) -> bool:
        """Return true if the task definition can be run on an EC2 cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "isEc2Compatible")

    @property
    @jsii.member(jsii_name="isFargateCompatible")
    def is_fargate_compatible(self) -> bool:
        """Return true if the task definition can be run on a Fargate cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "isFargateCompatible")

    @property
    @jsii.member(jsii_name="taskDefinitionArn")
    def task_definition_arn(self) -> str:
        """ARN of this task definition.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "taskDefinitionArn")

    @property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """Execution role for this task definition.

        Stability:
            experimental
        """
        return jsii.get(self, "executionRole")


@jsii.interface(jsii_type="@aws-cdk/aws-ecs.IEc2TaskDefinition")
class IEc2TaskDefinition(ITaskDefinition, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IEc2TaskDefinitionProxy

    pass

class _IEc2TaskDefinitionProxy(jsii.proxy_for(ITaskDefinition)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ecs.IEc2TaskDefinition"
    pass

@jsii.interface(jsii_type="@aws-cdk/aws-ecs.IFargateTaskDefinition")
class IFargateTaskDefinition(ITaskDefinition, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IFargateTaskDefinitionProxy

    pass

class _IFargateTaskDefinitionProxy(jsii.proxy_for(ITaskDefinition)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ecs.IFargateTaskDefinition"
    pass

@jsii.interface(jsii_type="@aws-cdk/aws-ecs.ITaskDefinitionExtension")
class ITaskDefinitionExtension(jsii.compat.Protocol):
    """An extension for Task Definitions.

    Classes that want to make changes to a TaskDefinition (such as
    adding helper containers) can implement this interface, and can
    then be "added" to a TaskDefinition like so::

       taskDefinition.addExtension(new MyExtension("some_parameter"));

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ITaskDefinitionExtensionProxy

    @jsii.member(jsii_name="extend")
    def extend(self, task_definition: "TaskDefinition") -> None:
        """Apply the extension to the given TaskDefinition.

        Arguments:
            taskDefinition: [disable-awslint:ref-via-interface].

        Stability:
            experimental
        """
        ...


class _ITaskDefinitionExtensionProxy():
    """An extension for Task Definitions.

    Classes that want to make changes to a TaskDefinition (such as
    adding helper containers) can implement this interface, and can
    then be "added" to a TaskDefinition like so::

       taskDefinition.addExtension(new MyExtension("some_parameter"));

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-ecs.ITaskDefinitionExtension"
    @jsii.member(jsii_name="extend")
    def extend(self, task_definition: "TaskDefinition") -> None:
        """Apply the extension to the given TaskDefinition.

        Arguments:
            taskDefinition: [disable-awslint:ref-via-interface].

        Stability:
            experimental
        """
        return jsii.invoke(self, "extend", [task_definition])


class LinuxParameters(aws_cdk.cdk.Construct, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.LinuxParameters"):
    """Linux Parameters for an ECS container.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, init_process_enabled: typing.Optional[bool]=None, shared_memory_size: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            initProcessEnabled: Whether the init process is enabled. Default: false
            sharedMemorySize: The shared memory size. Default: No shared memory.

        Stability:
            experimental
        """
        props: LinuxParametersProps = {}

        if init_process_enabled is not None:
            props["initProcessEnabled"] = init_process_enabled

        if shared_memory_size is not None:
            props["sharedMemorySize"] = shared_memory_size

        jsii.create(LinuxParameters, self, [scope, id, props])

    @jsii.member(jsii_name="addCapabilities")
    def add_capabilities(self, *cap: "Capability") -> None:
        """Add one or more capabilities.

        Only works with EC2 launch type.

        Arguments:
            cap: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addCapabilities", [*cap])

    @jsii.member(jsii_name="addDevices")
    def add_devices(self, *, host_path: str, container_path: typing.Optional[str]=None, permissions: typing.Optional[typing.List["DevicePermission"]]=None) -> None:
        """Add one or more devices.

        Arguments:
            device: -
            hostPath: Path on the host.
            containerPath: Path in the container. Default: Same path as the host
            permissions: Permissions. Default: Readonly

        Stability:
            experimental
        """
        device: Device = {"hostPath": host_path}

        if container_path is not None:
            device["containerPath"] = container_path

        if permissions is not None:
            device["permissions"] = permissions

        return jsii.invoke(self, "addDevices", [*device])

    @jsii.member(jsii_name="addTmpfs")
    def add_tmpfs(self, *, container_path: str, size: jsii.Number, mount_options: typing.Optional[typing.List["TmpfsMountOption"]]=None) -> None:
        """Add one or more tmpfs mounts.

        Only works with EC2 launch type.

        Arguments:
            tmpfs: -
            containerPath: Path in the container to mount.
            size: Size of the volume.
            mountOptions: Mount options.

        Stability:
            experimental
        """
        tmpfs: Tmpfs = {"containerPath": container_path, "size": size}

        if mount_options is not None:
            tmpfs["mountOptions"] = mount_options

        return jsii.invoke(self, "addTmpfs", [*tmpfs])

    @jsii.member(jsii_name="dropCapabilities")
    def drop_capabilities(self, *cap: "Capability") -> None:
        """Drop one or more capabilities.

        Only works with EC2 launch type.

        Arguments:
            cap: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "dropCapabilities", [*cap])

    @jsii.member(jsii_name="renderLinuxParameters")
    def render_linux_parameters(self) -> "CfnTaskDefinition.LinuxParametersProperty":
        """Render the Linux parameters to a CloudFormation object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderLinuxParameters", [])


@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.LinuxParametersProps", jsii_struct_bases=[])
class LinuxParametersProps(jsii.compat.TypedDict, total=False):
    """Properties for defining Linux Parameters.

    Stability:
        experimental
    """
    initProcessEnabled: bool
    """Whether the init process is enabled.

    Default:
        false

    Stability:
        experimental
    """

    sharedMemorySize: jsii.Number
    """The shared memory size.

    Default:
        No shared memory.

    Stability:
        experimental
    """

class LogDriver(aws_cdk.cdk.Construct, metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-ecs.LogDriver"):
    """Base class for log drivers.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _LogDriverProxy

    def __init__(self, scope: aws_cdk.cdk.Construct, id: str) -> None:
        """Creates a new construct node.

        Arguments:
            scope: The scope in which to define this construct.
            id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.

        Stability:
            experimental
        """
        jsii.create(LogDriver, self, [scope, id])

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def bind(self, container_definition: "ContainerDefinition") -> None:
        """Called when the log driver is configured on a container.

        Arguments:
            containerDefinition: -

        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="renderLogDriver")
    @abc.abstractmethod
    def render_log_driver(self) -> "CfnTaskDefinition.LogConfigurationProperty":
        """Return the log driver CloudFormation JSON.

        Stability:
            experimental
        """
        ...


class _LogDriverProxy(LogDriver):
    @jsii.member(jsii_name="bind")
    def bind(self, container_definition: "ContainerDefinition") -> None:
        """Called when the log driver is configured on a container.

        Arguments:
            containerDefinition: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [container_definition])

    @jsii.member(jsii_name="renderLogDriver")
    def render_log_driver(self) -> "CfnTaskDefinition.LogConfigurationProperty":
        """Return the log driver CloudFormation JSON.

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderLogDriver", [])


class AwsLogDriver(LogDriver, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.AwsLogDriver"):
    """A log driver that will log to an AWS Log Group.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, stream_prefix: str, datetime_format: typing.Optional[str]=None, log_group: typing.Optional[aws_cdk.aws_logs.ILogGroup]=None, log_retention_days: typing.Optional[aws_cdk.aws_logs.RetentionDays]=None, multiline_pattern: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            streamPrefix: Prefix for the log streams. The awslogs-stream-prefix option allows you to associate a log stream with the specified prefix, the container name, and the ID of the Amazon ECS task to which the container belongs. If you specify a prefix with this option, then the log stream takes the following format:: prefix-name/container-name/ecs-task-id
            datetimeFormat: This option defines a multiline start pattern in Python strftime format. A log message consists of a line that matches the pattern and any following lines that don’t match the pattern. Thus the matched line is the delimiter between log messages. Default: - No multiline matching.
            logGroup: The log group to log to. Default: - A log group is automatically created.
            logRetentionDays: The number of days log events are kept in CloudWatch Logs when the log group is automatically created by this construct. Default: - Logs never expire.
            multilinePattern: This option defines a multiline start pattern using a regular expression. A log message consists of a line that matches the pattern and any following lines that don’t match the pattern. Thus the matched line is the delimiter between log messages. This option is ignored if datetimeFormat is also configured. Default: - No multiline matching.

        Stability:
            experimental
        """
        props: AwsLogDriverProps = {"streamPrefix": stream_prefix}

        if datetime_format is not None:
            props["datetimeFormat"] = datetime_format

        if log_group is not None:
            props["logGroup"] = log_group

        if log_retention_days is not None:
            props["logRetentionDays"] = log_retention_days

        if multiline_pattern is not None:
            props["multilinePattern"] = multiline_pattern

        jsii.create(AwsLogDriver, self, [scope, id, props])

    @jsii.member(jsii_name="bind")
    def bind(self, container_definition: "ContainerDefinition") -> None:
        """Called when the log driver is configured on a container.

        Arguments:
            containerDefinition: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [container_definition])

    @jsii.member(jsii_name="renderLogDriver")
    def render_log_driver(self) -> "CfnTaskDefinition.LogConfigurationProperty":
        """Return the log driver CloudFormation JSON.

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderLogDriver", [])

    @property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> aws_cdk.aws_logs.ILogGroup:
        """The log group that the logs will be sent to.

        Stability:
            experimental
        """
        return jsii.get(self, "logGroup")

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "AwsLogDriverProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")


@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.MemoryUtilizationScalingProps", jsii_struct_bases=[aws_cdk.aws_applicationautoscaling.BaseTargetTrackingProps])
class MemoryUtilizationScalingProps(aws_cdk.aws_applicationautoscaling.BaseTargetTrackingProps, jsii.compat.TypedDict):
    """Properties for enabling scaling based on memory utilization.

    Stability:
        experimental
    """
    targetUtilizationPercent: jsii.Number
    """Target average memory utilization across the task.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.MountPoint", jsii_struct_bases=[])
class MountPoint(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    containerPath: str
    """
    Stability:
        experimental
    """

    readOnly: bool
    """
    Stability:
        experimental
    """

    sourceVolume: str
    """
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _NamespaceOptions(jsii.compat.TypedDict, total=False):
    type: "NamespaceType"
    """The type of CloudMap Namespace to create in your cluster.

    Default:
        PrivateDns

    Stability:
        experimental
    """
    vpc: aws_cdk.aws_ec2.IVpc
    """The Amazon VPC that you want to associate the namespace with.

    Required for Private DNS namespaces

    Default:
        VPC of the cluster for Private DNS Namespace, otherwise none

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.NamespaceOptions", jsii_struct_bases=[_NamespaceOptions])
class NamespaceOptions(_NamespaceOptions):
    """
    Stability:
        experimental
    """
    name: str
    """The domain name for the namespace, such as foo.com.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ecs.NamespaceType")
class NamespaceType(enum.Enum):
    """The type of CloudMap namespace to create.

    Stability:
        experimental
    """
    PrivateDns = "PrivateDns"
    """Create a private DNS namespace.

    Stability:
        experimental
    """
    PublicDns = "PublicDns"
    """Create a public DNS namespace.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ecs.NetworkMode")
class NetworkMode(enum.Enum):
    """The Docker networking mode to use for the containers in the task.

    Stability:
        experimental
    """
    None_ = "None"
    """The task's containers do not have external connectivity and port mappings can't be specified in the container definition.

    Stability:
        experimental
    """
    Bridge = "Bridge"
    """The task utilizes Docker's built-in virtual network which runs inside each container instance.

    Stability:
        experimental
    """
    AwsVpc = "AwsVpc"
    """The task is allocated an elastic network interface.

    Stability:
        experimental
    """
    Host = "Host"
    """The task bypasses Docker's built-in virtual network and maps container ports directly to the EC2 instance's network interface directly.

    In this mode, you can't run multiple instantiations of the same task on a
    single container instance when port mappings are used.

    Stability:
        experimental
    """

class PlacementConstraint(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.PlacementConstraint"):
    """An ECS placement constraint.

    Tasks will only be placed on instances that match these rules.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="distinctInstances")
    @classmethod
    def distinct_instances(cls) -> "PlacementConstraint":
        """Place every task on a different instance.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "distinctInstances", [])

    @jsii.member(jsii_name="memberOf")
    @classmethod
    def member_of(cls, *expressions: str) -> "PlacementConstraint":
        """Place tasks only on instances matching the given query expression.

        You can specify multiple expressions in one call. The tasks will only
        be placed on instances matching all expressions.

        Arguments:
            expressions: -

        See:
            https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cluster-query-language.html
        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "memberOf", [*expressions])

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List["CfnService.PlacementConstraintProperty"]:
        """Return the placement JSON.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJson", [])

    @property
    @jsii.member(jsii_name="json")
    def json(self) -> typing.List["CfnService.PlacementConstraintProperty"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "json")


class PlacementStrategy(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.PlacementStrategy"):
    """An ECS placement strategy.

    Tasks will preferentially be placed on instances that match these rules.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="packedBy")
    @classmethod
    def packed_by(cls, resource: "BinPackResource") -> "PlacementStrategy":
        """Try to place tasks on instances with the least amount of indicated resource available.

        This ensures the total consumption of this resource is lowest.

        Arguments:
            resource: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "packedBy", [resource])

    @jsii.member(jsii_name="packedByCpu")
    @classmethod
    def packed_by_cpu(cls) -> "PlacementStrategy":
        """Try to place tasks on instances with the least amount of CPU.

        This ensures the total consumption of CPU is lowest

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "packedByCpu", [])

    @jsii.member(jsii_name="packedByMemory")
    @classmethod
    def packed_by_memory(cls) -> "PlacementStrategy":
        """Try to place tasks on instances with the least amount of memory.

        This ensures the total consumption of memory is lowest

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "packedByMemory", [])

    @jsii.member(jsii_name="randomly")
    @classmethod
    def randomly(cls) -> "PlacementStrategy":
        """Place tasks randomly across the available instances.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "randomly", [])

    @jsii.member(jsii_name="spreadAcross")
    @classmethod
    def spread_across(cls, *fields: str) -> "PlacementStrategy":
        """Try to place tasks spread across instances based on given attributes.

        You can use one of the built-in attributes found on ``BuiltInAttributes``
        or supply your own custom instance attributes. If more than one attribute
        is supplied, spreading is done in order.

        Arguments:
            fields: -

        Default:
            attributes instanceId

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "spreadAcross", [*fields])

    @jsii.member(jsii_name="spreadAcrossInstances")
    @classmethod
    def spread_across_instances(cls) -> "PlacementStrategy":
        """Try to place tasks spread across instances.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "spreadAcrossInstances", [])

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List["CfnService.PlacementStrategyProperty"]:
        """Return the placement JSON.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toJson", [])

    @property
    @jsii.member(jsii_name="json")
    def json(self) -> typing.List["CfnService.PlacementStrategyProperty"]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "json")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _PortMapping(jsii.compat.TypedDict, total=False):
    hostPort: jsii.Number
    """Port on the host.

    In AwsVpc or Host networking mode, leave this out or set it to the
    same value as containerPort.

    In Bridge networking mode, leave this out or set it to non-reserved
    non-ephemeral port.

    Stability:
        experimental
    """
    protocol: "Protocol"
    """Protocol.

    Default:
        Tcp

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.PortMapping", jsii_struct_bases=[_PortMapping])
class PortMapping(_PortMapping):
    """Map a host port to a container port.

    Stability:
        experimental
    """
    containerPort: jsii.Number
    """Port inside the container.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ecs.Protocol")
class Protocol(enum.Enum):
    """Network protocol.

    Stability:
        experimental
    """
    Tcp = "Tcp"
    """TCP.

    Stability:
        experimental
    """
    Udp = "Udp"
    """UDP.

    Stability:
        experimental
    """

class RepositoryImage(ContainerImage, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.RepositoryImage"):
    """A container image hosted on DockerHub or another online registry.

    Stability:
        experimental
    """
    def __init__(self, image_name: str, *, credentials: typing.Optional[aws_cdk.aws_secretsmanager.ISecret]=None) -> None:
        """
        Arguments:
            imageName: -
            props: -
            credentials: Optional secret that houses credentials for the image registry.

        Stability:
            experimental
        """
        props: RepositoryImageProps = {}

        if credentials is not None:
            props["credentials"] = credentials

        jsii.create(RepositoryImage, self, [image_name, props])

    @jsii.member(jsii_name="bind")
    def bind(self, container_definition: "ContainerDefinition") -> None:
        """Called when the image is used by a ContainerDefinition.

        Arguments:
            containerDefinition: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [container_definition])

    @jsii.member(jsii_name="toRepositoryCredentialsJson")
    def to_repository_credentials_json(self) -> typing.Optional["CfnTaskDefinition.RepositoryCredentialsProperty"]:
        """Render the Repository credentials to the CloudFormation object.

        Stability:
            experimental
        """
        return jsii.invoke(self, "toRepositoryCredentialsJson", [])

    @property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> str:
        """Name of the image.

        Stability:
            experimental
        """
        return jsii.get(self, "imageName")


@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.RepositoryImageProps", jsii_struct_bases=[])
class RepositoryImageProps(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    credentials: aws_cdk.aws_secretsmanager.ISecret
    """Optional secret that houses credentials for the image registry.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.RequestCountScalingProps", jsii_struct_bases=[aws_cdk.aws_applicationautoscaling.BaseTargetTrackingProps])
class RequestCountScalingProps(aws_cdk.aws_applicationautoscaling.BaseTargetTrackingProps, jsii.compat.TypedDict):
    """Properties for enabling scaling based on ALB request counts.

    Stability:
        experimental
    """
    requestsPerTarget: jsii.Number
    """ALB requests per target.

    Stability:
        experimental
    """

    targetGroup: aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup
    """ALB Target Group.

    Stability:
        experimental
    """

class ScalableTaskCount(aws_cdk.aws_applicationautoscaling.BaseScalableAttribute, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.ScalableTaskCount"):
    """Scalable attribute representing task count.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, dimension: str, resource_id: str, role: aws_cdk.aws_iam.IRole, service_namespace: aws_cdk.aws_applicationautoscaling.ServiceNamespace, max_capacity: jsii.Number, min_capacity: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            dimension: Scalable dimension of the attribute.
            resourceId: Resource ID of the attribute.
            role: Role to use for scaling.
            serviceNamespace: Service namespace of the scalable attribute.
            maxCapacity: Maximum capacity to scale to.
            minCapacity: Minimum capacity to scale to. Default: 1

        Stability:
            experimental
        """
        props: ScalableTaskCountProps = {"dimension": dimension, "resourceId": resource_id, "role": role, "serviceNamespace": service_namespace, "maxCapacity": max_capacity}

        if min_capacity is not None:
            props["minCapacity"] = min_capacity

        jsii.create(ScalableTaskCount, self, [scope, id, props])

    @jsii.member(jsii_name="scaleOnCpuUtilization")
    def scale_on_cpu_utilization(self, id: str, *, target_utilization_percent: jsii.Number, disable_scale_in: typing.Optional[bool]=None, policy_name: typing.Optional[str]=None, scale_in_cooldown_sec: typing.Optional[jsii.Number]=None, scale_out_cooldown_sec: typing.Optional[jsii.Number]=None) -> None:
        """Scale out or in to achieve a target CPU utilization.

        Arguments:
            id: -
            props: -
            targetUtilizationPercent: Target average CPU utilization across the task.
            disableScaleIn: Indicates whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. Default: false
            policyName: A name for the scaling policy. Default: - Automatically generated name.
            scaleInCooldownSec: Period after a scale in activity completes before another scale in activity can start. Default: - No scale in cooldown.
            scaleOutCooldownSec: Period after a scale out activity completes before another scale out activity can start. Default: - No scale out cooldown.

        Stability:
            experimental
        """
        props: CpuUtilizationScalingProps = {"targetUtilizationPercent": target_utilization_percent}

        if disable_scale_in is not None:
            props["disableScaleIn"] = disable_scale_in

        if policy_name is not None:
            props["policyName"] = policy_name

        if scale_in_cooldown_sec is not None:
            props["scaleInCooldownSec"] = scale_in_cooldown_sec

        if scale_out_cooldown_sec is not None:
            props["scaleOutCooldownSec"] = scale_out_cooldown_sec

        return jsii.invoke(self, "scaleOnCpuUtilization", [id, props])

    @jsii.member(jsii_name="scaleOnMemoryUtilization")
    def scale_on_memory_utilization(self, id: str, *, target_utilization_percent: jsii.Number, disable_scale_in: typing.Optional[bool]=None, policy_name: typing.Optional[str]=None, scale_in_cooldown_sec: typing.Optional[jsii.Number]=None, scale_out_cooldown_sec: typing.Optional[jsii.Number]=None) -> None:
        """Scale out or in to achieve a target memory utilization.

        Arguments:
            id: -
            props: -
            targetUtilizationPercent: Target average memory utilization across the task.
            disableScaleIn: Indicates whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. Default: false
            policyName: A name for the scaling policy. Default: - Automatically generated name.
            scaleInCooldownSec: Period after a scale in activity completes before another scale in activity can start. Default: - No scale in cooldown.
            scaleOutCooldownSec: Period after a scale out activity completes before another scale out activity can start. Default: - No scale out cooldown.

        Stability:
            experimental
        """
        props: MemoryUtilizationScalingProps = {"targetUtilizationPercent": target_utilization_percent}

        if disable_scale_in is not None:
            props["disableScaleIn"] = disable_scale_in

        if policy_name is not None:
            props["policyName"] = policy_name

        if scale_in_cooldown_sec is not None:
            props["scaleInCooldownSec"] = scale_in_cooldown_sec

        if scale_out_cooldown_sec is not None:
            props["scaleOutCooldownSec"] = scale_out_cooldown_sec

        return jsii.invoke(self, "scaleOnMemoryUtilization", [id, props])

    @jsii.member(jsii_name="scaleOnMetric")
    def scale_on_metric(self, id: str, *, metric: aws_cdk.aws_cloudwatch.Metric, scaling_steps: typing.List[aws_cdk.aws_applicationautoscaling.ScalingInterval], adjustment_type: typing.Optional[aws_cdk.aws_applicationautoscaling.AdjustmentType]=None, cooldown_sec: typing.Optional[jsii.Number]=None, min_adjustment_magnitude: typing.Optional[jsii.Number]=None) -> None:
        """Scale out or in based on a metric value.

        Arguments:
            id: -
            props: -
            metric: Metric to scale on.
            scalingSteps: The intervals for scaling. Maps a range of metric values to a particular scaling behavior.
            adjustmentType: How the adjustment numbers inside 'intervals' are interpreted. Default: ChangeInCapacity
            cooldownSec: Grace period after scaling activity. Subsequent scale outs during the cooldown period are squashed so that only the biggest scale out happens. Subsequent scale ins during the cooldown period are ignored. Default: No cooldown period
            minAdjustmentMagnitude: Minimum absolute number to adjust capacity with as result of percentage scaling. Only when using AdjustmentType = PercentChangeInCapacity, this number controls the minimum absolute effect size. Default: No minimum scaling effect

        Stability:
            experimental
        """
        props: aws_cdk.aws_applicationautoscaling.BasicStepScalingPolicyProps = {"metric": metric, "scalingSteps": scaling_steps}

        if adjustment_type is not None:
            props["adjustmentType"] = adjustment_type

        if cooldown_sec is not None:
            props["cooldownSec"] = cooldown_sec

        if min_adjustment_magnitude is not None:
            props["minAdjustmentMagnitude"] = min_adjustment_magnitude

        return jsii.invoke(self, "scaleOnMetric", [id, props])

    @jsii.member(jsii_name="scaleOnRequestCount")
    def scale_on_request_count(self, id: str, *, requests_per_target: jsii.Number, target_group: aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup, disable_scale_in: typing.Optional[bool]=None, policy_name: typing.Optional[str]=None, scale_in_cooldown_sec: typing.Optional[jsii.Number]=None, scale_out_cooldown_sec: typing.Optional[jsii.Number]=None) -> None:
        """Scale out or in to achieve a target ALB request count per target.

        Arguments:
            id: -
            props: -
            requestsPerTarget: ALB requests per target.
            targetGroup: ALB Target Group.
            disableScaleIn: Indicates whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. Default: false
            policyName: A name for the scaling policy. Default: - Automatically generated name.
            scaleInCooldownSec: Period after a scale in activity completes before another scale in activity can start. Default: - No scale in cooldown.
            scaleOutCooldownSec: Period after a scale out activity completes before another scale out activity can start. Default: - No scale out cooldown.

        Stability:
            experimental
        """
        props: RequestCountScalingProps = {"requestsPerTarget": requests_per_target, "targetGroup": target_group}

        if disable_scale_in is not None:
            props["disableScaleIn"] = disable_scale_in

        if policy_name is not None:
            props["policyName"] = policy_name

        if scale_in_cooldown_sec is not None:
            props["scaleInCooldownSec"] = scale_in_cooldown_sec

        if scale_out_cooldown_sec is not None:
            props["scaleOutCooldownSec"] = scale_out_cooldown_sec

        return jsii.invoke(self, "scaleOnRequestCount", [id, props])

    @jsii.member(jsii_name="scaleOnSchedule")
    def scale_on_schedule(self, id: str, *, schedule: str, end_time: typing.Optional[datetime.datetime]=None, max_capacity: typing.Optional[jsii.Number]=None, min_capacity: typing.Optional[jsii.Number]=None, start_time: typing.Optional[datetime.datetime]=None) -> None:
        """Scale out or in based on time.

        Arguments:
            id: -
            props: -
            schedule: When to perform this action. Support formats: - at(yyyy-mm-ddThh:mm:ss) - rate(value unit) - cron(fields) "At" expressions are useful for one-time schedules. Specify the time in UTC. For "rate" expressions, value is a positive integer, and unit is minute, minutes, hour, hours, day, or days. For more information about cron expressions, see https://en.wikipedia.org/wiki/Cron.
            endTime: When this scheduled action expires. Default: The rule never expires.
            maxCapacity: The new maximum capacity. During the scheduled time, the current capacity is above the maximum capacity, Application Auto Scaling scales in to the maximum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new maximum capacity
            minCapacity: The new minimum capacity. During the scheduled time, if the current capacity is below the minimum capacity, Application Auto Scaling scales out to the minimum capacity. At least one of maxCapacity and minCapacity must be supplied. Default: No new minimum capacity
            startTime: When this scheduled action becomes active. Default: The rule is activate immediately

        Stability:
            experimental
        """
        props: aws_cdk.aws_applicationautoscaling.ScalingSchedule = {"schedule": schedule}

        if end_time is not None:
            props["endTime"] = end_time

        if max_capacity is not None:
            props["maxCapacity"] = max_capacity

        if min_capacity is not None:
            props["minCapacity"] = min_capacity

        if start_time is not None:
            props["startTime"] = start_time

        return jsii.invoke(self, "scaleOnSchedule", [id, props])

    @jsii.member(jsii_name="scaleToTrackCustomMetric")
    def scale_to_track_custom_metric(self, id: str, *, metric: aws_cdk.aws_cloudwatch.Metric, target_value: jsii.Number, disable_scale_in: typing.Optional[bool]=None, policy_name: typing.Optional[str]=None, scale_in_cooldown_sec: typing.Optional[jsii.Number]=None, scale_out_cooldown_sec: typing.Optional[jsii.Number]=None) -> None:
        """Scale out or in to track a custom metric.

        Arguments:
            id: -
            props: -
            metric: Metric to track. The metric must represent utilization; that is, you will always get the following behavior: - metric > targetValue => scale out - metric < targetValue => scale in
            targetValue: The target value to achieve for the metric.
            disableScaleIn: Indicates whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. Default: false
            policyName: A name for the scaling policy. Default: - Automatically generated name.
            scaleInCooldownSec: Period after a scale in activity completes before another scale in activity can start. Default: - No scale in cooldown.
            scaleOutCooldownSec: Period after a scale out activity completes before another scale out activity can start. Default: - No scale out cooldown.

        Stability:
            experimental
        """
        props: TrackCustomMetricProps = {"metric": metric, "targetValue": target_value}

        if disable_scale_in is not None:
            props["disableScaleIn"] = disable_scale_in

        if policy_name is not None:
            props["policyName"] = policy_name

        if scale_in_cooldown_sec is not None:
            props["scaleInCooldownSec"] = scale_in_cooldown_sec

        if scale_out_cooldown_sec is not None:
            props["scaleOutCooldownSec"] = scale_out_cooldown_sec

        return jsii.invoke(self, "scaleToTrackCustomMetric", [id, props])


@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.ScalableTaskCountProps", jsii_struct_bases=[aws_cdk.aws_applicationautoscaling.BaseScalableAttributeProps])
class ScalableTaskCountProps(aws_cdk.aws_applicationautoscaling.BaseScalableAttributeProps, jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    pass

@jsii.enum(jsii_type="@aws-cdk/aws-ecs.Scope")
class Scope(enum.Enum):
    """
    Stability:
        experimental
    """
    Task = "Task"
    """Docker volumes are automatically provisioned when the task starts and destroyed when the task stops.

    Stability:
        experimental
    """
    Shared = "Shared"
    """Docker volumes are persist after the task stops.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.ScratchSpace", jsii_struct_bases=[])
class ScratchSpace(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    containerPath: str
    """
    Stability:
        experimental
    """

    name: str
    """
    Stability:
        experimental
    """

    readOnly: bool
    """
    Stability:
        experimental
    """

    sourcePath: str
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.ServiceDiscoveryOptions", jsii_struct_bases=[])
class ServiceDiscoveryOptions(jsii.compat.TypedDict, total=False):
    """Options for enabling service discovery on an ECS service.

    Stability:
        experimental
    """
    dnsRecordType: aws_cdk.aws_servicediscovery.DnsRecordType
    """The DNS type of the record that you want AWS Cloud Map to create.

    Supported record types include A or SRV.

    Default:
        : A

    Stability:
        experimental
    """

    dnsTtlSec: jsii.Number
    """The amount of time, in seconds, that you want DNS resolvers to cache the settings for this record.

    Default:
        60

    Stability:
        experimental
    """

    failureThreshold: jsii.Number
    """The number of 30-second intervals that you want Cloud Map to wait after receiving an UpdateInstanceCustomHealthStatus request before it changes the health status of a service instance. NOTE: This is used for HealthCheckCustomConfig.

    Stability:
        experimental
    """

    name: str
    """Name of the cloudmap service to attach to the ECS Service.

    Default:
        CloudFormation-generated name

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _ServiceRegistry(jsii.compat.TypedDict, total=False):
    containerName: str
    """The container name value, already specified in the task definition, to be used for your service discovery service. If the task definition that your service task specifies uses the bridge or host network mode, you must specify a containerName and containerPort combination from the task definition. If the task definition that your service task specifies uses the awsvpc network mode and a type SRV DNS record is used, you must specify either a containerName and containerPort combination or a port value, but not both.

    Stability:
        experimental
    """
    containerPort: jsii.Number
    """The container port value, already specified in the task definition, to be used for your service discovery service. If the task definition that your service task specifies uses the bridge or host network mode, you must specify a containerName and containerPort combination from the task definition. If the task definition that your service task specifies uses the awsvpc network mode and a type SRV DNS record is used, you must specify either a containerName and containerPort combination or a port value, but not both.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.ServiceRegistry", jsii_struct_bases=[_ServiceRegistry])
class ServiceRegistry(_ServiceRegistry):
    """Service Registry for ECS service.

    Stability:
        experimental
    """
    arn: str
    """Arn of the Cloud Map Service that will register a Cloud Map Instance for your ECS Service.

    Stability:
        experimental
    """

@jsii.implements(ITaskDefinition)
class TaskDefinition(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.TaskDefinition"):
    """Base class for Ecs and Fargate task definitions.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, compatibility: "Compatibility", cpu: typing.Optional[str]=None, memory_mi_b: typing.Optional[str]=None, network_mode: typing.Optional["NetworkMode"]=None, placement_constraints: typing.Optional[typing.List["PlacementConstraint"]]=None, execution_role: typing.Optional[aws_cdk.aws_iam.IRole]=None, family: typing.Optional[str]=None, task_role: typing.Optional[aws_cdk.aws_iam.IRole]=None, volumes: typing.Optional[typing.List["Volume"]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            compatibility: What launch types this task definition should be compatible with.
            cpu: The number of cpu units used by the task. Optional for EC2 tasks and any value can be used. Required for Fargate tasks Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments Default: - CPU units are not specified.
            memoryMiB: The amount (in MiB) of memory used by the task. Optional for EC2 tasks and any value can be used. Required for Fargate tasks This field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 0.5GB, 1GB, 2GB - Available cpu values: 256 (.25 vCPU) 1GB, 2GB, 3GB, 4GB - Available cpu values: 512 (.5 vCPU) 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB - Available cpu values: 1024 (1 vCPU) Between 4GB and 16GB in 1GB increments - Available cpu values: 2048 (2 vCPU) Between 8GB and 30GB in 1GB increments - Available cpu values: 4096 (4 vCPU) Default: - Memory used by task is not specified.
            networkMode: The Docker networking mode to use for the containers in the task. On Fargate, the only supported networking mode is AwsVpc. Default: - NetworkMode.Bridge for EC2 tasks, AwsVpc for Fargate tasks.
            placementConstraints: An array of placement constraint objects to use for the task. You can specify a maximum of 10 constraints per task (this limit includes constraints in the task definition and those specified at run time). Not supported in Fargate. Default: - No placement constraints.
            executionRole: The IAM role assumed by the ECS agent. The role will be used to retrieve container images from ECR and create CloudWatch log groups. Default: - An execution role will be automatically created if you use ECR images in your task definition.
            family: Namespace for task definition versions. Default: - Automatically generated name.
            taskRole: The IAM role assumable by your application code running inside the container. Default: - A task role is automatically created for you.
            volumes: See: https://docs.aws.amazon.com/AmazonECS/latest/developerguide//task_definition_parameters.html#volumes. Default: - No volumes are passed to the Docker daemon on a container instance.

        Stability:
            experimental
        """
        props: TaskDefinitionProps = {"compatibility": compatibility}

        if cpu is not None:
            props["cpu"] = cpu

        if memory_mi_b is not None:
            props["memoryMiB"] = memory_mi_b

        if network_mode is not None:
            props["networkMode"] = network_mode

        if placement_constraints is not None:
            props["placementConstraints"] = placement_constraints

        if execution_role is not None:
            props["executionRole"] = execution_role

        if family is not None:
            props["family"] = family

        if task_role is not None:
            props["taskRole"] = task_role

        if volumes is not None:
            props["volumes"] = volumes

        jsii.create(TaskDefinition, self, [scope, id, props])

    @jsii.member(jsii_name="fromTaskDefinitionArn")
    @classmethod
    def from_task_definition_arn(cls, scope: aws_cdk.cdk.Construct, id: str, task_definition_arn: str) -> "ITaskDefinition":
        """Imports a task definition by ARN.

        The task will have a compatibility of EC2+Fargate.

        Arguments:
            scope: -
            id: -
            taskDefinitionArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromTaskDefinitionArn", [scope, id, task_definition_arn])

    @jsii.member(jsii_name="addContainer")
    def add_container(self, id: str, *, image: "ContainerImage", command: typing.Optional[typing.List[str]]=None, cpu: typing.Optional[jsii.Number]=None, disable_networking: typing.Optional[bool]=None, dns_search_domains: typing.Optional[typing.List[str]]=None, dns_servers: typing.Optional[typing.List[str]]=None, docker_labels: typing.Optional[typing.Mapping[str,str]]=None, docker_security_options: typing.Optional[typing.List[str]]=None, entry_point: typing.Optional[typing.List[str]]=None, environment: typing.Optional[typing.Mapping[str,str]]=None, essential: typing.Optional[bool]=None, extra_hosts: typing.Optional[typing.Mapping[str,str]]=None, health_check: typing.Optional["HealthCheck"]=None, hostname: typing.Optional[str]=None, linux_parameters: typing.Optional["LinuxParameters"]=None, logging: typing.Optional["LogDriver"]=None, memory_limit_mi_b: typing.Optional[jsii.Number]=None, memory_reservation_mi_b: typing.Optional[jsii.Number]=None, privileged: typing.Optional[bool]=None, readonly_root_filesystem: typing.Optional[bool]=None, user: typing.Optional[str]=None, working_directory: typing.Optional[str]=None) -> "ContainerDefinition":
        """Create a new container to this task definition.

        Arguments:
            id: -
            props: -
            image: The image to use for a container. You can use images in the Docker Hub registry or specify other repositories (repository-url/image:tag). TODO: Update these to specify using classes of IContainerImage
            command: The CMD value to pass to the container. If you provide a shell command as a single string, you have to quote command-line arguments. Default: - CMD value built into container image.
            cpu: The minimum number of CPU units to reserve for the container. Default: - No minimum CPU units reserved.
            disableNetworking: Indicates whether networking is disabled within the container. Default: false
            dnsSearchDomains: A list of DNS search domains that are provided to the container. Default: - No search domains.
            dnsServers: A list of DNS servers that Amazon ECS provides to the container. Default: - Default DNS servers.
            dockerLabels: A key-value map of labels for the container. Default: - No labels.
            dockerSecurityOptions: A list of custom labels for SELinux and AppArmor multi-level security systems. Default: - No security labels.
            entryPoint: The ENTRYPOINT value to pass to the container. Default: - Entry point configured in container.
            environment: The environment variables to pass to the container. Default: - No environment variables.
            essential: Indicates whether the task stops if this container fails. If you specify true and the container fails, all other containers in the task stop. If you specify false and the container fails, none of the other containers in the task is affected. You must have at least one essential container in a task. Default: true
            extraHosts: A list of hostnames and IP address mappings to append to the /etc/hosts file on the container. Default: - No extra hosts.
            healthCheck: Container health check. Default: - Health check configuration from container.
            hostname: The name that Docker uses for the container hostname. Default: - Automatic hostname.
            linuxParameters: Configures Linux Parameters. Default: - No Linux paramters.
            logging: Configures a custom log driver for the container. Default: - Containers use the same logging driver that the Docker daemon uses.
            memoryLimitMiB: The hard limit (in MiB) of memory to present to the container. If your container attempts to exceed the allocated memory, the container is terminated. At least one of memoryLimitMiB and memoryReservationMiB is required for non-Fargate services. Default: - No memory limit.
            memoryReservationMiB: The soft limit (in MiB) of memory to reserve for the container. When system memory is under contention, Docker attempts to keep the container memory within the limit. If the container requires more memory, it can consume up to the value specified by the Memory property or all of the available memory on the container instance—whichever comes first. At least one of memoryLimitMiB and memoryReservationMiB is required for non-Fargate services. Default: - No memory reserved.
            privileged: Indicates whether the container is given full access to the host container instance. Default: false
            readonlyRootFilesystem: Indicates whether the container's root file system is mounted as read only. Default: false
            user: The user name to use inside the container. Default: root
            workingDirectory: The working directory in the container to run commands in. Default: /

        Stability:
            experimental
        """
        props: ContainerDefinitionOptions = {"image": image}

        if command is not None:
            props["command"] = command

        if cpu is not None:
            props["cpu"] = cpu

        if disable_networking is not None:
            props["disableNetworking"] = disable_networking

        if dns_search_domains is not None:
            props["dnsSearchDomains"] = dns_search_domains

        if dns_servers is not None:
            props["dnsServers"] = dns_servers

        if docker_labels is not None:
            props["dockerLabels"] = docker_labels

        if docker_security_options is not None:
            props["dockerSecurityOptions"] = docker_security_options

        if entry_point is not None:
            props["entryPoint"] = entry_point

        if environment is not None:
            props["environment"] = environment

        if essential is not None:
            props["essential"] = essential

        if extra_hosts is not None:
            props["extraHosts"] = extra_hosts

        if health_check is not None:
            props["healthCheck"] = health_check

        if hostname is not None:
            props["hostname"] = hostname

        if linux_parameters is not None:
            props["linuxParameters"] = linux_parameters

        if logging is not None:
            props["logging"] = logging

        if memory_limit_mi_b is not None:
            props["memoryLimitMiB"] = memory_limit_mi_b

        if memory_reservation_mi_b is not None:
            props["memoryReservationMiB"] = memory_reservation_mi_b

        if privileged is not None:
            props["privileged"] = privileged

        if readonly_root_filesystem is not None:
            props["readonlyRootFilesystem"] = readonly_root_filesystem

        if user is not None:
            props["user"] = user

        if working_directory is not None:
            props["workingDirectory"] = working_directory

        return jsii.invoke(self, "addContainer", [id, props])

    @jsii.member(jsii_name="addExtension")
    def add_extension(self, extension: "ITaskDefinitionExtension") -> None:
        """Extend this TaskDefinition with the given extension.

        Extension can be used to apply a packaged modification to
        a task definition.

        Arguments:
            extension: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addExtension", [extension])

    @jsii.member(jsii_name="addPlacementConstraint")
    def add_placement_constraint(self, constraint: "PlacementConstraint") -> None:
        """Constrain where tasks can be placed.

        Arguments:
            constraint: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addPlacementConstraint", [constraint])

    @jsii.member(jsii_name="addToExecutionRolePolicy")
    def add_to_execution_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add a policy statement to the Execution Role.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToExecutionRolePolicy", [statement])

    @jsii.member(jsii_name="addToTaskRolePolicy")
    def add_to_task_role_policy(self, statement: aws_cdk.aws_iam.PolicyStatement) -> None:
        """Add a policy statement to the Task Role.

        Arguments:
            statement: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "addToTaskRolePolicy", [statement])

    @jsii.member(jsii_name="addVolume")
    def add_volume(self, *, name: str, docker_volume_configuration: typing.Optional["DockerVolumeConfiguration"]=None, host: typing.Optional["Host"]=None) -> None:
        """Add a volume to this task definition.

        Arguments:
            volume: -
            name: A name for the volume.
            dockerVolumeConfiguration: Specifies this configuration when using Docker volumes.
            host: Path on the host.

        Stability:
            experimental
        """
        volume: Volume = {"name": name}

        if docker_volume_configuration is not None:
            volume["dockerVolumeConfiguration"] = docker_volume_configuration

        if host is not None:
            volume["host"] = host

        return jsii.invoke(self, "addVolume", [volume])

    @jsii.member(jsii_name="obtainExecutionRole")
    def obtain_execution_role(self) -> aws_cdk.aws_iam.IRole:
        """Create the execution role if it doesn't exist.

        Stability:
            experimental
        """
        return jsii.invoke(self, "obtainExecutionRole", [])

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[str]:
        """Validate this task definition.

        Stability:
            experimental
        """
        return jsii.invoke(self, "validate", [])

    @property
    @jsii.member(jsii_name="compatibility")
    def compatibility(self) -> "Compatibility":
        """What launching modes this task is compatible with.

        Stability:
            experimental
        """
        return jsii.get(self, "compatibility")

    @property
    @jsii.member(jsii_name="containers")
    def _containers(self) -> typing.List["ContainerDefinition"]:
        """All containers.

        Stability:
            experimental
        """
        return jsii.get(self, "containers")

    @property
    @jsii.member(jsii_name="family")
    def family(self) -> str:
        """The family name of this task definition.

        Stability:
            experimental
        """
        return jsii.get(self, "family")

    @property
    @jsii.member(jsii_name="isEc2Compatible")
    def is_ec2_compatible(self) -> bool:
        """Return true if the task definition can be run on an EC2 cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "isEc2Compatible")

    @property
    @jsii.member(jsii_name="isFargateCompatible")
    def is_fargate_compatible(self) -> bool:
        """Return true if the task definition can be run on a Fargate cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "isFargateCompatible")

    @property
    @jsii.member(jsii_name="networkMode")
    def network_mode(self) -> "NetworkMode":
        """Network mode used by this task definition.

        Stability:
            experimental
        """
        return jsii.get(self, "networkMode")

    @property
    @jsii.member(jsii_name="taskDefinitionArn")
    def task_definition_arn(self) -> str:
        """ARN of this task definition.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "taskDefinitionArn")

    @property
    @jsii.member(jsii_name="taskRole")
    def task_role(self) -> aws_cdk.aws_iam.IRole:
        """Task role used by this task definition.

        Stability:
            experimental
        """
        return jsii.get(self, "taskRole")

    @property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """Execution role for this task definition.

        Stability:
            experimental
        """
        return jsii.get(self, "executionRole")

    @property
    @jsii.member(jsii_name="defaultContainer")
    def default_container(self) -> typing.Optional["ContainerDefinition"]:
        """Default container for this task.

        Load balancers will send traffic to this container. The first
        essential container that is added to this task will become the default
        container.

        Stability:
            experimental
        """
        return jsii.get(self, "defaultContainer")

    @default_container.setter
    def default_container(self, value: typing.Optional["ContainerDefinition"]):
        return jsii.set(self, "defaultContainer", value)


@jsii.implements(IEc2TaskDefinition)
class Ec2TaskDefinition(TaskDefinition, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.Ec2TaskDefinition"):
    """Define Tasks to run on an ECS cluster.

    Stability:
        experimental
    resource:
        AWS::ECS::TaskDefinition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, network_mode: typing.Optional["NetworkMode"]=None, placement_constraints: typing.Optional[typing.List["PlacementConstraint"]]=None, execution_role: typing.Optional[aws_cdk.aws_iam.IRole]=None, family: typing.Optional[str]=None, task_role: typing.Optional[aws_cdk.aws_iam.IRole]=None, volumes: typing.Optional[typing.List["Volume"]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            networkMode: The Docker networking mode to use for the containers in the task. On Fargate, the only supported networking mode is AwsVpc. Default: - NetworkMode.Bridge for EC2 tasks, AwsVpc for Fargate tasks.
            placementConstraints: An array of placement constraint objects to use for the task. You can specify a maximum of 10 constraints per task (this limit includes constraints in the task definition and those specified at run time). Not supported in Fargate. Default: - No placement constraints.
            executionRole: The IAM role assumed by the ECS agent. The role will be used to retrieve container images from ECR and create CloudWatch log groups. Default: - An execution role will be automatically created if you use ECR images in your task definition.
            family: Namespace for task definition versions. Default: - Automatically generated name.
            taskRole: The IAM role assumable by your application code running inside the container. Default: - A task role is automatically created for you.
            volumes: See: https://docs.aws.amazon.com/AmazonECS/latest/developerguide//task_definition_parameters.html#volumes. Default: - No volumes are passed to the Docker daemon on a container instance.

        Stability:
            experimental
        """
        props: Ec2TaskDefinitionProps = {}

        if network_mode is not None:
            props["networkMode"] = network_mode

        if placement_constraints is not None:
            props["placementConstraints"] = placement_constraints

        if execution_role is not None:
            props["executionRole"] = execution_role

        if family is not None:
            props["family"] = family

        if task_role is not None:
            props["taskRole"] = task_role

        if volumes is not None:
            props["volumes"] = volumes

        jsii.create(Ec2TaskDefinition, self, [scope, id, props])

    @jsii.member(jsii_name="fromEc2TaskDefinitionArn")
    @classmethod
    def from_ec2_task_definition_arn(cls, scope: aws_cdk.cdk.Construct, id: str, ec2_task_definition_arn: str) -> "IEc2TaskDefinition":
        """
        Arguments:
            scope: -
            id: -
            ec2TaskDefinitionArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromEc2TaskDefinitionArn", [scope, id, ec2_task_definition_arn])


@jsii.implements(IFargateTaskDefinition)
class FargateTaskDefinition(TaskDefinition, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-ecs.FargateTaskDefinition"):
    """A definition for Tasks on a Fargate cluster.

    Stability:
        experimental
    resource:
        AWS::ECS::TaskDefinition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cpu: typing.Optional[str]=None, memory_mi_b: typing.Optional[str]=None, execution_role: typing.Optional[aws_cdk.aws_iam.IRole]=None, family: typing.Optional[str]=None, task_role: typing.Optional[aws_cdk.aws_iam.IRole]=None, volumes: typing.Optional[typing.List["Volume"]]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            cpu: The number of cpu units used by the task. Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments. Default: 256
            memoryMiB: The amount (in MiB) of memory used by the task. This field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 0.5GB, 1GB, 2GB - Available cpu values: 256 (.25 vCPU) 1GB, 2GB, 3GB, 4GB - Available cpu values: 512 (.5 vCPU) 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB - Available cpu values: 1024 (1 vCPU) Between 4GB and 16GB in 1GB increments - Available cpu values: 2048 (2 vCPU) Between 8GB and 30GB in 1GB increments - Available cpu values: 4096 (4 vCPU) Default: 512
            executionRole: The IAM role assumed by the ECS agent. The role will be used to retrieve container images from ECR and create CloudWatch log groups. Default: - An execution role will be automatically created if you use ECR images in your task definition.
            family: Namespace for task definition versions. Default: - Automatically generated name.
            taskRole: The IAM role assumable by your application code running inside the container. Default: - A task role is automatically created for you.
            volumes: See: https://docs.aws.amazon.com/AmazonECS/latest/developerguide//task_definition_parameters.html#volumes. Default: - No volumes are passed to the Docker daemon on a container instance.

        Stability:
            experimental
        """
        props: FargateTaskDefinitionProps = {}

        if cpu is not None:
            props["cpu"] = cpu

        if memory_mi_b is not None:
            props["memoryMiB"] = memory_mi_b

        if execution_role is not None:
            props["executionRole"] = execution_role

        if family is not None:
            props["family"] = family

        if task_role is not None:
            props["taskRole"] = task_role

        if volumes is not None:
            props["volumes"] = volumes

        jsii.create(FargateTaskDefinition, self, [scope, id, props])

    @jsii.member(jsii_name="fromFargateTaskDefinitionArn")
    @classmethod
    def from_fargate_task_definition_arn(cls, scope: aws_cdk.cdk.Construct, id: str, fargate_task_definition_arn: str) -> "IFargateTaskDefinition":
        """
        Arguments:
            scope: -
            id: -
            fargateTaskDefinitionArn: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromFargateTaskDefinitionArn", [scope, id, fargate_task_definition_arn])

    @property
    @jsii.member(jsii_name="networkMode")
    def network_mode(self) -> "NetworkMode":
        """The configured network mode.

        Stability:
            experimental
        """
        return jsii.get(self, "networkMode")


@jsii.data_type_optionals(jsii_struct_bases=[CommonTaskDefinitionProps])
class _TaskDefinitionProps(CommonTaskDefinitionProps, jsii.compat.TypedDict, total=False):
    cpu: str
    """The number of cpu units used by the task.

    Optional for EC2 tasks and any value can be used.

    Required for Fargate tasks
    Valid values, which determines your range of valid values for the memory parameter:
    256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB
    512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB
    1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB
    2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments
    4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments

    Default:
        - CPU units are not specified.

    Stability:
        experimental
    """
    memoryMiB: str
    """The amount (in MiB) of memory used by the task.

    Optional for EC2 tasks and any value can be used.

    Required for Fargate tasks
    This field is required and you must use one of the following values, which determines your range of valid values
    for the cpu parameter:

    0.5GB, 1GB, 2GB - Available cpu values: 256 (.25 vCPU)

    1GB, 2GB, 3GB, 4GB - Available cpu values: 512 (.5 vCPU)

    2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB - Available cpu values: 1024 (1 vCPU)

    Between 4GB and 16GB in 1GB increments - Available cpu values: 2048 (2 vCPU)

    Between 8GB and 30GB in 1GB increments - Available cpu values: 4096 (4 vCPU)

    Default:
        - Memory used by task is not specified.

    Stability:
        experimental
    """
    networkMode: "NetworkMode"
    """The Docker networking mode to use for the containers in the task.

    On Fargate, the only supported networking mode is AwsVpc.

    Default:
        - NetworkMode.Bridge for EC2 tasks, AwsVpc for Fargate tasks.

    Stability:
        experimental
    """
    placementConstraints: typing.List["PlacementConstraint"]
    """An array of placement constraint objects to use for the task.

    You can
    specify a maximum of 10 constraints per task (this limit includes
    constraints in the task definition and those specified at run time).

    Not supported in Fargate.

    Default:
        - No placement constraints.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.TaskDefinitionProps", jsii_struct_bases=[_TaskDefinitionProps])
class TaskDefinitionProps(_TaskDefinitionProps):
    """Properties for generic task definitions.

    Stability:
        experimental
    """
    compatibility: "Compatibility"
    """What launch types this task definition should be compatible with.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _Tmpfs(jsii.compat.TypedDict, total=False):
    mountOptions: typing.List["TmpfsMountOption"]
    """Mount options.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.Tmpfs", jsii_struct_bases=[_Tmpfs])
class Tmpfs(_Tmpfs):
    """A tmpfs mount.

    Stability:
        experimental
    """
    containerPath: str
    """Path in the container to mount.

    Stability:
        experimental
    """

    size: jsii.Number
    """Size of the volume.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ecs.TmpfsMountOption")
class TmpfsMountOption(enum.Enum):
    """Options for a tmpfs mount.

    Stability:
        experimental
    """
    Defaults = "Defaults"
    """
    Stability:
        experimental
    """
    Ro = "Ro"
    """
    Stability:
        experimental
    """
    Rw = "Rw"
    """
    Stability:
        experimental
    """
    Suid = "Suid"
    """
    Stability:
        experimental
    """
    Nosuid = "Nosuid"
    """
    Stability:
        experimental
    """
    Dev = "Dev"
    """
    Stability:
        experimental
    """
    Nodev = "Nodev"
    """
    Stability:
        experimental
    """
    Exec = "Exec"
    """
    Stability:
        experimental
    """
    Noexec = "Noexec"
    """
    Stability:
        experimental
    """
    Sync = "Sync"
    """
    Stability:
        experimental
    """
    Async = "Async"
    """
    Stability:
        experimental
    """
    Dirsync = "Dirsync"
    """
    Stability:
        experimental
    """
    Remount = "Remount"
    """
    Stability:
        experimental
    """
    Mand = "Mand"
    """
    Stability:
        experimental
    """
    Nomand = "Nomand"
    """
    Stability:
        experimental
    """
    Atime = "Atime"
    """
    Stability:
        experimental
    """
    Noatime = "Noatime"
    """
    Stability:
        experimental
    """
    Diratime = "Diratime"
    """
    Stability:
        experimental
    """
    Nodiratime = "Nodiratime"
    """
    Stability:
        experimental
    """
    Bind = "Bind"
    """
    Stability:
        experimental
    """
    Rbind = "Rbind"
    """
    Stability:
        experimental
    """
    Unbindable = "Unbindable"
    """
    Stability:
        experimental
    """
    Runbindable = "Runbindable"
    """
    Stability:
        experimental
    """
    Private = "Private"
    """
    Stability:
        experimental
    """
    Rprivate = "Rprivate"
    """
    Stability:
        experimental
    """
    Shared = "Shared"
    """
    Stability:
        experimental
    """
    Rshared = "Rshared"
    """
    Stability:
        experimental
    """
    Slave = "Slave"
    """
    Stability:
        experimental
    """
    Rslave = "Rslave"
    """
    Stability:
        experimental
    """
    Relatime = "Relatime"
    """
    Stability:
        experimental
    """
    Norelatime = "Norelatime"
    """
    Stability:
        experimental
    """
    Strictatime = "Strictatime"
    """
    Stability:
        experimental
    """
    Nostrictatime = "Nostrictatime"
    """
    Stability:
        experimental
    """
    Mode = "Mode"
    """
    Stability:
        experimental
    """
    Uid = "Uid"
    """
    Stability:
        experimental
    """
    Gid = "Gid"
    """
    Stability:
        experimental
    """
    NrInodes = "NrInodes"
    """
    Stability:
        experimental
    """
    NrBlocks = "NrBlocks"
    """
    Stability:
        experimental
    """
    Mpol = "Mpol"
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.TrackCustomMetricProps", jsii_struct_bases=[aws_cdk.aws_applicationautoscaling.BaseTargetTrackingProps])
class TrackCustomMetricProps(aws_cdk.aws_applicationautoscaling.BaseTargetTrackingProps, jsii.compat.TypedDict):
    """Properties to target track a custom metric.

    Stability:
        experimental
    """
    metric: aws_cdk.aws_cloudwatch.Metric
    """Metric to track.

    The metric must represent utilization; that is, you will always get the following behavior:

    - metric > targetValue => scale out
    - metric < targetValue => scale in

    Stability:
        experimental
    """

    targetValue: jsii.Number
    """The target value to achieve for the metric.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.Ulimit", jsii_struct_bases=[])
class Ulimit(jsii.compat.TypedDict):
    """Container ulimits.

    Correspond to ulimits options on docker run.

    NOTE: Does not work for Windows containers.

    Stability:
        experimental
    """
    hardLimit: jsii.Number
    """Hard limit of the resource.

    Stability:
        experimental
    """

    name: "UlimitName"
    """What resource to enforce a limit on.

    Stability:
        experimental
    """

    softLimit: jsii.Number
    """Soft limit of the resource.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-ecs.UlimitName")
class UlimitName(enum.Enum):
    """Type of resource to set a limit on.

    Stability:
        experimental
    """
    Core = "Core"
    """
    Stability:
        experimental
    """
    Cpu = "Cpu"
    """
    Stability:
        experimental
    """
    Data = "Data"
    """
    Stability:
        experimental
    """
    Fsize = "Fsize"
    """
    Stability:
        experimental
    """
    Locks = "Locks"
    """
    Stability:
        experimental
    """
    Memlock = "Memlock"
    """
    Stability:
        experimental
    """
    Msgqueue = "Msgqueue"
    """
    Stability:
        experimental
    """
    Nice = "Nice"
    """
    Stability:
        experimental
    """
    Nofile = "Nofile"
    """
    Stability:
        experimental
    """
    Nproc = "Nproc"
    """
    Stability:
        experimental
    """
    Rss = "Rss"
    """
    Stability:
        experimental
    """
    Rtprio = "Rtprio"
    """
    Stability:
        experimental
    """
    Rttime = "Rttime"
    """
    Stability:
        experimental
    """
    Sigpending = "Sigpending"
    """
    Stability:
        experimental
    """
    Stack = "Stack"
    """
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _Volume(jsii.compat.TypedDict, total=False):
    dockerVolumeConfiguration: "DockerVolumeConfiguration"
    """Specifies this configuration when using Docker volumes.

    Stability:
        experimental
    """
    host: "Host"
    """Path on the host.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.Volume", jsii_struct_bases=[_Volume])
class Volume(_Volume):
    """Volume definition.

    Stability:
        experimental
    """
    name: str
    """A name for the volume.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-ecs.VolumeFrom", jsii_struct_bases=[])
class VolumeFrom(jsii.compat.TypedDict):
    """A volume from another container.

    Stability:
        experimental
    """
    readOnly: bool
    """Whether the volume is read only.

    Stability:
        experimental
    """

    sourceContainer: str
    """Name of the source container.

    Stability:
        experimental
    """

__all__ = ["AddAutoScalingGroupCapacityOptions", "AddCapacityOptions", "AmiHardwareType", "AssetImage", "AssetImageProps", "AwsLogDriver", "AwsLogDriverProps", "BaseService", "BaseServiceProps", "BinPackResource", "BuiltInAttributes", "Capability", "CfnCluster", "CfnClusterProps", "CfnService", "CfnServiceProps", "CfnTaskDefinition", "CfnTaskDefinitionProps", "Cluster", "ClusterAttributes", "ClusterProps", "CommonTaskDefinitionProps", "Compatibility", "ContainerDefinition", "ContainerDefinitionOptions", "ContainerDefinitionProps", "ContainerImage", "CpuUtilizationScalingProps", "Device", "DevicePermission", "DockerVolumeConfiguration", "Ec2Service", "Ec2ServiceProps", "Ec2TaskDefinition", "Ec2TaskDefinitionProps", "EcrImage", "EcsOptimizedAmi", "EcsOptimizedAmiProps", "FargatePlatformVersion", "FargateService", "FargateServiceProps", "FargateTaskDefinition", "FargateTaskDefinitionProps", "HealthCheck", "Host", "ICluster", "IEc2Service", "IEc2TaskDefinition", "IFargateService", "IFargateTaskDefinition", "IService", "ITaskDefinition", "ITaskDefinitionExtension", "LinuxParameters", "LinuxParametersProps", "LogDriver", "MemoryUtilizationScalingProps", "MountPoint", "NamespaceOptions", "NamespaceType", "NetworkMode", "PlacementConstraint", "PlacementStrategy", "PortMapping", "Protocol", "RepositoryImage", "RepositoryImageProps", "RequestCountScalingProps", "ScalableTaskCount", "ScalableTaskCountProps", "Scope", "ScratchSpace", "ServiceDiscoveryOptions", "ServiceRegistry", "TaskDefinition", "TaskDefinitionProps", "Tmpfs", "TmpfsMountOption", "TrackCustomMetricProps", "Ulimit", "UlimitName", "Volume", "VolumeFrom", "__jsii_assembly__"]

publication.publish()
