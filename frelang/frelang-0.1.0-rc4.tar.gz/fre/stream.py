class FreSyntaxError(BaseException):
    pass

class CharacterStream(object):
    def __init__(self):
        self.data = ""
        self.reset_positions()
        self.routine = None
        self.errored = False

    def write(self, data):
        self.data += data
        self.lines = self.data.split('\n')

    def reset_positions(self):
        self.pos = 0
        self.line = 1
        self.column = 0

    def get_line(self, l):
        return self.lines[l - 1]

    def set_data(self, data):
        self.data = data
        self.lines = self.data.split('\n')
        self.reset_positions()

    def fork(self):
        res = CharacterStream()

        res.set_data(self.data)

        res.line = self.line
        res.column = self.column
        res.pos = self.pos

        return res

    def call(self, routine, func, *args, **kwargs):
        old_routine = self.routine
        self.routine = routine

        res = func(*args, **kwargs)

        self.routine = old_routine
        return res

    def routine_name(self):
        if self.routine is None:
            return '(unknown)'

        else:
            return self.routine

    def error(self, message = ""):
        if self.errored:
            return

        print("[{}:{} @ {}] {}".format(self.line, self.column, self.routine_name(), message))
        self.errored = True

    def next(self):
        if len(self.data) <= self.pos:
            return None

        char = self.data[self.pos]

        if char == "\n":
            self.line += 1
            self.column = 0

        else:
            self.column += 1

        self.pos += 1

        # ignore carriage return characters
        while not self.eof() and self.data[self.pos] == "\r":
            self.pos += 1

        return char

    def peek(self, offset = 0, length = 1):
        if len(self.data) <= self.pos + offset:
            return None

        return self.data[self.pos + offset: self.pos + offset + length]

    def eof(self):
        return self.pos >= len(self.data)