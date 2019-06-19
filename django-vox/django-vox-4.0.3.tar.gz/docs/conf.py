# -- Django workaround
import django
import os
import sys

sys.path.append(os.path.dirname(__file__))
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
django.setup()

# -- Project information -----------------------------------------------------

project = "Django Vox"
copyright = "2018, Alan Trick"
author = "Alan Trick"

extensions = ["sphinx.ext.doctest", "sphinx.ext.autodoc"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

source_suffix = ".rst"

master_doc = "index"

language = None

exclude_patterns = ["_build", "api/modules.rst", "api/django_vox.migrations"]

pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
htmlhelp_basename = "DjangoVoxdoc"

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {}

latex_documents = [
    (master_doc, "DjangoVox.tex", "Django Vox Documentation", "Alan Trick", "manual")
]


# -- Options for manual page output ------------------------------------------

man_pages = [(master_doc, "djangovox", "Django Vox Documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

texinfo_documents = [
    (
        master_doc,
        "DjangoVox",
        "Django Vox Documentation",
        author,
        "DjangoVox",
        "One line description of project.",
        "Miscellaneous",
    )
]
