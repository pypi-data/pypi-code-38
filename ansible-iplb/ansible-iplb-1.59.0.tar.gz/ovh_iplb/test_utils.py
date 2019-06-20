import unittest
from ovh_iplb import utils


class TestUtil(unittest.TestCase):

    def test_convert_to_str_if_unicode(self):
        self.assertEquals(utils.convert_to_str_if_unicode(u'u'), 'u')

    def test_do_not_convert_for_str(self):
        self.assertEquals(utils.convert_to_str_if_unicode('u'), 'u')

    def test_do_not_fail_for_none(self):
        self.assertEquals(utils.convert_to_str_if_unicode(None), None)

    def test_do_not_fail_for_int(self):
        self.assertEquals(utils.convert_to_str_if_unicode(42), 42)

    def test_clean_unicode_of_dict_for_empty_dict(self):
        self.assertEquals(utils.clean_unicode_of_dict({}), {})

    def test_clean_unicode_of_dict_for_not_empty_dict(self):
        self.assertEquals(utils.clean_unicode_of_dict({
            u'key': u'val',
            2: 3
        }), {
            'key': 'val',
            2: 3
        })

    def test_is_int_repr_or_int_on_int_string(self):
        self.assertTrue(utils.is_int_repr_or_int('42'))

    def test_is_int_repr_or_int_on_int(self):
        self.assertTrue(utils.is_int_repr_or_int(42))

    def test_is_int_repr_or_int_on_non_int_string(self):
        self.assertFalse(utils.is_int_repr_or_int('toto'))

    def test_build_path_with_integer(self):
        self.assertEqual('/42/farm', utils.build_path(42, 'farm'))

    def test_build_path_with_no_argument(self):
        self.assertEqual('/', utils.build_path())

    def test_build_path_with_slash(self):
        self.assertEqual('/the/cat/is/sleeping', utils.build_path('the', 'cat/', '/is', '/sleeping/'))

    def test_to_camel_case(self):
        self.assertEqual(utils.to_camel_case('vrack_network_id'), 'vrackNetworkId')

    def test_convert_key_to_camel_case(self):
        self.assertEqual(utils.convert_key_to_camel_case({
            'vrack_network_id': 42,
            'probe': {
                'force_ssl': {
                    'type_of_field': 'boolean'
                }
            },
            'list_of_element': [{
                'vrack_network_id': 'id'
            }]
        }), {
            'vrackNetworkId': 42,
            'probe': {
                'forceSsl': {
                    'typeOfField': 'boolean'
                }
            },
            'listOfElement': [{
                'vrackNetworkId': 'id'
            }]
        })


if __name__ == '__main__':
    unittest.main()
