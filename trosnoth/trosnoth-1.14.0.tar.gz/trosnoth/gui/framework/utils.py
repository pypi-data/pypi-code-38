# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2012 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

def wrapWords(app, text, font, width, breakWords = True):
    '''
    Takes a section of text, a font with which it will be rendered, and the
    maximum size that a line can be, and returns a list of the new strings.
    @param text The text to split
    @param font The font that the text will be rendered with
    @param width The maximum width (in pixels) of a single line of text
    @param breakWords If this is set to true, words will be allowed to be
            broken in half if it may look neater (annotated with a hyphen).
            If not, words will only break if absolutely necessary.
    '''
    lines = text.split('\n')
    # Determine if the line needs word-wrapping:
    x = 0
    while x < len(lines):
        line = lines[x]
        lastSp = -1
        p = 0
        while p < len(line):
            if line[p] == ' ':
                lastSp = p

            p += 1
            if font.size(app, line[:p])[0] > width:
                # we need to wordwrap
                if lastSp == -1 or (p - lastSp > 20 and breakWords):
                    spFound = False
                    for t in range(p, p + 5):
                        if t >= len(line) or line[t] == ' ':
                            spFound = True
                            break
                    if spFound and breakWords:
                        # But there's a space coming up within the next 5
                        # characters - let's even things up a bit by giving
                        # it a few more from this end.
                        lines[x] = line[:p - t - 2] + '-'
                        lines.insert(x+1, line[p-t-2:])
                        line = line[:p - t - 2] + '-'
                    else:
                        lines[x] = line[:p] + '-'
                        lines.insert(x+1, line[p:])
                        line = line[:p] + '-'
                else:
                    lines[x] = line[:lastSp]
                    lines.insert(x + 1, line[lastSp + 1:])
                    line = lines[x]
                break
        x += 1
    return lines
