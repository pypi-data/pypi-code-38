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


class Role(object):
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
        'created': 'datetime',
        'artifact': 'str',
        'href': 'str',
        'type': 'str',
        'version': 'str',
        'name': 'str',
        'namespace': 'str'
    }

    attribute_map = {
        'created': '_created',
        'artifact': '_artifact',
        'href': '_href',
        'type': '_type',
        'version': 'version',
        'name': 'name',
        'namespace': 'namespace'
    }

    def __init__(self, created=None, artifact=None, href=None, type=None, version=None, name=None, namespace=None):  # noqa: E501
        """Role - a model defined in OpenAPI"""  # noqa: E501

        self._created = None
        self._artifact = None
        self._href = None
        self._type = None
        self._version = None
        self._name = None
        self._namespace = None
        self.discriminator = None

        if created is not None:
            self.created = created
        self.artifact = artifact
        if href is not None:
            self.href = href
        if type is not None:
            self.type = type
        self.version = version
        self.name = name
        self.namespace = namespace

    @property
    def created(self):
        """Gets the created of this Role.  # noqa: E501

        Timestamp of creation.  # noqa: E501

        :return: The created of this Role.  # noqa: E501
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """Sets the created of this Role.

        Timestamp of creation.  # noqa: E501

        :param created: The created of this Role.  # noqa: E501
        :type: datetime
        """

        self._created = created

    @property
    def artifact(self):
        """Gets the artifact of this Role.  # noqa: E501

        Artifact file representing the physical content  # noqa: E501

        :return: The artifact of this Role.  # noqa: E501
        :rtype: str
        """
        return self._artifact

    @artifact.setter
    def artifact(self, artifact):
        """Sets the artifact of this Role.

        Artifact file representing the physical content  # noqa: E501

        :param artifact: The artifact of this Role.  # noqa: E501
        :type: str
        """
        if artifact is None:
            raise ValueError("Invalid value for `artifact`, must not be `None`")  # noqa: E501

        self._artifact = artifact

    @property
    def href(self):
        """Gets the href of this Role.  # noqa: E501


        :return: The href of this Role.  # noqa: E501
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this Role.


        :param href: The href of this Role.  # noqa: E501
        :type: str
        """

        self._href = href

    @property
    def type(self):
        """Gets the type of this Role.  # noqa: E501


        :return: The type of this Role.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Role.


        :param type: The type of this Role.  # noqa: E501
        :type: str
        """
        if type is not None and len(type) < 1:
            raise ValueError("Invalid value for `type`, length must be greater than or equal to `1`")  # noqa: E501

        self._type = type

    @property
    def version(self):
        """Gets the version of this Role.  # noqa: E501


        :return: The version of this Role.  # noqa: E501
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this Role.


        :param version: The version of this Role.  # noqa: E501
        :type: str
        """
        if version is None:
            raise ValueError("Invalid value for `version`, must not be `None`")  # noqa: E501
        if version is not None and len(version) < 1:
            raise ValueError("Invalid value for `version`, length must be greater than or equal to `1`")  # noqa: E501

        self._version = version

    @property
    def name(self):
        """Gets the name of this Role.  # noqa: E501


        :return: The name of this Role.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Role.


        :param name: The name of this Role.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501
        if name is not None and len(name) < 1:
            raise ValueError("Invalid value for `name`, length must be greater than or equal to `1`")  # noqa: E501

        self._name = name

    @property
    def namespace(self):
        """Gets the namespace of this Role.  # noqa: E501


        :return: The namespace of this Role.  # noqa: E501
        :rtype: str
        """
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        """Sets the namespace of this Role.


        :param namespace: The namespace of this Role.  # noqa: E501
        :type: str
        """
        if namespace is None:
            raise ValueError("Invalid value for `namespace`, must not be `None`")  # noqa: E501
        if namespace is not None and len(namespace) < 1:
            raise ValueError("Invalid value for `namespace`, length must be greater than or equal to `1`")  # noqa: E501

        self._namespace = namespace

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
        if not isinstance(other, Role):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
