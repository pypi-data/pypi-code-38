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
Master class for generic export history views
"""

from __future__ import unicode_literals, absolute_import

import os

import six

from rattail.db import model

from pyramid.response import FileResponse
from webhelpers2.html import HTML, tags

from tailbone import forms
from tailbone.views import MasterView


class ExportMasterView(MasterView):
    """
    Master class for generic export history views
    """
    creatable = False
    editable = False
    export_has_file = False

    grid_columns = [
        'id',
        'created',
        'created_by',
        'record_count',
    ]

    form_fields = [
        'id',
        'created',
        'created_by',
        'record_count',
    ]

    def get_export_key(self):
        if hasattr(self, 'export_key'):
            return self.export_key

    def get_file_path(self, export, makedirs=False):
        return self.rattail_config.export_filepath(self.export_key,
                                                   export.uuid,
                                                   export.filename,
                                                   makedirs=makedirs)

    def configure_grid(self, g):
        super(ExportMasterView, self).configure_grid(g)

        g.joiners['created_by'] = lambda q: q.join(model.User)
        g.sorters['created_by'] = g.make_sorter(model.User.username)
        g.filters['created_by'] = g.make_filter('created_by', model.User.username)
        g.set_sort_defaults('created', 'desc')

        g.set_renderer('id', self.render_id)

        g.set_label('id', "ID")
        g.set_label('created_by', "Created by")

        g.set_link('id')

    def render_id(self, export, field):
        return export.id_str

    def configure_form(self, f):
        super(ExportMasterView, self).configure_form(f)
        export = f.model_instance

        # NOTE: we try to handle the 'creating' scenario even though this class
        # doesn't officially support that; just in case a subclass does want to

        # id
        if self.creating:
            f.remove_field('id')
        else:
            f.set_readonly('id')
            f.set_renderer('id', self.render_id)
            f.set_label('id', "ID")

        # created
        if self.creating:
            f.remove_field('created')
        else:
            f.set_readonly('created')
            f.set_type('created', 'datetime')

        # created_by
        if self.creating:
            f.remove_field('created_by')
        else:
            f.set_readonly('created_by')
            f.set_renderer('created_by', self.render_created_by)
            f.set_label('created_by', "Created by")

        # record_count
        if self.creating:
            f.remove_field('record_count')
        else:
            f.set_readonly('record_count')

        # download
        if self.export_has_file and self.viewing:
            # download = forms.renderers.FileFieldRenderer.new(
            #     self, storage_path=self.rattail_config.export_filedir(self.export_key),
            #     file_path=self.get_file_path(fs.model), download_url=self.get_download_url)
            f.append('download')
            f.set_renderer('download', self.render_download)

    def render_download(self, export, field):
        path = self.get_file_path(export)
        text = "{} ({})".format(export.filename, self.readable_size(path))
        url = self.request.route_url('{}.download'.format(self.get_route_prefix()), uuid=export.uuid)
        return tags.link_to(text, url)

    def render_created_by(self, export, field):
        user = export.created_by
        if not user:
            return ""
        text = six.text_type(user)
        if self.request.has_perm('users.view'):
            url = self.request.route_url('users.view', uuid=user.uuid)
            return tags.link_to(text, url)
        return text

    def get_download_url(self, filename):
        uuid = self.request.matchdict['uuid']
        return self.request.route_url('{}.download'.format(self.get_route_prefix()), uuid=uuid)

    def download(self):
        """
        View for downloading the export file.
        """
        export = self.get_instance()
        path = self.get_file_path(export)
        response = FileResponse(path, request=self.request)
        if six.PY3:
            response.headers['Content-Length'] = str(os.path.getsize(path))
            response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(export.filename)
        else:
            response.headers[b'Content-Length'] = six.binary_type(os.path.getsize(path))
            response.headers[b'Content-Disposition'] = b'attachment; filename="{}"'.format(export.filename)
        return response

    def delete_instance(self, export):
        """
        Delete the export file also, if it exists.
        """
        if self.export_has_file:
            path = self.get_file_path(export)
            if os.path.exists(path):
                os.remove(path)
                os.rmdir(os.path.dirname(path))
        super(ExportMasterView, self).delete_instance(export)

    @classmethod
    def defaults(cls, config):
        """
        Provide default configuration for a master view.
        """
        cls._defaults(config)
        cls._export_defaults(config)

    @classmethod
    def _export_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        # download export file
        if cls.export_has_file:
            config.add_route('{}.download'.format(route_prefix), '{}/{{{}}}/download'.format(url_prefix, model_key))
            config.add_view(cls, attr='download', route_name='{}.download'.format(route_prefix),
                            permission='{}.download'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.download'.format(permission_prefix),
                                           "Download {} data file".format(model_title))
