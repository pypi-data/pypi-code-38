# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['settingscascade']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=2.10,<2.11', 'sortedcontainers>=2.1,<2.2']

setup_kwargs = {
    'name': 'settingscascade',
    'version': '0.2',
    'description': 'Cascade settings from multiple levels of specificity',
    'long_description': '# Intro\n\nSettings cascade is designed for situations where you need to merge\nconfiguration settings from different hierarchical sources. The model\nis the way that CSS cascades onto elements.\n\n## Getting Started\n\nYour config will have 2  things- selectors and rules. Each section\nof rules will be associated with a selector, and then when your app\ntries to look up a rule, the most specific rule whose selector matches\nthe current context will be returned. Consider\n\n.env:\n\tval_a = "a"\n\nclass.env:\n\tval_a = "b"\n\t\nIf you try to look up "val_a" from the context "module.env" it would\nreturn "a", while from context "class.env" it would return "b". A rule\nsection must match ALL elements of the context to be used, but not all\nelements of the context need to be used in the selector.\n\nThe rule sections are loaded from a dictionary (which can be created \nfrom any file type you like, json, yaml, toml... whatever). This happens\nby creating a ConfigManager\n\n```python\nfrom pathlib import Path\nfrom toml import loads\nfrom settingscascade import ConfigManager\n\n# Levels is a list of valid "element" identifiers in your config\n# any key that doesn\'t appear hear will be treated as rule. Elements\n# ordering has no special meaning, and they can be nested in any order\n# or depth in the context or rule selectors\nlevels = {"environment", "task"}\n\n# data must be a dictionary or a list of dictionaries\ndata =  loads(Path("pyproject.toml").read_text())\nconfig = ConfigManager(data, levels)\n```\n\n## Data format\n\nThe data is then read based on the keys in the dictionary(s). Each key\nwill look up element names using the key. There are two different\nways to add classifiers or ids- first, you can just add them directly\nas though it were css. The toml file below has four sections. The specifiers\nare read as `environment`, `.prod`, `environment.prod`, \n`environment.prod task`. This winds up working exactly like CSS, and is\nthe most obvious way to use this library.\n\n```toml\n[environment]\nsetting_a = "outer"\n\n[".prod"]\nsome_setting = "production"\n\n["environment.prod"]\n\tname = "default_task"\n\ttask_setting = "less"\n["environment.prod".task]\n\tsetting_a = "inner"\n```\n\nIf for whatever reason adding the extra info to the keys isn\'t possible,\nthe library will look for magic names `_name_` and `_id_` to pull them\nfrom the object. Below, the selector for section 2 would be \n`tasks.default_task`\n\n```toml\n[environment]\nsetting_a = "outer"\n\n[[task]]\n\t_name_ = "default_task"\n\ttask_setting = "less"\n\t[task.environment]\n\t\tsetting_a = "inner"\n\n[[task]]\ntask_setting = "more"\n\n```\nNote there are two special cases to consider from the previous\nexample. The first is a list of dictionaries (like `task`). In\nthis case the library will use the key of the list to build the\nselector for each element of the list. In this case it would be\n`task.default_task` and `task` respectively. The other is that\nthe second list there has no _name_ variable, so will just get\nthe selector from the list- if there were more then one item in\nthat list with the same situation, they would override each other.\n\n## Accessing Config values\n\nOnce the data is loaded, it can be accessed anywhere in your\napplication by just accessing the attribute on your config\nobject.\n```python\nvar = config.my_var\n```\n\nThat would use an empty selector for the searchso would only match\nrules from the root context. If you wanted settings from further\ndown the tree, you set the context to search in first-\n\n```python\nwith config.context("task.default_task environment"):\n\tassert config.setting_a == "inner"\n```\n\n## Jinja templating\nAny string value returned from your config will be run through\na Jinja2 template resolver before being returned. Any missing\nvariables in the templates will be looked up in the config\nusing the current context.\n\n```python\nconfig = ConfigManager({\n\t"basic": "Var {{someval}}",\n\t"someval": "default", \n\t"task": {"someval": "override"}\n}, {"task"})\n\nconfig.basic == "Var default"\nwith config.context("task"):\n\tconfig.basic == "Var override"\n\n```\nThis could allow you to be more flexible when merging data from\nmultiple sources such as default, org, and user level config files.\nYou can even add custom filters to the environment such as\n```python\nconfig = ConfigManager({\n\t"myval": "{{ (1, 3) | add_two_numbers }}"\n})\nconfig.add_filter("add_two_numbers", lambda tup: tup[0] + tup[1])\nconfig.myval == "4"\n```\n\n## Detailed config to selector rules:\nParse map into selector/ruleset\n! Any key that is not an element is considered to be a rule !\nThere are two more special keynames - _name_ and _id_. If these\nare contained in a map, they update the selector of the parent\nkey\n\n`keyname`\n"keyname": {...\n\n`keyname.typename`\n"keyname.typename": {...\n\n`keyname.typename`\n"keyname": {"_name_": "typename, ...\n\n`keyname#id`\n"keyname": {"_id_": "id", ...\n\n`keyname.typename`\n"keyname": [{"_name_": "typename", ...\n\n`keyname otherkeyname.nestedname`\n"keyname": {"otherkeyname": {"_name_": "nestedname", ...\n',
    'author': 'Paul Becotte',
    'author_email': 'pjbecotte@gmail.com',
    'url': 'https://gitlab.com/pjbecotte/settingscascade',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
