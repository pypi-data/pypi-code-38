# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['planhat']

package_data = \
{'': ['*']}

install_requires = \
['requests[security]>=2.13,<3.0']

setup_kwargs = {
    'name': 'planhat',
    'version': '0.3.0',
    'description': 'Python client for Planhat API',
    'long_description': "Planhat Python\n==============\n\nPlanhat API Python client library\n\nhttps://docs.planhat.com/\n\n## Installation\n\n\n\n## Usage\n\n```python\nfrom planhat import Planhat\n\n# See https://docs.planhat.com/#base-url\nfrom planhat import API_URL, API_URL_EU, API_URL_US2\n\n# https://app.planhat.com/developer\nplanhat_client = Planhat(\n    API_URL,\n    'tenant-token',\n    'api-token'\n)\n\ncompanies_data = planhat_client.get_companies()\n```\n",
    'author': 'Nick Allen',
    'author_email': 'nick.allen.cse@gmail.com',
    'url': 'https://github.com/nick-allen/planhat-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*',
}


setup(**setup_kwargs)
