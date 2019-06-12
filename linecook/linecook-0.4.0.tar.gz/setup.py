# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['linecook',
 'linecook.config',
 'linecook.config.tests',
 'linecook.recipes',
 'linecook.tests',
 'linecook.transforms',
 'linecook.transforms.tests']

package_data = \
{'': ['*']}

install_requires = \
['future>=0.15,<0.16', 'termcolor>=1.0.0,<2.0.0', 'toolz>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['linecook = linecook.cli:main']}

setup_kwargs = {
    'name': 'linecook',
    'version': '0.4.0',
    'description': 'Prepare lines of text for easy consumption',
    'long_description': "====================================================\nlinecook: Prepare lines of text for easy consumption\n====================================================\n\n.. default-role:: literal\n\n.. image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg\n   :target: https://github.com/tonysyu/linecook/blob/master/LICENSE\n\n.. image:: https://travis-ci.com/tonysyu/linecook.svg?branch=master\n   :target: https://travis-ci.com/tonysyu/linecook\n\n.. image:: https://codecov.io/gh/tonysyu/linecook/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/tonysyu/linecook\n\n.. image:: https://readthedocs.org/projects/linecook/badge/\n   :target: https://linecook.readthedocs.io\n\n`linecook` is a command-line tool that transforms lines of text into a form\nthat's pleasant to consume.\n\n- **Documentation:** https://linecook.readthedocs.io\n- **Source:** https://github.com/tonysyu/linecook\n\nInstall\n=======\n\nThe recommended way of installing `linecook` is to use `pip`::\n\n    pip install linecook\n\nCooking up some beautiful text\n==============================\n\nThe core goal of `linecook` is to make it easy to create your own transforms to\nparse whatever text you have. For example, take an `app.log` file that looks\nlike:\n\n.. image:: docs/_static/images/app_log_raw.png\n\nIf you want to highlight the log type and mute the dates/times, then you can\ncreate a custom recipe in one of your `configuration files\n<https://linecook.readthedocs.io/en/latest/configuration.html>`_ like the\nfollowing:\n\n.. code-block:: python\n\n   from linecook import patterns as rx\n   from linecook.transforms import color_text\n\n   LINECOOK_CONFIG = {\n       'recipes': {\n           'my-logs': [\n                color_text(rx.any_of(rx.date, rx.time), color='blue'),\n                color_text('INFO', color='cyan'),\n                color_text('WARN', color='grey', on_color='on_yellow'),\n                color_text('ERROR', on_color='on_red'),\n           ],\n       },\n   }\n\nTo use this recipe, you can just pipe the log output to `linecook` with your\nnew recipe as an argument:\n\n.. image:: docs/_static/images/app_log_linecook.png\n\nThat's all there is to it!\n\nSee Also\n========\n\n- `grc <https://github.com/garabik/grc>`_: A generic colouriser (sic;) for log\n  files and command output.\n- `rainbow <https://github.com/nicoulaj/rainbow>`_: Colorize commands output or\n  STDIN using patterns.\n- `multitail <https://www.vanheusden.com/multitail/>`_: Tail multiple files at\n  once, with features to colorize, filter, and merge.\n- `colortail <https://github.com/joakim666/colortail>`_: Like the tail command\n  line utility but with colors\n- `StackOverflow post on colored output\n  <https://unix.stackexchange.com/questions/8414>`_\n",
    'author': 'Tony S. Yu',
    'author_email': 'tsyu80@gmail.com',
    'url': 'https://github.com/tonysyu/linecook',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
}


setup(**setup_kwargs)
