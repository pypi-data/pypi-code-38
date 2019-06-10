#
# Copyright (c) 2019 UCT Prague.
# 
# permissions.py is part of Invenio Explicit ACLs 
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
"""Invenio-compatible permissions."""
import logging
from functools import partial

from flask import request
from flask_login import current_user

logger = logging.getLogger(__name__)


def _check_elasticsearch(operation, record, *args, **kwargs):
    """Return permission that check if the record exists in ES index.

    :params record: A record object.
    :returns: A object instance with a ``can()`` method.
    """
    def can(self):
        """Try to search for given record."""
        if logger.isEnabledFor(logging.DEBUG):           # pragma no cover
            logger.debug('Check called, operation %s, record %s, current user %s', operation, record, current_user)
        search = request._methodview.search_class(operation=operation)
        search = search.get_record(str(record.id))
        # print(search.query.to_dict())
        resp = search.count() == 1
        if logger.isEnabledFor(logging.DEBUG):           # pragma no cover
            logger.debug('      -> allowed', resp)
        return resp

    return type(f'CheckES-{operation}', (), {'can': can})()


acl_read_permission_factory = partial(_check_elasticsearch, operation='get')
acl_update_permission_factory = partial(_check_elasticsearch, operation='update')
acl_delete_permission_factory = partial(_check_elasticsearch, operation='delete')
