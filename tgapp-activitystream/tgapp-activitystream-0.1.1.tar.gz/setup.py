# -*- coding: utf-8 -*-
import sys, os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires=[
    "TurboGears2 >= 2.3.9",
    "tgext.pluggable >= 0.7.1",
    "sprox>=0.10.2"
]

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(
    name='tgapp-activitystream',
    version='0.1.1',
    description='Pluggable for create a simple activity stream.',
    long_description=README,
    author='AXANT',
    author_email='tech@axant.it',
    url='https://github.com/axant/tgapp-activitystream',
    keywords='turbogears2.application',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    package_data={'activitystream': [
        'i18n/*/LC_MESSAGES/*.mo',
        'templates/*/*',
        'public/*/*'
    ]},
    message_extractors={'activitystream': [
            ('**.py', 'python', None),
            ('templates/**.xhtml', 'kajiki', None),
            ('public/**', 'ignore', None)
    ]},
    entry_points="""
    """,
    zip_safe=False
)
