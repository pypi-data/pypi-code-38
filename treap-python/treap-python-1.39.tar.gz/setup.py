from setuptools import setup

version = '1.39'


setup(
    name='treap-python',
    py_modules=[ 
        'treap',
        'py_treap',
        'nest',
        ],
    version=version,
    description='Python implementation of treaps',
    long_description='''
A set of python modules implementing treaps is provided.

Treaps perform most operations in O(log2(n)) time, and are innately sorted.
They're very nice for keeping a collection of values that needs to
always be sorted, or for optimization problems in which you need to find
the p best values out of q, when p is much smaller than q.

A module is provided for treaps that enforce uniqueness.

A pure python version is included, as is a Cython-enhanced version for performance.

Release 1.39 is pylint'd and is known to run on at least CPython 2.x, CPython 3.x
and Pypy, Pypy3 (beta) and Jython.
''',
    author='Daniel Richard Stromberg',
    author_email='strombrg@gmail.com',
    url='http://stromberg.dnsalias.org/~dstromberg/treap/',
    platforms='Cross platform',
    license='Apache v2',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        ],
    )
