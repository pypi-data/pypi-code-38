# coding: utf-8

"""
    ORCID Member

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: Latest
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class PeerReviewSummary(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, created_date=None, last_modified_date=None, source=None, reviewer_role=None, external_ids=None, review_url=None, review_type=None, completion_date=None, review_group_id=None, convening_organization=None, visibility=None, put_code=None, path=None, display_index=None):
        """
        PeerReviewSummary - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'created_date': 'object',
            'last_modified_date': 'object',
            'source': 'object',
            'reviewer_role': 'object',
            'external_ids': 'object',
            'review_url': 'object',
            'review_type': 'object',
            'completion_date': 'object',
            'review_group_id': 'str',
            'convening_organization': 'object',
            'visibility': 'str',
            'put_code': 'int',
            'path': 'str',
            'display_index': 'str'
        }

        self.attribute_map = {
            'created_date': 'created-date',
            'last_modified_date': 'last-modified-date',
            'source': 'source',
            'reviewer_role': 'reviewer-role',
            'external_ids': 'external-ids',
            'review_url': 'review-url',
            'review_type': 'review-type',
            'completion_date': 'completion-date',
            'review_group_id': 'review-group-id',
            'convening_organization': 'convening-organization',
            'visibility': 'visibility',
            'put_code': 'put-code',
            'path': 'path',
            'display_index': 'display-index'
        }

        self._created_date = created_date
        self._last_modified_date = last_modified_date
        self._source = source
        self._reviewer_role = reviewer_role
        self._external_ids = external_ids
        self._review_url = review_url
        self._review_type = review_type
        self._completion_date = completion_date
        self._review_group_id = review_group_id
        self._convening_organization = convening_organization
        self._visibility = visibility
        self._put_code = put_code
        self._path = path
        self._display_index = display_index

    @property
    def created_date(self):
        """
        Gets the created_date of this PeerReviewSummary.

        :return: The created_date of this PeerReviewSummary.
        :rtype: object
        """
        return self._created_date

    @created_date.setter
    def created_date(self, created_date):
        """
        Sets the created_date of this PeerReviewSummary.

        :param created_date: The created_date of this PeerReviewSummary.
        :type: object
        """

        self._created_date = created_date

    @property
    def last_modified_date(self):
        """
        Gets the last_modified_date of this PeerReviewSummary.

        :return: The last_modified_date of this PeerReviewSummary.
        :rtype: object
        """
        return self._last_modified_date

    @last_modified_date.setter
    def last_modified_date(self, last_modified_date):
        """
        Sets the last_modified_date of this PeerReviewSummary.

        :param last_modified_date: The last_modified_date of this PeerReviewSummary.
        :type: object
        """

        self._last_modified_date = last_modified_date

    @property
    def source(self):
        """
        Gets the source of this PeerReviewSummary.

        :return: The source of this PeerReviewSummary.
        :rtype: object
        """
        return self._source

    @source.setter
    def source(self, source):
        """
        Sets the source of this PeerReviewSummary.

        :param source: The source of this PeerReviewSummary.
        :type: object
        """

        self._source = source

    @property
    def reviewer_role(self):
        """
        Gets the reviewer_role of this PeerReviewSummary.

        :return: The reviewer_role of this PeerReviewSummary.
        :rtype: object
        """
        return self._reviewer_role

    @reviewer_role.setter
    def reviewer_role(self, reviewer_role):
        """
        Sets the reviewer_role of this PeerReviewSummary.

        :param reviewer_role: The reviewer_role of this PeerReviewSummary.
        :type: object
        """

        self._reviewer_role = reviewer_role

    @property
    def external_ids(self):
        """
        Gets the external_ids of this PeerReviewSummary.

        :return: The external_ids of this PeerReviewSummary.
        :rtype: object
        """
        return self._external_ids

    @external_ids.setter
    def external_ids(self, external_ids):
        """
        Sets the external_ids of this PeerReviewSummary.

        :param external_ids: The external_ids of this PeerReviewSummary.
        :type: object
        """

        self._external_ids = external_ids

    @property
    def review_url(self):
        """
        Gets the review_url of this PeerReviewSummary.

        :return: The review_url of this PeerReviewSummary.
        :rtype: object
        """
        return self._review_url

    @review_url.setter
    def review_url(self, review_url):
        """
        Sets the review_url of this PeerReviewSummary.

        :param review_url: The review_url of this PeerReviewSummary.
        :type: object
        """

        self._review_url = review_url

    @property
    def review_type(self):
        """
        Gets the review_type of this PeerReviewSummary.

        :return: The review_type of this PeerReviewSummary.
        :rtype: object
        """
        return self._review_type

    @review_type.setter
    def review_type(self, review_type):
        """
        Sets the review_type of this PeerReviewSummary.

        :param review_type: The review_type of this PeerReviewSummary.
        :type: object
        """

        self._review_type = review_type

    @property
    def completion_date(self):
        """
        Gets the completion_date of this PeerReviewSummary.

        :return: The completion_date of this PeerReviewSummary.
        :rtype: object
        """
        return self._completion_date

    @completion_date.setter
    def completion_date(self, completion_date):
        """
        Sets the completion_date of this PeerReviewSummary.

        :param completion_date: The completion_date of this PeerReviewSummary.
        :type: object
        """

        self._completion_date = completion_date

    @property
    def review_group_id(self):
        """
        Gets the review_group_id of this PeerReviewSummary.

        :return: The review_group_id of this PeerReviewSummary.
        :rtype: str
        """
        return self._review_group_id

    @review_group_id.setter
    def review_group_id(self, review_group_id):
        """
        Sets the review_group_id of this PeerReviewSummary.

        :param review_group_id: The review_group_id of this PeerReviewSummary.
        :type: str
        """
        if review_group_id is None:
            raise ValueError("Invalid value for `review_group_id`, must not be `None`")

        self._review_group_id = review_group_id

    @property
    def convening_organization(self):
        """
        Gets the convening_organization of this PeerReviewSummary.

        :return: The convening_organization of this PeerReviewSummary.
        :rtype: object
        """
        return self._convening_organization

    @convening_organization.setter
    def convening_organization(self, convening_organization):
        """
        Sets the convening_organization of this PeerReviewSummary.

        :param convening_organization: The convening_organization of this PeerReviewSummary.
        :type: object
        """
        if convening_organization is None:
            raise ValueError("Invalid value for `convening_organization`, must not be `None`")

        self._convening_organization = convening_organization

    @property
    def visibility(self):
        """
        Gets the visibility of this PeerReviewSummary.

        :return: The visibility of this PeerReviewSummary.
        :rtype: str
        """
        return self._visibility

    @visibility.setter
    def visibility(self, visibility):
        """
        Sets the visibility of this PeerReviewSummary.

        :param visibility: The visibility of this PeerReviewSummary.
        :type: str
        """
        allowed_values = ["LIMITED", "REGISTERED_ONLY", "PUBLIC", "PRIVATE"]
        if visibility not in allowed_values:
            raise ValueError(
                "Invalid value for `visibility` ({0}), must be one of {1}"
                .format(visibility, allowed_values)
            )

        self._visibility = visibility

    @property
    def put_code(self):
        """
        Gets the put_code of this PeerReviewSummary.

        :return: The put_code of this PeerReviewSummary.
        :rtype: int
        """
        return self._put_code

    @put_code.setter
    def put_code(self, put_code):
        """
        Sets the put_code of this PeerReviewSummary.

        :param put_code: The put_code of this PeerReviewSummary.
        :type: int
        """

        self._put_code = put_code

    @property
    def path(self):
        """
        Gets the path of this PeerReviewSummary.

        :return: The path of this PeerReviewSummary.
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """
        Sets the path of this PeerReviewSummary.

        :param path: The path of this PeerReviewSummary.
        :type: str
        """

        self._path = path

    @property
    def display_index(self):
        """
        Gets the display_index of this PeerReviewSummary.

        :return: The display_index of this PeerReviewSummary.
        :rtype: str
        """
        return self._display_index

    @display_index.setter
    def display_index(self, display_index):
        """
        Sets the display_index of this PeerReviewSummary.

        :param display_index: The display_index of this PeerReviewSummary.
        :type: str
        """

        self._display_index = display_index

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
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
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, PeerReviewSummary):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
