# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import fnmatch
import inspect
import tempfile
import os
import shutil
import hashlib
import sys
import traceback
import glob
import imp
import six
import Gui.wizard_helper_functions as whf
from collections import OrderedDict
from sympathy.utils.prim import localuri, nativepath
from sympathy.utils.parameter_helper import ParameterRoot
from sympathy.utils.parameter_helper_visitors import ReorderVisitor
from sympathy.platform import gennode
from sympathy.platform import version_support as vs
from sympathy.platform.exceptions import sywarn
from sympathy.platform import workflow_converter
from sympathy.utils.context import trim_doc
from sympathy.utils import tag
from sympathy.utils import library_info
from sympathy.utils import components

fs_encoding = sys.getfilesystemencoding()

pid = os.getpid()
hashings = 'md5', 'mtime'
hashing = hashings[0]


def hashstrings(strings):
    m = hashlib.md5()
    for string in strings:
        m.update(string)
    return m.hexdigest()


def library_package(library_root):
    """
    Return the Common package pointed to by the library.ini file.
    """
    package_name = library_info.instance()[
        library_root]['General']['common_path']
    package_name = os.path.basename(os.path.normpath(package_name))
    if len(package_name):
        return __import__(package_name)
    raise ImportError(
        'No common package found in library: "{}".'.format(library_root) +
        '\nThe library has been imported, but it is recommended to ' +
        'create this package in the library structure.' +
        '\nUse the Library Wizard to see an example of this.')


def check_file_for_classes(node):
    """
    Search a module and locate classes that are subclassed from gennode.Node.
    Returns list of located clases.
    """
    classes = []
    mod_name = os.path.basename(os.path.splitext(node)[0])
    node_path = vs.str_(os.path.dirname(node), vs.fs_encoding)
    if node_path not in sys.path:
        sys.path.append(node_path)

    if mod_name in sys.modules:
        members = OrderedDict(inspect.getmembers(sys.modules[mod_name]))
    else:
        with open(node, 'rb') as f:
            name = os.path.basename(vs.py_file(node.split('.')[-2]) +
                                    hashstrings([node.encode('utf8')]))
            path = node
            name = vs.str_(name.encode('ascii', errors='ignore'), 'ascii')
            mod_ = imp.load_source(name, vs.str_(path, vs.fs_encoding), f)
            members = OrderedDict(inspect.getmembers(mod_))

    for name, instance in [mod for mod in members.items()
                           if not mod[0].startswith('_')]:
        if inspect.isclass(instance) and issubclass(instance,
                                                    gennode.BasicNode):
            classes.append((mod_name, name, instance))
    return classes


NAME = 'name'
NODEID = 'nodeid'


def icon_dirs_path(icon, icon_dirs):
    for icon_dir in icon_dirs:
        icon_path = os.path.join(icon_dir, icon)
        if os.path.exists(icon_path):
            return icon_path


def get_properties(node, class_name, instance):
    """
    Return dictionary of select properties extracted from class instance.
    """
    def to_dict(params):
        try:
            return params.parameter_dict
        except AttributeError:
            return params

    top_level = (
        'author',
        'class',
        'copyright',
        'description',
        'file',
        'icon',
        NAME,
        NODEID,
        'type',
        'version')

    required_fields = (
        NAME,
        NODEID)

    translation_dict = {'nodeid': 'id', 'name': 'label'}

    members = dict(inspect.getmembers(instance))
    has_required = True
    properties = {}
    original = True

    # Mark classes that don't need to be validated.

    if 'verify_parameters' in members:
        original &= getattr(instance.verify_parameters, 'original', False)
    if 'verify_parameters_basic' in members:
        original &= getattr(
            instance.verify_parameters_basic, 'original', False)
    if 'verify_parameters_managed' in members:
        original &= getattr(
            instance.verify_parameters_managed, 'original', False)

    properties['validate'] = not original

    try:
        properties['parameters'] = {}
        parameters = members['parameters']
        properties['parameters']['data'] = to_dict(parameters)
        properties['parameters']['type'] = 'json'
        parameter_root = ParameterRoot(parameters)
        reorder_visitor = ReorderVisitor()
        parameter_root.accept(reorder_visitor)
    except:
        pass

    if 'tags' in members:
        try:
            properties['tags'] = members['tags'].to_dict()
        except:
            pass

    def plugin_data_base(plugin_cls):
        return {'class': plugin_cls.__name__, 'file':
                localuri(sys.modules[plugin_cls.__module__].__file__)}

    def plugin_data(plugin_cls):
        return {'class': plugin_cls.__name__, 'file':
                localuri(plugin_cls.__file__)}

    def plugins(plugin_cls):
        return [plugin_data(plugin_impl) for plugin_impl
                in components.get_components('plugin_*.py', plugin_cls)]

    if 'plugins' in members:
        properties['plugins'] = [
            {'interface': plugin_data_base(plugin_cls),
             'installed': plugins(plugin_cls)}
            for plugin_cls in members['plugins']]

    nodedir = os.path.dirname(node)
    for f in top_level:
        properties[f] = ''

    if not (members.get(NODEID) and members.get(NAME)):
        # Assuming that the node is a base class.
        return

    for origin, target in translation_dict.items():
        properties[target] = members[origin]

    for field in top_level:
        if field in members:
            properties[field] = members[field]
            if not isinstance(members[field], six.string_types):
                print('[{}] field {} is not a string'.format(node, field))
        elif field in required_fields:
            print('*** {0} is missing from {1}'.format(field, class_name))
            has_required = False

    field = '__doc__'
    doc = members.get(field)
    if doc:
        doc = trim_doc(doc)
    properties[field] = doc

    field = 'deprecated'
    deprecated = members.get(field)
    properties[field] = deprecated

    if not has_required:
        # When making a node be sure to include all require fields.
        return

    port_structure = {}
    properties['ports'] = port_structure
    group = False

    all_names = {}
    for field in ['inputs', 'outputs']:
        names = {}
        all_names[field] = names

        if field in members:
            member = members[field]
            member_data = [port.to_dict() for port in member]
            # Temporary restoration of indices.
            for i, port in enumerate(member_data):
                port['index'] = i
                name = port.get('name')

                type_ = port.get('type', None)
                if (isinstance(type_, tuple) and
                        "'sygroup'" in six.text_type(type_)):
                    group = True

                if name is not None and name in names:
                    print("*** {}: {} port names may not be reused".format(
                        class_name, field[:-1]))
                    return

                if name is not None:
                    names.setdefault(name, 0)
                    names[name] += 1

                    if name.startswith('__sy'):
                        print("*** {}: Port names starting with __sy are "
                              "reserved for internal use.".format(class_name))
                        return

                if 'n' in port:
                    if not name:
                        print("*** {}: When 'n' is used port name"
                              " need to be defined".format(class_name))
                        return

            port_structure[field] = member_data
        else:
            # Temporarily creating empty definition.
            port_structure[field] = []

        if group:
            if set(all_names.get('inputs', {})).intersection(
                    all_names.get('outputs', {})):
                print("*** {}: when template group is used, port names "
                      "need to be unique".format(
                          class_name))
                return

    # Check if we have a resource directory where icons could reside.
    icon = members.get('icon')
    if icon:
        icon_path = icon_dirs_path(
            icon, [os.path.join(nodedir, '_resources'), nodedir])
        if icon_path:
            properties['icon'] = localuri(icon_path)
        else:
            sywarn("Couldn't find icon for node {}".format(properties[NAME]))

    properties['type'] = 'python2'
    properties['file'] = localuri(node)
    properties['class'] = class_name
    return properties


def get_node_data(py_file):
    """
    Return a dictionary with the properties from each class in py_file.
    """
    return [(class_name, get_properties(py_file, class_name, instance))
            for (name, class_name, instance)
            in check_file_for_classes(py_file)]


def get_flow_data(syx_flow):
    properties = {}
    flow_dir = os.path.dirname(syx_flow)
    flow_name = os.path.basename(syx_flow)

    with open(syx_flow, 'rb') as f:
        flow_dict = workflow_converter.XMLToJson(f).dict()
        icon = flow_dict.get('icon')
        name = flow_dict.get('label') or flow_name
        properties['label'] = name

        if icon:
            icon_path = icon_dirs_path(icon, [flow_dir])
            if icon_path:
                properties['icon'] = localuri(icon_path)
            else:
                sywarn("Couldn't find icon for node {}".format(name))

        for key in ['author', 'copyright', 'description', 'version']:
            properties[key] = flow_dict.get(key)

        properties['file'] = localuri(syx_flow)
        properties['type'] = 'flow'
        properties['id'] = flow_dict['id']
        # Empty values to conform better to node-library interface.
        properties['ports'] = {}
        properties['parameters'] = {}
        properties['tags'] = [flow_dict.get('tag')]

    if flow_dict['id']:
        return [(flow_name, properties)]
    return []


def get_library(libraries, dirpath):
    """
    Return library matching dirpath, creating missing libraries.
    """
    for segment in dirpath.split(os.path.sep):
        try:
            library = libraries[segment]
            libraries = library[0]
        except KeyError:
            library = [{}, [], segment]
            libraries[segment] = library
            libraries = library[0]
    return library


def get_files(root):
    """
    Build tuple list of the relevant files.
    """
    result = []

    for dirpath, dirnames, filenames in os.walk(root, True):
        if dirpath == root:
            try:
                dirnames.remove('typealias')
            except ValueError:
                pass

        js_nodes = fnmatch.filter(filenames, '*.json')
        py_nodes = fnmatch.filter(filenames, 'node_*.py')
        syx_flows = fnmatch.filter(filenames, 'flow_*.syx')
        result.append((dirpath, js_nodes, py_nodes, syx_flows))
        result.sort()
    return result


def create_json_filename(name, dest):
    """
    Create a new json file with given properties at dest.
    Return the path to the new file.
    """
    return '{0}.json'.format(os.path.join(dest, name))


def create_json_file(name, props, dest):
    """
    Create a new json file with given properties at dest.
    Return the path to the new file.
    """
    js_node = create_json_filename(name, dest)

    with open(js_node, 'wb') as js_file:
        js_file.write(vs.encode(vs.json_dumps(
            props, indent=4, sort_keys=True,), 'utf8'))
    return js_node


def get_cache_path(cache, py_file):
    """
    Return the folder where json files for nodes that are defined in py_file
    will be stored.
    """
    res = None
    epy_file = py_file.encode('utf8')
    if hashing == 'md5':
        with open(py_file, 'rb') as f:
            res = os.path.join(
                cache, hashstrings([epy_file, f.read()]))
    elif hashing == 'mtime':
        mtime = six.text_type(os.path.getmtime(py_file))
        res = os.path.join(cache, hashstrings([epy_file, mtime]))
    else:
        assert False, 'Only md5 and mtime are supported.'

    return res


def get_cached_paths(cache, py_file):
    try:
        path = get_cache_path(cache, py_file)
        return [os.path.join(path, name) for name in os.listdir(path)]
    except:
        return None


def create_library_data_directory(library, temp, dirpath, js_nodes, py_nodes,
                                  syx_flows):
    """
    Create the nodes for a library directory. Can run in parallel for
    whatever gains that may bring.

    However for the current library the gain is small and therefore this
    is not run in parallel.

    Return list of js_node paths.
    """
    py_nodes = [os.path.join(dirpath, py_node)
                for py_node in py_nodes]
    syx_flows = [os.path.join(dirpath, syx_flow)
                 for syx_flow in syx_flows]
    js_nodes = [os.path.join(dirpath, js_node)
                for js_node in js_nodes
                if js_node != 'library.json']

    # Create json files from python node files.
    cache = os.path.join(temp, 'json')

    try:
        os.makedirs(cache)
    except (IOError, OSError):
        # Assume already existing.
        pass

    def create_js_cache(flodes, props_fun):
        for flode in flodes:
            # Attempt to get cached files.
            cached = get_cached_paths(cache, flode)
            if cached is not None:
                js_nodes.extend(cached)
            else:
                tempdir = None
                try:
                    tempdir = tempfile.mkdtemp(
                        prefix=str(os.getpid()), dir=cache)
                    js_dir = get_cache_path(cache, flode)
                    # Nothing cached, create files.
                    for name, props in props_fun(flode):
                        if props is not None:
                            create_json_file(name, props, tempdir)
                            js_nodes.append(create_json_filename(name, js_dir))

                    try:
                        os.rename(tempdir, js_dir)
                    except OSError:
                        # The directory seems to already exist. This means that
                        # another Sympathy instance created it just now, so we
                        # don't need to do anything here.
                        pass
                except:
                    print('Node error, failed to generate: {}'.format(flode))

                    # traceback.format_exc() gives a traceback encoded with
                    # fsencoding so we need to decode it.
                    print(vs.decode(traceback.format_exc(),
                                    fs_encoding))
                    try:
                        shutil.rmtree(tempdir)
                    except:
                        pass

    create_js_cache(py_nodes, get_node_data)
    create_js_cache(syx_flows, get_flow_data)
    return js_nodes


def create_library_data(root, temp):
    """
    Create a dictionary of the library data located while
    traversing the root structure.

    Create json files from python node files.
    Return library dictionary structure.
    """
    base = os.path.dirname(root)
    libraries = {}
    for dirpath, js_nodes, py_nodes, syx_flows in get_files(root):
        reldir = os.path.relpath(dirpath, base)
        library = get_library(libraries, reldir)
        library[1] = create_library_data_directory(
            root, temp, dirpath, js_nodes, py_nodes, syx_flows)
    return libraries[os.path.basename(root)]


def create_library_file(roots, temp):
    """
    Create library file and json files from python nodes.
    """
    def create_library(libraries, output):
        """
        Create transformed json library for writing to file.
        Avoid adding empty directories and Capitalize library names.
        """
        next_libraries, nodes, name = libraries
        output_libraries = []
        for key, value in next_libraries.items():
            library = create_library(value, {})
            if 'nodes' in library or 'libraries' in library:
                output_libraries.append(library)

        output['name'] = name
        if nodes:
            output['nodes'] = [localuri(nativepath(node)) for node in nodes]

        if output_libraries:
            output['libraries'] = sorted(
                output_libraries, key=lambda x: x['name'])
        return output

    result = {}
    library_data = {}
    nodes = []

    library_roots = {}

    for root_ in roots:
        root = os.path.normpath(os.path.join(root_, 'Library'))
        if not os.path.isdir(root):
            print('Error in library: "{}". '
                  'It does not contain required subdirectory called "Library" '
                  'containing nodes'.format(root_))
        else:
            try:
                library_, nodes_, name = create_library_data(root, temp)
                library_data.update(library_)
                nodes.extend(nodes_)
                for key in library_:
                    library_roots[key] = root
            except Exception as e:
                print('Error in library: "{}". It failed to generate '
                      'because of the following problem: "{}"'
                      .format(root_, e))
    library = create_library((library_data, nodes, 'Library'), result)

    for sub_library in library.get('libraries', []):
        sub_library['root'] = localuri(nativepath(
            library_roots[sub_library['name']]))
    return library


def create(source_dirs, temp, session):
    """Create library."""
    def create_tags(tagslist):
        tagslist = [tags() for tags in tagslist]
        if tagslist:
            return tag.LibraryTags.merge(tagslist).to_dict()
        return None

    def create_typealiases(typealiases):
        return {
            typealias.container_type.name():
            {'name': typealias.container_type.name(),
             'type': repr(typealias.container_type.get()),
             'icon': typealias.icon(),
             'util': '{}:{}'.format(typealias.__module__,
                                    typealias.__name__)}
            for typealias in typealiases}

    def create_missing_ini(library_root):
        info = whf.find_library_info(library_root)
        return whf.create_ini(library_root + '/' + whf.LIBRARY_INI, **info)

    def check_single_package(folder):
        pyfiles = os.path.join(folder, '*.py')
        pycfiles = os.path.join(folder, '*.pyc')
        initpy = os.path.join(folder, '*', '__init__.py*')
        initfiles = glob.glob(initpy)
        len_initfiles = len(initfiles)

        if glob.glob(pyfiles):
            sywarn('{} contains .py files'.format(folder))

        if glob.glob(pycfiles):
            sywarn('{} contains .pyc files'.format(folder))

        if len_initfiles == 2:
            pyfile, pycfile = sorted(initfiles)
            if not (len(pyfile) == len(pycfile) - 1 and
                    pyfile == pycfile[:-1]):
                sywarn('{} should contain only single package'.format(folder))
        elif len_initfiles > 2:
            sywarn('{} should contain only single package'.format(folder))

    types = []
    tags = []
    idents = {}
    ok_libraries = []

    for library in source_dirs:
        ok = False
        inipath = os.path.normpath(os.path.join(library, whf.LIBRARY_INI))
        library_info.create_library_info(inipath, library)

        try:
            package = library_package(library)
            try:
                types.extend(package.library_types())
            except AttributeError:
                pass
            try:
                tags.extend(package.library_tags())
            except AttributeError:
                pass
        except KeyError:
            sywarn('library.ini missing General:common_path option')
        except (IOError, OSError):
            success = create_missing_ini(library)
            message = (
                'library.ini was missing or cannot be read for library "' +
                library + '. ')
            if success:
                sywarn(message + 'It was however successfully created.')
            else:
                sywarn(message + 'Attempt to create it failed.')
        except ImportError as e:
            sywarn(e)
        except ValueError:
            ok = False
            sywarn('Library "' + library + '" could not be fully imported. '
                   u'Common_path should end with '
                   'slash followed by the package name.')
        else:
            ok = True
            try:
                ident = library_info.instance()[library][
                    'General']['identifier']
            except:
                ok = False
            else:
                if not ident:
                    sywarn(
                        'Ignoring library: "{}" which has no identifier.'
                        .format(library))
                    ok = False

                elif ident in idents:
                    sywarn(
                        'Ignoring library: "{}" which has same identifier: "{}" as '
                        '"{}" \n'
                        'Sympathy cannot use several different libraries with the '
                        'same identifier. '
                        .format(library, ident, idents[ident]))
                    ok = False

        if ok:
            ok_libraries.append(library)
            idents[ident] = library

    tags = create_tags(tags)
    types = create_typealiases(types)
    library = create_library_file(ok_libraries, temp)
    library['tags'] = tags
    library['typealiases'] = types
    return library


class LibraryCreator(object):
    name = 'Library Creator'
    empty_library = {'name': 'Library', 'libraries': [], 'tags': None}

    def create(self, library_dirs, temp_dir, session_dir):
        library = create(library_dirs, temp_dir, session_dir)
        if library is None:
            library = self.empty_library
        return library

    def source_file(self):
        return localuri(vs.py_file(__file__)).replace('.pyc', '.py')
