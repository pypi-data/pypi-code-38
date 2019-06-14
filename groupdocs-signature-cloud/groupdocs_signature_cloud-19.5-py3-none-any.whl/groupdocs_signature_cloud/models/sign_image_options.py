# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="SignImageOptions.py">
#   Copyright (c) 2003-2019 Aspose Pty Ltd
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

from groupdocs_signature_cloud.models import SignOptions

class SignImageOptions(SignOptions):
    """
    Represents the Image sign options
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'image_guid': 'str',
        'left': 'int',
        'top': 'int',
        'width': 'int',
        'height': 'int',
        'location_measure_type': 'str',
        'size_measure_type': 'str',
        'rotation_angle': 'int',
        'horizontal_alignment': 'str',
        'vertical_alignment': 'str',
        'margin': 'Padding',
        'margin_measure_type': 'str',
        'opacity': 'float'
    }

    attribute_map = {
        'image_guid': 'ImageGuid',
        'left': 'Left',
        'top': 'Top',
        'width': 'Width',
        'height': 'Height',
        'location_measure_type': 'LocationMeasureType',
        'size_measure_type': 'SizeMeasureType',
        'rotation_angle': 'RotationAngle',
        'horizontal_alignment': 'HorizontalAlignment',
        'vertical_alignment': 'VerticalAlignment',
        'margin': 'Margin',
        'margin_measure_type': 'MarginMeasureType',
        'opacity': 'Opacity'
    }

    def __init__(self, image_guid=None, left=None, top=None, width=None, height=None, location_measure_type=None, size_measure_type=None, rotation_angle=None, horizontal_alignment=None, vertical_alignment=None, margin=None, margin_measure_type=None, opacity=None, **kwargs):  # noqa: E501
        """Initializes new instance of SignImageOptions"""  # noqa: E501

        self._image_guid = None
        self._left = None
        self._top = None
        self._width = None
        self._height = None
        self._location_measure_type = None
        self._size_measure_type = None
        self._rotation_angle = None
        self._horizontal_alignment = None
        self._vertical_alignment = None
        self._margin = None
        self._margin_measure_type = None
        self._opacity = None

        if image_guid is not None:
            self.image_guid = image_guid
        if left is not None:
            self.left = left
        if top is not None:
            self.top = top
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if location_measure_type is not None:
            self.location_measure_type = location_measure_type
        if size_measure_type is not None:
            self.size_measure_type = size_measure_type
        if rotation_angle is not None:
            self.rotation_angle = rotation_angle
        if horizontal_alignment is not None:
            self.horizontal_alignment = horizontal_alignment
        if vertical_alignment is not None:
            self.vertical_alignment = vertical_alignment
        if margin is not None:
            self.margin = margin
        if margin_measure_type is not None:
            self.margin_measure_type = margin_measure_type
        if opacity is not None:
            self.opacity = opacity

        base = super(SignImageOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def image_guid(self):
        """
        Gets the image_guid.  # noqa: E501

        Gets or sets the signature image file name. This property is used only if ImageStream is not specified  # noqa: E501

        :return: The image_guid.  # noqa: E501
        :rtype: str
        """
        return self._image_guid

    @image_guid.setter
    def image_guid(self, image_guid):
        """
        Sets the image_guid.

        Gets or sets the signature image file name. This property is used only if ImageStream is not specified  # noqa: E501

        :param image_guid: The image_guid.  # noqa: E501
        :type: str
        """
        self._image_guid = image_guid
    
    @property
    def left(self):
        """
        Gets the left.  # noqa: E501

        Left X position of Signature on Document Page in Measure values (pixels or percent see MeasureType LocationMeasureType). (works if horizontal alignment is not specified). For Spreadsheet documents this property is mutually exclusive with Column property. If Left property is set ColumnNumber will be reset to 0  # noqa: E501

        :return: The left.  # noqa: E501
        :rtype: int
        """
        return self._left

    @left.setter
    def left(self, left):
        """
        Sets the left.

        Left X position of Signature on Document Page in Measure values (pixels or percent see MeasureType LocationMeasureType). (works if horizontal alignment is not specified). For Spreadsheet documents this property is mutually exclusive with Column property. If Left property is set ColumnNumber will be reset to 0  # noqa: E501

        :param left: The left.  # noqa: E501
        :type: int
        """
        if left is None:
            raise ValueError("Invalid value for `left`, must not be `None`")  # noqa: E501
        self._left = left
    
    @property
    def top(self):
        """
        Gets the top.  # noqa: E501

        Top Y Position of Signature on Document Page in Measure values (pixels or percent see MeasureType LocationMeasureType). (works if vertical alignment is not specified). For Spreadsheet documents this property is mutually exclusive with Row property. If Top property is set RowNumber will be reset to 0  # noqa: E501

        :return: The top.  # noqa: E501
        :rtype: int
        """
        return self._top

    @top.setter
    def top(self, top):
        """
        Sets the top.

        Top Y Position of Signature on Document Page in Measure values (pixels or percent see MeasureType LocationMeasureType). (works if vertical alignment is not specified). For Spreadsheet documents this property is mutually exclusive with Row property. If Top property is set RowNumber will be reset to 0  # noqa: E501

        :param top: The top.  # noqa: E501
        :type: int
        """
        if top is None:
            raise ValueError("Invalid value for `top`, must not be `None`")  # noqa: E501
        self._top = top
    
    @property
    def width(self):
        """
        Gets the width.  # noqa: E501

        Width of Signature on Document Page in Measure values (pixels or percent see MeasureType SizeMeasureType)  # noqa: E501

        :return: The width.  # noqa: E501
        :rtype: int
        """
        return self._width

    @width.setter
    def width(self, width):
        """
        Sets the width.

        Width of Signature on Document Page in Measure values (pixels or percent see MeasureType SizeMeasureType)  # noqa: E501

        :param width: The width.  # noqa: E501
        :type: int
        """
        if width is None:
            raise ValueError("Invalid value for `width`, must not be `None`")  # noqa: E501
        self._width = width
    
    @property
    def height(self):
        """
        Gets the height.  # noqa: E501

        Height of Signature on Document Page in Measure values (pixels or percent see MeasureType SizeMeasureType)  # noqa: E501

        :return: The height.  # noqa: E501
        :rtype: int
        """
        return self._height

    @height.setter
    def height(self, height):
        """
        Sets the height.

        Height of Signature on Document Page in Measure values (pixels or percent see MeasureType SizeMeasureType)  # noqa: E501

        :param height: The height.  # noqa: E501
        :type: int
        """
        if height is None:
            raise ValueError("Invalid value for `height`, must not be `None`")  # noqa: E501
        self._height = height
    
    @property
    def location_measure_type(self):
        """
        Gets the location_measure_type.  # noqa: E501

        Measure type (pixels or percent) for Left and Top properties  # noqa: E501

        :return: The location_measure_type.  # noqa: E501
        :rtype: str
        """
        return self._location_measure_type

    @location_measure_type.setter
    def location_measure_type(self, location_measure_type):
        """
        Sets the location_measure_type.

        Measure type (pixels or percent) for Left and Top properties  # noqa: E501

        :param location_measure_type: The location_measure_type.  # noqa: E501
        :type: str
        """
        if location_measure_type is None:
            raise ValueError("Invalid value for `location_measure_type`, must not be `None`")  # noqa: E501
        allowed_values = ["Pixels", "Percents", "Millimeters"]  # noqa: E501
        if not location_measure_type.isdigit():	
            if location_measure_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `location_measure_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(location_measure_type, allowed_values))
            self._location_measure_type = location_measure_type
        else:
            self._location_measure_type = allowed_values[int(location_measure_type) if six.PY3 else long(location_measure_type)]
    
    @property
    def size_measure_type(self):
        """
        Gets the size_measure_type.  # noqa: E501

        Measure type (pixels or percent) for Width and Height properties  # noqa: E501

        :return: The size_measure_type.  # noqa: E501
        :rtype: str
        """
        return self._size_measure_type

    @size_measure_type.setter
    def size_measure_type(self, size_measure_type):
        """
        Sets the size_measure_type.

        Measure type (pixels or percent) for Width and Height properties  # noqa: E501

        :param size_measure_type: The size_measure_type.  # noqa: E501
        :type: str
        """
        if size_measure_type is None:
            raise ValueError("Invalid value for `size_measure_type`, must not be `None`")  # noqa: E501
        allowed_values = ["Pixels", "Percents", "Millimeters"]  # noqa: E501
        if not size_measure_type.isdigit():	
            if size_measure_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `size_measure_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(size_measure_type, allowed_values))
            self._size_measure_type = size_measure_type
        else:
            self._size_measure_type = allowed_values[int(size_measure_type) if six.PY3 else long(size_measure_type)]
    
    @property
    def rotation_angle(self):
        """
        Gets the rotation_angle.  # noqa: E501

        Rotation angle of signature on document page (clockwise)  # noqa: E501

        :return: The rotation_angle.  # noqa: E501
        :rtype: int
        """
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, rotation_angle):
        """
        Sets the rotation_angle.

        Rotation angle of signature on document page (clockwise)  # noqa: E501

        :param rotation_angle: The rotation_angle.  # noqa: E501
        :type: int
        """
        if rotation_angle is None:
            raise ValueError("Invalid value for `rotation_angle`, must not be `None`")  # noqa: E501
        self._rotation_angle = rotation_angle
    
    @property
    def horizontal_alignment(self):
        """
        Gets the horizontal_alignment.  # noqa: E501

        Horizontal alignment of signature on document page  # noqa: E501

        :return: The horizontal_alignment.  # noqa: E501
        :rtype: str
        """
        return self._horizontal_alignment

    @horizontal_alignment.setter
    def horizontal_alignment(self, horizontal_alignment):
        """
        Sets the horizontal_alignment.

        Horizontal alignment of signature on document page  # noqa: E501

        :param horizontal_alignment: The horizontal_alignment.  # noqa: E501
        :type: str
        """
        if horizontal_alignment is None:
            raise ValueError("Invalid value for `horizontal_alignment`, must not be `None`")  # noqa: E501
        allowed_values = ["Default", "None", "Left", "Center", "Right"]  # noqa: E501
        if not horizontal_alignment.isdigit():	
            if horizontal_alignment not in allowed_values:
                raise ValueError(
                    "Invalid value for `horizontal_alignment` ({0}), must be one of {1}"  # noqa: E501
                    .format(horizontal_alignment, allowed_values))
            self._horizontal_alignment = horizontal_alignment
        else:
            self._horizontal_alignment = allowed_values[int(horizontal_alignment) if six.PY3 else long(horizontal_alignment)]
    
    @property
    def vertical_alignment(self):
        """
        Gets the vertical_alignment.  # noqa: E501

        Vertical alignment of signature on document page  # noqa: E501

        :return: The vertical_alignment.  # noqa: E501
        :rtype: str
        """
        return self._vertical_alignment

    @vertical_alignment.setter
    def vertical_alignment(self, vertical_alignment):
        """
        Sets the vertical_alignment.

        Vertical alignment of signature on document page  # noqa: E501

        :param vertical_alignment: The vertical_alignment.  # noqa: E501
        :type: str
        """
        if vertical_alignment is None:
            raise ValueError("Invalid value for `vertical_alignment`, must not be `None`")  # noqa: E501
        allowed_values = ["Default", "None", "Top", "Center", "Bottom"]  # noqa: E501
        if not vertical_alignment.isdigit():	
            if vertical_alignment not in allowed_values:
                raise ValueError(
                    "Invalid value for `vertical_alignment` ({0}), must be one of {1}"  # noqa: E501
                    .format(vertical_alignment, allowed_values))
            self._vertical_alignment = vertical_alignment
        else:
            self._vertical_alignment = allowed_values[int(vertical_alignment) if six.PY3 else long(vertical_alignment)]
    
    @property
    def margin(self):
        """
        Gets the margin.  # noqa: E501

        Gets or sets the space between Sign and Document edges (works ONLY if horizontal or vertical alignment are specified)  # noqa: E501

        :return: The margin.  # noqa: E501
        :rtype: Padding
        """
        return self._margin

    @margin.setter
    def margin(self, margin):
        """
        Sets the margin.

        Gets or sets the space between Sign and Document edges (works ONLY if horizontal or vertical alignment are specified)  # noqa: E501

        :param margin: The margin.  # noqa: E501
        :type: Padding
        """
        self._margin = margin
    
    @property
    def margin_measure_type(self):
        """
        Gets the margin_measure_type.  # noqa: E501

        Gets or sets the measure type (pixels or percent) for Margin  # noqa: E501

        :return: The margin_measure_type.  # noqa: E501
        :rtype: str
        """
        return self._margin_measure_type

    @margin_measure_type.setter
    def margin_measure_type(self, margin_measure_type):
        """
        Sets the margin_measure_type.

        Gets or sets the measure type (pixels or percent) for Margin  # noqa: E501

        :param margin_measure_type: The margin_measure_type.  # noqa: E501
        :type: str
        """
        if margin_measure_type is None:
            raise ValueError("Invalid value for `margin_measure_type`, must not be `None`")  # noqa: E501
        allowed_values = ["Pixels", "Percents", "Millimeters"]  # noqa: E501
        if not margin_measure_type.isdigit():	
            if margin_measure_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `margin_measure_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(margin_measure_type, allowed_values))
            self._margin_measure_type = margin_measure_type
        else:
            self._margin_measure_type = allowed_values[int(margin_measure_type) if six.PY3 else long(margin_measure_type)]
    
    @property
    def opacity(self):
        """
        Gets the opacity.  # noqa: E501

        Gets or sets the additional opacity for sign image (value from 0.0 (clear) through 1.0 (opaque)). By default the value is 1.0  # noqa: E501

        :return: The opacity.  # noqa: E501
        :rtype: float
        """
        return self._opacity

    @opacity.setter
    def opacity(self, opacity):
        """
        Sets the opacity.

        Gets or sets the additional opacity for sign image (value from 0.0 (clear) through 1.0 (opaque)). By default the value is 1.0  # noqa: E501

        :param opacity: The opacity.  # noqa: E501
        :type: float
        """
        if opacity is None:
            raise ValueError("Invalid value for `opacity`, must not be `None`")  # noqa: E501
        self._opacity = opacity

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
        if not isinstance(other, SignImageOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
