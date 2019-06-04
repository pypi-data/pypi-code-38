# coding: utf-8

"""
    ORCID Member

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: Latest
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six
from orcid_api_v3.models.keyword_v30 import KeywordV30  # noqa: F401,E501
from orcid_api_v3.models.last_modified_date_v30 import LastModifiedDateV30  # noqa: F401,E501


class KeywordsV30(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'last_modified_date': 'LastModifiedDateV30',
        'keyword': 'list[KeywordV30]',
        'path': 'str'
    }

    attribute_map = {
        'last_modified_date': 'last-modified-date',
        'keyword': 'keyword',
        'path': 'path'
    }

    def __init__(self, last_modified_date=None, keyword=None, path=None):  # noqa: E501
        """KeywordsV30 - a model defined in Swagger"""  # noqa: E501
        self._last_modified_date = None
        self._keyword = None
        self._path = None
        self.discriminator = None
        if last_modified_date is not None:
            self.last_modified_date = last_modified_date
        if keyword is not None:
            self.keyword = keyword
        if path is not None:
            self.path = path

    @property
    def last_modified_date(self):
        """Gets the last_modified_date of this KeywordsV30.  # noqa: E501


        :return: The last_modified_date of this KeywordsV30.  # noqa: E501
        :rtype: LastModifiedDateV30
        """
        return self._last_modified_date

    @last_modified_date.setter
    def last_modified_date(self, last_modified_date):
        """Sets the last_modified_date of this KeywordsV30.


        :param last_modified_date: The last_modified_date of this KeywordsV30.  # noqa: E501
        :type: LastModifiedDateV30
        """

        self._last_modified_date = last_modified_date

    @property
    def keyword(self):
        """Gets the keyword of this KeywordsV30.  # noqa: E501


        :return: The keyword of this KeywordsV30.  # noqa: E501
        :rtype: list[KeywordV30]
        """
        return self._keyword

    @keyword.setter
    def keyword(self, keyword):
        """Sets the keyword of this KeywordsV30.


        :param keyword: The keyword of this KeywordsV30.  # noqa: E501
        :type: list[KeywordV30]
        """

        self._keyword = keyword

    @property
    def path(self):
        """Gets the path of this KeywordsV30.  # noqa: E501


        :return: The path of this KeywordsV30.  # noqa: E501
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """Sets the path of this KeywordsV30.


        :param path: The path of this KeywordsV30.  # noqa: E501
        :type: str
        """

        self._path = path

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
        if issubclass(KeywordsV30, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, KeywordsV30):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
