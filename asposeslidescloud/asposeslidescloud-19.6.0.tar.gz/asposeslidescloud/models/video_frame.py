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

from asposeslidescloud.models.geometry_shape import GeometryShape

class VideoFrame(GeometryShape):


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
        'name': 'str',
        'width': 'float',
        'height': 'float',
        'alternative_text': 'str',
        'hidden': 'bool',
        'x': 'float',
        'y': 'float',
        'z_order_position': 'int',
        'shapes': 'ResourceUriElement',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'type': 'str',
        'shape_type': 'str',
        'geometry_shape_type': 'str',
        'full_screen_mode': 'bool',
        'hide_at_showing': 'bool',
        'play_loop_mode': 'bool',
        'play_mode': 'str',
        'rewind_video': 'bool',
        'volume': 'str',
        'base64_data': 'str'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks',
        'name': 'Name',
        'width': 'Width',
        'height': 'Height',
        'alternative_text': 'AlternativeText',
        'hidden': 'Hidden',
        'x': 'X',
        'y': 'Y',
        'z_order_position': 'ZOrderPosition',
        'shapes': 'Shapes',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'type': 'Type',
        'shape_type': 'ShapeType',
        'geometry_shape_type': 'GeometryShapeType',
        'full_screen_mode': 'FullScreenMode',
        'hide_at_showing': 'HideAtShowing',
        'play_loop_mode': 'PlayLoopMode',
        'play_mode': 'PlayMode',
        'rewind_video': 'RewindVideo',
        'volume': 'Volume',
        'base64_data': 'Base64Data'
    }

    def __init__(self, self_uri=None, alternate_links=None, name=None, width=None, height=None, alternative_text=None, hidden=None, x=None, y=None, z_order_position=None, shapes=None, fill_format=None, effect_format=None, line_format=None, type='VideoFrame', shape_type='VideoFrame', geometry_shape_type=None, full_screen_mode=None, hide_at_showing=None, play_loop_mode=None, play_mode=None, rewind_video=None, volume=None, base64_data=None):  # noqa: E501
        """VideoFrame - a model defined in Swagger"""  # noqa: E501
        super(VideoFrame, self).__init__(self_uri, alternate_links, name, width, height, alternative_text, hidden, x, y, z_order_position, shapes, fill_format, effect_format, line_format, type, shape_type, geometry_shape_type)

        self._full_screen_mode = None
        self._hide_at_showing = None
        self._play_loop_mode = None
        self._play_mode = None
        self._rewind_video = None
        self._volume = None
        self._base64_data = None

        if full_screen_mode is not None:
            self.full_screen_mode = full_screen_mode
        if hide_at_showing is not None:
            self.hide_at_showing = hide_at_showing
        if play_loop_mode is not None:
            self.play_loop_mode = play_loop_mode
        if play_mode is not None:
            self.play_mode = play_mode
        if rewind_video is not None:
            self.rewind_video = rewind_video
        if volume is not None:
            self.volume = volume
        if base64_data is not None:
            self.base64_data = base64_data

    @property
    def full_screen_mode(self):
        """Gets the full_screen_mode of this VideoFrame.  # noqa: E501

        Determines whether a video is shown in full screen mode.  # noqa: E501

        :return: The full_screen_mode of this VideoFrame.  # noqa: E501
        :rtype: bool
        """
        return self._full_screen_mode

    @full_screen_mode.setter
    def full_screen_mode(self, full_screen_mode):
        """Sets the full_screen_mode of this VideoFrame.

        Determines whether a video is shown in full screen mode.  # noqa: E501

        :param full_screen_mode: The full_screen_mode of this VideoFrame.  # noqa: E501
        :type: bool
        """
        self._full_screen_mode = full_screen_mode

    @property
    def hide_at_showing(self):
        """Gets the hide_at_showing of this VideoFrame.  # noqa: E501

        Determines whether a VideoFrame is hidden.   # noqa: E501

        :return: The hide_at_showing of this VideoFrame.  # noqa: E501
        :rtype: bool
        """
        return self._hide_at_showing

    @hide_at_showing.setter
    def hide_at_showing(self, hide_at_showing):
        """Sets the hide_at_showing of this VideoFrame.

        Determines whether a VideoFrame is hidden.   # noqa: E501

        :param hide_at_showing: The hide_at_showing of this VideoFrame.  # noqa: E501
        :type: bool
        """
        self._hide_at_showing = hide_at_showing

    @property
    def play_loop_mode(self):
        """Gets the play_loop_mode of this VideoFrame.  # noqa: E501

        Determines whether a video is looped.  # noqa: E501

        :return: The play_loop_mode of this VideoFrame.  # noqa: E501
        :rtype: bool
        """
        return self._play_loop_mode

    @play_loop_mode.setter
    def play_loop_mode(self, play_loop_mode):
        """Sets the play_loop_mode of this VideoFrame.

        Determines whether a video is looped.  # noqa: E501

        :param play_loop_mode: The play_loop_mode of this VideoFrame.  # noqa: E501
        :type: bool
        """
        self._play_loop_mode = play_loop_mode

    @property
    def play_mode(self):
        """Gets the play_mode of this VideoFrame.  # noqa: E501

        Returns or sets the video play mode.    # noqa: E501

        :return: The play_mode of this VideoFrame.  # noqa: E501
        :rtype: str
        """
        return self._play_mode

    @play_mode.setter
    def play_mode(self, play_mode):
        """Sets the play_mode of this VideoFrame.

        Returns or sets the video play mode.    # noqa: E501

        :param play_mode: The play_mode of this VideoFrame.  # noqa: E501
        :type: str
        """
        if play_mode is not None:
            allowed_values = ["Auto", "OnClick", "AllSlides", "Mixed"]  # noqa: E501
            if play_mode not in allowed_values:
                raise ValueError(
                    "Invalid value for `play_mode` ({0}), must be one of {1}"  # noqa: E501
                    .format(play_mode, allowed_values)
                )
        self._play_mode = play_mode

    @property
    def rewind_video(self):
        """Gets the rewind_video of this VideoFrame.  # noqa: E501

        Determines whether a video is automatically rewinded to start as soon as the movie has finished playing  # noqa: E501

        :return: The rewind_video of this VideoFrame.  # noqa: E501
        :rtype: bool
        """
        return self._rewind_video

    @rewind_video.setter
    def rewind_video(self, rewind_video):
        """Sets the rewind_video of this VideoFrame.

        Determines whether a video is automatically rewinded to start as soon as the movie has finished playing  # noqa: E501

        :param rewind_video: The rewind_video of this VideoFrame.  # noqa: E501
        :type: bool
        """
        self._rewind_video = rewind_video

    @property
    def volume(self):
        """Gets the volume of this VideoFrame.  # noqa: E501

        Returns or sets the audio volume.  # noqa: E501

        :return: The volume of this VideoFrame.  # noqa: E501
        :rtype: str
        """
        return self._volume

    @volume.setter
    def volume(self, volume):
        """Sets the volume of this VideoFrame.

        Returns or sets the audio volume.  # noqa: E501

        :param volume: The volume of this VideoFrame.  # noqa: E501
        :type: str
        """
        if volume is not None:
            allowed_values = ["Mute", "Low", "Medium", "Loud", "Mixed"]  # noqa: E501
            if volume not in allowed_values:
                raise ValueError(
                    "Invalid value for `volume` ({0}), must be one of {1}"  # noqa: E501
                    .format(volume, allowed_values)
                )
        self._volume = volume

    @property
    def base64_data(self):
        """Gets the base64_data of this VideoFrame.  # noqa: E501

        Video data encoded in base64.  # noqa: E501

        :return: The base64_data of this VideoFrame.  # noqa: E501
        :rtype: str
        """
        return self._base64_data

    @base64_data.setter
    def base64_data(self, base64_data):
        """Sets the base64_data of this VideoFrame.

        Video data encoded in base64.  # noqa: E501

        :param base64_data: The base64_data of this VideoFrame.  # noqa: E501
        :type: str
        """
        self._base64_data = base64_data

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
        if not isinstance(other, VideoFrame):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
