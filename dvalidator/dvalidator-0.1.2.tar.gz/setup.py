from setuptools import find_packages, setup


# Package meta-data.
NAME = 'dvalidator'
DESCRIPTION = 'dvalidator validation attributes'
LICENSE = 'MIT'
AUTHOR = 'Vlasov Sergei'
EMAIL = 'kakabara@outlook.com'
URL = 'https://github.com/kakabara/dvalidator'
VERSION = '0.1.2'

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    license=LICENSE,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(),
    install_requires=[
        'ipaddress==1.0.22',
        'jsonschema==3.0.1'
    ]
)
