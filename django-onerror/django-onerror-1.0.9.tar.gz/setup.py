# -*- coding: utf-8 -*-

from setuptools import setup


version = '1.0.9'


setup(
    name='django-onerror',
    version=version,
    keywords='Django window.onerror Report',
    description='Django ``window.onerror`` Report',
    long_description=open('README.rst').read(),

    url='https://github.com/django-xxx/django-onerror',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['django_onerror'],
    py_modules=[],
    install_requires=['django-admin>=1.2.4', 'django-response'],
    include_package_data=True,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
    ],
)
