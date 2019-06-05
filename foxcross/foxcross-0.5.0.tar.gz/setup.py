# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['foxcross']

package_data = \
{'': ['*'], 'foxcross': ['templates/*']}

install_requires = \
['aiofiles>=0.4.0,<0.5.0',
 'jinja2>=2.10,<3.0',
 'python-slugify[unidecode]>=3.0,<4.0',
 'starlette>=0.12.0,<0.13.0',
 'uvicorn>=0.7.1,<0.8.0']

extras_require = \
{'modin': ['modin>=0.5.1,<0.6.0'],
 'pandas': ['pandas>=0.24.2,<0.25.0'],
 'performance': ['ujson>=1.35,<2.0', 'modin>=0.5.1,<0.6.0'],
 'ujson': ['ujson>=1.35,<2.0']}

setup_kwargs = {
    'name': 'foxcross',
    'version': '0.5.0',
    'description': 'AsyncIO serving for data science models',
    'long_description': '## Foxcross\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)\n[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/laactech/foxcross/blob/master/LICENSE.md)\n[![Build Status](https://travis-ci.org/laactech/foxcross.svg?branch=master)](https://travis-ci.org/laactech/foxcross)\n[![Build status](https://ci.appveyor.com/api/projects/status/github/laactech/foxcross?branch=master&svg=true)](https://ci.appveyor.com/project/laactech/foxcross)\n![PyPI](https://img.shields.io/pypi/v/foxcross.svg?color=blue)\n[![codecov](https://codecov.io/gh/laactech/foxcross/branch/master/graph/badge.svg)](https://codecov.io/gh/laactech/foxcross)\n\nAsyncIO serving for data science models built on [Starlette](https://www.starlette.io/)\n\n**Documentation**: https://www.foxcross.dev/\n\n**Requirements**: Python 3.6+\n\n## Quick Start\nInstallation using `pip`:\n```bash\npip install foxcross\n```\n\nCreate some test data and a simple model in the same directory to be served:\n\n`data.json`\n```json\n[1,2,3,4,5]\n```\n\n`models.py`\n```python\nfrom foxcross.serving import ModelServing, run_model_serving\n\nclass AddOneModel(ModelServing):\n    test_data_path = "data.json"\n\n    def predict(self, data):\n        return [x + 1 for x in data]\n\nif __name__ == "__main__":\n    run_model_serving()\n```\n\nRun the model locally:\n```bash\npython models.py\n```\n\nNavigate to `localhost:8000/predict-test/`, and you should see the list incremented by 1.\nYou can visit `localhost:8000/` to see all the available routes for your model.\n',
    'author': 'Steven Pate',
    'author_email': 'steven@laac.dev',
    'url': 'https://github.com/laactech/foxcross',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
