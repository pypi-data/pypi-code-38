# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gcgc',
 'gcgc.alphabet',
 'gcgc.data',
 'gcgc.datasets',
 'gcgc.encoded_seq',
 'gcgc.fields',
 'gcgc.ml',
 'gcgc.ml.pytorch_utils',
 'gcgc.parser',
 'gcgc.random',
 'gcgc.rollout',
 'gcgc.tests',
 'gcgc.tests.alignment',
 'gcgc.tests.alphabet',
 'gcgc.tests.cli',
 'gcgc.tests.datasets',
 'gcgc.tests.encoded_seq',
 'gcgc.tests.fields',
 'gcgc.tests.fixtures',
 'gcgc.tests.parser',
 'gcgc.tests.rollout',
 'gcgc.tests.third_party.pytorch_utils']

package_data = \
{'': ['*'],
 'gcgc.data': ['splice/*'],
 'gcgc.tests.fixtures': ['PF12057/*',
                         'ecoli/*',
                         'globin_alignment/*',
                         'p53_human/*']}

install_requires = \
['aiohttp>=3.4',
 'biopython>=1.72',
 'click>=7.0',
 'idna_ssl>=1.1',
 'numpy>=1.15.2']

extras_require = \
{'torch': ['torch>=1.1.0']}

entry_points = \
{'console_scripts': ['gcgc = gcgc.cli:main']}

setup_kwargs = {
    'name': 'gcgc',
    'version': '0.6.1',
    'description': 'GCGC is a preprocessing library for biological sequence model development.',
    'long_description': '# GCGC\n\n> GCGC is a python package for feature processing on Biological Sequences.\n\n[![](https://img.shields.io/pypi/v/gcgc.svg)](https://pypi.python.org/pypi/gcgc)\n[![](https://img.shields.io/travis/tshauck/gcgc.svg)](https://travis-ci.org/tshauck/gcgc)\n[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2329966.svg)](https://doi.org/10.5281/zenodo.2329966)\n\n## Installation\n\nInstall GCGC via pip:\n\n```sh\n$ pip install gcgc\n```\n\nIf you\'d like to use one of the third party tools, install the related "extras".\n\n```bash\n$ pip install gcgc[torch]\n```\n\n## Documentation\n\nThe GCGC documentation is at [gcgc.trenthauck.com](http://gcgc.trenthauck.com).\n\n## Citing GCGC\n\nIf you use GCGC in your research, cite it with the following:\n\n```\n@misc{trent_hauck_2018_2329966,\n  author       = {Trent Hauck},\n  title        = {GCGC},\n  month        = dec,\n  year         = 2018,\n  doi          = {10.5281/zenodo.2329966},\n  url          = {https://doi.org/10.5281/zenodo.2329966}\n}\n```\n',
    'author': 'Trent Hauck',
    'author_email': 'trent@trenthauck.com',
    'url': 'http://gcgc.trenthauck.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
