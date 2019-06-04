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


class BTUploadParams(object):
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
        'state': 'str',
        'document_name': 'str',
        'element_id': 'str',
        'cloud_storage_account_id': 'str'
    }

    attribute_map = {
        'name': 'name',
        'state': 'state',
        'document_name': 'documentName',
        'element_id': 'elementId',
        'cloud_storage_account_id': 'cloudStorageAccountId'
    }

    def __init__(self, name=None, state=None, document_name=None, element_id=None, cloud_storage_account_id=None):  # noqa: E501
        """BTUploadParams - a model defined in OpenAPI"""  # noqa: E501

        self._name = None
        self._state = None
        self._document_name = None
        self._element_id = None
        self._cloud_storage_account_id = None
        self.discriminator = None

        if name is not None:
            self.name = name
        if state is not None:
            self.state = state
        if document_name is not None:
            self.document_name = document_name
        if element_id is not None:
            self.element_id = element_id
        if cloud_storage_account_id is not None:
            self.cloud_storage_account_id = cloud_storage_account_id

    @property
    def name(self):
        """Gets the name of this BTUploadParams.  # noqa: E501


        :return: The name of this BTUploadParams.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this BTUploadParams.


        :param name: The name of this BTUploadParams.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def state(self):
        """Gets the state of this BTUploadParams.  # noqa: E501


        :return: The state of this BTUploadParams.  # noqa: E501
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this BTUploadParams.


        :param state: The state of this BTUploadParams.  # noqa: E501
        :type: str
        """

        self._state = state

    @property
    def document_name(self):
        """Gets the document_name of this BTUploadParams.  # noqa: E501


        :return: The document_name of this BTUploadParams.  # noqa: E501
        :rtype: str
        """
        return self._document_name

    @document_name.setter
    def document_name(self, document_name):
        """Sets the document_name of this BTUploadParams.


        :param document_name: The document_name of this BTUploadParams.  # noqa: E501
        :type: str
        """

        self._document_name = document_name

    @property
    def element_id(self):
        """Gets the element_id of this BTUploadParams.  # noqa: E501


        :return: The element_id of this BTUploadParams.  # noqa: E501
        :rtype: str
        """
        return self._element_id

    @element_id.setter
    def element_id(self, element_id):
        """Sets the element_id of this BTUploadParams.


        :param element_id: The element_id of this BTUploadParams.  # noqa: E501
        :type: str
        """

        self._element_id = element_id

    @property
    def cloud_storage_account_id(self):
        """Gets the cloud_storage_account_id of this BTUploadParams.  # noqa: E501


        :return: The cloud_storage_account_id of this BTUploadParams.  # noqa: E501
        :rtype: str
        """
        return self._cloud_storage_account_id

    @cloud_storage_account_id.setter
    def cloud_storage_account_id(self, cloud_storage_account_id):
        """Sets the cloud_storage_account_id of this BTUploadParams.


        :param cloud_storage_account_id: The cloud_storage_account_id of this BTUploadParams.  # noqa: E501
        :type: str
        """

        self._cloud_storage_account_id = cloud_storage_account_id

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
        if not isinstance(other, BTUploadParams):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
