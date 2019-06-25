try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

config = {
  'install_requires' : [],
  'description': 'Industry codes standard translator (CAE and SCIAN)',
  'version': '0.3.0',
  'packages': ['cae2scian'],
  'package_data': dict(cae2scian=['db/cae2scian.tsv']),
  'include_package_data': True,
  'name': 'cae2scian'
}

setup(**config)
