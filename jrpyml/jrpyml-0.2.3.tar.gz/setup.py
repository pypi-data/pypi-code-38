# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jrpyml', 'jrpyml.datasets']

package_data = \
{'': ['*'], 'jrpyml': ['vignettes/*'], 'jrpyml.datasets': ['data/*']}

install_requires = \
['matplotlib>=3.1,<4.0',
 'numpy>=1.16,<2.0',
 'pandas>=0.24.2,<0.25.0',
 'scipy==1.2',
 'statsmodels>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'jrpyml',
    'version': '0.2.3',
    'description': '',
    'long_description': None,
    'author': 'Jamie',
    'author_email': 'jamie@jumpingrivers.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
