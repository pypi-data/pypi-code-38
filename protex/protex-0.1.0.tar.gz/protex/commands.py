from os.path import dirname, join, exists, normpath, expanduser, abspath
import json


class CommandPrototype:
    def __init__(self, name, expected_narg, template):
        self.name = name
        self.expected_narg = expected_narg
        self.template = template

    def tokens(self):
        i = 0
        mi = len(self.template)
        buff = []
        while i < mi:
            if self.template[i] == '%':
                if buff:
                    yield ''.join(buff)
                    buff.clear()
                if i == mi - 1 or self.template[i + 1] == '%':
                    yield '%'
                    i += 1
                else:
                    i += 1
                    while i < mi and self.template[i].isdigit():
                        buff.append(self.template[i])
                        i += 1
                    if buff:
                        k = int(''.join(buff))
                        if k == 0:
                            yield self.name
                        elif k <= self.expected_narg:
                            yield k - 1
                        else:
                            raise ValueError('Template {} is broken.'
                                             .format(self.name))
                    else:
                        yield '%'
                    buff.clear()
            else:
                buff.append(self.template[i])
                i += 1
        if buff:
            yield ''.join(buff)


class PrintOnePrototype(CommandPrototype):
    def __init__(self, name):
        self.name = name
        self.expected_narg = 1

    def tokens(self):
        yield 0


class PrintNamePrototype(CommandPrototype):
    def __init__(self, name):
        self.name = name
        self.expected_narg = 0

    def tokens(self):
        yield self.name


class DiscardPrototype(CommandPrototype):
    def __init__(self, name):
        self.name = name
        self.expected_narg = 1000

    def tokens(self):
        yield from ()  # empty generator


class IllformedCommandJSON(ValueError):
    pass


class CommandDict:
    def __init__(self, command_dict, default_proto=None):
        self.dict = command_dict
        self.default = default_proto

    @classmethod
    def from_file(cls, filename, default_proto=None):
        commands = {}
        with open(filename) as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise IllformedCommandJSON()

            specials = {
                'print_one': PrintOnePrototype,
                'print_name': PrintNamePrototype,
                'discard': DiscardPrototype
            }

            for key, proto in specials.items():
                if key in data and isinstance(data[key], (tuple, list)):
                    for cmd in data[key]:
                        if not isinstance(cmd, str):
                            raise IllformedCommandJSON()
                        commands[cmd] = proto(cmd)

            if 'other' in data and isinstance(data['other'], dict):
                for cmd in data['other']:
                    if not (isinstance(cmd, str)
                            and isinstance(data['other'][cmd], (list, tuple))
                            and len(data['other'][cmd]) == 2
                            and isinstance(data['other'][cmd][0], int)
                            and isinstance(data['other'][cmd][1], str)):
                        raise IllformedCommandJSON()
                    commands[cmd] = CommandPrototype(cmd, *data['other'][cmd])
        return cls(commands, default_proto)

    def update(self, other):
        self.dict.update(other.dict)

    def get(self, name):
        return self.dict.get(name, self.default(name))


class NoCommandFileFoundError(FileNotFoundError):
    pass


def command_file_seek(start_dir, file_name='commands.json', hidden_name=None):
    if hidden_name is None:
        hidden_name = '.' + file_name

    files = []

    current_dir = abspath(normpath(start_dir))
    while current_dir != '/':
        hf = join(start_dir, hidden_name)
        if exists(hf):
            files.append(hf)
        current_dir = dirname(current_dir)

    user = join(expanduser('~'), hidden_name)
    if exists(user):
        files.append(user)

    default = join(dirname(__file__), file_name)
    if exists(default):
        files.append(default)

    if not files:
        raise NoCommandFileFoundError("No command file have been found.")

    return reversed(files)


def load_all_files(name='commands.json', default_proto=DiscardPrototype):
    files = command_file_seek('.', file_name=name)

    commands = CommandDict({}, default_proto)
    for f in files:
        new = CommandDict.from_file(f)
        commands.update(new)

    return commands
