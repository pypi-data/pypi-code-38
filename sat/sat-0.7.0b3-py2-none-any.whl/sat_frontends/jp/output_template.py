#! /usr/bin/python
# -*- coding: utf-8 -*-

# jp: a SàT command line tool
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Standard outputs"""


from sat_frontends.jp.constants import Const as C
from sat.core.i18n import _
from sat.core import log
from sat.tools.common import template
from functools import partial
import logging
import webbrowser
import tempfile
import os.path

__outputs__ = ["Template"]
TEMPLATE = u"template"
OPTIONS = {u"template", u"browser", u"inline-css"}


class Template(object):
    """outputs data using SàT templates"""

    def __init__(self, jp):
        self.host = jp
        jp.register_output(C.OUTPUT_COMPLEX, TEMPLATE, self.render)

    def _front_url_tmp_dir(self, ctx, relative_url, tmp_dir):
        """Get front URL for temporary directory"""
        template_data = ctx[u'template_data']
        return u"file://" + os.path.join(tmp_dir, template_data.theme, relative_url)

    def _do_render(self, template_path, css_inline, **kwargs):
        try:
            return self.renderer.render(template_path, css_inline=css_inline, **kwargs)
        except template.TemplateNotFound:
            self.host.disp(_(u"Can't find requested template: {template_path}")
                .format(template_path=template_path), error=True)
            self.host.quit(C.EXIT_NOT_FOUND)

    def render(self, data):
        """render output data using requested template

        template to render the data can be either command's TEMPLATE or
        template output_option requested by user.
        @param data(dict): data is a dict which map from variable name to use in template
            to the variable itself.
            command's template_data_mapping attribute will be used if it exists to convert
            data to a dict usable by the template.
        """
        # media_dir is needed for the template
        self.host.media_dir = self.host.bridge.getConfig("", "media_dir")
        cmd = self.host.command
        try:
            template_path = cmd.TEMPLATE
        except AttributeError:
            if not "template" in cmd.args.output_opts:
                self.host.disp(_(
                    u"no default template set for this command, you need to specify a "
                    u"template using --oo template=[path/to/template.html]"),
                    error=True,
                )
                self.host.quit(C.EXIT_BAD_ARG)

        options = self.host.parse_output_options()
        self.host.check_output_options(OPTIONS, options)
        try:
            template_path = options["template"]
        except KeyError:
            # template is not specified, we use default one
            pass
        if template_path is None:
            self.host.disp(_(u"Can't parse template, please check its syntax"),
                           error=True)
            self.host.quit(C.EXIT_BAD_ARG)

        try:
            mapping_cb = cmd.template_data_mapping
        except AttributeError:
            kwargs = data
        else:
            kwargs = mapping_cb(data)

        css_inline = u"inline-css" in options

        if "browser" in options:
            template_name = os.path.basename(template_path)
            tmp_dir = tempfile.mkdtemp()
            front_url_filter = partial(self._front_url_tmp_dir, tmp_dir=tmp_dir)
            self.renderer = template.Renderer(
                self.host, front_url_filter=front_url_filter, trusted=True)
            rendered = self._do_render(template_path, css_inline=css_inline, **kwargs)
            self.host.disp(_(
                u"Browser opening requested.\n"
                u"Temporary files are put in the following directory, you'll have to "
                u"delete it yourself once finished viewing: {}").format(tmp_dir))
            tmp_file = os.path.join(tmp_dir, template_name)
            with open(tmp_file, "w") as f:
                f.write(rendered.encode("utf-8"))
            theme, theme_root_path = self.renderer.getThemeAndRoot(template_path)
            if theme is None:
                # we have an absolute path
                webbrowser
            static_dir = os.path.join(theme_root_path, C.TEMPLATE_STATIC_DIR)
            if os.path.exists(static_dir):
                # we have to copy static files in a subdirectory, to avoid file download
                # to be blocked by same origin policy
                import shutil
                shutil.copytree(
                    static_dir, os.path.join(tmp_dir, theme, C.TEMPLATE_STATIC_DIR)
                )
            webbrowser.open(tmp_file)
        else:
            # FIXME: Q&D way to disable template logging
            #        logs are overcomplicated, and need to be reworked
            template_logger = log.getLogger(u"sat.tools.common.template")
            template_logger.log = lambda *args: None

            logging.disable(logging.WARNING)
            self.renderer = template.Renderer(self.host, trusted=True)
            rendered = self._do_render(template_path, css_inline=css_inline, **kwargs)
            self.host.disp(rendered)
