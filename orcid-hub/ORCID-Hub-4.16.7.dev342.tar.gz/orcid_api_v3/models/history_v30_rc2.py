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
from orcid_api_v3.models.completion_date_v30_rc2 import CompletionDateV30Rc2  # noqa: F401,E501
from orcid_api_v3.models.deactivation_date_v30_rc2 import DeactivationDateV30Rc2  # noqa: F401,E501
from orcid_api_v3.models.last_modified_date_v30_rc2 import LastModifiedDateV30Rc2  # noqa: F401,E501
from orcid_api_v3.models.source_v30_rc2 import SourceV30Rc2  # noqa: F401,E501
from orcid_api_v3.models.submission_date_v30_rc2 import SubmissionDateV30Rc2  # noqa: F401,E501


class HistoryV30Rc2(object):
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
        'creation_method': 'str',
        'completion_date': 'CompletionDateV30Rc2',
        'submission_date': 'SubmissionDateV30Rc2',
        'last_modified_date': 'LastModifiedDateV30Rc2',
        'claimed': 'bool',
        'source': 'SourceV30Rc2',
        'deactivation_date': 'DeactivationDateV30Rc2',
        'verified_email': 'bool',
        'verified_primary_email': 'bool'
    }

    attribute_map = {
        'creation_method': 'creation-method',
        'completion_date': 'completion-date',
        'submission_date': 'submission-date',
        'last_modified_date': 'last-modified-date',
        'claimed': 'claimed',
        'source': 'source',
        'deactivation_date': 'deactivation-date',
        'verified_email': 'verified-email',
        'verified_primary_email': 'verified-primary-email'
    }

    def __init__(self, creation_method=None, completion_date=None, submission_date=None, last_modified_date=None, claimed=None, source=None, deactivation_date=None, verified_email=None, verified_primary_email=None):  # noqa: E501
        """HistoryV30Rc2 - a model defined in Swagger"""  # noqa: E501
        self._creation_method = None
        self._completion_date = None
        self._submission_date = None
        self._last_modified_date = None
        self._claimed = None
        self._source = None
        self._deactivation_date = None
        self._verified_email = None
        self._verified_primary_email = None
        self.discriminator = None
        if creation_method is not None:
            self.creation_method = creation_method
        if completion_date is not None:
            self.completion_date = completion_date
        if submission_date is not None:
            self.submission_date = submission_date
        if last_modified_date is not None:
            self.last_modified_date = last_modified_date
        if claimed is not None:
            self.claimed = claimed
        if source is not None:
            self.source = source
        if deactivation_date is not None:
            self.deactivation_date = deactivation_date
        if verified_email is not None:
            self.verified_email = verified_email
        if verified_primary_email is not None:
            self.verified_primary_email = verified_primary_email

    @property
    def creation_method(self):
        """Gets the creation_method of this HistoryV30Rc2.  # noqa: E501


        :return: The creation_method of this HistoryV30Rc2.  # noqa: E501
        :rtype: str
        """
        return self._creation_method

    @creation_method.setter
    def creation_method(self, creation_method):
        """Sets the creation_method of this HistoryV30Rc2.


        :param creation_method: The creation_method of this HistoryV30Rc2.  # noqa: E501
        :type: str
        """
        allowed_values = ["API", "DIRECT", "MEMBER_REFERRED", "WEBSITE", "INTEGRATION_TEST"]  # noqa: E501
        if creation_method not in allowed_values:
            raise ValueError(
                "Invalid value for `creation_method` ({0}), must be one of {1}"  # noqa: E501
                .format(creation_method, allowed_values)
            )

        self._creation_method = creation_method

    @property
    def completion_date(self):
        """Gets the completion_date of this HistoryV30Rc2.  # noqa: E501


        :return: The completion_date of this HistoryV30Rc2.  # noqa: E501
        :rtype: CompletionDateV30Rc2
        """
        return self._completion_date

    @completion_date.setter
    def completion_date(self, completion_date):
        """Sets the completion_date of this HistoryV30Rc2.


        :param completion_date: The completion_date of this HistoryV30Rc2.  # noqa: E501
        :type: CompletionDateV30Rc2
        """

        self._completion_date = completion_date

    @property
    def submission_date(self):
        """Gets the submission_date of this HistoryV30Rc2.  # noqa: E501


        :return: The submission_date of this HistoryV30Rc2.  # noqa: E501
        :rtype: SubmissionDateV30Rc2
        """
        return self._submission_date

    @submission_date.setter
    def submission_date(self, submission_date):
        """Sets the submission_date of this HistoryV30Rc2.


        :param submission_date: The submission_date of this HistoryV30Rc2.  # noqa: E501
        :type: SubmissionDateV30Rc2
        """

        self._submission_date = submission_date

    @property
    def last_modified_date(self):
        """Gets the last_modified_date of this HistoryV30Rc2.  # noqa: E501


        :return: The last_modified_date of this HistoryV30Rc2.  # noqa: E501
        :rtype: LastModifiedDateV30Rc2
        """
        return self._last_modified_date

    @last_modified_date.setter
    def last_modified_date(self, last_modified_date):
        """Sets the last_modified_date of this HistoryV30Rc2.


        :param last_modified_date: The last_modified_date of this HistoryV30Rc2.  # noqa: E501
        :type: LastModifiedDateV30Rc2
        """

        self._last_modified_date = last_modified_date

    @property
    def claimed(self):
        """Gets the claimed of this HistoryV30Rc2.  # noqa: E501


        :return: The claimed of this HistoryV30Rc2.  # noqa: E501
        :rtype: bool
        """
        return self._claimed

    @claimed.setter
    def claimed(self, claimed):
        """Sets the claimed of this HistoryV30Rc2.


        :param claimed: The claimed of this HistoryV30Rc2.  # noqa: E501
        :type: bool
        """

        self._claimed = claimed

    @property
    def source(self):
        """Gets the source of this HistoryV30Rc2.  # noqa: E501


        :return: The source of this HistoryV30Rc2.  # noqa: E501
        :rtype: SourceV30Rc2
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this HistoryV30Rc2.


        :param source: The source of this HistoryV30Rc2.  # noqa: E501
        :type: SourceV30Rc2
        """

        self._source = source

    @property
    def deactivation_date(self):
        """Gets the deactivation_date of this HistoryV30Rc2.  # noqa: E501


        :return: The deactivation_date of this HistoryV30Rc2.  # noqa: E501
        :rtype: DeactivationDateV30Rc2
        """
        return self._deactivation_date

    @deactivation_date.setter
    def deactivation_date(self, deactivation_date):
        """Sets the deactivation_date of this HistoryV30Rc2.


        :param deactivation_date: The deactivation_date of this HistoryV30Rc2.  # noqa: E501
        :type: DeactivationDateV30Rc2
        """

        self._deactivation_date = deactivation_date

    @property
    def verified_email(self):
        """Gets the verified_email of this HistoryV30Rc2.  # noqa: E501


        :return: The verified_email of this HistoryV30Rc2.  # noqa: E501
        :rtype: bool
        """
        return self._verified_email

    @verified_email.setter
    def verified_email(self, verified_email):
        """Sets the verified_email of this HistoryV30Rc2.


        :param verified_email: The verified_email of this HistoryV30Rc2.  # noqa: E501
        :type: bool
        """

        self._verified_email = verified_email

    @property
    def verified_primary_email(self):
        """Gets the verified_primary_email of this HistoryV30Rc2.  # noqa: E501


        :return: The verified_primary_email of this HistoryV30Rc2.  # noqa: E501
        :rtype: bool
        """
        return self._verified_primary_email

    @verified_primary_email.setter
    def verified_primary_email(self, verified_primary_email):
        """Sets the verified_primary_email of this HistoryV30Rc2.


        :param verified_primary_email: The verified_primary_email of this HistoryV30Rc2.  # noqa: E501
        :type: bool
        """

        self._verified_primary_email = verified_primary_email

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
        if issubclass(HistoryV30Rc2, dict):
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
        if not isinstance(other, HistoryV30Rc2):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
