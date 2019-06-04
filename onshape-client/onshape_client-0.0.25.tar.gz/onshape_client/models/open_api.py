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


class OpenAPI(object):
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
        'openapi': 'str',
        'info': 'Info',
        'external_docs': 'ExternalDocumentation',
        'servers': 'list[Server]',
        'security': 'list[SecurityRequirement]',
        'tags': 'list[Tag]',
        'paths': 'OAuthFlowScopes',
        'components': 'Components',
        'extensions': 'dict(str, object)'
    }

    attribute_map = {
        'openapi': 'openapi',
        'info': 'info',
        'external_docs': 'externalDocs',
        'servers': 'servers',
        'security': 'security',
        'tags': 'tags',
        'paths': 'paths',
        'components': 'components',
        'extensions': 'extensions'
    }

    def __init__(self, openapi=None, info=None, external_docs=None, servers=None, security=None, tags=None, paths=None, components=None, extensions=None):  # noqa: E501
        """OpenAPI - a model defined in OpenAPI"""  # noqa: E501

        self._openapi = None
        self._info = None
        self._external_docs = None
        self._servers = None
        self._security = None
        self._tags = None
        self._paths = None
        self._components = None
        self._extensions = None
        self.discriminator = None

        if openapi is not None:
            self.openapi = openapi
        if info is not None:
            self.info = info
        if external_docs is not None:
            self.external_docs = external_docs
        if servers is not None:
            self.servers = servers
        if security is not None:
            self.security = security
        if tags is not None:
            self.tags = tags
        if paths is not None:
            self.paths = paths
        if components is not None:
            self.components = components
        if extensions is not None:
            self.extensions = extensions

    @property
    def openapi(self):
        """Gets the openapi of this OpenAPI.  # noqa: E501


        :return: The openapi of this OpenAPI.  # noqa: E501
        :rtype: str
        """
        return self._openapi

    @openapi.setter
    def openapi(self, openapi):
        """Sets the openapi of this OpenAPI.


        :param openapi: The openapi of this OpenAPI.  # noqa: E501
        :type: str
        """

        self._openapi = openapi

    @property
    def info(self):
        """Gets the info of this OpenAPI.  # noqa: E501


        :return: The info of this OpenAPI.  # noqa: E501
        :rtype: Info
        """
        return self._info

    @info.setter
    def info(self, info):
        """Sets the info of this OpenAPI.


        :param info: The info of this OpenAPI.  # noqa: E501
        :type: Info
        """

        self._info = info

    @property
    def external_docs(self):
        """Gets the external_docs of this OpenAPI.  # noqa: E501


        :return: The external_docs of this OpenAPI.  # noqa: E501
        :rtype: ExternalDocumentation
        """
        return self._external_docs

    @external_docs.setter
    def external_docs(self, external_docs):
        """Sets the external_docs of this OpenAPI.


        :param external_docs: The external_docs of this OpenAPI.  # noqa: E501
        :type: ExternalDocumentation
        """

        self._external_docs = external_docs

    @property
    def servers(self):
        """Gets the servers of this OpenAPI.  # noqa: E501


        :return: The servers of this OpenAPI.  # noqa: E501
        :rtype: list[Server]
        """
        return self._servers

    @servers.setter
    def servers(self, servers):
        """Sets the servers of this OpenAPI.


        :param servers: The servers of this OpenAPI.  # noqa: E501
        :type: list[Server]
        """

        self._servers = servers

    @property
    def security(self):
        """Gets the security of this OpenAPI.  # noqa: E501


        :return: The security of this OpenAPI.  # noqa: E501
        :rtype: list[SecurityRequirement]
        """
        return self._security

    @security.setter
    def security(self, security):
        """Sets the security of this OpenAPI.


        :param security: The security of this OpenAPI.  # noqa: E501
        :type: list[SecurityRequirement]
        """

        self._security = security

    @property
    def tags(self):
        """Gets the tags of this OpenAPI.  # noqa: E501


        :return: The tags of this OpenAPI.  # noqa: E501
        :rtype: list[Tag]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this OpenAPI.


        :param tags: The tags of this OpenAPI.  # noqa: E501
        :type: list[Tag]
        """

        self._tags = tags

    @property
    def paths(self):
        """Gets the paths of this OpenAPI.  # noqa: E501


        :return: The paths of this OpenAPI.  # noqa: E501
        :rtype: OAuthFlowScopes
        """
        return self._paths

    @paths.setter
    def paths(self, paths):
        """Sets the paths of this OpenAPI.


        :param paths: The paths of this OpenAPI.  # noqa: E501
        :type: OAuthFlowScopes
        """

        self._paths = paths

    @property
    def components(self):
        """Gets the components of this OpenAPI.  # noqa: E501


        :return: The components of this OpenAPI.  # noqa: E501
        :rtype: Components
        """
        return self._components

    @components.setter
    def components(self, components):
        """Sets the components of this OpenAPI.


        :param components: The components of this OpenAPI.  # noqa: E501
        :type: Components
        """

        self._components = components

    @property
    def extensions(self):
        """Gets the extensions of this OpenAPI.  # noqa: E501


        :return: The extensions of this OpenAPI.  # noqa: E501
        :rtype: dict(str, object)
        """
        return self._extensions

    @extensions.setter
    def extensions(self, extensions):
        """Sets the extensions of this OpenAPI.


        :param extensions: The extensions of this OpenAPI.  # noqa: E501
        :type: dict(str, object)
        """

        self._extensions = extensions

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
        if not isinstance(other, OpenAPI):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
