# coding: utf-8

"""
    Pulp 3 API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: v3
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class GalaxyCollection(object):
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
        'name': 'str',
        'namespace': 'str',
        'version': 'str',
        'href': 'str',
        'versions_url': 'str'
    }

    attribute_map = {
        'name': 'name',
        'namespace': 'namespace',
        'version': 'version',
        'href': 'href',
        'versions_url': 'versions_url'
    }

    def __init__(self, name=None, namespace=None, version=None, href=None, versions_url=None):  # noqa: E501
        """GalaxyCollection - a model defined in OpenAPI"""  # noqa: E501

        self._name = None
        self._namespace = None
        self._version = None
        self._href = None
        self._versions_url = None
        self.discriminator = None

        self.name = name
        self.namespace = namespace
        self.version = version
        if href is not None:
            self.href = href
        if versions_url is not None:
            self.versions_url = versions_url

    @property
    def name(self):
        """Gets the name of this GalaxyCollection.  # noqa: E501


        :return: The name of this GalaxyCollection.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this GalaxyCollection.


        :param name: The name of this GalaxyCollection.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501
        if name is not None and len(name) < 1:
            raise ValueError("Invalid value for `name`, length must be greater than or equal to `1`")  # noqa: E501

        self._name = name

    @property
    def namespace(self):
        """Gets the namespace of this GalaxyCollection.  # noqa: E501


        :return: The namespace of this GalaxyCollection.  # noqa: E501
        :rtype: str
        """
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        """Sets the namespace of this GalaxyCollection.


        :param namespace: The namespace of this GalaxyCollection.  # noqa: E501
        :type: str
        """
        if namespace is None:
            raise ValueError("Invalid value for `namespace`, must not be `None`")  # noqa: E501
        if namespace is not None and len(namespace) < 1:
            raise ValueError("Invalid value for `namespace`, length must be greater than or equal to `1`")  # noqa: E501

        self._namespace = namespace

    @property
    def version(self):
        """Gets the version of this GalaxyCollection.  # noqa: E501


        :return: The version of this GalaxyCollection.  # noqa: E501
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this GalaxyCollection.


        :param version: The version of this GalaxyCollection.  # noqa: E501
        :type: str
        """
        if version is None:
            raise ValueError("Invalid value for `version`, must not be `None`")  # noqa: E501
        if version is not None and len(version) < 1:
            raise ValueError("Invalid value for `version`, length must be greater than or equal to `1`")  # noqa: E501

        self._version = version

    @property
    def href(self):
        """Gets the href of this GalaxyCollection.  # noqa: E501


        :return: The href of this GalaxyCollection.  # noqa: E501
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this GalaxyCollection.


        :param href: The href of this GalaxyCollection.  # noqa: E501
        :type: str
        """

        self._href = href

    @property
    def versions_url(self):
        """Gets the versions_url of this GalaxyCollection.  # noqa: E501


        :return: The versions_url of this GalaxyCollection.  # noqa: E501
        :rtype: str
        """
        return self._versions_url

    @versions_url.setter
    def versions_url(self, versions_url):
        """Sets the versions_url of this GalaxyCollection.


        :param versions_url: The versions_url of this GalaxyCollection.  # noqa: E501
        :type: str
        """

        self._versions_url = versions_url

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
        if not isinstance(other, GalaxyCollection):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
