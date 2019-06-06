# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyxbos', 'pyxbos.drivers', 'pyxbos.drivers.pbc']

package_data = \
{'': ['*'],
 'pyxbos': ['wave/*', 'wavemq/*'],
 'pyxbos.drivers': ['dark_sky/api',
                    'dark_sky/api',
                    'dark_sky/api',
                    'dark_sky/config.yaml',
                    'dark_sky/config.yaml',
                    'dark_sky/config.yaml',
                    'dark_sky/dark_sky.py',
                    'dark_sky/dark_sky.py',
                    'dark_sky/dark_sky.py',
                    'hue/hue.py',
                    'hue/hue.py',
                    'hue/requirements.txt',
                    'hue/requirements.txt',
                    'parker/*',
                    'system_monitor/requirements.txt',
                    'system_monitor/requirements.txt',
                    'system_monitor/systemmonitor.py',
                    'system_monitor/systemmonitor.py',
                    'weather_current/*',
                    'weather_prediction/*']}

install_requires = \
['aiogrpc>=1.6,<2.0',
 'beautifulsoup4>=4.7,<5.0',
 'googleapis-common-protos>=1.5,<2.0',
 'grpcio-tools>=1.18,<2.0',
 'grpcio>=1.18,<2.0',
 'jq>=0.1.6,<0.2.0',
 'tlslite-ng>=0.7.5,<0.8.0',
 'xxhash>=1.3,<2.0']

setup_kwargs = {
    'name': 'pyxbos',
    'version': '0.2.8',
    'description': 'Python bindings for XBOS-flavored WAVEMQ and related services',
    'long_description': None,
    'author': 'Gabe Fierro',
    'author_email': 'gtfierro@cs.berkeley.edu',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
