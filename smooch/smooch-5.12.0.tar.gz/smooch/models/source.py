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


class Source(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, type=None, original_message_id=None, original_message_timestamp=None):
        """
        Source - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'str',
            'type': 'str',
            'original_message_id': 'str',
            'original_message_timestamp': 'float'
        }

        self.attribute_map = {
            'id': 'id',
            'type': 'type',
            'original_message_id': 'originalMessageId',
            'original_message_timestamp': 'originalMessageTimestamp'
        }

        self._id = None
        self._type = None
        self._original_message_id = None
        self._original_message_timestamp = None

        # TODO: let required properties as mandatory parameter in the constructor.
        #       - to check if required property is not None (e.g. by calling setter)
        #       - ApiClient.__deserialize_model has to be adapted as well
        if id is not None:
          self.id = id
        if type is not None:
          self.type = type
        if original_message_id is not None:
          self.original_message_id = original_message_id
        if original_message_timestamp is not None:
          self.original_message_timestamp = original_message_timestamp

    @property
    def id(self):
        """
        Gets the id of this Source.
        An identifier used by Smooch for internal purposes.

        :return: The id of this Source.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this Source.
        An identifier used by Smooch for internal purposes.

        :param id: The id of this Source.
        :type: str
        """

        self._id = id

    @property
    def type(self):
        """
        Gets the type of this Source.
        An identifier for the channel from which a message originated. See [**IntegrationTypeEnum**](Enums.md#IntegrationTypeEnum) for available values.

        :return: The type of this Source.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this Source.
        An identifier for the channel from which a message originated. See [**IntegrationTypeEnum**](Enums.md#IntegrationTypeEnum) for available values.

        :param type: The type of this Source.
        :type: str
        """

        self._type = type

    @property
    def original_message_id(self):
        """
        Gets the original_message_id of this Source.
        Message identifier assigned by the originating channel.

        :return: The original_message_id of this Source.
        :rtype: str
        """
        return self._original_message_id

    @original_message_id.setter
    def original_message_id(self, original_message_id):
        """
        Sets the original_message_id of this Source.
        Message identifier assigned by the originating channel.

        :param original_message_id: The original_message_id of this Source.
        :type: str
        """

        self._original_message_id = original_message_id

    @property
    def original_message_timestamp(self):
        """
        Gets the original_message_timestamp of this Source.
        Message timestamp assigned by the originating channel.

        :return: The original_message_timestamp of this Source.
        :rtype: float
        """
        return self._original_message_timestamp

    @original_message_timestamp.setter
    def original_message_timestamp(self, original_message_timestamp):
        """
        Sets the original_message_timestamp of this Source.
        Message timestamp assigned by the originating channel.

        :param original_message_timestamp: The original_message_timestamp of this Source.
        :type: float
        """

        self._original_message_timestamp = original_message_timestamp

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
        if not isinstance(other, Source):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
