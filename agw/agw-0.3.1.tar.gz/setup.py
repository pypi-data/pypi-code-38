# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['agw', 'agw.cli']

package_data = \
{'': ['*']}

install_requires = \
['cutie>=0.2.2,<0.3.0', 'docopt>=0.6.2,<0.7.0', 'pyautogui>=0.9.41,<0.10.0']

extras_require = \
{':sys_platform == "darwin"': ['pyobjc-core>=5.1,<6.0',
                               'pyobjc-framework-Quartz>=5.1,<6.0']}

entry_points = \
{'console_scripts': ['agw = agw.cli:main']}

setup_kwargs = {
    'name': 'agw',
    'version': '0.3.1',
    'description': 'A pyautogui wrapper library for data entry macros.',
    'long_description': None,
    'author': 'Mark Gemmill',
    'author_email': 'contact@markgemmill.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
