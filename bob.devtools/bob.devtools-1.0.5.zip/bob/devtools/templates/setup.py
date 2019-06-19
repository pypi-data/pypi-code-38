#!/usr/bin/env python
# -*- coding: utf-8 -*-

{% if group == 'beat' %}from setuptools import setup, find_packages

def load_requirements(f):
  retval = [str(k.strip()) for k in open(f, 'rt')]
  return [k for k in retval if k and k[0] not in ('#', '-')]

install_requires=load_requirements('requirements.txt')
{% else %}from setuptools import setup, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements, find_packages
install_requires = load_requirements()
{% endif %}

setup(

    name='{{ name }}',
    version=open("version.txt").read().rstrip(),
    description='{{ title }}',

    url='https://gitlab.idiap.ch/{{ package }}',
    {% if license == 'gplv3' %}license='GPLv3'{% else %}license='BSD'{% endif %},

    # there may be multiple authors (separate entries by comma)
    author='{{ author }}',
    author_email='{{ email }}',

    # there may be a maintainer apart from the author - you decide
    #maintainer='?'
    #maintainer_email='email@example.com'

    # you may add more keywords separating those by commas (a, b, c, ...)
    keywords = "{{ group }}",

    long_description=open('README.rst').read(),

    # leave this here, it is pretty standard
    packages=find_packages(),
    include_package_data=True,
    zip_safe = False,

    install_requires=install_requires,

    entry_points={
      # add entry points (scripts, {{ group }} resources here, if any)
      },

    # check classifiers, add and remove as you see fit
    # full list here: https://pypi.org/classifiers/
    # don't remove the Bob framework unless it's not a {{ group }} package
    classifiers = [
      {% if group == 'bob' %}'Framework :: Bob',
      {% endif %}'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      {% if license == 'gplv3' %}'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'{% else %}'License :: OSI Approved :: BSD License'{% endif %},
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Software Development :: Libraries :: Python Modules',
      ],

)
