from setuptools import setup, find_packages

with open('requirements.txt') as file:
    install_requires = file.read()

setup(
    name='podder-lib',
    version='0.0.4',
    description='Library for the Podder Task.',
    packages=find_packages(),
    author="podder-ai",
    url='https://github.com/podder-ai/podder-lib',
    include_package_data=True,
    install_requires=install_requires
)
