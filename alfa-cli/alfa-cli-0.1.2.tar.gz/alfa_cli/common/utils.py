import os
import zipfile
from pathlib import Path


DEFAULT_EXCLUDES = [".git/*", ".gitignore", ".DS_Store"]


#


def zipdir(source, dest, *, excludes=[], includes=[], conf=None):
    if conf is not None:
        excludes, includes = extract_ignore_rules(conf)
    excludes, includes = parse_ignore_rules(excludes, includes)

    root = Path(source)
    files = set(root.glob("**/*"))

    flatten = lambda l: [item for sublist in l for item in sublist]
    excluded = set(flatten([root.glob(glob) for glob in excludes]))
    included = set(flatten([root.glob(glob) for glob in includes]))

    files = files - excluded | included
    files = [x for x in files if x.is_file()]

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            zf.write(file, file.relative_to(source))


def extract_ignore_rules(conf):
    excludes = []
    includes = []

    functions = conf.get("functions", [])
    for function in functions:
        if type(function) is dict:
            name = list(function.keys())[0]
            data = function.get(name)
        else:
            name = function
            data = functions.get(name)

        package = data.get("package")
        if package is None:
            continue

        to_exclude = ["{}/{}".format(name, x) for x in package.get("exclude", [])]
        to_include = ["{}/{}".format(name, x) for x in package.get("include", [])]
        excludes.extend(to_exclude)
        includes.extend(to_include)

    return excludes, includes


def parse_ignore_rules(excludes, includes):
    for glob in excludes:
        if glob.startswith("!"):
            excludes.remove(glob)
            includes.append(glob[1:])

    excludes = list(set(excludes + DEFAULT_EXCLUDES))
    includes = list(set(includes))

    # convert dir/** to dir/**/* (adds files instead of dirs)
    excludes = [x + "/*" if x.endswith("*") else x for x in excludes]
    includes = [x + "/*" if x.endswith("*") else x for x in includes]

    return excludes, includes

