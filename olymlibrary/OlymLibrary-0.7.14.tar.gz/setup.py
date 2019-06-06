from setuptools import setup, find_packages

setup(
    name = 'OlymLibrary',
    version = '0.7.14',
    keywords = ('OlymLibrary', 'robot'),
    description = 'olymtech test',
    license = 'MIT License',

    author = 'zy',
    author_email = '84497503@qq.com',

    packages = find_packages(),
    install_requires=['requests>=2.9.1','robotframework>=3.0','robotframework-ride>=1.5.2.1','robotframework-selenium2library>=1.7.4'],
    platforms = 'any',
)