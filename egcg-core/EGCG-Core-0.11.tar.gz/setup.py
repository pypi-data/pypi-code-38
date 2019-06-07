from setuptools import setup, find_packages
from os.path import join, abspath, dirname
requirements_txt = join(abspath(dirname(__file__)), 'requirements.txt')
requirements = [l.strip() for l in open(requirements_txt) if l and not l.startswith('#')]


def _translate_req(r):
    # this>=0.3.2 -> this(>=0.3.2)
    ops = ('<=', '>=', '==', '<', '>', '!=')
    _version = None
    for op in ops:
        if op in r:
            r, _version = r.split(op)
            _version = op + _version

    req = r
    if _version:
        req += '(%s)' % _version
    return req

version = '0.11'

setup(
    name='EGCG-Core',
    version=version,
    packages=find_packages(exclude=('tests',)),
    url='https://github.com/EdinburghGenomics/EGCG-Core',
    license='MIT',
    description='Shared functionality across EGCG projects',
    long_description='Common modules for use across EGCG projects. Includes logging, configuration, common '
                     'exceptions, random utility functions, and modules for interfacing with external data '
                     'sources such as EGCG\'s reporting app and Clarity LIMS instance',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.6",
    ],
    keywords='EdinburghGenomics executor notification logging api rest',
    requires=[_translate_req(r) for r in requirements],  # metadata
    install_requires=requirements,  # actual module requirements
    scripts=['bin/integration_test_runner.py'],
    zip_safe=False,
    author='Murray Wham',
    author_email='murray.wham@ed.ac.uk'
)
