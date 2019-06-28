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

from asposeslidescloud.models.task import Task

class SaveShape(Task):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'type': 'str',
        'format': 'str',
        'shape_path': 'str',
        'output': 'OutputFile',
        'options': 'IShapeExportOptions'
    }

    attribute_map = {
        'type': 'Type',
        'format': 'Format',
        'shape_path': 'ShapePath',
        'output': 'Output',
        'options': 'Options'
    }

    def __init__(self, type='SaveShape', format=None, shape_path=None, output=None, options=None):  # noqa: E501
        """SaveShape - a model defined in Swagger"""  # noqa: E501
        super(SaveShape, self).__init__(type)

        self._format = None
        self._shape_path = None
        self._output = None
        self._options = None

        self.format = format
        if shape_path is not None:
            self.shape_path = shape_path
        if output is not None:
            self.output = output
        if options is not None:
            self.options = options

    @property
    def format(self):
        """Gets the format of this SaveShape.  # noqa: E501

        Format.  # noqa: E501

        :return: The format of this SaveShape.  # noqa: E501
        :rtype: str
        """
        return self._format

    @format.setter
    def format(self, format):
        """Sets the format of this SaveShape.

        Format.  # noqa: E501

        :param format: The format of this SaveShape.  # noqa: E501
        :type: str
        """
        if format is not None:
            allowed_values = ["Jpeg", "Png", "Gif", "Bmp", "Tiff", "Svg"]  # noqa: E501
            if format not in allowed_values:
                raise ValueError(
                    "Invalid value for `format` ({0}), must be one of {1}"  # noqa: E501
                    .format(format, allowed_values)
                )
        self._format = format

    @property
    def shape_path(self):
        """Gets the shape_path of this SaveShape.  # noqa: E501

        Shape path.  # noqa: E501

        :return: The shape_path of this SaveShape.  # noqa: E501
        :rtype: str
        """
        return self._shape_path

    @shape_path.setter
    def shape_path(self, shape_path):
        """Sets the shape_path of this SaveShape.

        Shape path.  # noqa: E501

        :param shape_path: The shape_path of this SaveShape.  # noqa: E501
        :type: str
        """
        self._shape_path = shape_path

    @property
    def output(self):
        """Gets the output of this SaveShape.  # noqa: E501

        Output file.  # noqa: E501

        :return: The output of this SaveShape.  # noqa: E501
        :rtype: OutputFile
        """
        return self._output

    @output.setter
    def output(self, output):
        """Sets the output of this SaveShape.

        Output file.  # noqa: E501

        :param output: The output of this SaveShape.  # noqa: E501
        :type: OutputFile
        """
        self._output = output

    @property
    def options(self):
        """Gets the options of this SaveShape.  # noqa: E501

        Save options.  # noqa: E501

        :return: The options of this SaveShape.  # noqa: E501
        :rtype: IShapeExportOptions
        """
        return self._options

    @options.setter
    def options(self, options):
        """Sets the options of this SaveShape.

        Save options.  # noqa: E501

        :param options: The options of this SaveShape.  # noqa: E501
        :type: IShapeExportOptions
        """
        self._options = options

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
        if not isinstance(other, SaveShape):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
