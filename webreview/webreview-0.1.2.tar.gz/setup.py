"""WebReview Client Setup."""

import os
from setuptools import find_packages
from setuptools import setup


INSTALL_REQ = []

for i in open('requirements.txt').readlines():
    req = i.strip()
    if req.startswith(('#', '-')):
        continue
    INSTALL_REQ.append(req)

setup(
    name='webreview',
    version=open(os.path.join('webreview', 'VERSION')).read().strip(),
    description=(
        'Client library for the WebReview static site staging service.'
    ),
    url='https://github.com/grow/webreview-client',
    license='MIT',
    author='Grow SDK Authors',
    author_email='code@grow.io',
    include_package_data=True,
    install_requires=INSTALL_REQ,
    packages=find_packages(),
    keywords=[
        'grow',
        'cms',
        'static site generator',
        's3',
        'google cloud storage',
        'content management'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ])
