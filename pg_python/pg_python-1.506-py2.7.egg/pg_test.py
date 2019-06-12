from . import pg_python
import unittest
import logging
import requests

COL_1 = "col1"
COL_2 = "col2"
COL_3 = "col3"
COL_4 = "col4"
COL_5 = "int_value"
UPDATE = "update"
test_table = "pg_python_test"


class TestTests(unittest.TestCase):
    """
    Please run the following in your local database before running the test cases:
    1. A user postgres is required to be present with password "@pgtest"
    2. create database test_db;
    3. create table pg_python_test (col1 text, col2 text, col3 int, col4 text, int_value int)
    """
    def setUp(self):
        pg_python.pg_server("test_db", "postgres", "@pgtest", "localhost", False)

    def test_read_raw(self):
        create_rows()
        title1 = pg_python.read_raw("select col1,col3 from "+test_table+" where col2=%s",('read',))
        self.assertEqual(title1[0][0],"title1")
        self.assertEqual(title1[0][1], 76)
        print("Read raw done")
        clear_table()

    def test_write_raw(self):
        create_rows()
        values = ['title7','read7',77]
        pg_python.write_raw("insert into "+test_table+" values (%s,%s,%s)",values)
        title1 = pg_python.read(test_table,[COL_2,COL_3],{COL_1:'title7'})
        self.assertEqual(title1[0][COL_2], "read7")
        self.assertEqual(title1[0][COL_3], "77")
        print("Write raw done")
        clear_table()

    def test_update(self):
        create_rows()
        pg_python.update(test_table,{COL_4:'updated_name1'},{COL_1:'title1%'},clause='ilike')
        title1 = pg_python.read(test_table,[COL_4],{COL_1:'title15'})
        self.assertEqual(title1[0][COL_4],'updated_name1')
        print("Update single row done")
        clear_table()

    def test_multiple_update(self):
        create_rows()
        dict_lst =[
            {COL_1:'title1', UPDATE:'updated_name1'},
            {COL_1: 'title2', UPDATE: "update'd_name2"}
        ]
        pg_python.update_multiple(test_table,COL_4,[COL_1],dict_lst)
        title1 = pg_python.read(test_table,[COL_4],{COL_1:'title1'})
        title2 = pg_python.read(test_table, [COL_4], {COL_1: 'title2'})
        self.assertEqual(title1[0][COL_4],'updated_name1')
        self.assertEqual(title2[0][COL_4], "update'd_name2")
        print("Update multiple done")
        clear_table()

    def test_multiple_insert(self):
        column_to_insert = [COL_1, COL_3]
        insert_dict_list = [
            {COL_1: "insert1", COL_3: 1},
            {COL_3: 2, COL_1: "insert2"},
            {COL_1: "insert3", COL_3: 3}
        ]
        pg_python.insert_multiple(test_table,column_to_insert,insert_dict_list)
        val1 = pg_python.read(test_table,[COL_1],{COL_3:1})
        val2 = pg_python.read(test_table, [COL_1], {COL_3: 2})
        val3 = pg_python.read(test_table, [COL_1], {COL_3: 3})
        values = [val1[0][COL_1],val2[0][COL_1],val3[0][COL_1] ]
        self.assertEqual(values,["insert1","insert2","insert3"])
        print("Insert multiple done")
        clear_table()

    def test_update_raw(self):
        create_rows()
        updates = pg_python.update_raw("update "+ test_table + " set " + COL_4 + "= 'updated_name1' where " + COL_1 + " ilike 'title1%'" )
        title1 = pg_python.read(test_table, [COL_4], {COL_1: 'title15'})
        self.assertEqual(title1[0][COL_4], 'updated_name1')
        self.assertEqual(updates, 2)
        print("Update raw done")
        clear_table()

    def test_read_in(self):
        create_rows()
        values = ['title15','title1','title2','title3']
        rows = pg_python.read(test_table, [COL_1], {COL_1: values}, clause=" in ")
        read_values = []
        for row in rows:
            read_values.append(row.get(COL_1))
        self.assertEqual(sorted(read_values), sorted(values))
        print("Read in done")
        clear_table()

    def test_read_simple(self):
        create_rows()
        rows = pg_python.read(test_table, [COL_1], {COL_2: 'read'})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][COL_1], 'title1')
        print("Read simple done")
        clear_table()

    def test_read_greater_than(self):
        create_rows()
        rows = pg_python.read(test_table, [COL_1], {COL_5 + " >": 10})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][COL_1], 'title6')
        print("Read greater than done")
        clear_table()

    def test_delete(self):
        create_rows()
        where_kv_map={COL_1:'title15'}
        pg_python.delete(test_table, where_kv_map)
        read=pg_python.read(test_table,[COL_2], {COL_1:'title15'})
        self.assertEqual(read,[])
        print("Delete row done")
        clear_table()

class UpdateTests(unittest.TestCase):
    def setUp(self):
        pg_python.pg_server("test_db", "postgres", "@pgtest", "localhost", False)

    def test_update_multicol(self):
        create_rows()
        cols_to_update = [COL_2, COL_3]
        dict_lst =[
            {'where':{COL_1:'title1'}, UPDATE:{COL_2 : 'updated_col2a', COL_3:33}},
             {'where':{COL_1:'title2'}, UPDATE:{COL_2 : 'updated_col2b', COL_3:34}
            }
        ]
        pg_python.update_multiple_col(test_table,cols_to_update,[COL_1],dict_lst)
        title1 = pg_python.read(test_table,[COL_2, COL_3],{COL_1:'title1'})
        title2 = pg_python.read(test_table, [COL_2, COL_3], {COL_1: 'title2'})
        self.assertEqual(title1[0][COL_2],'updated_col2a')
        self.assertEqual(title1[0][COL_3], '33')
        self.assertEqual(title2[0][COL_2], 'updated_col2b')
        self.assertEqual(title2[0][COL_3], '34')
        print("Update multiple row multiple column done")
        clear_table()

    def test_update_multicol_2testcond(self):
        create_rows()
        cols_to_query = [COL_1, COL_3]
        cols_to_update = [COL_2]
        dict_lst =[
            {'where':{COL_1:'title1', COL_3:76}, UPDATE:{COL_2 : 'updated_col2a'}}
        ]
        num = pg_python.update_multiple_col(test_table,cols_to_update,cols_to_query,dict_lst)
        self.assertEqual(num['updated_records'], 1)
        title1 = pg_python.read(test_table,[COL_2],{COL_1:'title1'})

        self.assertEqual(title1[0][COL_2],'updated_col2a')
        print("Update multiple row multiple column with two test conditions done")
        clear_table()

def create_rows():
    pg_python.write(test_table, {COL_1: "title1", COL_2: "read", COL_3: 76, COL_4: "reeer"})
    pg_python.write(test_table, {COL_1: "title2", COL_2: "read2", COL_3: 77, COL_4: "reeer"})
    pg_python.write(test_table, {COL_1: "title3", COL_2: "read3", COL_3: 77, COL_4: "reeer"})
    pg_python.write(test_table, {COL_1: "title4", COL_2: "read4", COL_3: 77, COL_4: "reeer"})
    pg_python.write(test_table, {COL_1: "title15", COL_2: "read5", COL_3: 77, COL_4: "reeer"})
    pg_python.write(test_table, {COL_1: "title6", COL_2: "read6", COL_3: 77, COL_4: "reeer", COL_5: 20})

def clear_table():
    pg_python.write_raw("Delete from %s"%(test_table), None)
