import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-batch", "0.35.0", __name__, "aws-batch@0.35.0.jsii.tgz")
class CfnComputeEnvironment(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment"):
    """A CloudFormation ``AWS::Batch::ComputeEnvironment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Batch::ComputeEnvironment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, service_role: str, type: str, compute_environment_name: typing.Optional[str]=None, compute_resources: typing.Optional[typing.Union[typing.Optional["ComputeResourcesProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, state: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Batch::ComputeEnvironment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            serviceRole: ``AWS::Batch::ComputeEnvironment.ServiceRole``.
            type: ``AWS::Batch::ComputeEnvironment.Type``.
            computeEnvironmentName: ``AWS::Batch::ComputeEnvironment.ComputeEnvironmentName``.
            computeResources: ``AWS::Batch::ComputeEnvironment.ComputeResources``.
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
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> str:
        """``AWS::Batch::ComputeEnvironment.ServiceRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-servicerole
        Stability:
            experimental
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
            experimental
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
            experimental
        """
        return jsii.get(self, "computeEnvironmentName")

    @compute_environment_name.setter
    def compute_environment_name(self, value: typing.Optional[str]):
        return jsii.set(self, "computeEnvironmentName", value)

    @property
    @jsii.member(jsii_name="computeResources")
    def compute_resources(self) -> typing.Optional[typing.Union[typing.Optional["ComputeResourcesProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Batch::ComputeEnvironment.ComputeResources``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeresources
        Stability:
            experimental
        """
        return jsii.get(self, "computeResources")

    @compute_resources.setter
    def compute_resources(self, value: typing.Optional[typing.Union[typing.Optional["ComputeResourcesProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "computeResources", value)

    @property
    @jsii.member(jsii_name="state")
    def state(self) -> typing.Optional[str]:
        """``AWS::Batch::ComputeEnvironment.State``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-state
        Stability:
            experimental
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
            experimental
        """
        desiredvCpus: jsii.Number
        """``CfnComputeEnvironment.ComputeResourcesProperty.DesiredvCpus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-desiredvcpus
        Stability:
            experimental
        """
        ec2KeyPair: str
        """``CfnComputeEnvironment.ComputeResourcesProperty.Ec2KeyPair``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-ec2keypair
        Stability:
            experimental
        """
        imageId: str
        """``CfnComputeEnvironment.ComputeResourcesProperty.ImageId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-imageid
        Stability:
            experimental
        """
        launchTemplate: typing.Union[aws_cdk.cdk.IResolvable, "CfnComputeEnvironment.LaunchTemplateSpecificationProperty"]
        """``CfnComputeEnvironment.ComputeResourcesProperty.LaunchTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-launchtemplate
        Stability:
            experimental
        """
        placementGroup: str
        """``CfnComputeEnvironment.ComputeResourcesProperty.PlacementGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-placementgroup
        Stability:
            experimental
        """
        spotIamFleetRole: str
        """``CfnComputeEnvironment.ComputeResourcesProperty.SpotIamFleetRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-spotiamfleetrole
        Stability:
            experimental
        """
        tags: typing.Mapping[typing.Any, typing.Any]
        """``CfnComputeEnvironment.ComputeResourcesProperty.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-tags
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment.ComputeResourcesProperty", jsii_struct_bases=[_ComputeResourcesProperty])
    class ComputeResourcesProperty(_ComputeResourcesProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html
        Stability:
            experimental
        """
        instanceRole: str
        """``CfnComputeEnvironment.ComputeResourcesProperty.InstanceRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancerole
        Stability:
            experimental
        """

        instanceTypes: typing.List[str]
        """``CfnComputeEnvironment.ComputeResourcesProperty.InstanceTypes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-instancetypes
        Stability:
            experimental
        """

        maxvCpus: jsii.Number
        """``CfnComputeEnvironment.ComputeResourcesProperty.MaxvCpus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-maxvcpus
        Stability:
            experimental
        """

        minvCpus: jsii.Number
        """``CfnComputeEnvironment.ComputeResourcesProperty.MinvCpus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-minvcpus
        Stability:
            experimental
        """

        securityGroupIds: typing.List[str]
        """``CfnComputeEnvironment.ComputeResourcesProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-securitygroupids
        Stability:
            experimental
        """

        subnets: typing.List[str]
        """``CfnComputeEnvironment.ComputeResourcesProperty.Subnets``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-subnets
        Stability:
            experimental
        """

        type: str
        """``CfnComputeEnvironment.ComputeResourcesProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-type
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment.LaunchTemplateSpecificationProperty", jsii_struct_bases=[])
    class LaunchTemplateSpecificationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html
        Stability:
            experimental
        """
        launchTemplateId: str
        """``CfnComputeEnvironment.LaunchTemplateSpecificationProperty.LaunchTemplateId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-launchtemplateid
        Stability:
            experimental
        """

        launchTemplateName: str
        """``CfnComputeEnvironment.LaunchTemplateSpecificationProperty.LaunchTemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-launchtemplatename
        Stability:
            experimental
        """

        version: str
        """``CfnComputeEnvironment.LaunchTemplateSpecificationProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-launchtemplatespecification.html#cfn-batch-computeenvironment-launchtemplatespecification-version
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnComputeEnvironmentProps(jsii.compat.TypedDict, total=False):
    computeEnvironmentName: str
    """``AWS::Batch::ComputeEnvironment.ComputeEnvironmentName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeenvironmentname
    Stability:
        experimental
    """
    computeResources: typing.Union["CfnComputeEnvironment.ComputeResourcesProperty", aws_cdk.cdk.IResolvable]
    """``AWS::Batch::ComputeEnvironment.ComputeResources``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-computeresources
    Stability:
        experimental
    """
    state: str
    """``AWS::Batch::ComputeEnvironment.State``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-state
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironmentProps", jsii_struct_bases=[_CfnComputeEnvironmentProps])
class CfnComputeEnvironmentProps(_CfnComputeEnvironmentProps):
    """Properties for defining a ``AWS::Batch::ComputeEnvironment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html
    Stability:
        experimental
    """
    serviceRole: str
    """``AWS::Batch::ComputeEnvironment.ServiceRole``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-servicerole
    Stability:
        experimental
    """

    type: str
    """``AWS::Batch::ComputeEnvironment.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html#cfn-batch-computeenvironment-type
    Stability:
        experimental
    """

class CfnJobDefinition(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-batch.CfnJobDefinition"):
    """A CloudFormation ``AWS::Batch::JobDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Batch::JobDefinition
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, type: str, container_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ContainerPropertiesProperty"]]]=None, job_definition_name: typing.Optional[str]=None, node_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["NodePropertiesProperty"]]]=None, parameters: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, retry_strategy: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["RetryStrategyProperty"]]]=None, timeout: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["TimeoutProperty"]]]=None) -> None:
        """Create a new ``AWS::Batch::JobDefinition``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            type: ``AWS::Batch::JobDefinition.Type``.
            containerProperties: ``AWS::Batch::JobDefinition.ContainerProperties``.
            jobDefinitionName: ``AWS::Batch::JobDefinition.JobDefinitionName``.
            nodeProperties: ``AWS::Batch::JobDefinition.NodeProperties``.
            parameters: ``AWS::Batch::JobDefinition.Parameters``.
            retryStrategy: ``AWS::Batch::JobDefinition.RetryStrategy``.
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
    @jsii.member(jsii_name="type")
    def type(self) -> str:
        """``AWS::Batch::JobDefinition.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-type
        Stability:
            experimental
        """
        return jsii.get(self, "type")

    @type.setter
    def type(self, value: str):
        return jsii.set(self, "type", value)

    @property
    @jsii.member(jsii_name="containerProperties")
    def container_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ContainerPropertiesProperty"]]]:
        """``AWS::Batch::JobDefinition.ContainerProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-containerproperties
        Stability:
            experimental
        """
        return jsii.get(self, "containerProperties")

    @container_properties.setter
    def container_properties(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["ContainerPropertiesProperty"]]]):
        return jsii.set(self, "containerProperties", value)

    @property
    @jsii.member(jsii_name="jobDefinitionName")
    def job_definition_name(self) -> typing.Optional[str]:
        """``AWS::Batch::JobDefinition.JobDefinitionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-jobdefinitionname
        Stability:
            experimental
        """
        return jsii.get(self, "jobDefinitionName")

    @job_definition_name.setter
    def job_definition_name(self, value: typing.Optional[str]):
        return jsii.set(self, "jobDefinitionName", value)

    @property
    @jsii.member(jsii_name="nodeProperties")
    def node_properties(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["NodePropertiesProperty"]]]:
        """``AWS::Batch::JobDefinition.NodeProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-nodeproperties
        Stability:
            experimental
        """
        return jsii.get(self, "nodeProperties")

    @node_properties.setter
    def node_properties(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["NodePropertiesProperty"]]]):
        return jsii.set(self, "nodeProperties", value)

    @property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::Batch::JobDefinition.Parameters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-parameters
        Stability:
            experimental
        """
        return jsii.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "parameters", value)

    @property
    @jsii.member(jsii_name="retryStrategy")
    def retry_strategy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["RetryStrategyProperty"]]]:
        """``AWS::Batch::JobDefinition.RetryStrategy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-retrystrategy
        Stability:
            experimental
        """
        return jsii.get(self, "retryStrategy")

    @retry_strategy.setter
    def retry_strategy(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["RetryStrategyProperty"]]]):
        return jsii.set(self, "retryStrategy", value)

    @property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["TimeoutProperty"]]]:
        """``AWS::Batch::JobDefinition.Timeout``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-timeout
        Stability:
            experimental
        """
        return jsii.get(self, "timeout")

    @timeout.setter
    def timeout(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["TimeoutProperty"]]]):
        return jsii.set(self, "timeout", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ContainerPropertiesProperty(jsii.compat.TypedDict, total=False):
        command: typing.List[str]
        """``CfnJobDefinition.ContainerPropertiesProperty.Command``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-command
        Stability:
            experimental
        """
        environment: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnJobDefinition.EnvironmentProperty"]]]
        """``CfnJobDefinition.ContainerPropertiesProperty.Environment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-environment
        Stability:
            experimental
        """
        instanceType: str
        """``CfnJobDefinition.ContainerPropertiesProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-instancetype
        Stability:
            experimental
        """
        jobRoleArn: str
        """``CfnJobDefinition.ContainerPropertiesProperty.JobRoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-jobrolearn
        Stability:
            experimental
        """
        mountPoints: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnJobDefinition.MountPointsProperty"]]]
        """``CfnJobDefinition.ContainerPropertiesProperty.MountPoints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-mountpoints
        Stability:
            experimental
        """
        privileged: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnJobDefinition.ContainerPropertiesProperty.Privileged``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-privileged
        Stability:
            experimental
        """
        readonlyRootFilesystem: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnJobDefinition.ContainerPropertiesProperty.ReadonlyRootFilesystem``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-readonlyrootfilesystem
        Stability:
            experimental
        """
        resourceRequirements: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnJobDefinition.ResourceRequirementProperty"]]]
        """``CfnJobDefinition.ContainerPropertiesProperty.ResourceRequirements``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-resourcerequirements
        Stability:
            experimental
        """
        ulimits: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnJobDefinition.UlimitProperty"]]]
        """``CfnJobDefinition.ContainerPropertiesProperty.Ulimits``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-ulimits
        Stability:
            experimental
        """
        user: str
        """``CfnJobDefinition.ContainerPropertiesProperty.User``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-user
        Stability:
            experimental
        """
        volumes: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnJobDefinition.VolumesProperty"]]]
        """``CfnJobDefinition.ContainerPropertiesProperty.Volumes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-volumes
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.ContainerPropertiesProperty", jsii_struct_bases=[_ContainerPropertiesProperty])
    class ContainerPropertiesProperty(_ContainerPropertiesProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html
        Stability:
            experimental
        """
        image: str
        """``CfnJobDefinition.ContainerPropertiesProperty.Image``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-image
        Stability:
            experimental
        """

        memory: jsii.Number
        """``CfnJobDefinition.ContainerPropertiesProperty.Memory``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-memory
        Stability:
            experimental
        """

        vcpus: jsii.Number
        """``CfnJobDefinition.ContainerPropertiesProperty.Vcpus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-vcpus
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.EnvironmentProperty", jsii_struct_bases=[])
    class EnvironmentProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-environment.html
        Stability:
            experimental
        """
        name: str
        """``CfnJobDefinition.EnvironmentProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-environment.html#cfn-batch-jobdefinition-environment-name
        Stability:
            experimental
        """

        value: str
        """``CfnJobDefinition.EnvironmentProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-environment.html#cfn-batch-jobdefinition-environment-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.MountPointsProperty", jsii_struct_bases=[])
    class MountPointsProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html
        Stability:
            experimental
        """
        containerPath: str
        """``CfnJobDefinition.MountPointsProperty.ContainerPath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html#cfn-batch-jobdefinition-mountpoints-containerpath
        Stability:
            experimental
        """

        readOnly: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnJobDefinition.MountPointsProperty.ReadOnly``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html#cfn-batch-jobdefinition-mountpoints-readonly
        Stability:
            experimental
        """

        sourceVolume: str
        """``CfnJobDefinition.MountPointsProperty.SourceVolume``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-mountpoints.html#cfn-batch-jobdefinition-mountpoints-sourcevolume
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.NodePropertiesProperty", jsii_struct_bases=[])
    class NodePropertiesProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html
        Stability:
            experimental
        """
        mainNode: jsii.Number
        """``CfnJobDefinition.NodePropertiesProperty.MainNode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-mainnode
        Stability:
            experimental
        """

        nodeRangeProperties: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnJobDefinition.NodeRangePropertyProperty"]]]
        """``CfnJobDefinition.NodePropertiesProperty.NodeRangeProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-noderangeproperties
        Stability:
            experimental
        """

        numNodes: jsii.Number
        """``CfnJobDefinition.NodePropertiesProperty.NumNodes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-numnodes
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _NodeRangePropertyProperty(jsii.compat.TypedDict, total=False):
        container: typing.Union[aws_cdk.cdk.IResolvable, "CfnJobDefinition.ContainerPropertiesProperty"]
        """``CfnJobDefinition.NodeRangePropertyProperty.Container``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-noderangeproperty.html#cfn-batch-jobdefinition-noderangeproperty-container
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.NodeRangePropertyProperty", jsii_struct_bases=[_NodeRangePropertyProperty])
    class NodeRangePropertyProperty(_NodeRangePropertyProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-noderangeproperty.html
        Stability:
            experimental
        """
        targetNodes: str
        """``CfnJobDefinition.NodeRangePropertyProperty.TargetNodes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-noderangeproperty.html#cfn-batch-jobdefinition-noderangeproperty-targetnodes
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.ResourceRequirementProperty", jsii_struct_bases=[])
    class ResourceRequirementProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-resourcerequirement.html
        Stability:
            experimental
        """
        type: str
        """``CfnJobDefinition.ResourceRequirementProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-resourcerequirement.html#cfn-batch-jobdefinition-resourcerequirement-type
        Stability:
            experimental
        """

        value: str
        """``CfnJobDefinition.ResourceRequirementProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-resourcerequirement.html#cfn-batch-jobdefinition-resourcerequirement-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.RetryStrategyProperty", jsii_struct_bases=[])
    class RetryStrategyProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-retrystrategy.html
        Stability:
            experimental
        """
        attempts: jsii.Number
        """``CfnJobDefinition.RetryStrategyProperty.Attempts``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-retrystrategy.html#cfn-batch-jobdefinition-retrystrategy-attempts
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.TimeoutProperty", jsii_struct_bases=[])
    class TimeoutProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-timeout.html
        Stability:
            experimental
        """
        attemptDurationSeconds: jsii.Number
        """``CfnJobDefinition.TimeoutProperty.AttemptDurationSeconds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-timeout.html#cfn-batch-jobdefinition-timeout-attemptdurationseconds
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.UlimitProperty", jsii_struct_bases=[])
    class UlimitProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html
        Stability:
            experimental
        """
        hardLimit: jsii.Number
        """``CfnJobDefinition.UlimitProperty.HardLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html#cfn-batch-jobdefinition-ulimit-hardlimit
        Stability:
            experimental
        """

        name: str
        """``CfnJobDefinition.UlimitProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html#cfn-batch-jobdefinition-ulimit-name
        Stability:
            experimental
        """

        softLimit: jsii.Number
        """``CfnJobDefinition.UlimitProperty.SoftLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-ulimit.html#cfn-batch-jobdefinition-ulimit-softlimit
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.VolumesHostProperty", jsii_struct_bases=[])
    class VolumesHostProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumeshost.html
        Stability:
            experimental
        """
        sourcePath: str
        """``CfnJobDefinition.VolumesHostProperty.SourcePath``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumeshost.html#cfn-batch-jobdefinition-volumeshost-sourcepath
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinition.VolumesProperty", jsii_struct_bases=[])
    class VolumesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html
        Stability:
            experimental
        """
        host: typing.Union[aws_cdk.cdk.IResolvable, "CfnJobDefinition.VolumesHostProperty"]
        """``CfnJobDefinition.VolumesProperty.Host``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html#cfn-batch-jobdefinition-volumes-host
        Stability:
            experimental
        """

        name: str
        """``CfnJobDefinition.VolumesProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-volumes.html#cfn-batch-jobdefinition-volumes-name
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnJobDefinitionProps(jsii.compat.TypedDict, total=False):
    containerProperties: typing.Union[aws_cdk.cdk.IResolvable, "CfnJobDefinition.ContainerPropertiesProperty"]
    """``AWS::Batch::JobDefinition.ContainerProperties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-containerproperties
    Stability:
        experimental
    """
    jobDefinitionName: str
    """``AWS::Batch::JobDefinition.JobDefinitionName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-jobdefinitionname
    Stability:
        experimental
    """
    nodeProperties: typing.Union[aws_cdk.cdk.IResolvable, "CfnJobDefinition.NodePropertiesProperty"]
    """``AWS::Batch::JobDefinition.NodeProperties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-nodeproperties
    Stability:
        experimental
    """
    parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::Batch::JobDefinition.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-parameters
    Stability:
        experimental
    """
    retryStrategy: typing.Union[aws_cdk.cdk.IResolvable, "CfnJobDefinition.RetryStrategyProperty"]
    """``AWS::Batch::JobDefinition.RetryStrategy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-retrystrategy
    Stability:
        experimental
    """
    timeout: typing.Union[aws_cdk.cdk.IResolvable, "CfnJobDefinition.TimeoutProperty"]
    """``AWS::Batch::JobDefinition.Timeout``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-timeout
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobDefinitionProps", jsii_struct_bases=[_CfnJobDefinitionProps])
class CfnJobDefinitionProps(_CfnJobDefinitionProps):
    """Properties for defining a ``AWS::Batch::JobDefinition``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html
    Stability:
        experimental
    """
    type: str
    """``AWS::Batch::JobDefinition.Type``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-type
    Stability:
        experimental
    """

class CfnJobQueue(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-batch.CfnJobQueue"):
    """A CloudFormation ``AWS::Batch::JobQueue``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Batch::JobQueue
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, compute_environment_order: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ComputeEnvironmentOrderProperty"]]], priority: jsii.Number, job_queue_name: typing.Optional[str]=None, state: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::Batch::JobQueue``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            computeEnvironmentOrder: ``AWS::Batch::JobQueue.ComputeEnvironmentOrder``.
            priority: ``AWS::Batch::JobQueue.Priority``.
            jobQueueName: ``AWS::Batch::JobQueue.JobQueueName``.
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
    @jsii.member(jsii_name="computeEnvironmentOrder")
    def compute_environment_order(self) -> typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ComputeEnvironmentOrderProperty"]]]:
        """``AWS::Batch::JobQueue.ComputeEnvironmentOrder``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-computeenvironmentorder
        Stability:
            experimental
        """
        return jsii.get(self, "computeEnvironmentOrder")

    @compute_environment_order.setter
    def compute_environment_order(self, value: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ComputeEnvironmentOrderProperty"]]]):
        return jsii.set(self, "computeEnvironmentOrder", value)

    @property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        """``AWS::Batch::JobQueue.Priority``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-priority
        Stability:
            experimental
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
            experimental
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
            experimental
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
            experimental
        """
        computeEnvironment: str
        """``CfnJobQueue.ComputeEnvironmentOrderProperty.ComputeEnvironment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobqueue-computeenvironmentorder.html#cfn-batch-jobqueue-computeenvironmentorder-computeenvironment
        Stability:
            experimental
        """

        order: jsii.Number
        """``CfnJobQueue.ComputeEnvironmentOrderProperty.Order``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobqueue-computeenvironmentorder.html#cfn-batch-jobqueue-computeenvironmentorder-order
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnJobQueueProps(jsii.compat.TypedDict, total=False):
    jobQueueName: str
    """``AWS::Batch::JobQueue.JobQueueName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-jobqueuename
    Stability:
        experimental
    """
    state: str
    """``AWS::Batch::JobQueue.State``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-state
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-batch.CfnJobQueueProps", jsii_struct_bases=[_CfnJobQueueProps])
class CfnJobQueueProps(_CfnJobQueueProps):
    """Properties for defining a ``AWS::Batch::JobQueue``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html
    Stability:
        experimental
    """
    computeEnvironmentOrder: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnJobQueue.ComputeEnvironmentOrderProperty"]]]
    """``AWS::Batch::JobQueue.ComputeEnvironmentOrder``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-computeenvironmentorder
    Stability:
        experimental
    """

    priority: jsii.Number
    """``AWS::Batch::JobQueue.Priority``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-priority
    Stability:
        experimental
    """

__all__ = ["CfnComputeEnvironment", "CfnComputeEnvironmentProps", "CfnJobDefinition", "CfnJobDefinitionProps", "CfnJobQueue", "CfnJobQueueProps", "__jsii_assembly__"]

publication.publish()
