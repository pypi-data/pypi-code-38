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


class Effect(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'type': 'str',
        'subtype': 'str',
        'preset_class_type': 'str',
        'shape_index': 'int',
        'trigger_type': 'str',
        'accelerate': 'float',
        'auto_reverse': 'bool',
        'decelerate': 'float',
        'duration': 'float',
        'repeat_count': 'float',
        'repeat_duration': 'float',
        'restart': 'str',
        'speed': 'float',
        'trigger_delay_time': 'float'
    }

    attribute_map = {
        'type': 'Type',
        'subtype': 'Subtype',
        'preset_class_type': 'PresetClassType',
        'shape_index': 'ShapeIndex',
        'trigger_type': 'TriggerType',
        'accelerate': 'Accelerate',
        'auto_reverse': 'AutoReverse',
        'decelerate': 'Decelerate',
        'duration': 'Duration',
        'repeat_count': 'RepeatCount',
        'repeat_duration': 'RepeatDuration',
        'restart': 'Restart',
        'speed': 'Speed',
        'trigger_delay_time': 'TriggerDelayTime'
    }

    def __init__(self, type=None, subtype=None, preset_class_type=None, shape_index=None, trigger_type=None, accelerate=None, auto_reverse=None, decelerate=None, duration=None, repeat_count=None, repeat_duration=None, restart=None, speed=None, trigger_delay_time=None):  # noqa: E501
        """Effect - a model defined in Swagger"""  # noqa: E501

        self._type = None
        self._subtype = None
        self._preset_class_type = None
        self._shape_index = None
        self._trigger_type = None
        self._accelerate = None
        self._auto_reverse = None
        self._decelerate = None
        self._duration = None
        self._repeat_count = None
        self._repeat_duration = None
        self._restart = None
        self._speed = None
        self._trigger_delay_time = None

        if type is not None:
            self.type = type
        if subtype is not None:
            self.subtype = subtype
        if preset_class_type is not None:
            self.preset_class_type = preset_class_type
        self.shape_index = shape_index
        if trigger_type is not None:
            self.trigger_type = trigger_type
        if accelerate is not None:
            self.accelerate = accelerate
        if auto_reverse is not None:
            self.auto_reverse = auto_reverse
        if decelerate is not None:
            self.decelerate = decelerate
        if duration is not None:
            self.duration = duration
        if repeat_count is not None:
            self.repeat_count = repeat_count
        if repeat_duration is not None:
            self.repeat_duration = repeat_duration
        if restart is not None:
            self.restart = restart
        if speed is not None:
            self.speed = speed
        if trigger_delay_time is not None:
            self.trigger_delay_time = trigger_delay_time

    @property
    def type(self):
        """Gets the type of this Effect.  # noqa: E501

        Effect type.  # noqa: E501

        :return: The type of this Effect.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Effect.

        Effect type.  # noqa: E501

        :param type: The type of this Effect.  # noqa: E501
        :type: str
        """
        if type is not None:
            allowed_values = ["Appear", "CurveUpDown", "Ascend", "Blast", "Blinds", "Blink", "BoldFlash", "BoldReveal", "Boomerang", "Bounce", "Box", "BrushOnColor", "BrushOnUnderline", "CenterRevolve", "ChangeFillColor", "ChangeFont", "ChangeFontColor", "ChangeFontSize", "ChangeFontStyle", "ChangeLineColor", "Checkerboard", "Circle", "ColorBlend", "ColorTypewriter", "ColorWave", "ComplementaryColor", "ComplementaryColor2", "Compress", "ContrastingColor", "Crawl", "Credits", "Custom", "Darken", "Desaturate", "Descend", "Diamond", "Dissolve", "EaseInOut", "Expand", "Fade", "FadedSwivel", "FadedZoom", "FlashBulb", "FlashOnce", "Flicker", "Flip", "Float", "Fly", "Fold", "Glide", "GrowAndTurn", "GrowShrink", "GrowWithColor", "Lighten", "LightSpeed", "MediaPause", "MediaPlay", "MediaStop", "Path4PointStar", "Path5PointStar", "Path6PointStar", "Path8PointStar", "PathArcDown", "PathArcLeft", "PathArcRight", "PathArcUp", "PathBean", "PathBounceLeft", "PathBounceRight", "PathBuzzsaw", "PathCircle", "PathCrescentMoon", "PathCurvedSquare", "PathCurvedX", "PathCurvyLeft", "PathCurvyRight", "PathCurvyStar", "PathDecayingWave", "PathDiagonalDownRight", "PathDiagonalUpRight", "PathDiamond", "PathDown", "PathEqualTriangle", "PathFigure8Four", "PathFootball", "PathFunnel", "PathHeart", "PathHeartbeat", "PathHexagon", "PathHorizontalFigure8", "PathInvertedSquare", "PathInvertedTriangle", "PathLeft", "PathLoopdeLoop", "PathNeutron", "PathOctagon", "PathParallelogram", "PathPeanut", "PathPentagon", "PathPlus", "PathPointyStar", "PathRight", "PathRightTriangle", "PathSCurve1", "PathSCurve2", "PathSineWave", "PathSpiralLeft", "PathSpiralRight", "PathSpring", "PathSquare", "PathStairsDown", "PathSwoosh", "PathTeardrop", "PathTrapezoid", "PathTurnDown", "PathTurnRight", "PathTurnUp", "PathTurnUpRight", "PathUp", "PathUser", "PathVerticalFigure8", "PathWave", "PathZigzag", "Peek", "Pinwheel", "Plus", "RandomBars", "RandomEffects", "RiseUp", "Shimmer", "Sling", "Spin", "Spinner", "Spiral", "Split", "Stretch", "Strips", "StyleEmphasis", "Swish", "Swivel", "Teeter", "Thread", "Transparency", "Unfold", "VerticalGrow", "Wave", "Wedge", "Wheel", "Whip", "Wipe", "Magnify", "Zoom", "OLEObjectShow", "OLEObjectEdit", "OLEObjectOpen"]  # noqa: E501
            if type not in allowed_values:
                raise ValueError(
                    "Invalid value for `type` ({0}), must be one of {1}"  # noqa: E501
                    .format(type, allowed_values)
                )
        self._type = type

    @property
    def subtype(self):
        """Gets the subtype of this Effect.  # noqa: E501

        Effect subtype.  # noqa: E501

        :return: The subtype of this Effect.  # noqa: E501
        :rtype: str
        """
        return self._subtype

    @subtype.setter
    def subtype(self, subtype):
        """Sets the subtype of this Effect.

        Effect subtype.  # noqa: E501

        :param subtype: The subtype of this Effect.  # noqa: E501
        :type: str
        """
        if subtype is not None:
            allowed_values = ["None", "Across", "Bottom", "BottomLeft", "BottomRight", "Center", "Clockwise", "CounterClockwise", "GradualAndCycleClockwise", "GradualAndCycleCounterClockwise", "Down", "DownLeft", "DownRight", "FontAllCaps", "FontBold", "FontItalic", "FontShadow", "FontStrikethrough", "FontUnderline", "Gradual", "Horizontal", "HorizontalIn", "HorizontalOut", "In", "InBottom", "InCenter", "InSlightly", "Instant", "Left", "OrdinalMask", "Out", "OutBottom", "OutCenter", "OutSlightly", "Right", "Slightly", "Top", "TopLeft", "TopRight", "Up", "UpLeft", "UpRight", "Vertical", "VerticalIn", "VerticalOut", "Wheel1", "Wheel2", "Wheel3", "Wheel4", "Wheel8"]  # noqa: E501
            if subtype not in allowed_values:
                raise ValueError(
                    "Invalid value for `subtype` ({0}), must be one of {1}"  # noqa: E501
                    .format(subtype, allowed_values)
                )
        self._subtype = subtype

    @property
    def preset_class_type(self):
        """Gets the preset_class_type of this Effect.  # noqa: E501

        Preset class type.  # noqa: E501

        :return: The preset_class_type of this Effect.  # noqa: E501
        :rtype: str
        """
        return self._preset_class_type

    @preset_class_type.setter
    def preset_class_type(self, preset_class_type):
        """Sets the preset_class_type of this Effect.

        Preset class type.  # noqa: E501

        :param preset_class_type: The preset_class_type of this Effect.  # noqa: E501
        :type: str
        """
        if preset_class_type is not None:
            allowed_values = ["Entrance", "Exit", "Emphasis", "Path", "MediaCall", "OLEActionVerbs"]  # noqa: E501
            if preset_class_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `preset_class_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(preset_class_type, allowed_values)
                )
        self._preset_class_type = preset_class_type

    @property
    def shape_index(self):
        """Gets the shape_index of this Effect.  # noqa: E501

        Shape index.  # noqa: E501

        :return: The shape_index of this Effect.  # noqa: E501
        :rtype: int
        """
        return self._shape_index

    @shape_index.setter
    def shape_index(self, shape_index):
        """Sets the shape_index of this Effect.

        Shape index.  # noqa: E501

        :param shape_index: The shape_index of this Effect.  # noqa: E501
        :type: int
        """
        self._shape_index = shape_index

    @property
    def trigger_type(self):
        """Gets the trigger_type of this Effect.  # noqa: E501

        Effect trigger type.  # noqa: E501

        :return: The trigger_type of this Effect.  # noqa: E501
        :rtype: str
        """
        return self._trigger_type

    @trigger_type.setter
    def trigger_type(self, trigger_type):
        """Sets the trigger_type of this Effect.

        Effect trigger type.  # noqa: E501

        :param trigger_type: The trigger_type of this Effect.  # noqa: E501
        :type: str
        """
        if trigger_type is not None:
            allowed_values = ["AfterPrevious", "OnClick", "WithPrevious"]  # noqa: E501
            if trigger_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `trigger_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(trigger_type, allowed_values)
                )
        self._trigger_type = trigger_type

    @property
    def accelerate(self):
        """Gets the accelerate of this Effect.  # noqa: E501

        The percentage of duration accelerate behavior effect.  # noqa: E501

        :return: The accelerate of this Effect.  # noqa: E501
        :rtype: float
        """
        return self._accelerate

    @accelerate.setter
    def accelerate(self, accelerate):
        """Sets the accelerate of this Effect.

        The percentage of duration accelerate behavior effect.  # noqa: E501

        :param accelerate: The accelerate of this Effect.  # noqa: E501
        :type: float
        """
        self._accelerate = accelerate

    @property
    def auto_reverse(self):
        """Gets the auto_reverse of this Effect.  # noqa: E501

        True to automatically play the animation in reverse after playing it in the forward direction.  # noqa: E501

        :return: The auto_reverse of this Effect.  # noqa: E501
        :rtype: bool
        """
        return self._auto_reverse

    @auto_reverse.setter
    def auto_reverse(self, auto_reverse):
        """Sets the auto_reverse of this Effect.

        True to automatically play the animation in reverse after playing it in the forward direction.  # noqa: E501

        :param auto_reverse: The auto_reverse of this Effect.  # noqa: E501
        :type: bool
        """
        self._auto_reverse = auto_reverse

    @property
    def decelerate(self):
        """Gets the decelerate of this Effect.  # noqa: E501

        The percentage of duration decelerate behavior effect.  # noqa: E501

        :return: The decelerate of this Effect.  # noqa: E501
        :rtype: float
        """
        return self._decelerate

    @decelerate.setter
    def decelerate(self, decelerate):
        """Sets the decelerate of this Effect.

        The percentage of duration decelerate behavior effect.  # noqa: E501

        :param decelerate: The decelerate of this Effect.  # noqa: E501
        :type: float
        """
        self._decelerate = decelerate

    @property
    def duration(self):
        """Gets the duration of this Effect.  # noqa: E501

        The duration of animation effect.  # noqa: E501

        :return: The duration of this Effect.  # noqa: E501
        :rtype: float
        """
        return self._duration

    @duration.setter
    def duration(self, duration):
        """Sets the duration of this Effect.

        The duration of animation effect.  # noqa: E501

        :param duration: The duration of this Effect.  # noqa: E501
        :type: float
        """
        self._duration = duration

    @property
    def repeat_count(self):
        """Gets the repeat_count of this Effect.  # noqa: E501

        The number of times the effect should repeat.  # noqa: E501

        :return: The repeat_count of this Effect.  # noqa: E501
        :rtype: float
        """
        return self._repeat_count

    @repeat_count.setter
    def repeat_count(self, repeat_count):
        """Sets the repeat_count of this Effect.

        The number of times the effect should repeat.  # noqa: E501

        :param repeat_count: The repeat_count of this Effect.  # noqa: E501
        :type: float
        """
        self._repeat_count = repeat_count

    @property
    def repeat_duration(self):
        """Gets the repeat_duration of this Effect.  # noqa: E501

        The number of times the effect should repeat.  # noqa: E501

        :return: The repeat_duration of this Effect.  # noqa: E501
        :rtype: float
        """
        return self._repeat_duration

    @repeat_duration.setter
    def repeat_duration(self, repeat_duration):
        """Sets the repeat_duration of this Effect.

        The number of times the effect should repeat.  # noqa: E501

        :param repeat_duration: The repeat_duration of this Effect.  # noqa: E501
        :type: float
        """
        self._repeat_duration = repeat_duration

    @property
    def restart(self):
        """Gets the restart of this Effect.  # noqa: E501

        The way for a effect to restart after complete.  # noqa: E501

        :return: The restart of this Effect.  # noqa: E501
        :rtype: str
        """
        return self._restart

    @restart.setter
    def restart(self, restart):
        """Sets the restart of this Effect.

        The way for a effect to restart after complete.  # noqa: E501

        :param restart: The restart of this Effect.  # noqa: E501
        :type: str
        """
        if restart is not None:
            allowed_values = ["Always", "WhenNotActive", "Never", "NotDefined"]  # noqa: E501
            if restart not in allowed_values:
                raise ValueError(
                    "Invalid value for `restart` ({0}), must be one of {1}"  # noqa: E501
                    .format(restart, allowed_values)
                )
        self._restart = restart

    @property
    def speed(self):
        """Gets the speed of this Effect.  # noqa: E501

        The percentage by which to speed up (or slow down) the timing.  # noqa: E501

        :return: The speed of this Effect.  # noqa: E501
        :rtype: float
        """
        return self._speed

    @speed.setter
    def speed(self, speed):
        """Sets the speed of this Effect.

        The percentage by which to speed up (or slow down) the timing.  # noqa: E501

        :param speed: The speed of this Effect.  # noqa: E501
        :type: float
        """
        self._speed = speed

    @property
    def trigger_delay_time(self):
        """Gets the trigger_delay_time of this Effect.  # noqa: E501

        Delay time after trigger.  # noqa: E501

        :return: The trigger_delay_time of this Effect.  # noqa: E501
        :rtype: float
        """
        return self._trigger_delay_time

    @trigger_delay_time.setter
    def trigger_delay_time(self, trigger_delay_time):
        """Sets the trigger_delay_time of this Effect.

        Delay time after trigger.  # noqa: E501

        :param trigger_delay_time: The trigger_delay_time of this Effect.  # noqa: E501
        :type: float
        """
        self._trigger_delay_time = trigger_delay_time

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
        if not isinstance(other, Effect):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
