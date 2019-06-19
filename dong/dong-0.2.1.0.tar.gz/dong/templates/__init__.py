
import os.path
import string
from pkgutil import get_data

def get_template(name):
    pkg_name = __name__.split(".", 1)[0]
    file_name = "{name}.template".format(name=name)
    data = get_data(pkg_name, os.path.join("templates", file_name))
    return string.Template(data.decode(encoding='utf8'))

def make_template(name, opts):
    template = get_template(name)
    return template.safe_substitute(opts)
