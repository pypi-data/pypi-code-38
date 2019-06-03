# coding: utf-8

"""
    Smooch

    The Smooch API is a unified interface for powering messaging in your customer experiences across every channel. Our API speeds access to new markets, reduces time to ship, eliminates complexity, and helps you build the best experiences for your customers. For more information, visit our [official documentation](https://docs.smooch.io).

    OpenAPI spec version: 5.12
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class AttachmentResponse(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, media_url=None, media_type=None):
        """
        AttachmentResponse - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'media_url': 'str',
            'media_type': 'str'
        }

        self.attribute_map = {
            'media_url': 'mediaUrl',
            'media_type': 'mediaType'
        }

        self._media_url = None
        self._media_type = None

        # TODO: let required properties as mandatory parameter in the constructor.
        #       - to check if required property is not None (e.g. by calling setter)
        #       - ApiClient.__deserialize_model has to be adapted as well
        if media_url is not None:
          self.media_url = media_url
        if media_type is not None:
          self.media_type = media_type

    @property
    def media_url(self):
        """
        Gets the media_url of this AttachmentResponse.
        The mediaUrl for the message. Required for image/file messages. 

        :return: The media_url of this AttachmentResponse.
        :rtype: str
        """
        return self._media_url

    @media_url.setter
    def media_url(self, media_url):
        """
        Sets the media_url of this AttachmentResponse.
        The mediaUrl for the message. Required for image/file messages. 

        :param media_url: The media_url of this AttachmentResponse.
        :type: str
        """
        if media_url is None:
            raise ValueError("Invalid value for `media_url`, must not be `None`")

        self._media_url = media_url

    @property
    def media_type(self):
        """
        Gets the media_type of this AttachmentResponse.
        The mediaType for the message. Required for image/file messages. 

        :return: The media_type of this AttachmentResponse.
        :rtype: str
        """
        return self._media_type

    @media_type.setter
    def media_type(self, media_type):
        """
        Sets the media_type of this AttachmentResponse.
        The mediaType for the message. Required for image/file messages. 

        :param media_type: The media_type of this AttachmentResponse.
        :type: str
        """
        if media_type is None:
            raise ValueError("Invalid value for `media_type`, must not be `None`")

        self._media_type = media_type

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
        if not isinstance(other, AttachmentResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
