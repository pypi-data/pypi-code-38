import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-elasticbeanstalk", "0.36.0", __name__, "aws-elasticbeanstalk@0.36.0.jsii.tgz")
class CfnApplication(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplication"):
    """A CloudFormation ``AWS::ElasticBeanstalk::Application``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html
    Stability:
        stable
    cloudformationResource:
        AWS::ElasticBeanstalk::Application
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_name: typing.Optional[str]=None, description: typing.Optional[str]=None, resource_lifecycle_config: typing.Optional[typing.Union[typing.Optional["ApplicationResourceLifecycleConfigProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None) -> None:
        """Create a new ``AWS::ElasticBeanstalk::Application``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_name: ``AWS::ElasticBeanstalk::Application.ApplicationName``.
            description: ``AWS::ElasticBeanstalk::Application.Description``.
            resource_lifecycle_config: ``AWS::ElasticBeanstalk::Application.ResourceLifecycleConfig``.

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
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::Application.ApplicationName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html#cfn-elasticbeanstalk-application-name
        Stability:
            stable
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
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="resourceLifecycleConfig")
    def resource_lifecycle_config(self) -> typing.Optional[typing.Union[typing.Optional["ApplicationResourceLifecycleConfigProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::ElasticBeanstalk::Application.ResourceLifecycleConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html#cfn-elasticbeanstalk-application-resourcelifecycleconfig
        Stability:
            stable
        """
        return jsii.get(self, "resourceLifecycleConfig")

    @resource_lifecycle_config.setter
    def resource_lifecycle_config(self, value: typing.Optional[typing.Union[typing.Optional["ApplicationResourceLifecycleConfigProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "resourceLifecycleConfig", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplication.ApplicationResourceLifecycleConfigProperty", jsii_struct_bases=[])
    class ApplicationResourceLifecycleConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-applicationresourcelifecycleconfig.html
        Stability:
            stable
        """
        serviceRole: str
        """``CfnApplication.ApplicationResourceLifecycleConfigProperty.ServiceRole``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-applicationresourcelifecycleconfig.html#cfn-elasticbeanstalk-application-applicationresourcelifecycleconfig-servicerole
        Stability:
            stable
        """

        versionLifecycleConfig: typing.Union[aws_cdk.core.IResolvable, "CfnApplication.ApplicationVersionLifecycleConfigProperty"]
        """``CfnApplication.ApplicationResourceLifecycleConfigProperty.VersionLifecycleConfig``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-applicationresourcelifecycleconfig.html#cfn-elasticbeanstalk-application-applicationresourcelifecycleconfig-versionlifecycleconfig
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplication.ApplicationVersionLifecycleConfigProperty", jsii_struct_bases=[])
    class ApplicationVersionLifecycleConfigProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-applicationversionlifecycleconfig.html
        Stability:
            stable
        """
        maxAgeRule: typing.Union[aws_cdk.core.IResolvable, "CfnApplication.MaxAgeRuleProperty"]
        """``CfnApplication.ApplicationVersionLifecycleConfigProperty.MaxAgeRule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-applicationversionlifecycleconfig.html#cfn-elasticbeanstalk-application-applicationversionlifecycleconfig-maxagerule
        Stability:
            stable
        """

        maxCountRule: typing.Union[aws_cdk.core.IResolvable, "CfnApplication.MaxCountRuleProperty"]
        """``CfnApplication.ApplicationVersionLifecycleConfigProperty.MaxCountRule``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-applicationversionlifecycleconfig.html#cfn-elasticbeanstalk-application-applicationversionlifecycleconfig-maxcountrule
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplication.MaxAgeRuleProperty", jsii_struct_bases=[])
    class MaxAgeRuleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxagerule.html
        Stability:
            stable
        """
        deleteSourceFromS3: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnApplication.MaxAgeRuleProperty.DeleteSourceFromS3``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxagerule.html#cfn-elasticbeanstalk-application-maxagerule-deletesourcefroms3
        Stability:
            stable
        """

        enabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnApplication.MaxAgeRuleProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxagerule.html#cfn-elasticbeanstalk-application-maxagerule-enabled
        Stability:
            stable
        """

        maxAgeInDays: jsii.Number
        """``CfnApplication.MaxAgeRuleProperty.MaxAgeInDays``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxagerule.html#cfn-elasticbeanstalk-application-maxagerule-maxageindays
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplication.MaxCountRuleProperty", jsii_struct_bases=[])
    class MaxCountRuleProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxcountrule.html
        Stability:
            stable
        """
        deleteSourceFromS3: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnApplication.MaxCountRuleProperty.DeleteSourceFromS3``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxcountrule.html#cfn-elasticbeanstalk-application-maxcountrule-deletesourcefroms3
        Stability:
            stable
        """

        enabled: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnApplication.MaxCountRuleProperty.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxcountrule.html#cfn-elasticbeanstalk-application-maxcountrule-enabled
        Stability:
            stable
        """

        maxCount: jsii.Number
        """``CfnApplication.MaxCountRuleProperty.MaxCount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-application-maxcountrule.html#cfn-elasticbeanstalk-application-maxcountrule-maxcount
        Stability:
            stable
        """


@jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplicationProps", jsii_struct_bases=[])
class CfnApplicationProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::ElasticBeanstalk::Application``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html
    Stability:
        stable
    """
    applicationName: str
    """``AWS::ElasticBeanstalk::Application.ApplicationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html#cfn-elasticbeanstalk-application-name
    Stability:
        stable
    """

    description: str
    """``AWS::ElasticBeanstalk::Application.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html#cfn-elasticbeanstalk-application-description
    Stability:
        stable
    """

    resourceLifecycleConfig: typing.Union["CfnApplication.ApplicationResourceLifecycleConfigProperty", aws_cdk.core.IResolvable]
    """``AWS::ElasticBeanstalk::Application.ResourceLifecycleConfig``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk.html#cfn-elasticbeanstalk-application-resourcelifecycleconfig
    Stability:
        stable
    """

class CfnApplicationVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplicationVersion"):
    """A CloudFormation ``AWS::ElasticBeanstalk::ApplicationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html
    Stability:
        stable
    cloudformationResource:
        AWS::ElasticBeanstalk::ApplicationVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_name: str, source_bundle: typing.Union[aws_cdk.core.IResolvable, "SourceBundleProperty"], description: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ElasticBeanstalk::ApplicationVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_name: ``AWS::ElasticBeanstalk::ApplicationVersion.ApplicationName``.
            source_bundle: ``AWS::ElasticBeanstalk::ApplicationVersion.SourceBundle``.
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
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """``AWS::ElasticBeanstalk::ApplicationVersion.ApplicationName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html#cfn-elasticbeanstalk-applicationversion-applicationname
        Stability:
            stable
        """
        return jsii.get(self, "applicationName")

    @application_name.setter
    def application_name(self, value: str):
        return jsii.set(self, "applicationName", value)

    @property
    @jsii.member(jsii_name="sourceBundle")
    def source_bundle(self) -> typing.Union[aws_cdk.core.IResolvable, "SourceBundleProperty"]:
        """``AWS::ElasticBeanstalk::ApplicationVersion.SourceBundle``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html#cfn-elasticbeanstalk-applicationversion-sourcebundle
        Stability:
            stable
        """
        return jsii.get(self, "sourceBundle")

    @source_bundle.setter
    def source_bundle(self, value: typing.Union[aws_cdk.core.IResolvable, "SourceBundleProperty"]):
        return jsii.set(self, "sourceBundle", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::ApplicationVersion.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html#cfn-elasticbeanstalk-applicationversion-description
        Stability:
            stable
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
            stable
        """
        s3Bucket: str
        """``CfnApplicationVersion.SourceBundleProperty.S3Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-sourcebundle.html#cfn-beanstalk-sourcebundle-s3bucket
        Stability:
            stable
        """

        s3Key: str
        """``CfnApplicationVersion.SourceBundleProperty.S3Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-sourcebundle.html#cfn-beanstalk-sourcebundle-s3key
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnApplicationVersionProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::ElasticBeanstalk::ApplicationVersion.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html#cfn-elasticbeanstalk-applicationversion-description
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnApplicationVersionProps", jsii_struct_bases=[_CfnApplicationVersionProps])
class CfnApplicationVersionProps(_CfnApplicationVersionProps):
    """Properties for defining a ``AWS::ElasticBeanstalk::ApplicationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html
    Stability:
        stable
    """
    applicationName: str
    """``AWS::ElasticBeanstalk::ApplicationVersion.ApplicationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html#cfn-elasticbeanstalk-applicationversion-applicationname
    Stability:
        stable
    """

    sourceBundle: typing.Union[aws_cdk.core.IResolvable, "CfnApplicationVersion.SourceBundleProperty"]
    """``AWS::ElasticBeanstalk::ApplicationVersion.SourceBundle``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-version.html#cfn-elasticbeanstalk-applicationversion-sourcebundle
    Stability:
        stable
    """

class CfnConfigurationTemplate(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnConfigurationTemplate"):
    """A CloudFormation ``AWS::ElasticBeanstalk::ConfigurationTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html
    Stability:
        stable
    cloudformationResource:
        AWS::ElasticBeanstalk::ConfigurationTemplate
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_name: str, description: typing.Optional[str]=None, environment_id: typing.Optional[str]=None, option_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ConfigurationOptionSettingProperty"]]]]]=None, platform_arn: typing.Optional[str]=None, solution_stack_name: typing.Optional[str]=None, source_configuration: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SourceConfigurationProperty"]]]=None) -> None:
        """Create a new ``AWS::ElasticBeanstalk::ConfigurationTemplate``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_name: ``AWS::ElasticBeanstalk::ConfigurationTemplate.ApplicationName``.
            description: ``AWS::ElasticBeanstalk::ConfigurationTemplate.Description``.
            environment_id: ``AWS::ElasticBeanstalk::ConfigurationTemplate.EnvironmentId``.
            option_settings: ``AWS::ElasticBeanstalk::ConfigurationTemplate.OptionSettings``.
            platform_arn: ``AWS::ElasticBeanstalk::ConfigurationTemplate.PlatformArn``.
            solution_stack_name: ``AWS::ElasticBeanstalk::ConfigurationTemplate.SolutionStackName``.
            source_configuration: ``AWS::ElasticBeanstalk::ConfigurationTemplate.SourceConfiguration``.

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
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """``AWS::ElasticBeanstalk::ConfigurationTemplate.ApplicationName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-applicationname
        Stability:
            stable
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
            stable
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
            stable
        """
        return jsii.get(self, "environmentId")

    @environment_id.setter
    def environment_id(self, value: typing.Optional[str]):
        return jsii.set(self, "environmentId", value)

    @property
    @jsii.member(jsii_name="optionSettings")
    def option_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ConfigurationOptionSettingProperty"]]]]]:
        """``AWS::ElasticBeanstalk::ConfigurationTemplate.OptionSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-optionsettings
        Stability:
            stable
        """
        return jsii.get(self, "optionSettings")

    @option_settings.setter
    def option_settings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ConfigurationOptionSettingProperty"]]]]]):
        return jsii.set(self, "optionSettings", value)

    @property
    @jsii.member(jsii_name="platformArn")
    def platform_arn(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::ConfigurationTemplate.PlatformArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-platformarn
        Stability:
            stable
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
            stable
        """
        return jsii.get(self, "solutionStackName")

    @solution_stack_name.setter
    def solution_stack_name(self, value: typing.Optional[str]):
        return jsii.set(self, "solutionStackName", value)

    @property
    @jsii.member(jsii_name="sourceConfiguration")
    def source_configuration(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SourceConfigurationProperty"]]]:
        """``AWS::ElasticBeanstalk::ConfigurationTemplate.SourceConfiguration``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-sourceconfiguration
        Stability:
            stable
        """
        return jsii.get(self, "sourceConfiguration")

    @source_configuration.setter
    def source_configuration(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["SourceConfigurationProperty"]]]):
        return jsii.set(self, "sourceConfiguration", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _ConfigurationOptionSettingProperty(jsii.compat.TypedDict, total=False):
        resourceName: str
        """``CfnConfigurationTemplate.ConfigurationOptionSettingProperty.ResourceName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-configurationoptionsetting.html#cfn-elasticbeanstalk-configurationtemplate-configurationoptionsetting-resourcename
        Stability:
            stable
        """
        value: str
        """``CfnConfigurationTemplate.ConfigurationOptionSettingProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-configurationoptionsetting.html#cfn-elasticbeanstalk-configurationtemplate-configurationoptionsetting-value
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnConfigurationTemplate.ConfigurationOptionSettingProperty", jsii_struct_bases=[_ConfigurationOptionSettingProperty])
    class ConfigurationOptionSettingProperty(_ConfigurationOptionSettingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-configurationoptionsetting.html
        Stability:
            stable
        """
        namespace: str
        """``CfnConfigurationTemplate.ConfigurationOptionSettingProperty.Namespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-configurationoptionsetting.html#cfn-elasticbeanstalk-configurationtemplate-configurationoptionsetting-namespace
        Stability:
            stable
        """

        optionName: str
        """``CfnConfigurationTemplate.ConfigurationOptionSettingProperty.OptionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-configurationoptionsetting.html#cfn-elasticbeanstalk-configurationtemplate-configurationoptionsetting-optionname
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnConfigurationTemplate.SourceConfigurationProperty", jsii_struct_bases=[])
    class SourceConfigurationProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-sourceconfiguration.html
        Stability:
            stable
        """
        applicationName: str
        """``CfnConfigurationTemplate.SourceConfigurationProperty.ApplicationName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-sourceconfiguration.html#cfn-elasticbeanstalk-configurationtemplate-sourceconfiguration-applicationname
        Stability:
            stable
        """

        templateName: str
        """``CfnConfigurationTemplate.SourceConfigurationProperty.TemplateName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticbeanstalk-configurationtemplate-sourceconfiguration.html#cfn-elasticbeanstalk-configurationtemplate-sourceconfiguration-templatename
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnConfigurationTemplateProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-description
    Stability:
        stable
    """
    environmentId: str
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.EnvironmentId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-environmentid
    Stability:
        stable
    """
    optionSettings: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationTemplate.ConfigurationOptionSettingProperty"]]]
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.OptionSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-optionsettings
    Stability:
        stable
    """
    platformArn: str
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.PlatformArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-platformarn
    Stability:
        stable
    """
    solutionStackName: str
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.SolutionStackName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-solutionstackname
    Stability:
        stable
    """
    sourceConfiguration: typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationTemplate.SourceConfigurationProperty"]
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.SourceConfiguration``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-sourceconfiguration
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnConfigurationTemplateProps", jsii_struct_bases=[_CfnConfigurationTemplateProps])
class CfnConfigurationTemplateProps(_CfnConfigurationTemplateProps):
    """Properties for defining a ``AWS::ElasticBeanstalk::ConfigurationTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html
    Stability:
        stable
    """
    applicationName: str
    """``AWS::ElasticBeanstalk::ConfigurationTemplate.ApplicationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticbeanstalk-configurationtemplate.html#cfn-elasticbeanstalk-configurationtemplate-applicationname
    Stability:
        stable
    """

class CfnEnvironment(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnEnvironment"):
    """A CloudFormation ``AWS::ElasticBeanstalk::Environment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html
    Stability:
        stable
    cloudformationResource:
        AWS::ElasticBeanstalk::Environment
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application_name: str, cname_prefix: typing.Optional[str]=None, description: typing.Optional[str]=None, environment_name: typing.Optional[str]=None, option_settings: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "OptionSettingProperty"]]]]]=None, platform_arn: typing.Optional[str]=None, solution_stack_name: typing.Optional[str]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None, template_name: typing.Optional[str]=None, tier: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TierProperty"]]]=None, version_label: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::ElasticBeanstalk::Environment``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application_name: ``AWS::ElasticBeanstalk::Environment.ApplicationName``.
            cname_prefix: ``AWS::ElasticBeanstalk::Environment.CNAMEPrefix``.
            description: ``AWS::ElasticBeanstalk::Environment.Description``.
            environment_name: ``AWS::ElasticBeanstalk::Environment.EnvironmentName``.
            option_settings: ``AWS::ElasticBeanstalk::Environment.OptionSettings``.
            platform_arn: ``AWS::ElasticBeanstalk::Environment.PlatformArn``.
            solution_stack_name: ``AWS::ElasticBeanstalk::Environment.SolutionStackName``.
            tags: ``AWS::ElasticBeanstalk::Environment.Tags``.
            template_name: ``AWS::ElasticBeanstalk::Environment.TemplateName``.
            tier: ``AWS::ElasticBeanstalk::Environment.Tier``.
            version_label: ``AWS::ElasticBeanstalk::Environment.VersionLabel``.

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
    @jsii.member(jsii_name="attrEndpointUrl")
    def attr_endpoint_url(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            EndpointURL
        """
        return jsii.get(self, "attrEndpointUrl")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::ElasticBeanstalk::Environment.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-elasticbeanstalk-environment-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> str:
        """``AWS::ElasticBeanstalk::Environment.ApplicationName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-applicationname
        Stability:
            stable
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
            stable
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
            stable
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
            stable
        """
        return jsii.get(self, "environmentName")

    @environment_name.setter
    def environment_name(self, value: typing.Optional[str]):
        return jsii.set(self, "environmentName", value)

    @property
    @jsii.member(jsii_name="optionSettings")
    def option_settings(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "OptionSettingProperty"]]]]]:
        """``AWS::ElasticBeanstalk::Environment.OptionSettings``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-optionsettings
        Stability:
            stable
        """
        return jsii.get(self, "optionSettings")

    @option_settings.setter
    def option_settings(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "OptionSettingProperty"]]]]]):
        return jsii.set(self, "optionSettings", value)

    @property
    @jsii.member(jsii_name="platformArn")
    def platform_arn(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::Environment.PlatformArn``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-platformarn
        Stability:
            stable
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
            stable
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
            stable
        """
        return jsii.get(self, "templateName")

    @template_name.setter
    def template_name(self, value: typing.Optional[str]):
        return jsii.set(self, "templateName", value)

    @property
    @jsii.member(jsii_name="tier")
    def tier(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TierProperty"]]]:
        """``AWS::ElasticBeanstalk::Environment.Tier``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-tier
        Stability:
            stable
        """
        return jsii.get(self, "tier")

    @tier.setter
    def tier(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["TierProperty"]]]):
        return jsii.set(self, "tier", value)

    @property
    @jsii.member(jsii_name="versionLabel")
    def version_label(self) -> typing.Optional[str]:
        """``AWS::ElasticBeanstalk::Environment.VersionLabel``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-versionlabel
        Stability:
            stable
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
            stable
        """
        value: str
        """``CfnEnvironment.OptionSettingProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-option-settings.html#cfn-beanstalk-optionsettings-value
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnEnvironment.OptionSettingProperty", jsii_struct_bases=[_OptionSettingProperty])
    class OptionSettingProperty(_OptionSettingProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-option-settings.html
        Stability:
            stable
        """
        namespace: str
        """``CfnEnvironment.OptionSettingProperty.Namespace``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-option-settings.html#cfn-beanstalk-optionsettings-namespace
        Stability:
            stable
        """

        optionName: str
        """``CfnEnvironment.OptionSettingProperty.OptionName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-option-settings.html#cfn-beanstalk-optionsettings-optionname
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnEnvironment.TierProperty", jsii_struct_bases=[])
    class TierProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment-tier.html
        Stability:
            stable
        """
        name: str
        """``CfnEnvironment.TierProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment-tier.html#cfn-beanstalk-env-tier-name
        Stability:
            stable
        """

        type: str
        """``CfnEnvironment.TierProperty.Type``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment-tier.html#cfn-beanstalk-env-tier-type
        Stability:
            stable
        """

        version: str
        """``CfnEnvironment.TierProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment-tier.html#cfn-beanstalk-env-tier-version
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnEnvironmentProps(jsii.compat.TypedDict, total=False):
    cnamePrefix: str
    """``AWS::ElasticBeanstalk::Environment.CNAMEPrefix``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-cnameprefix
    Stability:
        stable
    """
    description: str
    """``AWS::ElasticBeanstalk::Environment.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-description
    Stability:
        stable
    """
    environmentName: str
    """``AWS::ElasticBeanstalk::Environment.EnvironmentName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-name
    Stability:
        stable
    """
    optionSettings: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnEnvironment.OptionSettingProperty"]]]
    """``AWS::ElasticBeanstalk::Environment.OptionSettings``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-optionsettings
    Stability:
        stable
    """
    platformArn: str
    """``AWS::ElasticBeanstalk::Environment.PlatformArn``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-platformarn
    Stability:
        stable
    """
    solutionStackName: str
    """``AWS::ElasticBeanstalk::Environment.SolutionStackName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-solutionstackname
    Stability:
        stable
    """
    tags: typing.List[aws_cdk.core.CfnTag]
    """``AWS::ElasticBeanstalk::Environment.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-elasticbeanstalk-environment-tags
    Stability:
        stable
    """
    templateName: str
    """``AWS::ElasticBeanstalk::Environment.TemplateName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-templatename
    Stability:
        stable
    """
    tier: typing.Union[aws_cdk.core.IResolvable, "CfnEnvironment.TierProperty"]
    """``AWS::ElasticBeanstalk::Environment.Tier``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-tier
    Stability:
        stable
    """
    versionLabel: str
    """``AWS::ElasticBeanstalk::Environment.VersionLabel``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-versionlabel
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-elasticbeanstalk.CfnEnvironmentProps", jsii_struct_bases=[_CfnEnvironmentProps])
class CfnEnvironmentProps(_CfnEnvironmentProps):
    """Properties for defining a ``AWS::ElasticBeanstalk::Environment``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html
    Stability:
        stable
    """
    applicationName: str
    """``AWS::ElasticBeanstalk::Environment.ApplicationName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-applicationname
    Stability:
        stable
    """

__all__ = ["CfnApplication", "CfnApplicationProps", "CfnApplicationVersion", "CfnApplicationVersionProps", "CfnConfigurationTemplate", "CfnConfigurationTemplateProps", "CfnEnvironment", "CfnEnvironmentProps", "__jsii_assembly__"]

publication.publish()
