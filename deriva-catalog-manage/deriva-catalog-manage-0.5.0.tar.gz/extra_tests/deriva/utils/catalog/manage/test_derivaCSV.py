from unittest import TestCase
import datetime
import os
import csv
import sys
import string
import tempfile
import random
import logging

from tableschema import exceptions
from deriva.utils.catalog.manage.utils import load_module_from_path
from deriva.utils.catalog.manage.deriva_csv import DerivaCSV
import deriva.utils.catalog.manage.dump_catalog as dump_catalog
import deriva.core.ermrest_model as em
from tests.deriva.utils.catalog.test_utils import *

logger = logging.getLogger(__name__)


class TestDerivaCSV(TestCase):
    def setUp(self):
        self.server = 'dev.isrd.isi.edu'
        self.catalog_id = None
        self.schema_name = 'TestSchema'
        self.table_name = 'TestTable'

        self.configfile = os.path.dirname(os.path.realpath(__file__)) + '/config.py'

        self.catalog = create_catalog(self.server)
        self.catalog.create_schema(self.schema_name)

        self.table_size = 1000
        self.column_count = 20
        self.test_dir = tempfile.mkdtemp()

        (row, self.headers) = generate_test_csv(self.column_count)

        self.tablefile = '{}/{}.csv'.format(self.test_dir, self.table_name)
        with open(self.tablefile, 'w', newline='') as f:
            tablewriter = csv.writer(f)
            for i, j in zip(range(self.table_size + 1), row):
                tablewriter.writerow(j)

    def tearDown(self):
        delete_catalog(self.catalog.ermrest_catalog)

    def _create_test_table(self):
        pyfile = '{}/{}.py'.format(self.test_dir, self.table_name)
        try:
            self.table.convert_to_deriva(outfile=pyfile)
            tablescript = load_module_from_path(pyfile)
            tablescript.main(self.catalog, 'table')
        except ValueError as e:
            print(e)

    def test_map_name(self):
        path = os.path.dirname(os.path.realpath(__file__))

        column_map = None
        table = DerivaCSV(path + '/test1.csv', self.schema_name, column_map=column_map)
        self.assertEqual(table.map_name('foo bar'), 'foo bar')

        column_map = False
        table = DerivaCSV(path + '/test1.csv', self.schema_name, column_map=column_map)
        self.assertEqual(table.map_name('foo bar'), 'foo bar')

        column_map = True
        table = DerivaCSV(path + '/test1.csv', self.schema_name, column_map=column_map)
        self.assertEqual(table.map_name('foo bar'), 'Foo_Bar')

        column_map = ['DNA', 'RNA']
        table = DerivaCSV(path + '/test1.csv', self.schema_name, column_map=column_map)
        self.assertEqual(table.map_name('foo bar'), 'Foo_Bar')

        column_map = {'(%)': '(Percent)', 'RnA': 'RNA', 'dna': 'DNA',
                      'the hun': 'Attila_The_Hun', 'the_clown': 'Bozo_The_Clown'}
        table = DerivaCSV(path + '/test1.csv', self.schema_name, column_map=column_map)
        self.assertEqual(table.map_name('Change in value (%)'), 'Change_In_Value_(Percent)')
        self.assertEqual(table.map_name('amountDna'), 'Amount_DNA')
        self.assertEqual(table.map_name('the hun'), 'Attila_The_Hun')
        self.assertEqual(table.map_name('the clown'), 'Bozo_The_Clown')

    def test_convert_to_deriva(self):
        self.table = DerivaCSV(self.tablefile, self.schema_name, key_columns='id', column_map=True)
        self._create_test_table()
        tname = self.table.map_name(self.table_name)

    def test_compound_key(self):
        key_columns = [['id', 'field 1', 'field 2'], 'field 3', ['field 4', 'field 5']]
        self.table = DerivaCSV(self.tablefile, self.schema_name, key_columns=key_columns, column_map=True)
        self.assertEqual(self.table.schema.primary_key,['id', 'field 1', 'field 2'])

        for h in self.table.headers:
            f = self.table.schema.get_field(h)
            self.assertEqual((h in ['id', 'field 1', 'field 2', 'field 3', 'field 4', 'field 5'] and f.required) or
                                not f.required, True, msg='Missing required in field {}'.format(h))
            self.assertEqual((h == 'field 3' and f.descriptor.get('unique', False)) or not \
                            f.descriptor.get('unique', False), True)

        self._create_test_table()

        target_table = self.catalog[self.schema_name][self.table.map_name(self.table_name)]

        catalog_keys = [ sorted([c.name for c in i.columns]) for i in target_table.keys]

        # Check to make sure that each key is set for no nulls...
        for k in self.table._key_columns:
            for col in k:
                self.assertEqual(target_table.columns[self.table.map_name(col)].nullok, False,
                                 msg='nullok not set for {}'.format(col))
            n = [self.table.map_name(i) for i in k]
            n.sort()
            self.assertEqual(n in catalog_keys,True, msg = 'Key missing {}'.format(k))
        # Now check to make sure the key constraints made it....
        for k in target_table.keys:
            print(k.columns)

        return

    def test_table_schema_from_catalog(self):
        self.table = DerivaCSV(self.tablefile, self.schema_name, key_columns='id', column_map=True)
        self._create_test_table()

        tableschema = self.table.table_schema_from_catalog(self.catalog)

        self.assertEqual([self.table.map_name(i['name']) for i in self.table.schema.descriptor['fields']],
                         [i['name'] for i in tableschema.descriptor['fields']])
        self.assertEqual([i['type'] for i in self.table.schema.descriptor['fields']],
                         [i['type'] for i in tableschema.descriptor['fields']])

    def test_table_schema_from_catalog_compound(self):
        self.table = DerivaCSV(self.tablefile, self.schema_name, key_columns=[['id','field 1']], column_map=True)
        self._create_test_table()

        tableschema = self.table.table_schema_from_catalog(self.catalog)

        self.assertEqual([self.table.map_name(i['name']) for i in self.table.schema.descriptor['fields']],
                         [i['name'] for i in tableschema.descriptor['fields']])
        self.assertEqual([i['type'] for i in self.table.schema.descriptor['fields']],
                         [i['type'] for i in tableschema.descriptor['fields']])
        print(tableschema.primary_key)
        self.assertEqual(set(tableschema.primary_key), {'Id', 'Field_1'})

    def test_validate(self):
        self.table = DerivaCSV(self.tablefile, self.schema_name, key_columns='id', column_map=True)
        self._create_test_table()
        self.table.validate(self.catalog)

    def test_upload_to_deriva(self):
        self.table = DerivaCSV(self.tablefile, self.schema_name, key_columns='id', column_map=True)
        self._create_test_table()
        row_count, _ = self.table.upload_to_deriva(self.catalog)
        self.assertEqual(row_count, self.table_size)

        pb = self.catalog.getPathBuilder()
        target_table = pb.schemas[self.schema_name].tables[self.table.map_name(self.table_name)].alias('target_table')
        e = target_table.entities()
        edict = {i['Id']: i for i in e}
        source = self.table.read(keyed=True)
        i = 0
        for k, v in source[i].items():
            id = source[i]['id']
            print(k, edict[id][self.table.map_name(k)], v)

    def test_upload_to_deriva_partial(self):
        self.table = DerivaCSV(self.tablefile, self.schema_name, key_columns='id', column_map=True)
        self._create_test_table()

        # get part of table:
        pfile_name = '{}/{}_partial.csv'.format(self.test_dir, self.table_name)

        with open(self.tablefile, 'r') as wholefile:
            with open(pfile_name, 'w', newline='') as partfile:
                tablereader = csv.reader(wholefile)
                tablewriter = csv.writer(partfile)
                for i in range(self.table_size // 2):
                    tablewriter.writerow(next(tablereader))

        partial_table = DerivaCSV(pfile_name, self.schema_name, table_name=self.table_name, key_columns='id',
                                  column_map=True)
        partial_row_count, _ = partial_table.upload_to_deriva(self.catalog)
        self.assertEqual(partial_row_count, self.table_size // 2 - 1)

        row_count, _ = self.table.upload_to_deriva(self.catalog)

        self.assertEqual(row_count, self.table_size - (self.table_size // 2 - 1))

        pb = self.catalog.getPathBuilder()
        target_table = pb.schemas[self.schema_name].tables[self.table.map_name(self.table_name)].alias('target_table')
        self.assertEqual(len(list(target_table.entities())), self.table_size)

    def test_upload_to_deriva_upload_id(self):
        self.table = DerivaCSV(self.tablefile, self.schema_name, column_map=True, row_number_as_key=True)
        self._create_test_table()
        row_count, upload_id = self.table.upload_to_deriva(self.catalog)
        print(row_count, upload_id)
        self.assertEqual(row_count, self.table_size)

    def test_upload_to_deriva_validate(self):
        self.table = DerivaCSV(self.tablefile, self.schema_name, column_map=True, key_columns='id')
        self._create_test_table()
        valid, report = self.table.validate(self.catalog)
        if not valid:
            for i in report['tables'][0]['errors']:
                print(i)
        self.assertEqual(valid, True)

    def test_upload_to_deriva_validate_id(self):
        self.table = DerivaCSV(self.tablefile, self.schema_name, column_map=True, row_number_as_key=True)
        self._create_test_table()
        try:
            valid, report = self.table.validate(self.catalog)
        except exceptions.ValidationError as err:
            print(err.errors)
        if not valid:
            for i in report['tables'][0]['errors']:
                print(i)
        self.assertEqual(valid, True)

    def test_upload_to_deriva_partial_id(self):
        # get part of table:
        pfile_name = '{}/{}_partial.csv'.format(self.test_dir, self.table_name)

        with open(self.tablefile, 'r') as wholefile:
            with open(pfile_name, 'w', newline='') as partfile:
                tablereader = csv.reader(wholefile)
                tablewriter = csv.writer(partfile)
                for i in range(self.table_size // 2):
                    tablewriter.writerow(next(tablereader))

        self.table = DerivaCSV(self.tablefile, self.schema_name, table_name=self.table_name,
                               row_number_as_key=True, column_map=True)
        partial_table = DerivaCSV(pfile_name, self.schema_name, table_name=self.table_name,
                                  row_number_as_key=True, column_map=True)
        self._create_test_table()

        # Upload first half...
        partial_row_count, partial_upload_id = partial_table.upload_to_deriva(self.catalog)
        self.assertEqual(partial_row_count, self.table_size // 2 - 1)

        # Upload second half....
        row_count, upload_id_1 = self.table.upload_to_deriva(self.catalog, upload_id=partial_upload_id)
        self.assertEqual(row_count, self.table_size - (self.table_size // 2 - 1))

        # Check to see if whole table is there.
        pb = self.catalog.getPathBuilder()
        target_table = pb.schemas[self.schema_name].tables[self.table.map_name(self.table_name)].alias('target_table')
        self.assertEqual(len(list(target_table.entities())), self.table_size)

        # Upload table again, using new upload_id.
        logger.info('Upload table again....')
        row_count, upload_id_1 = self.table.upload_to_deriva(self.catalog)
        self.assertEqual(row_count, self.table_size)

        target_table = pb.schemas[self.schema_name].tables[self.table.map_name(self.table_name)].alias('target_table')
        self.assertEqual(len(list(target_table.entities())), 2 * self.table_size)

