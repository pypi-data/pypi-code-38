
from rgi.geopackage.core.geopackage_core_table_adapter import GeoPackageCoreTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_layers.geopackage_vector_layers_table_adapter import GeoPackageVectorLayersTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_styles.geopackage_stylesheets_table_adapter import GeoPackageStylesheetsTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_styles.styles_extension_constants import \
    GEOPACKAGE_STYLESHEETS_TABLE_NAME
from rgi.geopackage.extensions.vector_tiles.vector_styles.stylesheets_entry import StyleSheetsEntry
from rgi.geopackage.extensions.vector_tiles.vector_tiles_constants import VECTOR_TILES_DATA_TYPE
from rgi.geopackage.writers.geopackage_writer import GeoPackageWriter
from rgi.geopackage.utility.sql_utility import table_exists


class GeoPackageVectorTileStylesWriter(GeoPackageWriter):
    """
    Writes style data for vector-tiles to a GeoPackage. Each instance will write to a single GeoPackage vector-tiles
    table.
    """

    def __init__(self,
                 gpkg_file_path,
                 vector_tile_table_name,
                 styles_set,
                 timeout=500):
        """
        Constructor.

        :param styles_set: the name of the collection of styles to be added to the GeoPackage file
        :type styles_set: str

        :param gpkg_file_path: the path to the existing geopackage file
        :type gpkg_file_path: str

        :param vector_tile_table_name: the name of the vector-tiles table to add style data to
        :type vector_tile_table_name: str

        :param timeout: the timeout for the database connection in miliseconds
         :type timeout: float
        """
        super(GeoPackageVectorTileStylesWriter, self).__init__(gpkg_file_path=gpkg_file_path,
                                                               timeout=timeout)
        self.styles_set = styles_set
        cursor = self._database_connection().cursor()
        # get the content entry from gpkg_contents table
        self._vector_tile_content_entry = GeoPackageCoreTableAdapter.get_content_entry_by_table_name(
            cursor=cursor,
            table_name=vector_tile_table_name)

        # check to make sure an entry exists
        if self._vector_tile_content_entry is None:
            raise ValueError("No table named: '{table_name}' "
                             "in the GeoPackage: {file_path}".format(table_name=vector_tile_table_name,
                                                                     file_path=gpkg_file_path))
        # check to make sure the entry is of type vector-tiles
        elif self._vector_tile_content_entry.data_type.lower() != VECTOR_TILES_DATA_TYPE:
            raise ValueError("Table: '{table_name}' is not a vector-tiles data type: '{data_type}' "
                             "in the GeoPackage: {file_path}".format(table_name=vector_tile_table_name,
                                                                     file_path=gpkg_file_path,
                                                                     data_type=self._vector_tile_content_entry.data_type))

        # create the styling tables
        if not GeoPackageVectorLayersTableAdapter.table_exists(cursor=cursor):
            GeoPackageVectorLayersTableAdapter.create_vector_layers_table(cursor=cursor)

        if not table_exists(cursor=cursor,
                            table_name=GEOPACKAGE_STYLESHEETS_TABLE_NAME):
            GeoPackageStylesheetsTableAdapter.create_stylesheets_table(cursor=cursor)
        # commit the new tables to the database
        self._database_connection().commit()

    def get_all_vector_layer_entries(self):
        """
        Returns any Vector Layer Entries that apply to this specified vector-tiles table.

        :return: Returns any Vector Layer Entries whose table_name column value matches the vector_tiles_table_name
        parameter.

        :rtype: list of VectorLayerEntry
        """
        cursor = self._database_connection().cursor()
        table_name = self._vector_tile_content_entry.table_name

        return GeoPackageVectorLayersTableAdapter.get_vector_layer_entries_by_table_name(cursor=cursor,
                                                                                         vector_tiles_table_name=table_name)

    def get_all_styles_for_tile_set(self):
        """
        Returns all the StyleSheetsEntry entries in the GeoPackage associated with this vector tile set.

        :rtype list of StyleSheetsEntry
        """

        cursor = self._database_connection().cursor()
        table_name = self._vector_tile_content_entry.table_name

        return GeoPackageStylesheetsTableAdapter.get_all_stylesheet_entries_for_tile_set(cursor=cursor,
                                                                                         vector_tiles_table_name=table_name)

    def get_all_styles_for_layer(self,
                                 layer_name):
        """
        Returns all the StyleSheetsEntry entries in the GeoPackage associated with this vector tile set with a layer
        name given.
        :rtype list of StyleSheetsEntry
        """
        cursor = self._database_connection().cursor()
        table_name = self._vector_tile_content_entry.table_name
        return GeoPackageStylesheetsTableAdapter.get_all_stylesheet_entries_by_layer_name_and_table_name(cursor=cursor,
                                                                                                         vector_tiles_table_name=table_name,
                                                                                                         layer_name=layer_name)

    def add_new_style_for_tile_set(self,
                                   style_format,
                                   style_data,
                                   style='default',
                                   description='my style description',
                                   title='my-style'):
        """
        Add the new style to the GeoPackage. This style applies to all layers in the vector-tiles table.

        :param style: alternative styles for the same set of layers (day, night)
        :type style: str

        :param style_format: the style encoding (i.e. SLD, MapBox, etc)
        :type style_format: str

        :param style_data: the stylesheet data (the JSON or xml as a binary)
        :type style_data: Binary
        """
        # check to see if a styleset exists already for this vector-tile set
        # get all vector layer entries and check for a styles_set id
        cursor = self._database_connection().cursor()
        table_name = self._vector_tile_content_entry.table_name
        vector_layer_entries = GeoPackageVectorLayersTableAdapter \
            .get_vector_layer_entries_by_table_name(cursor=cursor,
                                                    vector_tiles_table_name=table_name)

        # we set the styles_set to None and have the private method add_style update it with the correct value
        style_entry = StyleSheetsEntry(styles_set=self.styles_set,
                                       style=style,
                                       style_format=style_format,
                                       stylesheet=style_data,
                                       title=title,
                                       description=description)

        # if a style_set already exists, add to existing
        self.__add_style(cursor=cursor,
                         style_set_entry=style_entry,
                         vector_layer_entries=vector_layer_entries)

    def add_new_style_for_layer(self,
                                style_format,
                                style_data,
                                layer_name,
                                style='default',
                                min_zoom=None,
                                max_zoom=None,
                                attributes_table_name='',
                                description='',
                                title=''):
        """
        Add the new style to the GeoPackage.

        :param style_format: the style encoding (i.e. SLD, MapBox, etc)
        :type style_format: StyleFormat

        :param style_data: the stylesheet data (the JSON or xml as a binary)
        :type style_data: Binary

        :param layer_name: name of the layer that the style applies to. None if it applies to all
        :type layer_name: str

        :param style: alternative styles for the same set of layers (day, night)
        :type style: str

        :param min_zoom: optional integer minimum zoom level for the layer to be rendered at
        :type min_zoom: int, None

        :param max_zoom: optional maximum zoom level for the layer to be rendered at
        :type max_zoom: int, None

        :param attributes_table_name: optional name of the attributes table name associated with the layer
        :type attributes_table_name: str, None

        :param description:  optional text description of layer
        :type description: str, None
        """
        cursor = self._database_connection().cursor()
        # get all vector layer entries and check for a styles_set id
        vector_layer_entries = GeoPackageVectorLayersTableAdapter \
            .get_vector_layer_entries_by_table_name(cursor=cursor,
                                                    vector_tiles_table_name=self._vector_tile_content_entry.table_name)

        # get the specific entry with the layer name indicated above
        vector_layer_entry_targeting = next((vector_layer_entry
                                             for vector_layer_entry
                                             in vector_layer_entries
                                             if vector_layer_entry.name == layer_name),
                                            None)

        if vector_layer_entry_targeting is None:
            raise ValueError("No layer exist that is named {layer_name}. "
                             "Layer names found for this vector-tiles table are {layers}"
                             .format(layer_name=layer_name,
                                     layers=', '.join(vector_layer_entry.name
                                                      for vector_layer_entry
                                                      in vector_layer_entries)))

        # make sure the layer name we are targeting is updated with all the values specified
        vector_layer_entry_targeting.max_zoom = max_zoom
        vector_layer_entry_targeting.min_zoom = min_zoom
        vector_layer_entry_targeting.description = description
        vector_layer_entry_targeting.attributes_table_name = attributes_table_name

        # we set the styles_set to None and have the private method add_style update it with the correct value
        style_entry = StyleSheetsEntry(styles_set=self.styles_set,
                                       style=style,
                                       style_format=style_format,
                                       stylesheet=style_data,
                                       title=title,
                                       description=description)

        self.__add_style(cursor=cursor,
                         style_set_entry=style_entry,
                         vector_layer_entries=[vector_layer_entry_targeting])

    def __add_style(self,
                    cursor,
                    style_set_entry,
                    vector_layer_entries):
        """
        Helper function to add style data to the GeoPackage.

        :param style_set_entry: the StyleSheetEntry that needs to be added to the GeoPackage
        :type style_set_entry: StyleSheetsEntry

        :param vector_layer_entries: the list of vector layer entries for the vector-tile table with any alterations
        made previously to update into the table, and the stylable_layer_set needs to match the style_set_entry
        styles_set property
        :type vector_layer_entries: list of VectorLayersEntry
        """
        # need to set the all style_sets to be the same
        for vector_layer_entry in vector_layer_entries:
            vector_layer_entry.stylable_layer_set = style_set_entry.styles_set
            GeoPackageVectorLayersTableAdapter.insert_or_update_vector_tile_layer_entry(cursor=cursor,
                                                                                        vector_tile_layer_entry=
                                                                                    vector_layer_entry)

        GeoPackageStylesheetsTableAdapter.insert_or_update_stylesheet_entry(cursor=cursor,
                                                                            stylesheet_entry=style_set_entry)

        self._database_connection().commit()
