from unittest import TestCase
import tempfile
import sys
import deriva.core.ermrest_model as em
from deriva.utils.catalog.manage.utils import TempErmrestCatalog, load_module_from_path
from deriva.core import get_credential
from deriva.core.ermrest_config import tag as chaise_tags
from deriva.utils.catalog.manage.dump_catalog import DerivaCatalogToString

from urllib.parse import urlparse


from tests.deriva.utils.catalog.test_utils import *


class TestDerivaCatalogToString(TestCase):
    def setUp(self):
        self.server = 'dev.isrd.isi.edu'
        self.credentials = get_credential(self.server)

    def test_substitute_variables(self):
        pass

    def test_variable_to_str(self):
        pass

    def test_tag_variables_to_str(self):
        pass

    def test_annotations_to_str(self):
        pass

    def test_schema_to_str(self):
        catalog = create_catalog(self.server)
        try:
            catalog.create_schema('TestSchema')
            generate_test_tables(catalog, 'TestSchema')

            stringer = DerivaCatalogToString(catalog)
            schema_string = stringer.schema_to_str('TestSchema')
            tdir = tempfile.mkdtemp()
            modfile = '{}/TestSchema.py'.format(tdir)
            with open(modfile, mode='w') as f:
                print(schema_string, file=f)
            m = load_module_from_path(modfile)

            test_catalog = create_catalog(self.server)
            m.main(test_catalog, 'schema')
            m.main(test_catalog, 'annotations')
            m.main(test_catalog, 'acls')
            m.main(test_catalog, 'comment')
        finally:
            delete_catalog(catalog.ermrest_catalog)

    def test_catalog_to_str(self):
        catalog = create_catalog(self.server)
        try:
            catalog.create_schema('TestSchema')

            stringer = DerivaCatalogToString(catalog)
            catalog_string = stringer.catalog_to_str()
            tdir = tempfile.mkdtemp()
            modfile = '{}/TestCatalog.py'.format(tdir)
            with open(modfile, mode='w') as f:
                print(catalog_string, file=f)
            m = load_module_from_path(modfile)

            test_catalog = create_catalog(self.server)
            m.main(test_catalog, 'annotations')
        finally:
            delete_catalog(catalog.ermrest_catalog)

    def test_table_annotations_to_str(self):
        pass

    def test_column_annotations_to_str(self):
        pass

    def test_foreign_key_defs_to_str(self):
        pass

    def test_key_defs_to_str(self):
        pass

    def test_column_defs_to_str(self):
        pass

    def test_table_def_to_str(self):
        pass

    def test_table_to_str(self):
        catalog = create_catalog(self.server)
        try:
            catalog.create_schema('TestSchema')
            generate_test_tables(catalog, 'TestSchema')

            stringer = DerivaCatalogToString(catalog)
            table_string = stringer.table_to_str('TestSchema','Table1')
            tdir = tempfile.mkdtemp()
            modfile = '{}/TestTable.py'.format(tdir)
            with open(modfile, mode='w') as f:
                print(table_string, file=f)
            m = load_module_from_path(modfile)

            test_catalog = create_catalog(self.server)
            test_catalog.create_schema('TestSchema')
            m.main(test_catalog, 'table')
            m.main(test_catalog, 'annotations')
            m.main(test_catalog, 'acls')
            m.main(test_catalog, 'comment')
            m.main(test_catalog, 'keys')
            m.main(test_catalog, 'fkeys')
    #        m.main(test_catalog, 'columns', replace=True, really=True)
        finally:
            delete_catalog(catalog.ermrest_catalog)
