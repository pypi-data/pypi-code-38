# -*- coding: utf-8 -*-
# :Project:   metapensiero.deform.semantic_ui -- Pyramid glue
# :Created:   ven 16 feb 2018 17:34:58 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 eTour s.r.l.
#

import deform

from pkg_resources import resource_filename
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request


def includeme(config):
    config.include('pyramid_chameleon')

    config.add_translation_dirs(
        'colander:locale',
        'deform:locale')

    config.add_static_view('deform-static', 'deform:static')

    def translator(term):
        return get_localizer(get_current_request()).translate(term)

    templates_dir = resource_filename('metapensiero.deform.semantic_ui', 'templates/')
    zpt_renderer = deform.ZPTRendererFactory([templates_dir], translator=translator)
    deform.Form.set_default_renderer(zpt_renderer)
