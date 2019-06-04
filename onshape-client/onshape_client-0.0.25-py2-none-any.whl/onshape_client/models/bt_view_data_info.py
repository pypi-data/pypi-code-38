# coding: utf-8

"""
    Onshape REST API

    The Onshape REST API consumed by all clients.  # noqa: E501

    OpenAPI spec version: 1.97
    Contact: api-support@onshape.zendesk.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class BTViewDataInfo(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'is_perspective': 'bool',
        'camera_viewport': 'list[float]',
        'angle': 'float',
        'view_matrix': 'list[float]'
    }

    attribute_map = {
        'is_perspective': 'isPerspective',
        'camera_viewport': 'cameraViewport',
        'angle': 'angle',
        'view_matrix': 'viewMatrix'
    }

    def __init__(self, is_perspective=None, camera_viewport=None, angle=None, view_matrix=None):  # noqa: E501
        """BTViewDataInfo - a model defined in OpenAPI"""  # noqa: E501

        self._is_perspective = None
        self._camera_viewport = None
        self._angle = None
        self._view_matrix = None
        self.discriminator = None

        if is_perspective is not None:
            self.is_perspective = is_perspective
        if camera_viewport is not None:
            self.camera_viewport = camera_viewport
        if angle is not None:
            self.angle = angle
        if view_matrix is not None:
            self.view_matrix = view_matrix

    @property
    def is_perspective(self):
        """Gets the is_perspective of this BTViewDataInfo.  # noqa: E501


        :return: The is_perspective of this BTViewDataInfo.  # noqa: E501
        :rtype: bool
        """
        return self._is_perspective

    @is_perspective.setter
    def is_perspective(self, is_perspective):
        """Sets the is_perspective of this BTViewDataInfo.


        :param is_perspective: The is_perspective of this BTViewDataInfo.  # noqa: E501
        :type: bool
        """

        self._is_perspective = is_perspective

    @property
    def camera_viewport(self):
        """Gets the camera_viewport of this BTViewDataInfo.  # noqa: E501


        :return: The camera_viewport of this BTViewDataInfo.  # noqa: E501
        :rtype: list[float]
        """
        return self._camera_viewport

    @camera_viewport.setter
    def camera_viewport(self, camera_viewport):
        """Sets the camera_viewport of this BTViewDataInfo.


        :param camera_viewport: The camera_viewport of this BTViewDataInfo.  # noqa: E501
        :type: list[float]
        """

        self._camera_viewport = camera_viewport

    @property
    def angle(self):
        """Gets the angle of this BTViewDataInfo.  # noqa: E501


        :return: The angle of this BTViewDataInfo.  # noqa: E501
        :rtype: float
        """
        return self._angle

    @angle.setter
    def angle(self, angle):
        """Sets the angle of this BTViewDataInfo.


        :param angle: The angle of this BTViewDataInfo.  # noqa: E501
        :type: float
        """

        self._angle = angle

    @property
    def view_matrix(self):
        """Gets the view_matrix of this BTViewDataInfo.  # noqa: E501


        :return: The view_matrix of this BTViewDataInfo.  # noqa: E501
        :rtype: list[float]
        """
        return self._view_matrix

    @view_matrix.setter
    def view_matrix(self, view_matrix):
        """Sets the view_matrix of this BTViewDataInfo.


        :param view_matrix: The view_matrix of this BTViewDataInfo.  # noqa: E501
        :type: list[float]
        """

        self._view_matrix = view_matrix

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, BTViewDataInfo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
