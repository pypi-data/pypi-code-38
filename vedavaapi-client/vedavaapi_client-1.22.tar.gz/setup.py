from setuptools import setup

try:
    with open("README.md", "r") as fh:
        long_description = fh.read()
except:
    long_description = ''

setup(
    name='vedavaapi_client',
    version='1.22',
    packages=['vedavaapi', 'vedavaapi.client'],
    url='https://github.com/vedavaapi/client-scripts',
    author='vedavaapi',
    description='vedavaapi client',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['requests'],
    classifiers=(
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
    )
)