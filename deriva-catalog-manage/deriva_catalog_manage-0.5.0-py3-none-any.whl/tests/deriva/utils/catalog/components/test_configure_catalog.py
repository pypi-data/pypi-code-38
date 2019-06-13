import unittest
from unittest import TestCase
import logging

from deriva.core import get_credential, DerivaServer
import deriva.core.ermrest_model as em
from deriva.utils.catalog.components.configure_catalog import *
from deriva.utils.catalog.components.deriva_model import DerivaModel
from tests.deriva.utils.catalog.test_utils import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

server = 'dev.isrd.isi.edu'
schema_name = 'TestSchema'

def clean_schema(schema_name):
    with DerivaModel(catalog) as m:
        model = m.catalog_model()
        for t in model.schemas[schema_name].tables.values():
            for k in t.foreign_keys:
                k.delete(catalog.ermrest_catalog, t)
        for t in [i for i in model.schemas[schema_name].tables.values()]:
            t.delete(catalog.ermrest_catalog, model.schemas[schema_name])


def setUpModule():
    global catalog, catalog_id, ermrest_catalog

    credentials = get_credential(server)
    catalog = DerivaServer('https', server, credentials=credentials).create_ermrest_catalog()
    catalog_id = catalog._catalog_id
    logger.info('Catalog_id is {}'.format(catalog_id))

    catalog = DerivaCatalogConfigure(server, catalog_id=catalog_id)
    ermrest_catalog = catalog.ermrest_catalog
    with DerivaModel(catalog) as m:
        model = m.catalog_model()
        model.create_schema(catalog.ermrest_catalog, em.Schema.define(schema_name))


def tearDownModule():
    delete_catalog(ermrest_catalog)


class TestConfigureCatalog(TestCase):
    @classmethod
    def setUpClass(cls):
        global catalog
        clean_schema('TestSchema')

    def setUp(self):
        clean_schema(schema_name)
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

    @unittest.skip
    def test_catalog_defaults(self):
        catalog.configure_baseline_catalog(catalog_name='test', admin='isrd-systems')

    def test_table_defaults(self):
        catalog.configure_baseline_catalog(catalog_name='test',
                                           admin='isrd-systems',
                                           curator='isrd-systems',
                                           writer='isrd-systems',
                                           reader="*")
        catalog[schema_name]['TestTable1'].configure_table_defaults()
        print(catalog)
        self.assertEqual({s.name for s in catalog['public']},
                         {'ERMrest_Client', 'ERMrest_Group', 'Catalog_Group'})
        print(catalog['WWW'])
