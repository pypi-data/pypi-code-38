"""coarsenraster setup.py."""
from setuptools import setup

README = open('README.rst').read()

REQUIREMENTS = [
    x for x in open('requirements.txt').read().split('\n')
    if not x.startswith('#') and len(x) > 0]

setup(
    name='coarsenraster',
    use_scm_version={'version_scheme': 'post-release',
                     'local_scheme': 'node-and-date'},
    setup_requires=['setuptools_scm'],
    install_requires=REQUIREMENTS,
    description='utility to coarsen rasters',
    long_description=README,
    maintainer='Rich Sharp',
    maintainer_email='richpsharp@gmail.com',
    url='https://bitbucket.org/natcap/coarsenraster',
    packages=['coarsenraster'],
    package_dir={
        'coarsenraster': 'src/coarsenraster',
    },
    license='BSD',
    keywords='GIS',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: BSD License'
    ])
