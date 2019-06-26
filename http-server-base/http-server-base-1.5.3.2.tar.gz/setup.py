import sys
from distutils.core import setup

MIN_PYTHON_VERSION = (3, 6, 0)
if (sys.version_info[:3] < MIN_PYTHON_VERSION):
    raise SystemExit('ERROR: Python %s or higher is required, %s found.' % (
                         '.'.join(map(str,MIN_PYTHON_VERSION)),
                         '.'.join(map(str,sys.version_info[:3]))))

setup \
(
    name='http-server-base',
    version='1.5.3.2',
    install_requires=
    [
        'parse',
        'tornado>=5.0',
        'camel-case-switcher>=2.0',
    ],
    packages=
    [
        'http_server_base',
        'http_server_base.tools',
        'http_server_base.restapi',
    ],
    package_dir={ '': 'src' },
    url='https://gitlab.com/Hares/http-server-base',
    license='MIT',
    author='Peter Zaitcev / USSX-Hares',
    author_email='ussx.hares@yandex.ru',
    description='Library for simple HTTP server & REST HTTP server base based on Tornado. Includes: Logging requests and responses with Request Id; Configuration loading; Methods for requests proxying; ',
    keywords=[ 'http', 'tornado', 'server', 'http-server', 'restapi', 'rest' ],
)
