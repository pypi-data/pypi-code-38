# -*- coding: utf-8 -*-

"""
Adapter to use pystache to render a mustache template
"""

from __future__ import absolute_import, unicode_literals, print_function

import pystache


class PystacheAdapter(object):
    """
    Adapter for NoteBlockPreprocessor to render mustache templates using pystache
    """

    def render(self, template='', context=None, *args, **kwargs):
        if context is None:
            context = {}

        renderer = pystache.Renderer()
        return renderer.render(template, context)
