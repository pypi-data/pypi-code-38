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


class BTWebRendererPerformanceMeasurementParams(object):
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
        'vendor': 'str',
        'renderer': 'str',
        'triangles_per_second': 'float',
        'lines_per_second': 'float'
    }

    attribute_map = {
        'vendor': 'vendor',
        'renderer': 'renderer',
        'triangles_per_second': 'trianglesPerSecond',
        'lines_per_second': 'linesPerSecond'
    }

    def __init__(self, vendor=None, renderer=None, triangles_per_second=None, lines_per_second=None):  # noqa: E501
        """BTWebRendererPerformanceMeasurementParams - a model defined in OpenAPI"""  # noqa: E501

        self._vendor = None
        self._renderer = None
        self._triangles_per_second = None
        self._lines_per_second = None
        self.discriminator = None

        if vendor is not None:
            self.vendor = vendor
        if renderer is not None:
            self.renderer = renderer
        if triangles_per_second is not None:
            self.triangles_per_second = triangles_per_second
        if lines_per_second is not None:
            self.lines_per_second = lines_per_second

    @property
    def vendor(self):
        """Gets the vendor of this BTWebRendererPerformanceMeasurementParams.  # noqa: E501


        :return: The vendor of this BTWebRendererPerformanceMeasurementParams.  # noqa: E501
        :rtype: str
        """
        return self._vendor

    @vendor.setter
    def vendor(self, vendor):
        """Sets the vendor of this BTWebRendererPerformanceMeasurementParams.


        :param vendor: The vendor of this BTWebRendererPerformanceMeasurementParams.  # noqa: E501
        :type: str
        """

        self._vendor = vendor

    @property
    def renderer(self):
        """Gets the renderer of this BTWebRendererPerformanceMeasurementParams.  # noqa: E501


        :return: The renderer of this BTWebRendererPerformanceMeasurementParams.  # noqa: E501
        :rtype: str
        """
        return self._renderer

    @renderer.setter
    def renderer(self, renderer):
        """Sets the renderer of this BTWebRendererPerformanceMeasurementParams.


        :param renderer: The renderer of this BTWebRendererPerformanceMeasurementParams.  # noqa: E501
        :type: str
        """

        self._renderer = renderer

    @property
    def triangles_per_second(self):
        """Gets the triangles_per_second of this BTWebRendererPerformanceMeasurementParams.  # noqa: E501


        :return: The triangles_per_second of this BTWebRendererPerformanceMeasurementParams.  # noqa: E501
        :rtype: float
        """
        return self._triangles_per_second

    @triangles_per_second.setter
    def triangles_per_second(self, triangles_per_second):
        """Sets the triangles_per_second of this BTWebRendererPerformanceMeasurementParams.


        :param triangles_per_second: The triangles_per_second of this BTWebRendererPerformanceMeasurementParams.  # noqa: E501
        :type: float
        """

        self._triangles_per_second = triangles_per_second

    @property
    def lines_per_second(self):
        """Gets the lines_per_second of this BTWebRendererPerformanceMeasurementParams.  # noqa: E501


        :return: The lines_per_second of this BTWebRendererPerformanceMeasurementParams.  # noqa: E501
        :rtype: float
        """
        return self._lines_per_second

    @lines_per_second.setter
    def lines_per_second(self, lines_per_second):
        """Sets the lines_per_second of this BTWebRendererPerformanceMeasurementParams.


        :param lines_per_second: The lines_per_second of this BTWebRendererPerformanceMeasurementParams.  # noqa: E501
        :type: float
        """

        self._lines_per_second = lines_per_second

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
        if not isinstance(other, BTWebRendererPerformanceMeasurementParams):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
