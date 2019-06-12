# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['reprobench',
 'reprobench.core.bootstrap',
 'reprobench.executors',
 'reprobench.managers',
 'reprobench.managers.local',
 'reprobench.managers.slurm',
 'reprobench.statistics.plots',
 'reprobench.statistics.plots.cactus',
 'reprobench.statistics.tables',
 'reprobench.task_sources.doi']

package_data = \
{'': ['*'],
 'reprobench': ['console/*',
                'core/*',
                'statistics/*',
                'task_sources/*',
                'tools/*']}

install_requires = \
['click>=7.0,<8.0',
 'loguru>=0.2.5,<0.3.0',
 'numpy>=1.16,<2.0',
 'pathspec>=0.5.9,<0.6.0',
 'requests>=2.21,<3.0',
 'retrying>=1.3,<2.0',
 'sshtunnel>=0.1.4,<0.2.0',
 'strictyaml>=1.0,<2.0',
 'tqdm>=4.31,<5.0']

extras_require = \
{'all': ['psmon>=1.1.0,<2.0.0',
         'psutil>=5.6,<6.0',
         'py-cpuinfo>=4,<6',
         'msgpack-python>=0.5.6,<0.6.0',
         'pyzmq>=18.0,<19.0',
         'gevent>=1.4,<2.0',
         'peewee>=3.9,<4.0',
         'apsw>=3.9,<4.0',
         'configspace>=0.4.10,<0.5.0',
         'pandas>=0.24.2,<0.25.0',
         'papermill>=0.19.1,<1.1.0'],
 'analytics': ['peewee>=3.9,<4.0',
               'apsw>=3.9,<4.0',
               'pandas>=0.24.2,<0.25.0',
               'papermill>=0.19.1,<1.1.0'],
 'client': ['msgpack-python>=0.5.6,<0.6.0', 'pyzmq>=18.0,<19.0'],
 'pcs': ['configspace>=0.4.10,<0.5.0'],
 'psmon': ['psmon>=1.1.0,<2.0.0'],
 'server': ['msgpack-python>=0.5.6,<0.6.0',
            'pyzmq>=18.0,<19.0',
            'gevent>=1.4,<2.0',
            'peewee>=3.9,<4.0',
            'apsw>=3.9,<4.0'],
 'sysinfo': ['psutil>=5.6,<6.0', 'py-cpuinfo>=4,<6']}

entry_points = \
{'console_scripts': ['reprobench = reprobench.console.main:cli']}

setup_kwargs = {
    'name': 'reprobench',
    'version': '0.11.0.dev13',
    'description': 'Reproducible Benchmark for Everyone',
    'long_description': '# reprobench\n\n[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8163f0d20e9145cf9379a56f0383287c)](https://app.codacy.com/app/rkkautsar/reprobench?utm_source=github.com&utm_medium=referral&utm_content=rkkautsar/reprobench&utm_campaign=Badge_Grade_Dashboard)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/reprobench.svg)](https://pypi.org/project/reprobench)\n[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=rkkautsar/reprobench)](https://dependabot.com)\n[![Anaconda-Server Badge](https://anaconda.org/rkkautsar/reprobench/badges/installer/conda.svg)](https://conda.anaconda.org/rkkautsar)\n\n## Development Guide\n\n### Installing locally\n\nWe recommend using Anaconda.\n\n```sh\n$ conda env create -f environment.yml\n$ conda activate reprobench\n```\n',
    'author': 'Rakha Kanz Kautsar',
    'author_email': 'rkkautsar@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
