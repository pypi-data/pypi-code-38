#!/usr/bin/python2.7
"""
Copyright (C) 2014 Reinventing Geospatial, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>,
or write to the Free Software Foundation, Inc., 59 Temple Place -
Suite 330, Boston, MA 02111-1307, USA.

Author: Jenifer Cochran, Reinventing Geospatial Inc (RGi)
Date: 2018-11-11
   Requires: sqlite3, argparse
   Optional: Python Imaging Library (PIL or Pillow)
Credits:
  MapProxy imaging functions: http://mapproxy.org
  gdal2mb on github: https://github.com/developmentseed/gdal2mb

Version:
"""
from enum import Enum


class StyleFormat(Enum):
    """The Style format encoding."""
    MAPBOX_STYLE = "mbstyle"
    SLD_STYLE = "sld"
    GEO_CSS_STYLE = "geocss"
    G_CMSS_STYLE = "gcmss"
    OTHER = "other"
    UNKNOWN = "unknown"

    @staticmethod
    def get_style_format_from_string(style_format_name):
        """
        Get the style format from the string given.

        :param style_format_name:  the string to convert to a StyleFormat
        :type style_format_name: str

        :rtype: StyleFormat
        """
        return StyleFormat(style_format_name.lower())


class StyleSheetsEntry(object):
    """
    The object that represents an entry to the GeoPackage Stylesheets Table (gpkgext_stylesheets)
    """

    def __init__(self,
                 styles_set,
                 style,
                 style_format,
                 stylesheet,
                 title,
                 description,
                 identifier=None):
        """
        Constructor

        :param description: optional description of the styleset
        :type description: str, None

        :param identifier:primary key int identifier for the column id.  If None, a value will be assigned to it when
        added to the GeoPackage
        :type identifier: int, None

        :param styles_set: a style set id that groups a set of stylesheets
        :type styles_set: str

        :param style: alternative styles for the same set of layers (day, night) associated with an int value.
        :type style: str

        :param style_format: stylesheet's encoding standard/format
        :type style_format: str

        :param stylesheet: the stylesheet data
        :type stylesheet: Binary

        :param title: the layer id that is referenced in the gpkgext_vt_layers table
        :type title: int, None
        """

        self.styles_set = styles_set
        self.style = style
        self.style_format = style_format
        self.stylesheet = stylesheet
        self.title = title
        self.description = description
        self.identifier = identifier
