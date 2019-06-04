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


class FormDataBodyPart(object):
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
        'content_disposition': 'ContentDisposition',
        'entity': 'object',
        'headers': 'BodyPartHeaders',
        'media_type': 'BodyPartMediaType',
        'message_body_workers': 'MessageBodyWorkers',
        'parent': 'MultiPart',
        'providers': 'object',
        'name': 'str',
        'value': 'str',
        'form_data_content_disposition': 'FormDataContentDisposition',
        'simple': 'bool',
        'parameterized_headers': 'BodyPartHeaders'
    }

    attribute_map = {
        'content_disposition': 'contentDisposition',
        'entity': 'entity',
        'headers': 'headers',
        'media_type': 'mediaType',
        'message_body_workers': 'messageBodyWorkers',
        'parent': 'parent',
        'providers': 'providers',
        'name': 'name',
        'value': 'value',
        'form_data_content_disposition': 'formDataContentDisposition',
        'simple': 'simple',
        'parameterized_headers': 'parameterizedHeaders'
    }

    def __init__(self, content_disposition=None, entity=None, headers=None, media_type=None, message_body_workers=None, parent=None, providers=None, name=None, value=None, form_data_content_disposition=None, simple=None, parameterized_headers=None):  # noqa: E501
        """FormDataBodyPart - a model defined in OpenAPI"""  # noqa: E501

        self._content_disposition = None
        self._entity = None
        self._headers = None
        self._media_type = None
        self._message_body_workers = None
        self._parent = None
        self._providers = None
        self._name = None
        self._value = None
        self._form_data_content_disposition = None
        self._simple = None
        self._parameterized_headers = None
        self.discriminator = None

        if content_disposition is not None:
            self.content_disposition = content_disposition
        if entity is not None:
            self.entity = entity
        if headers is not None:
            self.headers = headers
        if media_type is not None:
            self.media_type = media_type
        if message_body_workers is not None:
            self.message_body_workers = message_body_workers
        if parent is not None:
            self.parent = parent
        if providers is not None:
            self.providers = providers
        if name is not None:
            self.name = name
        if value is not None:
            self.value = value
        if form_data_content_disposition is not None:
            self.form_data_content_disposition = form_data_content_disposition
        if simple is not None:
            self.simple = simple
        if parameterized_headers is not None:
            self.parameterized_headers = parameterized_headers

    @property
    def content_disposition(self):
        """Gets the content_disposition of this FormDataBodyPart.  # noqa: E501


        :return: The content_disposition of this FormDataBodyPart.  # noqa: E501
        :rtype: ContentDisposition
        """
        return self._content_disposition

    @content_disposition.setter
    def content_disposition(self, content_disposition):
        """Sets the content_disposition of this FormDataBodyPart.


        :param content_disposition: The content_disposition of this FormDataBodyPart.  # noqa: E501
        :type: ContentDisposition
        """

        self._content_disposition = content_disposition

    @property
    def entity(self):
        """Gets the entity of this FormDataBodyPart.  # noqa: E501


        :return: The entity of this FormDataBodyPart.  # noqa: E501
        :rtype: object
        """
        return self._entity

    @entity.setter
    def entity(self, entity):
        """Sets the entity of this FormDataBodyPart.


        :param entity: The entity of this FormDataBodyPart.  # noqa: E501
        :type: object
        """

        self._entity = entity

    @property
    def headers(self):
        """Gets the headers of this FormDataBodyPart.  # noqa: E501


        :return: The headers of this FormDataBodyPart.  # noqa: E501
        :rtype: BodyPartHeaders
        """
        return self._headers

    @headers.setter
    def headers(self, headers):
        """Sets the headers of this FormDataBodyPart.


        :param headers: The headers of this FormDataBodyPart.  # noqa: E501
        :type: BodyPartHeaders
        """

        self._headers = headers

    @property
    def media_type(self):
        """Gets the media_type of this FormDataBodyPart.  # noqa: E501


        :return: The media_type of this FormDataBodyPart.  # noqa: E501
        :rtype: BodyPartMediaType
        """
        return self._media_type

    @media_type.setter
    def media_type(self, media_type):
        """Sets the media_type of this FormDataBodyPart.


        :param media_type: The media_type of this FormDataBodyPart.  # noqa: E501
        :type: BodyPartMediaType
        """

        self._media_type = media_type

    @property
    def message_body_workers(self):
        """Gets the message_body_workers of this FormDataBodyPart.  # noqa: E501


        :return: The message_body_workers of this FormDataBodyPart.  # noqa: E501
        :rtype: MessageBodyWorkers
        """
        return self._message_body_workers

    @message_body_workers.setter
    def message_body_workers(self, message_body_workers):
        """Sets the message_body_workers of this FormDataBodyPart.


        :param message_body_workers: The message_body_workers of this FormDataBodyPart.  # noqa: E501
        :type: MessageBodyWorkers
        """

        self._message_body_workers = message_body_workers

    @property
    def parent(self):
        """Gets the parent of this FormDataBodyPart.  # noqa: E501


        :return: The parent of this FormDataBodyPart.  # noqa: E501
        :rtype: MultiPart
        """
        return self._parent

    @parent.setter
    def parent(self, parent):
        """Sets the parent of this FormDataBodyPart.


        :param parent: The parent of this FormDataBodyPart.  # noqa: E501
        :type: MultiPart
        """

        self._parent = parent

    @property
    def providers(self):
        """Gets the providers of this FormDataBodyPart.  # noqa: E501


        :return: The providers of this FormDataBodyPart.  # noqa: E501
        :rtype: object
        """
        return self._providers

    @providers.setter
    def providers(self, providers):
        """Sets the providers of this FormDataBodyPart.


        :param providers: The providers of this FormDataBodyPart.  # noqa: E501
        :type: object
        """

        self._providers = providers

    @property
    def name(self):
        """Gets the name of this FormDataBodyPart.  # noqa: E501


        :return: The name of this FormDataBodyPart.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this FormDataBodyPart.


        :param name: The name of this FormDataBodyPart.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def value(self):
        """Gets the value of this FormDataBodyPart.  # noqa: E501


        :return: The value of this FormDataBodyPart.  # noqa: E501
        :rtype: str
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this FormDataBodyPart.


        :param value: The value of this FormDataBodyPart.  # noqa: E501
        :type: str
        """

        self._value = value

    @property
    def form_data_content_disposition(self):
        """Gets the form_data_content_disposition of this FormDataBodyPart.  # noqa: E501


        :return: The form_data_content_disposition of this FormDataBodyPart.  # noqa: E501
        :rtype: FormDataContentDisposition
        """
        return self._form_data_content_disposition

    @form_data_content_disposition.setter
    def form_data_content_disposition(self, form_data_content_disposition):
        """Sets the form_data_content_disposition of this FormDataBodyPart.


        :param form_data_content_disposition: The form_data_content_disposition of this FormDataBodyPart.  # noqa: E501
        :type: FormDataContentDisposition
        """

        self._form_data_content_disposition = form_data_content_disposition

    @property
    def simple(self):
        """Gets the simple of this FormDataBodyPart.  # noqa: E501


        :return: The simple of this FormDataBodyPart.  # noqa: E501
        :rtype: bool
        """
        return self._simple

    @simple.setter
    def simple(self, simple):
        """Sets the simple of this FormDataBodyPart.


        :param simple: The simple of this FormDataBodyPart.  # noqa: E501
        :type: bool
        """

        self._simple = simple

    @property
    def parameterized_headers(self):
        """Gets the parameterized_headers of this FormDataBodyPart.  # noqa: E501


        :return: The parameterized_headers of this FormDataBodyPart.  # noqa: E501
        :rtype: BodyPartHeaders
        """
        return self._parameterized_headers

    @parameterized_headers.setter
    def parameterized_headers(self, parameterized_headers):
        """Sets the parameterized_headers of this FormDataBodyPart.


        :param parameterized_headers: The parameterized_headers of this FormDataBodyPart.  # noqa: E501
        :type: BodyPartHeaders
        """

        self._parameterized_headers = parameterized_headers

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
        if not isinstance(other, FormDataBodyPart):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
