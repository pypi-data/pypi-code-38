import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-batch", "0.36.0", __name__, "aws-batch@0.36.0.jsii.tgz")
class CfnComputeEnvironment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment"):
    """A CloudFormation ``AWS::Batch::ComputeEnvironment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html
    Stability:
        stable
    cloudformationResource:
        AWS::Batch::ComputeEnvironment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, service_role: str, type: str, compute_environment_name: typing.Optional[str]=None, compute_resources: typing.Optional[typing.Union[typing.Optional["ComputeResourcesProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, state: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Batch::ComputeEnvironment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            service_role: ``AWS::Batch::ComputeEnvironment.ServiceRole``.
            type: ``AWS::Batch::ComputeEnvironment.Type``.
            compute_environment_name: ``AWS::Batch::ComputeEnvironment.ComputeEnvironmentName``.
            compute_resources: ``AWS::Batch::ComputeEnvironment.ComputeResources``.
            state: ``AWS::Batch::ComputeEnvironment.State``.

        Stability:
            experimental
        """
        props: CfnComputeEnvironmentProps = {"serviceRole": service_role, "type": type}

        if compute_environment_name is not None:
            props["computeEnvironmentName"] = compute_environment_name

        if compute_resources is not None:
            props["computeResources"] = compute_resources

        if state is not None:
            props["state"] = state

        jsii.create(CfnComputeEnvironment, self, [scope, id, props])

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
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> str:
        """``AWS::Batch::ComputeEnvironment.ServiceRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-servicerole
        Stability:
            stable
        """
        return jsii.get(self, "serviceRole")

    @service_role.setter
    def service_role(self, value: str):
        return jsii.set(self, "serviceRole", value)

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """``AWS::Batch::ComputeEnvironment.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-type
        Stability:
            stable
        """
        return jsii.get(self, "type")

    @type.setter
    def type(self, value: str):
        return jsii.set(self, "type", value)

    @property
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> typing.Optional[str]:
        """``AWS::Batch::ComputeEnvironment.ComputeEnvironmentName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeenvironmentname
        Stability:
            stable
        """
        return jsii.get(self, "computeEnvironmentName")

    @compute_environment_name.setter
    def compute_environment_name(self, value: typing.Optional[str]):
        return jsii.set(self, "computeEnvironmentName", value)

    @property
    @jsii.member(jsii_name="computeResources")
    def compute_resources(self) -> typing.Optional[typing.Union[typing.Optional["ComputeResourcesProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::Batch::ComputeEnvironment.ComputeResources``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeresources
        Stability:
            stable
        """
        return jsii.get(self, "computeResources")

    @compute_resources.setter
    def compute_resources(self, value: typing.Optional[typing.Union[typing.Optional["ComputeResourcesProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "computeResources", value)

    @property
    @jsii.member(jsii_name="state")
    def state(self) -> typing.Optional[str]:
        """``AWS::Batch::ComputeEnvironment.State``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-state
        Stability:
            stable
        """
        return jsii.get(self, "state")

    @state.setter
    def state(self, value: typing.Optional[str]):
        return jsii.set(self, "state", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ComputeResourcesProperty(jsii.compat.TypedDict, total=False):
        bidPercentage: jsii.Number
        """``CfnComputeEnvironment.ComputeResourcesProperty.BidPercentage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-bidpercentage
        Stability:
            stable
        """
        desiredvCpus: jsii.Number
        """``CfnComputeEnvironment.ComputeResourcesProperty.DesiredvCpus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-desiredvcpus
        Stability:
            stable
        """
        ec2KeyPair: str
        """``CfnComputeEnvironment.ComputeResourcesProperty.Ec2KeyPair``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2keypair
        Stability:
            stable
        """
        imageId: str
        """``CfnComputeEnvironment.ComputeResourcesProperty.ImageId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-imageid
        Stability:
            stable
        """
        launchTemplate: typing.Union[aws_cdk.core.IResolvable, "CfnComputeEnvironment.LaunchTemplateSpecificationProperty"]
        """``CfnComputeEnvironment.ComputeResourcesProperty.LaunchTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-launchtemplate
        Stability:
            stable
        """
        placementGroup: str
        """``CfnComputeEnvironment.ComputeResourcesProperty.PlacementGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-placementgroup
        Stability:
            stable
        """
        spotIamFleetRole: str
        """``CfnComputeEnvironment.ComputeResourcesProperty.SpotIamFleetRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-spotiamfleetrole
        Stability:
            stable
        """
        tags: typing.Any
        """``CfnComputeEnvironment.ComputeResourcesProperty.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-tags
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment.ComputeResourcesProperty", jsii_struct_bases=[_ComputeResourcesProperty])
    class ComputeResourcesProperty(_ComputeResourcesProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html
        Stability:
            stable
        """
        instanceRole: str
        """``CfnComputeEnvironment.ComputeResourcesProperty.InstanceRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancerole
        Stability:
            stable
        """

        instanceTypes: typing.List[str]
        """``CfnComputeEnvironment.ComputeResourcesProperty.InstanceTypes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancetypes
        Stability:
            stable
        """

        maxvCpus: jsii.Number
        """``CfnComputeEnvironment.ComputeResourcesProperty.MaxvCpus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-maxvcpus
        Stability:
            stable
        """

        minvCpus: jsii.Number
        """``CfnComputeEnvironment.ComputeResourcesProperty.MinvCpus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-minvcpus
        Stability:
            stable
        """

        securityGroupIds: typing.List[str]
        """``CfnComputeEnvironment.ComputeResourcesProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-securitygroupids
        Stability:
            stable
        """

        subnets: typing.List[str]
        """``CfnComputeEnvironment.ComputeResourcesProperty.Subnets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-subnets
        Stability:
            stable
        """

        type: str
        """``CfnComputeEnvironment.ComputeResourcesProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-type
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment.LaunchTemplateSpecificationProperty", jsii_struct_bases=[])
    class LaunchTemplateSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html
        Stability:
            stable
        """
        launchTemplateId: str
        """``CfnComputeEnvironment.LaunchTemplateSpecificationProperty.LaunchTemplateId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-launchtemplateid
        Stability:
            stable
        """

        launchTemplateName: str
        """``CfnComputeEnvironment.LaunchTemplateSpecificationProperty.LaunchTemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-launchtemplatename
        Stability:
            stable
        """

        version: str
        """``CfnComputeEnvironment.LaunchTemplateSpecificationProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-version
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnComputeEnvironmentProps(jsii.compat.TypedDict, total=False):
    computeEnvironmentName: str
    """``AWS::Batch::ComputeEnvironment.ComputeEnvironmentName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeenvironmentname
    Stability:
        stable
    """
    computeResources: typing.Union["CfnComputeEnvironment.ComputeResourcesProperty", aws_cdk.core.IResolvable]
    """``AWS::Batch::ComputeEnvironment.ComputeResources``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeresources
    Stability:
        stable
    """
    state: str
    """``AWS::Batch::ComputeEnvironment.State``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-state
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironmentProps", jsii_struct_bases=[_CfnComputeEnvironmentProps])
class CfnComputeEnvironmentProps(_CfnComputeEnvironmentProps):
    """Properties for defining a ``AWS::Batch::ComputeEnvironment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html
    Stability:
        stable
    """
    serviceRole: str
    """``AWS::Batch::ComputeEnvironment.ServiceRole``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-servicerole
    Stability:
        stable
    """

    type: str
    """``AWS::Batch::ComputeEnvironment.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-type
    Stability:
        stable
    """

class CfnJobDefinition(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-batch.CfnJobDefinition"):
    """A CloudFormation ``AWS::Batch::JobDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html
    Stability:
        stable
    cloudformationResource:
        AWS::Batch::JobDefinition
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, type: str, container_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ContainerPropertiesProperty"]]]=None, job_definition_name: typing.Optional[str]=None, node_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["NodePropertiesProperty"]]]=None, parameters: typing.Any=None, retry_strategy: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RetryStrategyProperty"]]]=None, timeout: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TimeoutProperty"]]]=None) -> None:
        """Create a new ``AWS::Batch::JobDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            type: ``AWS::Batch::JobDefinition.Type``.
            container_properties: ``AWS::Batch::JobDefinition.ContainerProperties``.
            job_definition_name: ``AWS::Batch::JobDefinition.JobDefinitionName``.
            node_properties: ``AWS::Batch::JobDefinition.NodeProperties``.
            parameters: ``AWS::Batch::JobDefinition.Parameters``.
            retry_strategy: ``AWS::Batch::JobDefinition.RetryStrategy``.
            timeout: ``AWS::Batch::JobDefinition.Timeout``.

        Stability:
            experimental
        """
        props: CfnJobDefinitionProps = {"type": type}

        if container_properties is not None:
            props["containerProperties"] = container_properties

        if job_definition_name is not None:
            props["jobDefinitionName"] = job_definition_name

        if node_properties is not None:
            props["nodeProperties"] = node_properties

        if parameters is not None:
            props["parameters"] = parameters

        if retry_strategy is not None:
            props["retryStrategy"] = retry_strategy

        if timeout is not None:
            props["timeout"] = timeout

        jsii.create(CfnJobDefinition, self, [scope, id, props])

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
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        """``AWS::Batch::JobDefinition.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-parameters
        Stability:
            stable
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Any):
        return jsii.set(self, "parameters", value)

    @property
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """``AWS::Batch::JobDefinition.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-type
        Stability:
            stable
        """
        return jsii.get(self, "type")

    @type.setter
    def type(self, value: str):
        return jsii.set(self, "type", value)

    @property
    @jsii.member(jsii_name="containerProperties")
    def container_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ContainerPropertiesProperty"]]]:
        """``AWS::Batch::JobDefinition.ContainerProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-containerproperties
        Stability:
            stable
        """
        return jsii.get(self, "containerProperties")

    @container_properties.setter
    def container_properties(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["ContainerPropertiesProperty"]]]):
        return jsii.set(self, "containerProperties", value)

    @property
    @jsii.member(jsii_name="jobDefinitionName")
    def job_definition_name(self) -> typing.Optional[str]:
        """``AWS::Batch::JobDefinition.JobDefinitionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-jobdefinitionname
        Stability:
            stable
        """
        return jsii.get(self, "jobDefinitionName")

    @job_definition_name.setter
    def job_definition_name(self, value: typing.Optional[str]):
        return jsii.set(self, "jobDefinitionName", value)

    @property
    @jsii.member(jsii_name="nodeProperties")
    def node_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["NodePropertiesProperty"]]]:
        """``AWS::Batch::JobDefinition.NodeProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-nodeproperties
        Stability:
            stable
        """
        return jsii.get(self, "nodeProperties")

    @node_properties.setter
    def node_properties(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["NodePropertiesProperty"]]]):
        return jsii.set(self, "nodeProperties", value)

    @property
    @jsii.member(jsii_name="retryStrategy")
    def retry_strategy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RetryStrategyProperty"]]]:
        """``AWS::Batch::JobDefinition.RetryStrategy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-retrystrategy
        Stability:
            stable
        """
        return jsii.get(self, "retryStrategy")

    @retry_strategy.setter
    def retry_strategy(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["RetryStrategyProperty"]]]):
        return jsii.set(self, "retryStrategy", value)

    @property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TimeoutProperty"]]]:
        """``AWS::Batch::JobDefinition.Timeout``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-timeout
        Stability:
            stable
        """
        return jsii.get(self, "timeout")

    @timeout.setter
    def timeout(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TimeoutProperty"]]]):
        return jsii.set(self, "timeout", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ContainerPropertiesProperty(jsii.compat.TypedDict, total=False):
        command: typing.List[str]
        """``CfnJobDefinition.ContainerPropertiesProperty.Command``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-command
        Stability:
            stable
        """
        environment: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.EnvironmentProperty"]]]
        """``CfnJobDefinition.ContainerPropertiesProperty.Environment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-environment
        Stability:
            stable
        """
        instanceType: str
        """``CfnJobDefinition.ContainerPropertiesProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-instancetype
        Stability:
            stable
        """
        jobRoleArn: str
        """``CfnJobDefinition.ContainerPropertiesProperty.JobRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-jobrolearn
        Stability:
            stable
        """
        mountPoints: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.MountPointsProperty"]]]
        """``CfnJobDefinition.ContainerPropertiesProperty.MountPoints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-mountpoints
        Stability:
            stable
        """
        privileged: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnJobDefinition.ContainerPropertiesProperty.Privileged``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-privileged
        Stability:
            stable
        """
        readonlyRootFilesystem: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnJobDefinition.ContainerPropertiesProperty.ReadonlyRootFilesystem``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-readonlyrootfilesystem
        Stability:
            stable
        """
        resourceRequirements: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ResourceRequirementProperty"]]]
        """``CfnJobDefinition.ContainerPropertiesProperty.ResourceRequirements``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-resourcerequirements
        Stability:
            stable
        """
        ulimits: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.UlimitProperty"]]]
        """``CfnJobDefinition.ContainerPropertiesProperty.Ulimits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-ulimits
        Stability:
            stable
        """
        user: str
        """``CfnJobDefinition.ContainerPropertiesProperty.User``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-user
        Stability:
            stable
        """
        volumes: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.VolumesProperty"]]]
        """``CfnJobDefinition.ContainerPropertiesProperty.Volumes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-volumes
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.ContainerPropertiesProperty", jsii_struct_bases=[_ContainerPropertiesProperty])
    class ContainerPropertiesProperty(_ContainerPropertiesProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html
        Stability:
            stable
        """
        image: str
        """``CfnJobDefinition.ContainerPropertiesProperty.Image``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-image
        Stability:
            stable
        """

        memory: jsii.Number
        """``CfnJobDefinition.ContainerPropertiesProperty.Memory``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-memory
        Stability:
            stable
        """

        vcpus: jsii.Number
        """``CfnJobDefinition.ContainerPropertiesProperty.Vcpus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-vcpus
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.EnvironmentProperty", jsii_struct_bases=[])
    class EnvironmentProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-environment.html
        Stability:
            stable
        """
        name: str
        """``CfnJobDefinition.EnvironmentProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-environment.html#cfn-batch-jobdefinition-environment-name
        Stability:
            stable
        """

        value: str
        """``CfnJobDefinition.EnvironmentProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-environment.html#cfn-batch-jobdefinition-environment-value
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.MountPointsProperty", jsii_struct_bases=[])
    class MountPointsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html
        Stability:
            stable
        """
        containerPath: str
        """``CfnJobDefinition.MountPointsProperty.ContainerPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html#cfn-batch-jobdefinition-mountpoints-containerpath
        Stability:
            stable
        """

        readOnly: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnJobDefinition.MountPointsProperty.ReadOnly``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html#cfn-batch-jobdefinition-mountpoints-readonly
        Stability:
            stable
        """

        sourceVolume: str
        """``CfnJobDefinition.MountPointsProperty.SourceVolume``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html#cfn-batch-jobdefinition-mountpoints-sourcevolume
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.NodePropertiesProperty", jsii_struct_bases=[])
    class NodePropertiesProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html
        Stability:
            stable
        """
        mainNode: jsii.Number
        """``CfnJobDefinition.NodePropertiesProperty.MainNode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-mainnode
        Stability:
            stable
        """

        nodeRangeProperties: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NodeRangePropertyProperty"]]]
        """``CfnJobDefinition.NodePropertiesProperty.NodeRangeProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-noderangeproperties
        Stability:
            stable
        """

        numNodes: jsii.Number
        """``CfnJobDefinition.NodePropertiesProperty.NumNodes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-numnodes
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _NodeRangePropertyProperty(jsii.compat.TypedDict, total=False):
        container: typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ContainerPropertiesProperty"]
        """``CfnJobDefinition.NodeRangePropertyProperty.Container``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-noderangeproperty.html#cfn-batch-jobdefinition-noderangeproperty-container
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.NodeRangePropertyProperty", jsii_struct_bases=[_NodeRangePropertyProperty])
    class NodeRangePropertyProperty(_NodeRangePropertyProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-noderangeproperty.html
        Stability:
            stable
        """
        targetNodes: str
        """``CfnJobDefinition.NodeRangePropertyProperty.TargetNodes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-noderangeproperty.html#cfn-batch-jobdefinition-noderangeproperty-targetnodes
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.ResourceRequirementProperty", jsii_struct_bases=[])
    class ResourceRequirementProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-resourcerequirement.html
        Stability:
            stable
        """
        type: str
        """``CfnJobDefinition.ResourceRequirementProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-resourcerequirement.html#cfn-batch-jobdefinition-resourcerequirement-type
        Stability:
            stable
        """

        value: str
        """``CfnJobDefinition.ResourceRequirementProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-resourcerequirement.html#cfn-batch-jobdefinition-resourcerequirement-value
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.RetryStrategyProperty", jsii_struct_bases=[])
    class RetryStrategyProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-retrystrategy.html
        Stability:
            stable
        """
        attempts: jsii.Number
        """``CfnJobDefinition.RetryStrategyProperty.Attempts``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-retrystrategy.html#cfn-batch-jobdefinition-retrystrategy-attempts
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.TimeoutProperty", jsii_struct_bases=[])
    class TimeoutProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-timeout.html
        Stability:
            stable
        """
        attemptDurationSeconds: jsii.Number
        """``CfnJobDefinition.TimeoutProperty.AttemptDurationSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-timeout.html#cfn-batch-jobdefinition-timeout-attemptdurationseconds
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.UlimitProperty", jsii_struct_bases=[])
    class UlimitProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html
        Stability:
            stable
        """
        hardLimit: jsii.Number
        """``CfnJobDefinition.UlimitProperty.HardLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html#cfn-batch-jobdefinition-ulimit-hardlimit
        Stability:
            stable
        """

        name: str
        """``CfnJobDefinition.UlimitProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html#cfn-batch-jobdefinition-ulimit-name
        Stability:
            stable
        """

        softLimit: jsii.Number
        """``CfnJobDefinition.UlimitProperty.SoftLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html#cfn-batch-jobdefinition-ulimit-softlimit
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.VolumesHostProperty", jsii_struct_bases=[])
    class VolumesHostProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumeshost.html
        Stability:
            stable
        """
        sourcePath: str
        """``CfnJobDefinition.VolumesHostProperty.SourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumeshost.html#cfn-batch-jobdefinition-volumeshost-sourcepath
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.VolumesProperty", jsii_struct_bases=[])
    class VolumesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html
        Stability:
            stable
        """
        host: typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.VolumesHostProperty"]
        """``CfnJobDefinition.VolumesProperty.Host``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html#cfn-batch-jobdefinition-volumes-host
        Stability:
            stable
        """

        name: str
        """``CfnJobDefinition.VolumesProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html#cfn-batch-jobdefinition-volumes-name
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnJobDefinitionProps(jsii.compat.TypedDict, total=False):
    containerProperties: typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.ContainerPropertiesProperty"]
    """``AWS::Batch::JobDefinition.ContainerProperties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-containerproperties
    Stability:
        stable
    """
    jobDefinitionName: str
    """``AWS::Batch::JobDefinition.JobDefinitionName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-jobdefinitionname
    Stability:
        stable
    """
    nodeProperties: typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.NodePropertiesProperty"]
    """``AWS::Batch::JobDefinition.NodeProperties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-nodeproperties
    Stability:
        stable
    """
    parameters: typing.Any
    """``AWS::Batch::JobDefinition.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-parameters
    Stability:
        stable
    """
    retryStrategy: typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.RetryStrategyProperty"]
    """``AWS::Batch::JobDefinition.RetryStrategy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-retrystrategy
    Stability:
        stable
    """
    timeout: typing.Union[aws_cdk.core.IResolvable, "CfnJobDefinition.TimeoutProperty"]
    """``AWS::Batch::JobDefinition.Timeout``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-timeout
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinitionProps", jsii_struct_bases=[_CfnJobDefinitionProps])
class CfnJobDefinitionProps(_CfnJobDefinitionProps):
    """Properties for defining a ``AWS::Batch::JobDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html
    Stability:
        stable
    """
    type: str
    """``AWS::Batch::JobDefinition.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-type
    Stability:
        stable
    """

class CfnJobQueue(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-batch.CfnJobQueue"):
    """A CloudFormation ``AWS::Batch::JobQueue``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html
    Stability:
        stable
    cloudformationResource:
        AWS::Batch::JobQueue
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, compute_environment_order: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ComputeEnvironmentOrderProperty"]]], priority: jsii.Number, job_queue_name: typing.Optional[str]=None, state: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Batch::JobQueue``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            compute_environment_order: ``AWS::Batch::JobQueue.ComputeEnvironmentOrder``.
            priority: ``AWS::Batch::JobQueue.Priority``.
            job_queue_name: ``AWS::Batch::JobQueue.JobQueueName``.
            state: ``AWS::Batch::JobQueue.State``.

        Stability:
            experimental
        """
        props: CfnJobQueueProps = {"computeEnvironmentOrder": compute_environment_order, "priority": priority}

        if job_queue_name is not None:
            props["jobQueueName"] = job_queue_name

        if state is not None:
            props["state"] = state

        jsii.create(CfnJobQueue, self, [scope, id, props])

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
    @jsii.member(jsii_name="computeEnvironmentOrder")
    def compute_environment_order(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ComputeEnvironmentOrderProperty"]]]:
        """``AWS::Batch::JobQueue.ComputeEnvironmentOrder``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-computeenvironmentorder
        Stability:
            stable
        """
        return jsii.get(self, "computeEnvironmentOrder")

    @compute_environment_order.setter
    def compute_environment_order(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "ComputeEnvironmentOrderProperty"]]]):
        return jsii.set(self, "computeEnvironmentOrder", value)

    @property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        """``AWS::Batch::JobQueue.Priority``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-priority
        Stability:
            stable
        """
        return jsii.get(self, "priority")

    @priority.setter
    def priority(self, value: jsii.Number):
        return jsii.set(self, "priority", value)

    @property
    @jsii.member(jsii_name="jobQueueName")
    def job_queue_name(self) -> typing.Optional[str]:
        """``AWS::Batch::JobQueue.JobQueueName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-jobqueuename
        Stability:
            stable
        """
        return jsii.get(self, "jobQueueName")

    @job_queue_name.setter
    def job_queue_name(self, value: typing.Optional[str]):
        return jsii.set(self, "jobQueueName", value)

    @property
    @jsii.member(jsii_name="state")
    def state(self) -> typing.Optional[str]:
        """``AWS::Batch::JobQueue.State``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-state
        Stability:
            stable
        """
        return jsii.get(self, "state")

    @state.setter
    def state(self, value: typing.Optional[str]):
        return jsii.set(self, "state", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobQueue.ComputeEnvironmentOrderProperty", jsii_struct_bases=[])
    class ComputeEnvironmentOrderProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobqueue-computeenvironmentorder.html
        Stability:
            stable
        """
        computeEnvironment: str
        """``CfnJobQueue.ComputeEnvironmentOrderProperty.ComputeEnvironment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobqueue-computeenvironmentorder.html#cfn-batch-jobqueue-computeenvironmentorder-computeenvironment
        Stability:
            stable
        """

        order: jsii.Number
        """``CfnJobQueue.ComputeEnvironmentOrderProperty.Order``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobqueue-computeenvironmentorder.html#cfn-batch-jobqueue-computeenvironmentorder-order
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnJobQueueProps(jsii.compat.TypedDict, total=False):
    jobQueueName: str
    """``AWS::Batch::JobQueue.JobQueueName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-jobqueuename
    Stability:
        stable
    """
    state: str
    """``AWS::Batch::JobQueue.State``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-state
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobQueueProps", jsii_struct_bases=[_CfnJobQueueProps])
class CfnJobQueueProps(_CfnJobQueueProps):
    """Properties for defining a ``AWS::Batch::JobQueue``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html
    Stability:
        stable
    """
    computeEnvironmentOrder: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnJobQueue.ComputeEnvironmentOrderProperty"]]]
    """``AWS::Batch::JobQueue.ComputeEnvironmentOrder``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-computeenvironmentorder
    Stability:
        stable
    """

    priority: jsii.Number
    """``AWS::Batch::JobQueue.Priority``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-priority
    Stability:
        stable
    """

__all__ = ["CfnComputeEnvironment", "CfnComputeEnvironmentProps", "CfnJobDefinition", "CfnJobDefinitionProps", "CfnJobQueue", "CfnJobQueueProps", "__jsii_assembly__"]

publication.publish()
