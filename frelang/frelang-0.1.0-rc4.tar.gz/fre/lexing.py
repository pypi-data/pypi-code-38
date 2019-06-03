import string
import re

from . import stream
from . import specs


class LexerToken(object):
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return "({} '{}')".format(self.type, self.value)


class FreLexer(object):
    def __init__(self, lang_specs = None):
        lang_specs = lang_specs or specs.FreSpecs()
        self.input = stream.CharacterStream()
        self.lang_specs = lang_specs
    
    def write(self, data):
        self.input.write(data)

    def error(self, msg):
        self.input.error(msg)

    def read_hex_escape(self):
        data = ''

        for _ in range(2):
            ch = self.input.next()

            if ch is None:
                self.input.error("Hit end of file before proper hexadecimal character escape sequence!")

            elif ch not in '0123456789ABCDEF':
                self.input.error("Not a valid hexadecimal digit: '{}'".format(ch))

            data += ch

        return chr(int(ch, 16))

    def read_string_escape(self):
        seq = self.input.next()

        if seq is None:
            self.input.error("Hit end of file before escape sequence!")
            return ''

        elif seq == '"':
            self.input.error("Hit end of string before escape sequence!")
            return ''

        elif seq == 'n': return '\n'
        elif seq == '\\': return '\\'
        elif seq == '"': return '"'
        elif seq == "'": return "'"
        elif seq == 'x': return self.subreader('string.escape.hex', self.read_hex_escape)
        else:
            self.input.error("Hit end of file before escape sequence!")
            return ''

    def read_string(self):
        res = ""

        if self.input.peek() == "\"": self.input.next()

        while True:
            new_char = self.input.next()

            if new_char == "\"":
                break

            elif new_char == "\\":
                res += self.subreader('string.escape', self.read_string_escape).value

            else:
                res += new_char

        return LexerToken('string', res)
    
    def read_number_hex(self):
        accumulator = ''

        while True:
            if self.input.peek() not in '0123456789ABCDEF':
                break

            accumulator += self.input.next()

        if accumulator == '':
            self.input.error("No valid hexadecimal digit found! (found '{}' instead)".format(self.input.peek()))

        else:
            return int(accumulator, 16)

    def read_number_octal(self):
        accumulator = ''

        while True:
            if self.input.peek() not in '01234567':
                break

            accumulator += self.input.next()

        if accumulator == '':
            self.input.error("No valid octal digit found! (found '{}' instead)".format(self.input.peek()))

        else:
            return int(accumulator, 8)

    def read_number(self):
        accumulator = ''
        has_dot = False

        while True:
            if self.input.peek() == '.':
                if has_dot:
                    self.error("Multiple dots found in floating point literal!")

                else:
                    has_dot = True
                    accumulator += self.input.next()

            elif self.input.peek() not in string.digits:
                break

            accumulator += self.input.next()

        if has_dot:
            return LexerToken('number.float', float(accumulator))

        else:
            return int(accumulator, 10)

    def read_number_binary(self):
        accumulator = ''

        while True:
            if self.input.peek() not in '01':
                break

            accumulator += self.input.next()

        if accumulator == '':
            self.input.error("No valid binary digit found! (found '{}' instead)".format(self.input.peek()))

        else:
            return int(accumulator, 2)

    def subreader(self, name, func, *args, **kwargs):
        res = self.input.call(name, func, *args, **kwargs)

        if isinstance(res, LexerToken):
            return res

        else:
            return LexerToken(name.split('.')[0], res)

    def read_number_zero(self):
        accumulator = ""

        assert self.input.next() == '0';

        if self.input.peek() == '0': return

        if self.input.peek() in 'Xx':
            self.input.next()
            return self.subreader('number.hex', self.read_number_hex)

        elif self.input.peek() in 'Bb':
            self.input.next()
            return self.subreader('number.binary', self.read_number_binary)

        elif self.input.peek() in 'Oo':
            self.input.next()
            return self.subreader('number.octal', self.read_number_octal)

        elif self.input.peek() in string.digits + '.':
            return self.subreader('number.normal', self.read_number)

        else:
            return LexerToken('number', 0)
 
    def read_type_modifiers(self):
        accumulator = ''

        while True:
            if self.input.peek() in string.whitespace: self.input.next()
            elif self.input.peek() not in self.lang_specs.type_modifiers: break
            else: accumulator += self.input.next()

        return accumulator

    def read_type_or_identifier(self):
        accumulator = ''
        offset = 0

        fork = self.input.fork()
        paren = 0

        while True:
            if fork.peek() == '(':
                paren += 1

            elif fork.peek() == ')':
                paren -= 1
                if paren < 0:
                    accumulator = None
                    break

            if fork.peek() not in string.ascii_letters + string.digits + '_:' + '(,)' + self.lang_specs.type_modifiers and (fork.peek() not in string.whitespace or not paren): break

            if fork.peek() not in string.whitespace: accumulator += fork.next()
            else: fork.next()
                
            offset += 1

        if accumulator and self.is_type(accumulator):
            for _ in range(offset): self.input.next()
            return LexerToken('type', accumulator)

        return self.subreader('identifier', self.read_identifier)

    def is_type(self, name):
        if not name:
            return False

        elif name[-1] in self.lang_specs.type_modifiers:
            return self.is_type(name[:-1])

        elif re.match(r'.+?\(.*?\)', name):
            m = re.match(r'(.+?)\((.*?)\)', name)

            return_type = m.group(1)
            arg_types = [x for x in m.group(2).split(',') if x]
            
            return self.is_type(return_type) and all([self.is_type(a) for a in arg_types])

        else:
            return name in (x.name for x in self.lang_specs.types)

    def read_identifier(self):
        accumulator = ''
        real = ''
        offset = 0

        fork = self.input.fork()

        while True:
            if fork.peek() not in self.lang_specs.identifier_modifiers: break
            accumulator += fork.next()
            offset += 1

        while True:
            if fork.peek() not in string.ascii_letters + string.digits + '_:': break
            real += fork.next()
            offset += 1

        if not real:
            return LexerToken('operator', self.read_operator())

        for _ in range(offset):
            self.input.next()

        accumulator += real

        if accumulator in self.lang_specs.keywords:
            return LexerToken('keyword', accumulator)

        elif accumulator in self.lang_specs.values:
            return LexerToken('value', (accumulator, self.lang_specs.values[accumulator]))

        else:
            return LexerToken('identifier', accumulator)

    def read_operator(self):
        accumulator = ''

        while True:
            if not self.is_operator_char(self.input.peek()): break
            accumulator += self.input.next()

        return accumulator

    def is_operator_char(self, ch):
        return ch in '+-*/%=&|<>!@$'

    def is_punctuation(self, ch):
        ccode = ord(ch)
        
        return not (ccode <= 0x20 or ccode > 0x7E)

    def next_token(self):
        while True:
            if self.input.eof(): return

            next_char = self.input.peek()

            if next_char == '': return

            elif self.input.peek(length = 2) == '//':
                self.input.next()
                self.input.next()

                while self.input.peek() != '\n':
                    self.input.next()

            elif self.input.peek(length = 2) == '/*':
                self.input.next()
                self.input.next()
                
                while self.input.peek(length = 2) != '*/':
                    self.input.next()

            elif next_char in string.whitespace: self.input.next()
            elif next_char == '\"': yield self.subreader('string', self.read_string)
            elif next_char == '0': yield self.subreader('number.zero', self.read_number_zero)
            elif next_char in string.digits: yield self.subreader('number.normal', self.read_number)
            elif next_char in string.ascii_letters + '_:' + self.lang_specs.identifier_modifiers: yield self.subreader('identifiable', self.read_type_or_identifier)
            elif self.is_operator_char(next_char): yield self.subreader('operator', self.read_operator)
            elif self.is_punctuation(next_char):
                self.input.next()
                yield LexerToken('punctuation', next_char)

            else: self.input.error("Invalid character could not be handled: '{}'".format(next_char))

    def peek(self):
        curr = (self.input.pos, self.input.line, self.input.column)

        try:
            res = next(x for x in self.next_token() if x is not None)

        except StopIteration:
            res = None

        (self.input.pos, self.input.line, self.input.column) = curr

        return res

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        return next(x for x in self.next_token() if x is not None)

    @classmethod
    def lex(cls, data):
        lexer = cls()
        lexer.write(data)

        return iter(lexer)

def main():
    import sys

    data = sys.stdin.read()

    for x in FreLexer.lex(data):
        print(repr(x))

if __name__ == "__main__":
    main()            