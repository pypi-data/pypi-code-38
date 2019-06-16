# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Data Models for Label Printing
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy.orm import object_session

from .core import Base, uuid_column
from rattail.util import load_object


@six.python_2_unicode_compatible
class LabelProfile(Base):
    """
    Represents a collection of settings for product label printing.
    """
    __tablename__ = 'label_profile'
    __versioned__ = {}

    uuid = uuid_column()
    ordinal = sa.Column(sa.Integer())

    code = sa.Column(sa.String(length=30), nullable=True, doc="""
    Supposedly unique "code" for the label profile.  May be useful for
    identification of a common label type across nodes, for instance.
    """)

    description = sa.Column(sa.String(length=50))
    printer_spec = sa.Column(sa.String(length=255))
    formatter_spec = sa.Column(sa.String(length=255))
    format = sa.Column(sa.Text())
    visible = sa.Column(sa.Boolean())

    sync_me = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether this label profile should be synced across "all"
    other Rattail systems across the organization.
    """)

    _printer = None
    _formatter = None

    def __str__(self):
        return str(self.description or '')

    # TODO: Copy elsewhere, deprecate and remove this logic (not strictly an
    # API call from within data model, but should go with the others, below).
    def get_formatter(self, config):
        if not self._formatter and self.formatter_spec:
            try:
                formatter = load_object(self.formatter_spec)
            except AttributeError:
                pass
            else:
                self._formatter = formatter(config)
                self._formatter.format = self.format
        return self._formatter        

    # TODO: Copy elsewhere, deprecate and remove this logic (API call from
    # within data model).
    def get_printer(self, config):
        if not self._printer and self.printer_spec:
            try:
                printer = load_object(self.printer_spec)
            except AttributeError:
                pass
            else:
                self._printer = printer(config)
                for name in printer.required_settings:
                    setattr(printer, name, self.get_printer_setting(name))
                self._printer.formatter = self.get_formatter(config)
        return self._printer

    # TODO: Copy elsewhere, deprecate and remove this logic (API call from
    # within data model).
    def get_printer_setting(self, name):
        from rattail.db.api import get_setting
        if self.uuid is None:
            return None
        session = object_session(self)
        name = 'labels.{0}.printer.{1}'.format(self.uuid, name)
        return get_setting(session, name)

    # TODO: Copy elsewhere, deprecate and remove this logic (API call from
    # within data model).
    def save_printer_setting(self, name, value):
        from rattail.db.api import save_setting
        session = object_session(self)
        if self.uuid is None:
            session.flush()
        name = 'labels.{0}.printer.{1}'.format(self.uuid, name)
        save_setting(session, name, value)
