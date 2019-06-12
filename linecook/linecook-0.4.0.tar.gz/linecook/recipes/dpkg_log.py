# -*- coding: utf-8 -*-
"""
linecook recipe for dpkg.log.
"""
from __future__ import unicode_literals

from .. import patterns as rx
from ..transforms import color_text, partition


EMPHASIZE_ACTIONS = rx.bounded_word(rx.any_of(
    'install', 'upgrade', 'remove', 'purge',
))


def emphasize_dpkg_actions():
    """Return transform that emphasizes packaging actions"""
    return partition(
        rx.whitespace + EMPHASIZE_ACTIONS,
        on_match=color_text(color='yellow'),
        on_mismatch=color_text(color='cyan'),
    )


recipe = [
    partition(
        '{} {}'.format(rx.date, rx.time),
        on_match=color_text(color='blue'),
        on_mismatch=partition(
            rx.first_word,
            on_match=emphasize_dpkg_actions(),
        ),
    ),
]
