from setuptools import setup, find_packages

setup(
    name = 'cpbox',
    version = '1.4.20',
    keywords = ('cpbox'),
    description = 'cp tool box',
    license = '',
    install_requires = [
        'six',
        'ruamel.yaml',
        'Jinja2',
        'netaddr',
        'requests',
        'tzlocal',
        'redis',
        'configparser==3.5.0',
        ],

    scripts = [],

    author = 'http://www.liaohuqiu.net',
    author_email = 'liaohuqiu@gmail.com',
    url = '',

    packages = find_packages(),
    platforms = 'any',
)
