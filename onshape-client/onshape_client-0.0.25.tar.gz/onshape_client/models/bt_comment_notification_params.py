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


class BTCommentNotificationParams(object):
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
        'comment_id': 'str',
        'action': 'str'
    }

    attribute_map = {
        'comment_id': 'commentId',
        'action': 'action'
    }

    def __init__(self, comment_id=None, action=None):  # noqa: E501
        """BTCommentNotificationParams - a model defined in OpenAPI"""  # noqa: E501

        self._comment_id = None
        self._action = None
        self.discriminator = None

        if comment_id is not None:
            self.comment_id = comment_id
        if action is not None:
            self.action = action

    @property
    def comment_id(self):
        """Gets the comment_id of this BTCommentNotificationParams.  # noqa: E501


        :return: The comment_id of this BTCommentNotificationParams.  # noqa: E501
        :rtype: str
        """
        return self._comment_id

    @comment_id.setter
    def comment_id(self, comment_id):
        """Sets the comment_id of this BTCommentNotificationParams.


        :param comment_id: The comment_id of this BTCommentNotificationParams.  # noqa: E501
        :type: str
        """

        self._comment_id = comment_id

    @property
    def action(self):
        """Gets the action of this BTCommentNotificationParams.  # noqa: E501


        :return: The action of this BTCommentNotificationParams.  # noqa: E501
        :rtype: str
        """
        return self._action

    @action.setter
    def action(self, action):
        """Sets the action of this BTCommentNotificationParams.


        :param action: The action of this BTCommentNotificationParams.  # noqa: E501
        :type: str
        """
        allowed_values = ["CREATED", "UPDATED", "DELETED", "RESOLVED", "REOPENED", "REPLIED", "UNKNOWN"]  # noqa: E501
        if action not in allowed_values:
            raise ValueError(
                "Invalid value for `action` ({0}), must be one of {1}"  # noqa: E501
                .format(action, allowed_values)
            )

        self._action = action

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
        if not isinstance(other, BTCommentNotificationParams):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
