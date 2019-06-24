# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'requirements.txt')) as f:
    requires = f.read()

with open(os.path.join(here, 'CURRENT_VERSION')) as f:
    current_version = f.read().splitlines()[0].strip()


tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',  # includes virtualenv
    'pytest-cov',
    ]


entry_points = {
    "paste.app_factory": "main = endi_base:main",
}

setup(name='endi_base',
      version=current_version,
      description='endi_base',
      long_description=README,
      license='GPLv3',
      classifiers=[
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Coopérer Pour Entreprendre',
      author_email='contact@endi.coop',
      url='https://framagit.org/endi/endi_base',
      keywords='web wsgi bfg pylons pyramid endi',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=requires,
      entry_points=entry_points,
      )
