import os

from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    long_description = f.read().strip()


setup(
    name='enthought_sphinx_theme',
    version='0.6.1',
    author='Enthought, Inc.',
    author_email='info@enthought.com',
    description='Sphinx theme for Enthought products',
    long_description=long_description,
    url='https://github.com/enthought/enthought-sphinx-theme',
    packages=find_packages(),
    include_package_data=True,
    license = "BSD",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
)
