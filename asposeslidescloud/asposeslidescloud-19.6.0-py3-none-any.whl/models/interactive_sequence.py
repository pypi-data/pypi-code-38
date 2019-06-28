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


class InteractiveSequence(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'effects': 'list[Effect]',
        'trigger_shape_index': 'int'
    }

    attribute_map = {
        'effects': 'Effects',
        'trigger_shape_index': 'TriggerShapeIndex'
    }

    def __init__(self, effects=None, trigger_shape_index=None):  # noqa: E501
        """InteractiveSequence - a model defined in Swagger"""  # noqa: E501

        self._effects = None
        self._trigger_shape_index = None

        if effects is not None:
            self.effects = effects
        self.trigger_shape_index = trigger_shape_index

    @property
    def effects(self):
        """Gets the effects of this InteractiveSequence.  # noqa: E501

        Effect list.  # noqa: E501

        :return: The effects of this InteractiveSequence.  # noqa: E501
        :rtype: list[Effect]
        """
        return self._effects

    @effects.setter
    def effects(self, effects):
        """Sets the effects of this InteractiveSequence.

        Effect list.  # noqa: E501

        :param effects: The effects of this InteractiveSequence.  # noqa: E501
        :type: list[Effect]
        """
        self._effects = effects

    @property
    def trigger_shape_index(self):
        """Gets the trigger_shape_index of this InteractiveSequence.  # noqa: E501

        Index of the shape that triggers the sequence.  # noqa: E501

        :return: The trigger_shape_index of this InteractiveSequence.  # noqa: E501
        :rtype: int
        """
        return self._trigger_shape_index

    @trigger_shape_index.setter
    def trigger_shape_index(self, trigger_shape_index):
        """Sets the trigger_shape_index of this InteractiveSequence.

        Index of the shape that triggers the sequence.  # noqa: E501

        :param trigger_shape_index: The trigger_shape_index of this InteractiveSequence.  # noqa: E501
        :type: int
        """
        self._trigger_shape_index = trigger_shape_index

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
        if not isinstance(other, InteractiveSequence):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
