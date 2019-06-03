# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['globus_automate_client']

package_data = \
{'': ['*']}

install_requires = \
['globus-sdk>=1.7,<2.0']

entry_points = \
{'console_scripts': ['globus-automate = globus_automate_client.main:main']}

setup_kwargs = {
    'name': 'globus-automate-client',
    'version': '0.1.1',
    'description': 'Experimental client for the in-development Globus Automate services',
    'long_description': 'Globus SDK and CLI for Automate\n===============================\n\nThis is an experimental, and unsupported interface for working with Globus Automate tools, notably the Globus Flows service and any service implementing the Action Provider interface.\n\nAs this is experimental, no support is implied or provided for any sort of use of this package. It is published for ease of distribution among those planning to use it for its intended, experimental, purpose.\n\nBasic Usage\n-----------\n\nInstall with ``pip install globus-automate-client``\n\nThis will install an executable script ``globus-automate``. Run the script without arguments to get a summary of the sub-commands and their usage.\n\nUse of the script to invoke any services requires authentication. Upon first interaction with any Action Provider or the Flows Service, you will be prompted to proceed through an Authentication process using Globus Auth to consent for use by the CLI with the service it is interacting with. This typically only needs to be done once, the first time a service is invoked. Subsequently, the cached authentication information will be used. Authentication information is cached in the file ``$HOME/.globus_token_cache``. It is recommended that this file be protected, and deleted when experimentation with the services is complete.\n',
    'author': 'Mattias Lidman',
    'author_email': 'ml@globus.org',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
