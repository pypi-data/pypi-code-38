import re, pkg_resources

def e_onegin_as_lines():
    path = pkg_resources.resource_filename(__name__, "onegin.txt")
    with open(path, 'rt') as src:
        for line in src:
            x = re.findall(r'\b\w+\b', line, re.I)
            if len(x) > 0:
                yield [y.lower() for y in x]