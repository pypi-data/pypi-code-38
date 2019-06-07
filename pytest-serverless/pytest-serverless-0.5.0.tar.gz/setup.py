# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['pytest_serverless']
install_requires = \
['boto3>=1.9,<2.0',
 'moto>=1.3,<2.0',
 'pytest>=4.5,<5.0',
 'python-box>=3.4,<4.0',
 'pyyaml>=5.1,<6.0']

entry_points = \
{'pytest11': ['serverless = pytest_serverless']}

setup_kwargs = {
    'name': 'pytest-serverless',
    'version': '0.5.0',
    'description': 'Automatically mocks resources from serverless.yml file.',
    'long_description': 'pytest-serverless\n---\nMock local resources for serverless framework.\n\n| master | PyPI | Python | Licence |\n| --- | --- | --- | --- |\n| [![Build Status](https://travis-ci.org/whisller/pytest-serverless.svg?branch=master)](https://travis-ci.org/whisller/pytest-serverless) | [![PyPI](https://img.shields.io/pypi/v/pytest-serverless.svg)](https://pypi.org/project/pytest-serverless/) | ![](https://img.shields.io/pypi/pyversions/pytest-serverless.svg) | ![](https://img.shields.io/pypi/l/pytest-serverless.svg) |\n\n## Installation\n```sh\npip install pytest-serverless\n```\n\n## What problem it tries to solve?\nWhen building your project with [serverless](https://serverless.com/) most likely you will create\n[resources](https://serverless.com/framework/docs/providers/aws/guide/resources/) like dynamodb tables, sqs queues, sns topics.\n\nDuring writing tests you will have to mock those in [moto](https://github.com/spulec/moto). \n\nThis pytest plugin tries to automate this process by reading `serverless.yml` file and create\nmocks of resources for you.\n\n## Usage\nMark your test with `@pytest.mark.usefixtures("serverless")`, and rest will be done by plugin.\n```python\nimport boto3\nimport pytest\n\n\n@pytest.mark.usefixtures("serverless")\ndef test():\n    table = boto3.resource("dynamodb").Table("my-microservice.my-table")\n    count_of_items = len(table.scan()["Items"])\n    assert count_of_items == 0\n```\n\n## Supported resources\n### AWS::DynamoDB::Table\n### AWS::SQS::Queue\n\n## Issues?\nPlugin is in early stage of development, so you might find some bugs or missing functionality.\n\nIf possible create pull request (with tests) that fixes particular problem.\n',
    'author': 'Daniel Ancuta',
    'author_email': 'whisller@gmail.com',
    'url': 'https://github.com/whisller/pytest-serverless',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
