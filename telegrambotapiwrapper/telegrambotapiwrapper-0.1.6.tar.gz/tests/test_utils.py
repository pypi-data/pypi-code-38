import unittest
from pprint import pprint

from telegrambotapiwrapper.utils import is_str_int_float_bool
from telegrambotapiwrapper.utils import is_ends_with_underscore
from telegrambotapiwrapper.utils import replace_from_word
from telegrambotapiwrapper.utils import replace_from__word


class TestUtils(unittest.TestCase):
    def test_is_str_int_float_bool(self):
        self.assertTrue(is_str_int_float_bool("assaads"))
        self.assertTrue(is_str_int_float_bool(123))
        self.assertTrue(is_str_int_float_bool(23432.45435))
        self.assertTrue(is_str_int_float_bool(True))

        class A:
            pass

        self.assertFalse(is_str_int_float_bool(A()))

    def test_is_ends_with_underscore(self):
        self.assertTrue(is_ends_with_underscore("asedsaads_"))
        self.assertTrue(is_ends_with_underscore("_aessaads_"))
        self.assertFalse(is_ends_with_underscore("_aseswsdwc"))
        self.assertFalse(is_ends_with_underscore(""))

    def test_replace_from_word(self):
        """from -> from_"""
        without_from_ = {
            'chat': {
                'all_members_are_administrators': True,
                'first_name': 'regfrefre',
                'id': 1234,
                'pinned_message': {
                    'chat': {
                        'id': 12344332534,
                        'title': 'fjhdkjfhskdlhsj',
                        'type': 'sddsfdsf',
                        'from': False
                    },
                    'date': 12435324,
                    'message_id': 123214234
                },
                'title': 'fvgfgfd',
                'type': 'sdfdsfds',
                'username': 'regfrefre'
            },
            'date': 4584979847685478,
            'from': {
                'first_name': '23fdvfvdsc',
                'id': 1232343,
                'is_bot': False,
                'last_name': 'gjfdkjglkfjglkjf'
            },
            'message_id': 12312321
        }


        res = replace_from_word(without_from_)
        self.assertIn("from_", res['chat']['pinned_message']['chat'])
        self.assertNotIn("from", res['chat']['pinned_message']['chat'])
        self.assertIn("from_", res)
        self.assertNotIn("from", res)


    def test_replace_from__word(self):
        """from_ -> from"""

        with_from_ = {
            'chat': {
                'all_members_are_administrators': True,
                'first_name': 'regfrefre',
                'id': 1234,
                'pinned_message': {
                    'chat': {
                        'id': 12344332534,
                        'title': 'fjhdkjfhskdlhsj',
                        'type': 'sddsfdsf',
                        'from_': False
                    },
                    'date': 12435324,
                    'message_id': 123214234
                },
                'title': 'fvgfgfd',
                'type': 'sdfdsfds',
                'username': 'regfrefre'
            },
            'date': 4584979847685478,
            'from_': {
                'first_name': '23fdvfvdsc',
                'id': 1232343,
                'is_bot': False,
                'last_name': 'gjfdkjglkfjglkjf'
            },
            'message_id': 12312321
        }

        res = replace_from__word(with_from_)
        self.assertIn("from", res['chat']['pinned_message']['chat'])
        self.assertNotIn("from_", res['chat']['pinned_message']['chat'])
        self.assertIn("from", res)
        self.assertNotIn("from_", res)

