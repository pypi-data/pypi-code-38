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
from orcid_api_v3.models.group_id_record import GroupIdRecord  # noqa: F401,E501
from orcid_api_v3.models.last_modified_date_v30_rc2 import LastModifiedDateV30Rc2  # noqa: F401,E501


class GroupIdRecords(object):
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
        'last_modified_date': 'LastModifiedDateV30Rc2',
        'total': 'int',
        'page': 'int',
        'page_size': 'int',
        'group_id_record': 'list[GroupIdRecord]'
    }

    attribute_map = {
        'last_modified_date': 'last-modified-date',
        'total': 'total',
        'page': 'page',
        'page_size': 'page-size',
        'group_id_record': 'group-id-record'
    }

    def __init__(self, last_modified_date=None, total=None, page=None, page_size=None, group_id_record=None):  # noqa: E501
        """GroupIdRecords - a model defined in Swagger"""  # noqa: E501
        self._last_modified_date = None
        self._total = None
        self._page = None
        self._page_size = None
        self._group_id_record = None
        self.discriminator = None
        if last_modified_date is not None:
            self.last_modified_date = last_modified_date
        self.total = total
        self.page = page
        self.page_size = page_size
        if group_id_record is not None:
            self.group_id_record = group_id_record

    @property
    def last_modified_date(self):
        """Gets the last_modified_date of this GroupIdRecords.  # noqa: E501


        :return: The last_modified_date of this GroupIdRecords.  # noqa: E501
        :rtype: LastModifiedDateV30Rc2
        """
        return self._last_modified_date

    @last_modified_date.setter
    def last_modified_date(self, last_modified_date):
        """Sets the last_modified_date of this GroupIdRecords.


        :param last_modified_date: The last_modified_date of this GroupIdRecords.  # noqa: E501
        :type: LastModifiedDateV30Rc2
        """

        self._last_modified_date = last_modified_date

    @property
    def total(self):
        """Gets the total of this GroupIdRecords.  # noqa: E501


        :return: The total of this GroupIdRecords.  # noqa: E501
        :rtype: int
        """
        return self._total

    @total.setter
    def total(self, total):
        """Sets the total of this GroupIdRecords.


        :param total: The total of this GroupIdRecords.  # noqa: E501
        :type: int
        """
        if total is None:
            raise ValueError("Invalid value for `total`, must not be `None`")  # noqa: E501

        self._total = total

    @property
    def page(self):
        """Gets the page of this GroupIdRecords.  # noqa: E501


        :return: The page of this GroupIdRecords.  # noqa: E501
        :rtype: int
        """
        return self._page

    @page.setter
    def page(self, page):
        """Sets the page of this GroupIdRecords.


        :param page: The page of this GroupIdRecords.  # noqa: E501
        :type: int
        """
        if page is None:
            raise ValueError("Invalid value for `page`, must not be `None`")  # noqa: E501

        self._page = page

    @property
    def page_size(self):
        """Gets the page_size of this GroupIdRecords.  # noqa: E501


        :return: The page_size of this GroupIdRecords.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this GroupIdRecords.


        :param page_size: The page_size of this GroupIdRecords.  # noqa: E501
        :type: int
        """
        if page_size is None:
            raise ValueError("Invalid value for `page_size`, must not be `None`")  # noqa: E501

        self._page_size = page_size

    @property
    def group_id_record(self):
        """Gets the group_id_record of this GroupIdRecords.  # noqa: E501


        :return: The group_id_record of this GroupIdRecords.  # noqa: E501
        :rtype: list[GroupIdRecord]
        """
        return self._group_id_record

    @group_id_record.setter
    def group_id_record(self, group_id_record):
        """Sets the group_id_record of this GroupIdRecords.


        :param group_id_record: The group_id_record of this GroupIdRecords.  # noqa: E501
        :type: list[GroupIdRecord]
        """

        self._group_id_record = group_id_record

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
        if issubclass(GroupIdRecords, dict):
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
        if not isinstance(other, GroupIdRecords):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
