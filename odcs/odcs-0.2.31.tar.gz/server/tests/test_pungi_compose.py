# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>

import six
import unittest
from mock import patch

from odcs.server.pungi_compose import PungiCompose


RPMS_JSON = {
    "header": {
        "type": "productmd.rpms",
        "version": "1.2"
    },
    "payload": {
        "compose": {
            "date": "20181210",
            "id": "odcs-691-1-20181210.n.0",
            "respin": 0,
            "type": "nightly"
        },
        "rpms": {
            "Temporary": {
                "x86_64": {
                    "flatpak-rpm-macros-0:29-6.module+125+c4f5c7f2.src": {
                        "flatpak-rpm-macros-0:29-6.module+125+c4f5c7f2.src": {
                            "category": "source",
                            "path": "Temporary/source/tree/Packages/f/flatpak-rpm-macros-29-6.module+125+c4f5c7f2.src.rpm",
                            "sigkey": None
                        },
                        "flatpak-rpm-macros-0:29-6.module+125+c4f5c7f2.x86_64": {
                            "category": "binary",
                            "path": "Temporary/x86_64/os/Packages/f/flatpak-rpm-macros-29-6.module+125+c4f5c7f2.x86_64.rpm",
                            "sigkey": None
                        }
                    },
                    "flatpak-runtime-config-0:29-4.module+125+c4f5c7f2.src": {
                        "flatpak-runtime-config-0:29-4.module+125+c4f5c7f2.src": {
                            "category": "source",
                            "path": "Temporary/source/tree/Packages/f/flatpak-runtime-config-29-4.module+125+c4f5c7f2.src.rpm",
                            "sigkey": "sigkey1"
                        },
                        "flatpak-runtime-config-0:29-4.module+125+c4f5c7f2.x86_64": {
                            "category": "binary",
                            "path": "Temporary/x86_64/os/Packages/f/flatpak-runtime-config-29-4.module+125+c4f5c7f2.x86_64.rpm",
                            "sigkey": "sigkey1"
                        }
                    }
                }
            }
        }
    }
}


@patch("odcs.server.pungi_compose.PungiCompose._fetch_json")
class TestPungiCompose(unittest.TestCase):

    def test_get_rpms_data(self, fetch_json):
        fetch_json.return_value = RPMS_JSON
        compose = PungiCompose("http://localhost/compose/Temporary")
        data = compose.get_rpms_data()

        expected = {
            'sigkeys': set(['sigkey1', None]),
            'arches': set(['x86_64']),
            'builds': {
                'flatpak-rpm-macros-29-6.module+125+c4f5c7f2': set([
                    'flatpak-rpm-macros-0:29-6.module+125+c4f5c7f2.src',
                    'flatpak-rpm-macros-0:29-6.module+125+c4f5c7f2.x86_64']),
                'flatpak-runtime-config-29-4.module+125+c4f5c7f2': set([
                    'flatpak-runtime-config-0:29-4.module+125+c4f5c7f2.src',
                    'flatpak-runtime-config-0:29-4.module+125+c4f5c7f2.x86_64'])
            }
        }

        self.assertEqual(data, expected)

    def test_get_rpms_data_unknown_variant(self, fetch_json):
        fetch_json.return_value = RPMS_JSON
        msg = ("The http://localhost/compose/metadata/rpms.json does not "
               "contain payload -> rpms -> Workstation section")
        with six.assertRaisesRegex(self, ValueError, msg):
            compose = PungiCompose("http://localhost/compose/Workstation")
            compose.get_rpms_data()
