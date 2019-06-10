"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import unittest

from unittest.mock import Mock

from cortex.utils import decode_JWT
from cortex.exceptions import BadTokenException

from .fixtures import john_doe_token

class TestUtils(unittest.TestCase):
    # decode_JWT tests
    def test_can_decode_token(self):
        decodedJWT = decode_JWT(john_doe_token(), verify=False)
        self.assertEqual(
            decodedJWT,
            {
                "sub": "mliu",
                "tenant": "mliu",
                "name": "John Doe",
                "iat": 1516239022,
                "exp": 12312411251
            }
        )

    def test_empty_token_throws(self):
        with self.assertRaisesRegexp(BadTokenException, 'Your Cortex Token is invalid. For more information, go to Cortex Docs > Cortex Tools > Access'):
            decode_JWT('', verify=False)

    def test_nonsense_token_throws(self):
        with self.assertRaisesRegexp(BadTokenException, 'Your Cortex Token is invalid. For more information, go to Cortex Docs > Cortex Tools > Access'):
            decode_JWT('nonsensicaltoken', verify=False)

    def test_cortex_token_no_tenant_key_throws(self):
        """
        the token corresponds to below
            {
                "sub": "mliu",
                "name": "John Doe",
                "iat": 1516239022
            }
        """
        with self.assertRaisesRegexp(BadTokenException, 'Your Cortex Token is invalid. For more information, go to Cortex Docs > Cortex Tools > Access'):
            decode_JWT('eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtbGl1IiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.2ZfnDQtkCLzoAsF_7_2elRY7C05MAEc84Y5oY3WjVTsR9SJxnpWxLl5Ov3bb3JLD', verify=False)

    def test_cortex_token_no_cortex_keys_throws(self):
        """
        the token corresponds to below
            {
                "name": "John Doe",
                "iat": 1516239022
            }
        """
        with self.assertRaisesRegexp(BadTokenException, 'Your Cortex Token is invalid. For more information, go to Cortex Docs > Cortex Tools > Access'):
            decode_JWT('eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjJ9.jMgKlIcyp2pXyFgKHNVjtNrTXpNRBGqGCaVYDaps6qs7WM12G_HvjGXJ86rucMd_', verify=False)

    def test_cortex_token_expired_throws(self):
        """
        the token corresponds to below
            {
                "sub": "mliu",
                "tenant": "mliu",
                "exp": 459835561,
                "iat": 138625961
            }
        """
        with self.assertRaisesRegexp(BadTokenException, 'Your Cortex Token has expired. For more information, go to Cortex Docs > Cortex Tools > Access'):
            decode_JWT('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2duaXRpdmVzY2FsZS5jb20iLCJhdWQiOiJjb3J0ZXgiLCJzdWIiOiJjc2tpcnZpbiIsInRlbmFudCI6ImVkZ2VfdGVzdGVyIiwiYmVhcmVyIjoicHVibGljIiwia2V5IjoiVnBTMTNmNzYzVHBYUnFHbVVOU3htMFVxTFh5Q0czckMiLCJleHAiOjE1NTcxOTY2MTEsImFjbCI6eyIuKiI6WyJSRUFEIiwiUlVOIiwiV1JJVEUiLCJERUxFVEUiXX0sImlhdCI6MTU1NTk4NzAxMSwiZWRnZSI6dHJ1ZSwiZW52IjoiZGVmYXVsdC9lZGdlIn0.cfO_OcmZXYYbxTADL5JR9UdlB6WXpIRhFCx_NYo3664', verify=False)
