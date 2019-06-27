# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['flake8_pie']
entry_points = \
{'flake8.extension': ['PIE = flake8_pie:Flake8PieCheck']}

setup_kwargs = {
    'name': 'flake8-pie',
    'version': '0.3.0',
    'description': 'A flake8 extension that implements misc. lints',
    'long_description': '# flake8-pie [![CircleCI](https://circleci.com/gh/sbdchd/flake8-pie.svg?style=svg)](https://circleci.com/gh/sbdchd/flake8-pie) [![pypi](https://img.shields.io/pypi/v/flake8-pie.svg)](https://pypi.org/project/flake8-pie/)\n\n> A flake8 extension that implements misc. lints\n\nNote: flake8-pie requires Python 3.6 or greater\n\n## lints\n\n- PIE781: You are assigning to a variable and then returning. Instead remove the assignment and return.\n- PIE782: Unnecessary f-string. You can safely remove the `f` prefix.\n- PIE783: Celery tasks should have explicit names.\n\n### PIE781: Assign and Return\n\nBased on Clippy\'s\n[`let_and_return`](https://rust-lang.github.io/rust-clippy/master/index.html#let_and_return)\nand Microsoft\'s TSLint rule\n[`no-unnecessary-local-variable`](https://github.com/Microsoft/tslint-microsoft-contrib).\n\nFor more info on the structure of this lint, see the [accompanying blog\npost](https://steve.dignam.xyz/2018/12/16/creating-a-flake8-lint/).\n\n#### examples\n\n```python\n# error\ndef foo():\n   x = bar()\n   return x\n\n# allowed\ndef foo():\n   x, _ = bar()\n   return x\n```\n\n### PIE782: No Pointless F Strings\n\nWarn about usage of f-string without templated values.\n\n#### examples\n\n```python\nx = (\n    f"foo {y}", # ok\n    f"bar" # error\n)\n```\n\n### PIE783: Celery tasks should have explicit names.\n\nWarn about [Celery](https://pypi.org/project/celery/) task definitions that don\'t have explicit names.\n\nNote: this lint is kind of naive considering any decorator with a `.task()`\nmethod or any decorator called `shared_task()` a Celery decorator.\n\n#### examples\n\n```python\n# error\n@app.task()\ndef foo():\n    pass\n\n# ok\n@app.task(name="app_name.tasks.foo")\ndef foo():\n    pass\n```\n\n## dev\n\n```shell\n# install dependencies\npoetry install\n\n# install plugin to work with flake8\npoetry run python setup.py install\n\n# test\npoetry run pytest\n# or with watch\npoetry run ptw\n\n# typecheck\npoetry run mypy *.py\n\n# format\npoetry run black .\n\n# lint\npoetry run flake8 .\n```\n\n## uploading a new version to [PyPi](https://pypi.org)\n\n```shell\n# increment `Flake8PieCheck.version` and pyproject.toml `version`\n\n# build new distribution files and upload to pypi\n# Note: this will ask for login credentials\nrm -rf dist && poetry publish --build\n```\n',
    'author': 'Steve Dignam',
    'author_email': 'steve@dignam.xyz',
    'url': 'https://github.com/sbdchd/flake8-pie',
    'py_modules': modules,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
