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


class BTSubstituteApproverParams(object):
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
        'enabled': 'bool',
        'company_id': 'str',
        'identity': 'BTIdentityParams'
    }

    attribute_map = {
        'enabled': 'enabled',
        'company_id': 'companyId',
        'identity': 'identity'
    }

    def __init__(self, enabled=None, company_id=None, identity=None):  # noqa: E501
        """BTSubstituteApproverParams - a model defined in OpenAPI"""  # noqa: E501

        self._enabled = None
        self._company_id = None
        self._identity = None
        self.discriminator = None

        if enabled is not None:
            self.enabled = enabled
        if company_id is not None:
            self.company_id = company_id
        if identity is not None:
            self.identity = identity

    @property
    def enabled(self):
        """Gets the enabled of this BTSubstituteApproverParams.  # noqa: E501


        :return: The enabled of this BTSubstituteApproverParams.  # noqa: E501
        :rtype: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """Sets the enabled of this BTSubstituteApproverParams.


        :param enabled: The enabled of this BTSubstituteApproverParams.  # noqa: E501
        :type: bool
        """

        self._enabled = enabled

    @property
    def company_id(self):
        """Gets the company_id of this BTSubstituteApproverParams.  # noqa: E501


        :return: The company_id of this BTSubstituteApproverParams.  # noqa: E501
        :rtype: str
        """
        return self._company_id

    @company_id.setter
    def company_id(self, company_id):
        """Sets the company_id of this BTSubstituteApproverParams.


        :param company_id: The company_id of this BTSubstituteApproverParams.  # noqa: E501
        :type: str
        """

        self._company_id = company_id

    @property
    def identity(self):
        """Gets the identity of this BTSubstituteApproverParams.  # noqa: E501


        :return: The identity of this BTSubstituteApproverParams.  # noqa: E501
        :rtype: BTIdentityParams
        """
        return self._identity

    @identity.setter
    def identity(self, identity):
        """Sets the identity of this BTSubstituteApproverParams.


        :param identity: The identity of this BTSubstituteApproverParams.  # noqa: E501
        :type: BTIdentityParams
        """

        self._identity = identity

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
        if not isinstance(other, BTSubstituteApproverParams):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
