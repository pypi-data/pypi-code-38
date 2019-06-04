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


class BTApplicationElementThumbnailParams(object):
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
        'description': 'str',
        'is_primary': 'bool',
        'unique_id': 'str',
        'base64_encoded_image': 'str',
        'image_width': 'int',
        'image_height': 'int'
    }

    attribute_map = {
        'description': 'description',
        'is_primary': 'isPrimary',
        'unique_id': 'uniqueId',
        'base64_encoded_image': 'base64EncodedImage',
        'image_width': 'imageWidth',
        'image_height': 'imageHeight'
    }

    def __init__(self, description=None, is_primary=None, unique_id=None, base64_encoded_image=None, image_width=None, image_height=None):  # noqa: E501
        """BTApplicationElementThumbnailParams - a model defined in OpenAPI"""  # noqa: E501

        self._description = None
        self._is_primary = None
        self._unique_id = None
        self._base64_encoded_image = None
        self._image_width = None
        self._image_height = None
        self.discriminator = None

        if description is not None:
            self.description = description
        if is_primary is not None:
            self.is_primary = is_primary
        if unique_id is not None:
            self.unique_id = unique_id
        if base64_encoded_image is not None:
            self.base64_encoded_image = base64_encoded_image
        if image_width is not None:
            self.image_width = image_width
        if image_height is not None:
            self.image_height = image_height

    @property
    def description(self):
        """Gets the description of this BTApplicationElementThumbnailParams.  # noqa: E501


        :return: The description of this BTApplicationElementThumbnailParams.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this BTApplicationElementThumbnailParams.


        :param description: The description of this BTApplicationElementThumbnailParams.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def is_primary(self):
        """Gets the is_primary of this BTApplicationElementThumbnailParams.  # noqa: E501


        :return: The is_primary of this BTApplicationElementThumbnailParams.  # noqa: E501
        :rtype: bool
        """
        return self._is_primary

    @is_primary.setter
    def is_primary(self, is_primary):
        """Sets the is_primary of this BTApplicationElementThumbnailParams.


        :param is_primary: The is_primary of this BTApplicationElementThumbnailParams.  # noqa: E501
        :type: bool
        """

        self._is_primary = is_primary

    @property
    def unique_id(self):
        """Gets the unique_id of this BTApplicationElementThumbnailParams.  # noqa: E501


        :return: The unique_id of this BTApplicationElementThumbnailParams.  # noqa: E501
        :rtype: str
        """
        return self._unique_id

    @unique_id.setter
    def unique_id(self, unique_id):
        """Sets the unique_id of this BTApplicationElementThumbnailParams.


        :param unique_id: The unique_id of this BTApplicationElementThumbnailParams.  # noqa: E501
        :type: str
        """

        self._unique_id = unique_id

    @property
    def base64_encoded_image(self):
        """Gets the base64_encoded_image of this BTApplicationElementThumbnailParams.  # noqa: E501


        :return: The base64_encoded_image of this BTApplicationElementThumbnailParams.  # noqa: E501
        :rtype: str
        """
        return self._base64_encoded_image

    @base64_encoded_image.setter
    def base64_encoded_image(self, base64_encoded_image):
        """Sets the base64_encoded_image of this BTApplicationElementThumbnailParams.


        :param base64_encoded_image: The base64_encoded_image of this BTApplicationElementThumbnailParams.  # noqa: E501
        :type: str
        """

        self._base64_encoded_image = base64_encoded_image

    @property
    def image_width(self):
        """Gets the image_width of this BTApplicationElementThumbnailParams.  # noqa: E501


        :return: The image_width of this BTApplicationElementThumbnailParams.  # noqa: E501
        :rtype: int
        """
        return self._image_width

    @image_width.setter
    def image_width(self, image_width):
        """Sets the image_width of this BTApplicationElementThumbnailParams.


        :param image_width: The image_width of this BTApplicationElementThumbnailParams.  # noqa: E501
        :type: int
        """

        self._image_width = image_width

    @property
    def image_height(self):
        """Gets the image_height of this BTApplicationElementThumbnailParams.  # noqa: E501


        :return: The image_height of this BTApplicationElementThumbnailParams.  # noqa: E501
        :rtype: int
        """
        return self._image_height

    @image_height.setter
    def image_height(self, image_height):
        """Sets the image_height of this BTApplicationElementThumbnailParams.


        :param image_height: The image_height of this BTApplicationElementThumbnailParams.  # noqa: E501
        :type: int
        """

        self._image_height = image_height

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
        if not isinstance(other, BTApplicationElementThumbnailParams):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
