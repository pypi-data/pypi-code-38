# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['monobank']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'monobank',
    'version': '0.3.0',
    'description': 'Monobank.ua API implementation',
    'long_description': "# python-monobank\n\nPython client for Monobank API (https://api.monobank.ua/docs/)\n\n## Installation\n\n```\npip install monobank\n```\n\n\n# Usage\n\n## Personal api\n\n1) Request your token at https://api.monobank.ua/\n\n2) Use that token to initialize client:\n\n```\n  import monobank\n  token = 'xxxxxxxxxxxxxxx'\n\n  mono = monobank.Client(token)\n  user_info = mono.personal_clientinfo()\n  print(user_info)\n```\n\n### Methods\n\nGet currencies\n\n```\n>>> mono.bank_currency()\n[\n {'currencyCodeA': 840,\n  'currencyCodeB': 980,\n  'date': 1561686005,\n  'rateBuy': 25.911,\n  'rateSell': 26.2357},\n {'currencyCodeA': 978,\n  'currencyCodeB': 980,\n  'date': 1561686005,\n  'rateBuy': 29.111,\n  'rateSell': 29.7513},\n  ...\n```\n\nGet client info\n\n```\n>>> mono.personal_clientinfo()\n{\n  'name': 'Dmitriy Dubilet'\n  'accounts': [\n    {\n      'id': 'accidxxxxx'\n      'balance': 100000000,\n      'cashbackType': 'UAH',\n      'creditLimit': 100000000,\n      'currencyCode': 980,\n      }\n  ],\n}\n\n```\n\n\nGet statements\n```\n>>> mono.personal_statement('accidxxxxx', date(2019,1,1), date(2019,1,30))\n[\n  {\n    'id': 'iZDPhf8v32Qass',\n    'amount': -127603,\n    'balance': 99872397,\n    'cashbackAmount': 2552,\n    'commissionRate': 0,\n    'currencyCode': 978,\n    'description': 'Smarass club',\n    'hold': True,\n    'mcc': 5411,\n    'operationAmount': 4289,\n    'time': 1561658263\n  },\n  ...\n]\n```\n\n\n\n\n## Corporatre API\n\n...still negotiating...\n\n## Handling Errors\n\nTODO\n",
    'author': 'Vitaliy Kucheriavyi',
    'author_email': 'ppr.vitaly@gmail.com',
    'url': 'https://github.com/vitalik/python-monobank',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
