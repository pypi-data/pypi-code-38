from inspect import cleandoc

from setuptools import setup, find_packages

_version = {}
exec(open('crosscap/_version.py').read(), _version)

setup(
    name = 'Crosscap',
    packages=['crosscap/' + x for x in find_packages('crosscap')],
    version = _version['__version__'],
    description = 'Suite of tools for enhancing the Klein web framework',
    author = 'Cory Dodt',
    author_email = 'corydodt@gmail.com',
    url = 'https://github.com/corydodt/Crosscap',
    keywords = [],
    classifiers = [
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    scripts = ['bin/urltool'],
    install_requires=cleandoc('''
        click>=6.7
        ftfy==4.4.3
        future>=0.16.0
        pyjwt>=1.7.1
        pytest>=3.1.0
        pytest-cov>=2.5.1
        pytest-flakes>=2.0.0
        pytest-twisted>=1.5
        pyyaml>=3.12,<4.0
        twisted>=17.1.0
        werkzeug>=0.13
        wrapt>=1.11.1
        ''').split()
)
