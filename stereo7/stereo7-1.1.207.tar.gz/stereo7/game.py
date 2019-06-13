import fileutils
import os


class _Cache:
    units = []
    units_path = {}


def get_units_list():
    if _Cache.units:
        return _Cache.units
    units = []
    all_files = []
    dirs = [
        '/Resources/ini/units/creep/',
        '/Resources/ini/units/tower/',
        '/Resources/ini/units/hero/',
        '/Resources/ini/units/',
        ]
    for dir_ in dirs:
        if os.path.isdir(fileutils.root_dir + dir_):
            files = fileutils.getFilesList(fileutils.root_dir + dir_, False)
            all_files.extend([fileutils.root_dir + dir_ + x for x in files])
    # if os.path.isdir(fileutils.root_dir + '/Resources/ini/units/tower/'):
    #     all_files.extend(fileutils.getFilesList(fileutils.root_dir + '/Resources/ini/units/tower/', False))
    # if os.path.isdir(fileutils.root_dir + '/Resources/ini/units/hero/'):
    #     all_files.extend(fileutils.getFilesList(fileutils.root_dir + '/Resources/ini/units/hero/', False))
    # all_files.extend(fileutils.getFilesList(fileutils.root_dir + '/Resources/ini/units/', False))
    for file in all_files:
        name = file
        name = name[name.rindex('/')+1:]
        if name.startswith('_'):
            continue
        if not name.endswith('.xml'):
            continue
        name = name[0: -4]
        if name in ['death', 'death2']:
            continue
        units.append(name)
        _Cache.units_path[name] = file
    _Cache.units = units
    return units


def get_units_path():
    get_units_list()
    return _Cache.units_path
