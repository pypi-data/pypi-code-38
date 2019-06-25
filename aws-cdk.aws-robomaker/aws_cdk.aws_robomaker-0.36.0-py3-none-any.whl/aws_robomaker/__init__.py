import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-robomaker", "0.36.0", __name__, "aws-robomaker@0.36.0.jsii.tgz")
class CfnFleet(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-robomaker.CfnFleet"):
    """A CloudFormation ``AWS::RoboMaker::Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-fleet.html
    Stability:
        stable
    cloudformationResource:
        AWS::RoboMaker::Fleet
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: typing.Optional[str]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::RoboMaker::Fleet``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::RoboMaker::Fleet.Name``.
            tags: ``AWS::RoboMaker::Fleet.Tags``.

        Stability:
            experimental
        """
        props: CfnFleetProps = {}

        if name is not None:
            props["name"] = name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnFleet, self, [scope, id, props])

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
        """``AWS::RoboMaker::Fleet.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-fleet.html#cfn-robomaker-fleet-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::RoboMaker::Fleet.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-fleet.html#cfn-robomaker-fleet-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnFleetProps", jsii_struct_bases=[])
class CfnFleetProps(jsii.compat.TypedDict, total=False):
    """Properties for defining a ``AWS::RoboMaker::Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-fleet.html
    Stability:
        stable
    """
    name: str
    """``AWS::RoboMaker::Fleet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-fleet.html#cfn-robomaker-fleet-name
    Stability:
        stable
    """

    tags: typing.Any
    """``AWS::RoboMaker::Fleet.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-fleet.html#cfn-robomaker-fleet-tags
    Stability:
        stable
    """

class CfnRobot(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-robomaker.CfnRobot"):
    """A CloudFormation ``AWS::RoboMaker::Robot``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html
    Stability:
        stable
    cloudformationResource:
        AWS::RoboMaker::Robot
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, architecture: str, greengrass_group_id: str, fleet: typing.Optional[str]=None, name: typing.Optional[str]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::RoboMaker::Robot``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            architecture: ``AWS::RoboMaker::Robot.Architecture``.
            greengrass_group_id: ``AWS::RoboMaker::Robot.GreengrassGroupId``.
            fleet: ``AWS::RoboMaker::Robot.Fleet``.
            name: ``AWS::RoboMaker::Robot.Name``.
            tags: ``AWS::RoboMaker::Robot.Tags``.

        Stability:
            experimental
        """
        props: CfnRobotProps = {"architecture": architecture, "greengrassGroupId": greengrass_group_id}

        if fleet is not None:
            props["fleet"] = fleet

        if name is not None:
            props["name"] = name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnRobot, self, [scope, id, props])

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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::RoboMaker::Robot.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="architecture")
    def architecture(self) -> str:
        """``AWS::RoboMaker::Robot.Architecture``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-architecture
        Stability:
            stable
        """
        return jsii.get(self, "architecture")

    @architecture.setter
    def architecture(self, value: str):
        return jsii.set(self, "architecture", value)

    @property
    @jsii.member(jsii_name="greengrassGroupId")
    def greengrass_group_id(self) -> str:
        """``AWS::RoboMaker::Robot.GreengrassGroupId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-greengrassgroupid
        Stability:
            stable
        """
        return jsii.get(self, "greengrassGroupId")

    @greengrass_group_id.setter
    def greengrass_group_id(self, value: str):
        return jsii.set(self, "greengrassGroupId", value)

    @property
    @jsii.member(jsii_name="fleet")
    def fleet(self) -> typing.Optional[str]:
        """``AWS::RoboMaker::Robot.Fleet``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-fleet
        Stability:
            stable
        """
        return jsii.get(self, "fleet")

    @fleet.setter
    def fleet(self, value: typing.Optional[str]):
        return jsii.set(self, "fleet", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::RoboMaker::Robot.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


class CfnRobotApplication(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-robomaker.CfnRobotApplication"):
    """A CloudFormation ``AWS::RoboMaker::RobotApplication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html
    Stability:
        stable
    cloudformationResource:
        AWS::RoboMaker::RobotApplication
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, robot_software_suite: typing.Union["RobotSoftwareSuiteProperty", aws_cdk.core.IResolvable], sources: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "SourceConfigProperty"]]], current_revision_id: typing.Optional[str]=None, name: typing.Optional[str]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::RoboMaker::RobotApplication``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            robot_software_suite: ``AWS::RoboMaker::RobotApplication.RobotSoftwareSuite``.
            sources: ``AWS::RoboMaker::RobotApplication.Sources``.
            current_revision_id: ``AWS::RoboMaker::RobotApplication.CurrentRevisionId``.
            name: ``AWS::RoboMaker::RobotApplication.Name``.
            tags: ``AWS::RoboMaker::RobotApplication.Tags``.

        Stability:
            experimental
        """
        props: CfnRobotApplicationProps = {"robotSoftwareSuite": robot_software_suite, "sources": sources}

        if current_revision_id is not None:
            props["currentRevisionId"] = current_revision_id

        if name is not None:
            props["name"] = name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnRobotApplication, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrCurrentRevisionId")
    def attr_current_revision_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            CurrentRevisionId
        """
        return jsii.get(self, "attrCurrentRevisionId")

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
        """``AWS::RoboMaker::RobotApplication.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="robotSoftwareSuite")
    def robot_software_suite(self) -> typing.Union["RobotSoftwareSuiteProperty", aws_cdk.core.IResolvable]:
        """``AWS::RoboMaker::RobotApplication.RobotSoftwareSuite``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-robotsoftwaresuite
        Stability:
            stable
        """
        return jsii.get(self, "robotSoftwareSuite")

    @robot_software_suite.setter
    def robot_software_suite(self, value: typing.Union["RobotSoftwareSuiteProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "robotSoftwareSuite", value)

    @property
    @jsii.member(jsii_name="sources")
    def sources(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "SourceConfigProperty"]]]:
        """``AWS::RoboMaker::RobotApplication.Sources``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-sources
        Stability:
            stable
        """
        return jsii.get(self, "sources")

    @sources.setter
    def sources(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "SourceConfigProperty"]]]):
        return jsii.set(self, "sources", value)

    @property
    @jsii.member(jsii_name="currentRevisionId")
    def current_revision_id(self) -> typing.Optional[str]:
        """``AWS::RoboMaker::RobotApplication.CurrentRevisionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-currentrevisionid
        Stability:
            stable
        """
        return jsii.get(self, "currentRevisionId")

    @current_revision_id.setter
    def current_revision_id(self, value: typing.Optional[str]):
        return jsii.set(self, "currentRevisionId", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::RoboMaker::RobotApplication.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnRobotApplication.RobotSoftwareSuiteProperty", jsii_struct_bases=[])
    class RobotSoftwareSuiteProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-robotsoftwaresuite.html
        Stability:
            stable
        """
        name: str
        """``CfnRobotApplication.RobotSoftwareSuiteProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-robotsoftwaresuite.html#cfn-robomaker-robotapplication-robotsoftwaresuite-name
        Stability:
            stable
        """

        version: str
        """``CfnRobotApplication.RobotSoftwareSuiteProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-robotsoftwaresuite.html#cfn-robomaker-robotapplication-robotsoftwaresuite-version
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnRobotApplication.SourceConfigProperty", jsii_struct_bases=[])
    class SourceConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-sourceconfig.html
        Stability:
            stable
        """
        architecture: str
        """``CfnRobotApplication.SourceConfigProperty.Architecture``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-sourceconfig.html#cfn-robomaker-robotapplication-sourceconfig-architecture
        Stability:
            stable
        """

        s3Bucket: str
        """``CfnRobotApplication.SourceConfigProperty.S3Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-sourceconfig.html#cfn-robomaker-robotapplication-sourceconfig-s3bucket
        Stability:
            stable
        """

        s3Key: str
        """``CfnRobotApplication.SourceConfigProperty.S3Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-sourceconfig.html#cfn-robomaker-robotapplication-sourceconfig-s3key
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRobotApplicationProps(jsii.compat.TypedDict, total=False):
    currentRevisionId: str
    """``AWS::RoboMaker::RobotApplication.CurrentRevisionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-currentrevisionid
    Stability:
        stable
    """
    name: str
    """``AWS::RoboMaker::RobotApplication.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-name
    Stability:
        stable
    """
    tags: typing.Any
    """``AWS::RoboMaker::RobotApplication.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnRobotApplicationProps", jsii_struct_bases=[_CfnRobotApplicationProps])
class CfnRobotApplicationProps(_CfnRobotApplicationProps):
    """Properties for defining a ``AWS::RoboMaker::RobotApplication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html
    Stability:
        stable
    """
    robotSoftwareSuite: typing.Union["CfnRobotApplication.RobotSoftwareSuiteProperty", aws_cdk.core.IResolvable]
    """``AWS::RoboMaker::RobotApplication.RobotSoftwareSuite``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-robotsoftwaresuite
    Stability:
        stable
    """

    sources: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRobotApplication.SourceConfigProperty"]]]
    """``AWS::RoboMaker::RobotApplication.Sources``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-sources
    Stability:
        stable
    """

class CfnRobotApplicationVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-robomaker.CfnRobotApplicationVersion"):
    """A CloudFormation ``AWS::RoboMaker::RobotApplicationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplicationversion.html
    Stability:
        stable
    cloudformationResource:
        AWS::RoboMaker::RobotApplicationVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application: str, current_revision_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::RoboMaker::RobotApplicationVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application: ``AWS::RoboMaker::RobotApplicationVersion.Application``.
            current_revision_id: ``AWS::RoboMaker::RobotApplicationVersion.CurrentRevisionId``.

        Stability:
            experimental
        """
        props: CfnRobotApplicationVersionProps = {"application": application}

        if current_revision_id is not None:
            props["currentRevisionId"] = current_revision_id

        jsii.create(CfnRobotApplicationVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="application")
    def application(self) -> str:
        """``AWS::RoboMaker::RobotApplicationVersion.Application``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplicationversion.html#cfn-robomaker-robotapplicationversion-application
        Stability:
            stable
        """
        return jsii.get(self, "application")

    @application.setter
    def application(self, value: str):
        return jsii.set(self, "application", value)

    @property
    @jsii.member(jsii_name="currentRevisionId")
    def current_revision_id(self) -> typing.Optional[str]:
        """``AWS::RoboMaker::RobotApplicationVersion.CurrentRevisionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplicationversion.html#cfn-robomaker-robotapplicationversion-currentrevisionid
        Stability:
            stable
        """
        return jsii.get(self, "currentRevisionId")

    @current_revision_id.setter
    def current_revision_id(self, value: typing.Optional[str]):
        return jsii.set(self, "currentRevisionId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRobotApplicationVersionProps(jsii.compat.TypedDict, total=False):
    currentRevisionId: str
    """``AWS::RoboMaker::RobotApplicationVersion.CurrentRevisionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplicationversion.html#cfn-robomaker-robotapplicationversion-currentrevisionid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnRobotApplicationVersionProps", jsii_struct_bases=[_CfnRobotApplicationVersionProps])
class CfnRobotApplicationVersionProps(_CfnRobotApplicationVersionProps):
    """Properties for defining a ``AWS::RoboMaker::RobotApplicationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplicationversion.html
    Stability:
        stable
    """
    application: str
    """``AWS::RoboMaker::RobotApplicationVersion.Application``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplicationversion.html#cfn-robomaker-robotapplicationversion-application
    Stability:
        stable
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRobotProps(jsii.compat.TypedDict, total=False):
    fleet: str
    """``AWS::RoboMaker::Robot.Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-fleet
    Stability:
        stable
    """
    name: str
    """``AWS::RoboMaker::Robot.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-name
    Stability:
        stable
    """
    tags: typing.Any
    """``AWS::RoboMaker::Robot.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnRobotProps", jsii_struct_bases=[_CfnRobotProps])
class CfnRobotProps(_CfnRobotProps):
    """Properties for defining a ``AWS::RoboMaker::Robot``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html
    Stability:
        stable
    """
    architecture: str
    """``AWS::RoboMaker::Robot.Architecture``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-architecture
    Stability:
        stable
    """

    greengrassGroupId: str
    """``AWS::RoboMaker::Robot.GreengrassGroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-greengrassgroupid
    Stability:
        stable
    """

class CfnSimulationApplication(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplication"):
    """A CloudFormation ``AWS::RoboMaker::SimulationApplication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html
    Stability:
        stable
    cloudformationResource:
        AWS::RoboMaker::SimulationApplication
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, rendering_engine: typing.Union[aws_cdk.core.IResolvable, "RenderingEngineProperty"], robot_software_suite: typing.Union[aws_cdk.core.IResolvable, "RobotSoftwareSuiteProperty"], simulation_software_suite: typing.Union[aws_cdk.core.IResolvable, "SimulationSoftwareSuiteProperty"], sources: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "SourceConfigProperty"]]], current_revision_id: typing.Optional[str]=None, name: typing.Optional[str]=None, tags: typing.Any=None) -> None:
        """Create a new ``AWS::RoboMaker::SimulationApplication``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            rendering_engine: ``AWS::RoboMaker::SimulationApplication.RenderingEngine``.
            robot_software_suite: ``AWS::RoboMaker::SimulationApplication.RobotSoftwareSuite``.
            simulation_software_suite: ``AWS::RoboMaker::SimulationApplication.SimulationSoftwareSuite``.
            sources: ``AWS::RoboMaker::SimulationApplication.Sources``.
            current_revision_id: ``AWS::RoboMaker::SimulationApplication.CurrentRevisionId``.
            name: ``AWS::RoboMaker::SimulationApplication.Name``.
            tags: ``AWS::RoboMaker::SimulationApplication.Tags``.

        Stability:
            experimental
        """
        props: CfnSimulationApplicationProps = {"renderingEngine": rendering_engine, "robotSoftwareSuite": robot_software_suite, "simulationSoftwareSuite": simulation_software_suite, "sources": sources}

        if current_revision_id is not None:
            props["currentRevisionId"] = current_revision_id

        if name is not None:
            props["name"] = name

        if tags is not None:
            props["tags"] = tags

        jsii.create(CfnSimulationApplication, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrCurrentRevisionId")
    def attr_current_revision_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            CurrentRevisionId
        """
        return jsii.get(self, "attrCurrentRevisionId")

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
        """``AWS::RoboMaker::SimulationApplication.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-tags
        Stability:
            stable
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="renderingEngine")
    def rendering_engine(self) -> typing.Union[aws_cdk.core.IResolvable, "RenderingEngineProperty"]:
        """``AWS::RoboMaker::SimulationApplication.RenderingEngine``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-renderingengine
        Stability:
            stable
        """
        return jsii.get(self, "renderingEngine")

    @rendering_engine.setter
    def rendering_engine(self, value: typing.Union[aws_cdk.core.IResolvable, "RenderingEngineProperty"]):
        return jsii.set(self, "renderingEngine", value)

    @property
    @jsii.member(jsii_name="robotSoftwareSuite")
    def robot_software_suite(self) -> typing.Union[aws_cdk.core.IResolvable, "RobotSoftwareSuiteProperty"]:
        """``AWS::RoboMaker::SimulationApplication.RobotSoftwareSuite``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-robotsoftwaresuite
        Stability:
            stable
        """
        return jsii.get(self, "robotSoftwareSuite")

    @robot_software_suite.setter
    def robot_software_suite(self, value: typing.Union[aws_cdk.core.IResolvable, "RobotSoftwareSuiteProperty"]):
        return jsii.set(self, "robotSoftwareSuite", value)

    @property
    @jsii.member(jsii_name="simulationSoftwareSuite")
    def simulation_software_suite(self) -> typing.Union[aws_cdk.core.IResolvable, "SimulationSoftwareSuiteProperty"]:
        """``AWS::RoboMaker::SimulationApplication.SimulationSoftwareSuite``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-simulationsoftwaresuite
        Stability:
            stable
        """
        return jsii.get(self, "simulationSoftwareSuite")

    @simulation_software_suite.setter
    def simulation_software_suite(self, value: typing.Union[aws_cdk.core.IResolvable, "SimulationSoftwareSuiteProperty"]):
        return jsii.set(self, "simulationSoftwareSuite", value)

    @property
    @jsii.member(jsii_name="sources")
    def sources(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "SourceConfigProperty"]]]:
        """``AWS::RoboMaker::SimulationApplication.Sources``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-sources
        Stability:
            stable
        """
        return jsii.get(self, "sources")

    @sources.setter
    def sources(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "SourceConfigProperty"]]]):
        return jsii.set(self, "sources", value)

    @property
    @jsii.member(jsii_name="currentRevisionId")
    def current_revision_id(self) -> typing.Optional[str]:
        """``AWS::RoboMaker::SimulationApplication.CurrentRevisionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-currentrevisionid
        Stability:
            stable
        """
        return jsii.get(self, "currentRevisionId")

    @current_revision_id.setter
    def current_revision_id(self, value: typing.Optional[str]):
        return jsii.set(self, "currentRevisionId", value)

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::RoboMaker::SimulationApplication.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplication.RenderingEngineProperty", jsii_struct_bases=[])
    class RenderingEngineProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-renderingengine.html
        Stability:
            stable
        """
        name: str
        """``CfnSimulationApplication.RenderingEngineProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-renderingengine.html#cfn-robomaker-simulationapplication-renderingengine-name
        Stability:
            stable
        """

        version: str
        """``CfnSimulationApplication.RenderingEngineProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-renderingengine.html#cfn-robomaker-simulationapplication-renderingengine-version
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplication.RobotSoftwareSuiteProperty", jsii_struct_bases=[])
    class RobotSoftwareSuiteProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-robotsoftwaresuite.html
        Stability:
            stable
        """
        name: str
        """``CfnSimulationApplication.RobotSoftwareSuiteProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-robotsoftwaresuite.html#cfn-robomaker-simulationapplication-robotsoftwaresuite-name
        Stability:
            stable
        """

        version: str
        """``CfnSimulationApplication.RobotSoftwareSuiteProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-robotsoftwaresuite.html#cfn-robomaker-simulationapplication-robotsoftwaresuite-version
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplication.SimulationSoftwareSuiteProperty", jsii_struct_bases=[])
    class SimulationSoftwareSuiteProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-simulationsoftwaresuite.html
        Stability:
            stable
        """
        name: str
        """``CfnSimulationApplication.SimulationSoftwareSuiteProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-simulationsoftwaresuite.html#cfn-robomaker-simulationapplication-simulationsoftwaresuite-name
        Stability:
            stable
        """

        version: str
        """``CfnSimulationApplication.SimulationSoftwareSuiteProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-simulationsoftwaresuite.html#cfn-robomaker-simulationapplication-simulationsoftwaresuite-version
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplication.SourceConfigProperty", jsii_struct_bases=[])
    class SourceConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-sourceconfig.html
        Stability:
            stable
        """
        architecture: str
        """``CfnSimulationApplication.SourceConfigProperty.Architecture``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-sourceconfig.html#cfn-robomaker-simulationapplication-sourceconfig-architecture
        Stability:
            stable
        """

        s3Bucket: str
        """``CfnSimulationApplication.SourceConfigProperty.S3Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-sourceconfig.html#cfn-robomaker-simulationapplication-sourceconfig-s3bucket
        Stability:
            stable
        """

        s3Key: str
        """``CfnSimulationApplication.SourceConfigProperty.S3Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-sourceconfig.html#cfn-robomaker-simulationapplication-sourceconfig-s3key
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSimulationApplicationProps(jsii.compat.TypedDict, total=False):
    currentRevisionId: str
    """``AWS::RoboMaker::SimulationApplication.CurrentRevisionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-currentrevisionid
    Stability:
        stable
    """
    name: str
    """``AWS::RoboMaker::SimulationApplication.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-name
    Stability:
        stable
    """
    tags: typing.Any
    """``AWS::RoboMaker::SimulationApplication.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-tags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplicationProps", jsii_struct_bases=[_CfnSimulationApplicationProps])
class CfnSimulationApplicationProps(_CfnSimulationApplicationProps):
    """Properties for defining a ``AWS::RoboMaker::SimulationApplication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html
    Stability:
        stable
    """
    renderingEngine: typing.Union[aws_cdk.core.IResolvable, "CfnSimulationApplication.RenderingEngineProperty"]
    """``AWS::RoboMaker::SimulationApplication.RenderingEngine``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-renderingengine
    Stability:
        stable
    """

    robotSoftwareSuite: typing.Union[aws_cdk.core.IResolvable, "CfnSimulationApplication.RobotSoftwareSuiteProperty"]
    """``AWS::RoboMaker::SimulationApplication.RobotSoftwareSuite``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-robotsoftwaresuite
    Stability:
        stable
    """

    simulationSoftwareSuite: typing.Union[aws_cdk.core.IResolvable, "CfnSimulationApplication.SimulationSoftwareSuiteProperty"]
    """``AWS::RoboMaker::SimulationApplication.SimulationSoftwareSuite``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-simulationsoftwaresuite
    Stability:
        stable
    """

    sources: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnSimulationApplication.SourceConfigProperty"]]]
    """``AWS::RoboMaker::SimulationApplication.Sources``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-sources
    Stability:
        stable
    """

class CfnSimulationApplicationVersion(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplicationVersion"):
    """A CloudFormation ``AWS::RoboMaker::SimulationApplicationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplicationversion.html
    Stability:
        stable
    cloudformationResource:
        AWS::RoboMaker::SimulationApplicationVersion
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, application: str, current_revision_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::RoboMaker::SimulationApplicationVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application: ``AWS::RoboMaker::SimulationApplicationVersion.Application``.
            current_revision_id: ``AWS::RoboMaker::SimulationApplicationVersion.CurrentRevisionId``.

        Stability:
            experimental
        """
        props: CfnSimulationApplicationVersionProps = {"application": application}

        if current_revision_id is not None:
            props["currentRevisionId"] = current_revision_id

        jsii.create(CfnSimulationApplicationVersion, self, [scope, id, props])

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
    @jsii.member(jsii_name="application")
    def application(self) -> str:
        """``AWS::RoboMaker::SimulationApplicationVersion.Application``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplicationversion.html#cfn-robomaker-simulationapplicationversion-application
        Stability:
            stable
        """
        return jsii.get(self, "application")

    @application.setter
    def application(self, value: str):
        return jsii.set(self, "application", value)

    @property
    @jsii.member(jsii_name="currentRevisionId")
    def current_revision_id(self) -> typing.Optional[str]:
        """``AWS::RoboMaker::SimulationApplicationVersion.CurrentRevisionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplicationversion.html#cfn-robomaker-simulationapplicationversion-currentrevisionid
        Stability:
            stable
        """
        return jsii.get(self, "currentRevisionId")

    @current_revision_id.setter
    def current_revision_id(self, value: typing.Optional[str]):
        return jsii.set(self, "currentRevisionId", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSimulationApplicationVersionProps(jsii.compat.TypedDict, total=False):
    currentRevisionId: str
    """``AWS::RoboMaker::SimulationApplicationVersion.CurrentRevisionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplicationversion.html#cfn-robomaker-simulationapplicationversion-currentrevisionid
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplicationVersionProps", jsii_struct_bases=[_CfnSimulationApplicationVersionProps])
class CfnSimulationApplicationVersionProps(_CfnSimulationApplicationVersionProps):
    """Properties for defining a ``AWS::RoboMaker::SimulationApplicationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplicationversion.html
    Stability:
        stable
    """
    application: str
    """``AWS::RoboMaker::SimulationApplicationVersion.Application``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplicationversion.html#cfn-robomaker-simulationapplicationversion-application
    Stability:
        stable
    """

__all__ = ["CfnFleet", "CfnFleetProps", "CfnRobot", "CfnRobotApplication", "CfnRobotApplicationProps", "CfnRobotApplicationVersion", "CfnRobotApplicationVersionProps", "CfnRobotProps", "CfnSimulationApplication", "CfnSimulationApplicationProps", "CfnSimulationApplicationVersion", "CfnSimulationApplicationVersionProps", "__jsii_assembly__"]

publication.publish()
