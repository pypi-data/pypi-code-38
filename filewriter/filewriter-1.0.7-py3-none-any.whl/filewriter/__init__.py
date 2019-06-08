import collections
import json
import os

WRITER_DEFAULT_PLACEHOLDER = "readable"

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
              "READABLE_GLOBAL_VARIABLE_NAME. 'readable' is created globally "
              "as the default variable.")
        globals()[WRITER_DEFAULT_PLACEHOLDER] = None

WRITER_DEFAULT_FILENAME = os.getenv('READABLE_GLOBAL_VARIABLE_NAME', "debug")


class Reverse:
    __slots__ = [
        'item',
    ]

    def __init__(self, item):
        self.item = item

    def __rshift__(self, other):
        return other.__lshift__(self.item)

    def __lshift__(self, other):
        return other.__rshift__(self.item)


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
        "_shift",
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

    def __lshift__(self, other):
        filename = get_filename(self.filename)
        if (isinstance(other, list)
                or isinstance(other, set)
                or isinstance(other, collections.Iterable)):
            with open(filename, self.fopen_mode) as file:
                file_data = []
                for data in other:
                    line = self.parse_data(data)
                    file.write(str(line))
                    if self.debug:
                        print(line)
                    file_data.append(line)
        else:
            with open(filename, self.fopen_mode) as file:
                data = self.parse_data(other)
                file.write(data)
                if self.debug:
                    print(data)
                file_data =data
        if self.callback:
            self.callback(filename)

        return file_data


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
        data = file_data[0] if len(file_data) == 1 else file_data
        return data


class FReader(Base):
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

    def __rshift__(self, other):
        file_data = []
        with open(self.filename, self.fopen_mode) as file:
            for line in file.readlines():
                data_line = line
                file_data.append(parse_data(data_line, is_json=self.json))
                if self.debug:
                    print(parse_data(data_line, is_json=self.json))
        data = file_data[0] if len(file_data) == 1 else file_data
        global variable
        variable = data
        return data
