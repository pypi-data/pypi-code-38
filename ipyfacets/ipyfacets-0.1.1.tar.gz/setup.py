# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ipyfacets', 'ipyfacets.overview']

package_data = \
{'': ['*']}

install_requires = \
['ipython>=7.5,<8.0',
 'numpy>=1.16,<2.0',
 'pandas>=0.24.2,<0.25.0',
 'protobuf>=3.8,<4.0']

setup_kwargs = {
    'name': 'ipyfacets',
    'version': '0.1.1',
    'description': 'The facets project(https://github.com/PAIR-code/facets) wrapper for jupyter',
    'long_description': "jupyter-facets\n==============\n\nProviding `facets <https://github.com/PAIR-code/facets>`_ wrapper for jupyter\n\n\nInstallation\n============\n::\n\n   pip install ipyfacets\n\nUsage\n=====\nImport::\n\n    import ipyfacets as facets\n\nFacets Overview::\n\n    #\n    facets.overview({'train': df_train, 'test': df_test})\n\nFacets Dive::\n\n    facets.dive(df)\n\n",
    'author': 'porkbeans',
    'author_email': 'mizuo.taka@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
