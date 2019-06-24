# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['clikit',
 'clikit.adapter',
 'clikit.api',
 'clikit.api.application',
 'clikit.api.args',
 'clikit.api.args.format',
 'clikit.api.command',
 'clikit.api.config',
 'clikit.api.event',
 'clikit.api.formatter',
 'clikit.api.io',
 'clikit.api.resolver',
 'clikit.args',
 'clikit.args.inputs',
 'clikit.config',
 'clikit.formatter',
 'clikit.handler',
 'clikit.handler.help',
 'clikit.io',
 'clikit.io.input_stream',
 'clikit.io.output_stream',
 'clikit.resolver',
 'clikit.ui',
 'clikit.ui.alignment',
 'clikit.ui.components',
 'clikit.ui.help',
 'clikit.ui.layout',
 'clikit.ui.style',
 'clikit.utils']

package_data = \
{'': ['*']}

install_requires = \
['pastel>=0.1.0,<0.2.0', 'pylev>=1.3,<2.0']

extras_require = \
{':python_version >= "2.7" and python_version < "2.8"': ['enum34>=1.1,<2.0'],
 ':python_version >= "2.7" and python_version < "2.8" or python_version >= "3.4" and python_version < "3.5"': ['typing>=3.6,<4.0']}

setup_kwargs = {
    'name': 'clikit',
    'version': '0.3.0',
    'description': 'CliKit is a group of utilities to build beautiful and testable command line interfaces.',
    'long_description': '# CliKit\n\nCliKit is a group of utilities to build beautiful and testable command line interfaces.\n\nThis is at the core of [Cleo](https://github.com/sdispater/cleo).\n',
    'author': 'Sébastien Eustace',
    'author_email': 'sebastien@eustace.io',
    'url': 'https://github.com/sdispater/clikit',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
