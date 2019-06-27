from __future__ import absolute_import
import os
from os import path as osp

import nose

package_dir = osp.dirname(osp.dirname(__file__))


class WebGridNosePlugin(nose.plugins.Plugin):
    enabled = False

    def configure(self, options, config):
        """Configure the plugin"""
        curdir = osp.realpath(os.curdir)
        if curdir.lower().startswith(package_dir.lower()):
            self.enabled = True

    def begin(self):
        from webgrid_ta.app import create_app
        app = create_app(config='Test')
        app.test_request_context().push()

        from webgrid_ta.model import load_db
        load_db()
