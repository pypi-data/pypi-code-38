#!/usr/bin/env python

from io import open
from setuptools import setup
from sphinx_rigado_theme import __version__

setup(
    name='sphinx_rigado_theme',
    version=__version__,
    author='Spencer Williams',
    author_email='spencer.williams@rigado.com',
    description='A Sphinx theme for Rigado',
    long_description=open('README.rst', encoding='utf-8').read(),
    url='https://git.rigado.com/documentation/sphinx',
    license='MIT',
    packages=['sphinx_rigado_theme'],
    package_data={'sphinx_rigado_theme': [
        'theme.conf',
        '*.html',
        'static/css/*.css',
        'static/images/*.ico',
        'static/images/*.png'
    ]},
    include_package_data=True,
    # See http://www.sphinx-doc.org/en/stable/theming.html#distribute-your-theme-as-a-python-package
    entry_points = {
      'sphinx.html_themes': [
        'sphinx_rigado_theme = sphinx_rigado_theme',
      ]
    },
    classifiers=[
      'Framework :: Sphinx',
      'Framework :: Sphinx :: Theme',
      'Development Status :: 5 - Production/Stable',
      'License :: OSI Approved :: MIT License',
      'Environment :: Console',
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
      'Operating System :: OS Independent',
      'Topic :: Documentation',
      'Topic :: Software Development :: Documentation',
    ],
)
