# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['srec_nlp']

package_data = \
{'': ['*']}

install_requires = \
['Cython>=0.29.9,<0.30.0',
 'attrs>=19.1,<20.0',
 'aylien-apiclient>=0.7.0,<0.8.0',
 'google-cloud-language>=1.2,<2.0',
 'google-cloud>=0.34.0,<0.35.0',
 'ibm-watson>=3.0,<4.0',
 'numpy>=1.16,<2.0',
 'paralleldots>=3.2,<4.0',
 'pybind11>=2.2,<3.0',
 'requests>=2.22,<3.0',
 'sklearn>=0.0.0,<0.0.1',
 'trio>=0.11.0,<0.12.0']

setup_kwargs = {
    'name': 'srec-nlp',
    'version': '0.2.17a0',
    'description': '',
    'long_description': None,
    'author': 'Stelios Tymvios',
    'author_email': 'stelios.tymvios@icloud.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
