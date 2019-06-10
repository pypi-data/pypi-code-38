from setuptools import find_packages, setup


# Package meta-data.
NAME = 'dvalidator'
DESCRIPTION = 'dvalidator validation attributes'
LICENSE = 'MIT'
AUTHOR = 'Vlasov Sergei'
EMAIL = 'kakabara@outlook.com'
URL = 'https://github.com/kakabara/dvalidator'
VERSION = '0.1.3'

with open('README.rst', 'r') as rdm:
    LONG_DESCRIPTION = rdm.read()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    license=LICENSE,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        'ipaddress==1.0.22',
        'jsonschema==3.0.1'
    ]
)
