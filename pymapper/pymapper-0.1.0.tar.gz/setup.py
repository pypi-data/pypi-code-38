from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pymapper',
    version='0.1.0',
    packages=['propertymapper'],
    url='https://github.com/alburthoffman/pymapper',
    license='MIT',
    author='Alburt Hoffman',
    author_email='hoffmantang@yahoo.com',
    description='provide toDict method for subclasses '
)
