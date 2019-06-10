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

from asposeslidescloud.models.export_options import ExportOptions

class SwfExportOptions(ExportOptions):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'format': 'str',
        'show_hidden_slides': 'bool',
        'compressed': 'bool',
        'viewer_included': 'bool',
        'show_page_border': 'bool',
        'show_full_screen': 'bool',
        'show_page_stepper': 'bool',
        'show_search': 'bool',
        'show_top_pane': 'bool',
        'show_bottom_pane': 'bool',
        'show_left_pane': 'bool',
        'start_open_left_pane': 'bool',
        'enable_context_menu': 'bool',
        'logo_image': 'str',
        'logo_link': 'str',
        'jpeg_quality': 'int',
        'notes_position': 'str',
        'comments_position': 'str',
        'comments_area_width': 'int',
        'comments_area_color': 'str',
        'show_comments_by_no_author': 'bool'
    }

    attribute_map = {
        'format': 'Format',
        'show_hidden_slides': 'ShowHiddenSlides',
        'compressed': 'Compressed',
        'viewer_included': 'ViewerIncluded',
        'show_page_border': 'ShowPageBorder',
        'show_full_screen': 'ShowFullScreen',
        'show_page_stepper': 'ShowPageStepper',
        'show_search': 'ShowSearch',
        'show_top_pane': 'ShowTopPane',
        'show_bottom_pane': 'ShowBottomPane',
        'show_left_pane': 'ShowLeftPane',
        'start_open_left_pane': 'StartOpenLeftPane',
        'enable_context_menu': 'EnableContextMenu',
        'logo_image': 'LogoImage',
        'logo_link': 'LogoLink',
        'jpeg_quality': 'JpegQuality',
        'notes_position': 'NotesPosition',
        'comments_position': 'CommentsPosition',
        'comments_area_width': 'CommentsAreaWidth',
        'comments_area_color': 'CommentsAreaColor',
        'show_comments_by_no_author': 'ShowCommentsByNoAuthor'
    }

    def __init__(self, format='swf', show_hidden_slides=None, compressed=None, viewer_included=None, show_page_border=None, show_full_screen=None, show_page_stepper=None, show_search=None, show_top_pane=None, show_bottom_pane=None, show_left_pane=None, start_open_left_pane=None, enable_context_menu=None, logo_image=None, logo_link=None, jpeg_quality=None, notes_position=None, comments_position=None, comments_area_width=None, comments_area_color=None, show_comments_by_no_author=None):  # noqa: E501
        """SwfExportOptions - a model defined in Swagger"""  # noqa: E501
        super(SwfExportOptions, self).__init__(format)

        self._show_hidden_slides = None
        self._compressed = None
        self._viewer_included = None
        self._show_page_border = None
        self._show_full_screen = None
        self._show_page_stepper = None
        self._show_search = None
        self._show_top_pane = None
        self._show_bottom_pane = None
        self._show_left_pane = None
        self._start_open_left_pane = None
        self._enable_context_menu = None
        self._logo_image = None
        self._logo_link = None
        self._jpeg_quality = None
        self._notes_position = None
        self._comments_position = None
        self._comments_area_width = None
        self._comments_area_color = None
        self._show_comments_by_no_author = None

        self.show_hidden_slides = show_hidden_slides
        self.compressed = compressed
        self.viewer_included = viewer_included
        self.show_page_border = show_page_border
        self.show_full_screen = show_full_screen
        self.show_page_stepper = show_page_stepper
        self.show_search = show_search
        self.show_top_pane = show_top_pane
        self.show_bottom_pane = show_bottom_pane
        self.show_left_pane = show_left_pane
        self.start_open_left_pane = start_open_left_pane
        self.enable_context_menu = enable_context_menu
        if logo_image is not None:
            self.logo_image = logo_image
        if logo_link is not None:
            self.logo_link = logo_link
        self.jpeg_quality = jpeg_quality
        self.notes_position = notes_position
        self.comments_position = comments_position
        self.comments_area_width = comments_area_width
        if comments_area_color is not None:
            self.comments_area_color = comments_area_color
        self.show_comments_by_no_author = show_comments_by_no_author

    @property
    def show_hidden_slides(self):
        """Gets the show_hidden_slides of this SwfExportOptions.  # noqa: E501

        Specifies whether the generated document should include hidden slides or not. Default is false.   # noqa: E501

        :return: The show_hidden_slides of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_hidden_slides

    @show_hidden_slides.setter
    def show_hidden_slides(self, show_hidden_slides):
        """Sets the show_hidden_slides of this SwfExportOptions.

        Specifies whether the generated document should include hidden slides or not. Default is false.   # noqa: E501

        :param show_hidden_slides: The show_hidden_slides of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_hidden_slides = show_hidden_slides

    @property
    def compressed(self):
        """Gets the compressed of this SwfExportOptions.  # noqa: E501

        Specifies whether the generated SWF document should be compressed or not. Default is true.   # noqa: E501

        :return: The compressed of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._compressed

    @compressed.setter
    def compressed(self, compressed):
        """Sets the compressed of this SwfExportOptions.

        Specifies whether the generated SWF document should be compressed or not. Default is true.   # noqa: E501

        :param compressed: The compressed of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._compressed = compressed

    @property
    def viewer_included(self):
        """Gets the viewer_included of this SwfExportOptions.  # noqa: E501

        Specifies whether the generated SWF document should include the integrated document viewer or not. Default is true.   # noqa: E501

        :return: The viewer_included of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._viewer_included

    @viewer_included.setter
    def viewer_included(self, viewer_included):
        """Sets the viewer_included of this SwfExportOptions.

        Specifies whether the generated SWF document should include the integrated document viewer or not. Default is true.   # noqa: E501

        :param viewer_included: The viewer_included of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._viewer_included = viewer_included

    @property
    def show_page_border(self):
        """Gets the show_page_border of this SwfExportOptions.  # noqa: E501

        Specifies whether border around pages should be shown. Default is true.   # noqa: E501

        :return: The show_page_border of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_page_border

    @show_page_border.setter
    def show_page_border(self, show_page_border):
        """Sets the show_page_border of this SwfExportOptions.

        Specifies whether border around pages should be shown. Default is true.   # noqa: E501

        :param show_page_border: The show_page_border of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_page_border = show_page_border

    @property
    def show_full_screen(self):
        """Gets the show_full_screen of this SwfExportOptions.  # noqa: E501

        Show/hide fullscreen button. Can be overridden in flashvars. Default is true.   # noqa: E501

        :return: The show_full_screen of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_full_screen

    @show_full_screen.setter
    def show_full_screen(self, show_full_screen):
        """Sets the show_full_screen of this SwfExportOptions.

        Show/hide fullscreen button. Can be overridden in flashvars. Default is true.   # noqa: E501

        :param show_full_screen: The show_full_screen of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_full_screen = show_full_screen

    @property
    def show_page_stepper(self):
        """Gets the show_page_stepper of this SwfExportOptions.  # noqa: E501

        Show/hide page stepper. Can be overridden in flashvars. Default is true.   # noqa: E501

        :return: The show_page_stepper of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_page_stepper

    @show_page_stepper.setter
    def show_page_stepper(self, show_page_stepper):
        """Sets the show_page_stepper of this SwfExportOptions.

        Show/hide page stepper. Can be overridden in flashvars. Default is true.   # noqa: E501

        :param show_page_stepper: The show_page_stepper of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_page_stepper = show_page_stepper

    @property
    def show_search(self):
        """Gets the show_search of this SwfExportOptions.  # noqa: E501

        Show/hide search section. Can be overridden in flashvars. Default is true.   # noqa: E501

        :return: The show_search of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_search

    @show_search.setter
    def show_search(self, show_search):
        """Sets the show_search of this SwfExportOptions.

        Show/hide search section. Can be overridden in flashvars. Default is true.   # noqa: E501

        :param show_search: The show_search of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_search = show_search

    @property
    def show_top_pane(self):
        """Gets the show_top_pane of this SwfExportOptions.  # noqa: E501

        Show/hide whole top pane. Can be overridden in flashvars. Default is true.   # noqa: E501

        :return: The show_top_pane of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_top_pane

    @show_top_pane.setter
    def show_top_pane(self, show_top_pane):
        """Sets the show_top_pane of this SwfExportOptions.

        Show/hide whole top pane. Can be overridden in flashvars. Default is true.   # noqa: E501

        :param show_top_pane: The show_top_pane of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_top_pane = show_top_pane

    @property
    def show_bottom_pane(self):
        """Gets the show_bottom_pane of this SwfExportOptions.  # noqa: E501

        Show/hide bottom pane. Can be overridden in flashvars. Default is true.   # noqa: E501

        :return: The show_bottom_pane of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_bottom_pane

    @show_bottom_pane.setter
    def show_bottom_pane(self, show_bottom_pane):
        """Sets the show_bottom_pane of this SwfExportOptions.

        Show/hide bottom pane. Can be overridden in flashvars. Default is true.   # noqa: E501

        :param show_bottom_pane: The show_bottom_pane of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_bottom_pane = show_bottom_pane

    @property
    def show_left_pane(self):
        """Gets the show_left_pane of this SwfExportOptions.  # noqa: E501

        Show/hide left pane. Can be overridden in flashvars. Default is true.   # noqa: E501

        :return: The show_left_pane of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_left_pane

    @show_left_pane.setter
    def show_left_pane(self, show_left_pane):
        """Sets the show_left_pane of this SwfExportOptions.

        Show/hide left pane. Can be overridden in flashvars. Default is true.   # noqa: E501

        :param show_left_pane: The show_left_pane of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_left_pane = show_left_pane

    @property
    def start_open_left_pane(self):
        """Gets the start_open_left_pane of this SwfExportOptions.  # noqa: E501

        Start with opened left pane. Can be overridden in flashvars. Default is false.   # noqa: E501

        :return: The start_open_left_pane of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._start_open_left_pane

    @start_open_left_pane.setter
    def start_open_left_pane(self, start_open_left_pane):
        """Sets the start_open_left_pane of this SwfExportOptions.

        Start with opened left pane. Can be overridden in flashvars. Default is false.   # noqa: E501

        :param start_open_left_pane: The start_open_left_pane of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._start_open_left_pane = start_open_left_pane

    @property
    def enable_context_menu(self):
        """Gets the enable_context_menu of this SwfExportOptions.  # noqa: E501

        Enable/disable context menu. Default is true.   # noqa: E501

        :return: The enable_context_menu of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._enable_context_menu

    @enable_context_menu.setter
    def enable_context_menu(self, enable_context_menu):
        """Sets the enable_context_menu of this SwfExportOptions.

        Enable/disable context menu. Default is true.   # noqa: E501

        :param enable_context_menu: The enable_context_menu of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._enable_context_menu = enable_context_menu

    @property
    def logo_image(self):
        """Gets the logo_image of this SwfExportOptions.  # noqa: E501

        Image that will be displayed as logo in the top right corner of the viewer. The image data is a base 64 string. Image should be 32x64 pixels PNG image, otherwise logo can be displayed improperly.   # noqa: E501

        :return: The logo_image of this SwfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._logo_image

    @logo_image.setter
    def logo_image(self, logo_image):
        """Sets the logo_image of this SwfExportOptions.

        Image that will be displayed as logo in the top right corner of the viewer. The image data is a base 64 string. Image should be 32x64 pixels PNG image, otherwise logo can be displayed improperly.   # noqa: E501

        :param logo_image: The logo_image of this SwfExportOptions.  # noqa: E501
        :type: str
        """
        self._logo_image = logo_image

    @property
    def logo_link(self):
        """Gets the logo_link of this SwfExportOptions.  # noqa: E501

        Gets or sets the full hyperlink address for a logo. Has an effect only if a LogoImage is specified.   # noqa: E501

        :return: The logo_link of this SwfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._logo_link

    @logo_link.setter
    def logo_link(self, logo_link):
        """Sets the logo_link of this SwfExportOptions.

        Gets or sets the full hyperlink address for a logo. Has an effect only if a LogoImage is specified.   # noqa: E501

        :param logo_link: The logo_link of this SwfExportOptions.  # noqa: E501
        :type: str
        """
        self._logo_link = logo_link

    @property
    def jpeg_quality(self):
        """Gets the jpeg_quality of this SwfExportOptions.  # noqa: E501

        Specifies the quality of JPEG images. Default is 95.  # noqa: E501

        :return: The jpeg_quality of this SwfExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._jpeg_quality

    @jpeg_quality.setter
    def jpeg_quality(self, jpeg_quality):
        """Sets the jpeg_quality of this SwfExportOptions.

        Specifies the quality of JPEG images. Default is 95.  # noqa: E501

        :param jpeg_quality: The jpeg_quality of this SwfExportOptions.  # noqa: E501
        :type: int
        """
        self._jpeg_quality = jpeg_quality

    @property
    def notes_position(self):
        """Gets the notes_position of this SwfExportOptions.  # noqa: E501

        Gets or sets the position of the notes on the page.  # noqa: E501

        :return: The notes_position of this SwfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._notes_position

    @notes_position.setter
    def notes_position(self, notes_position):
        """Sets the notes_position of this SwfExportOptions.

        Gets or sets the position of the notes on the page.  # noqa: E501

        :param notes_position: The notes_position of this SwfExportOptions.  # noqa: E501
        :type: str
        """
        if notes_position is not None:
            allowed_values = ["None", "BottomFull", "BottomTruncated"]  # noqa: E501
            if notes_position not in allowed_values:
                raise ValueError(
                    "Invalid value for `notes_position` ({0}), must be one of {1}"  # noqa: E501
                    .format(notes_position, allowed_values)
                )
        self._notes_position = notes_position

    @property
    def comments_position(self):
        """Gets the comments_position of this SwfExportOptions.  # noqa: E501

        Gets or sets the position of the comments on the page.  # noqa: E501

        :return: The comments_position of this SwfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._comments_position

    @comments_position.setter
    def comments_position(self, comments_position):
        """Sets the comments_position of this SwfExportOptions.

        Gets or sets the position of the comments on the page.  # noqa: E501

        :param comments_position: The comments_position of this SwfExportOptions.  # noqa: E501
        :type: str
        """
        if comments_position is not None:
            allowed_values = ["None", "Bottom", "Right"]  # noqa: E501
            if comments_position not in allowed_values:
                raise ValueError(
                    "Invalid value for `comments_position` ({0}), must be one of {1}"  # noqa: E501
                    .format(comments_position, allowed_values)
                )
        self._comments_position = comments_position

    @property
    def comments_area_width(self):
        """Gets the comments_area_width of this SwfExportOptions.  # noqa: E501

        Gets or sets the width of the comment output area in pixels (Applies only if comments are displayed on the right).  # noqa: E501

        :return: The comments_area_width of this SwfExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._comments_area_width

    @comments_area_width.setter
    def comments_area_width(self, comments_area_width):
        """Sets the comments_area_width of this SwfExportOptions.

        Gets or sets the width of the comment output area in pixels (Applies only if comments are displayed on the right).  # noqa: E501

        :param comments_area_width: The comments_area_width of this SwfExportOptions.  # noqa: E501
        :type: int
        """
        self._comments_area_width = comments_area_width

    @property
    def comments_area_color(self):
        """Gets the comments_area_color of this SwfExportOptions.  # noqa: E501

        Gets or sets the color of comments area (Applies only if comments are displayed on the right).  # noqa: E501

        :return: The comments_area_color of this SwfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._comments_area_color

    @comments_area_color.setter
    def comments_area_color(self, comments_area_color):
        """Sets the comments_area_color of this SwfExportOptions.

        Gets or sets the color of comments area (Applies only if comments are displayed on the right).  # noqa: E501

        :param comments_area_color: The comments_area_color of this SwfExportOptions.  # noqa: E501
        :type: str
        """
        self._comments_area_color = comments_area_color

    @property
    def show_comments_by_no_author(self):
        """Gets the show_comments_by_no_author of this SwfExportOptions.  # noqa: E501

        True if comments that have no author are displayed. (Applies only if comments are displayed).  # noqa: E501

        :return: The show_comments_by_no_author of this SwfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_comments_by_no_author

    @show_comments_by_no_author.setter
    def show_comments_by_no_author(self, show_comments_by_no_author):
        """Sets the show_comments_by_no_author of this SwfExportOptions.

        True if comments that have no author are displayed. (Applies only if comments are displayed).  # noqa: E501

        :param show_comments_by_no_author: The show_comments_by_no_author of this SwfExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_comments_by_no_author = show_comments_by_no_author

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
        if not isinstance(other, SwfExportOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
