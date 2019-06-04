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


class DisambiguatedOrganizationV20(object):
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
        'disambiguated_organization_identifier': 'str',
        'disambiguation_source': 'str'
    }

    attribute_map = {
        'disambiguated_organization_identifier': 'disambiguated-organization-identifier',
        'disambiguation_source': 'disambiguation-source'
    }

    def __init__(self, disambiguated_organization_identifier=None, disambiguation_source=None):  # noqa: E501
        """DisambiguatedOrganizationV20 - a model defined in Swagger"""  # noqa: E501
        self._disambiguated_organization_identifier = None
        self._disambiguation_source = None
        self.discriminator = None
        self.disambiguated_organization_identifier = disambiguated_organization_identifier
        self.disambiguation_source = disambiguation_source

    @property
    def disambiguated_organization_identifier(self):
        """Gets the disambiguated_organization_identifier of this DisambiguatedOrganizationV20.  # noqa: E501


        :return: The disambiguated_organization_identifier of this DisambiguatedOrganizationV20.  # noqa: E501
        :rtype: str
        """
        return self._disambiguated_organization_identifier

    @disambiguated_organization_identifier.setter
    def disambiguated_organization_identifier(self, disambiguated_organization_identifier):
        """Sets the disambiguated_organization_identifier of this DisambiguatedOrganizationV20.


        :param disambiguated_organization_identifier: The disambiguated_organization_identifier of this DisambiguatedOrganizationV20.  # noqa: E501
        :type: str
        """
        if disambiguated_organization_identifier is None:
            raise ValueError("Invalid value for `disambiguated_organization_identifier`, must not be `None`")  # noqa: E501

        self._disambiguated_organization_identifier = disambiguated_organization_identifier

    @property
    def disambiguation_source(self):
        """Gets the disambiguation_source of this DisambiguatedOrganizationV20.  # noqa: E501


        :return: The disambiguation_source of this DisambiguatedOrganizationV20.  # noqa: E501
        :rtype: str
        """
        return self._disambiguation_source

    @disambiguation_source.setter
    def disambiguation_source(self, disambiguation_source):
        """Sets the disambiguation_source of this DisambiguatedOrganizationV20.


        :param disambiguation_source: The disambiguation_source of this DisambiguatedOrganizationV20.  # noqa: E501
        :type: str
        """
        if disambiguation_source is None:
            raise ValueError("Invalid value for `disambiguation_source`, must not be `None`")  # noqa: E501

        self._disambiguation_source = disambiguation_source

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
        if issubclass(DisambiguatedOrganizationV20, dict):
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
        if not isinstance(other, DisambiguatedOrganizationV20):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
