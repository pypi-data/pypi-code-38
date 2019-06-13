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
Report Definitions
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import cache
from rattail.util import progress_loop


@six.python_2_unicode_compatible
class Report(object):
    """
    Base class for all reports.

    .. attr:: type_key

       Any proper report definition should assign a "globally unique" value to
       this attribute.  In practice that means you should prefix the value with
       something specific to your org, e.g. ``'acme_'``.

    .. attr:: name

       This should be a human-recognizable name for the report.  It is
       (usually) saved along with the report output.

    .. attr:: param_sequence

       Unfortunately for now, the framework doesn't know how to order the
       report params, to match their definition in code.  So in the meantime
       you must explicitly declare this in ``param_sequence``.
    """
    type_key = None
    name = None
    param_sequence = []

    def __init__(self, config=None, **kwargs):
        self.config = config
        self.enum = config.get_enum() if config else None
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return str(self.name or "")

    def collect_static_params(self, **kwargs):
        """
        Returns the list of "static" params defined on the report class.
        """
        params = []
        possible_params = self.param_sequence or dir(self)
        for name in possible_params:

            # skip anything private-looking
            if name.startswith('_'):
                continue

            obj = getattr(self, name)
            if isinstance(obj, ReportParam):

                # make sure parameter knows its own name
                obj.name = name
                params.append(obj)

        return params

    def make_params(self, session, **kwargs):
        """
        Should return a list of :class:`ReportParam` objects, which will define
        user input options when generating a new report.  Default behavior is
        to return the list of "static" params which are defined on the report
        class itself, i.e. the result of :meth:`collect_static_params()`.
        """
        return self.collect_static_params(**kwargs)

    def make_data(self, session, params, progress=None, **kwargs):
        """
        Should generate and return a dict which contains all relevant data for
        the report, and which will be used when writing the output file.
        """
        raise NotImplementedError

    def make_report_name(self, session, params, data, **kwargs):
        """
        Should return a "name" for the specific report being generated.  This
        name is set on the :class:`~rattail.db.model.reports.ReportOutput`
        database record, for instance.  It needn't be unique as far as the DB
        schema is concerned.
        """
        return self.name or self.type_key or ""

    def make_filename(self, session, params, data, **kwargs):
        """
        Should generate and return a filename for the report output, according
        to the given params and data.
        """
        raise NotImplementedError

    def write_file(self, session, params, data, path, progress=None, **kwargs):
        """
        Should write the output file for the report with the given data and to
        the given filename.
        """
        raise NotImplementedError

    def cache_model(self, session, model, **kwargs):
        return cache.cache_model(session, model, **kwargs)

    def progress_loop(self, func, items, factory, **kwargs):
        return progress_loop(func, items, factory, **kwargs)


class ReportParam(object):
    """
    Base class for report parameter definitions.
    """

    def __init__(self, typ=str, required=True, doc="", **kwargs):
        self.type = typ
        self.required = required
        self.__doc__ == doc
        kwargs.pop('__doc__', None)
        for key, value in kwargs.items():
            setattr(self, key, value)
