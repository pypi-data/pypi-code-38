import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-robomaker", "0.35.0", __name__, "aws-robomaker@0.35.0.jsii.tgz")
class CfnFleet(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-robomaker.CfnFleet"):
    """A CloudFormation ``AWS::RoboMaker::Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-fleet.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RoboMaker::Fleet
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[typing.Any, typing.Any]]=None) -> None:
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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

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
        """``AWS::RoboMaker::Fleet.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-fleet.html#cfn-robomaker-fleet-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[str]:
        """``AWS::RoboMaker::Fleet.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-fleet.html#cfn-robomaker-fleet-name
        Stability:
            experimental
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
        experimental
    """
    name: str
    """``AWS::RoboMaker::Fleet.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-fleet.html#cfn-robomaker-fleet-name
    Stability:
        experimental
    """

    tags: typing.Mapping[typing.Any, typing.Any]
    """``AWS::RoboMaker::Fleet.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-fleet.html#cfn-robomaker-fleet-tags
    Stability:
        experimental
    """

class CfnRobot(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-robomaker.CfnRobot"):
    """A CloudFormation ``AWS::RoboMaker::Robot``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RoboMaker::Robot
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, architecture: str, greengrass_group_id: str, fleet: typing.Optional[str]=None, name: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[typing.Any, typing.Any]]=None) -> None:
        """Create a new ``AWS::RoboMaker::Robot``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            architecture: ``AWS::RoboMaker::Robot.Architecture``.
            greengrassGroupId: ``AWS::RoboMaker::Robot.GreengrassGroupId``.
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
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.cdk.TagManager:
        """``AWS::RoboMaker::Robot.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="architecture")
    def architecture(self) -> str:
        """``AWS::RoboMaker::Robot.Architecture``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-architecture
        Stability:
            experimental
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
            experimental
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
            experimental
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
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: typing.Optional[str]):
        return jsii.set(self, "name", value)


class CfnRobotApplication(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-robomaker.CfnRobotApplication"):
    """A CloudFormation ``AWS::RoboMaker::RobotApplication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RoboMaker::RobotApplication
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, robot_software_suite: typing.Union["RobotSoftwareSuiteProperty", aws_cdk.cdk.IResolvable], sources: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "SourceConfigProperty"]]], current_revision_id: typing.Optional[str]=None, name: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[typing.Any, typing.Any]]=None) -> None:
        """Create a new ``AWS::RoboMaker::RobotApplication``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            robotSoftwareSuite: ``AWS::RoboMaker::RobotApplication.RobotSoftwareSuite``.
            sources: ``AWS::RoboMaker::RobotApplication.Sources``.
            currentRevisionId: ``AWS::RoboMaker::RobotApplication.CurrentRevisionId``.
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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrCurrentRevisionId")
    def attr_current_revision_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            CurrentRevisionId
        """
        return jsii.get(self, "attrCurrentRevisionId")

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
        """``AWS::RoboMaker::RobotApplication.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="robotSoftwareSuite")
    def robot_software_suite(self) -> typing.Union["RobotSoftwareSuiteProperty", aws_cdk.cdk.IResolvable]:
        """``AWS::RoboMaker::RobotApplication.RobotSoftwareSuite``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-robotsoftwaresuite
        Stability:
            experimental
        """
        return jsii.get(self, "robotSoftwareSuite")

    @robot_software_suite.setter
    def robot_software_suite(self, value: typing.Union["RobotSoftwareSuiteProperty", aws_cdk.cdk.IResolvable]):
        return jsii.set(self, "robotSoftwareSuite", value)

    @property
    @jsii.member(jsii_name="sources")
    def sources(self) -> typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "SourceConfigProperty"]]]:
        """``AWS::RoboMaker::RobotApplication.Sources``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-sources
        Stability:
            experimental
        """
        return jsii.get(self, "sources")

    @sources.setter
    def sources(self, value: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "SourceConfigProperty"]]]):
        return jsii.set(self, "sources", value)

    @property
    @jsii.member(jsii_name="currentRevisionId")
    def current_revision_id(self) -> typing.Optional[str]:
        """``AWS::RoboMaker::RobotApplication.CurrentRevisionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-currentrevisionid
        Stability:
            experimental
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
            experimental
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
            experimental
        """
        name: str
        """``CfnRobotApplication.RobotSoftwareSuiteProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-robotsoftwaresuite.html#cfn-robomaker-robotapplication-robotsoftwaresuite-name
        Stability:
            experimental
        """

        version: str
        """``CfnRobotApplication.RobotSoftwareSuiteProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-robotsoftwaresuite.html#cfn-robomaker-robotapplication-robotsoftwaresuite-version
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnRobotApplication.SourceConfigProperty", jsii_struct_bases=[])
    class SourceConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-sourceconfig.html
        Stability:
            experimental
        """
        architecture: str
        """``CfnRobotApplication.SourceConfigProperty.Architecture``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-sourceconfig.html#cfn-robomaker-robotapplication-sourceconfig-architecture
        Stability:
            experimental
        """

        s3Bucket: str
        """``CfnRobotApplication.SourceConfigProperty.S3Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-sourceconfig.html#cfn-robomaker-robotapplication-sourceconfig-s3bucket
        Stability:
            experimental
        """

        s3Key: str
        """``CfnRobotApplication.SourceConfigProperty.S3Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-robotapplication-sourceconfig.html#cfn-robomaker-robotapplication-sourceconfig-s3key
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRobotApplicationProps(jsii.compat.TypedDict, total=False):
    currentRevisionId: str
    """``AWS::RoboMaker::RobotApplication.CurrentRevisionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-currentrevisionid
    Stability:
        experimental
    """
    name: str
    """``AWS::RoboMaker::RobotApplication.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-name
    Stability:
        experimental
    """
    tags: typing.Mapping[typing.Any, typing.Any]
    """``AWS::RoboMaker::RobotApplication.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnRobotApplicationProps", jsii_struct_bases=[_CfnRobotApplicationProps])
class CfnRobotApplicationProps(_CfnRobotApplicationProps):
    """Properties for defining a ``AWS::RoboMaker::RobotApplication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html
    Stability:
        experimental
    """
    robotSoftwareSuite: typing.Union["CfnRobotApplication.RobotSoftwareSuiteProperty", aws_cdk.cdk.IResolvable]
    """``AWS::RoboMaker::RobotApplication.RobotSoftwareSuite``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-robotsoftwaresuite
    Stability:
        experimental
    """

    sources: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnRobotApplication.SourceConfigProperty"]]]
    """``AWS::RoboMaker::RobotApplication.Sources``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplication.html#cfn-robomaker-robotapplication-sources
    Stability:
        experimental
    """

class CfnRobotApplicationVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-robomaker.CfnRobotApplicationVersion"):
    """A CloudFormation ``AWS::RoboMaker::RobotApplicationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplicationversion.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RoboMaker::RobotApplicationVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, application: str, current_revision_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::RoboMaker::RobotApplicationVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application: ``AWS::RoboMaker::RobotApplicationVersion.Application``.
            currentRevisionId: ``AWS::RoboMaker::RobotApplicationVersion.CurrentRevisionId``.

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
    @jsii.member(jsii_name="application")
    def application(self) -> str:
        """``AWS::RoboMaker::RobotApplicationVersion.Application``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplicationversion.html#cfn-robomaker-robotapplicationversion-application
        Stability:
            experimental
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
            experimental
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
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnRobotApplicationVersionProps", jsii_struct_bases=[_CfnRobotApplicationVersionProps])
class CfnRobotApplicationVersionProps(_CfnRobotApplicationVersionProps):
    """Properties for defining a ``AWS::RoboMaker::RobotApplicationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplicationversion.html
    Stability:
        experimental
    """
    application: str
    """``AWS::RoboMaker::RobotApplicationVersion.Application``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robotapplicationversion.html#cfn-robomaker-robotapplicationversion-application
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnRobotProps(jsii.compat.TypedDict, total=False):
    fleet: str
    """``AWS::RoboMaker::Robot.Fleet``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-fleet
    Stability:
        experimental
    """
    name: str
    """``AWS::RoboMaker::Robot.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-name
    Stability:
        experimental
    """
    tags: typing.Mapping[typing.Any, typing.Any]
    """``AWS::RoboMaker::Robot.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnRobotProps", jsii_struct_bases=[_CfnRobotProps])
class CfnRobotProps(_CfnRobotProps):
    """Properties for defining a ``AWS::RoboMaker::Robot``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html
    Stability:
        experimental
    """
    architecture: str
    """``AWS::RoboMaker::Robot.Architecture``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-architecture
    Stability:
        experimental
    """

    greengrassGroupId: str
    """``AWS::RoboMaker::Robot.GreengrassGroupId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-robot.html#cfn-robomaker-robot-greengrassgroupid
    Stability:
        experimental
    """

class CfnSimulationApplication(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplication"):
    """A CloudFormation ``AWS::RoboMaker::SimulationApplication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RoboMaker::SimulationApplication
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, rendering_engine: typing.Union[aws_cdk.cdk.IResolvable, "RenderingEngineProperty"], robot_software_suite: typing.Union[aws_cdk.cdk.IResolvable, "RobotSoftwareSuiteProperty"], simulation_software_suite: typing.Union[aws_cdk.cdk.IResolvable, "SimulationSoftwareSuiteProperty"], sources: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "SourceConfigProperty"]]], current_revision_id: typing.Optional[str]=None, name: typing.Optional[str]=None, tags: typing.Optional[typing.Mapping[typing.Any, typing.Any]]=None) -> None:
        """Create a new ``AWS::RoboMaker::SimulationApplication``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            renderingEngine: ``AWS::RoboMaker::SimulationApplication.RenderingEngine``.
            robotSoftwareSuite: ``AWS::RoboMaker::SimulationApplication.RobotSoftwareSuite``.
            simulationSoftwareSuite: ``AWS::RoboMaker::SimulationApplication.SimulationSoftwareSuite``.
            sources: ``AWS::RoboMaker::SimulationApplication.Sources``.
            currentRevisionId: ``AWS::RoboMaker::SimulationApplication.CurrentRevisionId``.
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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrCurrentRevisionId")
    def attr_current_revision_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            CurrentRevisionId
        """
        return jsii.get(self, "attrCurrentRevisionId")

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
        """``AWS::RoboMaker::SimulationApplication.Tags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-tags
        Stability:
            experimental
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="renderingEngine")
    def rendering_engine(self) -> typing.Union[aws_cdk.cdk.IResolvable, "RenderingEngineProperty"]:
        """``AWS::RoboMaker::SimulationApplication.RenderingEngine``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-renderingengine
        Stability:
            experimental
        """
        return jsii.get(self, "renderingEngine")

    @rendering_engine.setter
    def rendering_engine(self, value: typing.Union[aws_cdk.cdk.IResolvable, "RenderingEngineProperty"]):
        return jsii.set(self, "renderingEngine", value)

    @property
    @jsii.member(jsii_name="robotSoftwareSuite")
    def robot_software_suite(self) -> typing.Union[aws_cdk.cdk.IResolvable, "RobotSoftwareSuiteProperty"]:
        """``AWS::RoboMaker::SimulationApplication.RobotSoftwareSuite``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-robotsoftwaresuite
        Stability:
            experimental
        """
        return jsii.get(self, "robotSoftwareSuite")

    @robot_software_suite.setter
    def robot_software_suite(self, value: typing.Union[aws_cdk.cdk.IResolvable, "RobotSoftwareSuiteProperty"]):
        return jsii.set(self, "robotSoftwareSuite", value)

    @property
    @jsii.member(jsii_name="simulationSoftwareSuite")
    def simulation_software_suite(self) -> typing.Union[aws_cdk.cdk.IResolvable, "SimulationSoftwareSuiteProperty"]:
        """``AWS::RoboMaker::SimulationApplication.SimulationSoftwareSuite``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-simulationsoftwaresuite
        Stability:
            experimental
        """
        return jsii.get(self, "simulationSoftwareSuite")

    @simulation_software_suite.setter
    def simulation_software_suite(self, value: typing.Union[aws_cdk.cdk.IResolvable, "SimulationSoftwareSuiteProperty"]):
        return jsii.set(self, "simulationSoftwareSuite", value)

    @property
    @jsii.member(jsii_name="sources")
    def sources(self) -> typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "SourceConfigProperty"]]]:
        """``AWS::RoboMaker::SimulationApplication.Sources``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-sources
        Stability:
            experimental
        """
        return jsii.get(self, "sources")

    @sources.setter
    def sources(self, value: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "SourceConfigProperty"]]]):
        return jsii.set(self, "sources", value)

    @property
    @jsii.member(jsii_name="currentRevisionId")
    def current_revision_id(self) -> typing.Optional[str]:
        """``AWS::RoboMaker::SimulationApplication.CurrentRevisionId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-currentrevisionid
        Stability:
            experimental
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
            experimental
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
            experimental
        """
        name: str
        """``CfnSimulationApplication.RenderingEngineProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-renderingengine.html#cfn-robomaker-simulationapplication-renderingengine-name
        Stability:
            experimental
        """

        version: str
        """``CfnSimulationApplication.RenderingEngineProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-renderingengine.html#cfn-robomaker-simulationapplication-renderingengine-version
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplication.RobotSoftwareSuiteProperty", jsii_struct_bases=[])
    class RobotSoftwareSuiteProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-robotsoftwaresuite.html
        Stability:
            experimental
        """
        name: str
        """``CfnSimulationApplication.RobotSoftwareSuiteProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-robotsoftwaresuite.html#cfn-robomaker-simulationapplication-robotsoftwaresuite-name
        Stability:
            experimental
        """

        version: str
        """``CfnSimulationApplication.RobotSoftwareSuiteProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-robotsoftwaresuite.html#cfn-robomaker-simulationapplication-robotsoftwaresuite-version
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplication.SimulationSoftwareSuiteProperty", jsii_struct_bases=[])
    class SimulationSoftwareSuiteProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-simulationsoftwaresuite.html
        Stability:
            experimental
        """
        name: str
        """``CfnSimulationApplication.SimulationSoftwareSuiteProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-simulationsoftwaresuite.html#cfn-robomaker-simulationapplication-simulationsoftwaresuite-name
        Stability:
            experimental
        """

        version: str
        """``CfnSimulationApplication.SimulationSoftwareSuiteProperty.Version``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-simulationsoftwaresuite.html#cfn-robomaker-simulationapplication-simulationsoftwaresuite-version
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplication.SourceConfigProperty", jsii_struct_bases=[])
    class SourceConfigProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-sourceconfig.html
        Stability:
            experimental
        """
        architecture: str
        """``CfnSimulationApplication.SourceConfigProperty.Architecture``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-sourceconfig.html#cfn-robomaker-simulationapplication-sourceconfig-architecture
        Stability:
            experimental
        """

        s3Bucket: str
        """``CfnSimulationApplication.SourceConfigProperty.S3Bucket``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-sourceconfig.html#cfn-robomaker-simulationapplication-sourceconfig-s3bucket
        Stability:
            experimental
        """

        s3Key: str
        """``CfnSimulationApplication.SourceConfigProperty.S3Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-robomaker-simulationapplication-sourceconfig.html#cfn-robomaker-simulationapplication-sourceconfig-s3key
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnSimulationApplicationProps(jsii.compat.TypedDict, total=False):
    currentRevisionId: str
    """``AWS::RoboMaker::SimulationApplication.CurrentRevisionId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-currentrevisionid
    Stability:
        experimental
    """
    name: str
    """``AWS::RoboMaker::SimulationApplication.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-name
    Stability:
        experimental
    """
    tags: typing.Mapping[typing.Any, typing.Any]
    """``AWS::RoboMaker::SimulationApplication.Tags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-tags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplicationProps", jsii_struct_bases=[_CfnSimulationApplicationProps])
class CfnSimulationApplicationProps(_CfnSimulationApplicationProps):
    """Properties for defining a ``AWS::RoboMaker::SimulationApplication``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html
    Stability:
        experimental
    """
    renderingEngine: typing.Union[aws_cdk.cdk.IResolvable, "CfnSimulationApplication.RenderingEngineProperty"]
    """``AWS::RoboMaker::SimulationApplication.RenderingEngine``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-renderingengine
    Stability:
        experimental
    """

    robotSoftwareSuite: typing.Union[aws_cdk.cdk.IResolvable, "CfnSimulationApplication.RobotSoftwareSuiteProperty"]
    """``AWS::RoboMaker::SimulationApplication.RobotSoftwareSuite``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-robotsoftwaresuite
    Stability:
        experimental
    """

    simulationSoftwareSuite: typing.Union[aws_cdk.cdk.IResolvable, "CfnSimulationApplication.SimulationSoftwareSuiteProperty"]
    """``AWS::RoboMaker::SimulationApplication.SimulationSoftwareSuite``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-simulationsoftwaresuite
    Stability:
        experimental
    """

    sources: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnSimulationApplication.SourceConfigProperty"]]]
    """``AWS::RoboMaker::SimulationApplication.Sources``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplication.html#cfn-robomaker-simulationapplication-sources
    Stability:
        experimental
    """

class CfnSimulationApplicationVersion(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplicationVersion"):
    """A CloudFormation ``AWS::RoboMaker::SimulationApplicationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplicationversion.html
    Stability:
        experimental
    cloudformationResource:
        AWS::RoboMaker::SimulationApplicationVersion
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, application: str, current_revision_id: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::RoboMaker::SimulationApplicationVersion``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            application: ``AWS::RoboMaker::SimulationApplicationVersion.Application``.
            currentRevisionId: ``AWS::RoboMaker::SimulationApplicationVersion.CurrentRevisionId``.

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
    @jsii.member(jsii_name="application")
    def application(self) -> str:
        """``AWS::RoboMaker::SimulationApplicationVersion.Application``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplicationversion.html#cfn-robomaker-simulationapplicationversion-application
        Stability:
            experimental
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
            experimental
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
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-robomaker.CfnSimulationApplicationVersionProps", jsii_struct_bases=[_CfnSimulationApplicationVersionProps])
class CfnSimulationApplicationVersionProps(_CfnSimulationApplicationVersionProps):
    """Properties for defining a ``AWS::RoboMaker::SimulationApplicationVersion``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplicationversion.html
    Stability:
        experimental
    """
    application: str
    """``AWS::RoboMaker::SimulationApplicationVersion.Application``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-robomaker-simulationapplicationversion.html#cfn-robomaker-simulationapplicationversion-application
    Stability:
        experimental
    """

__all__ = ["CfnFleet", "CfnFleetProps", "CfnRobot", "CfnRobotApplication", "CfnRobotApplicationProps", "CfnRobotApplicationVersion", "CfnRobotApplicationVersionProps", "CfnRobotProps", "CfnSimulationApplication", "CfnSimulationApplicationProps", "CfnSimulationApplicationVersion", "CfnSimulationApplicationVersionProps", "__jsii_assembly__"]

publication.publish()
