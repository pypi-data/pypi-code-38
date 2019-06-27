from setuptools import setup
import os

if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
else:
    version = os.environ['CI_JOB_ID']

setup(name='gpam-logging',
      version=version,
      description='Logger handler with GPAM integration',
      url='http://gpam.unb.br',
      author='GPAM',
      author_email='gpamunb@gmail.com',
      license='MIT',
      install_requires=[
      ],
      packages=[
          'gpam_logging',
      ],
      zip_safe=False)
