# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['hyperscan']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hyperscan',
    'version': '0.1.2',
    'description': 'Python bindings for Hyperscan.',
    'long_description': "# Hyperscan for Python\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hyperscan.svg)\n![PyPI - Wheel](https://img.shields.io/pypi/wheel/hyperscan.svg)\n![PyPI - Status](https://img.shields.io/pypi/status/hyperscan.svg)\n![PyPI - License](https://img.shields.io/pypi/l/hyperscan.svg)\n[![Read the Docs](https://img.shields.io/readthedocs/python-hyperscan.svg)](https://python-hyperscan.readthedocs.io/en/latest/)\n\nA CPython extension for [Hyperscan](https://www.hyperscan.io/), Intel's\nopen source, high-performance multiple regex matching library. Currently\nonly supports manylinux-compatible Linux distributions.\n\n## Installation\n\n```shell\n$ pip install hyperscan\n```\n\n## API Support\n\n``python-hyperscan`` currently exposes *most* of the C API, with the\nfollowing caveats or exceptions:\n\n* No [Chimera][1] support yet.\n* No [stream compression][2] support.\n* No [custom allocator][3] support.\n* ``hs_expression_info``, ``hs_expression_ext_info``,\n  ``hs_populate_platform``, and ``hs_serialized_database_info`` not\n  exposed yet.\n\n``python-hyperscan`` has been built and tested against Hyperscan\n``v4.7.0`` and upwards, including the latest as of April 2019,\n``v5.1.1``.\n\n## Resources\n\n* [PyPI Project](https://pypi.org/project/hyperscan/)\n* [Documentation](https://python-hyperscan.readthedocs.io)\n* [Hyperscan C API Documentation](http://intel.github.io/hyperscan/dev-reference/)\n\n\n[1]: http://intel.github.io/hyperscan/dev-reference/chimera.html\n[2]: http://intel.github.io/hyperscan/dev-reference/runtime.html#stream-compression\n[3]: http://intel.github.io/hyperscan/dev-reference/runtime.html#custom-allocators\n[4]: http://intel.github.io/hyperscan/dev-reference/compilation.html\n[5]: https://github.com/darvid/python-hyperscan/issues\n",
    'author': 'David Gidwani',
    'author_email': 'david.gidwani@gmail.com',
    'url': 'https://github.com/darvid/python-hyperscan',
    'packages': packages,
    'package_data': package_data,
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
