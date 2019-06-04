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


class BodyPartMediaType(object):
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
        'type': 'str',
        'subtype': 'str',
        'parameters': 'dict(str, str)',
        'wildcard_type': 'bool',
        'wildcard_subtype': 'bool'
    }

    attribute_map = {
        'type': 'type',
        'subtype': 'subtype',
        'parameters': 'parameters',
        'wildcard_type': 'wildcardType',
        'wildcard_subtype': 'wildcardSubtype'
    }

    def __init__(self, type=None, subtype=None, parameters=None, wildcard_type=None, wildcard_subtype=None):  # noqa: E501
        """BodyPartMediaType - a model defined in OpenAPI"""  # noqa: E501

        self._type = None
        self._subtype = None
        self._parameters = None
        self._wildcard_type = None
        self._wildcard_subtype = None
        self.discriminator = None

        if type is not None:
            self.type = type
        if subtype is not None:
            self.subtype = subtype
        if parameters is not None:
            self.parameters = parameters
        if wildcard_type is not None:
            self.wildcard_type = wildcard_type
        if wildcard_subtype is not None:
            self.wildcard_subtype = wildcard_subtype

    @property
    def type(self):
        """Gets the type of this BodyPartMediaType.  # noqa: E501


        :return: The type of this BodyPartMediaType.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this BodyPartMediaType.


        :param type: The type of this BodyPartMediaType.  # noqa: E501
        :type: str
        """

        self._type = type

    @property
    def subtype(self):
        """Gets the subtype of this BodyPartMediaType.  # noqa: E501


        :return: The subtype of this BodyPartMediaType.  # noqa: E501
        :rtype: str
        """
        return self._subtype

    @subtype.setter
    def subtype(self, subtype):
        """Sets the subtype of this BodyPartMediaType.


        :param subtype: The subtype of this BodyPartMediaType.  # noqa: E501
        :type: str
        """

        self._subtype = subtype

    @property
    def parameters(self):
        """Gets the parameters of this BodyPartMediaType.  # noqa: E501


        :return: The parameters of this BodyPartMediaType.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Sets the parameters of this BodyPartMediaType.


        :param parameters: The parameters of this BodyPartMediaType.  # noqa: E501
        :type: dict(str, str)
        """

        self._parameters = parameters

    @property
    def wildcard_type(self):
        """Gets the wildcard_type of this BodyPartMediaType.  # noqa: E501


        :return: The wildcard_type of this BodyPartMediaType.  # noqa: E501
        :rtype: bool
        """
        return self._wildcard_type

    @wildcard_type.setter
    def wildcard_type(self, wildcard_type):
        """Sets the wildcard_type of this BodyPartMediaType.


        :param wildcard_type: The wildcard_type of this BodyPartMediaType.  # noqa: E501
        :type: bool
        """

        self._wildcard_type = wildcard_type

    @property
    def wildcard_subtype(self):
        """Gets the wildcard_subtype of this BodyPartMediaType.  # noqa: E501


        :return: The wildcard_subtype of this BodyPartMediaType.  # noqa: E501
        :rtype: bool
        """
        return self._wildcard_subtype

    @wildcard_subtype.setter
    def wildcard_subtype(self, wildcard_subtype):
        """Sets the wildcard_subtype of this BodyPartMediaType.


        :param wildcard_subtype: The wildcard_subtype of this BodyPartMediaType.  # noqa: E501
        :type: bool
        """

        self._wildcard_subtype = wildcard_subtype

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
        if not isinstance(other, BodyPartMediaType):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
