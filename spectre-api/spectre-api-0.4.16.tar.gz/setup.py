from setuptools import setup, find_packages

# The following few lines from PYPA Sample at https://github.com/pypa/sampleproject/blob/master/setup.py
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
        name="spectre-api",
        description="Wrapper to use the Lumeta Spectre API",
        version="0.4.16",
        license="MIT",
        install_requires=['requests'],
        packages=find_packages(where="src"),
        package_dir={'': 'src'},
        long_description=long_description,
        long_description_content_type='text/markdown'
        )

