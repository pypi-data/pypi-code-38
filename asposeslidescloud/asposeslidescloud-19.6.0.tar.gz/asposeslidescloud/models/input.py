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


class Input(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'template': 'InputFile',
        'html_data': 'InputFile',
        'template_data': 'InputFile'
    }

    attribute_map = {
        'template': 'Template',
        'html_data': 'HtmlData',
        'template_data': 'TemplateData'
    }

    def __init__(self, template=None, html_data=None, template_data=None):  # noqa: E501
        """Input - a model defined in Swagger"""  # noqa: E501

        self._template = None
        self._html_data = None
        self._template_data = None

        if template is not None:
            self.template = template
        if html_data is not None:
            self.html_data = html_data
        if template_data is not None:
            self.template_data = template_data

    @property
    def template(self):
        """Gets the template of this Input.  # noqa: E501

        Get or sets template document. If property is null new empty presentation will be created.  # noqa: E501

        :return: The template of this Input.  # noqa: E501
        :rtype: InputFile
        """
        return self._template

    @template.setter
    def template(self, template):
        """Sets the template of this Input.

        Get or sets template document. If property is null new empty presentation will be created.  # noqa: E501

        :param template: The template of this Input.  # noqa: E501
        :type: InputFile
        """
        self._template = template

    @property
    def html_data(self):
        """Gets the html_data of this Input.  # noqa: E501

        Get or sets html data for generate new presentation.  # noqa: E501

        :return: The html_data of this Input.  # noqa: E501
        :rtype: InputFile
        """
        return self._html_data

    @html_data.setter
    def html_data(self, html_data):
        """Sets the html_data of this Input.

        Get or sets html data for generate new presentation.  # noqa: E501

        :param html_data: The html_data of this Input.  # noqa: E501
        :type: InputFile
        """
        self._html_data = html_data

    @property
    def template_data(self):
        """Gets the template_data of this Input.  # noqa: E501

        Get or sets data for template engine.  # noqa: E501

        :return: The template_data of this Input.  # noqa: E501
        :rtype: InputFile
        """
        return self._template_data

    @template_data.setter
    def template_data(self, template_data):
        """Sets the template_data of this Input.

        Get or sets data for template engine.  # noqa: E501

        :param template_data: The template_data of this Input.  # noqa: E501
        :type: InputFile
        """
        self._template_data = template_data

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
        if not isinstance(other, Input):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
