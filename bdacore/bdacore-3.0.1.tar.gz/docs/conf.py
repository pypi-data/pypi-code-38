# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'nbsphinx',
              'sphinx.ext.mathjax',
 #             'sphinx_gallery.gen_gallery'
              ]

if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling',
    spelling_show_suggestions = True
    spelling_lang = 'en_US'

cwd = os.getcwd()
project_root = os.path.dirname(cwd)

# Insert the project root dir as the first element in the PYTHONPATH.
# This lets us ensure that the source package is imported, and that its
# version is used.
sys.path.insert(0, project_root)

import bdacore


source_suffix = '.rst'
master_doc = 'index'
project = u'bdacore'
year = u'2016-2017'
author = u'BDA Tribe - OCTO Technology'
copyright = '{0}, {1}'.format(year, author)
version = release = u'1.0.0'

templates_path = ['.']
extlinks = {
    'issue': ('https://github.com/octo/bdacore/issues/%s', '#'),
    'pr': ('https://github.com/octo/bdacore/pull/%s', 'PR #'),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only set the theme if we're building docs locally
    html_theme = 'sphinx_rtd_theme'

html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
autosummary_generate = True
numpydoc_show_class_members = False

# Include the example source for plots in API docs
plot_include_source = True
plot_formats = [("png", 90)]
plot_html_show_formats = False
plot_html_show_source_link = False
pygments_style = 'sphinx'

autosummary_generate = False