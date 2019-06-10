# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['datafiles', 'datafiles.converters', 'datafiles.tests']

package_data = \
{'': ['*']}

install_requires = \
['cached_property>=1.5,<2.0',
 'classproperties>=0.1.3,<0.2.0',
 'minilog>=1.2.3,<2.0.0',
 'parse>=1.12,<2.0',
 'ruamel.yaml>=0.15.96,<0.16.0',
 'tomlkit>=0.5.3,<0.6.0',
 'typing-extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'datafiles',
    'version': '0.4b3',
    'description': 'File-based ORM for dataclasses.',
    'long_description': '# Datafiles: A file-based ORM for dataclasses\n\nDatafiles is a bidirectional serialization library for Python [dataclasses](https://docs.python.org/3/library/dataclasses.html) to synchronizes objects to the filesystem using type annotations. It supports a variety of file formats with round-trip preservation of formatting and comments, where possible. By default, changes are automatically saved and only include the minimum data needed to restore an object.\n\n[![PyPI Version](https://img.shields.io/pypi/v/datafiles.svg)](https://pypi.org/project/datafiles)\n[![PyPI License](https://img.shields.io/pypi/l/datafiles.svg)](https://pypi.org/project/datafiles)\n[![Travis CI](https://img.shields.io/travis/jacebrowning/datafiles/develop.svg?label=unix)](https://travis-ci.org/jacebrowning/datafiles)\n[![AppVeyor](https://img.shields.io/appveyor/ci/jacebrowning/datafiles/develop.svg?label=windows)](https://ci.appveyor.com/project/jacebrowning/datafiles)\n[![Coveralls](https://img.shields.io/coveralls/jacebrowning/datafiles.svg)](https://coveralls.io/r/jacebrowning/datafiles)\n\n## Usage\n\nTake an existing dataclass such as [this example](https://docs.python.org/3/library/dataclasses.html#module-dataclasses) from the documentation:\n\n```python\nfrom dataclasses import dataclass\n\n@dataclass\nclass InventoryItem:\n    """Class for keeping track of an item in inventory."""\n\n    name: str\n    unit_price: float\n    quantity_on_hand: int = 0\n\n    def total_cost(self) -> float:\n        return self.unit_price * self.quantity_on_hand\n```\n\nand decorate it with directory pattern to synchronize instances:\n\n```python\nfrom datafiles import datafile\n\n@datafile("inventory/items/{self.name}.yml")\n@dataclass\nclass InventoryItem:\n    ...\n```\n\nThen, work with instances of the class as normal:\n\n```python\n>>> item = InventoryItem("widget", 3)\n```\n\n```yaml\n# inventory/items/widget.yml\n\nunit_price: 3.0\n```\n\nChanges to the object are automatically saved to the filesystem:\n\n```python\n>>> item.quantity_on_hand += 100\n```\n\n```yaml\n# inventory/items/widget.yml\n\nunit_price: 3.0\nquantity_on_hand: 100\n```\n\nChanges to the filesystem are automatically reflected in the object:\n\n```yaml\n# inventory/items/widget.yml\n\nunit_price: 2.5  # <= manually changed from "3.0"\nquantity_on_hand: 100\n```\n\n```python\n>>> item.unit_price\n2.5\n```\n\nObjects can also be restored from the filesystem:\n\n```python\n>>> from datafiles import Missing\n>>> item = InventoryItem("widget", Missing)\n>>> assert item.unit_price == 2.5\n>>> assert item.quantity_on_hand == 100\n```\n\nDemo: [Jupyter Notebook](https://github.com/jacebrowning/datafiles/blob/develop/notebooks/readme.ipynb)\n\n## Installation\n\nBecause datafiles relies on dataclasses and type annotations, Python 3.7+ is required. Install this library directly into an activated virtual environment:\n\n```\n$ pip install datafiles\n```\n\nor add it to your [Poetry](https://poetry.eustace.io/) project:\n\n```\n$ poetry add datafiles\n```\n\n## Documentation\n\nTo see additional syncrhonization and formatting options, please consult the [full documentation](https://datafiles.readthedocs.io).\n',
    'author': 'Jace Browning',
    'author_email': 'jacebrowning@gmail.com',
    'url': 'https://pypi.org/project/datafiles',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
