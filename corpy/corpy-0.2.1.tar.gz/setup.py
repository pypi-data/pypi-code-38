# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['corpy', 'corpy.morphodita', 'corpy.phonetics']

package_data = \
{'': ['*'], 'corpy': ['scripts/*']}

install_requires = \
['click>=7.0,<8.0',
 'lazy>=1.4,<2.0',
 'lxml>=4.3,<5.0',
 'matplotlib>=3.1,<4.0',
 'numpy>=1.16,<2.0',
 'regex>=2019.4,<2020.0',
 'ufal.morphodita>=1.9,<2.0',
 'ufal.udpipe>=1.2,<2.0',
 'wordcloud>=1.5,<2.0']

entry_points = \
{'console_scripts': ['xc = corpy.scripts.xc:main',
                     'zip-verticals = corpy.scripts.zip_verticals:main']}

setup_kwargs = {
    'name': 'corpy',
    'version': '0.2.1',
    'description': 'Tools for processing language data.',
    'long_description': "=====\nCorPy\n=====\n\n.. image:: https://readthedocs.org/projects/corpy/badge/?version=stable\n   :target: https://corpy.readthedocs.io/en/stable/?badge=stable\n   :alt: Documentation status\n\n.. image:: https://badge.fury.io/py/corpy.svg\n   :target: https://badge.fury.io/py/corpy\n   :alt: PyPI package\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/python/black\n   :alt: Code style\n\nWhat is CorPy?\n==============\n\nA fancy plural for *corpus* ;) Also, a collection of handy but not especially\nmutually integrated tools for dealing with linguistic data. It abstracts away\nfunctionality which is often needed in practice for teaching and/or day to day\nwork at the `Czech National Corpus <https://korpus.cz>`__, without aspiring to\nbe a fully featured or consistent NLP framework.\n\nThe short URL to the docs is: https://corpy.rtfd.io/\n\nHere's an idea of what you can do with CorPy:\n\n- add linguistic annotation to raw textual data using either UDPipe_ or\n  MorphoDiTa_\n\n.. _UDPipe: http://ufal.mff.cuni.cz/udpipe\n.. _MorphoDiTa: http://ufal.mff.cuni.cz/morphodita\n\n.. note::\n\n   **Should I pick UDPipe or MorphoDiTa?**\n\n   UDPipe_ is the successor to MorphoDiTa_, extending and improving upon the\n   original codebase. It has more features at the cost of being somewhat more\n   complex: it does both `morphological tagging (including lemmatization) and\n   syntactic parsing <https://corpy.rtfd.io/en/stable/guides/udpipe.html>`__,\n   and it handles a number of different input and output formats. You can also\n   download `pre-trained models <http://ufal.mff.cuni.cz/udpipe/models>`__ for\n   many different languages.\n\n   By contrast, MorphoDiTa_ only has `pre-trained models for Czech and English\n   <http://ufal.mff.cuni.cz/morphodita/users-manual>`__, and only performs\n   `morphological tagging (including lemmatization)\n   <https://corpy.rtfd.io/en/stable/guides/morphodita.html>`__. However, its\n   output is more straightforward -- it just splits your text into tokens and\n   annotates them, whereas UDPipe can (depending on the model) introduce\n   additional tokens necessary for a more explicit analysis, add multi-word\n   tokens etc. This is because UDPipe is tailored to the type of linguistic\n   analysis conducted within the UniversalDependencies_ project, using the\n   CoNLL-U_ data format.\n\n   MorphoDiTa can also help you if you just want to tokenize text and don't have\n   a language model available.\n\n.. _UniversalDependencies: https://universaldependencies.org\n.. _CoNLL-U: https://universaldependencies.org/format.html\n\n- `easily generate word clouds\n  <https://corpy.rtfd.io/en/stable/guides/vis.html>`__\n- `generate phonetic transcripts of Czech texts\n  <https://corpy.rtfd.io/en/stable/guides/phonetics_cs.html>`__\n- `wrangle corpora in the vertical format\n  <https://corpy.rtfd.io/en/stable/guides/vertical.html>`__ devised originally\n  for `CWB <http://cwb.sourceforge.net/>`__, used also by `(No)SketchEngine\n  <https://nlp.fi.muni.cz/trac/noske/>`__\n- plus some `command line utilities\n  <https://corpy.rtfd.io/en/stable/guides/cli.html>`__\n\nInstallation\n============\n\n.. code:: bash\n\n   $ pip3 install corpy\n\nRequirements\n============\n\nOnly recent versions of Python 3 (3.6+) are supported by design.\n\nDevelopment\n===========\n\nDependencies and building the docs\n----------------------------------\n\nThe canonical dependency requirements are listed in ``pyproject.toml`` and\nfrozen in ``poetry.lock``. However, in order to use ``autodoc`` to build the API\ndocs, the package has to be installed, and ``corpy`` has dependencies that are\ntoo resource-intensive to build on ReadTheDocs.\n\nThe solution is to use a dummy ``setup.py`` which lists *only* the dependencies\nneeded to build the docs properly, and mock all other dependencies by listing\nthem in ``autodoc_mock_imports`` in ``docs/conf.py``. This dummy ``setup.py`` is\nused to install ``corpy`` *only* on ReadTheDocs (via the appropriate config\noption in ``.readthedocs.yml``). The same goes for the ``MANIFEST.in`` file,\nwhich duplicates the ``tool.poetry.include`` entries in ``pyproject.toml`` for\nthe sole benefit of ReadTheDocs.\n\n.. license-marker\n\nLicense\n=======\n\nCopyright © 2016--present `ÚČNK <http://korpus.cz>`__/David Lukeš\n\nDistributed under the `GNU General Public License v3\n<http://www.gnu.org/licenses/gpl-3.0.en.html>`__.\n",
    'author': 'David Lukes',
    'author_email': 'dafydd.lukes@gmail.com',
    'url': 'https://github.com/dlukes/corpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
