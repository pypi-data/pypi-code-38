from setuptools import setup, find_packages
from KEGG_parser import __version__ as version

__author__ = 'kthurimella'
__version__ = version

setup(
      name="KEGG-parser",
      version=__version__,
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      install_requires=['aiohttp'],
      packages=find_packages(),
      description="KEGG Parser: A tool for parsing and converting KEGG data into manipulable Python objects.",
      author="Kumar Thurimella",
      author_email='kthurimella@gmail.com',
      url="https://github.com/lozuponelab/KEGG_parser/",
      download_url="https://github.com/lozuponelab/KEGG_parser/tarball/%s" % __version__
)
