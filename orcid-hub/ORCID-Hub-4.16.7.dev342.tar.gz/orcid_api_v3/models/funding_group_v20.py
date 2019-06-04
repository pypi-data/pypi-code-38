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
from orcid_api_v3.models.external_i_ds_v20 import ExternalIDsV20  # noqa: F401,E501
from orcid_api_v3.models.funding_summary_v20 import FundingSummaryV20  # noqa: F401,E501
from orcid_api_v3.models.last_modified_date_v20 import LastModifiedDateV20  # noqa: F401,E501


class FundingGroupV20(object):
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
        'last_modified_date': 'LastModifiedDateV20',
        'external_ids': 'ExternalIDsV20',
        'funding_summary': 'list[FundingSummaryV20]'
    }

    attribute_map = {
        'last_modified_date': 'last-modified-date',
        'external_ids': 'external-ids',
        'funding_summary': 'funding-summary'
    }

    def __init__(self, last_modified_date=None, external_ids=None, funding_summary=None):  # noqa: E501
        """FundingGroupV20 - a model defined in Swagger"""  # noqa: E501
        self._last_modified_date = None
        self._external_ids = None
        self._funding_summary = None
        self.discriminator = None
        if last_modified_date is not None:
            self.last_modified_date = last_modified_date
        if external_ids is not None:
            self.external_ids = external_ids
        if funding_summary is not None:
            self.funding_summary = funding_summary

    @property
    def last_modified_date(self):
        """Gets the last_modified_date of this FundingGroupV20.  # noqa: E501


        :return: The last_modified_date of this FundingGroupV20.  # noqa: E501
        :rtype: LastModifiedDateV20
        """
        return self._last_modified_date

    @last_modified_date.setter
    def last_modified_date(self, last_modified_date):
        """Sets the last_modified_date of this FundingGroupV20.


        :param last_modified_date: The last_modified_date of this FundingGroupV20.  # noqa: E501
        :type: LastModifiedDateV20
        """

        self._last_modified_date = last_modified_date

    @property
    def external_ids(self):
        """Gets the external_ids of this FundingGroupV20.  # noqa: E501


        :return: The external_ids of this FundingGroupV20.  # noqa: E501
        :rtype: ExternalIDsV20
        """
        return self._external_ids

    @external_ids.setter
    def external_ids(self, external_ids):
        """Sets the external_ids of this FundingGroupV20.


        :param external_ids: The external_ids of this FundingGroupV20.  # noqa: E501
        :type: ExternalIDsV20
        """

        self._external_ids = external_ids

    @property
    def funding_summary(self):
        """Gets the funding_summary of this FundingGroupV20.  # noqa: E501


        :return: The funding_summary of this FundingGroupV20.  # noqa: E501
        :rtype: list[FundingSummaryV20]
        """
        return self._funding_summary

    @funding_summary.setter
    def funding_summary(self, funding_summary):
        """Sets the funding_summary of this FundingGroupV20.


        :param funding_summary: The funding_summary of this FundingGroupV20.  # noqa: E501
        :type: list[FundingSummaryV20]
        """

        self._funding_summary = funding_summary

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
        if issubclass(FundingGroupV20, dict):
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
        if not isinstance(other, FundingGroupV20):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
