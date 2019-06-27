from setuptools import setup, find_packages

from orchestrate.version import VERSION


install_requires = [
  'awscli==1.16.14',
  'botocore==1.12.4',
  'boto3==1.9.4',
  'cement==2.10.12',
  'colorama==0.3.9',
  'docker==3.4.1',
  'futures; python_version == "2.7"',
  'kubernetes==8.0.0',
  'pystache==0.5.4',
  'PyYAML==3.13',
  'requests==2.19.1',
  'sigopt==3.6.4',
  'six==1.11.0',
]

with open('LONG_DESCRIPTION.rst', 'r') as f:
  long_description = f.read()

setup(
  name='orchestrate',
  version=VERSION,
  description='SigOpt Orchestrate Client',
  long_description=long_description,
  author='SigOpt',
  author_email='support@sigopt.com',
  url='https://sigopt.com/docs/orchestrate',
  packages=find_packages(exclude=['tests*']),
  package_data={
    '': ['*.ms', '*.yml'],
  },
  python_requires='>=2.7.9,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*',
  install_requires=install_requires,
  extras_require={
    'dev': [
      'flake8==3.5.0',
      'isort==4.3.4',
      'mock==2.0.0',
      'nose==1.3.7',
      'numpy==1.15.0',
      'pylint==1.9.1',
      'pytest==3.6.1',
      'setuptools==40.0.0',
      'twine==1.11.0',
    ],
  },
  entry_points = {
    'console_scripts': ['sigopt=orchestrate.core.main:main'],
  },
  license="Apache License 2.0",
  classifiers=(
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Operating System :: MacOS',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Software Development',
  ),
)
