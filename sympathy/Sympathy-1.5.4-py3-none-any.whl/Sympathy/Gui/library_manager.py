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
import os
import sys
import shutil
import json
import glob
import re
import io
import subprocess
import distutils.dir_util
import distutils.file_util
import logging
import threading
import six
import base64
from collections import OrderedDict

from . import task_worker
from . import library_creator
from . import version
from sympathy.platform import workflow_converter
from sympathy.platform import os_support
from sympathy.platform import version_support as vs
from sympathy.platform import node_result
from sympathy.utils.prim import (
    group_pairs, ungroup_pairs, fuzzy_filter, concat, uri_to_path, unipath)
from sympathy.utils.parameter_helper import ParameterRoot
from sympathy.utils.parameter_helper_visitors import ShowParameterVisitor
from sympathy.utils.context import indent_doc
from sympathy.utils import library_info

core_logger = logging.getLogger('core')
core_perf_logger = logging.getLogger('core.perf')
_fs_encoding = sys.getfilesystemencoding()

LABEL = 'label'


def library_by_json(library_json_filename):
    """Return the library from library_json_filename."""
    with open(library_json_filename) as library_json_file:
        return json.load(library_json_file)


def library_json_filenames(library_json):
    libraries = [library_json_filenames(child_library)
                 for child_library in library_json.setdefault('libraries', [])]
    return library_json.setdefault('nodes', []) + concat(libraries)


def library_node_filenames(library_json):
    library_json_filenames_ = library_json_filenames(library_json)
    result = []
    for library_json_filename in library_json_filenames_:
        path = uri_to_path(library_json_filename)
        with open(path) as node_file:
            try:
                node = json.load(node_file)
                result.append(uri_to_path(node['file']))
                for plugin in node.get('plugins', []):
                    for installed in plugin['installed']:
                        result.append(uri_to_path(installed['file']))
            except Exception:
                print('Failed processing node:{0}'.format(path))
    return result


def library_by_key(library_json, key_function):
    """
    Return library with nodes organized by keys provided by key_function.

    key_function is a function taking two arguments, the first being
    the list of library names, and the second being the node dictionary.
    The keys generated should probably be, but is not required to be, unique.

    The result is a list of key value pairs.
    """
    def inner(library, path, result, root=None):
        path += [library['name']]
        if 'root' in library:
            root = library['root']

        if 'nodes' in library:
            for node_json_filename in library['nodes']:
                try:
                    with open(uri_to_path(
                            node_json_filename)) as node_json_file:
                        node = json.load(
                            node_json_file, object_pairs_hook=OrderedDict)
                        result.append((key_function(path, node), node))
                        if root is not None:
                            node['library'] = root
                except Exception:
                    core_logger.warn('Failed to process library node %s',
                                     node_json_filename)
        if 'libraries' in library:
            for library in library['libraries']:
                inner(library, path, result, root)
    result = []
    if library_json is not None:
        inner(library_json, [], result)

    return result


def library_by_nodeid(library_json):
    """Return library with nodes organized by nodeid."""
    def key_function(path, node):
        return node['id']
    return dict(library_by_key(library_json, key_function))


def library_tags(library_json):
    return library_json.get('tags', None) if library_json else None


def library_by_name(library_json):
    """
    Return library with nodes organized by library node name.
    The result is a list of key-value pairs.
    """
    def key_function(path, node):
        return node['label']
    return library_by_key(library_json, key_function)


def library_find_by_field(library_nodeid, fieldkeys):
    """
    Return library with nodes organized by key value.

    Using field names from fieldkeys which is a list of keys, the nodes will be
    searched.

    The result is a list of key value pairs.
    """
    def inner(node, key, value, fieldkeys, result):
        if not fieldkeys:
            try:
                result.append((six.text_type(value), node))
            except Exception:
                return []
        else:
            try:
                current = fieldkeys[0]
                remaining = fieldkeys[1:]
                if current is None:
                    items = value.items()
                else:
                    items = [(current, value[current])]
                for key, next_value in items:
                    inner(node, key, next_value, remaining, result)
            except Exception:
                return []

    result = []
    for nodeid, value in library_nodeid.items():
        inner(value, nodeid, value, fieldkeys, result)
    return result


def library_by_field_list(library_nodeid, fieldkeys):
    """
    Return library with nodes organized by key value.

    Using field names from fieldkeys which is a list of keys, the nodes will be
    searched.

    The result is a dictionary of all where the values are lists containing all
    matches.
    """
    return dict(group_pairs(
        library_find_by_field(library_nodeid, fieldkeys)))


class RstMaker(object):
    """
    Used to generate rst files from a library.
    These are used by Sphinx to generate documentation.
    """
    _cache = {}

    @classmethod
    def file_cache_clear(cls):
        cls._cache.clear()

    @classmethod
    def file_cache(cls):
        return set(cls._cache)

    CONFIG = """# -*- coding: utf-8 -*-
#
# Sympathy documentation build configuration file, created by
# sphinx-quickstart on Mon Mar 12 09:40:09 2013.
#
# This file is execfile() with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys, os, time
import six
import warnings

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# Making sure that required modules are mocked if they are not available for
# importing (this requires the mock, module).
required_modules = [
    'PySide',
    'PySide.QtGui',
    'PySide.QtCore',
    'h5py',
    'matplotlib',
    'matplotlib.backends',
    'matplotlib.backends.backend_agg',
    'matplotlib.backends.backend_qt4agg',
    'matplotlib.colors',
    'matplotlib.lines',
    'matplotlib.axes',
    'matplotlib.dates',
    'matplotlib.figure',
    'matplotlib.font_manager',
    'matplotlib.transforms',
    'mpl_toolkits',
    'mpl_toolkits.axes_grid1',
    'mpl_toolkits.mplot3d',
    'numpy',
    'numpy.random',
    'pandas',
    'ply',
    'pyodbc',
    'pywintypes',
    'win32api',
    'win32con',
    'win32file',
    'win32job',
    'win32process',
    'scipy',
    'scipy.interpolate',
    'scipy.signal',
    'scipy.weave',
    'sklearn',
    'skimage',
    'spyderlib',
    'spyderlib.qt',
    'spyderlib.qt.QtGui',
    'spyderlib.plugins',
    'spyderlib.plugins.variableexplorer',
    'spyderlib.widgets',
    'spyderlib.widgets.externalshell',
    'spyderlib.widgets.externalshell.pythonshell',
    'dateutil',
    'dateutil.parser']

try:
    from mock import MagicMock
except ImportError:
    pass
else:
    for mod_name in required_modules:
        try:
            # Ignore a warning from numpy>=1.14 when importing h5py<=2.7.1:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                __import__(mod_name)
        except ImportError:
            sys.modules[mod_name] = MagicMock()


paths = {PATHS}

fs_encoding = sys.getfilesystemencoding()

try:
    confdir = os.path.dirname(__file__).decode(fs_encoding)
except Exception:
    confdir = os.path.dirname(__file__)


sys.path[:] = sys.path + [os.path.normpath(os.path.join(confdir, path)
    if not os.path.isabs(path) else path)
    for path in paths]

if six.PY2:

    def encode_unicode(path, encoding):
         if isinstance(path, six.text_type):
             return path.encode(fs_encoding)
         else:
             return path

    sys.path[:] = [encode_unicode(path, fs_encoding) for path in sys.path]

    import docutils.writers.html4css1 as html4css1
    Html = html4css1.HTMLTranslator
    encode = Html.encode

    def encode_monkeypatch(self, text):
        try:
            return encode(self, text)
        except UnicodeDecodeError:
            return encode(self, text.decode(fs_encoding))

    Html.encode = encode_monkeypatch


# For ensuring that everything fails when sympathy cannot be imported.
import sympathy

# -- General configuration ----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon']

try:
    import sphinx.ext.imgmath
    extensions.extend([
        'sphinx.ext.imgmath'])
except ImportError:
    extensions.extend([
        'sphinx.ext.pngmath',
        'sphinx.ext.mathjax'])

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Sympathy'
copyright = u'2013-%s, <a href="https://www.sympathyfordata.com/">Combine Control Systems AB</a>. All Rights Reserved' % time.strftime('%Y')

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '{major_version}.{minor_version}'
# The full version, including alpha/beta/rc tags.
release = '{version}'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# We need to exclude __library_description.rst files lest sphinx should give
# warnings about them not being included in the toctree.
exclude_patterns = ['build', '**/__library_description.rst']

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# A dictionary of external documentations that we might want to link to.
# intersphinx_mapping = dict([
#     ('python', ('http://docs.python.org/2', None)),
#     ('numpy', ('http://docs.scipy.org/doc/numpy/', None)),
#     ('scipy', ('http://docs.scipy.org/doc/scipy/reference/', None)),
#     ('matplotlib', ('http://matplotlib.sourceforge.net/', None))])

# -- Options for HTML output --------------------------------------------------

html_theme = 'alabaster'
html_theme_options = dict(logo_name=True)

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = 'src/application.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = 'src/favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
html_sidebars = dict()

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = dict()

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'Sympathydoc'
"""

    INDEX = """
Sympathy for Data
=================

Welcome to the documentation for *Sympathy for Data*.

:Project page: `https://www.sympathyfordata.com <https://www.sympathyfordata.com>`_
:Author: `Combine Control Systems AB <https://www.sympathyfordata.com/>`_


Getting started
---------------
Want to learn more about what Sympathy for Data is and what it can do for you?

.. toctree::
   :maxdepth: 2

   src/about_sympathy.rst
   src/installation.rst
   src/first_steps.rst


Important Concepts
------------------

.. toctree::
   :maxdepth: 2

   src/concepts.rst
   src/subflows.rst
   src/functions.rst


Graphical user interface
------------------------

.. toctree::
   :maxdepth: 2

   src/gui.rst

Command line options
--------------------

.. toctree::
   :maxdepth: 2

   src/batch.rst


Development
-----------
Learn how to write nodes and more.

.. toctree::
   :maxdepth: 2

   src/nodewriting.rst
   src/advanced_nodewriting.rst
   src/debugging_nodes.rst
   src/writing_good_nodes.rst
   src/pluginwriting.rst
   src/create_type.rst
   src/python3.rst
   src/interactive.rst


API Reference
-------------

.. toctree::
   :maxdepth: 2

   src/node_reference.rst
   src/parameter_helper_reference.rst
   src/type_apis.rst


.. _Library:

Libraries
---------
Documentation for each type of node in the standard library of Sympathy for
Data as well as in any third-party libraries. Right-clicking on any node in the
GUI and choosing *Help* will bring you to the help page for that specific node.

.. toctree::
   :maxdepth: 2

   src/typical_workflow_structure.rst

   src/machinelearning.rst

   src/Library/index.rst


Changes
-------

.. toctree::
   :maxdepth: 2

   src/news.rst
   src/deprecations.rst

"""

    PLUGIN = """
.. _ `{PLUGIN_NAME}`

{PLUGIN_NAME}`
{UNDERLINE}

.. automodule:: {CLASS_NAME}

"""

    LIBRARY = """
.. _`lib_{LIBRARY_NAME}`:

{LIBRARY_NAME}
{UNDERLINE}

{DESCRIPTION}

.. toctree::
   :maxdepth: 2

{LIBRARIES}
{NODES}
{PLUGINS}

"""

    NODE_PLUGINS = """
.. _`{NODE_NAME}`:

.. _`{NODE_ID}`:

{NODE_NAME}
{UNDERLINE}

{NODE_ICON}

{NODE_DOC}

{NODE_PORTS}

{NODE_PARAMS}

.. automodule:: {MODULE_NAME}

.. class:: {CLASS_NAME}

{NODE_EXAMPLES}

Plugins
#######

{PLUGIN_LINKS}

"""

    EXAMPLES = """
Example flows
#############

{EXAMPLE_LINKS}

"""

    NODE = """
.. _`{NODE_NAME}`:

.. _`{NODE_ID}`:

{NODE_NAME}
{UNDERLINE}

{NODE_ICON}

{NODE_DOC}

{NODE_PORTS}

{NODE_PARAMS}

.. automodule:: {MODULE_NAME}

.. class:: {CLASS_NAME}

{NODE_EXAMPLES}

"""

    FLOW = """
.. _`{NODE_NAME}`:

.. _`{NODE_ID}`:

{NODE_NAME}
{UNDERLINE}
{NODE_ICON}

{NODE_DESC}

{NODE_PORTS}

{NODE_EXAMPLES}

"""
    PLUGINS = """

Plugins
~~~~~~~

.. toctree::

{PLUGINS}
"""

    PLUGIN = """
.. _`{CLASS_NAME}`:

{CLASS_NAME}
{UNDERLINE}

.. py:currentmodule:: {MODULE_NAME}

.. autoclass:: {CLASS_NAME}

"""

    @classmethod
    def _add_to_cache(cls, filename):
        cls._cache[os.path.abspath(filename)] = None

    @classmethod
    def _write_cached(cls, filename, text):
        cls._add_to_cache(filename)
        cached = False
        try:
            with io.open(filename, 'r',
                         encoding='utf8') as f:
                if f.read() == text:
                    cached = True
        except (IOError, OSError):
            pass

        if not cached:
            with io.open(filename, 'w',
                         encoding='utf8') as f:
                f.write(text)

    @classmethod
    def process_plugin(cls, path, plugin):
        class_name = plugin['class']
        class_filename = os.path.join(path, class_name + '.rst')
        file_ = uri_to_path(plugin['file'])
        module_name = os.path.splitext(os.path.basename(file_))[0]
        cls._write_cached(class_filename,
                          cls.PLUGIN.format(CLASS_NAME=class_name,
                                            MODULE_NAME=module_name,
                                            UNDERLINE=('~' * len(class_name))))
        return class_filename[len(path) + len(os.sep):]

    @classmethod
    def process_plugins(cls, path, plugins):

        def to_uri(path):
            return '/'.join(path.split(os.path.sep))

        def indented_sequence(indent, sequence):
            return [' ' * indent + elem for elem in sequence]

        plugin_directory_name = 'plugin'
        plugin_directory = os.path.join(path, plugin_directory_name)
        try:
            os.mkdir(plugin_directory)
        except (IOError, OSError):
            pass

        plugin_uris = []

        for plugin in sorted(plugins.values(), key=lambda x: x['class']):
            plugin_uris.append(
                to_uri(os.path.join(
                    plugin_directory_name,
                    cls.process_plugin(plugin_directory, plugin))))

        class_filename = os.path.join(path, 'plugins.rst')
        cls._write_cached(
            class_filename,
            cls.PLUGINS.format(
                PLUGINS='\n'.join(indented_sequence(3, plugin_uris))))
        return class_filename[len(path) + len(os.sep):]

    @classmethod
    def process_node(cls, path, node_filename, all_plugins,
                     example_flows):

        def format_examples(node_id):
            examples = example_flows.get(node_id)
            res = ''
            if examples:
                res = cls.EXAMPLES.format(
                    EXAMPLE_LINKS='\n'.join(
                        '* :download:`{basename} <{filename}>`'.format(
                            basename=example[1] or os.path.basename(
                                example[0]),
                            filename=example[0])
                        for example in examples))
            return res

        def icon_path(icon_path, file_path, rel=True):
            if os.path.exists(icon_path):
                if rel:
                    icon = unipath(os.path.relpath(
                        icon_path, os.path.dirname(file_path)))
                else:
                    # TODO(erik): this case is somehow needed for icons in
                    # _resources folders. Remove the need and this case.
                    icon = os.path.basename(icon_path)
                return '.. image:: {}\n   :width: 48\n'.format(icon)
            return ''

        with open(uri_to_path(node_filename)) as node_file:
            try:
                node = json.load(node_file)
                name = node['label']
                type_ = node['type']
                node_id = node['id']
                desc = node['description'] or ''
                file_ = uri_to_path(node['file'])
                icon = uri_to_path(node.get('icon', ''))

                if type_ == 'flow':
                    ports = ''
                    icon = icon_path(icon, file_)

                    with open(file_, 'rb') as f:
                        flow_dict = workflow_converter.XMLToJson(f).dict()

                        port_dict = flow_dict.get('ports', [])
                        port_list = [
                            ('Input', port_dict.get('inputs', [])),
                            ('Output', port_dict.get('outputs', []))]

                        ports = u'\n\n'.join([
                            u'*{} ports*\n{}'.format(
                                group_key,
                                '\n'.join([
                                    u'    :{}: {}'.format(port['name'],
                                                          port['type'])
                                    for port in group_val]))
                            for group_key, group_val in port_list
                            if group_val])

                    data = cls.FLOW.format(
                        NODE_ID=node_id,
                        NODE_NAME=name,
                        NODE_ICON=icon,
                        NODE_DESC=desc,
                        NODE_PORTS=ports,
                        NODE_EXAMPLES=format_examples(node_id),
                        UNDERLINE=('~' * len(name)))
                    class_filename = os.path.join(
                        path, os.path.basename(file_) + '.rst')
                else:
                    icon = icon_path(icon, file_, False)
                    class_name = node['class']
                    node_id = node['id']
                    class_filename = os.path.join(path, class_name + '.rst')
                    module_name = os.path.splitext(os.path.basename(file_))[0]

                    doc = node.get('__doc__')

                    plugins = node.get('plugins', [])
                    formatted_plugins = '\n'.join([
                        '* :ref:`{}`'.format(installed['class'])
                        for plugin in plugins
                        for installed in plugin['installed']])

                    for plugin in plugins:
                        for installed in plugin['installed']:
                            all_plugins[installed['class']] = installed

                    show = ShowParameterVisitor()
                    parameters = ParameterRoot(
                        node.get('parameters', {}).get('data', {})).accept(
                            show)
                    parameters = show.result
                    port_dict = node.get('ports', [])
                    port_list = [
                        ('Input', port_dict.get('inputs', [])),
                        ('Output', port_dict.get('outputs', []))]

                    ports = '\n\n'.join([
                        '*{} ports*:\n{}'.format(
                            group_key,
                            '\n'.join([
                                '    :{}: {}\n\n'
                                '        {}'.format(
                                    port.get('name') or '<unnamed>',
                                    port['type'],
                                    port['description'])
                                for port in group_val]))
                        for group_key, group_val in port_list if group_val])

                    parameters = '*Configuration*:\n{}'.format(
                        indent_doc(parameters, 4))

                    if plugins:
                        data = cls.NODE_PLUGINS.format(
                            CLASS_NAME=class_name,
                            MODULE_NAME=module_name,
                            NODE_NAME=name,
                            NODE_ID=node_id,
                            NODE_DOC=doc,
                            NODE_ICON=icon,
                            NODE_PORTS=ports,
                            NODE_EXAMPLES=format_examples(node_id),
                            NODE_PARAMS=parameters,
                            UNDERLINE=('~' * len(name)),
                            PLUGIN_LINKS=formatted_plugins)
                    else:
                        data = cls.NODE.format(CLASS_NAME=class_name,
                                               MODULE_NAME=module_name,
                                               NODE_NAME=name,
                                               NODE_ID=node_id,
                                               NODE_DOC=doc,
                                               NODE_ICON=icon,
                                               NODE_PORTS=ports,
                                               NODE_EXAMPLES=format_examples(
                                                   node_id),
                                               NODE_PARAMS=parameters,
                                               UNDERLINE=('~' * len(name)))

                cls._write_cached(class_filename, data)
                return class_filename[len(path) + len(os.sep):]
            except Exception:
                print('Failed generating node:{0}'.format(node_filename))
                return 'missing'
            else:
                if plugins:
                    data = cls.NODE_PLUGINS.format(
                        CLASS_NAME=class_name,
                        MODULE_NAME=module_name,
                        NODE_NAME=name,
                        NODE_ICON=icon,
                        UNDERLINE=('~' * len(name)),
                        PLUGIN_LINKS=formatted_plugins)
                else:
                    data = cls.NODE.format(CLASS_NAME=class_name,
                                           MODULE_NAME=module_name,
                                           NODE_NAME=name,
                                           NODE_ICON=icon,
                                           UNDERLINE=('~' * len(name)))

                cls._write_cached(class_filename, data)
                return class_filename[len(path) + len(os.sep):]

    @classmethod
    def process_library(cls, path, library, plugins, example_flows,
                        top_level=False):
        def indented_sequence(indent, sequence):
            return [' ' * indent + elem for elem in sequence]

        def to_uri(path):
            return '/'.join(path.split(os.path.sep))

        # Name of current library.
        name = library['name']

        # Target path for library on disk and create.
        directory = os.path.join(path, name)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Process all other libraries.
        libraries = []
        for child_library in library.setdefault('libraries', []):
            # side-effect: files are written to disc.
            index_filename = cls.process_library(
                directory, child_library, plugins, example_flows, False)
            libraries.append(to_uri(index_filename))

        # Process nodes in library.
        node_uris = []
        node_list = library.setdefault('nodes', [])

        for node in node_list:
            # side-effect: files are written to disc.
            class_filename = cls.process_node(directory, node, plugins,
                                              example_flows)
            node_uris.append(to_uri(class_filename))

        # Store absolute path to library.
        description = ''
        if len(node_list) > 0:
            node_json_filename = node_list[0]
            with io.open(uri_to_path(node_json_filename), 'r') as f:
                node_dict = json.loads(f.read())
            node_file_path = uri_to_path(node_dict['file'])
            library_base_path = os.path.dirname(node_file_path)

            # Copy all SVG-icons outside _resources folder.
            root_svg_icons = glob.glob(os.path.join(
                library_base_path, '*.svg'))
            for filename in root_svg_icons:
                distutils.file_util.copy_file(filename, directory)

            # Copy resources to our target directory if any resources exists.
            resource_path = os.path.join(library_base_path, '_resources')
            if os.path.exists(resource_path):
                try:
                    with open(os.path.join(resource_path,
                                           "description.rst"), 'r') as f:
                        description = f.read()
                except Exception:
                    raise
                    description = ""

                for filename in walkrst(resource_path):
                    cls._add_to_cache(
                        filename.replace(resource_path, directory))

                distutils.dir_util.copy_tree(resource_path, directory)
                try:
                    os.remove(
                        os.path.join(directory, "__library_description.rst"))
                except (IOError, OSError):
                    pass
                if os.path.exists(os.path.join(directory, "description.rst")):
                    cls._add_to_cache(os.path.join(
                        directory, "__library_description.rst"))

                distutils.file_util.move_file(
                    os.path.join(directory, "description.rst"),
                    os.path.join(directory, "__library_description.rst"))

        plugin_uris = []
        if top_level:
            plugin_uris.append(to_uri(cls.process_plugins(directory, plugins)))

        # Write index file.
        index_filename = os.path.join(directory, 'index.rst')

        cls._write_cached(
            index_filename,
            cls.LIBRARY.format(
                LIBRARIES='\n'.join(indented_sequence(3, libraries)),
                LIBRARY_NAME=name.capitalize(),
                NODES='\n'.join(indented_sequence(3, node_uris)),
                UNDERLINE=('=' * len(name)),
                DESCRIPTION=description,
                PLUGINS='\n'.join(indented_sequence(3, plugin_uris))))

        return index_filename[len(path) + len(os.sep):]

    @classmethod
    def process(cls, library, outdir, appdir, paths, example_flows):
        # Create /doc/src folder.
        src = os.path.join(outdir, 'src')
        try:
            os.mkdir(src)
        except (IOError, OSError):
            pass

        # Write conf.py into /doc
        cls.write_config(os.path.join(outdir, 'conf.py'), paths)

        # Write conf.rtd.py into /doc
        doc_directory = os.path.join(appdir, 'Doc')
        try:
            paths = [os.path.relpath(path, doc_directory)
                     for path in paths]
        except ValueError:
            # Problems occur when libraries are on different drives than
            # doc_directory (Windows).  Relative paths are only useful when
            # building local documentation and when packaging external
            # documentation for RTD this will not be a problem.
            pass

        cls.write_config(os.path.join(outdir, 'conf.rtd.py'), paths)

        # Write index.rst into /doc
        cls._write_cached(os.path.join(outdir, 'index.rst'),
                          cls.INDEX)

        # Find all rst-documents and png-images in application
        # directory/Doc/src
        rsts = glob.glob(os.path.join(appdir, 'Doc', 'src', '*.rst'))
        pngs = glob.glob(os.path.join(appdir, 'Doc', 'src', '*.png'))

        app_icons = [os.path.join(appdir, 'Gui', 'Resources', 'icons', icon)
                     for icon in ['favicon.ico', 'application.png']]

        # Copy all files into /doc/src
        for filename in (rsts + pngs + app_icons):
            distutils.file_util.copy_file(
                filename, os.path.join(src, os.path.basename(filename)))
            cls._add_to_cache(os.path.join(src, os.path.basename(filename)))

        # Start processing libraries.
        cls.process_library(src, library, {}, example_flows, True)

    @classmethod
    def write_config(cls, config_filename, paths):
        cls._write_cached(config_filename,
                          cls.CONFIG.format(
                              PATHS=paths,
                              major_version=version.major,
                              minor_version=version.minor,
                              version=version.version))


def file_walk(root, ext):
    for root_, dirs, filenames in os.walk(root):
        for filename in filenames:
            filename = os.path.join(root_, filename)
            if filename.endswith(ext):
                yield filename


def walkrst(root):
    return file_walk(root, '.rst')


def walksyx(root):
    return file_walk(root, '.syx')


class DocsBuilder(threading.Thread):
    """"Interface for asynchronously building the documentation."""

    lock = threading.Lock()
    script = """
import os
import sys
import sphinx
import base64
import json
import six
fs_encoding = sys.getfilesystemencoding()
args = json.loads(base64.b64decode(b'{ARGS}').decode('ascii'))
working_dir = args['working_dir']
os.chdir(working_dir)
sys.argv[:] = ['', '-b', 'html', '.', os.path.join(working_dir, 'html')]

if six.PY2:
    sys.path[:] = sys.path + [arg.encode(fs_encoding)
        for arg in args['sys_path']]
else:
    sys.path[:] = sys.path + args['sys_path']
sphinx.main()
"""
    _tmp_dirname = 'doctmp'
    _res_dirname = 'doc'

    node_example_re = re.compile(
        'Node example(?::|[ \t]+for)[ \t]+\*([^ \t\n]*)\*',
        re.IGNORECASE)

    def __init__(self, library_manager, root_library, venv=False, folder=None):
        super(DocsBuilder, self).__init__()
        self._library_manager = library_manager
        self._venv = venv
        self._popen_process = None
        self._latest_progress = 0
        self._first_section_done = False
        self._stopper = threading.Event()
        self._storage_directory = (
            folder or self._library_manager.storage_directory)

    def format_node_example(node_id):
        return 'Node example: *{}*'.format(node_id)

    def get_progress(self):
        """Return the current status of the documentation process as an integer
        from 0 to 100 inclusive.
        """
        return self._latest_progress

    def stop(self):
        try:
            self._stopper.set()
            if self._popen_process.poll() is None:
                self._popen_process.kill()
        except Exception:
            pass

    def spawn_sphinx_process(self):
        """Spawn sphinx as a new process."""
        tmp_directory = os.path.join(
            self._storage_directory, self._tmp_dirname)

        # Create the doc folder if it does not exist.
        try:
            os.mkdir(tmp_directory)
        except (IOError, OSError):
            pass

        paths = [os.path.join(
            self._library_manager.application_directory, 'Python')]
        paths.extend(self._library_manager.python_directories)
        paths.extend(
            [os.path.join(os.path.normpath(library_directory), 'Common')
             for library_directory
             in self._library_manager.library_directories])

        paths.extend(set([os.path.dirname(filename)
                          for filename in
                          self._library_manager.library_node_filenames()]))

        example_flows = {}
        examples_tmp_root = os.path.join(tmp_directory, '_examples')

        try:
            os.mkdir(examples_tmp_root)
        except (IOError, OSError):
            pass

        for library_directory in self._library_manager.library_directories:
            library_ini = library_info.read_library_info(
                directory=library_directory)
            if library_ini:
                library_examples_dir = os.path.join(
                    examples_tmp_root, library_ini['General']['name'])
                try:
                    distutils.dir_util.copy_tree(
                        os.path.join(library_directory, 'Examples'),
                        library_examples_dir)
                except Exception:
                    pass
                else:
                    for syx_filename in walksyx(library_examples_dir):
                        with open(syx_filename, 'rb') as f:
                            flow_dict = workflow_converter.XMLToJson(f).dict()
                            texts = [flow_dict.get('description', '')]
                            for textfield in flow_dict['textfields']:
                                texts.append(textfield.get('text', ''))
                            for text in texts:
                                for node_id in self.node_example_re.findall(
                                        text):
                                    examples = example_flows.setdefault(
                                        node_id, [])
                                    rel_syx_filename = os.path.relpath(
                                        syx_filename,
                                        tmp_directory)
                                    rst_syx_filename = '/{}'.format(
                                        unipath(rel_syx_filename))
                                    examples.append(
                                        [rst_syx_filename,
                                         flow_dict.get('label')])

        RstMaker.file_cache_clear()
        RstMaker.process(
            self._library_manager.library_by_json(), tmp_directory,
            self._library_manager.application_directory, paths,
            example_flows)

        file_cache = RstMaker.file_cache()

        for filename in walkrst(os.path.join(tmp_directory, 'src')):
            if filename not in file_cache:
                os.remove(filename)

        # Run sphinx in a separate process to avoid polluting the
        # executing environment.
        executable = sys.executable
        env = vs.environ_wrapper()

        sys_path = list(vs.SYS.path) + paths

        arguments = [
            executable,
            '-c',
            DocsBuilder.script.format(
                ARGS=base64.b64encode(json.dumps(
                    dict(
                        working_dir=tmp_directory,
                        # TODO(erik): Replace with more reasonable argument
                        # passing.  Using format and string script seems, now,
                        # like an awkward solution.
                        sys_path=sys_path)).encode('ascii')).decode('ascii'))]

        examples = os.path.join(tmp_directory, 'examples')

        core_logger.debug('Generate documentation')
        # Use str() to assure python 2 and 3 compatibility
        env['QT_API'] = 'pyside'
        self._popen_process = os_support.Popen_no_console(
            arguments,
            env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def monitor_output(self):
        """Monitor the output of the sphinx process, blocking the current
        thread until the sphinx process closes its standard output pipe.
        """
        # Sphinx counts to 100% four times before its done, but the last one is
        # really quick.
        section = 0
        sections = ("reading sources",
                    "writing output",
                    "highlighting module code",
                    "copying images")
        offsets = (0, 40, 80, 99, 100)
        regexs = [re.compile("({})\.\.\. \[\W*([0-9]+)\%\]".format(s))
                  for s in sections]

        def total_progress(x):
            return offsets[section] + int(
                x / 100. * (offsets[section + 1] - offsets[section]))

        buf = ''
        while not self._stopper.is_set():
            # TODO(erik): Risk of decoding partial encoded character.
            raw = self._popen_process.stdout.read(64).decode(
                vs.fs_encoding, errors='replace')
            if raw:
                lines = re.split('(\r\n|[\r\n])', buf + raw)
                buf = lines[-1]

                for line in lines[:-1]:
                    line = line.rstrip()
                    if line:
                        core_logger.debug(line.rstrip())
                        for i, (regex, section_text) in enumerate(
                                zip(regexs, sections)):
                            match = regex.match(line)
                            if match:
                                section_progress = float(match.group(2))
                                section = i
                                self._latest_progress = total_progress(
                                    section_progress)
            else:
                self._latest_progress = 100
                self._stopper.set()
        self._popen_process.communicate()
        res = self._popen_process.wait()

        doc_directory = os.path.join(
            self._storage_directory, self._res_dirname)

        tmp_directory = os.path.join(
            self._storage_directory, self._tmp_dirname)

        if res != 0:
            shutil.rmtree(tmp_directory)
        else:
            try:
                shutil.rmtree(doc_directory)
            except OSError:
                pass
            try:
                os.rename(tmp_directory, doc_directory)
            except OSError:
                pass

        try:
            distutils.dir_util.copy_tree(doc_directory, tmp_directory)
        except Exception:
            pass

    def run(self):
        """Start the sphinx process and update progress until sphinx is
        done.
        """
        with DocsBuilder.lock:
            self.spawn_sphinx_process()
            self.monitor_output()


class LibraryManager(object):
    """LibraryManager the primary interface to this module's functionality."""

    def __init__(self,
                 application_directory,
                 storage_directory,
                 python_directories,
                 library_directories,
                 temp,
                 session):
        self.application_directory = application_directory
        self.storage_directory = storage_directory
        self.python_directories = python_directories
        self.library_directories = library_directories
        self.temp = temp
        self.session = session
        self._library_creator_result = None

    def typealiases(self):
        """Return typeliases."""
        return self.library_by_json()['typealiases']

    def library_creator_result(self):
        return self._library_creator_result

    def create_library_json(self):
        # Add and remove python directories.
        creator = library_creator.LibraryCreator()
        task = task_worker.worker(('execute_library_creator',
                                   creator.source_file(),
                                   'LibraryCreator',
                                   '',
                                   json.dumps([self.library_directories,
                                               self.storage_directory]),
                                   {},
                                   six.moves.getcwd(),
                                   {}),
                                  None,
                                  quit_after=True)
        with task_worker.await_done(task) as msg:
            result = node_result.from_dict(msg[2])
        result.log_times()
        self._library_creator_result = result

    def create_library_doc(self, root_library, venv=False, folder=None):
        """Create documentation"""
        # TODO(erik): make use of root library to generate the doc.
        # Instead of re-inspecting the file structure using library_creator.
        if folder is not None:
            try:
                os.mkdir(folder)
            except (IOError, OSError):
                pass
        docs_builder = DocsBuilder(self, root_library, venv, folder=folder)
        docs_builder.start()
        docs_builder.join()

    def get_documentation_builder(self, root_library):
        return DocsBuilder(self, root_library)

    def library_tags(self):
        return library_tags(self.library_by_json())

    def library_by_json(self):
        """Return the library."""
        if self._library_creator_result is None:
            self.create_library_json()
        result = self._library_creator_result.output
        if result is None:
            result = {'name': 'Library',
                      'libraries': [], 'tags': None, 'typealiases': {}}
        return result

    def library_node_filenames(self):
        return library_node_filenames(self.library_by_json())

    def library_by_name_list(self):
        """Return the library organized by name."""
        return dict(group_pairs(library_by_name(self.library_by_json())))

    def library_by_name_list_fuzzy(self, pattern):
        """Return the library organized by name, filtered with pattern."""
        items = [(key.split('/')[-1], value)
                 for key, value in ungroup_pairs(
                     self.library_by_name_list().items())]
        return dict(group_pairs(fuzzy_filter(pattern, items)))

    def library_by_nodeid_fuzzy(self, pattern):
        """Return the library organized by nodeid, filtered with pattern."""
        items = [(key.split('/')[-1], value)
                 for key, value in self.library_by_nodeid().items()]
        return dict(group_pairs(fuzzy_filter(pattern, items)))

    def library_by_nodeid(self):
        """Return the library organized by nodeid."""
        return library_by_nodeid(self.library_by_json())

    def library_by_input_type_list(self):
        """Return the library organized by input_type."""
        return library_by_field_list(
            self.library_by_nodeid(),
            ['ports', 'inputs', None, 'type'])

    def library_by_output_type_list(self):
        """Return the library organized by output_type."""
        return library_by_field_list(
            self.library_by_nodeid(),
            ['ports', 'outputs', None, 'type'])
