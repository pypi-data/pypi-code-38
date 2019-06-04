# coding: utf-8

"""
    ORCID Member

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: Latest
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class GroupIdRecord(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, name=None, group_id=None, description=None, type=None, put_code=None):
        """
        GroupIdRecord - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'name': 'str',
            'group_id': 'str',
            'description': 'str',
            'type': 'str',
            'put_code': 'int'
        }

        self.attribute_map = {
            'name': 'name',
            'group_id': 'group-id',
            'description': 'description',
            'type': 'type',
            'put_code': 'put-code'
        }

        self._name = name
        self._group_id = group_id
        self._description = description
        self._type = type
        self._put_code = put_code

    @property
    def name(self):
        """
        Gets the name of this GroupIdRecord.

        :return: The name of this GroupIdRecord.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this GroupIdRecord.

        :param name: The name of this GroupIdRecord.
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")

        self._name = name

    @property
    def group_id(self):
        """
        Gets the group_id of this GroupIdRecord.

        :return: The group_id of this GroupIdRecord.
        :rtype: str
        """
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        """
        Sets the group_id of this GroupIdRecord.

        :param group_id: The group_id of this GroupIdRecord.
        :type: str
        """
        if group_id is None:
            raise ValueError("Invalid value for `group_id`, must not be `None`")

        self._group_id = group_id

    @property
    def description(self):
        """
        Gets the description of this GroupIdRecord.

        :return: The description of this GroupIdRecord.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this GroupIdRecord.

        :param description: The description of this GroupIdRecord.
        :type: str
        """
        if description is None:
            raise ValueError("Invalid value for `description`, must not be `None`")

        self._description = description

    @property
    def type(self):
        """
        Gets the type of this GroupIdRecord.

        :return: The type of this GroupIdRecord.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this GroupIdRecord.

        :param type: The type of this GroupIdRecord.
        :type: str
        """
        if type is None:
            raise ValueError("Invalid value for `type`, must not be `None`")

        self._type = type

    @property
    def put_code(self):
        """
        Gets the put_code of this GroupIdRecord.

        :return: The put_code of this GroupIdRecord.
        :rtype: int
        """
        return self._put_code

    @put_code.setter
    def put_code(self, put_code):
        """
        Sets the put_code of this GroupIdRecord.

        :param put_code: The put_code of this GroupIdRecord.
        :type: int
        """

        self._put_code = put_code

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
        if not isinstance(other, GroupIdRecord):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
