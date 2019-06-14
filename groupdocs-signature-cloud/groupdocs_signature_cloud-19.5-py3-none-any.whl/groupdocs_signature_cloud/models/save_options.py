# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="SaveOptions.py">
#   Copyright (c) 2003-2019 Aspose Pty Ltd
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

class SaveOptions(object):
    """
    Base document save options class
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'overwrite_existing': 'bool',
        'output_file_path': 'str',
        'save_format': 'str'
    }

    attribute_map = {
        'overwrite_existing': 'OverwriteExisting',
        'output_file_path': 'OutputFilePath',
        'save_format': 'SaveFormat'
    }

    def __init__(self, overwrite_existing=None, output_file_path=None, save_format=None, **kwargs):  # noqa: E501
        """Initializes new instance of SaveOptions"""  # noqa: E501

        self._overwrite_existing = None
        self._output_file_path = None
        self._save_format = None

        if overwrite_existing is not None:
            self.overwrite_existing = overwrite_existing
        if output_file_path is not None:
            self.output_file_path = output_file_path
        if save_format is not None:
            self.save_format = save_format
    
    @property
    def overwrite_existing(self):
        """
        Gets the overwrite_existing.  # noqa: E501

        Overwrite existing file with new output file. Otherwise new file will be created with number as suffix  # noqa: E501

        :return: The overwrite_existing.  # noqa: E501
        :rtype: bool
        """
        return self._overwrite_existing

    @overwrite_existing.setter
    def overwrite_existing(self, overwrite_existing):
        """
        Sets the overwrite_existing.

        Overwrite existing file with new output file. Otherwise new file will be created with number as suffix  # noqa: E501

        :param overwrite_existing: The overwrite_existing.  # noqa: E501
        :type: bool
        """
        if overwrite_existing is None:
            raise ValueError("Invalid value for `overwrite_existing`, must not be `None`")  # noqa: E501
        self._overwrite_existing = overwrite_existing
    
    @property
    def output_file_path(self):
        """
        Gets the output_file_path.  # noqa: E501

        Output file name  # noqa: E501

        :return: The output_file_path.  # noqa: E501
        :rtype: str
        """
        return self._output_file_path

    @output_file_path.setter
    def output_file_path(self, output_file_path):
        """
        Sets the output_file_path.

        Output file name  # noqa: E501

        :param output_file_path: The output_file_path.  # noqa: E501
        :type: str
        """
        self._output_file_path = output_file_path
    
    @property
    def save_format(self):
        """
        Gets the save_format.  # noqa: E501

        format of save  # noqa: E501

        :return: The save_format.  # noqa: E501
        :rtype: str
        """
        return self._save_format

    @save_format.setter
    def save_format(self, save_format):
        """
        Sets the save_format.

        format of save  # noqa: E501

        :param save_format: The save_format.  # noqa: E501
        :type: str
        """
        self._save_format = save_format

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
        if not isinstance(other, SaveOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
