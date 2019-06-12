# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyparam']

package_data = \
{'': ['*']}

install_requires = \
['colorama', 'python-simpleconf>=0.1.4,<0.2.0']

setup_kwargs = {
    'name': 'pyparam',
    'version': '0.1.5',
    'description': 'Powerful parameter processing.',
    'long_description': "# pyparam\n[![pypi][1]][2] [![pypi][10]][11] [![travis][3]][4] [![docs][18]][19] [![codacy quality][5]][6] [![codacy quality][7]][6] ![pyver][8]\n\nPowerful parameter processing\n\n## Features\n- Command line argument parser (with subcommand support)\n- `list/array`, `dict`, `positional` and `verbose` options support\n- Type overwriting for parameters\n- Rich API for Help page redefinition\n- Parameter loading from configuration files\n- Shell completions\n\n## Installation\n```shell\npip install pyparam\n# install latest version via poetry\ngit clone https://github.com/pwwang/pyparam.git\ncd pyparam\npoetry install\n```\n\n## Basic usage\n\n`examples/basic.py`\n```python\nfrom pyparam import params\n# define arguments\nparams.version      = False\nparams.version.desc = 'Show the version and exit.'\nparams.quiet        = False\nparams.quiet.desc   = 'Silence warnings'\nparams.v            = 0\n# verbose option\nparams.v.type = 'verbose'\n# alias\nparams.verbose = params.v\n# list/array options\nparams.packages      = []\nparams.packages.desc = 'The packages to install.'\nparams.depends       = {}\nparams.depends.desc  = 'The dependencies'\n\nprint(params._parse())\n```\n```shell\n> python example/basic.py\n```\n![help][9]\n\n```shell\n> python examples/basic.py -vv --quiet \\\n\t--packages numpy pandas pyparam \\\n\t--depends.completions 0.0.1\n{'h': False, 'help': False, 'H': False,\n 'v': 2, 'verbose': 2, 'version': False,\n 'V': False, 'quiet': True, 'packages': ['numpy', 'pandas', 'pyparam'],\n 'depends': {'completions': '0.0.1'}}\n```\n\n## Documentation\n[ReadTheDocs][19]\n\n\n[1]: https://img.shields.io/pypi/v/pyparam.svg?style=flat-square\n[2]: https://pypi.org/project/pyparam/\n[3]: https://img.shields.io/travis/pwwang/pyparam.svg?style=flat-square\n[4]: https://travis-ci.org/pwwang/pyparam\n[5]: https://img.shields.io/codacy/grade/a34b1afaccf84019a6b138d40932d566.svg?style=flat-square\n[6]: https://app.codacy.com/project/pwwang/pyparam/dashboard\n[7]: https://img.shields.io/codacy/coverage/a34b1afaccf84019a6b138d40932d566.svg?style=flat-square\n[8]: https://img.shields.io/pypi/pyversions/pyparam.svg?style=flat-square\n[9]: https://raw.githubusercontent.com/pwwang/pyparam/master/docs/static/help.png\n[10]: https://img.shields.io/github/tag/pwwang/pyparam.svg?style=flat-square\n[11]: https://github.com/pwwang/pyparam\n[18]: https://img.shields.io/readthedocs/pyparam.svg?style=flat-square\n[19]: https://pyparam.readthedocs.io/en/latest/\n",
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'url': 'https://github.com/pwwang/pyparam',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
