# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt

from upt_fedora.upt_fedora import FedoraBackend


class TestFedoraBackend(unittest.TestCase):
    def setUp(self):
        self.fedora_backend = FedoraBackend()

    def test_unhandled_frontend(self):
        upt_pkg = upt.Package('foo', '42')
        upt_pkg.frontend = 'invalid backend'
        with self.assertRaises(upt.UnhandledFrontendError):
            self.fedora_backend.create_package(upt_pkg)


if __name__ == '__main__':
    unittest.main()
