
import csv
import logging

from deriva.core import get_credential, DerivaServer
import deriva.core.ermrest_model as em
from deriva.utils.catalog.manage.deriva_csv import DerivaCSV
from deriva.utils.catalog.components.configure_catalog import DerivaCatalogConfigure
from deriva.utils.catalog.components.deriva_model import DerivaTable, DerivaCatalogError, \
     DerivaKey, DerivaForeignKey, DerivaVisibleSources, DerivaContext, DerivaColumn

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

table_size = 10
column_count = 5
schema_name = 'TestSchema'
table_name = 'Foo'
public_table_name = 'Foo_Public'

# Create test datasets
csv_file = table_name + '.csv'
csv_file_public = public_table_name + ".csv"

def load_csvs(catalog):
    (row, headers) = generate_test_csv(column_count)
    with open(csv_file, 'w', newline='') as f:
        tablewriter = csv.writer(f)
        for i, j in zip(range(table_size + 1), row):
            tablewriter.writerow(j)
    
    (row, headers) = generate_test_csv(column_count)
    with open(csv_file_public, 'w', newline='') as f:
        tablewriter = csv.writer(f)
        for i, j in zip(range(table_size + 1), row):
            tablewriter.writerow(j)

    # Upload CSVs into catalog, creating two new tables....
    csv_foo = DerivaCSV(csv_file, schema_name, column_map=['ID'], key_columns='id')
    csv_foo.create_validate_upload_csv(catalog, convert=True, create=True, upload=True)
    
    csv_foo_public = DerivaCSV(csv_file_public, schema_name, column_map=True, key_columns='id')
    csv_foo_public.create_validate_upload_csv(catalog, convert=True, create=True, upload=True)

    table = catalog.schema_model('TestSchema').table_model('Foo')
    table.configure_table_defaults(public=True)
    table.create_default_visible_columns(really=True)
    table_public = catalog.schema_model('TestSchema').table_model('Foo')
    table_public.configure_table_defaults(public=True)
    table_public.create_default_visible_columns(really=True)
    

# Create a test catalog
server = 'dev.isrd.isi.edu'
credentials = get_credential(server)
catalog_id = 55001

def create_test_catalog():
    new_catalog = DerivaServer('https', server, credentials).create_ermrest_catalog()
    catalog_id = new_catalog.catalog_id()
    #new_catalog = ErmrestCatalog('https',host, catalog_id, credentials=credentials)
    print('Catalog_id is', catalog_id)
    return DerivaCatalogConfigure(server, catalog_id=catalog_id)


def set_default_config(catalog):
    # Set up catalog into standard configuration
    catalog.configure_baseline_catalog(catalog_name='test', admin='isrd-systems')
    schema = catalog.create_schema(schema_name)
    return catalog



def test_key_funcs(catalog):
    table = catalog['public']['ERMrest_Client']
    table.create_columns(DerivaColumn(table, 'Foo','text'))
    table.create_key()


# Mess with tables:

#print('Creating asset table')

def delete_tables(catalog, tlist):
    for i in tlist:
        try:
            catalog.schema_model('TestSchema').table_model(i).delete()
        except KeyError:
            pass
        

def delete_columns(table, tlist):
    for i in tlist:
        try:
            table.delete_columns([i])
        except KeyError:
            pass

tlist = ['Collection_Foo', 'Collection1_Foo', 'Collection_Foo_Public', 'Collection1_Foo_Public','Collection','Collection1','Collection_Status']


def create_collection(catalog):
    schema = catalog.schema_model('TestSchema')
    tlist = ['Collection_Foo', 'Collection1_Foo', 'Collection_Foo_Public', 'Collection1_Foo_Public', 'Collection',
             'Collection1', 'Collection_Status']
    delete_tables(catalog, tlist)
        
    test_schema = catalog['TestSchema']
    print('Creating collection')
    collection = test_schema.create_table('Collection',
                             [em.Column.define('Name',
                                               em.builtin_types['text']),
                              em.Column.define('Description',
                                               em.builtin_types['markdown']),
                              em.Column.define('Status', em.builtin_types['text'])]
                             )
    collection.configure_table_defaults()

    collection.associate_tables(schema_name, table_name)
    collection.associate_tables(schema_name, public_table_name)
    collection.create_default_visible_columns(really=True)
    collection.create_default_visible_foreign_keys(really=True)
    
    collection_status = test_schema.create_vocabulary('Collection_Status', 'TESTCATALOG:{RID}')
    collection.link_vocabulary('Status', collection_status)
    
    print('Adding element to collection')
    collection.datapath().insert([{'Name': 'Foo', 'Description':'My collection'}])
    return collection

def move_collection(catalog):
    schema = catalog.schema_model('TestSchema')
    tlist = ['Collection1_Foo','Collection1_Foo_Public','Collection1']
    delete_tables(catalog, tlist)
    schema.table_model('Collection').move_table('TestSchema', 'Collection1')
    schema.table_model('Collection_Foo').move_table('TestSchema', 'Collection1_Foo')

def create_link():
    pass

# table.create_asset_table('ID')


def test_tables(catalog):
    print('Renaming column')
    collection.rename_column('Status','MyStatus')
    print('Rename done')

    foo_table = DerivaTable(catalog, schema_name, "Foo")

    foo_table.delete_columns(['Field_3'])

    foo_table.move_table('WWW','Fun',
                        column_defs=[em.Column.define('NewColumn', em.builtin_types['text'], nullok=False)],
                         column_map={'ID':'NewID'}, column_fill={'NewColumn': 'hi there'}, delete_table=False)
    
    
def test_move_columns():
    pass