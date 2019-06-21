# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['avd_compose', 'avd_compose.androidstudio', 'avd_compose.configs.v1']

package_data = \
{'': ['*'], 'avd_compose': ['utils/*']}

install_requires = \
['PyYAML>=5.1,<6.0', 'click>=7.0,<8.0', 'delegator.py>=0.1.1,<0.2.0']

entry_points = \
{'console_scripts': ['avd-compose = avd_compose.cli:main']}

setup_kwargs = {
    'name': 'avd-compose',
    'version': '0.5.5',
    'description': 'Define and run android virtual devices',
    'long_description': '# avd-compose [![PyPi version](https://img.shields.io/pypi/v/avd-compose.svg)](https://pypi.python.org/pypi/avd-compose/) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/avd-compose.svg)](https://pypi.python.org/pypi/avd-compose/) [![](https://img.shields.io/github/license/f9n/avd-compose.svg)](https://github.com/f9n/avd-compose/blob/master/LICENSE)\n\nDefine and run android virtual devices\n\n# Requirements\n\n- android-studio\n- python3.4+\n- pip3\n\n# Notes\n\nMake sure that the `ANDROID_HOME` environment variable is set.\n\n```bash\n$ echo $ANDROID_HOME\n\n$ export ANDROID_HOME=$HOME/Android/Sdk\n$ echo $ANDROID_HOME\n/home/f9n/Android/Sdk\n```\n\n# Install\n\n```bash\n$ pip3 install --user avd-compose\n```\n\n# Usage\n\n```bash\n$ avd-compose --help\n$ avd-compose version\n$ cat <<EOF >avd-compose.yml\nversion: 1\n\nplatforms:\n  - name: My_Nexus_5\n    avd:\n      package: "system-images;android-27;google_apis_playstore;x86"\n      device: Nexus 5\n    emulator:\n\n  - name: My_Nexus_One\n    avd:\n      package: "system-images;android-27;google_apis_playstore;x86"\n      device: Nexus One\n    emulator:\n\nEOF\n$ # Create all of them\n$ avd-compose create\n$ # Create one of them\n$ avd-compose create --name My_Nexus_One\n$ # Destroy all of them\n$ avd-compose destroy\n$ # Destroy one of them\n$ avd-compose destroy --name My_Nexus_One\n$ avd-compose up --name My_Nexus_5\n```\n\n# Examples\n\nLook up the [examples](https://github.com/f9n/avd-compose/tree/master/examples) directory.\n\n# Credits\n\n- [Docker Compose](https://github.com/docker/compose)\n- [Vagrant](https://github.com/hashicorp/vagrant)\n',
    'author': 'Fatih Sarhan',
    'author_email': 'f9n@protonmail.com',
    'url': 'https://github.com/f9n/avd-compose',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
