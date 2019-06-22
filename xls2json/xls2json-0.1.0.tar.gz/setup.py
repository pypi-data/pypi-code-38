# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['xls2json']

package_data = \
{'': ['*']}

install_requires = \
['xlrd>=1.2,<2.0']

setup_kwargs = {
    'name': 'xls2json',
    'version': '0.1.0',
    'description': 'Convert XLS file to JSON.',
    'long_description': '## xls2json\n\nThis tool supports 3 modes:\n\n- **--perentry** Read XLS file and write a JSON file per entry of XLS file.\n- **--persheet** Read XLS file and write a JSON file per sheet of XLS file.\n- **default** Read XLS file and write to single JSON file.\n\n## TODO\n\n- auto detect cell type and write accordingly.\n- handle XLS file with no table headers.\n- handle non unique sheet names.\n',
    'author': 'Reza Handzalah',
    'author_email': 'rezahandzalah@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
