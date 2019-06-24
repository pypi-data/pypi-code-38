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


class MdScope(Enum):
    """
    Metadata Scope values

    see http://www.geopackage.org/spec121/#metadata_scopes
    """

    """Information applies to the (dataset) series """
    SERIES = "series"  # type: MdScope

    """Metadata information scope is undefined"""
    UNDEFINED = "undefined"  # type: MdScope

    """Information applies to the field session"""
    FIELD_SESSION = "fieldSession"  # type: MdScope

    """Information applies to the collection session"""
    COLLECTION_SESSION = "collectionSession"  # type: MdScope

    """Information applies to the (geographic feature) dataset"""
    DATASET = "dataset"  # type: MdScope

    """Information applies to a feature type (class)"""
    FEATURE_TYPE = "featureType"  # type: MdScope

    """Information applies to a feature (instance)"""
    FEATURE = "feature"  # type: MdScope

    """Information applies to the attribute class"""
    ATTRIBUTE_TYPE = "attributeType"  # type: MdScope

    """Information applies to the characteristic of a feature (instance)"""
    ATTRIBUTE = "attribute"  # type: MdScope

    """Information applies to a tile, a spatial subset of geographic data"""
    TILE = "tile"  # type: MdScope

    """Information applies to a copy or imitation of an existing or hypothetical object"""
    MODEL = "model"  # type: MdScope

    """Metadata applies to a feature catalog"""
    CATALOG = "catalog"  # type: MdScope

    """Metadata applies to an application schema"""
    SCHEMA = "schema"  # type: MdScope

    """Metadata applies to a taxonomy or knowledge system"""
    TAXONOMY = "taxonomy"  # type: MdScope

    """Information applies to a computer program or routine"""
    SOFTWARE = "software"  # type: MdScope

    """Information applies to a capability which a service provider entity makes available to a service user entity 
    through a set of interfaces that define a behavior, such as a use case"""
    SERVICE = "service"  # type: MdScope

    """Information applies to the collection hardware class"""
    COLLECTION_HARDWARE = "collectionHardware"  # type: MdScope

    """Information applies to non-geographic data"""
    NON_GEOGRAPHIC_DATASET = "nonGeographicDataset"  # type: MdScope

    """Information applies to a dimension group"""
    DIMENSION_GROUP = "dimensionGroup"  # type: MdScope

    @staticmethod
    def from_text(text):
        """
        MdScope representation of the text supplied, if none match, an error will be thrown

        :param text: the string value of an MdScope (i.e. 'nonGeoGraphicDataset')
        :type text: str

        :return: MdScope representation of the text supplied
        :rtype: MdScope
        """
        if text.lower() == MdScope.SERIES.value.lower():
            return MdScope.SERIES
        if text.lower() == MdScope.UNDEFINED.value.lower():
            return MdScope.UNDEFINED
        if text.lower() == MdScope.FIELD_SESSION.value.lower():
            return MdScope.FIELD_SESSION
        if text.lower() == MdScope.COLLECTION_SESSION.value.lower():
            return MdScope.COLLECTION_SESSION
        if text.lower() == MdScope.DATASET.value.lower():
            return MdScope.DATASET
        if text.lower() == MdScope.FEATURE_TYPE.value.lower():
            return MdScope.FEATURE_TYPE
        if text.lower() == MdScope.FEATURE.value.lower():
            return MdScope.FEATURE
        if text.lower() == MdScope.ATTRIBUTE_TYPE.value.lower():
            return MdScope.ATTRIBUTE_TYPE
        if text.lower() == MdScope.ATTRIBUTE.value.lower():
            return MdScope.ATTRIBUTE
        if text.lower() == MdScope.TILE.value.lower():
            return MdScope.TILE
        if text.lower() == MdScope.MODEL.value.lower():
            return MdScope.MODEL
        if text.lower() == MdScope.CATALOG.value.lower():
            return MdScope.CATALOG
        if text.lower() == MdScope.SCHEMA.value.lower():
            return MdScope.SCHEMA
        if text.lower() == MdScope.TAXONOMY.value.lower():
            return MdScope.TAXONOMY
        if text.lower() == MdScope.SOFTWARE.value.lower():
            return MdScope.SOFTWARE
        if text.lower() == MdScope.SERVICE.value.lower():
            return MdScope.SERVICE
        if text.lower() == MdScope.COLLECTION_HARDWARE.value.lower():
            return MdScope.COLLECTION_HARDWARE
        if text.lower() == MdScope.NON_GEOGRAPHIC_DATASET.value.lower():
            return MdScope.NON_GEOGRAPHIC_DATASET
        if text.lower() == MdScope.DIMENSION_GROUP.value.lower():
            return MdScope.DIMENSION_GROUP

        raise ValueError("No MetadataScope that matches {text}".format(text=text))
