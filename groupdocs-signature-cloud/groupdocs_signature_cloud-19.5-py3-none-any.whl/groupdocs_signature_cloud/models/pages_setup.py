# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="PagesSetup.py">
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

class PagesSetup(object):
    """
    Describes special pages of document to process
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'first_page': 'bool',
        'last_page': 'bool',
        'odd_pages': 'bool',
        'even_pages': 'bool',
        'page_numbers': 'list[int]'
    }

    attribute_map = {
        'first_page': 'FirstPage',
        'last_page': 'LastPage',
        'odd_pages': 'OddPages',
        'even_pages': 'EvenPages',
        'page_numbers': 'PageNumbers'
    }

    def __init__(self, first_page=None, last_page=None, odd_pages=None, even_pages=None, page_numbers=None, **kwargs):  # noqa: E501
        """Initializes new instance of PagesSetup"""  # noqa: E501

        self._first_page = None
        self._last_page = None
        self._odd_pages = None
        self._even_pages = None
        self._page_numbers = None

        if first_page is not None:
            self.first_page = first_page
        if last_page is not None:
            self.last_page = last_page
        if odd_pages is not None:
            self.odd_pages = odd_pages
        if even_pages is not None:
            self.even_pages = even_pages
        if page_numbers is not None:
            self.page_numbers = page_numbers
    
    @property
    def first_page(self):
        """
        Gets the first_page.  # noqa: E501

        Get or set flag to use first document page  # noqa: E501

        :return: The first_page.  # noqa: E501
        :rtype: bool
        """
        return self._first_page

    @first_page.setter
    def first_page(self, first_page):
        """
        Sets the first_page.

        Get or set flag to use first document page  # noqa: E501

        :param first_page: The first_page.  # noqa: E501
        :type: bool
        """
        if first_page is None:
            raise ValueError("Invalid value for `first_page`, must not be `None`")  # noqa: E501
        self._first_page = first_page
    
    @property
    def last_page(self):
        """
        Gets the last_page.  # noqa: E501

        Get or set flag to use last document page  # noqa: E501

        :return: The last_page.  # noqa: E501
        :rtype: bool
        """
        return self._last_page

    @last_page.setter
    def last_page(self, last_page):
        """
        Sets the last_page.

        Get or set flag to use last document page  # noqa: E501

        :param last_page: The last_page.  # noqa: E501
        :type: bool
        """
        if last_page is None:
            raise ValueError("Invalid value for `last_page`, must not be `None`")  # noqa: E501
        self._last_page = last_page
    
    @property
    def odd_pages(self):
        """
        Gets the odd_pages.  # noqa: E501

        Get or set flag to use odd pages of document  # noqa: E501

        :return: The odd_pages.  # noqa: E501
        :rtype: bool
        """
        return self._odd_pages

    @odd_pages.setter
    def odd_pages(self, odd_pages):
        """
        Sets the odd_pages.

        Get or set flag to use odd pages of document  # noqa: E501

        :param odd_pages: The odd_pages.  # noqa: E501
        :type: bool
        """
        if odd_pages is None:
            raise ValueError("Invalid value for `odd_pages`, must not be `None`")  # noqa: E501
        self._odd_pages = odd_pages
    
    @property
    def even_pages(self):
        """
        Gets the even_pages.  # noqa: E501

        Get or set flag to use even pages of document  # noqa: E501

        :return: The even_pages.  # noqa: E501
        :rtype: bool
        """
        return self._even_pages

    @even_pages.setter
    def even_pages(self, even_pages):
        """
        Sets the even_pages.

        Get or set flag to use even pages of document  # noqa: E501

        :param even_pages: The even_pages.  # noqa: E501
        :type: bool
        """
        if even_pages is None:
            raise ValueError("Invalid value for `even_pages`, must not be `None`")  # noqa: E501
        self._even_pages = even_pages
    
    @property
    def page_numbers(self):
        """
        Gets the page_numbers.  # noqa: E501

        Set arbitrary pages of document to use  # noqa: E501

        :return: The page_numbers.  # noqa: E501
        :rtype: list[int]
        """
        return self._page_numbers

    @page_numbers.setter
    def page_numbers(self, page_numbers):
        """
        Sets the page_numbers.

        Set arbitrary pages of document to use  # noqa: E501

        :param page_numbers: The page_numbers.  # noqa: E501
        :type: list[int]
        """
        self._page_numbers = page_numbers

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
        if not isinstance(other, PagesSetup):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
