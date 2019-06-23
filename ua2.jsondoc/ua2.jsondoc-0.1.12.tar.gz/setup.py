#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


Name='ua2.jsondoc'
ProjecUrl="https://bitbucket.org/sdh-llc/ua2.jsondoc"
Version='0.1.12'
Author='Viacheslav Vic Bukhantsov'
AuthorEmail='vic@ua2crm.com'
Maintainer='Viacheslav Vic Bukhantsov'
Summary='Library for serialize django model header to json dictionary'
License='BSD License'
ShortDescription=Summary

with open('README.rst') as fh:
    long_description = fh.read()

needed = [
]

EagerResources = [
    'ua2',
]

ProjectScripts = [
##    'scripts/runweb',
]

PackageData = {
    '': ['*.*', '*.html'],
}

# Make exe versions of the scripts:
EntryPoints = {
}

setup(
    url=ProjecUrl,
    name=Name,
    zip_safe=False,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=long_description,
    license=License,
    scripts=ProjectScripts,
    install_requires=needed,
    include_package_data=True,
    packages=find_packages('src'),
    package_data=PackageData,
    package_dir = {'': 'src'},
    eager_resources = EagerResources,
    entry_points = EntryPoints,
    namespace_packages = ['ua2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ]
)
