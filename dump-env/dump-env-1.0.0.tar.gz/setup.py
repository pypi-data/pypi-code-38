# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dump_env']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['dump-env = dump_env.cli:main']}

setup_kwargs = {
    'name': 'dump-env',
    'version': '1.0.0',
    'description': 'A utility tool to create .env files',
    'long_description': "# A utility tool to create ``.env`` files\n\n[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake.services) [![Build Status](https://travis-ci.org/sobolevn/dump-env.svg?branch=master)](https://travis-ci.org/sobolevn/dump-env) [![Coverage](https://coveralls.io/repos/github/sobolevn/dump-env/badge.svg?branch=master)](https://coveralls.io/github/sobolevn/dump-env?branch=master) [![Python Version](https://img.shields.io/pypi/pyversions/dump-env.svg)](https://pypi.org/project/dump-env/) [![Docs](https://readthedocs.org/projects/dump-env/badge/?version=latest)](http://dump-env.readthedocs.io/en/latest/?badge=latest) [![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\n`dump-env` takes an `.env.template` file and some optional environmental variables to create a new `.env` file from these two sources. No external dependencies are used.\n\n\n## Why?\n\nWhy do we need such a tool? Well, this tool is very helpful when your CI is building `docker` (or other) images.\n[Previously](https://github.com/wemake-services/wemake-django-template/blob/6a7ab060e8435fd855cd806706c5d1b5a9e76d12/%7B%7Bcookiecutter.project_name%7D%7D/.gitlab-ci.yml#L25) we had some complex logic of encrypting and decrypting files, importing secret keys and so on.\nNow we can just create secret variables for our CI, add some prefix to it, and use `dump-env` to make our life easier.\n\n\n## Installation\n\n```bash\n$ pip install dump-env\n```\n\n\n## Quickstart\n\nThis quick demo will demonstrate the main and the only purpose of `dump-env`:\n\n```bash\n$ dump-env --template=.env.template --prefix='SECRET_ENV_' > .env\n```\n\nThis command will:\n\n1. take `.env.template`\n2. parse its keys and values\n3. read and all the variables from the environment starting with `SECRET_ENV_`\n4. remove this prefix\n5. mix it all together, environment vars may override ones from the template\n6. sort keys in alphabetic order\n7. dump all the keys and values into the `.env` file\n\n\n## Advanced Usage\n\n```bash\n$ dump-env -t .env.template -p 'SECRET_ENV_' -p 'ANOTHER_SECRET_ENV_' > .env\n```\n\nThis command will do pretty much the same thing as with one prefix. But, it will replace multiple prefixes.\nFurther prefixes always replace previous ones if they are the same.\nFor example:\n\n```bash\n$ export SECRET_TOKEN='very secret string'\n$ export SECRET_ANSWER='13'\n$ export ANOTHER_SECRET_ENV_ANSWER='42'\n$ export ANOTHER_SECRET_ENV_VALUE='0'\n$ dump-env -p SECRET_ -p ANOTHER_SECRET_ENV_\nANSWER=42\nTOKEN=very secret string\nVALUE=0\n```\n\n\n## Creating secret variables in some CIs\n\n- [travis docs](https://docs.travis-ci.com/user/environment-variables/#Defining-encrypted-variables-in-.travis.yml)\n- [gitlab-ci docs](https://docs.gitlab.com/ce/ci/variables/README.html#secret-variables)\n\n\n## Real-world usages\n\nProjects that use this tool in production:\n\n- [wemake-django-template](https://github.com/wemake-services/wemake-django-template/blob/master/%7B%7Bcookiecutter.project_name%7D%7D/.gitlab-ci.yml#L24)\n- [wemake-vue-template](https://github.com/wemake-services/wemake-vue-template/blob/master/template/.gitlab-ci.yml#L24)\n",
    'author': 'Nikita Sobolev',
    'author_email': 'mail@sobolevn.me',
    'url': 'https://github.com/sobolevn/dump-env',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
