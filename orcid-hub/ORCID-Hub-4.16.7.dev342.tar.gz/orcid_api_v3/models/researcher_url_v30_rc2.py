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
from orcid_api_v3.models.last_modified_date_v30_rc2 import LastModifiedDateV30Rc2  # noqa: F401,E501
from orcid_api_v3.models.source_v30_rc2 import SourceV30Rc2  # noqa: F401,E501
from orcid_api_v3.models.url_v30_rc2 import UrlV30Rc2  # noqa: F401,E501


class ResearcherUrlV30Rc2(object):
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
        'url_name': 'str',
        'url': 'UrlV30Rc2',
        'visibility': 'str',
        'path': 'str',
        'put_code': 'int',
        'display_index': 'int'
    }

    attribute_map = {
        'created_date': 'created-date',
        'last_modified_date': 'last-modified-date',
        'source': 'source',
        'url_name': 'url-name',
        'url': 'url',
        'visibility': 'visibility',
        'path': 'path',
        'put_code': 'put-code',
        'display_index': 'display-index'
    }

    def __init__(self, created_date=None, last_modified_date=None, source=None, url_name=None, url=None, visibility=None, path=None, put_code=None, display_index=None):  # noqa: E501
        """ResearcherUrlV30Rc2 - a model defined in Swagger"""  # noqa: E501
        self._created_date = None
        self._last_modified_date = None
        self._source = None
        self._url_name = None
        self._url = None
        self._visibility = None
        self._path = None
        self._put_code = None
        self._display_index = None
        self.discriminator = None
        if created_date is not None:
            self.created_date = created_date
        if last_modified_date is not None:
            self.last_modified_date = last_modified_date
        if source is not None:
            self.source = source
        if url_name is not None:
            self.url_name = url_name
        if url is not None:
            self.url = url
        if visibility is not None:
            self.visibility = visibility
        if path is not None:
            self.path = path
        if put_code is not None:
            self.put_code = put_code
        if display_index is not None:
            self.display_index = display_index

    @property
    def created_date(self):
        """Gets the created_date of this ResearcherUrlV30Rc2.  # noqa: E501


        :return: The created_date of this ResearcherUrlV30Rc2.  # noqa: E501
        :rtype: CreatedDateV30Rc2
        """
        return self._created_date

    @created_date.setter
    def created_date(self, created_date):
        """Sets the created_date of this ResearcherUrlV30Rc2.


        :param created_date: The created_date of this ResearcherUrlV30Rc2.  # noqa: E501
        :type: CreatedDateV30Rc2
        """

        self._created_date = created_date

    @property
    def last_modified_date(self):
        """Gets the last_modified_date of this ResearcherUrlV30Rc2.  # noqa: E501


        :return: The last_modified_date of this ResearcherUrlV30Rc2.  # noqa: E501
        :rtype: LastModifiedDateV30Rc2
        """
        return self._last_modified_date

    @last_modified_date.setter
    def last_modified_date(self, last_modified_date):
        """Sets the last_modified_date of this ResearcherUrlV30Rc2.


        :param last_modified_date: The last_modified_date of this ResearcherUrlV30Rc2.  # noqa: E501
        :type: LastModifiedDateV30Rc2
        """

        self._last_modified_date = last_modified_date

    @property
    def source(self):
        """Gets the source of this ResearcherUrlV30Rc2.  # noqa: E501


        :return: The source of this ResearcherUrlV30Rc2.  # noqa: E501
        :rtype: SourceV30Rc2
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this ResearcherUrlV30Rc2.


        :param source: The source of this ResearcherUrlV30Rc2.  # noqa: E501
        :type: SourceV30Rc2
        """

        self._source = source

    @property
    def url_name(self):
        """Gets the url_name of this ResearcherUrlV30Rc2.  # noqa: E501


        :return: The url_name of this ResearcherUrlV30Rc2.  # noqa: E501
        :rtype: str
        """
        return self._url_name

    @url_name.setter
    def url_name(self, url_name):
        """Sets the url_name of this ResearcherUrlV30Rc2.


        :param url_name: The url_name of this ResearcherUrlV30Rc2.  # noqa: E501
        :type: str
        """

        self._url_name = url_name

    @property
    def url(self):
        """Gets the url of this ResearcherUrlV30Rc2.  # noqa: E501


        :return: The url of this ResearcherUrlV30Rc2.  # noqa: E501
        :rtype: UrlV30Rc2
        """
        return self._url

    @url.setter
    def url(self, url):
        """Sets the url of this ResearcherUrlV30Rc2.


        :param url: The url of this ResearcherUrlV30Rc2.  # noqa: E501
        :type: UrlV30Rc2
        """

        self._url = url

    @property
    def visibility(self):
        """Gets the visibility of this ResearcherUrlV30Rc2.  # noqa: E501


        :return: The visibility of this ResearcherUrlV30Rc2.  # noqa: E501
        :rtype: str
        """
        return self._visibility

    @visibility.setter
    def visibility(self, visibility):
        """Sets the visibility of this ResearcherUrlV30Rc2.


        :param visibility: The visibility of this ResearcherUrlV30Rc2.  # noqa: E501
        :type: str
        """
        allowed_values = ["LIMITED", "REGISTERED_ONLY", "PUBLIC", "PRIVATE"]  # noqa: E501
        if visibility not in allowed_values:
            raise ValueError(
                "Invalid value for `visibility` ({0}), must be one of {1}"  # noqa: E501
                .format(visibility, allowed_values)
            )

        self._visibility = visibility

    @property
    def path(self):
        """Gets the path of this ResearcherUrlV30Rc2.  # noqa: E501


        :return: The path of this ResearcherUrlV30Rc2.  # noqa: E501
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """Sets the path of this ResearcherUrlV30Rc2.


        :param path: The path of this ResearcherUrlV30Rc2.  # noqa: E501
        :type: str
        """

        self._path = path

    @property
    def put_code(self):
        """Gets the put_code of this ResearcherUrlV30Rc2.  # noqa: E501


        :return: The put_code of this ResearcherUrlV30Rc2.  # noqa: E501
        :rtype: int
        """
        return self._put_code

    @put_code.setter
    def put_code(self, put_code):
        """Sets the put_code of this ResearcherUrlV30Rc2.


        :param put_code: The put_code of this ResearcherUrlV30Rc2.  # noqa: E501
        :type: int
        """

        self._put_code = put_code

    @property
    def display_index(self):
        """Gets the display_index of this ResearcherUrlV30Rc2.  # noqa: E501


        :return: The display_index of this ResearcherUrlV30Rc2.  # noqa: E501
        :rtype: int
        """
        return self._display_index

    @display_index.setter
    def display_index(self, display_index):
        """Sets the display_index of this ResearcherUrlV30Rc2.


        :param display_index: The display_index of this ResearcherUrlV30Rc2.  # noqa: E501
        :type: int
        """

        self._display_index = display_index

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
        if issubclass(ResearcherUrlV30Rc2, dict):
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
        if not isinstance(other, ResearcherUrlV30Rc2):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
