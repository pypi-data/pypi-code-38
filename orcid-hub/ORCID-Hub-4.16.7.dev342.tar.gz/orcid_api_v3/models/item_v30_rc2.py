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
from orcid_api_v3.models.external_idv30_rc2 import ExternalIDV30Rc2  # noqa: F401,E501


class ItemV30Rc2(object):
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
        'put_code': 'str',
        'item_type': 'str',
        'item_name': 'str',
        'external_id': 'ExternalIDV30Rc2'
    }

    attribute_map = {
        'put_code': 'put-code',
        'item_type': 'item-type',
        'item_name': 'item-name',
        'external_id': 'external-id'
    }

    def __init__(self, put_code=None, item_type=None, item_name=None, external_id=None):  # noqa: E501
        """ItemV30Rc2 - a model defined in Swagger"""  # noqa: E501
        self._put_code = None
        self._item_type = None
        self._item_name = None
        self._external_id = None
        self.discriminator = None
        if put_code is not None:
            self.put_code = put_code
        self.item_type = item_type
        self.item_name = item_name
        self.external_id = external_id

    @property
    def put_code(self):
        """Gets the put_code of this ItemV30Rc2.  # noqa: E501


        :return: The put_code of this ItemV30Rc2.  # noqa: E501
        :rtype: str
        """
        return self._put_code

    @put_code.setter
    def put_code(self, put_code):
        """Sets the put_code of this ItemV30Rc2.


        :param put_code: The put_code of this ItemV30Rc2.  # noqa: E501
        :type: str
        """

        self._put_code = put_code

    @property
    def item_type(self):
        """Gets the item_type of this ItemV30Rc2.  # noqa: E501


        :return: The item_type of this ItemV30Rc2.  # noqa: E501
        :rtype: str
        """
        return self._item_type

    @item_type.setter
    def item_type(self, item_type):
        """Sets the item_type of this ItemV30Rc2.


        :param item_type: The item_type of this ItemV30Rc2.  # noqa: E501
        :type: str
        """
        if item_type is None:
            raise ValueError("Invalid value for `item_type`, must not be `None`")  # noqa: E501
        allowed_values = ["DISTINCTION", "EDUCATION", "EMPLOYMENT", "INVITED_POSITION", "FUNDING", "MEMBERSHIP", "PEER_REVIEW", "QUALIFICATION", "SERVICE", "WORK", "RESEARCH_RESOURCE"]  # noqa: E501
        if item_type not in allowed_values:
            raise ValueError(
                "Invalid value for `item_type` ({0}), must be one of {1}"  # noqa: E501
                .format(item_type, allowed_values)
            )

        self._item_type = item_type

    @property
    def item_name(self):
        """Gets the item_name of this ItemV30Rc2.  # noqa: E501


        :return: The item_name of this ItemV30Rc2.  # noqa: E501
        :rtype: str
        """
        return self._item_name

    @item_name.setter
    def item_name(self, item_name):
        """Sets the item_name of this ItemV30Rc2.


        :param item_name: The item_name of this ItemV30Rc2.  # noqa: E501
        :type: str
        """
        if item_name is None:
            raise ValueError("Invalid value for `item_name`, must not be `None`")  # noqa: E501

        self._item_name = item_name

    @property
    def external_id(self):
        """Gets the external_id of this ItemV30Rc2.  # noqa: E501


        :return: The external_id of this ItemV30Rc2.  # noqa: E501
        :rtype: ExternalIDV30Rc2
        """
        return self._external_id

    @external_id.setter
    def external_id(self, external_id):
        """Sets the external_id of this ItemV30Rc2.


        :param external_id: The external_id of this ItemV30Rc2.  # noqa: E501
        :type: ExternalIDV30Rc2
        """
        if external_id is None:
            raise ValueError("Invalid value for `external_id`, must not be `None`")  # noqa: E501

        self._external_id = external_id

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
        if issubclass(ItemV30Rc2, dict):
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
        if not isinstance(other, ItemV30Rc2):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
