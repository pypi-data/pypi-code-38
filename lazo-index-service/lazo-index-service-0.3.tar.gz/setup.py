import os
from setuptools import setup


os.chdir(os.path.abspath(os.path.dirname(__file__)))


req = [
    'grpcio==1.21.1',
    'protobuf==3.8.0'
]
setup(name='lazo-index-service',
      version='0.3',
      packages=['lazo_index_service'],
      install_requires=req,
      description="API for accessing the Lazo index.",
      author="Fernando Chirigati",
      author_email='fchirigati@nyu.edu',
      maintainer="Fernando Chirigati",
      maintainer_email='fchirigati@nyu.edu',
      url='https://gitlab.com/ViDA-NYU/datamart/lazo-index-service',
      project_urls={
          'Homepage': 'https://gitlab.com/ViDA-NYU/datamart/lazo-index-service',
          'Source': 'https://gitlab.com/ViDA-NYU/datamart/lazo-index-service',
          'Tracker': 'https://gitlab.com/ViDA-NYU/datamart/lazo-index-service/issues',
      },
      long_description="API for accessing the Lazo index.",
      license='BSD-3-Clause',
      keywords=['lazo'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Scientific/Engineering :: Information Analysis'])
