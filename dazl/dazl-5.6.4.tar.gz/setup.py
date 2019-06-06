# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dazl',
 'dazl._gen',
 'dazl._gen.com',
 'dazl._gen.com.digitalasset',
 'dazl._gen.com.digitalasset.ledger',
 'dazl._gen.com.digitalasset.ledger.api',
 'dazl._gen.com.digitalasset.ledger.api.v1',
 'dazl._gen.com.digitalasset.ledger.api.v1.admin',
 'dazl._gen.com.digitalasset.ledger.api.v1.testing',
 'dazl._gen.da',
 'dazl._gen.google',
 'dazl._gen.google.rpc',
 'dazl._gen.grpc',
 'dazl._gen.grpc.health',
 'dazl._gen.grpc.health.v1',
 'dazl.cli',
 'dazl.client',
 'dazl.damlast',
 'dazl.damleval',
 'dazl.damlsdk',
 'dazl.metrics',
 'dazl.model',
 'dazl.plugins',
 'dazl.plugins.capture',
 'dazl.pretty',
 'dazl.protocols',
 'dazl.protocols.admin',
 'dazl.protocols.v0',
 'dazl.protocols.v1',
 'dazl.protocols.v1.model',
 'dazl.rules',
 'dazl.server',
 'dazl.util']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp',
 'google-auth',
 'grpcio>=1.20.1',
 'oauthlib',
 'protobuf>=3.7.1',
 'pyyaml',
 'requests',
 'semver',
 'toposort']

extras_require = \
{':python_version >= "3.6.0" and python_version < "3.7.0"': ['dataclasses'],
 'prometheus': ['prometheus_client'],
 'pygments': ['pygments']}

entry_points = \
{'console_scripts': ['dazl = dazl.cli:main']}

setup_kwargs = {
    'name': 'dazl',
    'version': '5.6.4',
    'description': 'high-level Ledger API client for DAML ledgers',
    'long_description': 'dazl\n====\n\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/digital-asset/dazl-client/blob/master/LICENSE)\n<a href="https://circleci.com/gh/digital-asset/dazl-client">\n<img src="https://circleci.com/gh/digital-asset/dazl-client.svg?style=svg">\n</a>\n\nCopyright 2019 Digital Asset (Switzerland) GmbH and/or its affiliates. All Rights Reserved.\nSPDX-License-Identifier: Apache-2.0\n\n\nRich Python bindings for accessing Ledger API-based applications.\n\nRequirements\n------------\n* Python 3.6+\n* [Pipenv](https://pipenv.readthedocs.io/en/latest/)\n* Although not strictly required for building, you\'ll probably want the [DAML SDK](https://www.daml.com)\n\nExamples\n--------\n\nAll of the examples below assume you imported `dazl`.\n\nConnect to the ledger and submit a single command:\n\n```py\nwith dazl.simple_client(\'http://localhost:7600\', \'Alice\') as client:\n    client.submit_create(\'Alice\', \'My.Template\', { someField: \'someText\' })\n```\n\nConnect to the ledger as a single party, print all contracts, and close:\n\n```py\nwith dazl.simple_client(\'http://localhost:7600\', \'Alice\') as client:\n    # wait for the ACS to be fully read\n    client.ready()\n    contract_dict = client.find_active(\'*\')\nprint(contract_dict)\n```\n\nConnect to the ledger as multiple parties:\n\n```py\nnetwork = dazl.Network()\nnetwork.set_config(url=\'http://localhost:7600\')\n\nalice = network.simple_party(\'Alice\')\nbob = network.simple_party(\'Bob\')\n\n@alice.ledger_ready()\ndef set_up(event):\n    currency_cid, _ = await event.acs_find_one(\'My.Currency\', {"currency": "USD"})\n    return dazl.create(\'SomethingOf.Value\', {\n        \'amount\': 100,\n        \'currency\': currency_cid,\n        \'from\': \'Accept\',\n        \'to\': \'Bob\' })\n\n@bob.ledger_created(\'SomethingOf.Value\')\ndef on_something_of_value(event):\n    return dazl.exercise(event.cid, \'Accept\', { \'message\': \'Thanks!\' })\n\nnetwork.start()\n```\n\n\nBuilding locally\n----------------\n```sh\ncd python && pipenv run package\n```\n\nTests\n-----\n\n```sh\ncd python && pipenv run test\n```\n',
    'author': 'Davin K. Tanabe',
    'author_email': 'davin.tanabe@digitalasset.com',
    'url': 'https://github.com/digital-asset/dazl-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
