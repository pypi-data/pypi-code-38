#
# Copyright (c) 2019 UCT Prague.
# 
# signals.py is part of Invenio Explicit ACLs 
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
"""Signal called to add cached ACLs to ES data."""
from invenio_jsonschemas import current_jsonschemas

from invenio_explicit_acls.proxies import current_explicit_acls
from invenio_explicit_acls.utils import get_record_acl_enabled_schema


def add_acls(app, json=None, index=None, record=None, doc_type=None, **kwargs):
    """Signal handler that adds cached ACLs for all records that are ACL enabled."""
    # prevent injection of explicit acls even in case of a schema that
    # is not enabled and when marshmallow is circumvented
    if '_invenio_explicit_acls' in json:
        del json['_invenio_explicit_acls']  # pragma no cover

    schema = get_record_acl_enabled_schema(record)
    if not schema:
        return  # pragma no cover

    matching_acls = current_explicit_acls.get_record_acls(record)
    acl_props = current_explicit_acls.serialize_record_acls(matching_acls, record=record)
    json['_invenio_explicit_acls'] = acl_props
