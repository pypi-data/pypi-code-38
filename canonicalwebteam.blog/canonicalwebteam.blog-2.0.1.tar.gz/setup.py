# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['canonicalwebteam',
 'canonicalwebteam.blog',
 'canonicalwebteam.blog.django',
 'canonicalwebteam.blog.flask']

package_data = \
{'': ['*']}

install_requires = \
['canonicalwebteam.http>=1.0.1,<2.0.0']

extras_require = \
{'Flask': ['Flask>=1.0,<2.0'], 'django': ['django>=2.2,<3.0']}

setup_kwargs = {
    'name': 'canonicalwebteam.blog',
    'version': '2.0.1',
    'description': 'Flask extension and Django App to add a nice blog to your website',
    'long_description': None,
    'author': 'Canonical webteam',
    'author_email': 'webteam@canonical.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
