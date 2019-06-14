# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="InfoResult.py">
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

class InfoResult(object):
    """
    Document info result
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'file_info': 'FileInfo',
        'extension': 'str',
        'file_format': 'str',
        'size': 'int',
        'pages_count': 'int',
        'date_created': 'datetime',
        'date_modified': 'datetime',
        'width_for_max_height': 'int',
        'max_page_height': 'int',
        'pages': 'list[PageInfo]'
    }

    attribute_map = {
        'file_info': 'FileInfo',
        'extension': 'Extension',
        'file_format': 'FileFormat',
        'size': 'Size',
        'pages_count': 'PagesCount',
        'date_created': 'DateCreated',
        'date_modified': 'DateModified',
        'width_for_max_height': 'WidthForMaxHeight',
        'max_page_height': 'MaxPageHeight',
        'pages': 'Pages'
    }

    def __init__(self, file_info=None, extension=None, file_format=None, size=None, pages_count=None, date_created=None, date_modified=None, width_for_max_height=None, max_page_height=None, pages=None, **kwargs):  # noqa: E501
        """Initializes new instance of InfoResult"""  # noqa: E501

        self._file_info = None
        self._extension = None
        self._file_format = None
        self._size = None
        self._pages_count = None
        self._date_created = None
        self._date_modified = None
        self._width_for_max_height = None
        self._max_page_height = None
        self._pages = None

        if file_info is not None:
            self.file_info = file_info
        if extension is not None:
            self.extension = extension
        if file_format is not None:
            self.file_format = file_format
        if size is not None:
            self.size = size
        if pages_count is not None:
            self.pages_count = pages_count
        if date_created is not None:
            self.date_created = date_created
        if date_modified is not None:
            self.date_modified = date_modified
        if width_for_max_height is not None:
            self.width_for_max_height = width_for_max_height
        if max_page_height is not None:
            self.max_page_height = max_page_height
        if pages is not None:
            self.pages = pages
    
    @property
    def file_info(self):
        """
        Gets the file_info.  # noqa: E501

        File info  # noqa: E501

        :return: The file_info.  # noqa: E501
        :rtype: FileInfo
        """
        return self._file_info

    @file_info.setter
    def file_info(self, file_info):
        """
        Sets the file_info.

        File info  # noqa: E501

        :param file_info: The file_info.  # noqa: E501
        :type: FileInfo
        """
        self._file_info = file_info
    
    @property
    def extension(self):
        """
        Gets the extension.  # noqa: E501

        Document extension  # noqa: E501

        :return: The extension.  # noqa: E501
        :rtype: str
        """
        return self._extension

    @extension.setter
    def extension(self, extension):
        """
        Sets the extension.

        Document extension  # noqa: E501

        :param extension: The extension.  # noqa: E501
        :type: str
        """
        self._extension = extension
    
    @property
    def file_format(self):
        """
        Gets the file_format.  # noqa: E501

        Document file format  # noqa: E501

        :return: The file_format.  # noqa: E501
        :rtype: str
        """
        return self._file_format

    @file_format.setter
    def file_format(self, file_format):
        """
        Sets the file_format.

        Document file format  # noqa: E501

        :param file_format: The file_format.  # noqa: E501
        :type: str
        """
        self._file_format = file_format
    
    @property
    def size(self):
        """
        Gets the size.  # noqa: E501

        Document size in bytes  # noqa: E501

        :return: The size.  # noqa: E501
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size):
        """
        Sets the size.

        Document size in bytes  # noqa: E501

        :param size: The size.  # noqa: E501
        :type: int
        """
        if size is None:
            raise ValueError("Invalid value for `size`, must not be `None`")  # noqa: E501
        self._size = size
    
    @property
    def pages_count(self):
        """
        Gets the pages_count.  # noqa: E501

        Count of pages in document  # noqa: E501

        :return: The pages_count.  # noqa: E501
        :rtype: int
        """
        return self._pages_count

    @pages_count.setter
    def pages_count(self, pages_count):
        """
        Sets the pages_count.

        Count of pages in document  # noqa: E501

        :param pages_count: The pages_count.  # noqa: E501
        :type: int
        """
        if pages_count is None:
            raise ValueError("Invalid value for `pages_count`, must not be `None`")  # noqa: E501
        self._pages_count = pages_count
    
    @property
    def date_created(self):
        """
        Gets the date_created.  # noqa: E501

        Document created date  # noqa: E501

        :return: The date_created.  # noqa: E501
        :rtype: datetime
        """
        return self._date_created

    @date_created.setter
    def date_created(self, date_created):
        """
        Sets the date_created.

        Document created date  # noqa: E501

        :param date_created: The date_created.  # noqa: E501
        :type: datetime
        """
        if date_created is None:
            raise ValueError("Invalid value for `date_created`, must not be `None`")  # noqa: E501
        self._date_created = date_created
    
    @property
    def date_modified(self):
        """
        Gets the date_modified.  # noqa: E501

        Document modification date  # noqa: E501

        :return: The date_modified.  # noqa: E501
        :rtype: datetime
        """
        return self._date_modified

    @date_modified.setter
    def date_modified(self, date_modified):
        """
        Sets the date_modified.

        Document modification date  # noqa: E501

        :param date_modified: The date_modified.  # noqa: E501
        :type: datetime
        """
        if date_modified is None:
            raise ValueError("Invalid value for `date_modified`, must not be `None`")  # noqa: E501
        self._date_modified = date_modified
    
    @property
    def width_for_max_height(self):
        """
        Gets the width_for_max_height.  # noqa: E501

        Specifies width for max height of document page  # noqa: E501

        :return: The width_for_max_height.  # noqa: E501
        :rtype: int
        """
        return self._width_for_max_height

    @width_for_max_height.setter
    def width_for_max_height(self, width_for_max_height):
        """
        Sets the width_for_max_height.

        Specifies width for max height of document page  # noqa: E501

        :param width_for_max_height: The width_for_max_height.  # noqa: E501
        :type: int
        """
        if width_for_max_height is None:
            raise ValueError("Invalid value for `width_for_max_height`, must not be `None`")  # noqa: E501
        self._width_for_max_height = width_for_max_height
    
    @property
    def max_page_height(self):
        """
        Gets the max_page_height.  # noqa: E501

        Specifies max page height  # noqa: E501

        :return: The max_page_height.  # noqa: E501
        :rtype: int
        """
        return self._max_page_height

    @max_page_height.setter
    def max_page_height(self, max_page_height):
        """
        Sets the max_page_height.

        Specifies max page height  # noqa: E501

        :param max_page_height: The max_page_height.  # noqa: E501
        :type: int
        """
        if max_page_height is None:
            raise ValueError("Invalid value for `max_page_height`, must not be `None`")  # noqa: E501
        self._max_page_height = max_page_height
    
    @property
    def pages(self):
        """
        Gets the pages.  # noqa: E501

        List of document pages descriptions  # noqa: E501

        :return: The pages.  # noqa: E501
        :rtype: list[PageInfo]
        """
        return self._pages

    @pages.setter
    def pages(self, pages):
        """
        Sets the pages.

        List of document pages descriptions  # noqa: E501

        :param pages: The pages.  # noqa: E501
        :type: list[PageInfo]
        """
        self._pages = pages

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
        if not isinstance(other, InfoResult):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
