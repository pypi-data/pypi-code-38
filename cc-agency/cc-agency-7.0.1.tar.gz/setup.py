# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cc_agency',
 'cc_agency.broker',
 'cc_agency.broker.routes',
 'cc_agency.commons',
 'cc_agency.commons.schemas',
 'cc_agency.controller',
 'cc_agency.tools',
 'cc_agency.tools.create_broker_user',
 'cc_agency.tools.create_db_user',
 'cc_agency.tools.drop_db_collections',
 'cc_agency.trustee']

package_data = \
{'': ['*']}

install_requires = \
['cc-core>=7.0,<7.1',
 'cryptography>=2.2,<3.0',
 'docker>=3.4,<4.0',
 'flask>=1.0,<2.0',
 'jsonschema>=3.0,<4.0',
 'pymongo>=3.7,<4.0',
 'pyzmq>=17.0,<18.0',
 'requests>=2.18,<3.0',
 'ruamel.yaml>=0.15,<0.16']

entry_points = \
{'console_scripts': ['ccagency = cc_agency.tools.main:main',
                     'ccagency-controller = cc_agency.controller.main:main',
                     'ccagency-trustee = cc_agency.trustee.main:main']}

setup_kwargs = {
    'name': 'cc-agency',
    'version': '7.0.1',
    'description': 'CC-Agency is part of the Curious Containers project. It connects to a cluster of docker-engines for the distributed execution of reproducible data-driven experiments defined in RED format.',
    'long_description': '# CC-Agency\n\nCC-Agency is part of the Curious Containers project. It connects to a cluster of docker-engines for the distributed execution of reproducible data-driven experiments defined in RED format.\n\nFor more information please refer to the Curious Containers [documentation](https://www.curious-containers.cc/).\n\n## Acknowledgements\n\nThe Curious Containers software is developed at [CBMI](https://cbmi.htw-berlin.de/) (HTW Berlin - University of Applied Sciences). The work is supported by the German Federal Ministry of Economic Affairs and Energy (ZIM project BeCRF, grant number KF3470401BZ4), the German Federal Ministry of Education and Research (project deep.TEACHING, grant number 01IS17056 and project deep.HEALTH, grant number 13FH770IX6) and HTW Berlin Booster.\n',
    'author': 'Christoph Jansen',
    'author_email': 'Christoph.Jansen@htw-berlin.de',
    'url': 'https://www.curious-containers.cc/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
