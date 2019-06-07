# -*- coding: utf-8 -*-
# Copyright (c) 2003-2012 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Module that contains special canvas features.
"""
# pylint: disable=W,C,I,R

from urwid.canvas import (trim_line, rle_append_modify, apply_target_encoding,
                          rle_len, LayoutSegment, TextCanvas, rle_join_modify)

__all__ = ['apply_text_layout']

# hack marks: "#+": added, "#=": modified
def apply_text_layout(text, attr, ls, maxcol, numbering=False): #=
    """
    Hack for urwid.canvas.apply_text_layout that able to display line numbers
    """
    if numbering: #+
        lnb = len(str(text.count('\n') + 1)) + 1 #+
    else: #+
        lnb = 0 #+

    utext = type(text)==type(u"")
    t = []
    a = []
    c = []

    class AttrWalk:
        pass
    aw = AttrWalk
    aw.k = 0 # counter for moving through elements of a
    aw.off = 0 # current offset into text of attr[ak]

    def arange( start_offs, end_offs ):
        """Return an attribute list for the range of text specified."""
        if start_offs < aw.off:
            aw.k = 0
            aw.off = 0
        o = []
        while aw.off < end_offs:
            if len(attr)<=aw.k:
                # run out of attributes
                o.append((None,end_offs-max(start_offs,aw.off)))
                break
            at,run = attr[aw.k]
            if aw.off+run <= start_offs:
                # move forward through attr to find start_offs
                aw.k += 1
                aw.off += run
                continue
            if end_offs <= aw.off+run:
                o.append((at, end_offs-max(start_offs,aw.off)))
                break
            o.append((at, aw.off+run-max(start_offs, aw.off)))
            aw.k += 1
            aw.off += run
        return o

    for idx, line_layout in enumerate(ls):
        # trim the line to fit within maxcol
        line_layout = trim_line( line_layout, text, 0, maxcol - lnb) #=

        if lnb: #+
            line = [str(idx).rjust(lnb - 1) + ' '] #+
            linea = [('INFO', lnb)] #+
        else: #+
            line = [] #=
            linea = [] #=
        linec = []

        def attrrange( start_offs, end_offs, destw ):
            """
            Add attributes based on attributes between
            start_offs and end_offs.
            """
            if start_offs == end_offs:
                [(at,run)] = arange(start_offs,end_offs)
                rle_append_modify( linea, ( at, destw ))
                return
            if destw == end_offs-start_offs:
                for at, run in arange(start_offs,end_offs):
                    rle_append_modify( linea, ( at, run ))
                return
            # encoded version has different width
            o = start_offs
            for at, run in arange(start_offs, end_offs):
                if o+run == end_offs:
                    rle_append_modify( linea, ( at, destw ))
                    return
                tseg = text[o:o+run]
                tseg, cs = apply_target_encoding( tseg )
                segw = rle_len(cs)

                rle_append_modify( linea, ( at, segw ))
                o += run
                destw -= segw

        for seg in line_layout:
            #if seg is None: assert 0, ls
            s = LayoutSegment(seg)
            if s.end:
                tseg, cs = apply_target_encoding(
                    text[s.offs:s.end])
                line.append(tseg)
                attrrange(s.offs, s.end, rle_len(cs))
                rle_join_modify( linec, cs )
            elif s.text:
                tseg, cs = apply_target_encoding( s.text )
                line.append(tseg)
                attrrange( s.offs, s.offs, len(tseg) )
                rle_join_modify( linec, cs )
            elif s.offs:
                if s.sc:
                    line.append(" "*s.sc)
                    attrrange( s.offs, s.offs, s.sc )
            else:
                line.append(" "*s.sc)
                linea.append((None, s.sc))
                linec.append((None, s.sc))

        t.append("".join(line))
        a.append(linea)
        c.append(linec)

    return TextCanvas(t, a, c, maxcol=maxcol)

