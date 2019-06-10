import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_autoscaling
import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-eks", "0.34.0", __name__, "aws-eks@0.34.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-eks.AddAutoScalingGroupOptions", jsii_struct_bases=[])
class AddAutoScalingGroupOptions(jsii.compat.TypedDict):
    """Options for adding an AutoScalingGroup as capacity.

    Stability:
        experimental
    """
    maxPods: jsii.Number
    """How many pods to allow on this instance.

    Should be at most equal to the maximum number of IP addresses available to
    the instance type less one.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-eks.AddWorkerNodesOptions", jsii_struct_bases=[aws_cdk.aws_autoscaling.CommonAutoScalingGroupProps])
class AddWorkerNodesOptions(aws_cdk.aws_autoscaling.CommonAutoScalingGroupProps, jsii.compat.TypedDict):
    """Options for adding worker nodes.

    Stability:
        experimental
    """
    instanceType: aws_cdk.aws_ec2.InstanceType
    """Instance type of the instances to start.

    Stability:
        experimental
    """

class CfnCluster(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-eks.CfnCluster"):
    """A CloudFormation ``AWS::EKS::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EKS::Cluster
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, resources_vpc_config: typing.Union["ResourcesVpcConfigProperty", aws_cdk.cdk.Token], role_arn: str, name: typing.Optional[str]=None, version: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EKS::Cluster``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            resourcesVpcConfig: ``AWS::EKS::Cluster.ResourcesVpcConfig``.
            roleArn: ``AWS::EKS::Cluster.RoleArn``.
            name: ``AWS::EKS::Cluster.Name``.
            version: ``AWS::EKS::Cluster.Version``.

        Stability:
            experimental
        """
        props: CfnClusterProps = {"resourcesVpcConfig": resources_vpc_config, "roleArn": role_arn}

        if name is not None:
            props["name"] = name

        if version is not None:
            props["version"] = version

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
    @jsii.member(jsii_name="clusterCertificateAuthorityData")
    def cluster_certificate_authority_data(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            CertificateAuthorityData
        """
        return jsii.get(self, "clusterCertificateAuthorityData")

    @property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Endpoint
        """
        return jsii.get(self, "clusterEndpoint")

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

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ResourcesVpcConfigProperty(jsii.compat.TypedDict, total=False):
        securityGroupIds: typing.List[str]
        """``CfnCluster.ResourcesVpcConfigProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-cluster-resourcesvpcconfig.html#cfn-eks-cluster-resourcesvpcconfig-securitygroupids
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-eks.CfnCluster.ResourcesVpcConfigProperty", jsii_struct_bases=[_ResourcesVpcConfigProperty])
    class ResourcesVpcConfigProperty(_ResourcesVpcConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-cluster-resourcesvpcconfig.html
        Stability:
            experimental
        """
        subnetIds: typing.List[str]
        """``CfnCluster.ResourcesVpcConfigProperty.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-cluster-resourcesvpcconfig.html#cfn-eks-cluster-resourcesvpcconfig-subnetids
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnClusterProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::EKS::Cluster.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-name
    Stability:
        experimental
    """
    version: str
    """``AWS::EKS::Cluster.Version``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-version
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-eks.CfnClusterProps", jsii_struct_bases=[_CfnClusterProps])
class CfnClusterProps(_CfnClusterProps):
    """Properties for defining a ``AWS::EKS::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html
    Stability:
        experimental
    """
    resourcesVpcConfig: typing.Union["CfnCluster.ResourcesVpcConfigProperty", aws_cdk.cdk.Token]
    """``AWS::EKS::Cluster.ResourcesVpcConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-resourcesvpcconfig
    Stability:
        experimental
    """

    roleArn: str
    """``AWS::EKS::Cluster.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-rolearn
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-eks.ClusterAttributes", jsii_struct_bases=[])
class ClusterAttributes(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    clusterArn: str
    """The unique ARN assigned to the service by AWS in the form of arn:aws:eks:.

    Stability:
        experimental
    """

    clusterCertificateAuthorityData: str
    """The certificate-authority-data for your cluster.

    Stability:
        experimental
    """

    clusterEndpoint: str
    """The API Server endpoint URL.

    Stability:
        experimental
    """

    clusterName: str
    """The physical name of the Cluster.

    Stability:
        experimental
    """

    securityGroups: typing.List[aws_cdk.aws_ec2.ISecurityGroup]
    """
    Stability:
        experimental
    """

    vpc: aws_cdk.aws_ec2.IVpc
    """The VPC in which this Cluster was created.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _ClusterProps(jsii.compat.TypedDict, total=False):
    clusterName: str
    """Name for the cluster.

    Default:
        Automatically generated name

    Stability:
        experimental
    """
    role: aws_cdk.aws_iam.IRole
    """Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf.

    Default:
        A role is automatically created for you

    Stability:
        experimental
    """
    securityGroup: aws_cdk.aws_ec2.ISecurityGroup
    """Security Group to use for Control Plane ENIs.

    Default:
        A security group is automatically created

    Stability:
        experimental
    """
    version: str
    """The Kubernetes version to run in the cluster.

    Default:
        If not supplied, will use Amazon default version

    Stability:
        experimental
    """
    vpcSubnets: typing.List[aws_cdk.aws_ec2.SubnetSelection]
    """Where to place EKS Control Plane ENIs.

    If you want to create public load balancers, this must include public subnets.

    For example, to only select private subnets, supply the following::

       vpcSubnets: [
          { subnetType: ec2.SubnetType.Private }
       ]

    Default:
        All public and private subnets

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-eks.ClusterProps", jsii_struct_bases=[_ClusterProps])
class ClusterProps(_ClusterProps):
    """Properties to instantiate the Cluster.

    Stability:
        experimental
    """
    vpc: aws_cdk.aws_ec2.IVpc
    """The VPC in which to create the Cluster.

    Stability:
        experimental
    """

@jsii.implements(aws_cdk.aws_ec2.IMachineImageSource)
class EksOptimizedAmi(aws_cdk.aws_ec2.GenericLinuxImage, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-eks.EksOptimizedAmi"):
    """Source for EKS optimized AMIs.

    Stability:
        experimental
    """
    def __init__(self, *, kubernetes_version: typing.Optional[str]=None, node_type: typing.Optional["NodeType"]=None) -> None:
        """
        Arguments:
            props: -
            kubernetesVersion: The Kubernetes version to use. Default: The latest version
            nodeType: What instance type to retrieve the image for (normal or GPU-optimized). Default: Normal

        Stability:
            experimental
        """
        props: EksOptimizedAmiProps = {}

        if kubernetes_version is not None:
            props["kubernetesVersion"] = kubernetes_version

        if node_type is not None:
            props["nodeType"] = node_type

        jsii.create(EksOptimizedAmi, self, [props])


@jsii.data_type(jsii_type="@aws-cdk/aws-eks.EksOptimizedAmiProps", jsii_struct_bases=[])
class EksOptimizedAmiProps(jsii.compat.TypedDict, total=False):
    """Properties for EksOptimizedAmi.

    Stability:
        experimental
    """
    kubernetesVersion: str
    """The Kubernetes version to use.

    Default:
        The latest version

    Stability:
        experimental
    """

    nodeType: "NodeType"
    """What instance type to retrieve the image for (normal or GPU-optimized).

    Default:
        Normal

    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-eks.ICluster")
class ICluster(aws_cdk.cdk.IResource, aws_cdk.aws_ec2.IConnectable, jsii.compat.Protocol):
    """An EKS cluster.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IClusterProxy

    @property
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> str:
        """The unique ARN assigned to the service by AWS in the form of arn:aws:eks:.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="clusterCertificateAuthorityData")
    def cluster_certificate_authority_data(self) -> str:
        """The certificate-authority-data for your cluster.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> str:
        """The API Server endpoint URL.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """The physical name of the Cluster.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """The VPC in which this Cluster was created.

        Stability:
            experimental
        """
        ...


class _IClusterProxy(jsii.proxy_for(aws_cdk.cdk.IResource), jsii.proxy_for(aws_cdk.aws_ec2.IConnectable)):
    """An EKS cluster.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-eks.ICluster"
    @property
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> str:
        """The unique ARN assigned to the service by AWS in the form of arn:aws:eks:.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "clusterArn")

    @property
    @jsii.member(jsii_name="clusterCertificateAuthorityData")
    def cluster_certificate_authority_data(self) -> str:
        """The certificate-authority-data for your cluster.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "clusterCertificateAuthorityData")

    @property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> str:
        """The API Server endpoint URL.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "clusterEndpoint")

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """The physical name of the Cluster.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "clusterName")

    @property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """The VPC in which this Cluster was created.

        Stability:
            experimental
        """
        return jsii.get(self, "vpc")


@jsii.implements(ICluster)
class Cluster(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-eks.Cluster"):
    """A Cluster represents a managed Kubernetes Service (EKS).

    This is a fully managed cluster of API Servers (control-plane)
    The user is still required to create the worker nodes.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, vpc: aws_cdk.aws_ec2.IVpc, cluster_name: typing.Optional[str]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]=None, version: typing.Optional[str]=None, vpc_subnets: typing.Optional[typing.List[aws_cdk.aws_ec2.SubnetSelection]]=None) -> None:
        """Initiates an EKS Cluster with the supplied arguments.

        Arguments:
            scope: a Construct, most likely a cdk.Stack created.
            id: -
            props: properties in the IClusterProps interface.
            vpc: The VPC in which to create the Cluster.
            clusterName: Name for the cluster. Default: Automatically generated name
            role: Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf. Default: A role is automatically created for you
            securityGroup: Security Group to use for Control Plane ENIs. Default: A security group is automatically created
            version: The Kubernetes version to run in the cluster. Default: If not supplied, will use Amazon default version
            vpcSubnets: Where to place EKS Control Plane ENIs. If you want to create public load balancers, this must include public subnets. For example, to only select private subnets, supply the following:: vpcSubnets: [ { subnetType: ec2.SubnetType.Private } ] Default: All public and private subnets

        Stability:
            experimental
        """
        props: ClusterProps = {"vpc": vpc}

        if cluster_name is not None:
            props["clusterName"] = cluster_name

        if role is not None:
            props["role"] = role

        if security_group is not None:
            props["securityGroup"] = security_group

        if version is not None:
            props["version"] = version

        if vpc_subnets is not None:
            props["vpcSubnets"] = vpc_subnets

        jsii.create(Cluster, self, [scope, id, props])

    @jsii.member(jsii_name="fromClusterAttributes")
    @classmethod
    def from_cluster_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, cluster_arn: str, cluster_certificate_authority_data: str, cluster_endpoint: str, cluster_name: str, security_groups: typing.List[aws_cdk.aws_ec2.ISecurityGroup], vpc: aws_cdk.aws_ec2.IVpc) -> "ICluster":
        """Import an existing cluster.

        Arguments:
            scope: the construct scope, in most cases 'this'.
            id: the id or name to import as.
            attrs: the cluster properties to use for importing information.
            clusterArn: The unique ARN assigned to the service by AWS in the form of arn:aws:eks:.
            clusterCertificateAuthorityData: The certificate-authority-data for your cluster.
            clusterEndpoint: The API Server endpoint URL.
            clusterName: The physical name of the Cluster.
            securityGroups: 
            vpc: The VPC in which this Cluster was created.

        Stability:
            experimental
        """
        attrs: ClusterAttributes = {"clusterArn": cluster_arn, "clusterCertificateAuthorityData": cluster_certificate_authority_data, "clusterEndpoint": cluster_endpoint, "clusterName": cluster_name, "securityGroups": security_groups, "vpc": vpc}

        return jsii.sinvoke(cls, "fromClusterAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="addAutoScalingGroup")
    def add_auto_scaling_group(self, auto_scaling_group: aws_cdk.aws_autoscaling.AutoScalingGroup, *, max_pods: jsii.Number) -> None:
        """Add compute capacity to this EKS cluster in the form of an AutoScalingGroup.

        The AutoScalingGroup must be running an EKS-optimized AMI containing the
        /etc/eks/bootstrap.sh script. This method will configure Security Groups,
        add the right policies to the instance role, apply the right tags, and add
        the required user data to the instance's launch configuration.

        Prefer to use ``addCapacity`` if possible, it will automatically configure
        the right AMI and the ``maxPods`` number based on your instance type.

        Arguments:
            autoScalingGroup: [disable-awslint:ref-via-interface].
            options: -
            maxPods: How many pods to allow on this instance. Should be at most equal to the maximum number of IP addresses available to the instance type less one.

        See:
            https://docs.aws.amazon.com/eks/latest/userguide/launch-workers.html
        Stability:
            experimental
        """
        options: AddAutoScalingGroupOptions = {"maxPods": max_pods}

        return jsii.invoke(self, "addAutoScalingGroup", [auto_scaling_group, options])

    @jsii.member(jsii_name="addCapacity")
    def add_capacity(self, id: str, *, instance_type: aws_cdk.aws_ec2.InstanceType, allow_all_outbound: typing.Optional[bool]=None, associate_public_ip_address: typing.Optional[bool]=None, cooldown_seconds: typing.Optional[jsii.Number]=None, desired_capacity: typing.Optional[jsii.Number]=None, ignore_unmodified_size_properties: typing.Optional[bool]=None, key_name: typing.Optional[str]=None, max_capacity: typing.Optional[jsii.Number]=None, min_capacity: typing.Optional[jsii.Number]=None, notifications_topic: typing.Optional[aws_cdk.aws_sns.ITopic]=None, replacing_update_min_successful_instances_percent: typing.Optional[jsii.Number]=None, resource_signal_count: typing.Optional[jsii.Number]=None, resource_signal_timeout_sec: typing.Optional[jsii.Number]=None, rolling_update_configuration: typing.Optional[aws_cdk.aws_autoscaling.RollingUpdateConfiguration]=None, spot_price: typing.Optional[str]=None, update_type: typing.Optional[aws_cdk.aws_autoscaling.UpdateType]=None, vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None) -> aws_cdk.aws_autoscaling.AutoScalingGroup:
        """Add nodes to this EKS cluster.

        The nodes will automatically be configured with the right VPC and AMI
        for the instance type and Kubernetes version.

        Arguments:
            id: -
            options: -
            instanceType: Instance type of the instances to start.
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
        options: AddWorkerNodesOptions = {"instanceType": instance_type}

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

    @property
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> str:
        """The AWS generated ARN for the Cluster resource.

        Stability:
            experimental

        Example::
            arn:aws:eks:us-west-2:666666666666:cluster/prod
        """
        return jsii.get(self, "clusterArn")

    @property
    @jsii.member(jsii_name="clusterCertificateAuthorityData")
    def cluster_certificate_authority_data(self) -> str:
        """The certificate-authority-data for your cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "clusterCertificateAuthorityData")

    @property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> str:
        """The endpoint URL for the Cluster.

        This is the URL inside the kubeconfig file to use with kubectl

        Stability:
            experimental

        Example::
            https://5E1D0CEXAMPLEA591B746AFC5AB30262.yl4.us-west-2.eks.amazonaws.com
        """
        return jsii.get(self, "clusterEndpoint")

    @property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> str:
        """The Name of the created EKS Cluster.

        Stability:
            experimental
        """
        return jsii.get(self, "clusterName")

    @property
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        """Manages connection rules (Security Group Rules) for the cluster.

        Stability:
            experimental
        memberof:
            Cluster
        type:
            {ec2.Connections}
        """
        return jsii.get(self, "connections")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        """IAM role assumed by the EKS Control Plane.

        Stability:
            experimental
        """
        return jsii.get(self, "role")

    @property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        """The VPC in which this Cluster was created.

        Stability:
            experimental
        """
        return jsii.get(self, "vpc")


@jsii.enum(jsii_type="@aws-cdk/aws-eks.NodeType")
class NodeType(enum.Enum):
    """Whether the worker nodes should support GPU or just normal instances.

    Stability:
        experimental
    """
    Normal = "Normal"
    """Normal instances.

    Stability:
        experimental
    """
    GPU = "GPU"
    """GPU instances.

    Stability:
        experimental
    """

__all__ = ["AddAutoScalingGroupOptions", "AddWorkerNodesOptions", "CfnCluster", "CfnClusterProps", "Cluster", "ClusterAttributes", "ClusterProps", "EksOptimizedAmi", "EksOptimizedAmiProps", "ICluster", "NodeType", "__jsii_assembly__"]

publication.publish()
