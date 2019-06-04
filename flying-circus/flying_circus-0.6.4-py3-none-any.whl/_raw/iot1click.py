"""Raw representations of every data type in the AWS IoT1Click service.

See Also:
    `AWS developer guide for IoT1Click
    <https://docs.aws.amazon.com/iot-1-click/latest/developerguide/index.html>`_

This file is automatically generated, and should not be directly edited.
"""

from attr import attrib
from attr import attrs

from ..core import ATTRSCONFIG
from ..core import Resource
from ..core import ResourceProperties
from ..core import create_object_converter

__all__ = [
    "Device",
    "DeviceProperties",
    "Placement",
    "PlacementProperties",
    "Project",
    "ProjectProperties",
]


@attrs(**ATTRSCONFIG)
class DeviceProperties(ResourceProperties):
    DeviceId = attrib(default=None)
    Enabled = attrib(default=None)


@attrs(**ATTRSCONFIG)
class Device(Resource):
    """A Device for IoT1Click.

    See Also:
        `AWS Cloud Formation documentation for Device
        <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-device.html>`_
    """

    RESOURCE_TYPE = "AWS::IoT1Click::Device"

    Properties: DeviceProperties = attrib(
        factory=DeviceProperties, converter=create_object_converter(DeviceProperties)
    )


@attrs(**ATTRSCONFIG)
class PlacementProperties(ResourceProperties):
    AssociatedDevices = attrib(default=None)
    Attributes = attrib(default=None)
    PlacementName = attrib(default=None)
    ProjectName = attrib(default=None)


@attrs(**ATTRSCONFIG)
class Placement(Resource):
    """A Placement for IoT1Click.

    See Also:
        `AWS Cloud Formation documentation for Placement
        <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-placement.html>`_
    """

    RESOURCE_TYPE = "AWS::IoT1Click::Placement"

    Properties: PlacementProperties = attrib(
        factory=PlacementProperties,
        converter=create_object_converter(PlacementProperties),
    )


@attrs(**ATTRSCONFIG)
class ProjectProperties(ResourceProperties):
    Description = attrib(default=None)
    PlacementTemplate = attrib(default=None)
    ProjectName = attrib(default=None)


@attrs(**ATTRSCONFIG)
class Project(Resource):
    """A Project for IoT1Click.

    See Also:
        `AWS Cloud Formation documentation for Project
        <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot1click-project.html>`_
    """

    RESOURCE_TYPE = "AWS::IoT1Click::Project"

    Properties: ProjectProperties = attrib(
        factory=ProjectProperties, converter=create_object_converter(ProjectProperties)
    )
