from keycloak_config.encryption import EncryptionHelper

import mock
import unittest


class EncryptionHelperTests(unittest.TestCase):

    def setUp(self):
        self.encryption_prefix = "decrypt:"
        self.aws_profile = "saml"
        self.encryption_helper = EncryptionHelper(self.encryption_prefix, self.aws_profile)

    @mock.patch('keycloak_config.encryption.kmsdecrypt')
    def test_empty_input(self, decrypt):
        inputs = [
            None,
            "",
            {},
            []
        ]

        for input in inputs:
            output = self.encryption_helper.decrypt(input)
            decrypt.assert_not_called()
            self.assertEqual(input, output, "The actual output dict didn't match the expected one.")

    @mock.patch('keycloak_config.encryption.kmsdecrypt')
    def test_nothing_to_decrypt(self, decrypt):
        inputs = [
            {
                "no": "encrypted",
                "values": {
                    "this": "dict"
                }
            },
            1,
            "ABC",
            [1],
            [2, 3, "a"],
        ]

        for input in inputs:
            output = self.encryption_helper.decrypt(input)
            decrypt.assert_not_called()
            self.assertEqual(input, output, "The actual output dict didn't match the expected one.")

    @mock.patch('keycloak_config.encryption.kmsdecrypt')
    def test_decrypt_dictionaries(self, decrypt):
        decrypt.return_value = "valueXYZ"

        inputs = [
            {
                "key": "value",
                "key1": "decrypt:ASDF1234"
            },
            {
                "key": "value",
                "key1": {
                    "key2": "decrypt:ASDF1234",
                    "key3": 123
                }
            },
            {
                "key1": ["val2", "decrypt:ASDF1234", 123]
            }
        ]

        expected_outputs = [
            {
                "key": "value",
                "key1": "valueXYZ"
            },
            {
                "key": "value",
                "key1": {
                    "key2": "valueXYZ",
                    "key3": 123
                }
            },
            {
                "key1": ["val2", "valueXYZ", 123]
            }
        ]

        for input, expected_output in zip(inputs, expected_outputs):
            output = self.encryption_helper.decrypt(input)
            decrypt.assert_called_with(data='decrypt:ASDF1234', profile=self.aws_profile, prefix=self.encryption_prefix, env=None)
            self.assertDictEqual(expected_output, output, "The actual output dict didn't match the expected one.")

    @mock.patch('keycloak_config.encryption.kmsdecrypt')
    def test_decrypt_lists(self, decrypt):
        decrypt.return_value = "valueXYZ"

        inputs = [
            [["decrypt:ASDF1234"]],
            ["abc", "decrypt:ASDF1234", {}, {"key": [123, "decrypt:ASDF1234"]}]
        ]

        expected_outputs = [
            [["valueXYZ"]],
            ["abc", "valueXYZ", {}, {"key": [123, "valueXYZ"]}]
        ]

        for input, expected_output in zip(inputs, expected_outputs):
            output = self.encryption_helper.decrypt(input)
            decrypt.assert_called_with(data='decrypt:ASDF1234', profile=self.aws_profile, prefix=self.encryption_prefix, env=None)
            self.assertListEqual(expected_output, output, "The actual output list didn't match the expected one.")

    @mock.patch('keycloak_config.encryption.kmsdecrypt')
    def test_decrypt_string(self, decrypt):
        decrypt.return_value = "valueXYZ"

        output = self.encryption_helper.decrypt("decrypt:ASDF1234")
        self.assertEqual("valueXYZ", output)
