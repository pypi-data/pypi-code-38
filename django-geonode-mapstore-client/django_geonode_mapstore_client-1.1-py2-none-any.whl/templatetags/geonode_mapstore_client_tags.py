# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2015-2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################
from django import template

register = template.Library()


@register.inclusion_tag(
    'geonode-mapstore-client/_client_composer_js.html', takes_context=True)
def client_composer_js(context, options=None):
    """
    React Client Composer js template tag.
    """
    return context


@register.inclusion_tag(
    'geonode-mapstore-client/_client_viewer_js.html', takes_context=True)
def client_viewer_js(context, options=None):
    """
    React client viewer js template tag.
    """
    return context
