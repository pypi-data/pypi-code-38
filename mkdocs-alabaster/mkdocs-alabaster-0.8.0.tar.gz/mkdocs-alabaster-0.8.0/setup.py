# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mkdocs_alabaster']

package_data = \
{'': ['*'], 'mkdocs_alabaster': ['css/*', 'inc/*', 'js/*', 'sidebars/*']}

install_requires = \
['mkdocs>=1.0,<2.0']

entry_points = \
{'mkdocs.themes': ['alabaster = mkdocs_alabaster']}

setup_kwargs = {
    'name': 'mkdocs-alabaster',
    'version': '0.8.0',
    'description': 'Alabaster port for MkDocs',
    'long_description': '# Alabaster for MkDocs\n\n1. `pip install mkdocs-alabaster`\n2. Add to your mkdocs.yml: `theme: alabaster`\n\nDocumentation: <http://mkdocs-alabaster.ale.sh>\n',
    'author': 'Alexander Pushkov',
    'author_email': 'alexander@notpushk.in',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
