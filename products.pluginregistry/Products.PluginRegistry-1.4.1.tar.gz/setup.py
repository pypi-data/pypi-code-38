import os
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
package = os.path.join(here, 'Products', 'PluginRegistry')


def _package_doc(name):
    f = open(os.path.join(package, name))
    return f.read()

NAME = 'PluginRegistry'

VERSION = _package_doc('version.txt').strip()

with open('README.rst') as f:
    README = f.read()

with open('CHANGES.rst') as f:
    CHANGES = f.read()

setup(
    name='Products.PluginRegistry',
    version=VERSION,
    description='Configure application plugins based on interfaces',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development",
        "Topic :: System :: Archiving :: Packaging",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    keywords='web application server zope zope2',
    author="Zope Foundation and Contributors",
    author_email="zope-cmf@lists.zope.org",
    url="https://pypi.python.org/pypi/Products.PluginRegistry",
    license="ZPL 2.1 (http://www.zope.org/Resources/License/ZPL-2.1)",
    packages=find_packages(),
    include_package_data=True,
    namespace_packages=['Products'],
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Zope2 >= 2.12, <3',
        'Products.GenericSetup <1.9'
        ],
    entry_points="""
    [zope2.initialize]
    Products.PluginRegistry = Products.PluginRegistry:initialize
    """,
    )
