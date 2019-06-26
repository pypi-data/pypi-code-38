from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='komparse-generator',
    version='0.9.6',
    description='A parser generator tool',
    long_description=long_description,
    #url='', TODO: create website for komparse-generator
    author='Thomas Bollmeier',
    author_email='entwickler@tbollmeier.de',
    license='Apache-2.0',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3'
    ],
    keywords='parser development tools',
    packages=['komparse_gen'],
    package_dir={'komparse_gen': 'src/komparse_gen'},
    install_requires=['komparse'],
    entry_points={
        'console_scripts': [
            'komparsegen=komparse_gen.generator:generate'
        ]
    }
)
