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
    'version': '0.1.2',
    'description': 'ProseMirror in Python',
    'long_description': "# prosemirror-py\n\n[![CircleCI](https://circleci.com/gh/fellowinsights/prosemirror-py.svg?style=shield)](https://circleci.com/gh/fellowinsights/prosemirror-py) [![Code Coverage](https://codecov.io/gh/fellowinsights/prosemirror-py/branch/master/graph/badge.svg)](https://codecov.io/gh/fellowinsights/prosemirror-py)\n\nThis package provides Python implementations of the following [ProseMirror](https://prosemirror.net/) packages:\n\n-   [`prosemirror-model`](https://github.com/ProseMirror/prosemirror-model)\n-   [`prosemirror-transform`](https://github.com/ProseMirror/prosemirror-transform)\n-   [`prosemirror-test-builder`](https://github.com/ProseMirror/prosemirror-test-builder)\n-   [`prosemirror-schema-basic`](https://github.com/ProseMirror/prosemirror-schema-basic)\n-   [`prosemirror-schema-list`](https://github.com/ProseMirror/prosemirror-schema-list)\n\nThe original implementation has been followed as closely as possible during translation to simplify keeping this package up-to-date with any upstream changes.\n\n## Why?\n\nProseMirror provides a powerful toolkit for building rich-text editors, but it's JavaScript-only. Until now, the only option for manipulating and working with ProseMirror documents from Python was to embed a JS runtime. With this translation, you can now define schemas, parse documents, and apply transforms directly via a native Python API.\n\n## Status\n\nThe full ProseMirror test suite has been translated and passes. This project only supports Python 3. There are no type annotations at the moment, although the original has annotations available in doc comments.\n",
    'author': 'Shen Li',
    'author_email': 'shen@fellow.co',
    'url': 'https://github.com/fellowinsights/prosemirror-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4',
}


setup(**setup_kwargs)
