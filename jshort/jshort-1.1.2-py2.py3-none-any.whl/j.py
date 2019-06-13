import sys
import ujson
from pygments import highlight, lexers, formatters
from jsonpath_ng import jsonpath, parse


class Jobj:
    def __init__(self, data):
        self._data = data

    def __getattr__(self, key):
        return Jobj(self._data.get(key))

    def __setitem__(self, key, value):
        try:
            ujson.dumps(value)
            self._data[key] = value
        except Exception:
            print("Unable to serialize value to json")

    def __getitem__(self, index):
        try:
            return self._data[index]
        except Exception:
            return None

    def __repr__(self):
        return f"<{str(self._data)[:20]}>"

    def __str__(self):
        """Generate a colored output string"""
        formatted_json = ujson.dumps(self._data, sort_keys=True, indent=2)
        colorful_json = highlight(
            formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()
        )
        return colorful_json

    @property
    def d_(self):
        return self._data

    @property
    def data_(self):
        return self.d_


class J:
    def __call__(
        self,
        d=None,
        data=None,
        i=None,
        input_path=None,
        o=None,
        output_path=None,
        indent=4,
    ):
        self.data = d or data
        self.input_path = i or input_path
        self.output_path = o or output_path
        self.indent = indent

        if self.data and self.output_path:
            with open(self.output_path, "w") as f:
                f.write(ujson.dumps(self.data, indent=indent))

        if self.input_path:
            with open(self.input_path) as f:
                self.data = ujson.load(f)

        return self

    def __str__(self):
        """Generate a colored output string"""
        if self.data:
            formatted_json = ujson.dumps(self.data, sort_keys=True, indent=self.indent)
            colorful_json = highlight(
                formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()
            )
            return colorful_json

    def __unicode__(self):
        return str(self)

    def __repr__(self):
        """Generate an informative representation of the object"""
        if self.input_path:
            return "<J(input_path={})>".format(self.input_path)
        if self.output_path:
            return "<J(output_path={})>".format(self.output_path)
        return self.obj.__repr__()

    def prt(self):
        print(self)

    @property
    def d(self):
        """Shorthand for property data"""
        return self.data

    def p(self, path):
        """Shorthand for method path"""
        return self.path(path)

    def path(self, path):
        """Traversing json using https://pypi.org/project/jsonpath-ng/"""
        try:
            result = [match.value for match in parse(path).find(self.data)]
            if len(result) == 1:
                return result[0]
            else:
                return result
        except Exception:
            return None

    @property
    def obj(self):
        return Jobj(self.d)


# Install the J() object in sys.modules so that "import j" gives a callable j.
sys.modules["j"] = J()
sys.modules["Jobj"] = Jobj

