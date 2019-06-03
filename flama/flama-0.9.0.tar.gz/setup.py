# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['flama',
 'flama.codecs',
 'flama.codecs.http',
 'flama.codecs.websockets',
 'flama.components',
 'flama.pagination']

package_data = \
{'': ['*'], 'flama': ['templates/*']}

install_requires = \
['marshmallow>=3.0.0rc6,<4.0', 'starlette>=0.12.0,<0.13.0']

extras_require = \
{'full': ['python-forge>=18.6,<19.0',
          'apispec>=1.0.0,<2.0.0',
          'pyyaml>=3.13,<4.0',
          'sqlalchemy>=1.2,<2.0',
          'databases>=0.1.9,<0.2.0']}

setup_kwargs = {
    'name': 'flama',
    'version': '0.9.0',
    'description': 'Fire up your API with this flamethrower',
    'long_description': '<p align="center">\n  <a href="https://flama.perdy.io"><img src="https://raw.githubusercontent.com/perdy/flama/master/docs/images/logo.png" alt=\'Flama\'></a>\n</p>\n<p align="center">\n    &#128293; <em>Fire up your API with this flamethrower.</em>\n</p>\n<p align="center">\n<a href="https://circleci.com/gh/perdy/flama">\n    <img src="https://img.shields.io/circleci/project/github/perdy/flama/master.svg" alt="Build Status">\n</a>\n<a href="https://codecov.io/gh/perdy/flama">\n    <img src="https://codecov.io/gh/perdy/flama/branch/master/graph/badge.svg" alt="Coverage">\n</a>\n<a href="https://pypi.org/project/flama/">\n    <img src="https://badge.fury.io/py/flama.svg" alt="Package version">\n</a>\n</p>\n\n---\n\n**Documentation**: [https://flama.perdy.io](https://flama.perdy.io)\n\n---\n\n# Flama\n\nFlama aims to bring a layer on top of [Starlette] to provide an **easy to learn** and **fast to develop** approach for \nbuilding **highly performant** GraphQL and REST APIs. In the same way of Starlette is, Flama is a perfect option for \ndeveloping **asynchronous** and **production-ready** services. \n\nAmong other characteristics it provides the following:\n\n* **Generic classes** for API resources that provides standard CRUD methods over SQLAlchemy tables.\n* **Schema system** based on [Marshmallow] that allows to **declare** the inputs and outputs of endpoints and provides \na reliable way of **validate** data against those schemas.\n* **Dependency Injection** that ease the process of managing parameters needed in endpoints. Flama ASGI objects \nlike `Request`, `Response`, `Session` and so on are defined as components and ready to be injected in your endpoints.\n* **Components** as the base of the plugin ecosystem, allowing you to create custom or use those already defined in \nyour endpoints, injected as parameters.\n* **Auto generated API schema** using OpenAPI standard. It uses the schema system of your endpoints to extract all the \nnecessary information to generate your API Schema.\n* **Auto generated docs** providing a [Swagger UI] or [ReDoc] endpoint.\n* **Pagination** automatically handled using multiple methods such as limit and offset, page numbers...\n\n## Requirements\n\n* [Python] 3.6+\n* [Starlette] 0.10+\n* [Marshmallow] 3.0+\n\n## Installation\n\n```console\n$ pip install flama\n```\n\n## Example\n\n```python\nfrom marshmallow import Schema, fields, validate\nfrom flama.applications import Flama\n\n\n# Data Schema\nclass Puppy(Schema):\n    id = fields.Integer()\n    name = fields.String()\n    age = fields.Integer(validate=validate.Range(min=0))\n\n\n# Database\npuppies = [\n    {"id": 1, "name": "Canna", "age": 6},\n    {"id": 2, "name": "Sandy", "age": 12},\n]\n\n\n# Application\napp = Flama(\n    components=[],      # Without custom components\n    title="Foo",        # API title\n    version="0.1",      # API version\n    description="Bar",  # API description\n    schema="/schema/",  # Path to expose OpenAPI schema\n    docs="/docs/",      # Path to expose Swagger UI docs\n    redoc="/redoc/",    # Path to expose ReDoc docs\n)\n\n\n# Views\n@app.route("/", methods=["GET"])\ndef list_puppies(name: str = None) -> Puppy(many=True):\n    """\n    description:\n        List the puppies collection. There is an optional query parameter that \n        specifies a name for filtering the collection based on it.\n    responses:\n        200:\n            description: List puppies.\n    """\n    return [puppy for puppy in puppies if puppy["name"] == name]\n    \n\n@app.route("/", methods=["POST"])\ndef create_puppy(puppy: Puppy) -> Puppy:\n    """\n    description:\n        Create a new puppy using data validated from request body and add it \n        to the collection.\n    responses:\n        200:\n            description: Puppy created successfully.\n    """\n    puppies.append(puppy)\n    \n    return puppy\n```\n\n## Dependencies\n\nFollowing Starlette philosophy Flama reduce the number of hard dependencies to those that are used as the core:\n\n* [`starlette`][Starlette] - Flama is a layer on top of it.\n* [`marshmallow`][Marshmallow] - Flama data schemas and validation.\n\nIt does not have any more hard dependencies, but some of them are necessaries to use some features:\n\n* [`pyyaml`][pyyaml] - Required for API Schema and Docs auto generation.\n* [`apispec`][apispec] - Required for API Schema and Docs auto generation.\n* [`python-forge`][python-forge] - Required for pagination.\n* [`sqlalchemy`][SQLAlchemy] - Required for Generic API resources.\n* [`databases`][databases] - Required for Generic API resources.\n\nYou can install all of these with `pip3 install flama[full]`.\n\n## Credits\n\nThat library is heavily inspired by [APIStar] server in an attempt to bring a good amount of it essence to work with \n[Starlette] as the ASGI framework and [Marshmallow] as the schema system.\n\n## Contributing\n\nThis project is absolutely open to contributions so if you have a nice idea, create an issue to let the community \ndiscuss it.\n\n[Python]: https://www.python.org\n[Starlette]: https://starlette.io\n[APIStar]: https://github.com/encode/apistar/tree/version-0.5.x\n[Marshmallow]: https://marshmallow.readthedocs.io/\n[Swagger UI]: https://swagger.io/tools/swagger-ui/\n[ReDoc]: https://rebilly.github.io/ReDoc/\n[pyyaml]: https://pyyaml.org/wiki/PyYAMLDocumentation\n[apispec]: https://apispec.readthedocs.io/\n[python-forge]: https://python-forge.readthedocs.io/\n[SQLAlchemy]: https://www.sqlalchemy.org/\n[databases]: https://github.com/encode/databases',
    'author': 'José Antonio Perdiguero López',
    'author_email': 'perdy@perdy.io',
    'url': 'https://github.com/PeRDy/flama',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
