import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setup(
    name='pyshellwrapper', 
    version="0.1.4",
    description='Working with shell programs in Python made easier.',
    long_description=README,
    long_description_content_type="text/markdown",
    author='Matěj Mitaš',
    author_email='contact@matejmitas.com',
    license='MIT',
    packages=['pyshellwrapper'],
    include_package_data=True,
    install_requires=['jsonschema>=3', "importlib_resources ; python_version<'3.7'"]
)