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

class SaveSlide(Task):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'type': 'str',
        'output': 'OutputFile',
        'format': 'str',
        'options': 'ExportOptions',
        'width': 'int',
        'height': 'int',
        'position': 'int'
    }

    attribute_map = {
        'type': 'Type',
        'output': 'Output',
        'format': 'Format',
        'options': 'Options',
        'width': 'Width',
        'height': 'Height',
        'position': 'Position'
    }

    def __init__(self, type='SaveSlide', output=None, format=None, options=None, width=None, height=None, position=None):  # noqa: E501
        """SaveSlide - a model defined in Swagger"""  # noqa: E501
        super(SaveSlide, self).__init__(type)

        self._output = None
        self._format = None
        self._options = None
        self._width = None
        self._height = None
        self._position = None

        if output is not None:
            self.output = output
        self.format = format
        if options is not None:
            self.options = options
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        self.position = position

    @property
    def output(self):
        """Gets the output of this SaveSlide.  # noqa: E501

        Output to save the slide to.  # noqa: E501

        :return: The output of this SaveSlide.  # noqa: E501
        :rtype: OutputFile
        """
        return self._output

    @output.setter
    def output(self, output):
        """Sets the output of this SaveSlide.

        Output to save the slide to.  # noqa: E501

        :param output: The output of this SaveSlide.  # noqa: E501
        :type: OutputFile
        """
        self._output = output

    @property
    def format(self):
        """Gets the format of this SaveSlide.  # noqa: E501

        Save format.  # noqa: E501

        :return: The format of this SaveSlide.  # noqa: E501
        :rtype: str
        """
        return self._format

    @format.setter
    def format(self, format):
        """Sets the format of this SaveSlide.

        Save format.  # noqa: E501

        :param format: The format of this SaveSlide.  # noqa: E501
        :type: str
        """
        if format is not None:
            allowed_values = ["Jpeg", "Png", "Gif", "Bmp", "Tiff", "Html", "Pdf", "Xps", "Pptx", "Odp", "Otp", "Ppt", "Pps", "Ppsx", "Pptm", "Ppsm", "Potx", "Potm", "Svg"]  # noqa: E501
            if format not in allowed_values:
                raise ValueError(
                    "Invalid value for `format` ({0}), must be one of {1}"  # noqa: E501
                    .format(format, allowed_values)
                )
        self._format = format

    @property
    def options(self):
        """Gets the options of this SaveSlide.  # noqa: E501

        Save options.  # noqa: E501

        :return: The options of this SaveSlide.  # noqa: E501
        :rtype: ExportOptions
        """
        return self._options

    @options.setter
    def options(self, options):
        """Sets the options of this SaveSlide.

        Save options.  # noqa: E501

        :param options: The options of this SaveSlide.  # noqa: E501
        :type: ExportOptions
        """
        self._options = options

    @property
    def width(self):
        """Gets the width of this SaveSlide.  # noqa: E501

        Result width for saving to an image format.  # noqa: E501

        :return: The width of this SaveSlide.  # noqa: E501
        :rtype: int
        """
        return self._width

    @width.setter
    def width(self, width):
        """Sets the width of this SaveSlide.

        Result width for saving to an image format.  # noqa: E501

        :param width: The width of this SaveSlide.  # noqa: E501
        :type: int
        """
        self._width = width

    @property
    def height(self):
        """Gets the height of this SaveSlide.  # noqa: E501

        Result height for saving to an image format.  # noqa: E501

        :return: The height of this SaveSlide.  # noqa: E501
        :rtype: int
        """
        return self._height

    @height.setter
    def height(self, height):
        """Sets the height of this SaveSlide.

        Result height for saving to an image format.  # noqa: E501

        :param height: The height of this SaveSlide.  # noqa: E501
        :type: int
        """
        self._height = height

    @property
    def position(self):
        """Gets the position of this SaveSlide.  # noqa: E501

        Slide index.  # noqa: E501

        :return: The position of this SaveSlide.  # noqa: E501
        :rtype: int
        """
        return self._position

    @position.setter
    def position(self, position):
        """Sets the position of this SaveSlide.

        Slide index.  # noqa: E501

        :param position: The position of this SaveSlide.  # noqa: E501
        :type: int
        """
        self._position = position

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
        if not isinstance(other, SaveSlide):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
