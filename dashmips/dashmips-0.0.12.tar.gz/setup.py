# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['dashmips', 'dashmips.instructions', 'dashmips.plugins', 'dashmips.syscalls']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['dashmips = dashmips.__main__:main']}

setup_kwargs = {
    'name': 'dashmips',
    'version': '0.0.12',
    'description': 'Mips Interpreter',
    'long_description': '# Dashmips\n\nDashmips is a Mips Interpreter CLI Program.\n\n## Requirements\n\nDashmips has no dependencies beyond requiring `python 3.7`.\nThere is a dataclasses module for python 3.6 that may make this module work but it is untested.\n\n## Install\n\nThe recommended way to install dashmips is with pip:\n\n```sh\npip install dashmips\n```\n\n## Usage\n\nIf you installed via pip you should now have a binary in your path that you can launch by typing:\n\n```sh\ndashmips\n```\n\n## "Compiling"\n\nTo compile or run a mips program you run:\n\n```sh\ndashmips compile -f FILE.mips\n```\n\nWhat "compilation" means in dashmips is a conversion of the source file to a json format that is better understood by the program. You can use this json format to inspect the internals of how your mips program is interpretted by dashmips.\n\n## Running\n\nThis one\'s easy:\n\n```sh\ndashmips run FILE.mips\n```\n\n> Note: FILE is a positional argument in the run subcommand\n\n## Debugging\n\nIn order to leave a flexible environment for debugging dashmips doesn\'t provide an interface for human debugging of a mips program. Instead the debugger included is a server that accepts the json format of a mips program over the network and will do the requested operations returning an updated MipsProgram json object.\n\nThere is a vscode extension that can speak dashmips specific json language [here](https://github.com/nbbeeken/dashmips-debugger).\n\n### Debugging protocol\n\nSmall notes about the protocol if you want to proceed with a manual debugging. The JSON you send to the debug server is expected to take the following format:\n\n```ts\ninterface DebugMessage {\n    command: \'start\' | \'step\' | \'continue\' | \'stop\';\n    program: MipsProgram;  // MipsProgram can be found in `dashmips/models.py`\n    // properties below are optional\n    breakpoints?: number[];\n    message?: string;\n    error?: boolean;\n}\n```\n\nThe commands listed are `start`, `step`, `continue`, and `stop`. In short each operation does the following:\n\n- Start: sets the pc to the main label\n- Step: runs exactly one instruction from current pc\n- Continue: runs as many instructions as there are between current pc and a breakpoint\n- Stop: Does nothing\n\nThe server is designed to be stateless so it can handle many clients at once.\n\n## Contributing\n\n### Getting Setup\n\nIf you want to contribute to the dashmips project you will need the following:\n\n- [Poetry](https://poetry.eustace.io/docs/) is used for dependencies, it will help get you up and running\n- After installing Poetry, and cloning this repository:\n- `poetry install` - will install the dashmips dependencies in a virtual environment that won\'t harm your global set up.\n- `poetry run X` - can run X command in the correct python environment\n- Try `poetry run pytest --mypy --docstyle --codestyle` to ensure all tests are passing correctly\n\n\n### Adding Syscalls / Adding Instructions\n\nYou can add to the existing files in the `dashmips/instructions` and `dashmips/syscalls` directories using the relevant decorator (`@`).\nIf you add instructions or syscalls to a new file in these subdirectories ensure that the new file is named with the pattern: `*_instructions.py` or `*_syscalls.py` where `*` is whatever identifier you choose.\n\nHappy coding!\n',
    'author': 'Neal Beeken',
    'author_email': 'nbbeeken@gmail.com',
    'url': 'https://github.com/nbbeeken/dashmips',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
