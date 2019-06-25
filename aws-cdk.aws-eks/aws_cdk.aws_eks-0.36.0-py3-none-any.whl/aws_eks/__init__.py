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
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-eks", "0.36.0", __name__, "aws-eks@0.36.0.jsii.tgz")
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

class CfnCluster(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-eks.CfnCluster"):
    """A CloudFormation ``AWS::EKS::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html
    Stability:
        stable
    cloudformationResource:
        AWS::EKS::Cluster
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, resources_vpc_config: typing.Union["ResourcesVpcConfigProperty", aws_cdk.core.IResolvable], role_arn: str, name: typing.Optional[str]=None, version: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EKS::Cluster``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            resources_vpc_config: ``AWS::EKS::Cluster.ResourcesVpcConfig``.
            role_arn: ``AWS::EKS::Cluster.RoleArn``.
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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrCertificateAuthorityData")
    def attr_certificate_authority_data(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            CertificateAuthorityData
        """
        return jsii.get(self, "attrCertificateAuthorityData")

    @property
    @jsii.member(jsii_name="attrEndpoint")
    def attr_endpoint(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            Endpoint
        """
        return jsii.get(self, "attrEndpoint")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="resourcesVpcConfig")
    def resources_vpc_config(self) -> typing.Union["ResourcesVpcConfigProperty", aws_cdk.core.IResolvable]:
        """``AWS::EKS::Cluster.ResourcesVpcConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-resourcesvpcconfig
        Stability:
            stable
        """
        return jsii.get(self, "resourcesVpcConfig")

    @resources_vpc_config.setter
    def resources_vpc_config(self, value: typing.Union["ResourcesVpcConfigProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "resourcesVpcConfig", value)

    @property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        """``AWS::EKS::Cluster.RoleArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-rolearn
        Stability:
            stable
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter
    def role_arn(self, value: str):
        return jsii.set(self, "roleArn", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::EKS::Cluster.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="version")
    def version(self) -> typing.Optional[str]:
        """``AWS::EKS::Cluster.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-version
        Stability:
            stable
        """
        return jsii.get(self, "version")

    @version.setter
    def version(self, value: typing.Optional[str]):
        return jsii.set(self, "version", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ResourcesVpcConfigProperty(jsii.compat.TypedDict, total=False):
        securityGroupIds: typing.List[str]
        """``CfnCluster.ResourcesVpcConfigProperty.SecurityGroupIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-cluster-resourcesvpcconfig.html#cfn-eks-cluster-resourcesvpcconfig-securitygroupids
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-eks.CfnCluster.ResourcesVpcConfigProperty", jsii_struct_bases=[_ResourcesVpcConfigProperty])
    class ResourcesVpcConfigProperty(_ResourcesVpcConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-cluster-resourcesvpcconfig.html
        Stability:
            stable
        """
        subnetIds: typing.List[str]
        """``CfnCluster.ResourcesVpcConfigProperty.SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-cluster-resourcesvpcconfig.html#cfn-eks-cluster-resourcesvpcconfig-subnetids
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnClusterProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::EKS::Cluster.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-name
    Stability:
        stable
    """
    version: str
    """``AWS::EKS::Cluster.Version``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-version
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-eks.CfnClusterProps", jsii_struct_bases=[_CfnClusterProps])
class CfnClusterProps(_CfnClusterProps):
    """Properties for defining a ``AWS::EKS::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html
    Stability:
        stable
    """
    resourcesVpcConfig: typing.Union["CfnCluster.ResourcesVpcConfigProperty", aws_cdk.core.IResolvable]
    """``AWS::EKS::Cluster.ResourcesVpcConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-resourcesvpcconfig
    Stability:
        stable
    """

    roleArn: str
    """``AWS::EKS::Cluster.RoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-cluster.html#cfn-eks-cluster-rolearn
    Stability:
        stable
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

@jsii.implements(aws_cdk.aws_ec2.IMachineImage)
class EksOptimizedAmi(aws_cdk.aws_ec2.GenericLinuxImage, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-eks.EksOptimizedAmi"):
    """Source for EKS optimized AMIs.

    Stability:
        experimental
    """
    def __init__(self, *, kubernetes_version: typing.Optional[str]=None, node_type: typing.Optional["NodeType"]=None) -> None:
        """
        Arguments:
            props: -
            kubernetes_version: The Kubernetes version to use. Default: The latest version
            node_type: What instance type to retrieve the image for (normal or GPU-optimized). Default: Normal

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
class ICluster(aws_cdk.core.IResource, aws_cdk.aws_ec2.IConnectable, jsii.compat.Protocol):
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


class _IClusterProxy(jsii.proxy_for(aws_cdk.core.IResource), jsii.proxy_for(aws_cdk.aws_ec2.IConnectable)):
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
class Cluster(aws_cdk.core.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-eks.Cluster"):
    """A Cluster represents a managed Kubernetes Service (EKS).

    This is a fully managed cluster of API Servers (control-plane)
    The user is still required to create the worker nodes.

    Stability:
        experimental
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, vpc: aws_cdk.aws_ec2.IVpc, cluster_name: typing.Optional[str]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None, security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]=None, version: typing.Optional[str]=None, vpc_subnets: typing.Optional[typing.List[aws_cdk.aws_ec2.SubnetSelection]]=None) -> None:
        """Initiates an EKS Cluster with the supplied arguments.

        Arguments:
            scope: a Construct, most likely a cdk.Stack created.
            id: -
            props: properties in the IClusterProps interface.
            vpc: The VPC in which to create the Cluster.
            cluster_name: Name for the cluster. Default: Automatically generated name
            role: Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf. Default: A role is automatically created for you
            security_group: Security Group to use for Control Plane ENIs. Default: A security group is automatically created
            version: The Kubernetes version to run in the cluster. Default: If not supplied, will use Amazon default version
            vpc_subnets: Where to place EKS Control Plane ENIs. If you want to create public load balancers, this must include public subnets. For example, to only select private subnets, supply the following:: vpcSubnets: [ { subnetType: ec2.SubnetType.Private } ] Default: All public and private subnets

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
    def from_cluster_attributes(cls, scope: aws_cdk.core.Construct, id: str, *, cluster_arn: str, cluster_certificate_authority_data: str, cluster_endpoint: str, cluster_name: str, security_groups: typing.List[aws_cdk.aws_ec2.ISecurityGroup], vpc: aws_cdk.aws_ec2.IVpc) -> "ICluster":
        """Import an existing cluster.

        Arguments:
            scope: the construct scope, in most cases 'this'.
            id: the id or name to import as.
            attrs: the cluster properties to use for importing information.
            cluster_arn: The unique ARN assigned to the service by AWS in the form of arn:aws:eks:.
            cluster_certificate_authority_data: The certificate-authority-data for your cluster.
            cluster_endpoint: The API Server endpoint URL.
            cluster_name: The physical name of the Cluster.
            security_groups: 
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
            auto_scaling_group: [disable-awslint:ref-via-interface].
            options: -
            max_pods: How many pods to allow on this instance. Should be at most equal to the maximum number of IP addresses available to the instance type less one.

        See:
            https://docs.aws.amazon.com/eks/latest/userguide/launch-workers.html
        Stability:
            experimental
        """
        options: AddAutoScalingGroupOptions = {"maxPods": max_pods}

        return jsii.invoke(self, "addAutoScalingGroup", [auto_scaling_group, options])

    @jsii.member(jsii_name="addCapacity")
    def add_capacity(self, id: str, *, instance_type: aws_cdk.aws_ec2.InstanceType, allow_all_outbound: typing.Optional[bool]=None, associate_public_ip_address: typing.Optional[bool]=None, cooldown: typing.Optional[aws_cdk.core.Duration]=None, desired_capacity: typing.Optional[jsii.Number]=None, ignore_unmodified_size_properties: typing.Optional[bool]=None, key_name: typing.Optional[str]=None, max_capacity: typing.Optional[jsii.Number]=None, min_capacity: typing.Optional[jsii.Number]=None, notifications_topic: typing.Optional[aws_cdk.aws_sns.ITopic]=None, replacing_update_min_successful_instances_percent: typing.Optional[jsii.Number]=None, resource_signal_count: typing.Optional[jsii.Number]=None, resource_signal_timeout: typing.Optional[aws_cdk.core.Duration]=None, rolling_update_configuration: typing.Optional[aws_cdk.aws_autoscaling.RollingUpdateConfiguration]=None, spot_price: typing.Optional[str]=None, update_type: typing.Optional[aws_cdk.aws_autoscaling.UpdateType]=None, vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection]=None) -> aws_cdk.aws_autoscaling.AutoScalingGroup:
        """Add nodes to this EKS cluster.

        The nodes will automatically be configured with the right VPC and AMI
        for the instance type and Kubernetes version.

        Arguments:
            id: -
            options: -
            instance_type: Instance type of the instances to start.
            allow_all_outbound: Whether the instances can initiate connections to anywhere by default. Default: true
            associate_public_ip_address: Whether instances in the Auto Scaling Group should have public IP addresses associated with them. Default: - Use subnet setting.
            cooldown: Default scaling cooldown for this AutoScalingGroup. Default: Duration.minutes(5)
            desired_capacity: Initial amount of instances in the fleet. Default: 1
            ignore_unmodified_size_properties: If the ASG has scheduled actions, don't reset unchanged group sizes. Only used if the ASG has scheduled actions (which may scale your ASG up or down regardless of cdk deployments). If true, the size of the group will only be reset if it has been changed in the CDK app. If false, the sizes will always be changed back to what they were in the CDK app on deployment. Default: true
            key_name: Name of SSH keypair to grant access to instances. Default: - No SSH access will be possible.
            max_capacity: Maximum number of instances in the fleet. Default: desiredCapacity
            min_capacity: Minimum number of instances in the fleet. Default: 1
            notifications_topic: SNS topic to send notifications about fleet changes. Default: - No fleet change notifications will be sent.
            replacing_update_min_successful_instances_percent: Configuration for replacing updates. Only used if updateType == UpdateType.ReplacingUpdate. Specifies how many instances must signal success for the update to succeed. Default: minSuccessfulInstancesPercent
            resource_signal_count: How many ResourceSignal calls CloudFormation expects before the resource is considered created. Default: 1
            resource_signal_timeout: The length of time to wait for the resourceSignalCount. The maximum value is 43200 (12 hours). Default: Duration.minutes(5)
            rolling_update_configuration: Configuration for rolling updates. Only used if updateType == UpdateType.RollingUpdate. Default: - RollingUpdateConfiguration with defaults.
            spot_price: The maximum hourly price (in USD) to be paid for any Spot Instance launched to fulfill the request. Spot Instances are launched when the price you specify exceeds the current Spot market price. Default: none
            update_type: What to do when an AutoScalingGroup's instance configuration is changed. This is applied when any of the settings on the ASG are changed that affect how the instances should be created (VPC, instance type, startup scripts, etc.). It indicates how the existing instances should be replaced with new instances matching the new config. By default, nothing is done and only new instances are launched with the new config. Default: UpdateType.None
            vpc_subnets: Where to place instances within the VPC. Default: - All Private subnets.

        Stability:
            experimental
        """
        options: AddWorkerNodesOptions = {"instanceType": instance_type}

        if allow_all_outbound is not None:
            options["allowAllOutbound"] = allow_all_outbound

        if associate_public_ip_address is not None:
            options["associatePublicIpAddress"] = associate_public_ip_address

        if cooldown is not None:
            options["cooldown"] = cooldown

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

        if resource_signal_timeout is not None:
            options["resourceSignalTimeout"] = resource_signal_timeout

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
    NORMAL = "NORMAL"
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
