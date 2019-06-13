from __future__ import print_function
from __future__ import absolute_import
import os
import tempfile
import re
import sys
import time
import json
import ast
import datetime
import logging

from requests import HTTPError
from deriva.core import ErmrestCatalog, get_credential, init_logging, urlparse
from deriva.core.ermrest_config import tag as chaise_tags
import deriva.core.ermrest_model as em
from deriva.utils.catalog.manage.dump_catalog import DerivaCatalogToString
from deriva.utils.catalog.manage.utils import LoopbackCatalog, LoopbackModel
from deriva.utils.catalog.components.deriva_model import DerivaModel, DerivaCatalog
from deriva.core.base_cli import BaseCLI
from deriva.utils.catalog.version import __version__ as VERSION

IS_PY2 = (sys.version_info[0] == 2)
IS_PY3 = (sys.version_info[0] == 3)

logger = logging.getLogger(__name__)

try:
    from tableschema import Table, Schema, exceptions
    import goodtables
    import tabulator
    import dateutil
except Exception as e:
    logger.critical("Unable to import a required package dependency. %s. "
                    "Are you sure that this software package was installed with the [csv] qualifier?" % e)
    raise

# We should get range info in there....
table_schema_type_map = {
    'timestamp': ('timestamp', 'default'),
    'jsonb': ('object', 'default'),
    'float4': ('number', 'default'),
    'int4': ('integer', 'default'),
    'int8': ('integer', 'default'),
    'float8': ('number', 'default'),
    'text': ('string', 'default'),
    'markdown': ('string', 'default'),
    'date': ('datetime', 'any'),
    'json': ('object', 'default'),
    'boolean': ('boolean', 'default'),
    'int2': ('integer', 'default'),
    'timestamptz': ('datetime', 'default'),
    'timestamp[]': ('any', 'default'),
    'jsonb[]': ('array', 'default'),
    'int4[]': ('integer', 'default'),
    'int8[]': ('integer', "default"),
    'float8[]': ('number', 'default'),
    'text[]': ('any', 'default'),
    'date[]': ('any', 'default'),
    'json[]': ('array', 'default'),
    'boolean[]': ('boolean', 'default'),
    'int2[]': ('integer', 'default'),
    'timestamptz[]': ('any', 'default'),
    'ermrest_uri': ('string', 'uri'),
    'ermrest_rid': ('string', 'default'),
    'ermrest_rct': ('datetime', 'default'),
    'ermrest_rmt': ('datetime', 'default'),
    'ermrest_rcb': ('string', 'default'),
    'ermrest_rmb': ('string', 'default'),
}

table_schema_ermrest_type_map = {
    'string:default': 'text',
    'string:email': 'text',
    'string:uri': 'ermrest_uri',
    'string:binary': 'text',
    'string:uuid': 'text',
    'number:default': 'float8',
    'integer:default': 'int4',
    'boolean:default': 'boolean',
    'object:default': 'json',
    'array:default': 'json[]',
    'date:default': 'date',
    'date:any': 'date',
    'time:default': 'timestampz',
    'time:any': 'timestampz',
    'datetime:default': 'date',
    'datetime:any': 'date',
    'year:default': 'date',
    'yearmonth:default': 'date'
}


class DerivaUploadError(HTTPError):
    def __init__(self, chunk_size, chunk_number, http_err):
        self.chunk_number = chunk_number
        self.chunk_size = chunk_size
        self.reason = http_err


class DerivaCSVError(Exception):
    def __init__(self, msg):
        self.msg = msg


class DerivaCSVModel:
    """
    Class to represent a CSV schema as a dervia catalog model. This class takes a table schema, performs name
    mapping of column names and generates a deriva-py model.
    """

    def __init__(self, csvschema):
        self._csvschema = csvschema
        self.model = {}
        self.type_map = {}
        self.field_name_map = {}

        # Add extra columns and constraints necessary to use for Upload_Id/Row_Number primary key.
        if self._csvschema.row_number_as_key:
            column_defs = [em.Column.define('Upload_Id', em.builtin_types['int4'],
                                            comment='Identifier to keep track of different uploads'),
                           em.Column.define('Row_Number', em.builtin_types['int4'], nullok=False,
                                            comment='Row number in upload file')]
            constraint_name = (csvschema.schema_name,
                               csvschema.map_name('{}_Upload_Id_Row_Number_Key)'.format(csvschema.table_name)))
            key_defs = [em.Key.define(['Upload_Id', 'Row_Number'], constraint_names=[constraint_name])]
        else:
            column_defs, key_defs = [], []

        # Get model elements for columns and keys.
        column_defs.extend(self.__deriva_columns(csvschema))
        key_defs.extend(self.__deriva_keys(csvschema))
        logger.debug('schema %s table %s', csvschema.schema_name, csvschema.table_name)
        table_def = em.Table.define(csvschema.table_name, column_defs=column_defs, key_defs=key_defs)
        schema_def = em.Schema.define(csvschema.schema_name, comment="Schema from tableschema")
        schema_def['tables'] = {csvschema.table_name: table_def}

        self.model = LoopbackModel(
            {'schemas': {csvschema.schema_name: schema_def}, 'acls': {}, 'annotations': {}, 'comment': None})
        self.catalog = LoopbackCatalog(self.model)
        logger.debug('%s %s', self.catalog, [i for i in self.catalog.getCatalogModel().schemas])
        return

    def __deriva_columns(self, csvschema):
        """
        Add deriva_py column definitions, one for each field in the schema.
        :return:
        """
        column_defs = []

        system_columns = ['RID', 'RCB', 'RMB', 'RCT', 'RMT']

        for col in csvschema.schema.fields:
            # Don't include system columns in the list of column definitions.
            if col.name in system_columns:
                continue
            mapped_name = csvschema.map_name(col.name)
            self.field_name_map[col.name] = mapped_name
            self.type_map.setdefault(table_schema_ermrest_type_map[col.type + ':' + col.format], []).append(col.name)

            t = "{}:{}".format(col.type, col.format)
            column_defs.append(em.Column.define(mapped_name, em.builtin_types[table_schema_ermrest_type_map[t]],
                                                nullok=not col.required, comment=col.descriptor.get('description', '')))
        return column_defs

    @staticmethod
    def __deriva_keys(csvschema):
        keys = []
        for cols in csvschema._key_columns:
            mapped_cols = [csvschema.map_name(i) for i in cols]
            mapped_name = csvschema.map_name('{}_{}'.format(csvschema.table_name, '_'.join(cols)))
            constraint_name = (csvschema.schema_name, '{}_key'.format(mapped_name))
            keys.append(em.Key.define(mapped_cols, constraint_names=[constraint_name]))

        return keys


class DerivaCSV(Table):

    def __init__(self, source, schema_name, table_name=None, column_map=True,
                 key_columns=None, row_number_as_key=False,
                 schema=None):
        """

        :param source: File containing the table data
        :param schema_name: Name of the Deriva Schema in which this table will be located
        :param table_name: Name of the table.  If not provided, use the source file name
        :param column_map: a column name mapping dictionary, of the form [n1,n2,n3] or {n1:v, n2:v}.  In the list form
                           elements are the exact capatilization of words to be used in a name.  In the dictionary
                           form, the values are what the name should be replaced with.  All matching is done case
                           insensitive.  Word substitution is only done after column names are split. Other matches are
                           done both before and after the mapping of the name into snake case.

        :param key_columns: name of columns to use as keys (non-null, unique). Can be a single column or a list of
                            list of columns.  The first element of the list is used as the primary key.
        :param row_number_as_key: if key column is not provided, use the row number of the CSV in combination with a
                            upload ID generated by system to identify the row.
        :param schema: existing tableschema file to use instead of infering types
        """
        if schema is True:
            schema = None
        super(DerivaCSV, self).__init__(source, schema=schema)

        self.source = source
        self.table_name = table_name
        self._column_map = column_map
        self._key_columns = key_columns
        self.schema_name = schema_name
        self.row_count = None
        self.validation_report = None
        self.row_number_as_key = row_number_as_key if self._key_columns is None else False

        # Normalize the column map so we only have a dictionary.
        if self._column_map:
            if isinstance(self._column_map, list):
                # We have a word map.
                self._column_map = {i.upper(): i for i in self._column_map}
            elif isinstance(self._column_map, dict):
                self._column_map = {k.upper(): v for k, v in self._column_map.items()}
            else:
                self._column_map = {}

        # If tablename is not specified, use the file name of the data file as the table name.
        if not self.table_name:
            self.table_name = os.path.splitext(os.path.basename(source))[0]

        # Make the table name consistent with the naming strategy
        self.table_name = self.map_name(self.table_name)

        # Do initial infer to set up headers and schema.
        Table.infer(self)

        # Headers have to be unique
        if len(self.headers) != len(set(self.headers)):
            raise DerivaCSVError(msg='Duplicated column name in table')

        # Keys column can be a  single column or a list of a list of columns.  Normlize to list of lists...
        if self._key_columns is None or self._key_columns == []:
            self._key_columns = []
        elif not isinstance(self._key_columns, list):
            self._key_columns = [[self._key_columns]]
        else:
            self._key_columns = [i if type(i) is list else [i] for i in self._key_columns]
        self.__set_key_constraints()

        return

    def __set_key_constraints(self):
        """
        Go through the schema and set up the primary key column based on provided key_columns.  Then go through the
        fields and set the constraints to be consistant with a key.
        :return:
        """
        # Set the primary key value.  Use primary_key if there is one in the schema.  Otherwise, use the first
        # key in the key_columns list.
        if self.schema.primary_key:
            primary_key = self.schema.primary_key
            if primary_key not in self._key_columns:
                self._key_columns.append(self.schema.primary_key)
        elif self._key_columns:
            primary_key = self._key_columns[0]
        else:
            primary_key = []

        # Make sure primary key actually names columns...
        if len(primary_key) > 0:
            if all(map(lambda x: x in self.schema.field_names, primary_key)):
                self.schema.descriptor['primaryKey'] = primary_key
            else:
                raise DerivaCSVError(msg='Missing key column: {}'.format(primary_key))

        # Capture the key columns.
        for k in self._key_columns:
            # All columns good?
            if all(map(lambda x: x in self.schema.field_names, k)):
                for col in k:
                    idx = self.schema.field_names.index(col)
                    if len(k) == 1:
                        self.schema.descriptor['fields'][idx].update(
                            {'constraints': {'required': True, 'unique': True}})
                    else:
                        self.schema.descriptor['fields'][idx].update({'constraints': {'required': True}})
            else:
                raise DerivaCSVError('Missing key column {}'.format(k))
        self.schema.commit(strict=True)
        return

    @staticmethod
    def __get_type(val, prev_type):
        # Skip over empty cells or if you have already gotten to string type.
        if val == '' or prev_type is str:
            next_type = prev_type
        else:
            # Deal with booleans so you don't confuse with strings.
            if val.upper() == 'TRUE':
                val = True
            elif val.upper() == 'FALSE':
                val = False

            # Now see if you can turn into python numeric type...
            try:
                v = ast.literal_eval(val)
            except SyntaxError:
                v = val
            except ValueError:
                v = val
            val_type = type(v)

            if val_type is str:
                try:
                    dateutil.parser.parse(v, ignoretz=True)
                    val_type = datetime.datetime
                except ValueError:
                    pass

            if val_type is str:
                url_result = urlparse(v)
                if url_result.scheme != '' and url_result.netloc != '':
                    val_type = type(url_result)

            next_type = val_type

            # Do promotion/demotion.
            if prev_type is not None:
                # Float overrides integer.
                if (val_type == float and prev_type == int) or (val_type == int and prev_type == float):
                    next_type = float
                elif val_type != prev_type:  # Types are different, so pick text
                    next_type = str

        return next_type

    def infer(self, limit=None, confidence=.75):
        """
        Infer the current type by looking at the values in the table
         """
        # Do initial infer tqo set up headers and schema.
        Table.infer(self)

        rows = self.read(cast=False)
        headers = self.headers
        # Get descriptor
        fields = []
        type_matches = {}
        for header in headers:
            fields.append({'name': header})

        rindex = 0
        for rindex, row in enumerate(rows):
            if limit is not None and rindex == limit:
                break
            # build a column-wise lookup of type matches
            for cindex, value in enumerate(row):
                typeid = self.__get_type(value, type_matches.get(cindex, None))
                type_matches[cindex] = typeid
        self.row_count = rindex
        url_type = type(urlparse('foo'))

        for index, results in type_matches.items():
            type_name, type_format = None, 'default'
            if results is bool:
                type_name = 'boolean'
            elif results is int:
                type_name = 'integer'
            elif results is float:
                type_name = 'number'
            elif results is str:
                type_name = 'string'
            elif results is datetime.datetime:
                type_name = 'datetime'
                type_format = 'any'
            elif results is url_type:
                type_name = 'string'
                type_format = 'uri'
            else:
                raise DerivaCSVError(msg='Bad type in infer')

            fields[index].update({'type': type_name, 'format': type_format})
        # Now update the schema to have the inferred values.
        self.schema.descriptor['fields'] = fields

        # Reset the key constraints as they were blasted away by the infer.
        self.__set_key_constraints()
        self.schema.commit()
        return

    def validate(self, catalog, validation_limit=500000):
        """
        For the specified table data, validate the contents of the table against an existing table in a catalog.
        :parameter catalog
        :param validation_limit: How much of the table to check. Defaults to entire table.
        :return: an error report and the number of rows in the table as a tuple
        """

        table_schema = self.table_schema_from_catalog(catalog, self.schema_name, self.table_name)

        if self.row_number_as_key:
            # Need to correct for two upload_id and row number....
            del table_schema.descriptor['primaryKey']
            table_schema.descriptor['fields'] = table_schema.descriptor['fields'][2:]
            table_schema.commit()

        # First, just check the headers to make sure they line up under mapping.
        report = goodtables.validate(self.source, schema=table_schema.descriptor, checks=['non-matching-header'])
        if not report['valid'] and self._column_map:
            mapped_headers = map(lambda x: self.map_name(x), report['tables'][0]['headers'])
            bad_headers = list(filter(lambda x: x[0] != x[1], zip(table_schema.field_names, mapped_headers)))
            if bad_headers:
                report['headers'] = [x[1] for x in bad_headers]
                return report['valid'], report, validation_limit
        report = goodtables.validate(self.source, row_limit=validation_limit, schema=table_schema.descriptor,
                                     skip_checks=['non-matching-header'])
        self.validation_report = report

        return report['valid'], report

    def table_schema_from_catalog(self, catalog, skip_system_columns=True, outfile=None):
        """
        Create a TableSchema by querying an ERMRest catalog and converting the model format.

        :param catalog
        :param outfile: if this argument is specified, dump the scheme into the specified file.
        :param skip_system_columns: Don't include system columns in the schema.
        :return: table schema representation of the model
        """

        with DerivaModel(catalog) as m:
            schema = m.schema_model(catalog[self.schema_name])
            table = schema.tables[self.map_name(self.table_name)]
            fields = []
            primary_key = None

            for col in table.column_definitions:
                if col.name in ['RID', 'RCB', 'RMB', 'RCT', 'RMT', 'Batch_Id'] and skip_system_columns:
                    continue
                field = {
                    "name": col.name,
                    "type": table_schema_type_map[col.type.typename][0],
                    "constraints": {}
                }

                if field['type'] == 'boolean':
                    field['trueValues'] = ["true", "True", "TRUE", "1", "T", "t"]
                    field['falseValues'] = ["false", "False", "FALSE", "0", "F", "f"]

                if table_schema_type_map[col.type.typename][1] != 'default':
                    field['format'] = table_schema_type_map[col.type.typename][1]
                if col.display:
                    field['title'] = col.display['name']
                if col.comment:
                    field['description'] = col.comment

                # Now see if column is unique.  For this to be true, it must be in the list of keys for the table, and
                #  the unique column list must be a singleton.

                if [col.name] in [i.unique_columns for i in table.keys]:
                    field['constraints']['unique'] = True

                if not col.nullok:
                    field['constraints']['required'] = True
                fields.append(field)

            # Now look for a key column that is not the RID
            for i in table.keys:
                if i.unique_columns == ['RID']:
                    continue
                primary_key = i.unique_columns
                break

            try:
                descriptor = {'fields': fields, 'missingValues': ['', 'N/A', 'NULL']}
                if primary_key is not None:
                    descriptor['primaryKey'] = primary_key
                catalog_schema = Schema(descriptor=descriptor, strict=True)
                if outfile is not None:
                    catalog_schema.save(outfile)
            except exceptions.ValidationError as exception:
                print('error.....')
                print(exception.errors)
                raise exception
            return catalog_schema

    def upload_to_deriva(self, catalog, upload_id=None, chunk_size=10000):
        """
        Upload the source table to deriva.

        :param catalog
        :param upload_id
        :param chunk_size: Number of rows to upload at one time.
        :return:
        """

        target_table = catalog[self.schema_name][self.table_name].datapath()
        catalog_schema = self.table_schema_from_catalog(catalog)

        # Sanity check columns.
        for i in map(lambda x: self.map_name(x), self.headers):
            if i not in catalog_schema.headers:
                raise DerivaCSVError(msg="Incompatible column: " + i)

        field_types = [i.type for i in catalog_schema.fields]

        # Find the next available upload id.
        if upload_id is None and self.row_number_as_key:
            upload_id = 0
            e = list(target_table.entities().fetch(limit=1, sort=[target_table.column_definitions['Upload_Id'].desc]))
            if len(e) == 1:
                upload_id = e[0]['Upload_Id'] + 1
            logger.info('New upload id: %s', upload_id)
            sys.stdout.flush()

        def to_json(extended_rows):
            """
            Convert string values to python types.
            :param extended_rows:
            :return:
            """

            for row_number, headers, row in extended_rows:
                # Add system columns to deal with row number as primary key.
                if self.row_number_as_key:
                    # Need to correct row number to take header into account...
                    row = [upload_id, row_number - 1] + row
                for idx, (v, t) in enumerate(zip(row, field_types)):
                    if t in ['boolean', 'integer', 'number', 'date'] and v == '':
                        row[idx] = None
                    else:
                        if t == 'boolean':
                            row[idx] = True if row[idx] == 'true' else False
                        if t == 'integer':
                            row[idx] = int(v)
                        if t == 'number':
                            row[idx] = float(v)
                        if 'date' in t and v == '':
                            row[idx] = None
                yield (row_number, headers, row)

        with tabulator.Stream(self.source, headers=catalog_schema.headers, post_parse=[to_json],
                              skip_rows=[1]) as stream:
            rows = stream.read(keyed=True)
        row_index = 0

        # Read in the source table and sort based on the primary key value.
        if catalog_schema.primary_key:
            #  Sort the rows based on the primary key.
            rows.sort(key=lambda x: [x[i] for i in catalog_schema.primary_key])

            # determine current position in (partial?) copy
            # Key can be compound, so we meed to create the column sorting descriptor.
            filtered=target_table
            if self.row_number_as_key:
                logger.debug('setting ID filter %s', upload_id)
                filtered = target_table.filter(target_table.Upload_Id == upload_id)

            sort = [target_table.column_definitions[i].desc for i in catalog_schema.primary_key]
            logger.debug('Sort %s', sort)
            e = list(filtered.entities().fetch(limit=1, sort=sort))
            logging.debug('number of entities to upload %s %s', len(e), e)
            logging.debug('number of entities to upload %s %s', len(e), e)
            logging.debug('target_uri %s', target_table.uri)
            if len(e) == 1:
                # Part of this table has already been uploaded, so we want to find out how far we got and start from
                # there
                max_value = [e[0][i] for i in catalog_schema.primary_key]
                # Now convert this to an location in the table
                row_index = next(i for i, v in enumerate(rows)
                                 if [v[i] for i in catalog_schema.primary_key] == max_value) + 1
                if row_index == len(rows):
                    logger.info('Previous upload completed')
                else:
                    logger.info('Resuming upload at row count %s', row_index)
        else:
            # We don't have a key, or the key is composite, so in this case we just have to hope for the best....
            chunk_size = len(rows)
        chunk_cnt = 1
        row_count = 0
        while True:
            # Get chunk from rows from rows[last:last+page_size] ....
            chunk = rows[row_index:row_index + chunk_size]
            if not chunk == []:
                start_time = time.time()
                target_table.insert(chunk, add_system_defaults=True)
                stop_time = time.time()
                logger.info('Completed chunk {} size {} in {:.1f} sec.'.format(chunk_cnt, chunk_size, stop_time - start_time))
                sys.stdout.flush()
                chunk_cnt += 1
                row_index += len(chunk)
                row_count += len(chunk)
            else:
                break

        return row_count, upload_id

    def convert_to_deriva(self, outfile=None, schemafile=None):
        """
        Read in a table, try to figure out the type of its columns and output a deriva-py program that can be used
        to create the table in a catalog.

        :param outfile: Where to put the deriva_py program. If None, put in same directory as the input file with
                        the same name as the table.
        :param schemafile: If true, dump tableschema output.
        :return: dictionary that has the column name mapping derived by this routine.
        """

        if outfile is None:
            outfile = self.table_name + '.py'

        outname = os.path.splitext(os.path.abspath(outfile))[0]

        # If not provided the name of a schema file, then infer the schema and save to a file if True.
        if schemafile is True or schemafile is None or schemafile is False:
            self.infer()
        if schemafile is True:
            self.schema.save(outname + '.json')

        deriva_model = DerivaCSVModel(self)

        stringer = DerivaCatalogToString(
            DerivaCatalog("host", ermrest_catalog=deriva_model.catalog), groups={})
        table_string = stringer.table_to_str(self.schema_name, self.table_name)

        if schemafile is True:
            with open(outname + '_schema_map.json', 'w') as mapfile:
                json.dump({'field_name_map': deriva_model.field_name_map,
                           'type_map': deriva_model.type_map}, mapfile, indent=4)

        with open(outfile, 'w') as stream:
            print(table_string, file=stream)
        return deriva_model.field_name_map, deriva_model.type_map

    def create_validate_upload_csv(self, catalog, convert=True, validate=False, create=False, upload=False,
                                   upload_id=None, derivafile=None, schemafile=None, chunk_size=10000):
        """

        :param catalog: Ermrest catalog to be used for operations.
        :param convert: If true, use table inference to infer types for columns of table and create a deriva-py program
        :param derivafile: Specify the file name of where the deriva-py program to create the table exists
        :param schemafile: File that contains tableschema. May be input or output depending on other arguments
        :param create: If true, create a table in the catalog.
               If derivafile argument is not specified, then infer table definition
        :param validate: Run table validation on input before trying to upload
        :param upload: If true, upload file to deriva catalog.
        :param upload_id: ID of upload to continue.
        :param chunk_size: Number of rows to upload at one time.
        :return:
        """
        tdir = tempfile.mkdtemp()

        # If you are going to create a table, you either must have a definition file, or you need to generate one.
        if create and not convert:
            if derivafile is None:
                derivafile = '{}/{}.py'.format(tdir, self.table_name)
                convert = True

        if convert:  # Generate deriva-py file to create table if convert option is specified.
            logger.info('Converting table spec to deriva-py....')
            sys.stdout.flush()
            self.convert_to_deriva(outfile=derivafile, schemafile=schemafile)

        if create:
            logger.info('Creating table definition {}:{}'.format(self.schema_name, self.table_name))
            sys.stdout.flush()
            # If derivafile is specified, use that for file name.
            if derivafile is None:
                derivafile = '{}/{}.py'.format(tdir, self.table_name)
            tablescript = load_module_from_path(derivafile)
            # Now create the table.
            tablescript.main(catalog, 'table')

        if validate:
            try:
                valid, report = self.validate(catalog)
                if not valid:
                    for i in report['tables'][0]['errors']:
                        print(i)
            except exceptions.CastError as e:
                print('Error: ', e.errors)
                return report

        if upload:
            logger.info('Loading table data {}:{}'.format(self.schema_name, self.table_name))
            sys.stdout.flush()
            row_cnt = self.upload_to_deriva(catalog, chunk_size=chunk_size, upload_id=upload_id)

            return row_cnt

    def map_name(self, name, column_map=None):
        """
        A simple function that attempts to map a column name into a name that follows the deriva naming convetions.
        :param name: Column name to be mapped
        :param column_map: map of column names that should be used directly without additional modification
        :return: Resulting column name.
        """

        if column_map is None:
            column_map = self._column_map

        if self._column_map is None or self._column_map is False:
            return name

        name = column_map.get(name.upper(), name)

        # Split words based on capitol first letter, or existing underscore.  Capitolize the first letter of each
        # word unless it is in the provided word list.
        split_words = r"[A-Z]+[a-z0-9]*|[a-z0-9]+|\(.*?\)|[+\/\-*@<>%&=]"
        word_list = re.findall(split_words, name)
        word_list = map(lambda x: column_map.get(x.upper(), x[0].upper() + x[1:]), word_list)
        mname = '_'.join(list(word_list))

        mname = column_map.get(mname.upper(), mname)
        return mname


class DerivaCSVCLI (BaseCLI):

    def __init__(self, description, epilog):
        super(DerivaCSVCLI, self).__init__(description, epilog, VERSION)

        def python_value(s):
            return ast.literal_eval(s)

        parser = self.parser
        parser.add_argument('tabledata', help='Location of tablelike data to be added to catalog')
        parser.add_argument('schema', help='Name of the schema to be used for table')
        parser.add_argument('--catalog', default=1, help='ID number of desired catalog (Default:1)')
        parser.add_argument('--table', default=None, help='Name of table to be managed (Default:tabledata filename)')
        parser.add_argument('--key-columns', type=python_value, default=None,
                            help='List of columns to be used as key when creating table schema. Can be either:'
                                 '1) just the name of the column to be used as a key or a list of the columns to be '
                                 'used as keys. Compound keys can be expressed by using list of columns.')
        parser.add_argument('--rownumber-as-key', action='store_true',
                            help='Use the row number in the CSV as a unique key'
                                 'in conjunction with the upload_id')
        parser.add_argument('--upload-id', default=None, help='Restart the upload')
        parser.add_argument('--convert', action='store_true',
                            help='Generate a deriva-py program to create the table [Default:True]')
        parser.add_argument('--column-map', default=True, type=python_value,
                            help='Convert column names to cannonical form [Default:True]. A value can be provided to '
                                 'customize the column mapping.  If the value is of the form [n1,n2,n3] '
                                 'a column name is split into words, and if there is a case insenitive match on any of the '
                                 'members of the list, that exact capitalization is used.  Alternatively, a dictionary '
                                 'can be provided.  In this form, the key value is used to make a case insensitive match '
                                 'and the value is used.  Matches are checked prior to splitting a column into words, after'
                                 'the split is done, and after the words are joined back into the complete column name.'
                            )
        parser.add_argument('--derivafile', default=None,
                            help='Filename for deriva-py program. Can be input or output depending on other arguments. '
                                 '[Default: table name]')
        parser.add_argument('--schemafile', nargs='?', const=True, default=None,
                            help='If this argument is used without and arguement, then a schema file is output.'
                                 'If an argument is provided, then that schema file is used for the table.')
        parser.add_argument('--chunksize', default=10000, type=int,
                            help='Number of rows to use in chunked upload [Default:10000]')
        parser.add_argument('--validate', action='store_true',
                            help='Validate the table before uploading [Default:False]')
        parser.add_argument('--create', dest='create_table', action='store_true',
                            help='Automatically create catalog table based on column type inference [Default:False]')
        parser.add_argument('--upload', action='store_true', help='Load data into catalog [Default:False]')

    @staticmethod
    def _get_credential(host_name, token=None):
        if token:
            return {"cookie": "webauthn={t}".format(t=token)}
        else:
            return get_credential(host_name)

    def main(self):

        args = self.parse_cli()

        if not (args.convert or args.create_table or args.validate or args.upload):
            args.convert = True
            if args.derivafile is None:
                args.derivafile = None

        credential = self._get_credential(args.server)

        try:
            catalog = ErmrestCatalog('https', args.host, args.catalog_id, credentials=credential)

            table = DerivaCSV(args.tabledata, args.schema_model,
                              table_name=args.table_model, column_map=args.column_map,
                              key_columns=args.key_columns, row_number_as_key=args.row_number_as_key,
                              schema=args.schemafile)

            table.create_validate_upload_csv(catalog,
                                             convert=args.convert, validate=args.validate, create=args.create_table,
                                             upload=args.upload, upload_id=args.upload_id,
                                             derivafile=args.derivafile, schemafile=args.schemafile,
                                             chunk_size=args.chunksize)
        except DerivaCSVError as err:
            sys.stderr.write(str(err.msg))
            return 1
        except HTTPError as err:
            sys.stderr.write(str(err.msg))
            return 1
        except ValueError as err:
            sys.stderr.write(str(err.msg))
            return 1
        return


def main():
    DESC = "DERIVA Dump CSV Command-Line Interface"
    INFO = "For more information see: https://github.com/informatics-isi-edu/deriva-catalog-manage"
    return DerivaCSVCLI(DESC, INFO).main()


if __name__ == '__main__':
    sys.exit(main())
