# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose">
#   Copyright (c) 2018 Aspose.Slides for Cloud
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

import pprint
import re  # noqa: F401

import six

from asposeslidescloud.models.resource_base import ResourceBase

class Slide(ResourceBase):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'self_uri': 'ResourceUri',
        'alternate_links': 'list[ResourceUri]',
        'width': 'float',
        'height': 'float',
        'show_master_shapes': 'bool',
        'layout_slide': 'ResourceUriElement',
        'shapes': 'ResourceUriElement',
        'theme': 'ResourceUriElement',
        'placeholders': 'ResourceUriElement',
        'images': 'ResourceUriElement',
        'comments': 'ResourceUriElement',
        'background': 'ResourceUriElement',
        'notes_slide': 'ResourceUriElement'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks',
        'width': 'Width',
        'height': 'Height',
        'show_master_shapes': 'ShowMasterShapes',
        'layout_slide': 'LayoutSlide',
        'shapes': 'Shapes',
        'theme': 'Theme',
        'placeholders': 'Placeholders',
        'images': 'Images',
        'comments': 'Comments',
        'background': 'Background',
        'notes_slide': 'NotesSlide'
    }

    def __init__(self, self_uri=None, alternate_links=None, width=None, height=None, show_master_shapes=None, layout_slide=None, shapes=None, theme=None, placeholders=None, images=None, comments=None, background=None, notes_slide=None):  # noqa: E501
        """Slide - a model defined in Swagger"""  # noqa: E501
        super(Slide, self).__init__(self_uri, alternate_links)

        self._width = None
        self._height = None
        self._show_master_shapes = None
        self._layout_slide = None
        self._shapes = None
        self._theme = None
        self._placeholders = None
        self._images = None
        self._comments = None
        self._background = None
        self._notes_slide = None

        self.width = width
        self.height = height
        self.show_master_shapes = show_master_shapes
        if layout_slide is not None:
            self.layout_slide = layout_slide
        if shapes is not None:
            self.shapes = shapes
        if theme is not None:
            self.theme = theme
        if placeholders is not None:
            self.placeholders = placeholders
        if images is not None:
            self.images = images
        if comments is not None:
            self.comments = comments
        if background is not None:
            self.background = background
        if notes_slide is not None:
            self.notes_slide = notes_slide

    @property
    def width(self):
        """Gets the width of this Slide.  # noqa: E501

        Gets or sets the width.  # noqa: E501

        :return: The width of this Slide.  # noqa: E501
        :rtype: float
        """
        return self._width

    @width.setter
    def width(self, width):
        """Sets the width of this Slide.

        Gets or sets the width.  # noqa: E501

        :param width: The width of this Slide.  # noqa: E501
        :type: float
        """
        self._width = width

    @property
    def height(self):
        """Gets the height of this Slide.  # noqa: E501

        Gets or sets the height.  # noqa: E501

        :return: The height of this Slide.  # noqa: E501
        :rtype: float
        """
        return self._height

    @height.setter
    def height(self, height):
        """Sets the height of this Slide.

        Gets or sets the height.  # noqa: E501

        :param height: The height of this Slide.  # noqa: E501
        :type: float
        """
        self._height = height

    @property
    def show_master_shapes(self):
        """Gets the show_master_shapes of this Slide.  # noqa: E501

        Specifies if shapes of the master slide should be shown on the slide. True by default.  # noqa: E501

        :return: The show_master_shapes of this Slide.  # noqa: E501
        :rtype: bool
        """
        return self._show_master_shapes

    @show_master_shapes.setter
    def show_master_shapes(self, show_master_shapes):
        """Sets the show_master_shapes of this Slide.

        Specifies if shapes of the master slide should be shown on the slide. True by default.  # noqa: E501

        :param show_master_shapes: The show_master_shapes of this Slide.  # noqa: E501
        :type: bool
        """
        self._show_master_shapes = show_master_shapes

    @property
    def layout_slide(self):
        """Gets the layout_slide of this Slide.  # noqa: E501

        Gets or sets the  link to the layout slide.  # noqa: E501

        :return: The layout_slide of this Slide.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._layout_slide

    @layout_slide.setter
    def layout_slide(self, layout_slide):
        """Sets the layout_slide of this Slide.

        Gets or sets the  link to the layout slide.  # noqa: E501

        :param layout_slide: The layout_slide of this Slide.  # noqa: E501
        :type: ResourceUriElement
        """
        self._layout_slide = layout_slide

    @property
    def shapes(self):
        """Gets the shapes of this Slide.  # noqa: E501

        Gets or sets the  link to list of top-level shapes.  # noqa: E501

        :return: The shapes of this Slide.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._shapes

    @shapes.setter
    def shapes(self, shapes):
        """Sets the shapes of this Slide.

        Gets or sets the  link to list of top-level shapes.  # noqa: E501

        :param shapes: The shapes of this Slide.  # noqa: E501
        :type: ResourceUriElement
        """
        self._shapes = shapes

    @property
    def theme(self):
        """Gets the theme of this Slide.  # noqa: E501

        Gets or sets the link to theme.  # noqa: E501

        :return: The theme of this Slide.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._theme

    @theme.setter
    def theme(self, theme):
        """Sets the theme of this Slide.

        Gets or sets the link to theme.  # noqa: E501

        :param theme: The theme of this Slide.  # noqa: E501
        :type: ResourceUriElement
        """
        self._theme = theme

    @property
    def placeholders(self):
        """Gets the placeholders of this Slide.  # noqa: E501

        Gets or sets the  link to placeholders.  # noqa: E501

        :return: The placeholders of this Slide.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._placeholders

    @placeholders.setter
    def placeholders(self, placeholders):
        """Sets the placeholders of this Slide.

        Gets or sets the  link to placeholders.  # noqa: E501

        :param placeholders: The placeholders of this Slide.  # noqa: E501
        :type: ResourceUriElement
        """
        self._placeholders = placeholders

    @property
    def images(self):
        """Gets the images of this Slide.  # noqa: E501

        Gets or sets the link to images.  # noqa: E501

        :return: The images of this Slide.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._images

    @images.setter
    def images(self, images):
        """Sets the images of this Slide.

        Gets or sets the link to images.  # noqa: E501

        :param images: The images of this Slide.  # noqa: E501
        :type: ResourceUriElement
        """
        self._images = images

    @property
    def comments(self):
        """Gets the comments of this Slide.  # noqa: E501

        Gets or sets the link to comments.  # noqa: E501

        :return: The comments of this Slide.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._comments

    @comments.setter
    def comments(self, comments):
        """Sets the comments of this Slide.

        Gets or sets the link to comments.  # noqa: E501

        :param comments: The comments of this Slide.  # noqa: E501
        :type: ResourceUriElement
        """
        self._comments = comments

    @property
    def background(self):
        """Gets the background of this Slide.  # noqa: E501

        Get or sets the link to slide's background  # noqa: E501

        :return: The background of this Slide.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._background

    @background.setter
    def background(self, background):
        """Sets the background of this Slide.

        Get or sets the link to slide's background  # noqa: E501

        :param background: The background of this Slide.  # noqa: E501
        :type: ResourceUriElement
        """
        self._background = background

    @property
    def notes_slide(self):
        """Gets the notes_slide of this Slide.  # noqa: E501

        Get or sets the link to notes slide.  # noqa: E501

        :return: The notes_slide of this Slide.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._notes_slide

    @notes_slide.setter
    def notes_slide(self, notes_slide):
        """Sets the notes_slide of this Slide.

        Get or sets the link to notes slide.  # noqa: E501

        :param notes_slide: The notes_slide of this Slide.  # noqa: E501
        :type: ResourceUriElement
        """
        self._notes_slide = notes_slide

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

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Slide):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
