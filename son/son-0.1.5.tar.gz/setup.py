# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['son']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'son',
    'version': '0.1.5',
    'description': 'Tools to read and write .son files',
    'long_description': 'son | sequential object notation\n===\n\n![python](https://img.shields.io/badge/python-2.7--3.7-lightgrey.svg?style=flat-square)\n[![pypi](https://img.shields.io/pypi/v/son.svg?style=flat-square)](https://pypi.org/project/son/)\n![license](https://img.shields.io/pypi/l/son.svg?color=red&style=flat-square)\n[![code style](https://img.shields.io/badge/code%20style-black-202020.svg?style=flat-square)](https://github.com/ambv/black)\n\n\n## What is this?\n_son_ is a data format that builds on [JSON](https://www.json.org/) and adds one \nfeature inspired by [YAML](https://yaml.org/): concatenation of objects with \n`---`.  Optionally, the delimiter `===` can be used once per _son_ file to delimit \nmetadata.\n\n## Why _son_?\nWhile JSON is perfect for storing structured data, it is inherently impossible\nto add new portions of data to a file without reading it first. YAML files on \nthe other hand are self extensible by the `---` delimiter, but the flexibility \nYAML offers makes the files inefficient to parse. They are thus unsuited to \nstore significant amounts of data.\n\n_son_ fills the gap by allowing JSON objects to be concatenated with `---`. It\nthus combines the speed and efficiency of JSON with the sequential extensibility\nof YAML, see [example](#Example). It further adds to discern metadata from \nactual data by using `===`.\n\n_son_ does **not** allow to overwrite data. In order to avoid accidental data loss,\nmetada can only be written to fresh files, whereas data can only be appended to files.\n\n## Who needs this?\n_son_ originated from the need to store computational data that is produced\nportion by portion on a computer. The requirements were:\n- Possible to be read by a human,\n- possible to store arbitrary data structures _including_ metadata,\n- easy to write and parse by a computer,\n- efficient to parse to allow files of up to GB size (takes forever to parse with YAML),\n- sequential and incorruptible,\n- resilient to data loss.\n\n## Example\nThis is a valid _son_ string:\n```yaml\n{\n  "purpose": "store biography data",\n  "version": 0.1\n}\n===\n{\n  "first name": "Hildegard",\n  "second name": "Kneef",\n  "age": 93\n}\n---\n{\n  "first name": "Wiglaf",\n  "second name": "Droste",\n  "age": 57\n}\n```\nIt will be parsed into the metadata object, and a list containing the data objects with\n```python\nimport son\n\nmetadata, data = son.load(\'file.son\')\n```\n',
    'author': 'Florian Knoop',
    'author_email': None,
    'url': 'https://github.com/flokno/son',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.7',
}


setup(**setup_kwargs)
