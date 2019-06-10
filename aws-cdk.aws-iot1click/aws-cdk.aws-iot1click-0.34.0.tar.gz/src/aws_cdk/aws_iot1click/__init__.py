import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-iot1click", "0.34.0", __name__, "aws-iot1click@0.34.0.jsii.tgz")
class CfnDevice(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot1click.CfnDevice"):
    """A CloudFormation ``AWS::IoT1Click::Device``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoT1Click::Device
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, device_id: str, enabled: typing.Union[bool, aws_cdk.cdk.Token]) -> None:
        """Create a new ``AWS::IoT1Click::Device``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            deviceId: ``AWS::IoT1Click::Device.DeviceId``.
            enabled: ``AWS::IoT1Click::Device.Enabled``.

        Stability:
            experimental
        """
        props: CfnDeviceProps = {"deviceId": device_id, "enabled": enabled}

        jsii.create(CfnDevice, self, [scope, id, props])

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
    @jsii.member(jsii_name="deviceArn")
    def device_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "deviceArn")

    @property
    @jsii.member(jsii_name="deviceEnabled")
    def device_enabled(self) -> aws_cdk.cdk.Token:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Enabled
        """
        return jsii.get(self, "deviceEnabled")

    @property
    @jsii.member(jsii_name="deviceId")
    def device_id(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            DeviceId
        """
        return jsii.get(self, "deviceId")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnDeviceProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnDeviceProps", jsii_struct_bases=[])
class CfnDeviceProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::IoT1Click::Device``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html
    Stability:
        experimental
    """
    deviceId: str
    """``AWS::IoT1Click::Device.DeviceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html#cfn-iot1click-device-deviceid
    Stability:
        experimental
    """

    enabled: typing.Union[bool, aws_cdk.cdk.Token]
    """``AWS::IoT1Click::Device.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html#cfn-iot1click-device-enabled
    Stability:
        experimental
    """

class CfnPlacement(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot1click.CfnPlacement"):
    """A CloudFormation ``AWS::IoT1Click::Placement``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoT1Click::Placement
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, project_name: str, associated_devices: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, attributes: typing.Optional[typing.Union[typing.Optional[typing.Mapping[typing.Any, typing.Any]], typing.Optional[aws_cdk.cdk.Token]]]=None, placement_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT1Click::Placement``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            projectName: ``AWS::IoT1Click::Placement.ProjectName``.
            associatedDevices: ``AWS::IoT1Click::Placement.AssociatedDevices``.
            attributes: ``AWS::IoT1Click::Placement.Attributes``.
            placementName: ``AWS::IoT1Click::Placement.PlacementName``.

        Stability:
            experimental
        """
        props: CfnPlacementProps = {"projectName": project_name}

        if associated_devices is not None:
            props["associatedDevices"] = associated_devices

        if attributes is not None:
            props["attributes"] = attributes

        if placement_name is not None:
            props["placementName"] = placement_name

        jsii.create(CfnPlacement, self, [scope, id, props])

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
    @jsii.member(jsii_name="placementName")
    def placement_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            PlacementName
        """
        return jsii.get(self, "placementName")

    @property
    @jsii.member(jsii_name="placementPath")
    def placement_path(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "placementPath")

    @property
    @jsii.member(jsii_name="placementProjectName")
    def placement_project_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ProjectName
        """
        return jsii.get(self, "placementProjectName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnPlacementProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPlacementProps(jsii.compat.TypedDict, total=False):
    associatedDevices: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::IoT1Click::Placement.AssociatedDevices``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-associateddevices
    Stability:
        experimental
    """
    attributes: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
    """``AWS::IoT1Click::Placement.Attributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-attributes
    Stability:
        experimental
    """
    placementName: str
    """``AWS::IoT1Click::Placement.PlacementName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-placementname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnPlacementProps", jsii_struct_bases=[_CfnPlacementProps])
class CfnPlacementProps(_CfnPlacementProps):
    """Properties for defining a ``AWS::IoT1Click::Placement``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html
    Stability:
        experimental
    """
    projectName: str
    """``AWS::IoT1Click::Placement.ProjectName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-projectname
    Stability:
        experimental
    """

class CfnProject(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot1click.CfnProject"):
    """A CloudFormation ``AWS::IoT1Click::Project``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html
    Stability:
        experimental
    cloudformationResource:
        AWS::IoT1Click::Project
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, placement_template: typing.Union[aws_cdk.cdk.Token, "PlacementTemplateProperty"], description: typing.Optional[str]=None, project_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT1Click::Project``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            placementTemplate: ``AWS::IoT1Click::Project.PlacementTemplate``.
            description: ``AWS::IoT1Click::Project.Description``.
            projectName: ``AWS::IoT1Click::Project.ProjectName``.

        Stability:
            experimental
        """
        props: CfnProjectProps = {"placementTemplate": placement_template}

        if description is not None:
            props["description"] = description

        if project_name is not None:
            props["projectName"] = project_name

        jsii.create(CfnProject, self, [scope, id, props])

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
    @jsii.member(jsii_name="projectArn")
    def project_arn(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            Arn
        """
        return jsii.get(self, "projectArn")

    @property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> str:
        """
        Stability:
            experimental
        cloudformationAttribute:
            ProjectName
        """
        return jsii.get(self, "projectName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnProjectProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnProject.DeviceTemplateProperty", jsii_struct_bases=[])
    class DeviceTemplateProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-devicetemplate.html
        Stability:
            experimental
        """
        callbackOverrides: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnProject.DeviceTemplateProperty.CallbackOverrides``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-devicetemplate.html#cfn-iot1click-project-devicetemplate-callbackoverrides
        Stability:
            experimental
        """

        deviceType: str
        """``CfnProject.DeviceTemplateProperty.DeviceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-devicetemplate.html#cfn-iot1click-project-devicetemplate-devicetype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnProject.PlacementTemplateProperty", jsii_struct_bases=[])
    class PlacementTemplateProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-placementtemplate.html
        Stability:
            experimental
        """
        defaultAttributes: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnProject.PlacementTemplateProperty.DefaultAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-placementtemplate.html#cfn-iot1click-project-placementtemplate-defaultattributes
        Stability:
            experimental
        """

        deviceTemplates: typing.Union[aws_cdk.cdk.Token, "CfnProject.DeviceTemplateProperty"]
        """``CfnProject.PlacementTemplateProperty.DeviceTemplates``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-placementtemplate.html#cfn-iot1click-project-placementtemplate-devicetemplates
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnProjectProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::IoT1Click::Project.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-description
    Stability:
        experimental
    """
    projectName: str
    """``AWS::IoT1Click::Project.ProjectName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-projectname
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnProjectProps", jsii_struct_bases=[_CfnProjectProps])
class CfnProjectProps(_CfnProjectProps):
    """Properties for defining a ``AWS::IoT1Click::Project``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html
    Stability:
        experimental
    """
    placementTemplate: typing.Union[aws_cdk.cdk.Token, "CfnProject.PlacementTemplateProperty"]
    """``AWS::IoT1Click::Project.PlacementTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-placementtemplate
    Stability:
        experimental
    """

__all__ = ["CfnDevice", "CfnDeviceProps", "CfnPlacement", "CfnPlacementProps", "CfnProject", "CfnProjectProps", "__jsii_assembly__"]

publication.publish()
