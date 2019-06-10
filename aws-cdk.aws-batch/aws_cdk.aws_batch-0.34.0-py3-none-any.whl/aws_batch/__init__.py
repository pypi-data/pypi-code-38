import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-batch", "0.34.0", __name__, "aws-batch@0.34.0.jsii.tgz")
class CfnComputeEnvironment(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-batch.CfnComputeEnvironment"):
    """A CloudFormation ``AWS::Batch::ComputeEnvironment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Batch::ComputeEnvironment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, service_role: str, type: str, compute_environment_name: typing.Optional[str]=None, compute_resources: typing.Optional[typing.Union[typing.Optional["ComputeResourcesProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None, state: typing.Optional[str]=None) -> None:
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
    @jsii.member(jsii_name="computeEnvironmentArn")
    def compute_environment_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "computeEnvironmentArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnComputeEnvironmentProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ComputeResourcesProperty(jsii.compat.TypedDict, total=False):
        bidPercentage: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnComputeEnvironment.ComputeResourcesProperty.BidPercentage``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-bidpercentage
        Stability:
            experimental
        """
        desiredvCpus: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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
        launchTemplate: typing.Union[aws_cdk.cdk.Token, "CfnComputeEnvironment.LaunchTemplateSpecificationProperty"]
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

        maxvCpus: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnComputeEnvironment.ComputeResourcesProperty.MaxvCpus``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html#cfn-batch-computeenvironment-computeresources-maxvcpus
        Stability:
            experimental
        """

        minvCpus: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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
    computeResources: typing.Union["CfnComputeEnvironment.ComputeResourcesProperty", aws_cdk.cdk.Token]
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, type: str, container_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["ContainerPropertiesProperty"]]]=None, job_definition_name: typing.Optional[str]=None, node_properties: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["NodePropertiesProperty"]]]=None, parameters: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, retry_strategy: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["RetryStrategyProperty"]]]=None, timeout: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["TimeoutProperty"]]]=None) -> None:
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
    @jsii.member(jsii_name="jobDefinitionArn")
    def job_definition_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "jobDefinitionArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnJobDefinitionProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ContainerPropertiesProperty(jsii.compat.TypedDict, total=False):
        command: typing.List[str]
        """``CfnJobDefinition.ContainerPropertiesProperty.Command``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-command
        Stability:
            experimental
        """
        environment: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnJobDefinition.EnvironmentProperty"]]]
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
        mountPoints: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnJobDefinition.MountPointsProperty"]]]
        """``CfnJobDefinition.ContainerPropertiesProperty.MountPoints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-mountpoints
        Stability:
            experimental
        """
        privileged: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnJobDefinition.ContainerPropertiesProperty.Privileged``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-privileged
        Stability:
            experimental
        """
        readonlyRootFilesystem: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnJobDefinition.ContainerPropertiesProperty.ReadonlyRootFilesystem``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-readonlyrootfilesystem
        Stability:
            experimental
        """
        resourceRequirements: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnJobDefinition.ResourceRequirementProperty"]]]
        """``CfnJobDefinition.ContainerPropertiesProperty.ResourceRequirements``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-resourcerequirements
        Stability:
            experimental
        """
        ulimits: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnJobDefinition.UlimitProperty"]]]
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
        volumes: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnJobDefinition.VolumesProperty"]]]
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

        memory: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnJobDefinition.ContainerPropertiesProperty.Memory``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-containerproperties.html#cfn-batch-jobdefinition-containerproperties-memory
        Stability:
            experimental
        """

        vcpus: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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

        readOnly: typing.Union[bool, aws_cdk.cdk.Token]
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
        mainNode: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnJobDefinition.NodePropertiesProperty.MainNode``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-mainnode
        Stability:
            experimental
        """

        nodeRangeProperties: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnJobDefinition.NodeRangePropertyProperty"]]]
        """``CfnJobDefinition.NodePropertiesProperty.NodeRangeProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-noderangeproperties
        Stability:
            experimental
        """

        numNodes: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnJobDefinition.NodePropertiesProperty.NumNodes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-jobdefinition-nodeproperties.html#cfn-batch-jobdefinition-nodeproperties-numnodes
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _NodeRangePropertyProperty(jsii.compat.TypedDict, total=False):
        container: typing.Union[aws_cdk.cdk.Token, "CfnJobDefinition.ContainerPropertiesProperty"]
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
        attempts: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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
        attemptDurationSeconds: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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
        hardLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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

        softLimit: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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
        host: typing.Union[aws_cdk.cdk.Token, "CfnJobDefinition.VolumesHostProperty"]
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
    containerProperties: typing.Union[aws_cdk.cdk.Token, "CfnJobDefinition.ContainerPropertiesProperty"]
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
    nodeProperties: typing.Union[aws_cdk.cdk.Token, "CfnJobDefinition.NodePropertiesProperty"]
    """``AWS::Batch::JobDefinition.NodeProperties``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-nodeproperties
    Stability:
        experimental
    """
    parameters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::Batch::JobDefinition.Parameters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-parameters
    Stability:
        experimental
    """
    retryStrategy: typing.Union[aws_cdk.cdk.Token, "CfnJobDefinition.RetryStrategyProperty"]
    """``AWS::Batch::JobDefinition.RetryStrategy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobdefinition.html#cfn-batch-jobdefinition-retrystrategy
    Stability:
        experimental
    """
    timeout: typing.Union[aws_cdk.cdk.Token, "CfnJobDefinition.TimeoutProperty"]
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
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, compute_environment_order: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "ComputeEnvironmentOrderProperty"]]], priority: typing.Union[jsii.Number, aws_cdk.cdk.Token], job_queue_name: typing.Optional[str]=None, state: typing.Optional[str]=None) -> None:
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
    @jsii.member(jsii_name="jobQueueArn")
    def job_queue_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "jobQueueArn")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnJobQueueProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

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

        order: typing.Union[jsii.Number, aws_cdk.cdk.Token]
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
    computeEnvironmentOrder: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnJobQueue.ComputeEnvironmentOrderProperty"]]]
    """``AWS::Batch::JobQueue.ComputeEnvironmentOrder``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-computeenvironmentorder
    Stability:
        experimental
    """

    priority: typing.Union[jsii.Number, aws_cdk.cdk.Token]
    """``AWS::Batch::JobQueue.Priority``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-jobqueue.html#cfn-batch-jobqueue-priority
    Stability:
        experimental
    """

__all__ = ["CfnComputeEnvironment", "CfnComputeEnvironmentProps", "CfnJobDefinition", "CfnJobDefinitionProps", "CfnJobQueue", "CfnJobQueueProps", "__jsii_assembly__"]

publication.publish()
