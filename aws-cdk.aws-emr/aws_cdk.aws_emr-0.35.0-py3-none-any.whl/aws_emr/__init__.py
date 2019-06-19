import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-emr", "0.35.0", __name__, "aws-emr@0.35.0.jsii.tgz")
class CfnCluster(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-emr.CfnCluster"):
    """A CloudFormation ``AWS::EMR::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EMR::Cluster
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, instances: typing.Union["JobFlowInstancesConfigProperty", aws_cdk.cdk.IResolvable], job_flow_role: str, name: str, service_role: str, additional_info: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, applications: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ApplicationProperty"]]]]]=None, auto_scaling_role: typing.Optional[str]=None, bootstrap_actions: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "BootstrapActionConfigProperty"]]]]]=None, configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ConfigurationProperty"]]]]]=None, custom_ami_id: typing.Optional[str]=None, ebs_root_volume_size: typing.Optional[jsii.Number]=None, kerberos_attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["KerberosAttributesProperty"]]]=None, log_uri: typing.Optional[str]=None, release_label: typing.Optional[str]=None, scale_down_behavior: typing.Optional[str]=None, security_configuration: typing.Optional[str]=None, steps: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "StepConfigProperty"]]]]]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, visible_to_all_users: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None) -> None:
        """Create a new ``AWS::EMR::Cluster``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            instances: ``AWS::EMR::Cluster.Instances``.
            jobFlowRole: ``AWS::EMR::Cluster.JobFlowRole``.
            name: ``AWS::EMR::Cluster.Name``.
            serviceRole: ``AWS::EMR::Cluster.ServiceRole``.
            additionalInfo: ``AWS::EMR::Cluster.AdditionalInfo``.
            applications: ``AWS::EMR::Cluster.Applications``.
            autoScalingRole: ``AWS::EMR::Cluster.AutoScalingRole``.
            bootstrapActions: ``AWS::EMR::Cluster.BootstrapActions``.
            configurations: ``AWS::EMR::Cluster.Configurations``.
            customAmiId: ``AWS::EMR::Cluster.CustomAmiId``.
            ebsRootVolumeSize: ``AWS::EMR::Cluster.EbsRootVolumeSize``.
            kerberosAttributes: ``AWS::EMR::Cluster.KerberosAttributes``.
            logUri: ``AWS::EMR::Cluster.LogUri``.
            releaseLabel: ``AWS::EMR::Cluster.ReleaseLabel``.
            scaleDownBehavior: ``AWS::EMR::Cluster.ScaleDownBehavior``.
            securityConfiguration: ``AWS::EMR::Cluster.SecurityConfiguration``.
            steps: ``AWS::EMR::Cluster.Steps``.
            tags: ``AWS::EMR::Cluster.Tags``.
            visibleToAllUsers: ``AWS::EMR::Cluster.VisibleToAllUsers``.

        Stability:
            experimental
        """
        props: CfnClusterProps = {"instances": instances, "jobFlowRole": job_flow_role, "name": name, "serviceRole": service_role}

        if additional_info is not None:
            props["additionalInfo"] = additional_info

        if applications is not None:
            props["applications"] = applications

        if auto_scaling_role is not None:
            props["autoScalingRole"] = auto_scaling_role

        if bootstrap_actions is not None:
            props["bootstrapActions"] = bootstrap_actions

        if configurations is not None:
            props["configurations"] = configurations

        if custom_ami_id is not None:
            props["customAmiId"] = custom_ami_id

        if ebs_root_volume_size is not None:
            props["ebsRootVolumeSize"] = ebs_root_volume_size

        if kerberos_attributes is not None:
            props["kerberosAttributes"] = kerberos_attributes

        if log_uri is not None:
            props["logUri"] = log_uri

        if release_label is not None:
            props["releaseLabel"] = release_label

        if scale_down_behavior is not None:
            props["scaleDownBehavior"] = scale_down_behavior

        if security_configuration is not None:
            props["securityConfiguration"] = security_configuration

        if steps is not None:
            props["steps"] = steps

        if tags is not None:
            props["tags"] = tags

        if visible_to_all_users is not None:
            props["visibleToAllUsers"] = visible_to_all_users

        jsii.create(CfnCluster, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrMasterPublicDns")
    def attr_master_public_dns(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            MasterPublicDNS
        """
        return jsii.get(self, "attrMasterPublicDns")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::EMR::Cluster.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="instances")
    def instances(self) -> typing.Union["JobFlowInstancesConfigProperty", aws_cdk.cdk.IResolvable]:
        """``AWS::EMR::Cluster.Instances``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-instances
        Stability:
            experimental
        """
        return jsii.get(self, "instances")

    @instances.setter
    def instances(self, value: typing.Union["JobFlowInstancesConfigProperty", aws_cdk.cdk.IResolvable]):
        return jsii.set(self, "instances", value)

    @property
    @jsii.member(jsii_name="jobFlowRole")
    def job_flow_role(self) -> str:
        """``AWS::EMR::Cluster.JobFlowRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-jobflowrole
        Stability:
            experimental
        """
        return jsii.get(self, "jobFlowRole")

    @job_flow_role.setter
    def job_flow_role(self, value: str):
        return jsii.set(self, "jobFlowRole", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::EMR::Cluster.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> str:
        """``AWS::EMR::Cluster.ServiceRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-servicerole
        Stability:
            experimental
        """
        return jsii.get(self, "serviceRole")

    @service_role.setter
    def service_role(self, value: str):
        return jsii.set(self, "serviceRole", value)

    @property
    @jsii.member(jsii_name="additionalInfo")
    def additional_info(self) -> typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::EMR::Cluster.AdditionalInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-additionalinfo
        Stability:
            experimental
        """
        return jsii.get(self, "additionalInfo")

    @additional_info.setter
    def additional_info(self, value: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "additionalInfo", value)

    @property
    @jsii.member(jsii_name="applications")
    def applications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ApplicationProperty"]]]]]:
        """``AWS::EMR::Cluster.Applications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-applications
        Stability:
            experimental
        """
        return jsii.get(self, "applications")

    @applications.setter
    def applications(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ApplicationProperty"]]]]]):
        return jsii.set(self, "applications", value)

    @property
    @jsii.member(jsii_name="autoScalingRole")
    def auto_scaling_role(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.AutoScalingRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-autoscalingrole
        Stability:
            experimental
        """
        return jsii.get(self, "autoScalingRole")

    @auto_scaling_role.setter
    def auto_scaling_role(self, value: typing.Optional[str]):
        return jsii.set(self, "autoScalingRole", value)

    @property
    @jsii.member(jsii_name="bootstrapActions")
    def bootstrap_actions(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "BootstrapActionConfigProperty"]]]]]:
        """``AWS::EMR::Cluster.BootstrapActions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-bootstrapactions
        Stability:
            experimental
        """
        return jsii.get(self, "bootstrapActions")

    @bootstrap_actions.setter
    def bootstrap_actions(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "BootstrapActionConfigProperty"]]]]]):
        return jsii.set(self, "bootstrapActions", value)

    @property
    @jsii.member(jsii_name="configurations")
    def configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ConfigurationProperty"]]]]]:
        """``AWS::EMR::Cluster.Configurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-configurations
        Stability:
            experimental
        """
        return jsii.get(self, "configurations")

    @configurations.setter
    def configurations(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ConfigurationProperty"]]]]]):
        return jsii.set(self, "configurations", value)

    @property
    @jsii.member(jsii_name="customAmiId")
    def custom_ami_id(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.CustomAmiId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-customamiid
        Stability:
            experimental
        """
        return jsii.get(self, "customAmiId")

    @custom_ami_id.setter
    def custom_ami_id(self, value: typing.Optional[str]):
        return jsii.set(self, "customAmiId", value)

    @property
    @jsii.member(jsii_name="ebsRootVolumeSize")
    def ebs_root_volume_size(self) -> typing.Optional[jsii.Number]:
        """``AWS::EMR::Cluster.EbsRootVolumeSize``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-ebsrootvolumesize
        Stability:
            experimental
        """
        return jsii.get(self, "ebsRootVolumeSize")

    @ebs_root_volume_size.setter
    def ebs_root_volume_size(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "ebsRootVolumeSize", value)

    @property
    @jsii.member(jsii_name="kerberosAttributes")
    def kerberos_attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["KerberosAttributesProperty"]]]:
        """``AWS::EMR::Cluster.KerberosAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-kerberosattributes
        Stability:
            experimental
        """
        return jsii.get(self, "kerberosAttributes")

    @kerberos_attributes.setter
    def kerberos_attributes(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["KerberosAttributesProperty"]]]):
        return jsii.set(self, "kerberosAttributes", value)

    @property
    @jsii.member(jsii_name="logUri")
    def log_uri(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.LogUri``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-loguri
        Stability:
            experimental
        """
        return jsii.get(self, "logUri")

    @log_uri.setter
    def log_uri(self, value: typing.Optional[str]):
        return jsii.set(self, "logUri", value)

    @property
    @jsii.member(jsii_name="releaseLabel")
    def release_label(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.ReleaseLabel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-releaselabel
        Stability:
            experimental
        """
        return jsii.get(self, "releaseLabel")

    @release_label.setter
    def release_label(self, value: typing.Optional[str]):
        return jsii.set(self, "releaseLabel", value)

    @property
    @jsii.member(jsii_name="scaleDownBehavior")
    def scale_down_behavior(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.ScaleDownBehavior``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-scaledownbehavior
        Stability:
            experimental
        """
        return jsii.get(self, "scaleDownBehavior")

    @scale_down_behavior.setter
    def scale_down_behavior(self, value: typing.Optional[str]):
        return jsii.set(self, "scaleDownBehavior", value)

    @property
    @jsii.member(jsii_name="securityConfiguration")
    def security_configuration(self) -> typing.Optional[str]:
        """``AWS::EMR::Cluster.SecurityConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-securityconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "securityConfiguration")

    @security_configuration.setter
    def security_configuration(self, value: typing.Optional[str]):
        return jsii.set(self, "securityConfiguration", value)

    @property
    @jsii.member(jsii_name="steps")
    def steps(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "StepConfigProperty"]]]]]:
        """``AWS::EMR::Cluster.Steps``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-steps
        Stability:
            experimental
        """
        return jsii.get(self, "steps")

    @steps.setter
    def steps(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "StepConfigProperty"]]]]]):
        return jsii.set(self, "steps", value)

    @property
    @jsii.member(jsii_name="visibleToAllUsers")
    def visible_to_all_users(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::EMR::Cluster.VisibleToAllUsers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-visibletoallusers
        Stability:
            experimental
        """
        return jsii.get(self, "visibleToAllUsers")

    @visible_to_all_users.setter
    def visible_to_all_users(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "visibleToAllUsers", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ApplicationProperty", jsii_struct_bases=[])
    class ApplicationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-application.html
        Stability:
            experimental
        """
        additionalInfo: typing.Union[aws_cdk.cdk.IResolvable, typing.Mapping[str,str]]
        """``CfnCluster.ApplicationProperty.AdditionalInfo``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-application.html#cfn-elasticmapreduce-cluster-application-additionalinfo
        Stability:
            experimental
        """

        args: typing.List[str]
        """``CfnCluster.ApplicationProperty.Args``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-application.html#cfn-elasticmapreduce-cluster-application-args
        Stability:
            experimental
        """

        name: str
        """``CfnCluster.ApplicationProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-application.html#cfn-elasticmapreduce-cluster-application-name
        Stability:
            experimental
        """

        version: str
        """``CfnCluster.ApplicationProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-application.html#cfn-elasticmapreduce-cluster-application-version
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.AutoScalingPolicyProperty", jsii_struct_bases=[])
    class AutoScalingPolicyProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-autoscalingpolicy.html
        Stability:
            experimental
        """
        constraints: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.ScalingConstraintsProperty"]
        """``CfnCluster.AutoScalingPolicyProperty.Constraints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-autoscalingpolicy.html#cfn-elasticmapreduce-cluster-autoscalingpolicy-constraints
        Stability:
            experimental
        """

        rules: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.ScalingRuleProperty"]]]
        """``CfnCluster.AutoScalingPolicyProperty.Rules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-autoscalingpolicy.html#cfn-elasticmapreduce-cluster-autoscalingpolicy-rules
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.BootstrapActionConfigProperty", jsii_struct_bases=[])
    class BootstrapActionConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-bootstrapactionconfig.html
        Stability:
            experimental
        """
        name: str
        """``CfnCluster.BootstrapActionConfigProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-bootstrapactionconfig.html#cfn-elasticmapreduce-cluster-bootstrapactionconfig-name
        Stability:
            experimental
        """

        scriptBootstrapAction: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.ScriptBootstrapActionConfigProperty"]
        """``CfnCluster.BootstrapActionConfigProperty.ScriptBootstrapAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-bootstrapactionconfig.html#cfn-elasticmapreduce-cluster-bootstrapactionconfig-scriptbootstrapaction
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CloudWatchAlarmDefinitionProperty(jsii.compat.TypedDict, total=False):
        dimensions: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.MetricDimensionProperty"]]]
        """``CfnCluster.CloudWatchAlarmDefinitionProperty.Dimensions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-dimensions
        Stability:
            experimental
        """
        evaluationPeriods: jsii.Number
        """``CfnCluster.CloudWatchAlarmDefinitionProperty.EvaluationPeriods``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-evaluationperiods
        Stability:
            experimental
        """
        namespace: str
        """``CfnCluster.CloudWatchAlarmDefinitionProperty.Namespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-namespace
        Stability:
            experimental
        """
        statistic: str
        """``CfnCluster.CloudWatchAlarmDefinitionProperty.Statistic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-statistic
        Stability:
            experimental
        """
        unit: str
        """``CfnCluster.CloudWatchAlarmDefinitionProperty.Unit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-unit
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.CloudWatchAlarmDefinitionProperty", jsii_struct_bases=[_CloudWatchAlarmDefinitionProperty])
    class CloudWatchAlarmDefinitionProperty(_CloudWatchAlarmDefinitionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html
        Stability:
            experimental
        """
        comparisonOperator: str
        """``CfnCluster.CloudWatchAlarmDefinitionProperty.ComparisonOperator``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-comparisonoperator
        Stability:
            experimental
        """

        metricName: str
        """``CfnCluster.CloudWatchAlarmDefinitionProperty.MetricName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-metricname
        Stability:
            experimental
        """

        period: jsii.Number
        """``CfnCluster.CloudWatchAlarmDefinitionProperty.Period``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-period
        Stability:
            experimental
        """

        threshold: jsii.Number
        """``CfnCluster.CloudWatchAlarmDefinitionProperty.Threshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-cluster-cloudwatchalarmdefinition-threshold
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ConfigurationProperty", jsii_struct_bases=[])
    class ConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-configuration.html
        Stability:
            experimental
        """
        classification: str
        """``CfnCluster.ConfigurationProperty.Classification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-configuration.html#cfn-elasticmapreduce-cluster-configuration-classification
        Stability:
            experimental
        """

        configurationProperties: typing.Union[aws_cdk.cdk.IResolvable, typing.Mapping[str,str]]
        """``CfnCluster.ConfigurationProperty.ConfigurationProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-configuration.html#cfn-elasticmapreduce-cluster-configuration-configurationproperties
        Stability:
            experimental
        """

        configurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.ConfigurationProperty"]]]
        """``CfnCluster.ConfigurationProperty.Configurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-configuration.html#cfn-elasticmapreduce-cluster-configuration-configurations
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _EbsBlockDeviceConfigProperty(jsii.compat.TypedDict, total=False):
        volumesPerInstance: jsii.Number
        """``CfnCluster.EbsBlockDeviceConfigProperty.VolumesPerInstance``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-ebsblockdeviceconfig.html#cfn-elasticmapreduce-cluster-ebsblockdeviceconfig-volumesperinstance
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.EbsBlockDeviceConfigProperty", jsii_struct_bases=[_EbsBlockDeviceConfigProperty])
    class EbsBlockDeviceConfigProperty(_EbsBlockDeviceConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-ebsblockdeviceconfig.html
        Stability:
            experimental
        """
        volumeSpecification: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.VolumeSpecificationProperty"]
        """``CfnCluster.EbsBlockDeviceConfigProperty.VolumeSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-ebsblockdeviceconfig.html#cfn-elasticmapreduce-cluster-ebsblockdeviceconfig-volumespecification
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.EbsConfigurationProperty", jsii_struct_bases=[])
    class EbsConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-ebsconfiguration.html
        Stability:
            experimental
        """
        ebsBlockDeviceConfigs: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.EbsBlockDeviceConfigProperty"]]]
        """``CfnCluster.EbsConfigurationProperty.EbsBlockDeviceConfigs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-ebsconfiguration.html#cfn-elasticmapreduce-cluster-ebsconfiguration-ebsblockdeviceconfigs
        Stability:
            experimental
        """

        ebsOptimized: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnCluster.EbsConfigurationProperty.EbsOptimized``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-ebsconfiguration.html#cfn-elasticmapreduce-cluster-ebsconfiguration-ebsoptimized
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _HadoopJarStepConfigProperty(jsii.compat.TypedDict, total=False):
        args: typing.List[str]
        """``CfnCluster.HadoopJarStepConfigProperty.Args``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-hadoopjarstepconfig.html#cfn-elasticmapreduce-cluster-hadoopjarstepconfig-args
        Stability:
            experimental
        """
        mainClass: str
        """``CfnCluster.HadoopJarStepConfigProperty.MainClass``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-hadoopjarstepconfig.html#cfn-elasticmapreduce-cluster-hadoopjarstepconfig-mainclass
        Stability:
            experimental
        """
        stepProperties: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.KeyValueProperty"]]]
        """``CfnCluster.HadoopJarStepConfigProperty.StepProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-hadoopjarstepconfig.html#cfn-elasticmapreduce-cluster-hadoopjarstepconfig-stepproperties
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.HadoopJarStepConfigProperty", jsii_struct_bases=[_HadoopJarStepConfigProperty])
    class HadoopJarStepConfigProperty(_HadoopJarStepConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-hadoopjarstepconfig.html
        Stability:
            experimental
        """
        jar: str
        """``CfnCluster.HadoopJarStepConfigProperty.Jar``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-hadoopjarstepconfig.html#cfn-elasticmapreduce-cluster-hadoopjarstepconfig-jar
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.InstanceFleetConfigProperty", jsii_struct_bases=[])
    class InstanceFleetConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetconfig.html
        Stability:
            experimental
        """
        instanceTypeConfigs: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.InstanceTypeConfigProperty"]]]
        """``CfnCluster.InstanceFleetConfigProperty.InstanceTypeConfigs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetconfig.html#cfn-elasticmapreduce-cluster-instancefleetconfig-instancetypeconfigs
        Stability:
            experimental
        """

        launchSpecifications: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.InstanceFleetProvisioningSpecificationsProperty"]
        """``CfnCluster.InstanceFleetConfigProperty.LaunchSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetconfig.html#cfn-elasticmapreduce-cluster-instancefleetconfig-launchspecifications
        Stability:
            experimental
        """

        name: str
        """``CfnCluster.InstanceFleetConfigProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetconfig.html#cfn-elasticmapreduce-cluster-instancefleetconfig-name
        Stability:
            experimental
        """

        targetOnDemandCapacity: jsii.Number
        """``CfnCluster.InstanceFleetConfigProperty.TargetOnDemandCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetconfig.html#cfn-elasticmapreduce-cluster-instancefleetconfig-targetondemandcapacity
        Stability:
            experimental
        """

        targetSpotCapacity: jsii.Number
        """``CfnCluster.InstanceFleetConfigProperty.TargetSpotCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetconfig.html#cfn-elasticmapreduce-cluster-instancefleetconfig-targetspotcapacity
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.InstanceFleetProvisioningSpecificationsProperty", jsii_struct_bases=[])
    class InstanceFleetProvisioningSpecificationsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetprovisioningspecifications.html
        Stability:
            experimental
        """
        spotSpecification: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.SpotProvisioningSpecificationProperty"]
        """``CfnCluster.InstanceFleetProvisioningSpecificationsProperty.SpotSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancefleetprovisioningspecifications.html#cfn-elasticmapreduce-cluster-instancefleetprovisioningspecifications-spotspecification
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _InstanceGroupConfigProperty(jsii.compat.TypedDict, total=False):
        autoScalingPolicy: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.AutoScalingPolicyProperty"]
        """``CfnCluster.InstanceGroupConfigProperty.AutoScalingPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-autoscalingpolicy
        Stability:
            experimental
        """
        bidPrice: str
        """``CfnCluster.InstanceGroupConfigProperty.BidPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-bidprice
        Stability:
            experimental
        """
        configurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.ConfigurationProperty"]]]
        """``CfnCluster.InstanceGroupConfigProperty.Configurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-configurations
        Stability:
            experimental
        """
        ebsConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.EbsConfigurationProperty"]
        """``CfnCluster.InstanceGroupConfigProperty.EbsConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-ebsconfiguration
        Stability:
            experimental
        """
        market: str
        """``CfnCluster.InstanceGroupConfigProperty.Market``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-market
        Stability:
            experimental
        """
        name: str
        """``CfnCluster.InstanceGroupConfigProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.InstanceGroupConfigProperty", jsii_struct_bases=[_InstanceGroupConfigProperty])
    class InstanceGroupConfigProperty(_InstanceGroupConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html
        Stability:
            experimental
        """
        instanceCount: jsii.Number
        """``CfnCluster.InstanceGroupConfigProperty.InstanceCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-instancecount
        Stability:
            experimental
        """

        instanceType: str
        """``CfnCluster.InstanceGroupConfigProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancegroupconfig.html#cfn-elasticmapreduce-cluster-instancegroupconfig-instancetype
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _InstanceTypeConfigProperty(jsii.compat.TypedDict, total=False):
        bidPrice: str
        """``CfnCluster.InstanceTypeConfigProperty.BidPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html#cfn-elasticmapreduce-cluster-instancetypeconfig-bidprice
        Stability:
            experimental
        """
        bidPriceAsPercentageOfOnDemandPrice: jsii.Number
        """``CfnCluster.InstanceTypeConfigProperty.BidPriceAsPercentageOfOnDemandPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html#cfn-elasticmapreduce-cluster-instancetypeconfig-bidpriceaspercentageofondemandprice
        Stability:
            experimental
        """
        configurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.ConfigurationProperty"]]]
        """``CfnCluster.InstanceTypeConfigProperty.Configurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html#cfn-elasticmapreduce-cluster-instancetypeconfig-configurations
        Stability:
            experimental
        """
        ebsConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.EbsConfigurationProperty"]
        """``CfnCluster.InstanceTypeConfigProperty.EbsConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html#cfn-elasticmapreduce-cluster-instancetypeconfig-ebsconfiguration
        Stability:
            experimental
        """
        weightedCapacity: jsii.Number
        """``CfnCluster.InstanceTypeConfigProperty.WeightedCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html#cfn-elasticmapreduce-cluster-instancetypeconfig-weightedcapacity
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.InstanceTypeConfigProperty", jsii_struct_bases=[_InstanceTypeConfigProperty])
    class InstanceTypeConfigProperty(_InstanceTypeConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html
        Stability:
            experimental
        """
        instanceType: str
        """``CfnCluster.InstanceTypeConfigProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-instancetypeconfig.html#cfn-elasticmapreduce-cluster-instancetypeconfig-instancetype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.JobFlowInstancesConfigProperty", jsii_struct_bases=[])
    class JobFlowInstancesConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html
        Stability:
            experimental
        """
        additionalMasterSecurityGroups: typing.List[str]
        """``CfnCluster.JobFlowInstancesConfigProperty.AdditionalMasterSecurityGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-additionalmastersecuritygroups
        Stability:
            experimental
        """

        additionalSlaveSecurityGroups: typing.List[str]
        """``CfnCluster.JobFlowInstancesConfigProperty.AdditionalSlaveSecurityGroups``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-additionalslavesecuritygroups
        Stability:
            experimental
        """

        coreInstanceFleet: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.InstanceFleetConfigProperty"]
        """``CfnCluster.JobFlowInstancesConfigProperty.CoreInstanceFleet``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-coreinstancefleet
        Stability:
            experimental
        """

        coreInstanceGroup: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.InstanceGroupConfigProperty"]
        """``CfnCluster.JobFlowInstancesConfigProperty.CoreInstanceGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-coreinstancegroup
        Stability:
            experimental
        """

        ec2KeyName: str
        """``CfnCluster.JobFlowInstancesConfigProperty.Ec2KeyName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-ec2keyname
        Stability:
            experimental
        """

        ec2SubnetId: str
        """``CfnCluster.JobFlowInstancesConfigProperty.Ec2SubnetId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-ec2subnetid
        Stability:
            experimental
        """

        ec2SubnetIds: typing.List[str]
        """``CfnCluster.JobFlowInstancesConfigProperty.Ec2SubnetIds``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-ec2subnetids
        Stability:
            experimental
        """

        emrManagedMasterSecurityGroup: str
        """``CfnCluster.JobFlowInstancesConfigProperty.EmrManagedMasterSecurityGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-emrmanagedmastersecuritygroup
        Stability:
            experimental
        """

        emrManagedSlaveSecurityGroup: str
        """``CfnCluster.JobFlowInstancesConfigProperty.EmrManagedSlaveSecurityGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-emrmanagedslavesecuritygroup
        Stability:
            experimental
        """

        hadoopVersion: str
        """``CfnCluster.JobFlowInstancesConfigProperty.HadoopVersion``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-hadoopversion
        Stability:
            experimental
        """

        keepJobFlowAliveWhenNoSteps: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnCluster.JobFlowInstancesConfigProperty.KeepJobFlowAliveWhenNoSteps``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-keepjobflowalivewhennosteps
        Stability:
            experimental
        """

        masterInstanceFleet: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.InstanceFleetConfigProperty"]
        """``CfnCluster.JobFlowInstancesConfigProperty.MasterInstanceFleet``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-masterinstancefleet
        Stability:
            experimental
        """

        masterInstanceGroup: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.InstanceGroupConfigProperty"]
        """``CfnCluster.JobFlowInstancesConfigProperty.MasterInstanceGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-masterinstancegroup
        Stability:
            experimental
        """

        placement: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.PlacementTypeProperty"]
        """``CfnCluster.JobFlowInstancesConfigProperty.Placement``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-placement
        Stability:
            experimental
        """

        serviceAccessSecurityGroup: str
        """``CfnCluster.JobFlowInstancesConfigProperty.ServiceAccessSecurityGroup``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-serviceaccesssecuritygroup
        Stability:
            experimental
        """

        terminationProtected: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnCluster.JobFlowInstancesConfigProperty.TerminationProtected``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-jobflowinstancesconfig.html#cfn-elasticmapreduce-cluster-jobflowinstancesconfig-terminationprotected
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _KerberosAttributesProperty(jsii.compat.TypedDict, total=False):
        adDomainJoinPassword: str
        """``CfnCluster.KerberosAttributesProperty.ADDomainJoinPassword``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-kerberosattributes.html#cfn-elasticmapreduce-cluster-kerberosattributes-addomainjoinpassword
        Stability:
            experimental
        """
        adDomainJoinUser: str
        """``CfnCluster.KerberosAttributesProperty.ADDomainJoinUser``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-kerberosattributes.html#cfn-elasticmapreduce-cluster-kerberosattributes-addomainjoinuser
        Stability:
            experimental
        """
        crossRealmTrustPrincipalPassword: str
        """``CfnCluster.KerberosAttributesProperty.CrossRealmTrustPrincipalPassword``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-kerberosattributes.html#cfn-elasticmapreduce-cluster-kerberosattributes-crossrealmtrustprincipalpassword
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.KerberosAttributesProperty", jsii_struct_bases=[_KerberosAttributesProperty])
    class KerberosAttributesProperty(_KerberosAttributesProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-kerberosattributes.html
        Stability:
            experimental
        """
        kdcAdminPassword: str
        """``CfnCluster.KerberosAttributesProperty.KdcAdminPassword``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-kerberosattributes.html#cfn-elasticmapreduce-cluster-kerberosattributes-kdcadminpassword
        Stability:
            experimental
        """

        realm: str
        """``CfnCluster.KerberosAttributesProperty.Realm``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-kerberosattributes.html#cfn-elasticmapreduce-cluster-kerberosattributes-realm
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.KeyValueProperty", jsii_struct_bases=[])
    class KeyValueProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-keyvalue.html
        Stability:
            experimental
        """
        key: str
        """``CfnCluster.KeyValueProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-keyvalue.html#cfn-elasticmapreduce-cluster-keyvalue-key
        Stability:
            experimental
        """

        value: str
        """``CfnCluster.KeyValueProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-keyvalue.html#cfn-elasticmapreduce-cluster-keyvalue-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.MetricDimensionProperty", jsii_struct_bases=[])
    class MetricDimensionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-metricdimension.html
        Stability:
            experimental
        """
        key: str
        """``CfnCluster.MetricDimensionProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-metricdimension.html#cfn-elasticmapreduce-cluster-metricdimension-key
        Stability:
            experimental
        """

        value: str
        """``CfnCluster.MetricDimensionProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-metricdimension.html#cfn-elasticmapreduce-cluster-metricdimension-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.PlacementTypeProperty", jsii_struct_bases=[])
    class PlacementTypeProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-placementtype.html
        Stability:
            experimental
        """
        availabilityZone: str
        """``CfnCluster.PlacementTypeProperty.AvailabilityZone``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-placementtype.html#cfn-elasticmapreduce-cluster-placementtype-availabilityzone
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ScalingActionProperty(jsii.compat.TypedDict, total=False):
        market: str
        """``CfnCluster.ScalingActionProperty.Market``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingaction.html#cfn-elasticmapreduce-cluster-scalingaction-market
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ScalingActionProperty", jsii_struct_bases=[_ScalingActionProperty])
    class ScalingActionProperty(_ScalingActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingaction.html
        Stability:
            experimental
        """
        simpleScalingPolicyConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.SimpleScalingPolicyConfigurationProperty"]
        """``CfnCluster.ScalingActionProperty.SimpleScalingPolicyConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingaction.html#cfn-elasticmapreduce-cluster-scalingaction-simplescalingpolicyconfiguration
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ScalingConstraintsProperty", jsii_struct_bases=[])
    class ScalingConstraintsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingconstraints.html
        Stability:
            experimental
        """
        maxCapacity: jsii.Number
        """``CfnCluster.ScalingConstraintsProperty.MaxCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingconstraints.html#cfn-elasticmapreduce-cluster-scalingconstraints-maxcapacity
        Stability:
            experimental
        """

        minCapacity: jsii.Number
        """``CfnCluster.ScalingConstraintsProperty.MinCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingconstraints.html#cfn-elasticmapreduce-cluster-scalingconstraints-mincapacity
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ScalingRuleProperty(jsii.compat.TypedDict, total=False):
        description: str
        """``CfnCluster.ScalingRuleProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingrule.html#cfn-elasticmapreduce-cluster-scalingrule-description
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ScalingRuleProperty", jsii_struct_bases=[_ScalingRuleProperty])
    class ScalingRuleProperty(_ScalingRuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingrule.html
        Stability:
            experimental
        """
        action: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.ScalingActionProperty"]
        """``CfnCluster.ScalingRuleProperty.Action``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingrule.html#cfn-elasticmapreduce-cluster-scalingrule-action
        Stability:
            experimental
        """

        name: str
        """``CfnCluster.ScalingRuleProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingrule.html#cfn-elasticmapreduce-cluster-scalingrule-name
        Stability:
            experimental
        """

        trigger: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.ScalingTriggerProperty"]
        """``CfnCluster.ScalingRuleProperty.Trigger``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingrule.html#cfn-elasticmapreduce-cluster-scalingrule-trigger
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ScalingTriggerProperty", jsii_struct_bases=[])
    class ScalingTriggerProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingtrigger.html
        Stability:
            experimental
        """
        cloudWatchAlarmDefinition: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.CloudWatchAlarmDefinitionProperty"]
        """``CfnCluster.ScalingTriggerProperty.CloudWatchAlarmDefinition``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scalingtrigger.html#cfn-elasticmapreduce-cluster-scalingtrigger-cloudwatchalarmdefinition
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ScriptBootstrapActionConfigProperty(jsii.compat.TypedDict, total=False):
        args: typing.List[str]
        """``CfnCluster.ScriptBootstrapActionConfigProperty.Args``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scriptbootstrapactionconfig.html#cfn-elasticmapreduce-cluster-scriptbootstrapactionconfig-args
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.ScriptBootstrapActionConfigProperty", jsii_struct_bases=[_ScriptBootstrapActionConfigProperty])
    class ScriptBootstrapActionConfigProperty(_ScriptBootstrapActionConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scriptbootstrapactionconfig.html
        Stability:
            experimental
        """
        path: str
        """``CfnCluster.ScriptBootstrapActionConfigProperty.Path``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-scriptbootstrapactionconfig.html#cfn-elasticmapreduce-cluster-scriptbootstrapactionconfig-path
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SimpleScalingPolicyConfigurationProperty(jsii.compat.TypedDict, total=False):
        adjustmentType: str
        """``CfnCluster.SimpleScalingPolicyConfigurationProperty.AdjustmentType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-simplescalingpolicyconfiguration.html#cfn-elasticmapreduce-cluster-simplescalingpolicyconfiguration-adjustmenttype
        Stability:
            experimental
        """
        coolDown: jsii.Number
        """``CfnCluster.SimpleScalingPolicyConfigurationProperty.CoolDown``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-simplescalingpolicyconfiguration.html#cfn-elasticmapreduce-cluster-simplescalingpolicyconfiguration-cooldown
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.SimpleScalingPolicyConfigurationProperty", jsii_struct_bases=[_SimpleScalingPolicyConfigurationProperty])
    class SimpleScalingPolicyConfigurationProperty(_SimpleScalingPolicyConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-simplescalingpolicyconfiguration.html
        Stability:
            experimental
        """
        scalingAdjustment: jsii.Number
        """``CfnCluster.SimpleScalingPolicyConfigurationProperty.ScalingAdjustment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-simplescalingpolicyconfiguration.html#cfn-elasticmapreduce-cluster-simplescalingpolicyconfiguration-scalingadjustment
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SpotProvisioningSpecificationProperty(jsii.compat.TypedDict, total=False):
        blockDurationMinutes: jsii.Number
        """``CfnCluster.SpotProvisioningSpecificationProperty.BlockDurationMinutes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-spotprovisioningspecification.html#cfn-elasticmapreduce-cluster-spotprovisioningspecification-blockdurationminutes
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.SpotProvisioningSpecificationProperty", jsii_struct_bases=[_SpotProvisioningSpecificationProperty])
    class SpotProvisioningSpecificationProperty(_SpotProvisioningSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-spotprovisioningspecification.html
        Stability:
            experimental
        """
        timeoutAction: str
        """``CfnCluster.SpotProvisioningSpecificationProperty.TimeoutAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-spotprovisioningspecification.html#cfn-elasticmapreduce-cluster-spotprovisioningspecification-timeoutaction
        Stability:
            experimental
        """

        timeoutDurationMinutes: jsii.Number
        """``CfnCluster.SpotProvisioningSpecificationProperty.TimeoutDurationMinutes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-spotprovisioningspecification.html#cfn-elasticmapreduce-cluster-spotprovisioningspecification-timeoutdurationminutes
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _StepConfigProperty(jsii.compat.TypedDict, total=False):
        actionOnFailure: str
        """``CfnCluster.StepConfigProperty.ActionOnFailure``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-stepconfig.html#cfn-elasticmapreduce-cluster-stepconfig-actiononfailure
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.StepConfigProperty", jsii_struct_bases=[_StepConfigProperty])
    class StepConfigProperty(_StepConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-stepconfig.html
        Stability:
            experimental
        """
        hadoopJarStep: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.HadoopJarStepConfigProperty"]
        """``CfnCluster.StepConfigProperty.HadoopJarStep``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-stepconfig.html#cfn-elasticmapreduce-cluster-stepconfig-hadoopjarstep
        Stability:
            experimental
        """

        name: str
        """``CfnCluster.StepConfigProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-stepconfig.html#cfn-elasticmapreduce-cluster-stepconfig-name
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _VolumeSpecificationProperty(jsii.compat.TypedDict, total=False):
        iops: jsii.Number
        """``CfnCluster.VolumeSpecificationProperty.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-volumespecification.html#cfn-elasticmapreduce-cluster-volumespecification-iops
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnCluster.VolumeSpecificationProperty", jsii_struct_bases=[_VolumeSpecificationProperty])
    class VolumeSpecificationProperty(_VolumeSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-volumespecification.html
        Stability:
            experimental
        """
        sizeInGb: jsii.Number
        """``CfnCluster.VolumeSpecificationProperty.SizeInGB``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-volumespecification.html#cfn-elasticmapreduce-cluster-volumespecification-sizeingb
        Stability:
            experimental
        """

        volumeType: str
        """``CfnCluster.VolumeSpecificationProperty.VolumeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-cluster-volumespecification.html#cfn-elasticmapreduce-cluster-volumespecification-volumetype
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnClusterProps(jsii.compat.TypedDict, total=False):
    additionalInfo: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::EMR::Cluster.AdditionalInfo``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-additionalinfo
    Stability:
        experimental
    """
    applications: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.ApplicationProperty"]]]
    """``AWS::EMR::Cluster.Applications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-applications
    Stability:
        experimental
    """
    autoScalingRole: str
    """``AWS::EMR::Cluster.AutoScalingRole``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-autoscalingrole
    Stability:
        experimental
    """
    bootstrapActions: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.BootstrapActionConfigProperty"]]]
    """``AWS::EMR::Cluster.BootstrapActions``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-bootstrapactions
    Stability:
        experimental
    """
    configurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.ConfigurationProperty"]]]
    """``AWS::EMR::Cluster.Configurations``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-configurations
    Stability:
        experimental
    """
    customAmiId: str
    """``AWS::EMR::Cluster.CustomAmiId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-customamiid
    Stability:
        experimental
    """
    ebsRootVolumeSize: jsii.Number
    """``AWS::EMR::Cluster.EbsRootVolumeSize``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-ebsrootvolumesize
    Stability:
        experimental
    """
    kerberosAttributes: typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.KerberosAttributesProperty"]
    """``AWS::EMR::Cluster.KerberosAttributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-kerberosattributes
    Stability:
        experimental
    """
    logUri: str
    """``AWS::EMR::Cluster.LogUri``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-loguri
    Stability:
        experimental
    """
    releaseLabel: str
    """``AWS::EMR::Cluster.ReleaseLabel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-releaselabel
    Stability:
        experimental
    """
    scaleDownBehavior: str
    """``AWS::EMR::Cluster.ScaleDownBehavior``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-scaledownbehavior
    Stability:
        experimental
    """
    securityConfiguration: str
    """``AWS::EMR::Cluster.SecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-securityconfiguration
    Stability:
        experimental
    """
    steps: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnCluster.StepConfigProperty"]]]
    """``AWS::EMR::Cluster.Steps``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-steps
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::EMR::Cluster.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-tags
    Stability:
        experimental
    """
    visibleToAllUsers: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::EMR::Cluster.VisibleToAllUsers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-visibletoallusers
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnClusterProps", jsii_struct_bases=[_CfnClusterProps])
class CfnClusterProps(_CfnClusterProps):
    """Properties for defining a ``AWS::EMR::Cluster``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html
    Stability:
        experimental
    """
    instances: typing.Union["CfnCluster.JobFlowInstancesConfigProperty", aws_cdk.cdk.IResolvable]
    """``AWS::EMR::Cluster.Instances``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-instances
    Stability:
        experimental
    """

    jobFlowRole: str
    """``AWS::EMR::Cluster.JobFlowRole``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-jobflowrole
    Stability:
        experimental
    """

    name: str
    """``AWS::EMR::Cluster.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-name
    Stability:
        experimental
    """

    serviceRole: str
    """``AWS::EMR::Cluster.ServiceRole``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-cluster.html#cfn-elasticmapreduce-cluster-servicerole
    Stability:
        experimental
    """

class CfnInstanceFleetConfig(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig"):
    """A CloudFormation ``AWS::EMR::InstanceFleetConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EMR::InstanceFleetConfig
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, cluster_id: str, instance_fleet_type: str, instance_type_configs: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "InstanceTypeConfigProperty"]]]]]=None, launch_specifications: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["InstanceFleetProvisioningSpecificationsProperty"]]]=None, name: typing.Optional[str]=None, target_on_demand_capacity: typing.Optional[jsii.Number]=None, target_spot_capacity: typing.Optional[jsii.Number]=None) -> None:
        """Create a new ``AWS::EMR::InstanceFleetConfig``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            clusterId: ``AWS::EMR::InstanceFleetConfig.ClusterId``.
            instanceFleetType: ``AWS::EMR::InstanceFleetConfig.InstanceFleetType``.
            instanceTypeConfigs: ``AWS::EMR::InstanceFleetConfig.InstanceTypeConfigs``.
            launchSpecifications: ``AWS::EMR::InstanceFleetConfig.LaunchSpecifications``.
            name: ``AWS::EMR::InstanceFleetConfig.Name``.
            targetOnDemandCapacity: ``AWS::EMR::InstanceFleetConfig.TargetOnDemandCapacity``.
            targetSpotCapacity: ``AWS::EMR::InstanceFleetConfig.TargetSpotCapacity``.

        Stability:
            experimental
        """
        props: CfnInstanceFleetConfigProps = {"clusterId": cluster_id, "instanceFleetType": instance_fleet_type}

        if instance_type_configs is not None:
            props["instanceTypeConfigs"] = instance_type_configs

        if launch_specifications is not None:
            props["launchSpecifications"] = launch_specifications

        if name is not None:
            props["name"] = name

        if target_on_demand_capacity is not None:
            props["targetOnDemandCapacity"] = target_on_demand_capacity

        if target_spot_capacity is not None:
            props["targetSpotCapacity"] = target_spot_capacity

        jsii.create(CfnInstanceFleetConfig, self, [scope, id, props])

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
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> str:
        """``AWS::EMR::InstanceFleetConfig.ClusterId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-clusterid
        Stability:
            experimental
        """
        return jsii.get(self, "clusterId")

    @cluster_id.setter
    def cluster_id(self, value: str):
        return jsii.set(self, "clusterId", value)

    @property
    @jsii.member(jsii_name="instanceFleetType")
    def instance_fleet_type(self) -> str:
        """``AWS::EMR::InstanceFleetConfig.InstanceFleetType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancefleettype
        Stability:
            experimental
        """
        return jsii.get(self, "instanceFleetType")

    @instance_fleet_type.setter
    def instance_fleet_type(self, value: str):
        return jsii.set(self, "instanceFleetType", value)

    @property
    @jsii.member(jsii_name="instanceTypeConfigs")
    def instance_type_configs(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "InstanceTypeConfigProperty"]]]]]:
        """``AWS::EMR::InstanceFleetConfig.InstanceTypeConfigs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfigs
        Stability:
            experimental
        """
        return jsii.get(self, "instanceTypeConfigs")

    @instance_type_configs.setter
    def instance_type_configs(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "InstanceTypeConfigProperty"]]]]]):
        return jsii.set(self, "instanceTypeConfigs", value)

    @property
    @jsii.member(jsii_name="launchSpecifications")
    def launch_specifications(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["InstanceFleetProvisioningSpecificationsProperty"]]]:
        """``AWS::EMR::InstanceFleetConfig.LaunchSpecifications``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-launchspecifications
        Stability:
            experimental
        """
        return jsii.get(self, "launchSpecifications")

    @launch_specifications.setter
    def launch_specifications(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["InstanceFleetProvisioningSpecificationsProperty"]]]):
        return jsii.set(self, "launchSpecifications", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::EMR::InstanceFleetConfig.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="targetOnDemandCapacity")
    def target_on_demand_capacity(self) -> typing.Optional[jsii.Number]:
        """``AWS::EMR::InstanceFleetConfig.TargetOnDemandCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-targetondemandcapacity
        Stability:
            experimental
        """
        return jsii.get(self, "targetOnDemandCapacity")

    @target_on_demand_capacity.setter
    def target_on_demand_capacity(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "targetOnDemandCapacity", value)

    @property
    @jsii.member(jsii_name="targetSpotCapacity")
    def target_spot_capacity(self) -> typing.Optional[jsii.Number]:
        """``AWS::EMR::InstanceFleetConfig.TargetSpotCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-targetspotcapacity
        Stability:
            experimental
        """
        return jsii.get(self, "targetSpotCapacity")

    @target_spot_capacity.setter
    def target_spot_capacity(self, value: typing.Optional[jsii.Number]):
        return jsii.set(self, "targetSpotCapacity", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.ConfigurationProperty", jsii_struct_bases=[])
    class ConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-configuration.html
        Stability:
            experimental
        """
        classification: str
        """``CfnInstanceFleetConfig.ConfigurationProperty.Classification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-configuration.html#cfn-elasticmapreduce-instancefleetconfig-configuration-classification
        Stability:
            experimental
        """

        configurationProperties: typing.Union[aws_cdk.cdk.IResolvable, typing.Mapping[str,str]]
        """``CfnInstanceFleetConfig.ConfigurationProperty.ConfigurationProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-configuration.html#cfn-elasticmapreduce-instancefleetconfig-configuration-configurationproperties
        Stability:
            experimental
        """

        configurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceFleetConfig.ConfigurationProperty"]]]
        """``CfnInstanceFleetConfig.ConfigurationProperty.Configurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-configuration.html#cfn-elasticmapreduce-instancefleetconfig-configuration-configurations
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _EbsBlockDeviceConfigProperty(jsii.compat.TypedDict, total=False):
        volumesPerInstance: jsii.Number
        """``CfnInstanceFleetConfig.EbsBlockDeviceConfigProperty.VolumesPerInstance``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-ebsblockdeviceconfig.html#cfn-elasticmapreduce-instancefleetconfig-ebsblockdeviceconfig-volumesperinstance
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.EbsBlockDeviceConfigProperty", jsii_struct_bases=[_EbsBlockDeviceConfigProperty])
    class EbsBlockDeviceConfigProperty(_EbsBlockDeviceConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-ebsblockdeviceconfig.html
        Stability:
            experimental
        """
        volumeSpecification: typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceFleetConfig.VolumeSpecificationProperty"]
        """``CfnInstanceFleetConfig.EbsBlockDeviceConfigProperty.VolumeSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-ebsblockdeviceconfig.html#cfn-elasticmapreduce-instancefleetconfig-ebsblockdeviceconfig-volumespecification
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.EbsConfigurationProperty", jsii_struct_bases=[])
    class EbsConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-ebsconfiguration.html
        Stability:
            experimental
        """
        ebsBlockDeviceConfigs: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceFleetConfig.EbsBlockDeviceConfigProperty"]]]
        """``CfnInstanceFleetConfig.EbsConfigurationProperty.EbsBlockDeviceConfigs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-ebsconfiguration.html#cfn-elasticmapreduce-instancefleetconfig-ebsconfiguration-ebsblockdeviceconfigs
        Stability:
            experimental
        """

        ebsOptimized: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnInstanceFleetConfig.EbsConfigurationProperty.EbsOptimized``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-ebsconfiguration.html#cfn-elasticmapreduce-instancefleetconfig-ebsconfiguration-ebsoptimized
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.InstanceFleetProvisioningSpecificationsProperty", jsii_struct_bases=[])
    class InstanceFleetProvisioningSpecificationsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancefleetprovisioningspecifications.html
        Stability:
            experimental
        """
        spotSpecification: typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty"]
        """``CfnInstanceFleetConfig.InstanceFleetProvisioningSpecificationsProperty.SpotSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancefleetprovisioningspecifications.html#cfn-elasticmapreduce-instancefleetconfig-instancefleetprovisioningspecifications-spotspecification
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _InstanceTypeConfigProperty(jsii.compat.TypedDict, total=False):
        bidPrice: str
        """``CfnInstanceFleetConfig.InstanceTypeConfigProperty.BidPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfig-bidprice
        Stability:
            experimental
        """
        bidPriceAsPercentageOfOnDemandPrice: jsii.Number
        """``CfnInstanceFleetConfig.InstanceTypeConfigProperty.BidPriceAsPercentageOfOnDemandPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfig-bidpriceaspercentageofondemandprice
        Stability:
            experimental
        """
        configurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceFleetConfig.ConfigurationProperty"]]]
        """``CfnInstanceFleetConfig.InstanceTypeConfigProperty.Configurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfig-configurations
        Stability:
            experimental
        """
        ebsConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceFleetConfig.EbsConfigurationProperty"]
        """``CfnInstanceFleetConfig.InstanceTypeConfigProperty.EbsConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfig-ebsconfiguration
        Stability:
            experimental
        """
        weightedCapacity: jsii.Number
        """``CfnInstanceFleetConfig.InstanceTypeConfigProperty.WeightedCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfig-weightedcapacity
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.InstanceTypeConfigProperty", jsii_struct_bases=[_InstanceTypeConfigProperty])
    class InstanceTypeConfigProperty(_InstanceTypeConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html
        Stability:
            experimental
        """
        instanceType: str
        """``CfnInstanceFleetConfig.InstanceTypeConfigProperty.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-instancetypeconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfig-instancetype
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SpotProvisioningSpecificationProperty(jsii.compat.TypedDict, total=False):
        blockDurationMinutes: jsii.Number
        """``CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty.BlockDurationMinutes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-spotprovisioningspecification.html#cfn-elasticmapreduce-instancefleetconfig-spotprovisioningspecification-blockdurationminutes
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty", jsii_struct_bases=[_SpotProvisioningSpecificationProperty])
    class SpotProvisioningSpecificationProperty(_SpotProvisioningSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-spotprovisioningspecification.html
        Stability:
            experimental
        """
        timeoutAction: str
        """``CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty.TimeoutAction``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-spotprovisioningspecification.html#cfn-elasticmapreduce-instancefleetconfig-spotprovisioningspecification-timeoutaction
        Stability:
            experimental
        """

        timeoutDurationMinutes: jsii.Number
        """``CfnInstanceFleetConfig.SpotProvisioningSpecificationProperty.TimeoutDurationMinutes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-spotprovisioningspecification.html#cfn-elasticmapreduce-instancefleetconfig-spotprovisioningspecification-timeoutdurationminutes
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _VolumeSpecificationProperty(jsii.compat.TypedDict, total=False):
        iops: jsii.Number
        """``CfnInstanceFleetConfig.VolumeSpecificationProperty.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-volumespecification.html#cfn-elasticmapreduce-instancefleetconfig-volumespecification-iops
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfig.VolumeSpecificationProperty", jsii_struct_bases=[_VolumeSpecificationProperty])
    class VolumeSpecificationProperty(_VolumeSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-volumespecification.html
        Stability:
            experimental
        """
        sizeInGb: jsii.Number
        """``CfnInstanceFleetConfig.VolumeSpecificationProperty.SizeInGB``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-volumespecification.html#cfn-elasticmapreduce-instancefleetconfig-volumespecification-sizeingb
        Stability:
            experimental
        """

        volumeType: str
        """``CfnInstanceFleetConfig.VolumeSpecificationProperty.VolumeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancefleetconfig-volumespecification.html#cfn-elasticmapreduce-instancefleetconfig-volumespecification-volumetype
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnInstanceFleetConfigProps(jsii.compat.TypedDict, total=False):
    instanceTypeConfigs: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceFleetConfig.InstanceTypeConfigProperty"]]]
    """``AWS::EMR::InstanceFleetConfig.InstanceTypeConfigs``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancetypeconfigs
    Stability:
        experimental
    """
    launchSpecifications: typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceFleetConfig.InstanceFleetProvisioningSpecificationsProperty"]
    """``AWS::EMR::InstanceFleetConfig.LaunchSpecifications``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-launchspecifications
    Stability:
        experimental
    """
    name: str
    """``AWS::EMR::InstanceFleetConfig.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-name
    Stability:
        experimental
    """
    targetOnDemandCapacity: jsii.Number
    """``AWS::EMR::InstanceFleetConfig.TargetOnDemandCapacity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-targetondemandcapacity
    Stability:
        experimental
    """
    targetSpotCapacity: jsii.Number
    """``AWS::EMR::InstanceFleetConfig.TargetSpotCapacity``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-targetspotcapacity
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceFleetConfigProps", jsii_struct_bases=[_CfnInstanceFleetConfigProps])
class CfnInstanceFleetConfigProps(_CfnInstanceFleetConfigProps):
    """Properties for defining a ``AWS::EMR::InstanceFleetConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html
    Stability:
        experimental
    """
    clusterId: str
    """``AWS::EMR::InstanceFleetConfig.ClusterId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-clusterid
    Stability:
        experimental
    """

    instanceFleetType: str
    """``AWS::EMR::InstanceFleetConfig.InstanceFleetType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticmapreduce-instancefleetconfig.html#cfn-elasticmapreduce-instancefleetconfig-instancefleettype
    Stability:
        experimental
    """

class CfnInstanceGroupConfig(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig"):
    """A CloudFormation ``AWS::EMR::InstanceGroupConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EMR::InstanceGroupConfig
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, instance_count: jsii.Number, instance_role: str, instance_type: str, job_flow_id: str, auto_scaling_policy: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["AutoScalingPolicyProperty"]]]=None, bid_price: typing.Optional[str]=None, configurations: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ConfigurationProperty"]]]]]=None, ebs_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EbsConfigurationProperty"]]]=None, market: typing.Optional[str]=None, name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EMR::InstanceGroupConfig``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            instanceCount: ``AWS::EMR::InstanceGroupConfig.InstanceCount``.
            instanceRole: ``AWS::EMR::InstanceGroupConfig.InstanceRole``.
            instanceType: ``AWS::EMR::InstanceGroupConfig.InstanceType``.
            jobFlowId: ``AWS::EMR::InstanceGroupConfig.JobFlowId``.
            autoScalingPolicy: ``AWS::EMR::InstanceGroupConfig.AutoScalingPolicy``.
            bidPrice: ``AWS::EMR::InstanceGroupConfig.BidPrice``.
            configurations: ``AWS::EMR::InstanceGroupConfig.Configurations``.
            ebsConfiguration: ``AWS::EMR::InstanceGroupConfig.EbsConfiguration``.
            market: ``AWS::EMR::InstanceGroupConfig.Market``.
            name: ``AWS::EMR::InstanceGroupConfig.Name``.

        Stability:
            experimental
        """
        props: CfnInstanceGroupConfigProps = {"instanceCount": instance_count, "instanceRole": instance_role, "instanceType": instance_type, "jobFlowId": job_flow_id}

        if auto_scaling_policy is not None:
            props["autoScalingPolicy"] = auto_scaling_policy

        if bid_price is not None:
            props["bidPrice"] = bid_price

        if configurations is not None:
            props["configurations"] = configurations

        if ebs_configuration is not None:
            props["ebsConfiguration"] = ebs_configuration

        if market is not None:
            props["market"] = market

        if name is not None:
            props["name"] = name

        jsii.create(CfnInstanceGroupConfig, self, [scope, id, props])

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
    @jsii.member(jsii_name="instanceCount")
    def instance_count(self) -> jsii.Number:
        """``AWS::EMR::InstanceGroupConfig.InstanceCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfiginstancecount-
        Stability:
            experimental
        """
        return jsii.get(self, "instanceCount")

    @instance_count.setter
    def instance_count(self, value: jsii.Number):
        return jsii.set(self, "instanceCount", value)

    @property
    @jsii.member(jsii_name="instanceRole")
    def instance_role(self) -> str:
        """``AWS::EMR::InstanceGroupConfig.InstanceRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-instancerole
        Stability:
            experimental
        """
        return jsii.get(self, "instanceRole")

    @instance_role.setter
    def instance_role(self, value: str):
        return jsii.set(self, "instanceRole", value)

    @property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> str:
        """``AWS::EMR::InstanceGroupConfig.InstanceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-instancetype
        Stability:
            experimental
        """
        return jsii.get(self, "instanceType")

    @instance_type.setter
    def instance_type(self, value: str):
        return jsii.set(self, "instanceType", value)

    @property
    @jsii.member(jsii_name="jobFlowId")
    def job_flow_id(self) -> str:
        """``AWS::EMR::InstanceGroupConfig.JobFlowId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-jobflowid
        Stability:
            experimental
        """
        return jsii.get(self, "jobFlowId")

    @job_flow_id.setter
    def job_flow_id(self, value: str):
        return jsii.set(self, "jobFlowId", value)

    @property
    @jsii.member(jsii_name="autoScalingPolicy")
    def auto_scaling_policy(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["AutoScalingPolicyProperty"]]]:
        """``AWS::EMR::InstanceGroupConfig.AutoScalingPolicy``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-elasticmapreduce-instancegroupconfig-autoscalingpolicy
        Stability:
            experimental
        """
        return jsii.get(self, "autoScalingPolicy")

    @auto_scaling_policy.setter
    def auto_scaling_policy(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["AutoScalingPolicyProperty"]]]):
        return jsii.set(self, "autoScalingPolicy", value)

    @property
    @jsii.member(jsii_name="bidPrice")
    def bid_price(self) -> typing.Optional[str]:
        """``AWS::EMR::InstanceGroupConfig.BidPrice``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-bidprice
        Stability:
            experimental
        """
        return jsii.get(self, "bidPrice")

    @bid_price.setter
    def bid_price(self, value: typing.Optional[str]):
        return jsii.set(self, "bidPrice", value)

    @property
    @jsii.member(jsii_name="configurations")
    def configurations(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ConfigurationProperty"]]]]]:
        """``AWS::EMR::InstanceGroupConfig.Configurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-configurations
        Stability:
            experimental
        """
        return jsii.get(self, "configurations")

    @configurations.setter
    def configurations(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ConfigurationProperty"]]]]]):
        return jsii.set(self, "configurations", value)

    @property
    @jsii.member(jsii_name="ebsConfiguration")
    def ebs_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EbsConfigurationProperty"]]]:
        """``AWS::EMR::InstanceGroupConfig.EbsConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-ebsconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "ebsConfiguration")

    @ebs_configuration.setter
    def ebs_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["EbsConfigurationProperty"]]]):
        return jsii.set(self, "ebsConfiguration", value)

    @property
    @jsii.member(jsii_name="market")
    def market(self) -> typing.Optional[str]:
        """``AWS::EMR::InstanceGroupConfig.Market``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-market
        Stability:
            experimental
        """
        return jsii.get(self, "market")

    @market.setter
    def market(self, value: typing.Optional[str]):
        return jsii.set(self, "market", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::EMR::InstanceGroupConfig.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.AutoScalingPolicyProperty", jsii_struct_bases=[])
    class AutoScalingPolicyProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-autoscalingpolicy.html
        Stability:
            experimental
        """
        constraints: typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.ScalingConstraintsProperty"]
        """``CfnInstanceGroupConfig.AutoScalingPolicyProperty.Constraints``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-autoscalingpolicy.html#cfn-elasticmapreduce-instancegroupconfig-autoscalingpolicy-constraints
        Stability:
            experimental
        """

        rules: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.ScalingRuleProperty"]]]
        """``CfnInstanceGroupConfig.AutoScalingPolicyProperty.Rules``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-autoscalingpolicy.html#cfn-elasticmapreduce-instancegroupconfig-autoscalingpolicy-rules
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _CloudWatchAlarmDefinitionProperty(jsii.compat.TypedDict, total=False):
        dimensions: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.MetricDimensionProperty"]]]
        """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Dimensions``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-dimensions
        Stability:
            experimental
        """
        evaluationPeriods: jsii.Number
        """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.EvaluationPeriods``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-evaluationperiods
        Stability:
            experimental
        """
        namespace: str
        """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Namespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-namespace
        Stability:
            experimental
        """
        statistic: str
        """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Statistic``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-statistic
        Stability:
            experimental
        """
        unit: str
        """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Unit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-unit
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty", jsii_struct_bases=[_CloudWatchAlarmDefinitionProperty])
    class CloudWatchAlarmDefinitionProperty(_CloudWatchAlarmDefinitionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html
        Stability:
            experimental
        """
        comparisonOperator: str
        """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.ComparisonOperator``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-comparisonoperator
        Stability:
            experimental
        """

        metricName: str
        """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.MetricName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-metricname
        Stability:
            experimental
        """

        period: jsii.Number
        """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Period``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-period
        Stability:
            experimental
        """

        threshold: jsii.Number
        """``CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty.Threshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition.html#cfn-elasticmapreduce-instancegroupconfig-cloudwatchalarmdefinition-threshold
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.ConfigurationProperty", jsii_struct_bases=[])
    class ConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-configuration.html
        Stability:
            experimental
        """
        classification: str
        """``CfnInstanceGroupConfig.ConfigurationProperty.Classification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-configuration.html#cfn-emr-cluster-configuration-classification
        Stability:
            experimental
        """

        configurationProperties: typing.Union[aws_cdk.cdk.IResolvable, typing.Mapping[str,str]]
        """``CfnInstanceGroupConfig.ConfigurationProperty.ConfigurationProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-configuration.html#cfn-emr-cluster-configuration-configurationproperties
        Stability:
            experimental
        """

        configurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.ConfigurationProperty"]]]
        """``CfnInstanceGroupConfig.ConfigurationProperty.Configurations``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-cluster-configuration.html#cfn-emr-cluster-configuration-configurations
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _EbsBlockDeviceConfigProperty(jsii.compat.TypedDict, total=False):
        volumesPerInstance: jsii.Number
        """``CfnInstanceGroupConfig.EbsBlockDeviceConfigProperty.VolumesPerInstance``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig.html#cfn-emr-ebsconfiguration-ebsblockdeviceconfig-volumesperinstance
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.EbsBlockDeviceConfigProperty", jsii_struct_bases=[_EbsBlockDeviceConfigProperty])
    class EbsBlockDeviceConfigProperty(_EbsBlockDeviceConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig.html
        Stability:
            experimental
        """
        volumeSpecification: typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.VolumeSpecificationProperty"]
        """``CfnInstanceGroupConfig.EbsBlockDeviceConfigProperty.VolumeSpecification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig.html#cfn-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.EbsConfigurationProperty", jsii_struct_bases=[])
    class EbsConfigurationProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration.html
        Stability:
            experimental
        """
        ebsBlockDeviceConfigs: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.EbsBlockDeviceConfigProperty"]]]
        """``CfnInstanceGroupConfig.EbsConfigurationProperty.EbsBlockDeviceConfigs``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration.html#cfn-emr-ebsconfiguration-ebsblockdeviceconfigs
        Stability:
            experimental
        """

        ebsOptimized: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnInstanceGroupConfig.EbsConfigurationProperty.EbsOptimized``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration.html#cfn-emr-ebsconfiguration-ebsoptimized
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.MetricDimensionProperty", jsii_struct_bases=[])
    class MetricDimensionProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-metricdimension.html
        Stability:
            experimental
        """
        key: str
        """``CfnInstanceGroupConfig.MetricDimensionProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-metricdimension.html#cfn-elasticmapreduce-instancegroupconfig-metricdimension-key
        Stability:
            experimental
        """

        value: str
        """``CfnInstanceGroupConfig.MetricDimensionProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-metricdimension.html#cfn-elasticmapreduce-instancegroupconfig-metricdimension-value
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ScalingActionProperty(jsii.compat.TypedDict, total=False):
        market: str
        """``CfnInstanceGroupConfig.ScalingActionProperty.Market``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingaction.html#cfn-elasticmapreduce-instancegroupconfig-scalingaction-market
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.ScalingActionProperty", jsii_struct_bases=[_ScalingActionProperty])
    class ScalingActionProperty(_ScalingActionProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingaction.html
        Stability:
            experimental
        """
        simpleScalingPolicyConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty"]
        """``CfnInstanceGroupConfig.ScalingActionProperty.SimpleScalingPolicyConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingaction.html#cfn-elasticmapreduce-instancegroupconfig-scalingaction-simplescalingpolicyconfiguration
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.ScalingConstraintsProperty", jsii_struct_bases=[])
    class ScalingConstraintsProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingconstraints.html
        Stability:
            experimental
        """
        maxCapacity: jsii.Number
        """``CfnInstanceGroupConfig.ScalingConstraintsProperty.MaxCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingconstraints.html#cfn-elasticmapreduce-instancegroupconfig-scalingconstraints-maxcapacity
        Stability:
            experimental
        """

        minCapacity: jsii.Number
        """``CfnInstanceGroupConfig.ScalingConstraintsProperty.MinCapacity``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingconstraints.html#cfn-elasticmapreduce-instancegroupconfig-scalingconstraints-mincapacity
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ScalingRuleProperty(jsii.compat.TypedDict, total=False):
        description: str
        """``CfnInstanceGroupConfig.ScalingRuleProperty.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingrule.html#cfn-elasticmapreduce-instancegroupconfig-scalingrule-description
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.ScalingRuleProperty", jsii_struct_bases=[_ScalingRuleProperty])
    class ScalingRuleProperty(_ScalingRuleProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingrule.html
        Stability:
            experimental
        """
        action: typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.ScalingActionProperty"]
        """``CfnInstanceGroupConfig.ScalingRuleProperty.Action``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingrule.html#cfn-elasticmapreduce-instancegroupconfig-scalingrule-action
        Stability:
            experimental
        """

        name: str
        """``CfnInstanceGroupConfig.ScalingRuleProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingrule.html#cfn-elasticmapreduce-instancegroupconfig-scalingrule-name
        Stability:
            experimental
        """

        trigger: typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.ScalingTriggerProperty"]
        """``CfnInstanceGroupConfig.ScalingRuleProperty.Trigger``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingrule.html#cfn-elasticmapreduce-instancegroupconfig-scalingrule-trigger
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.ScalingTriggerProperty", jsii_struct_bases=[])
    class ScalingTriggerProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingtrigger.html
        Stability:
            experimental
        """
        cloudWatchAlarmDefinition: typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.CloudWatchAlarmDefinitionProperty"]
        """``CfnInstanceGroupConfig.ScalingTriggerProperty.CloudWatchAlarmDefinition``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-scalingtrigger.html#cfn-elasticmapreduce-instancegroupconfig-scalingtrigger-cloudwatchalarmdefinition
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _SimpleScalingPolicyConfigurationProperty(jsii.compat.TypedDict, total=False):
        adjustmentType: str
        """``CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty.AdjustmentType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration.html#cfn-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration-adjustmenttype
        Stability:
            experimental
        """
        coolDown: jsii.Number
        """``CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty.CoolDown``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration.html#cfn-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration-cooldown
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty", jsii_struct_bases=[_SimpleScalingPolicyConfigurationProperty])
    class SimpleScalingPolicyConfigurationProperty(_SimpleScalingPolicyConfigurationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration.html
        Stability:
            experimental
        """
        scalingAdjustment: jsii.Number
        """``CfnInstanceGroupConfig.SimpleScalingPolicyConfigurationProperty.ScalingAdjustment``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration.html#cfn-elasticmapreduce-instancegroupconfig-simplescalingpolicyconfiguration-scalingadjustment
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _VolumeSpecificationProperty(jsii.compat.TypedDict, total=False):
        iops: jsii.Number
        """``CfnInstanceGroupConfig.VolumeSpecificationProperty.Iops``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification.html#cfn-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification-iops
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfig.VolumeSpecificationProperty", jsii_struct_bases=[_VolumeSpecificationProperty])
    class VolumeSpecificationProperty(_VolumeSpecificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification.html
        Stability:
            experimental
        """
        sizeInGb: jsii.Number
        """``CfnInstanceGroupConfig.VolumeSpecificationProperty.SizeInGB``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification.html#cfn-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification-sizeingb
        Stability:
            experimental
        """

        volumeType: str
        """``CfnInstanceGroupConfig.VolumeSpecificationProperty.VolumeType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification.html#cfn-emr-ebsconfiguration-ebsblockdeviceconfig-volumespecification-volumetype
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnInstanceGroupConfigProps(jsii.compat.TypedDict, total=False):
    autoScalingPolicy: typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.AutoScalingPolicyProperty"]
    """``AWS::EMR::InstanceGroupConfig.AutoScalingPolicy``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-elasticmapreduce-instancegroupconfig-autoscalingpolicy
    Stability:
        experimental
    """
    bidPrice: str
    """``AWS::EMR::InstanceGroupConfig.BidPrice``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-bidprice
    Stability:
        experimental
    """
    configurations: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.ConfigurationProperty"]]]
    """``AWS::EMR::InstanceGroupConfig.Configurations``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-configurations
    Stability:
        experimental
    """
    ebsConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnInstanceGroupConfig.EbsConfigurationProperty"]
    """``AWS::EMR::InstanceGroupConfig.EbsConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-ebsconfiguration
    Stability:
        experimental
    """
    market: str
    """``AWS::EMR::InstanceGroupConfig.Market``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-market
    Stability:
        experimental
    """
    name: str
    """``AWS::EMR::InstanceGroupConfig.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-name
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnInstanceGroupConfigProps", jsii_struct_bases=[_CfnInstanceGroupConfigProps])
class CfnInstanceGroupConfigProps(_CfnInstanceGroupConfigProps):
    """Properties for defining a ``AWS::EMR::InstanceGroupConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html
    Stability:
        experimental
    """
    instanceCount: jsii.Number
    """``AWS::EMR::InstanceGroupConfig.InstanceCount``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfiginstancecount-
    Stability:
        experimental
    """

    instanceRole: str
    """``AWS::EMR::InstanceGroupConfig.InstanceRole``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-instancerole
    Stability:
        experimental
    """

    instanceType: str
    """``AWS::EMR::InstanceGroupConfig.InstanceType``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-instancetype
    Stability:
        experimental
    """

    jobFlowId: str
    """``AWS::EMR::InstanceGroupConfig.JobFlowId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-instancegroupconfig.html#cfn-emr-instancegroupconfig-jobflowid
    Stability:
        experimental
    """

class CfnSecurityConfiguration(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-emr.CfnSecurityConfiguration"):
    """A CloudFormation ``AWS::EMR::SecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-securityconfiguration.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EMR::SecurityConfiguration
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, security_configuration: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable], name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::EMR::SecurityConfiguration``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            securityConfiguration: ``AWS::EMR::SecurityConfiguration.SecurityConfiguration``.
            name: ``AWS::EMR::SecurityConfiguration.Name``.

        Stability:
            experimental
        """
        props: CfnSecurityConfigurationProps = {"securityConfiguration": security_configuration}

        if name is not None:
            props["name"] = name

        jsii.create(CfnSecurityConfiguration, self, [scope, id, props])

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
    @jsii.member(jsii_name="securityConfiguration")
    def security_configuration(self) -> typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]:
        """``AWS::EMR::SecurityConfiguration.SecurityConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-securityconfiguration.html#cfn-emr-securityconfiguration-securityconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "securityConfiguration")

    @security_configuration.setter
    def security_configuration(self, value: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]):
        return jsii.set(self, "securityConfiguration", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::EMR::SecurityConfiguration.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-securityconfiguration.html#cfn-emr-securityconfiguration-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSecurityConfigurationProps(jsii.compat.TypedDict, total=False):
    name: str
    """``AWS::EMR::SecurityConfiguration.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-securityconfiguration.html#cfn-emr-securityconfiguration-name
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnSecurityConfigurationProps", jsii_struct_bases=[_CfnSecurityConfigurationProps])
class CfnSecurityConfigurationProps(_CfnSecurityConfigurationProps):
    """Properties for defining a ``AWS::EMR::SecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-securityconfiguration.html
    Stability:
        experimental
    """
    securityConfiguration: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.IResolvable]
    """``AWS::EMR::SecurityConfiguration.SecurityConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-securityconfiguration.html#cfn-emr-securityconfiguration-securityconfiguration
    Stability:
        experimental
    """

class CfnStep(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-emr.CfnStep"):
    """A CloudFormation ``AWS::EMR::Step``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html
    Stability:
        experimental
    cloudformationResource:
        AWS::EMR::Step
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, action_on_failure: str, hadoop_jar_step: typing.Union[aws_cdk.cdk.IResolvable, "HadoopJarStepConfigProperty"], job_flow_id: str, name: str) -> None:
        """Create a new ``AWS::EMR::Step``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            actionOnFailure: ``AWS::EMR::Step.ActionOnFailure``.
            hadoopJarStep: ``AWS::EMR::Step.HadoopJarStep``.
            jobFlowId: ``AWS::EMR::Step.JobFlowId``.
            name: ``AWS::EMR::Step.Name``.

        Stability:
            experimental
        """
        props: CfnStepProps = {"actionOnFailure": action_on_failure, "hadoopJarStep": hadoop_jar_step, "jobFlowId": job_flow_id, "name": name}

        jsii.create(CfnStep, self, [scope, id, props])

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
    @jsii.member(jsii_name="actionOnFailure")
    def action_on_failure(self) -> str:
        """``AWS::EMR::Step.ActionOnFailure``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-actiononfailure
        Stability:
            experimental
        """
        return jsii.get(self, "actionOnFailure")

    @action_on_failure.setter
    def action_on_failure(self, value: str):
        return jsii.set(self, "actionOnFailure", value)

    @property
    @jsii.member(jsii_name="hadoopJarStep")
    def hadoop_jar_step(self) -> typing.Union[aws_cdk.cdk.IResolvable, "HadoopJarStepConfigProperty"]:
        """``AWS::EMR::Step.HadoopJarStep``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-hadoopjarstep
        Stability:
            experimental
        """
        return jsii.get(self, "hadoopJarStep")

    @hadoop_jar_step.setter
    def hadoop_jar_step(self, value: typing.Union[aws_cdk.cdk.IResolvable, "HadoopJarStepConfigProperty"]):
        return jsii.set(self, "hadoopJarStep", value)

    @property
    @jsii.member(jsii_name="jobFlowId")
    def job_flow_id(self) -> str:
        """``AWS::EMR::Step.JobFlowId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-jobflowid
        Stability:
            experimental
        """
        return jsii.get(self, "jobFlowId")

    @job_flow_id.setter
    def job_flow_id(self, value: str):
        return jsii.set(self, "jobFlowId", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::EMR::Step.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _HadoopJarStepConfigProperty(jsii.compat.TypedDict, total=False):
        args: typing.List[str]
        """``CfnStep.HadoopJarStepConfigProperty.Args``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-hadoopjarstepconfig.html#cfn-elasticmapreduce-step-hadoopjarstepconfig-args
        Stability:
            experimental
        """
        mainClass: str
        """``CfnStep.HadoopJarStepConfigProperty.MainClass``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-hadoopjarstepconfig.html#cfn-elasticmapreduce-step-hadoopjarstepconfig-mainclass
        Stability:
            experimental
        """
        stepProperties: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnStep.KeyValueProperty"]]]
        """``CfnStep.HadoopJarStepConfigProperty.StepProperties``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-hadoopjarstepconfig.html#cfn-elasticmapreduce-step-hadoopjarstepconfig-stepproperties
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnStep.HadoopJarStepConfigProperty", jsii_struct_bases=[_HadoopJarStepConfigProperty])
    class HadoopJarStepConfigProperty(_HadoopJarStepConfigProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-hadoopjarstepconfig.html
        Stability:
            experimental
        """
        jar: str
        """``CfnStep.HadoopJarStepConfigProperty.Jar``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-hadoopjarstepconfig.html#cfn-elasticmapreduce-step-hadoopjarstepconfig-jar
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnStep.KeyValueProperty", jsii_struct_bases=[])
    class KeyValueProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-keyvalue.html
        Stability:
            experimental
        """
        key: str
        """``CfnStep.KeyValueProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-keyvalue.html#cfn-elasticmapreduce-step-keyvalue-key
        Stability:
            experimental
        """

        value: str
        """``CfnStep.KeyValueProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticmapreduce-step-keyvalue.html#cfn-elasticmapreduce-step-keyvalue-value
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-emr.CfnStepProps", jsii_struct_bases=[])
class CfnStepProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::EMR::Step``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html
    Stability:
        experimental
    """
    actionOnFailure: str
    """``AWS::EMR::Step.ActionOnFailure``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-actiononfailure
    Stability:
        experimental
    """

    hadoopJarStep: typing.Union[aws_cdk.cdk.IResolvable, "CfnStep.HadoopJarStepConfigProperty"]
    """``AWS::EMR::Step.HadoopJarStep``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-hadoopjarstep
    Stability:
        experimental
    """

    jobFlowId: str
    """``AWS::EMR::Step.JobFlowId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-jobflowid
    Stability:
        experimental
    """

    name: str
    """``AWS::EMR::Step.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-emr-step.html#cfn-elasticmapreduce-step-name
    Stability:
        experimental
    """

__all__ = ["CfnCluster", "CfnClusterProps", "CfnInstanceFleetConfig", "CfnInstanceFleetConfigProps", "CfnInstanceGroupConfig", "CfnInstanceGroupConfigProps", "CfnSecurityConfiguration", "CfnSecurityConfigurationProps", "CfnStep", "CfnStepProps", "__jsii_assembly__"]

publication.publish()
