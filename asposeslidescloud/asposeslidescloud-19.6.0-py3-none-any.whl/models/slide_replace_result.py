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

from asposeslidescloud.models.slide import Slide

class SlideReplaceResult(Slide):


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
        'notes_slide': 'ResourceUriElement',
        'matches': 'int'
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
        'notes_slide': 'NotesSlide',
        'matches': 'Matches'
    }

    def __init__(self, self_uri=None, alternate_links=None, width=None, height=None, show_master_shapes=None, layout_slide=None, shapes=None, theme=None, placeholders=None, images=None, comments=None, background=None, notes_slide=None, matches=None):  # noqa: E501
        """SlideReplaceResult - a model defined in Swagger"""  # noqa: E501
        super(SlideReplaceResult, self).__init__(self_uri, alternate_links, width, height, show_master_shapes, layout_slide, shapes, theme, placeholders, images, comments, background, notes_slide)

        self._matches = None

        self.matches = matches

    @property
    def matches(self):
        """Gets the matches of this SlideReplaceResult.  # noqa: E501

        Gets or sets the number of matches   # noqa: E501

        :return: The matches of this SlideReplaceResult.  # noqa: E501
        :rtype: int
        """
        return self._matches

    @matches.setter
    def matches(self, matches):
        """Sets the matches of this SlideReplaceResult.

        Gets or sets the number of matches   # noqa: E501

        :param matches: The matches of this SlideReplaceResult.  # noqa: E501
        :type: int
        """
        self._matches = matches

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
        if not isinstance(other, SlideReplaceResult):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
