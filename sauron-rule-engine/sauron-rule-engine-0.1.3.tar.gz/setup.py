# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['sauron_rule_engine']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sauron-rule-engine',
    'version': '0.1.3',
    'description': 'A simple rule engine implemented in python',
    'long_description': '<h1 align="center">Sauron Rule engine - One engine to rule them all </h1>\n<p>\n  <img src="https://img.shields.io/badge/version-0.1-blue.svg?cacheSeconds=2592000" />\n  <a href="https://twitter.com/joaovoce">\n    <img alt="Twitter: joaovoce" src="https://img.shields.io/twitter/follow/joaovoce.svg?style=social" target="_blank" />\n  </a>\n</p>\n\n> A simple rule engine to be used in python, it is based on simple rules and actions that can be chained with each other. The idea is to run the rule processor on events and have it mutate data or trigger actions\n\n## Install\n\n```sh\npip install sauron-rule-engine\n```\n\n## Use it\n\nA simple example of the usage\n\n```python\nfrom sauron_rule_engine.rule_engine import GenericRuleProcessor\n\nclass CounterRuleProcessor(GenericRuleProcessor):\n\n    # CONDITIONS\n    @staticmethod\n    def counter_lt(value):\n        return counter < value\n\n    # ACTIONS\n    @staticmethod\n    def increment_counter():\n        global counter\n        counter += 2\n\n\ncounter = 0\n\ninput_rule1 = {\n    "when": "event 1",\n    "condition": "counter_lt",\n    "value": 1,\n    "action": "increment_counter",\n}\n\nif __name__ == "__main__":\n    print(f"counter value: {counter}")\n    processor = CounterRuleProcessor()\n    processor.run(input_rule1)\n    print(f"counter value: {counter}")\n    processor.run(input_rule1)\n    print(f"counter value: {counter}")\n```\n\n## Author\n\n👤 **João Ricardo Lhullier Lugão**\n\n- Twitter: [@joaovoce](https://twitter.com/joaovoce)\n- Github: [@jlugao](https://github.com/jlugao)\n\n## Show your support\n\nGive a ⭐️ if this project helped you!\n\n---\n\n_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_\n',
    'author': 'jlugao',
    'author_email': 'joaolhullier@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
