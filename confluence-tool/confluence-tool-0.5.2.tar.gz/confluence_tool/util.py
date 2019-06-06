import yaml

def get_list_data(data):
    #print "data", data
    if isinstance(data, basestring):
        ac = []
        for doc in yaml.safe_load_all(data):
            if isinstance(doc, list):
                ac += doc
            else:
                ac.append(doc)
        data = ac
    if not isinstance(data, list):
        data = [ data ]
    #print "data", data
    return data

import pyaml, yaml

from pyaml import UnsafePrettyYAMLDumper

def represent_stringish(dumper, data):
    data = unicode(data) # read the comment above

    style = dumper.pyaml_string_val_style
    if not style:
        style = 'plain'

        if '\n' not in data and ('@' in data or '{' in data or '}' in data):
            style = "'"

        elif '\n' in data or not data or data == '-' or data[0] in '!&*[?':
            if 0:
                style = 'literal'
                if '\n' in data[:-1]:
                    for line in data.splitlines():
                        if len(line) > dumper.best_width: break
                else: style = '|'

            style = "|"

    return yaml.representer.ScalarNode('tag:yaml.org,2002:str', data, style=style)

for str_type in {bytes, unicode}:
    UnsafePrettyYAMLDumper.add_representer(
        str_type, represent_stringish )
