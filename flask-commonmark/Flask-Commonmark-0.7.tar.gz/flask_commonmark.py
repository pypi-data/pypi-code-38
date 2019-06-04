# -*- coding: utf-8 -*-
"""
flask_commonmark
----------------

Commonmark filter class for Flask. One may notice a similarity to Dan Colish's Flask-Markdown, from which I shamelessly copied a bunch of this. Does not have all the nice provisions for extension baked in, but probably does what you need. See https://commonmark.org/ for details.

Usage
::
    from flask_commonmark import Commonmark
    cm = Commonmark(app)

Include filter in your template
::
    {% filter commonmark %}
    # Nagasaki
    1. Chew Terbaccy
    1. Wicky-waky-woo
    {% endfilter %}

Note: The filter expects renderable bits to be fully left-aligned! Otherwise expect plaintext. See example in README.

:copyright: (c) 2019 by Doug Shawhan.
:license: BSD, MIT see LICENSE for details.
"""
from flask import Markup
from jinja2 import evalcontextfilter, escape
import commonmark as cm


class Commonmark(object):
    """
    Commonmark
    ----------

    Wrapper class for Commonmark (aka "common markdown"), objects.

    Args:
        app (obj):  Flask app instance
        auto_escape (bool): Use Jinja2 auto_escape, default False
    """

    def __init__(self, app, auto_escape=False):
        """
        Create parser and renderer objects and auto_escape value.
        Set filter.
        """
        self.auto_escape = auto_escape
        self.cm_parse = cm.Parser()
        self.cm_render = cm.HtmlRenderer()

        app.jinja_env.filters.setdefault(
            "commonmark", self.__build_filter(self.auto_escape)
        )

    def __call__(self, stream):
        """
        Render markdown stream.

        Args:
            stream (str):   template stream containing markdown tags

        Returns:
            html (str):  markdown rendered as html
        """
        return self.cm_render.render(self.cm_parse.parse(stream))

    def __build_filter(self, app_auto_escape):
        """
        Jinja2 __build_filter

        Args:
            app_auto_escape (bool): auto_escape value (default False)
        Returns:
            commonmark_filter (obj):  context filter
        """

        @evalcontextfilter
        def commonmark_filter(eval_ctx, stream):
            """
            Called by Jinja2 when evaluating the Commonmark filter.

            Args:
                eval_ctx (obj): Jinja2 evaluation context
                stream (str):   string to filter
            """
            __filter = self
            if app_auto_escape and eval_ctx.autoescape:
                return Markup(__filter(escape(stream)))
            return Markup(__filter(stream))

        return commonmark_filter
