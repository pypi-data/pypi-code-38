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
from abc import abstractmethod
from sqlite3 import Cursor, Binary

from rgi.geopackage.tiles.tile_data_information import TileDataInformation

from rgi.geopackage.core.geopackage_core_table_adapter import GeoPackageCoreTableAdapter
from rgi.geopackage.tiles.tile_matrix_entry import TileMatrixEntry
from rgi.geopackage.tiles.tile_matrix_set_entry import TileMatrixSetEntry
from rgi.geopackage.tiles.tiles_content_entry import TilesContentEntry
from rgi.geopackage.utility.sql_column_query import SqlColumnQuery
from rgi.geopackage.utility.sql_utility import table_exists, select_query, insert_or_update_row, delete_row, delete_rows

GEOPACKAGE_TILE_MATRIX_TABLE_NAME = "gpkg_tile_matrix"
GEOPACKAGE_TILE_MATRIX_SET_TABLE_NAME = "gpkg_tile_matrix_set"


class GeoPackageAbstractTilesTableAdapter(object):
    """
    'Tiles' subsystem of the GeoPackage implementation.  Responsible for the gpkg_tile_matrix, gpkg_tile_matrix_set, and
    user pyramid data tables.
    """

    def __init__(self):
        """
        Constructor
        """
        super(GeoPackageAbstractTilesTableAdapter, self).__init__()


    @staticmethod
    def create_gpkg_tile_matrix(cursor):
        """
        Creates the gpkg_tile_matrix table documents the structure of the tile matrix at each zoom level in each tiles
        table. It allows GeoPackages to contain rectangular as well as square tiles (e.g. for better representation of
        polar regions). It allows tile pyramids with zoom levels that differ in resolution by factors of 2, irregular
        intervals, or regular intervals other than factors of 2.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor
        """
        cursor.execute("""
               CREATE TABLE IF NOT EXISTS {table_name}
               (table_name    TEXT    NOT NULL, -- Tile Pyramid User Data Table Name
                zoom_level    INTEGER NOT NULL, -- 0 <= zoom_level <= max_level for table_name
                matrix_width  INTEGER NOT NULL, -- Number of columns (>= 1) in tile matrix at this zoom level
                matrix_height INTEGER NOT NULL, -- Number of rows (>= 1) in tile matrix at this zoom level
                tile_width    INTEGER NOT NULL, -- Tile width in pixels (>= 1) for this zoom level
                tile_height   INTEGER NOT NULL, -- Tile height in pixels (>= 1) for this zoom level
                pixel_x_size  DOUBLE  NOT NULL, -- In t_table_name srid units or default meters for srid 0 (>0)
                pixel_y_size  DOUBLE  NOT NULL, -- In t_table_name srid units or default meters for srid 0 (>0)
                CONSTRAINT pk_ttm PRIMARY KEY (table_name, zoom_level), CONSTRAINT fk_tmm_table_name FOREIGN KEY (table_name) REFERENCES gpkg_contents(table_name))
             """.format(table_name=GEOPACKAGE_TILE_MATRIX_TABLE_NAME))

    @staticmethod
    def create_gpkg_tile_matrix_set(cursor):
        """
        Creates the gpkg_tile_matrix_set table defines the spatial reference system (srs_id) and the maximum bounding
        box (min_x, min_y, max_x, max_y) for all possible tiles in a tile pyramid user data table.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor
        """
        cursor.execute("""
               CREATE TABLE IF NOT EXISTS {table_name}
               (table_name TEXT    NOT NULL PRIMARY KEY, -- Tile Pyramid User Data Table Name
                srs_id     INTEGER NOT NULL,             -- Spatial Reference System ID: gpkg_spatial_ref_sys.srs_id
                min_x      DOUBLE  NOT NULL,             -- Bounding box minimum easting or longitude for all content in table_name
                min_y      DOUBLE  NOT NULL,             -- Bounding box minimum northing or latitude for all content in table_name
                max_x      DOUBLE  NOT NULL,             -- Bounding box maximum easting or longitude for all content in table_name
                max_y      DOUBLE  NOT NULL,             -- Bounding box maximum northing or latitude for all content in table_name
                CONSTRAINT fk_gtms_table_name FOREIGN KEY (table_name) REFERENCES gpkg_contents(table_name), CONSTRAINT fk_gtms_srs FOREIGN KEY (srs_id) REFERENCES gpkg_spatial_ref_sys (srs_id))
             """.format(table_name=GEOPACKAGE_TILE_MATRIX_SET_TABLE_NAME))

    @staticmethod
    @abstractmethod
    def create_default_tiles_tables(cursor):
        """
        Creates the default relational tables for the pyramid-user-data table (i.e. gpkg_tile_matrix, gpkg_tile_matrix_set etc..)
        :param cursor:  the cursor to the GeoPackage database's connection
        """
        raise NotImplementedError()

    @classmethod
    def create_pyramid_user_data_table(cls,
                                       cursor,
                                       tiles_content):
        """
        Creates the tile pyramid user data table containing the tile data. "Tile pyramid" refers to the concept of
        pyramid structure of tiles of different spatial extent and resolution at different zoom levels, and the tile
        data itself. "Tile" refers to an individual raster image such as a PNG or JPEG that covers a specific geographic
        area.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param tiles_content: The TileSet entry in the gpkg_contents table describing the tiles in the GeoPackage
        :type tiles_content: TilesContentEntry
        """

        if table_exists(cursor=cursor,
                        table_name=tiles_content.table_name):
            raise ValueError("Table {table_name} already exists! Cannot create another table by the same name."
                             .format(table_name=tiles_content.table_name))
        cls.create_default_tiles_tables(cursor=cursor)
        # create the tiles table
        cursor.execute("""
                          CREATE TABLE IF NOT EXISTS "{table_name}" 
                          (id          INTEGER PRIMARY KEY AUTOINCREMENT, -- Autoincrement primary key
                           zoom_level  INTEGER NOT NULL,                  -- min(zoom_level) <= zoom_level <= max(zoom_level) for t_table_name
                           tile_column INTEGER NOT NULL,                  -- 0 to tile_matrix matrix_width - 1
                           tile_row    INTEGER NOT NULL,                  -- 0 to tile_matrix matrix_height - 1
                           tile_data   BLOB    NOT NULL,                  -- Of an image MIME type specified in clauses Tile Encoding PNG, Tile Encoding JPEG, Tile Encoding WEBP
                           UNIQUE (zoom_level, tile_column, tile_row))
                       """.format(table_name=tiles_content.table_name))

        # add to contents table
        GeoPackageCoreTableAdapter.insert_or_update_content(cursor=cursor,
                                                            content=tiles_content)

    @classmethod
    def insert_or_udpate_gpkg_tile_matrix_row(cls,
                                              cursor,
                                              table_name,
                                              zoom_level,
                                              matrix_width,
                                              matrix_height,
                                              tile_width,
                                              tile_height,
                                              pixel_x_size,
                                              pixel_y_size):
        """
        Inserts a new row or updates an existing row in the gpkg_tile_matrix Table. The gpkg_tile_matrix table documents
        the structure of the tile matrix at each zoom level in each tiles table. It allows GeoPackages to contain
        rectangular as well as square tiles (e.g. for better representation of polar regions). It allows tile pyramids
        with zoom levels that differ in resolution by factors of 2, irregular intervals, or regular intervals other than
        factors of 2.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param table_name: Tile Pyramid User Data Table Name
        :type table_name: str

        :param zoom_level:  0 <= zoom_level <= max_level for table_name
        :type zoom_level: int

        :param matrix_width: Number of columns (>= 1) in tile matrix at this zoom level
        :type matrix_width: int

        :param matrix_height: Number of rows (>= 1) in tile matrix at this zoom level,
        :type matrix_height: int

        :param tile_width: Tile width in pixels (>= 1)for this zoom level
        :type tile_width: int

        :param tile_height: Tile height in pixels (>= 1) for this zoom level
        :type tile_height: int

        :param pixel_x_size: In table_name srid units or default meters for srid 0 (>0)
        :type pixel_x_size: float

        :param pixel_y_size: In table_name srid units or default meters for srid 0 (>0)
        :type pixel_y_size: float
        """
        cls.insert_or_update_gpkg_tile_matrix_row(cursor=cursor,
                                                  tile_matrix_entry=TileMatrixEntry(table_name=table_name,
                                                                                    zoom_level=zoom_level,
                                                                                    matrix_width=matrix_width,
                                                                                    matrix_height=matrix_height,
                                                                                    tile_width=tile_width,
                                                                                    tile_height=tile_height,
                                                                                    pixel_x_size=pixel_x_size,
                                                                                    pixel_y_size=pixel_y_size))

    @staticmethod
    def insert_or_update_gpkg_tile_matrix_set_row(cursor,
                                                  tiles_content,
                                                  update_contents_table=True):

        """
        Inserts or updates the gpkg_tile_matrix_set Table with the following values. The gpkg_tile_matrix_set table
        defines the spatial reference system (srs_id) and the maximum bounding box (min_x, min_y, max_x, max_y) for all
        possible tiles in a tile pyramid user data table.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param tiles_content:  The TileSet entry in the gpkg_contents table describing the tiles in the GeoPackage
        :type tiles_content: TilesContentEntry

        :param update_contents_table: True if the gpkg_contents table should be updated as well with the same bounds,
        false otherwise
        :type update_contents_table: bool
        """
        if not table_exists(cursor, GEOPACKAGE_TILE_MATRIX_SET_TABLE_NAME):
            raise ValueError("Cannot add row to {table} because it does not exist"
                             .format(table=GEOPACKAGE_TILE_MATRIX_SET_TABLE_NAME))

        insert_or_update_row(cursor=cursor,
                             table_name=GEOPACKAGE_TILE_MATRIX_SET_TABLE_NAME,
                             sql_columns_list=[SqlColumnQuery(column_name='table_name',
                                                              column_value=tiles_content.table_name),
                                               SqlColumnQuery(column_name='srs_id',
                                                              column_value=tiles_content.srs_id,
                                                              include_in_where_clause=False),
                                               SqlColumnQuery(column_name='min_x',
                                                              column_value=tiles_content.min_x,
                                                              include_in_where_clause=False),
                                               SqlColumnQuery(column_name='min_y',
                                                              column_value=tiles_content.min_y,
                                                              include_in_where_clause=False),
                                               SqlColumnQuery(column_name='max_x',
                                                              column_value=tiles_content.max_x,
                                                              include_in_where_clause=False),
                                               SqlColumnQuery(column_name='max_y',
                                                              column_value=tiles_content.max_y,
                                                              include_in_where_clause=False)])

        if update_contents_table:
            # update the contents table as well
            GeoPackageCoreTableAdapter.insert_or_update_content(cursor=cursor,
                                                                content=tiles_content)

    @classmethod
    def insert_or_update_tile_data(cls,
                                   cursor,
                                   table_name,
                                   zoom_level,
                                   tile_column,
                                   tile_row,
                                   tile_data):
        """
        Inserts or updates row in the pyramid user data table with the table_name provided.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param table_name: Tile Pyramid User Data Table Name
        :type table_name: str

        :param zoom_level:  0 <= zoom_level <= max_level for table_name
        :type zoom_level: int

        :param tile_column:  0 to tile_matrix matrix_width - 1
        :type tile_column: int

        :param tile_row: 0 to tile_matrix matrix_height - 1
        :type tile_row: int

        :param tile_data: Of an image MIME type specified in clauses Tile Encoding PNG, Tile Encoding JPEG,
        [tile_enc_webp]
        :type tile_data: Binary
        """
        if not table_exists(cursor, table_name):
            raise ValueError("Cannot add row to {table} because it does not exist"
                             .format(table=table_name))

        insert_or_update_row(cursor=cursor,
                             table_name=table_name,
                             sql_columns_list=[SqlColumnQuery(column_name='zoom_level',
                                                              column_value=zoom_level),
                                               SqlColumnQuery(column_name='tile_column',
                                                              column_value=tile_column),
                                               SqlColumnQuery(column_name='tile_row',
                                                              column_value=tile_row),
                                               SqlColumnQuery(column_name='tile_data',
                                                              column_value=tile_data,
                                                              include_in_where_clause=False)])

    @classmethod
    def insert_or_update_tile_data_bulk(cls,
                                        cursor,
                                        table_name,
                                        tiles):
        """
        Inserts or updates rows in the pyramid user data table with the table_name provided.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param table_name: Tile Pyramid User Data Table Name
        :type table_name: str

        :param tiles: the tiles to update or insert into the tile pyramid user data table
        :type tiles: list of TileDataInformation
        """

        if not table_exists(cursor, table_name):
            raise ValueError("Cannot add row to {table} because it does not exist"
                             .format(table=table_name))

        image_blob_stmt = """
                              INSERT OR REPLACE INTO "{table_name}"
                                  (zoom_level, 
                                  tile_column, 
                                  tile_row, 
                                  tile_data)
                              VALUES (?,?,?,?);
                          """.format(table_name=table_name)
        cursor.executemany(image_blob_stmt, tuple([(tile.zoom_level,
                                                    tile.tile_column,
                                                    tile.tile_row,
                                                    tile.tile_data) for tile in tiles]))

    @classmethod
    def get_tile_data(cls,
                      cursor,
                      table_name,
                      zoom_level,
                      tile_column,
                      tile_row):
        """
        Returns the tile data at the specified zoom level, tile row, and tile column from the table given

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param table_name: Tile Pyramid User Data Table Name
        :type table_name: str

        :param zoom_level:  0 <= zoom_level <= max_level for table_name
        :type zoom_level: int

        :param tile_column:  0 to tile_matrix matrix_width - 1
        :type tile_column: int

        :param tile_row: 0 to tile_matrix matrix_height - 1
        :type tile_row: int

        :return: the tile data at the specified zoom level, tile row, and tile column from the table given
        :rtype: Binary
        """

        rows = select_query(cursor=cursor,
                            table_name=table_name,
                            select_columns=['tile_data'],
                            where_columns_dictionary={'zoom_level': zoom_level,
                                                      'tile_column': tile_column,
                                                      'tile_row': tile_row})

        return None if rows is None or len(rows) < 1 else rows[0]['tile_data']

    @classmethod
    def get_all_tile_data(cls, cursor, tile_table_name, tiles):
        """
        Returns a list of TileDataInformation of all the tiles requested by their tile coordinate values.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param tile_table_name: Tile Pyramid User Data Table Name
        :type tile_table_name: str

        :param tiles: the list of tile coordinates that are being requested for the tile data
        :type tiles: list of TileCoordinate

        :rtype: list of TileDataInformation
        :return: the list of tiles found in the table with the tile coordinate given
        """
        tile_dict = {}
        coords = []

        for tile in tiles:
            coords.append(tile.tile_column)
            coords.append(tile.tile_row)
            coords.append(tile.zoom_level)
            tile_dict[(tile.tile_column, tile.tile_row, tile.zoom_level)] = tile

        if not tile_dict:
            # all tiles loaded or coords are None
            return []

        stmt_base = "SELECT tile_column, tile_row, zoom_level, tile_data FROM '{0}' WHERE ".format(tile_table_name)

        loaded_tiles = 0
        tiles_to_return = []
        # SQLite is limited to 1000 args -> split into multiple requests if more arguments are needed
        while coords:
            cur_coords = coords[:999]

            stmt = stmt_base + ' OR '.join(
                ['(tile_column = ? AND tile_row = ? AND zoom_level = ?)'] * (len(cur_coords) // 3))
            cursor.execute(stmt, cur_coords)

            for row in cursor:
                loaded_tiles += 1
                key = (row['tile_column'], row['tile_row'], row['zoom_level'])
                # tile requested doesn't exist in the table if the entry is none
                if key in tile_dict:
                    tile = tile_dict[key]
                    data = row['tile_data']
                    tiles_to_return.append(TileDataInformation(tile_column=tile.tile_column,
                                                               tile_row=tile.tile_row,
                                                               tile_zoom=tile.zoom_level,
                                                               tile_data=data))
            coords = coords[999:]

        return tiles_to_return

    @classmethod
    def delete_tile_data(cls,
                         cursor,
                         table_name,
                         zoom_level,
                         tile_column,
                         tile_row,
                         check_matrix_deletion=True):
        """
        Deletes a single tile row with the following tile coordinate. If more than one row applies or if no rows apply
        an error will be thrown.

        :param check_matrix_deletion: True if the GeoPackage should check if there are no more tiles with the zoom_level
        deleted in the gpkg_tile_matrix table.  If there are no more tiles with that zoom_level, then the row is deleted
        from the gpkg_tile_matrix table as well
        :type check_matrix_deletion: bool

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param table_name: Tile Pyramid User Data Table Name
        :type table_name: str

        :param tile_row: the y coordinate of the tile. 0 to tile_matrix matrix_height - 1
        :type tile_row: int

        :param tile_column: the x coordinate of the tile.  0 to tile_matrix matrix_width - 1
        :type tile_column: int

        :param zoom_level: the zoom level of the tile (z coordinate)
        :type zoom_level: int
        """
        delete_row(cursor=cursor,
                   table_name=table_name,
                   sql_columns_list=[SqlColumnQuery(column_name='zoom_level',
                                                    column_value=zoom_level),
                                     SqlColumnQuery(column_name='tile_column',
                                                    column_value=tile_column),
                                     SqlColumnQuery(column_name='tile_row',
                                                    column_value=tile_row)])

        if check_matrix_deletion:
            # check to see if any tiles are now represented in that zoom_level
            # if not, delete the tile_matrix entry that represents that row
            zoom_rows = select_query(cursor=cursor,
                                     table_name=table_name,
                                     select_columns=['id',
                                                     'zoom_level',
                                                     'tile_column',
                                                     'tile_row',
                                                     'tile_data'],
                                     where_columns_dictionary={'zoom_level': zoom_level})
            if zoom_rows is None or len(zoom_rows) == 0:
                # delete tile matrix entry for this zoom level since there are no tiles at this zoom anymore
                cls.__delete_matrix_entry_for_zoom_level(cursor=cursor,
                                                         tile_table_name=table_name,
                                                         zoom_level=zoom_level)

    @classmethod
    def delete_zoom_level(cls,
                          cursor,
                          tile_table_name,
                          zoom_level):
        """
        Deletes all tiles with the zoom level given.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param tile_table_name: Tile Pyramid User Data Table Name
        :type tile_table_name: str

        :param zoom_level: the zoom level of the tile (z coordinate)
        :type zoom_level: int
        """
        delete_rows(cursor=cursor,
                    table_name=tile_table_name,
                    sql_columns_list=[SqlColumnQuery(column_name='zoom_level',
                                                     column_value=zoom_level)])

        cls.__delete_matrix_entry_for_zoom_level(cursor=cursor,
                                                 tile_table_name=tile_table_name,
                                                 zoom_level=zoom_level)



    @classmethod
    def __delete_matrix_entry_for_zoom_level(cls,
                                             cursor,
                                             tile_table_name,
                                             zoom_level):
        delete_rows(cursor=cursor,
                    table_name=GEOPACKAGE_TILE_MATRIX_TABLE_NAME,
                    sql_columns_list=[SqlColumnQuery(column_name='table_name',
                                                     column_value=tile_table_name),
                                      SqlColumnQuery(column_name='zoom_level',
                                                     column_value=zoom_level)])

    @staticmethod
    def get_tile_matrix_set_entry_by_table_name(cursor, tile_table_name):
        """
        Returns the Tile Matrix Set entry in the GeoPackage Tile Matrix Set table (gpkg_tile_matrix_set) where the
        table_name column matches the table_name passed in or None if none match

        :param tile_table_name: Tile Pyramid User Data Table Name
        :type tile_table_name: str

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :return  Returns the Tile Matrix Set entry in the GeoPackage Tile Matrix Set table (gpkg_tile_matrix_set) where the
        table_name column matches the table_name passed in or None if none match
        :rtype: Union[TileMatrixSetEntry, None]
        """
        if not table_exists(cursor=cursor,
                            table_name=GEOPACKAGE_TILE_MATRIX_SET_TABLE_NAME):
            return None
        # select all the rows
        cursor.execute("SELECT * FROM {table_name} WHERE table_name = ?;"
                       .format(table_name=GEOPACKAGE_TILE_MATRIX_SET_TABLE_NAME),
                       (tile_table_name,))

        rows = select_query(cursor=cursor,
                            table_name=GEOPACKAGE_TILE_MATRIX_SET_TABLE_NAME,
                            select_columns=['table_name',
                                            'min_x',
                                            'min_y',
                                            'max_x',
                                            'max_y',
                                            'srs_id'],
                            where_columns_dictionary={'table_name': tile_table_name})
        # no matches found
        if rows is None or len(rows) == 0:
            return None

        row = rows[0]

        return TileMatrixSetEntry(table_name=row['table_name'],
                                  min_x=row['min_x'],
                                  min_y=row['min_y'],
                                  max_x=row['max_x'],
                                  max_y=row['max_y'],
                                  srs_id=row['srs_id'])

    @classmethod
    def get_tile_matrix_for_zoom_level(cls,
                                       cursor,
                                       tile_table_name,
                                       zoom_level):
        """
        Selects all rows that match the tile table name given and zoom level.

        :param zoom_level: the zoom level of the tile (z coordinate)
        :type zoom_level: int

        :param tile_table_name: Tile Pyramid User Data Table Name
        :type tile_table_name: str

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :rtype: list of TileMatrixEntry
        """

        rows = select_query(cursor=cursor,
                            table_name=GEOPACKAGE_TILE_MATRIX_TABLE_NAME,
                            select_columns=['table_name',
                                            'zoom_level',
                                            'matrix_width',
                                            'matrix_height',
                                            'tile_width',
                                            'tile_height',
                                            'pixel_x_size',
                                            'pixel_y_size'],
                            where_columns_dictionary={'table_name': tile_table_name,
                                                      'zoom_level': zoom_level})

        return [TileMatrixEntry(table_name=row['table_name'],
                                zoom_level=row['zoom_level'],
                                matrix_width=row['matrix_width'],
                                matrix_height=row['matrix_height'],
                                tile_width=row['tile_width'],
                                tile_height=row['tile_height'],
                                pixel_x_size=row['pixel_x_size'],
                                pixel_y_size=row['pixel_y_size']) for row in rows]

    @classmethod
    def get_tile_matrix_entries_by_table_name(cls,
                                              cursor,
                                              tile_table_name):
        """
        Selects all rows that match the tile table name given.

        :param zoom_level: the zoom level of the tile (z coordinate)
        :type zoom_level: int

        :param tile_table_name: Tile Pyramid User Data Table Name
        :type tile_table_name: str

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :rtype: list of TileMatrixEntry
        """
        rows = select_query(cursor=cursor,
                            table_name=GEOPACKAGE_TILE_MATRIX_TABLE_NAME,
                            select_columns=['table_name',
                                            'zoom_level',
                                            'matrix_width',
                                            'matrix_height',
                                            'tile_width',
                                            'tile_height',
                                            'pixel_x_size',
                                            'pixel_y_size'],
                            where_columns_dictionary={'table_name': tile_table_name})

        return [TileMatrixEntry(table_name=row['table_name'],
                                zoom_level=row['zoom_level'],
                                matrix_width=row['matrix_width'],
                                matrix_height=row['matrix_height'],
                                tile_width=row['tile_width'],
                                tile_height=row['tile_height'],
                                pixel_x_size=row['pixel_x_size'],
                                pixel_y_size=row['pixel_y_size']) for row in rows]
    @classmethod
    def insert_or_update_gpkg_tile_matrix_row(cls,
                                              cursor,
                                              tile_matrix_entry):

        """
        Inserts or updates the gpkg_tile_matrix Table with the following values. The gpkg_tile_matrix_set table
        defines the spatial reference system (srs_id) and the maximum bounding box (min_x, min_y, max_x, max_y) for all
        possible tiles in a tile pyramid user data table.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param tile_matrix_entry:  The TileMatrix entry in the gpkg_tile_matrix table describing the matrix dimensions
        of a Tile Set in the GeoPackage
        :type tile_matrix_entry: TileMatrixEntry

        """
        if not table_exists(cursor=cursor,
                            table_name=GEOPACKAGE_TILE_MATRIX_TABLE_NAME):
            raise ValueError("Cannot add row to {table} because it does not exist"
                             .format(table=GEOPACKAGE_TILE_MATRIX_TABLE_NAME))

        insert_or_update_row(cursor=cursor,
                             table_name=GEOPACKAGE_TILE_MATRIX_TABLE_NAME,
                             sql_columns_list=[
                                 SqlColumnQuery(column_name='table_name',
                                                column_value=tile_matrix_entry.table_name),
                                 SqlColumnQuery(column_name='zoom_level',
                                                column_value=tile_matrix_entry.zoom_level),
                                 SqlColumnQuery(column_name='matrix_width',
                                                column_value=tile_matrix_entry.matrix_width,
                                                include_in_where_clause=False),
                                 SqlColumnQuery(column_name='matrix_height',
                                                column_value=tile_matrix_entry.matrix_height,
                                                include_in_where_clause=False),
                                 SqlColumnQuery(column_name='tile_width',
                                                column_value=tile_matrix_entry.tile_width,
                                                include_in_where_clause=False),
                                 SqlColumnQuery(column_name='tile_height',
                                                column_value=tile_matrix_entry.tile_height,
                                                include_in_where_clause=False),
                                 SqlColumnQuery(column_name='pixel_x_size',
                                                column_value=tile_matrix_entry.pixel_x_size,
                                                include_in_where_clause=False),
                                 SqlColumnQuery(column_name='pixel_y_size',
                                                column_value=tile_matrix_entry.pixel_y_size,
                                                include_in_where_clause=False)])
