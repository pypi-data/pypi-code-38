import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_cloudwatch
import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_sns
import aws_cdk.aws_sqs
import aws_cdk.aws_stepfunctions
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-stepfunctions-tasks", "0.34.0", __name__, "aws-stepfunctions-tasks@0.34.0.jsii.tgz")
@jsii.data_type_optionals(jsii_struct_bases=[])
class _CommonEcsRunTaskProps(jsii.compat.TypedDict, total=False):
    containerOverrides: typing.List["ContainerOverride"]
    """Container setting overrides.

    Key is the name of the container to override, value is the
    values you want to override.

    Stability:
        experimental
    """
    synchronous: bool
    """Whether to wait for the task to complete and return the response.

    Default:
        true

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.CommonEcsRunTaskProps", jsii_struct_bases=[_CommonEcsRunTaskProps])
class CommonEcsRunTaskProps(_CommonEcsRunTaskProps):
    """Basic properties for ECS Tasks.

    Stability:
        experimental
    """
    cluster: aws_cdk.aws_ecs.ICluster
    """The topic to run the task on.

    Stability:
        experimental
    """

    taskDefinition: aws_cdk.aws_ecs.TaskDefinition
    """Task Definition used for running tasks in the service.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _ContainerOverride(jsii.compat.TypedDict, total=False):
    command: typing.List[str]
    """Command to run inside the container.

    Default:
        Default command

    Stability:
        experimental
    """
    cpu: jsii.Number
    """The number of cpu units reserved for the container.

    Stability:
        experimental
    Default:
        The default value from the task definition.
    """
    environment: typing.List["TaskEnvironmentVariable"]
    """Variables to set in the container's environment.

    Stability:
        experimental
    """
    memoryLimit: jsii.Number
    """Hard memory limit on the container.

    Stability:
        experimental
    Default:
        The default value from the task definition.
    """
    memoryReservation: jsii.Number
    """Soft memory limit on the container.

    Stability:
        experimental
    Default:
        The default value from the task definition.
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.ContainerOverride", jsii_struct_bases=[_ContainerOverride])
class ContainerOverride(_ContainerOverride):
    """
    Stability:
        experimental
    """
    containerName: str
    """Name of the container inside the task definition.

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_ec2.IConnectable, aws_cdk.aws_stepfunctions.IStepFunctionsTask)
class EcsRunTaskBase(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions-tasks.EcsRunTaskBase"):
    """A StepFunctions Task to run a Task on ECS or Fargate.

    Stability:
        experimental
    """
    def __init__(self, *, parameters: typing.Optional[typing.Mapping[str,typing.Any]]=None, cluster: aws_cdk.aws_ecs.ICluster, task_definition: aws_cdk.aws_ecs.TaskDefinition, container_overrides: typing.Optional[typing.List["ContainerOverride"]]=None, synchronous: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            props: -
            parameters: Additional parameters to pass to the base task.
            cluster: The topic to run the task on.
            taskDefinition: Task Definition used for running tasks in the service.
            containerOverrides: Container setting overrides. Key is the name of the container to override, value is the values you want to override.
            synchronous: Whether to wait for the task to complete and return the response. Default: true

        Stability:
            experimental
        """
        props: EcsRunTaskBaseProps = {"cluster": cluster, "taskDefinition": task_definition}

        if parameters is not None:
            props["parameters"] = parameters

        if container_overrides is not None:
            props["containerOverrides"] = container_overrides

        if synchronous is not None:
            props["synchronous"] = synchronous

        jsii.create(EcsRunTaskBase, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(self, task: aws_cdk.aws_stepfunctions.Task) -> aws_cdk.aws_stepfunctions.StepFunctionsTaskConfig:
        """Called when the task object is used in a workflow.

        Arguments:
            task: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [task])

    @jsii.member(jsii_name="configureAwsVpcNetworking")
    def _configure_aws_vpc_networking(self, vpc: aws_cdk.aws_ec2.IVpc, assign_public_ip: typing.Optional[bool]=None, subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None, security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]=None) -> None:
        """
        Arguments:
            vpc: -
            assignPublicIp: -
            subnetSelection: -
            securityGroup: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "configureAwsVpcNetworking", [vpc, assign_public_ip, subnet_selection, security_group])

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """Manage allowed network traffic for this service.

        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "EcsRunTaskBaseProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")


@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.EcsRunTaskBaseProps", jsii_struct_bases=[CommonEcsRunTaskProps])
class EcsRunTaskBaseProps(CommonEcsRunTaskProps, jsii.compat.TypedDict, total=False):
    """Construction properties for the BaseRunTaskProps.

    Stability:
        experimental
    """
    parameters: typing.Mapping[str,typing.Any]
    """Additional parameters to pass to the base task.

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_stepfunctions.IStepFunctionsTask)
class InvokeActivity(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions-tasks.InvokeActivity"):
    """A StepFunctions Task to invoke a Lambda function.

    A Function can be used directly as a Resource, but this class mirrors
    integration with other AWS services via a specific class instance.

    Stability:
        experimental
    """
    def __init__(self, activity: aws_cdk.aws_stepfunctions.IActivity, *, heartbeat_seconds: typing.Optional[jsii.Number]=None) -> None:
        """
        Arguments:
            activity: -
            props: -
            heartbeatSeconds: Maximum time between heart beats. If the time between heart beats takes longer than this, a 'Timeout' error is raised. Default: No heart beat timeout

        Stability:
            experimental
        """
        props: InvokeActivityProps = {}

        if heartbeat_seconds is not None:
            props["heartbeatSeconds"] = heartbeat_seconds

        jsii.create(InvokeActivity, self, [activity, props])

    @jsii.member(jsii_name="bind")
    def bind(self, _task: aws_cdk.aws_stepfunctions.Task) -> aws_cdk.aws_stepfunctions.StepFunctionsTaskConfig:
        """Called when the task object is used in a workflow.

        Arguments:
            _task: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_task])

    @property
    @jsii.member(jsii_name="activity")
    def activity(self) -> aws_cdk.aws_stepfunctions.IActivity:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "activity")

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "InvokeActivityProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")


@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.InvokeActivityProps", jsii_struct_bases=[])
class InvokeActivityProps(jsii.compat.TypedDict, total=False):
    """Properties for FunctionTask.

    Stability:
        experimental
    """
    heartbeatSeconds: jsii.Number
    """Maximum time between heart beats.

    If the time between heart beats takes longer than this, a 'Timeout' error is raised.

    Default:
        No heart beat timeout

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_stepfunctions.IStepFunctionsTask)
class InvokeFunction(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions-tasks.InvokeFunction"):
    """A StepFunctions Task to invoke a Lambda function.

    A Function can be used directly as a Resource, but this class mirrors
    integration with other AWS services via a specific class instance.

    Stability:
        experimental
    """
    def __init__(self, lambda_function: aws_cdk.aws_lambda.IFunction) -> None:
        """
        Arguments:
            lambdaFunction: -

        Stability:
            experimental
        """
        jsii.create(InvokeFunction, self, [lambda_function])

    @jsii.member(jsii_name="bind")
    def bind(self, _task: aws_cdk.aws_stepfunctions.Task) -> aws_cdk.aws_stepfunctions.StepFunctionsTaskConfig:
        """Called when the task object is used in a workflow.

        Arguments:
            _task: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_task])

    @property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.IFunction:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "lambdaFunction")


@jsii.implements(aws_cdk.aws_stepfunctions.IStepFunctionsTask)
class PublishToTopic(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions-tasks.PublishToTopic"):
    """A StepFunctions Task to invoke a Lambda function.

    A Function can be used directly as a Resource, but this class mirrors
    integration with other AWS services via a specific class instance.

    Stability:
        experimental
    """
    def __init__(self, topic: aws_cdk.aws_sns.ITopic, *, message: aws_cdk.aws_stepfunctions.TaskInput, message_per_subscription_type: typing.Optional[bool]=None, subject: typing.Optional[str]=None) -> None:
        """
        Arguments:
            topic: -
            props: -
            message: The text message to send to the topic.
            messagePerSubscriptionType: If true, send a different message to every subscription type. If this is set to true, message must be a JSON object with a "default" key and a key for every subscription type (such as "sqs", "email", etc.) The values are strings representing the messages being sent to every subscription type.
            subject: Message subject.

        Stability:
            experimental
        """
        props: PublishToTopicProps = {"message": message}

        if message_per_subscription_type is not None:
            props["messagePerSubscriptionType"] = message_per_subscription_type

        if subject is not None:
            props["subject"] = subject

        jsii.create(PublishToTopic, self, [topic, props])

    @jsii.member(jsii_name="bind")
    def bind(self, _task: aws_cdk.aws_stepfunctions.Task) -> aws_cdk.aws_stepfunctions.StepFunctionsTaskConfig:
        """Called when the task object is used in a workflow.

        Arguments:
            _task: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_task])

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "PublishToTopicProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")

    @property
    @jsii.member(jsii_name="topic")
    def topic(self) -> aws_cdk.aws_sns.ITopic:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "topic")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _PublishToTopicProps(jsii.compat.TypedDict, total=False):
    messagePerSubscriptionType: bool
    """If true, send a different message to every subscription type.

    If this is set to true, message must be a JSON object with a
    "default" key and a key for every subscription type (such as "sqs",
    "email", etc.) The values are strings representing the messages
    being sent to every subscription type.

    See:
        https://docs.aws.amazon.com/sns/latest/api/API_Publish.html#API_Publish_RequestParameters
    Stability:
        experimental
    """
    subject: str
    """Message subject.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.PublishToTopicProps", jsii_struct_bases=[_PublishToTopicProps])
class PublishToTopicProps(_PublishToTopicProps):
    """Properties for PublishTask.

    Stability:
        experimental
    """
    message: aws_cdk.aws_stepfunctions.TaskInput
    """The text message to send to the topic.

    Stability:
        experimental
    """

class RunEcsEc2Task(EcsRunTaskBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions-tasks.RunEcsEc2Task"):
    """Run an ECS/EC2 Task in a StepFunctions workflow.

    Stability:
        experimental
    """
    def __init__(self, *, placement_constraints: typing.Optional[typing.List[aws_cdk.aws_ecs.PlacementConstraint]]=None, placement_strategies: typing.Optional[typing.List[aws_cdk.aws_ecs.PlacementStrategy]]=None, security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]=None, subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None, cluster: aws_cdk.aws_ecs.ICluster, task_definition: aws_cdk.aws_ecs.TaskDefinition, container_overrides: typing.Optional[typing.List["ContainerOverride"]]=None, synchronous: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            props: -
            placementConstraints: Placement constraints. Default: No constraints
            placementStrategies: Placement strategies. Default: No strategies
            securityGroup: Existing security group to use for the task's ENIs. (Only applicable in case the TaskDefinition is configured for AwsVpc networking) Default: A new security group is created
            subnets: In what subnets to place the task's ENIs. (Only applicable in case the TaskDefinition is configured for AwsVpc networking) Default: Private subnets
            cluster: The topic to run the task on.
            taskDefinition: Task Definition used for running tasks in the service.
            containerOverrides: Container setting overrides. Key is the name of the container to override, value is the values you want to override.
            synchronous: Whether to wait for the task to complete and return the response. Default: true

        Stability:
            experimental
        """
        props: RunEcsEc2TaskProps = {"cluster": cluster, "taskDefinition": task_definition}

        if placement_constraints is not None:
            props["placementConstraints"] = placement_constraints

        if placement_strategies is not None:
            props["placementStrategies"] = placement_strategies

        if security_group is not None:
            props["securityGroup"] = security_group

        if subnets is not None:
            props["subnets"] = subnets

        if container_overrides is not None:
            props["containerOverrides"] = container_overrides

        if synchronous is not None:
            props["synchronous"] = synchronous

        jsii.create(RunEcsEc2Task, self, [props])


@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.RunEcsEc2TaskProps", jsii_struct_bases=[CommonEcsRunTaskProps])
class RunEcsEc2TaskProps(CommonEcsRunTaskProps, jsii.compat.TypedDict, total=False):
    """Properties to run an ECS task on EC2 in StepFunctionsan ECS.

    Stability:
        experimental
    """
    placementConstraints: typing.List[aws_cdk.aws_ecs.PlacementConstraint]
    """Placement constraints.

    Default:
        No constraints

    Stability:
        experimental
    """

    placementStrategies: typing.List[aws_cdk.aws_ecs.PlacementStrategy]
    """Placement strategies.

    Default:
        No strategies

    Stability:
        experimental
    """

    securityGroup: aws_cdk.aws_ec2.ISecurityGroup
    """Existing security group to use for the task's ENIs.

    (Only applicable in case the TaskDefinition is configured for AwsVpc networking)

    Default:
        A new security group is created

    Stability:
        experimental
    """

    subnets: aws_cdk.aws_ec2.SubnetSelection
    """In what subnets to place the task's ENIs.

    (Only applicable in case the TaskDefinition is configured for AwsVpc networking)

    Default:
        Private subnets

    Stability:
        experimental
    """

class RunEcsFargateTask(EcsRunTaskBase, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions-tasks.RunEcsFargateTask"):
    """Start a service on an ECS cluster.

    Stability:
        experimental
    """
    def __init__(self, *, assign_public_ip: typing.Optional[bool]=None, platform_version: typing.Optional[aws_cdk.aws_ecs.FargatePlatformVersion]=None, security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]=None, subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None, cluster: aws_cdk.aws_ecs.ICluster, task_definition: aws_cdk.aws_ecs.TaskDefinition, container_overrides: typing.Optional[typing.List["ContainerOverride"]]=None, synchronous: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            props: -
            assignPublicIp: Assign public IP addresses to each task. Default: false
            platformVersion: Fargate platform version to run this service on. Unless you have specific compatibility requirements, you don't need to specify this. Default: Latest
            securityGroup: Existing security group to use for the tasks. Default: A new security group is created
            subnets: In what subnets to place the task's ENIs. Default: Private subnet if assignPublicIp, public subnets otherwise
            cluster: The topic to run the task on.
            taskDefinition: Task Definition used for running tasks in the service.
            containerOverrides: Container setting overrides. Key is the name of the container to override, value is the values you want to override.
            synchronous: Whether to wait for the task to complete and return the response. Default: true

        Stability:
            experimental
        """
        props: RunEcsFargateTaskProps = {"cluster": cluster, "taskDefinition": task_definition}

        if assign_public_ip is not None:
            props["assignPublicIp"] = assign_public_ip

        if platform_version is not None:
            props["platformVersion"] = platform_version

        if security_group is not None:
            props["securityGroup"] = security_group

        if subnets is not None:
            props["subnets"] = subnets

        if container_overrides is not None:
            props["containerOverrides"] = container_overrides

        if synchronous is not None:
            props["synchronous"] = synchronous

        jsii.create(RunEcsFargateTask, self, [props])


@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.RunEcsFargateTaskProps", jsii_struct_bases=[CommonEcsRunTaskProps])
class RunEcsFargateTaskProps(CommonEcsRunTaskProps, jsii.compat.TypedDict, total=False):
    """Properties to define an ECS service.

    Stability:
        experimental
    """
    assignPublicIp: bool
    """Assign public IP addresses to each task.

    Default:
        false

    Stability:
        experimental
    """

    platformVersion: aws_cdk.aws_ecs.FargatePlatformVersion
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
        A new security group is created

    Stability:
        experimental
    """

    subnets: aws_cdk.aws_ec2.SubnetSelection
    """In what subnets to place the task's ENIs.

    Default:
        Private subnet if assignPublicIp, public subnets otherwise

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_stepfunctions.IStepFunctionsTask)
class SendToQueue(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions-tasks.SendToQueue"):
    """A StepFunctions Task to invoke a Lambda function.

    A Function can be used directly as a Resource, but this class mirrors
    integration with other AWS services via a specific class instance.

    Stability:
        experimental
    """
    def __init__(self, queue: aws_cdk.aws_sqs.IQueue, *, message_body: aws_cdk.aws_stepfunctions.TaskInput, delay_seconds: typing.Optional[jsii.Number]=None, message_deduplication_id: typing.Optional[str]=None, message_group_id: typing.Optional[str]=None) -> None:
        """
        Arguments:
            queue: -
            props: -
            messageBody: The text message to send to the queue.
            delaySeconds: The length of time, in seconds, for which to delay a specific message. Valid values are 0-900 seconds. Default: Default value of the queue is used
            messageDeduplicationId: The token used for deduplication of sent messages. Default: Use content-based deduplication
            messageGroupId: The tag that specifies that a message belongs to a specific message group. Required for FIFO queues. FIFO ordering applies to messages in the same message group. Default: No group ID

        Stability:
            experimental
        """
        props: SendToQueueProps = {"messageBody": message_body}

        if delay_seconds is not None:
            props["delaySeconds"] = delay_seconds

        if message_deduplication_id is not None:
            props["messageDeduplicationId"] = message_deduplication_id

        if message_group_id is not None:
            props["messageGroupId"] = message_group_id

        jsii.create(SendToQueue, self, [queue, props])

    @jsii.member(jsii_name="bind")
    def bind(self, _task: aws_cdk.aws_stepfunctions.Task) -> aws_cdk.aws_stepfunctions.StepFunctionsTaskConfig:
        """Called when the task object is used in a workflow.

        Arguments:
            _task: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_task])

    @property
    @jsii.member(jsii_name="props")
    def props(self) -> "SendToQueueProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "props")

    @property
    @jsii.member(jsii_name="queue")
    def queue(self) -> aws_cdk.aws_sqs.IQueue:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "queue")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _SendToQueueProps(jsii.compat.TypedDict, total=False):
    delaySeconds: jsii.Number
    """The length of time, in seconds, for which to delay a specific message.

    Valid values are 0-900 seconds.

    Default:
        Default value of the queue is used

    Stability:
        experimental
    """
    messageDeduplicationId: str
    """The token used for deduplication of sent messages.

    Default:
        Use content-based deduplication

    Stability:
        experimental
    """
    messageGroupId: str
    """The tag that specifies that a message belongs to a specific message group.

    Required for FIFO queues. FIFO ordering applies to messages in the same message
    group.

    Default:
        No group ID

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.SendToQueueProps", jsii_struct_bases=[_SendToQueueProps])
class SendToQueueProps(_SendToQueueProps):
    """Properties for SendMessageTask.

    Stability:
        experimental
    """
    messageBody: aws_cdk.aws_stepfunctions.TaskInput
    """The text message to send to the queue.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.TaskEnvironmentVariable", jsii_struct_bases=[])
class TaskEnvironmentVariable(jsii.compat.TypedDict):
    """An environment variable to be set in the container run as a task.

    Stability:
        experimental
    """
    name: str
    """Name for the environment variable.

    Exactly one of ``name`` and ``namePath`` must be specified.

    Stability:
        experimental
    """

    value: str
    """Value of the environment variable.

    Exactly one of ``value`` and ``valuePath`` must be specified.

    Stability:
        experimental
    """

__all__ = ["CommonEcsRunTaskProps", "ContainerOverride", "EcsRunTaskBase", "EcsRunTaskBaseProps", "InvokeActivity", "InvokeActivityProps", "InvokeFunction", "PublishToTopic", "PublishToTopicProps", "RunEcsEc2Task", "RunEcsEc2TaskProps", "RunEcsFargateTask", "RunEcsFargateTaskProps", "SendToQueue", "SendToQueueProps", "TaskEnvironmentVariable", "__jsii_assembly__"]

publication.publish()
