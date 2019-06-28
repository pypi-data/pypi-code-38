# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['linux-touchpad']

package_data = \
{'': ['*']}

install_requires = \
['filelock>=3.0,<4.0', 'pyudev>=0.21.0,<0.22.0']

setup_kwargs = {
    'name': 'linux-touchpad',
    'version': '0.2.4',
    'description': 'Auto-disable laptop touchpad when a mouse is detected.',
    'long_description': '#+title: Linux Touchpad\n#+author: Noah Corona\n#+email: noah@coronasoftware.net\n#+description: A simple tool for managing your touchpad.\n\nDisable touchpad when a mouse is plugged in.\n\nDoes its best at guessing device type, it should work for most\nunix systems.\n\n* Dependencies\n  | Python 3.7 | https://www.python.org/downloads/release/python-373/ |\n  | Xinput     | https://wiki.archlinux.org/index.php/Xinput          |\n* Install\n  #+begin_src bash\n  $ pip install linux-touchpad\n  #+end_src\n* Usage\n** Start\n   #+begin_src bash\n   $ python -m linux-touchpad start\n   #+end_src bash\n** Toggle\n   #+begin_src bash\n   $ python -m linux-touchpad toggle\n   #+end_src\n** Stop\n   #+begin_src bash\n   $ python -m linux-touchpad stop\n   #+end_src\n* Author\n [[https://github.com/Zer0897][Noah Corona]] \\\\\n [[mailto:noah@coronasoftware.net][noah@coronasoftware.net]]\n #+name: Logo\n [[https://coronasoftware.net][https://coronasoftware.net/s/sLogo.png]]\n',
    'author': 'Noah',
    'author_email': 'noah@coronasoftware.net',
    'url': 'https://github.com/Zer0897/linux-touchpad',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
