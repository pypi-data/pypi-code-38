# Don't import __future__ packages here; they make setup fail

# First, we try to use setuptools. If it's not available locally,
# we fall back on ez_setup.
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

with open("README.pypi.rst") as readmeFile:
    long_description = readmeFile.read()

install_requires = []
with open("requirements.txt") as requirementsFile:
    for line in requirementsFile:
        line = line.strip()
        if len(line) == 0:
            continue
        if line[0] == '#':
            continue
        pinnedVersion = line.split()[0]
        install_requires.append(pinnedVersion)

setup(
    # END BOILERPLATE
    name="candig_common",
    description="Common utilities for CanDIG packages",
    packages=["candig", "candig.common"],
    namespace_packages=["candig"],
    url="https://github.com/candig/candig-common",
    use_scm_version={"write_to": "candig/common/_version.py"},
    entry_points={
        "console_scripts": [
            "candig_run_tests=candig.common.run_tests:run_tests_main",
        ],
    },
    # BEGIN BOILERPLATE
    long_description=long_description,
    install_requires=install_requires,
    license='Apache License 2.0',
    include_package_data=True,
    zip_safe=True,
    author="CanDIG Team",
    author_email="info@distributedgenomics.ca",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    keywords=['genomics', 'reference'],
    # Use setuptools_scm to set the version number automatically from Git
    setup_requires=['setuptools_scm'],
)
