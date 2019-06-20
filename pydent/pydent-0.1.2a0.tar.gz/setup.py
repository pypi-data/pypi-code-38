# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pydent',
 'pydent._version',
 'pydent.marshaller',
 'pydent.models',
 'pydent.planner',
 'pydent.utils']

package_data = \
{'': ['*']}

install_requires = \
['inflection>=0.3.1,<0.4.0',
 'nest-asyncio>=1.0,<2.0',
 'networkx>=2.3,<3.0',
 'pandas>=0.24.2,<0.25.0',
 'requests>=2.22,<3.0',
 'tqdm>=4.32,<5.0']

entry_points = \
{'console_scripts': ['civerify = pydent:_version.verify_ci',
                     'upver = pydent:_version.pull_version',
                     'version = pydent:_version.get_version']}

setup_kwargs = {
    'name': 'pydent',
    'version': '0.1.2a0',
    'description': "Aquarium's Python API for planning, executing, and analyzing scientific experiments.",
    'long_description': '# Trident: Aquarium API Scripting\n\n[![CircleCI](https://circleci.com/gh/klavinslab/trident/tree/master.svg?style=svg&circle-token=88677c59698d55a127a080cba9ca025cf8072f6c)](https://circleci.com/gh/klavinslab/trident/tree/master)\n[![PyPI version](https://badge.fury.io/py/pydent.svg)](https://badge.fury.io/py/pydent)\n\nTrident is the python API scripting for Aquarium.\n\n## Documentation\n\n[API documentation can be found here at klavinslab.org/trident](http://www.klavinslab.org/trident)\n\n## Requirements\n\n* Python > 3.4\n* An Aquarium login\n\n## Quick installation\n\nPydent can be installed using `pip3`.\n\n```\n    pip3 install pydent\n```\n\nor upgraded using\n\n```\n    pip3 install pydent --upgrade\n```\n\n## Basic Usage\n\n### Logging in\n\n```python\nfrom pydent import AqSession\n\n# open a session\nmysession = AqSession("username", "password", "www.aquarium_nursery.url")\n\n# find a user\nu = mysession.User.find(1)\n\n# print the user data\nprint(u)\n```\n\n### Models\n\n```python\nprint(mysession.models)\n```\n\n#### Finding models\n\n* By name: `nursery.SampleType.find_by_name("Primer")`\n\n* By ID: `nursery.SampleType.find(1)`\n\n* By property: `nursery.SampleType.where({\'name\': \'Primer\'})`\n\n* All models: `nursery.SampleType.all()`\n\n#### Getting nested data\n\n```python\n# samples are linked to sample_type\nprimer_type = mysession.SampleType.find_by_name("Primer")\nprimers = primer_type.samples\n\n# and sample type is linked to sample\np = primers[0]\nprint(p.sample_type)\n```\n\n#### Available nested relationships\n\n```python\nprimer_type = mysession.SampleType.find(1)\nprint(primer_type.relationships)\n```\n\n',
    'author': 'jvrana',
    'author_email': 'justin.vrana@gmail.com',
    'url': 'https://www.github.com/klavinslab/trident',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
