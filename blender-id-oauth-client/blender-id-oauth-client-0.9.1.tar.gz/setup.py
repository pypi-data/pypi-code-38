# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['blender_id_oauth_client',
 'blender_id_oauth_client.management',
 'blender_id_oauth_client.management.commands',
 'blender_id_oauth_client.migrations']

package_data = \
{'': ['*'], 'blender_id_oauth_client': ['templates/blender_id_oauth_client/*']}

install_requires = \
['Django>=2.1,<3.0', 'requests-oauthlib>=1.0,<2.0']

setup_kwargs = {
    'name': 'blender-id-oauth-client',
    'version': '0.9.1',
    'description': 'Django app for using Blender ID as OAuth2 authentication service.',
    'long_description': None,
    'author': 'Sybren A. Stüvel',
    'author_email': 'sybren@blender.studio',
    'url': 'https://gitlab.com/blender-institute/blender-id-oauth-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
