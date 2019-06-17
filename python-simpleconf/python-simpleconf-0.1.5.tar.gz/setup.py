# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['simpleconf']
install_requires = \
['python-box>=3.4.1,<4.0.0']

extras_require = \
{'dotenv': ['python-dotenv'], 'toml': ['toml'], 'yaml': ['pyyaml']}

setup_kwargs = {
    'name': 'python-simpleconf',
    'version': '0.1.5',
    'description': 'Simple configuration management with python.',
    'long_description': "# simpleconf\nSimple configuration management with python\n\n## Installation\n```shell\n# released version\npip install python-simpleconf\n# lastest version\npip install git+https://github.com/pwwang/simpleconf\n```\n\n## Features\n- Simple! Simple! Simple!\n- Profile switching\n- Supported formats:  \n  - `.ini/.cfg/.config` (using `ConfigParse`)\n  - `.env` (using `python-dotenv`)\n  - `.yaml/.yml` (using `pyyaml`)\n  - `.toml` (using `toml`)\n  - `.json` (using `json`)\n  - systme environment variables \n  - python dictionaries\n- Value casting\n\n## Usage\n### Loading configurations\n```python\nfrom simpleconf import config\n\n# load a single file\nconfig._load('~/xxx.ini')\n# load multiple files\nconfig._load(\n   '~/xxx.ini', '~/xxx.env', '~/xxx.yaml', '~/xxx.toml', \n   '~/xxx.json', 'simpleconf.osenv', {'default': {'a': 3}}\n)\n```\n\nFor `.env` configurations, variable name uses the profile name as prefix. For example:\n```shell\ndefault_a=1\ndefault_b=py:1\ntest_a=2\n```\n```python\nconfig._load('xxx.env')\nconfig.a == '1'\nconfig.b == 1\nconfig._use('test')\nconfig.a == '2'\nconfig._revert()\nconfig.a == '1'\n```\nUse `with` to temporarily switch profile:\n```python\nconfig._load('xxx.env')\nconfig.a == '1'\nconfig.b == 1\nwith config._with('test') as cfg\n   config.a == '2'\nconfig.a == '1'\n```\n\nFor `.osenv` configurations, for example `simpleconf.osenv`, only variables with names start with `SIMPLECONF_` will be loaded, then the upper-cased profile name should follow.  \n```python\nos.environ['SIMPLECONF_DEFAULT_A'] = 1\nos.environ['SIMPLECONF_test_A'] = 2\nconfig._load('simpleconf.osenv')\nconfig.A == 1\nconfig._use('test')\nconfig.A == 2\n```\n\nPriority is decided by the order that configurations being loaded.  \nIn the above example, `config.A` is `3` anyway no matter whatever value is assigned in prior configurations.  \n\nHint: to get system environment variables always have the highest priority, they should be always loaded last.\n\n### Switching profiles\nLike `ConfigParse`, the default profile (section) will be loaded first.\n\n```ini\n[default]\na = 1\nb = 2\n\n[test]\na = 3\n```\n\n```python\nconfig._load('xxx.ini')\n\nconfig.a == 1\nconfig.b == 2\n\nconfig._use('test')\nconfig.a == 3\nconfig.b == 2\n```\n\nNote that `simpleconf` profiles are case-insensitive, and we use uppercase names for the first-layer configurations:  \n```yaml\ndefault:\n   complicated_conf:\n      a = 9\n```\n\n```python\nconfig._load('xxx.yaml')\nconfig.complicated_conf.a == 9\n```\n\n### Getting configuration values\n\n`simpleconf.config` is an instance of [`ConfigBox`](https://github.com/cdgriffith/Box#configbox) from `python-box`. All methods supported by `ConfigBox` is applicable with `simpleconf.config`.  \nAdditionally, we also extended `get` method to allow user-defined `cast` method:  \n```python\nconfig._load('xxx.ini')\nconfig.int('A') == 1\nconfig.float('A') == 1.0\n\ndef version(x):\n\treturn '%s.0.0' % x\n\nconfig.get('A', cast = version) == '1.0.0'\n```\n\n### None-profile mode\n```yaml\na: 1\nb: 2\n```\n\n```python\nfrom simpleconf import Config\nconfig = Config(with_profile = False)\nconfig._load('xxx.yaml')\nconfig.A == 1\nconfig.B == 2\n```\n\nNote that in .ini configuration file, you still have to use the section name `[DEFAULT]`\n",
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'url': 'https://github.com/pwwang/simpleconf',
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
