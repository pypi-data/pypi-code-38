# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pgnotify']

package_data = \
{'': ['*']}

install_requires = \
['logx', 'psycopg2-binary']

setup_kwargs = {
    'name': 'pgnotify',
    'version': '0.1.1561372201',
    'description': 'Easily LISTEN to PostgreSQL NOTIFY notifications',
    'long_description': '# pgnotify: A python library to easily LISTEN to PostgreSQL NOTIFY notifications\n\n## Example\n\nLISTEN to and process NOTIFY events with a simple `for` loop, like so:\n\n```python\nfrom pgnotify import await_pg_notifications\n\nfor notification in await_pg_notifications(\n        \'postgresql:///example\',\n        [\'channel1\', \'channel2\']):\n\n    print(notification.channel)\n    print(notification.payload)\n```\n\n## Install\n\nInstallable with any python package manager from the python package index, eg:\n\n```shell\npip install pgnotify\n```\n\n## All the bells and whistles\n\nYou can also handle timeouts and signals, as in this more fully-fleshed example:\n\n```python\nimport signal\n\nfrom pgnotify import await_pg_notifications, get_dbapi_connection\n\n# the first parameter of the await_pg_notifications\n# loop is a dbapi connection in autocommit mode\nCONNECT = "postgresql:///example"\n\n# use this convenient method to create the right connection\n# from a database URL\ne = get_dbapi_connection(CONNECT)\n\nSIGNALS_TO_HANDLE = [signal.SIGINT, signal.SIGTERM]\n\nfor n in await_pg_notifications(\n    e,\n    ["hello", "hello2"],\n    timeout=10,\n    yield_on_timeout=True,\n    handle_signals=SIGNALS_TO_HANDLE,\n):\n    # the integer code of the signal is yielded on each\n    # occurrence of a handled signal\n    if isinstance(n, int):\n        sig = signal.Signals(n)\n        print(f"handling {sig.name}, stopping")\n        break\n\n    # the `yield_on_timeout` option makes the\n    # loop yield `None` on timeout\n    elif n is None:\n        print("timeout, continuing")\n\n    # handle the actual notify occurrences here\n    else:\n        print((n.pid, n.channel, n.payload))\n```\n\nFurther documentation to come.\n',
    'author': 'Robert Lechte',
    'author_email': 'robertlechte@gmail.com',
    'url': 'https://github.com/djrobstep/pgnotify',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
