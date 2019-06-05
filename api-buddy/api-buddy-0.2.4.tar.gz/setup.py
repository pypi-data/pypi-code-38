# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['api_buddy',
 'api_buddy.config',
 'api_buddy.network',
 'api_buddy.network.auth',
 'api_buddy.utils',
 'api_buddy.validation']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML==4.2b1',
 'Pygments>=2.4.1,<3.0.0',
 'beautifulsoup4>=4.7.1,<5.0.0',
 'colorama>=0.4.1,<0.5.0',
 'docopt>=0.6.2,<0.7.0',
 'requests-oauthlib>=1.2.0,<2.0.0',
 'schema>=0.6.8,<0.7.0',
 'yaspin>=0.14.1,<0.15.0']

entry_points = \
{'console_scripts': ['api = api_buddy.cli:run']}

setup_kwargs = {
    'name': 'api-buddy',
    'version': '0.2.4',
    'description': 'Explore APIs from your console with API Buddy',
    'long_description': '# API Buddy\n\n[![Build Status](https://travis-ci.org/fonsecapeter/api-buddy.svg?branch=master)](https://travis-ci.org/fonsecapeter/api-buddy.svg)\n[![PyPI version](https://badge.fury.io/py/api-buddy.svg)](https://badge.fury.io/py/api-buddy)\n\n![Demo](https://raw.githubusercontent.com/fonsecapeter/api-buddy/master/media/demo.gif \'demo.gif\')\n\n> Right now, only OAuth2 authentication is supported. It\'s the most common, and current gold standard for security best practices. Also most APIs use it. That said, I have no beef with all the APIs out there using something else, so feel free to open a ticket if you want something else supported. 🎟\n>\n> You can also always manually set headers.\n\n## Installation\n\nAs long as you have python 3.7 or higher (I recommend using [pyenv](https://github.com/pyenv/pyenv)), just:\n```bash\npip install api-buddy\n```\n\n## Usage\n\nFirst, specify the API you\'re exploring in your preferences\n```yaml\n# ~/.api-buddy.yaml\napi_url: https://some.api.com\n```\n\nThen it\'s as easy as:\n```bash\napi get some-endpoint\n```\n```json\n=> 200\n{\n  "look": "I haz data",\n  "thx": "API Buddy"\n}\n```\n\nHTTP Method defaults to `get`:\n```bash\napi this-endpoint  # same as first example\n```\n\nYou can add query params in key=val format:\n```bash\napi get \\\n  my/favorite/endpoint \\\n  first_name=cosmo \\\n  last_name=kramer\n```\n\nYou can also add request body data in JSON format:\n```bash\napi post \\\n  some-endpoint \\\n  \'{"id": 1, "field": "value"}\'\n```\n\n🤔 Note the single-quotes. You can expand this accross multiple lines:\n```bash\napi post \\\n  some-endpoint \\\n  \'{\n     "id": 1,\n     "field": "value"\n  }\'\n```\n\n### [Preferences 👉](https://github.com/fonsecapeter/api-buddy/blob/master/docs/preferences.md)\n\n### Arguments\n- `http_method`: (optional, default=`get`) The HTTP method to use in your request.\n  - It should be one of:\n    - `get`\n    - `post`\n    - `patch`\n    - `put`\n    - `delete`\n- `endpoint`: (required) The relative path to an API endpoint.\n  - AKA you don\'t need to type the base api url again here.\n- `params`: (optional) A list of `key=val` query params\n- `data`: (optional) A JSON string of requets body data.\n  - You can\'t use this with `get` because HTTP.\n\n\n### Options\n- `-h`, `--help`: Show the help message\n- `-v`, `--version`: Show the installed version\n\n## Development\nRequires:\n- [poetry](https://poetry.eustace.io/)\n- Python 3.7\n  - Suggest using: [pyenv](https://github.com/pyenv/pyenv)\n\nSteps to start working:\n- Build and create the local venv with `bin/setup`\n- Make sure everything works with `bin/test`\n- Try the local cli with `poetry run api --help`\n- Find other management commands with `bin/list`\n',
    'author': 'Peter Fonseca',
    'author_email': 'peter.nfonseca@gmail.com',
    'url': 'https://github.com/fonsecapeter/api-buddy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
