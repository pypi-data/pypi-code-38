import os

from setuptools import setup, find_packages

description = (
    'PyTreaty is a hard fork of the PyContracts library '
    'from Andrea Censi. This fork has been updated to allow '
    'multiple contract definitions on a function, as well as '
    'removing Python 2.x support and other updates.'
)

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'readme.md'), encoding='utf-8') as f:
    long_description = f.read()


def get_version(filename):
    import ast
    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError('No version found in %r.' % filename)
    if version is None:
        raise ValueError(filename)
    return version


def read_reqs(filename):
    with open(filename) as file:
        return file.readlines()


version = get_version(filename='contracts/__init__.py')

setup(
    name='pytreaty',
    author="BlueCove Developers",
    url='http://github.com/bluecoveltd/contracts',

    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="type checking, value checking, contracts",
    license="LGPL",

    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
      'Topic :: Software Development :: Quality Assurance',
      'Topic :: Software Development :: Documentation',
      'Topic :: Software Development :: Testing'
    ],

    version=version,
    download_url='http://github.com/bluecoveltd/contracts/tarball/%s' % version,

    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=read_reqs('requirements.txt'),
    tests_require=read_reqs('requirements-dev.txt'),
    entry_points={},
)
