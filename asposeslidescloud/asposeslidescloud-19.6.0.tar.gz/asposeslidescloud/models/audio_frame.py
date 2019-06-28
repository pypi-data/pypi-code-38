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

class AudioFrame(GeometryShape):


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
        'audio_cd_end_track': 'int',
        'audio_cd_end_track_time': 'int',
        'audio_cd_start_track': 'int',
        'audio_cd_start_track_time': 'int',
        'embedded': 'bool',
        'hide_at_showing': 'bool',
        'play_loop_mode': 'bool',
        'play_mode': 'str',
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
        'audio_cd_end_track': 'AudioCdEndTrack',
        'audio_cd_end_track_time': 'AudioCdEndTrackTime',
        'audio_cd_start_track': 'AudioCdStartTrack',
        'audio_cd_start_track_time': 'AudioCdStartTrackTime',
        'embedded': 'Embedded',
        'hide_at_showing': 'HideAtShowing',
        'play_loop_mode': 'PlayLoopMode',
        'play_mode': 'PlayMode',
        'volume': 'Volume',
        'base64_data': 'Base64Data'
    }

    def __init__(self, self_uri=None, alternate_links=None, name=None, width=None, height=None, alternative_text=None, hidden=None, x=None, y=None, z_order_position=None, shapes=None, fill_format=None, effect_format=None, line_format=None, type='AudioFrame', shape_type='AudioFrame', geometry_shape_type=None, audio_cd_end_track=None, audio_cd_end_track_time=None, audio_cd_start_track=None, audio_cd_start_track_time=None, embedded=None, hide_at_showing=None, play_loop_mode=None, play_mode=None, volume=None, base64_data=None):  # noqa: E501
        """AudioFrame - a model defined in Swagger"""  # noqa: E501
        super(AudioFrame, self).__init__(self_uri, alternate_links, name, width, height, alternative_text, hidden, x, y, z_order_position, shapes, fill_format, effect_format, line_format, type, shape_type, geometry_shape_type)

        self._audio_cd_end_track = None
        self._audio_cd_end_track_time = None
        self._audio_cd_start_track = None
        self._audio_cd_start_track_time = None
        self._embedded = None
        self._hide_at_showing = None
        self._play_loop_mode = None
        self._play_mode = None
        self._volume = None
        self._base64_data = None

        if audio_cd_end_track is not None:
            self.audio_cd_end_track = audio_cd_end_track
        if audio_cd_end_track_time is not None:
            self.audio_cd_end_track_time = audio_cd_end_track_time
        if audio_cd_start_track is not None:
            self.audio_cd_start_track = audio_cd_start_track
        if audio_cd_start_track_time is not None:
            self.audio_cd_start_track_time = audio_cd_start_track_time
        if embedded is not None:
            self.embedded = embedded
        if hide_at_showing is not None:
            self.hide_at_showing = hide_at_showing
        if play_loop_mode is not None:
            self.play_loop_mode = play_loop_mode
        if play_mode is not None:
            self.play_mode = play_mode
        if volume is not None:
            self.volume = volume
        if base64_data is not None:
            self.base64_data = base64_data

    @property
    def audio_cd_end_track(self):
        """Gets the audio_cd_end_track of this AudioFrame.  # noqa: E501

        Returns or sets a last track index.  # noqa: E501

        :return: The audio_cd_end_track of this AudioFrame.  # noqa: E501
        :rtype: int
        """
        return self._audio_cd_end_track

    @audio_cd_end_track.setter
    def audio_cd_end_track(self, audio_cd_end_track):
        """Sets the audio_cd_end_track of this AudioFrame.

        Returns or sets a last track index.  # noqa: E501

        :param audio_cd_end_track: The audio_cd_end_track of this AudioFrame.  # noqa: E501
        :type: int
        """
        self._audio_cd_end_track = audio_cd_end_track

    @property
    def audio_cd_end_track_time(self):
        """Gets the audio_cd_end_track_time of this AudioFrame.  # noqa: E501

        Returns or sets a last track time.  # noqa: E501

        :return: The audio_cd_end_track_time of this AudioFrame.  # noqa: E501
        :rtype: int
        """
        return self._audio_cd_end_track_time

    @audio_cd_end_track_time.setter
    def audio_cd_end_track_time(self, audio_cd_end_track_time):
        """Sets the audio_cd_end_track_time of this AudioFrame.

        Returns or sets a last track time.  # noqa: E501

        :param audio_cd_end_track_time: The audio_cd_end_track_time of this AudioFrame.  # noqa: E501
        :type: int
        """
        self._audio_cd_end_track_time = audio_cd_end_track_time

    @property
    def audio_cd_start_track(self):
        """Gets the audio_cd_start_track of this AudioFrame.  # noqa: E501

        Returns or sets a start track index.  # noqa: E501

        :return: The audio_cd_start_track of this AudioFrame.  # noqa: E501
        :rtype: int
        """
        return self._audio_cd_start_track

    @audio_cd_start_track.setter
    def audio_cd_start_track(self, audio_cd_start_track):
        """Sets the audio_cd_start_track of this AudioFrame.

        Returns or sets a start track index.  # noqa: E501

        :param audio_cd_start_track: The audio_cd_start_track of this AudioFrame.  # noqa: E501
        :type: int
        """
        self._audio_cd_start_track = audio_cd_start_track

    @property
    def audio_cd_start_track_time(self):
        """Gets the audio_cd_start_track_time of this AudioFrame.  # noqa: E501

        Returns or sets a start track time.   # noqa: E501

        :return: The audio_cd_start_track_time of this AudioFrame.  # noqa: E501
        :rtype: int
        """
        return self._audio_cd_start_track_time

    @audio_cd_start_track_time.setter
    def audio_cd_start_track_time(self, audio_cd_start_track_time):
        """Sets the audio_cd_start_track_time of this AudioFrame.

        Returns or sets a start track time.   # noqa: E501

        :param audio_cd_start_track_time: The audio_cd_start_track_time of this AudioFrame.  # noqa: E501
        :type: int
        """
        self._audio_cd_start_track_time = audio_cd_start_track_time

    @property
    def embedded(self):
        """Gets the embedded of this AudioFrame.  # noqa: E501

        Determines whether a sound is embedded to a presentation.  # noqa: E501

        :return: The embedded of this AudioFrame.  # noqa: E501
        :rtype: bool
        """
        return self._embedded

    @embedded.setter
    def embedded(self, embedded):
        """Sets the embedded of this AudioFrame.

        Determines whether a sound is embedded to a presentation.  # noqa: E501

        :param embedded: The embedded of this AudioFrame.  # noqa: E501
        :type: bool
        """
        self._embedded = embedded

    @property
    def hide_at_showing(self):
        """Gets the hide_at_showing of this AudioFrame.  # noqa: E501

        Determines whether an AudioFrame is hidden.  # noqa: E501

        :return: The hide_at_showing of this AudioFrame.  # noqa: E501
        :rtype: bool
        """
        return self._hide_at_showing

    @hide_at_showing.setter
    def hide_at_showing(self, hide_at_showing):
        """Sets the hide_at_showing of this AudioFrame.

        Determines whether an AudioFrame is hidden.  # noqa: E501

        :param hide_at_showing: The hide_at_showing of this AudioFrame.  # noqa: E501
        :type: bool
        """
        self._hide_at_showing = hide_at_showing

    @property
    def play_loop_mode(self):
        """Gets the play_loop_mode of this AudioFrame.  # noqa: E501

        Determines whether an audio is looped.   # noqa: E501

        :return: The play_loop_mode of this AudioFrame.  # noqa: E501
        :rtype: bool
        """
        return self._play_loop_mode

    @play_loop_mode.setter
    def play_loop_mode(self, play_loop_mode):
        """Sets the play_loop_mode of this AudioFrame.

        Determines whether an audio is looped.   # noqa: E501

        :param play_loop_mode: The play_loop_mode of this AudioFrame.  # noqa: E501
        :type: bool
        """
        self._play_loop_mode = play_loop_mode

    @property
    def play_mode(self):
        """Gets the play_mode of this AudioFrame.  # noqa: E501

        Returns or sets the audio play mode.  # noqa: E501

        :return: The play_mode of this AudioFrame.  # noqa: E501
        :rtype: str
        """
        return self._play_mode

    @play_mode.setter
    def play_mode(self, play_mode):
        """Sets the play_mode of this AudioFrame.

        Returns or sets the audio play mode.  # noqa: E501

        :param play_mode: The play_mode of this AudioFrame.  # noqa: E501
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
    def volume(self):
        """Gets the volume of this AudioFrame.  # noqa: E501

        Returns or sets the audio volume.  # noqa: E501

        :return: The volume of this AudioFrame.  # noqa: E501
        :rtype: str
        """
        return self._volume

    @volume.setter
    def volume(self, volume):
        """Sets the volume of this AudioFrame.

        Returns or sets the audio volume.  # noqa: E501

        :param volume: The volume of this AudioFrame.  # noqa: E501
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
        """Gets the base64_data of this AudioFrame.  # noqa: E501

        Audio data encoded in base64.  # noqa: E501

        :return: The base64_data of this AudioFrame.  # noqa: E501
        :rtype: str
        """
        return self._base64_data

    @base64_data.setter
    def base64_data(self, base64_data):
        """Sets the base64_data of this AudioFrame.

        Audio data encoded in base64.  # noqa: E501

        :param base64_data: The base64_data of this AudioFrame.  # noqa: E501
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
        if not isinstance(other, AudioFrame):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
