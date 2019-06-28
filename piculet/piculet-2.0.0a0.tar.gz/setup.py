# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['piculet']
extras_require = \
{'yaml': ['strictyaml>=1.0,<2.0']}

entry_points = \
{'console_scripts': ['piculet = piculet:main']}

setup_kwargs = {
    'name': 'piculet',
    'version': '2.0.0a0',
    'description': 'XML/HTML scraper using XPath queries.',
    'long_description': '|pypi| |license| |azure|\n\n.. |pypi| image:: https://img.shields.io/pypi/v/piculet.svg?style=flat-square\n    :target: https://pypi.org/project/piculet/\n    :alt: PyPI version.\n\n.. |license| image:: https://img.shields.io/pypi/l/piculet.svg?style=flat-square\n    :target: https://pypi.org/project/piculet/\n    :alt: Project license.\n\n.. |azure| image:: https://dev.azure.com/tekir/piculet/_apis/build/status/uyar.piculet?branchName=master\n    :target: https://dev.azure.com/tekir/piculet/_build\n    :alt: Azure Pipelines build status.\n\nPiculet is a module for extracting data from XML or HTML documents\nusing XPath queries.\nIt consists of a `single source file`_ with no dependencies other than\nthe standard library, which makes it very easy to integrate into applications.\nIt also provides a command line interface.\n\nGetting started\n---------------\n\nPiculet has been tested with Python 3.5+ and compatible versions of PyPy.\nYou can install the latest version using ``pip``::\n\n    pip install piculet\n\n.. _single source file: https://github.com/uyar/piculet/blob/master/piculet.py\n\nGetting help\n------------\n\nThe documentation is available on: https://piculet.tekir.org/\n\nThe source code can be obtained from: https://github.com/uyar/piculet\n\nLicense\n-------\n\nCopyright (C) 2014-2019 H. Turgut Uyar <uyar@tekir.org>\n\nPiculet is released under the LGPL license, version 3 or later.\nRead the included `LICENSE.txt`_ file for details.\n\n.. _LICENSE.txt: https://github.com/uyar/piculet/blob/master/LICENSE.txt\n',
    'author': 'H. Turgut Uyar',
    'author_email': 'uyar@tekir.org',
    'url': 'https://piculet.tekir.org/',
    'py_modules': modules,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
