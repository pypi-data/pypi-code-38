# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------

from pkg_resources import get_distribution

project = 'channel_access.server'
author = 'André Althaus'
release = get_distribution(project).version
version = '.'.join(release.split('.')[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

templates_path = [ '_templates' ]
source_suffix = '.rst'
master_doc = 'index'
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------

html_title = 'Channel Access server library'
html_show_copyright = False
html_theme = 'alabaster'

html_theme_options = {
    'page_width': 'auto',
    'sidebar_width': '20em',
    'fixed_sidebar': False,
    'extra_nav_links': {
        'Index': 'genindex.html'
    }
}

html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'sourcelink.html',
        'searchbox.html'
    ]
}

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension -------------------------------------------

autodoc_member_order = 'groupwise'
autoclass_content = 'both'

# -- Options for napoleon extension ------------------------------------------

napoleon_numpy_docstring = False
