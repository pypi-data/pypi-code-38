from blessed import Terminal
from math import floor, ceil
from collections import defaultdict
import re
import math

# Not thread-safe
class Line():
    '''A line of formatted text in a blessed block. Most notably, this line
    does not wrap. Instead, it truncates at the block width value. It supports
    colored text using the blessed color tags, eg, ${blue}blue text{$normal}.
    Two different views of the text of the line are available, and they
    are adjusted dynamically as the width of the block changes: (1) plain,
    which is the text minus any color tabs, (2) display, which when printed
    shows the plain text with colors. When viewed outside of the blessed 
    terminal, display differs from plain in two ways. It shows the color tags,
    and it doubles curly braces in order to escape them. Also note that tags
    that don't have an affect do not show up in display. For example, tags
    that have no text following them before the end of the line (as determined
    dynamically by the width of the block) or before the next tag.
    '''

    COLORS = ['{{t.{}}}'.format(color) for color in ('black', 'red', 'green', 'yellow',
                                                     'blue', 'magenta', 'cyan', 'white')]
    def __init__(self, blessed_text, width, just):
        '''Create a Line object

        Args:
            blessed_text (str): Text of any length which may contain blessed color tags.

        Returns:
            nothing, but the plain and display attributes are made available.
        '''
        self._full = blessed_text
        self._text, self._seqs, self.last_seq = Line.parse(blessed_text)
        self._build(0, width, just)

    def __len__(self):
        '''Returns:
               the length of the text when viewed in a blessed terminal
        '''
        return len(self.plain)

    def __repr__(self):
        return self.plain  # TODO what should this be?

    def parse(full):
        seqs = defaultdict(list)
        text = ''
        loc = 0
        prev_end = 0
        prev_seq = None
        prev_loc = None
        if full:
            for match in re.finditer(r'{t\..+?}', full):
                loc += match.start() - prev_end
                curr_seq = full[match.start():match.end()]
                t = full[prev_end:match.start()] # text before/after/between sequences
                text += t
                if not prev_seq:
                    seqs[loc] = curr_seq  # always keep the first seq
                    prev_loc = loc
                else:
                    if (prev_end == match.start()
                        and curr_seq in Line.COLORS
                        and seqs[prev_loc] in Line.COLORS): # drop the first of two colors
                        seqs[prev_loc] = curr_seq
                    # Otherwise, Only skip sequences that are exact duplicates
                    elif curr_seq != prev_seq:
                        if loc in seqs:
                            seqs[loc] += curr_seq
                        else:
                            seqs[loc] = curr_seq
                        prev_loc = loc

                prev_seq = curr_seq
                prev_end = match.end()
            text += full[prev_end:]
        return text, seqs, prev_seq

    def _escape_brackets(self, text):
        out = []
        for c in text:
            if c in '{}':
                out.append(c)
            out.append(c)
        return ''.join(out)

    def _calc_just(self, just, extra):
        if just == '<':
            return '', ' ' * extra
        elif just == '>':
            return ' ' * extra, ''
        else:  # ^
            return (' ' * floor(extra/2),
                    ' ' * ceil(extra/2))

    def _build(self, begin, width, just):
        plain = ''
        display = ''
        last_seq = ''
        start = min(0,begin)
        stop = min(width,len(self._text))
        for i in range(start, stop):
            if i in self._seqs:
                display += self._seqs[i]
                last_seq = self._seqs[i]
            c = self._text[i]
            plain += c
            display += self._escape_brackets(c)

        left_pad = right_pad = ''
        if width > stop:
            left_pad, right_pad = self._calc_just(just, width - stop)
        self.plain = left_pad + plain + right_pad
        self.display = left_pad + display + right_pad

    def resize(self, begin, width, just):
        self._build(begin, width, just)

    def repeat_to_width(blessed_text, width):
        text, seqs, last_seq = Line.parse(blessed_text)
        line = []
        for i in range(width):
            j = i % len(text)
            if j == 0:
                if j in seqs:
                    line.append(seqs[j])
                else:
                    line.append('{t.normal}')
            elif j in seqs:
                line.append(seqs[j])
            line.append(text[j])
        return Line(''.join(line), width, '^')

if __name__ == '__main__':
    term = Terminal()
    just = '^'
    line = Line("{t.green}{}{}}{blac{t.yellow}k justp{t.cyan}laintext{t.pink}", 15, just)
    for i in range(len(line.plain) + 2):
        line.resize(0,i,just)
        print(line.plain)
        print((line.display + '{t.normal}').format(t=term) + '*')

    line.resize(0,len(line.plain), just)
    print(line._full)
    print(line.plain)
    print(line.display)
    print((line.display + '{t.normal}').format(t=term) + '*')
