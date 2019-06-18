# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['moldyn',
 'moldyn.processing',
 'moldyn.simulation',
 'moldyn.ui',
 'moldyn.utils']

package_data = \
{'': ['*'],
 'moldyn': ['data/*'],
 'moldyn.simulation': ['templates/*'],
 'moldyn.ui': ['qt/*']}

install_requires = \
['PyQt5>=5.11.3,<6.0.0',
 'datreant>=1.0,<2.0',
 'imageio_ffmpeg>=0.3.0,<0.4.0',
 'matplotlib>=3.1,<4.0',
 'moderngl>=5.5,<6.0',
 'numexpr>=2.6,<3.0',
 'numpy>=1.16,<2.0',
 'pillow>=6.0,<7.0',
 'pyqtgraph>=0.10.0,<0.11.0',
 'scipy>=1.3,<2.0']

entry_points = \
{'console_scripts': ['moldyn-gui = moldyn:gui']}

setup_kwargs = {
    'name': 'open-moldyn',
    'version': '0.0.1.dev1',
    'description': 'Tools for molecular dynamics simulation and analysis',
    'long_description': '# open-moldyn\n\nOpen Molecular Dynamics tools in Python 3\n\nread the doc on https://open-moldyn.readthedocs.io/en/latest/',
    'author': 'Arthur Luciani, Alexandre Faye-Bedrin',
    'author_email': None,
    'url': 'https://github.com/open-moldyn/moldyn',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
