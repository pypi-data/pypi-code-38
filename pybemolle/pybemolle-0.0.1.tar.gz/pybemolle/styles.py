# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pygments.style import Style

from pybemolle.tokens import *


__all__ = ['BemolleStyle']


class BemolleStyle(Style):
    """
    Colored chords theme.
    """

    background_color = '#f8f8f8'
    default_style = ''

    styles = {
        Whitespace: '#bbbbbb',
        Token: '#d0d0d0',

        Chord.C: '#00e800',
        Chord.D: '#006bff',
        Chord.E: '#8100ce',
        Chord.F: '#3d015b',
        Chord.G: '#d10400',
        Chord.A: '#ff8800',
        Chord.B: '#9af400',
        Chord.C.Flat: '#9af400',
        Chord.D.Flat: '#05feaa',
        Chord.E.Flat: '#2e01f0',
        Chord.F.Flat: '#8100ce',
        Chord.G.Flat: '#680351',
        Chord.A.Flat: '#e44202',
        Chord.B.Flat: '#ebff07',
        Chord.C.Sharp: '#05feaa',
        Chord.D.Sharp: '#2e01f0',
        Chord.E.Sharp: '#3d015b',
        Chord.F.Sharp: '#680351',
        Chord.G.Sharp: '#e44202',
        Chord.A.Sharp: '#ebff07',
        Chord.B.Sharp: '#00e800',

        Error: 'border: #ff0000'
    }
