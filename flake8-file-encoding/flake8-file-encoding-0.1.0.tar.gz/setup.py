# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['flake8_file_encoding']

package_data = \
{'': ['*']}

install_requires = \
['flake8>=3,<4']

entry_points = \
{'flake8.extension': ['FEN = flake8_file_encoding:EncodingChecker']}

setup_kwargs = {
    'name': 'flake8-file-encoding',
    'version': '0.1.0',
    'description': 'A Flake8 plugin to check for files opened without an explicit encoding',
    'long_description': "# flake8-file-encoding\n\nA Flake8 plugin to check for files opened without an explicit encoding.\n\n## Why check for encoding arguments?\n\nIf you don't specify an `encoding` argument to the\n[open](https://docs.python.org/3/library/functions.html#open) function, then\nPython will use a platform-dependent default encoding—whatever\n[locale.getpreferredencoding](https://docs.python.org/3/library/locale.html#locale.getpreferredencoding)\nreturns. On many platforms this is\n[UTF-8](https://en.wikipedia.org/wiki/UTF-8), but on a significant minority it\nis something different. For example, the default encoding on Japanese Windows\nmachines is cp932 (Microsoft's version of\n[Shift-JIS](https://en.wikipedia.org/wiki/Shift_JIS)). If you open a UTF-8 file\non such a system but do not specify an encoding, then attempting to read any\nmulti-byte characters in the file will cause a UnicodeDecodeError.\n\n## Installation\n\n```bash\npip install flake8-file-encoding\n```\n\n## Usage\n\nOnce this plugin is installed, Flake8 will check for missing `encoding`\narguments along with its other checks. No special activation for this plugin is\nnecessary. For more details on running Flake8, see the\n[Flake8 documentation](http://flake8.pycqa.org/en/latest/index.html).\n\n## Errors\n\nCode   | Message\n------ | --------\nFEN001 | open() call has no encoding argument\n",
    'author': 'Jack Taylor',
    'author_email': 'rayjolt@gmail.com',
    'url': 'https://github.com/rayjolt/flake8-file-encoding',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
