"""Raw representations of every data type in the AWS RAM service.

See Also:
    `AWS developer guide for RAM
    <https://docs.aws.amazon.com/ram/latest/userguide/index.html>`_

This file is automatically generated, and should not be directly edited.
"""

from attr import attrib
from attr import attrs

from ..core import ATTRSCONFIG
from ..core import Resource
from ..core import ResourceProperties
from ..core import create_object_converter

__all__ = ["ResourceShare", "ResourceShareProperties"]


@attrs(**ATTRSCONFIG)
class ResourceShareProperties(ResourceProperties):
    AllowExternalPrincipals = attrib(default=None)
    Name = attrib(default=None)
    Principals = attrib(default=None)
    ResourceArns = attrib(default=None)
    Tags = attrib(default=None)


@attrs(**ATTRSCONFIG)
class ResourceShare(Resource):
    """A Resource Share for RAM.

    See Also:
        `AWS Cloud Formation documentation for ResourceShare
        <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html>`_
    """

    RESOURCE_TYPE = "AWS::RAM::ResourceShare"

    Properties: ResourceShareProperties = attrib(
        factory=ResourceShareProperties,
        converter=create_object_converter(ResourceShareProperties),
    )
