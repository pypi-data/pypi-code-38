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

class ShapeBase(ResourceBase):


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
        'shape_type': 'str'
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
        'shape_type': 'ShapeType'
    }

    def __init__(self, self_uri=None, alternate_links=None, name=None, width=None, height=None, alternative_text=None, hidden=None, x=None, y=None, z_order_position=None, shapes=None, fill_format=None, effect_format=None, line_format=None, type=None, shape_type=None):  # noqa: E501
        """ShapeBase - a model defined in Swagger"""  # noqa: E501
        super(ShapeBase, self).__init__(self_uri, alternate_links)

        self._name = None
        self._width = None
        self._height = None
        self._alternative_text = None
        self._hidden = None
        self._x = None
        self._y = None
        self._z_order_position = None
        self._shapes = None
        self._fill_format = None
        self._effect_format = None
        self._line_format = None
        self._type = None
        self._shape_type = None

        if name is not None:
            self.name = name
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if alternative_text is not None:
            self.alternative_text = alternative_text
        if hidden is not None:
            self.hidden = hidden
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.z_order_position = z_order_position
        if shapes is not None:
            self.shapes = shapes
        if fill_format is not None:
            self.fill_format = fill_format
        if effect_format is not None:
            self.effect_format = effect_format
        if line_format is not None:
            self.line_format = line_format
        if type is not None:
            self.type = type
        if shape_type is not None:
            self.shape_type = shape_type

    @property
    def name(self):
        """Gets the name of this ShapeBase.  # noqa: E501

        Gets or sets the name.  # noqa: E501

        :return: The name of this ShapeBase.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this ShapeBase.

        Gets or sets the name.  # noqa: E501

        :param name: The name of this ShapeBase.  # noqa: E501
        :type: str
        """
        self._name = name

    @property
    def width(self):
        """Gets the width of this ShapeBase.  # noqa: E501

        Gets or sets the width.  # noqa: E501

        :return: The width of this ShapeBase.  # noqa: E501
        :rtype: float
        """
        return self._width

    @width.setter
    def width(self, width):
        """Sets the width of this ShapeBase.

        Gets or sets the width.  # noqa: E501

        :param width: The width of this ShapeBase.  # noqa: E501
        :type: float
        """
        self._width = width

    @property
    def height(self):
        """Gets the height of this ShapeBase.  # noqa: E501

        Gets or sets the height.  # noqa: E501

        :return: The height of this ShapeBase.  # noqa: E501
        :rtype: float
        """
        return self._height

    @height.setter
    def height(self, height):
        """Sets the height of this ShapeBase.

        Gets or sets the height.  # noqa: E501

        :param height: The height of this ShapeBase.  # noqa: E501
        :type: float
        """
        self._height = height

    @property
    def alternative_text(self):
        """Gets the alternative_text of this ShapeBase.  # noqa: E501

        Gets or sets the alternative text.  # noqa: E501

        :return: The alternative_text of this ShapeBase.  # noqa: E501
        :rtype: str
        """
        return self._alternative_text

    @alternative_text.setter
    def alternative_text(self, alternative_text):
        """Sets the alternative_text of this ShapeBase.

        Gets or sets the alternative text.  # noqa: E501

        :param alternative_text: The alternative_text of this ShapeBase.  # noqa: E501
        :type: str
        """
        self._alternative_text = alternative_text

    @property
    def hidden(self):
        """Gets the hidden of this ShapeBase.  # noqa: E501

        Gets or sets a value indicating whether this ShapeBase is hidden.  # noqa: E501

        :return: The hidden of this ShapeBase.  # noqa: E501
        :rtype: bool
        """
        return self._hidden

    @hidden.setter
    def hidden(self, hidden):
        """Sets the hidden of this ShapeBase.

        Gets or sets a value indicating whether this ShapeBase is hidden.  # noqa: E501

        :param hidden: The hidden of this ShapeBase.  # noqa: E501
        :type: bool
        """
        self._hidden = hidden

    @property
    def x(self):
        """Gets the x of this ShapeBase.  # noqa: E501

        Gets or sets the X  # noqa: E501

        :return: The x of this ShapeBase.  # noqa: E501
        :rtype: float
        """
        return self._x

    @x.setter
    def x(self, x):
        """Sets the x of this ShapeBase.

        Gets or sets the X  # noqa: E501

        :param x: The x of this ShapeBase.  # noqa: E501
        :type: float
        """
        self._x = x

    @property
    def y(self):
        """Gets the y of this ShapeBase.  # noqa: E501

        Gets or sets the Y.  # noqa: E501

        :return: The y of this ShapeBase.  # noqa: E501
        :rtype: float
        """
        return self._y

    @y.setter
    def y(self, y):
        """Sets the y of this ShapeBase.

        Gets or sets the Y.  # noqa: E501

        :param y: The y of this ShapeBase.  # noqa: E501
        :type: float
        """
        self._y = y

    @property
    def z_order_position(self):
        """Gets the z_order_position of this ShapeBase.  # noqa: E501

        Gets z-order position of shape  # noqa: E501

        :return: The z_order_position of this ShapeBase.  # noqa: E501
        :rtype: int
        """
        return self._z_order_position

    @z_order_position.setter
    def z_order_position(self, z_order_position):
        """Sets the z_order_position of this ShapeBase.

        Gets z-order position of shape  # noqa: E501

        :param z_order_position: The z_order_position of this ShapeBase.  # noqa: E501
        :type: int
        """
        self._z_order_position = z_order_position

    @property
    def shapes(self):
        """Gets the shapes of this ShapeBase.  # noqa: E501

        Gets or sets the link to shapes.  # noqa: E501

        :return: The shapes of this ShapeBase.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._shapes

    @shapes.setter
    def shapes(self, shapes):
        """Sets the shapes of this ShapeBase.

        Gets or sets the link to shapes.  # noqa: E501

        :param shapes: The shapes of this ShapeBase.  # noqa: E501
        :type: ResourceUriElement
        """
        self._shapes = shapes

    @property
    def fill_format(self):
        """Gets the fill_format of this ShapeBase.  # noqa: E501

        Gets or sets the fill format.  # noqa: E501

        :return: The fill_format of this ShapeBase.  # noqa: E501
        :rtype: FillFormat
        """
        return self._fill_format

    @fill_format.setter
    def fill_format(self, fill_format):
        """Sets the fill_format of this ShapeBase.

        Gets or sets the fill format.  # noqa: E501

        :param fill_format: The fill_format of this ShapeBase.  # noqa: E501
        :type: FillFormat
        """
        self._fill_format = fill_format

    @property
    def effect_format(self):
        """Gets the effect_format of this ShapeBase.  # noqa: E501

        Gets or sets the effect format.  # noqa: E501

        :return: The effect_format of this ShapeBase.  # noqa: E501
        :rtype: EffectFormat
        """
        return self._effect_format

    @effect_format.setter
    def effect_format(self, effect_format):
        """Sets the effect_format of this ShapeBase.

        Gets or sets the effect format.  # noqa: E501

        :param effect_format: The effect_format of this ShapeBase.  # noqa: E501
        :type: EffectFormat
        """
        self._effect_format = effect_format

    @property
    def line_format(self):
        """Gets the line_format of this ShapeBase.  # noqa: E501

        Gets or sets the line format.  # noqa: E501

        :return: The line_format of this ShapeBase.  # noqa: E501
        :rtype: LineFormat
        """
        return self._line_format

    @line_format.setter
    def line_format(self, line_format):
        """Sets the line_format of this ShapeBase.

        Gets or sets the line format.  # noqa: E501

        :param line_format: The line_format of this ShapeBase.  # noqa: E501
        :type: LineFormat
        """
        self._line_format = line_format

    @property
    def type(self):
        """Gets the type of this ShapeBase.  # noqa: E501


        :return: The type of this ShapeBase.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this ShapeBase.


        :param type: The type of this ShapeBase.  # noqa: E501
        :type: str
        """
        if type is not None:
            allowed_values = ["Shape", "Chart", "Table", "PictureFrame", "VideoFrame", "AudioFrame", "SmartArt", "OleObjectFrame", "GroupShape", "GraphicalObject", "Connector", "SmartArtShape"]  # noqa: E501
            if type not in allowed_values:
                raise ValueError(
                    "Invalid value for `type` ({0}), must be one of {1}"  # noqa: E501
                    .format(type, allowed_values)
                )
        self._type = type

    @property
    def shape_type(self):
        """Gets the shape_type of this ShapeBase.  # noqa: E501


        :return: The shape_type of this ShapeBase.  # noqa: E501
        :rtype: str
        """
        return self._shape_type

    @shape_type.setter
    def shape_type(self, shape_type):
        """Sets the shape_type of this ShapeBase.


        :param shape_type: The shape_type of this ShapeBase.  # noqa: E501
        :type: str
        """
        if shape_type is not None:
            allowed_values = ["Custom", "Line", "LineInverse", "Triangle", "RightTriangle", "Rectangle", "Diamond", "Parallelogram", "Trapezoid", "NonIsoscelesTrapezoid", "Pentagon", "Hexagon", "Heptagon", "Octagon", "Decagon", "Dodecagon", "FourPointedStar", "FivePointedStar", "SixPointedStar", "SevenPointedStar", "EightPointedStar", "TenPointedStar", "TwelvePointedStar", "SixteenPointedStar", "TwentyFourPointedStar", "ThirtyTwoPointedStar", "RoundCornerRectangle", "OneRoundCornerRectangle", "TwoSamesideRoundCornerRectangle", "TwoDiagonalRoundCornerRectangle", "OneSnipOneRoundCornerRectangle", "OneSnipCornerRectangle", "TwoSamesideSnipCornerRectangle", "TwoDiagonalSnipCornerRectangle", "Plaque", "Ellipse", "Teardrop", "HomePlate", "Chevron", "PieWedge", "Pie", "BlockArc", "Donut", "NoSmoking", "RightArrow", "LeftArrow", "UpArrow", "DownArrow", "StripedRightArrow", "NotchedRightArrow", "BentUpArrow", "LeftRightArrow", "UpDownArrow", "LeftUpArrow", "LeftRightUpArrow", "QuadArrow", "CalloutLeftArrow", "CalloutRightArrow", "CalloutUpArrow", "CalloutDownArrow", "CalloutLeftRightArrow", "CalloutUpDownArrow", "CalloutQuadArrow", "BentArrow", "UTurnArrow", "CircularArrow", "LeftCircularArrow", "LeftRightCircularArrow", "CurvedRightArrow", "CurvedLeftArrow", "CurvedUpArrow", "CurvedDownArrow", "SwooshArrow", "Cube", "Can", "LightningBolt", "Heart", "Sun", "Moon", "SmileyFace", "IrregularSeal1", "IrregularSeal2", "FoldedCorner", "Bevel", "Frame", "HalfFrame", "Corner", "DiagonalStripe", "Chord", "CurvedArc", "LeftBracket", "RightBracket", "LeftBrace", "RightBrace", "BracketPair", "BracePair", "StraightConnector1", "BentConnector2", "BentConnector3", "BentConnector4", "BentConnector5", "CurvedConnector2", "CurvedConnector3", "CurvedConnector4", "CurvedConnector5", "Callout1", "Callout2", "Callout3", "Callout1WithAccent", "Callout2WithAccent", "Callout3WithAccent", "Callout1WithBorder", "Callout2WithBorder", "Callout3WithBorder", "Callout1WithBorderAndAccent", "Callout2WithBorderAndAccent", "Callout3WithBorderAndAccent", "CalloutWedgeRectangle", "CalloutWedgeRoundRectangle", "CalloutWedgeEllipse", "CalloutCloud", "Cloud", "Ribbon", "Ribbon2", "EllipseRibbon", "EllipseRibbon2", "LeftRightRibbon", "VerticalScroll", "HorizontalScroll", "Wave", "DoubleWave", "Plus", "ProcessFlow", "DecisionFlow", "InputOutputFlow", "PredefinedProcessFlow", "InternalStorageFlow", "DocumentFlow", "MultiDocumentFlow", "TerminatorFlow", "PreparationFlow", "ManualInputFlow", "ManualOperationFlow", "ConnectorFlow", "PunchedCardFlow", "PunchedTapeFlow", "SummingJunctionFlow", "OrFlow", "CollateFlow", "SortFlow", "ExtractFlow", "MergeFlow", "OfflineStorageFlow", "OnlineStorageFlow", "MagneticTapeFlow", "MagneticDiskFlow", "MagneticDrumFlow", "DisplayFlow", "DelayFlow", "AlternateProcessFlow", "OffPageConnectorFlow", "BlankButton", "HomeButton", "HelpButton", "InformationButton", "ForwardOrNextButton", "BackOrPreviousButton", "EndButton", "BeginningButton", "ReturnButton", "DocumentButton", "SoundButton", "MovieButton", "Gear6", "Gear9", "Funnel", "PlusMath", "MinusMath", "MultiplyMath", "DivideMath", "EqualMath", "NotEqualMath", "CornerTabs", "SquareTabs", "PlaqueTabs", "ChartX", "ChartStar", "ChartPlus", "Chart", "Table", "PictureFrame", "VideoFrame", "AudioFrame", "Diagram", "OleObjectFrame", "GroupShape", "GraphicalObject", "NotDefined"]  # noqa: E501
            if shape_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `shape_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(shape_type, allowed_values)
                )
        self._shape_type = shape_type

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
        if not isinstance(other, ShapeBase):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
