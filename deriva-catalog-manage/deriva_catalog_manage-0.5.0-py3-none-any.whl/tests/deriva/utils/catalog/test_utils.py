import os
import random
import datetime
import string
import time
import logging
import sys

from deriva.core import DerivaServer, get_credential
from deriva.utils.catalog.components.deriva_model import DerivaModel, DerivaCatalog, DerivaColumn, DerivaKey, DerivaForeignKey

logger = logging.getLogger(__name__)


def clean_schema(catalog, schemas):
    logging.info('Cleaning schema...')
    t0 = time.time()
    if type(schemas) is str:
        schemas =[schemas]
    with DerivaModel(catalog) as m:
        model = m.catalog_model()
        for s in schemas:
            for k, t in model.schemas[s].tables.copy().items():
                for fk in t.foreign_keys.copy():
                    fk.delete(catalog.ermrest_catalog, t)
        for s in schemas:
            for k, t in model.schemas[s].tables.copy().items():
                t.delete(catalog.ermrest_catalog, model.schemas[s])

    logger.info('Time to clear schema %s', time.time()-t0)

def generate_test_tables(catalog, schema_name):
    logging.info('generating test tables')
    logging.disable(logging.CRITICAL)
    t0 = time.time()
    table1 = catalog[schema_name].create_table(
        'Table1',
        [DerivaColumn.define('ID1_Table1', 'int4'),
         DerivaColumn.define('ID2_Table1', 'int4'),
         DerivaColumn.define('ID3_Table1', 'int4'),
         DerivaColumn.define('ID4_Table1', 'int4'),
         DerivaColumn.define('Col1_Table1', 'text'),
         DerivaColumn.define('Col2_Table1', 'text'),
         DerivaColumn.define('Col3_Table1', 'text')],
        key_defs=[DerivaKey.define(['ID1_Table1']),
                  DerivaKey.define(['ID4_Table1']),
                  DerivaKey.define(['ID2_Table1', 'ID3_Table1'])]
    )

    table1.datapath().insert(
    [
        {'ID1_Table1':1, 'ID2_Table1':2, 'ID3_Table1':3, 'ID4_Table1':4, 'Col1_Table1':'a', 'Col2_Table1':'b', 'Col3_Table1': 'c'},
        {'ID1_Table1': 5, 'ID2_Table1': 6, 'ID3_Table1': 7, 'ID4_Table1': 8, 'Col1_Table1': 'd', 'Col2_Table1': 'e', 'Col3_Table1': 'f'}
     ],
    )

    table1.visible_columns.insert_context('filter', {'and': ['Col1_Table1', 'Col2_Table1']})
    logger.info('Time to create table1 %s', time.time()-t0)
 #   logging.disable(logging.CRITICAL)
    t0 = time.time()
    table2 = catalog[schema_name].create_table(
        'Table2',
        [DerivaColumn.define('ID1_Table2', 'int4'),
         DerivaColumn.define('ID2_Table2', 'int4'),
         DerivaColumn.define('ID3_Table2', 'int4'),
         DerivaColumn.define('Col1_Table2', 'text'),
         DerivaColumn.define('Col2_Table2', 'text'),
         DerivaColumn.define('Col3_Table2', 'text')],
        key_defs=[DerivaKey.define(['ID1_Table2']),
                  DerivaKey.define(['ID2_Table2', 'ID3_Table2'])],
        fkey_defs=[DerivaForeignKey.define(['ID1_Table2'], table1, ['ID1_Table1']),
                   DerivaForeignKey.define(['ID2_Table2', 'ID3_Table2'], table1,
                                           ['ID2_Table1', 'ID3_Table1'])]
    )
    table2.visible_columns.insert_context('filter', {'and': ['Col1_Table2', 'Col2_Table2']})
    table2.datapath().insert(
    [
        {'ID1_Table2':1, 'ID2_Table2':2, 'ID3_Table2':3, 'ID4_Table2':4, 'Col1_Table2':'a', 'Col2_Table2':'b', 'Col3_Table2': 'c'},
        {'ID1_Table2': 5, 'ID2_Table2': 6, 'ID3_Table2': 7, 'ID4_Table2': 8, 'Col1_Table2': 'd', 'Col2_Table2': 'e', 'Col3_Table2': 'f'}
     ],
    )

    logger.info('Time to create table2 %s', time.time()-t0)
    logging.disable(logging.NOTSET)



def generate_test_csv(columncnt):
    """
    Generate a test CSV file for testing derivaCSV routines.  First row returned will be a header.
    :param columncnt: Number of columns to be used in the CSV.
    :return: generator function and a map of the column names and types.
    """
    type_list = ['int4', 'boolean', 'float8', 'date', 'text']
    column_types = ['int4'] + [type_list[i % len(type_list)] for i in range(columncnt)]
    column_headings = ['id'] + ['field {}'.format(i) for i in range(len(column_types))]

    missing_value = .2  # What fraction of values should be empty.

    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x) for x in range(0, 100)]

    def col_value(c):
        v = ''

        if random.random() > missing_value:
            if c == 'boolean':
                v = random.choice(['true', 'false'])
            elif c == 'int4':
                v = random.randrange(-1000, 1000)
            elif c == 'float8':
                v = random.uniform(-1000, 1000)
            elif c == 'text':
                v = ''.join(random.sample(string.ascii_letters + string.digits, 5))
            elif c == 'date':
                v = str(random.choice(date_list))
        return v

    def row_generator(header=True):
        row_count = 1
        while True:
            if header is True:
                row = column_headings
                header = False
            else:
                row = [row_count]
                row_count += 1
                row.extend([col_value(i) for i in column_types])
            yield row

    return row_generator(), [{'name': i[0], 'type': i[1]} for i in zip(column_headings, column_types)]


# Create directories for testing upload spec.
def upload_test(schema_name, table_name):
    os.makedirs('upload_test', exist_ok=True)
    os.chdir('upload_test')
    create_upload_dirs(schema_name, table_name, range(1, 3))

    for i in os.listdir('assets/{}/{}'.format(schema_name, table_name)):
        filename = 'assets/{}/{}/{}/{}'.format(schema_name, table_name, i, 'foo.txt')
        with open(filename, "w") as f:
            f.write("FOOBAR {}\n".format(i))


def create_upload_dirs(schema_name, table_name, iditer):
    os.makedirs('records/{}'.format(schema_name), exist_ok=True)
    for i in iditer:
        asset_dir = 'assets/{}/{}/{}'.format(schema_name, table_name, i)
        os.makedirs(asset_dir, exist_ok=True)
    return


def create_catalog(server):
    t0 = time.time()
    credentials = get_credential(server)
    catalog = DerivaServer('https', server, credentials=credentials).create_ermrest_catalog()
    catalog_id = catalog.catalog_id
    logger.info('Catalog_id is {}'.format(catalog_id))

    catalog = DerivaCatalog(server, catalog_id=catalog_id, validate=False)
    logger.info('Time to create catalog %s', time.time()-t0)
    return catalog


def delete_catalog(ermrest_catalog):
    if os.environ.get("DCM_PRESERVE_TEST_CATALOGS", False):
        return
    try:
        logger.info("Deleting catalog ID: %s" % ermrest_catalog.catalog_id)
        ermrest_catalog.delete_ermrest_catalog(really=True)
    except Exception as e:
        logger.warning("Unable to delete catalog: %s" % e)
        raise
