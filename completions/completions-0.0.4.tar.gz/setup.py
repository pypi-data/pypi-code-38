# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['completions']

package_data = \
{'': ['*']}

install_requires = \
['colorama', 'pyparam>=0.1.3,<0.2.0', 'python-simpleconf>=0.1.4,<0.2.0']

entry_points = \
{'console_scripts': ['completions = completions:main']}

setup_kwargs = {
    'name': 'completions',
    'version': '0.0.4',
    'description': 'Shell completions made easy.',
    'long_description': "# completions\n\n[![pypi][1]][2] [![tag][3]][4] [![travis][5]][6] [![codacy quality][7]][8] ![pyver][11]\n\nShell completions for your program made easy.\n\n## Installation\n```shell\npip install completions\n# install lastest version using poetry\ngit clone https://github.com/pwwang/completions\ncd completions\npoetry install\n```\n\n## Usage\n\n### Defining your completions\nYou may define your completions, basically commands and options, by following schema (showed in `yaml`, but can be any format supported by [`python-simpleconf`][12]:\n`example.yaml`\n```yaml\nprogram:\n    # your program, or path to your program\n    name: completions-example\n    desc: Shell completions for your program made easy.\n    # whether global options should be inherited by commands\n    inherit: true\n    # options or global options if you have commands\n    options:\n        -s: The shell, one of bash, fish, zsh and auto.\n        --shell: The shell, one of bash, fish, zsh and auto.\n        -a: Automatically write completions to destination file.\n        --auto: Automatically write completions to destination file.\ncommands:\n    # No other options for command, give the description\n    self: Generate completions for myself.\n    generate:\n        desc: Generate completions from configuration files.\n        options:\n            -c: The configuration file to load.\n            --config: The configuration file to load.\n```\n\nHow it looks like in `fish`:\n![command][13]\n![option][14]\n\n### Generating completion scripts\n- Bash\n    ```shell\n    > completions generate --shell bash \\\n        --config example.yaml > ~/bash_completion.d/completions.bash-completion\n    ```\n    You may need to `source` it in your `.bashrc` and restart your shell for the changes to take effect.\n- Fish\n    ```shell\n    > completions generate --shell fish \\\n        --config example.yaml > ~/.config/fish/completions/completions.fish\n    ```\n    You may need to restart your shell for the changes to take effect.\n- Zsh\n    ```shell\n    > completions generate --shell zsh \\\n        --config example.yaml > ~/.zsh-completions/_completions\n    ```\n    Make sure `fpath+=~/.zsh-completions` is put before `compinit` in you `.zshrc`\n\n### Saving completions scripts automatically\n- Bash\n    ```shell\n    > completions generate --shell bash --config example.yaml --auto\n    ```\n\n- Fish\n    ```shell\n    > completions generate --shell fish --config example.yaml --auto\n    ```\n\n- Zsh\n    ```shell\n    > completions generate --shell zsh --config example.yaml --auto\n    ```\n\n### Python API\n```python\nfrom completions import Completions\ncompletions = Completions(\n    # if not given, will be read from sys.argv[0]\n    name    = 'completions',\n    # Add global options to commands\n    inherit = True,\n    desc    = 'Shell completions for your program made easy.')\ncompletions.addOption(\n    ['-s', '--shell'],\n    'The shell, one of bash, fish, zsh and auto.')\ncompletions.addOption(\n    ['-a', '--auto'],\n    'Automatically write completions to destination file.')\ncompletions.addCommand(\n    'self', 'Generate completions for myself.')\ncompletions.addCommand(\n    'generate', 'Generate completions from configuration files.')\ncompletions.command('generate').addOption(\n    ['-c', '--config'], 'The configuration file to load.')\ncompletions.generate(shell = 'fish', auto = False)\n```\n\n[1]: https://img.shields.io/pypi/v/completions.svg?style=flat-square\n[2]: https://pypi.org/project/completions/\n[3]: https://img.shields.io/github/tag/pwwang/completions.svg?style=flat-square\n[4]: https://github.com/pwwang/completions\n[5]: https://img.shields.io/travis/pwwang/completions.svg?style=flat-square\n[6]: https://travis-ci.org/pwwang/completions\n[7]: https://img.shields.io/codacy/grade/98c8035ccd4c4f97b454086271a1b1c1.svg?style=flat-square\n[8]: https://app.codacy.com/project/pwwang/completions/dashboard\n[11]: https://img.shields.io/pypi/pyversions/completions.svg?style=flat-square\n[12]: https://github.com/pwwang/simpleconf\n[13]: https://raw.githubusercontent.com/pwwang/completions/master/examples/command.png\n[14]: https://raw.githubusercontent.com/pwwang/completions/master/examples/option.png\n",
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'url': 'https://github.com/pwwang/completions',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
