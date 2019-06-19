# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['prosemirror',
 'prosemirror.model',
 'prosemirror.schema.basic',
 'prosemirror.schema.list',
 'prosemirror.test_builder',
 'prosemirror.transform']

package_data = \
{'': ['*']}

install_requires = \
['pyicu>=2.3,<3.0', 'typing-extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'prosemirror-py',
    'version': '0.1.1',
    'description': 'ProseMirror in Python',
    'long_description': None,
    'author': 'Shen Li',
    'author_email': 'shen@fellow.co',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
