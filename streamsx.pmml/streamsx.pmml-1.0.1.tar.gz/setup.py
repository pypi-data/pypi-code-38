from setuptools import setup
import streamsx.pmml
setup(
  name = 'streamsx.pmml',
  packages = ['streamsx.pmml'],
  include_package_data=True,
  version = streamsx.pmml.__version__,
  description = 'IBM Streams PMML integration',
  long_description = open('DESC.txt').read(),
  author = 'IBM Streams @ github.com',
  author_email = 'hegermar@de.ibm.com',
  license='Apache License - Version 2.0',
  url = 'https://github.com/IBMStreams/pypi.streamsx.pmml',
  keywords = ['streams', 'ibmstreams', 'streaming', 'analytics', 'streaming-analytics', 'pmml'],
  classifiers = [
    'Development Status :: 1 - Planning',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
  install_requires=['streamsx>=1.12.5'],
  
  test_suite='nose.collector',
  tests_require=['nose']
)
