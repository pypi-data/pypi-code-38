import os
from setuptools import setup, find_packages


name = 'databasetools'


def get_version(package_name, version_file='_version.py'):
    """Retrieve the package version from a version file in the package root."""
    filename = os.path.join(os.path.dirname(__file__), package_name, version_file)
    with open(filename, 'rb') as fp:
        return fp.read().decode('utf8').split('=')[1].strip(" \n'")


setup(
    name=name,
    version=get_version(name),
    packages=find_packages(),
    install_requires=[
        'mysql-toolkit>=1.7.6',
    ],
    url='https://github.com/mrstephenneal/databasetools',
    license='MIT License',
    author='Stephen Neal',
    author_email='stephen@stephenneal.net',
    description='Convenient data storage toolkit.',
    long_description='A collection of database tools written in Python for handling basic actions with CSV files, '
                'numpy dictionaries, SQLite databases and MySQL databases.'
)

