# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['klak']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['klak = klak.cli:main']}

setup_kwargs = {
    'name': 'klak',
    'version': '0.4.2',
    'description': 'Klak provides the ergonoics of a project Makefile with the ease of Python and power of Click.',
    'long_description': '[click]: https://click.palletsprojects.com/en/master/\n[poetry]: https://github.com/sdispater/poetry\n[click setuptools integration]: https://click.palletsprojects.com/en/master/setuptools/\n[click bash completions]: https://click.palletsprojects.com/en/master/bashcomplete/#activation\n\n# Klak\n\n[![pypi](https://img.shields.io/pypi/v/klak.svg)](https://pypi.python.org/pypi/klak)\n[![standard-readme compliant](https://img.shields.io/badge/standard--readme-OK-green.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)\n[![travis-ci](https://img.shields.io/travis/aubricus/klak.svg)](https://travis-ci.org/aubricus/klak)\n[![docs](https://readthedocs.org/projects/klak/badge/?version=latest)](https://klak.readthedocs.io/en/latest/?badge=latest)\n[![docs](https://readthedocs.org/projects/klak/badge/?version=latest)](https://klak.readthedocs.io/en/latest/?badge=latest)\n\n<!-- NOTE: If you update this line, update pyproject.toml -->\n\n> Klak provides the ergonoics of a project Makefile with the ease of Python and power of [Click].\n\n## Table of Contents\n\n-   [Background](#background)\n-   [Install](#install)\n-   [Usage](#usage)\n-   [Maintainers](#maintainers)\n-   [Contributing](#contributing)\n-   [License](#license)\n\n## Background\n\nMakefiles provide a simple interface, `make <command>`, that is great for automating repetitive project tasks. Makefile syntax, however, is archaic, error-prone, and ill-suited for constructing modern, useful command-line interfaces.\n\nPython, on the other hand, has wonderful syntax and is _great_ for scripting. When Python is paired with [Click] constructing modern, useful command-line interfaces is easy!\n\nIs there a way we can combine the power of Python and Click into a "Makefile like" experience?\n\n_Enter Klak_.\n\nKlak exposes a single entry-point—`klak`—which auto-loads a _100%_, vanilla Python file called a **Clickfile**. All CLI is built using standard Python and Click, and all commands are available via: `klak <command>` (see [Usage](#usage)).\n\n### What is it good for?\n\nKlak\'s purpose is to provide a convenient, single-file experince for automating repetitive project tasks. It does not, nor will it ever, intend to replace Make or Makefiles.\n\n## Install\n\n### Stable Release\n\n```bash\n# NOTE: This is the recommended method of installation.\npip install klak\n```\n\n### From Source\n\n> Klak uses [Poetry] to manage depdencies and distribution (in lieu of setuptools).\n\n```bash\n# NOTE: Clone the public repository\ngit clone git://github.com/aubricus/klak\n\n# NOTE: or download the tarball\ncurl  -OL https://github.com/aubricus/klak/tarball/master\n\n# NOTE: Once the source is downloaded\npoetry install\n```\n\n## Usage\n\nTo get started with Klak create a **Clickfile**. Here\'s an example **Clickfile** to get started:\n\n```python\n"""\nExample Clickfile.\n\nNOTE: Set your editor\'s language mode to Python to\n      enable syntax highlighting! :^)\n"""\n\nimport logging\nimport click\nfrom klak.cli import cli\n\n\nlog = logging.getLogger("Clickfile")\n\n\n# -------------------------------------\n# Examples\n# -------------------------------------\n\n\n# Example: Add a command.\n@cli.command()\n@click.argument("name")\ndef greet(name):\n    """Greet someone."""\n    click.secho(f"Hello, {name}")\n\n\n# Example: Add a group and sub-command.\n@cli.group()\ndef humans():\n    """Humans command group."""\n    pass\n\n\n@humans.command(name="count")\ndef humans_count():\n    """Count all the humans."""\n    click.secho("Over 9000!!!")\n\n```\n\nOnce your **Clickfile** is ready, access commands through `klak`.\n\n```bash\n$ klak --help\n```\n\n## Support\n\nThis project is a hobby/passion project which I maintain in my own time.\n\n### Python\n\n-   Python 3.5+\n\n### OS\n\n-   Linux ✓\n-   MacOS ✓\n-   Windows ✘ (any volunteers?)\n\n## Maintainers\n\n[@aubricus](https://github.com/aubricus)\n\n## Contributing\n\nSee [the contributing file](CONTRIBUTING.md)!\n\nPRs accepted!\n\nPlease note, if editing the README, please conform to the [standard-readme](https://github.com/RichardLitt/standard-readme) specification.\n\n## License\n\n[MIT © 2018, 2019 aubricus@gmail.com](./LICENSE)\n',
    'author': 'Aubrey Taylor',
    'author_email': 'aubricus+klak@gmail.com',
    'url': 'https://github.com/aubricus/klak',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
