# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['download_and_extract']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'download-and-extract',
    'version': '0.3.3',
    'description': 'Downloads zip archive and extracts it to specified folder',
    'long_description': 'Download And Extract\n====================\n\nIt will download zip file and extract it to the specified folder. Here is an example:\n\n```py\nfrom download_and_extract import Fetcher, FetcherException\n\ntry:\n    fetcher.fetch("http://example.com/about.txt", "./test/1")\nraise FetcherException as ex:\n    print("Some error")\n```\n',
    'author': 'Advaita Krishna das',
    'author_email': 'advaita.krishna.das@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
