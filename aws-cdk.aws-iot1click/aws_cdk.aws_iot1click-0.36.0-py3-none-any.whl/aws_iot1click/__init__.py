import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-iot1click", "0.36.0", __name__, "aws-iot1click@0.36.0.jsii.tgz")
class CfnDevice(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot1click.CfnDevice"):
    """A CloudFormation ``AWS::IoT1Click::Device``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoT1Click::Device
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, device_id: str, enabled: typing.Union[bool, aws_cdk.core.IResolvable]) -> None:
        """Create a new ``AWS::IoT1Click::Device``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            device_id: ``AWS::IoT1Click::Device.DeviceId``.
            enabled: ``AWS::IoT1Click::Device.Enabled``.

        Stability:
            experimental
        """
        props: CfnDeviceProps = {"deviceId": device_id, "enabled": enabled}

        jsii.create(CfnDevice, self, [scope, id, props])

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
    @jsii.member(jsii_name="attrDeviceId")
    def attr_device_id(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            DeviceId
        """
        return jsii.get(self, "attrDeviceId")

    @property
    @jsii.member(jsii_name="attrEnabled")
    def attr_enabled(self) -> aws_cdk.core.IResolvable:
        """
        Stability:
            stable
        cloudformationAttribute:
            Enabled
        """
        return jsii.get(self, "attrEnabled")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="deviceId")
    def device_id(self) -> str:
        """``AWS::IoT1Click::Device.DeviceId``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html#cfn-iot1click-device-deviceid
        Stability:
            stable
        """
        return jsii.get(self, "deviceId")

    @device_id.setter
    def device_id(self, value: str):
        return jsii.set(self, "deviceId", value)

    @property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[bool, aws_cdk.core.IResolvable]:
        """``AWS::IoT1Click::Device.Enabled``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html#cfn-iot1click-device-enabled
        Stability:
            stable
        """
        return jsii.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: typing.Union[bool, aws_cdk.core.IResolvable]):
        return jsii.set(self, "enabled", value)


@jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnDeviceProps", jsii_struct_bases=[])
class CfnDeviceProps(jsii.compat.TypedDict):
    """Properties for defining a ``AWS::IoT1Click::Device``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html
    Stability:
        stable
    """
    deviceId: str
    """``AWS::IoT1Click::Device.DeviceId``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html#cfn-iot1click-device-deviceid
    Stability:
        stable
    """

    enabled: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::IoT1Click::Device.Enabled``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html#cfn-iot1click-device-enabled
    Stability:
        stable
    """

class CfnPlacement(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot1click.CfnPlacement"):
    """A CloudFormation ``AWS::IoT1Click::Placement``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoT1Click::Placement
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, project_name: str, associated_devices: typing.Any=None, attributes: typing.Any=None, placement_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT1Click::Placement``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            project_name: ``AWS::IoT1Click::Placement.ProjectName``.
            associated_devices: ``AWS::IoT1Click::Placement.AssociatedDevices``.
            attributes: ``AWS::IoT1Click::Placement.Attributes``.
            placement_name: ``AWS::IoT1Click::Placement.PlacementName``.

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
    @jsii.member(jsii_name="attrPlacementName")
    def attr_placement_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            PlacementName
        """
        return jsii.get(self, "attrPlacementName")

    @property
    @jsii.member(jsii_name="attrProjectName")
    def attr_project_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            ProjectName
        """
        return jsii.get(self, "attrProjectName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="associatedDevices")
    def associated_devices(self) -> typing.Any:
        """``AWS::IoT1Click::Placement.AssociatedDevices``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-associateddevices
        Stability:
            stable
        """
        return jsii.get(self, "associatedDevices")

    @associated_devices.setter
    def associated_devices(self, value: typing.Any):
        return jsii.set(self, "associatedDevices", value)

    @property
    @jsii.member(jsii_name="attributes")
    def attributes(self) -> typing.Any:
        """``AWS::IoT1Click::Placement.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-attributes
        Stability:
            stable
        """
        return jsii.get(self, "attributes")

    @attributes.setter
    def attributes(self, value: typing.Any):
        return jsii.set(self, "attributes", value)

    @property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> str:
        """``AWS::IoT1Click::Placement.ProjectName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-projectname
        Stability:
            stable
        """
        return jsii.get(self, "projectName")

    @project_name.setter
    def project_name(self, value: str):
        return jsii.set(self, "projectName", value)

    @property
    @jsii.member(jsii_name="placementName")
    def placement_name(self) -> typing.Optional[str]:
        """``AWS::IoT1Click::Placement.PlacementName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-placementname
        Stability:
            stable
        """
        return jsii.get(self, "placementName")

    @placement_name.setter
    def placement_name(self, value: typing.Optional[str]):
        return jsii.set(self, "placementName", value)


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPlacementProps(jsii.compat.TypedDict, total=False):
    associatedDevices: typing.Any
    """``AWS::IoT1Click::Placement.AssociatedDevices``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-associateddevices
    Stability:
        stable
    """
    attributes: typing.Any
    """``AWS::IoT1Click::Placement.Attributes``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-attributes
    Stability:
        stable
    """
    placementName: str
    """``AWS::IoT1Click::Placement.PlacementName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-placementname
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnPlacementProps", jsii_struct_bases=[_CfnPlacementProps])
class CfnPlacementProps(_CfnPlacementProps):
    """Properties for defining a ``AWS::IoT1Click::Placement``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html
    Stability:
        stable
    """
    projectName: str
    """``AWS::IoT1Click::Placement.ProjectName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html#cfn-iot1click-placement-projectname
    Stability:
        stable
    """

class CfnProject(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iot1click.CfnProject"):
    """A CloudFormation ``AWS::IoT1Click::Project``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html
    Stability:
        stable
    cloudformationResource:
        AWS::IoT1Click::Project
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, placement_template: typing.Union[aws_cdk.core.IResolvable, "PlacementTemplateProperty"], description: typing.Optional[str]=None, project_name: typing.Optional[str]=None) -> None:
        """Create a new ``AWS::IoT1Click::Project``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            placement_template: ``AWS::IoT1Click::Project.PlacementTemplate``.
            description: ``AWS::IoT1Click::Project.Description``.
            project_name: ``AWS::IoT1Click::Project.ProjectName``.

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
    @jsii.member(jsii_name="attrProjectName")
    def attr_project_name(self) -> str:
        """
        Stability:
            stable
        cloudformationAttribute:
            ProjectName
        """
        return jsii.get(self, "attrProjectName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="placementTemplate")
    def placement_template(self) -> typing.Union[aws_cdk.core.IResolvable, "PlacementTemplateProperty"]:
        """``AWS::IoT1Click::Project.PlacementTemplate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-placementtemplate
        Stability:
            stable
        """
        return jsii.get(self, "placementTemplate")

    @placement_template.setter
    def placement_template(self, value: typing.Union[aws_cdk.core.IResolvable, "PlacementTemplateProperty"]):
        return jsii.set(self, "placementTemplate", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::IoT1Click::Project.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> typing.Optional[str]:
        """``AWS::IoT1Click::Project.ProjectName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-projectname
        Stability:
            stable
        """
        return jsii.get(self, "projectName")

    @project_name.setter
    def project_name(self, value: typing.Optional[str]):
        return jsii.set(self, "projectName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnProject.DeviceTemplateProperty", jsii_struct_bases=[])
    class DeviceTemplateProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-devicetemplate.html
        Stability:
            stable
        """
        callbackOverrides: typing.Any
        """``CfnProject.DeviceTemplateProperty.CallbackOverrides``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-devicetemplate.html#cfn-iot1click-project-devicetemplate-callbackoverrides
        Stability:
            stable
        """

        deviceType: str
        """``CfnProject.DeviceTemplateProperty.DeviceType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-devicetemplate.html#cfn-iot1click-project-devicetemplate-devicetype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnProject.PlacementTemplateProperty", jsii_struct_bases=[])
    class PlacementTemplateProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-placementtemplate.html
        Stability:
            stable
        """
        defaultAttributes: typing.Any
        """``CfnProject.PlacementTemplateProperty.DefaultAttributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-placementtemplate.html#cfn-iot1click-project-placementtemplate-defaultattributes
        Stability:
            stable
        """

        deviceTemplates: typing.Union[aws_cdk.core.IResolvable, "CfnProject.DeviceTemplateProperty"]
        """``CfnProject.PlacementTemplateProperty.DeviceTemplates``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot1click-project-placementtemplate.html#cfn-iot1click-project-placementtemplate-devicetemplates
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnProjectProps(jsii.compat.TypedDict, total=False):
    description: str
    """``AWS::IoT1Click::Project.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-description
    Stability:
        stable
    """
    projectName: str
    """``AWS::IoT1Click::Project.ProjectName``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-projectname
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-iot1click.CfnProjectProps", jsii_struct_bases=[_CfnProjectProps])
class CfnProjectProps(_CfnProjectProps):
    """Properties for defining a ``AWS::IoT1Click::Project``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html
    Stability:
        stable
    """
    placementTemplate: typing.Union[aws_cdk.core.IResolvable, "CfnProject.PlacementTemplateProperty"]
    """``AWS::IoT1Click::Project.PlacementTemplate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html#cfn-iot1click-project-placementtemplate
    Stability:
        stable
    """

__all__ = ["CfnDevice", "CfnDeviceProps", "CfnPlacement", "CfnPlacementProps", "CfnProject", "CfnProjectProps", "__jsii_assembly__"]

publication.publish()
