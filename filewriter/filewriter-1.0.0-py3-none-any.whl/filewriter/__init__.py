import collections
import json
import os

try:
    import django.conf.settings as settings

    variable = settings.READABLE_GLOBAL_VARIABLE_NAME
    globals()[settings.READABLE_GLOBAL_VARIABLE_NAME] = None
except Exception:
    variable = os.getenv("READABLE_GLOBAL_VARIABLE_NAME")
    if variable:
        globals()[variable] = None
    else:
        print("WARNING: You didn't set the environment variable "
              "READABLE_GLOBAL_VARIABLE_NAME. readable is created globally "
              "as the default variable.")
        globals()['readable'] = None

WRITER_DEFAULT_FILENAME = os.getenv('READABLE_GLOBAL_VARIABLE_NAME', "debug")


def get_filename(filename):
    if filename:
        if filename.endswith('.log'):
            return filename
        return f"{filename}.log"
    return f"{WRITER_DEFAULT_FILENAME}.log"


def parse_data(data, is_json=True):
    if is_json:
        return json.loads(data)
    return data


class Base:
    __slots__ = [
        "callback",
        "debug",
        "filename",
        "fopen_mode",
        "json",
    ]

    def __init__(
            self,
            fopen_mode,
            filename=WRITER_DEFAULT_FILENAME,
            debug=True,
            json=True,
            callback=None,
    ):
        self.debug = debug
        self.filename = get_filename(filename)
        self.fopen_mode = fopen_mode
        self.json = json
        self.callback = callback

    def parse_data(self, data):
        if self.json:
            return json.dumps(data)
        return data


class Writer(Base):
    def __init__(
            self,
            filename=WRITER_DEFAULT_FILENAME,
            debug=True,
            json=True,
            callback=None,
    ):
        super().__init__(
            "w+",
            filename=filename,
            debug=debug,
            json=json,
            callback=callback,
        )

    def __rshift__(self, other):
        filename = get_filename(self.filename)
        if (isinstance(other, list)
                or isinstance(other, set)
                or isinstance(other, collections.Iterable)):
            with open(filename, self.fopen_mode) as file:
                for data in other:
                    file.write(str(self.parse_data(data)))
                    if self.debug:
                        print(self.parse_data(data))

        with open(filename, self.fopen_mode) as file:
            file.write(self.parse_data(other))
            if self.debug:
                print(self.parse_data(other))

        if self.callback:
            self.callback(filename)


class Reader(Base):
    def __init__(
            self,
            filename=WRITER_DEFAULT_FILENAME,
            debug=True,
            json=True,
    ):
        super().__init__(
            "r",
            filename=filename,
            debug=debug,
            json=json,
        )

    def __new__(cls, item=WRITER_DEFAULT_FILENAME):
        return Reader._define(get_filename(item))

    @classmethod
    def _define(cls, filename, fopen_mode="r", debug=True, json=True):
        filename = get_filename(filename)
        file_data = []
        with open(filename, fopen_mode) as file:
            for line in file.readlines():
                data_line = line
                file_data.append(parse_data(data_line, is_json=json))
                if debug:
                    print(parse_data(data_line, is_json=json))
        global variable
        return file_data[0] if len(file_data) == 1 else file_data

    def __rshift__(self, other):
        if self.debug:
            print("WARNING: Doesn't make sense. If you think otherwise, create a PR.")
        pass
