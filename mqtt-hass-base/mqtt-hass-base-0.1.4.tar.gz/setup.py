
import sys

from setuptools import setup

if sys.version_info < (3,7):
    sys.exit('Sorry, Python < 3.7 is not supported')

install_requires = list(val.strip() for val in open('requirements.txt'))
tests_require = list(val.strip() for val in open('test_requirements.txt'))

setup(name='mqtt-hass-base',
      version="0.1.4",
      description='Bases to build mqtt daemon compatible with Home Assistant',
      author='Thibault Cohen',
      author_email='titilambert@gmail.com',
      url='http://gitlab.com/titilambert/mqtt_hass_base',
      packages=['mqtt_hass_base'],
      license='Apache 2.0',
      install_requires=install_requires,
      tests_require=tests_require,
      classifiers=[
        'Programming Language :: Python :: 3.7',
      ]

)
