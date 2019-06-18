import argparse
import ast
import os
import sys
import fileinput

MANIFEST_FILES = ['__odoo__.py', '__openerp__.py', '__terp__.py', '__manifest__.py']


def is_module(path):
    """return False if the path doesn't contain an odoo module, and the full
    path to the module manifest otherwise"""

    if not os.path.isdir(path):
        return False
    files = os.listdir(path)
    filtered = [x for x in files if x in (MANIFEST_FILES + ['__init__.py'])]
    if len(filtered) == 2 and '__init__.py' in filtered:
        return os.path.join(
            path, next(x for x in filtered if x != '__init__.py'))
    else:
        return False


def is_installable_module(path):
    """return False if the path doesn't contain an installable odoo module,
    and the full path to the module manifest otherwise"""
    manifest_path = is_module(path)
    if manifest_path:
        manifest = ast.literal_eval(open(manifest_path).read())
        if manifest.get('installable', True):
            return manifest_path
    return False


def get_modules(paths):
    res = []
    for path in paths:
        if not os.path.isdir(path):
            continue
        module_paths = list(
            map(lambda module: os.path.join(path, module),
                os.listdir(path))
        )
        modules = [
            module for module in module_paths if
            is_installable_module(module)
        ]
        res.extend(modules)
    return res


def is_addons(path):
    return bool(get_modules([path]))


def get_addons(paths, ignore_deps=False):
    """Walks a path a returns all the addons inside sorted according to its
    dependencies.

    :param path: The path to walk
    :type path: str

    :param ignore_deps: Whether to take into account the repositories'
    dependencies or not
    :type ignore_deps: bool

    :returns: All the found addons
    :rtype: list
    """
    addons = {}
    for path in paths:
        if not os.path.isdir(path):
            continue
        if is_addons(path):
            addons[path] = []
        for base, dirs, files in os.walk(path):
            dir_paths = [os.path.join(base, directory) for directory in dirs]
            addons.update({
                directory: [] for directory in dir_paths if
                is_addons(directory)
            })
    if ignore_deps:
        return addons
    for path in addons:
        addons[path] = get_dependencies(path)
    sorted_addons = get_sorted_addons_by_level(addons)
    return sorted_addons


def get_dependencies(path):
    """Gets the dependencies of an addon reading the `oca_dependencies.txt` file.

    :param path: The addon path
    :rtype: str

    :returns: The dependency list
    :rtype: list
    """
    deps = []
    dep_path = os.path.join(path, 'oca_dependencies.txt')
    try:
        with open(dep_path) as dep:
            for line in dep:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                deps.append(line.split()[0])
    except IOError:
        return []
    return deps


def get_sorted_addons_by_level(addons):
    """Sorts a list of addons according to its level, and followed
    by its dependencies also sorted by level.

    It first sorts the addons using `sort_addons_by_level` and then
    it puts the dependencies after their parents. This to keep the addons
    with higher dependency level first and then its addons also sorted by
    level.

    :param addons: The addons with their dependencies.
    :type addons: dict

    :returns: The addons sorted by level
    :rtype: list

    Example::

        get_sorted_addons_by_level({
            "e": [],
            "r": ["x"],
            "c": [],
            "t": ["r", "c"],
            "x": ["e"],
        })

    Returns::

        ["t", "r", "c", "x", "e"]

    """
    sorted_addons = []
    addons_by_deps = sort_addons_by_level(addons)
    addons_by_deps = sorted(addons_by_deps.keys(),
                            key=lambda dep, addons=addons_by_deps: -addons.get(dep))
    for addon in addons_by_deps:
        if addon not in sorted_addons:
            sorted_addons.append(addon)
        for dep in addons.get(addon, []):
            dep_addon = os.path.join(os.path.dirname(addon), dep)
            if dep_addon not in sorted_addons:
                sorted_addons.append(dep_addon)
    return sorted_addons


def sort_addons_by_level(addons, _key=False, _res=False):
    """Reads a dict of addons with dependencies and assigns a "level" that represents
    how deep its dependencies go.

    :param addons: The addons with their dependencies.
    :type addons: dict

    :param _key: This is for recursion purposes. Do not pass when calling from the outside.
    :param _res: This is for recursion purposes. Do not pass when calling from the outside.

    :returns: The addons with the level
    :rtype: dict

    Example::

        sort_addons_by_level({
            "e": [],
            "r": ["x"],
            "c": [],
            "t": ["r", "c"],
            "x": ["e"],
        })

    Returns::

        {
            "t": 3,
            "r": 2,
            "x": 1,
            "c": 0,
            "e": 0,
        }

    In this example "t" depends on "r" that depends on "x" that depends on "e".
    There are three "levels" of dependencies below "t".
    """
    _res = _res or {}
    if not _key:
        for _key in addons:
            _res.update(sort_addons_by_level(addons, _key, _res))
        return _res
    if _res.get(_key, -1) > -1:
        return _res
    _res[_key] = 0
    for dep in addons.get(_key, []):
        _res.update(sort_addons_by_level(
            addons, os.path.join(os.path.dirname(_key), dep), _res))
    _res[_key] = (max([
        _res.get(os.path.join(os.path.dirname(_key), dep), -1)
        for dep in addons.get(_key, [])
    ] or [-1]) + 1)
    return _res


parser = argparse.ArgumentParser(
    description="Given a list  of paths, finds and returns a list of valid addons."
)
parser.add_argument(
    '-m', help="Only look for installable modules in the specified paths",
    action='store_true')
parser.add_argument(
    '-e', required=False,
    help='Comma separated list of modules to exclude'
)
parser.add_argument(
    '--ignore-deps', action='store_true',
    help=('Ignore the oca_dependencies of the repostories and generate the'
          ' addons path using the available modules')
)
parser.add_argument(
    '--odoo-addons', required=False, default='/home/odoo/instance/odoo/addons',
    help='Path where the odoo addons are located, defaults to /home/odoo/instance/odoo/addons'
)
parser.add_argument(
    'paths', metavar='PATH',
    help="Comma separated list of paths where the addons are"
)


def main():
    args = parser.parse_args()
    list_modules = args.m
    exclude_modules = args.e.split(',') if args.e else []
    paths = args.paths.split(',')
    if list_modules:
        addons_path = get_modules(paths)
    else:
        addons_path = get_addons(paths, args.ignore_deps)
    res = [module for module in addons_path if module not in exclude_modules]
    enterprise_path = [path for path in res if os.path.basename(path) == 'enterprise']
    if enterprise_path:
        res.remove(enterprise_path[0])
    addons_path = ",".join(enterprise_path + [args.odoo_addons] + res)
    for line in fileinput.input('/home/odoo/.openerp_serverrc', inplace=True):
        if 'addons_path' in line:
            parts = line.split('=')
            new_str = '{field} = {addons}'.format(field=parts[0].strip(), addons=addons_path)
            print(new_str.replace('\n', ''))
        else:
            print(line.replace('\n', ''))


if __name__ == "__main__":
    sys.exit(main())
