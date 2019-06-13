import unittest
from unittest import TestCase
import warnings
from requests.exceptions import HTTPError
import logging
import sys


from deriva.core import get_credential, DerivaServer
import deriva.core.ermrest_model as em
from deriva.utils.catalog.components.deriva_model import *
from tests.deriva.utils.catalog.test_utils import *

logging.basicConfig(
    level=logging.INFO,
    format='[%(lineno)d] %(funcName)20s() %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings('ignore', category=ResourceWarning)

server = 'dev.isrd.isi.edu'
catalog_id = 1
catalog = None
schema_name = 'TestSchema'

def setUpModule():
    global catalog, catalog_id
    catalog = create_catalog(server)
    catalog_id = catalog.catalog_id
    t0 = time.time()
    logging.info('Creating schema')
    with DerivaModel(catalog) as m:
        model = m.catalog_model()
        model.create_schema(catalog.ermrest_catalog, em.Schema.define(schema_name))
        model.create_schema(catalog.ermrest_catalog, em.Schema.define('TestSchema1'))
    logging.info('Schema created %s', time.time() - t0)

def tearDownModule():
    delete_catalog(catalog.ermrest_catalog)


class TestVisibleSources(TestCase):

    @classmethod
    def setUpClass(cls):
        global catalog
        clean_schema(catalog, ['TestSchema', 'TestSchema1'])

    def setUp(self):
        clean_schema(catalog, ['TestSchema', 'TestSchema1'])
        ermrest_catalog = catalog.ermrest_catalog
        with DerivaModel(catalog) as m:
            model = m.catalog_model()
            t1 = model.schemas[schema_name].create_table(catalog.ermrest_catalog, em.Table.define('TestTable1', []))
            t2 = model.schemas[schema_name].create_table(catalog.ermrest_catalog, em.Table.define('TestTable2', []))

            for i in ['Foo', 'Foo1', 'Foo2']:
                t1.create_column(ermrest_catalog, em.Column.define(i, em.builtin_types['text']))
                t2.create_column(ermrest_catalog, em.Column.define(i, em.builtin_types['text']))

            t2.create_key(
                ermrest_catalog,
                em.Key.define(['Foo2'], constraint_names=[(schema_name, 'TestTable1_Foo2_key')])
            )

            t1.create_fkey(
                ermrest_catalog,
                em.ForeignKey.define(['Foo2'], schema_name, 'TestTable2', ['Foo2'],
                                     constraint_names=[[schema_name, 'TestTable1_Foo2_fkey']])
            )

            main = model.schemas[schema_name].create_table(
                catalog.ermrest_catalog,
                em.Table.define('Main',
                                [em.Column.define('text_col', em.builtin_types['text']),
                                 em.Column.define('f1_fkey', em.builtin_types['text'])]))

            f1 = model.schemas[schema_name].create_table(
                catalog.ermrest_catalog,
                em.Table.define('F1', [em.Column.define('f1_text', em.builtin_types['text'])]))

            f2 = model.schemas[schema_name].create_table(
                catalog.ermrest_catalog,
                em.Table.define('F2', [em.Column.define('main_fkey', em.builtin_types['text'])]))

            main_f3 = model.schemas[schema_name].create_table(
                catalog.ermrest_catalog,
                em.Table.define('Main_F3',
                                [em.Column.define('main_fkey', em.builtin_types['text']),
                                 em.Column.define('f3_fkey', em.builtin_types['text'])]))

            f3 = model.schemas[schema_name].create_table(
                catalog.ermrest_catalog,
                em.Table.define('F3',
                                [em.Column.define('f3_text', em.builtin_types['text'])]
                                )
            )

            main.create_fkey(ermrest_catalog,
                             em.ForeignKey.define(['f1_fkey'], 'TestSchema', 'F1', ['RID'],
                                                  constraint_names=[('TestSchema', 'fk1_cons')]
                                                  ))

            f2.create_fkey(ermrest_catalog,
                           em.ForeignKey.define(['main_fkey'], 'TestSchema', 'Main', ['RID'],
                                                constraint_names=[('TestSchema', 'fk2_cons')]
                                                ))

            main_f3.create_fkey(ermrest_catalog,
                                em.ForeignKey.define(['main_fkey'], 'TestSchema', 'Main', ['RID'],
                                                     constraint_names=[('TestSchema', 'fk3_cons')]
                                                     ))
            main_f3.create_fkey(ermrest_catalog,
                                em.ForeignKey.define(['f3_fkey'], 'TestSchema', 'F3', ['RID'],
                                                     constraint_names=[('TestSchema', 'main_f3_cons')]
                                                     ))
        catalog.refresh()

    def test_source_spec(self):
        # Normal Columns
        main = catalog['TestSchema']['Main']
        self.assertEqual(DerivaSourceSpec(main, 'text_col').spec, {'source': 'text_col'})
        with self.assertRaises(DerivaSourceError):
            DerivaSourceSpec(main, 'Foobar')
        self.assertEqual(DerivaSourceSpec(main, {'source': 'text_col'}).spec, {'source': 'text_col'})
        self.assertEqual(DerivaSourceSpec(main, {'source': 'RID', 'entity': False}).spec,
                         {'source': 'RID', 'entity': False})

        # Key Columns
        self.assertEqual(DerivaSourceSpec(main, ['TestSchema', 'Main_RIDkey1']).spec, {'source': 'RID'})
        with self.assertRaises(DerivaCatalogError):
            DerivaSourceSpec(main, ['TestSchema', 'Foobar'])

        # ForeignKey Columns
        self.assertEqual(DerivaSourceSpec(main, ['TestSchema', 'fk1_cons']).spec,
                         {"source": [{"outbound": ("TestSchema", "fk1_cons")}, "RID"]})
        self.assertEqual(DerivaSourceSpec(main, {"source": [{"outbound": ["TestSchema", "fk1_cons"]}, "RID"]}).spec,
                         {"source": [{"outbound": ["TestSchema", "fk1_cons"]}, "RID"]})

        with self.assertRaises(DerivaCatalogError):
            DerivaSourceSpec(main, {"source": [{"outbound": ["TestSchema1", "fk1_cons"]}, "RID"]})
        with self.assertRaises(DerivaCatalogError):
            DerivaSourceSpec(main, {"source": [{"outbound": ["TestSchema", "fk1_cons1"]}, "RID"]})

        # Inbound foreignkey columns
        self.assertEqual(DerivaSourceSpec(main, ["TestSchema", "fk2_cons"]).spec,
                         {"source": [{"inbound": ("TestSchema", "fk2_cons")}, "RID"]})
        self.assertEqual(DerivaSourceSpec(main, ["TestSchema", "fk3_cons"]).spec,
                         {"source": [{"inbound": ("TestSchema", "fk3_cons")}, "RID"]})
        self.assertEqual(DerivaSourceSpec(main,
                                          {"source": [{"inbound": ("TestSchema", "fk2_cons")}, "RID"]}).spec,
                         {"source": [{"inbound": ("TestSchema", "fk2_cons")}, "RID"]})
        self.assertEqual(DerivaSourceSpec(main,
                                          {"source": [{"inbound": ("TestSchema", "fk3_cons")},
                                                      {"outbound": ("TestSchema", "main_f3_cons")}, "RID"]}).spec,
                         {"source": [{"inbound": ("TestSchema", "fk3_cons")},
                                     {"outbound": ("TestSchema", "main_f3_cons")}, "RID"]})

        self.assertEqual(
            DerivaSourceSpec(main, 'f1_fkey').make_outbound().spec,
            {"source": [{"outbound": ("TestSchema", "fk1_cons")}, "RID"]}
        )
        self.assertEqual(
            DerivaSourceSpec(main, {"source": [{"outbound": ["TestSchema", "fk1_cons"]}, "RID"]}).make_column().spec,
            {"source": 'f1_fkey'}
        )

        main.visible_columns = {'*' : [{
            "source": [{'inbound': ('TestSchema', 'fk3_cons')},
                       {'outbound': ('TestSchema', 'main_f3_cons')}, 'RID']}]}
        # Now test to see if renaming a constraint in a path works.
        catalog['TestSchema']['Main_F3'].rename_columns({'main_fkey': 'main_fkeya'})
        self.assertDictEqual(main.annotations[chaise_tags.visible_columns],
                         {'*': [{'source': [{'inbound': ('TestSchema', 'Main_F3_main_fkeya_fkey')},
                                            {'outbound': ('TestSchema', 'main_f3_cons')},
                                            ['RID']]}]}

                         )

    def test_normalize_positions(self):
        DerivaVisibleSources._normalize_positions({'all'})

    def test_insert_sources(self):
        ermrest_catalog = catalog.ermrest_catalog
        t1 = ermrest_catalog.getCatalogModel().schemas['TestSchema'].tables['TestTable1']
        t1.annotations[chaise_tags.visible_columns] = {}

        table = catalog['TestSchema']['TestTable1']
        vs = table.visible_columns
        vs.insert_context('*')
        vs.insert_context('filter')
        vs.insert_sources([DerivaSourceSpec(table, 'Foo'), DerivaSourceSpec(table, 'Foo2')])
        print('star', table.visible_columns['*'])
        print('filter', table.visible_columns['filter'])
        self.assertIn({'source': 'Foo2'}, table.visible_columns['*'])


class TestColumnMap(TestCase):

    @classmethod
    def setUpClass(cls):
        global catalog
        clean_schema(catalog, ['TestSchema', 'TestSchema1'])

    def setUp(self):
        clean_schema(catalog, [schema_name, 'TestSchema1'])
        ermrest_catalog = catalog.ermrest_catalog
        with DerivaModel(catalog) as m:
            model = m.catalog_model()
            t1 = model.schemas[schema_name].create_table(catalog.ermrest_catalog, em.Table.define('TestTable1', []))
            for i in ['ID', 'Field_1', 'Field_2', 'Field_3']:
                t1.create_column(ermrest_catalog, em.Column.define(i, em.builtin_types['text']))
        catalog.refresh()

    def test_column_map(self):
        # Normal Columns
        main = catalog['TestSchema']['TestTable1']
        cm = DerivaColumnMap(main,
                             {'Field_1': 'Foobar',
                              'RCB': 'RCB1',
                              'ID': 'ID1',
                              'Bozo': 'text'},
                             main)
        print(cm)

        cm = DerivaColumnMap(main,
                             {'Field_1': {'name': 'Foobar', 'default': 23},
                              'RCB': 'RCB1',
                              'ID': {'name': 'ID1', 'fill': 26},
                              'Bozo': 'text'},
                             main)
        print(cm)


class TestAttributes(TestCase):
    def setUp(self):
        clean_schema(catalog, [schema_name, 'TestSchema1'])

    def test_display(self):
        logger.info('Creating tables....')
        generate_test_tables(catalog, schema_name)
        logger.info('done')
        table = catalog['TestSchema']['Table1']
        table.display = 'Foobar'
        root_model = catalog.ermrest_catalog.getCatalogModel()
        self.assertEqual(root_model.schemas['TestSchema'].tables['Table1'].annotations[chaise_tags.display], 'Foobar')
        self.assertEqual(table.display, 'Foobar')


class TestDerivaTable(TestCase):

    def setUp(self):
        logging.info('Calling table setup...')
        clean_schema(catalog, [schema_name, 'TestSchema1'])

    def test_lookup_table(self):
        with DerivaModel(catalog) as m:
            model = m.catalog_model()
            t1 = model.schemas[schema_name].create_table(catalog.ermrest_catalog, em.Table.define('TestTable', []))
            table = catalog[schema_name].tables['TestTable']
            print(table, catalog[schema_name])
            self.assertEqual(table.name, 'TestTable')

    def test_table_attributes(self):
        generate_test_tables(catalog, schema_name)
        table = catalog['TestSchema']['Table1']

        table.comment ='Comment 1'
        table.acls = {'owner': ['carl']}
        table.acl_bindings =  {'set_owner': {"types": ["update"], "projection": ["RCB"], "projection_type": "acl"}}
        table.acls['select'] = ['bubba']
        table.display = {'tag:misd.isi.edu,2015:display': {'name': 'foo'}}
        catalog.refresh()
        table = catalog['TestSchema']['Table1']

        self.assertEqual(table.comment, 'Comment 1')
        self.assertEqual(table.acls, {'owner': ['carl'], 'select': ['bubba']})
        self.assertEqual(table.acl_bindings,
                         {'set_owner':
                              {"types": ["update"], "projection": ["RCB"], "projection_type": "acl", 'scope_acl': ['*']}}
                         )
        self.assertEqual(table.display, {'tag:misd.isi.edu,2015:display': {'name': 'foo'}})

        table.comment = 'Comment 2'
        table.acls.update({'owner': ['carl1']})
        table.acl_bindings = {'set_owner': {"types": ["update"], "projection": ["RMB"], "projection_type": "acl"}}
        table.display = {'tag:misd.isi.edu,2015:display': {'name': 'foo1'}}
        catalog.refresh()
        table = catalog['TestSchema']['Table1']

        del table.acls['select']
        self.assertEqual(table.comment, 'Comment 2')
        self.assertEqual(table.acls, {'owner': ['carl1']})
        self.assertEqual(table.acl_bindings,
                         {'set_owner':
                              {"types": ["update"], "projection": ["RMB"], "projection_type": "acl",
                               'scope_acl': ['*']}}
                         )
        self.assertEqual(table.display, {'tag:misd.isi.edu,2015:display': {'name': 'foo1'}})

    def test_create_table(self):
        table = catalog[schema_name].create_table('TestTable1', [], comment='My test table')
        self.assertEqual(table.name, 'TestTable1')
        self.assertEqual(table.comment, 'My test table')
        table.comment = "My new comment"
        self.assertEqual(table.comment, 'My new comment')
        table = catalog[schema_name].create_table('TestTable2', [DerivaColumn.define('Foo', type='text')])
        self.assertEqual(table.name, 'TestTable2')
        self.assertEqual(table.visible_columns['*'],
                         [{'source': 'RID'},
                          {'source': 'RCT'},
                          {'source': 'RMT'},
                          {'source': 'RCB'},
                          {'source': 'RMB'},
                          {'source': 'Foo'}])
        table.delete()
        with self.assertRaises(DerivaCatalogError):
            catalog[schema_name]['TestTable2']

    def test_column_access(self):
        table = catalog['public']['ERMrest_Client']
        self.assertEqual(table['RID'].name, 'RID')
        self.assertEqual(table.column('RID').name, 'RID')
        self.assertEqual(table.columns['RID'].name, 'RID')
        self.assertEqual(table.columns[2].name, 'RMT')
        self.assertTrue({'RID', 'RCB', 'RMB', 'RCT', 'RMT'} < {i.name for i in table.columns})
        print(table['RID'])
        self.assertIsInstance(table['RID'].definition(), em.Column)
        with self.assertRaises(DerivaCatalogError):
            catalog['public']['foobar']

        generate_test_tables(catalog, schema_name)

        table = catalog[schema_name]['Table1']
        self.assertEqual(table['Col1_Table1'].name, 'Col1_Table1')

    def test_column_add(self):
        table = catalog[schema_name].create_table('TestTable1', [])
        table.create_columns(DerivaColumn.define('Foo1', 'text'))
        self.assertIn('Foo1', table.columns)
        self.assertIn({'source': 'Foo1'}, table.visible_columns['*'])

    def test_deriva_column_delete(self):
        generate_test_tables(catalog, schema_name)
        table = catalog['TestSchema']['Table1']
        print(table)
        table.visible_columns.insert_context('*')
        self.assertEqual(table['Col1_Table1'].name, 'Col1_Table1')
        print(DerivaSourceSpec(table, 'Col1_Table1').spec)
        print(table.visible_columns)
        table['Col1_Table1'].delete()
        with self.assertRaises(DerivaCatalogError):
            table['Col1_Table1']
        self.assertNotIn({'source': 'Col1_Table1'}, table.visible_columns)
        self.assertNotIn({'source': 'Col1_Table1'}, table.visible_columns['*'])
        self.assertNotIn({'source': 'Col1_Table1'}, table.visible_columns['entry'])
        table.delete_columns(['Col2_Table1', 'Col3_Table1'])
        with self.assertRaises(DerivaCatalogError):
            table['Col2_Table1']

    def test_deriva_column_delete_key_column(self):
        generate_test_tables(catalog, schema_name)
        table1 = catalog['TestSchema']['Table1']
        table2 = catalog['TestSchema']['Table2']

        table1['ID4_Table1'].delete()
        with self.assertRaises(DerivaCatalogError):
            table1['ID4_Table1']
        self.assertNotIn({'source': 'ID4_Table1'}, table1.visible_columns['*'])
        self.assertNotIn({'source': 'ID4_Table1'}, table1.visible_columns['entry'])

        # Try deleting one column of a compound key
        logger.info('Deleting one column of a compound key')
        with self.assertRaises(DerivaCatalogError):
            table2.delete_columns(['ID2_Table2'])

        logger.info('Deleting column referenced by foreign key')
        with self.assertRaises(DerivaCatalogError):
            table1.delete_columns(['ID1_Table1'])

        self.assertIn({'source': [{'inbound': ('TestSchema', 'Table2_ID2_Table2_ID3_Table2_fkey')}, 'RID']},
                      table1.visible_foreign_keys['*'])
        table2.delete_columns(['ID2_Table2', 'ID3_Table2'])
        # Check to see if columns are not in table
        with self.assertRaises(DerivaCatalogError):
            table2['ID2_Table2']
        with self.assertRaises(DerivaCatalogError):
            table2['ID3_Table2']

        # Check to see if columns are not in visible_columns
        self.assertNotIn({'source': 'ID2_Table2'}, table1.visible_columns['*'])
        self.assertNotIn({'source': 'ID3_Table2'}, table1.visible_columns['*'])
        # Check to see if referenced_by in table1 is correct.
        self.assertNotIn({'source': [{'inbound': ('TestSchema', 'Table1_ID2_Table1_ID3_Table1_fkey')}, 'RID']},
                      table1.visible_foreign_keys['*'])
        #table1.referenced_by()

    def test_keys(self):
        table = catalog[schema_name].create_table('TestTable1',
                                                  [DerivaColumn.define('Foo1', 'text'),
                                                   DerivaColumn.define('Foo2', 'text'),
                                                   DerivaColumn.define('Foo3', 'text')],
                                                  key_defs=[DerivaKey.define(['Foo1', 'Foo2'])])
        table.create_key(['Foo1'], comment='My Key')

        self.assertEqual({i.name for i in table.keys}, {'TestTable1_RIDkey1', 'TestTable1_Foo1_key', 'TestTable1_Foo1_Foo2_key'})

        self.assertEqual(table.key['Foo1'].name, 'TestTable1_Foo1_key')
        self.assertEqual([i.name for i in table.key['Foo1'].columns], ['Foo1'])
        self.assertEqual(table.key['Foo1', 'Foo2'].name, 'TestTable1_Foo1_Foo2_key')
        self.assertEqual({i.name for i in table.key['Foo1', 'Foo2'].columns}, {'Foo1', 'Foo2'})
        self.assertEqual(table.key['TestTable1_Foo1_key'].name, 'TestTable1_Foo1_key')
        self.assertEqual(table.keys['TestTable1_Foo1_key'].name, 'TestTable1_Foo1_key')
        self.assertIn('TestTable1_Foo1_key', table.keys)

        self.assertEqual(table.key['Foo1'].columns['Foo1'].name, 'Foo1')
        self.assertEqual(table.key['Foo1'].columns[6].name, 'Foo2')
        with self.assertRaises(DerivaCatalogError):
            table.create_key(['Foo1'], comment='My Key')
        with self.assertRaises(DerivaCatalogError):
            table.keys['TestTable1_Foo1']

        table.keys['Foo1'].delete()
        with self.assertRaises(DerivaCatalogError):
            table.keys['TestTable1_Foo1']
        table.create_key(['Foo1'], comment='My Key')
        self.assertIn('TestTable1_Foo1_key', table.keys)

        # Try to delete column in compound key
        with self.assertRaises(DerivaCatalogError):
            table.columns['Foo2'].delete()

    def test_fkeys(self):
        table1 = catalog[schema_name].create_table('TestTable1',
                                                   [DerivaColumn.define('Foo1a', 'text'),
                                                    DerivaColumn.define('Foo2a', 'text'),
                                                    DerivaColumn.define('Foo3a', 'text')],
                                                   key_defs=[DerivaKey.define(['Foo1a']),
                                                             DerivaKey.define(['Foo1a', 'Foo2a'])])

        table2 = catalog[schema_name].create_table('TestTable2',
                                                   [DerivaColumn.define('Foo1', 'text'),
                                                    DerivaColumn.define('Foo2', 'text'),
                                                    DerivaColumn.define('Foo3', 'text')],
                                                   key_defs=[DerivaKey.define(['Foo1'])],
                                                   fkey_defs=[DerivaForeignKey.define(['Foo1'], table1, ['Foo1a']),
                                                              DerivaForeignKey.define(['Foo1', 'Foo2'], table1,
                                                                                      ['Foo1a', 'Foo2a'])]
                                                   )
        logger.info('test table created')

        self.assertEqual(table2.foreign_key['Foo1'].name, 'TestTable2_Foo1_fkey')
        self.assertEqual(table2.foreign_keys['Foo1'].name, 'TestTable2_Foo1_fkey')
        self.assertEqual(table2.foreign_keys['TestTable2_Foo1_fkey'].name, 'TestTable2_Foo1_fkey')

        self.assertEqual({i.name for i in table2.foreign_keys['TestTable2_Foo1_Foo2_fkey'].columns}, {'Foo1', 'Foo2'})
        self.assertEqual({i.name for i in table2.foreign_keys['TestTable2_Foo1_Foo2_fkey'].referenced_columns},
                         {'Foo1a', 'Foo2a'})
        self.assertEqual(table2.foreign_keys['TestTable2_Foo1_Foo2_fkey'].referenced_columns['Foo1a'].name, "Foo1a")

        self.assertTrue(table1.referenced_by['TestTable2_Foo1_fkey'])

        with self.assertRaises(DerivaCatalogError):
            table2.foreign_keys['Bar'][0]

        print(table2.visible_columns['*'])
        self.assertIn({'source': [{'outbound': ('TestSchema', 'TestTable2_Foo1_fkey')}, 'RID']},
                      table2.visible_columns['*'])

        self.assertIn({'source': [{'inbound': ('TestSchema', 'TestTable2_Foo1_fkey')}, 'RID']},
                      table1.visible_foreign_keys['*'])
        self.assertIn({'source': [{'inbound': ('TestSchema', 'TestTable2_Foo1_Foo2_fkey')}, 'RID']},
                      table1.visible_foreign_keys['*'])

    def test_fkey_add(self):
        table1 = catalog[schema_name].create_table('TestTable1',
                                                   [DerivaColumn.define('Foo1a', 'text'),
                                                    DerivaColumn.define('Foo2a', 'text'),
                                                    DerivaColumn.define('Foo3a', 'text')],
                                                   key_defs=[DerivaKey.define(['Foo1a', ]),
                                                             DerivaKey.define(['Foo1a', 'Foo2a'])])

        table2 = catalog[schema_name].create_table('TestTable2',
                                                   [DerivaColumn.define('Foo1', 'text'),
                                                    DerivaColumn.define('Foo2', 'text'),
                                                    DerivaColumn.define('Foo3', 'text')],
                                                   key_defs=[DerivaKey.define(['Foo1'])],
                                                   )
        table1.create_key(['Foo2a'])
        table2.create_key(['Foo2'])
        table2.create_foreign_key(['Foo1'], table1, ['Foo1a'])
        table2.create_foreign_key(['Foo1', 'Foo2'], table1, ['Foo1a', 'Foo2a'])

        self.assertEqual(table2.foreign_key['Foo1'].name, 'TestTable2_Foo1_fkey')
        self.assertEqual(table2.foreign_keys['Foo1'].name, 'TestTable2_Foo1_fkey')
        self.assertEqual(table2.foreign_keys['TestTable2_Foo1_fkey'].name, 'TestTable2_Foo1_fkey')

        self.assertTrue(table1.referenced_by['TestTable2_Foo1_fkey'])
        self.assertTrue(table1.key_referenced(['Foo1a']))
        self.assertEqual(table1.key_referenced(['Foo1a'])[0].name, 'TestTable2_Foo1_fkey')
        with self.assertRaises(DerivaCatalogError):
            table1.key_referenced(['Foo1'])

        self.assertIn({'source': [{'outbound': ('TestSchema', 'TestTable2_Foo1_fkey')}, 'RID']},
                      table2.visible_columns['*'])

        self.assertIn({'source': [{'inbound': ('TestSchema', 'TestTable2_Foo1_fkey')}, 'RID']},
                      table1.visible_foreign_keys['*'])
        self.assertIn({'source': [{'inbound': ('TestSchema', 'TestTable2_Foo1_Foo2_fkey')}, 'RID']},
                      table1.visible_foreign_keys['*'])

        table2.foreign_keys['Foo1'].delete()
        with self.assertRaises(DerivaCatalogError):
            table2.columns['Foo1'].delete()

        with self.assertRaises(DerivaCatalogError):
            self.assertEqual(table2.foreign_key['Foo1'].name, 'TestTable2_Foo1_fkey')

        # Column entry in visible_columns should have changed back to simple column reference.
        self.assertIn({'source': 'Foo1'}, table2.visible_columns['*'])
        with self.assertRaises(DerivaCatalogError):
            self.assertTrue(table1.referenced_by['Foo1a'])

        self.assertNotIn({'source': [{'outbound': ('TestSchema', 'TestTable2_Foo1_fkey')}, 'RID']},
                         table2.visible_columns['*'])

        self.assertNotIn({'source': [{'inbound': ('TestSchema', 'TestTable2_Foo1_fkey')}, 'RID']},
                         table1.visible_foreign_keys['*'])

    def test_access_keys(self):
        generate_test_tables(catalog, schema_name)
        table1 = catalog['TestSchema']['Table1']
        table2 = catalog['TestSchema']['Table2']

        self.assertEqual(table2.keys['ID2_Table2','ID3_Table2'].name, 'Table2_ID2_Table2_ID3_Table2_key')
        self.assertEqual(table2.foreign_keys['ID2_Table2', 'ID3_Table2'].name, 'Table2_ID2_Table2_ID3_Table2_fkey')

        fk = table1.referenced_by['Table2_ID1_Table2_fkey']
        self.assertEqual(fk.name, 'Table2_ID1_Table2_fkey')

        fk = table1.referenced_by['Table2_ID2_Table2_ID3_Table2_fkey']
        self.assertEqual(fk.name, 'Table2_ID2_Table2_ID3_Table2_fkey')

        fk = table1.referenced_by['Table2_ID1_Table2_fkey']
        self.assertEqual(fk.name, 'Table2_ID1_Table2_fkey')

    def test_copy_columns(self):
        generate_test_tables(catalog, schema_name)
        table1 = catalog['TestSchema']['Table1']
        table2 = catalog['TestSchema']['Table2']

        table1.copy_columns(
            OrderedDict([('Col1_Table1', 'FooBar'), ('RCB', 'RCB1'), ('Bozo', 'int4'), ('Bozo1', {'type': 'text', 'default': 23})]))
        self.assertEqual(table1['FooBar'].name, 'FooBar')

        self.assertEqual([i.name for i in table1.columns],
                         ['RID', 'RCT', 'RMT', 'RCB', 'RMB',
                          'ID1_Table1', 'ID2_Table1', 'ID3_Table1', 'ID4_Table1',
                          'Col1_Table1', 'Col2_Table1', 'Col3_Table1', 'FooBar','RCB1', 'Bozo', 'Bozo1']
                        )
        self.assertEqual(
            [i['source'] for i in table1.visible_columns['*']],
            ['RID', 'RCT', 'RMT', 'RCB', 'RCB1', 'RMB',
             'ID1_Table1',    'ID2_Table1',    'ID3_Table1',    'ID4_Table1',
             'Col1_Table1', 'FooBar', 'Col2_Table1', 'Col3_Table1', 'Bozo', 'Bozo1']
        )

        table1.copy_columns({'ID4_Table1': 'ID4a_Table1'})
        self.assertEqual(table1.key['ID4a_Table1'].name, 'Table1_ID4a_Table1_key')
        self.assertEqual(table1.key['ID4_Table1'].name, 'Table1_ID4_Table1_key')
        self.assertEqual(
            [i['source'] for i in table1.visible_columns['*']],
            ['RID', 'RCT', 'RMT', 'RCB', 'RCB1', 'RMB',
             'ID1_Table1', 'ID2_Table1', 'ID3_Table1', 'ID4_Table1', 'ID4a_Table1',
             'Col1_Table1', 'FooBar', 'Col2_Table1', 'Col3_Table1', 'Bozo', 'Bozo1']
        )
        self.assertEqual([i.name for i in table1.columns],
                         ['RID', 'RCT', 'RMT', 'RCB', 'RMB',
                          'ID1_Table1', 'ID2_Table1', 'ID3_Table1', 'ID4_Table1',
                          'Col1_Table1', 'Col2_Table1', 'Col3_Table1', 'FooBar', 'RCB1','Bozo', 'Bozo1', 'ID4a_Table1']
                         )

        table1.copy_columns({'ID1_Table1': 'ID1a_Table1'})
        # Copy column that is a fkey table2:ID1
        table2.copy_columns({'ID1_Table2': 'ID1a_Table2'})
        self.assertEqual(table2.key['ID1a_Table2'].name, 'Table2_ID1a_Table2_key')
        self.assertEqual(table2.foreign_key['ID1a_Table2'].name, 'Table2_ID1a_Table2_fkey')

        # Copy a single column that is in a compound key.  This is ok because we are in the same table.
        table2.copy_columns({'ID2_Table2': 'ID2a_Table2'})
        self.assertEqual(table2.key['ID2a_Table2', 'ID3_Table2'].name, 'Table2_ID2a_Table2_ID3_Table2_key')
        self.assertEqual(table2.foreign_key['ID2a_Table2','ID3_Table2'].name, 'Table2_ID2a_Table2_ID3_Table2_fkey')

        # Copy columns that are compound key table1: ID2,ID3

        table2.copy_columns({'ID2_Table2': 'ID2b_Table2',  'ID3_Table2':'ID3b_Table2'})
        self.assertEqual(table2.key['ID2b_Table2', 'ID3b_Table2'].name, 'Table2_ID2b_Table2_ID3b_Table2_key')
        self.assertEqual(table2.foreign_key['ID2b_Table2','ID3b_Table2'].name, 'Table2_ID2b_Table2_ID3b_Table2_fkey')
        self.assertEqual(table2.foreign_key['ID3b_Table2','ID2b_Table2'].name, 'Table2_ID2b_Table2_ID3b_Table2_fkey')

    def test_copy_columns_between_tables(self):
        generate_test_tables(catalog, schema_name)
        table1 = catalog['TestSchema']['Table1']
        table2 = catalog['TestSchema']['Table2']

        # Test normal column
        table1.copy_columns(
            {'Col1_Table1': 'Foobar', 'RCB': 'RCB1', 'Bozo': 'int4', 'Bozo1': {'type': 'text', 'default': 23}}, table2)
        self.assertEqual(table2.columns['Foobar'].name, 'Foobar')
        self.assertIn({'source': 'Foobar'}, table2.visible_columns['*'])

        # Check key and fkey constraints....
        table3 = catalog[schema_name].create_table('TestTable3',[])
        table2.copy_columns({'ID1_Table2':'ID1_Table3'}, table3)
        self.assertEqual(table3.key['ID1_Table3'].name, 'TestTable3_ID1_Table3_key')
        self.assertEqual(table3.foreign_key['ID1_Table3'].name, 'TestTable3_ID1_Table3_fkey')

    def test_rename_columns(self):
        generate_test_tables(catalog, schema_name)
        table1 = catalog['TestSchema']['Table1']
        table2 = catalog['TestSchema']['Table2']

        table2.table_display ={'*': {'row_markdown_pattern': '{{{$fkeys.TestSchema.Table2_ID1_Table2_fkey.rowName}}}'}}

        # Plain old column....
        table1.rename_columns({'Col1_Table1': 'NewFoo1'})
        # Check column and visible columns.

        # Column that is pointed to by a FK.  This should fail
        with self.assertRaises(DerivaCatalogError):
            table1.rename_columns({'ID1_Table1': 'ID1a_Table1'})

        # Column that is a FK.
        table2.rename_columns({'ID1_Table2': 'ID1a_Table2'})
        table2.describe()
        # FK should be renamed as should incoming visible columns in table1
        self.assertEqual(table2.table_display,
                         {'*': {'row_markdown_pattern': '{{{$fkeys.TestSchema.Table2_ID1a_Table2_fkey.rowName}}}'}})

        # One column of a compound FK.  This should rename the FK and incoming.
        table2.rename_columns({'ID2_Table2': 'ID2a_Table2'})

    def test_move_columns_between_tables(self):
        generate_test_tables(catalog, schema_name)
        table1 = catalog['TestSchema']['Table1']
        table2 = catalog['TestSchema']['Table2']

        # Plain old column....
        table1.rename_columns({'Col1_Table1': 'NewFoo1'}, dest_table=table2)
        # Check column and visible columns.

        # Column that is pointed to by a FK.  This should fail
        with self.assertRaises(DerivaCatalogError):
            table1.rename_columns({'ID1_Table1': 'ID1a_Table1'})

        # Column that is a FK.
        table2.rename_columns({'ID1_Table2': 'ID1a_Table2'})
        # FK should be renamed as should incoming visible columns in table1

        # One column of a compound FK.  This should rename the FK and incoming.
        table2.rename_columns({'ID2_Table2': 'ID2a_Table2'})

    def test_move_columns_between_schema(self):
        generate_test_tables(catalog, schema_name)
        table1 = catalog['TestSchema']['Table1']
        table2 = catalog['TestSchema']['Table2']

        schema1 = catalog['TestSchema1']

        newtable = schema1.create_table('TestTable1', [])

        # Plain old column....
        table1.rename_columns({'Col1_Table1': 'NewFoo1'}, dest_table=newtable)
        # Check column and visible columns.

        # Column that is pointed to by a FK.  This should fail
        with self.assertRaises(DerivaCatalogError):
            table1.rename_columns({'ID1_Table1': 'ID1a_Table1'})

        # Column that is a FK.
        table2.rename_columns({'ID1_Table2': 'ID1a_Table2'})
        # FK should be renamed as should incoming visible columns in table1

        # One column of a compound FK.  This should rename the FK and incoming.
        table2.rename_columns({'ID2_Table2': 'ID2a_Table2'})


    def test_copy_table(self):
        logging.info('Starting copy_table test...')
        generate_test_tables(catalog, schema_name)
        table1 = catalog['TestSchema']['Table1']
        table2 = catalog['TestSchema']['Table2']

        t1 = table1.datapath()
        print(list(table1.datapath().attributes(
            t1.ID1_Table1, t1.ID2_Table1, t1.ID3_Table1, t1.ID4_Table1, t1.Col1_Table1, t1.Col2_Table1, t1.Col3_Table1
        )))

        t2 = table2.datapath()
        print(list(table2.datapath().attributes(
            t2.ID1_Table2, t2.ID2_Table2, t2.ID3_Table2, t2.Col1_Table2, t2.Col2_Table2, t2.Col3_Table2
        )))

        t0 = time.time()
        table1_copy = table1.copy_table('TestSchema', 'Table1_Copy')

        t1 = table1.datapath()
        print(list(table1.datapath().attributes(
            t1.ID1_Table1, t1.ID2_Table1, t1.ID3_Table1, t1.ID4_Table1, t1.Col1_Table1, t1.Col2_Table1, t1.Col3_Table1
        )))

        table2_copy = table2.copy_table('TestSchema', 'Table2_Copy')
        logging.info('Tables copied %s', time.time() - t0)

        self.assertEqual(table2_copy.key['ID1_Table2'].name, 'Table2_Copy_ID1_Table2_key')
        self.assertEqual(table2_copy.foreign_key['Table2_Copy_ID1_Table2_fkey'].name,
                         'Table2_Copy_ID1_Table2_fkey')

        print('table1 visible_keys', table1.visible_foreign_keys['*'])
        self.assertIn({'source': [{'inbound': ('TestSchema', 'Table2_Copy_ID1_Table2_fkey')}, 'RID']},
                         table1.visible_foreign_keys['*'])
        self.assertIn({'source': [{'inbound': ('TestSchema', 'Table2_Copy_ID2_Table2_ID3_Table2_fkey')}, 'RID']},
                         table1.visible_foreign_keys['*'])

        self.assertEqual([], table1_copy.visible_foreign_keys['*'])
        self.assertIn(
            {'source': [{'inbound': ('TestSchema', 'Table2_Copy_ID2_Table2_ID3_Table2_fkey')}, 'RID']},
            table1.visible_foreign_keys['*'])




    def test_copy_table_rename(self):
        generate_test_tables(catalog, schema_name)
        table1 = catalog['TestSchema']['Table1']
        table2 = catalog['TestSchema']['Table2']

        column_map = {'Col1_Table2': 'Field_1A', 'ID1_Table2': {'name': 'ID1', 'nullok': False, 'fill': 1},
                      'Status': {'type': 'int4', 'nullok': False, 'fill': 1}}
        table_copy = table2.copy_table('TestSchema', 'TableCopy')
        print(table_copy)
        #foo1 = table1.copy_table('TestSchema', 'Foo1', column_map=column_map)

    def test_copy_table_between_schema(self):
        generate_test_tables(catalog, schema_name)
        table1 = catalog['TestSchema']['Table1']
        table2 = catalog['TestSchema']['Table2']

        table1_copy = table1.copy_table('TestSchema1', 'Table1_Copy')

        table2_copy = table2.copy_table('TestSchema1', 'Table2_Copy')
        print(table1)
        print(table1_copy)
        print(table2_copy)

        self.assertEqual(table2_copy.key['ID1_Table2'].name, 'Table2_Copy_ID1_Table2_key')
        self.assertEqual(table2_copy.foreign_key['Table2_Copy_ID1_Table2_fkey'].name,
                         'Table2_Copy_ID1_Table2_fkey')

        print('table1 visible_keys', table1.visible_foreign_keys['*'])
        self.assertIn({'source': [{'inbound': ('TestSchema1', 'Table2_Copy_ID1_Table2_fkey')}, 'RID']},
                         table1.visible_foreign_keys['*'])
        self.assertIn({'source': [{'inbound': ('TestSchema1', 'Table2_Copy_ID2_Table2_ID3_Table2_fkey')}, 'RID']},
                         table1.visible_foreign_keys['*'])

        self.assertEqual([], table1_copy.visible_foreign_keys['*'])
        self.assertIn(
            {'source': [{'inbound': ('TestSchema1', 'Table2_Copy_ID2_Table2_ID3_Table2_fkey')}, 'RID']},
            table1.visible_foreign_keys['*'])

    def test_move_table(self):
        generate_test_tables(catalog, schema_name)
        table1 = catalog['TestSchema']['Table1']
        table2 = catalog['TestSchema']['Table2']

        #column_defs = [DerivaColumn.define(table, 'Status', 'int4', nullok=False)]
        table2_copy = table2.move_table('TestSchema', 'Table2_Copy')
        print(table1)
        print('visible keys', pprint.pformat(table1.visible_foreign_keys))
        print(table2_copy)
        print('visible keys', pprint.pformat(table2_copy.visible_foreign_keys))

        table1_copy = table1.move_table('TestSchema', 'Table1_Copy', delete=False)
        print(table1_copy)
        print(table1_copy.visible_columns)
        print(table2_copy)
        print(table2_copy.visible_columns)

    def test_move_table_between_schema(self):
        generate_test_tables(catalog, schema_name)
        table1 = catalog['TestSchema']['Table1']
        table2 = catalog['TestSchema']['Table2']
        print(table2)

        #column_defs = [DerivaColumn.define(table, 'Status', 'int4', nullok=False)]
        table2_copy = table2.move_table('TestSchema1', 'Table2_Copy')
        print(table1)
        print('visible keys', pprint.pformat(table1.visible_foreign_keys))
        print(table2_copy)
        print('visible keys', pprint.pformat(table2_copy.visible_foreign_keys))

        table1_copy = table1.move_table('TestSchema', 'Table1_Copy')

    def test_vocabulary_table(self):
        table1 = catalog[schema_name].create_table('TestTable1', [DerivaColumn.define('Foo1a', 'text')])
        v = catalog[schema_name].create_vocabulary('testterms', 'TESTSCHEMA:{RID}')
        self.assertTrue(v.is_vocabulary_table())

    def test_link_tables(self):
        table1 = catalog[schema_name].create_table('TestTable1', [DerivaColumn.define('Foo1a', 'text')])
        table2 = catalog[schema_name].create_table('TestTable2', [DerivaColumn.define('Foo1', 'text')])

        table1.link_tables(table2)
        self.assertIn('TestTable2', [i.name for i in table1.columns])
        print('table1 vc', table1.visible_columns)
        print('table1 vfk', table1.visible_foreign_keys)
        print('table2 vc',table2.visible_columns)
        print('table2 vfk', table2.visible_foreign_keys)

    def test_associate_tables(self):
        table1 = catalog[schema_name].create_table('TestTable1', [DerivaColumn.define('Foo1a', 'text')])
        table2 = catalog[schema_name].create_table('TestTable2', [DerivaColumn.define('Foo1', 'text')])
        table1.associate_tables(table2)
        assoc_table = catalog[schema_name]['TestTable1_TestTable2']
        self.assertTrue(assoc_table.is_pure_binary())
        assoc_table.associated_tables()
        generate_test_tables(catalog, schema_name)
        self.assertFalse(catalog['TestSchema']['Table2'].is_pure_binary())

    def test_create_asset_table(self):
        table = catalog[schema_name].create_table('TestTable1', [DerivaColumn.define('Foo1a', 'text')])
        table.create_asset_table('Foo1a', set_policy=False)
