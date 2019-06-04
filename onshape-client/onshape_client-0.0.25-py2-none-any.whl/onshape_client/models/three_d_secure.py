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


class ThreeDSecure(object):
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
        'id': 'str',
        'object': 'str',
        'amount': 'int',
        'authenticated': 'bool',
        'card': 'Card',
        'created': 'int',
        'currency': 'str',
        'livemode': 'bool',
        'redirect_url': 'str',
        'status': 'str'
    }

    attribute_map = {
        'id': 'id',
        'object': 'object',
        'amount': 'amount',
        'authenticated': 'authenticated',
        'card': 'card',
        'created': 'created',
        'currency': 'currency',
        'livemode': 'livemode',
        'redirect_url': 'redirectURL',
        'status': 'status'
    }

    def __init__(self, id=None, object=None, amount=None, authenticated=None, card=None, created=None, currency=None, livemode=None, redirect_url=None, status=None):  # noqa: E501
        """ThreeDSecure - a model defined in OpenAPI"""  # noqa: E501

        self._id = None
        self._object = None
        self._amount = None
        self._authenticated = None
        self._card = None
        self._created = None
        self._currency = None
        self._livemode = None
        self._redirect_url = None
        self._status = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if object is not None:
            self.object = object
        if amount is not None:
            self.amount = amount
        if authenticated is not None:
            self.authenticated = authenticated
        if card is not None:
            self.card = card
        if created is not None:
            self.created = created
        if currency is not None:
            self.currency = currency
        if livemode is not None:
            self.livemode = livemode
        if redirect_url is not None:
            self.redirect_url = redirect_url
        if status is not None:
            self.status = status

    @property
    def id(self):
        """Gets the id of this ThreeDSecure.  # noqa: E501


        :return: The id of this ThreeDSecure.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this ThreeDSecure.


        :param id: The id of this ThreeDSecure.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def object(self):
        """Gets the object of this ThreeDSecure.  # noqa: E501


        :return: The object of this ThreeDSecure.  # noqa: E501
        :rtype: str
        """
        return self._object

    @object.setter
    def object(self, object):
        """Sets the object of this ThreeDSecure.


        :param object: The object of this ThreeDSecure.  # noqa: E501
        :type: str
        """

        self._object = object

    @property
    def amount(self):
        """Gets the amount of this ThreeDSecure.  # noqa: E501


        :return: The amount of this ThreeDSecure.  # noqa: E501
        :rtype: int
        """
        return self._amount

    @amount.setter
    def amount(self, amount):
        """Sets the amount of this ThreeDSecure.


        :param amount: The amount of this ThreeDSecure.  # noqa: E501
        :type: int
        """

        self._amount = amount

    @property
    def authenticated(self):
        """Gets the authenticated of this ThreeDSecure.  # noqa: E501


        :return: The authenticated of this ThreeDSecure.  # noqa: E501
        :rtype: bool
        """
        return self._authenticated

    @authenticated.setter
    def authenticated(self, authenticated):
        """Sets the authenticated of this ThreeDSecure.


        :param authenticated: The authenticated of this ThreeDSecure.  # noqa: E501
        :type: bool
        """

        self._authenticated = authenticated

    @property
    def card(self):
        """Gets the card of this ThreeDSecure.  # noqa: E501


        :return: The card of this ThreeDSecure.  # noqa: E501
        :rtype: Card
        """
        return self._card

    @card.setter
    def card(self, card):
        """Sets the card of this ThreeDSecure.


        :param card: The card of this ThreeDSecure.  # noqa: E501
        :type: Card
        """

        self._card = card

    @property
    def created(self):
        """Gets the created of this ThreeDSecure.  # noqa: E501


        :return: The created of this ThreeDSecure.  # noqa: E501
        :rtype: int
        """
        return self._created

    @created.setter
    def created(self, created):
        """Sets the created of this ThreeDSecure.


        :param created: The created of this ThreeDSecure.  # noqa: E501
        :type: int
        """

        self._created = created

    @property
    def currency(self):
        """Gets the currency of this ThreeDSecure.  # noqa: E501


        :return: The currency of this ThreeDSecure.  # noqa: E501
        :rtype: str
        """
        return self._currency

    @currency.setter
    def currency(self, currency):
        """Sets the currency of this ThreeDSecure.


        :param currency: The currency of this ThreeDSecure.  # noqa: E501
        :type: str
        """

        self._currency = currency

    @property
    def livemode(self):
        """Gets the livemode of this ThreeDSecure.  # noqa: E501


        :return: The livemode of this ThreeDSecure.  # noqa: E501
        :rtype: bool
        """
        return self._livemode

    @livemode.setter
    def livemode(self, livemode):
        """Sets the livemode of this ThreeDSecure.


        :param livemode: The livemode of this ThreeDSecure.  # noqa: E501
        :type: bool
        """

        self._livemode = livemode

    @property
    def redirect_url(self):
        """Gets the redirect_url of this ThreeDSecure.  # noqa: E501


        :return: The redirect_url of this ThreeDSecure.  # noqa: E501
        :rtype: str
        """
        return self._redirect_url

    @redirect_url.setter
    def redirect_url(self, redirect_url):
        """Sets the redirect_url of this ThreeDSecure.


        :param redirect_url: The redirect_url of this ThreeDSecure.  # noqa: E501
        :type: str
        """

        self._redirect_url = redirect_url

    @property
    def status(self):
        """Gets the status of this ThreeDSecure.  # noqa: E501


        :return: The status of this ThreeDSecure.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this ThreeDSecure.


        :param status: The status of this ThreeDSecure.  # noqa: E501
        :type: str
        """

        self._status = status

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
        if not isinstance(other, ThreeDSecure):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
