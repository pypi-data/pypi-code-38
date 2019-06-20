# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['liquid']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'liquidpy',
    'version': '0.0.7',
    'description': 'A port of liquid template engine for python',
    'long_description': '# liquidpy\nA port of [liquid][1] template engine for python\n\n![Pypi][2] ![Github][3] ![PythonVers][4] ![Travis building][5]  ![Codacy][6] ![Codacy coverage][7]\n\n## Install\n```shell\n# install released version\npip install liquidpy\n# install lastest version\npip install git+https://github.com/pwwang/liquidpy.git\n```\n\n## Full Documentation\n[ReadTheDocs][8]\n\n## Baisic usage\n```python\nfrom liquid import Liquid\nliq = Liquid(\'{{a}}\')\nret = liq.render(a = 1)\n# ret == \'1\'\n```\nWith environments:\n```python\nliq = Liquid(\'{{os.path.basename(a)}}\', os = __import__(\'os\'))\nret = liq.render(a = "path/to/file.txt")\n# ret == \'file.txt\'\n```\n\n[1]: https://shopify.github.io/liquid/\n[2]: https://img.shields.io/pypi/v/liquidpy.svg?style=flat-square\n[3]: https://img.shields.io/github/tag/pwwang/liquidpy.svg?style=flat-square\n[4]: https://img.shields.io/pypi/pyversions/liquidpy.svg?style=flat-square\n[5]: https://img.shields.io/travis/pwwang/liquidpy.svg?style=flat-square\n[6]: https://api.codacy.com/project/badge/Grade/ddbe1b0441f343f5abfdec3811a4e482\n[7]: https://api.codacy.com/project/badge/Coverage/ddbe1b0441f343f5abfdec3811a4e482\n[8]: https://liquidpy.readthedocs.io/en/latest/\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'url': 'https://github.com/pwwang/liquidpy',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
