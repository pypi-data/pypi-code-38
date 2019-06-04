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


class BTAPIKeyParams(object):
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
        'scope_names': 'list[str]',
        'company_id': 'str'
    }

    attribute_map = {
        'scope_names': 'scopeNames',
        'company_id': 'companyId'
    }

    def __init__(self, scope_names=None, company_id=None):  # noqa: E501
        """BTAPIKeyParams - a model defined in OpenAPI"""  # noqa: E501

        self._scope_names = None
        self._company_id = None
        self.discriminator = None

        if scope_names is not None:
            self.scope_names = scope_names
        if company_id is not None:
            self.company_id = company_id

    @property
    def scope_names(self):
        """Gets the scope_names of this BTAPIKeyParams.  # noqa: E501


        :return: The scope_names of this BTAPIKeyParams.  # noqa: E501
        :rtype: list[str]
        """
        return self._scope_names

    @scope_names.setter
    def scope_names(self, scope_names):
        """Sets the scope_names of this BTAPIKeyParams.


        :param scope_names: The scope_names of this BTAPIKeyParams.  # noqa: E501
        :type: list[str]
        """

        self._scope_names = scope_names

    @property
    def company_id(self):
        """Gets the company_id of this BTAPIKeyParams.  # noqa: E501


        :return: The company_id of this BTAPIKeyParams.  # noqa: E501
        :rtype: str
        """
        return self._company_id

    @company_id.setter
    def company_id(self, company_id):
        """Sets the company_id of this BTAPIKeyParams.


        :param company_id: The company_id of this BTAPIKeyParams.  # noqa: E501
        :type: str
        """

        self._company_id = company_id

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
        if not isinstance(other, BTAPIKeyParams):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
