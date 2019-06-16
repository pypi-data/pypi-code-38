# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pygments.lexer import RegexLexer, bygroups, default
from pybemolle.tokens import *


__all__ = ['BemolleLexer']


class BemolleLexer(RegexLexer):
    name = 'Bemolle'
    aliases = ['bemolle', 'bmolle']
    filenames = ['*.bemolle', '*.bmolle']
    mimetypes = ['text/be-molle', 'text/b-molle',
                 'text/bemolle', 'text/bmolle']

    def include_chords(*tokens, alt=r'[#\*\+\w\\\/]*'):
        """Makes a list of tokens ready to include.
        Adds all possible tokens: major, minor, a symbols, etc.

        :param tuple tokens: tuple of (regex, pygments.token.Token)
        :param str alt: alteration symbols regexp
        :return list: list of tokens ready to include
        """
        result = [(r'(?:[ \t]|\\\n)+', Text)]
        for r, ch in tokens:
            result.append((r'\b({0}m)({1})'.format(r, alt),
                           bygroups(ch.Minor, ch.Alt)))
            result.append((r'\b({0})({1})'.format(r, alt),
                           bygroups(ch.Major, ch.Alt)))
        result.append(default('#pop'))
        return result

    tokens = {
        'root': [
            (r'(::|:lat)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
             'chords_lat'),
            (r'(;;|;eng)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
             'chords_eng'),
            (r'.', Text),
        ],
        'chords_lat': include_chords(
            (r'C#', Chord.C.Sharp),
            (r'D#', Chord.D.Sharp),
            (r'E#', Chord.E.Sharp),
            (r'F#', Chord.F.Sharp),
            (r'G#', Chord.G.Sharp),
            (r'A#', Chord.A.Sharp),
            (r'H#', Chord.B.Sharp),
            (r'Cb', Chord.C.Flat),
            (r'Db', Chord.D.Flat),
            (r'Eb', Chord.E.Flat),
            (r'Fb', Chord.F.Flat),
            (r'Gb', Chord.G.Flat),
            (r'Ab', Chord.A.Flat),
            (r'B', Chord.B.Flat),
            (r'C', Chord.C),
            (r'D', Chord.D),
            (r'E', Chord.E),
            (r'F', Chord.F),
            (r'G', Chord.G),
            (r'A', Chord.A),
            (r'H', Chord.B),
        ),
        'chords_eng': include_chords(
            (r'C#', Chord.C.Sharp),
            (r'D#', Chord.D.Sharp),
            (r'E#', Chord.E.Sharp),
            (r'F#', Chord.F.Sharp),
            (r'G#', Chord.G.Sharp),
            (r'A#', Chord.A.Sharp),
            (r'B#', Chord.B.Sharp),
            (r'Cb', Chord.C.Flat),
            (r'Db', Chord.D.Flat),
            (r'Eb', Chord.E.Flat),
            (r'Fb', Chord.F.Flat),
            (r'Gb', Chord.G.Flat),
            (r'Ab', Chord.A.Flat),
            (r'Bb', Chord.B.Flat),
            (r'C', Chord.C),
            (r'D', Chord.D),
            (r'E', Chord.E),
            (r'F', Chord.F),
            (r'G', Chord.G),
            (r'A', Chord.A),
            (r'B', Chord.B),
        ),
    }
