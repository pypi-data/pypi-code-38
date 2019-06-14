# -*- coding: utf-8 -*- vim: et ts=8 sw=4 sts=4 si tw=79 cc=+1
"""Installer for the visaplan.namespace.pkg_resource package.

Explicitly establishes a 'visaplan' package and ... namespace,
pkg_resource style; see
<https://packaging.python.org/guides/packaging-namespace-packages/#pkg-resources-style-namespace-packages>
and
<https://community.plone.org/t/factoring-out-packages-namespace-problem/6842>
"""

from setuptools import setup, find_packages
from os.path import isfile

package_name = 'visaplan.namespace.pkg_resource'

# -------------------------------------------- [ get the version ... [
def read_version(fn, sfn):
    main = open(fn).read().strip()
    if sfn is not None and isfile(sfn):
        suffix = valid_suffix(open(sfn).read().strip())
    else:
        suffix = ''
    return main + suffix
    # ... get the version ...
def valid_suffix(suffix):
    """
    Enforce our suffix convention
    """
    suffix = suffix.strip()
    if not suffix:
        return suffix
    allowed = set('.dev0123456789')
    disallowed = set(suffix).difference(allowed)
    if disallowed:
        disallowed = ''.join(sorted(disallowed))
        raise ValueError('Version suffix contains disallowed characters'
                         ' (%(disallowed)s)'
                         % locals())
    chunks = suffix.split('.')
    chunk = chunks.pop(0)
    if chunk:
        raise ValueError('Version suffix must start with "."'
                         ' (%(suffix)r)'
                         % locals())
    if not chunks:
        raise ValueError('Version suffix is too short'
                         ' (%(suffix)r)'
                         % locals())
    for chunk in chunks:
        if not chunk:
            raise ValueError('Empty chunk %(chunk)r in '
                             'version suffix %(suffix)r'
                             % locals())
        char = chunk[0]
        if char in '0123456789':
            raise ValueError('Chunk %(chunk)r of version suffix %(suffix)r'
                             ' starts with a digit'
                             % locals())
        char = chunk[-1]
        if char not in '0123456789':
            raise ValueError('Chunk %(chunk)r of version suffix %(suffix)r'
                             ' doesn\'t end with a digit'
                             % locals())
    return suffix  # ... valid_suffix
    # ... get the version ...
    # ... get the version ...
VERSION = read_version('VERSION',
                       'VERSION_SUFFIX')
# -------------------------------------------- ] ... get the version ]



# ------------------------------------------- [ for setup_kwargs ... [
long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])

# see as well --> src/visaplan/PACKAGE/configure.zcml:
exclude_subpackages = (
        )
exclude_packages = []
for subp in exclude_subpackages:
    exclude_packages.extend([package_name + '.' + subp,
                             package_name + '.' + subp + '.*',
                             ])
packages = find_packages(
            'src',
            exclude=exclude_packages)
# ------------------------------------------- ] ... for setup_kwargs ]

setup_kwargs = dict(
    name=package_name,
    # see also --> ./visaplan.namespace.pkg_resource.egg-info/PKG-INFO: 
    version=VERSION,
    description="Dummy namespace package, pkg_resource style",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    # Get more from https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    # keywords='Python Plone',
    author='Tobias Herp',
    author_email='tobias.herp@visaplan.com',
    url='https://pypi.org/project/visaplan.PACKAGE',
    license='GPL version 2',
    packages=packages,
    namespace_packages=[
        'visaplan',
        'visaplan.plone',
        ],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
setup(**setup_kwargs)
