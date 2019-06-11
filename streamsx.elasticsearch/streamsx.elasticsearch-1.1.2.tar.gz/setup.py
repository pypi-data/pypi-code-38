from setuptools import setup
import streamsx.elasticsearch
setup(
  name = 'streamsx.elasticsearch',
  packages = ['streamsx.elasticsearch'],
  include_package_data=True,
  version = streamsx.elasticsearch.__version__,
  description = 'IBM Streams Elasticsearch integration',
  long_description = open('DESC.txt').read(),
  author = 'IBM Streams @ github.com',
  author_email = 'hegermar@de.ibm.com',
  license='Apache License - Version 2.0',
  url = 'https://github.com/IBMStreams/streamsx.elasticsearch',
  keywords = ['streams', 'ibmstreams', 'streaming', 'analytics', 'streaming-analytics', 'elasticsearch'],
  classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
  install_requires=['streamsx'],
  
  test_suite='nose.collector',
  tests_require=['nose']
)
