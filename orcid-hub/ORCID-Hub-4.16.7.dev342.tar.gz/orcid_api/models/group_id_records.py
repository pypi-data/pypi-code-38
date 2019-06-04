# coding: utf-8

"""
    ORCID Member

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: Latest
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class GroupIdRecords(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, last_modified_date=None, total=None, page=None, page_size=None, group_id_record=None):
        """
        GroupIdRecords - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'last_modified_date': 'LastModifiedDate',
            'total': 'int',
            'page': 'int',
            'page_size': 'int',
            'group_id_record': 'list[GroupIdRecord]'
        }

        self.attribute_map = {
            'last_modified_date': 'last-modified-date',
            'total': 'total',
            'page': 'page',
            'page_size': 'page-size',
            'group_id_record': 'group-id-record'
        }

        self._last_modified_date = last_modified_date
        self._total = total
        self._page = page
        self._page_size = page_size
        self._group_id_record = group_id_record

    @property
    def last_modified_date(self):
        """
        Gets the last_modified_date of this GroupIdRecords.

        :return: The last_modified_date of this GroupIdRecords.
        :rtype: LastModifiedDate
        """
        return self._last_modified_date

    @last_modified_date.setter
    def last_modified_date(self, last_modified_date):
        """
        Sets the last_modified_date of this GroupIdRecords.

        :param last_modified_date: The last_modified_date of this GroupIdRecords.
        :type: LastModifiedDate
        """

        self._last_modified_date = last_modified_date

    @property
    def total(self):
        """
        Gets the total of this GroupIdRecords.

        :return: The total of this GroupIdRecords.
        :rtype: int
        """
        return self._total

    @total.setter
    def total(self, total):
        """
        Sets the total of this GroupIdRecords.

        :param total: The total of this GroupIdRecords.
        :type: int
        """
        if total is None:
            raise ValueError("Invalid value for `total`, must not be `None`")

        self._total = total

    @property
    def page(self):
        """
        Gets the page of this GroupIdRecords.

        :return: The page of this GroupIdRecords.
        :rtype: int
        """
        return self._page

    @page.setter
    def page(self, page):
        """
        Sets the page of this GroupIdRecords.

        :param page: The page of this GroupIdRecords.
        :type: int
        """
        if page is None:
            raise ValueError("Invalid value for `page`, must not be `None`")

        self._page = page

    @property
    def page_size(self):
        """
        Gets the page_size of this GroupIdRecords.

        :return: The page_size of this GroupIdRecords.
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """
        Sets the page_size of this GroupIdRecords.

        :param page_size: The page_size of this GroupIdRecords.
        :type: int
        """
        if page_size is None:
            raise ValueError("Invalid value for `page_size`, must not be `None`")

        self._page_size = page_size

    @property
    def group_id_record(self):
        """
        Gets the group_id_record of this GroupIdRecords.

        :return: The group_id_record of this GroupIdRecords.
        :rtype: list[GroupIdRecord]
        """
        return self._group_id_record

    @group_id_record.setter
    def group_id_record(self, group_id_record):
        """
        Sets the group_id_record of this GroupIdRecords.

        :param group_id_record: The group_id_record of this GroupIdRecords.
        :type: list[GroupIdRecord]
        """

        self._group_id_record = group_id_record

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
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
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, GroupIdRecords):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
