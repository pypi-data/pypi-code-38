# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['yapo', 'yapo._index', 'yapo._portfolio', 'yapo._sources', 'yapo.common']

package_data = \
{'': ['*']}

install_requires = \
['PyContracts>=1.8,<2.0',
 'numpy>=1.16,<2.0',
 'pandas>=0.24,<0.25',
 'quandl>=3.4,<4.0',
 'serum>=5.1,<6.0']

setup_kwargs = {
    'name': 'yapo',
    'version': '0.2.0',
    'description': 'Flexible and easy-to-use Python library for analysis & manipulation with financial & economic data',
    'long_description': '|Travis|_ |Gitter|_ |Pepy|_ |Codecov|_\n\n.. |Travis| image:: https://travis-ci.org/okama-io/yapo.svg?branch=master\n.. _Travis: https://travis-ci.org/okama-io/yapo\n\n.. |Gitter| image:: https://badges.gitter.im/okama-io/community.svg\n.. _Gitter: https://gitter.im/okama-io/community\n\n.. |Pepy| image:: https://pepy.tech/badge/yapo\n.. _Pepy: https://pepy.tech/badge/yapo\n\n.. |Codecov| image:: https://codecov.io/gh/okama-io/yapo/branch/master/graph/badge.svg\n.. _Codecov: https://codecov.io/gh/okama-io/yapo\n\n**YAPO** |--| a flexible and easy-to-use Python 3.6+ library for analysis &\nmanipulation with financial & economic data\n\n.. contents:: Contents of this Document\n\nIntroduction\n============\n\n``yapo`` is a Python library developed to solve quantitative finance and\ninvestments tasks. Additionally, it has the broader goal to become the most\nuseful and flexible open sourced tool for financial data analysis available in\npopular programming languages.\n\nApplications\n============\n\nUseful applications of ``yapo`` in the community developed are as follows:\n\n* Fully-functional ``Angular2+``-based web-application `okama.io`_\n* `tell us more <okama-discourse_>`_ if you know any\n\nThe Ecosystem\n=============\n\nThe ecosystem around the library consists of:\n\n* The Python package\n* Financial and Economic data for several markets\n* ``Angular2+`` web-application `okama.io`_\n* `Financial terms glossary <okama-glossary_>`_\n* `The community <okama-discourse_>`_\n\nMain Features\n=============\n\n* ``[x]`` ``TimeSeries`` to verify correctness of financial data manipulations\n* ``[x]`` Error-free manipulations with financial data checked by tests and active community\n* ``[x]`` Asset analysis tools for asset correlations and main performance indicators\n* ``[ ]`` Portfolio analysis tools for asset class allocation and portfolio backtesting\n* ``[ ]`` Portfolio optimization and efficient frontier visualization\n* ``[ ]`` Monte Carlo Simulation for financial assets and investment portfolios\n* ``[ ]`` Bonds key properties calculations\n* ``[x]`` Access to financial data from different stock markets: EOD close, adjusted close, currency rates, inflation\n* ``[x]`` Financial and Economic data with API with GraphQL data access\n\nFinancial and Economic data freely available\n============================================\n* ``[x]`` EOD adjusted close for NYSE and NASDAQ stocks and ETF\n* ``[x]`` EOD close for Moscow Exchange stocks and ETF\n* ``[x]`` EOD close for Russian open-end funds\n* ``[ ]`` EOD close for BSE and NSE stocks and ETF (India)\n* ``[x]`` EOD for main stock and bond Indexes\n* ``[ ]`` Bonds data for Moscow Exchange-traded securities: EOD close, coupons, maturity\n* ``[x]`` Exchange Rates for USD, EUR, RUB\n* ``[ ]`` Exchange Rates for Bitcoin [BTC], Ethereum [ETH], Binance Coin [BNB] and other cryptocurrencies\n* ``[x]`` Inflation for US, EU, and Russia\n* ``[x]`` Key interest rates for US, EU, and Russia\n* ``[x]`` History of deposit rates for top 10 banks of Russia\n\nInstallation\n============\n\nTODO\n\nJupyter Notebooks\n=================\n\nTODO\n\nDependencies\n============\n\nThe library dependencies are listed at\n`pyproject.toml <https://github.com/okama-io/yapo/blob/master/pyproject.toml>`_ under\n``[tool.poetry.dependencies]`` section.\n\nDiscussion, Development, and Getting Help\n=========================================\n\n- The development discussion takes place at `the GitHub repo\n  <yapo-github-issues_>`_. We encourage you to report issues using `the Github\n  tracker <yapo-github-issues_>`_. We welcome all kinds of issues related to\n  correctness, documentation, performance, and feature requests.\n- `The community forum <okama-discourse_>`_ can also be used for general\n  questions and discussions.\n- Finally, the `Gitter channel <Gitter_>`_ is available for the development\n  related questions.\n\nContributing\n============\n\nAll contributions, bug reports, bug fixes, documentation improvements,\nenhancements, frontend implementation, and ideas are welcomed and the subject\nto discuss. Simple ways to start contributing immediately:\n\n- Browse the issue tracker to find issues that interest you\n- Read the source code and improve the documentation or address TODOs\n- Improve the example library and tutorials\n- Bug reports are an important part of making the library more stable\n- Run the library through `the okama.io frontend <okama.io_>`_ and suggest\n  improvements in design, UI, and functionality\n\nThe code is hosted at `GitHub <yapo-github_>`_. You need an GitHub account\nwhich is free to contribute to the project. We use git for the version control\nto enable distributed work on the project.\n\nContributions should be submitted as a pull request. A member of the\ndevelopment team will review the pull request and guide you through the\ncontributing process.\n\nFeel free to ask questions at `the community <okama-discourse_>`_.\n\nLicense\n=======\n\n`MIT <license_>`_\n\n.. |--| unicode:: U+2013\n.. _okama.io: https://okama.io/\n.. _okama-glossary: https://okama.io/#/glossary\n.. _okama-discourse: http://community.okama.io\n.. _yapo-github: https://github.com/okama-io/yapo\n.. _yapo-github-issues: https://github.com/okama-io/yapo/issues\n.. _license: https://github.com/okama-io/yapo/blob/master/LICENSE\n',
    'author': 'Alexander Myltsev',
    'author_email': None,
    'url': 'https://github.com/okama-io/yapo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
