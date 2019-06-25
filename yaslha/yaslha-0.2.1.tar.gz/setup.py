# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['yaslha', 'yaslha.tests']

package_data = \
{'': ['*'],
 'yaslha.tests': ['data/*',
                  'data/pylha_json/*',
                  'data/pylha_yaml/*',
                  'examples/*']}

install_requires = \
['click>=7.0,<8.0',
 'colorama>=0.4,<0.5',
 'coloredlogs>=10.0,<11.0',
 'numpy>=1.16,<2.0',
 'ruamel.yaml>=0.15,<0.16',
 'typing-extensions>=3.7,<4.0']

entry_points = \
{'console_scripts': ['yaslha = yaslha.script:main']}

setup_kwargs = {
    'name': 'yaslha',
    'version': '0.2.1',
    'description': 'A Python package to handle SLHA (SUSY Les Houches Accord) files.',
    'long_description': '[![Build Status](https://api.travis-ci.org/misho104/yaslha.svg?branch=master)](https://travis-ci.org/misho104/yaslha)\n[![Coverage Status](https://coveralls.io/repos/github/misho104/yaslha/badge.svg?branch=master)](https://coveralls.io/github/misho104/yaslha?branch=master)\n[![Doc Status](http://readthedocs.org/projects/yaslha/badge/)](https://yaslha.readthedocs.io/)\n[![PyPI version](https://badge.fury.io/py/yaslha.svg)](https://badge.fury.io/py/yaslha)\n[![License: MIT](https://img.shields.io/badge/License-MIT-ff25d1.svg)](https://github.com/misho104/yaslha/blob/master/LICENSE)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n[yaslha](https://github.com/misho104/yaslha): Yet Another SLHA module for Python3\n=================================================================================\n\nA Python3 package to manipulate [SLHA](http://skands.physics.monash.edu/slha/) files and convert them to other file formats (JSON and YAML).\n\nQuick Start\n-----------\n\n(TBW)\n\nIntroduction\n------------\n\nThe [SUSY Les Houches Accord](http://skands.physics.monash.edu/slha/) is a data format widely used in particle physics phenomenology.\nIt is originally defined in [arXiv:hep-ph/0311123](https://arxiv.org/abs/hep-ph/0311123) and extended to SLHA2 in [arXiv:0801.0045](https://arxiv.org/abs/0801.0045).\n\nBecause of its birth in FORTRAN era it is a fixed length format such as\n\n```\nBLOCK SMINPUTS                  # Standard Model input parameters\n     1     1.27934000e+02   # alpha_em^-1(M_Z)^MSbar\n     2     1.16637000e-05   # G_F [GeV^-2]\n     3     1.17200000e-01   # alpha_S(M_Z)^MSbar\n     4     9.11876000e+01   # mZ (pole)\n     5     4.18000000e+00   # mb(mb)^MSbar\n     6     1.73300000e+02   # mt (pole)\n     7     1.77682000e+00   # mtau (pole)\n#\nBLOCK ALPHA                    #\n          -2.68630018e-02   # Higgs mixing parameter\n#\nBLOCK HMIX Q= 2.00000000e+02   # Higgs parameters (DRbar)\n     1     5.40000000e+02   # mu(Q)\n     2     4.00000000e+01   # tanbeta(Q)\n     3     2.46220569e+02   # vev(Q)\n     4     2.30400000e+05   # mA^2(Q)\n#\n...\n```\n\nand extended in many program codes.\n\nPython has two famous SLHA parser: [PySLHA](http://www.insectnation.org/projects/pyslha) by Andy Buckley and [pylha](https://github.com/DavidMStraub/pylha) by David M. Straub.\n[yaslha](https://github.com/misho104/yaslha) is "yet another" SLHA parser, influenced much by these two parsers.\n\nPython regrettably experienced a terrible era due to the transition from Python2 to Python3.\nTo reduce code complexity, this package supports only Python3.4 and later versions.\n\nUsage\n-----\n\n(TBW)\n\nAuthor\n------\n\n[Sho Iwamoto / Misho](https://www.misho-web.com/), under much influence from [PySLHA](http://www.insectnation.org/projects/pyslha) by Andy Buckley and [pylha](https://github.com/DavidMStraub/pylha) by David M. Straub.',
    'author': 'Sho Iwamoto (Misho)',
    'author_email': 'webmaster@misho-web.com',
    'url': 'https://github.com/misho104/yaslha',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
