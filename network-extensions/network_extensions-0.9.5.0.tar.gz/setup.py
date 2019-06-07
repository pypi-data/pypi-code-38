#from distutils.core import setup
from setuptools import setup

from network_extensions import  __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='network_extensions',
    version=__version__,
    packages=["network_extensions","network_extensions.igraphx",
              "network_extensions.igraphx.semantic",
              "network_extensions.extendedGraph",
              "network_extensions.helpers",
              "igraphx_simulations"
              ],
    url='',
    license='',
    author='dwinter',
    author_email='dwinter@mpiwg-berlin.mpg.de',
    install_requires=[
          'rdflib','python-igraph'
      ],
    description='Managing multilayer graphs with igraph',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
