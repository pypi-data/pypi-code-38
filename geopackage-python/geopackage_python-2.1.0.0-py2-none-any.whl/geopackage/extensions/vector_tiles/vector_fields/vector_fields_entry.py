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


class VectorFieldType(Enum):
    """
    Vector Field types for the gpkgext_vt_fields table can only be
    the following values.
    """

    BOOLEAN = "Boolean"
    NUMBER = "Number"
    STRING = "String"

    @staticmethod
    def get_vector_field_type_from_text(text):
        """
        returns The vector field type that matches the text value

        :param text: the text that needs to be converted to a Vector Field Type
        :type text: str

        :return: The vector field type that matches the text value
        :rtype: VectorFieldType
        """
        if text.lower() == VectorFieldType.BOOLEAN.value.lower():
            return VectorFieldType.BOOLEAN
        elif text.lower() == VectorFieldType.NUMBER.value.lower():
            return VectorFieldType.NUMBER
        elif text.lower() == VectorFieldType.STRING.value.lower():
            return VectorFieldType.STRING

        raise ValueError("No matching VectorFieldType for {text}".format(text=text))

    # noinspection PyBroadException
    @staticmethod
    def convert_string_value_to_vector_field_type(text):
        """
        Takes a string and determines if it is best categorized as a Number, Integer, or kept as a String.

        i.e. '1' would return VectorFieldType.NUMBER, 'True' would return VectorFieldType.BOOLEAN

        :param text: the string to determine which category it belongs in
        :type text: str
        """
        try:
            float(text)
            return VectorFieldType.NUMBER
        except:
            pass

        if text.lower() == 'true' or text.lower() == 'false':
            return VectorFieldType.BOOLEAN

        return VectorFieldType.STRING


class VectorFieldsEntry(object):
    """
    The object that represents an entry to the GeoPackage Vector Fields Table (gpkgext_vt_fields)
    """

    def __init__(self,
                 layer_id,
                 name,
                 field_type):
        """
        Constructor

        :param layer_id: is a foreign key to id in gpkgext_vt_layers
        :type layer_id: int

        :param name: the name of the field
        :type name: str

        :param field_type: the Vector Field type must be boolean, number, or string
        :type field_type: VectorFieldType
        """
        self.layer_id = layer_id
        self.name = name
        self.type = field_type
