# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['encapsia_cli']

package_data = \
{'': ['*']}

install_requires = \
['awscli>=1.16,<2.0',
 'click-completion>=0.5.0,<0.6.0',
 'click-shell>=1.0,<2.0',
 'click>=7.0,<8.0',
 'encapsia-api>=0.1.14',
 'http-prompt>=1.0,<2.0',
 'httpie>=1.0,<2.0',
 'requests[security]>=2.20,<3.0',
 'tabulate>=0.8.3,<0.9.0',
 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['encapsia = encapsia_cli.encapsia:main']}

setup_kwargs = {
    'name': 'encapsia-cli',
    'version': '0.1.11',
    'description': 'Client CLI for talking to an Encapsia system.',
    'long_description': '# About\n\nThis package provides command line access to Encapsia over the REST API.\n\nAll of these are designed to work with server 1.5 and beyond.\n\n# Autocomplete\n\nSetup autocomplete using the instructions found on https://github.com/click-contrib/click-completion.\n\n# Tests\n\nSee the `walkthrough_tests` directory for bash scripts which exercise the CLI.\n\nRun them e.g. with:\n\n    bash walkthrough_tests/all.sh --host <host> --example-plugin-src ../inf-ice-example-plugin/\n\nNote that these tests are *not* self-verifying; they just provide helpful coverage, assurance, and working documentation.\n\n# Release checklist\n\n* Run: `black .`\n* Run: `isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width=88 -y`\n* Run: `flake8 --ignore=E501 .`\n* Ensure "tests" run ok (see above). Also capture output and commit with:\n    `bash walkthrough_tests/all.sh --host <host> --example-plugin-src ../inf-ice-example-plugin/ 2>&1 | ansi2html -f 80% >WALKTHROUGH.html`\n* Ensure git tag, package version, and `enacpsia_cli.__version__` are all equal.\n\n# TODO\n\n* Feature: Add package command for running standard tasks\n* Feature: Add "encapsia plugins reactor" to forward local calls to remote for even easier dev without installing anything except the SQL.\n* Feature: Use click-web to create an encapsia webserve command?? Put in a plugin?',
    'author': 'Timothy Corbett-Clark',
    'author_email': 'timothy.corbettclark@gmail.com',
    'url': 'https://github.com/tcorbettclark/encapsia-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
