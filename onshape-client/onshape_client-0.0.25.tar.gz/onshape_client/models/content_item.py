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


class ContentItem(object):
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
        'link': 'str',
        'position': 'str',
        'title': 'str',
        'width': 'int',
        'height': 'int',
        'content_id': 'str',
        'item_title': 'str',
        'template': 'str',
        'thumbnail': 'str',
        'player': 'str',
        'pause_points': 'list[float]',
        'anchor': 'str',
        'vertical_offset': 'int',
        'horizontal_offset': 'int'
    }

    attribute_map = {
        'link': 'link',
        'position': 'position',
        'title': 'title',
        'width': 'width',
        'height': 'height',
        'content_id': 'contentId',
        'item_title': 'itemTitle',
        'template': 'template',
        'thumbnail': 'thumbnail',
        'player': 'player',
        'pause_points': 'pausePoints',
        'anchor': 'anchor',
        'vertical_offset': 'verticalOffset',
        'horizontal_offset': 'horizontalOffset'
    }

    def __init__(self, link=None, position=None, title=None, width=None, height=None, content_id=None, item_title=None, template=None, thumbnail=None, player=None, pause_points=None, anchor=None, vertical_offset=None, horizontal_offset=None):  # noqa: E501
        """ContentItem - a model defined in OpenAPI"""  # noqa: E501

        self._link = None
        self._position = None
        self._title = None
        self._width = None
        self._height = None
        self._content_id = None
        self._item_title = None
        self._template = None
        self._thumbnail = None
        self._player = None
        self._pause_points = None
        self._anchor = None
        self._vertical_offset = None
        self._horizontal_offset = None
        self.discriminator = None

        if link is not None:
            self.link = link
        if position is not None:
            self.position = position
        if title is not None:
            self.title = title
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if content_id is not None:
            self.content_id = content_id
        if item_title is not None:
            self.item_title = item_title
        if template is not None:
            self.template = template
        if thumbnail is not None:
            self.thumbnail = thumbnail
        if player is not None:
            self.player = player
        if pause_points is not None:
            self.pause_points = pause_points
        if anchor is not None:
            self.anchor = anchor
        if vertical_offset is not None:
            self.vertical_offset = vertical_offset
        if horizontal_offset is not None:
            self.horizontal_offset = horizontal_offset

    @property
    def link(self):
        """Gets the link of this ContentItem.  # noqa: E501


        :return: The link of this ContentItem.  # noqa: E501
        :rtype: str
        """
        return self._link

    @link.setter
    def link(self, link):
        """Sets the link of this ContentItem.


        :param link: The link of this ContentItem.  # noqa: E501
        :type: str
        """

        self._link = link

    @property
    def position(self):
        """Gets the position of this ContentItem.  # noqa: E501


        :return: The position of this ContentItem.  # noqa: E501
        :rtype: str
        """
        return self._position

    @position.setter
    def position(self, position):
        """Sets the position of this ContentItem.


        :param position: The position of this ContentItem.  # noqa: E501
        :type: str
        """

        self._position = position

    @property
    def title(self):
        """Gets the title of this ContentItem.  # noqa: E501


        :return: The title of this ContentItem.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this ContentItem.


        :param title: The title of this ContentItem.  # noqa: E501
        :type: str
        """

        self._title = title

    @property
    def width(self):
        """Gets the width of this ContentItem.  # noqa: E501


        :return: The width of this ContentItem.  # noqa: E501
        :rtype: int
        """
        return self._width

    @width.setter
    def width(self, width):
        """Sets the width of this ContentItem.


        :param width: The width of this ContentItem.  # noqa: E501
        :type: int
        """

        self._width = width

    @property
    def height(self):
        """Gets the height of this ContentItem.  # noqa: E501


        :return: The height of this ContentItem.  # noqa: E501
        :rtype: int
        """
        return self._height

    @height.setter
    def height(self, height):
        """Sets the height of this ContentItem.


        :param height: The height of this ContentItem.  # noqa: E501
        :type: int
        """

        self._height = height

    @property
    def content_id(self):
        """Gets the content_id of this ContentItem.  # noqa: E501


        :return: The content_id of this ContentItem.  # noqa: E501
        :rtype: str
        """
        return self._content_id

    @content_id.setter
    def content_id(self, content_id):
        """Sets the content_id of this ContentItem.


        :param content_id: The content_id of this ContentItem.  # noqa: E501
        :type: str
        """

        self._content_id = content_id

    @property
    def item_title(self):
        """Gets the item_title of this ContentItem.  # noqa: E501


        :return: The item_title of this ContentItem.  # noqa: E501
        :rtype: str
        """
        return self._item_title

    @item_title.setter
    def item_title(self, item_title):
        """Sets the item_title of this ContentItem.


        :param item_title: The item_title of this ContentItem.  # noqa: E501
        :type: str
        """

        self._item_title = item_title

    @property
    def template(self):
        """Gets the template of this ContentItem.  # noqa: E501


        :return: The template of this ContentItem.  # noqa: E501
        :rtype: str
        """
        return self._template

    @template.setter
    def template(self, template):
        """Sets the template of this ContentItem.


        :param template: The template of this ContentItem.  # noqa: E501
        :type: str
        """

        self._template = template

    @property
    def thumbnail(self):
        """Gets the thumbnail of this ContentItem.  # noqa: E501


        :return: The thumbnail of this ContentItem.  # noqa: E501
        :rtype: str
        """
        return self._thumbnail

    @thumbnail.setter
    def thumbnail(self, thumbnail):
        """Sets the thumbnail of this ContentItem.


        :param thumbnail: The thumbnail of this ContentItem.  # noqa: E501
        :type: str
        """

        self._thumbnail = thumbnail

    @property
    def player(self):
        """Gets the player of this ContentItem.  # noqa: E501


        :return: The player of this ContentItem.  # noqa: E501
        :rtype: str
        """
        return self._player

    @player.setter
    def player(self, player):
        """Sets the player of this ContentItem.


        :param player: The player of this ContentItem.  # noqa: E501
        :type: str
        """

        self._player = player

    @property
    def pause_points(self):
        """Gets the pause_points of this ContentItem.  # noqa: E501


        :return: The pause_points of this ContentItem.  # noqa: E501
        :rtype: list[float]
        """
        return self._pause_points

    @pause_points.setter
    def pause_points(self, pause_points):
        """Sets the pause_points of this ContentItem.


        :param pause_points: The pause_points of this ContentItem.  # noqa: E501
        :type: list[float]
        """

        self._pause_points = pause_points

    @property
    def anchor(self):
        """Gets the anchor of this ContentItem.  # noqa: E501


        :return: The anchor of this ContentItem.  # noqa: E501
        :rtype: str
        """
        return self._anchor

    @anchor.setter
    def anchor(self, anchor):
        """Sets the anchor of this ContentItem.


        :param anchor: The anchor of this ContentItem.  # noqa: E501
        :type: str
        """

        self._anchor = anchor

    @property
    def vertical_offset(self):
        """Gets the vertical_offset of this ContentItem.  # noqa: E501


        :return: The vertical_offset of this ContentItem.  # noqa: E501
        :rtype: int
        """
        return self._vertical_offset

    @vertical_offset.setter
    def vertical_offset(self, vertical_offset):
        """Sets the vertical_offset of this ContentItem.


        :param vertical_offset: The vertical_offset of this ContentItem.  # noqa: E501
        :type: int
        """

        self._vertical_offset = vertical_offset

    @property
    def horizontal_offset(self):
        """Gets the horizontal_offset of this ContentItem.  # noqa: E501


        :return: The horizontal_offset of this ContentItem.  # noqa: E501
        :rtype: int
        """
        return self._horizontal_offset

    @horizontal_offset.setter
    def horizontal_offset(self, horizontal_offset):
        """Sets the horizontal_offset of this ContentItem.


        :param horizontal_offset: The horizontal_offset of this ContentItem.  # noqa: E501
        :type: int
        """

        self._horizontal_offset = horizontal_offset

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
        if not isinstance(other, ContentItem):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
