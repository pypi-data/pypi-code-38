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
from orcid_api_v3.models.source_v30_rc2 import SourceV30Rc2  # noqa: F401,E501


class Notification(object):
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
        'source': 'SourceV30Rc2',
        'put_code': 'int',
        'notification_type': 'str',
        'created_date': 'datetime',
        'sent_date': 'datetime',
        'read_date': 'datetime',
        'archived_date': 'datetime'
    }

    attribute_map = {
        'source': 'source',
        'put_code': 'put-code',
        'notification_type': 'notification-type',
        'created_date': 'created-date',
        'sent_date': 'sent-date',
        'read_date': 'read-date',
        'archived_date': 'archived-date'
    }

    def __init__(self, source=None, put_code=None, notification_type=None, created_date=None, sent_date=None, read_date=None, archived_date=None):  # noqa: E501
        """Notification - a model defined in Swagger"""  # noqa: E501
        self._source = None
        self._put_code = None
        self._notification_type = None
        self._created_date = None
        self._sent_date = None
        self._read_date = None
        self._archived_date = None
        self.discriminator = None
        if source is not None:
            self.source = source
        if put_code is not None:
            self.put_code = put_code
        self.notification_type = notification_type
        if created_date is not None:
            self.created_date = created_date
        if sent_date is not None:
            self.sent_date = sent_date
        if read_date is not None:
            self.read_date = read_date
        if archived_date is not None:
            self.archived_date = archived_date

    @property
    def source(self):
        """Gets the source of this Notification.  # noqa: E501


        :return: The source of this Notification.  # noqa: E501
        :rtype: SourceV30Rc2
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this Notification.


        :param source: The source of this Notification.  # noqa: E501
        :type: SourceV30Rc2
        """

        self._source = source

    @property
    def put_code(self):
        """Gets the put_code of this Notification.  # noqa: E501


        :return: The put_code of this Notification.  # noqa: E501
        :rtype: int
        """
        return self._put_code

    @put_code.setter
    def put_code(self, put_code):
        """Sets the put_code of this Notification.


        :param put_code: The put_code of this Notification.  # noqa: E501
        :type: int
        """

        self._put_code = put_code

    @property
    def notification_type(self):
        """Gets the notification_type of this Notification.  # noqa: E501


        :return: The notification_type of this Notification.  # noqa: E501
        :rtype: str
        """
        return self._notification_type

    @notification_type.setter
    def notification_type(self, notification_type):
        """Sets the notification_type of this Notification.


        :param notification_type: The notification_type of this Notification.  # noqa: E501
        :type: str
        """
        if notification_type is None:
            raise ValueError("Invalid value for `notification_type`, must not be `None`")  # noqa: E501
        allowed_values = ["CUSTOM", "INSTITUTIONAL_CONNECTION", "PERMISSION", "AMENDED", "SERVICE_ANNOUNCEMENT", "ADMINISTRATIVE", "TIP", "FIND_MY_STUFF"]  # noqa: E501
        if notification_type not in allowed_values:
            raise ValueError(
                "Invalid value for `notification_type` ({0}), must be one of {1}"  # noqa: E501
                .format(notification_type, allowed_values)
            )

        self._notification_type = notification_type

    @property
    def created_date(self):
        """Gets the created_date of this Notification.  # noqa: E501


        :return: The created_date of this Notification.  # noqa: E501
        :rtype: datetime
        """
        return self._created_date

    @created_date.setter
    def created_date(self, created_date):
        """Sets the created_date of this Notification.


        :param created_date: The created_date of this Notification.  # noqa: E501
        :type: datetime
        """

        self._created_date = created_date

    @property
    def sent_date(self):
        """Gets the sent_date of this Notification.  # noqa: E501


        :return: The sent_date of this Notification.  # noqa: E501
        :rtype: datetime
        """
        return self._sent_date

    @sent_date.setter
    def sent_date(self, sent_date):
        """Sets the sent_date of this Notification.


        :param sent_date: The sent_date of this Notification.  # noqa: E501
        :type: datetime
        """

        self._sent_date = sent_date

    @property
    def read_date(self):
        """Gets the read_date of this Notification.  # noqa: E501


        :return: The read_date of this Notification.  # noqa: E501
        :rtype: datetime
        """
        return self._read_date

    @read_date.setter
    def read_date(self, read_date):
        """Sets the read_date of this Notification.


        :param read_date: The read_date of this Notification.  # noqa: E501
        :type: datetime
        """

        self._read_date = read_date

    @property
    def archived_date(self):
        """Gets the archived_date of this Notification.  # noqa: E501


        :return: The archived_date of this Notification.  # noqa: E501
        :rtype: datetime
        """
        return self._archived_date

    @archived_date.setter
    def archived_date(self, archived_date):
        """Sets the archived_date of this Notification.


        :param archived_date: The archived_date of this Notification.  # noqa: E501
        :type: datetime
        """

        self._archived_date = archived_date

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
        if issubclass(Notification, dict):
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
        if not isinstance(other, Notification):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
