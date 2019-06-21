from __future__ import print_function

from burlap.common import Satchel
from burlap.tests.base import TestCase

class ManifestTests(TestCase):

    def test_get_current(self):

        class MyTestSatchel(Satchel):

            name = 'mytest'

            def set_defaults(self):
                self.env.myvar = 123

            def configure(self):
                pass

        mytest = MyTestSatchel()

        manifest = mytest.current_manifest
        print('manifest0:', manifest)
        assert manifest == {'myvar': 123, 'enabled': True}

        mytest.env.myvar = 456

        manifest = mytest.current_manifest
        print('manifest1:', manifest)
        assert manifest == {'myvar': 456, 'enabled': True}
