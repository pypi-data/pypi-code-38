# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose">
#   Copyright (c) 2018 Aspose.Slides for Cloud
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

import pprint
import re  # noqa: F401

import six

from asposeslidescloud.models.geometry_shape import GeometryShape

class Connector(GeometryShape):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'self_uri': 'ResourceUri',
        'alternate_links': 'list[ResourceUri]',
        'name': 'str',
        'width': 'float',
        'height': 'float',
        'alternative_text': 'str',
        'hidden': 'bool',
        'x': 'float',
        'y': 'float',
        'z_order_position': 'int',
        'shapes': 'ResourceUriElement',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'type': 'str',
        'shape_type': 'str',
        'geometry_shape_type': 'str',
        'start_shape_connected_to': 'ResourceUri',
        'start_shape_connected_to_index': 'int',
        'end_shape_connected_to': 'ResourceUri',
        'end_shape_connected_to_index': 'int'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks',
        'name': 'Name',
        'width': 'Width',
        'height': 'Height',
        'alternative_text': 'AlternativeText',
        'hidden': 'Hidden',
        'x': 'X',
        'y': 'Y',
        'z_order_position': 'ZOrderPosition',
        'shapes': 'Shapes',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'type': 'Type',
        'shape_type': 'ShapeType',
        'geometry_shape_type': 'GeometryShapeType',
        'start_shape_connected_to': 'StartShapeConnectedTo',
        'start_shape_connected_to_index': 'StartShapeConnectedToIndex',
        'end_shape_connected_to': 'EndShapeConnectedTo',
        'end_shape_connected_to_index': 'EndShapeConnectedToIndex'
    }

    def __init__(self, self_uri=None, alternate_links=None, name=None, width=None, height=None, alternative_text=None, hidden=None, x=None, y=None, z_order_position=None, shapes=None, fill_format=None, effect_format=None, line_format=None, type='Connector', shape_type=None, geometry_shape_type=None, start_shape_connected_to=None, start_shape_connected_to_index=None, end_shape_connected_to=None, end_shape_connected_to_index=None):  # noqa: E501
        """Connector - a model defined in Swagger"""  # noqa: E501
        super(Connector, self).__init__(self_uri, alternate_links, name, width, height, alternative_text, hidden, x, y, z_order_position, shapes, fill_format, effect_format, line_format, type, shape_type, geometry_shape_type)

        self._start_shape_connected_to = None
        self._start_shape_connected_to_index = None
        self._end_shape_connected_to = None
        self._end_shape_connected_to_index = None

        if start_shape_connected_to is not None:
            self.start_shape_connected_to = start_shape_connected_to
        if start_shape_connected_to_index is not None:
            self.start_shape_connected_to_index = start_shape_connected_to_index
        if end_shape_connected_to is not None:
            self.end_shape_connected_to = end_shape_connected_to
        if end_shape_connected_to_index is not None:
            self.end_shape_connected_to_index = end_shape_connected_to_index

    @property
    def start_shape_connected_to(self):
        """Gets the start_shape_connected_to of this Connector.  # noqa: E501


        :return: The start_shape_connected_to of this Connector.  # noqa: E501
        :rtype: ResourceUri
        """
        return self._start_shape_connected_to

    @start_shape_connected_to.setter
    def start_shape_connected_to(self, start_shape_connected_to):
        """Sets the start_shape_connected_to of this Connector.


        :param start_shape_connected_to: The start_shape_connected_to of this Connector.  # noqa: E501
        :type: ResourceUri
        """
        self._start_shape_connected_to = start_shape_connected_to

    @property
    def start_shape_connected_to_index(self):
        """Gets the start_shape_connected_to_index of this Connector.  # noqa: E501


        :return: The start_shape_connected_to_index of this Connector.  # noqa: E501
        :rtype: int
        """
        return self._start_shape_connected_to_index

    @start_shape_connected_to_index.setter
    def start_shape_connected_to_index(self, start_shape_connected_to_index):
        """Sets the start_shape_connected_to_index of this Connector.


        :param start_shape_connected_to_index: The start_shape_connected_to_index of this Connector.  # noqa: E501
        :type: int
        """
        self._start_shape_connected_to_index = start_shape_connected_to_index

    @property
    def end_shape_connected_to(self):
        """Gets the end_shape_connected_to of this Connector.  # noqa: E501


        :return: The end_shape_connected_to of this Connector.  # noqa: E501
        :rtype: ResourceUri
        """
        return self._end_shape_connected_to

    @end_shape_connected_to.setter
    def end_shape_connected_to(self, end_shape_connected_to):
        """Sets the end_shape_connected_to of this Connector.


        :param end_shape_connected_to: The end_shape_connected_to of this Connector.  # noqa: E501
        :type: ResourceUri
        """
        self._end_shape_connected_to = end_shape_connected_to

    @property
    def end_shape_connected_to_index(self):
        """Gets the end_shape_connected_to_index of this Connector.  # noqa: E501


        :return: The end_shape_connected_to_index of this Connector.  # noqa: E501
        :rtype: int
        """
        return self._end_shape_connected_to_index

    @end_shape_connected_to_index.setter
    def end_shape_connected_to_index(self, end_shape_connected_to_index):
        """Sets the end_shape_connected_to_index of this Connector.


        :param end_shape_connected_to_index: The end_shape_connected_to_index of this Connector.  # noqa: E501
        :type: int
        """
        self._end_shape_connected_to_index = end_shape_connected_to_index

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
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
        if not isinstance(other, Connector):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
