from setuptools import setup

with open('keepit/VERSION') as f:
    __version__ = f.read().strip()
    assert __version__


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    with open(filename, 'r') as f:
        lineiter = list(line.strip() for line in f)
    return [line for line in lineiter if line and not line.startswith("#")]


install_reqs = parse_requirements("requirements.txt")
test_reqs = parse_requirements("test-requirements.txt")


# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='keepit',
    python_requires='>3.3',
    packages=['keepit'],  # this must be the same as the name above
    version=__version__,
    license='Apache License 2.0',
    description=('advanced memoization/caching of functions with data analytics in mind'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='J. Fernando Sanchez',
    author_email='balkian@gmail.com',
    url='https://github.com/balkian/keepit',  # use the URL to the github repo
    download_url='https://github.com/balkian/keepit/archive/{}.tar.gz'.format(
        __version__),
    keywords=['data analysis', 'memoization', 'cache'],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    install_requires=install_reqs,
    tests_require=test_reqs,
    setup_requires=['pytest-runner', ],
    include_package_data=True,
    entry_points={
        'console_scripts':
        ['keepit = keepit.__main__:main',]
    })
