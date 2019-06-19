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
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_sns
import aws_cdk.aws_sqs
import aws_cdk.aws_stepfunctions
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-stepfunctions-tasks", "0.35.0", __name__, "aws-stepfunctions-tasks@0.35.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.AlgorithmSpecification", jsii_struct_bases=[])
class AlgorithmSpecification(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    algorithmName: str
    """Name of the algorithm resource to use for the training job.

    Stability:
        experimental
    """

    metricDefinitions: typing.List["MetricDefinition"]
    """List of metric definition objects.

    Each object specifies the metric name and regular expressions used to parse algorithm logs.

    Stability:
        experimental
    """

    trainingImage: str
    """Registry path of the Docker image that contains the training algorithm.

    Stability:
        experimental
    """

    trainingInputMode: "InputMode"
    """Input mode that the algorithm supports.

    Default:
        is 'File' mode

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions-tasks.AssembleWith")
class AssembleWith(enum.Enum):
    """How to assemble the results of the transform job as a single S3 object.

    Stability:
        experimental
    """
    None_ = "None"
    """Concatenate the results in binary format.

    Stability:
        experimental
    """
    Line = "Line"
    """Add a newline character at the end of every transformed record.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions-tasks.BatchStrategy")
class BatchStrategy(enum.Enum):
    """Specifies the number of records to include in a mini-batch for an HTTP inference request.

    Stability:
        experimental
    """
    MultiRecord = "MultiRecord"
    """Fits multiple records in a mini-batch.

    Stability:
        experimental
    """
    SingleRecord = "SingleRecord"
    """Use a single record when making an invocation request.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _Channel(jsii.compat.TypedDict, total=False):
    compressionType: "CompressionType"
    """Compression type if training data is compressed.

    Stability:
        experimental
    """
    contentType: str
    """Content type.

    Stability:
        experimental
    """
    inputMode: "InputMode"
    """Input mode to use for the data channel in a training job.

    Stability:
        experimental
    """
    recordWrapperType: "RecordWrapperType"
    """Record wrapper type.

    Stability:
        experimental
    """
    shuffleConfig: "ShuffleConfig"
    """Shuffle config option for input data in a channel.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.Channel", jsii_struct_bases=[_Channel])
class Channel(_Channel):
    """Describes the training, validation or test dataset and the Amazon S3 location where it is stored.

    Stability:
        experimental
    """
    channelName: str
    """Name of the channel.

    Stability:
        experimental
    """

    dataSource: "DataSource"
    """Location of the data channel.

    Stability:
        experimental
    """

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

@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions-tasks.CompressionType")
class CompressionType(enum.Enum):
    """Compression type of the data.

    Stability:
        experimental
    """
    None_ = "None"
    """None compression type.

    Stability:
        experimental
    """
    Gzip = "Gzip"
    """Gzip compression type.

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

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.DataSource", jsii_struct_bases=[])
class DataSource(jsii.compat.TypedDict):
    """Location of the channel data.

    Stability:
        experimental
    """
    s3DataSource: "S3DataSource"
    """S3 location of the data source that is associated with a channel.

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

@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions-tasks.InputMode")
class InputMode(enum.Enum):
    """Input mode that the algorithm supports.

    Stability:
        experimental
    """
    Pipe = "Pipe"
    """Pipe mode.

    Stability:
        experimental
    """
    File = "File"
    """File mode.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions-tasks.InvocationType")
class InvocationType(enum.Enum):
    """Invocation type of a Lambda.

    Stability:
        experimental
    """
    RequestResponse = "RequestResponse"
    """Invoke synchronously.

    The API response includes the function response and additional data.

    Stability:
        experimental
    """
    Event = "Event"
    """Invoke asynchronously.

    Send events that fail multiple times to the function's dead-letter queue (if it's configured).
    The API response only includes a status code.

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

    OUTPUT: the output of this task is the return value of the Lambda Function.

    Stability:
        experimental
    """
    def __init__(self, lambda_function: aws_cdk.aws_lambda.IFunction, *, payload: typing.Optional[typing.Mapping[str,typing.Any]]=None) -> None:
        """
        Arguments:
            lambdaFunction: -
            props: -
            payload: The JSON that you want to provide to your Lambda function as input. Default: - The JSON data indicated by the task's InputPath is used as payload

        Stability:
            experimental
        """
        props: InvokeFunctionProps = {}

        if payload is not None:
            props["payload"] = payload

        jsii.create(InvokeFunction, self, [lambda_function, props])

    @jsii.member(jsii_name="bind")
    def bind(self, _task: aws_cdk.aws_stepfunctions.Task) -> aws_cdk.aws_stepfunctions.StepFunctionsTaskConfig:
        """Called when the task object is used in a workflow.

        Arguments:
            _task: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_task])


@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.InvokeFunctionProps", jsii_struct_bases=[])
class InvokeFunctionProps(jsii.compat.TypedDict, total=False):
    """Properties for InvokeFunction.

    Stability:
        experimental
    """
    payload: typing.Mapping[str,typing.Any]
    """The JSON that you want to provide to your Lambda function as input.

    Default:
        - The JSON data indicated by the task's InputPath is used as payload

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.MetricDefinition", jsii_struct_bases=[])
class MetricDefinition(jsii.compat.TypedDict):
    """Specifies the metric name and regular expressions used to parse algorithm logs.

    Stability:
        experimental
    """
    name: str
    """Name of the metric.

    Stability:
        experimental
    """

    regex: str
    """Regular expression that searches the output of a training job and gets the value of the metric.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _OutputDataConfig(jsii.compat.TypedDict, total=False):
    encryptionKey: aws_cdk.aws_kms.IKey
    """Optional KMS encryption key that Amazon SageMaker uses to encrypt the model artifacts at rest using Amazon S3 server-side encryption.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.OutputDataConfig", jsii_struct_bases=[_OutputDataConfig])
class OutputDataConfig(_OutputDataConfig):
    """
    Stability:
        experimental
    """
    s3OutputPath: str
    """Identifies the S3 path where you want Amazon SageMaker to store the model artifacts.

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_stepfunctions.IStepFunctionsTask)
class PublishToTopic(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions-tasks.PublishToTopic"):
    """A StepFunctions Task to invoke a Lambda function.

    A Function can be used directly as a Resource, but this class mirrors
    integration with other AWS services via a specific class instance.

    Stability:
        experimental
    """
    def __init__(self, topic: aws_cdk.aws_sns.ITopic, *, message: aws_cdk.aws_stepfunctions.TaskInput, message_per_subscription_type: typing.Optional[bool]=None, subject: typing.Optional[str]=None, wait_for_task_token: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            topic: -
            props: -
            message: The text message to send to the topic.
            messagePerSubscriptionType: If true, send a different message to every subscription type. If this is set to true, message must be a JSON object with a "default" key and a key for every subscription type (such as "sqs", "email", etc.) The values are strings representing the messages being sent to every subscription type.
            subject: Message subject.
            waitForTaskToken: Whether to pause the workflow until a task token is returned. Default: false

        Stability:
            experimental
        """
        props: PublishToTopicProps = {"message": message}

        if message_per_subscription_type is not None:
            props["messagePerSubscriptionType"] = message_per_subscription_type

        if subject is not None:
            props["subject"] = subject

        if wait_for_task_token is not None:
            props["waitForTaskToken"] = wait_for_task_token

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
    waitForTaskToken: bool
    """Whether to pause the workflow until a task token is returned.

    Default:
        false

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

@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions-tasks.RecordWrapperType")
class RecordWrapperType(enum.Enum):
    """Define the format of the input data.

    Stability:
        experimental
    """
    None_ = "None"
    """None record wrapper type.

    Stability:
        experimental
    """
    RecordIO = "RecordIO"
    """RecordIO record wrapper type.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _ResourceConfig(jsii.compat.TypedDict, total=False):
    volumeKmsKeyId: aws_cdk.aws_kms.IKey
    """KMS key that Amazon SageMaker uses to encrypt data on the storage volume attached to the ML compute instance(s) that run the training job.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.ResourceConfig", jsii_struct_bases=[_ResourceConfig])
class ResourceConfig(_ResourceConfig):
    """
    Stability:
        experimental
    """
    instanceCount: jsii.Number
    """The number of ML compute instances to use.

    Default:
        1 instance.

    Stability:
        experimental
    """

    instanceType: aws_cdk.aws_ec2.InstanceType
    """ML compute instance type.

    Default:
        is the 'm4.xlarge' instance type.

    Stability:
        experimental
    """

    volumeSizeInGB: jsii.Number
    """Size of the ML storage volume that you want to provision.

    Default:
        10 GB EBS volume.

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
class RunLambdaTask(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions-tasks.RunLambdaTask"):
    """Invoke a Lambda function as a Task.

    OUTPUT: the output of this task is either the return value of Lambda's
    Invoke call, or whatever the Lambda Function posted back using
    ``SendTaskSuccess/SendTaskFailure`` in ``waitForTaskToken`` mode.

    See:
        https://docs.aws.amazon.com/step-functions/latest/dg/connect-lambda.html
    Stability:
        experimental
    """
    def __init__(self, lambda_function: aws_cdk.aws_lambda.IFunction, *, client_context: typing.Optional[str]=None, invocation_type: typing.Optional["InvocationType"]=None, payload: typing.Optional[typing.Mapping[str,typing.Any]]=None, wait_for_task_token: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            lambdaFunction: -
            props: -
            clientContext: Client context to pass to the function. Default: - No context
            invocationType: Invocation type of the Lambda function. Default: RequestResponse
            payload: The JSON that you want to provide to your Lambda function as input.
            waitForTaskToken: Whether to pause the workflow until a task token is returned. If this is set to true, the Context.taskToken value must be included somewhere in the payload and the Lambda must call ``SendTaskSuccess/SendTaskFailure`` using that token. Default: false

        Stability:
            experimental
        """
        props: RunLambdaTaskProps = {}

        if client_context is not None:
            props["clientContext"] = client_context

        if invocation_type is not None:
            props["invocationType"] = invocation_type

        if payload is not None:
            props["payload"] = payload

        if wait_for_task_token is not None:
            props["waitForTaskToken"] = wait_for_task_token

        jsii.create(RunLambdaTask, self, [lambda_function, props])

    @jsii.member(jsii_name="bind")
    def bind(self, _task: aws_cdk.aws_stepfunctions.Task) -> aws_cdk.aws_stepfunctions.StepFunctionsTaskConfig:
        """Called when the task object is used in a workflow.

        Arguments:
            _task: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [_task])


@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.RunLambdaTaskProps", jsii_struct_bases=[])
class RunLambdaTaskProps(jsii.compat.TypedDict, total=False):
    """Properties for RunLambdaTask.

    Stability:
        experimental
    """
    clientContext: str
    """Client context to pass to the function.

    Default:
        - No context

    Stability:
        experimental
    """

    invocationType: "InvocationType"
    """Invocation type of the Lambda function.

    Default:
        RequestResponse

    Stability:
        experimental
    """

    payload: typing.Mapping[str,typing.Any]
    """The JSON that you want to provide to your Lambda function as input.

    Stability:
        experimental
    """

    waitForTaskToken: bool
    """Whether to pause the workflow until a task token is returned.

    If this is set to true, the Context.taskToken value must be included
    somewhere in the payload and the Lambda must call
    ``SendTaskSuccess/SendTaskFailure`` using that token.

    Default:
        false

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions-tasks.S3DataDistributionType")
class S3DataDistributionType(enum.Enum):
    """S3 Data Distribution Type.

    Stability:
        experimental
    """
    FullyReplicated = "FullyReplicated"
    """Fully replicated S3 Data Distribution Type.

    Stability:
        experimental
    """
    ShardedByS3Key = "ShardedByS3Key"
    """Sharded By S3 Key Data Distribution Type.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _S3DataSource(jsii.compat.TypedDict, total=False):
    attributeNames: typing.List[str]
    """List of one or more attribute names to use that are found in a specified augmented manifest file.

    Stability:
        experimental
    """
    s3DataDistributionType: "S3DataDistributionType"
    """S3 Data Distribution Type.

    Stability:
        experimental
    """
    s3DataType: "S3DataType"
    """S3 Data Type.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.S3DataSource", jsii_struct_bases=[_S3DataSource])
class S3DataSource(_S3DataSource):
    """S3 location of the channel data.

    Stability:
        experimental
    """
    s3Uri: str
    """S3 Uri.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions-tasks.S3DataType")
class S3DataType(enum.Enum):
    """S3 Data Type.

    Stability:
        experimental
    """
    ManifestFile = "ManifestFile"
    """Manifest File Data Type.

    Stability:
        experimental
    """
    S3Prefix = "S3Prefix"
    """S3 Prefix Data Type.

    Stability:
        experimental
    """
    AugmentedManifestFile = "AugmentedManifestFile"
    """Augmented Manifest File Data Type.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _SagemakerTrainProps(jsii.compat.TypedDict, total=False):
    hyperparameters: typing.Mapping[str,typing.Any]
    """Hyperparameters to be used for the train job.

    Stability:
        experimental
    """
    resourceConfig: "ResourceConfig"
    """Identifies the resources, ML compute instances, and ML storage volumes to deploy for model training.

    Stability:
        experimental
    """
    role: aws_cdk.aws_iam.IRole
    """Role for thte Training Job.

    Stability:
        experimental
    """
    stoppingCondition: "StoppingCondition"
    """Sets a time limit for training.

    Stability:
        experimental
    """
    synchronous: bool
    """Specify if the task is synchronous or asychronous.

    Default:
        false

    Stability:
        experimental
    """
    tags: typing.Mapping[str,typing.Any]
    """Tags to be applied to the train job.

    Stability:
        experimental
    """
    vpcConfig: "VpcConfig"
    """Specifies the VPC that you want your training job to connect to.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.SagemakerTrainProps", jsii_struct_bases=[_SagemakerTrainProps])
class SagemakerTrainProps(_SagemakerTrainProps):
    """
    Stability:
        experimental
    """
    algorithmSpecification: "AlgorithmSpecification"
    """Identifies the training algorithm to use.

    Stability:
        experimental
    """

    inputDataConfig: typing.List["Channel"]
    """Describes the various datasets (e.g. train, validation, test) and the Amazon S3 location where stored.

    Stability:
        experimental
    """

    outputDataConfig: "OutputDataConfig"
    """Identifies the Amazon S3 location where you want Amazon SageMaker to save the results of model training.

    Stability:
        experimental
    """

    trainingJobName: str
    """Training Job Name.

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_ec2.IConnectable, aws_cdk.aws_stepfunctions.IStepFunctionsTask)
class SagemakerTrainTask(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions-tasks.SagemakerTrainTask"):
    """Class representing the SageMaker Create Training Job task.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, *, algorithm_specification: "AlgorithmSpecification", input_data_config: typing.List["Channel"], output_data_config: "OutputDataConfig", training_job_name: str, hyperparameters: typing.Optional[typing.Mapping[str,typing.Any]]=None, resource_config: typing.Optional["ResourceConfig"]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, stopping_condition: typing.Optional["StoppingCondition"]=None, synchronous: typing.Optional[bool]=None, tags: typing.Optional[typing.Mapping[str,typing.Any]]=None, vpc_config: typing.Optional["VpcConfig"]=None) -> None:
        """
        Arguments:
            scope: -
            props: -
            algorithmSpecification: Identifies the training algorithm to use.
            inputDataConfig: Describes the various datasets (e.g. train, validation, test) and the Amazon S3 location where stored.
            outputDataConfig: Identifies the Amazon S3 location where you want Amazon SageMaker to save the results of model training.
            trainingJobName: Training Job Name.
            hyperparameters: Hyperparameters to be used for the train job.
            resourceConfig: Identifies the resources, ML compute instances, and ML storage volumes to deploy for model training.
            role: Role for thte Training Job.
            stoppingCondition: Sets a time limit for training.
            synchronous: Specify if the task is synchronous or asychronous. Default: false
            tags: Tags to be applied to the train job.
            vpcConfig: Specifies the VPC that you want your training job to connect to.

        Stability:
            experimental
        """
        props: SagemakerTrainProps = {"algorithmSpecification": algorithm_specification, "inputDataConfig": input_data_config, "outputDataConfig": output_data_config, "trainingJobName": training_job_name}

        if hyperparameters is not None:
            props["hyperparameters"] = hyperparameters

        if resource_config is not None:
            props["resourceConfig"] = resource_config

        if role is not None:
            props["role"] = role

        if stopping_condition is not None:
            props["stoppingCondition"] = stopping_condition

        if synchronous is not None:
            props["synchronous"] = synchronous

        if tags is not None:
            props["tags"] = tags

        if vpc_config is not None:
            props["vpcConfig"] = vpc_config

        jsii.create(SagemakerTrainTask, self, [scope, props])

    @jsii.member(jsii_name="bind")
    def bind(self, task: aws_cdk.aws_stepfunctions.Task) -> aws_cdk.aws_stepfunctions.StepFunctionsTaskConfig:
        """Called when the task object is used in a workflow.

        Arguments:
            task: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [task])

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """Allows specify security group connections for instances of this fleet.

        Stability:
            experimental
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        """The execution role for the Sagemaker training job.

        Default:
            new role for Amazon SageMaker to assume is automatically created.

        Stability:
            experimental
        """
        return jsii.get(self, "role")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _SagemakerTransformProps(jsii.compat.TypedDict, total=False):
    batchStrategy: "BatchStrategy"
    """Number of records to include in a mini-batch for an HTTP inference request.

    Stability:
        experimental
    """
    environment: typing.Mapping[str,typing.Any]
    """Environment variables to set in the Docker container.

    Stability:
        experimental
    """
    maxConcurrentTransforms: jsii.Number
    """Maximum number of parallel requests that can be sent to each instance in a transform job.

    Stability:
        experimental
    """
    maxPayloadInMB: jsii.Number
    """Maximum allowed size of the payload, in MB.

    Stability:
        experimental
    """
    role: aws_cdk.aws_iam.IRole
    """Role for thte Training Job.

    Stability:
        experimental
    """
    synchronous: bool
    """Specify if the task is synchronous or asychronous.

    Stability:
        experimental
    """
    tags: typing.Mapping[str,typing.Any]
    """Tags to be applied to the train job.

    Stability:
        experimental
    """
    transformResources: "TransformResources"
    """ML compute instances for the transform job.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.SagemakerTransformProps", jsii_struct_bases=[_SagemakerTransformProps])
class SagemakerTransformProps(_SagemakerTransformProps):
    """
    Stability:
        experimental
    """
    modelName: str
    """Name of the model that you want to use for the transform job.

    Stability:
        experimental
    """

    transformInput: "TransformInput"
    """Dataset to be transformed and the Amazon S3 location where it is stored.

    Stability:
        experimental
    """

    transformJobName: str
    """Training Job Name.

    Stability:
        experimental
    """

    transformOutput: "TransformOutput"
    """S3 location where you want Amazon SageMaker to save the results from the transform job.

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_stepfunctions.IStepFunctionsTask)
class SagemakerTransformTask(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions-tasks.SagemakerTransformTask"):
    """Class representing the SageMaker Create Training Job task.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, *, model_name: str, transform_input: "TransformInput", transform_job_name: str, transform_output: "TransformOutput", batch_strategy: typing.Optional["BatchStrategy"]=None, environment: typing.Optional[typing.Mapping[str,typing.Any]]=None, max_concurrent_transforms: typing.Optional[jsii.Number]=None, max_payload_in_mb: typing.Optional[jsii.Number]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, synchronous: typing.Optional[bool]=None, tags: typing.Optional[typing.Mapping[str,typing.Any]]=None, transform_resources: typing.Optional["TransformResources"]=None) -> None:
        """
        Arguments:
            scope: -
            props: -
            modelName: Name of the model that you want to use for the transform job.
            transformInput: Dataset to be transformed and the Amazon S3 location where it is stored.
            transformJobName: Training Job Name.
            transformOutput: S3 location where you want Amazon SageMaker to save the results from the transform job.
            batchStrategy: Number of records to include in a mini-batch for an HTTP inference request.
            environment: Environment variables to set in the Docker container.
            maxConcurrentTransforms: Maximum number of parallel requests that can be sent to each instance in a transform job.
            maxPayloadInMB: Maximum allowed size of the payload, in MB.
            role: Role for thte Training Job.
            synchronous: Specify if the task is synchronous or asychronous.
            tags: Tags to be applied to the train job.
            transformResources: ML compute instances for the transform job.

        Stability:
            experimental
        """
        props: SagemakerTransformProps = {"modelName": model_name, "transformInput": transform_input, "transformJobName": transform_job_name, "transformOutput": transform_output}

        if batch_strategy is not None:
            props["batchStrategy"] = batch_strategy

        if environment is not None:
            props["environment"] = environment

        if max_concurrent_transforms is not None:
            props["maxConcurrentTransforms"] = max_concurrent_transforms

        if max_payload_in_mb is not None:
            props["maxPayloadInMB"] = max_payload_in_mb

        if role is not None:
            props["role"] = role

        if synchronous is not None:
            props["synchronous"] = synchronous

        if tags is not None:
            props["tags"] = tags

        if transform_resources is not None:
            props["transformResources"] = transform_resources

        jsii.create(SagemakerTransformTask, self, [scope, props])

    @jsii.member(jsii_name="bind")
    def bind(self, task: aws_cdk.aws_stepfunctions.Task) -> aws_cdk.aws_stepfunctions.StepFunctionsTaskConfig:
        """Called when the task object is used in a workflow.

        Arguments:
            task: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "bind", [task])

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        """The execution role for the Sagemaker training job.

        Default:
            new role for Amazon SageMaker to assume is automatically created.

        Stability:
            experimental
        """
        return jsii.get(self, "role")


@jsii.implements(aws_cdk.aws_stepfunctions.IStepFunctionsTask)
class SendToQueue(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions-tasks.SendToQueue"):
    """A StepFunctions Task to invoke a Lambda function.

    A Function can be used directly as a Resource, but this class mirrors
    integration with other AWS services via a specific class instance.

    Stability:
        experimental
    """
    def __init__(self, queue: aws_cdk.aws_sqs.IQueue, *, message_body: aws_cdk.aws_stepfunctions.TaskInput, delay_seconds: typing.Optional[jsii.Number]=None, message_deduplication_id: typing.Optional[str]=None, message_group_id: typing.Optional[str]=None, wait_for_task_token: typing.Optional[bool]=None) -> None:
        """
        Arguments:
            queue: -
            props: -
            messageBody: The text message to send to the queue.
            delaySeconds: The length of time, in seconds, for which to delay a specific message. Valid values are 0-900 seconds. Default: Default value of the queue is used
            messageDeduplicationId: The token used for deduplication of sent messages. Default: Use content-based deduplication
            messageGroupId: The tag that specifies that a message belongs to a specific message group. Required for FIFO queues. FIFO ordering applies to messages in the same message group. Default: No group ID
            waitForTaskToken: Whether to pause the workflow until a task token is returned. Default: false

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

        if wait_for_task_token is not None:
            props["waitForTaskToken"] = wait_for_task_token

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
    waitForTaskToken: bool
    """Whether to pause the workflow until a task token is returned.

    Default:
        false

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

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.ShuffleConfig", jsii_struct_bases=[])
class ShuffleConfig(jsii.compat.TypedDict):
    """Configuration for a shuffle option for input data in a channel.

    Stability:
        experimental
    """
    seed: jsii.Number
    """Determines the shuffling order.

    Stability:
        experimental
    """

@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions-tasks.SplitType")
class SplitType(enum.Enum):
    """Method to use to split the transform job's data files into smaller batches.

    Stability:
        experimental
    """
    None_ = "None"
    """Input data files are not split,.

    Stability:
        experimental
    """
    Line = "Line"
    """Split records on a newline character boundary.

    Stability:
        experimental
    """
    RecordIO = "RecordIO"
    """Split using MXNet RecordIO format.

    Stability:
        experimental
    """
    TFRecord = "TFRecord"
    """Split using TensorFlow TFRecord format.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.StoppingCondition", jsii_struct_bases=[])
class StoppingCondition(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    maxRuntimeInSeconds: jsii.Number
    """The maximum length of time, in seconds, that the training or compilation job can run.

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

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.TransformDataSource", jsii_struct_bases=[])
class TransformDataSource(jsii.compat.TypedDict):
    """S3 location of the input data that the model can consume.

    Stability:
        experimental
    """
    s3DataSource: "TransformS3DataSource"
    """S3 location of the input data.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _TransformInput(jsii.compat.TypedDict, total=False):
    compressionType: "CompressionType"
    """The compression type of the transform data.

    Stability:
        experimental
    """
    contentType: str
    """Multipurpose internet mail extension (MIME) type of the data.

    Stability:
        experimental
    """
    splitType: "SplitType"
    """Method to use to split the transform job's data files into smaller batches.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.TransformInput", jsii_struct_bases=[_TransformInput])
class TransformInput(_TransformInput):
    """Dataset to be transformed and the Amazon S3 location where it is stored.

    Stability:
        experimental
    """
    transformDataSource: "TransformDataSource"
    """S3 location of the channel data.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _TransformOutput(jsii.compat.TypedDict, total=False):
    accept: str
    """MIME type used to specify the output data.

    Stability:
        experimental
    """
    assembleWith: "AssembleWith"
    """Defines how to assemble the results of the transform job as a single S3 object.

    Stability:
        experimental
    """
    encryptionKey: aws_cdk.aws_kms.Key
    """AWS KMS key that Amazon SageMaker uses to encrypt the model artifacts at rest using Amazon S3 server-side encryption.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.TransformOutput", jsii_struct_bases=[_TransformOutput])
class TransformOutput(_TransformOutput):
    """S3 location where you want Amazon SageMaker to save the results from the transform job.

    Stability:
        experimental
    """
    s3OutputPath: str
    """S3 path where you want Amazon SageMaker to store the results of the transform job.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _TransformResources(jsii.compat.TypedDict, total=False):
    volumeKmsKeyId: aws_cdk.aws_kms.Key
    """AWS KMS key that Amazon SageMaker uses to encrypt data on the storage volume attached to the ML compute instance(s).

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.TransformResources", jsii_struct_bases=[_TransformResources])
class TransformResources(_TransformResources):
    """ML compute instances for the transform job.

    Stability:
        experimental
    """
    instanceCount: jsii.Number
    """Nmber of ML compute instances to use in the transform job.

    Stability:
        experimental
    """

    instanceType: aws_cdk.aws_ec2.InstanceType
    """ML compute instance type for the transform job.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _TransformS3DataSource(jsii.compat.TypedDict, total=False):
    s3DataType: "S3DataType"
    """S3 Data Type.

    Default:
        'S3Prefix'

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.TransformS3DataSource", jsii_struct_bases=[_TransformS3DataSource])
class TransformS3DataSource(_TransformS3DataSource):
    """Location of the channel data.

    Stability:
        experimental
    """
    s3Uri: str
    """Identifies either a key name prefix or a manifest.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-stepfunctions-tasks.VpcConfig", jsii_struct_bases=[])
class VpcConfig(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    securityGroups: typing.List[aws_cdk.aws_ec2.ISecurityGroup]
    """VPC security groups.

    Stability:
        experimental
    """

    subnets: typing.List[aws_cdk.aws_ec2.ISubnet]
    """VPC subnets.

    Stability:
        experimental
    """

    vpc: aws_cdk.aws_ec2.Vpc
    """VPC id.

    Stability:
        experimental
    """

__all__ = ["AlgorithmSpecification", "AssembleWith", "BatchStrategy", "Channel", "CommonEcsRunTaskProps", "CompressionType", "ContainerOverride", "DataSource", "EcsRunTaskBase", "EcsRunTaskBaseProps", "InputMode", "InvocationType", "InvokeActivity", "InvokeActivityProps", "InvokeFunction", "InvokeFunctionProps", "MetricDefinition", "OutputDataConfig", "PublishToTopic", "PublishToTopicProps", "RecordWrapperType", "ResourceConfig", "RunEcsEc2Task", "RunEcsEc2TaskProps", "RunEcsFargateTask", "RunEcsFargateTaskProps", "RunLambdaTask", "RunLambdaTaskProps", "S3DataDistributionType", "S3DataSource", "S3DataType", "SagemakerTrainProps", "SagemakerTrainTask", "SagemakerTransformProps", "SagemakerTransformTask", "SendToQueue", "SendToQueueProps", "ShuffleConfig", "SplitType", "StoppingCondition", "TaskEnvironmentVariable", "TransformDataSource", "TransformInput", "TransformOutput", "TransformResources", "TransformS3DataSource", "VpcConfig", "__jsii_assembly__"]

publication.publish()
