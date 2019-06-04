# coding: utf-8

"""
    Onshape REST API

    The Onshape REST API consumed by all clients.  # noqa: E501

    OpenAPI spec version: 1.97
    Contact: api-support@onshape.zendesk.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class ShippingDetails(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'address': 'Address',
        'name': 'str',
        'phone': 'str'
    }

    attribute_map = {
        'address': 'address',
        'name': 'name',
        'phone': 'phone'
    }

    def __init__(self, address=None, name=None, phone=None):  # noqa: E501
        """ShippingDetails - a model defined in OpenAPI"""  # noqa: E501

        self._address = None
        self._name = None
        self._phone = None
        self.discriminator = None

        if address is not None:
            self.address = address
        if name is not None:
            self.name = name
        if phone is not None:
            self.phone = phone

    @property
    def address(self):
        """Gets the address of this ShippingDetails.  # noqa: E501


        :return: The address of this ShippingDetails.  # noqa: E501
        :rtype: Address
        """
        return self._address

    @address.setter
    def address(self, address):
        """Sets the address of this ShippingDetails.


        :param address: The address of this ShippingDetails.  # noqa: E501
        :type: Address
        """

        self._address = address

    @property
    def name(self):
        """Gets the name of this ShippingDetails.  # noqa: E501


        :return: The name of this ShippingDetails.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this ShippingDetails.


        :param name: The name of this ShippingDetails.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def phone(self):
        """Gets the phone of this ShippingDetails.  # noqa: E501


        :return: The phone of this ShippingDetails.  # noqa: E501
        :rtype: str
        """
        return self._phone

    @phone.setter
    def phone(self, phone):
        """Sets the phone of this ShippingDetails.


        :param phone: The phone of this ShippingDetails.  # noqa: E501
        :type: str
        """

        self._phone = phone

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
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
        if not isinstance(other, ShippingDetails):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
