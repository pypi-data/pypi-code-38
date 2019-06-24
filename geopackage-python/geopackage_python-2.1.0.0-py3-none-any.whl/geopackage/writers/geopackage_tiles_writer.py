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
    Jenifer Cochran, Reinventing Geospatial Inc (RGi)
Date: 2018-11-11
   Requires: sqlite3, argparse
   Optional: Python Imaging Library (PIL or Pillow)
Credits:
  MapProxy imaging functions: http://mapproxy.org
  gdal2mb on github: https://github.com/developmentseed/gdal2mb

Version:
"""
import imghdr
import json
from uuid import uuid4

from rgi.geopackage.extensions.geopackage_extensions_table_adapter import GeoPackageExtensionsTableAdapter
from rgi.geopackage.extensions.vector_tiles.geopackage_geojson_vector_tiles_table_adapter import GeoPackageGeoJSONVectorTilesTableAdapter
from rgi.geopackage.extensions.vector_tiles.geopackage_mapbox_vector_tiles_table_adapter import GeoPackageMapBoxVectorTilesTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_tiles_content_entry import VectorTilesContentEntry
from rgi.geopackage.writers.geopackage_writer import GeoPackageWriter
from rgi.geopackage.tiles.geopackage_tiles_table_adapter import GeoPackageAbstractTilesTableAdapter
from rgi.geopackage.tiles.tile_data_information import TileDataInformation

try:
    from cStringIO import StringIO as ioBuffer
except ImportError:
    from io import BytesIO as ioBuffer

try:
    from cStringIO import StringIO as ioString
except ImportError:
    from io import StringIO as ioString

import mapbox_vector_tile
from enum import Enum

from rgi.geopackage.common.zoom_times_two import ZoomTimesTwo
from rgi.geopackage.core.geopackage_core_table_adapter import GeoPackageCoreTableAdapter
from rgi.geopackage.core.spatial_ref_system_entry import SpatialReferenceSystemEntry
from rgi.geopackage.srs.ellipsoidal_mercator import EllipsoidalMercator
from rgi.geopackage.srs.geodetic_nsg import GeodeticNSG
from rgi.geopackage.srs.mercator import Mercator
from rgi.geopackage.srs.scaled_world_mercator import ScaledWorldMercator
from rgi.geopackage.srs.undefined_cartesian_coord_ref_sys import UndefinedCartesianCoordinateReferenceSystem
from rgi.geopackage.srs.undefined_geographic_coord_ref_sys import UndefinedGeographicCoordinateReferenceSystem
from rgi.geopackage.tiles.geopackage_tiles_table_adapter import GeoPackageTilesTableAdapter
from rgi.geopackage.tiles.tile_matrix_entry import TileMatrixEntry
from rgi.geopackage.tiles.tiles_content_entry import TilesContentEntry, TILES_DATA_TYPE
from rgi.geopackage.utility.sql_utility import table_exists, synchronized
from sqlite3 import Binary


class WritingMode(Enum):
    SPEED_MODE = "Speed_Mode"  # will skip validation checks on each tile added and will trust the writer to have the
    # correct tile added each time.  Will also require additional information up front to make things even quicker
    VALIDATION_MODE = "Validation_Mode"  # will ensure accuracy on each tile added by reading the data as well as
    # checking other tables to ensure the references are valid. Will check to make sure the tiles are not of mixed
    # incompatible types.  This validation will take considerably longer


class TileType(Enum):
    """
    Tile encoding types that are supported in the GeoPackageTileWriter
    """
    PNG = "png",
    JPEG = "jpeg",
    MAPBOX = "mapbox",
    GEOJSON = "geojson"

    def is_raster_type(self):
        """
        Returns true if the tile type is of type raster. Which is either PNG or JPEG

        :return: True if the tile type is of type PNG or JPEG, false otherwise
        :rtype: bool
        """
        return self == TileType.PNG or self == TileType.JPEG

    def is_vector_tile_type(self):
        """
        Returns true if the tile type is of type vector-tiles. Which is either MapBox or GeoJSON

        :return: True if the tile type is of type MapBox or GeoJSON, false otherwise
        :rtype: bool
        """
        return self == TileType.MAPBOX or self == TileType.GEOJSON


class GeoPackageTilesWriter(GeoPackageWriter):
    """
       Writes raster or vector-tiles to a GeoPackage. Each instance will write to a single GeoPackage tiles table.
    """

    @synchronized
    def __init__(self,
                 gpkg_file_path,
                 tile_table_name,
                 srs_id,
                 srs_bounds,
                 tile_size=(256, 256),
                 tile_scheme=ZoomTimesTwo(base_matrix_width=1, base_matrix_height=1),
                 tile_data_bounding_box=None,
                 identifier=uuid4().hex,
                 timeout=500,
                 writing_mode=WritingMode.VALIDATION_MODE,
                 tile_type=None,
                 zoom_levels=range(22)):
        """
        Constructor

        :param gpkg_file_path: the path where the GeoPackage should be written to or an existing GeoPackage to write
        to
        :type gpkg_file_path: str

        :param tile_table_name:  The name of the tiles table to write to
        :type tile_table_name: str

        :param srs_id: the Spatial Reference System identifier (i.e. 4326, 3857)
        :type srs_id: int

        :param tile_size:  The size of the tiles in the form of a tuple (i.e. (256,256), (512,256) ) where the first
        value is the width and the second value is the height
        :type tile_size: ``int(width), int(height)``

        :param srs_bounds: The full bounds of the Spatial Reference System
        (i.e. for EPSG:4326 the bounds would be (min_x=-180.0,min_y=-90.0,max_x=180.0,max_y=90.0)
        :type srs_bounds: BoundingBox

        :param tile_data_bounding_box: (optional) The bounds of the tile data only.  If not specified the full bounds of the
        Spatial Reference System will be used.
        :type tile_data_bounding_box:BoundingBox

        :param tile_scheme: (optional) The tiling scheme of the data. Defines the dimensions or the grid by zoom level
        (i.e. zoom level 0 have 1 tile, zoom level 1 have 2 by 2 or 4 tiles, zoom level 2 have 4 by 4 or 16 tiles etc.)
        :type tile_scheme: TileScheme

        :param identifier: (optional) Human readable identifier to describe the tile set. Must be unique to all
        other gpkg_contents entries
        :type identifier: str

        :param writing_mode: (optional) Defaults to Validation mode where each tile is checked before writing to the
        GeoPackage.  This is considerably processing heavy to ensure the writer isn't mixing tile types and auto-
        detecting the tile being added each time.  If writing needs to happen quickly use Speed_Mode which bypasses
        the checks on writing tiles to the GeoPackage. If Speed_Mode is declared, then you MUST give a tile_type
        to the Constructor.
        :type writing_mode: WritingMode

        :param tile_type: (optional) Only needed if writing mode is Speed_Mode. MUST PROVIDE THIS VALUE IF IN SPEED MODE
        :type tile_type: TileType

        :param zoom_levels: (optional) Only needed if writing mode is Speed_Mode.
        :type zoom_levels: list of int
        """
        super(GeoPackageTilesWriter, self).__init__(gpkg_file_path=gpkg_file_path,
                                                    timeout=timeout)
        # save the variables
        self.tile_table_name = tile_table_name
        self.srs_bounds = srs_bounds
        self.data_bounds = tile_data_bounding_box if tile_data_bounding_box is not None else srs_bounds
        self.identifier = identifier
        self.tile_size = tile_size
        self.tile_scheme = tile_scheme
        self.writing_mode = writing_mode
        self.tile_type = tile_type
        self.zoom_levels = zoom_levels
        # create default tables if they do not exist
        GeoPackageCoreTableAdapter.create_core_tables(cursor=self._database_connection().cursor())

        if self.writing_mode == WritingMode.SPEED_MODE and self.tile_type is None:
            raise ValueError(
                "Cannot do speed mode without also setting the tile_type value. None was given as tile_type.")
        # ensure the identifier is a unique value
        existing_entry = GeoPackageCoreTableAdapter.get_content_entry_by_identifier(cursor=self._database_connection().cursor(),
                                                                                    identifier=identifier)
        if existing_entry is not None and \
                existing_entry.table_name != tile_table_name:
            raise ValueError("The identifier {identifier} describes another row in the gpkg_contents with a table_name"
                             " {table_name}. Identifier values must be unique."
                             .format(identifier=identifier,
                                     table_name=existing_entry.table_name))

        # TODO: logic is not quite correct.  Need to use the coord ref sys id not srs id.  Can query the table
        # for an srs_id to get the coord ref id or just ask user to give coord ref id ...more thoughts need to be
        # placed on this
        # set the spatial reference system variable
        if srs_id == EllipsoidalMercator.srs_identifier:
            self.spatial_reference_system = EllipsoidalMercator()
        elif srs_id == GeodeticNSG.srs_identifier:
            self.spatial_reference_system = GeodeticNSG()
        elif srs_id == Mercator.srs_identifier:
            self.spatial_reference_system = Mercator()
        elif srs_id == ScaledWorldMercator.srs_identifier:
            self.spatial_reference_system = ScaledWorldMercator()
        elif srs_id == UndefinedCartesianCoordinateReferenceSystem.srs_identifier:
            self.spatial_reference_system = UndefinedCartesianCoordinateReferenceSystem()
        elif srs_id == UndefinedGeographicCoordinateReferenceSystem.srs_identifier:
            self.spatial_reference_system = UndefinedGeographicCoordinateReferenceSystem()
        else:
            self.spatial_reference_system = SpatialReferenceSystemEntry(srs_name="EPSG:{0}".format(srs_id),
                                                                        srs_id=srs_id,
                                                                        organization_coordsys_id=srs_id,
                                                                        definition="",
                                                                        description="Added via GeoPackage-Python",
                                                                        organization="EPSG")
        # add the spatial reference system to the GeoPackage
        GeoPackageCoreTableAdapter.insert_spatial_reference_system_row(cursor=self._database_connection().cursor(),
                                                                       spatial_reference_system=self.spatial_reference_system)

        # add all default tables and matrix entries if in speed mode
        if self.writing_mode == WritingMode.SPEED_MODE:
            self._initialize_tables_by_tile_type()

        # commit changes to the GeoPackage
        self._database_connection().commit()

    def _initialize_tables_by_tile_type(self):
        # write the default tables etc. we are in speed mode
        tiles_creator = self.__get_tiles_creator_by_tile_type(self.tile_type)
        self.__add_default_tables(gpkg_tiles_creator=tiles_creator,
                                  tile_table_name=self.tile_table_name,
                                  tile_type=self.tile_type)

        for zoom in self.zoom_levels:
            self.__add_tile_matrix_entry_for_zoom_level(gpkg_tiles_creator=tiles_creator,
                                                        tile_zoom=zoom)

    @synchronized
    def add_tiles(self,
                  tiles):

        """
        Adds the tiles to the GeoPackage

        :param tiles: the list of tiles to add to the GeoPackage
        :return: list of TileDataInformation
        """
        if tiles is None or len(tiles) == 0:
            raise ValueError("The list of tiles cannot be empty or None.")

        if self.writing_mode == WritingMode.VALIDATION_MODE:
            # check valid tile types: no mixing of vector and raster, AND no mixing of the two different vector tiles
            for index, tile in enumerate(tiles):
                for second_index, second_tile in enumerate(tiles, start=index + 1):
                    tile_type1 = self.get_tile_type_from_data(tile_data=tile.tile_data)
                    tile_type2 = self.get_tile_type_from_data(tile_data=second_tile.tile_data)
                    are_compatible, message = self.__are_tile_types_compatible(tile_type1=tile_type1,
                                                                               tile_type2=tile_type2)
                    if not are_compatible:
                        raise ValueError(message)
            # since all the tile types compatible, just grab the first one
            tile_type = self.get_tile_type_from_data(tiles[0].tile_data)

            # check the contents table- if the table was already created then we should check the tile type matches
            # what is already there
            contents_tile_type = self.__get_tile_type_by_contents_entry(self._database_connection(),
                                                                        self.tile_table_name)
            if contents_tile_type is not None:
                is_compatible, message = self.__are_tile_types_compatible(tile_type, contents_tile_type)
                if not is_compatible:
                    raise ValueError(message)
            gpkg_tiles_creator = self.__get_tiles_creator_by_tile_type(tile_type=tile_type)

            self.__add_default_tables(gpkg_tiles_creator=gpkg_tiles_creator,
                                      tile_table_name=self.tile_table_name,
                                      tile_type=tile_type)

            # add matrix entries
            for tile in tiles:
                matrix_entry = self.__add_tile_matrix_entry_for_zoom_level(gpkg_tiles_creator=gpkg_tiles_creator,
                                                                           tile_zoom=tile.zoom_level)

                self.__check_valid_range_tile_row_tle_column_for_matrix_entry(matrix_entry=matrix_entry,
                                                                              tile_row=tile.tile_row,
                                                                              tile_column=tile.tile_column)
        elif self.writing_mode == WritingMode.SPEED_MODE:
            gpkg_tiles_creator = self.__get_tiles_creator_by_tile_type(tile_type=self.tile_type)
        else:
            raise ValueError("Invalid Writing Mode")
        # add the tile data
        gpkg_tiles_creator.insert_or_update_tile_data_bulk(cursor=self._database_connection().cursor(),
                                                           table_name=self.tile_table_name,
                                                           tiles=[TileDataInformation(tile_column=tile.tile_column,
                                                                                      tile_row=tile.tile_row,
                                                                                      tile_zoom=tile.zoom_level,
                                                                                      tile_data=tile.tile_data)
                                                                  for tile in tiles])

        self._database_connection().commit()

    @synchronized
    def add_tile(self,
                 tile_row,
                 tile_column,
                 tile_zoom,
                 tile_data):
        """
        Adds the tile to the GeoPackage.  The tile coordinates must be of Tile Origin upper left.

        :param tile_row: the y coordinate of the tile. 0 to tile_matrix matrix_height - 1
        :type tile_row: int

        :param tile_column: the x coordinate of the tile.  0 to tile_matrix matrix_width - 1
        :type tile_column: int

        :param tile_zoom: the zoom level of the tile (z coordinate)
        :type tile_zoom: int

        :param tile_data: the tile data encoded in JPEG, PNG, MapBox Vector Tile (.pbf), or GeoJSON
        :type tile_data: Binary
        """
        self.add_tiles(tiles=[
            TileDataInformation(tile_column=tile_column, tile_row=tile_row, tile_zoom=tile_zoom, tile_data=tile_data)])

    @synchronized
    def add_tile_by_coordinate(self,
                               tile_cooordinate,
                               tile_data):
        """
        Adds the tile to the GeoPackage.  The tile coordinates must be of Tile Origin upper left.

        :param tile_cooordinate: The tile coordinate (where the tile origin is Upper Left) of the tile to insert
        :type tile_cooordinate: TileCoordinate

        :param tile_data:  the tile data encoded in JPEG, PNG, MapBox Vector Tile (.pbf), or GeoJSON
        :type tile_data: Binary
        """
        self.add_tile(tile_row=tile_cooordinate.tile_row,
                      tile_column=tile_cooordinate.tile_column,
                      tile_zoom=tile_cooordinate.zoom_level,
                      tile_data=tile_data)

    @synchronized
    def remove_tile(self,
                    tile):
        """
        Removes the tile from the table with the given tile coordinates

        :param tile: the tile coordinate of the tile that should be removed
        :type tile: TileCoordinate
        """
        if not table_exists(cursor=self._database_connection().cursor(),
                            table_name=self.tile_table_name):
            raise ValueError("Must add tiles first before attempting to remove any.")

        # get the tiles type creator
        if self.writing_mode == WritingMode.SPEED_MODE:
            gpkg_tiles_creator = self.__get_tiles_creator_by_tile_type(self.tile_type)
        else:
            gpkg_tiles_creator = self.__get_tiles_creator_by_contents_entry(self._database_connection(),
                                                                            self.tile_table_name)

        gpkg_tiles_creator.delete_tile_data(cursor=self._database_connection().cursor(),
                                            table_name=self.tile_table_name,
                                            zoom_level=tile.zoom_level,
                                            tile_row=tile.tile_row,
                                            tile_column=tile.tile_column,
                                            check_matrix_deletion=self.writing_mode != WritingMode.SPEED_MODE)
        self._database_connection().commit()

    @synchronized
    def remove_zoom_levels(self,
                           zoom_levels):
        """
        Removes all the tiles at the given zoom levels.

        :param zoom_levels: the zoom_levels (z coordinates) to remove
        :type zoom_levels: list of int
        """
        if not table_exists(cursor=self._database_connection().cursor(),
                            table_name=self.tile_table_name):
            raise ValueError("Must add tiles first before attempting to remove any.")

        # check contents table for data_type tiles, otherwise if vector-tiles must then check the extension next to
        # see which type
        if self.writing_mode == WritingMode.SPEED_MODE:
            gpkg_tiles_creator = self.__get_tiles_creator_by_tile_type(self.tile_type)
        else:
            gpkg_tiles_creator = self.__get_tiles_creator_by_contents_entry(self._database_connection(),
                                                                            self.tile_table_name)

        for zoom_level in zoom_levels:
            gpkg_tiles_creator.delete_zoom_level(cursor=self._database_connection().cursor(),
                                                 tile_table_name=self.tile_table_name,
                                                 zoom_level=zoom_level)
        self._database_connection().commit()

    def get_tile(self,
                 tile):
        """
        Retrieves the tile from the table with the given tile coordinate

        :param tile: the tile coordinate of the tile to retrieve
        :type tile: TileCoordinate

        :rtype: TileDataInformation
        """
        tiles = self.get_all_tiles([tile])
        return None if len(tiles) <= 0 else tiles[0]

    def get_all_tiles(self,
                      tiles):
        """
        Returns a list of TileDataInformation of all the tiles requested by their tile coordinate values.

        :param tiles: the list of tile coordinates that are being requested for the tile data
        :type tiles: list of TileCoordinate

        :rtype: list of TileDataInformation
        :return: the list of tiles found in the table with the tile coordinate given
        """
        # if the table doesn't exist, no tiles exist either
        if not self.does_tiles_table_exist():
            return []

        # load tiles in bulk
        if self.writing_mode == WritingMode.SPEED_MODE:
            gpkg_tiles_creator = self.__get_tiles_creator_by_tile_type(self.tile_type)
        else:
            gpkg_tiles_creator = self.__get_tiles_creator_by_contents_entry(self._database_connection(),
                                                                            self.tile_table_name)

        return gpkg_tiles_creator.get_all_tile_data(cursor=self._database_connection().cursor(),
                                                    tile_table_name=self.tile_table_name,
                                                    tiles=tiles)

    def get_gpkg_contents_entry(self):
        """
        Returns the entry in the gpkg_contents table for this tiles table

        :rtype: TilesContentEntry
        """
        return GeoPackageCoreTableAdapter.get_content_entry_by_table_name(cursor=self._database_connection().cursor(),
                                                                          table_name=self.tile_table_name)

    def get_srs_entry_by_id(self,
                            srs_id):
        """
        Returns the SpatialReferenceSystemEntry in the gpkg_spatial_ref_sys table with the srs_id given

        :rtype: SpatialReferenceSystemEntry
        """
        return GeoPackageCoreTableAdapter.get_spatial_reference_system_by_srs_id(cursor=self._database_connection().cursor(),
                                                                                 srs_id=srs_id)

    def does_tiles_table_exist(self):
        """
        Returns true if the tiles table exists, false otherwise

        :rtype: bool
        """

        return table_exists(self._database_connection().cursor(),
                            self.tile_table_name)

    @staticmethod
    def __are_tile_types_compatible(tile_type1, tile_type2):
        """
        Returns true if the tiles types are compatible (the same or able to be mixed together) with a blank message,
        false otherwise with a message what is incorrect

        :param tile_type1: the first tile type to compare to
        :type tile_type1: TileType

        :param tile_type2: the second tile type to compare
        :type tile_type2: TileType

        :return: Returns true if the tiles types are compatible (the same or able to be mixed together) with a blank
        message, false otherwise with a message what is incorrect
        :rtype: tuple(bool, str)
        """
        # check to see if there is a mix of raster and vector types, not allowed!
        if (tile_type1.is_raster_type() and tile_type2.is_vector_tile_type()) or \
                (tile_type1.is_vector_tile_type() and tile_type2.is_raster_type()):
            return False, "Cannot mix writing vector-tiles and raster tiles with the same GeoPackage Writer."

        # check to make sure if it is a vector type, it is the same
        if tile_type1.is_vector_tile_type() and tile_type2.is_vector_tile_type():
            if tile_type1 != tile_type2:
                return False, "Cannot mix two different types of vector-tile data encodings. Must all be GeoJSON " \
                              "vector tiles or MapBox vector tiles."
        return True, ""

    @staticmethod
    def get_tile_type_from_data(tile_data):
        """
        Determines the tile type based on the encoded data. Throws a ValueError if unable to determine the type.

        :param tile_data: the tile data to determine the encoding of
        :type tile_data: Binary

        :rtype: TileType
        """
        decoded_tile_data = ioBuffer(tile_data).read() if type(tile_data) != str else ioString(tile_data).read()

        # check to see if it is raster data
        mime_type = None
        try:
            mime_type = imghdr.what(file=None, h=decoded_tile_data)
        except:
            pass

        if mime_type is not None:
            if mime_type is 'png':
                return TileType.PNG
            elif mime_type is 'jpeg':
                return TileType.JPEG
            elif mime_type is not None:
                raise ValueError("Unsupported encoded data type: {type}".format(type=mime_type))

        # check to see if it is mapbox vector tile data
        try:
            if len(mapbox_vector_tile.decode(tile_data)) != 0:
                return TileType.MAPBOX
        except:
            pass

        # check to see if it is GeoJSON data
        try:
            json.loads(decoded_tile_data)
            return TileType.GEOJSON
        except ValueError:
            pass
        raise ValueError("Unsupported tile_data. Is not one of the following {types}"
                         .format(types=", ".join([tile_type.value[0]
                                                  for tile_type
                                                  in TileType])))

    @staticmethod
    def calc_resolutions(bounding_box,
                         tile_size,
                         zoom_level,
                         tile_scheme):
        """
        Returns the pixel_x_size, pixel_y_size given the following values.

        :param tile_scheme: Gives the dimensions of the tile grid given a zoom level
        :type tile_scheme: TileScheme

        :param bounding_box:  The bounds of the data in the CRS coordinates (meters, decimal degrees etc.)
        :type bounding_box: BoundingBox

        :ivar tile_size: the size of each tile in pixel
        :type tile_size: ``int(with), int(height)``

        :param zoom_level: the zoom level to calculate the resolution for
        :type zoom_level: int

        :return: tuple of pixel_x_size and pixel_y_size
        :rtype: tuple(float, float)
        """

        width = float(bounding_box.max_x - bounding_box.min_x)
        height = float(bounding_box.max_y - bounding_box.min_y)

        matrix_width, matrix_height = tile_scheme.get_matrix_dimensions(zoom_level=zoom_level)

        return ((width / float(tile_size[0])) / float(matrix_width)), \
               ((height / float(tile_size[1])) / float(matrix_height))

    @staticmethod
    def __check_valid_range_tile_row_tle_column_for_matrix_entry(matrix_entry,
                                                                 tile_row,
                                                                 tile_column):
        """
        Checks to see if the tile_row and tile_column are in a valid range according to the tile matrix entry given.
        Will raise an exception if there is an invalid value.

        :param matrix_entry:
        :type matrix_entry: list of TileMatrixEntry

        :param tile_row: the y coordinate of the tile. 0 to tile_matrix matrix_height - 1
        :type tile_row: int

        :param tile_column: the x coordinate of the tile.  0 to tile_matrix matrix_width - 1
        :type tile_column: int
        """

        if tile_column < 0 or tile_column > matrix_entry[0].matrix_width - 1:
            raise ValueError("tile_column {tile_column} needs to be within the range of the matrix_width "
                             "[0, {width}]".format(tile_column=tile_column,
                                                   width=matrix_entry[0].matrix_width - 1))
        elif tile_row < 0 or tile_row > matrix_entry[0].matrix_height - 1:
            raise ValueError("tile_row {tile_row} needs to be within the range of the matrix_height "
                             "[0, {height}]".format(tile_row=tile_row,
                                                    height=matrix_entry[0].matrix_height - 1))

    def __add_tile_matrix_entry_for_zoom_level(self,
                                               gpkg_tiles_creator,
                                               tile_zoom):
        """
        Adds a tile matrix entry for the given zoom level.  If the matrix entry for the zoom level already exists, will
        not add another.

        :return: the gpkg tiles creator associated with the encoding specified
        :rtype: GeoPackageTiles

        :param tile_zoom: the zoom level the tile matrix entry should be added for
        :type tile_zoom: int
        :return: the tile matrix entry created or found
        :rtype: list of TileMatrixEntry
        """
        # add tile matrix
        self.__add_tile_matrix_entry(tile_zoom=tile_zoom,
                                     gpkg_tiles_creator=gpkg_tiles_creator)

        if self.writing_mode == WritingMode.VALIDATION_MODE:
            # check to make sure the tile_row and tile_column are within the matrix dimensions
            matrix_entry = gpkg_tiles_creator.get_tile_matrix_for_zoom_level(cursor=self._database_connection()
                                                                             .cursor(),
                                                                             zoom_level=tile_zoom,
                                                                             tile_table_name=self.tile_table_name)
            if len(matrix_entry) > 1 or len(matrix_entry) < 0:
                # problem there should only be 1 matrix
                raise ValueError(
                    "There are multiple entries in the gpkg_tile_matrix table for this zoom_level and tiles "
                    "table name. There should only be one per zoom per tiles table. Remove the entries that "
                    "are invalid and try to add to the tiles table again.")

            return matrix_entry

    def __add_default_tables(self,
                             gpkg_tiles_creator,
                             tile_table_name,
                             tile_type):
        """
        Adds the default tables needed to add the tile to the GeoPackage

        :param gpkg_tiles_creator: the tile creator for the correct tables
        :type gpkg_tiles_creator: GeoPackageTilesTableAdapter

        :param tile_table_name: the name of the tiles table
        :type tile_table_name: str

        :param tile_type: the type of tile encoding
        :type tile_type: TileType
        """
        # check to make sure the tile pyramid user data table exists
        if not table_exists(cursor=self._database_connection().cursor(),
                            table_name=tile_table_name):
            self.__add_tile_pyramid_user_data_table(gpkg_tiles_creator=gpkg_tiles_creator,
                                                    tile_type=tile_type)
        else:
            # add the default tiles tables
            gpkg_tiles_creator.create_default_tiles_tables(cursor=self._database_connection().cursor())

        # if the tiles table does not have a an entry in the gpkg_contents table, create an entry
        if GeoPackageCoreTableAdapter.get_content_entry_by_table_name(cursor=self._database_connection().cursor(),
                                                                      table_name=tile_table_name) is None:
            tiles_content = TilesContentEntry(table_name=self.tile_table_name,
                                              identifier=self.identifier,
                                              min_x=self.data_bounds.min_x,
                                              min_y=self.data_bounds.min_y,
                                              max_x=self.data_bounds.max_x,
                                              max_y=self.data_bounds.max_y,
                                              srs_id=self.spatial_reference_system.srs_id) if tile_type.is_raster_type() \
                else VectorTilesContentEntry(table_name=self.tile_table_name,
                                             identifier=self.identifier,
                                             min_x=self.data_bounds.min_x,
                                             min_y=self.data_bounds.min_y,
                                             max_x=self.data_bounds.max_x,
                                             max_y=self.data_bounds.max_y,
                                             srs_id=self.spatial_reference_system.srs_id)
            GeoPackageCoreTableAdapter.insert_or_update_content(cursor=self._database_connection().cursor(),
                                                                content=tiles_content)

        # if the tiles table does not have a an entry in the gpkg_tile_matrix_set table, create an entry
        if gpkg_tiles_creator.get_tile_matrix_set_entry_by_table_name(cursor=self._database_connection().cursor(),
                                                                      tile_table_name=tile_table_name) is None:
            matrix_content = TilesContentEntry(table_name=self.tile_table_name,
                                               identifier=self.identifier,
                                               min_x=self.srs_bounds.min_x,
                                               min_y=self.srs_bounds.min_y,
                                               max_x=self.srs_bounds.max_x,
                                               max_y=self.srs_bounds.max_y,
                                               srs_id=self.spatial_reference_system.srs_id) if tile_type.is_raster_type() \
                else VectorTilesContentEntry(table_name=self.tile_table_name,
                                             identifier=self.identifier,
                                             min_x=self.srs_bounds.min_x,
                                             min_y=self.srs_bounds.min_y,
                                             max_x=self.srs_bounds.max_x,
                                             max_y=self.srs_bounds.max_y,
                                             srs_id=self.spatial_reference_system.srs_id)
            gpkg_tiles_creator.insert_or_update_gpkg_tile_matrix_set_row(cursor=self._database_connection().cursor(),
                                                                         tiles_content=matrix_content)

    def __add_tile_matrix_entry(self,
                                tile_zoom,
                                gpkg_tiles_creator):
        """
        Adds the Tile Matrix entry to the GeoPackage if one does not currently exist for the zoom level

        :param tile_zoom: the zoom level that needs a tile matrix entry
        :type tile_zoom: int

        :param gpkg_tiles_creator: the GeoPackageTiles creator
        :type gpkg_tiles_creator: GeoPackageTilesTableAdapter
        """
        if len(gpkg_tiles_creator.get_tile_matrix_for_zoom_level(cursor=self._database_connection().cursor(),
                                                                 tile_table_name=self.tile_table_name,
                                                                 zoom_level=tile_zoom)) < 1:
            # add tile matrix
            matrix_width, matrix_height = self.tile_scheme.get_matrix_dimensions(zoom_level=tile_zoom)

            pixel_x_size, pixel_y_size = GeoPackageTilesWriter.calc_resolutions(bounding_box=self.srs_bounds,
                                                                                tile_size=self.tile_size,
                                                                                zoom_level=tile_zoom,
                                                                                tile_scheme=self.tile_scheme)

            gpkg_tiles_creator.insert_or_update_gpkg_tile_matrix_row(cursor=self._database_connection().cursor(),
                                                                     tile_matrix_entry=TileMatrixEntry(
                                                                         table_name=self.tile_table_name,
                                                                         zoom_level=tile_zoom,
                                                                         matrix_height=matrix_height,
                                                                         matrix_width=matrix_width,
                                                                         tile_height=self.tile_size[1],
                                                                         tile_width=self.tile_size[0],
                                                                         pixel_x_size=pixel_x_size,
                                                                         pixel_y_size=pixel_y_size))

    def __add_tile_pyramid_user_data_table(self, gpkg_tiles_creator, tile_type):
        """
        Adds the pyramid user data table and includes the information in the gpkg_contents table as well as the
        gpkg_tile_matrix_set table

        :param gpkg_tiles_creator: the GeoPackage Tiles creator
        :type gpkg_tiles_creator: GeoPackageTilesTableAdapter

        :param tile_type:
        :type tile_type: TileType
        """
        tiles_content = TilesContentEntry(table_name=self.tile_table_name,
                                          identifier=self.identifier,
                                          min_x=self.data_bounds.min_x,
                                          min_y=self.data_bounds.min_y,
                                          max_x=self.data_bounds.max_x,
                                          max_y=self.data_bounds.max_y,
                                          srs_id=self.spatial_reference_system.srs_id) if tile_type.is_raster_type() \
            else VectorTilesContentEntry(table_name=self.tile_table_name,
                                         identifier=self.identifier,
                                         min_x=self.data_bounds.min_x,
                                         min_y=self.data_bounds.min_y,
                                         max_x=self.data_bounds.max_x,
                                         max_y=self.data_bounds.max_y,
                                         srs_id=self.spatial_reference_system.srs_id)

        gpkg_tiles_creator.create_pyramid_user_data_table(cursor=self._database_connection().cursor(),
                                                          tiles_content=tiles_content)

        matrix_content = TilesContentEntry(table_name=self.tile_table_name,
                                           identifier=self.identifier,
                                           min_x=self.srs_bounds.min_x,
                                           min_y=self.srs_bounds.min_y,
                                           max_x=self.srs_bounds.max_x,
                                           max_y=self.srs_bounds.max_y,
                                           srs_id=self.spatial_reference_system.srs_id) if tile_type.is_raster_type() \
            else VectorTilesContentEntry(table_name=self.tile_table_name,
                                         identifier=self.identifier,
                                         min_x=self.srs_bounds.min_x,
                                         min_y=self.srs_bounds.min_y,
                                         max_x=self.srs_bounds.max_x,
                                         max_y=self.srs_bounds.max_y,
                                         srs_id=self.spatial_reference_system.srs_id)

        gpkg_tiles_creator.insert_or_update_gpkg_tile_matrix_set_row(cursor=self._database_connection().cursor(),
                                                                     tiles_content=matrix_content,
                                                                     update_contents_table=False)

    @classmethod
    def __get_tiles_creator_by_contents_entry(cls, database_connection, tile_table_name):
        """
        Gets the Tiles Creator based on the values already existing in the GeoPackage.  The table must already exist
        and an entry should be in the gpkg_contents table

        :param database_connection: the connection to the database
        :type database_connection: Cursor

        :param tile_table_name: the name of the tiles table
        :type tile_table_name: str

        :rtype: GeoPackageAbstractTilesTableAdapter
        """
        tile_type = cls.__get_tile_type_by_contents_entry(database_connection=database_connection,
                                                          tile_table_name=tile_table_name)

        if tile_type is None:

            raise ValueError("No entry exists for this table. Cannot determine the tiles type if no entry exists.")

        # geopackage tiles
        elif tile_type.is_raster_type():

            gpkg_tiles_creator = GeoPackageTilesTableAdapter()

        # check if vector-tiles- geojson
        elif tile_type == TileType.GEOJSON:

            gpkg_tiles_creator = GeoPackageGeoJSONVectorTilesTableAdapter(vector_tiles_table_name=tile_table_name)
        # check if vector-tiles- Mapbox
        elif tile_type == TileType.MAPBOX:

            gpkg_tiles_creator = GeoPackageMapBoxVectorTilesTableAdapter(vector_tiles_table_name=tile_table_name)
        # or the entry in the table has a value that is unrecognized
        else:
            raise ValueError("The entry in the contents table has an unsupported tiles type.")

        return gpkg_tiles_creator

    def __get_tiles_creator_by_tile_type(self,
                                         tile_type):
        """
        Gets the gpkg tiles creator associated with the encoding specified

        :param tile_type: the tile type encoding
        :type tile_type: TileType

        :return: the gpkg tiles creator associated with the encoding specified
        :rtype: GeoPackageTilesTableAdapter
        """

        if tile_type == TileType.JPEG or tile_type == TileType.PNG:
            # raster tiles
            gpkg_tiles_creator = GeoPackageTilesTableAdapter()

        elif tile_type == TileType.MAPBOX:
            # map box vector tiles
            gpkg_tiles_creator = GeoPackageMapBoxVectorTilesTableAdapter(vector_tiles_table_name=self.tile_table_name)

        elif tile_type == TileType.GEOJSON:
            # geojson vector tiles
            gpkg_tiles_creator = GeoPackageGeoJSONVectorTilesTableAdapter(vector_tiles_table_name=self.tile_table_name)

        else:
            raise ValueError("Unsupported Tile type {type}. Unable to add tile data".format(type=tile_type))

        return gpkg_tiles_creator

    @classmethod
    def __get_tile_type_by_contents_entry(cls, database_connection, tile_table_name):
        """
        Returns the tile type based on what already exists in the geopackage. Returns None if there are no entries
        in the geopackage with the table name given.

        :param database_connection: connection to the database
        :type database_connection: Cursor
        :param tile_table_name: the name of the tiles table
        :type tile_table_name: str
        :rtype: TileType, None
        """
        content_entry = GeoPackageCoreTableAdapter.get_content_entry_by_table_name(cursor=database_connection.cursor(),
                                                                                   table_name=tile_table_name)
        if content_entry is None:
            return None
        # geopackage tiles
        if content_entry.data_type == TILES_DATA_TYPE:

            return TileType.PNG

        # check if vector-tiles- geojson
        elif GeoPackageExtensionsTableAdapter.has_extension(cursor=database_connection.cursor(),
                                                            extension=GeoPackageGeoJSONVectorTilesTableAdapter(
                                                    vector_tiles_table_name=tile_table_name)):

            return TileType.GEOJSON
        # check if vector-tiles- Mapbox
        elif GeoPackageExtensionsTableAdapter.has_extension(cursor=database_connection.cursor(),
                                                            extension=GeoPackageMapBoxVectorTilesTableAdapter(
                                                    vector_tiles_table_name=tile_table_name)):
            return TileType.MAPBOX
        else:
            geojson_extension = GeoPackageGeoJSONVectorTilesTableAdapter(vector_tiles_table_name=tile_table_name)
            mapbox_extension = GeoPackageMapBoxVectorTilesTableAdapter(vector_tiles_table_name=tile_table_name)

            raise ValueError("The existing entry in the contents table has an unsupported tiles type or no supported "
                             "Extension.\n Accepted data_type: {raster_tiles}. "
                             "\nAccepted Extensions: "
                             "\n MapBox (table_name, column_name, extension_name) "
                             "({mb_table_name}, {mb_column_name}, {mb_extension_name}) OR"
                             "\n GeoJSON (table_name, column_name, extension_name) "
                             "({gj_table_name}, {gj_column_name}, {gj_extension_name})"
                             .format(raster_tiles=TILES_DATA_TYPE,
                                     mb_table_name=mapbox_extension.table_name,
                                     mb_column_name=mapbox_extension.column_name,
                                     mb_extension_name=mapbox_extension.extension_name,
                                     gj_table_name=geojson_extension.table_name,
                                     gj_column_name=geojson_extension.column_name,
                                     gj_extension_name=geojson_extension.extension_name))
