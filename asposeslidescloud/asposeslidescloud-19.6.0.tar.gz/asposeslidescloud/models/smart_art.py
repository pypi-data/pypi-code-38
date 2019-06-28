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

from asposeslidescloud.models.shape_base import ShapeBase

class SmartArt(ShapeBase):


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
        'layout': 'str',
        'quick_style': 'str',
        'color_style': 'str',
        'nodes': 'list[SmartArtNode]',
        'is_reversed': 'bool'
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
        'layout': 'Layout',
        'quick_style': 'QuickStyle',
        'color_style': 'ColorStyle',
        'nodes': 'Nodes',
        'is_reversed': 'IsReversed'
    }

    def __init__(self, self_uri=None, alternate_links=None, name=None, width=None, height=None, alternative_text=None, hidden=None, x=None, y=None, z_order_position=None, shapes=None, fill_format=None, effect_format=None, line_format=None, type='SmartArt', shape_type='Diagram', layout=None, quick_style=None, color_style=None, nodes=None, is_reversed=None):  # noqa: E501
        """SmartArt - a model defined in Swagger"""  # noqa: E501
        super(SmartArt, self).__init__(self_uri, alternate_links, name, width, height, alternative_text, hidden, x, y, z_order_position, shapes, fill_format, effect_format, line_format, type, shape_type)

        self._layout = None
        self._quick_style = None
        self._color_style = None
        self._nodes = None
        self._is_reversed = None

        self.layout = layout
        self.quick_style = quick_style
        self.color_style = color_style
        if nodes is not None:
            self.nodes = nodes
        self.is_reversed = is_reversed

    @property
    def layout(self):
        """Gets the layout of this SmartArt.  # noqa: E501

        Layout type.  # noqa: E501

        :return: The layout of this SmartArt.  # noqa: E501
        :rtype: str
        """
        return self._layout

    @layout.setter
    def layout(self, layout):
        """Sets the layout of this SmartArt.

        Layout type.  # noqa: E501

        :param layout: The layout of this SmartArt.  # noqa: E501
        :type: str
        """
        if layout is not None:
            allowed_values = ["AccentProcess", "AccentedPicture", "AlternatingFlow", "AlternatingHexagons", "AlternatingPictureBlocks", "AlternatingPictureCircles", "ArrowRibbon", "AscendingPictureAccentProcess", "Balance", "BasicBendingProcess", "BasicBlockList", "BasicChevronProcess", "BasicCycle", "BasicMatrix", "BasicPie", "BasicProcess", "BasicPyramid", "BasicRadial", "BasicTarget", "BasicTimeline", "BasicVenn", "BendingPictureAccentList", "BendingPictureBlocks", "BendingPictureCaption", "BendingPictureCaptionList", "BendingPictureSemiTransparentText", "BlockCycle", "BubblePictureList", "CaptionedPictures", "ChevronList", "CircleAccentTimeline", "CircleArrowProcess", "CirclePictureHierarchy", "CircleRelationship", "CircularBendingProcess", "CircularPictureCallout", "ClosedChevronProcess", "ContinuousArrowProcess", "ContinuousBlockProcess", "ContinuousCycle", "ContinuousPictureList", "ConvergingArrows", "ConvergingRadial", "CounterbalanceArrows", "CycleMatrix", "DescendingBlockList", "DescendingProcess", "DetailedProcess", "DivergingArrows", "DivergingRadial", "Equation", "FramedTextPicture", "Funnel", "Gear", "GridMatrix", "GroupedList", "HalfCircleOrganizationChart", "HexagonCluster", "Hierarchy", "HierarchyList", "HorizontalBulletList", "HorizontalHierarchy", "HorizontalLabeledHierarchy", "HorizontalMultiLevelHierarchy", "HorizontalOrganizationChart", "HorizontalPictureList", "IncreasingArrowsProcess", "IncreasingCircleProcess", "InvertedPyramid", "LabeledHierarchy", "LinearVenn", "LinedList", "MultidirectionalCycle", "NameandTitleOrganizationChart", "NestedTarget", "NondirectionalCycle", "OpposingArrows", "OpposingIdeas", "OrganizationChart", "PhasedProcess", "PictureAccentBlocks", "PictureAccentList", "PictureAccentProcess", "PictureCaptionList", "PictureGrid", "PictureLineup", "PictureStrips", "PieProcess", "PlusandMinus", "ProcessArrows", "ProcessList", "PyramidList", "RadialCluster", "RadialCycle", "RadialList", "RadialVenn", "RandomToResultProcess", "RepeatingBendingProcess", "ReverseList", "SegmentedCycle", "SegmentedProcess", "SegmentedPyramid", "SnapshotPictureList", "SpiralPicture", "SquareAccentList", "StackedList", "StackedVenn", "StaggeredProcess", "StepDownProcess", "StepUpProcess", "SubStepProcess", "TableHierarchy", "TableList", "TargetList", "TextCycle", "TitlePictureLineup", "TitledMatrix", "TitledPictureAccentList", "TitledPictureBlocks", "TrapezoidList", "UpwardArrow", "VerticalAccentList", "VerticalArrowList", "VerticalBendingProcess", "VerticalBlockList", "VerticalBoxList", "VerticalBulletList", "VerticalChevronList", "VerticalCircleList", "VerticalCurvedList", "VerticalEquation", "VerticalPictureAccentList", "VerticalPictureList", "VerticalProcess", "Custom", "PictureOrganizationChart"]  # noqa: E501
            if layout not in allowed_values:
                raise ValueError(
                    "Invalid value for `layout` ({0}), must be one of {1}"  # noqa: E501
                    .format(layout, allowed_values)
                )
        self._layout = layout

    @property
    def quick_style(self):
        """Gets the quick_style of this SmartArt.  # noqa: E501

        Quick style.  # noqa: E501

        :return: The quick_style of this SmartArt.  # noqa: E501
        :rtype: str
        """
        return self._quick_style

    @quick_style.setter
    def quick_style(self, quick_style):
        """Sets the quick_style of this SmartArt.

        Quick style.  # noqa: E501

        :param quick_style: The quick_style of this SmartArt.  # noqa: E501
        :type: str
        """
        if quick_style is not None:
            allowed_values = ["SimpleFill", "WhiteOutline", "SubtleEffect", "ModerateEffect", "IntenceEffect", "Polished", "Inset", "Cartoon", "Powder", "BrickScene", "FlatScene", "MetallicScene", "SunsetScene", "BirdsEyeScene"]  # noqa: E501
            if quick_style not in allowed_values:
                raise ValueError(
                    "Invalid value for `quick_style` ({0}), must be one of {1}"  # noqa: E501
                    .format(quick_style, allowed_values)
                )
        self._quick_style = quick_style

    @property
    def color_style(self):
        """Gets the color_style of this SmartArt.  # noqa: E501

        Color style.  # noqa: E501

        :return: The color_style of this SmartArt.  # noqa: E501
        :rtype: str
        """
        return self._color_style

    @color_style.setter
    def color_style(self, color_style):
        """Sets the color_style of this SmartArt.

        Color style.  # noqa: E501

        :param color_style: The color_style of this SmartArt.  # noqa: E501
        :type: str
        """
        if color_style is not None:
            allowed_values = ["Dark1Outline", "Dark2Outline", "DarkFill", "ColorfulAccentColors", "ColorfulAccentColors2to3", "ColorfulAccentColors3to4", "ColorfulAccentColors4to5", "ColorfulAccentColors5to6", "ColoredOutlineAccent1", "ColoredFillAccent1", "GradientRangeAccent1", "GradientLoopAccent1", "TransparentGradientRangeAccent1", "ColoredOutlineAccent2", "ColoredFillAccent2", "GradientRangeAccent2", "GradientLoopAccent2", "TransparentGradientRangeAccent2", "ColoredOutlineAccent3", "ColoredFillAccent3", "GradientRangeAccent3", "GradientLoopAccent3", "TransparentGradientRangeAccent3", "ColoredOutlineAccent4", "ColoredFillAccent4", "GradientRangeAccent4", "GradientLoopAccent4", "TransparentGradientRangeAccent4", "ColoredOutlineAccent5", "ColoredFillAccent5", "GradientRangeAccent5", "GradientLoopAccent5", "TransparentGradientRangeAccent5", "ColoredOutlineAccent6", "ColoredFillAccent6", "GradientRangeAccent6", "GradientLoopAccent6", "TransparentGradientRangeAccent6"]  # noqa: E501
            if color_style not in allowed_values:
                raise ValueError(
                    "Invalid value for `color_style` ({0}), must be one of {1}"  # noqa: E501
                    .format(color_style, allowed_values)
                )
        self._color_style = color_style

    @property
    def nodes(self):
        """Gets the nodes of this SmartArt.  # noqa: E501

        Collection of nodes in SmartArt object.               # noqa: E501

        :return: The nodes of this SmartArt.  # noqa: E501
        :rtype: list[SmartArtNode]
        """
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        """Sets the nodes of this SmartArt.

        Collection of nodes in SmartArt object.               # noqa: E501

        :param nodes: The nodes of this SmartArt.  # noqa: E501
        :type: list[SmartArtNode]
        """
        self._nodes = nodes

    @property
    def is_reversed(self):
        """Gets the is_reversed of this SmartArt.  # noqa: E501

        The state of the SmartArt diagram with regard to (left-to-right) LTR or (right-to-left) RTL, if the diagram supports reversal.  # noqa: E501

        :return: The is_reversed of this SmartArt.  # noqa: E501
        :rtype: bool
        """
        return self._is_reversed

    @is_reversed.setter
    def is_reversed(self, is_reversed):
        """Sets the is_reversed of this SmartArt.

        The state of the SmartArt diagram with regard to (left-to-right) LTR or (right-to-left) RTL, if the diagram supports reversal.  # noqa: E501

        :param is_reversed: The is_reversed of this SmartArt.  # noqa: E501
        :type: bool
        """
        self._is_reversed = is_reversed

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
        if not isinstance(other, SmartArt):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
