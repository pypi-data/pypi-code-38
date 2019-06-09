from setuptools import setup, find_packages

setup(
    name='villadewow',
    version='0.1',
    include_package_data=True,
    packages=find_packages(exclude=("tests",)),
)
