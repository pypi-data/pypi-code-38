# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['sauron_rule_engine']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=0.29.0,<0.30.0']

setup_kwargs = {
    'name': 'sauron-rule-engine',
    'version': '0.1.5',
    'description': 'A simple rule engine implemented in python',
    'long_description': '<h1 align="center">Sauron Rule engine - One engine to rule them all </h1>\n<p>\n  <img src="https://img.shields.io/badge/version-0.1-blue.svg?cacheSeconds=2592000" />\n  <img src="https://circleci.com/gh/jlugao/sauron-rule-engine/tree/master.svg?style=svg" />\n<img alt="GitHub" src="https://img.shields.io/github/license/jlugao/sauron-rule-engine.svg?style=plastic">\n  <a href="https://twitter.com/joaovoce">\n    <img alt="Twitter: joaovoce" src="https://img.shields.io/twitter/follow/joaovoce.svg?style=social" target="_blank" />\n  </a>\n</p>\n\n> A simple rule engine to be used in python, it is based on simple rules and actions that can be chained with each other. The idea is to run the rule processor on events and have it mutate data or trigger actions\n\nHeavily inspired on FastAPI\n\n## Install\n\n```sh\npip install sauron-rule-engine\n```\n\n## Use it\n\nA simple example of the usage\n\n```python\nfrom sauron_rule_engine.rule_engine import RuleEngine\n\njson_rule = """\n    {\n        "conditions": [\n            {\n                "name": "is_smaller_than",\n                "arguments": {\n                    "compared_to": 2\n                }\n            }\n        ],\n        "actions": [\n            {\n                "name": "increment_number"\n            }\n        ]\n    }\n"""\n#instantiate your engine\nengine = RuleEngine()\n\n#just a dumb variable so we can see the actions in use\nnumber_to_be_incremented = 1\n\n@engine.condition\ndef is_smaller_than(compared_to: int) -> bool:\n    return number_to_be_incremented < compared_to\n\n@engine.action\ndef increment_number() -> None:\n    nonlocal number_to_be_incremented\n    number_to_be_incremented += 1\n\n# Then just use your engine\nif __name__ == "__main__":\n  print(number_to_be_incremented)\n  ## 1\n\n  engine.run(json_rule)\n  print(number_to_be_incremented)\n  ## 2\n\n  engine.run(json_rule)\n  print(number_to_be_incremented)\n  ## 2\n\n```\n\n## Features coming to town\n\n- Exporting a json string with the conditions and actions in a given engine\n- Exported conditions and actions should include sane typing and docstring exposure\n- Support pydantic types\n- Support for choices fields with enum\n- Support for complex types with hints to the frontend (like a range for an int type\n\n## Author\n\n👤 **João Ricardo Lhullier Lugão**\n\n- Twitter: [@joaovoce](https://twitter.com/joaovoce)\n- Github: [@jlugao](https://github.com/jlugao)\n\n## Show your support\n\nGive a ⭐️ if this project helped you!\n\n---\n\n_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_\n',
    'author': 'jlugao',
    'author_email': 'joaolhullier@gmail.com',
    'url': 'https://github.com/jlugao/sauron-rule-engine',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
