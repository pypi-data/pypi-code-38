# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['keios_protocol_classification_class2']

package_data = \
{'': ['*'], 'keios_protocol_classification_class2': ['flatbuffers/*']}

install_requires = \
['flatbuffers>=1.11,<2.0', 'keios-protocol-common>=0.1.1,<0.2.0']

setup_kwargs = {
    'name': 'keios-protocol-classification-class2',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Leftshift One',
    'author_email': 'contact@leftshift.one',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
