import setuptools

from customdocs import __version__

setuptools.setup(
    name='customdocs',
    version=__version__,
    packages=setuptools.find_packages(),
    author='Daniel Abercrombie',
    author_email='dabercro@mit.edu',
    description='Custom parsers for sphinx',
    url='https://github.com/dabercro/customdocs',
    install_requires=[
        'sphinx',
        'sphinxcontrib-autoanysrc']
    )
