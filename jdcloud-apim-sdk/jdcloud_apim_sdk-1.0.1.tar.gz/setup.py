from setuptools import setup, find_packages
from jdcloud_apim_sdk.core.version import VERSION

setup(
    name='jdcloud_apim_sdk',
    version=VERSION,
    description='JDCloud SDK Core for Python',
    author='JDCloud API Gateway Team',
    url='',
    scripts=[],
    packages=find_packages(),
    install_requires=['requests'],
    license="Apache License V2.0"
)
