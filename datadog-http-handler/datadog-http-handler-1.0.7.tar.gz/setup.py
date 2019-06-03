'''Python logging module allowing you to log directly to Datadog via https.'''

import sys
from setuptools import setup

if sys.argv[-1] == 'sdist':
      from m2r import convert
      with open('README.md', 'r') as handle:         
            long_description = convert(handle.read())
else:
      long_description = ''

setup(name='datadog-http-handler',
      version='1.0.7',
      description='Python logging module allowing you to log directly to Datadog via https',
      long_description=long_description,
      url='https://github.com/nrccua/datadog-http-handler',
      author='NRCCUA Architects',
      author_email='architecture@nrccua.org',
      license='MIT',
      packages=['datadog_http_handler'],
      install_requires=['requests'],
      setup_requires=['pytest-runner', 'm2r', 'twine'],
      tests_require=['pytest'],
      zip_safe=False,
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ])
