import string
from io import StringIO
from os.path import normpath, join, dirname
from .text_pos import text_origin
from .ast import (
    Word, CommandTok, CloseBra, OpenBra, WhiteSpace, NewParagraph,
    CloseSqBra, OpenSqBra
)


whitespaces = set(string.whitespace)


class Lexer:
    ident_chars = set(string.ascii_letters).union(set(string.digits)).union({
        '-', '+', '*'
    })
    special_chars = {'\\', '{', '}', '%', '[', ']'}
    special_command_chars = {'_', '\\', '%', '{', '}'}

    def __init__(self, source_name, stream, ident_chars=None, special_chars=set()):
        self.source_file = source_name
        self.file = stream
        self.pos = text_origin
        if ident_chars is not None:
            self.ident_chars = ident_chars
        self.special_chars = self.special_chars.union(special_chars)
        self._first = True
        self._end_reached = False

    @classmethod
    def from_file(cls, filename, ident_chars=None, special_chars=set()):
        file = open(filename)
        return cls(filename, file, ident_chars=ident_chars, special_chars=special_chars)

    @classmethod
    def from_source(cls, source, filename=None, ident_chars=None, special_chars=set()):
        if filename is None:
            _filename = 'anonym'
        else:
            _filename = filename
        return cls(_filename, StringIO(source), ident_chars=ident_chars, special_chars=special_chars)

    def open_newfile(self, source_file):
        path = normpath(join(dirname(self.source_file), source_file))
        return self.__class__.from_file(path, ident_chars=self.ident_chars,
                                        special_chars=self.special_chars)

    def read(self):
        c = self.file.read(1)
        if self._first:
            self._first = False
        elif c == '\n':
            self.pos = self.pos.new_line()
        elif c != '' or not self._end_reached:
            self.pos += 1

        if c == '':
            self._end_reached = True
        return c

    def tokens(self):
        c = self.read()
        buff_init_pos = self.pos
        buffer = []
        while c != '':
            if c in self.special_chars:

                if buffer:
                    yield Word(buff_init_pos, ''.join(buffer))
                    buffer = []

                if c == '%':
                    while c != '\n':
                        c = self.read()
                    c = self.read()

                elif c == '\\':
                    init_pos = self.pos
                    buffer = [c]
                    c = self.read()
                    while c in self.ident_chars:
                        buffer.append(c)
                        c = self.read()
                    if len(buffer) == 1 and c in self.special_command_chars:
                        buffer.append(c)
                        c = self.read()
                    yield CommandTok(init_pos, ''.join(buffer))
                    buffer = []

                elif c == '}':
                    yield CloseBra(self.pos)
                    c = self.read()

                elif c == '{':
                    yield OpenBra(self.pos)
                    c = self.read()

                elif c == ']':
                    yield CloseSqBra(self.pos)
                    c = self.read()

                elif c == '[':
                    yield OpenSqBra(self.pos)
                    c = self.read()

            elif c in whitespaces:
                if buffer:
                    yield Word(buff_init_pos, ''.join(buffer))
                    buffer = []
                newlines = 0
                new_par_pos = self.pos
                while c in whitespaces:
                    if c == '\n':
                        newlines += 1
                    c = self.read()

                if newlines > 1:
                    yield NewParagraph(new_par_pos, self.pos)
                else:
                    yield WhiteSpace(new_par_pos, self.pos)
            else:
                if not buffer:
                    buff_init_pos = self.pos
                buffer.append(c)
                c = self.read()

        if buffer:
            yield Word(buff_init_pos, ''.join(buffer))
