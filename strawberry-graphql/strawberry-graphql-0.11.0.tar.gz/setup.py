# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['strawberry',
 'strawberry.cli',
 'strawberry.contrib',
 'strawberry.contrib.starlette',
 'strawberry.contrib.starlette.app',
 'strawberry.contrib.starlette.utils',
 'strawberry.utils']

package_data = \
{'': ['*'], 'strawberry.contrib.starlette': ['templates/*']}

install_requires = \
['click>=7.0,<8.0',
 'graphql-core-next>=1.0,<2.0',
 'hupper>=1.5,<2.0',
 'pygments>=2.3,<3.0',
 'starlette>=0.11.3,<0.12.0',
 'uvicorn>=0.4.6,<0.5.0']

entry_points = \
{'console_scripts': ['strawberry = strawberry.cli:run']}

setup_kwargs = {
    'name': 'strawberry-graphql',
    'version': '0.11.0',
    'description': 'A library for creating GraphQL APIs',
    'long_description': '<img src="https://github.com/strawberry-graphql/strawberry/raw/master/.github/logo.png" width="124" height="150">\n\n# Strawberry GraphQL\n\n> Python GraphQL library based on dataclasses\n\n[![CircleCI](https://img.shields.io/circleci/token/307b40d5e152e074d34f84d30d226376a15667d5/project/github/strawberry-graphql/strawberry/master.svg?style=for-the-badge)](https://circleci.com/gh/strawberry-graphql/strawberry/tree/master)\n\n## Installation\n\nInstall with:\n\n```shell\npip install strawberry-graphql\n```\n\n## Getting Started\n\nCreate a file called `app.py` with the following code:\n\n```python\nimport strawberry\n\n\n@strawberry.type\nclass User:\n    name: str\n    age: int\n\n\n@strawberry.type\nclass Query:\n    @strawberry.field\n    def user(self, info) -> User:\n        return User(name="Patrick", age=100)\n\n\nschema = strawberry.Schema(query=Query)\n```\n\nThis will create a GraphQL schema defining a `User` type and a single query\nfield `user` that will return a hard coded user.\n\nTo run the debug server run the following command:\n\n```shell\nstrawberry server app\n```\n\nOpen the debug server by clicking on the follwing link:\n[http://0.0.0.0:8000/graphql](http://0.0.0.0:8000/graphql)\n\nThis will open a GraphQL playground where you can test the API.\n\n## Contributing\n\nWe use [poetry](https://github.com/sdispater/poetry) to manage dependencies, to\nget started follow these steps:\n\n```shell\ngit clone https://github.com/strawberry-graphql/strawberry\ncd strawberry\npoetry install\npoetry run pytest\n```\n\nThis will install all the dependencies (including dev ones) and run the tests.\n\n### Pre commit\n\nWe have a configuration for\n[pre-commit](https://github.com/pre-commit/pre-commit), to add the hook run the\nfollowing command:\n\n```shell\npre-commit install\n```\n\n## Links\n\n- Project homepage: https://strawberry.rocks\n- Repository: https://github.com/strawberry-graphql/strawberry\n- Issue tracker: https://github.com/strawberry-graphql/strawberry/issues\n  - In case of sensitive bugs like security vulnerabilities, please contact\n    patrick.arminio@gmail.com directly instead of using issue tracker. We value\n    your effort to improve the security and privacy of this project!\n\n## Licensing\n\nThe code in this project is licensed under MIT license. See [LICENSE](./LICENSE)\nfor more information.\n',
    'author': 'Patrick Arminio',
    'author_email': 'patrick.arminio@gmail.com',
    'url': 'https://strawberry.rocks/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
