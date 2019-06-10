#
# Copyright (c) 2019 UCT Prague.
# 
# ext.py is part of Invenio Explicit ACLs 
# (see https://github.com/oarepo/invenio-explicit-acls).
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

"""Flask extension for CIS ACLs."""

from __future__ import absolute_import, print_function

# noinspection PyUnresolvedReferences
from invenio_explicit_acls.api import AclAPI

from . import config


class InvenioExplicitAcls(object):
    """ACLs for invenio extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['invenio-explicit-acls'] = AclAPI(app)

        # register signals
        from invenio_explicit_acls.signals import add_acls
        from invenio_indexer.signals import before_record_index

        before_record_index.connect(add_acls)

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('INVENIO_EXPLICIT_ACLS_'):
                app.config.setdefault(k, getattr(config, k))
