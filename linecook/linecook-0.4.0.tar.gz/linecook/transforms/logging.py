# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from toolz.functoolz import compose

from . import core
from .. import patterns


colorizer = compose(*[
    core.color_text(patterns.date, color='blue'),
    core.color_text(patterns.time_ms, color='blue'),
    core.color_text(' INFO ', color='cyan'),
    core.color_text(' WARN ', color='grey', on_color='on_yellow'),
    core.color_text(' ERROR ', color='grey', on_color='on_red'),
])
