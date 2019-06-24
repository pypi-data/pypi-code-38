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
import mimetypes

from rgi.geopackage.extensions.metadata.md_scope import MdScope

try:
    # python2
    from urlparse import urlparse
except:
    # python3
    from urllib.parse import urlparse


class MetadataEntry(object):
    """
    Metadata object that represents an entry in the gpkg_metadata Table
    """

    def __init__(self,
                 md_standard_uri,
                 metadata="",
                 md_scope=MdScope.DATASET,
                 mime_type='text/xml'):
        """
        Constructor

        :param md_scope: Use MdScope Enum which has a case sensitive name of the data scope to which this metadata
        applies; see Metadata Scopes http://www.geopackage.org/spec121/#metadata_scopes
        :type md_scope: MdScope

        :param md_standard_uri: URI reference to the metadata structure definition authority
        :type md_standard_uri: str

        :param mime_type: MIME encoding of metadata
        :type mime_type: str

        :param metadata: Metadata text
        :type metadata: str
        """

        # check if the uri is a valid uri
        if not MetadataEntry.__is_valid_uri(md_standard_uri):
            raise ValueError("Invalid URI: {uri}.".format(uri=md_standard_uri))

        # check to make sure the MdScope value is a valid value
        if md_scope.value not in [md_scope_enum.value for md_scope_enum in MdScope]:
            raise ValueError("Invalid md_scope value {md_scope}. Must be one of the following: {md_scopes}."
                             .format(md_scope=md_scope,
                                     md_scopes=[md_scope_enum.value for md_scope_enum in MdScope]))
        # TODO: should this really be enforced? Since not all mimetypes are known?
        # # check to see if the mime type is a known mime type
        # if mime_type not in [value for ext, value in mimetypes.types_map.items()]:
        #     raise ValueError("Unknown mime type: {mime_type}. Must be one of the following: {types}."
        #                      .format(mime_type=mime_type,
        #                              types=[value for ext, value in mimetypes.types_map.items()]))

        if metadata is None:
            raise ValueError("Metadata cannot be None.")

        self.md_scope = md_scope
        self.md_standard_uri = md_standard_uri
        self.mime_type = mime_type
        self.metadata = metadata

    @staticmethod
    def __is_valid_uri(uri):
        try:
            result = urlparse(uri)
            return all([result.scheme, result.netloc, result.path])
        except:
            return False
