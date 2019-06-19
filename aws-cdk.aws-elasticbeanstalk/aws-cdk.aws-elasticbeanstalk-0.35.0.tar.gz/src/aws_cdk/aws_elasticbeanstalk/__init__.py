import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-elasticbeanstalk", "0.35.0", __name__, "aws-elasticbeanstalk@0.35.0.jsii.tgz")
class CfnApplication(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplication"):
    """A CloudFormation ``AWS::ElasticBeanstalk::Application``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ElasticBeanstalk::Application
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, application_name: typing.Optional[str]=None, description: typing.Optional[str]=None, resource_lifecycle_config: typing.Optional[typing.Union[typing.Optional["ApplicationResourceLifecycleConfigProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]=None) -> None:
        """Create a new ``AWS::ElasticBeanstalk::Application``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            applicationName: ``AWS::ElasticBeanstalk::Application.ApplicationName``.
            description: ``AWS::ElasticBeanstalk::Application.Description``.
            resourceLifecycleConfig: ``AWS::ElasticBeanstalk::Application.ResourceLifecycleConfig``.

        Stability:
            experimental
        """
        props: CfnApplicationProps = {}

        if application_name is not None:
            props["applicationName"] = application_name

        if description is not None:
            props["description"] = description

        if resource_lifecycle_config is not None:
            props["resourceLifecycleConfig"] = resource_lifecycle_config

        jsii.create(CfnApplication, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::Application.ApplicationName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html#cfn-elasticbeanstalk-application-name
        Stability:
            experimental
        """
        return jsii.get(self, "applicationName")

    @application_name.setter
    def application_name(self, value: typing.Optional[str]):
        return jsii.set(self, "applicationName", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::Application.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html#cfn-elasticbeanstalk-application-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="resourceLifecycleConfig")
    def resource_lifecycle_config(self) -> typing.Optional[typing.Union[typing.Optional["ApplicationResourceLifecycleConfigProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::ElasticBeanstalk::Application.ResourceLifecycleConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html#cfn-elasticbeanstalk-application-resourcelifecycleconfig
        Stability:
            experimental
        """
        return jsii.get(self, "resourceLifecycleConfig")

    @resource_lifecycle_config.setter
    def resource_lifecycle_config(self, value: typing.Optional[typing.Union[typing.Optional["ApplicationResourceLifecycleConfigProperty"], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "resourceLifecycleConfig", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplication.ApplicationResourceLifecycleConfigProperty", jsii_struct_bases=[])
    class ApplicationResourceLifecycleConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-applicationresourcelifecycleconfig.html
        Stability:
            experimental
        """
        serviceRole: str
        """``CfnApplication.ApplicationResourceLifecycleConfigProperty.ServiceRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-applicationresourcelifecycleconfig.html#cfn-elasticbeanstalk-application-applicationresourcelifecycleconfig-servicerole
        Stability:
            experimental
        """

        versionLifecycleConfig: typing.Union[aws_cdk.cdk.IResolvable, "CfnApplication.ApplicationVersionLifecycleConfigProperty"]
        """``CfnApplication.ApplicationResourceLifecycleConfigProperty.VersionLifecycleConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-applicationresourcelifecycleconfig.html#cfn-elasticbeanstalk-application-applicationresourcelifecycleconfig-versionlifecycleconfig
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplication.ApplicationVersionLifecycleConfigProperty", jsii_struct_bases=[])
    class ApplicationVersionLifecycleConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-applicationversionlifecycleconfig.html
        Stability:
            experimental
        """
        maxAgeRule: typing.Union[aws_cdk.cdk.IResolvable, "CfnApplication.MaxAgeRuleProperty"]
        """``CfnApplication.ApplicationVersionLifecycleConfigProperty.MaxAgeRule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-applicationversionlifecycleconfig.html#cfn-elasticbeanstalk-application-applicationversionlifecycleconfig-maxagerule
        Stability:
            experimental
        """

        maxCountRule: typing.Union[aws_cdk.cdk.IResolvable, "CfnApplication.MaxCountRuleProperty"]
        """``CfnApplication.ApplicationVersionLifecycleConfigProperty.MaxCountRule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-applicationversionlifecycleconfig.html#cfn-elasticbeanstalk-application-applicationversionlifecycleconfig-maxcountrule
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplication.MaxAgeRuleProperty", jsii_struct_bases=[])
    class MaxAgeRuleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxagerule.html
        Stability:
            experimental
        """
        deleteSourceFromS3: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnApplication.MaxAgeRuleProperty.DeleteSourceFromS3``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxagerule.html#cfn-elasticbeanstalk-application-maxagerule-deletesourcefroms3
        Stability:
            experimental
        """

        enabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnApplication.MaxAgeRuleProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxagerule.html#cfn-elasticbeanstalk-application-maxagerule-enabled
        Stability:
            experimental
        """

        maxAgeInDays: jsii.Number
        """``CfnApplication.MaxAgeRuleProperty.MaxAgeInDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxagerule.html#cfn-elasticbeanstalk-application-maxagerule-maxageindays
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplication.MaxCountRuleProperty", jsii_struct_bases=[])
    class MaxCountRuleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxcountrule.html
        Stability:
            experimental
        """
        deleteSourceFromS3: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnApplication.MaxCountRuleProperty.DeleteSourceFromS3``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxcountrule.html#cfn-elasticbeanstalk-application-maxcountrule-deletesourcefroms3
        Stability:
            experimental
        """

        enabled: typing.Union[bool, aws_cdk.cdk.IResolvable]
        """``CfnApplication.MaxCountRuleProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxcountrule.html#cfn-elasticbeanstalk-application-maxcountrule-enabled
        Stability:
            experimental
        """

        maxCount: jsii.Number
        """``CfnApplication.MaxCountRuleProperty.MaxCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxcountrule.html#cfn-elasticbeanstalk-application-maxcountrule-maxcount
        Stability:
            experimental
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplicationProps", jsii_struct_bases=[])
class CfnApplicationProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::ElasticBeanstalk::Application``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html
    Stability:
        experimental
    """
    applicationName: str
    """``AWS::ElasticBeanstalk::Application.ApplicationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html#cfn-elasticbeanstalk-application-name
    Stability:
        experimental
    """

    description: str
    """``AWS::ElasticBeanstalk::Application.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html#cfn-elasticbeanstalk-application-description
    Stability:
        experimental
    """

    resourceLifecycleConfig: typing.Union["CfnApplication.ApplicationResourceLifecycleConfigProperty", aws_cdk.cdk.IResolvable]
    """``AWS::ElasticBeanstalk::Application.ResourceLifecycleConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html#cfn-elasticbeanstalk-application-resourcelifecycleconfig
    Stability:
        experimental
    """

class CfnApplicationVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplicationVersion"):
    """A CloudFormation ``AWS::ElasticBeanstalk::ApplicationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ElasticBeanstalk::ApplicationVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, application_name: str, source_bundle: typing.Union[aws_cdk.cdk.IResolvable, "SourceBundleProperty"], description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ElasticBeanstalk::ApplicationVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            applicationName: ``AWS::ElasticBeanstalk::ApplicationVersion.ApplicationName``.
            sourceBundle: ``AWS::ElasticBeanstalk::ApplicationVersion.SourceBundle``.
            description: ``AWS::ElasticBeanstalk::ApplicationVersion.Description``.

        Stability:
            experimental
        """
        props: CfnApplicationVersionProps = {"applicationName": application_name, "sourceBundle": source_bundle}

        if description is not None:
            props["description"] = description

        jsii.create(CfnApplicationVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """``AWS::ElasticBeanstalk::ApplicationVersion.ApplicationName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html#cfn-elasticbeanstalk-applicationversion-applicationname
        Stability:
            experimental
        """
        return jsii.get(self, "applicationName")

    @application_name.setter
    def application_name(self, value: str):
        return jsii.set(self, "applicationName", value)

    @property
    @jsii.member(jsii_name="sourceBundle")
    def source_bundle(self) -> typing.Union[aws_cdk.cdk.IResolvable, "SourceBundleProperty"]:
        """``AWS::ElasticBeanstalk::ApplicationVersion.SourceBundle``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html#cfn-elasticbeanstalk-applicationversion-sourcebundle
        Stability:
            experimental
        """
        return jsii.get(self, "sourceBundle")

    @source_bundle.setter
    def source_bundle(self, value: typing.Union[aws_cdk.cdk.IResolvable, "SourceBundleProperty"]):
        return jsii.set(self, "sourceBundle", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::ApplicationVersion.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html#cfn-elasticbeanstalk-applicationversion-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplicationVersion.SourceBundleProperty", jsii_struct_bases=[])
    class SourceBundleProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-sourcebundle.html
        Stability:
            experimental
        """
        s3Bucket: str
        """``CfnApplicationVersion.SourceBundleProperty.S3Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-sourcebundle.html#cfn-beanstalk-sourcebundle-s3bucket
        Stability:
            experimental
        """

        s3Key: str
        """``CfnApplicationVersion.SourceBundleProperty.S3Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-sourcebundle.html#cfn-beanstalk-sourcebundle-s3key
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnApplicationVersionProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::ElasticBeanstalk::ApplicationVersion.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html#cfn-elasticbeanstalk-applicationversion-description
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplicationVersionProps", jsii_struct_bases=[_CfnApplicationVersionProps])
class CfnApplicationVersionProps(_CfnApplicationVersionProps):
    """Properties for defining a ``AWS::ElasticBeanstalk::ApplicationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html
    Stability:
        experimental
    """
    applicationName: str
    """``AWS::ElasticBeanstalk::ApplicationVersion.ApplicationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html#cfn-elasticbeanstalk-applicationversion-applicationname
    Stability:
        experimental
    """

    sourceBundle: typing.Union[aws_cdk.cdk.IResolvable, "CfnApplicationVersion.SourceBundleProperty"]
    """``AWS::ElasticBeanstalk::ApplicationVersion.SourceBundle``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html#cfn-elasticbeanstalk-applicationversion-sourcebundle
    Stability:
        experimental
    """

class CfnConfigurationTemplate(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnConfigurationTemplate"):
    """A CloudFormation ``AWS::ElasticBeanstalk::ConfigurationTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ElasticBeanstalk::ConfigurationTemplate
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, application_name: str, description: typing.Optional[str]=None, environment_id: typing.Optional[str]=None, option_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ConfigurationOptionSettingProperty"]]]]]=None, platform_arn: typing.Optional[str]=None, solution_stack_name: typing.Optional[str]=None, source_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SourceConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::ElasticBeanstalk::ConfigurationTemplate``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            applicationName: ``AWS::ElasticBeanstalk::ConfigurationTemplate.ApplicationName``.
            description: ``AWS::ElasticBeanstalk::ConfigurationTemplate.Description``.
            environmentId: ``AWS::ElasticBeanstalk::ConfigurationTemplate.EnvironmentId``.
            optionSettings: ``AWS::ElasticBeanstalk::ConfigurationTemplate.OptionSettings``.
            platformArn: ``AWS::ElasticBeanstalk::ConfigurationTemplate.PlatformArn``.
            solutionStackName: ``AWS::ElasticBeanstalk::ConfigurationTemplate.SolutionStackName``.
            sourceConfiguration: ``AWS::ElasticBeanstalk::ConfigurationTemplate.SourceConfiguration``.

        Stability:
            experimental
        """
        props: CfnConfigurationTemplateProps = {"applicationName": application_name}

        if description is not None:
            props["description"] = description

        if environment_id is not None:
            props["environmentId"] = environment_id

        if option_settings is not None:
            props["optionSettings"] = option_settings

        if platform_arn is not None:
            props["platformArn"] = platform_arn

        if solution_stack_name is not None:
            props["solutionStackName"] = solution_stack_name

        if source_configuration is not None:
            props["sourceConfiguration"] = source_configuration

        jsii.create(CfnConfigurationTemplate, self, [scope, id, props])

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
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """``AWS::ElasticBeanstalk::ConfigurationTemplate.ApplicationName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-applicationname
        Stability:
            experimental
        """
        return jsii.get(self, "applicationName")

    @application_name.setter
    def application_name(self, value: str):
        return jsii.set(self, "applicationName", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::ConfigurationTemplate.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="environmentId")
    def environment_id(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::ConfigurationTemplate.EnvironmentId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-environmentid
        Stability:
            experimental
        """
        return jsii.get(self, "environmentId")

    @environment_id.setter
    def environment_id(self, value: typing.Optional[str]):
        return jsii.set(self, "environmentId", value)

    @property
    @jsii.member(jsii_name="optionSettings")
    def option_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ConfigurationOptionSettingProperty"]]]]]:
        """``AWS::ElasticBeanstalk::ConfigurationTemplate.OptionSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-optionsettings
        Stability:
            experimental
        """
        return jsii.get(self, "optionSettings")

    @option_settings.setter
    def option_settings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ConfigurationOptionSettingProperty"]]]]]):
        return jsii.set(self, "optionSettings", value)

    @property
    @jsii.member(jsii_name="platformArn")
    def platform_arn(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::ConfigurationTemplate.PlatformArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-platformarn
        Stability:
            experimental
        """
        return jsii.get(self, "platformArn")

    @platform_arn.setter
    def platform_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "platformArn", value)

    @property
    @jsii.member(jsii_name="solutionStackName")
    def solution_stack_name(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::ConfigurationTemplate.SolutionStackName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-solutionstackname
        Stability:
            experimental
        """
        return jsii.get(self, "solutionStackName")

    @solution_stack_name.setter
    def solution_stack_name(self, value: typing.Optional[str]):
        return jsii.set(self, "solutionStackName", value)

    @property
    @jsii.member(jsii_name="sourceConfiguration")
    def source_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SourceConfigurationProperty"]]]:
        """``AWS::ElasticBeanstalk::ConfigurationTemplate.SourceConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-sourceconfiguration
        Stability:
            experimental
        """
        return jsii.get(self, "sourceConfiguration")

    @source_configuration.setter
    def source_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["SourceConfigurationProperty"]]]):
        return jsii.set(self, "sourceConfiguration", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ConfigurationOptionSettingProperty(jsii.compat.TypedDict, total=False):
        resourceName: str
        """``CfnConfigurationTemplate.ConfigurationOptionSettingProperty.ResourceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-configurationoptionsetting.html#cfn-elasticbeanstalk-configurationtemplate-configurationoptionsetting-resourcename
        Stability:
            experimental
        """
        value: str
        """``CfnConfigurationTemplate.ConfigurationOptionSettingProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-configurationoptionsetting.html#cfn-elasticbeanstalk-configurationtemplate-configurationoptionsetting-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnConfigurationTemplate.ConfigurationOptionSettingProperty", jsii_struct_bases=[_ConfigurationOptionSettingProperty])
    class ConfigurationOptionSettingProperty(_ConfigurationOptionSettingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-configurationoptionsetting.html
        Stability:
            experimental
        """
        namespace: str
        """``CfnConfigurationTemplate.ConfigurationOptionSettingProperty.Namespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-configurationoptionsetting.html#cfn-elasticbeanstalk-configurationtemplate-configurationoptionsetting-namespace
        Stability:
            experimental
        """

        optionName: str
        """``CfnConfigurationTemplate.ConfigurationOptionSettingProperty.OptionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-configurationoptionsetting.html#cfn-elasticbeanstalk-configurationtemplate-configurationoptionsetting-optionname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnConfigurationTemplate.SourceConfigurationProperty", jsii_struct_bases=[])
    class SourceConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-sourceconfiguration.html
        Stability:
            experimental
        """
        applicationName: str
        """``CfnConfigurationTemplate.SourceConfigurationProperty.ApplicationName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-sourceconfiguration.html#cfn-elasticbeanstalk-configurationtemplate-sourceconfiguration-applicationname
        Stability:
            experimental
        """

        templateName: str
        """``CfnConfigurationTemplate.SourceConfigurationProperty.TemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-sourceconfiguration.html#cfn-elasticbeanstalk-configurationtemplate-sourceconfiguration-templatename
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnConfigurationTemplateProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-description
    Stability:
        experimental
    """
    environmentId: str
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.EnvironmentId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-environmentid
    Stability:
        experimental
    """
    optionSettings: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnConfigurationTemplate.ConfigurationOptionSettingProperty"]]]
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.OptionSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-optionsettings
    Stability:
        experimental
    """
    platformArn: str
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.PlatformArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-platformarn
    Stability:
        experimental
    """
    solutionStackName: str
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.SolutionStackName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-solutionstackname
    Stability:
        experimental
    """
    sourceConfiguration: typing.Union[aws_cdk.cdk.IResolvable, "CfnConfigurationTemplate.SourceConfigurationProperty"]
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.SourceConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-sourceconfiguration
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnConfigurationTemplateProps", jsii_struct_bases=[_CfnConfigurationTemplateProps])
class CfnConfigurationTemplateProps(_CfnConfigurationTemplateProps):
    """Properties for defining a ``AWS::ElasticBeanstalk::ConfigurationTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html
    Stability:
        experimental
    """
    applicationName: str
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.ApplicationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-applicationname
    Stability:
        experimental
    """

class CfnEnvironment(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnEnvironment"):
    """A CloudFormation ``AWS::ElasticBeanstalk::Environment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html
    Stability:
        experimental
    cloudformationResource:
        AWS::ElasticBeanstalk::Environment
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, application_name: str, cname_prefix: typing.Optional[str]=None, description: typing.Optional[str]=None, environment_name: typing.Optional[str]=None, option_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "OptionSettingProperty"]]]]]=None, platform_arn: typing.Optional[str]=None, solution_stack_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.cdk.CfnTag]]=None, template_name: typing.Optional[str]=None, tier: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["TierProperty"]]]=None, version_label: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ElasticBeanstalk::Environment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            applicationName: ``AWS::ElasticBeanstalk::Environment.ApplicationName``.
            cnamePrefix: ``AWS::ElasticBeanstalk::Environment.CNAMEPrefix``.
            description: ``AWS::ElasticBeanstalk::Environment.Description``.
            environmentName: ``AWS::ElasticBeanstalk::Environment.EnvironmentName``.
            optionSettings: ``AWS::ElasticBeanstalk::Environment.OptionSettings``.
            platformArn: ``AWS::ElasticBeanstalk::Environment.PlatformArn``.
            solutionStackName: ``AWS::ElasticBeanstalk::Environment.SolutionStackName``.
            tags: ``AWS::ElasticBeanstalk::Environment.Tags``.
            templateName: ``AWS::ElasticBeanstalk::Environment.TemplateName``.
            tier: ``AWS::ElasticBeanstalk::Environment.Tier``.
            versionLabel: ``AWS::ElasticBeanstalk::Environment.VersionLabel``.

        Stability:
            experimental
        """
        props: CfnEnvironmentProps = {"applicationName": application_name}

        if cname_prefix is not None:
            props["cnamePrefix"] = cname_prefix

        if description is not None:
            props["description"] = description

        if environment_name is not None:
            props["environmentName"] = environment_name

        if option_settings is not None:
            props["optionSettings"] = option_settings

        if platform_arn is not None:
            props["platformArn"] = platform_arn

        if solution_stack_name is not None:
            props["solutionStackName"] = solution_stack_name

        if tags is not None:
            props["tags"] = tags

        if template_name is not None:
            props["templateName"] = template_name

        if tier is not None:
            props["tier"] = tier

        if version_label is not None:
            props["versionLabel"] = version_label

        jsii.create(CfnEnvironment, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrEndpointUrl")
    def attr_endpoint_url(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            EndpointURL
        """
        return jsii.get(self, "attrEndpointUrl")

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
        """``AWS::ElasticBeanstalk::Environment.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-elasticbeanstalk-environment-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """``AWS::ElasticBeanstalk::Environment.ApplicationName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-applicationname
        Stability:
            experimental
        """
        return jsii.get(self, "applicationName")

    @application_name.setter
    def application_name(self, value: str):
        return jsii.set(self, "applicationName", value)

    @property
    @jsii.member(jsii_name="cnamePrefix")
    def cname_prefix(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::Environment.CNAMEPrefix``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-cnameprefix
        Stability:
            experimental
        """
        return jsii.get(self, "cnamePrefix")

    @cname_prefix.setter
    def cname_prefix(self, value: typing.Optional[str]):
        return jsii.set(self, "cnamePrefix", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::Environment.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="environmentName")
    def environment_name(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::Environment.EnvironmentName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-name
        Stability:
            experimental
        """
        return jsii.get(self, "environmentName")

    @environment_name.setter
    def environment_name(self, value: typing.Optional[str]):
        return jsii.set(self, "environmentName", value)

    @property
    @jsii.member(jsii_name="optionSettings")
    def option_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "OptionSettingProperty"]]]]]:
        """``AWS::ElasticBeanstalk::Environment.OptionSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-optionsettings
        Stability:
            experimental
        """
        return jsii.get(self, "optionSettings")

    @option_settings.setter
    def option_settings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "OptionSettingProperty"]]]]]):
        return jsii.set(self, "optionSettings", value)

    @property
    @jsii.member(jsii_name="platformArn")
    def platform_arn(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::Environment.PlatformArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-platformarn
        Stability:
            experimental
        """
        return jsii.get(self, "platformArn")

    @platform_arn.setter
    def platform_arn(self, value: typing.Optional[str]):
        return jsii.set(self, "platformArn", value)

    @property
    @jsii.member(jsii_name="solutionStackName")
    def solution_stack_name(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::Environment.SolutionStackName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-solutionstackname
        Stability:
            experimental
        """
        return jsii.get(self, "solutionStackName")

    @solution_stack_name.setter
    def solution_stack_name(self, value: typing.Optional[str]):
        return jsii.set(self, "solutionStackName", value)

    @property
    @jsii.member(jsii_name="templateName")
    def template_name(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::Environment.TemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-templatename
        Stability:
            experimental
        """
        return jsii.get(self, "templateName")

    @template_name.setter
    def template_name(self, value: typing.Optional[str]):
        return jsii.set(self, "templateName", value)

    @property
    @jsii.member(jsii_name="tier")
    def tier(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["TierProperty"]]]:
        """``AWS::ElasticBeanstalk::Environment.Tier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-tier
        Stability:
            experimental
        """
        return jsii.get(self, "tier")

    @tier.setter
    def tier(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional["TierProperty"]]]):
        return jsii.set(self, "tier", value)

    @property
    @jsii.member(jsii_name="versionLabel")
    def version_label(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::Environment.VersionLabel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-versionlabel
        Stability:
            experimental
        """
        return jsii.get(self, "versionLabel")

    @version_label.setter
    def version_label(self, value: typing.Optional[str]):
        return jsii.set(self, "versionLabel", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _OptionSettingProperty(jsii.compat.TypedDict, total=False):
        resourceName: str
        """``CfnEnvironment.OptionSettingProperty.ResourceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-option-settings.html#cfn-elasticbeanstalk-environment-optionsetting-resourcename
        Stability:
            experimental
        """
        value: str
        """``CfnEnvironment.OptionSettingProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-option-settings.html#cfn-beanstalk-optionsettings-value
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnEnvironment.OptionSettingProperty", jsii_struct_bases=[_OptionSettingProperty])
    class OptionSettingProperty(_OptionSettingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-option-settings.html
        Stability:
            experimental
        """
        namespace: str
        """``CfnEnvironment.OptionSettingProperty.Namespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-option-settings.html#cfn-beanstalk-optionsettings-namespace
        Stability:
            experimental
        """

        optionName: str
        """``CfnEnvironment.OptionSettingProperty.OptionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-option-settings.html#cfn-beanstalk-optionsettings-optionname
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnEnvironment.TierProperty", jsii_struct_bases=[])
    class TierProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment-tier.html
        Stability:
            experimental
        """
        name: str
        """``CfnEnvironment.TierProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment-tier.html#cfn-beanstalk-env-tier-name
        Stability:
            experimental
        """

        type: str
        """``CfnEnvironment.TierProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment-tier.html#cfn-beanstalk-env-tier-type
        Stability:
            experimental
        """

        version: str
        """``CfnEnvironment.TierProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment-tier.html#cfn-beanstalk-env-tier-version
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEnvironmentProps(jsii.compat.TypedDict, total=False):
    cnamePrefix: str
    """``AWS::ElasticBeanstalk::Environment.CNAMEPrefix``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-cnameprefix
    Stability:
        experimental
    """
    description: str
    """``AWS::ElasticBeanstalk::Environment.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-description
    Stability:
        experimental
    """
    environmentName: str
    """``AWS::ElasticBeanstalk::Environment.EnvironmentName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-name
    Stability:
        experimental
    """
    optionSettings: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnEnvironment.OptionSettingProperty"]]]
    """``AWS::ElasticBeanstalk::Environment.OptionSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-optionsettings
    Stability:
        experimental
    """
    platformArn: str
    """``AWS::ElasticBeanstalk::Environment.PlatformArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-platformarn
    Stability:
        experimental
    """
    solutionStackName: str
    """``AWS::ElasticBeanstalk::Environment.SolutionStackName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-solutionstackname
    Stability:
        experimental
    """
    tags: typing.List[aws_cdk.cdk.CfnTag]
    """``AWS::ElasticBeanstalk::Environment.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-elasticbeanstalk-environment-tags
    Stability:
        experimental
    """
    templateName: str
    """``AWS::ElasticBeanstalk::Environment.TemplateName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-templatename
    Stability:
        experimental
    """
    tier: typing.Union[aws_cdk.cdk.IResolvable, "CfnEnvironment.TierProperty"]
    """``AWS::ElasticBeanstalk::Environment.Tier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-tier
    Stability:
        experimental
    """
    versionLabel: str
    """``AWS::ElasticBeanstalk::Environment.VersionLabel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-versionlabel
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnEnvironmentProps", jsii_struct_bases=[_CfnEnvironmentProps])
class CfnEnvironmentProps(_CfnEnvironmentProps):
    """Properties for defining a ``AWS::ElasticBeanstalk::Environment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html
    Stability:
        experimental
    """
    applicationName: str
    """``AWS::ElasticBeanstalk::Environment.ApplicationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-applicationname
    Stability:
        experimental
    """

__all__ = ["CfnApplication", "CfnApplicationProps", "CfnApplicationVersion", "CfnApplicationVersionProps", "CfnConfigurationTemplate", "CfnConfigurationTemplateProps", "CfnEnvironment", "CfnEnvironmentProps", "__jsii_assembly__"]

publication.publish()
