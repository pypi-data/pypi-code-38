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
from orcid_api_v3.models.item_v30_rc2 import ItemV30Rc2  # noqa: F401,E501


class ItemsV30Rc2(object):
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
        'item': 'list[ItemV30Rc2]'
    }

    attribute_map = {
        'item': 'item'
    }

    def __init__(self, item=None):  # noqa: E501
        """ItemsV30Rc2 - a model defined in Swagger"""  # noqa: E501
        self._item = None
        self.discriminator = None
        self.item = item

    @property
    def item(self):
        """Gets the item of this ItemsV30Rc2.  # noqa: E501


        :return: The item of this ItemsV30Rc2.  # noqa: E501
        :rtype: list[ItemV30Rc2]
        """
        return self._item

    @item.setter
    def item(self, item):
        """Sets the item of this ItemsV30Rc2.


        :param item: The item of this ItemsV30Rc2.  # noqa: E501
        :type: list[ItemV30Rc2]
        """
        if item is None:
            raise ValueError("Invalid value for `item`, must not be `None`")  # noqa: E501

        self._item = item

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
        if issubclass(ItemsV30Rc2, dict):
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
        if not isinstance(other, ItemsV30Rc2):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
