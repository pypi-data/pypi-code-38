# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['settingscascade']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=2.10,<2.11', 'sortedcontainers>=2.1,<2.2', 'toml>=0.10,<0.11']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.5,<0.6']}

setup_kwargs = {
    'name': 'settingscascade',
    'version': '0.1',
    'description': 'Cascade settings from multiple levels of specificity',
    'long_description': 'Settings cascade is designed for situations where you need to merge\nconfiguration settings from different hierarchical sources. The model\nis the way that CSS cascades onto elements.\n\nSettings have the concept of levels. The system is based on Toml, so\nthe root of the setting is always a map. Inside of that, each key is\neither a level or a setting. (This means you can\'t reuse a level name\nfor a setting!) In css parlance, a level would be an element type.\n\nIn the below example `val_a` is a key at the root level. `task` is a\nlevel. A level can either be a map or a list of maps. when you use a\nlist of maps, each map has a key called `name` - this is the key used\nto access settings of that map. This `name` key would map roughly to\nthe class of a css element. If it is left out, or the level is just set\ndirectly to a mapping, the selector is None (`tasks.None` for this one-)\n\nval_a = "a"\nval_b = "fallback"\n\n[[tasks]]\nname = "a"\nval_b = "1"\n\n[[tasks]]\nname = "b"\nval_b = "3"\n\n[[tasks]]\nval_b = "7"\n\nOnce the Config is set up, you can access variables by setting up your context\nand then just grabbing them. If there is no setting that matches your context,\nAttributeError is raised. If there are more then one, the MOST specific one is\nreturned. Below the selecor `environments=None`.setting_a would return "outer",\nwhile `tasks=default_task, environments=none` would return "inner". \n`tasks=default_task`.setting_a would return and error though. You can get a\nsetting that is LESS specific then your context, but not one that is MORE\nspecific. `tasks=None` could still get tasks.task_setting = "less"\n\n[environments]\nsetting_a = "outer"\n\n[[tasks]]\n\tname = "default_task"\n\ttask_setting = "less"\n\t[tasks.environments]\n\t\tsetting_a = "inner"\n\nIn your python code, this is accomplished with a context manager.\n\n```python\nwith MyConfig.context(tasks="default_task", "environments"=None):\n\tassert MyConfig.setting_a == "inner"\n```\n',
    'author': 'Paul Becotte',
    'author_email': 'pjbecotte@gmail.com',
    'url': 'https://gitlab.com/pjbecotte/settingscascade',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
