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
from orcid_api_v3.models.created_date_v30_rc2 import CreatedDateV30Rc2  # noqa: F401,E501
from orcid_api_v3.models.external_i_ds_v30_rc2 import ExternalIDsV30Rc2  # noqa: F401,E501
from orcid_api_v3.models.fuzzy_date_v30_rc2 import FuzzyDateV30Rc2  # noqa: F401,E501
from orcid_api_v3.models.last_modified_date_v30_rc2 import LastModifiedDateV30Rc2  # noqa: F401,E501
from orcid_api_v3.models.organization_v30_rc2 import OrganizationV30Rc2  # noqa: F401,E501
from orcid_api_v3.models.source_v30_rc2 import SourceV30Rc2  # noqa: F401,E501
from orcid_api_v3.models.url_v30_rc2 import UrlV30Rc2  # noqa: F401,E501


class EmploymentV30Rc2(object):
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
        'created_date': 'CreatedDateV30Rc2',
        'last_modified_date': 'LastModifiedDateV30Rc2',
        'source': 'SourceV30Rc2',
        'put_code': 'int',
        'path': 'str',
        'department_name': 'str',
        'role_title': 'str',
        'start_date': 'FuzzyDateV30Rc2',
        'end_date': 'FuzzyDateV30Rc2',
        'organization': 'OrganizationV30Rc2',
        'url': 'UrlV30Rc2',
        'external_ids': 'ExternalIDsV30Rc2',
        'display_index': 'str',
        'visibility': 'str'
    }

    attribute_map = {
        'created_date': 'created-date',
        'last_modified_date': 'last-modified-date',
        'source': 'source',
        'put_code': 'put-code',
        'path': 'path',
        'department_name': 'department-name',
        'role_title': 'role-title',
        'start_date': 'start-date',
        'end_date': 'end-date',
        'organization': 'organization',
        'url': 'url',
        'external_ids': 'external-ids',
        'display_index': 'display-index',
        'visibility': 'visibility'
    }

    def __init__(self, created_date=None, last_modified_date=None, source=None, put_code=None, path=None, department_name=None, role_title=None, start_date=None, end_date=None, organization=None, url=None, external_ids=None, display_index=None, visibility=None):  # noqa: E501
        """EmploymentV30Rc2 - a model defined in Swagger"""  # noqa: E501
        self._created_date = None
        self._last_modified_date = None
        self._source = None
        self._put_code = None
        self._path = None
        self._department_name = None
        self._role_title = None
        self._start_date = None
        self._end_date = None
        self._organization = None
        self._url = None
        self._external_ids = None
        self._display_index = None
        self._visibility = None
        self.discriminator = None
        if created_date is not None:
            self.created_date = created_date
        if last_modified_date is not None:
            self.last_modified_date = last_modified_date
        if source is not None:
            self.source = source
        if put_code is not None:
            self.put_code = put_code
        if path is not None:
            self.path = path
        if department_name is not None:
            self.department_name = department_name
        if role_title is not None:
            self.role_title = role_title
        self.start_date = start_date
        if end_date is not None:
            self.end_date = end_date
        self.organization = organization
        if url is not None:
            self.url = url
        if external_ids is not None:
            self.external_ids = external_ids
        if display_index is not None:
            self.display_index = display_index
        if visibility is not None:
            self.visibility = visibility

    @property
    def created_date(self):
        """Gets the created_date of this EmploymentV30Rc2.  # noqa: E501


        :return: The created_date of this EmploymentV30Rc2.  # noqa: E501
        :rtype: CreatedDateV30Rc2
        """
        return self._created_date

    @created_date.setter
    def created_date(self, created_date):
        """Sets the created_date of this EmploymentV30Rc2.


        :param created_date: The created_date of this EmploymentV30Rc2.  # noqa: E501
        :type: CreatedDateV30Rc2
        """

        self._created_date = created_date

    @property
    def last_modified_date(self):
        """Gets the last_modified_date of this EmploymentV30Rc2.  # noqa: E501


        :return: The last_modified_date of this EmploymentV30Rc2.  # noqa: E501
        :rtype: LastModifiedDateV30Rc2
        """
        return self._last_modified_date

    @last_modified_date.setter
    def last_modified_date(self, last_modified_date):
        """Sets the last_modified_date of this EmploymentV30Rc2.


        :param last_modified_date: The last_modified_date of this EmploymentV30Rc2.  # noqa: E501
        :type: LastModifiedDateV30Rc2
        """

        self._last_modified_date = last_modified_date

    @property
    def source(self):
        """Gets the source of this EmploymentV30Rc2.  # noqa: E501


        :return: The source of this EmploymentV30Rc2.  # noqa: E501
        :rtype: SourceV30Rc2
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this EmploymentV30Rc2.


        :param source: The source of this EmploymentV30Rc2.  # noqa: E501
        :type: SourceV30Rc2
        """

        self._source = source

    @property
    def put_code(self):
        """Gets the put_code of this EmploymentV30Rc2.  # noqa: E501


        :return: The put_code of this EmploymentV30Rc2.  # noqa: E501
        :rtype: int
        """
        return self._put_code

    @put_code.setter
    def put_code(self, put_code):
        """Sets the put_code of this EmploymentV30Rc2.


        :param put_code: The put_code of this EmploymentV30Rc2.  # noqa: E501
        :type: int
        """

        self._put_code = put_code

    @property
    def path(self):
        """Gets the path of this EmploymentV30Rc2.  # noqa: E501


        :return: The path of this EmploymentV30Rc2.  # noqa: E501
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """Sets the path of this EmploymentV30Rc2.


        :param path: The path of this EmploymentV30Rc2.  # noqa: E501
        :type: str
        """

        self._path = path

    @property
    def department_name(self):
        """Gets the department_name of this EmploymentV30Rc2.  # noqa: E501


        :return: The department_name of this EmploymentV30Rc2.  # noqa: E501
        :rtype: str
        """
        return self._department_name

    @department_name.setter
    def department_name(self, department_name):
        """Sets the department_name of this EmploymentV30Rc2.


        :param department_name: The department_name of this EmploymentV30Rc2.  # noqa: E501
        :type: str
        """

        self._department_name = department_name

    @property
    def role_title(self):
        """Gets the role_title of this EmploymentV30Rc2.  # noqa: E501


        :return: The role_title of this EmploymentV30Rc2.  # noqa: E501
        :rtype: str
        """
        return self._role_title

    @role_title.setter
    def role_title(self, role_title):
        """Sets the role_title of this EmploymentV30Rc2.


        :param role_title: The role_title of this EmploymentV30Rc2.  # noqa: E501
        :type: str
        """

        self._role_title = role_title

    @property
    def start_date(self):
        """Gets the start_date of this EmploymentV30Rc2.  # noqa: E501


        :return: The start_date of this EmploymentV30Rc2.  # noqa: E501
        :rtype: FuzzyDateV30Rc2
        """
        return self._start_date

    @start_date.setter
    def start_date(self, start_date):
        """Sets the start_date of this EmploymentV30Rc2.


        :param start_date: The start_date of this EmploymentV30Rc2.  # noqa: E501
        :type: FuzzyDateV30Rc2
        """
        if start_date is None:
            raise ValueError("Invalid value for `start_date`, must not be `None`")  # noqa: E501

        self._start_date = start_date

    @property
    def end_date(self):
        """Gets the end_date of this EmploymentV30Rc2.  # noqa: E501


        :return: The end_date of this EmploymentV30Rc2.  # noqa: E501
        :rtype: FuzzyDateV30Rc2
        """
        return self._end_date

    @end_date.setter
    def end_date(self, end_date):
        """Sets the end_date of this EmploymentV30Rc2.


        :param end_date: The end_date of this EmploymentV30Rc2.  # noqa: E501
        :type: FuzzyDateV30Rc2
        """

        self._end_date = end_date

    @property
    def organization(self):
        """Gets the organization of this EmploymentV30Rc2.  # noqa: E501


        :return: The organization of this EmploymentV30Rc2.  # noqa: E501
        :rtype: OrganizationV30Rc2
        """
        return self._organization

    @organization.setter
    def organization(self, organization):
        """Sets the organization of this EmploymentV30Rc2.


        :param organization: The organization of this EmploymentV30Rc2.  # noqa: E501
        :type: OrganizationV30Rc2
        """
        if organization is None:
            raise ValueError("Invalid value for `organization`, must not be `None`")  # noqa: E501

        self._organization = organization

    @property
    def url(self):
        """Gets the url of this EmploymentV30Rc2.  # noqa: E501


        :return: The url of this EmploymentV30Rc2.  # noqa: E501
        :rtype: UrlV30Rc2
        """
        return self._url

    @url.setter
    def url(self, url):
        """Sets the url of this EmploymentV30Rc2.


        :param url: The url of this EmploymentV30Rc2.  # noqa: E501
        :type: UrlV30Rc2
        """

        self._url = url

    @property
    def external_ids(self):
        """Gets the external_ids of this EmploymentV30Rc2.  # noqa: E501


        :return: The external_ids of this EmploymentV30Rc2.  # noqa: E501
        :rtype: ExternalIDsV30Rc2
        """
        return self._external_ids

    @external_ids.setter
    def external_ids(self, external_ids):
        """Sets the external_ids of this EmploymentV30Rc2.


        :param external_ids: The external_ids of this EmploymentV30Rc2.  # noqa: E501
        :type: ExternalIDsV30Rc2
        """

        self._external_ids = external_ids

    @property
    def display_index(self):
        """Gets the display_index of this EmploymentV30Rc2.  # noqa: E501


        :return: The display_index of this EmploymentV30Rc2.  # noqa: E501
        :rtype: str
        """
        return self._display_index

    @display_index.setter
    def display_index(self, display_index):
        """Sets the display_index of this EmploymentV30Rc2.


        :param display_index: The display_index of this EmploymentV30Rc2.  # noqa: E501
        :type: str
        """

        self._display_index = display_index

    @property
    def visibility(self):
        """Gets the visibility of this EmploymentV30Rc2.  # noqa: E501


        :return: The visibility of this EmploymentV30Rc2.  # noqa: E501
        :rtype: str
        """
        return self._visibility

    @visibility.setter
    def visibility(self, visibility):
        """Sets the visibility of this EmploymentV30Rc2.


        :param visibility: The visibility of this EmploymentV30Rc2.  # noqa: E501
        :type: str
        """
        allowed_values = ["LIMITED", "REGISTERED_ONLY", "PUBLIC", "PRIVATE"]  # noqa: E501
        if visibility not in allowed_values:
            raise ValueError(
                "Invalid value for `visibility` ({0}), must be one of {1}"  # noqa: E501
                .format(visibility, allowed_values)
            )

        self._visibility = visibility

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
        if issubclass(EmploymentV30Rc2, dict):
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
        if not isinstance(other, EmploymentV30Rc2):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
