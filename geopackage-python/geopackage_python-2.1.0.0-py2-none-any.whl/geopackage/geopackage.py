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
from rgi.geopackage.srs.ellipsoidal_mercator import EllipsoidalMercator
from rgi.geopackage.srs.geodetic import Geodetic
from rgi.geopackage.srs.mercator import Mercator
from rgi.geopackage.srs.scaled_world_mercator import ScaledWorldMercator
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

from operator import attrgetter
from sqlite3 import Error, sqlite_version
from os import remove
from os.path import exists
from distutils.version import LooseVersion

PRAGMA_MINIMUM_SQLITE_VERSION = '3.7.17'

DEFAULT_TILES_IDENTIFIER = "Raster Tiles"


class Geopackage(object):
    """Object representing a GeoPackage container."""

    def __enter__(self):
        """With-statement caller"""
        return self

    def __init__(self, file_path, srs, tiles_table_name):
        """Constructor.
        :param tiles_table_name:
        """
        self.__file_path = file_path
        self.__srs = srs
        if self.__srs == Mercator.srs_identifier:
            self.__projection = Mercator()
        elif self.__srs == EllipsoidalMercator.srs_identifier:
            self.__projection = EllipsoidalMercator()
        elif self.__srs == ScaledWorldMercator.srs_identifier:
            self.__projection = ScaledWorldMercator()
        else:
            self.__projection = Geodetic()
        self.__db_con = get_database_connection(self.__file_path)
        self.tiles_table_name = tiles_table_name

    def initialize(self, populate_srs_extra_values=True):
        """Initialized the database schema. previously this was done in the __init__ constructor, however this
        caused issues with inheritance trying to change the schemas, rather than mess with deleting things as needed,
        just made the initilization a later step. """
        self.__create_schema(populate_srs_extra_values=populate_srs_extra_values)

    def __create_schema(self, populate_srs_extra_values=True):
        """Create default geopackage schema on the database."""
        with self.__db_con as db_con:
            cursor = db_con.cursor()
            GeoPackageCoreTableAdapter.create_core_tables(cursor)
            if populate_srs_extra_values:
                GeoPackageCoreTableAdapter.insert_spatial_reference_system_row(cursor, Mercator())
                GeoPackageCoreTableAdapter.insert_spatial_reference_system_row(cursor, EllipsoidalMercator())
                GeoPackageCoreTableAdapter.insert_spatial_reference_system_row(cursor, ScaledWorldMercator())

            if self.__srs == Mercator.srs_identifier:
                GeoPackageCoreTableAdapter.insert_spatial_reference_system_row(cursor, Mercator())
            elif self.__srs == EllipsoidalMercator.srs_identifier:
                GeoPackageCoreTableAdapter.insert_spatial_reference_system_row(cursor, EllipsoidalMercator())
            elif self.__srs == ScaledWorldMercator.srs_identifier:
                GeoPackageCoreTableAdapter.insert_spatial_reference_system_row(cursor, ScaledWorldMercator())

            GeoPackageTilesTableAdapter.create_default_tiles_tables(cursor)
            GeoPackageTilesTableAdapter.create_pyramid_user_data_table(cursor=cursor,
                                                                       tiles_content=TilesContentEntry(table_name=
                                                                                           self.tiles_table_name,
                                                                                           identifier=
                                                                                           DEFAULT_TILES_IDENTIFIER,
                                                                                           min_x=0,
                                                                                           min_y=0,
                                                                                           max_x=0,
                                                                                           max_y=0,
                                                                                           srs_id=self.__srs))
            cursor.execute("pragma foreign_keys = 1;")
            # Add GP10 to the Sqlite header
            if LooseVersion(sqlite_version) >= LooseVersion(PRAGMA_MINIMUM_SQLITE_VERSION):
                cursor.execute("pragma application_id = 1196437808;")

    @property
    def file_path(self):
        """Return the path of the geopackage database on the file system."""
        return self.__file_path

    def update_metadata(self, metadata):
        """Update the metadata of the geopackage database after tile merge."""
        # initialize a new projection
        with self.__db_con as db_con:
            cursor = db_con.cursor()

            # iterate through each zoom level object and assign
            # matrix data to table
            for level in metadata:
                GeoPackageTilesTableAdapter.insert_or_udpate_gpkg_tile_matrix_row(cursor=cursor,
                                                                                  table_name=self.tiles_table_name,
                                                                                  zoom_level=level.zoom,
                                                                                  matrix_width=level.matrix_width,
                                                                                  matrix_height=level.matrix_height,
                                                                                  tile_width=self.__projection.tile_size,
                                                                                  tile_height=self.__projection.tile_size,
                                                                                  pixel_x_size=self.__projection.pixel_x_size(
                                                                          level.zoom),
                                                                                  pixel_y_size=self.__projection.pixel_y_size(
                                                                          level.zoom))

            # get bounding box info based on
            top_level = max(metadata, key=attrgetter('zoom'))
            top_level.min_x = top_level.min_x
            top_level.min_y = top_level.min_y
            top_level.max_x = top_level.max_x
            top_level.max_y = top_level.max_y
            # write bounds and matrix set info to table
            GeoPackageTilesTableAdapter.insert_or_update_gpkg_tile_matrix_set_row(cursor,
                                                                                  TilesContentEntry(
                                                                          table_name=self.tiles_table_name,
                                                                          identifier=DEFAULT_TILES_IDENTIFIER,
                                                                          min_x=top_level.min_x,
                                                                          min_y=top_level.min_y,
                                                                          max_x=top_level.max_x,
                                                                          max_y=top_level.max_y,
                                                                          srs_id=self.__srs))

    def execute(self, statement, inputs=None):
        """Execute a prepared SQL statement on this geopackage database."""
        with self.__db_con as db_con:
            cursor = db_con.cursor()
            if inputs is not None:
                result_cursor = cursor.execute(statement, inputs)
            else:
                result_cursor = cursor.execute(statement)
            return result_cursor

    def assimilate(self, source):
        """Assimilate .gpkg.part tiles into this geopackage database."""
        if not exists(source):
            raise IOError
        self.__db_con = get_database_connection(self.__file_path)

        with self.__db_con as db_con:
            # needed in python3 to avoid operation error on ATTACH.
            db_con.isolation_level = None
            cursor = db_con.cursor()
            cursor.execute("pragma synchronous = off;")
            cursor.execute("pragma journal_mode = off;")
            cursor.execute("pragma page_size = 65536;")
            # print "Merging", source, "into", self.__file_path, "..."
            query = "attach '" + source + "' as source;"
            cursor.execute(query)

            try:
                cursor.execute("""INSERT OR REPLACE INTO '{table_name}'
                (zoom_level, tile_column, tile_row, tile_data)
                SELECT zoom_level, tile_column, tile_row, tile_data
                FROM 'source'.'{table_name}';""".format(table_name=self.tiles_table_name))
                cursor.execute("detach source;")
            except Error as err:
                print("Error: {}".format(type(err)))
                print("Error msg:".format(err))
                raise
            remove(source)

    def __exit__(self, type, value, traceback):
        """Resource cleanup on destruction."""
        self.__db_con.close()
