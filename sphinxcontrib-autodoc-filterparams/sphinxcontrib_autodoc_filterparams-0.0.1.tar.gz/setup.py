#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = ['sphinx>=2']

setup(
    author='Erik Kemperman',
    author_email='erikkemperman@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description='A sphinx extension to filter parameters from documentation',
    license='MIT',
    long_description=readme,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords=[
        'sphinx',
        'extension',
        'filter',
        'hide',
        'exclude',
        'parameter',
        'argument',
    ],
    name='sphinxcontrib_autodoc_filterparams',
    packages=['sphinxcontrib_autodoc_filterparams'],
    install_requires=requirements,
    url='https://github.com/erikkemperman/sphinxcontrib-autodoc-filterparams/',
    version='0.0.1',
    zip_safe=True,
)