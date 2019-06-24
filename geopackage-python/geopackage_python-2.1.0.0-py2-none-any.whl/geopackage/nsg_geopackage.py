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

Authors:
    Steven D. Lander, Reinventing Geospatial Inc (RGi)
    Jenifer Cochran, Reinventing Geospatial Inc (RGi)
Date: 2018-11-11
   Requires: sqlite3, argparse
   Optional: Python Imaging Library (PIL or Pillow)
Credits:
  MapProxy imaging functions: http://mapproxy.org
  gdal2mb on github: https://github.com/developmentseed/gdal2mb

Version:
"""

from rgi.geopackage.core.geopackage_core_table_adapter import GeoPackageCoreTableAdapter
from rgi.geopackage.extensions.geopackage_extensions_table_adapter import GeoPackageExtensionsTableAdapter
from rgi.geopackage.geopackage import Geopackage, DEFAULT_TILES_IDENTIFIER
from rgi.geopackage.nsg.nsg_metadata_generator import Generator, BoundingBox
from rgi.geopackage.srs.geodetic_nsg import GeodeticNSG
from rgi.geopackage.tiles.geopackage_tiles_table_adapter import GeoPackageTilesTableAdapter
from rgi.geopackage.tiles.tiles_content_entry import TilesContentEntry
from rgi.geopackage.utility.sql_utility import get_database_connection

try:
    from cStringIO import StringIO as ioBuffer
except ImportError:
    from io import BytesIO as ioBuffer
from sys import version_info

if version_info[0] == 3:
    xrange = range

try:
    from PIL.Image import open as IOPEN
except ImportError:
    IOPEN = None


class NsgGeopackage(Geopackage):
    """
    Extension of the Geopackage class, restricts SRS, updated wkt for epsg 4326, additional metadata tables, as well as
    some changes to what goes into gpkg contents. kept separate for now, as the goal is to eventually roll the profile
    into the geopackage spec, and remove the need for an advanced profile.
    """

    def __init__(self, file_path, srs, tiles_table_name):
        super(NsgGeopackage, self).__init__(file_path=file_path,
                                            srs=srs,
                                            tiles_table_name=tiles_table_name)
        """Constructor."""
        self.__file_path = file_path
        self.__srs = srs
        # nsg profile only supported for 4326 for now in this script
        if self.__srs == GeodeticNSG().srs_id:
            self.__projection = GeodeticNSG()
        else:
            raise ValueError("SRS for NSG GeoPackages must be 4326")

        self.__db_con = get_database_connection(self.__file_path)
        self.tiles_table_name = tiles_table_name

    def __enter__(self):
        """With-statement caller"""
        return self

    def __exit__(self, type, value, traceback):
        """Resource cleanup on destruction."""
        super(NsgGeopackage, self).__exit__(type, value, traceback)
        self.__db_con.close()

    def initialize(self, populate_srs_extra_values=False):
        super(NsgGeopackage, self).initialize(False)
        self.__create_schema()

    def __create_schema(self, populate_srs_extra_values=False):
        """Create default geopackage schema on the database."""
        with self.__db_con as db_con:
            cursor = db_con.cursor()
            GeoPackageExtensionsTableAdapter.create_extensions_table(cursor=cursor)

    def update_metadata(self, metadata):
        """

        :param metadata:
        :type metadata: list of ZoomMetadata
        :return:
        """
        """Update the metadata of the geopackage database after tile merge."""
        # initialize a new projection
        super(NsgGeopackage, self).update_metadata(metadata=metadata)
        with self.__db_con as db_con:
            cursor = db_con.cursor()

            # write bounds and matrix set info to table
            bounds = self.__projection.bounds
            # tile matrix set needs the bounds of the srs
            tiles_content = TilesContentEntry(table_name=self.tiles_table_name,
                                              identifier=DEFAULT_TILES_IDENTIFIER,
                                              min_x=bounds[0],
                                              min_y=bounds[1],
                                              max_x=bounds[2],
                                              max_y=bounds[3],
                                              srs_id=self.__srs)

            GeoPackageTilesTableAdapter.insert_or_update_gpkg_tile_matrix_set_row(cursor,
                                                                                  tiles_content,
                                                                                  False)
            # create the metadata
            spatial_ref_system = next((srs
                                       for srs
                                       in GeoPackageCoreTableAdapter.get_all_spatial_reference_system_entries(cursor=cursor)
                                       if srs.srs_id == tiles_content.srs_id))

        self.__create_nmis_metadata(tiles_content, spatial_ref_system, self.file_path)

    @staticmethod
    def __create_nmis_metadata(content, srs, file_path):
        metadata_generator = Generator(file_path)
        metadata_generator.add_layer_identity(layer_table_name=content.table_name,
                                              abstract_msg="Created by tiles2gpkg_parallel.py, written by S. Lander and J. Cochran",
                                              BBOX=BoundingBox(min_x=content.min_x,
                                                               max_y=content.max_y,
                                                               max_x=content.max_x,
                                                               min_y=content.min_y),
                                              srs_id=str(srs.srs_id),
                                              srs_organization=srs.organization)
        metadata_generator.write_metadata()
