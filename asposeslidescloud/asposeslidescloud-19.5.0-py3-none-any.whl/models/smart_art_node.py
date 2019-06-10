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


class SmartArtNode(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'nodes': 'list[SmartArtNode]',
        'shapes': 'ResourceUriElement',
        'is_assistant': 'bool',
        'text': 'str',
        'org_chart_layout': 'str'
    }

    attribute_map = {
        'nodes': 'Nodes',
        'shapes': 'Shapes',
        'is_assistant': 'IsAssistant',
        'text': 'Text',
        'org_chart_layout': 'OrgChartLayout'
    }

    def __init__(self, nodes=None, shapes=None, is_assistant=None, text=None, org_chart_layout=None):  # noqa: E501
        """SmartArtNode - a model defined in Swagger"""  # noqa: E501

        self._nodes = None
        self._shapes = None
        self._is_assistant = None
        self._text = None
        self._org_chart_layout = None

        if nodes is not None:
            self.nodes = nodes
        if shapes is not None:
            self.shapes = shapes
        self.is_assistant = is_assistant
        if text is not None:
            self.text = text
        self.org_chart_layout = org_chart_layout

    @property
    def nodes(self):
        """Gets the nodes of this SmartArtNode.  # noqa: E501

        Node list.  # noqa: E501

        :return: The nodes of this SmartArtNode.  # noqa: E501
        :rtype: list[SmartArtNode]
        """
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        """Sets the nodes of this SmartArtNode.

        Node list.  # noqa: E501

        :param nodes: The nodes of this SmartArtNode.  # noqa: E501
        :type: list[SmartArtNode]
        """
        self._nodes = nodes

    @property
    def shapes(self):
        """Gets the shapes of this SmartArtNode.  # noqa: E501

        Gets or sets the link to shapes.  # noqa: E501

        :return: The shapes of this SmartArtNode.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._shapes

    @shapes.setter
    def shapes(self, shapes):
        """Sets the shapes of this SmartArtNode.

        Gets or sets the link to shapes.  # noqa: E501

        :param shapes: The shapes of this SmartArtNode.  # noqa: E501
        :type: ResourceUriElement
        """
        self._shapes = shapes

    @property
    def is_assistant(self):
        """Gets the is_assistant of this SmartArtNode.  # noqa: E501

        True for and assistant node.  # noqa: E501

        :return: The is_assistant of this SmartArtNode.  # noqa: E501
        :rtype: bool
        """
        return self._is_assistant

    @is_assistant.setter
    def is_assistant(self, is_assistant):
        """Sets the is_assistant of this SmartArtNode.

        True for and assistant node.  # noqa: E501

        :param is_assistant: The is_assistant of this SmartArtNode.  # noqa: E501
        :type: bool
        """
        self._is_assistant = is_assistant

    @property
    def text(self):
        """Gets the text of this SmartArtNode.  # noqa: E501

        Node text.  # noqa: E501

        :return: The text of this SmartArtNode.  # noqa: E501
        :rtype: str
        """
        return self._text

    @text.setter
    def text(self, text):
        """Sets the text of this SmartArtNode.

        Node text.  # noqa: E501

        :param text: The text of this SmartArtNode.  # noqa: E501
        :type: str
        """
        self._text = text

    @property
    def org_chart_layout(self):
        """Gets the org_chart_layout of this SmartArtNode.  # noqa: E501

        Organization chart layout type associated with current node.  # noqa: E501

        :return: The org_chart_layout of this SmartArtNode.  # noqa: E501
        :rtype: str
        """
        return self._org_chart_layout

    @org_chart_layout.setter
    def org_chart_layout(self, org_chart_layout):
        """Sets the org_chart_layout of this SmartArtNode.

        Organization chart layout type associated with current node.  # noqa: E501

        :param org_chart_layout: The org_chart_layout of this SmartArtNode.  # noqa: E501
        :type: str
        """
        if org_chart_layout is not None:
            allowed_values = ["Initial", "Standart", "BothHanging", "LeftHanging", "RightHanging"]  # noqa: E501
            if org_chart_layout not in allowed_values:
                raise ValueError(
                    "Invalid value for `org_chart_layout` ({0}), must be one of {1}"  # noqa: E501
                    .format(org_chart_layout, allowed_values)
                )
        self._org_chart_layout = org_chart_layout

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
        if not isinstance(other, SmartArtNode):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
