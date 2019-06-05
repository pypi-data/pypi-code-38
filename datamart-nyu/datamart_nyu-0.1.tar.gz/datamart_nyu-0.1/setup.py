import os
from setuptools import setup


os.chdir(os.path.abspath(os.path.dirname(__file__)))


req = [
    'd3m',
    'datamart',
    'requests==2.19.1',
    'websocket_client'
]
setup(name='datamart_nyu',
      version='0.1',
      py_modules=['datamart_nyu'],
      install_requires=req,
      description="Client library for NYU's DataMart",
      author="Remi Rampin, Fernando Chirigati",
      author_email='remi.rampin@nyu.edu, fchirigati@nyu.edu',
      maintainer="Remi Rampin, Fernando Chirigati",
      maintainer_email='remi.rampin@nyu.edu, fchirigati@nyu.edu',
      url='https://gitlab.com/datadrivendiscovery/datamart-api',
      project_urls={
          'Homepage': 'https://gitlab.com/datadrivendiscovery/datamart-api',
          'Source': 'https://gitlab.com/datadrivendiscovery/datamart-api',
          'Tracker': 'https://gitlab.com/datadrivendiscovery/datamart-api/issues',
      },
      long_description="Client library for NYU's DataMart",
      license='BSD-3-Clause',
      keywords=['datamart'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Information Analysis'])
