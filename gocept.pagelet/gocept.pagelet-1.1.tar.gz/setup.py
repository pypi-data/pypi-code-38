import os.path
from setuptools import setup, find_packages


def read(rel_path):
    rel_path = rel_path.split('/')
    base_path = os.path.dirname(__file__)
    path = (base_path,) + tuple(rel_path)
    with open(os.path.join(*path)) as f:
        return f.read()

setup(
    name='gocept.pagelet',
    version='1.1',
    author="Christian Zagrodnick",
    author_email="mail@gocept.com",
    description="Easier z3c.pagelet handling",
    long_description='\n\n'.join([
        read('README.rst'),
        read('COPYRIGHT.txt'),
        read('CHANGES.rst'),
        read('src/gocept/pagelet/README.rst')]),
    license="ZPL 2.1",
    url='https://bitbucket.org/gocept/gocept.pagelet',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='easy z3c.pagelet zope3 pagelet zope',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    namespace_packages=['gocept'],
    install_requires=[
        'setuptools',
        'zope.interface',
        'zope.component',
        'zope.publisher',
        'zope.viewlet',
        'z3c.template',
        'z3c.pagelet',
        'zope.browsermenu',
        'zope.browserpage',
    ],
    extras_require=dict(
        test=['zope.testing'])
)
