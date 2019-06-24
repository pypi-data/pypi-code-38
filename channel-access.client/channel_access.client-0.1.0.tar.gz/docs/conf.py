# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

import os
import sys
from pkg_resources import get_distribution



# -- Path setup --------------------------------------------------------------

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------

project = 'channel_access.client'
release = get_distribution(project).version
version = '.'.join(release.split('.')[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon'
]

# -- Options for HTML output -------------------------------------------------

html_show_copyright = False

html_theme_options = {
    'page_width': 'auto',
    'sidebar_width': '20em',
    'fixed_sidebar': False,
    'extra_nav_links': {
        'Index': 'genindex.html'
    }
}

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension -------------------------------------------

autoclass_content = 'both'

# -- Options for napoleon extension ------------------------------------------

napoleon_numpy_docstring = False
