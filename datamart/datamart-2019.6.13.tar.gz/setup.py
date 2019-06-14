import os
from setuptools import setup


os.chdir(os.path.abspath(os.path.dirname(__file__)))


req = [
    'd3m',
]
setup(name='datamart',
      version='2019.6.13',
      py_modules=['datamart'],
      install_requires=req,
      description="Datamart API",
      author="DARPA Datamart Program",
      maintainer="Remi Rampin",
      maintainer_email='remi.rampin@nyu.edu',
      url='https://gitlab.com/ViDA-NYU/datamart/datamart',
      project_urls={
          'Homepage': 'https://gitlab.com/datadrivendiscovery/datamart-api',
          'Source': 'https://gitlab.com/datadrivendiscovery/datamart-api',
          'Tracker': 'https://gitlab.com/datadrivendiscovery/datamart-api/issues',
      },
      long_description="Datamart API",
      keywords=['datamart', 'd3m'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Information Analysis'])
