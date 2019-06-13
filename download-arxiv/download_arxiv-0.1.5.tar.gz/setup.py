# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['download_arxiv']
install_requires = \
['arxiv>=0.3.1,<0.4.0',
 'click>=7.0,<8.0',
 'logzero>=1.5,<2.0',
 'pybtex>=0.22.2,<0.23.0',
 'python-dateutil>=2.8,<3.0']

entry_points = \
{'console_scripts': ['arxiv = download_arxiv:main']}

setup_kwargs = {
    'name': 'download-arxiv',
    'version': '0.1.5',
    'description': '',
    'long_description': '# download_arxiv\n\n## How-to-use\n\n`arxiv <URL> --out <path_to_output_dir>`\n\n## Installation\n\n`pip install download_arxiv`\n',
    'author': 'Shun Kiyono',
    'author_email': 'kiyono@ecei.tohoku.ac.jp',
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
