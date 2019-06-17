from setuptools import setup, find_packages

setup(
    name = 'cpbox',
    version = '1.4.19',
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
        'configparser',
        ],

    scripts = [],

    author = 'http://www.liaohuqiu.net',
    author_email = 'liaohuqiu@gmail.com',
    url = '',

    packages = find_packages(),
    platforms = 'any',
)
