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


class ContributorAttributesV30Rc1(object):
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
        'contributor_sequence': 'str',
        'contributor_role': 'str'
    }

    attribute_map = {
        'contributor_sequence': 'contributor-sequence',
        'contributor_role': 'contributor-role'
    }

    def __init__(self, contributor_sequence=None, contributor_role=None):  # noqa: E501
        """ContributorAttributesV30Rc1 - a model defined in Swagger"""  # noqa: E501
        self._contributor_sequence = None
        self._contributor_role = None
        self.discriminator = None
        self.contributor_sequence = contributor_sequence
        self.contributor_role = contributor_role

    @property
    def contributor_sequence(self):
        """Gets the contributor_sequence of this ContributorAttributesV30Rc1.  # noqa: E501


        :return: The contributor_sequence of this ContributorAttributesV30Rc1.  # noqa: E501
        :rtype: str
        """
        return self._contributor_sequence

    @contributor_sequence.setter
    def contributor_sequence(self, contributor_sequence):
        """Sets the contributor_sequence of this ContributorAttributesV30Rc1.


        :param contributor_sequence: The contributor_sequence of this ContributorAttributesV30Rc1.  # noqa: E501
        :type: str
        """
        if contributor_sequence is None:
            raise ValueError("Invalid value for `contributor_sequence`, must not be `None`")  # noqa: E501
        allowed_values = ["FIRST", "ADDITIONAL"]  # noqa: E501
        if contributor_sequence not in allowed_values:
            raise ValueError(
                "Invalid value for `contributor_sequence` ({0}), must be one of {1}"  # noqa: E501
                .format(contributor_sequence, allowed_values)
            )

        self._contributor_sequence = contributor_sequence

    @property
    def contributor_role(self):
        """Gets the contributor_role of this ContributorAttributesV30Rc1.  # noqa: E501


        :return: The contributor_role of this ContributorAttributesV30Rc1.  # noqa: E501
        :rtype: str
        """
        return self._contributor_role

    @contributor_role.setter
    def contributor_role(self, contributor_role):
        """Sets the contributor_role of this ContributorAttributesV30Rc1.


        :param contributor_role: The contributor_role of this ContributorAttributesV30Rc1.  # noqa: E501
        :type: str
        """
        if contributor_role is None:
            raise ValueError("Invalid value for `contributor_role`, must not be `None`")  # noqa: E501
        allowed_values = ["AUTHOR", "ASSIGNEE", "EDITOR", "CHAIR_OR_TRANSLATOR", "CO_INVESTIGATOR", "CO_INVENTOR", "GRADUATE_STUDENT", "OTHER_INVENTOR", "PRINCIPAL_INVESTIGATOR", "POSTDOCTORAL_RESEARCHER", "SUPPORT_STAFF"]  # noqa: E501
        if contributor_role not in allowed_values:
            raise ValueError(
                "Invalid value for `contributor_role` ({0}), must be one of {1}"  # noqa: E501
                .format(contributor_role, allowed_values)
            )

        self._contributor_role = contributor_role

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
        if issubclass(ContributorAttributesV30Rc1, dict):
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
        if not isinstance(other, ContributorAttributesV30Rc1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
