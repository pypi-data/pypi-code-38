from re import search

from setuptools import setup

with open('src/asyncmetrics/__init__.py') as f:
    version = str(search(r"__version__ = '(.*)'", f.read()).group(1))

with open('README.md') as fh:
    long_description = fh.read()

setup(
    name='asyncmetrics',
    version=version,
    packages=['asyncmetrics'],
    package_dir={'': 'src'},
    url='https://github.com/mon4ter/asyncmetrics',
    license='MIT',
    author='Dmitry Galkin',
    author_email='mon4ter@gmail.com',
    description='Send metrics to Graphite asynchronously from your asyncio application',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'aiographite>=0.1',
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest',
        'pytest-asyncio'
    ],
)
