# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['canonicalwebteam', 'canonicalwebteam.flask_base']

package_data = \
{'': ['*']}

install_requires = \
['canonicalwebteam.yaml-responses[flask]>=1.1,<2.0',
 'flask==1.0.2',
 'talisker[gunicorn]==0.14.3']

setup_kwargs = {
    'name': 'canonicalwebteam.flask-base',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Canonical webteam',
    'author_email': 'webteam@canonical.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3,<4',
}


setup(**setup_kwargs)
