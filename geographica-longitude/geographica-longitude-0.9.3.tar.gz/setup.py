# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['longitude',
 'longitude.aiohttp',
 'longitude.core',
 'longitude.core.caches',
 'longitude.core.common',
 'longitude.core.data_sources',
 'longitude.core.data_sources.postgres',
 'longitude.core.tests',
 'longitude.samples']

package_data = \
{'': ['*']}

install_requires = \
['aioauth-client>=0.16.2,<0.17.0',
 'aiohttp>=3.5,<4.0',
 'apispec>=1.3,<2.0',
 'aredis>=1.1,<2.0',
 'asyncio>=3.4,<4.0',
 'carto==1.4',
 'cartoframes>=0.9.0,<0.10.0',
 'environs>=4.1,<5.0',
 'flasgger>=0.9.2,<0.10.0',
 'flask>=1.0,<2.0',
 'flask_cors>=3.0,<4.0',
 'geolibs-cartoasync>=0.0.4,<0.0.5',
 'inflect>=2.1,<3.0',
 'marshmallow>=2.19,<3.0',
 'pandas>=0.24.1,<0.25.0',
 'psycopg2-binary==2.7.7',
 'pyjwt>=1.7,<2.0',
 'redis==3.1',
 'shapely>=1.6,<2.0',
 'sqlalchemy>=1.3,<2.0']

setup_kwargs = {
    'name': 'geographica-longitude',
    'version': '0.9.3',
    'description': 'A longitudinal lib',
    'long_description': '# Longitude\n\nA **new** bunch of middleware functions to build applications on top of CARTO.\n\n## Roadmap\n\n- [ ] Database model\n  - [x] CARTO data source\n    - [x] Basic parametrized queries (i.e. templated queries)\n    - [x] Protected parametrized queries (i.e. avoiding injection)\n    - [ ] Bind/dynamic parameters in queries (server-side render)\n  - [x] Postgres data source\n    - [x] psycopg2\n    - [x] SQLAlchemy\n  - [x] Cache\n    - [x] Base cache\n      - [x] Put\n      - [x] Get\n      - [x] Key generation\n      - [x] Flush\n      - [x] Tests\n    - [x] Ram Cache\n      - [x] Tests\n    - [x] Redis Cache\n      - [x] Tests \n  - [x] Documentation\n    - [x] Sample scripts\n  - [x] Unit tests\n  - [x] Sample scripts\n \n- [x] Config\n \n- [x] CI PyPi versioning\n\n- [ ] COPY operations\n  - [x] Carto\n    - [x] COPY FROM\n    - [ ] COPY TO\n  - [x] Postgres\n    - [x] COPY FROM\n    - [ ] COPY TO\n  - [x] SQLAlchemy\n    - [x] COPY FROM\n    - [ ] COPY TO\n \n- [ ] Validations\n  - [ ] Marshmallow\n    - [ ] Wrapper (?)\n    - [ ] Documentation\n \n- [x] Swagger\n  - [ ] Decorators\n  - [x] Flassger (?)\n  - [ ] OAuth integration\n  - [x] Postman integration\n  - [ ] Documentation\n  \n- [ ] SQL Alchemy\n  - [ ] Model definition\n  - [ ] Jenkins integration\n  - [ ] Documentation\n\n- [ ] OAuth\n  - [x] OAuth2 with Carto (onprem)\n  - [ ] Role mapping\n  - [ ] Token storage\n  - [ ] Documentation\n  \n## As final user...\n\nHow to use:\n```bash\npip install longitude\n```\n\nOr:\n```bash\npipenv install longitude\n```\n\nOr:\n```bash\npoetry add longitude\n```\n\nOr install from GitHub:\n```bash\npip install -e git+https://github.com/GeographicaGS/Longitude#egg=longitude\n```\n\n## As developer...\n\n### First time\n\n1. Install ```poetry``` using the [recommended process](https://github.com/sdispater/poetry#installation)\n    1. poetry is installed globally as a tool\n    1. It works along with virtualenvironments\n1. Create a virtual environment for Python 3.x (check the current development version in ```pyproject.toml```)\n    1. You can create it wherever you want but do not put it inside the project\n    1. A nice place is ```$HOME/virtualenvs/longitude```\n1. Clone the ```longitude``` repo\n1. `cd` to the repo and:\n    1. Activate the virtual environment: `. ~/virtualenvs/longitude/bin/activate`\n    1. Run `poetry install`\n1. Configure your IDE to use the virtual environment\n\n### Daily\n\n1. Remember to activate the virtual environment \n\n### Why Poetry?\n\nBecause it handles development dependencies and packaging with a single file (```pyproject.toml```), which is [already standard](https://flit.readthedocs.io/en/latest/pyproject_toml.html).\n\n## Sample scripts\n\nThese are intended to be used with real databases (i.e. those in your profile) to check features of the library. They must be run from the virtual environment.\n\n## Testing and coverage \n\nThe [```pytest-cov```](https://pytest-cov.readthedocs.io/en/latest/) plugin is being used. Coverage configuration is at ```.coveragerc``` (including output folder).\n\nYou can run something like: ```pytest --cov-report=html --cov=core core``` and the results will go in the defined html folder.\n\nThere is a bash script called ```generate_core_coverage.sh``` that runs the coverage analysis and shows the report in your browser.\n',
    'author': 'Geographica',
    'author_email': 'hello@geographica.com',
    'url': 'https://github.com/GeographicaGS/Longitude',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
