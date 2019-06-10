import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_autoscaling
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_elasticloadbalancing
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-codedeploy", "0.34.0", __name__, "aws-codedeploy@0.34.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.AutoRollbackConfig", jsii_struct_bases=[])
class AutoRollbackConfig(jsii.compat.TypedDict, total=False):
    """The configuration for automatically rolling back deployments in a given Deployment Group.

    Stability:
        experimental
    """
    deploymentInAlarm: bool
    """Whether to automatically roll back a deployment during which one of the configured CloudWatch alarms for this Deployment Group went off.

    Default:
        true if you've provided any Alarms with the ``alarms`` property, false otherwise

    Stability:
        experimental
    """

    failedDeployment: bool
    """Whether to automatically roll back a deployment that fails.

    Default:
        true

    Stability:
        experimental
    """

    stoppedDeployment: bool
    """Whether to automatically roll back a deployment that was manually stopped.

    Default:
        false

    Stability:
        experimental
    """

class CfnApplication(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codedeploy.CfnApplication"):
    """A CloudFormation ``AWS::CodeDeploy::Application``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-application.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CodeDeploy::Application
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, application_name: typing.Optional[str]=None, compute_platform: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::CodeDeploy::Application``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            applicationName: ``AWS::CodeDeploy::Application.ApplicationName``.
            computePlatform: ``AWS::CodeDeploy::Application.ComputePlatform``.

        Stability:
            experimental
        """
        props: CfnApplicationProps = {}

        if application_name is not None:
            props["applicationName"] = application_name

        if compute_platform is not None:
            props["computePlatform"] = compute_platform

        jsii.create(CfnApplication, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "applicationName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnApplicationProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnApplicationProps", jsii_struct_bases=[])
class CfnApplicationProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::CodeDeploy::Application``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-application.html
    Stability:
        experimental
    """
    applicationName: str
    """``AWS::CodeDeploy::Application.ApplicationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-application.html#cfn-codedeploy-application-applicationname
    Stability:
        experimental
    """

    computePlatform: str
    """``AWS::CodeDeploy::Application.ComputePlatform``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-application.html#cfn-codedeploy-application-computeplatform
    Stability:
        experimental
    """

class CfnDeploymentConfig(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentConfig"):
    """A CloudFormation ``AWS::CodeDeploy::DeploymentConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentconfig.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CodeDeploy::DeploymentConfig
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, deployment_config_name: typing.Optional[str]=None, minimum_healthy_hosts: typing.Optional[typing.Union[typing.Optional["MinimumHealthyHostsProperty"], typing.Optional[aws_cdk.cdk.Token]]]=None) -> None:
        """Create a new ``AWS::CodeDeploy::DeploymentConfig``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            deploymentConfigName: ``AWS::CodeDeploy::DeploymentConfig.DeploymentConfigName``.
            minimumHealthyHosts: ``AWS::CodeDeploy::DeploymentConfig.MinimumHealthyHosts``.

        Stability:
            experimental
        """
        props: CfnDeploymentConfigProps = {}

        if deployment_config_name is not None:
            props["deploymentConfigName"] = deployment_config_name

        if minimum_healthy_hosts is not None:
            props["minimumHealthyHosts"] = minimum_healthy_hosts

        jsii.create(CfnDeploymentConfig, self, [scope, id, props])

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
    @jsii.member(jsii_name="deploymentConfigId")
    def deployment_config_id(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentConfigId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDeploymentConfigProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentConfig.MinimumHealthyHostsProperty", jsii_struct_bases=[])
    class MinimumHealthyHostsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentconfig-minimumhealthyhosts.html
        Stability:
            experimental
        """
        type: str
        """``CfnDeploymentConfig.MinimumHealthyHostsProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentconfig-minimumhealthyhosts.html#cfn-codedeploy-deploymentconfig-minimumhealthyhosts-type
        Stability:
            experimental
        """

        value: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnDeploymentConfig.MinimumHealthyHostsProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentconfig-minimumhealthyhosts.html#cfn-codedeploy-deploymentconfig-minimumhealthyhosts-value
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentConfigProps", jsii_struct_bases=[])
class CfnDeploymentConfigProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::CodeDeploy::DeploymentConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentconfig.html
    Stability:
        experimental
    """
    deploymentConfigName: str
    """``AWS::CodeDeploy::DeploymentConfig.DeploymentConfigName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentconfig.html#cfn-codedeploy-deploymentconfig-deploymentconfigname
    Stability:
        experimental
    """

    minimumHealthyHosts: typing.Union["CfnDeploymentConfig.MinimumHealthyHostsProperty", aws_cdk.cdk.Token]
    """``AWS::CodeDeploy::DeploymentConfig.MinimumHealthyHosts``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentconfig.html#cfn-codedeploy-deploymentconfig-minimumhealthyhosts
    Stability:
        experimental
    """

class CfnDeploymentGroup(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup"):
    """A CloudFormation ``AWS::CodeDeploy::DeploymentGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html
    Stability:
        experimental
    cloudformationResource:
        AWS::CodeDeploy::DeploymentGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, application_name: str, service_role_arn: str, alarm_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["AlarmConfigurationProperty"]]]=None, auto_rollback_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["AutoRollbackConfigurationProperty"]]]=None, auto_scaling_groups: typing.Optional[typing.List[str]]=None, deployment: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["DeploymentProperty"]]]=None, deployment_config_name: typing.Optional[str]=None, deployment_group_name: typing.Optional[str]=None, deployment_style: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["DeploymentStyleProperty"]]]=None, ec2_tag_filters: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "EC2TagFilterProperty"]]]]]=None, ec2_tag_set: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["EC2TagSetProperty"]]]=None, load_balancer_info: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["LoadBalancerInfoProperty"]]]=None, on_premises_instance_tag_filters: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "TagFilterProperty"]]]]]=None, on_premises_tag_set: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional["OnPremisesTagSetProperty"]]]=None, trigger_configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "TriggerConfigProperty"]]]]]=None) -> None:
        """Create a new ``AWS::CodeDeploy::DeploymentGroup``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            applicationName: ``AWS::CodeDeploy::DeploymentGroup.ApplicationName``.
            serviceRoleArn: ``AWS::CodeDeploy::DeploymentGroup.ServiceRoleArn``.
            alarmConfiguration: ``AWS::CodeDeploy::DeploymentGroup.AlarmConfiguration``.
            autoRollbackConfiguration: ``AWS::CodeDeploy::DeploymentGroup.AutoRollbackConfiguration``.
            autoScalingGroups: ``AWS::CodeDeploy::DeploymentGroup.AutoScalingGroups``.
            deployment: ``AWS::CodeDeploy::DeploymentGroup.Deployment``.
            deploymentConfigName: ``AWS::CodeDeploy::DeploymentGroup.DeploymentConfigName``.
            deploymentGroupName: ``AWS::CodeDeploy::DeploymentGroup.DeploymentGroupName``.
            deploymentStyle: ``AWS::CodeDeploy::DeploymentGroup.DeploymentStyle``.
            ec2TagFilters: ``AWS::CodeDeploy::DeploymentGroup.Ec2TagFilters``.
            ec2TagSet: ``AWS::CodeDeploy::DeploymentGroup.Ec2TagSet``.
            loadBalancerInfo: ``AWS::CodeDeploy::DeploymentGroup.LoadBalancerInfo``.
            onPremisesInstanceTagFilters: ``AWS::CodeDeploy::DeploymentGroup.OnPremisesInstanceTagFilters``.
            onPremisesTagSet: ``AWS::CodeDeploy::DeploymentGroup.OnPremisesTagSet``.
            triggerConfigurations: ``AWS::CodeDeploy::DeploymentGroup.TriggerConfigurations``.

        Stability:
            experimental
        """
        props: CfnDeploymentGroupProps = {"applicationName": application_name, "serviceRoleArn": service_role_arn}

        if alarm_configuration is not None:
            props["alarmConfiguration"] = alarm_configuration

        if auto_rollback_configuration is not None:
            props["autoRollbackConfiguration"] = auto_rollback_configuration

        if auto_scaling_groups is not None:
            props["autoScalingGroups"] = auto_scaling_groups

        if deployment is not None:
            props["deployment"] = deployment

        if deployment_config_name is not None:
            props["deploymentConfigName"] = deployment_config_name

        if deployment_group_name is not None:
            props["deploymentGroupName"] = deployment_group_name

        if deployment_style is not None:
            props["deploymentStyle"] = deployment_style

        if ec2_tag_filters is not None:
            props["ec2TagFilters"] = ec2_tag_filters

        if ec2_tag_set is not None:
            props["ec2TagSet"] = ec2_tag_set

        if load_balancer_info is not None:
            props["loadBalancerInfo"] = load_balancer_info

        if on_premises_instance_tag_filters is not None:
            props["onPremisesInstanceTagFilters"] = on_premises_instance_tag_filters

        if on_premises_tag_set is not None:
            props["onPremisesTagSet"] = on_premises_tag_set

        if trigger_configurations is not None:
            props["triggerConfigurations"] = trigger_configurations

        jsii.create(CfnDeploymentGroup, self, [scope, id, props])

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
    @jsii.member(jsii_name="deploymentGroupName")
    def deployment_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentGroupName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDeploymentGroupProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.AlarmConfigurationProperty", jsii_struct_bases=[])
    class AlarmConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-alarmconfiguration.html
        Stability:
            experimental
        """
        alarms: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.AlarmProperty"]]]
        """``CfnDeploymentGroup.AlarmConfigurationProperty.Alarms``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-alarmconfiguration.html#cfn-codedeploy-deploymentgroup-alarmconfiguration-alarms
        Stability:
            experimental
        """

        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeploymentGroup.AlarmConfigurationProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-alarmconfiguration.html#cfn-codedeploy-deploymentgroup-alarmconfiguration-enabled
        Stability:
            experimental
        """

        ignorePollAlarmFailure: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeploymentGroup.AlarmConfigurationProperty.IgnorePollAlarmFailure``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-alarmconfiguration.html#cfn-codedeploy-deploymentgroup-alarmconfiguration-ignorepollalarmfailure
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.AlarmProperty", jsii_struct_bases=[])
    class AlarmProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-alarm.html
        Stability:
            experimental
        """
        name: str
        """``CfnDeploymentGroup.AlarmProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-alarm.html#cfn-codedeploy-deploymentgroup-alarm-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.AutoRollbackConfigurationProperty", jsii_struct_bases=[])
    class AutoRollbackConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-autorollbackconfiguration.html
        Stability:
            experimental
        """
        enabled: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeploymentGroup.AutoRollbackConfigurationProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-autorollbackconfiguration.html#cfn-codedeploy-deploymentgroup-autorollbackconfiguration-enabled
        Stability:
            experimental
        """

        events: typing.List[str]
        """``CfnDeploymentGroup.AutoRollbackConfigurationProperty.Events``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-autorollbackconfiguration.html#cfn-codedeploy-deploymentgroup-autorollbackconfiguration-events
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _DeploymentProperty(jsii.compat.TypedDict, total=False):
        description: str
        """``CfnDeploymentGroup.DeploymentProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment.html#cfn-properties-codedeploy-deploymentgroup-deployment-description
        Stability:
            experimental
        """
        ignoreApplicationStopFailures: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnDeploymentGroup.DeploymentProperty.IgnoreApplicationStopFailures``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment.html#cfn-properties-codedeploy-deploymentgroup-deployment-ignoreapplicationstopfailures
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.DeploymentProperty", jsii_struct_bases=[_DeploymentProperty])
    class DeploymentProperty(_DeploymentProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment.html
        Stability:
            experimental
        """
        revision: typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.RevisionLocationProperty"]
        """``CfnDeploymentGroup.DeploymentProperty.Revision``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment.html#cfn-properties-codedeploy-deploymentgroup-deployment-revision
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.DeploymentStyleProperty", jsii_struct_bases=[])
    class DeploymentStyleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deploymentstyle.html
        Stability:
            experimental
        """
        deploymentOption: str
        """``CfnDeploymentGroup.DeploymentStyleProperty.DeploymentOption``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deploymentstyle.html#cfn-codedeploy-deploymentgroup-deploymentstyle-deploymentoption
        Stability:
            experimental
        """

        deploymentType: str
        """``CfnDeploymentGroup.DeploymentStyleProperty.DeploymentType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deploymentstyle.html#cfn-codedeploy-deploymentgroup-deploymentstyle-deploymenttype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.EC2TagFilterProperty", jsii_struct_bases=[])
    class EC2TagFilterProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-ec2tagfilter.html
        Stability:
            experimental
        """
        key: str
        """``CfnDeploymentGroup.EC2TagFilterProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-ec2tagfilter.html#cfn-codedeploy-deploymentgroup-ec2tagfilter-key
        Stability:
            experimental
        """

        type: str
        """``CfnDeploymentGroup.EC2TagFilterProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-ec2tagfilter.html#cfn-codedeploy-deploymentgroup-ec2tagfilter-type
        Stability:
            experimental
        """

        value: str
        """``CfnDeploymentGroup.EC2TagFilterProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-ec2tagfilter.html#cfn-codedeploy-deploymentgroup-ec2tagfilter-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.EC2TagSetListObjectProperty", jsii_struct_bases=[])
    class EC2TagSetListObjectProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-ec2tagsetlistobject.html
        Stability:
            experimental
        """
        ec2TagGroup: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.EC2TagFilterProperty"]]]
        """``CfnDeploymentGroup.EC2TagSetListObjectProperty.Ec2TagGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-ec2tagsetlistobject.html#cfn-codedeploy-deploymentgroup-ec2tagsetlistobject-ec2taggroup
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.EC2TagSetProperty", jsii_struct_bases=[])
    class EC2TagSetProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-ec2tagset.html
        Stability:
            experimental
        """
        ec2TagSetList: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.EC2TagSetListObjectProperty"]]]
        """``CfnDeploymentGroup.EC2TagSetProperty.Ec2TagSetList``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-ec2tagset.html#cfn-codedeploy-deploymentgroup-ec2tagset-ec2tagsetlist
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.ELBInfoProperty", jsii_struct_bases=[])
    class ELBInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-elbinfo.html
        Stability:
            experimental
        """
        name: str
        """``CfnDeploymentGroup.ELBInfoProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-elbinfo.html#cfn-codedeploy-deploymentgroup-elbinfo-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.GitHubLocationProperty", jsii_struct_bases=[])
    class GitHubLocationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision-githublocation.html
        Stability:
            experimental
        """
        commitId: str
        """``CfnDeploymentGroup.GitHubLocationProperty.CommitId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision-githublocation.html#cfn-properties-codedeploy-deploymentgroup-deployment-revision-githublocation-commitid
        Stability:
            experimental
        """

        repository: str
        """``CfnDeploymentGroup.GitHubLocationProperty.Repository``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision-githublocation.html#cfn-properties-codedeploy-deploymentgroup-deployment-revision-githublocation-repository
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.LoadBalancerInfoProperty", jsii_struct_bases=[])
    class LoadBalancerInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-loadbalancerinfo.html
        Stability:
            experimental
        """
        elbInfoList: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.ELBInfoProperty"]]]
        """``CfnDeploymentGroup.LoadBalancerInfoProperty.ElbInfoList``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-loadbalancerinfo.html#cfn-codedeploy-deploymentgroup-loadbalancerinfo-elbinfolist
        Stability:
            experimental
        """

        targetGroupInfoList: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.TargetGroupInfoProperty"]]]
        """``CfnDeploymentGroup.LoadBalancerInfoProperty.TargetGroupInfoList``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-loadbalancerinfo.html#cfn-codedeploy-deploymentgroup-loadbalancerinfo-targetgroupinfolist
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.OnPremisesTagSetListObjectProperty", jsii_struct_bases=[])
    class OnPremisesTagSetListObjectProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-onpremisestagsetlistobject.html
        Stability:
            experimental
        """
        onPremisesTagGroup: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.TagFilterProperty"]]]
        """``CfnDeploymentGroup.OnPremisesTagSetListObjectProperty.OnPremisesTagGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-onpremisestagsetlistobject.html#cfn-codedeploy-deploymentgroup-onpremisestagsetlistobject-onpremisestaggroup
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.OnPremisesTagSetProperty", jsii_struct_bases=[])
    class OnPremisesTagSetProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-onpremisestagset.html
        Stability:
            experimental
        """
        onPremisesTagSetList: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.OnPremisesTagSetListObjectProperty"]]]
        """``CfnDeploymentGroup.OnPremisesTagSetProperty.OnPremisesTagSetList``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-onpremisestagset.html#cfn-codedeploy-deploymentgroup-onpremisestagset-onpremisestagsetlist
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.RevisionLocationProperty", jsii_struct_bases=[])
    class RevisionLocationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision.html
        Stability:
            experimental
        """
        gitHubLocation: typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.GitHubLocationProperty"]
        """``CfnDeploymentGroup.RevisionLocationProperty.GitHubLocation``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision.html#cfn-properties-codedeploy-deploymentgroup-deployment-revision-githublocation
        Stability:
            experimental
        """

        revisionType: str
        """``CfnDeploymentGroup.RevisionLocationProperty.RevisionType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision.html#cfn-properties-codedeploy-deploymentgroup-deployment-revision-revisiontype
        Stability:
            experimental
        """

        s3Location: typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.S3LocationProperty"]
        """``CfnDeploymentGroup.RevisionLocationProperty.S3Location``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision.html#cfn-properties-codedeploy-deploymentgroup-deployment-revision-s3location
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _S3LocationProperty(jsii.compat.TypedDict, total=False):
        bundleType: str
        """``CfnDeploymentGroup.S3LocationProperty.BundleType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision-s3location.html#cfn-properties-codedeploy-deploymentgroup-deployment-revision-s3location-bundletype
        Stability:
            experimental
        """
        eTag: str
        """``CfnDeploymentGroup.S3LocationProperty.ETag``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision-s3location.html#cfn-properties-codedeploy-deploymentgroup-deployment-revision-s3location-etag
        Stability:
            experimental
        """
        version: str
        """``CfnDeploymentGroup.S3LocationProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision-s3location.html#cfn-properties-codedeploy-deploymentgroup-deployment-revision-s3location-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.S3LocationProperty", jsii_struct_bases=[_S3LocationProperty])
    class S3LocationProperty(_S3LocationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision-s3location.html
        Stability:
            experimental
        """
        bucket: str
        """``CfnDeploymentGroup.S3LocationProperty.Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision-s3location.html#cfn-properties-codedeploy-deploymentgroup-deployment-revision-s3location-bucket
        Stability:
            experimental
        """

        key: str
        """``CfnDeploymentGroup.S3LocationProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-deployment-revision-s3location.html#cfn-properties-codedeploy-deploymentgroup-deployment-revision-s3location-key
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.TagFilterProperty", jsii_struct_bases=[])
    class TagFilterProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-tagfilter.html
        Stability:
            experimental
        """
        key: str
        """``CfnDeploymentGroup.TagFilterProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-tagfilter.html#cfn-codedeploy-deploymentgroup-tagfilter-key
        Stability:
            experimental
        """

        type: str
        """``CfnDeploymentGroup.TagFilterProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-tagfilter.html#cfn-codedeploy-deploymentgroup-tagfilter-type
        Stability:
            experimental
        """

        value: str
        """``CfnDeploymentGroup.TagFilterProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-tagfilter.html#cfn-codedeploy-deploymentgroup-tagfilter-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.TargetGroupInfoProperty", jsii_struct_bases=[])
    class TargetGroupInfoProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-targetgroupinfo.html
        Stability:
            experimental
        """
        name: str
        """``CfnDeploymentGroup.TargetGroupInfoProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-targetgroupinfo.html#cfn-codedeploy-deploymentgroup-targetgroupinfo-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroup.TriggerConfigProperty", jsii_struct_bases=[])
    class TriggerConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-triggerconfig.html
        Stability:
            experimental
        """
        triggerEvents: typing.List[str]
        """``CfnDeploymentGroup.TriggerConfigProperty.TriggerEvents``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-triggerconfig.html#cfn-codedeploy-deploymentgroup-triggerconfig-triggerevents
        Stability:
            experimental
        """

        triggerName: str
        """``CfnDeploymentGroup.TriggerConfigProperty.TriggerName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-triggerconfig.html#cfn-codedeploy-deploymentgroup-triggerconfig-triggername
        Stability:
            experimental
        """

        triggerTargetArn: str
        """``CfnDeploymentGroup.TriggerConfigProperty.TriggerTargetArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codedeploy-deploymentgroup-triggerconfig.html#cfn-codedeploy-deploymentgroup-triggerconfig-triggertargetarn
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnDeploymentGroupProps(jsii.compat.TypedDict, total=False):
    alarmConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.AlarmConfigurationProperty"]
    """``AWS::CodeDeploy::DeploymentGroup.AlarmConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-alarmconfiguration
    Stability:
        experimental
    """
    autoRollbackConfiguration: typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.AutoRollbackConfigurationProperty"]
    """``AWS::CodeDeploy::DeploymentGroup.AutoRollbackConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-autorollbackconfiguration
    Stability:
        experimental
    """
    autoScalingGroups: typing.List[str]
    """``AWS::CodeDeploy::DeploymentGroup.AutoScalingGroups``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-autoscalinggroups
    Stability:
        experimental
    """
    deployment: typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.DeploymentProperty"]
    """``AWS::CodeDeploy::DeploymentGroup.Deployment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-deployment
    Stability:
        experimental
    """
    deploymentConfigName: str
    """``AWS::CodeDeploy::DeploymentGroup.DeploymentConfigName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-deploymentconfigname
    Stability:
        experimental
    """
    deploymentGroupName: str
    """``AWS::CodeDeploy::DeploymentGroup.DeploymentGroupName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-deploymentgroupname
    Stability:
        experimental
    """
    deploymentStyle: typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.DeploymentStyleProperty"]
    """``AWS::CodeDeploy::DeploymentGroup.DeploymentStyle``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-deploymentstyle
    Stability:
        experimental
    """
    ec2TagFilters: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.EC2TagFilterProperty"]]]
    """``AWS::CodeDeploy::DeploymentGroup.Ec2TagFilters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-ec2tagfilters
    Stability:
        experimental
    """
    ec2TagSet: typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.EC2TagSetProperty"]
    """``AWS::CodeDeploy::DeploymentGroup.Ec2TagSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-ec2tagset
    Stability:
        experimental
    """
    loadBalancerInfo: typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.LoadBalancerInfoProperty"]
    """``AWS::CodeDeploy::DeploymentGroup.LoadBalancerInfo``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-loadbalancerinfo
    Stability:
        experimental
    """
    onPremisesInstanceTagFilters: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.TagFilterProperty"]]]
    """``AWS::CodeDeploy::DeploymentGroup.OnPremisesInstanceTagFilters``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-onpremisesinstancetagfilters
    Stability:
        experimental
    """
    onPremisesTagSet: typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.OnPremisesTagSetProperty"]
    """``AWS::CodeDeploy::DeploymentGroup.OnPremisesTagSet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-onpremisestagset
    Stability:
        experimental
    """
    triggerConfigurations: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnDeploymentGroup.TriggerConfigProperty"]]]
    """``AWS::CodeDeploy::DeploymentGroup.TriggerConfigurations``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-triggerconfigurations
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.CfnDeploymentGroupProps", jsii_struct_bases=[_CfnDeploymentGroupProps])
class CfnDeploymentGroupProps(_CfnDeploymentGroupProps):
    """Properties for defining a ``AWS::CodeDeploy::DeploymentGroup``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html
    Stability:
        experimental
    """
    applicationName: str
    """``AWS::CodeDeploy::DeploymentGroup.ApplicationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-applicationname
    Stability:
        experimental
    """

    serviceRoleArn: str
    """``AWS::CodeDeploy::DeploymentGroup.ServiceRoleArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html#cfn-codedeploy-deploymentgroup-servicerolearn
    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-codedeploy.ILambdaApplication")
class ILambdaApplication(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """Represents a reference to a CodeDeploy Application deploying to AWS Lambda.

    If you're managing the Application alongside the rest of your CDK resources,
    use the {@link LambdaApplication} class.

    If you want to reference an already existing Application,
    or one defined in a different CDK Stack,
    use the {@link LambdaApplication#import} method.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ILambdaApplicationProxy

    @property
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...


class _ILambdaApplicationProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """Represents a reference to a CodeDeploy Application deploying to AWS Lambda.

    If you're managing the Application alongside the rest of your CDK resources,
    use the {@link LambdaApplication} class.

    If you want to reference an already existing Application,
    or one defined in a different CDK Stack,
    use the {@link LambdaApplication#import} method.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codedeploy.ILambdaApplication"
    @property
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "applicationArn")

    @property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "applicationName")


@jsii.interface(jsii_type="@aws-cdk/aws-codedeploy.ILambdaDeploymentConfig")
class ILambdaDeploymentConfig(jsii.compat.Protocol):
    """The Deployment Configuration of a Lambda Deployment Group. The default, pre-defined Configurations are available as constants on the {@link LambdaDeploymentConfig} class (``LambdaDeploymentConfig.AllAtOnce``, ``LambdaDeploymentConfig.Canary10Percent30Minutes``, etc.).

    Note: CloudFormation does not currently support creating custom lambda configs outside
    of using a custom resource. You can import custom deployment config created outside the
    CDK or via a custom resource with {@link LambdaDeploymentConfig#import}.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ILambdaDeploymentConfigProxy

    @property
    @jsii.member(jsii_name="deploymentConfigArn")
    def deployment_config_arn(self) -> str:
        """
        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="deploymentConfigName")
    def deployment_config_name(self) -> str:
        """
        Stability:
            experimental
        """
        ...


class _ILambdaDeploymentConfigProxy():
    """The Deployment Configuration of a Lambda Deployment Group. The default, pre-defined Configurations are available as constants on the {@link LambdaDeploymentConfig} class (``LambdaDeploymentConfig.AllAtOnce``, ``LambdaDeploymentConfig.Canary10Percent30Minutes``, etc.).

    Note: CloudFormation does not currently support creating custom lambda configs outside
    of using a custom resource. You can import custom deployment config created outside the
    CDK or via a custom resource with {@link LambdaDeploymentConfig#import}.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codedeploy.ILambdaDeploymentConfig"
    @property
    @jsii.member(jsii_name="deploymentConfigArn")
    def deployment_config_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentConfigArn")

    @property
    @jsii.member(jsii_name="deploymentConfigName")
    def deployment_config_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentConfigName")


@jsii.interface(jsii_type="@aws-cdk/aws-codedeploy.ILambdaDeploymentGroup")
class ILambdaDeploymentGroup(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """Interface for a Lambda deployment groups.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _ILambdaDeploymentGroupProxy

    @property
    @jsii.member(jsii_name="application")
    def application(self) -> "ILambdaApplication":
        """The reference to the CodeDeploy Lambda Application that this Deployment Group belongs to.

        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="deploymentGroupArn")
    def deployment_group_arn(self) -> str:
        """The ARN of this Deployment Group.

        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="deploymentGroupName")
    def deployment_group_name(self) -> str:
        """The physical name of the CodeDeploy Deployment Group.

        Stability:
            experimental
        attribute:
            true
        """
        ...


class _ILambdaDeploymentGroupProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """Interface for a Lambda deployment groups.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codedeploy.ILambdaDeploymentGroup"
    @property
    @jsii.member(jsii_name="application")
    def application(self) -> "ILambdaApplication":
        """The reference to the CodeDeploy Lambda Application that this Deployment Group belongs to.

        Stability:
            experimental
        """
        return jsii.get(self, "application")

    @property
    @jsii.member(jsii_name="deploymentGroupArn")
    def deployment_group_arn(self) -> str:
        """The ARN of this Deployment Group.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "deploymentGroupArn")

    @property
    @jsii.member(jsii_name="deploymentGroupName")
    def deployment_group_name(self) -> str:
        """The physical name of the CodeDeploy Deployment Group.

        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "deploymentGroupName")


@jsii.interface(jsii_type="@aws-cdk/aws-codedeploy.IServerApplication")
class IServerApplication(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """Represents a reference to a CodeDeploy Application deploying to EC2/on-premise instances.

    If you're managing the Application alongside the rest of your CDK resources,
    use the {@link ServerApplication} class.

    If you want to reference an already existing Application,
    or one defined in a different CDK Stack,
    use the {@link #import} method.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IServerApplicationProxy

    @property
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IServerApplicationProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """Represents a reference to a CodeDeploy Application deploying to EC2/on-premise instances.

    If you're managing the Application alongside the rest of your CDK resources,
    use the {@link ServerApplication} class.

    If you want to reference an already existing Application,
    or one defined in a different CDK Stack,
    use the {@link #import} method.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codedeploy.IServerApplication"
    @property
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "applicationArn")

    @property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "applicationName")


@jsii.interface(jsii_type="@aws-cdk/aws-codedeploy.IServerDeploymentConfig")
class IServerDeploymentConfig(jsii.compat.Protocol):
    """The Deployment Configuration of an EC2/on-premise Deployment Group. The default, pre-defined Configurations are available as constants on the {@link ServerDeploymentConfig} class (``ServerDeploymentConfig.HalfAtATime``, ``ServerDeploymentConfig.AllAtOnce``, etc.). To create a custom Deployment Configuration, instantiate the {@link ServerDeploymentConfig} Construct.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IServerDeploymentConfigProxy

    @property
    @jsii.member(jsii_name="deploymentConfigArn")
    def deployment_config_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="deploymentConfigName")
    def deployment_config_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...


class _IServerDeploymentConfigProxy():
    """The Deployment Configuration of an EC2/on-premise Deployment Group. The default, pre-defined Configurations are available as constants on the {@link ServerDeploymentConfig} class (``ServerDeploymentConfig.HalfAtATime``, ``ServerDeploymentConfig.AllAtOnce``, etc.). To create a custom Deployment Configuration, instantiate the {@link ServerDeploymentConfig} Construct.

    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codedeploy.IServerDeploymentConfig"
    @property
    @jsii.member(jsii_name="deploymentConfigArn")
    def deployment_config_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "deploymentConfigArn")

    @property
    @jsii.member(jsii_name="deploymentConfigName")
    def deployment_config_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "deploymentConfigName")


@jsii.interface(jsii_type="@aws-cdk/aws-codedeploy.IServerDeploymentGroup")
class IServerDeploymentGroup(aws_cdk.cdk.IResource, jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IServerDeploymentGroupProxy

    @property
    @jsii.member(jsii_name="application")
    def application(self) -> "IServerApplication":
        """
        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="deploymentConfig")
    def deployment_config(self) -> "IServerDeploymentConfig":
        """
        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="deploymentGroupArn")
    def deployment_group_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="deploymentGroupName")
    def deployment_group_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        ...

    @property
    @jsii.member(jsii_name="autoScalingGroups")
    def auto_scaling_groups(self) -> typing.Optional[typing.List[aws_cdk.aws_autoscaling.AutoScalingGroup]]:
        """
        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """
        Stability:
            experimental
        """
        ...


class _IServerDeploymentGroupProxy(jsii.proxy_for(aws_cdk.cdk.IResource)):
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-codedeploy.IServerDeploymentGroup"
    @property
    @jsii.member(jsii_name="application")
    def application(self) -> "IServerApplication":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "application")

    @property
    @jsii.member(jsii_name="deploymentConfig")
    def deployment_config(self) -> "IServerDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentConfig")

    @property
    @jsii.member(jsii_name="deploymentGroupArn")
    def deployment_group_arn(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "deploymentGroupArn")

    @property
    @jsii.member(jsii_name="deploymentGroupName")
    def deployment_group_name(self) -> str:
        """
        Stability:
            experimental
        attribute:
            true
        """
        return jsii.get(self, "deploymentGroupName")

    @property
    @jsii.member(jsii_name="autoScalingGroups")
    def auto_scaling_groups(self) -> typing.Optional[typing.List[aws_cdk.aws_autoscaling.AutoScalingGroup]]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "autoScalingGroups")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "role")


class InstanceTagSet(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codedeploy.InstanceTagSet"):
    """Represents a set of instance tag groups. An instance will match a set if it matches all of the groups in the set - in other words, sets follow 'and' semantics. You can have a maximum of 3 tag groups inside a set.

    Stability:
        experimental
    """
    def __init__(self, *instance_tag_groups: typing.Mapping[str,typing.List[str]]) -> None:
        """
        Arguments:
            instanceTagGroups: -

        Stability:
            experimental
        """
        jsii.create(InstanceTagSet, self, [*instance_tag_groups])

    @property
    @jsii.member(jsii_name="instanceTagGroups")
    def instance_tag_groups(self) -> typing.List[typing.Mapping[str,typing.List[str]]]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "instanceTagGroups")


@jsii.implements(ILambdaApplication)
class LambdaApplication(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codedeploy.LambdaApplication"):
    """A CodeDeploy Application that deploys to an AWS Lambda function.

    Stability:
        experimental
    resource:
        AWS::CodeDeploy::Application
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, application_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            applicationName: The physical, human-readable name of the CodeDeploy Application. Default: an auto-generated name will be used

        Stability:
            experimental
        """
        props: LambdaApplicationProps = {}

        if application_name is not None:
            props["applicationName"] = application_name

        jsii.create(LambdaApplication, self, [scope, id, props])

    @jsii.member(jsii_name="fromLambdaApplicationName")
    @classmethod
    def from_lambda_application_name(cls, scope: aws_cdk.cdk.Construct, id: str, lambda_application_name: str) -> "ILambdaApplication":
        """Import an Application defined either outside the CDK, or in a different CDK Stack and exported using the {@link ILambdaApplication#export} method.

        Arguments:
            scope: the parent Construct for this new Construct.
            id: the logical ID of this new Construct.
            lambdaApplicationName: the name of the application to import.

        Returns:
            a Construct representing a reference to an existing Application

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromLambdaApplicationName", [scope, id, lambda_application_name])

    @property
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "applicationArn")

    @property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "applicationName")


@jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.LambdaApplicationProps", jsii_struct_bases=[])
class LambdaApplicationProps(jsii.compat.TypedDict, total=False):
    """Construction properties for {@link LambdaApplication}.

    Stability:
        experimental
    """
    applicationName: str
    """The physical, human-readable name of the CodeDeploy Application.

    Default:
        an auto-generated name will be used

    Stability:
        experimental
    """

class LambdaDeploymentConfig(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codedeploy.LambdaDeploymentConfig"):
    """A custom Deployment Configuration for a Lambda Deployment Group.

    Note: This class currently stands as namespaced container of the default configurations
    until CloudFormation supports custom Lambda Deployment Configs. Until then it is closed
    (private constructor) and does not extend {@link cdk.Construct}

    Stability:
        experimental
    resource:
        AWS::CodeDeploy::DeploymentConfig
    """
    @jsii.member(jsii_name="import")
    @classmethod
    def import_(cls, _scope: aws_cdk.cdk.Construct, _id: str, *, deployment_config_name: str) -> "ILambdaDeploymentConfig":
        """Import a custom Deployment Configuration for a Lambda Deployment Group defined outside the CDK.

        Arguments:
            _scope: the parent Construct for this new Construct.
            _id: the logical ID of this new Construct.
            props: the properties of the referenced custom Deployment Configuration.
            deploymentConfigName: The physical, human-readable name of the custom CodeDeploy Lambda Deployment Configuration that we are referencing.

        Returns:
            a Construct representing a reference to an existing custom Deployment Configuration

        Stability:
            experimental
        """
        props: LambdaDeploymentConfigImportProps = {"deploymentConfigName": deployment_config_name}

        return jsii.sinvoke(cls, "import", [_scope, _id, props])

    @classproperty
    @jsii.member(jsii_name="AllAtOnce")
    def ALL_AT_ONCE(cls) -> "ILambdaDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "AllAtOnce")

    @classproperty
    @jsii.member(jsii_name="Canary10Percent10Minutes")
    def CANARY10_PERCENT10_MINUTES(cls) -> "ILambdaDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Canary10Percent10Minutes")

    @classproperty
    @jsii.member(jsii_name="Canary10Percent15Minutes")
    def CANARY10_PERCENT15_MINUTES(cls) -> "ILambdaDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Canary10Percent15Minutes")

    @classproperty
    @jsii.member(jsii_name="Canary10Percent30Minutes")
    def CANARY10_PERCENT30_MINUTES(cls) -> "ILambdaDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Canary10Percent30Minutes")

    @classproperty
    @jsii.member(jsii_name="Canary10Percent5Minutes")
    def CANARY10_PERCENT5_MINUTES(cls) -> "ILambdaDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Canary10Percent5Minutes")

    @classproperty
    @jsii.member(jsii_name="Linear10PercentEvery10Minutes")
    def LINEAR10_PERCENT_EVERY10_MINUTES(cls) -> "ILambdaDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Linear10PercentEvery10Minutes")

    @classproperty
    @jsii.member(jsii_name="Linear10PercentEvery1Minute")
    def LINEAR10_PERCENT_EVERY1_MINUTE(cls) -> "ILambdaDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Linear10PercentEvery1Minute")

    @classproperty
    @jsii.member(jsii_name="Linear10PercentEvery2Minutes")
    def LINEAR10_PERCENT_EVERY2_MINUTES(cls) -> "ILambdaDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Linear10PercentEvery2Minutes")

    @classproperty
    @jsii.member(jsii_name="Linear10PercentEvery3Minutes")
    def LINEAR10_PERCENT_EVERY3_MINUTES(cls) -> "ILambdaDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "Linear10PercentEvery3Minutes")


@jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.LambdaDeploymentConfigImportProps", jsii_struct_bases=[])
class LambdaDeploymentConfigImportProps(jsii.compat.TypedDict):
    """Properties of a reference to a CodeDeploy Lambda Deployment Configuration.

    See:
        LambdaDeploymentConfig#export
    Stability:
        experimental
    """
    deploymentConfigName: str
    """The physical, human-readable name of the custom CodeDeploy Lambda Deployment Configuration that we are referencing.

    Stability:
        experimental
    """

@jsii.implements(ILambdaDeploymentGroup)
class LambdaDeploymentGroup(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codedeploy.LambdaDeploymentGroup"):
    """
    Stability:
        experimental
    resource:
        AWS::CodeDeploy::DeploymentGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, alias: aws_cdk.aws_lambda.Alias, alarms: typing.Optional[typing.List[aws_cdk.aws_cloudwatch.IAlarm]]=None, application: typing.Optional["ILambdaApplication"]=None, auto_rollback: typing.Optional["AutoRollbackConfig"]=None, deployment_config: typing.Optional["ILambdaDeploymentConfig"]=None, deployment_group_name: typing.Optional[str]=None, ignore_poll_alarms_failure: typing.Optional[bool]=None, post_hook: typing.Optional[aws_cdk.aws_lambda.IFunction]=None, pre_hook: typing.Optional[aws_cdk.aws_lambda.IFunction]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            alias: Lambda Alias to shift traffic. Updating the version of the alias will trigger a CodeDeploy deployment. [disable-awslint:ref-via-interface] since we need to modify the alias CFN resource update policy
            alarms: The CloudWatch alarms associated with this Deployment Group. CodeDeploy will stop (and optionally roll back) a deployment if during it any of the alarms trigger. Alarms can also be added after the Deployment Group is created using the {@link #addAlarm} method. Default: []
            application: The reference to the CodeDeploy Lambda Application that this Deployment Group belongs to. Default: - One will be created for you.
            autoRollback: The auto-rollback configuration for this Deployment Group. Default: - default AutoRollbackConfig.
            deploymentConfig: The Deployment Configuration this Deployment Group uses. Default: LambdaDeploymentConfig#AllAtOnce
            deploymentGroupName: The physical, human-readable name of the CodeDeploy Deployment Group. Default: - An auto-generated name will be used.
            ignorePollAlarmsFailure: Whether to continue a deployment even if fetching the alarm status from CloudWatch failed. Default: false
            postHook: The Lambda function to run after traffic routing starts. Default: - None.
            preHook: The Lambda function to run before traffic routing starts. Default: - None.
            role: The service Role of this Deployment Group. Default: - A new Role will be created.

        Stability:
            experimental
        """
        props: LambdaDeploymentGroupProps = {"alias": alias}

        if alarms is not None:
            props["alarms"] = alarms

        if application is not None:
            props["application"] = application

        if auto_rollback is not None:
            props["autoRollback"] = auto_rollback

        if deployment_config is not None:
            props["deploymentConfig"] = deployment_config

        if deployment_group_name is not None:
            props["deploymentGroupName"] = deployment_group_name

        if ignore_poll_alarms_failure is not None:
            props["ignorePollAlarmsFailure"] = ignore_poll_alarms_failure

        if post_hook is not None:
            props["postHook"] = post_hook

        if pre_hook is not None:
            props["preHook"] = pre_hook

        if role is not None:
            props["role"] = role

        jsii.create(LambdaDeploymentGroup, self, [scope, id, props])

    @jsii.member(jsii_name="fromLambdaDeploymentGroupAttributes")
    @classmethod
    def from_lambda_deployment_group_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, application: "ILambdaApplication", deployment_group_name: str) -> "ILambdaDeploymentGroup":
        """Import an Lambda Deployment Group defined either outside the CDK, or in a different CDK Stack and exported using the {@link #export} method.

        Arguments:
            scope: the parent Construct for this new Construct.
            id: the logical ID of this new Construct.
            attrs: the properties of the referenced Deployment Group.
            application: The reference to the CodeDeploy Lambda Application that this Deployment Group belongs to.
            deploymentGroupName: The physical, human-readable name of the CodeDeploy Lambda Deployment Group that we are referencing.

        Returns:
            a Construct representing a reference to an existing Deployment Group

        Stability:
            experimental
        """
        attrs: LambdaDeploymentGroupAttributes = {"application": application, "deploymentGroupName": deployment_group_name}

        return jsii.sinvoke(cls, "fromLambdaDeploymentGroupAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="addAlarm")
    def add_alarm(self, alarm: aws_cdk.aws_cloudwatch.IAlarm) -> None:
        """Associates an additional alarm with this Deployment Group.

        Arguments:
            alarm: the alarm to associate with this Deployment Group.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAlarm", [alarm])

    @jsii.member(jsii_name="addPostHook")
    def add_post_hook(self, post_hook: aws_cdk.aws_lambda.IFunction) -> None:
        """Associate a function to run after deployment completes.

        Arguments:
            postHook: function to run after deployment completes.

        Stability:
            experimental
        throws:
            an error if a post-hook function is already configured
        """
        return jsii.invoke(self, "addPostHook", [post_hook])

    @jsii.member(jsii_name="addPreHook")
    def add_pre_hook(self, pre_hook: aws_cdk.aws_lambda.IFunction) -> None:
        """Associate a function to run before deployment begins.

        Arguments:
            preHook: function to run before deployment beings.

        Stability:
            experimental
        throws:
            an error if a pre-hook function is already configured
        """
        return jsii.invoke(self, "addPreHook", [pre_hook])

    @jsii.member(jsii_name="grantPutLifecycleEventHookExecutionStatus")
    def grant_put_lifecycle_event_hook_execution_status(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        """Grant a principal permission to codedeploy:PutLifecycleEventHookExecutionStatus on this deployment group resource.

        Arguments:
            grantee: to grant permission to.

        Stability:
            experimental
        """
        return jsii.invoke(self, "grantPutLifecycleEventHookExecutionStatus", [grantee])

    @property
    @jsii.member(jsii_name="application")
    def application(self) -> "ILambdaApplication":
        """The reference to the CodeDeploy Lambda Application that this Deployment Group belongs to.

        Stability:
            experimental
        """
        return jsii.get(self, "application")

    @property
    @jsii.member(jsii_name="deploymentGroupArn")
    def deployment_group_arn(self) -> str:
        """The ARN of this Deployment Group.

        Stability:
            experimental
        """
        return jsii.get(self, "deploymentGroupArn")

    @property
    @jsii.member(jsii_name="deploymentGroupName")
    def deployment_group_name(self) -> str:
        """The physical name of the CodeDeploy Deployment Group.

        Stability:
            experimental
        """
        return jsii.get(self, "deploymentGroupName")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "role")


@jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.LambdaDeploymentGroupAttributes", jsii_struct_bases=[])
class LambdaDeploymentGroupAttributes(jsii.compat.TypedDict):
    """Properties of a reference to a CodeDeploy Lambda Deployment Group.

    See:
        ILambdaDeploymentGroup#export
    Stability:
        experimental
    """
    application: "ILambdaApplication"
    """The reference to the CodeDeploy Lambda Application that this Deployment Group belongs to.

    Stability:
        experimental
    """

    deploymentGroupName: str
    """The physical, human-readable name of the CodeDeploy Lambda Deployment Group that we are referencing.

    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _LambdaDeploymentGroupProps(jsii.compat.TypedDict, total=False):
    alarms: typing.List[aws_cdk.aws_cloudwatch.IAlarm]
    """The CloudWatch alarms associated with this Deployment Group. CodeDeploy will stop (and optionally roll back) a deployment if during it any of the alarms trigger.

    Alarms can also be added after the Deployment Group is created using the {@link #addAlarm} method.

    Default:
        []

    See:
        https://docs.aws.amazon.com/codedeploy/latest/userguide/monitoring-create-alarms.html
    Stability:
        experimental
    """
    application: "ILambdaApplication"
    """The reference to the CodeDeploy Lambda Application that this Deployment Group belongs to.

    Default:
        - One will be created for you.

    Stability:
        experimental
    """
    autoRollback: "AutoRollbackConfig"
    """The auto-rollback configuration for this Deployment Group.

    Default:
        - default AutoRollbackConfig.

    Stability:
        experimental
    """
    deploymentConfig: "ILambdaDeploymentConfig"
    """The Deployment Configuration this Deployment Group uses.

    Default:
        LambdaDeploymentConfig#AllAtOnce

    Stability:
        experimental
    """
    deploymentGroupName: str
    """The physical, human-readable name of the CodeDeploy Deployment Group.

    Default:
        - An auto-generated name will be used.

    Stability:
        experimental
    """
    ignorePollAlarmsFailure: bool
    """Whether to continue a deployment even if fetching the alarm status from CloudWatch failed.

    Default:
        false

    Stability:
        experimental
    """
    postHook: aws_cdk.aws_lambda.IFunction
    """The Lambda function to run after traffic routing starts.

    Default:
        - None.

    Stability:
        experimental
    """
    preHook: aws_cdk.aws_lambda.IFunction
    """The Lambda function to run before traffic routing starts.

    Default:
        - None.

    Stability:
        experimental
    """
    role: aws_cdk.aws_iam.IRole
    """The service Role of this Deployment Group.

    Default:
        - A new Role will be created.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.LambdaDeploymentGroupProps", jsii_struct_bases=[_LambdaDeploymentGroupProps])
class LambdaDeploymentGroupProps(_LambdaDeploymentGroupProps):
    """Construction properties for {@link LambdaDeploymentGroup}.

    Stability:
        experimental
    """
    alias: aws_cdk.aws_lambda.Alias
    """Lambda Alias to shift traffic. Updating the version of the alias will trigger a CodeDeploy deployment.

    [disable-awslint:ref-via-interface] since we need to modify the alias CFN resource update policy

    Stability:
        experimental
    """

class LoadBalancer(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-codedeploy.LoadBalancer"):
    """An interface of an abstract load balancer, as needed by CodeDeploy. Create instances using the static factory methods: {@link #classic}, {@link #application} and {@link #network}.

    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _LoadBalancerProxy

    def __init__(self) -> None:
        jsii.create(LoadBalancer, self, [])

    @jsii.member(jsii_name="application")
    @classmethod
    def application(cls, alb_target_group: aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup) -> "LoadBalancer":
        """Creates a new CodeDeploy load balancer from an Application Load Balancer Target Group.

        Arguments:
            albTargetGroup: an ALB Target Group.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "application", [alb_target_group])

    @jsii.member(jsii_name="classic")
    @classmethod
    def classic(cls, load_balancer: aws_cdk.aws_elasticloadbalancing.LoadBalancer) -> "LoadBalancer":
        """Creates a new CodeDeploy load balancer from a Classic ELB Load Balancer.

        Arguments:
            loadBalancer: a classic ELB Load Balancer.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "classic", [load_balancer])

    @jsii.member(jsii_name="network")
    @classmethod
    def network(cls, nlb_target_group: aws_cdk.aws_elasticloadbalancingv2.NetworkTargetGroup) -> "LoadBalancer":
        """Creates a new CodeDeploy load balancer from a Network Load Balancer Target Group.

        Arguments:
            nlbTargetGroup: an NLB Target Group.

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "network", [nlb_target_group])

    @property
    @jsii.member(jsii_name="generation")
    @abc.abstractmethod
    def generation(self) -> "LoadBalancerGeneration":
        """
        Stability:
            experimental
        """
        ...

    @property
    @jsii.member(jsii_name="name")
    @abc.abstractmethod
    def name(self) -> str:
        """
        Stability:
            experimental
        """
        ...


class _LoadBalancerProxy(LoadBalancer):
    @property
    @jsii.member(jsii_name="generation")
    def generation(self) -> "LoadBalancerGeneration":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "generation")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "name")


@jsii.enum(jsii_type="@aws-cdk/aws-codedeploy.LoadBalancerGeneration")
class LoadBalancerGeneration(enum.Enum):
    """The generations of AWS load balancing solutions.

    Stability:
        experimental
    """
    FIRST = "FIRST"
    """The first generation (ELB Classic).

    Stability:
        experimental
    """
    SECOND = "SECOND"
    """The second generation (ALB and NLB).

    Stability:
        experimental
    """

class MinimumHealthyHosts(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codedeploy.MinimumHealthyHosts"):
    """Minimum number of healthy hosts for a server deployment.

    Stability:
        experimental
    """
    @jsii.member(jsii_name="count")
    @classmethod
    def count(cls, value: jsii.Number) -> "MinimumHealthyHosts":
        """The minimum healhty hosts threshold expressed as an absolute number.

        Arguments:
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "count", [value])

    @jsii.member(jsii_name="percentage")
    @classmethod
    def percentage(cls, value: jsii.Number) -> "MinimumHealthyHosts":
        """The minmum healhty hosts threshold expressed as a percentage of the fleet.

        Arguments:
            value: -

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "percentage", [value])

    @property
    @jsii.member(jsii_name="json")
    def json(self) -> "CfnDeploymentConfig.MinimumHealthyHostsProperty":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "json")


@jsii.implements(IServerApplication)
class ServerApplication(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codedeploy.ServerApplication"):
    """A CodeDeploy Application that deploys to EC2/on-premise instances.

    Stability:
        experimental
    resource:
        AWS::CodeDeploy::Application
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, application_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            applicationName: The physical, human-readable name of the CodeDeploy Application. Default: an auto-generated name will be used

        Stability:
            experimental
        """
        props: ServerApplicationProps = {}

        if application_name is not None:
            props["applicationName"] = application_name

        jsii.create(ServerApplication, self, [scope, id, props])

    @jsii.member(jsii_name="fromServerApplicationName")
    @classmethod
    def from_server_application_name(cls, scope: aws_cdk.cdk.Construct, id: str, server_application_name: str) -> "IServerApplication":
        """Import an Application defined either outside the CDK, or in a different CDK Stack and exported using the {@link #export} method.

        Arguments:
            scope: the parent Construct for this new Construct.
            id: the logical ID of this new Construct.
            serverApplicationName: the name of the application to import.

        Returns:
            a Construct representing a reference to an existing Application

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromServerApplicationName", [scope, id, server_application_name])

    @property
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "applicationArn")

    @property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "applicationName")


@jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.ServerApplicationProps", jsii_struct_bases=[])
class ServerApplicationProps(jsii.compat.TypedDict, total=False):
    """Construction properties for {@link ServerApplication}.

    Stability:
        experimental
    """
    applicationName: str
    """The physical, human-readable name of the CodeDeploy Application.

    Default:
        an auto-generated name will be used

    Stability:
        experimental
    """

@jsii.implements(IServerDeploymentConfig)
class ServerDeploymentConfig(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codedeploy.ServerDeploymentConfig"):
    """A custom Deployment Configuration for an EC2/on-premise Deployment Group.

    Stability:
        experimental
    resource:
        AWS::CodeDeploy::DeploymentConfig
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, minimum_healthy_hosts: "MinimumHealthyHosts", deployment_config_name: typing.Optional[str]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            minimumHealthyHosts: Minimum number of healthy hosts.
            deploymentConfigName: The physical, human-readable name of the Deployment Configuration. Default: a name will be auto-generated

        Stability:
            experimental
        """
        props: ServerDeploymentConfigProps = {"minimumHealthyHosts": minimum_healthy_hosts}

        if deployment_config_name is not None:
            props["deploymentConfigName"] = deployment_config_name

        jsii.create(ServerDeploymentConfig, self, [scope, id, props])

    @jsii.member(jsii_name="fromServerDeploymentConfigName")
    @classmethod
    def from_server_deployment_config_name(cls, scope: aws_cdk.cdk.Construct, id: str, server_deployment_config_name: str) -> "IServerDeploymentConfig":
        """Import a custom Deployment Configuration for an EC2/on-premise Deployment Group defined either outside the CDK, or in a different CDK Stack and exported using the {@link #export} method.

        Arguments:
            scope: the parent Construct for this new Construct.
            id: the logical ID of this new Construct.
            serverDeploymentConfigName: the properties of the referenced custom Deployment Configuration.

        Returns:
            a Construct representing a reference to an existing custom Deployment Configuration

        Stability:
            experimental
        """
        return jsii.sinvoke(cls, "fromServerDeploymentConfigName", [scope, id, server_deployment_config_name])

    @classproperty
    @jsii.member(jsii_name="AllAtOnce")
    def ALL_AT_ONCE(cls) -> "IServerDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "AllAtOnce")

    @classproperty
    @jsii.member(jsii_name="HalfAtATime")
    def HALF_AT_A_TIME(cls) -> "IServerDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "HalfAtATime")

    @classproperty
    @jsii.member(jsii_name="OneAtATime")
    def ONE_AT_A_TIME(cls) -> "IServerDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.sget(cls, "OneAtATime")

    @property
    @jsii.member(jsii_name="deploymentConfigArn")
    def deployment_config_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentConfigArn")

    @property
    @jsii.member(jsii_name="deploymentConfigName")
    def deployment_config_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentConfigName")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ServerDeploymentConfigProps(jsii.compat.TypedDict, total=False):
    deploymentConfigName: str
    """The physical, human-readable name of the Deployment Configuration.

    Default:
        a name will be auto-generated

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.ServerDeploymentConfigProps", jsii_struct_bases=[_ServerDeploymentConfigProps])
class ServerDeploymentConfigProps(_ServerDeploymentConfigProps):
    """Construction properties of {@link ServerDeploymentConfig}.

    Stability:
        experimental
    """
    minimumHealthyHosts: "MinimumHealthyHosts"
    """Minimum number of healthy hosts.

    Stability:
        experimental
    """

@jsii.implements(IServerDeploymentGroup)
class ServerDeploymentGroup(aws_cdk.cdk.Resource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-codedeploy.ServerDeploymentGroup"):
    """A CodeDeploy Deployment Group that deploys to EC2/on-premise instances.

    Stability:
        experimental
    resource:
        AWS::CodeDeploy::DeploymentGroup
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, alarms: typing.Optional[typing.List[aws_cdk.aws_cloudwatch.IAlarm]]=None, application: typing.Optional["IServerApplication"]=None, auto_rollback: typing.Optional["AutoRollbackConfig"]=None, auto_scaling_groups: typing.Optional[typing.List[aws_cdk.aws_autoscaling.AutoScalingGroup]]=None, deployment_config: typing.Optional["IServerDeploymentConfig"]=None, deployment_group_name: typing.Optional[str]=None, ec2_instance_tags: typing.Optional["InstanceTagSet"]=None, ignore_poll_alarms_failure: typing.Optional[bool]=None, install_agent: typing.Optional[bool]=None, load_balancer: typing.Optional["LoadBalancer"]=None, on_premise_instance_tags: typing.Optional["InstanceTagSet"]=None, role: typing.Optional[aws_cdk.aws_iam.IRole]=None) -> None:
        """
        Arguments:
            scope: -
            id: -
            props: -
            alarms: The CloudWatch alarms associated with this Deployment Group. CodeDeploy will stop (and optionally roll back) a deployment if during it any of the alarms trigger. Alarms can also be added after the Deployment Group is created using the {@link #addAlarm} method. Default: []
            application: The CodeDeploy EC2/on-premise Application this Deployment Group belongs to. Default: - A new Application will be created.
            autoRollback: The auto-rollback configuration for this Deployment Group. Default: - default AutoRollbackConfig.
            autoScalingGroups: The auto-scaling groups belonging to this Deployment Group. Auto-scaling groups can also be added after the Deployment Group is created using the {@link #addAutoScalingGroup} method. [disable-awslint:ref-via-interface] is needed because we update userdata for ASGs to install the codedeploy agent. Default: []
            deploymentConfig: The EC2/on-premise Deployment Configuration to use for this Deployment Group. Default: ServerDeploymentConfig#OneAtATime
            deploymentGroupName: The physical, human-readable name of the CodeDeploy Deployment Group. Default: - An auto-generated name will be used.
            ec2InstanceTags: All EC2 instances matching the given set of tags when a deployment occurs will be added to this Deployment Group. Default: - No additional EC2 instances will be added to the Deployment Group.
            ignorePollAlarmsFailure: Whether to continue a deployment even if fetching the alarm status from CloudWatch failed. Default: false
            installAgent: If you've provided any auto-scaling groups with the {@link #autoScalingGroups} property, you can set this property to add User Data that installs the CodeDeploy agent on the instances. Default: true
            loadBalancer: The load balancer to place in front of this Deployment Group. Can be created from either a classic Elastic Load Balancer, or an Application Load Balancer / Network Load Balancer Target Group. Default: - Deployment Group will not have a load balancer defined.
            onPremiseInstanceTags: All on-premise instances matching the given set of tags when a deployment occurs will be added to this Deployment Group. Default: - No additional on-premise instances will be added to the Deployment Group.
            role: The service Role of this Deployment Group. Default: - A new Role will be created.

        Stability:
            experimental
        """
        props: ServerDeploymentGroupProps = {}

        if alarms is not None:
            props["alarms"] = alarms

        if application is not None:
            props["application"] = application

        if auto_rollback is not None:
            props["autoRollback"] = auto_rollback

        if auto_scaling_groups is not None:
            props["autoScalingGroups"] = auto_scaling_groups

        if deployment_config is not None:
            props["deploymentConfig"] = deployment_config

        if deployment_group_name is not None:
            props["deploymentGroupName"] = deployment_group_name

        if ec2_instance_tags is not None:
            props["ec2InstanceTags"] = ec2_instance_tags

        if ignore_poll_alarms_failure is not None:
            props["ignorePollAlarmsFailure"] = ignore_poll_alarms_failure

        if install_agent is not None:
            props["installAgent"] = install_agent

        if load_balancer is not None:
            props["loadBalancer"] = load_balancer

        if on_premise_instance_tags is not None:
            props["onPremiseInstanceTags"] = on_premise_instance_tags

        if role is not None:
            props["role"] = role

        jsii.create(ServerDeploymentGroup, self, [scope, id, props])

    @jsii.member(jsii_name="fromServerDeploymentGroupAttributes")
    @classmethod
    def from_server_deployment_group_attributes(cls, scope: aws_cdk.cdk.Construct, id: str, *, application: "IServerApplication", deployment_group_name: str, deployment_config: typing.Optional["IServerDeploymentConfig"]=None) -> "IServerDeploymentGroup":
        """Import an EC2/on-premise Deployment Group defined either outside the CDK, or in a different CDK Stack and exported using the {@link #export} method.

        Arguments:
            scope: the parent Construct for this new Construct.
            id: the logical ID of this new Construct.
            attrs: the properties of the referenced Deployment Group.
            application: The reference to the CodeDeploy EC2/on-premise Application that this Deployment Group belongs to.
            deploymentGroupName: The physical, human-readable name of the CodeDeploy EC2/on-premise Deployment Group that we are referencing.
            deploymentConfig: The Deployment Configuration this Deployment Group uses. Default: ServerDeploymentConfig#OneAtATime

        Returns:
            a Construct representing a reference to an existing Deployment Group

        Stability:
            experimental
        """
        attrs: ServerDeploymentGroupAttributes = {"application": application, "deploymentGroupName": deployment_group_name}

        if deployment_config is not None:
            attrs["deploymentConfig"] = deployment_config

        return jsii.sinvoke(cls, "fromServerDeploymentGroupAttributes", [scope, id, attrs])

    @jsii.member(jsii_name="addAlarm")
    def add_alarm(self, alarm: aws_cdk.aws_cloudwatch.IAlarm) -> None:
        """Associates an additional alarm with this Deployment Group.

        Arguments:
            alarm: the alarm to associate with this Deployment Group.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAlarm", [alarm])

    @jsii.member(jsii_name="addAutoScalingGroup")
    def add_auto_scaling_group(self, asg: aws_cdk.aws_autoscaling.AutoScalingGroup) -> None:
        """Adds an additional auto-scaling group to this Deployment Group.

        Arguments:
            asg: the auto-scaling group to add to this Deployment Group. [disable-awslint:ref-via-interface] is needed in order to install the code deploy agent by updating the ASGs user data.

        Stability:
            experimental
        """
        return jsii.invoke(self, "addAutoScalingGroup", [asg])

    @property
    @jsii.member(jsii_name="application")
    def application(self) -> "IServerApplication":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "application")

    @property
    @jsii.member(jsii_name="deploymentConfig")
    def deployment_config(self) -> "IServerDeploymentConfig":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentConfig")

    @property
    @jsii.member(jsii_name="deploymentGroupArn")
    def deployment_group_arn(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentGroupArn")

    @property
    @jsii.member(jsii_name="deploymentGroupName")
    def deployment_group_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "deploymentGroupName")

    @property
    @jsii.member(jsii_name="autoScalingGroups")
    def auto_scaling_groups(self) -> typing.Optional[typing.List[aws_cdk.aws_autoscaling.AutoScalingGroup]]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "autoScalingGroups")

    @property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "role")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ServerDeploymentGroupAttributes(jsii.compat.TypedDict, total=False):
    deploymentConfig: "IServerDeploymentConfig"
    """The Deployment Configuration this Deployment Group uses.

    Default:
        ServerDeploymentConfig#OneAtATime

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.ServerDeploymentGroupAttributes", jsii_struct_bases=[_ServerDeploymentGroupAttributes])
class ServerDeploymentGroupAttributes(_ServerDeploymentGroupAttributes):
    """Properties of a reference to a CodeDeploy EC2/on-premise Deployment Group.

    See:
        IServerDeploymentGroup#export
    Stability:
        experimental
    """
    application: "IServerApplication"
    """The reference to the CodeDeploy EC2/on-premise Application that this Deployment Group belongs to.

    Stability:
        experimental
    """

    deploymentGroupName: str
    """The physical, human-readable name of the CodeDeploy EC2/on-premise Deployment Group that we are referencing.

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-codedeploy.ServerDeploymentGroupProps", jsii_struct_bases=[])
class ServerDeploymentGroupProps(jsii.compat.TypedDict, total=False):
    """Construction properties for {@link ServerDeploymentGroup}.

    Stability:
        experimental
    """
    alarms: typing.List[aws_cdk.aws_cloudwatch.IAlarm]
    """The CloudWatch alarms associated with this Deployment Group. CodeDeploy will stop (and optionally roll back) a deployment if during it any of the alarms trigger.

    Alarms can also be added after the Deployment Group is created using the {@link #addAlarm} method.

    Default:
        []

    See:
        https://docs.aws.amazon.com/codedeploy/latest/userguide/monitoring-create-alarms.html
    Stability:
        experimental
    """

    application: "IServerApplication"
    """The CodeDeploy EC2/on-premise Application this Deployment Group belongs to.

    Default:
        - A new Application will be created.

    Stability:
        experimental
    """

    autoRollback: "AutoRollbackConfig"
    """The auto-rollback configuration for this Deployment Group.

    Default:
        - default AutoRollbackConfig.

    Stability:
        experimental
    """

    autoScalingGroups: typing.List[aws_cdk.aws_autoscaling.AutoScalingGroup]
    """The auto-scaling groups belonging to this Deployment Group.

    Auto-scaling groups can also be added after the Deployment Group is created
    using the {@link #addAutoScalingGroup} method.

    [disable-awslint:ref-via-interface] is needed because we update userdata
    for ASGs to install the codedeploy agent.

    Default:
        []

    Stability:
        experimental
    """

    deploymentConfig: "IServerDeploymentConfig"
    """The EC2/on-premise Deployment Configuration to use for this Deployment Group.

    Default:
        ServerDeploymentConfig#OneAtATime

    Stability:
        experimental
    """

    deploymentGroupName: str
    """The physical, human-readable name of the CodeDeploy Deployment Group.

    Default:
        - An auto-generated name will be used.

    Stability:
        experimental
    """

    ec2InstanceTags: "InstanceTagSet"
    """All EC2 instances matching the given set of tags when a deployment occurs will be added to this Deployment Group.

    Default:
        - No additional EC2 instances will be added to the Deployment Group.

    Stability:
        experimental
    """

    ignorePollAlarmsFailure: bool
    """Whether to continue a deployment even if fetching the alarm status from CloudWatch failed.

    Default:
        false

    Stability:
        experimental
    """

    installAgent: bool
    """If you've provided any auto-scaling groups with the {@link #autoScalingGroups} property, you can set this property to add User Data that installs the CodeDeploy agent on the instances.

    Default:
        true

    See:
        https://docs.aws.amazon.com/codedeploy/latest/userguide/codedeploy-agent-operations-install.html
    Stability:
        experimental
    """

    loadBalancer: "LoadBalancer"
    """The load balancer to place in front of this Deployment Group. Can be created from either a classic Elastic Load Balancer, or an Application Load Balancer / Network Load Balancer Target Group.

    Default:
        - Deployment Group will not have a load balancer defined.

    Stability:
        experimental
    """

    onPremiseInstanceTags: "InstanceTagSet"
    """All on-premise instances matching the given set of tags when a deployment occurs will be added to this Deployment Group.

    Default:
        - No additional on-premise instances will be added to the Deployment Group.

    Stability:
        experimental
    """

    role: aws_cdk.aws_iam.IRole
    """The service Role of this Deployment Group.

    Default:
        - A new Role will be created.

    Stability:
        experimental
    """

__all__ = ["AutoRollbackConfig", "CfnApplication", "CfnApplicationProps", "CfnDeploymentConfig", "CfnDeploymentConfigProps", "CfnDeploymentGroup", "CfnDeploymentGroupProps", "ILambdaApplication", "ILambdaDeploymentConfig", "ILambdaDeploymentGroup", "IServerApplication", "IServerDeploymentConfig", "IServerDeploymentGroup", "InstanceTagSet", "LambdaApplication", "LambdaApplicationProps", "LambdaDeploymentConfig", "LambdaDeploymentConfigImportProps", "LambdaDeploymentGroup", "LambdaDeploymentGroupAttributes", "LambdaDeploymentGroupProps", "LoadBalancer", "LoadBalancerGeneration", "MinimumHealthyHosts", "ServerApplication", "ServerApplicationProps", "ServerDeploymentConfig", "ServerDeploymentConfigProps", "ServerDeploymentGroup", "ServerDeploymentGroupAttributes", "ServerDeploymentGroupProps", "__jsii_assembly__"]

publication.publish()
