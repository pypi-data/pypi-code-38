# -*- coding: utf-8 -*-
from io import open
from setuptools import setup
from divio_docs_theme import __version__


setup(
    name='divio-docs-theme',
    version=__version__,
    url='https://github.com/divio/divio-docs-theme/',
    license='MIT',
    author='Divio AG',
    author_email='developers@divio.com',
    description='Divio theme for Sphinx',
    long_description=open('README.rst', encoding='utf-8').read(),
    zip_safe=False,
    packages=['divio_docs_theme'],
    package_data={'divio_docs_theme': [
        'theme.conf',
        '*.html',
        'static/css/*.css',
        'static/js/*.js',
        'static/font/*.*'
    ]},
    include_package_data=True,
    entry_points={
        'sphinx.html_themes': [
            'divio_docs_theme = divio_docs_theme',
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
