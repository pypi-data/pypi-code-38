# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
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
Data models for reporting
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa

from rattail.db.model import Base, ExportMixin
from rattail.db.core import filename_column
from rattail.db.types import JSONTextDict
from rattail.util import NOTSET


@six.python_2_unicode_compatible
class ReportOutput(ExportMixin, Base):
    """
    Represents a generated report(s)
    """
    __tablename__ = 'report_output'
    model_title = "Generated Report"

    report_name = sa.Column(sa.String(length=255), nullable=True, doc="""
    Proper name of the report.
    """)

    report_type = sa.Column(sa.String(length=255), nullable=True, doc="""
    Type key for the report.
    """)

    params = sa.Column(JSONTextDict(), nullable=True, doc="""
    Parameters used to generate the report, encoded as JSON.
    """)

    filename = filename_column()

    def filepath(self, config, filename=NOTSET, **kwargs):
        if filename is NOTSET:
            filename = self.filename
        return super(ReportOutput, self).filepath(config, filename=filename, **kwargs)

    def __str__(self):
        return "{} {}".format(self.id_str, self.report_name)
