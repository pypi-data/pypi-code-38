import unittest
import tempfile

import os

from datetime import datetime

from syncloudlib.json.convertible import from_json, to_json, read_json, write_json, to_dict, Field, List, pretty_print, ugly_print


class Klass:

    def __init__(self, member1, member2):
        self.member1 = member1
        self.member2 = member2

class KlassWithMeta:
    member1 = Field()

class KlassWithMetaParent:
    member1 = Field(field_type=KlassWithMeta)

class KlassWithMeta2:
    member1 = Field(default=True)

class TestDictionary(unittest.TestCase):

    def test_datetime_member(self):
        datetime_value = datetime(2014, 6, 28, hour=7, minute=58, second=59)
        obj = Klass("value1", datetime_value)
        d = to_dict(obj)
        self.assertEquals(datetime_value, d["member2"])


class TestJson(unittest.TestCase):

    def test_from_object_json(self):
        json_text = '{"member1": "value", "member2": 345}'
        actual = from_json(json_text)
        self.assertEquals("value", actual.member1)
        self.assertEquals(345, actual.member2)

    def test_from_nested_json(self):
        json_text = '{"member1": "value1", "member2": {"member1": 345, "member2": "value2"}}'
        actual = from_json(json_text)
        self.assertEquals("value1", actual.member1)
        self.assertEquals(345, actual.member2.member1)
        self.assertEquals("value2", actual.member2.member2)

    def test_from_nested_json_list(self):
        json_text = '{"member1": "value1", "member2": [{"member1": 345, "member2": "value2"}]}'
        actual = from_json(json_text)
        self.assertEquals("value1", actual.member1)
        self.assertEquals(1, len(actual.member2))
        self.assertEquals(345, actual.member2[0].member1)
        self.assertEquals("value2", actual.member2[0].member2)

    def test_from_list_json(self):
        json_text = '[{"member1": "value1", "member2": 123}, {"member1": "value2", "member2": 345}]'
        actual = from_json(json_text)
        self.assertEquals(2, len(actual))
        self.assertEquals("value1", actual[0].member1)
        self.assertEquals(123, actual[0].member2)
        self.assertEquals("value2", actual[1].member1)
        self.assertEquals(345, actual[1].member2)

    def test_object_to_json(self):
        obj = Klass("value", 345)
        actual = to_json(obj)
        expected = '{"member1": "value", "member2": 345}'
        self.assertEquals(expected, actual)

    def test_nested_to_json(self):
        obj = Klass(True, Klass("value", 345))
        actual = to_json(obj)
        expected = '{"member1": true, "member2": {"member1": "value", "member2": 345}}'
        self.assertEquals(expected, actual)

    def test_list_to_json(self):
        objects_list = [Klass("value1", 123), Klass("value2", 345)]
        actual = to_json(objects_list)
        expected = '[{"member1": "value1", "member2": 123}, {"member1": "value2", "member2": 345}]'
        self.assertEquals(expected, actual)

    def test_dictionary_to_json(self):
        objects_dict = {"obj1": Klass("value1", 123), "obj2": Klass("value2", 345)}
        actual = to_json(objects_dict)
        expected = '{"obj1": {"member1": "value1", "member2": 123}, "obj2": {"member1": "value2", "member2": 345}}'
        self.assertEquals(expected, actual)

    def test_datetime_to_json(self):
        datetime_value = datetime(2014, 6, 28, hour=7, minute=58, second=59)
        obj = Klass("value1", datetime_value)
        actual = to_json(obj)
        expected = '{"member1": "value1", "member2": "2014-06-28 07:58:59"}'
        self.assertEquals(expected, actual)

    def test_dictionary_to_json_pretty_rpint(self):
        pretty_print()
        objects_dict = {"key1": "value1", "key2": "value2"}
        actual = to_json(objects_dict)
        lines = actual.split('\n')
        ugly_print()
        self.assertEquals(4, len(lines), msg='Pretty printed json should have multiple lines')


class TestJsonFile(unittest.TestCase):

    def temp_text(self, text=''):
        fd, filename = tempfile.mkstemp()
        f = os.fdopen(fd, 'w')
        f.write(text)
        f.close()
        return filename

    def test_read_file(self):
        filename = self.temp_text('{"member1": "value", "member2": 345}')

        actual = read_json(filename)
        self.assertEquals("value", actual.member1)
        self.assertEquals(345, actual.member2)

    def test_write_file(self):
        filename = self.temp_text()

        obj = Klass("value", 345)
        write_json(filename, obj)

        actual = read_json(filename)
        self.assertEquals("value", actual.member1)
        self.assertEquals(345, actual.member2)

    def test_from_non_existing_file(self):
        filename = self.temp_text('{"member1": "value", "member2": 345}')
        os.remove(filename)
        actual = read_json(filename)
        self.assertIsNone(actual)

    def test_from_empty_file(self):
        filename = self.temp_text()
        actual = read_json(filename)
        self.assertIsNone(actual)

    def test_from_new_lines_and_spaces(self):
        filename = self.temp_text(' \n \n  \n')
        actual = read_json(filename)
        self.assertIsNone(actual)

    def test_None_to_json(self):
        filename = self.temp_text()

        write_json(filename, None)

        actual = read_json(filename)
        self.assertIsNone(actual)

class TestToTyped(unittest.TestCase):

    def test_simple(self):
        json_text = '{"member1": 345}'
        actual = from_json(json_text, KlassWithMeta)
        self.assertTrue(isinstance(actual, KlassWithMeta))
        self.assertEquals(345, actual.member1)

    def test_list(self):
        json_text = '[{"member1": 345}]'
        actual = from_json(json_text, List(KlassWithMeta))
        self.assertEquals(1, len(actual))
        self.assertTrue(isinstance(actual[0], KlassWithMeta))
        self.assertEquals(345, actual[0].member1)

    def test_default(self):
        json_text = '{}'
        actual = from_json(json_text, KlassWithMeta2)
        self.assertTrue(isinstance(actual, KlassWithMeta2))
        self.assertEquals(True, actual.member1)

    def test_nested(self):
        json_text = '{"member1": {"member1": 345}}'
        actual = from_json(json_text, KlassWithMetaParent)
        self.assertTrue(isinstance(actual, KlassWithMetaParent))
        self.assertTrue(isinstance(actual.member1, KlassWithMeta))
        self.assertEquals(345, actual.member1.member1)

    def test_array_inside_array(self):
        json_text = '''{ "param": [ { "messages": [ "123" ] } ] }'''
        actual = from_json(json_text)
        self.assertEquals(1, len(actual.param))
        self.assertEquals(1, len(actual.param[0].messages))
        self.assertEquals('123', actual.param[0].messages[0])
