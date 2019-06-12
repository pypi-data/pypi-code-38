# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['starlette_apispec']

package_data = \
{'': ['*']}

install_requires = \
['apispec>=1.0.0,<2.0.0', 'pyyaml>=5.1,<6.0', 'starlette>=0.11']

setup_kwargs = {
    'name': 'starlette-apispec',
    'version': '1.0.2',
    'description': 'APISpec support for starlette',
    'long_description': '==================\nStarlette APISpec\n==================\n\n    Easy APISpec integration for Starlette\n\n.. image:: https://img.shields.io/travis/Woile/starlette-apispec.svg?style=flat-square\n    :alt: Travis\n    :target: https://travis-ci.org/Woile/starlette-apispec\n\n.. image:: https://img.shields.io/codecov/c/github/Woile/starlette-apispec.svg?style=flat-square\n    :alt: Codecov\n    :target: https://codecov.io/gh/Woile/starlette-apispec\n\n.. image:: https://img.shields.io/pypi/v/starlette-apispec.svg?style=flat-square\n    :alt: PyPI\n    :target: https://pypi.org/project/starlette-apispec/\n\n.. image:: https://img.shields.io/pypi/pyversions/starlette-apispec.svg?style=flat-square\n    :alt: PyPI - Python Version\n    :target: https://pypi.org/project/starlette-apispec/\n\n.. contents::\n    :depth: 2\n\n.. code-block:: python\n\n    from apispec import APISpec\n    from apispec.ext.marshmallow import MarshmallowPlugin\n    from starlette.applications import Starlette\n    from starlette_apispec import APISpecSchemaGenerator\n\n    app = Starlette()\n\n    schemas = APISpecSchemaGenerator(\n        APISpec(\n            title="Example API",\n            version="1.0",\n            openapi_version="3.0.0",\n            info={"description": "explanation of the api purpose"},\n            plugins=[MarshmallowPlugin()],\n        )\n    )\n\n    @app.route("/schema", methods=["GET"], include_in_schema=False)\n    def schema(request):\n        return schemas.OpenAPIResponse(request=request)\n\n\nInstallation\n============\n\n::\n\n    pip install -U starlette-apispec\n\nAlternatively you can do\n\n::\n\n    poetry add starlette-apispec\n\nAbout\n-----\n\nThis library helps you easily document your REST API built with starlette.\n\nStarlette_ is a is a lightweight ASGI framework/toolkit,\nwhich is ideal for building high performance asyncio services.\n\nAPISpec_ supports the `OpenApi Specification <https://github.com/OAI/OpenAPI-Specification>`_\nand it has some useful plugins like marshmallow_ support.\n\nVersion supported: :code:`^1.0.0`\n\n\nUsage\n=====\n\n\nThis example includes marshmallow_ integration\n\n.. code-block:: python\n\n    from apispec import APISpec\n\n    from starlette.applications import Starlette\n    from starlette.endpoints import HTTPEndpoint\n    from starlette.testclient import TestClient\n\n    from starlette_apispec import APISpecSchemaGenerator\n\n\n    app = Starlette()\n\n    schemas = APISpecSchemaGenerator(\n        APISpec(\n            title="Example API",\n            version="1.0",\n            openapi_version="3.0.0",\n            info={"description": "explanation of the api purpose"},\n        )\n    )\n\n\n    @app.websocket_route("/ws")\n    def ws(session):\n        """ws"""\n        pass  # pragma: no cover\n\n\n    @app.route("/users", methods=["GET", "HEAD"])\n    def list_users(request):\n        """\n        responses:\n        200:\n            description: A list of users.\n            examples:\n            [{"username": "tom"}, {"username": "lucy"}]\n        """\n        pass  # pragma: no cover\n\n\n    @app.route("/users", methods=["POST"])\n    def create_user(request):\n        """\n        responses:\n        200:\n            description: A user.\n            examples:\n            {"username": "tom"}\n        """\n        pass  # pragma: no cover\n\n\n    @app.route("/orgs")\n    class OrganisationsEndpoint(HTTPEndpoint):\n        def get(self, request):\n            """\n            responses:\n            200:\n                description: A list of organisations.\n                examples:\n                [{"name": "Foo Corp."}, {"name": "Acme Ltd."}]\n            """\n            pass  # pragma: no cover\n\n        def post(self, request):\n            """\n            responses:\n            200:\n                description: An organisation.\n                examples:\n                {"name": "Foo Corp."}\n            """\n            pass  # pragma: no cover\n\n\n    @app.route("/schema", methods=["GET"], include_in_schema=False)\n    def schema(request):\n        return schemas.OpenAPIResponse(request=request)\n\nMore documentation\n==================\n\nThis package is basically a proxy, so if you wonder how to do something,\nhere are the sources you need:\n\n`Starlette documentation`_\n\n`APISpec documentation`_\n\n\nTesting\n=======\n\n1. Clone the repo\n2. Activate venv ``. venv/bin/activate``\n3. Install dependencies\n\n::\n\n    poetry install\n\n4. Run tests\n\n::\n\n    ./scripts/test\n\n\nContributing\n============\n\n**PRs are welcome!**\n\n\n.. _marshmallow: https://marshmallow.readthedocs.io/\n.. _APISpec: https://apispec.readthedocs.io/en/stable/\n.. _Starlette: https://www.starlette.io/\n.. _`Starlette documentation`: https://www.starlette.io/\n.. _`APISpec documentation`: https://apispec.readthedocs.io/en/stable/\n',
    'author': 'Santiago Fraire Willemoes',
    'author_email': 'santiwilly@gmail.com',
    'url': 'https://github.com/Woile/starlette-apispec',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
